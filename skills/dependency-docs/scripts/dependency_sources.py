"""Bounded, non-executing retrieval from publisher registries and maintainer sources."""
from pathlib import Path, PurePosixPath
import base64
import gzip
import hashlib
import io
import json
import re
import sys
import tarfile
import urllib.parse
import urllib.request

import doclib as core

HERE = Path(__file__).resolve().parent
CATALOG = json.loads((HERE / 'catalog.json').read_text(encoding='utf-8'))
DOWNLOAD_LIMIT = 20 * 1024 * 1024
UNPACK_LIMIT = 64 * 1024 * 1024


def identity(dep):
    return dep['ecosystem'] + ':' + dep['name']


def source_id(dep):
    key = identity(dep)
    return 'dependency-' + re.sub(r'[^a-z0-9-]', '-', key.lower())[:70] + '-' + hashlib.sha256(key.encode()).hexdigest()[:8]


def allowed_url(url, hosts):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in hosts or parsed.username or parsed.password or parsed.port not in {None, 443}:
        raise ValueError('Documentation URL is outside the permitted public source host')


class Redirects(urllib.request.HTTPRedirectHandler):
    def __init__(self, hosts):
        self.hosts = hosts
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        allowed_url(newurl, self.hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url, hosts, limit=DOWNLOAD_LIMIT):
    allowed_url(url, hosts)
    request = urllib.request.Request(url, headers={'User-Agent': 'dependency-docs/1.0', 'Accept-Encoding': 'identity'})
    with urllib.request.build_opener(Redirects(hosts)).open(request, timeout=35) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Documentation download exceeds its size limit')
    return data


def fetch_json(url, hosts):
    return json.loads(download(url, hosts, 4 * 1024 * 1024).decode('utf-8'))


def metadata(dep, coverage, provenance):
    return {'ecosystem': dep['ecosystem'], 'name': dep['name'], 'major': dep['major'],
            'resolved_version': dep['version'], 'coverage': coverage, 'provenance': provenance}


def save(root, dep, files, coverage, provenance, repository, notes):
    revision = hashlib.sha256((identity(dep) + '@' + dep['version']).encode() + b''.join(data for _, data, _, _ in files)).hexdigest()
    spec = {'stack': 'dependency', 'repo': repository}
    manifest = core.publish(root, source_id(dep), spec, dep['version'], revision, files, notes,
                            {'dependency': metadata(dep, coverage, provenance)})
    return manifest


def npm_docs(root, dep):
    name = dep['name']; version = dep['version']
    if not re.fullmatch(r'(?:@[A-Za-z0-9_.-]+/)?[A-Za-z0-9_.-]+', name):
        raise ValueError('Unsupported npm package identity')
    url = 'https://registry.npmjs.org/' + urllib.parse.quote(name, safe='') + '/' + urllib.parse.quote(version, safe='')
    info = fetch_json(url, {'registry.npmjs.org'})
    if info.get('name') != name or info.get('version') != version:
        raise ValueError('Registry metadata did not match the requested package and version')
    distribution = info.get('dist', {})
    archive_url = distribution.get('tarball', '')
    archive = download(archive_url, {'registry.npmjs.org'})
    integrity = distribution.get('integrity', '')
    checked = False
    for algorithm in ['sha512', 'sha384', 'sha256']:
        for item in integrity.split():
            if item.startswith(algorithm + '-'):
                expected = item.split('-', 1)[1].split('?', 1)[0]
                if base64.b64encode(hashlib.new(algorithm, archive).digest()).decode() != expected:
                    raise ValueError('Published npm archive integrity verification failed')
                checked = True; break
        if checked:
            break
    if not checked:
        if not distribution.get('shasum') or hashlib.sha1(archive).hexdigest() != distribution['shasum']:
            raise ValueError('No matching published npm archive checksum')
    with gzip.GzipFile(fileobj=io.BytesIO(archive)) as compressed:
        uncompressed = compressed.read(UNPACK_LIMIT + 1)
    if len(uncompressed) > UNPACK_LIMIT:
        raise ValueError('Published archive exceeds the 64 MiB unpack limit; register a focused documentation source')
    files = []
    with tarfile.open(fileobj=io.BytesIO(uncompressed), mode='r:') as tar:
        for member in tar:
            parts = PurePosixPath(member.name).parts
            if not member.isfile() or len(parts) != 2 or parts[0] != 'package' or member.size > 2 * 1024 * 1024:
                continue
            name = parts[1]
            if not re.match(r'(?i)^(readme|license|copying|notice)(?:\.|$)', name):
                continue
            stream = tar.extractfile(member)
            data = stream.read() if stream else b''
            if name.lower().startswith('readme') and Path(name).suffix.lower() not in core.DOC_EXTENSIONS:
                name += '.txt'
            files.append((name, data, archive_url, 'https://www.npmjs.com/package/' + dep['name'] + '/v/' + version))
    if not any(name.lower().startswith('readme') for name, *_ in files):
        raise ValueError('The published package has no README; register a focused maintainer documentation source')
    return save(root, dep, files, 'published-readme', 'publisher-registry-artifact', url,
                'Publisher README and notices from the checksum-verified exact npm release. This is not a complete API manual. Repository/homepage claims in package metadata were not independently verified.')


def pypi_docs(root, dep):
    name = dep['name']; version = dep['version']
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', name):
        raise ValueError('Unsupported PyPI package identity')
    url = f'https://pypi.org/pypi/{name}/{urllib.parse.quote(version, safe="")}/json'
    info = fetch_json(url, {'pypi.org'})['info']
    normalized = re.sub(r'[-_.]+', '-', info.get('name', '')).lower()
    if normalized != name or info.get('version') != version:
        raise ValueError('PyPI metadata did not match the requested package/version')
    description = info.get('description', '').strip()
    if not description:
        raise ValueError('No publisher description on PyPI; register a focused maintainer source')
    page = f'https://pypi.org/project/{name}/{version}/'
    files = [('README.txt', description.encode(), url, page)]
    if isinstance(info.get('license'), str) and info['license']:
        files.append(('LICENSE.txt', info['license'].encode(), url, page))
    return save(root, dep, files, 'published-readme', 'publisher-registry-description', url,
                'Exact-release publisher description from PyPI. External project links are discovery leads, not independently verified documentation sources.')


def github_docs(root, dep, configuration, refresh=False):
    version = dep['version']; numbers = version.split('.')
    values = {'version': version, 'major': dep['major'], 'minor': numbers[1] if len(numbers) > 1 else '0'}
    repository = configuration['repository']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Source must name a public owner/repository on GitHub')
    if dep['ecosystem'] == 'npm' and configuration.get('provenance') != 'user-registered':
        package = fetch_json('https://registry.npmjs.org/' + urllib.parse.quote(dep['name'], safe='') + '/' + urllib.parse.quote(version, safe=''), {'registry.npmjs.org'})
        declared = package.get('repository', {})
        declared = declared.get('url', '') if isinstance(declared, dict) else declared
        match = re.search(r'github\.com[:/]([^/]+/[^/#]+)', declared)
        if not match or match[1].removesuffix('.git').lower() != repository.lower():
            raise ValueError('Catalog repository does not match the package publisher metadata')
    # No Git credentials are sent to this lookup; a private/missing repository is not fetched.
    repo = fetch_json('https://api.github.com/repos/' + repository, {'api.github.com'})
    if repo.get('private') or repo.get('full_name', '').lower() != repository.lower():
        raise ValueError('Documentation repository was not confirmed public')
    ref = configuration.get('tag', 'v{version}').format(**values)
    path_sets = configuration.get('path_sets', [configuration.get('paths', [])])
    candidates = [[value.format(**values) for value in paths] for paths in path_sets]
    if any(p.startswith(('/', '-')) or '..' in Path(p).parts for paths in candidates for p in paths):
        raise ValueError('Invalid configured documentation directory')
    spec = {'stack': 'dependency', 'repo': repository, 'ref': ref, 'kind': 'repository',
            'site': configuration.get('site', 'https://github.com/' + repository).format(**values),
            'include_root_docs': True, 'dependency': metadata(dep, configuration.get('coverage', 'maintainer-docs'), configuration.get('provenance', 'verified-source-catalog'))}
    signature = hashlib.sha256(json.dumps(configuration, sort_keys=True).encode()).hexdigest()[:8]
    # A changed docs-source configuration must not alias an immutable older snapshot.
    for index, paths in enumerate(candidates):
        try:
            manifest, _ = core.sync_repo(root, source_id(dep) + '-' + signature, spec | {'paths': paths}, refresh=refresh)
            return manifest
        except RuntimeError as error:
            if not str(error).startswith('Configured documentation path missing') or index == len(candidates) - 1:
                raise
    raise ValueError('No usable documentation path set')


def go_docs(root, dep):
    name = dep['name']; version = 'v' + dep['version'].removeprefix('v')
    # Unknown company/private vanity domains need an explicitly registered source.
    if not name.startswith(('github.com/', 'golang.org/', 'gopkg.in/', 'go.uber.org/', 'modernc.org/')):
        raise ValueError('Unverified Go vanity domain; register a maintainer source before fetching')
    if name.startswith('github.com/'):
        repository = '/'.join(name.split('/')[1:3])
        info = fetch_json('https://api.github.com/repos/' + repository, {'api.github.com'})
        if info.get('private') or info.get('full_name', '').lower() != repository.lower():
            raise ValueError('Go module repository was not confirmed public')
    url = 'https://pkg.go.dev/' + urllib.parse.quote(name, safe='/') + '@' + urllib.parse.quote(version, safe='')
    data = download(url, {'pkg.go.dev'}, 8 * 1024 * 1024)
    text = data.decode('utf-8', errors='replace')
    if name not in text or version not in text or 'Documentation' not in text:
        raise ValueError('Versioned Go package documentation was not confirmed in the response')
    return save(root, dep, [('package.html', data, url, url)], 'versioned-api', 'go-package-index', url,
                'API documentation generated from the named public Go module release. Subpackages may require their own focused page; this is not every package in the module.')


def sqlite_docs(root, dep):
    files = []
    for page in ['docs.html', 'lang.html', 'lang_transaction.html', 'pragma.html', 'wal.html', 'c3ref/intro.html', 'copyright.html']:
        url = 'https://sqlite.org/' + page
        data = download(url, {'sqlite.org', 'www.sqlite.org'}, 4 * 1024 * 1024)
        if b'SQLite' not in data:
            raise ValueError('SQLite documentation response was not confirmed')
        files.append((page, data, url, url))
    return save(root, dep, files, 'major-website-snapshot', 'maintainer-website', 'https://sqlite.org/docs.html',
                'Selected current SQLite 3 SQL, transaction, WAL and C API references. Not a patch-specific engine manual. Verify feature availability against the actual embedded SQLite engine version, separately from the driver version.')


def obtain(root, dep, configuration=None, refresh=False):
    configuration = configuration or CATALOG.get(identity(dep), {})
    kind = configuration.get('kind', dep['ecosystem'])
    if kind == 'github':
        try:
            return github_docs(root, dep, configuration, refresh)
        except Exception as error:
            if not configuration.get('fallback_readme'):
                raise
            print(f"Full source unavailable for {identity(dep)}; using the publisher README: {error}", file=sys.stderr)
            return npm_docs(root, dep)
    handlers = {'npm': npm_docs, 'pypi': pypi_docs, 'go': go_docs, 'sqlite': sqlite_docs}
    if kind not in handlers:
        raise ValueError('No verified source adapter; register the maintainer repository before fetching')
    return handlers[kind](root, dep)

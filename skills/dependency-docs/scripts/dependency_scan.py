"""Read dependency manifests/locks without installing packages or executing project code."""
from pathlib import Path
import fnmatch
import hashlib
import json
import os
import re
import tomllib
from urllib.parse import urlparse
from package_locks import exact_version as exact, matches_version as matches, manager, parse_yarn, resolve_dependency, scalar

SKIP = {'.git', 'node_modules', 'vendor', '.venv', 'venv', '__pycache__', '.cache', '.next',
        'dist', 'build', 'target', '.yarn', 'Binaries', 'Intermediate', 'Saved', 'DerivedDataCache', '.local'}
MAX_FILES = 20_000
MAX_MANIFEST = 16 * 1024 * 1024


def read(path):
    if path.stat().st_size > MAX_MANIFEST:
        raise ValueError('Manifest exceeds the 16 MiB scan limit')
    return path.read_text(encoding='utf-8-sig')


def major(version):
    match = re.match(r'^v?(\d+)(?:\.|$)', version or '')
    return match[1] if match else None


def public_registry(value, allowed):
    try:
        parsed = urlparse(value)
        return parsed.scheme == 'https' and parsed.hostname in allowed and not parsed.username and not parsed.password
    except ValueError:
        return False


def ancestors(directory, root):
    current = directory
    while current.is_relative_to(root):
        yield current
        if current == root:
            break
        current = current.parent


def npm_registry(directory, root, name, selected_manager="npm"):
    registry, scoped_registry = 'https://registry.npmjs.org', None
    scope = name.split('/')[0] if name.startswith('@') else None
    # Read only registry settings. Credentials are never returned, logged or transmitted.
    configs = [Path.home() / '.npmrc', *reversed([p / '.npmrc' for p in ancestors(directory, root)])]
    for config in configs:
        if not config.is_file():
            continue
        for line in read(config).splitlines():
            key, separator, value = line.partition('=')
            if separator and key.strip() == 'registry':
                registry = value.strip()
            elif separator and scope and key.strip() == scope + ':registry':
                scoped_registry = value.strip()
    registry = os.environ.get('NPM_CONFIG_REGISTRY') or os.environ.get('npm_config_registry') or registry
    if selected_manager == 'yarn':
        for parent in [Path.home(), *reversed(list(ancestors(directory, root)))]:
            classic = parent / '.yarnrc'
            if classic.is_file():
                found = re.search(r'^registry\s+(.+)$', read(classic), re.M)
                if found:
                    registry = scalar(found[1])
            config = parent / '.yarnrc.yml'
            if not config.is_file():
                continue
            in_scopes, current_scope = False, None
            for line in read(config).splitlines():
                if not line.strip() or line.lstrip().startswith('#'):
                    continue
                indent = len(line) - len(line.lstrip())
                if indent == 0:
                    in_scopes = line.strip() == 'npmScopes:'
                    current_scope = None
                if in_scopes and indent == 2 and line.strip().endswith(':'):
                    current_scope = scalar(line.strip()[:-1])
                key, colon, value = line.strip().partition(':')
                if key == 'npmRegistryServer' and colon:
                    if not in_scopes:
                        registry = scalar(value)
                    elif scope and current_scope == scope.removeprefix('@'):
                        scoped_registry = scalar(value)
        registry = os.environ.get('YARN_NPM_REGISTRY_SERVER') or registry
    registry = scoped_registry or registry
    return 'public' if public_registry(registry, {'registry.npmjs.org', 'registry.yarnpkg.com'}) else 'private'


def npm_resolution(directory, root, alias, requested, lock_cache=None):
    result = resolve_dependency(directory, root, alias, requested, lock_cache)
    registry = npm_registry(directory, root, result['name'], result['manager'])
    if any(not public_registry(url, {'registry.npmjs.org', 'registry.yarnpkg.com'}) for url in result['urls']):
        registry = 'private'
    return result['name'], result['version'], result['status'], result['note'], registry


def go_directives(content, directive):
    block = False
    for original in content.splitlines():
        line = original.split('//', 1)[0].strip()
        if not line:
            continue
        if line == directive + ' (':
            block = True; continue
        if block and line == ')':
            block = False; continue
        if block:
            yield line
        elif line.startswith(directive + ' '):
            yield line[len(directive):].strip()


def scan(project, include_transitive=False):
    root = project.expanduser().resolve()
    if not root.is_dir():
        raise ValueError('Project must be an existing directory')
    dependencies, errors, warnings, fingerprints = [], [], [], []
    lock_cache = {}
    paths = []
    seen = 0
    for directory, folders, files in os.walk(root, followlinks=False):
        folders[:] = sorted(name for name in folders if name not in SKIP and not (Path(directory) / name).is_symlink())
        for name in sorted(files):
            seen += 1
            if seen > MAX_FILES:
                warnings.append('Scan reached the 20,000-file limit; inventory may be incomplete. Run at the affected application directory.')
                folders[:] = []; break
            if name in {'package.json', 'package-lock.json', 'npm-shrinkwrap.json', 'pnpm-lock.yaml', 'yarn.lock',
                        '.yarnrc', '.yarnrc.yml', 'go.mod', 'go.work', 'pyproject.toml', 'uv.lock', 'poetry.lock', 'vcpkg.json', 'conanfile.txt', '.npmrc'} or name.startswith('requirements') and name.endswith('.txt') or name.endswith(('.uproject', '.uplugin')):
                file = Path(directory) / name
                if file.is_symlink():
                    warnings.append(f'Skipped symlinked manifest: {file.relative_to(root)}'); continue
                paths.append(file)
        if seen > MAX_FILES:
            break
    def add(ecosystem, name, declared, version, manifest, scope='runtime', resolution=None, note='', registry='public', **extra):
        dependencies.append({'ecosystem': ecosystem, 'name': name, 'declared': declared, 'version': version,
                             'major': major(version), 'manifest': manifest.relative_to(root).as_posix(), 'scope': scope,
                             'resolution': resolution or ('resolved' if version else 'unresolved'), 'note': note, 'registry': registry, **extra})
    for file in paths:
        try:
            content = read(file)
            fingerprints.append((file.relative_to(root).as_posix(), hashlib.sha256(content.encode()).hexdigest()))
            if file.name == 'package.json':
                data = json.loads(content); chosen = {}
                for section in ['peerDependencies', 'devDependencies', 'dependencies', 'optionalDependencies']:
                    chosen.update({name: (value, section) for name, value in data.get(section, {}).items()})
                for alias, (requested, section) in sorted(chosen.items()):
                    if not isinstance(requested, str):
                        warnings.append(f'Non-string npm dependency {alias} in {file.relative_to(root)}'); continue
                    name, version, resolution, note, registry = npm_resolution(file.parent, root, alias, requested, lock_cache)
                    add('npm', name, requested, version, file, section, resolution, note, registry, alias=alias, package_manager=manager(file.parent, root))
            elif file.name in {'package-lock.json', 'npm-shrinkwrap.json'} and include_transitive:
                for key, entry in json.loads(content).get('packages', {}).items():
                    if not key or entry.get('link') or '/node_modules/' not in '/' + key:
                        continue
                    tail = key.rsplit('node_modules/', 1)[-1]
                    name = entry.get('name') or tail
                    version = exact(entry.get('version'))
                    registry = 'public' if not entry.get('resolved') or public_registry(entry['resolved'], {'registry.npmjs.org'}) else 'private'
                    add('npm', name, entry.get('version', ''), version, file, 'transitive', registry=registry)
            elif file.name == 'yarn.lock' and include_transitive:
                entries = lock_cache.setdefault(file, parse_yarn(content))
                used = set()
                for selector, item in entries.items():
                    if id(item) in used:
                        continue
                    used.add(id(item))
                    match = re.match(r'^((?:@[^/]+/)?[^@]+)@(.+)$', selector)
                    if not match:
                        continue
                    alias, requested = match.groups()
                    if requested.startswith('npm:') and not re.match(r'npm:(?:@[^/]+/)?[^@]+@', requested):
                        requested = requested[4:]
                    name, version, resolution, note, registry = npm_resolution(file.parent, root, alias, requested, lock_cache)
                    add('npm', name, requested, version, file, 'transitive', resolution, note, registry, alias=alias, package_manager='yarn')
            elif file.name == 'go.mod':
                replacements = {}
                for line in go_directives(content, 'replace'):
                    left, separator, right = line.partition('=>')
                    if separator:
                        key = left.split(); value = right.split()
                        if key and value:
                            replacements[tuple(key)] = value
                local_modules = set()
                for parent in ancestors(file.parent, root):
                    workspace = parent / 'go.work'
                    if not workspace.is_file():
                        continue
                    work = read(workspace)
                    for line in go_directives(work, 'replace'):
                        left, separator, right = line.partition('=>')
                        if separator and left.split() and right.split():
                            replacements[tuple(left.split())] = right.split()
                    for line in go_directives(work, 'use'):
                        module_file = (parent / line.strip('"') / 'go.mod').resolve()
                        if module_file.is_relative_to(root) and module_file.is_file():
                            declared = re.search(r'^module\s+(\S+)', read(module_file), re.M)
                            if declared:
                                local_modules.add(declared[1])
                    break
                indirect = {(m[1], m[2]) for m in re.finditer(r'(?m)^\s*(?:require\s+)?(\S+)\s+(v\S+)\s+//\s*indirect', content)}
                for line in go_directives(content, 'require'):
                    values = line.split()
                    if len(values) < 2:
                        continue
                    name, requested = values[:2]; resolved = requested
                    if not include_transitive and (name, requested) in indirect:
                        continue
                    if name in local_modules:
                        add('go', name, requested, None, file, resolution='local', note='Local go.work module; use its local docs/source'); continue
                    replacement = replacements.get((name, requested), replacements.get((name,)))
                    original = name
                    if replacement:
                        name = replacement[0]
                        if len(replacement) == 1:
                            add('go', original, requested, None, file, resolution='local', note='Local Go replacement; use its local docs/source'); continue
                        resolved = replacement[1]
                    private = any(fnmatch.fnmatch(name, pattern) or name.startswith(pattern.rstrip('/') + '/')
                                  for pattern in os.environ.get('GOPRIVATE', '').split(',') if pattern)
                    add('go', name, requested, exact(resolved), file, registry='private' if private else 'public', original_name=original)
            elif file.name == 'pyproject.toml' or file.name.startswith('requirements') and file.suffix == '.txt':
                locked = {}
                for lock_name in ['uv.lock', 'poetry.lock']:
                    lock = file.parent / lock_name
                    if lock.is_file():
                        for package in tomllib.loads(read(lock)).get('package', []):
                            if package.get('name') and package.get('version'):
                                identity = re.sub(r'[-_.]+', '-', package['name']).lower()
                                locked.setdefault(identity, []).append(package)
                entries = []
                private = bool(os.environ.get('PIP_INDEX_URL') and not public_registry(os.environ['PIP_INDEX_URL'], {'pypi.org'}))
                if file.name == 'pyproject.toml':
                    data = tomllib.loads(content); configuration = data.get('project', {})
                    entries.extend((value, 'runtime') for value in configuration.get('dependencies', []))
                    entries.extend((value, group) for group, values in configuration.get('optional-dependencies', {}).items() for value in values)
                    entries.extend((value, group) for group, values in data.get('dependency-groups', {}).items() for value in values if isinstance(value, str))
                    poetry = data.get('tool', {}).get('poetry', {})
                    private |= bool(poetry.get('source') or data.get('tool', {}).get('uv', {}).get('index'))
                    entries.extend((name + '==' + value, 'poetry') for name, value in poetry.get('dependencies', {}).items() if name != 'python' and isinstance(value, str) and exact(value))
                    if any(name != 'python' and not (isinstance(value, str) and exact(value)) for name, value in poetry.get('dependencies', {}).items()):
                        warnings.append(f'{file.relative_to(root)}: non-exact Poetry dependency declarations are not resolved by this scanner; inspect the manifest/lock explicitly.')
                else:
                    for line in content.splitlines():
                        line = line.split('#', 1)[0].strip()
                        if line.startswith(('--index-url', '--extra-index-url')):
                            private = True
                        elif line and not line.startswith('-'):
                            entries.append((line, 'requirements'))
                        elif line.startswith(('-r ', '--requirement', '-c ', '--constraint', '-e ', '--editable')):
                            warnings.append(f'{file.relative_to(root)}: requirement includes/constraints/editables require explicit inspection; this scanner does not execute or expand them.')
                for entry, scope in entries:
                    match = re.match(r'^([A-Za-z0-9][A-Za-z0-9_.-]*)(?:\[[^]]+\])?\s*(.*)', entry)
                    if not match:
                        continue
                    name = re.sub(r'[-_.]+', '-', match[1]).lower(); constraint = match[2].split(';', 1)[0].strip()
                    pinned = re.fullmatch(r'==\s*([^\s*]+)(?:\s+--hash=\S+)*', constraint)
                    values = locked.get(name, [])
                    versions = {p['version'] for p in values}
                    version = exact(pinned[1]) if pinned else next(iter(versions)) if len(versions) == 1 else None
                    is_private = private or any(p.get('source', {}).get('registry') and not public_registry(p['source']['registry'], {'pypi.org'}) for p in values)
                    local = '@' in constraint or any(p.get('source', {}).get('editable') or p.get('source', {}).get('path') for p in values)
                    conflict = bool(pinned and versions and versions != {version})
                    add('pypi', name, constraint or '*', None if conflict else version, file, scope, 'conflict' if conflict else 'local' if local else None,
                        'Resolve a pinned/lockfile version' if not version else 'Using the exact lock version; Python range/marker compatibility is not evaluated' if not pinned else '', 'private' if is_private else 'public')
            elif file.name == 'vcpkg.json':
                data = json.loads(content)
                overrides = {p['name']: next((p[key] for key in ['version', 'version-string', 'version-semver', 'version-date'] if key in p), None) for p in data.get('overrides', [])}
                for item in data.get('dependencies', []):
                    name = item if isinstance(item, str) else item.get('name')
                    if name:
                        declared = overrides.get(name) or (item.get('version>=', '*') if isinstance(item, dict) else '*')
                        add('vcpkg', name, declared, exact(overrides.get(name)), file, note='Without an override, resolve the actual baseline/installed port version before fetching versioned docs')
            elif file.name == 'conanfile.txt':
                requires = False
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith('['):
                        requires = line == '[requires]'
                    elif requires and '/' in line and not line.startswith('#'):
                        name, value = line.split('/', 1); value = value.split('@', 1)[0]
                        add('conan', name, value, exact(value), file)
            elif file.suffix in {'.uproject', '.uplugin'}:
                data = json.loads(content)
                for plugin in data.get('Plugins', []):
                    if plugin.get('Enabled', True) and plugin.get('Name'):
                        version = exact(plugin.get('VersionName'))
                        add('unreal', plugin['Name'], plugin.get('VersionName', 'enabled'), version, file,
                            note='Engine/project plugin descriptors often omit a resolved plugin version; inspect the matching installed descriptor and maintainer docs')
        except (OSError, ValueError, TypeError, KeyError) as error:
            errors.append({'manifest': file.relative_to(root).as_posix(), 'error': str(error)})
    if any(p.name == 'pnpm-lock.yaml' for p in paths):
        warnings.append('pnpm projects use installed package metadata when available; unresolved ranges are reported rather than guessed from lockfile text.')
    signature = hashlib.sha256(json.dumps(sorted(fingerprints)).encode()).hexdigest()
    return {'project': str(root), 'fingerprint': signature, 'manifests': [name for name, _ in fingerprints],
            'dependencies': dependencies, 'warnings': warnings, 'errors': errors}

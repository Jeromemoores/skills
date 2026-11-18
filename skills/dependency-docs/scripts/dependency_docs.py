#!/usr/bin/env python3
"""Inventory repository dependencies and cache bounded maintainer/publisher documentation."""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import os
import re
import sys
import time

import doclib as core
from dependency_scan import scan, major
import dependency_sources as sources

HERE = Path(__file__).resolve().parent


def data_root():
    if os.environ.get('DEPENDENCY_DOCS_HOME'):
        return Path(os.environ['DEPENDENCY_DOCS_HOME']).expanduser().resolve()
    if not os.environ.get('OFFICIAL_DOCS_HOME'):
        sibling = HERE.parent.parent / 'official-stack-dev/scripts/library-location.json'
        preference = core.load_json(sibling, {}).get('preferred_root')
        if preference and (Path(preference) / 'doclib.py').is_file():
            return Path(preference).resolve()
    return core.default_root()


def project_file(root, project):
    key = hashlib.sha256(str(project.resolve()).encode()).hexdigest()[:20]
    return root / 'dependency-projects' / (key + '.json')


def documentation_dependency(dep, configurations):
    configuration = configurations.get(sources.identity(dep), {})
    if configuration.get('kind') == 'sqlite' and dep['ecosystem'] != 'engine':
        return dep | {'ecosystem': 'engine', 'name': 'sqlite', 'version': '3', 'major': '3'}
    return dep


def inventory(project, transitive=False):
    report = scan(project, transitive)
    related = []
    for dep in report['dependencies']:
        for name in sources.CATALOG.get(sources.identity(dep), {}).get('related', []):
            if dep['resolution'] == 'resolved' and dep['registry'] == 'public' and name not in related:
                related.append(name)
    report['dependencies'].extend({'ecosystem': 'engine', 'name': name, 'declared': 'SQLite 3 family', 'version': '3', 'major': '3',
                                   'manifest': '(related engine documentation)', 'scope': 'related', 'resolution': 'resolved',
                                   'note': 'Engine documentation is separate from driver/package documentation; the embedded patch version remains to be verified.',
                                   'registry': 'public'} for name in related)
    return report


def records(root):
    result = collections.defaultdict(list)
    for file in core.manifests(root):
        try:
            manifest = core.load_json(file)
            dependency = manifest.get('dependency')
            # Reuse identifiable existing stack snapshots instead of downloading another copy.
            if not dependency and manifest['source'] == 'nextjs' and major(manifest['version']):
                dependency = {'ecosystem': 'npm', 'name': 'next', 'major': major(manifest['version']),
                              'resolved_version': manifest['version'].removeprefix('v'), 'coverage': 'maintainer-docs', 'provenance': 'existing-stack-cache'}
            if not dependency and manifest['source'].startswith('react'):
                documented = manifest.get('docs_major') or (manifest['source'].split('-')[-1] if manifest['source'] in {'react-16', 'react-17', 'react-18'} else None)
                if documented:
                    dependency = {'ecosystem': 'npm', 'name': 'react', 'major': str(documented),
                                  'resolved_version': manifest['version'], 'coverage': 'maintainer-docs', 'provenance': 'existing-stack-cache'}
            if dependency:
                key = (dependency['ecosystem'], dependency['name'], str(dependency['major']))
                result[key].append((file, manifest, dependency))
                if dependency['ecosystem'] == 'npm' and dependency['name'] == 'react':
                    result[('npm', 'react-dom', str(dependency['major']))].append((file, manifest, dependency))
        except (OSError, ValueError, KeyError, TypeError):
            # An unreadable manifest cannot establish cache coverage. verify reports details.
            continue
    for choices in result.values():
        choices.sort(key=lambda item: (item[1]['downloaded_at'], item[0].stat().st_mtime_ns), reverse=True)
    return result


def valid_snapshot(file, manifest):
    try:
        for entry in manifest['files']:
            target = core.safe_file(file.parent / 'files', entry['path'])
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != entry['sha256']:
                return False
        return bool(manifest['files'])
    except (OSError, ValueError, KeyError):
        return False


def cached_document(dep, index, exact=False, validity=None):
    validity = validity if validity is not None else {}
    options = index.get((dep['ecosystem'], dep['name'], str(dep['major'])), [])
    options = sorted(options, key=lambda item: item[2]['resolved_version'] == dep['version'], reverse=True)
    for file, manifest, metadata in options:
        same_version = metadata['resolved_version'] == dep['version']
        if exact and not same_version:
            continue
        if file not in validity:
            validity[file] = valid_snapshot(file, manifest)
        if not validity[file]:
            continue
        warning = '' if same_version else f"Major-version reuse: cached for {metadata['resolved_version']}; project uses {dep['version']}. Verify minor/patch API availability."
        if str(dep['major']) == '0':
            warning += ' Major zero does not promise API stability; use --exact when needed.'
        return {'status': 'cached-exact' if same_version else 'cached-major', 'snapshot': manifest['id'],
                'source': manifest['source'], 'cached_version': metadata['resolved_version'],
                'coverage': metadata['coverage'], 'provenance': metadata['provenance'], 'warning': warning.strip(), 'notes': manifest.get('notes', '')}
    return None


def configurations(root):
    return sources.CATALOG | core.load_json(root / 'dependency-sources.json', {})


def add_documentation(report, root, exact=False):
    index, validity, configured = records(root), {}, configurations(root)
    for dep in report['dependencies']:
        if dep['resolution'] != 'resolved':
            dep['docs'] = {'status': dep['resolution'], 'warning': dep['note']}
        elif dep['registry'] != 'public':
            dep['docs'] = {'status': 'private', 'warning': 'No public network request. Use approved local/private maintainer references.'}
        else:
            target = documentation_dependency(dep, configured)
            if exact and configured.get(sources.identity(target), {}).get('kind') == 'sqlite':
                dep['docs'] = {'status': 'unsupported-exact', 'warning': 'The SQLite website adapter is a current major-only snapshot, not an exact engine patch manual. Use a verified version-specific source.'}
            else:
                dep['docs'] = cached_document(target, index, exact, validity) or {'status': 'missing'}
    report['summary'] = dict(collections.Counter(dep['docs']['status'] for dep in report['dependencies']))
    report['root'] = str(root)
    previous = core.load_json(project_file(root, Path(report['project'])), {})
    def versions(items):
        return {f"{item['manifest']}|{sources.identity(item)}": item.get('version') for item in items}
    before, after = versions(previous.get('dependencies', [])), versions(report['dependencies'])
    report['changes_since_ensure'] = {'added': sorted(after.keys() - before.keys()), 'removed': sorted(before.keys() - after.keys()),
                                      'version_changed': sorted(key for key in before.keys() & after.keys() if before[key] != after[key]),
                                      'manifests_changed': previous.get('fingerprint') != report['fingerprint']}
    return report


def check(root, project, exact=False, transitive=False):
    """Read-only, offline command: no network, cache writes or package-manager execution."""
    return add_documentation(inventory(project, transitive), root, exact)


def ensure(root, project, exact=False, transitive=False, refresh=False):
    report = check(root, project, exact, transitive)
    downloaded, failures = set(), []
    with core.lock(root):
        configured = configurations(root)
        for dep in report['dependencies']:
            if dep['resolution'] != 'resolved' or dep['registry'] != 'public' or dep['docs']['status'] == 'unsupported-exact':
                continue
            target = documentation_dependency(dep, configured)
            key = sources.identity(target) + ':' + (target['version'] if exact else str(target['major']))
            existing = cached_document(target, records(root), exact)
            if existing and not refresh or key in downloaded:
                continue
            try:
                file = sources.obtain(root, target, configured.get(sources.identity(target)), refresh=refresh)
                manifest = core.load_json(file)
                if not valid_snapshot(file, manifest):
                    raise ValueError('Downloaded snapshot failed checksum validation; run verify before reusing it')
                downloaded.add(key)
            except Exception as error:
                failures.append({'dependency': sources.identity(dep), 'error': str(error)})
        report = add_documentation(report, root, exact)
        selected = any(dep['docs'].get('snapshot') for dep in report['dependencies'])
        if selected and (not (root / 'index.sqlite3').exists() or core.load_json(root / 'index-state.json', {}).get('active') != core.active(root)):
            core.build_index(root)
        for dep in report['dependencies']:
            target = documentation_dependency(dep, configured)
            key = sources.identity(target) + ':' + (target['version'] if exact else str(target['major']))
            if key in downloaded and dep['docs'].get('snapshot'):
                dep['docs']['status'] = 'downloaded'
            for failure in failures:
                if failure['dependency'] == sources.identity(dep):
                    dep['docs'] = {'status': 'unavailable', 'warning': failure['error']}
        report['summary'] = dict(collections.Counter(dep['docs']['status'] for dep in report['dependencies']))
        report['fetch_errors'] = failures
        report['snapshots'] = sorted({dep['docs']['snapshot'] for dep in report['dependencies'] if dep['docs'].get('snapshot')})
        if scan(project, transitive)['fingerprint'] != report['fingerprint']:
            report['errors'].append({'error': 'Dependency manifests changed while fetching. Run ensure again; watch will detect the next change.'})
        core.write_json(project_file(root, project), report)
    return report


def project_search(root, project, query, package=None, ecosystem=None, limit=5, any_term=False):
    state = core.load_json(project_file(root, project))
    if state is None:
        raise ValueError('Run ensure --project first')
    current = check(root, project)
    if current['fingerprint'] != state['fingerprint']:
        raise ValueError('Dependency manifests changed; run ensure before project-specific searches')
    ids = sorted({dep['docs']['snapshot'] for dep in current['dependencies'] if dep['docs'].get('snapshot')
                  and (not package or dep['name'] == package) and (not ecosystem or dep['ecosystem'] == ecosystem)})
    return {'root': str(root), 'results': core.search(root, query, limit=limit, any_term=any_term, snapshot_ids=ids)}


def register(root, ecosystem, name, repository, paths, tag):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Use a public GitHub owner/repository')
    if not re.fullmatch(r'(?:@[A-Za-z0-9_.-]+/)?[A-Za-z0-9_./-]+', name):
        raise ValueError('Invalid dependency identity')
    if any(Path(value).is_absolute() or '..' in Path(value).parts for value in paths):
        raise ValueError('Documentation paths must stay within the maintainer repository')
    with core.lock(root):
        file = root / 'dependency-sources.json'
        data = core.load_json(file, {})
        data[ecosystem + ':' + name] = {'kind': 'github', 'repository': repository, 'paths': paths,
                                       'tag': tag, 'coverage': 'maintainer-docs', 'provenance': 'user-registered'}
        core.write_json(file, data)
    return {'registered': ecosystem + ':' + name, 'repository': repository, 'notes': 'Registration records your source choice; independently verify maintainer ownership and version coverage.'}


def output(report, table=False):
    if table and 'dependencies' in report:
        print(f"Dependencies: {report['project']}\nCache: {report['root']}\n")
        for dep in report['dependencies']:
            print(f"{dep['ecosystem']:8} {dep['name']:35} {(dep['version'] or '?'):16} {dep['docs']['status']}")
            if dep['docs'].get('coverage'):
                print('  Coverage: ' + dep['docs']['coverage'] + '; provenance: ' + dep['docs']['provenance'])
            if dep['docs'].get('warning'):
                print('  ' + dep['docs']['warning'])
        print('\n' + json.dumps(report['summary']))
        print('Changes since ensure: ' + json.dumps(report['changes_since_ensure']))
        for warning in report.get('warnings', []):
            print('Note: ' + warning)
        for error in [*report.get('errors', []), *report.get('fetch_errors', [])]:
            print('Error: ' + json.dumps(error))
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, help='Shared documentation cache; overrides DEPENDENCY_DOCS_HOME')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ['check', 'ensure', 'watch']:
        command = commands.add_parser(name)
        command.add_argument('--project', type=Path, default=Path.cwd())
        command.add_argument('--exact', action='store_true', help='Require the exact cached package version instead of major reuse')
        command.add_argument('--include-transitive', action='store_true', help='Also inventory npm/Yarn lockfile transitive entries')
        command.add_argument('--format', choices=['json', 'table'], default='json')
        command.add_argument('--strict', action='store_true', help='Exit 2 if any dependency lacks cached coverage')
        if name in {'ensure', 'watch'}:
            command.add_argument('--refresh', action='store_true')
        if name == 'watch':
            command.add_argument('--interval', type=float, default=5)
            command.add_argument('--once', action='store_true', help='Perform one watch/ensure cycle and exit')
    command = commands.add_parser('search')
    command.add_argument('query'); command.add_argument('--project', type=Path, required=True)
    command.add_argument('--package'); command.add_argument('--ecosystem'); command.add_argument('--limit', type=int, default=5)
    command.add_argument('--any', action='store_true')
    command = commands.add_parser('read'); command.add_argument('id'); command.add_argument('--offset', type=int, default=0); command.add_argument('--max-chars', type=int, default=6000)
    command = commands.add_parser('register-source'); command.add_argument('--ecosystem', required=True, choices=['npm', 'go', 'pypi', 'vcpkg', 'conan', 'unreal'])
    command.add_argument('--package', required=True); command.add_argument('--repo', required=True); command.add_argument('--path', action='append', default=[]); command.add_argument('--tag', default='v{version}')
    commands.add_parser('verify')
    args = parser.parse_args(argv)
    root = (args.root or data_root()).expanduser().resolve()
    if args.command in {'check', 'ensure', 'watch'}:
        if args.command == 'watch' and not 0.5 <= args.interval <= 30:
            parser.error('Watch interval must be 0.5..30 seconds')
        previous = None
        while True:
            report = check(root, args.project, args.exact, args.include_transitive)
            changed = report['fingerprint'] != previous
            if args.command != 'check' and (args.command != 'watch' or changed):
                report = ensure(root, args.project, args.exact, args.include_transitive, args.refresh)
                previous = report['fingerprint']
            if args.command != 'watch' or changed:
                output(report, args.format == 'table')
            if args.command != 'watch' or args.once:
                break
            time.sleep(args.interval)
        if report.get('errors') or report.get('fetch_errors'):
            return 1
        if args.strict and any(dep['docs']['status'] not in {'cached-exact', 'cached-major', 'downloaded', 'local'} for dep in report['dependencies']):
            return 2
        return 0
    if args.command == 'search':
        result = project_search(root, args.project, args.query, args.package, args.ecosystem, args.limit, args.any)
    elif args.command == 'read':
        if args.offset < 0 or not 1 <= args.max_chars <= 24000:
            parser.error('offset must be nonnegative and max-chars must be 1..24000')
        result = core.read_chunk(root, args.id, args.offset, args.max_chars)
    elif args.command == 'register-source':
        result = register(root, args.ecosystem, args.package, args.repo, args.path, args.tag)
    else:
        result = core.verify(root)
    output(result)
    return 1 if result.get('errors') else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)

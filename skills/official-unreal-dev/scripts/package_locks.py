"""Read generated Yarn Classic/Berry lock scalars; never load .pnp.cjs or run Yarn."""
import csv
import json
import re
from pathlib import Path


def exact_version(value):
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r'v?(\d+\.\d+(?:\.\d+)?(?:[a-zA-Z][\w.-]*|-[\w.-]+)?(?:\+[\w.-]+)?)', value.strip())
    return match[1] if match else None


def matches_version(version, constraint):
    """Common npm ranges only: None explicitly denotes an unimplemented range."""
    if constraint in {'*', 'latest', ''}:
        return True
    if '||' in constraint:
        results = [matches_version(version, item.strip()) for item in constraint.split('||')]
        return True if True in results else None if None in results else False
    stable = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)', version or '')
    if not stable:
        return version == constraint if exact_version(constraint) else None
    numbers = tuple(map(int, stable.groups()))
    match = re.fullmatch(r'([~^]?)v?(\d+)(?:\.(\d+|[xX*]))?(?:\.(\d+|[xX*]))?', constraint)
    if not match:
        return None
    operator, first, second, third = match.groups()
    minimum = (int(first), int(second) if second and second.isdigit() else 0, int(third) if third and third.isdigit() else 0)
    if operator == '^':
        upper = ((minimum[0] + 1, 0, 0) if minimum[0] or not second or not second.isdigit()
                 else (0, minimum[1] + 1, 0) if minimum[1] or not third or not third.isdigit()
                 else (0, 0, minimum[2] + 1))
        return minimum <= numbers < upper
    if operator == '~':
        upper = (minimum[0], minimum[1] + 1, 0) if second and second.isdigit() else (minimum[0] + 1, 0, 0)
        return minimum <= numbers < upper
    count = 1 + int(bool(second and second.isdigit())) + int(bool(second and second.isdigit() and third and third.isdigit()))
    return numbers[:count] == minimum[:count]


def scalar(value):
    value = value.strip()
    if value.startswith('"'):
        return json.loads(value)
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if value.startswith(('&', '*', '!', '|', '>')):
        raise ValueError('Unsupported generated lockfile scalar; resolve it with the package manager')
    return value


def parse_yarn(content):
    modern = bool(re.search(r'^__metadata:\s*$', content, re.M))
    if not modern and '# yarn lockfile v1' not in content:
        raise ValueError('Unrecognized Yarn lockfile format')
    entries, current = {}, None
    for line in content.splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if not line[0].isspace():
            if not line.endswith(':'):
                raise ValueError('Malformed Yarn lockfile entry')
            header = line[:-1]
            if header == '__metadata':
                current = None; continue
            if modern:
                selectors = re.split(r',\s+(?=(?:@[^/\s]+/)?[^@\s]+@)', scalar(header))
            else:
                selectors = next(csv.reader([header], skipinitialspace=True))
            current = {'format': 'yarn-modern' if modern else 'yarn-classic'}
            for selector in selectors:
                if '@' not in selector or selector in entries:
                    raise ValueError('Invalid or duplicate Yarn selector')
                entries[selector] = current
        elif current is not None and len(line) - len(line.lstrip()) == 2:
            if modern:
                field = re.match(r'  (version|resolution|linkType):\s*(.+)$', line)
            else:
                field = re.match(r'  (version|resolved|integrity)\s+(.+)$', line)
            if field:
                current[field[1]] = scalar(field[2])
    return entries


def parents(directory, root):
    current = directory
    while current.is_relative_to(root):
        yield current
        if current == root:
            break
        current = current.parent


def manager(directory, root):
    """Explicit packageManager wins; ambiguous npm/Yarn locks require a decision."""
    for parent in parents(directory, root):
        manifest = parent / 'package.json'
        if manifest.is_file():
            data = json.loads(manifest.read_text(encoding='utf-8-sig'))
            selected = data.get('packageManager', '')
            if selected.startswith(('npm@', 'yarn@', 'pnpm@')):
                return selected.split('@', 1)[0]
    for parent in parents(directory, root):
        yarn = (parent / 'yarn.lock').is_file()
        npm = (parent / 'package-lock.json').is_file() or (parent / 'npm-shrinkwrap.json').is_file()
        if yarn and npm:
            return 'ambiguous'
        if yarn:
            return 'yarn'
        if npm:
            return 'npm'
        if (parent / 'pnpm-lock.yaml').is_file():
            return 'pnpm'
    return 'npm'


def yarn_entry(directory, root, name, requested, cache=None):
    cache = cache if cache is not None else {}
    for parent in parents(directory, root):
        lock = parent / 'yarn.lock'
        if not lock.is_file():
            continue
        if lock.stat().st_size > 16 * 1024 * 1024:
            raise ValueError('Yarn lockfile exceeds 16 MiB')
        if lock not in cache:
            cache[lock] = parse_yarn(lock.read_text(encoding='utf-8-sig'))
        entries = cache[lock]
        for selector in [f'{name}@{requested}', f'{name}@npm:{requested}']:
            if selector in entries:
                return entries[selector]
        # Never select a different range/major merely because its package name matches.
        return None
    return None


def resolve_dependency(directory, root, alias, requested, cache=None):
    """Resolve one declared dependency using the active lock and installed metadata."""
    directory, root = Path(directory).resolve(), Path(root).resolve()
    selected = manager(directory, root)
    result = {'name': alias, 'version': None, 'status': 'unresolved', 'note': '', 'manager': selected, 'urls': []}
    if selected == 'ambiguous':
        return result | {'status': 'conflict', 'note': 'Both npm and Yarn locks exist; declare packageManager or resolve the active lockfile'}
    original = requested
    if requested.startswith('npm:'):
        protocol_range = requested[4:]
        if re.match(r'^[~^*<>=\d]', protocol_range):
            requested = protocol_range
        else:
            match = re.fullmatch(r'npm:((?:@[^/]+/)?[^@]+)(?:@(.+))?', requested)
            if not match:
                return result | {'note': 'Invalid npm alias'}
            result['name'], requested = match[1], match[2] or '*'
    if requested.startswith(('workspace:', 'file:', 'link:', 'portal:', 'git:', 'git+', 'https:', 'http:', 'github:')):
        return result | {'status': 'local', 'note': 'Local/workspace/Git/URL dependency; use its local source/docs'}
    def load(file):
        if file.stat().st_size > 16 * 1024 * 1024:
            raise ValueError('Package metadata exceeds 16 MiB')
        return json.loads(file.read_text(encoding='utf-8-sig'))
    installed = locked = None
    for parent in parents(directory, root):
        package = parent / 'node_modules' / alias / 'package.json'
        if package.is_file():
            actual = package.resolve()
            if not actual.is_relative_to(root) or 'node_modules' not in actual.relative_to(root).parts:
                return result | {'status': 'local', 'note': 'Linked local dependency'}
            installed = exact_version(load(package).get('version')); break
    entry = None
    if selected == 'yarn':
        entry = yarn_entry(directory, root, alias, original, cache)
        if entry:
            locator = entry.get('resolution', '')
            if entry.get('linkType') == 'soft' or any(token in locator for token in ['@workspace:', '@portal:', '@link:', '@file:']):
                return result | {'status': 'local', 'note': 'Yarn workspace/local locator'}
            locked = exact_version(entry.get('version'))
            if entry.get('resolved'):
                result['urls'].append(entry['resolved'])
            if '__archiveUrl=' in locator:
                from urllib.parse import unquote
                result['urls'].append(unquote(locator.split('__archiveUrl=', 1)[1].split('&', 1)[0]))
            if '@patch:' in locator:
                result['note'] = 'Yarn-patched package: verify local patches alongside upstream docs'
    elif selected == 'npm':
        for parent in parents(directory, root):
            lock = next((parent / name for name in ['npm-shrinkwrap.json', 'package-lock.json'] if (parent / name).is_file()), None)
            if lock is None:
                continue
            data = load(lock)
            for place in parents(directory, parent):
                key = (place.relative_to(parent) / 'node_modules' / alias).as_posix()
                entry = data.get('packages', {}).get(key)
                if entry:
                    break
            if not entry and data.get('lockfileVersion', 1) == 1:
                entry = data.get('dependencies', {}).get(alias)
            if entry:
                if entry.get('link'):
                    return result | {'status': 'local', 'note': 'Workspace link in npm lockfile'}
                locked = exact_version(entry.get('version'))
                if entry.get('resolved'):
                    result['urls'].append(entry['resolved'])
                if locked:
                    break
    if installed and locked and installed != locked:
        return result | {'status': 'conflict', 'note': f'Installed {installed} differs from locked {locked}'}
    version = locked or installed or exact_version(requested)
    if version and matches_version(version, requested) is False:
        return result | {'status': 'conflict', 'note': f'Resolved {version} does not satisfy manifest {requested}'}
    if version:
        if matches_version(version, requested) is None and not result['note']:
            result['note'] = 'Complex range not evaluated; using exact locked/installed version'
        return result | {'version': version, 'status': 'resolved'}
    return result | {'note': 'Resolve the lockfile/installed version; a range is not an exact version'}

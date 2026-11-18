"""Offline dependency discovery, Yarn resolution, provenance and cache behavior."""
from pathlib import Path
import base64
import gzip
import hashlib
import io
import json
import os
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import doclib as core
import dependency_docs as docs
import dependency_scan as scanner
import dependency_sources as sources
from package_locks import parse_yarn
from package_locks import matches_version


class DependencyTests(unittest.TestCase):
    def test_partial_major_zero_ranges_preserve_npm_caret_semantics(self):
        self.assertTrue(matches_version('0.9.3', '^0'))
        self.assertTrue(matches_version('0.0.9', '^0.0'))
        self.assertFalse(matches_version('0.1.0', '^0.0'))
        self.assertFalse(matches_version('0.0.2', '^0.0.1'))

    def test_yarn_npm_protocol_range_keeps_the_package_identity(self):
        self.yarn(modern=True, requested='npm:^5.3.0')
        dependency = scanner.scan(self.app)['dependencies'][0]
        self.assertEqual(dependency['name'], 'bootstrap')
        self.assertEqual(dependency['version'], '5.3.8')

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.app = self.base / 'app'; self.app.mkdir()
        self.cache = self.base / 'cache'
        self.environment = patch.dict(os.environ, {'NPM_CONFIG_REGISTRY': 'https://registry.npmjs.org', 'PIP_INDEX_URL': 'https://pypi.org/simple', 'GOPRIVATE': ''})
        self.environment.start()
        self.home = patch.object(Path, 'home', return_value=self.base / 'profile'); self.home.start()
    def tearDown(self):
        self.home.stop(); self.environment.stop(); self.temporary.cleanup()
    def write(self, name, value):
        file = self.app / name; file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(value) if isinstance(value, dict) else value, encoding='utf-8')
        return file
    def npm(self, version='5.3.8', constraint='^5.3.0'):
        self.write('package.json', {'dependencies': {'bootstrap': constraint}})
        self.write('package-lock.json', {'lockfileVersion': 3, 'packages': {'node_modules/bootstrap': {'version': version, 'resolved': f'https://registry.npmjs.org/bootstrap/-/bootstrap-{version}.tgz'}}})
    def yarn(self, modern=False, name='bootstrap', version='5.3.8', requested='^5.3.0', **fields):
        self.write('package.json', {'packageManager': 'yarn@4.10.3' if modern else 'yarn@1.22.22', 'dependencies': {name: requested}})
        if modern:
            descriptor = requested if requested.startswith('npm:') else 'npm:' + requested
            content = f'__metadata:\n  version: 10\n\n"{name}@{descriptor}":\n  version: {version}\n  resolution: "{name}@npm:{version}"\n  linkType: hard\n'
        else:
            content = f'# yarn lockfile v1\n\n{name}@{requested}:\n  version "{version}"\n  resolved "https://registry.yarnpkg.com/{name}/-/{name}-{version}.tgz"\n'
        self.write('yarn.lock', content)
    def dependency(self, name='bootstrap', version='5.3.8', ecosystem='npm'):
        return {'ecosystem': ecosystem, 'name': name, 'version': version, 'major': version.split('.')[0]}
    def snapshot(self, dep, body=None):
        body = body or f"# Reference\n{dep['name']} major {dep['major']} documentation."
        return core.publish(self.cache, sources.source_id(dep), {'stack': 'dependency', 'repo': 'maintainer/example'}, dep['version'], sources.identity(dep) + dep['version'],
                            [('reference.md', body.encode(), 'https://example.org/docs', 'https://example.org/docs')],
                            extra={'dependency': sources.metadata(dep, 'maintainer-docs', 'test-source')})
    def mocked_fetch(self, root, dep, configuration=None, refresh=False):
        self.assertEqual(root, self.cache)
        return self.snapshot(dep)

    def test_check_is_offline_read_only_and_reports_exact_npm_versions(self):
        self.npm()
        with patch.object(sources, 'download', side_effect=AssertionError('network forbidden')), patch.object(core, 'run', side_effect=AssertionError('process forbidden')):
            result = docs.check(self.cache, self.app)
        item = result['dependencies'][0]
        self.assertEqual((item['version'], item['docs']['status']), ('5.3.8', 'missing'))
        self.assertFalse(self.cache.exists())

    def test_new_major_downloads_but_same_major_reuses_cache_without_network(self):
        self.npm(); self.snapshot(self.dependency(version='5.1.0'))
        with patch.object(sources, 'obtain', side_effect=AssertionError('must reuse cache')):
            result = docs.ensure(self.cache, self.app)
        self.assertEqual(result['dependencies'][0]['docs']['status'], 'cached-major')
        self.assertTrue((self.cache / 'index.sqlite3').exists())
        self.npm('6.0.0', '^6.0.0')
        with patch.object(sources, 'obtain', side_effect=self.mocked_fetch) as fetch:
            result = docs.ensure(self.cache, self.app)
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(result['dependencies'][0]['docs']['status'], 'downloaded')

    def test_exact_mode_does_not_accept_a_different_minor_snapshot(self):
        self.npm(); self.snapshot(self.dependency(version='5.1.0'))
        with patch.object(sources, 'obtain', side_effect=self.mocked_fetch) as fetch:
            result = docs.ensure(self.cache, self.app, exact=True)
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(result['dependencies'][0]['docs']['cached_version'], '5.3.8')

    def test_cache_identity_does_not_mix_different_libraries_with_the_same_major(self):
        self.npm(); self.snapshot(self.dependency(name='unrelated'))
        self.assertEqual(docs.check(self.cache, self.app)['dependencies'][0]['docs']['status'], 'missing')

    def test_adding_a_dependency_is_detected_and_only_missing_docs_are_fetched(self):
        self.npm()
        with patch.object(sources, 'obtain', side_effect=self.mocked_fetch):
            docs.ensure(self.cache, self.app)
        self.write('package.json', {'dependencies': {'bootstrap': '^5.3.0', 'example': '1.2.3'}})
        report = docs.check(self.cache, self.app)
        self.assertTrue(any('example' in key for key in report['changes_since_ensure']['added']))
        with patch.object(sources, 'obtain', side_effect=self.mocked_fetch) as fetch:
            result = docs.ensure(self.cache, self.app)
        self.assertEqual([call.args[1]['name'] for call in fetch.call_args_list], ['example'])
        self.assertFalse(docs.check(self.cache, self.app)['changes_since_ensure']['manifests_changed'])

    def test_failed_fetch_is_not_reported_as_cached_and_does_not_remove_old_docs(self):
        self.npm(); old = self.snapshot(self.dependency(version='4.6.2'))
        with patch.object(sources, 'obtain', side_effect=RuntimeError('offline')):
            result = docs.ensure(self.cache, self.app)
        self.assertEqual(result['dependencies'][0]['docs']['status'], 'unavailable')
        self.assertTrue(result['fetch_errors']); self.assertTrue(old.exists())

    def test_dependency_selections_are_kept_by_existing_prune(self):
        self.npm(); pinned = self.snapshot(self.dependency(version='5.1.0'))
        with patch.object(sources, 'obtain', side_effect=AssertionError()):
            docs.ensure(self.cache, self.app)
        self.snapshot(self.dependency(version='6.0.0'))
        with core.lock(self.cache): core.prune(self.cache)
        self.assertTrue(pinned.exists())

    def test_project_search_excludes_other_majors_and_rejects_changed_manifests(self):
        self.npm(); self.snapshot(self.dependency(version='5.3.8'))
        with patch.object(sources, 'obtain', side_effect=AssertionError()): docs.ensure(self.cache, self.app)
        self.snapshot(self.dependency(version='6.0.0')); core.build_index(self.cache)
        rows = docs.project_search(self.cache, self.app, 'documentation')['results']
        self.assertEqual({row['version'] for row in rows}, {'5.3.8'})
        self.write('package.json', {'dependencies': {'bootstrap': '^6.0.0'}})
        with self.assertRaisesRegex(ValueError, 'changed'): docs.project_search(self.cache, self.app, 'documentation')

    def test_existing_next_docs_are_reused_by_identifiable_major(self):
        self.write('package.json', {'dependencies': {'next': '16.4.6'}})
        core.publish(self.cache, 'nextjs', {'stack': 'nextjs', 'repo': 'vercel/next.js'}, 'v16.4.1', 'next-revision', [('docs.md', b'# Routing\nRoutes.', 'https://nextjs.org/docs', 'https://nextjs.org/docs')])
        item = docs.check(self.cache, self.app)['dependencies'][0]
        self.assertEqual((item['docs']['status'], item['docs']['source']), ('cached-major', 'nextjs'))

    def test_sqlite_engine_and_driver_have_separate_documentation_identities(self):
        self.write('package.json', {'dependencies': {'sqlite3': '5.1.7'}})
        self.snapshot(self.dependency('sqlite', '3', 'engine'))
        result = docs.check(self.cache, self.app)
        self.assertEqual({item['name']: item['docs']['status'] for item in result['dependencies']}, {'sqlite3': 'missing', 'sqlite': 'cached-exact'})

    def test_major_only_sqlite_website_is_not_claimed_as_exact_patch_docs(self):
        self.write('vcpkg.json', {'dependencies': ['sqlite3'], 'overrides': [{'name': 'sqlite3', 'version': '3.46.0'}]})
        self.snapshot(self.dependency('sqlite', '3', 'engine'))
        item = docs.check(self.cache, self.app, exact=True)['dependencies'][0]
        self.assertEqual(item['docs']['status'], 'unsupported-exact')

    def test_unresolved_ranges_and_installed_lock_conflicts_are_not_guessed(self):
        self.write('package.json', {'dependencies': {'bootstrap': '^5.3.0'}})
        self.assertEqual(docs.check(self.cache, self.app)['dependencies'][0]['resolution'], 'unresolved')
        self.npm(); self.write('node_modules/bootstrap/package.json', {'name': 'bootstrap', 'version': '4.6.2'})
        item = docs.check(self.cache, self.app)['dependencies'][0]
        self.assertEqual(item['resolution'], 'conflict'); self.assertIsNone(item['version'])

    def test_stale_manifest_constraint_is_not_satisfied_by_old_lock(self):
        self.npm('5.3.8', '^6.0.0')
        self.assertEqual(docs.check(self.cache, self.app)['dependencies'][0]['resolution'], 'conflict')

    def test_private_registry_is_skipped_without_fetching_or_printing_credentials(self):
        self.write('package.json', {'dependencies': {'@company/private': '1.2.3'}})
        self.write('.npmrc', '@company:registry=https://secret:do-not-print@registry.company.invalid\n//registry.company.invalid/:_authToken=never-output\n')
        with patch.object(sources, 'obtain', side_effect=AssertionError('private request forbidden')):
            result = docs.ensure(self.cache, self.app)
        self.assertEqual(result['dependencies'][0]['docs']['status'], 'private')
        self.assertNotIn('do-not-print', json.dumps(result)); self.assertNotIn('never-output', json.dumps(result))

    def test_yarn_classic_resolves_without_node_modules_and_reuses_major_docs(self):
        self.yarn(); self.snapshot(self.dependency(version='5.1.0'))
        with patch.object(sources, 'obtain', side_effect=AssertionError('cached Yarn dependency must stay offline')):
            result = docs.ensure(self.cache, self.app)
        item = result['dependencies'][0]
        self.assertEqual((item['version'], item['package_manager'], item['docs']['status']), ('5.3.8', 'yarn', 'cached-major'))

    def test_modern_yarn_pnp_does_not_execute_pnp_or_require_an_install(self):
        self.yarn(modern=True)
        self.write('.pnp.cjs', "throw new Error('Do not execute project code')")
        result = docs.check(self.cache, self.app)
        self.assertEqual(result['dependencies'][0]['version'], '5.3.8')

    def test_yarn_grouped_classic_selectors_and_scoped_modern_packages(self):
        self.yarn()
        self.write('yarn.lock', '# yarn lockfile v1\nbootstrap@^5.3.0, bootstrap@~5.3.0:\n  version "5.3.8"\n')
        self.assertEqual(scanner.scan(self.app)['dependencies'][0]['version'], '5.3.8')
        self.yarn(modern=True, name='@scope/example', version='2.4.1', requested='^2.4.0')
        self.assertEqual(scanner.scan(self.app)['dependencies'][0]['version'], '2.4.1')

    def test_yarn_aliases_use_actual_publisher_identity(self):
        self.write('package.json', {'packageManager': 'yarn@4.10.3', 'dependencies': {'db': 'npm:sqlite3@^5.1.0'}})
        self.write('yarn.lock', '__metadata:\n  version: 10\n\n"db@npm:sqlite3@^5.1.0":\n  version: 5.1.7\n  resolution: "sqlite3@npm:5.1.7"\n  linkType: hard\n')
        item = scanner.scan(self.app)['dependencies'][0]
        self.assertEqual((item['name'], item['version'], item['alias']), ('sqlite3', '5.1.7', 'db'))

    def test_yarn_workspace_locators_are_local(self):
        self.write('package.json', {'packageManager': 'yarn@4.10.3', 'dependencies': {'shared': '*'}})
        self.write('yarn.lock', '__metadata:\n  version: 10\n\n"shared@npm:*":\n  version: 0.0.0-use.local\n  resolution: "shared@workspace:packages/shared"\n  linkType: soft\n')
        self.assertEqual(scanner.scan(self.app)['dependencies'][0]['resolution'], 'local')

    def test_package_manager_selects_yarn_over_stale_npm_lock(self):
        self.npm('4.6.2', '^5.3.0'); self.yarn(modern=True)
        self.assertEqual(scanner.scan(self.app)['dependencies'][0]['version'], '5.3.8')
        self.write('package.json', {'dependencies': {'bootstrap': '^5.3.0'}})
        self.assertEqual(scanner.scan(self.app)['dependencies'][0]['resolution'], 'conflict')

    def test_yarn_selector_for_another_range_is_not_reused(self):
        self.yarn(modern=True)
        self.write('yarn.lock', '__metadata:\n  version: 10\n\n"bootstrap@npm:^4.0.0":\n  version: 4.6.2\n  resolution: "bootstrap@npm:4.6.2"\n')
        self.assertEqual(scanner.scan(self.app)['dependencies'][0]['resolution'], 'unresolved')

    def test_yarn_private_scope_and_patched_locators_are_explicit(self):
        self.yarn(modern=True, name='@company/example', version='2.4.1', requested='^2.4.0')
        self.write('.yarnrc.yml', 'npmScopes:\n  company:\n    npmRegistryServer: "https://private.invalid"\n    npmAuthToken: "do-not-leak"\n')
        result = docs.check(self.cache, self.app)
        self.assertEqual(result['dependencies'][0]['docs']['status'], 'private')
        self.assertNotIn('do-not-leak', json.dumps(result))
        self.yarn(modern=True)
        self.write('yarn.lock', '__metadata:\n  version: 10\n\n"bootstrap@npm:^5.3.0":\n  version: 5.3.8\n  resolution: "bootstrap@patch:bootstrap@npm%3A5.3.8#local.patch"\n  linkType: hard\n')
        self.assertIn('patched', scanner.scan(self.app)['dependencies'][0]['note'])

    def test_yarn_transitives_are_available_when_requested(self):
        self.yarn(modern=True)
        with (self.app / 'yarn.lock').open('a', encoding='utf-8') as stream:
            stream.write('\n"other@npm:^1.0.0":\n  version: 1.2.3\n  resolution: "other@npm:1.2.3"\n  linkType: hard\n')
        report = scanner.scan(self.app, include_transitive=True)
        self.assertTrue(any(item['name'] == 'other' and item['version'] == '1.2.3' for item in report['dependencies']))

    def test_main_stack_detection_supports_yarn_pnp_react_and_next(self):
        self.write('.git', 'boundary')
        self.write('package.json', {'packageManager': 'yarn@4.10.3', 'dependencies': {'react': '^19.0.0', 'next': '^16.0.0'}})
        self.write('yarn.lock', '__metadata:\n  version: 10\n\n"react@npm:^19.0.0":\n  version: 19.3.1\n  resolution: "react@npm:19.3.1"\n\n"next@npm:^16.0.0":\n  version: 16.4.6\n  resolution: "next@npm:16.4.6"\n')
        self.assertEqual(core.detect(self.app)['versions'], {'react': '19.3.1', 'next': '16.4.6'})

    def test_go_replacements_and_workspace_modules_are_not_misidentified(self):
        self.write('go.mod', 'module example.com/app\ngo 1.26\nrequire (\n modernc.org/sqlite v1.62.0\n example.com/shared v0.1.0\n)\nreplace modernc.org/sqlite => github.com/mattn/go-sqlite3 v1.14.32\n')
        self.write('shared/go.mod', 'module example.com/shared\ngo 1.26\n')
        self.write('go.work', 'go 1.26\nuse (\n .\n ./shared\n)\n')
        entries = {item['name']: item for item in scanner.scan(self.app)['dependencies']}
        self.assertEqual(entries['github.com/mattn/go-sqlite3']['version'], '1.14.32')
        self.assertEqual(entries['example.com/shared']['resolution'], 'local')

    def test_pypi_lock_resolution_and_cpp_plugins_are_inventoried(self):
        self.write('pyproject.toml', '[project]\nname="demo"\ndependencies=["requests>=2"]\n')
        self.write('uv.lock', '[[package]]\nname="requests"\nversion="2.32.5"\n[package.source]\nregistry="https://pypi.org/simple"\n')
        self.write('vcpkg.json', {'dependencies': ['sqlite3'], 'overrides': [{'name': 'sqlite3', 'version': '3.46.0'}]})
        self.write('Game.uproject', {'Plugins': [{'Name': 'UnknownPlugin', 'Enabled': True}]})
        entries = {item['name']: item for item in scanner.scan(self.app)['dependencies']}
        self.assertEqual(entries['requests']['version'], '2.32.5')
        self.assertEqual(entries['sqlite3']['version'], '3.46.0')
        self.assertEqual(entries['UnknownPlugin']['resolution'], 'unresolved')

    def test_cli_check_strict_exit_and_watch_once(self):
        self.npm()
        with patch('sys.stdout', new_callable=io.StringIO):
            self.assertEqual(docs.main(['--root', str(self.cache), 'check', '--project', str(self.app), '--strict']), 2)
            with patch.object(sources, 'obtain', side_effect=self.mocked_fetch):
                self.assertEqual(docs.main(['--root', str(self.cache), 'watch', '--project', str(self.app), '--once']), 0)
        self.assertEqual(docs.check(self.cache, self.app)['dependencies'][0]['docs']['status'], 'cached-exact')


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.dep = {'ecosystem': 'npm', 'name': 'example-package', 'version': '1.2.3', 'major': '1'}
    def tearDown(self): self.temp.cleanup()
    def artifact(self):
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode='w') as tar:
            for name, data in [('package/README.md', b'# API\nPublisher documentation.'), ('package/LICENSE', b'Example license.'), ('package/postinstall.js', b'throw new Error("never execute")')]:
                info = tarfile.TarInfo(name); info.size = len(data); tar.addfile(info, io.BytesIO(data))
        artifact = gzip.compress(stream.getvalue())
        metadata = {'name': self.dep['name'], 'version': self.dep['version'], 'dist': {'tarball': 'https://registry.npmjs.org/example-package/-/example-package-1.2.3.tgz', 'integrity': 'sha512-' + base64.b64encode(hashlib.sha512(artifact).digest()).decode()}}
        return artifact, metadata
    def test_npm_provider_verifies_release_and_stores_docs_without_package_code(self):
        artifact, metadata = self.artifact()
        with patch.object(sources, 'fetch_json', return_value=metadata), patch.object(sources, 'download', return_value=artifact), patch.object(core, 'run', side_effect=AssertionError('must not execute package code')):
            file = sources.npm_docs(self.root, self.dep)
        manifest = core.load_json(file)
        self.assertEqual({entry['path'] for entry in manifest['files']}, {'README.md', 'LICENSE'})
        self.assertEqual(manifest['dependency']['coverage'], 'published-readme')
    def test_corrupt_npm_artifact_is_rejected_before_publishing(self):
        artifact, metadata = self.artifact()
        with patch.object(sources, 'fetch_json', return_value=metadata), patch.object(sources, 'download', return_value=artifact + b'bad'):
            with self.assertRaisesRegex(ValueError, 'integrity'): sources.npm_docs(self.root, self.dep)
        self.assertEqual(list(core.manifests(self.root)), [])
    def test_archive_expansion_limit_is_enforced(self):
        artifact, metadata = self.artifact()
        with patch.object(sources, 'fetch_json', return_value=metadata), patch.object(sources, 'download', return_value=artifact), patch.object(sources, 'UNPACK_LIMIT', 100):
            with self.assertRaisesRegex(ValueError, 'unpack limit'): sources.npm_docs(self.root, self.dep)
    def test_redirect_hosts_and_documentation_credentials_are_rejected(self):
        for url in ['http://registry.npmjs.org/a', 'https://localhost/a', 'https://u:p@registry.npmjs.org/a', 'https://registry.npmjs.org:8443/a']:
            with self.assertRaises(ValueError): sources.allowed_url(url, {'registry.npmjs.org'})
        redirect = sources.Redirects({'registry.npmjs.org'})
        with self.assertRaises(ValueError): redirect.redirect_request(None, None, 302, '', {}, 'https://private.invalid/a')
    def test_pypi_provider_records_exact_publisher_description(self):
        dep = {'ecosystem': 'pypi', 'name': 'example-package', 'version': '2.1.0', 'major': '2'}
        with patch.object(sources, 'fetch_json', return_value={'info': {'name': 'Example_Package', 'version': '2.1.0', 'description': 'Maintainer reference.', 'license': 'Example license'}}):
            manifest = core.load_json(sources.pypi_docs(self.root, dep))
        self.assertEqual(manifest['dependency']['provenance'], 'publisher-registry-description')
    def test_catalog_repository_must_match_publisher_metadata(self):
        with patch.object(sources, 'fetch_json', return_value={'repository': {'url': 'https://github.com/other/repository'}}):
            with self.assertRaisesRegex(ValueError, 'does not match'): sources.github_docs(self.root, self.dep, {'repository': 'maintainer/docs', 'paths': []})

    def test_curated_sources_support_new_and_old_documentation_layouts(self):
        configuration = {'repository': 'maintainer/docs', 'path_sets': [['site/src/content/docs'], ['site/content/docs/{major}.{minor}']], 'tag': 'v{version}'}
        metadata = [{'repository': {'url': 'https://github.com/maintainer/docs.git'}}, {'full_name': 'maintainer/docs', 'private': False}]
        expected = self.root / 'manifest.json'
        with patch.object(sources, 'fetch_json', side_effect=metadata), patch.object(core, 'sync_repo', side_effect=[RuntimeError('Configured documentation path missing at v1.2.3: site/src/content/docs'), (expected, True)]) as fetch:
            self.assertEqual(sources.github_docs(self.root, self.dep, configuration), expected)
        self.assertEqual([call.args[2]['paths'] for call in fetch.call_args_list], [['site/src/content/docs'], ['site/content/docs/1.2']])


if __name__ == '__main__': unittest.main()

"""Offline tests of version selection, bounded retrieval, and snapshot preservation."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import doclib


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def snapshot(self, version, content):
        return doclib.publish(self.root, "nextjs", {"stack": "nextjs", "repo": "vercel/next.js"},
                              version, version, [("docs/cache.md", content.encode(),
                                                  "https://github.com/vercel/next.js", "https://nextjs.org/docs")])

    def test_version_filter_and_archived_snapshot_survive_reindex(self):
        old = self.snapshot("v15.0.0", "# Cache\n\nCache behavior for older routers.\n")
        new = self.snapshot("v16.0.0", "# Cache\n\nCache behavior for newer routers.\n")
        doclib.build_index(self.root)
        rows = doclib.search(self.root, "cache", stack="nextjs")
        self.assertEqual({r["version"] for r in rows}, {"v16.0.0"})
        rows = doclib.search(self.root, "cache", version="v15.0.0")
        self.assertEqual({r["version"] for r in rows}, {"v15.0.0"})
        self.assertTrue(old.exists() and new.exists())
        self.assertEqual(doclib.verify(self.root)["errors"], [])

    def test_read_pagination_loses_no_text(self):
        self.snapshot("v16.0.0", "# API\n\n" + "A useful cache sentence. " * 50)
        doclib.build_index(self.root)
        row = doclib.search(self.root, "cache")[0]
        first = doclib.read_chunk(self.root, row["id"], max_chars=41)
        self.assertEqual(len(first["text"]), 41)
        second = doclib.read_chunk(self.root, row["id"], offset=first["next_offset"], max_chars=24000)
        whole = doclib.read_chunk(self.root, row["id"], max_chars=24000)
        self.assertEqual(first["text"] + second["text"], whole["text"])

    def test_code_fence_heading_does_not_split_a_section(self):
        text = "# Guide\n\n```python\n# a code comment\nprint('x')\n```\n\n## Real heading\nText"
        parts = list(doclib.chunks(text, "fallback"))
        self.assertEqual(len(parts), 2)
        self.assertIn("# a code comment", parts[0][-1])
        self.assertEqual(parts[1][1], "Real heading")

    def test_read_can_follow_neighboring_sections(self):
        self.snapshot("v16.0.0", "# Cache\nOverview.\n\n## API {/*api*/}\nCache contract.\n\n## Examples\nUsage.\n")
        doclib.build_index(self.root)
        row = next(r for r in doclib.search(self.root, "contract") if r["heading"] == "API")
        section = doclib.read_chunk(self.root, row["id"])
        self.assertEqual(section["previous_section"]["heading"], "Cache")
        self.assertEqual(section["next_section"]["heading"], "Examples")

    def test_query_punctuation_is_not_fts_syntax(self):
        self.snapshot("v16.0.0", "# API\n\nCache behavior.\n")
        doclib.build_index(self.root)
        self.assertTrue(doclib.search(self.root, 'cache"*'))
        with self.assertRaises(ValueError):
            doclib.search(self.root, '"*')

    def test_project_resolves_lockfile_and_does_not_treat_range_as_exact(self):
        doclib.write_json(self.root / "package.json", {"dependencies": {"next": "^15.0.0", "react": "^19.0.0"}})
        doclib.write_json(self.root / "package-lock.json", {"packages": {"node_modules/next": {"version": "15.4.1"}}})
        info = doclib.detect(self.root)
        self.assertEqual(info["versions"]["next"], "15.4.1")
        self.assertNotIn("react", info["versions"])
        self.assertTrue(info["warnings"])

    def test_cached_ensure_needs_no_network_and_no_reindex(self):
        self.snapshot("v16.0.0", "# Cache\n\nCache behavior.\n")
        for source in ["css", "javascript", "web-apis"]:
            doclib.publish(self.root, source, doclib.SOURCES[source], "main", "revision-1",
                           [("reference.md", b"# Reference\nBrowser documentation.\n", "https://github.com/mdn/content", "https://developer.mozilla.org")])
        doclib.build_index(self.root)
        doclib.write_json(self.root / "package.json", {"dependencies": {"next": "16.0.0"}})
        with patch.object(doclib, "fetch_json", side_effect=AssertionError("Unexpected network request")), \
             patch.object(doclib, "run", side_effect=AssertionError("Unexpected subprocess")), \
             patch.object(doclib, "build_index", side_effect=AssertionError("Unexpected rebuild")):
            result = doclib.ensure(self.root, self.root, {})
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["snapshots"]), 4)

    def test_mdn_canonical_link_uses_frontmatter_slug(self):
        page = doclib.canonical(doclib.SOURCES["javascript"],
                               "files/en-us/web/javascript/reference/global_objects/promise/index.md",
                               "---\ntitle: Promise\nslug: Web/JavaScript/Reference/Global_Objects/Promise\n---\n")
        self.assertEqual(page, "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise")

    def test_plain_javascript_detection_skips_dependency_files(self):
        (self.root / "app.js").write_text("const answer = 42;", encoding="utf-8")
        dependency = self.root / "node_modules" / "unrelated"
        dependency.mkdir(parents=True)
        (dependency / "demo.html").write_text("<html></html>", encoding="utf-8")
        flags = doclib.detect(self.root)["web"]
        self.assertTrue(flags["javascript"])
        self.assertFalse(flags["browser"])
        self.assertFalse(flags["css"])

    def test_plain_website_automatically_gets_all_web_references(self):
        (self.root / "index.html").write_text("<!doctype html><title>Example</title>", encoding="utf-8")
        requested = []
        def download(root, source, spec, override=None, refresh=False):
            requested.append(source)
            path = doclib.publish(root, source, spec, "main", "revision-2",
                                  [("reference.md", b"# Layout\nCSS and JavaScript reference.\n", "https://github.com/mdn/content", "https://developer.mozilla.org")])
            return path, True
        with patch.object(doclib, "sync_repo", side_effect=download):
            result = doclib.ensure(self.root, self.root, {})
        self.assertEqual(set(requested), {"css", "javascript", "web-apis"})
        self.assertEqual(result["errors"], [])
        self.assertTrue(doclib.search(self.root, "layout", stack="css", snapshot_ids=result["snapshots"]))
        self.assertEqual({r["stack"] for r in doclib.search(self.root, "layout", stack="javascript")}, {"javascript"})

    def test_explicit_web_mode_prepares_an_empty_new_website(self):
        requested = []
        def download(root, source, spec, override=None, refresh=False):
            requested.append(source)
            path = doclib.publish(root, source, spec, "main", "revision-3",
                                  [("reference.md", b"# Reference\n", "https://github.com/mdn/content", "https://developer.mozilla.org")])
            return path, True
        with patch.object(doclib, "sync_repo", side_effect=download):
            result = doclib.ensure(self.root, self.root, {}, web=True)
        self.assertEqual(set(requested), {"css", "javascript", "web-apis"})
        self.assertEqual(result["errors"], [])

    def test_snapshot_traversal_is_rejected(self):
        with self.assertRaises(ValueError):
            doclib.safe_file(self.root, "../outside.md")

    def react_project(self, docs_major):
        doclib.publish(self.root, "react", doclib.SOURCES["react"], "main", f"react-{docs_major}",
                       [("learn.md", b"# Learn\nComponents.\n", "https://github.com/reactjs/react.dev", "https://react.dev")],
                       extra={"docs_major": docs_major})
        for source in ["css", "javascript", "web-apis"]:
            doclib.publish(self.root, source, doclib.SOURCES[source], "main", "revision-1",
                           [("reference.md", b"# Reference\n", "https://github.com/mdn/content", "https://developer.mozilla.org")])
        doclib.write_json(self.root / "react-majors.json", {"19": {"source": "react", "spec": doclib.SOURCES["react"]}})
        doclib.write_json(self.root / "package.json", {"dependencies": {"react": "19.0.0"}})
        with patch.object(doclib, "fetch_json", side_effect=AssertionError("Unexpected network request")), \
             patch.object(doclib, "run", side_effect=AssertionError("Unexpected subprocess")):
            return doclib.ensure(self.root, self.root, {})

    def test_saved_react_mapping_rejects_docs_refreshed_to_a_newer_major(self):
        result = self.react_project(20)
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("React 20", result["errors"][0])
        self.assertFalse(any(s.startswith("react-") for s in result["snapshots"]))

    def test_saved_react_mapping_accepts_docs_for_the_same_major(self):
        result = self.react_project(19)
        self.assertEqual(result["errors"], [])
        self.assertTrue(any(s.startswith("react-") for s in result["snapshots"]))

    def test_package_version_lookup_stops_at_repository_root(self):
        stray = self.root / "node_modules" / "react"
        stray.mkdir(parents=True)
        doclib.write_json(stray / "package.json", {"version": "18.0.0"})
        app = self.root / "app"
        (app / ".git").mkdir(parents=True)
        doclib.write_json(app / "package.json", {"dependencies": {"react": "^19.0.0"}})
        info = doclib.detect(app)
        self.assertNotIn("react", info["versions"])

    def test_bundled_doclib_copies_are_identical_and_work_without_web_sources(self):
        skills = Path(__file__).resolve().parents[1] / "skills"
        stack, unreal = (skills / name / "scripts" for name in ["official-stack-dev", "official-unreal-dev"])
        self.assertEqual((stack / "doclib.py").read_bytes(), (unreal / "doclib.py").read_bytes())
        self.assertFalse((unreal / "sources.json").exists())
        spec = importlib.util.spec_from_file_location("unreal_doclib", unreal / "doclib.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.SOURCES, {})

    def mdn(self, revision):
        return {source: doclib.publish(self.root, source, doclib.SOURCES[source], "main", revision,
                                       [("reference.md", f"# Reference\n{revision} docs.\n".encode(),
                                         "https://github.com/mdn/content", "https://developer.mozilla.org")])
                for source in ["css", "javascript", "web-apis"]}

    def test_prune_keeps_active_and_project_snapshots_and_removes_leftovers(self):
        unused = self.snapshot("v15.0.0", "# Cache\nOld.\n")
        pinned = self.snapshot("v15.1.0", "# Cache\nPinned.\n")
        current = self.snapshot("v16.0.0", "# Cache\nCurrent.\n")
        app = self.root / "app"
        app.mkdir()
        doclib.write_json(self.root / "projects/app.json", {"project": str(app), "snapshots": [pinned.parent.name]})
        gone = self.root / "projects/gone.json"
        doclib.write_json(gone, {"project": str(self.root / "deleted-app"), "snapshots": [unused.parent.name]})
        stray = self.root / ("active.json." + "0" * 32 + ".tmp")
        stray.write_text("{}")
        doclib.build_index(self.root)
        preview = doclib.prune(self.root, dry_run=True)
        self.assertEqual(preview["removed_snapshots"], [unused.parent.name])
        self.assertTrue(unused.exists() and gone.exists() and stray.exists())
        result = doclib.prune(self.root)
        self.assertEqual(result["forgotten_projects"], [str(self.root / "deleted-app")])
        self.assertFalse(unused.exists() or gone.exists() or stray.exists())
        self.assertTrue(pinned.exists() and current.exists())
        self.assertEqual(doclib.search(self.root, "cache", version="v15.0.0"), [])
        self.assertTrue(doclib.search(self.root, "cache", version="v15.1.0"))
        self.assertEqual(doclib.verify(self.root)["errors"], [])

    def test_update_refreshes_branch_docs_reselects_projects_and_prunes(self):
        old = self.mdn("revision-1")
        doclib.ensure(self.root, self.root, {}, web=True)
        def download(root, source, spec, override=None, refresh=False):
            path = doclib.publish(root, source, spec, "main", "revision-2",
                                  [("reference.md", b"# Reference\nrevision-2 docs.\n", "https://github.com/mdn/content", "https://developer.mozilla.org")])
            return path, True
        with patch.object(doclib, "sync_repo", side_effect=download):
            result = doclib.update(self.root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(sorted(result["pruned"]["removed_snapshots"]), sorted(p.parent.name for p in old.values()))
        self.assertFalse(any(p.exists() for p in old.values()))
        state = next((self.root / "projects").glob("*.json"))
        self.assertEqual(set(doclib.load_json(state)["snapshots"]), set(doclib.active(self.root).values()))

    def test_update_does_not_prune_after_a_failed_step(self):
        old = self.mdn("revision-1")
        self.mdn("revision-2")
        with patch.object(doclib, "sync_repo", side_effect=RuntimeError("offline")):
            result = doclib.update(self.root)
        self.assertTrue(result["errors"])
        self.assertIsNone(result["pruned"])
        self.assertTrue(all(p.exists() for p in old.values()))

    def test_failed_download_does_not_replace_existing_snapshot(self):
        self.snapshot("v16.0.0", "# Cache\n\nOriginal docs.\n")
        before = doclib.active(self.root)
        with patch.object(doclib, "run", side_effect=RuntimeError("offline")):
            with self.assertRaises(RuntimeError):
                doclib.sync_repo(self.root, "nextjs", doclib.SOURCES["nextjs"], "v16.1.0")
        self.assertEqual(doclib.active(self.root), before)


if __name__ == "__main__":
    unittest.main()

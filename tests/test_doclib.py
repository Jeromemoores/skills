"""Offline tests of version selection, bounded retrieval, and snapshot preservation."""
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

    def test_failed_download_does_not_replace_existing_snapshot(self):
        self.snapshot("v16.0.0", "# Cache\n\nOriginal docs.\n")
        before = doclib.active(self.root)
        with patch.object(doclib, "run", side_effect=RuntimeError("offline")):
            with self.assertRaises(RuntimeError):
                doclib.sync_repo(self.root, "nextjs", doclib.SOURCES["nextjs"], "v16.1.0")
        self.assertEqual(doclib.active(self.root), before)


if __name__ == "__main__":
    unittest.main()

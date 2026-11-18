"""Offline checks for engine matching, provenance, cache extraction, and reuse."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import unreal_docs as docs


def page(version="5.8", text="An Actor can be spawned into a world. " * 8):
    return f"<html><title>Actor Lifecycle | Unreal Engine {version} Documentation | Epic Developer Community</title><nav>GLOBAL NAVIGATION</nav><article><h1>Actor Lifecycle</h1><p>{text}</p><pre><code>if (A &lt; B) {{ DoWork(); }}</code></pre><script>SECRET_SCRIPT</script></article></html>".encode()


class UnrealDocsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "library"
        self.engine = self.base / "engine"
        docs.core.write_json(self.engine / "Engine/Build/Build.version", {
            "MajorVersion": 5, "MinorVersion": 8, "PatchVersion": 4})
        self.project = self.base / "game/Game.uproject"
        docs.core.write_json(self.project, {"EngineAssociation": "5.8"})

    def tearDown(self):
        self.temp.cleanup()

    def test_project_version_and_build_declarations(self):
        build = self.project.parent / "Source/Game/Game.Build.cs"
        build.parent.mkdir(parents=True)
        build.write_text("CppStandard = CppStandardVersion.Cpp20;", encoding="utf-8")
        result = docs.detect(self.project, self.engine)
        self.assertEqual(result["engine_version"], "5.8.4")
        self.assertEqual(result["engine_doc_version"], "5.8")
        self.assertEqual(len(result["cpp_declarations"]), 1)

    def test_engine_mismatch_and_silent_project_upgrade_are_rejected(self):
        with self.assertRaises(ValueError):
            docs.detect(self.project, self.engine, "5.9")
        with self.assertRaises(ValueError):
            docs.detect(None, self.engine, "5.8.3")

    def test_ambiguous_uproject_requires_explicit_file(self):
        docs.core.write_json(self.project.parent / "Other.uproject", {"EngineAssociation": "5.8"})
        with self.assertRaises(ValueError):
            docs.find_project(self.project.parent)

    def test_missing_machine_preference_falls_back_to_user_cache(self):
        folder = self.base / "portable-skill"
        docs.core.write_json(folder / "unreal-location.json", {"preferred_root": str(self.base / "absent-library")})
        with patch.object(docs, "HERE", folder), patch.dict(docs.os.environ, {"UNREAL_DOCS_HOME": "", "LOCALAPPDATA": str(self.base / "user-cache")}):
            self.assertEqual(docs.data_root(), self.base / "user-cache" / "unreal-dev-docs")

    def test_multiple_engines_without_version_are_not_guessed(self):
        with patch.object(docs, "engine_candidates", return_value=[self.engine, self.base / "other-engine"]):
            with self.assertRaises(ValueError):
                docs.detect()

    def test_epic_url_restricts_host_and_version(self):
        url = docs.epic_url("https://dev.epicgames.com/documentation/unreal-engine/objects-in-unreal-engine", "5.8")
        self.assertIn("/en-us/unreal-engine/", url)
        self.assertTrue(url.endswith("application_version=5.8"))
        for bad in ["https://example.com/documentation/en-us/unreal-engine/x", "https://dev.epicgames.com/account/x", "https://dev.epicgames.com/documentation/en-us/unreal-engine/x?application_version=5.9"]:
            with self.assertRaises(ValueError):
                docs.epic_url(bad, "5.8")

    def test_article_extraction_preserves_code_and_excludes_page_chrome(self):
        title, text = docs.parse_epic(page(), "5.8")
        self.assertEqual(title, "Actor Lifecycle")
        self.assertIn("if (A < B)", text)
        self.assertIn("```", text)
        self.assertNotIn("GLOBAL NAVIGATION", text)
        self.assertNotIn("SECRET_SCRIPT", text)

    def test_mismatched_or_shell_page_is_not_accepted(self):
        with self.assertRaises(ValueError):
            docs.parse_epic(page("5.9"), "5.8")
        with self.assertRaises(ValueError):
            docs.parse_epic(b"<html><title>Challenge</title></html>", "5.8")
        with self.assertRaises(ValueError):
            docs.parse_epic(b"<title>Unreal Engine 5.8 Documentation</title><article></article>", "5.8")

    def test_cached_page_reuse_needs_no_network(self):
        url = "https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-actor-lifecycle"
        with patch.object(docs, "request_bytes", return_value=page()):
            first, changed = docs.fetch_epic(self.root, url, "5.8")
        self.assertTrue(changed)
        with patch.object(docs, "request_bytes", side_effect=AssertionError("Unexpected network")):
            second, changed = docs.fetch_epic(self.root, url, "5.8")
        self.assertFalse(changed)
        self.assertEqual(first["sha256"], second["sha256"])

    def test_cached_corruption_is_detected(self):
        url = "https://dev.epicgames.com/documentation/en-us/unreal-engine/objects-in-unreal-engine"
        with patch.object(docs, "request_bytes", return_value=page()):
            meta, _ = docs.fetch_epic(self.root, url, "5.8")
        (self.root / ".cache/epic/5.8" / (meta["key"] + ".raw")).write_bytes(b"corrupt")
        with self.assertRaises(ValueError):
            docs.fetch_epic(self.root, url, "5.8")

    def test_new_page_is_available_to_existing_project_selection(self):
        with patch.object(docs, "request_bytes", return_value=page()):
            docs.fetch_epic(self.root, "https://dev.epicgames.com/documentation/en-us/unreal-engine/first", "5.8")
        first = docs.publish_epic(self.root, "5.8")
        key = docs.hashlib.sha256(docs.os.path.normcase(str(self.project.resolve())).encode()).hexdigest()[:20]
        docs.core.write_json(self.root / "projects" / (key + ".json"), {
            "snapshots": [docs.core.load_json(first)["id"]], "engine_doc_version": "5.8"})
        with patch.object(docs, "request_bytes", return_value=page(text="ReplicatedInventory " * 20)):
            docs.fetch_epic(self.root, "https://dev.epicgames.com/documentation/en-us/unreal-engine/second", "5.8")
        second = docs.publish_epic(self.root, "5.8")
        docs.core.build_index(self.root)
        ids = docs.project_snapshots(self.root, self.project)
        self.assertIn(docs.core.load_json(second)["id"], ids)
        self.assertTrue(docs.core.search(self.root, "ReplicatedInventory", stack="unreal", snapshot_ids=ids))

    def test_header_import_tracks_changed_source_with_same_engine_version(self):
        relative = "Engine/Source/Runtime/Example/Public/Thing.h"
        header = self.engine / relative
        header.parent.mkdir(parents=True)
        header.write_text("// Copyright holder\nclass Thing {};", encoding="utf-8")
        info = docs.detect(self.project, self.engine)
        config = dict(docs.CONFIG, engine_headers=[relative])
        with patch.object(docs, "CONFIG", config):
            first, _, _ = docs.import_headers(self.root, info)
            header.write_text("// Copyright holder\nclass Thing { int Value; };", encoding="utf-8")
            second, changed, _ = docs.import_headers(self.root, info)
        self.assertTrue(changed)
        self.assertNotEqual(first, second)
        self.assertTrue(first.exists())

    def test_microsoft_canonical_link(self):
        url = docs.core.canonical(docs.CONFIG["cpp-msvc"], "docs/cpp/move-constructors-and-move-assignment-operators-cpp.md")
        self.assertEqual(url, "https://learn.microsoft.com/en-us/cpp/cpp/move-constructors-and-move-assignment-operators-cpp")

    def test_same_second_snapshots_select_latest_write(self):
        first = docs.core.publish(self.root, "example", {"stack": "cpp"}, "main", "revision-z",
                                  [("first.md", b"# First\n", "https://example.com", "https://example.com")])
        second = docs.core.publish(self.root, "example", {"stack": "cpp"}, "main", "revision-a",
                                   [("second.md", b"# Second\n", "https://example.com", "https://example.com")])
        for file in [first, second]:
            meta = docs.core.load_json(file)
            meta["downloaded_at"] = "2026-01-01T00:00:00+00:00"
            docs.core.write_json(file, meta)
        docs.os.utime(first, ns=(1000000000, 1000000000))
        docs.os.utime(second, ns=(2000000000, 2000000000))
        self.assertEqual(docs.core.cached(self.root, "example", "main"), second)

    def run_update(self, errors):
        docs.core.write_json(self.root / "projects/game.json", {"project": str(self.project), "topics": ["networking"]})
        docs.core.write_json(self.root / "projects/gone.json", {"project": str(self.base / "Gone.uproject")})
        calls = []
        def prepare(root, refresh=False, **options):
            calls.append((refresh, options))
            return {"project": str(options.get("project")), "engine_doc_version": "5.8", "snapshots": [], "errors": errors}
        with patch.object(docs, "prepare", side_effect=prepare), \
             patch.object(docs.core, "prune", return_value={"removed_snapshots": []}) as prune:
            result = docs.update(self.root)
        self.assertEqual(calls, [(True, {"project": self.project, "topics": ["networking"]})])
        return result, prune

    def test_update_refreshes_recorded_projects_and_tolerates_missing_pages(self):
        result, prune = self.run_update([{"page": "missing-page", "error": "404"}])
        prune.assert_called_once()
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["page_errors"]), 1)

    def test_update_source_failure_skips_pruning(self):
        result, prune = self.run_update([{"source": "cpp-msvc", "error": "offline"}])
        prune.assert_not_called()
        self.assertIsNone(result["pruned"])


if __name__ == "__main__":
    unittest.main()

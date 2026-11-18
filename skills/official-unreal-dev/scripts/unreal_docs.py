#!/usr/bin/env python3
"""Version-aware Unreal/C++ documentation cache. No editor or project mutations."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

import doclib as core

HERE = Path(__file__).resolve().parent
CONFIG = core.load_json(HERE / "game-sources.json")


def data_root():
    if os.environ.get("UNREAL_DOCS_HOME"):
        return Path(os.environ["UNREAL_DOCS_HOME"]).expanduser().resolve()
    preferred = core.load_json(HERE / "unreal-location.json", {}).get("preferred_root")
    if preferred and (Path(preferred) / "unreal_docs.py").is_file():
        return Path(preferred).resolve()
    if (HERE / "README.md").is_file():
        return HERE
    return Path(os.environ.get("LOCALAPPDATA", Path.home() / ".cache")) / "unreal-dev-docs"


def doc_version(value):
    if not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", value or ""):
        raise ValueError("Use an explicit Unreal version such as 5.8 or 5.8.4")
    return ".".join(value.split(".")[:2])


def find_project(path):
    path = path.expanduser().resolve()
    if path.is_file():
        if path.suffix.lower() != ".uproject":
            raise ValueError("Project file must be a .uproject")
        return path
    if not path.is_dir():
        raise ValueError("Project directory does not exist")
    for directory in [path, *path.parents]:
        files = list(directory.glob("*.uproject"))
        if len(files) == 1:
            return files[0]
        if len(files) > 1:
            raise ValueError("Multiple .uproject files; pass the intended file explicitly")
        if (directory / ".git").exists():
            break
    raise ValueError("No .uproject found; pass its path, or use sync --version for standalone docs")


def engine_candidates(association=""):
    candidates = []
    if os.environ.get("UNREAL_ENGINE_ROOT"):
        candidates.append(Path(os.environ["UNREAL_ENGINE_ROOT"]))
    if sys.platform == "win32":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Epic Games\Unreal Engine\Builds") as key:
                for i in range(winreg.QueryInfoKey(key)[1]):
                    name, value, _ = winreg.EnumValue(key, i)
                    if name.strip("{}") == association.strip("{}"):
                        candidates.append(Path(value))
        except OSError:
            pass
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\EpicGames\Unreal Engine") as parent:
                for i in range(winreg.QueryInfoKey(parent)[0]):
                    name = winreg.EnumKey(parent, i)
                    if association and name != association:
                        continue
                    with winreg.OpenKey(parent, name) as key:
                        value, _ = winreg.QueryValueEx(key, "InstalledDirectory")
                        candidates.append(Path(value))
        except OSError:
            pass
    base = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Epic Games"
    if base.exists():
        candidates.extend(sorted(base.glob("UE_" + association if association else "UE_*"), reverse=True))
    return list(dict.fromkeys(p.resolve() for p in candidates if (p / "Engine/Build/Build.version").is_file()))


def detect(project=None, engine=None, version=None):
    result = {"project": None, "engine_root": None, "engine_version": None,
              "engine_doc_version": None, "association": None, "cpp_declarations": [], "warnings": []}
    association = ""
    if project:
        file = find_project(project)
        data = core.load_json(file)
        association = str(data.get("EngineAssociation", ""))
        result.update(project=str(file), association=association)
        for pattern in ["Source/**/*.Build.cs", "Source/**/*.Target.cs"]:
            for file_cs in list(file.parent.glob(pattern))[:128]:
                for line in file_cs.read_text(encoding="utf-8-sig", errors="replace").splitlines():
                    if re.search(r"\b(CppStandard|CompilerVersion|ToolchainVersion|WindowsCompiler)\b", line):
                        result["cpp_declarations"].append({"path": str(file_cs), "declaration": line.strip()[:300]})
    expected = doc_version(version) if version else (association if re.fullmatch(r"\d+\.\d+", association) else None)
    if version and re.fullmatch(r"\d+\.\d+", association) and expected != association:
        raise ValueError(f"Project association {association} conflicts with requested documentation {expected}; do not silently upgrade the project")
    candidates = [Path(engine).expanduser().resolve()] if engine else engine_candidates(association if project else (expected or ""))
    if not engine and not expected and len(candidates) > 1:
        raise ValueError("Multiple engine installations are possible; pass --engine or --version instead of guessing")
    for candidate in candidates:
        file = candidate / "Engine/Build/Build.version"
        if not file.is_file():
            if engine:
                raise ValueError("Engine path must contain Engine/Build/Build.version")
            continue
        build = core.load_json(file)
        actual = f"{build['MajorVersion']}.{build['MinorVersion']}.{build['PatchVersion']}"
        if version and len(version.split(".")) == 3 and actual != version:
            if engine:
                raise ValueError(f"Installed patch {actual} does not match explicitly requested patch {version}")
            continue
        if expected and doc_version(actual) != expected:
            if engine:
                raise ValueError(f"Engine {actual} does not match requested/project documentation {expected}")
            continue
        result.update(engine_root=str(candidate), engine_version=actual,
                      engine_doc_version=doc_version(actual), engine_build=build)
        break
    if expected:
        result["engine_doc_version"] = expected
    if not result["engine_doc_version"]:
        raise ValueError("Cannot resolve the project's engine. Pass --engine or --version; no silent upgrade is performed")
    if not result["engine_root"]:
        result["warnings"].append("Matching engine installation unresolved; local header coverage and exact patch/compiler verification are unavailable.")
    result["warnings"].append("Epic pages are verified at major.minor; installed headers establish the exact local patch. C++ references do not establish compiler/engine feature support.")
    return result


class ArticleText(HTMLParser):
    """Extract Epic's document article, excluding page navigation and scripts."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.article = 0
        self.skip = 0
        self.pre = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "article":
            self.article += 1
        if not self.article:
            return
        if tag in {"script", "style", "nav"}:
            self.skip += 1
        if self.skip:
            return
        if tag in {"p", "div", "section", "tr", "ul", "ol"}:
            self.parts.append("\n")
        if re.fullmatch(r"h[1-6]", tag):
            self.parts.append("\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag == "br":
            self.parts.append("\n")
        elif tag in {"td", "th"}:
            self.parts.append(" | ")
        elif tag == "pre":
            self.pre += 1
            self.parts.append("\n```\n")
        elif tag == "code" and not self.pre:
            self.parts.append("`")

    def handle_endtag(self, tag):
        if not self.article:
            return
        if tag in {"script", "style", "nav"}:
            self.skip = max(0, self.skip - 1)
        elif not self.skip:
            if tag == "pre":
                self.pre = max(0, self.pre - 1)
                self.parts.append("\n```\n")
            elif tag == "code" and not self.pre:
                self.parts.append("`")
            elif tag in {"p", "div", "li", "tr", "section"} or re.fullmatch(r"h[1-6]", tag):
                self.parts.append("\n")
        if tag == "article":
            self.article -= 1

    def handle_data(self, data):
        if self.article and not self.skip:
            self.parts.append(data)


def epic_url(url, version):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname != "dev.epicgames.com" or parts.port:
        raise ValueError("Cache only HTTPS Epic documentation URLs")
    path = parts.path.replace("/documentation/unreal-engine/", "/documentation/en-us/unreal-engine/", 1)
    if not path.startswith("/documentation/en-us/unreal-engine/") or ".." in path:
        raise ValueError("Use the English Unreal Engine documentation path")
    params = urllib.parse.parse_qs(parts.query)
    if any(key not in {"application_version", "lang"} for key in params):
        raise ValueError("Unsupported documentation query parameters")
    if params.get("application_version", [version])[0] != version:
        raise ValueError("URL application_version conflicts with the requested engine version")
    return urllib.parse.urlunsplit(("https", "dev.epicgames.com", path.rstrip("/"),
                                   urllib.parse.urlencode({"application_version": version}), ""))


def request_bytes(url):
    request = urllib.request.Request(url, headers={"User-Agent": "official-unreal-docs/1.0", "Accept": "text/html,text/plain;q=0.9"})
    with urllib.request.urlopen(request, timeout=45) as response:
        body = response.read(10 * 1024 * 1024 + 1)
        if len(body) > 10 * 1024 * 1024:
            raise ValueError("Document exceeds the 10 MiB per-page limit")
        return body


def parse_epic(raw, version):
    html = raw.decode("utf-8", errors="replace")
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else ""
    if not re.search(r"Unreal Engine\s+" + re.escape(version) + r"\s+Documentation", title, re.I):
        raise ValueError(f"Epic page did not confirm Unreal {version}; refusing to relabel a missing/latest page ({title[:140]})")
    parser = ArticleText()
    parser.feed(html)
    body = "".join(parser.parts).strip()
    if len(body) < 100:
        raise ValueError("Epic document article is missing/too short; not caching a shell or challenge page")
    return title.split(" | ")[0], body


def fetch_epic(root, url, version, refresh=False):
    url = epic_url(url, version)
    key = hashlib.sha256(url.encode()).hexdigest()[:24]
    folder = root / ".cache" / "epic" / version
    meta_path, raw_path = folder / (key + ".json"), folder / (key + ".raw")
    if meta_path.exists() and raw_path.exists() and not refresh:
        metadata = core.load_json(meta_path)
        if hashlib.sha256(raw_path.read_bytes()).hexdigest() != metadata["sha256"]:
            raise ValueError(f"Cached Epic page checksum mismatch: {raw_path}")
        return metadata, False
    raw = request_bytes(url)
    title, body = parse_epic(raw, version)
    folder.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(raw)
    metadata = {"url": url, "title": title, "version": version, "downloaded_at": core.now(),
                "sha256": hashlib.sha256(raw).hexdigest(), "key": key}
    core.write_json(meta_path, metadata)
    return metadata, True


def publish_epic(root, version):
    folder = root / ".cache" / "epic" / version
    files = []
    digest = hashlib.sha256()
    for path in sorted(folder.glob("*.json")):
        meta = core.load_json(path)
        raw = (folder / (meta["key"] + ".raw")).read_bytes()
        if hashlib.sha256(raw).hexdigest() != meta["sha256"]:
            raise ValueError(f"Cached page checksum mismatch: {path}")
        title, body = parse_epic(raw, version)
        digest.update(meta["url"].encode() + raw)
        markdown = f"# {title}\n\nSource: {meta['url']}\nVerified documentation version: Unreal {version}\n\n{body}\n"
        files.extend([(meta["key"] + ".md", markdown.encode(), meta["url"], meta["url"]),
                      (meta["key"] + ".html.raw", raw, meta["url"], meta["url"])])
    if not files:
        raise ValueError("No verified Epic pages are available")
    return core.publish(root, "unreal-pages", {"stack": "unreal", "repo": "Epic Games public documentation"},
                        version, version + ":" + digest.hexdigest(), files,
                        "Selected Epic pages verified at major.minor, not a full site mirror or patch-level API guarantee. Raw HTML retained alongside extracted text.")


def sync_epic(root, version, topics, refresh=False):
    slugs = []
    for topic in topics:
        slugs.extend(CONFIG["epic_topics"][topic])
    errors, changed = [], False
    def fetch(slug):
        url = "https://dev.epicgames.com/documentation/en-us/unreal-engine/" + slug
        try:
            _, updated = fetch_epic(root, url, version, refresh)
            return updated, None
        except Exception as exc:
            return False, {"page": slug, "error": str(exc)}
    with ThreadPoolExecutor(max_workers=2) as pool:
        for updated, error in pool.map(fetch, sorted(set(slugs))):
            changed |= updated
            if error:
                errors.append(error)
                print(json.dumps(error), file=sys.stderr, flush=True)
    old = core.cached(root, "unreal-pages", version)
    path = publish_epic(root, version) if changed or not old else old
    core.activate(root, path)
    return path, changed, errors


def sync_guidelines(root, refresh=False):
    source = "cpp-core-guidelines"
    old = core.cached(root, source, "master")
    if old and not refresh:
        core.activate(root, old)
        return old, False
    spec = CONFIG[source]
    commit = core.fetch_json(f"https://api.github.com/repos/{spec['repo']}/commits/{spec['ref']}")["sha"]
    listing = core.fetch_json(f"https://api.github.com/repos/{spec['repo']}/contents?ref={commit}")
    names = [spec["file"], *[entry["name"] for entry in listing if entry["type"] == "file" and entry["name"].startswith("LICENSE")]]
    if len(names) == 1:
        raise ValueError("Core Guidelines license notice was not found; inspect upstream before caching")
    files = []
    for name in names:
        url = f"https://raw.githubusercontent.com/{spec['repo']}/{commit}/{name}"
        files.append((name, request_bytes(url), f"https://github.com/{spec['repo']}/blob/{commit}/{name}", spec["site"]))
    return core.publish(root, source, {"stack": "cpp", "repo": spec["repo"]}, "master", commit, files,
                        "Maintained C++ design guidance, not the normative ISO standard. Unreal object/reflection rules and actual compiler support still apply."), True


def import_headers(root, info, refresh=False):
    if not info["engine_root"]:
        return None, False, []
    engine = Path(info["engine_root"])
    version = info["engine_version"]
    files, missing = [], []
    digest = hashlib.sha256(json.dumps(info.get("engine_build", {}), sort_keys=True).encode())
    for relative in CONFIG["engine_headers"]:
        path = core.safe_file(engine, relative)
        if not path.is_file():
            missing.append(relative)
            continue
        raw = path.read_bytes()
        digest.update(relative.encode() + raw)
        wrapper = f"# Unreal {version}: {path.name}\n\nInstalled source: {path}\n\nThe indexed wrapper has extra heading/fence lines; consult the original header for exact source line numbers.\n\n```cpp\n{raw.decode('utf-8-sig', errors='replace')}\n```\n"
        files.extend([(relative + ".md", wrapper.encode(), str(path), str(path)),
                      (relative + ".raw", raw, str(path), str(path))])
    if not files:
        raise ValueError("The engine exposes no configured headers; cannot claim local API-source coverage")
    revision = version + ":" + digest.hexdigest()
    old = core.cached(root, "unreal-headers", version)
    if old and core.load_json(old)["revision"] == revision and not refresh:
        core.activate(root, old)
        return old, False, missing
    path = core.publish(root, "unreal-headers", {"stack": "unreal", "repo": "locally installed Epic engine headers"},
                        version, revision, files,
                        "Selected licensed headers from the installed engine; cached locally and excluded from portable skill bundles. Not the complete engine API.")
    return path, True, missing


def prepare(root, project=None, engine=None, version=None, topics=None, refresh=False, source="all"):
    info = detect(project, engine, version)
    info.update(root=str(root), snapshots=[], errors=[])
    changed = False
    with core.lock(root):
        if source in {"all", "cpp-msvc"}:
            try:
                path, new = core.sync_repo(root, "cpp-msvc", CONFIG["cpp-msvc"], refresh=refresh)
                info["snapshots"].append(core.load_json(path)["id"])
                changed |= new
            except Exception as exc:
                info["errors"].append({"source": "cpp-msvc", "error": str(exc)})
        if source in {"all", "cpp-core-guidelines"}:
            try:
                path, new = sync_guidelines(root, refresh)
                info["snapshots"].append(core.load_json(path)["id"])
                changed |= new
            except Exception as exc:
                info["errors"].append({"source": "cpp-core-guidelines", "error": str(exc)})
        if source in {"all", "unreal-pages"}:
            try:
                path, new, errors = sync_epic(root, info["engine_doc_version"], topics or ["core", "build"], refresh)
                info["snapshots"].append(core.load_json(path)["id"])
                info["errors"].extend(errors)
                changed |= new
            except Exception as exc:
                info["errors"].append({"source": "unreal-pages", "error": str(exc)})
        if source in {"all", "unreal-headers"}:
            try:
                path, new, missing = import_headers(root, info, refresh)
                if path:
                    info["snapshots"].append(core.load_json(path)["id"])
                if missing:
                    info["warnings"].append({"configured_headers_not_installed": missing})
                changed |= new
            except Exception as exc:
                info["errors"].append({"source": "unreal-headers", "error": str(exc)})
        if info["snapshots"] and (changed or not (root / "index.sqlite3").exists() or
                                  core.load_json(root / "index-state.json", {}).get("active") != core.active(root)):
            core.build_index(root)
        if info["project"] and source == "all":
            key = hashlib.sha256(os.path.normcase(info["project"]).encode()).hexdigest()[:20]
            core.write_json(root / "projects" / (key + ".json"), info)
    return info


def project_snapshots(root, project):
    file = find_project(project)
    key = hashlib.sha256(os.path.normcase(str(file)).encode()).hexdigest()[:20]
    state = core.load_json(root / "projects" / (key + ".json"))
    if not state:
        raise ValueError("Run ensure --project first for this .uproject")
    ids = state["snapshots"]
    latest = core.cached(root, "unreal-pages", state["engine_doc_version"])
    if latest:
        ids = [value for value in ids if not value.startswith("unreal-pages-")] + [core.load_json(latest)["id"]]
    return ids


def status(root):
    selected = core.active(root)
    result = []
    for path in core.manifests(root):
        manifest = core.load_json(path)
        result.append({key: manifest[key] for key in ["id", "source", "stack", "version", "revision", "downloaded_at", "notes"]} |
                      {"active": selected.get(manifest["source"]) == manifest["id"], "files": len(manifest["files"])})
    return {"root": str(root), "snapshots": result}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ["sync", "ensure", "detect"]:
        option = sub.add_parser(command)
        option.add_argument("--project", type=Path, default=Path.cwd() if command == "ensure" else None)
        option.add_argument("--engine", type=Path)
        option.add_argument("--version")
        if command != "detect":
            option.add_argument("--topics", nargs="+", choices=[*CONFIG["epic_topics"], "all"], default=["core", "build"])
            option.add_argument("--refresh", action="store_true")
            option.add_argument("--source", choices=["all", "cpp-msvc", "cpp-core-guidelines", "unreal-pages", "unreal-headers"], default="all")
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--stack", choices=["unreal", "cpp"])
    search.add_argument("--source")
    search.add_argument("--version")
    search.add_argument("--project", type=Path)
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--any", action="store_true")
    read = sub.add_parser("read")
    read.add_argument("id")
    read.add_argument("--offset", type=int, default=0)
    read.add_argument("--max-chars", type=int, default=8000)
    add = sub.add_parser("cache-url")
    add.add_argument("url")
    add.add_argument("--version", required=True)
    add.add_argument("--refresh", action="store_true")
    for command in ["status", "verify", "index"]:
        sub.add_parser(command)
    args = parser.parse_args(argv)
    root = (args.root or data_root()).expanduser().resolve()
    if args.command == "detect":
        result = detect(args.project, args.engine, args.version)
    elif args.command in {"sync", "ensure"}:
        topics = list(CONFIG["epic_topics"]) if "all" in args.topics else args.topics
        result = prepare(root, args.project, args.engine, args.version, topics, args.refresh, args.source)
    elif args.command == "search":
        ids = project_snapshots(root, args.project) if args.project else None
        result = {"root": str(root), "results": core.search(root, args.query, args.stack, args.version,
                  args.source, args.limit, args.any, ids)}
    elif args.command == "read":
        if args.offset < 0 or not 1 <= args.max_chars <= 24000:
            raise ValueError("offset must be nonnegative; max-chars must be 1..24000")
        result = core.read_chunk(root, args.id, args.offset, args.max_chars)
    elif args.command == "cache-url":
        version = doc_version(args.version)
        with core.lock(root):
            fetch_epic(root, args.url, version, args.refresh)
            path = publish_epic(root, version)
            core.build_index(root)
        result = core.load_json(path)
        result.pop("files", None)
    elif args.command == "verify":
        result = core.verify(root)
    elif args.command == "index":
        with core.lock(root):
            result = core.build_index(root)
    else:
        result = status(root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result.get("errors") or result.get("sqlite_integrity", "ok") != "ok" else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, core.sqlite3.Error) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)

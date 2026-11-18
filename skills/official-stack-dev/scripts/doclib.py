#!/usr/bin/env python3
"""Official documentation snapshots and bounded, offline full-text retrieval. Python 3.11+."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import urllib.request
import uuid

HERE = Path(__file__).resolve().parent
SOURCES = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
DOC_EXTENSIONS = {".md", ".mdx", ".html", ".article", ".txt"}
COPY_EXTENSIONS = DOC_EXTENSIONS | {".go", ".mod", ".sum", ".play", ".code", ".json", ".js", ".css"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load_json(path, default=None):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "official-stack-docs/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def run(args, cwd=None, timeout=180):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GOTOOLCHAIN="local", GOFLAGS="")
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed: {result.stderr.strip()[-2000:]}")
    return result.stdout.strip()


def default_root():
    if os.environ.get("OFFICIAL_DOCS_HOME"):
        return Path(os.environ["OFFICIAL_DOCS_HOME"]).expanduser().resolve()
    # The portable skill uses a machine-local preference only while its library exists.
    preferred = load_json(HERE / "library-location.json", {}).get("preferred_root")
    if preferred and (Path(preferred) / "doclib.py").is_file():
        return Path(preferred).resolve()
    if (HERE / "README.md").is_file():
        return HERE
    return Path(os.environ.get("LOCALAPPDATA", Path.home() / ".cache")) / "official-stack-docs"


@contextmanager
def lock(root):
    root.mkdir(parents=True, exist_ok=True)
    path = root / ".writer.lock"
    try:
        with path.open("x", encoding="utf-8") as f:
            f.write(json.dumps({"pid": os.getpid(), "created": now()}))
    except FileExistsError:
        raise RuntimeError(f"Another writer may be running. Inspect {path}; remove it only if its process has exited.")
    try:
        yield
    finally:
        path.unlink(missing_ok=True)


def safe_file(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError(f"Path escapes documentation snapshot: {relative}")
    return path


def manifests(root):
    return sorted((root / "snapshots").glob("*/*/manifest.json"))


def active(root):
    return load_json(root / "active.json", {})


def activate(root, manifest_path):
    manifest = load_json(manifest_path)
    selected = active(root)
    selected[manifest["source"]] = manifest["id"]
    write_json(root / "active.json", selected)


def cached(root, source, ref):
    matches = [(p, load_json(p)) for p in manifests(root)]
    matches = [(p, m) for p, m in matches if m["source"] == source and m["version"] == ref]
    return max(matches, key=lambda pair: (pair[1]["downloaded_at"], pair[0].stat().st_mtime_ns))[0] if matches else None


def resolve_ref(spec, override=None):
    ref = override or spec["ref"]
    if ref.startswith("npm:"):
        return "v" + fetch_json(f"https://registry.npmjs.org/{ref[4:]}/latest")["version"]
    if ref == "go:stable":
        return next(x["version"] for x in fetch_json("https://go.dev/dl/?mode=json") if x["stable"])
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/+-]*", ref) or ".." in ref:
        raise ValueError("Invalid Git ref")
    return ref


def canonical(spec, repo_path, text=None):
    kind = spec["kind"]
    path = repo_path
    if kind == "react":
        path = path.removeprefix("src/content/")
    elif kind == "react-legacy":
        path = "docs/" + path.removeprefix("content/docs/")
    elif kind == "nextjs":
        path = "/".join(re.sub(r"^\d+-", "", p) for p in path.removeprefix("docs/").split("/"))
    elif kind == "go-guides":
        path = path.removeprefix("_content/")
    elif kind == "go-language":
        path = {"doc/go_spec.html": "ref/spec", "doc/go_mem.html": "ref/mem"}.get(path, path)
    elif kind == "mdn":
        slug = re.search(r"^slug:\s*['\"]?([^\n'\"]+)", text or "", re.M)
        if slug:
            return spec["site"].rstrip("/") + "/" + slug.group(1).strip()
        path = path.removeprefix("files/en-us/")
    elif kind == "generic":
        path = path.removeprefix(spec.get("strip_prefix", ""))
    path = re.sub(r"\.(mdx?|html|article)$", "", path)
    path = re.sub(r"(^|/)index$", "", path)
    return spec["site"].rstrip("/") + "/" + path


def publish(root, source, spec, version, revision, files, notes=""):
    snapshot_id = source + "-" + hashlib.sha256(revision.encode()).hexdigest()[:16]
    destination = root / "snapshots" / source / snapshot_id
    if (destination / "manifest.json").exists():
        activate(root, destination / "manifest.json")
        return destination / "manifest.json"
    destination.mkdir(parents=True, exist_ok=True)
    entries = []
    for relative, data, url, page in files:
        out = safe_file(destination / "files", relative)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        entries.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest(),
                        "source_url": url, "canonical_url": page})
    docs = [f for f in entries if Path(f["path"]).suffix.lower() in DOC_EXTENSIONS]
    if not docs:
        raise RuntimeError(f"No documentation found for {source}@{version}; not activating it")
    manifest = {"schema": 1, "id": snapshot_id, "source": source, "stack": spec["stack"],
                "version": version, "revision": revision, "downloaded_at": now(),
                "repository": spec.get("repo", "installed Go toolchain"), "notes": notes, "files": entries}
    path = destination / "manifest.json"
    write_json(path, manifest)
    activate(root, path)
    print(f"Saved {source}@{version}: {len(docs)} documents", file=sys.stderr, flush=True)
    return path


def sync_repo(root, source, spec, override=None, refresh=False):
    # Exact tags and explicit refs are reused without network access on ensure.
    requested = override or spec["ref"]
    found = cached(root, source, requested)
    if found and not refresh:
        activate(root, found)
        return found, False
    ref = resolve_ref(spec, override)
    found = cached(root, source, ref)
    if found and not refresh:
        activate(root, found)
        return found, False
    checkout = root / ".cache" / source
    checkout.mkdir(parents=True, exist_ok=True)
    url = "https://github.com/" + spec["repo"] + ".git"
    if not (checkout / ".git").exists():
        run(["git", "init", str(checkout)])
        run(["git", "remote", "add", "origin", url], checkout)
        run(["git", "config", "core.longpaths", "true"], checkout)
        run(["git", "config", "core.autocrlf", "false"], checkout)
        run(["git", "sparse-checkout", "init", "--cone"], checkout)
    if run(["git", "remote", "get-url", "origin"], checkout) != url:
        raise RuntimeError(f"Unexpected remote in {checkout}")
    run(["git", "sparse-checkout", "set", *spec["paths"]], checkout)
    print(f"Fetching {spec['repo']}@{ref}...", file=sys.stderr, flush=True)
    run(["git", "-c", "http.version=HTTP/1.1", "fetch", "--depth=1", "--filter=blob:none", "origin", ref], checkout, 600)
    run(["git", "checkout", "--detach", "--force", "FETCH_HEAD"], checkout, 600)
    revision = run(["git", "rev-parse", "HEAD"], checkout)
    paths = []
    for directory in spec["paths"]:
        if not (checkout / directory).is_dir():
            raise RuntimeError(f"Configured documentation path missing at {ref}: {directory}")
        paths.extend(p for p in (checkout / directory).rglob("*") if p.is_file() and not p.is_symlink()
                     and p.suffix.lower() in COPY_EXTENSIONS)
    paths.extend(p for p in checkout.iterdir() if p.is_file() and
                 (p.name.startswith("LICENSE") or p.name in {"PATENTS", "AUTHORS", "CONTRIBUTORS"}))
    files = []
    for path in sorted(set(paths)):
        relative = path.relative_to(checkout).as_posix()
        data = path.read_bytes()
        files.append((relative, data,
                      f"https://github.com/{spec['repo']}/blob/{revision}/{relative}",
                      canonical(spec, relative, data.decode("utf-8", errors="replace"))))
    notes = "React documentation is maintained by major version, not exact minor/patch; verify API introductions separately." if spec["stack"] == "react" else ""
    if spec["kind"] == "mdn":
        notes = "MDN reference snapshot, not a browser-version guarantee. Raw Markdown macros do not include rendered compatibility tables; verify target browser/runtime support separately."
    return publish(root, source, spec, ref, revision, files, notes), True


def sync_stdlib(root, refresh=False):
    version = run(["go", "env", "GOVERSION"])
    found = cached(root, "go-stdlib", version)
    if found and not refresh:
        activate(root, found)
        return found, False
    goroot = Path(run(["go", "env", "GOROOT"]))
    packages = run(["go", "list", "std"], timeout=120).splitlines()
    packages = [p for p in packages if not p.startswith(("vendor/", "internal/", "cmd/")) and "/internal/" not in p]
    print(f"Reading {len(packages)} local standard library packages ({version})...", file=sys.stderr, flush=True)
    def capture(package):
        body = run(["go", "doc", "-all", package], timeout=60) + "\n"
        return (package + ".txt", body.encode("utf-8"),
                f"https://github.com/golang/go/tree/{version}/src/{package}", f"https://pkg.go.dev/{package}")
    with ThreadPoolExecutor(max_workers=6) as pool:
        files = list(pool.map(capture, packages))
    files.append(("LICENSE", (goroot / "LICENSE").read_bytes(), "https://go.dev/LICENSE", "https://go.dev/LICENSE"))
    return publish(root, "go-stdlib", {"stack": "go"}, version, version, files,
                   f"Generated with go doc -all from installed {version}; public standard library packages only."), True


class HTMLText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip += 1
        if tag in {"p", "div", "br", "pre", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")
        if tag in {"h1", "h2", "h3", "h4"}:
            self.parts.append("#" * int(tag[1]) + " ")
    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip = max(0, self.skip - 1)
        if tag in {"p", "div", "pre", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def extract(text, suffix):
    if suffix == ".html":
        parser = HTMLText()
        parser.feed(text)
        return re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", "".join(parser.parts))
    return text.replace("\r\n", "\n")


def chunks(text, fallback):
    lines = text.splitlines()
    title_match = re.search(r"^title:\s*['\"]?(.+?)['\"]?\s*$", text, re.M)
    first_heading = re.search(r"^#\s+(.+)$", text, re.M)
    title = (title_match or first_heading).group(1) if title_match or first_heading else fallback
    start, heading, size, fence = 0, title, 0, None
    for i, line in enumerate(lines):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        is_heading = re.match(r"^#{1,6}\s+(.+)", line) if fence is None else None
        is_go_decl = re.match(r"^(?:func|type|const|var)\s+\S+", line) if fence is None else None
        if i > start and (is_heading or is_go_decl or (size > 4500 and fence is None and not line.strip()) or size > 10000):
            body = "\n".join(lines[start:i]).strip()
            if body:
                yield title, heading, start + 1, i, body
            start, size = i, 0
        if is_heading:
            heading = re.sub(r"\s*\{(?:#[^}]+|/\*.*?\*/)\}\s*$", "", is_heading.group(1))
        elif is_go_decl:
            heading = line[:180]
        if marker:
            m = marker.group(1)
            if fence is None:
                fence = (m[0], len(m))
            elif m[0] == fence[0] and len(m) >= fence[1] and not line[marker.end():].strip():
                fence = None
        size += len(line) + 1
    body = "\n".join(lines[start:]).strip()
    if body:
        yield title, heading, start + 1, len(lines), body


def build_index(root):
    temporary = root / ("index-" + uuid.uuid4().hex + ".sqlite3")
    db = sqlite3.connect(temporary)
    try:
        db.executescript("""
        CREATE TABLE chunks (id TEXT UNIQUE, snapshot TEXT, source TEXT, stack TEXT, version TEXT,
          revision TEXT, active INTEGER, title TEXT, heading TEXT, path TEXT,
          start_line INTEGER, end_line INTEGER, body TEXT, source_url TEXT, canonical_url TEXT);
        CREATE INDEX filters ON chunks(stack, version, active);
        CREATE VIRTUAL TABLE search USING fts5(title, heading, body, content='chunks', content_rowid='rowid', tokenize='porter unicode61');
        """)
        selected = active(root)
        docs = 0
        for manifest_path in manifests(root):
            manifest = load_json(manifest_path)
            for entry in manifest["files"]:
                suffix = Path(entry["path"]).suffix.lower()
                if suffix not in DOC_EXTENSIONS:
                    continue
                path = safe_file(manifest_path.parent / "files", entry["path"])
                text = extract(path.read_text(encoding="utf-8", errors="replace"), suffix)
                docs += 1
                for title, heading, first, last, body in chunks(text, Path(entry["path"]).stem):
                    if suffix == ".txt":
                        title = Path(entry["path"]).with_suffix("").as_posix()
                    chunk_id = hashlib.sha256(f"{manifest['id']}:{entry['path']}:{first}".encode()).hexdigest()[:20]
                    db.execute("INSERT INTO chunks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                        chunk_id, manifest["id"], manifest["source"], manifest["stack"], manifest["version"],
                        manifest["revision"], int(selected.get(manifest["source"]) == manifest["id"]),
                        title, heading, str(path.relative_to(root)), first, last, body,
                        entry["source_url"], entry["canonical_url"]))
        db.execute("INSERT INTO search(search) VALUES('rebuild')")
        db.commit()
        count = db.execute("SELECT count(*) FROM chunks").fetchone()[0]
        db.close()
        os.replace(temporary, root / "index.sqlite3")
        write_json(root / "index-state.json", {"active": selected, "built_at": now()})
        print(f"Indexed {docs} documents / {count} sections", file=sys.stderr, flush=True)
        return {"documents": docs, "sections": count}
    finally:
        db.close()
        temporary.unlink(missing_ok=True)


@contextmanager
def connect(root):
    path = root / "index.sqlite3"
    if not path.exists():
        raise RuntimeError("No local index yet. Run sync or ensure first.")
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()


def search(root, query, stack=None, version=None, source=None, limit=5, any_term=False, snapshot_ids=None):
    terms = re.findall(r"\w+", query, re.UNICODE)
    if not terms:
        raise ValueError("Search needs at least one word or API name")
    match = (" OR " if any_term else " AND ").join('"' + t + '"' for t in terms[:24])
    clauses, values = ["search MATCH ?"], [match]
    for name, value in [("stack", stack), ("version", version), ("source", source)]:
        if value:
            clauses.append(f"c.{name} = ?")
            values.append(value)
    if snapshot_ids is not None:
        if not snapshot_ids:
            return []
        clauses.append("c.snapshot IN (" + ",".join("?" for _ in snapshot_ids) + ")")
        values.extend(snapshot_ids)
    elif not version:
        clauses.append("c.active = 1")
    sql = """SELECT c.id,c.stack,c.source,c.version,c.snapshot,c.title,c.heading,
             c.path,c.start_line,c.end_line,c.source_url,c.canonical_url,
             snippet(search,2,'[',']',' ... ',36) AS excerpt
             FROM search JOIN chunks c ON c.rowid=search.rowid WHERE """
    with connect(root) as db:
        rows = db.execute(sql + " AND ".join(clauses) + " ORDER BY bm25(search,4,6,1) LIMIT ?",
                          [*values, min(max(limit, 1), 20)]).fetchall()
    return [dict(row) for row in rows]


def read_chunk(root, chunk_id, offset=0, max_chars=8000):
    with connect(root) as db:
        row = db.execute("SELECT * FROM chunks WHERE id=?", (chunk_id,)).fetchone()
        if row is not None:
            previous = db.execute("SELECT id,heading FROM chunks WHERE path=? AND snapshot=? AND start_line<? ORDER BY start_line DESC LIMIT 1",
                                  (row["path"], row["snapshot"], row["start_line"])).fetchone()
            following = db.execute("SELECT id,heading FROM chunks WHERE path=? AND snapshot=? AND start_line>? ORDER BY start_line LIMIT 1",
                                   (row["path"], row["snapshot"], row["start_line"])).fetchone()
    if row is None:
        raise ValueError("Unknown section ID; search again after an index update")
    result = dict(row)
    body = result.pop("body")
    result["text"] = body[offset:offset + max_chars]
    result["total_characters"] = len(body)
    result["next_offset"] = offset + max_chars if offset + max_chars < len(body) else None
    result["previous_section"] = dict(previous) if previous else None
    result["next_section"] = dict(following) if following else None
    result["line_numbers"] = "Extracted text lines for HTML; original file lines for Markdown/plain text."
    return result


def package_version(project, name):
    # Installed packages and lockfiles, not dependency ranges, establish exact versions.
    for parent in [project, *project.parents]:
        package = parent / "node_modules" / name / "package.json"
        if package.exists():
            return load_json(package)["version"]
        lockfile = parent / "package-lock.json"
        if lockfile.exists():
            data = load_json(lockfile)
            package = data.get("packages", {}).get("node_modules/" + name, {})
            if package.get("version"):
                return package["version"]
            package = data.get("dependencies", {}).get(name, {})
            if package.get("version"):
                return package["version"]
    return None


def detect_web(project):
    """Bounded source-file discovery; skip dependency, build, and cache directories."""
    flags = {"javascript": False, "css": False, "browser": False}
    excluded = {"node_modules", ".git", ".next", "dist", "build", ".cache", "snapshots",
                ".validation", "__pycache__", ".venv", "venv", "vendor", "coverage"}
    count = 0
    for directory, dirs, files in os.walk(project):
        dirs[:] = sorted(d for d in dirs if d not in excluded and not Path(directory, d).is_symlink())
        for name in sorted(files):
            count += 1
            suffix = Path(name).suffix.lower()
            if suffix in {".js", ".mjs", ".cjs", ".ts"}:
                flags["javascript"] = True
            if suffix in {".css", ".scss", ".sass", ".less"}:
                flags["css"] = True
            if suffix in {".html", ".htm", ".jsx", ".tsx"}:
                return {"javascript": True, "css": True, "browser": True}
            if count >= 2000:
                return flags
    return flags


def detect(project):
    project = project.resolve()
    if not project.is_dir():
        raise ValueError("Project must be an existing directory")
    result = {"project": str(project), "versions": {}, "warnings": [], "web": detect_web(project)}
    for parent in [project, *project.parents]:
        package = parent / "package.json"
        if package.exists():
            data = load_json(package)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "react" in deps or "next" in deps:
                result["web"] = {"javascript": True, "css": True, "browser": True}
            for name in ["react", "next"]:
                if name not in deps:
                    continue
                value = package_version(parent, name)
                if not value and re.fullmatch(r"\d+\.\d+\.\d+(?:-[\w.-]+)?", deps[name]):
                    value = deps[name]
                if value:
                    result["versions"][name] = value
                else:
                    result["warnings"].append(f"Cannot resolve {name} from {deps[name]!r}. Install project dependencies or provide --{name}-version; pnpm/yarn lockfiles without installed packages require an explicit version.")
            break
        if (parent / ".git").exists():
            break
    for parent in [project, *project.parents]:
        mod = parent / "go.mod"
        if mod.exists():
            text = mod.read_text(encoding="utf-8")
            baseline = re.search(r"^go\s+(\d+\.\d+(?:\.\d+)?)", text, re.M)
            toolchain = re.search(r"^toolchain\s+(go\d+\.\d+\.\d+)", text, re.M)
            minimum = baseline.group(1) if baseline else None
            chosen = toolchain.group(1) if toolchain else None
            try:
                installed = run(["go", "env", "GOVERSION"], project)
                def parts(v):
                    return tuple(int(n) for n in re.findall(r"\d+", v)[:3])
                if not chosen and (not minimum or parts(installed) >= parts(minimum)):
                    chosen = installed
            except (OSError, RuntimeError):
                pass
            if not chosen and minimum:
                chosen = "go" + minimum + (".0" if minimum.count(".") == 1 else "")
            if chosen:
                result["versions"]["go"] = chosen
            break
        if (parent / ".git").exists():
            break
    return result


def react_spec(version):
    major = int(version.split(".")[0])
    spec = dict(SOURCES["react"])
    if major == 18:
        spec.update(ref="react-18", site="https://18.react.dev")
        return "react-18", spec
    if major in {16, 17}:
        spec.update(repo="reactjs/legacy.reactjs.org", ref=f"{major}.reactjs.org",
                    paths=["content/docs"], site=f"https://{major}.react.dev", kind="react-legacy")
        return f"react-{major}", spec
    # Current-major docs are not claimed to be an exact patch-version snapshot.
    latest = fetch_json("https://registry.npmjs.org/react/latest")["version"]
    if major != int(latest.split(".")[0]):
        raise ValueError(f"No configured React archive for major {major}; consult https://react.dev/versions")
    return "react", spec


def ensure(root, project, overrides, web=False):
    info = detect(project)
    info["versions"].update({key: value for key, value in overrides.items() if value})
    if web or "react" in info["versions"] or "next" in info["versions"]:
        info["web"] = {"javascript": True, "css": True, "browser": True}
    selected, errors, changed = [], [], False
    def obtain(source, spec, ref=None):
        nonlocal changed
        path, new = sync_repo(root, source, spec, ref)
        selected.append(load_json(path)["id"])
        changed |= new
    versions = info["versions"]
    with lock(root):
        if "react" in versions:
            try:
                # Reuse a previously resolved current-major mapping offline.
                mapping_file = root / "react-majors.json"
                mappings = load_json(mapping_file, {})
                major = versions["react"].split(".")[0]
                if major in mappings:
                    source, spec = mappings[major]["source"], mappings[major]["spec"]
                else:
                    source, spec = react_spec(versions["react"])
                    mappings[major] = {"source": source, "spec": spec}
                    write_json(mapping_file, mappings)
                obtain(source, spec)
                info["warnings"].append("React docs cover a major version; verify minor/patch API availability separately.")
            except Exception as exc:
                errors.append(str(exc))
        if "next" in versions:
            try:
                obtain("nextjs", SOURCES["nextjs"], "v" + versions["next"].removeprefix("v"))
            except Exception as exc:
                errors.append(str(exc))
        if "go" in versions:
            try:
                obtain("go-language", SOURCES["go-language"], versions["go"])
                obtain("go-guides", SOURCES["go-guides"])
                if shutil.which("go") and run(["go", "env", "GOVERSION"]) == versions["go"]:
                    path, new = sync_stdlib(root)
                    selected.append(load_json(path)["id"])
                    changed |= new
                else:
                    info["warnings"].append("Matching Go standard library is not installed; use version-specific upstream package docs for APIs.")
            except Exception as exc:
                errors.append(str(exc))
        for source, needed in [("css", info["web"]["css"]),
                               ("javascript", info["web"]["javascript"]),
                               ("web-apis", info["web"]["browser"])]:
            if needed:
                try:
                    obtain(source, SOURCES[source])
                except Exception as exc:
                    errors.append(str(exc))
        if selected and (changed or not (root / "index.sqlite3").exists() or
                         load_json(root / "index-state.json", {}).get("active") != active(root)):
            # active flags may change even when all snapshots are cached.
            build_index(root)
        info.update(snapshots=selected, errors=errors, root=str(root))
        if not versions and not any(info["web"].values()) and not info["warnings"]:
            info["warnings"].append("No supported project detected. Use --web for a new website, sync for latest docs, or pass explicit framework versions.")
        key = hashlib.sha256(str(project.resolve()).encode()).hexdigest()[:20]
        write_json(root / "projects" / (key + ".json"), info)
    return info


def verify(root):
    errors, count = [], 0
    for path in manifests(root):
        manifest = load_json(path)
        for entry in manifest["files"]:
            file = safe_file(path.parent / "files", entry["path"])
            count += 1
            if not file.exists() or hashlib.sha256(file.read_bytes()).hexdigest() != entry["sha256"]:
                errors.append(str(file))
    with connect(root) as db:
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        sections = db.execute("SELECT count(*) FROM chunks").fetchone()[0]
    return {"files_checked": count, "sections": sections, "sqlite_integrity": integrity, "errors": errors}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="Library data directory; overrides OFFICIAL_DOCS_HOME")
    sub = parser.add_subparsers(dest="command", required=True)
    sync = sub.add_parser("sync", help="Download latest stable official sources or a specified ref")
    sync.add_argument("--source", choices=[*SOURCES, "go-stdlib", "all"], default="all")
    sync.add_argument("--ref", help="Exact Git tag/branch/commit; requires one repository source")
    sync.add_argument("--refresh", action="store_true", help="Fetch upstream again; preserve previous snapshots")
    ens = sub.add_parser("ensure", help="Detect project versions and automatically cache missing docs")
    ens.add_argument("--project", type=Path, default=Path.cwd())
    ens.add_argument("--web", action="store_true", help="Ensure CSS, JavaScript, and common browser API docs, including for an empty new website")
    for name in ["react", "next", "go"]:
        ens.add_argument(f"--{name}-version")
    det = sub.add_parser("detect")
    det.add_argument("--project", type=Path, default=Path.cwd())
    find = sub.add_parser("search")
    find.add_argument("query")
    find.add_argument("--stack", choices=["react", "nextjs", "go", "css", "javascript"])
    find.add_argument("--source")
    find.add_argument("--version", help="Exact snapshot label (e.g. v16.4.6 or go1.26.4)")
    find.add_argument("--project", type=Path, help="Use only snapshots selected by ensure for this project")
    find.add_argument("--snapshot", action="append", help="Restrict to snapshot IDs returned by ensure")
    find.add_argument("--limit", type=int, default=5)
    find.add_argument("--any", action="store_true", help="Match any query term instead of all")
    read = sub.add_parser("read")
    read.add_argument("id")
    read.add_argument("--offset", type=int, default=0)
    read.add_argument("--max-chars", type=int, default=8000)
    sub.add_parser("index")
    sub.add_parser("status")
    sub.add_parser("verify")
    args = parser.parse_args(argv)
    root = (args.root or default_root()).expanduser().resolve()
    if args.command == "detect":
        result = detect(args.project)
    elif args.command == "ensure":
        result = ensure(root, args.project, {n: getattr(args, n + "_version") for n in ["react", "next", "go"]}, args.web)
    elif args.command == "sync":
        if args.ref and args.source in {"all", "go-stdlib"}:
            parser.error("--ref requires a single repository source")
        failures = []
        with lock(root):
            sources = list(SOURCES) if args.source == "all" else [args.source]
            if args.source == "all" and shutil.which("go"):
                sources.append("go-stdlib")
            for source in sources:
                try:
                    if source == "go-stdlib":
                        sync_stdlib(root, args.refresh)
                    else:
                        sync_repo(root, source, SOURCES[source], args.ref, args.refresh)
                except Exception as exc:
                    failures.append({"source": source, "error": str(exc)})
                    print(f"Failed {source}: {exc}", file=sys.stderr, flush=True)
            result = build_index(root)
        result.update(root=str(root), errors=failures)
    elif args.command == "index":
        with lock(root):
            result = build_index(root)
    elif args.command == "search":
        ids = args.snapshot
        if args.project:
            key = hashlib.sha256(str(args.project.resolve()).encode()).hexdigest()[:20]
            project_state = load_json(root / "projects" / (key + ".json"))
            if project_state is None:
                raise ValueError("Run ensure --project for this directory first")
            ids = project_state["snapshots"]
        result = {"root": str(root), "results": search(root, args.query, args.stack, args.version,
                  args.source, args.limit, args.any, ids)}
    elif args.command == "read":
        if args.offset < 0 or not 1 <= args.max_chars <= 24000:
            parser.error("offset must be nonnegative and max-chars must be 1..24000")
        result = read_chunk(root, args.id, args.offset, args.max_chars)
    elif args.command == "verify":
        result = verify(root)
    else:
        selected = active(root)
        result = {"root": str(root), "snapshots": []}
        for path in manifests(root):
            m = load_json(path)
            result["snapshots"].append({k: m[k] for k in ["id", "source", "stack", "version", "revision", "downloaded_at", "notes"]} |
                                       {"active": selected.get(m["source"]) == m["id"], "files": len(m["files"])})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if isinstance(result, dict) and (result.get("errors") or result.get("sqlite_integrity", "ok") != "ok") else 0


if __name__ == "__main__":
    # Windows pipes can otherwise inherit a legacy code page that cannot print docs.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, sqlite3.Error, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)

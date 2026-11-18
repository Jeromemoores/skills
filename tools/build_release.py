"""Build portable release archives without documentation caches or local settings."""
from pathlib import Path
import hashlib
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("VERSION must be major.minor.patch")
    for installer, pattern in [("install.ps1", r"\$taskVersion = '([^']+)'"), ("install.sh", r"^version=(.+)$")]:
        match = re.search(pattern, (ROOT / installer).read_text(encoding="utf-8"), re.MULTILINE)
        if not match or match[1] != version:
            raise ValueError(f"{installer} version differs from VERSION")
    for selected in ["web", "unreal"]:
        for extension in ["ps1", "sh"]:
            wrapper = ROOT / f"install-{selected}.{extension}"
            if f"/v{version}/install.{extension}" not in wrapper.read_text(encoding="utf-8"):
                raise ValueError(f"{wrapper.name} version differs from VERSION")
    output = ROOT / "dist" / f"v{version}"
    output.mkdir(parents=True, exist_ok=True)
    assets = []
    for selected in ["all", "web", "unreal"]:
        sets = ["shared"] + (["web", "unreal"] if selected == "all" else [selected])
        names = {line for group in sets for line in (ROOT / f"skill-sets/{group}.txt").read_text(encoding="utf-8").splitlines() if line}
        ps = (ROOT / "install.ps1").read_text(encoding="utf-8").replace("[string]$SkillSet = 'All'", f"[string]$SkillSet = '{selected.title()}'")
        shell = (ROOT / "install.sh").read_text(encoding="utf-8").replace("skill_set=all\n", f"skill_set={selected}\n", 1)
        readme = (ROOT / "README.md").read_text(encoding="utf-8") if selected == "all" else (
            f"# {selected.title()} development skills v{version}\n\n"
            f"Includes {len(names)} skills for {selected.title()}, including shared workflow, dependency, security and migration skills.\n\n"
            "On Windows, extract this ZIP and double-click `install.cmd` to install for both agents without PowerShell or network access. "
            "Alternatively run `.\\install.ps1` on Windows or `sh ./install.sh` on macOS/Linux. "
            "Use `-Target Claude` / `-Target Codex` or `--target claude` / `--target codex` to select one.\n\n"
            "Python 3.11+ and Git are needed when downloading/searching documentation. "
            "Unreal local header references require an authorized engine installation.\n\n"
            "Run `check-dependencies.cmd PROJECT_DIR` to inventory dependencies offline, or `ensure-dependency-docs.cmd PROJECT_DIR` to prepare missing docs. "
            "macOS/Linux: `sh ./check-dependencies.sh PROJECT_DIR` / `sh ./ensure-dependency-docs.sh PROJECT_DIR`. npm and Yarn Classic/modern/PnP are supported.\n\n"
            "Full guidance and other bundles: https://github.com/Jeromemoores/skills\n")
        contents = {"VERSION": f"{version}\n".encode(), "README.md": readme.encode(),
                    "VALIDATION.md": (ROOT / "VALIDATION.md").read_bytes(),
                    "install.ps1": ps.encode(), "install.sh": shell.encode(),
                    "install.cmd": (ROOT / "install.cmd").read_bytes()}
        for command in ["check-dependencies", "ensure-dependency-docs"]:
            for extension in ["cmd", "sh"]:
                name = f"{command}.{extension}"
                contents[name] = (ROOT / name).read_bytes()
        for group in sets:
            contents[f"skill-sets/{group}.txt"] = (ROOT / f"skill-sets/{group}.txt").read_bytes()
        for name in names:
            for path in (ROOT / "skills" / name).rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"} and path.name not in {"library-location.json", "unreal-location.json"}:
                    contents[path.relative_to(ROOT).as_posix()] = path.read_bytes()
        bundle = "skills" if selected == "all" else f"{selected}-skills"
        prefix = f"{bundle}-v{version}"
        archive = output / f"{prefix}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in sorted(contents.items()):
                info = zipfile.ZipInfo(f"{prefix}/{name}", date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
                z.writestr(info, data)
        assets.append(archive)
    (output / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in assets), encoding="utf-8")
    print(f"Built three ZIPs and checksums for v{version} in {output}")
    return output


if __name__ == "__main__":
    build()

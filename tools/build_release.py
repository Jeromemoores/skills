"""Build portable release archives without documentation caches or local settings."""
from pathlib import Path
import gzip
import hashlib
import io
import re
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build():
    version = (ROOT / "VERSION").read_text().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("VERSION must be major.minor.patch")
    for installer, pattern in [("install.ps1", r"\$taskVersion = '([^']+)'"), ("install.sh", r"^version=(.+)$")]:
        match = re.search(pattern, (ROOT / installer).read_text(), re.MULTILINE)
        if not match or match[1] != version:
            raise ValueError(f"{installer} version differs from VERSION")
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    assets = []
    for selected in ["all", "web", "unreal"]:
        sets = ["shared"] + (["web", "unreal"] if selected == "all" else [selected])
        names = {line for group in sets for line in (ROOT / f"skill-sets/{group}.txt").read_text().splitlines() if line}
        ps = (ROOT / "install.ps1").read_text().replace("[string]$SkillSet = 'All'", f"[string]$SkillSet = '{selected.title()}'")
        shell = (ROOT / "install.sh").read_text().replace("skill_set=all\n", f"skill_set={selected}\n", 1)
        readme = (ROOT / "README.md").read_text(encoding="utf-8") if selected == "all" else (
            f"# {selected.title()} development skills v{version}\n\n"
            f"Includes {len(names)} skills for {selected.title()}, including the four shared roles.\n\n"
            "Run `.\\install.ps1` on Windows or `sh ./install.sh` on macOS/Linux to install this set for both agents. "
            "Use `-Target Claude` / `-Target Codex` or `--target claude` / `--target codex` to select one.\n\n"
            "Python 3.11+ and Git are needed when downloading/searching documentation. "
            "Unreal local header references require an authorized engine installation.\n\n"
            "Full guidance and other bundles: https://github.com/Jeromemoores/skills\n")
        contents = {"VERSION": f"{version}\n".encode(), "README.md": readme.encode(),
                    "install.ps1": ps.encode(), "install.sh": shell.encode()}
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
                info.external_attr = (0o100755 if name == "install.sh" else 0o100644) << 16
                z.writestr(info, data)
        tarball = output / f"{prefix}.tar.gz"
        with tarball.open("wb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as tar:
                for name, data in sorted(contents.items()):
                    info = tarfile.TarInfo(f"{prefix}/{name}")
                    info.size = len(data)
                    info.mode = 0o755 if name == "install.sh" else 0o644
                    tar.addfile(info, io.BytesIO(data))
        suffix = "" if selected == "all" else f"-{selected}"
        ps_asset, sh_asset = output / f"install{suffix}.ps1", output / f"install{suffix}.sh"
        ps_asset.write_bytes(ps.encode())
        sh_asset.write_bytes(shell.encode())
        assets.extend([archive, tarball, ps_asset, sh_asset])
    (output / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in assets), encoding="utf-8")
    print(f"Built three bundles and six installers for v{version} in {output}")
    return output


if __name__ == "__main__":
    build()

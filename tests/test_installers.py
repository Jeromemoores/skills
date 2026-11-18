"""Exercise real local and download/bootstrap installers in disposable profiles."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile

from build_release import build

ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")
if os.name == "nt":
    # git may resolve to Git\cmd\git.exe or Git\mingw64\bin\git.exe; never fall back to WSL's bash.
    git = shutil.which("git")
    candidates = [parent / "bin/bash.exe" for parent in Path(git).parents] if git else []
    SHELL = next((str(c) for c in candidates if c.is_file()), None)
else:
    SHELL = shutil.which("sh")


class InstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = build()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="skills install ")
        self.folder = Path(self.temp.name)
        self.profile = self.folder / "profile with spaces"

    def tearDown(self):
        self.temp.cleanup()

    def expected(self, selected):
        sets = ["shared"] + (["web", "unreal"] if selected == "all" else [selected])
        return {line for name in sets for line in (ROOT / f"skill-sets/{name}.txt").read_text().splitlines() if line}

    def assert_install(self, selected="all", target="both"):
        expected = self.expected(selected)
        for agent, directory in [("claude", ".claude"), ("codex", ".agents")]:
            location = self.profile / directory / "skills"
            if target not in ["both", agent]:
                self.assertFalse(location.exists())
                continue
            self.assertEqual({p.name for p in location.iterdir()}, expected)
            for name in expected:
                for source in (ROOT / "skills" / name).rglob("*"):
                    if source.is_file() and "__pycache__" not in source.parts and source.suffix != ".pyc":
                        self.assertEqual(source.read_bytes(), (location / name / source.relative_to(ROOT / "skills" / name)).read_bytes())

    def run_ps(self, selected="all", target="both", bootstrap=False, corrupt=False, variant=None):
        env = os.environ.copy()
        if not bootstrap:
            args = [POWERSHELL, "-NoProfile", "-File", str(ROOT / "install.ps1"),
                    "-UserRoot", str(self.profile), "-SkillSet", selected, "-Target", target]
        else:
            loader = self.folder / "loader"
            loader.mkdir()
            suffix = f"-{variant}" if variant else ""
            shutil.copy2(ROOT / f"install{suffix}.ps1", loader / "install.ps1")
            assets = self.folder / "assets"
            shutil.copytree(self.assets, assets)
            if corrupt:
                archive = assets / f"skills-v{(ROOT / 'VERSION').read_text().strip()}.zip"
                archive.write_bytes(archive.read_bytes() + b"corrupted")
            temp = self.folder / "downloads"
            temp.mkdir()
            env.update(TEMP=str(temp), TMP=str(temp))
            harness = self.folder / "bootstrap-test.ps1"
            harness.write_text('''param($ReleaseAssets, $Loader, $ProfileRoot, $RepoRoot)
$ErrorActionPreference = 'Stop'
function Invoke-WebRequest {
    param($Uri, $OutFile, [switch]$UseBasicParsing)
    $name = ([uri]$Uri).Segments[-1]
    Copy-Item -LiteralPath (Join-Path $ReleaseAssets $name) -Destination $OutFile
}
function Invoke-RestMethod {
    param($Uri)
    Get-Content -Raw -LiteralPath (Join-Path $RepoRoot 'install.ps1')
}
& (Join-Path $Loader 'install.ps1') -UserRoot $ProfileRoot
''', encoding="utf-8")
            args = [POWERSHELL, "-NoProfile", "-File", str(harness), str(assets), str(loader), str(self.profile), str(ROOT)]
        return subprocess.run(args, env=env, capture_output=True, text=True, timeout=60)

    def run_sh(self, selected="all", target="both", bootstrap=False, corrupt=False, variant=None, bare=False):
        env = os.environ.copy()
        args = [SHELL]
        stdin = None
        cwd = None
        if bare:
            # `sh install.sh` from the extracted folder; an unreachable proxy makes any download fail.
            args += ["install.sh"]
            cwd = ROOT
            env.update(https_proxy="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
        elif not bootstrap:
            args += [(ROOT / "install.sh").as_posix()]
        else:
            assets = self.folder / "assets"
            shutil.copytree(self.assets, assets)
            if corrupt:
                archive = assets / f"skills-v{(ROOT / 'VERSION').read_text().strip()}.zip"
                archive.write_bytes(archive.read_bytes() + b"corrupted")
            fake_bin = self.folder / "bin"
            fake_bin.mkdir()
            fake_curl = fake_bin / "curl"
            fake_curl.write_text('''#!/bin/sh
set -eu
url=
out=
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o) out=$2; shift 2 ;;
        https:*) url=$1; shift ;;
        *) shift ;;
    esac
done
case "$url" in
    */install.sh) source="$SKILLS_TEST_REPO/install.sh" ;;
    *) source="$SKILLS_TEST_ASSETS/${url##*/}" ;;
esac
if [ -n "$out" ]; then cp "$source" "$out"; else cat "$source"; fi
''', encoding="utf-8", newline="\n")
            fake_curl.chmod(0o755)
            env["SKILLS_TEST_ASSETS"] = assets.as_posix()
            env["SKILLS_TEST_REPO"] = ROOT.as_posix()
            env["SKILLS_TEST_BIN"] = ("/" + fake_bin.as_posix()[0].lower() + fake_bin.as_posix()[2:]
                                     if os.name == "nt" else str(fake_bin))
            download = self.folder / "downloads"
            download.mkdir()
            env["TMPDIR"] = download.as_posix()
            args += ["-s", "--"]
            # Git Bash prepends its own binaries during startup; select the test
            # transport inside the shell so no network request can escape.
            suffix = f"-{variant}" if variant else ""
            stdin = 'PATH="$SKILLS_TEST_BIN:$PATH"\nexport PATH\n' + (ROOT / f"install{suffix}.sh").read_text()
        args += ["--user-root", self.profile.as_posix(), "--target", target]
        if not variant:
            args += ["--set", selected]
        return subprocess.run(args, env=env, cwd=cwd, input=stdin, capture_output=True, text=True, timeout=60)

    def assert_ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(POWERSHELL, "PowerShell is unavailable")
    def test_powershell_all_and_repeat_preserves_unrelated_skill(self):
        self.assert_ok(self.run_ps())
        self.assert_install()
        extra = self.profile / ".claude/skills/unrelated/SKILL.md"
        extra.parent.mkdir()
        extra.write_text("existing user skill")
        self.assert_ok(self.run_ps())
        self.assertEqual(extra.read_text(), "existing user skill")

    def assert_reinstall_replaces_skill_folders(self, run, agent=".claude"):
        self.assert_ok(run())
        skills = self.profile / agent / "skills"
        stale = skills / "implement-task/references/removed-in-new-release.md"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text("old release file")
        preference = skills / "official-stack-dev/scripts/library-location.json"
        preference.write_text('{"preferred_root": "D:/docs"}')
        unrelated = skills / "unrelated/SKILL.md"
        unrelated.parent.mkdir()
        unrelated.write_text("existing user skill")
        self.assert_ok(run())
        self.assertFalse(stale.exists())
        self.assertFalse(stale.parent.exists())
        self.assertEqual(preference.read_text(), '{"preferred_root": "D:/docs"}')
        self.assertEqual(unrelated.read_text(), "existing user skill")

    @unittest.skipUnless(POWERSHELL, "PowerShell is unavailable")
    def test_powershell_reinstall_replaces_skill_folders(self):
        self.assert_reinstall_replaces_skill_folders(self.run_ps)

    @unittest.skipUnless(SHELL, "POSIX shell is unavailable")
    def test_shell_reinstall_replaces_skill_folders(self):
        self.assert_reinstall_replaces_skill_folders(self.run_sh)

    @unittest.skipUnless(os.name == "nt", "Windows Command Prompt is unavailable")
    def test_extracted_zip_reinstall_replaces_skill_folders(self):
        version = (ROOT / "VERSION").read_text().strip()
        with zipfile.ZipFile(self.assets / f"web-skills-v{version}.zip") as z:
            z.extractall(self.folder / "extracted")
        folder = self.folder / "extracted" / f"web-skills-v{version}"
        self.assert_reinstall_replaces_skill_folders(lambda: subprocess.run(
            [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", ".\\install.cmd", str(self.profile)],
            cwd=folder, capture_output=True, text=True, timeout=60))

    @unittest.skipUnless(POWERSHELL, "PowerShell is unavailable")
    def test_powershell_web_claude_only(self):
        self.assert_ok(self.run_ps("web", "claude"))
        self.assert_install("web", "claude")

    @unittest.skipUnless(POWERSHELL, "PowerShell is unavailable")
    def test_powershell_unreal_codex_only(self):
        self.assert_ok(self.run_ps("unreal", "codex"))
        self.assert_install("unreal", "codex")

    @unittest.skipUnless(POWERSHELL, "PowerShell is unavailable")
    def test_powershell_download_bootstrap(self):
        self.assert_ok(self.run_ps(bootstrap=True))
        self.assert_install()

    @unittest.skipUnless(POWERSHELL, "PowerShell is unavailable")
    def test_powershell_web_release_defaults_to_web_only(self):
        self.assert_ok(self.run_ps(bootstrap=True, variant="web"))
        self.assert_install("web")

    @unittest.skipUnless(POWERSHELL, "PowerShell is unavailable")
    def test_powershell_unreal_release_defaults_to_unreal_only(self):
        self.assert_ok(self.run_ps(bootstrap=True, variant="unreal"))
        self.assert_install("unreal")

    @unittest.skipUnless(POWERSHELL, "PowerShell is unavailable")
    def test_powershell_corrupt_download_is_rejected_before_install(self):
        result = self.run_ps(bootstrap=True, corrupt=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum verification failed", result.stderr)
        self.assertFalse(self.profile.exists())

    @unittest.skipUnless(SHELL, "POSIX shell is unavailable")
    def test_shell_all_and_repeat_preserves_unrelated_skill(self):
        self.assert_ok(self.run_sh())
        self.assert_install()
        extra = self.profile / ".agents/skills/unrelated/SKILL.md"
        extra.parent.mkdir()
        extra.write_text("existing user skill")
        self.assert_ok(self.run_sh())
        self.assertEqual(extra.read_text(), "existing user skill")

    @unittest.skipUnless(SHELL, "POSIX shell is unavailable")
    def test_shell_web_claude_only(self):
        self.assert_ok(self.run_sh("web", "claude"))
        self.assert_install("web", "claude")

    @unittest.skipUnless(SHELL, "POSIX shell is unavailable")
    def test_shell_unreal_codex_only(self):
        self.assert_ok(self.run_sh("unreal", "codex"))
        self.assert_install("unreal", "codex")

    @unittest.skipUnless(SHELL, "POSIX shell is unavailable")
    def test_shell_bare_script_name_installs_local_files(self):
        result = self.run_sh(bare=True)
        self.assert_ok(result)
        self.assertNotIn("Downloaded release", result.stdout)
        self.assert_install()

    @unittest.skipUnless(SHELL, "POSIX shell is unavailable")
    def test_shell_download_bootstrap(self):
        self.assert_ok(self.run_sh(bootstrap=True))
        self.assert_install()

    @unittest.skipUnless(SHELL, "POSIX shell is unavailable")
    def test_shell_web_release_defaults_to_web_only(self):
        self.assert_ok(self.run_sh(bootstrap=True, variant="web"))
        self.assert_install("web")

    @unittest.skipUnless(SHELL, "POSIX shell is unavailable")
    def test_shell_unreal_release_defaults_to_unreal_only(self):
        self.assert_ok(self.run_sh(bootstrap=True, variant="unreal"))
        self.assert_install("unreal")

    def test_split_archives_contain_only_the_selected_skills(self):
        version = (ROOT / "VERSION").read_text().strip()
        for selected in ["all", "web", "unreal"]:
            prefix = f"{'skills' if selected == 'all' else selected + '-skills'}-v{version}"
            with zipfile.ZipFile(self.assets / f"{prefix}.zip") as z:
                zip_names = set(z.namelist())
                actual = {name.split('/')[2] for name in zip_names if '/skills/' in name}
                self.assertEqual(actual, self.expected(selected))
                self.assertFalse(any('location.json' in n or '__pycache__' in n for n in zip_names))
                for command in ['check-dependencies', 'ensure-dependency-docs']:
                    for extension in ['cmd', 'sh']:
                        self.assertIn(f'{prefix}/{command}.{extension}', zip_names)

    @unittest.skipUnless(os.name == 'nt', 'Windows Command Prompt is unavailable')
    def test_dependency_check_command_is_offline_and_preserves_project(self):
        project = self.folder / 'existing application'; project.mkdir()
        manifest = project / 'package.json'
        manifest.write_text('{"packageManager":"yarn@4.10.3","dependencies":{"bootstrap":"5.3.8"}}')
        env = os.environ.copy()
        env['DEPENDENCY_DOCS_HOME'] = str(self.folder / 'empty-cache')
        result = subprocess.run([os.environ.get('COMSPEC', 'cmd.exe'), '/d', '/c', '.\\check-dependencies.cmd', str(project)],
                                cwd=ROOT, env=env, capture_output=True, text=True, timeout=20)
        self.assert_ok(result)
        self.assertIn('bootstrap', result.stdout)
        self.assertIn('5.3.8', result.stdout)
        self.assertFalse((self.folder / 'empty-cache').exists())
        self.assertEqual([p.name for p in project.iterdir()], ['package.json'])

    def test_release_has_only_three_zips_and_checksums(self):
        version = (ROOT / "VERSION").read_text().strip()
        self.assertEqual({p.name for p in self.assets.iterdir()}, {
            f"skills-v{version}.zip", f"web-skills-v{version}.zip",
            f"unreal-skills-v{version}.zip", "SHA256SUMS"})

    @unittest.skipUnless(os.name == "nt", "Windows Command Prompt is unavailable")
    def test_extracted_web_zip_installs_without_powershell(self):
        version = (ROOT / "VERSION").read_text().strip()
        with zipfile.ZipFile(self.assets / f"web-skills-v{version}.zip") as z:
            z.extractall(self.folder / "extracted")
        installer = self.folder / "extracted" / f"web-skills-v{version}" / "install.cmd"
        result = subprocess.run([os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", ".\\install.cmd", str(self.profile)],
                                cwd=installer.parent, capture_output=True, text=True, timeout=60)
        self.assert_ok(result)
        self.assert_install("web")
        existing = self.profile / ".agents/skills/unrelated/SKILL.md"
        existing.parent.mkdir()
        existing.write_text("keep user skill")
        result = subprocess.run([os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", ".\\install.cmd", str(self.profile)],
                                cwd=installer.parent, capture_output=True, text=True, timeout=60)
        self.assert_ok(result)
        self.assertEqual(existing.read_text(), "keep user skill")

    @unittest.skipUnless(SHELL, "POSIX shell is unavailable")
    def test_shell_corrupt_download_is_rejected_before_install(self):
        result = self.run_sh(bootstrap=True, corrupt=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum verification failed", result.stderr)
        self.assertFalse(self.profile.exists())

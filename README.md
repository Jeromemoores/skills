# Documentation-first development skills

Web development and Unreal Engine skill sets for Claude Code and Codex. They support new projects and existing repositories, version-matched official documentation, architecture/capacity planning, focused implementation, code review, reuse, and validation.

## Install with one command

**Web only — Windows PowerShell (recommended for the work laptop):**

```powershell
irm https://github.com/Jeromemoores/skills/releases/latest/download/install-web.ps1 | iex
```

**Unreal only — Windows PowerShell:**

```powershell
irm https://github.com/Jeromemoores/skills/releases/latest/download/install-unreal.ps1 | iex
```

**Both sets — Windows PowerShell:**

```powershell
irm https://github.com/Jeromemoores/skills/releases/latest/download/install.ps1 | iex
```

**macOS/Linux — choose one terminal command:**

```sh
curl -fsSL https://github.com/Jeromemoores/skills/releases/latest/download/install-web.sh | sh
curl -fsSL https://github.com/Jeromemoores/skills/releases/latest/download/install-unreal.sh | sh
curl -fsSL https://github.com/Jeromemoores/skills/releases/latest/download/install.sh | sh
```

Web-only and Unreal-only each install seven skills, including the four shared roles. The combined option installs all 10. Each option installs for both agents into your user profile: `~/.claude/skills/` and `~/.agents/skills/`. Each downloads only its selected versioned bundle and verifies its SHA-256 checksum. Existing files belonging to these skill folders are updated; unrelated skills are preserved. Selecting Web-only leaves any previously installed Unreal skills alone. Run the same command to install a newer release. Start a new agent session if updated skills do not appear.

The commands execute this repository's installer. You can inspect/download it first or use a local release archive instead. Windows needs PowerShell 5.1+; macOS/Linux needs `sh`, `curl`, `tar`, and `sha256sum` or `shasum`.

Installing the skills does not require Python. **Downloading/searching documentation requires Python 3.11+ with SQLite FTS5 and Git.** Install those through your usual workstation setup if missing. Unreal header references use your own authorized engine installation. Installing skills does not install an engine, change models, or configure every ChatGPT chat/account.

## Choose a set or agent

The release has separate `web-skills`, `unreal-skills`, and combined `skills` ZIP/tarball downloads. Extracted packages default to their selected set. To choose an agent, or choose a set from a full clone/combined bundle, run:

```powershell
.\install.ps1 -SkillSet Web -Target Claude
.\install.ps1 -SkillSet Unreal -Target Codex
.\install.ps1 -SkillSet All -Target Both
```

```sh
sh ./install.sh --set web --target claude
sh ./install.sh --set unreal --target codex
sh ./install.sh --set all --target both
```

Each set includes the four shared roles. `-UserRoot PATH` / `--user-root PATH` selects another profile root, useful for testing an installation. On other hosts, copy the desired complete folders from `skills/` to the agent's supported skill directory.

## Included skills

| Set | Skill | Purpose |
| --- | --- | --- |
| Web | `official-stack-dev` | React, Next.js, Go, CSS, JavaScript and browser APIs using maintainer docs/MDN |
| Web | `plan-web-capacity` | Workload, architecture, bottlenecks and growth planning |
| Web | `validate-web-capacity` | Representative, bounded performance measurements |
| Unreal | `official-unreal-dev` | Epic/C++ docs and matching installed engine headers |
| Unreal | `plan-unreal-project` | Gameplay architecture, ownership and target budgets |
| Unreal | `validate-unreal-project` | Real build/runtime, automation, packaging and profiling evidence |
| Shared | `coordinate-project` | Plan, contracts, task ownership and integration for requested agent teams |
| Shared | `implement-task` | Focused implementation with documentation and acceptance evidence |
| Shared | `review-and-repair-code` | Correctness checks and useful refactor/optimization recommendations |
| Shared | `audit-code-reuse` | Find compatible existing behavior, duplication and potentially unused code |

For example: “Use official-stack-dev to extend this existing repo. Establish its versions, conventions and baseline before changing behavior.” Or: “Use official-unreal-dev and review-and-repair-code to review this gameplay system; suggest cohesive function boundaries and evidence-based optimizations without making edits.”

## How documentation works

The coding skills bundle Python standard-library helpers that detect project versions and download missing references on demand. Both agents share per-user caches. Search returns bounded excerpts; useful sections are read rather than loading a whole manual into context. Cached retrieval works offline. Source revisions, checksums, licenses and upstream links are retained in the local snapshots.

Web sources include React/Next.js/Go maintainer references and MDN CSS/JavaScript/browser APIs. Unreal sources include selected Epic pages, Microsoft C++ docs, C++ Core Guidelines, and selected headers from the local engine. Coverage and version limitations are explained in each coding skill's references. Upstream documents remain subject to their own licenses; downloaded corpora and engine headers are not distributed in this repo or its releases.

For custom cache locations use `OFFICIAL_DOCS_HOME` and `UNREAL_DOCS_HOME`. No machine-specific cache paths are included. Current documentation is not permission to upgrade a project's dependencies or engine.

## Review and validation approach

Agents connect consequential documentation contracts to implementation mechanisms and failure-case checks. Review includes ownership, asynchronous ordering and retry recovery, plus concrete recommendations for cohesion, reuse and efficiency. Optimizations distinguish measured evidence from hypotheses. Existing repos retain their architecture, compatible APIs/assets/data and pending work; baseline failures remain separate from regressions.

Skills guide behavior; they do not guarantee correct code or capacity. Actual multi-agent/model routing belongs to the runner. Unreal runtime checks require the appropriate engine/toolchain, and capacity claims require representative measurements.

## Development

```sh
python tests/run_tests.py
python tools/build_release.py
```

The offline suite covers documentation selection/retrieval, selection-specific bundles and installer behavior. Build output is written to `dist/`: separate ZIP/tarballs for Web, Unreal and combined, six one-command installers, and `SHA256SUMS`. The release build checks that installer versions match `VERSION`. Keep shared roles in one place under `skills/`; the set manifests select which ones to install.

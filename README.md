# Documentation-first development skills

Web development and Unreal Engine skill sets for Claude Code and Codex. They support new projects and existing repositories, version-matched official documentation, architecture/capacity planning, focused implementation, code review, reuse, and validation.

## Install with one command

**Windows offline option:** download the **Web-only ZIP** from [Releases](https://github.com/Jeromemoores/skills/releases/latest), extract it, and double-click **`install.cmd`**. It copies the 13 skills to both agents using standard Windows file-copy tools. No PowerShell or network access is needed for this installation step. First-time documentation downloads still need network access, Python and Git.

**Web only — Windows PowerShell (recommended for the work laptop):**

```powershell
irm https://raw.githubusercontent.com/Jeromemoores/skills/main/install-web.ps1 | iex
```

**Unreal only — Windows PowerShell:**

```powershell
irm https://raw.githubusercontent.com/Jeromemoores/skills/main/install-unreal.ps1 | iex
```

**Both sets — Windows PowerShell:**

```powershell
irm https://raw.githubusercontent.com/Jeromemoores/skills/main/install.ps1 | iex
```

**macOS/Linux — choose one terminal command:**

```sh
curl -fsSL https://raw.githubusercontent.com/Jeromemoores/skills/main/install-web.sh | sh
curl -fsSL https://raw.githubusercontent.com/Jeromemoores/skills/main/install-unreal.sh | sh
curl -fsSL https://raw.githubusercontent.com/Jeromemoores/skills/main/install.sh | sh
```

Web-only installs 13 skills; Unreal-only installs 10. Both include the four shared roles, dependency documentation, security review and safe-migration planning. The combined option installs all 16 unique skills. Each option installs for both agents into your user profile: `~/.claude/skills/` and `~/.agents/skills/`. Each downloads only its selected versioned bundle and verifies its SHA-256 checksum. Each installed skill folder is replaced, so files removed by a newer release do not linger; machine-local `library-location.json`/`unreal-location.json` preferences and unrelated skills are preserved. Selecting Web-only leaves any previously installed Unreal skills alone. Run the same command to install a newer release. Start a new agent session if updated skills do not appear.

The commands execute this repository's installer. You can inspect/download it first or use a local release archive instead. Windows needs PowerShell 5.1+; macOS/Linux needs `sh`, `curl`, `unzip`, and `sha256sum` or `shasum`.

Installing the skills does not require Python. **Downloading/searching documentation requires Python 3.11+ with SQLite FTS5 and Git.** Install those through your usual workstation setup if missing. Unreal header references use your own authorized engine installation. Installing skills does not install an engine, change models, or configure every ChatGPT chat/account.

## Choose a set or agent

The release has separate `web-skills`, `unreal-skills`, and combined `skills` ZIP downloads. Extracted packages default to their selected set. To choose an agent, or choose a set from a full clone/combined bundle, run:

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

Each set includes the four shared roles, `dependency-docs`, `review-security` and `plan-safe-migrations`. Web also includes `review-accessibility`. `-UserRoot PATH` / `--user-root PATH` selects another profile root, useful for testing an installation. On other hosts, copy the desired complete folders from `skills/` to the agent's supported skill directory.

## Included skills

| Set | Skill | Purpose |
| --- | --- | --- |
| Web | `official-stack-dev` | React, Next.js, Go, CSS, JavaScript and browser APIs using maintainer docs/MDN |
| Web | `plan-web-capacity` | Workload, architecture, bottlenecks and growth planning |
| Web | `validate-web-capacity` | Representative, bounded performance measurements |
| Web | `review-accessibility` | W3C-based keyboard, focus, form, visual and assistive-technology review |
| Web | `design-web-interface` | Task flows, content hierarchy, visual direction and responsive UI implementation |
| Web | `review-web-design` | Rendered UI/UX critique, state review and contextual de-slop checks |
| Unreal | `official-unreal-dev` | Epic/C++ docs and matching installed engine headers |
| Unreal | `plan-unreal-project` | Gameplay architecture, ownership and target budgets |
| Unreal | `validate-unreal-project` | Real build/runtime, automation, packaging and profiling evidence |
| Shared | `coordinate-project` | Plan, contracts, task ownership and integration for requested agent teams |
| Shared | `implement-task` | Focused implementation with documentation and acceptance evidence |
| Shared | `review-and-repair-code` | Correctness checks and useful refactor/optimization recommendations |
| Shared | `dependency-docs` | Dependency discovery, version-aware docs caching and coverage checks; npm/Yarn, Go, Python and selected C++/Unreal inputs |
| Shared | `audit-code-reuse` | Find compatible existing behavior, duplication and potentially unused code |
| Shared | `review-security` | Focused trust-boundary/security review with separate Web and Unreal guidance |
| Shared | `plan-safe-migrations` | Database/API and Unreal save/reflected-asset compatibility, rehearsal and recovery planning |

The review skills mention `propose-code-review` for Accept/Reject previews of proposed changes. It is a separate optional skill that is not part of these bundles; without it, reviews report findings or edit directly within the authorized scope.

For example: “Use official-stack-dev to extend this existing repo. Establish its versions, conventions and baseline before changing behavior.” Or: “Use official-unreal-dev and review-and-repair-code to review this gameplay system; suggest cohesive function boundaries and evidence-based optimizations without making edits.”

## How documentation works

The coding skills bundle Python standard-library helpers that detect project versions and download missing references on demand. Both agents share per-user caches. Search returns bounded excerpts; useful sections are read rather than loading a whole manual into context. Cached retrieval works offline. Source revisions, checksums, licenses and upstream links are retained in the local snapshots.

Web sources include React/Next.js/Go maintainer references and MDN CSS/JavaScript/browser APIs. Unreal sources include selected Epic pages, Microsoft C++ docs, C++ Core Guidelines, and selected headers from the local engine. Coverage and version limitations are explained in each coding skill's references. Upstream documents remain subject to their own licenses; downloaded corpora and engine headers are not distributed in this repo or its releases.

For custom cache locations use `OFFICIAL_DOCS_HOME` and `UNREAL_DOCS_HOME`. No machine-specific cache paths are included. Current documentation is not permission to upgrade a project's dependencies or engine.

## Dependency documentation and Yarn

The new `dependency-docs` skill inventories existing repositories, prepares missing maintainer references, and notices dependency changes. Both skill sets include it. Agents are instructed to run it before consequential third-party API work and again after manifest/lockfile changes. It never installs packages or executes their install scripts.

From a clone or extracted release ZIP:

```bat
check-dependencies.cmd "E:\path\to\project"
ensure-dependency-docs.cmd "E:\path\to\project"
```

macOS/Linux: `sh ./check-dependencies.sh /path/to/project` and `sh ./ensure-dependency-docs.sh /path/to/project`. With no path, the current working directory is scanned. The check is offline/read-only; ensure downloads missing references. After installation, agents use the helper inside the installed `dependency-docs/scripts/` folder. These commands do not modify your shell profile or global PATH.

**npm and Yarn Classic/modern are supported**, including Yarn Plug'n'Play without `node_modules`, grouped/scoped selectors, aliases and workspaces. The active package manager and resolved versions come from project evidence; conflicting/stale locks are reported. Yarn/PnP code is never executed. pnpm currently needs installed package metadata or an independently established version.

Cache reuse is by ecosystem, actual package identity and major version. Exact matches are preferred; same-major references skip downloads and display the cached version. Use `--exact` for stricter coverage. A same-major guide does not prove minor/patch API availability. SQLite engine references are separate from its Node/Go drivers. Bootstrap has a curated fuller documentation source; general npm/PyPI fallbacks use the publisher's release README/description and are clearly marked limited coverage. Go module docs and selected C++/Unreal declarations are supported; unresolved versions/private sources remain visible gaps. This is not a complete resolver for every ecosystem or a vulnerability audit.

For human dependency edits, agents rescan on subsequent work. An optional foreground watcher runs only when started explicitly:

```text
python "PATH_TO_INSTALLED_SKILL/scripts/dependency_docs.py" watch --project "PROJECT_DIR" --format table
```

Stop with Ctrl+C. No background service or automatic package-manager hook is installed. A skill cannot monitor changes while no agent/watcher is running. Search/read only the relevant indexed sections rather than loading all docs into context. See [the skill](skills/dependency-docs/SKILL.md) for exact mode, transitive inventory, source registration, coverage and private/local dependency handling. `DEPENDENCY_DOCS_HOME` overrides its cache; otherwise it shares the web documentation library.

## Specialized reviews and migrations

Use `review-security` for requested security assessments and consequential trust-boundary changes. It traces reachable effects and legitimate/invalid caller cases, using OWASP ASVS for Web and matching Epic ownership/networking evidence for Unreal. It distinguishes intentional synthetic identities from production authentication and preserves review-only scope.

Use `review-accessibility` for affected Web accessibility journeys. It connects W3C criteria to actual keyboard/focus, form/reset/status, visual and assistive-technology evidence, with explicit limits on automated scans and conformance claims. This skill is in the Web bundle only.

Use `plan-safe-migrations` before consequential schema, persisted API/data, game-save or reflected-asset transitions. It establishes compatibility windows, preserves atomicity/data meaning, rehearses older-format fixtures and interruption/recovery on copies, and separates planning from live execution. Core Redirects are not treated as a universal save converter.

The existing reviewer and Web/Unreal validation skills now include regression-test design: independent oracles, representative fixtures, deterministic ordering, correct runtime boundaries and a source/build snapshot. Skills route relevant work without imposing unrelated audits on ordinary edits. See [validation evidence](VALIDATION.md) for packaging checks and the independent source-only scenario evaluation.

## Review and validation approach

v1.3.1 is a documentation patch: the planner, implementer, stack, Unreal and code-review entrypoints open with a short workflow and a single companion-skill list, and nine references add version-sensitive "commonly missed cases" lists to verify against the project's actual versions. Review tightened overbroad claims about serialization, lifecycle and platform behavior. Release checksums are now written with LF line endings, and the shell bootstrap tolerates legacy CRLF checksum files.

v1.3.0 adds two Web-only design skills. Use `design-web-interface` for a new or reshaped page/flow; it establishes the user task and content, preserves relevant existing brand/components, chooses a coherent visual direction and inspects the rendered result. Use `review-web-design` for visual/UX critique or a de-slop pass, separating reproducible barriers, unsupported claims and optional taste changes. Familiar fonts, palettes, cards and dense tables are evaluated in context rather than banned.

The skills include focused references for tasks/recovery states, visual composition and rendered critique. They reuse the existing stack, accessibility and code-review specialists. A browser walkthrough is not a user study, and an attractive screenshot does not establish working interactions. See [validation evidence](VALIDATION.md) for the actual evaluation and its limits.

Phone/tablet/desktop guidance covers content-driven breakpoints, portrait/landscape layouts, touch and keyboard/mouse use, hover-free actions, constrained-height forms, meaningful table scrolling, zoom, safe areas and overlay behavior. Checks report the actual browser/input conditions; emulation is kept distinct from physical devices and on-screen keyboards. Planner, implementer, stack-development and code-review skills explicitly reference the design skills for relevant work when installed.

Agents connect consequential documentation contracts to implementation mechanisms and failure-case checks. Review includes ownership, asynchronous ordering and retry recovery, plus concrete recommendations for cohesion, reuse and efficiency. Optimizations distinguish measured evidence from hypotheses. Existing repos retain their architecture, compatible APIs/assets/data and pending work; baseline failures remain separate from regressions.

v1.2.1 strengthens cross-boundary compatibility checks: accepted legacy values and emitted artifacts must remain usable by downstream validators and operations. Builders and reviewers test the actual round trip, account for representation/length/precision differences, preserve required historical data, and distinguish supported compatibility failures from constructed unsupported imports.

Skills guide behavior; they do not guarantee correct code or capacity. Actual multi-agent/model routing belongs to the runner. Unreal runtime checks require the appropriate engine/toolchain, and capacity claims require representative measurements.

## Development

```sh
python tests/run_tests.py
python tools/build_release.py
```

The offline suite covers documentation selection/retrieval, selection-specific bundles and installer behavior. Build output is written to `dist/vVERSION/`: three ZIPs (Web, Unreal and combined) plus `SHA256SUMS`. The one-command installers live in the repository, keeping release downloads uncluttered. GitHub also adds its two automatic source archives. The release build checks that installer versions match `VERSION`. Keep shared roles in one place under `skills/`; the set manifests select which ones to install.

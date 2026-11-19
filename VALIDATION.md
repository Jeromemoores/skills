# v1.3.1 validation

## v1.3.1 scope and current evidence

This patch changes skill documentation and two release-tooling details. No documentation helper or skill set membership changed.

Release tooling: `SHA256SUMS` is now written with LF line endings. Windows-built v1.3.0 used CRLF; implementations that retain the carriage return in the filename field can fail exact matching. `install.sh` strips carriage returns before matching, and the writer's output is checked for LF. Git Bash's `awk` tolerates the carriage return, so this review does not claim reproduction of the old failure on a native macOS/Linux host. `.gitattributes` pins `*.json`, `*.yaml` and `VERSION` checkout line endings to LF.

Five entrypoints (`implement-task`, `coordinate-project`, `official-stack-dev`, `official-unreal-dev`, `review-and-repair-code`) were restructured: each opens with a short workflow and one companion-skill list replacing scattered routing sentences, and `implement-task` gained section headings. The guidance itself was kept; routing sentences were consolidated, not removed. These five files are about 10% longer than in v1.3.0.

Nine references gained a "Commonly missed cases" list (Go, React, Next.js, CSS/JavaScript, Web security, Unreal security, Web migrations, Unreal persistence, Unreal C++ quality), each framed as candidates to verify against the project's version. `dependency-docs` documents its options, `verify` and cache pruning; the web local-docs reference documents `detect`; `review-and-repair-code` and the README mention the separate optional `propose-code-review` skill.

Claude's prepublication draft recorded **96 tests passed in 107.893 seconds** on Windows, local-link/frontmatter checks and command/flag parsing checks. The final publication checks below supersede that test count.

The initial added lists were written from general engineering knowledge, not verified across every framework or engine version. Publication review corrected specific overgeneralizations using primary references; the remaining lists are scoped prompts for version-matched investigation, not a certified catalog of universal rules.

## Final publication review and checks

Retained the workflow restructuring and expanded helper documentation. Corrected guidance on sticky positioning inside scroll containers, JSON Date/Map/Set conversion, React effect/ref/draft exceptions, Next.js environment-variable exposure, Go timeout/error semantics, conditional migration strategies, and Unreal save/delegate/Live Coding behavior. In particular, Epic's [SaveGameToSlot contract](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UGameplayStatics/SaveGameToSlot?application_version=5.8) does not filter properties by the SaveGame flag; custom archives can differ. [React ref initialization](https://react.dev/reference/react/useRef), [CSS positioning](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position), [JSON behavior](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify), [Next environment variables](https://nextjs.org/docs/app/guides/environment-variables), [Epic delegate bindings](https://dev.epicgames.com/documentation/en-us/unreal-engine/delegates-and-lambda-functions-in-unreal-engine) and [Live Coding](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-live-coding-to-recompile-unreal-engine-applications-at-runtime) support the revised distinctions. These spot checks do not validate every item on every historical version.

On a stable final skill tree, `python tests/run_tests.py`: **97 tests passed in 109.788 seconds**. The added end-to-end shell-bootstrap test actually installs from a CRLF checksum fixture. All **16 skill entrypoints** passed the skill-creator validator, and source/archive local-reference checks passed. The new verify/detect documentation was checked against the bundled command parsers. One earlier run overlapped a final reference edit and had two archive/source snapshot mismatches; it was retained locally, then rerun without source edits rather than changing assertions.

Fresh Node 24.15.0/Chromium 159.0.8154.6 probes verified Date/undefined/Map/Set JSON behavior, structured-clone type preservation, invalid-URL fetch rejection, and sticky positioning inside an `overflow:auto` scroller. No Unreal build/runtime, native macOS/Linux host, physical-device run or fresh model benchmark was performed in this review. Installer checks used Windows PowerShell, Command Prompt and Git Bash. Local review evidence is under `E:/coding/skills/.cache/review-1.3.1` and is not shipped.

Installed the final 16 skills for both local Claude and Codex profiles; 138 installed files matched source, machine-local preferences were preserved, and all three bundles' skill Markdown matched the final tree. Skill membership remains Web 13, Unreal 10 and combined 16. No application/game repository was edited for this patch.

## v1.3.1 independent forward-test

Four fresh reviewer contexts each performed a review-only, source-only review of a small fixture with planted defects: a Go/Next.js/PostgreSQL web fixture (18 defects, 3 correct "control" patterns) and an Unreal C++ fixture (12 defects, 2 controls). Each fixture was reviewed once with the v1.3.0 skills and once with the v1.3.1 skills, under anonymous variant labels. Reviewers started from `review-and-repair-code` and chose their own companions and references. They were barred from the network, the documentation helpers, installed skills and the other variant. The answer key was written before any reviewer ran.

Result: all four reviewers found every planted defect (18/18 and 12/12 for both versions) and none reported a control as a defect. With the restructured entrypoints, reviewers reached the same references as before, honored review-only scope, separated findings from optional improvements and labeled unverified engine/framework behaviour as unverified.

No regression was observed in those sampled source-only fixtures. This does **not** show an improvement: both versions scored 100%, so the fixtures could not distinguish them. There was one reviewer per arm, the reviewers used the same model family that wrote the fixtures and the new lists, and nothing was compiled or run. That evaluation used Claude's prepublication draft, not all final wording corrections described above. The v1.3.0 design forward-test below was not repeated.

Fixtures, answer key, scoring and raw transcripts are outside the release tree at `E:/coding/skill-forward-test-v1.3.1` and are not shipped.

## Historical v1.3.0 evidence

## v1.3.0 scope and package checks

Adds `design-web-interface` and `review-web-design` to the Web bundle, with original instructions and focused references for task flows/states, visual direction, phone/tablet/desktop input/layout, and rendered critique/de-slop. Planner, implementer, official-stack development and code-review skills route relevant work to them when installed. No third-party skill runtime, hook, design catalog or new package dependency is imported. The Unreal-only set retains 10 skills; Web has 13; combined has 16 unique skills.

`python tests/run_tests.py`: **96 tests passed in 104.428 seconds** on Windows. Two added checks verify that design skills ship with Web/combined only, every source skill is distributed, and local Markdown references resolve inside each archive. All 16 skill entrypoints passed the skill-creator validator; local references were also checked against source. Existing helper/installer checks cover the local/bootstrap/offline paths, checksum verification, preferences and unrelated-skill preservation. These checks do not test subjective design quality.

Installed all 16 skills for both local Claude and Codex profiles and verified 138 installed files against source. Machine-local documentation preferences were preserved. The four planner/implementer/stack/code-review entrypoints include the relevant design-skill references in both installations. Final archives were checked against shipped skill source; documentation caches, machine settings and benchmark artifacts remain excluded.

## Independent design forward-test

Four fresh builder contexts received equivalent supplied inputs for two isolated local briefs: a fictional bicycle-repair site and an existing-brand dispatch dashboard. Each brief was built using the existing skills and again with the new design skill added. All used the same inherited model configuration (exact model ID not exposed), native HTML/CSS/JavaScript, supplied facts/data, local/system fonts, no external assets/packages, and one bounded self-review/revision allowance. Tool use and actual effort varied; this was not a timed performance or cost experiment.

A separate reviewer context used the new review skill with anonymized A/B source/screenshots and the briefs. It was not given variant labels, the parent's conclusions, expected defects or builder handoffs. The reviewer inspected renders and independently operated the important tasks. It preferred the guided marketing page for service/form grouping, readable content and narrow navigation, and the guided dashboard more modestly for comparison density, delayed-job hierarchy and recovery focus. These are evidence-based heuristic judgments from one pair per brief, not real-user preference, conversion evidence, a statistical improvement estimate or proof across models.

The review found corrupted punctuation/hour ranges in the marketing baseline, and keyboard Retry focus loss plus a missing tablet scroll cue in the dashboard baseline. First-evaluation snapshots/reports were retained. A narrow correction round in the disposable prototypes followed; original application repositories were not edited. The encoding finding informed an explicit instruction to verify decoded source and visible text rather than mistaking terminal decoding for source corruption. Mobile/tablet/desktop coverage was expanded at the user's request; the full paired build experiment was not repeated after these small guidance refinements.

## Browser evidence and limits

The parent rerendered all four anonymized prototypes with a common Playwright/Chromium harness. Four default runs checked 1280/768/390/320px layouts and meaningful tasks: invalid/corrected local form submission, complete 16-record fidelity, combined search/status filters, no-results recovery, retained-data failure and Retry. Sixteen additional runs exercised phone-touch 390×844, tablet portrait 768×1024, tablet landscape 1024×768, and wide desktop 1440×900. All 20 common runs passed their scoped functional checks with no whole-page overflow, page errors or attempted external requests. These automated checks did not detect every visual or focus issue; the independent review's findings remain distinct evidence.

The reviewer additionally tested keyboard focus after recovery, contained table scrolling, content retention, tablet touch taps, orientation/resizing and constrained-height views. Both dashboard variants retained the specified purple primary identity, Inter/system fallback declaration, semantic table and supplied records. A narrow screenshot or a coarse-pointer emulation does not reproduce a physical phone/tablet, Safari/Android, native picker, soft keyboard, safe area, assistive technology or full zoom matrix. None of those untested conditions is claimed as validated. No performance/user-count or whole-site accessibility certification follows.

The local research/evaluation artifacts are outside the release tree at `E:/coding/design-skill-research/benchmark-2026-11-19`, including input fingerprints, first-evaluation source/skill hashes, anonymized snapshots, independent reports, source mapping and browser results. They contain fictional prototype data, are not shipped in the ZIPs and are not prerequisites for using the skills. This section records the actual method/results without embedding project-specific repair instructions in a skill.

## Historical v1.2.1 evidence

## v1.2.1 scope and current evidence

This patch updates the shared implementation, review, migration and planner-handoff guidance, so it ships in both Web and Unreal bundles. It requires accepted migrated values and emitted artifacts to remain usable through downstream validation and the next operation, with explicit supported-domain/limit policies. No application source or existing database was edited by this skills update.

The motivating independent application review reproduced a migration that accepted a constructed long-fraction timestamp and emitted a pagination cursor rejected by the next request. Normal application writers did not generate that representation; the finding was classified as a low-priority compatibility edge. The guidance generalizes the producer/consumer mismatch rather than prescribing a timestamp length or requiring every project to support arbitrary imported data.

`python tests/run_tests.py`: **94 tests passed in 94.815 seconds**, including helper, bundle and installer regressions. All **14 skill entrypoints** passed the skill-creator validator, and local Markdown reference targets were checked. The validator ran in UTF-8 mode with PyYAML isolated in an ignored validation-only directory. No runtime helper logic or dependencies changed in this patch.

Installed all 14 skills into both local agent directories. Verified 122 installed files against source, preserved machine-local documentation preferences, and checked bundled skill Markdown against final source in the Web, Unreal and combined archives.

The guidance was inspected for the demonstrated Web cursor/migration mismatch and the equivalent Unreal persisted-reference consumer boundary. Checks remain conditional on affected contracts and supported data; ordinary stateless edits do not acquire an unrelated migration/runtime requirement. This is same-context instruction review plus structural/packaging evidence, not a new independent agent behavior evaluation or proof that future agents cannot miss an edge case. Historical v1.2.0 evidence below remains separately labeled.

## Historical v1.2.0 evidence

Validated on Windows with Python 3.14, Windows PowerShell 5.1, Command Prompt and Git Bash. Documentation helpers require Python 3.11+; macOS/Linux distributions were not independently exercised.

## Packaging and installer evidence

`python tests/run_tests.py`: **94 tests passed** in 94 seconds. Coverage includes existing Web/Unreal documentation selection, dependency discovery and npm/Yarn/PnP behavior, cache/update/prune behavior, failed retrieval, all/split archives, local/bootstrap/offline installers, checksum rejection, retained cache preferences, obsolete-file cleanup and unrelated-skill preservation.

All **14 skill entrypoints** passed the skill-creator validator. Local Markdown reference links were checked for broken targets. The validator's PyYAML prerequisite stays in an ignored validation-only directory; shipped documentation helpers remain standard-library-only.

Bundles contain 11 Web skills, 10 Unreal skills, or all 14 unique skills. Security and migration guidance is shared; accessibility appears only in Web. Validation guidance ships inside the archives. Downloaded corpora, engine headers, machine preferences, temporary evaluation fixtures and private project code are excluded.

## Independent skill forward-test

A separate agent context read the three new skills and only relevant references, then reviewed small source-only fixtures under a realistic review-only brief. It received requirements and raw artifacts, without the parent agent's expected findings or conclusions. No fixture or application source was modified.

The evaluation identified source-supported ownership and server-price failures, keyboard/reset validation problems, and a destructive data conversion that broke an explicit old/new-version overlap requirement. It distinguished an intentional synthetic identity selector from an authorization defect, kept Web ASVS separate from Unreal ownership semantics, preserved review-only scope, and reported missing browser/database/engine/runtime evidence. It did not claim a live exploit, accessibility conformance, migration rehearsal, restore or game build.

A minor migration instruction ambiguity was corrected after this pass: implementation/rehearsal assignments should exercise disposable copies, while review-only or unidentified-format work reports a concrete transition and evidence gaps instead of inventing an execution target. This one scenario pass is evidence about the sampled skill behavior, not a general guarantee of agent reliability.

## Documentation basis and coverage

Security guidance links OWASP ASVS and matching Epic RPC references; accessibility links W3C WCAG, WAI forms/keyboard and evaluation guidance. Migration guidance links the actual database DDL documentation and Epic save/load/Core Redirects references. Agents must still match project versions and read relevant sections before consequential API claims; a link in a skill is not proof that a project decision was verified.

The earlier v1.1.0 live helper checks remain historical evidence: Bootstrap/SQLite retrieval, zero-fetch same-major reuse with npm and modern Yarn fixtures, parsing 2,662 real Yarn selectors, and verifying 4,679 cached files with SQLite integrity `ok`. They were not repeated as live network benchmarks for this prose/packaging update. The offline regression suite was rerun.

## Limits

The new specialists provide scoped guidance and evidence boundaries. They do not certify an application, replace manual accessibility/assistive-technology checks, authorize production migrations, or establish Unreal runtime compatibility without the appropriate real environment. Test-design references distinguish stubs, builds, source snapshots and runtime assertions; existing capacity evidence still requires representative measurements. No production application or game was audited or migrated by this update.

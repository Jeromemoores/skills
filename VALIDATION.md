# v1.2.0 validation

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

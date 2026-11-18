# v1.1.0 validation

Validated on Windows with Python 3.14, Windows PowerShell 5.1, Command Prompt and Git Bash. Python 3.11+ is the supported helper prerequisite; macOS/Linux distributions were not independently exercised.

## Automated evidence

`python tests/run_tests.py`: 94 tests passed. Coverage includes existing web/Unreal helper behavior, update/prune, matching selections, failed downloads, all/split bundles, local/bootstrap/offline installers, checksum rejection, retained machine preferences, removal of obsolete skill files and preservation of unrelated skills.

Dependency tests cover npm, Yarn Classic and modern/PnP without installing packages; scoped/grouped selectors, aliases, workspaces, patched/private dependencies, active-manager selection, stale/ambiguous locks, React/Next detection, exact/major cache reuse, changed inventory, project-scoped search and pruning pins. Retrieval checks include publisher identity, artifact checksums, bounded archives, source hosts, and explicitly limited coverage. After the final fixture/output refinements, all 36 dependency tests passed again.

All 11 skill entrypoints passed the skill-creator validator. The validator's PyYAML prerequisite was installed into an ignored validation-only directory, not a project or global environment. Packaged helpers themselves use the Python standard library.

## Live source checks

- Retrieved Bootstrap 5.3.9 maintainer docs from `twbs/bootstrap`: 120 documents. The source adapter handles its newer Astro layout and older documentation layouts.
- Retrieved the `TryGhost/node-sqlite3` 6.0.1 maintainer README and seven selected SQLite engine pages. Driver and engine coverage have separate cache identities.
- Changed a disposable fixture to Bootstrap 5.3.8 and sqlite3 6.0.0; missing-source retrieval was patched to fail if called. Both reused same-major snapshots with zero fetches; related SQLite family docs reused their cache too. Bootstrap modal search returned five scoped results.
- Repeated that offline reuse using a modern Yarn/PnP fixture with no node_modules. No errors or fetches occurred.
- Parsed 2,662 selectors from the Yarn maintainers' actual generated Berry lockfile at `https://raw.githubusercontent.com/yarnpkg/berry/master/yarn.lock`.
- Verified the live shared library: 4,679 stored files passed checksum validation and SQLite integrity was `ok`.

Fixtures and downloaded corpora are outside published source/release payloads. Sources keep their upstream URLs, revisions and license notices. These observations validate helper behavior, not application correctness or Unreal runtime compatibility.

## Included maintenance changes

This release retains the preceding local maintenance work: optional source configuration for the shared Unreal runtime, React-major selection evidence, recorded inputs/topics, refresh/update/prune commands, pruning only after successful updates, and installer replacement of outdated skill files while retaining local cache preferences. Dependency selections also pin their snapshots during pruning.

## Boundaries

Same-major reuse does not prove minor/patch API compatibility; exact mode is available. General npm/PyPI fallbacks contain publisher README/description material rather than full manuals. Go coverage may need additional subpackage pages. Python ranges/markers and complex Poetry declarations, C++ baselines, and many Unreal plugin versions need explicit inspection. pnpm needs installed metadata or independently established versions. A docs check does not install packages, perform a vulnerability audit, or continuously watch while no agent/watcher is running.

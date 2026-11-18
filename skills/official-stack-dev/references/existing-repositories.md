# Working in an existing repository

Use this workflow for feature work, fixes, refactors, and reviews in an established project. Inspect the affected path and its consumers; do not inventory the entire repository for a small change.

## Discover the actual application

Read applicable repository/subdirectory instructions, the relevant README/design decisions, and package/workspace/build/deployment configuration. Inspect the current version-control status and relevant diff without discarding or automatically stashing work. If no VCS baseline is available, identify a file snapshot. Do not treat pre-existing changes as your own or silently overwrite another contributor's work.

Find the executable application/package within the repository, which may differ from the repository root. Resolve the package manager, lockfile/workspace ownership, installed versions, router/runtime, and Go modules/workspace/replacements. Run the documentation helper at the affected package, separately for distinct applications when necessary. Match existing versions and supported targets; availability of newer docs is not a reason to upgrade dependencies or regenerate lockfiles.

Trace the requested user action from its entry point through components/handlers, shared domain operations, persistence, background work, and relevant consumers. Search by domain behavior/types as well as function names before adding a helper. Locate existing tests/fixtures and compatible implementations, including shared packages. Use project architecture, conventions, and ADRs as integration context while verifying consequential API assumptions against matching documentation. A familiar existing pattern may still contain a bug.

## Establish a useful baseline

Inspect scripts and environment expectations before running them. Use established targeted commands and disposable local fixtures; an existing command named `test` or `dev` is not evidence that it avoids production services, migrations, notifications, or data resets. Reuse known setup and avoid exposing secrets. Installing skills does not authorize operating an existing deployment.

Run the relevant current check/reproduction when feasible before editing meaningful behavior. Record the revision/snapshot, configuration, command and outcome. Distinguish pre-existing failures, missing environment/dependencies, and new regressions. Do not repair unrelated baseline failures or weaken assertions to obtain a clean result. If execution is unavailable, state the gap and continue supported analysis; do not require a whole-repo green build before every narrow change.

When important existing behavior lacks tests, add a focused characterization/regression check if useful. Separate behavior that must remain compatible from the requested defect/behavior change; do not preserve a bug merely because it is current behavior.

## Integrate incrementally

Identify the smallest coherent change and affected consumers before editing. Reuse compatible logic, dependency direction, styling/design-system patterns, error conventions, auth boundaries, and test tooling. Keep public API/data formats, database migration history, persisted client state, and background-job compatibility in view when affected. An authorized breaking change may need a migration/transition plan; an ordinary feature is not permission to reset data or replace the stack.

Validate changed behavior plus relevant existing journeys and failure cases against the same baseline. For async/recovery changes, also use [Asynchronous operation contracts](async-operations.md). Review the final diff for incidental generated files, lockfile churn, unrelated formatting, and lost pre-existing work. Report the integration points, behavior/compatibility changes, actual before/after checks, and material gaps. Do not claim that scoped tests certify the entire repository.

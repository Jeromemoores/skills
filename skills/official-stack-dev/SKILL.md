---
name: official-stack-dev
description: "Build, extend, debug, review, or explain new and existing React, Next.js, Go, CSS, and JavaScript projects using cached maintainer documentation, MDN, and applicable standards. Use for websites, components, browser behavior, routing, APIs, and Go services; exclude unrelated stacks and prose-only edits."
---

# Official Stack Development

Ground framework and language decisions in the maintainers' documentation, then verify the implementation in the actual project. This skill guides research and implementation; it does not change the model's training or guarantee correctness.

For a requested team or mixed-model workflow, use `coordinate-project` when available to manage the plan, shared contracts, builder tasks, and review. `implement-task` and `review-and-repair-code` provide optional role guidance. These companions do not replace documentation research, change permissions, or select models by themselves; ordinary solo tasks can use this skill directly.

## Documentation is the default authority

Treat a recalled pattern as a candidate to verify. Before implementing consequential API, rendering, styling, asynchronous, or lifecycle behavior, read the relevant version/runtime-appropriate reference and identify the constraints that affect this change. Searching or attaching a citation after writing code does not satisfy this step. Reuse references already read during the task; mechanical edits do not need repetitive research.

Prefer the framework/package maintainers' documentation for their APIs, MDN for practical CSS/JavaScript/browser guidance, and the applicable standards for normative language/platform semantics. A popular repository, familiar snippet, or repeated training example does not establish correctness. Existing project code establishes conventions and intended integration; verify questionable API assumptions before repeating them.

Distinguish documented requirements, documented recommendations, and your own design choices. A page supporting an API does not automatically support the application's architecture. Use simple, documented primitives appropriate to the requirement; justify added dependencies, abstractions, optimizations, and workarounds with a concrete need.

Read example assumptions, errors, cleanup, and support notes before adapting an example. Tutorial code may intentionally omit production concerns. Verify proposed/experimental features and browser/runtime support before adoption. If a documented contract and observed behavior disagree, investigate versions, configuration, release notes, and relevant maintainer source/tests; report the discrepancy instead of asserting either source is infallible.

For each consequential correctness claim, connect the documented requirement to the implementing mechanism and an observable failure-case check. For example, a mutable external store needs a working change-notification path, not merely a Hook with the right name. A citation and passing build do not establish that the contract is implemented. Keep this connection in the existing task/review handoff; create no separate research artifact unless useful.

When evidence is missing, choose an established documented alternative where possible. Label material unresolved assumptions and preserve the user's requirements. Do not invent an API, option, supported-version claim, or a citation to make an implementation appear grounded.

## Establish the project context

Read the applicable project instructions and the code involved in the request. Inspect only the relevant manifests, lockfiles, configuration, and existing tests.

- React/Next.js: establish the resolved package versions where possible, package manager, JavaScript or TypeScript conventions, runtime, and App Router or Pages Router usage. A dependency range alone is not the resolved version. Account for framework-provided React behavior where applicable.
- Go: inspect `go.mod`, relevant `go.work`/`replace` directives, and the installed toolchain when available. Distinguish the module's Go directive, toolchain directive, and selected dependency versions.
- CSS/JavaScript: identify the browser/runtime targets and relevant build configuration. Language syntax, DOM/Web APIs, and Node.js APIs have different support boundaries; a current documentation snapshot does not guarantee availability in the target environment.
- Keep the existing stack and versions unless the task requires changing them. Do not turn a feature or bug fix into an unsolicited migration.

For an existing repository, read [Existing repositories](references/existing-repositories.md) before consequential changes. Establish the affected package and behavior, preserve uncommitted work, and capture a relevant baseline. Extend existing architecture and compatible domain logic; this skill does not authorize re-scaffolding, dependency upgrades, broad cleanup, or replacing project conventions with a tutorial's structure. Small edits need only proportionate discovery.

## Assess architecture before consequential builds

For a new application, substantial data-flow/deployment change, or explicit scalability question, present a concise workload and architecture assessment before implementing the affected architecture. Establish peak requests/actions, data growth, expensive operations, latency/error objectives, relevant cost/team constraints, and likely bottlenecks. Distinguish documented limits, assumptions, and measurements; a framework name and a total user count do not establish capacity. Explain what to build now, what to defer, and observable triggers for revisiting the design. Reuse existing assessments for small changes.

If `plan-web-capacity` is installed, use it for this assessment; otherwise apply the criteria above using the relevant maintainer docs. If capacity testing is requested and `validate-web-capacity` is available, use it to guide representative measurement. These skills are optional companions: do not promise a user ceiling without workload-specific evidence or impose a new approval gate on ordinary authorized implementation.

## Consult the right documentation

Before choosing or changing behavior that depends on a framework or language API, use the bundled local documentation helper. Read [Local documentation](references/local-docs.md) for commands and portable cache behavior. Resolve the helper path relative to this skill folder, not the current project directory.

1. Run `python "<skill-folder>/scripts/doclib.py" ensure --project "<relevant-project-directory>"`. This automatically downloads missing official docs and records the project's snapshot selection in the library, outside the project. Reuse cached snapshots on later calls. Run it at the relevant application directory in a monorepo.
2. For a plain or new website, add `--web` to `ensure` so CSS, JavaScript, and common browser API docs are available even before files exist. Existing React/Next.js and plain web projects are detected automatically. Search with `search "<focused API or topic>" --stack react|nextjs|go|css|javascript --project "<same-directory>"` and read useful section IDs with `read ID`. Prefer the project's bundled Next.js docs when available. Search results alone do not establish the full API contract.
3. Respect reported resolution errors. For unresolved package ranges, establish the actual version before passing an explicit override. React docs match major versions rather than individual minor/patch releases; Go website guides are revision snapshots. Verify finer-grained API availability when needed.
4. Use the web for missing material, unresolved version details, or requested freshness checks. Do not refresh all sources before every task or load the full documentation corpus into context. For a new project whose versions are undecided, `sync` can cache current stable docs.

Read only the stack references needed for the task:

- [React](references/react.md): components, state, Hooks, effects, and React APIs.
- [Next.js](references/nextjs.md): routing, server/client boundaries, data fetching, caching, and deployment behavior.
- [Go](references/go.md): language, standard library, modules, toolchain, concurrency, and services.
- [CSS and JavaScript](references/web-platform.md): layout, cascade, styling, JavaScript semantics, and common DOM/browser APIs.

The helper requires Python 3.11+ and Git for first-time repository downloads, and no API key, MCP server, or paid service. If a prerequisite is missing, report it and use available official documentation tools. When searching the web, search within the official domain and open the actual result; a search snippet or an unopened URL is not verification. Use first-party migration guides, release notes, and tagged source/tests when the main docs do not resolve a version-specific detail.

For additional dependencies, use `dependency-docs` when installed: run its `ensure --project PROJECT_DIR` during onboarding and after manifest/lockfile changes, then search/read the relevant package sections before implementing consequential APIs. It supports npm and Yarn Classic/modern (including PnP) without installing packages. Reuse identifiable same-major snapshots while checking minor/patch availability; use `--exact` when needed. Inspect coverage: a publisher README is a limited reference, and private/local/unresolved dependencies need appropriate project or maintainer sources. Otherwise consult those sources directly. Hosting on GitHub or pkg.go.dev alone does not establish maintainer identity.

If the user asks to investigate a community solution, verify its API assumptions against the applicable maintainer references or standards. Where documentation leaves a choice open, choose based on the user's needs and project conventions.

If web access fails, use local version-matched package declarations/source, `go doc`, or an available documentation snapshot and disclose the limitation. Do not claim to have checked current docs. Continue work supported by the available evidence; identify any material unresolved assumption. Do not replace missing older documentation with current behavior silently.

## Implement and verify

For function/module additions, refactors, or documentation changes, read [Code quality](references/code-quality.md). Use cohesive responsibilities, visible side-effect boundaries, useful contract/rationale documentation, and a search for existing behavior before introducing a production helper. Use `audit-code-reuse` when available for substantial duplication or unused-code questions; an absent text reference alone does not justify deletion.

Adapt documented APIs to the project's requirements instead of transplanting a whole example. Preserve relevant behavior, follow existing organization, and introduce dependencies only for a concrete need.

For work crossing Next.js/React and Go, establish the existing request/response contract, serialization, authentication boundary, and error behavior. Make browser-facing and server-side calls consistent with that contract. Documentation for each framework does not by itself establish the application's API contract.

Use the project's existing commands and active package manager for the checks appropriate to the change. For Yarn projects use their configured Yarn version and scripts (`yarn build`, `yarn test`, or the actual workspace commands); do not create an npm lockfile or switch managers for convenience. Check observable behavior and failure cases for meaningful logic changes. Avoid adding tooling or tests merely to restate a trivial implementation. Never claim a check passed if it was not run; report missing dependencies or unavailable services.

For asynchronous mutations, persistent client state, subscriptions, or retry/recovery behavior, read [Asynchronous operation contracts](references/async-operations.md). Verify relevant ownership changes and response ordering across the client/server boundary; a server idempotency test alone does not prove the UI reuses the same logical operation.

In the final response, briefly state what changed, the verification outcome and material limitations, and link the official pages or revision-pinned source URLs of local sections actually consulted for consequential decisions. Separate documented facts from project-specific reasoning. Do not add research logs, citation comments, or documentation files to the repository unless requested or useful to maintainers.

---
name: audit-code-reuse
description: "Find existing implementations before adding helpers, investigate duplicate domain logic, and identify potentially unused functions/modules with reachability evidence. Use for reuse checks, duplicate-code audits, and dead-code cleanup; exclude deletion based only on text counts or forced abstraction of unrelated logic."
---

# Audit Code Reuse

Help the project reuse compatible behavior and remove justified dead code without breaking hidden entry points or public contracts. Distinguish a search candidate from a proven duplicate or unused implementation. Perform the requested analysis first; make refactors/deletions only within the authorized task scope.

## Find existing behavior before adding code

Establish the operation's expected behavior, types, inputs/outputs, errors, side effects, and owning layer. Inspect the relevant module layout and public contracts. Start with `rg --files` and focused `rg` searches across project-owned source, excluding dependency/build/generated output unless it is relevant evidence. Search domain verbs/nouns, types, routes, call sites, and tests; names alone miss semantic duplicates.

For an established repository, include relevant workspace/shared packages, configured aliases/replacements, plugins, and existing architectural boundaries in the search scope. Check repository instructions and pending work before proposing edits. Do not conclude that a helper is absent from the application after searching only the current feature folder, or that code can be removed after analyzing only one executable/target. Keep the investigation bounded to implicated behavior and report unresolved external/dynamic consumers.

Inspect likely candidates and their consumers. Compare the actual contract, edge cases, authorization/ownership, transaction/cancellation semantics, runtime availability, and dependency direction. Prefer calling an existing compatible implementation or making a small coherent extension. If none fits, identify the nearest candidate and explain the concrete mismatch before proposing a new helper. Keep that explanation in the handoff rather than scattering research comments through the code.

For existing duplication, determine whether the code represents the same domain rule or only similar syntax. Consolidate only when a shared boundary preserves behavior and reduces maintenance cost. Avoid unrelated wrappers, cross-layer dependencies, or generalized helpers with mode flags that obscure different responsibilities. Separate implementations can be justified when their rules or future reasons to change differ; record material intentional duplication concisely.

## Investigate unused candidates

Use compiler/language-server references, call/import graphs, and configured project analyzers where available. A text search or an analyzer finding is evidence within its analyzed entry points/configuration, not a universal removal guarantee. For JavaScript/TypeScript, inspect an existing unused-code tool such as [Knip](https://knip.dev/overview/getting-started) and its entry/plugin/workspace setup. For Go executables, the Go team's [deadcode guidance](https://go.dev/blog/deadcode) describes whole-program unreachable-function analysis. Read the selected tool's current documentation and options before running it; do not silently install new global tools or assume a normal Go build/vet pass finds all unused functions.

Check framework-recognized routes, exported APIs, package entry points, callbacks passed as values, registration maps, reflection/dynamic property access/imports, tests/examples, generated consumers, build tags/platform variants, and externally consumed packages when relevant. A public library export can have consumers outside this checkout. Dynamic or unsupported configurations may leave usage unknown.

Classify each finding as: unused within the explicitly analyzed scope, likely unused with remaining uncertainty, or retained because of a known/dynamic/external entry point. State the scope, evidence, affected consumers, and a recommendation. Do not report a symbol as definitely unused merely because its name appears once.

## Refactor or remove with evidence

Coordinate ownership before changing shared utilities or files another agent is editing. Preserve the original contract or update affected consumers and agreed documentation together. Avoid deleting or changing public APIs as incidental cleanup. For meaningful consolidation/removal, run appropriate builds/tests and a behavior-focused regression check when needed; review the resulting diff and relevant runtime/configuration paths. Report coverage gaps honestly. Do not hide an uncertain removal behind disabled tests or unrelated changes.

Return concise findings with file/symbol locations, evidence/limitations, reuse or consolidation choices, files changed if authorized, and checks actually executed. When used before a new helper, a short statement of the search scope and compatible existing candidate (or reason none fits) is enough. A repository-wide audit is unnecessary for every local variable or trivial inline transformation.

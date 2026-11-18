# Unreal reuse and reachability

Use the shared `audit-code-reuse` skill when installed, with these engine-specific constraints. Without it, search the relevant code/contracts and apply the same evidence standards directly. Search project-owned source first, excluding normal `Binaries`, `Intermediate`, `DerivedDataCache`, and `Saved` output. Inspect generated metadata only when it is evidence, not a file to edit.

Before adding gameplay helpers, inspect existing classes, components, interfaces, subsystems, modules/plugins, delegates, and applicable engine APIs. Search by operation and types as well as names. Compare world/lifetime context, authority, threading, state ownership, reflection, and serialization behavior before reuse. A generic utility is not automatically a safe replacement for an engine-aware operation.

No direct C++ caller does not prove an Unreal symbol is unused. Relevant consumers include reflected `UFUNCTION`/`UPROPERTY`/class metadata, Blueprint graphs and overrides, virtual engine hooks, input/delegate bindings, registration tables, string/FName/config references, save games, soft/hard asset references, editor tools, plugins, generated code, and platform/target build variants. Public plugin/module APIs may have consumers outside the checkout.

Use language-server/call references and configured static tooling where applicable, then inspect Unreal's asset/reference information with the editor, Asset Registry, Reference Viewer, or a suitable documented bridge when authorized and available. C++ static reachability does not by itself prove absence of Blueprint/asset consumers. Text grep of `.uasset` files is not a complete reference analysis. If the editor or relevant assets cannot be inspected, report the uncertainty instead of deleting candidates.

Preserve serialized/reflected names and paths unless renaming/removal is in scope and references/migration needs are established. Coordinate redirector/reference updates and affected saves/packages with a single writer. Do not mass-delete assets, remove reflection declarations, or run broad fix-up commandlets just to improve an unused-code count. Binary assets/maps must be modified through appropriate Unreal tools, not text patches.

For a meaningful consolidation/removal, verify the relevant Unreal target builds and affected Blueprint/assets/runtime scenarios, including cook/package when relevant. Report the configuration and coverage. An editor-only success does not prove a runtime package, dedicated server, or another target still works.

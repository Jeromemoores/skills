# Unreal C++ quality and documentation

Follow the installed version's [Epic coding standard](https://dev.epicgames.com/documentation/en-us/unreal-engine/epic-cplusplus-coding-standard-for-unreal-engine), project conventions, and actual module/toolchain settings. Use [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) for applicable general C++ reasoning, not as a replacement for engine-specific behavior. Preserve appropriate source ownership notices rather than copying an Epic copyright header into unrelated new user-owned code.

## Cohesion and visible effects

Give functions a coherent purpose and descriptive names. Separate reusable calculations/queries, gameplay state changes, and presentation where these are distinct responsibilities. A getter or Blueprint-pure operation must not hide unrelated mutations or UI side effects. An interaction handler/application operation can legitimately coordinate several steps; do not create meaningless wrappers to satisfy a function-length quota. Preserve atomic state transitions and correct sequencing when refactoring.

Document public/Blueprint-facing and non-obvious contracts: effects, preconditions, outcomes/errors, ownership/lifetime, thread/world context, authority, and persistence/replication when relevant. Explain reasons and constraints rather than narrating obvious statements. Keep declarations/comments and Blueprint-facing metadata synchronized with behavior. Do not use a comment to assert an untested guarantee.

## Engine object and execution boundaries

Identify whether a value is a UObject-managed object, an actor/component, or a non-UObject C++ resource. Verify the appropriate creation, owning references, GC/weak-pointer behavior, invalidation, and destruction using the object-pointer/lifetime docs and actual headers. Standard/shared C++ ownership advice cannot be assumed to manage Unreal's GC objects correctly. RAII remains useful for appropriate non-UObject resources.

Distinguish constructor/CDO/default-subobject setup from runtime world-dependent behavior. Verify lifecycle hooks, component registration, repeated PIE/world teardown, timer/delegate binding/removal, and latent/asynchronous callback captures. Check valid object/world context at execution time; a pointer captured earlier may no longer represent a live object. Do not move game-thread/engine operations to worker threads merely because general C++ concurrency permits a container operation.

For networking, identify authority, owning connection, replication state, RPC ownership/reliability, and client presentation separately. A local or single-player test does not establish server/client correctness. Do not equate multi-user editor collaboration with gameplay replication.

Respect reflected declarations, generated-header requirements, module export/dependency boundaries, and supported build settings. Source/header or reflection changes may require a different rebuild/restart path than an ordinary function-body patch; consult the engine's Live Coding/UHT guidance. Generated files, binaries, and cached build products are not the authoritative place to implement a fix.

## Scope and measurement

Search project modules, existing engine/plugin capabilities, and appropriate components/subsystems before adding helpers or a new manager. Reuse compatible behavior; compare lifetime, state, network, serialization, and dependency contracts before consolidating superficially similar functions. Keep runtime modules free of accidental editor-only dependencies.

Avoid unnecessary per-frame work, but preserve legitimate continuous updates. Use profiles/traces to establish a real hotspot and validate the actual change. Do not introduce pooling, concurrency, custom containers, engine modifications, or broad architectural abstractions solely because they sound faster. Treat CPU, render/GPU, memory, streaming, and networking as different budgets with explicit target conditions.

## Review recommendations

Suggest useful improvements within the reviewed system even when no correctness bug is found. Separate optional refactors and efficiency opportunities from defects; give the C++ function, Blueprint graph/function, asset, or module location and explain a concrete benefit. Do not invent recommendations to fill a quota.

For mixed responsibilities, identify the proposed boundaries: for example, reusable damage calculation, authoritative state mutation, and cosmetic/UI feedback may deserve separate functions when currently tangled. Explain what remains in the coordinating gameplay action. Consider an existing component/interface/helper before proposing a new component, subsystem, manager, or parallel Blueprint/C++ implementation. Extract a meaningful concept or testable contract, rather than splitting solely by function length or creating trivial wrappers. Keep intentional sequencing and atomic state transitions intact.

Account for reflected/Blueprint callers, node/API metadata, object ownership/GC, world context, authority and replication, save/config/asset references, and runtime/editor module dependencies when affected. A source-level extraction can change those contracts; inspect the relevant matching engine docs/headers and consumers before recommending the shape. Avoid wholesale Blueprint-to-C++ conversion or a replacement gameplay framework as routine cleanup.

For efficiency, look for code-supported opportunities such as repeated actor/object searches, duplicate calculations or allocations, unnecessary per-frame work, and excessive replication/RPC activity where present. State the actual frequency, entity/content scale, and execution context that could make the work material. Treat these as hypotheses until relevant evidence establishes impact. Compare event-driven updates, caching, batching, or reuse only with their invalidation, lifetime, ordering, memory, and networking tradeoffs; none is a universal upgrade.

For each worthwhile suggestion, give a bounded change or short before/after responsibility outline, expected benefit, material risks, and a verification plan. Use representative Unreal Insights or appropriate profiling evidence for runtime claims, and target the actual game-thread, render/GPU, memory/streaming, or network budget. Use build/UHT, Blueprint consumer checks, functional tests, and affected multiplayer roles to verify behavior as appropriate. A readability improvement can be justified without a speed claim. Prioritize a few valuable changes and make edits only when the user's task includes them.

## Commonly missed cases

These are frequent sources of real defects. Treat each as a candidate to check against the matching documentation for the project's version, not as a rule to apply blindly or a complete list.

- **UObject references:** an untracked raw member does not keep its target alive and can dangle. Use the project's reflected strong-reference pattern or `TWeakObjectPtr` for non-owning references. Check a valid tracked/weak handle before use; `IsValid` does not make an arbitrary stale raw address safe.
- **Captured `this`:** a lambda bound to a timer, delegate or async task outlives the object. Use the weak-binding forms or check a weak pointer before use.
- **Constructors also run for class default objects and editor loading.** A valid runtime world is not guaranteed. Create default subobjects there; use appropriate runtime lifecycle hooks for world queries, spawning and timers.
- **Symmetric teardown:** clear timers and unbind delegates in `EndPlay`/destruction, and call the `Super` implementation in overridden lifecycle functions.
- **Delegates:** dynamic member bindings require the reflected function signature. Check duplicate multicast subscriptions and teardown for the binding API in use. UObject-aware bindings can track weak references; raw bindings and lambdas capturing `this` need different lifetime protection. [Binding semantics](https://dev.epicgames.com/documentation/en-us/unreal-engine/delegates-and-lambda-functions-in-unreal-engine)
- **Replication:** verify native property registration and a replicating actor/component. C++ assignment does not automatically invoke server-side `OnRep`. Client-originated Server RPC routing depends on ownership/connection rules. High-rate reliable traffic can overflow buffers under load/loss; measure and bound it.
- **Tick:** disable ticking where it is not needed, and prefer events or timers for infrequent work.
- **Hard references:** loading the owning class/asset can pull in referenced dependencies, not necessarily only at startup. Consider soft references/async loading for optional or large content after checking load timing, lifetime and failure handling.
- **Text types:** `FText` for user-facing localizable text, `FName` for identifiers, `FString` for manipulation.
- **Modules and headers:** missing `.Build.cs` dependencies can cause include/UHT/compile/link failures. The `.generated.h` include must be last. Keep editor-only dependencies out of runtime targets, using appropriate guards/module separation and a real package check.
- **Containers:** adding to a `TArray` can reallocate and invalidate pointers and references to its elements; removing while iterating needs the appropriate iterator or reverse loop.
- **Live Coding:** structural-change support depends on engine version and object-reinstancing settings. Check matching guidance, invalidate affected cached pointers, and use a clean rebuild/restart when required or when patch state is unreliable; a patch is not a clean-build/package check. [Live Coding and reinstancing](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-live-coding-to-recompile-unreal-engine-applications-at-runtime)

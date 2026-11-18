# Design Unreal regression checks

Start with the gameplay or serialized/asset contract, a specific trigger and an observable oracle. Choose the matching installed engine's documented unit/low-level, automation, functional, multiplayer or packaged-target mechanism. [Epic's automation overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/automation-test-framework-in-unreal-engine) is an entry point; test availability and invocation still depend on the actual engine/project.

Use deterministic pure tests for engine-independent calculations, engine-aware tests for reflection/world/subsystem behavior, and appropriate functional maps/sessions for gameplay and network roles. A source parse or mocked UObject cannot establish real lifetime, replication, content loading or cook behavior. Select only the boundaries the change affects.

Define meaningful expected state independently of the implementation: ownership, authoritative counts, serialized values, received events or resource cleanup. A no-crash observation alone can miss incorrect gameplay. Reuse suitable project fixtures and preserve existing user maps/assets/saves.

Control relevant ordering with explicit engine test conditions: owner teardown, world travel, late joining or old callbacks after replacement. Reset worlds/fixtures and clean up delegates, timers, actors and sessions on both success and failure. Keep timeouts bounded and distinguish an assertion failure from unavailable SDKs, test content or editor/runtime access.

Capture project/source snapshot, engine/fork, target/platform/configuration, required plugins/assets, command and actual result. For a meaningful defect, demonstrate baseline failure then corrected behavior where feasible; maintain older-save/asset fixtures for compatibility work. Rebuild/reload as required by the changed contract instead of assuming Live Coding validates serialized/reflected changes. Profiling regressions also need equivalent representative scenes and measurement conditions.

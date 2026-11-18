---
name: validate-unreal-project
description: "Validate Unreal C++/Blueprint changes with appropriate real engine builds, automation, editor/runtime checks, cook/package checks, and representative profiling. Use for game-system verification, regressions, multiplayer tests, and performance evidence; exclude unsupported success claims from syntax checks or empty-map benchmarks."
---

# Validate Unreal Project

Match the check to the actual claim. Inspect the intended `.uproject`, engine version/build, target/config/platform, changed source/assets/config, available SDKs/toolchain, editor state, and relevant existing checks. Use `official-unreal-dev` if installed or first-party docs/local engine evidence directly. If workload/budgets are missing, establish them before interpreting a capacity/performance result; `plan-unreal-project` can help when available.

For an existing project, identify pending source-control/unsaved editor work and establish relevant build/runtime results before changes where feasible. Reuse established test maps, automation, and representative content without overwriting real player data or user saves. Compare equivalent target/configuration, content, and profiling conditions for regression claims; distinguish baseline failures, new failures, and unavailable checks. Validate affected existing Blueprint/asset/public consumers and compatibility, rather than exercising only a newly added sample map.

## Build and behavior evidence

Choose an appropriately scoped real Unreal Build Tool/UHT target for source/reflection/module changes. Derive the correct executable, arguments, target, and configuration from the project/version rather than guessing them. Keep editor/runtime-only/server target differences visible. A generic compiler parse or code-generation stub does not prove a reflected Unreal build works.

Live Coding/Hot Reload, a fresh build, editor load/Blueprint compile, PIE, standalone, automation, cook/package, and a launched packaged build establish different things. Use the checks affected by the change and record which were actually run. A successful patch or command acknowledgment alone is not packaged/runtime validation. Structural/reflection/default changes can need a different rebuild/reload process; inspect the applicable docs and preserve user work before any required editor restart.

Run relevant automation or functional checks and exercise changed gameplay behavior, errors, cleanup, repeated start/stop, world transitions, and affected object lifetimes. Verify Blueprint/asset consumers when reflected/public contracts change. When multiplayer is in scope, distinguish standalone, listen/dedicated server, authority/owning/remote clients, and late joining/reconnection as relevant; one local viewport is insufficient evidence. Treat editor Multi-User collaboration as a separate system.

When asynchronous callbacks or pending operations change, choose a focused adversarial ordering: complete work after owner teardown/world transition, or complete older work after a replacement operation starts, as the feature permits. Use deterministic synchronization or appropriate engine test controls and assert authoritative gameplay state, cleanup, and ownership; absence of a crash alone does not establish correctness. Select checks from the documented API's actual lifetime/thread/cancellation contract and report missing engine/runtime evidence. Do not impose these cases on unrelated changes.

For cook/package changes, verify the intended target assets/maps, runtime module dependencies, saved references/redirectors, and loading behavior as relevant. Do not manipulate binaries/generated files to simulate success. If a platform SDK, engine build, editor connection, content dependency, or test runner is missing, report exactly which check is unavailable.

## Representative profiling

State hardware/OS/driver, engine and build configuration, resolution/render API/quality/upscaling, frame caps, scene/content state, warm-up/shader/streaming conditions, duration, and relevant input/network workload. Compare equivalent conditions; an empty scene, a debug/editor build, and a shipping target are not interchangeable performance tests. Profile game/render threads, GPU, memory/VRAM, streaming/loading, or network/server tick as the question requires. Prefer Unreal Insights and relevant documented engine profiling tools where available.

Check that instrumentation, frame caps, or the test host are not determining the result. Report frame-time distributions/hitches and relevant resource evidence rather than an unsupported headline FPS. Treat multiplayer bandwidth/latency/loss/relevancy conditions explicitly. For a suspected hotspot, reproduce, identify supporting trace evidence, change a justified factor, and remeasure comparable behavior when needed. Do not infer linear gains from more threads, a pool, a new engine version, or a stripped-down sample.

## Scope, artifacts, and reporting

Use the user's authorized project/environment and limits. Preparing docs does not authorize launching or modifying an unrelated game/editor. Avoid overwriting unsaved work, conflicting asset writes, broad content fix-ups, unrequested platform/toolchain installation, or material paid infrastructure as incidental testing. Reuse explicit session authorization; ask only when genuinely missing scope is required. State bounded duration/load/stop conditions proportional to the test's resource use and side effects.

Return actual commands/actions, target/config/version, affected code/assets, observed results, saved artifacts/traces/logs when useful, and untested coverage. Separate repaired-and-verified findings from hypotheses and estimates. Do not claim game correctness, target-platform compatibility, long-duration stability, maximum players/entities, or FPS beyond the measured conditions. If all roles ran in one context, disclose the absence of an independent review pass.

Relevant primary references: [Automation framework](https://dev.epicgames.com/documentation/en-us/unreal-engine/automation-test-framework-in-unreal-engine), [Unreal Insights](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-insights-in-unreal-engine), [UHT](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-header-tool-for-unreal-engine), and [packaging](https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project). Use the project's version and open the actual applicable sections.

---
name: plan-unreal-project
description: "Assess Unreal game/system architecture, target platforms, object/network ownership, content workflow, performance budgets, and growth risks before a substantial build or redesign. Use for gameplay system plans, frame/memory budgets, multiplayer scope, and engine/plugin choices; exclude small edits and unmeasured player/entity guarantees."
---

# Plan Unreal Project

Produce a practical, evidence-based assessment before implementing consequential architecture. Read existing requirements, `.uproject`, engine/build version, relevant modules/plugins/config, assets, and measured evidence. Use `official-unreal-dev` when available for matching references, otherwise consult Epic and actual installed source/toolchain evidence directly.

For an established game/plugin, map the affected current gameplay/content/authority flow and inspect representative baseline evidence before proposing new systems. Reuse compatible extension points, module boundaries, tooling, and supported engine/platform constraints. Compare incremental changes with the current design, including affected Blueprint/asset/plugin consumers and save/config/network compatibility when relevant. Include transition and validation costs for a justified migration; onboarding alone is not permission for an engine upgrade, framework replacement, or broad content rewrite.

Establish the intended gameplay/user flows, target platforms/hardware, resolution/render settings, FPS/frame-time and memory/loading objectives, content/world/AI/physics complexity, persistence, and multiplayer needs. Distinguish total players/accounts from players per session, locally visible/simulated entities, replicated relevant actors, update/message rates, and server tick workload. Ask only about material unknown decisions; otherwise use explicit scenarios instead of fabricated targets.

Convert target FPS to a frame-time budget when useful (1,000/FPS in milliseconds), but do not simply add pipelined CPU/render/GPU times or equate a budget with measured performance. Establish relevant platform constraints and quality/settings assumptions. A game-thread bottleneck, GPU bottleneck, memory/VRAM pressure, content streaming hitch, network saturation, and slow iteration/build pipeline require different evidence and remedies.

Choose coherent boundaries for actors/components, subsystems, data/assets, modules/plugins, C++/Blueprint responsibilities, UI presentation, persistence, and authority when relevant. Verify object/world lifetimes and asynchronous/thread ownership. Compare existing engine/project capabilities before adding a manager/framework or custom implementation. Do not choose a larger architecture or engine fork solely because an ambitious player/entity number was mentioned.

Use current version-appropriate primary docs for relevant engine features, target SDKs/toolchains, and platform/deployment limits. Distinguish documented constraints, measured results, modeled estimates, and unknowns. Give alternatives only when a real tradeoff matters, including complexity, iteration time, operational burden, and migration cost. Identify the simplest viable starting point and evidence-based triggers for revisiting it.

For a team, define ownership of shared source interfaces, module/build config, reflected/serialized names, binary maps/assets, editor state, and validation artifacts before parallel work. A coordinator can use `coordinate-project` if installed. Worktrees isolate files but do not resolve conflicting binary asset or shared editor state changes.

Present the requirements/assumptions, proposed system/data/authority flow, relevant budgets and risks, what to build now/defer, and the validation plan before implementing affected architecture. Do not impose a new approval gate on ordinary authorized work; seek a decision only for material unresolved product/cost/correctness choices. Reuse the assessment for small edits and update it when evidence changes.

Use `validate-unreal-project` if available for measurement. Do not promise a maximum player count, entity count, FPS, memory footprint, or target-platform compatibility without representative evidence. A documentation example, framework claim, empty map, or single PIE viewport does not establish those capacities. Save a design document when requested or consistent with the project's established workflow.

Primary references as needed: [Gameplay framework](https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-framework-in-unreal-engine), [Unreal Insights](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-insights-in-unreal-engine), and [networking](https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-and-multiplayer-in-unreal-engine). Select the project's engine version and inspect actual content rather than assuming the unversioned URL matches.

---
name: official-unreal-dev
description: "Build, extend, debug, review, or explain new and existing Unreal Engine C++/Blueprint projects using cached Epic/C++ documentation and matching installed headers. Use for gameplay, modules, reflection, assets, UI, networking, and tooling; exclude unrelated web work and unrequested engine upgrades."
---

# Official Unreal Development

Use documented engine behavior and actual project/version evidence before consequential implementation choices. Treat recalled examples as candidates to verify. Engine rules, platform/toolchain support, and observed behavior take priority over generic C++ advice. Documentation supports decisions; it does not prove game correctness or measured performance.

## Workflow

1. Read the project instructions, the intended `.uproject`, engine/build version and the code and assets involved.
2. Run the local documentation helper; read matching Epic pages and installed headers for the affected APIs.
3. Implement within the current modules and asset contracts, with one writer per shared binary asset.
4. Verify with a real Unreal build and the runtime checks the change affects.
5. Report what changed, the checks actually run and what remains unverified.

## Companion skills

Use these when installed and the change calls for them; otherwise apply the same criteria with Epic docs and installed engine evidence. Small changes can reuse existing decisions, and none of these adds unrelated audits.

- `plan-unreal-project`: assessment before substantial architecture or performance changes.
- `validate-unreal-project`: build, automation, runtime, cook/package and profiling evidence.
- `dependency-docs`: inventory and references for third-party libraries and enabled plugins.
- `coordinate-project`, `implement-task`, `review-and-repair-code`: a requested team workflow and shared review reporting.
- `review-security`: a requested security review or an affected untrusted-client/plugin boundary.
- `plan-safe-migrations`: save, serialized or reflected-asset compatibility changes.
- `audit-code-reuse`: substantial reuse or unused-code questions.

## Establish the actual project

Read applicable project instructions, the intended `.uproject`, engine association/build version, relevant `.uplugin`, `.Build.cs`/`.Target.cs`, configuration, code, and asset contracts. Distinguish engine major.minor docs from the installed patch/fork and actual compiler/C++ standard. Do not silently migrate a project, enable a plugin, or switch toolchains because current docs describe a newer feature.

For an existing repository/game, read [Existing Unreal projects](references/existing-projects.md). Map the affected source/Blueprint/asset consumers, preserve pending source-control and unsaved editor work, and establish an appropriate build/runtime baseline. Integrate with the current project rather than creating a replacement module, gameplay framework, or sample project for convenience. Scale discovery to the requested change.

For substantial architecture/performance changes, establish gameplay requirements, target hardware/platforms, frame/memory/load-time goals, multiplayer/session assumptions, relevant ownership/lifecycle boundaries, and likely constraints. Present that assessment before implementing affected architecture.

## Read matching references first

For third-party libraries and enabled plugins, inventory the project directory and prepare available maintainer references with `dependency-docs`; rerun its `ensure` after dependency changes. vcpkg baselines and Unreal plugin descriptors may lack resolved versions; report those gaps and inspect matching installed descriptors/headers. An engine's major number, a wrapper version, and a plugin's version are different identities. Cached upstream docs do not establish compatibility with a local patch or Unreal ABI. Use appropriate maintainer/project sources for private or unsupported dependencies.

Read [Local documentation](references/local-docs.md) and run the bundled helper relative to this skill folder:

```text
python "SKILL_DIR/scripts/unreal_docs.py" ensure --project "PROJECT.uproject"
python "SKILL_DIR/scripts/unreal_docs.py" search "object pointers" --stack unreal --project "PROJECT.uproject"
python "SKILL_DIR/scripts/unreal_docs.py" read SECTION_ID --max-chars 6000
```

Add relevant topic groups or cache a specific verified Epic page as needed. Read useful sections and source headers, not the full corpus. Reuse references already read during the task. Use first-party web docs when local coverage is missing; never claim a blocked page, search snippet, or guessed URL established an API contract. Report missing evidence and distinguish documented requirements, recommendations, your design choices, and measured results.

Epic pages are checked at major.minor; use the installed headers/source to resolve API signatures and patch/fork differences. Microsoft C++ docs include implementation-specific behavior, while C++ Core Guidelines are advisory rather than the normative standard. Confirm the project's compiler/standard/platform support before adopting syntax or library features. Do not transplant general C++ ownership/error-handling prescriptions into Unreal without checking engine/module rules.

For consequential documented guarantees, connect the constraint to the actual implementing mechanism and a runtime check that could falsify it. For timers, delegates, async loads, tasks, and network callbacks when affected, establish object/world lifetime, operation identity, execution context, notification, and completion/cleanup ownership from matching Epic docs/headers. Verify late or out-of-order completion cannot act on a destroyed/replaced owner or clear newer work. Cancellation or unbinding must be checked against the actual API contract; do not assume it undoes an already completed effect. Keep this evidence in the normal task/review handoff.

Use [Unreal C++ and code quality](references/unreal-code-quality.md) for object lifetime, reflection, dependencies, clean functions, and documentation. Use [Reuse and reachability](references/reuse-and-reachability.md) before adding shared logic or removing allegedly unused reflected code/assets. For networking or performance, fetch the applicable topic docs and verify authority, state ownership, execution context, and measurement assumptions.

## Coordinate code and assets

For a requested team, provide Unreal-specific constraints and references in each packet; generic web assumptions do not apply. Assign a single writer to each shared binary asset/map, shared module/build configuration, and editor-global operation. Separate worktrees do not make incompatible `.uasset`/`.umap` edits safely mergeable.

Inspect a connected editor's project/version/state before operating it. Use available documented bridge capabilities or project tools rather than inventing actions. A docs task does not require starting the editor or changing the game. Do not edit binary assets as text, modify generated intermediates as source, or overwrite another agent's pending work. Preserve unsaved user work and use the user's existing authorization for the actual requested project operations.

## Verify the changed behavior

For security and persisted-compatibility questions, follow engine-specific references and tests; web ASVS requirements do not establish Unreal networking or serialization behavior. A generic source rename can have persisted consumers even when compilation succeeds.

For a code review, assess useful maintainability and efficiency improvements as well as defects. Follow the review-recommendation criteria in [Unreal C++ and code quality](references/unreal-code-quality.md). Give concrete locations, bounded changes, expected benefits/tradeoffs, and verification, keeping optional refactors separate from acceptance defects. A review request does not authorize implementing its suggestions.

Run the relevant real Unreal build/UHT, automation, editor/runtime, and cook/package checks. Choose checks based on impact. A successful generic C++ syntax check, bridge response, Live Coding patch, or editor compile does not by itself prove the packaged target or gameplay works. Check lifetimes, repeated start/stop, relevant failure paths, and multiplayer roles when affected. Base optimizations on representative profiling.

Report changed code/assets, docs actually consulted, exact checks and results, and material gaps. Distinguish source changes, saved assets, compiled binaries, exercised runtime behavior, packaged output, and measured performance. Do not present absent editor/SDK/test access as successful validation or guarantee a player/entity count from framework choice alone.

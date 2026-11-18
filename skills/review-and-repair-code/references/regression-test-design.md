# Choose regression evidence

Start from the affected observable contract and a failure that could falsify it. Define the trigger, authoritative oracle, fixture and relevant execution boundary before choosing a test tool. Reuse equivalent coverage. A test that repeats the implementation's calculation or checks only that its helper was called can miss the actual defect.

Choose the narrowest meaningful boundary: a unit test for a deterministic transformation, integration for storage/transport contracts, and browser or real-engine behavior for lifecycle/input/ownership claims. Combine levels only when they establish different necessary facts. Explain what a stub omits; a transpiled handler with mocked state is not a mounted UI, and a generic C++ stub is not an Unreal runtime.

For a meaningful reproduced defect, make the focused check fail on the relevant baseline and pass on the proposed correction when execution is possible. Keep assertions independent: expected values/relationships, externally visible effects and authoritative state. Check supported legitimate behavior as well as the invalid/failure path. Avoid incidental line counts, internal naming, or test quotas.

Use representative disposable records/assets, older-format fixtures where compatibility matters, and controlled synchronization for important races. Prefer a completion barrier or explicit test condition over an arbitrary delay. Bound time/resources and arrange cleanup for success and failure; do not make a fixture reset someone's live data or unsaved editor work.

Identify the actual source snapshot and build/engine/runtime exercised. Rebuild or otherwise establish that generated code and running artifacts correspond to the reviewed source before claiming current behavior. Keep defect reproduction separate from verification of a proposed replacement, and report stale builds, missing tools or unrun tests explicitly.

For recovery/concurrency work, choose relevant ordering: commit then lose a response, retry an unresolved operation, replace its owner, or finish old work after a new operation begins. Assert logical identity and authoritative allocation/state, not only success text. For persisted data, include upgrade/retry and recovery on copies. These are selected risk-based cases, not mandatory exercises for every edit.

Return command/configuration, fixture/baseline, expected and observed result, and material remaining coverage. A passing check establishes its actual conditions. Do not weaken failing assertions, hide errors, convert an unexecuted check to passed, or claim an independent review when the same context built and checked the change.

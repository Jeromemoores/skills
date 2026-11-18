---
name: review-and-repair-code
description: "Review new or existing code for correctness, maintainability, and performance; reproduce defects, suggest useful refactors/optimizations, and repair within authorized scope. Use for code checking and review-and-fix work; honor review-only requests and exclude cosmetic-only rewrites or unsupported correctness/performance guarantees."
---

# Review and Repair Code

Inspect the implementation and its observable behavior rather than trusting a builder's summary. Prioritize defects that affect the user's requirements, correctness, data integrity, integration, and relevant security/error boundaries. Keep style preferences separate from material findings.

## Establish the review boundary

For affected third-party APIs or dependency changes, use `dependency-docs` when installed to check the actual resolved versions, changed inventory and reference coverage. Prepare missing relevant docs and verify consequential contracts against matching maintainer sources. Separate missing documentation from demonstrated code defects; unrelated undocumented dependencies do not by themselves block the review. Do not infer exact patch behavior from a same-major snapshot or complete API coverage from a publisher README.

Read the original requirements, applicable project instructions, shared contracts, relevant acceptance checks, and the actual diff/change snapshot. Identify the baseline and relevant configuration/dependency versions. If other agents are writing concurrently, coordinate a stable snapshot or single-writer handoff before evaluating or repairing affected files. Preserve unrelated user/agent work.

For established repositories, review integration with the existing module boundaries, conventions, compatible helpers, and downstream consumers. Compare relevant before/after checks on equivalent configuration where feasible. Separate pre-existing defects/failures from introduced regressions and avoid treating unrelated dirty files as this task's changes. If no diff is supplied, scope the review to the requested current behavior rather than inventing a clean baseline. Check API/data/asset compatibility when affected; broad rewrites or cleanup do not follow from finding an existing issue.

Inspect high-impact paths first: state transitions, API/request validation, database transactions/concurrency, ownership/authorization, retries/idempotency, resource cleanup, and cross-component contract compatibility when the change touches them. Follow the actual control/data flow and important dependencies. Do not turn every review into an unrelated full-system audit.

Check changed functions for coherent responsibilities, hidden side effects, unnecessary duplicate domain logic, and missing/stale contract documentation. Verify whether a compatible implementation already exists before accepting a new helper. Use `audit-code-reuse` when available for deeper reuse/reachability questions. Do not demand tiny wrappers or remove public/framework/dynamic entry points simply to satisfy a style or unused-code count; preserve behavior, transaction boundaries, and language idioms.

Consult the version-matched maintainer documentation for disputed or consequential API assumptions. Use the applicable documentation skill when available: `official-stack-dev` for its supported web stacks or `official-unreal-dev` for Unreal. Otherwise consult appropriate maintainer references directly. A citation must support the behavior in question. A passing type check or familiar pattern does not establish the runtime contract. Conversely, distinguish a confirmed defect from a hypothesis requiring missing environment evidence.

Translate consequential documented contracts into concrete obligations and trace their implementation: notification on mutation, lifetime/cleanup ownership, retry identity, or atomicity as applicable. Check callbacks and adapters actually fulfill the contract rather than merely importing the correct API. Derive at least one focused adversarial check for a high-impact guarantee touched by the change, independently of the builder's happy-path tests; reuse equivalent coverage when it exists. Select relevant cases rather than imposing an unrelated test matrix.

For asynchronous/shared state, follow work across owner destruction/remount, resource/identity changes, and out-of-order completions when supported. Verify that old work cannot clear newer pending state and that the action a user sees submits the operation it promises. For retry claims involving remote effects, exercise commit-then-response-loss at the real integration boundary when feasible and reconcile authoritative state; mocked responses or server-only deduplication tests leave client recovery unproved. Use the relevant stack's lifecycle/reference guidance and state precisely which cases remain untested.

## Produce actionable findings

For each substantive finding, state the affected file/location, trigger or reproduction, expected versus actual behavior, impact, and the supporting evidence. Use severity appropriate to real impact and distinguish new regressions from relevant existing issues. Avoid speculative findings without a credible execution path; mark unresolved questions explicitly.

Run focused reproductions and relevant existing checks when feasible. Include failure cases and invariants the builder may have missed. Review tests for meaningful assertions and representative setup: stubs, single-process assumptions, empty databases, or cached endpoints can hide relevant failures. Do not report checks as run when you only inspected their code.

## Suggest useful improvements

In addition to bugs, look for concrete maintainability and efficiency improvements within the reviewed scope. Return worthwhile recommendations separately from correctness findings, including when no bug was found. Do not invent suggestions to fill a quota or label a preferred style as a defect.

For function boundaries, identify responsibilities that change for different reasons: reusable calculation/validation, persistence/network mutation, and UI/gameplay presentation. Suggest a specific extraction or separation when it clarifies effects, reduces meaningful branching/duplication, enables reuse, or creates a useful test boundary. Name the proposed responsibilities and explain what remains in the coordinating function. Preserve transaction atomicity, lifecycle/ownership, error handling, and required sequencing. A long function can be cohesive; several steps for one user action can be legitimate orchestration. Do not use line counts or one-line wrappers as a quality target. Search for a compatible existing implementation before proposing a new helper.

For optimization, inspect demonstrable unnecessary work such as repeated queries/network calls, avoidable scans or allocations, duplicate derived computations, and unjustified render/per-frame processing when relevant to the code. Explain the workload and execution frequency that would make it matter. Distinguish a measured bottleneck, a code-supported efficiency opportunity, and a hypothesis requiring profiling. State a representative benchmark/trace or behavioral check for the proposed change; never invent speedups or require a benchmark for a readability-only extraction. Consider caching invalidation, memory, contention, correctness, and complexity costs before suggesting caching, memoization, pooling, or concurrency. Use matching API documentation and stack-specific profiling guidance when needed.

For Unreal C++/Blueprint reviews, apply these criteria to the actual gameplay/module/asset boundaries. Use `official-unreal-dev` and its code-quality reference when available for concrete function/component separation, reuse, and performance recommendations. Check the effect on UObject/world lifetime, reflected/Blueprint consumers, authority/replication, serialization, and target builds before suggesting an extraction or optimization. Distinguish game-thread, rendering/GPU, memory, streaming, and network evidence; do not prescribe removing Tick, moving Blueprint logic to C++, adding subsystems, or pooling without a concrete reason and verification plan.

For each recommendation, provide the file/function location, concrete evidence/problem, a bounded proposed change or short outline, expected benefit, material tradeoffs, and how to verify preservation/improvement. Mark priority and whether it blocks acceptance based on actual requirements or evidence. A nonblocking improvement is not an unresolved correctness defect. Prefer the few changes with the clearest value over a large cleanup list, and retain intentional project conventions when no practical benefit justifies changing them.

## Repair within the authorized scope

Honor a review-only request by reporting findings without edits. When the user/session authorizes fixes, or the coordinator assigns a repair, make the smallest coherent correction under a single-writer arrangement. If the fix changes a shared API/schema or architectural decision, synchronize the contract and affected owners first. Do not redesign unrelated areas or weaken tests/requirements to remove a failure.

Suggesting a refactor/optimization does not itself authorize implementing it. A bug-fix assignment does not automatically include nonblocking cleanup. If improvement work is within scope, preserve observable contracts and verify the stated benefit with the appropriate evidence; separate structural/readability gains from measured runtime gains.

For a meaningful bug, demonstrate the failure before the correction when feasible and add or adapt a behavioral regression check when useful. Verify the correction and affected integration paths, then inspect the final diff. Record when reproduction or validation was unavailable. Distinguish remaining findings from repaired-and-verified findings; changing code alone is not proof of repair.

After two unsuccessful attempts at the same underlying issue, return the evidence and unresolved assumption to the coordinator/user for reassessment rather than applying repeated speculative patches. Continue independent review work where useful. Stronger models can help difficult diagnosis when the user's routing/budget permits, but review never guarantees an absence of defects.

Return the review scope/baseline, correctness findings with dispositions, useful improvement recommendations, files repaired, checks actually executed/results, and material coverage gaps. Keep recommendations distinct from confirmed defects and repaired-and-verified changes. A separate reviewer context provides an independent pass; if the builder and checker were the same context, say so. In a team, the coordinator accepts the integrated outcome; do not silently redefine acceptance criteria or mark the whole project complete.

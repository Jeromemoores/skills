# Task packets and ownership

Use the project's existing equivalent or this compact structure. Include only fields that affect execution; avoid copying the whole conversation or documentation corpus into every worker.

```text
Task ID / outcome:
Owner role / actual model when known:
Dependencies / ready conditions:
Read first: requirement, contract revision, relevant files, exact docs/sections
Allowed files / shared files assigned to this task:
Behavior and invariants to preserve:
Critical contract -> implementing owner/mechanism -> failure-case acceptance evidence:
Existing implementation/reuse candidates and relevant code-documentation contracts:
Acceptance checks / relevant known baseline failures:
Non-goals / decisions that must return to the coordinator:
Baseline: commit/worktree, or a precise file/change snapshot
Existing-repo integration: affected package/module and consumers, relevant baseline results, pending work to preserve
Expected return: changed files, behavior, executed checks/results, uncertainties
```

Shared contracts should specify relevant routes/schemas, error semantics, ownership/authorization, idempotency, and data invariants. Update the contract before parallel implementations diverge. When a contract changes, identify dependent tasks and communicate the new revision. A task packet must not imply that a dependency is complete when it is only planned.

For asynchronous or persistent shared state, specify the logical operation identity, owner/lifetime, state observers/notification, completion/cleanup authority, and supported recovery boundary where relevant. Assign integrated verification of cross-boundary guarantees to an owner. The reviewer should choose a relevant adversarial ordering or failure case independently rather than checking only the builder's selected examples. Evidence may be an existing equivalent test; do not add fields or tests for unrelated risks.

Suggested states are `queued`, `ready`, `implementing`, `ready-for-review`, `needs-changes`, `accepted`, and `blocked`. The coordinator updates the canonical ledger; builders and reviewers return reports instead of racing to rewrite it. Each blocking finding has an owner, expected evidence for resolution, and a disposition. Use existing task IDs rather than filing duplicates.

Separate worktrees or branches can isolate filesystem edits when supported. They do not eliminate integration work or prevent two agents from making incompatible changes. In a shared checkout, define non-overlapping file ownership and serialize migrations, shared configuration, manifests/lockfiles, and repairs. Never use a destructive reset to discard another worker's changes.

The reviewer receives the user-visible requirements and raw changes, not just the builder's interpretation. When practical, first inspect behavior independently, then compare the builder's claims. A reviewer who writes a fix should verify it against the original invariant and inspect the resulting diff. The coordinator performs final integration acceptance; if all roles ran in one context, report that limitation plainly.

Review handoffs should separate correctness findings from concrete function-design, reuse, and efficiency recommendations. Each worthwhile recommendation identifies the location, evidence, bounded change, expected benefit/tradeoffs, and verification. Track nonblocking improvements separately from acceptance defects; scheduling or suggesting them does not expand a bug-fix task into unrequested cleanup.

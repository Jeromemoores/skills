---
name: coordinate-project
description: "Plan and coordinate a requested multi-agent or mixed-model software workflow: maintain requirements, architecture, task ownership, implementation/review handoffs, and integrated acceptance evidence. Use when a planner should direct builders and reviewers; exclude simple solo edits and unrequested delegation."
---

# Coordinate Project

Keep the user's intent, scope, contracts, and completion criteria consistent across planning, implementation, and review. Use a stronger planning/review model and economical implementation models when the user has selected that mix and the runner supports it. Skills describe behavior; the runner controls actual model selection, permissions, and execution.

## Establish a shared plan

Use `dependency-docs` when installed for the affected project's dependency/version inventory and relevant cached references. Include important coverage gaps in task packets. Give manifest/lockfile changes one owner and have that owner rerun documentation preparation before dependent API implementation; the planner need not download every unrelated manual for each worker.

Inspect the project and existing task state before making a new plan. Reuse its established tracking system; for a portable local workflow, the coordinator owns concise plan/task/contract files. Do not create a competing board or impose a large planning ceremony on a small change.

For an existing repository, onboard the affected system before task assignment: actual applications/modules and versions, current architecture/decisions, entry points and consumers, compatible reuse candidates, pending work, and relevant baseline checks/failures. Plan an incremental integration into that system. Include affected contracts and any required migration/rollout compatibility in the task packets; do not default to a new scaffold, stack upgrade, or wholesale rewrite. Keep discovery proportional to the request and use available stack-specific existing-project guidance.

Record the outcome, non-goals, important requirements/invariants, acceptance evidence, and unresolved decisions. For consequential web architecture use a workload/capacity assessment through `plan-web-capacity` when available; for Unreal use the platform, lifecycle, asset, networking, and performance assessment in `plan-unreal-project` if installed. Otherwise apply the relevant criteria directly. Identify actual versions, maintainer references, and interface/data contracts before delegating code that depends on them. Ask the user only about material decisions that cannot be established from context; continue independent work in the meantime.

Turn high-impact guarantees into acceptance obligations before assigning dependent work: documented constraint, implementing mechanism/owner, and observable failure-case evidence. Include relevant operation identity, lifecycle/cleanup, notification, and recovery boundaries in shared contracts; do not leave a client/server retry guarantee owned by neither task. Keep this proportional to risk and reuse existing plan/contract records.

Divide the work into small verifiable tasks with dependency order and explicit ownership. Use [task handoffs](references/task-handoffs.md) for a compact packet that a focused implementer can execute without guessing. The coordinator owns changes to shared API/schema contracts, dependency manifests/lockfiles, migrations, and the task ledger, or assigns a single named owner. Scope ownership to the actual task, not a permanent ban on editing those files.

## Route work deliberately

Route a requested security assessment to `review-security`, affected web accessibility work to `review-accessibility`, and consequential persisted-data/reflected-asset transitions to `plan-safe-migrations` when available. Include relevant findings/compatibility obligations in the normal task packet; do not turn every task into three additional audits or treat a plan as authorization to execute production changes.

For an explicitly requested delegated workflow, use available agent tools to assign ready tasks. Pass only the relevant requirements, contracts, references, files, baseline, and checks. Delegate independent file sets in parallel; serialize overlapping edits and dependent tasks. Prefer a narrow implementation model for well-specified routine work. Keep ambiguous design, concurrency/data-integrity decisions, and difficult diagnosis with an appropriately capable role. Do not assume a model is adequate solely from its price or label.

Respect the user's selected models, available tools, and time/cost limits. If model routing or delegation is unavailable, perform sequential role passes or give manual handoffs; disclose that fallback rather than claiming separate agents or lower-cost execution occurred. A skill does not provision cloud services or bypass parent permissions.

Track each task's owner, dependencies, state, and current evidence. Builder completion means ready for review, not accepted. Inspect reports and the changed files; a worker's summary does not establish correctness. Update the plan when evidence or user steering changes a dependency or decision, then notify affected workers. Preserve completed useful work and do not let workers silently redefine requirements to simplify their tasks.

## Review, repair, and integrate

Assign review to a separate agent/context when available, supplying the same acceptance contract and a reproducible baseline. Use `review-and-repair-code` if installed, or require evidence-based findings and relevant verification directly. Grant one writer ownership of affected files before repairs; stop overlapping builder edits first. Builders may fix narrow findings, while complex or repeated failures should return to the reviewer/planner for diagnosis.

Keep repair cycles bounded. After two unsuccessful attempts at the same underlying issue, reassess the contract, reproduction, or implementation approach instead of repeating the same prompt. Escalate using the user's authorized model/cost options, or report the unresolved blocker. Do not declare a task accepted while material correctness findings or required checks remain unresolved.

Verify the integrated user journey after individual tasks pass. Check contract compatibility and run the appropriate combined checks; do not rerun every check after unrelated prose edits. When capacity validation is requested, use a representative authorized test environment and distinguish measured results from estimates. Never weaken tests or acceptance criteria to obtain a green status.

Have the reviewer challenge a consequential guarantee with a relevant failure/order/lifecycle case beyond the builder's success path. Accept cross-boundary claims using integrated evidence: backend deduplication alone does not prove frontend retry identity, and compilation alone does not prove callback lifetime safety. Keep unresolved material findings and missing required evidence visible even when build/lint/unit checks are green.

Report delivered behavior, substantive findings/fixes, actual checks/results, remaining limitations, and whether the requested role/model split was actually used. Keep status updates useful to the user and retain compact durable handoffs so another agent can resume.

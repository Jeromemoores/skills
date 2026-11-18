---
name: plan-safe-migrations
description: "Plan and rehearse compatible changes to databases, persisted APIs/data and Unreal save/reflected asset contracts in existing projects. Use for schema/data conversions, renamed persisted fields and rolling-version compatibility; exclude routine stateless edits and unrequested production execution or engine upgrades."
---

# Plan Safe Migrations

Make the existing data and active consumers part of the design before changing their representation. A successful fresh install or clean build does not prove an upgrade works.

## Establish the compatibility boundary

Inspect actual schema/serialization versions, migration history, readers/writers, deployment topology and representative data. Preserve pending work, real databases, saves and unsaved assets. Identify who must still read or write old/new formats and for how long. Distinguish a source rename from a persisted/reflected identity change. Use actual version evidence and maintainer documentation; current docs do not authorize upgrading the database, toolchain or engine.

Read [Web/data transitions](references/web-data.md) for databases and APIs, or [Unreal persistence](references/unreal-data.md) for saves and reflected assets. Use the relevant installed documentation/validation companions when available. Inspect existing migration mechanisms before adding another runner or helper.

## Produce a concrete transition

Describe the old/new representation, invariants, affected consumers, execution order and compatibility window. Use additive/expand-transition-contract steps when overlapping versions need them; a small offline conversion may justify a simpler plan. Identify irreversible information loss before the destructive step. Do not assume every change needs a distributed rollout or that a rollback script can restore discarded data.

Specify preconditions, expected volume/cost, relevant lock/downtime limits, progress/checkpoints, interruption/retry behavior, and the owner of each step. Explain how concurrent writers and duplicate retries preserve correctness. Keep required atomic operations intact when splitting functions. Check conversions for null/default semantics, identifiers, ranges/precision, time/encoding, uniqueness and references as applicable.

Define validation and recovery with the actual data model: counts plus meaningful invariants, converted values, relationships and application behavior. State what an application rollback can read after new writes, what a restore would lose, and when a forward correction is safer. A backup's existence is not a demonstrated restore procedure.

Include downstream usability in migration acceptance. Values admitted or preserved by the transition must work through the supported new readers, validators and affected operations, including any tokens or references those operations generate. Reconcile mismatched representation, length/range/precision and normalization limits explicitly; a permissive library parser is not the application's support policy. Test representative legacy/boundary values through the real consumer, and distinguish constructed unsupported imports from supported compatibility failures. Preserve required historical values when canonicalizing a transport token or reference.

## Rehearse within scope

For an implementation/rehearsal assignment, prepare scripts and exercise representative disposable copies before consequential execution. Include an existing older dataset/save, the intended upgrade path, relevant supported reader/writer combinations, interruption/retry and recovery. Test the proposed failure boundary, not just an empty target schema or freshly created save. Keep source and target fingerprints/evidence sufficient to assess preservation without exposing personal data. For review-only work or an unidentified database/format, return the concrete transition and missing evidence; do not invent an execution target to satisfy a rehearsal step.

A planning request permits local preparation/rehearsal with disposable fixtures; it does not by itself authorize production changes, real save overwrites, destructive asset fix-ups or public deployment. Reuse execution authorization already provided and prepare a concrete plan before asking about genuinely missing scope. Do not impose another approval gate on ordinary authorized reversible implementation.

Return the transition, compatibility matrix, material risks/limits, exact rehearsal results and remaining execution requirements. Honor review-only scope and integrate with the existing task ledger. Do not mark an unexecuted migration, restore, cook/package or runtime check as complete.

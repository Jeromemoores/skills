---
name: review-security
description: "Review affected web/service or Unreal code for exploitable trust-boundary failures, with maintainer/standards evidence and scoped reproductions. Use for security reviews or consequential authorization, input, secrets, upload, deserialization and network-authority changes; exclude cosmetic edits and unsupported certification claims."
---

# Review Security

Trace untrusted input to the operation it can influence. Establish a reachable failure and its impact before calling something a vulnerability. This skill supplies focused security analysis; it does not change task permissions or establish that a whole application is secure.

## Establish scope and evidence

Read the actual diff or requested behavior, applicable instructions, resolved dependencies, deployment/engine configuration and relevant tests. Preserve pending work. Identify the caller, trust boundary, authoritative owner, protected resource and expected access rule. Distinguish a local synthetic prototype from a deployed authenticated service; an explicitly test-only identity selector is not automatically a newly discovered authentication bypass.

Use the applicable stack/documentation skill and matching maintainer references before consequential API claims. Reuse identifiable cached docs; consult focused official sources for gaps. `dependency-docs`, if installed, helps establish versions and source coverage. A dependency audit result is evidence about the reported dependency/version, not proof of an exploitable application path. Report incomplete source/runtime access.

Read [Web/service boundaries](references/web-services.md) for web work or [Unreal boundaries](references/unreal.md) for engine/game work. ASVS supplies web requirements; it is not a game-networking specification. Select only the boundaries affected by the task.

## Verify a finding

Follow the complete path from attacker-controlled value through validation, authorization and side effects. Check the authoritative server or storage rule, not only a UI restriction. Establish prerequisites and distinguish missing defense in depth from a reachable bypass. Search existing middleware/helpers and downstream checks before proposing another layer.

For a substantive issue, record location, controlled input, required access, trigger, expected/observed result, impact, and the bounded correction. A plausible hypothesis with missing evidence stays a hypothesis. Redact secret values and personal data from artifacts; identify the configuration field or secret location instead. Do not upload project material to an external scanner merely because its URL appears in documentation.

Use local disposable fixtures or the already-authorized environment for focused negative tests. Ordinary code review does not authorize external exploitation, production load, real account abuse, notifications or data changes. Preparing a concrete local reproduction can proceed within the existing task. Do not add a new approval gate to normal authorized fixes.

## Recommend or repair

Honor review-only scope. When fixes are authorized, preserve public contracts and address the actual trust boundary with existing compatible mechanisms. Avoid invented cryptography, speculative sanitizers and unrelated rewrites. Keep validation, authorization and atomic state changes connected; splitting functions must not separate a checked condition from the protected operation.

Use `review-and-repair-code` when available for findings and repair reporting. If the user wants preview/Accept/Reject changes, publish through `propose-code-review` when installed instead of editing source. Add a focused regression that fails for the demonstrated attack path and preserves legitimate behavior. Record what ran, what remains untested, the sources actually consulted, and any relevant residual risk. Passing checks and an ASVS reference do not establish certification or absence of vulnerabilities.

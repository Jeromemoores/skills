---
name: plan-web-capacity
description: "Assess web application architecture, likely bottlenecks, capacity assumptions, and growth options before a new build or consequential architecture change. Use for scalability questions, traffic targets, deployment/database choices, and migration planning; exclude small UI fixes and claims of measured capacity without testing."
---

# Plan Web Capacity

Produce a concise, evidence-based architecture assessment before committing a substantial web build to a topology. Explain what is known, what is assumed, what could limit growth, and which measurements would validate the recommendation. A framework name and a total user count cannot establish capacity.

## Establish the workload and constraints

Read applicable project instructions, architecture/deployment files, relevant manifests, and existing performance evidence. Use available context before asking questions. Clarify missing information only when it materially changes the recommendation; otherwise show clearly labeled scenarios and continue useful design work.

Distinguish registered users, monthly/daily active users, concurrent sessions/connections, requests per second, and in-flight work. Establish the busiest user journeys, read/write mix, work per request, payload sizes, cacheability and freshness, real-time connections/message rates, background work, data volume/growth, and expected bursts. Include relevant regions and client/browser constraints.

Identify latency and error-rate objectives for important journeys, the availability/recovery requirements that matter to the product, cost constraints, and the team's deployment/operations capacity. Do not invent universal targets. For ambiguous "10 million users," explain which population/time window matters and present an illustrative workload conversion with units. Use [workload estimates](references/workload-estimates.md) for formulas and their limits.

## Assess the actual system

Trace representative requests through the CDN/static assets, rendering/API tier, database/cache, queues/workers, and external dependencies. Separate browser performance from backend throughput. Identify relevant limits such as query plans/indexes, write contention, connection pools, state stored in process memory/local disks, cache invalidation, large payloads, rendering cost, fan-out, and provider quotas. Inspect only components implicated by the workload.

For an existing application, establish the current topology, workload evidence, objectives, known incidents/bottlenecks, and deployment/data compatibility before proposing a replacement. Compare the smallest useful change with retaining the current design; reuse existing capacity evidence only within its recorded conditions. Include affected consumers, migration/backfill/rollout and recovery considerations when the recommendation changes persistent data or deployment contracts. Do not turn onboarding or an unmeasured concern into an unsolicited rewrite.

Consult first-party documentation for the actual framework, database, runtime, and hosting topology. Use existing local version-matched docs when available; otherwise open the relevant official pages. Verify provider-specific limits and costs from current sources when needed. Classify evidence as **documented constraint**, **measured behavior**, **modeled estimate**, or **unknown**. Vendor benchmarks describe their conditions and do not prove this application's capacity.

Recommend the simplest architecture supported by the requirements and evidence. Explain real tradeoffs when alternatives matter. Give a path to add replicas, caching, asynchronous work, partitioning, or other changes only when an identified demand/bottleneck justifies them. Account for shared state, correctness, connection budgets, and cache coordination before assuming another replica increases usable capacity. Avoid introducing microservices, queues, sharding, Kubernetes, or a rewrite solely because a large user number was mentioned.

## Present the assessment before implementation

Scale detail to the decision. For a new project or consequential architecture change, surface the assessment to the user before implementing the affected architecture. Include:

- The target workload, quality objectives, and important assumptions or unknowns.
- The proposed request/data flow and why it fits; use a compact diagram when it clarifies the design.
- Likely bottlenecks and documented limits, with supporting references.
- What to build now, what to defer, and observable triggers for revisiting those choices. Derive triggers from the workload, objectives, and measurements rather than arbitrary user-count thresholds.
- The validation plan and which claims remain unmeasured. State a capacity range only when the model or measurements support it, including its conditions.

Do not impose an approval gate on ordinary authorized implementation. Ask for a decision when a materially unresolved tradeoff changes cost, correctness, or product behavior. Save an architecture document only when requested or consistent with the project's established design-document workflow. Reuse an existing assessment and revisit it when workload, topology, or requirements change; do not repeat it for every small edit.

Use a measured-capacity workflow when validation is requested. If `validate-web-capacity` is installed, it can guide that work; the assessment remains usable without it. Never report "supports 10 million users" as a guarantee based on framework selection or arithmetic alone.

## Primary references

Open relevant material, not the entire list:

- [Google SRE: implementing objectives](https://sre.google/workbook/implementing-slos/) for user-relevant reliability targets.
- [Google SRE: monitoring](https://sre.google/sre-book/monitoring-distributed-systems/) for latency, traffic, errors, and saturation.
- [Google SRE: overload](https://sre.google/sre-book/handling-overload/) for bounded work and degraded service under overload.
- [Next.js self-hosting](https://nextjs.org/docs/app/guides/self-hosting) for the installed version's multi-instance/cache behavior.
- [Go diagnostics](https://go.dev/doc/diagnostics) for profiling and tracing evidence.

Framework-specific guidance must match the installed version. These links are references, not a claim that all linked material is cached locally.

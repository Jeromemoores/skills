---
name: validate-web-capacity
description: "Design and, within authorized scope, run representative web application performance tests to measure capacity, bottlenecks, and growth limits against latency/error objectives. Use for load tests, performance validation, and capacity evidence; exclude ordinary unit tests and unsupported user-count guarantees."
---

# Validate Web Capacity

Turn a workload target or architecture assessment into reproducible capacity evidence. If there is no usable workload/objective definition, inspect the project and establish one before interpreting throughput. `plan-web-capacity` can help if available; this skill does not require it.

## Match the test to the question

Use existing test/performance tooling where suitable and consult its official documentation for configuration semantics. Choose tools based on required browser, HTTP, WebSocket, or worker behavior rather than a fixed preference. A Go microbenchmark, cached static endpoint, and representative end-to-end user journey answer different questions.

Establish the exact environment, software/configuration revision, instance counts/sizes, representative data distribution/cardinality, cache conditions, request mix, authentication, external dependencies, and target latency/error objectives. Distinguish intended arrival rate, attempted/sent work, completed work, and successful work meeting objectives. Keep user think time, actions/second, requests/action, and active connections explicit.

For changes to an existing application, reuse the established performance fixtures/tooling where suitable and capture a comparable baseline when feasible. Separate existing correctness/performance failures from regressions. Hold relevant workload, data/cache, environment, and measurement conditions equivalent for before/after claims; label unavailable baselines and confounding changes. Inspect scripts/target configuration before execution, and do not reset real data or run production migrations as incidental test setup.

For offered-throughput questions, use an appropriate arrival-rate model; a closed fixed-user test can lower its offered request rate as responses slow. Account for dropped/unscheduled work and verify the load generator is not saturated. For session/concurrency questions, model sessions explicitly and also report the actual resulting request/message rate. Percentiles must cover the relevant journey/time window; do not average percentiles across endpoints or runs.

## Prepare bounded, meaningful execution

Use the user's authorized target and session constraints. Prepare scripts, data, and a concrete test plan before asking about genuinely missing execution scope. Local functional/smoke checks can proceed within ordinary task authorization. A general request to assess scalability does not authorize stressing production, third-party endpoints, sending real notifications/payments, or incurring material cloud charges. Reuse explicit authorization already given. For a bounded authorized run, state duration, load limits, side effects, and stop conditions proportional to the environment and impact.

Start with a low-load smoke test to verify responses and business assertions. Add only the expected-load, stepped-load, burst, or sustained test needed to resolve the question. Monitor application and load-generator health. Use disposable or authorized test data and stub side-effecting integrations when appropriate; report the representativeness tradeoff of stubs. Test failure/degraded-capacity scenarios only when relevant and authorized.

Correlate client latency, throughput, errors, and dropped work with server CPU/memory, database waits/query behavior, connection pools, queue depth/age, cache behavior, and dependency latency as relevant. Distinguish time spent waiting from CPU execution. Use profiling/tracing to test the suspected bottleneck rather than guessing a rewrite. Change a justified factor, then compare an equivalent workload when additional measurements are needed.

## Report exactly what was established

Give the reproducible command/configuration, environment and workload conditions, duration, requested and achieved load, latency distribution, errors/correctness failures, saturation evidence, and relevant observations. State the tested operating range that met objectives and where results failed or were inconclusive. An unreached limit is not unlimited capacity; one endpoint or a brief run does not establish whole-application capacity or long-duration reliability.

Clearly separate measurements, hypotheses, and extrapolations. Do not convert results into a total-user ceiling without an explicit workload model. Do not multiply single-replica results to promise multi-replica capacity. If tests were prepared but not executed, say so and identify the required environment or authorization. Save reusable scripts/results in the project's established locations without exposing credentials or personal data.

## Primary references

Read only relevant material and match the selected tool's version:

- [Grafana k6 test types](https://grafana.com/docs/k6/latest/testing-guides/test-types/) for smoke, expected-load, stress, spike, and sustained tests.
- [Grafana k6 open and closed models](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/) for offered-load interpretation. These principles do not require choosing k6.
- [Google SRE monitoring](https://sre.google/sre-book/monitoring-distributed-systems/) for latency, traffic, errors, and saturation.
- [Go diagnostics](https://go.dev/doc/diagnostics) for relevant profiling/tracing tools.

Use maintainer documentation for the actual runtime, database, hosting, and tooling. Links are not a claim that their contents have been read or cached.

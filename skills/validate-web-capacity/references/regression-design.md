# Regression checks around capacity measurements

Establish relevant functional correctness before interpreting a speed result. Define the operation's observable contract, failure trigger and authoritative oracle; reuse existing focused tests. Keep the capacity skill scoped to the performance question rather than turning every UI edit into a load test.

For an affected API/storage path, separate valid successful work from expected rejection, transport errors and partial/unknown outcomes. Assert inventory, ownership, durability, uniqueness or other actual business invariants when relevant. Cheap rejected/cached responses must not replace the operation whose performance is being measured.

Use a unit test for deterministic logic, integration for database/transaction/transport behavior, and a browser journey for affected rendered state, input or lifecycle claims. A browser mock can isolate UI behavior; it cannot prove a real server commit or persistent recovery. Select an appropriate real boundary for that claim.

For an asynchronous regression, use deterministic interception/barriers to control the relevant ordering and inspect authoritative state afterward. Keep workloads, data distribution, cache state and code/build versions comparable for before/after performance claims. Verify the running build matches the reviewed source; a green old artifact does not validate today's edits.

Record intended assertions, fixture isolation, baseline failure/correction evidence and untested paths. Report representative measurement limits separately from functional correctness. Do not add a speed benchmark to justify a readability-only change or infer capacity from passing regression tests.

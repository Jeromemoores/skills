# Workload estimates with explicit assumptions

Use calculations to expose assumptions and size tests, not to manufacture a capacity rating. Keep units and averaging windows visible. Present low/base/high scenarios only when uncertainty justifies them; do not fabricate precision.

- **Mean request rate:** requests over a period / seconds in that period. Ten million page views per day is about 116 page views/second on average. A page view can generate multiple requests; this says nothing by itself about peak demand or expensive operations.
- **Interaction-driven peak:** concurrent active users x actions/user/second x requests/action. Ten thousand active users each issuing one request/second produce 10,000 requests/second. Open idle connections and total registered accounts are different quantities.
- **Origin demand after caching:** total request rate x (1 - cacheable fraction x hit rate for the cacheable subset). Check personalization, authorization, freshness, invalidation, and cold-cache bursts before assuming a high hit rate. Static asset/CDN hits do not measure API capacity.
- **Database operations:** sum across request classes of origin request rate x operations/request. Include background jobs and read/write differences. Operations with different query plans, row counts, and contention are not interchangeable units of resource cost.
- **Mean in-flight work:** arrival rate x mean time in system at a consistent boundary under stable conditions (Little's law). Do not substitute p95 latency for the mean, equate this with total users, or use it to assume throughput remains stable after saturation.
- **Raw data growth:** writes/second x bytes/write x seconds. Estimate indexes, replication, retention, logs, backups, and storage headroom separately. Traffic averages alone do not establish disk I/O or database capacity.
- **Initial replica estimate:** peak demand / measured safe throughput per replica under the stated objectives, rounded up. This is only a starting point: validate shared database limits, inter-instance state, routing, autoscaling lag, failures, and the actual multi-replica system. Do not extrapolate linear gains from an unloaded single-instance benchmark.

When inputs are missing, state them as unknowns or explicitly hypothetical values. Use measured figures from a representative environment before presenting a tested capacity. State the hardware, data size/distribution, traffic mix, software versions, cache conditions, test duration, and latency/error objectives that the result applies to.

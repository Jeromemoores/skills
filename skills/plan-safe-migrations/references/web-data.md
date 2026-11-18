# Web, service and database transitions

Establish the actual database/driver, migration runner and deployment versions. Read the relevant database DDL/locking/transaction documentation and runner behavior, including partial-failure recording. [SQLite ALTER TABLE](https://www.sqlite.org/lang_altertable.html) and [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html) are entry points; choose the project's version. Do not assume identical transactional DDL, lock duration or online behavior across databases/statements.

Map affected rows, defaults/nulls, constraints, indexes, foreign keys, triggers and dependent queries. Preserve application invariants during backfills and concurrent writes. For a large transition, justify batching/checkpointing, retry idempotency, progress validation and the point when old fields can actually be removed. Keep single-transaction changes atomic where required; adding helper functions is not permission to split a transaction.

For an API/event format, identify deployed producers/consumers and persisted messages. Document field meaning, optional/default behavior and compatibility while versions overlap. Renaming a JSON key can be a persisted contract change even if server and local frontend compile together. Rehearse old clients/messages and new code against older records as relevant. Do not invent a rolling-upgrade requirement when the product permits a bounded offline upgrade.

Recovery must account for post-migration writes and external consumers. A down migration that drops newly collected values is information loss, not a safe reversal. Test realistic rollback/restore or a forward repair on copies, and state the recovery point and unavailable evidence.

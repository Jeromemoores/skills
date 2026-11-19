# Web, service and database transitions

Establish the actual database/driver, migration runner and deployment versions. Read the relevant database DDL/locking/transaction documentation and runner behavior, including partial-failure recording. [SQLite ALTER TABLE](https://www.sqlite.org/lang_altertable.html) and [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html) are entry points; choose the project's version. Do not assume identical transactional DDL, lock duration or online behavior across databases/statements.

Map affected rows, defaults/nulls, constraints, indexes, foreign keys, triggers and dependent queries. Preserve application invariants during backfills and concurrent writes. For a large transition, justify batching/checkpointing, retry idempotency, progress validation and the point when old fields can actually be removed. Keep single-transaction changes atomic where required; adding helper functions is not permission to split a transaction.

For an API/event format, identify deployed producers/consumers and persisted messages. Document field meaning, optional/default behavior and compatibility while versions overlap. Renaming a JSON key can be a persisted contract change even if server and local frontend compile together. Rehearse old clients/messages and new code against older records as relevant. Do not invent a rolling-upgrade requirement when the product permits a bounded offline upgrade.

Recovery must account for post-migration writes and external consumers. A down migration that drops newly collected values is information loss, not a safe reversal. Test realistic rollback/restore or a forward repair on copies, and state the recovery point and unavailable evidence.

## Commonly missed cases

These are frequent sources of real defects. Treat each as a candidate to check against the matching documentation for the project's version, not as a rule to apply blindly or a complete list.

- **Blocking DDL:** some statements rewrite the table or hold a lock that blocks reads or writes for the duration, and behavior differs by database, version and statement. A DDL statement waiting behind a long transaction can also block every query queued behind it; a lock timeout bounds that.
- **Index builds:** PostgreSQL's `CREATE INDEX CONCURRENTLY` avoids blocking writes but cannot run inside a transaction and can leave an invalid index on failure. Check how the migration runner wraps statements.
- **Constraints on existing data:** preflight violations and validation/scan cost for unique indexes, foreign keys and `NOT NULL`. PostgreSQL offers staged validation for supported constraint types/versions; do not assume `NOT VALID` applies to every constraint. [ALTER TABLE reference](https://www.postgresql.org/docs/current/sql-altertable.html)
- **SQLite:** `ALTER TABLE` supports a limited set of changes. Others need the documented create-copy-rename procedure, with attention to foreign-key enforcement, indexes, triggers and views.
- **Renames during overlapping deployments:** if old/new application versions must coexist, design an expand/transition/contract sequence with compatible readers/writers and a safe backfill. Dual writing is one option requiring consistency handling, not a requirement for a permitted offline migration.
- **Backfills:** one large `UPDATE` holds locks and bloats logs. Batch by key range, make each batch idempotent, and handle rows written while the backfill runs.
- **Order with deploys:** the schema must work with the previous application version until that version is gone, and the new application must tolerate the old schema if it can start first.
- **Type and encoding changes:** narrowing a column, changing a time zone convention or changing text collation can truncate, shift or reorder existing values without an error.
- **Enumerations and status values:** readers that reject unknown values break when a writer starts emitting a new one. Deploy tolerant readers first.

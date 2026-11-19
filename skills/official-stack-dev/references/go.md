# Go documentation route

Use [Go documentation](https://go.dev/doc/), the [language specification](https://go.dev/ref/spec), [standard library reference](https://pkg.go.dev/std), and [release notes](https://go.dev/doc/devel/release) for the actual toolchain. Check when a symbol or language feature was introduced; the current specification and package pages may describe a newer release.

For a specific task:

- Installed package behavior: use `go doc` for the exact package/symbol. For a dependency, use the selected module version's package documentation and upstream repository; distinguish third-party packages from the standard library and Go team's modules.
- Modules/toolchain: consult the [modules reference](https://go.dev/ref/mod) and [toolchain documentation](https://go.dev/doc/toolchain). Avoid version-changing commands merely to inspect a project.
- Services: consult the exact APIs under [net/http](https://pkg.go.dev/net/http), [context](https://pkg.go.dev/context), and [database/sql](https://pkg.go.dev/database/sql) as applicable. Resolve cancellation, timeouts, resource closure, and error handling for the operation being changed.
- Concurrency: check synchronization ownership and goroutine exit paths. Use the [memory model](https://go.dev/ref/mem) for synchronization claims and [race detector guidance](https://go.dev/doc/articles/race_detector) when race testing is warranted and supported.

[Effective Go](https://go.dev/doc/effective_go) supports core idioms, but its own notice says it is not actively updated and omits newer language/ecosystem features. Pair it with current, version-relevant references.

Format changed Go files with the project's formatter (normally `gofmt`). Run appropriately scoped existing tests and static checks such as `go test` and `go vet`; broaden scope when the change's impact warrants it. Run race tests when concurrency changes justify them. A passing race run covers exercised paths rather than proving all possible executions race-free.

## Commonly missed cases

These are frequent sources of real defects. Treat each as a candidate to check against the matching documentation for the project's version, not as a rule to apply blindly or a complete list.

- **Timeouts:** a zero `http.Client.Timeout` supplies no overall request deadline; request contexts and transport phase timeouts are separate. `http.Server` supplies no read/write timeout by default. Configure appropriate limits deliberately for the operation.
- **Response bodies:** close the body on every path, including errors after a successful request. Connection reuse depends on the body being read to completion.
- **Context:** derive from the incoming request's context, `defer cancel()`, and pass it to the context-aware calls (`NewRequestWithContext`, `QueryContext`, `ExecContext`). A context that is created but never passed cancels nothing.
- **Goroutine exit:** give long-lived work an exit path. A blocking send with no remaining receiver or cancellation/select path can leak the goroutine.
- **Loop variables:** per-iteration loop variables arrived in Go 1.22 and follow the `go` directive in `go.mod`. In older modules, closures and goroutines started in a loop share one variable.
- **`defer` in loops:** deferred calls run when the function returns, not at the end of each iteration; files and rows opened in a loop stay open.
- **Errors:** use `%w` when wrapping must preserve classification, and `errors.Is`/`errors.As` when checking through wrappers. Direct sentinel equality can be correct for a known unwrapped error. A typed nil pointer stored in an interface is not a nil interface.
- **Shared data:** concurrent map writes are a fatal runtime error, not a recoverable panic. `append` can write into a backing array another slice still shares.
- **database/sql:** `*sql.DB` is a connection pool. Close `Rows` and check `rows.Err()` after iteration. `defer tx.Rollback()` after `Begin` is safe after a successful `Commit`. Pool limits must fit the database's connection limit across all instances.
- **JSON:** only exported fields are encoded. Unknown fields are ignored unless disallowed. `omitempty` drops zero values a client may need. Integers beyond 2^53 lose precision in JavaScript clients.
- **Shutdown:** `Server.Shutdown` drains ordinary requests but does not wait for hijacked connections such as WebSockets.

# Go documentation route

Use [Go documentation](https://go.dev/doc/), the [language specification](https://go.dev/ref/spec), [standard library reference](https://pkg.go.dev/std), and [release notes](https://go.dev/doc/devel/release) for the actual toolchain. Check when a symbol or language feature was introduced; the current specification and package pages may describe a newer release.

For a specific task:

- Installed package behavior: use `go doc` for the exact package/symbol. For a dependency, use the selected module version's package documentation and upstream repository; distinguish third-party packages from the standard library and Go team's modules.
- Modules/toolchain: consult the [modules reference](https://go.dev/ref/mod) and [toolchain documentation](https://go.dev/doc/toolchain). Avoid version-changing commands merely to inspect a project.
- Services: consult the exact APIs under [net/http](https://pkg.go.dev/net/http), [context](https://pkg.go.dev/context), and [database/sql](https://pkg.go.dev/database/sql) as applicable. Resolve cancellation, timeouts, resource closure, and error handling for the operation being changed.
- Concurrency: check synchronization ownership and goroutine exit paths. Use the [memory model](https://go.dev/ref/mem) for synchronization claims and [race detector guidance](https://go.dev/doc/articles/race_detector) when race testing is warranted and supported.

[Effective Go](https://go.dev/doc/effective_go) supports core idioms, but its own notice says it is not actively updated and omits newer language/ecosystem features. Pair it with current, version-relevant references.

Format changed Go files with the project's formatter (normally `gofmt`). Run appropriately scoped existing tests and static checks such as `go test` and `go vet`; broaden scope when the change's impact warrants it. Run race tests when concurrency changes justify them. A passing race run covers exercised paths rather than proving all possible executions race-free.

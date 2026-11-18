# Cohesive functions, useful documentation, and reuse

Apply these principles to changed code in its actual language/framework. They are design criteria, not a line-count quota or a demand to rewrite the whole project.

## One clear responsibility

Give a function a coherent purpose and a name that describes its observable behavior. Separate calculations/queries, state-changing operations, and presentation when they represent different responsibilities. A function named like a reader should not secretly persist changes, show a dialog, or mutate unrelated application state.

Keep calculations and formatting pure where practical. Make mutations, network/storage operations, and other effects visible at clear boundaries. An event handler or application service can intentionally coordinate several steps for one user action; do not fragment it into meaningless wrappers merely to make every function call one other function. A command may legitimately return a result or error. Database read-modify-write logic may need one atomic transaction; splitting it into separate unprotected reads/writes would harm correctness.

In React, follow documented render purity and put relevant state changes/effects in the appropriate event/lifecycle boundaries. In Go, use idiomatic error returns and resource ownership; do not transplant language-specific book prescriptions such as exception-based error handling. Preserve transaction, cancellation, and cleanup guarantees when extracting functions.

Prefer clear names, explicit inputs/outputs, straightforward control flow, and a consistent level of detail. Extract a helper when it creates a useful boundary, reusable concept, or independently meaningful test surface. Avoid speculative generalization, boolean-mode helpers that conceal unrelated behaviors, and layers that add navigation without clarifying the operation.

## Document the contract and the reason

Follow the project's public API/package conventions, including [Go doc comments](https://go.dev/doc/comment) and appropriate JSDoc/TSDoc conventions when used by the project. Document externally consumed APIs and non-obvious internal contracts: purpose, effects, input constraints, meaningful results/errors, invariants, concurrency/transaction behavior, and resource ownership as relevant. Type declarations already carry ordinary type information; do not duplicate them in prose mechanically.

Use comments for reasons, constraints, tradeoffs, and surprising behavior, not a narration of obvious statements. Explain a workaround with its actual rationale and supporting reference when useful. Keep comments, examples, and API docs synchronized when behavior changes. Do not mask unclear code with a long comment or require a comment for every trivial private helper. Avoid stale TODOs and comments claiming guarantees the implementation/tests do not establish.

## Search before adding; prove before deleting

Before adding a production helper/module, look for the same domain operation, relevant types, routes, and existing utilities. Search by behavior and data flow as well as names. Compare error handling, side effects, ownership, runtime constraints, and dependencies before reusing a candidate. Use `audit-code-reuse` when available for a substantial reuse/dead-code question.

Reuse or extend a compatible implementation instead of copying it. When similar code embodies distinct rules or would create an inappropriate dependency/coupling, keep it separate and explain the reason where it matters. Shared abstractions must preserve semantics, not just remove visually similar lines.

An absent text reference does not prove a function is unused. Check call/import graphs, framework entry points, exports, tests, generated code, build variants, and dynamic consumers before removing it. Keep public/external contracts unless deprecation/removal is within scope and justified. Do not equate a passing build with a proof of reachability across every supported configuration.

## Background references

The user preference aligns with ideas discussed in Robert C. Martin's [Clean Code](https://www.pearson.com/en-us/subject-catalog/p/clean-code-a-handbook-of-agile-software-craftsmanship-2nd-edition/P200000013239/9780135398579) and [command-query separation](https://martinfowler.com/bliki/CommandQuerySeparation.html). This reference provides original project guidance rather than copying the book or treating its advice as a language-independent specification. Use documented framework contracts and demonstrated behavior to resolve concrete decisions.

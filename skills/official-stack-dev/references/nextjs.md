# Next.js documentation route

Start at [Next.js Docs](https://nextjs.org/docs). Select documentation for the installed version and the actual router: [App Router](https://nextjs.org/docs/app) or [Pages Router](https://nextjs.org/docs/pages). Projects can use both; inspect the route being changed.

Use the relevant version's navigation to find these topics; the direct links below point to current documentation and may move:

- Rendering boundaries: [Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components). Determine what runs on the server, what needs browser interactivity, what crosses the boundary, and where secrets are read.
- Data freshness: [Caching](https://nextjs.org/docs/app/getting-started/caching). Verify fetching, cache scope, invalidation, request-specific data, and configuration against this project's version; caching defaults and APIs can change.
- HTTP endpoints: [Route Handlers](https://nextjs.org/docs/app/getting-started/route-handlers) for App Router, or the Pages Router reference for API Routes. Verify method, request/response, and runtime requirements.
- Version changes: [Upgrading](https://nextjs.org/docs/app/guides/upgrading) and the matching release/migration guide before changing async request APIs, caching configuration, middleware/proxy conventions, or runtime assumptions.

Check loading/error behavior and authorization where the change touches them. Choose an existing Go endpoint, a Route Handler, or a server mutation based on the application's architecture and request contract; do not duplicate backend logic merely because Next.js supports it.

## Commonly missed cases

These are frequent sources of real defects. Treat each as a candidate to check against the matching documentation for the project's version, not as a rule to apply blindly or a complete list.

- **Remotely callable Server Actions and Route Handlers are trust boundaries.** Validate inputs and enforce the endpoint's required authentication/authorization at the operation. Intentionally public endpoints need their own contract; hiding a calling control provides no access check.
- **Props to Client Components are sent to the browser.** Pass only the fields the UI needs, never a whole record containing secrets. Only serializable values cross the boundary.
- **Environment variables:** ordinary direct `NEXT_PUBLIC_` references are exposed/inlined at build time and need a rebuild to change. The prefix is not a secrecy barrier: config, props or responses can expose other values too. Inspect the actual bundle/data path. [Environment-variable guide](https://nextjs.org/docs/app/guides/environment-variables)
- **`redirect()` and `notFound()` work by throwing.** A surrounding `try`/`catch` swallows them.
- **Caching defaults changed between major versions** (fetch, GET Route Handlers, client router cache). Establish the installed version before reasoning about stale data, and revalidate the affected path or tag after a mutation.
- **Request APIs** (`cookies`, `headers`, `params`, `searchParams`) became asynchronous in newer majors. Check the installed version's signature.
- **Accidentally static routes:** a page that reads no request-specific data can be rendered once at build time and served to everyone. Check the build output's route types when data must be per-request or per-user.
- **Per-process memory:** module-level caches, rate limiters and counters are not shared across instances or serverless invocations.
- **`'use client'` marks a boundary, not one file.** Everything it imports joins the client bundle. Keep the boundary low in the tree and keep server-only modules out of it.
- **Middleware is not the only authorization layer.** Enforce access again where the data is read or changed.

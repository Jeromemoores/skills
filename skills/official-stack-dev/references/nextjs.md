# Next.js documentation route

Start at [Next.js Docs](https://nextjs.org/docs). Select documentation for the installed version and the actual router: [App Router](https://nextjs.org/docs/app) or [Pages Router](https://nextjs.org/docs/pages). Projects can use both; inspect the route being changed.

Use the relevant version's navigation to find these topics; the direct links below point to current documentation and may move:

- Rendering boundaries: [Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components). Determine what runs on the server, what needs browser interactivity, what crosses the boundary, and where secrets are read.
- Data freshness: [Caching](https://nextjs.org/docs/app/getting-started/caching). Verify fetching, cache scope, invalidation, request-specific data, and configuration against this project's version; caching defaults and APIs can change.
- HTTP endpoints: [Route Handlers](https://nextjs.org/docs/app/getting-started/route-handlers) for App Router, or the Pages Router reference for API Routes. Verify method, request/response, and runtime requirements.
- Version changes: [Upgrading](https://nextjs.org/docs/app/guides/upgrading) and the matching release/migration guide before changing async request APIs, caching configuration, middleware/proxy conventions, or runtime assumptions.

Check loading/error behavior and authorization where the change touches them. Choose an existing Go endpoint, a Route Handler, or a server mutation based on the application's architecture and request contract; do not duplicate backend logic merely because Next.js supports it.

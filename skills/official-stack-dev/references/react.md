# React documentation route

Start at [Learn](https://react.dev/learn), [API Reference](https://react.dev/reference/react), or [React versions](https://react.dev/versions). Use the version archive where needed; do not assume the current reference applies to an older project.

For the specific change, resolve these questions using the relevant pages:

- Components and Hooks: check [Rules of React](https://react.dev/reference/rules) and the exact Hook/API reference, including documented exceptions and version availability.
- State and effects: check [Choosing the State Structure](https://react.dev/learn/choosing-the-state-structure) and [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect). Determine whether the work belongs in rendering, an event handler, or external synchronization before introducing an effect.
- Integration: use [React DOM references](https://react.dev/reference/react-dom) for browser APIs and the framework's docs for framework-owned rendering and data loading.

Check purity, mutation, state ownership, dependencies, and cleanup when relevant to the bug. Do not introduce memoization, a compiler setting, or a state library merely because an example uses it. Verify availability and project configuration first.

For external mutable state, read the actual [useSyncExternalStore contract](https://react.dev/reference/react/useSyncExternalStore). Trace who writes the value, who notifies subscribers, and who unsubscribes. A no-op subscription cannot keep a changing value reactive; hydration-compatible reads alone do not establish synchronization. Verify snapshot stability and server/client snapshot behavior as applicable.

For browser storage, check [storage event semantics](https://developer.mozilla.org/en-US/docs/Web/API/Window/storage_event): native events do not notify the document that performed the write, and session storage is not shared across ordinary tabs. Choose a coherent state owner and notification mechanism for the relevant readers; avoid independent storage/React/ref copies that silently diverge. Follow [Asynchronous operation contracts](async-operations.md) for pending requests, remounts, and recovery.

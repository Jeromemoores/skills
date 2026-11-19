# React documentation route

Start at [Learn](https://react.dev/learn), [API Reference](https://react.dev/reference/react), or [React versions](https://react.dev/versions). Use the version archive where needed; do not assume the current reference applies to an older project.

For the specific change, resolve these questions using the relevant pages:

- Components and Hooks: check [Rules of React](https://react.dev/reference/rules) and the exact Hook/API reference, including documented exceptions and version availability.
- State and effects: check [Choosing the State Structure](https://react.dev/learn/choosing-the-state-structure) and [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect). Determine whether the work belongs in rendering, an event handler, or external synchronization before introducing an effect.
- Integration: use [React DOM references](https://react.dev/reference/react-dom) for browser APIs and the framework's docs for framework-owned rendering and data loading.

Check purity, mutation, state ownership, dependencies, and cleanup when relevant to the bug. Do not introduce memoization, a compiler setting, or a state library merely because an example uses it. Verify availability and project configuration first.

For external mutable state, read the actual [useSyncExternalStore contract](https://react.dev/reference/react/useSyncExternalStore). Trace who writes the value, who notifies subscribers, and who unsubscribes. A no-op subscription cannot keep a changing value reactive; hydration-compatible reads alone do not establish synchronization. Verify snapshot stability and server/client snapshot behavior as applicable.

For browser storage, check [storage event semantics](https://developer.mozilla.org/en-US/docs/Web/API/Window/storage_event): native events do not notify the document that performed the write, and session storage is not shared across ordinary tabs. Choose a coherent state owner and notification mechanism for the relevant readers; avoid independent storage/React/ref copies that silently diverge. Follow [Asynchronous operation contracts](async-operations.md) for pending requests, remounts, and recovery.

## Commonly missed cases

These are frequent sources of real defects. Treat each as a candidate to check against the matching documentation for the project's version, not as a rule to apply blindly or a complete list.

- **Fetching in effects:** a slower earlier response can overwrite a newer one. Ignore or abort the superseded request in the effect's cleanup.
- **Strict Mode:** relevant development checks can run an extra effect setup/cleanup cycle. Check cleanup, idempotence and operation ownership; removing Strict Mode does not repair the lifecycle assumption. [Effect semantics](https://react.dev/reference/react/useEffect)
- **State is a snapshot:** setting state does not change the variable in the running handler. Use an updater function when the next value depends on the previous one.
- **Mutation:** changing an object or array in state in place does not trigger a render and corrupts earlier snapshots. Create a new value.
- **Keys:** use a stable identity from the data. Index keys misattribute state when a list reorders, inserts or deletes. Changing a key deliberately resets a component's state.
- **Derived data:** pure derivations usually belong in render, with justified memoization if needed. Distinguish independently editable drafts or intentional initial values; syncing props into those can erase user work.
- **Dependencies:** objects and functions created during render have a new identity every render and re-run effects. Restructure the code instead of silencing the dependency lint rule.
- **Inputs:** an editable controlled input needs the relevant change handler; a deliberately read-only field can declare `readOnly`. Switching from `undefined` to a defined value can switch an input from uncontrolled to controlled.
- **Hydration:** output that differs between server and client (current time, random values, `window`, locale formatting) causes mismatches.
- **Refs:** changing `ref.current` does not re-render. Avoid render-time reads/writes except React's documented predictable initialization pattern. [Ref caveats](https://react.dev/reference/react/useRef)
- **Context:** a provider value created inline is a new object each render and re-renders every consumer.

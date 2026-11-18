# Asynchronous operation contracts

Read this for asynchronous mutations, persistent pending state, subscriptions, and retry/recovery work. Apply only the cases affected by the change. These are application design and verification criteria, not a claim that every app needs a state library or a full test matrix.

## Establish ownership before choosing Hooks

Identify the logical operation, its identity/key, authoritative result, state owner, lifetime, persistence boundary, and observers. Distinguish a user deliberately starting another operation from retrying an unresolved one. A boolean such as `pending` does not identify which operation may be retried or cleared.

Trace every producer and consumer of shared state. A late response from an old component, identity, resource, or request generation must not overwrite or erase a newer operation's state. For shared pending records, completion must verify ownership against the current operation before clearing/replacing it. Keep that transition atomic within the actual execution boundary; a same-document check does not establish cross-tab or server atomicity.

Choose one coherent owner with explicit persistence and notification boundaries. Check all mutation paths, including success, terminal error, ambiguous failure, cleanup, remount, and reset. For React external stores, verify the subscription/snapshot contract in [React guidance](react.md); using the API name is insufficient. Do not assume adding a native storage event listener covers writes from the same document.

## Preserve the operation across uncertain outcomes

When retry safety is required, define what happens if the server commits but the response is lost. Preserve the original operation identity across the supported navigation/reload lifetime. A control labeled as retry must use that identity; it must not silently fall back to creating a fresh operation when recovery state is unavailable. Reconcile the authoritative result or expose an explicit unresolved state consistent with the product contract.

Cancellation/aborting a client wait does not establish that a server mutation was rolled back. Check the actual API and server transaction semantics. Distinguish an original response snapshot from current resource state, and a browser-local retry record from durable server deduplication. Document unsupported recovery boundaries, such as unavailable storage, where material.

## Check adversarial ordering at the relevant boundary

Select focused behavioral checks from the risks present:

- Let a real mutation commit, delay/drop its response, then retry or reload. Assert the logical operation identity and authoritative allocation count, not just success text.
- Navigate away/back or remount while work is in flight. Verify that visible pending/retry state stays consistent with the operation the next action will submit.
- Complete an older request after a newer operation starts. Verify that old completion cannot clear the newer recovery key, overwrite its result, or report the wrong owner's success.
- Change identity/resource, repeat an action, or unmount its owner when the changed code supports those transitions. Check notification and cleanup as well as eventual data.

Control ordering with deterministic barriers/interception instead of arbitrary sleeps. If the claim depends on an actual server commit, use a disposable local fixture and delay the response after that commit; a mocked success response proves only the mocked path. Keep assertions independent of implementation details, including externally visible results and authoritative state. Reuse equivalent existing coverage and report unexercised cases.

Primary contract references: [React external stores](https://react.dev/reference/react/useSyncExternalStore), [React effect cleanup and response ordering](https://react.dev/reference/react/useEffect), and [MDN storage events](https://developer.mozilla.org/en-US/docs/Web/API/Window/storage_event). Read the version/runtime-appropriate sections needed for the change; these links do not themselves prove an application design.

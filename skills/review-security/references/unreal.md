# Unreal trust boundaries

Establish the actual engine version, multiplayer topology, shipping/editor targets and enabled plugins. Read matching [Epic RPC documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-procedure-calls-in-unreal-engine) and installed declarations for the affected API; generic web security rules do not establish Unreal ownership or replication semantics.

Trace client-controlled RPC parameters, identifiers and requested gameplay effects to the authoritative server rule. Actor ownership or the ability to call an RPC does not itself establish that an amount, target, position or action is permitted. Check meaningful range/state/ownership/work limits and the real rejecting path; demonstrate legitimate and invalid clients when the runtime is available.

Inspect affected save/import/plugin/network parsing paths for untrusted file/data handling and bounded resource use. Keep credentials, privileged service actions and authoritative outcomes out of client-only assumptions. Distinguish local-only gameplay from server-authoritative multiplayer before claiming a bypass. An anti-cheat product or a shipping build is not proof of these application contracts.

Use actual server/client roles and matching builds for consequential claims. Never claim an exploit was reproduced from a generic C++ parse, mocked engine interface or one standalone viewport. Follow `official-unreal-dev`/`validate-unreal-project` when installed for lifecycle, build and runtime evidence.

## Commonly missed cases

These are frequent sources of real defects. Treat each as a candidate to check against the matching documentation for the project's version, not as a rule to apply blindly or a complete list.

- **Client-reported outcomes:** damage, cost, cooldown, hit result and position sent in a Server RPC are attacker-controlled. Recompute them on the server from authoritative state.
- **Object references in RPCs:** a client can pass any actor it knows about. Verify ownership, range, line of sight and current state for the specific target.
- **Call rate and size:** a Server RPC can be sent every frame with maximum-size arrays or strings. Bound the work per call and per connection.
- **Validation functions:** a failed `WithValidation` check disconnects the client, so reserve it for input a legitimate client can never send. Reject ordinary invalid requests inside the implementation.
- **Information exposure:** data replicated to every client (hidden positions, other players' inventories, random seeds) is readable by a modified client. Use owner-only conditions and relevancy for private state.
- **Debug surface:** `Exec` functions, cheat-manager commands and debug RPCs must be excluded from or disabled in shipping builds, on the server as well as the client.
- **Listen servers:** the hosting player is the authority. Competitive integrity against the host requires a dedicated server.
- **Local saves are editable.** Progression or economy that matters online needs server-side validation or storage.
- **Custom movement:** abilities that set location or velocity directly can bypass the movement component's server correction.

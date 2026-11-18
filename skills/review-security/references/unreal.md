# Unreal trust boundaries

Establish the actual engine version, multiplayer topology, shipping/editor targets and enabled plugins. Read matching [Epic RPC documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-procedure-calls-in-unreal-engine) and installed declarations for the affected API; generic web security rules do not establish Unreal ownership or replication semantics.

Trace client-controlled RPC parameters, identifiers and requested gameplay effects to the authoritative server rule. Actor ownership or the ability to call an RPC does not itself establish that an amount, target, position or action is permitted. Check meaningful range/state/ownership/work limits and the real rejecting path; demonstrate legitimate and invalid clients when the runtime is available.

Inspect affected save/import/plugin/network parsing paths for untrusted file/data handling and bounded resource use. Keep credentials, privileged service actions and authoritative outcomes out of client-only assumptions. Distinguish local-only gameplay from server-authoritative multiplayer before claiming a bypass. An anti-cheat product or a shipping build is not proof of these application contracts.

Use actual server/client roles and matching builds for consequential claims. Never claim an exploit was reproduced from a generic C++ parse, mocked engine interface or one standalone viewport. Follow `official-unreal-dev`/`validate-unreal-project` when installed for lifecycle, build and runtime evidence.

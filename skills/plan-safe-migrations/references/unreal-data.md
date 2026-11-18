# Unreal save and asset compatibility

Identify the actual engine/fork, game/content version, save format and serialized/reflected names. Read matching [Epic save/load guidance](https://dev.epicgames.com/documentation/en-us/unreal-engine/saving-and-loading-your-game-in-unreal-engine), [Core Redirects](https://dev.epicgames.com/documentation/en-us/unreal-engine/core-redirects-in-unreal-engine) and installed serializer/header evidence as needed.

A C++ rename can affect Blueprint/reflected assets and saved data. Inventory consumers before choosing a redirect, explicit converter or versioned serializer. Core Redirects address supported reflected-name remapping; they do not establish that an arbitrary binary save, changed field meaning or numeric conversion is compatible. Inspect the actual save/serialization mechanism rather than treating all files as the same format.

Use copies of representative older saves/assets and preserve originals. Check old-value semantics, missing/default properties, renamed classes/structs/enums, object/soft references and load failures where affected. Make format versions and supported upgrade paths explicit; reject or recover unsupported/future data deliberately instead of silently resetting progress.

For relevant asset/reflection changes, validate loading and consumers in the real engine, then appropriate cook/package and launched-target behavior. Keep editor and packaged/platform results separate. Do not rewrite `.uasset`/`.umap` bytes as text, run broad resave/fix-up operations outside scope, overwrite unsaved assets, or upgrade the engine as incidental migration setup. `validate-unreal-project` supplies the execution/evidence workflow when installed.

# Unreal save and asset compatibility

Identify the actual engine/fork, game/content version, save format and serialized/reflected names. Read matching [Epic save/load guidance](https://dev.epicgames.com/documentation/en-us/unreal-engine/saving-and-loading-your-game-in-unreal-engine), [Core Redirects](https://dev.epicgames.com/documentation/en-us/unreal-engine/core-redirects-in-unreal-engine) and installed serializer/header evidence as needed.

A C++ rename can affect Blueprint/reflected assets and saved data. Inventory consumers before choosing a redirect, explicit converter or versioned serializer. Core Redirects address supported reflected-name remapping; they do not establish that an arbitrary binary save, changed field meaning or numeric conversion is compatible. Inspect the actual save/serialization mechanism rather than treating all files as the same format.

Use copies of representative older saves/assets and preserve originals. Check old-value semantics, missing/default properties, renamed classes/structs/enums, object/soft references and load failures where affected. Make format versions and supported upgrade paths explicit; reject or recover unsupported/future data deliberately instead of silently resetting progress.

For relevant asset/reflection changes, validate loading and consumers in the real engine, then appropriate cook/package and launched-target behavior. Keep editor and packaged/platform results separate. Do not rewrite `.uasset`/`.umap` bytes as text, run broad resave/fix-up operations outside scope, overwrite unsaved assets, or upgrade the engine as incidental migration setup. `validate-unreal-project` supplies the execution/evidence workflow when installed.

## Commonly missed cases

These are frequent sources of real defects. Treat each as a candidate to check against the matching documentation for the project's version, not as a rule to apply blindly or a complete list.

- **Binary save layout:** a positional `Serialize`/`operator<<` sequence can misread older data after fields change. Define versioned or explicitly compatible reads for supported historical layouts, rather than assuming a current writer defines every old file.
- **Version markers:** ensure the selected format actually stores and restores version information. Use the engine's custom-version mechanism where supported, with deliberate handling of missing and future versions; registering a version alone does not establish persistence.
- **Property-based saves:** inspect the actual serializer/archive flags. Epic's `SaveGameToSlot` writes non-transient properties without filtering by the `SaveGame` flag; a custom save archive can have different rules. Renames/retypes may need redirects or explicit conversion rather than silently accepting defaults. [SaveGameToSlot contract](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UGameplayStatics/SaveGameToSlot)
- **Enums:** inserting or reordering implicit values can change stored numeric meanings. Preserve explicit persisted values or convert supported old data. Name-based renames may need redirects/conversion too.
- **Asset moves and renames:** old soft references/saved paths may depend on redirects. Verify the actual load path and packaged availability; add explicit mapping when the supported redirect mechanism cannot resolve existing saves.
- **Blueprint consumers:** renaming or removing a reflected function or property breaks Blueprint nodes that compile only when the asset is next loaded. Deprecate first, then remove after consumers are updated.
- **Default changes:** a new class default does not change instances whose saved value differed from the old default, and does change instances that saved nothing because they matched it.
- **Load-time fix-ups:** conversions in `PostLoad` or a load callback must be idempotent and must run on every path that loads the object.
- **Platform and build differences:** check packaged builds as well as the editor; cooked data, save locations and byte handling can differ.

# Working in an existing Unreal project

Use this for established games, plugins, and engine-fork projects. Inspect the affected system and consumers rather than turning a narrow request into a full content audit.

## Discover and preserve the current state

Read repository/subdirectory instructions, setup/build notes, design decisions, and the requested feature/defect. Establish the active source-control system and pending changes (for example Git or Perforce) without reverting, automatically stashing, or submitting work. Identify who owns shared binary assets/maps and preserve unsaved editor changes. Source-control cleanliness does not establish that editor state is saved.

Resolve the intended `.uproject`, engine association, installed build/fork, target/platform/configuration, modules/plugins, supported C++ toolchain, and content/config locations. A repository may contain several projects or a plugin with a separate host project. Match its actual engine and installed headers; do not associate it with the newest engine, regenerate project settings, or enable a plugin solely to fit an example.

Trace the requested gameplay action through its C++/Blueprint boundaries, owning actor/component/subsystem, authority/replication, data assets, maps/widgets, and relevant persistence. Search existing domain implementations and asset/reflection consumers before adding systems. Reuse compatible project capabilities and conventions; verify questionable existing API/lifetime assumptions against matching Epic documentation and source.

## Establish evidence before changing behavior

Inspect existing build/automation/editor scripts and environment assumptions before running them. Choose the relevant existing target/test map/functional check and record revision or file snapshot, engine/configuration, command/actions, and actual result. Distinguish baseline failures from new regressions and missing engine/SDK/content access. Do not modify unrelated content, install/upgrade the engine, or overwrite user saves merely to create a clean baseline.

Use an isolated test fixture/profile or approved representative content for runtime validation. When important existing behavior lacks checks, add a focused regression/characterization case where useful; do not require the whole game to be rebuilt and packaged for every small edit. Current behavior supplies compatibility evidence, not permission to preserve a requested defect.

## Make a compatible, bounded change

Identify existing extension points and affected C++/Blueprint/asset consumers. Preserve module boundaries and the project's gameplay, input, UI, error, lifetime, and networking conventions where compatible with the requirement. Treat changes to reflected/serialized names, asset paths, config, save formats, replication contracts, and public plugin APIs as compatibility work when affected: inspect matching engine guidance and plan the required consumer updates or transition. Do not rename/move broad asset trees or replace a framework as incidental cleanup.

Coordinate a single writer for affected binary assets and editor-global actions. Check the resulting source/config/asset changes and preserve pre-existing work. Validate the requested behavior and relevant existing journeys with the real target/runtime checks appropriate to the claim; `validate-unreal-project` provides guidance when installed. Report baseline versus new failures, compatibility/asset changes, exact checks, and untested configurations. Do not equate a source-only diff, successful Live Coding update, or absence of crashes with complete project validation.

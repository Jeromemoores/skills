---
name: review-web-design
description: "Review rendered website UI/UX, visual composition and generic or unsupported design choices. Use for design critique, de-slop passes, responsive/state reviews and proposed refinements; exclude backend-only review and whole-site accessibility certification."
---

# Review Web Design

Judge the interface against its brief, users, content and actual tasks. A review may retain a familiar visual treatment when it works. Novelty, fewer cards, a different font or an automated score does not establish improvement.

## Establish the review scope

Read the requested change, real content, current brand/design system, relevant flow and available evidence. Identify what should be preserved. Distinguish observed user/product evidence from assumptions and the reviewer's aesthetic preference. Honor review-only scope; proposing a redesign does not authorize edits. Use `propose-code-review` when installed and the user requests Accept/Reject code previews.

Read [Rendered review and de-slop](references/rendered-review.md). Use `design-web-interface` references for substantial flow/composition questions, including its phone/tablet/desktop and input reference for affected responsive work, when available. Use `review-accessibility` for affected accessibility behavior, and `official-stack-dev`/`review-and-repair-code` for consequential implementation/API questions. Apply these companions proportionately rather than duplicating all their checklists.

## Inspect what people encounter

Inspect rendered screens in the actual browser/runtime when available. Record relevant viewport, states and interactions. Evaluate hierarchy, grouping, alignment, typography, density, imagery, action priority, content clarity and responsive adaptation against the task. Operate an important flow and its relevant failure/recovery path; a polished static screenshot does not establish usable interaction.

Challenge fragile assumptions with realistic content or an affected boundary: long labels, missing data/media, empty versus error states, filters, pending submission, Back/cancel/resume, narrow layout or keyboard focus as applicable. Use supplied facts and state clearly when a fixture is constructed. Do not demand an unrelated full state/device matrix for a local edit.

For a de-slop pass, investigate generic copy, unsupported credibility claims, arbitrary visual devices, mismatched content structures, inappropriate density and decorative or false affordances. Treat patterns as candidates requiring a concrete reason to change, not a blacklist of fonts, colors, gradients, cards or conventional layouts. Preserve truthful content, useful consistency, important controls and the intended brand.

If rendered access is unavailable, provide a source-supported preliminary review and name the missing evidence. Do not claim screenshots, interaction success, assistive-technology behavior, user preference or conversion benefits that were not observed. Pixel comparisons detect change against a reference, not whether the reference is good design.

## Report and verify

Prioritize by effect on the user's task. Separate reproducible functional/accessibility barriers, evidence-supported usability/visual problems, unsupported product claims and optional aesthetic preferences. For a worthwhile finding give the page/control/location, observed condition, effect, bounded recommendation and how to verify it. Avoid arbitrary issue quotas, unsupported numerical design scores and blanket claims that something looks human-made or AI-made.

When repairs are authorized, make a coherent scoped change, preserve behavior/contracts, then inspect the rendered result and affected interaction again. Record any regression or unavailable check. A reference image or customer preference may settle a visual choice without making it a universal design rule.

Return the important findings, checks actually performed, preserved constraints and remaining uncertainty. An agent walkthrough is heuristic inspection, not a user study or whole-site conformance claim.

---
name: design-web-interface
description: "Plan and implement website UI/UX and visual direction for new or existing pages, dashboards and user flows. Use for layout, typography, content hierarchy, responsive composition and interaction design; exclude backend-only work and review-only audits."
---

# Design Web Interfaces

Make the interface fit its users, content and task. A distinctive appearance is useful when it serves the brief; novelty, fashionable decoration and a familiar font are not measures of quality.

## Establish the design problem

Read the brief, actual content, relevant routes/components and existing brand/tokens before changing the design. Identify the primary task, audience/context, important constraints and observable completion. Separate supplied facts, observed product evidence and assumptions. Do not fabricate research, customer claims, testimonials or production capabilities. For an existing product, preserve unaffected behavior, terminology, brand and compatible components; a local improvement does not authorize a redesign.

For a new or consequential flow, read [Tasks, content and states](references/tasks-and-states.md). Map the important journey and recovery path before polishing screens. For a small visual edit, use the relevant existing context rather than creating a new planning ceremony. Ask only for missing decisions that materially change the result; reuse established preferences and proceed on stated routine assumptions.

## Choose a coherent direction

Read [Visual direction](references/visual-direction.md) when choosing or reshaping composition, typography or imagery, and [Responsive layouts and input](references/responsive-and-input.md) for affected phone/tablet/desktop layout, navigation, forms and touch/keyboard behavior. Analyze a few relevant references when useful: describe what transfers and why. Do not copy another brand's assets or treat a design system's tokens as universal rules. Honor a supplied design/reference before inventing alternatives. Explore different compositions when the brief is open and the decision matters; do not require multiple concepts for every change.

Define a compact project-specific system: content hierarchy, type roles, spacing/grouping, layout, color roles, imagery and interaction treatment as relevant. Use existing tokens/components where compatible. Choose density for the task: an operational table, reading experience and campaign page need different emphasis. Avoid automatic bans on colors, fonts, cards or conventional navigation. Every prominent visual device should have a useful role in communication, identity, grouping, state or feedback.

Record the direction and rationale in the existing task/design record when useful. Keep product copy focused on the user's action and supplied facts. Implementation choices and internal architecture belong in developer documentation unless they help the site's users decide something.

## Implement and inspect

When implementation is requested, use the existing stack and relevant maintainer documentation. Use `official-stack-dev` and `dependency-docs` when installed for actual versions, documented APIs and compatible reuse. Design work does not imply a new UI framework, font service, animation package or dependency upgrade. Preserve data/API contracts and meaningful behavior; mock interactions must be clearly identified as prototypes.

Use semantic controls and truthful affordances. Include affected loading, empty, invalid, failure, success and recovery states rather than designing only the ideal populated screen. Read the tasks/states reference for relevant cases, not a compulsory matrix for cosmetic edits. Keep calculations, state changes and presentation cohesive using the project's code-quality conventions.

Inspect the rendered result in a real browser when available: relevant desktop/narrow widths, realistic content, long labels and the important interaction. Recompose for constrained widths rather than merely shrinking the desktop. Check for clipping, missing content, confusing action priority and decoration that competes with the task. Verify the implementation against the selected direction and fix the largest supported problems before micro-polish. Browser screenshots support visual observations; source inspection alone does not establish rendered quality.

Use `review-accessibility` for affected accessibility behavior when installed and `review-web-design` for a rendered visual/UX critique. Keep accessibility, functionality, aesthetic preference and measured performance distinct. If browser/runtime access is unavailable, provide the requested artifact and a precise unverified-check handoff; do not claim screenshots or tests were inspected.

Return the design rationale, changed scope, references actually used, observed checks, meaningful tradeoffs and remaining uncertainties. Planning-only requests return a concrete plan; reviews use the review skill when available. Preserve the user's requested deliverable and existing authorization.

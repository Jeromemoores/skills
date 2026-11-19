# Rendered review and de-slop

## Establish evidence

Use the real brief, content, current design system and affected task. A screenshot can support composition observations; source can explain a cause; a browser interaction can reproduce behavior. Match the evidence to the claim. Record what was actually inspected and avoid substituting a build, linter, pixel diff or code detector for design judgment.

Review meaningful desktop/narrow views and states. Use relevant intermediate widths or zoom/reflow checks when the layout warrants them. Browser emulation is not physical-device testing. Control fonts, browser, OS and other rendering conditions for repeatable screenshot comparisons. Do not automatically accept a changed baseline as an improvement. [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots), [emulation](https://playwright.dev/docs/emulation)

For substantial responsive work, include relevant phone touch, tablet portrait/landscape and desktop keyboard/mouse paths. Check that collapsed navigation remains operable, actions do not require hover, meaningful tables remain usable and overlays do not obscure focused fields/actions. A narrow screenshot alone does not verify soft-keyboard, safe-area or physical-device behavior. Use the design skill's responsive/input reference when installed.

## Task and composition critique

Ask whether people can identify the important information, understand their options and complete the intended job. Inspect reading/action priority, grouping, alignment, type roles, density, imagery and state feedback. Check actual labels/content and the path through correction, Back, cancel or retry where affected. Do not judge an operational screen by a campaign-page aesthetic. Heuristics identify risks; they do not prove that a proposed design improves user outcomes. [NN/G heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)

Inspect actual visible text for corrupted punctuation/symbols or missing glyphs, including important prices, hours and labels. Distinguish a terminal's decoding problem from corruption in the file/browser; use decoded source plus rendered evidence. Preserve valid non-ASCII content and fix the cause rather than categorizing damaged text as an aesthetic preference.

Give findings as observation -> task/communication effect -> bounded change -> verification. For example, an empty filter result and a failed data request need different messages and recovery; the same illustration cannot establish which occurred. [Carbon empty states](https://www.carbondesignsystem.com/building-blocks/core/patterns/empty-states)

## Diagnose generic or misleading output

| Candidate | Useful question | Preservation boundary |
| --- | --- | --- |
| Interchangeable copy | Could this describe any unrelated product? Does the CTA explain what happens? | Preserve meaning; use verified specifics rather than invented capabilities. |
| Unsupported proof | Are metrics, endorsements, logos or comparisons grounded in supplied facts? | Flag, substantiate or omit; do not fabricate better testimonials. |
| Arbitrary decoration | Does a glow, marker, number or animation carry identity, grouping, priority, state or feedback? | Keep purposeful branding and useful guidance; no decoration ban. |
| Container monotony | Are unlike information types forced into one repeated card? | Keep consistent rows/cards when repeated records benefit from scanning. |
| Inappropriate density | Does the space support the task and amount of content? | Preserve efficient tables and expert workflows; more whitespace is not automatically better. |
| False affordance | Does a button/link/hover treatment promise an action that actually works? | Preserve truthful controls; label illustrative prototypes clearly. |
| Fragile polish | Does the composition survive real content, missing media and affected states? | Fix the cause; do not hide content or remove functionality to improve a screenshot. |

These checks are original diagnostic guidance, not an automated classifier of authorship. An established purple/Inter brand or a familiar navigation layout may be entirely appropriate. Identify a concrete task, legibility, consistency or communication problem before recommending a change. Distinguish optional taste changes from acceptance defects.

## Compare and revise

For evaluating a new design workflow, use contrasting briefs, such as a service-business website and an existing-brand task-heavy application. Keep facts, assets, model, tools, code baseline and effort comparable. Randomize presentation when feasible and initially hide builder explanations. Compare brief fit, clarity, hierarchy, content fidelity, task behavior and responsive adaptation; explain judgments instead of inventing a global quality score.

Include negative controls that should survive review, such as a working established brand and a purposeful dense table. Do not reward novelty, fewer recognizable patterns, removed content or decorative replacement of a working flow. Give a bounded revision round and inspect both improvement and regressions. This is a proposed evaluation method, not a standardized test or evidence of improvement before execution.

Keep functional and accessibility findings separate from aesthetic preferences; attractive styling cannot compensate for an unusable required control. Use the accessibility specialist for applicable criteria, and distinguish an agent review from actual users attempting neutral, believable tasks. [GOV.UK usability testing](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing)

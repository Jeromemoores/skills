---
name: review-accessibility
description: "Review or improve web UI accessibility using W3C guidance and observed keyboard, focus, form, visual and assistive-technology behavior. Use for accessibility reviews or affected interactive UI flows; exclude Unreal-specific game accessibility and whole-site conformance claims from limited checks."
---

# Review Accessibility

Evaluate whether people can complete the affected task with the supported input and assistive technologies. A semantic-looking component, ARIA attribute or passing automated scan does not establish usable behavior.

## Establish the target

Read the requested journey, current markup/components/styles, browser targets and existing tests. Preserve the project's architecture and pending work. Use its adopted accessibility target; if none is specified, describe WCAG 2.2 Level AA as a proposed engineering review baseline, not a legal conclusion or certification. Keep the review proportionate to the affected UI.

Use matching cached MDN/framework references through `official-stack-dev` when available, then focused W3C/maintainer pages for missing contracts. Read the relevant [WCAG 2.2 success criteria](https://www.w3.org/TR/WCAG22/), distinguishing normative requirements from techniques and examples. Record only criteria actually evaluated. Avoid turning a local component fix into an unsupported claim about every page, browser or disability.

## Inspect the actual interaction

Choose relevant checks rather than imposing the whole list on every edit:

- **Structure and names:** meaningful page regions/headings, accessible control names, visible labels and useful alternatives for informative content. Check computed role/name/state where tools permit. Prefer native HTML behavior; adding ARIA does not supply missing interaction logic.
- **Keyboard and focus:** complete the journey with Tab/Shift+Tab and the widget's documented keys. Check visible/predictable focus, entry/exit, focus after close/removal/navigation, and absence of unintended traps. Custom widgets need their actual keyboard behavior, not just roles. Consult [WAI keyboard guidance](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/).
- **Forms and status:** connect instructions/errors to the relevant field, preserve useful input, and verify invalid/pending/success states against the visible value and submitted operation. Exercise correction, reset, retry and completion. An error that remains after reset is observable behavior, not merely an attribute check. Read [WAI notifications](https://www.w3.org/WAI/tutorials/forms/notifications/).
- **Visual and responsive use:** inspect relevant contrast, focus visibility, zoom/reflow, target size and non-color cues against the applicable criterion. Assess motion/time limits and media alternatives when affected. Do not infer measured contrast or keyboard usability from a screenshot alone.

## Verify and report

Reuse existing browser/audit tooling where suitable and match its documentation/version. Record viewport, browser, input method, relevant assistive technology and the states actually exercised. Combine automated checks with manual interaction appropriate to the claim. [WAI Easy Checks](https://www.w3.org/WAI/test-evaluate/preliminary/) is an initial assessment, not comprehensive evaluation.

For a meaningful defect, give the file/control, user action, expected versus observed experience, applicable reference, impact and a bounded correction. Separate verified barriers from suspected assistive-technology issues requiring unavailable tools. A DOM live region does not prove an announcement was heard; distinguish inspected markup, accessibility-tree evidence and an actual screen-reader run. Do not invent check outcomes or user feedback.

Honor review-only scope; use `propose-code-review` if installed when previews are requested. For authorized fixes, preserve application behavior and public component contracts. Add focused behavioral coverage for the regression when useful, then repeat the affected journey. Report remaining coverage gaps and sources actually read. Avoid unrelated visual redesign, cosmetic cleanup quotas, automatic overlays, or a whole-site conformance claim based on one component or scanner score.

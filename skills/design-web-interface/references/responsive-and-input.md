# Phone, tablet, desktop and input behavior

Design for the supported range of available space and input capabilities. Phone/tablet/desktop are useful test categories, not sufficient detection rules: a narrow window can have a mouse, a tablet can have a keyboard, and a large screen can be touch-enabled. Reuse the project's browser/device targets; identify meaningful gaps without inventing a mandatory full device lab for a local edit.

## Layout and content

- Start from the smallest useful content arrangement and add space deliberately. Choose breakpoints where content or interaction needs a different composition; do not assume one framework's device widths are universal.
- Keep primary tasks, necessary navigation and important information available across layouts. Reorder/group deliberately and preserve sensible DOM reading/focus order. If navigation collapses, provide an operable labeled replacement; hiding destinations is not a complete mobile-navigation solution.
- Test intermediate widths as well as phone/tablet/desktop samples. Check tablet portrait/landscape and short landscape windows when relevant; unnecessary orientation restrictions can prevent use.
- Allow long labels, supported text scaling and realistic content. Avoid fixed heights that clip fields, messages or expanded sections. Desktop layouts should also remain readable instead of stretching text/data indiscriminately across a large monitor.
- Contain genuinely two-dimensional content, such as a comparison table or map, with a usable, discoverable scrolling/alternative treatment. Preserve necessary columns and keyboard access. Avoid whole-page overflow, clipped data or replacing every dense table with cards merely to obtain a screenshot without scrollbars.
- Use responsive media sizing/crops and appropriate delivery for the project. Missing-media behavior should preserve the task. Test content priorities before hiding media or text for a smaller viewport.

[GOV.UK layout](https://design-system.service.gov.uk/styles/layout/) gives contextual layout examples; [W3C reflow guidance](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) explains constrained-width behavior and exceptions. Distinguish their exact conventions and criteria from project design choices.

## Touch, mouse and keyboard

Provide visible, operable controls without requiring hover. Use hover/pointer capability queries for optional enhancements, not as a complete device detector; hybrid input remains possible. Preserve native activation, focus visibility and keyboard paths instead of adding redundant handlers indiscriminately. Gesture/drag actions need appropriate ordinary-control alternatives when applicable. [MDN hover feature](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/hover)

Give targets usable size/spacing for supported inputs. WCAG 2.2 AA target-size minimum uses 24 by 24 CSS pixels with defined exceptions; generous project targets may improve comfort, but a fixed 44px rule is not the universal AA requirement. Inspect actual target bounds and spacing when making a claim. [W3C target-size minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)

For forms, choose appropriate native types, input modes and autocomplete behavior. Check focused fields, validation, messages and submit actions under constrained height. A screenshot of an unfocused form does not prove the on-screen keyboard leaves it usable. Preserve input and recovery behavior across resizing/orientation where the product supports it.

## Viewport, overlays and motion

Use an appropriate viewport declaration and preserve zoom. Inspect sticky/fixed navigation, dialogs and bottom actions for obstruction of content/focus. Account for dynamic browser chrome, on-screen keyboards and safe areas when affected, using supported platform features and fallbacks. Do not assume a desktop viewport resize reproduces these behaviors. [MDN viewport](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name/viewport), [safe-area environment values](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/env)

Respect reduced-motion preferences and keep actions responsive. Scope asset/effect costs to realistic devices and networks when performance is part of the brief; desktop smoothness is not mobile performance evidence.

## Verification record

Select representative widths, orientations and inputs from the affected risk. Record dimensions, browser/engine, touch or keyboard method, relevant preference settings and states actually exercised. Check task completion and recovery, not only page width. For a substantial new interface, include a phone touch path, tablet layouts and a desktop keyboard/mouse path when available.

Use the accessibility specialist for applicable reflow, orientation, target, focus and gesture criteria. Browser emulation establishes its tested conditions; actual Safari/Android behavior, soft keyboards, safe-area geometry and physical-device usability need the relevant real environment before claiming support. Report those limits explicitly. [Playwright emulation](https://playwright.dev/docs/emulation)

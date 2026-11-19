# Tasks, content and interaction states

## Understand the job

For the affected flow, establish the user/context, trigger, goal, necessary information, important decisions and successful outcome. Existing research, support issues, analytics and observed behavior may inform the design when available. Label stakeholder or agent guesses as assumptions, including invented personas. Do not claim a user study from an agent walkthrough. [GOV.UK user needs](https://www.gov.uk/service-manual/user-research/start-by-learning-user-needs)

Map enough of the journey to expose prerequisites, handoffs, completion and later follow-up. Preserve relevant current behavior before proposing a change. Choose navigation around tasks and useful destinations; a route/database tree is not automatically a useful menu. Repeated nonlinear work differs from a linear completion flow. Government-service patterns are contextual examples, not a requirement to make every site look or navigate like GOV.UK. [Whole-problem mapping](https://www.gov.uk/service-manual/design/map-a-users-whole-problem), [service navigation](https://design-system.service.gov.uk/patterns/navigate-a-service/)

## Reduce effort and support recovery

Justify questions and required fields; reuse supplied information where appropriate. Make labels, consequences and action names clear. Preserve useful input during correction, Back, retry or uncertain submission where the product supports those actions. Distinguish invalid input, denied access, missing configuration and infrastructure failure. Check the visible draft and the submitted operation agree; a retry must perform the operation it promises. Do not prescribe one-question pages or disabling native validation without the actual product/component context. [Question pages](https://design-system.service.gov.uk/patterns/question-pages/), [validation](https://design-system.service.gov.uk/patterns/validation/)

Keep relevant context available instead of requiring memory across screens. Progressive disclosure is appropriate for secondary information when its path remains apparent; avoid hiding required instructions, important consequences or primary controls for visual neatness. [Recognition and recall](https://www.nngroup.com/articles/recognition-and-recall/), [progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/)

Use facts supplied by the user/product or clearly labeled illustrative content. Unsupported metrics, reviews, customer logos and performance/security claims should be flagged, substantiated or omitted. Preserve the intended meaning when revising vague copy; do not invent capabilities to make a headline more specific.

## Choose relevant state checks

Use the states affected by the change rather than requiring every case for every edit:

- Initial/loading, populated, first-use empty, zero filtered results and completed work.
- Invalid input and correction; pending, success, failure and uncertain remote outcome.
- Permission/configuration changes, unavailable media and partial data where applicable.
- Back, cancel, refresh, filter/pagination reset, resumption and repeated actions.
- Realistic long/short text, supported locale/number/date variation and narrow layouts.

Each state needs an accurate explanation and a useful next action where one exists. Avoid presenting service failure as no records, or every empty state as the same illustration and onboarding button. [Carbon empty states](https://www.carbondesignsystem.com/building-blocks/core/patterns/empty-states)

Onboarding should help people reach useful work. Explain necessary setup; allow resuming or dismissing nonessential teaching where appropriate. Required security or configuration prerequisites remain required. [Shopify App Home](https://shopify.dev/docs/apps/design/user-experience/app-home-page)

## Evidence and boundaries

Observe the actual interaction when claiming it works. Check relevant keyboard/focus behavior and use the accessibility specialist for its criteria. Heuristic inspection identifies likely usability risks; it does not establish real-user success, conversion improvement or accessibility conformance. Report what was observed and what still needs user research. [NN/G heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/), [GOV.UK usability testing](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing)

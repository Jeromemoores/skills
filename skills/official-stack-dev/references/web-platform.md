# CSS and plain JavaScript documentation

Use the locally cached MDN references for practical platform guidance:

- [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS): cascade, inheritance, selectors, layout, properties, values, responsive design, and animations. Search with `--stack css`.
- [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript): language guide, syntax, functions, objects, collections, promises, modules, and standard built-ins. Search with `--stack javascript --source javascript`.
- [Web APIs](https://developer.mozilla.org/en-US/docs/Web/API): the local `web-apis` source covers common DOM manipulation, events, window operations, fetch/request/response, cancellation, URLs, forms, storage, history, location, and console APIs. Search with `--stack javascript --source web-apis`. This is a selected subset, not every browser API; retrieve missing APIs from their maintained references.

MDN is a maintained developer reference, not the normative specification itself. For precise or disputed semantics, follow the page's specification links to [CSS specifications](https://www.w3.org/Style/CSS/specs.en.html), the [ECMAScript specification](https://tc39.es/ecma262/), or the appropriate web-platform standard. The latest ECMAScript page includes the evolving draft; verify feature standardization and implementation support separately. These standards are linked references, not an additional locally mirrored corpus.

For a new plain website, run `ensure --project PATH --web`. Existing HTML/CSS/JS and React/Next.js projects are detected with a bounded file scan that excludes dependencies/build outputs. A JavaScript-only package receives language docs; browser APIs are included for detected websites or explicit `--web` mode. No framework is required.

CSS and JS snapshots are pinned to the MDN repository revision. They are not bound to a React release, an ECMAScript edition, or a particular browser version. Read the project's browser targets and runtime/tooling configuration before choosing modern features. Raw MDN Markdown contains macros such as compatibility-table placeholders; the downloaded text does not include every rendered table. Check live compatibility data when support matters, and disclose when it could not be verified.

For CSS changes, resolve the actual cascade, specificity, sizing/overflow, and layout context; choose an appropriate primitive before stacking overrides. Verify affected viewport sizes and relevant interaction states. For JavaScript, distinguish language semantics from host APIs, and check errors, asynchronous ordering, cancellation, and event-listener lifetime where relevant. Use behavior-focused checks rather than assuming that a familiar snippet or a documentation example proves the complete application works.

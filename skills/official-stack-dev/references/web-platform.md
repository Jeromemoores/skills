# CSS and plain JavaScript documentation

Use the locally cached MDN references for practical platform guidance:

- [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS): cascade, inheritance, selectors, layout, properties, values, responsive design, and animations. Search with `--stack css`.
- [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript): language guide, syntax, functions, objects, collections, promises, modules, and standard built-ins. Search with `--stack javascript --source javascript`.
- [Web APIs](https://developer.mozilla.org/en-US/docs/Web/API): the local `web-apis` source covers common DOM manipulation, events, window operations, fetch/request/response, cancellation, URLs, forms, storage, history, location, and console APIs. Search with `--stack javascript --source web-apis`. This is a selected subset, not every browser API; retrieve missing APIs from their maintained references.

MDN is a maintained developer reference, not the normative specification itself. For precise or disputed semantics, follow the page's specification links to [CSS specifications](https://www.w3.org/Style/CSS/specs.en.html), the [ECMAScript specification](https://tc39.es/ecma262/), or the appropriate web-platform standard. The latest ECMAScript page includes the evolving draft; verify feature standardization and implementation support separately. These standards are linked references, not an additional locally mirrored corpus.

For a new plain website, run `ensure --project PATH --web`. Existing HTML/CSS/JS and React/Next.js projects are detected with a bounded file scan that excludes dependencies/build outputs. A JavaScript-only package receives language docs; browser APIs are included for detected websites or explicit `--web` mode. No framework is required.

CSS and JS snapshots are pinned to the MDN repository revision. They are not bound to a React release, an ECMAScript edition, or a particular browser version. Read the project's browser targets and runtime/tooling configuration before choosing modern features. Raw MDN Markdown contains macros such as compatibility-table placeholders; the downloaded text does not include every rendered table. Check live compatibility data when support matters, and disclose when it could not be verified.

For CSS changes, resolve the actual cascade, specificity, sizing/overflow, and layout context; choose an appropriate primitive before stacking overrides. Verify affected viewport sizes and relevant interaction states. For JavaScript, distinguish language semantics from host APIs, and check errors, asynchronous ordering, cancellation, and event-listener lifetime where relevant. Use behavior-focused checks rather than assuming that a familiar snippet or a documentation example proves the complete application works.

## Commonly missed cases

These are frequent sources of real defects. Treat each as a candidate to check against the matching documentation for the project's version, not as a rule to apply blindly or a complete list.

CSS:

- **Overflowing flex/grid children:** items default to `min-width: auto`, so long content forces overflow. `min-width: 0` or `minmax(0, 1fr)` lets them shrink.
- **`z-index` only orders elements inside the same stacking context.** `transform`, `opacity` below 1, `filter` and similar properties create a new one.
- **Positioning:** a transformed ancestor can establish the containing block for `fixed`. A `sticky` element follows its nearest scrolling ancestor and needs a non-auto inset on the intended axis; an overflow ancestor changes that context rather than universally disabling sticky. Check available scroll space and containment. [Positioning reference](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position)
- **`100vh` on phones includes the area behind browser chrome.** Dynamic viewport units address this; check target support.
- **Vertical margins collapse**, and percentage heights need an ancestor with a definite height.
- **Specificity fights:** lower the competing selector or use cascade layers before reaching for `!important`.
- **Motion:** honor `prefers-reduced-motion`, and animate `transform`/`opacity` rather than properties that trigger layout.

JavaScript:

- **`fetch` resolves on HTTP 4xx/5xx.** Check `response.ok` and handle rejected promises separately; network errors, cancellation and invalid/unsupported requests can reject.
- **`await` inside a `forEach` callback is not awaited** by the caller. Use `for...of` or `Promise.all`. `Promise.all` rejects on the first failure while the other operations keep running; `Promise.allSettled` reports each result.
- **Out-of-order responses:** cancel or ignore superseded requests for search-as-you-type and similar inputs.
- **Listeners:** `removeEventListener` needs the same function reference and capture option. An `AbortSignal` passed to `addEventListener` removes several at once.
- **`innerHTML` with untrusted text is script injection.** Use `textContent` or the framework's escaping.
- **Numbers are IEEE doubles:** `0.1 + 0.2 !== 0.3`, and integers beyond 2^53 lose precision. Keep money in integer minor units.
- **Dates:** parsing non-ISO strings is implementation-defined. A date-only ISO string parses as UTC, while a date-time without an offset parses as local time.
- **`localStorage`** is synchronous, stores only strings, and can throw (quota, privacy modes).
- **Copies:** a JSON round trip omits object properties containing `undefined` (array entries become `null`), converts `Date` to a string, and normally loses `Map`/`Set` contents. Custom serialization can differ. `structuredClone` supports those data types where available, but not every value/prototype. [JSON behavior](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify)

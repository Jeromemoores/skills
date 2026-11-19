# Web and service review

Select relevant controls from the project's security requirements and the [OWASP ASVS](https://asvs.owasp.org/). Record the edition and requirement identifiers only when actually consulted. Match framework/runtime behavior to the installed version.

Follow affected paths:

- Authentication establishes identity; authorization must also enforce access to the particular object/action/tenant on the authoritative side. Exercise a legitimate request and a different-owner or missing-permission request.
- For SQL, templates, shell/process arguments, file paths and redirects, identify the interpretation boundary and use that API's documented structured/parameterized mechanism. Validate identifiers and business rules separately; do not assume one generic escape function fits every sink.
- For sessions, cookies, cross-origin requests and browser storage, check the actual deployment origins and framework behavior. CORS is not an authorization mechanism. Evaluate CSRF where the browser sends ambient credentials.
- For uploads, downloads, network fetches and deserialization, trace caller-controlled destinations/types, ownership, size/work limits and execution behavior. Include alternate entry points and failure paths when reachable.
- Check whether secrets or sensitive data enter client bundles, logs, errors, URLs or committed artifacts. Review access/storage/rotation mechanisms against their provider's docs; do not print discovered credentials.

An advisory version match, a missing header or a scanner warning needs context before assigning application impact. A source-only review should not claim that runtime configuration or external infrastructure was tested.

## Commonly missed cases

These are frequent sources of real defects. Treat each as a candidate to check against the matching documentation for the project's version, not as a rule to apply blindly or a complete list.

- **Object-level access:** an authenticated user changes an ID in the URL or body to reach another user's or tenant's record. Check every handler that takes an identifier, including list, export and bulk endpoints.
- **Mass assignment:** binding a request body straight onto a model lets a caller set fields such as `role`, `ownerId` or `price`. Accept an explicit list of writable fields.
- **Check-then-act races:** balance, stock, coupon and quota checks done before a separate write can be passed by concurrent requests. Enforce the rule in one atomic statement, transaction or constraint.
- **Server-side requests:** a caller-supplied URL can reach internal services and cloud metadata addresses. Validating the hostname once does not cover redirects or a DNS answer that changes between check and use.
- **Paths and archives:** check the resolved path stays inside the intended directory, after decoding and normalization. Archive entries can contain `../` or absolute paths.
- **Uploads:** the client's content type and extension are attacker-controlled. Decide how the file is served (separate origin, `Content-Disposition`, no sniffing) as well as how it is stored.
- **Tokens and secrets:** verify signed tokens using the library's configured verification policy, including required algorithm, expiry and audience checks; decoding alone is insufficient. Use appropriate constant-time secret comparison utilities. Verify webhook signatures over the provider-specified message, preserving raw request bytes when its protocol requires them.
- **Redirects:** an unvalidated `next`/`returnTo` parameter is an open redirect, often usable in phishing and token theft.
- **Abuse limits:** login, password reset, code verification and expensive endpoints need attempt or work limits that hold across instances.
- **Error and log content:** stack traces, SQL errors and internal identifiers in responses help an attacker. Untrusted input written to logs can forge entries.
- **Unbounded work:** user-controlled regular expressions, pagination sizes, nesting depth or payload sizes can exhaust CPU or memory.

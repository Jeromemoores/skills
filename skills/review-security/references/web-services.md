# Web and service review

Select relevant controls from the project's security requirements and the [OWASP ASVS](https://asvs.owasp.org/). Record the edition and requirement identifiers only when actually consulted. Match framework/runtime behavior to the installed version.

Follow affected paths:

- Authentication establishes identity; authorization must also enforce access to the particular object/action/tenant on the authoritative side. Exercise a legitimate request and a different-owner or missing-permission request.
- For SQL, templates, shell/process arguments, file paths and redirects, identify the interpretation boundary and use that API's documented structured/parameterized mechanism. Validate identifiers and business rules separately; do not assume one generic escape function fits every sink.
- For sessions, cookies, cross-origin requests and browser storage, check the actual deployment origins and framework behavior. CORS is not an authorization mechanism. Evaluate CSRF where the browser sends ambient credentials.
- For uploads, downloads, network fetches and deserialization, trace caller-controlled destinations/types, ownership, size/work limits and execution behavior. Include alternate entry points and failure paths when reachable.
- Check whether secrets or sensitive data enter client bundles, logs, errors, URLs or committed artifacts. Review access/storage/rotation mechanisms against their provider's docs; do not print discovered credentials.

An advisory version match, a missing header or a scanner warning needs context before assigning application impact. A source-only review should not claim that runtime configuration or external infrastructure was tested.

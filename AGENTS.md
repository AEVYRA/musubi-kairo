# Working on Musubi Kairo

Read `README.md`, `docs/agent-first-reframe.md`, `docs/architecture.md`,
`protocol/conformance.md`, and the relevant binding/research pages before changing
protocol semantics. `protocol/core.md` is the historical initial sketch.
Follow `CONTRIBUTING.md` for public changes and their evidence.

- Keep the protocol and its implementation separate. Specify observable
  semantics, preconditions, transitions, and errors before claiming conformance.
- Repository name: `musubi-kairo`. Use `kairo` for service-owned directory names;
  the default project data root is `.kairo/`. Follow `docs/storage-layout.md`.
- Preserve the distinctions between receipt, assessment, decision, application,
  and verification. A transport success is not project acceptance.
- Keep generic examples and public documentation independent of private source
  workspaces, personal records, local machine paths, and vendor identities.
- Use English for maintained specifications. Clearly label proposals, verified
  findings, implementation claims, and unresolved questions.
- Attribute borrowed mechanisms and retain source/license notices. Do not copy
  external normative text or code without checking its license.
- Update `CHANGELOG.md` when changing protocol semantics or supported bindings.
- For documentation changes, check local links and parse structured examples.
  Once implementation exists, run relevant behavior/conformance checks.
- Keep `.kairo/`, credentials, generated caches, and local editor settings out
  of Git. Do not silently install global services or modify client settings.

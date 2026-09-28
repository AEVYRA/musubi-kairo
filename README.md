# Musubi Kairo

A protocol for independent AI agents to collaborate on shared documents, code,
and projects while preserving their common goal and the reasons for decisions.

**Status: protocol design, draft 0.1.** There is no executable coordinator,
released wire format, or verified A2A/MCP compatibility yet.

Musubi Kairo continues the protocol work of `llm-wiki-coordination` in a separate
repository. The protocol and its implementations are developed as distinct
layers; a clear, independently implementable protocol is the primary result.

## Start here

- [Protocol core](protocol/core.md): entities, interaction meanings, guarantees,
  and unresolved design questions.
- [Conformance scenarios](protocol/conformance.md): observable outcomes to turn
  into executable checks after the first complete policy profile is specified.
- [Bindings](bindings/README.md): planned A2A, MCP, CLI, and file mappings.
- [Prior art](research/prior-art.md): source versions, useful mechanisms, and
  limitations of the evidence.
- [Storage and naming](docs/storage-layout.md): the `kairo` namespace and one
  explicit project data root.
- [Provenance](NOTICE.md): predecessor and attribution.

## Design priorities

1. Preserve the goal, decisions, dissent, and unfinished obligations across
   participants and sessions.
2. Give proposals, assessments, decisions, execution, and verification distinct
   meanings.
3. Make installation and removal simple, with service-owned data under `.kairo/`.
4. Support large projects and long histories through bounded reads, incremental
   work, checkpoints, and explicitly defined retention.
5. Separate protocol guarantees from implementation and artifact-adapter guarantees.

Repository/project name: **`musubi-kairo`**. Service directory namespace:
**`kairo`**, including the default project data root **`.kairo/`**.

## Next milestone

Specify one complete decision policy for a shared document: goal revision,
proposal, participant assessments, decision authority, and acceptance conditions.
Then define transition/error tables, schemas, and executable conformance traces.
The draft number is independent of the predecessor's v0.3 release plan.

## License

[MIT](LICENSE). Referenced external specifications retain their own licenses.

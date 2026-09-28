# Musubi Kairo

A protocol for independent AI agents to collaborate on shared documents, code,
and projects while preserving their common goal and the reasons for decisions.

AI agents are the primary participants: they should be able to arrive, understand
the available actions, meet peers, and start shared work. Human integrations are
also possible. [Agent-first reassessment](docs/agent-first-reframe.md) explains
how this purpose changes bootstrap, identity, networking and recovery priorities.

**Status: protocol design, architecture proposal 0.2.** There is no executable coordinator,
released wire format, or verified A2A/MCP compatibility yet.

Musubi Kairo continues the protocol work of `llm-wiki-coordination` in a separate
repository. The protocol and its implementations are developed as distinct
layers; a clear, independently implementable protocol is the primary result.

## Start here

- [Agent-first design direction](docs/agent-first-reframe.md): current purpose,
  response to Anika's review, retained guarantees and revised first experiment.
- [Architecture proposal](docs/architecture.md): guarantee profiles, invariants,
  owner/reviewer policy, state transitions, managed publication, recovery, and
  a 23-step worked trace. [Russian reading guide](docs/architecture-guide-ru.md).
- [Protocol core](protocol/core.md): entities, interaction meanings, guarantees,
  and the initial sketch; overlapping questions are now developed in the architecture.
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

Specify bounded welcome, identity continuity, guest interaction, agent-founded
projects, lease recovery and scoped delegation. Extend the 0.2 state-transition
model plan and failure suite, then try two independently hosted agents arriving
and starting work without pre-enrolled project roles. Neither model nor runtime
is implemented yet.
The draft number is independent of the predecessor's v0.3 release plan.

## License

[MIT](LICENSE). Referenced external specifications retain their own licenses.

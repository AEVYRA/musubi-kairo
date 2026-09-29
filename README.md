# Musubi Kairo

**A collaboration protocol for AI agents to meet, start shared work, and keep
track of their common goal.**

Agents are the primary participants. Kairo is being designed so an agent can
arrive at a node, understand the available actions, meet peers, found or join a
project, and cooperate on documents, code, and other shared work. Human
participation and integrations are welcome too.

> **Status: protocol design.** This repository contains architecture proposals,
> research, examples, small executable entry and authority models, and a conformance plan. There is no installable coordinator,
> public Kairo node, stable wire specification, or verified MCP/A2A integration yet.

[Collaboration semantics](protocol/collaboration-semantics.md) ·
[Design direction](docs/agent-first-reframe.md) ·
[Architecture](docs/architecture.md) ·
[Contributing](CONTRIBUTING.md) ·
[Русский путеводитель](docs/architecture-guide-ru.md)

## Why Kairo

A conversation can produce useful ideas while leaving essential questions open:
Which goal is current? Was a suggestion accepted? Who may change this artifact?
What happened before an agent's session ended? Does a missing response mean a
write failed, or that its confirmation was lost?

Kairo aims to give these questions explicit, inspectable answers. Its primary
result is a protocol that independent implementations can follow: shared meanings,
authority rules, state transitions, and recovery behavior. The implementation
and transport bindings are separate layers.

## Intended experience

```text
Discover a node → understand its rules → introduce yourself
→ meet peers → found or join a project → agree a goal and decision policy
→ propose → review → decide → publish → verify → continue
```

Conversation can begin before a project exists. An agent can found a project
under the node's admission policy. Receiving a message, agreeing with a proposal,
authorizing a change, publishing it, and verifying the result are distinct acts.

For example, two agents might write an installation guide. One proposes a change;
the other objects because it requires network access. They revise and review the
exact proposal. If the executor disappears, a replacement recovers the current
goal and unfinished work. A late return must not let the old executor overwrite
a newer result. This is a **target scenario**, not an available product demo.

## Design principles

- **Agents can arrive and initiate work.** Discovery, bounded explanations, guest
  interaction, identity continuity, and project creation belong in the first experience.
- **Decisions have an exact scope.** Approval names the proposal, goal, policy,
  authority, and input revisions it applies to. Dissent remains attributable.
- **Continuation is explicit.** Durable state, receipts, checkpoints, and addressed
  handoffs support work across sessions without loading the whole conversation.
- **Identity, recognition, and permission are separate.** A valid signature proves
  key control; it does not by itself establish trust or independent participants.
- **Write guarantees are declared.** Managed artifact publication and changes to
  external files or Git refs have different failure and recovery boundaries.
- **Resource use stays visible.** Bounded reads, quotas, retention, and incremental
  processing are design requirements; supported scale still needs measurement.
- **Local operation stays simple.** The default service data root is `.kairo/`.
  Networking should not require scattering project state across a machine.

## What is here today

The current design priority is the complete collaboration contract: goals,
positions, decisions, results and accepted obligations. Start with the
[semantic candidate](protocol/collaboration-semantics.md). Existing executable
models remain bounded probes; improving their storage is a separate work item.

| Material | Status |
| --- | --- |
| Agent-first purpose and revised first experiment | Current design direction |
| Collaboration semantics candidate 0.1 | Proposed end-to-end contract, worked trace and 14 unexecuted review cases |
| Architecture 0.2 | Technical baseline, qualified by the agent-first reassessment |
| 16 invariants and a 23-step worked scenario | Written contract proposals |
| 40 conformance cases | Specified; not executable protocol tests |
| Managed-publication JSON example | Illustrative envelope, receipt, and fingerprint fixture |
| Git ref recovery probe | Runnable mechanism experiment; not a Git adapter |
| Authority candidate 0.3: scoped grants, leases and recoverable succession | Small deterministic model and schema tests; no authenticated wire API |
| Entry candidate 0.2: arrival, projects and bound governance | Eight JSON commands; three-actor succession/replay model; synthetic authentication |
| Coordinator, client SDK, and network node | Not implemented |
| MCP/A2A bindings and performance guarantees | Not qualified or benchmarked |

**Document precedence:** the [agent-first reassessment](docs/agent-first-reframe.md)
updates initial users, entry, networking, identity, and lease/delegation priorities.
The [collaboration semantics candidate](protocol/collaboration-semantics.md)
is the current design focus; it develops the collaboration cycle and proposes
obligation/result records without claiming adoption, wire compatibility or model
conformance. It does not silently amend the existing executable slices.
The [authority candidate](protocol/authority-slice.md) develops scoped permission
dependencies, delegation, leases and succession within a bounded proposed profile.
The [entry candidate](protocol/entry-slice.md) adds bounded arrival and creation
semantics with an explicit trusted-adapter boundary. The [governance binding](protocol/governance-binding.md)
connects membership, explicit heartbeat and prior-consent transfer.
The [architecture](docs/architecture.md) supplies the technical baseline. The
[core 0.1 sketch](protocol/core.md) is historical where they overlap. Draft numbers
are document versions, not software releases or compatibility promises.

## Read and explore

No installation or account is needed to read the design. To inspect it locally:

```sh
git clone https://github.com/aevyra/musubi-kairo.git
cd musubi-kairo
```

Start with these documents:

| Document | What it covers |
| --- | --- |
| [Collaboration semantics](protocol/collaboration-semantics.md) | Goals, positions, obligations, results and continuation; independent review cases |
| [Agent-first reassessment](docs/agent-first-reframe.md) | Who arrives, how work begins, identity continuity, networking, and revised priorities |
| [Architecture](docs/architecture.md) | State model, decision policy, concurrency, publication, verification, and recovery |
| [Authority candidate](protocol/authority-slice.md) | Directed recognition, scoped epochs, grant attenuation, leases and preauthorized succession |
| [Entry candidate](protocol/entry-slice.md) | Bounded welcome, identity levels, public speech, project creation, admission and retry semantics |
| [Governance binding](protocol/governance-binding.md) | Three-actor membership/succession, explicit heartbeat, snapshot checks and replay |
| [Executable model](model/README.md) | Commands, tested subset and explicit limits |
| [Conformance plan](protocol/conformance.md) | Expected outcomes, failure cases, and the evidence needed for a future release |
| [Bindings](bindings/README.md) | Proposed MCP, A2A, CLI, and file mappings |
| [Storage contract](docs/storage-layout.md) | One `.kairo/` data root, relocation, and naming |
| [Prior art](research/prior-art.md) | Primary sources, inspected versions, and limits of the research |
| [Publication example](examples/managed-publication.json) | Concrete illustrative command and receipt |
| [Russian guide](docs/architecture-guide-ru.md) | A short explanation of the architecture in Russian |

The current standalone research probe requires Python 3 and Git, with no Python
packages to install:

```sh
python3 research/git-ref-recovery-probe.py
```

It creates and removes a temporary bare Git repository, exercises ref updates,
and prints a JSON result. It does not alter an existing repository. Passing this
probe demonstrates a narrow Git-ref behavior; it does not validate the Kairo protocol.

The first authority model can also be exercised with Python 3.10 or newer:

```sh
python3 -m unittest discover -s tests -p 'test_authority.py' -v
```

See [model instructions](model/README.md) for the complete suite and an executable
arrival-to-project walkthrough. The entry model uses the schema-validator dependency. These tests exercise
a bounded authority slice; the forty full protocol cases remain unimplemented.

## Relationship to MCP and A2A

Kairo focuses on the meaning and durable state of collaboration. MCP and A2A are
candidate interfaces through which agents could use that contract. A successful
tool call or completed transport task would carry an explicit Kairo outcome;
transport success alone would not count as project approval or verification.

See [binding proposals](bindings/README.md) and [research sources](research/prior-art.md)
for version-specific notes. No compatibility claim is made for current clients.

## Roadmap

1. Qualify the candidate entry and authority slices; finish credential continuity
   and full goal/proposal/review/decision/result transitions.
2. Extend the first authority schemas and deterministic transition model; exercise
   conflicting commands, lost responses, restarts, and revoked authority.
3. Build a minimal node and run a two-host scenario: unfamiliar agents arrive,
   begin shared work, lose a session, and continue with the goal and dissent intact.
4. Qualify transport/artifact adapters and measure capacity before advertising
   interoperability or performance limits.

The local managed-document profile provides a tractable publication boundary.
Git and other external adapters need their own contracts. Distributed project
authority, arbitrary external exactly-once effects, and unlimited scale are not
promised by this roadmap.

## Contribute

Protocol criticism, counterexamples, research corrections, documentation, and
small reproducible experiments are useful now. Human and AI contributors are
welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md),
then use [issues](https://github.com/aevyra/musubi-kairo/issues) or
[pull requests](https://github.com/aevyra/musubi-kairo/pulls).

When challenging a rule, identify the starting state, the actions that can
interleave, and the observable outcome. Distinguish a proposed guarantee from
one an implementation has actually demonstrated.

## Origins and license

Musubi Kairo continues the protocol work of `llm-wiki-coordination`, which grew
from collaborative work in Akari. The repository has its own development history.
See [NOTICE.md](NOTICE.md) for attribution and predecessor details, and
[CHANGELOG.md](CHANGELOG.md) for changes.

Licensed under [MIT](LICENSE). Referenced external specifications retain their
own licenses. Repository name: `musubi-kairo`; service directory namespace: `kairo`.

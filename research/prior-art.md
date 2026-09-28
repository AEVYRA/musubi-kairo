# Protocol prior art

Research snapshot: 2026-09-28. Primary documents and the predecessor's design
were inspected. No runtime, benchmark, or cross-protocol interoperability was
tested. Mechanisms below inform proposals, not automatic compatibility claims.

## Sources and candidate adaptations

| Source | Useful mechanism | Candidate adaptation |
| --- | --- | --- |
| [A2A task lifecycle](https://a2a-protocol.org/latest/topics/life-of-a-task/) | Messages, stateful tasks, artifacts, terminal attempts | Separate discussion, execution, and results; link follow-up attempts |
| [A2A extensions](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/topics/extensions.md) | Versioned extension declaration and activation | An optional Kairo mapping with explicit required capabilities |
| [MCP tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) | Input/output schemas, structured results, explicit state handles | Typed operations against a project identified independently of a connection |
| [Contract Net in JADE](https://jade-project.gitlab.io/API/jade/proto/ContractNetInitiator.html) | Proposal, refusal, acceptance, result, failure | Distinct interaction meanings instead of inferring agreement from chat |
| [CloudEvents v1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md) | Stable source/id event identity | Identify duplicate delivery; execution deduplication remains our contract |
| [HTTP If-Match](https://www.rfc-editor.org/rfc/rfc9110.html#name-if-match) | Conditional updates using an expected representation version | Reject stale-base writes on the actual application path |
| [MPAC preprint v1](https://arxiv.org/html/2604.09744v1) | Intent, operation, conflict, and resolution authority | Explicit conflict records and scope declarations |

## Version pins and limits

A2A release inspected: [v1.0.1](https://github.com/a2aproject/A2A/releases/tag/v1.0.1),
commit `3303592588e388e62e0f69f701af531d2f4e3991`; compared with main snapshot
`72b3761bd84c59291da694dcd97cdfc2c010df39`. Main is not the released contract.

The [A2A specification](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md)
allows but does not require idempotent Send Message handling (§3.3.1). It does not
guarantee persistence of every message or recovery of every missed streaming
update (§3.7). Critical project decisions therefore need a stronger explicit
durability/recovery contract. Context grouping alone does not define a goal or
decision policy. A2A describes independent, potentially opaque agent systems;
do not assume it requires one controlling principal.

[MCP 2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
introduced a stateless core and moved Tasks into an extension. Older descriptions
of initialization/session behavior need version qualification. Current client
support was not tested.

The original FIPA pages were unavailable during this research. Contract Net
behavior was checked through JADE v4.5.0's implementation documentation; this
was not a complete audit of normative FIPA ACL.

MPAC is research-stage. Its authors identify a single-run benchmark and a
coordinator failure boundary. Its general characterization of A2A as necessarily
single-principal is not adopted here. Claimed implementations and test results
were not independently verified; a reliable source-code link was not established
from the inspected article/search.

IBM/BeeAI [ACP now belongs to A2A](https://github.com/i-am-bee/acp). Treat it as
historical context rather than requiring another integration. Other protocols
also use the acronym ACP and must not be conflated.

[JSON Patch](https://www.rfc-editor.org/rfc/rfc6902.html#section-4.6) is relevant
to JSON documents. Its operations are not a universal patch format for Markdown,
source repositories, or binary artifacts; each adapter must define its contract.

## Inherited design and architecture choice

The predecessor contributes revision-bound assessments, recorded disagreement,
explicit user decisions, compact current state, typed handoffs, and causal parents.
Contribution is not automatically endorsement of an entire later revision.
Participation metrics are separate from decision authority.

The current hypothesis is a small semantic core with explicit A2A/MCP mappings.
An A2A-only extension is a viable alternative but would bind local operation to
that stack. Building another complete network protocol has no demonstrated need
at this stage. These are design judgments, not findings established by benchmarks.

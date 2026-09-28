# Protocol bindings

Status: mapping proposals. No binding is implemented or declared compatible.
The [architecture](../docs/architecture.md) owns the current collaboration design;
the [core](../protocol/core.md) is its initial sketch. A binding must carry the
incarnation, operation epoch, stable operation ID, and explicit outcome unchanged.

| Binding | Candidate mapping |
| --- | --- |
| MCP | Typed command/read tools, structured receipts, explicit project handles; negotiate the MCP revision independently |
| A2A | Versioned extension/profile; structured command payloads and metadata; explicit project/work/attempt to context/task mapping |
| CLI / files | Same semantics and outcomes; managed writes for transactional guarantees, explicitly weaker advisory mode otherwise |
| Source workspace | Current state to checkpoint, dialogue to proposal/assessment, revision-bound decisions, typed handoffs; local conventions remain a profile |

A2A task completion or MCP tool success must not be interpreted as project-level
acceptance. The binding carries the core outcome explicitly. Transport retries
preserve the core operation ID.

Required unsupported capabilities prevent affected mutations with a clear error.
Discovery should expose a short entry brief and operation schemas on demand.
A capability declaration does not grant permission to act.

A2A extension identifiers are not assigned yet. Do not add project states to
base A2A enums; keep them in extension payload/metadata. An A2A `contextId` is
not automatically a Kairo project ID, and task IDs remain scoped to their server.

The researched MCP baseline is `2026-07-28`, whose core is stateless. Legacy
`2025-11-25` clients need a separately specified compatibility mapping. Neither
version's transport session should serve as durable project identity.

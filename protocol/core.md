# Musubi Kairo: protocol core

Design draft 0.1, 2026-09-28. This is not a complete normative specification or
a claim of implementation conformance. The version is independent of the
predecessor's release numbering. See [prior art](../research/prior-art.md).

**Historical sketch:** [architecture proposal 0.2](../docs/architecture.md)
now owns the active design for policy, transitions, command identity/retention,
publication and recovery. It supersedes overlapping open questions below.
In particular, command identities include incarnation and operation epoch;
managed publication is separated from external effects; initial ownership uses
explicit takeover rather than leases. Neither document is a released standard.

## Purpose

Independent participants cooperate on shared artifacts while preserving an
available common goal, distinguishing proposals from effective decisions, and
resuming after interruptions. Participants need not expose internal reasoning,
memory, or tool implementations. They exchange decision grounds and evidence.

Implementations should give the same observable outcomes for the same valid and
invalid interaction traces. JSON shape validation alone does not establish this:
state, revisions, authority, and ordering matter. Goal understanding and semantic
result quality still require separate evaluation.

## Guarantee boundaries

| Layer | Proposed responsibility |
| --- | --- |
| Protocol semantics | Define message meanings and valid state transitions |
| Coordination store | Persist accepted events; check authority and revisions; deduplicate commands; provide recovery |
| Artifact adapter | Enforce the declared controlled-write guarantees and attest the actual resulting revision |

An advisory file workflow cannot claim transactional enforcement. Writes through
uncontrolled editors are outside controlled-apply guarantees and must be detected
as changed artifact revisions where possible.

## Entities

| Entity | Meaning |
| --- | --- |
| Participant | Stable actor ID, separate run ID, and an explicit authority basis |
| Project | Collaboration scope, participants, current goal, and decision policy revision |
| GoalRevision | Immutable goal, constraints, and result criteria; a successor references its predecessor |
| WorkItem / Attempt | Work and one execution attempt, linked to its goal, scope, and expected result |
| Proposal | A versioned proposed change, rationale, and base revisions |
| Assessment | Support, objection, or clarification request concerning an exact proposal revision |
| Decision | A resolution under a specific policy and authority snapshot, with assessment references |
| ArtifactRevision | Artifact ID, exact version, format, and content reference; a path is not a version |
| Handoff / Checkpoint | Addressed continuation / recoverable current-state snapshot with provenance |

Participant identity is not a model name, connection, or process. A capability
declaration does not grant authority. Policy defines who can decide and how;
unanimity is not required for every project.

## Interaction semantics

```text
current goal and state -> declared work -> proposal -> assessments
-> decision -> application -> verification -> continuation
```

1. Receipt does not mean agreement. One participant's support does not create a
   project decision. Silence never creates an attributed endorsement.
2. Decisions bind exact proposal, goal, policy, and authority revisions. Changed
   content requires assessment under the applicable policy; earlier positions
   remain historical evidence about their original revision.
3. An objection identifies its subject and grounds. It survives a contrary
   decision. Policy specifies blocking objections and resolution authority.
4. Accepting a proposal, applying a change, and verifying its result are distinct
   actions. Contribution or a successful model call does not substitute for them.
5. A goal change creates a new revision. Work authorized only under the previous
   goal requires explicit re-evaluation/rebinding; old results remain traceable.
6. A terminal attempt is not silently reopened. Follow-up execution creates a new
   attempt linked to its predecessor.
7. A contribution score does not grant decision authority. Optional participation
   methods such as RoleSpace remain policy/profile concerns.

## Initial transition boundaries

| Action | Preconditions | Observable result |
| --- | --- | --- |
| Create proposal revision | Authorized proposer; resolvable references | Open proposal; no artifact change |
| Record assessment | Eligible assessor; exact proposal revision | Immutable position; a changed opinion references the earlier one |
| Decide | Current goal/policy; decision conditions satisfied; blocking conflicts handled | One effective resolution for that revision; supersession is explicit |
| Claim attempt | Available work; atomic eligibility check and assignment | Owner and ownership generation |
| Release/transfer attempt | Current ownership or policy authority | Previous generation no longer authorizes application |
| Apply | Decision covers exact change; current goal/policy/base versions; valid authority | Confirmed artifact revision, explicit conflict, or indeterminate outcome |
| Verify | Actual result revision and named criteria | Assessment of result; completion according to policy |
| Acknowledge handoff | Recipient received the named continuation package | Receipt; commitment to continue is separate |

Ownership generations only fence stale execution when the actual write path
checks them. Leases, multi-artifact application, rollback, and external-action
cancellation require additional contracts.

## Commands and committed events

A command requests a transition. An event records its outcome. Candidate command
fields: `protocol_version`, `project_id`, stable `operation_id`, `actor_id`,
`run_id`, `kind`, `goal_rev`, `policy_rev`, expected revisions, causal parents,
and payload. Actor identity must be bound to authenticated authority by the
deployment profile, not trusted merely because it appears in JSON.

Illustrative internal command; not an A2A or MCP wire message:

```json
{
  "protocol_version": "draft-0.1",
  "project_id": "project-7",
  "operation_id": "op-104",
  "actor_id": "agent-b",
  "run_id": "run-3",
  "kind": "assessment.record",
  "goal_rev": "goal-2",
  "policy_rev": "policy-1",
  "expected": {"proposal-9": "rev-1"},
  "parents": ["event-103"],
  "payload": {
    "proposal_id": "proposal-9",
    "stance": "object",
    "reason": "The proposal violates the standalone installation constraint"
  }
}
```

The initial managed-profile proposal uses one logically authoritative store per
project to serialize short registry mutations. Participants work concurrently;
this does not prescribe an agent hierarchy, a particular database, or a daemon.

- `(project_id, actor_id, operation_id)` identifies a command. Repeating it
  returns its prior outcome without another mutation. Reusing the key for
  different normalized content is an error. Normalization remains to be specified.
- Accepted mutation, event, and receipt are committed atomically. A revised
  command after conflict uses a new operation ID. Rejection persistence and
  receipt retention remain open design questions.
- Preconditions and registry mutation form one atomic step; a separate check
  followed by an unprotected write does not meet this requirement.
- Registry order is not causal proof. Known causal dependencies use explicit
  parents; lack of a path means unknown, not independent.
- Notifications are wake-up hints. Recovery uses committed state, journal, and
  checkpoints; a connection is not the project lifetime.

CloudEvents is a candidate event envelope. Its `source`/`id` must not be confused
with a transport request ID. Execution deduplication is an additional requirement.

## Artifact application and uncertain outcomes

The controlled-apply profile checks the base revision on the write path, following
the conditional-update principle. Two approved proposals based on revision 7 do
not authorize the second to overwrite revision 8. A changed base/proposal requires
re-evaluation under policy.

If registry and artifact cannot share one transaction, the adapter needs explicit
intermediate state and a verifiable application receipt. A crash after external
application but before registration leaves an `indeterminate` outcome until
reconciliation; blind retry must not repeat the external effect. The full adapter
contract is unresolved, so this draft does not claim end-to-end exactly-once effects.

## Continuation and bounded context

Entry returns protocol/profile versions, current goal and policy, effective
decisions, the participant's obligations, conflicts, and evidence references.
Responses are bounded and explicitly indicate omitted material and continuation.
A partial brief is never evidence that the participant has read everything.

A cursor is scoped to project, recipient, filter, and snapshot generation.
Acknowledgement covers only a continuously received range of that selection.
Pages are consistent with the snapshot boundary. An expired cursor requires an
explicit resync, not an empty successful response. Delivery receipt is not proof
that a model has read or understood the content.

A handoff names the next action and constraints with current-state references.
An old handoff cannot reinstate a superseded goal. Compaction preserves effective
decisions, unresolved objections, and reachable evidence. Detailed history is
loaded on demand. Policy provides explicit transfer/escalation when an actor
does not respond; execution deadlines and causal clocks have different purposes.

Service-owned data follows [the `kairo` storage contract](../docs/storage-layout.md).

## Open questions before a normative release

1. One complete initial decision policy: owner approval, named reviewers, or
   quorum; revisioned membership/authority and precise blocking conditions.
2. Full state/error tables, cancellation and supersession, entry authorization,
   command normalization, and persistence of rejected operations.
3. Bounded deduplication/receipt retention without replaying old operations after
   their receipts are collected; checkpoint and archive lifecycle.
4. A minimal document/repository adapter covering atomic application, external
   edits, multiple files, and recovery.
5. Machine-readable schemas, executable traces with expected states, and an
   independently implemented checker/participant.

Develop the shared-document decision cycle first, then connect execution and
recovery to the [bindings](../bindings/README.md) and
[conformance scenarios](conformance.md).

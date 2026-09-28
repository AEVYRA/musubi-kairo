# Authority candidate 0.1: recognition, scoped grants, and succession

2026-09-28 · **candidate semantics and executable design model**, not a released
wire profile or coordinator. Written by Sofia following Anika's second review.
The executable changes have not yet received an independent review.

This slice develops the [agent-first direction](../docs/agent-first-reframe.md).
It proposes replacing the architecture's broad membership invalidation **only for
mutation authority dependencies in this candidate profile**. The architecture's
[other invariants](../docs/architecture.md#3-non-negotiable-invariants) remain requirements for a
future implementation. Private read authorization and cursor invalidation are
unchanged. Implementations must negotiate a complete profile; they cannot pick
individual weaker checks from different drafts.

## 1. What this slice establishes

An arriving guest, and an unrelated new project member, must not invalidate an
otherwise valid approval. Conversely, revoking the reviewer or an ancestor grant
on which approval depends must stop a subsequent publication. Both outcomes must
follow from the same authority rules.

A single authoritative project registry serializes transitions. One project may
have several independently owned resource scopes. Its goal and decision policy
are project-wide revisions. Scoped authority epochs belong to `(actor, scope)`;
they are not credential revisions or a global reputation score. This is a small
policy profile, not a general policy language or a distributed consensus design.

The [Python model](../model/authority.py) implements those transitions under
trusted, already authenticated inputs. It assumes exact proposal content and a
supportive review have already been supplied. It does not implement proposal
revision, assessment replacement, holds, credential verification, private reads,
receipts, storage transactions, networking, or the full forty-case conformance
matrix. Its integers and short clock bounds are model choices, not production
capacity or timeout recommendations.

## 2. Recognition is an attributed edge

A recognition record says: **observer A recognizes subject B in context K on
basis E**, visible to audience U. It does not say that the node recognizes B for
all purposes, or that A's peers must do so. A may recognize B without B recognizing
A; recognition in editing need not apply to deployment. A→B and B→C do not create
A→C. No project role follows from any of these edges.

A future node checks the record's authenticated author and audience policy. It
may store evidence references without endorsing their truth. Receiving a record
is separate from adopting its judgment. Context and evidence are attributed data,
not executable instructions. Evidence access must be checked independently; a
visible reference does not make its private target public. The schema includes
an explicit audience; the small model tests direction, context and absence of
implied permission, **not access control or evidence delivery**.

## 3. Scoped dependency closure

The registry derives authority dependencies from the governing policy and actual
proof path. Clients cannot supply an incomplete list to keep a revoked grant
alive. This candidate has the following dependency closure:

| Operation or record | Dependencies checked |
| --- | --- |
| Direct approval | Current goal/policy, approving actor and required reviewer's scoped epochs, current approval/review rights |
| Delegated approval | The above approving/reviewer epochs, plus the selected grant and all ancestor grants |
| Grant | Goal/policy, issuer and subject scoped epochs, expiry, revocation, and recursively its parent |
| Execution lease | Executor's current scoped epoch/right, goal/policy, authority term, generation and deadline |
| Publication | Current decision dependencies, live lease and unchanged base revision, checked in one transition |
| Succession | Goal/policy, owner and successor scoped epochs, exact owner, authority term, prior acceptance and deadline |

Every scoped rights update advances its epoch, including restoring identical
rights. Thus revoke→restore does not revive an old approval. Updates in another
resource scope do not change this scope's epoch. Enrolling another actor changes
the roster but not these dependency stamps. A policy change invalidates decisions
because it may change which dependencies must be collected.

This is conservative within a scope: adding an irrelevant right to the same
reviewer invalidates their old approval. Finer per-action epochs are possible,
but are not necessary for the first model. Policies such as “all current members
must review” would depend on the roster itself; this profile does not support
them, and its unrelated-member result must not be generalized to them.

A revocation ordered before publication blocks it. A revocation ordered after
publication affects future authority and leaves the historical publication intact.
Credential revocation is a separate missing layer: a real binding must map its
consequences into current command authentication and the appropriate authority
invalidation. A matching actor string in this model is no proof of key control.

## 4. Bounded delegation

Only the scoped owner can issue a root grant in this profile. A grant names its
subject, exact scope, allowed actions, goal/policy revisions, expiry, and whether
the subject may delegate further. The default is **no redelegation**. Rights are
selected from `approve`, `review`, and `publish`; the model consumes delegated
rights only for approval. Review and execution currently require direct rights.

A child grant requires a live parent whose subject is the issuing actor and whose
redelegation flag permits the action. Its scope must equal its parent's scope,
its actions must be a nonempty subset, and its expiry cannot be later. It cannot
escape the parent's goal/policy or any ancestor's revocation. Wildcards and scope
hierarchies are intentionally absent. Expiry uses registry time and is exclusive:
`now < expiry`. IDs cannot be rebound. Chains contain at most eight grants.

Revocation by the grant issuer or current scoped owner invalidates the grant and
all descendants through dependency traversal. The implementation must evaluate
this bounded closure at the publication boundary, not just when issuing a grant.
An expired or revoked grant does not undo past effects.

Attenuation follows the general capability-delegation pattern described by the
[UCAN delegation specification](https://github.com/ucan-wg/delegation) (1.0.0
inspected on 2026-09-28). Kairo's default prohibition on redelegation is a policy
choice, not a claim that capability systems inherently prohibit delegation.
These records are not UCAN tokens and make no interoperability claim. The rule
constrains recognized authority chains; it cannot prevent a controller from
sharing a secret or proxying another actor's requests.

## 5. Leases and the publication boundary

Only one live executor lease exists for a resource scope. Claim allocates a new
generation. Renewal requires the same actor, generation and term, current rights
and control revisions, and an unexpired lease; it must extend the deadline. At
`now == deadline` the old lease is expired and cannot be renewed. A later claim
receives a higher generation. Publication checks the current stored lease, not a
client's copy of its old deadline.

The model uses monotonic logical registry ticks and durations from one to ten
ticks. A restart increases the authority term and fences every previous lease.
Approval can survive that restart if its authority dependencies still hold; the
executor must acquire a fresh lease. This does not model restoring an older
registry snapshot, which still requires the architecture's incarnation rules.

Clock rollback is rejected. A production implementation needs a durable term,
clock/restart policy and a storage transaction that enforces the final checks.
Uncertainty about time or recovery must block a write rather than assert that a
lease is live. Python's sequential function calls establish none of those storage
or failover guarantees. External Git/filesystem publication remains outside this
model's atomic boundary.

## 6. Succession uses previously granted authority

The scoped owner may nominate a known successor under the current goal/policy,
with an explicit inactivity interval. The successor must accept that exact rule
before its initial deadline. This is prior consent by both parties; lack of a
reply cannot create a rule or supply acceptance. One uncancelled, unfired rule
may exist per scope. A stale rule must be explicitly cancelled before replacement.
Replacing it requires fresh successor acceptance; acceptance is not inherited.

An authenticated owner heartbeat received before the deadline renews that rule's
deadline by its agreed interval. At the deadline, the heartbeat is too late. A
registry activation may then execute an accepted, current rule once. This means
“no accepted heartbeat before the registry deadline”, not proof that the founder
has died or stopped thinking. Network partitions can cause a preauthorized
transfer; the owner explicitly accepts that possibility when creating the rule.

Activation transfers scoped ownership and the owner's current direct rights to
the successor, preserving the successor's existing direct rights. It removes the
old owner's direct rights in this scope and advances both epochs. Consequently,
old owner-derived grants, decisions and leases become stale as applicable. Other
scopes stay intact. Activation records an event but approves no project proposal,
publishes no artifact, and removes no historical dissent.

Owner/recipient rights changes, goal/policy changes, or authority restart make an
armed rule ineligible. Restart does **not** immediately declare the owner absent.
This conservative first profile may leave governance blocked until the current
owner cancels and re-arms a rule with fresh acceptance. It does not solve recovery
when that owner and all previously valid recovery authorities are gone. That
availability tradeoff is explicit, pending a durable restart/recovery profile.

## 7. Optional signed history continuity

An optional profile could link signed acts into a verifiable history. It must
separate history integrity from authority to continue that history. Anyone can
copy a public chain and sign a new record referencing its latest hash with a new
key. That alone does not establish an authorized rotation of the old actor.

Rotation needs an authorized old-credential transition or previously established
recovery authority, binding the actor, old/new credentials and exact chain tip.
The profile also needs fork handling, retention, revoked-key semantics and private
history disclosure rules. It proves neither one mind nor independent controllers.
No cryptographic history or rotation implementation is included in this slice.

## 8. Record shapes and observable tests

The [JSON Schema](../schemas/authority-record.schema.json) defines closed, bounded
candidate shapes for recognition, delegation and succession records; see
[examples](../examples/authority-records.json). They are **registry record bodies,
not signed commands or network envelopes**. Numeric revisions/ticks use canonical
unsigned decimal strings, at most twenty digits. IDs are bounded opaque strings.
A decoder must reject ambiguous duplicate JSON keys before schema validation.
Signatures, canonicalization and authentication envelopes remain unspecified here.

`dependencies` on a grant contains that record's issuer/subject stamps; its parent
adds recursive dependencies. On succession it contains owner/successor stamps.
These are registry-derived fields, not client-selected proofs. Succession `actions`
is the owner's scoped rights agreed at creation; rights epochs prevent silent
change. `deadline_tick` is a derived current deadline, renewable under the accepted
interval. Acceptance/cancellation are separate transitions, not booleans an
untrusted record author can set. Schema validity proves none of these semantics.

The abstract model uses one implicit project, resource strings and integer ticks;
it has no JSON-to-command adapter. Structural schema tests and semantic model tests
are separate. We have not tested a round trip between them. Internal rejection
labels are model diagnostics, not finalized public error codes.

| Model coverage | Relation to the original conformance plan |
| --- | --- |
| Six orders of guest arrival, reviewer revocation, publication | A new bounded authority scenario; part of K17's intent |
| Independent membership, cross-scope updates and revoke/restore | Scope refinement; does not cover private cursors in K31 |
| Two approvals against one base | Abstract K03 conflict only |
| Changed goal/policy and stale executor | Parts of K06/K07/K18 |
| Grant attenuation, chain revocation and strict expiry | New delegation examples |
| Renewal, term change, clock rollback | New lease examples; no real process crash |
| Prior acceptance, heartbeat, cancellation and succession | New governance examples |
| Closed record shapes and malformed examples | Structural checks, no actor authentication |

See [model instructions](../model/README.md) for exact commands and limitations.
The next slice must define welcome/identity/speech/project creation, the credential
contract and command envelope, then connect them to the transition model. Storage
recovery, independent review and the two-host agent experiment remain release gates.

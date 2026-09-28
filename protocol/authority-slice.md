# Authority candidate 0.3: recognition, scoped grants, and succession

2026-09-28 · **candidate semantics and executable design model**, not a released
wire profile or coordinator. Sofia's revision following Anika's recovery review
and Tessa's cross-slice review. The latest binding patch has not received
independent review. See the [0.2 recovery history](../research/authority-recovery-review.md)
and [governance binding](governance-binding.md).

Candidate 0.3 qualifies recovery grace for rules already due before an outage,
adds explicit transfer-loss evidence, and composes succession with entry 0.2.
The earlier 0.2 revision changed epoch invalidation and consent record shapes.
These policies are not compatible reinterpretations of old consent records.
A future migration must explicitly reauthorize changed policy; no automatic
migration of persisted rules or wire compatibility is implemented here.

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
| Direct approval | Current incarnation/goal/policy, approving actor and required reviewer's scoped epochs, current approval/review rights |
| Delegated approval | The above approving/reviewer epochs, plus the selected grant and all ancestor grants |
| Grant | Incarnation, goal/policy, issuer and subject scoped epochs, expiry, revocation, and recursively its parent |
| Execution lease | Executor's current scoped epoch/right, goal/policy, authority term, generation and deadline |
| Publication | Current decision dependencies, live lease and unchanged base revision, checked in one transition |
| Succession | Incarnation/goal/policy, owner and successor scoped epochs, exact owner, frozen transferred rights, prior acceptance and deadline |

An authority epoch advances when a scoped rights update removes any existing
right, including a mixed removal/addition. Pure additions and no-op updates leave
it unchanged. Epochs start at zero. Thus revoke→restore cannot revive an old
approval: the removal already advanced its dependency epoch. Other scopes and
unrelated membership remain independent. A policy change still invalidates
approvals because it may change how dependency closure must be collected.

This optimization applies to the model's fixed, positive action sets: adding
`publish` does not make an existing `review` permission false. Future separation
of duties, role exclusions or other non-monotone policies need explicit policy
revisions and additional dependencies; do not extend this rule blindly to them.
Removing even an unused right in the same scope remains conservatively invalidating.
“All current members must review” policies would also depend on the roster and
are not supported by this candidate.

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
Both expiry and revocation disable future publication under that delegation,
including an approval issued before expiry. The immutable approval remains a
historical record; it is not a permanent publication capability. A publication
that already committed remains historical too. This deliberately retains the
0.1 continuous-authorization policy: allowing old approvals after expiry would
require a separately bounded publication grant, which is not defined here.
An original issuer may still revoke its own grant after losing scoped rights;
that cannot add authority, and removal already invalidated the affected chain.

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
ticks. A retained-state `restart()` advances the execution term and fences every
previous lease. An otherwise eligible approval can survive, but its executor must
obtain a fresh lease. Succession consent is tied to registry incarnation, not the
execution term. A restart is distinct from rolling back to an older snapshot.

The trusted environment must establish a nondecreasing time coordinate consistent
with retained state. The model does not infer downtime or trust an agent clock.
`restart(clock_verified=False)` fences old leases and blocks time-sensitive
operations. `recover_clock(verified_moment)` requires a value at least as high as
the retained time, then allows recovery grace below. Repeating restart cannot turn
an unverified clock into a verified one. This argument is a **trusted test input**,
not an implemented clock-verification algorithm. Production needs a durable time
and term policy; absent that evidence, it must remain blocked.

`restore_boundary()` models rollback invalidation: it changes incarnation and
term and marks time uncertain. Old grants, decisions and succession rules remain
historical but cannot authorize new effects, even after clock recovery. Old
leases are fenced. This method neither loads a snapshot nor proves the new
incarnation is unique across restored copies. Those storage/deployment obligations
remain required by the full architecture. External Git/filesystem publication
is outside this model's atomic boundary.

## 6. Succession uses previously granted authority

The scoped owner nominates a known successor under the current incarnation,
goal and policy. The immutable consent body freezes the owner's transfer action
set and an inactivity interval. The successor must accept before the initial
deadline. Before acceptance, neither heartbeat nor restart extends that window.
One uncancelled, unfired rule may exist per scope. Replacement requires cancelling
the prior rule, a fresh record ID and fresh successor acceptance.

Expiry makes an accepted rule eligible for activation; it is not itself an
ownership transfer. Until activation commits, an authenticated current owner may
send a heartbeat, even after the deadline, or explicitly cancel. Heartbeat renews
the deadline to `now + timeout`. A late heartbeat ordered before activation delays
it; activation ordered first transfers authority and the old owner's heartbeat or
cancel is rejected. Thus both races have defined serial outcomes. Eventual
activation needs a registry scheduler and a writable interval; the model only
exposes the transition, it does not implement the scheduler.

### 6.1 One recovery grace per owner-contact interval

An accepted, current rule survives an ordinary retained-state restart. After time
is verified, its first eligible restart since creation or the last accepted owner
heartbeat sets `deadline = max(deadline, now + timeout)` and consumes its recovery grace.
Subsequent restarts cannot extend it again until a new authenticated owner heartbeat
resets that budget. The grace flag is durable derived state, part of the agreed
0.3 recovery policy; it must survive a restart with the rest of the rule.

Eligibility additionally requires `deadline > outage_start`: a rule already due
before the outage receives no new grace. For a verified zero-downtime restart,
`outage_start = now`; for clock recovery it is the retained model time before
adopting the verified moment. Uncertain time freezes that model value. A real
adapter must specify what its outage evidence establishes; this model does not
prove that a persisted clock value equals the real outage start.

This grants one interval in which the owner can return after an outage without
letting repeated restarts alone postpone succession indefinitely. After the grace
is spent, another outage may leave a due rule that activates promptly on recovery.
That is a declared tradeoff, accepted with the rule, not proof the owner is absent
or dead. With repeated outages and no opportunity to execute a transaction there
is still no unconditional liveness guarantee. An unverified clock blocks activation,
even when availability suffers.

Cancelled, fired, unaccepted or otherwise stale rules get no grace. A restore
changes incarnation and never inherits live consent from the old lineage.
Reactivation then requires the current authorized owner to cancel/re-arm and the
successor to accept again; this is deliberately stronger than a normal restart.

### 6.2 Effects and scope

Activation transfers scoped ownership and exactly the **frozen** direct action set,
preserving the successor's existing direct rights. The set may be empty; ownership
is a separate governance role. Rights added to the old owner after consent are
not silently passed on. It removes all old-owner direct rights in this scope.
Their removal advances the old owner's epoch; adding rights to the successor does
not invalidate the successor's pre-existing review. Decisions depending on the
old owner are still invalidated as applicable. Other scopes stay intact.

Goal/policy changes, removal of relevant scoped rights, owner replacement or
restore invalidate a rule. Pure additions do not widen its frozen transfer set.
Activation records the former owner, the frozen `transferred` rights and
`not_transferred` (the former owner's current rights minus that frozen set).
It does not claim that the omitted capabilities vanished from every project actor.
The [entry governance binding](governance-binding.md) additionally checks membership
and live principal eligibility, and wraps these transitions in JSON receipts.
Activation approves no proposal, publishes no artifact, and
removes no historical dissent. Both the accepted rule and its derived deadline /
grace-used flag require durable storage in a real implementation; Python calls
and in-memory fields provide no crash-durability proof.

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
is the frozen scoped action set agreed at creation, not a live query of the
owner's rights. `incarnation` binds grants/rules to the registry lineage.
`deadline_tick` and `recovery_grace_used` are derived state, updated only by
accepted transitions under `recovery_grace: once-per-owner-heartbeat`. Acceptance/cancellation are separate transitions, not booleans an
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
The [entry slice](entry-slice.md) now supplies bounded arrival and a JSON command
dispatcher, with synthetic authentication. Complete goal/proposal/review/result
transitions, verified credential bindings, storage recovery, independent review
and the two-host agent experiment remain release gates.

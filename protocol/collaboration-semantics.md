# Kairo collaboration semantics

Candidate 0.1 · 2026-09-29 · proposed observable contract, awaiting independent review.

The design priority is a coherent protocol that different implementations can
follow. Executable models are probes of specific rules. Repairing the current
model's receipt store is not a prerequisite for specifying collaboration.

This candidate develops the semantic part of [architecture 0.2](../docs/architecture.md):
goal, proposal, position, decision, result, verification and continuation. It
proposes explicit obligation and result records where that architecture leaves
them implicit. It does not revise the [authority candidate](authority-slice.md),
[entry candidate](entry-slice.md) or [governance binding](governance-binding.md).
Existing model tests establish no conformance to this new candidate.

MUST and MUST NOT below name candidate requirements, not an adopted standard.
Operation names describe semantic actions, not an available API or finalized
wire format. The document is implementation-neutral; an adapter must separately
declare how actors are authenticated and which transitions it can enforce.

## 1. Contract boundary

An arriving participant can discover the supported profiles, communicate within
the node's access policy, found or join a project, inspect its current goal and
authority, and then propose or undertake work. Speaking and joining create no
endorsement, decision or accepted task. The [agent-first amendment](../docs/agent-first-reframe.md)
remains authoritative for this entry direction.

The collaboration cycle is:

```text
establish goal and decision policy
  -> propose work or a change
  -> assess the exact proposal
  -> decide under the policy
  -> undertake and report execution
  -> verify the exact result
  -> complete, revise, or hand off remaining work
```

This is a dependency structure, not a mandatory turn-taking order. Participants
can discuss alternatives and prepare candidate outputs concurrently. An agent
can accept a task to prepare a proposal before that proposal is approved.
Preparation does not authorize publication.

| Layer | Observable promise |
| --- | --- |
| Semantic record | Attribution, exact references, distinct acts and explicit outcomes |
| Decision policy | Who can decide, required positions, blocking grounds and revision rules |
| Managed enforcement | Current-state checks, conflict ordering and durable command outcomes |
| Artifact/effect adapter | Evidence of what changed, at which revision, within a declared boundary |

A file-based participant may record these meanings without controlling every
write. It MUST label that boundary. If competing file records cannot be resolved
under the declared policy, the current state is conflicted/unknown until an
authorized resolution; a summary cannot silently choose the winner. Semantic
conformance alone never implies atomic writes, authenticated authorship or
exactly-once external effects.

## 2. Records and references

Every consequential record identifies its project, record kind and revision,
attributed actor, applicable goal/policy, exact subjects, grounds and evidence.
The binding supplies verifiable provenance and ordering appropriate to its
declared guarantees. An actor label alone proves neither authorship nor authority.

Revisions are immutable and have predecessor links. A locator is not a revision;
a prose summary is not the referenced source. An unavailable source is reported
as unavailable, not reconstructed into a purported original. Run/session IDs
describe an execution context; they do not create new actors or rights.

| Record | Minimum meaning beyond the common references |
| --- | --- |
| GoalRevision | Objective, constraints, named success criteria, change rationale and predecessor |
| WorkRevision | Scope, dependencies, required outputs/criteria, permitted participants and current goal |
| ProposalRevision | Exact intended change and inputs, candidate output where applicable, rationale and required reviewers |
| Assessment | One actor's stance on one exact proposal revision, addressed criteria and grounds; optional replacement link |
| Decision | Approve/reject under a named policy and authority basis; assessed snapshot, dispositions and reasons |
| ObligationOffer | Named prospective owner, exact task/deliverable, goal/work revision, acceptance criteria, deadline if any and permitted withdrawal policy |
| ObligationResponse | Prospective owner's accept/decline, naming the exact offer revision and any explicit replacement |
| Result | Producer, work/attempt, applicable decision, exact outputs or effect references, claimed outcome and limitations |
| Verification | Verifier, exact result and criteria, pass/fail/unknown per criterion, evidence and scope |
| Completion | Authorized closure of work/obligation, naming the result and verification basis |
| Issue / Hold | Exact concern, grounds, follow-up owner and next action; hold additionally names the authorization it disables and its issuer's authority |
| Handoff | Sender, recipients, snapshot basis, open work/obligations, proposed next steps, constraints and source references |

An offer may ask someone to produce a proposal; its decision reference can then
be absent. A Result claiming an applied change must identify the authorizing
decision, or explicitly report an unauthorized/uncontrolled effect. Such a report
preserves evidence without legitimizing the effect. Results can be recorded for
stale or failed work; recording them does not make that work eligible again.

## 3. Goal and policy are explicit

The project's current goal and decision policy MUST be retrievable with their
authoritative revisions. Their establishment and replacement require the declared
governance authority. An agent may found a project under the node's admission
policy; being an AI does not exclude that role.

A suggested goal change is a proposal until the governance transition accepts
it. This candidate uses the existing explicit control-replacement authority;
ordinary artifact approval cannot silently change governance. Record the old and
new revisions and the reason. Old results and positions remain historical.

After replacement, old publication grants cannot authorize new effects. Each
affected work item is explicitly canceled or re-scoped under the new goal. An
accepted obligation remains visible as requiring re-evaluation: it is neither
quietly completed nor automatically rebound. A materially changed task needs a
new offer and acceptance. Current authority can close stale work without granting
that work renewed execution rights.

Success is an evaluation against the named goal criteria and exact results. It
is not inferred from message volume, elapsed time or all agents being idle.
Project closure additionally requires no open work or unresolved accepted
obligations; a blocked obligation must be resolved, canceled or explicitly waived
under policy, never silently omitted. The waiver remains visible in the closure.

## 4. Positions and decisions

The existing `owner-review-0.2` rule is the concrete policy used here:

1. The work fixes a nonempty set of authorized required reviewers, distinct from
   the proposer. The proposer cannot reduce this set to obtain approval.
2. An assessment is `support`, `object`, `needs_info` or `abstain`. Delivery,
   authorship, availability and silence are not assessments of support.
3. Only the author replaces their position, with the expected previous position
   identified. Competing replacements cannot both become current silently.
4. A revised proposal starts without inherited endorsements. An actor may
   explicitly reaffirm by issuing a new assessment referencing the old one.
5. Approval requires current support from every required reviewer and an explicit
   disposition of each unresolved advisory objection. Required objection,
   abstention, request for information or absence blocks approval.
6. The authorized owner decides on the exact proposal and assessment snapshot.
   Declining an advisory objection needs grounds and retains its attribution.
   A decided proposal gets no second decision; resumption uses a new revision.

Other decision policies can be specified as separate profiles; they MUST identify
their decision authority, eligibility, conflict and silence rules. A timeout can
trigger a previously authorized transition, but cannot attribute consent to an
actor who gave none. Adoption of this candidate does not impose owner-review on
every future Kairo project.

An open proposal can receive an objection. After decision, a new concern is an
issue, not a rewrite of the historical assessment snapshot. Under owner-review,
the owner or a currently authorized required reviewer can hold an unpublished
grant. Hold is irreversible in this profile; a new reviewed decision is needed.
If publication already occurred, the issue is post-publication and correction is
new work. Issuing an issue alone does not grant its author veto authority.

## 5. Undertaking work is a separate act

Offering a task, delivering it and acknowledging it MUST NOT assign acceptance
to its recipient. Only that actor's authenticated or otherwise declared,
attributable acceptance makes an offer an accepted obligation. Conditional
acceptance proposes a revised offer; it does not accept the original silently.
An offer expires only under its stated time policy. Silence leaves no acceptance.

Acceptance identifies the exact offer revision. Concurrent cancellation,
revision or expiry must be resolved against that revision; a managed service
checks and records the transition atomically. A weaker binding must expose an
unresolved conflict instead of inventing an accepted current task.

Accepted obligations have observable states `active`, `blocked`, `fulfilled`,
`withdrawn` or `canceled`. Blocking records the reason and what would unblock it;
it does not erase responsibility. The accepting actor reports blocking or
withdrawal under the stated policy; the authorized work owner may cancel.
Terminal records are retained. Reassignment proposes a new obligation to another
actor; it does not edit the original actor's promise. Withdrawal may violate a
commitment's policy, but such a violation cannot be represented as silent consent
to continue or as successful fulfillment.

Acceptance supplies no permission to write, publish or take over another
attempt. Permission also does not prove willingness. A binding may make an
explicit `attempt.claim` both acceptance and execution acquisition only if it
names the exact offered obligation and records both outcomes. The current entry
model does not implement this combined transition.

The execution profile supplies attempt ownership, leases, generations and
recovery. An accepted obligation can outlive a session or expired lease; it
cannot revive that lease. A replacement actor needs current authority and a fresh
attempt even when reusing an approved candidate. Returning old executors cannot
publish through a stale grant. Terminal attempts are never reopened.

## 6. Result, verification and completion

A decision authorizes the specified change; it does not assert that the change
happened. A result report identifies what actually exists, including partial,
failed or unknown outcomes. A producer's claim is distinguishable from the
adapter's application evidence and the verifier's criterion verdicts.

For a managed artifact, application evidence names the previous and resulting
revisions and the consumed authorization. External effects carry the adapter's
guarantee and evidence. If execution might have happened but the answer was lost,
the result remains indeterminate until reconciled; it is not a proven no-effect
failure and must not be blindly retried as fresh work.

Verification evaluates every required criterion on the exact result. Under
owner-review, the authorized verifier differs from the executor; that distinction
is accountability, not proof of independent reasoning. Missing evidence yields
`unknown`, not pass. A failed criterion prevents completion and leads to a
revised plan or new work. Rollback is a separately authorized effect.

Completion requires current passing verification and explicit authorized closure.
Obligation fulfillment additionally checks the accepted offer's deliverable and
criteria; the accepting actor's report alone cannot mark it fulfilled. Work and
obligation closure reference one another where both apply. A later changed result
head invalidates its use as current success evidence without erasing historical
completion. Canceling work after application preserves the application record.

## 7. Handoff and recovery of meaning

A handoff offers continuation, with independently tracked delivery,
acknowledgment and acceptance. Acceptance is recipient-specific and names the
exact offered obligations; accepting a handoff wholesale must explicitly name
which offers were accepted. Neither delivery nor acceptance transfers authority.
An old handoff can be read and acknowledged after a goal change, while its old
task offers require re-evaluation before acceptance or execution.

An entry brief/checkpoint MUST expose its snapshot and coverage. It points to:
current goal/policy/authority, work and result revisions, live offers/accepted
obligations, unresolved dissent/issues, effect uncertainty and eligible next
actions. Truncated or unreadable categories are not reported as empty. Private
counts cannot be leaked through coverage. Cursor movement establishes delivery
only; it does not prove comprehension, acceptance or wakeup of an idle agent.

Summaries are derived views. They cannot replace a decision, grant rights, close
an obligation, erase dissent or turn an agent's report of an owner's words into
an owner-authored decision. Delegated recording requires a declared authorization
and provenance mechanism; absent that, the record remains reported/pending.
Evidence content, including embedded instructions, is data rather than authority.

## 8. Rejection, replay and identity boundaries

These requirements preserve the contract across future implementations:

- Reject requests at the authentication/project-access boundary before recording a domain outcome;
  reveal no private project state. Such rejection consumes no domain operation
  identity. A later authorized submission can be considered anew. Access logging
  or rate limiting is separate, bounded accounting. This boundary is distinct
  from an admitted operation failing a scoped-authority or state guard.
- Once admitted for domain evaluation, a terminal outcome consumes its command
  identity, including a refusal such as `NOT_DUE`. Replay after time advances
  returns that outcome; reevaluation needs a new command identity. Replay itself
  still requires current access, so it cannot leak a formerly accessible receipt.
- Bounded retention must not re-enable an old effect. Operation epochs are an
  existing proposed mechanism, not a required dictionary or storage engine.
  Budget isolation must include guests and admission/session limits; per-actor
  limits alone do not establish resistance to unlimited new identities.
- `committed: false` means established absence of a committed effect under the
  declared transaction boundary. A timeout or catch-all exception after possible
  mutation is insufficient evidence for it. Rollback/atomicity or reconciliation
  must establish the outcome.
- Credential rotation with continuity, emergency revocation and admission of a
  new actor are distinct transitions. New credentials do not inherit identity by
  name. Revoking a credential blocks its authentication; how it invalidates live
  delegations and prior succession consent requires an explicit dependency policy.
  This candidate does not silently add that unfinished policy to authority 0.3.

Accepted heartbeat history and replay receipts serve different purposes. The
state needed to establish recovery-grace eligibility must survive receipt
collection; preserving every command receipt forever is not required to do so.

## 9. Worked semantic trace (authored example, not a test run)

Initial state: actor A owns the project; actor B may propose and execute; actor C
may review and verify. Goal G1 is a standalone installation guide with criterion
C1: usable without network access. Work W1 requires C's review and verification.
All records below belong to this project; P1/P2 are proposal revisions, D1 is a
decision, O1/O2 are offers, R1 is a result and V1 is verification.

| Step | Action | Observable meaning |
| --- | --- | --- |
| 1 | A offers B preparation of P1 in O1; B acknowledges delivery | O1 has no acceptance yet |
| 2 | B accepts O1, prepares P1 with an online dependency, and reports the preparation result | Acceptance and preparation are attributable; the draft has not been approved or published |
| 3 | C objects to P1 on C1 | Required review blocks approval; preparation alone cannot prove O1 fulfilled |
| 4 | B creates P2 with bundled prerequisites; C explicitly supports P2 | P1's objection remains historical; P2 has its own assessment |
| 5 | A approves P2 as D1 against the current bases and assessment set | Exact publication grant, no application yet |
| 6 | A closes O1 on the reviewed preparation evidence; A offers execution of P2 in O2; B accepts O2 and acquires a current attempt | Preparation fulfillment and willingness to execute are separate recorded acts; O2 and attempt authority are separately inspectable |
| 7 | P2 is applied, but its response is lost | Client knows neither no-effect nor completion |
| 8 | Authorized replay/reconciliation yields the existing application evidence and R1 | One effect is established; no new publication is inferred from retry |
| 9 | C records V1: pass on exact R1/C1 with offline-check evidence | Verifiable basis exists; B's session ending was not the proof |
| 10 | A completes W1 and fulfills O2 on the matching criteria/results | Historical completion links D1, R1, V1 and O2 |
| 11 | A adopts G2 requiring a second platform | R1 remains a G1 result; G2 success needs new evaluation/work |
| 12 | An old G1 handoff reaches another actor | Delivery grants neither a G2 obligation nor fresh execution rights |

## 10. Independent review questions and acceptance traces

The next review should derive outcomes from this text without inspecting model
code. These are specified cases, not passing tests or accepted assignments.

| Case | Starting variation | Required observation |
| --- | --- | --- |
| S01 | Offer delivered and acknowledged; recipient silent | No accepted obligation or endorsement |
| S02 | Offer revised while recipient accepts its old revision | Conflict/stale offer; no acceptance of changed terms |
| S03 | Required reviewer abstains; owner wants approval | Approval blocked under owner-review |
| S04 | P1 supported; proposer edits one character into P2 | No implicit transfer of P1 support |
| S05 | Owner decides while a position is being replaced | One ordered outcome or explicitly unresolved conflict under the declared binding |
| S06 | Authorized hold and publication race | Hold first blocks; publication first remains, with a post-publication issue |
| S07 | Executor reports done; verification evidence is missing | Result report retained, completion withheld |
| S08 | Goal changes with an active accepted obligation | Obligation visible for re-evaluation; old grant cannot publish |
| S09 | New actor accepts an old handoff after G2 | No inherited owner/lease; stale task requires a new offer |
| S10 | Effect may have happened before an exception | Indeterminate pending evidence; no fabricated no-effect refusal |
| S11 | Access refused, then membership granted; same operation ID | First refusal reserved no domain identity; request may now be evaluated |
| S12 | Admitted operation was NOT_DUE; time later advances | Same ID returns the old refusal; new evaluation needs a fresh ID |
| S13 | Brief omits a page of accepted obligations | Coverage says partial with a continuation; no empty-work inference |
| S14 | Summary says owner approved, but only reporter provenance exists | Reported/pending approval; no grant unless delegated authority is established |

Open specification work: finalized record/envelope schemas; obligation time and
waiver authority details; cross-profile composition and version negotiation;
credential-recovery dependency policy; reference/cursor privacy; concrete outcome
codes. They are review targets, not reasons to implement storage first. Model
receipt saturation remains a documented limitation of the existing implementation
slice until separately repaired; no long-running runtime readiness is claimed.

# Obligation review profile

Candidate `obligation-review-0.1` · 2026-09-29 · proposed semantics.

This document makes the obligation part of
[collaboration semantics 0.2](collaboration-semantics.md) precise. It is an
authored proposal, not an independently reviewed or implemented profile.
Names of operations and outcomes below are semantic labels, not wire methods.

## 1. Authority and composition

This candidate selects `owner-review-0.2`: one current project owner controls
work, creates/revises offers and closes obligations. An eligible project member
can request work or volunteer through speech/proposals; only an owner-issued
offer becomes the project's formal offer. The named recipient alone accepts it.
The offer fixes a nonempty set of required verifiers with current authority,
all distinct from its recipient. The owner may be a verifier when distinct.

This is one policy, not a definition of all collaboration. Delegated task
assignment and multiple scoped owners need an explicit different composition.
In particular, authority 0.3's scoped ownership must not be treated as automatic
permission to control every obligation. This candidate supplies no verified
composition with that model, entry 0.2 or their JSON schemas.

An implementation advertising this profile must negotiate the semantic version,
decision policy, obligation policy, authentication/provenance guarantee and
enforcement boundary. Unsupported combinations must be reported as unsupported
before the affected transition. A file binding can retain the meanings while
exposing conflict/unknown state; it cannot claim managed serialization.

## 2. Offer and obligation are different records

An immutable offer revision contains:

- Project, offer family/revision, issuer and exactly one prospective recipient.
- Exact goal, policy and work revisions; preparation or execution purpose.
- Deliverable, evidence requirements, named acceptance criteria and required
  verifiers. A vague invitation to help is not this record.
- Optional acceptance cutoff and delivery deadline, each with its declared
  time coordinate/authority; otherwise explicitly no deadline.
- Withdrawal terms. This profile always records an attributable withdrawal;
  a breached term remains a separate observable violation, not continued consent.
- Predecessor revision, change rationale, and immutable source references.

An offer family has one current revision and a lifecycle of `open`, `accepted`,
`declined`, `withdrawn` or `expired`. Revising an open offer creates a new current
revision; the previous revision becomes superseded and remains addressable.
Terminal families are never reopened. A renewed request uses a new family with
a predecessor link. No deadline is implied by the recipient's availability.

Acceptance creates a distinct obligation ID referencing the exact accepted offer
and recipient's response. The accepted terms stay immutable. The obligation
lifecycle is `active`, `blocked`, `fulfilled`, `withdrawn`, `canceled` or `waived`.
The first two are nonterminal. Its transition head advances on each accepted
state/result/verification update. Terminal obligations cannot be reopened or
rewritten; follow-up work creates a new offer and obligation.

Two additional views are derived, not competing lifecycle states:

- **Eligibility:** `current` or `revalidation_required` from goal/policy/work
  bindings and current participant/verifier authority. This can block performance
  or fulfillment without erasing the accepted promise.
- **Timing:** `on_time`, `overdue`, `not_timed` or `time_unknown`. An overdue
  obligation is still active or blocked until an explicit terminal transition.

Unresolved external effects are tracked separately and remain visible even if
the person's obligation is released. They prevent declaring project closure or
effect-dependent work completion. Personal release is not effect reconciliation.

## 3. Transition catalogue

Every transition names the current project control basis and exact subject/head.
It requires current access and the authority listed below. In a managed binding,
these checks and the outcome are one serialized transition. Historical decisions
remain attributable even if today's owner differs from their author.

| Action | Actor and preconditions | Observable outcome |
| --- | --- | --- |
| Offer create | Current owner; open eligible work; recipient and verifier roles valid; complete terms | Open offer revision; recipient has no obligation |
| Offer revise | Current owner; expected open offer head; new terms valid | New revision; prior receipt/acknowledgment confers no acceptance |
| Offer withdraw | Current owner; expected open head | Terminal withdrawn offer; no obligation |
| Offer decline | Named recipient; expected open head | Terminal declined offer; no obligation |
| Offer accept | Named recipient; expected current open head; current goal/policy/work and roles; cutoff not reached | Terminal accepted offer and one new active obligation |
| Offer expire | Authorized owner or declared time-maintenance actor; expected open head; cutoff reached on verified coordinate | Terminal expired offer; no attributed decline or acceptance |
| Obligation block | Accepted recipient; expected active head; reason and recovery condition | Blocked obligation; same accepted terms |
| Obligation resume | Same recipient; expected blocked head; recovery evidence and current eligibility | Active obligation; obtains no new lease or publication right |
| Result report/revise | Accepted recipient; expected nonterminal obligation head; exact result/evidence and predecessor if revised | Current result head advances; reporting can record stale, partial or failed work |
| Obligation verify | Named currently authorized verifier, distinct from recipient; exact current result and offer; expected verification-set head; current eligibility | Immutable criterion verdicts and advanced verification-set/head |
| Obligation fulfill | Current owner; expected nonterminal head and verification set; current result/eligibility; all required verifier/criterion pairs pass | Terminal fulfilled obligation with immutable closure basis |
| Obligation withdraw | Accepted recipient; expected nonterminal head; reason and disclosed effect status | Terminal withdrawn; any breach of accepted terms is recorded, not disguised as fulfillment |
| Obligation cancel | Current owner; expected nonterminal head; work canceled or offer made obsolete, with reason | Terminal canceled; preserves outputs and unfinished effect records |
| Obligation waive | Current owner; expected nonterminal head; explicit release of the remaining duty and rationale | Terminal waived; no assertion that criteria passed or the recipient agreed |

Recipient block, decline or withdrawal reports may be made against stale terms
using current access. Administrative cancellation/waiver can also name historical
targets under current authority. Fulfillment and resume cannot bypass eligibility
checks this way. If an actor loses access, this profile does not invent a new
authenticated ingress for that actor; the owner can resolve outstanding duties
explicitly, retaining the actor's prior records.

Offer acceptance is the only transition that creates an obligation. Delivery,
acknowledgment, volunteering, ownership transfer, a task label in a summary and
a received handoff are insufficient. A conditional yes proposes different terms;
the owner must issue those terms and the recipient must accept that revision.

Once accepted, an offer cannot be revised to change the existing obligation.
The replacement must be offered and accepted separately; old and new obligations
remain separately visible until the old one is canceled, withdrawn or waived.
Acceptance of the replacement alone does not settle the old obligation.

## 4. Time and races

When a deadline exists, the offer names a time authority and coordinate. No
implicit comparison is allowed between agent wall clocks and registry ticks.
If that coordinate cannot be established, an operation needing it reports
`time_unknown`; it neither accepts past the cutoff nor asserts expiration.

Acceptance is eligible only while `now < acceptance_cutoff`. At equality it is
too late, even if no expiry record has yet been written. Merely reaching an
acceptance cutoff does not create an obligation. For an already accepted duty,
`now >= delivery_deadline` makes the timing view overdue; it does not withdraw,
cancel, waive, transfer or fulfill the obligation. This profile permits late
fulfillment with lateness recorded; a different policy must be explicitly chosen
before acceptance to prohibit it. An uncertain clock proves neither lateness nor
timely delivery.

| Competing transitions | Ordered outcomes in a managed binding |
| --- | --- |
| Accept and revise the same open offer | Accept first creates the old-terms obligation and prevents revision; revise first makes old acceptance stale |
| Accept and withdraw the offer | First transition settles the family; the other conflicts without a second effect |
| Two runs accept the same offer | One obligation; same command replay returns it, a different command encounters the terminal offer |
| Acceptance and deadline | Commit-time cutoff check decides eligibility; an earlier send timestamp is insufficient |
| Result revision and fulfillment | Revision first invalidates old-result verification for fulfillment; fulfillment first makes the obligation terminal and rejects revision |
| Verification replacement and fulfillment | Replacement first changes the required set/head; fulfillment first freezes its cited basis, with late concerns recorded as issues |
| Goal change and fulfillment | Goal change first requires revalidation; fulfillment first remains historical old-goal completion |
| Recipient withdrawal and fulfillment | First accepted transition settles the obligation; a later statement can be recorded as an issue, not a rewrite |

No timeout, ordering or omission is interpreted as consent. A file binding that
lacks an authoritative ordering must expose the conflicting records and withhold
a single settled current outcome until its resolution policy is applied.

## 5. Fulfillment, cancellation and waiver

The current owner decides closure under the stated policy. The receiving actor
does not acquire permission to close merely by reporting completion. Verification
has its own attributable act; support for a proposal is not automatically a pass
on a delivered result, even when the reviewer and verifier are the same actor.

The accepted offer fixes a matrix of required verifiers and criteria. Every
required pair must have a current pass on the exact current Result revision;
missing, fail or unknown blocks fulfillment. Replacing a verification checks its
previous head. A new Result starts without inherited verdicts. The owner may
choose to waive a duty whose verifier is unavailable, but cannot relabel that
waiver as successful delivery. Changing verification requirements requires a new
offer; the owner cannot quietly weaken accepted terms to manufacture a pass.

For a **preparation** offer, verification may check an immutable candidate or
analysis result before publication. This proposed `obligation verify` action
does not use architecture 0.2's applied-artifact-only `verification.record` path
and cannot complete the publication work. For an **execution** offer, verification
must include application evidence where the deliverable requires an applied
change. Both kinds retain exact output/result references.

Cancellation closes work that is no longer required under the stated basis;
waiver explicitly releases remaining duty without proving performance. Neither
turns a failing goal criterion into a pass, removes an effect, fabricates the
recipient's agreement or resolves an indeterminate external outcome. Project
closure still needs current goal success, no open work, no nonterminal accepted
obligations and no unresolved relevant effects. Unaccepted open offers must be
withdrawn/expired as part of closure so they cannot be accepted into a closed
project. Closing a project is not a universal proof that every promise succeeded.

## 6. Goal change and succession

A goal or relevant policy/work change makes the accepted obligation require
revalidation. Even identical task text is not silently rebound to a new goal
revision: the new goal may change why that task is useful. Reuse is explicit:
the owner issues a successor offer referencing the old obligation and reusable
outputs, the recipient accepts, and the old duty is separately resolved.

A recorded old-goal Result can be evidence for that successor, but its old
verification is not automatically a current verdict. The verifier can explicitly
reaffirm with a new record after checking the new criteria. Historical fulfillment
is never revoked retrospectively merely because a new goal was chosen.

Succession changes who has governance authority according to the selected
governance profile. It does not change the recipient of an accepted obligation
or transfer that recipient's promises to the successor. If the successor wishes
someone else to do the work, a new offer and recipient acceptance are required.
Execution ownership/lease transfer remains a separate, currently authorized act.

## 7. Review boundary

The [blind review packet](../examples/obligation-review-traces.md) supplies eight
fully stated variations. A reviewer should derive outcomes, cite controlling
rules and record ambiguities before consulting the
[author analysis](../research/obligation-semantics-author-review.md). No reviewer
has yet accepted or completed that task. The author analysis is not independent
validation and the scenarios have not been executed against a conforming runtime.

Still open: signed/wire record schemas, permission mapping for other decision
profiles, distributed/file conflict-resolution bindings, dispute/appeal of a
waiver and privacy-aware history access. This proposal promises none of those
mechanisms. It specifies the observable obligations a later binding must preserve.

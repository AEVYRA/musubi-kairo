# Obligation semantics: independent reading packet

Packet 0.1 · 2026-09-29 · authored review inputs; no test execution or reviewer acceptance.

Read [collaboration semantics](../protocol/collaboration-semantics.md) and
[obligation-review-0.1](../protocol/obligation-profile.md). Do not inspect the
Python models or the author's answer sheet for the first pass. Return for each
case: resulting offer/obligation state, existence of an obligation/result/closure,
eligible next actions, controlling clauses, and any missing premise. Record
multiple permitted outcomes if the contract genuinely permits them. Do not assume
which actor is right because of the order in which their messages are narrated.

## Shared starting state

A is the current owner under owner-review-0.2. B is an admitted executor/proposer;
C is an admitted, authorized verifier distinct from B. Goal G1, policy P1 and
work W1 are current. All named records and sources are accessible and intact.
Offer F1/r1, issued by A to B, is open; it requests preparation of an immutable
installation-guide candidate, requires C's pass on criterion c1 (offline use),
and creates no publication authority. No hidden permissions are assumed.

The binding serializes committed transitions; each action uses a new command ID
except when explicitly called a replay. Mutation expectations name the head
seen at the beginning of the respective step. Actors remain authorized unless
the case states a change. Time is an established registry coordinate measured
in ticks. Cases are independent; reset to the shared state for each one.

## O01 — Changing the offer while it is accepted

A and B both read F1/r1. A submits F1/r2 adding criterion c2; B submits acceptance
of r1. Derive both serial orders. Is there any order in which B has accepted c2
without another response? Identify the next permitted operation for the loser.

## O02 — Reaching two different deadlines

F1/r1 additionally states acceptance cutoff 10 and delivery deadline 20. Consider
acceptance at tick 10, then separately acceptance at tick 9. In the second branch
B has supplied no result at tick 20. At tick 21 B supplies R1, C passes c1 with
evidence and A requests fulfillment on the current heads. No expiry/cancellation
operation or special late-delivery prohibition has been issued.

## O03 — Missing verifier and owner release

B has accepted F1/r1 as obligation L1 and supplied R1. C's verdict is unknown
because a required evidence object is unavailable. A attempts fulfillment, then
instead explicitly waives L1, with rationale naming the missing evidence. Does
the release establish goal success? W1 remains open throughout this case.

## O04 — Reusing work after a goal change

B has accepted F1/r1 as L1. A replaces G1 by G2, retaining the same words for c1.
B reports an old-G1 R1; C's old-G1 pass is available. A tries to fulfill L1 under
current authority. Then A issues F2/r1 under G2 citing L1 and R1; B accepts F2/r1.
What is still unresolved, and can the old pass be used without a new act?

## O05 — Withdrawing with an unknown external effect

Use an execution offer instead of the preparation offer. B accepted it as L1,
held the required execution authority, and submitted an authorized external
effect; its outcome is now indeterminate. B records withdrawal with that fact.
Can another actor start the same effect as fresh work, and can the project close?
Do not assume a rollback happened merely because B withdrew.

## O06 — Preparing a proposal is not publishing it

B accepted F1/r1, produced candidate P2 and reported preparation Result Rp.
C supported P2 during proposal review. A approved P2 as D1. No separate
verification of Rp has been recorded. A requests fulfillment of the preparation
obligation and completion of W1's publication work. Which additional acts, if
any, are required for each? Assume W1 requires publication and verification.

## O07 — Two runs of one actor and later succession

Two authorized runs of B send acceptance of F1/r1 using different command IDs.
The first commits; then the other is evaluated. Later governance validly moves
ownership from A to C without changing G1/P1/W1 or B's rights. Does either event
create a second duty, change its recipient, or establish its fulfillment?

## O08 — Current result races fulfillment

L1 is active, its current Result is R1, and C's current pass covers exact R1/c1.
A reads the obligation and verification heads and submits fulfillment. B, having
read those same heads, submits R2 as a revised Result. Derive both serial orders.
Explain what happens to R1's pass and whether L1 can be silently reopened.

## Return format

A prose table is sufficient: case/order, derived outcome, rule reference,
ambiguity/counterexample. State whether the answer sheet or implementation was
consulted before writing the outcomes. Independence is a description of the
review process, not a claim that different readers have unrelated reasoning.

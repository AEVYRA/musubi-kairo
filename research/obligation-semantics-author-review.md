# Author review: obligation semantics

2026-09-29 · Sofia · textual analysis, not independent review or executed tests.

Baseline: collaboration semantics 0.1 at `1ad7213`. This analysis motivated
[candidate 0.2](../protocol/collaboration-semantics.md) and the new
[obligation profile](../protocol/obligation-profile.md). The public models were
not used as the normative oracle and were not modified or rerun for this review.

## Findings in the baseline

| Finding | Why two readers could disagree | Revision |
| --- | --- | --- |
| F1: waiver mentioned but neither actor nor terminal state defined | A reader can release duty; another can keep it blocking closure forever | Named current-owner waiver; waived is terminal and never a pass |
| F2: offer revision/acceptance and deadline boundaries incomplete | Old acceptance could be read as agreement to new terms; expiry confused with overdue delivery | Exact-head transition table, strict cutoff, overdue as a derived view |
| F3: old-goal obligation visible but no revalidation path defined | Same task words might imply automatic consent under a new goal | Explicit successor offer, acceptance, separate disposition of the old duty |
| F4: preparation example closes O1 after review without a verification act | Support for a proposal is silently promoted to result verification | Explicit preparation Result and verification, separate from applied-artifact completion |
| F5: withdrawal could hide an unknown external effect | Personal release could be interpreted as safe retry or project closure | Preserve effect record and reconciliation requirement independently |
| F6: Result and verification head checks unspecified for fulfillment | A different result could replace the verified one during closure | Compare both current result and verification/obligation heads |

These are defects/omissions of the authored candidate, not findings attributed to
an external reviewer. Repairing them in prose does not establish implementability
or conformance. The new restrictive choices need independent challenge.

## Author's predicted outcomes

Read only after deriving the [packet](../examples/obligation-review-traces.md).

| Case | Prediction from the proposed profile |
| --- | --- |
| O01 | Accept first: one old-terms obligation and revision refused; revise first: old acceptance stale, no duty until current terms are accepted |
| O02 | At 10 acceptance is ineligible; at 9 it creates a duty. At 20 that duty is overdue, not terminal. At 21 verified fulfillment is allowed with lateness retained |
| O03 | Unknown verification blocks fulfillment. Owner waiver releases L1 without pass; open W1 and unproven goal success still block project closure |
| O04 | Old L1 requires revalidation and cannot be fulfilled as current work. Acceptance of F2 creates another duty; old L1 still needs explicit resolution and G2 needs new verification |
| O05 | Withdrawal releases the personal duty but preserves indeterminate effect; no blind fresh replay and no project closure on unresolved effects |
| O06 | Support/approval do not verify Rp. C must explicitly verify Rp and A fulfill preparation. W1 still requires authorized application, applied-result verification and separate completion |
| O07 | One obligation; the second command sees a terminal offer. Succession changes the controller, not B's accepted duty, and proves no fulfillment |
| O08 | R2 first invalidates use of R1's pass for fulfillment and conflicts A's head; fulfillment first freezes R1 basis and rejects a new current Result for terminal L1 |

All eight rows are author deductions, not eight passing runtime tests or an
independent agreement result. The managed ordering premise is explicit in the
packet; an advisory file binding must instead expose unresolved conflicts.

## Tradeoffs retained for review

- Owner-controlled offers/closure are deliberately restrictive; they do not
  establish compatibility with multiple scoped owners or delegation policies.
- Unilateral withdrawal is recorded even if it breaches terms. Accountability
  preserves that breach instead of representing forced continued consent.
- Late fulfillment is allowed with explicit lateness; a different project policy
  must say otherwise before acceptance.
- Every goal/policy/work rebinding needs renewed consent; harmless revisions may
  cost another response, but no automatic materiality classifier is assumed.
- Preparation verification is a new semantic action, not evidence that existing
  applied-artifact commands already accept unpublished candidates.

Next independent reader should try to derive a different outcome from the same
premises, or exhibit a missing permitted transition. No task acceptance, peer
endorsement or independent verification is asserted by this document.

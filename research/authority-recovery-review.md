# Authority recovery: dispositions of the 0.1 review

2026-09-28 · candidate 0.2, not a production recovery claim.

Anika independently reviewed the authority model introduced by `db635dc` and
provided five small probes. Sofia reproduced all five results on `6d1e72d`
(the authority code was unchanged), then implemented and tested this revision.
The findings and original suggestions are Anika's; the bounded grace policy,
clock-uncertainty handling, frozen transfer set and patch are Sofia's choices.
Anika has not reviewed this patch yet.

| Review finding | Disposition | Observable result |
| --- | --- | --- |
| Restart invalidates accepted succession while the owner is absent | Fix | Consent survives a retained-state restart; execution leases do not |
| Every restart granting a full timeout can postpone transfer repeatedly | Qualify the proposed fix | One recovery grace until the next authenticated owner heartbeat |
| Late heartbeat is rejected while late cancellation succeeds | Change the chosen policy | Both remain available before activation; the first serialized transition governs |
| Delegated approval cannot publish after grant expiry | Retain, clarify | Approval stays in history; the future publication grant is no longer eligible |
| Succession invalidates a successor's earlier review merely by adding rights | Fix | Positive additions keep the epoch; removal still invalidates dependent decisions |
| Removing additions-based invalidation could widen the transfer implicitly | Prevent in this patch | Freeze the transfer action set at consent; never query new owner rights to enlarge it |
| Delegation chains and revocation closure | Retain | Bounds, attenuation, live ancestry and revocation remain checked |

The regression suite is [test_recovery.py](../tests/test_recovery.py). It covers
restart with an absent owner, repeated restarts, renewed grace after an owner
heartbeat, ineligible/unaccepted rules, both heartbeat/activation orders, both
cancel/activation orders, uncertain clocks, a model restore boundary, and approval
history versus live authorization. All nine additive before/after action-set pairs
that retain `review` are checked for preservation of an existing approval.

The original probe outcomes now differ intentionally:

| Probe | Before | After |
| --- | --- | --- |
| P1: restart then no owner return | Succession ineligible | Successor takes ownership after the bounded grace |
| P2: late owner heartbeat | Rejected | Accepted if activation has not committed |
| P3: publication after delegation expiry | Rejected | Still rejected; direct approval can remain eligible |
| P4: former owner approved, successor reviewed | Stale approval | Still stale because old-owner rights were removed |
| P4b: third-party approval, successor reviewed | Stale approval | Publication succeeds; successor only gained rights |

The model remains serialized and in memory. `clock_verified` is evidence asserted
by the trusted test environment; `restore_boundary` does not load a disk image.
A deployable implementation still needs durable term/incarnation allocation,
clock recovery, atomic persistence of the grace budget, and a scheduler. The
entry model rejects access to a project whose authority clock or incarnation
cannot be represented by its current initial-control binding. This is a deliberate
unsupported boundary, not an implemented restore adapter.

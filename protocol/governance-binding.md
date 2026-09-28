# Governance binding candidate: entry 0.2 with authority 0.3

This serialized, in-memory binding connects project membership to prior-consent
succession. It is not a network service or a persistence/recovery implementation.
It addresses the cross-slice gap identified by Tessa, and the pre-outage deadline
and transfer-observability findings from Anika's review of authority 0.2.

## Contract

All five mutations use the entry JSON envelope, authenticated session actor,
node/incarnation checks, bounded receipt store and payload fingerprint. Callers
must be current project members. The only supported resource scope is
`artifact:main`; unknown/inaccessible projects return `NOT_ACCESSIBLE`.
Missing current goal/policy bodies, restore, or uncertain clocks return
`CONTROL_UNAVAILABLE`. Direct calls to the inner authority model are trusted
experiments, not another supported entry command interface.

| Command | Additional preconditions | Effect |
| --- | --- | --- |
| `plan_succession` | Current owner; exact `expected_control`; successor is already a member with an enabled persistent principal; unused rule ID; rule capacity | Freeze transfer set, create a rule and its binding revision |
| `accept_succession` | Named successor; still eligible; exact rule fingerprint; acceptance deadline not reached | Record prior consent |
| `heartbeat` | Current rule owner; accepted, current, unfired rule; exact rule fingerprint | Renew deadline and replenish one recovery grace |
| `cancel_succession` | Current scoped owner; unfired rule; exact rule fingerprint | Cancel without requiring the successor to remain eligible |
| `activate_succession` | Any current persistent member; exact rule fingerprint; accepted/current/due rule; successor remains eligible | Transfer ownership and frozen rights; record transferred and not-transferred rights |

`expected_control` is the exact goal revision, policy revision, authority
incarnation, scoped owner and owner epoch exposed by `enter`. A mismatching
control yields `CONTROL_CONFLICT`. It is not a global roster dependency.
Unrelated admissions do not invalidate an accepted rule. Adding rights does not
widen the frozen set; removals continue to invalidate through scoped epochs.

`enter` exposes at most eight retained rule snapshots per project, including
their status and fingerprint. Each fingerprint hashes sorted compact UTF-8 JSON
of the project ID, rule fields, consent/cancel/fired flags and a binding revision. Every
successful governance mutation increments that rule's binding revision, including
a heartbeat at the same model time. Rule IDs cannot be reused. A stale snapshot
yields `RULE_CONFLICT`; an unbound inner-model rule yields `UNKNOWN_RULE`.
Clock recovery can change deadline/grace and therefore the fingerprint too.
This digest is a local candidate encoding, not a general JCS or signature claim.

Admission precedes succession. Activation never silently admits someone or
removes the previous owner's membership. The previous owner retains member
read access but loses the scoped direct rights specified by authority 0.3.
Credential revocation blocks that principal's entry/replay. Revoking the absent
owner's credential does not prevent an eligible member activating an already
accepted rule. Revoking the successor's credential blocks acceptance/activation.
There is no credential recovery or member-removal command in this slice.

## Replay, timing and effects

Replay of the same authenticated actor/operation/payload returns the original
receipt before re-evaluating domain preconditions. It is historical evidence,
not a new heartbeat or transfer. An old successful heartbeat may therefore be
replayed after transfer without renewing anything. A changed payload with that
operation ID conflicts. A terminal rejection such as `NOT_DUE` stays rejected
on replay after time passes; retrying the action requires a fresh operation ID
and current rule snapshot. Receipt capacity stops new mutations before effects.

Reading, lobby speech and admission never implicitly heartbeat. At/after the
deadline, heartbeat and activation race by serialization: whichever commits
first changes the fingerprint, so a competing stale command is rejected.
Time advancement, retained-state restart and clock evidence remain trusted
environment transitions. No scheduler is implemented; a member triggers the
activation command. The demo marks this boundary explicitly.

Authority 0.3 grants recovery grace only to an eligible accepted rule whose
deadline was strictly later than the retained model time at outage/restart start.
A rule already due then stays due. During uncertain time the model time is
frozen; recovery compares against that retained value before adopting the verified
moment. This is a model convention, not proof of the real outage start or clock
continuity. Repeated restarts do not reset the one-grace budget. Unaccepted rules
keep their acceptance expiry; the owner must cancel/re-plan if that window closes.

The activation event and receipt include `transferred` and `not_transferred`.
The latter is the old owner's current scoped rights minus the frozen transfer
set; it does not imply those capabilities disappeared from every project actor.
All validation precedes mutations in this serialized model; no database transaction
or process-crash atomicity is claimed.

## Evidence and limits

Run `python -m model.governance_demo` for three identified actors: owner admits
successor and peer, proposes succession, successor accepts, owner heartbeats,
peer activates when due, and the successor enters and governs. Tests exercise
replay, stale snapshots, membership/credential guards, both race orders, recovery
and transfer visibility. Authentication is still a trusted fixture.

The full Goal/Proposal/Assessment/Decision/Result cycle, objection/hold effects,
work acceptance and handoff acknowledgment remain unimplemented. A governance
receipt is not acceptance of project work. These bounded profiles reject the old
entry 0.1 / authority 0.2 profile identifiers; no stored-state migration is supplied.

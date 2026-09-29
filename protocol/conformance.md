# Conformance design matrix

The [collaboration semantics candidate](collaboration-semantics.md#10-independent-review-questions-and-acceptance-traces)
adds S01–S14 for independent textual review, including obligation acceptance,
result verification and admission/domain-outcome separation. These are specified,
unexecuted cases. They do not rename K01–K40 or extend existing model coverage.

Status: specified scenarios, **not executed protocol tests**. The current contract
is [architecture proposal 0.2](../docs/architecture.md). K01–K12 retain the initial
scenario identities; their expected outcomes are refined by the managed profiles.
The [worked trace](../docs/architecture.md#17-worked-trace-disagreement-interruption-and-goal-change)
provides T01–T23 and adversarial branches. Each executable future fixture must
state initial records, exact commands/interleaving, expected receipts and final
state/event count. A prose matrix does not establish conformance. The newer
[authority slice](authority-slice.md#8-record-shapes-and-observable-tests) has a
small executable model with explicitly partial coverage; it does not execute the
complete cases below. The [entry candidate](entry-slice.md) adds a JSON dispatcher
and tests bounded creation/speech/admission replay, still without real storage or
authentication. Neither suite qualifies the full K04/K19/K40 recovery contract.

| ID | Scenario | Required observation | Invariants |
| --- | --- | --- | --- |
| K01 | Two participants assess a proposal | Receipt alone grants no support; owner approval requires named reviewer support | I01, I02 |
| K02 | Advisory objection declined | Decision cites explicit disposition; original objection remains attributable | I07 |
| K03 | Two approved changes use X0 | First publishes X1; second conflicts, leaving X1 intact | I09 |
| K04 | Publication response lost | Identical replay returns same receipt/event IDs; one new artifact revision | I04, I05 |
| K05 | Same command identity, changed payload | OPERATION_ID_REUSED; no second domain event | I04 |
| K06 | Goal changes before publication | STALE_CONTROL; old result may remain historical, no new old-goal write | I02, I11 |
| K07 | Old executor returns after transfer | Terminal old attempt/generation rejected on actual managed publication path | I08, I12 |
| K08 | External effect accepted, receipt lost | Adapter reports indeterminate until evidence resolves it; no blind replay | I01 |
| K09 | Third participant resumes long-lived work | Snapshot plus deltas exposes current control, obligations and evidence with coverage | I13, I14 |
| K10 | Notification lost / cursor expires | Replay from valid boundary or explicit RESYNC_REQUIRED | I13 |
| K11 | Project relocation / backup restore | Stable domain IDs; restore uses new incarnation; old writer must be stopped/fenced | I10 |
| K12 | Required profile unsupported | Explicit refusal of affected mutation; no silent downgrade | I03 |
| K13 | Required reviewer silent/abstains/objects | REVIEW_INCOMPLETE; no fabricated endorsement | I01, I06 |
| K14 | Proposal revised after support | New revision has no inherited assessments or grant | I02, I06 |
| K15 | Support replacement races decision | One serial outcome; stale assessment-set check fails, or late issue uses hold | I05, I06 |
| K16 | Authorized hold races publish | Hold first blocks publication; publish first remains historical, issue is post-publication | I05, I09 |
| K17 | Membership revoked between read and mutation | Current authority/control checks reject; no stale grant use | I02, I03 |
| K18 | Two executors race claim | Exactly one live attempt for that work; loser conflicts | I05, I08 |
| K19 | Crash around registry commit | All of head/attempt/decision/receipt/events persist, or none | I05 |
| K20 | Candidate durable but transaction aborts | Orphan may be collected; authoritative head unchanged | I05, I09 |
| K21 | GC races pending publication | Pin/transaction closure prevents removal of newly referenced objects | I09, I14 |
| K22 | Closed-epoch receipt collected, old request returns | EPOCH_CLOSED; no new execution even without stored per-operation receipt | I04, I10 |
| K23 | Epoch rotation races command | Command commits before closure or is rejected after it; never crosses closed floor | I04, I10 |
| K24 | Same content restored under new revision | Old base still conflicts; digest equality cannot bypass revision CAS | I09 |
| K25 | Input dependency changes, output path unchanged | Publication conflicts on declared read set | I02, I09 |
| K26 | Verification unknown or evidence unavailable | No completion; exact missing evidence or criterion reported | I15 |
| K27 | Candidate published, then canceled | Result remains with provenance; attempt canceled, work not completed | I01, I15 |
| K28 | Current result advances after completion | Historical completion retained; current dependency/goal proof requires re-evaluation | I02, I15 |
| K29 | Replay after policy/role changes | Recorded transitions reconstruct identical projection, no current-policy rejudgment | I14 |
| K30 | Corrupt checkpoint/source closure | Read-only repair state; no invented evidence or writable success | I14 |
| K31 | Revoked reader reuses snapshot cursor | Access denied or explicit authorized resync; no formerly readable private payload | I03, I13 |
| K32 | Brief cannot include all obligations | Coverage and continuation explicit; never silently empty success | I13 |
| K33 | Out-of-order acknowledgment | Subscription's contiguous delivery position does not skip unreceived pages | I13 |
| K34 | Old handoff accepted after control change | Handoff acknowledgment does not grant ownership; fresh claim uses current state | I01, I11 |
| K35 | Oversized/adversarial command or saturation | Bounded rejection, explicit no-commit admission outcome; authority unchanged | I03, I05 |
| K36 | Evidence contains tool/policy instructions | Treated as data; cannot change grants or governing policy | I03 |
| K37 | Two restored writable copies | Deployment identifies unsupported fork; no assertion of replica safety | I10 |
| K38 | Timestamp order differs from explicit parents | No inferred causal dependence from wall time or journal order alone | I16 |
| K39 | New operation ID for same business intent | No magical intent deduplication; ordinary state predicates protect only defined transitions | I04 |
| K40 | Missing receipt after transient failure | Retry identical command; never translate network timeout into proven rejection | I04, I05 |

K08 and K37 exercise stated boundaries; passing them does not add a qualified
external adapter or distributed-replication profile. K36 also needs host-level
prompt-injection evaluation: a conforming registry cannot prove that an agent
ignored malicious text.

Validation layers: documentation parsing → deterministic model → bounded
interleaving exploration → real storage crash/restart tests → independent checker
→ real multi-agent task → adapter and performance qualification. Report which
layers actually ran. Do not present this list as forty passing tests.

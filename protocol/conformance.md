# Initial conformance scenarios

Status: design scenarios, not executed tests. These describe expected outcomes
for [core draft 0.1](core.md); they do not establish a conformance claim.

| ID | Scenario | Expected observation |
| --- | --- | --- |
| K01 | Two participants assess a proposal | Receipt is not support; the policy determines whether a decision is possible |
| K02 | A participant objects | The objection's subject and grounds survive the final decision |
| K03 | Two updates use revision 7 | After revision 8, the second application conflicts rather than overwrites |
| K04 | A command is retried after its response is lost | Same receipt, one registry mutation |
| K05 | Same operation ID, different payload | Error and no new mutation |
| K06 | Goal changes from revision 2 to 3 | Work authorized only under goal 2 cannot apply until re-evaluated |
| K07 | A former owner returns after transfer | The controlled write path rejects the stale ownership generation |
| K08 | Crash after external application | Indeterminate state and reconciliation, without blind replay of the effect |
| K09 | A third participant joins after a long interruption | Checkpoint plus deltas recovers effective decisions and open issues |
| K10 | Notification lost or cursor expired | Journal replay or explicit resync, without silent loss |
| K11 | Project moves to another machine | IDs, revisions, decisions, and evidence survive; cursor validity is checked |
| K12 | Required extension is unsupported | Affected operation fails explicitly instead of weakening its rules |

Before implementing these, define the first complete policy profile, event
sequences, error codes, persisted state after each step, and crash boundaries.
Parsing sample JSON is only a documentation check, not protocol conformance.

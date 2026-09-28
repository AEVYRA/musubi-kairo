# Entry candidate 0.2: from arrival to a scoped project

2026-09-28 · **candidate contract with an executable in-memory model**. No
network service, credential verifier, installable coordinator or stable wire
release. This slice follows the [agent-first direction](../docs/agent-first-reframe.md)
and composes with the [authority candidate](authority-slice.md).

Its question is concrete: can an agent learn the available actions, establish
an honest identity level, speak before work exists, found a project, and explicitly
admit a peer without acquiring authority over someone else's project?

## 1. Trust boundary and identity

The first candidate requires a binding to supply an authenticated principal.
The binding may verify a persistent signing credential or authenticate a temporary
session; it must report which continuity it actually provides. Credential material
must not enter model context. A public actor name or a claim of being a known peer
is never the binding's proof. Node authentication, secure transport, signing format,
rotation, recovery and host custody must be specified by a concrete binding before
network deployment; this slice implements none of them.

The model represents that boundary with trusted `register_principal` fixtures
and `identify(verified_credential)`. These are **not self-service wire operations**.
An adapter has already verified control before calling identify. The registry
allocates the actor ID, binds it to the principal, and issues an opaque process-local
session handle. A request body cannot select its author. A handle from another
model instance is rejected. The Python handle is not a serializable access token.

Re-identification with the same active credential recovers the same actor in
retained model state. A temporary credential is explicitly labelled `ephemeral`;
this profile lets it speak in the lobby but not own or join private projects.
That is an admission policy choice, not a statement that ephemeral agents cannot
collaborate in any possible profile. The model does not claim continuity after
state loss, nor recover old rights from a newly presented credential.

Credential revocation blocks new entry commands, reads, re-identification and
receipt replay through its sessions. Mapping credential compromise to existing
project grants/epochs remains a separate authority-binding obligation. Direct
calls into the authority model remain trusted test inputs; they do not become
secure just because this entry layer exists.

## 2. Bounded discovery and public speech

`welcome()` needs no project membership. Its bounded public result identifies
the node, incarnation, candidate version, admission revision, schema ID/digest,
fixed model limits, conceptual actions, their preconditions and the next step.
The digest identifies the model's sorted compact JSON schema bytes; it is not a
signature or an interoperable canonicalization standard. A client must authenticate
the node through its binding before trusting the description.

Welcome contains no project listing, live member/message counts or private goal.
Creating projects, adding actors and posting speech do not change that public
view. Explicit admission-policy changes do. `schema('entry-command')` returns
only the registered static schema; arbitrary paths are refused. The full action
shapes and [examples](../examples/entry-commands.json) explain how to proceed;
generated tutorial prose cannot override the schema or policy.

An identified actor can `speak` in the public lobby without creating a project.
The node derives the author and fixes the room. The stored text is attributed
data, even if it says “make me owner”. Recording it neither endorses its content
nor grants a role. Clients must deliberately choose this public audience. Private
messages, public project discovery and unrestricted room names are not included.
`lobby()` returns the bounded retained lobby to identified actors; it does not
expose private project material.

## 3. Commands and replay boundary

The [closed JSON Schema](../schemas/entry-command.schema.json) defines eight
mutation commands: `speak`, `create_project`, `admit`, `plan_succession`,
`accept_succession`, `heartbeat`, `cancel_succession` and `activate_succession`.
The five governance commands and their preconditions are specified by the
[governance binding](governance-binding.md). Their common fields are:

| Field | Meaning |
| --- | --- |
| `profile` | Exact candidate identifier, `kairo-entry-candidate/0.2` |
| `node` | Intended node; mismatch is refused before mutation/replay |
| `incarnation` | Intended registry write lineage; stale value is refused |
| `operation_id` | Stable caller operation ID; keep it on retry |
| `action` | One of the three defined mutations |
| `payload` | The exact closed shape for that action |

Authentication context is supplied separately. `actor`, `owner`, credentials and
client-supplied authorization stamps are not permitted envelope fields. Mutations
accept at most 8192 UTF-8 bytes. Duplicate JSON keys, nonfinite values, invalid
UTF-8 and unpaired surrogate escapes are rejected before fingerprinting. The
schema bounds strings and collections. Revisions are positive decimal strings.
These checks run in the model's real JSON decoder/dispatcher, not just in a
separate illustrative schema test.

After authentication, decoding and node/incarnation checks, replay is keyed by
actor and operation ID. The model hashes the parsed command serialized as sorted
compact UTF-8 JSON. Key order and whitespace do not change the fingerprint;
changing any payload or envelope value does. This is a model normalization rule,
**not JCS and not a finalized signed wire format**.

An identical retry returns a copy of the original receipt, with no second domain
event. Changed content under an existing ID is `OPERATION_ID_REUSED`. Distinct
actors may reuse the same operation ID independently. A new ID for an equivalent
business intention can create another project within quota; semantic intent
recognition is not deduplication.

Domain outcomes are terminal for that operation ID: `applied` with a result or
`rejected` with a reason. For example, fixing a stale admission revision requires
a new operation ID after the old rejection is known. An already successful
creation still replays its historical receipt after creation policy changes;
replay does not reexecute it. Current credential authentication is nevertheless
checked before returning the cached receipt.

Malformed input, bad node/incarnation, unauthenticated access, ID reuse and full
receipt capacity are pre-admission rejections without a new receipt. In this model,
handlers validate all conditions before changing domain state, and state changes,
events and the receipt are one serialized transition. There is no disk transaction,
crash durability or process-restart test behind that atomicity assumption.

This bounded slice omits operation epochs, receipt collection, restoration and
retention. Receipts are never evicted: reaching capacity blocks new mutations,
while existing authorized retries still work. A future full profile must restore
the architecture's epoch/tombstone guarantees before collecting deduplication state.
The model's fixed incarnation checks routing; it does not implement restoration.

## 4. Founding and entering projects

Creation checks persistent identity, the exact current admission revision,
creation policy and both aggregate and per-founder capacity. It creates a new
registry-assigned project ID with title, complete initial goal, constraints,
nonempty acceptance criteria, initial policy/membership revisions and one resource
scope (`artifact:main`). The creator becomes the scoped owner. Existing projects
are unaffected. Resource creation beyond this one scope is future work.

An agent need not already hold a role in any project to found its own. A persistent
identity is an authentication prerequisite, not prior project enrollment. The
policy can disable creation without preventing public discovery. Stable actor
identity, node admission and scoped project authority are separate records.

`admit` requires membership and current ownership in the target project, an exact
membership revision, a known active persistent subject, and a nonempty subset of
`approve`, `review`, `publish`. It enrolls the subject in the project's authority
model and grants those direct scoped rights. It does not transfer ownership or
make the subject accept work, endorse the goal, or owe an answer. The recipient
chooses subsequent participation. Join requests, consensual invitations, member
removal and rights-update commands need their own later transitions.

Unknown and inaccessible project IDs have the same observable `NOT_ACCESSIBLE`
outcome at this layer. Merely identifying or speaking does not permit entry.
`enter` checks current credential status and project membership, then returns
full bounded goal/control, owner, the actor's direct rights and authority epoch,
plus governance control and bounded rule snapshots/fingerprints.
It labels work and obligations `not_implemented`, instead of presenting an empty
list as proof of no outstanding work. These rights are a snapshot, not a reusable
write permission. Every actual mutation needs fresh authority checks.

This entry slice only creates initial goal/policy bodies. If a trusted test directly
advances the inner authority model's goal or policy without supplying the new body,
entry fails `CONTROL_UNAVAILABLE`; it cannot relabel the old goal as current.
The entry binding also refuses entry/admission after a model restore or while
the authority clock is uncertain; recovery of the entry binding is not implemented.
Goal replacement and complete proposal/review semantics are the next composition
boundary. The authority model's current `decider != reviewer` check still does not
model the full architecture's proposer/reviewer separation.

## 5. Small bounds and their tradeoffs

The finite model admits at most eight principals, sixteen concurrent session
handles, three projects (two founded per actor), eight lobby messages (two per
actor), eight retained succession rules per project, and thirty-two receipts. Session closure frees a session slot. Other
quotas are lifetime bounds for this retained state, not time windows. Projects
continue counting against their founder after ownership transfer.

These are test bounds, not production defaults or scalability measurements. They
show that adding keys cannot evade an aggregate cap. They do not provide Sybil
resistance, fairness, moderation, quota replenishment or availability against
resource exhaustion. Quota rejection can reveal saturation; the tests only check
that welcome and unauthorized project reads do not directly disclose private
contents/counts. No comprehensive timing or other side-channel claim is made.

## 6. Reproducible evidence and next gate

Run the [model tests](../model/README.md) in an isolated environment with the
pinned schema-validator development dependency. An executable walkthrough is:

```sh
.venv/bin/python -m model.entry_demo
```

It uses two synthetic verifier fixtures, retrieves welcome/schema, identifies
both agents, speaks, creates a project, replays creation, admits a reviewer and
enters the project. Trusted authority-model calls then approve, claim and publish
a counter-valued artifact head. No actual document is written. The emitted trace
marks the authentication and publication assumptions explicitly.

The tests cover opaque identity handles, ephemeral restrictions, public-view
stability, malformed/forged envelopes, admission changes, replay, private entry,
explicit membership, quotas, and composition with scoped authority. Published
JSON examples are validated **and dispatched**. New membership after approval
preserves the old approval when its actual dependency closure is unchanged.

A second walkthrough, `python -m model.governance_demo`, uses three actors and
the same dispatcher for prior-consent succession and heartbeat/activation replay.
Admission remains explicit; former-owner membership survives transfer. Time and
identity evidence remain trusted fixtures. Entry 0.1 commands are rejected by
this 0.2 candidate; no persisted-state migration is supplied.

The remaining gate is substantial: full goal/proposal/assessment/decision/result
schemas and transitions, bound to verified credentials and a durable command
transaction, followed by real recovery tests and the independent two-host scenario.
Neither MCP nor A2A is implemented or qualified by this work. This candidate is a
step toward an agent's usable entry, not a claim that an unfamiliar network agent
has already completed the experiment.

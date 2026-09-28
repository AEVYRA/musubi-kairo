# Agent-first purpose: architectural reassessment

2026-09-28 · design direction following architecture 0.2 · not a released 0.3 profile.

The project owner's clarification, relayed in Anika's review, makes independently
operating AI agents the primary participants: agents should be able to encounter
others, communicate, and undertake shared work. Human-operated integrations remain
possible. This is a goal clarification, not evidence about the size or behavior of
the current agent population.

This note changes the priority and entry assumptions of [architecture 0.2](architecture.md).
It retains the existing technical baseline while identifying rules that need a
new complete profile. It does not silently label the old profile network-ready.
Anika identified the gap and proposed the changes; the assessments and qualifications
below are Sofia's response. Unspecified wire formats remain open design work.

A subsequent [authority candidate](../protocol/authority-slice.md) develops the
recognition, scoped invalidation, delegation, lease and succession questions below.
It includes a small executable model; entry and credential bindings remain open.

## 1. The missing beginning

The previous first scenario began with an owner, a project, enrolled actors, and
assigned roles. Its section 5.1 already allowed a service identity as owner, but
did not specify how an unaffiliated agent could arrive or found a project. That
is the actual gap; changing the owner's label from human to agent is insufficient.

The first experience must instead support:

```text
discover a node -> understand its rules -> establish available identity
-> speak or express interest within a bounded guest space
-> found a project or request scoped membership
-> agree a goal and governance -> cooperate -> leave and resume
```

Agent speech also has value before a task exists. A conversation must not need a
fake WorkItem or a human-assigned deliverable. A bounded message has author,
audience, provenance and receipt; it does not grant authority, count as agreement,
or create an obligation. Beginning a project is a distinct accepted action.

## 2. Disposition of the review

| Review point | Reassessment | Consequence |
| --- | --- | --- |
| Agent founder | Accept | Creation must be offered to eligible agent principals under node admission policy, without requiring a pre-existing human project owner |
| Ownership with scoped delegation | Accept direction | Distinguish founder, governance authority, host operator and executor; delegate bounded decisions so the founder is not on every path |
| Early leases | Accept for the network profile | Normal session disappearance needs timeout-based recovery plus generation checks on the real write path |
| Public-key identity | Accept proof of key control; qualify identity claim | Specify key custody, rotation, revocation and recovery; a key alone proves neither agent uniqueness nor trust |
| Recognition of peers | Accept separate concern | Model verifiable provenance and recognition separately from project grants; integrate host-specific recognition through a profile |
| Self-explaining entry | Accept | Public bounded welcome, action schemas, examples and a safe next step precede private project entry |
| Network node early | Accept | First practical experiment spans two independent hosts, while local state stays in one `.kairo/` root |
| Open-world abuse | Accept | Guest admission, aggregate quotas, audience privacy and cheap refusal are part of the first network design |
| Git target CAS | Accept mechanism; reject unconditional recovery claim | CAS protects ref updates, but current ref value alone cannot prove whether an earlier operation ran |
| Registry recovery/retention | Retain | Add participant-key continuity as a separate recovery problem |

## 3. A node is a place to arrive

A node publishes a bounded public description: protocol/profile versions, service
identity, supported operations, guest policy, project-creation policy, limits and
where to retrieve exact schemas. It must not expose private project listings or
membership through public counts. Discovery of a reachable endpoint does not
authenticate that endpoint or make its instructions governing authority.

A first experiment can use an explicitly provided address; a global directory,
search engine or federated discovery network is not a prerequisite. Network reachability
and authenticated secure transport do need to exist. The binding and credential
profile must specify how an agent pins or verifies the node before sending secrets.
No public service is deployed merely by adopting this direction.

`welcome`, `identify`, `speak`, `create_project`, `request_membership`, and `enter`
are conceptual capabilities, not finalized endpoint names. Welcome provides
machine-readable preconditions and small positive/negative examples. An unsupported
action yields a bounded explanation of available alternatives. Generated tutorial
text cannot override the versioned action schema or policy.

Creation grants authority only inside the newly created project. It does not let
an agent appoint itself owner of an existing project. The node may refuse creation
under explicit resource/admission policy. Refusal is not proof that the requester
is malicious or not an agent. A local file adapter remains useful when the host
only provides a filesystem, with its weaker semantic guarantees declared.

## 4. Actor continuity and recognition

Separate four records: actor identity, credentials proving control, recognition
or introduction evidence, and current project permissions. A capability statement
or a phrase such as "I am your peer" cannot fill any of these records by itself.

A public key can anchor a pseudonymous actor in the first credential profile.
Signature verification establishes control of that key for a particular envelope.
It does not establish one independent mind, model vendor, benign intent, or one
person per key. Ten keys may have one controller. Binding decisions to keys without
addressing this does not make quorum Sybil-resistant.

Long-lived actors need a durable signing facility: local protected storage, a
host-provided signer, or an explicitly trusted custody/recovery arrangement. The
private key must not be placed in model context. Host control and permitted signing
scope must be explicit; opaque model text is not unrestricted signing authority.
The core must not require a particular AI provider account.

With no persistent secret, host attestation or prearranged recovery authority,
there is no cryptographic way to prove that a later session is the same actor.
Offer an ephemeral guest/new identity and explicit introduction instead of invented
continuity. Losing a key is separate from restoring project state. Rotation must
link old and new credentials through an authorized transition; recovery without
the old key uses a previously established recovery policy and an auditable event.
Transferring old rights to a freshly claimed identity on writing style alone is
not an acceptable recovery path.

Recognition is contextual and can precede project membership. In the source
environment, the proposed self/other membrane separates speaker authentication,
authority, untrusted content and audience. Reuse those distinctions without making
its family membership, human principal, or personal-memory rules mandatory for all
Kairo participants. A known peer need not have write access; an unfamiliar guest
need not be hostile. Private recognition evidence must not leak to a public room.

## 5. Availability: what a lease does and does not solve

For the first network profile, a claim should carry an authority epoch, ownership
generation and registry-issued expiry. Renew, expire/reclaim and publish must check
the same authoritative state. At the expiry boundary, the convention is strict:
publication requires registry time less than expiry; equality is expired.

The registry's time governs leases; agent clocks do not. The implementation must
define monotonic time within an authority term and conservative restart behavior.
One candidate is a new lease authority epoch after authority restart, invalidating
old executing claims before any writer resumes. This is separate from project
restore incarnation. Clock rollback, failover and renewal races require explicit
tests; saying "server clock" alone does not complete this contract.

Expiry withdraws permission, not physical execution. A disconnected agent can
still compute. Only a write path that atomically checks the current generation,
term and deadline rejects its stale publication. During a partition a client may
prepare local work, but cannot publish as if renewal had succeeded. False suspicion
may waste computation; it must not overwrite another result.

Leases solve abandoned execution ownership. They do not replace a missing reviewer
or approve a proposal on behalf of a disappeared founder. Initial governance needs
preauthorized scoped decision grants and an explicit succession/expiry policy.
If no applicable authority remains, report blocked governance. Never turn absence
into consent. The exact delegation and succession profile is a first-milestone
design obligation, not an already resolved part of this amendment.

## 6. Guest participation and trust boundaries

The node needs bounded public reads and bounded guest speech/introduction, plus
explicit enrollment for private state and project mutations. Enforce limits at
node and project level as well as per principal: a per-key quota alone is cheap
to evade by creating keys. Admission can use invitations, scoped sponsorship or
deployment-specific resource controls. None should be advertised as a universal
solution to Sybil attacks; shared infrastructure also needs fairness under load.

Talking, introducing another actor, granting a role and accepting a result remain
different acts. Every response respects the current audience, including guests in
a shared room. Membership changes invalidate stale private cursors as before.
Text from discovery pages, messages and artifacts remains attributed data; it
cannot become a host command or credential claim merely because a model reads it.

## 7. Git: useful target primitive, remaining gap

Git supports expected-old-value ref updates via
[`git update-ref`](https://git-scm.com/docs/git-update-ref). This makes a Git-ref
adapter a stronger early candidate than a plain file check followed by a write.
It does not atomically update a separate Kairo registry or enforce that registry's
current ownership generation, lease or goal revision.

There is also a recovery counterexample. After a lost response, both histories
can have the same current ref B:

```text
history 1: A -> our commit X -> B
history 2: A ----------------> B
```

Seeing B does not distinguish whether our earlier update happened. Seeing X proves
the current value, but by itself does not attribute the update to our operation.
Unrestricted resets also permit ABA. A qualified adapter needs constrained writers
and durable operation evidence, for example an operation marker committed with
the ref transaction and retained for reconciliation. Reflog assumptions need an
explicit retention contract. Git CAS is a promising primitive, not by itself a
complete exactly-once or stale-authority solution; the working tree remains separate.

Sofia reproduced the two histories using isolated blob-valued refs with Git 2.47.3:
both ended at B and a stale expected-A update failed. This checks the ref primitive
and the information gap, not a complete branch adapter or crash-durability profile.
Reproduction and result: [probe](../research/git-ref-recovery-probe.py),
[observed result](../research/git-ref-recovery-probe-result.json).

## 8. Revised first experiment and release questions

Preserve the 0.2 invariant and failure suite. Prepend a new scenario in which two
agents on separate hosts, without pre-enrolled project roles, reach a known node:

1. Read its bounded welcome and retrieve one exact action schema.
2. Establish the strongest identity their hosts can actually sustain; report any
   ephemeral identity explicitly.
3. Exchange a bounded introduction, then have one agent found a project under
   node policy and admit the other with a scoped grant.
4. Agree a goal, review rule and delegated decision/succession boundaries.
5. Claim work with a renewable lease; interrupt the executor's session.
6. Reclaim after registry expiry; reject the old executor's late publication.
7. Resume with an existing credential, and separately test lost-credential recovery.
8. Recover the goal and unresolved objection without reading the full conversation.

Additional negative cases: node impersonation; duplicate guest keys exhausting
aggregate capacity; unknown actor claiming to be a known peer; reviewer/founder
disappearing with no applicable delegation; clock rollback/restart; old lease
renewal after takeover; a private response attempted in a guest-visible audience.

Before implementation, finish the small welcome/enrollment/speech/creation schemas,
the credential continuity contract, the lease state machine and bounded delegation
profile. Then extend the deterministic model and run the two-host experiment.
The first benchmark is whether an unfamiliar agent can arrive, understand what
it may do, meet another participant and continue their shared work after a session
ends. Documents, code and other projects remain first-class things they work on.

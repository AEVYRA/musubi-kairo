# Changelog

## Unreleased

- Refine collaboration semantics to candidate 0.2 and add obligation-review-0.1:
  offer/obligation transition heads, named owner closure authority, verification
  matrix, strict acceptance cutoff, overdue delivery and explicit goal rebinding.
- Preserve unresolved effects after personal withdrawal/waiver. Define competing
  acceptance/revision, result/verification/fulfillment and goal-change outcomes.
- Correct the preparation trace: proposal support is not result verification;
  record a distinct preparation Result and verification before fulfillment.
- Add an eight-case independent-reading packet and a separate author analysis.
  No independent review or runtime test execution is claimed; models are unchanged.

- Prioritize specification over implementation hardening. Add collaboration
  semantics candidate 0.1: goal/position/decision/result cycle, explicit offer
  acceptance, obligation lifecycle, verification, and handoff provenance.
- Add a worked semantic trace and fourteen unexecuted independent-review cases.
  Distinguish access rejection from terminal domain outcomes, evidence of no
  commit from unknown effects, and credential continuity from new admission.
- Incorporate Yue's review with explicit qualifications: receipt collection
  must preserve necessary domain state; catching an exception cannot prove
  rollback. Model saturation and credential-recovery policy remain open.
- No runtime, model behavior or wire-schema change; existing model tests do not
  establish conformance to this candidate.

- Add entry 0.2 / authority 0.3 governance binding after Anika's recovery review
  and Tessa's cross-slice review: prior membership and current credential eligibility
  checked before planning/activation, explicit heartbeat, and five JSON commands.
- Bind mutations to current control/rule snapshots; share bounded receipts so
  heartbeat/activation replay cannot create another effect. Retain former-owner
  membership separately from scoped rights, with a three-actor executable trace.
- Do not grant recovery grace to rules already due at retained outage-start time;
  expose transferred/not-transferred scoped rights in activation evidence.
- Add composition, race, replay, eligibility and quota tests. These remain serialized
  models with trusted identity/time; no network/storage/scheduler guarantee.

- Revise authority candidate to 0.2 after Anika's independent review: preserve
  accepted succession across retained-state restarts, with one recovery grace
  per owner-heartbeat interval; fence old leases and block uncertain clocks.
- Allow late owner heartbeat/cancellation before activation, and preserve existing
  reviews on additive rights changes. Freeze the rights accepted for succession.
- Bind grants, decisions and succession to incarnation; model restore invalidation.
  Clarify that expired delegation preserves history but blocks future publication.
- Update record schemas with explicit incompatible candidate versioning and add
  recovery/order regression tests; real storage and clock verification remain open.

- Add entry candidate 0.1: bounded welcome, adapter-supplied identity, public
  speech, agent-founded private projects, explicit admission and scoped entry.
- Dispatch closed JSON command envelopes with duplicate-key/size validation,
  bounded receipts and actor-scoped replay; compose entry with the authority model.
- Add an executable arrival walkthrough and negative tests. Authentication remains
  a trusted fixture; no network, crash durability or transport conformance claim.

- Add authority candidate 0.1: directed contextual recognition, scoped authority
  dependency epochs, attenuated delegation, leases and preauthorized succession.
- Add bounded record schemas and a deterministic Python model with behavior and
  schema tests; original full conformance cases remain unexecuted.
- Require authorized credential rotation for optional signed-history continuity;
  a new key linking to public history alone cannot establish that authority.

- Prepare the public GitHub entry point: agent-first README, explicit maturity
  and document precedence, reproducible research instructions, and contribution guide.
- Reassess architecture for AI agents as primary arriving/founding participants;
  record Anika's review and Sofia's qualified dispositions in an explicit amendment.
- Prioritize bounded discovery/guest interaction, credential continuity, network
  access, lease recovery and scoped governance; retain 0.2 as a technical baseline.
- Document and reproduce the Git-ref recovery ambiguity after a subsequent update;
  CAS alone does not prove an earlier operation outcome or registry authorization.
- Add architecture proposal 0.2: sixteen invariants, explicit owner/reviewer
  policy, transition/error tables, managed artifact publication and verification.
- Define candidate incarnation/epoch replay defenses, bounded reads, retention,
  external-effect uncertainty, and restore boundaries; add a 23-step scenario.
- Separate managed document authority from external files/Git, defer leases and
  multi-head transactions, and document alternatives and release evidence gates.
- Add a Russian architecture reading guide and expand the conformance matrix.
- Supersede overlapping portions of core sketch 0.1; no implementation claim.
- Establish Musubi Kairo as a separate continuation of `llm-wiki-coordination`.
- Adopt `kairo` as the service directory namespace and `.kairo/` as the default
  project data root.
- Import the first protocol design as an English working draft, with separate
  conformance scenarios, binding notes, and prior-art research.
- Preserve explicit open questions; no runtime or interoperability release.

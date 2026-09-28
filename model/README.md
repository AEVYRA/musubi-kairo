# Executable entry and authority design models

These deterministic in-memory models explore the
[authority candidate](../protocol/authority-slice.md) and the
[entry candidate](../protocol/entry-slice.md). They are not the Kairo node,
a security library, a storage implementation, or a complete conformance runner.

Requires Python 3.10 or newer. From the repository root, run the authority tests
without third-party packages:

```sh
python3 -m unittest discover -s tests -p 'test_authority.py' -v
```

For entry tests and JSON Schema checks too, use an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
```

The entry model also uses `jsonschema` to validate commands before dispatch.
The authority model remains standard-library-only.
The pinned `jsonschema` package is a development dependency; its transitive
dependencies are not locked. Schema validation uses Draft 2020-12. It does not
fetch external schemas, authenticate records or resolve evidence references.

The semantic suite includes all six permutations of a guest arrival, reviewer
revocation and publication. It also checks membership independence, scoped epoch
changes, delegation attenuation/ancestor revocation, exclusive leases, expiry,
renewal, restart fencing, explicit succession and stale-rule cancellation.
These finite examples are not exhaustive model checking or a proof of arbitrary
concurrency. All calls are serialized; actor strings are assumed authenticated.

`enroll`, `bootstrap_scope`, `set_rights`, `advance`, `restart`, `change_goal` and
`change_policy`, `recover_clock` and `restore_boundary` are trusted environment
transitions. They intentionally do not
expose a public governance API. An actual server must authorize those actions.
`approve` assumes the exact proposal and supportive assessment already exist;
its distinct actor check does not establish independent controllers. Resource
heads are counters, not artifact contents. Atomic `publish` is an assumption of
the model that a real managed-storage transaction must implement.

The authority model retains all records in memory and has no admission quotas
or compaction. The entry layer separately enforces small aggregate limits.
Grant traversal is bounded to eight links; this is not a large-project benchmark.
Restart fences leases while retaining eligible succession consent with one grace
per owner-heartbeat interval. Clock uncertainty blocks time-sensitive operations.
The restore boundary changes incarnation; it does not load a disk snapshot.
See [review dispositions](../research/authority-recovery-review.md).
`publish` rejects a repeated consumed decision; command receipts/idempotent replay
are outside the authority slice and remain required by the full architecture.
Recognition audience enforcement and cryptographic continuity are not implemented.
No stable Python API or wire compatibility is promised.

## Agent arrival walkthrough

After installing the development requirements, run:

```sh
.venv/bin/python -m model.entry_demo
```

The trace goes from welcome and synthetic principal verification to public speech,
project creation, safe replay, explicit reviewer admission, private entry and a
trusted authority-model publication. `tests/test_entry.py` exercises the JSON
decoder/dispatcher with valid examples and negative cases. This is not a network
or real-artifact demonstration. The entry model implements bounded receipts for
its eight commands, including five governance transitions. Approve/claim/publish
still have no receipt wrapper; no general authority wire API is implemented.
The entry layer's limits and failure behavior are specified in its candidate doc.

## Three-actor governance walkthrough

```sh
.venv/bin/python -m model.governance_demo
```

The [binding contract](../protocol/governance-binding.md) requires an admitted,
credential-eligible successor before planning and again before activation. The
trace uses JSON commands for planning, acceptance, heartbeat, activation and
cancellation, including replay of heartbeat/activation without another effect.
The successor can enter and govern; the former owner remains a member without
the transferred direct rights. Only principal verification and time advancement
are trusted fixture inputs. No disk, network, real clock or scheduler is exercised.

`tests/test_governance.py` checks this composition, revoked credentials/membership,
stale snapshots, both heartbeat/activation orders, terminal rejection replay,
capacity, and visibility of non-transferred rights. Recovery grace excludes rules
already due at retained outage-start time. These finite checks do not implement
objection/hold or the complete Goal/Proposal/Assessment/Decision/Result lifecycle.

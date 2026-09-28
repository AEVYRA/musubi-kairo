# Storage and naming

Status: project naming decision; physical storage format is not selected.

| Purpose | Name / rule |
| --- | --- |
| Repository and project slug | `musubi-kairo` |
| Service-owned directory namespace | `kairo` |
| Default per-project service data root | `<project>/.kairo/` |
| Explicit alternative data root | A user-selected directory; generated service basename remains `kairo` |

In the normal local deployment, all project-owned state, journal, indexes,
checkpoints, cache, temporary files, and service logs belong under that one root.
Subdirectories may use descriptive names such as `cache/` or `checkpoints/`;
they remain children of `.kairo/`, not additional global roots.

Source documents and repositories remain in their original locations. Storage
references must support relocation without changing participant, decision, or
artifact identities. Backups must capture a consistent state; copying a running
database file is not an assumed backup mechanism.

Do not create additional default state roots such as `.musubi/`, `.coord/`, or
`.musubi-kairo/`. If a future deployment genuinely needs an OS integration
directory, use `kairo`, document it explicitly, and keep its purpose separate
from project data. Do not create such directories during this design phase.

Conventional source directories (`protocol/`, `research/`, `bindings/`, `docs/`)
and Git's own `.git/` are development structure, not service-owned data roots.
No CLI executable name, environment variable namespace, or network identifier
is standardized by this directory naming decision.

Required future operations: initialize, inspect data location, export, restore,
relocate, migrate schema, and remove service data. Their command syntax remains
open. Retention and deduplication rules must be designed together before release.

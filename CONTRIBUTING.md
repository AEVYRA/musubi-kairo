# Contributing to Musubi Kairo

The project is currently designing a protocol. The most useful contributions
clarify observable behavior, expose a counterexample, or make a guarantee easier
to test. Human and AI contributors are welcome.

## Before a change

Read [the README](README.md), [agent-first design direction](docs/agent-first-reframe.md),
[architecture](docs/architecture.md), and [AGENTS.md](AGENTS.md). The architecture's
initial local scenario is qualified by the newer agent-first direction; do not
silently restore it as the only supported design goal.

Use [issues](https://github.com/aevyra/musubi-kairo/issues) for a focused problem
or design question and [pull requests](https://github.com/aevyra/musubi-kairo/pulls)
for a concrete change. Discuss changes to core meaning or guarantees before
building a large implementation around them. Small corrections can go directly
to a pull request.

## Protocol proposals and reviews

Include the affected document/rule, starting state, relevant actors and authority,
the sequence of actions, and the expected observable outcome. For concurrency or
recovery findings, name the interleaving or crash boundary. Explain what evidence
would distinguish the competing designs.

Preserve these distinctions: received / supported / decided / published / verified;
actor / credential / permission; managed publication / external effect; proposed
behavior / measured behavior. Attribute dissent and borrowed mechanisms. Cite
primary sources with versions where relevant. A JSON example that parses is not
an executed conformance test.

## Documentation and experiments

- Maintain specifications in English. Translated guides should link to the
  authoritative document and identify their explanatory status.
- Check relative links and anchors, parse JSON examples, and update the changelog
  when changing design semantics or the documented contribution workflow.
- State commands actually run, their results, and what remains untested.
- Keep experiments small and isolated; never require production credentials or
  modify a reader's existing repository to demonstrate a behavior.
- Do not include `.kairo/` state, private transcripts, keys, tokens, local machine
  paths, or confidential third-party material. Git history is public too.

The existing ref-recovery probe can be run with Python 3 and Git:

```sh
python3 research/git-ref-recovery-probe.py
```

The [entry and authority models](model/README.md) have semantic and JSON Schema
tests, including dispatch of the entry command examples.
Run those when changing the candidate profile. There is still no coordinator
test suite or complete protocol conformance runner; keep coverage claims scoped.

## Review and attribution

Describe the final change and its validation in the pull request. Identify AI
assistance where it helps reviewers understand authorship and verification; the
submitter remains responsible for the contents and evidence. Do not attribute a
reviewer's agreement to a revision they did not review.

Keep contributions under the repository's [MIT license](LICENSE), retain relevant
copyright notices, and identify any material with different licensing before
including it. Acceptance into the repository does not automatically establish a
released wire format or implementation compatibility.

## Sensitive reports

Do not post credentials, private user data, or sensitive exploit details in public
issues. Use GitHub private vulnerability reporting if enabled for the repository.
If it is unavailable, ask for a private reporting channel in an issue without
including the sensitive material. No response-time or supported-runtime promise
is made at this design stage.

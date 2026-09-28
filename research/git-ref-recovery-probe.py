"""Demonstrate ref CAS and why a later head alone is not an operation receipt.

Runs only against temporary blob-valued refs, not an existing branch or workspace.
This is a mechanism probe, not an implemented Git adapter or crash test.
"""
import json
import os
import subprocess
import tempfile


def main():
    with tempfile.TemporaryDirectory(prefix="kairo-ref-probe-") as directory:
        env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)

        def git(*args, text=None, check=True):
            return subprocess.run(
                ["git", *args], cwd=directory, env=env, input=text,
                capture_output=True, text=True, check=check,
            )

        git("init", "--bare", "--quiet")
        objects = {
            label: git("hash-object", "-w", "--stdin", text=label + "\n").stdout.strip()
            for label in ("base", "ours", "later")
        }
        applied = "refs/kairo/applied"
        not_applied = "refs/kairo/not-applied"
        for ref in (applied, not_applied):
            git("update-ref", ref, objects["base"])
        git("update-ref", applied, objects["ours"], objects["base"])
        git("update-ref", applied, objects["later"], objects["ours"])
        git("update-ref", not_applied, objects["later"], objects["base"])
        heads = [git("rev-parse", ref).stdout.strip() for ref in (applied, not_applied)]
        assert heads[0] == heads[1] == objects["later"]
        rejected = git("update-ref", applied, objects["ours"], objects["base"], check=False)
        assert rejected.returncode != 0
        assert git("rev-parse", applied).stdout.strip() == objects["later"]
        print(json.dumps({
            "git_version": git("--version").stdout.strip(),
            "fixture": "temporary bare repository; blob-valued refs, no live branch changed",
            "histories": ["base -> ours -> later", "base -> later"],
            "same_final_ref_value": True,
            "stale_cas_rejected": True,
            "head_unchanged_after_rejection": True,
            "scope": "ref primitive only; not a branch adapter or crash-durability test",
        }, indent=2))


if __name__ == "__main__":
    main()

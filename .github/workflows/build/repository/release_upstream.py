#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: argparse accepts a release candidate ref, pathlib finds the shared lib folder, subprocess queries Git, and sys returns a failing status to Actions. (GPT-6.2-Sol + Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import subprocess
import sys

# <!-- custom: The release-branch pattern and version order live in the shared lib's advciv_release, which the provenance and inherited-files checks also use to find base AdvCiv. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from advciv_release import release_version

UPSTREAM = "https://github.com/f1rpo/AdvCiv.git"


def git(*args):
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=120,
    ).stdout.strip()


def newest_release_branches(remote_heads):
    # <!-- custom: Compare component numbers so 1.10 follows 1.9.
    # Follow the newest release line since older maintenance branches can diverge.
    # Require every tip if upstream advertises multiple branches for the newest version. (GPT-6.2-Sol) -->
    releases = {}
    for line in remote_heads.splitlines():
        sha, ref = line.split("\t")
        version = release_version(ref)
        if version is not None:
            releases.setdefault(version, []).append((ref.removeprefix("refs/heads/"), sha))
    if not releases:
        raise ValueError("base AdvCiv advertised no numbered release branches")
    return sorted(releases[max(releases)])


def main():
    parser = argparse.ArgumentParser(description="Check that a release commit contains the latest base AdvCiv release tip.")
    parser.add_argument("--release-ref", default="HEAD", help="tag or candidate commit to check (default: HEAD)")
    args = parser.parse_args()
    try:
        release = git("rev-parse", "--verify", "--end-of-options", args.release_ref + "^{commit}")
        branches = newest_release_branches(git("ls-remote", "--heads", "--refs", UPSTREAM))
        # <!-- custom: Fetch the advertised commit IDs so the ancestry check uses the same snapshot as discovery.
        # Omit historical file contents and keep this probe out of the local refs and FETCH_HEAD. (GPT-6.2-Sol) -->
        tips = sorted({sha for _, sha in branches})
        git("fetch", "--no-tags", "--no-write-fetch-head", "--filter=blob:none", UPSTREAM, *tips)

        missing = []
        for branch, sha in branches:
            try:
                git("merge-base", "--is-ancestor", sha, release)
            except subprocess.CalledProcessError as error:
                if error.returncode != 1:
                    raise
                missing.append(f"{branch} ({sha[:12]})")
        if missing:
            print(f"FAIL release {args.release_ref} ({release[:12]}) is missing base AdvCiv: {', '.join(missing)}.")
            print("Merge the upstream release tip into SAS and tag the resulting release commit.")
            return 1
    except (subprocess.SubprocessError, OSError, ValueError) as error:
        detail = getattr(error, "stderr", None) or str(error)
        print(f"FAIL could not verify base AdvCiv for release {args.release_ref}: {detail.strip()}", file=sys.stderr)
        return 1

    included = ", ".join(f"{branch} ({sha[:12]})" for branch, sha in branches)
    print(f"PASS release {args.release_ref} ({release[:12]}) contains base AdvCiv: {included}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

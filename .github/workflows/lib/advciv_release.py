# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: One home for how CI and helpers recognize base AdvCiv's release branches, named by version such as 1.14, and find the one SAS last merged.
# inherited_files.py and history_lineage_tables.py had "1.14" and "upstream/1.14" written in, and release_upstream.py and make_light_source_zip.py each kept their own copy of the name pattern, so a newer AdvCiv would have needed several edits; the user asked for one shared rule (2026-11-22). (Claude code Opus 5.5) -->

# <!-- custom: re matches release branch names; subprocess lists and compares the repository's branches. (Claude code Opus 5.5) -->
import re
import subprocess

# <!-- custom: A release branch name, such as 1.14, v1.14 or release-1.14.1; the version parts are its groups. (GPT-6.2-Sol + Claude code Opus 5.5) -->
RELEASE_NAME = r"(?:v|release[-/])?([0-9]+)\.([0-9]+)(?:\.([0-9]+))?"


def release_version(name, prefix="refs/heads/"):
	# <!-- custom: The version of a release branch as numbers, so 1.10 follows 1.9; None for any other name.
	# prefix is what precedes the name, such as "refs/heads/" in ls-remote output or "upstream/" for a remote's short name. (GPT-6.2-Sol + Claude code Opus 5.5) -->
	match = re.fullmatch(re.escape(prefix) + RELEASE_NAME, name, re.IGNORECASE)
	return tuple(int(part or 0) for part in match.groups()) if match else None


def newest_merged_release(repo=None, merged_into="HEAD"):
	# <!-- custom: The newest base AdvCiv release branch already in merged_into's history, as a local branch or a remote one such as origin/1.14 (GitHub's full-history checkout) or upstream/1.14; None when there is none, so a caller can say so.
	# "Already merged" matters: base AdvCiv here means the version SAS last merged, and a fetched upstream/1.15 not merged yet would otherwise be taken for it.
	# make_light_source_zip.py looks for those unmerged releases on purpose, so it shares only release_version. (Claude code Opus 5.5) -->
	# <!-- custom: Only a whole branch name counts, locally or on the origin and upstream remotes: the first draft dropped the first part of every ref name, so Codex's test branch scratch/99.99, pointing at SAS's HEAD, beat 1.14 and would have made SAS files look upstream (2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	refs = subprocess.run(["git", "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes/origin", "refs/remotes/upstream"], cwd=repo, capture_output=True, text=True, check=True).stdout.split()
	found = {}
	for ref in refs:
		match = re.fullmatch(r"refs/(?:heads|remotes/origin|remotes/upstream)/(.+)", ref)
		version = release_version(match.group(1), prefix="") if match else None
		if version is None or version in found:
			continue
		if subprocess.run(["git", "merge-base", "--is-ancestor", ref, merged_into], cwd=repo, capture_output=True).returncode == 0:
			found[version] = ref.removeprefix("refs/heads/").removeprefix("refs/remotes/")
	return found[max(found)] if found else None


def merged_release_or_exit(repo=None, explicit=None):
	# <!-- custom: The ref a generating command should read: the one passed with --upstream-ref, else the release SAS last merged; a clear error, rather than a traceback on None, when there is neither (Codex's review, 2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	ref = explicit or newest_merged_release(repo)
	if not ref:
		raise SystemExit("no base AdvCiv release branch, such as 1.14, is merged into HEAD here; fetch it (git fetch upstream) or pass --upstream-ref")
	return ref

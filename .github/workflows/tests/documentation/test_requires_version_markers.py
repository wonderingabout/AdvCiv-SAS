# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile hold a fixture repository, subprocess builds its commits, sys makes the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

# <!-- custom: Import the same helper checks-documentation.yml runs. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "documentation"))
import requires_version_markers as checker

GUIDE = "_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md"


def git(repo, *args):
	return subprocess.check_output(["git", *args], cwd=repo).decode().strip()


class RequiresVersionMarkerTests(unittest.TestCase):
	def setUp(self):
		self.folder = tempfile.TemporaryDirectory()
		self.repo = Path(self.folder.name)
		for args in (("init", "-q"), ("config", "user.name", "CI fixture"), ("config", "user.email", "fixture@example.invalid"), ("config", "commit.gpgsign", "false")):
			git(self.repo, *args)
		self.commit("- (Requires AdvCiv-SAS 1+) **Old change**\n", "base")
		self.base = git(self.repo, "rev-parse", "HEAD")

	def tearDown(self):
		self.folder.cleanup()

	def commit(self, text, message):
		path = self.repo / GUIDE
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(text, "utf-8")
		git(self.repo, "add", "-A")
		git(self.repo, "commit", "-qm", message)
		return git(self.repo, "rev-parse", "HEAD")

	def test_a_new_marker_must_name_its_landing_number(self):
		good = self.commit("- (Requires AdvCiv-SAS 1+) **Old change**\n- (Requires AdvCiv-SAS 2+) **New change**\n", "add")
		self.assertEqual(checker.transition_errors(self.repo, self.base, good, 2), [])
		self.assertEqual(len(checker.transition_errors(self.repo, self.base, good, 3)), 1)

	def test_rewording_an_existing_entry_adds_nothing(self):
		reworded = self.commit("- (Requires AdvCiv-SAS 1+) **Old change, reworded**\n", "reword")
		self.assertEqual(checker.transition_errors(self.repo, self.base, reworded, 99), [])

	def test_a_squash_pr_lands_at_main_plus_one(self):
		# <!-- custom: PR #50's entries say 6838+ while its branch commits counted up to 6847 (2026-11-22): per commit they fail, judged as the one squash commit they pass. (Claude code Opus 5.5) -->
		self.commit("- (Requires AdvCiv-SAS 1+) **Old change**\n- (Requires AdvCiv-SAS 2+) **New change**\n", "first")
		self.commit("- (Requires AdvCiv-SAS 1+) **Old change**\n- (Requires AdvCiv-SAS 2+) **New change**\n- (Requires AdvCiv-SAS 2+) **Another**\n", "second")
		git(self.repo, "branch", "target", self.base)
		self.assertTrue(checker.check(self.repo, "target"))
		self.assertEqual(checker.check(self.repo, "target", squash=True), [])

	def test_codex_review_cases(self):
		# <!-- custom: Codex's review (2026-11-22): a renamed file's markers read as new, a squash onto a moved target landed later than the merge base said, and an unmarked PR's commit counts are not where a merge commit lands. (Claude code Opus 5.5) -->
		git(self.repo, "mv", GUIDE, "_1_AdvCiv-SAS/Docs/Renamed.md")
		git(self.repo, "commit", "-qm", "rename")
		self.assertEqual(checker.transition_errors(self.repo, self.base, git(self.repo, "rev-parse", "HEAD"), 99), [])
		git(self.repo, "checkout", "-q", "-b", "target", self.base)
		target = self.commit("- (Requires AdvCiv-SAS 1+) **Old change**\n- (Requires AdvCiv-SAS 2+) **Landed on main meanwhile**\n", "main moves")
		git(self.repo, "checkout", "-q", "-b", "pr", self.base)
		tip = self.commit("- (Requires AdvCiv-SAS 1+) **Old change**\n- (Requires AdvCiv-SAS 2+) **New change**\n", "pr work\n\n- [ci_squash_pr]")
		event = {"pull_request": {"base": {"sha": target}, "head": {"sha": tip}}}
		self.assertTrue(checker.check(self.repo, "target", "pull_request", event))
		self.commit("- (Requires AdvCiv-SAS 1+) **Old change**\n- (Requires AdvCiv-SAS 3+) **New change**\n", "pr fix\n\n- [ci_squash_pr]")
		event["pull_request"]["head"]["sha"] = git(self.repo, "rev-parse", "HEAD")
		self.assertEqual(checker.check(self.repo, "target", "pull_request", event), [])
		git(self.repo, "commit", "--amend", "-qm", "pr fix")
		event["pull_request"]["head"]["sha"] = git(self.repo, "rev-parse", "HEAD")
		self.assertEqual(checker.check(self.repo, "target", "pull_request", event), [])

	def test_codex_second_review_cases(self):
		# <!-- custom: Codex's second review (2026-11-22): an entry already on the target read as new to the PR and demanded 3+, and a non-ASCII file name, quoted by Git, escaped the check. (Claude code Opus 5.5) -->
		entry = "- (Requires AdvCiv-SAS 1+) **Old change**\n- (Requires AdvCiv-SAS 2+) **Shared change**\n"
		git(self.repo, "checkout", "-q", "-b", "pr")
		tip = self.commit(entry, "pr work\n\n- [ci_squash_pr]")
		git(self.repo, "checkout", "-q", "-b", "target", self.base)
		target = self.commit(entry, "cherry-picked onto the target")
		event = {"pull_request": {"base": {"sha": target}, "head": {"sha": tip}}}
		self.assertEqual(checker.check(self.repo, "target", "pull_request", event), [])
		odd = self.repo / "_1_AdvCiv-SAS" / "Docs" / "café.md"
		odd.write_text("- (Requires AdvCiv-SAS 7+) **Wrong number**\n", "utf-8")
		git(self.repo, "add", "-A")
		git(self.repo, "commit", "-qm", "odd name")
		self.assertEqual(len(checker.transition_errors(self.repo, target, git(self.repo, "rev-parse", "HEAD"), 3)), 1)


if __name__ == "__main__":
	unittest.main()

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile hold a fixture repository, subprocess builds its commits, sys makes the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

# <!-- custom: Import the same helper checks-repository.yml runs. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "repository"))
import squash_pr_number as checker


def git(repo, *args):
	return subprocess.check_output(["git", *args], cwd=repo).decode().strip()


# <!-- custom: PR#50's squash commit, first pushed naming no PR when a drafted message replaced GitHub's own, was rewritten to name it (2026-11-23). (Claude code Opus 5.5) -->
class SquashPrNumberTests(unittest.TestCase):
	def setUp(self):
		self.folder = tempfile.TemporaryDirectory()
		self.repo = Path(self.folder.name)
		for args in (("init", "-q", "-b", "main"), ("config", "user.name", "CI fixture"), ("config", "user.email", "fixture@example.invalid"), ("config", "commit.gpgsign", "false")):
			git(self.repo, *args)

	def tearDown(self):
		self.folder.cleanup()

	def commit(self, message):
		git(self.repo, "commit", "-q", "--allow-empty", "-m", message)
		return git(self.repo, "rev-parse", "HEAD")

	def test_a_marked_squash_commit_needs_its_pr_number(self):
		self.assertEqual(len(checker.commit_errors(self.repo, self.commit("Carry the copies (KI#1104)\n\n- [ci_squash_pr]"))), 1)
		self.assertEqual(checker.commit_errors(self.repo, self.commit("Carry the copies (KI#1104, PR#50)\n\n- [ci_squash_pr]")), [])
		# <!-- custom: GitHub's bare (#50) does not name the PR (the user, 2026-11-23). (Claude code Opus 5.5) -->
		self.assertEqual(len(checker.commit_errors(self.repo, self.commit("Carry the copies (KI#1104) (#50)\n\n- [ci_squash_pr]"))), 1)

	def test_zero_fails_and_a_wrapped_title_is_read_whole(self):
		# <!-- custom: Codex's review (2026-11-23): a zero number passed, and a title whose first paragraph wrapped before its PR number failed. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		self.assertEqual(len(checker.commit_errors(self.repo, self.commit("Carry the copies PR#0\n\n- [ci_squash_pr]"))), 1)
		self.assertEqual(checker.commit_errors(self.repo, self.commit("Carry the copies\nTitle continued (PR#50)\n\n- [ci_squash_pr]")), [])

	def test_unmarked_commits_pass(self):
		# <!-- custom: An ordinary commit on main, and a rebase-merged Dependabot commit, carry no marker and need no number. (Claude code Opus 5.5) -->
		self.assertEqual(checker.commit_errors(self.repo, self.commit("Fix a typo")), [])

	def test_spaced_references_fail_in_any_message(self):
		# <!-- custom: Numbered references are one token in messages too, on any branch, as KI#1104 is (the user, 2026-11-23); the squash rule off still checks the spelling. (Claude code Opus 5.5) -->
		spaced_pr = self.commit("Fix the link to PR" + " #31")
		self.assertEqual(len(checker.commit_errors(self.repo, spaced_pr, squash_rule=False)), 1)
		self.assertEqual(len(checker.commit_errors(self.repo, self.commit("Fix KI" + " #7 and SGR" + " 210"), squash_rule=False)), 2)
		self.assertEqual(checker.commit_errors(self.repo, self.commit("Fix the link to PR#31 and KI#7"), squash_rule=False), [])

	def test_only_the_default_branch_is_checked(self):
		# <!-- custom: A PR's own commits carry the marker without a number, so pushes to other branches and PR runs pass. (Claude code Opus 5.5) -->
		self.commit("base")
		self.assertTrue(checker.on_default_branch(self.repo, "local", {}))
		self.assertTrue(checker.on_default_branch(self.repo, "push", {"ref": "refs/heads/main", "repository": {"default_branch": "main"}}))
		self.assertFalse(checker.on_default_branch(self.repo, "push", {"ref": "refs/heads/feature", "repository": {"default_branch": "main"}}))
		self.assertFalse(checker.on_default_branch(self.repo, "pull_request", {}))
		git(self.repo, "checkout", "-q", "-b", "feature")
		self.assertFalse(checker.on_default_branch(self.repo, "local", {}))


if __name__ == "__main__":
	unittest.main()

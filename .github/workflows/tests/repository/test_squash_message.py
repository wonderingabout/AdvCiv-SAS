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
import squash_message as checker


def git(repo, *args):
	return subprocess.check_output(["git", *args], cwd=repo).decode().strip()


class SquashMessageTests(unittest.TestCase):
	# <!-- custom: PR#50's drafted squash title lacked SGR210 (2026-11-22); the fixture PR bumps SGR, opens a KI and ships a DLL, so all three requirements show. (Claude code Opus 5.5) -->
	def setUp(self):
		self.folder = tempfile.TemporaryDirectory()
		self.repo = Path(self.folder.name)
		for args in (("init", "-q"), ("config", "user.name", "CI fixture"), ("config", "user.email", "fixture@example.invalid"), ("config", "commit.gpgsign", "false")):
			git(self.repo, *args)
		self.write(1, "")
		git(self.repo, "add", "-A")
		git(self.repo, "commit", "-qm", "base")
		self.base = git(self.repo, "rev-parse", "HEAD")
		self.write(2, '<a id="ki-7"></a>\n\n## KI#7 - new\n')
		(self.repo / "Assets").mkdir(exist_ok=True)
		(self.repo / "Assets" / "CvGameCoreDLL.dll").write_bytes(b"binary")
		git(self.repo, "add", "-A")
		git(self.repo, "commit", "-qm", "work")
		self.tip = git(self.repo, "rev-parse", "HEAD")

	def tearDown(self):
		self.folder.cleanup()

	def write(self, revision, known_issues):
		defines = self.repo / "Assets" / "XML" / "GlobalDefines_advciv_sas.xml"
		defines.parent.mkdir(parents=True, exist_ok=True)
		defines.write_text("<Civ4Defines><Define><DefineName>SAS_SGR_REVISION</DefineName><iDefineIntVal>%d</iDefineIntVal></Define></Civ4Defines>" % revision, "utf-8")
		issues = self.repo / checker.KNOWN_ISSUES
		issues.parent.mkdir(parents=True, exist_ok=True)
		issues.write_text("# Known Issues\n" + known_issues, "utf-8")

	def test_requirements_follow_the_whole_pr(self):
		labels, kis, dll = checker.requirements(self.repo, self.base, self.tip)
		self.assertEqual((labels, kis, dll), (["SGR2"], ["7"], True))

	def test_a_drafted_message_must_meet_them(self):
		requirements = checker.requirements(self.repo, self.base, self.tip)
		self.assertEqual(len(checker.message_errors("Carry the copies (KI#7, PR#5)\n\n- [ci_squash_pr]\n", *requirements)), 2)
		self.assertEqual(checker.message_errors("Carry the copies (KI#7, SGR2, PR#5)\n\n- [ci_update_dll]\n- [ci_squash_pr]\n", *requirements), [])
		self.assertEqual(len(checker.message_errors("Carry the copies (KI#70, SGR20, PR#5)\n\n- [ci_update_dll]\n- [ci_squash_pr]\n", *requirements)), 2)

	def test_the_title_names_the_pr_and_the_marker_stays(self):
		# <!-- custom: PR#50's drafted squash message, pasted over GitHub's own, lost both its PR number and the [ci_squash_pr] marker GitHub's body carries (2026-11-23). (Claude code Opus 5.5) -->
		self.assertEqual(len(checker.message_errors("Carry the copies\n\nbody\n", [], [], False)), 2)
		self.assertEqual(checker.message_errors("Carry the copies (PR#50)\n\n- [ci_squash_pr]\n", [], [], False), [])
		self.assertEqual(checker.message_errors("Carry the copies (PR#50)\n\n- [ci_squash_pr]\n", [], [], False, 50), [])
		self.assertEqual(len(checker.message_errors("Carry the copies (PR#49)\n\n- [ci_squash_pr]\n", [], [], False, 50)), 1)
		self.assertIn("the title names PR#50", checker.checklist([], [], False, 50))
		# <!-- custom: Codex's review (2026-11-23): a zero number passed, and a wrapped first paragraph was read as its first line only. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		self.assertEqual(len(checker.message_errors("Carry the copies (PR#0)\n\n- [ci_squash_pr]\n", [], [], False)), 1)
		self.assertEqual(checker.message_errors("Carry the copies\ncontinued (PR#50)\n\n- [ci_squash_pr]\n", [], [], False, 50), [])

	def test_only_the_joined_spelling_counts(self):
		# <!-- custom: GitHub's bare (#50) and a spaced PR do not name the PR; a numbered reference is one token, as KI#1104 is (the user, 2026-11-23). (Claude code Opus 5.5) -->
		self.assertEqual(len(checker.message_errors("Carry the copies (#50)\n\n- [ci_squash_pr]\n", [], [], False, 50)), 1)
		spaced_title = "Carry the copies (PR" + " #50)\n\n- [ci_squash_pr]\n"
		self.assertEqual(len(checker.message_errors(spaced_title, [], [], False, 50)), 2)

	def test_dll_rule_matches_the_dll_gate(self):
		# <!-- custom: Codex's review (2026-11-22): a DLL renamed away from .dll still needs the marker, as the DLL gate says, and the marker without any DLL change is refused there too. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		git(self.repo, "mv", "Assets/CvGameCoreDLL.dll", "Assets/CvGameCoreDLL.bin")
		git(self.repo, "commit", "-qm", "rename")
		tip = git(self.repo, "rev-parse", "HEAD")
		self.assertTrue(checker.requirements(self.repo, self.tip, tip)[2])
		self.assertEqual(len(checker.message_errors("Plain (PR#5)\n\n- [ci_update_dll]\n- [ci_squash_pr]\n", [], [], False)), 1)


if __name__ == "__main__":
	unittest.main()

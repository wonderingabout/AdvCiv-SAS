# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib, subprocess and tempfile build a disposable Git repository; sys locates the checker; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "hygiene"))
# <!-- custom: line_ending_churn is the checker under test. (Claude code Opus 5.5) -->
import line_ending_churn as checker

LINES = ["line %d" % i for i in range(40)]


class LineEndingChurnTests(unittest.TestCase):
	def setUp(self):
		self.folder = tempfile.TemporaryDirectory()
		self.addCleanup(self.folder.cleanup)
		self.repo = Path(self.folder.name)
		for args in (("init", "-q"), ("config", "user.name", "CI fixture"), ("config", "user.email", "fixture@example.invalid"), ("config", "commit.gpgsign", "false"), ("config", "core.autocrlf", "false")):
			subprocess.run(["git", *args], cwd=self.repo, check=True)
		self.commit("\n".join(LINES) + "\n", "Add the file")

	def commit(self, text, message):
		(self.repo / "doc.md").write_bytes(text.encode("utf-8"))
		subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
		subprocess.run(["git", "commit", "-q", "-m", message], cwd=self.repo, check=True)
		return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()

	def test_whole_file_switch_fails(self):
		self.assertEqual(len(checker.commit_errors(self.repo, self.commit("\r\n".join(LINES) + "\r\n", "Edit one line"))), 1)

	def test_ordinary_edit_passes(self):
		self.assertEqual(checker.commit_errors(self.repo, self.commit("\n".join(LINES[:-1] + ["changed"]) + "\n", "Edit one line")), [])

	def test_marker_allows_a_deliberate_conversion(self):
		self.assertEqual(checker.commit_errors(self.repo, self.commit("\r\n".join(LINES) + "\r\n", "Convert line endings of doc.md to CRLF")), [])


if __name__ == "__main__":
	unittest.main()

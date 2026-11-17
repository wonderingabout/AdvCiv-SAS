# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib, subprocess and tempfile build a disposable Git repository; sys locates the checker; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "hygiene"))
# <!-- custom: line_endings is the checker under test; only its stored-endings rule is tested here. (Claude code Opus 5.5) -->
import line_endings as checker


class StoredLineEndingTests(unittest.TestCase):
	def setUp(self):
		self.folder = tempfile.TemporaryDirectory()
		self.addCleanup(self.folder.cleanup)
		self.repo = Path(self.folder.name)
		for args in (("init", "-q"), ("config", "core.autocrlf", "false")):
			subprocess.run(["git", *args], cwd=self.repo, check=True)

	def stage(self, name, data):
		(self.repo / name).write_bytes(data)
		subprocess.run(["git", "add", name], cwd=self.repo, check=True)

	def test_stored_crlf_fails(self):
		self.stage("doc.md", b"one\r\ntwo\r\n")
		self.assertEqual([issue.relative_path.as_posix() for issue in checker.stored_crlf_issues(self.repo)], ["doc.md"])

	def test_stored_lf_passes(self):
		self.stage("doc.md", b"one\ntwo\n")
		self.assertEqual(checker.stored_crlf_issues(self.repo), [])

	def test_crlf_kind_must_stay_crlf(self):
		# <!-- custom: A kind marked -text, such as theme files, is CRLF everywhere, so storing one as LF fails and as CRLF passes. (Claude code Opus 5.5) -->
		(self.repo / ".gitattributes").write_bytes(b"*.thm -text\n")
		self.stage("good.thm", b"a\r\nb\r\n")
		self.stage("bad.thm", b"a\nb\n")
		self.assertEqual([issue.relative_path.as_posix() for issue in checker.stored_crlf_issues(self.repo)], ["bad.thm"])

	def test_binary_is_ignored(self):
		self.stage("art.dds", b"\0\r\n\0")
		self.assertEqual(checker.stored_crlf_issues(self.repo), [])


if __name__ == "__main__":
	unittest.main()

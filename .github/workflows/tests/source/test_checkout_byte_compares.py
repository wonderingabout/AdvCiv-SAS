# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile build a small fake build folder; sys locates the checker; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
# <!-- custom: checkout_byte_compares is the checker under test. (Claude code Opus 5.5) -->
import checkout_byte_compares as checker


class CheckoutByteCompareTests(unittest.TestCase):
	def errors(self, source):
		with tempfile.TemporaryDirectory() as folder:
			path = Path(folder) / "check.py"
			path.write_text(source, encoding="utf-8")
			return checker.file_errors(path, "check.py")

	def test_unexplained_byte_comparison_fails(self):
		self.assertEqual(len(self.errors("if generated.read_bytes() != committed.read_bytes():\n\tpass\n")), 1)
		self.assertEqual(len(self.errors("same = data == path.read_bytes()\n")), 1)

	def test_text_comparison_and_explained_bytes_pass(self):
		self.assertEqual(self.errors("if generated.read_text(encoding='utf-8') != committed.read_text(encoding='utf-8'):\n\tpass\n"), [])
		self.assertEqual(self.errors("# bytes-compare: a DLL is binary\nif dll.read_bytes() != built:\n\tpass\n"), [])
		self.assertEqual(self.errors("data = path.read_bytes()  # read only, no comparison\n"), [])


if __name__ == "__main__":
	unittest.main()

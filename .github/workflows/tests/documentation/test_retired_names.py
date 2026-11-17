# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile build a disposable list; sys locates the checker; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "documentation"))
# <!-- custom: retired_names is the checker under test. (Claude code Opus 5.5) -->
import retired_names as checker

# <!-- custom: old tool is listed with Checked no, so it must be left out. (Claude code Opus 5.5) -->
LIST = "# Retired names\n\n| Retired name | Current name | Checked | Renamed | Why |\n| --- | --- | --- | --- | --- |\n| `the pilot` | `SASPilot` | yes | 2026-11-17 | Renamed. |\n| `save transplanter` | `SASSaveTransplanter` | yes | 2026-11-17 | Renamed. |\n| `old tool` | `NewTool` | no | 2026-11-17 | Off while a branch catches up. |\n"


class RetiredNamesTests(unittest.TestCase):
	def names(self):
		with tempfile.TemporaryDirectory() as folder:
			path = Path(folder) / checker.LIST
			path.parent.mkdir(parents=True)
			path.write_text(LIST, encoding="utf-8")
			return checker.retired_names(Path(folder))

	def test_list_is_read_from_the_table(self):
		self.assertEqual(self.names(), ["the pilot", "save transplanter"])

	def test_retired_name_fails_whatever_its_case(self):
		self.assertEqual(len(checker.errors_in("Run the Save Transplanter first.\n", "a.md", self.names())), 1)

	def test_whole_words_only(self):
		# <!-- custom: The harbour sense, plural, must pass; the possessive is still the retired name. (Claude code Opus 5.5) -->
		self.assertEqual(checker.errors_in("Ports require the pilots and tugboats.\n", "a.md", self.names()), [])
		self.assertEqual(len(checker.errors_in("Found through the pilot's map.\n", "a.md", self.names())), 1)

	def test_current_name_passes(self):
		self.assertEqual(checker.errors_in("Run SASSaveTransplanter first.\n", "a.md", self.names()), [])

	def test_history_records_are_skipped(self):
		for path in ("_1_AdvCiv-SAS/Docs/dev_logs/log.txt", "LLM_Helpers/context/commit_diffs/x.diff", "_1_AdvCiv-SAS/Docs/Deprecated/retired_names.md"):
			self.assertTrue(checker.HISTORY.search(path), path)
		self.assertFalse(checker.HISTORY.search("_1_AdvCiv-SAS/Docs/README_Known_Issues.md"))


if __name__ == "__main__":
	unittest.main()

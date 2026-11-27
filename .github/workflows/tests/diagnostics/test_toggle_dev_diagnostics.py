# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the toggle beside define_values.py; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "LLM_Helpers" / "diagnostics"))

# <!-- custom: The development toggle, which switches settings in GlobalDefines_advciv_sas.xml and SASSessionTunables.py (KI#128.11). (Claude code Opus 5.5) -->
import toggle_dev_diagnostics as toggle


# <!-- custom: The toggle edits a SASSessionTunables.py setting through its top-level assignment: an assignment-shaped line inside a string is not it, a trailing comment and CRLF line endings stay, and only the integer changes, the three cases Codex's review (GPT-6.2-Sol) reproduced against the first, pattern-based version. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
class TunablesEditTests(unittest.TestCase):
	TEXT = 'X = """\r\nSAS_UI_DAWN_OF_MAN_ON = 5\r\n"""\r\nSAS_UI_DAWN_OF_MAN_ON = 1  # keep\r\nY = 2\r\n'

	def test_reads_the_top_level_assignment(self):
		self.assertEqual(toggle.get_value({toggle.TUNABLES_RELATIVE: self.TEXT}, "SAS_UI_DAWN_OF_MAN_ON"), 1)

	def test_changes_only_the_integer(self):
		texts = {toggle.TUNABLES_RELATIVE: self.TEXT}
		toggle.set_value(texts, "SAS_UI_DAWN_OF_MAN_ON", 0)
		self.assertEqual(texts[toggle.TUNABLES_RELATIVE], self.TEXT.replace("SAS_UI_DAWN_OF_MAN_ON = 1  # keep", "SAS_UI_DAWN_OF_MAN_ON = 0  # keep"))

	def test_a_missing_setting_stops(self):
		with self.assertRaises(SystemExit):
			toggle.get_value({toggle.TUNABLES_RELATIVE: "Y = 2\n"}, "SAS_UI_DAWN_OF_MAN_ON")


if __name__ == "__main__":
	unittest.main()

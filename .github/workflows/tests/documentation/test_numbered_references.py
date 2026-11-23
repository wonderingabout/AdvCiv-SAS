# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib finds the checker and the shared table, sys makes them importable and unittest checks them. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same helper checks-documentation.yml runs, and the table it shares with the commit-message check. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "documentation"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import numbered_references as checker
from reference_spellings import joined, spaced


# <!-- custom: Each spaced form is built from two pieces, so this file does not hold one for the check to find. (Claude code Opus 5.5) -->
SPACE = " "


class NumberedReferencesTests(unittest.TestCase):
	def test_spaced_references_are_found_and_joined(self):
		# <!-- custom: Pull requests were written both ways, 29 spaced against 5 joined, while KI numbers never were (the user, 2026-11-23). (Claude code Opus 5.5) -->
		text = "See [PR" + SPACE + "#31](url), pr" + SPACE + "#7, KI" + SPACE + "#1104 and SGR" + SPACE + "180's pilot."
		self.assertEqual(spaced(text), ["PR", "KI", "SGR"])
		self.assertEqual(joined(text), "See [PR#31](url), PR#7, KI#1104 and SGR180's pilot.")
		self.assertEqual(len(checker.file_errors("doc.md", "line one\n" + text + "\n")), 3)

	def test_known_issues_in_words_are_found_and_joined(self):
		# <!-- custom: The oldest KIs were cited in words, with "as of now" while their numbers were not yet stable (the user, 2026-11-23). (Claude code Opus 5.5) -->
		KNOWN = "known" + SPACE + "issue"
		text = "see " + KNOWN + " as of now 53.2.2, " + KNOWN + " number 22, as of now " + KNOWN + " 34 and [Known" + SPACE + "issue #71](url)."
		self.assertEqual(spaced(text), ["Known issue"])
		self.assertEqual(joined(text), "see KI#53.2.2, KI#22, KI#34 and [KI#71](url).")
		self.assertEqual(joined("see " + KNOWN + " of as now 88 and " + KNOWN + " as of 47."), "see KI#88 and KI#47.")

	def test_joined_and_unrelated_text_passes(self):
		for text in ("PR#50 and KI#1104 and SGR210", "C2C issue" + SPACE + "#1604", "EXPR" + SPACE + "#5", "SGR level 3", "PR" + SPACE + "#N", "the Known" + SPACE + "Issues section", "unknown" + SPACE + "issue 3"):
			self.assertEqual(spaced(text), [], text)


if __name__ == "__main__":
	unittest.main()

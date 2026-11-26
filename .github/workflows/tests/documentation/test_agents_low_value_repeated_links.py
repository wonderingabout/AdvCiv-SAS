# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys put the checker folder on the import path; unittest runs the tests. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/documentation"))
# <!-- custom: agents_low_value_repeated_links is the checker module under test, imported as checker. (Claude code Opus 5.5) -->
import agents_low_value_repeated_links as checker

ANCHORS = {"7", "7.2", "70"}


def linked(number):
	return checker.link(number)


class AgentsLowValueRepeatedLinksTests(unittest.TestCase):
	def test_only_first_linked_passes(self):
		text = "See %s, then KI#7.2 and KI#70." % linked("7")
		errors, fixed, _ = checker.process(text, ANCHORS)
		self.assertEqual(errors, [])
		self.assertEqual(fixed, text)

	def test_unlinked_first_mention_is_linked(self):
		errors, fixed, _ = checker.process("KI#7 and KI#70.", ANCHORS)
		self.assertEqual(len(errors), 1)
		self.assertEqual(fixed, "%s and KI#70." % linked("7"))

	def test_later_links_are_unlinked(self):
		errors, fixed, _ = checker.process("%s, then %s and %s" % (linked("7"), linked("7.2"), linked("7")), ANCHORS)
		self.assertEqual(len(errors), 2)
		self.assertEqual(fixed, "%s, then KI#7.2 and KI#7" % linked("7"))

	def test_code_and_missing_numbers_are_not_linked(self):
		text = "`rg \"KI#7\b\"` finds it; KI#176.2 was merged; %s" % linked("70")
		errors, fixed, _ = checker.process(text, ANCHORS)
		self.assertEqual(errors, [])
		self.assertEqual(fixed, text)

	def test_mention_inside_other_link_label_is_kept(self):
		text = "[the KI#7 tool](/tool.md) then %s" % linked("7")
		errors, fixed, _ = checker.process(text, ANCHORS)
		self.assertEqual(errors, [])

	def test_repository_passes(self):
		self.assertEqual(checker.main([]), 0)


if __name__ == "__main__":
	unittest.main()

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: importlib loads the check from its file, as in test_lint_suppressions.py. (Claude code Opus 5.5) -->
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
_SPEC = importlib.util.spec_from_file_location("advisor_tab_registry", ROOT / ".github/workflows/build/source/advisor_tab_registry.py")
assert _SPEC is not None and _SPEC.loader is not None
advisor_tab_registry = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(advisor_tab_registry)

ENUMS = '''MILITARY_ADVISOR = 14
ADVISOR_TABS = (
	("military", MILITARY_ADVISOR, "CONTROL_MILITARY_SCREEN", ( # F5
		("SUMMARY", "TXT_KEY_SUMMARY_TAB", None),
		("MAP", "TXT_KEY_MAP_TAB", None),
	)),
)
'''
HOTKEYS = {"CONTROL_MILITARY_SCREEN": "F5"}
TEXT = {"TXT_KEY_SUMMARY_TAB", "TXT_KEY_MAP_TAB"}


class AdvisorTabRegistryTests(unittest.TestCase):
	def registry(self, text=ENUMS):
		(advisors, problems) = advisor_tab_registry.parse_registry(text)
		self.assertEqual(problems, [])
		return advisors

	def test_consistent_registry_passes(self):
		self.assertEqual(advisor_tab_registry.check_registry(self.registry(), HOTKEYS, TEXT), [])

	def test_hotkey_comment_must_match_the_control(self):
		# <!-- custom: The hotkey comments were added at the user's request, checked so a remapped key cannot leave a stale comment. (Claude code Opus 5.5) -->
		problems = advisor_tab_registry.check_registry(self.registry(), {"CONTROL_MILITARY_SCREEN": "F6"}, TEXT)
		self.assertIn("hotkey comment says F5", problems[0])

	def test_unknown_text_key_fails(self):
		problems = advisor_tab_registry.check_registry(self.registry(), HOTKEYS, {"TXT_KEY_SUMMARY_TAB"})
		self.assertIn("TXT_KEY_MAP_TAB", problems[0])

	def test_screen_with_its_own_tab_list_fails(self):
		# <!-- custom: The shape the registry replaced: a screen drawing tabs from a literal list of its own. (Claude code Opus 5.5) -->
		problems = advisor_tab_registry.check_screens({"Screens/CvNewAdvisor.py": 'self.PAGE_NAME_LIST = ["TXT_KEY_A", "TXT_KEY_B"]\ndrawAdvisorFooterTabs(screen, ids, labels)\n'})
		self.assertEqual(len(problems), 2)

	def test_screen_reading_the_registry_passes(self):
		self.assertEqual(advisor_tab_registry.check_screens({"Screens/CvNewAdvisor.py": 'self.PAGE_NAME_LIST = []\nself.PAGE_NAME_LIST[:] = getAdvisorTabLabels("x")\ndrawAdvisorFooterTabs(screen, ids, labels)\n'}), [])

	def test_new_tab_needs_a_command_entry(self):
		ui = '_TAB_COMMANDS = {\n\t"military/SUMMARY": ("military", None),\n}\n'
		problems = advisor_tab_registry.check_commands(self.registry(), ui)
		self.assertEqual(len(problems), 1)
		self.assertIn("military/MAP", problems[0])

	def test_unrelated_and_duplicate_command_keys_fail(self):
		ui = '_TAB_COMMANDS = {"military/SUMMARY": ("military", None), "military/SUMMARY": (None, "other")}\n'
		ui += 'other = {"military/MAP": ("units", None)}\n'
		problems = advisor_tab_registry.check_commands(self.registry(), ui)
		self.assertEqual(len(problems), 2)
		self.assertIn("duplicate _TAB_COMMANDS entry military/SUMMARY", problems[0])
		self.assertIn("military/MAP", problems[1])

	def test_command_must_exist_or_carry_a_note(self):
		# <!-- custom: Codex's review (2026-11-27): "battlez" for "battles" passed while only keys were checked. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		ui = '_TAB_COMMANDS = {"military/SUMMARY": ("battlez", None), "military/MAP": (None, None)}\n'
		problems = advisor_tab_registry.check_commands(self.registry(), ui, advisor_tab_registry.command_names(["def cmd_battles(args):\n"]))
		self.assertEqual(len(problems), 2)
		self.assertIn("'battlez', which is no SASPilot command", problems[0])
		self.assertIn("military/MAP has no command", problems[1])

	def test_comments_do_not_count_and_multiline_literal_fails(self):
		text = '# getAdvisorTabLabels("military")\nself.PAGE_NAME_LIST[:] = [\n\t"SUMMARY",\n]\n'
		text += 'drawAdvisorFooterTabs(screen, ids, labels)\n'
		problems = advisor_tab_registry.check_screens({"Screens/CvNewAdvisor.py": text})
		self.assertEqual(len(problems), 2)

	def test_malformed_tab_reports_its_line(self):
		text = ENUMS.replace('("MAP", "TXT_KEY_MAP_TAB", None)', '("MAP", "TXT_KEY_MAP_TAB")')
		(advisors, problems) = advisor_tab_registry.parse_registry(text)
		self.assertEqual(len(advisors[0]["tabs"]), 1)
		self.assertIn("line 5: a tab is", problems[0])

	def test_dll_info_page_must_match_the_registry(self):
		# <!-- custom: CvDLLWidgetData.cpp opens Info on Score with showInfoScreen(1); a registry with another tab second, or a new number in the DLL, fails. See KI#1110. (Claude code Opus 5.5) -->
		info = '''INFO_SCREEN = 18
ADVISOR_TABS = (
	("info", INFO_SCREEN, "CONTROL_INFO", ( # F8
		("GRAPH", "TXT_KEY_GRAPH", None),
		("TIMELINE", "TXT_KEY_TIMELINE", None),
		("SCORE", "TXT_KEY_SCORE", None),
	)),
)
'''
		problems = advisor_tab_registry.check_dll_info_pages(self.registry(info), {"CvDLLWidgetData.cpp": "py.showInfoScreen(1);\npy.showInfoScreen(4);\n"})
		self.assertEqual(len(problems), 2)
		self.assertIn("meant as SCORE, but the registry has TIMELINE", problems[0])
		self.assertIn("does not name", problems[1])


if __name__ == "__main__":
	unittest.main()

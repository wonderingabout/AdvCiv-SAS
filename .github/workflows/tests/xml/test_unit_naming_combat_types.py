# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: importlib loads the check from its file, as in the source tests. (Claude code Opus 5.5) -->
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
_SPEC = importlib.util.spec_from_file_location("unit_naming_combat_types", ROOT / ".github/workflows/build/xml/unit_naming_combat_types.py")
assert _SPEC is not None and _SPEC.loader is not None
unit_naming_combat_types = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(unit_naming_combat_types)


def tags(*names):
	return {"TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_%s_%s" % (name.upper(), suffix) for name in names for suffix in ("TEXT", "HOVER")}


class UnitNamingCombatTypeTests(unittest.TestCase):
	def test_matching_options_pass(self):
		self.assertEqual(unit_naming_combat_types.check({"SIEGE"}, ["None", "SIEGE"], ["None", "SIEGE"], tags("None", "SIEGE")), [])

	def test_split_type_without_option_fails(self):
		# <!-- custom: The KI#1087 case: the old MELEE option kept, the split types missing. (Claude code Opus 5.5) -->
		failures = unit_naming_combat_types.check({"MELEE_SHOCK"}, ["None", "MELEE"], ["None", "MELEE"], tags("None", "MELEE"))
		self.assertTrue(any("no Combat_MELEE_SHOCK option" in failure for failure in failures))
		self.assertTrue(any("Combat_MELEE names no unit combat type" in failure for failure in failures))

	def test_missing_text_fails(self):
		failures = unit_naming_combat_types.check({"SIEGE"}, ["None", "SIEGE"], ["None", "SIEGE"], tags("None"))
		self.assertEqual(len(failures), 2)


if __name__ == "__main__":
	unittest.main()

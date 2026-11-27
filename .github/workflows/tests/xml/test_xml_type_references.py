# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the checker; tempfile builds a fixture repository; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "xml"))

# <!-- custom: The check that references to types the carried XML defines name a defined type (KI#1104.3). (Claude code Opus 5.5) -->
import xml_type_references as checker


# <!-- custom: A defined formation type passes, and NONE counts as no reference; a misspelt one fails, as does a rule that finds no reference at all, which would otherwise check nothing. (Claude code Opus 5.5) -->
class TypeReferenceTests(unittest.TestCase):
	def setUp(self):
		temporary = tempfile.TemporaryDirectory()
		self.addCleanup(temporary.cleanup)
		self.repo = Path(temporary.name)
		(self.repo / "Assets/XML/Units").mkdir(parents=True)
		(self.repo / "Assets/XML/Units/CIV4FormationInfos.xml").write_text("<UnitFormations><UnitFormation><FormationType>FORMATION_TYPE_DEFAULT</FormationType></UnitFormation><UnitFormation><FormationType>FORMATION_TYPE_DEFAULT</FormationType></UnitFormation></UnitFormations>", encoding="utf-8")
		self.rules = checker.RULES
		checker.RULES = ((("Units/CIV4UnitInfos.xml",), "FormationType", "Units/CIV4FormationInfos.xml", "UnitFormation/FormationType"),)
		self.addCleanup(setattr, checker, "RULES", self.rules)

	def units(self, *values):
		(self.repo / "Assets/XML/Units/CIV4UnitInfos.xml").write_text("<Civ4UnitInfos>" + "".join("<UnitInfo><FormationType>%s</FormationType></UnitInfo>" % value for value in values) + "</Civ4UnitInfos>", encoding="utf-8")

	def test_defined_type_passes(self):
		self.units("FORMATION_TYPE_DEFAULT", "NONE")
		self.assertEqual(checker.check(self.repo), ([], 1))

	def test_misspelt_type_fails(self):
		self.units("FORMATION_TYPE_DEFAULT", "FORMATION_TYPE_DEFUALT")
		failures, _ = checker.check(self.repo)
		self.assertEqual(len(failures), 1)

	def test_rule_with_no_reference_fails(self):
		self.units()
		failures, _ = checker.check(self.repo)
		self.assertEqual(len(failures), 1)


if __name__ == "__main__":
	unittest.main()

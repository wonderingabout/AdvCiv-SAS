# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates minimal XML files; unittest exercises the limit rules. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real XML readers and audit rather than duplicating them. (Claude code Opus 5.5) -->
import corporation_prereq_bonuses as check


def corporation(corporation_type, inputs):
    return "<CorporationInfo><Type>%s</Type><PrereqBonuses>%s</PrereqBonuses></CorporationInfo>" % (corporation_type, "".join("<BonusType>%s</BonusType>" % b for b in inputs))


class CorporationPrereqBonusesTests(unittest.TestCase):
    def root(self, corporations_xml, defines_xml=None):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        path = root / check.CORPORATION_INFOS_REL_PATH
        path.parent.mkdir(parents=True)
        path.write_text("<Root>" + corporations_xml + "</Root>", encoding="utf-8")
        if defines_xml is not None:
            defines = root / check.SAS_DEFINES_REL_PATH
            defines.parent.mkdir(parents=True, exist_ok=True)
            defines.write_text("<Civ4Defines>" + defines_xml + "</Civ4Defines>", encoding="utf-8")
        return root

    def test_five_inputs_pass_and_six_fail_at_the_bts_limit(self):
        root = self.root(corporation("CORPORATION_A", ["B1", "B2", "B3", "B4", "B5"]) + corporation("CORPORATION_B", ["B1", "B2", "B3", "B4", "B5", "B6"]))
        failures = check.check_corporation_inputs(check.read_corporations(root), check.read_limit(root))
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("CORPORATION_B", failures[0])

    def test_sas_override_raises_the_limit(self):
        root = self.root(corporation("CORPORATION_B", ["B1", "B2", "B3", "B4", "B5", "B6"]), "<Define><DefineName>NUM_CORPORATION_PREREQ_BONUSES</DefineName><iDefineIntVal>6</iDefineIntVal></Define>")
        self.assertEqual(check.check_corporation_inputs(check.read_corporations(root), check.read_limit(root)), [])

    def test_duplicate_input_fails(self):
        root = self.root(corporation("CORPORATION_A", ["B1", "B1"]))
        failures = check.check_corporation_inputs(check.read_corporations(root), check.read_limit(root))
        self.assertEqual(len(failures), 1, failures)


if __name__ == "__main__":
    unittest.main()

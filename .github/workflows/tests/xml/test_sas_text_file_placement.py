# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates the fixture text files; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real text scan rather than duplicating it. (Claude code Opus 5.5) -->
import sas_text_file_placement as placement


def entry(tag):
    return f"<TEXT><Tag>{tag}</Tag><English>x</English></TEXT>"


class SasTextFilePlacementTests(unittest.TestCase):
    # <!-- custom: civilopedia lists the keys a fixture infos file uses as <Civilopedia> values; by default every _PEDIA key in the text files. (Claude code Opus 5.5) -->
    def run_check(self, files, civilopedia=None):
        if civilopedia is None:
            civilopedia = [tag for tags in files.values() for tag in tags if tag.endswith("_PEDIA")]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            infos = root / "Assets/XML/Units/CIV4UnitInfos.xml"
            infos.parent.mkdir(parents=True, exist_ok=True)
            infos.write_text("<Root>" + "".join(f"<UnitInfo><Civilopedia>{tag}</Civilopedia></UnitInfo>" for tag in civilopedia) + "</Root>", encoding="utf-8")
            for name, tags in files.items():
                path = root / placement.TEXT_DIR / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("<Civ4GameText>" + "".join(entry(tag) for tag in tags) + "</Civ4GameText>", encoding="utf-8")
            return placement.check(root)

    def test_pedia_and_concept_files_pass(self):
        self.assertEqual(self.run_check({placement.PEDIA_FILE: ["TXT_KEY_UNIT_WARRIOR_PEDIA"], placement.CONCEPT_FILE: ["TXT_KEY_CONCEPT_RIVERS_PEDIA"], "AdvCiv-SAS_main.xml": ["TXT_KEY_UNIT_WARRIOR"]}), [])

    # <!-- custom: The City Center case: a pedia text in AdvCiv-SAS_main.xml. (Claude code Opus 5.5) -->
    def test_pedia_outside_lengthy_fails(self):
        self.assertEqual(len(self.run_check({"AdvCiv-SAS_main.xml": ["TXT_KEY_BUILDING_CITY_CENTER_PEDIA"]})), 1)

    def test_concept_outside_core_fails(self):
        self.assertEqual(len(self.run_check({placement.PEDIA_FILE: ["TXT_KEY_CONCEPT_RIVERS_PEDIA"]})), 1)

    def test_civilopedia_text_without_pedia_suffix_fails(self):
        self.assertEqual(len(self.run_check({placement.PEDIA_FILE: ["TXT_KEY_UNIT_WARRIOR_TEXT"]}, ["TXT_KEY_UNIT_WARRIOR_TEXT"])), 1)

    def test_pedia_text_unused_by_civilopedia_fails(self):
        self.assertEqual(len(self.run_check({placement.PEDIA_FILE: ["TXT_KEY_UNIT_WARRIOR_PEDIA"]}, [])), 1)

    # <!-- custom: The BtS-style concept page name. (Claude code Opus 5.5) -->
    def test_pedia_sr_suffix_passes(self):
        self.assertEqual(self.run_check({placement.CONCEPT_FILE: ["TXT_KEY_BASE_ADVCIV_SOME_CHANGES_PEDIA_SR"]}, ["TXT_KEY_BASE_ADVCIV_SOME_CHANGES_PEDIA_SR"]), [])

    def test_commented_out_entries_are_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / placement.TEXT_DIR / "AdvCiv-SAS_main.xml"
            path.parent.mkdir(parents=True)
            path.write_text("<Civ4GameText><!-- " + entry("TXT_KEY_UNIT_OLD_PEDIA") + " --></Civ4GameText>", encoding="utf-8")
            self.assertEqual(placement.check(root), [])


if __name__ == "__main__":
    unittest.main()

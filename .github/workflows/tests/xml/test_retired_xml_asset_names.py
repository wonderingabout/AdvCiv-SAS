# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates the fixture doc and code; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real table parsing and code scan rather than duplicating them. (Claude code Opus 5.5) -->
import retired_xml_asset_names as retired

DOC = "| Retired SAS machine family | Current | Name |\n| --- | --- | --- |\n| `BONUS_GRAPES`, `TXT_KEY_BONUS_GRAPES*` | `BONUS_WINE` | Grapes |\n"


class RetiredXmlAssetNamesTests(unittest.TestCase):
    def run_check(self, xml):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / retired.MAP_FILE).parent.mkdir(parents=True)
            (root / retired.MAP_FILE).write_text(DOC, encoding="utf-8")
            (root / "Assets/XML").mkdir(parents=True)
            (root / "Assets/XML/Test.xml").write_text(xml, encoding="utf-8")
            return retired.check(root)

    def test_retired_name_in_code_fails(self):
        self.assertEqual(len(self.run_check("<BonusType>BONUS_GRAPES</BonusType>\n<Civilopedia>TXT_KEY_BONUS_GRAPES_PEDIA</Civilopedia>")), 2)

    def test_comments_and_longer_names_pass(self):
        self.assertEqual(self.run_check("<!-- was BONUS_GRAPES -->\n<BonusType>BONUS_WINE</BonusType>\n<Type>HAS_BONUS_GRAPES_X</Type>"), [])


if __name__ == "__main__":
    unittest.main()

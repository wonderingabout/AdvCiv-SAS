# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates the canonical KI mapping plus active-source fixtures so tests cover declarations, lookup/cache spellings, XML comments, and historical-doc exclusion. (ChatGPT-5.6-Sol) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Import the production retired-name guard so fixtures validate its actual source/documentation policy and canonical map parser. (GPT-6.1-Sol) -->
import retired_global_define_names as retired


class RetiredGlobalDefineNameTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.write_map("SAS_OLD_SETTING", "SAS_NEW_SETTING")
        self.write("Assets/XML/GlobalDefines_advciv_sas.xml", "<Civ4Defines><Define><DefineName>SAS_NEW_SETTING</DefineName><iDefineIntVal>1</iDefineIntVal></Define></Civ4Defines>")

    def write(self, relative: str, text: str) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_map(self, old: str, new: str) -> None:
        self.write(
            str(retired.MAP_FILE),
            retired.MAP_START + "\n"
            "| Original name | Current name | Original bytes | Current bytes | Δ bytes |\n"
            "| --- | --- | ---: | ---: | ---: |\n"
            f"| `{old}` | `{new}` | {len(old)} | {len(new)} | {len(new) - len(old):+d} |\n"
            + retired.MAP_END + "\n",
        )

    def errors(self):
        return retired.check(self.repo)[0]

    def test_current_name_passes(self):
        self.write("CvGameCoreDLL/Test.cpp", 'GC.getDefineINT("SAS_NEW_SETTING");\n')
        self.assertEqual(self.errors(), [])

    def test_retired_runtime_lookup_fails(self):
        self.write("CvGameCoreDLL/Test.cpp", 'GC.getDefineINT("SAS_OLD_SETTING");\n')
        self.assertTrue(any("retired GlobalDefine name SAS_OLD_SETTING" in error for error in self.errors()))

    def test_retired_copied_cache_identifier_fails(self):
        for prefix in ("i", "IS_", "g_i"):
            with self.subTest(prefix=prefix):
                self.write("Assets/Python/Test.py", "self.%sSAS_OLD_SETTING = 1\n" % prefix)
                self.assertTrue(any("Assets/Python/Test.py" in error for error in self.errors()))

    def test_longer_unrelated_key_is_not_a_retired_name(self):
        self.write("Assets/Python/Test.py", 'value = "SAS_OLD_SETTING_EXTRA"\n')
        self.assertEqual(self.errors(), [])

    def test_reversed_mapping_markers_report_an_error(self):
        self.write(str(retired.MAP_FILE), retired.MAP_END + "\n" + retired.MAP_START)
        self.assertTrue(any("precedes" in error for error in self.errors()))

    def test_retired_xml_comment_fails(self):
        self.write("Assets/XML/Technologies/Test.xml", "<!-- see SAS_OLD_SETTING -->\n<Root/>\n")
        self.assertTrue(any("Technologies/Test.xml" in error for error in self.errors()))

    def test_current_documentation_fails_but_historical_evidence_passes(self):
        self.write("_1_AdvCiv-SAS/Docs/README_Current.md", "Use SAS_OLD_SETTING\n")
        self.assertTrue(any("README_Current.md" in error for error in self.errors()))
        self.write("_1_AdvCiv-SAS/Docs/README_Current.md", "Use SAS_NEW_SETTING\n")
        for name in retired.HISTORICAL_FILES - {retired.MAP_FILE.as_posix()}:
            self.write(name, "Historical spelling: SAS_OLD_SETTING\n")
        self.assertEqual(self.errors(), [])

    def test_mapping_current_name_must_exist(self):
        self.write("Assets/XML/GlobalDefines_advciv_sas.xml", "<Civ4Defines/>")
        self.assertTrue(any("missing or empty" in error for error in self.errors()))


if __name__ == "__main__":
    unittest.main()

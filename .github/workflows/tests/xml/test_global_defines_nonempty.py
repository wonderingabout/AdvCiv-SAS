# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates shipped XML layouts and unittest exercises content validation plus cross-file collisions. (GPT-6.1-Sol) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Run the existing content checker through its expanded shared namespace, rather than maintaining a second uniqueness implementation. (GPT-6.1-Sol) -->
import global_defines_nonempty as defines


class GlobalDefineContentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)

    def write(self, relative, *entries):
        target = self.repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "<Civ4Defines>" + "".join(
                f"<Define><DefineName>{name}</DefineName><iDefineIntVal>{value}</iDefineIntVal></Define>"
                for name, value in entries
            ) + "</Civ4Defines>",
            encoding="utf-8",
        )

    def errors(self):
        return defines.check_global_defines_nonempty(self.repo)

    def test_unique_names_across_root_callback_and_modules_pass(self):
        for index, path in enumerate((
            "Assets/XML/GlobalDefines_advc.xml",
            "Assets/XML/PythonCallbackDefines.xml",
            "Assets/Modules/Test/Test_GlobalDefines.xml",
            "Assets/Modules/Test/Test_PythonCallbackDefines.xml",
        )):
            self.write(path, (f"SETTING_{index}", 1))
        self.assertEqual(self.errors(), [])

    def test_same_file_duplicate_still_fails(self):
        self.write("Assets/XML/GlobalDefines.xml", ("SAS_SETTING", 1), ("SAS_SETTING", 2))
        errors = self.errors()
        self.assertEqual(len(errors), 1)
        self.assertIn("<Define> #2", errors[0])
        self.assertIn("<Define> #1", errors[0])

    def test_cross_file_duplicates_fail_even_for_equal_values(self):
        first = "Assets/XML/GlobalDefines.xml"
        second = "Assets/XML/GlobalDefines_advciv_sas.xml"
        for value in (1, 2):
            with self.subTest(value=value):
                self.write(first, ("SAS_PROD_SETTING", 1))
                self.write(second, ("SAS_PROD_SETTING", value))
                errors = self.errors()
                self.assertEqual(len(errors), 1)
                self.assertIn(first, errors[0].replace("\\", "/"))
                self.assertIn(second, errors[0].replace("\\", "/"))

    def test_callback_and_modular_collisions_are_all_reported(self):
        self.write("Assets/XML/GlobalDefines.xml", ("INHERITED_SETTING", 1), ("SAS_SETTING", 2))
        self.write("Assets/XML/PythonCallbackDefines.xml", ("INHERITED_SETTING", 1))
        self.write("Assets/Modules/Test/Test_GlobalDefines.xml", ("SAS_SETTING", 2))
        self.assertEqual(len(self.errors()), 2)

    def test_expanded_scope_keeps_value_validation(self):
        self.write("Assets/XML/PythonCallbackDefines.xml", ("SAS_CALLBACK", ""))
        self.assertTrue(any("empty value" in error for error in self.errors()))


if __name__ == "__main__":
    unittest.main()

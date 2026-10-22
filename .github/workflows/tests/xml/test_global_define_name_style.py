# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates XML fixtures and unittest exercises the naming boundary without requiring the in-progress current tree to pass it. (GPT-6.1-Sol) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the separate 42-byte naming policy directly; the existing global_define_lengths tests continue to own the unrelated 255-byte loader-safety boundary. (ChatGPT-5.6-Sol) -->
import global_define_name_style as style


class GlobalDefineNameStyleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)

    def write_define(self, relative: str, name: str) -> None:
        target = self.repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "<Civ4Defines><Define><DefineName>"
            + name
            + "</DefineName><iDefineIntVal>1</iDefineIntVal></Define></Civ4Defines>",
            encoding="utf-8",
        )

    def errors(self) -> list[str]:
        return style.check(self.repo)[0]

    def test_exact_42_byte_name_passes(self):
        self.write_define("Assets/XML/GlobalDefines.xml", "N" * 42)
        self.assertEqual(self.errors(), [])

    def test_43_byte_name_fails(self):
        self.write_define("Assets/XML/GlobalDefines.xml", "N" * 43)
        self.assertTrue(any("DefineName is 43 UTF-8 bytes" in error for error in self.errors()))

    def test_counts_utf8_bytes_not_characters(self):
        self.write_define("Assets/XML/GlobalDefines.xml", "é" * 22)
        self.assertTrue(any("DefineName is 44 UTF-8 bytes" in error for error in self.errors()))

    def test_inherited_names_are_not_exempt(self):
        self.write_define("Assets/XML/GlobalDefinesAlt.xml", "INHERITED_" + "X" * 34)
        self.assertTrue(any("GlobalDefinesAlt.xml" in error for error in self.errors()))

    def test_python_callback_and_modular_files_are_checked(self):
        self.write_define("Assets/XML/PythonCallbackDefines.xml", "P" * 43)
        self.write_define("Assets/Modules/Test/Synthetic_GlobalDefines.xml", "M" * 43)
        errors = self.errors()
        self.assertTrue(any("PythonCallbackDefines.xml" in error for error in errors))
        self.assertTrue(any("Synthetic_GlobalDefines.xml" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates the fixture text and manifest; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real entry parsing and hashing rather than duplicating them. (Claude code Opus 5.5) -->
import xml_sas_text_inherited as inherited


class SasTextInheritedTests(unittest.TestCase):
    def run_check(self, english):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            text = root / "Assets/XML/Text/AdvCiv-SAS_main.xml"
            text.parent.mkdir(parents=True)
            text.write_bytes(("<Civ4GameText><TEXT>\r\n<Tag>TXT_KEY_TEST</Tag>\r\n<English>" + english + "</English>\r\n</TEXT></Civ4GameText>").encode("utf-8"))
            manifest = root / "hashes.tsv"
            manifest.write_text(inherited.MANIFEST_HEADER + "\nTXT_KEY_TEST\tvanilla\t" + inherited.english_hash("Sailing - Quote") + "\n", encoding="utf-8")
            original = inherited.MANIFEST
            inherited.MANIFEST = manifest
            try:
                return inherited.check(root)
            finally:
                inherited.MANIFEST = original

    def test_identical_english_fails(self):
        self.assertEqual(len(self.run_check("Sailing - Quote")), 1)

    def test_any_character_change_passes(self):
        self.assertEqual(self.run_check("Sailing - Quote "), [])
        self.assertEqual(self.run_check("Sailing: Quote"), [])

    def test_line_endings_alone_do_not_count(self):
        self.assertEqual(inherited.english_hash("a\r\nb"), inherited.english_hash("a\nb"))


if __name__ == "__main__":
    unittest.main()

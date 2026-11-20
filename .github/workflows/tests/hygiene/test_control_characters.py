# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys/unittest are the usual test scaffolding; control_characters is the checker under test. (Claude Code Sonnet 5.5) -->
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/hygiene"))
# <!-- custom: control_characters is the checker module under test, imported as checker. (Claude Code Sonnet 5.5) -->
import control_characters as checker


class ControlCharacterTests(unittest.TestCase):
    def test_nul_and_bel_are_reported_with_line_and_context(self):
        errors = checker.control_errors("AGENTS.md", b"fine\n(`\x00.610_tech_tree`, `\x07dvisors`)\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("AGENTS.md:2", errors[0])
        self.assertIn("0x00", errors[0])
        self.assertIn("0x07", errors[0])
        self.assertIn("<0x00>.610_tech_tree", errors[0])

    def test_tab_and_crlf_are_allowed(self):
        self.assertEqual(checker.control_errors("a.py", b"\tx = 1\r\n\r\n"), [])

    # <!-- custom: The 2026-11-13 case: a shell turned "\find.exe" into a form feed and "ind.exe" in the Makefile. See KI#38.7. (Claude code Opus 5.5) -->
    def test_form_feed_from_a_lost_backslash_is_reported(self):
        errors = checker.control_errors("CvGameCoreDLL/Project/Makefile", b"FOR /F %%i IN ('%SystemRoot%\\System32\x0cind.exe /c') DO\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("0x0C", errors[0])
        self.assertIn("System32<0x0C>ind.exe", errors[0])

    def test_tsv_manifests_are_scanned(self):
        self.assertTrue(checker.is_text_path(".github/workflows/build/xml/xml_sas_text_inherited_hashes.tsv"))

    def test_only_text_formats_are_scanned(self):
        self.assertTrue(checker.is_text_path("AGENTS.md"))
        self.assertTrue(checker.is_text_path(".gitattributes"))
        self.assertFalse(checker.is_text_path("Assets/Res/Cursors/Waiting.ani"))
        self.assertFalse(checker.is_text_path("_1_AdvCiv-SAS/Windows_shortcuts/x.lnk"))
        self.assertFalse(checker.is_text_path("_0_Legacy/Docs/BUG/BUG Mod Help-ENG.chm"))


if __name__ == "__main__":
    unittest.main()

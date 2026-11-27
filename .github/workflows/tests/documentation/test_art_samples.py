# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib, sys, tempfile and unittest build a throwaway repository of renderer files. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/documentation"))
# <!-- custom: art_samples is the checker module under test, imported as checker. (Claude code Opus 5.5) -->
import art_samples as checker


class ArtSamplesTests(unittest.TestCase):
    def repository(self, folder):
        root = Path(folder)
        (root / "LLM_Helpers" / "art_viewing").mkdir(parents=True)
        for name in checker.RENDERER_FILES:
            (root / name).write_text("value = 1\n", encoding="utf-8")
        return root

    def test_missing_fingerprint_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertTrue(checker.check(self.repository(folder)))

    def test_comment_edit_keeps_samples_fresh(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.repository(folder)
            checker.write(root)
            (root / checker.RENDERER_FILES[0]).write_text("# a new comment\n\nvalue = 1  # and another\n", encoding="utf-8")
            self.assertEqual(checker.check(root), [])

    def test_code_edit_asks_for_new_samples(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.repository(folder)
            checker.write(root)
            (root / checker.RENDERER_FILES[0]).write_text("value = 2\n", encoding="utf-8")
            self.assertTrue(checker.check(root))


if __name__ == "__main__":
    unittest.main()

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Standard-library modules build throwaway git repositories (tempfile, subprocess, pathlib) for the check() test and run unittest; sys.path lets the test import the checker module, imported below as checker. (Claude Code Sonnet 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/documentation"))
# <!-- custom: image_filename_policy is the checker module under test, imported as checker. (Claude Code Sonnet 5.5) -->
import image_filename_policy as checker


class ImageFilenamePolicyTests(unittest.TestCase):
    def test_valid_legacy_sas_and_descriptive_names_pass(self):
        self.assertEqual(checker.filename_errors([
            "_0_Legacy/Images/advisors/0.400_foreign_advisor_relations.JPG",
            "_1_AdvCiv-SAS/Images/advisors/1.513_foreign_advisor (1).JPG",
            "_1_AdvCiv-SAS/Images/LLM/chatgpt_example.PNG",
        ]), [])

    def test_wrong_numbered_namespace_fails(self):
        errors = checker.filename_errors([
            "_0_Legacy/Images/advisors/1.400_foreign_advisor_relations.JPG",
            "_1_AdvCiv-SAS/Images/advisors/0.513_foreign_advisor.JPG",
            "_1_AdvCiv-SAS/Images/advisors/2.513_foreign_advisor.JPG",
        ])
        self.assertEqual(len(errors), 3)

    def test_duplicate_basenames_are_case_insensitive_across_image_trees(self):
        errors = checker.filename_errors([
            "_0_Legacy/Images/advisors/0.400_same.JPG",
            "_1_AdvCiv-SAS/Images/ui_other/0.400_SAME.jpg",
        ])
        self.assertTrue(any("duplicate maintained image basename" in error for error in errors))

    def test_legacy_folders_must_exist_in_sas_tree(self):
        errors = checker.filename_errors([
            "_0_Legacy/Images/advisors/0.400_a.JPG",
            "_0_Legacy/Images/legacy_only/0.401_b.JPG",
            "_0_Legacy/Docs/BBAI/readme.txt",
            "_1_AdvCiv-SAS/Images/advisors/1.513_c.JPG",
            "_1_AdvCiv-SAS/Docs/README_Known_Issues.md",
        ])
        self.assertEqual(len(errors), 1)
        self.assertIn("legacy_only", errors[0])

    def test_unrelated_game_assets_are_outside_policy(self):
        self.assertEqual(checker.filename_errors([
            "Assets/Art/Interface/Button.dds",
            "Assets/Art/Units/Button.dds",
        ]), [])

    def test_check_reads_tracked_and_untracked_current_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.DEVNULL)
            git("init", "-q")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            tracked = root / "_1_AdvCiv-SAS/Images/advisors/1.500_screen.JPG"
            tracked.parent.mkdir(parents=True)
            tracked.write_bytes(b"fixture")
            git("add", ".")
            git("commit", "-qm", "baseline")
            self.assertEqual(checker.check(root), [])
            duplicate = root / "_0_Legacy/Images/advisors/1.500_screen.JPG"
            duplicate.parent.mkdir(parents=True)
            duplicate.write_bytes(b"fixture")
            errors = checker.check(root)
            self.assertTrue(any("legacy/reference image filenames" in error for error in errors))
            self.assertTrue(any("duplicate maintained image basename" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

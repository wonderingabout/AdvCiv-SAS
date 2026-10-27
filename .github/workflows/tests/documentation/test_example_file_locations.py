# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Exercise production filename/location rules without opening example payloads or duplicating their classifier in test code. (GPT-6.1-Sol) -->
from pathlib import Path
import sys
import unittest
# <!-- custom: Real temporary Git history checks that normal runs select changes and renames, while --all still detects an older misplaced artifact. (GPT-6.1-Sol) -->
import subprocess
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/documentation"))
# <!-- custom: Test the actual documentation placement helper, including the screenshots/test-module distinctions found during the initial inventory. (GPT-6.1-Sol) -->
import example_file_locations as checker


class ExampleFileLocationTests(unittest.TestCase):
    def test_misplaced_text_code_and_data_examples_fail(self):
        for path in ("LLM_Helpers/output_example.txt", "sample_EXAMPLE.json", "Assets/Python/source_example.py"):
            with self.subTest(path=path):
                self.assertEqual(len(checker.placement_errors([path])), 1)

    def test_examples_and_screenshot_hierarchy_pass(self):
        self.assertEqual(checker.placement_errors([
            "_1_AdvCiv-SAS/Docs/examples/light_source/packaging_refresh_example.txt",
            "_1_AdvCiv-SAS/Docs/examples/source_comparison/source_example.py",
            "_1_AdvCiv-SAS/Images/diagnostics/0.290_SASGameRecord_log_vs_code.PNG",
        ]), [])
        self.assertTrue(checker.placement_errors(["_1_AdvCiv-SAS/Images/report_example.txt"]))

    def test_images_cannot_use_textual_example_marker_even_in_examples_folder(self):
        for path in ("_1_AdvCiv-SAS/Images/diagnostics/capture_example.PNG", "_1_AdvCiv-SAS/Docs/examples/capture_example.png"):
            with self.subTest(path=path):
                self.assertTrue(any("rename the image" in error for error in checker.placement_errors([path])))

    def test_similar_folder_names_do_not_bypass_rule(self):
        self.assertTrue(checker.placement_errors(["_1_AdvCiv-SAS/Docs/examples_other/report_example.log"]))

    def test_imports_generated_outputs_and_test_modules_are_not_captures(self):
        self.assertEqual(checker.placement_errors([
            "_0_Common_Docs/import_example.txt", "LLM_Helpers/context/import_example.py",
            "LLM_Helpers/outputs/run_example.json", ".github/workflows/tests/repository/test_examples_archive_size.py",
            ".github/workflows/tests/documentation/test_example_file_locations.py",
        ]), [])

    def test_git_range_checks_changed_files_and_accepts_relocation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.DEVNULL)
            git("init", "-q")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            git("config", "commit.gpgsign", "false")
            old = root / "capture_example.txt"
            old.write_text("old capture\n", encoding="utf-8")
            git("add", ".")
            git("commit", "-qm", "baseline")
            self.assertEqual(checker.check(root, "HEAD"), [])
            self.assertTrue(checker.check(root, full=True))
            old.write_text("modified capture\n", encoding="utf-8")
            self.assertTrue(checker.check(root, "HEAD"))
            destination = root / checker.EXAMPLES / old.name
            destination.parent.mkdir(parents=True)
            old.rename(destination)
            git("add", "-A")
            self.assertEqual(checker.check(root, "HEAD"), [])


if __name__ == "__main__":
    unittest.main()

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Capture console streams in temporary directories and exercise failure/dry-run paths without rebuilding thousands of historical patches or a full ZIP. (GPT-6.1-Sol) -->
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "LLM_Helpers"))
# <!-- custom: Test the production report wrapper and CLI dispatch directly, preserving the existing archive implementation behind the wrapper. (GPT-6.1-Sol) -->
import make_light_source_zip as light


class PackagingReportTests(unittest.TestCase):
    def test_progress_errors_unicode_and_completion_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            console = io.StringIO()
            errors = io.StringIO()
            def action():
                # <!-- custom: The accented fixture checks UTF-8 receipt encoding; it is not a real packaging status message. (GPT-6.1-Sol) -->
                print("History preparation: café")
                print("warning fixture", file=sys.stderr)
                print("Duration: 42 ms total")
                return 0
            with patch.object(sys, "stdout", console), patch.object(sys, "stderr", errors):
                self.assertEqual(light.run_with_packaging_report(root, action), 0)
            reports = list(root.glob("LLM_Helpers/outputs/light_source/packaging_*.txt"))
            self.assertEqual(len(reports), 1)
            text = reports[0].read_text(encoding="utf-8")
            for expected in ("History preparation: café", "warning fixture", "Duration: 42", "Packaging exit status: 0"):
                self.assertIn(expected, text)
            self.assertIn("History preparation: café", console.getvalue())
            self.assertIn("warning fixture", errors.getvalue())

    def test_failure_receipt_survives_and_original_error_propagates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def action():
                print("partial progress")
                raise RuntimeError("fixture failure")
            with patch.object(sys, "stdout", io.StringIO()), self.assertRaisesRegex(RuntimeError, "fixture failure"):
                light.run_with_packaging_report(root, action)
            text = next(root.glob("LLM_Helpers/outputs/light_source/*.txt")).read_text(encoding="utf-8")
            self.assertIn("partial progress", text)
            self.assertIn("RuntimeError: fixture failure", text)
            self.assertIn("Packaging exit status: EXCEPTION", text)
            self.assertNotIn("Packaging exit status: 0", text)

    def test_unavailable_report_does_not_prevent_packaging(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "LLM_Helpers").write_text("blocked directory", encoding="utf-8")
            errors = io.StringIO()
            with patch.object(sys, "stderr", errors):
                self.assertEqual(light.run_with_packaging_report(root, lambda: 7), 7)
            self.assertIn("report unavailable", errors.getvalue())

    def test_dry_run_skips_report_creation(self):
        args = SimpleNamespace(dry_run=True)
        with patch.object(light, "parse_args", return_value=args), patch.object(light, "build_archive", return_value=0) as build, patch.object(light, "run_with_packaging_report") as record:
            self.assertEqual(light.main(), 0)
            build.assert_called_once_with(args)
            record.assert_not_called()

    # <!-- custom: A ZIP cannot contain its own final receipt; verify prior successful/failed attempts are eligible but an open current run is excluded, with only one report carried forward. (GPT-6.1-Sol) -->
    def test_archive_selects_latest_finalized_report_and_labels_origin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "LLM_Helpers/outputs/light_source"
            folder.mkdir(parents=True)
            self.assertEqual(light.previous_packaging_report_context(root), {})
            (folder / "packaging_20261027T100000Z.txt").write_text("older success\nPackaging exit status: 0\n", encoding="utf-8")
            failed = folder / "packaging_20261027T110000Z.txt"
            failed.write_text("Packaging exit status: EXCEPTION\nRuntimeError: failed\n", encoding="utf-8")
            (folder / "packaging_20261027T120000Z.txt").write_text("current unfinished progress\n", encoding="utf-8")
            context = light.previous_packaging_report_context(root)
            self.assertEqual(list(context), ["_SNAPSHOT_CONTEXT/previous_packaging_report.txt"])
            text = next(iter(context.values())).decode("utf-8")
            self.assertIn(failed.name, text)
            self.assertIn("not the current archive", text)
            self.assertNotIn("current unfinished progress", text)
            self.assertNotIn("older success", text)


if __name__ == "__main__":
    unittest.main()

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Exercise explicit filename/path matching and actual changed-file Git ranges, including docs-only removal and renamed sources, so incremental checking preserves the initial full-audit invariant. (GPT-6.1-Sol) -->
# <!-- custom: pathlib/sys locate the production helper; subprocess and tempfile create isolated Git histories, while unittest checks matching and changed-range behavior. (GPT-6.1-Sol) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

# <!-- custom: Import the production documentation checker directly; fixtures use small standalone repositories without emulating gameplay or relying on this checkout's history. (GPT-6.1-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/documentation"))
import sas_source_guide as guide

SOURCE = "CvGameCoreDLL/SASGameRecordLog.cpp"
LINK = "[`SASGameRecordLog.cpp`](/CvGameCoreDLL/SASGameRecordLog.cpp)"


class SourceGuideTests(unittest.TestCase):
    def test_gameplay_scope_and_branding(self):
        for path in (SOURCE, "Assets/Python/SASExample.py", "Assets/XML/GlobalDefines_advciv_sas.xml", "Assets/XML/Text/AdvCiv-SAS_Core.xml", "PrivateMaps/SAS_Longworld.py", "Assets/SASObserver.ps1", "Assets/SASDialog.cs"):
            self.assertTrue(guide.gameplay_source(path), path)
        for path in ("CvGameCoreDLL/StartPointsAsHandicap.cpp", "CvGameCoreDLL/Project/SASBuild.py", "tests/SASExample.cpp", "LLM_Helpers/SASExample.py", "Assets/Art/SASExample.dds", "LLM_Helpers/SASBuild.ps1", "Assets/Art/SASImage.png", "_0_Common_Docs/SASExample.py", "Assets/Python/Examples.py"):
            self.assertFalse(guide.gameplay_source(path), path)

    def test_filename_and_exact_root_destination(self):
        self.assertEqual(guide.missing_links([SOURCE], LINK), [])
        self.assertEqual(guide.missing_links([SOURCE], "[SASGameRecordLog.cpp](/CvGameCoreDLL/SASGameRecordLog.cpp#helper)"), [])
        for text in ("SASGameRecordLog.cpp", "[implementation](/CvGameCoreDLL/SASGameRecordLog.cpp)", "[SASGameRecordLog.cpp](/elsewhere/SASGameRecordLog.cpp)", "[SASGameRecordLog.cpp](/CvGameCoreDLL/SASGameRecordLog.h)"):
            self.assertEqual(len(guide.missing_links([SOURCE], text)), 1, text)
        self.assertEqual(guide.missing_links([SOURCE], "[SASGameRecordLog.cpp][native]\n\n[native]: /CvGameCoreDLL/SASGameRecordLog.cpp"), [])
        self.assertEqual(guide.missing_links(["Assets/Python/SAS Helper.py"], "[`SAS Helper.py`](</Assets/Python/SAS%20Helper.py>)"), [])

    def test_hidden_and_example_links_do_not_count(self):
        for text in ("<!-- " + LINK + " -->", "```md\n" + LINK + "\n```", "![SASGameRecordLog.cpp](/CvGameCoreDLL/SASGameRecordLog.cpp)", "``" + LINK + "``"):
            self.assertEqual(len(guide.missing_links([SOURCE], text)), 1, text)

    def test_all_missing_paths_reported_together(self):
        paths = [SOURCE, "Assets/Python/SASExample.py"]
        errors = guide.missing_links(paths, "")
        self.assertEqual(len(errors), 2)
        self.assertTrue(all(any(path in error for error in errors) for path in paths))


class GitScopeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sas-guide-test-")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.write(SOURCE, "// existing source\n")
        for document in guide.DOCUMENTS:
            self.write(document, "# Guide\n\n" + LINK + "\n")
        self.git("add", ".")
        self.git("commit", "-qm", "baseline")

    def git(self, *args):
        subprocess.run(["git", "-c", "core.autocrlf=false", *args], cwd=self.repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def write(self, path, text):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def test_changed_source_and_new_source(self):
        self.write(SOURCE, "// updated source\n")
        self.assertEqual(guide.check(self.repo, "HEAD"), ([], 1))
        self.write("Assets/Python/SASNew.py", "pass\n")
        self.git("add", "Assets/Python/SASNew.py")
        errors, count = guide.check(self.repo, "HEAD")
        self.assertEqual(count, 2)
        self.assertEqual(len(errors), 2)
        self.assertIn("Assets/Python/SASNew.py", errors[0])

    def test_cli_fails_then_passes_after_documenting_new_sources(self):
        paths = ["Assets/Python/SASNew.py", "Assets/XML/SASNew.xml", "Assets/SASObserver.ps1", "Assets/SASDialog.cs"]
        for path in paths:
            self.write(path, "fixture\n")
        self.git("add", ".")
        command = [sys.executable, guide.__file__, "--repo-root", str(self.repo), "--base-ref", "HEAD"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for path in paths:
            self.assertIn(path, result.stdout)
        text = "# Guide\n\n" + LINK + "\n" + "\n".join(f"[{Path(path).name}](/{path})" for path in paths)
        for document in guide.DOCUMENTS:
            self.write(document, text)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_docs_only_link_removal_is_checked(self):
        self.write(guide.GUIDE, "# Guide\n\nNo source link.\n")
        errors, count = guide.check(self.repo, "HEAD")
        self.assertEqual(count, 1)
        self.assertIn(SOURCE, errors[0])

    def test_root_readme_removal_is_checked_independently(self):
        self.write("README.md", "# README\n\nNo source link.\n")
        errors, count = guide.check(self.repo, "HEAD")
        self.assertEqual(count, 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("in README.md", errors[0])
        self.assertIn(SOURCE, errors[0])

    def test_new_source_requires_both_documents(self):
        path = "Assets/Python/SASNew.py"
        self.write(path, "pass\n")
        self.git("add", path)
        self.write(guide.GUIDE, LINK + "\n[SASNew.py](/" + path + ")\n")
        errors, count = guide.check(self.repo, "HEAD")
        self.assertEqual(count, 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("in README.md", errors[0])

    def test_full_audit_finds_untouched_missing_link(self):
        self.write(guide.GUIDE, "# Guide\n")
        self.git("add", ".")
        self.git("commit", "-qm", "legacy missing link")
        self.assertEqual(guide.check(self.repo, "HEAD"), ([], 0))
        errors, count = guide.check(self.repo, full=True)
        self.assertEqual(count, 1)
        self.assertEqual(len(errors), 1)
        self.write(guide.CHECKER, "# changed policy fixture\n")
        self.git("add", guide.CHECKER)
        self.assertEqual(len(guide.check(self.repo, "HEAD")[0]), 1)
        self.write(SOURCE, "// edited legacy source\n")
        self.assertEqual(len(guide.check(self.repo, "HEAD")[0]), 1)

    def test_renamed_source_requires_new_link(self):
        renamed = "CvGameCoreDLL/SASRenamed.cpp"
        self.git("mv", SOURCE, renamed)
        errors, count = guide.check(self.repo, "HEAD")
        self.assertEqual(count, 1)
        self.assertIn(renamed, errors[0])

    def test_deleted_source_no_longer_required(self):
        self.git("rm", SOURCE)
        self.assertEqual(guide.check(self.repo, "HEAD"), ([], 0))
        self.assertEqual(guide.check(self.repo, full=True), ([], 0))


if __name__ == "__main__":
    unittest.main()

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib, sys, tempfile and unittest build small fixture repositories for the checker. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/documentation"))
# <!-- custom: folder_indexes is the checker module under test, imported as checker. (Claude code Opus 5.5) -->
import folder_indexes as checker

HELPERS_README = """# Helpers

## Folders

| Folder | Holds |
| --- | --- |
| `audits/` | reports |
| `balance/` | tuning |

### Why folders are named by job

| Before | After |
| --- | --- |
| `xml/` | `audits/` |

## `audits/`

### `ci_report.py`

## `balance/`

### `speed.py`
"""

WORKFLOWS_README = """# Workflows

| Helper/test area | Workflow |
| --- | --- |
| `build/assets/` | `checks-assets.yml` |
| `build/xml/` | `checks-xml.yml` |

## Helper reference

### Assets

#### `build/assets/fonts.py`

#### `build/assets/tech_audio.py`

### XML and rules

#### `build/xml/launch_guard.py`

## Run Locally
"""


class HelperDocOrderTests(unittest.TestCase):
    def repository(self, folder, helpers=HELPERS_README, workflows=WORKFLOWS_README):
        root = Path(folder)
        for path, content in (("LLM_Helpers/README.md", helpers), ("LLM_Helpers/audits/ci_report.py", ""), ("LLM_Helpers/balance/speed.py", ""), (".github/workflows/README.md", workflows)):
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(content, encoding="utf-8")
        (root / "LLM_Helpers/outputs").mkdir()
        return root

    def errors(self, root):
        return checker.check_helpers(root) + checker.check_workflows(root)

    def test_matching_layout_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(self.errors(self.repository(folder)), [])

    def test_loose_helper_and_undescribed_file_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.repository(folder)
            (root / "LLM_Helpers/loose.py").write_text("", encoding="utf-8")
            (root / "LLM_Helpers/balance/new_tuning.py").write_text("", encoding="utf-8")
            errors = self.errors(root)
            self.assertTrue(any("loose.py" in error for error in errors))
            self.assertTrue(any("new_tuning.py" in error for error in errors))

    def test_unsorted_sections_and_missing_folder_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            helpers = HELPERS_README.replace("## `audits/`\n\n### `ci_report.py`\n\n## `balance/`\n\n### `speed.py`\n", "## `balance/`\n\n### `speed.py`\n\n## `audits/`\n\n### `ci_report.py`\n")
            root = self.repository(folder, helpers=helpers)
            (root / "LLM_Helpers/diagnostics").mkdir()
            errors = self.errors(root)
            self.assertTrue(any("folder sections are not in alphabetical order" in error for error in errors))
            self.assertTrue(any("diagnostics/ has no" in error for error in errors))

    def test_guide_list_covers_its_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            guides = root / checker.GUIDES
            guides.mkdir(parents=True)
            for name in ("README_Art_Tools.md", "README_DLL_Compilation.md", "README_New.md"):
                (guides / name).write_text("# Guide\n", encoding="utf-8")
            listing = "# Modding\n\n## Guides in this folder\n\n- [DLL](/%s/README_DLL_Compilation.md): build\n- [Art](/%s/README_Art_Tools.md): art\n\n## Next\n" % (checker.GUIDES, checker.GUIDES)
            (guides / "README.md").write_text(listing, encoding="utf-8")
            errors = checker.check_guides(root)
            self.assertTrue(any("not in alphabetical order" in error for error in errors))
            self.assertTrue(any("README_New.md is not listed" in error for error in errors))

    def test_unsorted_workflow_helpers_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            workflows = WORKFLOWS_README.replace("#### `build/assets/fonts.py`\n\n#### `build/assets/tech_audio.py`", "#### `build/assets/tech_audio.py`\n\n#### `build/assets/fonts.py`")
            errors = self.errors(self.repository(folder, workflows=workflows))
            self.assertEqual(len(errors), 1)
            self.assertIn("Assets helpers", errors[0])


if __name__ == "__main__":
    unittest.main()

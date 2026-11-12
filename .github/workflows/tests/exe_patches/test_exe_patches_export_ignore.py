# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Real Git attributes in a temporary repository: pathlib locates the checker, subprocess runs git init, tempfile holds the fixture and unittest runs the tests. (Claude code Opus 5.5) -->
# <!-- custom: importlib loads the checker from build/exe_patches/, its own category since 2026-11-12, as checker; no sys.path entry or late import is needed. (Claude code Opus 5.5) -->
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

_SPEC = importlib.util.spec_from_file_location("exe_patches_export_ignore", Path(__file__).resolve().parents[2] / "build" / "exe_patches" / "exe_patches_export_ignore.py")
assert _SPEC is not None and _SPEC.loader is not None
checker = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(checker)

ATTRIBUTES = "/.github/ export-ignore\n/AGENTS.md export-ignore\n/LLM_Helpers/exe_analysis/ export-ignore\n/_1_AdvCiv-SAS/Docs/Modding_Resources/README_EXE_Patches.md export-ignore\n"


class ExePatchesExportIgnoreTests(unittest.TestCase):
	def repository(self, folder, attributes):
		root = Path(folder)
		subprocess.run(["git", "init", "-q", str(root)], check=True)
		for path in (".github/workflows/README.md", "AGENTS.md", "LLM_Helpers/exe_analysis/dump.py", "_1_AdvCiv-SAS/Docs/Modding_Resources/README_EXE_Patches.md"):
			(root / path).parent.mkdir(parents=True, exist_ok=True)
			(root / path).write_text("", encoding="utf-8")
		(root / ".gitattributes").write_text(attributes, encoding="utf-8")
		return root

	def test_all_excluded_passes(self):
		with tempfile.TemporaryDirectory() as folder:
			self.assertEqual(checker.check(self.repository(folder, ATTRIBUTES)), [])

	def test_removed_line_fails(self):
		with tempfile.TemporaryDirectory() as folder:
			errors = checker.check(self.repository(folder, ATTRIBUTES.replace("/LLM_Helpers/exe_analysis/ export-ignore\n", "")))
			self.assertEqual(len(errors), 1)
			self.assertIn("LLM_Helpers/exe_analysis/", errors[0])

	def test_moved_guide_fails_loudly(self):
		with tempfile.TemporaryDirectory() as folder:
			root = self.repository(folder, ATTRIBUTES)
			(root / "AGENTS.md").unlink()
			self.assertTrue(any("AGENTS.md: missing" in error for error in checker.check(root)))

	def test_repository_passes(self):
		self.assertEqual(checker.check(checker.ROOT), [])


if __name__ == "__main__":
	unittest.main()

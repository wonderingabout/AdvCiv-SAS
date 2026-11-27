# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: importlib loads the check from its file, as in test_advisor_tab_registry.py.
# tempfile holds the sample modules. (Claude code Opus 5.5) -->
import importlib.util
from pathlib import Path
# <!-- custom: subprocess builds a small Git tree for the new-files test; unittest.mock patches the check's REPO onto it. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
_SPEC = importlib.util.spec_from_file_location("inherited_files", ROOT / ".github/workflows/build/source/inherited_files.py")
assert _SPEC is not None and _SPEC.loader is not None
inherited_files = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(inherited_files)

_REPORT_SPEC = importlib.util.spec_from_file_location("inherited_report", ROOT / "LLM_Helpers/code_history/inherited_files.py")
assert _REPORT_SPEC is not None and _REPORT_SPEC.loader is not None
inherited_report = importlib.util.module_from_spec(_REPORT_SPEC)
_REPORT_SPEC.loader.exec_module(inherited_report)


class InheritedFilesTests(unittest.TestCase):
	def test_imports_name_the_module_not_what_it_imports(self):
		# <!-- custom: The draft helper matched any word, so "from CvScreenEnums import SevoScreenEnums" counted as importing the removed SevoScreenEnums.py. (Claude code Opus 5.5) -->
		with tempfile.TemporaryDirectory() as folder:
			path = Path(folder) / "CvFoo.py"
			path.write_text("from CvScreenEnums import SevoScreenEnums\nimport PyHelpers, ScreenInput\nimport CvUtil as Util\n# import CvWBPopups\n\timport TechTree\n", encoding="latin-1")
			found = inherited_files.imported_modules([path])
		self.assertEqual(sorted(found), ["cvscreenenums", "cvutil", "pyhelpers", "screeninput", "techtree"])

	def test_python24_imports_with_aliases_and_conditional_suites(self):
		text = "\"\"\"\nimport NotAModule\n\"\"\"\n"
		text += "if ready: import first as alias, second.child as third, fourth; from pkg.sub import Member\n"
		text += "try:\n  import fifth, " + chr(92) + "\n    sixth as alias\nexcept ImportError: from fallback import (item, other)\n"
		self.assertEqual(list(inherited_files.module_imports(text)), ["first", "second", "fourth", "pkg", "fifth", "sixth", "fallback"])

	def test_res_hash_distinguishes_binary_newlines(self):
		with tempfile.TemporaryDirectory() as folder:
			first = Path(folder) / "cursor.ani"
			second = Path(folder) / "other.ani"
			first.write_bytes(b"RIFF\r\n")
			second.write_bytes(b"RIFF\n")
			self.assertNotEqual(inherited_files.asset_hash("res", first), inherited_files.asset_hash("res", second))
			self.assertEqual(inherited_files.asset_hash("config", first), inherited_files.asset_hash("config", second))

	def test_new_files_follow_git_paths_and_skip_ignored_outputs(self):
		with tempfile.TemporaryDirectory() as folder:
			root = Path(folder)
			subprocess.run(["git", "init", "--quiet", folder], check=True)
			(root / ".gitignore").write_text("*.generated.h\n", encoding="utf-8")
			for name in ("Assets/Res/new.ani", "Assets/Python/Screens/Adv.py", "Assets/Python/Screens/New.py", "CvGameCoreDLL/temp.generated.h"):
				path = root / name
				path.parent.mkdir(parents=True, exist_ok=True)
				path.touch()
			rows = [{"area": "python", "file": "adv.py"}]
			with patch.object(inherited_files, "REPO", root):
				try:
					self.assertEqual(inherited_files.new_sas_files("res", "Assets/res", None, rows), [root / "Assets/Res/new.ani"])
					self.assertEqual(inherited_files.new_sas_files("python", "Assets/Python", (".py",), rows), [root / "Assets/Python/Screens/New.py"])
					self.assertEqual(inherited_files.new_sas_files("cpp", "CvGameCoreDLL", (".h",), rows), [])
				finally:
					inherited_files.repo_area_paths.cache_clear()

	def test_rename_history_tracks_each_path_lifetime(self):
		a, b, c = ("Assets/Python/" + name for name in ("A.py", "B.py", "C.py"))
		operations = [("A", a), ("R100", a, b), ("A", a), ("D", b), ("A", b), ("R100", b, c), ("A", b)]
		log = "".join("\x1e2026-01-%02d sha%d\0\n%s\0" % (day, day, "\0".join(operation)) for day, operation in enumerate(operations, 1))
		events = inherited_files.parse_upstream_events(log)
		self.assertEqual(inherited_files.file_history(events, c), "2026-01-05 sha5 added; 2026-01-06 sha6 renamed from %s to %s" % (b, c))
		story = inherited_files.file_history(events, b)
		self.assertIn("2026-01-01 sha1 added", story)
		self.assertIn("2026-01-04 sha4 deleted; 2026-01-05 sha5 added", story)
		self.assertNotIn("sha3", story)

	def test_rename_back_and_case_only_moves_appear_once(self):
		a, b, lower = "Assets/Python/A.py", "Assets/Python/B.py", "Assets/Python/a.py"
		operations = [("A", a), ("R100", a, b), ("R100", b, a), ("R100", a, lower)]
		log = "".join("\x1e2026-01-%02d sha%d\0\n%s\0" % (day, day, "\0".join(operation)) for day, operation in enumerate(operations, 1))
		story = inherited_files.file_history(inherited_files.parse_upstream_events(log), lower)
		self.assertEqual([event.split()[1] for event in story.split("; ")], ["sha1", "sha2", "sha3", "sha4"])

	def test_upstream_paths_and_carry_fingerprint_share_keys(self):
		paths = ["assets/PYTHON/EntryPoints/Example.PY", "Assets/PythonExtras/Fake.py", "ASSETS/RES/Fonts/GameFont.tga"]
		self.assertEqual(inherited_files.upstream_files(paths, "python", "Assets/Python", (".py",)), {"example.py": paths[0]})
		self.assertEqual(inherited_files.upstream_files(paths, "res", "Assets/res", None), {"fonts/gamefont.tga": paths[2]})
		rows = [{"area": "python", "file": "example.py", "path": paths[0]}]
		root = inherited_files.REPO
		original = root / "Assets/Python/Screens/Example.py"
		moved = root / "Assets/Python/Contrib/Example.py"
		with patch.object(inherited_files, "repo_area_paths", side_effect=lambda folder, _: [original] if folder == "Assets/Python" else []):
			first = inherited_files.carried_inherited(rows)
		with patch.object(inherited_files, "repo_area_paths", side_effect=lambda folder, _: [moved, original.with_name("Own.py")] if folder == "Assets/Python" else []):
			second = inherited_files.carried_inherited(rows)
		self.assertEqual(second, [paths[0] + "\tAssets/Python/Contrib/Example.py"])
		self.assertNotEqual(first, second)


	def test_dropped_again_requires_a_sas_arrival_and_departure(self):
		original = "Assets/Python/Screens/CvExample.py"
		renamed = "Assets/Python/Screens/CvOther.py"
		add = (original, "added", None, "a", "2026-01-01", "Add example")
		move = (original, "renamed to", renamed, "b", "2026-01-02", "Rename example")
		self.assertFalse(inherited_report.taken_and_dropped(inherited_report.sas_file_changes([move, add], {"a"})))
		events = inherited_report.sas_file_changes([move, add], set())
		self.assertTrue(inherited_report.taken_and_dropped(events))
		self.assertIn(renamed, inherited_report.sas_side_events(events))
		same_name = (original, "renamed to", "Assets/Python/Contrib/CvExample.py", "b", "2026-01-02", "Move example")
		self.assertFalse(inherited_report.taken_and_dropped(inherited_report.sas_file_changes([same_name, add], set(), by_module=True)))

	def test_first_clause_skips_abbreviations_and_keeps_short_clauses(self):
		self.assertEqual(inherited_report.first_clause("Fix AI. Follow up later"), "Fix AI")
		self.assertEqual(inherited_report.first_clause("Adjust e.g. yield thresholds — refresh screenshots"), "Adjust e.g. yield thresholds")
		prefix = "Update a group of eligible city and tile widgets " * 2
		title = prefix + ", including " + "a very long explanation " * 6
		self.assertEqual(inherited_report.first_clause(title), prefix.rstrip() + " (full title in the report)")


	def test_markers_change_with_the_imported_modules_only(self):
		# <!-- custom: The audit's fingerprints: the same imports give the same markers, and starting to import one more inherited module changes only the imports marker. (Claude code Opus 5.5) -->
		rows = inherited_files.read_tsv()
		# <!-- custom: repo_area_paths caches the real repository's paths, which then leaked into the temporary-repository test that runs after this one, so clear it. (Claude code Opus 5.5) -->
		try:
			first = inherited_files.audit_markers(rows, {"cvwbpopups"})
			self.assertEqual(first, inherited_files.audit_markers(rows, {"cvwbpopups"}))
			second = inherited_files.audit_markers(rows, {"cvwbpopups", "pyhelpers"})
			self.assertEqual(first[:2], second[:2])
			self.assertNotEqual(first[2], second[2])
		finally:
			inherited_files.repo_area_paths.cache_clear()


if __name__ == "__main__":
	unittest.main()

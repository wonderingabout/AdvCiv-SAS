# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: importlib loads the check from its file, so no sys.path entry and late import, which needed a noqa, is required. (Claude code Opus 5.5) -->
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
_SPEC = importlib.util.spec_from_file_location("map_previews", ROOT / ".github/workflows/build/assets/map_previews.py")
assert _SPEC is not None and _SPEC.loader is not None
map_previews = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(map_previews)


def make_repo(base: Path, scripts: dict, entries: list, files: list) -> Path:
	(base / "PrivateMaps").mkdir()
	for name, value in scripts.items():
		body = "def isAdvancedMap():\n\treturn %d\n" % value if value is not None else "def getDescription():\n\treturn ''\n"
		(base / "PrivateMaps" / (name + ".py")).write_text(body, encoding="latin-1")
	xml = "".join("<WorldPickerInfo><MapName>%s</MapName><WaterLevelDecalPath>Art/AdvCiv_SAS/Maps/%s/FLAT_%s.dds</WaterLevelDecalPath></WorldPickerInfo>" % (n, n, n) for n in entries)
	(base / "Assets" / "XML" / "Interface").mkdir(parents=True)
	(base / "Assets" / "XML" / "Interface" / "CIV4WorldPickerInfos.xml").write_text("<x>%s</x>" % xml, encoding="utf-8")
	for name in files:
		path = base / "Assets" / "Art" / "AdvCiv_SAS" / "Maps" / name / ("FLAT_%s.dds" % name)
		path.parent.mkdir(parents=True)
		path.write_bytes(b"DDS ")
	return base


class MapPreviewTests(unittest.TestCase):
	def test_shown_script_without_entry_fails(self):
		with tempfile.TemporaryDirectory() as tmp:
			root = make_repo(Path(tmp), {"Shown": 0, "Hidden": 1, "NoFunction": None}, [], [])
			failures = map_previews.check(root)
			self.assertEqual(len(failures), 1)
			self.assertIn("Shown is shown in Simple Game", failures[0])

	def test_false_and_one_line_returns_count_as_shown(self):
		# <!-- custom: PerfectMongoose returns False, which the first version missed. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		with tempfile.TemporaryDirectory() as tmp:
			maps = Path(tmp)
			(maps / "Mongoose.py").write_text("def isAdvancedMap():\n\t# return 1 hides it\n\treturn False\n\ndef other():\n\treturn 0\n", encoding="latin-1")
			(maps / "OneLine.py").write_text("def isAdvancedMap(): return 0\n", encoding="latin-1")
			(maps / "Advanced.py").write_text("def isAdvancedMap():\n\treturn True\n\ndef other():\n\treturn 0\n", encoding="latin-1")
			self.assertEqual(map_previews.shown_scripts(maps), ["Mongoose", "OneLine"])

	def test_entry_with_missing_file_fails(self):
		with tempfile.TemporaryDirectory() as tmp:
			root = make_repo(Path(tmp), {"Shown": 0}, ["Shown"], [])
			self.assertTrue(any("does not exist" in f for f in map_previews.check(root)))

	def test_complete_preview_and_exception_pass(self):
		with tempfile.TemporaryDirectory() as tmp:
			root = make_repo(Path(tmp), {"Shown": 0, "RandomScriptMap": 0}, ["Shown"], ["Shown"])
			self.assertEqual(map_previews.check(root), [])

	def test_stale_exception_fails(self):
		with tempfile.TemporaryDirectory() as tmp:
			root = make_repo(Path(tmp), {"RandomScriptMap": 0}, ["RandomScriptMap"], ["RandomScriptMap"])
			self.assertTrue(any("DEFAULT_GLOBE_ON_PURPOSE" in f for f in map_previews.check(root)))


if __name__ == "__main__":
	unittest.main()

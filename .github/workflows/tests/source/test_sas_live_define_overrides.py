# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib, shutil and tempfile build a small fake repository around the real bridge; sys and unittest import and run the check. See KI#128.5. (Claude code Opus 5.5) -->
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import sas_live_define_overrides as checker

REPO_ROOT = Path(__file__).resolve().parents[4]
XML = "<Define>\n\t\t<DefineName>SAS_A</DefineName>\n\t\t<iDefineIntVal>1</iDefineIntVal>\n\t</Define>\n<Define><DefineName>SAS_LIVE_DEFINE_OVERRIDES_ON</DefineName><iDefineIntVal>1</iDefineIntVal></Define>\n<Define><DefineName>SAS_T</DefineName><DefineTextVal>x &amp; y</DefineTextVal></Define>\n<Define><DefineName>SAS_F</DefineName><fDefineFloatVal>1.5</fDefineFloatVal></Define>\n<!-- <Define><DefineName>SAS_C</DefineName><iDefineIntVal>1</iDefineIntVal></Define> -->\n"


class SASLiveDefineOverridesTests(unittest.TestCase):
	def setUp(self):
		self.root = Path(tempfile.mkdtemp())
		self.addCleanup(shutil.rmtree, self.root)
		for folder in ("Assets/Python", "Assets/XML", "PrivateMaps", "CvGameCoreDLL", "SASLiveDefineOverrides", "LLM_Helpers/diagnostics"):
			(self.root / folder).mkdir(parents=True)
		shutil.copy(REPO_ROOT / "LLM_Helpers" / "diagnostics" / "define_values.py", self.root / "LLM_Helpers" / "diagnostics")
		shutil.copy(REPO_ROOT / "Assets" / "Python" / "SASLiveDefineOverridesBridge.py", self.root / "Assets" / "Python")
		shutil.copy(REPO_ROOT / "SASLiveDefineOverrides" / "SASLiveDefineOverridesNoEntry.txt", self.root / "SASLiveDefineOverrides")
		self.write("Assets/XML/GlobalDefines_advciv_sas.xml", XML)
		self.write("Assets/Python/Reader.py", "def f():\n\treturn gc.getDefineINT(\"SAS_A\")\n")

	def write(self, relative, text):
		(self.root / relative).write_text(text, encoding="utf-8")

	def run_check(self, overrides):
		self.write("SASLiveDefineOverrides/SASLiveDefineOverrides.txt", overrides)
		return checker.main(["--repo-root", str(self.root)])

	def problems(self, values):
		return checker.problems(self.root, values, checker.xml_values(self.root))

	def test_bridge_rejects_a_no_entry_define(self):
		# <!-- custom: The bridge enforces NoEntry in game too since 2026-11-26, as Codex's review (GPT-6.2-Sol) advised; the shipped list's own lines parse with it. See KI#128.5. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		import sas_live_define_overrides_file as lib
		bridge = lib.load_bridge(REPO_ROOT)
		no_entry = bridge._parseNoEntry("# comment\n\nSAS_A: a reason\nSAS_B: same reason as SAS_A\n")
		self.assertEqual(no_entry, {"SAS_A": "a reason", "SAS_B": "a reason"})
		with self.assertRaises(ValueError) as caught:
			bridge._parse("SAS_A = 1\n", bridge._parseXml(XML), no_entry)
		self.assertIn("a reason", str(caught.exception))
		shipped = bridge._parseNoEntry((REPO_ROOT / "SASLiveDefineOverrides" / "SASLiveDefineOverridesNoEntry.txt").read_text(encoding="utf-8"))
		self.assertIn("SAS_SGR_LOG_ON", shipped)

	def test_define_the_dev_toggle_switches_fails(self):
		# <!-- custom: A shipped line would win over the XML value toggle_dev_diagnostics.py sets. See KI#128.5. (Claude code Opus 5.5) -->
		self.write("Assets/XML/GlobalDefines_advciv_sas.xml", XML + "<Define><DefineName>SAS_SGR_LOG</DefineName><iDefineIntVal>1</iDefineIntVal></Define>\n")
		self.assertTrue(any("toggle_dev_diagnostics" in problem for problem in self.problems({"SAS_SGR_LOG": 1})))

	def test_failed_dll_refill_rolls_back_and_retries(self):
		# <!-- custom: The DLL refill runs inside the push, so a failure there rolls the defines back and the next reread applies the file again; a first draft called it after the change was counted, so a failing call left it never retried, as Codex's review (GPT-6.2-Sol) found. See KI#128.5. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		import sas_live_define_overrides_file as lib
		bridge = lib.load_bridge(REPO_ROOT)
		records = []
		bridge.SASPythonLogging.writeRecord = lambda record, fields="": records.append(fields)

		class FakeGlobals:
			def __init__(self):
				self.defines = {"SAS_LIVE_DEFINE_OVERRIDES_ON": 1, "SAS_A": 1}
				self.failures = 1
				self.refills = []

			def getDefineINT(self, name):
				return self.defines[name]

			def setDefineINT(self, name, value):
				self.defines[name] = value

			def onSASLiveDefineOverridesApplied(self):
				self.refills.append(self.defines["SAS_A"])
				if self.failures > 0:
					self.failures -= 1
					raise RuntimeError("refill failed")

		fake = FakeGlobals()
		bridge.CyGlobalContext = lambda: fake
		files = {"SASLiveDefineOverrides.txt": "SAS_A = 2\n", "GlobalDefines_advciv_sas.xml": XML, "SASLiveDefineOverridesNoEntry.txt": ""}
		bridge._readBytes = lambda parts: files[parts[-1]]
		self.assertEqual(bridge.refresh(), 0)
		self.assertEqual(fake.defines["SAS_A"], 1)
		self.assertTrue(any("PUSH_FAILED" in fields for fields in records))
		self.assertEqual(bridge.refresh(), 1)
		self.assertEqual(fake.defines["SAS_A"], 2)
		self.assertEqual(fake.refills, [2, 1, 2])

	# <!-- custom: A save caught midway, such as an emptied file, parses as valid; Codex's review (GPT-6.2-Sol) showed it would apply as deleted lines, so settled polls apply a text only once read twice. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	def test_settled_refresh_skips_a_save_caught_midway(self):
		sys.path.insert(0, str(REPO_ROOT / ".github" / "workflows" / "lib"))
		import sas_live_define_overrides_file as lib
		bridge = lib.load_bridge(REPO_ROOT)
		bridge.SASPythonLogging.writeRecord = lambda record, fields="": None

		class FakeGlobals:
			def __init__(self):
				self.defines = {"SAS_LIVE_DEFINE_OVERRIDES_ON": 1, "SAS_A": 1}
				self.sets = []

			def getDefineINT(self, name):
				return self.defines[name]

			def setDefineINT(self, name, value):
				self.defines[name] = value
				self.sets.append(value)

			def onSASLiveDefineOverridesApplied(self):
				pass

		fake = FakeGlobals()
		bridge.CyGlobalContext = lambda: fake
		files = {"SASLiveDefineOverrides.txt": "SAS_A = 2\n", "GlobalDefines_advciv_sas.xml": XML, "SASLiveDefineOverridesNoEntry.txt": ""}
		bridge._readBytes = lambda parts: files[parts[-1]]
		self.assertEqual(bridge.refresh(), 1)
		files["SASLiveDefineOverrides.txt"] = ""
		self.assertEqual(bridge.refresh(True), 1)
		files["SASLiveDefineOverrides.txt"] = "SAS_A = 2\n"
		self.assertEqual(bridge.refresh(True), 1)
		self.assertEqual(fake.sets, [2])
		files["SASLiveDefineOverrides.txt"] = "SAS_A = 3\n"
		self.assertEqual(bridge.refresh(True), 1)
		self.assertEqual(bridge.refresh(True), 2)
		self.assertEqual(fake.sets, [2, 3])
		# <!-- custom: Codex's next review (GPT-6.2-Sol) applied an empty file read around a failed read; a failed read now forgets the pending text. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		files["SASLiveDefineOverrides.txt"] = ""
		self.assertEqual(bridge.refresh(True), 2)
		read = bridge._readBytes
		def failing(parts):
			raise IOError("busy")
		bridge._readBytes = failing
		self.assertEqual(bridge.refresh(True), 2)
		bridge._readBytes = read
		self.assertEqual(bridge.refresh(True), 2)
		self.assertEqual(bridge.refresh(True), 3)

	def test_override_equal_to_the_xml_passes(self):
		self.assertEqual(self.run_check("SAS_A = 1\n"), 0)

	def test_empty_file_passes(self):
		self.assertEqual(self.run_check(""), 0)

	def test_override_different_from_the_xml_fails(self):
		# <!-- custom: A shipped override equals its XML value, so the game plays the same with the overrides on or off; a different value stays a local, unstaged experiment. (Claude code Opus 5.5) -->
		self.assertIn("in the shipped overrides but 1", self.problems({"SAS_A": 2})[0])

	def test_unknown_or_commented_define_is_rejected(self):
		# <!-- custom: setDefineINT would create a new entry for any name, so a typo must not reach it; nor a define that exists only inside an XML comment, which Codex's review (GPT-6.2-Sol) reproduced being read as real. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		for line in ("SAS_B = 1\n", "SAS_C = 1\n"):
			self.assertEqual(self.run_check(line), 1)

	def test_value_must_fit_the_define_type(self):
		# <!-- custom: Each line is read by its define's XML type since floats and strings joined on 2026-11-26: an integer, a float, or a double-quoted string. (Claude code Opus 5.5) -->
		for line in ("SAS_A = 1.5\n", "SAS_A = abc\n", "SAS_A = \"x\"\n", "SAS_F = abc\n", "SAS_T = x\n", "SAS_T = 1\n"):
			self.assertEqual(self.run_check(line), 1)

	def test_float_and_string_overrides_equal_to_the_xml_pass(self):
		self.assertEqual(self.run_check("SAS_F = 1.5\nSAS_T = \"x & y\"\n"), 0)

	def test_string_escapes(self):
		values = checker.read_values(self.root, "SAS_T = \"say \\\"hi\\\" \\\\ ok\"\n")
		self.assertEqual(values, {"SAS_T": "say \"hi\" \\ ok"})

	def test_float_differing_from_the_xml_fails(self):
		self.assertIn("2.5 in the shipped overrides but 1.5", self.problems({"SAS_F": 2.5})[0])

	def test_name_set_twice_is_rejected(self):
		self.assertEqual(self.run_check("SAS_A = 1\nSAS_A = 1\n"), 1)

	def test_no_entry_define_fails(self):
		self.assertIn("no override may name it", self.problems({"SAS_LIVE_DEFINE_OVERRIDES_ON": 1})[0])

	def test_no_entry_pattern_is_rejected(self):
		# <!-- custom: Each NoEntry line names a define in full since 2026-11-26, so a grep for a define finds its line. (Claude code Opus 5.5) -->
		with self.assertRaises(ValueError):
			checker.read_no_entry(self.root, "SAS_EXE_P_*: an EXE patch setting\n")

	def test_comment_line_fails(self):
		self.assertEqual(checker.comment_lines("SAS_A = 1\n# why\n\n  # indented\n"), [2, 4])

	def test_python_attribute_keeping_the_value_fails(self):
		self.write("Assets/Python/Reader.py", "class S:\n\tdef __init__(self):\n\t\tself.iA = gc.getDefineINT(\"SAS_A\")\n")
		self.assertEqual(self.problems({"SAS_A": 1}), ["Assets/Python/Reader.py:3: SAS_A is kept in a module global or attribute, so its override never reaches this reader; read it at each use"])

	def test_python_module_global_keeping_the_value_fails(self):
		self.write("Assets/Python/Reader.py", "A = gc.getDefineINT(\"SAS_A\")\n")
		self.assertIn("kept in a module global", self.problems({"SAS_A": 1})[0])

	def test_commented_out_python_read_passes(self):
		self.write("Assets/Python/Reader.py", "# A = gc.getDefineINT(\"SAS_A\")\n")
		self.assertEqual(self.problems({"SAS_A": 1}), [])

	def test_dll_static_fails_by_name_or_enum(self):
		for code in ("static int const i = GC.getDefineINT(\"SAS_A\");\n", "static int const i = GC.getDefineINT(CvGlobals::SAS_A);\n"):
			self.write("CvGameCoreDLL/Reader.cpp", code)
			self.assertIn("kept in a static", self.problems({"SAS_A": 1})[0])

	def test_dll_read_at_each_use_passes(self):
		self.write("CvGameCoreDLL/Reader.cpp", "int const i = GC.getDefineINT(CvGlobals::SAS_A);\n// static int const j = GC.getDefineINT(\"SAS_A\");\n")
		self.assertEqual(self.problems({"SAS_A": 1}), [])

	# <!-- custom: Codex's review (GPT-6.2-Sol) found --staged read NoEntry from disk, so a staged forbidden line passed once its NoEntry line was removed unstaged; every file now comes from the index. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	def test_staged_reads_no_entry_from_the_index(self):
		import subprocess
		def git(*args):
			subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=self.root, check=True, capture_output=True)
		git("init", "-q")
		# <!-- custom: Git writes its objects read-only, which Windows refuses to delete, so they are made writable before setUp's cleanup runs, as cleanups run last added first. (Claude code Opus 5.5) -->
		import os
		import stat
		self.addCleanup(lambda: [os.chmod(path, stat.S_IWRITE) for path in (self.root / ".git").rglob("*") if path.is_file()])
		self.write("SASLiveDefineOverrides/SASLiveDefineOverrides.txt", "SAS_LIVE_DEFINE_OVERRIDES_ON = 1\n")
		git("add", "-A")
		self.write("SASLiveDefineOverrides/SASLiveDefineOverridesNoEntry.txt", "# emptied on disk only\n")
		self.assertEqual(checker.main(["--repo-root", str(self.root)]), 0)
		self.assertEqual(checker.main(["--repo-root", str(self.root), "--staged"]), 1)
		# <!-- custom: The development values come from the index too, as Codex's next review (GPT-6.2-Sol) found them imported from disk. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		self.write("Assets/XML/GlobalDefines_advciv_sas.xml", XML + "<Define><DefineName>SAS_SGR_LOG</DefineName><iDefineIntVal>0</iDefineIntVal></Define>\n")
		self.write("SASLiveDefineOverrides/SASLiveDefineOverrides.txt", "SAS_SGR_LOG = 0\n")
		self.write("SASLiveDefineOverrides/SASLiveDefineOverridesNoEntry.txt", "# none\n")
		git("add", "-A")
		self.write("LLM_Helpers/diagnostics/define_values.py", "DEVELOPMENT_VALUES = {}\n")
		self.assertEqual(checker.main(["--repo-root", str(self.root)]), 0)
		self.assertEqual(checker.main(["--repo-root", str(self.root), "--staged"]), 1)

	def test_repository_passes_staged(self):
		# <!-- custom: The staged content, as ci_report.py checks it, since a local override usually stays unstaged; skipped until the files are in the index. (Claude code Opus 5.5) -->
		try:
			result = checker.main(["--staged"])
		except RuntimeError:
			self.skipTest("SASLiveDefineOverrides.txt is not staged")
		self.assertEqual(result, 0)


if __name__ == "__main__":
	unittest.main()

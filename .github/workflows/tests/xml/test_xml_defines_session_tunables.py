# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the shared library; tempfile builds a fixture repository; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared reader the shipped-value checks use, so its rules are tested once rather than through each check. (Claude code Opus 5.5) -->
import xml_defines


# <!-- custom: read_global_define_ints with session_names: a check names the settings it takes from SASSessionTunables.py, a name in both files fails whatever its type, and a revision without the file keeps reading the XML (KI#128.11).
# The first version merged every integer of the file and compared integers only, so a Python string could shadow an XML integer, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
class SessionTunablesReaderTests(unittest.TestCase):
	def setUp(self):
		temporary = tempfile.TemporaryDirectory()
		self.addCleanup(temporary.cleanup)
		self.repo = Path(temporary.name)
		self.write_xml(("SAS_XML_SETTING", "1"))

	def write_xml(self, *entries, text=()):
		body = "".join(f"<Define><DefineName>{name}</DefineName><iDefineIntVal>{value}</iDefineIntVal></Define>" for name, value in entries)
		body += "".join(f"<Define><DefineName>{name}</DefineName><DefineTextVal>{value}</DefineTextVal></Define>" for name, value in text)
		path = self.repo / "Assets/XML/GlobalDefines_advciv_sas.xml"
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(f"<Civ4Defines>{body}</Civ4Defines>", encoding="utf-8")

	def write_tunables(self, text):
		path = self.repo / "Assets/Python/SASSessionTunables.py"
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(text, encoding="utf-8")

	def test_named_setting_is_read_from_the_file(self):
		self.write_tunables("SAS_PY_SETTING = 3\n")
		defines = xml_defines.read_global_define_ints(self.repo, session_names=("SAS_PY_SETTING",))
		self.assertEqual(defines, {"SAS_XML_SETTING": 1, "SAS_PY_SETTING": 3})

	def test_unnamed_setting_is_not_merged(self):
		self.write_tunables("SAS_PY_SETTING = 3\nSAS_OTHER = 4\n")
		defines = xml_defines.read_global_define_ints(self.repo, session_names=("SAS_PY_SETTING",))
		self.assertNotIn("SAS_OTHER", defines)

	def test_name_in_both_files_fails_whatever_its_type(self):
		self.write_tunables("SAS_PY_SETTING = 3\nSAS_XML_SETTING = 'text'\n")
		with self.assertRaises(RuntimeError):
			xml_defines.read_global_define_ints(self.repo, session_names=("SAS_PY_SETTING",))
		self.write_xml(("SAS_XML_SETTING", "1"), text=(("SAS_PY_SETTING", "words"),))
		self.write_tunables("SAS_PY_SETTING = 3\n")
		with self.assertRaises(RuntimeError):
			xml_defines.read_global_define_ints(self.repo, session_names=("SAS_PY_SETTING",))

	def test_named_setting_must_be_an_integer(self):
		self.write_tunables("SAS_PY_SETTING = '3'\n")
		with self.assertRaises(RuntimeError):
			xml_defines.read_global_define_ints(self.repo, session_names=("SAS_PY_SETTING",))
		self.write_tunables("SAS_OTHER = 1\n")
		with self.assertRaises(RuntimeError):
			xml_defines.read_global_define_ints(self.repo, session_names=("SAS_PY_SETTING",))

	def test_revision_without_the_file_reads_the_xml(self):
		self.write_xml(("SAS_XML_SETTING", "1"), ("SAS_PY_SETTING", "5"))
		defines = xml_defines.read_global_define_ints(self.repo, session_names=("SAS_PY_SETTING",))
		self.assertEqual(defines["SAS_PY_SETTING"], 5)


if __name__ == "__main__":
	unittest.main()

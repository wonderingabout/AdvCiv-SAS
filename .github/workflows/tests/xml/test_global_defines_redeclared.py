# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the checker; tempfile builds a fixture repository; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "xml"))

# <!-- custom: The check of the carried BtS GlobalDefines.xml's list of removed, redeclared names (KI#1104.2). (Claude code Opus 5.5) -->
import global_defines_redeclared as checker

LOADER = 'ReadGlobalDefines("xml\\\\GlobalDefines.xml", cache);\nReadGlobalDefines("xml\\\\GlobalDefinesAlt.xml", cache);\nReadGlobalDefines("xml\\\\GlobalDefines_advc.xml", cache);\n'


# <!-- custom: A name declared only inside a comment of the later file must fail, the case Codex's review (GPT-6.2-Sol) found in GlobalDefinesAlt.xml, as must a file the DLL never loads and a header whose stated count does not match its list; a real declaration passes. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
class RedeclaredTests(unittest.TestCase):
	def setUp(self):
		temporary = tempfile.TemporaryDirectory()
		self.addCleanup(temporary.cleanup)
		self.repo = Path(temporary.name)
		(self.repo / "Assets/XML").mkdir(parents=True)
		(self.repo / "CvGameCoreDLL").mkdir()
		(self.repo / "CvGameCoreDLL/CvXMLLoadUtilitySet.cpp").write_text(LOADER, encoding="latin-1")

	def write(self, name, text):
		(self.repo / "Assets/XML" / name).write_text(text, encoding="utf-8")

	def carried(self, entries, declared="", stated=None):
		count = len(entries) if stated is None else stated
		self.write("GlobalDefines.xml", "<?xml version=\"1.0\"?>\n<!-- custom: BtS's declarations of the %d names below were removed:\n" % count + "\n".join(entries) + ". (Claude code Opus 5.5) -->\n<Civ4Defines>" + declared + "</Civ4Defines>\n")

	def advc(self):
		self.write("GlobalDefines_advc.xml", "<Civ4Defines><Define><DefineName>MIN_VERSION</DefineName><iDefineIntVal>2</iDefineIntVal></Define></Civ4Defines>")

	def test_real_redeclaration_passes(self):
		self.carried(["MIN_VERSION = 1 in BtS, redeclared in GlobalDefines_advc.xml"])
		self.advc()
		self.assertEqual(checker.check(self.repo), ([], 1))

	def test_name_only_in_a_comment_fails(self):
		self.carried(["BASE_REVOLT_OCCUPATION_TURNS = 2 in BtS, redeclared in GlobalDefinesAlt.xml"])
		self.write("GlobalDefinesAlt.xml", "<Civ4Defines><!-- <Define><DefineName>BASE_REVOLT_OCCUPATION_TURNS</DefineName><iDefineIntVal>3</iDefineIntVal></Define> --></Civ4Defines>")
		failures, _ = checker.check(self.repo)
		self.assertEqual(len(failures), 1)

	def test_name_still_in_the_copy_fails(self):
		self.carried(["MIN_VERSION = 1 in BtS, redeclared in GlobalDefines_advc.xml"], "<Define><DefineName>MIN_VERSION</DefineName><iDefineIntVal>1</iDefineIntVal></Define>")
		self.advc()
		failures, _ = checker.check(self.repo)
		self.assertEqual(len(failures), 1)

	def test_file_the_dll_never_loads_fails(self):
		self.carried(["MIN_VERSION = 1 in BtS, redeclared in NeverLoaded.xml"])
		self.write("NeverLoaded.xml", "<Civ4Defines><Define><DefineName>MIN_VERSION</DefineName><iDefineIntVal>2</iDefineIntVal></Define></Civ4Defines>")
		failures, _ = checker.check(self.repo)
		self.assertEqual(len(failures), 1)

	def test_stated_count_must_match_the_list(self):
		self.carried(["MIN_VERSION = 1 in BtS, redeclared in GlobalDefines_advc.xml"], stated=2)
		self.advc()
		failures, _ = checker.check(self.repo)
		self.assertEqual(len(failures), 1)
		self.carried([], stated=0)
		failures, _ = checker.check(self.repo)
		self.assertEqual(len(failures), 1)


if __name__ == "__main__":
	unittest.main()

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys make the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_define_reads_import as checker


class PythonDefineReadsImportTests(unittest.TestCase):
	def test_module_constant_fails(self):
		text = 'IS_SHOW_AI_INFO = (gc.getDefineINT("SAS_SEVO_UNIT_SHOW_AI_INFORMATION") > 0)\n'
		self.assertEqual(checker.import_time_reads(text), [(1, "getDefineINT")])

	def test_read_in_function_passes(self):
		text = 'def f():\n\treturn gc.getDefineINT("PEACE_TREATY_LENGTH")\n'
		self.assertEqual(checker.import_time_reads(text), [])

	def test_class_body_fails_and_method_passes(self):
		text = 'class A:\n\tX = gc.getDefineINT("A")\n\tdef f(self):\n\t\tself.Y = gc.getDefineINT("B")\n'
		self.assertEqual(checker.import_time_reads(text), [(2, "getDefineINT")])

	def test_module_if_block_fails(self):
		text = 'if True:\n\tX = gc.getDefineSTRING("A")\n'
		self.assertEqual(checker.import_time_reads(text), [(2, "getDefineSTRING")])

	def test_multiline_signature_with_dedented_comment_passes(self):
		# <!-- custom: CvMapGeneratorUtil's __init__ signatures span lines with AdvCiv's "# </advc.137>" at a lower indent, which misled the line-based audit. (Claude code Opus 5.5) -->
		text = 'class F:\n\tdef __init__(self, a=None,\n\t# </advc.137>\nb=None):\n\t\tif a is None:\n\t\t\ta = gc.getDefineINT("A")\n'
		self.assertEqual(checker.import_time_reads(text), [])

	def test_one_line_def_and_lambda_pass(self):
		text = 'def f(): return gc.getDefineINT("A")\ng = lambda: gc.getDefineINT("B")\n'
		self.assertEqual(checker.import_time_reads(text), [])

	def test_default_arguments_and_lambda_neighbours_fail(self):
		# <!-- custom: Codex's three reproduced misses: these all run at import. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		text = 'def f(x=gc.getDefineINT("X")): pass\ng = lambda x=gc.getDefineINT("X"): x\nh = (lambda: None, gc.getDefineINT("X"))\n'
		self.assertEqual(checker.import_time_reads(text), [(1, "getDefineINT"), (2, "getDefineINT"), (3, "getDefineINT")])

	def test_lambda_in_default_keeps_its_body_lazy(self):
		text = 'def f(x=lambda: gc.getDefineINT("X")):\n\treturn x\n'
		self.assertEqual(checker.import_time_reads(text), [])

	def test_current_defines_at_import_fails(self):
		text = 'X = SASCurrentDefines.getInt("SAS_UI_FONT_LABEL")\ndef f():\n\treturn SASCurrentDefines.getInt("SAS_UI_FONT_LABEL")\n'
		self.assertEqual(checker.import_time_reads(text), [(1, "getInt")])

	def test_name_in_comment_or_string_passes(self):
		text = '# X = gc.getDefineINT("A")\nNAME = "getDefineINT"\n'
		self.assertEqual(checker.import_time_reads(text), [])

	def test_init_of_a_screen_built_at_import_fails(self):
		# <!-- custom: The KI#128.6 gap: CvScreensInterface builds screens at module level, so their __init__, and the methods it calls through self, run at import. (Claude code Opus 5.5) -->
		screen = Path("Screens/CvA.py")
		interface = Path("CvI.py")
		texts = {
			screen: 'class CvA:\n\tdef __init__(self):\n\t\tself.x = 1\n\t\tself.setup()\n\tdef setup(self):\n\t\tself.y = gc.getDefineINT("A")\n\tdef draw(self):\n\t\tz = SASCurrentDefines.getInt("B")\n',
			interface: 'import CvA\nscreen = CvA.CvA()\n',
		}
		self.assertEqual(checker.constructed_at_import_reads(texts), [(screen, 6, "CvA.setup", interface, 2)])

	def test_class_imported_by_name_is_followed(self):
		# <!-- custom: The map scripts' balancer = BonusBalancer() after from CvMapGeneratorUtil import BonusBalancer, which a first scan missed. (Claude code Opus 5.5) -->
		util = Path("CvMapGeneratorUtil.py")
		script = Path("Continents.py")
		texts = {
			util: 'class BonusBalancer:\n\tdef __init__(self):\n\t\tself.x = SASCurrentDefines.getInt("A")\n',
			script: 'from CvMapGeneratorUtil import BonusBalancer\nbalancer = BonusBalancer()\n',
		}
		self.assertEqual(checker.constructed_at_import_reads(texts), [(util, 3, "BonusBalancer.__init__", script, 2)])

	def test_construction_inside_a_function_passes(self):
		texts = {Path("CvB.py"): 'class CvB:\n\tdef __init__(self):\n\t\tself.y = gc.getDefineINT("A")\ndef make():\n\treturn CvB()\n'}
		self.assertEqual(checker.constructed_at_import_reads(texts), [])

	def test_paths_codex_found_missing_are_followed(self):
		# <!-- custom: Each path Codex's review (GPT-6.2-Sol) reproduced a first, line-based scan missing: an inherited base __init__, an explicit Base.__init__(self), an object built inside __init__, a module helper, a construction under a module-level if, and a one-line __init__. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		path = Path("M.py")
		text = (
			'class Base:\n\tdef __init__(self):\n\t\tself.a = gc.getDefineINT("A")\n'
			'class Inherits(Base):\n\tpass\n'
			'class Explicit(Base):\n\tdef __init__(self):\n\t\tBase.__init__(self)\n'
			'class Inner:\n\tdef __init__(self): self.b = gc.getDefineINT("B")\n'
			'class Outer:\n\tdef __init__(self):\n\t\tself.inner = Inner()\n'
			'def helper():\n\treturn SASCurrentDefines.getInt("C")\n'
			'one = Inherits()\n'
			'if True:\n\ttwo = Outer()\n'
			'three = helper()\n'
		)
		self.assertEqual([hit[:3] for hit in checker.constructed_at_import_reads({path: text})], [(path, 3, "Base.__init__"), (path, 10, "Inner.__init__"), (path, 15, "helper")])

	def test_false_leads_codex_found_are_not_followed(self):
		# <!-- custom: A call in a comment, a decorator's lambda after a method, and a name imported from another module than the one holding a same-named class. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		texts = {
			Path("a.py"): 'class Screen:\n\tdef __init__(self):\n\t\tself.x = gc.getDefineINT("A")\nclass Other:\n\tpass\n',
			Path("b.py"): 'class Screen:\n\tdef __init__(self):\n\t\tself.n = 1\n\t\t# self.later()\n\t@decorate(lambda: gc.getDefineINT("B"))\n\tdef later(self):\n\t\tz = gc.getDefineINT("C")\n',
			Path("c.py"): 'from a import Other\nfrom b import Screen\nscreen = Screen()\n',
		}
		self.assertEqual(checker.constructed_at_import_reads(texts), [])

	def test_qualified_bases_and_overrides_are_followed(self):
		# <!-- custom: Codex's second review (GPT-6.2-Sol) reproduced misses for class C(a.Base), a.Base.__init__(self) and a base __init__ calling a method the built class overrides. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		base = Path("a.py")
		user = Path("m.py")
		texts = {
			base: 'class Base:\n\tdef __init__(self):\n\t\tself.read()\n\tdef read(self):\n\t\tpass\nclass Plain:\n\tdef __init__(self):\n\t\tself.x = gc.getDefineINT("P")\n',
			user: 'import a\nclass C(a.Base):\n\tdef read(self):\n\t\tself.y = gc.getDefineINT("C")\nclass D:\n\tdef __init__(self):\n\t\ta.Plain.__init__(self)\none = C()\ntwo = D()\n',
		}
		self.assertEqual([hit[:3] for hit in checker.constructed_at_import_reads(texts)], [(base, 8, "Plain.__init__"), (user, 4, "C.read")])

	def test_default_arguments_run_and_lambda_bodies_wait(self):
		# <!-- custom: def f(x=read()) runs read() at import, f = lambda: later() does not, which a first version had the wrong way round (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		path = Path("L.py")
		text = 'def read():\n\treturn gc.getDefineINT("A")\ndef later():\n\treturn gc.getDefineINT("B")\ndef f(x=read()):\n\tpass\ng = lambda: later()\n'
		self.assertEqual([hit[:3] for hit in checker.constructed_at_import_reads({path: text})], [(path, 2, "read")])

	def test_marker_in_a_string_does_not_exempt(self):
		path = Path("S.py")
		text = 'def read():\n\treturn gc.getDefineINT("A")\nread(); note = "# ci_import_call: not a comment"\n'
		self.assertEqual([hit[:3] for hit in checker.constructed_at_import_reads({path: text})], [(path, 2, "read")])

	def test_marked_module_call_is_not_followed(self):
		text = 'def reload():\n\treturn gc.getDefineINT("A")\n# <!-- custom: ci_import_call: reads only after a reload. (X) -->\nreload()\n'
		self.assertEqual(checker.constructed_at_import_reads({Path("E.py"): text}), [])


if __name__ == "__main__":
	unittest.main()

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys make the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_define_reads_cached as checker


class PythonDefineReadsCachedTests(unittest.TestCase):
	def test_read_at_use_fails(self):
		text = 'def f():\n\tif gc.getDefineINT("A") > 0:\n\t\treturn 1\n'
		self.assertEqual(checker.uncached_reads(text), [(2, "A", "f")])

	def test_marker_in_function_passes(self):
		text = 'def f():\n\t# ci_define_uncached: once per map.\n\tx = gc.getDefineINT("A")\n\treturn x\n'
		self.assertEqual(checker.uncached_reads(text), [])

	def test_marker_after_read_in_same_function_passes(self):
		text = 'def f():\n\tx = gc.getDefineINT("A")\n\t# ci_define_uncached: once per map.\n\treturn x\n'
		self.assertEqual(checker.uncached_reads(text), [])

	def test_marker_in_another_function_fails(self):
		text = 'def f():\n\t# ci_define_uncached: once.\n\treturn 0\n\ndef g():\n\treturn gc.getDefineINT("A")\n'
		self.assertEqual(checker.uncached_reads(text), [(6, "A", "g")])

	def test_marker_inside_a_string_fails(self):
		text = 'def f():\n\tlog("ci_define_uncached: no")\n\treturn gc.getDefineINT("A")\n'
		self.assertEqual(checker.uncached_reads(text), [(3, "A", "f")])

	def test_attribute_in_init_and_lazy_global_pass(self):
		text = 'def __init__(self):\n\tself.x = gc.getDefineINT("A")\n\ndef f():\n\tglobal Y\n\tif Y is None:\n\t\tY = gc.getDefineINT("B")\n'
		self.assertEqual(checker.uncached_reads(text), [])

	def test_store_outside_init_or_in_a_loop_fails(self):
		# <!-- custom: Codex's review (GPT-6.2-Sol) reproduced both: a store into self in a method called at each draw, and one inside a loop, read at each call or pass. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		text = 'def draw(self):\n\tself.x = gc.getDefineINT("A")\n\ndef __init__(self, items):\n\tfor i in items:\n\t\tself.y = gc.getDefineINT("B")\n'
		self.assertEqual(checker.uncached_reads(text), [(2, "A", "draw"), (6, "B", "__init__")])

	def test_unrelated_guard_fails_and_inline_lazy_guard_passes(self):
		text = 'def f(self, value):\n\tif self.ready and value is None:\n\t\tvalue = gc.getDefineINT("A")\n\tif self.x is None: self.x = gc.getDefineINT("B")\n'
		self.assertEqual(checker.uncached_reads(text), [(3, "A", "f")])

	def test_read_split_after_its_bracket_fails(self):
		text = 'def f():\n\treturn gc.getDefineINT(\n\t\t"A")\n'
		self.assertEqual(checker.uncached_reads(text), [(2, "A", "f")])

	def test_inner_loop_needs_its_own_marker_and_while_condition_belongs_to_its_loop(self):
		text = 'def f(rows):\n\tfor r in rows:\n\t\t# ci_define_uncached: once per row.\n\t\tfor c in r:\n\t\t\tx = gc.getDefineINT("A")\n\t# ci_define_uncached: once.\n\twhile gc.getDefineINT("B") > 0:\n\t\tbreak\n'
		self.assertEqual(checker.uncached_reads(text), [(5, "A", "f"), (7, "B", "f")])

	def test_attribute_of_a_local_object_fails(self):
		# <!-- custom: MoreCiv4lerts' deal field is built at each call, so it caches nothing. (Claude code Opus 5.5) -->
		text = 'def f():\n\ttradeData = TradeData()\n\ttradeData.iData = gc.getDefineINT("PEACE_TREATY_LENGTH")\n'
		self.assertEqual(checker.uncached_reads(text), [(3, "PEACE_TREATY_LENGTH", "f")])

	def test_lazy_guards_on_self_or_global_pass(self):
		text = 'def f(self):\n\tif self.x is None:\n\t\tm = gc.getDefineINT("A")\n\t\tself.x = m\n\tif getattr(self, "y", None) is None:\n\t\tself.y = 1 + gc.getDefineINT("B")\n'
		self.assertEqual(checker.uncached_reads(text), [])

	def test_parameter_fallback_fails(self):
		# <!-- custom: CvMapGeneratorUtil's "if fracXExp is None:" falls back to the define at each call, so it is no cache. (Claude code Opus 5.5) -->
		text = 'def f(self, a=None):\n\tif a is None:\n\t\ta = self.gc.getDefineINT("A")\n\treturn a\n'
		self.assertEqual(checker.uncached_reads(text), [(3, "A", "f")])

	def test_nested_function_needs_its_own_marker(self):
		text = 'def f():\n\t# ci_define_uncached: once.\n\tdef g():\n\t\treturn gc.getDefineINT("A")\n\treturn g\n'
		self.assertEqual(checker.uncached_reads(text), [(4, "A", "g")])

	def test_one_line_def_needs_a_marker_on_its_line(self):
		text = 'def f(): return gc.getDefineINT("A")\ndef g(): return gc.getDefineINT("B")  # ci_define_uncached: once.\n'
		self.assertEqual(checker.uncached_reads(text), [(1, "A", "f")])

	def test_loop_body_needs_a_marker_inside_the_loop(self):
		# <!-- custom: As in the C++ check, a read at each pass is not covered by a reason for the whole function. (Claude code Opus 5.5) -->
		text = 'def f(cities):\n\t# ci_define_uncached: once.\n\tfor c in cities:\n\t\tx = gc.getDefineINT("A")\n'
		self.assertEqual(checker.uncached_reads(text), [(4, "A", "f")])
		text = 'def f(cities):\n\tfor c in cities:\n\t\t# ci_define_uncached: rare.\n\t\tx = gc.getDefineINT("A")\n'
		self.assertEqual(checker.uncached_reads(text), [])

	def test_loop_header_follows_the_function_marker(self):
		text = 'def f(city):\n\t# ci_define_uncached: once per city.\n\tfor i in range(gc.getDefineINT("MAX_TRADE_ROUTES")):\n\t\tpass\n'
		self.assertEqual(checker.uncached_reads(text), [])

	def test_module_reads_and_variable_names_are_left_alone(self):
		# <!-- custom: Module-level reads are python_define_reads_import.py's; a name read through a variable is a cache's own lookup. (Claude code Opus 5.5) -->
		text = 'X = gc.getDefineINT("A")\ndef f(name):\n\treturn gc.getDefineINT(name)\n'
		self.assertEqual(checker.uncached_reads(text), [])


if __name__ == "__main__":
	unittest.main()

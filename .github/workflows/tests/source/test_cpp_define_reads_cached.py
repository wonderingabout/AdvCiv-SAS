# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys make the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import cpp_define_reads_cached as checker


class CppDefineReadsCachedTests(unittest.TestCase):
	def test_read_in_a_loop_fails(self):
		# <!-- custom: The shape of the 2026-11-25 finding in SAS_logFirstCityShadowScoutEntry. (Claude code Opus 5.5) -->
		text = "void f()\n{\n\tfor (int i = 0; i < n; i++)\n\t\tx += GC.getDefineINT(\"SAS_A\") * i;\n}\n"
		self.assertEqual(checker.uncached_reads(text), [(4, "SAS_A")])

	def test_static_passes(self):
		self.assertEqual(checker.uncached_reads("void f()\n{\n\tstatic const int iA = GC.getDefineINT(\"SAS_A\");\n}\n"), [])

	def test_static_after_a_closed_block_passes(self):
		# <!-- custom: The first version walked past the } and flagged CvUnit.cpp's bSAS_SCRAP_ON. (Claude code Opus 5.5) -->
		text = "void f()\n{\n\tif (b)\n\t{\n\t\tg();\n\t}\n\n\tstatic const bool bA = GC.getDefineBOOL(\"SAS_A\");\n}\n"
		self.assertEqual(checker.uncached_reads(text), [])

	def test_static_array_initializer_passes(self):
		text = "void f()\n{\n\tstatic const int ai[] = {\n\t\tstd::max(0, GC.getDefineINT(\"SAS_A\")),\n\t\tGC.getDefineINT(\"SAS_B\")\n\t};\n}\n"
		self.assertEqual(checker.uncached_reads(text), [])

	def test_marker_in_the_function_passes(self):
		text = "// <!-- custom: ci_define_uncached: runs once at load. (m) -->\nvoid f()\n{\n\tg(GC.getDefineINT(\"SAS_A\"));\n}\n"
		self.assertEqual(checker.uncached_reads(text), [])

	def test_marker_does_not_cover_the_next_function(self):
		text = "void f()\n{\n\t// ci_define_uncached: once.\n\tg(GC.getDefineINT(\"SAS_A\"));\n}\nvoid h()\n{\n\tg(GC.getDefineINT(\"SAS_B\"));\n}\n"
		self.assertEqual(checker.uncached_reads(text), [(8, "SAS_B")])

	def test_inline_class_method_is_its_own_function(self):
		text = "class A\n{\npublic:\n\tbool f()\n\t{\n\t\t// ci_define_uncached: once.\n\t\treturn GC.getDefineBOOL(\"SAS_A\");\n\t}\n\tbool h()\n\t{\n\t\treturn GC.getDefineBOOL(\"SAS_B\");\n\t}\n};\n"
		self.assertEqual(checker.uncached_reads(text), [(11, "SAS_B")])

	def test_comments_and_strings_are_not_reads(self):
		text = "void f()\n{\n\t// GC.getDefineINT(\"SAS_A\")\n\t/* GC.getDefineINT(\"SAS_B\") */\n\tlog(\"GC.getDefineINT(\\\"SAS_C\\\")\");\n}\n"
		self.assertEqual(checker.uncached_reads(text), [])

	def test_inherited_defines_are_reported_only_on_request(self):
		text = "void f()\n{\n\tg(GC.getDefineINT(\"MAX_X\"));\n}\n"
		self.assertEqual(checker.uncached_reads(text), [])
		self.assertEqual(checker.uncached_reads(text, sas_only=False), [(3, "MAX_X")])

	# <!-- custom: The next six are Codex's reproductions against the first version (GPT-6.2-Sol, 2026-11-25), plus the loop scope its review asked for. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	def test_marker_inside_a_string_does_not_count(self):
		text = "void f()\n{\n\tlog(\"ci_define_uncached: example\");\n\tuse(GC.getDefineINT(\"SAS_HOT\"));\n}\n"
		self.assertEqual(checker.uncached_reads(text), [(4, "SAS_HOT")])

	def test_functions_inside_extern_c_are_apart(self):
		text = "extern \"C\"\n{\nvoid f()\n{\n\t// ci_define_uncached: once.\n\tg(GC.getDefineINT(\"SAS_A\"));\n}\nvoid h()\n{\n\tg(GC.getDefineINT(\"SAS_B\"));\n}\n}\n"
		self.assertEqual(checker.uncached_reads(text), [(10, "SAS_B")])

	def test_marker_above_a_loop_does_not_cover_a_read_in_it(self):
		text = "void f()\n{\n\t// ci_define_uncached: setup read.\n\tg(GC.getDefineINT(\"SAS_A\"));\n\tfor (int i = 0; i < n; i++)\n\t{\n\t\tx += GC.getDefineINT(\"SAS_B\");\n\t}\n\twhile (b)\n\t\tx += GC.getDefineINT(\"SAS_C\");\n}\n"
		self.assertEqual(checker.uncached_reads(text), [(7, "SAS_B"), (10, "SAS_C")])

	def test_marker_inside_the_loop_covers_it(self):
		text = "void f()\n{\n\tfor (int i = 0; i < n; i++)\n\t{\n\t\t// ci_define_uncached: a loop of two, once at load.\n\t\tx += GC.getDefineINT(\"SAS_B\");\n\t}\n}\n"
		self.assertEqual(checker.uncached_reads(text), [])

	def test_preprocessor_line_before_a_static_passes(self):
		text = "void f()\n{\n\tg();\n#if X\n\tstatic const int iA = GC.getDefineINT(\"SAS_A\");\n#endif\n}\n"
		self.assertEqual(checker.uncached_reads(text), [])

	def test_comma_declarator_after_an_initializer_passes(self):
		text = "void f()\n{\n\tstatic int a[] = {0}, b = GC.getDefineINT(\"SAS_A\");\n}\n"
		self.assertEqual(checker.uncached_reads(text), [])

	def test_line_spliced_call_is_a_read(self):
		text = "void f()\n{\n\tg(GC.getDefineINT(\\\n\t\t\"SAS_A\"));\n}\n"
		self.assertEqual(checker.uncached_reads(text), [(3, "SAS_A")])

	def test_const_static_passes(self):
		# <!-- custom: CvPlayerAI.cpp writes const static, which Codex's second review found counted as uncached. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		self.assertEqual(checker.uncached_reads("void f()\n{\n\tconst static int iA = GC.getDefineINT(\"SAS_A\");\n}\n"), [])

	def test_repository_passes(self):
		self.assertEqual(checker.main([]), 0)


if __name__ == "__main__":
	unittest.main()

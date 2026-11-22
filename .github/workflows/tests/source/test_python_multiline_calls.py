# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile hold a sample file, sys makes the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_multiline_calls as checker


class PythonMultilineCallsTests(unittest.TestCase):
    def run_checker(self, text, fix=False):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.py"
            path.write_bytes(text.encode("utf-8"))
            errors = checker.file_errors(path, "sample.py", fix)
            return errors, path.read_bytes().decode("utf-8")

    def errors(self, text):
        return self.run_checker(text)[0]

    def test_one_argument_per_line_call_fails(self):
        self.assertEqual(len(self.errors("screen.attachPanelAt(\n\t\"Main\",\n\t\"\",\n\t\"\",\n\t-1)\n")), 1)

    def test_calls_the_old_helper_missed_fail(self):
        # <!-- custom: collapse_multiline_calls.py only knew f(, x = f( and return f(, so these stayed multi-line in SAS files. (Claude code Opus 5.5) -->
        self.assertEqual(len(self.errors("szText += getText(\"KEY\", (\n\tknownText(a),\n\tb))\n")), 1)
        self.assertEqual(len(self.errors("a, b = readValues(\n\tpath,\n\tTrue)\n")), 1)

    def test_tables_pass(self):
        self.assertEqual(self.errors("CHOICES = Choices((\n\t(\"ACCEPT\", \"TXT_A\"),\n\t(\"REFUSE\", \"TXT_B\"),\n))\n"), [])
        self.assertEqual(self.errors("addButtons(popup, {\n\tA: \"TXT_A\",\n\tB: \"TXT_B\"})\n"), [])
        self.assertEqual(self.errors("return (\n\t\"line one\",\n\t\"line two\",\n)\n"), [])

    def test_comments_conditions_and_one_line_calls_pass(self):
        self.assertEqual(self.errors("setText(name,\n\t# <advc.092>\n\tx, y)\n"), [])
        self.assertEqual(self.errors("if (a or\n\tb):\n\tpass\n"), [])
        self.assertEqual(self.errors("setText(name, x, y)\n"), [])

    def test_commented_out_calls_fail_and_prose_passes(self):
        self.assertEqual(len(self.errors("\t#screen.addPanel( \"Main\", u\"Debug\",\n\t#\t\t  0, 1,\n\t#\t\t  PanelStyles.PANEL_STYLE_BLUELARGE )\nx = 1\n")), 1)
        self.assertEqual(self.errors("# getCount() returns the number of trades (one per deal,\n# not per item).\nx = 1\n"), [])

    def test_fix_collapses_a_commented_out_call(self):
        errors, text = self.run_checker("\t#screen.addPanel( \"Main\",\n\t#\t\t  0, 1 )\nx = 1\n", fix=True)
        self.assertEqual(errors, [])
        self.assertEqual(text, "\t#screen.addPanel( \"Main\", 0, 1 )\nx = 1\n")

    def test_codex_review_cases(self):
        # <!-- custom: Codex's review (2026-11-22) reproduced each: a "#f(" inside a triple-quoted string taken for disabled code and rewritten by --fix, subscript and commented-out return targets missed, and a call already on one line flagged for its condition. See KI#21.7. (Claude code Opus 5.5) -->
        text = "s = '''\n#f(a,\n# b)\n'''\n"
        errors, fixed = self.run_checker(text, fix=True)
        self.assertEqual((errors, fixed), ([], text))
        self.assertEqual(len(self.errors("out[0] = f(a,\n\tb)\n")), 1)
        self.assertEqual(len(self.errors("\t#return f(a,\n\t#\tb)\nx = 1\n")), 1)
        self.assertEqual(self.errors("x = f() if (a or\n\tb) else c\n"), [])

    def test_windows_1252_ellipsis_byte_keeps_line_numbers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.py"
            path.write_bytes(b"# was \x85\nx = f(a,\n\tb)\n")
            self.assertEqual(checker.file_errors(path, "sample.py", True), [])
            self.assertEqual(path.read_bytes(), b"# was \x85\nx = f(a, b)\n")

    def test_fix_collapses_and_keeps_the_code(self):
        errors, text = self.run_checker("\tscreen.setText( \"Header\", \n\t\t\t\"Background\",\n\t\t\t-1 )\nx = 1\n", fix=True)
        self.assertEqual(errors, [])
        self.assertEqual(text, "\tscreen.setText( \"Header\", \"Background\", -1 )\nx = 1\n")


if __name__ == "__main__":
    unittest.main()

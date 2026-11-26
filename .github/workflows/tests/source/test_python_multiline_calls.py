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
    # <!-- custom: credit added, so --fix can write its note above moved comments; None tests the refusal without one. (Claude code Opus 5.5) -->
    def run_checker(self, text, fix=False, credit="Test model"):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.py"
            path.write_bytes(text.encode("utf-8"))
            errors = checker.file_errors(path, "sample.py", fix, credit)
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

    def test_plain_comment_inside_moves_above_and_markers_stay(self):
        # <!-- custom: The movie screens' setButtonGFC kept "#self.EXIT_TEXT," inside its arguments; AdvCiv's "# <advc.092>" markers stay, as they say which arguments changed (2026-11-22). See KI#21.7. (Claude code Opus 5.5) -->
        errors, text = self.run_checker("\tf(\"Exit\", \"\", #self.EXIT_TEXT,\n\t\tx, y)\n", fix=True)
        self.assertEqual((errors, text), ([], "\t" + checker.hoist_note(1, "Test model") + "\n\t#self.EXIT_TEXT,\n\tf(\"Exit\", \"\", x, y)\n"))
        self.assertEqual(self.errors("setText(name, # advc.002b: text offset\n\tx, y)\n"), [])

    def test_moved_comments_need_a_credit_and_get_one_note(self):
        # <!-- custom: The note above moved comments carries a model credit, so --fix refuses to move one without --credit and leaves the file unchanged (the user, 2026-11-22). (Claude code Opus 5.5) -->
        text = "f(a, # first\n\tb, # second\n\tc)\n"
        errors, fixed = self.run_checker(text, fix=True, credit=None)
        self.assertEqual((len(errors), fixed), (1, text))
        self.assertIn("--credit", errors[0])
        errors, fixed = self.run_checker(text, fix=True)
        self.assertEqual((errors, fixed), ([], checker.hoist_note(2, "Test model") + "\n# first\n# second\nf(a, b, c)\n"))

    def test_codex_credit_review_cases(self):
        # <!-- custom: Codex's review of the credited note (2026-11-22): moved comments that look like a call were merged by the disabled-call pass, a blank credit was accepted, and an em dash credit crashed on a Windows-1252 file. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
        errors, fixed = self.run_checker("f(a, # g(\n\tb, # 1)\n\tc)\n", fix=True)
        self.assertEqual((errors, fixed), ([], checker.hoist_note(2, "Test model") + "\n# g(\n# 1)\nf(a, b, c)\n"))
        self.assertEqual(len(self.errors(checker.hoist_note(1, "Test model") + "\n# note\n# h(a,\n#\tb)\nf(x)\n")), 1)
        text = "f(a, # note\n\tb)\n"
        errors, fixed = self.run_checker(text, fix=True, credit="  ")
        self.assertEqual((len(errors), fixed), (1, text))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "legacy.py"
            original = "f(a, # caf\xe9\n\tb)\n".encode("latin-1")
            path.write_bytes(original)
            errors = checker.file_errors(path, "legacy.py", True, "Model — test")
            self.assertEqual((len(errors), path.read_bytes()), (1, original))
            self.assertIn("legacy.py", errors[0])

    def test_wrapped_flat_list_fails_and_one_item_per_line_passes(self):
        errors, text = self.run_checker("\tITEMS = [\"Power\", \"Assets\",\n\t\t\t\"# Cities\"]\n", fix=True)
        self.assertEqual((errors, text), ([], "\tITEMS = [\"Power\", \"Assets\", \"# Cities\"]\n"))
        self.assertEqual(self.errors("KEYS = (\n\t\"a\",\n\t\"b\",\n)\n"), [])

    def test_codex_second_review_cases(self):
        # <!-- custom: Codex's review of the comment rule (2026-11-22) reproduced each: a disabled call with an inner comment crashed --fix, a moved noqa directive re-enabled its warning, a prose "AdvCiv" exempted a call, an unclosed note hid later disabled calls, and "a and b" counted as a plain value. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
        text = "\t# f(\n\t# 1, # note\n\t# 2)\nx = 1\n"
        errors, fixed = self.run_checker(text, fix=True)
        self.assertEqual((errors, fixed), ([], text))
        self.assertEqual(self.errors("f(a, # noqa: F821\n\tb)\n"), [])
        self.assertEqual(len(self.errors("f(a, # AdvCiv compatibility\n\tb)\n")), 1)
        self.assertEqual(len(self.errors("# <!-- custom: unclosed note\nx = 1\n# g(a,\n#\tb)\ny = 2\n")), 1)
        self.assertEqual(self.errors("X = [a and b, c,\n\td]\n"), [])
        errors, fixed = self.run_checker("f(a,\n\tb)  # end note\n", fix=True)
        self.assertEqual((errors, fixed), ([], "f(a, b) # end note\n"))

    def test_quote_inside_a_custom_note_is_not_disabled_code(self):
        text = "# <!-- custom: AdvCiv writes:\n# self.screen.addMultiListControlGFC(\"List\", u\"\",\n#\t\t4, iSize, # numLists, defaultWidth\n#\t\tTableStyles.TABLE_STYLE_STANDARD)\n# if it helps -->\nx = 1\n"
        self.assertEqual(self.errors(text), [])

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
        # <!-- custom: Codex's review (2026-11-22) reproduced each: a "#f(" inside a triple-quoted string taken for disabled code and rewritten by --fix, subscript and commented-out return targets missed, and a call already on one line flagged for its condition. See KI#21.7. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
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

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile hold a sample file, sys makes the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_aligned_columns as checker


# <!-- custom: Each case below is a pitfall met while fixing the repository with --fix (2026-11-22 to 2026-11-23). See KI#21.8. (Claude code Opus 5.5) -->
class PythonAlignedColumnsTests(unittest.TestCase):
    def run_checker(self, text, fix=False):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.py"
            path.write_bytes(text.encode("utf-8"))
            errors = checker.file_errors(path, "sample.py", fix)
            return errors, path.read_bytes().decode("utf-8")

    def fixed(self, text):
        # <!-- custom: A second pass must change nothing: the first table finder grew tables from whichever line it met first, and passes over SevoPediaMain.py's widget IDs flipped between two layouts. (Claude code Opus 5.5) -->
        errors, fixed = self.run_checker(text, fix=True)
        self.assertEqual(errors, [])
        self.assertEqual(self.run_checker(fixed), ([], fixed))
        return fixed

    def test_space_aligned_table_becomes_tabs(self):
        # <!-- custom: A table's widest row often has one space before its next column, as "bAllGoodyTechs" here, and still joins its table. (Claude code Opus 5.5) -->
        text = "S = (\n\t(\"bNoGoodies\",     \"No Goodies\",      1),\n\t(\"bAllGoodyTechs\", \"All Goody Techs\", 2),\n\t(\"bNoAnimals\",     \"No Animals\",      3),\n)\n"
        self.assertEqual(len(self.run_checker(text)[0]), 3)
        self.assertEqual(self.fixed(text), "S = (\n\t(\"bNoGoodies\",\t\t\"No Goodies\",\t\t1),\n\t(\"bAllGoodyTechs\",\t\"All Goody Techs\",\t2),\n\t(\"bNoAnimals\",\t\t\"No Animals\",\t\t3),\n)\n")

    def test_one_column_table_gets_one_space(self):
        # <!-- custom: SAS_WorldSizeUtils.py's WorldSizeTypes.WORLDSIZE_ARENA:  1, and enum or assignment lists gain little from one aligned column (the user, 2026-11-23); Tectonics.py's xMoves =\t\t[ rows were tab-only. (Claude code Opus 5.5) -->
        self.assertEqual(self.fixed("D = {\n\tARENA:     1,\n\tSTANDARD:  2,\n\tHUGE:      3,\n}\n"), "D = {\n\tARENA: 1,\n\tSTANDARD: 2,\n\tHUGE: 3,\n}\n")
        self.assertEqual(self.fixed("xMoves =\t\t[0, 1]\nsubduction =\t[1, 0]\n"), "xMoves = [0, 1]\nsubduction = [1, 0]\n")

    def test_column_that_aligns_nothing_gets_one_space(self):
        # <!-- custom: Ring.py's option dicts, such as `4:  "TXT_KEY_MAP_WORLD_WRAP"`, have one-digit keys, so their tab aligned nothing (the user, 2026-11-22). (Claude code Opus 5.5) -->
        text = "S = (\n\t(\"a\",    \"x\",  1),\n\t(\"bbbbb\", \"y\",  2),\n\t(\"cc\",   \"zzz\", 3),\n)\n"
        self.assertEqual(self.fixed(text), "S = (\n\t(\"a\",\t\t\"x\",\t1),\n\t(\"bbbbb\",\t\"y\",\t2),\n\t(\"cc\",\t\t\"zzz\",\t3),\n)\n")
        self.assertEqual(self.fixed("D = {\n\t4:  \"WRAP\",\n\t5:  \"RES\",\n}\n"), "D = {\n\t4: \"WRAP\",\n\t5: \"RES\",\n}\n")

    def test_tab_table_must_match_the_fix_layout(self):
        # <!-- custom: Like a formatter's check, a tab table whose stops are not the ones --fix chooses fails too; CvDebugInfoScreen.py's dispatch rows also mixed a space with tabs. (Claude code Opus 5.5) -->
        good = "S = (\n\t(\"a\",\t\t\"x\",\t1),\n\t(\"bbbbb\",\t\"yy\",\t2),\n)\n"
        self.assertEqual(self.run_checker(good)[0], [])
        self.assertEqual(len(self.run_checker(good.replace("\"a\",\t\t", "\"a\",\t\t\t"))[0]), 1)
        self.assertEqual(len(self.run_checker(good.replace("\"a\",\t\t", "\"a\", \t"))[0]), 1)

    def test_lone_double_space_becomes_one(self):
        self.assertEqual(self.fixed("x =  y\nelif_ = 1\n"), "x = y\nelif_ = 1\n")
        # <!-- custom: GameFontDisplay.py's two identical rows both held "%  (iID)": not a column, as columns meet only at separators. (Claude code Opus 5.5) -->
        self.assertEqual(self.fixed("a = (u\" %c\" %  (i))\nb = (u\" %c\" %  (i))\n"), "a = (u\" %c\" % (i))\nb = (u\" %c\" % (i))\n")

    def test_strings_comments_and_indentation_are_left_alone(self):
        self.assertEqual(self.run_checker("x = \"a  b\"  # two  spaces\n    y = 1\n")[0], [])

    def test_row_with_no_space_after_its_commas_keeps_its_columns(self):
        # <!-- custom: SevoPediaEraChart.py's ("iAIMaxGroundbreakingPenalty","AI Max Groundbreaking Pen.", row. (Claude code Opus 5.5) -->
        text = "S = (\n\t(\"a\",    \"x\",   1),\n\t(\"bbbbb\",\"yyy\",2),\n\t(\"cc\",   \"z\",   3),\n)\n"
        self.assertEqual(self.fixed(text), "S = (\n\t(\"a\",\t\t\"x\",\t1),\n\t(\"bbbbb\",\t\"yyy\",\t2),\n\t(\"cc\",\t\t\"z\",\t3),\n)\n")

    def test_one_space_column_does_not_merge(self):
        # <!-- custom: SevoPediaWorldSizeChart.py's "Building Class Prereq Mod" row had one space before its next column, which once merged two columns. (Claude code Opus 5.5) -->
        text = "S = (\n\t(\"a\",      \"b\",  1),\n\t(\"cccccccc\", \"dddd\", 2),\n\t(\"e\",      \"f\",  3),\n)\n"
        self.assertEqual(self.fixed(text), "S = (\n\t(\"a\",\t\t\t\"b\",\t1),\n\t(\"cccccccc\",\t\"dddd\",\t2),\n\t(\"e\",\t\t\t\"f\",\t3),\n)\n")

    def test_dotted_names_are_not_split(self):
        # <!-- custom: CvCustomizableDomesticAdvisor.py's COLUMNS_LIST holds CyCity.getCommerceRate in one row where another holds None; columns meet at separators only. (Claude code Opus 5.5) -->
        text = "L = [\n\t(\"A\",  None,  CyCity.getRate, 1),\n\t(\"BB\", CyCity.getModifier, None, 0),\n]\n"
        fixed = self.fixed(text)
        self.assertIn("CyCity.getRate,", fixed)
        self.assertIn("CyCity.getModifier,", fixed)

    def test_differently_shaped_neighbours_are_not_aligned_together(self):
        # <!-- custom: SevoPediaMain.py's HEAD_TEXT and BACK_TEXT lines sit together but are different calls; only rows with as many separators share columns. (Claude code Opus 5.5) -->
        text = "h = a + f(\"T\",      ()) + c\nb = g(f(\"B\",    (), x).upper())\n"
        self.assertEqual(self.fixed(text), "h = a + f(\"T\", ()) + c\nb = g(f(\"B\", (), x).upper())\n")

    def test_separators_must_match_in_kind_and_depth(self):
        # <!-- custom: Codex's review (2026-11-23): a call's comma and a slice's colon once paired these two lines as a table. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
        text = "left = foo(a,    b)\nright = bar[long_key:    very_long]\n"
        self.assertEqual(self.fixed(text), "left = foo(a, b)\nright = bar[long_key: very_long]\n")

    def test_changed_lines_drop_trailing_whitespace(self):
        # <!-- custom: git diff --check flagged inherited trailing spaces on lines the sweep touched (Codex's review, 2026-11-23); an unchanged line keeps them, and so does a line opening a multi-line string, where they belong to the string. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
        self.assertEqual(self.fixed("x =  y  \nz = 1  \n"), "x = y\nz = 1  \n")
        text = "s =  \"\"\"a  \nb\"\"\"\n"
        self.assertEqual(self.fixed(text), "s = \"\"\"a  \nb\"\"\"\n")

    def test_strings_that_look_like_commented_code_stay(self):
        # <!-- custom: Codex's review (2026-11-23): "# x =  y" inside a live triple-quoted string, and inside a commented-out one, was laid out as commented-out code, changing the string. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
        live = "text = \"\"\"\n# x =  y\n\"\"\"\n"
        self.assertEqual(self.run_checker(live), ([], live))
        commented = "# text = \"\"\"\n# x =  y\n# \"\"\"\n"
        self.assertEqual(self.run_checker(commented), ([], commented))
        self.assertEqual(self.fixed("# a  = 1\n"), "# a = 1\n")

    def test_table_runs_through_comment_lines(self):
        # <!-- custom: COLUMNS_LIST's "# advc.004:" note between rows once split the table into two layouts. (Claude code Opus 5.5) -->
        text = "L = [\n\t(\"A\",  \"x\",   1),\n\t# note\n\t(\"BBBBBBB\",  \"yyyyy\", 2),\n]\n"
        self.assertEqual(self.fixed(text), "L = [\n\t(\"A\",\t\t\"x\",\t\t1),\n\t# note\n\t(\"BBBBBBB\",\t\"yyyyy\",\t2),\n]\n")


if __name__ == "__main__":
    unittest.main()

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib, subprocess and tempfile build a disposable Git repository; sys locates the checker; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "repository"))
# <!-- custom: adjacent_duplicate_lines is the checker under test. (Claude code Opus 5.5) -->
import adjacent_duplicate_lines as checker


class AdjacentDuplicateLineTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.repo = Path(self.folder.name)
        for args in (("init", "-q"), ("config", "user.name", "CI fixture"), ("config", "user.email", "fixture@example.invalid"), ("config", "commit.gpgsign", "false"), ("config", "core.autocrlf", "false")):
            subprocess.run(["git", *args], cwd=self.repo, check=True)

    def commit(self, path, text):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "Fixture"], cwd=self.repo, check=True)
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        return checker.commit_errors(self.repo, commit)

    def test_added_double_fails_once(self):
        # <!-- custom: The SevoPediaMusic.py case: a label set twice in a row. (Claude code Opus 5.5) -->
        self.commit("a.py", "def f():\n\tstart()\n\treturn 1\n")
        errors = self.commit("a.py", "def f():\n\tstart()\n\tsetLabel(x)\n\tsetLabel(x)\n\treturn 1\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("a.py:4 repeats the line above it", errors[0])

    def test_adding_a_copy_beside_an_old_line_fails(self):
        self.commit("b.cpp", "void f()\n{\n\tg();\n}\n")
        self.assertEqual(len(self.commit("b.cpp", "void f()\n{\n\tg();\n\tg();\n}\n")), 1)

    def test_old_doubles_decoration_xml_and_explained_doubles_pass(self):
        self.commit("c.py", "x = 1\nx = 1\n")
        self.assertEqual(self.commit("c.py", "x = 1\nx = 1\ny = 2\n"), [])
        self.assertEqual(self.commit("d.cpp", "void f()\n{\n\t{\n\t}\n\t}\n}\n"), [])
        self.assertEqual(self.commit("e.xml", "<a>\n\t<i>0</i>\n\t<i>0</i>\n</a>\n"), [])
        self.assertEqual(self.commit("f.cpp", "s.append(NEWLINE);\ns.append(NEWLINE); // blank line\n"), [])

    def test_different_indentation_passes(self):
        self.assertEqual(self.commit("g.py", "if a:\n\t\treturn None\n\treturn None\n"), [])


    def test_cpp_duplicate_include_detects_nonadjacent_addition(self):
        path = "CvGameCoreDLL/Test.cpp"
        old = '#include "RiseFall.h"\n#include "CvBugOptions.h"\n'
        new = old + '# include "RiseFall.h" // advc.708\n'
        self.commit(path, old)
        errors = self.commit(path, new)
        self.assertTrue(any(':3: duplicate C++ include "RiseFall.h"; first included on line 1' in error for error in errors))
        self.assertEqual(checker.cpp_duplicate_include_errors(path, new, new), [])

    def test_cpp_duplicate_include_respects_preprocessor_arms_and_comments(self):
        path = "CvGameCoreDLL/Test.cpp"
        conditional = '#if FIRST\n#include "Same.h"\n#elif SECOND\n#include "Same.h"\n#else\n#include "Same.h"\n#endif\n'
        examples = '/*\n#include "Same.h"\n*/\n// #include "Same.h"\n'
        self.assertEqual(checker.cpp_duplicate_include_errors(path, "", conditional + examples), [])
        nested = '#include "Same.h"\n#if FIRST\n#if NESTED\n#include "Same.h"\n#endif\n#endif\n'
        self.assertEqual(len(checker.cpp_duplicate_include_errors(path, "", nested)), 1)
        repeated_in_arm = conditional.replace('#if FIRST\n', '#if FIRST\n#include "Same.h"\n')
        self.assertEqual(len(checker.cpp_duplicate_include_errors(path, conditional, repeated_in_arm)), 1)

    def test_cpp_adjacent_include_is_reported_once(self):
        header = '#include "Same.h"\n'
        errors = self.commit("adjacent.cpp", header + header)
        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate C++ include", errors[0])

    def test_cpp_duplicate_include_added_by_merge_is_checked(self):
        path = "CvGameCoreDLL/Test.cpp"
        header = '#include "Same.h"\n'
        self.commit(path, header)
        subprocess.run(["git", "switch", "-q", "-c", "side"], cwd=self.repo, check=True)
        self.commit("note.txt", "side branch\n")
        subprocess.run(["git", "switch", "-q", "-"], cwd=self.repo, check=True)
        subprocess.run(["git", "merge", "-q", "--no-ff", "--no-commit", "side"], cwd=self.repo, check=True)
        errors = self.commit(path, header + '\n#include "Same.h"\n')
        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate C++ include", errors[0])


if __name__ == "__main__":
    unittest.main()

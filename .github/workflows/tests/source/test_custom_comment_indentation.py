# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Path/sys load the actual indentation checker; unittest pins the slip it catches and the legitimate shapes it must allow. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build/source"))
# <!-- custom: Import the same checker as CI so fixtures exercise one implementation. (Claude code Opus 5.5) -->
import custom_comment_indentation as checker


class CustomCommentIndentationTests(unittest.TestCase):
    def errors(self, source):
        return checker.check_lines("Test.cpp", source.split("\n"))

    def test_too_deep_note_fails(self):
        source = "\t\t}\n\t\t\t\t// <!-- custom: Retired a guard. (model) -->\n\t\tif (x)\n"
        self.assertEqual(len(self.errors(source)), 1)

    def test_legitimate_shapes_pass(self):
        for source in ["\t\tfoo();\n\t\t// <!-- custom: note (model) -->\n\t\tbar();\n",
                       "\t\t\tfoo();\n\t\t\t// <!-- custom: End - block (model) -->\n\n\t\tbar();\n",
                       "\tif (x)\n\t{\n\t\t// <!-- custom: first line in block (model) -->\n\t}\n",
                       "\t#if x:\n\t\t# <!-- custom: inside commented-out block (model) -->\n\tfoo()\n"]:
            with self.subTest(source=source):
                self.assertEqual(self.errors(source), [])


if __name__ == "__main__":
    unittest.main()

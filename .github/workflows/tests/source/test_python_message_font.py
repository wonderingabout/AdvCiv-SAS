# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys make the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_message_font as checker


class PythonMessageFontTests(unittest.TestCase):
	def test_direct_calls_fail(self):
		text = 'CyInterface().addMessage(i, False, 10, sz, None, 0, None, ColorTypes(-1), 0, 0, False, False)\ninterface = CyInterface()\ninterface.addImmediateMessage(sz, "")\n'
		self.assertEqual(checker.direct_calls(text), [(1, "addMessage"), (3, "addImmediateMessage")])

	def test_only_the_forwarding_functions_may_call(self):
		# <!-- custom: Codex's review (GPT-6.2-Sol) reproduced the first draft passing a direct call anywhere in CvUtil.py; only its helper may make it now. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		text = 'def addCombatMessageScaled(e, sz):\n\tCyInterface().addCombatMessage(e, sz)\ndef other(e, sz):\n\tCyInterface().addCombatMessage(e, sz)\n'
		self.assertEqual(checker.direct_calls(text, "Assets/Python/CvUtil.py"), [(4, "addCombatMessage")])
		text = 'def addMessage(e, b, i, sz):\n\tCyInterface().addMessage(e, b, i, sz)\ndef other(sz):\n\tCyInterface().addImmediateMessage(sz, "")\n'
		self.assertEqual(checker.direct_calls(text, "Assets/Python/SASTextScale.py"), [(4, "addImmediateMessage")])

	def test_unrelated_receivers_comments_and_strings_pass(self):
		text = 'self.ui = CyInterface()\nui.addMessage(record)\ninbox.addMessage(record)\nSASTextScale.addMessage(i, False, 10, sz)\n# CyInterface().addMessage(x)\ns = "CyInterface().addImmediateMessage(x)"\n'
		self.assertEqual(checker.direct_calls(text), [])


if __name__ == "__main__":
	unittest.main()

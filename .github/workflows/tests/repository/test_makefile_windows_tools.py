# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: importlib loads the check from its file, as in the other check tests. (Claude code Opus 5.5) -->
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
_SPEC = importlib.util.spec_from_file_location("makefile_windows_tools", ROOT / ".github/workflows/build/repository/makefile_windows_tools.py")
assert _SPEC is not None and _SPEC.loader is not None
makefile_windows_tools = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(makefile_windows_tools)


class MakefileWindowsToolTests(unittest.TestCase):
	def failures(self, text):
		return makefile_windows_tools.check_text("Makefile", text)

	def test_bare_find_fails(self):
		# <!-- custom: The provenance line that ran Git's find on 2026-11-11 and 2026-11-13. (Claude code Opus 5.5) -->
		self.assertEqual(len(self.failures("\t@FOR /F %i IN ('DIR /S /B x 2^>NUL ^| FIND /C /V \"\"') DO @ECHO %i\n")), 1)

	def test_system32_path_passes(self):
		self.assertEqual(self.failures("\t@FOR /F %i IN ('DIR /S /B x 2^>NUL ^| \"%SystemRoot%\\System32\\find.exe\" /C /V \"\"') DO @ECHO %i\n"), [])
		self.assertEqual(self.failures("\t%SystemRoot%\\System32\\sort.exe list.txt\n"), [])

	def test_control_character_fails(self):
		# <!-- custom: The form feed a shell left where "\f" of "\find.exe" had been (2026-11-13). (Claude code Opus 5.5) -->
		self.assertIn("control character", self.failures("\t%SystemRoot%\\System32\x0cind.exe /C\n")[0])

	def test_name_as_text_passes_but_as_command_fails(self):
		# <!-- custom: Codex's review case: a tool's name in echoed text is not a command. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		self.assertEqual(self.failures("\t@ECHO sort complete\n"), [])
		self.assertEqual(len(self.failures("\tsort list.txt\n\t@SORT list.txt\n\tDIR (find x)\n")), 3)

	def test_names_inside_other_words_and_comments_pass(self):
		self.assertEqual(self.failures("# find the sources\nFINDSTR /C:x y\nSOURCES=$(SRC)\\Sort.cpp\nTARGET=find_paths\n"), [])


if __name__ == "__main__":
	unittest.main()

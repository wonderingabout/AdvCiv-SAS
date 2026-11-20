#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: the shipped and development values of switched GlobalDefines are written only in LLM_Helpers/diagnostics/define_values.py.
# <!-- custom: On 2026-11-19 SAS_UI_DAWN_OF_MAN_ON alone stayed at its shipped 1 after a branch switch, and an audit of the toggle behind it found each shipped value written twice: once in a CI check and once in toggle_dev_diagnostics.py, with nothing keeping the copies in step.
# The values now live once in LLM_Helpers/diagnostics/define_values.py, so a change is made and seen in one place; this check fails when a script writes one of those names with a number again instead of importing it. (Claude code Opus 5.5) -->

from pathlib import Path
import argparse
import re
import sys

# <!-- custom: define_values from LLM_Helpers/diagnostics supplies the names to look for, and xml_defines from the workflows' lib/ the repository root. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "LLM_Helpers" / "diagnostics"))

from define_values import DEVELOPMENT_VALUES, SHIPPED_VALUES
from xml_defines import get_default_repo_root


SCAN_RELATIVE_DIRS = (Path(".github"), Path("LLM_Helpers"), Path("tests"), Path("Assets/Python"), Path("PrivateMaps"))
OWNER = Path("LLM_Helpers/diagnostics/define_values.py")
# <!-- custom: Tests feed chosen values to the checks, such as {"SAS_RUNTIME_STATUS_ON": 1} to exercise an enabled recorder, rather than restating what ships; LLM_Helpers/outputs holds Git-ignored review copies. (Claude code Opus 5.5) -->
SKIPPED_PREFIXES = (".github/workflows/tests/", "tests/", "LLM_Helpers/outputs/")


def value_pattern(names):
	# <!-- custom: A name in quotes followed by ":" or "," and a number, as in {"NAME": 1}, ("NAME", 0) or "NAME": (1, 0); the name alone, as in getDefineINT("NAME"), is fine. (Claude code Opus 5.5) -->
	return re.compile(r"""["'](%s)["']\s*[:,]\s*\(?\s*-?\d""" % "|".join(re.escape(name) for name in sorted(names)))


def find_problems(repo_root):
	pattern = value_pattern(set(SHIPPED_VALUES) | set(DEVELOPMENT_VALUES))
	problems = []
	for relative in SCAN_RELATIVE_DIRS:
		for path in sorted((repo_root / relative).rglob("*.py")):
			shown = path.relative_to(repo_root).as_posix()
			if "__pycache__" in shown or shown == OWNER.as_posix() or shown.startswith(SKIPPED_PREFIXES):
				continue
			for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
				if line.lstrip().startswith("#"):
					continue
				match = pattern.search(line)
				if match:
					problems.append("%s:%d: %s is written with a value here; import it from %s instead" % (shown, number, match.group(1), OWNER.as_posix()))
	return problems


def main():
	parser = argparse.ArgumentParser(description="Check that switched GlobalDefines values are written only in LLM_Helpers/diagnostics/define_values.py.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	problems = find_problems(args.repo_root.resolve())
	for problem in problems:
		print("ERROR: " + problem)
	if problems:
		print("FAIL shared define values (%d)" % len(problems))
		return 1
	print("PASS shared define values")
	return 0


if __name__ == "__main__":
	sys.exit(main())

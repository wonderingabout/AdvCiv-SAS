#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: SASGameRecord report logging must be disabled by default, the public revision/current history marker must stay synchronized, and canonical readable AI-strategy diagnostics must match the native enum.

from pathlib import Path
import argparse
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from xml_defines import get_default_repo_root, read_global_define_ints, require_int_values


REVISION_HEADER = Path("CvGameCoreDLL/SASGameRecordLog.h")
REVISION_SOURCE = Path("CvGameCoreDLL/SASGameRecordLog.cpp")
REVISION_HISTORY = Path("_1_AdvCiv-SAS/Docs/README_SASGameRecord_Revisions.md")
AI_STRATEGIES_HEADER = Path("CvGameCoreDLL/AIStrategies.h")
GAME_CORE_UTILS_SOURCE = Path("CvGameCoreDLL/CvGameCoreUtils.cpp")



def check_revision(repo_root: Path) -> list[str]:
	failures = []
	for relative_path in (REVISION_HEADER, REVISION_SOURCE, REVISION_HISTORY):
		if not (repo_root / relative_path).is_file():
			failures.append(f"missing SASGameRecord revision file: {relative_path}")
	if failures:
		return failures

	header_text = (repo_root / REVISION_HEADER).read_text(encoding="utf-8", errors="replace")
	revision_matches = re.findall(r"\bSAS_GAME_RECORD_REVISION\s*=\s*(\d+)\b", header_text)
	if len(revision_matches) != 1:
		return [f"{REVISION_HEADER}: expected exactly one SAS_GAME_RECORD_REVISION assignment, found {len(revision_matches)}"]
	revision = int(revision_matches[0])

	history_text = (repo_root / REVISION_HISTORY).read_text(encoding="utf-8", errors="replace")
	history_revisions = [int(value) for value in re.findall(r"^### Revision (\d+) - SAS practical ", history_text, flags=re.MULTILINE)]
	if not history_revisions:
		failures.append(f"{REVISION_HISTORY}: no revision-history headings found")
	else:
		if history_revisions[0] != revision:
			failures.append(f"revision mismatch: source={revision}, newest history={history_revisions[0]}")
		expected = list(range(revision, 0, -1))
		if history_revisions != expected:
			failures.append(f"{REVISION_HISTORY}: expected contiguous latest-first revisions {revision}..1")
	documented_revision_matches = re.findall(r"GAME_RECORD_SOURCE_CONTEXT recordRevision=(\d+) \.\.\.", history_text)
	if len(documented_revision_matches) != 1:
		failures.append(f"{REVISION_HISTORY}: expected exactly one current emitted recordRevision example, found {len(documented_revision_matches)}")
	elif int(documented_revision_matches[0]) != revision:
		failures.append(f"{REVISION_HISTORY}: current emitted recordRevision example={documented_revision_matches[0]}, source={revision}")

	source_text = (repo_root / REVISION_SOURCE).read_text(encoding="utf-8", errors="replace")
	if 'GAME_RECORD_SOURCE_CONTEXT recordRevision=%d %s' not in source_text or 'SAS_GAME_RECORD_REVISION' not in source_text:
		failures.append(f"{REVISION_SOURCE}: missing emitted recordRevision SOURCE_CONTEXT field tied to SAS_GAME_RECORD_REVISION")
	return failures

def check_ai_strategy_diagnostics(repo_root: Path) -> list[str]:
	failures = []
	for relative_path in (AI_STRATEGIES_HEADER, GAME_CORE_UTILS_SOURCE, REVISION_SOURCE):
		if not (repo_root / relative_path).is_file():
			failures.append(f"missing AI-strategy diagnostic file: {relative_path}")
	if failures:
		return failures

	enum_text = (repo_root / AI_STRATEGIES_HEADER).read_text(encoding="utf-8", errors="replace")
	enum_match = re.search(r"enum\s+AIStrategy\b[^\{]*\{(?P<body>.*?)\};", enum_text, flags=re.DOTALL)
	if enum_match is None:
		return [f"{AI_STRATEGIES_HEADER}: could not locate enum AIStrategy"]
	enum_entries = re.findall(
		r"^\s*(NO_AI_STRATEGY|AI_DEFAULT_STRATEGY|AI_STRATEGY_[A-Z0-9_]+)\s*=\s*([^,]+),",
		enum_match.group("body"), flags=re.MULTILINE)
	if not enum_entries:
		return [f"{AI_STRATEGIES_HEADER}: no explicitly assigned AIStrategy enumerators found"]
	enum_tokens = [token for token, _ in enum_entries]
	if len(enum_tokens) != len(set(enum_tokens)):
		failures.append(f"{AI_STRATEGIES_HEADER}: duplicate AIStrategy enumerator names found")
	if enum_tokens[0] != "NO_AI_STRATEGY" or len(enum_tokens) < 2 or enum_tokens[1] != "AI_DEFAULT_STRATEGY":
		failures.append(f"{AI_STRATEGIES_HEADER}: expected NO_AI_STRATEGY then AI_DEFAULT_STRATEGY at the start of enum AIStrategy")
	for iEntry, (token, expression) in enumerate(enum_entries):
		normalized_expression = re.sub(r"\s+", "", expression)
		if token == "NO_AI_STRATEGY":
			if normalized_expression != "0":
				failures.append(f"{AI_STRATEGIES_HEADER}: NO_AI_STRATEGY must remain 0 for complete bit scans")
			continue
		bit_match = re.fullmatch(r"\(?1<<(?P<bit>\d+)\)?", normalized_expression)
		expected_bit = iEntry - 1
		if bit_match is None or int(bit_match.group("bit")) != expected_bit:
			failures.append(
				f"{AI_STRATEGIES_HEADER}: {token} must remain the contiguous bit (1 << {expected_bit}); "
				f"complete SASGameRecord scans advance with iStrategy <<= 1")
	strategy_tokens = [token for token in enum_tokens if token.startswith("AI_STRATEGY_")]
	if not strategy_tokens:
		failures.append(f"{AI_STRATEGIES_HEADER}: no non-default AI_STRATEGY_* enumerators found")
		return failures
	last_strategy = strategy_tokens[-1]

	utils_text = (repo_root / GAME_CORE_UTILS_SOURCE).read_text(encoding="utf-8", errors="replace")
	helper_match = re.search(
		r"char\s+const\*\s+getSASAIStrategyType\s*\([^)]*\)\s*\{(?P<body>.*?)^\}",
		utils_text, flags=re.DOTALL | re.MULTILINE)
	if helper_match is None:
		failures.append(f"{GAME_CORE_UTILS_SOURCE}: missing getSASAIStrategyType definition")
	else:
		case_pairs = re.findall(r'case\s+(NO_AI_STRATEGY|AI_DEFAULT_STRATEGY|AI_STRATEGY_[A-Z0-9_]+)\s*:\s*return\s+"([^"]+)"\s*;', helper_match.group("body"))
		case_tokens = [token for token, _ in case_pairs]
		if len(case_tokens) != len(set(case_tokens)):
			failures.append(f"{GAME_CORE_UTILS_SOURCE}: duplicate getSASAIStrategyType case(s) found")
		missing = [token for token in enum_tokens if token not in case_tokens]
		extra = [token for token in case_tokens if token not in enum_tokens]
		if missing:
			failures.append(f"{GAME_CORE_UTILS_SOURCE}: getSASAIStrategyType missing {', '.join(missing)}")
		if extra:
			failures.append(f"{GAME_CORE_UTILS_SOURCE}: getSASAIStrategyType has non-enum case(s): {', '.join(extra)}")
		for token, label in case_pairs:
			if token != label:
				failures.append(f"{GAME_CORE_UTILS_SOURCE}: {token} maps to {label!r}, expected identical raw enum token")

	record_text = (repo_root / REVISION_SOURCE).read_text(encoding="utf-8", errors="replace")
	loop_matches = re.findall(
		r"for\s*\(\s*int\s+iStrategy\s*=\s*(AI_DEFAULT_STRATEGY|AI_STRATEGY_DAGGER)\s*;\s*"
		r"iStrategy\s*<=\s*(AI_STRATEGY_[A-Z0-9_]+)\s*;\s*iStrategy\s*<<=\s*1\s*\)",
		record_text, flags=re.DOTALL)
	if len(loop_matches) != 3:
		failures.append(f"{REVISION_SOURCE}: expected 3 complete AIStrategy scans (CORE/snapshot/transitions), found {len(loop_matches)}")
	else:
		starts = [start for start, _ in loop_matches]
		if starts.count("AI_DEFAULT_STRATEGY") != 1 or starts.count("AI_STRATEGY_DAGGER") != 2:
			failures.append(f"{REVISION_SOURCE}: expected one CORE scan from AI_DEFAULT_STRATEGY and two readable scans from AI_STRATEGY_DAGGER")
		for start, end in loop_matches:
			if end != last_strategy:
				failures.append(f"{REVISION_SOURCE}: strategy scan starting at {start} ends at {end}, current enum ends at {last_strategy}")
	for required in ("GAME_RECORD_AI_STRATEGIES", "GAME_RECORD_AI_STRATEGY_CHANGE", "getSASAIStrategyType"):
		if required not in record_text:
			failures.append(f"{REVISION_SOURCE}: missing AI-strategy diagnostic token {required}")
	return failures



EXPECTED_GAME_RECORD_DEFAULTS = {
	"SAS_GAME_RECORD_LOG_LEVEL": 0,
	# These configure enabled record logging but do not enable it themselves.
	"SAS_GAME_RECORD_INTERVAL_TURNS_UNSCALED_GAMESPEED": 10,
	"SAS_GAME_RECORD_LOG_USE_TIMESTAMPED_FILENAME": 1,
	"SAS_GAME_RECORD_PERFORMANCE_METRICS_ENABLE": 1,
	"SAS_GAME_RECORD_SYSTEM_CONTEXT_LEVEL": 2,
}


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that SASGameRecord report logging is disabled by default unless explicitly listed as non-enabling configuration.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()

	defines = read_global_define_ints(args.repo_root)
	failures = require_int_values(defines, EXPECTED_GAME_RECORD_DEFAULTS)
	failures.extend(check_revision(args.repo_root))
	failures.extend(check_ai_strategy_diagnostics(args.repo_root))
	if failures:
		print("FAIL SASGameRecord report/revision checks")
		for failure in failures:
			print(f"  - {failure}")
		return 1
	print(f"PASS SASGameRecord report/revision checks: logging defaults={len(EXPECTED_GAME_RECORD_DEFAULTS)}, revision history/current marker/AI-strategy diagnostics synchronized")
	return 0


if __name__ == "__main__":
	sys.exit(main())

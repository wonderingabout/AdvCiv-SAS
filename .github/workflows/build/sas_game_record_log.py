#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: SASGameRecord report logging must be disabled by default, the public revision/current history marker must stay synchronized.
# Canonical readable AI-strategy/AreaAI/contact diagnostics must match their native enums, exact AI target-city provenance/checkpoints must cover every writer/effective clear, periodic AI-attitude provenance must stay synchronized with AI_updateAttitude, and strategic/vote/contact decision schemas must remain present.

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
CV_ENUMS_HEADER = Path("CvGameCoreDLL/CvEnums.h")
GAME_CORE_UTILS_SOURCE = Path("CvGameCoreDLL/CvGameCoreUtils.cpp")
PLAYER_AI_SOURCE = Path("CvGameCoreDLL/CvPlayerAI.cpp")
PLAYER_AI_HEADER = Path("CvGameCoreDLL/CvPlayerAI.h")
GAME_SOURCE = Path("CvGameCoreDLL/CvGame.cpp")
PLAYER_SOURCE = Path("CvGameCoreDLL/CvPlayer.cpp")
PLOT_SOURCE = Path("CvGameCoreDLL/CvPlot.cpp")
CITY_SOURCE = Path("CvGameCoreDLL/CvCity.cpp")
TEAM_AI_SOURCE = Path("CvGameCoreDLL/CvTeamAI.cpp")
UWAI_AGENT_SOURCE = Path("CvGameCoreDLL/UWAIAgent.cpp")



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


def check_area_ai_diagnostics(repo_root: Path) -> list[str]:
	failures = []
	for relative_path in (CV_ENUMS_HEADER, GAME_CORE_UTILS_SOURCE, TEAM_AI_SOURCE, UWAI_AGENT_SOURCE, REVISION_SOURCE):
		if not (repo_root / relative_path).is_file():
			failures.append(f"missing AreaAI diagnostic file: {relative_path}")
	if failures:
		return failures

	enum_text = (repo_root / CV_ENUMS_HEADER).read_text(encoding="utf-8", errors="replace")
	enum_match = re.search(r"ENUM_START\(AreaAI,\s*AREAAI\)(?P<body>.*?)ENUM_END\(AreaAI,\s*AREAAI\)", enum_text, flags=re.DOTALL)
	if enum_match is None:
		return [f"{CV_ENUMS_HEADER}: could not locate AreaAI enum block"]
	enum_tokens = ["NO_AREAAI"] + re.findall(r"^\s*(AREAAI_[A-Z0-9_]+)\s*,", enum_match.group("body"), flags=re.MULTILINE)
	if len(enum_tokens) != len(set(enum_tokens)) or len(enum_tokens) < 2:
		failures.append(f"{CV_ENUMS_HEADER}: invalid/duplicate AreaAI enumerators found")

	utils_text = (repo_root / GAME_CORE_UTILS_SOURCE).read_text(encoding="utf-8", errors="replace")
	helper_match = re.search(r"char\s+const\*\s+getSASAreaAIType\s*\([^)]*\)\s*\{(?P<body>.*?)^\}", utils_text, flags=re.DOTALL | re.MULTILINE)
	if helper_match is None:
		failures.append(f"{GAME_CORE_UTILS_SOURCE}: missing getSASAreaAIType definition")
	else:
		case_pairs = re.findall(r'case\s+(NO_AREAAI|AREAAI_[A-Z0-9_]+)\s*:\s*return\s+"([^"]+)"\s*;', helper_match.group("body"))
		case_tokens = [token for token, _ in case_pairs]
		missing = [token for token in enum_tokens if token not in case_tokens]
		extra = [token for token in case_tokens if token not in enum_tokens]
		if missing:
			failures.append(f"{GAME_CORE_UTILS_SOURCE}: getSASAreaAIType missing {', '.join(missing)}")
		if extra:
			failures.append(f"{GAME_CORE_UTILS_SOURCE}: getSASAreaAIType has non-enum case(s): {', '.join(extra)}")
		for token, label in case_pairs:
			if token != label:
				failures.append(f"{GAME_CORE_UTILS_SOURCE}: {token} maps to {label!r}, expected identical raw enum token")

	team_text = (repo_root / TEAM_AI_SOURCE).read_text(encoding="utf-8", errors="replace")
	uwai_text = (repo_root / UWAI_AGENT_SOURCE).read_text(encoding="utf-8", errors="replace")
	record_text = (repo_root / REVISION_SOURCE).read_text(encoding="utf-8", errors="replace")
	# AI_updateAreaStrategies deliberately duplicates the one-line setter between its disabled fast path and logged path so recorder-off gameplay pays no per-area diagnostic branch/read. UWAI has one setter in its alignment writer.
	if team_text.count("setAreaAIType(") != 2 or uwai_text.count("setAreaAIType(") != 1:
		failures.append(f"AreaAI writer shape changed: expected two guarded setter call sites in {TEAM_AI_SOURCE} and one in {UWAI_AGENT_SOURCE}")
	if "logSASGameRecordAreaAIChanged(" not in team_text or '"CALCULATED"' not in team_text:
		failures.append(f"{TEAM_AI_SOURCE}: missing calculated AreaAI transition bridge/source provenance")
	if ("logSASGameRecordAreaAIChanged(" not in uwai_text or '"UWAI_ALIGN_NAVAL"' not in uwai_text or
			'"UWAI_ALIGN_LAND"' not in uwai_text):
		failures.append(f"{UWAI_AGENT_SOURCE}: missing UWAI AreaAI transition bridge/source provenance")
	for required in ("GAME_RECORD_AREA_AI_CHANGE", "GAME_RECORD_AREA_AI", "getSASAreaAIType"):
		if required not in record_text:
			failures.append(f"{REVISION_SOURCE}: missing AreaAI diagnostic token {required}")
	if "logSASGameRecordAreaAISnapshot(BARBARIAN_TEAM, iGameTurn);" not in record_text:
		failures.append(f"{REVISION_SOURCE}: missing Barbarian AreaAI periodic checkpoint bridge")
	return failures


def check_ai_target_city_provenance(repo_root: Path) -> list[str]:
	failures = []
	required_paths = (REVISION_HEADER, REVISION_SOURCE, PLAYER_AI_SOURCE, PLAYER_SOURCE, PLOT_SOURCE, CITY_SOURCE)
	for relative_path in required_paths:
		if not (repo_root / relative_path).is_file():
			failures.append(f"missing AI target-city provenance file: {relative_path}")
	if failures:
		return failures

	header_text = (repo_root / REVISION_HEADER).read_text(encoding="utf-8", errors="replace")
	expected_sources = [
		"SAS_AI_TARGET_CITY_AREA_SEARCH",
		"SAS_AI_TARGET_CITY_RANDOM_CLEAR",
		"SAS_AI_TARGET_CITY_DIPLO_COORDINATION",
		"SAS_AI_TARGET_CITY_AREA_REASSIGN_CLEAR",
		"SAS_AI_TARGET_CITY_CITY_REMOVED",
	]
	enum_match = re.search(
		r"enum\s+SASGameRecordAITargetCityChangeSource\s*\{(?P<body>.*?)\};",
		header_text, flags=re.DOTALL)
	if enum_match is None:
		failures.append(f"{REVISION_HEADER}: missing SASGameRecordAITargetCityChangeSource enum")
	else:
		source_tokens = re.findall(r"\b(SAS_AI_TARGET_CITY_[A-Z0-9_]+)\b", enum_match.group("body"))
		if source_tokens != expected_sources:
			failures.append(
				f"{REVISION_HEADER}: AI target-city source vocabulary changed; "
				f"expected {expected_sources}, found {source_tokens}")

	record_text = (repo_root / REVISION_SOURCE).read_text(encoding="utf-8", errors="replace")
	mapping_match = re.search(
		r"getSASGameRecordAITargetCityChangeSource\s*\([^)]*\)\s*\{(?P<body>.*?)^\}",
		record_text, flags=re.DOTALL | re.MULTILINE)
	if mapping_match is None:
		failures.append(f"{REVISION_SOURCE}: missing AI target-city source-name mapping")
	else:
		mapped_tokens = re.findall(
			r'case\s+(SAS_AI_TARGET_CITY_[A-Z0-9_]+)\s*:\s*return\s+"[A-Z0-9_]+"\s*;',
			mapping_match.group("body"))
		if mapped_tokens != expected_sources:
			failures.append(
				f"{REVISION_SOURCE}: AI target-city source-name mapping changed; "
				f"expected {expected_sources}, found {mapped_tokens}")

	# The normal updater keeps one target-refresh loop and caches its level-2 gate once.
	# Provenance-only old-target/value work remains conditional; writer counts guard new state-changing paths.
	writer_files = {}
	for source_path in (repo_root / "CvGameCoreDLL").glob("*.cpp"):
		if source_path.name == "CvArea.cpp":
			continue  # contains the setter definition, not a caller
		source_text = source_path.read_text(encoding="utf-8", errors="replace")
		count = source_text.count("AI_setTargetCity(")
		if count:
			writer_files[source_path.name] = count
	expected_writer_files = {"CvPlayerAI.cpp": 1, "CvPlayer.cpp": 1, "CvPlot.cpp": 1}
	if writer_files != expected_writer_files:
		failures.append(
			f"AI target-city writer shape changed; expected {expected_writer_files}, found {writer_files}. "
			"Update exact transition provenance/checkpoints together with any new writer.")

	player_ai_text = (repo_root / PLAYER_AI_SOURCE).read_text(encoding="utf-8", errors="replace")
	player_text = (repo_root / PLAYER_SOURCE).read_text(encoding="utf-8", errors="replace")
	plot_text = (repo_root / PLOT_SOURCE).read_text(encoding="utf-8", errors="replace")
	city_text = (repo_root / CITY_SOURCE).read_text(encoding="utf-8", errors="replace")
	for source_text, relative_path, required in (
		(player_ai_text, PLAYER_AI_SOURCE, (
			"SAS_AI_TARGET_CITY_AREA_SEARCH", "SAS_AI_TARGET_CITY_RANDOM_CLEAR",
			"bLogTargetCityChanges", "&iSelectionValue", "logSASGameRecordAITargetCityChanged(",
		)),
		(player_text, PLAYER_SOURCE, (
			"SAS_AI_TARGET_CITY_DIPLO_COORDINATION", "logSASGameRecordAITargetCityChanged(",
		)),
		(plot_text, PLOT_SOURCE, (
			"SAS_AI_TARGET_CITY_AREA_REASSIGN_CLEAR", "logSASGameRecordAITargetCityChanged(",
		)),
		(city_text, CITY_SOURCE, (
			"SAS_AI_TARGET_CITY_CITY_REMOVED", "logSASGameRecordAITargetCityChanged(",
		)),
	):
		for token in required:
			if token not in source_text:
				failures.append(f"{relative_path}: missing AI target-city provenance token {token}")

	for required in (
		"GAME_RECORD_AI_TARGET_CITY_CHANGE", "GAME_RECORD_AI_TARGET_CITIES",
		"selectionValue=%d", "areaAI=%s", "newTargetWarPlan=%s",
		"logSASGameRecordAITargetCities(ePlayer, iGameTurn);",
	):
		if required not in record_text:
			failures.append(f"{REVISION_SOURCE}: missing AI target-city diagnostic/checkpoint token {required}")
	return failures


def _strip_cpp_comments(text: str) -> str:
	text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
	return re.sub(r"//.*", "", text)


def check_ai_attitude_breakdown(repo_root: Path) -> list[str]:
	failures = []
	for relative_path in (PLAYER_AI_SOURCE, REVISION_SOURCE):
		if not (repo_root / relative_path).is_file():
			failures.append(f"missing AI-attitude diagnostic file: {relative_path}")
	if failures:
		return failures

	expected_getters = [
		"AI_getFirstImpressionAttitude", "AI_getTeamSizeAttitude", "AI_getRankDifferenceAttitude",
		"AI_getCloseBordersAttitude", "AI_getPeaceAttitude", "AI_getSameReligionAttitude",
		"AI_getDifferentReligionAttitude", "AI_getBonusTradeAttitude", "AI_getOpenBordersAttitude",
		"AI_getDefensivePactAttitude", "AI_getRivalDefensivePactAttitude", "AI_getRivalVassalAttitude",
		"AI_getExpansionistAttitude", "AI_getShareWarAttitude", "AI_getFavoriteCivicAttitude",
		"AI_getTradeAttitude", "AI_getRivalTradeAttitude", "AI_getMemoryAttitude",
		"AI_getAttitudeExtra", "AI_getWarAttitude",
	]
	expected_labels = [
		"firstImpression", "teamSize", "rankDifference", "closeBorders", "peace", "sameReligion",
		"differentReligion", "bonusTrade", "openBorders", "defensivePact", "rivalDefensivePact",
		"rivalVassal", "expansionist", "sharedWar", "favoriteCivic", "trade", "rivalTrade",
		"memories", "extra", "war",
	]

	player_text = (repo_root / PLAYER_AI_SOURCE).read_text(encoding="utf-8", errors="replace")
	start = player_text.find("void CvPlayerAI::AI_updateAttitude(PlayerTypes ePlayer")
	end = player_text.find("// for making minor adjustments", start)
	if start < 0 or end < 0:
		return [f"{PLAYER_AI_SOURCE}: could not isolate CvPlayerAI::AI_updateAttitude(PlayerTypes,...)"]
	update_body = _strip_cpp_comments(player_text[start:end])
	getters = re.findall(
		r"(?:int\s+iAttitude\s*=|iAttitude\s*\+=)\s*(AI_get[A-Za-z0-9_]+)\s*\(",
		update_body)
	if getters != expected_getters:
		failures.append(
			f"{PLAYER_AI_SOURCE}: AI_updateAttitude component sequence changed; "
			f"expected {expected_getters}, found {getters}. Update GAME_RECORD_DIPLO_ATTITUDE_BREAKDOWN and this check together.")

	record_text = (repo_root / REVISION_SOURCE).read_text(encoding="utf-8", errors="replace")
	start = record_text.find("static void logSASGameRecordDiplomaticAttitudes(PlayerTypes ePlayer")
	end = record_text.find("static void logSASGameRecordDiploStatus(PlayerTypes ePlayer", start)
	if start < 0 or end < 0:
		return failures + [f"{REVISION_SOURCE}: could not isolate logSASGameRecordDiplomaticAttitudes"]
	record_body = _strip_cpp_comments(record_text[start:end])
	labels = re.findall(r'appendSASGameRecordAttitudeComponent\s*\([^;]*?"([A-Za-z0-9_]+)"', record_body)
	if labels != expected_labels:
		failures.append(
			f"{REVISION_SOURCE}: attitude-breakdown component labels/order changed; "
			f"expected {expected_labels}, found {labels}")
	for required in (
		"GAME_RECORD_DIPLO_ATTITUDE_BREAKDOWN", "componentSum=%+d", "componentValue=%+d",
		"cachedRawValue=%+d", "effectiveValue=%+d", "forcedDelta=%+d",
	):
		if required not in record_body:
			failures.append(f"{REVISION_SOURCE}: missing AI-attitude diagnostic token {required}")
	return failures


def check_strategic_trade_market(repo_root: Path) -> list[str]:
	failures = []
	record_path = repo_root / REVISION_SOURCE
	if not record_path.is_file():
		return [f"missing strategic trade-market diagnostic file: {REVISION_SOURCE}"]

	record_text = record_path.read_text(encoding="utf-8", errors="replace")
	start = record_text.find("static void logSASGameRecordStrategicTradeMarketPair")
	end = record_text.find("static void logSASGameRecordTradeMarket", start)
	if start < 0 or end < 0:
		return [f"{REVISION_SOURCE}: could not isolate logSASGameRecordStrategicTradeMarketPair"]
	record_body = _strip_cpp_comments(record_text[start:end])
	expected_items = [
		"TRADE_MAPS", "TRADE_VASSAL", "TRADE_SURRENDER", "TRADE_OPEN_BORDERS",
		"TRADE_DEFENSIVE_PACT", "TRADE_PERMANENT_ALLIANCE", "TRADE_DISENGAGE",
	]
	items = re.findall(
		r"appendSASGameRecordStrategicTradeStatus\s*\([^;]*?,\s*(TRADE_[A-Z0-9_]+)\s*\);",
		record_body, flags=re.DOTALL)
	if items != expected_items:
		failures.append(
			f"{REVISION_SOURCE}: strategic bilateral trade-status sequence changed; "
			f"expected {expected_items}, found {items}")
	for required in (
		"GAME_RECORD_TRADE_STRATEGIC", "bilateral=%s", "citiesWillCede=%s", "cityDenials=%s",
		"glanceWarTargets=%s", "glanceWarTargetDenials=%s",
	):
		if required not in record_body:
			failures.append(f"{REVISION_SOURCE}: missing strategic trade-market diagnostic token {required}")

	market_start = record_text.find("static void logSASGameRecordTradeMarket(int iGameTurn)")
	market_end = record_text.find("static void logSASGameRecordEnvironment", market_start)
	if market_start < 0 or market_end < 0:
		failures.append(f"{REVISION_SOURCE}: could not isolate logSASGameRecordTradeMarket")
	else:
		market_body = _strip_cpp_comments(record_text[market_start:market_end])
		for required in (
			"if (!isSASGameRecordTradeMarketEnabled())",
			"logSASGameRecordStrategicTradeMarketPair(",
		):
			if required not in market_body:
				failures.append(f"{REVISION_SOURCE}: missing strategic trade-market gate/bridge token {required}")
	return failures


def check_uwai_war_plan_decisions(repo_root: Path) -> list[str]:
	failures = []
	for relative_path in (REVISION_HEADER, REVISION_SOURCE, UWAI_AGENT_SOURCE):
		if not (repo_root / relative_path).is_file():
			failures.append(f"missing UWAI war-plan provenance file: {relative_path}")
	if failures:
		return failures

	expected = [
		("SAS_UWAI_WAR_PLAN_ILLEGAL_TARGET", "ILLEGAL_TARGET"),
		("SAS_UWAI_WAR_PLAN_VICTORY_DENIAL_DIRECT", "VICTORY_DENIAL_DIRECT"),
		("SAS_UWAI_WAR_PLAN_IMMINENT_NEGATIVE_UTILITY", "IMMINENT_NEGATIVE_UTILITY"),
		("SAS_UWAI_WAR_PLAN_IMMINENT_TIMEOUT", "IMMINENT_TIMEOUT"),
		("SAS_UWAI_WAR_PLAN_PREPARATION_DEADLINE_REACHED", "PREPARATION_DEADLINE_REACHED"),
		("SAS_UWAI_WAR_PLAN_PREPARATION_DEADLINE_NEGATIVE_UTILITY", "PREPARATION_DEADLINE_NEGATIVE_UTILITY"),
		("SAS_UWAI_WAR_PLAN_SEVERE_NEGATIVE_UTILITY", "SEVERE_NEGATIVE_UTILITY"),
		("SAS_UWAI_WAR_PLAN_TARGET_SWITCH", "TARGET_SWITCH"),
		("SAS_UWAI_WAR_PLAN_ATTACKED_RECENT_MATURED", "ATTACKED_RECENT_MATURED"),
		("SAS_UWAI_WAR_PLAN_ACTIVE_TYPE_SWITCH", "ACTIVE_TYPE_SWITCH"),
		("SAS_UWAI_WAR_PLAN_DIRECT_UTILITY_THRESHOLD", "DIRECT_UTILITY_THRESHOLD"),
	]
	expected_tokens = [token for token, _ in expected]

	header_text = (repo_root / REVISION_HEADER).read_text(encoding="utf-8", errors="replace")
	enum_match = re.search(r"enum\s+SASGameRecordUWAIWarPlanDecisionReason\s*\{(?P<body>.*?)\};", header_text, flags=re.DOTALL)
	if enum_match is None:
		failures.append(f"{REVISION_HEADER}: missing SASGameRecordUWAIWarPlanDecisionReason")
	else:
		enum_tokens = re.findall(r"^\s*(SAS_UWAI_WAR_PLAN_[A-Z0-9_]+)\s*,?\s*$", enum_match.group("body"), flags=re.MULTILINE)
		if enum_tokens != expected_tokens:
			failures.append(f"{REVISION_HEADER}: UWAI war-plan decision reasons changed; expected {expected_tokens}, found {enum_tokens}")

	record_text = (repo_root / REVISION_SOURCE).read_text(encoding="utf-8", errors="replace")
	mapping_match = re.search(r"getSASGameRecordUWAIWarPlanDecisionReason\s*\([^)]*\)\s*\{(?P<body>.*?)^\}", record_text, flags=re.DOTALL | re.MULTILINE)
	if mapping_match is None:
		failures.append(f"{REVISION_SOURCE}: missing UWAI war-plan reason stringifier")
	else:
		pairs = re.findall(r'case\s+(SAS_UWAI_WAR_PLAN_[A-Z0-9_]+)\s*:\s*return\s+"([A-Z0-9_]+)"\s*;', mapping_match.group("body"))
		if pairs != expected:
			failures.append(f"{REVISION_SOURCE}: UWAI war-plan reason mapping changed; expected {expected}, found {pairs}")
	for required in (
		"GAME_RECORD_AI_WAR_PLAN_DECISION", "planner=UWAI", "action=%s", "reason=%s",
		"comparisonTargetTeam=%d", "comparisonUtility=%d", "decisionValue=%d",
		"decisionThreshold=%d", "victoryDenialBoost=%d",
	):
		if required not in record_text:
			failures.append(f"{REVISION_SOURCE}: missing foreground-UWAI war-plan diagnostic token {required}")

	uwai_text = (repo_root / UWAI_AGENT_SOURCE).read_text(encoding="utf-8", errors="replace")
	bridge_count = uwai_text.count("logSASGameRecordUWAIWarPlanDecision(")
	if bridge_count != len(expected):
		failures.append(f"{UWAI_AGENT_SOURCE}: expected {len(expected)} realized UWAI war-plan decision bridges, found {bridge_count}")
	for token in expected_tokens:
		if uwai_text.count(token) != 1:
			failures.append(f"{UWAI_AGENT_SOURCE}: expected exactly one realized bridge for {token}, found {uwai_text.count(token)}")
	return failures


def check_ai_diplo_vote_provenance(repo_root: Path) -> list[str]:
	failures = []
	for relative_path in (REVISION_HEADER, REVISION_SOURCE, PLAYER_AI_SOURCE, PLAYER_AI_HEADER, TEAM_AI_SOURCE, GAME_SOURCE):
		if not (repo_root / relative_path).is_file():
			failures.append(f"missing AI diplomatic-vote provenance file: {relative_path}")
	if failures:
		return failures

	expected = [
		("SAS_AI_DIPLO_VOTE_TEAM_SELF_ELIGIBLE", "TEAM_SELF_ELIGIBLE"),
		("SAS_AI_DIPLO_VOTE_TEAM_VASSAL_MASTER", "TEAM_VASSAL_MASTER"),
		("SAS_AI_DIPLO_VOTE_TEAM_OWN_DIPLO_VICTORY_ABSTAIN", "TEAM_OWN_DIPLO_VICTORY_ABSTAIN"),
		("SAS_AI_DIPLO_VOTE_TEAM_ATTITUDE_TIE_ABSTAIN", "TEAM_ATTITUDE_TIE_ABSTAIN"),
		("SAS_AI_DIPLO_VOTE_TEAM_BEST_ATTITUDE", "TEAM_BEST_ATTITUDE"),
		("SAS_AI_DIPLO_VOTE_SECRETARY_SELF_OR_MASTER", "SECRETARY_SELF_OR_MASTER"),
		("SAS_AI_DIPLO_VOTE_FRIENDLY_SECRETARY", "FRIENDLY_SECRETARY"),
		("SAS_AI_DIPLO_VOTE_FORCE_CIVIC", "FORCE_CIVIC"),
		("SAS_AI_DIPLO_VOTE_TRADE_ROUTES", "TRADE_ROUTES"),
		("SAS_AI_DIPLO_VOTE_NO_NUKES", "NO_NUKES"),
		("SAS_AI_DIPLO_VOTE_FREE_TRADE", "FREE_TRADE"),
		("SAS_AI_DIPLO_VOTE_OPEN_BORDERS", "OPEN_BORDERS"),
		("SAS_AI_DIPLO_VOTE_DEFENSIVE_PACT", "DEFENSIVE_PACT"),
		("SAS_AI_DIPLO_VOTE_FORCE_PEACE", "FORCE_PEACE"),
		("SAS_AI_DIPLO_VOTE_EMBARGO_RECENT_DEAL", "EMBARGO_RECENT_DEAL"),
		("SAS_AI_DIPLO_VOTE_EMBARGO_UNMET_ABSTAIN", "EMBARGO_UNMET_ABSTAIN"),
		("SAS_AI_DIPLO_VOTE_EMBARGO", "EMBARGO"),
		("SAS_AI_DIPLO_VOTE_FORCE_WAR", "FORCE_WAR"),
		("SAS_AI_DIPLO_VOTE_ASSIGN_CITY", "ASSIGN_CITY"),
		("SAS_AI_DIPLO_VOTE_DEFAULT", "DEFAULT"),
	]
	expected_tokens = [token for token, _ in expected]

	header_text = (repo_root / REVISION_HEADER).read_text(encoding="utf-8", errors="replace")
	enum_match = re.search(r"enum\s+SASGameRecordAIDiploVoteReason\s*\{(?P<body>.*?)\};", header_text, flags=re.DOTALL)
	if enum_match is None:
		failures.append(f"{REVISION_HEADER}: missing SASGameRecordAIDiploVoteReason")
	else:
		enum_tokens = re.findall(r"^\s*(SAS_AI_DIPLO_VOTE_[A-Z0-9_]+)\s*,?\s*$", enum_match.group("body"), flags=re.MULTILINE)
		if enum_tokens != expected_tokens:
			failures.append(f"{REVISION_HEADER}: AI diplomatic-vote reasons changed; expected {expected_tokens}, found {enum_tokens}")

	record_text = (repo_root / REVISION_SOURCE).read_text(encoding="utf-8", errors="replace")
	mapping_match = re.search(r"getSASGameRecordAIDiploVoteReason\s*\([^)]*\)\s*\{(?P<body>.*?)^\}", record_text, flags=re.DOTALL | re.MULTILINE)
	if mapping_match is None:
		failures.append(f"{REVISION_SOURCE}: missing AI diplomatic-vote reason stringifier")
	else:
		pairs = re.findall(r'case\s+(SAS_AI_DIPLO_VOTE_[A-Z0-9_]+)\s*:\s*return\s+"([A-Z0-9_]+)"\s*;', mapping_match.group("body"))
		if pairs != expected:
			failures.append(f"{REVISION_SOURCE}: AI diplomatic-vote reason mapping changed; expected {expected}, found {pairs}")
	for required in (
		"GAME_RECORD_AI_DIPLO_VOTE", "triggeredId=%d", "choice=%s", "reason=%s",
		"decisionValue=%s", "decisionThreshold=%s", "randomRoll=%s",
		"GAME_RECORD_AI_ELECTION_CHOICE", "selectionId=%d", "selectedRandomValue=%d", "selectedVictoryBoost=%d",
	):
		if required not in record_text:
			failures.append(f"{REVISION_SOURCE}: missing AI diplomatic-vote/proposal diagnostic token {required}")

	player_header = (repo_root / PLAYER_AI_HEADER).read_text(encoding="utf-8", errors="replace")
	if "bool bPropose, int iTriggeredVoteId = -1" not in player_header:
		failures.append(f"{PLAYER_AI_HEADER}: AI_diploVote must keep optional triggered-vote identity for real-ballot provenance")
	player_text = (repo_root / PLAYER_AI_SOURCE).read_text(encoding="utf-8", errors="replace")
	if "!isHuman() && iTriggeredVoteId >= 0 && getSASGameRecordLogLevel() >= 2" not in player_text:
		failures.append(f"{PLAYER_AI_SOURCE}: actual AI ballot logging must remain pre-gated by non-human, triggered id and level 2+")
	for token in expected_tokens:
		if token not in player_text and token != "SAS_AI_DIPLO_VOTE_DEFAULT":
			failures.append(f"{PLAYER_AI_SOURCE}: no live AI_diploVote path references {token}")

	game_text = (repo_root / GAME_SOURCE).read_text(encoding="utf-8", errors="replace")
	actual_ballot_calls = game_text.count("AI_diploVote(kOptionData, eVoteSource, false, pData->getID())")
	if actual_ballot_calls != 2:
		failures.append(f"{GAME_SOURCE}: expected two real ballot calls to pass triggered vote id, found {actual_ballot_calls}")

	team_text = (repo_root / TEAM_AI_SOURCE).read_text(encoding="utf-8", errors="replace")
	choose_match = re.search(r"int\s+CvTeamAI::AI_chooseElection\([^)]*\)\s+const\s*\{(?P<body>.*?)^\}", team_text, flags=re.DOTALL | re.MULTILINE)
	if choose_match is None:
		failures.append(f"{TEAM_AI_SOURCE}: could not locate AI_chooseElection")
	else:
		body = choose_match.group("body")
		if body.count("SyncRandNum(10000)") != 1:
			failures.append(f"{TEAM_AI_SOURCE}: AI_chooseElection must retain exactly one existing proposal-selection RNG call site")
		if body.count("logSASGameRecordAIElectionChoice(") != 1:
			failures.append(f"{TEAM_AI_SOURCE}: expected exactly one compact AI election-choice recorder bridge")
	return failures


def check_ai_conquer_city_provenance(repo_root: Path) -> list[str]:
	failures = []
	for relative_path in (REVISION_HEADER, REVISION_SOURCE, PLAYER_AI_SOURCE):
		if not (repo_root / relative_path).is_file():
			failures.append(f"missing AI captured-city provenance file: {relative_path}")
	if failures:
		return failures

	header_text = (repo_root / REVISION_HEADER).read_text(encoding="utf-8", errors="replace")
	expected_outcomes = [
		"SAS_AI_CONQUER_CITY_KEEP", "SAS_AI_CONQUER_CITY_RAZE", "SAS_AI_CONQUER_CITY_LIBERATE",
	]
	expected_reasons = [
		"SAS_AI_CONQUER_CITY_CANNOT_RAZE", "SAS_AI_CONQUER_CITY_DOMINATION3_PRIMARY_AREA_KEEP",
		"SAS_AI_CONQUER_CITY_CULTURE_VICTORY", "SAS_AI_CONQUER_CITY_UNLIKELY_LONG_TERM_BENEFIT",
		"SAS_AI_CONQUER_CITY_EARLY_REMOTE_BARB", "SAS_AI_CONQUER_CITY_EARLY_REMOTE_NONBARB",
		"SAS_AI_CONQUER_CITY_BARBARIAN_VALUE", "SAS_AI_CONQUER_CITY_NORMAL_VALUE",
		"SAS_AI_CONQUER_CITY_LIBERATION", "SAS_AI_CONQUER_CITY_LIBERATION_WITHHELD_HOSTAGE",
	]
	for enum_name, expected in (("SASGameRecordAIConquerCityOutcome", expected_outcomes), ("SASGameRecordAIConquerCityReason", expected_reasons)):
		m = re.search(r"enum\s+" + enum_name + r"\s*\{(?P<body>.*?)\};", header_text, flags=re.DOTALL)
		if m is None:
			failures.append(f"{REVISION_HEADER}: missing {enum_name}")
			continue
		tokens = re.findall(r"^\s*(SAS_AI_CONQUER_CITY_[A-Z0-9_]+)\s*,?\s*$", m.group("body"), flags=re.MULTILINE)
		if tokens != expected:
			failures.append(f"{REVISION_HEADER}: {enum_name} changed; expected {expected}, found {tokens}")

	record_text = (repo_root / REVISION_SOURCE).read_text(encoding="utf-8", errors="replace")
	for required in (
		"GAME_RECORD_AI_CONQUER_CITY_DECISION", "outcome=%s", "reason=%s", "valueValid=%d",
		"razeValueBeforeRandom=%d", "random=%d", "razeValue=%d", "componentsValid=%d",
		"distanceAndLocalPower=%d", "maintenanceDelta=%+d", "populationDelta=%+d",
		"personalityDominationDelta=%+d", "otherDelta=%+d", "barbarianRollPassed=%d", "liberationPlayer=%d",
	):
		if required not in record_text:
			failures.append(f"{REVISION_SOURCE}: missing AI captured-city diagnostic token {required}")
	for token in expected_outcomes + expected_reasons:
		if token not in record_text:
			failures.append(f"{REVISION_SOURCE}: captured-city stringifier missing {token}")

	player_text = (repo_root / PLAYER_AI_SOURCE).read_text(encoding="utf-8", errors="replace")
	for token in expected_reasons:
		if token not in player_text:
			failures.append(f"{PLAYER_AI_SOURCE}: no AI_conquerCity path references {token}")
	if "bLogSASConquerCityDecision = (gGameRecordLogLevel >= 2)" not in player_text:
		failures.append(f"{PLAYER_AI_SOURCE}: captured-city valuation logging must retain the cached level-2 gate")
	if player_text.count("SyncRandSuccess100(iRazeValue)") != 1:
		failures.append(f"{PLAYER_AI_SOURCE}: inherited Barbarian raze percentage roll must remain a single live RNG call site")
	if player_text.count("SyncRandNum(6)") < 1:
		failures.append(f"{PLAYER_AI_SOURCE}: normal raze valuation lost its existing SyncRandNum(6) random component")
	return failures


def check_ai_diplo_contact_provenance(repo_root: Path) -> list[str]:
	failures = []
	for relative_path in (CV_ENUMS_HEADER, GAME_CORE_UTILS_SOURCE, REVISION_SOURCE, PLAYER_AI_SOURCE):
		if not (repo_root / relative_path).is_file():
			failures.append(f"missing AI diplomatic-contact provenance file: {relative_path}")
	if failures:
		return failures

	enum_text = (repo_root / CV_ENUMS_HEADER).read_text(encoding="utf-8", errors="replace")
	enum_match = re.search(r"ENUM_START\(Contact,\s*CONTACT\)(?P<body>.*?)ENUM_END\(Contact,\s*CONTACT\)", enum_text, flags=re.DOTALL)
	if enum_match is None:
		return [f"{CV_ENUMS_HEADER}: could not locate Contact enum block"]
	enum_tokens = re.findall(r"^\s*(CONTACT_[A-Z0-9_]+)\s*,", enum_match.group("body"), flags=re.MULTILINE)
	if not enum_tokens or len(enum_tokens) != len(set(enum_tokens)):
		failures.append(f"{CV_ENUMS_HEADER}: invalid/duplicate Contact enumerators found")

	utils_text = (repo_root / GAME_CORE_UTILS_SOURCE).read_text(encoding="utf-8", errors="replace")
	helper_match = re.search(r"char\s+const\*\s+getSASContactType\s*\([^)]*\)\s*\{(?P<body>.*?)^\}", utils_text, flags=re.DOTALL | re.MULTILINE)
	if helper_match is None:
		failures.append(f"{GAME_CORE_UTILS_SOURCE}: missing getSASContactType definition")
	else:
		case_pairs = re.findall(r'case\s+(CONTACT_[A-Z0-9_]+)\s*:\s*return\s+"([^"]+)"\s*;', helper_match.group("body"))
		case_tokens = [token for token, _ in case_pairs]
		missing = [token for token in enum_tokens if token not in case_tokens]
		extra = [token for token in case_tokens if token not in enum_tokens]
		if missing:
			failures.append(f"{GAME_CORE_UTILS_SOURCE}: getSASContactType missing {', '.join(missing)}")
		if extra:
			failures.append(f"{GAME_CORE_UTILS_SOURCE}: getSASContactType has non-enum case(s): {', '.join(extra)}")
		if len(case_tokens) != len(set(case_tokens)):
			failures.append(f"{GAME_CORE_UTILS_SOURCE}: duplicate getSASContactType case(s) found")
		for token, label in case_pairs:
			if token != label:
				failures.append(f"{GAME_CORE_UTILS_SOURCE}: {token} maps to {label!r}, expected identical raw enum token")

	record_text = (repo_root / REVISION_SOURCE).read_text(encoding="utf-8", errors="replace")
	for required in (
		"GAME_RECORD_AI_DIPLO_CONTACT", "contact=%s", "delivery=%s", "attitudeValue=%d",
		"subject=%s", "aiGives=%s", "aiReceives=%s", "getSASContactType",
	):
		if required not in record_text:
			failures.append(f"{REVISION_SOURCE}: missing AI diplomatic-contact diagnostic token {required}")

	player_text = (repo_root / PLAYER_AI_SOURCE).read_text(encoding="utf-8", errors="replace")
	bridged_contacts = re.findall(
		r"logSASGameRecordAIDiploContactIntent\s*\([^;]*?\b(CONTACT_[A-Z0-9_]+)\b",
		player_text, flags=re.DOTALL)
	bridged_set = set(bridged_contacts)
	expected_generic = {
		"CONTACT_RELIGION_PRESSURE", "CONTACT_CIVIC_PRESSURE", "CONTACT_JOIN_WAR",
		"CONTACT_STOP_TRADING", "CONTACT_GIVE_HELP", "CONTACT_ASK_FOR_HELP",
		"CONTACT_DEMAND_TRIBUTE", "CONTACT_OPEN_BORDERS", "CONTACT_DEFENSIVE_PACT",
		"CONTACT_PERMANENT_ALLIANCE", "CONTACT_TRADE_TECH", "CONTACT_TRADE_MAP",
	}
	missing_generic = sorted(expected_generic - bridged_set)
	unexpected_generic = sorted(bridged_set - expected_generic)
	if missing_generic:
		failures.append(f"{PLAYER_AI_SOURCE}: generic realized-contact provenance missing {', '.join(missing_generic)}")
	if unexpected_generic:
		failures.append(f"{PLAYER_AI_SOURCE}: unexpected generic realized-contact class(es): {', '.join(unexpected_generic)}")
	for delivery in ('"HUMAN_CONTACT"', '"AI_DEAL"'):
		if delivery not in record_text:
			failures.append(f"{REVISION_SOURCE}: missing realized diplomatic-contact delivery marker {delivery}")
	if "gGameRecordLogLevel >= 2" not in player_text:
		failures.append(f"{PLAYER_AI_SOURCE}: realized diplomatic-contact bridges must remain level-2 pre-gated")

	# Peace and proactive resource exchange already have richer dedicated provenance;
	# keeping them out of the generic row prevents duplicate rows for the same intent.
	for specialized in ("GAME_RECORD_AI_PEACE_DECISION", "GAME_RECORD_AI_BONUS_TRADE_DECISION"):
		if specialized not in record_text:
			failures.append(f"{REVISION_SOURCE}: specialized contact provenance missing {specialized}")
	if "CONTACT_PEACE_TREATY" in bridged_set or "CONTACT_TRADE_BONUS" in bridged_set:
		failures.append(f"{PLAYER_AI_SOURCE}: peace/resource intent should remain in specialized provenance rather than duplicate GAME_RECORD_AI_DIPLO_CONTACT")
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
	failures.extend(check_area_ai_diagnostics(args.repo_root))
	failures.extend(check_ai_target_city_provenance(args.repo_root))
	failures.extend(check_ai_attitude_breakdown(args.repo_root))
	failures.extend(check_strategic_trade_market(args.repo_root))
	failures.extend(check_uwai_war_plan_decisions(args.repo_root))
	failures.extend(check_ai_diplo_vote_provenance(args.repo_root))
	failures.extend(check_ai_diplo_contact_provenance(args.repo_root))
	failures.extend(check_ai_conquer_city_provenance(args.repo_root))
	if failures:
		print("FAIL SASGameRecord report/revision checks")
		for failure in failures:
			print(f"  - {failure}")
		return 1
	print(f"PASS SASGameRecord report/revision checks: logging defaults={len(EXPECTED_GAME_RECORD_DEFAULTS)}, revision history/current marker/AI-strategy/AreaAI/AI-target-city/AI-attitude/strategic-trade/UWAI-war-plan/AI-vote/AI-contact/AI-conquer-city diagnostics synchronized")
	return 0


if __name__ == "__main__":
	sys.exit(main())

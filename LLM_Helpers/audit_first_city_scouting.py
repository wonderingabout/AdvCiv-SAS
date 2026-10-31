#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
"""Summarize opening Settler traces without adding game-side instrumentation."""

# <!-- custom: Use Python 3 standard-library CLI, streaming text parsing and timestamped JSON reports; this helper runs outside Civ4 and needs no runtime dependency. (GPT-6.1-Sol) -->
import argparse
import glob
import json
from pathlib import Path
import re
# <!-- custom: UTC timestamps keep optional offline reports distinct across repeated batch reviews. (GPT-6.1-Sol) -->
from datetime import datetime, timezone


FIELDS = re.compile(r'(\w+)=("(?:\\.|[^"\\])*"|\S+)')
SCOUT_PREFIX = "GAME_RECORD_AI_FIRST_CITY_"


def fields(line):
    result = {}
    for key, value in FIELDS.findall(line):
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except ValueError:
                value = value[1:-1]
        result[key] = value
    return result


def point(row, x="fromX", y="fromY"):
    return (int(row[x]), int(row[y]))


def session(header):
    # <!-- custom: Sink timestamps can differ by a second.
    # Match the process and load ordinal, never nearest wall time; missing identity cannot safely pair runs. (GPT-6.1-Sol) -->
    ordinal = re.search(r"_load(\d+)\.log$", header.get("logFile", ""))
    if header.get("processUtc") and ordinal:
        return header["processUtc"], ordinal.group(1)
    return None


def read_record(path):
    result = {"record": str(path), "header": {}, "players": {}, "units": {}, "lastTurn": None}
    with path.open(encoding="utf-8-sig", errors="replace") as stream:
        for line_number, line in enumerate(stream, 1):
            tag = line.split(" ", 1)[0]
            if not (tag.startswith(SCOUT_PREFIX) or tag in (
                    "GAME_RECORD_SAVE_LOADED", "GAME_RECORD_NEW_GAME_STARTED", "GAME_RECORD_PLAYER",
                    "GAME_RECORD_CITY", "GAME_RECORD_SOURCE_CONTEXT")):
                continue
            row = fields(line)
            if "turn" in row:
                result["lastTurn"] = max(int(row["turn"]), result["lastTurn"] or 0)
            if tag in ("GAME_RECORD_SAVE_LOADED", "GAME_RECORD_NEW_GAME_STARTED"):
                if result["header"]:
                    raise ValueError("Multiple sessions in one record are not supported: " + str(path))
                result["header"] = row
            elif tag == "GAME_RECORD_SOURCE_CONTEXT":
                result["source"] = {key: row[key] for key in ("version", "commit", "dirty") if key in row}
            elif tag == "GAME_RECORD_PLAYER":
                result["players"].setdefault(row["player"], {})["civilization"] = row.get("civ")
            elif tag == "GAME_RECORD_CITY":
                player = result["players"].setdefault(row["player"], {})
                city = {key: row.get(key) for key in ("city", "x", "y", "foundedTurn", "capital")}
                # <!-- custom: Earliest observed own-founded city is evidence, not proof of the original capital after a late load. (GPT-6.1-Sol) -->
                if row.get("originalOwner") == row["player"] and int(row.get("foundedTurn", "-1")) >= 0:
                    previous = player.get("earliestObservedCity")
                    if previous is None or int(city["foundedTurn"]) < int(previous["foundedTurn"]):
                        player["earliestObservedCity"] = city
            elif "unitId" in row:
                key = row["player"] + ":" + row["unitId"]
                unit = result["units"].setdefault(key, {"player": row["player"], "unitId": row["unitId"],
                    "observations": [], "scoutDecisions": 0, "reversals": [], "revisits": 0, "end": None})
                if tag.endswith("SCOUT_END"):
                    unit["end"] = {key: row.get(key) for key in ("turn", "reason", "action", "elapsed", "maxFirstCityTurns")}
                if tag.endswith("SCOUT_STEP"):
                    unit["scoutDecisions"] += 1
                    position = point(row)
                    observations = unit["observations"]
                    # <!-- custom: endTurnX/Y is a requested waypoint.
                    # Only later fromX/Y observations establish movement; otherwise an unexecuted A-B-A request would falsely look like a reversal.
                    # Return-to-found rows are not scouting reversals. (GPT-6.1-Sol) -->
                    if not observations or tuple(observations[-1]["position"]) != position:
                        if any(tuple(item["position"]) == position for item in observations):
                            unit["revisits"] += 1
                        observations.append({"position": position, "turn": int(row["turn"]), "line": line_number})
                        if len(observations) >= 3 and observations[-3]["position"] == position:
                            unit["reversals"].append(observations[-3:])
    return result


def as_int(row, key, default=0):
    try:
        return int(row.get(key, default))
    except (TypeError, ValueError):
        return default


def bounded_prospect(row):
    """Re-score a candidate with logged active floors; dormant floor eligibility is unknown."""
    information = as_int(row, "informationValue")
    found_value = as_int(row, "foundValue")
    best_known = as_int(row, "bestKnownFoundValue")
    quality_percent = 0
    if information > 0 and found_value > 0 and best_known > 0:
        quality_percent = min(100, (100 * found_value) // best_known)
    prospect_value = (information * quality_percent) // 100
    found_gain = as_int(row, "foundValueGain")
    base = information + prospect_value + found_gain

    # <!-- custom: Preserve recorded active approach floors.
    # A zero logged bonus does not identify whether its endpoint was eligible but already above the floor; lowering its base could activate that floor in a rebuilt game.
    # This rescore cannot reconstruct that missing eligibility and is calibration, not an exact runtime replay. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
    old_base = information + as_int(row, "knownProspectValue") + found_gain
    floor_value = base
    if as_int(row, "knownTargetApproachValue") > 0:
        floor_value = max(floor_value, best_known)
    if as_int(row, "promisingFogApproachValue") > 0:
        floor_value = max(floor_value, old_base + as_int(row, "promisingFogApproachValue"))
    return {
        "qualityPercent": quality_percent,
        "prospectValue": prospect_value,
        "total": floor_value,
    }


def rank_candidate(row, total):
    # <!-- custom: Mirror runtime tie-breaks so old-selection reproduction checks compare the actual ranking rather than total score alone. (ChatGPT-5.6-Sol) -->
    return (total, as_int(row, "explorerSeparation", -1),
            as_int(row, "endpointKnownSeeFromLevel", -2147483647),
            as_int(row, "stepDistance", -1))


def median(values):
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def finalize_counterfactual(summary):
    # <!-- custom: Missing oracle fields use -1, which must not count as a low-reveal result. (GPT-6.1-Sol) -->
    current = [value for value in summary.pop("_currentOracle", []) if value >= 0]
    bounded = [value for value in summary.pop("_boundedOracle", []) if value >= 0]
    summary["currentOracleSamples"] = len(current)
    summary["boundedOracleSamples"] = len(bounded)
    summary["currentSelectedZeroOracle"] = sum(value == 0 for value in current)
    summary["boundedSelectedZeroOracle"] = sum(value == 0 for value in bounded)
    summary["currentSelectedAtMostOneOracle"] = sum(value <= 1 for value in current)
    summary["boundedSelectedAtMostOneOracle"] = sum(value <= 1 for value in bounded)
    summary["currentAverageOracleReveals"] = (sum(current) / float(len(current)) if current else None)
    summary["boundedAverageOracleReveals"] = (sum(bounded) / float(len(bounded)) if bounded else None)
    summary["currentMedianOracleReveals"] = median(current)
    summary["boundedMedianOracleReveals"] = median(bounded)
    summary["currentOracleHistogram"] = {str(value): current.count(value) for value in sorted(set(current))}
    summary["boundedOracleHistogram"] = {str(value): bounded.count(value) for value in sorted(set(bounded))}


def bbai_summary(path):
    result = {"path": str(path), "header": {}, "selectedCandidates": 0, "zeroOracleRevealSelections": [],
              "boundedProspectCounterfactual": {"decisions": 0, "changedSelections": 0,
                  "loggedSelectionReproductionMismatches": 0, "examples": [],
                  "_currentOracle": [], "_boundedOracle": []}}
    active = {}
    pending = {}
    with path.open(encoding="utf-8-sig", errors="replace") as stream:
        for line_number, line in enumerate(stream, 1):
            tag = line.split(" ", 1)[0]
            if tag not in ("BBAI_SAVE_LOADED", "BBAI_NEW_GAME_STARTED", "FIRST_CITY_CANDIDATES",
                           "FIRST_CITY_SCOUT_STEP_CANDIDATE", "FIRST_CITY_SCOUT_MOVEMENT_SEARCH",
                           "FIRST_CITY_SCOUT_FOOD_POOR_SITE"):
                continue
            row = fields(line)
            if tag.startswith("BBAI_"):
                if result["header"]:
                    raise ValueError("Multiple sessions in one BBAI log: " + str(path))
                result["header"] = row
            elif tag == "FIRST_CITY_CANDIDATES":
                active[row["player"]] = []
                pending.pop(row["player"], None)
            elif tag == "FIRST_CITY_SCOUT_STEP_CANDIDATE":
                player = row["player"]
                batch = active.setdefault(player, [])
                if batch and batch[-1].get("from") != row.get("from"):
                    batch[:] = []
                batch.append(row)
            elif tag == "FIRST_CITY_SCOUT_MOVEMENT_SEARCH":
                player = row["player"]
                candidates = [item for item in active.get(player, []) if item.get("from") == row.get("from")]
                pending[player] = {"movement": row, "candidates": candidates}
                active[player] = []
            else:
                player = row["player"]
                decision = pending.pop(player, None)
                if not decision or decision["movement"].get("from") != row.get("from"):
                    continue
                candidates = [item for item in decision["candidates"] if as_int(item, "worthScoutDelay") == 1]
                selected = next((item for item in candidates if item.get("endTurn") == row.get("target")), None)
                if selected is None:
                    continue
                result["selectedCandidates"] += 1
                selected_oracle = as_int(selected, "actualLOSRevealPlots", -1)
                if selected_oracle == 0 and as_int(selected, "informationValue") > 0:
                    result["zeroOracleRevealSelections"].append({"player": row["player"], "from": row["from"],
                        "target": row["target"], "elapsed": row.get("elapsed"), "line": line_number,
                        "informationValue": selected["informationValue"], "oracleRevealPlots": 0})

                if not candidates:
                    continue
                counter = result["boundedProspectCounterfactual"]
                counter["decisions"] += 1
                logged_best = max(candidates, key=lambda item: rank_candidate(item, as_int(item, "total", -2147483647)))
                if logged_best.get("endTurn") != row.get("target"):
                    counter["loggedSelectionReproductionMismatches"] += 1
                rescored = [(item, bounded_prospect(item)) for item in candidates]
                bounded_best, bounded_data = max(rescored, key=lambda pair: rank_candidate(pair[0], pair[1]["total"]))
                bounded_oracle = as_int(bounded_best, "actualLOSRevealPlots", -1)
                counter["_currentOracle"].append(selected_oracle)
                counter["_boundedOracle"].append(bounded_oracle)
                if bounded_best.get("endTurn") != row.get("target"):
                    counter["changedSelections"] += 1
                    if len(counter["examples"]) < 40:
                        counter["examples"].append({
                            "player": player, "from": row.get("from"), "elapsed": row.get("elapsed"),
                            "currentTarget": row.get("target"), "boundedTarget": bounded_best.get("endTurn"),
                            "currentTotal": as_int(selected, "total"), "boundedTotal": bounded_data["total"],
                            "currentOracleReveals": selected_oracle, "boundedOracleReveals": bounded_oracle,
                            "boundedQualityPercent": bounded_data["qualityPercent"],
                            "boundedProspectValue": bounded_data["prospectValue"],
                        })
    finalize_counterfactual(result["boundedProspectCounterfactual"])
    return result


def expand(patterns):
    paths = set()
    for pattern in patterns:
        matches = glob.glob(pattern)
        if not matches:
            raise ValueError("No matching input: " + pattern)
        paths.update(Path(match).resolve() for match in matches)
    return sorted(paths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", nargs="+", help="SGR paths or quoted globs; one session per file")
    parser.add_argument("--bbai", action="append", default=[], help="Optional BBAI path/glob; repeatable")
    parser.add_argument("--output", type=Path, help="JSON report; default timestamped under LLM_Helpers/outputs")
    args = parser.parse_args()
    try:
        bbai = [bbai_summary(path) for path in expand(args.bbai)]
        reports = []
        for path in expand(args.records):
            report = read_record(path)
            identity = session(report["header"])
            matches = [item for item in bbai if identity is not None and session(item["header"]) == identity
                       and item["header"].get("activeCivilization") == report["header"].get("activeCivilization")
                       and item["header"].get("turn") == report["header"].get("turn")]
            report["bbaiCoverage"] = "MATCHED" if len(matches) == 1 else "ABSENT_OR_AMBIGUOUS"
            if len(matches) == 1:
                report["bbai"] = matches[0]
            reports.append(report)
    except (ValueError, OSError, KeyError) as error:
        parser.error(str(error))
    output = args.output or Path(__file__).resolve().parent / "outputs" / "first_city_scouting" / (
        "audit_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    output.parent.mkdir(parents=True, exist_ok=True)
    # <!-- custom: A wide BBAI glob can include unrelated runs; aggregate only uniquely paired sessions, once per file, so the headline matches the SGR batch requested. (GPT-6.1-Sol) -->
    paired = {report["bbai"]["path"]: report["bbai"] for report in reports if "bbai" in report}
    aggregate = {"sessions": len(paired), "excludedBBAISessions": len(bbai) - len(paired),
                 "decisions": 0, "changedSelections": 0,
                 "loggedSelectionReproductionMismatches": 0,
                 "_currentOracle": [], "_boundedOracle": []}
    for item in paired.values():
        counter = item["boundedProspectCounterfactual"]
        for key in ("decisions", "changedSelections", "loggedSelectionReproductionMismatches"):
            aggregate[key] += counter[key]
        for prefix in ("current", "bounded"):
            for value, count in counter[prefix + "OracleHistogram"].items():
                aggregate["_" + prefix + "Oracle"].extend([int(value)] * count)
    finalize_counterfactual(aggregate)
    output.write_text(json.dumps({"interpretation": "Review flags and counterfactual calibration, not automatic defect verdicts. Oracle counts are pre-move estimates and never inputs to the bounded-prospect score. The counterfactual preserves logged active approach floors; dormant floor eligibility is unavailable, so it need not reproduce the rebuilt runtime choice. It does not simulate future map states after a changed move.",
                                 "scope": "Initial-capital Settlers only; scout origins omit unlogged movement and the final founding approach. No trace means no coverage verdict. Earliest observed city after a late load need not be the original capital.",
                                 "bbaiCounterfactualAggregate": aggregate, "bbaiSessions": bbai, "runs": reports}, indent=2) + "\n", encoding="utf-8")
    print("Bounded-prospect BBAI counterfactual: decisions={decisions}; changed={changedSelections}; current zero-oracle={currentSelectedZeroOracle}; bounded zero-oracle={boundedSelectedZeroOracle}; current <=1 oracle={currentSelectedAtMostOneOracle}; bounded <=1 oracle={boundedSelectedAtMostOneOracle}; current avg oracle={currentAverageOracleReveals}; bounded avg oracle={boundedAverageOracleReveals}; current median oracle={currentMedianOracleReveals}; bounded median oracle={boundedMedianOracleReveals}; paired sessions={sessions}; excluded BBAI sessions={excludedBBAISessions}; reproduction mismatches={loggedSelectionReproductionMismatches}".format(**aggregate))
    for report in reports:
        print(Path(report["record"]).name + " | " + report["bbaiCoverage"])
        if not report["units"]:
            print("  No traced first-city scouting units; efficiency coverage is unknown.")
        for unit in report["units"].values():
            player = report["players"].get(unit["player"], {})
            city = player.get("earliestObservedCity") or {}
            route = " -> ".join(",".join(map(str, item["position"])) for item in unit["observations"])
            print("  player={player} unit={unitId} decisions={scoutDecisions} reversals={reversals} revisits={revisits} city={city} founded={founded} observedScoutOrigins={route}".format(
                **{**unit, "reversals": len(unit["reversals"])}, city=city.get("city", "UNKNOWN"), founded=city.get("foundedTurn", "UNKNOWN"), route=route))
        if "bbai" in report:
            print("  selected candidates={}; positive-information/zero-oracle-reveal={}".format(
                report["bbai"]["selectedCandidates"], len(report["bbai"]["zeroOracleRevealSelections"])))
    print("Report: " + str(output))


if __name__ == "__main__":
    main()

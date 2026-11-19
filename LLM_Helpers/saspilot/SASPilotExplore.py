# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Move several scouting units a turn at a time, each looping around its own center with SASPilotScout's choices, then end the turn, stopping on anything an agent should look at.
# Grown from a scratch driver over the playthroughs of 2026-11-14 (a Pangaea start played three times, then a Continents game), where each rule below came from a mistake the user pointed out; kept in the repo so the next agent starts from it rather than rewriting it. (Claude code Opus 5.5) -->

import argparse
import json
import os
import sys
import time

# <!-- custom: SASPilotClient, as pilot, for the requests, logged with each move's reason as any SASPilotClient.py command is; SASPilotScout for the choices. (Claude code Opus 5.5) -->
import SASPilotClient as pilot
from SASPilotClient import PilotError, pick_pid, request
import SASPilotScout


def ask(pid, command, args=None, note=None):
    # <!-- custom: The reason goes into the command log beside the order, as SASPilotClient.py's --note does, so the SASPilotConsole shows why each step was taken. (Claude code Opus 5.5) -->
    if note:
        pilot._log_context["note"] = note
    reply = request(pid, command, args or {})
    if not reply["ok"]:
        raise PilotError(reply["error"].strip().splitlines()[-1])
    return reply["result"]


_enemies = {}


def hostiles(pid, unit):
    # <!-- custom: Barbarians (animals included) and players we are at war with, by identity: the first version took every owner from slot 40 up as hostile, but SAS has 48 civilization slots, so a peaceful player 40 stopped the run and a civilization at war in slot 3 was ignored (Codex's review, round 38). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
    if not _enemies:
        players = ask(pid, "players")
        _enemies["ids"] = set(p["player"] for p in players if p.get("civ") == "CIVILIZATION_BARBARIAN" and p.get("player") is not None)
        mine = [p for p in players if p.get("human")]
        if mine:
            _enemies["ids"].update(mine[0].get("atWarWith") or [])
    plots = ask(pid, "plots", {"unit": unit, "radius": 2, "fog": True})
    return [(plot["x"], plot["y"], other["type"]) for plot in plots for other in plot.get("units", []) if other["owner"] in _enemies["ids"]]


def step(pid, spec, depth=0):
    """Move one unit as far as it safely gets this turn; return a reason to stop the run, or None."""
    unit, center, band, flags = spec
    info = ask(pid, "unit", {"unit": unit, "fog": True})
    if info["movesLeft"] <= 0:
        return None
    threats = hostiles(pid, unit)
    # <!-- custom: An animal or barbarian next to the unit is the agent's call, not the helper's: run 3 of the Pangaea trial lost its Scout beside a visible Bear. (Claude code Opus 5.5) -->
    if any(max(abs(t[0] - info["x"]), abs(t[1] - info["y"])) <= 1 for t in threats):
        return "hostile next to unit %d at %d,%d: %s" % (unit, info["x"], info["y"], threats)
    # <!-- custom: A goody hut in reach comes first unless the unit has 'nohut', which keeps a unit in its own sector while another takes the hut (the Warrior turned back across the map for one, Pangaea run 3). (Claude code Opus 5.5) -->
    if "nohut" not in flags:
        grid = ask(pid, "grid", {"unit": unit, "radius": 6, "network": False, "fog": True})
        for tile in grid["tiles"]:
            if tile.get("improvement") == "IMPROVEMENT_GOODY_HUT" and not any(max(abs(t[0] - tile["x"]), abs(t[1] - tile["y"])) <= 1 for t in threats):
                path = ask(pid, "path", {"unit": unit, "x": tile["x"], "y": tile["y"], "fog": True})
                if path["found"]:
                    first = min(s["turn"] for s in path["steps"])
                    stop = [s for s in path["steps"] if s["turn"] == first][-1]
                    return move(pid, spec, stop["x"], stop["y"], "goody hut at %d,%d, %d turns" % (tile["x"], tile["y"], path["turns"]), depth)
    try:
        found = SASPilotScout.compare(pid, unit, 8, 3, center, band, "ccw" in flags)
    except PilotError as error:
        return "unit %d: %s" % (unit, error)
    if not found["choices"]:
        return "no safe loop choice for unit %d around %d,%d" % (unit, center[0], center[1])
    choice = found["choices"][0]
    stop = choice["stopThisTurn"]
    # <!-- custom: One plot at a time, then look again, the user's advice after the Bear: each step can reveal an animal that changes the next choice. (Claude code Opus 5.5) -->
    path = ask(pid, "path", {"unit": unit, "x": stop["x"], "y": stop["y"], "fog": True})
    steps = [s for s in path.get("steps", []) if (s["x"], s["y"]) != (info["x"], info["y"])]
    if not steps:
        return None
    nxt = steps[0]
    why = "loop around %d,%d toward %d,%d (reveals %d, %d turns); this turn's stop %d,%d, defence %s; one step to %d,%d, then look again" % (center[0], center[1], choice["x"], choice["y"], choice["unknownOutsideEarlierChoices"], choice["turns"], stop["x"], stop["y"], stop["defense"], nxt["x"], nxt["y"])
    return move(pid, spec, nxt["x"], nxt["y"], why, depth)


def move(pid, spec, x, y, why, depth):
    unit = spec[0]
    try:
        # <!-- custom: A MISSION_MOVE_TO that replaces the group's queue rather than 'move': after a step into a forest the group still held its move order, and 'move' refused the next step ("cannot start MISSION_MOVE_TO ... whose current mission is MISSION_MOVE_TO"), so the Scout stood still two turns (Continents game, turn 15). (Claude code Opus 5.5) -->
        result = None
        # <!-- custom: Retried a few times a short moment apart: right after a step the group is still busy while the game plays the move, and canStartMission refuses until it is done (cmd_mission's own comment records the same for 'MISSION_FOUND append=1'); the Scout lost turns 15 to 17 to it. (Claude code Opus 5.5) -->
        for attempt in range(6):
            try:
                result = ask(pid, "mission", {"unit": unit, "mission": "MISSION_MOVE_TO", "data1": x, "data2": y}, why)
                break
            except PilotError as error:
                if "current mission" not in str(error) or attempt == 5:
                    raise
                time.sleep(0.4)
    except PilotError as error:
        # <!-- custom: The game can refuse a step the path planned, as "no path" through plots the order cannot use, or a hill that needs more moves than are left; the unit stays this turn rather than the run stopping. (Claude code Opus 5.5) -->
        print("  %d stays: %s" % (unit, error))
        return None
    print("  %d: %s -> %s,%s" % (unit, why, result.get("x"), result.get("y")))
    if result.get("movesLeft", 0) > 0 and depth < 4:
        return step(pid, spec, depth + 1)
    return None


def digest(end, ids, known):
    """What in an endturn reply should stop the run: new messages, notices and reminders, idle units and cities."""
    flags = {}
    messages = [m["text"] for m in end.get("messages", []) if "borders" not in m.get("text", "")]
    if messages:
        flags["messages"] = messages
    if end.get("notices"):
        flags["notices"] = end["notices"]
    # <!-- custom: A reminder stops the run only the first time it appears in it, and not when a unit for it is on its way or in production: the Clam reminder came every turn while its Work Boat was being built (Pangaea run 1). (Claude code Opus 5.5) -->
    new = [r["text"] for r in end.get("reminders", []) if not (r.get("inProduction") or r.get("unitOnTheWay")) and r["text"].split(" (")[0] not in known]
    known.update(r["text"].split(" (")[0] for r in end.get("reminders", []))
    if new:
        flags["reminders"] = new
    todo = end.get("todo", {})
    idle = [(u["type"], u["id"], u["x"], u["y"]) for u in todo.get("idleUnits", []) if u["id"] not in ids]
    if idle:
        flags["idleUnits"] = idle
    for key in ("idleCities", "heldPopups"):
        if todo.get(key):
            flags[key] = todo[key]
    if todo.get("needsResearch"):
        flags["needsResearch"] = True
    return flags


def parse_spec(text):
    parts = text.split(":")
    if len(parts) < 3:
        raise argparse.ArgumentTypeError("UNIT:X,Y:MIN,MAX[:ccw,nohut], such as 24578:56,27:3,6:ccw")
    flags = len(parts) > 3 and parts[3].split(",") or []
    return (int(parts[0]), tuple(int(v) for v in parts[1].split(",")), tuple(int(v) for v in parts[2].split(",")), flags)


def main():
    parser = argparse.ArgumentParser(description="Scout with several units for some turns, each looping around its own center, ending each turn; stops on anything worth an agent's look.")
    parser.add_argument("--pid", type=int, help="Civ4 client PID")
    parser.add_argument("--turns", type=int, default=5, help="turns to play at most")
    parser.add_argument("units", nargs="+", type=parse_spec, help="UNIT:X,Y:MIN,MAX[:ccw,nohut] per unit: its center, the band of distances from it, and flags (ccw loops the other way, so two units circle apart; nohut leaves huts to other units)")
    args = parser.parse_args()
    pilot._log_context["operator"] = os.environ.get("SAS_PILOT_OPERATOR") or None
    pilot._log_context["session"] = os.environ.get("SAS_PILOT_OPERATOR_SESSION") or os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CODEX_THREAD_ID") or None
    try:
        pid = pick_pid(args.pid)
        ids = [spec[0] for spec in args.units]
        known = set(r["text"].split(" (")[0] for r in ask(pid, "reminders").get("reminders", []))
        for _ in range(args.turns):
            for spec in args.units:
                reason = step(pid, spec)
                if reason:
                    print(json.dumps({"stop": reason}))
                    return 0
            # <!-- custom: Codex's review (round 38, P1): the immediate 'endturn' reply holds only the turn ended and what it skipped, so the new turn's messages and reminders never reached the stop check.
            # Check 'todo' before ending, then wait for the new turn and read the 'turn' digest, as SASPilotClient.py endturn does. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
            before = ask(pid, "todo")
            waiting = digest({"todo": before}, ids, known)
            if waiting:
                print(json.dumps({"beforeEndTurn": waiting}))
                return 0
            end = ask(pid, "endturn", {}, "SASPilotExplore: scouts moved, turn ended")
            pilot.wait_for_turn(pid, 600.0, after_turn=end["gameTurn"])
            turn = ask(pid, "turn")
            flags = digest(turn, ids, known)
            print(json.dumps({"turnEnded": end.get("gameTurn"), "flags": flags}))
            if flags:
                return 0
    except (OSError, PilotError) as error:
        print("SASPilotExplore: %s" % error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

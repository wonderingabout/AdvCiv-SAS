# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

"""Compare fog-frontier destinations for one land scout using SASPilot."""

import argparse
import json
import math
import sys

from SASPilotClient import PilotError, pick_pid, request


def neighborhood(center, radius, grid):
    x, y = center
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            nx, ny = x + dx, y + dy
            if grid["wrapX"]:
                nx %= grid["width"]
            if grid["wrapY"]:
                ny %= grid["height"]
            if 0 <= nx < grid["width"] and 0 <= ny < grid["height"]:
                yield nx, ny


def orbit_advance(center, point, origin):
    # <!-- custom: Degrees clockwise from origin to point as seen from center; Civ4's y grows northward, so clockwise lowers the math angle. (Claude code Opus 5.5) -->
    before = math.degrees(math.atan2(origin[1] - center[1], origin[0] - center[0]))
    after = math.degrees(math.atan2(point[1] - center[1], point[0] - center[0]))
    return (before - after) % 360


def compare(pid, unit, radius, limit, around=None, band=(3, 5), counterclockwise=False, min_health=80):
    def ask(command, args):
        reply = request(pid, command, args)
        if not reply["ok"]:
            raise PilotError(reply["error"])
        return reply["result"]

    role = ask("role", {})
    if role["role"] != "play" or not role["locked"]:
        raise PilotError("start the client with --role play for a fog-on scouting trial")

    # <!-- custom: Batch the reads and path probes separately so the desktop tool can shortlist candidates without sending the full grid to the agent. (GPT-6.1-Sol) -->
    snapshot = ask("batch", {"commands": [
        {"cmd": "grid", "args": {"network": False, "fog": True}},
        {"cmd": "unit", "args": {"unit": unit, "fog": True}},
        {"cmd": "plots", "args": {"unit": unit, "radius": radius + 2, "fog": True}},
    ]})
    grid, scout, plots = snapshot
    if scout["domain"] != "DOMAIN_LAND" or scout["transport"] is not None:
        raise PilotError("select a land unit off its transport")
    origin = scout["x"], scout["y"]
    # <!-- custom: A wounded scout heals before it scouts on: in the scouting trial (run 3, turn 33) the Scout went back out at 64% health after a Panther and a Bear killed it from the fog, 99% odds for the Bear, though Scouts get +200% against animals. (Claude code Opus 5.5) -->
    # <!-- custom: The bar is --min-health (default 80): refusing any damage at all held back an Archer at 83% beside the capital after it beat a Wolf (Continents game, turn 10). (Claude code Opus 5.5) -->
    if 100 - scout["damage"] < min_health:
        raise PilotError("unit %d is at %d%% health, under %d%%; heal it before scouting on" % (unit, 100 - scout["damage"], min_health))

    # <!-- custom: Use the full reveal mask so the search boundary cannot turn known tiles into apparent fog. (GPT-6.1-Sol) -->
    known = {(plot["x"], plot["y"]) for plot in grid["tiles"]}
    search = set(neighborhood(origin, radius, grid))
    visible_foreign = {(plot["x"], plot["y"], other["id"], other["owner"]): other["type"]
        for plot in plots for other in plot["units"] if other["owner"] != grid["player"]}
    candidates = []
    for tile in grid["tiles"]:
        point = tile["x"], tile["y"]
        if point not in search or point == origin or tile["water"] or tile["peak"]:
            continue
        # <!-- custom: --around keeps a loop around a city, the user's advice for the opening (2026-11-14): circle the capital first to find city sites, huts and the nearest rivals before heading far.
        # Candidates outside the distance band from the center are left out. (Claude code Opus 5.5) -->
        if around is not None and not band[0] <= max(abs(point[0] - around[0]), abs(point[1] - around[1])) <= band[1]:
            continue
        # <!-- custom: Match scout's one/two-plot square as a coverage proxy.
        # Actual sight depends on terrain occlusion and the unit's visibility. (GPT-6.1-Sol, Claude Code Opus 5.5) -->
        reveal = set(neighborhood(point, 2 if tile["hill"] else 1, grid)) - known
        if reveal:
            candidates.append((point, reveal, tile))

    paths = ask("batch", {"commands": [
        {"cmd": "path", "args": {"unit": unit, "x": point[0], "y": point[1], "fog": True}}
        for point, _, _ in candidates
    ]}) if candidates else []

    options = []
    hills = {(plot["x"], plot["y"]) for plot in grid["tiles"] if plot["hill"]}
    defense = {(plot["x"], plot["y"]): plot.get("defense") for plot in grid["tiles"]}
    for (point, reveal, tile), path in zip(candidates, paths):
        if not path["found"] or not all((step["x"], step["y"]) in known for step in path["steps"]):
            continue
        # <!-- custom: Count what every step of the route reveals, not only the destination: the user's advice (2026-11-14) to favour diagonals and high plots, as a diagonal step uncovers five new plots where a straight one uncovers three, and a hill sees two plots out.
        # Counting the route ranks those paths higher without a rule of its own. (Claude code Opus 5.5) -->
        for step in path["steps"]:
            reveal = reveal | (set(neighborhood((step["x"], step["y"]), 2 if (step["x"], step["y"]) in hills else 1, grid)) - known)
        nearby = set(neighborhood(point, 2, grid))
        sightings = [{"x": x, "y": y, "type": kind, "owner": owner}
            for (x, y, _, owner), kind in sorted(visible_foreign.items()) if (x, y) in nearby]
        if path["turns"] < 1:
            continue
        # <!-- custom: Where to stop this turn on the way: the best-defended plot among this turn's steps, the farthest on a tie.
        # The user's advice (2026-11-14): a scout ends its turn on a hill or forest, to defend rather than attack, after a multi-turn order walked the Warrior next to a Lion at turn 13 of the scouting trial; it won at 95% yet was left at 10 health.
        # Moving only to this stop re-checks the danger each turn. (Claude code Opus 5.5) -->
        # <!-- custom: The unit's own plot is never this turn's stop: the path's steps can include it, and with the best defence it was chosen, so the Scout stood still at 17,22 (scouting trial run 3, turn 22). (Claude code Opus 5.5) -->
        moves = [step for step in path["steps"] if (step["x"], step["y"]) != origin]
        if not moves:
            continue
        first = min(step["turn"] for step in moves)
        reach = [step for step in moves if step["turn"] == first]
        # <!-- custom: Only a stop in sight, whose defence and neighbours we know: the Scout lost at turn 33 had stopped on a plot out of sight (defense None), and the Bear came from the fog. (Claude code Opus 5.5) -->
        reach = [step for step in reach if defense.get((step["x"], step["y"])) is not None]
        # <!-- custom: Nor a stop within two plots of a foreign unit we see: only the destination was checked, so at turn 33 the Scout stopped on the way beside a visible Bear and died, though its two moves could have kept it away (the user caught it). (Claude code Opus 5.5) -->
        reach = [step for step in reach if not any(max(abs(step["x"] - fx), abs(step["y"] - fy)) <= 2 for (fx, fy, _, _) in visible_foreign)]
        if not reach:
            continue
        best = max(range(len(reach)), key=lambda i: (defense.get((reach[i]["x"], reach[i]["y"])) or 0, i))
        stop = {"x": reach[best]["x"], "y": reach[best]["y"], "defense": defense.get((reach[best]["x"], reach[best]["y"]))}
        row = {"x": point[0], "y": point[1], "turns": path["turns"],
            "unknownNearby": len(reveal), "hill": tile["hill"], "visibleForeignUnitsWithin2": sightings, "stopThisTurn": stop}
        if around is not None:
            # <!-- custom: --ccw turns the loop the other way, so two scouts can circle in opposite directions without retracing each other, the user's advice (2026-11-14), and a unit on the wrong side of its center need not turn back. (Claude code Opus 5.5) -->
            advance = orbit_advance(around, point, origin)
            row["clockwiseDegrees"] = int(round(counterclockwise and (360 - advance) % 360 or advance))
        options.append((row, reveal))

    reachable = len(options)

    def nearness(row):
        # <!-- custom: Around a center, a pocket near the city outranks a bigger reveal farther out: in the Continents game (turns 9 to 14) dark plots 3 to 5 from Karakorum, at 58,24, 60,25 and 51,26, stayed unseen while the loop chased reveals farther away, and the user pointed at each; the closest sites are the first a Settler can use. (Claude code Opus 5.5) -->
        if around is None:
            return 1.0
        return 1.0 + max(abs(row["x"] - around[0]), abs(row["y"] - around[1])) / 3.0
    choices, covered = [], set()
    while options and len(choices) < limit:
        # <!-- custom: Around a center, a step that goes on clockwise by 1 to 135 degrees comes first, so the loop does not turn back on itself; the reveal per turn ranks within each group. (Claude code Opus 5.5) -->
        # <!-- custom: The defence of this turn's stop scales the reveal per turn, so of two similar routes the one ending on a hill or forest wins. (Claude code Opus 5.5) -->
        options.sort(key=lambda option: (bool(option[0]["visibleForeignUnitsWithin2"]),
            around is not None and not 0 < option[0]["clockwiseDegrees"] <= 135,
            -len(option[1] - covered) / option[0]["turns"] * (100 + max(option[0]["stopThisTurn"]["defense"] or 0, 0)) / 100 / nearness(option[0]),
            option[0]["turns"], option[0]["x"], option[0]["y"]))
        row, reveal = options.pop(0)
        # <!-- custom: A destination with an animal or barbarian in sight within two plots is left out rather than listed last: the user's rule, as killing an animal gains a little experience while losing the scout loses our only scout. (Claude code Opus 5.5) -->
        if row["visibleForeignUnitsWithin2"]:
            continue
        row["unknownOutsideEarlierChoices"] = len(reveal - covered)
        if not row["unknownOutsideEarlierChoices"]:
            continue
        covered.update(reveal)
        choices.append(row)
    return {"turn": grid["turn"], "unit": scout["type"], "origin": origin, "around": around,
        "candidatesChecked": len(candidates), "reachableThroughKnownTiles": reachable, "choices": choices}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", type=int, help="Civ4 client PID")
    parser.add_argument("--unit", type=int, required=True, help="land scout or Warrior ID from 'SASPilotClient.py units'")
    parser.add_argument("--radius", type=int, default=5, choices=range(1, 9))
    parser.add_argument("--limit", type=int, default=3, choices=range(1, 11))
    parser.add_argument("--around", help="X,Y of a city to loop around clockwise, such as the capital in the opening")
    parser.add_argument("--min-health", type=int, default=80, help="refuse a unit under this health percent; it heals first")
    parser.add_argument("--ccw", action="store_true", help="with --around: loop counter-clockwise; clockwiseDegrees then counts that way")
    parser.add_argument("--band", default="3,5", help="with --around: nearest and farthest distance in plots from the center, default 3,5")
    args = parser.parse_args()
    try:
        around = args.around and tuple(int(value) for value in args.around.split(",")) or None
        band = tuple(int(value) for value in args.band.split(","))
        print(json.dumps(compare(pick_pid(args.pid), args.unit, args.radius, args.limit, around, band, args.ccw, args.min_health), indent=2))
    except (OSError, PilotError) as error:
        print(f"SASPilotScout: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

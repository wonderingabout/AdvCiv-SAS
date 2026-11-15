# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Compare candidate city sites from the fogged grid, so an agent can weigh sites before its Settler is built, when the window's recommended sites ('sites') show only once a Settler is selected.
# The score is a heuristic of ours, advice rather than fact, and each part came from the user's review of the 2026-11-14 playthroughs; the facts behind it are printed beside it, so the agent can judge for itself. (Claude code Opus 5.5) -->

import argparse
import json
import sys

# <!-- custom: SASPilotClient, as pilot, for the grid request, logged as any SASPilotClient.py command is. (Claude code Opus 5.5) -->
import SASPilotClient as pilot
from SASPilotClient import PilotError, pick_pid, request

FOOD = {"BONUS_CLAM", "BONUS_FISH", "BONUS_CRAB", "BONUS_BANANA", "BONUS_PIG", "BONUS_COW", "BONUS_SHEEP", "BONUS_WHEAT", "BONUS_RICE", "BONUS_CORN", "BONUS_DEER", "BONUS_CAMEL"}


def fat_cross(center):
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if not (abs(dx) == 2 and abs(dy) == 2):
                yield (center[0] + dx, center[1] + dy)


def distance(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def compare(pid, cities, near, far, limit):
    reply = request(pid, "grid", {"network": False, "fog": True})
    if not reply["ok"]:
        raise PilotError(reply["error"])
    grid = reply["result"]
    tiles = {(t["x"], t["y"]): t for t in grid["tiles"]}
    player = grid["player"]
    if not cities:
        cities = [(t["x"], t["y"]) for t in grid["tiles"] if t.get("city") and t["owner"] == player]
    taken = set()
    for city in cities:
        taken |= set(fat_cross(city))
    # <!-- custom: Rival borders and cities, for how contested a site is: the user's idea in the Continents game (2026-11-14), as valuable land near a rival goes first while safe land can wait. (Claude code Opus 5.5) -->
    rival_plots = [(t["x"], t["y"]) for t in grid["tiles"] if t["owner"] not in (-1, player)]
    rival_cities = [(t["x"], t["y"]) for t in grid["tiles"] if t.get("city") and t["owner"] not in (-1, player)]

    def fresh(point):
        for q in [point] + [(point[0] + dx, point[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]:
            t = tiles.get(q)
            if t and (t.get("southRiver") or t.get("eastRiver")):
                return True
        return False

    rows = []
    for point, tile in tiles.items():
        if tile["water"] or tile["peak"] or tile["owner"] not in (-1, player):
            continue
        dist = min([distance(point, c) for c in cities] or [0])
        if not near <= dist <= far:
            continue
        food, other, unknown, grass, overlap, water = [], [], 0, 0, 0, 0
        for q in fat_cross(point):
            overlap += q in taken
            t = tiles.get(q)
            if t is None:
                unknown += 1
                continue
            if t["water"]:
                water += 1
            elif t["terrain"] == "TERRAIN_GRASS":
                grass += 1
            bonus = t.get("bonus")
            if bonus in FOOD:
                food.append(bonus[6:])
            elif bonus:
                other.append(bonus[6:])
        coastal = any((tiles.get((point[0] + dx, point[1] + dy)) or {}).get("water") for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        # <!-- custom: The parts of the score, each from the user's review: food resources count most, then other resources; fresh water; the coast, which grows a city further with a Harbor than flat plains can, whatever its water hides; a hill city tile, for defence and a hammer for good; grassland plots for the land's own food, as a site of plains with three resources had ranked first (Thessalonica, Pangaea run 3); overlap with our cities costs.
        # Unknown plots are counted but not taken off: taking them off made a fully seen site beat 10,19 and 11,17, whose radius still had fog, when fog around a promising site calls for a scout before the Settler commits. (Claude code Opus 5.5) -->
        score = 3 * len(food) + len(other) + 2 * fresh(point) + 2 * coastal + tile["hill"] + 0.3 * grass - 0.5 * overlap
        rows.append({"x": point[0], "y": point[1], "score": round(score, 1), "food": food, "other": other, "fresh": fresh(point), "coastal": coastal, "hill": tile["hill"], "terrain": tile["terrain"], "feature": tile.get("feature"), "grass": grass, "water": water, "overlap": overlap, "unknown": unknown, "fromOurCity": dist,
            "rivalBorder": min([distance(point, q) for q in rival_plots] or [None]), "rivalCity": min([distance(point, q) for q in rival_cities] or [None])})
    rows.sort(key=lambda row: -row["score"])
    # <!-- custom: The plot to stand on matters as well as the radius: the user's rule is to settle on the plot worst to work and best to stand on, such as a plains hill, and to keep a grass hill as a worked plot; compare neighbouring rows for that rather than taking the top one blindly. (Claude code Opus 5.5) -->
    return {"cities": cities, "sites": rows[:limit]}


def main():
    parser = argparse.ArgumentParser(description="Compare candidate city sites from the fogged grid: resources, fresh water, coast, hill, grassland, overlap, unknown plots and distance to rivals, with a heuristic score.")
    parser.add_argument("--pid", type=int, help="Civ4 client PID")
    parser.add_argument("--cities", help="X,Y;X,Y of our cities to measure from; default every city of ours in sight")
    parser.add_argument("--near", type=int, default=3, help="nearest distance from our cities, default 3")
    parser.add_argument("--far", type=int, default=6, help="farthest distance from our cities, default 6")
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()
    cities = args.cities and [tuple(int(v) for v in c.split(",")) for c in args.cities.split(";")] or []
    try:
        print(json.dumps(compare(pick_pid(args.pid), cities, args.near, args.far, args.limit), indent=1))
    except (OSError, PilotError) as error:
        print("SASPilotSites: %s" % error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

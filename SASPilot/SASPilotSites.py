# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Compare candidate city sites from the fogged grid, so an agent can weigh sites before its Settler is built, when the window's recommended sites ('sites') show only once a Settler is selected.
# The score is a heuristic of ours, advice rather than fact, and each part came from the user's review of the 2026-11-14 playthroughs; the facts behind it are printed beside it, so the agent can judge for itself. (Claude code Opus 5.5) -->

import argparse
import json
import sys

# <!-- custom: SASPilotClient, as saspilot, for the grid request, logged as any SASPilotClient.py command is. (Claude code Opus 5.5) -->
import SASPilotClient as saspilot
from SASPilotClient import PilotError, pick_pid, request

FOOD = {"BONUS_CLAM", "BONUS_FISH", "BONUS_CRAB", "BONUS_BANANA", "BONUS_PIG", "BONUS_COW", "BONUS_SHEEP", "BONUS_WHEAT", "BONUS_RICE", "BONUS_CORN", "BONUS_DEER", "BONUS_CAMEL"}


def fat_cross(center):
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if not (abs(dx) == 2 and abs(dy) == 2):
                yield (center[0] + dx, center[1] + dy)


def distance(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def ask(pid, command, args):
    reply = request(pid, command, args)
    if not reply["ok"]:
        raise PilotError(reply["error"])
    return reply["result"]


def direction(src, dst):
    dx, dy = dst[0] - src[0], dst[1] - src[1]
    # <!-- custom: Civ4's y grows northward. (Claude code Opus 5.5) -->
    return ("north" if dy > 0 else "south" if dy < 0 else "") + ("east" if dx > 0 else "west" if dx < 0 else "") or "here"


def compare(pid, cities, near, far, limit):
    grid = ask(pid, "grid", {"network": False, "fog": True})
    player = grid["player"]
    if not cities:
        cities = [(t["x"], t["y"]) for t in grid["tiles"] if t.get("city") and t["owner"] == player]
    # <!-- custom: Plots come from 'plots', not 'grid': grid gives river edges only for plots in sight, so every site seen earlier but out of sight read "no fresh water", and the river and flood plains around 21,15 went unnoticed in the Continents replay (2026-11-19) until the user named the site.
    # 'plots' gives the game's own freshWater and river for every revealed plot. (Claude code Opus 5.5) -->
    tiles = {}
    for city in cities or [(grid["box"][0], grid["box"][1])]:
        for t in ask(pid, "plots", {"x": city[0], "y": city[1], "radius": far + 2, "fog": True}):
            if t.get("revealed"):
                tiles[(t["x"], t["y"])] = t
    taken = set()
    for city in cities:
        taken |= set(fat_cross(city))
    owners = dict((p["id"] if "id" in p else p["player"], p.get("civ") or p.get("name")) for p in ask(pid, "players", {}))
    # <!-- custom: Rival borders and cities, for how contested a site is: the user's idea in the Continents game (2026-11-14), as valuable land near a rival goes first while safe land can wait.
    # Named with their owner and direction since the Continents replay (2026-11-19): the user read Persia's border at 17,19 and the northern desert as leaving north-east the only lane to expand into, which a bare distance did not show. (Claude code Opus 5.5) -->
    rival_plots = [(t["x"], t["y"], t["owner"]) for t in grid["tiles"] if t["owner"] not in (-1, player)]
    rival_cities = [(t["x"], t["y"]) for t in grid["tiles"] if t.get("city") and t["owner"] not in (-1, player)]
    # <!-- custom: The AI's found value beside our facts: the AI rated 20,12 highest and our own score did not list it, while neither listed the user's 21,15, so the two views are shown together rather than one trusted (Continents replay, 2026-11-19). (Claude code Opus 5.5) -->
    ai_values = dict(((s["x"], s["y"]), s["value"]) for s in ask(pid, "plansites", {"legal": True, "spread": 0, "limit": 2000})["sites"])
    # <!-- custom: The user's own dot-map marks are always rated, whatever their distance: 21,15 lay 7 plots from Dublin, past the default band, and was the best site. (Claude code Opus 5.5) -->
    marked = set((dot["x"], dot["y"]) for dot in grid.get("dotMap") or [])

    rows = []
    for point, tile in tiles.items():
        water_tile = tile["plotType"] == "PLOT_OCEAN"
        if water_tile or tile["plotType"] == "PLOT_PEAK" or tile["owner"] not in (-1, player):
            continue
        dist = min([distance(point, c) for c in cities] or [0])
        if not (near <= dist <= far or point in marked):
            continue
        food, other, unknown, grass, overlap, water, desert, flood, oasis, river = [], [], 0, 0, 0, 0, 0, 0, 0, 0
        rival_owned, at_risk = 0, 0
        for q in fat_cross(point):
            overlap += q in taken
            t = tiles.get(q)
            if t is None:
                unknown += 1
                continue
            # <!-- custom: Plots a rival already owns are not usable, so they add nothing to the score, and unowned plots next to a rival's border are counted as at risk: Cork at 21,15, founded at turn 53 of the Continents replay (2026-11-19), had 10 of its radius plots in Persia's borders, and the user suggested counting only the plots a city can expect to work. (Claude code Opus 5.5) -->
            if t["owner"] not in (-1, player):
                rival_owned += 1
                continue
            if t["owner"] == -1 and any(distance(q, r[:2]) <= 1 for r in rival_plots):
                at_risk += 1
            if t["plotType"] == "PLOT_OCEAN":
                water += 1
            elif t["terrain"] == "TERRAIN_GRASS":
                grass += 1
            elif t["terrain"] == "TERRAIN_DESERT" and t.get("feature") not in ("FEATURE_FLOOD_PLAINS", "FEATURE_OASIS"):
                desert += 1
            flood += t.get("feature") == "FEATURE_FLOOD_PLAINS"
            oasis += t.get("feature") == "FEATURE_OASIS"
            river += bool(t.get("river"))
            bonus = t.get("bonus")
            if bonus in FOOD:
                food.append(bonus[6:])
            elif bonus:
                other.append(bonus[6:])
        coastal = any((tiles.get((point[0] + dx, point[1] + dy)) or {}).get("plotType") == "PLOT_OCEAN" for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        hill = tile["plotType"] == "PLOT_HILLS"
        fresh = bool(tile.get("freshWater"))
        # <!-- custom: The parts of the score, each from the user's review: food resources count most, then other resources; fresh water; the coast, which grows a city further with a Harbor than flat plains can, whatever its water hides; a hill city tile, for defence and a hammer for good; grassland plots for the land's own food, as a site of plains with three resources had ranked first (Thessalonica, Pangaea run 3); overlap with our cities costs.
        # Unknown plots are counted but not taken off: taking them off made a fully seen site beat 10,19 and 11,17, whose radius still had fog, when fog around a promising site calls for a scout before the Settler commits. (Claude code Opus 5.5) -->
        # <!-- custom: Flood plains and oases count as food, river plots as commerce, and bare desert costs, from the user's reading of 21,15 (Continents replay, 2026-11-19): a plains-hill centre with fresh water, two flood plains, two oases, the Gold and a Camel. (Claude code Opus 5.5) -->
        score = 3 * len(food) + len(other) + 2 * fresh + 2 * coastal + hill + 0.3 * grass - 0.5 * overlap + 1.5 * flood + oasis + 0.3 * river - 0.3 * desert - 0.5 * at_risk
        near_rival = min([(distance(point, q[:2]), q) for q in rival_plots] or [(None, None)])
        rows.append({"x": point[0], "y": point[1], "score": round(score, 1), "aiValue": ai_values.get(point), "marked": point in marked, "food": food, "other": other, "fresh": fresh, "coastal": coastal, "hill": hill, "terrain": tile["terrain"], "feature": tile.get("feature"),
            "grass": grass, "floodPlains": flood, "oases": oasis, "riverPlots": river, "desert": desert, "water": water, "overlap": overlap, "unknown": unknown, "fromOurCity": dist,
            "rivalOwned": rival_owned, "atRisk": at_risk, "usable": 21 - rival_owned - unknown,
            "rivalBorder": near_rival[0], "rivalBorderOwner": near_rival[1] and owners.get(near_rival[1][2]), "rivalBorderDirection": near_rival[1] and direction(point, near_rival[1][:2]),
            "rivalCity": min([distance(point, q) for q in rival_cities] or [None])})
    rows.sort(key=lambda row: -row["score"])
    # <!-- custom: Sites within 2 plots of a better one are listed under it as alternatives, one region per entry: 24,12, 24,13 and 24,14 took three of the eight rows as one choice (Continents replay, 2026-11-19). (Claude code Opus 5.5) -->
    regions = []
    for row in rows:
        home = [region for region in regions if distance((row["x"], row["y"]), (region["x"], region["y"])) <= 2]
        if home and not row["marked"]:
            home[0]["alternatives"].append({"x": row["x"], "y": row["y"], "score": row["score"], "aiValue": row["aiValue"]})
        else:
            row["alternatives"] = []
            regions.append(row)
    # <!-- custom: The plot to stand on matters as well as the radius: the user's rule is to settle on the plot worst to work and best to stand on, such as a plains hill, and to keep a grass hill as a worked plot; compare the alternatives for that rather than taking the top one blindly. (Claude code Opus 5.5) -->
    top = regions[:limit]
    top += [region for region in regions[limit:] if region["marked"]]
    return {"cities": cities, "sites": top}


def main():
    parser = argparse.ArgumentParser(description="Compare candidate city sites from the fogged grid: resources, fresh water, coast, hill, grassland, overlap, unknown plots and distance to rivals, with a heuristic score.")
    parser.add_argument("--pid", type=int, help="Civ4 client PID")
    parser.add_argument("--cities", help="X,Y;X,Y of our cities to measure from; default every city of ours in sight")
    parser.add_argument("--near", type=int, default=3, help="nearest distance from our cities, default 3")
    # <!-- custom: Default 8, was 6: the user's 21,15 lay 7 from Dublin and was the best site (Continents replay, 2026-11-19). (Claude code Opus 5.5) -->
    parser.add_argument("--far", type=int, default=8, help="farthest distance from our cities, default 8; dot-map marks are rated at any distance")
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

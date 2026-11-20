# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Watch a game a person plays in the window and print one line per change: units moved, created or lost, city builds and sizes, worked plots, research, and turns.
# Written on 2026-11-19, when the user took the controls of the Continents replay and asked the agent to follow each move; clicks in the window do not pass through SASPilot's command log, so the game's state is polled and compared instead. (Claude code Opus 5.5) -->

import argparse
import json
import sys
import time

# <!-- custom: SASPilotClient for the read requests; reads go into the command log as any SASPilotClient.py command does. (Claude code Opus 5.5) -->
import SASPilotClient as pilot
from SASPilotClient import PilotError, pick_pid, request


def ask(pid, command, args=None):
    reply = request(pid, command, args or {})
    if not reply["ok"]:
        raise PilotError(reply["error"].strip().splitlines()[-1])
    return reply["result"]


def snapshot(pid):
    state = {"turn": ask(pid, "todo")["turn"]}
    state["units"] = dict((u["id"], (u["type"], u["x"], u["y"], u.get("mission"), u.get("activity"))) for u in ask(pid, "units"))
    state["cities"] = {}
    for city in ask(pid, "cities"):
        worked = [(p["x"], p["y"]) for p in ask(pid, "citizens", {"city": city["id"]})["plots"] if p["worked"]]
        state["cities"][city["id"]] = (city["name"], city["population"], tuple(city["queue"]), tuple(sorted(worked)))
    research = ask(pid, "research")
    state["research"] = (tuple(q["tech"] for q in research["queue"]), tuple(research["known"]))
    # <!-- custom: The game's own messages too, as a hut's result (49 gold at 13,11) or a combat showed only through a separate 'messages' read in the first watch (2026-11-19). (Claude code Opus 5.5) -->
    state["messages"] = tuple((m["turn"], m["text"]) for m in ask(pid, "messages"))
    # <!-- custom: Foreign units and cities in sight around our own, so a rival Settler heading for a contested site shows the moment it is seen: the user's request (2026-11-19), to settle first and deny it if Persia threatened the sites at 21,15 and 14,16. (Claude code Opus 5.5) -->
    centers = set((u[1], u[2]) for u in state["units"].values()) | set()
    for city in ask(pid, "cities"):
        centers.add((city["x"], city["y"]))
    foreign, rival_cities = {}, set()
    for (x, y) in centers:
        for plot in ask(pid, "plots", {"x": x, "y": y, "radius": FOREIGN_RADIUS, "fog": True}):
            if plot.get("isCity") and plot.get("owner") not in (None, -1, 0):
                rival_cities.add((plot["x"], plot["y"], plot["owner"]))
            for unit in plot.get("units", []):
                if unit["owner"] != 0:
                    foreign[(unit["owner"], unit.get("id"))] = (unit["type"], plot["x"], plot["y"])
    state["foreign"] = foreign
    state["rivalCities"] = rival_cities
    return state


FOREIGN_RADIUS = 3


def changes(old, new):
    lines = []
    if new["turn"] != old["turn"]:
        lines.append("turn %d began" % new["turn"])
    for uid, unit in new["units"].items():
        before = old["units"].get(uid)
        if before is None:
            lines.append("new %s %d at %d,%d" % (unit[0], uid, unit[1], unit[2]))
        elif (before[1], before[2]) != (unit[1], unit[2]):
            lines.append("%s %d moved %d,%d -> %d,%d" % (unit[0], uid, before[1], before[2], unit[1], unit[2]))
        # <!-- custom: An order that ends (mission cleared, unit awake again) is left out: it followed each move as a second line, "now ACTIVITY_AWAKE", in the first watch of the user's moves (2026-11-19). (Claude code Opus 5.5) -->
        elif (before[3], before[4]) != (unit[3], unit[4]) and not (unit[3] is None and unit[4] == "ACTIVITY_AWAKE"):
            lines.append("%s %d at %d,%d now %s %s" % (unit[0], uid, unit[1], unit[2], unit[3] or "", unit[4] or ""))
    for uid, unit in old["units"].items():
        if uid not in new["units"]:
            lines.append("%s %d gone from %d,%d (used, lost or upgraded)" % (unit[0], uid, unit[1], unit[2]))
    for cid, city in new["cities"].items():
        before = old["cities"].get(cid)
        if before is None:
            lines.append("city %s founded (size %d)" % (city[0], city[1]))
            continue
        if before[1] != city[1]:
            lines.append("%s size %d -> %d" % (city[0], before[1], city[1]))
        if before[2] != city[2]:
            lines.append("%s queue %s -> %s" % (city[0], list(before[2]), list(city[2])))
        if before[3] != city[3]:
            lines.append("%s works %s instead of %s" % (city[0], sorted(set(city[3]) - set(before[3])), sorted(set(before[3]) - set(city[3]))))
    if new["research"][0] != old["research"][0]:
        # <!-- custom: An empty queue says so plainly: the user chose to research one tech at a time (2026-11-19), so each landing tech leaves the choice open, and a turn must not pass without one. (Claude code Opus 5.5) -->
        lines.append(new["research"][0] and "research queue %s" % list(new["research"][0]) or "research queue empty: choose the next tech")
    for tech in new["research"][1]:
        if tech not in old["research"][1]:
            lines.append("learned %s" % tech)
    for message in new["messages"]:
        if message not in old["messages"]:
            lines.append("message T%d: %s" % message)
    for key, unit in new.get("foreign", {}).items():
        if key not in old.get("foreign", {}):
            lines.append("%sforeign %s of player %d seen at %d,%d" % ("RIVAL SETTLER: " if unit[0] == "UNIT_SETTLER" else "", unit[0], key[0], unit[1], unit[2]))
    for city in new.get("rivalCities", set()) - old.get("rivalCities", set()):
        lines.append("RIVAL CITY of player %d seen at %d,%d" % (city[2], city[0], city[1]))
    return lines


# <!-- custom: Moments worth a named save, which a replay can start from: the user's point (2026-11-19) after an autosave of turn 8 nearly got overwritten by a replay reaching the same year, and the request to recognise such moments without being told. (Claude code Opus 5.5) -->
KEY_UNITS = ("UNIT_SETTLER", "UNIT_WORKER", "UNIT_SCOUT")
KEY_MESSAGES = ("We have met", "declared war", "declares war")
SMALL_CITY = 3


def key_moment(old, new):
    for uid, unit in new["units"].items():
        if uid not in old["units"] and unit[0] in KEY_UNITS:
            return "new_" + unit[0][5:].lower()
    for cid, city in new["cities"].items():
        if cid not in old["cities"]:
            return "founded_" + city[0].lower().replace(" ", "_")
        if city[1] > old["cities"][cid][1] and city[1] <= SMALL_CITY:
            return "%s_size%d" % (city[0].lower().replace(" ", "_"), city[1])
    for message in new["messages"]:
        if message not in old["messages"] and any(key in message[1] for key in KEY_MESSAGES):
            return "contact_or_war"
    # <!-- custom: A research choice is a decision worth returning to, the user's view when Masonry was chosen for Slavery (2026-11-19). (Claude code Opus 5.5) -->
    # <!-- custom: Only when the queue's goal, its last tech, changes: a tech landing shortened the queue toward the same goal and took a needless save at turns 18 and 30 of the replay. (Claude code Opus 5.5) -->
    if new["research"][0] and new["research"][0][-1:] != old["research"][0][-1:]:
        return "research_" + new["research"][0][-1][5:].lower()
    return None


def main():
    parser = argparse.ArgumentParser(description="Print one line per change in the game a person plays in the window: units, cities, worked plots, research, messages and turns.")
    parser.add_argument("--pid", type=int, help="Civ4 client PID")
    parser.add_argument("--interval", type=float, default=2.0, help="seconds between polls (default 2)")
    parser.add_argument("--saves", metavar="PREFIX", help="take a named save PREFIX_tNNN_<moment> at key moments: a new Settler, Worker or Scout, a city founded or growing while small, a contact or a war; at most one a turn")
    args = parser.parse_args()
    saved_turns = set()
    pid = pick_pid(args.pid)
    old = snapshot(pid)
    print("watching turn %d: %d units, %d cities" % (old["turn"], len(old["units"]), len(old["cities"])), flush=True)
    while True:
        time.sleep(args.interval)
        try:
            new = snapshot(pid)
        except (OSError, PilotError) as error:
            # <!-- custom: A poll can fail while the game is busy, such as between turns or on a screen change; the next poll tries again, and only a closed game ends the watch. (Claude code Opus 5.5) -->
            if "not running" in str(error) or "no Civ4" in str(error):
                print("watch ended: %s" % error, flush=True)
                return 0
            continue
        for line in changes(old, new):
            print(line, flush=True)
        moment = args.saves and new["turn"] not in saved_turns and key_moment(old, new)
        if moment:
            name = "%s_t%03d_%s" % (args.saves, new["turn"], moment)
            try:
                ask(pid, "save", {"path": name})
                saved_turns.add(new["turn"])
                print("saved %s" % name, flush=True)
            except (OSError, PilotError) as error:
                print("save %s failed: %s" % (name, error), flush=True)
        old = new


if __name__ == "__main__":
    raise SystemExit(main())

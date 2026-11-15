# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Plot analysis for the pilot, in numbers rather than pictures.
# At turn 57 of the islands replay (2026-11-15) the AI's found value rated one site on our island, while the user's plan (claim the coast by settling its corners) needed sites the AI rates 0; judging them meant reading plots one by one.
# The user asked for plots judged numerically, for settling and also for Workers and military: this fetches the plot data once through the pilot's 'plots' (fog respected, as the game shows it: every revealed plot with its current yields; 'grid' gives yields only for plots in sight) and computes over it with numpy and scipy, which the game's Python 2.4 does not have.
# The area is a square around an anchor the user asked for (2026-11-15): coordinates, one of our units, a city, a known bonus or the plot the camera looks at, with --radius for its size.
# Run with modern Python; the game must be running under SASPilotClient.py.
# Its requests go through SASPilotClient.request, so the command log keeps them.
# For city sites, SASPilotSites.py scores candidates by our heuristic and the 'plansites' command adds legality and the AI's value. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads options, sys reports errors; SASPilotClient sends the requests, logged as its own are; numpy and scipy.ndimage do the sums over the city radius and the connected regions. (Claude code Opus 5.5) -->
import argparse
import sys

import numpy
from scipy import ndimage

from SASPilotClient import PilotError, pick_pid, request

PID = None
YIELDS = ("food", "production", "commerce")
# <!-- custom: The city radius of Civ4 (NUM_CITY_PLOTS = 21): the 5 by 5 square without its four corners. (Claude code Opus 5.5) -->
CITY_KERNEL = numpy.ones((5, 5), dtype=int)
for (cy, cx) in ((0, 0), (0, 4), (4, 0), (4, 4)):
	CITY_KERNEL[cy, cx] = 0


def pilot(command, **args):
	# <!-- custom: One pilot request; an error reply ends the run with the pilot's message. (Claude code Opus 5.5) -->
	reply = request(PID, command, args)
	if not reply["ok"]:
		raise PilotError("%s: %s" % (command, reply["error"]))
	return reply["result"]


class Area:
	# <!-- custom: The square around the anchor as arrays, indexed by offset from it (row 0 the south row): yields, land, coast, hills, owner and whether the team has revealed each plot.
	# Unrevealed plots hold 0 and revealed is False.
	# By offset, as Codex's review found the first version, indexed by the plots' min and max, turned a square across the east-west seam of a wrapping map into a map-wide box whose sums and regions missed the neighbours across the seam. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	def __init__(self, cx, cy, radius, width, height, wrapX, wrapY):
		self.cx, self.cy, self.radius = cx, cy, radius
		self.width, self.height, self.wrapX, self.wrapY = width, height, wrapX, wrapY
		self.w = self.h = 2 * radius + 1
		shape = (self.h, self.w)
		self.yields = numpy.zeros((3,) + shape, dtype=int)
		self.revealed = numpy.zeros(shape, dtype=bool)
		self.land = numpy.zeros(shape, dtype=bool)
		self.coast = numpy.zeros(shape, dtype=bool)
		self.hill = numpy.zeros(shape, dtype=bool)
		self.owner = numpy.full(shape, -1, dtype=int)
		self.bonus = numpy.full(shape, "", dtype=object)

	def offset(self, x, y):
		dx, dy = x - self.cx, y - self.cy
		if self.wrapX:
			dx = (dx + self.width // 2) % self.width - self.width // 2
		if self.wrapY:
			dy = (dy + self.height // 2) % self.height - self.height // 2
		return (dx, dy)

	def inside(self, x, y):
		dx, dy = self.offset(x, y)
		return abs(dx) <= self.radius and abs(dy) <= self.radius

	def at(self, x, y):
		dx, dy = self.offset(x, y)
		return (dy + self.radius, dx + self.radius)

	def x_of(self, c):
		x = self.cx + c - self.radius
		return self.wrapX and x % self.width or x

	def y_of(self, r):
		y = self.cy + r - self.radius
		return self.wrapY and y % self.height or y

	def describe(self):
		return "square of radius %d around %d,%d" % (self.radius, self.cx, self.cy)

	def radius_sum(self, layer):
		# <!-- custom: For each plot, the sum of layer over the city radius around it, as if a city stood there.
		# Outside the square counts 0, so plots near its edge read low; judge plots at least 2 inside it. (Claude code Opus 5.5) -->
		return ndimage.convolve(layer.astype(int), CITY_KERNEL, mode="constant", cval=0)


def anchor(args):
	# <!-- custom: The center as 'plots' takes it, from whichever anchor was given; a bonus is found in 'resources', the bonuses the player knows, the first of that type or the --nth. (Claude code Opus 5.5) -->
	if args.camera:
		return {"camera": 1}
	if args.unit is not None:
		return {"unit": args.unit}
	if args.city is not None:
		return {"city": args.city}
	if args.bonus:
		found = [r for r in pilot("resources")["resources"] if r["bonus"] == args.bonus]
		if len(found) < args.nth:
			raise PilotError("%d %s known; --nth %d is past them" % (len(found), args.bonus, args.nth))
		return {"x": found[args.nth - 1]["x"], "y": found[args.nth - 1]["y"]}
	if args.x is None or args.y is None:
		raise PilotError("give an anchor: --x and --y, --unit, --city, --bonus or --camera")
	return {"x": args.x, "y": args.y}


def fetch_square(center, radius):
	# <!-- custom: The anchor's plot and the map's size and wrapping come from 'grid' with radius 0; the plots from 'plots', and their yields from 'potential' up to its radius of 15: out of sight, 'plots' gives live yields, which showed improvements a rival had built out of sight, while 'potential' gives what the team last saw (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	query = dict(center)
	query["radius"] = 0
	query["edge"] = 0
	query["network"] = 0
	where = pilot("grid", **query)
	area = Area(where["box"][0], where["box"][1], radius, where["width"], where["height"], where["wrapX"], where["wrapY"])
	query = {"x": area.cx, "y": area.cy, "radius": radius}
	for tile in pilot("plots", **query):
		if not area.inside(tile["x"], tile["y"]):
			continue
		r, c = area.at(tile["x"], tile["y"])
		area.revealed[r, c] = True
		area.yields[:, r, c] = tile["yields"]
		area.land[r, c] = tile["plotType"] != "PLOT_OCEAN"
		area.coast[r, c] = tile["terrain"] == "TERRAIN_COAST"
		area.hill[r, c] = tile["plotType"] == "PLOT_HILLS"
		area.owner[r, c] = tile["owner"] if tile["owner"] is not None else -1
		area.bonus[r, c] = tile["bonus"] or ""
	area.options = {}
	if radius <= 15:
		for tile in pilot("potential", **query):
			if area.inside(tile["x"], tile["y"]):
				r, c = area.at(tile["x"], tile["y"])
				area.yields[:, r, c] = tile["yields"]
				area.options[(r, c)] = tile["options"]
	else:
		print("note: radius over 15, so plots out of sight show their live yields", file=sys.stderr)
	return area


def improve(area, weights, bLater):
	# <!-- custom: --potential: each plot takes the yields of its best improvement by the given weights, from the pilot's 'potential' (today's techs; builds a tech away only with --later), or keeps its yields when nothing improves it more.
	# Asked by the user at turn 59 of the islands replay (2026-11-15), as a site with two Clams rated below plain coast on today's yields. (Claude code Opus 5.5) -->
	for ((r, c), options) in area.options.items():
		best = list(area.yields[:, r, c])
		for option in options:
			if (option["now"] or bLater) and sum([w * y for (w, y) in zip(weights, option["yields"])]) > sum([w * y for (w, y) in zip(weights, best)]):
				best = option["yields"]
		area.yields[:, r, c] = best


def fetch(args):
	area = fetch_square(anchor(args), args.radius)
	if args.potential:
		weights = [float(w) for w in args.potential.split(",")]
		if len(weights) != 3:
			raise PilotError("--potential takes food,production,commerce weights, e.g. 2,1,3")
		if args.radius > 15:
			raise PilotError("--potential needs --radius 15 or less")
		improve(area, weights, args.later)
	return area


def print_layer(area, values, mask=None):
	# <!-- custom: North at the top, as the map shows it; '.'
	# for an unrevealed plot, '~' for water when mask leaves water out. (Claude code Opus 5.5) -->
	width = max([len(str(v)) for v in values.flatten()] + [len(str(area.x_of(c))) for c in range(area.w)] + [2])
	print("     " + "".join([("%d" % area.x_of(c)).rjust(width + 1) for c in range(area.w)]))
	for r in range(area.h - 1, -1, -1):
		cells = []
		for c in range(area.w):
			if not area.revealed[r, c]:
				cells.append(".".rjust(width + 1))
			elif mask is not None and not mask[r, c]:
				cells.append("~".rjust(width + 1))
			else:
				cells.append(str(values[r, c]).rjust(width + 1))
		print(("%4d " % area.y_of(r)) + "".join(cells))


def cmd_layer(args):
	area = fetch(args)
	if args.name in YIELDS:
		values = area.yields[YIELDS.index(args.name)]
	elif args.name == "owner":
		values = area.owner
	elif args.name == "coast":
		values = area.coast.astype(int)
	else:
		sys.exit("layer must be food, production, commerce, owner or coast")
	if args.sum:
		values = area.radius_sum(values)
	print("%s%s%s, %s" % (args.name, args.potential and (" with the best improvement by weights %s%s" % (args.potential, args.later and ", builds a tech away included" or "")) or "", args.sum and ", summed over a city radius" or "", area.describe()))
	# <!-- custom: Water shows its values too: coast commerce is what an island plan counts. (Claude code Opus 5.5) -->
	print_layer(area, values)


def cmd_regions(args):
	# <!-- custom: Connected revealed land (diagonals connect, as units move), and within it the unowned clusters, each with its size and box: where land is left to claim and how big each piece is. (Claude code Opus 5.5) -->
	area = fetch(args)
	structure = numpy.ones((3, 3), dtype=int)
	for (name, mask) in (("land", area.land & area.revealed), ("unowned land", area.land & area.revealed & (area.owner < 0))):
		labels, count = ndimage.label(mask, structure=structure)
		print("%s: %d region(s) in the %s" % (name, count, area.describe()))
		for i, box in enumerate(ndimage.find_objects(labels)):
			size = int((labels[box] == i + 1).sum())
			print("  %3d plots, x %d..%d, y %d..%d" % (size, area.x_of(box[1].start), area.x_of(box[1].stop - 1), area.y_of(box[0].start), area.y_of(box[0].stop - 1)))


def main():
	# <!-- custom: The examples live in --help rather than the header comment, where the comment reflow joined the command lines into one sentence. (Claude code Opus 5.5) -->
	parser = argparse.ArgumentParser(description="Plot analysis in numbers over the pilot's map data (fog respected).", formatter_class=argparse.RawDescriptionHelpFormatter, epilog="examples:\n  python LLM_Helpers/saspilot/SASPilotPlots.py layer food --camera --radius 6\n  python LLM_Helpers/saspilot/SASPilotPlots.py layer commerce --sum --city 8192 --radius 5\n  python LLM_Helpers/saspilot/SASPilotPlots.py layer production --bonus BONUS_HORSE --radius 3\n  python LLM_Helpers/saspilot/SASPilotPlots.py layer food --unit 40962\n  python LLM_Helpers/saspilot/SASPilotPlots.py layer food --sum --potential 2,1,3 --later --x 96 --y 22 --radius 4\n  python LLM_Helpers/saspilot/SASPilotPlots.py regions --x 99 --y 25 --radius 10")
	sub = parser.add_subparsers(dest="command", required=True)
	for name in ("layer", "regions"):
		p = sub.add_parser(name)
		if name == "layer":
			p.add_argument("name", help="food, production, commerce, owner or coast")
			p.add_argument("--sum", action="store_true", help="sum over a city radius around each plot")
		p.add_argument("--camera", action="store_true", help="center on the plot the main view looks at")
		p.add_argument("--unit", type=int, help="center on one of our units")
		p.add_argument("--city", type=int, help="center on one of our cities")
		p.add_argument("--bonus", help="center on a known bonus, e.g. BONUS_HORSE (the first, or --nth)")
		p.add_argument("--nth", type=int, default=1)
		p.add_argument("--x", type=int)
		p.add_argument("--y", type=int)
		p.add_argument("--radius", type=int, default=6, help="half the square's side")
		p.add_argument("--potential", help="food,production,commerce weights: each plot counts the yields of its best improvement by them (today's techs)")
		p.add_argument("--later", action="store_true", help="with --potential, also builds a tech away (still with today's tech bonuses)")
	parser.add_argument("--pid", type=int, help="Civ4 client PID")
	args = parser.parse_args()
	global PID
	try:
		PID = pick_pid(args.pid)
		{"layer": cmd_layer, "regions": cmd_regions}[args.command](args)
	except (OSError, PilotError) as error:
		print("SASPilotPlots: %s" % error, file=sys.stderr)
		return 1
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

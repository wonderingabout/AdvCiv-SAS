#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Builds a map plot for nif_preview.py to draw a unit, bonus or feature on: its terrain, plot type and feature, from the game's own art.
# Adding the Marsh feature meant judging its bog.nif and its fit on Grassland from in-game screenshots alone; a plot preview shows such art on any terrain without the game.
# The engine draws terrain from texture sheets and heightmaps rather than models, so this is an approximation: one terrain's solid tile, rolling ground under the Hill terrain's rock overlay for hills, the game's peak heightmap under the Peak terrain's rock and snow for peaks, a river piece where a feature needs one, and the feature's fullest art piece.
# Art comes from the mod's XML where the game defines it there: terrains, the Hill and Peak terrains, features, river pieces and flood plain textures.
# See README_Art_Tools.md. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the sheet options; concurrent.futures render a sheet's plots in parallel; os counts processors. (Claude code Opus 5.5) -->
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
# <!-- custom: pathlib, subprocess and sys run nif_preview.py for each plot; re reads the XML fields. (Claude code Opus 5.5) -->
from pathlib import Path
import re
import subprocess
import sys

# <!-- custom: numpy builds the ground grid; Pillow loads the textures and assembles the sheet. (Claude code Opus 5.5) -->
import numpy as np
from PIL import Image, ImageDraw

# <!-- custom: The ground around the plot's centre reaches past the plot, as feature art does: the forest's pieces span about 230 of the plot's 180 units. (Claude code Opus 5.5) -->
GROUND_REACH = 0.75
GRID = 24
# <!-- custom: Plot types are fixed in the game (peak, hills, flat land and water); the game paints hills and peaks with the terrains a mod gives these Types, whose art each mod may change. (Claude code Opus 5.5) -->
PLOT_TYPE_TERRAINS = {"hills": "TERRAIN_HILL", "peak": "TERRAIN_PEAK"}
# <!-- custom: The peak's heightmaps are named in no XML, so the engine loads them by these paths; a mod replaces one by putting a file there, which staging through the mod finds. (Claude code Opus 5.5) -->
PEAK_HEIGHTMAP = "Art/Terrain/Features/Peak/PeakHeightA.tga"
# <!-- custom: The peak's height at the heightmap's full value, chosen by eye: in-game screenshots (2026-11-09) show a steep peak about four fifths of a plot tall. (Claude code Opus 5.5) -->
PEAK_RELIEF = 1.1
# <!-- custom: The game lights terrain paler and bluer than its textures: in-game screenshots (2026-11-09) averaged desert 235 207 163, plains 158 151 118, grassland 113 131 73, tundra 98 102 82 and snow 186 213 236, against 244 206 146, 174 149 89, 108 119 61, 108 106 93 and 189 211 227 for their tiles after the Detail texture.
# Our lighting also darkens a flat plot to about 0.9 of its texture; this per-channel gain and offset is fitted to those five pairs.
# A first fit to the first three alone added more blue, which turned tundra blue-grey at 110 120 114; no one gain and offset fits all five exactly, and tundra stays a little bluer than in game. (Claude code Opus 5.5) -->
MAP_LIGHT_GAIN = np.array([1.057, 1.096, 1.106], dtype=np.float32)
MAP_LIGHT_OFFSET = np.array([1.6, 5.3, 13.1], dtype=np.float32) / 255.0
# <!-- custom: The water plane's colour and opacity, solved from the Coast and Ocean tiles after the light above and their in-game averages; see water_surface. (Claude code Opus 5.5) -->
WATER_COLOUR = np.array([52, 99, 127], dtype=np.float32) / 255.0
WATER_OPACITY = 0.65


def texture_array(path):
	return np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / 255.0


def terrain_tile(path):
	# <!-- custom: A land terrain's Blend sheet holds alpha-masked edge pieces in its top half and solid, seamless terrain in its bottom half, which is the tile.
	# Coast's and Ocean's sheets are nearly all edge pieces, and their bottom half mixed sand into the water, so there the tile is the most opaque single cell of the 4 by 8 grid. (Claude code Opus 5.5) -->
	sheet = texture_array(path)
	height, width = sheet.shape[:2]
	bottom = sheet[height // 2:]
	if bottom[..., 3].min() > 0.99:
		return bottom
	cell = width // 4
	cells = [sheet[row:row + cell, column:column + cell] for row in range(0, height, cell) for column in range(0, width, cell)]
	return max(cells, key=lambda piece: piece[..., 3].mean())


def with_detail(tile, detail):
	# <!-- custom: The engine multiplies a terrain's tile by its Detail texture at twice its value: the base game's Detail textures average about 128, which leaves the tile's colour, while Caveman2Cosmos's Lush and Rocky tiles are plain grey and take their colour from theirs.
	# Without it, those terrains came out blue-grey.
	# The Detail is laid once over the tile here; how often the engine repeats it was not measured. (Claude code Opus 5.5) -->
	size = (tile.shape[1], tile.shape[0])
	scaled = np.asarray(Image.fromarray((detail * 255).astype(np.uint8)).resize(size), dtype=np.float32) / 255.0
	result = tile.copy()
	result[..., :3] = np.clip(tile[..., :3] * scaled[..., :3] * 2, 0, 1)
	return result


def map_light(tile):
	lit = tile.copy()
	lit[..., :3] = np.clip(tile[..., :3] * MAP_LIGHT_GAIN + MAP_LIGHT_OFFSET, 0, 1)
	return lit


def field(body, tag):
	match = re.search(r"<%s>\s*([^<]*?)\s*</%s>" % (tag, tag), body or "")
	return match.group(1) if match else None


def listed(body, outer, inner, flag):
	# <!-- custom: Types an info marks allowed, such as a bonus's <TerrainBooleans>: each <TerrainType> whose <bTerrain> is 1. (Claude code Opus 5.5) -->
	section = re.search(r"<%s>(.*?)</%s>" % (outer, outer), body or "", re.DOTALL)
	if not section:
		return []
	return [kind for kind, value in re.findall(r"<%s>\s*([^<\s]+)\s*</%s>\s*<%s>\s*(\d)" % (inner, inner, flag), section.group(1)) if value == "1"]


def is_water(terrain_body):
	# <!-- custom: Caveman2Cosmos leaves out <bWater> and gives its water terrains <iDistanceToLand> instead, which no land terrain has there. (Claude code Opus 5.5) -->
	return field(terrain_body, "bWater") == "1" or (field(terrain_body, "bWater") is None and field(terrain_body, "iDistanceToLand") is not None)


def fallback_terrains(assets):
	# <!-- custom: The land and water terrains a preview falls back on: Grassland and Coast, or a mod's first land and water terrain when it has neither, as Caveman2Cosmos names Grassland TERRAIN_GRASSLAND. (Claude code Opus 5.5) -->
	terrains = assets.infos("Terrain", "terraininfos", "TerrainInfo")
	land = [kind for kind, body in terrains.items() if not is_water(body) and kind not in PLOT_TYPE_TERRAINS.values()]
	sea = [kind for kind, body in terrains.items() if is_water(body)]
	return ("TERRAIN_GRASS" if "TERRAIN_GRASS" in land else land[0]), ("TERRAIN_COAST" if "TERRAIN_COAST" in sea else sea[0])


def defaults(assets, subject):
	# <!-- custom: The terrain, feature and plot type a preview starts from, taken from what the XML allows: a bonus's first allowed feature on a terrain that feature allows, else its first terrain, flat when it allows flatlands; a feature's first terrain; an improvement's first valid terrain or feature; a unit's domain, land on Grassland and sea on Coast. (Claude code Opus 5.5) -->
	subject = subject.upper()
	land, sea = fallback_terrains(assets)
	if subject.startswith("TERRAIN_"):
		for plot, kind in PLOT_TYPE_TERRAINS.items():
			if subject == kind:
				return land, None, plot
		return subject, None, "flat"
	features = assets.infos("Terrain", "featureinfos", "FeatureInfo")
	if subject.startswith("FEATURE_"):
		terrains = listed(features.get(subject), "TerrainBooleans", "TerrainType", "bTerrain")
		return (terrains[0] if terrains else land), subject, "flat"
	bonuses = assets.infos("Terrain", "bonusinfos", "BonusInfo")
	bonus = bonuses.get(subject) or next((body for body in bonuses.values() if field(body, "ArtDefineTag") == subject), None)
	if bonus is not None:
		terrains = listed(bonus, "TerrainBooleans", "TerrainType", "bTerrain")
		features_allowed = listed(bonus, "FeatureBooleans", "FeatureType", "bFeature")
		feature_terrains = listed(bonus, "FeatureTerrainBooleans", "TerrainType", "bFeatureTerrain")
		plot = "flat" if field(bonus, "bFlatlands") == "1" or field(bonus, "bHills") != "1" else "hills"
		if features_allowed:
			feature = features_allowed[0]
			on = feature_terrains or listed(features.get(feature), "TerrainBooleans", "TerrainType", "bTerrain")
			return (on[0] if on else land), feature, plot
		return (terrains[0] if terrains else land), None, plot
	improvements = assets.infos("Terrain", "improvementinfos", "ImprovementInfo")
	improvement = improvements.get(subject) or next((body for body in improvements.values() if field(body, "ArtDefineTag") == subject), None)
	if improvement is not None:
		# <!-- custom: An improvement's first valid terrain or feature from <TerrainMakesValids> and <FeatureMakesValids>, on hills when only bHillsMakesValid allows it, as for the Mine. (Claude code Opus 5.5) -->
		terrains = listed(improvement, "TerrainMakesValids", "TerrainType", "bMakesValid")
		features_valid = listed(improvement, "FeatureMakesValids", "FeatureType", "bMakesValid")
		if field(improvement, "bWater") == "1":
			return sea, None, "flat"
		if terrains:
			return terrains[0], None, "flat"
		if features_valid:
			on = listed(features.get(features_valid[0]), "TerrainBooleans", "TerrainType", "bTerrain")
			return (on[0] if on else land), features_valid[0], "flat"
		return land, None, "hills" if field(improvement, "bHillsMakesValid") == "1" else "flat"
	unit = assets.units().get(subject)
	if unit is not None and unit["Domain"] == "DOMAIN_SEA":
		return sea, None, "flat"
	return land, None, "flat"


# <!-- custom: Added effect, at and scrolling for features whose art is animated, Fallout's cards and the Oasis's water; their defaults draw any other model as before. (Claude code Opus 5.5) -->
def model_meshes(assets, cache, args, path, effect=None, at=None, scrolling=False):
	# <!-- custom: nif_preview reads and poses the hill, peak and feature models; imported here because nif_preview imports this module. (Claude code Opus 5.5) -->
	from nif_preview import read_nif, scene_geometry
	local, _ = assets.stage(path, cache)
	return scene_geometry(read_nif(local), str(local.parent), args, at, {}, {}, effect=effect, scrolling=scrolling)[1]


def textures_scroll(assets, cache, args, path):
	# <!-- custom: Whether a model scrolls its textures, as the Oasis's water, noting the loop's length for a GIF. (Claude code Opus 5.5) -->
	from nif_preview import NifFormat, read_nif
	stops = [block.stop_time for block in read_nif(assets.stage(path, cache)[0]).blocks if isinstance(block, NifFormat.NiTextureTransformController)]
	if stops:
		args.plot_span = max(stops)
	return bool(stops)


def billboard_effect(assets, cache, args, path):
	# <!-- custom: A model of camera-facing cards, as Fallout's, gets the view and --glow, and notes its colour loop's length for a GIF; None for any other model. (Claude code Opus 5.5) -->
	from nif_preview import NifFormat, grid_view, read_nif
	blocks = read_nif(assets.stage(path, cache)[0]).blocks
	if not any(isinstance(block, NifFormat.NiBillboardNode) for block in blocks):
		return None
	args.plot_span = max((block.stop_time for block in blocks if isinstance(block, NifFormat.NiMaterialColorController)), default=None)
	view = grid_view(args, 0, True)
	return np.array([view[0], view[1], -view[2]]), args.glow / 100.0


def relief(x, y, size, height, rolling):
	# <!-- custom: The ground's height: a broad rise in the plot's middle, plus fixed ripples on hills, which in game roll over the whole plot rather than forming one smooth bump.
	# Sums of sines keep every render the same. (Claude code Opus 5.5) -->
	z = height * np.exp(-(x * x + y * y) / (2 * (0.35 * size) ** 2))
	if rolling:
		u, v = x / size * 2 * np.pi, y / size * 2 * np.pi
		z = z + height * 0.35 * (np.sin(1.7 * u + 0.6) * np.cos(1.3 * v - 0.4) + 0.5 * np.sin(3.1 * u - 1.2 * v + 1.0))
	return z


class Surface:
	# <!-- custom: The ground's heights on a square grid over the ground's reach, so a feature or a river piece can stand on a hill or a peak at any point. (Claude code Opus 5.5) -->
	def __init__(self, size, heights):
		self.reach = size * GROUND_REACH
		self.heights = heights

	def axis(self):
		return np.linspace(-self.reach, self.reach, self.heights.shape[0])

	def at(self, x, y):
		count = self.heights.shape[0] - 1
		column = np.clip((np.asarray(x) + self.reach) / (2 * self.reach) * count, 0, count)
		row = np.clip((np.asarray(y) + self.reach) / (2 * self.reach) * count, 0, count)
		c0, r0 = np.minimum(column.astype(int), count - 1), np.minimum(row.astype(int), count - 1)
		fc, fr = column - c0, row - r0
		h = self.heights
		return (h[r0, c0] * (1 - fc) + h[r0, c0 + 1] * fc) * (1 - fr) + (h[r0 + 1, c0] * (1 - fc) + h[r0 + 1, c0 + 1] * fc) * fr


def flat_surface(size, height, rolling, grid=GRID):
	axis = np.linspace(-size * GROUND_REACH, size * GROUND_REACH, grid + 1)
	x, y = np.meshgrid(axis, axis)
	return Surface(size, relief(x, y, size, height, rolling))


def peak_surface(assets, cache, size):
	# <!-- custom: The game raises a peak from a 10 by 10 heightmap: one summit whose slopes fall in a few big ridges and do not reach zero at the edges, so a peak spills a little into its neighbours, as in-game screenshots show.
	# The first previews stood Peak_Single.nif, a cone, on the plot instead; in game the peak is the ground itself, a wider pyramid.
	# The heightmap is laid over the ground's whole reach, a plot and a half. (Claude code Opus 5.5) -->
	# <!-- custom: Its 10 by 10 points are used as they are, joined by flat faces: in-game peaks (2026-11-09 screenshots) are faceted, with a sharp summit and a few broad ridges.
	# Smoothing them up bicubically to 40 by 40 made the peak round, and dozens of added sine ridges on top made it wavy, both unlike the game. (Claude code Opus 5.5) -->
	values = np.asarray(Image.open(assets.stage(PEAK_HEIGHTMAP, cache)[0]).convert("L"), dtype=np.float32)
	# <!-- custom: Raised to the power 1.4, the slopes curve outward toward the foot, steep near the summit and flaring at the base, as in-game peaks do; the heightmap's own straight slopes looked like a plain ramp. (Claude code Opus 5.5) -->
	return Surface(size, (values / 255.0) ** 1.4 * PEAK_RELIEF * size)


def ground(size, surface, texture, uv_span=None):
	# <!-- custom: A square grid at the surface's heights, textured with the terrain tile once per plot, or once over the whole ground with uv_span for a texture painted for this plot alone. (Claude code Opus 5.5) -->
	axis = surface.axis()
	count = len(axis)
	x, y = np.meshgrid(axis, axis)
	points = np.stack([x.ravel(), y.ravel(), surface.heights.ravel()], axis=1)
	if uv_span:
		uvs = np.stack([(x.ravel() + uv_span) / (2 * uv_span), (y.ravel() + uv_span) / (2 * uv_span)], axis=1)
	else:
		uvs = np.stack([x.ravel() / size, y.ravel() / size], axis=1)
	index = np.arange(count * count).reshape(count, count)
	a, b, c, d = index[:-1, :-1].ravel(), index[:-1, 1:].ravel(), index[1:, :-1].ravel(), index[1:, 1:].ravel()
	triangles = np.concatenate([np.stack([a, b, d], axis=1), np.stack([a, d, c], axis=1)])
	return points, uvs, triangles, texture, False, -1.0


def surface_height(points, surface):
	return surface.at(points[:, 0], points[:, 1])


def overlay_cell(path, strengthen=True):
	# <!-- custom: The Hill and Peak terrains' Blend sheets are overlays the engine paints over the base terrain (LayerOrder 79 and 80, above the land terrains): grey rock streaks for hills, brown rock and snow for peaks, transparent elsewhere.
	# Take the 256-pixel cell they cover most, the piece for a plot inside a range, discounted for snow: the Peak sheet's fullest cell left the ground around the cone white, while in game it is brown rock with snow only near the summits. (Claude code Opus 5.5) -->
	sheet = texture_array(path)
	cell = sheet.shape[1] // 4
	cells = [sheet[row:row + cell, column:column + cell] for row in range(0, sheet.shape[0], cell) for column in range(0, sheet.shape[1], cell)]
	piece = max(cells, key=lambda piece: piece[..., 3].mean() * (1 - 4 * ((piece[..., :3].min(axis=2) > 0.7) & (piece[..., 3] > 0.5)).mean())).copy()
	if strengthen:
		# <!-- custom: Strengthened: at their own alpha the Hill sheet's streaks were faint, while in game the grey rock stands out on plains and desert hills. (Claude code Opus 5.5) -->
		piece[..., 3] = np.minimum(1.0, piece[..., 3] * 1.8)
	return piece


def plot_type_art(assets, terrains, plot):
	# <!-- custom: The Hill or Peak terrain's art define, through the mod's own TerrainInfo rather than a fixed art name, so a mod's own hill and peak art shows. (Claude code Opus 5.5) -->
	kind = PLOT_TYPE_TERRAINS[plot]
	if kind not in terrains:
		raise SystemExit("%s has no %s to paint %s with" % (assets.mod_assets or "the base game", kind, plot))
	tag = field(terrains[kind], "ArtDefineTag")
	return assets.art_defines(tag)[tag]


def sample_tiled(texture, x, y, period):
	# <!-- custom: The texture's texels at ground points, repeating every period units, as the ground's own texturing does. (Claude code Opus 5.5) -->
	h, w = texture.shape[:2]
	return texture[((y / period) % 1.0 * h).astype(int) % h, ((x / period) % 1.0 * w).astype(int) % w]


def centred(texture, x, y, span):
	# <!-- custom: The texture's texels at ground points, laid once over span units around the plot's middle and clamped beyond. (Claude code Opus 5.5) -->
	h, w = texture.shape[:2]
	columns = np.clip(((x / span) + 0.5) * w, 0, w - 1).astype(int)
	rows = np.clip(((y / span) + 0.5) * h, 0, h - 1).astype(int)
	return texture[rows, columns]


def peak_texture(tile, rock, decal, surface, size, resolution=1024):
	# <!-- custom: A peak's slopes are the Peak sheet's rock, its stretched streaks running down the slopes as in game, covered by its decal, with snow near the summit and the base terrain at the foot.
	# The first heightmap peak filled the sheet's transparent texels with its average colour, which looked smoothly spread rather than striped; the sheet's colour is rock everywhere, so all of it is used.
	# Painted for this plot alone, since rock and snow follow the height. (Claude code Opus 5.5) -->
	reach = size * GROUND_REACH
	axis = (np.arange(resolution) + 0.5) / resolution * 2 * reach - reach
	x, y = np.meshgrid(axis, axis)
	height = surface.at(x, y) / max(float(surface.heights.max()), 1e-6)
	base = sample_tiled(tile, x, y, size)[..., :3]
	# <!-- custom: The rock is lit as the terrain is, with its streaks' contrast raised: unlit and darkened by PeakDarkMap2.dds laid around the summit, the slopes averaged 94 78 64, much darker and warmer than in-game peaks' light tan-brown of about 124 113 99 (2026-11-09 screenshots).
	# In game the dark streaks fall on gullies and shadowed faces, sometimes low on the peak and sometimes absent, rather than around the summit, so that dark map, whose use by the engine is not known, is left out. (Claude code Opus 5.5) -->
	lit = map_light(sample_tiled(rock, x, y, size))[..., :3]
	# <!-- custom: Tried and left out (2026-11-09): softening only the dark streaks, their darkening taken from a blurred copy of the rock so their edges faded, with a third of the crisp detail kept inside and at 0.85 strength.
	# It did fade their hard edges as intended, but on comparison the crisp version was preferred as closer to the game overall. (Claude code Opus 5.5) -->
	rock_rgb = np.clip(lit.mean(axis=(0, 1)) + (lit - lit.mean(axis=(0, 1))) * 1.4, 0, 1)
	# <!-- custom: The decal at half its opacity: at full opacity its dark ring around the snowy middle drew a dark band under the snow with a hard edge to the lighter rock below, which in-game peaks do not show. (Claude code Opus 5.5) -->
	cover = centred(decal, x, y, size)
	opacity = 0.5 * cover[..., 3:4]
	rock_rgb = rock_rgb * (1 - opacity) + cover[..., :3] * opacity
	# <!-- custom: The rock fades into the base terrain over the lower slopes, as in-game peaks show (2026-11-09 screenshots); fading it within the bottom sixth gave a sharp foot. (Claude code Opus 5.5) -->
	rise = np.clip((height - 0.02) / 0.4, 0, 1)
	rise = (rise * rise * (3 - 2 * rise))[..., None]
	painted = base * (1 - rise) + rock_rgb * rise
	# <!-- custom: In game the snow cap is the top sixth or so, sharply bounded and speckled with rock. (Claude code Opus 5.5) -->
	snow = np.clip((height - 0.88) / 0.05, 0, 1) * np.clip(0.4 + rock_rgb.mean(axis=2), 0, 1)
	painted = painted * (1 - snow[..., None]) + np.array([0.93, 0.94, 0.96]) * snow[..., None]
	return np.concatenate([painted, np.ones(painted.shape[:2] + (1,))], axis=2).astype(np.float32)


def water_surface(assets, cache):
	# <!-- custom: The water plane: the ripples of ART_WATER in CIV4ArtDefines_Misc.xml, in one colour and opacity fitted so Coast and Ocean come out at their in-game colours.
	# In-game screenshots (2026-11-09) averaged Coast 45 88 116 and Ocean 30 71 97; the first plane, a flat 0.12 0.36 0.55 at 0.6, gave 32 80 116 and 16 62 95, a deeper, more saturated blue than the game's. (Claude code Opus 5.5) -->
	ripples = texture_array(assets.stage(assets.art_defines("ART_WATER")["ART_WATER"]["Path"], cache)[0])
	brightness = ripples[..., :3].mean(axis=2, keepdims=True)
	surface = np.empty(ripples.shape, dtype=np.float32)
	surface[..., :3] = np.clip(WATER_COLOUR * brightness / max(float(brightness.mean()), 1e-6), 0, 1)
	surface[..., 3] = WATER_OPACITY
	# <!-- custom: In game, water plots show scattered white glints even without a bonus, about 0.04% of a Coast view's pixels in a 2026-11-09 screenshot; sprinkle a fixed few, the same in every render. (Claude code Opus 5.5) -->
	# <!-- custom: They vary in size, shape and brightness and lie unevenly: first drawn as ten equal 2 by 3 dashes, they looked too regular and too many. (Claude code Opus 5.5) -->
	rng = np.random.default_rng(4)
	rows, columns = np.mgrid[0:surface.shape[0], 0:surface.shape[1]]
	for _ in range(7):
		row, column = rng.uniform(0, surface.shape[0], 2)
		across, along, angle = rng.uniform(0.6, 1.6), rng.uniform(1.0, 3.2), rng.uniform(0, np.pi)
		u = (columns - column) * np.cos(angle) + (rows - row) * np.sin(angle)
		v = (rows - row) * np.cos(angle) - (columns - column) * np.sin(angle)
		glint = np.clip(1.2 - (u / along) ** 2 - (v / across) ** 2, 0, 1) * rng.uniform(0.5, 0.95)
		surface[..., :3] = surface[..., :3] * (1 - glint[..., None]) + np.array([0.95, 0.97, 1.0]) * glint[..., None]
		surface[..., 3] = np.maximum(surface[..., 3], glint)
	return surface


def river_pieces(assets):
	# <!-- custom: The river pieces of CIV4RiverModelInfos.xml, the mod's first: each model joins the plot edges its <Connections> lists, such as "N S" for a straight run. (Claude code Opus 5.5) -->
	for _, path in assets.xml_files("Art", "rivermodelinfos"):
		text = path.read_bytes().decode("latin-1")
		return [(field(body, "ModelFile"), (field(body, "Connections") or "").split()) for body in re.findall(r"<RiverModelInfo>(.*?)</RiverModelInfo>", text, re.DOTALL)]
	return []


def flood_texture(sheet, mask, uvs):
	# <!-- custom: The flood plain sheet has the river sheet's layout, a green band around each river piece, so the river piece's own texture coordinates place it along that river.
	# The engine thins it with its mask texture laid once over the piece, which leaves the desert gaps in-game screenshots show between the green patches. (Claude code Opus 5.5) -->
	painted = sheet.copy()
	h, w = sheet.shape[:2]
	left, top = int(uvs[:, 0].min() * w), int(uvs[:, 1].min() * h)
	right, bottom = int(round(uvs[:, 0].max() * w)), int(round(uvs[:, 1].max() * h))
	thinning = np.asarray(Image.fromarray((mask[..., :3].mean(axis=2) * 255).astype(np.uint8)).resize((right - left, bottom - top)), dtype=np.float32) / 255.0
	painted[top:bottom, left:right, 3] *= thinning
	return painted


def river_meshes(assets, cache, args, size, surface, flood):
	# <!-- custom: A straight river piece along the plot's east edge, as rivers run along plot edges in game, repeated to cross the ground; with flood, the flood plain band under it.
	# The river texture is the one the engine uses, RIVER_BASE_TEXTURE in CIV4ArtDefines_Misc.xml, and the flood plain's RIVER_FLOOD_PLAIN_TEXTURE and its mask. (Claude code Opus 5.5) -->
	straight = next((model for model, joins in river_pieces(assets) if sorted(joins) == ["N", "S"]), None)
	if straight is None:
		raise SystemExit("%s has no straight river piece in CIV4RiverModelInfos.xml" % (assets.mod_assets or "the base game"))
	misc = assets.art_defines("RIVER_*")
	water = texture_array(assets.stage(misc["RIVER_BASE_TEXTURE"]["Path"], cache)[0])
	if flood:
		sheet = texture_array(assets.stage(misc["RIVER_FLOOD_PLAIN_TEXTURE"]["Path"], cache)[0])
		mask = texture_array(assets.stage(misc["RIVER_FLOOD_PLAIN_MASK_TEXTURE"]["Path"], cache)[0])
	reach = size * GROUND_REACH
	meshes = []
	# <!-- custom: The pieces' small shapes of up to 8 vertices drew as stray squares; only the river plane and its wisps are kept. (Claude code Opus 5.5) -->
	pieces = [mesh for mesh in model_meshes(assets, cache, args, straight) if len(mesh[0]) > 8]
	plane = max(pieces, key=lambda mesh: len(mesh[0]))
	for offset in (-size, 0.0, size):
		for points, uvs, triangles, texture, blend, threshold in pieces:
			placed = points + np.array([size / 2, offset, 0])
			centres = placed[triangles].mean(axis=1)
			keep = (np.abs(centres[:, 0]) < reach) & (np.abs(centres[:, 1]) < reach)
			if not keep.any():
				continue
			# <!-- custom: Keep only the vertices of kept triangles: the cut-off ones still counted when framing the camera and shrank the plot in the picture. (Claude code Opus 5.5) -->
			used = np.unique(triangles[keep])
			renumber = np.zeros(len(placed), dtype=int)
			renumber[used] = np.arange(len(used))
			placed, kept_uvs, kept = placed[used], uvs[used], renumber[triangles[keep]]
			placed[:, 2] = surface_height(placed, surface)
			if points is plane[0]:
				if flood:
					meshes.append((placed + np.array([0, 0, 0.4]), kept_uvs, kept, flood_texture(sheet, mask, uvs), True, 0.0))
				texture = water
			elif texture is not None:
				# <!-- custom: The wisps at a third of their strength: in game they animate, so a still picture catches only part of them, sparse thin white zigzags along the middle of the flow (2026-11-09 screenshots), while at full strength they drew dense white blobs over the whole river. (Claude code Opus 5.5) -->
				texture = np.array(texture, dtype=np.float32)
				texture *= 0.33
			meshes.append((placed + np.array([0, 0, 0.8]), kept_uvs, kept, texture, blend, threshold))
	return meshes


def build(assets, cache, args, terrain, feature, plot):
	size = float(assets.define("PLOT_SIZE") or 180)
	terrains = assets.infos("Terrain", "terraininfos", "TerrainInfo")
	if terrain not in terrains:
		raise SystemExit("%s is not a terrain of %s: %s" % (terrain, args.mod, ", ".join(terrains)))
	tag = field(terrains[terrain], "ArtDefineTag")
	art = assets.art_defines(tag)[tag]
	tile = terrain_tile(assets.stage(art["Path"], cache)[0])
	if art.get("Detail"):
		tile = with_detail(tile, texture_array(assets.stage(art["Detail"], cache)[0]))
	water_plot = is_water(terrains[terrain])
	tile = map_light(tile)
	# <!-- custom: The plot's lit ground colour, which a scrolling feature's soft edge fades toward. (Claude code Opus 5.5) -->
	args.ground_colour = tile[..., :3].mean(axis=(0, 1))
	if plot == "peak":
		surface = peak_surface(assets, cache, size)
		art = plot_type_art(assets, terrains, plot)
		rock = overlay_cell(assets.stage(art["Path"], cache)[0], strengthen=False)
		if art.get("Detail"):
			rock = with_detail(rock, texture_array(assets.stage(art["Detail"], cache)[0]))
		# <!-- custom: ART_PEAK_DECAL in CIV4ArtDefines_Misc.xml is four views of a peak from above, snow in their middle; one of them covers the plot. (Claude code Opus 5.5) -->
		decal = texture_array(assets.stage(assets.art_defines("ART_PEAK_DECAL")["ART_PEAK_DECAL"]["Path"], cache)[0])
		decal = decal[:decal.shape[0] // 2, :decal.shape[1] // 2]
		meshes = [ground(size, surface, peak_texture(tile, rock, decal, surface, size), uv_span=size * GROUND_REACH)]
	else:
		# <!-- custom: Hill height chosen by eye against in-game screenshots: at 0.12 of the plot size a hill barely showed under the default camera. (Claude code Opus 5.5) -->
		surface = flat_surface(size, 0.14 * size if plot == "hills" else 0.0, plot == "hills")
		meshes = [ground(size, surface, tile)]
	if plot == "hills":
		# <!-- custom: Hills are the base terrain with the Hill terrain's overlay on top, as in game, where plains hills are sandy-brown ground cut by grey rock streaks.
		# The first previews used the grassy Hills_GrassA.nif mounds and a hill decal blended toward the middle, which looked nothing like in-game hills. (Claude code Opus 5.5) -->
		points, uvs, triangles, _, _, _ = ground(size, surface, None)
		meshes.append((points + np.array([0, 0, 0.3]), uvs, triangles, overlay_cell(assets.stage(plot_type_art(assets, terrains, plot)["Path"], cache)[0]), True, 0.0))
	if water_plot:
		# <!-- custom: The engine draws water as a surface over the terrain texture; lower the ground and cover it with a translucent plane, so a Fish or ship sits in water rather than in sand. (Claude code Opus 5.5) -->
		points, uvs, triangles, texture, blend, threshold = meshes[0]
		meshes[0] = (points - np.array([0, 0, 0.06 * size]), uvs, triangles, texture, blend, threshold)
		meshes.append(ground(size, flat_surface(size, 0.0, False), None)[:3] + (water_surface(assets, cache), True, 0.0))
	stand = standing_height(meshes, size)
	features = assets.infos("Terrain", "featureinfos", "FeatureInfo")
	# <!-- custom: A river runs along the plot's edge with --river, or when the feature needs one, as Flood Plains do through <bRequiresRiver>. (Claude code Opus 5.5) -->
	needs_river = bool(feature) and field(features.get(feature), "bRequiresRiver") == "1"
	if getattr(args, "river", False) or needs_river:
		meshes += river_meshes(assets, cache, args, size, surface, flood=needs_river and feature_is_decal(assets, features, feature))
	if feature and not (needs_river and feature_is_decal(assets, features, feature)):
		meshes += feature_meshes(assets, cache, args, terrain, feature, size, surface)
	return meshes, size, stand


def feature_is_decal(assets, features, feature):
	# <!-- custom: Flood Plains' art piece is a texture rather than a model; the engine paints it along the river, which river_meshes does. (Claude code Opus 5.5) -->
	body = assets.art_body(field(features[feature], "ArtDefineTag")) or ""
	return all(model.lower().endswith(".dds") for model in re.findall(r"<ModelFile>\s*([^<]+?)\s*</ModelFile>", body)) and "<ModelFile>" in body


def feature_meshes(assets, cache, args, terrain, feature, size, surface):
	features = assets.infos("Terrain", "featureinfos", "FeatureInfo")
	if feature not in features:
		raise SystemExit("%s is not a feature of %s: %s" % (feature, args.mod, ", ".join(features)))
	body = assets.art_body(field(features[feature], "ArtDefineTag"))
	varieties = re.findall(r"<FeatureVariety>(.*?)</FeatureVariety>", body or "", re.DOTALL)
	if not varieties:
		raise SystemExit("%s has no art pieces" % feature)
	# <!-- custom: The Forest's varieties are leafy, evergreen and snowy.
	# The game picks one from the plot's latitude, as CvPlot::setFeatureType does: varieties * (latitude * 9 / 8) / 90, so with three a Forest is leafy below 27 degrees, evergreen to 53 and snowy beyond, whatever its terrain.
	# Take --variety, else that rule for --latitude, else the snowy one on Tundra and Snow and the first elsewhere. (Claude code Opus 5.5) -->
	index = args.variety
	if index is None and args.latitude is not None:
		index = len(varieties) * (abs(args.latitude) * 9 // 8) // 90
	if index is None:
		snowy = [k for k, variety in enumerate(varieties) if "snow" in variety.lower()]
		index = snowy[0] if snowy and terrain in ("TERRAIN_TUNDRA", "TERRAIN_SNOW") else 0
	pieces = re.findall(r"<ModelFile>\s*([^<]+?)\s*</ModelFile>\s*<Connections(?:/>|>([^<]*)</Connections>)", varieties[min(index, len(varieties) - 1)])
	if field(body, "TileArtType") == "TILE_ART_TYPE_HALF_TILING":
		# <!-- custom: Half-tiling features such as Ice are drawn as pieces on the plot's corners, each filling the quarters its Connections name among the four plots around that corner.
		# A lone plot takes, on each corner, the piece joining only toward itself, which gives its cliffs on every side as in-game ice floes show.
		# The first preview took the piece joining the most, the inside of a large ice cap, which drew a flat white square. (Claude code Opus 5.5) -->
		joins = dict((tuple(sorted(connections.split())), model) for model, connections in pieces)
		meshes = []
		for dx, dy, toward in ((1, 1, "SW"), (-1, 1, "SE"), (1, -1, "NW"), (-1, -1, "NE")):
			if (toward,) not in joins:
				raise SystemExit("%s has no half-tiling piece joining only %s" % (feature, toward))
			for points, uvs, triangles, texture, blend, threshold in model_meshes(assets, cache, args, joins[(toward,)]):
				placed = points + np.array([dx * size / 2, dy * size / 2, 0])
				placed[:, 2] += surface_height(placed, surface)
				meshes.append((placed, uvs, triangles, texture, blend, threshold))
		return meshes
	# <!-- custom: A piece is chosen by which neighbouring plots share the feature; the one joining the most, such as the Forest's "NW NE SE SW", fits a plot inside a larger patch. (Claude code Opus 5.5) -->
	model = max(pieces, key=lambda piece: len(piece[1].split()))[0]
	if model.lower().endswith(".dds"):
		# <!-- custom: A texture laid over the plot, for a texture feature without a river; Flood Plains go along their river instead. (Claude code Opus 5.5) -->
		decal = terrain_tile(assets.stage(model, cache)[0])
		points, uvs, triangles, _, _, _ = ground(size, surface, None)
		points = points + np.array([0, 0, 0.5])
		uvs = (points[:, :2] + size / 2) / size
		keep = np.all((uvs[triangles] >= 0) & (uvs[triangles] <= 1), axis=(1, 2))
		return [(points, uvs, triangles[keep], decal, True, 0.0)]
	effect = billboard_effect(assets, cache, args, model)
	if effect:
		# <!-- custom: The cards face the camera around the plot's middle, so the ground's height there lifts them all alike. (Claude code Opus 5.5) -->
		return [(points + np.array([0, 0, float(surface.at(0.0, 0.0))]), *rest) for points, *rest in model_meshes(assets, cache, args, model, effect, args.plot_time)]
	meshes = []
	scrolling = textures_scroll(assets, cache, args, model)
	pieces = model_meshes(assets, cache, args, model, at=args.plot_time if scrolling else None, scrolling=scrolling)
	# <!-- custom: Lift a model that dips below the ground: the Oasis's pool sits in a bowl about 5 units deep, so our flat ground covered most of its water, while in game the pool shows as a bright turquoise mini lake.
	# The engine sinks the plot's ground there, which is not drawn here. (Claude code Opus 5.5) -->
	sunk = [points[:, 2].min() for points, *_ in pieces if len(points) > 8]
	rise = max(0.0, -min(sunk)) if sunk else 0.0
	for points, uvs, triangles, texture, blend, threshold in pieces:
		lifted = points + np.stack([np.zeros(len(points)), np.zeros(len(points)), surface_height(points, surface) + rise], axis=1)
		meshes.append((lifted, uvs, triangles, texture, blend, threshold))
	return meshes


def describe(terrain, feature, plot):
	# <!-- custom: Hills and peaks are plot types with a terrain under them, so they lead: "hills + TERRAIN_PLAINS". (Claude code Opus 5.5) -->
	return "%s%s%s" % ("" if plot == "flat" else plot + " + ", terrain, " + " + feature if feature else "")


def standing_height(meshes, size):
	# <!-- custom: Where a unit or bonus stands: the highest ground or hill or peak model near the plot's middle, before the feature is added, or a forest would lift it onto the treetops.
	# Standing on the ground's own bump hid the Llama Kamayuq inside the peak's cone. (Claude code Opus 5.5) -->
	points = np.vstack([mesh[0] for mesh in meshes])
	near = np.hypot(points[:, 0], points[:, 1]) < 0.12 * size
	return float(points[near, 2].max()) if near.any() else 0.0


def sheet_jobs(assets):
	# <!-- custom: Every terrain the XML has, flat and, on land, as hills and peak; then every feature on each terrain its <TerrainBooleans> allows, or the fallback land terrain when it lists none, as Fallout, and once on hills unless it requires flatlands.
	# Read from the XML rather than listed, so a mod's own terrains and features, such as Sengoku's graphical-only snow peak terrain, join the sheet. (Claude code Opus 5.5) -->
	terrains = assets.infos("Terrain", "terraininfos", "TerrainInfo")
	land_fallback, _ = fallback_terrains(assets)
	shown = [kind for kind in terrains if kind not in PLOT_TYPE_TERRAINS.values()]
	land = [kind for kind in shown if not is_water(terrains[kind])]
	jobs = []
	for kind in shown:
		jobs += [(kind, None, plot) for plot in (("flat", "hills", "peak") if kind in land else ("flat",))]
	for feature, body in assets.infos("Terrain", "featureinfos", "FeatureInfo").items():
		allowed = [kind for kind in listed(body, "TerrainBooleans", "TerrainType", "bTerrain") if kind in terrains] or [land_fallback]
		jobs += [(kind, feature, "flat") for kind in allowed]
		on_land = [kind for kind in allowed if kind in land]
		if on_land and field(body, "bRequiresFlatlands") != "1":
			jobs.append((on_land[0], feature, "hills"))
	return jobs


def sheet_label(terrain, feature, plot):
	return describe(terrain, feature, plot).replace("TERRAIN_", "").replace("FEATURE_", "").lower()


def labelled_sheet(pictures, columns, path):
	width, height = pictures[0][1].size
	sheet = Image.new("RGB", (width * columns, (height + 14) * ((len(pictures) + columns - 1) // columns)), (20, 20, 20))
	draw = ImageDraw.Draw(sheet)
	for k, (label, picture) in enumerate(pictures):
		x, y = (k % columns) * width, (k // columns) * (height + 14)
		sheet.paste(picture, (x, y))
		draw.text((x + 4, y + height + 1), label, fill=(230, 230, 230))
	sheet.save(path)


def sheet_pictures(assets, mod, scratch, workers, size=200, pattern=None):
	# <!-- custom: Render each plot of sheet_jobs with nif_preview.py, in parallel, labelled as describe() does without the TERRAIN_ and FEATURE_ prefixes, such as "hills + plains"; pattern matches those labels.
	# A failed plot fails the sheet with its error. (Claude code Opus 5.5) -->
	jobs = [job for job in sheet_jobs(assets) if pattern is None or re.search(pattern, sheet_label(*job))]
	if not jobs:
		raise SystemExit("no plot matches %s" % pattern)
	scratch = Path(scratch)
	scratch.mkdir(parents=True, exist_ok=True)

	def render(job):
		terrain, feature, plot = job
		out = scratch / ("plot_%s_%s_%s.png" % (terrain, feature or "none", plot))
		result = subprocess.run([sys.executable, str(Path(__file__).with_name("nif_preview.py")), feature or terrain, str(out), "--mod", mod, "--size", str(size), "--terrain", terrain, "--plot", plot, "--feature", feature or "none"], capture_output=True, text=True, errors="replace")
		return out, None if result.returncode == 0 else (result.stderr.strip() or result.stdout.strip()).splitlines()[-1:]
	with ThreadPoolExecutor(workers) as pool:
		results = list(pool.map(render, jobs))
	pictures = []
	for job, (out, error) in zip(jobs, results):
		if error:
			raise SystemExit("%s: %s" % (describe(*job), error[0] if error else "failed"))
		pictures.append((sheet_label(*job), Image.open(out).convert("RGB")))
	return pictures


def main():
	# <!-- custom: Draw a mod's terrains, plot types and features as one labelled sheet, to see a mod's terrain art without the game, such as Caveman2Cosmos's many terrains. (Claude code Opus 5.5) -->
	# <!-- custom: civ4_assets finds the mod's XML and art, loose or in FPKs, and the base game's under it. (Claude code Opus 5.5) -->
	from civ4_assets import Civ4Assets, default_cache
	parser = argparse.ArgumentParser(description="Draw every terrain of a mod flat, as hills and as a peak, then every feature on the terrains it allows, as one labelled PNG sheet.")
	parser.add_argument("out", help="PNG sheet to write")
	parser.add_argument("--mod", required=True, help="mod folder name under Mods, or an absolute path")
	parser.add_argument("--match", help="only plots whose label matches this regular expression, such as 'peak|forest'")
	parser.add_argument("--size", type=int, default=200, help="each plot's picture size")
	parser.add_argument("--columns", type=int, default=6)
	parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
	args = parser.parse_args()
	assets = Civ4Assets(args.mod)
	pictures = sheet_pictures(assets, args.mod, default_cache(Path(args.mod).name) / "plot_sheet", args.jobs, args.size, args.match)
	labelled_sheet(pictures, args.columns, args.out)
	print("wrote %s: %d plots" % (args.out, len(pictures)))


if __name__ == "__main__":
	main()

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The sample pictures in _1_AdvCiv-SAS/Images/LLM were rendered one by one as the renderer improved, so some fell behind: Grace's still kept the wide eyes of a render made before the bone skinning was fixed, while her GIFs had them right.
# This renders every sample nif_preview.py and art_gallery.py made again, with the commands the Art Tools Guide shows, so they all show the current renderer.
# Base-game files are found through this mod as the game does, so no extracted folders are needed.
# Movie and audio samples come from ffmpeg, which renderer changes do not affect, and composite pictures were assembled by hand; neither is listed.
# See README_Art_Tools.md. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options; concurrent.futures and subprocess render in parallel; fnmatch selects samples; os counts processors; pathlib and sys find the helpers; civ4_assets finds base-game art; Pillow builds the size comparison. (Claude code Opus 5.5) -->
import argparse
from concurrent.futures import ThreadPoolExecutor
import fnmatch
import os
from pathlib import Path
import subprocess
import sys

# <!-- custom: civ4_assets finds base-game and mod art as the game does and gives the cache folder. (Claude code Opus 5.5) -->
from civ4_assets import Civ4Assets, default_cache
# <!-- custom: plot_scene draws the plot sheets and their labelled sheet layout, shared with its own command. (Claude code Opus 5.5) -->
from plot_scene import labelled_sheet

# <!-- custom: Pillow crops and joins the size comparison; fail with the install command if it is missing. (Claude code Opus 5.5) -->
try:
	from PIL import Image, ImageDraw
except ImportError:
	raise SystemExit("Pillow is required: py -m pip install pillow")

HERE = Path(__file__).resolve().parent
# <!-- custom: Helpers now sit in LLM_Helpers folders named by job, so find the repo root from the LLM_Helpers folder instead of a fixed parent depth. (Claude code Opus 5.5) -->
REPO = next(path for path in Path(__file__).resolve().parents if path.name == "LLM_Helpers").parent
IMAGES = REPO / "_1_AdvCiv-SAS" / "Images" / "LLM"
SAS = "Assets/Art/AdvCiv_SAS/"
GRACE = SAS + "LeaderHeads/Grace_O_Malley/nif/"
LAND = "art:Art/Interface/Screens/Civilopedia/AncientBattlefield/AncientBattlefield.nif"
WATER = "art:Art/Interface/Screens/Civilopedia/WaterEnvironment/WaterEnvironment.nif"
SKY = "art:Art/Interface/Screens/Civilopedia/SkyEnvironment/SkyEnvironment.nif"
IMMORTAL = SAS + "Units/Persia_Immortal/nif/persianimmortalarmoreddark.nif"
SPEARMAN = "art:Art/Units/Charlemagne_HeavySpearman/HeavySpearman.kfm"
GANDHI = "art:Art/LeaderHeads/Gandhi/"
MONTEZUMA = "art:Art/LeaderHeads/Montezuma/"

# <!-- custom: Each sample: its file and the nif_preview.py arguments the Art Tools Guide gives for it.
# An "art:" path is a base-game or mod path found as the game would, and "particles:" a folder of the fire sprites the religion scenes use. (Claude code Opus 5.5) -->
SAMPLES = [
	("llm_nif_immortal_current.png", [IMMORTAL, "--yaw", "0", "--pitch", "15", "--size", "280"]),
	("llm_animation_immortal_idle.gif", [SPEARMAN, "--clip", "idle", "--model", IMMORTAL, "--environment", LAND, "--model-scale", "2.15", "--yaw", "-2", "--frame-shift-y", "0.32", "--sway", "14", "--cycles", "2", "--frames", "48", "--size", "280"]),
	("llm_animation_immortal.gif", [SPEARMAN, "--clip", "strikea", "--model", IMMORTAL, "--environment", LAND, "--model-scale", "2.15", "--yaw", "12", "--frame-shift-y", "0.32", "--frames", "24", "--size", "280", "--speed", "0.65"]),
	("llm_nif_scene_frames_daoism.PNG", ["art:Art/Movies/Religion/Taoism/Tao_Found.nif", "--scene-camera", "--frames", "4", "--size", "320"]),
	("llm_animation_daoism.gif", ["art:Art/Movies/Religion/Taoism/Tao_Found.nif", "--scene-camera", "--frames", "36", "--size", "240", "--particle-textures", "particles:"]),
	("llm_animation_christianity.gif", ["art:Art/Movies/Religion/Christianity/Chr_Found.nif", "--scene-camera", "--frames", "36", "--size", "240", "--particle-textures", "particles:"]),
	("llm_kf_frames_llama_run.PNG", [SAS + "Units/Incan_Llama_Kamayuq/nif/llamaarcher.kfm", "--clip", "1010", "--size", "200"]),
	("llm_animation_llama.gif", [SAS + "Units/Incan_Llama_Kamayuq/nif/llamaarcher.kfm", "--clip", "1010", "--frames", "16", "--size", "200", "--speed", "0.6"]),
	("llm_kf_frames_houfnice_strike.PNG", [SAS + "Units/Holy_Roman_Houfnice/nif/cannon.kfm", "--clip", "32113672", "--size", "200"]),
	("llm_animation_houfnice.gif", [SAS + "Units/Holy_Roman_Houfnice/nif/cannon.kfm", "--clip", "32113672", "--environment", LAND, "--model-scale", "2.2", "--pitch", "8", "--frames", "24", "--size", "280", "--speed", "0.8"]),
	("llm_kf_frames_catapult_strike.PNG", ["art:Art/Units/Catapult/Catapult.kfm", "--clip", "1032", "--model", "art:Art/Units/Catapult/Catapult_FX.nif", "--size", "200"]),
	("llm_animation_catapult.gif", ["art:Art/Units/Catapult/Catapult.kfm", "--clip", "1032", "--model", "art:Art/Units/Catapult/Catapult_FX.nif", "--frames", "24", "--size", "200", "--speed", "0.45"]),
	("llm_nif_leaderhead_grace.png", [GRACE + "John II.nif", "--leader-background", GRACE + "mansa_musa_bg.kfm", "--size", "480"]),
	("llm_animation_grace.gif", [GRACE + "John II.kfm", "--clip", "6553600", "--leader-background", GRACE + "mansa_musa_bg.kfm", "--frames", "60", "--size", "230"]),
	("llm_animation_grace_disagree.gif", [GRACE + "John II.kfm", "--clip", "disagree", "--leader-background", GRACE + "mansa_musa_bg.kfm", "--frames", "40", "--size", "230"]),
	("llm_nif_leaderhead_gandhi.png", [GANDHI + "Gandhi_noshader.nif", "--leader-background", GANDHI + "Gandhi_BG.kfm", "--size", "440"]),
	("llm_animation_gandhi_greeting.gif", [GANDHI + "Gandhi.kfm", "--clip", "0", "--model", GANDHI + "Gandhi_noshader.nif", "--leader-background", GANDHI + "Gandhi_BG.kfm", "--frames", "24", "--size", "200"]),
	("llm_animation_gandhi_refusal.gif", [GANDHI + "Gandhi.kfm", "--clip", "6", "--model", GANDHI + "Gandhi_noshader.nif", "--leader-background", GANDHI + "Gandhi_BG.kfm", "--frames", "24", "--size", "200"]),
	("llm_animation_montezuma.gif", [MONTEZUMA + "Montezuma.kfm", "--clip", "0", "--model", MONTEZUMA + "Montezuma_noshader.nif", "--leader-background", MONTEZUMA + "Montezuma_BG.kfm", "--frames", "30", "--size", "200"]),
	("llm_animation_montezuma_disagree.gif", [MONTEZUMA + "Montezuma.kfm", "--clip", "disagree", "--model", MONTEZUMA + "Montezuma_noshader.nif", "--leader-background", MONTEZUMA + "Montezuma_BG.kfm", "--frames", "30", "--size", "200"]),
	("llm_nif_bonus_pig.png", ["art:Art/Terrain/Resources/Pig/Pig.nif", "--size", "220"]),
	("llm_animation_pig.gif", ["art:Art/Terrain/Resources/Pig/Pig.kfm", "--clip", "normal", "--environment", LAND, "--model-scale", "5", "--model-offset", "0", "0", "40", "--sway", "8", "--frames", "56", "--size", "280", "--speed", "1.25"]),
	("llm_animation_fish.gif", ["art:Art/Terrain/Resources/Fish/Fish.kfm", "--clip", "normal", "--environment", WATER, "--model-scale", "1.6", "--model-offset", "0", "-45", "0", "--water-opacity", "0.55", "--opacity-gain", "2.7", "--sway", "8", "--frames", "56", "--size", "280"]),
	("llm_animation_whale.gif", ["art:Art/Terrain/Resources/Whale/Whale.kfm", "--clip", "normal", "--environment", WATER, "--model-scale", "1.35", "--model-offset", "0", "-28", "0", "--water-opacity", "0.55", "--frames", "50", "--size", "280"]),
	("llm_animation_bomber.gif", ["art:Art/Units/Bomber/Bomber.kfm", "--clip", "idle", "--model", "art:Art/Units/Bomber/Bomber_FX.nif", "--environment", SKY, "--model-offset", "55", "-70", "-490", "--pitch", "20", "--sway", "26", "--cycles", "36", "--frames", "157", "--size", "240"]),
	("llm_animation_fallout.gif", ["FEATURE_FALLOUT", "--mod", REPO.name, "--frames", "32", "--size", "280"]),
	("llm_animation_oasis.gif", ["FEATURE_OASIS", "--mod", REPO.name, "--frames", "40", "--size", "400"]),
	("llm_animation_building_ziggurat.gif", ["BUILDING_SUMERIAN_ZIGGURAT", "--mod", REPO.name, "--orbit", "60", "--frames", "64", "--size", "300"]),
	("llm_animation_building_drydock.gif", ["BUILDING_DRYDOCK", "--mod", REPO.name, "--orbit", "60", "--frames", "64", "--size", "300"]),
	("llm_mod_hr_alexander_greeting.gif", ["ART_DEF_LEADER_ALEXANDER", "--mod", "History Rewritten", "--clip", "greeting", "--frames", "24", "--size", "200"]),
	("llm_mod_ri_apache_raiders_idle.gif", ["ART_DEF_UNIT_APACHE_RAIDERS", "--mod", "Realism Invictus", "--clip", "idle", "--frames", "24", "--size", "200", "--orbit", "360", "--environment", "none"]),
]
GALLERY = "llm_gallery_civgold_leaders.png"
# <!-- custom: The other art_gallery.py examples of the Art Tools Guide: a mod's Ancient buildings, and the beasts of a mod with many monsters. (Claude code Opus 5.5) -->
BUILDINGS = "llm_gallery_sas_ancient_buildings.png"
BEASTS = "llm_gallery_erebus_beasts.png"
OTHER_GALLERIES = {
	BUILDINGS: ["--mod", REPO.name, "--pattern", "ART_DEF_BUILDING_*", "--era", "ancient", "--limit", "20", "--labels", "--size", "200", "--jobs", "1"],
	BEASTS: ["--mod", "Ashes of Erebus", "--pattern", "ART_DEF_UNIT_*", "--combat", "beast,animal", "--limit", "20", "--labels", "--size", "200", "--jobs", "1"],
}
FEMALE = "llm_search_female_units.png"
# <!-- custom: The art_search.py example for units: units across the installed mods whose Types name women, so an agent can look for such art. (Claude code Opus 5.5) -->
FEMALE_PATTERN = "FEMALE_(PROPHET|GREAT)|AMAZON|VALKYR|MAIDEN|_ONNA|GEISHA|BLADEDANCER|MERMAID|SORCERESS|WISE_WOMAN|PRIESTESS|HEROINE|LADY$|MOBIUS_WITCH|WITCH_MISSIONARY"
FUTURE = "llm_search_future_buildings.png"
# <!-- custom: The art_search.py example of hunting for art to use: labs, farms and embassies across the installed mods, for ideas for a future era. (Claude code Opus 5.5) -->
FUTURE_PATTERN = "QUANTUM_LAB|QUANTUM_SUPERCOMPUTER|EXPERIMENTAL_QUANTUM|SCIENCE_QUANTUM|BIODOME|BIOFARM|BIOLAB|GENE_FARMING|HYDROPONIC|AGRODOME|DIGITAL_EMBASSY|ALIEN_EMBASSY|ARCOLOGY$|CLONING|FUSION_?PLANT|FUSION_REACTOR|SUPERCOLLIDER|COLLIDER|NANOFACTORY|NANOTECH_COMPLEX|NANOPUTER|MEGANANO|ORBITAL_RING|ORBITAL_FACTORY|ORBITAL_OBSERVATORY|ANDROID_FACTORY|ROBOTICS_LAB|ROBOT_FACTORY|PRIME_ROBOT|ANTIMATTER_?(PLANT|FACTORY)|HOLODECK|HOLO_COMBAT|SURVIVAL_DOME|GEODESIC_DOME|RESEARCH_LAB|SINGULARITY_BRAIN"
WONDERS = "llm_search_ancient_wonders.png"
# <!-- custom: The art_search.py example for buildings: Ancient wonders whose art differs from the base game's, in three mods. (Claude code Opus 5.5) -->
WONDERS_PATTERN = "PYRAMID|STONEHENGE|ORACLE|LIGHTHOUSE|HANGING"
WONDERS_MODS = ["Caveman2Cosmos", "History Rewritten", "Realism Invictus"]
SIZE_COMPARISON = "llm_nif_resolution_gandhi.png"
PLOTS = "llm_plot_previews.png"
TERRAINS = "llm_plot_terrains.png"
FALLOUT = "llm_plot_fallout.png"
MARSHES = "llm_search_marshes.png"
# <!-- custom: The art_search.py example of the Art Tools Guide: marsh-like terrains and features across the installed mods. (Claude code Opus 5.5) -->
MARSH_PATTERN = "MARSH|SWAMP|WETLAND|BOG|MANGROVE|MUD"
# <!-- custom: Left out of this sample by the maintainer's choice: RFC Dawn of Civilization (see its section in LICENSE.md), and Dawn of Civilization: America, whose bog and swamp models are byte-identical to RFC Dawn of Civilization's marsh models under other names. (Claude code Opus 5.5) -->
MARSH_EXCLUDED = ["RFC Dawn of Civilization", "DOCAmerica-0.0.15"]
EFFECTS = "llm_search_effects.png"
# <!-- custom: Other mods' animated features, which the plot preview finds in their models rather than from a list: glowing cards, fog, storms, meteors and volcanoes. (Claude code Opus 5.5) -->
EFFECTS_PATTERN = "HAUNTED|QUASAR|^FEATURE_RADIATION$|^FEATURE_STORM$|SANDSTORM|^FEATURE_BLIZZARD$|NEBEL|^FEATURE_MIST$|VOLCANO|METEORS"
EFFECTS_MODS = ["Caveman2Cosmos", "Master of Mana", "Rise of Mankind", "Chronicles of Mankind", "The Eugenics Wars", "Ashes of Erebus", "Pie'sAncientEurope", "Sengoku"]
SCALE = "llm_scene_unit_scale.png"
# <!-- custom: Units in their Sevopedia scenes at their art define's size: futuremod's Warbot is its Assault Mech's model at a quarter of the size, and the Frigate outsizes the Galley. (Claude code Opus 5.5) -->
SCALE_SAMPLES = [("futuremod", "ART_DEF_UNIT_ASSAULT_MECH"), ("futuremod", "ART_DEF_UNIT_WARBOT"), (REPO.name, "ART_DEF_UNIT_GALLEY"), (REPO.name, "ART_DEF_UNIT_FRIGATE")]
# <!-- custom: Plot previews on one labelled sheet: features, plot types, bonuses and an improvement on the plot their XML allows first, Iron forced onto hills, and units standing on desert and plains hills. (Claude code Opus 5.5) -->
PLOT_SAMPLES = [
	("FEATURE_MARSH", []), ("FEATURE_FOREST", []), ("FEATURE_FLOOD_PLAINS", []), ("TERRAIN_HILL", []),
	("TERRAIN_PEAK", []), ("BONUS_DEER", []), ("BONUS_IRON", ["--plot", "hills"]), ("IMPROVEMENT_FISHING_BOATS", []),
	("ART_DEF_UNIT_INCAN_LLAMA_KAMAYUQ", ["--terrain", "TERRAIN_DESERT", "--plot", "hills"]), ("ART_DEF_UNIT_WARRIOR", ["--terrain", "TERRAIN_PLAINS", "--plot", "hills"]),
]


class Resolver:
	def __init__(self):
		self.assets = Civ4Assets(str(REPO))
		self.cache = default_cache(REPO.name)

	def __call__(self, value):
		if value.startswith("art:"):
			return str(self.assets.stage(value[4:], self.cache)[0])
		if value == "particles:":
			# <!-- custom: The religion scenes' fire sprites are Art/Shared/fx_fire*.dds; copy only those rather than all of Art/Shared. (Claude code Opus 5.5) -->
			folder = self.cache / "particles"
			folder.mkdir(parents=True, exist_ok=True)
			for layer in self.assets.layers:
				for name in layer.names_in("art/shared"):
					if fnmatch.fnmatch(name, "fx_fire*.dds") and not (folder / name).exists():
						(folder / name).write_bytes(layer.read("art/shared/" + name))
			return str(folder)
		return str(REPO / value) if value.startswith("Assets/") else value


def run(command):
	result = subprocess.run(command, capture_output=True, text=True, errors="replace", cwd=REPO)
	return None if result.returncode == 0 else (result.stderr.strip() or result.stdout.strip()).splitlines()[-1:]


def plot_sheet(scratch):
	pictures = []
	for subject, extra in PLOT_SAMPLES:
		out = scratch / ("plot_%s.png" % subject.lower())
		result = subprocess.run([sys.executable, str(HERE / "nif_preview.py"), subject, str(out), "--mod", REPO.name, "--size", "200"] + extra, capture_output=True, text=True, errors="replace", cwd=REPO)
		if result.returncode:
			return (result.stderr.strip() or result.stdout.strip()).splitlines()[-1:]
		# <!-- custom: Label with the plot nif_preview.py reports, so TERRAIN_HILL reads "hills + grass", the plot type over its terrain, rather than the subject alone. (Claude code Opus 5.5) -->
		plot = next(line[6:] for line in result.stdout.splitlines() if line.startswith("plot: "))
		label = "%s: %s" % (subject.replace("ART_DEF_UNIT_", "").replace("IMPROVEMENT_", "").replace("FEATURE_", "").replace("TERRAIN_", "").replace("BONUS_", "").lower(), plot.replace("TERRAIN_", "").replace("FEATURE_", "").lower())
		pictures.append((label, Image.open(out).convert("RGB")))
	labelled_sheet(pictures, 5, IMAGES / PLOTS)
	return None


def terrain_sheet(resolve, scratch, workers):
	# <!-- custom: plot_scene.py draws the sheet from the XML, as its own command does for any mod. (Claude code Opus 5.5) -->
	import plot_scene
	labelled_sheet(plot_scene.sheet_pictures(resolve.assets, REPO.name, scratch / "terrains", workers), 6, IMAGES / TERRAINS)
	return None


def fallout_sheet(scratch):
	# <!-- custom: Fallout's light swells and fades, so one still cannot show it: a strip from none to its brightest, and 50% on Desert, the moment the terrain sheet shows. (Claude code Opus 5.5) -->
	pictures = []
	for terrain, glow in [("TERRAIN_GRASS", glow) for glow in range(0, 101, 10)] + [("TERRAIN_DESERT", 50)]:
		out = scratch / ("fallout_%s_%d.png" % (terrain.lower(), glow))
		error = run([sys.executable, str(HERE / "nif_preview.py"), "FEATURE_FALLOUT", str(out), "--mod", REPO.name, "--size", "200", "--terrain", terrain, "--glow", str(glow)])
		if error:
			return error
		pictures.append(("%s, %d%% glow" % (terrain.replace("TERRAIN_", "").lower(), glow), Image.open(out).convert("RGB")))
	labelled_sheet(pictures, 6, IMAGES / FALLOUT)
	return None


def scale_sheet(scratch):
	pictures = []
	for mod, art_type in SCALE_SAMPLES:
		out = scratch / ("scale_%s.png" % art_type.lower())
		error = run([sys.executable, str(HERE / "nif_preview.py"), art_type, str(out), "--mod", mod, "--size", "200"])
		if error:
			return error
		pictures.append(("%s (%s)" % (art_type.replace("ART_DEF_UNIT_", ""), "SAS" if mod == REPO.name else mod), Image.open(out).convert("RGB")))
	labelled_sheet(pictures, 4, IMAGES / SCALE)
	return None


def size_comparison(resolve, scratch):
	# <!-- custom: Gandhi's face at about a Sevopedia panel's size and at about a full 4K view, cropped and shown at the same size. (Claude code Opus 5.5) -->
	crops = []
	for size in (300, 1200):
		out = scratch / ("gandhi_%d.png" % size)
		error = run([sys.executable, str(HERE / "nif_preview.py"), resolve(GANDHI + "Gandhi_noshader.nif"), str(out), "--leader-background", resolve(GANDHI + "Gandhi_BG.kfm"), "--size", str(size)])
		if error:
			return error
		image = Image.open(out)
		width, height = image.size
		crop = image.crop((int(width * 0.25), int(height * 0.12), int(width * 0.75), int(height * 0.5))).resize((400, 304), Image.LANCZOS)
		draw = ImageDraw.Draw(crop)
		draw.rectangle((0, 0, 170, 16), fill=(0, 0, 0))
		draw.text((4, 2), "--size %d (%s)" % (size, "panel" if size < 400 else "4K screen"), fill=(255, 255, 255))
		crops.append(crop)
	joined = Image.new("RGB", (800, 304))
	joined.paste(crops[0], (0, 0))
	joined.paste(crops[1], (400, 0))
	joined.save(IMAGES / SIZE_COMPARISON)
	return None


def main():
	parser = argparse.ArgumentParser(description="Render again every Art Tools Guide sample that nif_preview.py or art_gallery.py made, into _1_AdvCiv-SAS/Images/LLM.")
	parser.add_argument("pattern", nargs="?", default="*", help="only samples whose file name matches, such as '*grace*'")
	parser.add_argument("--list", action="store_true", help="list the samples and their commands without rendering")
	parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
	args = parser.parse_args()
	names = [name for name, _ in SAMPLES] + [GALLERY, SIZE_COMPARISON, PLOTS, TERRAINS, FALLOUT, MARSHES, EFFECTS, SCALE, WONDERS, FEMALE, FUTURE] + list(OTHER_GALLERIES)
	chosen = [name for name in names if fnmatch.fnmatch(name.lower(), args.pattern.lower())]
	if not chosen:
		raise SystemExit("no sample matches %s" % args.pattern)
	if args.list:
		for name, arguments in SAMPLES:
			if name in chosen:
				print("%s: nif_preview.py %s" % (name, " ".join('"%s"' % value if " " in value else value for value in arguments)))
		for name, arguments in OTHER_GALLERIES.items():
			if name in chosen:
				print("%s: art_gallery.py %s" % (name, " ".join('"%s"' % value if " " in value else value for value in arguments)))
		if FEMALE in chosen:
			print("%s: art_search.py \"%s\" --kind unit --exclude %s" % (FEMALE, FEMALE_PATTERN, " ".join('"%s"' % mod for mod in MARSH_EXCLUDED)))
		if FUTURE in chosen:
			print("%s: art_search.py \"%s\" --kind building --exclude %s" % (FUTURE, FUTURE_PATTERN, " ".join('"%s"' % mod for mod in MARSH_EXCLUDED)))
		if WONDERS in chosen:
			print("%s: art_search.py \"%s\" --kind building --era ancient --mods %s" % (WONDERS, WONDERS_PATTERN, " ".join('"%s"' % mod for mod in WONDERS_MODS)))
		for name in (GALLERY, SIZE_COMPARISON, PLOTS, TERRAINS, FALLOUT, MARSHES, EFFECTS, SCALE):
			if name in chosen:
				print("%s: %s" % (name, {GALLERY: "art_gallery.py --mod \"CIV Gold\" --limit 20 --labels --size 140", SIZE_COMPARISON: "Gandhi at --size 300 and 1200, cropped", PLOTS: "nif_preview.py --mod %s --size 200 for %s" % (REPO.name, ", ".join(" ".join([subject] + extra) for subject, extra in PLOT_SAMPLES)), TERRAINS: "nif_preview.py --mod %s --size 200 --terrain --plot --feature for every terrain and plot type, then every feature on its allowed terrains" % REPO.name, FALLOUT: "nif_preview.py FEATURE_FALLOUT --glow 0 to 100 on Grassland, and 50 on Desert", MARSHES: "art_search.py \"%s\" --exclude %s" % (MARSH_PATTERN, " ".join('"%s"' % mod for mod in MARSH_EXCLUDED)), EFFECTS: "art_search.py \"%s\" --kind feature --mods %s" % (EFFECTS_PATTERN, " ".join(EFFECTS_MODS)), SCALE: "nif_preview.py --size 200 for %s" % ", ".join("%s --mod %s" % (art_type, mod) for mod, art_type in SCALE_SAMPLES)}[name]))
		return
	resolve = Resolver()
	jobs = []
	for name, arguments in SAMPLES:
		if name in chosen:
			jobs.append((name, [sys.executable, str(HERE / "nif_preview.py"), resolve(arguments[0]), str(IMAGES / name)] + [resolve(value) for value in arguments[1:]]))
	scratch = resolve.cache / "samples"
	scratch.mkdir(parents=True, exist_ok=True)
	if GALLERY in chosen:
		jobs.append((GALLERY, [sys.executable, str(HERE / "art_gallery.py"), str(scratch / "gallery"), "--mod", "CIV Gold", "--limit", "20", "--labels", "--size", "140", "--jobs", "1"]))
	for name, arguments in OTHER_GALLERIES.items():
		if name in chosen:
			jobs.append((name, [sys.executable, str(HERE / "art_gallery.py"), str(scratch / name)] + arguments))
	print("rendering %d sample(s) into %s" % (len(jobs) + (SIZE_COMPARISON in chosen), IMAGES))
	with ThreadPoolExecutor(args.jobs) as pool:
		results = dict(zip([name for name, _ in jobs], pool.map(lambda job: run(job[1]), jobs)))
	# <!-- custom: Writing llm_nif_scene_frames_daoism.PNG once failed with "Invalid argument" and then succeeded alone, as when another program briefly holds the file; retry a failed sample once. (Claude code Opus 5.5) -->
	for name, command in jobs:
		if results[name]:
			results[name] = run(command)
	if GALLERY in chosen and not results[GALLERY]:
		(IMAGES / GALLERY).write_bytes((scratch / "gallery" / "sheet_01.png").read_bytes())
	for name in OTHER_GALLERIES:
		if name in chosen and not results[name]:
			(IMAGES / name).write_bytes((scratch / name / "sheet_01.png").read_bytes())
	if WONDERS in chosen:
		results[WONDERS] = run([sys.executable, str(HERE / "art_search.py"), WONDERS_PATTERN, str(IMAGES / WONDERS), "--kind", "building", "--era", "ancient", "--mods"] + WONDERS_MODS + ["--columns", "5", "--size", "260"])
	if FUTURE in chosen:
		results[FUTURE] = run([sys.executable, str(HERE / "art_search.py"), FUTURE_PATTERN, str(IMAGES / FUTURE), "--kind", "building", "--exclude"] + MARSH_EXCLUDED + ["--columns", "6", "--size", "260"])
	if FEMALE in chosen:
		results[FEMALE] = run([sys.executable, str(HERE / "art_search.py"), FEMALE_PATTERN, str(IMAGES / FEMALE), "--kind", "unit", "--exclude"] + MARSH_EXCLUDED + ["--columns", "6", "--size", "200"])
	if PLOTS in chosen:
		results[PLOTS] = plot_sheet(scratch)
	if TERRAINS in chosen:
		results[TERRAINS] = terrain_sheet(resolve, scratch, args.jobs)
	if FALLOUT in chosen:
		results[FALLOUT] = fallout_sheet(scratch)
	if MARSHES in chosen:
		results[MARSHES] = run([sys.executable, str(HERE / "art_search.py"), MARSH_PATTERN, str(IMAGES / MARSHES), "--exclude"] + MARSH_EXCLUDED)
	if EFFECTS in chosen:
		results[EFFECTS] = run([sys.executable, str(HERE / "art_search.py"), EFFECTS_PATTERN, str(IMAGES / EFFECTS), "--kind", "feature", "--mods"] + EFFECTS_MODS + ["--columns", "6", "--size", "200"])
	if SCALE in chosen:
		results[SCALE] = scale_sheet(scratch)
	if SIZE_COMPARISON in chosen:
		results[SIZE_COMPARISON] = size_comparison(resolve, scratch)
	failed = {name: error for name, error in results.items() if error}
	for name in sorted(results):
		print("  %s %s" % ("FAILED" if name in failed else "ok    ", name + (": " + failed[name][0][:160] if name in failed else "")))
	print("%d rendered, %d failed" % (len(results) - len(failed), len(failed)))
	if not failed and len(chosen) == len(names):
		# <!-- custom: Record the renderer's code fingerprint after a complete, successful run; the art sample freshness CI check compares it with the current code. (Claude code Opus 5.5) -->
		sys.path.insert(0, str(REPO / ".github" / "workflows" / "build" / "documentation"))
		import art_samples
		art_samples.write(REPO)
		print("recorded the renderer fingerprint in %s" % art_samples.FINGERPRINT)
	return 1 if failed else 0


if __name__ == "__main__":
	sys.exit(main())

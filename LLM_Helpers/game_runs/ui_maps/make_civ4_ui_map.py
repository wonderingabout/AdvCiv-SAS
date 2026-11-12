#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Writes civ4_ui_map.json, the map of Civ4's screens: each screen, how to reach it, and its controls with positions, targets and notes, as explored on 2026-11-11 with check_points.py, hover_tooltips.py and capture_dropdowns.py.
# The data lives here as code so each screen reads as one block and the file stays one control per line; edit a screen here and rerun to regenerate the JSON, which also checks that every "to" names an existing screen. (Claude Code Opus 5.5) -->

# <!-- custom: json writes and rereads the map; sys and pathlib find the output. (Claude Code Opus 5.5) -->
# <!-- custom: importlib loads simple_game_scripts.shown_scripts from the parent game_runs/ folder, for the Simple Game map list; it shares that classifier with map_preview_dds.py and the CI check, and ships in GitHub ZIPs, unlike the CI check it was first loaded from. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
_SGS_SPEC = importlib.util.spec_from_file_location("simple_game_scripts", REPO / "LLM_Helpers" / "game_runs" / "simple_game_scripts.py")
if _SGS_SPEC is None or _SGS_SPEC.loader is None:
	raise SystemExit("cannot load LLM_Helpers/game_runs/simple_game_scripts.py")
simple_game_scripts = importlib.util.module_from_spec(_SGS_SPEC)
_SGS_SPEC.loader.exec_module(simple_game_scripts)

OUT = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent / "civ4_ui_map.json")
T = "2026-11-11"
NC = "not clicked: "
copyright = "AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy). (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md). JSON allows no comments, so this notice and the descriptions are fields."
about = ("Civ4's screens, from the main menu to the screens and popups of a game, how to reach each one and where its controls are, explored on %s at 1920x1080 windowed (a 1926x1120 window). "
	"Each control has its window-relative xy, the screen it leads to (to) when clicked, and a short note; a screen's tests list keys or clicks tried and what they did, while the story behind them, quirks and failed tries are in README_Game_Runs.md; controls marked 'not clicked' have real effects, such as starting a game, switching mod, going online or closing Civ4, and were left alone. "
	"desktop_windows.py click --point SCREEN.CONTROL clicks one, such as single_player.load_game. Menu items sit at x 965 from y 575, 45 px apart. "
	"Since 2026-11-12 the setup screens (Simple Game, scenario lists, BTS Content, Load a Mod) fill the window, 85%% wide and its height minus 86 px (KI#1082); their footer OK and GO BACK did not move, and the lists inside were re-measured. "
	"Each control sits on one line so the screens read like tables. These positions change with the resolution or the mod's UI code; re-check them with check_points.py after such a change.") % T


# <!-- custom: Helpers: c builds one control, menu places the nth item of a main menu column, dd one Custom Game dropdown, read_shortcuts the Sevopedia's key lists. (Claude Code Opus 5.5) -->
# <!-- custom: Controls are dicts of mixed values (a list xy, string to and note), typed as such so a type checker accepts both. (Claude code Opus 5.5) -->
def c(xy, to=None, note=""):
	d: dict[str, object] = {"xy": list(xy)}
	if to:
		d["to"] = to
	if note:
		d["note"] = note
	return d


def menu(i):
	return (965, 575 + 45 * i)


def dd(xy, span, note=""):
	d: dict[str, object] = {"xy": list(xy), "span": list(span)}
	if note:
		d["note"] = note
	return d


def read_shortcuts():
	# <!-- custom: The Sevopedia's Shortcuts pages already list every key, so they are read from the mod's text on each run rather than copied, and stay in step when the text changes.
	# Each line is [BOLD]key[\BOLD], tabs, then the action; [H1]/[H2] start a group. (Claude Code Opus 5.5) -->
	import re
	text = (Path(__file__).resolve().parents[3] / "Assets" / "XML" / "Text" / "AdvCiv-SAS_Sevopedia_Lengthy.xml").read_text(encoding="utf-8", errors="replace")
	groups = {}
	for match in re.finditer(r"<Tag>TXT_KEY_SHORTCUTS_([A-Z_]+)_PEDIA</Tag>\s*<English>(.*?)</English>", text, re.S):
		group = match.group(1).lower()
		for line in match.group(2).split("[NEWLINE]"):
			heading = re.search(r"\[H[12]\](.*?)\[\\H[12]\]", line)
			if heading:
				group = "%s: %s" % (match.group(1).lower(), heading.group(1).strip())
			key = re.search(r"\[BOLD\](.*?)\[\\BOLD\]", line)
			if key:
				name = re.sub(r"\[[^\]]*\]", "", key.group(1)).strip()
				action = re.sub(r"\s+", " ", re.sub(r"\[[^\]]*\]", " ", line[key.end():])).strip()
				if name and action:
					groups.setdefault(group, []).append([name, action])
	return groups


# <!-- custom: Item lists shown in Custom Game's dropdowns, and the advisors' tabs, read off screenshots on 2026-11-11. (Claude Code Opus 5.5) -->
MAPS = "aDebugMap Arboria Archipelago Balanced Big_and_Small Boreal BTG_Cross BTG_Grid BTG_Lagoon Continents Custom_Continents Donut Earth2 Equal_Islands_V2_beta Fantasy_Realm Fractal Global_Highlands Great_Plains Hemispheres Highlands Hub Ice_Age Inland_Sea Islands Lakes Maze Medium_and_Small Mirror Mixed_Continents not_too_Big_or_Small Oasis Pangaea Peirce PerfectMongoose Planet_Generator_0_68 Rainforest RandomScriptMap Ring SAS_Large_Facing_Islands SAS_Longworld SAS_Parallel_Lines SAS_Simple_Flat_Grass SAS_Spiky_Avenues Shuffle Team_Battleground Tectonics Terra Tilted_Axis Water Wheel".split()
LEADERS = ["Random", "Alexander III [Phi/Agg]", "Ashoka [Spi/Pro]", "Augustus [Ind/Imp]", "Bismarck [Org/Pro]", "Boudica [Agg/Chm]", "Brennus [Spi/Chm]", "Catherine [Phi/Imp]", "Charlemagne [Org/Imp]", "Churchill [Chm/Pro]", "Cyrus [Chm/Imp]", "Darius I [Fin/Org]", "De Gaulle [Org/Chm]", "Elizabeth [Cre/Fin]", "Ewuare [Spi/Ind]", "Frederick [Phi/Cre]", "Gandhi [Phi/Spi]", "Genghis Khan [Agg/Imp]", "Gilgamesh [Cre/Pro]", "Grace O'Malley [Agg/Fin]", "Hammurabi [Agg/Org]", "Hannibal [Fin/Chm]", "Hatshepsut [Spi/Fin]", "Huayna Capac [Ind/Org]", "Isabella I [Spi/Imp]", "Joao II [Fin/Imp]", "Julius Caesar [Agg/Imp]", "Justinian I [Phi/Ind]", "Kublai Khan [Agg/Cre]", "Lincoln [Phi/Chm]", "Louis XIV [Ind/Cre]", "Mansa Musa [Spi/Fin]", "Mao Zedong [Agg/Pro]", "Mehmed II [Org/Imp]", "Michael Collins [Phi/Org]", "Moctezuma II [Agg/Spi]", "Napoleon [Chm/Imp]", "Pacal II [Ind/Fin]", "Pericles [Phi/Cre]", "Peter [Phi/Org]", "Qin Shi Huang [Ind/Pro]", "Ragnar [Agg/Fin]", "Ramesses II [Spi/Ind]", "Roosevelt [Ind/Chm]", "Saladin [Spi/Chm]", "Shaka [Agg/Org]", "Sitting Bull [Phi/Pro]", "Stalin [Agg/Ind]", "Suleiman [Phi/Imp]", "Suryavarman II [Ind/Cre]", "Tokugawa [Org/Pro]", "Victoria [Fin/Imp]", "Wang Kon [Fin/Pro]", "Washington [Chm/Pro]", "Willem [Cre/Fin]", "Zara Yaqob [Spi/Org]"]
CIVS = ["Random", "Arabia", "Aztec", "Babylon", "Byzantium", "Carthage", "Celtia", "China", "Egypt", "England", "Ethiopia", "France", "Germany", "Greece", "Holy Rome", "Inca", "India", "Ireland", "Japan", "Khmer", "Kingdom of Benin", "Korea", "Mali", "Maya", "Mongolia", "Native America", "Netherlands", "Ottomans", "Persia", "Portugal", "Rome", "Russia", "Scandinavia", "Spain", "Sumer", "United States", "Zululand"]

# <!-- custom: Tab centres read off each advisor's bottom strip on 2026-11-11 (SAS48 game, 1926x1120 window); all sit at y 1091 with EXIT at x 1446.
# The tech tree (F6) has no tabs. (Claude Code Opus 5.5) -->
ADVISOR_TABS = {"f1": [("overview_1", 132), ("overview_2", 390), ("overview_3", 648), ("overview_4", 906), ("finance", 1130)],
	"f2": [("civics", 136), ("religions", 465), ("corporations", 938)],
	"f3": [("relations", 189), ("glance", 520), ("info", 764), ("espionage", 1051)],
	"f4": [("treaties", 182), ("bonuses", 531), ("techs", 832), ("cities", 1092)],
	"f5": [("summary", 170), ("map", 430), ("battles", 668), ("composition", 1032)],
	"f7": [("bfc_1", 134), ("bfc_2", 306), ("territory", 548), ("environment", 899), ("changes", 1228)],
	"f8": [("graph", 75), ("score", 216), ("timeline", 376), ("demographics", 608), ("top_5_cities_wonders", 954), ("statistics", 1262)],
	"f9": [("victories", 103), ("settings", 323), ("resolutions", 543), ("members", 763)]}


# <!-- custom: Screens outside a game, from the main menu down. (Claude Code Opus 5.5) -->
S = {}
S["main_menu"] = {"reach": "start Civ4 with mod=\\AdvCiv-SAS; GO BACK from any first-level screen", "controls": {
	"single_player": c(menu(0), "single_player"), "multiplayer": c(menu(1), "multiplayer"), "hall_of_fame": c(menu(2), "hall_of_fame"),
	"sevopedia": c((945, 710), "sevopedia"), "advanced": c(menu(4), "advanced"),
	"unload_mod": c(menu(5), None, NC + "restarts the game without this mod"), "exit_game": c((80, 1092), None, NC + "closes Civ4")}}
S["single_player"] = {"reach": "main_menu.single_player", "controls": {
	"simple_game": c(menu(0), "simple_game_1_map", "a six-step quick setup"),
	"load_game": c(menu(1), "load_dialog"),
	"bts_content": c(menu(2), "bts_content", "drawn grey but works"),
	"play_scenario": c(menu(3), "scenario_list"), "custom_game": c(menu(4), "custom_game"),
	"custom_scenario": c(menu(5), "scenario_list", "the same list of WorldBuilder saves"),
	"go_back": c((100, 1094), "main_menu")}}
S["load_dialog"] = {"reach": "single_player.load_game", "controls": {
	"folder": c((1000, 136), None, "current folder, such as My Games\\beyond the sword\\Saves\\single"),
	"folder_tree": c((430, 560), None, "folder tree, x 150-710, y 180-956"),
	"file_list": c((1250, 560), None, "saves, newest first, x 724-1770, y 180-956; columns name, size, modified"),
	"filename": c((980, 978), None, "file name field"),
	"ok": c((1732, 978), None, NC + "loads the selected save"), "cancel": c((1732, 1018), "single_player")}}
S["scenario_list"] = {"reach": "single_player.play_scenario or single_player.custom_scenario", "controls": {
	"list": c((460, 600), None, "WorldBuilder saves, x 152-790, y 140-1065 since the 2026-11-12 enlarged setup screen (was x 543-871, y 300-857); see KI#1082"),
	"preview": c((1290, 430), None, "globe, name and map size, x 822-1758 since the 2026-11-12 enlarged setup screen (was x 886-1377)"),
	"ok": c((1857, 1094), None, NC + "starts the scenario"), "go_back": c((100, 1094), "single_player")}}
S["bts_content"] = {"reach": "single_player.bts_content", "controls": {
	"list": c((460, 600), None, "scenarios of other installed mods, each with map size, description and its Mod Folder; x 152-790 since the 2026-11-12 enlarged setup screen. Its title shows raw markup, <COLOR=165,165,165,255>BTS CONTENT</COLOR>, once the header is visible"),
	"ok": c((1857, 1094), None, NC + "loads the other mod's scenario"), "go_back": c((100, 1094), "single_player")}}
S["custom_game"] = {"reach": "single_player.custom_game", "note": "Civ4 remembers these settings for the next custom game, so none was changed.", "controls": {
	"player_rows": c((280, 144), None, "one row per player, 47 px apart from y 144, scrollbar at x 1866; columns: type or name x 280, team x 590, civilization x 1030, leader x 1474, difficulty x 1720"),
	"settings": c((430, 560), None, "dropdowns at x 430: map y 560, size 594, climate 630, sea level 664, era 700, speed 736"),
	"options": c((756, 594), None, "checkboxes at x 756 from y 594, about 35 px apart, in a scrolling column"),
	"victories": c((1398, 560), None, "six checkboxes at x 1398 from y 560, about 35 px apart"),
	"go_back": c((104, 1096), "single_player"),
	"launch": c((1830, 1096), None, NC + "starts the game")}}
S["custom_game"]["list_layout"] = "A dropdown's list opens below its header: 10 items visible, about 26 px apart, the first 35 px below the header; 3 wheel clicks over the list scroll it by 9 items. A second click on the header closes it unchanged."
S["custom_game"]["dropdowns"] = {
	"map": dd((429, 560), (144, 714), "map scripts; the choice adds the script's own options below Speed") | {"items": MAPS},
	"size": dd((429, 595), (144, 714)) | {"items": ["Random", "Arena", "Duel", "Tiny", "Small", "Standard", "Large", "Huge", "SAS24", "SAS32", "SAS40", "SAS48"]},
	"climate": dd((429, 630), (144, 714)) | {"items": ["Random", "Temperate", "Tropical", "Arid", "Rocky", "Cold"]},
	"sea_level": dd((429, 665), (144, 714)) | {"items": ["Random", "Low", "Medium", "High"]},
	"era": dd((429, 700), (144, 714)) | {"items": ["Random", "Ancient", "Classical", "Medieval", "Renaissance", "Industrial", "Modern", "Future"]},
	"speed": dd((429, 735), (144, 714)) | {"items": ["Nitro (165 / 33%)", "Turbo (250 / 50%)", "Quick (330 / 67%)", "Normal (500 / 100%)", "Epic (750 / 150%)", "Marathon (1000 / 200%)", "Slow (1500 / 300%)", "Very Slow (2000 / 400%)"]},
	"row1_team": dd((592, 145), (474, 711), "the user's row") | {"items": ["Team %d" % n for n in range(1, 49)]},
	"row1_leader": dd((1033, 145), (721, 1345), "the wide column: leaders with their two traits") | {"items": LEADERS},
	"row1_civilization": dd((1474, 145), (1354, 1594), "the narrow column") | {"items": CIVS},
	"row1_difficulty": dd((1722, 145), (1602, 1842)) | {"items": ["Rookie", "Settler", "Chieftain", "Warlord", "Noble", "Prince", "Monarch", "Emperor", "Immortal", "Deity", "Deity+"]},
	"row2_type": dd((283, 192), (102, 465), "an AI row's player type") | {"items": ["Open", "AI", "Closed"]}}
S["custom_game"]["controls"]["player_rows"]["note"] = "one row per player, 47 px apart from y 145, scrollbar at x 1866; columns: type or name x 280, team x 592, leader x 1033, civilization x 1474, difficulty x 1722 (the AI rows show it greyed)"
S["custom_game"]["controls"]["options"]["note"] = "27 checkboxes counted at x 757, 35 px apart from y 595, in a panel that scrolls by about 478 px, but only 26 names were read into items, so one is missing; Advanced Start Base Points field at (1332, 560)"
S["custom_game"]["controls"]["options"]["items"] = ['Advanced Start', 'Start Points as Handicap', 'No City Flipping From Culture', 'No City Flipping after Conquest', 'No Barbarians', 'Raging Barbarians', 'Aggressive AI (Legacy)', 'Unrestricted Leaders', 'Random Personalities', 'Choose Religions', 'No Technology Trading', 'No Technology Brokering', 'Permanent Alliances', 'Always War', 'Always Peace', 'One-City Challenge', 'New Random Seed on Reload', 'Lock Modified Assets', 'Rise and Fall', 'True Starts', 'No Tribal Villages', 'No Random Events', 'No Vassal States', 'No City Razing', 'No Animals', 'No Slavery']
S["custom_game"]["map_script_options"] = {
	"about": "A map script adds its own dropdowns below Speed, 35 px apart from y 770, and can grey out Climate or Sea Level when it ignores them. Defaults seen on 2026-11-11, the user's other settings unchanged:",
	"aDebugMap": "none (the user's choice, restored afterwards)",
	"Continents": "World Wrap (Cylindrical), Resources (Standard)",
	"Fractal": "World Wrap (Cylindrical), Resources (Standard)",
	"Pangaea": "Shoreline (Random), World Wrap (Cylindrical), Resources (Standard)",
	"Archipelago": "Landmass Type (Archipelago), World Wrap (Cylindrical), Resources (Standard)",
	"Inland_Sea": "World Wrap (Flat), Resources (Standard)",
	"Tectonics": "Landmass Type (Earthlike (70% water)), Aridity Level (Normal); Climate and Sea Level greyed",
	"PerfectMongoose": "Land Shape (Plate Tectonics), Start (Start Anywhere), World Wrap (Cylindrical); Climate greyed",
	"Planet_Generator_0_68": "Continents (18 continents), Continent separation (Min 10 water tiles), Continent distribution (Around center), Continent shape (Unpredictable), Continent scattering (Rare small islands), Relative continent size (Equal size), Percentage of ocean (More than 60%); Climate and Sea Level greyed",
	"Ring": "Areas Per Player (1 Per Player), Land Shape (Random), Neutral Territory (Random), Isthmus Width (2 Plots Wide), World Wrap (Flat), Resources (Standard)",
	"SAS_Longworld": "LongWorld Height (4 Plots (Recommended)), Width Per Player (12 (Recommended)), Revolving World (WrapX (Recommended))",
	"Earth2": "none"}
S["custom_game"]["controls"]["victories"]["note"] = "checkboxes at x 1400, 35 px apart from y 560: Time, Conquest, Domination, Cultural, Space Race, Diplomatic"
# <!-- custom: Simple Game's six steps, re-mapped on 2026-11-12 after the enlarged setup screen (KI#1082): every list row now has a named control, generated from its item names and row spacing.
# The previous chat edited the JSON directly instead, so a rerun of this generator dropped that work; the data now lives here. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
def slug(text):
	import re
	return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def rows(prefix, names, x, y, step, note=None):
	# <!-- custom: One control per list row, named prefix + slug of its item; note is None (no note), a callable on the item, or a fixed string. (Claude code Opus 5.5) -->
	out = {}
	for i, name in enumerate(names):
		text = note(name) if callable(note) else note
		out[prefix + slug(name)] = c((x, y + step * i), None, str(text or ""))
	return out


# <!-- custom: The map list is derived from the scripts themselves, in Civ4's case-insensitive order, instead of typed here: a script added, removed or hidden from Simple Game changes the rows at once, and the CI check ui_map_sync.py fails until the JSON is regenerated.
# The list's place and capacity follow the box, sized by the SAS_EXE_P_DYNAM_MAIN_MENU_* formula read from GlobalDefines_advciv_sas.xml, so a changed default moves the rows here too; the first version hardcoded 38 rows from y 148. (Claude code Opus 5.5) -->
SIMPLE_MAPS = sorted(simple_game_scripts.shown_scripts(REPO / "PrivateMaps"), key=str.lower)
def simple_game_box(client):
	# <!-- custom: The box sasSetupScreenGetSize computes for this client size, at least the stock 850 x 569 and within the window minus FREE_MIN, as SelfMod.cpp does. (Claude code Opus 5.5) -->
	import re
	xml = (REPO / "Assets" / "XML" / "GlobalDefines_advciv_sas.xml").read_text(encoding="utf-8")
	def define(name):
		found = re.search(r"<DefineName>SAS_EXE_P_DYNAM_MAIN_MENU_%s</DefineName>\s*<iDefineIntVal>(-?\d+)" % name, xml)
		if found is None:
			raise SystemExit("SAS_EXE_P_DYNAM_MAIN_MENU_%s is missing from GlobalDefines_advciv_sas.xml" % name)
		return int(found.group(1))
	size = []
	for side, stock, window in (("WIDTH", 850, client[0]), ("HEIGHT", 569, client[1])):
		free = window - max(0, define(side + "_FREE_MIN"))
		cap = free if free >= stock else window
		size.append(min(max(window * define(side + "_PCT") // 100 + define(side + "_ADD"), stock), cap))
	return size


# <!-- custom: Fixed facts of the theme, measured on the user's 1920 x 1080 capture on 2026-11-12: the window's client area starts 3 px right and 37 px down, the list's first row is centred 56 + 12 px below the box's top and 53 px in from its left, rows are 24 px tall, and the list ends 13 px above the box's bottom. (Claude code Opus 5.5) -->
CLIENT = (1920, 1080)
CLIENT_OFFSET = (3, 37)
LIST_TOP, LIST_BOTTOM, LIST_LEFT, ROW = 56, 13, 53, 24
BOX = simple_game_box(CLIENT)
SIMPLE_MAP_ROWS = (BOX[1] - LIST_TOP - LIST_BOTTOM) // ROW
SIMPLE_MAP_X = CLIENT_OFFSET[0] + (CLIENT[0] - BOX[0]) // 2 + LIST_LEFT
SIMPLE_MAP_Y = CLIENT_OFFSET[1] + (CLIENT[1] - BOX[1]) // 2 + LIST_TOP + ROW // 2
if len(SIMPLE_MAPS) > SIMPLE_MAP_ROWS:
	raise SystemExit("%d scripts are shown in Simple Game, but only %d rows fit at 1920 x 1080 without a scrollbar; re-measure the map list's points (README_Game_Runs.md) or hide a script" % (len(SIMPLE_MAPS), SIMPLE_MAP_ROWS))
SIZE_STOPS = (("Random", 214), ("Arena", 352), ("Duel", 488), ("Tiny", 625), ("Small", 762), ("Standard", 899), ("Large", 1035), ("Huge", 1172), ("SAS24", 1309), ("SAS32", 1446), ("SAS40", 1582), ("SAS48", 1719))
MAP_OPTIONS = (("archipelago__", ["Random", "Snaky Continents", "Archipelago", "Tiny Islands"], ""),
	("btg_cross__", ["Flat", "Cylindrical", "Toroidal"], ""),
	("highlands__", ["Random", "Scattered", "Ridgelines", "Clustered"], ""),
	("pangaea__", ["Random", "Natural", "Pressed", "Solid"], ""),
	("sas_longworld__", ["%d Plots" % n if n != 4 else "4 Plots (Recommended)" for n in range(2, 8)], ""),
	("tectonics__", ["Random", "Earthlike (80% water)", "Earthlike (70% water)", "Earthlike (60% water)", "Pangaea (70% water)", "Lakes (30% water)", "Islands (90% water)", "Mediterranean (45% water)", "Randomized Earth (67% water)", "Randomized Earth (Old World Start)"], ""),
	("planet_generator_0_68__", ["First Time (FT) Random"] + ["FT Random (%s continents)" % r for r in ("1 - 3", "1 - 5", "1 - 7", "2 - 5", "2 - 7", "2 - 13", "2 - 15", "3 - 7", "3 - 13", "3 - 15", "3 - 18")] + ["One continent"] + ["%d continents" % n for n in range(2, 19)], ""),
	("tectonics_aridity__", ["Random", "Arid", "Normal", "Wet", "No ice"], "second option step, SELECT AN ARIDITY LEVEL: "),
	("perfectmongoose__", ["Perlin Noise", "Plate Tectonics"], "SELECT A LAND SHAPE: "))
MAP_OPTIONS[6][1][4] = "FT Random (2 - 5 continents, default)"
SIMPLE_CIVS = ["Random"] + ["%s Empire" % n for n in ("Arabian", "Aztec", "Babylonian", "Byzantine", "Carthaginian", "Celtic", "Chinese", "Dutch", "Egyptian", "English", "Ethiopian", "French", "German", "Greek", "Holy Roman", "Incan", "Indian", "Irish", "Japanese", "Khmer")] + ["Kingdom of Benin"] + ["%s Empire" % n for n in ("Korean", "Mali", "Maya", "Mongolian", "Native American", "Ottoman", "Persian", "Portuguese", "Roman", "Russian", "Scandinavian", "Spanish", "Sumerian")] + ["United States of America", "Zulu Empire"]
step_controls = [rows("map_", SIMPLE_MAPS, SIMPLE_MAP_X, SIMPLE_MAP_Y, ROW),
	dict(list(rows("climate_", ["Random", "Temperate", "Tropical", "Arid", "Rocky", "Cold"], 180, 178, 32).items()) + list(rows("sea_", ["Random", "Low", "Medium", "High"], 509, 178, 32).items()) + [("size_" + slug(name), c((x, 1042), None, "slider stop; clicking the track was not tested")) for name, x in SIZE_STOPS]),
	{},
	dict(list(rows("civ_", SIMPLE_CIVS, 200, 148, 24).items()) + [("leader_%d" % (i + 1), c((1688, 218 + 82 * i), None, "leader portraits of the selected civilization, top to bottom; English shows three")) for i in range(3)]),
	rows("", ["Leader Name", "Civ Description", "Short Description", "Civ Adjective"], 1033, 653, 39),
	dict(list(rows("handicap_", ["Rookie", "Settler", "Chieftain", "Warlord", "Noble", "Prince", "Monarch", "Emperor", "Immortal", "Deity", "Deity Plus"], 180, 178, 24).items()) + [("speed_" + slug(item.split(" (")[0]), c((180, 876 + 24 * i), None, item)) for i, item in enumerate(S["custom_game"]["dropdowns"]["speed"]["items"])])]
for prefix, names, note in MAP_OPTIONS:
	step_controls[2].update(rows(prefix, names, 200, 148, 24, lambda name, note=note: note + name))
steps = [("map", "SELECT A MAP: the map script list, 24 px apart from y 148, with preview and description; all 38 scripts fit, the 38 rows that show at once since the 2026-11-12 enlarged setup screen (KI#1082)"),
	("climate_size", "WORLD SIZE: Climate and Sea Level radio buttons, 32 px apart from y 178, and the World Size slider at y 1042 with 12 stops from Random to SAS48"),
	("map_option", "the map script's own option, a list 24 px apart from y 148: Archipelago and Tectonics landmass type, BTG_Cross world wrap, Highlands mountain pattern, Pangaea shoreline, Planet_Generator_0_68 continents, SAS_Longworld height, PerfectMongoose land shape"),
	("civilization", "SELECT A CIVILIZATION: Random and 36 civilizations, 24 px apart from y 148, all visible since the enlarged setup screen; the leaders column on the right and the selected leader's portrait, traits, units and buildings"),
	("names", "YOUR DETAILS: the leader's portrait, then Leader Name, Civ Description, Short Description and Civ Adjective fields; this box grows only in height and stays about 900 px wide, x 512-1415"),
	("handicap_speed", "GAME SNAPSHOT: Handicap list, 24 px apart from y 178, Game Speed list from y 876, and a summary of map, size, climate, sea level, era and the player's details")]
keys = ["simple_game_%d_%s" % (n, t) for n, (t, _d) in enumerate(steps, 1)]
for n, (title, desc) in enumerate(steps, 1):
	ok = c((1857, 1094), None, NC + "starts the game") if n == 6 else c((1857, 1094), keys[n])
	back = c((100, 1094), "single_player" if n == 1 else keys[n - 2])
	S[keys[n - 1]] = {"reach": "single_player.simple_game, then OK %d time(s)" % (n - 1), "shows": desc, "controls": dict(list(step_controls[n - 1].items()) + [("ok", ok), ("go_back", back)])}
S["simple_game_3_map_option"]["about"] = "Mapped on 2026-11-12 for popular scripts; controls are named SCRIPT__OPTION. Continents, Earth2, Fractal and Inland_Sea have no option step: their OK leads straight to simple_game_4_civilization. A script can also have several option steps, each its own screen at this position: Tectonics asks for its landmass type, then an aridity level, so count its OKs accordingly. Each script remembers its last choice, so the selected row is not always the default."
S["multiplayer"] = {"reach": "main_menu.multiplayer", "controls": {
	"lan_games": c(menu(0), "lan_lobby"), "gamespy_lobby": c(menu(1), None, NC + "the old online service; drawn grey"),
	"hot_seat": c(menu(2), "hot_seat"), "play_by_email": c(menu(3), "play_by_email"), "go_back": c((100, 1094), "main_menu")}}
S["lan_lobby"] = {"reach": "multiplayer.lan_games", "controls": {
	"name": c((371, 100), None, "player name field"), "game_name": c((157, 197), None, "name of a game to create"),
	"new_game": c((157, 234), None, NC + "hosts a game on the local network"), "new_scenario": c((157, 274), None, "not clicked"),
	"load_game": c((157, 320), None, "not clicked"), "refresh_list": c((157, 360), None, "not clicked"),
	"games": c((1070, 580), None, "LAN games, x 286-1857, y 157-1000; columns name, players, map, new, PB, host ping"),
	"go_back": c((103, 1094), "multiplayer"), "join_game": c((1820, 1094), None, NC + "joins the selected game")}}
for k in ("hot_seat", "play_by_email"):
	S[k] = {"reach": "multiplayer." + k, "controls": {
		"new_game": c(menu(0), None, "not explored further"), "new_scenario": c(menu(1), None, "not explored further"),
		"load_game": c(menu(2), None, "drawn grey; not explored further"), "go_back": c((100, 1094), "multiplayer")}}
S["hall_of_fame"] = {"reach": "main_menu.hall_of_fame", "controls": {
	"filters_row_1": c((557, 123), None, "dropdowns at y 123: leaders x 557, difficulties 829, starting eras 1100, single player 1366"),
	"filters_row_2": c((557, 171), None, "dropdowns at y 171: victories x 557, world sizes 829, game speeds 1100, normalized score 1366"),
	"table": c((960, 640), None, "finished games, y 214-1071: leader, normalized score, finish date, score, victory, handicap, size, start era, speed"),
	"legend": c((1863, 60), None, "not clicked"), "exit": c((1863, 1091), "main_menu")}}
S["advanced"] = {"reach": "main_menu.advanced", "controls": {
	"about_this_build": c(menu(0), "about_this_build"), "load_a_mod": c(menu(1), "load_a_mod"), "options": c(menu(2), "options"),
	"check_for_updates": c(menu(3), None, NC + "goes online; drawn grey"), "credits": c(menu(4), "credits", "labelled CREDITS (BTS)"),
	"go_back": c((100, 1094), "main_menu")}}
S["about_this_build"] = {"reach": "advanced.about_this_build", "shows": "Civ version 319, save version 19119, build 3.1.9.0 (128105), build date May 29 2014, FINAL RELEASE, mod name", "controls": {"ok": c((963, 731), "advanced")}}
S["options"] = {"reach": "advanced.options, or ingame_menu: Options (the same window over a game)", "note": "Nothing was changed except Numbers on City Bar, switched on and back off; these are the user's profile settings, saved for every game.", "controls": {
	"tab_controls": c((618, 328), None, "Turn Sequence (Wait at End of Turn: on, which is why Enter is needed once all units moved; Minimize Pop-Ups), Unit Controls, Rival Moves, Automation, Recommendations; Language; the BUG Menu button"),
	"tab_graphics": c((702, 328), None, "full-screen mode, resolution, quality, globe and movie settings; Disable Animations, Unit Graphics and Visual Aids checkboxes in the right column"),
	"tab_audio": c((776, 328), None, "master volume with No Sound; music, sound effects, speech, ambience and interface sliders, each with Mute; speakers, custom music folder, voice chat"),
	"tab_other": c((840, 328), None, "Clock (on, 24 hour, alarm) and Option Profiles (choose, create, delete); no Restore Defaults here"),
	"numbers_on_city_bar": c((1113, 756), None, "Graphics tab, last Visual Aids box: turns to grow and production turns on every city bar, taking effect at once; AdvCiv's rename of Detailed City Info"),
	"bug_menu": c((1070, 772), "bug_menu", "Controls tab"),
	"restore_defaults": c((925, 828), None, NC + "resets the user's options on that tab"), "exit": c((1036, 830), "advanced")}}
S["bug_menu"] = {"reach": "options.bug_menu, or ingame_menu: BUG Menu", "shows": "12 tabs of BUG settings; every field with its label, configured default and storage is in ui_maps/bug_options.txt, from export_bug_options.py", "controls": {
	"tabs": c((540, 272), None, "tab names along y 272: General x 540, Map 604, City Screen 682, Advisors 776, Alerts 850, Scores 914, Time 976, Unit Icons 1054, Odds 1130, Unit Names 1210, Autolog 1302, System 1380"),
	"help": c((922, 888), None, "BUG Mod Help"), "exit": c((1034, 888), None, "closes the BUG menu")}}
S["load_a_mod"] = {"reach": "advanced.load_a_mod", "controls": {
	"list": c((460, 600), None, "installed mods, the current one selected, preview on the right; x 152-790 since the 2026-11-12 enlarged setup screen"),
	"ok": c((1857, 1094), None, NC + "switches mod and restarts the game"), "go_back": c((100, 1094), "advanced")}}
S["credits"] = {"reach": "advanced.credits", "shows": "scrolling credits in a panel", "controls": {"go_back": c((100, 1094), "advanced")}}
S["sevopedia"] = {"reach": "main_menu.sevopedia", "shows": "see the pedia_* points in civ4_points.json and civ4_sevopedia_map.json", "controls": {"exit": c((1866, 1094), "main_menu")}}


# <!-- custom: Screens inside a game: the main screen, the city screen and the advisors. (Claude Code Opus 5.5) -->
S["game_main"] = {"reach": "load or start a game; mapped on 2026-11-11 at turn 200 of a Standard Pangaea game, with a Worker selected",
	"note": "Hovering shows help text at the bottom left, just above the unit panel near (100, 910), growing upwards, only while Civ4 is the foreground window; hover_tooltips.py --front --area 0 420 960 960 captures it. The player is named Autoplay after run_autoplay.py, so the scoreboard and diplomacy say [Autoplay].",
	"controls": {
	"event_log": c((32, 75), None, "Event Log <Ctrl+Tab>"),
	"turn_date": c((110, 52), None, "turn, gold rate and date; era at x 340"),
	"great_general": c((455, 52), None, "Great General progress, such as 6/88 experience"),
	"research_choices": c((715, 52), None, "next research choices as icons at x 715, 748, 785, 825; each shows the tech's effects and turns"),
	"great_person_bar": c((1270, 55), None, "the city closest to its next Great Person, with its progress and the odds of each kind"),
	"gold": c((1755, 52), None, "gold and rate; no help text"),
	"main_menu": c((1878, 52), None, "Open Main Menu: a panel of 11 items at x 1780, 31 px apart from y 207: Exit to Desktop, Exit to Main Menu, Retire, Load Game, Save Game, Options, BUG Menu, Enter WorldBuilder, Game Details, Your Details, Cancel (y 517, closes it); only Cancel was clicked (2026-11-11)"), "sevopedia": c((1905, 52), "sevopedia", "Sevopedia <F12>"),
	"advisor_domestic": c((1650, 79), None, "Domestic Advisor <F1>"), "advisor_policy": c((1678, 79), None, "Policy Advisor <F2>"),
	"advisor_diplomacy": c((1706, 79), None, "Foreign Diplomacy Advisor <F3>"), "advisor_trade": c((1734, 79), None, "Foreign Trade Advisor <F4>"),
	"advisor_military": c((1762, 79), None, "Military Advisor <F5>"), "advisor_technology": c((1790, 79), None, "Technology Advisor <F6>"),
	"advisor_world": c((1818, 79), None, "World Advisor <F7>"), "info_screen": c((1846, 79), None, "Info Screen <F8>"),
	"victory_screen": c((1874, 79), None, "Victory Screen <F9>"), "espionage": c((1902, 79), None, "Espionage Tab <Ctrl+E>"),
	"research_slider": c((1805, 111), None, "research rate buttons at x 1805, 1825, 1845, 1865: +50%, +10%, -10%, -50%; culture at y 133 and espionage at y 155 in the same columns"),
	"scoreboard": c((1700, 715), None, "one row per leader from about y 715, 22 px apart, growing upwards with more players (from about y 670 with 11 on SAS48); hovering shows attitude and its reasons; [Ctrl] opens the trade table, [Alt] declares war"),
	"scoreboard_lock": c((1887, 912), None, "Toggle lock scoreboard hover"),
	"scoreboard_scroll": c((1748, 912), None, "with more players than fit, as on SAS48 in Debug Mode: a row of buttons under the scoreboard, about 22 px apart from x 1748 here: scroll up fast, scroll up, center on the active player, scroll down, scroll down fast, toggle autocenter, then the lock and the background style; the row moved right (from about x 1794) after scrolling, so read it off a screenshot"),
	"scoreboard_style": c((1910, 912), None, "Cycle scoreboard background style: brown, blue-grey, dark navy and the translucent default, at least"),
	"unit_bar": c((1239, 955), None, "units on the selected plot at y 955, about 37 px apart from x 425; the selected one has a yellow frame; Ctrl or Alt with a click selects all of that type or all"),
	"unit_actions": c((432, 1023), None, "the selected unit's actions at y 1023, 52 px apart from x 432; for a Worker: Sleep <F>, Skip Turn <Space>, Go To <G>, Go To same type <Ctrl+G>, Go To all <Alt+G>, Route To <Alt+R>, Build Railroad <R>, Automate improvements <A>, Automate trade network <N>, Improve Nearest City <Shift+Ctrl+C>, Delete <Delete>; they differ by unit"),
	"end_turn": c((1688, 955), None, "End Turn <Shift+Enter>: the green circle; see tests"),
	"city_previous": c((1672, 983), None, "selects the previous city without opening its screen: the map centres on it and the bottom panel shows its production choices, headed by its current item"),
	"city_next": c((1702, 983), None, "selects the next city the same way; both arrows have no help text; the user notes these and the toggle buttons shift slightly with the map's settings, from the mod's layout tweaks, so re-check them on another map: on a SAS48 Pangaea game at turn 100 End Turn sat at about x 1680, the arrows at 1662 and 1696, and the map buttons from about 1720 to 1902, all at the same heights"),
	"toggle_units": c((1730, 942), None, "Unit Display <Alt+U>: unit position and density; turning it on replaced the resource bubbles, and a second click left neither"),
	"toggle_resources": c((1758, 942), None, "Resource Display <Ctrl+R>: round resource bubbles; one of the unit, resource and yield layers shows at a time"),
	"toggle_grid": c((1785, 942), None, "Grid <Ctrl+T>: the tile grid lines, on in the user's settings"),
	"toggle_yields": c((1812, 942), None, "Yield Display <Ctrl+Y>: food, production and commerce icons on each tile"),
	"toggle_bare_map": c((1837, 942), None, "Bare Map <Ctrl+B>: hides improvements and units to show the landscape"),
	"toggle_annotations": c((1858, 942), None, "map annotations: no visible change on this map, which had none"),
	"toggle_scoreboard": c((1882, 942), None, "Scoreboard: hides the whole scoreboard; a second click shows it again"),
	"globe_view": c((1905, 942), None, "Globe View <F11>: zooms out to the globe with city names, and back in"),
	"minimap": c((1820, 1050), None, "x 1718-1920, y 990-1110")},
	"tests": [
		["ctrl+left, ctrl+right", "rotate the camera 45 degrees and back"],
		["f10, then enter", "open the capital's city screen, then leave it"],
		["alt+i", "hides the whole interface; a second alt+i restores it"],
		["pgup, pgdn", "no zoom change, with or without the extended-key flag"],
		["mouse wheel over the map", "zooms, only with Civ4 in front; from the farthest view +4 clicks show cities and borders, +6 to +8 a medium zoom with units readable, +10 close"],
		["c, num6 with no unit selected", "nothing; after the city screen or advisors no unit is selected, so click one first"],
		["num6 with a Worker selected", "did not move it"],
		["g, then a click on a tile", "moves the selected unit there: a Worker centred by c at (960, 520) moved one tile east with a click at (1060, 520)"],
		["period, comma", "select the next or previous unit in unit_bar, on the same tile"],
		["w", "selected a group of about 8 units"],
		["click a unit in unit_bar", "selected about 8 units at once, most likely the group it already belonged to"],
		["ctrl+click a unit in unit_bar", "selected every unit of that type on the tile (11 of 11)"],
		["shift+click a second unit after a click", "added it, and several more units, to the selection"],
		["alt+click a unit in unit_bar", "selected nearly every unit on the tile; those left out had a grey dot rather than green, likely no moves left"],
		["backslash, as the US key code", "moved one unit right in unit_bar, not back"],
		["ctrl+shift+x", "opens autoplay_prompt; during a run it stops autoplay after 1 to 2 turns, then the held-back popups follow"],
		["ctrl+l", "opens game_load_file"],
		["end_turn click", "ended the turn (200 to 201); then popup_choose_research and popup_choose_production came"],
		["city_previous, then esc", "a city selected on the main screen; esc returns to the unit"],
		["scoreboard scroll buttons (SAS48, Debug Mode)", "down moves 1 row, down fast about 5; the list opens centred on the active player, so the top scorers (Justinian 248, Frederick 227) were hidden above until scrolled up"],
		["click the minimap", "centres the view there; its lower right was open ocean on SAS48 Pangaea"],
		["click a foreign city's banner in Debug Mode", "selects it on the main screen with its production choices, as city_previous does"],
		["click --double a foreign city's banner in Debug Mode", "opens its city screen; the top bar then shows that player's research and gold"],
		["alt+click a leader on the scoreboard", "opens popup_declare_war"],
		["g, then hover a far tile", "draws the path with a numbered marker for each turn; a click gives the order and the selection moves to the next unit"],
		["click a plot with units", "selects a unit there and can recentre the view, so re-read positions after each step"],
		["esc with no screen open", "opens ingame_menu, even with a unit selected; with a popup open, the first esc closed that instead"],
		["b with a Settler selected", "founds the city, then popup_city_name, popup_choose_research and popup_choose_production in turn"],
		["enter", "ends the turn only when the end_turn circle is red, that is when no unit waits for orders; f (fortify) on the last idle unit made it red"],
		["hover or ctrl+z with a popup open", "no help text, and Debug Mode did not toggle: popups take the input until answered"],
		["click a city banner (own)", "selects the city with its production queue; a click on the city's buildings just above selected its units instead"],
		["hover an enemy city in Debug Mode", "shows its food, production, build, gold and maintenance, not its units; --double opens its city screen with its buildings, such as Walls"],
		["mouse wheel while another window is in front", "no zoom; bring Civ4 forward first (desktop_windows key pause does it harmlessly)"],
		["shift+enter", "ends the turn, as the end_turn button does; a new tech then opened popup_tech_discovered"],
		["ctrl+z", "Debug Mode on, revealing the whole map; again turns it off (needs CheatCode = chipotle)"]]}

S["city_screen"] = {"reach": "F10 opens the capital, Insert the nearest city, or click a city; Enter, the middle mouse button or a minimap click leaves",
	"note": "Mapped on 2026-11-11 on Carthage, size 14, at turn 200. Here help text appears next to the pointer, not at the bottom left, so use hover_tooltips.py --front without --area. The named tiles use the normal city camera at the mapped window size. Verify the tile grid in a screenshot after changing camera or resolution.",
	"tests": [
		["click a production choice", "changes production at once (Pikeman to Settler)"],
		["shift+click a production choice", "adds it to the end of the queue"],
		["ctrl+click a production choice", "puts it first in the queue"],
		["click an item in the queue", "removes it"],
		["specialist +, then -", "a citizen became an Engineer (culture 99.00 to 100.50, science down), and back"],
		["click a worked tile", "takes its citizen off (the growth bar shows Shrinking); on a fresh city screen a second click puts it back, but one about 2 s later closed the city screen instead (cause unknown)"]],
	"controls": {
	"city_bar": c((960, 92), None, "name, size, culture and production modifier; religion icons at its left, such as (418, 92) Christianity"),
	"growth_bar": c((960, 136), None, "Growing or Shrinking with food stored, turns; no help text"),
	"production_bar": c((960, 166), None, "current production with hammers and turns; no help text"),
	"commerce_sliders": c((110, 112), None, "the empire's commerce sliders with + and - buttons, as on the main screen, and each rate at x 380"),
	"maintenance": c((100, 198), None, "city maintenance"),
	"trade_routes": c((60, 260), None, "one row per trade route; hovering shows the route's yield breakdown beside the list"),
	"buildings": c((60, 366), None, "buildings with their effects, 24 px apart from y 366; hovering shows a building's effects beside the list"),
	"bonuses": c((1690, 95), None, "bonus resources in two columns at x 1690 and 1880 from y 95, about 40 px apart; hovering shows effects, such as Maize +1 health with Granary"),
	"specialists": c((1855, 502), None, "one figure per kind at x 1855, rows 28 px apart from y 502 (Engineer first here; the figure at y 472 has no button); hovering shows its yields, such as Engineer +3 hammers, +2 science, +1 culture, +3 birth rate"),
	"specialist_plus": c((1880, 502), None, "+ beside each kind: moves a citizen from a tile to that specialist; the button then becomes a - at x 1903, which moves it back"),
	"specialists_now": c((1802, 672), None, "the city's current specialists and settled Great People, 28 px apart at y 672"),
	"info_lines": c((1720, 760), None, "Great People, culture, nationality and religion lines; the culture bar at (1720, 840) shows its breakdown"),
	"citizen_automation": c((1790, 892), None, "Turn Off Citizen Automation, among small buttons at y 892; arrows at (1712, 892) and (1740, 892) show no help text"),
	"nationality": c((1810, 924), None, "City Nationality, such as 100% Carthaginian"),
	"production_filters": c((60, 932), None, "ten buttons at y 932, about 34 px apart from x 60: Start Scroll at Units, at Buildings, at Wonders; Show All Buildings, Regular Buildings Only, National Wonders Only (identified from the named control in CvMainInterface.py), World Wonders Only; Hurry with population, Hurry with gold (needs a civic), and one more without help text; at turn 100 the filters barely changed the short list"),
	"production_choices": c((430, 925), None, "units, then buildings and wonders in rows from y 925, about 54 px apart across from x 433 and 53 px down (re-measured 2026-11-11; 37 and 50 px were wrong); hovering shows cost and effects; a click starts it; Ctrl+click puts it first in the queue, Shift+click last, Alt+click repeats it"),
	"processes": c((433, 1083), None, "Wealth, Research and Culture at y 1083, 54 px apart from x 433"),
	"queue": c((80, 966), None, "the production queue at the bottom left, one row per item about 24 px apart from y 966, with counts; it replaces the units list once something is queued"),
	"units": c((60, 966), None, "units in the city, with the selected one's portrait")}}


# <!-- custom: Generate named city-relative tile centres from the visible rows and columns, with north at the top and the four BFC corners omitted.
# The earlier centre at y=523 was high on Uruk's city screen; the centre of its worked ring is near y=540 at the mapped window size and camera. (GPT-6.1-Sol) -->
city_controls = S["city_screen"]["controls"]
tile_columns = (681, 822, 963, 1104, 1245)
tile_rows = (257, 398, 540, 681, 822)
for dy, y in enumerate(tile_rows, start=-2):
	for dx, x in enumerate(tile_columns, start=-2):
		if abs(dx) == abs(dy) == 2:
			continue
		directions = []
		if dy:
			directions.append("%s%d" % ("n" if dy < 0 else "s", abs(dy)))
		if dx:
			directions.append("%s%d" % ("w" if dx < 0 else "e", abs(dx)))
		name = "tile_" + ("_".join(directions) or "center")
		if directions:
			city_controls[name] = c((x, y))
		else:
			city_controls[name] = c((x, y), None, "city tile; clicking it restores automatic citizen assignment")
city_controls["tiles"] = city_controls["tile_center"]

S["advisors"] = {"reach": "F1 to F9 and Ctrl+E from the main screen, or the advisor buttons at y 79; Esc closes each, as does its EXIT tab",
	"note": "Opened on 2026-11-11 at turn 200, not in Debug Mode. Each advisor covers about the left three quarters of the window (x 0-1440); the scoreboard, top right and minimap stay visible to its right. Its tabs run along the bottom at about y 1095, left to right, with EXIT last near x 1440.",
	"controls": {
	"f1_domestic": c((1650, 79), None, "Domestic Advisor: tabs Overview 1, Overview 2, Overview 3, Overview 4, Finance; a city table"),
	"f2_policy": c((1678, 79), None, "Policy Advisor: tabs Civics, Religions, Corporations; civic columns Government, Legal, Labor, Economy, Religion"),
	"f3_diplomacy": c((1706, 79), None, "Foreign Diplomacy Advisor: tabs Relations, Glance, Info, Espionage; a web of leader portraits"),
	"f4_trade": c((1734, 79), None, "Foreign Trade Advisor: tabs Treaties, Bonuses, Techs, Cities; one row per civilization"),
	"f5_military": c((1762, 79), None, "Military Advisor: tabs Summary, Map, Battles, Composition along y 1090 (Map at x 430, Battles at x 668)"),
	"f5_map_leaders": c((60, 180), None, "Map tab: leader portraits in rows of 10, about 68 px apart, the Barbarian skull last; a click lists that player's units on the right, grouped by combat type, with a Show individual units checkbox; the world map below"),
	"f5_battles_player": c((176, 96), None, "Battles tab, Debug Mode: a player dropdown; items 26 px apart from y 132 at x 100; the table lists that player's battles with turn, odds, units, XP and plot; LOG and Legend at the top right; clicking a row showed no change"),
	"f6_technology": c((1790, 79), None, "Technology Advisor: the tech tree, no tabs"),
	"f7_world": c((1818, 79), None, "World Advisor: tabs BFC 1, BFC 2, Territory, Environment, Changes"),
	"f8_info": c((1846, 79), None, "Info Screen: tabs Graph, Score, Timeline, Demographics, Top 5 Cities/Wonders, Statistics"),
	"f9_victory": c((1874, 79), None, "Victory Screen: tabs Victories, Settings, Resolutions, Members"),
	"ctrl_e_espionage": c((1902, 79), None, "opens the Foreign Diplomacy Advisor on its Espionage tab"),
	"debug_player_dropdown": c((200, 140), None, "in Debug Mode only: a wide dropdown at the top left of F1 and F3, likely choosing whose data the advisor shows; its items were not read yet")},
	"tests": [
		["esc", "closes the advisor"],
		["reopening an advisor", "it opens on the tab last used: F3 on Espionage after Ctrl+E"],
		["f1, f3 in Debug Mode", "each gains debug_player_dropdown"],
		["f2, Tribalism, REVOLUTION", "\"Autoplay adopts Tribalism! (Abolishes Slavery.)\" on the main screen, at once"]]}
for advisor, tabs in ADVISOR_TABS.items():
	for name, x in tabs:
		S["advisors"]["controls"]["%s_%s" % (advisor, name)] = c((x, 1091))
S["advisors"]["controls"]["f2_civic_columns"] = c((90, 196), None, "Civics tab: Government, Legal, Labor, Economy and Religion columns 300 px apart from x 90 (names at x 90, 390, 690, 990, 1290), civics 30 px apart from y 196; an icon marks the ones available; a click previews it below and turns the bottom bar into CANCEL (x 752) and REVOLUTION (x 1398)")
S["advisors"]["controls"]["f2_revolution"] = c((1398, 1091), "game_main", "after choosing civics: adopts them and closes the advisor; with 0 turns for revolution there was no anarchy")
# <!-- custom: Inside the tabs, read off a tour of every tab at turn 201 on 2026-11-11; table rows are about 24 px apart, and a click on a column heading sorts it, a second click reverses. (Claude Code Opus 5.5) -->
for name, xy, note in (
		("f1_table", (40, 138), "Overview 1-4: one city per row from y 162, 24 px apart, headings at y 138; Overview 1 ends with Producing, Overview 4 with the city's X and Y"),
		("f1_legend", (1462, 90), "Legend at the top right, as on several advisors"),
		("f1_finance_rates", (50, 740), "Finance: rate buttons beside Research, Culture, Espionage and Gold, at x 50 and 72, 30 px apart from y 740; the treasury line at y 420"),
		("f2_religions", (268, 150), "Religions: one religion per column at the top with founded, holy city, leader and influence; a city table below"),
		("f3_relations_legend", (80, 870), "Relations: line colours for contact, war, defensive pact, open borders, team and vassal at the bottom left"),
		("f3_espionage_weights", (60, 165), "Espionage: one leader per row about 56 px apart with + and - weight buttons; cities, passive effects and missions with costs to the right"),
		("f5_map_show_units", (760, 160), "Map: the Show individual units checkbox above the unit list"),
		("f5_battles_table", (40, 140), "Battles: headings at y 140, rows 24 px apart from y 164; Turn sorted ascending, then descending; LOG at (1394, 94)"),
		("f8_graph_dropdowns", (180, 164), "Graph: two dropdowns at the top left, the measure (Score) and the time span (Entire timeline)"),
		("f8_timeline_log", (1428, 94), "Timeline: LOG at the top right; the event list scrolls"),
		("f8_score_table", (400, 140), "Score: one leader per row; a heading click re-sorts"),
		("f9_space_view", (516, 503), "Victories: the space race's View button")):
	S["advisors"]["controls"][name] = c(xy, None, note)
S["game_main"]["controls"]["select_next_unit"] = c((1636, 983), None, "Select Next Unit <W>, left of the city arrows; selected the next unit to move")
S["city_screen"]["tests"].append(["shift-click, ctrl-click, then click the first queue row", "re-checked 2026-11-11 on Uruk: Shift added a second Missionary, shown as one row with (2); Ctrl put a Worker first; clicking the Worker's row removed it"])
S["city_screen"]["tests"].append(["tiles on Uruk at turn 201, 2026-11-11: click a worked tile, again, an unworked mine, then the city tile", "the first click freed its citizen as a specialist (growth 9 to 25 turns), the second put it back; the mine took a citizen from another tile (growth 13 turns, production faster); the city tile then reset all to the automatic choice. Tiles show bread, hammer and coin icons for their yields, bonuses in purple circles and worked tiles in white rings"])
S["city_screen"]["tests"].append(["Right, Left; Home, End, Page Down", "Right and Left switch to the next and previous city; the others did nothing"])
S["city_screen"]["tests"].append(["tile_n2_w1 on Uruk; tile_s1_e2 on Eridu; tile_center after each", "GPT-6.1-Sol repeated the turn-201 test on 2026-11-11. Each worked ring disappeared when clicked; clicking the centre restored that city's automatic assignment and the ring."])
# <!-- custom: Round of 2026-11-11 evening, from Codex's list, on the turn-200 Gilgamesh save (Uruk, Eridu, Kish, Lagash). (Claude Code Opus 5.5) -->
for name, y in (("engineer", 502), ("merchant", 530), ("scientist", 558), ("artist", 586), ("priest", 614), ("citizen", 642)):
	S["city_screen"]["controls"]["specialist_" + name] = c((1858, y), None, "+ at (1880, %d) when the city has a free slot, - at (1903, %d) once one is assigned; assigned ones show as figures to the left, 28 px apart" % (y, y))
S["city_screen"]["tests"].append(["hover each specialist row", "named the rows Engineer, Merchant, Scientist, Artist, Priest, Citizen from y 502; the figure at y 472 has no help text; yields differ between games, so read the help rather than assume them"])
S["city_screen"]["tests"].append(["specialist_scientist +, then -", "the figure lit up, a - appeared, Great Person points went from 0 to 3 per turn with new type odds; the - restored it"])
S["city_screen"]["tests"].append(["compare Uruk, Eridu, Kish, Lagash", "only Uruk had a + for Engineer, so a + needs a free slot; Eridu showed its four Priests as figures left of the row, with + and -"])
S["city_screen"]["tests"].append(["production_filters in Lagash: the three scroll buttons, then the four building filters", "Units, Buildings and Wonders scroll the list (Buildings brings the processes into view); the four building filters changed nothing visible there; the two hurry buttons were not clicked"])
S["tech_tree"] = {"reach": "F6, or the Technology Advisor button at (1790, 79); EXIT at (1660, 1090)", "shows": "the tech tree: known techs green, available ones lavender, out of reach blue; the queue position and turns before a queued tech's name, such as 1 Professional Army (1); a bottom strip shows which techs each Great Person could discover", "controls": {
	"tree": c((860, 600), None, "the wheel scrolls it sideways: 10 clicks down went from the classical to the industrial techs; click a tech's title"),
	"scrollbar": c((860, 1050), None, "horizontal scrollbar"),
	"great_people_techs": c((32, 1094), None, "lightbulb: techs Great People could discover; icon groups to its right, about x 110, 204, 320, 410, 504, show each Great Person type's current discovery and preference order"),
	"exit": c((1660, 1090), "game_main")},
	"tests": [
		["click an available tech's title (Banking)", "replaced the whole queue with the path to it: 1 Broader Education (4), 2 Banking (5); the current tech dropped out but kept its progress"],
		["click the dropped tech again, then shift+click Banking", "1 Professional Army (1), 2 Broader Education (4), 3 Banking (5): Shift appends the path"],
		["click an unlock icon inside a tech box", "nothing opened"]]}
S["advisors"]["tests"].append(["f5_map_show_units", "turns into Hide individual units and lists each unit with strength, moves, XP and promotion icons"])
S["advisors"]["tests"].append(["Map tab: click a unit row, then another leader, without and with Debug Mode", "the row turns yellow; without Debug Mode another leader's list is empty; with it, that leader's units are listed, the world map is revealed, and the selected type's units show as yellow dots on the map"])
# <!-- custom: Round of 2026-11-11/12 night, on the Gilgamesh game autoplayed to turn 350-369 (Modern era, lost to a Roman Domination victory at turn 369). (Claude Code Opus 5.5) -->
S["game_main"]["tests"] += [
	["in-game autoplay running: Civ4 in the background, then in front", "it kept playing either way, about 20 turns per 15 s; focus does not pause it"],
	["f3 during autoplay", "the Foreign Diplomacy Advisor opened on Relations and stayed open while turns kept passing; esc closed it, autoplay still running"],
	["ctrl+z on and off during autoplay", "Debug Mode toggled without stopping autoplay"],
	["ctrl+shift+x during autoplay", "stopped it; here an AI won a Domination victory the same turn, so popup_victory came next"],
	["click a city banner with a unit selected", "nothing: the click did not reach the banner; city_previous and city_next selected the city instead"],
	["city selected on the main screen: click a production choice, then a queue row", "the choice went to the queue's front and onto the city's banner (Stable (8)); clicking its queue row (y about 962, rows 30 px apart) removed it: production can be changed without entering the city"],
	["the next-unit button left of the city arrows, clicked repeatedly", "selects the next unit still waiting for orders, centring the map on it each time, across ships and land units; 44 presses brought the first unit round again in this game"],
	["g with a Privateer selected, then a click on a fogged sea tile", "drew the path into the fog with a turn marker and gave the order; the selection then moved to the next unit"],
	["click the Great Person bar (top middle)", "opened the city screen of the city it names (Eridu)"]]
S["game_main"]["controls"]["hurry_buttons"] = c((300, 938), None, "with a city selected on the main screen: population hurry at x 300, gold hurry at x 335, and draft at x 368; availability depends on the city and rules; not clicked")
S["city_screen"]["controls"]["religion_icons"] = c((415, 84), "sevopedia", "the city's religion and corporation icons at y 84, 30 px apart from x 415; hover names it and its effects; a click opens its Sevopedia page, and esc there returns to the city screen")
S["popup_victory"] = {"reach": "someone wins", "shows": "X has won a ... Victory, with OK", "controls": {
	"ok": c((1703, 220), "replay_screen", "then come the replay, the Info Screen's graph, Your Place in History and the Hall of Fame, each with EXIT, and then popup_end_of_history")}}
S["popup_end_of_history"] = {"reach": "after the end-of-game screens", "shows": "The End of History...", "controls": {
	"one_more_turn": c((1700, 187), "game_main", "Wait! Just one more turn..."), "exit_to_main_menu": c((1700, 217), "main_menu")}}
S["replay_screen"] = {"reach": "end of a game, or hall_of_fame's V button from the main menu", "shows": "the map growing turn by turn, a score graph below it, and the game's event log on the right, which lists major events such as wars and city captures", "controls": {
	"play": c((52, 1094), None, "PLAY, which becomes STOP while playing; plays to the end, about 10 s for 369 turns at default speed"),
	"next": c((202, 1094), None, "NEXT advanced one replay turn in the early-game check"),
	"speed": c((930, 1083), None, "speed slider from about x 822 to 1020, default near the left; after a drag to the left end the replay took about 8 s and after one to the right about 10 s, too close to tell which way is faster; the user thinks the far right is the fastest; re-test with a longer game"),
	"exit": c((1872, 1092), None, "back to the previous screen")}}
S["main_menu"]["controls"]["hall_of_fame"] = c(menu(2), "hall_of_fame")
S["hall_of_fame"]["controls"]["view_replay"] = c((20, 243), "replay_screen", "the V button of each row, only from the main menu; rows 22 px apart from y 243")
S["hall_of_fame"]["tests"] = [
	["click and double-click a row inside a game", "no replay: the in-game Hall of Fame has no V column"],
	["filter dropdowns", "Leaders, Difficulties (All, Rookie..Deity+), Starting Eras (All, Ancient..Future), Single/Multiplayer, Victories (All, Score, Time, Conquest, Domination, Cultural, Space Race, Diplomatic), World Sizes (All, Arena..SAS48), Game Speeds (Nitro..Very Slow), sort (Normalized Score, Finish Date, In-game Score); items 31 px apart from 32 px below the header"],
	["click a column heading twice", "sorts ascending, then descending"],
	["legend", "opens the Hall of Fame Legend page in the Sevopedia"]]
S["load_dialog"]["controls"]["autosaves"] = c((298, 652), None, "the auto folder in the tree once Saves/single is expanded: this run had autosaves every 4 turns plus the initial one; typing a path into the filename box did not work here, so open the folder")
S["advisors"]["tests"].append(["Map tab: click a unit type row, then ctrl+click and shift+click others", "both modifiers add the type to the selection (rows turn yellow) and the map dots show all selected types; rows 32 px apart from y 218 at x 850 in this game"])
S["tech_tree"]["tests"] += [
	["click an already known tech (Fishing)", "clears all research, as the user said; the top bar then shows one icon per available tech instead of the research bar"],
	["great_people_techs icons", "the lightbulb shows techs Great People could discover; each group to its right shows one Great Person type's current discovery or preference order, so they differ"]]
S["game_main"]["controls"]["research_icons"] = c((660, 52), None, "when no research is set: one icon per available tech, 37 px apart from x 660; hover shows unlocks, turns, progress and diffusion; a click sets research, keeping earlier progress")
S["advisors"]["controls"]["f2_corporations"] = c((286, 188), None, "Corporations tab: one column per corporation, 177 px apart from x 286 (built by, consumes, generates, founded, HQ); the player's cities below in two lists, those with a corporation marked by its icon and yield; in Debug Mode the player dropdown at (176, 96) switches whose cities show, items 23 px apart from y 134; clicking a city name does nothing")
S["advisors"]["tests"] += [
	["f1 or f2 in Debug Mode: choose another player", "their cities and data show; double-clicking a foreign city's row in F1 does not open it"],
	["find another player's city with a corporation", "F2 Corporations with that player chosen names the cities; minimap click toward their colour, zoom in, then click the banner"]]
S["city_screen"]["controls"]["corporation_icons"] = c((1508, 92), "sevopedia", "corporation icons at the right end of the city bar, apart from the religions at the left; hover names it, its yields and what it consumes; a click opens its Sevopedia page, esc returns")
S["game_main"]["tests"] += [
	["click a city banner while one of our units is selected", "nothing; esc then opened ingame_menu instead of deselecting; after cancelling it a click selected the city, and a double-click opened its city screen, a foreign city too in Debug Mode"],
	["zoom level for clicking banners", "at the farthest zooms banners are tiny and each click recentred the map; 4 wheel clicks in from far made them easy targets and readable"]]
S["city_screen"]["controls"]["specialist_spy"] = c((1858, 446), None, "the top row, without help text when empty; Cahokia (turn 368) had two Spies with a - at (1903, 446); rows shift with how many specialists and Great People a city has, so read them off a screenshot")
S["city_screen"]["tests"] += [
	["mouse wheel over the building list", "did not scroll it"],
	["drag the building list's scrollbar (x 386, y 345 to 895) down", "scrolled to the end; the list shows about 22 rows (Cahokia had 24 buildings and wonders)"],
	["a big late-game city (Cahokia, size 17, corporation HQ, wonders, settled Great People)", "shows most elements a small city leaves empty: Spy row in use, settled Great People as a row of figures below the specialists, the corporation icon on the city bar"]]
S["city_screen"]["tests"] += [
	["f1 from the city screen, then esc or the EXIT tab", "advisors open over the city screen, but both esc and EXIT then return to the main map, not to the city (the user expected EXIT to keep it; tested, it does not)"],
	["specialist + and - in a rival city (Debug Mode)", "nothing changes; the buttons are shown anyway (noted in changes_new.md)"],
	["hover a trade route row (y about 236)", "its yield breakdown: base, then each modifier, then the total"],
	["hover the settled Great People row and the red faces below it", "each settled Great Person and specialist with their yields; the faces are the city's unhappy citizens"],
	["full-size crop of the tile grid", "yields are readable as icons per tile (bread food, hammers production, coins commerce); at half scale they blur, so crop at full size to read them"]]
S["city_screen"]["tests"] += [
	["hover a red face below the specialists", "Angry Citizen (Refuses to work...), with each cause and its count, such as +17 It's too crowded!, and the total unhappiness"],
	["citizen + five times, then once more (own capital)", "the row's figures merge into one figure with a yellow V above at 5; the sixth shows as one more plain figure beside it, as the user said"],
	["six citizen - clicks afterwards", "left one Citizen specialist where an Engineer had been, so assignments do not simply undo; check the column after each click"],
	["the ten production filters in a big late-game city", "inconclusive: after the first filter click the screen was back on the main map, so the next clicks hit the main screen; the user was moving the mouse meanwhile, which most likely caused it; retest one click at a time with a screenshot after each"]]
S["advisors"]["controls"]["exit_tab"] = c((1446, 1091), "game_main", "EXIT, the last tab of every advisor")
# <!-- custom: WorldBuilder's tool icons, from their tooltips on 2026-11-12 (hovered with hover_tooltips.py --front --wait 4; without the window in front or with a shorter wait none showed): two rows of six at the top right, 35 px apart.
# Then each mode was clicked on 2026-11-12 in the user's turn-0 game; the notes say what opened. (Claude code Opus 5.5) -->
WB_ICONS = (("landmark_mode", "Enter landmark mode", "a map click asks Enter caption (text field, OK) and puts a sign with that text on the plot; a right-click removes it"),
	("erase_mode", "Enter erase mode", "one map click removes everything placed on the plot at once: units, resource and improvement were all gone after one click"),
	("change_all_plots", "Change All Plots", "a modal panel at the right: Add Mountain, Add Hill, Add Grass, Add Ocean, Cancel (about (1780, 308)); until Cancel, other icons and tooltips do nothing. Add Hill turned every plot of the map into a hill, the ocean included, with no undo (2026-11-12, test game; the log showed DEBUG Event: WBAllPlotsPopup)"),
	("save", "Save", "a Save File dialog in Saves/WorldBuilder for .CivBeyondSwordWBSave files: folder tree, file list, Filename, File Type, OK (1619, 904) and Cancel (1619, 943); entering WorldBuilder itself had written WBQuickSave"),
	("load", "Load", "a Load File dialog with the same layout and folder; Cancel at (1620, 944)"), ("exit", "Exit World Builder", "back to the game; reopening with Ctrl+W resets every panel's size and position"),
	("edit_unit_mode", "Edit Unit Mode", "a map click on a unit opens World Builder Edit Control: Choose Unit (a dropdown of the plot's units, the unit's name, Experience and Level spinners, a UNITAI_ dropdown, Add Script) and Promotions (a click toggles one; a yellow frame means the unit has it); a click on an empty plot opens nothing"),
	("edit_city_mode", "Edit City Mode", "a map click on a city opens World Builder Edit Control: City Data (name, Population, Culture, Gold, Add Script, then rows for religions, holy cities, corporations and headquarters, whose clicks toggle) and Buildings (a click toggles one; a yellow frame means the city has it)"),
	("player_mode", "Player Mode", "the mode panel top left with Units, Buildings and Technologies tabs; click an item (yellow frame), then a plot: a unit is placed for the player in the dropdown; a right-click on a plot removes its units. A building clicked onto a city showed no effect (use Edit City instead)"),
	("map_mode", "Map Mode", "the mode panel with Improvements, Resources, Terrains and Territory tabs, and a brush size dropdown; click an item, then a plot: it paints that item. A right-click removes a resource, improvement, feature, route or ownership, but not a terrain or plot type, which are changed by painting another"),
	("reveal_tile_mode", "Reveal Tile Mode", "Reveal All Tiles (1718, 134) and Unreveal All Tiles (1753, 134) for the player in the dropdown; unrevealed plots show hatched; a map click reveals that plot"),
	("diplomacy_mode", "Diplomacy Mode", "a centred Diplomacy panel: the leader whose relations are edited, a vassal dropdown, then per other player a War with or Peace with dropdown and an AI attitude weight slider from -100 to 100; Restore Defaults and Exit; choosing War with set it at once, and Peace with set it back"))
S["worldbuilder"] = {"reach": "Ctrl+W from a game", "shows": "the map with a tool panel top right (two rows of six icons, a player dropdown and Add Techs by Era) and a mode panel top left, such as Player Mode with Units, Buildings and Technologies tabs",
	"note": "In Player Mode and Map Mode a click on the map edits the game: on 2026-11-12 a drag that missed the panel's grip moved the panel, and the tab clicks that followed landed on the map and placed Lions; the vertical drag that was meant to shrink the panel also painted a Lion on each plot it crossed. A right-click on a plot in Player Mode removes its units, as the user pointed out, which removed all eleven. Click only on panels, start a drag exactly on the grip, and screenshot after each drag.",
	"tests": [
		["right-click a plot in Player Mode", "removes the units on it (a desktop_windows.py drag --button right with the same start and end point is a right-click)"],
		["drag the panel grip", "resizes the panel; a press beside the grip moves the whole panel instead"],
		["Change All Plots open, then other icons or hovers", "nothing happens until its Cancel is clicked"],
		["Map Mode, 3x3 brush: paint territory, then right-click", "9 plots changed owner, and the right-click cleared all 9"],
		["Map Mode: desert, then right-click", "the desert stayed; painting grassland restored the plot"],
		["Player Mode: a building clicked on an empty land plot (SAS48, 2026-11-12)", "founded a city there with that building, a capital with the Palace; a research choice popup then opened and blocked other clicks until answered"],
		["Player Mode, Technologies: click a tech; Add Techs by Era: Add all Ancient Techs", "a click toggles the tech for the selected player (yellow frame = known); the era item framed every Ancient tech, and the panel jumped back to the Units tab"],
		["Edit Unit or Edit City: Add Script", "asks Enter your script name (field at about (1700, 185), OK (1703, 235)); the text is stored and shown when reopened; OK with an empty field kept the old text, so this popup cannot clear a script"],
		["Edit City: Population up arrow", "the city grew at once (the banner showed 2)"],
		["Map Mode: Regenerate Map Using Current Map Script (the crosshair at (1718, 134))", "did nothing in a game where a city had been founded"],
		["Diplomacy Mode with 48 players (SAS48)", "about 6 player columns show at a time, with a horizontal scrollbar; the panel already spans x 110-1818, so no size fits 48"],
		["closing the client while in WorldBuilder", "it ignored the close request; run_autoplay.close_civ4 forced it after its wait, so leave WorldBuilder first"]],
	"controls": dict((name, c((1718 + 35 * (i % 6), 63 if i < 6 else 98), None, "tooltip: %s; %s" % (tip, done))) for i, (name, tip, done) in enumerate(WB_ICONS))}
S["worldbuilder"]["controls"].update({
	"panel_tabs": c((46, 82), None, "the mode panel's tabs at y 82: Player Mode has Units x 46, Buildings x 119, Technologies x 222; Map Mode, once widened, Improvements x 80, Resources x 190, Terrains x 278 (terrain types, plot types, features, then routes) and Territory x 362; at the default width arrows at about (298, 84) scroll the tab strip"),
	"map_brush_size": c((1825, 135), None, "Map Mode and Reveal Tile Mode: brush size 1x1, 3x3 or 5x5, items 26 px apart; the target icon left of it at (1718, 134)"),
	"reveal_all": c((1718, 134), None, "Reveal Tile Mode: tooltip Reveal All Tiles; not clicked"), "unreveal_all": c((1753, 134), None, "Reveal Tile Mode: tooltip Unreveal All Tiles; not clicked"),
	"diplomacy_panel": c((962, 575), None, "Diplomacy Mode: a centred panel, x 107-1820, y 382-768: a leader dropdown (296, 492), War with ?, AI Attitude Weight and a vassal dropdown (Not a Vassal) at (296, 591), then one column per other player with a Peace with dropdown and a -100 to 100 slider, a horizontal scrollbar, Restore Defaults (962, 691) and Exit (962, 730); nothing was changed"),
	"panel_items": c((39, 121), None, "item grid, 7 per row at the default size, about 34 px apart from (39, 121); hovering shows the item's Sevopedia-style help, such as Lion or Swift Worker"),
	"panel_collapse": c((305, 46), None, "the arrow at the panel's top right: collapses it"),
	"panel_grip": c((302, 267), None, "the yellow grip at the panel's bottom right, at the default size: drag it to resize the panel; sizes reset when WorldBuilder is reopened. Edit Control has a grip too: for Edit City, from (1104, 799) to (1478, 799) shows all buildings in 9 rows of 18 with a spare row; for Edit Unit, from (1125, 735) to (1261, 735) shows all 57 promotions in 5 rows of 12; both widen from the centre. Sizes chosen with the user on 2026-11-12, each the smallest that shows every tab without scrolling, with one spare row for new buildings: Player Mode, grip to (648, 470): 18 columns, Units 8 rows, Buildings 9 plus the spare, Technologies 6. Map Mode, grip to about (429, 292): 11 columns, all four tab names without arrows, Territory's 49 slots (48 players and the Barbarians; empty ones show a skull and the tooltip None) in 5 rows"),
	"player_dropdown": c((1805, 135), None, "the player being edited: PC, then every leader, items 26 px apart from y 169; a second click on it closes it unchanged"),
	"add_techs_by_era": c((1805, 171), None, "Add all Ancient, Classical, Medieval, Renaissance, Industrial, Modern or Future Techs to that player, items 26 px apart from y 205; opened only to read, a second click closed it unchanged")})


# <!-- custom: Advanced Start, explored on 2026-11-12 in an agent's own Standard Pangaea game.
# A QuickStart game with the option gave 0 points, as the setup's Advanced Start Base Points (400 by default) come only through Custom Game; the game reads no points key from the INI.
# Custom Game in a client started from a per-run INI copy keeps the user's INI untouched. (Claude code Opus 5.5) -->
S["advanced_start"] = {"reach": "Custom Game with the Advanced Start option ticked (custom_game options, first box), then Launch",
	"shows": "the points box top left (points, Begin!, Cost Here), 10 turns of Universal Peace Remaining, and an Advanced Start panel at the bottom left with Cities, Units, Improvements, Visibility and Techs tabs",
	"note": "Select an item, hover a plot to see Cost Here (0 means it cannot go there, as a Cottage on forest showed), click to buy; a right-click on the plot sells it back for the full price. Items marked Not removable in their help (City, Culture, buildings, Visibility, Techs) cannot be sold. A new city asks for a name, and the first one also opens a research choice popup; answer them before the next click.",
	"controls": {
	"points": c((75, 66), None, "points left; leftover points became gold after Begin!"),
	"begin": c((117, 97), "game_main", "ends Advanced Start; the game then asks the capital what to build"),
	"cost_here": c((100, 136), None, "the price of the selected item on the hovered plot"),
	"tab_cities": c((337, 987)), "tab_units": c((397, 987)), "tab_improvements": c((490, 987)), "tab_visibility": c((597, 987)), "tab_techs": c((672, 987)),
	"items": c((330, 1026), None, "the tab's items from here, about 34 px apart. Cities: City (Not removable), Population Point (33, then 36 for the next), Culture (Not removable), Build Improvements (Automated) below at (330, 1058), then the civilization's buildings (Not removable). Units: Settler (National Unit, 1 allowed), Worker (90 on the capital), a third unit. Improvements: Cottage. Visibility: one eye that reveals a plot for 2. Techs: one item that opens the Technology Advisor"),
	"automate": c((330, 1058), None, "Build Improvements (Automated): spent 239 of 248 points at once, including a second city (Akkad), whose name popup then had to be answered"),
	"techs_advisor": c((70, 176), None, "after the Techs item: the Technology Advisor; clicking a tech title (Fishing) set it as research, 1. Fishing, without spending points; EXIT at (1660, 1090)")}}


# <!-- custom: Popups and dialogs that open over a game. (Claude Code Opus 5.5) -->
S["autoplay_prompt"] = {"reach": "game_main: ctrl+shift+x", "shows": "Turn on AI Auto Play? How many turns would you like the AI to control?", "controls": {
	"turns": c((1100, 536), None, "prefilled with 501: click it, backspace 4 times, then type the count"),
	"ok": c((976, 574), "game_main", "starts autoplay; 2 turns ran in under 3 s"), "cancel": c((976, 606), "game_main")}}
S["game_load_file"] = {"reach": "game_main: ctrl+l", "shows": "Load File: folder tree on the left, opened on Saves/single; saves on the right, newest first, with size and date", "controls": {
	"file_list": c((980, 290), None, "the first save; rows 24 px apart; one wheel click scrolls 3 rows; a click fills the filename"),
	"filename": c((960, 904), None, "file name field"),
	"ok": c((1618, 904), "game_main", "loads the save: under 5 s for a turn-200 Standard game"), "cancel": c((1618, 942), "game_main")}}
S["popup_deal_cancelled"] = {"reach": "an AI cancels a deal; came first after an interrupted autoplay", "shows": "the diplomacy screen with the leader, both sides' items and one answer", "controls": {
	"exit": c((958, 860), "game_main", "Fair enough. (exit)")}}
S["popup_choose_production"] = {"reach": "a city finished or can no longer build its item; came after an interrupted autoplay", "shows": "a list on the right: Examine City, then recommended and other items", "controls": {
	"examine_city": c((1700, 245), "city_screen"), "items": c((1700, 283), "game_main", "items 40 px apart from here; a click sets the city's production")}}
S["popup_choose_research"] = {"reach": "research finished, after End Turn", "shows": "What would you like to research next? Let's see the Big Picture, then techs with turns and recommendations", "controls": {
	"big_picture": c((1640, 190), None, "opens the tech tree"), "techs": c((1640, 225), "game_main", "the first tech; rows 36 px apart; a click sets research")}}
S["popup_declare_war"] = {"reach": "game_main: alt+click a leader on the scoreboard", "shows": "Does this mean WAR?!? (vs. the leader), and which third parties will disapprove", "controls": {
	"yes": c((1704, 246), "game_main", "Yes, DECLARE WAR!: on 2026-11-11 also cancelled open borders, and the enemy's city banners turned red"),
	"no": c((1704, 278), "game_main", "No, let's reconsider")}}
S["ingame_menu"] = {"reach": "game_main: esc with nothing open", "shows": "Exit to Desktop, Exit to Main Menu, Retire, Load Game, Save Game, Options, BUG Menu, Enter WorldBuilder, Game Details, Your Details, Cancel", "controls": {
	"items": c((1780, 206), None, "the first item, Exit to Desktop; items 31 px apart; at the start of a game Regenerate Map appears fourth and pushes the later items down a row; the exits, Retire and WorldBuilder have real effects"),
	"exit_to_main_menu": c((1780, 237), "popup_are_you_sure", "the second item in both layouts"),
	"cancel": c((1780, 516), "game_main")}}
S["popup_tech_discovered"] = {"reach": "a tech is discovered at the start of a turn", "shows": "the tech's quote, special abilities, what it leads to and allows", "controls": {
	"continue": c((968, 868), "game_main", "Continue")}}
S["popup_are_you_sure"] = {"reach": "ingame_menu: Exit to Main Menu", "shows": "Are you sure?", "controls": {
	"exit_to_main_menu": c((1700, 180), "main_menu", "leaves the game without asking to save; the main menu came back within 8 s"),
	"cancel": c((1700, 210), "game_main")}}
S["popup_city_name"] = {"reach": "after founding a city", "shows": "What would you like to name this settlement? with the suggested name", "controls": {
	"ok": c((1705, 292), "popup_choose_research", "keeps the name; the first city then asked for research, then production")}}
S["popup_civic_available"] = {"reach": "a new civic becomes available, such as Pacifism at a Renaissance start", "shows": "Would you like to start a revolution?", "controls": {
	"no": c((1705, 202), "game_main", "No, the old ways are best"), "big_picture": c((1705, 232), None, "Let's see the Big Picture")}}
S["popup_first_unit"] = {"reach": "the first unit of a new kind is trained, such as the first Camel Knight", "shows": "Congratulations, you have trained your first ... unit, with what it does", "controls": {
	"carry_on": c((1700, 267), "game_main", "Very well, carry on then"), "big_picture": c((1700, 297), None, "What's the Big Picture?")}}
S["popup_vote_result"] = {"reach": "a vote in the Apostolic Palace or United Nations ends", "shows": "the resolution, the result and each civilization's vote", "controls": {
	"ok": c((1630, 396), "game_main")}}


# <!-- custom: Write the JSON, one control per line, then reread it to check that every "to" names a screen. (Claude Code Opus 5.5) -->
SHORTCUTS = read_shortcuts()
lines = ['{', '  "copyright": %s,' % json.dumps(copyright), '  "about": %s,' % json.dumps(about), '  "window": [1926, 1120],',
	'  "shortcuts_about": %s,' % json.dumps("Every key from the Sevopedia's Shortcuts pages, read from Assets/XML/Text/AdvCiv-SAS_Sevopedia_Lengthy.xml when this file is generated; \"chipotle\" entries need CheatCode = chipotle in CivilizationIV.ini, which the user's has. Keys reach Civ4 through desktop_windows.py key and type, whose events carry scan codes."),
	'  "shortcuts": {']
shortcut_groups = list(SHORTCUTS.items())
for gi, (group, pairs) in enumerate(shortcut_groups):
	lines.append('    %s: [' % json.dumps(group))
	for pi, pair in enumerate(pairs):
		lines.append('      %s%s' % (json.dumps(pair), "," if pi < len(pairs) - 1 else ""))
	lines.append('    ]' + ("," if gi < len(shortcut_groups) - 1 else ""))
lines += ['  },', '  "screens": {']
items = list(S.items())
for si, (k, v) in enumerate(items):
	lines.append('    %s: {' % json.dumps(k))
	lines.append('      "reach": %s,' % json.dumps(v["reach"]))
	for extra in ("shows", "about", "note", "list_layout"):
		if extra in v:
			lines.append('      %s: %s,' % (json.dumps(extra), json.dumps(v[extra])))
	if "tests" in v:
		lines.append('      "tests": [')
		for ti, test in enumerate(v["tests"]):
			lines.append('        %s%s' % (json.dumps(test), "," if ti < len(v["tests"]) - 1 else ""))
		lines.append('      ],')
	lines.append('      "controls": {')
	controls = list(v["controls"].items())
	for ci, (ck, cv) in enumerate(controls):
		lines.append('        %s: %s%s' % (json.dumps(ck), json.dumps(cv), "," if ci < len(controls) - 1 else ""))
	if "map_script_options" in v:
		lines.append('      },')
		lines.append('      "map_script_options": {')
		options = list(v["map_script_options"].items())
		for oi, (ok_, ov) in enumerate(options):
			lines.append('        %s: %s%s' % (json.dumps(ok_), json.dumps(ov), "," if oi < len(options) - 1 else ""))
	if "dropdowns" in v:
		lines.append('      },')
		lines.append('      "dropdowns": {')
		dropdowns = list(v["dropdowns"].items())
		for di, (dk, dv) in enumerate(dropdowns):
			lines.append('        %s: %s%s' % (json.dumps(dk), json.dumps(dv), "," if di < len(dropdowns) - 1 else ""))
	lines.append('      }')
	lines.append('    }' + ("," if si < len(items) - 1 else ""))
lines += ['  }', '}']
open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
d = json.load(open(OUT, encoding="utf-8"))
bad = [(s, k, v["to"]) for s, x in d["screens"].items() for k, v in x["controls"].items() if "to" in v and v["to"] not in d["screens"]]
print(len(d["screens"]), "screens,", sum(len(x["controls"]) for x in d["screens"].values()), "controls; broken links:", bad)

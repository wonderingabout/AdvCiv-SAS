# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The folders whose Python the game runs, under its Python 2.4, which the runtime Python checks scan; reference copies, docs examples and tooling Python are not listed, so dead or documented code never trips these checks.
# Each check held its own copy of this list before (2026-11-27), so a new runtime folder had to be added to each by hand: SASPilot's game files, which moved to the root SASPilot/ folder on its branch, still left a stale LLM_Helpers/saspilot entry in one check while others never had it.
# Scanning every .py file instead would trip on code the game never runs: the user's example is _1_AdvCiv-SAS/Docs/examples/source_comparison/CvMainInterface_1_12_singleline.py, base AdvCiv 1.12's main interface collapsed to one line per call for comparison, whose findings would be false positives tedious to exempt one by one.
# Kept as a plain tuple, as python24_compile.py imports it under Python 2.4 itself.
# A branch that runs Python from another folder, such as SASPilot's SASPilot/game, adds it here, and every check follows; SASLiveDefineOverrides/ would join it only if Python ever moved there, as it holds text files alone today. (Claude code Opus 5.5) -->
# <!-- custom: SASPilot/game holds SASPilotCommands.py and SASPilotUI.py, which run inside the game's Python 2.4 too; the SASPilot branch adds it here, as this list's comment asks of such a branch, so every runtime check scans it, the per-check folder lists it had replaced when main was merged on 2026-11-27. (Claude code Opus 5.5) -->
RUNTIME_PYTHON_DIRS = ("Assets/Python", "PrivateMaps", "SASPilot/game")

# <!-- custom: Single files the game runs from a folder that also holds modern tooling Python, each with why, so they need no whole folder listed above, which the Python 2.4 compile would then scan; empty on main.
# On the branches, Codex's review (GPT-6.2-Sol) found SASPilot's SASPilot/checks/trade_items_parity.py run inside Civ4 as a snippet, and SASSaveTransplanter's SASSaveTransplanterExport.py and SASSaveTransplanterUnitState.py copied or injected into it (2026-11-27).
# Only python_runtime_placement.py reads it so far, as an allowance: the other runtime checks scan the folders above alone, so a branch listing a file here also says, in its reason, what checks that file, until those checks read this list too, as Codex's review advised. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
RUNTIME_PYTHON_FILES = {
	"SASPilot/checks/trade_items_parity.py": "a snippet SASPilotClient.py injects into the running game with py @file, so it runs under Civ4's Python 2.4; listed for the placement check only, as no other runtime check scans it",
	"LLM_Helpers/sassavetransplanter/SASSaveTransplanterExport.py": "copied into or imported by the running game to export a save's state, so it runs under Civ4's Python 2.4; listed for the placement check only, as its folder also holds Python 3 tooling",
	"LLM_Helpers/sassavetransplanter/SASSaveTransplanterUnitState.py": "injected into the running game with py @file, so it runs under Civ4's Python 2.4; listed for the placement check only, as its folder also holds Python 3 tooling",
}

# <!-- custom: Copies of code kept for reference, never run, which the runtime placement check skips: 131 game files in LLM_Helpers/context, mostly the original map scripts in mapscript_refs, and base AdvCiv 1.12's single-line main interface in the docs examples.
# Git-ignored scratch such as LLM_Helpers/outputs is never listed, as the check reads Git's file list. (Claude code Opus 5.5) -->
REFERENCE_PYTHON_PREFIXES = ("LLM_Helpers/context/", "_0_Legacy/", "_1_AdvCiv-SAS/Docs/examples/")

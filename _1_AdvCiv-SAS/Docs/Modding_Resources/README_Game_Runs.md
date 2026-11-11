# AdvCiv-SAS Game Runs Guide

How an AI/LLM helper runs Civ4 itself: load a save or start a new game, autoplay a number of turns, look at the window, close the game and read what happened, without the user at the keyboard.

Built and tested by Claude Code Opus 5.5 on 2026-11-10, from a plan drafted with Codex (GPT-6.1-Sol) and ChatGPT-5.6-Sol's earlier research into launching Civ4 externally.

## Menu

[What an agent can do](#what-an-agent-can-do)\
&emsp;[Who can use them](#who-can-use-them)\
[Before a run](#before-a-run)\
&emsp;[Which DLL to test with](#which-dll-to-test-with)\
[Run autoplay from a save](#run-autoplay-from-a-save)\
[Start a new game](#start-a-new-game)\
[How the request reaches the game](#how-the-request-reaches-the-game)\
[How the run ends](#how-the-run-ends)\
[Two clients at once](#two-clients-at-once)\
[Screenshots and clicks](#screenshots-and-clicks)\
[What did not work, and why](#what-did-not-work-and-why)\
[Limits](#limits)

## What an agent can do

- Launch Civ4 into a save made with this mod, or start a new game with a chosen map, size, speed, difficulty, era and leaders.
- Run AI Auto Play for a requested number of turns, optionally in Debug Mode so a watching user sees the whole map.
- Tell how the run ended: completed, ended early, never started, stalled, crashed or timed out.
- Take screenshots of the game window, even while other windows cover it, and click in it.
- Close Civ4 and collect the run's logs and saves.
- Run two or more clients at once, each with its own logs.
- Do all of this in the background: the game never needs the foreground, and runs went on under other applications such as Chrome, VS Code or File Explorer, so the user can keep working meanwhile. Only a click moves the real mouse pointer, and runs need none.

Everything goes through two Python 3 helpers in [`LLM_Helpers/game_runs/`](/LLM_Helpers/README.md#game_runs): [`run_autoplay.py`](/LLM_Helpers/README.md#run_autoplaypy) for whole runs and [`desktop_windows.py`](/LLM_Helpers/README.md#desktop_windowspy) for the window.

Before them, every autoplay needed the user to start Civ4, load the save, press Ctrl+Shift+X and type a turn count, then exit the game afterward.

### Who can use them

- Any local agent that can run commands on the user's Windows PC, such as Claude Code or Codex. Nothing depends on one agent's own tools: the helpers are plain Python 3 scripts calling Windows itself (`user32`/`gdi32` for windows, input and pictures, and WMI through PowerShell to start Civ4).
- They are Windows-only, as Civ4 is. External agents without the game, such as ChatGPT with a light-source ZIP, can read this guide and the logs a run produced, but cannot run one.
- A person can run them too, for example to start a long autoplay and get a summary without watching it.

## Before a run

Everything here was tested in November 2026 on Windows 10 Pro 22H2 (build 19045.6466) with the Steam edition of Beyond the Sword 3.19. Other Windows versions and other editions, such as GOG's, were not tried.

- **Civ4 closed:** the runner refuses to start while another Civ4 runs, unless `--multiple` says that is intended. Check first that the user is not playing.
- **Runtime diagnostics on:** `SAS_RUNTIME_STATUS_ON=1` in [GlobalDefines_advciv_sas.xml](/Assets/XML/GlobalDefines_advciv_sas.xml), the usual development setting. The runner reads the run's Runtime history to know how it ended.
- **Python 3 with Pillow** for screenshots. Nothing else needs installing.
- **A save made with this mod:** a save names its mod in its header (`Mods\AdvCiv-SAS\`), and the runner refuses one made with another mod.
- **No XML or Python edits during a run**, as for any autoplay; see [Runtime safety](/AGENTS.md#runtime-safety-and-diagnostics).
- **Windowed mode:** the runner always sets `FullScreen = 0` for the run, whatever the user's INI says.
  - A window can be captured, clicked and closed by its handle, never takes over the screen or needs Alt+Tab, and lets two clients sit side by side.
  - Civ4 runs fine in it, and the [Quick Install Setup Guide](/_1_AdvCiv-SAS/Docs/README_Quick_Install_Setup_Guide.md) already recommends it for development and autoplays.
- **Dawn of Man:** it did not block these autoplays; the final screenshots showed the map with no popup.
  - A recheck on 2026-11-11 with `SAS_UI_DAWN_OF_MAN_ON=1` agreed: a loaded save and a new game, run side by side with `--multiple`, each completed 5 turns.
  - A game kept open with `--keep-open`, or loaded just to look, still waits on its Continue button, which the first tests dismissed with a click.
  - `SAS_UI_DAWN_OF_MAN_ON=0` skips the screen. It is a player option like SASFastSave, described in the [Main Changes Guide](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md#system---misc); [`toggle_dev_diagnostics.py`](/LLM_Helpers/README.md#toggle_dev_diagnosticspy) `on` sets it locally.

### Which DLL to test with

Build with the [DLL Compilation Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_DLL_Compilation.md) and copy the DLL into `Assets/` while Civ4 is closed. On 2026-11-10 all three configurations below ran these autoplays:

| Configuration | Build time | Assertions |
| --- | --- | --- |
| `Release` | about 2 minutes | none |
| `Debug-opt` | about 2 minutes | compiled out unless `/DFASSERT_ENABLE` is uncommented in `Makefile.project`; keeps its PDB for crash dumps |
| `Assert-fast` | about 25 seconds, compiled in parallel | on, written to `SASAssertions_*.log` and ignored automatically with the default `SAS_ASSERT_SILENT_ACTION=1`, so they never stop a run |

`build_with_report.ps1 -Configuration Assert-fast` builds the Makefile's `Assert` target. Its `temp_files/Assert` folder can stay afterward: it is git-ignored, and the next `BUILD` refuses to start until it is cleaned, so use `-Request REBUILD` then.

## Run autoplay from a save

```bash
python LLM_Helpers/game_runs/run_autoplay.py "C:/path/to/save.CivBeyondSwordSave" --turns 100
```

- `--turns` counts the loaded turn, so 100 turns from T0 play T0 to T99, as with the Ctrl+Shift+X popup.
- `--debug-mode` turns on Debug Mode before autoplay starts. It seems to change the AI's game ([KI#1080](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1080)), so leave it off when comparing runs.
- `--keep-open` leaves Civ4 running afterward, for example to look around or take more screenshots.
- `--verbose` prints the turn as the run advances.

The save is only read. The runner copies the user's `CivilizationIV.ini` so graphics and sound settings match, and deletes that copy when Civ4 closes.

## Start a new game

```bash
python LLM_Helpers/game_runs/run_autoplay.py --new-game --map Pangaea --world-size WORLDSIZE_STANDARD --era ERA_ANCIENT --handicap HANDICAP_NOBLE --fixed-seeds --leaders "LEADER_ALEXANDER,-,LEADER_MANSA_MUSA" --turns 60
```

- `--new-game` sets the INI's `QuickStart = 1`, which starts a game straight from the INI's `[GAME]` settings, without menus.
- `--map` (script name without `.py`), `--world-size`, `--speed`, `--handicap`, `--era`, `--climate` and `--sea-level` override the user's last settings. Other settings, such as the game options string, come from the user's INI.
- `--fixed-seeds` sets `SyncRandSeed` and `MapRandSeed` to `1`. Two such games on Standard Pangaea matched at every RNG and state checkpoint over 60 turns, so a repeatable benchmark needs no save.
- `--leaders` names a leader for each civilization slot in order, with `-` keeping the random one. Each leader brings the first playable civilization that lists it; a requested leader already drawn for another slot is swapped with it.
  - Tested on 2026-11-10: `LEADER_ALEXANDER,-,LEADER_MANSA_MUSA,LEADER_GANDHI` gave Alexander, a random leader, Mansa Musa and Gandhi, and SGR recorded the three as chosen rather than random.
  - A bad name, such as `LEADER_NOPE` or the civilization `CIVILIZATION_GREEK`, leaves that slot random; the run's outcome is `REQUEST_FAILED`, with the mismatch in `pythonErrors`.
  - It needs a DLL built since SGR199, because the leaders are set in `CvInitCore` before the game starts.

## How the request reaches the game

The runner writes a settings file for the run beside `Civ4BeyondSword.exe`, named `SASAutoplay_<run id>.ini`, and launches:

```text
Civ4BeyondSword.exe /FXSLOAD="C:\path\to\save.CivBeyondSwordSave" ini=SASAutoplay_<run id>.ini
```

- `/FXSLOAD=` is the EXE's own argument for loading a save, found among its strings. It must come first and be quoted: after `ini=`, Civ4 opened at the main menu.
  - CivFanatics threads, found by a web search while building the runner, document the switch too. [Command Line Options](https://forums.civfanatics.com/threads/command-line-options.172014/) (2006) quotes a Firaxis list of options that gives `/FXSLOAD=foo`.
  - In [Windows 10, Civ 4 & file associations](https://forums.civfanatics.com/threads/windows-10-civ-4-file-associations.566100/) (2021), loading a save from a command line worked only with the slash, the equals sign and quotation marks around the path.
  - In [Opening savegames with the correct mod](https://forums.civfanatics.com/threads/opening-savegames-with-the-correct-mod.677580/) (2022), double-clicking a save opened it only once the file association's command passed it with `/fxsload="%1"`.
  - None of them mentions its order relative to `ini=`; our runs found that.
- `ini=` makes Civ4 read that file instead of `CivilizationIV.ini`. It loads `Mods\AdvCiv-SAS` in a window and adds an `[SASAutoplay]` section, which Civ4 itself ignores:

| Key | Meaning |
| --- | --- |
| `Turns` | AI Auto Play turns to run; required |
| `DebugMode` | `1` turns on Debug Mode first |
| `RunId` | the run's ID, logged in SGR's settings snapshot so a run can find its own SGR file |
| `Leaders` | leaders by civilization slot, for a new game |

- [SASAutoplayRequest.py](/Assets/Python/SASAutoplayRequest.py) reads the section once, when the first game loads or starts, and starts autoplay on the next game update.
- Only an explicit `ini=` file is read, so ordinary launches never autoplay. `PythonDbg.log` records `SAS_AUTOPLAY_REQUEST` rows when a request is armed and started.
- Civ4 is started through Windows' WMI, not as a child of the agent's shell: when an agent stopped the shell command that had started Civ4, the game and its Runtime observers were killed with it.

## How the run ends

The runner reads the process's own `SASRuntimeHistory_<processStartUtc>_<pid>.jsonl`. `AUTOPLAY_STARTED` and `AUTOPLAY_ENDED` rows give the start, the end turn and `autoplayEndCause`.

| Outcome | Meaning |
| --- | --- |
| `COMPLETED` | autoplay ended as scheduled |
| `REQUEST_FAILED` | autoplay ran, but the request raised an error, such as leaders not applied |
| `ENDED_EARLY` | autoplay ended for another recorded cause, such as victory, defeat or an assertion |
| `NOT_STARTED` | no autoplay within `--start-minutes` (default 5) |
| `STALLED` | no new history row for `--stall-minutes` (default 15) while autoplaying |
| `FAILURE_DIALOG` | the Runtime dialog observer saw a runtime-error or crash dialog |
| `EXITED` | Civ4 exited before autoplay ended |
| `TIMED_OUT` | `--timeout-minutes` (default 240) passed |

Then it takes a final screenshot and closes Civ4 with `WM_CLOSE`, as the title bar's X does. Civ4 exited with code 0 and no confirmation dialog every time it was tested; the runner forces the process only after 90 seconds.

It writes `SASAutoplay_<run id>.json` to `Logs/` under the Civ4 user folder. For example, the test run's `SASAutoplay_20261111T123518Z_6384.json` identifies a run launched at 12:35:18 UTC by runner PID 6384.

- Optional captures share `Downloads/AdvCiv-SAS_LLM/autoplay_screenshots/`, with names such as `SASAutoplay_<capture UTC>_<Civ4 PID>_final.png`; the [Logging Inventory](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_Logging_Inventory.md#autoplay-run-summary) explains why reports and screenshots are kept apart.
- When reporting an issue, the summary and the game logs are in the same directory. You can sort by date or size and collect the relevant files in one view. If an image would help, add the specific PNG linked from the summary.

The screenshot uses [Windows window capture](#screenshots-and-clicks) on the Civ4 client launched for the run. It leaves the window where it is and sends no screenshot hotkey.

- The summary's `screenshot` field gives the saved PNG path when capture succeeds.
- Use `--no-screenshot` to skip the capture, and `--screenshot-root` to choose another image directory.
- If an image has been archived, search for its filename in the screenshot archive.

The runner exits with code 0 only for `COMPLETED`:

```json
{
  "outcome": "COMPLETED",
  "requestedTurns": 30,
  "startTurn": 0,
  "endTurn": 29,
  "autoplayEndCause": "SCHEDULED",
  "wallSeconds": 18.3,
  "civ4": "CLOSED",
  "exitObservation": {"outcome": "ZERO_EXIT_CODE", "exitCode": 0, "failureDialog": null},
  "gameRecord": "...Logs/SASGameRecord_20261110T165714Z_26088_load1.log",
  "pythonErrors": []
}
```

The summary also lists the Runtime history, the new saves (including SASFastSave's stop save) and the last popup that awaited a choice, if any.

Measured on 2026-11-10 on the development PC with a Huge Pangaea T0 save: 10 turns took 14 seconds from launch to exit, 100 turns about 50 seconds, and 300 turns about 400 seconds with Debug Mode on in a smaller window.

## Two clients at once

Why each client needs its own files: in one test two clients started in the same millisecond and opened their SASGameRecord logs in the same second. With names made only of the time, both would have written into one file, mixing two games. With the process ID in every name, each client knows where to write from its start, without checking what the other does.

Pass `--multiple` to each runner, which adds Civ4's `multiple` launch argument:

```bash
python LLM_Helpers/game_runs/run_autoplay.py save.CivBeyondSwordSave --turns 100 --multiple &
python LLM_Helpers/game_runs/run_autoplay.py save.CivBeyondSwordSave --turns 100 --multiple &
```

Each client's files carry its process ID, so they cannot collide:

| File | Name |
| --- | --- |
| Runtime current state | `SASRuntimeStatus_<processStartUtc>_<pid>.json`; `SASRuntimeStatus.json` shows the latest writer |
| Runtime history, exit, screenshot and source records | `SASRuntime*_<processStartUtc>_<pid>.*` |
| SASGameRecord and BBAI | `SASGameRecord_<UTC>_<pid>_load1.log`, `BBAI_<UTC>_<pid>_new1.log` |
| Assertions | `SASAssertions_<UTC with milliseconds>_<pid>_new1.log` |

- In one test both clients started in the same millisecond and their SGR logs in the same second; before the process ID was added, both would have written to the same SGR file.
- The SGR and BBAI session headers also name `processId` and `processStartUtc`.
- Two clients on the same save matched at every RNG and state checkpoint over 100 turns, so parallel runs are as repeatable as single ones.
- Runtime writes its small status snapshot twice per update, once to the process's own file and once to the shared one for existing readers; updates happen at turn and session boundaries, not every frame, so the extra write costs little.
- Still shared, because Civ4's EXE owns them ([KI#1081](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1081)): autosaves in `Saves/single/auto`, where same-turn names overwrite each other; `PythonDbg.log` and `PythonErr.log`, so a run's `pythonErrors` can include another client's lines; and the user's BUG settings. A request error names its `RunId`, so a runner counts only its own.

## Screenshots and clicks

```bash
python LLM_Helpers/game_runs/desktop_windows.py list
python LLM_Helpers/game_runs/desktop_windows.py screenshot --pid 15692 --out shot.png
python LLM_Helpers/game_runs/desktop_windows.py click --pid 15692 963 809
python LLM_Helpers/game_runs/desktop_windows.py hover --pid 15692 963 809
python LLM_Helpers/game_runs/desktop_windows.py close --pid 15692
```

Other apps' windows, such as Codex's or Claude's, work the same way; see [README_Desktop_Windows.md](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_Desktop_Windows.md).

A screenshot captures only Civ4's window, wherever it is and at its current size, not the whole screen or a fixed area.

- The default `window` method asks the window to draw itself into a picture (Windows' `PrintWindow`). It shows what the game draws, not what is on the screen, so the game need not be in front: a video, a browser or Notepad over it does not appear, and the user can keep working while an agent takes screenshots.
- `--method screen` brings the game to the front, then copies its area of the screen. It shows exactly what a person would see there, but it takes the focus, and anything that pops up over the game in that moment appears in the picture.

Tested on 2026-11-10 during an autoplay:

| Window state | `window` (default) | `screen` |
| --- | --- | --- |
| in front | captured; two captures 3 seconds apart differed as turns advanced | captured |
| covered by Notepad | captured the game, not Notepad | brings the game to the front first |
| moved and resized to 1300x760 | captured at the new size; Civ4 scales its picture down rather than redrawing it | captured |
| minimized | only the 237x39 title bar | not tried |
| after Civ4 exits | nothing to capture; `run_autoplay.py` takes its final screenshot before closing | same |

- Coordinates are physical pixels from the window's top-left corner, as in the screenshots. The tool makes itself DPI-aware first: without that, at 150% display scaling, Windows reported a 1284x747 window for a 1926x1120 one and the first screenshots were cropped.
- A click moves the real mouse pointer and brings the window to the front, so it does interrupt a user working at the PC.
- One click on the Dawn of Man popup's Continue button reached the game. Its position, `963,809` in a 1926x1120 window, was read off a screenshot, so it holds only for that window size and layout; a different resolution, text scale or UI change moves it. Take a screenshot and read the position again before each click, and prefer a request that needs no click, as autoplay itself does.
- `hover` moves the pointer to a point without clicking or focusing the window, so a tooltip appears without disturbing a user typing elsewhere. It refuses a point outside the window.
- Keystrokes did not: simulated Ctrl+Shift+X and Enter never reached the game, so the tool offers none, and the autoplay request avoids the keyboard. Anyone typing at the PC also cannot disturb a run.
- Civ4's own screenshot key, which the Runtime screenshot observer records, was not tried from the tools.

## What did not work, and why

Kept so the next agent does not repeat these steps:

| Tried | What happened | What works |
| --- | --- | --- |
| `/FXSLOAD=<save>` after `ini=`, or unquoted | Civ4 opened at the main menu | `/FXSLOAD="<save>"` first, then `ini=` |
| Keystrokes (`keybd_event`) for Ctrl+Shift+X and Enter | nothing reached the game | the `[SASAutoplay]` request; mouse clicks for anything else |
| Starting Civ4 from the agent's shell command | stopping that command killed Civ4 and its Runtime observers | starting it through WMI, detached |
| Window rectangle without DPI awareness | at 150% scaling, 1284x747 reported for a 1926x1120 window, so screenshots were cropped | `desktop_windows.py` makes itself DPI-aware |
| Reading `PythonErr.log` for request errors with two clients | the other client's error marked a normal run `REQUEST_FAILED` | errors name their `RunId` ([KI#1081](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1081)) |
| The user's INI map `C2C_Arboria` while loading a save | an assertion-enabled DLL raised "Map script not found" at startup | the run's INI sets `Map = Pangaea` for loads |
| A leader name looked up without its type | `getInfoTypeForString` matches any XML type, so a civilization name would pass | the DLL requires a leader whose own type matches |
| Clicking a position read from an earlier screenshot | in the Codex app, the user had closed a side panel meanwhile, so the chat moved and the click selected a word instead of expanding a section | take a fresh screenshot right before each click; any window can change between two steps, and `desktop_windows.py` works on other apps' windows the same way |
| Reporting the last turn seen in the history | a 300-turn run showed T300, a turn after autoplay ended | `endTurn` comes from the `AUTOPLAY_ENDED` row |

## Limits

- Leaders can be chosen only for a new game, by civilization slot. Civilizations follow from leaders, and other game options come from the user's INI.
- Votes, diplomacy and other prompts that need a decision were not met in these runs. One that blocks autoplay would show as `STALLED`, with the waiting popup in the summary.
- Debug Mode seems to change the game ([KI#1080](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1080)).
- The INI's `Autorun` and `AutorunTurnLimit` keys, which ChatGPT's research suggested, were not tried; the `[SASAutoplay]` request worked first.
- Moving units, saving or other in-game actions are possible only through clicks for now.

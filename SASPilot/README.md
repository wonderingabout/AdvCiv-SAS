# SASPilot

SASPilot reads and drives a running Civ4 game for agents, as JSON rather than screenshots and clicks. This README describes its files; the commands, measurements and limits are in the [SASPilot Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot.md).

## Menu

- [Layout](#layout)
- [Piloting a running game](#piloting-a-running-game)
  - [`SASPilotClient.py` and `SASPilotCommands.py`](#saspilotclientpy-and-saspilotcommandspy)

## Layout

- `game/` holds the Python 2.4 files Civ4 loads and runs inside the game, `SASPilotCommands.py` and `SASPilotUI.py`; everything else here is Python 3 run on the desktop, with `checks/` and `sequences/` beside it.
- Why at the root since 2026-11-20, not in `LLM_Helpers/saspilot/` (2026-11-15 to 2026-11-20):
  - The game files are live game code in Python 2.4, unlike the modern-Python desktop tools in `LLM_Helpers/`. They had moved there out of `Assets/` only because saving a `.py` under `Assets` while Civ4 runs makes the EXE reinitialize its Python and breaks the game; outside `Assets`, the root is as safe.
  - A folder of their own lets CI treat them by folder: the Python 2.4 compile check named only `SASPilotCommands.py` there, so `SASPilotUI.py` went unchecked; it now covers all of `game/`.
  - Commands are shorter, such as `python SASPilot/SASPilotClient.py`.
  - The client and helpers stay beside the game files rather than in `LLM_Helpers/`, as both are parts of one feature (Codex, GPT-6.2-Sol); `game/` says where its code runs, as folders here are named by job.
  - The user's idea, agreed with Codex; moved by Claude Code Opus 5.5.

## Piloting a running game

- Why a folder of its own: SASPilot started in `game_runs/` beside the autoplay and click tools, but it is a job of its own, reading and driving a game as JSON, and had grown to seven scripts and two data folders. The user asked for its own folder, `LLM_Helpers/saspilot/`, on 2026-11-15; it moved to the root on 2026-11-20 (see [Layout](#layout)).
  - Inside it the old `pilot_` prefix said nothing, so `pilot_checks/` and `pilot_sequences/` became `checks/` and `sequences/`.
  - The folder was `saspilot/`, now `SASPilot/`, not `pilot/`: a bare "pilot" leaves a reader wondering what it is, while SASPilot names the feature, as SGR and BBAI logging do, and greps as one word (the user's point).
  - `run_autoplay.py` stays in `game_runs/` and `desktop_windows.py` sits in [`desktop/`](/LLM_Helpers/README.md#desktop), as other tools use them too; `SASPilotClient.py` and `SASPilotConsole.py` add those folders to their import path.
- Why `SASPilot<Role>.py`: the console window was already called SASPilotConsole, and the user wanted script and window to share one name, so the other scripts followed.
  - `SASPilotClient.py`, not `SASPilot.py`, for the old `pilot.py`: [`SASPilot.py`](/Assets/Python/SASPilot.py) is already the in-game bridge that answers it, and two files of one name would make every grep and link ambiguous. Client says what it is: the desktop side of that bridge. `Core` or `Main` were considered and said less.
  - A CamelCase name had been avoided at first, lest it read as another in-game file like `SASPilotCommands.py`; the folder now tells them apart, as Civ4 loads only the files in `game/`, and the desktop scripts start with a shebang and argparse.
  - The helpers import the client as `import SASPilotClient as pilot`, so their code still reads `pilot.request(...)`.

### `SASPilotClient.py` and `SASPilotCommands.py`

- `SASPilotClient.py` is the command-line client of SASPilot: it starts a piloted game (`start`), then reads and drives it as JSON, such as `todo`, `units`, `city city=Carthage`, `move unit=16385 x=40 y=28`, `produce`, `research`, `endturn`, `save`, `autoplay`, `info type=UNIT_WARRIOR`, and `py "<code>"` to run Python inside the game. `help` lists the commands.
- `SASPilotCommands.py` holds those commands. It is Python 2.4 run inside Civ4, loaded from `game/` by [SASPilot.py](/Assets/Python/SASPilot.py) and reloaded when it changes, so commands can be added while a game runs. It sits here because the EXE reinitializes its Python when a `.py` under `Assets` changes.
  - It sits in [`game/`](#layout) with `SASPilotUI.py`, which the Python 2.4 compile check covers.
- [`SASPilotUI.py`](/SASPilot/game/SASPilotUI.py) holds the `ui*` commands, which open screens and read and click their widgets by name; `SASPilotCommands.py` loads it from beside itself the same way and adds its commands.
  - Added on 2026-11-20 by Claude Code Opus 5.5 at the user's request; see [Screens and buttons by name](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot.md#screens-and-buttons-by-name-saspilotui).
- SASPilot is off unless `SAS_PILOT_ON` is 1 or the launch INI has `[SASPilot] On = 1`, which `SASPilotClient.py start` writes.
- Commands, measurements, what failed first and the limits (popups, diplomacy, the main menu) are in the [SASPilot Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot.md).
- Written on 2026-11-13 by Claude Code Fable 5.2, when the user asked for a way to pilot the active player from the command line rather than through screenshots and clicks.
- `SASPilotReplay.py` replays a sequence from [`sequences/`](/SASPilot/sequences/), a list of pilot commands against a save, and lists each reply that differs from the last accepted run (`--accept`), so a DLL rebuild or a command edit that changes an answer shows up at once.
  - Added the same day by Claude Code Opus 5.5, after about ten DLL rebuilds checked by hand only; see [Replaying commands](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot.md#replaying-commands).
  - `fogplay_t105_freetech.json` takes the Oracle's free tech at turn 105 of the 2026-11-13 fog-on playthrough; `fogplay_t115_core.json` reads most commands with fog on at turn 115, opens and leaves diplomacy, and ends a turn; `fogplay_t116_queued_build.json` queues a Work Boat's fishing boats behind its move and checks they are built; `fogplay_t148_trade_table.json` puts Navigation on Pacal's trade table and expects his 65-gold counter-offer, which an empty trade table had given away for free. Their saves are local, in `Saves/single`.
- `SASPilotClient.py` appends every request to a per-client command log, `Logs/SASPilot_<processStartUtc>_<pid>.jsonl`, with the agent's `note=` reason; [`SASPilotConsole.py`](/SASPilot/SASPilotConsole.py) opens SASPilotConsole, showing orders by default and reads with `--all`.
  - Added by Claude Code Opus 5.5 on 2026-11-14 so the user can watch an agent play and a game can be reviewed afterwards beside SASGameRecord; see [SASPilotConsole](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot.md#saspilotconsole).
- [`SASPilotScout.py`](/SASPilot/SASPilotScout.py) is a read-only opening experiment for locked play clients.
  - It shortlists frontier destinations from the fogged grid and checks travel times with Civ4's pathfinder.
  - `--around X,Y` (with `--band` and `--ccw`) loops around a city, and each choice gives the best-defended plot to stop on this turn; it refuses a wounded unit and stops near visible animals, rules added after the 2026-11-14 playthroughs lost a Warrior's health to a Lion and a Scout to a Bear.
  - See [the scouting trial](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot_Playtests.md#scouting-trial).
- [`SASPilotExplore.py`](/SASPilot/SASPilotExplore.py) moves several scouting units a turn at a time, each looping around its own center with `SASPilotScout.py`'s choices (`UNIT:X,Y:MIN,MAX[:ccw,nohut]`), one plot per step, huts first, then ends the turn; it stops on a hostile next to a unit and on new messages, reminders or idle units.
  - Grown from a scratch driver over the 2026-11-14 playthroughs; see [the scouting trial](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot_Playtests.md#scouting-trial).
  - Rules added in the Continents replay (2026-11-19), each after a slip the user caught:
    - It keeps a unit's target across turns while it still reveals something: re-ranked from scratch, the target flipped each step and a Warrior circled one spot for six turns.
    - It avoids stopping on the unit's last six plots unless nothing else is left, as back-and-forth reveals nothing.
    - It remembers hostiles seen for five turns and keeps stops two plots from them, not only from those in sight.
    - Avoiding is the default, not a rule against fighting: a hostile next to the unit stops the run with our attack odds on it, and attacking with confident odds is the agent's call when it serves the goal.
    - Its state sits in the temp folder per client, as each run is a new process.
- [`SASPilotWatch.py`](/SASPilot/SASPilotWatch.py) follows a game a person plays in the window, one line per change, with named saves at key moments (`--saves`); see [Watching a person play](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot.md#watching-a-person-play).
- [`SASPilotSites.py`](/SASPilot/SASPilotSites.py) compares candidate city sites from the fogged grid before a Settler exists: resources, fresh water, coast, hill, grassland, overlap, unknown plots and distance to rival borders, with a heuristic score whose parts come from the user's reviews of the same playthroughs. Advice, not fact: it prints the facts beside the score.
  - Since the Continents replay (2026-11-19), where the user named the best site, 21,15, and both this tool and the AI's found value had missed it:
    - It reads `plots` rather than `grid`, as grid gave river edges only for plots in sight, so every site out of sight read "no fresh water".
    - It counts flood plains, oases, river plots and bare desert, and the default reach is 8 plots (was 6).
    - The user's dot-map marks are always rated, at any distance.
    - Each site shows the AI's found value beside its own score, and the nearest rival border with its owner and direction, the lane the user read from Persia's border.
    - Sites within 2 plots of a better one are listed under it as alternatives, one region per entry.
- [`SASPilotPlots.py`](/SASPilot/SASPilotPlots.py) judges plots in numbers rather than pictures, with numpy and scipy, which Civ4's Python 2.4 lacks: `layer` prints food, production, commerce, owner or coast as a grid you can read row by row, or with `--sum` each plot's total over a city radius, and `regions` lists landmasses and unowned clusters with their sizes.
  - With `--potential food,production,commerce`, each plot counts its best improvement by those weights, from the in-game `potential` command (`--later` adds builds a tech away), so a site with two unimproved Clams no longer reads as plain coast.
  - The square is centered on an anchor, `--x/--y`, `--unit`, `--city`, `--bonus` or `--camera`, with `--radius` for its size, so a large map such as SAS48 is read a crop at a time.
  - It reads `plots`, which gives every revealed plot's yields under fog, where `grid` gives them only for plots in sight.
  - Begun at the user's request in the islands replay (2026-11-15), for Workers and military as well as settling.
- [`SASPilotTurns.py`](/SASPilot/SASPilotTurns.py) ends turns until something needs the agent (`todo`'s `blocking`), handling only routine steps: the ships named with `--explorers` scout one plot at a time toward `seareach`'s recommendation; with `--peace-on-contact` a first-contact greeting gets peace; with `--refuse-recommendations` the advisor's production popup is refused; an AI offer of techs we already have is rejected.
  - After each turn it prints only the new reminders and messages.
  - Written in the islands replay (2026-11-15) after the same shell loop had been rewritten many times, and once ended six turns against an open diplomacy screen.
- [`SASPilotSweep.py`](/SASPilot/SASPilotSweep.py) runs `unit` on every unit and `city` on every city of the running game and lists the failures, as a regression check after a DLL or command change; `--commands unit` limits it, and `--player` sweeps another player's under the all role.
  - It prints the player, fog mode and role first: with fog on, another player's units and cities are read only as far as our team sees them (Codex's review).
  - `unit` asks the game about every mission with no target, which a player's clicks never do, and on 2026-11-20 it raised "unidentifiable C++ exception" for units in cities on a turn-402 save: inherited checks read past the map ([KI#1091.3](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1091.3)).
  - Begun as a shell loop typed by hand twice; on the same save, 69 of 108 units failed with the old DLL and none with the fixed one.
- [`checks/`](/SASPilot/checks/) holds snippets run inside the game with `SASPilotClient.py py @<file>`. `trade_items_parity.py` compares the C++ trade table (`getSASPilotTradeItemsJson`) with the Python loop it replaced, for every pair of players, and lists any entry only one side has; written for that port's first test on 2026-11-13 and kept to recheck either side after a change.

```bash
python SASPilot/SASPilotReplay.py SASPilot/sequences/fogplay_t115_core.json
```

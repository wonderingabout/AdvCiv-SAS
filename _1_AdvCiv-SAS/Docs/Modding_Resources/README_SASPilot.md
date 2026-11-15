# AdvCiv-SAS SASPilot Guide

How an AI/LLM helper reads and drives a running game from the command line, as JSON, instead of through screenshots and clicks: unit and city orders, research, end of turn, saves, autoplay, any XML info, and arbitrary Python run inside the game.

Built and tested by Claude Code Fable 5.2 on 2026-11-13, at the user's request for a way to pilot the active player digitally, as research projects did for StarCraft and Dota 2. The mailbox idea comes from CIVAI, whose repository the user keeps at `C:\Users\PC\Downloads\civai-main`; the goal differs: CIVAI makes LLMs fair opponents behind fog of war, while the pilot gives one agent full information and control of the active player, for AI research and for reproducing bugs and crashes.

The video demos cover two stages of the playtest.

- Part 1 covers the early diplomacy playtest and agent review. Video link to add.
- Part 2 covers the longer live playtest and debugging session. Video link to add.

## Menu

[Quick start](#quick-start)\
[How it works](#how-it-works)\
&emsp;[Switching it on](#switching-it-on)\
&emsp;[Changing commands while Civ4 runs](#changing-commands-while-civ4-runs)\
&emsp;[Why Python, and where the DLL comes in](#why-python-and-where-the-dll-comes-in)\
[Commands](#commands)\
&emsp;[Graph queries](#graph-queries)\
&emsp;[Plot grid and trade network](#plot-grid-and-trade-network)\
&emsp;&emsp;[Roles](#roles)\
&emsp;[SASPilotConsole](#saspilotconsole)\
&emsp;[Running Python in the game](#running-python-in-the-game)\
&emsp;[Using it from a script](#using-it-from-a-script)\
&emsp;[Replaying commands](#replaying-commands)\
[Popups](#popups)\
[Loading a save](#loading-a-save)\
[What was measured](#what-was-measured)\
[What did not work, and why](#what-did-not-work-and-why)\
[Limits](#limits)\
[Where to take it](#where-to-take-it)

## Quick start

Run these from `LLM_Helpers/saspilot/`. `start` launches Civ4 with the pilot on and returns once the first turn waits for orders; every other command talks to that client.

```bash
python SASPilotClient.py start --map Pangaea --world-size WORLDSIZE_SMALL --fixed-seeds
```

```bash
python SASPilotClient.py todo
```

```bash
python SASPilotClient.py mission unit=8192 mission=MISSION_FOUND
```

```bash
python SASPilotClient.py produce city=Carthage item=UNIT_WARRIOR
```

```bash
python SASPilotClient.py research tech=TECH_MINING
```

```bash
python SASPilotClient.py move unit=16385 x=40 y=28
```

```bash
python SASPilotClient.py endturn
```

```bash
python SASPilotClient.py close
```

- `SASPilotClient.py help` lists every command with its arguments, straight from the running game.
- `start` first lists the recommended settings for agent runs with their values, `ok` or `WARN`, warning of any not set, such as the Dawn of Man screen or a tech splash, which make the window wait on a Continue button, SASGameRecord off, or in `CivilizationIV.ini` logging, crash dumps, windowed mode or shown Python errors off; `SASPilotClient.py check` prints the same list alone. The values are the development ones from [`toggle_dev_diagnostics.py`](/LLM_Helpers/diagnostics/toggle_dev_diagnostics.py), read from the working tree, which may differ from the committed values players get (the user's suggestion, 2026-11-14).
- Arguments are `key=value`; a value is read as JSON when it parses (`x=12`, `append=true`, `args=[3]`) and as a string otherwise (`item=UNIT_WARRIOR`).
- `--compact` prints one line of JSON; `--pid` picks a client when several are piloted; `--timeout` changes the 60 s wait for a reply.
- `--timing` prints a request's `roundTripMs` and `gameMs` on stderr, and `bench <command> [key=value...] --count N` sends the same request N times and summarizes both; see [What was measured](#what-was-measured).
- `start --save <file>` loads a save instead of a new game; `start --multiple` runs beside other clients, as in the [Game Runs Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_Game_Runs.md#two-clients-at-once).
- The run above is the sequence tested on 2026-11-13: the Settler founded Carthage, the queue and research were set, the warrior walked to its target over two turns, and 22 turns were ended in a row.

`start` lays out SASPilotConsole beside the game as soon as it is ready, and any later command reopens it if it was closed; every client has one (`SAS_PILOT_WATCH=0` only for automated tests that must not open windows). When the user watches you play, keep the camera on your orders too (see [SASPilotConsole](#saspilotconsole)):

```bash
python SASPilotClient.py start --save <save> --fog
```

```bash
python SASPilotClient.py look follow=1
```

- Give the reason for each order with `note="..."`, which the console shows as `why:`. For two clients, start them with `--watch-slots 2 --watch-slot 1` and `--watch-slot 2`; for a client already running, `SASPilotConsole.py --window --pid <pid>` does the same.
- Close the console window when done; the log stays in `Logs/` for review.

## How it works

- [`SASPilot.py`](/Assets/Python/SASPilot.py), in the game, is a small loader hooked to the `gameUpdate` event beside the autoplay request in `AIAutoPlay.py`, and to screen updates in `CvScreensInterface.update`, which come every frame (see [Speed](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot_Performance.md#speed)).
- Each client has a mailbox folder, `SASPilot/<process ID>` beside `CivilizationIV.ini` in `Documents/My Games/beyond the sword`, so several clients can be piloted at once; see [KI#1081](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1081) for why our files are named by process.
- [`SASPilotClient.py`](/LLM_Helpers/saspilot/SASPilotClient.py) writes a request as `req_<id>.json`, whole and then renamed into place. On its next frame the game claims it by renaming it `run_<id>.json`, runs it and writes `rep_<id>.json` the same way: `{"id", "ok", "result" or "error" and "traceback", "gameTurn", "gameMs", "tick"}`, where `tick` names the event that served it.
  - On a timeout the client deletes its `req_` if it is still there, so the command never runs; a `run_` means the game took it, so the error says to check the game's state before retrying.
- The commands themselves are in [`SASPilotCommands.py`](/LLM_Helpers/saspilot/SASPilotCommands.py), which the loader reads from disk; it is Python 2.4, run inside Civ4.
- Commands see everything, without fog of war, and orders are applied directly to the game objects, as a human's are in single player. Network games are untested.
- Python 2.4 has no `json` module, so the command file carries its own small writer and reader.

### Switching it on

- It is off for players. `SASPilotClient.py start` switches it on for its own process by adding an `[SASPilot]` section with `On = 1` to the per-run INI it passes with `ini=`, as the autoplay runner does with `[SASAutoplay]`.
- `SAS_PILOT_ON` in `GlobalDefines_advciv_sas.xml` switches it on for every launch, for example to pilot a game the user started by hand. Keep it at `0` in commits.
- When off, the cost is one comparison per game update and per frame.
- When on, anyone who can write to the mailbox folder can run Python inside the game, which is the point of the tool; it is a local folder of the user's own account.

### Changing commands while Civ4 runs

- Save an edit to `SASPilotCommands.py` and the running game picks it up within a fraction of a second (it compares the file's size and time every 20 updates, about 30 times a second in game). `ping` then shows `reloadError` if the new file failed to load; the previous version keeps serving.
  - The failure is also written to stderr, which the game shows as a Python error in its window. On 2026-11-13 an edit saved a help string with double quotes inside it, the user watching saw the error, and the corrected file loaded 4 seconds later; so an error that appears while an agent edits this file is usually such a transient save, and `PythonErr.log` names the line.
  - Checking the edit first with Python 2.4 (`C:\Python24\python.exe`, as in [Syntax checks](/AGENTS.md#syntax-checks-and-linting)) before relying on the reload catches such a slip, but the Edit tool saves at once, so the game may load the broken version first.
- This is why the command file lives in `LLM_Helpers/saspilot/` and not in `Assets/Python/`; see [What did not work](#what-did-not-work-and-why).
- `SASPilot.py` itself is in `Assets/Python/`, so changing it needs Civ4 closed first, like any mod Python.
- `ping` reports the loaded `PILOT_REVISION`. Keep one revision for the candidate during a draft PR and record its command changes in [SASPilot revisions](/_1_AdvCiv-SAS/Docs/revisions/SASPilot.md).
- A script writing the command file can fail with `OSError: [Errno 22] Invalid argument` while the game has the file open for its reload check; it happened twice on 2026-11-14, and a retry a moment later succeeded. The Edit tool retries on its own.
  - Later the same day the same error came three times when writing `SASPilotClient.py`, which the game never reads, so the game's reload check is not the only cause; some other process held the file a moment. The cause was not found; a retry loop of a few one-second tries always got through.

### Why Python, and where the DLL comes in

The user asked on 2026-11-13 whether the bridge would be faster or more reliable in the DLL.

- The commands are Python because a command can then be added or fixed in a minute, with no compile and without restarting Civ4, and Python already reaches nearly the whole game API.
- The DLL would not answer sooner: the 250 ms wait was how often the game called the bridge, not Python's speed, and a DLL poll at the same place would have waited as long.
  - Measured later the same day (2026-11-13): a ping spent 0.27 ms in the game against 250 ms round trip. Serving on every frame instead brought it to 2 ms, and a faster JSON writer brought 441 plots from 250 ms to 12 ms, both in Python; see [What was measured](#what-was-measured).
  - Reading the game data itself took 3 ms for 441 plots, so a C++ version of the reads looked likely to save only a few ms.
  - Correction after a C++ prototype the same day: C++ did both reading and writing the JSON in 0.32 ms against Python's 8 ms, but a bridge served from the DLL alone still waited about 200 ms, as the EXE calls the DLL only about four times a second. See [Would the DLL be faster?](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot_Performance.md#would-the-dll-be-faster).
- The DLL is needed for reach: what Python cannot see or do at all. Popups were the first case, so `CyGame` gained `getSASPilotPopups`, `closeSASPilotPopups` and `answerSASPilotPopup`; deals and a hook at the main menu would be next.
- So the split is: small DLL bindings for what Python lacks, and the commands themselves in Python on top of them.

## Commands

| Command | What it does |
| --- | --- |
| `ping` | bridge revision, PID, whether a game runs, turn, year, active player, whether it is that player's turn, autoplay turns left, map, and the difficulty (`handicap`, `playerHandicap`), as the Victory screen shows it: the user asked whether the pilot played Monarch or Noble (Noble, 2026-11-14) |
| `todo` | what waits for orders: cities with an empty queue, missing research, units ready to move with no mission and not automated, and held popups that ask for a choice; also an open diplomacy screen, and a city screen left open over the map (`cityScreen`), as a spy's Investigate City leaves one, and any advisor or other screen left open (`openScreens`) |
| `closescreens` | close the screens left open in the window, all or one `name=` as `todo`'s `openScreens` names it, as Esc or their Exit button does: the pilot could open an advisor with `control` or `screen` but not close it, and the user saw a Foreign Advisor left open by a test (2026-11-14) |
| `turn` | what a person sees as a turn starts: turn, year, `todo` and the messages since the previous turn |
| `player`, `players` | gold, rates, research, civics, religion, counts, wars; one player or all. Under fog, `players` gives other teams' players only once met, with their ID, name, civilization, team and whether alive, as the scoreboard does: it gave every civilization in full, unmet ones included (Codex's review, round 32) |
| `units`, `unit` | a player's units briefly, or every living player's with `player=all`; one unit in full, with the missions, builds, commands, promotions and upgrades it can take now |
| `cities`, `city` | a player's cities briefly; one city in full, with what it can train, construct, create, maintain or hurry now, and as the city screen shows them its trade routes (each partner and the commerce it brings), defense and bombard damage, and Great People progress. The user asked at turn 141 of the turn-0 game whether the pilot had the city screen's details: London then traded with York for 1 commerce and, after Currency, with Pericles's Sparta for 3, as foreign routes need foreign cities we have seen |
| `plot`, `plots` | terrain, feature, bonus, improvement, route, owner, yields and units of one plot or of a square of plots; with fog on, only what the team knows (see [Playing as a person would](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot_Playtests.md#playing-as-a-person-would)). Center `plots` on `x=` and `y=`, or use `unit=` or `city=` with `radius=` |
| `grid` | an inclusive rectangle or the whole map, with canonical plot coordinates, terrain, fog and optional trade-network edges. See [Plot grid and trade network](#plot-grid-and-trade-network) |
| `fog` | switch between the full view (default) and what the active player's team knows or sees |
| `path` | the route a unit would take to a plot before ordering it: each step's plot, turn and moves left, and the total turns |
| `messages` | the messages the game showed the player at the top of the screen and still lists, such as combat results |
| `citizens`, `work`, `specialist`, `emphasize` | the city screen: worked plots, specialists, governor and emphasis buttons, and the clicks that change them |
| `civics`, `sliders`, `religion` | the civic options with what can be adopted, the commerce percentages, the state religion; each also makes the change |
| `types`, `pedia` | the XML types of one kind, and a type's Sevopedia text: its name and the effects text the DLL composes |
| `info` | any XML info by type, such as `type=UNIT_WARRIOR` or `type=BUILDINGCLASS_PALACE`: every simple getter of its info object, which is the data the Sevopedia shows |
| `mission`, `move` | give a unit's group a mission (`MISSION_FOUND`, `MISSION_FORTIFY`, `MISSION_BUILD data1=BUILD_FARM`...); `move` is `MISSION_MOVE_TO` after a path check; with `append=1` the mission is checked where the queue ends; a unit with no moves left takes a new order too, starting next turn, as in the window (a Worker's replacement queue was refused as "moves left 0", 2026-11-14) |
| `builds` | what a unit could build on a plot, with turns, the improvement or route, and the improvement's yield change; with `refused=1`, also each build the plot refuses and why, in `CvPlayer::canBuild`'s order: the plot's own check first (an improvement the plot cannot have, a feature that unclaimed land cannot have removed (advc.119; in SAS a road drains Marsh, which is why a road at 26,28 of the turn-0 game was refused), or another team's land), then a missing tech, a missing feature tech, and gold with inflation, nothing for a build already begun. The first version asked the tech first and took the XML gold cost (Codex's review, round 32) |
| `sites` | the recommended city sites the window circles for a selected Settler, with found value and path turns |
| `mark` | a sign with text on a plot and, by default, dots over its city radius, so a candidate city site shows on screen; `grid` lists the marks too, so the agent's analysis and the screen show the same sites; `clear=1` removes them. The user's idea in the scouting trial (2026-11-14), when the agent compared sites only in JSON and the user could not see which plots it meant. Cosmetic: nothing in the game changes |
| `odds` | the combat odds the window shows when a unit is pointed at a plot: the defender the game would pick, strengths, and the chance to win in per mille |
| `group` | group a unit with another on its plot, as selecting both does, so they move as one; without `with=`, split it off |
| `diplo`, `reply`, `contact` | the diplomacy screen as the window shows it: the AI's line, the numbered replies and the screen's number; `reply n= screen=` answers one as a click does, refused if the screen has changed since, and `comment=` names the reply instead of its number (`comment=COMPLETE_DEAL`), which is safer: at turn 128 of the turn-0 game the agent sent `n=1` meaning "What would make this deal work?", but with only our Pig on the table the list was FISH_FOR_DEAL, GIFT, and the Pig went to Gilgamesh as a gift; `contact` opens the screen with a leader, and with `give=`/`take=` on its trade table with that deal on it |
| `freetech` | choose a free tech such as the Oracle's, while one is owed |
| `trade` | the diplomacy screen's table with another player: what each side could give, the AI's refusal reason per item (`DENIAL_` type), and its attitude |
| `propose` | propose a deal to an AI, as the Propose button does: `give=[...] take=[...]` with items as `trade` lists them; an accepted deal is made |
| `techs` | the tech market across the players met: each tech we lack that a rival holds, with its cost, whether SAS's XML lets it be traded at all (`bTrade`, off for 32 techs such as Bronze Working, Engineering and Chivalry), and per holder whether it can go in a deal, the AI's refusal and whether it will talk; then what we could give each, with the gold each could pay at once (`maxGoldTrade`, the tab's coin column); and `nobodyHas`, the techs we can research that none of them holds, with `unseenPlayers` counting met players whose techs the fog hides. Under fog, as the Foreign Advisor's tech tab shows it. The user pointed out at turn 139 of the turn-0 game that the agent kept researching techs every neighbour had, which trade buys far cheaper, while a tech nobody has trades to several leaders; at that turn Navigation was the only one |
| `SASPilotClient.py price` | an AI's price, as "What do you want for this?" gives it: `price with=2 take=["TRADE_TECHNOLOGIES:TECH_MACHINERY"]` puts the items on the table, reads the counter-offer and leaves with nothing agreed; `accept=1` takes it (reported as `acceptSent`: read the result back). It stops if another leader's screen or a new conversation takes over. A client-side sequence of `contact`, `diplo` and `reply`. It leaves by Reject or Never mind before Exit and checks a second later that the screen stayed closed: Exit straight from a trade table after a refusal reported it closed, but the table came back and blocked the next call (2026-11-14) |
| `SASPilotClient.py leave` | click through diplomacy screens that only inform (thanks, a cancelled deal, a war declaration) with their exit reply, as a person does, and stop at the first screen with a choice (a deal, peace, a demand), returned for the agent to answer. On turn 289 (2026-11-14) Kublai's declaration, a thanks and two cancelled deals queued up one after another, each needing a `diplo` and a `reply` |
| `look` | turn the window's camera to a plot, a unit or a city; following is on by default since the user, watching the Orleans attack (turn 129 of the turn-0 game, 2026-11-14), asked for it without anyone switching it on (`follow=0` stops it): it makes each `move` and attack look at its destination first, and each order on one of our units or cities (`mission`, `command`, `produce`, `hurry`, `spy`...) look at it, so a person watching sees the action; only our own units and cities, so fog hides nothing more than in the window |
| `command` | a unit command, such as `COMMAND_PROMOTION data1=PROMOTION_COMBAT1`, `COMMAND_AUTOMATE data1=AUTOMATE_EXPLORE` or `COMMAND_DELETE confirm=1`. Deleting needs `confirm=1` or `true`, as the window asks: at turn 90 of the turn-0 game the agent sent `COMMAND_DELETE` to two new Workers meaning to clear their queues, and lost one (a new mission without `append=1` clears a queue) |
| `produce`, `hurry` | set or append a city's production; hurry it, or without `hurry=` list the ways with their gold and population costs (gold needs Universal Suffrage, population Slavery) |
| `research` | the techs available now with turns, and the queue; or research a tech, queueing missing prerequisites first, `append=1` to add. Use `effects=1` to include each available tech's rules and unlocks. `ahead=N` lists every tech at most N techs away in the tree's column and row order, with era, steps, beakers and turns, the techs on the way, its OR alternatives, what it unlocks or reveals, and the met players seen to hold it, to plan by proximity; `rivals` gives each met player's current research and percent when espionage shows it, as the scoreboard does, else `unknown` |
| `tech` | one tech's effects and requirements, with the selected team's cost, progress and missing immediate prerequisites, and its `path`: every tech still to research, prerequisites first, in the order `research` queues them, with beakers and turns each and in total. Effects say `leadsTo` for later techs and `prerequisite` for what it unlocks |
| `graph` | the tech tree, promotion prerequisites, unit upgrade paths, current diplomatic relations or completed-turn Info graphs as JSON. See [Graph queries](#graph-queries) |
| `endturn` | end the turn, reporting what was left (`skipped`); the client then waits for the next turn and prints its `turn` digest, unless `--no-wait`; `--turns N` keeps ending turns until something waits |
| `autoplay` | AI Auto Play for a number of turns; follow with `SASPilotClient.py wait` |
| `save` | save; through `SASPilotClient.py` a bare name goes to `Saves/single`; an existing file needs `overwrite=true` |
| `menu` | leave the game: with `path=`, load that save in the same process and wait until it is ready (`--no-wait` returns at once); without, go to the main menu. In a big late game, close and `start --save` instead: leaving a Huge turn-305 game crashed Civ4 ([KI#1084](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1084)) |
| `control` | any `ControlTypes` entry, as its hotkey would: `CONTROL_DOMESTIC_SCREEN`, `CONTROL_WORLD_BUILDER`, `CONTROL_QUICK_SAVE`...; a number works too, and the role check resolves it first, as `control=57` (the WorldBuilder) passed the play role when it compared names (Codex's review, round 32) |
| `screen` | call a `CvScreensInterface` function, such as `name=pediaJumpToUnit args=[29]`, to show an advisor or Sevopedia page in the window; under `play` and `assist`, only `show*` and `pedia*` functions, without the WorldBuilder's and the debug screen, as `name=WorldBuilderRevealAllCB` would reveal the map; the Foreign Advisor also takes its tab number (`name=showForeignAdvisorScreen args=[5]` opens Glance), a click a player makes |
| `batch` | several commands in one request |
| `py` | run Python inside the game |
| `profile` | run a command and split its time into reading the game (`gatherMs`) and writing the JSON (`encodeMs`) |
| `popups` | the active player's popups held back from the window, plus any displayed or queued; see [Popups](#popups) |
| `answer` | answer a held popup as if one of its buttons were clicked: `id=` from `popups`, `button=` by number or name (`button=RAZE`), `text=` for an edit box |
| `closepopups` | drop held and queued popups, all or of one `type=` |
| `dequeue` | remove one entry from a city's build queue by position, as clicking it in the city screen does |
| `espionage` | the espionage screen: per team met, our points against it, our spending weight and its counterespionage against us; `team=` with `weight=` sets a weight |
| `spy` | what a spy could do where it stands, as the espionage popups offer it: the plot's owner (`target`), our points against that team, and each affordable mission with its cost and targets; run one with `mission=MISSION_ESPIONAGE data1=<mission> data2=<data>`. An empty list with few `points` means no mission is affordable, as at Madrid with 40 points against Kublai (2026-11-14); `blocked` names why a spy can do nothing this turn: it moved (a spy acts only on a turn it has not moved), attacked, or the target team sees it |
| `relations` | per player met: attitude, will to talk, war, treaties, open borders, defensive pact, closest city distance, cities within 10 plots, score, power (fog off), and `viewsOf`, each leader's attitude toward every other, which is not symmetric. Also `powerRatioPerMille`, their power against ours as the scoreboard shows it beside each leader (1488 is 1.488 times ours), wherever the scoreboard shows it (`canSeeDemographics`), and `attitudeModifiers`, the hover's lines such as "+1: Years of peace" or "-1: You're getting ahead of us": the user pointed to both at turn 90 of the turn-0 game, when every rival was 1.2 to 2.2 times stronger. Under fog, only cities whose city, not just plot, the team has revealed count (Codex's review, round 35). `attitudeValue` and each `viewsOf` cell carry the Foreign Advisor Glance tab's number (the sum of the hover's modifiers, as BUG's AttitudeUtil reads it), with `worstEnemy`, `atWar`, `peaceTreaty` and `wouldJoinWarIfAsked` (advc.152): the user had the agent compare the reply with the Glance tab at turn 127 of the turn-0 game, which showed +11 and -5 where the reply had only Friendly and Annoyed, and the numbers and icons pick a war target and its likely friends |
| `deals` | our running deals, as the Foreign Advisor lists them: the leader, the turn each began, `turnsToCancel` and what each side gives. A resource we export leaves our network, as `CvPlot::updatePlotGroupBonus` subtracts the capital's exports, so `resources` shows it unconnected: at turn 125 of the turn-0 game the mined Iron beside London read unconnected for seven turns, and `deals` showed it had gone to Gilgamesh inside the turn-118 Pig sale |
| `canceldeal` | cancel one of our deals as the Foreign Advisor's cancel does: it raises the window's `BUTTONPOPUP_DEAL_CANCELED`, which `answer` confirms (`CANCEL_DEAL`) or declines; refused before `turnsToCancel` reaches 0 and for deals holding a vassal item, as `CvDeal::isCancelable` is not exposed to Python. The Iron came back at turn 128 this way |
| `trainable` | the units a city can train now, for value per hammer: turns, cost, strength, moves, strength per 100 hammers, and what strength leaves out (first strikes, collateral damage and reach, withdrawal, bombard, city attack and defense, bonuses against unit types). The user's advice at turn 100 of the turn-0 game: weigh strength against cost, as an Axeman for 35 hammers is strong early, and the effects, as a Trebuchet's strength is low. Axeman and Spearman gave 1428 per 100 hammers, the Longbowman and Catapult 1000 |
| `bonustrade` | the Foreign Advisor's Bonuses tab: our resources with how many we have and who would import each, and per leader met whether our networks connect, the most gold per turn they would pay, and what they would import, will export, won't export and we don't need, by the tab's own tests (CvForeignAdvisor.drawResourceDeals). The user advised trading spare copies actively (turn 111 of the turn-0 game, 2026-11-14): asking leaders one by one with `price` had found only that nobody wanted a Pig, while the table showed Louis importing Wine, our second copy, which then sold for 4 gold a turn. The hover's per-resource price ("Will import: Pericles (6), Zara Yaqob (8)" over Rice, from `CvPlayerAI::AI_goldForBonus`) is not exposed to Python; `price` gives the price of one deal |
| `scores` | the SAS Info screen's Score tab: per player met and ourselves, score and its change since last turn, techs known, land share in per mille, power and power per city where the demographics are visible, cities seen, state religion and holy city, vassal status, will to talk, and research where espionage shows it. The user pointed to the tab at turn 150 of the turn-0 game: it showed at once that we knew 27 techs against 29 to 37 for every rival. Also every other column of the tab: traits, land to the hundredth of a percent, masters and vassals, and per rival the power ratio, attitude and its value, worst enemy, war, peace treaty, trade network, open borders, defensive pact, golden age or anarchy and our espionage weight; checked column by column against the tab at turn 200 of a Large autoplay (2026-11-15). `sort=<field>` or `sort=-<field>` sorts as a column header does |
| `demographics` | the Info screen's Demographics tab: soldiers, land, population, economy, industry and agriculture, with our value and rank, and the rivals' best, worst and average, under fog by the tab's own rules (rank among met players, best and worst among those whose demographics we see, average above 3 rivals, rounded) |
| `finance`, `domestic`, `military` | the Finance tab's numbers; the Domestic Advisor's per-city overview, with `coastal` per city and a `summary` (cities, coastal, unhealthy or at the health cap, unhappy or at the happy cap, starving), as the user asked at turn 156 of the turn-0 game how many coastal cities we have and which cities need health, and from the advisor's other overview pages each city's defense %, garrison, revolt chance in per mille (Orleans's 9.2% at turn 139 had been learned only from a turn message), food stored against the growth threshold, war weariness and the turn founded; at turn 157 they showed 16 units idle in Orleans and one in London; the Military Advisor's units by domain and place, wounded, upgradeable now with the cheapest cost, Great General progress and walls |
| `targets` | the plots a unit could pick for an interface mode from `unit`'s `targetModes` (recon, air bomb, air strike, rebase, paradrop, airlift, ranged attack, nuke), as the window highlights them, with the mission to send; under fog, revealed plots only. Without `mode=`, the unit's modes. A Jet Fighter's recon flew this way on turn 285 (2026-11-14) |
| `settle` | give every idle group Fortify, else Sleep, else Skip, once per group, as a player does before ending the turn |
| `routes` | a text map of the player's land, one row per map row from the north: `C` city, `#` railroad, `=` road, `.` own land with no route, `~` own water, `x` another's land, `?` unrevealed under fog; plus each city's connection to the capital. Under fog, only our own team: `player=` naming a rival still drew the map's edges from all its plots and listed its cities (Codex's review, 2026-11-14) |
| `map` | a text map of the known world, one character per plot: `C` our city, `c` another's, `~` water, `^` peak, `h` hills, `f` forest or jungle, `x` another's land, `u` one of our units, space unknown; under fog, only revealed plots, with their last-seen owners. Made for an opening's scouting and city sites: at turn 25 of the turn-0 game only 150 of 3168 plots were known |
| `resources` | every resource the team knows of, with its owner, improvement and each build that connects it, with the build's tech and whether we have it: at turn 37 of the turn-0 game it showed that SAS's Agriculture opens the Banana's Plantation and five more resources nearby, so Agriculture went ahead of Masonry (the user's advice: check resources first). `connected` on our own plots says whether the plot supplies its resource: at turn 90 the Banana, the Copper and two Pigs were improved but unconnected, with no road from their plots to a city, which the user saw before the agent did |
| `reminders` | what the game does not announce but a player would want pointed out, as small checks: no research, an empty build queue, a starving or angry city, a wounded unit outside our borders, gold running out within ten turns, techs a met player could be offered, and screens or popups left open in the window, which the user noticed before the pilot did (2026-11-14). Each turn's digest carries them, and `endturn --brief` prints them as `remind:` when they change. Added when the user noted that a missed choice can cost a turn the game never mentions; Seafaring, 2 turns of research no neighbour had, then bought Construction and Metal Casting (2026-11-14). A `losses` check lists our units destroyed or captured since the previous turn: two Workers killed by a barbarian Archer went unnoticed when the agent cut each digest to its last lines. An `unfinished` check lists builds a city has hammers in but is not making, as a city keeps them after switching (the user's advice: a Worker one turn from done is worth finishing). An `unimproved` check lists resources inside our borders that supply nothing though we have the tech for a build that would connect them, such as the Clam at 22,31 of the turn-0 game, outside every city's radius but in our borders, which the user pointed out a cheap Work Boat connects for health (turn 156); it also catches an improvement pillaged by barbarians or rivals, and names a worker of ours already headed there (`unitOnTheWay`, where its group's mission queue ends), as at turn 160 the agent queued a second Work Boat for the Clam while the first was one plot away. A `sleepingWorkers` check lists Workers asleep, as a sleeping unit is not idle and appears nowhere else: three slept near York from turn 155 to 160 while the user saw York under-improved. An `exports` check lists resources we give away in a deal while none is left for ourselves, as the Iron was from turn 118 to 128 of the turn-0 game, with nothing in the game saying so. Added in the scouting trial and the Continents game (2026-11-14), each after a slip the user caught: `idleImprovements` (an improved plot no city works while the city works an unimproved one: the Clam's boats sat unworked six turns with the governor off), `scoutBeforeFounding` (no city yet and units with moves left besides the Settler), `exposed` (a unit within two plots of a visible animal or barbarian: a Scout died beside a Bear), `huts` (every goody hut seen, with our nearest unit), `idleGarrison` (military units waiting in a city, with the nearest foreign unit and how much of the map is revealed; usually they should explore early, not always); `unimproved` also names a unit for it already in a city's queue (`inProduction`) |
| `role` | the session's role, the user's idea (2026-11-14): `play` allows what a player sees and does, keeps fog on and refuses `py`, the WorldBuilder, `fog=0` and orders or reads with another team's `player=`, in `batch` and `profile` too; `assist` adds advice to `play`; `all`, the default, allows everything. `lock=1` holds the role until Civ4 closes, and `start --role` locks it. See [Roles](#roles) below |
| `advise` | advice, a heuristic of ours that may be wrong, naming its rule in each reply: `about=scout` ranks `scout`'s steps; `about=threats` weighs each animal and barbarian within 4 plots of a unit and says which to `avoid`. See [Roles](#roles) below |
| `SASPilotClient.py health` | the pilot's own state in one reply, the user's idea (2026-11-14): the bridge's tick errors, settings not at their recommended values, this session's errors and `py` snippets, operators present, role and fog, and whether SASPilotConsole follows the client; `problems` lists what needs a look and is empty when all is well |
| `scout` | each plot a scout could step to now, with how many unknown plots it would reveal, its defense bonus and the animals and barbarians seen within two plots, in a fixed order; the choice stays the agent's, as automated exploring lost a Warrior that fought on at 15 HP. Its ranking moved to `advise about=scout` with the facts-versus-advice split |
| `greatpeople` | Great People planning: the threshold, per city its points, points per turn, rate modifier, turns left and the mix of types with each one's chance (`chancePctX100`), as the city screen's bar shows; and the techs whose first discoverer gets a free Great Person that nobody has yet |
| `workers` | planning Workers by hand instead of automating them: without `city=`, each Worker with its mission, per city the worked plots left unimproved and the city AI's three most valued builds, and per leader we can trade with whether their capital is on our trade network (a missing road link means no foreign trade routes); with `city=`, each plot's terrain, feature, bonus, river, improvement, route and yields, the city AI's best build and value (`getSASPilotCityBuildsJson`, as Python had no getter), and every improvement a Worker could build with its yield change and turns. The AI's choice is a reference to compare with, as the user wanted the pilot to decide as a player (2026-11-14); as advice no screen shows, it is left out unless the session's role allows advice |

- Types are passed and returned as XML types (`UNIT_WARRIOR`, `TECH_MINING`), never as numbers or translated names.
- Unit and city IDs are per player; `player=` selects another player than the active one, for reading and for orders alike.
- A reply that names another player gives its ID with the leader's name and civilization XML type, such as `contact`'s `{"contacted": {"player": 2, "name": "Kublai Khan", "civ": "CIVILIZATION_MONGOL"}}`; only the ID is unique, as with duplicate leaders or civilizations allowed two players can share both (2026-11-14). Unit and city rows keep a bare `owner` number, as naming it in every row would swell large replies; `players` maps the numbers.
- An order's reply shows the state at the moment the order was given. A mission is carried out on the following game updates: right after `MISSION_FOUND` the reply still showed the Settler, and the city existed a moment later. Read again before relying on the result.
- A `MISSION_MOVE_TO` longer than the unit's moves continues when the turn ends, as it does for a human's unit.
- `start`, `list`, `wait` and `close` are handled by `SASPilotClient.py` itself and are not in `help`.

### Graph queries

Fetch the full rules graph once when planning across several turns, then use a type filter for an individual lookup. The Pilot builds the three rules graphs from the running game's loaded definitions and caches them for the lifetime of the command module. Tech effects and upgrades use the selected player's civilization, so unique units and buildings appear in place of their generic counterparts.

```powershell
python SASPilotClient.py graph kind=tech
python SASPilotClient.py tech type=TECH_AGRICULTURE
python SASPilotClient.py graph kind=promotions type=PROMOTION_COMBAT1
python SASPilotClient.py graph kind=upgrades type=UNIT_WARRIOR
python SASPilotClient.py graph kind=relations fog=1
python SASPilotClient.py graph kind=history metric=power start=100 end=150 fog=1
python SASPilotClient.py plots x=26 y=27 radius=2 fog=1
```

- The tech graph has the F6 grid coordinates, separate required-all and required-any prerequisite groups, and named effects. Agriculture, for example, can enable a worker build and separately satisfy the technology requirement for connecting a resource. The `tech` command adds current research progress and can expose other missing tech prerequisites for a unit or building. Training or construction can still depend on the city, resources, and other conditions.
- Promotions include mandatory and alternative promotions, required technology and state religion, and eligible unit combat classes. Unit upgrades link direct destinations with the appropriate civilization replacements. A single-node lookup also lists incoming links.
- The relations graph is fetched live. Nodes are keyed by player ID, and directed edges preserve cases such as one leader liking another more than the feeling is returned, or a vassal pointing to its master. The graph combines the F3 Relations links with attitude details from Glance and omits uncontacted pairs.
- The Info graphs offer `score`, `economy`, `industry`, `agriculture`, `power`, `culture` and `espionage` by player and completed turn. With fog on, rival series follow the advisor's demographics and partial-score rules.
- Use `plots` for structured spatial data alongside those graphs. Its coordinates and plot fields can be indexed directly while the same fog settings apply.

### Plot grid and trade network

Use `grid` for spatial analysis. It gives the requested bounds, map size, wrapping flags, sparse plot rows keyed by coordinates, and trade links between neighboring plots. Request an inclusive `box=[west,south,east,north]`, center on `x=` and `y=`, `city=` or `unit=` with `radius=`, or omit the area to get the full map. Radius clips at the map boundary. Pass `network=0` when the calculation needs only tile data.

```powershell
python SASPilotClient.py grid 'box=[19,21,30,32]' fog=1 network=0 > grid.json
```

Run this from `LLM_Helpers/saspilot`. An agent can load the JSON into desktop Python, index the tiles by `(x, y)`, compute features for every candidate in the rectangle, and print only the matching plots or aggregate results. For repeated neighborhood scans, use separate numeric arrays for each yield and Boolean masks for land, hills and visibility. Track missing tiles in the mask so an unknown yield stays distinct from a known zero.

- With `fog=1`, unexplored plots have no rows. Explored plots outside current sight retain remembered ownership, route and improvement data. Fields without a last-seen accessor, including current yields and network membership, appear only where the team sees now.
- For network analysis, use `tradeLinks` as edges between coordinate pairs. Each edge comes from the engine's connectivity rules, which can join rivers and water as well as routes. The crop and fog can exclude parts of a path. For capital connectivity, use the engine's `capitalNetwork` result for eligible plots rather than inferring it from a cropped graph.
- On a client whose role permits `fog=0`, the full view includes unrevealed tiles. The selected team's trade-network rules still include its exploration requirement. The text `map` and `routes` commands remain available for compact logs.

The scouting helpers built on `grid` came from the [scouting trial](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot_Playtests.md#scouting-trial), recorded with its lessons in SASPilot Playtests.

#### Roles

- Each command has a role, shown by `role`: play (what a player sees and does), advice, omniscient (seeing past the fog), create (changing the game beyond play, as the WorldBuilder or `py`) or meta (running the session). The user's idea, 2026-11-14.
  - Some depend on their arguments: `fog=0` is omniscient; `control` is resolved to its value first, as `control=57` (the WorldBuilder) passed the play role when names were compared (Codex's review, round 32); `screen` is play only for the advisors and Sevopedia navigation without arguments, as `showReplay` passed a player index to native code unchecked (round 33).
- Facts and advice are kept apart, the user's next idea the same day.
  - `play` commands state what the game shows a player, the same for anyone who can see it, and rarely change.
  - `advice` commands weigh facts into a recommendation by a heuristic of ours, which may be wrong and gets tuned as we learn. Each reply names its rule and shows the facts it weighed.
  - A command of its own, `advise`, so tuning a rule never changes the fact commands that replays compare. `scout` lost its ranking to `advise about=scout`; `workers` leaves out the city AI's builds unless advice is allowed, as no screen shows them; `sites` stays play, as the window circles those sites for any player.
  - `advise about=threats` is the user's own rule: avoid an animal faster than you while you are weaker, as animals are strong in SAS and give little. It gives each unit's moves and strength, whether it could attack ours this turn on open ground, the odds both ways (null for an attack that cannot happen, such as by a Settler or across domains, after Codex's review), and `avoid`.
- The session's role decides what runs:
  - `play` gets facts only, which shows what an agent works out by itself; `assist` adds advice, so the log shows which advice an agent asked for; `all`, the default, allows everything.
  - Under `play` and `assist`, fog stays on, and `player=` naming another team is refused.
  - `SASPilotClient.py start --role play` sets it from the first command, and the game banner records it.
  - `role set=<role> lock=1` holds the role until Civ4 closes. `start --role` writes it into the per-run INI, which the bridge applies, locked, before its first request: set by a request after the game was ready, a second client could act first (Codex's review, round 33), and `role set=all` could lift it (round 32).
  - A refusal names the roles that would allow the command.

### SASPilotConsole

SASPilotConsole shows the command log for a running Civ4 client. This full console capture from the England playthrough shows orders, results, numbered `why` notes, and a refused mission. It predates the SASPilotConsole title bar.

<img src="/_1_AdvCiv-SAS/Images/LLM/pilot/llm_sasSASPilotConsole.PNG" alt="llm_sasSASPilotConsole.PNG" width="750">

Every request `SASPilotClient.py` sends is appended to `Logs/SASPilot_<processStartUtc>_<pid>.jsonl`, named per client like the other per-process logs ([KI#1081](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1081)): its time, turn, command, arguments, `kind` (`read` or `order`), and its result, cut at 1,500 characters, or its error.

```bash
python LLM_Helpers/saspilot/SASPilotConsole.py
```

- `SASPilotConsole.py` follows the newest log, like `tail -f`, and prints each order with its turn and result; `--all` adds the reads, `--from-start` the earlier lines, `--pid` picks a client; results and arguments show whole, `--width 160` cuts them (the log keeps at most 1,500 characters of a result).
- The log is for agents first, one JSON object per line to grep or parse, so it stays compact; a result cut at 1,500 characters keeps its size, and the same command gives it again. The console is the human view: one line per command, or `--pretty` for indented results cut at `--max-lines` (default 40), as a nested reply such as `workers city=Hippo` was hard to read on one line (2026-11-14).
- A `=== <date> (UTC) ===` line marks each new day. Each line starts with the UTC time to the millisecond and `T<turn>-<n>`, the request's number within that turn (`T285-00012`, five digits so a long turn cannot outgrow it; `seq` in the log counts across turns): several commands often land in one second, and the user wanted lines that can be cited exactly (2026-11-14).
- `SASPilotConsole.py --window --pid <civ4 pid>` opens SASPilotConsole in its own window and lays the desktop out: Civ4 at its own size in the top-left corner, the console filling the rest of the screen to its right. `--slots 2 --slot 1` and `--slot 2` split the monitor into one band per client for two clients run with `multiple`.
  - Set up at the user's 3840x2160 monitor with a 1920x1110 Civ4 window; halving the screen with `desktop_windows.py move` had stretched Civ4 to 1920x2100 instead. Other resolutions were not tried. `desktop_windows.py move topleft` and `move beside --beside <pid>` do the same by hand.
- `note=<why>` on any command, or `--note`, writes the agent's reason beside it, shown as `why:`; it is taken out before the request, so the game never sees it.
- Why: the user had nothing to watch while an agent played, as replies are deleted once read, and a game reviewed later lacked the orders and their reasons to set beside SASGameRecord (2026-11-14).
- The log costs the game nothing, as the client writes it, and the client about 0.2 ms a command, against about 7 ms for the request itself (measured 2026-11-14); `SAS_PILOT_LOG=0` in the environment switches it off.
- Pings `wait_for_turn` sends while a turn passes are not logged, or `endturn` would fill the log with them.
- One client often plays many games in a session (each replay and each `menu path=` loads one), so `start` and every load write a row of kind `game` with the save, map and turn; `grep '"kind": "game"'` splits the log by game, and the watcher prints it as a banner. Samples and the reasons are in the [Logging Inventory](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_Logging_Inventory.md#saspilot-command-log).
- Each row names its operator, the agent that sent it, as several agents may pilot one client (the user's idea, 2026-11-14).
  - `operator` comes from `--operator "Claude Code Opus 5.5"` or the `SAS_PILOT_OPERATOR` environment variable.
  - `operatorSession` is the agent's session: `SAS_PILOT_OPERATOR_SESSION`, else Claude Code's `CLAUDE_CODE_SESSION_ID` (also its session log's file name) or Codex's `CODEX_THREAD_ID`.
  - Two sessions of one agent and model are different operators, so an operator is identified by its session when there is one, and by its name otherwise.
  - Without a name, a Claude Code or Codex shell is named by the agent's kind ("Claude Code", "Codex"), as its shell gives the session but not the model; on 2026-11-14 two `py` commands sent without `SAS_PILOT_OPERATOR` were logged without an operator before this.
  - The session ID is a random identifier of a chat on this computer, not a secret; the account ID and email that Claude Code's shell also exposes are not logged.
- Operators join and leave in rows of kind `operator`.
  - An operator's first row in a log is preceded by one, numbered in order of arrival, which the watcher shows as `=== operator 2 joined: <name> ===`.
  - `SASPilotClient.py operator joined` and `SASPilotClient.py operator left` write the opening and closing rows with the same number, and report whether the row was written; an agent that simply stops leaves no closing row.
  - `SASPilotClient.py operator list` gives every operator of the client's log in order of arrival, with its session, join and leave times (`left` null while present), command count and last command, its errors with the time of the last, and how many operators there are and how many are present.
- The watcher's console view:
  - A header: its full UTC start time, its own command line, the log, the client, the filter, the recommended-settings check and the columns.
  - Colors in a console (`--no-color` for plain text): errors red, banners yellow, results sky blue, notes bold orchid, `py` code light green. Banners carry their time.
  - An `op6` column on every line names the operator, as the user asked whether each command should say who sent it.
  - Errors and notes are numbered from the watcher's start, zero-padded and with the operator: `ERROR #00003 (op6)`, `why #00012 (op6)`.
    - A first per-operator form, `why 6.3` for operator 6's third note, restarted at 1 for each operator, so the numbers did not rise down the screen, which the user read as backward.
  - Turns are padded too (`T0068-00012`), so `T0068-` greps turn 68 alone, and lines sort by turn (the user's idea).
  - `py` code shows whole, multi-line code as a block, unless `--short-code`.
  - The game banner shows the recommended-settings check that `start` runs, which until then went only to the terminal that ran `start`.
- A watcher started with `--pid` ends once that Civ4 process has closed, compared by its start time, as Windows reuses process IDs: on 2026-11-14 two watcher consoles were open, one still following a client closed half an hour before, as nothing told it, so each relaunch with `--watch` added a console.
- Test an operator change with `SAS_PILOT_LOG=0` or on a client of its own: the turn-0 game's log numbers its two real agents 4 and 6, as the previous session's tests of the feature registered `test-sec`, `explicit` and `rejoin-t` as operators 2, 3 and 5 (operator 1's row went with a `.seq` reset that a later fix stopped), and the user asked why there was an operator 6 (2026-11-14).
- The console opens with `start` and reopens on any later command if it has closed: later the same day it had ended with the agent's session while Civ4 ran on, and the user could not find it. The console writes its PID, start time and band to `<log>.watch`; `SASPilotClient.py` checks it before each command, one file read and one process check, and opens a new console in the same band if that process is gone. `SAS_PILOT_WATCH=0` turns this off, for automated tests that must not open windows.
  - `start --no-watch` was removed the same day: Codex started a scouting trial with it, and the user, watching, saw one console for two running clients and could not follow the trial. Every client now has its console, as the user asked; a `.watch` file still saying `declined` opens one on the next command.
  - The check and the launch run under a lock on `<log>.watchlock`, one caller at a time: Codex reproduced two simultaneous commands that both found no console and both opened one (round 33), then, with an exclusive claim file instead, two that both took over a stale claim (round 34). With the lock, four commands sent at once opened one console.
- `SASPilotClient.py review` lists, for the operator's session, its errors and its `py` snippets grouped by code, most repeated first; after every `py` order and every error, `SASPilotClient.py` prints a one-line reminder on stderr, so the agent sees it with the reply without the user pointing it out (the user's idea, 2026-11-14). Operator rows and banners also carry how many operators the log has had. The first review of the turn-0 game showed 10 snippets, 9 distinct: the most repeated was the resource list, by then the `resources` command, and three were Pasture checks that `builds refused=1` now answers.

### Running Python in the game

`py` is the general tool: whatever the fixed commands lack, the game's whole Python API is there.

```bash
python SASPilotClient.py py "game.getGameTurn()"
```

```bash
python SASPilotClient.py py "print player.getName(); result = [c.getName() for c in pilot._cities(player)]"
```

- One expression returns its value; otherwise set `result`. What the code prints is shown first.
- The namespace persists between calls and holds `gc`, `game`, `map`, `interface`, `player` (the active one), `describe()`, `pilot` (the command module) and everything from `CvPythonExtensions`.
- `py -` reads the code from standard input and `py @file.py` from a file, for anything longer than a line.
- `describe(obj)` calls every zero-argument `get`/`is`/`can`/`has`/`count` method of an object, which is how `info` works; use it to see what a `CyCity` or `CyPlayer` can tell.
- The [Sevopedia debug dumps](/_1_AdvCiv-SAS/Docs/Sevopedia/Debug/) and the [BUG API text](/_0_Legacy/Docs/Civ4BUG_Python_API/all_classes_web.txt) say which methods exist; with the pilot a doubt is now settled by calling the method in a running game.
- When a `py` snippet proves useful twice, make it a `cmd_<name>` function in the command file.

### Using it from a script

```python
import pilot
pid = pilot.pick_pid(None)
for unit in pilot.call(pid, "units"):
	print(unit["type"], unit["x"], unit["y"])
pilot.call(pid, "endturn")
pilot.wait_for_turn(pid, 600, after_turn=0)
```

- `call` returns the result or raises `PilotError` with the game's traceback; `request` returns the whole reply.
- `load_game(pid, path)` loads a save in a running client and returns once that game waits for orders; see [Loading a save](#loading-a-save).

### Replaying commands

[`SASPilotReplay.py`](/LLM_Helpers/saspilot/SASPilotReplay.py) runs a sequence, a list of commands against a save, and compares each reply with the run last accepted. A changed answer after a DLL rebuild or an edit of the command file then shows as a list of differences, instead of turning up in the middle of a playthrough.

```bash
python SASPilotReplay.py sequences/fogplay_t105_freetech.json
```

- They were called scenarios until 2026-11-13. Civ4 already uses "scenario" for its scenario maps and "replay" for Hall of Fame replays, so the user and Codex chose "command sequence", which says what the files hold; the runner kept its name.
- A sequence is JSON in [`sequences/`](/LLM_Helpers/saspilot/sequences/): `save` (a file in `Saves/single`, or a full path) and `steps`, each with `cmd`, `args`, and optionally `ignore` (result keys left out for that step) and `expectError`.
- The first clean run is written as the baseline, `Logs/SASPilotReplay_<sequence>.json`; later runs list each differing path, such as `steps[3].result.queue[0].turns: 5 -> 4`, and exit 1. `--accept` makes the run the new baseline once a change is meant.
- It starts its own client from the save and closes it after (`--keep` leaves it open), or loads the save in a running one with `--pid`.
- Timings and reply sizes are left out; a failed step is kept by its error line, not its traceback, whose line numbers move with every edit.
- `sleep` waits before a step, for what the game does on later frames; `from` fills arguments from this run's earlier replies, such as the diplomacy screen's number for `reply`; `afterTurn` waits for the turn after an `endturn`.
- `expect` states the value a step must give, the expression's for `py`, so a first run already verifies a fix: `fogplay_t116_queued_build.json` expects fishing boats on the crab and the boat used up.
  - `fogplay_t148_trade_table.json` guards the trade table's empty-columns finding: with Navigation on Pacal's table, "What do you want for this?" must ask 65 gold, a read token from before the counter-offer must be refused, and no gold or tech may change hands.
- A step's error that names a `from`-filled screen number, as in "what read 9 showed", is kept as `read <screen>`, as the number changes every run; only that phrase is rewritten, so an equal number elsewhere, such as `65 gold`, stays compared (Codex's review).
- A result that depends on a local setting is better left out with `ignore` than baked into the baseline: `fogplay_t105_freetech.json`'s last `todo` ignores `infoScreens`, since whether Sailing's splash shows depends on `SAS_UI_TECH_SPLASH_ON`, which ships on while the dev toggle turns it off.
- A held popup's ID is compared only as `held`, as IDs are never reused within a process; unit and city IDs, which the save fixes, are compared.
- The saves are local, so baselines stay in `Logs`, not in the repository; a sequence names the save it was written for.
  - A sequence lives only as long as its save loads. SAS does not keep saves compatible across commits, so a DLL change to what a save stores ends every sequence at once, while an XML rebalance usually loads but may change replies, which `--accept` then records.
  - Discussed with the user on 2026-11-13 and left for when the first save breaks: a sequence that starts a game with a fixed map and seed through `start --fixed-seeds`, then sets up its units and cities by command, would need no save. That needs the WorldBuilder-style commands listed under [Where to take it](#where-to-take-it).
- Why: by 2026-11-13 the command file was 1,800 lines and the Debug-opt DLL had been rebuilt about ten times in one day, each round checked by hand only.

## Popups

While the pilot drives, the DLL does not launch the game's popups into the window: it keeps each one in a held list that `popups` shows and `answer` or `closepopups` settles. The Esc menu and its confirmations still open, so a person at the window can leave the game, and so do requests to open a screen (`BUTTONPOPUP_PYTHON_SCREEN`). Fable designed this on 2026-11-13; Claude Code Opus 5.5 tested and completed it the same day.

- Why not close them in the window: a popup on display could not be closed from the DLL. `killAll`, `clearQueuedPopups` and a cancel checked in the popup's focus callback each removed only queued popups. Only one popup shows at a time, so an unanswered one also held back the rest.
- The city-name popup is a Python popup the DLL cannot hold, so `CvEventManager.py` skips it while the pilot drives; the city keeps its default name.
- Founding a city at turn 0 held `BUTTONPOPUP_CHOOSETECH` and `BUTTONPOPUP_CHOOSEPRODUCTION`, with the city ID as `data1`. Turns ended normally with popups held.
- Each held popup has an `id`, never reused in the process; `answer` takes it, and refuses an id that is gone, including one already answered.
- `answer` calls the popup's OK handler, `CvDLLButtonPopup::OnOkClicked`, which does not make every choice: production and tech are chosen through the popup's buttons as widgets, and their OK handler only opens the city or the Technology Advisor. `answer index=2 button=0` on the production popup dropped it with the queue still empty. So use `produce` and `research` for those; `answer` fits popups whose OK handler acts, such as `BUTTONPOPUP_RAZECITY` and `BUTTONPOPUP_CHANGECIVIC`.
- Two faults found in testing, both fixed in the DLL:
  - A settled popup stayed listed: after `research` chose Mining, the choose-tech popup was still held three turns later. The game drops such popups just before showing them, in `CvDLLButtonPopup::OnFocus`, which a held popup never reaches. `pruneSASPilotHeldPopups` now applies the same rules each time `popups` lists them.
  - The held list outlived the game: a save loaded in the same process still listed the previous game's popups. `CvGame::reset` now clears it on a load or a new game.
- Codex (GPT-6.1-Sol) reviewed this and found three more, all fixed:
  - `answer` first took a list position, which could name another popup once the list shifted after a prune or a reload; it takes the `id` now, and the DLL prunes and looks it up again before answering.
  - The hold also caught `BUTTONPOPUP_PYTHON_SCREEN`, a request to open a screen such as Dawn of Man rather than a choice, which first showed up as a held entry. It is launched as usual now. With the local `SAS_UI_DAWN_OF_MAN_ON` at 0, Dawn of Man did not show at all; with it at 1 it would open in the window, which was not tried.
  - Listing changed the game: for a city in disorder or on automated production, the pruning marked the city to ask again, as `OnFocus` does. Such a popup now stays held, so listing has no side effect. The election and vote checks and Python focus callbacks of `OnFocus` are not mirrored.
- Tested at turn 300 to 306 of a Huge game (2026-11-13), which also showed popups the hold never saw:
  - Granting `TECH_NATIONALISM` by `py` raised no popup at first: the revolution timer was at 4, so the game kept Nationhood as a reminder and asked again when it reached 0, at turn 304.
  - That popup then sat in the player's queue (`QUEUED`), out of reach of `answer`. AdvCiv's Minimize Pop-Ups option keeps popups queued until every unit has moved, and with 150 units that did not happen. `CvPlayer::takeSASPilotQueuedPopups` now moves the popups the pilot holds out of the queue into the held list before `popups` lists them and before `answer`; which popups are held is decided in one place, `isSASPilotPopupHoldable`.
  - `answer` on the `BUTTONPOPUP_CHANGECIVIC` with button 0 (`SAS_POPUP_CIVIC_ADOPT_CIVIC`; 1 declines, 2 opens the advisor) changed Bureaucracy to Nationhood.
  - `player.acquireCity(city, True, False)` by `py` raised `BUTTONPOPUP_RAZECITY`, with the city's new ID as `data1` and the captured gold as `data3`. Button 1 razed Lakamha; on a second city, button 0 kept Mayapan.
  - Two choose-production popups for one city, differing only in `data2` (0 and -1), were both held; `produce` for that city cleared both.
- Codex (GPT-6.1-Sol) reviewed this round too and found four more, all fixed:
  - Held popups were lost on a save: the save writes the queue and the displayed popups, not the held list, and taking from the queue made it worse. `CvPlayer::write` now writes the held popups with the queue; a fresh Civ4 loading such a save on 2026-11-13 held the same three choices again.
  - `answer` passed any button to the game's handler; for an election, a negative button would have indexed its vote options out of range. `answer` now takes only the popup types listed in `_ANSWER_MAX_BUTTON` in `SASPilotCommands.py`, each with its highest button, and refuses others with the list of those it takes.
  - A held or taken popup skipped `reportButtonPopupLaunched`, which keeps count of relaunched popups to keep their sound quiet, so a later popup could have lost its sound; both paths now report it.
  - The client: see [At scale, and the client's own cost](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot_Performance.md#at-scale-and-the-clients-own-cost).
- Codex's suggested check, saving and reloading in the same Civ4 to see the held popups come back, crashed Civ4 every time. Narrowing it down showed the crash came from leaving that Huge game, not from the pilot or the day's DLL; see [KI#1084](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1084).

- Codex's fourth review (GPT-6.1-Sol) found three more, fixed by Claude Code Fable 5.2 and tested at turn 83 of a Small game on 2026-11-13:
  - A button inside the type's range could still be one the game would not offer, such as raze when `canRaze` is false. `getSASPilotPopupButtons` in `CvDLLButtonPopup.cpp` now lists what each launch function would offer, as `0=KEEP,1=RAZE,2=LIBERATE`; `popups` shows them and `answer` takes a number or a name. `_ANSWER_MAX_BUTTON` is gone.
    - The DLL checks the button itself before taking the popup: `answerSASPilotPopup(4, 3, u'')` from `py`, past the CLI's check, returned `false` and left the raze popup held. `answer id=4 button=RAZE` then razed Beshbalik.
    - Buttons that only open a screen or the city (raze 3, civics 2) are not listed, as they make no choice.
    - Adopting a civic was first listed whenever the revolution was possible. Codex's fifth review asked for the launcher's exact rule, so it is listed only when the window would show it: AdvCiv hides it when other new civics could be adopted too. In that case decline and use `civics set=`, which adopts several at once.
    - An event's buttons are the `EventTypes` it can choose, listed by type. Before holding an event popup, the DLL makes the launcher's checks and cleanup (`isSASPilotEventPopupLaunchable`), also from the fifth review. Neither was tried on a real event.
  - Switching holding off cleared the held choices. `popups held=0` now hands them back: two held popups (`CHOOSETECH`, `CHOOSEPRODUCTION`) were listed `QUEUED` at once and the first `DISPLAYED` two seconds later, and setting research removed the displayed one.
    - They go back through the game's usual `addPopup`, which for a civics, religion or choose-tech popup first drops a queued one of the same type, as it does whenever the game asks again. A held choice handed back beside a queued one of the same type was not tried.
  - Taking a popup from the queue lowered `killAll`'s relaunch count for every popup; it now does so only for one inside the counted front run. This was not tested, as it only affects a popup's sound.
- Conquering a size-1 city by `py` raised no raze popup: the game destroys such a city on capture, and its owner was eliminated. Use a city of size 2 or more to raise one.

## Loading a save

`start --save` and `menu path=` load a save, but first `SASPilotClient.py` checks which mod the save was made with and refuses a save from another mod.

- `menu path=` waits until the loaded game waits for orders. The first runs of `SASPilotReplay.py` (2026-11-13) loaded the turn-105 save with `menu` and then `wait`, and found no free tech owed and no popups: the game being left still answered `ping` as in game with its turn active, so the wait returned before the load had begun and the first steps read the old game. `SASPilot.py` now counts finished loads on the `OnLoad` event, `ping` reports `loads`, and `load_game` waits for the count to rise; tested from turn 105 to the turn-97 save, back in 1.4 s.

- Every mod names its saves `PC BC-<year>` by default, and they all share `Saves/single`. On 2026-11-13 the largest recent save there, `PC BC-149491`, looked like an AdvCiv-SAS one but had been made with Caveman2Cosmos.
- Civ4 then stopped on its own dialog asking to restart into that mod. The pilot cannot answer it, and the game no longer replied to requests, so the client had to be closed.
- A save's header holds the mod it needs: 4 bytes, then a 4-byte length and the folder, such as `Mods\AdvCiv-SAS\` (16 bytes) or `Mods\Caveman2Cosmos\` (20). `run_autoplay.save_mod_folder` reads it for both tools, as Codex's review suggested, and reports a missing, short or cut file plainly; what the first 4 bytes hold is not known.

<img src="/_1_AdvCiv-SAS/Images/LLM/pilot/llm_pilot_save_needs_other_mod.PNG" alt="llm_pilot_save_needs_other_mod.PNG" width="250">

## What was measured

Speed, the C++ versus Python question and the client's own cost are in [SASPilot Performance](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot_Performance.md); playing as a person would and the playthroughs are in [SASPilot Playtests](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot_Playtests.md).

## What did not work, and why

- The command file in `Assets/Python/`: saving an edit while Civ4 ran made the EXE reinitialize its Python, `PythonErr.log` filled with `Can't find module CvScreensInterface`, and the game stopped answering. The user confirmed that the mod has no working Python reload, unlike Realism Invictus; the notes on RI's approach are in `C:\Users\PC\Downloads\AdvCiv-SAS_LLM\ri_python_reload`.
  - Moving the file to `Assets/SASPilot/` broke the same way, so the EXE watches all of `Assets`.
  - In `LLM_Helpers/game_runs/`, outside `Assets`, edits reload cleanly. The loader compiles the file's text itself: `imp.load_source` worked too but left a `.pyc` beside the source.
- Plain integers for enum arguments: Boost.Python raised `ArgumentError` for `plot.getYield(0)` and `unit.canDoCommand(3, ...)`. Convert with the enum class, `YieldTypes(i)` or `CommandTypes(i)`; methods declared with `int`, such as `canStartMission`, take numbers.
- Enum values in replies: a Boost enum is an `int` whose `str()` is its name, so `info` first wrote `"getCommandType":COMMAND_UPGRADE`, which is not JSON. Enums now go out as quoted names.
  - The client first treated a reply it could not parse as still being written and retried until its timeout, which looked like a hung game. Replies are renamed into place whole, so it now fails at once and keeps the file.
- `CyInterface().exitingToMainMenu(path)`: its help string shows one argument, but the EXE's binding takes `(path, bool)`. With `False` it loaded the save in the same process, and the pilot answered again once the game was up. What the bool changes was not tested.
- A ping straight after `endturn` still showed the old turn as active, because the turn ends after the reply is written. The client's `endturn` therefore waits for a later game turn.
- The main menu: no `gameUpdate` fires there, and with `USE_ON_UPDATE_CALLBACK` at 1 no `Update` either, so Python cannot serve the mailbox outside a game.
  - Screen updates do not fire there either: after `menu` from a client started with a save, a ping got no reply in 10 s (2026-11-13).
  - `menu` without a path, in a client started with a new game, did not stay at the menu: the per-run INI still said `QuickStart = 1`, so a new game started at once, which makes it a way to restart.
  - In a client started from a save it stays at the main menu, silent. From there use the UI tools of the [Game Runs Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_Game_Runs.md#the-main-menu-and-the-sevopedia), or `close` and `start` again, which takes about a minute.

## Limits

- Popups are held rather than shown (see [Popups](#popups)); `answer` was tried on the production, civics and raze popups, not on war declarations, random events or other Python popups.
- Diplomacy goes through the screen (`contact`, `diplo`, `reply`) and `propose`; the trade table behind "Care to negotiate?" cannot be filled by the pilot.
- `messages` holds only what the game still lists; the full history of the other players' turns is in SASGameRecord (see the [Logging Inventory](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_Logging_Inventory.md)).
- Fog covers the map reads only; see [Playing as a person would](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot_Playtests.md#playing-as-a-person-would).
- A save made while popups were held writes them into the player's popup queue. Loading it with the pilot on held them again; loading it with the pilot off, where they should show in the window, was not tried.
- A request made during a long AI turn or a load waits until the game updates again; raise `--timeout` rather than repeat it.
- `info` and `describe` skip getters that need arguments, such as yields per type; read those with `py`.

## Where to take it

The handoff for the next agent, with the state of the latest games and what is left, is in [SASPilot Playtests](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot_Playtests.md#where-to-take-it).

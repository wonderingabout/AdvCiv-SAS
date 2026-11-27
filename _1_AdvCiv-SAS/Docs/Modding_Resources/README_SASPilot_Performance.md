# AdvCiv-SAS SASPilot Performance

How fast SASPilot answers, why, and what moving parts of it to C++ gained: the measurements behind the [SASPilot Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot.md)'s design. Split from the guide on 2026-11-15, as the guide is technical and these records are analytical (the user's call).

## Menu

[What was measured](#what-was-measured)\
&emsp;[Speed](#speed)\
&emsp;&emsp;[How it was found](#how-it-was-found)\
&emsp;[Would the DLL be faster?](#would-the-dll-be-faster)\
&emsp;&emsp;[Which other commands to move](#which-other-commands-to-move)\
&emsp;&emsp;[The same question for the Timeline tab, January 2026](#the-same-question-for-the-timeline-tab-january-2026)\
&emsp;[At scale, and the client's own cost](#at-scale-and-the-clients-own-cost)\
&emsp;[How it was measured](#how-it-was-measured)

## What was measured

All on 2026-11-13, Small Pangaea, turn 0 to 22, Debug-opt DLL, one client.

- A request took about 250 ms (20 pings averaged 246 ms): the game served the mailbox on game updates, about four a second while it waits for the player.
- Size hardly mattered: 441 plots in full came back in 273 ms.
- With `USE_ON_UPDATE_CALLBACK` set to 1 in `PythonCallbackDefines.xml`, the per-frame `Update` event fired 239 times against 2 game updates by the first ping, so serving on it would cut the wait to about a frame.

### Speed

Measured by Claude Code Opus 5.5 later on 2026-11-13 with `SASPilotClient.py bench`, same map and seeds (`--fixed-seeds`), plots at radius 10 (441 plots, 113 KB of JSON).

`roundTripMs` runs from writing the request to reading the reply, so it also holds the client's polling and the file handling; `gameMs` runs from the game reading the request through encoding the reply, and ends before the reply file is written.

| Setup | Ping round trip | Ping in game | 441 plots round trip | 441 plots in game |
| --- | --- | --- | --- | --- |
| Served on game updates (first version) | 251 ms | 0.27 ms | 251 ms | 30 ms |
| Per-frame `Update` callback on, client checks every 20 ms | 21 ms | 0.27 ms | 43 ms | 31 ms |
| Same, client checks every 1 ms | 1.9 ms | 0.24 ms | 35 ms | 31 ms |
| Same, ASCII fast path in the JSON writer | 1.9 ms | 0.24 ms | 11 ms | 7.4 ms |
| Served on screen updates, callback back at 0 (current) | 2.0 ms | 0.16 ms | 12 ms | 8.7 ms |

- Medians of 30 pings or 10 plot reads. Nearly all of the first 250 ms was waiting for the game to look, not serving.
- Of the 30 ms for 441 plots, reading the game took 3 ms and writing the JSON 28 ms: the writer escaped every character in Python. Plain ASCII strings, nearly all XML types and names, are now copied whole, which cut it to about 4 ms with byte-identical output.
- The client checked for the reply every 20 ms, which became most of a 21 ms ping once the game answered every frame; it now checks every 1 ms.
- `CvScreensInterface.update`, which the EXE calls for the open Python screens, fired about 650 times a second in game, once a frame, with `USE_ON_UPDATE_CALLBACK` at 0. SASPilot now serves from it, so players keep the callback off; for them it costs one Python check a frame on top of a call the EXE already makes.
- One mailbox listing took 19 microseconds, so checking every frame costs about 1% of one core while piloted.
- Turning `USE_ON_UPDATE_CALLBACK` on from Python with `gc.setDefineINT` did nothing: the EXE reads it at launch only.
- So ask for much in one request, with `plots`, `batch` or `py`, when the data is large; small requests are now cheap too.

#### How it was found

Each step came from what the previous measurement showed, not from a plan made up front.

1. The question was whether the DLL would be faster. Rather than argue it, `--timing` and `bench` were added to time each request on both sides: the client's round trip and the game's own work (`gameMs`).
2. The first numbers settled where the time went: a ping spent 0.27 ms in the game out of 251 ms. Neither Python nor C++ could fix that; only being served more often could.
3. Switching on `USE_ON_UPDATE_CALLBACK` cut a ping to 21 ms, which matched the client's own 20 ms sleep between checks; at 1 ms it fell to 1.9 ms.
4. The plot read stayed at 31 ms in the game. Timing its two halves (now the `profile` command) showed 3 ms reading and 28 ms writing JSON, which led to the ASCII fast path.
5. The callback is a setting for every player, and `gc.setDefineINT` could not switch it on for SASPilot alone, so the open screens' `update` call was tried instead: it fires every frame with no setting.

### Would the DLL be faster?

A C++ prototype (Claude Code Opus 5.5, 2026-11-13) answered this with numbers. It had two parts, switched on by a `native` SASPilot command:

- `getSASPilotPlotsJson` wrote the same plots as the Python `plots` command, in C++. Its output was byte-identical to Python's for the 441 plots.
- A mailbox served entirely in C++ (`nreq_<id>.txt` requests, `bench --native`), from the five update functions the EXE calls on the DLL, each counted.

| Path | Ping round trip | 441 plots round trip | 441 plots in game |
| --- | --- | --- | --- |
| Python, served every frame | 1.9 ms | 11.6 ms | 8.4 ms |
| C++ mailbox in the DLL | 200 ms (median) | 200 ms (median) | 0.46 ms |
| C++ plots called from Python's every-frame check (current) | 1.9 ms | 3.2 ms | 0.51 ms |

- C++ was about 25 times faster at the work itself: 0.32 ms against 8.1 ms (3.3 ms reading, 4.9 ms writing), timed around the call alone. In SASPilot's own `gameMs`, which also counts reading the request and its JSON, it was 0.51 ms.
- The last row was first estimated at about 2.5 ms; measured after the change, it was 3.2 ms (median of 10).
- But in 10 seconds of that run, at turn 0 waiting for orders, only `CvGame::update` and `updateTestEndTurn` ran, 40 times each; `updateColoredPlots`, `updateBlockadedPlots` and `updateSelectionList` did not run at all with nothing selected. The DLL has no call every frame, so a bridge in the DLL alone waits for those, about 200 ms.
- So the fastest shape is Python's every-frame check calling C++ for large reads. At 441 plots the gain is about 8 ms per request; it grows with size, by about 18 microseconds per plot in Python against 0.7 in C++, so a full Huge map read would be where it pays.
- Codex (GPT-6.1-Sol) reviewed the prototype and suggested keeping it on a side branch, as it would mean two writers to keep identical. The user preferred the long-term speed ("a house of iron rather than of wood"), so the plot reads moved to C++ for good, with the Python writer removed so there is one writer only:
  - `plot` and `plots` now return the C++ JSON as it is, through `RawJson` in `SASPilotCommands.py`; a new plot field goes in `appendSASPilotPlotJson` in [CvGameInterface.cpp](/CvGameCoreDLL/CvGameInterface.cpp) and needs a DLL build.
  - The C++ mailbox, its hook counters and the `native` command were dropped, since the mailbox was the slow part. They are kept as a diff in `Downloads/AdvCiv-SAS_diff_backups/saspilot_native_mailbox_prototype_*`, outside the repository.
  - Codex's review also found that a SASPilot error in the screen update would skip the screen's own update, that the C++ radius needed bounds, and that the JSON key cache mixed up equal keys such as `1` and `True`; all three were fixed. It confirmed the ASCII fast path against all 256 byte values under Python 2.4.

#### Which other commands to move

Later the same day, the user asked why every command was not moved to C++, as the plots had been. The answer is measured per command, not assumed, as the plots' was. `SASPilotClient.py --count 10 bench <command>` on a Small map at turn 176 with fog on (medians):

| Command | Round trip | Game time (`gameMs`) | Above a bare request |
| --- | --- | --- | --- |
| `ping` | 5.4 ms | 0.23 ms | |
| `todo` | 5.4 ms | 0.19 ms | 0 |
| `units player=all` | 5.4 ms | 0.26 ms | 0.03 ms |
| `cities` | 5.4 ms | 0.26 ms | 0.03 ms |
| `techs` | 7.0 ms | 0.77 ms | 0.54 ms |
| `trade with=2` | 9.0 ms | 3.49 ms | 3.3 ms |

- `trade` checks every tradeable item in both directions, so its loop moved to C++ (`getSASPilotTradeItemsJson` in [CvGameInterface.cpp](/CvGameCoreDLL/CvGameInterface.cpp)), and `techs` reads that table instead of checking each tech itself. One writer, as for the plots.
  - Measured after, same save: `trade` 3.49 → 2.15 ms of game time, less than the plots' 25 times, as most of what remains is the game's own `getTradeDenial` AI work, which C++ calls just the same.
    - [`checks/trade_items_parity.py`](/SASPilot/checks/trade_items_parity.py) found the same entries as the Python loop for all 20 pairs of players; only the order changed, to the game's enum order, which the turn-115 baseline accepted after a sorted comparison.
  - `techs` first got slower, 0.77 → 3.3 ms, as it read the whole table eight times for its tech rows, which Codex predicted from the code; a kind filter on the C++ table brought it to 0.57 ms. A port is checked by timing it afterwards, not only before.
- The others add nothing measurable to a bare request, whose time is the wait for the game's next frame, so they stay in Python, which reloads while Civ4 runs and reports its errors instead of crashing the game. AGENTS.md's rule applies: prefer the faster version for a measured gain, the simpler one when there is none.
- Some cannot move: the diplomacy screen's text and replies exist only in `CvDiplomacy.py`, which the EXE calls; `look` uses the EXE's camera, not the DLL's; `SASPilotClient.py price` waits across frames for a screen, which no single game-side call can.
- `units` and `cities` grow with the map, so a Huge late game is worth timing again before deciding they stay.

#### The same question for the Timeline tab, January 2026

The Info Screen's Timeline tab, then called the History tab, went through the same Python-or-DLL question ten months earlier, without measurements.

- On 2026-01-24, in a Codex (GPT-5.2-Codex) session, the user asked whether the DLL could build the tab's replay messages faster, as mid-to-late games showed a delay. Codex moved the filtering and formatting into C++ (`CvGame::getReplayMessagesFiltered`), then added a C++ cache.
- By eye, the C++ cache felt slower than the version before it and the C++ filtering only slightly faster, "hard to tell". These were the user's visual impressions in game, with no timing taken: the slowdown seemed clear enough to notice, but was not confirmed and could be mistaken.
  - The user's reasons, as recalled on 2026-11-13: Python keeps the tab easy for modmods to carry over and change, and the C++ version seemed slower, not faster.
    - A clearly faster C++ version could have been judged differently. The user kept the pure Python version for simplicity and saved the C++ one on the side branch `history-tab-dll-implementation`, commit `a256d0638` ("loading times are not fast enough to justify not going full python rather for simplicity").
- That branch was deleted from GitHub on 2026-10-13 with other old branches. On 2026-11-13 GitHub's activity log gave its last commit, `git fetch origin <sha>` brought it back, and it was restored as a local branch.
- In May 2026 the tab's real cost turned out to be elsewhere: caching the data and even the prepared rows "did not significantly help", while keeping the table widget the EXE had built made reopening almost instant (practical commit 5859; the comment is in [CvMilitaryAdvisor.py](/Assets/Python/Screens/CvMilitaryAdvisor.py) for the Battles tab, which shared the fix).
- SASPilot's test showed C++ faster only at the part it replaces, with most of the time elsewhere, in waiting for the game to look. The Timeline may have been the same, with its time in the EXE building table rows, but that is a reading of two separate findings: the January impressions and the May table fix. Neither measured what the January C++ changed.
- The difference is that SASPilot's time was measured, part by part, before choosing; the Timeline's was judged by eye, which could suggest that C++ did not help much but not show why.

### At scale, and the client's own cost

A Huge Pangaea autoplayed to turn 300 (876 units, 82 cities, 6,016 plots) showed where the time goes once the game is large, measured by Claude Code Opus 5.5 on 2026-11-13.

- Every read command but two stayed near 1 ms in the game: one player's 150 units 1.3 ms, all cities 1.4 ms, all players 1.1 ms. These were left in Python.
- All 876 units, as one `batch` of `units` per player, took 8 ms: 2 ms reading the game and 6 ms writing JSON. So `units` moved to C++ like the plots, and `units player=all` gives every living player's units in one request.
  - In C++ (`getSASPilotUnitsJson`, sharing the unit writer of the plots), all 876 units took 0.58 ms in the game and 4.5 ms round trip (median of 10), and the output was identical to Python's, in the same order.
- The whole map's plots took 6.8 ms in the game but 21.6 ms round trip. The game wrote the 1.6 MB reply in 0.5 ms; the rest was the client: `json.loads` took 9 ms, and printing it indented with `json.dumps` took 58 ms.
  - With `orjson` (installed 2026-11-13, `python -m pip install orjson`) the same parse took 7 ms and the indented print 2.2 ms, with identical data. Importing `orjson` costs about 27 ms, so `SASPilotClient.py` uses it only for replies of at least `ORJSON_MIN_BYTES` (200 KB); it indents by 2 rather than 1. Without `orjson`, such replies use the `json` module, as Codex's review asked.
  - Codex also found that skipping the process check with one mailbox made a crashed Civ4 wait out the whole timeout; the client now checks once a reply is a second late, which costs nothing when it is quick.
- Each `SASPilotClient.py` command is a new Python, and that start cost more than the request: a whole `SASPilotClient.py ping` took 56 ms for a 2 ms request.
  - Python itself starts in 15 ms; importing `SASPilotClient.py` took 38 ms, 18 ms of it `desktop_windows` and `run_autoplay`, which only `start`, `close` and a few checks need. They are now imported where they are used, and with one mailbox the client no longer checks its process before sending.

| Whole `SASPilotClient.py` command | Before | After |
| --- | --- | --- |
| `ping` | 56 ms | 43 ms |
| whole Huge map's plots, indented | 139 ms | 74 ms |
| whole Huge map's plots, `--compact` | 83 ms | 72 ms |

- What remains of a ping is mostly Python's start (15 ms) and `argparse` (11 ms). A script that imports `saspilot` and calls `saspilot.call` pays them once, so for many requests in a row it is the faster way.

### How it was measured

The timers are Windows' high-resolution performance counter in all three places, not a Civ4 clock:

- The client, `SASPilotClient.py`, uses Python 3's `time.perf_counter()` for `roundTripMs`, from writing the request to reading the reply.
- The game's Python uses `time.clock()`, which in Python 2.4 on Windows reads the same counter, for `gameMs` and the `profile` command. The values came out in fractions of a millisecond and agreed with the round trips, unlike `time.time()`, whose coarse steps the loader's comments warn about.
- The C++ prototype called `QueryPerformanceCounter` directly.

To repeat or extend a measurement:

1. `SASPilotClient.py start --map Pangaea --world-size WORLDSIZE_SMALL --fixed-seeds`, so every run has the same map and units.
2. `SASPilotClient.py bench ping --count 30` and `SASPilotClient.py bench plots x=27 y=19 radius=10 --count 10` give medians for the round trip and the game's share, and `servedOn` tells which event served them.
3. If the game's share is large, `SASPilotClient.py profile cmd=<command> 'args={...}'` splits it into reading the game and writing JSON.
4. To compare a C++ version of a command, call it from `py` with `time.clock()` around it, as the plot writer was compared; the C++ mailbox comparison needs the backed-up prototype diff.
5. To see how often an event fires, compare the `ticks` in two `ping` replies taken a known time apart.

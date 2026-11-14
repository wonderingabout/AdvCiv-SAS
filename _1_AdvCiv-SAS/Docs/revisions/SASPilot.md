# SASPilot command revisions

`PILOT_REVISION` lives in `LLM_Helpers/game_runs/SASPilotCommands.py`, alongside the interface it identifies. Civ4 loads that Python file, and the mailbox greeting and `ping` report its number. The XML switch `SAS_PILOT_ON` enables the Pilot.

Record one entry per integrated command revision. Keep one number for the candidate while it is under review, including drafts that will be squashed. Bump it for changes to command names, arguments, replies or observable behavior.

## Initial SASPilot interface

The initial interface covers fog-aware state queries and orders, popup and diplomacy handling, and replayable command sequences. It also provides structured plot grids and rules graphs for agent-side analysis, and session-aware mailbox replies that distinguish a withdrawn request from one with an unknown outcome after a timeout.

Development snapshots reported their loaded revision so they could be identified during playtesting. The history groups that work into this single baseline.

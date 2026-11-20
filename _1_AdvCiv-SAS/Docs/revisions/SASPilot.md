# SASPilot Revision History

## Menu

- [Revision policy](#revision-policy)
- [Where the number lives](#where-the-number-lives)
- [History (latest first)](#history-latest-first)
  - [Revision 1 - SAS practical 6750](#revision-1---sas-practical-6750)

## Revision policy

`PILOT_REVISION` tells an agent which command interface the running game answers with, so a client or a saved command sequence can tell whether a command it relies on may have changed. Like [SASGameRecord's revision](/_1_AdvCiv-SAS/Docs/revisions/SASGameRecord.md#revision-policy), it is an update signal, not a compatibility promise.

- Increment it once per commit that changes a command's name, arguments, reply or observable behavior, in `SASPilotCommands.py`, the in-game loader [`SASPilot.py`](/Assets/Python/SASPilot.py) or the C++ bindings the commands call.
  - Desktop-only changes to the client, console or helpers in [`LLM_Helpers/saspilot/`](/LLM_Helpers/README.md#saspilot) do not change what the game answers, so they need no bump.
  - Do not debate whether a change is compatible; when in doubt, increment.
- A squash-bound PR keeps one number for the whole candidate, relative to its base, however many local commits it has.
- Add one short latest-first entry below in the same commit, with `pending` as its commit until the next commit fills it in.

## Where the number lives

- `PILOT_REVISION` sits in [`SASPilotCommands.py`](/LLM_Helpers/saspilot/SASPilotCommands.py), beside the interface it identifies; it is the one file Civ4 hot-reloads, so the number changes with the commands without restarting the game.
- The mailbox greeting (`hello.json`) and `ping` report the number the running game loaded.
- The XML define `SAS_PILOT_ON` only switches the pilot on; it carries no revision.

## History (latest first)

### Revision 1 - SAS practical 6750

- **Date:** 2026-11-15
- **Git commit:** `5e8ce0d1b3ff6f1c6bb6f8eb9f1da9a7e86a9d21`
- **Change:** The first revision, covering the pilot from its first commit on `main` through the `saspilot` draft PR, which are meant to be squashed into one commit; the entry stays broad until that work settles.
  - The interface covers fog-aware state queries and orders, popup and diplomacy handling, replayable command sequences, plot grids and rules graphs for agent-side analysis, session-aware mailbox replies, and screens' widgets opened, read and clicked by name (SASPilotUI, with the `executeSASPilotWidget` binding).
    - See the [SASPilot Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot.md) for the commands.

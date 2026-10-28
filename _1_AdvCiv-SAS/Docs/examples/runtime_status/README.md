# Runtime history example

This folder retains a complete history from an earlier real Civ4 run. Complete current-status and exit JSON examples are inline in the [Logging Inventory](/_1_AdvCiv-SAS/Docs/README_Logging_Inventory.md#runtime-status-and-history).

## Menu

- [Capture](#capture)
- [Reading the history](#reading-the-history)
- [Test fixtures](#test-fixtures)

## Capture

[SASRuntimeHistory_example.jsonl](/_1_AdvCiv-SAS/Docs/examples/runtime_status/SASRuntimeHistory_example.jsonl) was captured on 2026-10-19 with runtime revision 5 and a Debug-opt DLL. It retains real timestamps, process/DLL identity and measured intervals; it is not synthetic harness output.

The process created two games, loaded a save, opened/closed Sevopedia in several contexts, ran scheduled and interrupted autoplay, entered/exited WorldBuilder, returned to the menu twice and exited through the in-game UI. These are functional observations, not a controlled performance comparison.

This earlier capture predates the source-provenance, native-popup, external-exit and revision-13 player-turn timing fields shown/described in newer documentation; it is a separate run, not their matching history.

## Reading the history

- Each physical JSONL line is a complete JSON object. Read records individually rather than treating the file as one JSON array.
- The `run` record gives constant process/DLL identity; `session` records preserve the first ready-game context; `transition` records give timed lifecycle/presentation observations. Runtime revision 13 can additionally append one `player_turn_summary` per completed sequential game turn, containing every measured player's activation/main/ending duration without one history row per player boundary.
- `stateSerial` orders transition observations, including presentation-only events; it does not count completed activity intervals. Gaps and publication-failure counters matter when interpreting completeness.
- UTC timestamps locate observations in external evidence. Production interval durations use the monotonic diagnostic clock, independently of wall-clock corrections.
- A close request or entry into orderly destruction does not prove the process finished exiting. Runtime revision 10 adds independent process-handle exit evidence; see the [Main Changes Guide](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md#runtime-status-and-history) and [revision history](/_1_AdvCiv-SAS/Docs/revisions/SASRuntime.md) for current behavior and field interpretation.

## Test fixtures

The native harness can export synthetic status/history fixtures to a scratch directory:

```powershell
python tests/diagnostics/run_writer_tests.py --export-runtime-examples "$env:TEMP\sas-runtime-fixture-examples"
```

This compiles only the temporary harness, without building/installing the game DLL or reading private user logs. Ordinary test runs do not refresh the real example; exported synthetic files remain separate from it.

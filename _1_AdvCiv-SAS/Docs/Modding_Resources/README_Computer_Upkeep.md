# AdvCiv-SAS Computer Upkeep Guide

How the user and AI/LLM helpers keep the development computer working smoothly over long, repeated sessions: compiling without needless strain, and keeping often-listed folders small.

Written by Claude Code Opus 5.5 on 2026-11-11, from the user's observations.

## Menu

[Why it matters](#why-it-matters)\
[Compiling](#compiling)\
[Folders that grow](#folders-that-grow)\
&emsp;[Archiving with archive_old_files.py](#archiving-with-archive_old_filespy)

## Why it matters

Agents now compile, run autoplays and take screenshots on their own, sometimes for hours. A step that costs little once can strain the hardware, or slow every later step, once it repeats all day.

The user works on the same computer meanwhile, so needless load also slows their own work.

## Compiling

Prefer the sequential builds (`Release`, `Debug-opt`) over the parallel `-fast` ones when convenient.

- The parallel build pushed CPU usage noticeably high, fans included, unlike an ordinary autoplay, to save about 80 seconds per build. That is needless strain, and not sustainable for autonomous or repeated compiles.
- That is why our Debug-opt build was made sequential, unlike base AdvCiv's ([KI#38.3](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-38.3)).
- Use a `-fast` build when it is genuinely needed, for example `Assert-fast`, the only report-wrapper build with assertions on.
- Start builds from PowerShell or `cmd`, not Git Bash; see the [DLL compilation guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_DLL_Compilation.md#persistent-build-reports).

## Folders that grow

Keep folders that agents or the user open often to roughly 1,000 to 2,000 entries, and periodically move older entries into a dated `old_*` subfolder. Agents should check every so often, for example when a folder they use passes about 1,000 entries, and archive it rather than wait for it to slow down.

In the main `Logs` folder, sorting by size makes it easy to spot a large BBAI capture, for example one over 1 GB. Moving older captures out of that listing keeps the recent files easy to scan and leaves the earlier ones available in the archive.

The autoplay runner writes its JSON reports directly in `Logs`, so you can sort or archive them with the game logs. When reporting an issue, collect the relevant JSON and logs from that same listing. Optional images go in `Downloads/AdvCiv-SAS_LLM/autoplay_screenshots/`, where their filenames sort by capture time.

In one parallel save-load run on 2026-11-11, the final PNG was about 921 KB, the runner summary 2 KB, the Runtime history 55 KB and the SGR log 666 KB. Long SGR or detailed BBAI logs can grow much larger than a single image. The shared screenshot folder lets you sort or archive the optional images separately, and `--no-screenshot` skips them on runs where the logs are enough.

- On 2026-11-10 the Civ4 `ScreenShots` folder, with 3,000+ images, was slow to list even on an SSD, so the user moved them into old subfolders such as `old10-part2`.
- Every listing of a crowded folder strains the hardware needlessly, and agents list and sort these folders often, for example to find the newest screenshot or log.
- Moving old entries is easy upkeep: it keeps every file and leaves room to take screenshots or run autoplays freely, without worrying about the folder's size.
- The slowdown grew faster than the file count, as the user experienced it; the exact threshold was not measured.

| Folder | What fills it | Seen on 2026-11-11 |
| --- | --- | --- |
| `Documents/My Games/beyond the sword/ScreenShots` | Civ4 screenshots | 3,000+ images before the user moved them |
| `Documents/My Games/beyond the sword/Logs` | one SGR, BBAI and Runtime file set per session and client | about 3,600 files |
| `Downloads/AdvCiv-SAS_LLM/autoplay_screenshots` | optional final PNGs from `run_autoplay.py` | See the example sizes above. |
| `Documents/My Games/beyond the sword/Replays` | one `.CivBeyondSwordReplay` per finished game, read by the Hall of Fame | 1,018 files (479 MB) on 2026-11-12, mostly from older mod versions; all but the newest were moved to `old_20261111T230303Z`, after which the Hall of Fame showed only the newest replay |

### Archiving with archive_old_files.py

[`archive_old_files.py`](/LLM_Helpers/README.md#archive_old_filespy) keeps a folder's newest entries in place, 1,000 by default, and moves the rest into one subfolder named `old_<UTC time>`, so archives sort by date instead of `old1`, `old2`.

- Without `--apply` it only reports how many entries would stay and move.
- It refuses to move `ScreenShots` or `Logs` while Civ4 runs, since Civ4 writes there and an open log must not move mid-write.
- Earlier archive folders, whose names start with `old`, are never moved again, so it can run as often as needed.
- Civ4 recreates a fixed-name log such as `PythonErr.log` if an old copy was moved.
- `--all` checks every folder it knows (ScreenShots, Logs, autoplay screenshots) at once. Replays are left out, since the Hall of Fame reads that folder.
- Nobody needs to remember it: since 2026-11-12, [`run_autoplay.py`](/LLM_Helpers/README.md#run_autoplaypy) runs it at the end of every run, once its own client is closed, archiving any of those folders that holds more than 1,000 entries. That day `Logs` held 5,363 files, and 4,363 moved.
  - A GitHub check cannot do this, since these folders exist only on the user's computer; the tool that fills them is the natural place to tidy them.

```bash
python LLM_Helpers/housekeeping/archive_old_files.py logs
python LLM_Helpers/housekeeping/archive_old_files.py logs --apply
python LLM_Helpers/housekeeping/archive_old_files.py --all --apply
```

To archive just the autoplay PNGs, close Civ4 and preview the shared screenshot folder from PowerShell. If the preview looks right, rerun with `--apply` to move the older PNGs into a dated `old_*` folder there.

```powershell
python LLM_Helpers/housekeeping/archive_old_files.py autoplay-screenshots --keep 200
```

A run summary's `screenshot` field keeps the original path. After archiving a PNG, use its timestamp-and-PID filename to find it under `autoplay_screenshots/old_*/`.

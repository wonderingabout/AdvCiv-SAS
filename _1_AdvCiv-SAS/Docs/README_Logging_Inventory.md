# Civ4 / AdvCiv-SAS logging inventory

**Authors (2026-10-19):** GPT-6.1-Sol (Codex); historical provenance research and rebase by ChatGPT-5.6-Sol. Minor review from Claude Sonnet 5.5: 2026-10-20.

Use this inventory to locate diagnostic output, identify its writer or enabling conditions, distinguish current SAS evidence from older or other-mod files, and compare meaningful inherited/base behavior with current SAS behavior.

**Editorial scope:** this is a canonical reference/inventory, not an iterative changelog.

- Keep Before/After comparisons when they show a meaningful inherited/base/legacy -> current SAS difference or make a SAS enhancement easier to understand.
- Treat the **After/current SAS** side as canonical; replace superseded intermediate SAS stages instead of stacking them as implementation chronology.
- Keep step-by-step development history in Git, KIs or subsystem revision histories.
- Retain historical details here when they explain provenance, ownership or compatibility, or help identify an older file/output someone may encounter.

Dated snapshots below identify when local presence, counts, settings and file dates were inspected; they are not live status or a claim that every installation produces these files.

The EXE is closed source, mods can supply arbitrary filenames, and some outputs require particular situations or compile options. Consequently, an exhaustive universal filename list is unavailable. The tables distinguish observed files from source-supported possibilities.

## Menu

- [Overview](#overview)
- [Historical lineage and ownership](#historical-lineage-and-ownership)
  - [Modernization principles](#modernization-principles)
- [Files present in the user Logs folder](#files-present-in-the-user-logs-folder)
  - [Other diagnostic files present](#other-diagnostic-files-present)
- [Conditional outputs not found in the current Logs folder](#conditional-outputs-not-found-in-the-current-logs-folder)
- [Outputs outside the user Logs folder](#outputs-outside-the-user-logs-folder)
- [Historical engine outputs not present in this snapshot](#historical-engine-outputs-not-present-in-this-snapshot)
- [Inspected switches and timestamp evidence](#inspected-switches-and-timestamp-evidence)
- [SAS assertion diagnostics](#sas-assertion-diagnostics)
  - [Session files and metadata](#session-files-and-metadata)
  - [Captured assertion examples](#captured-assertion-examples)
    - [Startup example](#startup-example)
    - [Gameplay example](#gameplay-example)
  - [Historical comparison](#historical-comparison)
- [SAS AI and game-record diagnostics](#sas-ai-and-game-record-diagnostics)
  - [Session headers and provenance](#session-headers-and-provenance)
  - [SASGameRecord (SGR)](#sasgamerecord-sgr)
    - [SASGameRecord session header example](#sasgamerecord-session-header-example)
    - [SASGameRecord gameplay example](#sasgamerecord-gameplay-example)
    - [`SASGameRecord_*.log` (runtime and version context)](#sasgamerecord_log-runtime-and-version-context)
  - [BBAI](#bbai)
    - [BBAI session header example](#bbai-session-header-example)
    - [Categories and inherited Settler logging](#categories-and-inherited-settler-logging)
    - [Settler Before/After: selecting a movement target](#settler-beforeafter-selecting-a-movement-target)
    - [UWAI diagnostics: standalone AdvCiv reports vs current BBAI records](#uwai-diagnostics-standalone-advciv-reports-vs-current-bbai-records)
      - [UWAI Before/After: separate prose report to shared BBAI records](#uwai-beforeafter-separate-prose-report-to-shared-bbai-records)
- [Runtime observations and DLL build reports](#runtime-observations-and-dll-build-reports)
  - [Runtime status and history](#runtime-status-and-history)
    - [`SASRuntimeStatus.json` (current status)](#sasruntimestatusjson-current-status)
    - [`SASRuntimeExit_*.json` (exit observation)](#sasruntimeexit_json-exit-observation)
      - [Notable examples: failure dialogs while Civ4 is alive](#notable-examples-failure-dialogs-while-civ4-is-alive)
        - [Crash-dump prompt](#crash-dump-prompt)
        - [C++ Runtime Library error](#c-runtime-library-error)
    - [`SASRuntimeHistory_*.jsonl` (session and exit history)](#sasruntimehistory_jsonl-session-and-exit-history)
    - [Live source-edit observation](#live-source-edit-observation)
      - [`SASRuntimeSourceWatch_*.json` (watcher state and host)](#sasruntimesourcewatch_json-watcher-state-and-host)
      - [`SASRuntimeSourceChanges_*.jsonl` (live file changes)](#sasruntimesourcechanges_jsonl-live-file-changes)
  - [DLL build reports](#dll-build-reports)
    - [`CvGameCoreDLL.dll.build.json` (toolchain and build launcher)](#cvgamecoredlldllbuildjson-toolchain-and-build-launcher)
    - [`AdvCiv.log` (compiler output and build summaries)](#advcivlog-compiler-output-and-build-summaries)
    - [`_SNAPSHOT_CONTEXT/archive_contents_and_context.txt` (packaging host)](#_snapshot_contextarchive_contents_and_contexttxt-packaging-host)
- [Python diagnostic messages](#python-diagnostic-messages)
- [Startup rows and run boundaries](#startup-rows-and-run-boundaries)
- [Structured Python diagnostic records](#structured-python-diagnostic-records)
- [Screen LOG button exports](#screen-log-button-exports)
  - [Military Advisor: Battles](#military-advisor-battles)
  - [World Advisor: Changes](#world-advisor-changes)
  - [Info Screen: Timeline](#info-screen-timeline)
  - [Sevopedia chart exports](#sevopedia-chart-exports)
    - [Era chart](#era-chart)
    - [Handicap chart](#handicap-chart)
    - [Game Speed chart](#game-speed-chart)
    - [World Size chart](#world-size-chart)
- [Before and after: shared Python log timestamps](#before-and-after-shared-python-log-timestamps)
  - [`PythonDbg.log`](#pythondbglog)
    - [Before: PythonDbg.log](#before-pythondbglog)
    - [After: PythonDbg.log](#after-pythondbglog)
  - [`PythonErr.log`](#pythonerrlog)
    - [Before: PythonErr.log](#before-pythonerrlog)
    - [After: PythonErr.log](#after-pythonerrlog)
  - [`PythonErr2.log`](#pythonerr2log)
    - [Before: PythonErr2.log](#before-pythonerr2log)
    - [After: PythonErr2.log](#after-pythonerr2log)
  - [Engine-log captured formats and SAS comparisons](#engine-log-captured-formats-and-sas-comparisons)
    - [`app.log`](#applog)
    - [`audio.log`](#audiolog)
    - [`init.log`](#initlog)
    - [`initmgr.log`](#initmgrlog)
    - [`resmgr.log`](#resmgrlog)
    - [Before: xml.log](#before-xmllog)
    - [After: xml.log](#after-xmllog)
    - [`LSystem.log`](#lsystemlog)
- [Source references](#source-references)
  - [Current/local source](#currentlocal-source)
  - [Historical / external provenance](#historical--external-provenance)

## Overview

Screenshots of game-generated diagnostic output, including SASGameRecord text/maps and runtime failure dialogs, are grouped in [`Images/diagnostics/`](/_1_AdvCiv-SAS/Images/diagnostics/). External-tool examples remain in `Images/tools/`; agent conversations and development demonstrations remain in `Images/LLM/`.

This inventory brings together game, AI, Python, engine and build diagnostics, including what SAS changes relative to inherited output and which diagnostics SAS adds itself.

The file inventory and source references distinguish current writers from historical or other-mod output. Matched Before/After sections show important inherited/current differences without preserving obsolete intermediate SAS stages.

- `PythonDbg.log` (debug messages), `PythonErr.log` (tracebacks) and `PythonErr2.log` (including module-loading output) have captured [Before/After samples](#before-and-after-shared-python-log-timestamps); `xml.log` separately now has real pre-change and rebuilt-DLL After captures for its DLL-controlled UTC/`record=` modernization.
- Screen **LOG** buttons: [manual exports](#screen-log-button-exports) from Battles, Changes, Timeline and Sevopedia comparison charts into `PythonDbg.log`.
- `BBAI_*.log`: [AI decision diagnostics](#bbai), including Settler behavior and formerly independent UWAI reports now merged into BBAI; explicitly covered producers include `MilitaryAnalyst`, `InvasionGraph`, `ArmamentForecast`, `WarEvaluator` and `WarUtilityAspect`.
- SAS-created `SASGameRecord_*.log`: [gameplay/run context](#sasgamerecord-sgr), with a captured gameplay excerpt and a separate full example.
- SAS-created `SASAssertions_<UTC>_startup.log` / `_newN.log` / `_loadN.log`: assertion-enabled DLL failure/resolution evidence, with lazy per-session metadata, a startup-safe sink independent from XML/INI logging gates and optional silent handling once GlobalDefines exist.
- `RandLog` / `MessageLog` INI controls and RNG/message traces such as `MPLog.txt`, `MPLog<player>.log` and `ASyncRand.log`; `OOSLog - <player> - Turn <turn>.log` captures state after multiplayer desynchronization.
- `StartingPos.log` for starting-position diagnostics and `IFP_log.txt` / `TSCProfile.log` for profiling; BUG Autolog supplies a configurable text/HTML gameplay journal.
- `SASRuntimeStatus.json` / `SASRuntimeHistory_*.jsonl`: [latest runtime observation and transition history](#runtime-status-and-history), linked to representative examples.
- Compiler `AdvCiv.log` / `CvGameCoreDLL.dll.build.json`: [build output, progress/results and identity](#dll-build-reports), with tracked example captures and links to the compilation guide. Ordinary generated build logs remain local; the linked `_example` captures are deliberately tracked documentation files.
- Historical/other-mod outputs such as `bull.log` (BULL), `C2C.log` (Caveman2Cosmos) and `MLF.log` (modular XML loading), with uncertain cases such as `ResourceAllocation.log` kept explicit.

## Historical lineage and ownership

The files below do not belong to one logging framework. Civ4 accumulated several generations of engine, Python and mod diagnostics, and that lineage affects ownership, format and safe modernization. Dates identify the earliest documented evidence cited here, not necessarily the first private implementation.

| Output / family | Producer / lineage | Established history and purpose | SAS ownership / modernization implication |
| --- | --- | --- | --- |
| `PythonDbg.log`, `PythonErr.log`, `PythonErr2.log` | Firaxis Civ4 Python/EXE logging, with occasional DLL-written `PythonDbg.log` rows | All three are documented together on 2005-10-28, during Civ4's launch period. `PythonDbg` is the general Python/debug stream; `PythonErr` carries Python exceptions; `PythonErr2` is a secondary startup/interpreter stream rather than simply another traceback file. | The EXE owns file creation and early startup output. SAS consistently formats Python-written rows after `SASPythonLogging` installs. The one current direct DLL-written Starting Position Iteration row in `PythonDbg.log` also uses SAS UTC/`record=` formatting. Earlier/direct EXE rows remain outside SAS control and cannot have their original timestamps reconstructed. |
| `app.log`, `init.log`, `initmgr.log`, `audio.log`, `resmgr.log`, `xml.log`, `LSystem.log`, `network-<port>.txt` | Firaxis engine, with live DLL-origin rows in `xml.log` | Native application, initialization, audio, resource, XML, LSystem and networking diagnostics. Old Civ4 troubleshooting captures already show the engine's numeric elapsed-time-style prefixes. Current SAS source has live DLL writers for `xml.log`; `resmgr.log` retains only a commented-out inherited writer, and no live DLL writer was found for the other listed engine logs. | SAS adds millisecond UTC and stable `record=` fields only to the DLL-owned `xml.log` rows while preserving the native elapsed prefix. EXE-owned rows remain in their native format. Absence of a current DLL writer means SAS has no in-place row-format hook there today; it does not prove that future interception or integration would be impossible. |
| `MPLog.txt`, optional `MPLog<player>.log`, `ASyncRand.log` | Firaxis message-control/RNG logging, later wrapped and extended by AdvCiv | The INI's message/random/synchronization logging family is old Civ4 machinery. AdvCiv introduced `CvDLLLogger` in 2019 to encapsulate the message-control log and supports per-player MP filenames; a 2020 AdvCiv fix made asynchronous RNG logging work correctly. | Preserve deterministic comparability. Session/header context can help, but wall-clock decoration must not obscure RNG or OOS comparisons. |
| BUG Autolog | eotinb -> BUG -> K-Mod/AdvCiv/SAS | Publicly introduced on 2005-11-15 as a note-taking/gameplay journal "with succession games in mind". Its author explicitly distinguished it from Civ4's existing debug/error logs. | Preserve its human-readable journal role. It is configurable text/HTML output, not a machine diagnostic stream. |
| BUG StatusDump | Ruff_Hi / BUG, inherited through K-Mod/AdvCiv | Current SAS loads the inherited `StatusDump` module. Ctrl+Alt+D invokes a support dump using the Autolog path and a `<player>_<year>.txt` filename. Large sections remain literal placeholders such as `Spinner stuff here`, `Player Cities here` and `AIs stuff here`; the older unused helper class still hardcodes `StatusDump.txt`. | Document as an incomplete inherited support facility, not as a dependable SAS diagnostic. Do not modernize it merely because it can emit a file. |
| `BBAI.log` -> `BBAI_*.log` | Better BTS AI -> K-Mod -> AdvCiv -> SAS | Better BTS AI 0.82 publicly documented its AI decision logging system on 2009-11-05: the purpose was to expose major AI decisions each turn for analysis and improvement. The original file was `BBAI.log`. | SAS owns its current BBAI wrapper/filename/session improvements while preserving the log's AI-decision semantics. This is a legacy diagnostic worth modernizing, not replacing. |
| `SASAssertions_*.log` | SAS extension of inherited `FAssert` dialog machinery | Base/K-Mod/AdvCiv assertion-enabled builds display the failed site/message and let the user ignore, debug or abort. Public Better AI/Civ4 modding guidance documents the same popup/manual-report workflow; no equivalent paired persistent assertion/action stream was found in the sources reviewed for this inventory. | SAS records each failed assertion before dialog/automatic resolution and the effective action afterward. Optional silent handling is cached only after all GlobalDefines overrides load; startup failures still log and retain the dialog. The same safe turn/autoplay/active-viewer snapshot decorates the log and dialog. |
| `bull.log` | BULL, the DLL companion to BUG | BULL 1.0 was released with BUG 4.2 on 2009-11-15. Public BULL-derived sources use `bull.log` for DLL-side BUG/options diagnostics. No current SAS filename producer was found. | Treat the local file as historical/foreign evidence unless a current producer is established. |
| `OOSLog - <player> - Turn <turn>.log` | Kek-Mod -> AdvCiv, with idea credited to Fall from Heaven 2 / Kael | Kek-Mod 0.23 (2019-03-18) included `OOSLogger`; AdvCiv merged it on 2019-03-27. Kek-Mod 0.25 (2019-07-16) then incorporated OOSLogger fixes from AdvCiv. It dumps deterministic game state when an OOS is detected. | Keep distinct from `MPLog`: OOSLog is a state snapshot for diffing after divergence, while MPLog helps trace message/RNG activity leading to divergence. |
| `IFP_log.txt` | Inherited DLL internal profiler | Function/call timing profiler output; earliest introduction not established. | Keep numerical/data-oriented. Prefer run metadata or a header to per-row decoration. |
| `TSCProfile.log` | We the People profiler -> AdvCiv | AdvCiv imported Time Stamp Counter profiling code from We the People on 2019-11-05 and integrated it with Civ4 logging. | Keep profiler rows compact and machine-friendly; add provenance/header context only if needed. |
| `StartingPos.log` | AdvCiv | AdvCiv's Starting Position Iteration work began publicly on 2020-05-27 as a fairer-start algorithm; this log traces that subsystem when enabled. | Algorithm trace, not general diagnostics. Header/run context is preferable to verbose per-line timestamps. |
| `juggle_log.txt`, `combat.txt` | K-Mod/AdvCiv developer diagnostics | Compile-time specialist diagnostics: citizen-assignment efficiency and combat-odds verification respectively. Exact first introduction was not established here. | Preserve as experiment datasets. A small metadata header is safer than making every record verbose. |
| `uwai<turn>.log` | AdvCiv `UWAIReport` | Separate war-evaluation reports, with Textile markup, turn-number filenames and report interval/threshold controls. Writers include `UWAIAgent`, `MilitaryAnalyst`, `InvasionGraph`, `ArmamentForecast`, `WarEvaluator` and `WarUtilityAspect`. | Historical in SAS: the standalone report files/logger were retired in favor of five independently controlled BBAI categories; see [UWAI diagnostics comparison](#uwai-diagnostics-standalone-advciv-reports-vs-current-bbai-records). |
| `SASGameRecord_*.log` | AdvCiv-SAS | A new structured game record, complementing inherited BBAI decision traces with run context, periodic state, gameplay history and reproduction evidence. | Independent `SAS_SGR_LOG`; its [revision history](/_1_AdvCiv-SAS/Docs/revisions/SASGameRecord.md) documents recorder changes. |
| `SASRuntimeStatus.json`, `SASRuntimeHistory_*.jsonl`, `SASRuntimeExit_*.json`, optional `SASRuntimeSourceWatch_*.json` / `SASRuntimeSourceChanges_*.jsonl` | AdvCiv-SAS | Latest runtime/process evidence and optional live mod-source/configuration disk-edit observations. | Independent `SAS_RUNTIME_STATUS_ON`; source watching additionally requires default-off `SAS_RUNTIME_SOURCE_WATCH_ON`. Its [revision history](/_1_AdvCiv-SAS/Docs/revisions/SASRuntime.md) documents runtime-recorder changes. |

### Modernization principles

Format changes follow the ownership and purpose of each diagnostic family:

- **SAS-controlled diagnostics:** direct timestamp, filename, session, provenance and flushing improvements are appropriate when they preserve semantics and performance.
- **Shared Python streams:** SAS can improve rows that pass through its Python wrapper after installation, while clearly preserving the existence of EXE-written startup rows that bypass it.
- **EXE-owned Firaxis logs:** do not pretend SAS controls the writer. Modernize DLL-owned rows that deliberately share such a file, but keep EXE-owned rows and their native timing semantics explicit.
- **RNG/OOS/profiling/experiment data:** preserve stable comparison-friendly rows; a header or sidecar is often better than per-row wall-clock text.
- **Human journals such as Autolog:** optimize for readable gameplay notes, not grep-oriented diagnostic structure.
- **Foreign/stale files from other mods:** identify their probable or verified origin, but do not add SAS support merely because they remain in the shared user folder.

## Files present in the user Logs folder

The folder is `Documents/My Games/beyond the sword/Logs`. Presence establishes that a file exists, not that the current SAS run wrote it. Empty files are included.

Inventory snapshot: **2026-10-20 08:34:07 UTC**. The Python captures were taken after process 32608 exited; its runtime status records `EXITED_CLEANLY`.

**Latest modified (UTC)** is the filesystem's last-write time; for a family it is the newest member's time. It helps identify stale evidence but does not establish generation time or which mod wrote it: copying/restoring files can preserve or change filesystem dates. Embedded process/session timestamps provide stronger run identity where available.

| File or family | Present | Latest modified (UTC) | Role / evidence |
| --- | --- | --- | --- |
| `PythonDbg.log` | Yes | 2026-10-20 08:30:49 | Python stdout, direct prints, BUG messages and some DLL diagnostics. |
| `PythonErr.log` | Yes, empty | 2026-10-20 08:16:03 | Python error output; an empty file is distinct from an absent file. |
| `PythonErr2.log` | Yes | 2026-10-20 08:16:03 | Secondary Python output; current sample includes converter warnings and the Python search path. |
| `app.log` | Yes | 2026-10-20 08:30:48 | EXE/application activity; current sample includes activation and framebuffer information. |
| `init.log` | Yes | 2026-10-20 08:16:30 | Startup/version and initialization messages. |
| `initmgr.log` | Yes | 2026-10-20 08:16:30 | EXE initialization manager; current sample includes new-game initialization and elapsed time. |
| `audio.log` | Yes | 2026-10-20 08:16:03 | Audio-manager initialization and asset loading. |
| `resmgr.log` | Yes | 2026-10-20 08:16:31 | Resource-loading diagnostics; current sample includes texture-load failures. |
| `xml.log` | Yes | 2026-10-20 08:16:26 | XML loading and related errors; current DLL also explicitly writes this file. |
| `LSystem.log` | Yes | 2026-10-20 08:16:32 | City/plot LSystem diagnostics; current sample begins with the city LSystem XML. |
| `network-2056.txt` | Yes | 2026-10-20 08:30:49 | Network diagnostics with the configured port in its filename. Other ports/instances may produce other names. |
| `BBAI_*.log` | Yes, 28 files | 2026-10-18 14:08:54 | Timestamped detailed AI diagnostics, including older runs. |
| `SASGameRecord_*.log` | Yes, 1,119 files | 2026-10-20 08:17:39 | Timestamped game/session records, including older runs. |
| `SASRuntimeStatus.json` | Yes | 2026-10-20 08:30:49 | Latest fixed-name runtime observation and linked history identity. |
| `SASRuntimeHistory_*.jsonl` | Yes, 32 files | 2026-10-20 08:30:49 | Per-process runtime history. |

The BBAI/SASGameRecord counts above describe timestamped files, not a requirement that their legacy fixed filenames exist. Configured filename/session/player variations are handled by the shared filename builder.

### Other diagnostic files present

These files exist locally, but no corresponding filename producer was found in current SAS source. They are not evidence that SAS currently generates them; the shared Logs folder can contain output from other mods and earlier runs.

External-source identifications below describe matching public writers, not proof of which exact executable produced the local copy.

| Filename | Present | Latest modified (UTC) | External lineage / interpretation |
| --- | --- | --- | --- |
| `ANewDawn.log` | Yes | 2026-06-04 07:51:16 | Probably Rise of Mankind: A New Dawn by filename/context, but an authoritative producer for this exact file was not established. Keep origin/purpose explicitly unverified. |
| `C2C.log` | Yes | 2026-01-23 07:08:51 | Verified in current Caveman2Cosmos source as a broad generic DLL/debug log used by unrelated systems. |
| `Checksum.log` | Yes | 2026-09-04 13:37:08 | Verified in RoM-AND/C2C lineage: `CvGlobals` writes per-info checksums, useful for comparing loaded XML/info state. |
| `CvGameTextMgr_buildCityBillboardString.log` | Yes | 2026-06-04 08:12:28 | Matching public Civ4-mod evidence identifies this as city-billboard debug output; another project removed an unconditional writer as needless disk I/O. The origin of this local copy is not established. |
| `CvGlobals_logInfoTypeMap.log` | Yes | 2026-08-13 15:58:52 | Verified in modular-DLL descendants as a dump of the string-to-integer info-type map. |
| `CvTechInfo_readPass2.log` | Yes | 2026-08-13 15:58:53 | Producer not verified. The filename suggests second-pass tech-info XML diagnostics, but that interpretation must not be presented as established fact. |
| `CvXMLLoadUtilitySetMod_MLFEnumerateFiles.log` | Yes | 2026-08-30 15:18:26 | Verified in WoC/RoM/C2C-style modular-loading source: traces directories/subdirectories while enumerating module XML files. |
| `MLF.log` | Yes | 2026-08-30 15:18:20 | Verified Modular Loading Framework / modular-loading-control diagnostic, including module selection and load order. |
| `ResourceAllocation.log` | Yes | 2026-06-04 08:12:21 | Producer unverified; retain as unknown foreign/historical residue. |
| `XmlDependencyTypes.log` | Yes | 2026-08-13 15:58:54 | Verified in True Modular / RoM-derived XML loaders as dependency/type-resolution diagnostics. |
| `bull.log` | Yes | 2026-09-13 08:31:55 | BULL/BUG DLL diagnostic lineage is verified in public source, but no current SAS producer was found. |

The manually created ` - Copie` files are backups of existing log types, not additional Civ4 outputs. `Archipelago.cfg`, `Inland_Sea.cfg` and a saved Git diff also reside in Logs but are not log streams.

## Conditional outputs not found in the current Logs folder

These are supported by current source or inherited documentation. Absence does not indicate a fault: their enabling conditions may never have occurred, or an optional facility may not be compiled/enabled.

| File or family | Present here | Source / condition |
| --- | --- | --- |
| `MPLog.txt` | No | Inherited manual identifies the EXE message-control log. Current DLL calls `messageControlLog`; the EXE chooses its actual default filename. |
| `MPLog<player>.log` | No | Current `CvDLLLogger.cpp` explicitly uses this form for RNG logging in network multiplayer with `PER_PLAYER_MESSAGE_CONTROL_LOG`. |
| `ASyncRand.log` | No | `CvGlobals.cpp` assigns this filename to the extended asynchronous RNG; output requires the corresponding RNG logging path to run. |
| `OOSLog - <player> - Turn <turn>.log` | No | `OOSLogger.py` writes desynchronization state when OOS is visible, message logging is enabled and WorldBuilder is not active. Player names can appear in the filename. |
| `StartingPos.log` | No | Starting-position iteration diagnostics when its logging is enabled. |
| `IFP_log.txt` | No | Internal profiler output when that profiling facility runs. |
| `TSCProfile.log` | No | Timestamp-counter profiling, conditional on `USE_TSC_PROFILER` and collected samples. |
| `juggle_log.txt` | No | Citizen-assignment diagnostic inside `LOG_JUGGLE_CITIZENS`. |
| `combat.txt` | No | Combat-outcome diagnostic inside `LOG_COMBAT_OUTCOMES`. |
| `SASAssertions_<UTC>_startup.log`, `_newN.log`, `_loadN.log` | Not present in the 2026-10-20 inventory baseline; first development captures taken 2026-10-22 | Lazily created by an assertion-enabled SAS DLL only after a failed runtime SAS-DLL assertion in that startup/new/load session. A metadata row identifies the session/build/DLL; each `SAS_ASSERT_FAILURE` is followed by its resolved `SAS_ASSERT_CHOICE`. The default cached policy is automatic Ignore Once after GlobalDefines load, while normal Release builds compile these assertions out. |
| BUG Autolog `<configured name>.txt` / `.html` | Not found in Logs or the checked default Autolog directories | User-configurable gameplay journal; its filename, directory and format are configurable, so this is not proof that no output exists elsewhere. |
| BUG StatusDump `<player>_<year>.txt` | Not found in the checked default Autolog directories | Current inherited module listens for Ctrl+Alt+D and writes through `BugFile` using the Autolog path. The implementation is incomplete and still emits placeholder sections; an older unused helper class separately hardcodes `StatusDump.txt`. |

`RandLog` and `SynchLog` are INI options, not verified standalone filenames in this inventory. RNG messages can go into the message-control log or an explicitly assigned RNG file. The synchronization-output filename is EXE-owned and has not been established here.

`debug_SPaH.log` appears only in a commented-out source statement; it is not an active output path. `Profile output.txt` likewise remains in a commented-out block in `TSCProfiler.cpp`; the active profiler writer uses `TSCProfile.log`. Obsolete commented filenames should not be presented as currently supported logs.

## Outputs outside the user Logs folder

| Output | Present | Meaning |
| --- | --- | --- |
| `CvGameCoreDLL/Project/<configuration>/AdvCiv.log` | Yes, Release and Debug-opt | Compiler/linker diagnostics, not game output. |
| `<DLL filename>.build.json` | Yes | Build status, configuration, inputs, warning/error counts and binary identity; includes the installed DLL's companion report. |
| BUG Autolog / StatusDump directory | No current file found in the checked default paths | Autolog and StatusDump normally use their configurable/default Autolog directory rather than requiring `Logs`. |
| `ThemeParseLog.txt` | Not inventoried in this snapshot | Historical BtS engine/theme parser diagnostic reported in the Beyond the Sword installation directory rather than the user `Logs` folder. It records `.thm` parsing/resource errors; some warnings can be benign. |
| Crash dump files | Not inventoried here | Binary crash evidence, not a text log. `GenerateCrashDumps=1` is currently configured; actual dump location/presence needs separate inspection. |

## Historical engine outputs not present in this snapshot

- `legacy.log` appears in old Civ4 troubleshooting captures with low-level graphics/resource compatibility messages such as legacy tree/asset use. It was not present in the inspected SAS Logs snapshot.
- `Python.log` appears in some early Civ4 troubleshooting material, but its exact relationship to the persistent `PythonDbg.log`/error trio across versions was not established. Treat it as a historical variant, not an expected current SAS file.

## Inspected switches and timestamp evidence

The inspected `CivilizationIV.ini` has:

| Setting | Value |
| --- | --- |
| `LoggingEnabled` | `1` |
| `OverwriteLogs` | `1` |
| `MessageLog` | `0` |
| `RandLog` | `0` |
| `SynchLog` | `0` |
| `GenerateCrashDumps` | `1` |

BBAI, SASGameRecord and SAS runtime recording have their own SAS controls; these files are not governed solely by the EXE logging switches.

Several existing engine files already begin messages with numeric timing tags such as `[30717.468]`. Old Civ4 captures show this style long before SAS.

Better BTS AI's original logging documentation describes its own left-hand values as time in seconds relative to Civ startup, with some uncertainty about the precise origin. This does not establish the clock source of every EXE log prefix; do not reinterpret those numbers as UTC calendar timestamps.

At this inventory baseline, `BugUtil` added local `HH:MM:SS` prefixes to its own messages, whereas direct Python prints and multiline dumps followed their writers' formatting. The shared Python writer described below uses UTC timestamps.

BBAI, SASGameRecord and runtime output already carry substantial instrumentation; timestamp/archival work should account for that existing context. Before/after comparisons should use real captured samples and distinguish timestamps emitted by a writer from observation times supplied by an external collector.

## SAS assertion diagnostics

Assertion-enabled SAS DLLs extend the inherited Civ4 `FAssert` dialog path with persistent evidence and optional unattended handling. Output is independent of `LoggingEnabled`, BBAI, SASGameRecord and runtime-status switches. It is lazy: a startup/menu/new/load session with no failed runtime assertion creates no assertion file.

`SAS_ASSERT_FAILURE` is submitted before any dialog or automatic action. `SAS_ASSERT_CHOICE` is then submitted after resolution with the effective action, whether it was automatic, any Stop-Autoplay fallback, and the actual dialog result when a dialog existed. Both rows use the same captured game context and assertion site.

The writer opens/appends/closes each completed row with shared-read access, so a second process can inspect the file while Civ4 is running. It does not call `FlushFileBuffers`, and therefore does not promise physical-media durability against power/system loss.

The default `SAS_ASSERT_SILENT_ACTION=1` automatically chooses inherited **Ignore Once** after GlobalDefines finish loading. This is intentionally useful for unattended Debug-opt/Assert autoplay: a repeated assertion no longer blocks the run, but every occurrence and resolution remains available for live or later analysis.

Mode `0` uses the normal dialog, mode `2` chooses Ignore Always, and mode `3` stops autoplay when possible or otherwise chooses Ignore Once. Startup assertions before the policy cache exists keep the normal dialog. Ignore actions do not fix the failed condition; they only continue through the inherited path.

### Session files and metadata

The filename identifies the assertion logger's observed lifecycle: `SASAssertions_<UTC>_startup.log` covers failures before opening-menu/game identity exists; actual opening-menu scene requests establish `_menu1`, `_menu2`, etc.; new games and loaded saves share a separate sequence such as `_new1`, `_load2`, `_new3`. WorldBuilder and advisors remain inside their current game session.

Session numbering advances at every observed boundary even when no file is created. For example, a quiet `_new1` session can be followed by `_load2` without any `_new1` assertion file. Menu visits use their own counter and therefore never consume new/load numbers.

These counters intentionally belong only to SASAssertions, keeping optional assertion diagnostics from advancing or changing the established BBAI/SASGameRecord session numbering. Those loggers are independently gated and keep their existing counters, so equal numeric suffixes across log families are not a correlation guarantee.

Use UTC timestamps, process identity and surrounding metadata when matching records across families.

The process-wide `assertion=` number does not reset during rollovers. Each failure/choice row also carries `session=` plus `sessionSequence=` so copied excerpts remain self-identifying.

Each created file begins with `SAS_ASSERT_METADATA`. It records process/session start identity, PID/TID, assertion/build enablement, the initial cached handling mode, writer behavior and the exact loaded DLL's lightweight binary identity. Fixed process/DLL identity and session-start details stay in that header rather than being repeated on every event row.

Event rows retain only the compact session label/sequence plus thread and dynamic assertion/game context, so copied excerpts remain self-identifying without duplicating the heavier metadata.

Effective silent policy remains on failure/choice rows because startup handling can differ from the post-GlobalDefines cache. The assertion path reuses cached loaded-module metadata rather than scanning current build intermediates or `temp_files`.

### Captured assertion examples

The current examples preserve unchanged startup and gameplay captures from the same Debug-opt process. Original timestamps and DLL identity connect the files, while the process-wide assertion numbers continue across them.

#### Startup example

[SASAssertions_startup_example.log](/_1_AdvCiv-SAS/Docs/examples/assertions/SASAssertions_startup_example.log) is reproduced in full below. In this capture, metadata is followed by several assertions: the first is handled manually before the policy cache loads, and later failures use automatic Ignore Once.

```log
2026-10-22T11:46:01.022Z record=SAS_ASSERT_METADATA pid=40788 tid=25968 processStartUtc=2026-10-22T11:45:58.906Z session=startup sessionSequence=0 sessionStartUtc=2026-10-22T11:45:58.906Z assertionsEnabled=1 initialSilentMode=-1 initialSilentPolicy=STARTUP_DIALOG writer=OPEN_APPEND_CLOSE liveReadable=1 forcedPhysicalFlush=0 build=Debug-opt moduleFound=1 fileReadable=1 fileSizeBytes=14700544 dllFingerprint=FNV1A64:E2DF645582B673E9 dllLastWriteUtc=20261022T114354.489Z peTimestampRaw=1792669425 peTimestampUtc=20261022T114345Z resourceFileVersion=- resourceProductVersion=- fassertEnabled=1
2026-10-22T11:46:01.022Z record=SAS_ASSERT_FAILURE assertion=1 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=-1 silentPolicy=STARTUP_DIALOG file="..\\.\\CvGlobals.cpp" line=927 function="CvGlobals::getDefineSTRING" expression="bSuccess" message="Missing STRING define 'SAS_MOD_DISPLAY_NAME' | XML=xml\\GameInfo/CIV4GraphicOptionInfos.xml"
2026-10-22T11:46:03.900Z record=SAS_ASSERT_CHOICE assertion=1 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=-1 silentPolicy=STARTUP_DIALOG choice=IGNORE_ONCE action=IGNORE_ONCE automatic=0 silentFallback=- actionCode=1 dialogShown=1 dialogResult=1 file="..\\.\\CvGlobals.cpp" line=927 function="CvGlobals::getDefineSTRING" expression="bSuccess" message="Missing STRING define 'SAS_MOD_DISPLAY_NAME' | XML=xml\\GameInfo/CIV4GraphicOptionInfos.xml"
2026-10-22T11:46:04.566Z record=SAS_ASSERT_FAILURE assertion=2 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\CvInfo_GameOption.cpp" line=493 function="CvGameSpeedInfo::read" expression="m_iResearchPercent >= 100 ? (m_iGoldenAgePercent * 3 > m_iResearchPercent && m_iGoldenAgePercent <= m_iResearchPercent) : (3 * m_iGoldenAgePercent < 4 * m_iResearchPercent && m_iGoldenAgePercent >= m_iResearchPercent)" message="The Golden Age modifier gets used for various adjustments; unusual values should be avoided."
2026-10-22T11:46:04.566Z record=SAS_ASSERT_CHOICE assertion=2 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\CvInfo_GameOption.cpp" line=493 function="CvGameSpeedInfo::read" expression="m_iResearchPercent >= 100 ? (m_iGoldenAgePercent * 3 > m_iResearchPercent && m_iGoldenAgePercent <= m_iResearchPercent) : (3 * m_iGoldenAgePercent < 4 * m_iResearchPercent && m_iGoldenAgePercent >= m_iResearchPercent)" message="The Golden Age modifier gets used for various adjustments; unusual values should be avoided."
2026-10-22T11:46:06.203Z record=SAS_ASSERT_FAILURE assertion=3 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\CvXMLLoadUtilityGet.cpp" line=431 function="CvXMLLoadUtility::GetChildXmlVal" expression="false" message="Error in GetChildXmlVal function, unable to find a child node"
2026-10-22T11:46:06.203Z record=SAS_ASSERT_CHOICE assertion=3 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\CvXMLLoadUtilityGet.cpp" line=431 function="CvXMLLoadUtility::GetChildXmlVal" expression="false" message="Error in GetChildXmlVal function, unable to find a child node"
2026-10-22T11:46:06.203Z record=SAS_ASSERT_FAILURE assertion=4 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\CvXMLLoadUtilityGet.cpp" line=431 function="CvXMLLoadUtility::GetChildXmlVal" expression="false" message="Error in GetChildXmlVal function, unable to find a child node"
2026-10-22T11:46:06.203Z record=SAS_ASSERT_CHOICE assertion=4 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\CvXMLLoadUtilityGet.cpp" line=431 function="CvXMLLoadUtility::GetChildXmlVal" expression="false" message="Error in GetChildXmlVal function, unable to find a child node"
2026-10-22T11:46:06.203Z record=SAS_ASSERT_FAILURE assertion=5 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\CvXMLLoadUtilityGet.cpp" line=431 function="CvXMLLoadUtility::GetChildXmlVal" expression="false" message="Error in GetChildXmlVal function, unable to find a child node"
2026-10-22T11:46:06.204Z record=SAS_ASSERT_CHOICE assertion=5 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\CvXMLLoadUtilityGet.cpp" line=431 function="CvXMLLoadUtility::GetChildXmlVal" expression="false" message="Error in GetChildXmlVal function, unable to find a child node"
2026-10-22T11:46:06.204Z record=SAS_ASSERT_FAILURE assertion=6 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\CvXMLLoadUtilityGet.cpp" line=431 function="CvXMLLoadUtility::GetChildXmlVal" expression="false" message="Error in GetChildXmlVal function, unable to find a child node"
2026-10-22T11:46:06.204Z record=SAS_ASSERT_CHOICE assertion=6 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\CvXMLLoadUtilityGet.cpp" line=431 function="CvXMLLoadUtility::GetChildXmlVal" expression="false" message="Error in GetChildXmlVal function, unable to find a child node"
2026-10-22T11:46:06.204Z record=SAS_ASSERT_FAILURE assertion=7 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\CvXMLLoadUtilityGet.cpp" line=431 function="CvXMLLoadUtility::GetChildXmlVal" expression="false" message="Error in GetChildXmlVal function, unable to find a child node"
2026-10-22T11:46:06.204Z record=SAS_ASSERT_CHOICE assertion=7 tid=25968 session=startup sessionSequence=0 activity=UNAVAILABLE gameObjectAvailable=1 finalInitialized=0 turn=-1 elapsed=-1 autoPlayRemaining=-1 activePlayer=-1 activeTeam=-1 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\CvXMLLoadUtilityGet.cpp" line=431 function="CvXMLLoadUtility::GetChildXmlVal" expression="false" message="Error in GetChildXmlVal function, unable to find a child node"
```

Note: several of the sample examples in this section are now seemingly fixed, but remain valid/illustrative examples; notably:

- the former (now deleted SAS define) `SAS_MOD_DISPLAY_NAME`-related assertion rows capture the startup-order issue addressed by [KI#110.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-110.2); this example predates the INI-backed name cache.
- The `CvGameSpeedInfo::read` Golden Age assertion rows capture SAS-added Nitro's former 55% Golden Age modifier against its 33% research pace; the inherited AdvCiv check diagnoses this relationship rather than changing gameplay. [KI#92.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-92.2) documents the 40% setting, giving three base Golden Age turns instead of the earlier SAS value's four.
- The consecutive `CvXMLLoadUtility::GetChildXmlVal` failures are consistent with direct comments encountered by the inherited civilization mapping reader. [KI#3.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-3.2) distinguishes that hypothesis from unverified tail-mapping loss, and documents count-independent sibling traversal, comment skipping and caller-context assertions for replay diagnosis.

#### Gameplay example

[SASAssertions_game_example.log](/_1_AdvCiv-SAS/Docs/examples/assertions/SASAssertions_game_example.log) illustrates gameplay after either creating a new game or loading a save. The current capture is from a loaded game and shares process identity with the startup example.

- In this example, metadata precedes **6,576 failure/choice pairs** (6,260,100 bytes), spanning recorded turns 98–366 and ending in `GAME_OVER`.
- The excerpt below keeps the metadata and one complete pair from each of the seven distinct assertion sites in this capture. It includes the once-only city-defense failure and both different `InvasionGraph::Node::step` conditions; gaps in assertion numbers omit repeated occurrences.

```log
2026-10-22T11:47:09.573Z record=SAS_ASSERT_METADATA pid=40788 tid=25968 processStartUtc=2026-10-22T11:45:58.906Z session=load1 sessionSequence=1 sessionStartUtc=2026-10-22T11:46:20.030Z assertionsEnabled=1 initialSilentMode=1 initialSilentPolicy=IGNORE_ONCE writer=OPEN_APPEND_CLOSE liveReadable=1 forcedPhysicalFlush=0 build=Debug-opt moduleFound=1 fileReadable=1 fileSizeBytes=14700544 dllFingerprint=FNV1A64:E2DF645582B673E9 dllLastWriteUtc=20261022T114354.489Z peTimestampRaw=1792669425 peTimestampUtc=20261022T114345Z resourceFileVersion=- resourceProductVersion=- fassertEnabled=1
2026-10-22T11:47:09.573Z record=SAS_ASSERT_FAILURE assertion=8 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=98 elapsed=98 autoPlayRemaining=403 activePlayer=0 activeTeam=0 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\CvPlayer.cpp" line=10831 function="CvPlayer::isBuildingClassMaxedOut" expression="getBuildingClassCount(eBuildingClass) <= GC.getInfo(eBuildingClass).getMaxPlayerInstances() + GC.getInfo(eBuildingClass).getExtraPlayerInstances()" message=""
2026-10-22T11:47:09.574Z record=SAS_ASSERT_CHOICE assertion=8 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=98 elapsed=98 autoPlayRemaining=403 activePlayer=0 activeTeam=0 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\CvPlayer.cpp" line=10831 function="CvPlayer::isBuildingClassMaxedOut" expression="getBuildingClassCount(eBuildingClass) <= GC.getInfo(eBuildingClass).getMaxPlayerInstances() + GC.getInfo(eBuildingClass).getExtraPlayerInstances()" message=""
2026-10-22T11:48:10.183Z record=SAS_ASSERT_FAILURE assertion=27 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=148 elapsed=148 autoPlayRemaining=353 activePlayer=0 activeTeam=0 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\CvPlayerAI.cpp" line=2415 function="CvPlayerAI::AI_conquerCity" expression="false" message="Just to test AI liberation upon conquest"
2026-10-22T11:48:10.184Z record=SAS_ASSERT_CHOICE assertion=27 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=148 elapsed=148 autoPlayRemaining=353 activePlayer=0 activeTeam=0 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\CvPlayerAI.cpp" line=2415 function="CvPlayerAI::AI_conquerCity" expression="false" message="Just to test AI liberation upon conquest"
2026-10-22T11:51:07.807Z record=SAS_ASSERT_FAILURE assertion=50 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=227 elapsed=227 autoPlayRemaining=274 activePlayer=1 activeTeam=1 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\CvUnitAI.cpp" line=17091 function="CvUnitAI::AI_guardCityOnlyDefender" expression="getGroup()->getNumUnits() == 1" message=""
2026-10-22T11:51:07.808Z record=SAS_ASSERT_CHOICE assertion=50 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=227 elapsed=227 autoPlayRemaining=274 activePlayer=1 activeTeam=1 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\CvUnitAI.cpp" line=17091 function="CvUnitAI::AI_guardCityOnlyDefender" expression="getGroup()->getNumUnits() == 1" message=""
2026-10-22T11:58:03.072Z record=SAS_ASSERT_FAILURE assertion=55 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=336 elapsed=336 autoPlayRemaining=165 activePlayer=3 activeTeam=3 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\InvasionGraph.cpp" line=1419 function="InvasionGraph::Node::step" expression="iDefCities <= 0" message="No typical garrison unit found"
2026-10-22T11:58:03.072Z record=SAS_ASSERT_CHOICE assertion=55 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=336 elapsed=336 autoPlayRemaining=165 activePlayer=3 activeTeam=3 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\InvasionGraph.cpp" line=1419 function="InvasionGraph::Node::step" expression="iDefCities <= 0" message="No typical garrison unit found"
2026-10-22T11:58:03.072Z record=SAS_ASSERT_FAILURE assertion=56 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=336 elapsed=336 autoPlayRemaining=165 activePlayer=3 activeTeam=3 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\InvasionGraph.cpp" line=1471 function="InvasionGraph::Node::step" expression="!bNoGuardUnit || iDefCities <= 0" message=""
2026-10-22T11:58:03.072Z record=SAS_ASSERT_CHOICE assertion=56 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=336 elapsed=336 autoPlayRemaining=165 activePlayer=3 activeTeam=3 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\InvasionGraph.cpp" line=1471 function="InvasionGraph::Node::step" expression="!bNoGuardUnit || iDefCities <= 0" message=""
2026-10-22T11:58:40.237Z record=SAS_ASSERT_FAILURE assertion=3917 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=344 elapsed=344 autoPlayRemaining=157 activePlayer=3 activeTeam=3 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\CvCity.cpp" line=5585 function="CvCity::changeMilitaryHappinessUnits" expression="getMilitaryHappinessUnits() >= 0" message=""
2026-10-22T11:58:40.237Z record=SAS_ASSERT_CHOICE assertion=3917 tid=25968 session=load1 sessionSequence=1 activity=AUTOPLAY gameObjectAvailable=1 finalInitialized=1 turn=344 elapsed=344 autoPlayRemaining=157 activePlayer=3 activeTeam=3 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\CvCity.cpp" line=5585 function="CvCity::changeMilitaryHappinessUnits" expression="getMilitaryHappinessUnits() >= 0" message=""
2026-10-22T12:01:22.827Z record=SAS_ASSERT_FAILURE assertion=5592 tid=25968 session=load1 sessionSequence=1 activity=GAME_OVER gameObjectAvailable=1 finalInitialized=1 turn=366 elapsed=366 autoPlayRemaining=0 activePlayer=3 activeTeam=3 silentMode=1 silentPolicy=IGNORE_ONCE file="..\\.\\CvReplayInfo.cpp" line=1039 function="CvReplayInfo::checkBounds" expression="m->bDisplayOtherMods || m->iVersionRead < REPLAY_VERSION" message=""
2026-10-22T12:01:22.827Z record=SAS_ASSERT_CHOICE assertion=5592 tid=25968 session=load1 sessionSequence=1 activity=GAME_OVER gameObjectAvailable=1 finalInitialized=1 turn=366 elapsed=366 autoPlayRemaining=0 activePlayer=3 activeTeam=3 silentMode=1 silentPolicy=IGNORE_ONCE choice=AUTOMATIC action=IGNORE_ONCE automatic=1 silentFallback=- actionCode=1 dialogShown=0 dialogResult=-1 file="..\\.\\CvReplayInfo.cpp" line=1039 function="CvReplayInfo::checkBounds" expression="m->bDisplayOtherMods || m->iVersionRead < REPLAY_VERSION" message=""
```

The full game capture also illustrates how a repeatedly failing check can generate substantial output: silent handling removes popup clicks, but does not repair the failed condition or eliminate its recording cost. Some captured conditions were addressed during subsequent review; notably:

- [KI#486.5](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-486.5) retires the inherited `AI_conquerCity` development probe shown here. It marked preliminary path entry, whereas enabled SASGameRecord/BBAI diagnostics record actual conquest-liberation decisions and KI#486.2 documents a successful transfer replay.
- [KI#49.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-49.2) addresses the `AI_guardCityOnlyDefender` singleton assumption illustrated here: a multi-unit Reserve group can leave one defender instead of parking the whole group. Enabled Unit BBAI diagnostics report the split as `RESERVE_ONLY_DEFENDER_SPLIT`.
- [KI#537.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-537.2) retires the paired `InvasionGraph::Node::step` city-count assertions shown here. KI#537 made a live player with no currently trainable representative a valid `MilitaryBranch` state; the existing Warrior-power fallback remains, while high-detail InvasionGraph BBAI now records `unit=NONE` explicitly.
- The `CvReplayInfo::checkBounds` rows illustrate replay identity checks encountered when opening the Hall of Fame; [KI#166.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-166.2) and [KI#166.3](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-166.3) document the related replay-identity and date-bound fixes.

### Historical comparison

Public Civ4/mod documentation shows the traditional workflow clearly: Better AI asked testers to use an Assert build, manually capture the assertion popup, then choose Ignore Once or Always Ignore.

Civ4 DLL compilation guidance likewise describes using assertion-enabled builds/dialogs and a debugger, and recent Civ4Col discussion still describes individual assertions as popups that can be ignored or reported.

These sources support the comparison that persistent paired assertion/action rows plus an unattended policy are an SAS extension of the inherited popup workflow. They do **not** prove that no Civ4 derivative anywhere has independently built similar tooling.

- [Better AI assert-test instructions (CivFanatics)](https://forums.civfanatics.com/threads/a-better-ai.191685/page-91)
- [Civ4 DLL build/debugging discussion of FAssert and Assert builds (CivFanatics)](https://forums.civfanatics.com/threads/cvgamecoredll-build-error-boost-python-list-hpp.648072/page-2)
- [Civ4 modding discussion explaining Ignore Always / Release behavior (CivFanatics)](https://forums.civfanatics.com/threads/ai-founding-city-behavior.657249/)
- [Recent Civ4Col/We the People assertion discussion (CivFanatics)](https://forums.civfanatics.com/threads/assertive-assert.699650/)

## SAS AI and game-record diagnostics

BBAI and SASGameRecord answer different questions: BBAI explains detailed AI decisions and candidate calculations; SASGameRecord supplies the broader game/run history needed to interpret them. SASGameRecord is an additional SAS-created output, not a renamed inherited BBAI or UWAI report.

Both can use UTC-stamped new/load filenames, shared source/DLL identity and the live-readable diagnostic writer. These are separate from the Python-stream modernization described below: BBAI and SASGameRecord retain their own compact row formats rather than receiving `record=` or a UTC clock prefix on every row.

### Session headers and provenance

Both log families place canonical mod/source context and exact loaded-DLL build/binary provenance immediately after the session lifecycle marker.

The source row records the practical commit-count version when available, exact Git commit, branch/date metadata when known, tracked dirty state/files for a live Git checkout, and a compact fingerprint/byte count of tracked gameplay code/rules/scripts changes relative to `HEAD`.

The shared DLL row separately records the build target, file size, a diagnostic FNV-1a 64-bit fingerprint of the DLL bytes, DLL last-write and PE/linker timestamps, and relevant compile flags, so source/rules edits and the binary actually loaded by Civ4 can be distinguished independently.

For example, a changed C++ diff fingerprint with an unchanged DLL fingerprint exposes a rebuild/copy mistake, while XML/Python edits can legitimately change only the source-diff fingerprint.

With no scoped tracked diff the byte count is `0`; unavailable Git-derived provenance remains explicit instead of being mislabeled as clean. These fingerprints are diagnostic identities, not cryptographic security hashes.

Identity rows place the stable `processUtc` for one Civ4 launch before plain `utc`; the row type identifies that second timestamp as a new-game, save-load or individual snapshot observation. Timestamped filename counters such as `new1` and `load2` preserve game order within the process.

`dirty` is tri-state: `-1` means unavailable because there is no inspectable Git worktree (for example an extracted GitHub ZIP), `0` means Git verified the tracked tree clean, and `1` means tracked local edits were found.

### SASGameRecord (SGR)

SASGameRecord is abbreviated SGR in current recorder define names (`SAS_SGR_*`).

For example, `SAS_SGR_MAP_ASCII_SCALE_1_PCT` and `SAS_SGR_MAP_ASCII_SCALE_2_PCT` size the small/medium initial text-map previews.

The first name previously read `SAS_SGR_MAP_ASCII_OVERVIEW_1_SCALE_PCT`: `MAP_ASCII` already identifies the text map, so dropping `OVERVIEW` makes it shorter and avoids suggesting the unrelated Domestic Advisor Overview tabs. The second setting follows the same pattern.

Enable `SAS_SGR_LOG` in [`GlobalDefines_advciv_sas.xml`](/Assets/XML/GlobalDefines_advciv_sas.xml); `0` disables the recorder independently of BBAI. `SAS_SGR_LOG_USE_TIMESTAMPED_FILENAME` selects per-session `SASGameRecord_*.log` files or the fixed `SASGameRecord.log` name.

The record brings together map/geography context, settings and provenance, economy/expansion, city and battle history, diplomacy and military composition. It also records exact AI strategy/victory-stage transitions, RNG evidence and shared diagnostic-writer health according to the selected level and supporting switches.

- With system context enabled, the session-settings baseline includes `group=PYTHON_RUNTIME_CONTEXT source=RUNNING_INTERPRETER`, reporting the interpreter executing the collector rather than assuming the separate Python 2.4 syntax checker matches it.
- At system-context level 2+, `GAME_RECORD_RUNTIME_CONTEXT` records `pointerBits`, `intBits`, `intMax` and `processTotalVirtualBytes`; the EXE identity reports `exeLargeAddressAware`.
  - A signed integer ceiling and the process address-space ceiling are different limits. Existing performance snapshots separately report working-set/page-file usage and available virtual memory when performance metrics are enabled.
  - `intMax` is not a universal safe gameplay ceiling: some enum-map values use narrower storage, commerce can be stored at times-100 precision, and multiplication can overflow before a final division. Those field/calculation limits need their own source review.
  - The [Chronicles of Mankind population-limit discussion](https://forums.civfanatics.com/threads/chronicles-of-mankind.643052/post-17003355) prompted this numeric-versus-address-space distinction.
  - C2C also has a [report of city outputs failing around 210,000–220,000](https://github.com/caveman2cosmos/Caveman2Cosmos/issues/1604); it is a separate arithmetic-audit lead, not evidence that SAS has the same defect or threshold.
- `processTotalVirtualBytes` is Windows' reported user-mode address-space total, not installed RAM or a promise that an allocation of that size can succeed. Fragmentation, mappings and other allocations still matter; the EXE's LAA flag affects address-space eligibility, not the range of C++ `int`.
  - See Microsoft's [memory/address-space limits](https://learn.microsoft.com/en-us/windows/win32/memory/memory-limits-for-windows-releases) and [integer limits](https://learn.microsoft.com/en-us/cpp/cpp/integer-limits).

- Search examples include `GAME_RECORD_SOURCE_CONTEXT`, `GAME_RECORD_DLL_CONTEXT`, `GAME_RECORD_AI_STRATEGY_CHANGE`, `GAME_RECORD_AI_VICTORY_STAGE_CHANGE` and `GAME_RECORD_DIAGNOSTIC_WRITER`.
- `SAS_SGR_INTERVAL_T_UNSCALED_GS` controls periodic snapshots; with interval 10 they occur at completed turns 10, 20, 30 and so on, while turn 0 has separate initial context. Chronicle actions can appear between snapshots.
- This is an all-player diagnostic and can contain spoilers. Use the [Main Changes Guide's SASGameRecord section](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md#sasgamerecord-log) and [recorder revision history](/_1_AdvCiv-SAS/Docs/revisions/SASGameRecord.md) for coverage/controls, and the [representative raw record](/_1_AdvCiv-SAS/Docs/examples/sasgamerecord/SASGameRecord_example.log) for actual output.

#### SASGameRecord session header example

For example, `SASGameRecord_*.log` starts with lifecycle, provenance and run-setup rows before adding RNG/state checkpoints and compact turn snapshots. These selected rows are from `SASGameRecord_20261025T180717Z_load1.log` (recorder revision 172), including an actual test branch one commit ahead of main and its local XML source-diff evidence; gaps in `seq` mean intervening rows are omitted:

```log
GAME_RECORD_SAVE_LOADED seq=1 processUtc=20261025T180708Z utc=20261025T180717Z logFile="SASGameRecord_20261025T180717Z_load1.log" turn=0 elapsed=0 year=-50000 scenario=0 activePlayer=0 activeCivilization=CIVILIZATION_KOREA activeHandicap=HANDICAP_MONARCH playersDefined=16 playersAlive=16 playersEverAlive=16 humans=1 sessionWallMilliseconds=0
GAME_RECORD_SESSION_CONTEXT seq=2 gameType=GAME_SP_LOAD gameMode=GAMEMODE_NORMAL newGame=0 savedGame=1 scenario=0 gameMultiplayer=0 networkMultiplayer=0 hotseat=0 pbem=0 pitboss=0 simultaneousTeamTurns=0 mpOptions=-
GAME_RECORD_GAME_SETTINGS seq=3 mapScript="Archipelago" map=120x84 landHeavy=0 navalHeavy=1 world=WORLDSIZE_HUGE climate=CLIMATE_TEMPERATE seaLevel=SEALEVEL_MEDIUM gameSpeed=GAMESPEED_NORMAL startEra=ERA_ANCIENT calendar=CALENDAR_DEFAULT startTurn=0 startYear=-50000 gameHandicap=HANDICAP_MONARCH maxTurns=500 targetScore=0 advancedStartConfiguredPoints=-1 advancedStartXmlDefaultPoints=-1 victories=VICTORY_SCORE,VICTORY_TIME,VICTORY_CONQUEST,VICTORY_DOMINATION,VICTORY_CULTURAL,VICTORY_SPACE_RACE,VICTORY_DIPLOMATIC options=GAMEOPTION_AGGRESSIVE_AI,GAMEOPTION_NO_EVENTS
GAME_RECORD_WAR_AI_SETTINGS seq=8 warPeaceAI=UWAI uwaiMode=FULL engineAggressiveAI=1 USE_KMOD_AI_NONAGGRESSIVE=0 DISABLE_UWAI=0 UWAI_IN_BACKGROUND=0 SAS_UWAI_NAVAL_LOGISTICS_DEPLOYMENT_ON=1
GAME_RECORD_RUNTIME_CONTEXT seq=9 systemContextLevel=2 win32Runtime=NATIVE_WINDOWS wineVersion=- windowsMajor=10 windowsMinor=0 windowsBuild=19045 windowsUpdateRevision=6466 windowsServicePackMajor=0 windowsServicePackMinor=0 windowsDisplayVersion="22H2" pointerBits=32 processArch=X86 nativeArch=X64 wow64=1 cpuVendor=- cpuBrand=- logicalProcessors=-1 totalPhysicalMemoryMB=-1 processPriorityClass=- processAffinityQueryAvailable=-1 processAffinityMask=- systemAffinityMask=- debuggerAttached=-1 developmentProcessScanAvailable=-1 vcExpressRunning=-1 devenvRunning=-1 msBuildRunning=-1 nmakeRunning=-1 clRunning=-1 linkRunning=-1
GAME_RECORD_GAME_RNG seq=10 mapRandState=2502007618 syncRandState=4091165095 initialMapRandSeed=35414771 initialSyncRandSeed=35414771
GAME_RECORD_MOD_CONTEXT seq=15 displayName="AdvCiv-SAS" folderName="AdvCiv-SAS" modPath="Mods\\AdvCiv-SAS\\"
GAME_RECORD_SOURCE_CONTEXT seq=16 recordRevision=172 version="6685" commit="126f63d50557b15f99af0257bc6017fad6736b57" shortCommit="126f63d505" branch="codex/autoplay-branch-context" commitDate="2026-10-25T19:05:27+01:00" metadataSource="git" defaultBranch="main" defaultCommit="a89fd0967e68949416854fb8ed3ab1f57530b06e" defaultVersion="6684" defaultRefSource="LOCAL_BRANCH" mergeBaseCommit="a89fd0967e68949416854fb8ed3ab1f57530b06e" mergeBaseVersion="6684" branchRelation="AHEAD_OF_DEFAULT" currentOnlyCommits=1 defaultOnlyCommits=0 dirty=1 dirtyTrackedCount=1 sourceDiffDetailsAvailable=1 sourceDiffEntries=1 trackedCodeRulesDiffBytes=2534 trackedCodeRulesDiffFingerprint="FNV1A64:2AEE28C0D5AFEE3D" stagedCodeRulesDiffBytes=0 stagedCodeRulesDiffFingerprint="FNV1A64:CBF29CE484222325" unstagedCodeRulesDiffBytes=2534 unstagedCodeRulesDiffFingerprint="FNV1A64:2AEE28C0D5AFEE3D" dirtyFiles="[ M] Assets/XML/GlobalDefines_advciv_sas.xml"
GAME_RECORD_SOURCE_DIFF_SUMMARY seq=17 available=1 entries=1 stagedBytes=0 stagedFingerprint="FNV1A64:CBF29CE484222325" unstagedBytes=2534 unstagedFingerprint="FNV1A64:2AEE28C0D5AFEE3D" scope=TRACKED_RUNTIME_CODE_RULES
GAME_RECORD_SOURCE_DIFF_FILE seq=18 index=0 scope="UNSTAGED" path="Assets/XML/GlobalDefines_advciv_sas.xml" diffBytes=2534 diffFingerprint="FNV1A64:2AEE28C0D5AFEE3D"
GAME_RECORD_DLL_CONTEXT seq=19 build=Release moduleFound=1 fileReadable=1 fileSizeBytes=8204288 dllFingerprint=FNV1A64:B9FE3361A2E7B53F dllLastWriteUtc=20261025T163024.228Z peTimestampRaw=1792945823 peTimestampUtc=20261025T163023Z resourceFileVersion=- resourceProductVersion=- buildEvidence=EMBEDDED buildRequest=BUILD preexistingObjectCount=0 preexistingIncompleteMarkerCount=0 preexistingPch=0 reusableArtifactBaseline=CLEAN projectTreePresent=1 buildOutputDllState=FINGERPRINT_MATCH tempDirPresent=0 tempDllState=MISSING tempObjectCount=-1 tempIncompleteMarkerCount=-1 tempPchPresent=-1 tempPdbPresent=-1 fassertEnabled=0 debugDefine=0 ndebugDefine=1 msvcVersion=1310 msvcFullVersion=13103077 internalProfilerCompiled=0 tscProfilerCompiled=0 profileAIAutoPlayCompiled=0 reproTestCompiled=0
GAME_RECORD_EXE_CONTEXT seq=20 moduleFound=1 fileReadable=1 fileSizeBytes=12594192 exeFingerprint=FNV1A64:98123F43E2DC14E6 exeLastWriteUtc=20250328T141834.588Z peTimestampRaw=1401330529 peTimestampUtc=20140529T022849Z resourceFileVersion=3.1.9.0 resourceProductVersion=3.1.9.0
GAME_RECORD_INSTALL_CONTEXT seq=21 systemContextLevel=2 distributionHint=STEAM steamAppId=8800 steamBuildId=283175 steamBetaKey=- absoluteExePath=- absoluteModPath=-
GAME_RECORD_RNG_CHECKPOINT seq=246 turn=0 reason=SAVE_LOADED rngFingerprintSchema=1 mapSessionStartState=2502007618 mapIntervalStartState=2502007618 mapState=2502007618 mapIntervalCalls=0 mapSessionCalls=0 mapIntervalNullMessageCalls=0 mapSessionNullMessageCalls=0 mapIntervalExternalCalls=0 mapSessionExternalCalls=0 mapIntervalDeterministicRangeCalls=0 mapSessionDeterministicRangeCalls=0 mapIntervalSeedSets=0 mapSessionSeedSets=0 mapIntervalStreamFingerprint=FNV1A32:811C9DC5 mapSessionStreamFingerprint=FNV1A64:CBF29CE484222325 mapIntervalCallFingerprint=FNV1A32:811C9DC5 mapSessionCallFingerprint=FNV1A64:CBF29CE484222325 syncSessionStartState=4091165095 syncIntervalStartState=4091165095 syncState=4091165095 syncIntervalCalls=0 syncSessionCalls=0 syncIntervalNullMessageCalls=0 syncSessionNullMessageCalls=0 syncIntervalExternalCalls=0 syncSessionExternalCalls=0 syncIntervalDeterministicRangeCalls=0 syncSessionDeterministicRangeCalls=0 syncIntervalSeedSets=0 syncSessionSeedSets=0 syncIntervalStreamFingerprint=FNV1A32:811C9DC5 syncSessionStreamFingerprint=FNV1A64:CBF29CE484222325 syncIntervalCallFingerprint=FNV1A32:811C9DC5 syncSessionCallFingerprint=FNV1A64:CBF29CE484222325
GAME_RECORD_STATE_CHECKPOINT seq=247 turn=0 reason=SAVE_LOADED coverage=CORE everAliveTeamCount=17 everAlivePlayerCount=17 cityCount=0 unitCount=42 groupCount=42 plotCount=10080 dealCount=0 gameFingerprint=FNV1A64:4E7C5025C618AFDE teamsFingerprint=FNV1A64:3CADD15644E68454 playersFingerprint=FNV1A64:4C5D16D5DEFE6F73 citiesFingerprint=FNV1A64:CBF29CE484222325 unitsFingerprint=FNV1A64:C5CAF94F860BD9D0 groupsFingerprint=FNV1A64:C637269CD6E942DE plotsFingerprint=FNV1A64:A0F621DB4D4DD7BC dealsFingerprint=FNV1A64:CBF29CE484222325 combinedFingerprint=FNV1A64:11A21E074BE40F3A computeMilliseconds=0
```

The same run also shows nonzero RNG activity and state fingerprints at a completed-turn checkpoint:

```log
GAME_RECORD_RNG_CHECKPOINT seq=7380 turn=10 reason=END_GAME_TURN rngFingerprintSchema=1 mapSessionStartState=2502007618 mapIntervalStartState=2502007618 mapState=2502007618 mapIntervalCalls=0 mapSessionCalls=0 mapIntervalNullMessageCalls=0 mapSessionNullMessageCalls=0 mapIntervalExternalCalls=0 mapSessionExternalCalls=0 mapIntervalDeterministicRangeCalls=0 mapSessionDeterministicRangeCalls=0 mapIntervalSeedSets=0 mapSessionSeedSets=0 mapIntervalStreamFingerprint=FNV1A32:811C9DC5 mapSessionStreamFingerprint=FNV1A64:CBF29CE484222325 mapIntervalCallFingerprint=FNV1A32:811C9DC5 mapSessionCallFingerprint=FNV1A64:CBF29CE484222325 syncSessionStartState=4091165095 syncIntervalStartState=788291066 syncState=2316915261 syncIntervalCalls=4519 syncSessionCalls=40386 syncIntervalNullMessageCalls=2332 syncSessionNullMessageCalls=19396 syncIntervalExternalCalls=0 syncSessionExternalCalls=0 syncIntervalDeterministicRangeCalls=20 syncSessionDeterministicRangeCalls=184 syncIntervalSeedSets=0 syncSessionSeedSets=0 syncIntervalStreamFingerprint=FNV1A32:8E08F1C5 syncSessionStreamFingerprint=FNV1A64:3A5EB75114BFE6E4 syncIntervalCallFingerprint=FNV1A32:D7FEE1F4 syncSessionCallFingerprint=FNV1A64:31EA6E9A05712E10
GAME_RECORD_STATE_CHECKPOINT seq=7381 turn=10 reason=END_GAME_TURN coverage=CORE everAliveTeamCount=17 everAlivePlayerCount=17 cityCount=16 unitCount=65 groupCount=65 plotCount=10080 dealCount=0 gameFingerprint=FNV1A64:FFF17DFCB573519E teamsFingerprint=FNV1A64:1D9DB91FF8CA0461 playersFingerprint=FNV1A64:4D0B998B1980031A citiesFingerprint=FNV1A64:17F0B852EEE852A7 unitsFingerprint=FNV1A64:9A5A027DEB88809E groupsFingerprint=FNV1A64:022A98FB6AA6118E plotsFingerprint=FNV1A64:488C3B3B792646CD dealsFingerprint=FNV1A64:CBF29CE484222325 combinedFingerprint=FNV1A64:F4B69AD13547052C computeMilliseconds=1
```

#### SASGameRecord gameplay example

These are **35 selected, unchanged rows** from `SASGameRecord_20261025T180717Z_load1.log` (recorder revision 172). Gaps in `seq` omit repeated detail rows while preserving the selected rows' order.

They follow player 2 at turn 20 through resources, AI priorities, economy/production, diplomacy and unit composition, including typed parked-production fields; this is actual output, not a reconstructed Before/After comparison.

```log
GAME_RECORD_PLAYER seq=10154 turn=20 player=2 team=2 civ=CIVILIZATION_MAYA leader=LEADER_PACAL isHuman=0 humanSlot=0 currentlyHumanControlled=0 autoplayControlled=0 rank=4 deltaValid=1 score=64 scoreDelta=+22 cities=1 citiesDelta=+0 pop=2 popDelta=+1 land=18 landDelta=+0 units=3 unitsDelta=+1 combatUnits=2 combatUnitsDelta=+1 militarySupportUnits=2 militarySupportUnitsDelta=+1 power=12 powerDelta=+5 gold=0 goldDelta=+0 gpt=0 gptDelta=+0 financialStrike=0 cumulativeStrikeTurns=0 researchRate=14 researchRateDelta=+3 researchPercent=100 currentResearch=TECH_AGRICULTURE researchOverflow=0 noResearchAvailable=0 researchTurns=2 era=ERA_ANCIENT stateReligion=- techScorePercent=100 combatXP=0 greatPeopleCreated=0 greatGeneralsCreated=0 greatGeneralThreshold=24 goldenAgeTurns=0 loggedGoldenAgeTurns=0 anarchyTurns=0 loggedAnarchyTurns=0 revolutionTimer=0 conversionTimer=0 wars=-
GAME_RECORD_PLAYER_HISTORY seq=10155 turn=20 player=2 deltaValid=1 historyScore=64 historyScoreDelta=+22 historyEconomy=11 historyEconomyDelta=+0 historyIndustry=5 historyIndustryDelta=+3 historyAgriculture=7 historyAgricultureDelta=+3 historyPower=11 historyPowerDelta=+6 historyCulture=37 historyCultureDelta=+20 historyEspionage=73 historyEspionageDelta=+40
GAME_RECORD_POLLUTION seq=10156 turn=20 player=2 total=20 buildings=0 bonuses=0 power=0 population=20
GAME_RECORD_BONUSES seq=10157 turn=20 player=2 detailRows=1 deltaValid=1 bonusTypes=1 bonusTypesDelta=+1 bonusInstances=1 bonusInstancesDelta=+1 imports=0 importsDelta=+0 exports=0 exportsDelta=+0
GAME_RECORD_BONUSES_AVAILABLE seq=10158 turn=20 player=2 available=BONUS_ELEPHANTS:1
GAME_RECORD_BONUSES_TRADEABLE seq=10159 turn=20 player=2 tradeable=BONUS_ELEPHANTS:1
GAME_RECORD_BONUSES_IMPORT_EXPORT seq=10160 turn=20 player=2 imported=- exported=-
GAME_RECORD_BONUS_DETAIL seq=10161 turn=20 player=2 bonusId=25 bonus=BONUS_ELEPHANTS available=1 tradeable=1 imported=0 exported=0
GAME_RECORD_AI_STRATEGIES seq=10162 turn=20 player=2 team=2 strategies=AI_STRATEGY_GET_BETTER_UNITS
GAME_RECORD_AI_TARGET_CITIES seq=10163 turn=20 player=2 team=2 timer=0 targetCount=0 targets=-
GAME_RECORD_AI_VICTORY_STAGES seq=10164 turn=20 player=2 team=2 playerMaxStage=0 teamMaxStage=0 culture=0 space=0 conquest=0 domination=0 diplomacy=0
GAME_RECORD_AI_MILITARY_PRODUCTION seq=10165 turn=20 player=2 personalityBuildProb=34 unitSpending=0 maxUnitSpendingNoArea=83 spendingGapNoArea=83 aggressiveAI=1 financialTrouble=0 economyFocus=0 getBetterUnits=1 focusWar=0 dagger=0 crush=0 alert1=0 alert2=0 turtle=0 lastStand=0 finalWar=0 fastMovers=0 landBlitz=0 airBlitz=0 nuclear=0 totalWarPlans=0 preparingTotalWarPlans=0 sneakPreparing=0 sneakReady=0
GAME_RECORD_POLICIES seq=10166 turn=20 player=2 civicEntries=5 religionEntries=0 corporationEntries=0 civics=CIVICOPTION_GOVERNMENT:CIVIC_DESPOTISM,CIVICOPTION_LEGAL:CIVIC_BARBARISM,CIVICOPTION_LABOR:CIVIC_TRIBALISM,CIVICOPTION_ECONOMY:CIVIC_DECENTRALIZATION,CIVICOPTION_RELIGION:CIVIC_PREHISTORIC_RELIGION stateReligion=- cityReligions=- cityCorporations=- playerExtraHealth=0 playerExtraHappiness=0 extraHealthSources=- extraHappinessSources=-
GAME_RECORD_POLICY_CIVIC seq=10167 turn=20 player=2 optionId=0 option=CIVICOPTION_GOVERNMENT civicId=0 civic=CIVIC_DESPOTISM
GAME_RECORD_ECONOMY seq=10172 turn=20 player=2 commerceEntries=4 gold=0 goldRate=0 goldCommerceRate=0 dealGoldPerTurn=0 inflatedCosts=0 unitCost=0 unitSupply=0 cityMaintenance=0 civicUpkeep=0 inflationRate=0 totalCommerce=11 sliders=COMMERCE_GOLD:0,COMMERCE_RESEARCH:100,COMMERCE_CULTURE:0,COMMERCE_ESPIONAGE:0 commerceTypeRates=COMMERCE_GOLD:0,COMMERCE_RESEARCH:12,COMMERCE_CULTURE:2,COMMERCE_ESPIONAGE:4 flexible=COMMERCE_GOLD:1,COMMERCE_RESEARCH:1,COMMERCE_CULTURE:0,COMMERCE_ESPIONAGE:0 currentResearch=TECH_AGRICULTURE currentResearchTeamProgress=50 currentResearchCost=70 researchRate=14 researchOverflow=0 noResearchAvailable=0 researchTurns=2
GAME_RECORD_ECONOMY_COMMERCE seq=10173 turn=20 player=2 commerceId=0 commerce=COMMERCE_GOLD percent=0 rate=0 flexible=1
GAME_RECORD_PRODUCTION_PIPELINE seq=10177 turn=20 player=2 activeFiniteItems=1 activeStored=45 activeNeeded=92 activeProcesses=0 activeFoodProductionUnits=1 activeFoodProductionUnitStored=45 parkedItems=1 parkedStored=4 parkedNeeded=22 citiesWithParked=1 maxParkedItemsOneCity=1 maxParkedStoredOneCity=4 parkedHalfComplete=0 parkedThreeQuarterComplete=0 parkedUnitItems=1 parkedUnitStored=4 parkedFoodProductionUnitItems=0 parkedFoodProductionUnitStored=0 parkedBuildingItems=0 parkedBuildingStored=0 parkedWonderItems=0 parkedWonderStored=0 parkedProjectItems=0 parkedProjectStored=0 inactivityCounterItems=1 accumulatedInactiveTurnsTotal=5 maxAccumulatedInactiveTurns=5
GAME_RECORD_PRODUCTION_PARKED seq=10178 turn=20 player=2 items=8192:UNIT:UNIT_ARCHER:4/22@5
GAME_RECORD_PRODUCTION_PARKED_ITEM seq=10179 turn=20 player=2 index=0 cityId=8192 kind=UNIT target=UNIT_ARCHER stored=4 needed=22 inactiveTurnsValid=1 inactiveTurns=5
GAME_RECORD_STATISTICS seq=10180 turn=20 player=2 currentCities=1 persistentCitiesBuilt=1 persistentCitiesRazed=0 loggedCitiesAcquired=0 loggedCitiesLost=0 loggedCitiesConquered=0 loggedCitiesLostByConquest=0 loggedCitiesTradedIn=0 loggedCitiesTradedOut=0 loggedCityNet=+0 loggedBattleWins=2 loggedBattleLosses=0 loggedCityBattleWins=0 loggedCityBattleLosses=0 loggedBattleNet=+2 loggedWithdrawals=0 loggedEnemyWithdrawals=0 loggedCombatLimitAttacks=0 loggedCombatLimitDefenses=0 loggedLuckEligibleBattles=0 loggedLuckEligibleWins=0 loggedExpectedWinsX1000=0 loggedLuckDeltaX1000=+0 loggedUpsetWins=0 loggedUpsetLosses=0 loggedLowestOddsWinPermille=-1 loggedHighestOddsLossPermille=-1 loggedXpGained=6 loggedCombatXpGained=1 loggedNonCombatXpGained=5 loggedXpPreventedByCap=2 loggedXpLostAdjustments=0 loggedPromotionsChosen=2 loggedLeaderPromotionApplications=0 loggedEnemyXpDestroyed=0 loggedOwnXpLost=0
GAME_RECORD_ESPIONAGE seq=10181 turn=20 player=2 team=2 rivalTeamEntries=15 playerTargetEntries=0 espionageRate=4 espionagePercent=0 teamEP=84 unspentEP=0 weights=- spending=- pointsAgainst=- modifiers=0:+98,1:+98,3:+97,4:+100,5:+97,6:+100,7:+98,8:+107,9:+99,10:+99,11:+100,12:+100,13:+105,14:+108,15:+100 bigEspionage=0 espionageEconomy=0 spies=0 greatSpies=0 spiesInForeignTerritory=0 spiesInForeignCities=0 stationarySpies=0 maxFortifyTurns=0 spyTargets=- attackSpyIntent=0 spyMissionTargets=- reconSpyIntent=0 guardSpyIntent=0
GAME_RECORD_ESPIONAGE_TEAM seq=10182 turn=20 player=2 team=2 targetTeam=0 met=0 weight=0 spendingValid=0 spending=-1 pointsAgainst=0 modifier=98
GAME_RECORD_ESPIONAGE_DELTAS seq=10197 turn=20 player=2 deltaValid=1 espionageRateDelta=+0 espionagePercentDelta=+0 teamEPDelta=+40 unspentEPDelta=+0
GAME_RECORD_DEMOGRAPHICS seq=10198 turn=20 player=2 rank=4 score=64 population=2 land=18 food=8 production=6 commerce=11 research=12 culture=2 espionage=4 goldRate=0 power=12
GAME_RECORD_DEMOGRAPHICS_DELTAS seq=10199 turn=20 player=2 deltaValid=1 scoreDelta=+22 populationDelta=+1 landDelta=+0 foodDelta=+4 productionDelta=+4 commerceDelta=+1 researchDelta=+1 cultureDelta=+0 espionageDelta=+0 goldRateDelta=+0 powerDelta=+5
GAME_RECORD_ATTITUDES seq=10200 turn=20 player=2 towardValues=-
GAME_RECORD_DIPLO_STATUS seq=10201 turn=20 player=2 team=2 worstEnemyTeam=-1 worstEnemyPlayers=- worstEnemyOfTeams=- atWar=- openBorders=- defensivePacts=- forcePeace=- canContact=- canContactWilling=- wontTalkTo=- wontTalkFrom=-
GAME_RECORD_UNIT_POSTURE seq=10202 turn=20 player=2 total=3 military=2 landMilitary=2 seaMilitary=0 airMilitary=0 attackAir=0 defenseAir=0 carrierAir=0 missileAir=0 icbm=0 carrierSea=0 missileCarrierSea=0 airCargo=0 carrierAirCargo=0 missileCargo=0 nukes=0 blockadingUnits=0 workers=1 settlers=0 recon=1 cityDefenders=1 fieldArmy=1 ownTerritory=2 enemyTerritory=0 neutralTerritory=1 unitsInCities=1 enemyUnitsInTerritory=0 totalXP=6 avgXpX100=200 maxXP=6 promotionReady=0 level2Plus=1 level4Plus=0 level6Plus=0 promotionInstances=3 militaryXP=6 avgMilitaryXpX100=300 maxMilitaryXP=6 avgMilitaryLevelX100=200 maxMilitaryLevel=3 militaryPromotionReady=0 greatGeneralLedMilitary=0 militaryCostedUnits=2 militaryXmlProductionCost=43 militaryProductionNeeded=38 woundedMilitary=1 militaryHealthMeasured=2 avgMilitaryHealthX100=6800 minMilitaryHealthX100=3600 maxMilitaryHealthX100=10000 militaryHealthFull=1 militaryHealthHigh=0 militaryHealthMedium=1 militaryHealthLow=0 militaryPromotionInstances=3
GAME_RECORD_UNIT_POSTURE_DELTAS seq=10203 turn=20 player=2 deltaValid=1 totalDelta=+1 militaryDelta=+1 workersDelta=+0 settlersDelta=+0 fieldArmyDelta=+0 cityDefendersDelta=+1 enemyUnitsInTerritoryDelta=+0 totalXPDelta=+6 promotionReadyDelta=+0
GAME_RECORD_UNIT_COMPOSITION seq=10204 turn=20 player=2 unitTypes=UNIT_MAYA_QUICK_WORKER:1,UNIT_WARRIOR:1,UNIT_ARCHER:1 unitAI=UNITAI_WORKER:1,UNITAI_CITY_DEFENSE:1,UNITAI_EXPLORE:1 unitCombatTotal=2 unitCombat=UNITCOMBAT_ARCHER_BOW_SHORT:1,UNITCOMBAT_MELEE_SHOCK:1 unitCombatPercentX100=UNITCOMBAT_ARCHER_BOW_SHORT:5000,UNITCOMBAT_MELEE_SHOCK:5000
GAME_RECORD_NAVAL_ASSAULT_POSTURE seq=10205 turn=20 player=2 assaultTransports=0 assaultTransportsTraining=0 cargoCapacity=0 loadedCargo=0 cargoUtilizationPercentX100=-1 openOceanTransports=0 openOceanCapacity=0 openOceanLoadedCargo=0 openOceanGroups=0 transportsEmpty=0 transportsPartial=0 transportsFull=0 damagedTransports=0 assaultGroups=0 groupsEmpty=0 groupsPartial=0 groupsFull=0 groupsAtBase=0 groupsEmptyAtBase=0 groupsEmptyNoMissionAIAtBase=0 groupsLoadedAwayFromBase=0 groupsNoMissionAI=0 groupsAssault=0 groupsPickup=0 groupsReinforce=0 groupsOtherMissionAI=0 groupsMissionQueueNonempty=0 groupsHealing=0 groupsWithSeaCombatSupport=0 groupedSeaCombatSupportUnits=0 loadedCargoCanAttack=0 loadedCargoCannotAttack=0 transportUnitTypes=- cargoUnitTypes=- cargoUnitAI=- missionTargets=-
GAME_RECORD_UNIT_PROMOTIONS seq=10206 turn=20 player=2 promotions=PROMOTION_COMBAT1:1,PROMOTION_MEDIC1:1,PROMOTION_RETREAT1:1 militaryPromotions=PROMOTION_COMBAT1:1,PROMOTION_MEDIC1:1,PROMOTION_RETREAT1:1
GAME_RECORD_BARBARIAN_PRESSURE seq=10207 turn=20 player=2 team=2 human=0 barbarianCreationEra=1 visibleUnits=1 visibleAnimals=1 visibleNonAnimals=0 visibleLandUnits=1 visibleSeaUnits=0 visibleUnitsInTerritory=0 visibleUnitsWithin3OfCity=0 visibleUnitsWithin6OfCity=1 nearestVisibleUnitDistance=4 nearestVisibleUnitId=262170 nearestVisibleUnit=UNIT_BEAR nearestVisibleUnitX=23 nearestVisibleUnitY=18 revealedCities=0 visibleCities=0 knownCities=0 nearestKnownCityDistance=-1 nearestKnownCityId=-1 nearestKnownCityX=-1 nearestKnownCityY=-1 cityAttackRoleUnits=0 exploreRoleUnits=1 exploreMissionGroups=1 guardCityMissionGroups=1 citySiteGuardGroups=0 citySiteGuardGroupsAtTarget=0 citySiteAdjacentGuardGroups=0 citySiteGuardTargets=- barbarianDefenseFocusAreas=0 capitalAreaBarbarianDefenseFocus=0 aiBarbarianAttackersNeeded=3
GAME_RECORD_WORKER seq=10208 turn=20 player=2 unitId=24576 unit=UNIT_MAYA_QUICK_WORKER unitAI=UNITAI_WORKER x=19 y=17 mission=MISSION_BUILD build=BUILD_COTTAGE buildTurnsLeft=2 plotOwner=2 plotTerrain=TERRAIN_GRASS plotFeature=- plotBonus=- plotImprovement=- plotRoute=- guarded=0 threatened=0
GAME_RECORD_WORKERS seq=10209 turn=20 player=2 workers=1 seaWorkers=0 idle=0 building=1 buildingImprovement=1 buildingRoute=0 moving=0 waiting=0 ownTerritory=1 enemyTerritory=0 neutralTerritory=0 guarded=0 unguarded=1 threatened=0 builds=BUILD_COTTAGE:1
```

The full example includes initial map context, city details and later gameplay history. Its captured revision is independent of the more recent session-header example above.

#### `SASGameRecord_*.log` (runtime and version context)

These complete rows come from the live 2026-10-27 `SASGameRecord_20261027T063129Z_load1.log`. They illustrate separate compiled-DLL, executable, process-limit and embedded-Python evidence; intervening rows are omitted:

```log
GAME_RECORD_RUNTIME_CONTEXT seq=9 systemContextLevel=2 win32Runtime=NATIVE_WINDOWS wineVersion=- windowsMajor=10 windowsMinor=0 windowsBuild=19045 windowsUpdateRevision=6466 windowsServicePackMajor=0 windowsServicePackMinor=0 windowsDisplayVersion="22H2" pointerBits=32 intBits=32 intMax=2147483647 processTotalVirtualBytes=4294836224 processArch=X86 nativeArch=X64 wow64=1 cpuVendor=- cpuBrand=- logicalProcessors=-1 totalPhysicalMemoryMB=-1 processPriorityClass=- processAffinityQueryAvailable=-1 processAffinityMask=- systemAffinityMask=- debuggerAttached=-1 developmentProcessScanAvailable=-1 vcExpressRunning=-1 devenvRunning=-1 msBuildRunning=-1 nmakeRunning=-1 clRunning=-1 linkRunning=-1
GAME_RECORD_DLL_CONTEXT seq=31 build=Debug-opt moduleFound=1 fileReadable=1 fileSizeBytes=14155776 dllFingerprint=FNV1A64:01E510BDF789FA31 dllLastWriteUtc=20261027T062619.916Z peTimestampRaw=1793082369 peTimestampUtc=20261027T062609Z resourceFileVersion=- resourceProductVersion=- buildEvidence=EMBEDDED buildRequest=BUILD preexistingObjectCount=0 preexistingIncompleteMarkerCount=0 preexistingPch=0 reusableArtifactBaseline=CLEAN projectTreePresent=1 buildOutputDllState=FINGERPRINT_MATCH tempDirPresent=1 tempDllState=FINGERPRINT_MATCH tempObjectCount=169 tempIncompleteMarkerCount=0 tempPchPresent=1 tempPdbPresent=1 fassertEnabled=0 debugDefine=0 ndebugDefine=1 msvcVersion=1310 msvcFullVersion=13103077 internalProfilerCompiled=0 tscProfilerCompiled=0 profileAIAutoPlayCompiled=0 reproTestCompiled=0
GAME_RECORD_EXE_CONTEXT seq=32 moduleFound=1 fileReadable=1 fileSizeBytes=12594192 exeFingerprint=FNV1A64:98123F43E2DC14E6 exeLastWriteUtc=20250328T141834.588Z peTimestampRaw=1401330529 peTimestampUtc=20140529T022849Z resourceFileVersion=3.1.9.0 resourceProductVersion=3.1.9.0 exeLargeAddressAware=1
GAME_RECORD_SESSION_SETTINGS seq=294 schema=1 turn=0 elapsed=0 event=SNAPSHOT reason=ON_LOAD source=RUNNING_INTERPRETER group=PYTHON_RUNTIME_CONTEXT count=5 values=apiVersion=1012;buildDescription=2.4.1%20%28%2365%2C%20Mar%2030%202005%2C%2009%3A13%3A57%29%20%5BMSC%20v.1310%2032%20bit%20%28Intel%29%5D;byteOrder=little;maxUnicode=65535;version=2.4.1
```

The embedded interpreter reports Python 2.4.1 in this capture; that is distinct from the standalone checker's 2.4.4 and packaging host's 3.12.3. These are captured examples, not fixed expected versions.

### BBAI

#### BBAI session header example

Selected save-load header rows from `BBAI_20261018T140808Z_load1.log`. Its source identity and Debug-opt DLL describe that captured development build, rather than the shipped Release DLL:

```log
BBAI_SAVE_LOADED processUtc=20261018T140754Z utc=20261018T140808Z logFile="BBAI_20261018T140808Z_load1.log" turn=0 elapsed=0 year=-50000 scenario=0 activePlayer=0 activeCivilization=CIVILIZATION_KOREA activeHandicap=HANDICAP_MONARCH playersDefined=16 playersAlive=16 playersEverAlive=16 humans=1
BBAI_GAME_SETTINGS mapScript=Archipelago map=120x84 landHeavy=0 navalHeavy=1 world=WORLDSIZE_HUGE climate=CLIMATE_TEMPERATE seaLevel=SEALEVEL_MEDIUM gameSpeed=GAMESPEED_NORMAL startEra=ERA_ANCIENT gameHandicap=HANDICAP_MONARCH options=GAMEOPTION_AGGRESSIVE_AI,GAMEOPTION_NO_EVENTS
BBAI_GAME_RNG mapRandState=2502007618 syncRandState=4091165095
BBAI_MOD_CONTEXT displayName="AdvCiv-SAS" folderName="AdvCiv-SAS" modPath="Mods\\AdvCiv-SAS\\"
BBAI_SOURCE_CONTEXT version="6641" commit="7cd0c44ffced52c13505d6a62d411ab4a68178e1" shortCommit="7cd0c44ffc" branch="main" commitDate="2026-10-18T13:17:52+02:00" metadataSource="git" dirty=1 dirtyTrackedCount=25 trackedCodeRulesDiffBytes=43385 trackedCodeRulesDiffFingerprint="FNV1A64:240E60008057A355" dirtyFiles="[ M] .github/workflows/README.md; [AM] .github/workflows/build/diagnostics/runtime_status.py; [ A] .github/workflows/build/repository/project_sources.py; [ M] .github/workflows/build/source/source_change_provenance.py; [M ] .github/workflows/checks-diagnostics.yml; [ M] .github/workflows/checks-repository.yml; [ A] .github/workflows/tests/repository/test_project_sources.py; [ M] .github/workflows/tests/source/test_source_change_provenance.py; [MM] AGENTS.md; [ M] Assets/CvGameCoreDLL.dll; [ M] Assets/CvGameCoreDLL.dll.build.json; [MM] Assets/XML/GlobalDefines_advciv_sas.xml; [MM] CvGameCoreDLL/CvEventReporter.cpp; [MM] CvGameCoreDLL/CvGame.cpp; [MM] CvGameCoreDLL/CvGameCoreUtils.cpp; [MM] CvGameCoreDLL/CvGameCoreUtils.h; [ M] CvGameCoreDLL/Project/AdvCiv.vcxproj; [ A] CvGameCoreDLL/SASRuntimeStatus.cpp; [ A] CvGameCoreDLL/SASRuntimeStatusReasons.h; [ M] README.md; [MM] _1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md; [ M] _1_AdvCiv-SAS/Docs/README_SASGameRecord_Revisions.md; [ M] tests/README.md; [ M] tests/diagnostics/run_writer_tests.py; [ M] tests/diagnostics/sas_diagnostic_writer_harness.cpp"
BBAI_DLL_CONTEXT build=Debug-opt moduleFound=1 fileReadable=1 fileSizeBytes=13946880 dllFingerprint=FNV1A64:5B589A8B39B86325 dllLastWriteUtc=20261018T140725.670Z peTimestampRaw=1792332436 peTimestampUtc=20261018T140716Z resourceFileVersion=- resourceProductVersion=- buildEvidence=EMBEDDED buildRequest=BUILD preexistingObjectCount=0 preexistingIncompleteMarkerCount=0 preexistingPch=0 reusableArtifactBaseline=CLEAN projectTreePresent=1 buildOutputDllState=FINGERPRINT_MATCH tempDirPresent=1 tempDllState=FINGERPRINT_MATCH tempObjectCount=169 tempIncompleteMarkerCount=0 tempPchPresent=1 tempPdbPresent=1 fassertEnabled=0 debugDefine=0 ndebugDefine=1 msvcVersion=1310 msvcFullVersion=13103077 internalProfilerCompiled=0 tscProfilerCompiled=0 profileAIAutoPlayCompiled=0 reproTestCompiled=0
```

From practical 6680 onward, the shared BBAI source-context header receives the same branch relation and staged/unstaged aggregate fields through the central resolver. BBAI also emits the same one-time `BBAI_SOURCE_DIFF_SUMMARY` / `BBAI_SOURCE_DIFF_FILE` path-layer evidence as SGR, so an AI-only diagnostic run remains self-contained without embedding raw patches.

This BBAI capture predates those fields; the SGR header above illustrates the shared resolver's current output.

#### Categories and inherited Settler logging

Base AdvCiv's `BBAILog.h` used compile-time `LOG_AI` / `LOG_FOUND_VALUE` switches and fixed category levels. Its `logBBAI` wrote `BBAI.log`, or `BBAI<player>.log` in network multiplayer. SAS exposes the settings through XML and caches them after define loading, so diagnostic levels can be changed before launch without rebuilding the DLL.

Enable `SAS_BBAI_LOG_ON` and select the relevant category levels. `SAS_BBAI_LOG_USE_TIMESTAMPED_FILENAME` chooses new/load session files instead of fixed-name appending; ordinary diagnostic categories ship disabled. The XML comments describe exact levels and supporting controls; the table below is a subject index, not a claim that every category emits the same detail at each level.

These controls all select categories within the same BBAI output, including the UWAI controls below; they do not create separate files such as `Settler.log` or `MilitaryAnalyst.log`.

| Current control | Diagnostic subject / search examples |
| --- | --- |
| `SAS_BBAI_PLAYER_LOG`, `SAS_BBAI_TEAM_LOG`, `SAS_BBAI_WAR_LOG` | General player/team decisions and dedicated war-plan/target decisions. |
| `SAS_BBAI_CITY_LOG`, `SAS_BBAI_PROD_NO_TARGET_LOG` | General city decisions and missing-production-target/chooser-path diagnostics. |
| `SAS_BBAI_MILIT_PROD_LOG`, `SAS_BBAI_BLDG_PROD_LOG` | Military-unit versus infrastructure opportunities and production decisions. |
| `SAS_BBAI_SPACE_PROD_LOG`, `SAS_BBAI_LIMITED_PROJECT_PROD_LOG` | Spaceship projects and one-copy non-spaceship projects. |
| `SAS_BBAI_CITIZEN_LOG`, `SAS_BBAI_CULT_LOG` | Citizen assignments and culture-victory decisions. |
| `SAS_BBAI_UNIT_LOG`, `SAS_BBAI_OVERSEAS_TRANSPORT_LOG`, `SAS_BBAI_GREAT_GENERAL_LOG` | General unit behavior, transport/cargo decisions and Great General actions. |
| `SAS_BBAI_SETTLER_LOG` | Movement, target decisions, founding, parking and escorts; examples include `SETTLER_MISSION_DECISION`, `SETTLER_PARKED` and `SETTLER_CITY_ESCORT_POOL`. |
| `SAS_BBAI_FOUND_LOG` | City-site scoring and selection; examples include `FOUND_SITE_SELECTED` and `FOUND_SITE_STORED`. |
| `SAS_BBAI_EVACUATION_LOG`, `SAS_BBAI_WORKER_LOG`, `SAS_BBAI_WORKER_SEA_LOG` | Retreat/evacuation, land Workers and Work Boats. |
| `SAS_BBAI_MAP_LOG`, `SAS_BBAI_DEAL_CANCEL_LOG`, `SAS_BBAI_BONUS_LOG` | Map/start context, deal cancellation and resource valuation/trade. |

The inherited `CvUnitAI::AI_found` / `AI_foundFollow` path already logged messages such as `Settler heading for site %d, %d` and `Settler founding at plot %d, %d (follow)` under `gUnitLogLevel >= 2`. SAS separates Settler diagnostics from general UNIT output and adds named fields for decisions, reasons and safety/escort context; FOUND separately follows the scoring used to choose sites.

`ReproTest.cpp` is another BBAI/message-control producer rather than a separate filename family: when compiled with `ENABLE_REPRO_TEST`, it brackets the replay comparison with `ReproTest: start`, `ReproTest: reloading` and `ReproTest: done` in enabled BBAI output, and also uses `messageControlLog` when engine logging is active.

Those quoted Settler strings are source format templates, not captured game rows. The split matters in practice: enabling FOUND alone does not request the whole Settler movement/escort trace, and enabling SETTLER does not request full per-plot found-value calculations.

#### Settler Before/After: selecting a movement target

This comparison reconstructs the **source formats**, not a recorded Settler trip: the checked captures did not supply a matching movement row. Both sides describe moving toward a selected founding site; `%d` / `%S` retain the actual source placeholders instead of inventing a unit, turn or coordinates.

Before (`CvUnitAI::AI_found`, base AdvCiv; general UNIT level 2+):

```log
    Settler heading for site %d, %d
```

After (SAS `SAS_logSettlerMissionDecision`, SETTLER level 2+; action/reason resolved from the `AI_found` call):

```log
SETTLER_MISSION_DECISION turn=%d player=%d %S action=PUSH_MOVE_TO_FOUND reason=AI_FOUND_MOVE unitId=%d x=%d y=%d target=(%d,%d) endTurn=(%d,%d) targetOwner=%d targetFoundValue=%d pathTurns=%d groupId=%d groupUnits=%d groupSettlers=%d groupDefenders=%d groupHealthyDefenders=%d groupCanDefend=%d plotDanger=%d targetDanger=%d missionAI=%d
```

The old line identifies only the destination. The SAS row also identifies the player/unit, turn, current and end-turn positions, selected-site value, path length, group/escort composition, danger and mission context, so it can explain how the Settler is reaching that target. Separate `SETTLER_PARKED` and `SETTLER_CITY_ESCORT_POOL` rows expose waiting and escort availability.

#### UWAI diagnostics: standalone AdvCiv reports vs current BBAI records

Base AdvCiv's `UWAIReport.cpp` wrote `uwai<turn>.log` through the EXE logger, with Textile-oriented headings and a conversion note. `UWAIAgent.cpp` selected report turns through `REPORT_INTERVAL` or a forced report, while utility thresholds selected additional detailed evaluation output; `DISABLE_UWAI_REPORT` was a compile-time suppression option.

SAS merged these formerly independent UWAI diagnostics into BBAI and retired `UWAIReport.cpp` / `UWAIReport.h`, so war analysis uses the same session files, XML category controls and live-readable sink as other AI decision traces. Caller gates also avoid the disabled-report argument/setup work described in KI#505.3.

The war-planning subsystems now write directly to BBAI under the following five controls; these select portions of BBAI output, not separate `MilitaryAnalyst.log`, `InvasionGraph.log` or other per-class files:

| Current control | Explicit source / responsibility | Search examples in BBAI |
| --- | --- | --- |
| `SAS_BBAI_UWAI_AGENT_LOG` | `UWAIAgent.cpp`: top-level team war planning and negotiation flow. | `UWAI_AGENT_` |
| `SAS_BBAI_UWAI_MILIT_ANALYST_LOG` | `MilitaryAnalyst.cpp`: scenario participants, phases and projected war/capitulation/elimination outcomes. | `UWAI_MILITARY_ANALYSIS_` |
| `SAS_BBAI_UWAI_INVASION_GRAPH_LOG` | `InvasionGraph.cpp`: invasion targets, deployment, clashes and conquest simulation. | `UWAI_INVASION_` |
| `SAS_BBAI_UWAI_ARMAMENT_FORECAST_LOG` | `ArmamentForecast.cpp`: predicted military production, upgrades and power increases. | `UWAI_ARMAMENT_` |
| `SAS_BBAI_UWAI_WAR_UTILITY_LOG` | `WarEvaluator.cpp` and `WarUtilityAspect.cpp`: war/peace scenario totals and individual utility contributions. | `UWAI_WAR_` |

Level 1 selects important outcomes, with higher levels exposing more calculation context where implemented; the Agent and Military Analyst currently have the same detail at levels 2 and 3. Caller gates skip disabled diagnostic argument/setup work; shared nested mute state keeps selected internal hypothetical passes silent without changing gameplay calculations.

At InvasionGraph level 3, missing representatives are visible without using assertions as diagnostics; see [KI#537.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-537.2).

- `UWAI_INVASION_GRAPH_TYPICAL_UNIT` records `unit=NONE` with the modeled player, branch and current branch unit/power totals.
- For Army/Home Guard, `UWAI_INVASION_GRAPH_TRAINABILITY_CONTEXT` adds the actual capital, capital-network bonuses and full-combat land unit-type lists/counts: player-level eligibility versus full capital trainability. It runs once per node detail report rather than per combat step; these counts are distinct from UWAI's representative-selection filters.

See [KI#505.3](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-505.3) for the investigation and conversion rationale, and the [Main Changes Guide's BBAI section](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md#bbai-log) for diagnostic behavior and controls. Historical `uwai<turn>.log` files belong to the old report path; absence of those files in current SAS is expected.

##### UWAI Before/After: separate prose report to shared BBAI records

**After** consists of six real rows selected in order from `BBAI_20261018T080928Z_load1.log`, lines 29319–29339; intervening rows are omitted. The surrounding captured team-member row identifies player 2 as Lincoln.

**Before** reconstructs the corresponding base AdvCiv `MilitaryAnalyst.cpp`, `InvasionGraph.cpp` and `ArmamentForecast.cpp` message formats using the same captured name/values.

This is a layout comparison, not a claim that base AdvCiv replayed this SAS game; its default hardcoded `bLOG_AI=false` also muted AI-player armament forecasts, so those old-style rows are shown as they would read when enabled.

Before (`uwai21.log`, reconstructed old formats):

```log
Military analysis from the pov of Lincoln
Constructing invasion graph
(no civs are currently at war)
Armament forecast for *Lincoln*
Production per turn: 3
Total production for build-up: 5 hammers
```

After (captured SAS BBAI rows):

```log
UWAI_MILITARY_ANALYSIS_BEGIN turn=21 agentPlayer=2 agentTeam=2 targetTeam=13 scenario=WAR
UWAI_INVASION_GRAPH_BEGIN turn=21 agentPlayer=2 scenario=WAR warPartyCount=0
UWAI_INVASION_GRAPH_NO_WAR_PARTIES turn=21 agentPlayer=2 scenario=WAR
UWAI_ARMAMENT_FORECAST_BEGIN turn=21 analystPlayer=2 player=2 targetTeam=13 scenario=WAR horizon=4
UWAI_ARMAMENT_FORECAST_PRODUCTION_INPUTS turn=21 player=2 baseHammersPerTurn=3 productionPortionPercent=100 effectiveHammersPerTurn=3 upgradeHammers=0 upgradingDisabled=0
UWAI_ARMAMENT_FORECAST_TOTAL_PRODUCTION turn=21 player=2 hammers=5
```

The SAS rows retain the analysis/forecast values and make turn, analyst, player, target team and war/peace scenario explicit at the relevant boundary. They can be searched alongside other BBAI categories without opening another per-turn report or converting Textile; more detailed context remains controlled by each subsystem's XML level.

## Runtime observations and DLL build reports

### Runtime status and history

`SASRuntimeStatus.json` gives the latest observation; `SASRuntimeHistory_*.jsonl` preserves timed game/session activity, and `SASRuntimeExit_*.json` records the externally observed process exit.

The external observer uses Windows PowerShell and .NET Framework independently of the VC2003 game DLL. Its receipt records the actual PowerShell/CLR versions, Framework release and process architecture in `environment`, plus C# listener compilation result/duration in `listenerCompilation`. These observations are not established minimum requirements.

See the [observer environment and tests](/tests/README.md#runtime-exit-observer) for version/architecture details and failure limits.

Enabled runtime diagnostics start a hidden Windows observer so exit evidence can survive a crash or an interrupted current-status rewrite. This complements the existing close-request and orderly-shutdown hooks; it does not diagnose a crash or make Python/XML live editing safe.

Starting PowerShell/.NET and compiling the C# listener adds startup CPU, disk and memory work when runtime diagnostics are enabled. The native launcher does not wait for listener initialization, but the external process can still compete for system resources.

The exit/dialog observer and optional source watcher run in separate PowerShell processes, not inside Civ4; the compiled C# listener is loaded into the external observer. Their allocations therefore do not consume Civ4's own virtual-address-space allowance. They still share the computer's physical RAM, CPU and disk resources, and do not increase Civ4's address-space limit.

Around the watcher's introduction, the user noticed a brief flicker/pause after the XML loading bar filled and disappeared, before the main menu appeared. Observer startup is a possible contributor, not an established cause; its contribution was not measured. Other initialization and enabled diagnostics may also contribute.

`SAS_RUNTIME_STATUS_ON=0` prevents the watcher from starting, so its startup/compilation work is absent. No controlled on/off timing comparison was performed; Civ4's separate `LoggingEnabled` setting does not govern this observer.

For this capture, the user deliberately edited Python code while Civ4 was running, including deleting functions and adding/removing blank lines, to provoke a failure. Python errors and a Microsoft Visual C++ Runtime termination dialog appeared; the observer then recorded process exit code `3`. This test did not use an RI-style safer Python-reload implementation.

This illustrates why exit observation lives outside Civ4: its normal runtime hooks may not execute after a failure. The same mechanism can record termination following native DLL/EXE failures, including AI-code crashes, while the observer is attached; it does not identify the faulty function or make live editing safe.

The complete records below belong to that same run. JSON whitespace is normalized for readability; field values are unchanged.

#### `SASRuntimeStatus.json` (current status)

Complete `SASRuntimeStatus.json`, including the last in-process state and the later external exit observation:

```json
{
  "revision": 10,
  "dllIdentity": {
    "buildConfiguration": "Debug-opt",
    "moduleFound": 1,
    "fileReadable": 1,
    "fileSizeBytes": 14147584,
    "fingerprint": "FNV1A64:86D151B7A9F327B2",
    "lastWriteUtc": "20261026T125633.496Z",
    "peTimestampRaw": 1793019383
  },
  "sourceIdentity": {
    "version": "6687",
    "commit": "70d73a41e1bc6236cd0de33c97a64c7f4c2b0101",
    "branch": "main",
    "metadataSource": "git",
    "defaultBranch": "main",
    "defaultCommit": "70d73a41e1bc6236cd0de33c97a64c7f4c2b0101",
    "defaultVersion": "6687",
    "defaultRefSource": "LOCAL_BRANCH",
    "mergeBaseCommit": "70d73a41e1bc6236cd0de33c97a64c7f4c2b0101",
    "mergeBaseVersion": "6687",
    "branchRelation": "AT_DEFAULT",
    "currentOnlyCommits": 0,
    "defaultOnlyCommits": 0,
    "dirty": 1,
    "dirtyTrackedCount": 18,
    "sourceDiffDetailsAvailable": 1,
    "sourceDiffEntries": 3,
    "trackedCodeRulesDiffBytes": 11893,
    "trackedCodeRulesDiffFingerprint": "FNV1A64:F075A816EEA0997D",
    "stagedCodeRulesDiffBytes": 10032,
    "stagedCodeRulesDiffFingerprint": "FNV1A64:A9F7C04CAF458D78",
    "unstagedCodeRulesDiffBytes": 1860,
    "unstagedCodeRulesDiffFingerprint": "FNV1A64:BF746AEFC639D812"
  },
  "statusSerial": 9,
  "statusWriteFailures": 0,
  "processId": 24768,
  "processStartUtc": "20261026T130019.231Z",
  "dllLoadUtc": "20261026T130020Z",
  "updatedUtc": "20261026T130738.696Z",
  "processState": "EXITED",
  "exitObserverProcessId": 14584,
  "exitObserverLaunchError": 0,
  "exitObservationFilename": "SASRuntimeExit_20261026T130019.231Z_24768.json",
  "windowCloseObservationArmed": 1,
  "windowCloseRequestObservedUtc": "-",
  "gameState": "PLAYING",
  "activity": "PLAYING",
  "activitySerial": 4,
  "activityStartedUtc": "20261026T130104.045Z",
  "activityElapsedMilliseconds": 349817,
  "previousActivity": "LOADING_SAVE",
  "previousActivityStartedUtc": "20261026T130103.847Z",
  "previousActivityEndedUtc": "20261026T130104.045Z",
  "previousActivityDurationMilliseconds": 198,
  "historyFilename": "SASRuntimeHistory_20261026T130019.231Z_24768.jsonl",
  "historyAtCurrentRoot": 1,
  "historyRowsWritten": 7,
  "historyWriteFailures": 0,
  "updateReason": "PROCESS_EXIT_OBSERVED",
  "sessionSerial": 1,
  "newGameCount": 0,
  "loadCount": 1,
  "sessionKind": "LOAD_GAME",
  "sessionStartedUtc": "20261026T130103.847Z",
  "nativeReadyUtc": "20261026T130104.045Z",
  "mainMenuSceneRequestedUtc": "-",
  "mainMenuStateObservedUtc": "-",
  "loadingScreenAssetRequestedUtc": "-",
  "pythonPreGameStartUtc": "20261026T130106.083Z",
  "worldBuilderMode": 0,
  "worldBuilderScreenVisible": 0,
  "civilopediaVisible": 0,
  "civilopediaContext": "NONE",
  "civilopediaActivePlayer": -1,
  "civilopediaActiveCivilization": -1,
  "buttonPopupAwaitingInteraction": 0,
  "buttonPopupType": "NONE",
  "buttonPopupTypeId": -1,
  "buttonPopupActivePlayer": -1,
  "buttonPopupFocusedUtc": "-",
  "buttonPopupResolvedUtc": "-",
  "buttonPopupResolution": "-",
  "buttonPopupResponseButton": -1,
  "extendedGame": 0,
  "gameTurn": 290,
  "elapsedGameTurns": 290,
  "lastCompletedTurn": 289,
  "activePlayer": 0,
  "autoplayActive": 0,
  "autoplayRemainingTurns": 0,
  "mapWidth": 120,
  "mapHeight": 84,
  "worldSize": 6,
  "gameSpeed": 3,
  "scenario": 0,
  "loadedSaveCheckpointTurn": 289,
  "loadedSaveCheckpointElapsedTurn": 289,
  "loadedSaveCheckpointUtc": "20261026T062353.280Z",
  "lastInProcessUpdatedUtc": "20261026T130653.862Z",
  "exitObservation": {
    "observer": "WINDOWS_PROCESS_HANDLE",
    "recordedUtc": "20261026T130738.696Z",
    "processExitedUtc": "20261026T130738.595Z",
    "exitCode": 3,
    "exitCodeHex": "0x00000003",
    "outcome": "NONZERO_EXIT_CODE",
    "historyAppend": "WRITTEN",
    "unterminatedHistoryTail": false
  }
}
```

`processState=EXITED` and `updateReason=PROCESS_EXIT_OBSERVED` report termination; `lastInProcessUpdatedUtc`, `gameTurn` and `activity` retain the last game-owned observation. Thus `activity=PLAYING` does not mean the process is still alive.

A current-run excerpt from `SASRuntimeStatus.json` on 2026-10-27 shows the additional source-watcher fields; the complete older example above retains its exit/failure context. Only the following fields are selected here:

```json
{
  "revision": 12,
  "processId": 524,
  "processStartUtc": "20261027T062715.357Z",
  "sourceWatchEnabled": 1,
  "sourceWatchObserverProcessId": 10248,
  "sourceWatchLaunchError": 0,
  "sourceWatchStateFilename": "SASRuntimeSourceWatch_20261027T062715.357Z_524.json",
  "sourceWatchHistoryFilename": "SASRuntimeSourceChanges_20261027T062715.357Z_524.jsonl"
}
```

#### `SASRuntimeExit_*.json` (exit observation)

Complete `SASRuntimeExit_*.json` from the same process:

```json
{
  "revision": 10,
  "processId": 24768,
  "processStartUtc": "20261026T130019.231Z",
  "observerProcessId": 14584,
  "observerState": "EXITED",
  "attachedUtc": "20261026T130026.133Z",
  "recordedUtc": "20261026T130738.696Z",
  "processExitedUtc": "20261026T130738.595Z",
  "exitCode": 3,
  "exitCodeHex": "0x00000003",
  "outcome": "NONZERO_EXIT_CODE"
}
```

`observerState=EXITED` confirms that the attached process ended; the earlier `WAITING` receipt only confirms attachment.

Runtime revision 11 can also record a recognized MSVC runtime-error (`MSVC_RUNTIME_ERROR`) or Civ4 “Program Execution Problem” dump-choice dialog (`CIV4_CRASH_DUMP_PROMPT`) while `observerState` remains `WAITING`.

`dialogObserverState` reports listener availability; `failureDialog` records the latest recognized dialog, its visibility, text and first/last observation times, with `failureDialogCount` and `dialogEventsDropped` disclosing repeated or lost observations.

Dialog titles and messages are read directly from Windows window/control text (`GetWindowText` and bounded `WM_GETTEXT` calls), then written to JSON. The screenshots illustrate the corresponding windows; they are not the text source, and the captured messages were not manually transcribed.

These are observation times, not the exact fault/appearance time: an already-open dialog can be discovered after attachment. Live evidence stays in the per-run companion; the final `process_exit` history row retains its dialog summary after termination. The separate file preserves final evidence even if the current snapshot is unreadable or has been replaced by a newer game.

The following selected fields from the live 2026-10-27 `SASRuntimeExit_*.json` receipt show observer-host identity and actual listener compilation duration. `WAITING` here means the process was still alive when captured:

```json
{
  "revision": 12,
  "processId": 524,
  "observerState": "WAITING",
  "dialogObserverState": "ACTIVE",
  "environment": {
    "powershellVersion": "5.1.19041.6456",
    "powershellEdition": "Desktop",
    "clrVersion": "4.0.30319.42000",
    "frameworkRelease": 533325,
    "processBits": 32,
    "executablePath": "C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe"
  },
  "listenerCompilation": {
    "state": "SUCCEEDED",
    "elapsedMilliseconds": 165
  }
}
```

##### Notable examples: failure dialogs while Civ4 is alive

These two real captures show how different visible failure dialogs appear in `SASRuntimeExit_*.json`, before the process actually exits. They illustrate the recognized dialog forms rather than every possible crash.

Both were reproduced on **2026-10-26** by pressing **Ctrl+S in VS Code on `SevoPediaMain.py`, without changing its contents**, while Civ4 was running. AdvCiv-SAS did not include an RI-style safer Python-reload implementation for these captures; saving an unchanged file was sufficient to trigger the observed failures.

###### Crash-dump prompt

This screenshot shows the in-game dialog corresponding to `CIV4_CRASH_DUMP_PROMPT` in the JSON capture below.

<img src="/_1_AdvCiv-SAS/Images/diagnostics/0.295_SASRuntime_crash_dump_dialog.PNG" alt="0.295_SASRuntime_crash_dump_dialog.PNG" width="250"></img>

This dump-prompt capture used `[DEBUG] generatecrashdumps = 1` in the user's `CivilizationIV.ini`, matching the existing [dump-generation instructions](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README.md). SAS runtime observation does not enable that setting or request a dump.

The updated external observer was restarted while the dump-choice dialog remained open; it recorded the existing dialog without pressing any button. These timestamps therefore describe discovery, not when the failure began.

Complete `SASRuntimeExit_*.json` at that observation:

```json
{
  "revision": 11,
  "processId": 16124,
  "processStartUtc": "20261026T174016.979Z",
  "observerProcessId": 12200,
  "observerState": "WAITING",
  "attachedUtc": "20261026T174937.254Z",
  "dialogObserverState": "ACTIVE",
  "dialogObserverErrorCode": 0,
  "dialogObserverError": "",
  "dialogEventsDropped": 0,
  "failureDialogCount": 1,
  "failureDialog": {
    "kind": "CIV4_CRASH_DUMP_PROMPT",
    "visible": true,
    "firstObservedUtc": "20261026T174937.360Z",
    "observedUtc": "20261026T174937.360Z",
    "windowHandle": "0x30F56",
    "title": "Program Execution Problem",
    "text": "This program has encountered a problem and needs to be closed.  Do you wish to save a diagnostic file?"
  },
  "firstFailureDialogObservedUtc": "20261026T174937.360Z"
}
```

Here, `WAITING` means the process has not exited, while `failureDialog.visible=true` records the recognized failure dialog. This distinguishes a process blocked at the dump prompt from a game merely sitting idle; it does not establish which Python code failed or whether the file contents changed.

###### C++ Runtime Library error

This screenshot shows the in-game dialog corresponding to `MSVC_RUNTIME_ERROR` in the JSON capture below.

<img src="/_1_AdvCiv-SAS/Images/diagnostics/0.296_SASRuntime_cpp_runtime_error.PNG" alt="0.296_SASRuntime_cpp_runtime_error.PNG" width="250"></img>

In a fresh run using the same Ctrl+S reproduction, the Microsoft Visual C++ Runtime Library dialog appeared on the first attempt, and the external observer recorded it before OK was pressed. These observations do not identify the internal fault or imply that every unchanged-file save produces the same failure.

Complete `SASRuntimeExit_*.json` while the Microsoft Visual C++ Runtime Library dialog remained open:

```json
{
  "revision": 11,
  "processId": 40152,
  "processStartUtc": "20261026T175231.114Z",
  "observerProcessId": 1280,
  "observerState": "WAITING",
  "attachedUtc": "20261026T175237.808Z",
  "dialogObserverState": "ACTIVE",
  "dialogObserverErrorCode": 0,
  "dialogObserverError": "",
  "dialogEventsDropped": 0,
  "failureDialogCount": 1,
  "failureDialog": {
    "kind": "MSVC_RUNTIME_ERROR",
    "visible": true,
    "firstObservedUtc": "20261026T175309.567Z",
    "observedUtc": "20261026T175309.567Z",
    "windowHandle": "0xE0018",
    "title": "Microsoft Visual C++ Runtime Library",
    "text": "Runtime Error!\n\nProgram: ...IV Beyond the Sword\\Beyond the Sword\\Civ4BeyondSword.exe\n\n\r\nThis application has requested the Runtime to terminate it in an unusual way.\nPlease contact the application's support team for more information.\r\n"
  },
  "firstFailureDialogObservedUtc": "20261026T175309.567Z"
}
```

Both runs subsequently recorded `observerState=EXITED` and `failureDialog.visible=false`, retaining the dialog text and observation times: the dump-prompt run ended with `exitCodeHex=0xC0000005`, and the Runtime Library run with `0x00000003`.

This confirms their observed dialog-to-exit sequences, but does not establish which fault caused them or whether Normal Dump, Full Dump or No Dump was chosen.

#### `SASRuntimeHistory_*.jsonl` (session and exit history)

Selected complete records from the real histories show scheduled/interrupted autoplay, popup responses, WorldBuilder screen entry/exit, and final process exits with both observed failure-dialog types. They come from separate processes, identified by each row's `run`; this is not one continuous game.

```log
{"record":"transition","revision":8,"run":"20261026T060725.015Z_640","stateSerial":20,"intervalStarted":1,"previousState":"PLAYING","previousStartedUtc":"20261026T061509.929Z","previousEndedUtc":"20261026T061516.960Z","previousDurationMilliseconds":7032,"previousSessionSerial":6,"previousStartTurn":0,"previousRequestedAutoplayTurns":0,"recordedUtc":"20261026T061516.960Z","state":"AUTOPLAY","stateStartedUtc":"20261026T061516.960Z","stateElapsedMilliseconds":0,"sessionSerial":6,"gameTurn":0,"autoplayRemainingTurns":251,"reason":"AUTOPLAY_STARTED","civilopediaVisible":0,"civilopediaContext":"NONE","civilopediaActivePlayer":-1,"civilopediaActiveCivilization":-1,"buttonPopupAwaitingInteraction":0,"buttonPopupType":"NONE","buttonPopupTypeId":-1,"buttonPopupActivePlayer":-1,"buttonPopupFocusedUtc":"-","buttonPopupResolvedUtc":"-","buttonPopupResolution":"-","buttonPopupResponseButton":-1,"autoplayEndCause":"-","priorStatusWriteFailures":0,"priorHistoryWriteFailures":0}
{"record":"transition","revision":8,"run":"20261026T060725.015Z_640","stateSerial":21,"intervalStarted":1,"previousState":"AUTOPLAY","previousStartedUtc":"20261026T061516.960Z","previousEndedUtc":"20261026T061952.839Z","previousDurationMilliseconds":275887,"previousSessionSerial":6,"previousStartTurn":0,"previousRequestedAutoplayTurns":251,"recordedUtc":"20261026T061952.839Z","state":"PLAYING","stateStartedUtc":"20261026T061952.839Z","stateElapsedMilliseconds":0,"sessionSerial":6,"gameTurn":250,"autoplayRemainingTurns":0,"reason":"AUTOPLAY_ENDED","civilopediaVisible":0,"civilopediaContext":"NONE","civilopediaActivePlayer":-1,"civilopediaActiveCivilization":-1,"buttonPopupAwaitingInteraction":0,"buttonPopupType":"NONE","buttonPopupTypeId":-1,"buttonPopupActivePlayer":-1,"buttonPopupFocusedUtc":"-","buttonPopupResolvedUtc":"-","buttonPopupResolution":"-","buttonPopupResponseButton":-1,"autoplayEndCause":"SCHEDULED","priorStatusWriteFailures":0,"priorHistoryWriteFailures":0}
{"record":"transition","revision":8,"run":"20261026T060725.015Z_640","stateSerial":23,"intervalStarted":1,"previousState":"PLAYING","previousStartedUtc":"20261026T061952.839Z","previousEndedUtc":"20261026T062208.451Z","previousDurationMilliseconds":135615,"previousSessionSerial":6,"previousStartTurn":250,"previousRequestedAutoplayTurns":0,"recordedUtc":"20261026T062208.451Z","state":"AUTOPLAY","stateStartedUtc":"20261026T062208.451Z","stateElapsedMilliseconds":0,"sessionSerial":6,"gameTurn":251,"autoplayRemainingTurns":100,"reason":"AUTOPLAY_STARTED","civilopediaVisible":0,"civilopediaContext":"NONE","civilopediaActivePlayer":-1,"civilopediaActiveCivilization":-1,"buttonPopupAwaitingInteraction":1,"buttonPopupType":"BUTTONPOPUP_MAIN_MENU","buttonPopupTypeId":1,"buttonPopupActivePlayer":0,"buttonPopupFocusedUtc":"20261026T062159.004Z","buttonPopupResolvedUtc":"-","buttonPopupResolution":"-","buttonPopupResponseButton":-1,"autoplayEndCause":"-","priorStatusWriteFailures":0,"priorHistoryWriteFailures":0}
{"record":"transition","revision":8,"run":"20261026T060725.015Z_640","stateSerial":24,"intervalStarted":1,"previousState":"AUTOPLAY","previousStartedUtc":"20261026T062208.451Z","previousEndedUtc":"20261026T062353.274Z","previousDurationMilliseconds":104826,"previousSessionSerial":6,"previousStartTurn":251,"previousRequestedAutoplayTurns":100,"recordedUtc":"20261026T062353.274Z","state":"PLAYING","stateStartedUtc":"20261026T062353.274Z","stateElapsedMilliseconds":0,"sessionSerial":6,"gameTurn":289,"autoplayRemainingTurns":0,"reason":"AUTOPLAY_ENDED","civilopediaVisible":0,"civilopediaContext":"NONE","civilopediaActivePlayer":-1,"civilopediaActiveCivilization":-1,"buttonPopupAwaitingInteraction":1,"buttonPopupType":"BUTTONPOPUP_MAIN_MENU","buttonPopupTypeId":1,"buttonPopupActivePlayer":0,"buttonPopupFocusedUtc":"20261026T062159.004Z","buttonPopupResolvedUtc":"-","buttonPopupResolution":"-","buttonPopupResponseButton":-1,"autoplayEndCause":"USER_INTERRUPTED","priorStatusWriteFailures":0,"priorHistoryWriteFailures":0}
{"record":"transition","revision":8,"run":"20261026T084132.556Z_7048","stateSerial":21,"intervalStarted":0,"previousState":"NONE","previousStartedUtc":"-","previousEndedUtc":"-","previousDurationMilliseconds":-1,"previousSessionSerial":0,"previousStartTurn":-1,"previousRequestedAutoplayTurns":0,"recordedUtc":"20261026T084336.729Z","state":"PLAYING","stateStartedUtc":"20261026T084215.564Z","stateElapsedMilliseconds":81165,"sessionSerial":1,"gameTurn":290,"autoplayRemainingTurns":0,"reason":"BUTTON_POPUP_RESPONDED","civilopediaVisible":0,"civilopediaContext":"IN_GAME","civilopediaActivePlayer":0,"civilopediaActiveCivilization":17,"buttonPopupAwaitingInteraction":0,"buttonPopupType":"BUTTONPOPUP_MAIN_MENU","buttonPopupTypeId":1,"buttonPopupActivePlayer":0,"buttonPopupFocusedUtc":"20261026T084335.443Z","buttonPopupResolvedUtc":"20261026T084336.729Z","buttonPopupResolution":"RESPONDED","buttonPopupResponseButton":8,"autoplayEndCause":"-","priorStatusWriteFailures":0,"priorHistoryWriteFailures":0}
{"record":"transition","revision":8,"run":"20261026T084132.556Z_7048","stateSerial":23,"intervalStarted":0,"previousState":"NONE","previousStartedUtc":"-","previousEndedUtc":"-","previousDurationMilliseconds":-1,"previousSessionSerial":0,"previousStartTurn":-1,"previousRequestedAutoplayTurns":0,"recordedUtc":"20261026T084338.086Z","state":"PLAYING","stateStartedUtc":"20261026T084215.564Z","stateElapsedMilliseconds":82522,"sessionSerial":1,"gameTurn":290,"autoplayRemainingTurns":0,"reason":"BUTTON_POPUP_RESPONDED","civilopediaVisible":0,"civilopediaContext":"IN_GAME","civilopediaActivePlayer":0,"civilopediaActiveCivilization":17,"buttonPopupAwaitingInteraction":0,"buttonPopupType":"BUTTONPOPUP_CONFIRM_MENU","buttonPopupTypeId":2,"buttonPopupActivePlayer":0,"buttonPopupFocusedUtc":"20261026T084336.730Z","buttonPopupResolvedUtc":"20261026T084338.086Z","buttonPopupResolution":"RESPONDED","buttonPopupResponseButton":0,"autoplayEndCause":"-","priorStatusWriteFailures":0,"priorHistoryWriteFailures":0}
{"record":"transition","revision":8,"run":"20261026T084132.556Z_7048","stateSerial":25,"intervalStarted":1,"previousState":"PLAYING","previousStartedUtc":"20261026T084215.564Z","previousEndedUtc":"20261026T084338.115Z","previousDurationMilliseconds":82551,"previousSessionSerial":1,"previousStartTurn":289,"previousRequestedAutoplayTurns":0,"recordedUtc":"20261026T084338.115Z","state":"WORLD_BUILDER","stateStartedUtc":"20261026T084338.115Z","stateElapsedMilliseconds":0,"sessionSerial":1,"gameTurn":290,"autoplayRemainingTurns":0,"reason":"WORLD_BUILDER_SCREEN_SHOWN","civilopediaVisible":0,"civilopediaContext":"IN_GAME","civilopediaActivePlayer":0,"civilopediaActiveCivilization":17,"buttonPopupAwaitingInteraction":0,"buttonPopupType":"BUTTONPOPUP_CONFIRM_MENU","buttonPopupTypeId":2,"buttonPopupActivePlayer":0,"buttonPopupFocusedUtc":"20261026T084336.730Z","buttonPopupResolvedUtc":"20261026T084338.086Z","buttonPopupResolution":"RESPONDED","buttonPopupResponseButton":0,"autoplayEndCause":"-","priorStatusWriteFailures":0,"priorHistoryWriteFailures":0}
{"record":"transition","revision":8,"run":"20261026T084132.556Z_7048","stateSerial":26,"intervalStarted":1,"previousState":"WORLD_BUILDER","previousStartedUtc":"20261026T084338.115Z","previousEndedUtc":"20261026T084348.297Z","previousDurationMilliseconds":10182,"previousSessionSerial":1,"previousStartTurn":290,"previousRequestedAutoplayTurns":0,"recordedUtc":"20261026T084348.297Z","state":"PLAYING","stateStartedUtc":"20261026T084348.297Z","stateElapsedMilliseconds":0,"sessionSerial":1,"gameTurn":290,"autoplayRemainingTurns":0,"reason":"WORLD_BUILDER_SCREEN_HIDDEN","civilopediaVisible":0,"civilopediaContext":"IN_GAME","civilopediaActivePlayer":0,"civilopediaActiveCivilization":17,"buttonPopupAwaitingInteraction":0,"buttonPopupType":"BUTTONPOPUP_CONFIRM_MENU","buttonPopupTypeId":2,"buttonPopupActivePlayer":0,"buttonPopupFocusedUtc":"20261026T084336.730Z","buttonPopupResolvedUtc":"20261026T084338.086Z","buttonPopupResolution":"RESPONDED","buttonPopupResponseButton":0,"autoplayEndCause":"-","priorStatusWriteFailures":0,"priorHistoryWriteFailures":0}
{"record":"process_exit","revision":11,"run":"20261026T174016.979Z_16124","processId":16124,"recordedUtc":"20261026T175207.503Z","processExitedUtc":"20261026T175207.373Z","exitCode":-1073741819,"exitCodeHex":"0xC0000005","outcome":"NONZERO_EXIT_CODE","lastInProcessUpdatedUtc":"20261026T175204.459Z","lastActivity":"EXIT_REQUESTED","sessionSerial":1,"gameTurn":291,"firstFailureDialogObservedUtc":"20261026T174937.360Z","failureDialogCount":1,"failureDialog":{"kind":"CIV4_CRASH_DUMP_PROMPT","visible":false,"firstObservedUtc":"20261026T174937.360Z","observedUtc":"20261026T175206.059Z","windowHandle":"0x30F56","title":"Program Execution Problem","text":"This program has encountered a problem and needs to be closed.  Do you wish to save a diagnostic file?"}}
{"record":"process_exit","revision":11,"run":"20261026T175231.114Z_40152","processId":40152,"recordedUtc":"20261026T175504.432Z","processExitedUtc":"20261026T175504.243Z","exitCode":3,"exitCodeHex":"0x00000003","outcome":"NONZERO_EXIT_CODE","lastInProcessUpdatedUtc":"20261026T175309.243Z","lastActivity":"PLAYING","sessionSerial":1,"gameTurn":289,"firstFailureDialogObservedUtc":"20261026T175309.567Z","failureDialogCount":1,"failureDialog":{"kind":"MSVC_RUNTIME_ERROR","visible":false,"firstObservedUtc":"20261026T175309.567Z","observedUtc":"20261026T175504.223Z","windowHandle":"0xE0018","title":"Microsoft Visual C++ Runtime Library","text":"Runtime Error!\n\nProgram: ...IV Beyond the Sword\\Beyond the Sword\\Civ4BeyondSword.exe\n\n\r\nThis application has requested the Runtime to terminate it in an unusual way.\nPlease contact the application\u0027s support team for more information.\r\n"}}
```

The [full history example](/_1_AdvCiv-SAS/Docs/examples/runtime_status/SASRuntimeHistory_example.jsonl) retains a separate, richer earlier run with new/load/menu/Sevopedia and autoplay observations; its [capture notes](/_1_AdvCiv-SAS/Docs/examples/runtime_status/README.md) identify that run. The newer excerpts above supplement it here rather than replacing the full example.

For lifecycle details and field interpretation, see the [Main Changes Guide's runtime section](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md#runtime-status-and-history) and [runtime revision history](/_1_AdvCiv-SAS/Docs/revisions/SASRuntime.md).

#### Live source-edit observation

Enabled runtime diagnostics can additionally use `SAS_RUNTIME_SOURCE_WATCH_ON=1` to launch [`SASRuntimeSourceObserver.ps1`](/Assets/SASRuntimeSourceObserver.ps1). This is default-off and separate from the exit/dialog observer.

- `SASRuntimeSourceWatch_<process-start UTC>_<PID>.json` reports attachment/state, watched scopes, observer host versions and event/write/drop/error counters.
- `SASRuntimeSourceChanges_<process-start UTC>_<PID>.jsonl` records coalesced disk-change bursts for Python/XML (including BUG Config XML), PrivateMaps scripts/scenarios, Resource `.thm` themes, mod Settings `.ini`/`.xml`/`.txt` files, and nonrecursive mod-root `.ini` files with mod-relative path, first/last observed UTC, observed action kinds, final presence/size/write time and SHA-256 status.
- `engineReloadState=NOT_OBSERVED` is intentional: filesystem change evidence does not establish that Civ4 reloaded, parsed or executed the edited file. C++ is excluded because source edits cannot replace the loaded DLL.
- Observation times belong to filesystem notifications/recording, not necessarily the editor's original save syscall. No file contents are copied, and large/unreadable files use explicit fingerprint status rather than an invented hash.

Paths, observed times and fingerprints provide an initial timeline for correlating file saves with errors or crashes. Keeping that evidence without retaining earlier source contents avoids content-snapshot storage and line-diff machinery.

This is evidence of disk activity, not proof that an edit caused a failure. Explaining the exact changed lines still requires a content diff; the watcher does not claim to supply one.

`FileSystemWatcher` receives Windows notifications rather than repeatedly scanning/hashing the tree. The helper's one-second event-wait timeout only services save-burst coalescing; idle cycles do not rewrite state.

Hashes are sampled after a short quiet period, with a 16 MiB file-size check; files that are too large or unreadable get an explicit status.

Enabled observation costs a separate PowerShell process, notification buffers and event/hash work; gameplay performance was not measured.

With source watching disabled, its helper is not launched and performs no monitoring or hashing.

The live journal identifies **which path was saved, when, its final byte size and SHA-256**. It does not retain old contents, line/value diffs or a before/after byte delta. An unchanged-content save can therefore have a filesystem row with the same fingerprint as its previous observed save.

The SGR175 source-provenance extension serves a different purpose: existing Git patch/source-context evidence now includes the external `.ps1`/`.cs` helpers, so those changes are not omitted when identifying the source behind a run. It is a cached source baseline, not a live edit timeline.

The user Logs directory is excluded to avoid watching continuously written output. User-folder BUG settings are also outside this watcher.

SASGameRecord already captures configured options through `SASGameRecordSettings.py` at session initialization and relevant options callbacks.

That semantic record describes option values, whereas a file notification alone cannot establish whether a running consumer adopted an edit. Disk changes made directly to user settings are not comprehensively tracked here.

##### `SASRuntimeSourceWatch_*.json` (watcher state and host)

The matching `SASRuntimeSourceWatch_20261027T062715.357Z_524.json` state capture includes actual host metadata and watcher-health counters. This is a snapshot during the run, so its counters/state are illustrative rather than fixed expected values:

```json
{
    "revision":  12,
    "processId":  524,
    "processStartUtc":  "20261027T062715.357Z",
    "observerProcessId":  10248,
    "observerState":  "WATCHING",
    "startedUtc":  "20261027T062723.907Z",
    "environment":  {
                        "powershellVersion":  "5.1.19041.6456",
                        "powershellEdition":  "Desktop",
                        "clrVersion":  "4.0.30319.42000",
                        "frameworkRelease":  533325,
                        "processBits":  32,
                        "executablePath":  "C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe"
                    },
    "watchedScopes":  [
                          "Assets/Python/**/*.py",
                          "Assets/XML/**/*.xml",
                          "Assets/Config/**/*.xml",
                          "PrivateMaps/*.py and scenarios (recursive)",
                          "Resource/**/*.thm",
                          "Settings/**/*.{ini,xml,txt}",
                          "*.ini (mod root only)"
                      ],
    "eventFilename":  "SASRuntimeSourceChanges_20261027T062715.357Z_524.jsonl",
    "rawEventsObserved":  20,
    "burstsWritten":  8,
    "rawEventsCoalesced":  12,
    "rowsDropped":  0,
    "writeFailures":  0,
    "watcherErrors":  0,
    "pendingPaths":  0,
    "lastRecordedUtc":  "20261027T063737.690Z",
    "attachedUtc":  "20261027T062724.019Z"
}
```

[`SASRuntimeObserverEnvironment.ps1`](/Assets/SASRuntimeObserverEnvironment.ps1) collects these values once per helper startup. Version fields belong to the state/receipt, not every edit row. The exit receipt's `listenerCompilation` measures only the C# `Add-Type` step and reports success/failure and elapsed milliseconds; no C# compiler version is inferred from the CLR version.

##### `SASRuntimeSourceChanges_*.jsonl` (live file changes)

The following six complete JSONL rows are from `SASRuntimeSourceChanges_20261027T062715.357Z_524.jsonl`, recorded during the live 2026-10-27 autoplay test. The first five cover creating a disposable INI, changing `test=1` to `test=2`, saving the same contents again, renaming it and deleting it; the final row is an observed XML-save burst from the same run.

```jsonl
{"record":"source_file_change","revision":12,"run":"20261027T062715.357Z_524","recordedUtc":"20261027T063513.813Z","firstObservedUtc":"20261027T063512.738Z","lastObservedUtc":"20261027T063512.761Z","path":"SASWatcherProbe.ini","eventCount":2,"actionsObserved":["CREATED","CHANGED"],"oldPathsObserved":[],"finalState":"PRESENT","sizeBytes":8,"lastWriteUtc":"20261027T063512.724Z","fingerprintAlgorithm":"SHA256","fingerprint":"44031683E33D3405122814D4EC2FFFFD552958A417335E37283A196D9581B8B8","fingerprintStatus":"AVAILABLE","engineReloadState":"NOT_OBSERVED"}
{"record":"source_file_change","revision":12,"run":"20261027T062715.357Z_524","recordedUtc":"20261027T063514.850Z","firstObservedUtc":"20261027T063513.833Z","lastObservedUtc":"20261027T063513.834Z","path":"SASWatcherProbe.ini","eventCount":2,"actionsObserved":["CHANGED"],"oldPathsObserved":[],"finalState":"PRESENT","sizeBytes":8,"lastWriteUtc":"20261027T063513.833Z","fingerprintAlgorithm":"SHA256","fingerprint":"E685DA9095347C0BDE9D8D1C76ABD7452F6B8FEBF7C82EB45CCB3875FD9FBD5F","fingerprintStatus":"AVAILABLE","engineReloadState":"NOT_OBSERVED"}
{"record":"source_file_change","revision":12,"run":"20261027T062715.357Z_524","recordedUtc":"20261027T063515.961Z","firstObservedUtc":"20261027T063514.943Z","lastObservedUtc":"20261027T063514.944Z","path":"SASWatcherProbe.ini","eventCount":2,"actionsObserved":["CHANGED"],"oldPathsObserved":[],"finalState":"PRESENT","sizeBytes":8,"lastWriteUtc":"20261027T063514.943Z","fingerprintAlgorithm":"SHA256","fingerprint":"E685DA9095347C0BDE9D8D1C76ABD7452F6B8FEBF7C82EB45CCB3875FD9FBD5F","fingerprintStatus":"AVAILABLE","engineReloadState":"NOT_OBSERVED"}
{"record":"source_file_change","revision":12,"run":"20261027T062715.357Z_524","recordedUtc":"20261027T063517.072Z","firstObservedUtc":"20261027T063516.054Z","lastObservedUtc":"20261027T063516.054Z","path":"SASWatcherProbeRenamed.ini","eventCount":1,"actionsObserved":["RENAMED"],"oldPathsObserved":["SASWatcherProbe.ini"],"finalState":"PRESENT","sizeBytes":8,"lastWriteUtc":"20261027T063514.943Z","fingerprintAlgorithm":"SHA256","fingerprint":"E685DA9095347C0BDE9D8D1C76ABD7452F6B8FEBF7C82EB45CCB3875FD9FBD5F","fingerprintStatus":"AVAILABLE","engineReloadState":"NOT_OBSERVED"}
{"record":"source_file_change","revision":12,"run":"20261027T062715.357Z_524","recordedUtc":"20261027T063518.181Z","firstObservedUtc":"20261027T063517.162Z","lastObservedUtc":"20261027T063517.162Z","path":"SASWatcherProbeRenamed.ini","eventCount":1,"actionsObserved":["DELETED"],"oldPathsObserved":[],"finalState":"ABSENT","sizeBytes":-1,"lastWriteUtc":"-","fingerprintAlgorithm":"SHA256","fingerprint":"-","fingerprintStatus":"NOT_PRESENT","engineReloadState":"NOT_OBSERVED"}
{"record":"source_file_change","revision":12,"run":"20261027T062715.357Z_524","recordedUtc":"20261027T063727.412Z","firstObservedUtc":"20261027T063726.387Z","lastObservedUtc":"20261027T063726.389Z","path":"Assets/XML/GlobalDefines_advciv_sas.xml","eventCount":3,"actionsObserved":["CHANGED"],"oldPathsObserved":[],"finalState":"PRESENT","sizeBytes":277002,"lastWriteUtc":"20261027T063726.387Z","fingerprintAlgorithm":"SHA256","fingerprint":"09CC65D4D07C40F882A03450516AF49AA4DC4C516966D4ECCC51D2187221FD68","fingerprintStatus":"AVAILABLE","engineReloadState":"NOT_OBSERVED"}
```

The first two fingerprints differ despite equal byte sizes; the unchanged-content save retains the second fingerprint. The XML row identifies the saved file and its final hash, but does not show edited lines or establish that Civ4 adopted the changes. Both disposable INI paths were removed after the test.

### DLL build reports

`CvGameCoreDLL/Project/<configuration>/AdvCiv.log` carries compiler/linker messages, and `CvGameCoreDLL.dll.build.json` reports build progress/result, Git/source context, warnings/errors and binary identity. These help distinguish the source being reviewed from the DLL actually built or loaded.

SAS enriches the existing `AdvCiv.log` rather than replacing its compiler output: the reporting wrapper adds UTC start/end times, configuration/request and Git context, temporary-artifact state, source/project input-change summary counts, final result/exit code/duration and distinct coded warning/error counts.

These build-level summaries help explain what was compiled and how it finished; ordinary compiler lines keep their existing format.

The build pair describes a development process; the runtime JSON/JSONL describes observations from Civ4. They share the goal of identifying ongoing activity and its result, but have different producers and lifetimes.

#### `CvGameCoreDLL.dll.build.json` (toolchain and build launcher)

The companion JSON adds structured detail, including source/project manifests and changes, recognized diagnostic lines and before/after DLL identity. Its `toolchain` records Makefile-expanded C/C++ compiler, linker and resource-compiler commands, resolved executable paths/file/product versions, and configured toolkit/SDK paths.

This distinguishes the build tools from the IDE: a VS2010 IDE can invoke VC2003. The wrapper queries a print-only Makefile target and reads executable version resources; it does not run the compiler for detection. Missing query/tool metadata is explicit and does not block compilation.

`invocation` independently records the explicit wrapper entry mode (`IDE_SWITCH` for `-IdeBuild`, otherwise `DIRECT_WRAPPER`), PowerShell host versions/bitness, and up to eight observed parent-process names/paths/executable versions. This can identify VCExpress, devenv, MSBuild or another launcher when present.

A direct wrapper call can itself come from automation or an IDE terminal; the mode alone does not identify a human, agent or IDE version. Missing/partial parent evidence remains explicit, and command lines are not collected.

The following selected fields come from the successful Debug-opt build of 2026-10-27. Paths, process IDs and other fields are omitted from this excerpt; retained values are unchanged. It shows VS2010 Express and MSBuild separately from the VC2003 compiler:

```json
{
  "configuration": "Debug-opt",
  "status": "SUCCEEDED",
  "toolchain": {
    "selection": "MAKEFILE_EXPANSION",
    "tools": {
      "cppCompiler": {
        "fileVersion": "13.10.3077",
        "productVersion": "7.10.3077"
      },
      "linker": {
        "fileVersion": "7.10.3077",
        "productVersion": "7.10.3077"
      }
    }
  },
  "invocation": {
    "entryMode": "IDE_SWITCH",
    "powershellVersion": "5.1.19041.6456",
    "processBits": 32,
    "ancestorState": "OBSERVED",
    "ancestors": [
      {
        "name": "cmd.exe",
        "fileVersion": "10.0.19041.4522 (WinBuild.160101.0800)"
      },
      {
        "name": "MSBuild.exe",
        "fileVersion": "4.8.9037.0 built by: NET481REL1"
      },
      {
        "name": "VCExpress.exe",
        "fileVersion": "10.0.30319.1 built by: RTMRel"
      }
    ]
  }
}
```

Selected-tool metadata is build-time evidence, not a claim that an old DLL was produced by the currently configured compiler. Existing loaded-DLL context separately reports compile-time `msvcVersion` / `msvcFullVersion`; those describe the compiler that produced that binary.

The complete fields appear in future build reports and as compact `Selected build toolchain:` / `Build invocation:` lines in `AdvCiv.log`; older full examples retain their original metadata.

An XML declaration such as `version="1.0"` identifies document syntax, not the parser executable/version or the mod's rules/schema revision.

Civ4 exposes parsing through `CvDLLXmlIFaceBase` in the EXE; that interface has no parser-version getter. No MSXML identity is inferred from the declaration or from an installed DLL.

XML changes remain part of the existing source/build provenance rather than a fabricated parser-version field.

#### `AdvCiv.log` (compiler output and build summaries)

For example, these five rows come from the [captured Release compiler log](/_1_AdvCiv-SAS/Docs/examples/build_reports/AdvCiv_Release_example.log), dated 2026-10-12 (IDE indentation omitted, intervening rows omitted; `<MOD_ROOT>` is the example's existing path substitution):

```log
Started UTC: 2026-10-12T21:24:06.628Z
Configuration: Release; request: BUILD; branch: main; commit: -
Ended UTC: 2026-10-12T21:25:52.293Z; result: SUCCEEDED; exit code: 0; duration milliseconds: 105657
Distinct coded diagnostic lines: warnings=0; errors=0
Build details (JSON): <MOD_ROOT>\CvGameCoreDLL\Project\Release\CvGameCoreDLL.dll.build.json
```

Selected, nonadjacent complete rows from the 2026-10-27 Debug-opt `AdvCiv.log` show the newer caller metadata beside ordinary build boundaries (IDE indentation removed). Its `Selected build toolchain:` row carries the toolchain object illustrated in the JSON excerpt above:

```log
Started UTC: 2026-10-27T06:24:16.025Z
Configuration: Debug-opt; request: BUILD; branch: main; commit: 7fb4c4308559b1d658f1ea0d8b6b4c19e6bd95da
Build invocation: {"entryMode":"IDE_SWITCH","powershellVersion":"5.1.19041.6456","powershellEdition":"Desktop","clrVersion":"4.0.30319.42000","processBits":32,"ancestorState":"OBSERVED","ancestors":[{"processId":25500,"name":"cmd.exe","path":"C:\\Windows\\SysWOW64\\cmd.exe","fileVersion":"10.0.19041.4522 (WinBuild.160101.0800)","productVersion":"10.0.19041.4522"},{"processId":3968,"name":"MSBuild.exe","path":"C:\\Windows\\Microsoft.NET\\Framework\\v4.0.30319\\MSBuild.exe","fileVersion":"4.8.9037.0 built by: NET481REL1","productVersion":"4.8.9037.0"},{"processId":5124,"name":"VCExpress.exe","path":"C:\\Program Files (x86)\\Microsoft Visual Studio 10.0\\Common7\\IDE\\VCExpress.exe","fileVersion":"10.0.30319.1 built by: RTMRel","productVersion":"10.0.30319.1"}]}
Ended UTC: 2026-10-27T06:26:20.041Z; result: SUCCEEDED; exit code: 0; duration milliseconds: 124018
Distinct coded diagnostic lines: warnings=0; errors=0
```

#### `_SNAPSHOT_CONTEXT/archive_contents_and_context.txt` (packaging host)

The light-source ZIP helper writes its actual packaging Python version/executable to the console and `_SNAPSHOT_CONTEXT/archive_contents_and_context.txt`. Packaging-host, syntax-checker and embedded-game Python versions describe separate tools. A real packaging dry run on 2026-10-27 printed the following (executable path omitted):

```log
Packaging Python: 3.12.3 (tags/v3.12.3:f6650f9, Apr  9 2024, 14:05:25) [MSC v.1938 64 bit (AMD64)]
```

The local standalone checker reported Python 2.4.4 in a separate collector test; neither of these observations establishes Civ4's embedded version. That value comes from its own enabled SGR session baseline.

- The [root README's build-report overview](/README.md#dll-build-reports) introduces their role alongside other development tools.
- The [DLL Compilation Guide](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README_DLL_Compilation.md#persistent-build-reports) explains generation, fields, replacement on the next attempt and shipping requirements.
- Complete Release examples: [build JSON](/_1_AdvCiv-SAS/Docs/examples/build_reports/AdvCiv_Release_example.build.json) and [compiler log](/_1_AdvCiv-SAS/Docs/examples/build_reports/AdvCiv_Release_example.log). The guide also links [Debug-opt examples](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README_DLL_Compilation.md#example-build-output).

## Python diagnostic messages

`SASPythonLogging` wraps Python stdout/stderr and supplies the same row formatter to Civ4's `CvUtil.RedirectDebug` and `RedirectError` classes. Direct prints, BUG file messages and multiline traceback text therefore share one timestamp path after installation.

The shared formatter adds a UTC date/time with milliseconds at logical line starts. Fragmented writes retain line-start state, and each write is forwarded immediately; no partial row is held until its newline. Blank rows remain blank. BUG's timestamp option controls the shared formatter, while its existing message-level filtering and on-screen messages remain unchanged.

The timestamp comes from the DLL's Windows UTC sampler. The Python layer requires a DLL exposing `getSASDiagnosticUtcTimestamp`; disabling timestamps avoids sampling the clock. The leader-cache serializer uses an explicit raw-output path so its generated Python module remains copyable.

Timestamp work occurs when Python writes output; there is no frame timer or background polling. BUG-filtered messages never reach the stream, and disabling timestamps skips clock sampling while retaining stream processing.

The wrapper does not gate on the INI's `LoggingEnabled` switch. If Python still emits text while the engine suppresses file output, formatting work can still occur; the logging-disabled case has not been measured here.

Structured SAS Python diagnostics use the same stream boundary through `SASPythonLogging.writeRecord`; ordinary callers normally use `CvUtil.pyPrintRecord`. A stable record name is followed by explicit `key=value` fields, while the stream wrapper remains responsible for UTC timestamps.

This avoids repeated hand-built `record=` prefixes without changing inherited `CvUtil.pyPrint` prose/debug behavior.

EXE output produced before installation or written directly to its files bypasses these streams. In particular, the Python startup preamble and early `PythonErr2.log` warnings cannot be assumed to pass through the Python wrappers.

`PythonErr.log` keeps ordinary traceback syntax rather than converting frames into `record=` fields; preserving Python's standard exception shape is more useful than machine-labelling each frame. `PythonErr2.log` likewise retains module-loader/warning prose after the shared timestamp prefix. Generic BUG severity rows and intentionally human-oriented debug dumps also remain prose.

## Startup rows and run boundaries

Rows emitted before the stream wrapper is installed remain in the original log, with their text unchanged. Their exact per-row UTC times cannot be reconstructed from a later snapshot. Preserving a copy retains this evidence, but does not recover those missing timestamps.

This is the boundary of the current Python interception, not a demonstrated impossibility of native interception. Capturing EXE-written startup or engine-log rows at emission would require a separate integration approach; its feasibility and cost were not established by these Python/DLL writer changes.

When runtime recording is enabled, `SASRuntimeStatus.json` identifies the process through `processId` and `processStartUtc`, and the current new/load session through `sessionSerial`, `sessionKind` and `sessionStartedUtc`. `nativeReadyUtc` distinguishes session initialization from the game becoming ready.

The companion `SASRuntimeHistory_*.jsonl` preserves dated transitions, including completed activity intervals and reset/exit observations. A clean shutdown publishes `PROCESS_EXIT` with `EXITED_CLEANLY`; its observation timestamp identifies the recorded shutdown boundary.

There is no separate universal `sessionEndedUtc` field, and a crash or forced termination can leave only the last observation rather than an exact end time.

## Structured Python diagnostic records

Screen notifications retain their numeric ID and add its canonical Python constant name, such as `screenId=99 screenType=CvScreenEnums.MAIN_INTERFACE`; `13` is `REPLAY_SCREEN` and `18` is `INFO_SCREEN`.

Names are derived once from `CvScreenEnums.py`, which now also contains the IDs from the removed standalone `SevoScreenEnums.py` under class `SevoScreenEnums`, alongside the original general-screen and vanilla Civilopedia definitions.

The class keeps overlapping encyclopedia IDs distinct; the lookup selects the active encyclopedia while retaining general screen names. Unregistered IDs remain explicit.

`record=SCREEN_OFF` includes the last notified screen as context; it does not establish a verified individual screen-close callback.

Font initialization messages identify the icon role, XML type, font character code and description. For example, the formerly ambiguous `329 - judaism` and `330 - judaism` refer to the religion and holy-city glyphs, respectively, rather than religion enum IDs. The richer messages preserve the inherited icon-map behavior.

SAS-formatted diagnostics identify their kind through a `record=` field, such as `record=SCREEN_TURNED_ON`, `record=SCREEN_OFF` or `record=FONT_ICON`. Searching for `record=SCREEN_` groups screen/navigation messages; `record=WB_BRUSH_SELECTED` finds brush rows with `mode=ADVANCED_START`, `PLAYER` or `MAP`.

Other labelled families include `record=VICTORY_SCREEN_*` for vote-definition scans/tallies, `record=DIPLOMACY_*` for optional diplomacy debugging, `record=EVENT_MANAGER_*` and `record=PLAYER_ALIVE_CHANGED` for event lifecycle/state, and `record=PY_COMPONENT_*` for Python component lifecycle.

AI Auto Play and ChangePlayer use their own action/result records, SAS font-size resolution uses `record=UI_FONT_SIZE_RESOLVED`, and WorldBuilder save/read/apply work uses `record=WB_*`. `record=MOD_NET_MESSAGE`, `record=GAME_END_CALLBACK` and `record=SEVOPEDIA_*` remain explicit families as well.

These labels describe existing diagnostics; game-end callbacks are distinct from process exit, and vote-definition scans are distinct from player choices.

These message refinements concern chiefly Python-emitted output in `PythonDbg.log`. Shared stream timestamps also cover Python error output; the one direct C++ Starting Position Iteration row now follows the same UTC/`record=` convention. Engine-written `app.log` and `audio.log` retain their original formats, while DLL-controlled `xml.log` rows are modernized separately as described above.

## Screen LOG button exports

The **LOG** buttons on selected SAS screens append a read-only inspection copy to `PythonDbg.log`; they do not create a new file per screen or enable continuous SASGameRecord/BBAI logging. Search the screen-specific `_BEGIN` / `_END` markers to find a click's output among normal Python messages.

The UTC prefix is the time the export was written, not when an old battle or timeline event happened. In-game turns/years belong to the exported data. These are on-demand screen snapshots, separate from SGR's automatic game record and runtime-status observations.

The samples below are unchanged captured rows, selected for variety with intervening rows omitted; their original order, timestamps and values are retained. Battles, Timeline and the four Sevopedia charts were exported on 2026-10-26; Changes uses the 2026-10-25 export containing both Advanced Start and WorldBuilder edits.

| Screen | Button control | Output search key |
| --- | --- | --- |
| Military Advisor, Battles | `SAS_MILIT_UI_BATTLES_LOG_BUTTON_ON=1` | `SAS_MILITARY_ADVISOR_BATTLE_HISTORY` |
| World Advisor, Changes | LOG is provided on the Changes tab when saved entries exist | `SAS_WORLD_ADVISOR_CHANGES` |
| Info Screen, Timeline | `SAS_INFO_UI_TIMELINE_LOG_BUTTON_ON=1` | `SAS_CV_INFO_SCREEN_TIMELINE_PANEL` |
| Sevopedia, Era chart | `SAS_INFO_UI_TIMELINE_LOG_BUTTON_ON=1` | `SAS_SEVOPEDIA_ERA_CHART` |
| Sevopedia, Handicap chart | `SAS_INFO_UI_TIMELINE_LOG_BUTTON_ON=1` | `SAS_SEVOPEDIA_HANDICAP_CHART` |
| Sevopedia, Game Speed chart | `SAS_INFO_UI_TIMELINE_LOG_BUTTON_ON=1` | `SAS_SEVOPEDIA_GAME_SPEED_CHART` |
| Sevopedia, World Size chart | `SAS_INFO_UI_TIMELINE_LOG_BUTTON_ON=1` | `SAS_SEVOPEDIA_WORLD_SIZE_CHART` |

### Military Advisor: Battles

The selected player's battle perspective, opponent identities and combat columns are exported as pipe-separated text. The captured context identifies the observer and inspected player; the screen's location/perspective filtering still applies. Writer: `dbgLogBattleHistory` in [CvMilitaryAdvisor.py](/Assets/Python/Screens/CvMilitaryAdvisor.py).

```log
2026-10-26T04:38:18.856Z SAS_MILITARY_ADVISOR_BATTLE_HISTORY_BEGIN
2026-10-26T04:38:18.856Z BattleHistoryContext: DebugMode=0 | ObserverPID=0
2026-10-26T04:38:18.856Z PerspectivePlayer: 0 | PC | LEADER_WANGKON | CIVILIZATION_KOREA
2026-10-26T04:38:18.857Z OpponentPlayers: PID | PlayerName | LeaderType | CivType
2026-10-26T04:38:18.857Z OpponentPlayer: 3 | Isabella I | LEADER_ISABELLA | CIVILIZATION_SPAIN
2026-10-26T04:38:18.857Z OpponentPlayer: 7 | Suryavarman II | LEADER_SURYAVARMAN | CIVILIZATION_KHMER
2026-10-26T04:38:18.857Z OpponentPlayer: 8 | Gilgamesh | LEADER_GILGAMESH | CIVILIZATION_SUMERIA
2026-10-26T04:38:18.857Z OpponentPlayer: 10 | Alexander III | LEADER_ALEXANDER | CIVILIZATION_GREECE
2026-10-26T04:38:18.857Z OpponentPlayer: 12 | Huayna Capac | LEADER_HUAYNA_CAPAC | CIVILIZATION_INCA
2026-10-26T04:38:18.857Z OpponentPlayer: 13 | Mao Zedong | LEADER_MAO_ZEDONG | CIVILIZATION_CHINA
2026-10-26T04:38:18.857Z OpponentPlayer: 15 | Mehmed II | LEADER_MEHMED | CIVILIZATION_OTTOMAN
2026-10-26T04:38:18.857Z OpponentPlayer: 48 | Barbarian | LEADER_BARBARIAN | CIVILIZATION_BARBARIAN
2026-10-26T04:38:18.857Z 10 | 18000 BC | Lost | 57 |  | 3 | 3.99 |  | 3.99 | 0 | 0 | Ancient Maceman | Wolf | 0 | 0 | 3 | 3.00 | 0.24 | 3.00 | 48 | 0 |  |  | TERRAIN_PLAINS |  | 56 | 28
2026-10-26T04:38:18.857Z 66 | 2200 BC | Ret. | 67 |  | 4 | 4.00 | 2.88 | 4.00 | 0 | 0 | Longbowman | Archer | 0 | 0 | 2 | 2.00 | 0.32 | 2.00 | 48 | 0 |  |  | TERRAIN_GRASS |  | 50 | 26
2026-10-26T04:38:18.857Z 67 | 2160 BC | Won | 91 |  | 2 | 3.30 | 2.90 | 3.30 | 0 | 0 | Archer | Archer | 1 | 0 | 2 | 0.32 |  | 2.00 | 48 | 0 |  |  | TERRAIN_GRASS |  | 51 | 27
2026-10-26T04:38:18.866Z 487 | 2098 AD | Ret. | 49 |  | 34 | 12.37 | 7.14 | 47.60 | 7 | 0 | Mechanized Infantry | Levitation Artillery | 4 | 0 | 46 | 12.88 | 3.68 | 46.00 | 13 | 0 |  |  | TERRAIN_TUNDRA |  | 53 | 11
2026-10-26T04:38:18.866Z 488 | 2099 AD | Won | 72 | A | 34 | 11.90 | 11.90 | 34.00 | 7 | 0 | Mechanized Infantry | Levitation Artillery | 6 | 0 | 46 | 4.60 |  | 46.00 | 13 | 0 |  |  | TERRAIN_DESERT |  | 52 | 11
2026-10-26T04:38:18.866Z 488 | 2099 AD | Lost | 61 | A | 34 | 5.74 |  | 44.20 | 9 | 0 | Mechanized Infantry | Levitation Artillery | 5 | 0 | 46 | 3.68 | 3.68 | 46.00 | 13 | 0 |  |  | TERRAIN_DESERT |  | 52 | 11
2026-10-26T04:38:18.866Z SAS_MILITARY_ADVISOR_BATTLE_HISTORY_END
```

### World Advisor: Changes

The related `SHOW_INTERMEDIATE` and `SHOW_CANCELLED` settings both mean that `1` shows the named detail and `0` keeps the summary compact. This consistent positive wording avoids reading one option as show and its neighbor as hide; neither changes the raw LOG export.

This export includes Advanced Start purchases/refunds and WorldBuilder edits with recorded budgets, locations and Before/After values. LOG preserves permitted raw events even when the table compacts scalar runs or hides eligible cancellations; the two level edits below remain separate. Writer: `dbgLogChangesHistory` in [CvWorldAdvisorScreen.py](/Assets/Python/Screens/CvWorldAdvisorScreen.py).

```log
2026-10-25T19:33:28.633Z HistoryExportMode: RAW_APPLIED_EVENTS; the Changes table may compact contiguous WorldBuilder scalar edit runs.
2026-10-25T19:33:28.633Z # | Turn | Year | Source | Actor | Action | Target | Location | Before | After | PointsBefore | PointsAfter | GoldBefore | GoldAfter | Cost | VersionIndex
2026-10-25T19:33:28.633Z 0 | 0 | -50000 | ADVANCED_START | P0 | Add City | City #8192 | 33,45 | - | - | 400 | 250 | 0 | 0 | 150 | 0
2026-10-25T19:33:28.633Z 2 | 0 | -50000 | ADVANCED_START | P0 | Add Population | City #16385 | 32,41 | - | - | 100 | 67 | 0 | 0 | 33 | 0
2026-10-25T19:33:28.635Z 51 | 0 | -50000 | WORLD_BUILDER | P0 | Set Level | Level #8192 | 29,42 | 1 | 2 | - | - | - | - | - | 0
2026-10-25T19:33:28.635Z 52 | 0 | -50000 | WORLD_BUILDER | P0 | Set Level | Level #8192 | 29,42 | 2 | 3 | - | - | - | - | - | 0
```

### Info Screen: Timeline

Timeline exports its built/cached, perspective-filtered event text in chronological order, stripping display font/color markup. Unlike the numeric history tables, these are readable event sentences with in-game dates. Writer: `dbgLogPrettySummary` in [CvInfoScreen.py](/Assets/Python/Screens/CvInfoScreen.py).

```log
2026-10-26T04:38:33.777Z SAS_CV_INFO_SCREEN_TIMELINE_PANEL_BEGIN
2026-10-26T04:38:33.780Z - 50000 BC: Session 2 starts
2026-10-26T04:38:33.780Z - 50000 BC: AI Auto Play started
2026-10-26T04:38:33.780Z - 50000 BC: Paris is founded.
2026-10-26T04:38:33.780Z - 45000 BC: Rome is founded.
2026-10-26T04:38:33.780Z - 14250 BC: Huayna Capac is the first to discover Metal Casting!
2026-10-26T04:38:33.780Z - 3750 BC: Mehmed II is the first to discover Writing!
2026-10-26T04:38:33.780Z - 2080 BC: Pacal II completes the Colossus
2026-10-26T04:38:33.780Z - 1240 BC: Mao Zedong is the first to discover Navigation!
2026-10-26T04:38:33.780Z - 340 BC: Suryavarman II completes the Kashi Vishwanath
2026-10-26T04:38:33.780Z - AD 500: Mao Zedong has entered the Medieval era.
2026-10-26T04:38:33.780Z - AD 1000: The Great Scientist Gottfried Leibniz has been born in the Ottoman Empire.
2026-10-26T04:38:33.780Z - AD 1550: Mao Zedong has entered the Industrial era.
2026-10-26T04:38:33.780Z - AD 1745: Julius Caesar declares war on Justinian I!
2026-10-26T04:38:33.780Z - AD 1892: Alexander III has entered the Future era.
2026-10-26T04:38:33.780Z - AD 2009: Suryavarman II has made peace with Mao Zedong
2026-10-26T04:38:33.781Z - AD 2054: Great Engineer has been born in the Incan Empire.
2026-10-26T04:38:33.781Z - January, AD 2083: Napoleon completes the SS Casing!
2026-10-26T04:38:33.781Z - January, AD 2105: Session 3 starts
2026-10-26T04:38:33.787Z SAS_CV_INFO_SCREEN_TIMELINE_PANEL_END
```

### Sevopedia chart exports

The four chart buttons share `chart_dump_table_csv` in [_sevopedia_helpers.py](/Assets/Python/Contrib/Sevopedia/_sevopedia_helpers.py). They export comma-separated field/comparison rows with quoting for embedded delimiters, rather than gameplay-event records. To parse them as CSV, isolate the chart block and remove the UTC prefixes and boundary markers first.

The literal `?` characters below occur in the captures: the shared writer uses Latin-1 encoding with replacement, so unsupported icon glyphs can become `?`. They are not uncertainty labels for the numeric values. The Game Speed header also retains repeated duration/speed text from its current display labels; the sample does not silently correct it.

#### Era chart

Compares starting conditions, initial units/population and era modifiers across the XML eras. Source: [SevoPediaEraChart.py](/Assets/Python/Contrib/Sevopedia/SevoPediaEraChart.py).

```log
2026-10-26T04:38:51.878Z SAS_SEVOPEDIA_ERA_CHART_BEGIN
2026-10-26T04:38:51.878Z ,Field,Ancient,Classical,Medieval,Renaissance,Industrial,Modern,Future
2026-10-26T04:38:51.878Z ,No Goodies,,,,+,+,+,+
2026-10-26T04:38:51.878Z ?,All Goody Techs,+,+,+,+,,,
2026-10-26T04:38:51.878Z ,No Animals,,+,+,+,+,+,+
2026-10-26T04:38:51.878Z ,No Barb Units,,,,,,,
2026-10-26T04:38:51.878Z ,No Barb Cities,,,,+,+,+,+
2026-10-26T04:38:51.878Z ?,Advanced Start Points,400,1600,2400,3600,5500,7500,9500
2026-10-26T04:38:51.878Z ,Starting Unit Multiplier,1,1,2,2,3,3,3
2026-10-26T04:38:51.878Z ,Starting Defense Units,0,1,2,2,3,3,3
2026-10-26T04:38:51.878Z ?,Starting Worker Units,0,1,1,1,2,2,3
2026-10-26T04:38:51.878Z ,Starting Explore Units,1,1,1,1,2,2,2
2026-10-26T04:38:51.878Z ?,Starting Gold,0,10,25,50,100,200,400
2026-10-26T04:38:51.878Z ?,Free Population,0,0,0,1,2,3,4
2026-10-26T04:38:51.878Z ?,Start Percent,0,10,22,36,50,65,80
2026-10-26T04:38:51.878Z ,Train ,100,100,100,100,100,100,100
2026-10-26T04:38:51.878Z ?,Create ,100,100,100,100,100,100,100
2026-10-26T04:38:51.879Z ?,Research ,100,100,100,100,100,100,100
2026-10-26T04:38:51.879Z ,Human Max Groundbreaking Pen.,0,0,15,25,35,25,0
2026-10-26T04:38:51.879Z ?,Culture ,100,100,100,100,100,100,100
2026-10-26T04:38:51.879Z ,AI Age Of Fertility,,,,,+,,
2026-10-26T04:38:51.879Z ?,Tech 03,Literature,Monarchy,Sacred Architecture,Naturalism,Military Tradition,Fission,Alien Life
2026-10-26T04:38:51.880Z ?,Tech 10,Calendar,Currency,Gunpowder,,Electricity,Artillery,Transhumanism
2026-10-26T04:38:51.880Z ?,Tech 18,Sailing,,,,,,
2026-10-26T04:38:51.880Z SAS_SEVOPEDIA_ERA_CHART_END
```

#### Handicap chart

Compares difficulty rules and Human/AI modifiers, including growth, upkeep, research, starting units and barbarian settings. Source: [SevoPediaHandicapChart.py](/Assets/Python/Contrib/Sevopedia/SevoPediaHandicapChart.py).

```log
2026-10-26T04:38:54.199Z SAS_SEVOPEDIA_HANDICAP_CHART_BEGIN
2026-10-26T04:38:54.199Z ,Field,Rookie,Settler,Chieftain,Warlord,Noble,Prince,Monarch,Emperor,Immortal,Deity,Deity+
2026-10-26T04:38:54.199Z ?,iAIAdvancedStartPercent,60,70,80,90,100,120,140,160,180,200,220
2026-10-26T04:38:54.199Z ,iAIAttitudeChangePercent,0,10,20,30,40,50,60,70,80,90,100
2026-10-26T04:38:54.199Z ,iAIDeclareWarProb,70,80,90,100,110,120,130,140,150,160,170
2026-10-26T04:38:54.199Z ?,iAIGrowthPercent,120,115,110,105,100,95,90,85,80,75,70
2026-10-26T04:38:54.199Z ,iAIUnitSupplyPercent,100,100,100,100,100,100,100,100,100,100,100
2026-10-26T04:38:54.199Z ,iAIWarWearinessPercent,124,118,112,106,100,94,88,82,76,70,64
2026-10-26T04:38:54.200Z ,Animal Bonus (Human / AI),-30 / -30,-20 / -20,-10 / -10,0 / 0,0 / 0,0 / 0,0 / 0,0 / 0,0 / 0,0 / 0,0 / 0
2026-10-26T04:38:54.200Z ,Barbarian Bonus (Human / AI),-30 / -30,-20 / -20,-10 / -10,0 / 0,0 / 0,0 / 0,0 / 0,0 / 0,0 / 0,0 / 0,0 / 0
2026-10-26T04:38:54.200Z ,iBarbarianCityCreationProb,0,4,8,12,16,20,24,28,32,36,40
2026-10-26T04:38:54.200Z ?,Civic Upkeep Percent (Human / AI),100 / 124,100 / 118,100 / 112,100 / 106,100 / 100,100 / 94,100 / 88,100 / 82,100 / 76,100 / 70,100 / 64
2026-10-26T04:38:54.201Z ?,Construct Percent (Human / AI),100 / 120,100 / 115,100 / 110,100 / 105,100 / 100,100 / 95,100 / 90,100 / 85,100 / 80,100 / 75,100 / 70
2026-10-26T04:38:54.201Z ?,Create Percent (Human / AI),100 / 112,100 / 109,100 / 106,100 / 103,100 / 100,100 / 97,100 / 94,100 / 91,100 / 88,100 / 85,100 / 82
2026-10-26T04:38:54.201Z ?,iForeignCultureStrength,8,11,14,17,20,23,26,29,32,35,38
2026-10-26T04:38:54.201Z ?,iHealthBonus,3,3,3,2,2,2,2,2,2,2,2
2026-10-26T04:38:54.201Z ?,Inflation Percent (Human / AI),100 / 120,100 / 115,100 / 110,100 / 105,100 / 100,100 / 95,100 / 90,100 / 85,100 / 80,100 / 75,100 / 70
2026-10-26T04:38:54.201Z ?,iNumCitiesMaintenancePercent,55,60,65,70,75,80,85,90,95,100,105
2026-10-26T04:38:54.201Z ?,Research Percent (Human / AI),100 / 124,100 / 118,100 / 112,100 / 106,100 / 100,100 / 94,100 / 88,100 / 82,100 / 76,100 / 70,100 / 64
2026-10-26T04:38:54.202Z ,Starting Defense Units (Human / AI),1 / 1,1 / 1,1 / 1,1 / 1,1 / 1,1 / 1,1 / 1,1 / 1,1 / 1,1 / 1,1 / 1
2026-10-26T04:38:54.202Z ?,iStartingLocPercent,0,11,22,33,44,55,66,77,88,99,100
2026-10-26T04:38:54.202Z ,Train Percent (Human / AI),100 / 120,100 / 115,100 / 110,100 / 105,100 / 100,100 / 95,100 / 90,100 / 85,100 / 80,100 / 75,100 / 70
2026-10-26T04:38:54.202Z ,iUnownedTilesPerBarbarianUnit,67,64,61,58,55,52,49,46,43,40,37
2026-10-26T04:38:54.203Z ?,AI Free Tech 01,None,None,None,None,None,None,None,None,None,None,None
2026-10-26T04:38:54.203Z ?,Free Tech 01,None,None,None,None,None,None,None,None,None,None,None
2026-10-26T04:38:54.203Z SAS_SEVOPEDIA_HANDICAP_CHART_END
```

#### Game Speed chart

Compares speed-scaled costs/durations and calendar analysis, rather than a particular game's current research or production. Source: [SevoPediaGameSpeedChart.py](/Assets/Python/Contrib/Sevopedia/SevoPediaGameSpeedChart.py).

```log
2026-10-26T04:38:56.423Z SAS_SEVOPEDIA_GAME_SPEED_CHART_BEGIN
2026-10-26T04:38:56.423Z ,,Nitro (165 / 33) (165 / 33),Turbo (250 / 50) (250 / 50),Quick (330 / 67) (330 / 67),Normal (500 / 100) (500 / 100),Epic (750 / 150) (750 / 150),Marathon (1000 / 200) (1000 / 200),Slow (1500 / 300) (1500 / 300),Very Slow (2000 / 400) (2000 / 400)
2026-10-26T04:38:56.423Z ?,Growth ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.423Z ,Train ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.423Z ?,Construct ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.423Z ?,Create ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.423Z ?,Research ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.423Z ?,Build ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.423Z ?,Improvement ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.423Z ?,Great People ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.423Z ?,Culture ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.423Z ,Barb ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.423Z ?,Unit Discover ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.424Z ?,Golden Age ,40,60,80,100,125,200,300,400
2026-10-26T04:38:56.424Z ?,Hurry Conscript Anger ,33,50,67,100,150,200,300,400
2026-10-26T04:38:56.424Z ,Extra Free Outside Units,0,0,0,0,0,1,1,1
2026-10-26T04:38:56.424Z ,Revolt Div ,60,70,80,100,125,200,300,400
2026-10-26T04:38:56.424Z ,Num Turn Increments*,23,20,25,24,22,34,37,40
2026-10-26T04:38:56.425Z ,Inc Y 05,"80, 60, 50","40, 20, 10","45, 35, 25","10, 10, 5","30, 25, 20","16, 15, 15","10, 15, 10","10, 9, 8"
2026-10-26T04:38:56.425Z ,Inc M 01,"108000, 60000, 36000","120000, 60000, 24000","54000, 30000, 18000","60000, 30000, 12000","36000, 18000, 12000","24000, 12000, 9000","15000, 7500, 3600","13500, 6000, 3000"
2026-10-26T04:38:56.426Z ,Cal 01,+3*9k=23k,+2*10k=30k,+6*4.5k=23k,+4*5k=30k,+6*3k=32k,+10*2k=30k,+16*1250=30k,+20*1125=27500
2026-10-26T04:38:56.426Z ,Cal 17,+1*25=1470,+15*6=1880,+6*25=1265,+30*3=1880,+50*5=1700,+20*8=1398,+55*5=1431,+66*8=112
2026-10-26T04:38:56.427Z ,Cal 33,,,,,,+40*m3=2098m5,+24*m2=2064m10,+160*m3=2025
2026-10-26T04:38:56.428Z ?,S 07 (35),T58=+1015 (600),T88=+1020 (480),T116=+1015 (300),T175=+1000 (240),T263=+1020 (120),T350=+1014 (96),T525=+1000 (72),T700=+994 (48)
2026-10-26T04:38:56.429Z ?,Legendary,15000,20000,30000,45000,67500,90000,135000,180000
2026-10-26T04:38:56.429Z SAS_SEVOPEDIA_GAME_SPEED_CHART_END
```

#### World Size chart

Compares configured dimensions, ratios, player counts and world-size rules. Grid rows describe chart configuration, not a claim that every map script generates those exact dimensions. This small captured chart is included in full. Source: [SevoPediaWorldSizeChart.py](/Assets/Python/Contrib/Sevopedia/SevoPediaWorldSizeChart.py).

```log
2026-10-26T04:38:58.437Z SAS_SEVOPEDIA_WORLD_SIZE_CHART_BEGIN
2026-10-26T04:38:58.437Z ,Field,Arena,Duel,Tiny,Small,Standard,Large,Huge,SAS24,SAS32,SAS40,SAS48
2026-10-26T04:38:58.437Z ?,Usual Grid Cells W x H,14 x 10,18 x 13,23 x 17,30 x 22,39 x 28,47 x 34,60 x 42,70 x 49,80 x 56,90 x 63,99 x 70
2026-10-26T04:38:58.437Z ?,W/H Ratio*,1.4000,1.3846,1.3529,1.3636,1.3929,1.3824,1.4286,1.4286,1.4286,1.4286,1.4143
2026-10-26T04:38:58.437Z ?,Ratio to Standard*,0.128,0.214,0.358,0.604,1.000,1.463,2.308,3.141,4.103,5.192,6.346
2026-10-26T04:38:58.437Z ?,Ratio to Largest*,0.020,0.034,0.056,0.095,0.158,0.231,0.364,0.495,0.646,0.818,1.000
2026-10-26T04:38:58.437Z ?,WorldInfo Grid Cells*,140,234,391,660,1092,1598,2520,3430,4480,5670,6930
2026-10-26T04:38:58.437Z ?,Cells Per Default Player*,70,117,130,132,137,145,158,143,140,142,144
2026-10-26T04:38:58.437Z ?,Default Players,2,2,3,5,8,11,16,24,32,40,48
2026-10-26T04:38:58.437Z ?,Target Num Cities,4,4,4,5,5,6,6,7,8,9,10
2026-10-26T04:38:58.437Z ?,Free Building Bonuses,1,1,1,3,4,5,6,7,8,9,10
2026-10-26T04:38:58.437Z ?,Building Class Prereq Mod,0,0,0,25,38,50,75,100,125,150,175
2026-10-26T04:38:58.437Z ,Unit Name Modifier,50,50,40,30,20,10,0,0,0,0,0
2026-10-26T04:38:58.437Z ,Max Conscript Mod,-30,-30,-15,0,15,30,45,60,75,90,105
2026-10-26T04:38:58.437Z ?,War Weariness Mod,30,30,20,12,0,-13,-25,-35,-45,-55,-65
2026-10-26T04:38:58.437Z ,Unit Cost ,109,109,106,103,100,97,94,91,88,85,82
2026-10-26T04:38:58.437Z ,Terrain Grain Change,-1,-1,-1,0,0,1,2,2,2,2,2
2026-10-26T04:38:58.438Z ,Feature Grain Change,-1,-1,-1,0,0,1,2,2,2,2,2
2026-10-26T04:38:58.438Z ?,Research ,85,85,90,95,100,105,110,115,120,125,130
2026-10-26T04:38:58.438Z ?,Trade Profit ,70,70,63,55,48,40,33,26,19,12,5
2026-10-26T04:38:58.438Z ?,Distance Maintenance ,55,55,64,73,82,91,100,109,118,127,136
2026-10-26T04:38:58.438Z ?,Num Cities Maintenance ,42,42,38,34,30,26,22,18,14,10,6
2026-10-26T04:38:58.438Z ?,Colony Maintenance ,67,67,60,52,45,37,30,23,15,8,2
2026-10-26T04:38:58.438Z ?,Corporation Maintenance ,400,400,200,150,100,75,50,40,30,20,10
2026-10-26T04:38:58.438Z ,Num Cities Anarchy ,11,11,10,9,8,7,6,5,4,3,2
2026-10-26T04:38:58.438Z ?,Advanced Start Points Mod,100,100,100,100,100,100,100,100,100,100,100
2026-10-26T04:38:58.438Z SAS_SEVOPEDIA_WORLD_SIZE_CHART_END
```

## Before and after: shared Python log timestamps

Each pair shows the same captured messages in the same order. **Before** rows reconstruct the old message formats, rather than presenting a second recorded run.

PythonDbg **After** rows reconstruct the current `record=` fields and vote labels from captured data; PythonErr/PythonErr2 After rows remain direct captures. Only formatting and diagnostic fields change, not the recorded screen visits, glyphs or timestamps.

The PythonDbg/PythonErr2 captures are from 2026-10-20 with the matching Release DLL and the in-progress Python UI-resource draft loaded. The PythonErr startup-failure excerpt comes from a later run on 2026-10-20, before correcting the visual-resource import order. Excerpts may omit intervening rows, but their order and message data are preserved.

| File | Change | Examples |
| --- | --- | --- |
| `PythonDbg.log` | UTC prefixes plus structured screen/glyph, lifecycle, component, autoplay and WorldBuilder records | [Before](#before-pythondbglog) / [After](#after-pythondbglog) |
| `PythonErr.log` | UTC prefixes on traceback rows | [Before](#before-pythonerrlog) / [After](#after-pythonerrlog) |
| `PythonErr2.log` | UTC prefixes on module-loading/warning rows | [Before](#before-pythonerr2log) / [After](#after-pythonerr2log) |
| `app.log` | Native EXE format; no live SAS/DLL writer found | [Current format](#applog) |
| `audio.log` | Native EXE format; no live SAS/DLL writer found | [Current format](#audiolog) |
| `init.log` | Native EXE format; no live SAS/DLL writer found | [Current format](#initlog) |
| `initmgr.log` | Native EXE format; no live SAS/DLL writer found | [Current format](#initmgrlog) |
| `resmgr.log` | Native format; no live writer, only a commented-out inherited DLL writer | [Current format](#resmgrlog) |
| `xml.log` | DLL-controlled rows now use UTC + `record=` fields while preserving the native elapsed prefix | [Before](#before-xmllog) / [After](#after-xmllog) |
| `LSystem.log` | Native EXE format; no live SAS/DLL writer found | [Current format](#lsystemlog) |

### `PythonDbg.log`

A varied 30-row excerpt covers Sevopedia, glyph initialization, game/advisor screens, module loading, a WorldBuilder save and shutdown. All 17 screen notifications from the capture are included, with repeated switches retained; these are screen notifications, not individual category/tab selections.

450 of 618 nonempty rows carry timestamps in the full capture. 165 precede wrapper installation; the three later unprefixed rows are two `import failed` messages and `UnInit Python`. The final row below illustrates this direct-output limit.

#### Before: PythonDbg.log

Reconstructed old formatting of the same 30 rows:

```log
200 SCREEN TURNED ON
SCREEN OFF
275 - gold
329 - judaism
330 - judaism
3 SCREEN TURNED ON
99 SCREEN TURNED ON
load_module BugUnitPlot
load_module CvWBInterface
load_module CvWBDesc
PY:saveDesc:C:\Users\PC\Documents\My Games\Beyond the Sword\Saves\WorldBuilder\WBQuickSave, curDir:C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword
WBSave done
load_module encodings.ascii
0 SCREEN TURNED ON
9 SCREEN TURNED ON
30 SCREEN TURNED ON
0 SCREEN TURNED ON
9 SCREEN TURNED ON
30 SCREEN TURNED ON
4 SCREEN TURNED ON
14 SCREEN TURNED ON
31 SCREEN TURNED ON
18 SCREEN TURNED ON
15 SCREEN TURNED ON
votesource
secgen
SCREEN OFF
30 SCREEN TURNED ON
PY:OnUnInit
UnInit Python
```

#### After: PythonDbg.log

Current formatting reconstructed from the captured rows, with the same selection and order. The WorldBuilder and event-manager rows below apply the current source's structured record names to the captured message data; replace these reconstructed lines with a live capture after the candidate is exercised in game.

The rebuilt-DLL run also captured the direct C++ Starting Position row exactly as `utc=20261020T170806.389Z record=STARTING_POSITION_ITERATION phase=BEGIN source=AdvCiv`. It bypasses `SASPythonLogging`, so its compact `utc=` field is intentionally not rewritten into the Python wrapper's extended ISO prefix.

```log
2026-10-20T08:16:11.208Z record=SCREEN_TURNED_ON screenId=200 screenType=CvScreenEnums.SevoScreenEnums.PEDIA_MAIN
2026-10-20T08:16:23.371Z record=SCREEN_OFF previousScreenId=200 previousScreenType=CvScreenEnums.SevoScreenEnums.PEDIA_MAIN
2026-10-20T08:16:28.877Z record=FONT_ICON role=commerce type=COMMERCE_GOLD charCode=275 description=gold
2026-10-20T08:16:28.878Z record=FONT_ICON role=religion type=RELIGION_JUDAISM charCode=329 description=judaism
2026-10-20T08:16:28.878Z record=FONT_ICON role=holy-city type=RELIGION_JUDAISM charCode=330 description=judaism
2026-10-20T08:16:28.878Z record=SCREEN_TURNED_ON screenId=3 screenType=CvScreenEnums.TECH_CHOOSER
2026-10-20T08:16:29.114Z record=SCREEN_TURNED_ON screenId=99 screenType=CvScreenEnums.MAIN_INTERFACE
2026-10-20T08:16:29.363Z load_module BugUnitPlot
2026-10-20T08:16:30.925Z load_module CvWBInterface
2026-10-20T08:16:30.926Z load_module CvWBDesc
2026-10-20T08:16:30.932Z record=WB_SAVE_BEGIN file=C:\Users\PC\Documents\My Games\Beyond the Sword\Saves\WorldBuilder\WBQuickSave currentDir=C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword
2026-10-20T08:16:31.417Z record=WB_SAVE_END outcome=SUCCEEDED
2026-10-20T08:16:31.433Z load_module encodings.ascii
2026-10-20T08:16:34.331Z record=SCREEN_TURNED_ON screenId=0 screenType=CvScreenEnums.DOMESTIC_ADVISOR
2026-10-20T08:16:34.903Z record=SCREEN_TURNED_ON screenId=9 screenType=CvScreenEnums.POLICY_ADVISOR_SCREEN
2026-10-20T08:16:35.232Z record=SCREEN_TURNED_ON screenId=30 screenType=CvScreenEnums.FOREIGN_DIPLOMACY_ADVISOR
2026-10-20T08:16:36.142Z record=SCREEN_TURNED_ON screenId=0 screenType=CvScreenEnums.DOMESTIC_ADVISOR
2026-10-20T08:16:39.191Z record=SCREEN_TURNED_ON screenId=9 screenType=CvScreenEnums.POLICY_ADVISOR_SCREEN
2026-10-20T08:16:41.438Z record=SCREEN_TURNED_ON screenId=30 screenType=CvScreenEnums.FOREIGN_DIPLOMACY_ADVISOR
2026-10-20T08:16:45.207Z record=SCREEN_TURNED_ON screenId=4 screenType=CvScreenEnums.FOREIGN_ADVISOR
2026-10-20T08:16:47.863Z record=SCREEN_TURNED_ON screenId=14 screenType=CvScreenEnums.MILITARY_ADVISOR
2026-10-20T08:17:03.784Z record=SCREEN_TURNED_ON screenId=31 screenType=CvScreenEnums.WORLD_ADVISOR
2026-10-20T08:17:09.160Z record=SCREEN_TURNED_ON screenId=18 screenType=CvScreenEnums.INFO_SCREEN
2026-10-20T08:17:14.145Z record=SCREEN_TURNED_ON screenId=15 screenType=CvScreenEnums.VICTORY_SCREEN
2026-10-20T08:17:17.857Z record=VICTORY_SCREEN_VOTE_SOURCE_MATCH voteId=0
2026-10-20T08:17:17.857Z record=VICTORY_SCREEN_SECRETARY_GENERAL_MATCH voteId=0
2026-10-20T08:17:20.783Z record=SCREEN_OFF previousScreenId=15 previousScreenType=CvScreenEnums.VICTORY_SCREEN
2026-10-20T08:17:23.955Z record=SCREEN_TURNED_ON screenId=30 screenType=CvScreenEnums.FOREIGN_DIPLOMACY_ADVISOR
2026-10-20T08:30:49.505Z record=EVENT_MANAGER_UNINIT
UnInit Python
```

### `PythonErr.log`

This real startup failure was captured on 2026-10-20 while testing the visual-resource refactor: `SASVisualUtils` imported `BugConfig` first, leading through `BugCore` to `BugOptions` before `BugConfig.Handler` existed. The sample preserves that pre-fix traceback, including its original file/line references.

Direct EXE `ERR:` messages interleaved with the timestamped traceback. This excerpt retains the first three and omits subsequent repetitions; the exception's final fragments remain separate instead of being joined into a reconstructed exception row. It illustrates that direct EXE rows bypass the Python wrapper, rather than implying every error row receives a timestamp.

#### Before: PythonErr.log

Reconstructed by removing only the UTC prefixes from the same selected rows:

```log
Traceback (most recent call last):
ERR: Call function onEvent failed. Can't find module CvEventInterface
  File "<string>", line 1, in ?
ERR: Call function onEvent failed. Can't find module CvEventInterface
ERR: Call function onEvent failed. Can't find module CvEventInterface
  File "<string>", line 52, in load_module
  File "CvEventInterface", line 16, in ?
  File "<string>", line 52, in load_module
  File "BugEventManager", line 109, in ?
  File "<string>", line 52, in load_module
  File "SASVisualUtils", line 13, in ?
  File "<string>", line 52, in load_module
  File "BugConfig", line 33, in ?
  File "<string>", line 52, in load_module
  File "BugCore", line 12, in ?
  File "<string>", line 52, in load_module
  File "BugOptions", line 1270, in ?
AttributeError
:
'module' object has no attribute 'Handler'
Failed to load python module CvEventInterface.
```

#### After: PythonErr.log

Real captured rows, in their original order:

```log
2026-10-20T13:57:18.566Z Traceback (most recent call last):
ERR: Call function onEvent failed. Can't find module CvEventInterface
2026-10-20T13:57:24.356Z   File "<string>", line 1, in ?
ERR: Call function onEvent failed. Can't find module CvEventInterface
ERR: Call function onEvent failed. Can't find module CvEventInterface
2026-10-20T13:57:25.138Z   File "<string>", line 52, in load_module
2026-10-20T13:57:25.529Z   File "CvEventInterface", line 16, in ?
2026-10-20T13:57:25.921Z   File "<string>", line 52, in load_module
2026-10-20T13:57:26.106Z   File "BugEventManager", line 109, in ?
2026-10-20T13:57:26.283Z   File "<string>", line 52, in load_module
2026-10-20T13:57:26.434Z   File "SASVisualUtils", line 13, in ?
2026-10-20T13:57:26.595Z   File "<string>", line 52, in load_module
2026-10-20T13:57:26.762Z   File "BugConfig", line 33, in ?
2026-10-20T13:57:26.920Z   File "<string>", line 52, in load_module
2026-10-20T13:57:27.098Z   File "BugCore", line 12, in ?
2026-10-20T13:57:27.257Z   File "<string>", line 52, in load_module
2026-10-20T13:57:27.433Z   File "BugOptions", line 1270, in ?
2026-10-20T13:57:27.609Z AttributeError
:
'module' object has no attribute 'Handler'
Failed to load python module CvEventInterface.
```

### `PythonErr2.log`

120 of 131 nonempty rows carry timestamps in the full 2026-10-20 capture; 11 precede wrapper installation. The matched 30-row excerpt combines the 20-row warning/module-loading slice with the final 10 rows, including `PY:OnInit`.

#### Before: PythonErr2.log

Reconstructed by removing only the UTC prefixes from the same rows:

```log
load_module BugUtil
load_module ColorUtil
load_module BugInit
load_module BugPath
load_module BugConfigTracker
load_module shutil
load_module BugTypes
load_module xmllib
..\WARLORDS\ASSETS\PYTHON\SYSTEM\xmllib.py:9: DeprecationWarning: The xmllib module is obsolete.  Use xml.sax instead.
load_module configobj
load_module __future__
load_module validate
validate import failed
load_module BugOptionsScreen
load_module BugErrorOptionsTab
load_module BugOptionsTab
load_module BugHelp
load_module Popup
load_module CityUtil
load_module ReligionUtil
load_module CvAdvisorUtils
load_module SASBattleHistory
load_module InputUtil
load_module SASBillboardScale
load_module SASFastSave
load_module AIAutoPlay
load_module ChangePlayer
load_module Tester
load_module encodings.utf_8
PY:OnInit
```

#### After: PythonErr2.log

Real captured rows:

```log
2026-10-20T08:16:03.531Z load_module BugUtil
2026-10-20T08:16:03.533Z load_module ColorUtil
2026-10-20T08:16:03.533Z load_module BugInit
2026-10-20T08:16:03.534Z load_module BugPath
2026-10-20T08:16:03.535Z load_module BugConfigTracker
2026-10-20T08:16:03.536Z load_module shutil
2026-10-20T08:16:03.544Z load_module BugTypes
2026-10-20T08:16:03.545Z load_module xmllib
2026-10-20T08:16:03.560Z ..\WARLORDS\ASSETS\PYTHON\SYSTEM\xmllib.py:9: DeprecationWarning: The xmllib module is obsolete.  Use xml.sax instead.
2026-10-20T08:16:03.564Z load_module configobj
2026-10-20T08:16:03.570Z load_module __future__
2026-10-20T08:16:03.576Z load_module validate
2026-10-20T08:16:03.582Z validate import failed
2026-10-20T08:16:03.585Z load_module BugOptionsScreen
2026-10-20T08:16:03.586Z load_module BugErrorOptionsTab
2026-10-20T08:16:03.587Z load_module BugOptionsTab
2026-10-20T08:16:03.589Z load_module BugHelp
2026-10-20T08:16:03.590Z load_module Popup
2026-10-20T08:16:03.591Z load_module CityUtil
2026-10-20T08:16:03.592Z load_module ReligionUtil
2026-10-20T08:16:03.860Z load_module CvAdvisorUtils
2026-10-20T08:16:03.865Z load_module SASBattleHistory
2026-10-20T08:16:03.868Z load_module InputUtil
2026-10-20T08:16:03.869Z load_module SASBillboardScale
2026-10-20T08:16:03.870Z load_module SASFastSave
2026-10-20T08:16:03.871Z load_module AIAutoPlay
2026-10-20T08:16:03.874Z load_module ChangePlayer
2026-10-20T08:16:03.875Z load_module Tester
2026-10-20T08:16:03.876Z load_module encodings.utf_8
2026-10-20T08:16:03.877Z PY:OnInit
```

### Engine-log captured formats and SAS comparisons

The Python stream changes did not alter the native captures for `app.log`, `audio.log`, `init.log`, `initmgr.log`, `resmgr.log` and `LSystem.log`. `xml.log` now has both the real pre-change baseline and a rebuilt-DLL After capture from 2026-10-20.

The native baselines below are from the earlier 2026-10-20 run. The `xml.log` After sample is from the rebuilt Debug-opt run beginning at `20261020T170755Z`. Longer excerpts combine selected head/tail or record-family rows as noted; shorter files are shown in full.

#### `app.log`

All 4 nonempty rows in the capture.

```log
[21962.546] FBMode = FBMODE_MULTISAMPLES_2
[21963.391] CvApp::OnActivate
[22098.547] CvApp::OnDeactivate
[22844.109] CvApp::OnActivate
```

#### `audio.log`

30 of 38 nonempty rows: the first 20 and final 10.

```log
[21958.656] Audio Manager: Loading Audio Defines file XML\Audio\AudioDefines.xml...
[21958.734] Audio Manager: Successfully loaded Audio Defines file XML\Audio\AudioDefines.xml.
[21958.734] Audio Manager: Loading 2D Scripts file XML\Audio\Audio2DScripts.xml...
[21958.796] ERR: FAudioManager::GetAudioTagIndex(): Could not find string DIPLO_PETER_SFX of TagId 0
[21958.875] Audio Manager: Successfully loaded 2D scripts file XML\Audio\Audio2DScripts.xml.
[21958.875] Audio Manager: Loading 3D Scripts file XML\Audio\Audio3DScripts.xml...
[21958.984] Audio Manager: Successfully loaded 3D scripts file XML\Audio\Audio3DScripts.xml.
[21958.984] Audio Manager: Successfully loaded Soundscape scripts file XML\Audio\AudioSoundscapeScripts.xml.
[21958.984] Audio Manager: Initializing
[21958.984] Audio Manager: Attempting to initialize the audio system.
[21958.984] Audio System: Initializing Miles Audio System...
[21958.984] Audio System: redistribution directory: ..\Miles\win32
[21958.984] Audio System: Starting Miles.
[21959.000] Audio System: Opening the sound driver.
[21959.046] Audio System: CAPS: Total HW Bytes: 0
[21959.046] Audio System: CAPS: Max Contiguous Free HW Bytes: 0
[21959.046] Audio System: CAPS: Total HW 3D Buffers: 0
[21959.046] Audio System: CAPS: Static HW 3D Buffers: 0
[21959.046] Audio System: CAPS: Streaming HW 3D Buffers: 0
[21959.046] Audio System: CAPS: Total Mixing HW 3D Buffers: 1
[21959.046] Audio System: VOICES: 2D: 54
[21959.046] Audio System: VOICES: 3D: 64
[21959.046] Audio System: Initializing 2D samples...
[21959.046] Audio System: Successfully initialized 2D samples.
[21959.046] Audio System: Initializing 3D samples...
[21959.046] Audio System: Successfully initialized 3D samples.
[21959.046] Audio System: Successfully initialized base audio system.
[21959.046] Audio System: Successfully initialized Miles Audio System.
[21959.046] AudioManager: Successfully initialized the audio system.
[21959.046] AudioManager: Successfully initialized the audio manager.
```

#### `init.log`

30 of 32 nonempty rows: the first 20 and final 10.

```log
[21955.968] DBG: CIV Init
[21955.968] VERSION: App: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Civ4BeyondSword.exe
[21955.968] VERSION: Build: Thu May 29 04:28:49 2014
[21955.968] VERSION: 3.1.9.0 (128100)
[21957.312] VERSION: Mod Loaded: Mods\AdvCiv-SAS\
[21957.312] DBG: FILE Cat Init
[21958.437] DBG: Game Init
[21958.437] DBG: Multiplayer Init BEGIN
[21958.656] DBG: Multiplayer Init END
[21958.656] DBG: Audio Init
[21959.046] DBG: ArtFileMgr Init
[21959.046] DBG: Python Init
[21962.531] VERSION: CIV Version: 319
[21962.531] VERSION: Minimum Version: 319
[21962.531] VERSION: Save Version: 14223
[21962.546] DBG: Input Init
[21962.546] DBG: Engine Init
[21962.671] DBG: Checking available screen resolution
[21962.828] DBG: Validating screen resolution
[21962.828] DBG: Creating rendererer
[21963.547] DBG: Engine: Scene Lights Initialized
[21963.563] DBG: Music Start
[21963.578] DBG: Font Init
[21963.594] DBG: Begin MenuManager
[21963.594] DBG: Total Frame MS: 7694.0  FPS: 000  Min:000 Max:000 Avg:000  SampleFilter:10.000000
 Time   :   Ave  :  Min% :  Max% : Num : Profile Name
-----------------------------------------------------
--------------------------------------------------
[21983.063] DBG: Engine: Camera Initialized
[21986.672] DBG: SyncRandSeed is 21963585, MapRandSeed is 21963585
```

#### `initmgr.log`

All 6 nonempty rows in the capture.

```log
[21985.328] InitMgr elapsed time = 3.51
[21986.641] DBG: Total Frame MS: 4828.0  FPS: 000  Min:000 Max:000 Avg:000  SampleFilter:0.010000
 Time   :   Ave  :  Min% :  Max% : Num : Profile Name
-----------------------------------------------------
--------------------------------------------------
[21986.641] RELEASE build, World size=Huge
```

#### `resmgr.log`

All 3 nonempty rows in the capture.

```log
RESMGR: Texture FlagDECAL.dds failed to load
RESMGR: Texture PlayerColor01.tga failed to load
RESMGR: Texture PlayerColor02.tga failed to load
```

#### Before: xml.log

This real capture predates the DLL-row UTC/`record=` modernization described above and is retained as its matched pre-change baseline.

30 of 627 nonempty rows: the first 20 and final 10.

```log
[21958.046] Loading XML file xml\GameInfo/CIV4PlayerOptionInfos.xml
[21958.062] Load XML file xml\GameInfo/CIV4PlayerOptionInfos.xml SUCCEEDED
[21958.062] SetGlobalClassInfo (Civ4PlayerOptionInfos/PlayerOptionInfos/PlayerOptionInfo)
[21958.062] Loading XML file xml\GameInfo/CIV4GraphicOptionInfos.xml
[21958.062] Load XML file xml\GameInfo/CIV4GraphicOptionInfos.xml SUCCEEDED
[21958.062] SetGlobalClassInfo (Civ4GraphicOptionInfos/GraphicOptionInfos/GraphicOptionInfo)
[21959.625] Loading XML file xml\GlobalDefines.xml
[21959.625] Load XML file xml\GlobalDefines.xml SUCCEEDED
[21959.625] Loading XML file xml\GlobalDefinesAlt.xml
[21959.625] Load XML file xml\GlobalDefinesAlt.xml SUCCEEDED
[21959.625] Loading XML file xml\PythonCallbackDefines.xml
[21959.625] Load XML file xml\PythonCallbackDefines.xml SUCCEEDED
[21959.625] Loading XML file xml\GlobalDefines_devel.xml
[21959.625] Load XML file xml\GlobalDefines_devel.xml SUCCEEDED
[21959.625] Loading XML file xml\GlobalDefines_advc.xml
[21959.625] Load XML file xml\GlobalDefines_advc.xml SUCCEEDED
[21959.625] Loading XML file xml\GlobalDefines_advciv_sas.xml
[21959.640] Load XML file xml\GlobalDefines_advciv_sas.xml SUCCEEDED
[21959.656] Loading XML file xml\BBAI_Game_Options_GlobalDefines.xml
[21959.656] Load XML file xml\BBAI_Game_Options_GlobalDefines.xml SUCCEEDED
[21981.750] SetGlobalClassInfo (Civ4AttachableInfos/AttachableInfos/AttachableInfo)
[21981.750] Loading XML file xml\GameInfo/CIV4DiplomacyInfos.xml
[21981.766] Load XML file xml\GameInfo/CIV4DiplomacyInfos.xml SUCCEEDED
[21981.766] SetDiplomacyInfo (Civ4DiplomacyInfos/DiplomacyInfos/DiplomacyInfo)
[21981.781] Loading XML file xml\Misc/Civ4TutorialInfos.xml
[21981.781] Load XML file xml\Misc/Civ4TutorialInfos.xml SUCCEEDED
[21981.781] SetGlobalClassInfo (Civ4TutorialInfos/TutorialInfo)
[21981.781] Loading XML file xml\GameInfo/CIV4EspionageMissionInfo.xml
[21981.781] Load XML file xml\GameInfo/CIV4EspionageMissionInfo.xml SUCCEEDED
[21981.781] SetGlobalClassInfo (Civ4EspionageMissionInfo/EspionageMissionInfos/EspionageMissionInfo)
```

#### After: xml.log

SAS formats the DLL-owned rows through the narrow `logSASCiv4LegacyLogRow` helper; it does not intercept or rewrite EXE-owned rows that may share the file. The structured DLL record families cover file loading, cache activity, global/info setup and unknown XML types. `XML_CACHE` and `XML_UNKNOWN_TYPE` are source-supported even when a particular startup run does not exercise them.

The rebuilt Debug-opt capture also contains 627 nonempty rows. The identical observed row count is reassuring because the modernization restructures existing DLL messages rather than intentionally adding a second stream of startup rows, but it is not treated as a formal invariant across runs.

The selection below keeps the first 10 rows, all 10 `XML_GLOBAL_STRING_ARRAY` rows and later action/diplomacy/end-of-load rows so the main captured record families are visible.

```log
[53871.687] utc=20261020T170755.441Z record=XML_FILE_LOAD phase=BEGIN path=xml\GameInfo/CIV4PlayerOptionInfos.xml
[53871.703] utc=20261020T170755.447Z record=XML_FILE_LOAD phase=END outcome=SUCCEEDED path=xml\GameInfo/CIV4PlayerOptionInfos.xml
[53871.703] utc=20261020T170755.447Z record=XML_GLOBAL_CLASS_INFO tag=Civ4PlayerOptionInfos/PlayerOptionInfos/PlayerOptionInfo pass=1 final=1
[53871.703] utc=20261020T170755.448Z record=XML_FILE_LOAD phase=BEGIN path=xml\GameInfo/CIV4GraphicOptionInfos.xml
[53871.703] utc=20261020T170755.449Z record=XML_FILE_LOAD phase=END outcome=SUCCEEDED path=xml\GameInfo/CIV4GraphicOptionInfos.xml
[53871.703] utc=20261020T170755.449Z record=XML_GLOBAL_CLASS_INFO tag=Civ4GraphicOptionInfos/GraphicOptionInfos/GraphicOptionInfo pass=1 final=1
[53872.687] utc=20261020T170756.440Z record=XML_FILE_LOAD phase=BEGIN path=xml\GlobalDefines.xml
[53872.687] utc=20261020T170756.441Z record=XML_FILE_LOAD phase=END outcome=SUCCEEDED path=xml\GlobalDefines.xml
[53872.703] utc=20261020T170756.444Z record=XML_FILE_LOAD phase=BEGIN path=xml\GlobalDefinesAlt.xml
[53872.703] utc=20261020T170756.445Z record=XML_FILE_LOAD phase=END outcome=SUCCEEDED path=xml\GlobalDefinesAlt.xml
[53873.140] utc=20261020T170756.888Z record=XML_GLOBAL_STRING_ARRAY tag=Civ4Types/AnimationOperatorTypes/AnimationOperatorType
[53873.140] utc=20261020T170756.888Z record=XML_GLOBAL_STRING_ARRAY tag=Civ4Types/FunctionTypes/FunctionType
[53873.140] utc=20261020T170756.888Z record=XML_GLOBAL_STRING_ARRAY tag=Civ4Types/FlavorTypes/FlavorType
[53873.140] utc=20261020T170756.888Z record=XML_GLOBAL_STRING_ARRAY tag=Civ4Types/ArtStyleTypes/ArtStyleType
[53873.140] utc=20261020T170756.888Z record=XML_GLOBAL_STRING_ARRAY tag=Civ4Types/CitySizeTypes/CitySizeType
[53873.140] utc=20261020T170756.888Z record=XML_GLOBAL_STRING_ARRAY tag=Civ4Types/ContactTypes/ContactType
[53873.140] utc=20261020T170756.888Z record=XML_GLOBAL_STRING_ARRAY tag=Civ4Types/DiplomacyPowerTypes/DiplomacyPowerType
[53873.140] utc=20261020T170756.888Z record=XML_GLOBAL_STRING_ARRAY tag=Civ4Types/AutomateTypes/AutomateType
[53873.140] utc=20261020T170756.888Z record=XML_GLOBAL_STRING_ARRAY tag=Civ4Types/DirectionTypes/DirectionType
[53873.140] utc=20261020T170756.888Z record=XML_GLOBAL_STRING_ARRAY tag=Civ4Types/FootstepAudioTypes/FootstepAudioType
[53882.109] utc=20261020T170805.863Z record=XML_GLOBAL_ACTION_INFO action=SET
[53882.125] utc=20261020T170805.869Z record=XML_GLOBAL_CLASS_INFO tag=Civ4AttachableInfos/AttachableInfos/AttachableInfo pass=1 final=1
[53882.125] utc=20261020T170805.870Z record=XML_FILE_LOAD phase=BEGIN path=xml\GameInfo/CIV4DiplomacyInfos.xml
[53882.125] utc=20261020T170805.874Z record=XML_FILE_LOAD phase=END outcome=SUCCEEDED path=xml\GameInfo/CIV4DiplomacyInfos.xml
[53882.125] utc=20261020T170805.874Z record=XML_DIPLOMACY_INFO tag=Civ4DiplomacyInfos/DiplomacyInfos/DiplomacyInfo
[53882.141] utc=20261020T170805.884Z record=XML_FILE_LOAD phase=BEGIN path=xml\Misc/Civ4TutorialInfos.xml
[53882.141] utc=20261020T170805.885Z record=XML_FILE_LOAD phase=END outcome=SUCCEEDED path=xml\Misc/Civ4TutorialInfos.xml
[53882.141] utc=20261020T170805.885Z record=XML_GLOBAL_CLASS_INFO tag=Civ4TutorialInfos/TutorialInfo pass=1 final=1
[53882.141] utc=20261020T170805.886Z record=XML_FILE_LOAD phase=BEGIN path=xml\GameInfo/CIV4EspionageMissionInfo.xml
[53882.141] utc=20261020T170805.887Z record=XML_FILE_LOAD phase=END outcome=SUCCEEDED path=xml\GameInfo/CIV4EspionageMissionInfo.xml
[53882.141] utc=20261020T170805.887Z record=XML_GLOBAL_CLASS_INFO tag=Civ4EspionageMissionInfo/EspionageMissionInfos/EspionageMissionInfo pass=1 final=1
```

No `XML_CACHE` or `XML_UNKNOWN_TYPE` row occurred in this successful startup capture, so neither is illustrated in the excerpt above.

#### `LSystem.log`

30 selected rows: the first 20 plus 10 distinct later rows; repeated identical warnings are omitted.

```log
Initial System for XML/Buildings/CIV4CityLSystem.xml:
------------------------------------------------------------------------
Nodes:
	    Emergency_Overflow: [w=0.5 h=0.5] [0 art, 1 prods]
	<T> Leaf_1x1: [w=1.0 h=1.0] [39 art, 0 prods]
	    Node_2x2: [w=2.0 h=2.0] [0 art, 6 prods]
	    Node_3x1: [w=3.0 h=1.0] [0 art, 5 prods]
	    Node_6x6: [w=6.0 h=6.0] [0 art, 9 prods]
	    EONode: [w=4.0 h=4.0] [0 art, 5 prods]
	<T> Leaf_2x1: [w=2.0 h=1.0] [66 art, 0 prods]
	    Node_3x2: [w=3.0 h=2.0] [0 art, 4 prods]
	    Node_4x1: [w=4.0 h=1.0] [0 art, 4 prods]
	<T> Leaf_2x2: [w=2.0 h=2.0] [22 art, 0 prods]
	<T> Leaf_3x1: [w=3.0 h=1.0] [14 art, 0 prods]
	    Node_16x16: [w=16.0 h=16.0] [0 art, 3 prods]
	    Node_3x3: [w=3.0 h=3.0] [0 art, 3 prods]
	    Node_4x2: [w=4.0 h=2.0] [0 art, 5 prods]
	    CITY_ROOT: [w=16.0 h=16.0] [0 art, 1 prods]
	<T> Leaf_3x2: [w=3.0 h=2.0] [2 art, 0 prods]
	    Node_2x1: [w=2.0 h=1.0] [0 art, 3 prods]
	<T> BLeaf_3x2: [w=3.0 h=2.0] [55 art, 0 prods]
	<T> Leaf_Farm_1x1: [w=1.0 h=1.0] [7 art, 0 prods]
	<T> BLeaf_4x2: [w=4.0 h=2.0] [7 art, 0 prods]
------------------------------------------------------------------------
building:Art/Structures/Buildings/Public_Transportation/Public_Transportation.nif does not contain a node called SHADOW. Its shadow, if present, will be corrupt!
Failed to place goal building ART_DEF_BUILDING_LIGHTHOUSE.
building:Art/Structures/Buildings/Grocer/Grocer.nif does not contain a node called SHADOW. Its shadow, if present, will be corrupt!
building:Art/AdvCiv_SAS/Buildings/Natya_Shastra/nif/Brihadeeswarar.nif does not contain a node called SHADOW. Its shadow, if present, will be corrupt!
Failed to place goal building ART_DEF_BUILDING_HOLLYWOOD.
building:Art/Structures/Buildings/Levee/Levee.nif does not contain a node called SHADOW. Its shadow, if present, will be corrupt!
```

## Source references

### Current/local source

- [DLL logger](/CvGameCoreDLL/CvDLLLogger.cpp), [RNG initialization](/CvGameCoreDLL/CvGlobals.cpp), [shared filename builder](/CvGameCoreDLL/CvGameCoreUtils.cpp).
- [BBAI category registry and session writer](/CvGameCoreDLL/BBAILog.cpp), [cached BBAI gates](/CvGameCoreDLL/BBAILog.h), [Settler decision producers](/CvGameCoreDLL/CvUnitAI.cpp), [site selection/stored values](/CvGameCoreDLL/CvPlayerAI.cpp) and [SASGameRecord writer](/CvGameCoreDLL/SASGameRecordLog.cpp).
- UWAI producers and support:
  - [UWAIAgent](/CvGameCoreDLL/UWAIAgent.cpp), [MilitaryAnalyst](/CvGameCoreDLL/MilitaryAnalyst.cpp), [InvasionGraph](/CvGameCoreDLL/InvasionGraph.cpp), [ArmamentForecast](/CvGameCoreDLL/ArmamentForecast.cpp), [WarEvaluator](/CvGameCoreDLL/WarEvaluator.cpp) and [WarUtilityAspect](/CvGameCoreDLL/WarUtilityAspect.cpp).
  - [Shared nested mute state](/CvGameCoreDLL/UWAILogMuteState.h).
- Inherited comparison: local sibling `AdvCiv/CvGameCoreDLL/BBAILog.h`, `BBAILog.cpp`, `CvUnitAI.cpp`, `UWAIReport.cpp` and `UWAIAgent.cpp` (AdvCiv 1.14); [KI#505.3](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-505.3) preserves the SAS investigation of the retired report path.
- [BUG generic logging](/Assets/Python/BUG/BugUtil.py), [shared SAS timestamp/record writer](/Assets/Python/SASPythonLogging.py), [CvUtil structured-record facade](/Assets/Python/CvUtil.py), [OOS logger](/Assets/Python/Contrib/OOSLogger.py) and [Autolog](/Assets/Python/Contrib/autolog.py).
- [Inherited-log row formatter](/CvGameCoreDLL/CvGameCoreUtils.cpp), [XML log producer](/CvGameCoreDLL/CvXMLLoadUtility.cpp) and [XML setup/cache producers](/CvGameCoreDLL/CvXMLLoadUtilitySet.cpp).
- [StatusDump event manager](/Assets/Python/Contrib/StatusDumpEventManager.py), [older StatusDump helper](/Assets/Python/Contrib/StatusDump.py), [StatusDump config](/Assets/Config/StatusDump.xml).
- [Starting-position iteration](/CvGameCoreDLL/StartingPositionIteration.cpp), [internal profiler](/CvGameCoreDLL/FProfiler.cpp), [TSC profiler](/CvGameCoreDLL/TSCProfiler.cpp).
- [Inherited AdvCiv manual](/_0_Common_Docs/AdvCiv_Base_Doc/manual.txt), especially message-control logging and multiplayer debugging.

### Historical / external provenance

- CivFanatics, 2005-10-28: [launch-era report documenting `PythonDbg.log`, `PythonErr.log` and `PythonErr2.log`](https://forums.civfanatics.com/threads/possible-python-error-temp-solution.134453/).
- CivFanatics, 2005-11-15 onward: [eotinb's original Autolog thread](https://forums.civfanatics.com/threads/mod-log-changes.141164/), explicitly describing a succession-game/note-taking journal and distinguishing it from debug/error logs.
- CivFanatics, 2009-11-05: [Better BTS AI 0.82 decision-logging documentation](https://forums.civfanatics.com/threads/bts-in-game-debug-mode.279903/), including `BBAI.log`, `/DLOG_AI` and interpretation of its timing prefix.
- CivFanatics, 2009-11-15: [BUG 4.2 / BULL 1.0 release](https://forums.civfanatics.com/threads/download-bug-and-bat-here.274636/).
- CivFanatics, 2019-03-18: [Kek-Mod 0.23 release](https://forums.civfanatics.com/threads/modmod-kek-mod.563377/) included OOSLogger and credited the idea to Fall from Heaven 2 by Kael. The same changelog lists OOSLogger fixes from AdvCiv in 0.25 (2019-07-16).
- AdvCiv Git, 2019-03-27: [OOSLogger merge from Kek-Mod](https://github.com/f1rpo/AdvCiv/commit/81c89a9e0511aa58630f7821fdc9287ecffa8edf).
- AdvCiv Git, 2019-08-27: [`CvDLLLogger` introduction](https://github.com/f1rpo/AdvCiv/commit/553b1a0f8d92b00f09f64f2ee1ecb4d696ebe43e), encapsulating the message-control log.
- AdvCiv Git, 2019-11-05: [TSC profiler import from We the People](https://github.com/f1rpo/AdvCiv/commit/031365f32f6d71519e2fd09c6f6e963ecbef4bd3).
- AdvCiv Git, 2020-05-27: [initial Starting Position Iteration implementation](https://github.com/f1rpo/AdvCiv/commit/a70e4ce3a1db01c51da7fa370a706d8784191b38).
- AdvCiv Git, 2020-11-18: [AsyncRand logging fix](https://github.com/f1rpo/AdvCiv/commit/64e3335495dcd86aebf5068bf8903c0a1f83c508).
- Public RoM-AND/C2C-derived source provides matching producers for `Checksum.log`, `MLF.log`, `XmlDependencyTypes.log`, `CvGlobals_logInfoTypeMap.log` and MLF enumeration diagnostics; these establish external lineage but do not prove which mod produced the user's local copies.

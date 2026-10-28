# SAS runtime recorder revisions

`SASRuntimeStatus.json` describes the latest observed state; its companion `SASRuntimeHistory_*.jsonl` retains timed activity transitions. Both report the same compiled `SAS_RUNTIME_REVISION` as `revision`, identifying their recorder implementation independently of SASGameRecord's revision.

Increment once per commit changing the loaded runtime recorder, its interfaces, configuration, call sites or shared runtime services, including implementation comments/provenance. Keep one pending revision throughout drafting and amend cycles.

Pure CI/checker, test, documentation and historical-example maintenance does not change the loaded recorder and does not require an increment or DLL rebuild.

Add a latest-first entry explaining the behavior and rationale. The diagnostics check requires consecutive history entries, agreement with the compiled value, and exactly one increment per recognized implementation commit. Shared-code detection uses changed runtime symbols; review unusual refactors manually because CI cannot infer every dependency.

## History

### Revision 15 - SAS practical 6697

- **Date:** 2026-10-28
- **Git commit:** pending
- **Change:** Separate human end-turn readiness from player-turn wall time and record compact pre-end-turn order context without per-frame unit scans.
  - The existing `updateTestEndTurn` UI boundary now reports when the inherited end-turn message becomes active or is revoked because new orderable work appears. Runtime measures only those ready-message intervals; `HUMAN_INPUT` remains broader wall time including thinking, popups and screens.
  - Accepted `CONTROL_ENDTURN` / `CONTROL_ENDTURN_ALT` / `CONTROL_FORCEENDTURN` requests capture one `end_turn_context` row before `sendTurnComplete`.
    - It includes logical and UI-ready orderable groups/units plus busy, automated, auto-ready, queued-mission, waiting, HOLD and SLEEP state. Orderable unit counts include only movable units inside qualifying groups; the other state categories describe group membership and can overlap rather than forming a partition.
    - The row stores the engine control ID/name but `physicalInput=NOT_OBSERVED`; Enter and the end-turn widget can share `CONTROL_FORCEENDTURN`.
  - Actual `MISSION_SKIP` application increments one in-memory per-player-turn counter. HOLD is never treated as proof of Skip because AI/gameplay code can create HOLD through other paths. No per-mission history row is emitted.
  - Completed sequential `player_turn_summary` player entries now retain `readyUiMilliseconds`, `skipOrdersApplied` and final compact readiness counts. This gives AI turns compact end-state context too without tracing every AI mission.
  - Current status exposes the live ready interval, current Skip count and latest accepted-request summary. An accepted request closes the user's ready-wait interval even if the EXE leaves its visual end-turn message up until deactivation.
  - Readiness closes at player-turn ending even if no local accepted-request hook ran; cleanup time is excluded. A loaded turn whose activation was not observed has no readiness/Skip measurements until the next observed activation.

### Revision 14 - SAS practical 6696

- **Date:** 2026-10-28
- **Git commit:** `59f88590b4b2f03174ac1dc3d5fda6c6d48fed9f`
- **Change:** Observe confirmed screenshot files externally and correlate them with the matching Runtime process/session context without treating a Print Screen request as proof that capture succeeded.
  - With `SAS_RUNTIME_STATUS_ON=1`, the independent default-off `SAS_RUNTIME_SCREENSHOT_WATCH_ON=1` launches adjacent `Assets/SASRuntimeScreenshotObserver.ps1` through the already attached exit observer after exact process/start identity is confirmed; no additional game input, screenshot request or directory polling is introduced.
  - The watcher derives Civ4's native user `ScreenShots` directory from the target executable folder and Documents/My Games convention used by the engine diagnostics. It ignores pre-existing files and records only future `.jpg`/`.jpeg`/`.png`/`.bmp` create/change/rename bursts after short per-file coalescing.
  - `SASRuntimeScreenshotWatch_<process-start UTC>_<PID>.json` reports observer state/counters, while `SASRuntimeScreenshots_<process-start UTC>_<PID>.jsonl` stores confirmed filename, observation/file times, size, width/height with explicit reader/format availability, and bounded SHA-256 evidence. Image bytes are never copied into diagnostic output.
  - Each screenshot row snapshots the matching `SASRuntimeStatus.json` context available at the first observed file event: session/game turn/active player/activity plus available player-turn, WorldBuilder, Civilopedia and popup context.
    - The row also retains status age and explicitly states that the writer/capture request/exact screen are not observed, so stale status or an external capture tool cannot be mistaken for a proven in-game Print Screen completion.
  - The exit receipt records screenshot-observer launch PID/error and expected companion filenames but does not duplicate screenshot rows. `LAUNCHED` proves process creation only; the independent watcher state distinguishes WATCHING, missing screenshot directory, I/O failure and target exit.
    - Runtime off launches no observer; screenshot off launches no screenshot child and writes no screenshot files while ordinary exit observation remains available.

### Revision 13 - SAS practical 6695

- **Date:** 2026-10-28
- **Git commit:** `12251f88fda55a5994d04bc20d88011376228bd2`
- **Change:** Add native sequential player-turn timing for external Runtime diagnostics without turning every player boundary into a disk-write event.
  - `CvPlayer::setTurnActive` supplies authoritative activation, main active interval and ending boundaries. Current JSON distinguishes the actually processed player/team/civilization and `AI_MOVES`, `HUMAN_INPUT` or `ENDING` phase from the existing `activePlayer`, which remains UI ownership.
  - Every measured player is retained in memory; the authoritative completed-game-turn boundary appends one `player_turn_summary` JSONL row containing fast and slow players plus activation/main/ending durations. Missing/interrupted boundaries, including a load that resumes after activation, set `complete=0` rather than fabricating timing.
    - A crash before turn completion can therefore lose the in-memory current-turn summary.
  - `SAS_RUNTIME_PLAYER_TURN_LIVE_THRESHOLD_MS=3000` and `SAS_RUNTIME_PLAYER_TURN_LIVE_REFRESH_MS=3000` optionally refresh the overwrite-only JSON for a slow AI/HUMAN_DISABLED/barbarian turn.
    - Fast players cause no timing-progress writes; a player context published by any Runtime event receives one clearing update when it ends.
    - Threshold `-1` disables live refresh while preserving the summary; refresh `0` publishes only the first crossing.
  - Live progress remains best effort: one cheap check runs from the ordinary game-update loop, so a single uninterrupted blocking AI call cannot update the file until control returns. An unchanged snapshot is therefore not a hang detector.
  - Simultaneous-player/team modes report `playerTurnTimingMode=SIMULTANEOUS` but intentionally emit no sequential timing summary; overlapping active turns do not identify one executing civilization.

### Revision 12 - SAS practical 6690

- **Date:** 2026-10-26
- **Git commit:** `9e6e527431b576ecc8622f7230eacb8084b0e9ff`
- **Change:** Add an optional external live-source observer for mod-source/configuration disk edits while Runtime diagnostics are enabled, without claiming that Civ4 reloaded or executed the changed files.
  - `SAS_RUNTIME_SOURCE_WATCH_ON=1` launches adjacent `Assets/SASRuntimeSourceObserver.ps1`; the shipped default is 0, and ordinary Runtime status does not start the watcher.
  - The companion uses recursive `FileSystemWatcher` events for Python/XML/BUG Config, PrivateMaps scripts/scenarios, Resource themes, mod Settings and mod-root INI files, coalesces rapid save/rename bursts per path, then records mod-relative path, observed actions/times, final presence/size/write time and bounded SHA-256 evidence. File contents are never copied.
  - `SASRuntimeSourceWatch_<process-start UTC>_<PID>.json` reports watcher state/counters; `SASRuntimeSourceChanges_<process-start UTC>_<PID>.jsonl` contains bounded change rows. Each row states `engineReloadState=NOT_OBSERVED`: a disk edit is not proof that embedded Python/XML reloaded successfully. C++ is deliberately excluded because editing source never replaces the loaded DLL.
  - Process creation time, per-run/root ownership and bounded pending/row/fingerprint limits protect identity and overhead. The watcher is event-driven rather than a periodic source-tree scan/hash; state JSON rewrites only when watcher state/counters change.
  - A single post-subscription process check covers an exit between enabling notifications and registering the exit handler, preventing an orphaned watcher without periodic process polling. Windows fixtures also verify unchanged-content saves and exact final file hashes.
  - Both external observers record startup host metadata through `Assets/SASRuntimeObserverEnvironment.ps1`; the exit receipt also records C# listener compilation result/duration. This replaces the manually maintained host-version table without repeating metadata in every source event.
  - Shared cached binary context also retains the loaded PE Large Address Aware flag for EXE diagnostics; this describes address-space eligibility rather than an integer-size or allocation guarantee.
  - Current Runtime JSON exposes whether source watching is enabled plus observer PID/launch error and companion filenames. Missing/blocked PowerShell, filesystem-watcher overflow or I/O failure remains explicit rather than being interpreted as no edits.

### Revision 11 - SAS practical 6689

- **Date:** 2026-10-26
- **Git commit:** `7fb4c4308559b1d658f1ea0d8b6b4c19e6bd95da`
- **Change:** Observe the captured Microsoft Visual C++ Runtime Library error and Civ4 Program Execution Problem dump-choice dialogs while Civ4 remains alive, complementing the process-exit wait. PowerShell compiles the adjacent `Assets/SASRuntimeDialogObserver.cs` through the installed .NET tooling; the game DLL does not compile or load this managed listener.
  - A process-filtered, out-of-context WinEvent listener with an initial window scan detects recognized visible dialogs and later hide/destroy observations. It reads only bounded standard text from the recognized target dialog and never clicks or dismisses it.
    - The dump reporter’s known Edit 1004 is guarded by its message and three dump-choice buttons; ordinary popups/assertions are excluded.
  - The independent per-run JSON reports listener availability, failure-dialog count/latest evidence and dropped events without changing process liveness. Times describe observation, including already-visible dialogs, rather than claiming the exact original fault time.
  - The final exit history row retains the bounded dialog summary after Civ4 stops; live observations do not compete with the native history writer. A transient per-run/root ownership lock prevents duplicate helpers from replacing captured evidence with empty startup state.
  - Hook/compilation failure retains the original exit-observation fallback. A missing dialog observation does not prove health: other failure dialogs, localization differences, hangs and silent exits remain distinct cases. Runtime-off still launches no helper; enabled observation adds managed startup/event handling, with no periodic game/UI polling.

### Revision 10 - SAS practical 6688

- **Date:** 2026-10-26
- **Git commit:** `def6878daa1cc7115e13e173c4de2bf967e90e84`
- **Change:** Enabled runtime diagnostics launch the adjacent `Assets/SASRuntimeExitObserver.ps1` as a hidden, same-user Windows PowerShell process. It waits for the matching process handle and records final exit time/code even when Civ4 cannot execute its shutdown hooks.
  - The current JSON exposes the launched observer PID and Win32 launch error; launch success does not prove attachment. The separate `SASRuntimeExit_<process-start UTC>_<PID>.json` first confirms handle attachment with WAITING, then records EXITED and the final result independently of current-status readability.
  - After an observed exit, `exitObservation` records signed/hex exit code, UTC and history-append result. `lastInProcessUpdatedUtc` preserves the last game-owned observation.
  - A compact `process_exit` history row preserves the final process evidence and last observed activity/turn. Nonzero codes do not by themselves distinguish a crash from external termination or identify the faulty code.
  - Creation-time checks prevent PID-reuse mistakes; an exclusive writer lock and same-handle identity check protect newer game snapshots. Optional diagnostics being off launches no helper. Root migrations can start an observer for each distinct published root; retired snapshots are ignored.
  - This addresses stale RUNNING reports observed after Python-reload crashes, not Python-reload safety. Missing/blocked PowerShell, failure before attachment, observer termination or failed I/O can still leave stale output; readers must retain direct process checks.

### Revision 9 - SAS practical 6686

- **Date:** 2026-10-26
- **Git commit:** `86385960a026023db376c265eebfa794af77ba07`
- **Change:** Normalize contributor credits in runtime implementation comments by removing the optional reviewer-role label; retain existing author attribution. The revision advances under the implementation-comment policy; recorder behavior and output fields are unchanged.

### Revision 8 - SAS practical 6680

- **Date:** 2026-10-24
- **Git commit:** `7030fbbe4fe8b48f2b548c6c54daeb4a9c118b34`
- **Change:** Add cached source/branch provenance to the standalone runtime view so external agents can interpret a practical count correctly when Civ4 is running from a feature, reproducer or diverged branch.
  - Current `SASRuntimeStatus.json` and the JSONL `run` record add `sourceIdentity` with exact current commit/count/branch, locally known default commit/count, merge-base commit/count, branch relation, current-only/default-only commit counts, combined/staged/unstaged tracked runtime-code/rules fingerprints, and the number of staged/unstaged per-file diff entries available in the shared cache.
  - Diagnostic ancestry/patch resolution stays behind the runtime-status enable gate in a separate `ModName` cache, so basic version UI does not trigger it; enabled transition updates do not repeatedly invoke Git. No fetch is attempted, and shallow/missing default ancestry remains explicit.
  - Per-file dirty-layer rows remain in SGR/build provenance rather than the frequently rewritten current-status JSON, keeping runtime status compact while still identifying the exact aggregate tested state.
  - Player-facing source/version presentation is unchanged; branch topology is development/agent evidence rather than normal gameplay UI.

### Revision 7 - SAS practical 6676

- **Date:** 2026-10-23
- **Git commit:** `a9f16ef4a2a969ced13de011b19f795938977705`
- **Change:** Expose native ButtonPopup interaction as a compact event-driven wait state without turning UI prompts into gameplay/activity intervals.
  - `BUTTON_POPUP_FOCUSED` begins `buttonPopupAwaitingInteraction=1` only from `CvDLLButtonPopup::OnFocus`, after popup-specific stale/cancellation checks. Focus is stronger evidence than merely queueing/launching a popup: the EXE has reached its native focus/interaction callback for that ButtonPopup. It is not claimed as an exact rendered-frame timestamp.
    - The snapshot/history retain fixed `buttonPopupType`/numeric ID, active player and focus time. No popup body, edit-box text, player-entered name/password/mail/server value, or arbitrary Python text is recorded.
    - `BUTTONPOPUP_PYTHON_SCREEN` is an EXE queue shim for a full Python screen rather than a displayed native popup and therefore is not claimed as covered by this focus state.
  - `BUTTON_POPUP_RESPONDED` closes the observed wait at the generic native button-return boundary and retains the numeric response button. `BUTTON_POPUP_CANCELLED` is reserved for an already-focused popup that the EXE/UI marks stale before interaction.
    - Resolution matches the opaque in-process popup identity while a prompt is tracked, so an old/dying popup response or cancellation cannot clear a newer prompt of the same type. A response can still be recorded without prior focus when no prompt currently owns the wait state.
    - Internal Alt-execute requeue is not mislabeled as a player choice/cancel; the replacement popup's focus refreshes the wait identity.
    - A response is evidence that a button return reached native dispatch, not that the downstream gameplay action succeeded; realized gameplay remains separate evidence.
    - A response without observed focus has no focus timestamp; it cannot inherit a previously resolved popup's time. Shared popup-type naming lives with the common game utilities rather than either recorder.
  - Popup observations are transition rows with `intervalStarted=0`. Waiting during ordinary play, autoplay or an end-game prompt preserves the underlying activity clock instead of introducing an `AWAITING_POPUP` activity that would fragment coarse timing.
  - Reset/new-session clears popup context. After a resolved popup, type/player/resolution remain as the last observed interaction until the next popup or reset, analogous to retained Civilopedia context. No frame/update polling or popup-queue scans are added.

### Revision 6 - SAS practical 6660

- **Date:** 2026-10-21
- **Git commit:** `73fba8f1cf408ebac14cf28c170fbb9090d6f1b7`
- **Change:** Rename the enable setting to `SAS_RUNTIME_STATUS_ON` with the GlobalDefine naming review (KI#1001.2). Its default, cached enable check and runtime observations are unchanged.

### Revision 5 - SAS practical 6646

- **Date:** 2026-10-19
- **Git commit:** `61c86a8949e29f1c6f0cd0379c563c70596d54ca`
- **Change:** Add stronger event-driven menu and initialization observations where the Python/UI interfaces expose state, while keeping unavailable EXE presentation facts explicitly unresolved.
  - `MAIN_MENU_STATE_OBSERVED` records the first positive `CyInterface().isInMainMenu()` sample in a no-game interval, but only when an explicit menu-capable Python screen entry point already runs. `mainMenuStateObservedUtc` therefore proves menu state at that callback; it is not claimed as the initial rendered-menu arrival time.
  - Civilopedia visibility distinguishes `MAIN_MENU` and `IN_GAME` context in both the current JSON and history. The top-level entry covers standard Civilopedia/Sevopedia; Sevopedia's shared screen-creation hook also covers direct in-game page links.
    - Show observations require an active screen. Hides use the EXE's no-screens notification, with an inactive-screen check after close handlers as another observation path; duplicate hides are suppressed.
      - Real menu/game tests retained `civilopediaVisible=1` after closing Sevopedia: `PythonDbg.log` recorded screen `200` followed by `SCREEN OFF`, but the `onClose` path supplied no hide row. The existing `toggleSetNoScreens()` callback closes this gap without frame polling or assuming when `isActive()` changes during dispatch.
    - `civilopediaVisible` and `civilopediaContext` keep this overlay separate from the underlying activity clock.
    - `civilopediaActivePlayer` and `civilopediaActiveCivilization` identify the in-game UI owner at observation time, not the page or 3D model being previewed. Main-menu observations use `-1` for both; hide rows retain the last observed context until reset/new-session clears it.
  - BUG's EXE-driven `PreGameStart` extension records `PYTHON_PRE_GAME_START` once per current session as `pythonPreGameStartUtc`. This is a Python initialization boundary for new/load flows, not proof that any loading/slideshow frame was rendered, and its ordering relative to native-ready is not assumed for every load path.
  - These are observation-only timeline rows: they preserve the underlying `NO_GAME`, creation/load or play activity interval instead of inventing a menu-overlay/loading-screen activity. Python checks the cached native enable flag before diagnostic-only interface/screen queries; the samples occur only on existing callbacks, without frame polling.
  - The exact initial main-menu frame, exact loading-frame visibility and the EXE-owned main-menu Exit button remain unavailable through the reviewed SDK/Python callbacks. Continue to report scene/loading requests and orderly teardown as separate evidence rather than inferring those missing facts.

- **Follow-up, 2026-10-19:** The menu/loading-visibility and EXE main-menu Exit-button investigations were closed for the current callback-based recorder after live tests and SDK/Python review. Neither missing feature was added. (ChatGPT-5.6-Sol investigation, reviewed with Codex.)
  - **Initial menu/loading visibility:** reviewed getters select assets, `isInMainMenu()` samples state, and `PreGameStart` marks initialization; no callback establishing the first displayed frame was found. Polling or more asset observations would still not establish that render boundary.
    - Proactively calling `getSoundtrack()` would also change SAS's shuffle bag/ASyncRand state, while merely observing its existing call would add another asset-request proxy.
  - **EXE main-menu Exit button:** its handler is inside the EXE, unlike the in-game `CvDLLButtonPopup::OnOkClicked` path. The real button test produced orderly teardown without a Windows close-request or dedicated UI-request row.
    - Generic destruction/quit/uninitialization observations identify shutdown, not its originating button; additional hooks would not reliably distinguish that source. Existing requests, state samples and teardown remain separate evidence.

### Revision 4 - SAS practical 6645

- **Date:** 2026-10-19
- **Git commit:** `5174aae5d8ec4b2172ca4a8bd31e08f6c4429700`
- **Change:** Observe Windows close messages as distinct best-effort exit-request evidence without replacing Civ4's window procedure.
  - When runtime status is enabled, observe both sent messages (`WH_CALLWNDPROC`) and queue removal (`WH_GETMESSAGE`) on the window's thread.
    - Before a visible window is available, arm on the lifecycle caller's thread and bind a later top-level close target; later lifecycle callbacks can retarget the hooks.
    - Disabled status performs no window enumeration or hook installation; enabled ordinary messages incur only short filters.
  - Distinguish `WM_CLOSE` from the earlier `WM_SYSCOMMAND` / `SC_CLOSE` command.
    - `WINDOW_CLOSE_MESSAGE_OBSERVED` and `WINDOW_CLOSE_COMMAND_OBSERVED` identify sent-message observations; their `DEQUEUED` counterparts identify removal from the message queue, before the EXE decides whether to dispatch or handle them directly.
    - They do not identify red-X versus Alt+F4/automation, and explicit Civ4 UI exit requests remain separate evidence.
  - The first real red-cross/autoplay run exited with the observer armed but no close row. The expanded Windows fixture reproduced a blind spot in the original direct-`SendMessage` test: posted close commands need queue observation even when subsequently dispatched.
    - Ignore non-removing peeks, and leave retrieved messages unchanged. The first run establishes missing evidence, not which message the EXE handled.
    - The rebuilt autoplay/red-cross retest recorded a sent `SC_CLOSE` command, followed by orderly teardown, without a `WM_CLOSE` observation. Queue handling remains separately covered by the Windows fixture.
    - Initial-main-menu red cross also recorded `SC_CLOSE`; in-game Exit to Desktop recorded its explicit UI request instead. The tested EXE main-menu Exit button reached orderly teardown without a close-command/message or dedicated UI-request row; absence of those rows alone does not identify that button.
  - A close-message observation enters the existing `EXIT_REQUESTED` activity when no exit request is already active; when an explicit UI exit already started that activity, the close message is retained as an observation-only transition instead of restarting the interval.
  - The fixed snapshot exposes whether close observation was successfully armed in the process; `windowCloseRequestObservedUtc` retains the latest observed request time for either message or command. Orderly `CvGame` destruction publishes its final state before unhooking; abrupt process termination remains identifiable only through stale process identity, not a fabricated crash cause.
  - Both hooks chain through `CallNextHookEx`; the recorder neither changes queue messages nor replaces Civ4's window procedure. Window discovery/rearming remains confined to non-turn lifecycle observations. Roll back partial installation, and release both hooks after the final orderly snapshot.

### Revision 3 - SAS practical 6644

- **Date:** 2026-10-19
- **Git commit:** `39a7ad075bd95ce94f6bb683b3436da693ec4033`
- **Change:** Make each per-process JSONL timeline more useful as a standalone archive while removing repeated constant identity from every transition.
  - Add one typed `run` record with process start/PID, DLL-load UTC and full loaded-DLL identity. Transition records retain the recorder revision and compact run ID so a copied/grepped line still identifies its source run without repeating the full identity object.
  - Add one typed `session` record for each ready new/load session, normally before its first ready transition, with session timestamps/counters, ready-game turn/active-player IDs, map/game configuration and known loaded-save checkpoint evidence. Capture that context once so a later retry preserves the original ready observation even after the game advances or resets.
  - Keep `transition` records focused on timed activity boundaries and presentation observations. Record prior status/history publication-failure counters on archival rows so recovered evidence discloses earlier gaps.
  - A failed run-metadata publication does not block later transitions. Open/partial failures retry on later updates; a fully written row with an unconfirmed close is not duplicated, and failure counters disclose the uncertainty. Root migration treats such possibly written rows as evidence too, so typed records remain together when `CvAltRoot` takes over.

### Revision 2 - SAS practical 6643

- **Date:** 2026-10-18
- **Git commit:** `e58d41b6e8a6e6fe69993c4b8aa056f8679d82bd`
- **Change:** Add event-driven presentation/lifecycle observations without frame polling or side-effectful diagnostic queries.
  - Record the EXE's existing main-menu scene and loading-screen asset requests as explicitly named evidence, without treating either request as proof that a rendered frame reached the user.
  - Distinguish native WorldBuilder mode from the Python WorldBuilder screen; time active editor intervals as their own coarse activity while recording screen show/hide separately and ignoring Advanced Start's reuse of the same Python screen.
  - Restore `PLAYING` when `GAMESTATE_OVER` transitions to `GAMESTATE_EXTENDED`, so "Just one more turn" does not leave external status stuck at `GAME_ENDED`.
  - Preserve whole activity durations when recording presentation-only observations. Timeline rows distinguish interval starts from observations inside an existing interval; a repeated activity label no longer implies that its clock restarted or that another completed duration should be counted.
  - Filter Advanced Start inside the cached native gate, retaining real screen observations even when native mode is reported later. Pending menu/exit requests remain authoritative while editor callbacks finish arriving.

### Revision 1 - SAS practical 6642

- **Date:** 2026-10-18
- **Git commit:** `b0ddbda713d15d04f229a377af1d0c392e886351`
- **Change:** Publish optional current-state observations and a per-process activity timeline so agents can inspect creation, loading and autoplay while Civ4 remains open, with timing and loaded-DLL identity to interpret those observations.
  - Use one implementation revision across both outputs, replacing the draft's separate layout `schema` labels. The number refers to this history; it does not select compatibility branches or identify the Windows process.
  - Keep snapshot and activity serials as independent per-process counters: snapshots can advance each completed turn, while activity serials connect transitions with the snapshot that describes them.
  - Disclose publication failures and retain the last observed state without claiming that an absent process proves a crash or that a shutdown observation proves successful process termination.

## Maintenance template

Increment compiled `SAS_RUNTIME_REVISION` once for the next qualifying commit and prepend one entry:

```markdown
### Revision N - SAS practical XXXX

- **Date:** YYYY-MM-DD
- **Git commit:** pending
- **Change:** Explain the runtime-recorder change and why it matters to readers of its observations.
```

Keep only the latest entry's Git commit as `pending` in its introducing commit; finalize it in the next commit, even without another recorder change. Reconcile hashes and practical numbers after an amend, rebase or squash; ordinary merges preserve the original commit identities.

Do not put the current commit's own SHA into its entry: editing the document would change that SHA again. Exact loaded-DLL identity remains separate evidence in both runtime files.

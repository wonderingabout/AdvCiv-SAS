// AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
// (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

#include "CvGameCoreDLL.h" // <!-- custom: Required first for this DLL's precompiled game/Win32 declarations. (GPT-6.1-Sol) -->
#include "CvGameCoreUtils.h" // <!-- custom: Declares typed status reasons plus the shared clocks and user-root services used by this publisher. (GPT-6.1-Sol) -->
// <!-- custom: Keep this publisher separate from the BBAI/SASGameRecord writer so its standalone I/O fixture has explicit gameplay dependencies. (GPT-6.1-Sol) -->
#include "CvGame.h" // <!-- custom: Game/autoplay/save-checkpoint getters require the complete CvGame type, not a forward declaration. (GPT-6.1-Sol) -->
#include "CvPlayerAI.h" // <!-- custom: GET_PLAYER returns CvPlayerAI; its complete type provides the active player civilization for UI context, distinct from the previewed entry. (GPT-6.1-Sol) -->
#include "CvSelectionGroupAI.h" // <!-- custom: The private readiness scan inspects selection groups; the iterator returns CvSelectionGroupAI, requiring its complete type. (GPT-6.1-Sol) -->
#include "CvUnit.h" // <!-- custom: Count individually movable units inside qualifying groups rather than assuming every group member can move. (GPT-6.1-Sol) -->
#include "CvMap.h" // <!-- custom: Map dimension/world-size getters require the complete CvMap type. (GPT-6.1-Sol) -->

// <!-- custom: Readiness counts and scanning are private Runtime aggregation, not a shared gameplay utility.
// Keep them here because only this recorder consumes them; public hooks in CvGameCoreUtils.h let gameplay report existing boundaries without exposing this data layout.
// The enabled Runtime call chain gates every scan, so disabled diagnostics do not traverse groups or units. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
struct SASRuntimeTurnReadinessSnapshot
{
	SASRuntimeTurnReadinessSnapshot();
	int iGroups, iUnits;
	int iOrderableGroups, iOrderableUnits;
	int iUIReadyGroups, iUIReadyUnits;
	int iBusyGroups, iBusyUnits;
	int iAutomatedGroups, iAutomatedUnits;
	int iAutoReadyGroups, iAutoReadyUnits;
	int iMissionGroups, iMissionUnits;
	int iWaitingGroups, iWaitingUnits;
	int iHoldGroups, iHoldUnits;
	int iSleepGroups, iSleepUnits;
};
SASRuntimeTurnReadinessSnapshot::SASRuntimeTurnReadinessSnapshot()
: iGroups(0), iUnits(0), iOrderableGroups(0), iOrderableUnits(0),
  iUIReadyGroups(0), iUIReadyUnits(0), iBusyGroups(0), iBusyUnits(0),
  iAutomatedGroups(0), iAutomatedUnits(0), iAutoReadyGroups(0), iAutoReadyUnits(0),
  iMissionGroups(0), iMissionUnits(0), iWaitingGroups(0), iWaitingUnits(0),
  iHoldGroups(0), iHoldUnits(0), iSleepGroups(0), iSleepUnits(0)
{}

// <!-- custom: Runtime readiness scans only at accepted end-turn / player-turn-end boundaries, never per frame.
// `bUIAnyMove` reproduces updateTestEndTurn's selected-unit/cycling rule for the UI-specific ready count; the logical orderable count always uses canAnyMove so partially movable groups are not hidden.
// HOLD and SLEEP are descriptive current activities only.
// Explicit Skip is counted separately at the actual MISSION_SKIP application point because HOLD has other producers. (ChatGPT-5.6-Sol) -->
static void getSASRuntimeTurnReadinessSnapshot(PlayerTypes ePlayer, bool bUIAnyMove, SASRuntimeTurnReadinessSnapshot& kSnapshot)
{
	kSnapshot = SASRuntimeTurnReadinessSnapshot();
	if (ePlayer == NO_PLAYER)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	FOR_EACH_GROUP(pGroup, kPlayer)
	{
		int const iUnits = pGroup->getNumUnits();
		kSnapshot.iGroups++;
		kSnapshot.iUnits += iUnits;
		bool const bAutomated = pGroup->isAutomated();
		// <!-- custom: Skip orderability work for automated groups; the common any-move UI rule equals logical orderability, so reuse that result rather than traverse the group twice. (GPT-6.1-Sol) -->
		bool const bOrderable = !bAutomated && pGroup->readyToMove(true);
		bool const bUIReady = bUIAnyMove ? bOrderable : (!bAutomated && pGroup->readyToMove(false));
		bool const bBusy = pGroup->isBusy();
		bool const bAutoReady = pGroup->readyToAuto();
		bool const bMission = (pGroup->getLengthMissionQueue() > 0);
		bool const bWaiting = pGroup->isWaiting();
		ActivityTypes const eActivity = pGroup->getActivityType();
		int iMovableUnits = 0;
		if (bOrderable || bUIReady)
		{
			FOR_EACH_UNIT_IN(pUnit, *pGroup)
			{
				if (pUnit->canMove()) iMovableUnits++;
			}
		}
		// <!-- custom: A group can satisfy canAnyMove with only part of a mixed-movement stack ready.
		// Count actual movable units for orderability rather than labelling every member of that qualifying group orderable. (ChatGPT-5.6-Sol) -->
		if (bOrderable) { kSnapshot.iOrderableGroups++; kSnapshot.iOrderableUnits += iMovableUnits; }
		if (bUIReady) { kSnapshot.iUIReadyGroups++; kSnapshot.iUIReadyUnits += iMovableUnits; }
		if (bBusy) { kSnapshot.iBusyGroups++; kSnapshot.iBusyUnits += iUnits; }
		if (bAutomated) { kSnapshot.iAutomatedGroups++; kSnapshot.iAutomatedUnits += iUnits; }
		if (bAutoReady) { kSnapshot.iAutoReadyGroups++; kSnapshot.iAutoReadyUnits += iUnits; }
		if (bMission) { kSnapshot.iMissionGroups++; kSnapshot.iMissionUnits += iUnits; }
		if (bWaiting) { kSnapshot.iWaitingGroups++; kSnapshot.iWaitingUnits += iUnits; }
		if (eActivity == ACTIVITY_HOLD) { kSnapshot.iHoldGroups++; kSnapshot.iHoldUnits += iUnits; }
		if (eActivity == ACTIVITY_SLEEP) { kSnapshot.iSleepGroups++; kSnapshot.iSleepUnits += iUnits; }
	}
}

// <!-- custom: Finite process/game/session states use enums rather than heap-backed strings; the same local rows generate their immutable JSON names.
// Update-reason rows are shared with the public enum so callers cannot invent misspelled reasons; serialize names only when publishing JSON.
// Like building focus, each expansion generates one representation and then undefines its temporary macro to avoid leaking it into later code; this is compile-time work only. (GPT-6.1-Sol) -->
// <!-- custom: Both files come from this runtime recorder, so one implementation revision identifies their paired observations and refers readers to its revision history.
// Compile the label into the publisher: an edited XML value must not make an older loaded DLL report a newer implementation; this counter is independent of SASGameRecord and binary-save versions. (GPT-6.1-Sol) -->
enum SASRuntimeRecorderRevision
{
	SAS_RUNTIME_REVISION = 15
};

#define SAS_RUNTIME_PROCESS_STATES(DO) DO(RUNNING) DO(EXITED_CLEANLY) DO(EXITED)
enum SASRuntimeProcessState
{
#define SAS_RUNTIME_PROCESS_ENUM(NAME) SAS_RUNTIME_PROCESS_##NAME,
	SAS_RUNTIME_PROCESS_STATES(SAS_RUNTIME_PROCESS_ENUM)
#undef SAS_RUNTIME_PROCESS_ENUM
};
static char const* const aSASRuntimeProcessStateNames[] =
{
#define SAS_RUNTIME_PROCESS_NAME(NAME) #NAME,
	SAS_RUNTIME_PROCESS_STATES(SAS_RUNTIME_PROCESS_NAME)
#undef SAS_RUNTIME_PROCESS_NAME
};
#undef SAS_RUNTIME_PROCESS_STATES

#define SAS_RUNTIME_GAME_STATES(DO) DO(NO_GAME) DO(SESSION_STARTING) DO(PLAYING) DO(GAME_ENDED)
enum SASRuntimeGameState
{
#define SAS_RUNTIME_GAME_ENUM(NAME) SAS_RUNTIME_GAME_##NAME,
	SAS_RUNTIME_GAME_STATES(SAS_RUNTIME_GAME_ENUM)
#undef SAS_RUNTIME_GAME_ENUM
};
static char const* const aSASRuntimeGameStateNames[] =
{
#define SAS_RUNTIME_GAME_NAME(NAME) #NAME,
	SAS_RUNTIME_GAME_STATES(SAS_RUNTIME_GAME_NAME)
#undef SAS_RUNTIME_GAME_NAME
};
#undef SAS_RUNTIME_GAME_STATES

#define SAS_RUNTIME_SESSION_STATES(DO) DO(NONE) DO(NEW_GAME) DO(LOAD_GAME)
enum SASRuntimeSessionState
{
#define SAS_RUNTIME_SESSION_ENUM(NAME) SAS_RUNTIME_SESSION_##NAME,
	SAS_RUNTIME_SESSION_STATES(SAS_RUNTIME_SESSION_ENUM)
#undef SAS_RUNTIME_SESSION_ENUM
};
static char const* const aSASRuntimeSessionStateNames[] =
{
#define SAS_RUNTIME_SESSION_NAME(NAME) #NAME,
	SAS_RUNTIME_SESSION_STATES(SAS_RUNTIME_SESSION_NAME)
#undef SAS_RUNTIME_SESSION_NAME
};
#undef SAS_RUNTIME_SESSION_STATES

static char const* const aSASRuntimeStatusReasonNames[] =
{
#define SAS_RUNTIME_STATUS_REASON(NAME) #NAME,
// <!-- custom: Reuse the public enum's catalog at the serialization boundary; no per-event allocation or string search is needed. (GPT-6.1-Sol) -->
#include "SASRuntimeStatusReasons.h"
#undef SAS_RUNTIME_STATUS_REASON
};
BOOST_STATIC_ASSERT(sizeof(aSASRuntimeStatusReasonNames) / sizeof(aSASRuntimeStatusReasonNames[0]) == NUM_SAS_RUNTIME_STATUS_REASONS);

// <!-- custom: Activity is separate from game lifecycle: initialized play can be manual or autoplay, while creation and save loading need distinct timed intervals.
// Requests such as returning to the menu are observed boundaries, not claims that the EXE has displayed that menu. (GPT-6.1-Sol) -->
#define SAS_RUNTIME_ACTIVITIES(DO) DO(NONE) DO(NO_GAME) DO(CREATING_GAME) DO(LOADING_SAVE) DO(PLAYING) DO(AUTOPLAY) DO(WORLD_BUILDER) DO(GAME_ENDED) DO(RETURNING_TO_MENU) DO(EXIT_REQUESTED) DO(SHUTTING_DOWN)
enum SASRuntimeActivity
{
#define SAS_RUNTIME_ACTIVITY_ENUM(NAME) SAS_RUNTIME_ACTIVITY_##NAME,
	SAS_RUNTIME_ACTIVITIES(SAS_RUNTIME_ACTIVITY_ENUM)
#undef SAS_RUNTIME_ACTIVITY_ENUM
};
static char const* const aSASRuntimeActivityNames[] =
{
#define SAS_RUNTIME_ACTIVITY_NAME(NAME) #NAME,
	SAS_RUNTIME_ACTIVITIES(SAS_RUNTIME_ACTIVITY_NAME)
#undef SAS_RUNTIME_ACTIVITY_NAME
};
#undef SAS_RUNTIME_ACTIVITIES
static SASRuntimeActivity g_eSASRuntimeActivity = SAS_RUNTIME_ACTIVITY_NONE;
static SASRuntimeActivity g_eSASRuntimePreviousActivity = SAS_RUNTIME_ACTIVITY_NONE;
static CvString g_szSASRuntimeActivityStartedUtc = "-";
static CvString g_szSASRuntimePreviousStartedUtc = "-";
static CvString g_szSASRuntimePreviousEndedUtc = "-";
static uint g_uiSASRuntimeActivityStartedMilliseconds = 0;
static __int64 g_iSASRuntimePreviousDurationMilliseconds = -1;
// <!-- custom: stateSerial orders transition observations only; run/session metadata contributes to confirmed historyRowsWritten without consuming a transition serial. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static unsigned int g_uiSASRuntimeActivitySerial = 0;
static unsigned int g_uiSASRuntimeActivitySession = 0;
static int g_iSASRuntimeActivityStartTurn = -1;
static int g_iSASRuntimeActivityRequestedTurns = 0;
static SASAutoPlayEndCause g_eSASRuntimeLastAutoplayEndCause = SAS_AUTOPLAY_END_UNSPECIFIED;
static CvString g_szSASRuntimeHistoryFilename;
static CvString g_szSASRuntimeHistoryRunId;
static std::wstring g_szSASRuntimeHistoryRoot;
static unsigned int g_uiSASRuntimeHistoryRowsWritten = 0;
static unsigned int g_uiSASRuntimeHistoryWriteFailures = 0;
// <!-- custom: Retain one bounded ready-session payload for retry, not an in-memory history.
// A failed publication at turn 9/player 0 was retried with turn 10/player 1 mislabeled as the ready state; capture before I/O and retain that observation while failure counters remain live.
// A later ready session supersedes any still-unpublished context; this best-effort archive does not queue failed sessions indefinitely. (GPT-6.1-Sol) -->
static unsigned int g_uiSASRuntimeHistorySessionMetadataCaptured = 0;
static CvString g_szSASRuntimeHistoryPendingSessionMetadata;
static bool g_bSASRuntimeHistoryMetadataWritten = false;
static bool g_bSASRuntimeHistoryMayContainRows = false;
static bool g_bSASRuntimeHistoryAtCurrentRoot = false;

// <!-- custom: Player-turn timing is in-memory instrumentation layered on Runtime rather than a per-player log stream.
// Sequential native turn boundaries retain every measured player's phase durations until TURN_COMPLETED writes one compact summary; slow AI-controlled turns may additionally refresh only the overwrite-only current snapshot.
// Simultaneous turn modes are reported as such but deliberately do not pretend overlapping active turns identify one executing civilization. (ChatGPT-5.6-Sol) -->
#define SAS_RUNTIME_PLAYER_TURN_MODES(DO) DO(UNAVAILABLE) DO(SEQUENTIAL) DO(SIMULTANEOUS)
enum SASRuntimePlayerTurnMode
{
#define SAS_RUNTIME_PLAYER_TURN_MODE_ENUM(NAME) SAS_RUNTIME_PLAYER_TURN_MODE_##NAME,
	SAS_RUNTIME_PLAYER_TURN_MODES(SAS_RUNTIME_PLAYER_TURN_MODE_ENUM)
#undef SAS_RUNTIME_PLAYER_TURN_MODE_ENUM
};
static char const* const aSASRuntimePlayerTurnModeNames[] =
{
#define SAS_RUNTIME_PLAYER_TURN_MODE_NAME(NAME) #NAME,
	SAS_RUNTIME_PLAYER_TURN_MODES(SAS_RUNTIME_PLAYER_TURN_MODE_NAME)
#undef SAS_RUNTIME_PLAYER_TURN_MODE_NAME
};
#undef SAS_RUNTIME_PLAYER_TURN_MODES

#define SAS_RUNTIME_PLAYER_TURN_CONTROLS(DO) DO(NONE) DO(AI) DO(HUMAN) DO(HUMAN_DISABLED) DO(BARBARIAN)
enum SASRuntimePlayerTurnControl
{
#define SAS_RUNTIME_PLAYER_TURN_CONTROL_ENUM(NAME) SAS_RUNTIME_PLAYER_TURN_CONTROL_##NAME,
	SAS_RUNTIME_PLAYER_TURN_CONTROLS(SAS_RUNTIME_PLAYER_TURN_CONTROL_ENUM)
#undef SAS_RUNTIME_PLAYER_TURN_CONTROL_ENUM
};
static char const* const aSASRuntimePlayerTurnControlNames[] =
{
#define SAS_RUNTIME_PLAYER_TURN_CONTROL_NAME(NAME) #NAME,
	SAS_RUNTIME_PLAYER_TURN_CONTROLS(SAS_RUNTIME_PLAYER_TURN_CONTROL_NAME)
#undef SAS_RUNTIME_PLAYER_TURN_CONTROL_NAME
};
#undef SAS_RUNTIME_PLAYER_TURN_CONTROLS

#define SAS_RUNTIME_PLAYER_TURN_PHASES(DO) DO(NONE) DO(ACTIVATING) DO(AI_MOVES) DO(HUMAN_INPUT) DO(ENDING)
enum SASRuntimePlayerTurnPhase
{
#define SAS_RUNTIME_PLAYER_TURN_PHASE_ENUM(NAME) SAS_RUNTIME_PLAYER_TURN_PHASE_##NAME,
	SAS_RUNTIME_PLAYER_TURN_PHASES(SAS_RUNTIME_PLAYER_TURN_PHASE_ENUM)
#undef SAS_RUNTIME_PLAYER_TURN_PHASE_ENUM
};
static char const* const aSASRuntimePlayerTurnPhaseNames[] =
{
#define SAS_RUNTIME_PLAYER_TURN_PHASE_NAME(NAME) #NAME,
	SAS_RUNTIME_PLAYER_TURN_PHASES(SAS_RUNTIME_PLAYER_TURN_PHASE_NAME)
#undef SAS_RUNTIME_PLAYER_TURN_PHASE_NAME
};
#undef SAS_RUNTIME_PLAYER_TURN_PHASES

struct SASRuntimePlayerTurnRecord
{
	int iPlayer;
	int iTeam;
	int iCivilization;
	SASRuntimePlayerTurnControl eControl;
	CvString szCivilizationType;
	CvString szStartedUtc;
	CvString szEndedUtc;
	uint uiTotalMilliseconds;
	uint uiActivatingMilliseconds;
	uint uiMainMilliseconds;
	uint uiEndingMilliseconds;
	uint uiEndTurnReadyMilliseconds;
	uint uiSkipOrdersApplied;
	SASRuntimeTurnReadinessSnapshot kEndReadiness;
	bool bCompleted;
};

static PlayerTypes g_eSASRuntimePlayerTurnPlayer = NO_PLAYER;
static TeamTypes g_eSASRuntimePlayerTurnTeam = NO_TEAM;
static CivilizationTypes g_eSASRuntimePlayerTurnCivilization = NO_CIVILIZATION;
static SASRuntimePlayerTurnControl g_eSASRuntimePlayerTurnControl = SAS_RUNTIME_PLAYER_TURN_CONTROL_NONE;
static SASRuntimePlayerTurnPhase g_eSASRuntimePlayerTurnPhase = SAS_RUNTIME_PLAYER_TURN_PHASE_NONE;
static CvString g_szSASRuntimePlayerTurnCivilizationType = "-";
static CvString g_szSASRuntimePlayerTurnStartedUtc = "-";
static CvString g_szSASRuntimePlayerTurnPhaseStartedUtc = "-";
static uint g_uiSASRuntimePlayerTurnStartedMilliseconds = 0;
static uint g_uiSASRuntimePlayerTurnPhaseStartedMilliseconds = 0;
static uint g_uiSASRuntimePlayerTurnActivatingMilliseconds = 0;
static uint g_uiSASRuntimePlayerTurnMainMilliseconds = 0;
static uint g_uiSASRuntimePlayerTurnEndingMilliseconds = 0;
static uint g_uiSASRuntimePlayerTurnLastLivePublicationMilliseconds = 0;
static bool g_bSASRuntimePlayerTurnLivePublicationAttempted = false;
static bool g_bSASRuntimePlayerTurnContextPublished = false;
static int g_iSASRuntimePlayerTurnSummaryTurn = -1;
static bool g_bSASRuntimePlayerTurnSummaryBoundariesComplete = true;
static std::vector<SASRuntimePlayerTurnRecord> g_aSASRuntimePlayerTurnRecords;
// <!-- custom: Human end-turn readiness is a separate event-driven interval inside HUMAN_INPUT, not a replacement for player-turn wall time.
// Skip orders count actual applied MISSION_SKIP operations; request context is captured once before sendTurnComplete and never guesses the physical key/button source. (ChatGPT-5.6-Sol) -->
static bool g_bSASRuntimeEndTurnReadyUI = false;
static CvString g_szSASRuntimeEndTurnReadySinceUtc = "-";
static uint g_uiSASRuntimeEndTurnReadyStartedMilliseconds = 0;
static uint g_uiSASRuntimeEndTurnReadyMilliseconds = 0;
static uint g_uiSASRuntimeSkipOrdersApplied = 0;
static bool g_bSASRuntimeEndTurnRequestObserved = false;
static CvString g_szSASRuntimeEndTurnRequestRecordedUtc = "-";
static ControlTypes g_eSASRuntimeEndTurnRequestControl = NO_CONTROL;
static bool g_bSASRuntimeEndTurnRequestUIReady = false;
static uint g_uiSASRuntimeEndTurnRequestReadyMilliseconds = 0;
static uint g_uiSASRuntimeEndTurnRequestSkipOrdersApplied = 0;
static SASRuntimeTurnReadinessSnapshot g_kSASRuntimeEndTurnRequestReadiness;
static bool g_bSASRuntimeEndTurnRequestEndTurnMessage = false;
static bool g_bSASRuntimeEndTurnRequestUIAnyMove = false;
static bool g_bSASRuntimeEndTurnRequestSelectedUnit = false;
static bool g_bSASRuntimeEndTurnRequestForcePopup = false;
static bool g_bSASRuntimeEndTurnRequestHasMovedUnit = false;
static bool g_bSASRuntimeEndTurnRequestWaitOption = false;

// <!-- custom: Keep the external-agent runtime status independent from the structured game-record and AI-diagnostic enablement.
// It is default-off and primarily boundary-driven; the fixed JSON is current state, with an optional throttled slow-player progress refresh and completed evidence retained in the companion JSONL.
// The tri-state integer below caches the XML switch once (-1 uninitialized, 0 off, 1 on); repeated isSASRuntimeStatusEnabled calls only read this cache after initialization.
// Keep that cache private behind the named predicate so callers cannot bypass its lazy initialization or mutate it; do not add separate per-caller copies of the same switch.
// Session/load counters live for the DLL process so repeated new/load actions are distinguishable without retaining a growing history in memory. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static int g_iSASRuntimeStatusEnabled = -1;
// <!-- custom: Live Python/XML disk-edit observation is a separate default-off subfeature of runtime diagnostics; cache its define independently so ordinary Runtime status does not start a filesystem watcher. (ChatGPT-5.6-Sol) -->
static int g_iSASRuntimeSourceWatchEnabled = -1;
static unsigned int g_uiSASRuntimeStatusSerial = 0;
// <!-- custom: Recovered snapshots disclose failed earlier publications even to readers without an older statusSerial; status and history failures describe separate outputs. (ChatGPT + GPT-6.1-Sol) -->
static unsigned int g_uiSASRuntimeStatusWriteFailures = 0;
static unsigned int g_uiSASRuntimeSessionSerial = 0;
static unsigned int g_uiSASRuntimeNewGameCount = 0;
static unsigned int g_uiSASRuntimeLoadCount = 0;
static int g_iSASRuntimeLastCompletedTurn = -1;
static SASRuntimeProcessState g_eSASRuntimeProcessState = SAS_RUNTIME_PROCESS_RUNNING;
static SASRuntimeGameState g_eSASRuntimeGameState = SAS_RUNTIME_GAME_NO_GAME;
static SASRuntimeSessionState g_eSASRuntimeSessionKind = SAS_RUNTIME_SESSION_NONE;
static CvString g_szSASRuntimeSessionStartedUtc = "-";
static CvString g_szSASRuntimeNativeReadyUtc = "-";
// <!-- custom: These are passive presentation observations, not claims that an EXE-rendered frame reached the user; exported info getters and Python screen callbacks provide event-driven boundaries without frame polling. (ChatGPT-5.6-Sol) -->
static CvString g_szSASRuntimeMainMenuSceneRequestedUtc = "-";
static CvString g_szSASRuntimeMainMenuStateObservedUtc = "-";
static CvString g_szSASRuntimeLoadingScreenAssetRequestedUtc = "-";
static CvString g_szSASRuntimePythonPreGameStartUtc = "-";
static bool g_bSASRuntimeWorldBuilderMode = false;
static bool g_bSASRuntimeWorldBuilderScreenVisible = false;
// <!-- custom: Remember the last observed overlay context through its hide row; reset/new-session clears it.
// Active player/civilization identify the game's UI owner, not the civilization or model being previewed in a page. (GPT-6.1-Sol) -->
#define SAS_RUNTIME_CIVILOPEDIA_CONTEXTS(DO) DO(NONE) DO(MAIN_MENU) DO(IN_GAME)
enum SASRuntimeCivilopediaContext
{
#define SAS_RUNTIME_CIVILOPEDIA_ENUM(NAME) SAS_RUNTIME_CIVILOPEDIA_##NAME,
	SAS_RUNTIME_CIVILOPEDIA_CONTEXTS(SAS_RUNTIME_CIVILOPEDIA_ENUM)
#undef SAS_RUNTIME_CIVILOPEDIA_ENUM
};
static char const* const aSASRuntimeCivilopediaContextNames[] =
{
#define SAS_RUNTIME_CIVILOPEDIA_NAME(NAME) #NAME,
	SAS_RUNTIME_CIVILOPEDIA_CONTEXTS(SAS_RUNTIME_CIVILOPEDIA_NAME)
#undef SAS_RUNTIME_CIVILOPEDIA_NAME
};
#undef SAS_RUNTIME_CIVILOPEDIA_CONTEXTS
static bool g_bSASRuntimeCivilopediaVisible = false;
static SASRuntimeCivilopediaContext g_eSASRuntimeCivilopediaContext = SAS_RUNTIME_CIVILOPEDIA_NONE;
static int g_iSASRuntimeCivilopediaActivePlayer = -1;
static int g_iSASRuntimeCivilopediaActiveCivilization = -1;
// <!-- custom: ButtonPopup focus is the strongest generic EXE callback that a native prompt has reached its interaction boundary; keep its wait state independent from the underlying PLAYING/AUTOPLAY/GAME_ENDED activity.
// Retain the last popup type/player/resolution after it closes for agent inspection, while reset/new-session clears the context.
// Never expose popup free text or edit-box contents here. (ChatGPT-5.6-Sol) -->
static bool g_bSASRuntimeButtonPopupAwaitingInteraction = false;
static ButtonPopupTypes g_eSASRuntimeButtonPopupType = NO_BUTTONPOPUP;
static int g_iSASRuntimeButtonPopupActivePlayer = -1;
static CvString g_szSASRuntimeButtonPopupFocusedUtc = "-";
static CvString g_szSASRuntimeButtonPopupResolvedUtc = "-";
static CvString g_szSASRuntimeButtonPopupResolution = "-";
static int g_iSASRuntimeButtonPopupResponseButton = -1;
static CvPopup const* g_pSASRuntimeButtonPopup = NULL;

static char const* getSASRuntimeCivilopediaContext()
{
	return aSASRuntimeCivilopediaContextNames[g_eSASRuntimeCivilopediaContext];
}
static std::wstring g_szSASRuntimeStatusRootDirectory;
static std::wstring g_szSASRuntimeStatusSupersededPath;
static bool g_bSASRuntimeStatusRootResolved = false;
// <!-- custom: Track the last successfully published root, not merely the last attempted root; several failed handoffs must retain the actual fallback copy until a replacement succeeds. (GPT-6.1-Sol) -->
static std::wstring g_szSASRuntimeStatusLastPublishedRoot;
// <!-- custom: Observe Windows close messages without replacing Civ4's WndProc: thread-specific hooks watch queue removal and sent-message delivery, always chaining onward.
// Keep the hook entirely inside the default-off runtime recorder; normal gameplay with status disabled never enumerates windows or installs a hook.
// The observation identifies a Windows close message/command, not whether it came from the title-bar X, Alt+F4, automation, or another sender. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static HHOOK g_hSASRuntimeWindowMessageHook = NULL;
// <!-- custom: Window-procedure delivery alone missed the first real autoplay/red-cross test although the observer was armed.
// Observe queue removal too: an EXE can handle a retrieved message without dispatching it to its WndProc; both hooks remain read-only and thread-specific. (GPT-6.1-Sol) -->
static HHOOK g_hSASRuntimeWindowQueueHook = NULL;
static DWORD g_uiSASRuntimeWindowHookThreadId = 0;
static HWND g_hSASRuntimeObservedWindow = NULL;
static bool g_bSASRuntimeHandlingWindowClose = false;
static bool g_bSASRuntimeWindowCloseObservationArmed = false;
// <!-- custom: Both WM_CLOSE and SC_CLOSE observations update this request timestamp; the field names the shared meaning rather than suggesting only WM_CLOSE is covered. (GPT-6.1-Sol) -->
static CvString g_szSASRuntimeWindowCloseRequestObservedUtc = "-";

// <!-- custom: Read XML once on first use, then reuse the setting until restart: -1 means unread, 0 means cached off, and 1 means cached on.
// Shutdown checks the stored value directly; if it was never read, skip status publication rather than performing a first XML lookup after XML caches may have been released. (GPT-6.1-Sol) -->
bool isSASRuntimeStatusEnabled()
{
	if (g_iSASRuntimeStatusEnabled < 0)
		g_iSASRuntimeStatusEnabled = (GC.getDefineINT("SAS_RUNTIME_STATUS_ON") > 0 ? 1 : 0);
	return g_iSASRuntimeStatusEnabled > 0;
}

static bool isSASRuntimeSourceWatchEnabled()
{
	if (g_iSASRuntimeSourceWatchEnabled < 0)
		g_iSASRuntimeSourceWatchEnabled = (GC.getDefineINT("SAS_RUNTIME_SOURCE_WATCH_ON") > 0 ? 1 : 0);
	return g_iSASRuntimeSourceWatchEnabled > 0;
}

static bool writeSASRuntimeStatus(SASRuntimeStatusReason eReason);

// <!-- custom: These settings affect only Runtime's live slow-player publication cadence, not the in-memory measurements or gameplay.
// Cache them only after Runtime itself is enabled; -1 threshold disables live refresh, while refresh 0 means publish only the first threshold crossing. (ChatGPT-5.6-Sol) -->
static int getSASRuntimePlayerTurnLiveThresholdMilliseconds()
{
	static int iMilliseconds = std::max(-1, GC.getDefineINT("SAS_RUNTIME_PLAYER_TURN_LIVE_THRESHOLD_MS"));
	return iMilliseconds;
}

static int getSASRuntimePlayerTurnLiveRefreshMilliseconds()
{
	static int iMilliseconds = std::max(0, GC.getDefineINT("SAS_RUNTIME_PLAYER_TURN_LIVE_REFRESH_MS"));
	return iMilliseconds;
}

static SASRuntimePlayerTurnMode getSASRuntimePlayerTurnMode()
{
	CvGame const& kGame = GC.getGame();
	if (g_eSASRuntimeGameState != SAS_RUNTIME_GAME_PLAYING || !kGame.isFinalInitialized())
		return SAS_RUNTIME_PLAYER_TURN_MODE_UNAVAILABLE;
	if (kGame.isMPOption(MPOPTION_SIMULTANEOUS_TURNS) || kGame.isSimultaneousTeamTurns())
		return SAS_RUNTIME_PLAYER_TURN_MODE_SIMULTANEOUS;
	return SAS_RUNTIME_PLAYER_TURN_MODE_SEQUENTIAL;
}

static SASRuntimePlayerTurnControl getSASRuntimePlayerTurnControl(CvPlayer const& kPlayer)
{
	if (kPlayer.isBarbarian())
		return SAS_RUNTIME_PLAYER_TURN_CONTROL_BARBARIAN;
	if (kPlayer.isHumanDisabled())
		return SAS_RUNTIME_PLAYER_TURN_CONTROL_HUMAN_DISABLED;
	if (kPlayer.isHuman())
		return SAS_RUNTIME_PLAYER_TURN_CONTROL_HUMAN;
	return SAS_RUNTIME_PLAYER_TURN_CONTROL_AI;
}

static bool isSASRuntimeAIControlledPlayerTurn()
{
	return g_eSASRuntimePlayerTurnControl == SAS_RUNTIME_PLAYER_TURN_CONTROL_AI ||
		g_eSASRuntimePlayerTurnControl == SAS_RUNTIME_PLAYER_TURN_CONTROL_HUMAN_DISABLED ||
		g_eSASRuntimePlayerTurnControl == SAS_RUNTIME_PLAYER_TURN_CONTROL_BARBARIAN;
}

// <!-- custom: Name the existing engine ControlTypes accepted by the end-turn hook; this is not a new Runtime enum.
// The three-value switch needs no second enum/catalog: immutable string literals allocate nothing, and Runtime update reasons such as END_TURN_READY name different events. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static char const* getSASRuntimeEndTurnControlName(ControlTypes eControl)
{
	switch (eControl)
	{
	case CONTROL_ENDTURN: return "END_TURN";
	case CONTROL_ENDTURN_ALT: return "END_TURN_ALT";
	case CONTROL_FORCEENDTURN: return "FORCE_END_TURN";
	default: return "UNAVAILABLE";
	}
}

static uint getSASRuntimeEndTurnReadyMilliseconds(uint uiNowMilliseconds)
{
	return g_uiSASRuntimeEndTurnReadyMilliseconds + (g_bSASRuntimeEndTurnReadyUI ? getSASElapsedMilliseconds(g_uiSASRuntimeEndTurnReadyStartedMilliseconds, uiNowMilliseconds) : 0);
}

static void clearSASRuntimeEndTurnContext()
{
	g_bSASRuntimeEndTurnReadyUI = false;
	g_szSASRuntimeEndTurnReadySinceUtc = "-";
	g_uiSASRuntimeEndTurnReadyStartedMilliseconds = 0;
	g_uiSASRuntimeEndTurnReadyMilliseconds = 0;
	g_uiSASRuntimeSkipOrdersApplied = 0;
	g_bSASRuntimeEndTurnRequestObserved = false;
	g_szSASRuntimeEndTurnRequestRecordedUtc = "-";
	g_eSASRuntimeEndTurnRequestControl = NO_CONTROL;
	g_bSASRuntimeEndTurnRequestUIReady = false;
	g_uiSASRuntimeEndTurnRequestReadyMilliseconds = 0;
	g_uiSASRuntimeEndTurnRequestSkipOrdersApplied = 0;
	g_kSASRuntimeEndTurnRequestReadiness = SASRuntimeTurnReadinessSnapshot();
	g_bSASRuntimeEndTurnRequestEndTurnMessage = false;
	g_bSASRuntimeEndTurnRequestUIAnyMove = false;
	g_bSASRuntimeEndTurnRequestSelectedUnit = false;
	g_bSASRuntimeEndTurnRequestForcePopup = false;
	g_bSASRuntimeEndTurnRequestHasMovedUnit = false;
	g_bSASRuntimeEndTurnRequestWaitOption = false;
}

static void clearSASRuntimeCurrentPlayerTurn()
{
	g_eSASRuntimePlayerTurnPlayer = NO_PLAYER;
	g_eSASRuntimePlayerTurnTeam = NO_TEAM;
	g_eSASRuntimePlayerTurnCivilization = NO_CIVILIZATION;
	g_eSASRuntimePlayerTurnControl = SAS_RUNTIME_PLAYER_TURN_CONTROL_NONE;
	g_eSASRuntimePlayerTurnPhase = SAS_RUNTIME_PLAYER_TURN_PHASE_NONE;
	g_szSASRuntimePlayerTurnCivilizationType = "-";
	g_szSASRuntimePlayerTurnStartedUtc = "-";
	g_szSASRuntimePlayerTurnPhaseStartedUtc = "-";
	g_uiSASRuntimePlayerTurnStartedMilliseconds = 0;
	g_uiSASRuntimePlayerTurnPhaseStartedMilliseconds = 0;
	g_uiSASRuntimePlayerTurnActivatingMilliseconds = 0;
	g_uiSASRuntimePlayerTurnMainMilliseconds = 0;
	g_uiSASRuntimePlayerTurnEndingMilliseconds = 0;
	g_uiSASRuntimePlayerTurnLastLivePublicationMilliseconds = 0;
	g_bSASRuntimePlayerTurnLivePublicationAttempted = false;
	g_bSASRuntimePlayerTurnContextPublished = false;
	clearSASRuntimeEndTurnContext();
}

static void resetSASRuntimePlayerTurnTiming()
{
	clearSASRuntimeCurrentPlayerTurn();
	g_iSASRuntimePlayerTurnSummaryTurn = -1;
	g_bSASRuntimePlayerTurnSummaryBoundariesComplete = true;
	g_aSASRuntimePlayerTurnRecords.clear();
}

static void addSASRuntimeCurrentPlayerTurnPhase(uint uiNowMilliseconds)
{
	if (g_eSASRuntimePlayerTurnPlayer == NO_PLAYER || g_eSASRuntimePlayerTurnPhase == SAS_RUNTIME_PLAYER_TURN_PHASE_NONE)
		return;
	uint const uiElapsed = getSASElapsedMilliseconds(g_uiSASRuntimePlayerTurnPhaseStartedMilliseconds, uiNowMilliseconds);
	if (g_eSASRuntimePlayerTurnPhase == SAS_RUNTIME_PLAYER_TURN_PHASE_ACTIVATING)
		g_uiSASRuntimePlayerTurnActivatingMilliseconds += uiElapsed;
	else if (g_eSASRuntimePlayerTurnPhase == SAS_RUNTIME_PLAYER_TURN_PHASE_AI_MOVES || g_eSASRuntimePlayerTurnPhase == SAS_RUNTIME_PLAYER_TURN_PHASE_HUMAN_INPUT)
		g_uiSASRuntimePlayerTurnMainMilliseconds += uiElapsed;
	else if (g_eSASRuntimePlayerTurnPhase == SAS_RUNTIME_PLAYER_TURN_PHASE_ENDING)
		g_uiSASRuntimePlayerTurnEndingMilliseconds += uiElapsed;
}

static bool resolveSASRuntimeStatusDefaultRootDirectory()
{
	if (g_bSASRuntimeStatusRootResolved)
		return !g_szSASRuntimeStatusRootDirectory.empty();
	if (!getSASNativeDefaultRootDirectory(g_szSASRuntimeStatusRootDirectory))
		return false;
	g_bSASRuntimeStatusRootResolved = true;
	return true;
}

// <!-- custom: A case-only Windows root handoff previously wrote and then deleted the same JSON through its old spelling; the native fixture reproduced the missing file.
// Compare normalized slash spellings with Windows Unicode case folding so an equivalent path is never treated as obsolete. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static bool isSASRuntimeStatusSamePath(std::wstring szLeft, std::wstring szRight)
{
	for (size_t i = 0; i < szLeft.size(); i++)
	{
		if (szLeft[i] == L'/')
			szLeft[i] = L'\\';
	}
	for (size_t i = 0; i < szRight.size(); i++)
	{
		if (szRight[i] == L'/')
			szRight[i] = L'\\';
	}
	return CompareStringW(LOCALE_INVARIANT, NORM_IGNORECASE, szLeft.c_str(), -1, szRight.c_str(), -1) == CSTR_EQUAL;
}

// <!-- custom: An in-process shutdown hook cannot run reliably after abort/access violation/TerminateProcess.
// A live Python-edit reproduction produced tracebacks and a Windows-reported python24.dll access violation while the last runtime snapshot still said RUNNING.
// This records final process evidence regardless of whether failure originated in Python, XML-triggered initialization, the game DLL or the EXE; it neither diagnoses the cause nor makes live reload safe.
// Existing close-message and orderly-shutdown hooks remain useful for request/progress timing; observing the later process exit does not replace those earlier boundaries.
// Launch the adjacent same-user Windows observer only for enabled diagnostics and a successfully resolved output root; it waits on a process handle instead of polling gameplay.
// Enabled observation adds PowerShell startup/resident-memory cost and attachment/exit writes, but no per-turn watcher polling; disabled runtime diagnostics launch no observer.
// Remember each attempted root to avoid duplicate helpers on ordinary updates or a later return to a previous CvAltRoot.
// A root migration may need a second observer; a retired status path is ignored after exit. (GPT-6.1-Sol) -->
struct SASRuntimeExitObserverLaunch
{
	std::wstring szRoot;
	DWORD uiProcessId;
	DWORD uiError;
};
static std::vector<SASRuntimeExitObserverLaunch> g_aSASRuntimeExitObservers;
static DWORD g_uiSASRuntimeExitObserverProcessId = 0;
static DWORD g_uiSASRuntimeExitObserverLaunchError = 0;
static std::wstring g_szSASRuntimeExitObserverCurrentRoot;

static void ensureSASRuntimeExitObserver(std::wstring const& szStatusPath)
{
	if (g_szSASRuntimeExitObserverCurrentRoot == g_szSASRuntimeStatusRootDirectory)
		return;
	g_szSASRuntimeExitObserverCurrentRoot = g_szSASRuntimeStatusRootDirectory;
	for (size_t i = 0; i < g_aSASRuntimeExitObservers.size(); i++)
	{
		if (isSASRuntimeStatusSamePath(g_aSASRuntimeExitObservers[i].szRoot, g_szSASRuntimeStatusRootDirectory))
		{
			g_uiSASRuntimeExitObserverProcessId = g_aSASRuntimeExitObservers[i].uiProcessId;
			g_uiSASRuntimeExitObserverLaunchError = g_aSASRuntimeExitObservers[i].uiError;
			return;
		}
	}
	SASRuntimeExitObserverLaunch kLaunch;
	kLaunch.szRoot = g_szSASRuntimeStatusRootDirectory;
	kLaunch.uiProcessId = 0;
	kLaunch.uiError = ERROR_FILE_NOT_FOUND;
	// <!-- custom: Resolve the script beside the actual loaded module, independent of working directory, mod display name or narrow-character mod paths.
	// VirtualQuery identifies the containing image without incrementing its loader reference count. (GPT-6.1-Sol) -->
	MEMORY_BASIC_INFORMATION kMemory;
	wchar_t aModulePath[MAX_PATH];
	wchar_t aSystemPath[MAX_PATH];
	DWORD const uiSystemLength = GetSystemDirectoryW(aSystemPath, MAX_PATH);
	if (VirtualQuery((LPCVOID)&ensureSASRuntimeExitObserver, &kMemory, sizeof(kMemory)) != 0 && uiSystemLength > 0 && uiSystemLength < MAX_PATH)
	{
		DWORD const uiLength = GetModuleFileNameW((HMODULE)kMemory.AllocationBase, aModulePath, MAX_PATH);
		if (uiLength > 0 && uiLength < MAX_PATH)
		{
			std::wstring szScript(aModulePath, uiLength);
			size_t const iSlash = szScript.find_last_of(L"\\/");
			if (iSlash != std::wstring::npos)
			{
				szScript = szScript.substr(0, iSlash + 1) + L"SASRuntimeExitObserver.ps1";
				if (GetFileAttributesW(szScript.c_str()) != INVALID_FILE_ATTRIBUTES)
				{
					std::wstring const szPowerShell = std::wstring(aSystemPath) + L"\\WindowsPowerShell\\v1.0\\powershell.exe";
					CvString szProcessId;
					szProcessId.Format("%lu", (unsigned long)GetCurrentProcessId());
					CvString const& szStartedUtc = getSASExecutableProcessStartUtc();
					CvString szRevision;
					szRevision.Format("%d", SAS_RUNTIME_REVISION);
					// <!-- custom: File arguments are quoted Win32 paths (which cannot contain a quote); no shell command text is assembled or evaluated.
					// ExecutionPolicy applies only to this child process and requires no elevation; machine policy can still block it, so report launch evidence without claiming successful attachment. (GPT-6.1-Sol) -->
					std::wstring szCommand = L"\"" + szPowerShell + L"\" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File \"" + szScript + L"\" -StatusPath \"" + szStatusPath + L"\" -TargetProcessId " + std::wstring(szProcessId.begin(), szProcessId.end()) + L" -ProcessStartUtc " + std::wstring(szStartedUtc.begin(), szStartedUtc.end()) + L" -RecorderRevision " + std::wstring(szRevision.begin(), szRevision.end());
					// <!-- custom: This launcher already runs only under the master Runtime gate.
					// Cache the independent screenshot opt-in here and pass a scalar to the parent observer, so screenshot-off creates no screenshot watcher or files while exit evidence remains available. (GPT-6.1-Sol) -->
					static bool const bScreenshotWatch = (GC.getDefineINT("SAS_RUNTIME_SCREENSHOT_WATCH_ON") > 0);
					szCommand += (bScreenshotWatch ? L" -ScreenshotWatchOn 1" : L" -ScreenshotWatchOn 0");
					std::vector<wchar_t> aCommand(szCommand.begin(), szCommand.end());
					aCommand.push_back(L'\0');
					STARTUPINFOW kStartup;
					PROCESS_INFORMATION kProcess;
					ZeroMemory(&kStartup, sizeof(kStartup));
					ZeroMemory(&kProcess, sizeof(kProcess));
					kStartup.cb = sizeof(kStartup);
					kStartup.dwFlags = STARTF_USESHOWWINDOW;
					kStartup.wShowWindow = SW_HIDE;
					if (CreateProcessW(szPowerShell.c_str(), &aCommand[0], NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &kStartup, &kProcess))
					{
						kLaunch.uiProcessId = kProcess.dwProcessId;
						kLaunch.uiError = 0;
						CloseHandle(kProcess.hThread);
						CloseHandle(kProcess.hProcess);
					}
					else kLaunch.uiError = GetLastError();
				}
			}
		}
	}
	g_aSASRuntimeExitObservers.push_back(kLaunch);
	g_uiSASRuntimeExitObserverProcessId = kLaunch.uiProcessId;
	g_uiSASRuntimeExitObserverLaunchError = kLaunch.uiError;
}

// <!-- custom: Runtime 12 keeps live source observation in its own optional process instead of coupling FileSystemWatcher event handling to the always-on exit/dialog observer.
// Only the explicit default-off source-watch define launches it.
// The companion watches Python/XML disk events, not engine reload state; changing C++ source never replaces the loaded DLL.
// Root migration mirrors exit-observer ownership: one helper per distinct published Logs root, with process/start identity checked again inside the script. (ChatGPT-5.6-Sol) -->
struct SASRuntimeSourceObserverLaunch
{
	std::wstring szRoot;
	DWORD uiProcessId;
	DWORD uiError;
};
static std::vector<SASRuntimeSourceObserverLaunch> g_aSASRuntimeSourceObservers;
static DWORD g_uiSASRuntimeSourceObserverProcessId = 0;
static DWORD g_uiSASRuntimeSourceObserverLaunchError = 0;
static std::wstring g_szSASRuntimeSourceObserverCurrentRoot;

static void ensureSASRuntimeSourceObserver(std::wstring const& szStatusPath)
{
	if (!isSASRuntimeSourceWatchEnabled())
		return;
	if (g_szSASRuntimeSourceObserverCurrentRoot == g_szSASRuntimeStatusRootDirectory)
		return;
	g_szSASRuntimeSourceObserverCurrentRoot = g_szSASRuntimeStatusRootDirectory;
	for (size_t i = 0; i < g_aSASRuntimeSourceObservers.size(); i++)
	{
		if (isSASRuntimeStatusSamePath(g_aSASRuntimeSourceObservers[i].szRoot, g_szSASRuntimeStatusRootDirectory))
		{
			g_uiSASRuntimeSourceObserverProcessId = g_aSASRuntimeSourceObservers[i].uiProcessId;
			g_uiSASRuntimeSourceObserverLaunchError = g_aSASRuntimeSourceObservers[i].uiError;
			return;
		}
	}
	SASRuntimeSourceObserverLaunch kLaunch;
	kLaunch.szRoot = g_szSASRuntimeStatusRootDirectory;
	kLaunch.uiProcessId = 0;
	kLaunch.uiError = ERROR_FILE_NOT_FOUND;
	MEMORY_BASIC_INFORMATION kMemory;
	wchar_t aModulePath[MAX_PATH];
	wchar_t aSystemPath[MAX_PATH];
	DWORD const uiSystemLength = GetSystemDirectoryW(aSystemPath, MAX_PATH);
	if (VirtualQuery((LPCVOID)&ensureSASRuntimeSourceObserver, &kMemory, sizeof(kMemory)) != 0 && uiSystemLength > 0 && uiSystemLength < MAX_PATH)
	{
		DWORD const uiLength = GetModuleFileNameW((HMODULE)kMemory.AllocationBase, aModulePath, MAX_PATH);
		if (uiLength > 0 && uiLength < MAX_PATH)
		{
			std::wstring szScript(aModulePath, uiLength);
			size_t const iSlash = szScript.find_last_of(L"\\/");
			if (iSlash != std::wstring::npos)
			{
				szScript = szScript.substr(0, iSlash + 1) + L"SASRuntimeSourceObserver.ps1";
				if (GetFileAttributesW(szScript.c_str()) != INVALID_FILE_ATTRIBUTES)
				{
					std::wstring const szPowerShell = std::wstring(aSystemPath) + L"\\WindowsPowerShell\\v1.0\\powershell.exe";
					CvString szProcessId;
					szProcessId.Format("%lu", (unsigned long)GetCurrentProcessId());
					CvString const& szStartedUtc = getSASExecutableProcessStartUtc();
					CvString szRevision;
					szRevision.Format("%d", SAS_RUNTIME_REVISION);
					std::wstring szCommand = L"\"" + szPowerShell + L"\" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File \"" + szScript + L"\" -StatusPath \"" + szStatusPath + L"\" -TargetProcessId " + std::wstring(szProcessId.begin(), szProcessId.end()) + L" -ProcessStartUtc " + std::wstring(szStartedUtc.begin(), szStartedUtc.end()) + L" -RecorderRevision " + std::wstring(szRevision.begin(), szRevision.end());
					std::vector<wchar_t> aCommand(szCommand.begin(), szCommand.end());
					aCommand.push_back(L'\0');
					STARTUPINFOW kStartup;
					PROCESS_INFORMATION kProcess;
					ZeroMemory(&kStartup, sizeof(kStartup));
					ZeroMemory(&kProcess, sizeof(kProcess));
					kStartup.cb = sizeof(kStartup);
					kStartup.dwFlags = STARTF_USESHOWWINDOW;
					kStartup.wShowWindow = SW_HIDE;
					if (CreateProcessW(szPowerShell.c_str(), &aCommand[0], NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &kStartup, &kProcess))
					{
						kLaunch.uiProcessId = kProcess.dwProcessId;
						kLaunch.uiError = 0;
						CloseHandle(kProcess.hThread);
						CloseHandle(kProcess.hProcess);
					}
					else kLaunch.uiError = GetLastError();
				}
			}
		}
	}
	g_aSASRuntimeSourceObservers.push_back(kLaunch);
	g_uiSASRuntimeSourceObserverProcessId = kLaunch.uiProcessId;
	g_uiSASRuntimeSourceObserverLaunchError = kLaunch.uiError;
}

// <!-- custom: Accept BUG's already-trimmed Unicode root independently of historical log handles; status is replaceable current state, not append history. (GPT-6.1-Sol) -->
void setSASRuntimeStatusRootDirectory(std::wstring const& szRoot)
{
	if (!isSASRuntimeStatusEnabled())
		return;
	// <!-- custom: An enabled session transition can publish status through the native default root before BUG supplies CvAltRoot.
	// Preserve that last good fallback copy until an authoritative-root rewrite succeeds; if a live reader blocks deletion, later successful updates retry cleanup. (ChatGPT-5.6-Sol) -->
	if (!g_szSASRuntimeStatusLastPublishedRoot.empty() && !isSASRuntimeStatusSamePath(g_szSASRuntimeStatusLastPublishedRoot, szRoot))
		g_szSASRuntimeStatusSupersededPath = g_szSASRuntimeStatusLastPublishedRoot + L"\\Logs\\SASRuntimeStatus.json";
	g_szSASRuntimeStatusRootDirectory = szRoot;
	g_bSASRuntimeStatusRootResolved = true;
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_ROOT_READY);
}

// <!-- custom: Locate Civ4's visible, unowned top-level window only during enabled lifecycle observations.
// Queue and sent-message hooks observe its thread without subclassing, consuming, or altering the EXE's messages; when no window is visible yet, arm on the lifecycle caller's thread. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
struct SASRuntimeProcessWindow
{
	SASRuntimeProcessWindow() : hWindow(NULL), uiThreadId(0) {}
	HWND hWindow;
	DWORD uiThreadId;
};

static BOOL CALLBACK findSASRuntimeProcessWindow(HWND hWindow, LPARAM lParam)
{
	DWORD uiProcessId = 0;
	DWORD const uiThreadId = GetWindowThreadProcessId(hWindow, &uiProcessId);
	if (uiProcessId != GetCurrentProcessId() || uiThreadId == 0 || !IsWindowVisible(hWindow) || GetWindow(hWindow, GW_OWNER) != NULL)
		return TRUE;
	SASRuntimeProcessWindow& kWindow = *(SASRuntimeProcessWindow*)lParam;
	kWindow.hWindow = hWindow;
	kWindow.uiThreadId = uiThreadId;
	return FALSE;
}

// <!-- custom: Keep close evidence typed by both message and observation boundary.
// Queue removal proves retrieval, not window-procedure delivery or completed exit; keep a later delivery observation without restarting its exit interval. (GPT-6.1-Sol) -->
static bool isSASRuntimeWindowCloseReason(SASRuntimeStatusReason eReason)
{
	switch (eReason)
	{
	case SAS_RUNTIME_STATUS_WINDOW_CLOSE_MESSAGE_OBSERVED:
	case SAS_RUNTIME_STATUS_WINDOW_CLOSE_COMMAND_OBSERVED:
	case SAS_RUNTIME_STATUS_WINDOW_CLOSE_MESSAGE_DEQUEUED:
	case SAS_RUNTIME_STATUS_WINDOW_CLOSE_COMMAND_DEQUEUED:
		return true;
	default:
		return false;
	}
}

// <!-- custom: Reject unrelated messages before querying windows, formatting JSON or writing files; enabled hooks incur only this small filter for ordinary messages.
// SC_CLOSE can precede WM_CLOSE and may be handled directly by the EXE.
// Windows reserves the low four command bits, so mask them as documented for WM_SYSCOMMAND.
// The first real autoplay/red-cross retest observed SC_CLOSE without WM_CLOSE; the queue hook separately covers posted requests reproduced by the standalone fixture. (GPT-6.1-Sol) -->
static void observeSASRuntimeWindowClose(HWND hWindow, UINT uiMessage, WPARAM wParam, bool bDequeued)
{
	bool const bCloseMessage = (uiMessage == WM_CLOSE);
	if (!bCloseMessage && !(uiMessage == WM_SYSCOMMAND && (wParam & 0xFFF0) == SC_CLOSE))
		return;
	if (g_bSASRuntimeHandlingWindowClose || g_eSASRuntimeProcessState == SAS_RUNTIME_PROCESS_EXITED_CLEANLY)
		return;
	if (g_hSASRuntimeObservedWindow == NULL)
	{
		// <!-- custom: Civ4's first menu-scene observation occurred before a visible window was discoverable.
		// An observer armed on that thread can bind a later close target without frame polling or requiring a game to have started. (GPT-6.1-Sol) -->
		DWORD uiProcessId = 0;
		DWORD const uiThreadId = GetWindowThreadProcessId(hWindow, &uiProcessId);
		if (uiProcessId != GetCurrentProcessId() || uiThreadId != g_uiSASRuntimeWindowHookThreadId || GetWindow(hWindow, GW_OWNER) != NULL)
			return;
		g_hSASRuntimeObservedWindow = hWindow;
	}
	if (hWindow != g_hSASRuntimeObservedWindow)
		return;
	SASRuntimeStatusReason const eReason = (bCloseMessage ?
		(bDequeued ? SAS_RUNTIME_STATUS_WINDOW_CLOSE_MESSAGE_DEQUEUED : SAS_RUNTIME_STATUS_WINDOW_CLOSE_MESSAGE_OBSERVED) :
		(bDequeued ? SAS_RUNTIME_STATUS_WINDOW_CLOSE_COMMAND_DEQUEUED : SAS_RUNTIME_STATUS_WINDOW_CLOSE_COMMAND_OBSERVED));
	g_bSASRuntimeHandlingWindowClose = true;
	writeSASRuntimeStatus(eReason);
	g_bSASRuntimeHandlingWindowClose = false;
}

static LRESULT CALLBACK observeSASRuntimeWindowMessage(int iCode, WPARAM wParam, LPARAM lParam)
{
	if (iCode >= 0 && lParam != 0)
	{
		CWPSTRUCT const& kMessage = *(CWPSTRUCT const*)lParam;
		observeSASRuntimeWindowClose(kMessage.hwnd, kMessage.message, kMessage.wParam, false);
	}
	return CallNextHookEx(g_hSASRuntimeWindowMessageHook, iCode, wParam, lParam);
}

// <!-- custom: WH_GETMESSAGE runs before GetMessage/PeekMessage returns to the EXE, covering messages consumed by its message loop before DispatchMessage.
// Ignore PM_NOREMOVE peeks so repeatedly inspecting one queued request does not repeatedly record it.
// Never modify MSG or suppress its normal return to the EXE. (GPT-6.1-Sol) -->
static LRESULT CALLBACK observeSASRuntimeWindowQueue(int iCode, WPARAM wParam, LPARAM lParam)
{
	if (iCode >= 0 && wParam == PM_REMOVE && lParam != 0)
	{
		MSG const& kMessage = *(MSG const*)lParam;
		observeSASRuntimeWindowClose(kMessage.hwnd, kMessage.message, kMessage.wParam, true);
	}
	return CallNextHookEx(g_hSASRuntimeWindowQueueHook, iCode, wParam, lParam);
}

static void releaseSASRuntimeWindowMessageHook()
{
	if (g_hSASRuntimeWindowMessageHook != NULL)
		UnhookWindowsHookEx(g_hSASRuntimeWindowMessageHook);
	if (g_hSASRuntimeWindowQueueHook != NULL)
		UnhookWindowsHookEx(g_hSASRuntimeWindowQueueHook);
	g_hSASRuntimeWindowMessageHook = NULL;
	g_hSASRuntimeWindowQueueHook = NULL;
	g_hSASRuntimeObservedWindow = NULL;
	g_uiSASRuntimeWindowHookThreadId = 0;
}

static void ensureSASRuntimeWindowMessageHook()
{
	if (g_hSASRuntimeWindowMessageHook != NULL && g_hSASRuntimeWindowQueueHook != NULL &&
		g_hSASRuntimeObservedWindow != NULL && IsWindow(g_hSASRuntimeObservedWindow))
		return;
	SASRuntimeProcessWindow kWindow;
	EnumWindows(findSASRuntimeProcessWindow, (LPARAM)&kWindow);
	// <!-- custom: Before the main window is visible, observe the thread making this lifecycle callback; bind its top-level close target when one is actually observed.
	// Later lifecycle observations can move the hooks to the discovered window's thread if it differs.
	// No turn/frame polling is added. (GPT-6.1-Sol) -->
	if (kWindow.uiThreadId == 0)
		kWindow.uiThreadId = GetCurrentThreadId();
	if (g_hSASRuntimeWindowMessageHook != NULL && g_hSASRuntimeWindowQueueHook != NULL && g_uiSASRuntimeWindowHookThreadId == kWindow.uiThreadId)
	{
		g_hSASRuntimeObservedWindow = kWindow.hWindow;
		return;
	}
	releaseSASRuntimeWindowMessageHook();
	HHOOK const hMessageHook = SetWindowsHookExW(WH_CALLWNDPROC, observeSASRuntimeWindowMessage, NULL, kWindow.uiThreadId);
	if (hMessageHook == NULL)
		return;
	HHOOK const hQueueHook = SetWindowsHookExW(WH_GETMESSAGE, observeSASRuntimeWindowQueue, NULL, kWindow.uiThreadId);
	if (hQueueHook == NULL)
	{
		// <!-- custom: Arming means both observation paths were installed; roll back a partial installation so later lifecycle callbacks can retry the complete pair. (GPT-6.1-Sol) -->
		UnhookWindowsHookEx(hMessageHook);
		return;
	}
	g_hSASRuntimeObservedWindow = kWindow.hWindow;
	g_uiSASRuntimeWindowHookThreadId = kWindow.uiThreadId;
	g_hSASRuntimeWindowMessageHook = hMessageHook;
	g_hSASRuntimeWindowQueueHook = hQueueHook;
	g_bSASRuntimeWindowCloseObservationArmed = true;
}

// <!-- custom: Cache each whitespace representation once for enabled output; the shared binary context already caches module discovery/hashing, so neither formatting style repeats that I/O. (GPT-6.1-Sol) -->
static CvString const& getSASRuntimeDllIdentity(bool bIndented = false)
{
	if (bIndented)
	{
		static CvString const szIndentedIdentity = getSASDllRuntimeIdentityJson(true);
		return szIndentedIdentity;
	}
	static CvString const szCompactIdentity = getSASDllRuntimeIdentityJson(false);
	return szCompactIdentity;
}

// <!-- custom: Keep the timing history append-only and independent from optional SASGameRecord logging; retaining only the latest snapshot lost earlier new/load/autoplay intervals.
// Runtime revision 3 stores constant process/DLL identity once in a typed run record and ready-game context once per session; transition rows keep a compact run reference plus their local timing/failure evidence.
// A copied transition identifies its run, but full DLL/map interpretation needs its metadata records; the fixed current-state snapshot remains self-contained, and missing metadata does not suppress later transition evidence.
// State durations use the shared monotonic clock, not UTC subtraction; UTC still locates intervals in external evidence. (GPT-6.1-Sol + ChatGPT-5.6-Sol) -->
static CvString const& getSASRuntimeHistoryRunId()
{
	if (g_szSASRuntimeHistoryRunId.empty())
		g_szSASRuntimeHistoryRunId.Format("%s_%lu", getSASExecutableProcessStartUtc().GetCString(), (unsigned long)GetCurrentProcessId());
	return g_szSASRuntimeHistoryRunId;
}

static bool prepareSASRuntimeHistory(std::wstring const& szRoot)
{
	if (g_szSASRuntimeHistoryFilename.empty())
		g_szSASRuntimeHistoryFilename.Format("SASRuntimeHistory_%s.jsonl", getSASRuntimeHistoryRunId().GetCString());
	std::wstring const szName(g_szSASRuntimeHistoryFilename.begin(), g_szSASRuntimeHistoryFilename.end());
	if (g_bSASRuntimeHistoryMayContainRows && !g_szSASRuntimeHistoryRoot.empty() && !isSASRuntimeStatusSamePath(g_szSASRuntimeHistoryRoot, szRoot))
	{
		// <!-- custom: Copy the small timeline when BUG changes the root; never delete the old evidence, and continue there if migration fails rather than silently splitting the history. (GPT-6.1-Sol) -->
		std::wstring const szOldPath = g_szSASRuntimeHistoryRoot + L"\\Logs\\" + szName;
		std::wstring const szNewPath = szRoot + L"\\Logs\\" + szName;
		if (CopyFileW(szOldPath.c_str(), szNewPath.c_str(), FALSE))
			g_szSASRuntimeHistoryRoot = szRoot;
	}
	else g_szSASRuntimeHistoryRoot = szRoot;
	g_bSASRuntimeHistoryAtCurrentRoot = isSASRuntimeStatusSamePath(g_szSASRuntimeHistoryRoot, szRoot);
	return !g_szSASRuntimeHistoryRoot.empty();
}

// <!-- custom: Distinguish complete row bytes from confirmed write/close success through pbContentComplete.
// Metadata can avoid duplicate retries after an uncertain close while confirmed-row counters still require the successful close result. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static bool appendSASRuntimeHistory(CvString const& szRow, bool* pbContentComplete = NULL)
{
	if (pbContentComplete != NULL)
		*pbContentComplete = false;
	if (g_szSASRuntimeHistoryRoot.empty())
		return false;
	std::wstring const szName(g_szSASRuntimeHistoryFilename.begin(), g_szSASRuntimeHistoryFilename.end());
	std::wstring const szPath = g_szSASRuntimeHistoryRoot + L"\\Logs\\" + szName;
	HANDLE const hFile = CreateFileW(szPath.c_str(), GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
	if (hFile == INVALID_HANDLE_VALUE)
		return false;
	LARGE_INTEGER kZero, kStart;
	kZero.QuadPart = 0;
	bool bComplete = SetFilePointerEx(hFile, kZero, &kStart, FILE_END) != FALSE;
	size_t iWrittenTotal = 0;
	while (bComplete && iWrittenTotal < szRow.size())
	{
		DWORD iWritten = 0;
		BOOL const bWritten = WriteFile(hFile, szRow.GetCString() + iWrittenTotal, (DWORD)(szRow.size() - iWrittenTotal), &iWritten, NULL);
		iWrittenTotal += iWritten;
		bComplete = (bWritten != FALSE && iWritten != 0);
	}
	// <!-- custom: A failed partial append must not join a torn JSON row to the next transition; roll back this row while retaining earlier complete intervals. (GPT-6.1-Sol) -->
	if (!bComplete && iWrittenTotal != 0)
	{
		if (SetFilePointerEx(hFile, kStart, NULL, FILE_BEGIN))
			SetEndOfFile(hFile);
	}
	if (pbContentComplete != NULL)
		*pbContentComplete = bComplete;
	BOOL const bClosed = CloseHandle(hFile);
	return bComplete && bClosed != FALSE;
}

// <!-- custom: Account for all three record types in one place; physical-row evidence and confirmed-success counts are deliberately separate after an uncertain close.
// Separate row writes keep each retry decision tied to that record's outcome rather than an ambiguous context/transition batch. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static bool recordSASRuntimeHistoryRow(CvString const& szRow, bool* pbContentComplete = NULL)
{
	bool bContentComplete = false;
	bool const bConfirmed = appendSASRuntimeHistory(szRow, &bContentComplete);
	if (pbContentComplete != NULL)
		*pbContentComplete = bContentComplete;
	// <!-- custom: A full WriteFile followed by an unconfirmed close can leave a physical row even though it is not counted as confirmed; remember that possibility so a later CvAltRoot migration does not silently abandon the old history file. (ChatGPT-5.6-Sol) -->
	if (bConfirmed || bContentComplete)
		g_bSASRuntimeHistoryMayContainRows = true;
	if (bConfirmed)
	{
		g_uiSASRuntimeHistoryRowsWritten++;
		return true;
	}
	g_uiSASRuntimeHistoryWriteFailures++;
	return false;
}

// <!-- custom: Persist one accepted human end-turn request before sendTurnComplete so later cleanup cannot erase whether orderable/busy/automated/mission groups remained.
// `physicalInput` is deliberately NOT_OBSERVED: CONTROL_FORCEENDTURN can come from Enter or the end-turn widget.
// HOLD is reported only as current activity; explicit Skip is the separately tracked applied-order counter. (ChatGPT-5.6-Sol) -->
static void recordSASRuntimeEndTurnContext(int iGameTurn)
{
	if (!g_bSASRuntimeEndTurnRequestObserved || g_eSASRuntimePlayerTurnPlayer == NO_PLAYER)
		return;
	CvString szRow;
	szRow.Format("{\"record\":\"end_turn_context\","
		"\"revision\":%d,"
		"\"run\":\"%s\","
		"\"recordedUtc\":\"%s\","
		"\"sessionSerial\":%u,"
		"\"gameTurn\":%d,"
		"\"player\":%d,"
		"\"team\":%d,"
		"\"civilization\":%d,"
		"\"civilizationType\":\"%s\","
		"\"control\":\"%s\","
		"\"controlId\":%d,"
		"\"physicalInput\":\"NOT_OBSERVED\","
		"\"uiEndTurnMessage\":%d,"
		"\"uiReadyForEndTurn\":%d,"
		"\"uiAnyMoveRule\":%d,"
		"\"selectedUnitPresent\":%d,"
		"\"forcePopup\":%d,"
		"\"hasMovedUnit\":%d,"
		"\"waitEndTurnOption\":%d,"
		"\"readyUiMilliseconds\":%u,"
		"\"skipOrdersAppliedThisTurn\":%u,"
		"\"groups\":%d,"
		"\"units\":%d,"
		"\"orderableGroups\":%d,"
		"\"orderableUnits\":%d,"
		"\"uiReadyGroups\":%d,"
		"\"uiReadyUnits\":%d,"
		"\"busyGroups\":%d,"
		"\"busyUnits\":%d,"
		"\"automatedGroups\":%d,"
		"\"automatedUnits\":%d,"
		"\"autoReadyGroups\":%d,"
		"\"autoReadyUnits\":%d,"
		"\"missionGroups\":%d,"
		"\"missionUnits\":%d,"
		"\"waitingGroups\":%d,"
		"\"waitingUnits\":%d,"
		"\"holdGroups\":%d,"
		"\"holdUnits\":%d,"
		"\"sleepGroups\":%d,"
		"\"sleepUnits\":%d,"
		"\"priorStatusWriteFailures\":%u,"
		"\"priorHistoryWriteFailures\":%u}\r\n",
		SAS_RUNTIME_REVISION, getSASRuntimeHistoryRunId().GetCString(), g_szSASRuntimeEndTurnRequestRecordedUtc.GetCString(), g_uiSASRuntimeSessionSerial, iGameTurn,
		(int)g_eSASRuntimePlayerTurnPlayer, (int)g_eSASRuntimePlayerTurnTeam, (int)g_eSASRuntimePlayerTurnCivilization, g_szSASRuntimePlayerTurnCivilizationType.GetCString(),
		getSASRuntimeEndTurnControlName(g_eSASRuntimeEndTurnRequestControl), (int)g_eSASRuntimeEndTurnRequestControl, g_bSASRuntimeEndTurnRequestEndTurnMessage ? 1 : 0, g_bSASRuntimeEndTurnRequestUIReady ? 1 : 0,
		g_bSASRuntimeEndTurnRequestUIAnyMove ? 1 : 0, g_bSASRuntimeEndTurnRequestSelectedUnit ? 1 : 0, g_bSASRuntimeEndTurnRequestForcePopup ? 1 : 0, g_bSASRuntimeEndTurnRequestHasMovedUnit ? 1 : 0, g_bSASRuntimeEndTurnRequestWaitOption ? 1 : 0,
		g_uiSASRuntimeEndTurnRequestReadyMilliseconds, g_uiSASRuntimeEndTurnRequestSkipOrdersApplied,
		g_kSASRuntimeEndTurnRequestReadiness.iGroups, g_kSASRuntimeEndTurnRequestReadiness.iUnits, g_kSASRuntimeEndTurnRequestReadiness.iOrderableGroups, g_kSASRuntimeEndTurnRequestReadiness.iOrderableUnits,
		g_kSASRuntimeEndTurnRequestReadiness.iUIReadyGroups, g_kSASRuntimeEndTurnRequestReadiness.iUIReadyUnits, g_kSASRuntimeEndTurnRequestReadiness.iBusyGroups, g_kSASRuntimeEndTurnRequestReadiness.iBusyUnits,
		g_kSASRuntimeEndTurnRequestReadiness.iAutomatedGroups, g_kSASRuntimeEndTurnRequestReadiness.iAutomatedUnits, g_kSASRuntimeEndTurnRequestReadiness.iAutoReadyGroups, g_kSASRuntimeEndTurnRequestReadiness.iAutoReadyUnits,
		g_kSASRuntimeEndTurnRequestReadiness.iMissionGroups, g_kSASRuntimeEndTurnRequestReadiness.iMissionUnits, g_kSASRuntimeEndTurnRequestReadiness.iWaitingGroups, g_kSASRuntimeEndTurnRequestReadiness.iWaitingUnits,
		g_kSASRuntimeEndTurnRequestReadiness.iHoldGroups, g_kSASRuntimeEndTurnRequestReadiness.iHoldUnits, g_kSASRuntimeEndTurnRequestReadiness.iSleepGroups, g_kSASRuntimeEndTurnRequestReadiness.iSleepUnits,
		g_uiSASRuntimeStatusWriteFailures, g_uiSASRuntimeHistoryWriteFailures);
	recordSASRuntimeHistoryRow(szRow);
}

// <!-- custom: Emit one bounded row for the just-completed sequential game turn instead of one history row per player boundary.
// Every measured player remains in memory regardless of speed; complete=0 flags a missing/mismatched native boundary rather than inventing a duration.
// The enclosing enabled scope in publishSASRuntimeStatus pre-gates this call and its arguments; repeating the switch beside this private helper would not skip additional work.
// The mode check here is a timing-policy check, not the logging gate.
// Row/string construction occurs only after that enclosing gate and only at the completed-turn publication boundary.
// Simultaneous-turn modes deliberately emit no sequential summary because overlapping active turns do not identify one executing civilization. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static void recordSASRuntimePlayerTurnSummary(int iCompletedTurn, CvString const& szRecordedUtc)
{
	if (getSASRuntimePlayerTurnMode() != SAS_RUNTIME_PLAYER_TURN_MODE_SEQUENTIAL)
	{
		resetSASRuntimePlayerTurnTiming();
		return;
	}
	if (g_aSASRuntimePlayerTurnRecords.empty() || g_iSASRuntimePlayerTurnSummaryTurn < 0)
		return;
	bool const bComplete = g_bSASRuntimePlayerTurnSummaryBoundariesComplete && g_eSASRuntimePlayerTurnPlayer == NO_PLAYER && g_iSASRuntimePlayerTurnSummaryTurn == iCompletedTurn;
	CvString szRow;
	szRow.Format("{\"record\":\"player_turn_summary\","
		"\"revision\":%d,"
		"\"run\":\"%s\","
		"\"recordedUtc\":\"%s\","
		"\"sessionSerial\":%u,"
		"\"gameTurn\":%d,"
		"\"timingMode\":\"SEQUENTIAL\","
		"\"complete\":%d,"
		"\"players\":[",
		SAS_RUNTIME_REVISION, getSASRuntimeHistoryRunId().GetCString(), szRecordedUtc.GetCString(), g_uiSASRuntimeSessionSerial, g_iSASRuntimePlayerTurnSummaryTurn, bComplete ? 1 : 0);
	for (size_t i = 0; i < g_aSASRuntimePlayerTurnRecords.size(); i++)
	{
		SASRuntimePlayerTurnRecord const& kRecord = g_aSASRuntimePlayerTurnRecords[i];
		CvString szPlayer;
		szPlayer.Format("%s{\"player\":%d,"
			"\"team\":%d,"
			"\"civilization\":%d,"
			"\"civilizationType\":\"%s\","
			"\"control\":\"%s\","
			"\"startedUtc\":\"%s\","
			"\"endedUtc\":\"%s\","
			"\"totalMilliseconds\":%u,"
			"\"activatingMilliseconds\":%u,"
			"\"mainMilliseconds\":%u,"
			"\"endingMilliseconds\":%u,"
			"\"readyUiMilliseconds\":%u,"
			"\"skipOrdersApplied\":%u,"
			"\"endGroups\":%d,"
			"\"endUnits\":%d,"
			"\"endOrderableGroups\":%d,"
			"\"endOrderableUnits\":%d,"
			"\"endBusyGroups\":%d,"
			"\"endAutomatedGroups\":%d,"
			"\"endAutoReadyGroups\":%d,"
			"\"endMissionGroups\":%d,"
			"\"endWaitingGroups\":%d,"
			"\"endHoldGroups\":%d,"
			"\"endSleepGroups\":%d,"
			"\"completed\":%d}",
			(i == 0 ? "" : ","), kRecord.iPlayer, kRecord.iTeam, kRecord.iCivilization, kRecord.szCivilizationType.GetCString(), aSASRuntimePlayerTurnControlNames[kRecord.eControl], kRecord.szStartedUtc.GetCString(), kRecord.szEndedUtc.GetCString(),
			kRecord.uiTotalMilliseconds, kRecord.uiActivatingMilliseconds, kRecord.uiMainMilliseconds, kRecord.uiEndingMilliseconds, kRecord.uiEndTurnReadyMilliseconds, kRecord.uiSkipOrdersApplied,
			kRecord.kEndReadiness.iGroups, kRecord.kEndReadiness.iUnits, kRecord.kEndReadiness.iOrderableGroups, kRecord.kEndReadiness.iOrderableUnits, kRecord.kEndReadiness.iBusyGroups,
			kRecord.kEndReadiness.iAutomatedGroups, kRecord.kEndReadiness.iAutoReadyGroups, kRecord.kEndReadiness.iMissionGroups, kRecord.kEndReadiness.iWaitingGroups, kRecord.kEndReadiness.iHoldGroups, kRecord.kEndReadiness.iSleepGroups,
			kRecord.bCompleted ? 1 : 0);
		szRow += szPlayer;
	}
	CvString szTail;
	szTail.Format("],"
		"\"priorStatusWriteFailures\":%u,"
		"\"priorHistoryWriteFailures\":%u}\r\n", g_uiSASRuntimeStatusWriteFailures, g_uiSASRuntimeHistoryWriteFailures);
	szRow += szTail;
	// <!-- custom: This is a bounded best-effort summary: after the write attempt, release the turn records even if output failed; the history failure counter discloses loss instead of accumulating an unbounded backlog of turns. (GPT-6.1-Sol) -->
	recordSASRuntimeHistoryRow(szRow);
	resetSASRuntimePlayerTurnTiming();
}

// <!-- custom: Normally publish one run record before transitions so constant revision/process/DLL identity is not repeated on every line.
// If this metadata write fails, transition rows still carry revision + run ID and prior failure counters; open/partial failures retry later, while a full row with unconfirmed close is not duplicated. (ChatGPT-5.6-Sol) -->
static bool ensureSASRuntimeHistoryMetadata()
{
	if (g_bSASRuntimeHistoryMetadataWritten)
		return true;
	CvString szRow;
	CvString const& szDllIdentity = getSASRuntimeDllIdentity();
	CvString const szSourceIdentity = getSASSourceRuntimeIdentityJson(false);
	szRow.Format("{\"record\":\"run\","
		"\"revision\":%d,"
		"\"run\":\"%s\","
		"\"processId\":%lu,"
		"\"processStartUtc\":\"%s\","
		"\"dllLoadUtc\":\"%s\","
		"\"dllIdentity\":%s,"
		"\"sourceIdentity\":%s,"
		"\"priorStatusWriteFailures\":%u,"
		"\"priorHistoryWriteFailures\":%u}\r\n",
		SAS_RUNTIME_REVISION, getSASRuntimeHistoryRunId().GetCString(), (unsigned long)GetCurrentProcessId(), getSASExecutableProcessStartUtc().GetCString(), getSASProcessUtcTimestamp().GetCString(), szDllIdentity.GetCString(), szSourceIdentity.GetCString(),
		g_uiSASRuntimeStatusWriteFailures, g_uiSASRuntimeHistoryWriteFailures);
	bool bContentComplete = false;
	bool const bConfirmed = recordSASRuntimeHistoryRow(szRow, &bContentComplete);
	// <!-- custom: Do not duplicate a fully written row after an unconfirmed close; historyWriteFailures already marks that its physical presence is uncertain.
	// Retry only when the row bytes themselves did not complete. (ChatGPT-5.6-Sol) -->
	g_bSASRuntimeHistoryMetadataWritten = bConfirmed || bContentComplete;
	return g_bSASRuntimeHistoryMetadataWritten;
}

// <!-- custom: Capture first-ready context once per session instead of repeating it on transitions or resampling a later turn during retries.
// Cache the serialized stable fields independently of directory availability or metadata-write success; recordedUtc locates that observation, while publication-failure counters are appended at each write attempt. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static void captureSASRuntimeHistorySessionMetadata(CvString const& szNowUtc, int iReadyGameTurn, int iReadyActivePlayer, int iMapWidth, int iMapHeight, int iWorldSize, int iGameSpeed, int iScenario, int iLoadedCheckpointTurn, int iLoadedCheckpointElapsedTurn, char const* szLoadedCheckpointUtc)
{
	if (g_uiSASRuntimeSessionSerial == 0 || g_uiSASRuntimeHistorySessionMetadataCaptured == g_uiSASRuntimeSessionSerial)
		return;
	g_szSASRuntimeHistoryPendingSessionMetadata.Format("{\"record\":\"session\","
		"\"revision\":%d,"
		"\"run\":\"%s\","
		"\"recordedUtc\":\"%s\","
		"\"sessionSerial\":%u,"
		"\"sessionKind\":\"%s\","
		"\"sessionStartedUtc\":\"%s\","
		"\"nativeReadyUtc\":\"%s\","
		"\"newGameCount\":%u,"
		"\"loadCount\":%u,"
		"\"readyGameTurn\":%d,"
		"\"readyActivePlayer\":%d,"
		"\"mapWidth\":%d,"
		"\"mapHeight\":%d,"
		"\"worldSize\":%d,"
		"\"gameSpeed\":%d,"
		"\"scenario\":%d,"
		"\"loadedSaveCheckpointTurn\":%d,"
		"\"loadedSaveCheckpointElapsedTurn\":%d,"
		"\"loadedSaveCheckpointUtc\":\"%s\",",
		SAS_RUNTIME_REVISION, getSASRuntimeHistoryRunId().GetCString(), szNowUtc.GetCString(), g_uiSASRuntimeSessionSerial, aSASRuntimeSessionStateNames[g_eSASRuntimeSessionKind], g_szSASRuntimeSessionStartedUtc.GetCString(), g_szSASRuntimeNativeReadyUtc.GetCString(),
		g_uiSASRuntimeNewGameCount, g_uiSASRuntimeLoadCount, iReadyGameTurn, iReadyActivePlayer, iMapWidth, iMapHeight, iWorldSize, iGameSpeed, iScenario,
		iLoadedCheckpointTurn, iLoadedCheckpointElapsedTurn, szLoadedCheckpointUtc);
	g_uiSASRuntimeHistorySessionMetadataCaptured = g_uiSASRuntimeSessionSerial;
}

// <!-- custom: Retry the frozen session payload independently of live gameplay so a menu/reset update can still recover the last ready observation.
// Open/partial failures leave it pending; fully written metadata with an uncertain close is not duplicated, and keeping the capture serial prevents later turn updates from recreating it. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static void ensureSASRuntimeHistorySessionMetadata()
{
	if (!g_bSASRuntimeHistoryMetadataWritten || g_szSASRuntimeHistoryPendingSessionMetadata.empty())
		return;
	CvString szRow;
	szRow.Format("%s\"priorStatusWriteFailures\":%u,"
		"\"priorHistoryWriteFailures\":%u}\r\n",
		g_szSASRuntimeHistoryPendingSessionMetadata.GetCString(), g_uiSASRuntimeStatusWriteFailures, g_uiSASRuntimeHistoryWriteFailures);
	bool bContentComplete = false;
	bool const bConfirmed = recordSASRuntimeHistoryRow(szRow, &bContentComplete);
	if (bConfirmed || bContentComplete)
		g_szSASRuntimeHistoryPendingSessionMetadata.clear();
}

static SASRuntimeActivity getSASRuntimeActivity(SASRuntimeStatusReason eReason, int iAutoPlayRemaining)
{
	if (g_eSASRuntimeProcessState == SAS_RUNTIME_PROCESS_EXITED_CLEANLY)
		return SAS_RUNTIME_ACTIVITY_SHUTTING_DOWN;
	if (eReason == SAS_RUNTIME_STATUS_RETURN_TO_MENU_REQUESTED)
		return SAS_RUNTIME_ACTIVITY_RETURNING_TO_MENU;
	if (eReason == SAS_RUNTIME_STATUS_EXIT_REQUESTED || isSASRuntimeWindowCloseReason(eReason))
		return SAS_RUNTIME_ACTIVITY_EXIT_REQUESTED;
	if (g_eSASRuntimeGameState == SAS_RUNTIME_GAME_NO_GAME)
		return SAS_RUNTIME_ACTIVITY_NO_GAME;
	if (g_eSASRuntimeGameState == SAS_RUNTIME_GAME_SESSION_STARTING)
		return (g_eSASRuntimeSessionKind == SAS_RUNTIME_SESSION_NEW_GAME ? SAS_RUNTIME_ACTIVITY_CREATING_GAME : SAS_RUNTIME_ACTIVITY_LOADING_SAVE);
	if (g_eSASRuntimeGameState == SAS_RUNTIME_GAME_GAME_ENDED)
		return SAS_RUNTIME_ACTIVITY_GAME_ENDED;
	// <!-- custom: A completed-turn callback can arrive after an exit request; preserve the pending request until a reset/new session or shutdown actually changes lifecycle. (GPT-6.1-Sol) -->
	if (g_eSASRuntimeActivity == SAS_RUNTIME_ACTIVITY_RETURNING_TO_MENU || g_eSASRuntimeActivity == SAS_RUNTIME_ACTIVITY_EXIT_REQUESTED)
		return g_eSASRuntimeActivity;
	// <!-- custom: A still-visible editor must not overwrite an already observed menu/exit request when another callback arrives before its hide notification. (GPT-6.1-Sol) -->
	if (g_bSASRuntimeWorldBuilderMode && g_bSASRuntimeWorldBuilderScreenVisible)
		return SAS_RUNTIME_ACTIVITY_WORLD_BUILDER;
	return (iAutoPlayRemaining > 0 ? SAS_RUNTIME_ACTIVITY_AUTOPLAY : SAS_RUNTIME_ACTIVITY_PLAYING);
}

// <!-- custom: Save-checkpoint/map context now belongs to frozen session metadata; this formatter takes only the current transition's time, turn and autoplay values. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static void updateSASRuntimeActivity(SASRuntimeStatusReason eReason, CvString const& szNowUtc, uint uiNowMilliseconds, int iGameTurn, int iAutoPlayRemaining)
{
	SASRuntimeActivity const eActivity = getSASRuntimeActivity(eReason, iAutoPlayRemaining);
	// <!-- custom: Keep presentation observations in the timeline without splitting the underlying activity interval.
	// The native fixture's creation from 1000 to 2000 ms previously became 250 ms plus 750 ms after its loading-asset request; preserving the interval start restores the full 1000 ms completion duration. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
	bool const bObservationBoundary = (
		eReason == SAS_RUNTIME_STATUS_MAIN_MENU_SCENE_REQUESTED ||
		eReason == SAS_RUNTIME_STATUS_MAIN_MENU_STATE_OBSERVED ||
		eReason == SAS_RUNTIME_STATUS_LOADING_SCREEN_ASSET_REQUESTED ||
		eReason == SAS_RUNTIME_STATUS_PYTHON_PRE_GAME_START ||
		eReason == SAS_RUNTIME_STATUS_WORLD_BUILDER_MODE_ENTERED ||
		eReason == SAS_RUNTIME_STATUS_WORLD_BUILDER_MODE_EXITED ||
		eReason == SAS_RUNTIME_STATUS_WORLD_BUILDER_SCREEN_SHOWN ||
		eReason == SAS_RUNTIME_STATUS_WORLD_BUILDER_SCREEN_HIDDEN ||
		eReason == SAS_RUNTIME_STATUS_CIVILOPEDIA_SHOWN ||
		eReason == SAS_RUNTIME_STATUS_CIVILOPEDIA_HIDDEN ||
		eReason == SAS_RUNTIME_STATUS_BUTTON_POPUP_FOCUSED ||
		eReason == SAS_RUNTIME_STATUS_BUTTON_POPUP_RESPONDED ||
		eReason == SAS_RUNTIME_STATUS_BUTTON_POPUP_CANCELLED ||
		eReason == SAS_RUNTIME_STATUS_END_TURN_READY ||
		eReason == SAS_RUNTIME_STATUS_END_TURN_NOT_READY ||
		eReason == SAS_RUNTIME_STATUS_END_TURN_REQUEST_ACCEPTED ||
		isSASRuntimeWindowCloseReason(eReason));
	bool const bIntervalStarted = (eActivity != g_eSASRuntimeActivity || eReason == SAS_RUNTIME_STATUS_AUTOPLAY_CHANGED || g_uiSASRuntimeActivitySession != g_uiSASRuntimeSessionSerial);
	if (!bIntervalStarted && !bObservationBoundary)
		return;
	unsigned int const uiPreviousSession = (bIntervalStarted ? g_uiSASRuntimeActivitySession : 0);
	int const iPreviousStartTurn = (bIntervalStarted ? g_iSASRuntimeActivityStartTurn : -1);
	int const iPreviousRequestedTurns = (bIntervalStarted ? g_iSASRuntimeActivityRequestedTurns : 0);
	if (bIntervalStarted)
	{
		g_eSASRuntimePreviousActivity = g_eSASRuntimeActivity;
		g_szSASRuntimePreviousStartedUtc = g_szSASRuntimeActivityStartedUtc;
		g_szSASRuntimePreviousEndedUtc = (g_eSASRuntimeActivity == SAS_RUNTIME_ACTIVITY_NONE ? CvString("-") : szNowUtc);
		g_iSASRuntimePreviousDurationMilliseconds = (g_eSASRuntimeActivity == SAS_RUNTIME_ACTIVITY_NONE ? -1 : (__int64)getSASElapsedMilliseconds(g_uiSASRuntimeActivityStartedMilliseconds, uiNowMilliseconds));
		g_eSASRuntimeActivity = eActivity;
		g_szSASRuntimeActivityStartedUtc = szNowUtc;
		g_uiSASRuntimeActivityStartedMilliseconds = uiNowMilliseconds;
		g_uiSASRuntimeActivitySession = g_uiSASRuntimeSessionSerial;
		g_iSASRuntimeActivityStartTurn = iGameTurn;
		g_iSASRuntimeActivityRequestedTurns = iAutoPlayRemaining;
	}
	CvString szRow;
	// <!-- custom: Keep one JSONL record on each output line.
	// Constant binary/process identity lives in the run record; revision + run ID stay on transitions so copied/grepped lines still identify their recorder/run.
	// Observation-only rows do not repeat a completed previous interval; the fixed snapshot still retains the most recently completed activity.
	// Prior publication counters disclose missing earlier evidence without making every row repeat the fixed snapshot or session metadata. (GPT-6.1-Sol + ChatGPT-5.6-Sol) -->
	szRow.Format("{\"record\":\"transition\","
		"\"revision\":%d,"
		"\"run\":\"%s\","
		"\"stateSerial\":%u,"
		"\"intervalStarted\":%d,"
		"\"previousState\":\"%s\","
		"\"previousStartedUtc\":\"%s\","
		"\"previousEndedUtc\":\"%s\","
		"\"previousDurationMilliseconds\":%I64d,"
		"\"previousSessionSerial\":%u,"
		"\"previousStartTurn\":%d,"
		"\"previousRequestedAutoplayTurns\":%d,"
		"\"recordedUtc\":\"%s\","
		"\"state\":\"%s\","
		"\"stateStartedUtc\":\"%s\","
		"\"stateElapsedMilliseconds\":%u,"
		"\"sessionSerial\":%u,"
		"\"gameTurn\":%d,"
		"\"autoplayRemainingTurns\":%d,"
		"\"reason\":\"%s\","
		"\"civilopediaVisible\":%d,"
		"\"civilopediaContext\":\"%s\","
		"\"civilopediaActivePlayer\":%d,"
		"\"civilopediaActiveCivilization\":%d,"
		"\"buttonPopupAwaitingInteraction\":%d,"
		"\"buttonPopupType\":\"%s\","
		"\"buttonPopupTypeId\":%d,"
		"\"buttonPopupActivePlayer\":%d,"
		"\"buttonPopupFocusedUtc\":\"%s\","
		"\"buttonPopupResolvedUtc\":\"%s\","
		"\"buttonPopupResolution\":\"%s\","
		"\"buttonPopupResponseButton\":%d,"
		"\"autoplayEndCause\":\"%s\","
		"\"priorStatusWriteFailures\":%u,"
		"\"priorHistoryWriteFailures\":%u}\r\n",
		SAS_RUNTIME_REVISION, getSASRuntimeHistoryRunId().GetCString(), ++g_uiSASRuntimeActivitySerial, bIntervalStarted ? 1 : 0,
		aSASRuntimeActivityNames[bIntervalStarted ? g_eSASRuntimePreviousActivity : SAS_RUNTIME_ACTIVITY_NONE], bIntervalStarted ? g_szSASRuntimePreviousStartedUtc.GetCString() : "-", bIntervalStarted ? g_szSASRuntimePreviousEndedUtc.GetCString() : "-", bIntervalStarted ? g_iSASRuntimePreviousDurationMilliseconds : (__int64)-1,
		uiPreviousSession, iPreviousStartTurn, iPreviousRequestedTurns, szNowUtc.GetCString(), aSASRuntimeActivityNames[eActivity], g_szSASRuntimeActivityStartedUtc.GetCString(), getSASElapsedMilliseconds(g_uiSASRuntimeActivityStartedMilliseconds, uiNowMilliseconds), g_uiSASRuntimeSessionSerial, iGameTurn, iAutoPlayRemaining,
		aSASRuntimeStatusReasonNames[eReason], g_bSASRuntimeCivilopediaVisible, getSASRuntimeCivilopediaContext(), g_iSASRuntimeCivilopediaActivePlayer, g_iSASRuntimeCivilopediaActiveCivilization,
		g_bSASRuntimeButtonPopupAwaitingInteraction ? 1 : 0, getSASButtonPopupTypeName(g_eSASRuntimeButtonPopupType), (int)g_eSASRuntimeButtonPopupType, g_iSASRuntimeButtonPopupActivePlayer,
		g_szSASRuntimeButtonPopupFocusedUtc.GetCString(), g_szSASRuntimeButtonPopupResolvedUtc.GetCString(), g_szSASRuntimeButtonPopupResolution.GetCString(), g_iSASRuntimeButtonPopupResponseButton,
		(eReason == SAS_RUNTIME_STATUS_AUTOPLAY_ENDED ? getSASAutoPlayEndCause(g_eSASRuntimeLastAutoplayEndCause) : "-"), g_uiSASRuntimeStatusWriteFailures, g_uiSASRuntimeHistoryWriteFailures);
	recordSASRuntimeHistoryRow(szRow);
}

// <!-- custom: Write one small current-state JSON file for external agents.
// This snapshot stays overwrite-only; the companion JSONL retains timed activity transitions and one compact completed-turn player summary without rewriting an ever-growing current-state file.
// Readers may momentarily catch the short CREATE_ALWAYS rewrite and should retry malformed JSON; avoiding rename/delete semantics keeps ordinary readers from blocking updates.
// Its fixed name is a discovery endpoint; the timestamped runtime timeline retains coarse state intervals, while SASGameRecord owns detailed game/action evidence.
// The dedicated enable flag controls direct writes independently of LoggingEnabled/MessageLog/RandLog/SynchLog; OverwriteLogs does not apply to a current-state snapshot.
// No FlushFileBuffers is requested. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
static bool publishSASRuntimeStatus(SASRuntimeStatusReason eReason)
{
	if (!isSASRuntimeStatusEnabled())
		return true;
	FAssert(eReason >= 0 && eReason < NUM_SAS_RUNTIME_STATUS_REASONS);
	if (eReason < 0 || eReason >= NUM_SAS_RUNTIME_STATUS_REASONS)
		return false;
	// <!-- custom: Do not retry window discovery on ordinary turn heartbeats; startup/menu/session/request boundaries provide repeated low-frequency opportunities to arm the observer if the window did not exist yet. (ChatGPT-5.6-Sol) -->
	if (eReason != SAS_RUNTIME_STATUS_TURN_COMPLETED && eReason != SAS_RUNTIME_STATUS_PLAYER_TURN_PROGRESS && eReason != SAS_RUNTIME_STATUS_PLAYER_TURN_ENDED && eReason != SAS_RUNTIME_STATUS_PROCESS_EXIT && !isSASRuntimeWindowCloseReason(eReason))
		ensureSASRuntimeWindowMessageHook();
	// <!-- custom: Sample the observed boundary before root discovery or file I/O, so slow publication does not redefine when creation/loading or autoplay changed state. (GPT-6.1-Sol) -->
	CvString const szUpdatedUtc = createSASUtcTimestampMilliseconds();
	if (isSASRuntimeWindowCloseReason(eReason))
		g_szSASRuntimeWindowCloseRequestObservedUtc = szUpdatedUtc;
	uint const uiNowMilliseconds = getSASMonotonicMilliseconds();
	bool const bRootReady = resolveSASRuntimeStatusDefaultRootDirectory();
	std::wstring const szLogDirectory = g_szSASRuntimeStatusRootDirectory + L"\\Logs";
	bool const bDirectoryReady = bRootReady && (CreateDirectoryW(szLogDirectory.c_str(), NULL) || GetLastError() == ERROR_ALREADY_EXISTS);
	std::wstring const szPath = szLogDirectory + L"\\SASRuntimeStatus.json";

	CvGame const& kGame = GC.getGame();
	// <!-- custom: During load/reset, final-initialized state can belong to an earlier lifecycle boundary; SESSION_STARTING/NO_GAME must not publish ready-game fields. (GPT-6.1-Sol) -->
	bool const bGameLoaded = (g_eSASRuntimeGameState != SAS_RUNTIME_GAME_NO_GAME && g_eSASRuntimeGameState != SAS_RUNTIME_GAME_SESSION_STARTING && kGame.isFinalInitialized());
	int const iGameTurn = (bGameLoaded ? kGame.getGameTurn() : -1);
	int const iElapsedGameTurns = (bGameLoaded ? kGame.getElapsedGameTurns() : -1);
	int const iActivePlayer = (bGameLoaded ? kGame.getActivePlayer() : -1);
	int const iAutoPlayRemaining = (bGameLoaded ? std::max(0, kGame.getAIAutoPlay()) : 0);
	int const iMapWidth = (bGameLoaded ? GC.getMap().getGridWidth() : -1);
	int const iMapHeight = (bGameLoaded ? GC.getMap().getGridHeight() : -1);
	int const iWorldSize = (bGameLoaded ? (int)GC.getMap().getWorldSize() : -1);
	int const iGameSpeed = (bGameLoaded ? (int)kGame.getGameSpeedType() : -1);
	int const iScenario = (bGameLoaded ? (int)kGame.isScenario() : 0);
	int const iExtendedGame = (bGameLoaded && kGame.getGameState() == GAMESTATE_EXTENDED ? 1 : 0);
	int const iLoadedCheckpointTurn = (bGameLoaded && g_eSASRuntimeSessionKind == SAS_RUNTIME_SESSION_LOAD_GAME ? kGame.getSASLoadedSaveCheckpointTurn() : -1);
	int const iLoadedCheckpointElapsedTurn = (bGameLoaded && g_eSASRuntimeSessionKind == SAS_RUNTIME_SESSION_LOAD_GAME ? kGame.getSASLoadedSaveCheckpointElapsedTurn() : -1);
	char const* szLoadedCheckpointUtc = "-";
	if (bGameLoaded && g_eSASRuntimeSessionKind == SAS_RUNTIME_SESSION_LOAD_GAME && kGame.getSASLoadedSaveCheckpointUtc() != NULL && kGame.getSASLoadedSaveCheckpointUtc()[0] != '\0')
		szLoadedCheckpointUtc = kGame.getSASLoadedSaveCheckpointUtc();
	// <!-- custom: Timing fields below, including the JSON literal fields, are prepared inside this already-enabled publisher; absent player context uses explicit sentinel values rather than fabricating current execution. (GPT-6.1-Sol) -->
	SASRuntimePlayerTurnMode const ePlayerTurnMode = getSASRuntimePlayerTurnMode();
	bool const bPlayerTurnActive = (g_eSASRuntimePlayerTurnPlayer != NO_PLAYER && ePlayerTurnMode == SAS_RUNTIME_PLAYER_TURN_MODE_SEQUENTIAL);
	__int64 const iPlayerTurnElapsedMilliseconds = (bPlayerTurnActive ? (__int64)getSASElapsedMilliseconds(g_uiSASRuntimePlayerTurnStartedMilliseconds, uiNowMilliseconds) : (__int64)-1);
	__int64 const iPlayerTurnPhaseElapsedMilliseconds = (bPlayerTurnActive ? (__int64)getSASElapsedMilliseconds(g_uiSASRuntimePlayerTurnPhaseStartedMilliseconds, uiNowMilliseconds) : (__int64)-1);
	if (bGameLoaded)
		captureSASRuntimeHistorySessionMetadata(szUpdatedUtc, iGameTurn, iActivePlayer, iMapWidth, iMapHeight, iWorldSize, iGameSpeed, iScenario, iLoadedCheckpointTurn, iLoadedCheckpointElapsedTurn, szLoadedCheckpointUtc);
	// <!-- custom: Failed output must not postpone the observed transition or inflate the next interval; retain timing in memory and disclose unsuccessful history appends when publication resumes. (GPT-6.1-Sol) -->
	if (bDirectoryReady)
	{
		prepareSASRuntimeHistory(g_szSASRuntimeStatusRootDirectory);
		ensureSASRuntimeHistoryMetadata();
		// <!-- custom: Normally session context precedes its ready transition; after I/O failure, retry the captured context even if this update reports a menu/reset boundary. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
		ensureSASRuntimeHistorySessionMetadata();
		if (eReason == SAS_RUNTIME_STATUS_END_TURN_REQUEST_ACCEPTED)
			recordSASRuntimeEndTurnContext(iGameTurn);
		if (eReason == SAS_RUNTIME_STATUS_TURN_COMPLETED)
			recordSASRuntimePlayerTurnSummary(g_iSASRuntimeLastCompletedTurn, szUpdatedUtc);
	}
	else g_bSASRuntimeHistoryAtCurrentRoot = false;
	updateSASRuntimeActivity(eReason, szUpdatedUtc, uiNowMilliseconds, iGameTurn, iAutoPlayRemaining);
	if (!bDirectoryReady)
		return false;
	ensureSASRuntimeExitObserver(szPath);
	ensureSASRuntimeSourceObserver(szPath);
	g_uiSASRuntimeStatusSerial++;
	// <!-- custom: Cache DLL identity only after the status gate; disabled runs do no provenance work, and enabled turn updates never rehash the binary or rescan build outputs. (GPT-6.1-Sol) -->
	CvString const& szDllIdentity = getSASRuntimeDllIdentity(true);
	CvString const szSourceIdentity = getSASSourceRuntimeIdentityJson(true);
	CvString szJson;
	// <!-- custom: Indent the current-state snapshot for direct inspection as well as agent parsing; whitespace does not change its JSON fields. (GPT-6.1-Sol) -->
	szJson.Format("{\r\n"
		"  \"revision\": %d,\r\n"
		"  \"dllIdentity\": %s,\r\n"
		"  \"sourceIdentity\": %s,\r\n"
		"  \"statusSerial\": %u,\r\n"
		"  \"statusWriteFailures\": %u,\r\n"
		"  \"processId\": %lu,\r\n"
		"  \"processStartUtc\": \"%s\",\r\n"
		"  \"dllLoadUtc\": \"%s\",\r\n"
		"  \"updatedUtc\": \"%s\",\r\n"
		"  \"processState\": \"%s\",\r\n"
		"  \"exitObserverProcessId\": %lu,\r\n"
		"  \"exitObserverLaunchError\": %lu,\r\n"
		"  \"exitObservationFilename\": \"SASRuntimeExit_%s_%lu.json\",\r\n"
		"  \"sourceWatchEnabled\": %d,\r\n"
		"  \"sourceWatchObserverProcessId\": %lu,\r\n"
		"  \"sourceWatchLaunchError\": %lu,\r\n"
		"  \"sourceWatchStateFilename\": \"SASRuntimeSourceWatch_%s_%lu.json\",\r\n"
		"  \"sourceWatchHistoryFilename\": \"SASRuntimeSourceChanges_%s_%lu.jsonl\",\r\n"
		"  \"windowCloseObservationArmed\": %d,\r\n"
		"  \"windowCloseRequestObservedUtc\": \"%s\",\r\n"
		"  \"gameState\": \"%s\",\r\n"
		"  \"activity\": \"%s\",\r\n"
		"  \"activitySerial\": %u,\r\n"
		"  \"activityStartedUtc\": \"%s\",\r\n"
		"  \"activityElapsedMilliseconds\": %u,\r\n"
		"  \"previousActivity\": \"%s\",\r\n"
		"  \"previousActivityStartedUtc\": \"%s\",\r\n"
		"  \"previousActivityEndedUtc\": \"%s\",\r\n"
		"  \"previousActivityDurationMilliseconds\": %I64d,\r\n"
		"  \"historyFilename\": \"%s\",\r\n"
		"  \"historyAtCurrentRoot\": %d,\r\n"
		"  \"historyRowsWritten\": %u,\r\n"
		"  \"historyWriteFailures\": %u,\r\n"
		"  \"updateReason\": \"%s\",\r\n"
		"  \"sessionSerial\": %u,\r\n"
		"  \"newGameCount\": %u,\r\n"
		"  \"loadCount\": %u,\r\n"
		"  \"sessionKind\": \"%s\",\r\n"
		"  \"sessionStartedUtc\": \"%s\",\r\n"
		"  \"nativeReadyUtc\": \"%s\",\r\n"
		"  \"mainMenuSceneRequestedUtc\": \"%s\",\r\n"
		"  \"mainMenuStateObservedUtc\": \"%s\",\r\n"
		"  \"loadingScreenAssetRequestedUtc\": \"%s\",\r\n"
		"  \"pythonPreGameStartUtc\": \"%s\",\r\n"
		"  \"worldBuilderMode\": %d,\r\n"
		"  \"worldBuilderScreenVisible\": %d,\r\n"
		"  \"civilopediaVisible\": %d,\r\n"
		"  \"civilopediaContext\": \"%s\",\r\n"
		"  \"civilopediaActivePlayer\": %d,\r\n"
		"  \"civilopediaActiveCivilization\": %d,\r\n"
		"  \"buttonPopupAwaitingInteraction\": %d,\r\n"
		"  \"buttonPopupType\": \"%s\",\r\n"
		"  \"buttonPopupTypeId\": %d,\r\n"
		"  \"buttonPopupActivePlayer\": %d,\r\n"
		"  \"buttonPopupFocusedUtc\": \"%s\",\r\n"
		"  \"buttonPopupResolvedUtc\": \"%s\",\r\n"
		"  \"buttonPopupResolution\": \"%s\",\r\n"
		"  \"buttonPopupResponseButton\": %d,\r\n"
		"  \"extendedGame\": %d,\r\n"
		"  \"gameTurn\": %d,\r\n"
		"  \"elapsedGameTurns\": %d,\r\n"
		"  \"lastCompletedTurn\": %d,\r\n"
		"  \"activePlayer\": %d,\r\n"
		"  \"playerTurnTimingMode\": \"%s\",\r\n"
		"  \"playerTurnPlayer\": %d,\r\n"
		"  \"playerTurnTeam\": %d,\r\n"
		"  \"playerTurnCivilization\": %d,\r\n"
		"  \"playerTurnCivilizationType\": \"%s\",\r\n"
		"  \"playerTurnControl\": \"%s\",\r\n"
		"  \"playerTurnPhase\": \"%s\",\r\n"
		"  \"playerTurnStartedUtc\": \"%s\",\r\n"
		"  \"playerTurnElapsedMilliseconds\": %I64d,\r\n"
		"  \"playerTurnPhaseStartedUtc\": \"%s\",\r\n"
		"  \"playerTurnPhaseElapsedMilliseconds\": %I64d,\r\n"
		"  \"playerTurnSummaryTurn\": %d,\r\n"
		"  \"playerTurnSummaryPlayersMeasured\": %u,\r\n"
		"  \"playerTurnSummaryBoundariesComplete\": %d,\r\n"
		"  \"playerTurnLiveThresholdMilliseconds\": %d,\r\n"
		"  \"playerTurnLiveRefreshMilliseconds\": %d,\r\n"
		"  \"endTurnReadyUiActive\": %d,\r\n"
		"  \"endTurnReadySinceUtc\": \"%s\",\r\n"
		"  \"endTurnReadyUiElapsedMilliseconds\": %I64d,\r\n"
		"  \"endTurnReadyUiTotalMilliseconds\": %u,\r\n"
		"  \"playerTurnSkipOrdersApplied\": %u,\r\n"
		"  \"endTurnRequestObserved\": %d,\r\n"
		"  \"endTurnRequestRecordedUtc\": \"%s\",\r\n"
		"  \"endTurnRequestControl\": \"%s\",\r\n"
		"  \"endTurnRequestControlId\": %d,\r\n"
		"  \"endTurnRequestUiReady\": %d,\r\n"
		"  \"endTurnRequestReadyUiMilliseconds\": %u,\r\n"
		"  \"endTurnRequestOrderableGroups\": %d,\r\n"
		"  \"endTurnRequestOrderableUnits\": %d,\r\n"
		"  \"endTurnRequestBusyGroups\": %d,\r\n"
		"  \"endTurnRequestAutoReadyGroups\": %d,\r\n"
		"  \"autoplayActive\": %d,\r\n"
		"  \"autoplayRemainingTurns\": %d,\r\n"
		"  \"mapWidth\": %d,\r\n"
		"  \"mapHeight\": %d,\r\n"
		"  \"worldSize\": %d,\r\n"
		"  \"gameSpeed\": %d,\r\n"
		"  \"scenario\": %d,\r\n"
		"  \"loadedSaveCheckpointTurn\": %d,\r\n"
		"  \"loadedSaveCheckpointElapsedTurn\": %d,\r\n"
		"  \"loadedSaveCheckpointUtc\": \"%s\"\r\n"
		"}\r\n",
		SAS_RUNTIME_REVISION, szDllIdentity.GetCString(), szSourceIdentity.GetCString(), g_uiSASRuntimeStatusSerial, g_uiSASRuntimeStatusWriteFailures, (unsigned long)GetCurrentProcessId(), getSASExecutableProcessStartUtc().GetCString(), getSASProcessUtcTimestamp().GetCString(), szUpdatedUtc.GetCString(),
		aSASRuntimeProcessStateNames[g_eSASRuntimeProcessState], (unsigned long)g_uiSASRuntimeExitObserverProcessId, (unsigned long)g_uiSASRuntimeExitObserverLaunchError, getSASExecutableProcessStartUtc().GetCString(), (unsigned long)GetCurrentProcessId(),
		(isSASRuntimeSourceWatchEnabled() ? 1 : 0), (unsigned long)g_uiSASRuntimeSourceObserverProcessId, (unsigned long)g_uiSASRuntimeSourceObserverLaunchError,
		getSASExecutableProcessStartUtc().GetCString(), (unsigned long)GetCurrentProcessId(), getSASExecutableProcessStartUtc().GetCString(), (unsigned long)GetCurrentProcessId(),
		(g_bSASRuntimeWindowCloseObservationArmed ? 1 : 0), g_szSASRuntimeWindowCloseRequestObservedUtc.GetCString(),
		aSASRuntimeGameStateNames[g_eSASRuntimeGameState],
		aSASRuntimeActivityNames[g_eSASRuntimeActivity], g_uiSASRuntimeActivitySerial, g_szSASRuntimeActivityStartedUtc.GetCString(), getSASElapsedMilliseconds(g_uiSASRuntimeActivityStartedMilliseconds, uiNowMilliseconds),
		aSASRuntimeActivityNames[g_eSASRuntimePreviousActivity], g_szSASRuntimePreviousStartedUtc.GetCString(), g_szSASRuntimePreviousEndedUtc.GetCString(), g_iSASRuntimePreviousDurationMilliseconds,
		g_szSASRuntimeHistoryFilename.GetCString(), g_bSASRuntimeHistoryAtCurrentRoot, g_uiSASRuntimeHistoryRowsWritten, g_uiSASRuntimeHistoryWriteFailures,
		aSASRuntimeStatusReasonNames[eReason], g_uiSASRuntimeSessionSerial, g_uiSASRuntimeNewGameCount, g_uiSASRuntimeLoadCount,
		aSASRuntimeSessionStateNames[g_eSASRuntimeSessionKind], g_szSASRuntimeSessionStartedUtc.GetCString(), g_szSASRuntimeNativeReadyUtc.GetCString(),
		g_szSASRuntimeMainMenuSceneRequestedUtc.GetCString(), g_szSASRuntimeMainMenuStateObservedUtc.GetCString(), g_szSASRuntimeLoadingScreenAssetRequestedUtc.GetCString(), g_szSASRuntimePythonPreGameStartUtc.GetCString(),
		g_bSASRuntimeWorldBuilderMode, g_bSASRuntimeWorldBuilderScreenVisible, g_bSASRuntimeCivilopediaVisible, getSASRuntimeCivilopediaContext(), g_iSASRuntimeCivilopediaActivePlayer, g_iSASRuntimeCivilopediaActiveCivilization,
		g_bSASRuntimeButtonPopupAwaitingInteraction ? 1 : 0, getSASButtonPopupTypeName(g_eSASRuntimeButtonPopupType), (int)g_eSASRuntimeButtonPopupType, g_iSASRuntimeButtonPopupActivePlayer,
		g_szSASRuntimeButtonPopupFocusedUtc.GetCString(), g_szSASRuntimeButtonPopupResolvedUtc.GetCString(), g_szSASRuntimeButtonPopupResolution.GetCString(), g_iSASRuntimeButtonPopupResponseButton, iExtendedGame,
		iGameTurn, iElapsedGameTurns, g_iSASRuntimeLastCompletedTurn, iActivePlayer,
		aSASRuntimePlayerTurnModeNames[ePlayerTurnMode], bPlayerTurnActive ? (int)g_eSASRuntimePlayerTurnPlayer : -1, bPlayerTurnActive ? (int)g_eSASRuntimePlayerTurnTeam : -1, bPlayerTurnActive ? (int)g_eSASRuntimePlayerTurnCivilization : -1,
		bPlayerTurnActive ? g_szSASRuntimePlayerTurnCivilizationType.GetCString() : "-", bPlayerTurnActive ? aSASRuntimePlayerTurnControlNames[g_eSASRuntimePlayerTurnControl] : aSASRuntimePlayerTurnControlNames[SAS_RUNTIME_PLAYER_TURN_CONTROL_NONE],
		bPlayerTurnActive ? aSASRuntimePlayerTurnPhaseNames[g_eSASRuntimePlayerTurnPhase] : aSASRuntimePlayerTurnPhaseNames[SAS_RUNTIME_PLAYER_TURN_PHASE_NONE], bPlayerTurnActive ? g_szSASRuntimePlayerTurnStartedUtc.GetCString() : "-", iPlayerTurnElapsedMilliseconds,
		bPlayerTurnActive ? g_szSASRuntimePlayerTurnPhaseStartedUtc.GetCString() : "-", iPlayerTurnPhaseElapsedMilliseconds, g_iSASRuntimePlayerTurnSummaryTurn, (unsigned int)g_aSASRuntimePlayerTurnRecords.size(), g_bSASRuntimePlayerTurnSummaryBoundariesComplete ? 1 : 0,
		getSASRuntimePlayerTurnLiveThresholdMilliseconds(), getSASRuntimePlayerTurnLiveRefreshMilliseconds(),
		(g_bSASRuntimeEndTurnReadyUI ? 1 : 0), g_bSASRuntimeEndTurnReadyUI ? g_szSASRuntimeEndTurnReadySinceUtc.GetCString() : "-",
		(g_bSASRuntimeEndTurnReadyUI ? (__int64)getSASElapsedMilliseconds(g_uiSASRuntimeEndTurnReadyStartedMilliseconds, uiNowMilliseconds) : (__int64)-1), getSASRuntimeEndTurnReadyMilliseconds(uiNowMilliseconds), g_uiSASRuntimeSkipOrdersApplied,
		(g_bSASRuntimeEndTurnRequestObserved ? 1 : 0), g_bSASRuntimeEndTurnRequestObserved ? g_szSASRuntimeEndTurnRequestRecordedUtc.GetCString() : "-",
		g_bSASRuntimeEndTurnRequestObserved ? getSASRuntimeEndTurnControlName(g_eSASRuntimeEndTurnRequestControl) : "UNAVAILABLE", g_bSASRuntimeEndTurnRequestObserved ? (int)g_eSASRuntimeEndTurnRequestControl : -1,
		g_bSASRuntimeEndTurnRequestObserved && g_bSASRuntimeEndTurnRequestUIReady ? 1 : 0, g_bSASRuntimeEndTurnRequestObserved ? g_uiSASRuntimeEndTurnRequestReadyMilliseconds : 0,
		g_bSASRuntimeEndTurnRequestObserved ? g_kSASRuntimeEndTurnRequestReadiness.iOrderableGroups : -1, g_bSASRuntimeEndTurnRequestObserved ? g_kSASRuntimeEndTurnRequestReadiness.iOrderableUnits : -1,
		g_bSASRuntimeEndTurnRequestObserved ? g_kSASRuntimeEndTurnRequestReadiness.iBusyGroups : -1, g_bSASRuntimeEndTurnRequestObserved ? g_kSASRuntimeEndTurnRequestReadiness.iAutoReadyGroups : -1,
		(iAutoPlayRemaining > 0 ? 1 : 0), iAutoPlayRemaining, iMapWidth, iMapHeight, iWorldSize, iGameSpeed, iScenario,
		iLoadedCheckpointTurn, iLoadedCheckpointElapsedTurn, szLoadedCheckpointUtc);

	HANDLE const hFile = CreateFileW(szPath.c_str(), GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
	if (hFile == INVALID_HANDLE_VALUE)
		return false;
	size_t iWrittenTotal = 0;
	bool bWriteSucceeded = true;
	while (iWrittenTotal < szJson.size())
	{
		DWORD iWritten = 0;
		DWORD const iChunk = (DWORD)std::min(szJson.size() - iWrittenTotal, (size_t)0xffffffff);
		BOOL const bWritten = WriteFile(hFile, szJson.GetCString() + iWrittenTotal, iChunk, &iWritten, NULL);
		iWrittenTotal += iWritten;
		if (!bWritten || iWritten == 0)
		{
			bWriteSucceeded = false;
			break;
		}
	}
	// <!-- custom: A reported failed write can acknowledge the entire byte count; require successful write/close results before retiring the fallback copy. (GPT-6.1-Sol) -->
	BOOL const bClosed = CloseHandle(hFile);
	bool const bComplete = (bWriteSucceeded && iWrittenTotal == szJson.size() && bClosed != FALSE);
	if (bComplete)
	{
		if (g_eSASRuntimePlayerTurnPlayer != NO_PLAYER)
			g_bSASRuntimePlayerTurnContextPublished = true;
		g_szSASRuntimeStatusLastPublishedRoot = g_szSASRuntimeStatusRootDirectory;
		if (!g_szSASRuntimeStatusSupersededPath.empty())
		{
			if (isSASRuntimeStatusSamePath(g_szSASRuntimeStatusSupersededPath, szPath) || DeleteFileW(g_szSASRuntimeStatusSupersededPath.c_str()) || GetLastError() == ERROR_FILE_NOT_FOUND)
				g_szSASRuntimeStatusSupersededPath.clear();
		}
	}
	return bComplete;
}

// <!-- custom: Count every failed publication once, including root/open/write/close failures; the next successful snapshot reports the cumulative count without retaining a failure history. (ChatGPT + GPT-6.1-Sol) -->
// <!-- custom: The publisher owns the first cached enablement guard; this wrapper only accounts for publication failure, so a disabled call returns without timestamp/string/I/O work or failure-counter mutation. (GPT-6.1-Sol) -->
static bool writeSASRuntimeStatus(SASRuntimeStatusReason eReason)
{
	bool const bPublished = publishSASRuntimeStatus(eReason);
	if (!bPublished)
		g_uiSASRuntimeStatusWriteFailures++;
	return bPublished;
}

// <!-- custom: Reset always publishes GAME_RESET; removing the free-form label keeps the fixed event catalog authoritative. (GPT-6.1-Sol) -->
void updateSASRuntimeStatusNoGame()
{
	if (!isSASRuntimeStatusEnabled())
		return;
	g_eSASRuntimeGameState = SAS_RUNTIME_GAME_NO_GAME;
	g_eSASRuntimeSessionKind = SAS_RUNTIME_SESSION_NONE;
	g_szSASRuntimeSessionStartedUtc = "-";
	g_szSASRuntimeNativeReadyUtc = "-";
	g_szSASRuntimeMainMenuSceneRequestedUtc = "-";
	g_szSASRuntimeMainMenuStateObservedUtc = "-";
	g_szSASRuntimeLoadingScreenAssetRequestedUtc = "-";
	g_szSASRuntimePythonPreGameStartUtc = "-";
	g_bSASRuntimeWorldBuilderMode = false;
	g_bSASRuntimeWorldBuilderScreenVisible = false;
	g_bSASRuntimeCivilopediaVisible = false;
	g_eSASRuntimeCivilopediaContext = SAS_RUNTIME_CIVILOPEDIA_NONE;
	g_iSASRuntimeCivilopediaActivePlayer = -1;
	g_iSASRuntimeCivilopediaActiveCivilization = -1;
	g_bSASRuntimeButtonPopupAwaitingInteraction = false;
	g_eSASRuntimeButtonPopupType = NO_BUTTONPOPUP;
	g_iSASRuntimeButtonPopupActivePlayer = -1;
	g_szSASRuntimeButtonPopupFocusedUtc = "-";
	g_szSASRuntimeButtonPopupResolvedUtc = "-";
	g_szSASRuntimeButtonPopupResolution = "-";
	g_iSASRuntimeButtonPopupResponseButton = -1;
	g_pSASRuntimeButtonPopup = NULL;
	g_iSASRuntimeLastCompletedTurn = -1;
	resetSASRuntimePlayerTurnTiming();
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_GAME_RESET);
}

// <!-- custom: CvMainMenuInfo scene getters are DllExports consumed by the EXE and have no local caller; observing an existing request avoids calling side-effectful soundtrack code or polling CyInterface().
// Record this only while no game is represented and once per no-game interval.
// It is presentation evidence, not proof that a rendered frame reached the user. (ChatGPT-5.6-Sol) -->
void updateSASRuntimeStatusMainMenuSceneRequested()
{
	if (!isSASRuntimeStatusEnabled() || g_eSASRuntimeGameState != SAS_RUNTIME_GAME_NO_GAME || g_szSASRuntimeMainMenuSceneRequestedUtc != "-")
		return;
	g_szSASRuntimeMainMenuSceneRequestedUtc = createSASUtcTimestampMilliseconds();
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_MAIN_MENU_SCENE_REQUESTED);
}

// <!-- custom: Sample the Python-provided main-menu Boolean only from explicit menu-capable screen entry points.
// A positive sample proves EXE main-menu state at that callback, but can occur long after initial arrival; retain the first positive sample per no-game interval without frame polling. (ChatGPT-5.6-Sol) -->
void updateSASRuntimeStatusMainMenuState(bool bInMainMenu)
{
	if (!isSASRuntimeStatusEnabled() || !bInMainMenu || g_eSASRuntimeGameState != SAS_RUNTIME_GAME_NO_GAME || g_szSASRuntimeMainMenuStateObservedUtc != "-")
		return;
	g_szSASRuntimeMainMenuStateObservedUtc = createSASUtcTimestampMilliseconds();
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_MAIN_MENU_STATE_OBSERVED);
}

void updateSASRuntimeStatusSessionStarted(bool bLoadedSave)
{
	if (!isSASRuntimeStatusEnabled())
		return;
	g_uiSASRuntimeSessionSerial++;
	if (bLoadedSave)
	{
		g_uiSASRuntimeLoadCount++;
		g_eSASRuntimeSessionKind = SAS_RUNTIME_SESSION_LOAD_GAME;
	}
	else
	{
		g_uiSASRuntimeNewGameCount++;
		g_eSASRuntimeSessionKind = SAS_RUNTIME_SESSION_NEW_GAME;
	}
	g_eSASRuntimeGameState = SAS_RUNTIME_GAME_SESSION_STARTING;
	g_szSASRuntimeSessionStartedUtc = createSASUtcTimestampMilliseconds();
	g_szSASRuntimeNativeReadyUtc = "-";
	g_szSASRuntimeMainMenuSceneRequestedUtc = "-";
	g_szSASRuntimeMainMenuStateObservedUtc = "-";
	g_szSASRuntimeLoadingScreenAssetRequestedUtc = "-";
	g_szSASRuntimePythonPreGameStartUtc = "-";
	g_bSASRuntimeWorldBuilderMode = false;
	g_bSASRuntimeWorldBuilderScreenVisible = false;
	g_bSASRuntimeCivilopediaVisible = false;
	g_eSASRuntimeCivilopediaContext = SAS_RUNTIME_CIVILOPEDIA_NONE;
	g_iSASRuntimeCivilopediaActivePlayer = -1;
	g_iSASRuntimeCivilopediaActiveCivilization = -1;
	g_bSASRuntimeButtonPopupAwaitingInteraction = false;
	g_eSASRuntimeButtonPopupType = NO_BUTTONPOPUP;
	g_iSASRuntimeButtonPopupActivePlayer = -1;
	g_szSASRuntimeButtonPopupFocusedUtc = "-";
	g_szSASRuntimeButtonPopupResolvedUtc = "-";
	g_szSASRuntimeButtonPopupResolution = "-";
	g_iSASRuntimeButtonPopupResponseButton = -1;
	g_pSASRuntimeButtonPopup = NULL;
	g_iSASRuntimeLastCompletedTurn = -1;
	resetSASRuntimePlayerTurnTiming();
	writeSASRuntimeStatus(bLoadedSave ? SAS_RUNTIME_STATUS_LOAD_GAME_STARTED : SAS_RUNTIME_STATUS_NEW_GAME_STARTED);
}

// <!-- custom: getLoading/getLoadingSlideshow are passive EXE-facing asset requests.
// Preserve the first request inside each native new/load interval as a loading-presentation proxy without calling either getter ourselves. (ChatGPT-5.6-Sol) -->
void updateSASRuntimeStatusLoadingScreenAssetRequested()
{
	if (!isSASRuntimeStatusEnabled() || g_eSASRuntimeGameState != SAS_RUNTIME_GAME_SESSION_STARTING || g_szSASRuntimeLoadingScreenAssetRequestedUtc != "-")
		return;
	g_szSASRuntimeLoadingScreenAssetRequestedUtc = createSASUtcTimestampMilliseconds();
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_LOADING_SCREEN_ASSET_REQUESTED);
}

// <!-- custom: BUG's PreGameStart extension is an EXE-driven initialization callback shared by new and loaded games.
// Record it once for the current session without assuming its order relative to native-ready on every load path; it does not prove that a loading image or slideshow frame was actually rendered. (ChatGPT-5.6-Sol) -->
void updateSASRuntimeStatusPreGameStart()
{
	if (!isSASRuntimeStatusEnabled() || g_eSASRuntimeSessionKind == SAS_RUNTIME_SESSION_NONE || g_szSASRuntimePythonPreGameStartUtc != "-")
		return;
	g_szSASRuntimePythonPreGameStartUtc = createSASUtcTimestampMilliseconds();
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_PYTHON_PRE_GAME_START);
}

void updateSASRuntimeStatusSessionReady()
{
	if (!isSASRuntimeStatusEnabled())
		return;
	g_eSASRuntimeGameState = SAS_RUNTIME_GAME_PLAYING;
	g_szSASRuntimeNativeReadyUtc = createSASUtcTimestampMilliseconds();
	writeSASRuntimeStatus(g_eSASRuntimeSessionKind == SAS_RUNTIME_SESSION_LOAD_GAME ? SAS_RUNTIME_STATUS_LOAD_GAME_NATIVE_READY : SAS_RUNTIME_STATUS_NEW_GAME_NATIVE_READY);
}

// <!-- custom: ePlayer is the native player whose ordinary sequential turn has just become active.
// Caller gates skip diagnostic argument preparation; this public entry also returns on the cached disabled switch before game lookups, timestamps or record work, including when called directly.
// This early return is a defensive in-function guard, not caller pre-gating: arguments have already been evaluated and this function has been entered.
// Production CvPlayer/CvGame hooks also pre-gate the call (or their enclosing block) so disabled runs skip it entirely; Main, Ending, Ended and Progress follow the same contract.
// Start measuring before activation/setup work; no history/status row is written here, and an unexpected overlapping start degrades the compact turn summary instead of guessing which boundary was lost. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
void updateSASRuntimeStatusPlayerTurnStarted(PlayerTypes ePlayer)
{
	if (!isSASRuntimeStatusEnabled() || ePlayer == NO_PLAYER || getSASRuntimePlayerTurnMode() != SAS_RUNTIME_PLAYER_TURN_MODE_SEQUENTIAL)
		return;
	CvGame const& kGame = GC.getGame();
	int const iGameTurn = kGame.getGameTurn();
	if (g_iSASRuntimePlayerTurnSummaryTurn != iGameTurn)
	{
		bool const bHadOlderEvidence = (g_iSASRuntimePlayerTurnSummaryTurn >= 0 || !g_aSASRuntimePlayerTurnRecords.empty());
		clearSASRuntimeCurrentPlayerTurn();
		g_aSASRuntimePlayerTurnRecords.clear();
		g_iSASRuntimePlayerTurnSummaryTurn = iGameTurn;
		g_bSASRuntimePlayerTurnSummaryBoundariesComplete = !bHadOlderEvidence;
	}
	if (g_eSASRuntimePlayerTurnPlayer != NO_PLAYER)
	{
		g_bSASRuntimePlayerTurnSummaryBoundariesComplete = false;
		clearSASRuntimeCurrentPlayerTurn();
	}
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	g_eSASRuntimePlayerTurnPlayer = ePlayer;
	g_eSASRuntimePlayerTurnTeam = kPlayer.getTeam();
	g_eSASRuntimePlayerTurnCivilization = kPlayer.getCivilizationType();
	g_eSASRuntimePlayerTurnControl = getSASRuntimePlayerTurnControl(kPlayer);
	g_eSASRuntimePlayerTurnPhase = SAS_RUNTIME_PLAYER_TURN_PHASE_ACTIVATING;
	g_szSASRuntimePlayerTurnCivilizationType = (g_eSASRuntimePlayerTurnCivilization == NO_CIVILIZATION ? "-" : GC.getCivilizationInfo(g_eSASRuntimePlayerTurnCivilization).getType());
	g_szSASRuntimePlayerTurnStartedUtc = createSASUtcTimestampMilliseconds();
	g_szSASRuntimePlayerTurnPhaseStartedUtc = g_szSASRuntimePlayerTurnStartedUtc;
	g_uiSASRuntimePlayerTurnStartedMilliseconds = getSASMonotonicMilliseconds();
	g_uiSASRuntimePlayerTurnPhaseStartedMilliseconds = g_uiSASRuntimePlayerTurnStartedMilliseconds;
}

// <!-- custom: The main phase begins after setTurnActive's activation/setup work returns toward ordinary movement/input processing.
// AI/HUMAN_DISABLED/BARBARIAN turns use AI_MOVES; a normal human turn uses HUMAN_INPUT, which is measured for the final summary but never drives live slow-AI refreshes.
// These are wall-clock intervals, including human thinking or popup waits; HUMAN_INPUT classifies the human-controlled phase rather than proving the EXE is idle.
// CvPlayer pre-gates the call; the disabled/mismatched-player return here is an additional in-function guard before clock reads and phase mutation. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
void updateSASRuntimeStatusPlayerTurnMain(PlayerTypes ePlayer)
{
	if (!isSASRuntimeStatusEnabled() || g_eSASRuntimePlayerTurnPlayer != ePlayer)
		return;
	uint const uiNow = getSASMonotonicMilliseconds();
	addSASRuntimeCurrentPlayerTurnPhase(uiNow);
	g_eSASRuntimePlayerTurnPhase = (g_eSASRuntimePlayerTurnControl == SAS_RUNTIME_PLAYER_TURN_CONTROL_HUMAN ? SAS_RUNTIME_PLAYER_TURN_PHASE_HUMAN_INPUT : SAS_RUNTIME_PLAYER_TURN_PHASE_AI_MOVES);
	g_szSASRuntimePlayerTurnPhaseStartedUtc = createSASUtcTimestampMilliseconds();
	g_uiSASRuntimePlayerTurnPhaseStartedMilliseconds = uiNow;
}

// <!-- custom: Begin ENDING before CvPlayer::doTurn/final cleanup so the summary separates post-movement turn work from the long active interval external users usually see as waiting.
// CvPlayer's enclosing enabled block is the caller pre-gate for this branch and the interrupted-end branch; the first return below is additional defensive gating. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
void updateSASRuntimeStatusPlayerTurnEnding(PlayerTypes ePlayer)
{
	if (!isSASRuntimeStatusEnabled())
		return;
	if (g_eSASRuntimePlayerTurnPlayer != ePlayer)
	{
		// <!-- custom: A loaded game can resume after this player's activation, before any timing record exists; preserve that missing start so later players cannot make this partial turn appear complete. (GPT-6.1-Sol) -->
		if (getSASRuntimePlayerTurnMode() == SAS_RUNTIME_PLAYER_TURN_MODE_SEQUENTIAL)
		{
			if (g_iSASRuntimePlayerTurnSummaryTurn < 0) g_iSASRuntimePlayerTurnSummaryTurn = GC.getGame().getGameTurn();
			g_bSASRuntimePlayerTurnSummaryBoundariesComplete = false;
		}
		return;
	}
	uint const uiNow = getSASMonotonicMilliseconds();
	// <!-- custom: Turn deactivation can bypass the observed UI-control request (for example a network-driven completion).
	// Stop readiness before ending work so its duration cannot absorb turn cleanup; no extra status write is needed here. (GPT-6.1-Sol) -->
	if (g_bSASRuntimeEndTurnReadyUI)
	{
		g_uiSASRuntimeEndTurnReadyMilliseconds = getSASRuntimeEndTurnReadyMilliseconds(uiNow);
		g_bSASRuntimeEndTurnReadyUI = false;
		g_szSASRuntimeEndTurnReadySinceUtc = "-";
		g_uiSASRuntimeEndTurnReadyStartedMilliseconds = 0;
	}
	addSASRuntimeCurrentPlayerTurnPhase(uiNow);
	g_eSASRuntimePlayerTurnPhase = SAS_RUNTIME_PLAYER_TURN_PHASE_ENDING;
	g_szSASRuntimePlayerTurnPhaseStartedUtc = createSASUtcTimestampMilliseconds();
	g_uiSASRuntimePlayerTurnPhaseStartedMilliseconds = uiNow;
}

// <!-- custom: Finish the current player before setTurnActive recursively activates the next civilization.
// CvPlayer pre-gates the call or its enclosing branch before evaluating arguments; retain the entry guard below for direct calls.
// bCompleted=false preserves an interrupted record but marks both it and the containing turn incomplete; clear the overwrite-only current snapshot only if some prior successful publication exposed this player context. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
void updateSASRuntimeStatusPlayerTurnEnded(PlayerTypes ePlayer, bool bCompleted)
{
	if (!isSASRuntimeStatusEnabled())
		return;
	if (g_eSASRuntimePlayerTurnPlayer != ePlayer)
	{
		// <!-- custom: Retain the incomplete-turn marker even if observation began between activation and deactivation; do not invent the missing player's duration. (GPT-6.1-Sol) -->
		if (getSASRuntimePlayerTurnMode() == SAS_RUNTIME_PLAYER_TURN_MODE_SEQUENTIAL)
		{
			if (g_iSASRuntimePlayerTurnSummaryTurn < 0) g_iSASRuntimePlayerTurnSummaryTurn = GC.getGame().getGameTurn();
			g_bSASRuntimePlayerTurnSummaryBoundariesComplete = false;
		}
		return;
	}
	uint const uiNow = getSASMonotonicMilliseconds();
	addSASRuntimeCurrentPlayerTurnPhase(uiNow);
	if (!bCompleted || g_eSASRuntimePlayerTurnPhase != SAS_RUNTIME_PLAYER_TURN_PHASE_ENDING)
		g_bSASRuntimePlayerTurnSummaryBoundariesComplete = false;
	SASRuntimePlayerTurnRecord kRecord;
	kRecord.iPlayer = (int)g_eSASRuntimePlayerTurnPlayer;
	kRecord.iTeam = (int)g_eSASRuntimePlayerTurnTeam;
	kRecord.iCivilization = (int)g_eSASRuntimePlayerTurnCivilization;
	kRecord.eControl = g_eSASRuntimePlayerTurnControl;
	kRecord.szCivilizationType = g_szSASRuntimePlayerTurnCivilizationType;
	kRecord.szStartedUtc = g_szSASRuntimePlayerTurnStartedUtc;
	kRecord.szEndedUtc = createSASUtcTimestampMilliseconds();
	kRecord.uiTotalMilliseconds = getSASElapsedMilliseconds(g_uiSASRuntimePlayerTurnStartedMilliseconds, uiNow);
	kRecord.uiActivatingMilliseconds = g_uiSASRuntimePlayerTurnActivatingMilliseconds;
	kRecord.uiMainMilliseconds = g_uiSASRuntimePlayerTurnMainMilliseconds;
	kRecord.uiEndingMilliseconds = g_uiSASRuntimePlayerTurnEndingMilliseconds;
	kRecord.uiEndTurnReadyMilliseconds = getSASRuntimeEndTurnReadyMilliseconds(uiNow);
	kRecord.uiSkipOrdersApplied = g_uiSASRuntimeSkipOrdersApplied;
	getSASRuntimeTurnReadinessSnapshot(ePlayer, true, kRecord.kEndReadiness);
	kRecord.bCompleted = bCompleted;
	g_aSASRuntimePlayerTurnRecords.push_back(kRecord);
	bool const bClearPublishedContext = g_bSASRuntimePlayerTurnContextPublished;
	clearSASRuntimeCurrentPlayerTurn();
	if (bClearPublishedContext)
		writeSASRuntimeStatus(SAS_RUNTIME_STATUS_PLAYER_TURN_ENDED);
}

// <!-- custom: Observe only actual UI end-turn-message transitions.
// This interval is distinct from HUMAN_INPUT wall time: it begins when the inherited readiness logic displays the end-turn message and stops if new orderable work appears.
// CvGame::updateTestEndTurn pre-gates the call and its arguments, after changing the UI flag; the cached disabled return below is a defensive backstop, not a replacement for that caller gate. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
void updateSASRuntimeStatusEndTurnReady(PlayerTypes ePlayer, bool bReady)
{
	if (!isSASRuntimeStatusEnabled() || g_eSASRuntimePlayerTurnPlayer != ePlayer || g_eSASRuntimePlayerTurnControl != SAS_RUNTIME_PLAYER_TURN_CONTROL_HUMAN || g_bSASRuntimeEndTurnReadyUI == bReady)
		return;
	uint const uiNow = getSASMonotonicMilliseconds();
	if (bReady)
	{
		g_bSASRuntimeEndTurnReadyUI = true;
		g_szSASRuntimeEndTurnReadySinceUtc = createSASUtcTimestampMilliseconds();
		g_uiSASRuntimeEndTurnReadyStartedMilliseconds = uiNow;
	}
	else
	{
		g_uiSASRuntimeEndTurnReadyMilliseconds += getSASElapsedMilliseconds(g_uiSASRuntimeEndTurnReadyStartedMilliseconds, uiNow);
		g_bSASRuntimeEndTurnReadyUI = false;
		g_szSASRuntimeEndTurnReadySinceUtc = "-";
		g_uiSASRuntimeEndTurnReadyStartedMilliseconds = 0;
	}
	writeSASRuntimeStatus(bReady ? SAS_RUNTIME_STATUS_END_TURN_READY : SAS_RUNTIME_STATUS_END_TURN_NOT_READY);
}

// <!-- custom: Capture applied end-turn-request context immediately before sendTurnComplete.
// `bUIAnyMove` is the exact updateTestEndTurn selected-unit/cycling rule; the snapshot also retains logical canAnyMove orderability so a force-end request with partially movable groups is visible.
// CvGame::doControl pre-gates this call and all diagnostic-only UI getters; this entry guard is a defensive backstop.
// The control enum identifies END_TURN/ALT/FORCE only; physical keyboard versus widget origin is intentionally not inferred. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
void updateSASRuntimeStatusEndTurnRequest(PlayerTypes ePlayer, ControlTypes eControl, bool bEndTurnMessage, bool bUIAnyMove, bool bSelectedUnitPresent, bool bForcePopup, bool bHasMovedUnit, bool bWaitEndTurnOption)
{
	if (!isSASRuntimeStatusEnabled() || ePlayer == NO_PLAYER || g_eSASRuntimePlayerTurnPlayer != ePlayer || g_eSASRuntimePlayerTurnControl != SAS_RUNTIME_PLAYER_TURN_CONTROL_HUMAN)
		return;
	if (eControl != CONTROL_ENDTURN && eControl != CONTROL_ENDTURN_ALT && eControl != CONTROL_FORCEENDTURN)
		return;
	uint const uiNow = getSASMonotonicMilliseconds();
	g_bSASRuntimeEndTurnRequestObserved = true;
	g_szSASRuntimeEndTurnRequestRecordedUtc = createSASUtcTimestampMilliseconds();
	g_eSASRuntimeEndTurnRequestControl = eControl;
	g_bSASRuntimeEndTurnRequestUIReady = g_bSASRuntimeEndTurnReadyUI;
	g_uiSASRuntimeEndTurnRequestReadyMilliseconds = getSASRuntimeEndTurnReadyMilliseconds(uiNow);
	// <!-- custom: An accepted request ends the user's UI-ready waiting interval even if the EXE leaves its visual message up until deactivation; the request row retains whether that ready state was active. (ChatGPT-5.6-Sol) -->
	if (g_bSASRuntimeEndTurnReadyUI)
	{
		g_uiSASRuntimeEndTurnReadyMilliseconds = g_uiSASRuntimeEndTurnRequestReadyMilliseconds;
		g_bSASRuntimeEndTurnReadyUI = false;
		g_szSASRuntimeEndTurnReadySinceUtc = "-";
		g_uiSASRuntimeEndTurnReadyStartedMilliseconds = 0;
	}
	g_uiSASRuntimeEndTurnRequestSkipOrdersApplied = g_uiSASRuntimeSkipOrdersApplied;
	g_bSASRuntimeEndTurnRequestEndTurnMessage = bEndTurnMessage;
	g_bSASRuntimeEndTurnRequestUIAnyMove = bUIAnyMove;
	g_bSASRuntimeEndTurnRequestSelectedUnit = bSelectedUnitPresent;
	g_bSASRuntimeEndTurnRequestForcePopup = bForcePopup;
	g_bSASRuntimeEndTurnRequestHasMovedUnit = bHasMovedUnit;
	g_bSASRuntimeEndTurnRequestWaitOption = bWaitEndTurnOption;
	getSASRuntimeTurnReadinessSnapshot(ePlayer, bUIAnyMove, g_kSASRuntimeEndTurnRequestReadiness);
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_END_TURN_REQUEST_ACCEPTED);
}

// <!-- custom: Count an actual applied MISSION_SKIP at its group mission boundary instead of inferring Skip from ACTIVITY_HOLD, which has other producers.
// CvSelectionGroup::startMission pre-gates the call and getOwner argument; the disabled return here is defensive.
// This is in-memory only and emits no row per mission; the compact count is exposed in current status, accepted end-turn context and the completed player-turn summary. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
void updateSASRuntimeStatusMissionSkip(PlayerTypes ePlayer)
{
	if (!isSASRuntimeStatusEnabled() || g_eSASRuntimePlayerTurnPlayer != ePlayer)
		return;
	g_uiSASRuntimeSkipOrdersApplied++;
}

// <!-- custom: CvGame caller-pre-gates this check in its ordinary update loop; the first short-circuit operand below is a defensive cached-switch guard, before mode checks, clock reads or publication.
// No per-group/AI-loop polling or helper thread is introduced.
// A long uninterrupted callback therefore cannot refresh the file until control returns here, and unchanged status alone is never evidence of a hang. (ChatGPT-5.6-Sol) -->
void updateSASRuntimeStatusPlayerTurnProgress()
{
	if (!isSASRuntimeStatusEnabled() || getSASRuntimePlayerTurnMode() != SAS_RUNTIME_PLAYER_TURN_MODE_SEQUENTIAL || g_eSASRuntimePlayerTurnPlayer == NO_PLAYER || !isSASRuntimeAIControlledPlayerTurn())
		return;
	int const iThreshold = getSASRuntimePlayerTurnLiveThresholdMilliseconds();
	if (iThreshold < 0)
		return;
	uint const uiNow = getSASMonotonicMilliseconds();
	uint const uiElapsed = getSASElapsedMilliseconds(g_uiSASRuntimePlayerTurnStartedMilliseconds, uiNow);
	if (uiElapsed < (uint)iThreshold)
		return;
	int const iRefresh = getSASRuntimePlayerTurnLiveRefreshMilliseconds();
	if (g_bSASRuntimePlayerTurnLivePublicationAttempted && (iRefresh <= 0 || getSASElapsedMilliseconds(g_uiSASRuntimePlayerTurnLastLivePublicationMilliseconds, uiNow) < (uint)iRefresh))
		return;
	g_bSASRuntimePlayerTurnLivePublicationAttempted = true;
	g_uiSASRuntimePlayerTurnLastLivePublicationMilliseconds = uiNow;
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_PLAYER_TURN_PROGRESS);
}

// <!-- custom: iCompletedTurn is the authoritative global boundary after all sequential players have ended.
// publishSASRuntimeStatus appends at most one compact player_turn_summary through the existing history writer before formatting the current snapshot. (ChatGPT-5.6-Sol) -->
void updateSASRuntimeStatusTurnCompleted(int iCompletedTurn)
{
	if (!isSASRuntimeStatusEnabled())
		return;
	g_iSASRuntimeLastCompletedTurn = iCompletedTurn;
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_TURN_COMPLETED);
}

// <!-- custom: Accept the caller's typed start/end/adjustment reason and existing completion-cause enum, so history distinguishes interruption from scheduled completion without parsing SASGameRecord. (GPT-6.1-Sol) -->
void updateSASRuntimeStatusAutoPlay(SASRuntimeStatusReason eReason, SASAutoPlayEndCause eEndCause)
{
	if (!isSASRuntimeStatusEnabled())
		return;
	g_eSASRuntimeLastAutoplayEndCause = eEndCause;
	writeSASRuntimeStatus(eReason);
}

void updateSASRuntimeStatusWorldBuilderMode(bool bEnabled)
{
	if (!isSASRuntimeStatusEnabled() || g_bSASRuntimeWorldBuilderMode == bEnabled)
		return;
	g_bSASRuntimeWorldBuilderMode = bEnabled;
	// <!-- custom: Keep the Python screen observation independent from native mode so either exit ordering remains visible: mode-off ends editor activity immediately, while the later hide callback records presentation closure. (ChatGPT-5.6-Sol) -->
	writeSASRuntimeStatus(bEnabled ? SAS_RUNTIME_STATUS_WORLD_BUILDER_MODE_ENTERED : SAS_RUNTIME_STATUS_WORLD_BUILDER_MODE_EXITED);
}

void updateSASRuntimeStatusWorldBuilderScreen(bool bVisible)
{
	if (!isSASRuntimeStatusEnabled() || g_eSASRuntimeGameState != SAS_RUNTIME_GAME_PLAYING || g_bSASRuntimeWorldBuilderScreenVisible == bVisible)
		return;
	// <!-- custom: The Python bridge filters Advanced Start before reaching this helper; retain a genuine show observation even if the EXE has not exposed its mode toggle yet.
	// Editor activity starts only once both mode and visibility are observed, so callback order cannot discard a visible screen or invent active editor time from mode alone. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
	g_bSASRuntimeWorldBuilderScreenVisible = bVisible;
	writeSASRuntimeStatus(bVisible ? SAS_RUNTIME_STATUS_WORLD_BUILDER_SCREEN_SHOWN : SAS_RUNTIME_STATUS_WORLD_BUILDER_SCREEN_HIDDEN);
}

// <!-- custom: Shows require an active screen; hides use the EXE no-screens notification or an inactive-screen check after close handlers.
// Keep the overlay separate from activity timing and retain its origin/player on the hide row, so agents can distinguish game UI from menu previews without inventing an active menu player. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
void updateSASRuntimeStatusCivilopedia(bool bVisible, bool bInMainMenu)
{
	if (!isSASRuntimeStatusEnabled())
		return;
	if (bVisible)
	{
		if (bInMainMenu ? g_eSASRuntimeGameState != SAS_RUNTIME_GAME_NO_GAME : (g_eSASRuntimeGameState != SAS_RUNTIME_GAME_PLAYING && g_eSASRuntimeGameState != SAS_RUNTIME_GAME_GAME_ENDED))
			return;
		SASRuntimeCivilopediaContext const eContext = bInMainMenu ? SAS_RUNTIME_CIVILOPEDIA_MAIN_MENU : SAS_RUNTIME_CIVILOPEDIA_IN_GAME;
		int const iPlayer = bInMainMenu ? -1 : (int)GC.getGame().getActivePlayer();
		if (g_bSASRuntimeCivilopediaVisible && g_eSASRuntimeCivilopediaContext == eContext && g_iSASRuntimeCivilopediaActivePlayer == iPlayer)
			return;
		g_eSASRuntimeCivilopediaContext = eContext;
		g_iSASRuntimeCivilopediaActivePlayer = iPlayer;
		g_iSASRuntimeCivilopediaActiveCivilization = (iPlayer < 0 ? -1 : (int)GET_PLAYER((PlayerTypes)iPlayer).getCivilizationType());
	}
	else if (!g_bSASRuntimeCivilopediaVisible)
		return;
	g_bSASRuntimeCivilopediaVisible = bVisible;
	writeSASRuntimeStatus(bVisible ? SAS_RUNTIME_STATUS_CIVILOPEDIA_SHOWN : SAS_RUNTIME_STATUS_CIVILOPEDIA_HIDDEN);
}

// <!-- custom: Focus is the first generic ButtonPopup callback that proves an interactive popup reached the EXE UI rather than merely being queued/launched.
// Keep this overlay observational so waiting on a prompt during PLAYING, AUTOPLAY or GAME_ENDED never restarts the activity timer. (ChatGPT-5.6-Sol) -->
void updateSASRuntimeStatusButtonPopupFocused(CvPopup const* pPopup, ButtonPopupTypes eType)
{
	if (!isSASRuntimeStatusEnabled() || pPopup == NULL || eType == NO_BUTTONPOPUP || eType == BUTTONPOPUP_PYTHON_SCREEN)
		return;
	if (g_bSASRuntimeButtonPopupAwaitingInteraction && g_pSASRuntimeButtonPopup == pPopup && g_eSASRuntimeButtonPopupType == eType)
		return;
	g_bSASRuntimeButtonPopupAwaitingInteraction = true;
	g_eSASRuntimeButtonPopupType = eType;
	g_iSASRuntimeButtonPopupActivePlayer = (int)GC.getGame().getActivePlayer();
	g_szSASRuntimeButtonPopupFocusedUtc = createSASUtcTimestampMilliseconds();
	g_szSASRuntimeButtonPopupResolvedUtc = "-";
	g_szSASRuntimeButtonPopupResolution = "-";
	g_iSASRuntimeButtonPopupResponseButton = -1;
	g_pSASRuntimeButtonPopup = pPopup;
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_BUTTON_POPUP_FOCUSED);
}

// <!-- custom: A returned button is user/EXE response evidence, not proof that the downstream gameplay action succeeded.
// Cancellation can be reported only for the exact popup identity already observed in focus, preventing a stale/dying popup from closing a newer popup of the same type. (ChatGPT-5.6-Sol) -->
void updateSASRuntimeStatusButtonPopupResolved(CvPopup const* pPopup, ButtonPopupTypes eType, int iButtonClicked, bool bCancelled)
{
	if (!isSASRuntimeStatusEnabled() || pPopup == NULL || eType == NO_BUTTONPOPUP || eType == BUTTONPOPUP_PYTHON_SCREEN)
		return;
	bool const bMatchesFocusedPopup = (g_bSASRuntimeButtonPopupAwaitingInteraction && g_pSASRuntimeButtonPopup == pPopup && g_eSASRuntimeButtonPopupType == eType);
	// <!-- custom: Once a focused popup owns the wait state, only that exact popup may resolve it.
	// A stale response can otherwise arrive after a newer popup focused and incorrectly clear the newer prompt; response-without-focus remains usable when no popup is currently tracked. (ChatGPT-5.6-Sol) -->
	if (g_bSASRuntimeButtonPopupAwaitingInteraction && !bMatchesFocusedPopup)
		return;
	if (bCancelled && !bMatchesFocusedPopup)
		return;
	g_bSASRuntimeButtonPopupAwaitingInteraction = false;
	g_eSASRuntimeButtonPopupType = eType;
	// <!-- custom: Preserve the UI owner sampled at focus when resolving that same popup; a stale cancellation can coincide with an active-player change.
	// A response observed without prior focus gets the current player as best available context and no focus timestamp; otherwise a previous resolved popup's time would be misattributed to this response. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
	if (!bMatchesFocusedPopup)
	{
		g_iSASRuntimeButtonPopupActivePlayer = (int)GC.getGame().getActivePlayer();
		g_szSASRuntimeButtonPopupFocusedUtc = "-";
	}
	g_szSASRuntimeButtonPopupResolvedUtc = createSASUtcTimestampMilliseconds();
	g_szSASRuntimeButtonPopupResolution = (bCancelled ? "CANCELLED" : "RESPONDED");
	g_iSASRuntimeButtonPopupResponseButton = (bCancelled ? -1 : iButtonClicked);
	g_pSASRuntimeButtonPopup = NULL;
	writeSASRuntimeStatus(bCancelled ? SAS_RUNTIME_STATUS_BUTTON_POPUP_CANCELLED : SAS_RUNTIME_STATUS_BUTTON_POPUP_RESPONDED);
}

void updateSASRuntimeStatusExtendedGameStarted()
{
	if (!isSASRuntimeStatusEnabled())
		return;
	g_eSASRuntimeGameState = SAS_RUNTIME_GAME_PLAYING;
	g_bSASRuntimeWorldBuilderMode = false;
	g_bSASRuntimeWorldBuilderScreenVisible = false;
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_EXTENDED_GAME_STARTED);
}

// <!-- custom: Preserve explicit UI navigation/exit requests separately from observed reset/shutdown completion. (GPT-6.1-Sol) -->
void updateSASRuntimeStatusRequest(SASRuntimeStatusReason eReason)
{
	if (!isSASRuntimeStatusEnabled())
		return;
	writeSASRuntimeStatus(eReason);
}

void updateSASRuntimeStatusGameEnded()
{
	if (!isSASRuntimeStatusEnabled())
		return;
	g_eSASRuntimeGameState = SAS_RUNTIME_GAME_GAME_ENDED;
	g_bSASRuntimeWorldBuilderMode = false;
	g_bSASRuntimeWorldBuilderScreenVisible = false;
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_GAME_ENDED);
}

void updateSASRuntimeStatusCleanExit()
{
	// <!-- custom: Do not resolve/query XML for the first time during global teardown; any enabled status session initialized this cache earlier.
	// The destructor intentionally calls this no-argument entry without the usual caller predicate, leaving only call entry and this cached comparison when disabled; do not replace it with the lazy isSASRuntimeStatusEnabled getter. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
	if (g_iSASRuntimeStatusEnabled <= 0)
		return;
	g_eSASRuntimeProcessState = SAS_RUNTIME_PROCESS_EXITED_CLEANLY;
	writeSASRuntimeStatus(SAS_RUNTIME_STATUS_PROCESS_EXIT);
	// <!-- custom: Release the thread-local message observer after the final orderly snapshot; the snapshot keeps the cumulative observation-armed flag, while abrupt process termination is cleaned up by Windows. (ChatGPT-5.6-Sol) -->
	releaseSASRuntimeWindowMessageHook();
}

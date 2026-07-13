#include "CvGameCoreDLL.h"
#include "BBAILog.h"
// <advc.133>
#include "CvGameTextMgr.h"
#include "CvGamePlay.h" // </advc.133>
#include "CvInfo_GameOption.h" // <!-- custom: Needed to log enabled game-option type names; CvGlobals only forward-declares CvGameOptionInfo. (GPT-5.5) -->
#include "CvMap.h" // <!-- custom: Needed to log map dimensions; CvGlobals only forward-declares CvMap. (GPT-5.5) -->
#include <time.h> // <!-- custom: Added for UTC session timestamps in timestamped BBAI log filenames. (ChatGPT-5.5) -->

// AI decision making logging

static int getClampedSASBBAILogLevel(char const* szDefineName)
{
	const int iLevel = GC.getDefineINT(szDefineName);
	if (iLevel < 0)
		return 0;
	if (iLevel > 3)
		return 3;
	return iLevel;
}

// <!-- custom: Cache each effective XML-backed BBAI diagnostic log setting on first use for cheap hot-path checks. Game-summary run reports are handled independently in SASGameSummaryLog.cpp. (GPT-5.5? + GPT-5.5) -->
bool isSASBBAILogEnabled()
{
	static const bool bEnabled = (isSASBBAILogMasterEnabled() && (getSASBBAIPlayerLogLevel() > 0 || getSASBBAITeamLogLevel() > 0 || getSASBBAIWarLogLevel() > 0 || getSASBBAICityLogLevel() > 0 || getSASBBAICitizenLogLevel() > 0 || getSASBBAIUnitLogLevel() > 0 || getSASBBAIGreatGeneralLogLevel() > 0 || getSASBBAISettlerLogLevel() > 0 || getSASBBAIEvacuationLogLevel() > 0 || getSASBBAIWorkerLogLevel() > 0 || getSASBBAIWorkerSeaLogLevel() > 0 || getSASBBAIMapLogLevel() > 0 || getSASBBAIFoundLogLevel() > 0 || getSASBBAIDealCancelLogLevel() > 0 || getSASBBAICultureLogLevel() > 0));
	return bEnabled;
}

bool isSASBBAILogMasterEnabled()
{
	static const bool bEnabled = (GC.getDefineINT("SAS_BBAI_LOG_ENABLE") > 0);
	return bEnabled;
}

int getSASBBAIPlayerLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_PLAYER_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAITeamLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_TEAM_LOG_LEVEL") : 0);
	return iLevel;
}

// <!-- custom: Dedicated war diagnostics for UWAI target choice, war-plan lifecycle, and declaration context. TEAM remains for broader diplomacy/team events. (GPT-5.5) -->
int getSASBBAIWarLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_WAR_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAICityLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_CITY_LOG_LEVEL") : 0);
	return iLevel;
}

// <!-- custom: Separate citizen-assignment log level so expensive contextual swap and raw plot-yield diagnostics can run without broad city logging. (GPT-5.5) -->
int getSASBBAICitizenLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_CITIZEN_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAIUnitLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_UNIT_LOG_LEVEL") : 0);
	return iLevel;
}

// <!-- custom: Separate Great General diagnostics from general UNIT logging because one decision spans Military Academy construction, Military Instructor joining, Warlord attachment, and the target-city/unit valuation that decides between them. (GPT-5.5) -->
int getSASBBAIGreatGeneralLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_GREAT_GENERAL_LOG_LEVEL") : 0);
	return iLevel;
}

// <!-- custom: Separate Settler diagnostics from general UNIT logging so each can be inspected independently; FOUND separately controls detailed city-site scoring calculations. (GPT-5.5) -->
int getSASBBAISettlerLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_SETTLER_LOG_LEVEL") : 0);
	return iLevel;
}

// <!-- custom: Separate evacuation/retreat diagnostics, notably for doomed cities, workers, and naval units. (GPT-5.5) -->
int getSASBBAIEvacuationLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_EVACUATION_LOG_LEVEL") : 0);
	return iLevel;
}

// <!-- custom: New Land-worker BBAI log level for Worker AI build, movement, and improvement-replacement diagnostics. This keeps WORKER_* diagnostics out of the general UNIT category, so UNIT can stay focused on non-worker unit AI. (ChatGPT-5.5 + GPT-5.5 review) -->
int getSASBBAIWorkerLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_WORKER_LOG_LEVEL") : 0);
	return iLevel;
}

// <!-- custom: New Worker-sea/Work Boat BBAI log level for UNITAI_WORKER_SEA production, target, audit, movement, and sea-improvement diagnostics. This separates noisy Work Boat diagnostics from both CITY and UNIT logging. (ChatGPT-5.5 + GPT-5.5 review) -->
int getSASBBAIWorkerSeaLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_WORKER_SEA_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAIMapLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_MAP_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAIFoundLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_FOUND_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAIDealCancelLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_DEAL_CANCEL_LOG_LEVEL") : 0);
	return iLevel;
}

// <!-- custom: Separate culture-victory BBAI log level so culture-slider, victory-stage, and city-target diagnostics can be enabled without turning on broad player/city logging. (ChatGPT-5.5) -->
int getSASBBAICultureLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_CULTURE_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAIScoreLogInterval()
{
	// <!-- custom: When the master switch is disabled, return 1 rather than 0 because this value can be used as a modulo divisor. (GPT-5.5?) -->
	static const int iInterval = (isSASBBAILogMasterEnabled() ? std::max(1, GC.getDefineINT("SAS_BBAI_SCORE_LOG_INTERVAL")) : 1);
	return iInterval;
}

static CvString createSASBBAILogTimestamp()
{
	CvString szTimestamp;
	char szBuffer[32];
	time_t kNow;
	time(&kNow);
	struct tm* pUtcTime = gmtime(&kNow);
	if (pUtcTime != NULL && strftime(szBuffer, sizeof(szBuffer), "%Y%m%dT%H%M%SZ", pUtcTime) > 0)
	{
		szTimestamp = szBuffer;
	}
	else
	{
		szTimestamp = "unknown_time";
	}
	return szTimestamp;
}

static CvString g_szSASBBAILogTimestamp;
static int g_iSASBBAILogSequence = 0;
static CvString g_szSASBBAILogContext;

static CvString getSASBBAILogTimestamp()
{
	if (g_szSASBBAILogTimestamp.empty())
		g_szSASBBAILogTimestamp = createSASBBAILogTimestamp();
	return g_szSASBBAILogTimestamp;
}

static bool isSASBBAILogTimestampedFilenameEnabled()
{
	static const bool bUseTimestampedFilename = (GC.getDefineINT("SAS_BBAI_LOG_USE_TIMESTAMPED_FILENAME") > 0);
	return bUseTimestampedFilename;
}

static CvString getSASBBAILogName()
{
	// <!-- custom: When timestamped filenames are enabled, use a new file for every new game and loaded save. The new/load context and shared chronological sequence keep files distinct and show their order even when multiple new/load actions occur within the same UTC second. (GPT-5.5) -->
	const bool bUseTimestampedFilename = isSASBBAILogTimestampedFilenameEnabled();
	CvString szLogName;
	// <advc.007>
	if (GC.getGame().isNetworkMultiPlayer())
	{
		// For OOS debugging on one PC
		if (bUseTimestampedFilename)
		{
			if (!g_szSASBBAILogContext.empty())
				szLogName.Format("BBAI%d_%s_%s.log", (int)GC.getGame().getActivePlayer(), getSASBBAILogTimestamp().GetCString(), g_szSASBBAILogContext.GetCString());
			else szLogName.Format("BBAI%d_%s.log", (int)GC.getGame().getActivePlayer(), getSASBBAILogTimestamp().GetCString());
		}
		else szLogName.Format("BBAI%d.log", (int)GC.getGame().getActivePlayer());
	}
	else
	{
		if (bUseTimestampedFilename)
		{
			if (!g_szSASBBAILogContext.empty())
				szLogName.Format("BBAI_%s_%s.log", getSASBBAILogTimestamp().GetCString(), g_szSASBBAILogContext.GetCString());
			else szLogName.Format("BBAI_%s.log", getSASBBAILogTimestamp().GetCString());
		}
		else szLogName = "BBAI.log";
	} // </advc.007>
	return szLogName;
}

static void rollSASBBAILog(const char* szContext)
{
	if (isSASBBAILogTimestampedFilenameEnabled())
	{
		g_szSASBBAILogTimestamp = createSASBBAILogTimestamp();
		g_iSASBBAILogSequence++;
		g_szSASBBAILogContext.Format("%s%d", szContext, g_iSASBBAILogSequence);
	}
}

static void logSASBBAIGameState(const char* szRowType)
{
	CvGame& kGame = GC.getGame();
	CvInitCore const& kInitCore = GC.getInitCore();
	const PlayerTypes eActivePlayer = kGame.getActivePlayer();
	const char* szActiveCivilization = "-";
	const char* szActiveHandicap = "-";
	if (eActivePlayer != NO_PLAYER)
	{
		CvPlayer const& kActivePlayer = GET_PLAYER(eActivePlayer);
		if (kActivePlayer.getCivilizationType() != NO_CIVILIZATION)
			szActiveCivilization = GC.getInfo(kActivePlayer.getCivilizationType()).getType();
		if (kActivePlayer.getHandicapType() != NO_HANDICAP)
			szActiveHandicap = GC.getInfo(kActivePlayer.getHandicapType()).getType();
	}
	CvString szGameOptions;
	FOR_EACH_ENUM(GameOption)
	{
		if (!kGame.isOption(eLoopGameOption))
			continue;
		if (!szGameOptions.empty())
			szGameOptions += ",";
		szGameOptions += GC.getInfo(eLoopGameOption).getType();
	}
	if (szGameOptions.empty())
		szGameOptions = "-";
	const CvString szLogName = getSASBBAILogName();
	logBBAI("%s utc=%s logFile=%s turn=%d elapsed=%d year=%d scenario=%d activePlayer=%d activeCivilization=%s activeHandicap=%s playersDefined=%d playersAlive=%d playersEverAlive=%d humans=%d",
			szRowType, getSASBBAILogTimestamp().GetCString(), szLogName.GetCString(), kGame.getGameTurn(), kGame.getElapsedGameTurns(), kGame.getGameTurnYear(), kGame.isScenario(), eActivePlayer, szActiveCivilization, szActiveHandicap, kInitCore.getNumDefinedPlayers(), kGame.countCivPlayersAlive(), kGame.countCivPlayersEverAlive(), kGame.getNumHumanPlayers());
	// <!-- custom: Log the actual cached DLL map classification rather than requiring tests to infer it from the map-script name. (GPT-5.5) -->
	logBBAI("BBAI_GAME_SETTINGS mapScript=%S map=%dx%d landHeavy=%d navalHeavy=%d world=%s climate=%s seaLevel=%s gameSpeed=%s startEra=%s gameHandicap=%s options=%s",
			kInitCore.getMapScriptName().GetCString(), GC.getMap().getGridWidth(), GC.getMap().getGridHeight(), kGame.isLandHeavyMapnameCached(), kGame.isNavalHeavyMapnameCached(), GC.getInfo(kInitCore.getWorldSize()).getType(), GC.getInfo(kInitCore.getClimate()).getType(), GC.getInfo(kInitCore.getSeaLevel()).getType(), GC.getInfo(kGame.getGameSpeedType()).getType(), GC.getInfo(kGame.getStartEra()).getType(), GC.getInfo(kGame.getHandicapType()).getType(), szGameOptions.GetCString());
	logBBAI("BBAI_GAME_RNG mapRandState=%u syncRandState=%u", kGame.getMapRand().getSeed(), kGame.getSorenRand().getSeed());
}

// <!-- custom: Record the effective BBAI diagnostic profile in each new/load file so test runs with different category levels are not compared as if they contained the same diagnostics. (GPT-5.5) -->
static void logSASBBAILogSettings()
{
	logBBAI("BBAI_LOG_SETTINGS SAS_BBAI_LOG_ENABLE=%d SAS_BBAI_LOG_USE_TIMESTAMPED_FILENAME=%d SAS_BBAI_PLAYER_LOG_LEVEL=%d SAS_BBAI_TEAM_LOG_LEVEL=%d SAS_BBAI_WAR_LOG_LEVEL=%d SAS_BBAI_CITY_LOG_LEVEL=%d SAS_BBAI_CITIZEN_LOG_LEVEL=%d SAS_BBAI_UNIT_LOG_LEVEL=%d SAS_BBAI_GREAT_GENERAL_LOG_LEVEL=%d SAS_BBAI_SETTLER_LOG_LEVEL=%d SAS_BBAI_EVACUATION_LOG_LEVEL=%d SAS_BBAI_WORKER_LOG_LEVEL=%d SAS_BBAI_WORKER_SEA_LOG_LEVEL=%d SAS_BBAI_MAP_LOG_LEVEL=%d SAS_BBAI_FOUND_LOG_LEVEL=%d SAS_BBAI_DEAL_CANCEL_LOG_LEVEL=%d SAS_BBAI_CULTURE_LOG_LEVEL=%d SAS_BBAI_SCORE_LOG_INTERVAL=%d",
			isSASBBAILogMasterEnabled(), isSASBBAILogTimestampedFilenameEnabled(), getSASBBAIPlayerLogLevel(), getSASBBAITeamLogLevel(), getSASBBAIWarLogLevel(), getSASBBAICityLogLevel(), getSASBBAICitizenLogLevel(), getSASBBAIUnitLogLevel(), getSASBBAIGreatGeneralLogLevel(), getSASBBAISettlerLogLevel(), getSASBBAIEvacuationLogLevel(), getSASBBAIWorkerLogLevel(), getSASBBAIWorkerSeaLogLevel(), getSASBBAIMapLogLevel(), getSASBBAIFoundLogLevel(), getSASBBAIDealCancelLogLevel(), getSASBBAICultureLogLevel(), getSASBBAIScoreLogInterval());
}

// <!-- custom: Roll over before new-game initialization can emit map-generation or starting-position diagnostics. The complete metadata is logged later from CvEventReporter::gameStart, once the generated game state exists. (GPT-5.5) -->
void startSASBBAILogForNewGame()
{
	rollSASBBAILog("new");
	logBBAI("BBAI_NEW_GAME_INITIALIZING utc=%s logFile=%s", getSASBBAILogTimestamp().GetCString(), getSASBBAILogName().GetCString());
	logSASBBAILogSettings();
}

void logSASBBAINewGameStarted()
{
	logSASBBAIGameState("BBAI_NEW_GAME_STARTED");
}

// <!-- custom: Civ4 does not expose the source save filename to the DLL or Python OnLoad event. Start a distinct BBAI file after all save data is read and identify the loaded state through UTC, turn/year, map/game settings, player counts, and read-only RNG states instead. This removes the need to restart Civ4 between repeated save-file tests. (GPT-5.5) -->
void startSASBBAILogForLoadedSave()
{
	rollSASBBAILog("load");
	logSASBBAIGameState("BBAI_SAVE_LOADED");
	logSASBBAILogSettings();
}

void logBBAI(TCHAR* format, ... )
{
	static const bool bEnabled = isSASBBAILogEnabled();
	if (!bEnabled)
		return;

	static char buf[2048];
	va_list args;
	va_start(args, format);
	// <!-- custom: Replace the old fixed 2048-4 limit with the real buffer size, while reserving one byte for the forced terminator below. See KI#161.2. (ChatGPT-5.5) -->
	// _vsnprintf(buf, 2048-4, format, args);
	_vsnprintf(buf, sizeof(buf) - 1, format, args);
	va_end(args); // kmodx
	// <!-- custom: MSVC 7.1 _vsnprintf may leave truncated output unterminated, so guard logMsg against rare logging/heap crash signatures. See KI#161.2. (ChatGPT-5.5) -->
	buf[sizeof(buf) - 1] = '\0';
	CvString szLogName = getSASBBAILogName();
	gDLL->logMsg(szLogName.GetCString(), buf, /* advc.007: No time stamps */ false, false);
}

// advc.133:
void logBBAICancel(CvDeal const& d, PlayerTypes eCancelPlayer, wchar const* szReason)
{
	if (gDealCancelLogLevel <= 0)
		return;

	CvWStringBuffer szTmpBuffer;
	GAMETEXT.getDealString(szTmpBuffer, d, eCancelPlayer, false);
	CvWString szBuffer;
	szBuffer.Format(L"    %s cancels deal (%s): %s", GET_PLAYER(eCancelPlayer).getName(0),
			szReason, szTmpBuffer.getCString());
	// Leave it to logBBAI to narrow the string
	logBBAI("%S", szBuffer.GetCString());
}

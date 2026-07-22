#include "CvGameCoreDLL.h"
#include "SASGameSummaryLog.h"
#include "CvGame.h" // <!-- custom: Needed for game-summary turn, game-state, victory, RNG, and map-classification context rows. (GPT-5.5) -->
#include "CvCity.h" // <!-- custom: Needed by game-summary city action/BFC rows; SASGameSummaryLog.h only forward-declares CvCity. (GPT-5.5) -->
#include "CvUnit.h" // <!-- custom: Needed by game-summary battle rows; SASGameSummaryLog.h only forward-declares CvUnit. (GPT-5.5) -->
#include "CvUnitAI.h" // <!-- custom: Needed to inspect the head unit of large city groups and its UnitAI role; the base unit header only forward-declares CvUnitAI. (GPT-5.6-Sol) -->
#include "CityPlotIterator.h" // <!-- custom: Needed by compact game-summary BFC composition rows. (ChatGPT-5.5) -->
#include "CvPlot.h" // <!-- custom: Needed by game-summary BFC and unit posture rows. (ChatGPT-5.5) -->
#include "CvInfo_Build.h" // <!-- custom: Needed for worker build-type names and build target classification in game-summary rows. (ChatGPT-5.5) -->
#include "CvInfo_Command.h" // <!-- custom: Needed for mission-type names in worker/settler game-summary rows. (ChatGPT-5.5) -->
#include "CvInfo_Building.h" // <!-- custom: Needed to classify city production in game-summary city rows. (ChatGPT-5.5) -->
#include "CvInfo_Tech.h" // <!-- custom: Needed to bucket owned-tech counts by era in game-summary rows. (ChatGPT-5.5) -->
#include "CvInfo_Terrain.h" // <!-- custom: Needed for terrain/feature/bonus type names in game-summary context rows. (ChatGPT-5.5) -->
#include "CvInfo_Organization.h" // <!-- custom: Needed for religion/corporation type names in game-summary action rows. (ChatGPT-5.5) -->
#include "CvInfo_Unit.h" // <!-- custom: Needed to classify unit composition and city production in game-summary rows. (ChatGPT-5.5) -->
#include "CvInfo_Symbol.h" // <!-- custom: Needed for commerce-slider type names in game-summary economy rows. (GPT-5.5) -->
#include "CvInfo_City.h" // <!-- custom: Needed for specialist and process type names in game-summary city rows. (ChatGPT-5.5) -->
#include "CvInfo_Civics.h" // <!-- custom: Needed for policy/civic names in game-summary advisor rows. (ChatGPT-5.5) -->
#include "CvInfo_Civilization.h" // <!-- custom: Needed to attribute player-wide extra happiness/health to traits instead of leaving effects from loaded-mod rules under an opaque `extra` label. (GPT-5.6-Sol) -->
#include "CvInfo_GameOption.h" // <!-- custom: Needed to log enabled game-option type names; CvGlobals only forward-declares CvGameOptionInfo. (GPT-5.5) -->
#include "CvMap.h" // <!-- custom: Needed to log map dimensions; CvGlobals only forward-declares CvMap. (GPT-5.5) -->
#include "CvSelectionGroup.h" // <!-- custom: Needed to inspect worker/settler mission queues in game-summary rows. (ChatGPT-5.5) -->
#include "CvSelectionGroupAI.h" // <!-- custom: Needed for large city-group mission targets and MissionAI state; the base group header only forward-declares CvSelectionGroupAI. (GPT-5.6-Sol) -->
#include "CvPlotGroup.h" // <!-- custom: Needed to identify connected city networks in game-summary city rows. (ChatGPT-5.5) -->
#include "CvArea.h" // <!-- custom: Needed for area-wide city happiness/health detail rows. (ChatGPT-5.5) -->
#include "CvPlayerAI.h" // <!-- custom: Needed for attitude/glance values in game-summary advisor rows. (ChatGPT-5.5) -->
#include "CvTeamAI.h" // <!-- custom: Needed for team-level worst-enemy state in game-summary diplomacy-status rows. (ChatGPT-5.5) -->
#include "CvStatistics.h" // <!-- custom: Needed for persistent player-record statistics in game-summary benchmark rows. (GPT-5.5) -->
#include <time.h>
#include <algorithm> // <!-- custom: Needed to deduplicate buffered plot-change/map-revelation coordinates within each turn. (GPT-5.6-Sol) -->
#include <utility> // <!-- custom: Needed for Great Person odds pairs in game-summary city rows. (ChatGPT-5.5) -->
#include <vector> // <!-- custom: Used for compact dynamic buckets in game-summary known-area, BFC development, advisor, tech-era, worker/settler, and unit-composition rows. (ChatGPT-5.5) -->

static int getClampedSASGameSummaryLogLevel(char const* szDefineName)
{
	const int iLevel = GC.getDefineINT(szDefineName);
	if (iLevel < 0)
		return 0;
	if (iLevel > 3)
		return 3;
	return iLevel;
}

// <!-- custom: Dedicated structured game-summary log for autoplay comparison, general game analysis, and external LLM review. This is independent from SAS_BBAI_LOG_ENABLE because it is a run-report artifact rather than classic AI-decision diagnostics, and writes to SASGameSummary_*.log when enabled. Use ACTION rows rather than EVENT rows to avoid confusion with Civ4 random events. (ChatGPT-5.5 + GPT-5.5) -->
int getSASGameSummaryLogLevel()
{
	static const int iLevel = getClampedSASGameSummaryLogLevel("SAS_GAME_SUMMARY_LOG_LEVEL");
	return iLevel;
}

bool isSASGameSummaryLogEnabled()
{
	static const bool bEnabled = (getSASGameSummaryLogLevel() > 0);
	return bEnabled;
}

int getSASGameSummaryTurnInterval()
{
	// <!-- custom: Separate snapshot frequency from detail level. Level 0 disables the game-summary rows; the interval is still clamped so modulo callers are safe. (ChatGPT-5.5) -->
	static const int iInterval = std::max(1, GC.getDefineINT("SAS_GAME_SUMMARY_TURN_INTERVAL"));
	return iInterval;
}

static CvString createSASGameSummaryLogTimestamp()
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

static CvString g_szSASGameSummaryLogTimestamp;
static int g_iSASGameSummaryLogSequence = 0;
static CvString g_szSASGameSummaryLogContext;

static CvString getSASGameSummaryLogTimestamp()
{
	if (g_szSASGameSummaryLogTimestamp.empty())
		g_szSASGameSummaryLogTimestamp = createSASGameSummaryLogTimestamp();
	return g_szSASGameSummaryLogTimestamp;
}

static bool isSASGameSummaryTimestampedFilenameEnabled()
{
	static const bool bUseTimestampedFilename = (GC.getDefineINT("SAS_GAME_SUMMARY_LOG_USE_TIMESTAMPED_FILENAME") > 0);
	return bUseTimestampedFilename;
}

static CvString getSASGameSummaryLogName()
{
	const bool bUseTimestampedFilename = isSASGameSummaryTimestampedFilenameEnabled();
	CvString szLogName;
	if (GC.getGame().isNetworkMultiPlayer())
	{
		if (bUseTimestampedFilename)
		{
			if (!g_szSASGameSummaryLogContext.empty())
				szLogName.Format("SASGameSummary%d_%s_%s.log", (int)GC.getGame().getActivePlayer(), getSASGameSummaryLogTimestamp().GetCString(), g_szSASGameSummaryLogContext.GetCString());
			else szLogName.Format("SASGameSummary%d_%s.log", (int)GC.getGame().getActivePlayer(), getSASGameSummaryLogTimestamp().GetCString());
		}
		else szLogName.Format("SASGameSummary%d.log", (int)GC.getGame().getActivePlayer());
	}
	else
	{
		if (bUseTimestampedFilename)
		{
			if (!g_szSASGameSummaryLogContext.empty())
				szLogName.Format("SASGameSummary_%s_%s.log", getSASGameSummaryLogTimestamp().GetCString(), g_szSASGameSummaryLogContext.GetCString());
			else szLogName.Format("SASGameSummary_%s.log", getSASGameSummaryLogTimestamp().GetCString());
		}
		else szLogName = "SASGameSummary.log";
	}
	return szLogName;
}

static void rollSASGameSummaryLog(const char* szContext)
{
	if (isSASGameSummaryTimestampedFilenameEnabled())
	{
		g_szSASGameSummaryLogTimestamp = createSASGameSummaryLogTimestamp();
		g_iSASGameSummaryLogSequence++;
		g_szSASGameSummaryLogContext.Format("%s%d", szContext, g_iSASGameSummaryLogSequence);
	}
}

static void logSASGameSummaryFormattedLine(CvString const& szLogName, TCHAR* format, va_list args)
{
	static char buf[2048];
	_vsnprintf(buf, sizeof(buf) - 1, format, args);
	// <!-- custom: As with BBAI logging, guard this new game-summary logger against MSVC 7.1 _vsnprintf leaving truncated output unterminated, which fixed rare logging/heap crash signatures. See KI#161.2. (ChatGPT-5.5 + GPT-5.5) -->
	buf[sizeof(buf) - 1] = '\0';
	gDLL->logMsg(szLogName.GetCString(), buf, false, false);
}

void logSASGameSummary(TCHAR* format, ... )
{
	static const bool bEnabled = isSASGameSummaryLogEnabled();
	if (!bEnabled)
		return;

	va_list args;
	va_start(args, format);
	logSASGameSummaryFormattedLine(getSASGameSummaryLogName(), format, args);
	va_end(args);
}

// <!-- custom: Quote free-text game-summary values so simple key=value parsers do not split names such as "New York" or "De Gaulle" on spaces. Keep XML enum/type tags unquoted. Escape quotes, backslashes, and line separators so one log row remains one parseable row. (GPT-5.5) -->
static CvString getSASGameSummaryQuoted(char const* szValue)
{
	if (szValue == NULL)
		return "-";
	CvString szQuoted = "\"";
	for (int iI = 0; szValue[iI] != '\0'; iI++)
	{
		const char c = szValue[iI];
		if (c == '\\')
			szQuoted += "\\\\";
		else if (c == '"')
			szQuoted += "\\\"";
		else if (c == '\n')
			szQuoted += "\\n";
		else if (c == '\r')
			szQuoted += "\\r";
		else if (c == '\t')
			szQuoted += "\\t";
		else szQuoted += c;
	}
	szQuoted += "\"";
	return szQuoted;
}

static CvWString getSASGameSummaryQuoted(wchar const* szValue)
{
	if (szValue == NULL)
		return L"-";
	CvWString szQuoted = L"\"";
	for (int iI = 0; szValue[iI] != L'\0'; iI++)
	{
		const wchar c = szValue[iI];
		if (c == L'\\')
			szQuoted += L"\\\\";
		else if (c == L'"')
			szQuoted += L"\\\"";
		else if (c == L'\n')
			szQuoted += L"\\n";
		else if (c == L'\r')
			szQuoted += L"\\r";
		else if (c == L'\t')
			szQuoted += L"\\t";
		else szQuoted += c;
	}
	szQuoted += L"\"";
	return szQuoted;
}

static CvWString getSASGameSummaryQuotedCityName(CvCity const* pCity)
{
	return pCity == NULL ? L"-" : getSASGameSummaryQuoted(pCity->getName().GetCString());
}

// <!-- custom: Use "row" wording for generic SAS game-summary row prefixes because Civ4 also has EventInfo/random events. Keep GAME_SUMMARY_ACTION only for chronological gameplay action rows. (GPT-5.5) -->
static void logSASGameSummaryGameState(const char* szRowType)
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
	CvString szVictories;
	FOR_EACH_ENUM(Victory)
	{
		if (!kGame.isVictoryValid(eLoopVictory))
			continue;
		if (!szVictories.empty())
			szVictories += ",";
		szVictories += GC.getInfo(eLoopVictory).getType();
	}
	if (szVictories.empty())
		szVictories = "-";
	const CvString szLogName = getSASGameSummaryLogName();
	logSASGameSummary("%s utc=%s logFile=%s turn=%d elapsed=%d year=%d scenario=%d activePlayer=%d activeCivilization=%s activeHandicap=%s playersDefined=%d playersAlive=%d playersEverAlive=%d humans=%d",
			szRowType, getSASGameSummaryLogTimestamp().GetCString(), getSASGameSummaryQuoted(szLogName.GetCString()).GetCString(), kGame.getGameTurn(), kGame.getElapsedGameTurns(), kGame.getGameTurnYear(), kGame.isScenario(), eActivePlayer, szActiveCivilization, szActiveHandicap, kInitCore.getNumDefinedPlayers(), kGame.countCivPlayersAlive(), kGame.countCivPlayersEverAlive(), kGame.getNumHumanPlayers());
	// <!-- custom: Enabled victories and their fixed turn/score limits determine which later victory-progress and AI-strategy rows are relevant. Record this compact setup context instead of requiring external XML or save inspection. (GPT-5.6-Sol) -->
	logSASGameSummary("GAME_SUMMARY_GAME_SETTINGS mapScript=%S map=%dx%d landHeavy=%d navalHeavy=%d world=%s climate=%s seaLevel=%s gameSpeed=%s startEra=%s gameHandicap=%s maxTurns=%d targetScore=%d victories=%s options=%s",
			getSASGameSummaryQuoted(kInitCore.getMapScriptName().GetCString()).GetCString(), GC.getMap().getGridWidth(), GC.getMap().getGridHeight(), kGame.isLandHeavyMapnameCached(), kGame.isNavalHeavyMapnameCached(), GC.getInfo(kInitCore.getWorldSize()).getType(), GC.getInfo(kInitCore.getClimate()).getType(), GC.getInfo(kInitCore.getSeaLevel()).getType(), GC.getInfo(kGame.getGameSpeedType()).getType(), GC.getInfo(kGame.getStartEra()).getType(), GC.getInfo(kGame.getHandicapType()).getType(), kGame.getMaxTurns(), kGame.getTargetScore(), szVictories.GetCString(), szGameOptions.GetCString());
	logSASGameSummary("GAME_SUMMARY_GAME_RNG mapRandState=%u syncRandState=%u", kGame.getMapRand().getSeed(), kGame.getSorenRand().getSeed());
}

static void logSASGameSummaryLogSettings()
{
	logSASGameSummary("GAME_SUMMARY_LOG_SETTINGS SAS_GAME_SUMMARY_LOG_LEVEL=%d SAS_GAME_SUMMARY_TURN_INTERVAL=%d SAS_GAME_SUMMARY_LOG_USE_TIMESTAMPED_FILENAME=%d",
			getSASGameSummaryLogLevel(), getSASGameSummaryTurnInterval(), isSASGameSummaryTimestampedFilenameEnabled());
}

static void resetSASGameSummaryState();
static void logSASGameSummaryInitialContext();

void startSASGameSummaryLogForNewGame()
{
	rollSASGameSummaryLog("new");
	resetSASGameSummaryState();
	logSASGameSummary("GAME_SUMMARY_NEW_GAME_INITIALIZING utc=%s logFile=%s", getSASGameSummaryLogTimestamp().GetCString(), getSASGameSummaryQuoted(getSASGameSummaryLogName().GetCString()).GetCString());
	logSASGameSummaryLogSettings();
}

void logSASGameSummaryNewGameStarted()
{
	logSASGameSummaryGameState("GAME_SUMMARY_NEW_GAME_STARTED");
	logSASGameSummaryInitialContext();
}

void startSASGameSummaryLogForLoadedSave()
{
	rollSASGameSummaryLog("load");
	resetSASGameSummaryState();
	logSASGameSummaryGameState("GAME_SUMMARY_SAVE_LOADED");
	logSASGameSummaryLogSettings();
	logSASGameSummaryInitialContext();
}

// <!-- custom: Game-summary helpers keep output compact, stable, and machine-readable. They intentionally use XML type names instead of localized text where possible, so external tools can diff and parse autoplay runs reliably. The static state below is tiny and is only reset/updated through game-summary call sites when the XML log level enables this feature; dynamic XML logging cannot be compiled out cleanly without losing normal runtime XML tuning. (ChatGPT-5.5) -->
static int g_aiSASGameSummaryBattleWins[MAX_PLAYERS];
static int g_aiSASGameSummaryBattleLosses[MAX_PLAYERS];
static int g_aiSASGameSummaryCityBattleWins[MAX_PLAYERS];
static int g_aiSASGameSummaryCityBattleLosses[MAX_PLAYERS];
static int g_aiSASGameSummaryTotalBattleWins[MAX_PLAYERS];
static int g_aiSASGameSummaryTotalBattleLosses[MAX_PLAYERS];
static int g_aiSASGameSummaryTotalCityBattleWins[MAX_PLAYERS];
static int g_aiSASGameSummaryTotalCityBattleLosses[MAX_PLAYERS];
static int g_aiSASGameSummaryTotalGoldenAgeTurns[MAX_PLAYERS];
static int g_aiSASGameSummaryTotalAnarchyTurns[MAX_PLAYERS];
static int g_aiSASGameSummaryCitiesAcquired[MAX_PLAYERS];
static int g_aiSASGameSummaryCitiesLost[MAX_PLAYERS];
static int g_aiSASGameSummaryCitiesConquered[MAX_PLAYERS];
static int g_aiSASGameSummaryCitiesLostByConquest[MAX_PLAYERS];
static int g_aiSASGameSummaryCitiesTradedIn[MAX_PLAYERS];
static int g_aiSASGameSummaryCitiesTradedOut[MAX_PLAYERS];
static int g_iSASGameSummaryLastFullSnapshotTurn = -1;

struct SASGameSummaryPlotChangeGroup
{
	CvString szCategory;
	std::vector<std::pair<int,int> > aCoordinates;
};

static int g_iSASGameSummaryPendingPlotTurn = -1;
static std::vector<SASGameSummaryPlotChangeGroup> g_aSASGameSummaryPlotChanges;
static std::vector<std::pair<int,int> > g_aaSASGameSummaryRevealedPlots[MAX_TEAMS];
static TeamTypes g_eSASGameSummaryFullMapRevelationTeam = NO_TEAM;
static int g_iSASGameSummaryFullMapRevealedBefore = 0;

struct SASGameSummaryPlayerPrevious
{
	bool bValid;
	int iScore;
	int iCities;
	int iPopulation;
	int iLand;
	int iUnits;
	int iMilitaryUnits;
	int iPower;
	int iGold;
	int iGoldRate;
	int iResearchRate;
	int iBonusTypes;
	int iBonusInstances;
	int iBonusImports;
	int iBonusExports;
	int iHistoryScore;
	int iHistoryEconomy;
	int iHistoryIndustry;
	int iHistoryAgriculture;
	int iHistoryPower;
	int iHistoryCulture;
	int iHistoryEspionage;
	int iEspionageRate;
	int iEspionagePercent;
	int iTeamEP;
	int iUnspentEP;
	int iDemoScore;
	int iDemoPopulation;
	int iDemoLand;
	int iDemoFood;
	int iDemoProduction;
	int iDemoCommerce;
	int iDemoResearch;
	int iDemoCulture;
	int iDemoEspionage;
	int iDemoGoldRate;
	int iDemoPower;
	int iUnitTotal;
	int iUnitMilitary;
	int iUnitWorkers;
	int iUnitSettlers;
	int iUnitFieldArmy;
	int iUnitCityDefenders;
	int iUnitEnemyUnitsInTerritory;
	int iUnitTotalExperience;
	int iUnitPromotionReady;
	int iWorkerWorkers;
	int iWorkerBuilding;
	int iWorkerIdle;
	int iWorkerMoving;
	int iWorkerWaiting;
	int iWorkerThreatened;
	int iTerritoryImprovedLand;
	int iTerritoryImprovedWater;
	int iTerritoryRoaded;
	int iTerritoryFarms;
	int iTerritoryIrrigatedFarms;
	int iTerritoryDryFarms;
	int iSettlerSettlers;
	int iSettlerFoundMission;
	int iSettlerMoving;
	int iSettlerIdle;
	int iSettlerWaiting;
	int iSettlerThreatened;
	int iCityCount;
	int iCityConnectedToCapital;
	int iCityFoodSurplus;
	int iCityHappySurplus;
	int iCityHealthSurplus;
	int iCityFood;
	int iCityProduction;
	int iCityCommerce;
	int iCityTradeRoutes;
	int iCityTradeCommerce;
	int iCitySpecialists;
	int iCityFreeSpecialists;
	int iCityGarrison;
};

struct SASGameSummaryTeamPrevious
{
	bool bValid;
	bool bContactsValid;
	int iTechs;
	int iLand;
	int iLandPctX100;
	int iPopulation;
	int iPopPctX100;
	int iMetTeams;
};

struct SASGameSummaryGlobalPrevious
{
	bool bValid;
	int iGlobalWarmingIndex;
	int iGlobalWarmingChances;
	int iOwnedLand;
	int iUnownedLand;
};

struct SASGameSummaryPlotComposition
{
	int iPlots;
	int iLand;
	int iWater;
	int iHills;
	int iPeaks;
	int iRiverSide;
	int iFreshWater;
	int iCoastal;
	int iImproved;
	int iUnimprovedLand;
	int iRoaded;
	int iBonusImproved;
	int iBonusUnimproved;
	int iWorked;
	int iWorkedImproved;
	int iWorkedUnimproved;
	int iNatureFood;
	int iNatureProduction;
	int iNatureCommerce;
	int iCurrentFood;
	int iCurrentProduction;
	int iCurrentCommerce;
	std::vector<int> aiTerrains;
	std::vector<int> aiFeatures;
	std::vector<int> aiBonuses;
	std::vector<int> aiImprovements;
	std::vector<int> aiRoutes;

	SASGameSummaryPlotComposition() : iPlots(0), iLand(0), iWater(0), iHills(0), iPeaks(0), iRiverSide(0), iFreshWater(0), iCoastal(0), iImproved(0), iUnimprovedLand(0), iRoaded(0), iBonusImproved(0), iBonusUnimproved(0), iWorked(0), iWorkedImproved(0), iWorkedUnimproved(0), iNatureFood(0), iNatureProduction(0), iNatureCommerce(0), iCurrentFood(0), iCurrentProduction(0), iCurrentCommerce(0), aiTerrains(GC.getNumTerrainInfos(), 0), aiFeatures(GC.getNumFeatureInfos(), 0), aiBonuses(GC.getNumBonusInfos(), 0), aiImprovements(GC.getNumImprovementInfos(), 0), aiRoutes(GC.getNumRouteInfos(), 0) {}
};

struct SASGameSummaryTerritoryDevelopment
{
	SASGameSummaryPlotComposition kOwned;
	std::vector<int> aiImprovedBonuses;
	std::vector<int> aiUnimprovedBonuses;
	int iBFCPlots;
	int iSuburbPlots;
	int iDevelopmentLand;
	int iDevelopmentWater;
	int iImprovedLand;
	int iImprovedWater;
	int iBFCDevelopmentLand;
	int iBFCImprovedLand;
	int iSuburbDevelopmentLand;
	int iSuburbImprovedLand;
	int iFarms;
	int iIrrigatedFarms;
	int iDryFarms;
	int iBonusFarms;
	int iIrrigatedBonusFarms;
	int iDryBonusFarms;
	int iBFCFarms;
	int iBFCIrrigatedFarms;
	int iBFCDryFarms;
	SASGameSummaryTerritoryDevelopment() : aiImprovedBonuses(GC.getNumBonusInfos(), 0), aiUnimprovedBonuses(GC.getNumBonusInfos(), 0), iBFCPlots(0), iSuburbPlots(0), iDevelopmentLand(0), iDevelopmentWater(0), iImprovedLand(0), iImprovedWater(0), iBFCDevelopmentLand(0), iBFCImprovedLand(0), iSuburbDevelopmentLand(0), iSuburbImprovedLand(0), iFarms(0), iIrrigatedFarms(0), iDryFarms(0), iBonusFarms(0), iIrrigatedBonusFarms(0), iDryBonusFarms(0), iBFCFarms(0), iBFCIrrigatedFarms(0), iBFCDryFarms(0) {}
};

static SASGameSummaryPlayerPrevious g_akSASGameSummaryPlayerPrevious[MAX_PLAYERS];
static SASGameSummaryTeamPrevious g_akSASGameSummaryTeamPrevious[MAX_TEAMS];
static SASGameSummaryGlobalPrevious g_kSASGameSummaryGlobalPrevious;

static int getSASGameSummaryDelta(bool bValid, int iCurrent, int iPrevious)
{
	return bValid ? iCurrent - iPrevious : 0;
}

static void resetSASGameSummaryState()
{
	for (int iI = 0; iI < MAX_PLAYERS; iI++)
	{
		g_aiSASGameSummaryBattleWins[iI] = 0;
		g_aiSASGameSummaryBattleLosses[iI] = 0;
		g_aiSASGameSummaryCityBattleWins[iI] = 0;
		g_aiSASGameSummaryCityBattleLosses[iI] = 0;
		g_aiSASGameSummaryTotalBattleWins[iI] = 0;
		g_aiSASGameSummaryTotalBattleLosses[iI] = 0;
		g_aiSASGameSummaryTotalCityBattleWins[iI] = 0;
		g_aiSASGameSummaryTotalCityBattleLosses[iI] = 0;
		g_aiSASGameSummaryTotalGoldenAgeTurns[iI] = 0;
		g_aiSASGameSummaryTotalAnarchyTurns[iI] = 0;
		g_aiSASGameSummaryCitiesAcquired[iI] = 0;
		g_aiSASGameSummaryCitiesLost[iI] = 0;
		g_aiSASGameSummaryCitiesConquered[iI] = 0;
		g_aiSASGameSummaryCitiesLostByConquest[iI] = 0;
		g_aiSASGameSummaryCitiesTradedIn[iI] = 0;
		g_aiSASGameSummaryCitiesTradedOut[iI] = 0;
		g_akSASGameSummaryPlayerPrevious[iI].bValid = false;
	}
	for (int iI = 0; iI < MAX_TEAMS; iI++)
	{
		g_akSASGameSummaryTeamPrevious[iI].bValid = false;
		g_akSASGameSummaryTeamPrevious[iI].bContactsValid = false;
	}
	g_kSASGameSummaryGlobalPrevious.bValid = false;
	g_iSASGameSummaryLastFullSnapshotTurn = -1;
	g_iSASGameSummaryPendingPlotTurn = -1;
	g_aSASGameSummaryPlotChanges.clear();
	g_eSASGameSummaryFullMapRevelationTeam = NO_TEAM;
	g_iSASGameSummaryFullMapRevealedBefore = 0;
	for (int iI = 0; iI < MAX_TEAMS; iI++)
		g_aaSASGameSummaryRevealedPlots[iI].clear();
}

static void appendSASGameSummaryIntList(CvString& szList, int iValue)
{
	CvString szItem;
	szItem.Format(szList.empty() ? "%d" : ",%d", iValue);
	szList += szItem;
}

static CvString getSASGameSummaryTeamMembers(TeamTypes eTeam)
{
	CvString szList;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (kLoopPlayer.isAlive() && kLoopPlayer.getTeam() == eTeam)
			appendSASGameSummaryIntList(szList, eLoopPlayer);
	}
	return szList.empty() ? CvString("-") : szList;
}

static CvString getSASGameSummaryWarTeams(TeamTypes eTeam)
{
	CvString szList;
	CvTeam const& kTeam = GET_TEAM(eTeam);
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam != eTeam && GET_TEAM(eLoopTeam).isAlive() && kTeam.isAtWar(eLoopTeam))
			appendSASGameSummaryIntList(szList, eLoopTeam);
	}
	return szList.empty() ? CvString("-") : szList;
}

static CvString getSASGameSummaryVassalTeams(TeamTypes eTeam)
{
	CvString szList;
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam != eTeam && GET_TEAM(eLoopTeam).isAlive() && GET_TEAM(eLoopTeam).isVassal(eTeam))
			appendSASGameSummaryIntList(szList, eLoopTeam);
	}
	return szList.empty() ? CvString("-") : szList;
}

static CvString getSASGameSummaryMetTeams(TeamTypes eTeam)
{
	CvString szMetTeams;
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam == eTeam || !GET_TEAM(eLoopTeam).isAlive() || GET_TEAM(eLoopTeam).isBarbarian())
			continue;
		if (GET_TEAM(eTeam).isHasMet(eLoopTeam))
			appendSASGameSummaryIntList(szMetTeams, eLoopTeam);
	}
	return szMetTeams.empty() ? CvString("-") : szMetTeams;
}

static int getSASGameSummaryMetTeamCount(TeamTypes eTeam)
{
	int iCount = 0;
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam != eTeam && GET_TEAM(eLoopTeam).isAlive() && !GET_TEAM(eLoopTeam).isBarbarian() && GET_TEAM(eTeam).isHasMet(eLoopTeam))
			iCount++;
	}
	return iCount;
}

static void logSASGameSummaryTeamContacts(TeamTypes eTeam, int iGameTurn, const char* szReason)
{
	SASGameSummaryTeamPrevious& kPrevious = g_akSASGameSummaryTeamPrevious[eTeam];
	const int iMetTeams = getSASGameSummaryMetTeamCount(eTeam);
	logSASGameSummary("GAME_SUMMARY_CONTACTS turn=%d reason=%s team=%d deltaValid=%d metCount=%d metCountDelta=%+d metTeams=%s",
			iGameTurn, szReason, eTeam, kPrevious.bContactsValid, iMetTeams, getSASGameSummaryDelta(kPrevious.bContactsValid, iMetTeams, kPrevious.iMetTeams), getSASGameSummaryMetTeams(eTeam).GetCString());
	kPrevious.bContactsValid = true;
	kPrevious.iMetTeams = iMetTeams;
}

static TeamTypes getSASGameSummaryMasterTeam(TeamTypes eTeam)
{
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam != eTeam && GET_TEAM(eLoopTeam).isAlive() && GET_TEAM(eTeam).isVassal(eLoopTeam))
			return eLoopTeam;
	}
	return NO_TEAM;
}

static const char* getSASGameSummaryTechType(TechTypes eTech)
{
	return (eTech == NO_TECH ? "-" : GC.getInfo(eTech).getType());
}

static const char* getSASGameSummaryReligionType(ReligionTypes eReligion)
{
	return (eReligion == NO_RELIGION ? "-" : GC.getInfo(eReligion).getType());
}

static const char* getSASGameSummaryCorporationType(CorporationTypes eCorporation)
{
	return (eCorporation == NO_CORPORATION ? "-" : GC.getInfo(eCorporation).getType());
}

static const char* getSASGameSummaryBuildingType(BuildingTypes eBuilding)
{
	return (eBuilding == NO_BUILDING ? "-" : GC.getInfo(eBuilding).getType());
}

static const char* getSASGameSummaryProjectType(ProjectTypes eProject)
{
	return (eProject == NO_PROJECT ? "-" : GC.getInfo(eProject).getType());
}

static const char* getSASGameSummaryUnitType(UnitTypes eUnit)
{
	return (eUnit == NO_UNIT ? "-" : GC.getInfo(eUnit).getType());
}

static const char* getSASGameSummaryBonusType(BonusTypes eBonus)
{
	return (eBonus == NO_BONUS ? "-" : GC.getInfo(eBonus).getType());
}

static const char* getSASGameSummaryTerrainType(TerrainTypes eTerrain)
{
	return (eTerrain == NO_TERRAIN ? "-" : GC.getInfo(eTerrain).getType());
}

static const char* getSASGameSummaryFeatureType(FeatureTypes eFeature)
{
	return (eFeature == NO_FEATURE ? "-" : GC.getInfo(eFeature).getType());
}

static const char* getSASGameSummaryImprovementType(ImprovementTypes eImprovement)
{
	return (eImprovement == NO_IMPROVEMENT ? "-" : GC.getInfo(eImprovement).getType());
}

static const char* getSASGameSummaryRouteType(RouteTypes eRoute)
{
	return (eRoute == NO_ROUTE ? "-" : GC.getInfo(eRoute).getType());
}

SASGameSummaryPlotState::SASGameSummaryPlotState()
:	eTerrain(NO_TERRAIN), eFeature(NO_FEATURE), eBonus(NO_BONUS), eImprovement(NO_IMPROVEMENT), eRoute(NO_ROUTE)
{
	for (int iI = 0; iI < NUM_YIELD_TYPES; iI++)
		aiExtraYield[iI] = 0;
}

SASGameSummaryPlotState::SASGameSummaryPlotState(CvPlot const& kPlot)
:	eTerrain(kPlot.getTerrainType()), eFeature(kPlot.getFeatureType()), eBonus(kPlot.getBonusType()),
	eImprovement(kPlot.getImprovementType()), eRoute(kPlot.getRouteType())
{
	for (int iI = 0; iI < NUM_YIELD_TYPES; iI++)
		aiExtraYield[iI] = GC.getMap().getPlotExtraYield(kPlot, (YieldTypes)iI);
}

static bool isSASGameSummaryPlotStateChanged(SASGameSummaryPlotState const& kOldState, CvPlot const& kPlot)
{
	if (kOldState.eTerrain != kPlot.getTerrainType() || kOldState.eFeature != kPlot.getFeatureType() || kOldState.eBonus != kPlot.getBonusType() || kOldState.eImprovement != kPlot.getImprovementType() || kOldState.eRoute != kPlot.getRouteType())
		return true;
	for (int iI = 0; iI < NUM_YIELD_TYPES; iI++)
	{
		if (kOldState.aiExtraYield[iI] != GC.getMap().getPlotExtraYield(kPlot, (YieldTypes)iI))
			return true;
	}
	return false;
}

static void addSASGameSummaryCoordinate(std::vector<std::pair<int,int> >& aCoordinates, CvPlot const& kPlot)
{
	std::pair<int,int> const kCoordinate(kPlot.getX(), kPlot.getY());
	if (std::find(aCoordinates.begin(), aCoordinates.end(), kCoordinate) == aCoordinates.end())
		aCoordinates.push_back(kCoordinate);
}

static void appendSASGameSummaryCoordinateChunks(std::vector<CvString>& aszChunks, CvString& szChunk, char const* szCategory, std::vector<std::pair<int,int> > const& aCoordinates)
{
	for (size_t iI = 0; iI < aCoordinates.size(); iI++)
	{
		CvString szItem;
		if (iI == 0)
			szItem.Format("%s%s=(%d,%d)", szChunk.empty() ? "" : " ", szCategory, aCoordinates[iI].first, aCoordinates[iI].second);
		else szItem.Format(",(%d,%d)", aCoordinates[iI].first, aCoordinates[iI].second);
		if (!szChunk.empty() && szChunk.length() + szItem.length() > 1500)
		{
			aszChunks.push_back(szChunk);
			szChunk.clear();
			szItem.Format("%s=(%d,%d)", szCategory, aCoordinates[iI].first, aCoordinates[iI].second);
		}
		szChunk += szItem;
	}
}

static int getSASGameSummaryRevealedPlotCount(TeamTypes eTeam)
{
	int iRevealed = 0;
	int iLoop = 0;
	for (CvArea const* pLoopArea = GC.getMap().firstArea(&iLoop); pLoopArea != NULL; pLoopArea = GC.getMap().nextArea(&iLoop))
		iRevealed += pLoopArea->getNumRevealedTiles(eTeam);
	return iRevealed;
}

void beginSASGameSummaryFullMapRevelation(TeamTypes eTeam, TechTypes eTech)
{
	FAssert(g_eSASGameSummaryFullMapRevelationTeam == NO_TEAM);
	FAssert(eTeam >= 0 && eTeam < MAX_CIV_TEAMS);
	FAssert(eTech != NO_TECH);
	g_eSASGameSummaryFullMapRevelationTeam = eTeam;
	g_iSASGameSummaryFullMapRevealedBefore = getSASGameSummaryRevealedPlotCount(eTeam);
}

void endSASGameSummaryFullMapRevelation(TeamTypes eTeam, TechTypes eTech)
{
	FAssert(g_eSASGameSummaryFullMapRevelationTeam == eTeam);
	int const iRevealed = getSASGameSummaryRevealedPlotCount(eTeam);
	int const iNewlyRevealed = iRevealed - g_iSASGameSummaryFullMapRevealedBefore;
	int const iRevealedPctX100 = (10000 * iRevealed) / std::max(1, (int)GC.getMap().numPlots());
	logSASGameSummary("GAME_SUMMARY_MAP_REVELATION turn=%d team=%d cause=MAP_VISIBLE_TECH tech=%s revealMode=FULL_MAP newlyRevealedCount=%d revealedPlots=%d revealedPctX100=%d", GC.getGame().getGameTurn(), eTeam, getSASGameSummaryTechType(eTech), iNewlyRevealed, iRevealed, iRevealedPctX100);
	g_eSASGameSummaryFullMapRevelationTeam = NO_TEAM;
	g_iSASGameSummaryFullMapRevealedBefore = 0;
}

void flushSASGameSummaryTurnChanges(int iGameTurn)
{
	if (g_iSASGameSummaryPendingPlotTurn < 0)
		return;
	FAssert(iGameTurn == g_iSASGameSummaryPendingPlotTurn);
	int const iLoggedTurn = iGameTurn;
	std::vector<CvString> aszPlotChunks;
	CvString szPlotChunk;
	for (size_t iI = 0; iI < g_aSASGameSummaryPlotChanges.size(); iI++)
		appendSASGameSummaryCoordinateChunks(aszPlotChunks, szPlotChunk, g_aSASGameSummaryPlotChanges[iI].szCategory.GetCString(), g_aSASGameSummaryPlotChanges[iI].aCoordinates);
	if (!szPlotChunk.empty())
		aszPlotChunks.push_back(szPlotChunk);
	for (size_t iI = 0; iI < aszPlotChunks.size(); iI++)
		logSASGameSummary("GAME_SUMMARY_PLOT_CHANGES turn=%d part=%d parts=%d changes=%s", iLoggedTurn, (int)iI + 1, (int)aszPlotChunks.size(), aszPlotChunks[iI].GetCString());
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		std::vector<std::pair<int,int> > const& aCoordinates = g_aaSASGameSummaryRevealedPlots[iI];
		if (aCoordinates.empty())
			continue;
		std::vector<CvString> aszRevelationChunks;
		CvString szRevelationChunk;
		appendSASGameSummaryCoordinateChunks(aszRevelationChunks, szRevelationChunk, "newlyRevealed", aCoordinates);
		if (!szRevelationChunk.empty())
			aszRevelationChunks.push_back(szRevelationChunk);
		// <!-- custom: CvMap::numPlots returns PlotNumTypes; casting it to int keeps MSVC 7.1 std::max template deduction unambiguous and fixed the compile error from adding map-revelation percentages. (GPT-5.6-Sol) -->
		int const iRevealedPctX100 = (10000 * getSASGameSummaryRevealedPlotCount((TeamTypes)iI)) / std::max(1, (int)GC.getMap().numPlots());
		for (size_t iJ = 0; iJ < aszRevelationChunks.size(); iJ++)
			logSASGameSummary("GAME_SUMMARY_MAP_REVELATION turn=%d team=%d cause=INCREMENTAL revealMode=COORDINATES newlyRevealedCount=%d part=%d parts=%d revealedPctX100=%d %s", iLoggedTurn, iI, (int)aCoordinates.size(), (int)iJ + 1, (int)aszRevelationChunks.size(), iRevealedPctX100, aszRevelationChunks[iJ].GetCString());
	}
	g_iSASGameSummaryPendingPlotTurn = -1;
	g_aSASGameSummaryPlotChanges.clear();
	for (int iI = 0; iI < MAX_TEAMS; iI++)
		g_aaSASGameSummaryRevealedPlots[iI].clear();
}

static void prepareSASGameSummaryTurnChanges()
{
	int const iGameTurn = GC.getGame().getGameTurn();
	if (g_iSASGameSummaryPendingPlotTurn >= 0 && g_iSASGameSummaryPendingPlotTurn != iGameTurn)
		flushSASGameSummaryTurnChanges(g_iSASGameSummaryPendingPlotTurn);
	if (g_iSASGameSummaryPendingPlotTurn < 0)
		g_iSASGameSummaryPendingPlotTurn = iGameTurn;
}

void recordSASGameSummaryPlotChange(CvPlot const& kPlot, SASGameSummaryPlotState const& kOldState, char const* szCategory, char const* szCause, bool bDetailed)
{
	if (GC.getGame().getElapsedGameTurns() <= 0 || !isSASGameSummaryPlotStateChanged(kOldState, kPlot))
		return;
	prepareSASGameSummaryTurnChanges();
	SASGameSummaryPlotChangeGroup* pGroup = NULL;
	for (size_t iI = 0; iI < g_aSASGameSummaryPlotChanges.size(); iI++)
	{
		if (g_aSASGameSummaryPlotChanges[iI].szCategory == szCategory)
		{
			pGroup = &g_aSASGameSummaryPlotChanges[iI];
			break;
		}
	}
	if (pGroup == NULL)
	{
		SASGameSummaryPlotChangeGroup kGroup;
		kGroup.szCategory = szCategory;
		g_aSASGameSummaryPlotChanges.push_back(kGroup);
		pGroup = &g_aSASGameSummaryPlotChanges.back();
	}
	addSASGameSummaryCoordinate(pGroup->aCoordinates, kPlot);
	if (bDetailed)
	{
		logSASGameSummary("GAME_SUMMARY_PLOT_CHANGE turn=%d cause=%s category=%s x=%d y=%d owner=%d terrainOld=%s terrainNew=%s featureOld=%s featureNew=%s bonusOld=%s bonusNew=%s improvementOld=%s improvementNew=%s routeOld=%s routeNew=%s extraFoodOld=%d extraFoodNew=%d extraProductionOld=%d extraProductionNew=%d extraCommerceOld=%d extraCommerceNew=%d",
				GC.getGame().getGameTurn(), szCause, szCategory, kPlot.getX(), kPlot.getY(), kPlot.getOwner(), getSASGameSummaryTerrainType(kOldState.eTerrain), getSASGameSummaryTerrainType(kPlot.getTerrainType()), getSASGameSummaryFeatureType(kOldState.eFeature), getSASGameSummaryFeatureType(kPlot.getFeatureType()), getSASGameSummaryBonusType(kOldState.eBonus), getSASGameSummaryBonusType(kPlot.getBonusType()), getSASGameSummaryImprovementType(kOldState.eImprovement), getSASGameSummaryImprovementType(kPlot.getImprovementType()), getSASGameSummaryRouteType(kOldState.eRoute), getSASGameSummaryRouteType(kPlot.getRouteType()), kOldState.aiExtraYield[YIELD_FOOD], GC.getMap().getPlotExtraYield(kPlot, YIELD_FOOD), kOldState.aiExtraYield[YIELD_PRODUCTION], GC.getMap().getPlotExtraYield(kPlot, YIELD_PRODUCTION), kOldState.aiExtraYield[YIELD_COMMERCE], GC.getMap().getPlotExtraYield(kPlot, YIELD_COMMERCE));
	}
}

void recordSASGameSummaryPlotRevealed(CvPlot const& kPlot, TeamTypes eTeam)
{
	if (GC.getGame().getElapsedGameTurns() <= 0 || eTeam < 0 || eTeam >= MAX_CIV_TEAMS)
		return;
	if (eTeam == g_eSASGameSummaryFullMapRevelationTeam)
		return;
	prepareSASGameSummaryTurnChanges();
	// <!-- custom: setRevealed calls this only on false-to-true transitions, so the same team cannot add this plot twice without first losing permanent revelation; append directly instead of repeatedly searching a potentially large map-trade list. (GPT-5.6-Sol) -->
	g_aaSASGameSummaryRevealedPlots[eTeam].push_back(std::make_pair(kPlot.getX(), kPlot.getY()));
}

void logSASGameSummaryEnvironmentTurn(int iPollution, int iSustainabilityThreshold, int iLandDefense, int iIndexBefore, int iIndexBeforeRestoration, int iIndexEnd, int iWarmingChances, int iEventTally)
{
	logSASGameSummary("GAME_SUMMARY_ENVIRONMENT_TURN turn=%d pollution=%d sustainabilityThreshold=%d landDefense=%d totalDefense=%d indexBefore=%d indexBeforeRestoration=%d indexEnd=%d indexDelta=%+d warmingChances=%d eventTally=%d severityPercent=%d active=%d",
			GC.getGame().getGameTurn(), iPollution, iSustainabilityThreshold, iLandDefense, iSustainabilityThreshold + iLandDefense, iIndexBefore, iIndexBeforeRestoration, iIndexEnd, iIndexEnd - iIndexBefore, iWarmingChances, iEventTally, GC.getGame().calculateGwSeverityRating(), iIndexEnd > 0);
}

void logSASGameSummaryBonusChanged(CvPlot const* pPlot, BonusTypes eOldBonus, BonusTypes eNewBonus)
{
	if (pPlot == NULL || eOldBonus == eNewBonus)
		return;
	SASGameSummaryPlotState kOldState(*pPlot);
	kOldState.eBonus = eOldBonus;
	recordSASGameSummaryPlotChange(*pPlot, kOldState, "resourceChanges", "RESOURCE_CHANGE", false);
	const char* szAction = (eOldBonus == NO_BONUS ? "appeared" : (eNewBonus == NO_BONUS ? "disappeared" : "changed"));
	CvCity const* pWorkingCity = pPlot->getWorkingCity();
	CvCity const* pPlotCity = pPlot->getPlotCity();
	// <!-- custom: Reproducible T129 crash dumps after adding this row failed in msvcr71!_output/_vsnprintf with an invalid read at 0x000003fc. The original argument for area=%d was pPlot->getArea(), but CvPlot::getArea returns CvArea&, not an integer; passing that object reference through varargs corrupted the following formatter reads. Logging the area ID explicitly fixed the crash in the next test run. (GPT-5.5) -->
	logSASGameSummary("GAME_SUMMARY_BONUS_CHANGE turn=%d elapsed=%d action=%s x=%d y=%d area=%d owner=%d oldBonus=%s newBonus=%s terrain=%s feature=%s improvement=%s route=%s water=%d hills=%d peak=%d riverSide=%d cityRadius=%d workingCity=%S workingCityId=%d plotCity=%S plotCityId=%d",
			GC.getGame().getGameTurn(), GC.getGame().getElapsedGameTurns(), szAction, pPlot->getX(), pPlot->getY(), pPlot->getArea().getID(), pPlot->getOwner(), getSASGameSummaryBonusType(eOldBonus), getSASGameSummaryBonusType(eNewBonus), getSASGameSummaryTerrainType(pPlot->getTerrainType()), getSASGameSummaryFeatureType(pPlot->getFeatureType()), getSASGameSummaryImprovementType(pPlot->getImprovementType()), getSASGameSummaryRouteType(pPlot->getRouteType()), pPlot->isWater(), pPlot->isHills(), pPlot->isPeak(), pPlot->isRiverSide(), pPlot->isCityRadius(), getSASGameSummaryQuotedCityName(pWorkingCity).GetCString(), (pWorkingCity == NULL ? -1 : pWorkingCity->getID()), getSASGameSummaryQuotedCityName(pPlotCity).GetCString(), (pPlotCity == NULL ? -1 : pPlotCity->getID()));
}

static const char* getSASGameSummaryCommerceType(CommerceTypes eCommerce)
{
	return (eCommerce == NO_COMMERCE ? "-" : GC.getInfo(eCommerce).getType());
}

static const char* getSASGameSummaryBuildType(BuildTypes eBuild)
{
	return (eBuild == NO_BUILD ? "-" : GC.getInfo(eBuild).getType());
}

static const char* getSASGameSummaryMissionType(MissionTypes eMission)
{
	return (eMission == NO_MISSION ? "-" : GC.getInfo(eMission).getType());
}

static const char* getSASGameSummaryEspionageMissionType(EspionageMissionTypes eMission)
{
	return (eMission == NO_ESPIONAGEMISSION ? "-" : GC.getInfo(eMission).getType());
}

static const char* getSASGameSummaryUnitAIType(UnitAITypes eUnitAI)
{
	return (eUnitAI == NO_UNITAI ? "-" : GC.getInfo(eUnitAI).getType());
}

static const char* getSASGameSummaryUnitCombatType(UnitCombatTypes eUnitCombat)
{
	return (eUnitCombat == NO_UNITCOMBAT ? "-" : GC.getInfo(eUnitCombat).getType());
}

static const char* getSASGameSummaryPromotionType(PromotionTypes ePromotion)
{
	return (ePromotion == NO_PROMOTION ? "-" : GC.getInfo(ePromotion).getType());
}

static const char* getSASGameSummarySpecialistType(SpecialistTypes eSpecialist)
{
	return (eSpecialist == NO_SPECIALIST ? "-" : GC.getInfo(eSpecialist).getType());
}

static const char* getSASGameSummaryProcessType(ProcessTypes eProcess)
{
	return (eProcess == NO_PROCESS ? "-" : GC.getInfo(eProcess).getType());
}

static const char* getSASGameSummaryCivicType(CivicTypes eCivic)
{
	return (eCivic == NO_CIVIC ? "-" : GC.getInfo(eCivic).getType());
}

static const char* getSASGameSummaryVoteSourceType(VoteSourceTypes eVoteSource)
{
	return (eVoteSource == NO_VOTESOURCE ? "-" : GC.getInfo(eVoteSource).getType());
}

static const char* getSASGameSummaryVoteType(VoteTypes eVote)
{
	return (eVote == NO_VOTE ? "-" : GC.getInfo(eVote).getType());
}

static const char* getSASGameSummaryEraType(EraTypes eEra)
{
	return (eEra == NO_ERA ? "-" : GC.getInfo(eEra).getType());
}

static void appendSASGameSummaryTypeCount(CvString& szList, const char* szType, int iCount)
{
	if (iCount <= 0)
		return;
	CvString szItem;
	szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", szType, iCount);
	szList += szItem;
}

static CvString getSASGameSummaryOrDash(CvString const& szList)
{
	return szList.empty() ? CvString("-") : szList;
}

static void appendSASGameSummaryPositiveValue(CvString& szList, const char* szName, int iValue)
{
	if (iValue <= 0)
		return;
	CvString szItem;
	szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", szName, iValue);
	szList += szItem;
}

static void appendSASGameSummaryValue(CvString& szList, const char* szName, int iValue)
{
	CvString szItem;
	szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", szName, iValue);
	szList += szItem;
}

static void appendSASGameSummarySignedValue(CvString& szList, const char* szName, int iValue)
{
	if (iValue == 0)
		return;
	CvString szItem;
	szItem.Format(szList.empty() ? "%s:%+d" : ",%s:%+d", szName, iValue);
	szList += szItem;
}

static void addSASGameSummaryPlotComposition(SASGameSummaryPlotComposition& kComposition, CvPlot const& kPlot, TeamTypes eTeam)
{
	kComposition.iPlots++;
	if (kPlot.isWater())
		kComposition.iWater++;
	else kComposition.iLand++;
	if (kPlot.isHills())
		kComposition.iHills++;
	if (kPlot.isPeak())
		kComposition.iPeaks++;
	if (kPlot.isRiverSide())
		kComposition.iRiverSide++;
	if (kPlot.isFreshWater())
		kComposition.iFreshWater++;
	if (kPlot.isCoastalLand())
		kComposition.iCoastal++;
	if (kPlot.getTerrainType() != NO_TERRAIN)
		kComposition.aiTerrains[kPlot.getTerrainType()]++;
	if (kPlot.getFeatureType() != NO_FEATURE)
		kComposition.aiFeatures[kPlot.getFeatureType()]++;
	ImprovementTypes eImprovement = kPlot.getImprovementType();
	if (eImprovement != NO_IMPROVEMENT)
	{
		kComposition.iImproved++;
		kComposition.aiImprovements[eImprovement]++;
	}
	else if (!kPlot.isWater())
	{
		kComposition.iUnimprovedLand++;
	}
	RouteTypes eRoute = kPlot.getRouteType();
	if (eRoute != NO_ROUTE)
	{
		kComposition.iRoaded++;
		kComposition.aiRoutes[eRoute]++;
	}
	BonusTypes eBonus = kPlot.getBonusType(eTeam);
	if (eBonus != NO_BONUS)
	{
		kComposition.aiBonuses[eBonus]++;
		if (eImprovement != NO_IMPROVEMENT)
			kComposition.iBonusImproved++;
		else kComposition.iBonusUnimproved++;
	}
	if (kPlot.isBeingWorked())
	{
		kComposition.iWorked++;
		if (eImprovement != NO_IMPROVEMENT)
			kComposition.iWorkedImproved++;
		else kComposition.iWorkedUnimproved++;
	}
	kComposition.iNatureFood += kPlot.calculateBestNatureYield(YIELD_FOOD, eTeam);
	kComposition.iNatureProduction += kPlot.calculateBestNatureYield(YIELD_PRODUCTION, eTeam);
	kComposition.iNatureCommerce += kPlot.calculateBestNatureYield(YIELD_COMMERCE, eTeam);
	kComposition.iCurrentFood += kPlot.calculateYield(YIELD_FOOD);
	kComposition.iCurrentProduction += kPlot.calculateYield(YIELD_PRODUCTION);
	kComposition.iCurrentCommerce += kPlot.calculateYield(YIELD_COMMERCE);
}

static int getSASGameSummaryPercentX100(int iValue, int iTotal)
{
	return (iTotal <= 0 ? -1 : (10000 * iValue) / iTotal);
}

// <!-- custom: Add lightweight owned-territory counts to the map scan already used by the expansion summary, rather than scanning every plot again or calculating unused plot yields. BFC means the plot is assigned to one of this player's cities; development land excludes city centers and peaks because Workers cannot add ordinary improvements there. (GPT-5.6-Sol) -->
static void addSASGameSummaryTerritoryDevelopment(SASGameSummaryTerritoryDevelopment& kDevelopment, CvPlot const& kPlot, PlayerTypes ePlayer, TeamTypes eTeam, ImprovementTypes eFarm)
{
	SASGameSummaryPlotComposition& kOwned = kDevelopment.kOwned;
	kOwned.iPlots++;
	if (kPlot.isWater())
		kOwned.iWater++;
	else kOwned.iLand++;
	if (kPlot.getTerrainType() != NO_TERRAIN)
		kOwned.aiTerrains[kPlot.getTerrainType()]++;
	if (kPlot.getFeatureType() != NO_FEATURE)
		kOwned.aiFeatures[kPlot.getFeatureType()]++;
	CvCity const* pWorkingCity = kPlot.getWorkingCity();
	bool const bBFC = (pWorkingCity != NULL && pWorkingCity->getOwner() == ePlayer);
	if (bBFC)
		kDevelopment.iBFCPlots++;
	else kDevelopment.iSuburbPlots++;
	ImprovementTypes const eImprovement = kPlot.getImprovementType();
	bool const bImproved = (eImprovement != NO_IMPROVEMENT);
	if (bImproved)
	{
		kOwned.iImproved++;
		kOwned.aiImprovements[eImprovement]++;
	}
	RouteTypes const eRoute = kPlot.getRouteType();
	if (eRoute != NO_ROUTE)
	{
		kOwned.iRoaded++;
		kOwned.aiRoutes[eRoute]++;
	}
	BonusTypes const eBonus = kPlot.getBonusType(eTeam);
	if (eBonus != NO_BONUS)
	{
		kOwned.aiBonuses[eBonus]++;
		if (bImproved)
		{
			kOwned.iBonusImproved++;
			kDevelopment.aiImprovedBonuses[eBonus]++;
		}
		else
		{
			kOwned.iBonusUnimproved++;
			kDevelopment.aiUnimprovedBonuses[eBonus]++;
		}
	}
	bool const bDevelopmentLand = (!kPlot.isWater() && !kPlot.isPeak() && !kPlot.isCity());
	if (bDevelopmentLand)
	{
		kDevelopment.iDevelopmentLand++;
		if (bImproved)
			kDevelopment.iImprovedLand++;
		if (bBFC)
		{
			kDevelopment.iBFCDevelopmentLand++;
			if (bImproved)
				kDevelopment.iBFCImprovedLand++;
		}
		else
		{
			kDevelopment.iSuburbDevelopmentLand++;
			if (bImproved)
				kDevelopment.iSuburbImprovedLand++;
		}
	}
	else if (kPlot.isWater() && (eBonus != NO_BONUS || bImproved))
	{
		// <!-- custom: Ordinary water cannot receive an improvement. Count only visible bonus water or an already improved water plot in the development denominator, so seafood coverage is not diluted by unusable ocean. (GPT-5.6-Sol) -->
		kDevelopment.iDevelopmentWater++;
		if (bImproved)
			kDevelopment.iImprovedWater++;
	}
	if (eImprovement != eFarm)
		return;
	kDevelopment.iFarms++;
	bool const bIrrigated = kPlot.isIrrigated();
	if (bIrrigated)
		kDevelopment.iIrrigatedFarms++;
	else kDevelopment.iDryFarms++;
	if (eBonus != NO_BONUS)
	{
		kDevelopment.iBonusFarms++;
		if (bIrrigated)
			kDevelopment.iIrrigatedBonusFarms++;
		else kDevelopment.iDryBonusFarms++;
	}
	if (bBFC)
	{
		kDevelopment.iBFCFarms++;
		if (bIrrigated)
			kDevelopment.iBFCIrrigatedFarms++;
		else kDevelopment.iBFCDryFarms++;
	}
}

static void getSASGameSummaryImprovementRouteTypes(SASGameSummaryPlotComposition const& kComposition, CvString& szImprovements, CvString& szRoutes)
{
	for (int iI = 0; iI < GC.getNumImprovementInfos(); iI++)
		appendSASGameSummaryTypeCount(szImprovements, getSASGameSummaryImprovementType((ImprovementTypes)iI), kComposition.aiImprovements[iI]);
	for (int iI = 0; iI < GC.getNumRouteInfos(); iI++)
		appendSASGameSummaryTypeCount(szRoutes, getSASGameSummaryRouteType((RouteTypes)iI), kComposition.aiRoutes[iI]);
}

static void getSASGameSummaryLandscapeTypes(SASGameSummaryPlotComposition const& kComposition, CvString& szTerrains, CvString& szFeatures, CvString& szBonuses)
{
	for (int iI = 0; iI < GC.getNumTerrainInfos(); iI++)
		appendSASGameSummaryTypeCount(szTerrains, getSASGameSummaryTerrainType((TerrainTypes)iI), kComposition.aiTerrains[iI]);
	for (int iI = 0; iI < GC.getNumFeatureInfos(); iI++)
		appendSASGameSummaryTypeCount(szFeatures, getSASGameSummaryFeatureType((FeatureTypes)iI), kComposition.aiFeatures[iI]);
	for (int iI = 0; iI < GC.getNumBonusInfos(); iI++)
		appendSASGameSummaryTypeCount(szBonuses, getSASGameSummaryBonusType((BonusTypes)iI), kComposition.aiBonuses[iI]);
}

static void logSASGameSummaryTerritoryDevelopment(PlayerTypes ePlayer, int iGameTurn, SASGameSummaryTerritoryDevelopment const& kDevelopment)
{
	SASGameSummaryPlotComposition const& kOwned = kDevelopment.kOwned;
	SASGameSummaryPlayerPrevious& kPrevious = g_akSASGameSummaryPlayerPrevious[ePlayer];
	CvString szImprovements;
	CvString szRoutes;
	getSASGameSummaryImprovementRouteTypes(kOwned, szImprovements, szRoutes);
	int const iDevelopmentPlots = kDevelopment.iDevelopmentLand + kDevelopment.iDevelopmentWater;
	int const iImprovedPlots = kDevelopment.iImprovedLand + kDevelopment.iImprovedWater;
	int const iSuburbFarms = kDevelopment.iFarms - kDevelopment.iBFCFarms;
	int const iSuburbIrrigatedFarms = kDevelopment.iIrrigatedFarms - kDevelopment.iBFCIrrigatedFarms;
	int const iSuburbDryFarms = kDevelopment.iDryFarms - kDevelopment.iBFCDryFarms;
	logSASGameSummary("GAME_SUMMARY_TERRITORY_DEVELOPMENT turn=%d player=%d deltaValid=%d ownedPlots=%d ownedLand=%d ownedWater=%d bfcPlots=%d suburbPlots=%d developmentPlots=%d improvedPlots=%d improvedPercentX100=%d developmentLand=%d improvedLand=%d improvedLandDelta=%+d improvedLandPercentX100=%d developmentWater=%d improvedWater=%d improvedWaterDelta=%+d improvedWaterPercentX100=%d"
			" bfcDevelopmentLand=%d bfcImprovedLand=%d bfcImprovedLandPercentX100=%d suburbDevelopmentLand=%d suburbImprovedLand=%d suburbImprovedLandPercentX100=%d roaded=%d roadedDelta=%+d bonusImproved=%d bonusUnimproved=%d"
			" farms=%d farmsDelta=%+d irrigatedFarms=%d irrigatedFarmsDelta=%+d dryFarms=%d dryFarmsDelta=%+d irrigatedFarmPercentX100=%d dryFarmPercentX100=%d bonusFarms=%d irrigatedBonusFarms=%d dryBonusFarms=%d bfcFarms=%d bfcIrrigatedFarms=%d bfcDryFarms=%d bfcIrrigatedFarmPercentX100=%d suburbFarms=%d suburbIrrigatedFarms=%d suburbDryFarms=%d suburbIrrigatedFarmPercentX100=%d improvements=%s routes=%s",
			iGameTurn, ePlayer, kPrevious.bValid, kOwned.iPlots, kOwned.iLand, kOwned.iWater, kDevelopment.iBFCPlots, kDevelopment.iSuburbPlots, iDevelopmentPlots, iImprovedPlots, getSASGameSummaryPercentX100(iImprovedPlots, iDevelopmentPlots),
			kDevelopment.iDevelopmentLand, kDevelopment.iImprovedLand, getSASGameSummaryDelta(kPrevious.bValid, kDevelopment.iImprovedLand, kPrevious.iTerritoryImprovedLand), getSASGameSummaryPercentX100(kDevelopment.iImprovedLand, kDevelopment.iDevelopmentLand), kDevelopment.iDevelopmentWater, kDevelopment.iImprovedWater, getSASGameSummaryDelta(kPrevious.bValid, kDevelopment.iImprovedWater, kPrevious.iTerritoryImprovedWater), getSASGameSummaryPercentX100(kDevelopment.iImprovedWater, kDevelopment.iDevelopmentWater),
			kDevelopment.iBFCDevelopmentLand, kDevelopment.iBFCImprovedLand, getSASGameSummaryPercentX100(kDevelopment.iBFCImprovedLand, kDevelopment.iBFCDevelopmentLand), kDevelopment.iSuburbDevelopmentLand, kDevelopment.iSuburbImprovedLand, getSASGameSummaryPercentX100(kDevelopment.iSuburbImprovedLand, kDevelopment.iSuburbDevelopmentLand), kOwned.iRoaded, getSASGameSummaryDelta(kPrevious.bValid, kOwned.iRoaded, kPrevious.iTerritoryRoaded), kOwned.iBonusImproved, kOwned.iBonusUnimproved,
			kDevelopment.iFarms, getSASGameSummaryDelta(kPrevious.bValid, kDevelopment.iFarms, kPrevious.iTerritoryFarms), kDevelopment.iIrrigatedFarms, getSASGameSummaryDelta(kPrevious.bValid, kDevelopment.iIrrigatedFarms, kPrevious.iTerritoryIrrigatedFarms), kDevelopment.iDryFarms, getSASGameSummaryDelta(kPrevious.bValid, kDevelopment.iDryFarms, kPrevious.iTerritoryDryFarms), getSASGameSummaryPercentX100(kDevelopment.iIrrigatedFarms, kDevelopment.iFarms), getSASGameSummaryPercentX100(kDevelopment.iDryFarms, kDevelopment.iFarms),
			kDevelopment.iBonusFarms, kDevelopment.iIrrigatedBonusFarms, kDevelopment.iDryBonusFarms, kDevelopment.iBFCFarms, kDevelopment.iBFCIrrigatedFarms, kDevelopment.iBFCDryFarms, getSASGameSummaryPercentX100(kDevelopment.iBFCIrrigatedFarms, kDevelopment.iBFCFarms), iSuburbFarms, iSuburbIrrigatedFarms, iSuburbDryFarms, getSASGameSummaryPercentX100(iSuburbIrrigatedFarms, iSuburbFarms), getSASGameSummaryOrDash(szImprovements).GetCString(), getSASGameSummaryOrDash(szRoutes).GetCString());
	if (gGameSummaryLogLevel >= 3)
	{
		CvString szTerrains;
		CvString szFeatures;
		CvString szBonuses;
		CvString szImprovedBonuses;
		CvString szUnimprovedBonuses;
		getSASGameSummaryLandscapeTypes(kOwned, szTerrains, szFeatures, szBonuses);
		for (int iI = 0; iI < GC.getNumBonusInfos(); iI++)
		{
			appendSASGameSummaryTypeCount(szImprovedBonuses, getSASGameSummaryBonusType((BonusTypes)iI), kDevelopment.aiImprovedBonuses[iI]);
			appendSASGameSummaryTypeCount(szUnimprovedBonuses, getSASGameSummaryBonusType((BonusTypes)iI), kDevelopment.aiUnimprovedBonuses[iI]);
		}
		logSASGameSummary("GAME_SUMMARY_TERRITORY_LANDSCAPE turn=%d player=%d terrains=%s features=%s bonuses=%s improvedBonuses=%s unimprovedBonuses=%s", iGameTurn, ePlayer, getSASGameSummaryOrDash(szTerrains).GetCString(), getSASGameSummaryOrDash(szFeatures).GetCString(), getSASGameSummaryOrDash(szBonuses).GetCString(), getSASGameSummaryOrDash(szImprovedBonuses).GetCString(), getSASGameSummaryOrDash(szUnimprovedBonuses).GetCString());
	}
	kPrevious.iTerritoryImprovedLand = kDevelopment.iImprovedLand;
	kPrevious.iTerritoryImprovedWater = kDevelopment.iImprovedWater;
	kPrevious.iTerritoryRoaded = kOwned.iRoaded;
	kPrevious.iTerritoryFarms = kDevelopment.iFarms;
	kPrevious.iTerritoryIrrigatedFarms = kDevelopment.iIrrigatedFarms;
	kPrevious.iTerritoryDryFarms = kDevelopment.iDryFarms;
}

static void getSASGameSummaryPlotCompositionTypes(SASGameSummaryPlotComposition const& kComposition, CvString& szTerrains, CvString& szFeatures, CvString& szBonuses, CvString& szImprovements, CvString& szRoutes)
{
	getSASGameSummaryLandscapeTypes(kComposition, szTerrains, szFeatures, szBonuses);
	getSASGameSummaryImprovementRouteTypes(kComposition, szImprovements, szRoutes);
}

static void logSASGameSummaryKnownArea(PlayerTypes ePlayer, const char* szReason)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	TeamTypes eTeam = kPlayer.getTeam();
	if (eTeam == NO_TEAM)
		return;
	SASGameSummaryPlotComposition kRevealed;
	SASGameSummaryPlotComposition kVisible;
	CvMap const& kMap = GC.getMap();
	for (int iI = 0; iI < kMap.numPlots(); iI++)
	{
		CvPlot const& kPlot = kMap.getPlotByIndex(iI);
		if (kPlot.isRevealed(eTeam, false))
			addSASGameSummaryPlotComposition(kRevealed, kPlot, eTeam);
		if (kPlot.isVisible(eTeam, false))
			addSASGameSummaryPlotComposition(kVisible, kPlot, eTeam);
	}
	logSASGameSummary("GAME_SUMMARY_KNOWN_AREA turn=%d reason=%s player=%d team=%d revealedPlots=%d visiblePlots=%d revealedLand=%d visibleLand=%d revealedWater=%d visibleWater=%d revealedHills=%d visibleHills=%d revealedPeaks=%d visiblePeaks=%d revealedRiverSide=%d visibleRiverSide=%d revealedFreshWater=%d visibleFreshWater=%d revealedCoastal=%d visibleCoastal=%d revealedImproved=%d visibleImproved=%d revealedUnimprovedLand=%d visibleUnimprovedLand=%d revealedRoaded=%d visibleRoaded=%d revealedBonusImproved=%d visibleBonusImproved=%d revealedBonusUnimproved=%d visibleBonusUnimproved=%d revealedNatureFood=%d visibleNatureFood=%d revealedNatureProd=%d visibleNatureProd=%d revealedNatureCommerce=%d visibleNatureCommerce=%d revealedCurrentFood=%d visibleCurrentFood=%d revealedCurrentProd=%d visibleCurrentProd=%d revealedCurrentCommerce=%d visibleCurrentCommerce=%d",
			GC.getGame().getGameTurn(), szReason, ePlayer, eTeam, kRevealed.iPlots, kVisible.iPlots, kRevealed.iLand, kVisible.iLand, kRevealed.iWater, kVisible.iWater, kRevealed.iHills, kVisible.iHills, kRevealed.iPeaks, kVisible.iPeaks, kRevealed.iRiverSide, kVisible.iRiverSide, kRevealed.iFreshWater, kVisible.iFreshWater, kRevealed.iCoastal, kVisible.iCoastal, kRevealed.iImproved, kVisible.iImproved, kRevealed.iUnimprovedLand, kVisible.iUnimprovedLand, kRevealed.iRoaded, kVisible.iRoaded, kRevealed.iBonusImproved, kVisible.iBonusImproved, kRevealed.iBonusUnimproved, kVisible.iBonusUnimproved, kRevealed.iNatureFood, kVisible.iNatureFood, kRevealed.iNatureProduction, kVisible.iNatureProduction, kRevealed.iNatureCommerce, kVisible.iNatureCommerce, kRevealed.iCurrentFood, kVisible.iCurrentFood, kRevealed.iCurrentProduction, kVisible.iCurrentProduction, kRevealed.iCurrentCommerce, kVisible.iCurrentCommerce);
	CvString szRevealedTerrains;
	CvString szVisibleTerrains;
	CvString szRevealedFeatures;
	CvString szVisibleFeatures;
	CvString szRevealedBonuses;
	CvString szVisibleBonuses;
	CvString szRevealedImprovements;
	CvString szVisibleImprovements;
	CvString szRevealedRoutes;
	CvString szVisibleRoutes;
	getSASGameSummaryPlotCompositionTypes(kRevealed, szRevealedTerrains, szRevealedFeatures, szRevealedBonuses, szRevealedImprovements, szRevealedRoutes);
	getSASGameSummaryPlotCompositionTypes(kVisible, szVisibleTerrains, szVisibleFeatures, szVisibleBonuses, szVisibleImprovements, szVisibleRoutes);
	logSASGameSummary("GAME_SUMMARY_KNOWN_AREA_TYPES turn=%d reason=%s player=%d team=%d revealedTerrains=%s visibleTerrains=%s revealedFeatures=%s visibleFeatures=%s revealedBonuses=%s visibleBonuses=%s revealedImprovements=%s visibleImprovements=%s revealedRoutes=%s visibleRoutes=%s",
			GC.getGame().getGameTurn(), szReason, ePlayer, eTeam, getSASGameSummaryOrDash(szRevealedTerrains).GetCString(), getSASGameSummaryOrDash(szVisibleTerrains).GetCString(), getSASGameSummaryOrDash(szRevealedFeatures).GetCString(), getSASGameSummaryOrDash(szVisibleFeatures).GetCString(), getSASGameSummaryOrDash(szRevealedBonuses).GetCString(), getSASGameSummaryOrDash(szVisibleBonuses).GetCString(), getSASGameSummaryOrDash(szRevealedImprovements).GetCString(), getSASGameSummaryOrDash(szVisibleImprovements).GetCString(), getSASGameSummaryOrDash(szRevealedRoutes).GetCString(), getSASGameSummaryOrDash(szVisibleRoutes).GetCString());
}

static void logSASGameSummaryStartingUnits(PlayerTypes ePlayer, const char* szReason)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	if (GC.getGame().getElapsedGameTurns() > 1)
		return;
	int iLoop = 0;
	for (CvUnit const* pLoopUnit = kPlayer.firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iLoop))
	{
		CvPlot const& kPlot = pLoopUnit->getPlot();
		logSASGameSummary("GAME_SUMMARY_STARTING_UNIT turn=%d reason=%s player=%d unitId=%d unit=%s unitAI=%s unitCombat=%s x=%d y=%d damage=%d xp=%d level=%d movesLeft=%d plotOwner=%d plotTerrain=%s plotFeature=%s plotBonus=%s plotImprovement=%s plotRoute=%s",
				GC.getGame().getGameTurn(), szReason, ePlayer, pLoopUnit->getID(), getSASGameSummaryUnitType(pLoopUnit->getUnitType()), getSASGameSummaryUnitAIType(pLoopUnit->AI_getUnitAIType()), getSASGameSummaryUnitCombatType(pLoopUnit->getUnitInfo().getUnitCombatType()), pLoopUnit->getX(), pLoopUnit->getY(), pLoopUnit->getDamage(), pLoopUnit->getExperience(), pLoopUnit->getLevel(), pLoopUnit->movesLeft(), kPlot.getOwner(), getSASGameSummaryTerrainType(kPlot.getTerrainType()), getSASGameSummaryFeatureType(kPlot.getFeatureType()), getSASGameSummaryBonusType(kPlot.getBonusType(pLoopUnit->getTeam())), getSASGameSummaryImprovementType(kPlot.getImprovementType()), getSASGameSummaryRouteType(kPlot.getRouteType()));
	}
}

static void logSASGameSummaryCityBFC(CvCity const& kCity, const char* szReason)
{
	CvString szTerrains;
	CvString szFeatures;
	CvString szBonuses;
	CvString szImprovements;
	CvString szRoutes;
	SASGameSummaryPlotComposition kComposition;
	int iOwned = 0;
	TeamTypes eTeam = GET_PLAYER(kCity.getOwner()).getTeam();
	for (CityPlotIter it(kCity); it.hasNext(); ++it)
	{
		CvPlot const& kPlot = *it;
		if (kPlot.getOwner() == kCity.getOwner())
			iOwned++;
		addSASGameSummaryPlotComposition(kComposition, kPlot, eTeam);
	}
	getSASGameSummaryPlotCompositionTypes(kComposition, szTerrains, szFeatures, szBonuses, szImprovements, szRoutes);
	logSASGameSummary("GAME_SUMMARY_CITY_BFC turn=%d reason=%s player=%d cityId=%d city=%S x=%d y=%d plots=%d owned=%d land=%d water=%d hills=%d peaks=%d riverSide=%d freshWater=%d coastal=%d improved=%d unimprovedLand=%d roaded=%d bonusImproved=%d bonusUnimproved=%d worked=%d workedImproved=%d workedUnimproved=%d natureFood=%d natureProd=%d natureCommerce=%d currentFood=%d currentProd=%d currentCommerce=%d terrains=%s features=%s bonuses=%s improvements=%s routes=%s",
			GC.getGame().getGameTurn(), szReason, kCity.getOwner(), kCity.getID(), getSASGameSummaryQuotedCityName(&kCity).GetCString(), kCity.getX(), kCity.getY(), kComposition.iPlots, iOwned, kComposition.iLand, kComposition.iWater, kComposition.iHills, kComposition.iPeaks, kComposition.iRiverSide, kComposition.iFreshWater, kComposition.iCoastal, kComposition.iImproved, kComposition.iUnimprovedLand, kComposition.iRoaded, kComposition.iBonusImproved, kComposition.iBonusUnimproved, kComposition.iWorked, kComposition.iWorkedImproved, kComposition.iWorkedUnimproved, kComposition.iNatureFood, kComposition.iNatureProduction, kComposition.iNatureCommerce, kComposition.iCurrentFood, kComposition.iCurrentProduction, kComposition.iCurrentCommerce, getSASGameSummaryOrDash(szTerrains).GetCString(), getSASGameSummaryOrDash(szFeatures).GetCString(), getSASGameSummaryOrDash(szBonuses).GetCString(), getSASGameSummaryOrDash(szImprovements).GetCString(), getSASGameSummaryOrDash(szRoutes).GetCString());
}

static SASGameSummaryPlotComposition getSASGameSummaryWorkedPlotComposition(CvCity const& kCity)
{
	SASGameSummaryPlotComposition kComposition;
	const TeamTypes eTeam = GET_PLAYER(kCity.getOwner()).getTeam();
	// <!-- custom: Exclude the city center from worked-plot allocation summaries because it is always worked and would blur comparisons of citizen plot choices and improvement coverage between benchmark runs. (GPT-5.5) -->
	for (WorkingPlotIter it(kCity, false); it.hasNext(); ++it)
		addSASGameSummaryPlotComposition(kComposition, *it, eTeam);
	return kComposition;
}

static void addSASGameSummaryPlotComposition(SASGameSummaryPlotComposition& kTarget, SASGameSummaryPlotComposition const& kSource)
{
	kTarget.iPlots += kSource.iPlots;
	kTarget.iLand += kSource.iLand;
	kTarget.iWater += kSource.iWater;
	kTarget.iHills += kSource.iHills;
	kTarget.iPeaks += kSource.iPeaks;
	kTarget.iRiverSide += kSource.iRiverSide;
	kTarget.iFreshWater += kSource.iFreshWater;
	kTarget.iCoastal += kSource.iCoastal;
	kTarget.iImproved += kSource.iImproved;
	kTarget.iUnimprovedLand += kSource.iUnimprovedLand;
	kTarget.iRoaded += kSource.iRoaded;
	kTarget.iBonusImproved += kSource.iBonusImproved;
	kTarget.iBonusUnimproved += kSource.iBonusUnimproved;
	kTarget.iWorked += kSource.iWorked;
	kTarget.iWorkedImproved += kSource.iWorkedImproved;
	kTarget.iWorkedUnimproved += kSource.iWorkedUnimproved;
	kTarget.iNatureFood += kSource.iNatureFood;
	kTarget.iNatureProduction += kSource.iNatureProduction;
	kTarget.iNatureCommerce += kSource.iNatureCommerce;
	kTarget.iCurrentFood += kSource.iCurrentFood;
	kTarget.iCurrentProduction += kSource.iCurrentProduction;
	kTarget.iCurrentCommerce += kSource.iCurrentCommerce;
	for (int iI = 0; iI < GC.getNumTerrainInfos(); iI++)
		kTarget.aiTerrains[iI] += kSource.aiTerrains[iI];
	for (int iI = 0; iI < GC.getNumFeatureInfos(); iI++)
		kTarget.aiFeatures[iI] += kSource.aiFeatures[iI];
	for (int iI = 0; iI < GC.getNumBonusInfos(); iI++)
		kTarget.aiBonuses[iI] += kSource.aiBonuses[iI];
	for (int iI = 0; iI < GC.getNumImprovementInfos(); iI++)
		kTarget.aiImprovements[iI] += kSource.aiImprovements[iI];
	for (int iI = 0; iI < GC.getNumRouteInfos(); iI++)
		kTarget.aiRoutes[iI] += kSource.aiRoutes[iI];
}

static CvString getSASGameSummaryTechEraCounts(TeamTypes eTeam)
{
	std::vector<int> aiEras(GC.getNumEraInfos(), 0);
	CvTeam const& kTeam = GET_TEAM(eTeam);
	FOR_EACH_ENUM(Tech)
	{
		if (!kTeam.isHasTech(eLoopTech))
			continue;
		EraTypes eEra = GC.getInfo(eLoopTech).getEra();
		if (eEra != NO_ERA)
			aiEras[eEra]++;
	}
	CvString szList;
	for (int iI = 0; iI < GC.getNumEraInfos(); iI++)
		appendSASGameSummaryTypeCount(szList, getSASGameSummaryEraType((EraTypes)iI), aiEras[iI]);
	return getSASGameSummaryOrDash(szList);
}

static void logSASGameSummaryPlayerSetup(PlayerTypes ePlayer)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvInitCore const& kInitCore = GC.getInitCore();
	const char* szCivType = (kPlayer.getCivilizationType() == NO_CIVILIZATION ? "-" : GC.getInfo(kPlayer.getCivilizationType()).getType());
	const char* szLeaderType = (kPlayer.getLeaderType() == NO_LEADER ? "-" : GC.getInfo(kPlayer.getLeaderType()).getType());
	const wchar* szLeaderName = (kPlayer.getLeaderType() == NO_LEADER ? L"-" : GC.getInfo(kPlayer.getLeaderType()).getDescription());
	// <!-- custom: During AI Auto Play, isHuman becomes false for the original human slot while isHumanDisabled becomes true. Record both states explicitly so setup/load rows do not make the same player appear ambiguously human in one place and AI-controlled in another. (GPT-5.6-Sol) -->
	const bool bCurrentlyHumanControlled = kPlayer.isHuman();
	const bool bAutoplayControlled = kPlayer.isHumanDisabled();
	const bool bHumanSlot = (bCurrentlyHumanControlled || bAutoplayControlled);
	CvString szTraits;
	FOR_EACH_ENUM(Trait)
	{
		if (!kPlayer.hasTrait(eLoopTrait))
			continue;
		if (!szTraits.empty())
			szTraits += ",";
		szTraits += GC.getInfo(eLoopTrait).getType();
	}
	// <!-- custom: Leader traits and favorites are fixed but materially explain AI behavior and economic results. Record them once per setup/load rather than repeating them in periodic player or policy snapshots. (GPT-5.6-Sol) -->
	logSASGameSummary("GAME_SUMMARY_PLAYER_SETUP turn=%d player=%d team=%d alive=%d everAlive=%d human=%d humanSlot=%d currentlyHumanControlled=%d autoplayControlled=%d slotStatus=%d playerName=%S civType=%s civName=%S civShortName=%S leaderType=%s leaderName=%S traits=%s favoriteCivic=%s favoriteReligion=%s handicap=%s",
			GC.getGame().getGameTurn(), ePlayer, kPlayer.getTeam(), kPlayer.isAlive(), kPlayer.isEverAlive(), bCurrentlyHumanControlled, bHumanSlot, bCurrentlyHumanControlled, bAutoplayControlled, kInitCore.getSlotStatus(ePlayer), getSASGameSummaryQuoted(kPlayer.getName(0)).GetCString(), szCivType, getSASGameSummaryQuoted(kPlayer.getCivilizationDescription(0)).GetCString(), getSASGameSummaryQuoted(kPlayer.getCivilizationShortDescription(0)).GetCString(), szLeaderType, getSASGameSummaryQuoted(szLeaderName).GetCString(), getSASGameSummaryOrDash(szTraits).GetCString(), getSASGameSummaryCivicType(kPlayer.getFavoriteCivic()), getSASGameSummaryReligionType(kPlayer.getFavoriteReligion()), kPlayer.getHandicapType() == NO_HANDICAP ? "-" : GC.getInfo(kPlayer.getHandicapType()).getType());
}

static void logSASGameSummaryAttitudeLegend()
{
	const int iFuriousMax = GC.getDefineINT(CvGlobals::RELATIONS_THRESH_FURIOUS);
	const int iAnnoyedMax = GC.getDefineINT(CvGlobals::RELATIONS_THRESH_ANNOYED);
	const int iPleasedMin = GC.getDefineINT(CvGlobals::RELATIONS_THRESH_PLEASED);
	const int iFriendlyMin = GC.getDefineINT(CvGlobals::RELATIONS_THRESH_FRIENDLY);
	logSASGameSummary("GAME_SUMMARY_ATTITUDE_LEGEND valueFrom=AI_getAttitudeVal furious=<=%d annoyed=%d..%d cautious=%d..%d pleased=%d..%d friendly=>=%d",
			iFuriousMax, iFuriousMax + 1, iAnnoyedMax, iAnnoyedMax + 1, iPleasedMin - 1, iPleasedMin, iFriendlyMin - 1, iFriendlyMin);
}

static void logSASGameSummaryInitialContext()
{
	// <!-- custom: Archived summaries can otherwise be mistaken for logs from another Civ4 mod. Record the active cached mod folder name and mod-relative path once, without relying on file timestamps or a manually maintained version string. (GPT-5.6-Sol) -->
	logSASGameSummary("GAME_SUMMARY_MOD_CONTEXT modName=%s modPath=%s", getSASGameSummaryQuoted(GC.getModName().getName()).GetCString(), getSASGameSummaryQuoted(GC.getModName().getPathInRoot()).GetCString());
	// <!-- custom: Player/team IDs appear throughout the summary, but live-player counts do not reveal where ordinary civilization slots end and the special Barbarian slots begin. Record the fixed DLL boundaries once at setup so external analysis can interpret every later ID correctly. (GPT-5.6-Sol) -->
	logSASGameSummary("GAME_SUMMARY_SLOT_CONSTANTS MAX_CIV_PLAYERS=%d MAX_PLAYERS=%d BARBARIAN_PLAYER=%d MAX_CIV_TEAMS=%d MAX_TEAMS=%d BARBARIAN_TEAM=%d NO_PLAYER=%d NO_TEAM=%d", MAX_CIV_PLAYERS, MAX_PLAYERS, BARBARIAN_PLAYER, MAX_CIV_TEAMS, MAX_TEAMS, BARBARIAN_TEAM, NO_PLAYER, NO_TEAM);
	if (gGameSummaryLogLevel >= 2) logSASGameSummaryAttitudeLegend();
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (kLoopPlayer.isEverAlive() && !kLoopPlayer.isBarbarian())
			logSASGameSummaryPlayerSetup(eLoopPlayer);
	}
	if (gGameSummaryLogLevel < 2)
		return;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (!kLoopPlayer.isAlive() || kLoopPlayer.isBarbarian())
			continue;
		logSASGameSummaryKnownArea(eLoopPlayer, "setup");
		logSASGameSummaryStartingUnits(eLoopPlayer, "setup");
		int iLoop = 0;
		for (CvCity const* pLoopCity = kLoopPlayer.firstCity(&iLoop); pLoopCity != NULL; pLoopCity = kLoopPlayer.nextCity(&iLoop))
			logSASGameSummaryCityBFC(*pLoopCity, "setup");
	}
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (GET_TEAM(eLoopTeam).isAlive() && !GET_TEAM(eLoopTeam).isBarbarian())
			logSASGameSummaryTeamContacts(eLoopTeam, GC.getGame().getGameTurn(), "setup");
	}
}

static void logSASGameSummaryMapBonusTotals(int iGameTurn)
{
	CvString szBonuses;
	FOR_EACH_ENUM(Bonus)
		appendSASGameSummaryTypeCount(szBonuses, getSASGameSummaryBonusType(eLoopBonus), GC.getMap().getNumBonuses(eLoopBonus));
	logSASGameSummary("GAME_SUMMARY_MAP_BONUSES turn=%d total=%s", iGameTurn, getSASGameSummaryOrDash(szBonuses).GetCString());
}

static void logSASGameSummaryTeamProjects(TeamTypes eTeam, int iGameTurn);

static void logSASGameSummaryBattleBuckets(int iGameTurn)
{
	const int iStartTurn = std::max(0, iGameTurn - getSASGameSummaryTurnInterval() + 1);
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		if (g_aiSASGameSummaryBattleWins[iI] == 0 && g_aiSASGameSummaryBattleLosses[iI] == 0 && g_aiSASGameSummaryCityBattleWins[iI] == 0 && g_aiSASGameSummaryCityBattleLosses[iI] == 0)
			continue;
		logSASGameSummary("GAME_SUMMARY_BATTLE_SUMMARY turn=%d range=%d-%d player=%d wins=%d losses=%d cityPlotWins=%d cityPlotLosses=%d",
				iGameTurn, iStartTurn, iGameTurn, eLoopPlayer, g_aiSASGameSummaryBattleWins[iI], g_aiSASGameSummaryBattleLosses[iI], g_aiSASGameSummaryCityBattleWins[iI], g_aiSASGameSummaryCityBattleLosses[iI]);
		g_aiSASGameSummaryBattleWins[iI] = 0;
		g_aiSASGameSummaryBattleLosses[iI] = 0;
		g_aiSASGameSummaryCityBattleWins[iI] = 0;
		g_aiSASGameSummaryCityBattleLosses[iI] = 0;
	}
}

// <!-- custom: Project completion rows did not show whether a project-based victory had its minimum/full component set or an active launch countdown. Build one compact shared state for periodic progress and the explicit launch action. (GPT-5.6-Sol) -->
static bool getSASGameSummaryVictoryProjectState(TeamTypes eTeam, VictoryTypes eVictory, int& iPartsBuilt, int& iPartsMinimum, int& iPartsMaximum, bool& bMinimumComplete, CvString& szProjectParts)
{
	iPartsBuilt = 0;
	iPartsMinimum = 0;
	iPartsMaximum = 0;
	bMinimumComplete = true;
	szProjectParts.clear();
	CvTeam const& kTeam = GET_TEAM(eTeam);
	FOR_EACH_ENUM(Project)
	{
		CvProjectInfo const& kProject = GC.getInfo(eLoopProject);
		int const iMinimum = kProject.getVictoryMinThreshold(eVictory);
		int const iMaximum = kProject.getVictoryThreshold(eVictory);
		if (iMinimum <= 0 && iMaximum <= 0)
			continue;
		int const iBuilt = kTeam.getProjectCount(eLoopProject);
		iPartsBuilt += iBuilt;
		iPartsMinimum += iMinimum;
		iPartsMaximum += iMaximum;
		if (iBuilt < iMinimum)
			bMinimumComplete = false;
		CvString szItem;
		szItem.Format(szProjectParts.empty() ? "%s:%d/%d/%d" : ",%s:%d/%d/%d", getSASGameSummaryProjectType(eLoopProject), iBuilt, iMinimum, iMaximum);
		szProjectParts += szItem;
	}
	return !szProjectParts.empty();
}

static char const* getSASGameSummaryVictoryType(VictoryTypes eVictory)
{
	return eVictory == NO_VICTORY ? "-" : GC.getInfo(eVictory).getType();
}

typedef std::pair<int, CvCity const*> SASGameSummaryCultureCity;

static bool compareSASGameSummaryCultureCities(SASGameSummaryCultureCity const& kFirst, SASGameSummaryCultureCity const& kSecond)
{
	return kFirst.first > kSecond.first;
}

static CvString getSASGameSummaryCultureVictoryCities(TeamTypes eTeam, int iRequired, int iThreshold, int& iComplete)
{
	std::vector<SASGameSummaryCultureCity> aCities;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		CvPlayer const& kMember = GET_PLAYER((PlayerTypes)iI);
		if (!kMember.isAlive() || kMember.getTeam() != eTeam)
			continue;
		int iLoop = 0;
		for (CvCity const* pCity = kMember.firstCity(&iLoop); pCity != NULL; pCity = kMember.nextCity(&iLoop))
			aCities.push_back(std::make_pair(pCity->getCulture(pCity->getOwner()), pCity));
	}
	std::sort(aCities.begin(), aCities.end(), compareSASGameSummaryCultureCities);
	iComplete = 0;
	for (int iI = 0; iI < (int)aCities.size(); iI++)
	{
		if (aCities[iI].first >= iThreshold)
			iComplete++;
	}
	CvString szCities;
	for (int iI = 0; iI < std::min(iRequired, (int)aCities.size()); iI++)
	{
		CvCity const& kCity = *aCities[iI].second;
		CvString szItem;
		szItem.Format(szCities.empty() ? "P%d:C%d@%d:%d=%d/%d" : ",P%d:C%d@%d:%d=%d/%d", kCity.getOwner(), kCity.getID(), kCity.getX(), kCity.getY(), aCities[iI].first, iThreshold);
		szCities += szItem;
	}
	return getSASGameSummaryOrDash(szCities);
}

static void logSASGameSummaryTeamSnapshot(TeamTypes eTeam, int iGameTurn)
{
	CvGame const& kGame = GC.getGame();
	CvTeam const& kTeam = GET_TEAM(eTeam);
	const int iLandPlots = std::max(1, GC.getMap().getLandPlots());
	const int iGamePopulation = std::max(1, kGame.getTotalPopulation());
	const int iTechs = kTeam.getTechCount();
	const int iLand = kTeam.getTotalLand();
	const int iLandPctX100 = (10000 * iLand) / iLandPlots;
	const int iPopulation = kTeam.getTotalPopulation();
	const int iPopPctX100 = (10000 * iPopulation) / iGamePopulation;
	SASGameSummaryTeamPrevious& kPrevious = g_akSASGameSummaryTeamPrevious[eTeam];
	TeamTypes eMaster = getSASGameSummaryMasterTeam(eTeam);
	logSASGameSummary("GAME_SUMMARY_TEAM turn=%d team=%d members=%s alive=%d deltaValid=%d techs=%d techsDelta=%+d techEraCounts=%s techTrading=%d goldTrading=%d land=%d landDelta=%+d landPctX100=%d landPctX100Delta=%+d pop=%d popDelta=%+d popPctX100=%d popPctX100Delta=%+d wars=%s vassals=%s master=%d",
			iGameTurn, eTeam, getSASGameSummaryTeamMembers(eTeam).GetCString(), kTeam.isAlive(), kPrevious.bValid, iTechs, getSASGameSummaryDelta(kPrevious.bValid, iTechs, kPrevious.iTechs), getSASGameSummaryTechEraCounts(eTeam).GetCString(), kTeam.isTechTrading(), kTeam.isGoldTrading(), iLand, getSASGameSummaryDelta(kPrevious.bValid, iLand, kPrevious.iLand), iLandPctX100, getSASGameSummaryDelta(kPrevious.bValid, iLandPctX100, kPrevious.iLandPctX100), iPopulation, getSASGameSummaryDelta(kPrevious.bValid, iPopulation, kPrevious.iPopulation), iPopPctX100, getSASGameSummaryDelta(kPrevious.bValid, iPopPctX100, kPrevious.iPopPctX100), getSASGameSummaryWarTeams(eTeam).GetCString(), getSASGameSummaryVassalTeams(eTeam).GetCString(), eMaster);
	if (gGameSummaryLogLevel >= 2) logSASGameSummaryTeamContacts(eTeam, iGameTurn, "snapshot");
	kPrevious.bValid = true;
	kPrevious.iTechs = iTechs;
	kPrevious.iLand = iLand;
	kPrevious.iLandPctX100 = iLandPctX100;
	kPrevious.iPopulation = iPopulation;
	kPrevious.iPopPctX100 = iPopPctX100;

	VictoryTypes eScoreVictory = NO_VICTORY;
	VictoryTypes eTimeVictory = NO_VICTORY;
	VictoryTypes eConquestVictory = NO_VICTORY;
	VictoryTypes eCultureVictory = NO_VICTORY;
	VictoryTypes eDiplomaticVictory = NO_VICTORY;
	int iCultureCitiesRequired = 0;
	int iCultureThreshold = 0;
	FOR_EACH_ENUM(Victory)
	{
		if (!kGame.isVictoryValid(eLoopVictory))
			continue;
		CvVictoryInfo const& kVictory = GC.getInfo(eLoopVictory);
		if (kVictory.isTargetScore()) eScoreVictory = eLoopVictory;
		if (kVictory.isEndScore()) eTimeVictory = eLoopVictory;
		if (kVictory.isConquest()) eConquestVictory = eLoopVictory;
		if (kVictory.isDiploVote()) eDiplomaticVictory = eLoopVictory;
		if (kVictory.getCityCulture() != NO_CULTURELEVEL && kVictory.getNumCultureCities() > 0)
		{
			eCultureVictory = eLoopVictory;
			iCultureCitiesRequired = kVictory.getNumCultureCities();
			iCultureThreshold = kGame.getCultureThreshold((CultureLevelTypes)kVictory.getCityCulture());
		}
	}
	CvString szConquestRivals;
	int iConquestRivalCities = 0;
	if (eConquestVictory != NO_VICTORY)
	{
		for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
		{
			TeamTypes const eRival = (TeamTypes)iI;
			CvTeam const& kRival = GET_TEAM(eRival);
			if (eRival == eTeam || !kRival.isAlive() || kRival.isBarbarian() || kRival.isVassal(eTeam) || kRival.getNumCities() <= 0)
				continue;
			appendSASGameSummaryIntList(szConquestRivals, eRival);
			iConquestRivalCities += kRival.getNumCities();
		}
	}
	int iBestRivalScore = -1;
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes const eRival = (TeamTypes)iI;
		if (eRival != eTeam && GET_TEAM(eRival).isAlive() && !GET_TEAM(eRival).isBarbarian())
			iBestRivalScore = std::max(iBestRivalScore, kGame.getTeamScore(eRival));
	}
	int const iTeamScore = kGame.getTeamScore(eTeam);
	int const iTurnsRemaining = (kGame.getMaxTurns() <= 0 ? -1 : std::max(0, kGame.getMaxTurns() - kGame.getElapsedGameTurns()));
	int iCultureCitiesComplete = 0;
	CvString szCultureCities;
	if (eCultureVictory == NO_VICTORY) szCultureCities = "-";
	else szCultureCities = getSASGameSummaryCultureVictoryCities(eTeam, iCultureCitiesRequired, iCultureThreshold, iCultureCitiesComplete);
	// <!-- custom: Domination and Space already have detailed per-victory rows, and diplomatic vote-source rows already contain exact vote thresholds.
	// Add one compact general row per team rather than one new row per missing victory, so Score/Time, Conquest, and Cultural progress become explicit without multiplying snapshot noise.
	// Culture lists only the required number of leading cities. (GPT-5.6-Sol) -->
	logSASGameSummary("GAME_SUMMARY_VICTORY_PROGRESS_GENERAL turn=%d team=%d scoreVictory=%s timeVictory=%s conquestVictory=%s culturalVictory=%s diplomaticVictory=%s teamScore=%d bestRivalScore=%d scoreLead=%+d targetScore=%d turnsRemaining=%d conquestRivals=%s conquestRivalCities=%d cultureCitiesComplete=%d cultureCitiesRequired=%d cultureThreshold=%d cultureCities=%s",
			iGameTurn, eTeam, getSASGameSummaryVictoryType(eScoreVictory), getSASGameSummaryVictoryType(eTimeVictory), getSASGameSummaryVictoryType(eConquestVictory), getSASGameSummaryVictoryType(eCultureVictory), getSASGameSummaryVictoryType(eDiplomaticVictory),
			iTeamScore, iBestRivalScore, iBestRivalScore < 0 ? iTeamScore : iTeamScore - iBestRivalScore, kGame.getTargetScore(), iTurnsRemaining, getSASGameSummaryOrDash(szConquestRivals).GetCString(), iConquestRivalCities,
			iCultureCitiesComplete, iCultureCitiesRequired, iCultureThreshold, szCultureCities.GetCString());

	FOR_EACH_ENUM(Victory)
	{
		if (!kGame.isVictoryValid(eLoopVictory))
			continue;
		const int iLandNeed = kGame.getAdjustedLandPercent(eLoopVictory);
		const int iPopNeed = kGame.getAdjustedPopulationPercent(eLoopVictory);
		int iPartsBuilt = 0;
		int iPartsMinimum = 0;
		int iPartsMaximum = 0;
		bool bMinimumComplete = false;
		CvString szProjectParts;
		bool const bProjectVictory = getSASGameSummaryVictoryProjectState(eTeam, eLoopVictory, iPartsBuilt, iPartsMinimum, iPartsMaximum, bMinimumComplete, szProjectParts);
		if (iLandNeed > 0 || iPopNeed > 0 || bProjectVictory)
		{
			int const iCountdown = kTeam.getVictoryCountdown(eLoopVictory);
			int const iTravelTurns = (bProjectVictory && bMinimumComplete ? kTeam.getVictoryDelay(eLoopVictory) : -1);
			logSASGameSummary("GAME_SUMMARY_VICTORY_PROGRESS turn=%d team=%d victory=%s landPctX100=%d landNeed=%d popPctX100=%d popNeed=%d projectVictory=%d launched=%d countdown=%d arrivalTurn=%d canLaunch=%d launchSuccessPercent=%d travelTurns=%d partsBuilt=%d partsMinimum=%d partsMaximum=%d projectParts=%s",
				iGameTurn, eTeam, GC.getInfo(eLoopVictory).getType(), iLandPctX100, iLandNeed, iPopPctX100, iPopNeed, bProjectVictory, bProjectVictory && iCountdown >= 0, iCountdown, iCountdown < 0 ? -1 : iGameTurn + iCountdown, bProjectVictory && kTeam.canLaunch(eLoopVictory), bProjectVictory ? kTeam.getLaunchSuccessRate(eLoopVictory) : -1, iTravelTurns, iPartsBuilt, iPartsMinimum, iPartsMaximum, bProjectVictory ? szProjectParts.GetCString() : "-");
		}
	}
	if (gGameSummaryLogLevel >= 2) logSASGameSummaryTeamProjects(eTeam, iGameTurn);
}



static CvString getSASGameSummaryCivicList(CvPlayer const& kPlayer)
{
	CvString szList;
	FOR_EACH_ENUM(CivicOption)
	{
		CivicTypes eCivic = kPlayer.getCivics(eLoopCivicOption);
		if (eCivic == NO_CIVIC)
			continue;
		CvString szItem;
		szItem.Format(szList.empty() ? "%s:%s" : ",%s:%s", GC.getInfo(eLoopCivicOption).getType(), getSASGameSummaryCivicType(eCivic));
		szList += szItem;
	}
	return getSASGameSummaryOrDash(szList);
}

static CvString getSASGameSummaryPlayerCityReligions(CvPlayer const& kPlayer)
{
	std::vector<int> aiCounts(GC.getNumReligionInfos(), 0);
	int iLoop = 0;
	for (CvCity const* pLoopCity = kPlayer.firstCity(&iLoop); pLoopCity != NULL; pLoopCity = kPlayer.nextCity(&iLoop))
	{
		FOR_EACH_ENUM(Religion)
		{
			if (pLoopCity->isHasReligion(eLoopReligion))
				aiCounts[eLoopReligion]++;
		}
	}
	CvString szList;
	FOR_EACH_ENUM(Religion)
		appendSASGameSummaryTypeCount(szList, getSASGameSummaryReligionType(eLoopReligion), aiCounts[eLoopReligion]);
	return getSASGameSummaryOrDash(szList);
}

static CvString getSASGameSummaryPlayerCityCorporations(CvPlayer const& kPlayer)
{
	std::vector<int> aiCounts(GC.getNumCorporationInfos(), 0);
	int iLoop = 0;
	for (CvCity const* pLoopCity = kPlayer.firstCity(&iLoop); pLoopCity != NULL; pLoopCity = kPlayer.nextCity(&iLoop))
	{
		FOR_EACH_ENUM(Corporation)
		{
			if (pLoopCity->isHasCorporation(eLoopCorporation))
				aiCounts[eLoopCorporation]++;
		}
	}
	CvString szList;
	FOR_EACH_ENUM(Corporation)
		appendSASGameSummaryTypeCount(szList, getSASGameSummaryCorporationType(eLoopCorporation), aiCounts[eLoopCorporation]);
	return getSASGameSummaryOrDash(szList);
}

// <!-- custom: City health/happiness rows previously combined player-wide modifiers under `extra`, hiding whether a loaded-mod rule caused a demographic change; for example, AdvCiv-SAS's TECH_DEPOPULATION currently applies negative health and happiness.
// Reconstruct all currently defined trait, civic and technology contributions once per player snapshot; preserve any event or other DLL adjustment as OTHER. (GPT-5.6-Sol) -->
static void getSASGameSummaryPlayerExtraSources(CvPlayer const& kPlayer, CvString& szHealthSources, CvString& szHappinessSources)
{
	int iKnownHealth = 0;
	int iKnownHappiness = 0;
	FOR_EACH_ENUM(Trait)
	{
		if (!kPlayer.hasTrait(eLoopTrait))
			continue;
		CvTraitInfo const& kTrait = GC.getInfo(eLoopTrait);
		iKnownHealth += kTrait.getHealth();
		iKnownHappiness += kTrait.getHappiness();
		appendSASGameSummarySignedValue(szHealthSources, kTrait.getType(), kTrait.getHealth());
		appendSASGameSummarySignedValue(szHappinessSources, kTrait.getType(), kTrait.getHappiness());
	}
	FOR_EACH_ENUM(CivicOption)
	{
		CivicTypes const eCivic = kPlayer.getCivics(eLoopCivicOption);
		if (eCivic == NO_CIVIC)
			continue;
		CvCivicInfo const& kCivic = GC.getInfo(eCivic);
		iKnownHealth += kCivic.getExtraHealth();
		iKnownHappiness += kCivic.getExtraHappiness();
		appendSASGameSummarySignedValue(szHealthSources, kCivic.getType(), kCivic.getExtraHealth());
		appendSASGameSummarySignedValue(szHappinessSources, kCivic.getType(), kCivic.getExtraHappiness());
	}
	CvTeam const& kTeam = GET_TEAM(kPlayer.getTeam());
	FOR_EACH_ENUM(Tech)
	{
		if (!kTeam.isHasTech(eLoopTech))
			continue;
		CvTechInfo const& kTech = GC.getInfo(eLoopTech);
		iKnownHealth += kTech.getHealth();
		iKnownHappiness += kTech.getHappiness();
		appendSASGameSummarySignedValue(szHealthSources, kTech.getType(), kTech.getHealth());
		appendSASGameSummarySignedValue(szHappinessSources, kTech.getType(), kTech.getHappiness());
	}
	appendSASGameSummarySignedValue(szHealthSources, "OTHER", kPlayer.getExtraHealth() - iKnownHealth);
	appendSASGameSummarySignedValue(szHappinessSources, "OTHER", kPlayer.getExtraHappiness() - iKnownHappiness);
}

// <!-- custom: Objective victory progress does not show which route currently guides AI strategy. Record the compact 0..4 route stages once per AI snapshot so city production and war choices can be interpreted without enabling detailed BBAI decisions. (GPT-5.6-Sol) -->
static void logSASGameSummaryAIVictoryStages(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayerAI const& kPlayer = GET_PLAYER(ePlayer);
	if (kPlayer.isHuman() && !kPlayer.isHumanDisabled())
		return;
	AIVictoryStage const eStages = kPlayer.AI_getVictoryStageHash();
	int const iCultureStage = getSASCultureVictoryStageLevel(eStages);
	int const iSpaceStage = getSASSpaceVictoryStageLevel(eStages);
	int const iConquestStage = getSASConquestVictoryStageLevel(eStages);
	int const iDominationStage = getSASDominationVictoryStageLevel(eStages);
	int const iDiplomacyStage = getSASDiplomacyVictoryStageLevel(eStages);
	int const iPlayerMaxStage = std::max(std::max(iCultureStage, iSpaceStage), std::max(std::max(iConquestStage, iDominationStage), iDiplomacyStage));
	logSASGameSummary("GAME_SUMMARY_AI_VICTORY_STAGES turn=%d player=%d team=%d playerMaxStage=%d teamMaxStage=%d culture=%d space=%d conquest=%d domination=%d diplomacy=%d",
			iGameTurn, ePlayer, kPlayer.getTeam(), iPlayerMaxStage, getSASTeamMaxVictoryStage(kPlayer.getTeam()), iCultureStage, iSpaceStage, iConquestStage, iDominationStage, iDiplomacyStage);
}

static void logSASGameSummaryPolicies(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvString szExtraHealthSources;
	CvString szExtraHappinessSources;
	getSASGameSummaryPlayerExtraSources(kPlayer, szExtraHealthSources, szExtraHappinessSources);
	logSASGameSummary("GAME_SUMMARY_POLICIES turn=%d player=%d civics=%s stateReligion=%s cityReligions=%s cityCorporations=%s playerExtraHealth=%d playerExtraHappiness=%d extraHealthSources=%s extraHappinessSources=%s",
			iGameTurn, ePlayer, getSASGameSummaryCivicList(kPlayer).GetCString(), getSASGameSummaryReligionType(kPlayer.getStateReligion()), getSASGameSummaryPlayerCityReligions(kPlayer).GetCString(), getSASGameSummaryPlayerCityCorporations(kPlayer).GetCString(),
			kPlayer.getExtraHealth(), kPlayer.getExtraHappiness(), getSASGameSummaryOrDash(szExtraHealthSources).GetCString(), getSASGameSummaryOrDash(szExtraHappinessSources).GetCString());
}

static void logSASGameSummaryEspionage(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvTeam const& kTeam = GET_TEAM(kPlayer.getTeam());
	SASGameSummaryPlayerPrevious& kPrevious = g_akSASGameSummaryPlayerPrevious[ePlayer];
	CvString szWeights;
	CvString szPoints;
	CvString szModifiers;
	// <!-- custom: EP totals alone do not show whether Spies are reaching rivals or remaining idle at home. At periodic level-2 snapshots, summarize foreign deployment, city infiltration, stationary cost-reduction preparation, and current rival targets without logging movement choices. (GPT-5.6-Sol) -->
	CvString szSpyTargets;
	std::vector<int> aiSpiesAgainstPlayer(MAX_PLAYERS, 0);
	int iSpies = 0;
	int iGreatSpies = 0;
	int iSpiesInForeignTerritory = 0;
	int iSpiesInForeignCities = 0;
	int iStationarySpies = 0;
	int iMaxFortifyTurns = 0;
	int iUnitLoop = 0;
	for (CvUnit const* pLoopUnit = kPlayer.firstUnit(&iUnitLoop); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iUnitLoop))
	{
		UnitAITypes const eUnitAI = pLoopUnit->AI_getUnitAIType();
		if (!pLoopUnit->isSpy() && eUnitAI != UNITAI_GREAT_SPY)
			continue;
		iSpies++;
		if (eUnitAI == UNITAI_GREAT_SPY)
			iGreatSpies++;
		if (pLoopUnit->getFortifyTurns() > 0)
		{
			iStationarySpies++;
			iMaxFortifyTurns = std::max(iMaxFortifyTurns, pLoopUnit->getFortifyTurns());
		}
		CvPlot const& kPlot = pLoopUnit->getPlot();
		PlayerTypes const ePlotOwner = kPlot.getOwner();
		if (ePlotOwner != NO_PLAYER && kPlot.getTeam() != kPlayer.getTeam())
		{
			iSpiesInForeignTerritory++;
			if (kPlot.isCity())
				iSpiesInForeignCities++;
			aiSpiesAgainstPlayer[ePlotOwner]++;
		}
	}
	for (int iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (aiSpiesAgainstPlayer[iI] <= 0)
			continue;
		CvString szItem;
		szItem.Format(szSpyTargets.empty() ? "%d:%d" : ",%d:%d", iI, aiSpiesAgainstPlayer[iI]);
		szSpyTargets += szItem;
	}
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam == kPlayer.getTeam() || !GET_TEAM(eLoopTeam).isAlive() || GET_TEAM(eLoopTeam).isBarbarian())
			continue;
		const int iWeight = kPlayer.getEspionageSpendingWeightAgainstTeam(eLoopTeam);
		const int iPoints = kTeam.getEspionagePointsAgainstTeam(eLoopTeam);
		const int iModifier = kTeam.getEspionageModifier(eLoopTeam);
		if (iWeight > 0)
		{
			CvString szItem;
			szItem.Format(szWeights.empty() ? "%d:%d" : ",%d:%d", eLoopTeam, iWeight);
			szWeights += szItem;
		}
		if (iPoints > 0)
		{
			CvString szItem;
			szItem.Format(szPoints.empty() ? "%d:%d" : ",%d:%d", eLoopTeam, iPoints);
			szPoints += szItem;
		}
		if (iModifier != 0)
		{
			CvString szItem;
			szItem.Format(szModifiers.empty() ? "%d:%+d" : ",%d:%+d", eLoopTeam, iModifier);
			szModifiers += szItem;
		}
	}
	const int iEspionageRate = kPlayer.getCommerceRate(COMMERCE_ESPIONAGE);
	const int iEspionagePercent = kPlayer.getCommercePercent(COMMERCE_ESPIONAGE);
	const int iTeamEP = kTeam.getEspionagePointsEver();
	const int iUnspentEP = kTeam.getTotalUnspentEspionage();
	logSASGameSummary("GAME_SUMMARY_ESPIONAGE turn=%d player=%d team=%d espionageRate=%d espionagePercent=%d teamEP=%d unspentEP=%d weights=%s pointsAgainst=%s modifiers=%s spies=%d greatSpies=%d spiesInForeignTerritory=%d spiesInForeignCities=%d stationarySpies=%d maxFortifyTurns=%d spyTargets=%s",
			iGameTurn, ePlayer, kPlayer.getTeam(), iEspionageRate, iEspionagePercent, iTeamEP, iUnspentEP, getSASGameSummaryOrDash(szWeights).GetCString(), getSASGameSummaryOrDash(szPoints).GetCString(), getSASGameSummaryOrDash(szModifiers).GetCString(), iSpies, iGreatSpies, iSpiesInForeignTerritory, iSpiesInForeignCities, iStationarySpies, iMaxFortifyTurns, getSASGameSummaryOrDash(szSpyTargets).GetCString());
	logSASGameSummary("GAME_SUMMARY_ESPIONAGE_DELTAS turn=%d player=%d deltaValid=%d espionageRateDelta=%+d espionagePercentDelta=%+d teamEPDelta=%+d unspentEPDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameSummaryDelta(kPrevious.bValid, iEspionageRate, kPrevious.iEspionageRate), getSASGameSummaryDelta(kPrevious.bValid, iEspionagePercent, kPrevious.iEspionagePercent), getSASGameSummaryDelta(kPrevious.bValid, iTeamEP, kPrevious.iTeamEP), getSASGameSummaryDelta(kPrevious.bValid, iUnspentEP, kPrevious.iUnspentEP));
	kPrevious.iEspionageRate = iEspionageRate;
	kPrevious.iEspionagePercent = iEspionagePercent;
	kPrevious.iTeamEP = iTeamEP;
	kPrevious.iUnspentEP = iUnspentEP;
}

static CvString getSASGameSummaryCommercePercents(CvPlayer const& kPlayer)
{
	CvString szList;
	FOR_EACH_ENUM(Commerce)
		appendSASGameSummaryValue(szList, getSASGameSummaryCommerceType(eLoopCommerce), kPlayer.getCommercePercent(eLoopCommerce));
	return getSASGameSummaryOrDash(szList);
}

static CvString getSASGameSummaryCommerceRates(CvPlayer const& kPlayer)
{
	CvString szList;
	FOR_EACH_ENUM(Commerce)
		appendSASGameSummaryValue(szList, getSASGameSummaryCommerceType(eLoopCommerce), kPlayer.getCommerceRate(eLoopCommerce));
	return getSASGameSummaryOrDash(szList);
}

static CvString getSASGameSummaryCommerceFlexible(CvPlayer const& kPlayer)
{
	CvString szList;
	FOR_EACH_ENUM(Commerce)
		appendSASGameSummaryValue(szList, getSASGameSummaryCommerceType(eLoopCommerce), kPlayer.isCommerceFlexible(eLoopCommerce));
	return getSASGameSummaryOrDash(szList);
}

static void logSASGameSummaryEconomy(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	TechTypes eResearch = kPlayer.getCurrentResearch();
	// <!-- custom: currentResearch=- does not mean that science is lost: CvPlayer::doResearch stores the nominal research rate as overflow until another technology can be selected. Report that rate, accumulated overflow, and whether any technology remains available instead of misleadingly forcing researchRate=0. (GPT-5.6-Sol) -->
	logSASGameSummary("GAME_SUMMARY_ECONOMY turn=%d player=%d gold=%d goldRate=%d totalCommerce=%d sliders=%s commerceTypeRates=%s flexible=%s currentResearch=%s researchRate=%d researchOverflow=%d noResearchAvailable=%d researchTurns=%d",
			iGameTurn, ePlayer, kPlayer.getGold(), kPlayer.calculateGoldRate(), kPlayer.calculateTotalYield(YIELD_COMMERCE), getSASGameSummaryCommercePercents(kPlayer).GetCString(), getSASGameSummaryCommerceRates(kPlayer).GetCString(), getSASGameSummaryCommerceFlexible(kPlayer).GetCString(), getSASGameSummaryTechType(eResearch), kPlayer.calculateResearchRate(eResearch), kPlayer.getOverflowResearch(), kPlayer.isNoResearchAvailable(), eResearch == NO_TECH ? -1 : kPlayer.getResearchTurnsLeft(eResearch, true));
}

static void logSASGameSummaryStatistics(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvPlayerRecord const* pRecord = kPlayer.getPlayerRecord();
	const int iCitiesBuilt = (pRecord == NULL ? 0 : pRecord->getNumCitiesBuilt());
	const int iCitiesRazed = (pRecord == NULL ? 0 : pRecord->getNumCitiesRazed());
	// <!-- custom: Built/razed are persistent CyStatistics player-record values used by the Statistics tab. Acquired/lost and battle totals are game-summary runtime counters from action rows; keeping them local avoids save-format churn while still making conquest swings visible in benchmark logs. (GPT-5.5) -->
	logSASGameSummary("GAME_SUMMARY_STATISTICS turn=%d player=%d currentCities=%d persistentCitiesBuilt=%d persistentCitiesRazed=%d loggedCitiesAcquired=%d loggedCitiesLost=%d loggedCitiesConquered=%d loggedCitiesLostByConquest=%d loggedCitiesTradedIn=%d loggedCitiesTradedOut=%d loggedCityNet=%+d loggedBattleWins=%d loggedBattleLosses=%d loggedCityBattleWins=%d loggedCityBattleLosses=%d loggedBattleNet=%+d",
			iGameTurn, ePlayer, kPlayer.getNumCities(), iCitiesBuilt, iCitiesRazed, g_aiSASGameSummaryCitiesAcquired[ePlayer], g_aiSASGameSummaryCitiesLost[ePlayer], g_aiSASGameSummaryCitiesConquered[ePlayer], g_aiSASGameSummaryCitiesLostByConquest[ePlayer], g_aiSASGameSummaryCitiesTradedIn[ePlayer], g_aiSASGameSummaryCitiesTradedOut[ePlayer], g_aiSASGameSummaryCitiesAcquired[ePlayer] - g_aiSASGameSummaryCitiesLost[ePlayer], g_aiSASGameSummaryTotalBattleWins[ePlayer], g_aiSASGameSummaryTotalBattleLosses[ePlayer], g_aiSASGameSummaryTotalCityBattleWins[ePlayer], g_aiSASGameSummaryTotalCityBattleLosses[ePlayer], g_aiSASGameSummaryTotalBattleWins[ePlayer] - g_aiSASGameSummaryTotalBattleLosses[ePlayer]);
}

static CvString getSASGameSummaryEliminatedPlayers()
{
	CvString szList;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes const eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (kLoopPlayer.isEverAlive() && !kLoopPlayer.isAlive() && !kLoopPlayer.isBarbarian())
			appendSASGameSummaryIntList(szList, eLoopPlayer);
	}
	return getSASGameSummaryOrDash(szList);
}

static PlayerTypes getSASGameSummaryTopScorePlayer()
{
	PlayerTypes eBestPlayer = NO_PLAYER;
	int iBestScore = MIN_INT;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes const eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (!kLoopPlayer.isAlive() || kLoopPlayer.isBarbarian())
			continue;
		int const iScore = kLoopPlayer.calculateScore();
		if (eBestPlayer == NO_PLAYER || iScore > iBestScore)
		{
			eBestPlayer = eLoopPlayer;
			iBestScore = iScore;
		}
	}
	return eBestPlayer;
}

static PlayerTypes getSASGameSummaryTopPowerPlayer()
{
	PlayerTypes eBestPlayer = NO_PLAYER;
	int iBestPower = MIN_INT;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes const eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (!kLoopPlayer.isAlive() || kLoopPlayer.isBarbarian())
			continue;
		int const iPower = kLoopPlayer.getPower();
		if (eBestPlayer == NO_PLAYER || iPower > iBestPower)
		{
			eBestPlayer = eLoopPlayer;
			iBestPower = iPower;
		}
	}
	return eBestPlayer;
}

void logSASGameSummaryRunStatus(char const* szReason)
{
	// <!-- custom: CvGame::getNumHumanPlayers is not const in the Civ4 SDK headers, so this local game reference cannot be const. (GPT-5.5) -->
	CvGame& kGame = GC.getGame();
	PlayerTypes const eTopScorePlayer = getSASGameSummaryTopScorePlayer();
	PlayerTypes const eTopPowerPlayer = getSASGameSummaryTopPowerPlayer();
	// <!-- custom: Compact run-status row gives autoplay/LLM review a single parse-friendly checkpoint for who is alive, eliminated, leading by score, and leading by power. Victory already has its own action row; this row also works for ordinary stopped autoplays where no victory event fires. (GPT-5.5) -->
	logSASGameSummary("GAME_SUMMARY_RUN_STATUS turn=%d reason=%s elapsed=%d year=%d winnerTeam=%d victory=%s playersAlive=%d teamsAlive=%d playersEverAlive=%d humans=%d eliminatedPlayers=%s topScorePlayer=%d topScore=%d topPowerPlayer=%d topPower=%d totalCities=%d totalPopulation=%d",
			kGame.getGameTurn(), szReason == NULL ? "-" : szReason, kGame.getElapsedGameTurns(), kGame.getGameTurnYear(), kGame.getWinner(), kGame.getVictory() == NO_VICTORY ? "-" : GC.getInfo(kGame.getVictory()).getType(), kGame.countCivPlayersAlive(), kGame.countCivTeamsAlive(), kGame.countCivPlayersEverAlive(), kGame.getNumHumanPlayers(), getSASGameSummaryEliminatedPlayers().GetCString(), eTopScorePlayer, eTopScorePlayer == NO_PLAYER ? 0 : GET_PLAYER(eTopScorePlayer).calculateScore(), eTopPowerPlayer, eTopPowerPlayer == NO_PLAYER ? 0 : GET_PLAYER(eTopPowerPlayer).getPower(), kGame.getNumCities(), kGame.getTotalPopulation());
}

static void logSASGameSummaryDemographics(PlayerTypes ePlayer, int iGameTurn)
{
	CvGame const& kGame = GC.getGame();
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	SASGameSummaryPlayerPrevious& kPrevious = g_akSASGameSummaryPlayerPrevious[ePlayer];
	const int iScore = kPlayer.calculateScore();
	const int iPopulation = kPlayer.getTotalPopulation();
	const int iLand = kPlayer.getTotalLand();
	const int iFood = kPlayer.calculateTotalYield(YIELD_FOOD);
	const int iProduction = kPlayer.calculateTotalYield(YIELD_PRODUCTION);
	const int iCommerce = kPlayer.calculateTotalYield(YIELD_COMMERCE);
	const int iResearch = kPlayer.getCommerceRate(COMMERCE_RESEARCH);
	const int iCulture = kPlayer.getCommerceRate(COMMERCE_CULTURE);
	const int iEspionage = kPlayer.getCommerceRate(COMMERCE_ESPIONAGE);
	const int iGoldRate = kPlayer.calculateGoldRate();
	const int iPower = kPlayer.getPower();
	logSASGameSummary("GAME_SUMMARY_DEMOGRAPHICS turn=%d player=%d rank=%d score=%d population=%d land=%d food=%d production=%d commerce=%d research=%d culture=%d espionage=%d goldRate=%d power=%d",
			iGameTurn, ePlayer, kGame.getPlayerRank(ePlayer) + 1, iScore, iPopulation, iLand, iFood, iProduction, iCommerce, iResearch, iCulture, iEspionage, iGoldRate, iPower);
	logSASGameSummary("GAME_SUMMARY_DEMOGRAPHICS_DELTAS turn=%d player=%d deltaValid=%d scoreDelta=%+d populationDelta=%+d landDelta=%+d foodDelta=%+d productionDelta=%+d commerceDelta=%+d researchDelta=%+d cultureDelta=%+d espionageDelta=%+d goldRateDelta=%+d powerDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameSummaryDelta(kPrevious.bValid, iScore, kPrevious.iDemoScore), getSASGameSummaryDelta(kPrevious.bValid, iPopulation, kPrevious.iDemoPopulation), getSASGameSummaryDelta(kPrevious.bValid, iLand, kPrevious.iDemoLand), getSASGameSummaryDelta(kPrevious.bValid, iFood, kPrevious.iDemoFood), getSASGameSummaryDelta(kPrevious.bValid, iProduction, kPrevious.iDemoProduction), getSASGameSummaryDelta(kPrevious.bValid, iCommerce, kPrevious.iDemoCommerce), getSASGameSummaryDelta(kPrevious.bValid, iResearch, kPrevious.iDemoResearch), getSASGameSummaryDelta(kPrevious.bValid, iCulture, kPrevious.iDemoCulture), getSASGameSummaryDelta(kPrevious.bValid, iEspionage, kPrevious.iDemoEspionage), getSASGameSummaryDelta(kPrevious.bValid, iGoldRate, kPrevious.iDemoGoldRate), getSASGameSummaryDelta(kPrevious.bValid, iPower, kPrevious.iDemoPower));
	kPrevious.iDemoScore = iScore;
	kPrevious.iDemoPopulation = iPopulation;
	kPrevious.iDemoLand = iLand;
	kPrevious.iDemoFood = iFood;
	kPrevious.iDemoProduction = iProduction;
	kPrevious.iDemoCommerce = iCommerce;
	kPrevious.iDemoResearch = iResearch;
	kPrevious.iDemoCulture = iCulture;
	kPrevious.iDemoEspionage = iEspionage;
	kPrevious.iDemoGoldRate = iGoldRate;
	kPrevious.iDemoPower = iPower;
}

static void logSASGameSummaryAttitudes(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayerAI const& kPlayer = GET_PLAYER(ePlayer);
	CvString szToward;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		if (eLoopPlayer == ePlayer || !GET_PLAYER(eLoopPlayer).isAlive() || GET_PLAYER(eLoopPlayer).isBarbarian())
			continue;
		if (!GET_TEAM(kPlayer.getTeam()).isHasMet(GET_PLAYER(eLoopPlayer).getTeam()))
			continue;
		const int iValue = kPlayer.AI_getAttitudeVal(eLoopPlayer);
		CvString szItem;
		szItem.Format(szToward.empty() ? "%d:%+d" : ",%d:%+d", eLoopPlayer, iValue);
		szToward += szItem;
	}
	logSASGameSummary("GAME_SUMMARY_ATTITUDES turn=%d player=%d towardValues=%s", iGameTurn, ePlayer, getSASGameSummaryOrDash(szToward).GetCString());
}

static void logSASGameSummaryDiplomaticMemories(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayerAI const& kPlayer = GET_PLAYER(ePlayer);
	CvTeam const& kTeam = GET_TEAM(kPlayer.getTeam());
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes const eTowardPlayer = (PlayerTypes)iI;
		if (eTowardPlayer == ePlayer || !GET_PLAYER(eTowardPlayer).isAlive() || GET_PLAYER(eTowardPlayer).isBarbarian() || !kTeam.isHasMet(GET_PLAYER(eTowardPlayer).getTeam()))
			continue;
		CvString szMemories;
		int iMemoryAttitude = 0;
		for (int iJ = 0; iJ < NUM_MEMORY_TYPES; iJ++)
		{
			MemoryTypes const eMemory = (MemoryTypes)iJ;
			int const iCount = kPlayer.AI_getMemoryCount(eTowardPlayer, eMemory);
			if (iCount <= 0)
				continue;
			int const iAttitude = kPlayer.AI_getMemoryAttitude(eTowardPlayer, eMemory);
			iMemoryAttitude += iAttitude;
			CvString szItem;
			szItem.Format(szMemories.empty() ? "%s=%d/%+d" : ",%s=%d/%+d", getSASMemoryType(eMemory), iCount, iAttitude);
			szMemories += szItem;
		}
		if (!szMemories.empty())
		{
			// <!-- custom: Level-3 memory rows explain why the existing attitude value changed. Each item is MEMORY_TYPE=count/attitudeContribution; periodic snapshots avoid logging every routine memory decay. (GPT-5.6-Sol) -->
			logSASGameSummary("GAME_SUMMARY_DIPLO_MEMORIES turn=%d player=%d toward=%d attitudeValue=%+d memoryAttitude=%+d memories=%s", iGameTurn, ePlayer, eTowardPlayer, kPlayer.AI_getAttitudeVal(eTowardPlayer), iMemoryAttitude, szMemories.GetCString());
		}
	}
}

static void logSASGameSummaryDiploStatus(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayerAI const& kPlayer = GET_PLAYER(ePlayer);
	CvTeam const& kTeam = GET_TEAM(kPlayer.getTeam());
	const TeamTypes eWorstEnemy = kTeam.AI().AI_getWorstEnemy();
	CvString szWorstEnemyPlayers;
	CvString szWorstEnemyOfTeams;
	CvString szAtWar;
	CvString szOpenBorders;
	CvString szDefensivePacts;
	CvString szForcePeace;
	CvString szCanContact;
	CvString szCanContactWilling;
	CvString szWontTalkTo;
	CvString szWontTalkFrom;
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam == kPlayer.getTeam() || !GET_TEAM(eLoopTeam).isAlive() || GET_TEAM(eLoopTeam).isBarbarian())
			continue;
		if (!kTeam.isHasMet(eLoopTeam))
			continue;
		if (kTeam.isAtWar(eLoopTeam))
			appendSASGameSummaryIntList(szAtWar, eLoopTeam);
		if (kTeam.isOpenBorders(eLoopTeam))
			appendSASGameSummaryIntList(szOpenBorders, eLoopTeam);
		if (kTeam.isDefensivePact(eLoopTeam))
			appendSASGameSummaryIntList(szDefensivePacts, eLoopTeam);
		if (kTeam.isForcePeace(eLoopTeam))
			appendSASGameSummaryIntList(szForcePeace, eLoopTeam);
		if (GET_TEAM(eLoopTeam).AI().AI_getWorstEnemy() == kPlayer.getTeam())
			appendSASGameSummaryIntList(szWorstEnemyOfTeams, eLoopTeam);
	}
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		if (eLoopPlayer == ePlayer || !GET_PLAYER(eLoopPlayer).isAlive() || GET_PLAYER(eLoopPlayer).isBarbarian())
			continue;
		if (!kTeam.isHasMet(GET_PLAYER(eLoopPlayer).getTeam()))
			continue;
		if (GET_PLAYER(eLoopPlayer).getTeam() == eWorstEnemy)
			appendSASGameSummaryIntList(szWorstEnemyPlayers, eLoopPlayer);
		if (kPlayer.canContact(eLoopPlayer, false))
			appendSASGameSummaryIntList(szCanContact, eLoopPlayer);
		if (kPlayer.canContact(eLoopPlayer, true))
			appendSASGameSummaryIntList(szCanContactWilling, eLoopPlayer);
		if (!kPlayer.AI_isWillingToTalk(eLoopPlayer))
			appendSASGameSummaryIntList(szWontTalkTo, eLoopPlayer);
		if (!GET_PLAYER(eLoopPlayer).AI_isWillingToTalk(ePlayer))
			appendSASGameSummaryIntList(szWontTalkFrom, eLoopPlayer);
	}
	logSASGameSummary("GAME_SUMMARY_DIPLO_STATUS turn=%d player=%d team=%d worstEnemyTeam=%d worstEnemyPlayers=%s worstEnemyOfTeams=%s atWar=%s openBorders=%s defensivePacts=%s forcePeace=%s canContact=%s canContactWilling=%s wontTalkTo=%s wontTalkFrom=%s",
			iGameTurn, ePlayer, kPlayer.getTeam(), eWorstEnemy, getSASGameSummaryOrDash(szWorstEnemyPlayers).GetCString(), getSASGameSummaryOrDash(szWorstEnemyOfTeams).GetCString(), getSASGameSummaryOrDash(szAtWar).GetCString(), getSASGameSummaryOrDash(szOpenBorders).GetCString(), getSASGameSummaryOrDash(szDefensivePacts).GetCString(), getSASGameSummaryOrDash(szForcePeace).GetCString(), getSASGameSummaryOrDash(szCanContact).GetCString(), getSASGameSummaryOrDash(szCanContactWilling).GetCString(), getSASGameSummaryOrDash(szWontTalkTo).GetCString(), getSASGameSummaryOrDash(szWontTalkFrom).GetCString());
}

static void logSASGameSummaryEnvironment(int iGameTurn)
{
	CvMap const& kMap = GC.getMap();
	std::vector<int> aiFeatures(GC.getNumFeatureInfos(), 0);
	std::vector<int> aiNegativeHealthFeatures(GC.getNumFeatureInfos(), 0);
	int iOwnedLand = 0;
	int iUnownedLand = 0;
	for (int iI = 0; iI < kMap.numPlots(); iI++)
	{
		CvPlot const& kPlot = kMap.getPlotByIndex(iI);
		if (!kPlot.isWater())
		{
			if (kPlot.isOwned())
				iOwnedLand++;
			else iUnownedLand++;
		}
		FeatureTypes eFeature = kPlot.getFeatureType();
		if (eFeature != NO_FEATURE)
		{
			aiFeatures[eFeature]++;
			if (GC.getInfo(eFeature).getHealthPercent() < 0)
				aiNegativeHealthFeatures[eFeature]++;
		}
	}
	CvString szFeatures;
	CvString szNegativeHealthFeatures;
	FOR_EACH_ENUM(Feature)
	{
		appendSASGameSummaryTypeCount(szFeatures, getSASGameSummaryFeatureType(eLoopFeature), aiFeatures[eLoopFeature]);
		appendSASGameSummaryTypeCount(szNegativeHealthFeatures, getSASGameSummaryFeatureType(eLoopFeature), aiNegativeHealthFeatures[eLoopFeature]);
	}
	const int iGlobalWarmingIndex = GC.getGame().getGlobalWarmingIndex();
	const int iGlobalWarmingChances = GC.getGame().getGlobalWarmingChances();
	logSASGameSummary("GAME_SUMMARY_ENVIRONMENT turn=%d globalWarmingIndex=%d globalWarmingChances=%d land=%d water=%d ownedLand=%d unownedLand=%d negativeHealthFeatures=%s features=%s",
			iGameTurn, iGlobalWarmingIndex, iGlobalWarmingChances, kMap.getLandPlots(), kMap.getWaterPlots(), iOwnedLand, iUnownedLand, getSASGameSummaryOrDash(szNegativeHealthFeatures).GetCString(), getSASGameSummaryOrDash(szFeatures).GetCString());
	logSASGameSummary("GAME_SUMMARY_ENVIRONMENT_DELTAS turn=%d deltaValid=%d globalWarmingIndexDelta=%+d globalWarmingChancesDelta=%+d ownedLandDelta=%+d unownedLandDelta=%+d",
			iGameTurn, g_kSASGameSummaryGlobalPrevious.bValid, getSASGameSummaryDelta(g_kSASGameSummaryGlobalPrevious.bValid, iGlobalWarmingIndex, g_kSASGameSummaryGlobalPrevious.iGlobalWarmingIndex), getSASGameSummaryDelta(g_kSASGameSummaryGlobalPrevious.bValid, iGlobalWarmingChances, g_kSASGameSummaryGlobalPrevious.iGlobalWarmingChances), getSASGameSummaryDelta(g_kSASGameSummaryGlobalPrevious.bValid, iOwnedLand, g_kSASGameSummaryGlobalPrevious.iOwnedLand), getSASGameSummaryDelta(g_kSASGameSummaryGlobalPrevious.bValid, iUnownedLand, g_kSASGameSummaryGlobalPrevious.iUnownedLand));
	g_kSASGameSummaryGlobalPrevious.bValid = true;
	g_kSASGameSummaryGlobalPrevious.iGlobalWarmingIndex = iGlobalWarmingIndex;
	g_kSASGameSummaryGlobalPrevious.iGlobalWarmingChances = iGlobalWarmingChances;
	g_kSASGameSummaryGlobalPrevious.iOwnedLand = iOwnedLand;
	g_kSASGameSummaryGlobalPrevious.iUnownedLand = iUnownedLand;
}

static void logSASGameSummaryVoteSources(int iGameTurn)
{
	CvGame const& kGame = GC.getGame();
	FOR_EACH_ENUM(VoteSource)
	{
		CvCity const* pSourceCity = kGame.getVoteSourceCity(eLoopVoteSource, NO_TEAM, true);
		ReligionTypes eReligion = kGame.getVoteSourceReligion(eLoopVoteSource);
		TeamTypes eSecretary = kGame.getSecretaryGeneral(eLoopVoteSource);
		CvString szVotingTeams;
		CvString szFullTeams;
		CvString szVotes;
		for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
		{
			TeamTypes eLoopTeam = (TeamTypes)iI;
			CvTeam const& kLoopTeam = GET_TEAM(eLoopTeam);
			if (!kLoopTeam.isAlive() || kLoopTeam.isBarbarian())
				continue;
			if (kLoopTeam.isVotingMember(eLoopVoteSource))
				appendSASGameSummaryIntList(szVotingTeams, eLoopTeam);
			if (kLoopTeam.isFullMember(eLoopVoteSource))
				appendSASGameSummaryIntList(szFullTeams, eLoopTeam);
			const int iVotes = kLoopTeam.getVotes(NO_VOTE, eLoopVoteSource);
			if (iVotes > 0)
			{
				CvString szItem;
				szItem.Format(szVotes.empty() ? "%d:%d" : ",%d:%d", eLoopTeam, iVotes);
				szVotes += szItem;
			}
		}
		CvString szVictoryVotes;
		FOR_EACH_ENUM(Vote)
		{
			if (!GC.getInfo(eLoopVote).isVoteSourceType(eLoopVoteSource) || !GC.getInfo(eLoopVote).isVictory())
				continue;
			CvString szItem;
			szItem.Format(szVictoryVotes.empty() ? "%s:required=%d,possible=%d" : ",%s:required=%d,possible=%d", getSASGameSummaryVoteType(eLoopVote), kGame.getVoteRequired(eLoopVote, eLoopVoteSource), kGame.countPossibleVote(eLoopVote, eLoopVoteSource));
			szVictoryVotes += szItem;
		}
		if (pSourceCity == NULL && eReligion == NO_RELIGION && eSecretary == NO_TEAM && szVotingTeams.empty() && szVictoryVotes.empty())
			continue;
		logSASGameSummary("GAME_SUMMARY_DIPLO_VOTE_SOURCE turn=%d source=%s secretaryTeam=%d secretaryTimer=%d voteTimer=%d religion=%s sourceOwner=%d sourceCityId=%d sourceCity=%S sourceX=%d sourceY=%d votingTeams=%s fullTeams=%s votes=%s victoryVotes=%s",
				iGameTurn, getSASGameSummaryVoteSourceType(eLoopVoteSource), eSecretary, kGame.getSecretaryGeneralTimer(eLoopVoteSource), kGame.getVoteTimer(eLoopVoteSource), getSASGameSummaryReligionType(eReligion), pSourceCity == NULL ? -1 : pSourceCity->getOwner(), pSourceCity == NULL ? -1 : pSourceCity->getID(), getSASGameSummaryQuotedCityName(pSourceCity).GetCString(), pSourceCity == NULL ? -1 : pSourceCity->getX(), pSourceCity == NULL ? -1 : pSourceCity->getY(), getSASGameSummaryOrDash(szVotingTeams).GetCString(), getSASGameSummaryOrDash(szFullTeams).GetCString(), getSASGameSummaryOrDash(szVotes).GetCString(), getSASGameSummaryOrDash(szVictoryVotes).GetCString());
	}
}

static void logSASGameSummaryTeamProjects(TeamTypes eTeam, int iGameTurn)
{
	CvString szProjects;
	FOR_EACH_ENUM(Project)
		appendSASGameSummaryTypeCount(szProjects, getSASGameSummaryProjectType(eLoopProject), GET_TEAM(eTeam).getProjectCount(eLoopProject));
	if (!szProjects.empty())
		logSASGameSummary("GAME_SUMMARY_TEAM_PROJECTS turn=%d team=%d projects=%s", iGameTurn, eTeam, szProjects.GetCString());
}

static void logSASGameSummaryPlayerBonuses(PlayerTypes ePlayer, int iGameTurn, SASGameSummaryPlayerPrevious const& kPrevious)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvString szAvailable;
	CvString szTradeable;
	CvString szImports;
	CvString szExports;
	int iBonusTypes = 0;
	int iBonusInstances = 0;
	int iBonusImports = 0;
	int iBonusExports = 0;
	FOR_EACH_ENUM(Bonus)
	{
		const int iAvailable = kPlayer.getNumAvailableBonuses(eLoopBonus);
		const int iTradeable = kPlayer.getNumTradeableBonuses(eLoopBonus);
		const int iImport = kPlayer.getBonusImport(eLoopBonus);
		const int iExport = kPlayer.getBonusExport(eLoopBonus);
		if (iAvailable > 0)
		{
			iBonusTypes++;
			iBonusInstances += iAvailable;
			appendSASGameSummaryTypeCount(szAvailable, getSASGameSummaryBonusType(eLoopBonus), iAvailable);
		}
		appendSASGameSummaryTypeCount(szTradeable, getSASGameSummaryBonusType(eLoopBonus), iTradeable);
		if (iImport > 0)
		{
			iBonusImports += iImport;
			appendSASGameSummaryTypeCount(szImports, getSASGameSummaryBonusType(eLoopBonus), iImport);
		}
		if (iExport > 0)
		{
			iBonusExports += iExport;
			appendSASGameSummaryTypeCount(szExports, getSASGameSummaryBonusType(eLoopBonus), iExport);
		}
	}
	logSASGameSummary("GAME_SUMMARY_BONUSES turn=%d player=%d deltaValid=%d bonusTypes=%d bonusTypesDelta=%+d bonusInstances=%d bonusInstancesDelta=%+d imports=%d importsDelta=%+d exports=%d exportsDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, iBonusTypes, getSASGameSummaryDelta(kPrevious.bValid, iBonusTypes, kPrevious.iBonusTypes), iBonusInstances, getSASGameSummaryDelta(kPrevious.bValid, iBonusInstances, kPrevious.iBonusInstances), iBonusImports, getSASGameSummaryDelta(kPrevious.bValid, iBonusImports, kPrevious.iBonusImports), iBonusExports, getSASGameSummaryDelta(kPrevious.bValid, iBonusExports, kPrevious.iBonusExports));
	logSASGameSummary("GAME_SUMMARY_BONUSES_AVAILABLE turn=%d player=%d available=%s", iGameTurn, ePlayer, getSASGameSummaryOrDash(szAvailable).GetCString());
	logSASGameSummary("GAME_SUMMARY_BONUSES_TRADEABLE turn=%d player=%d tradeable=%s", iGameTurn, ePlayer, getSASGameSummaryOrDash(szTradeable).GetCString());
	logSASGameSummary("GAME_SUMMARY_BONUSES_IMPORT_EXPORT turn=%d player=%d imported=%s exported=%s", iGameTurn, ePlayer, getSASGameSummaryOrDash(szImports).GetCString(), getSASGameSummaryOrDash(szExports).GetCString());
}

static bool isSASGameSummaryMilitaryUnit(CvUnit const& kUnit)
{
	return kUnit.canDefend(kUnit.plot()) || kUnit.baseCombatStr() > 0 || kUnit.airBaseCombatStr() > 0;
}

static bool isSASGameSummaryWorkerUnit(CvUnit const& kUnit)
{
	UnitAITypes eUnitAI = kUnit.AI_getUnitAIType();
	return eUnitAI == UNITAI_WORKER || eUnitAI == UNITAI_WORKER_SEA || kUnit.workRate(true) > 0;
}

static bool isSASGameSummarySettlerUnit(CvUnit const& kUnit)
{
	return kUnit.AI_getUnitAIType() == UNITAI_SETTLE || kUnit.isFound();
}

static MissionTypes getSASGameSummaryUnitMissionType(CvUnit const& kUnit)
{
	CvSelectionGroup const* pGroup = kUnit.getGroup();
	return pGroup == NULL ? NO_MISSION : pGroup->getMissionType(0);
}

static int getSASGameSummaryBuildTurnsLeft(CvUnit const& kUnit, BuildTypes eBuild)
{
	return eBuild == NO_BUILD ? -1 : kUnit.getPlot().getBuildTurnsLeft(eBuild, kUnit.getOwner(), 0, 0);
}

static bool isSASGameSummaryUnitGuarded(CvUnit const& kUnit)
{
	CvPlot const* pPlot = kUnit.plot();
	return pPlot != NULL && pPlot->getNumDefenders(kUnit.getOwner()) > 0;
}

static bool isSASGameSummaryUnitThreatened(CvUnit const& kUnit)
{
	CvPlot const* pPlot = kUnit.plot();
	return pPlot != NULL && pPlot->isVisibleEnemyUnit(kUnit.getOwner());
}

static void logSASGameSummaryUnitPosture(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	TeamTypes eTeam = kPlayer.getTeam();
	SASGameSummaryPlayerPrevious& kPrevious = g_akSASGameSummaryPlayerPrevious[ePlayer];
	int iTotal = 0;
	int iMilitary = 0;
	int iLandMilitary = 0;
	int iSeaMilitary = 0;
	int iAirMilitary = 0;
	int iWorkers = 0;
	int iSettlers = 0;
	int iRecon = 0;
	int iCityDefenders = 0;
	int iFieldArmy = 0;
	int iOwnTerritory = 0;
	int iEnemyTerritory = 0;
	int iNeutralTerritory = 0;
	int iUnitsInCities = 0;
	int iEnemyUnitsInTerritory = 0;
	int iTotalExperience = 0;
	int iMaxExperience = 0;
	int iPromotionReady = 0;
	int iLevel2Plus = 0;
	int iLevel4Plus = 0;
	int iLevel6Plus = 0;
	int iPromotionInstances = 0;
	std::vector<int> aiUnitTypes(GC.getNumUnitInfos(), 0);
	std::vector<int> aiUnitAI(NUM_UNITAI_TYPES, 0);
	std::vector<int> aiUnitCombat(GC.getNumUnitCombatInfos(), 0);
	std::vector<int> aiPromotions(gGameSummaryLogLevel >= 3 ? GC.getNumPromotionInfos() : 0, 0);
	int iLoop = 0;
	for (CvUnit const* pLoopUnit = kPlayer.firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iLoop))
	{
		iTotal++;
		if (pLoopUnit->getUnitType() != NO_UNIT)
			aiUnitTypes[pLoopUnit->getUnitType()]++;
		const int iExperience = pLoopUnit->getExperience();
		iTotalExperience += iExperience;
		iMaxExperience = std::max(iMaxExperience, iExperience);
		if (pLoopUnit->isPromotionReady())
			iPromotionReady++;
		if (pLoopUnit->getLevel() >= 2)
			iLevel2Plus++;
		if (pLoopUnit->getLevel() >= 4)
			iLevel4Plus++;
		if (pLoopUnit->getLevel() >= 6)
			iLevel6Plus++;
		CvPlot const* pPlot = pLoopUnit->plot();
		const bool bMilitary = isSASGameSummaryMilitaryUnit(*pLoopUnit);
		if (bMilitary)
		{
			iMilitary++;
			if (pLoopUnit->getDomainType() == DOMAIN_SEA)
				iSeaMilitary++;
			else if (pLoopUnit->getDomainType() == DOMAIN_AIR)
				iAirMilitary++;
			else iLandMilitary++;
			if (pPlot != NULL && pPlot->isCity() && pLoopUnit->canDefend(pPlot))
				iCityDefenders++;
			else iFieldArmy++;
		}
		UnitAITypes eUnitAI = pLoopUnit->AI_getUnitAIType();
		if (eUnitAI >= 0 && eUnitAI < NUM_UNITAI_TYPES)
			aiUnitAI[eUnitAI]++;
		UnitCombatTypes eUnitCombat = pLoopUnit->getUnitCombatType();
		if (eUnitCombat != NO_UNITCOMBAT)
			aiUnitCombat[eUnitCombat]++;
		if (gGameSummaryLogLevel >= 3)
		{
			FOR_EACH_ENUM(Promotion)
			{
				if (pLoopUnit->isHasPromotion(eLoopPromotion))
				{
					aiPromotions[eLoopPromotion]++;
					iPromotionInstances++;
				}
			}
		}
		if (isSASGameSummaryWorkerUnit(*pLoopUnit))
			iWorkers++;
		if (isSASGameSummarySettlerUnit(*pLoopUnit))
			iSettlers++;
		if (eUnitAI == UNITAI_EXPLORE || eUnitAI == UNITAI_EXPLORE_SEA)
			iRecon++;
		if (pPlot != NULL)
		{
			if (pPlot->isCity())
				iUnitsInCities++;
			if (pPlot->getOwner() == ePlayer)
				iOwnTerritory++;
			else if (pPlot->getTeam() != NO_TEAM && GET_TEAM(eTeam).isAtWar(pPlot->getTeam()))
				iEnemyTerritory++;
			else iNeutralTerritory++;
		}
	}
	for (int iPlayer = 0; iPlayer < MAX_PLAYERS; iPlayer++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iPlayer;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (!kLoopPlayer.isAlive() || kLoopPlayer.getTeam() == eTeam || !GET_TEAM(eTeam).isAtWar(kLoopPlayer.getTeam()))
			continue;
		int iEnemyLoop = 0;
		for (CvUnit const* pLoopUnit = kLoopPlayer.firstUnit(&iEnemyLoop); pLoopUnit != NULL; pLoopUnit = kLoopPlayer.nextUnit(&iEnemyLoop))
		{
			CvPlot const* pPlot = pLoopUnit->plot();
			if (pPlot != NULL && pPlot->getOwner() == ePlayer)
				iEnemyUnitsInTerritory++;
		}
	}
	CvString szUnitTypes;
	CvString szUnitAI;
	CvString szUnitCombat;
	CvString szPromotions;
	// <!-- custom: UnitAI and combat class are useful but too coarse for game-summary review: a Galley and Galleon can share naval transport roles, and a Camel Archer and Dragoon can sit in similar mounted/combat buckets despite very different strength and era impact. Include actual unit-type counts so LLM/autoplay review can see army and navy quality without per-unit spam. (GPT-5.5) -->
	for (int iI = 0; iI < GC.getNumUnitInfos(); iI++)
		appendSASGameSummaryTypeCount(szUnitTypes, getSASGameSummaryUnitType((UnitTypes)iI), aiUnitTypes[iI]);
	for (int iI = 0; iI < NUM_UNITAI_TYPES; iI++)
		appendSASGameSummaryTypeCount(szUnitAI, getSASGameSummaryUnitAIType((UnitAITypes)iI), aiUnitAI[iI]);
	for (int iI = 0; iI < GC.getNumUnitCombatInfos(); iI++)
		appendSASGameSummaryTypeCount(szUnitCombat, getSASGameSummaryUnitCombatType((UnitCombatTypes)iI), aiUnitCombat[iI]);
	if (gGameSummaryLogLevel >= 3)
	{
		FOR_EACH_ENUM(Promotion)
			appendSASGameSummaryTypeCount(szPromotions, getSASGameSummaryPromotionType(eLoopPromotion), aiPromotions[eLoopPromotion]);
	}
	logSASGameSummary("GAME_SUMMARY_UNIT_POSTURE turn=%d player=%d total=%d military=%d landMilitary=%d seaMilitary=%d airMilitary=%d workers=%d settlers=%d recon=%d cityDefenders=%d fieldArmy=%d ownTerritory=%d enemyTerritory=%d neutralTerritory=%d unitsInCities=%d enemyUnitsInTerritory=%d totalXP=%d avgXpX100=%d maxXP=%d promotionReady=%d level2Plus=%d level4Plus=%d level6Plus=%d promotionInstances=%d",
			iGameTurn, ePlayer, iTotal, iMilitary, iLandMilitary, iSeaMilitary, iAirMilitary, iWorkers, iSettlers, iRecon, iCityDefenders, iFieldArmy, iOwnTerritory, iEnemyTerritory, iNeutralTerritory, iUnitsInCities, iEnemyUnitsInTerritory, iTotalExperience, iTotal == 0 ? 0 : (100 * iTotalExperience) / iTotal, iMaxExperience, iPromotionReady, iLevel2Plus, iLevel4Plus, iLevel6Plus, iPromotionInstances);
	logSASGameSummary("GAME_SUMMARY_UNIT_POSTURE_DELTAS turn=%d player=%d deltaValid=%d totalDelta=%+d militaryDelta=%+d workersDelta=%+d settlersDelta=%+d fieldArmyDelta=%+d cityDefendersDelta=%+d enemyUnitsInTerritoryDelta=%+d totalXPDelta=%+d promotionReadyDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameSummaryDelta(kPrevious.bValid, iTotal, kPrevious.iUnitTotal), getSASGameSummaryDelta(kPrevious.bValid, iMilitary, kPrevious.iUnitMilitary), getSASGameSummaryDelta(kPrevious.bValid, iWorkers, kPrevious.iUnitWorkers), getSASGameSummaryDelta(kPrevious.bValid, iSettlers, kPrevious.iUnitSettlers), getSASGameSummaryDelta(kPrevious.bValid, iFieldArmy, kPrevious.iUnitFieldArmy), getSASGameSummaryDelta(kPrevious.bValid, iCityDefenders, kPrevious.iUnitCityDefenders), getSASGameSummaryDelta(kPrevious.bValid, iEnemyUnitsInTerritory, kPrevious.iUnitEnemyUnitsInTerritory), getSASGameSummaryDelta(kPrevious.bValid, iTotalExperience, kPrevious.iUnitTotalExperience), getSASGameSummaryDelta(kPrevious.bValid, iPromotionReady, kPrevious.iUnitPromotionReady));
	kPrevious.iUnitTotal = iTotal;
	kPrevious.iUnitMilitary = iMilitary;
	kPrevious.iUnitWorkers = iWorkers;
	kPrevious.iUnitSettlers = iSettlers;
	kPrevious.iUnitFieldArmy = iFieldArmy;
	kPrevious.iUnitCityDefenders = iCityDefenders;
	kPrevious.iUnitEnemyUnitsInTerritory = iEnemyUnitsInTerritory;
	kPrevious.iUnitTotalExperience = iTotalExperience;
	kPrevious.iUnitPromotionReady = iPromotionReady;
	logSASGameSummary("GAME_SUMMARY_UNIT_COMPOSITION turn=%d player=%d unitTypes=%s unitAI=%s unitCombat=%s", iGameTurn, ePlayer, getSASGameSummaryOrDash(szUnitTypes).GetCString(), getSASGameSummaryOrDash(szUnitAI).GetCString(), getSASGameSummaryOrDash(szUnitCombat).GetCString());
	if (gGameSummaryLogLevel >= 3) logSASGameSummary("GAME_SUMMARY_UNIT_PROMOTIONS turn=%d player=%d promotions=%s", iGameTurn, ePlayer, getSASGameSummaryOrDash(szPromotions).GetCString());
}

static void logSASGameSummaryWorkers(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	TeamTypes eTeam = kPlayer.getTeam();
	SASGameSummaryPlayerPrevious& kPrevious = g_akSASGameSummaryPlayerPrevious[ePlayer];
	int iWorkers = 0;
	int iSeaWorkers = 0;
	int iIdle = 0;
	int iBuilding = 0;
	int iBuildingImprovement = 0;
	int iBuildingRoute = 0;
	int iMoving = 0;
	int iWaiting = 0;
	int iOwnTerritory = 0;
	int iEnemyTerritory = 0;
	int iNeutralTerritory = 0;
	int iGuarded = 0;
	int iUnguarded = 0;
	int iThreatened = 0;
	std::vector<int> aiBuilds(GC.getNumBuildInfos(), 0);
	int iLoop = 0;
	for (CvUnit const* pLoopUnit = kPlayer.firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iLoop))
	{
		if (!isSASGameSummaryWorkerUnit(*pLoopUnit))
			continue;
		iWorkers++;
		if (pLoopUnit->AI_getUnitAIType() == UNITAI_WORKER_SEA || pLoopUnit->getDomainType() == DOMAIN_SEA)
			iSeaWorkers++;
		CvPlot const* pPlot = pLoopUnit->plot();
		MissionTypes eMission = getSASGameSummaryUnitMissionType(*pLoopUnit);
		BuildTypes eBuild = pLoopUnit->getBuildType();
		if (eBuild != NO_BUILD)
		{
			iBuilding++;
			aiBuilds[eBuild]++;
			if (GC.getInfo(eBuild).getImprovement() != NO_IMPROVEMENT)
				iBuildingImprovement++;
			if (GC.getInfo(eBuild).getRoute() != NO_ROUTE)
				iBuildingRoute++;
		}
		else if (eMission == MISSION_MOVE_TO || eMission == MISSION_ROUTE_TO || eMission == MISSION_MOVE_TO_UNIT)
			iMoving++;
		else if (pLoopUnit->canMove())
			iIdle++;
		else iWaiting++;
		if (pPlot != NULL)
		{
			if (pPlot->getOwner() == ePlayer)
				iOwnTerritory++;
			else if (pPlot->getTeam() != NO_TEAM && GET_TEAM(eTeam).isAtWar(pPlot->getTeam()))
				iEnemyTerritory++;
			else iNeutralTerritory++;
		}
		if (isSASGameSummaryUnitGuarded(*pLoopUnit))
			iGuarded++;
		else iUnguarded++;
		if (isSASGameSummaryUnitThreatened(*pLoopUnit))
			iThreatened++;
		if (gGameSummaryLogLevel >= 3 && pPlot != NULL)
		{
			logSASGameSummary("GAME_SUMMARY_WORKER turn=%d player=%d unitId=%d unit=%s unitAI=%s x=%d y=%d mission=%s build=%s buildTurnsLeft=%d plotOwner=%d plotTerrain=%s plotFeature=%s plotBonus=%s plotImprovement=%s plotRoute=%s guarded=%d threatened=%d",
					iGameTurn, ePlayer, pLoopUnit->getID(), getSASGameSummaryUnitType(pLoopUnit->getUnitType()), getSASGameSummaryUnitAIType(pLoopUnit->AI_getUnitAIType()), pLoopUnit->getX(), pLoopUnit->getY(), getSASGameSummaryMissionType(eMission), getSASGameSummaryBuildType(eBuild), getSASGameSummaryBuildTurnsLeft(*pLoopUnit, eBuild), pPlot->getOwner(), getSASGameSummaryTerrainType(pPlot->getTerrainType()), getSASGameSummaryFeatureType(pPlot->getFeatureType()), getSASGameSummaryBonusType(pPlot->getBonusType(pLoopUnit->getTeam())), getSASGameSummaryImprovementType(pPlot->getImprovementType()), getSASGameSummaryRouteType(pPlot->getRouteType()), isSASGameSummaryUnitGuarded(*pLoopUnit), isSASGameSummaryUnitThreatened(*pLoopUnit));
		}
	}
	CvString szBuilds;
	for (int iI = 0; iI < GC.getNumBuildInfos(); iI++)
		appendSASGameSummaryTypeCount(szBuilds, getSASGameSummaryBuildType((BuildTypes)iI), aiBuilds[iI]);
	logSASGameSummary("GAME_SUMMARY_WORKERS turn=%d player=%d workers=%d seaWorkers=%d idle=%d building=%d buildingImprovement=%d buildingRoute=%d moving=%d waiting=%d ownTerritory=%d enemyTerritory=%d neutralTerritory=%d guarded=%d unguarded=%d threatened=%d builds=%s",
			iGameTurn, ePlayer, iWorkers, iSeaWorkers, iIdle, iBuilding, iBuildingImprovement, iBuildingRoute, iMoving, iWaiting, iOwnTerritory, iEnemyTerritory, iNeutralTerritory, iGuarded, iUnguarded, iThreatened, getSASGameSummaryOrDash(szBuilds).GetCString());
	logSASGameSummary("GAME_SUMMARY_WORKERS_DELTAS turn=%d player=%d deltaValid=%d workersDelta=%+d buildingDelta=%+d idleDelta=%+d movingDelta=%+d waitingDelta=%+d threatenedDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameSummaryDelta(kPrevious.bValid, iWorkers, kPrevious.iWorkerWorkers), getSASGameSummaryDelta(kPrevious.bValid, iBuilding, kPrevious.iWorkerBuilding), getSASGameSummaryDelta(kPrevious.bValid, iIdle, kPrevious.iWorkerIdle), getSASGameSummaryDelta(kPrevious.bValid, iMoving, kPrevious.iWorkerMoving), getSASGameSummaryDelta(kPrevious.bValid, iWaiting, kPrevious.iWorkerWaiting), getSASGameSummaryDelta(kPrevious.bValid, iThreatened, kPrevious.iWorkerThreatened));
	kPrevious.iWorkerWorkers = iWorkers;
	kPrevious.iWorkerBuilding = iBuilding;
	kPrevious.iWorkerIdle = iIdle;
	kPrevious.iWorkerMoving = iMoving;
	kPrevious.iWorkerWaiting = iWaiting;
	kPrevious.iWorkerThreatened = iThreatened;
}

static void logSASGameSummaryExpansion(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	const TeamTypes eTeam = kPlayer.getTeam();
	static const ImprovementTypes eFarm = (ImprovementTypes)GC.getInfoTypeForString("IMPROVEMENT_FARM");
	int iRevealedLand = 0;
	int iVisibleLand = 0;
	int iRevealedUnownedLand = 0;
	int iVisibleUnownedLand = 0;
	int iRevealedForeignLand = 0;
	int iVisibleForeignLand = 0;
	SASGameSummaryTerritoryDevelopment kTerritoryDevelopment;
	CvMap const& kMap = GC.getMap();
	for (int iI = 0; iI < kMap.numPlots(); iI++)
	{
		CvPlot const& kPlot = kMap.getPlotByIndex(iI);
		if (kPlot.getOwner() == ePlayer)
			addSASGameSummaryTerritoryDevelopment(kTerritoryDevelopment, kPlot, ePlayer, eTeam, eFarm);
		if (kPlot.isWater())
			continue;
		if (kPlot.isRevealed(eTeam, false))
		{
			iRevealedLand++;
			if (kPlot.getOwner() == NO_PLAYER)
				iRevealedUnownedLand++;
			else if (kPlot.getOwner() != ePlayer)
				iRevealedForeignLand++;
		}
		if (kPlot.isVisible(eTeam, false))
		{
			iVisibleLand++;
			if (kPlot.getOwner() == NO_PLAYER)
				iVisibleUnownedLand++;
			else if (kPlot.getOwner() != ePlayer)
				iVisibleForeignLand++;
		}
	}
	int iCitiesProducingSettlers = 0;
	int iCityLoop = 0;
	for (CvCity const* pLoopCity = kPlayer.firstCity(&iCityLoop); pLoopCity != NULL; pLoopCity = kPlayer.nextCity(&iCityLoop))
	{
		UnitTypes eProductionUnit = pLoopCity->getProductionUnit();
		if (eProductionUnit != NO_UNIT && GC.getInfo(eProductionUnit).getDefaultUnitAIType() == UNITAI_SETTLE)
			iCitiesProducingSettlers++;
	}
	int iSettlers = 0;
	int iFoundMission = 0;
	int iNearestSettlerCityDistance = -1;
	int iTotalSettlerCityDistance = 0;
	int iSettlersWithCityDistance = 0;
	int iUnitLoop = 0;
	for (CvUnit const* pLoopUnit = kPlayer.firstUnit(&iUnitLoop); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iUnitLoop))
	{
		if (!isSASGameSummarySettlerUnit(*pLoopUnit))
			continue;
		iSettlers++;
		if (getSASGameSummaryUnitMissionType(*pLoopUnit) == MISSION_FOUND)
			iFoundMission++;
		CvCity const* pNearestCity = kMap.findCity(pLoopUnit->getX(), pLoopUnit->getY(), ePlayer, NO_TEAM, false);
		if (pNearestCity == NULL)
			continue;
		const int iDistance = plotDistance(pLoopUnit->getX(), pLoopUnit->getY(), pNearestCity->getX(), pNearestCity->getY());
		iNearestSettlerCityDistance = (iNearestSettlerCityDistance < 0 ? iDistance : std::min(iNearestSettlerCityDistance, iDistance));
		iTotalSettlerCityDistance += iDistance;
		iSettlersWithCityDistance++;
	}
	const int iAvgSettlerCityDistanceX100 = (iSettlersWithCityDistance == 0 ? -1 : (100 * iTotalSettlerCityDistance) / iSettlersWithCityDistance);
	logSASGameSummary("GAME_SUMMARY_EXPANSION turn=%d player=%d cities=%d targetCities=%d ownedLand=%d revealedLand=%d visibleLand=%d revealedUnownedLand=%d visibleUnownedLand=%d revealedForeignLand=%d visibleForeignLand=%d settlers=%d foundMission=%d citiesProducingSettlers=%d nearestSettlerCityDistance=%d avgSettlerCityDistanceX100=%d",
			iGameTurn, ePlayer, kPlayer.getNumCities(), GC.getInfo(kMap.getWorldSize()).getTargetNumCities(), kPlayer.getTotalLand(), iRevealedLand, iVisibleLand, iRevealedUnownedLand, iVisibleUnownedLand, iRevealedForeignLand, iVisibleForeignLand, iSettlers, iFoundMission, iCitiesProducingSettlers, iNearestSettlerCityDistance, iAvgSettlerCityDistanceX100);
	logSASGameSummaryTerritoryDevelopment(ePlayer, iGameTurn, kTerritoryDevelopment);
}

static void logSASGameSummarySettlers(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	TeamTypes eTeam = kPlayer.getTeam();
	SASGameSummaryPlayerPrevious& kPrevious = g_akSASGameSummaryPlayerPrevious[ePlayer];
	int iSettlers = 0;
	int iFoundMission = 0;
	int iMoving = 0;
	int iIdle = 0;
	int iWaiting = 0;
	int iOwnTerritory = 0;
	int iEnemyTerritory = 0;
	int iNeutralTerritory = 0;
	int iGuarded = 0;
	int iUnguarded = 0;
	int iThreatened = 0;
	int iLoop = 0;
	for (CvUnit const* pLoopUnit = kPlayer.firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iLoop))
	{
		if (!isSASGameSummarySettlerUnit(*pLoopUnit))
			continue;
		iSettlers++;
		CvPlot const* pPlot = pLoopUnit->plot();
		MissionTypes eMission = getSASGameSummaryUnitMissionType(*pLoopUnit);
		if (eMission == MISSION_FOUND)
			iFoundMission++;
		else if (eMission == MISSION_MOVE_TO || eMission == MISSION_ROUTE_TO || eMission == MISSION_MOVE_TO_UNIT)
			iMoving++;
		else if (pLoopUnit->canMove())
			iIdle++;
		else iWaiting++;
		if (pPlot != NULL)
		{
			if (pPlot->getOwner() == ePlayer)
				iOwnTerritory++;
			else if (pPlot->getTeam() != NO_TEAM && GET_TEAM(eTeam).isAtWar(pPlot->getTeam()))
				iEnemyTerritory++;
			else iNeutralTerritory++;
		}
		if (isSASGameSummaryUnitGuarded(*pLoopUnit))
			iGuarded++;
		else iUnguarded++;
		if (isSASGameSummaryUnitThreatened(*pLoopUnit))
			iThreatened++;
		if (gGameSummaryLogLevel >= 3 && pPlot != NULL)
		{
			CvCity const* pNearestCity = GC.getMap().findCity(pLoopUnit->getX(), pLoopUnit->getY(), ePlayer, NO_TEAM, false);
			const int iNearestDistance = pNearestCity == NULL ? -1 : plotDistance(pLoopUnit->getX(), pLoopUnit->getY(), pNearestCity->getX(), pNearestCity->getY());
			logSASGameSummary("GAME_SUMMARY_SETTLER turn=%d player=%d unitId=%d unit=%s unitAI=%s x=%d y=%d mission=%s plotOwner=%d plotTerrain=%s plotFeature=%s plotBonus=%s plotImprovement=%s plotRoute=%s guarded=%d threatened=%d nearestCityId=%d nearestCity=%S nearestCityDistance=%d",
					iGameTurn, ePlayer, pLoopUnit->getID(), getSASGameSummaryUnitType(pLoopUnit->getUnitType()), getSASGameSummaryUnitAIType(pLoopUnit->AI_getUnitAIType()), pLoopUnit->getX(), pLoopUnit->getY(), getSASGameSummaryMissionType(eMission), pPlot->getOwner(), getSASGameSummaryTerrainType(pPlot->getTerrainType()), getSASGameSummaryFeatureType(pPlot->getFeatureType()), getSASGameSummaryBonusType(pPlot->getBonusType(pLoopUnit->getTeam())), getSASGameSummaryImprovementType(pPlot->getImprovementType()), getSASGameSummaryRouteType(pPlot->getRouteType()), isSASGameSummaryUnitGuarded(*pLoopUnit), isSASGameSummaryUnitThreatened(*pLoopUnit), pNearestCity == NULL ? -1 : pNearestCity->getID(), getSASGameSummaryQuotedCityName(pNearestCity).GetCString(), iNearestDistance);
		}
	}
	logSASGameSummary("GAME_SUMMARY_SETTLERS turn=%d player=%d settlers=%d foundMission=%d moving=%d idle=%d waiting=%d ownTerritory=%d enemyTerritory=%d neutralTerritory=%d guarded=%d unguarded=%d threatened=%d",
			iGameTurn, ePlayer, iSettlers, iFoundMission, iMoving, iIdle, iWaiting, iOwnTerritory, iEnemyTerritory, iNeutralTerritory, iGuarded, iUnguarded, iThreatened);
	logSASGameSummary("GAME_SUMMARY_SETTLERS_DELTAS turn=%d player=%d deltaValid=%d settlersDelta=%+d foundMissionDelta=%+d movingDelta=%+d idleDelta=%+d waitingDelta=%+d threatenedDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameSummaryDelta(kPrevious.bValid, iSettlers, kPrevious.iSettlerSettlers), getSASGameSummaryDelta(kPrevious.bValid, iFoundMission, kPrevious.iSettlerFoundMission), getSASGameSummaryDelta(kPrevious.bValid, iMoving, kPrevious.iSettlerMoving), getSASGameSummaryDelta(kPrevious.bValid, iIdle, kPrevious.iSettlerIdle), getSASGameSummaryDelta(kPrevious.bValid, iWaiting, kPrevious.iSettlerWaiting), getSASGameSummaryDelta(kPrevious.bValid, iThreatened, kPrevious.iSettlerThreatened));
	kPrevious.iSettlerSettlers = iSettlers;
	kPrevious.iSettlerFoundMission = iFoundMission;
	kPrevious.iSettlerMoving = iMoving;
	kPrevious.iSettlerIdle = iIdle;
	kPrevious.iSettlerWaiting = iWaiting;
	kPrevious.iSettlerThreatened = iThreatened;
}

static CvString getSASGameSummaryCitySpecialists(CvCity const& kCity, bool bFree)
{
	CvString szList;
	FOR_EACH_ENUM(Specialist)
	{
		const int iCount = (bFree ? kCity.getFreeSpecialistCount(eLoopSpecialist) : kCity.getSpecialistCount(eLoopSpecialist));
		appendSASGameSummaryTypeCount(szList, getSASGameSummarySpecialistType(eLoopSpecialist), iCount);
	}
	return getSASGameSummaryOrDash(szList);
}

static CvString getSASGameSummaryCityGPOdds(CvCity const& kCity)
{
	CvString szList;
	std::vector<std::pair<UnitTypes,int> > aeiProjection;
	kCity.GPProjection(aeiProjection);
	for (size_t iI = 0; iI < aeiProjection.size(); iI++)
		appendSASGameSummaryTypeCount(szList, getSASGameSummaryUnitType(aeiProjection[iI].first), aeiProjection[iI].second);
	return getSASGameSummaryOrDash(szList);
}

static CvString getSASGameSummaryCityHappySources(CvCity const& kCity)
{
	CvString szList;
	CvPlayer const& kOwner = GET_PLAYER(kCity.getOwner());
	appendSASGameSummaryPositiveValue(szList, "largestCity", std::max(0, kCity.getLargestCityHappiness()));
	appendSASGameSummaryPositiveValue(szList, "military", std::max(0, kCity.getMilitaryHappiness()));
	appendSASGameSummaryPositiveValue(szList, "stateReligion", std::max(0, kCity.getCurrentStateReligionHappiness()));
	appendSASGameSummaryPositiveValue(szList, "building", std::max(0, kCity.getBuildingGoodHappiness()));
	appendSASGameSummaryPositiveValue(szList, "extraBuilding", std::max(0, kCity.getExtraBuildingGoodHappiness()));
	appendSASGameSummaryPositiveValue(szList, "surrounding", std::max(0, kCity.getSurroundingGoodHappiness()));
	appendSASGameSummaryPositiveValue(szList, "bonus", std::max(0, kCity.getBonusGoodHappiness()));
	appendSASGameSummaryPositiveValue(szList, "religion", std::max(0, kCity.getReligionGoodHappiness()));
	appendSASGameSummaryPositiveValue(szList, "commerce", std::max(0, kCity.getCommerceHappiness()));
	appendSASGameSummaryPositiveValue(szList, "areaBuilding", std::max(0, kCity.getArea().getBuildingHappiness(kCity.getOwner())));
	appendSASGameSummaryPositiveValue(szList, "playerBuilding", std::max(0, kOwner.getBuildingHappiness()));
	appendSASGameSummaryPositiveValue(szList, "extra", std::max(0, kCity.getExtraHappiness() + kOwner.getExtraHappiness()));
	appendSASGameSummaryPositiveValue(szList, "handicap", std::max(0, GC.getInfo(kCity.getHandicapType()).getHappyBonus()));
	appendSASGameSummaryPositiveValue(szList, "vassal", std::max(0, kCity.getVassalHappiness()));
	appendSASGameSummaryPositiveValue(szList, "temporary", kCity.getHappinessTimer() > 0 ? GC.getDefineINT("TEMP_HAPPY") : 0);
	return getSASGameSummaryOrDash(szList);
}

static CvString getSASGameSummaryCityFlatUnhappySources(CvCity const& kCity)
{
	CvString szList;
	CvPlayer const& kOwner = GET_PLAYER(kCity.getOwner());
	appendSASGameSummaryPositiveValue(szList, "largestCity", -std::min(0, kCity.getLargestCityHappiness()));
	appendSASGameSummaryPositiveValue(szList, "military", -std::min(0, kCity.getMilitaryHappiness()));
	appendSASGameSummaryPositiveValue(szList, "stateReligion", -std::min(0, kCity.getCurrentStateReligionHappiness()));
	appendSASGameSummaryPositiveValue(szList, "building", -std::min(0, kCity.getBuildingBadHappiness()));
	appendSASGameSummaryPositiveValue(szList, "extraBuilding", -std::min(0, kCity.getExtraBuildingBadHappiness()));
	appendSASGameSummaryPositiveValue(szList, "surrounding", -std::min(0, kCity.getSurroundingBadHappiness()));
	appendSASGameSummaryPositiveValue(szList, "bonus", -std::min(0, kCity.getBonusBadHappiness()));
	appendSASGameSummaryPositiveValue(szList, "religion", -std::min(0, kCity.getReligionBadHappiness()));
	appendSASGameSummaryPositiveValue(szList, "commerce", -std::min(0, kCity.getCommerceHappiness()));
	appendSASGameSummaryPositiveValue(szList, "areaBuilding", -std::min(0, kCity.getArea().getBuildingHappiness(kCity.getOwner())));
	appendSASGameSummaryPositiveValue(szList, "playerBuilding", -std::min(0, kOwner.getBuildingHappiness()));
	appendSASGameSummaryPositiveValue(szList, "extra", -std::min(0, kCity.getExtraHappiness() + kOwner.getExtraHappiness()));
	appendSASGameSummaryPositiveValue(szList, "handicap", -std::min(0, GC.getInfo(kCity.getHandicapType()).getHappyBonus()));
	appendSASGameSummaryPositiveValue(szList, "vassal", std::max(0, kCity.getVassalUnhappiness()));
	appendSASGameSummaryPositiveValue(szList, "espionage", std::max(0, kCity.getEspionageHappinessCounter()));
	return getSASGameSummaryOrDash(szList);
}

static CvString getSASGameSummaryCityAngerPercentSources(CvCity const& kCity)
{
	CvString szList;
	CvPlayer const& kOwner = GET_PLAYER(kCity.getOwner());
	int iCivicAnger = 0;
	FOR_EACH_ENUM(Civic)
		iCivicAnger += kOwner.getCivicPercentAnger(eLoopCivic);
	appendSASGameSummaryPositiveValue(szList, "overcrowding", kCity.getOvercrowdingPercentAnger());
	appendSASGameSummaryPositiveValue(szList, "noMilitary", kCity.getNoMilitaryPercentAnger());
	appendSASGameSummaryPositiveValue(szList, "culture", kCity.getCulturePercentAnger());
	appendSASGameSummaryPositiveValue(szList, "religion", kCity.getReligionPercentAnger());
	appendSASGameSummaryPositiveValue(szList, "hurry", kCity.getHurryPercentAnger());
	appendSASGameSummaryPositiveValue(szList, "conscript", kCity.getConscriptPercentAnger());
	appendSASGameSummaryPositiveValue(szList, "defyResolution", kCity.getDefyResolutionPercentAnger());
	appendSASGameSummaryPositiveValue(szList, "warWeariness", kCity.getWarWearinessPercentAnger());
	appendSASGameSummaryPositiveValue(szList, "globalWarming", std::max(0, kOwner.getGwPercentAnger() * 10));
	appendSASGameSummaryPositiveValue(szList, "civics", iCivicAnger);
	return getSASGameSummaryOrDash(szList);
}

static CvString getSASGameSummaryCityHealthySources(CvCity const& kCity)
{
	CvString szList;
	CvPlayer const& kOwner = GET_PLAYER(kCity.getOwner());
	appendSASGameSummaryPositiveValue(szList, "freshWater", std::max(0, kCity.getFreshWaterGoodHealth()));
	appendSASGameSummaryPositiveValue(szList, "surrounding", std::max(0, kCity.getSurroundingGoodHealth()));
	appendSASGameSummaryPositiveValue(szList, "power", std::max(0, kCity.getPowerGoodHealth()));
	appendSASGameSummaryPositiveValue(szList, "bonus", std::max(0, kCity.getBonusGoodHealth()));
	appendSASGameSummaryPositiveValue(szList, "building", std::max(0, kCity.totalGoodBuildingHealth()));
	appendSASGameSummaryPositiveValue(szList, "extra", std::max(0, kCity.getExtraHealth() + kOwner.getExtraHealth()));
	appendSASGameSummaryPositiveValue(szList, "handicap", std::max(0, GC.getInfo(kCity.getHandicapType()).getHealthBonus()));
	return getSASGameSummaryOrDash(szList);
}

static CvString getSASGameSummaryCityUnhealthySources(CvCity const& kCity)
{
	CvString szList;
	CvPlayer const& kOwner = GET_PLAYER(kCity.getOwner());
	appendSASGameSummaryPositiveValue(szList, "population", kCity.unhealthyPopulation());
	appendSASGameSummaryPositiveValue(szList, "espionage", std::max(0, kCity.getEspionageHealthCounter()));
	appendSASGameSummaryPositiveValue(szList, "freshWater", -std::min(0, kCity.getFreshWaterBadHealth()));
	appendSASGameSummaryPositiveValue(szList, "surrounding", -std::min(0, kCity.getSurroundingBadHealth()));
	appendSASGameSummaryPositiveValue(szList, "power", -std::min(0, kCity.getPowerBadHealth()));
	appendSASGameSummaryPositiveValue(szList, "bonus", -std::min(0, kCity.getBonusBadHealth()));
	appendSASGameSummaryPositiveValue(szList, "building", -std::min(0, kCity.totalBadBuildingHealth()));
	appendSASGameSummaryPositiveValue(szList, "extra", -std::min(0, kCity.getExtraHealth() + kOwner.getExtraHealth()));
	appendSASGameSummaryPositiveValue(szList, "handicap", -std::min(0, GC.getInfo(kCity.getHandicapType()).getHealthBonus()));
	return getSASGameSummaryOrDash(szList);
}

static const char* getSASGameSummaryCityProductionKind(CvCity const& kCity)
{
	if (kCity.getProductionUnit() != NO_UNIT)
		return "UNIT";
	if (kCity.getProductionBuilding() != NO_BUILDING)
		return GC.getInfo(kCity.getProductionBuilding()).isLimited() ? "WONDER" : "BUILDING";
	if (kCity.getProductionProject() != NO_PROJECT)
		return "PROJECT";
	if (kCity.getProductionProcess() != NO_PROCESS)
		return "PROCESS";
	return "-";
}

static const char* getSASGameSummaryCityProductionType(CvCity const& kCity)
{
	if (kCity.getProductionUnit() != NO_UNIT)
		return getSASGameSummaryUnitType(kCity.getProductionUnit());
	if (kCity.getProductionBuilding() != NO_BUILDING)
		return getSASGameSummaryBuildingType(kCity.getProductionBuilding());
	if (kCity.getProductionProject() != NO_PROJECT)
		return getSASGameSummaryProjectType(kCity.getProductionProject());
	if (kCity.getProductionProcess() != NO_PROCESS)
		return getSASGameSummaryProcessType(kCity.getProductionProcess());
	return "-";
}

// <!-- custom: Building-completion actions alone cannot reconstruct buildings inherited through conquest, granted for free, or already present when a log begins. At detail level, snapshot the exact owned buildings and compact regular/national/team/world-wonder totals for each city. (GPT-5.6-Sol) -->
static CvString getSASGameSummaryCityBuildings(CvCity const& kCity, int& iTotal, int& iRegular, int& iNationalWonders, int& iTeamWonders, int& iWorldWonders)
{
	CvString szBuildings;
	iTotal = iRegular = iNationalWonders = iTeamWonders = iWorldWonders = 0;
	for (int iI = 0; iI < GC.getNumBuildingInfos(); iI++)
	{
		BuildingTypes const eBuilding = (BuildingTypes)iI;
		int const iCount = kCity.getNumBuilding(eBuilding);
		if (iCount <= 0)
			continue;
		iTotal += iCount;
		CvBuildingInfo const& kBuilding = GC.getInfo(eBuilding);
		if (kBuilding.isWorldWonder())
			iWorldWonders += iCount;
		else if (kBuilding.isTeamWonder())
			iTeamWonders += iCount;
		else if (kBuilding.isNationalWonder())
			iNationalWonders += iCount;
		else iRegular += iCount;
		CvString szItem;
		szItem.Format(szBuildings.empty() ? "%s:%d" : ",%s:%d", getSASGameSummaryBuildingType(eBuilding), iCount);
		szBuildings += szItem;
	}
	return getSASGameSummaryOrDash(szBuildings);
}

// <!-- custom: A PROCESS production name identifies Wealth/Research/Culture but not its actual gain. Record the exact production-to-commerce contribution in hundredths, matching CvCity::updateCommerce without rounding away fractional output. (GPT-5.6-Sol) -->
static CvString getSASGameSummaryCityProductionConversion(CvCity const& kCity)
{
	CvString szConversion;
	if (kCity.getProductionProcess() == NO_PROCESS)
		return "-";
	for (int iI = 0; iI < NUM_COMMERCE_TYPES; iI++)
	{
		CommerceTypes const eCommerce = (CommerceTypes)iI;
		int const iRateX100 = kCity.getYieldRate(YIELD_PRODUCTION) * kCity.getProductionToCommerceModifier(eCommerce);
		if (iRateX100 > 0)
			appendSASGameSummaryValue(szConversion, getSASGameSummaryCommerceType(eCommerce), iRateX100);
	}
	return getSASGameSummaryOrDash(szConversion);
}

static CvString getSASGameSummaryCityTradePartners(CvCity const& kCity)
{
	CvString szList;
	for (int iI = 0; iI < kCity.getTradeRoutes(); iI++)
	{
		CvCity const* pTradeCity = kCity.getTradeCity(iI);
		if (pTradeCity == NULL)
			continue;
		CvString szItem;
		szItem.Format(szList.empty() ? "%d:%d:%S" : ",%d:%d:%S", pTradeCity->getOwner(), pTradeCity->getID(), pTradeCity->getName().GetCString());
		szList += szItem;
	}
	return szList.empty() ? "-" : getSASGameSummaryQuoted(szList.GetCString());
}

// <!-- custom: Settler unit-state helpers for event-based expansion diagnostics. Keep game-summary rows descriptive: raw unit counts, visible enemy counts and combat/founding context, while BBAI logs carry the heavier AI-decision reasons. No gameplay behavior change. (ChatGPT-5.5) -->
struct SASGameSummaryPlotUnitCounts
{
	int iUnits;
	int iMilitaryUnits;
	int iCivilianUnits;
	int iDefenders;
	int iHealthyDefenders;
	int iWoundedDefenders;
	int iSettlers;
	int iWorkers;
	int iAttackers;
	CvUnit const* pBestDefender;
	CvUnit const* pFirstSettler;
	SASGameSummaryPlotUnitCounts() : iUnits(0), iMilitaryUnits(0), iCivilianUnits(0), iDefenders(0), iHealthyDefenders(0), iWoundedDefenders(0), iSettlers(0), iWorkers(0), iAttackers(0), pBestDefender(NULL), pFirstSettler(NULL) {}
};

static void collectSASGameSummaryPlotUnitCounts(CvPlot const& kPlot, PlayerTypes ePlayer, SASGameSummaryPlotUnitCounts& kCounts)
{
	for (CLLNode<IDInfo> const* pUnitNode = kPlot.headUnitNode(); pUnitNode != NULL; pUnitNode = kPlot.nextUnitNode(pUnitNode))
	{
		CvUnit const* pLoopUnit = ::getUnit(pUnitNode->m_data);
		if (pLoopUnit == NULL || pLoopUnit->getOwner() != ePlayer)
			continue;
		kCounts.iUnits++;
		if (pLoopUnit->baseCombatStr() > 0 || pLoopUnit->canAttack() || pLoopUnit->canDefend(&kPlot))
			kCounts.iMilitaryUnits++;
		else kCounts.iCivilianUnits++;
		if (isSASGameSummarySettlerUnit(*pLoopUnit))
		{
			kCounts.iSettlers++;
			if (kCounts.pFirstSettler == NULL)
				kCounts.pFirstSettler = pLoopUnit;
		}
		if (isSASGameSummaryWorkerUnit(*pLoopUnit))
			kCounts.iWorkers++;
		if (pLoopUnit->canAttack())
			kCounts.iAttackers++;
		if (pLoopUnit->canDefend(&kPlot))
		{
			kCounts.iDefenders++;
			if (pLoopUnit->getDamage() <= 25)
				kCounts.iHealthyDefenders++;
			else kCounts.iWoundedDefenders++;
			if (kCounts.pBestDefender == NULL || pLoopUnit->baseCombatStr() > kCounts.pBestDefender->baseCombatStr() || (pLoopUnit->baseCombatStr() == kCounts.pBestDefender->baseCombatStr() && pLoopUnit->getDamage() < kCounts.pBestDefender->getDamage()))
				kCounts.pBestDefender = pLoopUnit;
		}
	}
}


static void logSASGameSummaryWorkedPlots(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	SASGameSummaryPlotComposition kComposition;
	int iLoop = 0;
	for (CvCity const* pLoopCity = kPlayer.firstCity(&iLoop); pLoopCity != NULL; pLoopCity = kPlayer.nextCity(&iLoop))
		addSASGameSummaryPlotComposition(kComposition, getSASGameSummaryWorkedPlotComposition(*pLoopCity));
	CvString szTerrains;
	CvString szFeatures;
	CvString szBonuses;
	CvString szImprovements;
	CvString szRoutes;
	getSASGameSummaryPlotCompositionTypes(kComposition, szTerrains, szFeatures, szBonuses, szImprovements, szRoutes);
	logSASGameSummary("GAME_SUMMARY_WORKED_PLOTS turn=%d player=%d cities=%d worked=%d improved=%d unimproved=%d land=%d water=%d hills=%d riverSide=%d freshWater=%d bonusImproved=%d bonusUnimproved=%d currentFood=%d currentProd=%d currentCommerce=%d natureFood=%d natureProd=%d natureCommerce=%d terrains=%s features=%s bonuses=%s improvements=%s routes=%s",
			iGameTurn, ePlayer, kPlayer.getNumCities(), kComposition.iWorked, kComposition.iWorkedImproved, kComposition.iWorkedUnimproved, kComposition.iLand, kComposition.iWater, kComposition.iHills, kComposition.iRiverSide, kComposition.iFreshWater, kComposition.iBonusImproved, kComposition.iBonusUnimproved, kComposition.iCurrentFood, kComposition.iCurrentProduction, kComposition.iCurrentCommerce, kComposition.iNatureFood, kComposition.iNatureProduction, kComposition.iNatureCommerce, getSASGameSummaryOrDash(szTerrains).GetCString(), getSASGameSummaryOrDash(szFeatures).GetCString(), getSASGameSummaryOrDash(szBonuses).GetCString(), getSASGameSummaryOrDash(szImprovements).GetCString(), getSASGameSummaryOrDash(szRoutes).GetCString());
}

static void logSASGameSummaryCityDetail(CvCity const& kCity, int iGameTurn)
{
	CvPlotGroup const* pPlotGroup = kCity.plotGroup(kCity.getOwner());
	int iDomesticTradeRoutes = 0;
	int iForeignTradeRoutes = 0;
	for (int iI = 0; iI < kCity.getTradeRoutes(); iI++)
	{
		CvCity const* pTradeCity = kCity.getTradeCity(iI);
		if (pTradeCity == NULL)
			continue;
		if (pTradeCity->getOwner() == kCity.getOwner())
			iDomesticTradeRoutes++;
		else iForeignTradeRoutes++;
	}
	CvPlayer const& kOwner = GET_PLAYER(kCity.getOwner());
	const SASGameSummaryPlotComposition kWorkedPlots = getSASGameSummaryWorkedPlotComposition(kCity);
	SASGameSummaryPlotUnitCounts kCityUnits;
	collectSASGameSummaryPlotUnitCounts(kCity.getPlot(), kCity.getOwner(), kCityUnits);
	logSASGameSummary("GAME_SUMMARY_CITY turn=%d player=%d cityId=%d city=%S x=%d y=%d pop=%d foodSurplus=%d happySurplus=%d healthSurplus=%d food=%d prod=%d commerce=%d worked=%d workedImproved=%d workedUnimproved=%d workedFood=%d workedProd=%d workedCommerce=%d garrison=%d cityUnits=%d militaryUnits=%d civilianUnits=%d defenders=%d healthyDefenders=%d woundedDefenders=%d settlers=%d workers=%d attackers=%d connectedToCapital=%d plotGroupId=%d tradeRoutes=%d domesticTradeRoutes=%d foreignTradeRoutes=%d tradeFood=%d tradeProd=%d tradeCommerce=%d productionKind=%s production=%s productionTurns=%d productionStored=%d productionNeeded=%d overflowProduction=%d featureProduction=%d productionConversionX100=%s specialists=%s freeSpecialists=%s gpProgress=%d gpThreshold=%d gpRate=%d gpTurnsLeft=%d gpOdds=%s",
			iGameTurn, kCity.getOwner(), kCity.getID(), getSASGameSummaryQuotedCityName(&kCity).GetCString(), kCity.getX(), kCity.getY(), kCity.getPopulation(), kCity.foodDifference(), kCity.happyLevel() - kCity.unhappyLevel(), kCity.goodHealth() - kCity.badHealth(), kCity.getYieldRate(YIELD_FOOD), kCity.getYieldRate(YIELD_PRODUCTION), kCity.getYieldRate(YIELD_COMMERCE),
			kWorkedPlots.iWorked, kWorkedPlots.iWorkedImproved, kWorkedPlots.iWorkedUnimproved, kWorkedPlots.iCurrentFood, kWorkedPlots.iCurrentProduction, kWorkedPlots.iCurrentCommerce, kCity.plot()->getNumDefenders(kCity.getOwner()), kCityUnits.iUnits, kCityUnits.iMilitaryUnits, kCityUnits.iCivilianUnits, kCityUnits.iDefenders, kCityUnits.iHealthyDefenders, kCityUnits.iWoundedDefenders, kCityUnits.iSettlers, kCityUnits.iWorkers, kCityUnits.iAttackers,
			kCity.isConnectedToCapital(), pPlotGroup == NULL ? -1 : pPlotGroup->getID(), kCity.getTradeRoutes(), iDomesticTradeRoutes, iForeignTradeRoutes, kCity.getTradeYield(YIELD_FOOD), kCity.getTradeYield(YIELD_PRODUCTION), kCity.getTradeYield(YIELD_COMMERCE),
			getSASGameSummaryCityProductionKind(kCity), getSASGameSummaryCityProductionType(kCity), kCity.getProductionTurnsLeft(), kCity.getProduction(), kCity.getProductionNeeded(), kCity.getOverflowProduction(), kCity.getFeatureProduction(), getSASGameSummaryCityProductionConversion(kCity).GetCString(), getSASGameSummaryCitySpecialists(kCity, false).GetCString(), getSASGameSummaryCitySpecialists(kCity, true).GetCString(),
			kCity.getGreatPeopleProgress(), kOwner.greatPeopleThreshold(false), kCity.getGreatPeopleRate(), kCity.GPTurnsLeft(), getSASGameSummaryCityGPOdds(kCity).GetCString());
	logSASGameSummary("GAME_SUMMARY_CITY_HAPPINESS turn=%d player=%d cityId=%d happy=%d unhappy=%d surplus=%d happySources=%s flatUnhappySources=%s angerPercentSources=%s",
			iGameTurn, kCity.getOwner(), kCity.getID(), kCity.happyLevel(), kCity.unhappyLevel(), kCity.happyLevel() - kCity.unhappyLevel(),
			getSASGameSummaryCityHappySources(kCity).GetCString(), getSASGameSummaryCityFlatUnhappySources(kCity).GetCString(), getSASGameSummaryCityAngerPercentSources(kCity).GetCString());
	logSASGameSummary("GAME_SUMMARY_CITY_HEALTH turn=%d player=%d cityId=%d goodHealth=%d badHealth=%d surplus=%d powered=%d dirtyPower=%d areaCleanPower=%d powerGoodHealth=%d powerBadHealth=%d healthySources=%s unhealthySources=%s",
			iGameTurn, kCity.getOwner(), kCity.getID(), kCity.goodHealth(), kCity.badHealth(), kCity.goodHealth() - kCity.badHealth(),
			kCity.isPower(), kCity.isDirtyPower(), kCity.isAreaCleanPower(), kCity.getPowerGoodHealth(), kCity.getPowerBadHealth(), getSASGameSummaryCityHealthySources(kCity).GetCString(), getSASGameSummaryCityUnhealthySources(kCity).GetCString());
	int iBuildings, iRegularBuildings, iNationalWonders, iTeamWonders, iWorldWonders;
	CvString const szBuildings = getSASGameSummaryCityBuildings(kCity, iBuildings, iRegularBuildings, iNationalWonders, iTeamWonders, iWorldWonders);
	logSASGameSummary("GAME_SUMMARY_CITY_BUILDINGS turn=%d player=%d cityId=%d total=%d regular=%d nationalWonders=%d teamWonders=%d worldWonders=%d buildings=%s", iGameTurn, kCity.getOwner(), kCity.getID(), iBuildings, iRegularBuildings, iNationalWonders, iTeamWonders, iWorldWonders, szBuildings.GetCString());
	if (gGameSummaryLogLevel >= 3) logSASGameSummary("GAME_SUMMARY_CITY_TRADE_PARTNERS turn=%d player=%d cityId=%d partners=%s", iGameTurn, kCity.getOwner(), kCity.getID(), getSASGameSummaryCityTradePartners(kCity).GetCString());
	// <!-- custom: Large city garrisons in autoplay logs did not reveal whether an army was one parked attack stack or many defensive/miscellaneous groups. At game-summary level 3, record compact group and UnitAI composition for cities with at least six military units; BBAI UNIT logging remains responsible for the groups' decision reasons. (GPT-5.6-Sol) -->
	if (gGameSummaryLogLevel >= 3 && kCityUnits.iMilitaryUnits >= 6)
	{
		std::vector<int> aiUnitTypes(GC.getNumUnitInfos(), 0);
		std::vector<int> aiUnitAI(NUM_UNITAI_TYPES, 0);
		std::vector<int> aiGroupIds;
		CvSelectionGroup const* pLargestGroup = NULL;
		for (CLLNode<IDInfo> const* pUnitNode = kCity.getPlot().headUnitNode(); pUnitNode != NULL; pUnitNode = kCity.getPlot().nextUnitNode(pUnitNode))
		{
			CvUnit const* pLoopUnit = ::getUnit(pUnitNode->m_data);
			if (pLoopUnit == NULL || pLoopUnit->getOwner() != kCity.getOwner() || !isSASGameSummaryMilitaryUnit(*pLoopUnit))
				continue;
			if (pLoopUnit->getUnitType() != NO_UNIT)
				aiUnitTypes[pLoopUnit->getUnitType()]++;
			UnitAITypes const eUnitAI = pLoopUnit->AI_getUnitAIType();
			if (eUnitAI >= 0 && eUnitAI < NUM_UNITAI_TYPES)
				aiUnitAI[eUnitAI]++;
			CvSelectionGroup const* pGroup = pLoopUnit->getGroup();
			if (pGroup == NULL)
				continue;
			bool bGroupAlreadyCounted = false;
			for (size_t iI = 0; iI < aiGroupIds.size(); iI++)
			{
				if (aiGroupIds[iI] == pGroup->getID())
				{
					bGroupAlreadyCounted = true;
					break;
				}
			}
			if (!bGroupAlreadyCounted)
				aiGroupIds.push_back(pGroup->getID());
			if (pLargestGroup == NULL || pGroup->getNumUnits() > pLargestGroup->getNumUnits())
				pLargestGroup = pGroup;
		}
		CvString szUnitTypes;
		CvString szUnitAI;
		for (int iI = 0; iI < GC.getNumUnitInfos(); iI++)
			appendSASGameSummaryTypeCount(szUnitTypes, getSASGameSummaryUnitType((UnitTypes)iI), aiUnitTypes[iI]);
		for (int iI = 0; iI < NUM_UNITAI_TYPES; iI++)
			appendSASGameSummaryTypeCount(szUnitAI, getSASGameSummaryUnitAIType((UnitAITypes)iI), aiUnitAI[iI]);
		CvSelectionGroupAI const* pLargestGroupAI = (pLargestGroup == NULL ? NULL : &pLargestGroup->AI());
		CvUnitAI const* pLargestGroupHead = (pLargestGroupAI == NULL ? NULL : pLargestGroupAI->AI_getHeadUnit());
		CvPlot const* pLargestGroupMissionPlot = (pLargestGroupAI == NULL ? NULL : pLargestGroupAI->AI_getMissionAIPlot());
		CvUnitAI const* pLargestGroupMissionUnit = (pLargestGroupAI == NULL ? NULL : pLargestGroupAI->AI_getMissionAIUnit());
		int iLargestGroupWounded = 0;
		if (pLargestGroup != NULL)
		{
			FOR_EACH_UNIT_IN(pLoopUnit, *pLargestGroup)
			{
				if (pLoopUnit->getDamage() > 0) iLargestGroupWounded++;
			}
		}
		// <!-- custom: Ordinary city-detail calculations above use CvPlayer, but incoming group-mission queries are available only through CvPlayerAI. Keep the derived reference scoped to this level-3 diagnostic. (GPT-5.6-Sol) -->
		CvPlayerAI const& kOwnerAI = GET_PLAYER(kCity.getOwner());
		int const iLargestGroupIncomingJoiners = (pLargestGroupHead == NULL ? -1 : kOwnerAI.AI_unitTargetMissionAIs(*pLargestGroupHead, MISSIONAI_GROUP));
		// <!-- custom: A peaceful Aztec attack-city group grew to 86 of 137 military units but stopped appearing in ATTACK_CITY_PARKING, so its persistent state or an earlier return path was invisible.
		// At level 3, preserve the largest city group's activity, queued mission, MissionAI target, wounded count, and incoming joiners alongside composition; paired UNIT diagnostics trace AI_attackCityMove when it is actually entered. (GPT-5.6-Sol) -->
		logSASGameSummary("GAME_SUMMARY_CITY_UNIT_COMPOSITION turn=%d player=%d cityId=%d city=%S militaryUnits=%d groups=%d largestGroupId=%d largestGroupUnits=%d largestGroupHeadAI=%s largestGroupActivity=%d largestGroupMission=%s largestGroupMissionAI=%d largestGroupMissionPlot=(%d,%d) largestGroupMissionUnitOwner=%d largestGroupMissionUnitId=%d largestGroupMissionQueue=%d largestGroupWounded=%d largestGroupIncomingJoiners=%d unitTypes=%s unitAI=%s",
				iGameTurn, kCity.getOwner(), kCity.getID(), getSASGameSummaryQuotedCityName(&kCity).GetCString(), kCityUnits.iMilitaryUnits, (int)aiGroupIds.size(), (pLargestGroup == NULL ? -1 : pLargestGroup->getID()), (pLargestGroup == NULL ? 0 : pLargestGroup->getNumUnits()), (pLargestGroupHead == NULL ? "-" : getSASGameSummaryUnitAIType(pLargestGroupHead->AI_getUnitAIType())),
				(pLargestGroup == NULL ? NO_ACTIVITY : pLargestGroup->getActivityType()), (pLargestGroup == NULL ? "-" : getSASGameSummaryMissionType(pLargestGroup->getMissionType(0))), (pLargestGroupAI == NULL ? NO_MISSIONAI : pLargestGroupAI->AI_getMissionAIType()),
				(pLargestGroupMissionPlot == NULL ? -1 : pLargestGroupMissionPlot->getX()), (pLargestGroupMissionPlot == NULL ? -1 : pLargestGroupMissionPlot->getY()), (pLargestGroupMissionUnit == NULL ? -1 : pLargestGroupMissionUnit->getOwner()), (pLargestGroupMissionUnit == NULL ? -1 : pLargestGroupMissionUnit->getID()), (pLargestGroup == NULL ? 0 : pLargestGroup->getLengthMissionQueue()),
				iLargestGroupWounded, iLargestGroupIncomingJoiners, getSASGameSummaryOrDash(szUnitTypes).GetCString(), getSASGameSummaryOrDash(szUnitAI).GetCString());
	}
}

static void logSASGameSummaryCities(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	SASGameSummaryPlayerPrevious& kPrevious = g_akSASGameSummaryPlayerPrevious[ePlayer];
	int iCities = 0;
	int iTotalFoodSurplus = 0;
	int iTotalHappySurplus = 0;
	int iTotalHealthSurplus = 0;
	int iTotalFoodYield = 0;
	int iTotalProductionYield = 0;
	int iTotalCommerceYield = 0;
	int iTotalTradeRoutes = 0;
	int iDomesticTradeRoutes = 0;
	int iForeignTradeRoutes = 0;
	int iTradeFood = 0;
	int iTradeProduction = 0;
	int iTradeCommerce = 0;
	int iConnectedToCapital = 0;
	int iUnhappyCities = 0;
	int iUnhealthyCities = 0;
	int iStarvingCities = 0;
	int iCitiesProducingUnits = 0;
	int iCitiesProducingMilitary = 0;
	int iCitiesProducingWorkers = 0;
	int iCitiesProducingSettlers = 0;
	int iCitiesProducingBuildings = 0;
	int iCitiesProducingWonders = 0;
	int iCitiesProducingProjects = 0;
	int iCitiesProducingProcesses = 0;
	int iSpecialists = 0;
	int iFreeSpecialists = 0;
	int iGarrison = 0;
	int iCityUnits = 0;
	int iMilitaryUnitsInCities = 0;
	int iCivilianUnitsInCities = 0;
	int iDefendersInCities = 0;
	int iSettlersInCities = 0;
	int iWorkersInCities = 0;
	int iBestGPTurns = 1000000;
	CvCity const* pNextGPCity = NULL;
	int iLoop = 0;
	CvCity const* pCapital = kPlayer.getCapital();
	for (CvCity const* pLoopCity = kPlayer.firstCity(&iLoop); pLoopCity != NULL; pLoopCity = kPlayer.nextCity(&iLoop))
	{
		iCities++;
		const int iFoodSurplus = pLoopCity->foodDifference();
		const int iHappySurplus = pLoopCity->happyLevel() - pLoopCity->unhappyLevel();
		const int iHealthSurplus = pLoopCity->goodHealth() - pLoopCity->badHealth();
		iTotalFoodSurplus += iFoodSurplus;
		iTotalHappySurplus += iHappySurplus;
		iTotalHealthSurplus += iHealthSurplus;
		iTotalFoodYield += pLoopCity->getYieldRate(YIELD_FOOD);
		iTotalProductionYield += pLoopCity->getYieldRate(YIELD_PRODUCTION);
		iTotalCommerceYield += pLoopCity->getYieldRate(YIELD_COMMERCE);
		iTotalTradeRoutes += pLoopCity->getTradeRoutes();
		iTradeFood += pLoopCity->getTradeYield(YIELD_FOOD);
		iTradeProduction += pLoopCity->getTradeYield(YIELD_PRODUCTION);
		iTradeCommerce += pLoopCity->getTradeYield(YIELD_COMMERCE);
		for (int iTrade = 0; iTrade < pLoopCity->getTradeRoutes(); iTrade++)
		{
			CvCity const* pTradeCity = pLoopCity->getTradeCity(iTrade);
			if (pTradeCity == NULL)
				continue;
			if (pTradeCity->getOwner() == ePlayer)
				iDomesticTradeRoutes++;
			else iForeignTradeRoutes++;
		}
		if (pLoopCity->isConnectedToCapital())
			iConnectedToCapital++;
		if (iHappySurplus < 0)
			iUnhappyCities++;
		if (iHealthSurplus < 0)
			iUnhealthyCities++;
		if (iFoodSurplus < 0)
			iStarvingCities++;
		iSpecialists += pLoopCity->getSpecialistPopulation();
		iFreeSpecialists += pLoopCity->totalFreeSpecialists();
		iGarrison += pLoopCity->plot()->getNumDefenders(ePlayer);
		SASGameSummaryPlotUnitCounts kCityUnits;
		collectSASGameSummaryPlotUnitCounts(pLoopCity->getPlot(), ePlayer, kCityUnits);
		iCityUnits += kCityUnits.iUnits;
		iMilitaryUnitsInCities += kCityUnits.iMilitaryUnits;
		iCivilianUnitsInCities += kCityUnits.iCivilianUnits;
		iDefendersInCities += kCityUnits.iDefenders;
		iSettlersInCities += kCityUnits.iSettlers;
		iWorkersInCities += kCityUnits.iWorkers;
		const int iGPTurns = pLoopCity->GPTurnsLeft();
		if (iGPTurns >= 0 && iGPTurns < iBestGPTurns)
		{
			iBestGPTurns = iGPTurns;
			pNextGPCity = pLoopCity;
		}
		UnitTypes eProductionUnit = pLoopCity->getProductionUnit();
		BuildingTypes eProductionBuilding = pLoopCity->getProductionBuilding();
		if (eProductionUnit != NO_UNIT)
		{
			iCitiesProducingUnits++;
			UnitAITypes eUnitAI = GC.getInfo(eProductionUnit).getDefaultUnitAIType();
			if (GC.getInfo(eProductionUnit).isMilitaryProduction())
				iCitiesProducingMilitary++;
			if (eUnitAI == UNITAI_WORKER || eUnitAI == UNITAI_WORKER_SEA)
				iCitiesProducingWorkers++;
			if (eUnitAI == UNITAI_SETTLE)
				iCitiesProducingSettlers++;
		}
		else if (eProductionBuilding != NO_BUILDING)
		{
			iCitiesProducingBuildings++;
			if (GC.getInfo(eProductionBuilding).isLimited())
				iCitiesProducingWonders++;
		}
		else if (pLoopCity->getProductionProject() != NO_PROJECT)
			iCitiesProducingProjects++;
		else if (pLoopCity->getProductionProcess() != NO_PROCESS)
			iCitiesProducingProcesses++;
		if (gGameSummaryLogLevel >= 3) logSASGameSummaryCityDetail(*pLoopCity, iGameTurn);
	}
	logSASGameSummary("GAME_SUMMARY_CITIES turn=%d player=%d cities=%d capitalId=%d capital=%S connectedToCapital=%d totalFoodSurplus=%d totalHappySurplus=%d totalHealthSurplus=%d totalFood=%d totalProd=%d totalCommerce=%d tradeRoutes=%d domesticTradeRoutes=%d foreignTradeRoutes=%d tradeFood=%d tradeProd=%d tradeCommerce=%d unhappyCities=%d unhealthyCities=%d starvingCities=%d specialists=%d freeSpecialists=%d garrison=%d cityUnits=%d militaryUnits=%d civilianUnits=%d defenders=%d settlers=%d workers=%d nextGPCityId=%d nextGPCity=%S nextGPTurns=%d nextGPRate=%d nextGPProgress=%d citiesProducingUnits=%d citiesProducingMilitary=%d citiesProducingWorkers=%d citiesProducingSettlers=%d citiesProducingBuildings=%d citiesProducingWonders=%d citiesProducingProjects=%d citiesProducingProcesses=%d",
			iGameTurn, ePlayer, iCities, pCapital == NULL ? -1 : pCapital->getID(), getSASGameSummaryQuotedCityName(pCapital).GetCString(), iConnectedToCapital, iTotalFoodSurplus, iTotalHappySurplus, iTotalHealthSurplus, iTotalFoodYield, iTotalProductionYield, iTotalCommerceYield, iTotalTradeRoutes, iDomesticTradeRoutes, iForeignTradeRoutes, iTradeFood, iTradeProduction, iTradeCommerce, iUnhappyCities, iUnhealthyCities, iStarvingCities, iSpecialists, iFreeSpecialists, iGarrison, iCityUnits, iMilitaryUnitsInCities, iCivilianUnitsInCities, iDefendersInCities, iSettlersInCities, iWorkersInCities, pNextGPCity == NULL ? -1 : pNextGPCity->getID(), getSASGameSummaryQuotedCityName(pNextGPCity).GetCString(), pNextGPCity == NULL ? -1 : iBestGPTurns, pNextGPCity == NULL ? 0 : pNextGPCity->getGreatPeopleRate(), pNextGPCity == NULL ? 0 : pNextGPCity->getGreatPeopleProgress(), iCitiesProducingUnits, iCitiesProducingMilitary, iCitiesProducingWorkers, iCitiesProducingSettlers, iCitiesProducingBuildings, iCitiesProducingWonders, iCitiesProducingProjects, iCitiesProducingProcesses);
	logSASGameSummary("GAME_SUMMARY_CITIES_DELTAS turn=%d player=%d deltaValid=%d citiesDelta=%+d connectedToCapitalDelta=%+d totalFoodSurplusDelta=%+d totalHappySurplusDelta=%+d totalHealthSurplusDelta=%+d totalFoodDelta=%+d totalProdDelta=%+d totalCommerceDelta=%+d tradeRoutesDelta=%+d tradeCommerceDelta=%+d specialistsDelta=%+d freeSpecialistsDelta=%+d garrisonDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameSummaryDelta(kPrevious.bValid, iCities, kPrevious.iCityCount), getSASGameSummaryDelta(kPrevious.bValid, iConnectedToCapital, kPrevious.iCityConnectedToCapital), getSASGameSummaryDelta(kPrevious.bValid, iTotalFoodSurplus, kPrevious.iCityFoodSurplus), getSASGameSummaryDelta(kPrevious.bValid, iTotalHappySurplus, kPrevious.iCityHappySurplus), getSASGameSummaryDelta(kPrevious.bValid, iTotalHealthSurplus, kPrevious.iCityHealthSurplus), getSASGameSummaryDelta(kPrevious.bValid, iTotalFoodYield, kPrevious.iCityFood), getSASGameSummaryDelta(kPrevious.bValid, iTotalProductionYield, kPrevious.iCityProduction), getSASGameSummaryDelta(kPrevious.bValid, iTotalCommerceYield, kPrevious.iCityCommerce), getSASGameSummaryDelta(kPrevious.bValid, iTotalTradeRoutes, kPrevious.iCityTradeRoutes), getSASGameSummaryDelta(kPrevious.bValid, iTradeCommerce, kPrevious.iCityTradeCommerce), getSASGameSummaryDelta(kPrevious.bValid, iSpecialists, kPrevious.iCitySpecialists), getSASGameSummaryDelta(kPrevious.bValid, iFreeSpecialists, kPrevious.iCityFreeSpecialists), getSASGameSummaryDelta(kPrevious.bValid, iGarrison, kPrevious.iCityGarrison));
	kPrevious.iCityCount = iCities;
	kPrevious.iCityConnectedToCapital = iConnectedToCapital;
	kPrevious.iCityFoodSurplus = iTotalFoodSurplus;
	kPrevious.iCityHappySurplus = iTotalHappySurplus;
	kPrevious.iCityHealthSurplus = iTotalHealthSurplus;
	kPrevious.iCityFood = iTotalFoodYield;
	kPrevious.iCityProduction = iTotalProductionYield;
	kPrevious.iCityCommerce = iTotalCommerceYield;
	kPrevious.iCityTradeRoutes = iTotalTradeRoutes;
	kPrevious.iCityTradeCommerce = iTradeCommerce;
	kPrevious.iCitySpecialists = iSpecialists;
	kPrevious.iCityFreeSpecialists = iFreeSpecialists;
	kPrevious.iCityGarrison = iGarrison;
}

static void logSASGameSummaryPlayerSnapshot(PlayerTypes ePlayer, int iGameTurn)
{
	CvGame const& kGame = GC.getGame();
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvTeam const& kTeam = GET_TEAM(kPlayer.getTeam());
	TechTypes eResearch = kPlayer.getCurrentResearch();
	const int iScore = kPlayer.calculateScore();
	const int iCities = kPlayer.getNumCities();
	const int iPopulation = kPlayer.getTotalPopulation();
	const int iLand = kPlayer.getTotalLand();
	const int iUnits = kPlayer.getNumUnits();
	const int iMilitaryUnits = kPlayer.getNumMilitaryUnits();
	const int iPower = kPlayer.getPower();
	const int iGold = kPlayer.getGold();
	const int iGoldRate = kPlayer.calculateGoldRate();
	// <!-- custom: Keep nominal science visible when no target is selected because that science becomes stored research overflow rather than disappearing. (GPT-5.6-Sol) -->
	const int iResearchRate = kPlayer.calculateResearchRate(eResearch);
	const int iResearchTurns = (eResearch == NO_TECH ? -1 : kPlayer.getResearchTurnsLeft(eResearch, true));
	const int iHistoryScore = kPlayer.getHistorySafe(PLAYER_HISTORY_SCORE, iGameTurn);
	const int iHistoryEconomy = kPlayer.getHistorySafe(PLAYER_HISTORY_ECONOMY, iGameTurn);
	const int iHistoryIndustry = kPlayer.getHistorySafe(PLAYER_HISTORY_INDUSTRY, iGameTurn);
	const int iHistoryAgriculture = kPlayer.getHistorySafe(PLAYER_HISTORY_AGRICULTURE, iGameTurn);
	const int iHistoryPower = kPlayer.getHistorySafe(PLAYER_HISTORY_POWER, iGameTurn);
	const int iHistoryCulture = kPlayer.getHistorySafe(PLAYER_HISTORY_CULTURE, iGameTurn);
	const int iHistoryEspionage = kPlayer.getHistorySafe(PLAYER_HISTORY_ESPIONAGE, iGameTurn);
	SASGameSummaryPlayerPrevious& kPrevious = g_akSASGameSummaryPlayerPrevious[ePlayer];
	const char* szCiv = (kPlayer.getCivilizationType() == NO_CIVILIZATION ? "-" : GC.getInfo(kPlayer.getCivilizationType()).getType());
	const char* szLeader = (kPlayer.getLeaderType() == NO_LEADER ? "-" : GC.getInfo(kPlayer.getLeaderType()).getType());
	const char* szEra = (kPlayer.getCurrentEra() == NO_ERA ? "-" : GC.getInfo(kPlayer.getCurrentEra()).getType());
	const bool bCurrentlyHumanControlled = kPlayer.isHuman();
	const bool bAutoplayControlled = kPlayer.isHumanDisabled();
	const bool bHumanSlot = (bCurrentlyHumanControlled || bAutoplayControlled);
	logSASGameSummary("GAME_SUMMARY_PLAYER turn=%d player=%d team=%d civ=%s leader=%s isHuman=%d humanSlot=%d currentlyHumanControlled=%d autoplayControlled=%d rank=%d deltaValid=%d score=%d scoreDelta=%+d cities=%d citiesDelta=%+d pop=%d popDelta=%+d land=%d landDelta=%+d units=%d unitsDelta=%+d militaryUnits=%d militaryUnitsDelta=%+d power=%d powerDelta=%+d gold=%d goldDelta=%+d gpt=%d gptDelta=%+d researchRate=%d researchRateDelta=%+d researchPercent=%d currentResearch=%s researchOverflow=%d noResearchAvailable=%d researchTurns=%d era=%s stateReligion=%s techScorePercent=%d combatXP=%d greatPeopleCreated=%d greatGeneralsCreated=%d greatGeneralThreshold=%d goldenAgeTurns=%d totalGoldenAgeTurns=%d anarchyTurns=%d totalAnarchyTurns=%d revolutionTimer=%d conversionTimer=%d wars=%s",
			iGameTurn, ePlayer, kPlayer.getTeam(), szCiv, szLeader, bCurrentlyHumanControlled, bHumanSlot, bCurrentlyHumanControlled, bAutoplayControlled, kGame.getPlayerRank(ePlayer) + 1, kPrevious.bValid,
			iScore, getSASGameSummaryDelta(kPrevious.bValid, iScore, kPrevious.iScore), iCities, getSASGameSummaryDelta(kPrevious.bValid, iCities, kPrevious.iCities),
			iPopulation, getSASGameSummaryDelta(kPrevious.bValid, iPopulation, kPrevious.iPopulation), iLand, getSASGameSummaryDelta(kPrevious.bValid, iLand, kPrevious.iLand),
			iUnits, getSASGameSummaryDelta(kPrevious.bValid, iUnits, kPrevious.iUnits), iMilitaryUnits, getSASGameSummaryDelta(kPrevious.bValid, iMilitaryUnits, kPrevious.iMilitaryUnits),
			iPower, getSASGameSummaryDelta(kPrevious.bValid, iPower, kPrevious.iPower), iGold, getSASGameSummaryDelta(kPrevious.bValid, iGold, kPrevious.iGold), iGoldRate, getSASGameSummaryDelta(kPrevious.bValid, iGoldRate, kPrevious.iGoldRate),
			iResearchRate, getSASGameSummaryDelta(kPrevious.bValid, iResearchRate, kPrevious.iResearchRate), kPlayer.getCommercePercent(COMMERCE_RESEARCH), getSASGameSummaryTechType(eResearch), kPlayer.getOverflowResearch(), kPlayer.isNoResearchAvailable(), iResearchTurns,
			szEra, getSASGameSummaryReligionType(kPlayer.getStateReligion()), kTeam.getBestKnownTechScorePercent(), kPlayer.getCombatExperience(), kPlayer.getGreatPeopleCreated(), kPlayer.getGreatGeneralsCreated(), kPlayer.greatPeopleThreshold(true),
			kPlayer.getGoldenAgeTurns(), g_aiSASGameSummaryTotalGoldenAgeTurns[ePlayer], kPlayer.getAnarchyTurns(), g_aiSASGameSummaryTotalAnarchyTurns[ePlayer], kPlayer.getRevolutionTimer(), kPlayer.getConversionTimer(), getSASGameSummaryWarTeams(kPlayer.getTeam()).GetCString());
	logSASGameSummary("GAME_SUMMARY_PLAYER_HISTORY turn=%d player=%d deltaValid=%d historyScore=%d historyScoreDelta=%+d historyEconomy=%d historyEconomyDelta=%+d historyIndustry=%d historyIndustryDelta=%+d historyAgriculture=%d historyAgricultureDelta=%+d historyPower=%d historyPowerDelta=%+d historyCulture=%d historyCultureDelta=%+d historyEspionage=%d historyEspionageDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, iHistoryScore, getSASGameSummaryDelta(kPrevious.bValid, iHistoryScore, kPrevious.iHistoryScore), iHistoryEconomy, getSASGameSummaryDelta(kPrevious.bValid, iHistoryEconomy, kPrevious.iHistoryEconomy), iHistoryIndustry, getSASGameSummaryDelta(kPrevious.bValid, iHistoryIndustry, kPrevious.iHistoryIndustry), iHistoryAgriculture, getSASGameSummaryDelta(kPrevious.bValid, iHistoryAgriculture, kPrevious.iHistoryAgriculture), iHistoryPower, getSASGameSummaryDelta(kPrevious.bValid, iHistoryPower, kPrevious.iHistoryPower), iHistoryCulture, getSASGameSummaryDelta(kPrevious.bValid, iHistoryCulture, kPrevious.iHistoryCulture), iHistoryEspionage, getSASGameSummaryDelta(kPrevious.bValid, iHistoryEspionage, kPrevious.iHistoryEspionage));
	// <!-- custom: The environment row shows world pollution, but not which player produced it or whether buildings, bonuses, dirty power, or population caused it. Keep these city scans behind summary level 2, and derive the total from the four components rather than scanning a fifth time. (GPT-5.6-Sol) -->
	if (gGameSummaryLogLevel >= 2)
	{
		int const iBuildingPollution = kPlayer.calculatePollution(CvPlayer::POLLUTION_BUILDINGS);
		int const iBonusPollution = kPlayer.calculatePollution(CvPlayer::POLLUTION_BONUSES);
		int const iPowerPollution = kPlayer.calculatePollution(CvPlayer::POLLUTION_POWER);
		int const iPopulationPollution = kPlayer.calculatePollution(CvPlayer::POLLUTION_POPULATION);
		logSASGameSummary("GAME_SUMMARY_POLLUTION turn=%d player=%d total=%d buildings=%d bonuses=%d power=%d population=%d", iGameTurn, ePlayer, iBuildingPollution + iBonusPollution + iPowerPollution + iPopulationPollution, iBuildingPollution, iBonusPollution, iPowerPollution, iPopulationPollution);
	}
	if (gGameSummaryLogLevel >= 2)
	{
		logSASGameSummaryPlayerBonuses(ePlayer, iGameTurn, kPrevious);
		logSASGameSummaryAIVictoryStages(ePlayer, iGameTurn);
		logSASGameSummaryPolicies(ePlayer, iGameTurn);
		logSASGameSummaryEconomy(ePlayer, iGameTurn);
		logSASGameSummaryStatistics(ePlayer, iGameTurn);
		logSASGameSummaryEspionage(ePlayer, iGameTurn);
		logSASGameSummaryDemographics(ePlayer, iGameTurn);
		logSASGameSummaryAttitudes(ePlayer, iGameTurn);
		if (gGameSummaryLogLevel >= 3) logSASGameSummaryDiplomaticMemories(ePlayer, iGameTurn);
		logSASGameSummaryDiploStatus(ePlayer, iGameTurn);
		logSASGameSummaryUnitPosture(ePlayer, iGameTurn);
		logSASGameSummaryWorkers(ePlayer, iGameTurn);
		logSASGameSummaryExpansion(ePlayer, iGameTurn);
		logSASGameSummarySettlers(ePlayer, iGameTurn);
		logSASGameSummaryWorkedPlots(ePlayer, iGameTurn);
		logSASGameSummaryCities(ePlayer, iGameTurn);
	}
	kPrevious.bValid = true;
	kPrevious.iScore = iScore;
	kPrevious.iCities = iCities;
	kPrevious.iPopulation = iPopulation;
	kPrevious.iLand = iLand;
	kPrevious.iUnits = iUnits;
	kPrevious.iMilitaryUnits = iMilitaryUnits;
	kPrevious.iPower = iPower;
	kPrevious.iGold = iGold;
	kPrevious.iGoldRate = iGoldRate;
	kPrevious.iResearchRate = iResearchRate;
	if (gGameSummaryLogLevel >= 2)
	{
		int iBonusTypes = 0;
		int iBonusInstances = 0;
		int iBonusImports = 0;
		int iBonusExports = 0;
		FOR_EACH_ENUM(Bonus)
		{
			const int iAvailable = kPlayer.getNumAvailableBonuses(eLoopBonus);
			if (iAvailable > 0)
			{
				iBonusTypes++;
				iBonusInstances += iAvailable;
			}
			iBonusImports += kPlayer.getBonusImport(eLoopBonus);
			iBonusExports += kPlayer.getBonusExport(eLoopBonus);
		}
		kPrevious.iBonusTypes = iBonusTypes;
		kPrevious.iBonusInstances = iBonusInstances;
		kPrevious.iBonusImports = iBonusImports;
		kPrevious.iBonusExports = iBonusExports;
	}
	kPrevious.iHistoryScore = iHistoryScore;
	kPrevious.iHistoryEconomy = iHistoryEconomy;
	kPrevious.iHistoryIndustry = iHistoryIndustry;
	kPrevious.iHistoryAgriculture = iHistoryAgriculture;
	kPrevious.iHistoryPower = iHistoryPower;
	kPrevious.iHistoryCulture = iHistoryCulture;
	kPrevious.iHistoryEspionage = iHistoryEspionage;
}

static void logSASGameSummarySnapshot(int iGameTurn, char const* szReason)
{
	CvGame const& kGame = GC.getGame();
	logSASGameSummary("GAME_SUMMARY_TURN_BEGIN turn=%d reason=%s elapsed=%d year=%d playersAlive=%d teamsAlive=%d totalCities=%d totalPopulation=%d",
			iGameTurn, szReason, kGame.getElapsedGameTurns(), kGame.getGameTurnYear(), kGame.countCivPlayersAlive(), kGame.countCivTeamsAlive(), kGame.getNumCities(), kGame.getTotalPopulation());
	logSASGameSummaryRunStatus(szReason);
	if (gGameSummaryLogLevel >= 2)
	{
		logSASGameSummaryMapBonusTotals(iGameTurn);
		logSASGameSummaryEnvironment(iGameTurn);
		logSASGameSummaryVoteSources(iGameTurn);
	}
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		if (GET_PLAYER(eLoopPlayer).isAlive() && !GET_PLAYER(eLoopPlayer).isBarbarian())
			logSASGameSummaryPlayerSnapshot(eLoopPlayer, iGameTurn);
	}
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (GET_TEAM(eLoopTeam).isAlive() && !GET_TEAM(eLoopTeam).isBarbarian())
			logSASGameSummaryTeamSnapshot(eLoopTeam, iGameTurn);
	}
	if (gGameSummaryLogLevel >= 2) logSASGameSummaryBattleBuckets(iGameTurn);
	logSASGameSummary("GAME_SUMMARY_TURN_END turn=%d reason=%s", iGameTurn, szReason);
	g_iSASGameSummaryLastFullSnapshotTurn = iGameTurn;
}

void logSASGameSummaryTurn(int iGameTurn)
{
	// <!-- custom: Victory now forces a full snapshot immediately. If it occurs on an ordinary snapshot turn, do not repeat the same large snapshot again at end-of-turn. (GPT-5.6-Sol) -->
	if (g_iSASGameSummaryLastFullSnapshotTurn == iGameTurn)
		return;
	logSASGameSummarySnapshot(iGameTurn, "interval");
}

void updateSASGameSummaryPlayerTurnState(PlayerTypes ePlayer)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	if (kPlayer.getGoldenAgeTurns() > 0)
		g_aiSASGameSummaryTotalGoldenAgeTurns[ePlayer]++;
	if (kPlayer.getAnarchyTurns() > 0)
		g_aiSASGameSummaryTotalAnarchyTurns[ePlayer]++;
}


static void countSASGameSummaryVisibleEnemiesNearPlot(CvPlot const& kCenter, PlayerTypes ePlayer, int iRange, int& iVisibleEnemies, int& iVisibleCombatEnemies, CvUnit const*& pNearestEnemy, int& iNearestEnemyDistance)
{
	iVisibleEnemies = 0;
	iVisibleCombatEnemies = 0;
	pNearestEnemy = NULL;
	iNearestEnemyDistance = -1;
	if (ePlayer == NO_PLAYER)
		return;
	TeamTypes const eTeam = GET_PLAYER(ePlayer).getTeam();
	for (int iDX = -iRange; iDX <= iRange; iDX++)
	{
		for (int iDY = -iRange; iDY <= iRange; iDY++)
		{
			CvPlot const* pLoopPlot = plotXY(kCenter.getX(), kCenter.getY(), iDX, iDY);
			if (pLoopPlot == NULL || !pLoopPlot->isVisible(eTeam, false))
				continue;
			for (CLLNode<IDInfo> const* pUnitNode = pLoopPlot->headUnitNode(); pUnitNode != NULL; pUnitNode = pLoopPlot->nextUnitNode(pUnitNode))
			{
				CvUnit const* pLoopUnit = ::getUnit(pUnitNode->m_data);
				if (pLoopUnit == NULL || !pLoopUnit->isEnemy(eTeam, kCenter) || pLoopUnit->isInvisible(eTeam, false))
					continue;
				iVisibleEnemies++;
				if (pLoopUnit->baseCombatStr() > 0 || pLoopUnit->canAttack())
					iVisibleCombatEnemies++;
				int const iDistance = plotDistance(kCenter.getX(), kCenter.getY(), pLoopPlot->getX(), pLoopPlot->getY());
				if (iNearestEnemyDistance < 0 || iDistance < iNearestEnemyDistance)
				{
					iNearestEnemyDistance = iDistance;
					pNearestEnemy = pLoopUnit;
				}
			}
		}
	}
}

static void logSASGameSummaryCityUnits(CvCity const& kCity, char const* szReason)
{
	SASGameSummaryPlotUnitCounts kCounts;
	collectSASGameSummaryPlotUnitCounts(kCity.getPlot(), kCity.getOwner(), kCounts);
	int iVisibleEnemies = 0;
	int iVisibleCombatEnemies = 0;
	int iNearestEnemyDistance = -1;
	CvUnit const* pNearestEnemy = NULL;
	countSASGameSummaryVisibleEnemiesNearPlot(kCity.getPlot(), kCity.getOwner(), 2, iVisibleEnemies, iVisibleCombatEnemies, pNearestEnemy, iNearestEnemyDistance);
	CvCity const* pNearestOtherOwnCity = NULL;
	int iNearestOtherOwnCityDistance = -1;
	int iCityLoop = 0;
	for (CvCity const* pLoopCity = GET_PLAYER(kCity.getOwner()).firstCity(&iCityLoop); pLoopCity != NULL; pLoopCity = GET_PLAYER(kCity.getOwner()).nextCity(&iCityLoop))
	{
		if (pLoopCity->getID() == kCity.getID())
			continue;
		int const iDistance = plotDistance(kCity.getX(), kCity.getY(), pLoopCity->getX(), pLoopCity->getY());
		if (iNearestOtherOwnCityDistance < 0 || iDistance < iNearestOtherOwnCityDistance)
		{
			iNearestOtherOwnCityDistance = iDistance;
			pNearestOtherOwnCity = pLoopCity;
		}
	}
	logSASGameSummary("GAME_SUMMARY_CITY_UNITS turn=%d reason=%s player=%d cityId=%d city=%S x=%d y=%d pop=%d ownerUnits=%d militaryUnits=%d civilianUnits=%d defenders=%d healthyDefenders=%d woundedDefenders=%d settlers=%d workers=%d attackers=%d bestDefenderId=%d bestDefenderUnit=%s bestDefenderAI=%s bestDefenderDamage=%d visibleEnemiesR2=%d visibleCombatEnemiesR2=%d nearestEnemyPlayer=%d nearestEnemyUnit=%s nearestEnemyDist=%d nearestOtherOwnCityId=%d nearestOtherOwnCity=%S nearestOtherOwnCityDistance=%d",
		GC.getGame().getGameTurn(), szReason, kCity.getOwner(), kCity.getID(), getSASGameSummaryQuotedCityName(&kCity).GetCString(), kCity.getX(), kCity.getY(), kCity.getPopulation(), kCounts.iUnits, kCounts.iMilitaryUnits, kCounts.iCivilianUnits, kCounts.iDefenders, kCounts.iHealthyDefenders, kCounts.iWoundedDefenders, kCounts.iSettlers, kCounts.iWorkers, kCounts.iAttackers, (kCounts.pBestDefender == NULL ? -1 : kCounts.pBestDefender->getID()), (kCounts.pBestDefender == NULL ? "-" : getSASGameSummaryUnitType(kCounts.pBestDefender->getUnitType())), (kCounts.pBestDefender == NULL ? "-" : getSASGameSummaryUnitAIType(kCounts.pBestDefender->AI_getUnitAIType())), (kCounts.pBestDefender == NULL ? -1 : kCounts.pBestDefender->getDamage()), iVisibleEnemies, iVisibleCombatEnemies, (pNearestEnemy == NULL ? -1 : pNearestEnemy->getOwner()), (pNearestEnemy == NULL ? "-" : getSASGameSummaryUnitType(pNearestEnemy->getUnitType())), iNearestEnemyDistance, (pNearestOtherOwnCity == NULL ? -1 : pNearestOtherOwnCity->getID()), getSASGameSummaryQuotedCityName(pNearestOtherOwnCity).GetCString(), iNearestOtherOwnCityDistance);
}

static bool logSASGameSummarySettlerCombatForPlot(CvUnit const* pWinner, CvUnit const* pLoser, CvPlot const* pPlot, PlayerTypes eSettlerOwner, bool bLoserWasSettler, bool bWinnerWasSettler)
{
	if (pWinner == NULL || pLoser == NULL || pPlot == NULL || eSettlerOwner == NO_PLAYER)
		return false;
	SASGameSummaryPlotUnitCounts kCounts;
	collectSASGameSummaryPlotUnitCounts(*pPlot, eSettlerOwner, kCounts);
	if (kCounts.iSettlers <= 0 && !bLoserWasSettler && !bWinnerWasSettler)
		return false;
	CvUnit const* pSettler = (bLoserWasSettler ? pLoser : (bWinnerWasSettler ? pWinner : kCounts.pFirstSettler));
	CvSelectionGroup const* pSettlerGroup = (pSettler == NULL ? NULL : pSettler->getGroup());
	int iGroupUnits = 0;
	int iGroupDefenders = 0;
	int iGroupSettlers = 0;
	if (pSettlerGroup != NULL)
	{
		FOR_EACH_UNIT_IN(pLoopUnit, *pSettlerGroup)
		{
			iGroupUnits++;
			if (isSASGameSummarySettlerUnit(*pLoopUnit))
				iGroupSettlers++;
			if (pLoopUnit->canDefend(pLoopUnit->plot()))
				iGroupDefenders++;
		}
	}
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=SETTLER_GROUP_ATTACKED settlerOwner=%d settlerId=%d settlerUnit=%s x=%d y=%d cityPlot=%d winnerPlayer=%d winnerUnitId=%d winnerUnit=%s winnerAI=%s winnerBaseStr=%d winnerDamage=%d loserPlayer=%d loserUnitId=%d loserUnit=%s loserAI=%s loserBaseStr=%d loserDamage=%d loserWasSettler=%d winnerWasSettler=%d ownerUnitsOnPlot=%d militaryUnitsOnPlot=%d civilianUnitsOnPlot=%d settlersOnPlot=%d defendersOnPlot=%d healthyDefendersOnPlot=%d workersOnPlot=%d settlerGroupId=%d settlerGroupUnits=%d settlerGroupSettlers=%d settlerGroupDefenders=%d",
		GC.getGame().getGameTurn(), eSettlerOwner, (pSettler == NULL ? -1 : pSettler->getID()), (pSettler == NULL ? "-" : getSASGameSummaryUnitType(pSettler->getUnitType())), pPlot->getX(), pPlot->getY(), pPlot->isCity(), pWinner->getOwner(), pWinner->getID(), getSASGameSummaryUnitType(pWinner->getUnitType()), getSASGameSummaryUnitAIType(pWinner->AI_getUnitAIType()), pWinner->baseCombatStr(), pWinner->getDamage(), pLoser->getOwner(), pLoser->getID(), getSASGameSummaryUnitType(pLoser->getUnitType()), getSASGameSummaryUnitAIType(pLoser->AI_getUnitAIType()), pLoser->baseCombatStr(), pLoser->getDamage(), bLoserWasSettler, bWinnerWasSettler, kCounts.iUnits, kCounts.iMilitaryUnits, kCounts.iCivilianUnits, kCounts.iSettlers, kCounts.iDefenders, kCounts.iHealthyDefenders, kCounts.iWorkers, (pSettlerGroup == NULL ? -1 : pSettlerGroup->getID()), iGroupUnits, iGroupSettlers, iGroupDefenders);
	return true;
}

static void logSASGameSummarySettlerCombatIfNeeded(CvUnit const* pWinner, CvUnit const* pLoser)
{
	if (pWinner == NULL || pLoser == NULL)
		return;
	bool const bLoserWasSettler = isSASGameSummarySettlerUnit(*pLoser);
	bool const bWinnerWasSettler = isSASGameSummarySettlerUnit(*pWinner);
	if (bLoserWasSettler && logSASGameSummarySettlerCombatForPlot(pWinner, pLoser, pLoser->plot(), pLoser->getOwner(), true, bWinnerWasSettler))
		return;
	if (bWinnerWasSettler && logSASGameSummarySettlerCombatForPlot(pWinner, pLoser, pWinner->plot(), pWinner->getOwner(), bLoserWasSettler, true))
		return;
	if (logSASGameSummarySettlerCombatForPlot(pWinner, pLoser, pLoser->plot(), pLoser->getOwner(), false, false))
		return;
	logSASGameSummarySettlerCombatForPlot(pWinner, pLoser, pWinner->plot(), pWinner->getOwner(), false, false);
}

// <!-- custom: GAME_SUMMARY_ACTION is narrower than a generic row: it records chronological gameplay happenings such as techs, city ownership, war state, Great People, unit upgrades, and victory. Do not rename this to GAME_SUMMARY_ROW; "row" is too generic because every log line is already a row. This keeps the row type useful without using "event", which can be confused with Civ4 EventInfo/random events. (GPT-5.5) -->
void logSASGameSummaryTechAcquired(TechTypes eType, TeamTypes eTeam, PlayerTypes ePlayer)
{
	CvTechInfo const& kTech = GC.getInfo(eType);
	// <!-- custom: The acquisition turn already gives the exact chronology. Mark technologies that enable tech or gold trading, while team snapshots state whether each capability is currently available. (GPT-5.6-Sol) -->
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=TECH_ACQUIRED player=%d team=%d tech=%s enablesTechTrading=%d enablesGoldTrading=%d", GC.getGame().getGameTurn(), ePlayer, eTeam, getSASGameSummaryTechType(eType), kTech.isTechTrading(), kTech.isGoldTrading());
}

void logSASGameSummaryCityBuilt(CvCity const* pCity)
{
	if (pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=CITY_BUILT player=%d cityId=%d city=%S x=%d y=%d pop=%d",
			GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), pCity->getX(), pCity->getY(), pCity->getPopulation());
	if (gGameSummaryLogLevel >= 2)
	{
		logSASGameSummaryCityBFC(*pCity, "built");
		logSASGameSummaryCityUnits(*pCity, "built");
	}
}

void logSASGameSummaryCityRazed(CvCity const* pCity, PlayerTypes ePlayer)
{
	if (pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=CITY_RAZED player=%d oldOwner=%d cityId=%d city=%S x=%d y=%d pop=%d",
			GC.getGame().getGameTurn(), ePlayer, pCity->getOwner(), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), pCity->getX(), pCity->getY(), pCity->getPopulation());
}

void logSASGameSummaryCityAcquired(PlayerTypes eOldOwner, PlayerTypes eNewOwner, CvCity const* pCity, bool bConquest, bool bTrade)
{
	if (pCity == NULL)
		return;
	if (eNewOwner >= 0 && eNewOwner < MAX_PLAYERS)
	{
		g_aiSASGameSummaryCitiesAcquired[eNewOwner]++;
		if (bConquest)
			g_aiSASGameSummaryCitiesConquered[eNewOwner]++;
		if (bTrade)
			g_aiSASGameSummaryCitiesTradedIn[eNewOwner]++;
	}
	if (eOldOwner >= 0 && eOldOwner < MAX_PLAYERS)
	{
		g_aiSASGameSummaryCitiesLost[eOldOwner]++;
		if (bConquest)
			g_aiSASGameSummaryCitiesLostByConquest[eOldOwner]++;
		if (bTrade)
			g_aiSASGameSummaryCitiesTradedOut[eOldOwner]++;
	}
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=CITY_ACQUIRED oldOwner=%d newOwner=%d cityId=%d city=%S x=%d y=%d pop=%d conquest=%d trade=%d",
			GC.getGame().getGameTurn(), eOldOwner, eNewOwner, pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), pCity->getX(), pCity->getY(), pCity->getPopulation(), bConquest, bTrade);
	if (gGameSummaryLogLevel >= 2)
	{
		logSASGameSummaryCityBFC(*pCity, "acquired");
		logSASGameSummaryCityUnits(*pCity, "acquired");
	}
}

void logSASGameSummaryWarStarted(TeamTypes eDeclarer, TeamTypes eTarget, WarPlanTypes eWarPlan, bool bPrimaryDoW, bool bNewDiplo, PlayerTypes eSponsor, bool bRandomEvent, WarDeclarationCause eCause)
{
	CvTeam const& kDeclarer = GET_TEAM(eDeclarer);
	CvTeam const& kTarget = GET_TEAM(eTarget);
	CvTeamAI const& kTargetAI = GET_TEAM(eTarget);
	char const* szCause = (bRandomEvent ? "RANDOM_EVENT" : (eSponsor != NO_PLAYER ? "SPONSORED_WAR" : getSASWarDeclarationCause(eCause)));
	// <!-- custom: `cause=DIRECT` identifies how war began, not why the AI selected that rival.
	// Preserve the target's exact victory state at declaration time so archived summaries show whether victory denial was relevant without falsely claiming it was the sole strategic motive. (GPT-5.6-Sol) -->
	int const iTargetMaxVictoryStage = getSASTeamMaxVictoryStage(eTarget);
	int const iTargetSpaceVictoryStage = getSASTeamSpaceVictoryStage(eTarget);
	int const iTargetSpaceshipParts = getSASTeamSpaceshipPartsBuilt(eTarget);
	int const iSpaceshipPartsRequired = getSASSpaceshipPartsRequired();
	int const iTargetSpaceshipPartsPercent = (iSpaceshipPartsRequired <= 0 ? 0 : iTargetSpaceshipParts * 100 / iSpaceshipPartsRequired);
	int const iTargetVictoryCountdown = kTargetAI.AI_getLowestVictoryCountdown();
	bool const bVictoryDenialContext = (iTargetVictoryCountdown >= 0 || iTargetMaxVictoryStage >= 4 || isSASTeamStage3SpaceVictoryThreat(eTarget));
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=WAR_STARTED declarerTeam=%d targetTeam=%d cause=%s primary=%d newDiplo=%d warPlan=%s sponsorPlayer=%d sponsorTeam=%d randomEvent=%d declarerMaster=%d targetMaster=%d declarerWarsAfter=%d targetWarsAfter=%d victoryDenialContext=%d targetMaxVictoryStage=%d targetSpaceVictoryStage=%d targetSpaceshipParts=%d targetSpaceshipPartsPercent=%d targetVictoryCountdown=%d",
			GC.getGame().getGameTurn(), eDeclarer, eTarget, szCause, bPrimaryDoW, bNewDiplo, getSASWarPlanType(eWarPlan),
			eSponsor, eSponsor == NO_PLAYER ? NO_TEAM : GET_PLAYER(eSponsor).getTeam(), bRandomEvent,
			kDeclarer.isAVassal() ? kDeclarer.getMasterTeam() : NO_TEAM, kTarget.isAVassal() ? kTarget.getMasterTeam() : NO_TEAM, kDeclarer.getNumWars(false), kTarget.getNumWars(false),
			bVictoryDenialContext, iTargetMaxVictoryStage, iTargetSpaceVictoryStage, iTargetSpaceshipParts, iTargetSpaceshipPartsPercent, iTargetVictoryCountdown);
}

void logSASGameSummaryWarEnded(TeamTypes eTeam, TeamTypes eOtherTeam)
{
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=WAR_ENDED teamA=%d teamB=%d teamAWarsAfter=%d teamBWarsAfter=%d", GC.getGame().getGameTurn(), eTeam, eOtherTeam, GET_TEAM(eTeam).getNumWars(false), GET_TEAM(eOtherTeam).getNumWars(false));
}

void logSASGameSummaryTeamMet(TeamTypes eTeam, TeamTypes eOtherTeam, bool bNewDiplo, int iX1, int iY1, int iX2, int iY2, CvPlot const* pTeamContactPlot, CvPlot const* pOtherContactPlot)
{
	const bool bMeetDataPlot1Valid = (iX1 >= 0 && iY1 >= 0 && iX1 < GC.getMap().getGridWidth() && iY1 < GC.getMap().getGridHeight());
	const bool bMeetDataPlot2Valid = (iX2 >= 0 && iY2 >= 0 && iX2 < GC.getMap().getGridWidth() && iY2 < GC.getMap().getGridHeight());
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=TEAM_MET team=%d otherTeam=%d bNewDiplo=%d teamMembers=%s otherMembers=%s meetDataPlot1=%d,%d meetDataPlot1Valid=%d meetDataPlot2=%d,%d meetDataPlot2Valid=%d teamContactPlot=%d,%d otherTeamContactPlot=%d,%d",
			GC.getGame().getGameTurn(), eTeam, eOtherTeam, bNewDiplo, getSASGameSummaryTeamMembers(eTeam).GetCString(), getSASGameSummaryTeamMembers(eOtherTeam).GetCString(), iX1, iY1, bMeetDataPlot1Valid, iX2, iY2, bMeetDataPlot2Valid, pTeamContactPlot == NULL ? -1 : pTeamContactPlot->getX(), pTeamContactPlot == NULL ? -1 : pTeamContactPlot->getY(), pOtherContactPlot == NULL ? -1 : pOtherContactPlot->getX(), pOtherContactPlot == NULL ? -1 : pOtherContactPlot->getY());
}

void logSASGameSummaryPlayerGoldTrade(PlayerTypes eFromPlayer, PlayerTypes eToPlayer, int iAmount)
{
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GOLD_TRADE from=%d to=%d amount=%d", GC.getGame().getGameTurn(), eFromPlayer, eToPlayer, iAmount);
}

void logSASGameSummaryReligionFounded(ReligionTypes eReligion, PlayerTypes ePlayer)
{
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=RELIGION_FOUNDED player=%d religion=%s", GC.getGame().getGameTurn(), ePlayer, getSASGameSummaryReligionType(eReligion));
}

void logSASGameSummaryCorporationFounded(CorporationTypes eCorporation, PlayerTypes ePlayer)
{
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=CORPORATION_FOUNDED player=%d corporation=%s", GC.getGame().getGameTurn(), ePlayer, getSASGameSummaryCorporationType(eCorporation));
}

void logSASGameSummaryGoldenAge(PlayerTypes ePlayer, bool bStart)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=%s player=%d goldenAgeTurns=%d totalGoldenAgeTurns=%d anarchyTurns=%d totalAnarchyTurns=%d", GC.getGame().getGameTurn(), bStart ? "GOLDEN_AGE_STARTED" : "GOLDEN_AGE_ENDED", ePlayer, kPlayer.getGoldenAgeTurns(), g_aiSASGameSummaryTotalGoldenAgeTurns[ePlayer], kPlayer.getAnarchyTurns(), g_aiSASGameSummaryTotalAnarchyTurns[ePlayer]);
}

void logSASGameSummaryGoldenAgeTurnsChanged(PlayerTypes ePlayer, int iChange, int iOldGoldenAgeTurns, int iNewGoldenAgeTurns)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GOLDEN_AGE_TURNS_CHANGED player=%d change=%+d oldGoldenAgeTurns=%d newGoldenAgeTurns=%d goldenAgeTurns=%d totalGoldenAgeTurns=%d anarchyTurns=%d totalAnarchyTurns=%d", GC.getGame().getGameTurn(), ePlayer, iChange, iOldGoldenAgeTurns, iNewGoldenAgeTurns, kPlayer.getGoldenAgeTurns(), g_aiSASGameSummaryTotalGoldenAgeTurns[ePlayer], kPlayer.getAnarchyTurns(), g_aiSASGameSummaryTotalAnarchyTurns[ePlayer]);
}

void logSASGameSummaryAnarchy(PlayerTypes ePlayer, bool bStart)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=%s player=%d anarchyTurns=%d totalAnarchyTurns=%d goldenAgeTurns=%d totalGoldenAgeTurns=%d revolutionTimer=%d conversionTimer=%d", GC.getGame().getGameTurn(), bStart ? "ANARCHY_STARTED" : "ANARCHY_ENDED", ePlayer, kPlayer.getAnarchyTurns(), g_aiSASGameSummaryTotalAnarchyTurns[ePlayer], kPlayer.getGoldenAgeTurns(), g_aiSASGameSummaryTotalGoldenAgeTurns[ePlayer], kPlayer.getRevolutionTimer(), kPlayer.getConversionTimer());
}

void logSASGameSummaryBuildingBuilt(CvCity const* pCity, BuildingTypes eBuilding)
{
	if (pCity == NULL || eBuilding == NO_BUILDING || !GC.getInfo(eBuilding).isLimited())
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=WONDER_BUILT player=%d cityId=%d city=%S building=%s", GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), getSASGameSummaryBuildingType(eBuilding));
}

void logSASGameSummaryProjectBuilt(CvCity const* pCity, ProjectTypes eProject)
{
	if (pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=PROJECT_BUILT player=%d cityId=%d city=%S project=%s", GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), getSASGameSummaryProjectType(eProject));
}

void logSASGameSummaryProductionOverflow(CvCity const* pCity, int iRawModifiedOverflow, int iUnmodifiedOverflow, int iKeptOverflow, int iLostProduction, int iUnusedCapacity, int iGold)
{
	if (pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=PRODUCTION_OVERFLOW player=%d cityId=%d city=%S productionKind=%s production=%s rawModifiedOverflow=%d unmodifiedOverflow=%d keptOverflow=%d lostProduction=%d unusedOverflowCapacity=%d gold=%d", GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), getSASGameSummaryCityProductionKind(*pCity), getSASGameSummaryCityProductionType(*pCity), iRawModifiedOverflow, iUnmodifiedOverflow, iKeptOverflow, iLostProduction, iUnusedCapacity, iGold);
}

void logSASGameSummaryProductionFailed(CvCity const* pCity, int iOrderData, bool bProject, int iInvestedProduction, int iGold)
{
	if (pCity == NULL)
		return;
	char const* szProduction = (bProject ? GC.getInfo((ProjectTypes)iOrderData).getType() : getSASGameSummaryBuildingType((BuildingTypes)iOrderData));
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=PRODUCTION_FAILED_TO_GOLD player=%d cityId=%d city=%S productionKind=%s production=%s investedProduction=%d gold=%d", GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), bProject ? "PROJECT" : "BUILDING", szProduction, iInvestedProduction, iGold);
}

void logSASGameSummaryVictoryLaunched(PlayerTypes ePlayer, VictoryTypes eVictory)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS || eVictory == NO_VICTORY)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvTeam const& kTeam = GET_TEAM(kPlayer.getTeam());
	int iPartsBuilt = 0;
	int iPartsMinimum = 0;
	int iPartsMaximum = 0;
	bool bMinimumComplete = false;
	CvString szProjectParts;
	bool const bProjectVictory = getSASGameSummaryVictoryProjectState(kPlayer.getTeam(), eVictory, iPartsBuilt, iPartsMinimum, iPartsMaximum, bMinimumComplete, szProjectParts);
	int const iCountdown = kTeam.getVictoryCountdown(eVictory);
	// <!-- custom: PROJECT_BUILT rows could only imply a spaceship launch. Record the actual launch and its exact arrival state so a Space victory no longer has to be reconstructed from component timing. (GPT-5.6-Sol) -->
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=SPACESHIP_LAUNCHED player=%d team=%d victory=%s countdown=%d arrivalTurn=%d travelTurns=%d launchSuccessPercent=%d partsBuilt=%d partsMinimum=%d partsMaximum=%d projectParts=%s",
			GC.getGame().getGameTurn(), ePlayer, kPlayer.getTeam(), GC.getInfo(eVictory).getType(), iCountdown, iCountdown < 0 ? -1 : GC.getGame().getGameTurn() + iCountdown, bProjectVictory && bMinimumComplete ? kTeam.getVictoryDelay(eVictory) : -1, kTeam.getLaunchSuccessRate(eVictory), iPartsBuilt, iPartsMinimum, iPartsMaximum, bProjectVictory ? szProjectParts.GetCString() : "-");
}

static void logSASGameSummaryVictoryProgressRemoved(TeamTypes eTeam, VictoryTypes eVictory, char const* szAction, char const* szCause, int iLaunchSuccessPercent, CvCity const* pCapital)
{
	CvTeam const& kTeam = GET_TEAM(eTeam);
	int iPartsBuilt = 0;
	int iPartsMinimum = 0;
	int iPartsMaximum = 0;
	bool bMinimumComplete = false;
	CvString szProjectParts;
	bool const bProjectVictory = getSASGameSummaryVictoryProjectState(eTeam, eVictory, iPartsBuilt, iPartsMinimum, iPartsMaximum, bMinimumComplete, szProjectParts);
	int const iCountdown = kTeam.getVictoryCountdown(eVictory);
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=%s team=%d victory=%s cause=%s countdown=%d arrivalTurn=%d launchSuccessPercent=%d capitalPlayer=%d capitalCityId=%d capital=%S capitalX=%d capitalY=%d projectVictory=%d partsBuilt=%d partsMinimum=%d partsMaximum=%d projectParts=%s",
			GC.getGame().getGameTurn(), szAction, eTeam, getSASGameSummaryVictoryType(eVictory), szCause, iCountdown, iCountdown < 0 ? -1 : GC.getGame().getGameTurn() + iCountdown,
			iLaunchSuccessPercent, pCapital == NULL ? NO_PLAYER : pCapital->getOwner(), pCapital == NULL ? -1 : pCapital->getID(), getSASGameSummaryQuotedCityName(pCapital).GetCString(), pCapital == NULL ? -1 : pCapital->getX(), pCapital == NULL ? -1 : pCapital->getY(),
			bProjectVictory, iPartsBuilt, iPartsMinimum, iPartsMaximum, bProjectVictory ? szProjectParts.GetCString() : "-");
}

void logSASGameSummaryVictoryProgressResetForCapital(CvCity const* pCapital)
{
	if (pCapital == NULL || GC.getGame().getGameState() != GAMESTATE_ON)
		return;
	TeamTypes const eTeam = pCapital->getTeam();
	CvTeam const& kTeam = GET_TEAM(eTeam);
	FOR_EACH_ENUM(Victory)
	{
		if (kTeam.getVictoryCountdown(eLoopVictory) >= 0)
			logSASGameSummaryVictoryProgressRemoved(eTeam, eLoopVictory, "VICTORY_PROGRESS_RESET", "CAPITAL_LOST", kTeam.getLaunchSuccessRate(eLoopVictory), pCapital);
	}
}

void logSASGameSummarySpaceshipFailed(TeamTypes eTeam, VictoryTypes eVictory, int iLaunchSuccessPercent)
{
	if (eTeam == NO_TEAM || eVictory == NO_VICTORY)
		return;
	// <!-- custom: A failed arrival roll previously erased the countdown and spaceship projects without an explicit event. Preserve the losing launch state immediately before resetVictoryProgress removes it. (GPT-5.6-Sol) -->
	logSASGameSummaryVictoryProgressRemoved(eTeam, eVictory, "SPACESHIP_FAILED", "LAUNCH_ROLL_FAILED", iLaunchSuccessPercent, NULL);
}

void logSASGameSummaryVassalState(TeamTypes eMaster, TeamTypes eVassal, bool bVassal)
{
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=%s master=%d vassal=%d", GC.getGame().getGameTurn(), bVassal ? "VASSALAGE_STARTED" : "VASSALAGE_ENDED", eMaster, eVassal);
}

void logSASGameSummaryVictory(TeamTypes eWinner, VictoryTypes eVictory)
{
	// <!-- custom: Victory can be reported before the ordinary end-turn hook. Flush this turn's buffered map history first so the final snapshot does not precede its last plot changes or map revelation. (GPT-5.6-Sol) -->
	if (gGameSummaryLogLevel >= 2) flushSASGameSummaryTurnChanges(GC.getGame().getGameTurn());
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=VICTORY team=%d victory=%s", GC.getGame().getGameTurn(), eWinner, eVictory == NO_VICTORY ? "-" : GC.getInfo(eVictory).getType());
	// <!-- custom: Periodic snapshots could stop several turns before victory, leaving every civilization's exact final state unknown. Force one complete marked snapshot now; the ordinary end-turn hook suppresses a duplicate on the same turn. (GPT-5.6-Sol) -->
	logSASGameSummarySnapshot(GC.getGame().getGameTurn(), "victory");
}

void logSASGameSummaryPlayerEliminated(PlayerTypes ePlayer)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=PLAYER_ELIMINATED player=%d team=%d civ=%s leader=%s cities=%d units=%d score=%d power=%d playersAlive=%d teamsAlive=%d eliminatedPlayers=%s",
			GC.getGame().getGameTurn(), ePlayer, kPlayer.getTeam(), kPlayer.getCivilizationType() == NO_CIVILIZATION ? "-" : GC.getInfo(kPlayer.getCivilizationType()).getType(), kPlayer.getLeaderType() == NO_LEADER ? "-" : GC.getInfo(kPlayer.getLeaderType()).getType(), kPlayer.getNumCities(), kPlayer.getNumUnits(), kPlayer.calculateScore(), kPlayer.getPower(), GC.getGame().countCivPlayersAlive(), GC.getGame().countCivTeamsAlive(), getSASGameSummaryEliminatedPlayers().GetCString());
	logSASGameSummaryRunStatus("playerEliminated");
}

void logSASGameSummaryPlayerAliveChanged(PlayerTypes ePlayer, bool bRevived)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=%s player=%d team=%d civ=%s leader=%s cities=%d units=%d score=%d power=%d playersAlive=%d teamsAlive=%d playersEverAlive=%d",
			GC.getGame().getGameTurn(), bRevived ? "PLAYER_REVIVED" : "PLAYER_APPEARED", ePlayer, kPlayer.getTeam(), kPlayer.getCivilizationType() == NO_CIVILIZATION ? "-" : GC.getInfo(kPlayer.getCivilizationType()).getType(), kPlayer.getLeaderType() == NO_LEADER ? "-" : GC.getInfo(kPlayer.getLeaderType()).getType(), kPlayer.getNumCities(), kPlayer.getNumUnits(), kPlayer.calculateScore(), kPlayer.getPower(), GC.getGame().countCivPlayersAlive(), GC.getGame().countCivTeamsAlive(), GC.getGame().countCivPlayersEverAlive());
	logSASGameSummaryRunStatus(bRevived ? "playerRevived" : "playerAppeared");
}

void logSASGameSummaryAutoPlayChanged(int iOldValue, int iNewValue, bool bChangePlayerStatus)
{
	if (iOldValue == iNewValue)
		return;
	CvGame const& kGame = GC.getGame();
	const char* szAction = (iOldValue <= 0 && iNewValue > 0 ? "AUTOPLAY_STARTED" : (iOldValue > 0 && iNewValue <= 0 ? "AUTOPLAY_ENDED" : "AUTOPLAY_CHANGED"));
	const PlayerTypes eActivePlayer = kGame.getActivePlayer();
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=%s oldTurnsLeft=%d newTurnsLeft=%d activePlayer=%d changePlayerStatus=%d",
			kGame.getGameTurn(), szAction, iOldValue, iNewValue, eActivePlayer, bChangePlayerStatus);
	logSASGameSummaryRunStatus(szAction);
}

void logSASGameSummaryGreatPersonBorn(CvUnit const* pUnit, PlayerTypes ePlayer, CvCity const* pCity)
{
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_BORN player=%d cityId=%d city=%S unit=%s combatXP=%d greatPeopleCreated=%d greatGeneralsCreated=%d greatGeneralThreshold=%d",
			GC.getGame().getGameTurn(), ePlayer, pCity == NULL ? -1 : pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), pUnit == NULL ? "-" : getSASGameSummaryUnitType(pUnit->getUnitType()), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).getCombatExperience(), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).getGreatPeopleCreated(), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).getGreatGeneralsCreated(), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).greatPeopleThreshold(true));
}

void logSASGameSummaryGreatPersonJoined(CvUnit const* pUnit, CvCity const* pCity, SpecialistTypes eSpecialist)
{
	if (pUnit == NULL || pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_JOINED_CITY player=%d unitId=%d unit=%s cityId=%d city=%S specialist=%s freeSpecialists=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), eSpecialist == NO_SPECIALIST ? "-" : GC.getInfo(eSpecialist).getType(), pCity->getFreeSpecialistCount(eSpecialist));
}

// <!-- custom: Great Person births and city joining were already recorded, but other completed Great Person missions disappeared from the summary when the unit was consumed. Record the rare completed outcome and its concrete gain without logging AI candidate values or reasoning. (GPT-5.6-Sol) -->
void logSASGameSummaryGreatPersonConstructed(CvUnit const* pUnit, CvCity const* pCity, BuildingTypes eBuilding)
{
	if (pUnit == NULL || pCity == NULL || eBuilding == NO_BUILDING)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_USED use=CONSTRUCT_BUILDING player=%d unitId=%d unit=%s cityId=%d city=%S building=%s",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), getSASGameSummaryBuildingType(eBuilding));
}

void logSASGameSummaryGreatPersonDiscovered(CvUnit const* pUnit, TechTypes eTech, int iResearch)
{
	if (pUnit == NULL || eTech == NO_TECH)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_USED use=DISCOVER_TECH player=%d unitId=%d unit=%s x=%d y=%d tech=%s research=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), pUnit->getX(), pUnit->getY(), getSASGameSummaryTechType(eTech), iResearch);
}

void logSASGameSummaryGreatPersonHurried(CvUnit const* pUnit, CvCity const* pCity, BuildingTypes eBuilding, int iProduction)
{
	if (pUnit == NULL || pCity == NULL || eBuilding == NO_BUILDING)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_USED use=HURRY_BUILDING player=%d unitId=%d unit=%s cityId=%d city=%S building=%s production=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), getSASGameSummaryBuildingType(eBuilding), iProduction);
}

void logSASGameSummaryGreatPersonTradeMission(CvUnit const* pUnit, CvCity const* pCity, int iGold)
{
	if (pUnit == NULL || pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_USED use=TRADE_MISSION player=%d unitId=%d unit=%s targetPlayer=%d cityId=%d city=%S gold=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), pCity->getOwner(), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), iGold);
}

void logSASGameSummaryGreatPersonGreatWork(CvUnit const* pUnit, CvCity const* pCity, int iCulture)
{
	if (pUnit == NULL || pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_USED use=GREAT_WORK player=%d unitId=%d unit=%s cityId=%d city=%S culture=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), iCulture);
}

void logSASGameSummaryGreatPersonInfiltrated(CvUnit const* pUnit, CvCity const* pCity, int iEspionage)
{
	if (pUnit == NULL || pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_USED use=INFILTRATE player=%d unitId=%d unit=%s targetPlayer=%d targetTeam=%d cityId=%d city=%S espionage=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), pCity->getOwner(), pCity->getTeam(), pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), iEspionage);
}

void logSASGameSummaryGreatPersonGoldenAgeConsumed(CvUnit const* pUnit)
{
	if (pUnit == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_USED use=GOLDEN_AGE player=%d unitId=%d unit=%s x=%d y=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), pUnit->getX(), pUnit->getY());
}

void logSASGameSummaryGreatPersonDied(CvUnit const* pUnit, PlayerTypes eResponsiblePlayer, char const* szCause)
{
	if (pUnit == NULL || (!pUnit->isGoldenAge() && pUnit->getUnitInfo().getLeaderExperience() <= 0))
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_DIED player=%d unitId=%d unit=%s x=%d y=%d cause=%s responsiblePlayer=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), pUnit->getX(), pUnit->getY(), szCause, eResponsiblePlayer);
}

// <!-- custom: Periodic espionage totals showed investment against each rival but not what those points accomplished. Record only completed missions and actual interceptions at game-summary level 2; mission selection and movement reasoning remain BBAI diagnostics. Resolve iExtraData to XML types so stolen technologies and sabotaged buildings/projects/units are readable. (GPT-5.6-Sol) -->
void logSASGameSummaryEspionageMission(CvUnit const* pUnit, EspionageMissionTypes eMission, PlayerTypes eTargetPlayer, CvPlot const* pPlot, int iExtraData, int iCost, int iEPBefore, int iEPAfter, ImprovementTypes eTargetImprovement, RouteTypes eTargetRoute, UnitTypes eTargetUnit, int iEffectValue, char const* szEffectKind)
{
	if (pUnit == NULL || eMission == NO_ESPIONAGEMISSION)
		return;
	CvEspionageMissionInfo const& kMission = GC.getInfo(eMission);
	char const* szTargetKind = "-";
	char const* szTargetType = "-";
	if (kMission.isDestroyImprovement())
	{
		if (eTargetImprovement != NO_IMPROVEMENT)
		{
			szTargetKind = "improvement";
			szTargetType = getSASGameSummaryImprovementType(eTargetImprovement);
		}
		else if (eTargetRoute != NO_ROUTE)
		{
			szTargetKind = "route";
			szTargetType = getSASGameSummaryRouteType(eTargetRoute);
		}
	}
	else if (kMission.getDestroyBuildingCostFactor() > 0)
	{
		szTargetKind = "building";
		szTargetType = getSASGameSummaryBuildingType((BuildingTypes)iExtraData);
	}
	else if (kMission.getDestroyProjectCostFactor() > 0)
	{
		szTargetKind = "project";
		szTargetType = getSASGameSummaryProjectType((ProjectTypes)iExtraData);
	}
	else if (kMission.getDestroyUnitCostFactor() > 0 || kMission.getBuyUnitCostFactor() > 0)
	{
		szTargetKind = "unit";
		szTargetType = getSASGameSummaryUnitType(eTargetUnit);
	}
	else if (kMission.getBuyTechCostFactor() > 0)
	{
		szTargetKind = "tech";
		szTargetType = getSASGameSummaryTechType((TechTypes)iExtraData);
	}
	else if (kMission.getSwitchCivicCostFactor() > 0)
	{
		szTargetKind = "civic";
		szTargetType = getSASGameSummaryCivicType((CivicTypes)iExtraData);
	}
	else if (kMission.getSwitchReligionCostFactor() > 0)
	{
		szTargetKind = "religion";
		szTargetType = getSASGameSummaryReligionType((ReligionTypes)iExtraData);
	}
	CvCity const* pCity = (pPlot == NULL ? NULL : pPlot->getPlotCity());
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=ESPIONAGE_MISSION player=%d spyId=%d spy=%s spyAI=%s targetPlayer=%d targetTeam=%d mission=%s cost=%d epBefore=%d epAfter=%d cityId=%d city=%S x=%d y=%d targetKind=%s target=%s effectKind=%s effectValue=%d extraData=%d fortifyTurns=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), getSASGameSummaryUnitAIType(pUnit->AI_getUnitAIType()), eTargetPlayer, eTargetPlayer == NO_PLAYER ? NO_TEAM : GET_PLAYER(eTargetPlayer).getTeam(), getSASGameSummaryEspionageMissionType(eMission), iCost, iEPBefore, iEPAfter, pCity == NULL ? -1 : pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), pPlot == NULL ? -1 : pPlot->getX(), pPlot == NULL ? -1 : pPlot->getY(), szTargetKind, szTargetType, szEffectKind, iEffectValue, iExtraData, pUnit->getFortifyTurns());
}

void logSASGameSummarySpyIntercepted(CvUnit const* pUnit, PlayerTypes eTargetPlayer, char const* szPhase, int iModifier, int iInterceptChanceX100)
{
	if (pUnit == NULL)
		return;
	CvCity const* pCity = pUnit->getPlot().getPlotCity();
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=SPY_INTERCEPTED player=%d spyId=%d spy=%s spyAI=%s targetPlayer=%d targetTeam=%d phase=%s x=%d y=%d cityId=%d city=%S modifier=%d interceptChanceX100=%d fortifyTurns=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), getSASGameSummaryUnitAIType(pUnit->AI_getUnitAIType()), eTargetPlayer, eTargetPlayer == NO_PLAYER ? NO_TEAM : GET_PLAYER(eTargetPlayer).getTeam(), szPhase, pUnit->getX(), pUnit->getY(), pCity == NULL ? -1 : pCity->getID(), getSASGameSummaryQuotedCityName(pCity).GetCString(), iModifier, iInterceptChanceX100, pUnit->getFortifyTurns());
}

void logSASGameSummaryGreatGeneralAttached(CvUnit const* pGreatGeneral, CvUnit const* pTargetUnit, PromotionTypes ePromotion)
{
	if (pGreatGeneral == NULL || pTargetUnit == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_GENERAL_ATTACHED player=%d generalUnitId=%d generalUnit=%s targetUnitId=%d targetUnit=%s targetUnitAI=%s x=%d y=%d promotion=%s targetXP=%d targetLevel=%d",
			GC.getGame().getGameTurn(), pGreatGeneral->getOwner(), pGreatGeneral->getID(), getSASGameSummaryUnitType(pGreatGeneral->getUnitType()), pTargetUnit->getID(), getSASGameSummaryUnitType(pTargetUnit->getUnitType()), getSASGameSummaryUnitAIType(pTargetUnit->AI_getUnitAIType()), pTargetUnit->getX(), pTargetUnit->getY(), ePromotion == NO_PROMOTION ? "-" : GC.getInfo(ePromotion).getType(), pTargetUnit->getExperience(), pTargetUnit->getLevel());
}


void logSASGameSummaryUnitScrapped(CvUnit const* pUnit)
{
	if (pUnit == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=UNIT_SCRAPPED player=%d unitId=%d unit=%s unitAI=%s x=%d y=%d damage=%d xp=%d level=%d age=%d cargo=%d cargoSpace=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), getSASGameSummaryUnitAIType(pUnit->AI_getUnitAIType()), pUnit->getX(), pUnit->getY(), pUnit->getDamage(), pUnit->getExperience(), pUnit->getLevel(), GC.getGame().getGameTurn() - pUnit->getGameTurnCreated(), pUnit->getCargo(), pUnit->cargoSpace());
}

void logSASGameSummaryUnitUpgraded(CvUnit const* pOldUnit, CvUnit const* pNewUnit, int iCost)
{
	if (pOldUnit == NULL || pNewUnit == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=UNIT_UPGRADED player=%d oldUnitId=%d newUnitId=%d fromUnit=%s toUnit=%s unitAI=%s x=%d y=%d cost=%d oldXP=%d newXP=%d oldLevel=%d newLevel=%d",
			GC.getGame().getGameTurn(), pOldUnit->getOwner(), pOldUnit->getID(), pNewUnit->getID(), getSASGameSummaryUnitType(pOldUnit->getUnitType()), getSASGameSummaryUnitType(pNewUnit->getUnitType()), getSASGameSummaryUnitAIType(pNewUnit->AI_getUnitAIType()), pNewUnit->getX(), pNewUnit->getY(), iCost, pOldUnit->getExperience(), pNewUnit->getExperience(), pOldUnit->getLevel(), pNewUnit->getLevel());
}

void logSASGameSummaryUnitCaptured(PlayerTypes eOldOwner, UnitTypes eOldUnitType, CvUnit const* pNewUnit)
{
	if (pNewUnit == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=UNIT_CAPTURED oldOwner=%d newOwner=%d oldUnit=%s newUnitId=%d newUnit=%s newUnitAI=%s x=%d y=%d",
			GC.getGame().getGameTurn(), eOldOwner, pNewUnit->getOwner(), getSASGameSummaryUnitType(eOldUnitType), pNewUnit->getID(), getSASGameSummaryUnitType(pNewUnit->getUnitType()), getSASGameSummaryUnitAIType(pNewUnit->AI_getUnitAIType()), pNewUnit->getX(), pNewUnit->getY());
}

void logSASGameSummaryCombatResult(CvUnit const* pWinner, CvUnit const* pLoser)
{
	if (pWinner == NULL || pLoser == NULL)
		return;
	if (gGameSummaryLogLevel > 0) logSASGameSummarySettlerCombatIfNeeded(pWinner, pLoser);
	PlayerTypes eWinner = pWinner->getOwner();
	PlayerTypes eLoser = pLoser->getOwner();
	CvPlot const* pPlot = pLoser->plot();
	const bool bCityPlot = (pPlot != NULL && pPlot->isCity());
	if (eWinner >= 0 && eWinner < MAX_PLAYERS)
	{
		g_aiSASGameSummaryBattleWins[eWinner]++;
		g_aiSASGameSummaryTotalBattleWins[eWinner]++;
		if (bCityPlot)
		{
			g_aiSASGameSummaryCityBattleWins[eWinner]++;
			g_aiSASGameSummaryTotalCityBattleWins[eWinner]++;
		}
	}
	if (eLoser >= 0 && eLoser < MAX_PLAYERS)
	{
		g_aiSASGameSummaryBattleLosses[eLoser]++;
		g_aiSASGameSummaryTotalBattleLosses[eLoser]++;
		if (bCityPlot)
		{
			g_aiSASGameSummaryCityBattleLosses[eLoser]++;
			g_aiSASGameSummaryTotalCityBattleLosses[eLoser]++;
		}
	}
	if (pLoser->getLeaderUnitType() != NO_UNIT)
	{
		logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_GENERAL_UNIT_DIED player=%d unitId=%d unit=%s attachedGreatGeneral=%s winnerPlayer=%d winnerUnitId=%d winnerUnit=%s x=%d y=%d",
				GC.getGame().getGameTurn(), eLoser, pLoser->getID(), getSASGameSummaryUnitType(pLoser->getUnitType()), getSASGameSummaryUnitType(pLoser->getLeaderUnitType()), eWinner, pWinner->getID(), getSASGameSummaryUnitType(pWinner->getUnitType()), pLoser->getX(), pLoser->getY());
	}
	logSASGameSummaryGreatPersonDied(pLoser, eWinner, "COMBAT");
	if (gGameSummaryLogLevel >= 3)
	{
		logSASGameSummary("GAME_SUMMARY_BATTLE turn=%d winner=%d loser=%d winnerUnit=%s loserUnit=%s x=%d y=%d cityPlot=%d winnerBaseStr=%d loserBaseStr=%d winnerDamage=%d loserDamage=%d winnerLeaderUnit=%s loserLeaderUnit=%s",
				GC.getGame().getGameTurn(), eWinner, eLoser, getSASGameSummaryUnitType(pWinner->getUnitType()), getSASGameSummaryUnitType(pLoser->getUnitType()), pLoser->getX(), pLoser->getY(), bCityPlot, pWinner->baseCombatStr(), pLoser->baseCombatStr(), pWinner->getDamage(), pLoser->getDamage(), getSASGameSummaryUnitType(pWinner->getLeaderUnitType()), getSASGameSummaryUnitType(pLoser->getLeaderUnitType()));
	}
}


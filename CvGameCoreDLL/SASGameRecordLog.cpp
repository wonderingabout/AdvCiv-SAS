#include "CvGameCoreDLL.h"
#include "SASGameRecordLog.h"
#include "CvGame.h" // <!-- custom: Needed for game-record turn, game-state, victory, RNG, and map-classification context rows. (GPT-5.5) -->
#include "CvCity.h" // <!-- custom: Needed by game-record city action/BFC rows; SASGameRecordLog.h only forward-declares CvCity. (GPT-5.5) -->
#include "CvUnit.h" // <!-- custom: Needed by game-record battle rows; SASGameRecordLog.h only forward-declares CvUnit. (GPT-5.5) -->
#include "CvUnitAI.h" // <!-- custom: Needed to inspect the head unit of large city groups and its UnitAI role; the base unit header only forward-declares CvUnitAI. (GPT-5.6-Sol) -->
#include "CityPlotIterator.h" // <!-- custom: Needed by compact game-record BFC composition rows. (ChatGPT-5.5) -->
#include "CvPlot.h" // <!-- custom: Needed by game-record BFC and unit posture rows. (ChatGPT-5.5) -->
#include "CvInfo_Build.h" // <!-- custom: Needed for worker build-type names and build target classification in game-record rows. (ChatGPT-5.5) -->
#include "CvInfo_Command.h" // <!-- custom: Needed for mission-type names in worker/settler game-record rows. (ChatGPT-5.5) -->
#include "CvInfo_Building.h" // <!-- custom: Needed to classify city production in game-record city rows. (ChatGPT-5.5) -->
#include "CvInfo_Tech.h" // <!-- custom: Needed to bucket owned-tech counts by era in game-record rows. (ChatGPT-5.5) -->
#include "CvInfo_Terrain.h" // <!-- custom: Needed for terrain/feature/bonus type names in game-record context rows. (ChatGPT-5.5) -->
#include "CvInfo_Organization.h" // <!-- custom: Needed for religion/corporation type names in game-record action rows. (ChatGPT-5.5) -->
#include "CvInfo_Unit.h" // <!-- custom: Needed to classify unit composition and city production in game-record rows. (ChatGPT-5.5) -->
#include "CvInfo_Symbol.h" // <!-- custom: Needed for commerce-slider type names in game-record economy rows. (GPT-5.5) -->
#include "CvInfo_City.h" // <!-- custom: Needed for specialist and process type names in game-record city rows. (ChatGPT-5.5) -->
#include "CvInfo_Civics.h" // <!-- custom: Needed for policy/civic names in game-record advisor rows. (ChatGPT-5.5) -->
#include "CvInfo_Civilization.h" // <!-- custom: Needed to attribute player-wide extra happiness/health to traits instead of leaving effects from loaded-mod rules under an opaque `extra` label. (GPT-5.6-Sol) -->
#include "CvInfo_GameOption.h" // <!-- custom: Needed to log enabled game-option type names; CvGlobals only forward-declares CvGameOptionInfo. (GPT-5.5) -->
#include "CvMap.h" // <!-- custom: Needed to log map dimensions; CvGlobals only forward-declares CvMap. (GPT-5.5) -->
#include "CvSelectionGroup.h" // <!-- custom: Needed to inspect worker/settler mission queues in game-record rows. (ChatGPT-5.5) -->
#include "CvSelectionGroupAI.h" // <!-- custom: Needed for large city-group mission targets and MissionAI state; the base group header only forward-declares CvSelectionGroupAI. (GPT-5.6-Sol) -->
#include "CvPlotGroup.h" // <!-- custom: Needed to identify connected city networks in game-record city rows. (ChatGPT-5.5) -->
#include "CvArea.h" // <!-- custom: Needed for area-wide city happiness/health detail rows. (ChatGPT-5.5) -->
#include "CvPlayerAI.h" // <!-- custom: Needed for attitude/glance values in game-record advisor rows. (ChatGPT-5.5) -->
#include "CvTeamAI.h" // <!-- custom: Needed for team-level worst-enemy state in game-record diplomacy-status rows. (ChatGPT-5.5) -->
#include "CvStatistics.h" // <!-- custom: Needed for persistent player-record statistics in game-record benchmark rows. (GPT-5.5) -->
#include <time.h>
#include <algorithm> // <!-- custom: Needed to deduplicate buffered plot-change/map-revelation coordinates within each turn. (GPT-5.6-Sol) -->
#include <utility> // <!-- custom: Needed for Great Person odds pairs in game-record city rows. (ChatGPT-5.5) -->
#include <vector> // <!-- custom: Used for compact dynamic buckets in game-record known-area, BFC development, advisor, tech-era, worker/settler, and unit-composition rows. (ChatGPT-5.5) -->

static int getClampedSASGameRecordLogLevel(char const* szDefineName)
{
	const int iLevel = GC.getDefineINT(szDefineName);
	if (iLevel < 0)
		return 0;
	if (iLevel > 3)
		return 3;
	return iLevel;
}

// <!-- custom: Dedicated structured game-record log for autoplay comparison, general game analysis, and external LLM review. This is independent from SAS_BBAI_LOG_ENABLE because it is a run-report artifact rather than classic AI-decision diagnostics, and writes to SASGameRecord_*.log when enabled. Use ACTION rows rather than EVENT rows to avoid confusion with Civ4 random events. (ChatGPT-5.5 + GPT-5.5) -->
int getSASGameRecordLogLevel()
{
	static const int iLevel = getClampedSASGameRecordLogLevel("SAS_GAME_RECORD_LOG_LEVEL");
	return iLevel;
}

bool isSASGameRecordLogEnabled()
{
	static const bool bEnabled = (getSASGameRecordLogLevel() > 0);
	return bEnabled;
}

int getSASGameRecordTurnInterval()
{
	// <!-- custom: Separate snapshot frequency from detail level. Level 0 disables the game-record rows; the interval is still clamped so modulo callers are safe. (ChatGPT-5.5) -->
	static const int iInterval = std::max(1, GC.getDefineINT("SAS_GAME_RECORD_INTERVAL_TURNS_UNSCALED_GAMESPEED"));
	return iInterval;
}

static CvString createSASGameRecordLogTimestamp()
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

static CvString g_szSASGameRecordLogTimestamp;
static int g_iSASGameRecordLogSequence = 0;
static CvString g_szSASGameRecordLogContext;
static void flushSASGameRecordPendingCityBombard();
static bool g_bSASGameRecordFlushingCityBombard = false;

static CvString getSASGameRecordLogTimestamp()
{
	if (g_szSASGameRecordLogTimestamp.empty())
		g_szSASGameRecordLogTimestamp = createSASGameRecordLogTimestamp();
	return g_szSASGameRecordLogTimestamp;
}

static bool isSASGameRecordTimestampedFilenameEnabled()
{
	static const bool bUseTimestampedFilename = (GC.getDefineINT("SAS_GAME_RECORD_LOG_USE_TIMESTAMPED_FILENAME") > 0);
	return bUseTimestampedFilename;
}

static CvString getSASGameRecordLogName()
{
	const bool bUseTimestampedFilename = isSASGameRecordTimestampedFilenameEnabled();
	CvString szLogName;
	if (GC.getGame().isNetworkMultiPlayer())
	{
		if (bUseTimestampedFilename)
		{
			if (!g_szSASGameRecordLogContext.empty())
				szLogName.Format("SASGameRecord%d_%s_%s.log", (int)GC.getGame().getActivePlayer(), getSASGameRecordLogTimestamp().GetCString(), g_szSASGameRecordLogContext.GetCString());
			else szLogName.Format("SASGameRecord%d_%s.log", (int)GC.getGame().getActivePlayer(), getSASGameRecordLogTimestamp().GetCString());
		}
		else szLogName.Format("SASGameRecord%d.log", (int)GC.getGame().getActivePlayer());
	}
	else
	{
		if (bUseTimestampedFilename)
		{
			if (!g_szSASGameRecordLogContext.empty())
				szLogName.Format("SASGameRecord_%s_%s.log", getSASGameRecordLogTimestamp().GetCString(), g_szSASGameRecordLogContext.GetCString());
			else szLogName.Format("SASGameRecord_%s.log", getSASGameRecordLogTimestamp().GetCString());
		}
		else szLogName = "SASGameRecord.log";
	}
	return szLogName;
}

static void rollSASGameRecordLog(const char* szContext)
{
	if (isSASGameRecordTimestampedFilenameEnabled())
	{
		g_szSASGameRecordLogTimestamp = createSASGameRecordLogTimestamp();
		g_iSASGameRecordLogSequence++;
		g_szSASGameRecordLogContext.Format("%s%d", szContext, g_iSASGameRecordLogSequence);
	}
}

static void logSASGameRecordFormattedLine(CvString const& szLogName, TCHAR* format, va_list args)
{
	static char buf[2048];
	_vsnprintf(buf, sizeof(buf) - 1, format, args);
	// <!-- custom: As with BBAI logging, guard this new game-record logger against MSVC 7.1 _vsnprintf leaving truncated output unterminated, which fixed rare logging/heap crash signatures. See KI#161.2. (ChatGPT-5.5 + GPT-5.5) -->
	buf[sizeof(buf) - 1] = '\0';
	gDLL->logMsg(szLogName.GetCString(), buf, false, false);
}

void logSASGameRecord(TCHAR* format, ... )
{
	static const bool bEnabled = isSASGameRecordLogEnabled();
	if (!bEnabled)
		return;
	// <!-- custom: CITY_BOMBARD is buffered only across consecutive equivalent actions. Flush it before the next ordinary GameRecord row so repeated siege clicks become one synthetic line without losing same-turn ordering relative to battles or other actions. (GPT-5.6 Thinking) -->
	if (!g_bSASGameRecordFlushingCityBombard)
		flushSASGameRecordPendingCityBombard();

	va_list args;
	va_start(args, format);
	logSASGameRecordFormattedLine(getSASGameRecordLogName(), format, args);
	va_end(args);
}

// <!-- custom: Quote free-text game-record values so simple key=value parsers do not split names such as "New York" or "De Gaulle" on spaces. Keep XML enum/type tags unquoted. Escape quotes, backslashes, and line separators so one log row remains one parseable row. (GPT-5.5) -->
static CvString getSASGameRecordQuoted(char const* szValue)
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

static CvWString getSASGameRecordQuoted(wchar const* szValue)
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

static CvWString getSASGameRecordQuotedCityName(CvCity const* pCity)
{
	return pCity == NULL ? L"-" : getSASGameRecordQuoted(pCity->getName().GetCString());
}

// <!-- custom: Use "row" wording for generic SAS game-record row prefixes because Civ4 also has EventInfo/random events. Keep GAME_RECORD_ACTION only for chronological gameplay action rows. (GPT-5.5) -->
static void logSASGameRecordGameState(const char* szRowType)
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
	const CvString szLogName = getSASGameRecordLogName();
	logSASGameRecord("%s utc=%s logFile=%s turn=%d elapsed=%d year=%d scenario=%d activePlayer=%d activeCivilization=%s activeHandicap=%s playersDefined=%d playersAlive=%d playersEverAlive=%d humans=%d",
			szRowType, getSASGameRecordLogTimestamp().GetCString(), getSASGameRecordQuoted(szLogName.GetCString()).GetCString(), kGame.getGameTurn(), kGame.getElapsedGameTurns(), kGame.getGameTurnYear(), kGame.isScenario(), eActivePlayer, szActiveCivilization, szActiveHandicap, kInitCore.getNumDefinedPlayers(), kGame.countCivPlayersAlive(), kGame.countCivPlayersEverAlive(), kGame.getNumHumanPlayers());
	// <!-- custom: Enabled victories and their fixed turn/score limits determine which later victory-progress and AI-strategy rows are relevant. Record this compact setup context instead of requiring external XML or save inspection. (GPT-5.6-Sol) -->
	logSASGameRecord("GAME_RECORD_GAME_SETTINGS mapScript=%S map=%dx%d landHeavy=%d navalHeavy=%d world=%s climate=%s seaLevel=%s gameSpeed=%s startEra=%s gameHandicap=%s maxTurns=%d targetScore=%d victories=%s options=%s",
			getSASGameRecordQuoted(kInitCore.getMapScriptName().GetCString()).GetCString(), GC.getMap().getGridWidth(), GC.getMap().getGridHeight(), kGame.isLandHeavyMapnameCached(), kGame.isNavalHeavyMapnameCached(), GC.getInfo(kInitCore.getWorldSize()).getType(), GC.getInfo(kInitCore.getClimate()).getType(), GC.getInfo(kInitCore.getSeaLevel()).getType(), GC.getInfo(kGame.getGameSpeedType()).getType(), GC.getInfo(kGame.getStartEra()).getType(), GC.getInfo(kGame.getHandicapType()).getType(), kGame.getMaxTurns(), kGame.getTargetScore(), szVictories.GetCString(), szGameOptions.GetCString());
	logSASGameRecord("GAME_RECORD_GAME_RNG mapRandState=%u syncRandState=%u", kGame.getMapRand().getSeed(), kGame.getSorenRand().getSeed());
}

static void logSASGameRecordLogSettings()
{
	logSASGameRecord("GAME_RECORD_LOG_SETTINGS SAS_GAME_RECORD_LOG_LEVEL=%d SAS_GAME_RECORD_INTERVAL_TURNS_UNSCALED_GAMESPEED=%d SAS_GAME_RECORD_LOG_USE_TIMESTAMPED_FILENAME=%d",
			getSASGameRecordLogLevel(), getSASGameRecordTurnInterval(), isSASGameRecordTimestampedFilenameEnabled());
}

static void resetSASGameRecordState();
static void logSASGameRecordInitialContext();

void startSASGameRecordLogForNewGame()
{
	rollSASGameRecordLog("new");
	resetSASGameRecordState();
	logSASGameRecord("GAME_RECORD_NEW_GAME_INITIALIZING utc=%s logFile=%s", getSASGameRecordLogTimestamp().GetCString(), getSASGameRecordQuoted(getSASGameRecordLogName().GetCString()).GetCString());
	logSASGameRecordLogSettings();
}

void logSASGameRecordNewGameStarted()
{
	logSASGameRecordGameState("GAME_RECORD_NEW_GAME_STARTED");
	logSASGameRecordInitialContext();
}

void startSASGameRecordLogForLoadedSave()
{
	rollSASGameRecordLog("load");
	resetSASGameRecordState();
	logSASGameRecordGameState("GAME_RECORD_SAVE_LOADED");
	logSASGameRecordLogSettings();
	logSASGameRecordInitialContext();
}

// <!-- custom: Game-record helpers keep output compact, stable, and machine-readable. They intentionally use XML type names instead of localized text where possible, so external tools can diff and parse autoplay runs reliably. The static state below is tiny and is only reset/updated through game-record call sites when the XML log level enables this feature; dynamic XML logging cannot be compiled out cleanly without losing normal runtime XML tuning. (ChatGPT-5.5) -->
static int g_aiSASGameRecordBattleWins[MAX_PLAYERS];
static int g_aiSASGameRecordBattleLosses[MAX_PLAYERS];
static int g_aiSASGameRecordCityBattleWins[MAX_PLAYERS];
static int g_aiSASGameRecordCityBattleLosses[MAX_PLAYERS];
static int g_aiSASGameRecordTotalBattleWins[MAX_PLAYERS];
static int g_aiSASGameRecordTotalBattleLosses[MAX_PLAYERS];
static int g_aiSASGameRecordTotalCityBattleWins[MAX_PLAYERS];
static int g_aiSASGameRecordTotalCityBattleLosses[MAX_PLAYERS];
static int g_aiSASGameRecordTotalGoldenAgeTurns[MAX_PLAYERS];
static int g_aiSASGameRecordTotalAnarchyTurns[MAX_PLAYERS];
static int g_aiSASGameRecordCitiesAcquired[MAX_PLAYERS];
static int g_aiSASGameRecordCitiesLost[MAX_PLAYERS];
static int g_aiSASGameRecordCitiesConquered[MAX_PLAYERS];
static int g_aiSASGameRecordCitiesLostByConquest[MAX_PLAYERS];
static int g_aiSASGameRecordCitiesTradedIn[MAX_PLAYERS];
static int g_aiSASGameRecordCitiesTradedOut[MAX_PLAYERS];
static int g_iSASGameRecordLastFullSnapshotTurn = -1;

struct SASGameRecordPlotChangeGroup
{
	CvString szCategory;
	std::vector<std::pair<int,int> > aCoordinates;
};

static int g_iSASGameRecordPendingPlotTurn = -1;

struct SASGameRecordCityBombardPending
{
	bool bValid;
	int iTurn;
	CvString szMode;
	PlayerTypes ePlayer;
	PlayerTypes eTargetPlayer;
	int iCityId;
	CvWString szCity;
	int iX;
	int iY;
	int iActions;
	int iBombardRateTotal;
	int iIgnoreBuildingDefenseActions;
	int iDefenseModifierBefore;
	int iDefenseModifierAfter;
	int iTotalDefense;
	int iDefenseDamageBefore;
	int iDefenseDamageAfter;
	int iDefenseDamageMax;
	std::vector<std::pair<CvString,int> > aUnitTypes;
	std::vector<std::pair<CvString,int> > aUnitAIs;
	SASGameRecordCityBombardPending() : bValid(false), iTurn(-1), ePlayer(NO_PLAYER), eTargetPlayer(NO_PLAYER), iCityId(-1), iX(-1), iY(-1), iActions(0), iBombardRateTotal(0), iIgnoreBuildingDefenseActions(0), iDefenseModifierBefore(-1), iDefenseModifierAfter(-1), iTotalDefense(-1), iDefenseDamageBefore(-1), iDefenseDamageAfter(-1), iDefenseDamageMax(-1) {}
};

static SASGameRecordCityBombardPending g_kSASGameRecordPendingCityBombard;
static std::vector<SASGameRecordPlotChangeGroup> g_aSASGameRecordPlotChanges;
static std::vector<std::pair<int,int> > g_aaSASGameRecordRevealedPlots[MAX_TEAMS];
static TeamTypes g_eSASGameRecordFullMapRevelationTeam = NO_TEAM;
static int g_iSASGameRecordFullMapRevealedBefore = 0;

struct SASGameRecordPlayerPrevious
{
	bool bValid;
	int iScore;
	int iCities;
	int iPopulation;
	int iLand;
	int iUnits;
	int iCombatUnits;
	int iMilitarySupportUnits;
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

struct SASGameRecordTeamPrevious
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

struct SASGameRecordGlobalPrevious
{
	bool bValid;
	int iGlobalWarmingIndex;
	int iGlobalWarmingChances;
	int iOwnedLand;
	int iUnownedLand;
};

struct SASGameRecordPlotComposition
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

	SASGameRecordPlotComposition() : iPlots(0), iLand(0), iWater(0), iHills(0), iPeaks(0), iRiverSide(0), iFreshWater(0), iCoastal(0), iImproved(0), iUnimprovedLand(0), iRoaded(0), iBonusImproved(0), iBonusUnimproved(0), iWorked(0), iWorkedImproved(0), iWorkedUnimproved(0), iNatureFood(0), iNatureProduction(0), iNatureCommerce(0), iCurrentFood(0), iCurrentProduction(0), iCurrentCommerce(0), aiTerrains(GC.getNumTerrainInfos(), 0), aiFeatures(GC.getNumFeatureInfos(), 0), aiBonuses(GC.getNumBonusInfos(), 0), aiImprovements(GC.getNumImprovementInfos(), 0), aiRoutes(GC.getNumRouteInfos(), 0) {}
};

struct SASGameRecordTerritoryDevelopment
{
	SASGameRecordPlotComposition kOwned;
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
	SASGameRecordTerritoryDevelopment() : aiImprovedBonuses(GC.getNumBonusInfos(), 0), aiUnimprovedBonuses(GC.getNumBonusInfos(), 0), iBFCPlots(0), iSuburbPlots(0), iDevelopmentLand(0), iDevelopmentWater(0), iImprovedLand(0), iImprovedWater(0), iBFCDevelopmentLand(0), iBFCImprovedLand(0), iSuburbDevelopmentLand(0), iSuburbImprovedLand(0), iFarms(0), iIrrigatedFarms(0), iDryFarms(0), iBonusFarms(0), iIrrigatedBonusFarms(0), iDryBonusFarms(0), iBFCFarms(0), iBFCIrrigatedFarms(0), iBFCDryFarms(0) {}
};

static SASGameRecordPlayerPrevious g_akSASGameRecordPlayerPrevious[MAX_PLAYERS];
static SASGameRecordTeamPrevious g_akSASGameRecordTeamPrevious[MAX_TEAMS];
static SASGameRecordGlobalPrevious g_kSASGameRecordGlobalPrevious;

static int getSASGameRecordDelta(bool bValid, int iCurrent, int iPrevious)
{
	return bValid ? iCurrent - iPrevious : 0;
}

static void resetSASGameRecordState()
{
	for (int iI = 0; iI < MAX_PLAYERS; iI++)
	{
		g_aiSASGameRecordBattleWins[iI] = 0;
		g_aiSASGameRecordBattleLosses[iI] = 0;
		g_aiSASGameRecordCityBattleWins[iI] = 0;
		g_aiSASGameRecordCityBattleLosses[iI] = 0;
		g_aiSASGameRecordTotalBattleWins[iI] = 0;
		g_aiSASGameRecordTotalBattleLosses[iI] = 0;
		g_aiSASGameRecordTotalCityBattleWins[iI] = 0;
		g_aiSASGameRecordTotalCityBattleLosses[iI] = 0;
		g_aiSASGameRecordTotalGoldenAgeTurns[iI] = 0;
		g_aiSASGameRecordTotalAnarchyTurns[iI] = 0;
		g_aiSASGameRecordCitiesAcquired[iI] = 0;
		g_aiSASGameRecordCitiesLost[iI] = 0;
		g_aiSASGameRecordCitiesConquered[iI] = 0;
		g_aiSASGameRecordCitiesLostByConquest[iI] = 0;
		g_aiSASGameRecordCitiesTradedIn[iI] = 0;
		g_aiSASGameRecordCitiesTradedOut[iI] = 0;
		g_akSASGameRecordPlayerPrevious[iI].bValid = false;
	}
	for (int iI = 0; iI < MAX_TEAMS; iI++)
	{
		g_akSASGameRecordTeamPrevious[iI].bValid = false;
		g_akSASGameRecordTeamPrevious[iI].bContactsValid = false;
	}
	g_kSASGameRecordGlobalPrevious.bValid = false;
	g_iSASGameRecordLastFullSnapshotTurn = -1;
	g_iSASGameRecordPendingPlotTurn = -1;
	g_kSASGameRecordPendingCityBombard = SASGameRecordCityBombardPending();
	g_aSASGameRecordPlotChanges.clear();
	g_eSASGameRecordFullMapRevelationTeam = NO_TEAM;
	g_iSASGameRecordFullMapRevealedBefore = 0;
	for (int iI = 0; iI < MAX_TEAMS; iI++)
		g_aaSASGameRecordRevealedPlots[iI].clear();
}

static void appendSASGameRecordIntList(CvString& szList, int iValue)
{
	CvString szItem;
	szItem.Format(szList.empty() ? "%d" : ",%d", iValue);
	szList += szItem;
}

static CvString getSASGameRecordTeamMembers(TeamTypes eTeam)
{
	CvString szList;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (kLoopPlayer.isAlive() && kLoopPlayer.getTeam() == eTeam)
			appendSASGameRecordIntList(szList, eLoopPlayer);
	}
	return szList.empty() ? CvString("-") : szList;
}

static CvString getSASGameRecordWarTeams(TeamTypes eTeam)
{
	CvString szList;
	CvTeam const& kTeam = GET_TEAM(eTeam);
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam != eTeam && GET_TEAM(eLoopTeam).isAlive() && kTeam.isAtWar(eLoopTeam))
			appendSASGameRecordIntList(szList, eLoopTeam);
	}
	return szList.empty() ? CvString("-") : szList;
}

static CvString getSASGameRecordVassalTeams(TeamTypes eTeam)
{
	CvString szList;
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam != eTeam && GET_TEAM(eLoopTeam).isAlive() && GET_TEAM(eLoopTeam).isVassal(eTeam))
			appendSASGameRecordIntList(szList, eLoopTeam);
	}
	return szList.empty() ? CvString("-") : szList;
}

static CvString getSASGameRecordMetTeams(TeamTypes eTeam)
{
	CvString szMetTeams;
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam == eTeam || !GET_TEAM(eLoopTeam).isAlive() || GET_TEAM(eLoopTeam).isBarbarian())
			continue;
		if (GET_TEAM(eTeam).isHasMet(eLoopTeam))
			appendSASGameRecordIntList(szMetTeams, eLoopTeam);
	}
	return szMetTeams.empty() ? CvString("-") : szMetTeams;
}

static int getSASGameRecordMetTeamCount(TeamTypes eTeam)
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

static void logSASGameRecordTeamContacts(TeamTypes eTeam, int iGameTurn, const char* szReason)
{
	SASGameRecordTeamPrevious& kPrevious = g_akSASGameRecordTeamPrevious[eTeam];
	const int iMetTeams = getSASGameRecordMetTeamCount(eTeam);
	logSASGameRecord("GAME_RECORD_CONTACTS turn=%d reason=%s team=%d deltaValid=%d metCount=%d metCountDelta=%+d metTeams=%s",
			iGameTurn, szReason, eTeam, kPrevious.bContactsValid, iMetTeams, getSASGameRecordDelta(kPrevious.bContactsValid, iMetTeams, kPrevious.iMetTeams), getSASGameRecordMetTeams(eTeam).GetCString());
	kPrevious.bContactsValid = true;
	kPrevious.iMetTeams = iMetTeams;
}

static TeamTypes getSASGameRecordMasterTeam(TeamTypes eTeam)
{
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam != eTeam && GET_TEAM(eLoopTeam).isAlive() && GET_TEAM(eTeam).isVassal(eLoopTeam))
			return eLoopTeam;
	}
	return NO_TEAM;
}

static const char* getSASGameRecordTechType(TechTypes eTech)
{
	return (eTech == NO_TECH ? "-" : GC.getInfo(eTech).getType());
}

static const char* getSASGameRecordReligionType(ReligionTypes eReligion)
{
	return (eReligion == NO_RELIGION ? "-" : GC.getInfo(eReligion).getType());
}

static const char* getSASGameRecordCorporationType(CorporationTypes eCorporation)
{
	return (eCorporation == NO_CORPORATION ? "-" : GC.getInfo(eCorporation).getType());
}

static const char* getSASGameRecordBuildingType(BuildingTypes eBuilding)
{
	return (eBuilding == NO_BUILDING ? "-" : GC.getInfo(eBuilding).getType());
}

static const char* getSASGameRecordProjectType(ProjectTypes eProject)
{
	return (eProject == NO_PROJECT ? "-" : GC.getInfo(eProject).getType());
}

static const char* getSASGameRecordUnitType(UnitTypes eUnit)
{
	return (eUnit == NO_UNIT ? "-" : GC.getInfo(eUnit).getType());
}

static const char* getSASGameRecordBonusType(BonusTypes eBonus)
{
	return (eBonus == NO_BONUS ? "-" : GC.getInfo(eBonus).getType());
}

static const char* getSASGameRecordTerrainType(TerrainTypes eTerrain)
{
	return (eTerrain == NO_TERRAIN ? "-" : GC.getInfo(eTerrain).getType());
}

static const char* getSASGameRecordFeatureType(FeatureTypes eFeature)
{
	return (eFeature == NO_FEATURE ? "-" : GC.getInfo(eFeature).getType());
}

static const char* getSASGameRecordImprovementType(ImprovementTypes eImprovement)
{
	return (eImprovement == NO_IMPROVEMENT ? "-" : GC.getInfo(eImprovement).getType());
}

static const char* getSASGameRecordRouteType(RouteTypes eRoute)
{
	return (eRoute == NO_ROUTE ? "-" : GC.getInfo(eRoute).getType());
}

SASGameRecordPlotState::SASGameRecordPlotState()
:	eTerrain(NO_TERRAIN), eFeature(NO_FEATURE), eBonus(NO_BONUS), eImprovement(NO_IMPROVEMENT), eRoute(NO_ROUTE)
{
	for (int iI = 0; iI < NUM_YIELD_TYPES; iI++)
		aiExtraYield[iI] = 0;
}

SASGameRecordPlotState::SASGameRecordPlotState(CvPlot const& kPlot)
:	eTerrain(kPlot.getTerrainType()), eFeature(kPlot.getFeatureType()), eBonus(kPlot.getBonusType()),
	eImprovement(kPlot.getImprovementType()), eRoute(kPlot.getRouteType())
{
	for (int iI = 0; iI < NUM_YIELD_TYPES; iI++)
		aiExtraYield[iI] = GC.getMap().getPlotExtraYield(kPlot, (YieldTypes)iI);
}

static bool isSASGameRecordPlotStateChanged(SASGameRecordPlotState const& kOldState, CvPlot const& kPlot)
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

static void addSASGameRecordCoordinate(std::vector<std::pair<int,int> >& aCoordinates, CvPlot const& kPlot)
{
	std::pair<int,int> const kCoordinate(kPlot.getX(), kPlot.getY());
	if (std::find(aCoordinates.begin(), aCoordinates.end(), kCoordinate) == aCoordinates.end())
		aCoordinates.push_back(kCoordinate);
}

static void appendSASGameRecordCoordinateChunks(std::vector<CvString>& aszChunks, CvString& szChunk, char const* szCategory, std::vector<std::pair<int,int> > const& aCoordinates)
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

static int getSASGameRecordRevealedPlotCount(TeamTypes eTeam)
{
	int iRevealed = 0;
	int iLoop = 0;
	for (CvArea const* pLoopArea = GC.getMap().firstArea(&iLoop); pLoopArea != NULL; pLoopArea = GC.getMap().nextArea(&iLoop))
		iRevealed += pLoopArea->getNumRevealedTiles(eTeam);
	return iRevealed;
}

void beginSASGameRecordFullMapRevelation(TeamTypes eTeam, TechTypes eTech)
{
	FAssert(g_eSASGameRecordFullMapRevelationTeam == NO_TEAM);
	FAssert(eTeam >= 0 && eTeam < MAX_CIV_TEAMS);
	FAssert(eTech != NO_TECH);
	g_eSASGameRecordFullMapRevelationTeam = eTeam;
	g_iSASGameRecordFullMapRevealedBefore = getSASGameRecordRevealedPlotCount(eTeam);
}

void endSASGameRecordFullMapRevelation(TeamTypes eTeam, TechTypes eTech)
{
	FAssert(g_eSASGameRecordFullMapRevelationTeam == eTeam);
	int const iRevealed = getSASGameRecordRevealedPlotCount(eTeam);
	int const iNewlyRevealed = iRevealed - g_iSASGameRecordFullMapRevealedBefore;
	int const iRevealedPctX100 = (10000 * iRevealed) / std::max(1, (int)GC.getMap().numPlots());
	logSASGameRecord("GAME_RECORD_MAP_REVELATION turn=%d team=%d cause=MAP_VISIBLE_TECH tech=%s revealMode=FULL_MAP newlyRevealedCount=%d revealedPlots=%d revealedPctX100=%d", GC.getGame().getGameTurn(), eTeam, getSASGameRecordTechType(eTech), iNewlyRevealed, iRevealed, iRevealedPctX100);
	g_eSASGameRecordFullMapRevelationTeam = NO_TEAM;
	g_iSASGameRecordFullMapRevealedBefore = 0;
}

void flushSASGameRecordTurnChanges(int iGameTurn)
{
	flushSASGameRecordPendingCityBombard();
	if (g_iSASGameRecordPendingPlotTurn < 0)
		return;
	FAssert(iGameTurn == g_iSASGameRecordPendingPlotTurn);
	int const iLoggedTurn = iGameTurn;
	std::vector<CvString> aszPlotChunks;
	CvString szPlotChunk;
	for (size_t iI = 0; iI < g_aSASGameRecordPlotChanges.size(); iI++)
		appendSASGameRecordCoordinateChunks(aszPlotChunks, szPlotChunk, g_aSASGameRecordPlotChanges[iI].szCategory.GetCString(), g_aSASGameRecordPlotChanges[iI].aCoordinates);
	if (!szPlotChunk.empty())
		aszPlotChunks.push_back(szPlotChunk);
	for (size_t iI = 0; iI < aszPlotChunks.size(); iI++)
		logSASGameRecord("GAME_RECORD_PLOT_CHANGES turn=%d part=%d parts=%d changes=%s", iLoggedTurn, (int)iI + 1, (int)aszPlotChunks.size(), aszPlotChunks[iI].GetCString());
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		std::vector<std::pair<int,int> > const& aCoordinates = g_aaSASGameRecordRevealedPlots[iI];
		if (aCoordinates.empty())
			continue;
		std::vector<CvString> aszRevelationChunks;
		CvString szRevelationChunk;
		appendSASGameRecordCoordinateChunks(aszRevelationChunks, szRevelationChunk, "newlyRevealed", aCoordinates);
		if (!szRevelationChunk.empty())
			aszRevelationChunks.push_back(szRevelationChunk);
		// <!-- custom: CvMap::numPlots returns PlotNumTypes; casting it to int keeps MSVC 7.1 std::max template deduction unambiguous and fixed the compile error from adding map-revelation percentages. (GPT-5.6-Sol) -->
		int const iRevealedPctX100 = (10000 * getSASGameRecordRevealedPlotCount((TeamTypes)iI)) / std::max(1, (int)GC.getMap().numPlots());
		for (size_t iJ = 0; iJ < aszRevelationChunks.size(); iJ++)
			logSASGameRecord("GAME_RECORD_MAP_REVELATION turn=%d team=%d cause=INCREMENTAL revealMode=COORDINATES newlyRevealedCount=%d part=%d parts=%d revealedPctX100=%d %s", iLoggedTurn, iI, (int)aCoordinates.size(), (int)iJ + 1, (int)aszRevelationChunks.size(), iRevealedPctX100, aszRevelationChunks[iJ].GetCString());
	}
	g_iSASGameRecordPendingPlotTurn = -1;
	g_aSASGameRecordPlotChanges.clear();
	for (int iI = 0; iI < MAX_TEAMS; iI++)
		g_aaSASGameRecordRevealedPlots[iI].clear();
}

static void prepareSASGameRecordTurnChanges()
{
	int const iGameTurn = GC.getGame().getGameTurn();
	if (g_iSASGameRecordPendingPlotTurn >= 0 && g_iSASGameRecordPendingPlotTurn != iGameTurn)
		flushSASGameRecordTurnChanges(g_iSASGameRecordPendingPlotTurn);
	if (g_iSASGameRecordPendingPlotTurn < 0)
		g_iSASGameRecordPendingPlotTurn = iGameTurn;
}

void recordSASGameRecordPlotChange(CvPlot const& kPlot, SASGameRecordPlotState const& kOldState, char const* szCategory, char const* szCause, bool bDetailed)
{
	if (GC.getGame().getElapsedGameTurns() <= 0 || !isSASGameRecordPlotStateChanged(kOldState, kPlot))
		return;
	prepareSASGameRecordTurnChanges();
	SASGameRecordPlotChangeGroup* pGroup = NULL;
	for (size_t iI = 0; iI < g_aSASGameRecordPlotChanges.size(); iI++)
	{
		if (g_aSASGameRecordPlotChanges[iI].szCategory == szCategory)
		{
			pGroup = &g_aSASGameRecordPlotChanges[iI];
			break;
		}
	}
	if (pGroup == NULL)
	{
		SASGameRecordPlotChangeGroup kGroup;
		kGroup.szCategory = szCategory;
		g_aSASGameRecordPlotChanges.push_back(kGroup);
		pGroup = &g_aSASGameRecordPlotChanges.back();
	}
	addSASGameRecordCoordinate(pGroup->aCoordinates, kPlot);
	if (bDetailed)
	{
		logSASGameRecord("GAME_RECORD_PLOT_CHANGE turn=%d cause=%s category=%s x=%d y=%d owner=%d terrainOld=%s terrainNew=%s featureOld=%s featureNew=%s bonusOld=%s bonusNew=%s improvementOld=%s improvementNew=%s routeOld=%s routeNew=%s extraFoodOld=%d extraFoodNew=%d extraProductionOld=%d extraProductionNew=%d extraCommerceOld=%d extraCommerceNew=%d",
				GC.getGame().getGameTurn(), szCause, szCategory, kPlot.getX(), kPlot.getY(), kPlot.getOwner(), getSASGameRecordTerrainType(kOldState.eTerrain), getSASGameRecordTerrainType(kPlot.getTerrainType()), getSASGameRecordFeatureType(kOldState.eFeature), getSASGameRecordFeatureType(kPlot.getFeatureType()), getSASGameRecordBonusType(kOldState.eBonus), getSASGameRecordBonusType(kPlot.getBonusType()), getSASGameRecordImprovementType(kOldState.eImprovement), getSASGameRecordImprovementType(kPlot.getImprovementType()), getSASGameRecordRouteType(kOldState.eRoute), getSASGameRecordRouteType(kPlot.getRouteType()), kOldState.aiExtraYield[YIELD_FOOD], GC.getMap().getPlotExtraYield(kPlot, YIELD_FOOD), kOldState.aiExtraYield[YIELD_PRODUCTION], GC.getMap().getPlotExtraYield(kPlot, YIELD_PRODUCTION), kOldState.aiExtraYield[YIELD_COMMERCE], GC.getMap().getPlotExtraYield(kPlot, YIELD_COMMERCE));
	}
}

void recordSASGameRecordPlotRevealed(CvPlot const& kPlot, TeamTypes eTeam)
{
	if (GC.getGame().getElapsedGameTurns() <= 0 || eTeam < 0 || eTeam >= MAX_CIV_TEAMS)
		return;
	if (eTeam == g_eSASGameRecordFullMapRevelationTeam)
		return;
	prepareSASGameRecordTurnChanges();
	// <!-- custom: setRevealed calls this only on false-to-true transitions, so the same team cannot add this plot twice without first losing permanent revelation; append directly instead of repeatedly searching a potentially large map-trade list. (GPT-5.6-Sol) -->
	g_aaSASGameRecordRevealedPlots[eTeam].push_back(std::make_pair(kPlot.getX(), kPlot.getY()));
}

void logSASGameRecordEnvironmentTurn(int iPollution, int iSustainabilityThreshold, int iLandDefense, int iIndexBefore, int iIndexBeforeRestoration, int iIndexEnd, int iWarmingChances, int iEventTally)
{
	logSASGameRecord("GAME_RECORD_ENVIRONMENT_TURN turn=%d pollution=%d sustainabilityThreshold=%d landDefense=%d totalDefense=%d indexBefore=%d indexBeforeRestoration=%d indexEnd=%d indexDelta=%+d warmingChances=%d eventTally=%d severityPercent=%d active=%d",
			GC.getGame().getGameTurn(), iPollution, iSustainabilityThreshold, iLandDefense, iSustainabilityThreshold + iLandDefense, iIndexBefore, iIndexBeforeRestoration, iIndexEnd, iIndexEnd - iIndexBefore, iWarmingChances, iEventTally, GC.getGame().calculateGwSeverityRating(), iIndexEnd > 0);
}

void logSASGameRecordBonusChanged(CvPlot const* pPlot, BonusTypes eOldBonus, BonusTypes eNewBonus)
{
	if (pPlot == NULL || eOldBonus == eNewBonus)
		return;
	SASGameRecordPlotState kOldState(*pPlot);
	kOldState.eBonus = eOldBonus;
	recordSASGameRecordPlotChange(*pPlot, kOldState, "resourceChanges", "RESOURCE_CHANGE", false);
	const char* szAction = (eOldBonus == NO_BONUS ? "appeared" : (eNewBonus == NO_BONUS ? "disappeared" : "changed"));
	CvCity const* pWorkingCity = pPlot->getWorkingCity();
	CvCity const* pPlotCity = pPlot->getPlotCity();
	// <!-- custom: Reproducible T129 crash dumps after adding this row failed in msvcr71!_output/_vsnprintf with an invalid read at 0x000003fc. The original argument for area=%d was pPlot->getArea(), but CvPlot::getArea returns CvArea&, not an integer; passing that object reference through varargs corrupted the following formatter reads. Logging the area ID explicitly fixed the crash in the next test run. (GPT-5.5) -->
	logSASGameRecord("GAME_RECORD_BONUS_CHANGE turn=%d elapsed=%d action=%s x=%d y=%d area=%d owner=%d oldBonus=%s newBonus=%s terrain=%s feature=%s improvement=%s route=%s water=%d hills=%d peak=%d riverSide=%d cityRadius=%d workingCity=%S workingCityId=%d plotCity=%S plotCityId=%d",
			GC.getGame().getGameTurn(), GC.getGame().getElapsedGameTurns(), szAction, pPlot->getX(), pPlot->getY(), pPlot->getArea().getID(), pPlot->getOwner(), getSASGameRecordBonusType(eOldBonus), getSASGameRecordBonusType(eNewBonus), getSASGameRecordTerrainType(pPlot->getTerrainType()), getSASGameRecordFeatureType(pPlot->getFeatureType()), getSASGameRecordImprovementType(pPlot->getImprovementType()), getSASGameRecordRouteType(pPlot->getRouteType()), pPlot->isWater(), pPlot->isHills(), pPlot->isPeak(), pPlot->isRiverSide(), pPlot->isCityRadius(), getSASGameRecordQuotedCityName(pWorkingCity).GetCString(), (pWorkingCity == NULL ? -1 : pWorkingCity->getID()), getSASGameRecordQuotedCityName(pPlotCity).GetCString(), (pPlotCity == NULL ? -1 : pPlotCity->getID()));
}

static const char* getSASGameRecordCommerceType(CommerceTypes eCommerce)
{
	return (eCommerce == NO_COMMERCE ? "-" : GC.getInfo(eCommerce).getType());
}

static const char* getSASGameRecordBuildType(BuildTypes eBuild)
{
	return (eBuild == NO_BUILD ? "-" : GC.getInfo(eBuild).getType());
}

static const char* getSASGameRecordMissionType(MissionTypes eMission)
{
	return (eMission == NO_MISSION ? "-" : GC.getInfo(eMission).getType());
}

static const char* getSASGameRecordEspionageMissionType(EspionageMissionTypes eMission)
{
	return (eMission == NO_ESPIONAGEMISSION ? "-" : GC.getInfo(eMission).getType());
}

static const char* getSASGameRecordUnitAIType(UnitAITypes eUnitAI)
{
	return (eUnitAI == NO_UNITAI ? "-" : GC.getInfo(eUnitAI).getType());
}

static const char* getSASGameRecordUnitCombatType(UnitCombatTypes eUnitCombat)
{
	return (eUnitCombat == NO_UNITCOMBAT ? "-" : GC.getInfo(eUnitCombat).getType());
}

static const char* getSASGameRecordPromotionType(PromotionTypes ePromotion)
{
	return (ePromotion == NO_PROMOTION ? "-" : GC.getInfo(ePromotion).getType());
}

static const char* getSASGameRecordSpecialistType(SpecialistTypes eSpecialist)
{
	return (eSpecialist == NO_SPECIALIST ? "-" : GC.getInfo(eSpecialist).getType());
}

static const char* getSASGameRecordProcessType(ProcessTypes eProcess)
{
	return (eProcess == NO_PROCESS ? "-" : GC.getInfo(eProcess).getType());
}

static const char* getSASGameRecordCivicType(CivicTypes eCivic)
{
	return (eCivic == NO_CIVIC ? "-" : GC.getInfo(eCivic).getType());
}

static const char* getSASGameRecordVoteSourceType(VoteSourceTypes eVoteSource)
{
	return (eVoteSource == NO_VOTESOURCE ? "-" : GC.getInfo(eVoteSource).getType());
}

static const char* getSASGameRecordVoteType(VoteTypes eVote)
{
	return (eVote == NO_VOTE ? "-" : GC.getInfo(eVote).getType());
}

static const char* getSASGameRecordEraType(EraTypes eEra)
{
	return (eEra == NO_ERA ? "-" : GC.getInfo(eEra).getType());
}

static void appendSASGameRecordTypeCount(CvString& szList, const char* szType, int iCount)
{
	if (iCount <= 0)
		return;
	CvString szItem;
	szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", szType, iCount);
	szList += szItem;
}

static void addSASGameRecordCityBombardTypeCount(std::vector<std::pair<CvString,int> >& aCounts, char const* szType)
{
	for (size_t iI = 0; iI < aCounts.size(); iI++)
	{
		if (aCounts[iI].first == szType)
		{
			aCounts[iI].second++;
			return;
		}
	}
	aCounts.push_back(std::make_pair(CvString(szType), 1));
}

static void flushSASGameRecordPendingCityBombard()
{
	if (!g_kSASGameRecordPendingCityBombard.bValid)
		return;
	CvString szUnitTypes;
	CvString szUnitAIs;
	for (size_t iI = 0; iI < g_kSASGameRecordPendingCityBombard.aUnitTypes.size(); iI++)
		appendSASGameRecordTypeCount(szUnitTypes, g_kSASGameRecordPendingCityBombard.aUnitTypes[iI].first.GetCString(), g_kSASGameRecordPendingCityBombard.aUnitTypes[iI].second);
	for (size_t iI = 0; iI < g_kSASGameRecordPendingCityBombard.aUnitAIs.size(); iI++)
		appendSASGameRecordTypeCount(szUnitAIs, g_kSASGameRecordPendingCityBombard.aUnitAIs[iI].first.GetCString(), g_kSASGameRecordPendingCityBombard.aUnitAIs[iI].second);
	if (szUnitTypes.empty()) szUnitTypes = "-";
	if (szUnitAIs.empty()) szUnitAIs = "-";
	g_bSASGameRecordFlushingCityBombard = true;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=CITY_BOMBARD mode=%s player=%d targetPlayer=%d cityId=%d city=%S x=%d y=%d actions=%d unitTypes=%s unitAI=%s bombardRateTotal=%d ignoreBuildingDefenseActions=%d defenseModifierBefore=%d defenseModifierAfter=%d defenseReduction=%d totalDefense=%d defenseDamageBefore=%d defenseDamageAfter=%d defenseDamageMax=%d",
			g_kSASGameRecordPendingCityBombard.iTurn, g_kSASGameRecordPendingCityBombard.szMode.GetCString(), g_kSASGameRecordPendingCityBombard.ePlayer, g_kSASGameRecordPendingCityBombard.eTargetPlayer, g_kSASGameRecordPendingCityBombard.iCityId, g_kSASGameRecordPendingCityBombard.szCity.GetCString(), g_kSASGameRecordPendingCityBombard.iX, g_kSASGameRecordPendingCityBombard.iY, g_kSASGameRecordPendingCityBombard.iActions, szUnitTypes.GetCString(), szUnitAIs.GetCString(),
			g_kSASGameRecordPendingCityBombard.iBombardRateTotal, g_kSASGameRecordPendingCityBombard.iIgnoreBuildingDefenseActions, g_kSASGameRecordPendingCityBombard.iDefenseModifierBefore, g_kSASGameRecordPendingCityBombard.iDefenseModifierAfter, std::max(0, g_kSASGameRecordPendingCityBombard.iDefenseModifierBefore - g_kSASGameRecordPendingCityBombard.iDefenseModifierAfter), g_kSASGameRecordPendingCityBombard.iTotalDefense, g_kSASGameRecordPendingCityBombard.iDefenseDamageBefore, g_kSASGameRecordPendingCityBombard.iDefenseDamageAfter, g_kSASGameRecordPendingCityBombard.iDefenseDamageMax);
	g_bSASGameRecordFlushingCityBombard = false;
	g_kSASGameRecordPendingCityBombard = SASGameRecordCityBombardPending();
}

static CvString getSASGameRecordOrDash(CvString const& szList)
{
	return szList.empty() ? CvString("-") : szList;
}

static void appendSASGameRecordPositiveValue(CvString& szList, const char* szName, int iValue)
{
	if (iValue <= 0)
		return;
	CvString szItem;
	szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", szName, iValue);
	szList += szItem;
}

static void appendSASGameRecordValue(CvString& szList, const char* szName, int iValue)
{
	CvString szItem;
	szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", szName, iValue);
	szList += szItem;
}

static void appendSASGameRecordSignedValue(CvString& szList, const char* szName, int iValue)
{
	if (iValue == 0)
		return;
	CvString szItem;
	szItem.Format(szList.empty() ? "%s:%+d" : ",%s:%+d", szName, iValue);
	szList += szItem;
}

static void addSASGameRecordPlotComposition(SASGameRecordPlotComposition& kComposition, CvPlot const& kPlot, TeamTypes eTeam)
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

static int getSASGameRecordPercentX100(int iValue, int iTotal)
{
	return (iTotal <= 0 ? -1 : (10000 * iValue) / iTotal);
}

// <!-- custom: Add lightweight owned-territory counts to the map scan already used by the expansion record, rather than scanning every plot again or calculating unused plot yields. BFC means the plot is assigned to one of this player's cities; development land excludes city centers and peaks because Workers cannot add ordinary improvements there. (GPT-5.6-Sol) -->
static void addSASGameRecordTerritoryDevelopment(SASGameRecordTerritoryDevelopment& kDevelopment, CvPlot const& kPlot, PlayerTypes ePlayer, TeamTypes eTeam, ImprovementTypes eFarm)
{
	SASGameRecordPlotComposition& kOwned = kDevelopment.kOwned;
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

static void getSASGameRecordImprovementRouteTypes(SASGameRecordPlotComposition const& kComposition, CvString& szImprovements, CvString& szRoutes)
{
	for (int iI = 0; iI < GC.getNumImprovementInfos(); iI++)
		appendSASGameRecordTypeCount(szImprovements, getSASGameRecordImprovementType((ImprovementTypes)iI), kComposition.aiImprovements[iI]);
	for (int iI = 0; iI < GC.getNumRouteInfos(); iI++)
		appendSASGameRecordTypeCount(szRoutes, getSASGameRecordRouteType((RouteTypes)iI), kComposition.aiRoutes[iI]);
}

static void getSASGameRecordLandscapeTypes(SASGameRecordPlotComposition const& kComposition, CvString& szTerrains, CvString& szFeatures, CvString& szBonuses)
{
	for (int iI = 0; iI < GC.getNumTerrainInfos(); iI++)
		appendSASGameRecordTypeCount(szTerrains, getSASGameRecordTerrainType((TerrainTypes)iI), kComposition.aiTerrains[iI]);
	for (int iI = 0; iI < GC.getNumFeatureInfos(); iI++)
		appendSASGameRecordTypeCount(szFeatures, getSASGameRecordFeatureType((FeatureTypes)iI), kComposition.aiFeatures[iI]);
	for (int iI = 0; iI < GC.getNumBonusInfos(); iI++)
		appendSASGameRecordTypeCount(szBonuses, getSASGameRecordBonusType((BonusTypes)iI), kComposition.aiBonuses[iI]);
}

static void logSASGameRecordTerritoryDevelopment(PlayerTypes ePlayer, int iGameTurn, SASGameRecordTerritoryDevelopment const& kDevelopment)
{
	SASGameRecordPlotComposition const& kOwned = kDevelopment.kOwned;
	SASGameRecordPlayerPrevious& kPrevious = g_akSASGameRecordPlayerPrevious[ePlayer];
	CvString szImprovements;
	CvString szRoutes;
	getSASGameRecordImprovementRouteTypes(kOwned, szImprovements, szRoutes);
	int const iDevelopmentPlots = kDevelopment.iDevelopmentLand + kDevelopment.iDevelopmentWater;
	int const iImprovedPlots = kDevelopment.iImprovedLand + kDevelopment.iImprovedWater;
	int const iSuburbFarms = kDevelopment.iFarms - kDevelopment.iBFCFarms;
	int const iSuburbIrrigatedFarms = kDevelopment.iIrrigatedFarms - kDevelopment.iBFCIrrigatedFarms;
	int const iSuburbDryFarms = kDevelopment.iDryFarms - kDevelopment.iBFCDryFarms;
	logSASGameRecord("GAME_RECORD_TERRITORY_DEVELOPMENT turn=%d player=%d deltaValid=%d ownedPlots=%d ownedLand=%d ownedWater=%d bfcPlots=%d suburbPlots=%d developmentPlots=%d improvedPlots=%d improvedPercentX100=%d developmentLand=%d improvedLand=%d improvedLandDelta=%+d improvedLandPercentX100=%d developmentWater=%d improvedWater=%d improvedWaterDelta=%+d improvedWaterPercentX100=%d"
			" bfcDevelopmentLand=%d bfcImprovedLand=%d bfcImprovedLandPercentX100=%d suburbDevelopmentLand=%d suburbImprovedLand=%d suburbImprovedLandPercentX100=%d roaded=%d roadedDelta=%+d bonusImproved=%d bonusUnimproved=%d"
			" farms=%d farmsDelta=%+d irrigatedFarms=%d irrigatedFarmsDelta=%+d dryFarms=%d dryFarmsDelta=%+d irrigatedFarmPercentX100=%d dryFarmPercentX100=%d bonusFarms=%d irrigatedBonusFarms=%d dryBonusFarms=%d bfcFarms=%d bfcIrrigatedFarms=%d bfcDryFarms=%d bfcIrrigatedFarmPercentX100=%d suburbFarms=%d suburbIrrigatedFarms=%d suburbDryFarms=%d suburbIrrigatedFarmPercentX100=%d improvements=%s routes=%s",
			iGameTurn, ePlayer, kPrevious.bValid, kOwned.iPlots, kOwned.iLand, kOwned.iWater, kDevelopment.iBFCPlots, kDevelopment.iSuburbPlots, iDevelopmentPlots, iImprovedPlots, getSASGameRecordPercentX100(iImprovedPlots, iDevelopmentPlots),
			kDevelopment.iDevelopmentLand, kDevelopment.iImprovedLand, getSASGameRecordDelta(kPrevious.bValid, kDevelopment.iImprovedLand, kPrevious.iTerritoryImprovedLand), getSASGameRecordPercentX100(kDevelopment.iImprovedLand, kDevelopment.iDevelopmentLand), kDevelopment.iDevelopmentWater, kDevelopment.iImprovedWater, getSASGameRecordDelta(kPrevious.bValid, kDevelopment.iImprovedWater, kPrevious.iTerritoryImprovedWater), getSASGameRecordPercentX100(kDevelopment.iImprovedWater, kDevelopment.iDevelopmentWater),
			kDevelopment.iBFCDevelopmentLand, kDevelopment.iBFCImprovedLand, getSASGameRecordPercentX100(kDevelopment.iBFCImprovedLand, kDevelopment.iBFCDevelopmentLand), kDevelopment.iSuburbDevelopmentLand, kDevelopment.iSuburbImprovedLand, getSASGameRecordPercentX100(kDevelopment.iSuburbImprovedLand, kDevelopment.iSuburbDevelopmentLand), kOwned.iRoaded, getSASGameRecordDelta(kPrevious.bValid, kOwned.iRoaded, kPrevious.iTerritoryRoaded), kOwned.iBonusImproved, kOwned.iBonusUnimproved,
			kDevelopment.iFarms, getSASGameRecordDelta(kPrevious.bValid, kDevelopment.iFarms, kPrevious.iTerritoryFarms), kDevelopment.iIrrigatedFarms, getSASGameRecordDelta(kPrevious.bValid, kDevelopment.iIrrigatedFarms, kPrevious.iTerritoryIrrigatedFarms), kDevelopment.iDryFarms, getSASGameRecordDelta(kPrevious.bValid, kDevelopment.iDryFarms, kPrevious.iTerritoryDryFarms), getSASGameRecordPercentX100(kDevelopment.iIrrigatedFarms, kDevelopment.iFarms), getSASGameRecordPercentX100(kDevelopment.iDryFarms, kDevelopment.iFarms),
			kDevelopment.iBonusFarms, kDevelopment.iIrrigatedBonusFarms, kDevelopment.iDryBonusFarms, kDevelopment.iBFCFarms, kDevelopment.iBFCIrrigatedFarms, kDevelopment.iBFCDryFarms, getSASGameRecordPercentX100(kDevelopment.iBFCIrrigatedFarms, kDevelopment.iBFCFarms), iSuburbFarms, iSuburbIrrigatedFarms, iSuburbDryFarms, getSASGameRecordPercentX100(iSuburbIrrigatedFarms, iSuburbFarms), getSASGameRecordOrDash(szImprovements).GetCString(), getSASGameRecordOrDash(szRoutes).GetCString());
	if (gGameRecordLogLevel >= 3)
	{
		CvString szTerrains;
		CvString szFeatures;
		CvString szBonuses;
		CvString szImprovedBonuses;
		CvString szUnimprovedBonuses;
		getSASGameRecordLandscapeTypes(kOwned, szTerrains, szFeatures, szBonuses);
		for (int iI = 0; iI < GC.getNumBonusInfos(); iI++)
		{
			appendSASGameRecordTypeCount(szImprovedBonuses, getSASGameRecordBonusType((BonusTypes)iI), kDevelopment.aiImprovedBonuses[iI]);
			appendSASGameRecordTypeCount(szUnimprovedBonuses, getSASGameRecordBonusType((BonusTypes)iI), kDevelopment.aiUnimprovedBonuses[iI]);
		}
		logSASGameRecord("GAME_RECORD_TERRITORY_LANDSCAPE turn=%d player=%d terrains=%s features=%s bonuses=%s improvedBonuses=%s unimprovedBonuses=%s", iGameTurn, ePlayer, getSASGameRecordOrDash(szTerrains).GetCString(), getSASGameRecordOrDash(szFeatures).GetCString(), getSASGameRecordOrDash(szBonuses).GetCString(), getSASGameRecordOrDash(szImprovedBonuses).GetCString(), getSASGameRecordOrDash(szUnimprovedBonuses).GetCString());
	}
	kPrevious.iTerritoryImprovedLand = kDevelopment.iImprovedLand;
	kPrevious.iTerritoryImprovedWater = kDevelopment.iImprovedWater;
	kPrevious.iTerritoryRoaded = kOwned.iRoaded;
	kPrevious.iTerritoryFarms = kDevelopment.iFarms;
	kPrevious.iTerritoryIrrigatedFarms = kDevelopment.iIrrigatedFarms;
	kPrevious.iTerritoryDryFarms = kDevelopment.iDryFarms;
}

static void getSASGameRecordPlotCompositionTypes(SASGameRecordPlotComposition const& kComposition, CvString& szTerrains, CvString& szFeatures, CvString& szBonuses, CvString& szImprovements, CvString& szRoutes)
{
	getSASGameRecordLandscapeTypes(kComposition, szTerrains, szFeatures, szBonuses);
	getSASGameRecordImprovementRouteTypes(kComposition, szImprovements, szRoutes);
}

static void logSASGameRecordKnownArea(PlayerTypes ePlayer, const char* szReason)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	TeamTypes eTeam = kPlayer.getTeam();
	if (eTeam == NO_TEAM)
		return;
	SASGameRecordPlotComposition kRevealed;
	SASGameRecordPlotComposition kVisible;
	CvMap const& kMap = GC.getMap();
	for (int iI = 0; iI < kMap.numPlots(); iI++)
	{
		CvPlot const& kPlot = kMap.getPlotByIndex(iI);
		if (kPlot.isRevealed(eTeam, false))
			addSASGameRecordPlotComposition(kRevealed, kPlot, eTeam);
		if (kPlot.isVisible(eTeam, false))
			addSASGameRecordPlotComposition(kVisible, kPlot, eTeam);
	}
	logSASGameRecord("GAME_RECORD_KNOWN_AREA turn=%d reason=%s player=%d team=%d revealedPlots=%d visiblePlots=%d revealedLand=%d visibleLand=%d revealedWater=%d visibleWater=%d revealedHills=%d visibleHills=%d revealedPeaks=%d visiblePeaks=%d revealedRiverSide=%d visibleRiverSide=%d revealedFreshWater=%d visibleFreshWater=%d revealedCoastal=%d visibleCoastal=%d revealedImproved=%d visibleImproved=%d revealedUnimprovedLand=%d visibleUnimprovedLand=%d revealedRoaded=%d visibleRoaded=%d revealedBonusImproved=%d visibleBonusImproved=%d revealedBonusUnimproved=%d visibleBonusUnimproved=%d revealedNatureFood=%d visibleNatureFood=%d revealedNatureProd=%d visibleNatureProd=%d revealedNatureCommerce=%d visibleNatureCommerce=%d revealedCurrentFood=%d visibleCurrentFood=%d revealedCurrentProd=%d visibleCurrentProd=%d revealedCurrentCommerce=%d visibleCurrentCommerce=%d",
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
	getSASGameRecordPlotCompositionTypes(kRevealed, szRevealedTerrains, szRevealedFeatures, szRevealedBonuses, szRevealedImprovements, szRevealedRoutes);
	getSASGameRecordPlotCompositionTypes(kVisible, szVisibleTerrains, szVisibleFeatures, szVisibleBonuses, szVisibleImprovements, szVisibleRoutes);
	logSASGameRecord("GAME_RECORD_KNOWN_AREA_TYPES turn=%d reason=%s player=%d team=%d revealedTerrains=%s visibleTerrains=%s revealedFeatures=%s visibleFeatures=%s revealedBonuses=%s visibleBonuses=%s revealedImprovements=%s visibleImprovements=%s revealedRoutes=%s visibleRoutes=%s",
			GC.getGame().getGameTurn(), szReason, ePlayer, eTeam, getSASGameRecordOrDash(szRevealedTerrains).GetCString(), getSASGameRecordOrDash(szVisibleTerrains).GetCString(), getSASGameRecordOrDash(szRevealedFeatures).GetCString(), getSASGameRecordOrDash(szVisibleFeatures).GetCString(), getSASGameRecordOrDash(szRevealedBonuses).GetCString(), getSASGameRecordOrDash(szVisibleBonuses).GetCString(), getSASGameRecordOrDash(szRevealedImprovements).GetCString(), getSASGameRecordOrDash(szVisibleImprovements).GetCString(), getSASGameRecordOrDash(szRevealedRoutes).GetCString(), getSASGameRecordOrDash(szVisibleRoutes).GetCString());
}

static void logSASGameRecordStartingUnits(PlayerTypes ePlayer, const char* szReason)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	if (GC.getGame().getElapsedGameTurns() > 1)
		return;
	int iLoop = 0;
	for (CvUnit const* pLoopUnit = kPlayer.firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iLoop))
	{
		CvPlot const& kPlot = pLoopUnit->getPlot();
		logSASGameRecord("GAME_RECORD_STARTING_UNIT turn=%d reason=%s player=%d unitId=%d unit=%s unitAI=%s unitCombat=%s x=%d y=%d damage=%d xp=%d level=%d movesLeft=%d plotOwner=%d plotTerrain=%s plotFeature=%s plotBonus=%s plotImprovement=%s plotRoute=%s",
				GC.getGame().getGameTurn(), szReason, ePlayer, pLoopUnit->getID(), getSASGameRecordUnitType(pLoopUnit->getUnitType()), getSASGameRecordUnitAIType(pLoopUnit->AI_getUnitAIType()), getSASGameRecordUnitCombatType(pLoopUnit->getUnitInfo().getUnitCombatType()), pLoopUnit->getX(), pLoopUnit->getY(), pLoopUnit->getDamage(), pLoopUnit->getExperience(), pLoopUnit->getLevel(), pLoopUnit->movesLeft(), kPlot.getOwner(), getSASGameRecordTerrainType(kPlot.getTerrainType()), getSASGameRecordFeatureType(kPlot.getFeatureType()), getSASGameRecordBonusType(kPlot.getBonusType(pLoopUnit->getTeam())), getSASGameRecordImprovementType(kPlot.getImprovementType()), getSASGameRecordRouteType(kPlot.getRouteType()));
	}
}

static void logSASGameRecordCityBFC(CvCity const& kCity, const char* szReason)
{
	CvString szTerrains;
	CvString szFeatures;
	CvString szBonuses;
	CvString szImprovements;
	CvString szRoutes;
	SASGameRecordPlotComposition kComposition;
	int iOwned = 0;
	TeamTypes eTeam = GET_PLAYER(kCity.getOwner()).getTeam();
	for (CityPlotIter it(kCity); it.hasNext(); ++it)
	{
		CvPlot const& kPlot = *it;
		if (kPlot.getOwner() == kCity.getOwner())
			iOwned++;
		addSASGameRecordPlotComposition(kComposition, kPlot, eTeam);
	}
	getSASGameRecordPlotCompositionTypes(kComposition, szTerrains, szFeatures, szBonuses, szImprovements, szRoutes);
	logSASGameRecord("GAME_RECORD_CITY_BFC turn=%d reason=%s player=%d cityId=%d city=%S x=%d y=%d plots=%d owned=%d land=%d water=%d hills=%d peaks=%d riverSide=%d freshWater=%d coastal=%d improved=%d unimprovedLand=%d roaded=%d bonusImproved=%d bonusUnimproved=%d worked=%d workedImproved=%d workedUnimproved=%d natureFood=%d natureProd=%d natureCommerce=%d currentFood=%d currentProd=%d currentCommerce=%d terrains=%s features=%s bonuses=%s improvements=%s routes=%s",
			GC.getGame().getGameTurn(), szReason, kCity.getOwner(), kCity.getID(), getSASGameRecordQuotedCityName(&kCity).GetCString(), kCity.getX(), kCity.getY(), kComposition.iPlots, iOwned, kComposition.iLand, kComposition.iWater, kComposition.iHills, kComposition.iPeaks, kComposition.iRiverSide, kComposition.iFreshWater, kComposition.iCoastal, kComposition.iImproved, kComposition.iUnimprovedLand, kComposition.iRoaded, kComposition.iBonusImproved, kComposition.iBonusUnimproved, kComposition.iWorked, kComposition.iWorkedImproved, kComposition.iWorkedUnimproved, kComposition.iNatureFood, kComposition.iNatureProduction, kComposition.iNatureCommerce, kComposition.iCurrentFood, kComposition.iCurrentProduction, kComposition.iCurrentCommerce, getSASGameRecordOrDash(szTerrains).GetCString(), getSASGameRecordOrDash(szFeatures).GetCString(), getSASGameRecordOrDash(szBonuses).GetCString(), getSASGameRecordOrDash(szImprovements).GetCString(), getSASGameRecordOrDash(szRoutes).GetCString());
}

static SASGameRecordPlotComposition getSASGameRecordWorkedPlotComposition(CvCity const& kCity)
{
	SASGameRecordPlotComposition kComposition;
	const TeamTypes eTeam = GET_PLAYER(kCity.getOwner()).getTeam();
	// <!-- custom: Exclude the city center from worked-plot allocation records because it is always worked and would blur comparisons of citizen plot choices and improvement coverage between benchmark runs. (GPT-5.5) -->
	for (WorkingPlotIter it(kCity, false); it.hasNext(); ++it)
		addSASGameRecordPlotComposition(kComposition, *it, eTeam);
	return kComposition;
}

static void addSASGameRecordPlotComposition(SASGameRecordPlotComposition& kTarget, SASGameRecordPlotComposition const& kSource)
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

static CvString getSASGameRecordTechEraCounts(TeamTypes eTeam)
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
		appendSASGameRecordTypeCount(szList, getSASGameRecordEraType((EraTypes)iI), aiEras[iI]);
	return getSASGameRecordOrDash(szList);
}

static void logSASGameRecordPlayerSetup(PlayerTypes ePlayer)
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
	logSASGameRecord("GAME_RECORD_PLAYER_SETUP turn=%d player=%d team=%d alive=%d everAlive=%d human=%d humanSlot=%d currentlyHumanControlled=%d autoplayControlled=%d slotStatus=%d playerName=%S civType=%s civName=%S civShortName=%S leaderType=%s leaderName=%S traits=%s favoriteCivic=%s favoriteReligion=%s handicap=%s",
			GC.getGame().getGameTurn(), ePlayer, kPlayer.getTeam(), kPlayer.isAlive(), kPlayer.isEverAlive(), bCurrentlyHumanControlled, bHumanSlot, bCurrentlyHumanControlled, bAutoplayControlled, kInitCore.getSlotStatus(ePlayer), getSASGameRecordQuoted(kPlayer.getName(0)).GetCString(), szCivType, getSASGameRecordQuoted(kPlayer.getCivilizationDescription(0)).GetCString(), getSASGameRecordQuoted(kPlayer.getCivilizationShortDescription(0)).GetCString(), szLeaderType, getSASGameRecordQuoted(szLeaderName).GetCString(), getSASGameRecordOrDash(szTraits).GetCString(), getSASGameRecordCivicType(kPlayer.getFavoriteCivic()), getSASGameRecordReligionType(kPlayer.getFavoriteReligion()), kPlayer.getHandicapType() == NO_HANDICAP ? "-" : GC.getInfo(kPlayer.getHandicapType()).getType());
}

static void logSASGameRecordAttitudeLegend()
{
	const int iFuriousMax = GC.getDefineINT(CvGlobals::RELATIONS_THRESH_FURIOUS);
	const int iAnnoyedMax = GC.getDefineINT(CvGlobals::RELATIONS_THRESH_ANNOYED);
	const int iPleasedMin = GC.getDefineINT(CvGlobals::RELATIONS_THRESH_PLEASED);
	const int iFriendlyMin = GC.getDefineINT(CvGlobals::RELATIONS_THRESH_FRIENDLY);
	logSASGameRecord("GAME_RECORD_ATTITUDE_LEGEND valueFrom=AI_getAttitudeVal furious=<=%d annoyed=%d..%d cautious=%d..%d pleased=%d..%d friendly=>=%d",
			iFuriousMax, iFuriousMax + 1, iAnnoyedMax, iAnnoyedMax + 1, iPleasedMin - 1, iPleasedMin, iFriendlyMin - 1, iFriendlyMin);
}

struct SASGameRecordLandmassGeography
{
	SASGameRecordLandmassGeography() : iAreaId(-1), iAnchorX(-1), iAnchorY(-1), iPlots(0), iHabitablePlots(0), iImpassablePlots(0), iZeroNatureYieldPlots(0), iWaterBorderPlots(0), iSeaBorderPlots(0), iLakeBorderPlots(0), iIceBorderPlots(0), iSeaBorderEdges(0), iLakeBorderEdges(0), iIceBorderEdges(0), iHillsPlots(0), iPeakPlots(0), iRiverSidePlots(0), iFreshWaterPlots(0), iSumWrappedDX(0), iSumWrappedDY(0), iStartingPlayers(0), iNatureFood(0), iNatureProduction(0), iNatureCommerce(0), iBonusCount(0) {}
	int iAreaId;
	int iAnchorX;
	int iAnchorY;
	int iPlots;
	int iHabitablePlots;
	int iImpassablePlots;
	int iZeroNatureYieldPlots;
	int iWaterBorderPlots;
	int iSeaBorderPlots;
	int iLakeBorderPlots;
	int iIceBorderPlots;
	int iSeaBorderEdges;
	int iLakeBorderEdges;
	int iIceBorderEdges;
	int iHillsPlots;
	int iPeakPlots;
	int iRiverSidePlots;
	int iFreshWaterPlots;
	int iSumWrappedDX;
	int iSumWrappedDY;
	int iStartingPlayers;
	int iNatureFood;
	int iNatureProduction;
	int iNatureCommerce;
	int iBonusCount;
	CvString szStartingPlayers;
	std::vector<int> aiNoOceanConnectedAreas;
	std::vector<int> aiNoOceanNavigableConnectedAreas;
	std::vector<int> aiAdjacentLakeAreas;
	std::vector<int> aiTerrainCounts;
	std::vector<int> aiFeatureCounts;
	std::vector<int> aiBonusCounts;
	std::vector<CvString> aszBonusCoordinates;
	std::vector<int> aiEraRevealedRawFood;
	std::vector<int> aiEraRevealedRawProduction;
	std::vector<int> aiEraRevealedRawCommerce;
	std::vector<int> aiEraRevealedRaw321;
	std::vector<int> aiEraBonusPotentialFood;
	std::vector<int> aiEraBonusPotentialProduction;
	std::vector<int> aiEraBonusPotentialCommerce;
	std::vector<int> aiEraBonusPotential321;
};

static SASGameRecordLandmassGeography* getSASGameRecordLandmassGeography(std::vector<SASGameRecordLandmassGeography>& aLandmasses, int iAreaId)
{
	for (size_t iI = 0; iI < aLandmasses.size(); iI++)
	{
		if (aLandmasses[iI].iAreaId == iAreaId)
			return &aLandmasses[iI];
	}
	return NULL;
}

static void addSASGameRecordUniqueArea(std::vector<int>& aiAreas, int iAreaId)
{
	if (iAreaId < 0)
		return;
	if (std::find(aiAreas.begin(), aiAreas.end(), iAreaId) == aiAreas.end())
		aiAreas.push_back(iAreaId);
}

static CvString getSASGameRecordLandmassName(SASGameRecordLandmassGeography const& kLandmass)
{
	CvString szName;
	szName.Format("LAND_%d_%d_A%d", kLandmass.iAnchorX, kLandmass.iAnchorY, kLandmass.iAreaId);
	return szName;
}

static CvString getSASGameRecordLandmassList(std::vector<SASGameRecordLandmassGeography> const& aLandmasses, std::vector<int> const& aiAreas)
{
	CvString szList;
	for (size_t iI = 0; iI < aiAreas.size(); iI++)
	{
		for (size_t iJ = 0; iJ < aLandmasses.size(); iJ++)
		{
			if (aLandmasses[iJ].iAreaId != aiAreas[iI])
				continue;
			CvString szItem;
			CvString const szName = getSASGameRecordLandmassName(aLandmasses[iJ]);
			szItem.Format(szList.empty() ? "%s" : ",%s", szName.GetCString());
			szList += szItem;
			break;
		}
	}
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordLandmassTerrainPercentages(SASGameRecordLandmassGeography const& kLandmass)
{
	CvString szList;
	for (int iTerrain = 0; iTerrain < (int)kLandmass.aiTerrainCounts.size(); iTerrain++)
	{
		if (kLandmass.aiTerrainCounts[iTerrain] <= 0)
			continue;
		CvString szItem;
		szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", GC.getInfo((TerrainTypes)iTerrain).getType(), getSASGameRecordPercentX100(kLandmass.aiTerrainCounts[iTerrain], kLandmass.iPlots));
		szList += szItem;
	}
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordLandmassFeaturePercentages(SASGameRecordLandmassGeography const& kLandmass)
{
	CvString szList;
	for (int iFeature = 0; iFeature < (int)kLandmass.aiFeatureCounts.size(); iFeature++)
	{
		if (kLandmass.aiFeatureCounts[iFeature] <= 0)
			continue;
		CvString szItem;
		szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", GC.getInfo((FeatureTypes)iFeature).getType(), getSASGameRecordPercentX100(kLandmass.aiFeatureCounts[iFeature], kLandmass.iPlots));
		szList += szItem;
	}
	return getSASGameRecordOrDash(szList);
}

static int getSASGameRecordAdjacentLakePlots(SASGameRecordLandmassGeography const& kLandmass)
{
	int iPlots = 0;
	for (size_t iI = 0; iI < kLandmass.aiAdjacentLakeAreas.size(); iI++)
	{
		CvArea const* pArea = GC.getMap().getArea(kLandmass.aiAdjacentLakeAreas[iI]);
		if (pArea != NULL && pArea->isLake())
			iPlots += pArea->getNumTiles();
	}
	return iPlots;
}

static bool isSASGameRecordTechAvailableByEra(TechTypes eTech, EraTypes eEra)
{
	return (eTech == NO_TECH || GC.getInfo(eTech).getEra() <= eEra);
}

static bool isSASGameRecordBuildAvailableByEra(CvPlot const& kPlot, BuildTypes eBuild, EraTypes eEra)
{
	CvBuildInfo const& kBuild = GC.getInfo(eBuild);
	if (kBuild.getImprovement() == NO_IMPROVEMENT || !isSASGameRecordTechAvailableByEra(kBuild.getTechPrereq(), eEra))
		return false;
	FeatureTypes const eFeature = kPlot.getFeatureType();
	if (eFeature != NO_FEATURE && kBuild.isFeatureRemove(eFeature) && !isSASGameRecordTechAvailableByEra(kBuild.getFeatureTech(eFeature), eEra))
		return false;
	return kPlot.canHaveImprovement(kBuild.getImprovement(), NO_TEAM, true, eBuild, false);
}

static bool isSASGameRecordIrrigationAvailableByEra(EraTypes eEra)
{
	static std::vector<char> abAvailable;
	if (abAvailable.empty())
	{
		abAvailable.assign(GC.getNumEraInfos(), 0);
		FOR_EACH_ENUM(Tech)
		{
			if (!GC.getInfo(eLoopTech).isIrrigation())
				continue;
			for (int iEra = GC.getInfo(eLoopTech).getEra(); iEra < GC.getNumEraInfos(); iEra++)
				abAvailable[iEra] = 1;
		}
	}
	return (eEra >= 0 && eEra < (int)abAvailable.size() && abAvailable[eEra] != 0);
}

static int getSASGameRecordImprovementTechYieldByEra(ImprovementTypes eImprovement, YieldTypes eYield, EraTypes eEra)
{
	static std::vector<int> aiYield;
	int const iNumEras = GC.getNumEraInfos();
	int const iNumImprovements = GC.getNumImprovementInfos();
	if (aiYield.empty())
	{
		aiYield.assign(iNumEras * iNumImprovements * NUM_YIELD_TYPES, 0);
		for (int iEra = 0; iEra < iNumEras; iEra++)
		{
			for (int iImprovement = 0; iImprovement < iNumImprovements; iImprovement++)
			{
				FOR_EACH_ENUM(Yield)
				{
					int iValue = 0;
					FOR_EACH_ENUM(Tech)
					{
						if (GC.getInfo(eLoopTech).getEra() <= iEra)
							iValue += GC.getInfo((ImprovementTypes)iImprovement).getTechYieldChanges(eLoopTech, eLoopYield);
					}
					aiYield[(iEra * iNumImprovements + iImprovement) * NUM_YIELD_TYPES + eLoopYield] = iValue;
				}
			}
		}
	}
	if (eEra < 0 || eEra >= iNumEras || eImprovement < 0 || eImprovement >= iNumImprovements || eYield < 0 || eYield >= NUM_YIELD_TYPES)
		return 0;
	return aiYield[(eEra * iNumImprovements + eImprovement) * NUM_YIELD_TYPES + eYield];
}

static void getSASGameRecordLandmassPlotPotential(CvPlot const& kPlot, EraTypes eEra, int& iRawFood, int& iRawProduction, int& iRawCommerce, int& iRaw321, int& iPotentialFood, int& iPotentialProduction, int& iPotentialCommerce, int& iPotential321)
{
	BonusTypes const eBonus = kPlot.getBonusType(NO_TEAM);
	bool const bBonusRevealed = (eBonus != NO_BONUS && isSASGameRecordTechAvailableByEra(GC.getInfo(eBonus).getTechReveal(), eEra));
	int aiRaw[NUM_YIELD_TYPES] = { 0 };
	FOR_EACH_ENUM(Yield)
	{
		aiRaw[eLoopYield] = kPlot.calculateNatureYield(eLoopYield, NO_TEAM);
		if (bBonusRevealed)
			aiRaw[eLoopYield] += GC.getInfo(eBonus).getYieldChange(eLoopYield);
	}
	iRawFood = aiRaw[YIELD_FOOD];
	iRawProduction = aiRaw[YIELD_PRODUCTION];
	iRawCommerce = aiRaw[YIELD_COMMERCE];
	iRaw321 = 3 * iRawFood + 2 * iRawProduction + iRawCommerce;
	iPotentialFood = iRawFood;
	iPotentialProduction = iRawProduction;
	iPotentialCommerce = iRawCommerce;
	iPotential321 = iRaw321;
	if (!bBonusRevealed || !isSASGameRecordTechAvailableByEra(GC.getInfo(eBonus).getTechCityTrade(), eEra))
		return;
	bool const bIrrigationPotential = (isSASGameRecordIrrigationAvailableByEra(eEra) && kPlot.canHavePotentialIrrigation());
	FOR_EACH_ENUM(Build)
	{
		if (!isSASGameRecordBuildAvailableByEra(kPlot, eLoopBuild, eEra))
			continue;
		CvBuildInfo const& kBuild = GC.getInfo(eLoopBuild);
		ImprovementTypes const eImprovement = kBuild.getImprovement();
		CvImprovementInfo const& kImprovement = GC.getInfo(eImprovement);
		// <!-- custom: Ordinary Farm/Cottage/Mine/etc. choices encode city specialization rather than intrinsic geography. Only project an improvement when XML explicitly says that it connects this bonus, making the resource improvement a comparatively unambiguous part of the landmass's potential. (ChatGPT-5.6-Sol) -->
		if (!kImprovement.isImprovementBonusMakesValid(eBonus))
			continue;
		int aiYield[NUM_YIELD_TYPES] = { 0 };
		FOR_EACH_ENUM(Yield)
		{
			int iYield = kPlot.calculateNatureYield(eLoopYield, NO_TEAM, kPlot.getFeatureType() != NO_FEATURE && kBuild.isFeatureRemove(kPlot.getFeatureType()));
			iYield += GC.getInfo(eBonus).getYieldChange(eLoopYield);
			iYield += kImprovement.getYieldChange(eLoopYield);
			if (kPlot.isRiverSide())
				iYield += kImprovement.getRiverSideYieldChange(eLoopYield);
			if (kPlot.isHills())
				iYield += kImprovement.getHillsYieldChange(eLoopYield);
			if (bIrrigationPotential)
				iYield += kImprovement.getIrrigatedYieldChange(eLoopYield);
			iYield += getSASGameRecordImprovementTechYieldByEra(eImprovement, eLoopYield, eEra);
			iYield += kImprovement.getImprovementBonusYield(eBonus, eLoopYield);
			aiYield[eLoopYield] = std::max(0, iYield);
		}
		iPotentialFood = std::max(iPotentialFood, aiYield[YIELD_FOOD]);
		iPotentialProduction = std::max(iPotentialProduction, aiYield[YIELD_PRODUCTION]);
		iPotentialCommerce = std::max(iPotentialCommerce, aiYield[YIELD_COMMERCE]);
		iPotential321 = std::max(iPotential321, 3 * aiYield[YIELD_FOOD] + 2 * aiYield[YIELD_PRODUCTION] + aiYield[YIELD_COMMERCE]);
	}
}

static CvString getSASGameRecordEraLandmassYieldList(SASGameRecordLandmassGeography const& kLandmass, bool bBonusPotential)
{
	CvString szList;
	for (int iEra = 0; iEra < GC.getNumEraInfos(); iEra++)
	{
		if (kLandmass.iPlots <= 0)
			continue;
		std::vector<int> const& aiFood = (bBonusPotential ? kLandmass.aiEraBonusPotentialFood : kLandmass.aiEraRevealedRawFood);
		std::vector<int> const& aiProduction = (bBonusPotential ? kLandmass.aiEraBonusPotentialProduction : kLandmass.aiEraRevealedRawProduction);
		std::vector<int> const& aiCommerce = (bBonusPotential ? kLandmass.aiEraBonusPotentialCommerce : kLandmass.aiEraRevealedRawCommerce);
		std::vector<int> const& ai321 = (bBonusPotential ? kLandmass.aiEraBonusPotential321 : kLandmass.aiEraRevealedRaw321);
		CvString szItem;
		szItem.Format(szList.empty() ? "%s:%d/%d/%d/%d" : ",%s:%d/%d/%d/%d", GC.getInfo((EraTypes)iEra).getType(), (100 * aiFood[iEra]) / kLandmass.iPlots, (100 * aiProduction[iEra]) / kLandmass.iPlots, (100 * aiCommerce[iEra]) / kLandmass.iPlots, (100 * ai321[iEra]) / kLandmass.iPlots);
		szList += szItem;
	}
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordLandmassBonusTypes(SASGameRecordLandmassGeography const& kLandmass)
{
	CvString szTypes;
	for (int iBonus = 0; iBonus < (int)kLandmass.aiBonusCounts.size(); iBonus++)
	{
		if (kLandmass.aiBonusCounts[iBonus] <= 0)
			continue;
		appendSASGameRecordTypeCount(szTypes, getSASGameRecordBonusType((BonusTypes)iBonus), kLandmass.aiBonusCounts[iBonus]);
	}
	return getSASGameRecordOrDash(szTypes);
}

static void logSASGameRecordLandmassBonusCoordinates(SASGameRecordLandmassGeography const& kLandmass, CvString const& szLandmassName)
{
	std::vector<CvString> aszParts;
	CvString szPart;
	for (size_t iI = 0; iI < kLandmass.aszBonusCoordinates.size(); iI++)
	{
		CvString const& szItem = kLandmass.aszBonusCoordinates[iI];
		if (!szPart.empty() && szPart.length() + szItem.length() + 1 > 1200)
		{
			aszParts.push_back(szPart);
			szPart = "";
		}
		if (!szPart.empty())
			szPart += ";";
		szPart += szItem;
	}
	if (!szPart.empty())
		aszParts.push_back(szPart);
	if (aszParts.empty())
	{
		logSASGameRecord("GAME_RECORD_LANDMASS_BONUS_COORDS turn=%d landmass=%s part=1 parts=1 bonuses=-", GC.getGame().getGameTurn(), szLandmassName.GetCString());
		return;
	}
	for (size_t iI = 0; iI < aszParts.size(); iI++)
		logSASGameRecord("GAME_RECORD_LANDMASS_BONUS_COORDS turn=%d landmass=%s part=%d parts=%d bonuses=%s", GC.getGame().getGameTurn(), szLandmassName.GetCString(), (int)iI + 1, (int)aszParts.size(), aszParts[iI].GetCString());
}

// <!-- custom: Record a map-geography snapshot once per new/load context so autoplay analysis can distinguish crowded continents, isolated islands, coast-connected landmasses, terrain/feature composition, lake/sea structure, map-resource distribution, and underlying land quality without reconstructing the map from later city history.
// Landmass names use a deterministic anchor coordinate plus the Civ4 area ID; center coordinates are wrap-aware approximations. "habitable" uses CvPlot::isHabitable, while impassable and zero-natural-yield plots remain separate.
// Nature yields exclude bonuses. Per-era raw value adds a bonus only from its reveal era; conservative potential improves only revealed/connectable bonus plots through an XML-valid resource improvement, leaving ordinary non-bonus specialization choices untouched.
// Routes, civics and improvement maturation remain excluded because they are not intrinsic geography. (ChatGPT-5.6-Sol); or because they are available everywhere, so counting them or not has no extra strategic information value so do not count them. -->
static void addSASGameRecordNoOceanConnections(CvMap const& kMap, TerrainTypes eOcean, bool bSkipImpassable, std::vector<SASGameRecordLandmassGeography>& aLandmasses)
{
	std::vector<char> abVisited(kMap.numPlots(), 0);
	for (int iI = 0; iI < kMap.numPlots(); iI++)
	{
		CvPlot const& kStart = kMap.getPlotByIndex(iI);
		if (abVisited[iI] || !kStart.isWater() || kStart.getTerrainType() == eOcean || (bSkipImpassable && kStart.isImpassable()))
			continue;
		std::vector<int> aiQueue;
		std::vector<int> aiBorderLandAreas;
		abVisited[iI] = 1;
		aiQueue.push_back(iI);
		for (size_t iQ = 0; iQ < aiQueue.size(); iQ++)
		{
			CvPlot const& kWater = kMap.getPlotByIndex(aiQueue[iQ]);
			FOR_EACH_ADJ_PLOT(kWater)
			{
				if (!pAdj->isWater())
				{
					addSASGameRecordUniqueArea(aiBorderLandAreas, pAdj->getArea().getID());
					continue;
				}
				if (pAdj->getTerrainType() == eOcean || (bSkipImpassable && pAdj->isImpassable()))
					continue;
				int const iAdjIndex = kMap.plotNum(pAdj->getX(), pAdj->getY());
				if (iAdjIndex < 0 || abVisited[iAdjIndex])
					continue;
				abVisited[iAdjIndex] = 1;
				aiQueue.push_back(iAdjIndex);
			}
		}
		for (size_t iA = 0; iA < aiBorderLandAreas.size(); iA++)
		{
			SASGameRecordLandmassGeography* pLandmass = getSASGameRecordLandmassGeography(aLandmasses, aiBorderLandAreas[iA]);
			if (pLandmass == NULL)
				continue;
			for (size_t iB = 0; iB < aiBorderLandAreas.size(); iB++)
			{
				if (iA == iB)
					continue;
				if (bSkipImpassable)
					addSASGameRecordUniqueArea(pLandmass->aiNoOceanNavigableConnectedAreas, aiBorderLandAreas[iB]);
				else addSASGameRecordUniqueArea(pLandmass->aiNoOceanConnectedAreas, aiBorderLandAreas[iB]);
			}
		}
	}
}

static void logSASGameRecordGeography()
{
	CvMap const& kMap = GC.getMap();
	std::vector<SASGameRecordLandmassGeography> aLandmasses;
	int iLandPlots = 0;
	int iWaterPlots = 0;
	int iSeaPlots = 0;
	int iLakePlots = 0;
	int iCoastSeaPlots = 0;
	int iOceanSeaPlots = 0;
	int iOtherSeaPlots = 0;
	int iIcePlots = 0;
	int iIceSeaPlots = 0;
	int iIceLakePlots = 0;
	int iIceCoastSeaPlots = 0;
	int iIceOceanSeaPlots = 0;
	int iWaterAreas = 0;
	int iSeaAreas = 0;
	int iLakeAreas = 0;
	TerrainTypes const eCoast = (TerrainTypes)GC.getInfoTypeForString("TERRAIN_COAST");
	TerrainTypes const eOcean = (TerrainTypes)GC.getInfoTypeForString("TERRAIN_OCEAN");
	FeatureTypes const eIce = (FeatureTypes)GC.getInfoTypeForString("FEATURE_ICE");
	int iLoop = 0;
	for (CvArea const* pLoopArea = kMap.firstArea(&iLoop); pLoopArea != NULL; pLoopArea = kMap.nextArea(&iLoop))
	{
		if (pLoopArea->isWater())
		{
			iWaterAreas++;
			if (pLoopArea->isLake())
				iLakeAreas++;
			else iSeaAreas++;
			continue;
		}
		SASGameRecordLandmassGeography kLandmass;
		kLandmass.iAreaId = pLoopArea->getID();
		kLandmass.aiTerrainCounts.assign(GC.getNumTerrainInfos(), 0);
		kLandmass.aiFeatureCounts.assign(GC.getNumFeatureInfos(), 0);
		kLandmass.aiBonusCounts.assign(GC.getNumBonusInfos(), 0);
		kLandmass.aiEraRevealedRawFood.assign(GC.getNumEraInfos(), 0);
		kLandmass.aiEraRevealedRawProduction.assign(GC.getNumEraInfos(), 0);
		kLandmass.aiEraRevealedRawCommerce.assign(GC.getNumEraInfos(), 0);
		kLandmass.aiEraRevealedRaw321.assign(GC.getNumEraInfos(), 0);
		kLandmass.aiEraBonusPotentialFood.assign(GC.getNumEraInfos(), 0);
		kLandmass.aiEraBonusPotentialProduction.assign(GC.getNumEraInfos(), 0);
		kLandmass.aiEraBonusPotentialCommerce.assign(GC.getNumEraInfos(), 0);
		kLandmass.aiEraBonusPotential321.assign(GC.getNumEraInfos(), 0);
		aLandmasses.push_back(kLandmass);
	}
	for (int iI = 0; iI < kMap.numPlots(); iI++)
	{
		CvPlot const& kPlot = kMap.getPlotByIndex(iI);
		if (kPlot.isWater())
		{
			iWaterPlots++;
			bool const bIce = (eIce != NO_FEATURE && kPlot.getFeatureType() == eIce);
			if (bIce)
				iIcePlots++;
			if (kPlot.isLake())
			{
				iLakePlots++;
				if (bIce)
					iIceLakePlots++;
				FOR_EACH_ADJ_PLOT(kPlot)
				{
					if (pAdj->isWater())
						continue;
					SASGameRecordLandmassGeography* pAdjacentLandmass = getSASGameRecordLandmassGeography(aLandmasses, pAdj->getArea().getID());
					if (pAdjacentLandmass != NULL)
						addSASGameRecordUniqueArea(pAdjacentLandmass->aiAdjacentLakeAreas, kPlot.getArea().getID());
				}
			}
			else
			{
				iSeaPlots++;
				if (bIce)
					iIceSeaPlots++;
				if (kPlot.getTerrainType() == eCoast)
				{
					iCoastSeaPlots++;
					if (bIce)
						iIceCoastSeaPlots++;
				}
				else if (kPlot.getTerrainType() == eOcean)
				{
					iOceanSeaPlots++;
					if (bIce)
						iIceOceanSeaPlots++;
				}
				else iOtherSeaPlots++;
			}
			continue;
		}
		iLandPlots++;
		SASGameRecordLandmassGeography* pLandmass = getSASGameRecordLandmassGeography(aLandmasses, kPlot.getArea().getID());
		if (pLandmass == NULL)
			continue;
		if (pLandmass->iPlots == 0)
		{
			pLandmass->iAnchorX = kPlot.getX();
			pLandmass->iAnchorY = kPlot.getY();
		}
		pLandmass->iPlots++;
		if (kPlot.getTerrainType() != NO_TERRAIN)
			pLandmass->aiTerrainCounts[kPlot.getTerrainType()]++;
		if (kPlot.getFeatureType() != NO_FEATURE)
			pLandmass->aiFeatureCounts[kPlot.getFeatureType()]++;
		if (kPlot.isHills())
			pLandmass->iHillsPlots++;
		if (kPlot.isPeak())
			pLandmass->iPeakPlots++;
		if (kPlot.isRiverSide())
			pLandmass->iRiverSidePlots++;
		if (kPlot.isFreshWater())
			pLandmass->iFreshWaterPlots++;
		pLandmass->iSumWrappedDX += kMap.dxWrap(kPlot.getX() - pLandmass->iAnchorX);
		pLandmass->iSumWrappedDY += kMap.dyWrap(kPlot.getY() - pLandmass->iAnchorY);
		if (kPlot.isHabitable())
			pLandmass->iHabitablePlots++;
		if (kPlot.isImpassable())
			pLandmass->iImpassablePlots++;
		int const iNatureFood = kPlot.calculateNatureYield(YIELD_FOOD, NO_TEAM);
		int const iNatureProduction = kPlot.calculateNatureYield(YIELD_PRODUCTION, NO_TEAM);
		int const iNatureCommerce = kPlot.calculateNatureYield(YIELD_COMMERCE, NO_TEAM);
		if (iNatureFood + iNatureProduction + iNatureCommerce <= 0)
			pLandmass->iZeroNatureYieldPlots++;
		pLandmass->iNatureFood += iNatureFood;
		pLandmass->iNatureProduction += iNatureProduction;
		pLandmass->iNatureCommerce += iNatureCommerce;
		BonusTypes const eBonus = kPlot.getBonusType(NO_TEAM);
		if (eBonus != NO_BONUS)
		{
			pLandmass->iBonusCount++;
			if (eBonus >= 0 && eBonus < (int)pLandmass->aiBonusCounts.size())
				pLandmass->aiBonusCounts[eBonus]++;
			CvString szBonus;
			szBonus.Format("%s@%d,%d", getSASGameRecordBonusType(eBonus), kPlot.getX(), kPlot.getY());
			pLandmass->aszBonusCoordinates.push_back(szBonus);
		}
		for (int iEra = 0; iEra < GC.getNumEraInfos(); iEra++)
		{
			int iRawFood = 0;
			int iRawProduction = 0;
			int iRawCommerce = 0;
			int iRaw321 = 0;
			int iPotentialFood = 0;
			int iPotentialProduction = 0;
			int iPotentialCommerce = 0;
			int iPotential321 = 0;
			getSASGameRecordLandmassPlotPotential(kPlot, (EraTypes)iEra, iRawFood, iRawProduction, iRawCommerce, iRaw321, iPotentialFood, iPotentialProduction, iPotentialCommerce, iPotential321);
			pLandmass->aiEraRevealedRawFood[iEra] += iRawFood;
			pLandmass->aiEraRevealedRawProduction[iEra] += iRawProduction;
			pLandmass->aiEraRevealedRawCommerce[iEra] += iRawCommerce;
			pLandmass->aiEraRevealedRaw321[iEra] += iRaw321;
			pLandmass->aiEraBonusPotentialFood[iEra] += iPotentialFood;
			pLandmass->aiEraBonusPotentialProduction[iEra] += iPotentialProduction;
			pLandmass->aiEraBonusPotentialCommerce[iEra] += iPotentialCommerce;
			pLandmass->aiEraBonusPotential321[iEra] += iPotential321;
		}
		bool bBordersWater = false;
		bool bBordersSea = false;
		bool bBordersLake = false;
		bool bBordersIce = false;
		FOR_EACH_ADJ_PLOT(kPlot)
		{
			if (!pAdj->isWater())
				continue;
			bBordersWater = true;
			if (pAdj->isLake())
			{
				bBordersLake = true;
				pLandmass->iLakeBorderEdges++;
			}
			else
			{
				bBordersSea = true;
				pLandmass->iSeaBorderEdges++;
			}
			if (eIce != NO_FEATURE && pAdj->getFeatureType() == eIce)
			{
				bBordersIce = true;
				pLandmass->iIceBorderEdges++;
			}
		}
		if (bBordersWater) pLandmass->iWaterBorderPlots++;
		if (bBordersSea) pLandmass->iSeaBorderPlots++;
		if (bBordersLake) pLandmass->iLakeBorderPlots++;
		if (bBordersIce) pLandmass->iIceBorderPlots++;
	}
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kPlayer = GET_PLAYER(eLoopPlayer);
		CvPlot const* pStart = kPlayer.getStartingPlot();
		if (!kPlayer.isEverAlive() || kPlayer.isBarbarian() || pStart == NULL || pStart->isWater())
			continue;
		SASGameRecordLandmassGeography* pLandmass = getSASGameRecordLandmassGeography(aLandmasses, pStart->getArea().getID());
		if (pLandmass == NULL)
			continue;
		pLandmass->iStartingPlayers++;
		CvString szItem;
		szItem.Format(pLandmass->szStartingPlayers.empty() ? "%d@%d,%d" : ";%d@%d,%d", eLoopPlayer, pStart->getX(), pStart->getY());
		pLandmass->szStartingPlayers += szItem;
	}
	if (eOcean != NO_TERRAIN)
	{
		// <!-- custom: Keep terrain-only coastal connectivity for shape/topology, then separately exclude impassable water (currently Ice) to capture what ordinary pre-ocean sea units can actually traverse. (ChatGPT-5.6-Sol) -->
		addSASGameRecordNoOceanConnections(kMap, eOcean, false, aLandmasses);
		addSASGameRecordNoOceanConnections(kMap, eOcean, true, aLandmasses);
	}

	int iLargestAreaId = -1;
	int iLargestAreaPlots = 0;
	for (size_t iI = 0; iI < aLandmasses.size(); iI++)
	{
		if (aLandmasses[iI].iPlots > iLargestAreaPlots)
		{
			iLargestAreaPlots = aLandmasses[iI].iPlots;
			iLargestAreaId = aLandmasses[iI].iAreaId;
		}
	}
	CvString szLargestLandmass = "-";
	SASGameRecordLandmassGeography* pLargestLandmass = getSASGameRecordLandmassGeography(aLandmasses, iLargestAreaId);
	if (pLargestLandmass != NULL)
		szLargestLandmass = getSASGameRecordLandmassName(*pLargestLandmass);
	int const iMapPlots = iLandPlots + iWaterPlots;
	logSASGameRecord("GAME_RECORD_GEOGRAPHY_SUMMARY turn=%d landmasses=%d waterAreas=%d seaAreas=%d lakeAreas=%d mapPlots=%d landPlots=%d landPercentOfMapX100=%d waterPlots=%d waterPercentOfMapX100=%d seaPlots=%d seaPercentOfMapX100=%d coastSeaPlots=%d coastSeaPercentOfMapX100=%d oceanSeaPlots=%d oceanSeaPercentOfMapX100=%d otherSeaPlots=%d lakePlots=%d lakePercentOfMapX100=%d icePlots=%d icePercentOfMapX100=%d icePercentOfWaterX100=%d iceSeaPlots=%d icePercentOfSeaX100=%d iceCoastSeaPlots=%d iceOceanSeaPlots=%d iceLakePlots=%d largestLandmass=%s largestLandmassPlots=%d wrapX=%d wrapY=%d coastTerrain=%s oceanTerrain=%s iceFeature=%s",
			GC.getGame().getGameTurn(), (int)aLandmasses.size(), iWaterAreas, iSeaAreas, iLakeAreas, iMapPlots, iLandPlots, getSASGameRecordPercentX100(iLandPlots, iMapPlots), iWaterPlots, getSASGameRecordPercentX100(iWaterPlots, iMapPlots), iSeaPlots, getSASGameRecordPercentX100(iSeaPlots, iMapPlots), iCoastSeaPlots, getSASGameRecordPercentX100(iCoastSeaPlots, iMapPlots), iOceanSeaPlots, getSASGameRecordPercentX100(iOceanSeaPlots, iMapPlots), iOtherSeaPlots, iLakePlots, getSASGameRecordPercentX100(iLakePlots, iMapPlots), iIcePlots, getSASGameRecordPercentX100(iIcePlots, iMapPlots), getSASGameRecordPercentX100(iIcePlots, iWaterPlots), iIceSeaPlots, getSASGameRecordPercentX100(iIceSeaPlots, iSeaPlots), iIceCoastSeaPlots, iIceOceanSeaPlots, iIceLakePlots,
			szLargestLandmass.GetCString(), iLargestAreaPlots, kMap.isWrapX(), kMap.isWrapY(), eCoast == NO_TERRAIN ? "-" : GC.getInfo(eCoast).getType(), eOcean == NO_TERRAIN ? "-" : GC.getInfo(eOcean).getType(), eIce == NO_FEATURE ? "-" : GC.getInfo(eIce).getType());
	logSASGameRecord("GAME_RECORD_GEOGRAPHY_YIELD_LEGEND nature=terrain_feature_hills_river_without_bonus revealedRaw=nature_plus_bonus_base_yield_from_reveal_era bonusImprovedPotential=revealedRaw_plus_only_XML_valid_bonus_improvement_after_reveal_connection_and_build_tech nonBonusPlots=never_improvement_optimized routesCivicsMaturation=excluded potentialIrrigation=allowed_on_valid_bonus_improvement improvementTechYieldChanges=included score321=3F+2H+C averageScale=100 eraFormat=ERA:F/H/C/321");
	logSASGameRecord("GAME_RECORD_GEOGRAPHY_COMPOSITION_LEGEND percentScale=100 terrainPercentDenominator=landmassPlots featurePercentDenominator=landmassPlots featurelessPercent=plots_without_feature waterBorderLand=land_plots_adjacent_to_any_water seaBorderLand=land_plots_adjacent_to_nonlake_water lakeBorderLand=land_plots_adjacent_to_lake_water borderEdgesPerLandX100=adjacent_land_water_edges_per_land_plot_times_100 iceBorderLand=land_plots_adjacent_to_FEATURE_ICE adjacentLakePlots=unique_lake_area_tiles_touching_landmass adjacentLakePerLandPercentDenominator=landmassPlots noOceanConnected=non_ocean_water_topology_ignoring_impassable_features noOceanNavigable=non_ocean_water_excluding_impassable_plots sea=water_excluding_lakes coastSea=nonlake_TERRAIN_COAST oceanSea=nonlake_TERRAIN_OCEAN");
	for (size_t iI = 0; iI < aLandmasses.size(); iI++)
	{
		SASGameRecordLandmassGeography const& kLandmass = aLandmasses[iI];
		if (kLandmass.iPlots <= 0)
			continue;
		int iCenterX100 = kLandmass.iAnchorX * 100 + (100 * kLandmass.iSumWrappedDX) / kLandmass.iPlots;
		int iCenterY100 = kLandmass.iAnchorY * 100 + (100 * kLandmass.iSumWrappedDY) / kLandmass.iPlots;
		if (kMap.isWrapX())
		{
			int const iWidthX100 = kMap.getGridWidth() * 100;
			while (iCenterX100 < 0) iCenterX100 += iWidthX100;
			while (iCenterX100 >= iWidthX100) iCenterX100 -= iWidthX100;
		}
		if (kMap.isWrapY())
		{
			int const iHeightX100 = kMap.getGridHeight() * 100;
			while (iCenterY100 < 0) iCenterY100 += iHeightX100;
			while (iCenterY100 >= iHeightX100) iCenterY100 -= iHeightX100;
		}
		CvString const szName = getSASGameRecordLandmassName(kLandmass);
		logSASGameRecord("GAME_RECORD_LANDMASS turn=%d landmass=%s area=%d anchor=%d,%d centerX100=%d centerY100=%d plots=%d landSharePercentX100=%d habitablePlots=%d nonHabitablePlots=%d impassablePlots=%d zeroNatureYieldPlots=%d waterBorderPlots=%d seaBorderPlots=%d lakeBorderPlots=%d startingPlayers=%d starts=%s noOceanConnectedCount=%d noOceanConnectedTo=%s",
				GC.getGame().getGameTurn(), szName.GetCString(), kLandmass.iAreaId, kLandmass.iAnchorX, kLandmass.iAnchorY, iCenterX100, iCenterY100, kLandmass.iPlots, getSASGameRecordPercentX100(kLandmass.iPlots, iLandPlots), kLandmass.iHabitablePlots, kLandmass.iPlots - kLandmass.iHabitablePlots, kLandmass.iImpassablePlots, kLandmass.iZeroNatureYieldPlots, kLandmass.iWaterBorderPlots, kLandmass.iSeaBorderPlots, kLandmass.iLakeBorderPlots, kLandmass.iStartingPlayers, getSASGameRecordOrDash(kLandmass.szStartingPlayers).GetCString(), (int)kLandmass.aiNoOceanConnectedAreas.size(), getSASGameRecordLandmassList(aLandmasses, kLandmass.aiNoOceanConnectedAreas).GetCString());
		std::vector<int> aiIceBlockedNoOceanAreas;
		for (size_t iConnection = 0; iConnection < kLandmass.aiNoOceanConnectedAreas.size(); iConnection++)
		{
			int const iAreaId = kLandmass.aiNoOceanConnectedAreas[iConnection];
			if (std::find(kLandmass.aiNoOceanNavigableConnectedAreas.begin(), kLandmass.aiNoOceanNavigableConnectedAreas.end(), iAreaId) == kLandmass.aiNoOceanNavigableConnectedAreas.end())
				aiIceBlockedNoOceanAreas.push_back(iAreaId);
		}
		logSASGameRecord("GAME_RECORD_LANDMASS_NAVIGATION turn=%d landmass=%s noOceanNavigableConnectedCount=%d iceBlockedNoOceanCount=%d iceBlockedNoOceanTo=%s",
				GC.getGame().getGameTurn(), szName.GetCString(), (int)kLandmass.aiNoOceanNavigableConnectedAreas.size(), (int)aiIceBlockedNoOceanAreas.size(), getSASGameRecordLandmassList(aLandmasses, aiIceBlockedNoOceanAreas).GetCString());
		int iFeaturePlots = 0;
		for (size_t iFeature = 0; iFeature < kLandmass.aiFeatureCounts.size(); iFeature++)
			iFeaturePlots += kLandmass.aiFeatureCounts[iFeature];
		int const iAdjacentLakePlots = getSASGameRecordAdjacentLakePlots(kLandmass);
		logSASGameRecord("GAME_RECORD_LANDMASS_COMPOSITION turn=%d landmass=%s hillsPercentX100=%d peakPercentX100=%d riverSidePercentX100=%d freshWaterPercentX100=%d waterBorderLandPercentX100=%d seaBorderLandPercentX100=%d lakeBorderLandPercentX100=%d iceBorderLandPercentX100=%d seaBorderEdgesPerLandX100=%d lakeBorderEdgesPerLandX100=%d iceBorderEdgesPerLandX100=%d featurelessPercentX100=%d adjacentLakePlots=%d adjacentLakePerLandPercentX100=%d terrainPercentX100=%s featurePercentX100=%s",
				GC.getGame().getGameTurn(), szName.GetCString(), getSASGameRecordPercentX100(kLandmass.iHillsPlots, kLandmass.iPlots), getSASGameRecordPercentX100(kLandmass.iPeakPlots, kLandmass.iPlots), getSASGameRecordPercentX100(kLandmass.iRiverSidePlots, kLandmass.iPlots), getSASGameRecordPercentX100(kLandmass.iFreshWaterPlots, kLandmass.iPlots),
				getSASGameRecordPercentX100(kLandmass.iWaterBorderPlots, kLandmass.iPlots), getSASGameRecordPercentX100(kLandmass.iSeaBorderPlots, kLandmass.iPlots), getSASGameRecordPercentX100(kLandmass.iLakeBorderPlots, kLandmass.iPlots), getSASGameRecordPercentX100(kLandmass.iIceBorderPlots, kLandmass.iPlots), (100 * kLandmass.iSeaBorderEdges) / kLandmass.iPlots, (100 * kLandmass.iLakeBorderEdges) / kLandmass.iPlots, (100 * kLandmass.iIceBorderEdges) / kLandmass.iPlots, getSASGameRecordPercentX100(kLandmass.iPlots - iFeaturePlots, kLandmass.iPlots), iAdjacentLakePlots, getSASGameRecordPercentX100(iAdjacentLakePlots, kLandmass.iPlots), getSASGameRecordLandmassTerrainPercentages(kLandmass).GetCString(), getSASGameRecordLandmassFeaturePercentages(kLandmass).GetCString());
		int const iFinalEra = GC.getNumEraInfos() - 1;
		int const iNature321 = 3 * kLandmass.iNatureFood + 2 * kLandmass.iNatureProduction + kLandmass.iNatureCommerce;
		logSASGameRecord("GAME_RECORD_LANDMASS_YIELDS turn=%d landmass=%s natureAvgF100=%d natureAvgH100=%d natureAvgC100=%d natureAvg321X100=%d revealedRawFinalAvgF100=%d revealedRawFinalAvgH100=%d revealedRawFinalAvgC100=%d revealedRawFinalAvg321X100=%d bonusImprovedPotentialFinalAvgF100=%d bonusImprovedPotentialFinalAvgH100=%d bonusImprovedPotentialFinalAvgC100=%d bonusImprovedPotentialFinalAvg321X100=%d eraRevealedRawAvgFHC321X100=%s eraBonusImprovedPotentialAvgFHC321X100=%s",
				GC.getGame().getGameTurn(), szName.GetCString(), (100 * kLandmass.iNatureFood) / kLandmass.iPlots, (100 * kLandmass.iNatureProduction) / kLandmass.iPlots, (100 * kLandmass.iNatureCommerce) / kLandmass.iPlots, (100 * iNature321) / kLandmass.iPlots,
				iFinalEra < 0 ? 0 : (100 * kLandmass.aiEraRevealedRawFood[iFinalEra]) / kLandmass.iPlots, iFinalEra < 0 ? 0 : (100 * kLandmass.aiEraRevealedRawProduction[iFinalEra]) / kLandmass.iPlots, iFinalEra < 0 ? 0 : (100 * kLandmass.aiEraRevealedRawCommerce[iFinalEra]) / kLandmass.iPlots, iFinalEra < 0 ? 0 : (100 * kLandmass.aiEraRevealedRaw321[iFinalEra]) / kLandmass.iPlots,
				iFinalEra < 0 ? 0 : (100 * kLandmass.aiEraBonusPotentialFood[iFinalEra]) / kLandmass.iPlots, iFinalEra < 0 ? 0 : (100 * kLandmass.aiEraBonusPotentialProduction[iFinalEra]) / kLandmass.iPlots, iFinalEra < 0 ? 0 : (100 * kLandmass.aiEraBonusPotentialCommerce[iFinalEra]) / kLandmass.iPlots, iFinalEra < 0 ? 0 : (100 * kLandmass.aiEraBonusPotential321[iFinalEra]) / kLandmass.iPlots, getSASGameRecordEraLandmassYieldList(kLandmass, false).GetCString(), getSASGameRecordEraLandmassYieldList(kLandmass, true).GetCString());
		logSASGameRecord("GAME_RECORD_LANDMASS_BONUS_SUMMARY turn=%d landmass=%s bonusCount=%d types=%s", GC.getGame().getGameTurn(), szName.GetCString(), kLandmass.iBonusCount, getSASGameRecordLandmassBonusTypes(kLandmass).GetCString());
		logSASGameRecordLandmassBonusCoordinates(kLandmass, szName);
	}
}

static void logSASGameRecordInitialContext()
{
	// <!-- custom: Archived records can otherwise be mistaken for logs from another Civ4 mod. Record the active cached mod folder name and mod-relative path once, without relying on file timestamps or a manually maintained version string. (GPT-5.6-Sol) -->
	logSASGameRecord("GAME_RECORD_MOD_CONTEXT modName=%s modPath=%s", getSASGameRecordQuoted(GC.getModName().getName()).GetCString(), getSASGameRecordQuoted(GC.getModName().getPathInRoot()).GetCString());
	// <!-- custom: Player/team IDs appear throughout the record, but live-player counts do not reveal where ordinary civilization slots end and the special Barbarian slots begin. Record the fixed DLL boundaries once at setup so external analysis can interpret every later ID correctly. (GPT-5.6-Sol) -->
	logSASGameRecord("GAME_RECORD_SLOT_CONSTANTS MAX_CIV_PLAYERS=%d MAX_PLAYERS=%d BARBARIAN_PLAYER=%d MAX_CIV_TEAMS=%d MAX_TEAMS=%d BARBARIAN_TEAM=%d NO_PLAYER=%d NO_TEAM=%d", MAX_CIV_PLAYERS, MAX_PLAYERS, BARBARIAN_PLAYER, MAX_CIV_TEAMS, MAX_TEAMS, BARBARIAN_TEAM, NO_PLAYER, NO_TEAM);
	logSASGameRecordGeography();
	if (gGameRecordLogLevel >= 2) logSASGameRecordAttitudeLegend();
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (kLoopPlayer.isEverAlive() && !kLoopPlayer.isBarbarian())
			logSASGameRecordPlayerSetup(eLoopPlayer);
	}
	if (gGameRecordLogLevel < 2)
		return;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (!kLoopPlayer.isAlive() || kLoopPlayer.isBarbarian())
			continue;
		logSASGameRecordKnownArea(eLoopPlayer, "setup");
		logSASGameRecordStartingUnits(eLoopPlayer, "setup");
		int iLoop = 0;
		for (CvCity const* pLoopCity = kLoopPlayer.firstCity(&iLoop); pLoopCity != NULL; pLoopCity = kLoopPlayer.nextCity(&iLoop))
			logSASGameRecordCityBFC(*pLoopCity, "setup");
	}
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (GET_TEAM(eLoopTeam).isAlive() && !GET_TEAM(eLoopTeam).isBarbarian())
			logSASGameRecordTeamContacts(eLoopTeam, GC.getGame().getGameTurn(), "setup");
	}
}

static void logSASGameRecordMapBonusTotals(int iGameTurn)
{
	CvString szBonuses;
	FOR_EACH_ENUM(Bonus)
		appendSASGameRecordTypeCount(szBonuses, getSASGameRecordBonusType(eLoopBonus), GC.getMap().getNumBonuses(eLoopBonus));
	logSASGameRecord("GAME_RECORD_MAP_BONUSES turn=%d total=%s", iGameTurn, getSASGameRecordOrDash(szBonuses).GetCString());
}

static void logSASGameRecordTeamProjects(TeamTypes eTeam, int iGameTurn);

static void logSASGameRecordBattleBuckets(int iGameTurn)
{
	const int iStartTurn = std::max(0, iGameTurn - getSASGameRecordTurnInterval() + 1);
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		if (g_aiSASGameRecordBattleWins[iI] == 0 && g_aiSASGameRecordBattleLosses[iI] == 0 && g_aiSASGameRecordCityBattleWins[iI] == 0 && g_aiSASGameRecordCityBattleLosses[iI] == 0)
			continue;
		logSASGameRecord("GAME_RECORD_BATTLE_SUMMARY turn=%d range=%d-%d player=%d wins=%d losses=%d cityPlotWins=%d cityPlotLosses=%d",
				iGameTurn, iStartTurn, iGameTurn, eLoopPlayer, g_aiSASGameRecordBattleWins[iI], g_aiSASGameRecordBattleLosses[iI], g_aiSASGameRecordCityBattleWins[iI], g_aiSASGameRecordCityBattleLosses[iI]);
		g_aiSASGameRecordBattleWins[iI] = 0;
		g_aiSASGameRecordBattleLosses[iI] = 0;
		g_aiSASGameRecordCityBattleWins[iI] = 0;
		g_aiSASGameRecordCityBattleLosses[iI] = 0;
	}
}

// <!-- custom: Project completion rows did not show whether a project-based victory had its minimum/full component set or an active launch countdown. Build one compact shared state for periodic progress and the explicit launch action. (GPT-5.6-Sol) -->
static bool getSASGameRecordVictoryProjectState(TeamTypes eTeam, VictoryTypes eVictory, int& iPartsBuilt, int& iPartsMinimum, int& iPartsMaximum, bool& bMinimumComplete, CvString& szProjectParts)
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
		szItem.Format(szProjectParts.empty() ? "%s:%d/%d/%d" : ",%s:%d/%d/%d", getSASGameRecordProjectType(eLoopProject), iBuilt, iMinimum, iMaximum);
		szProjectParts += szItem;
	}
	return !szProjectParts.empty();
}

static char const* getSASGameRecordVictoryType(VictoryTypes eVictory)
{
	return eVictory == NO_VICTORY ? "-" : GC.getInfo(eVictory).getType();
}

typedef std::pair<int, CvCity const*> SASGameRecordCultureCity;

static bool compareSASGameRecordCultureCities(SASGameRecordCultureCity const& kFirst, SASGameRecordCultureCity const& kSecond)
{
	return kFirst.first > kSecond.first;
}

static CvString getSASGameRecordCultureVictoryCities(TeamTypes eTeam, int iRequired, int iThreshold, int& iComplete)
{
	std::vector<SASGameRecordCultureCity> aCities;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		CvPlayer const& kMember = GET_PLAYER((PlayerTypes)iI);
		if (!kMember.isAlive() || kMember.getTeam() != eTeam)
			continue;
		int iLoop = 0;
		for (CvCity const* pCity = kMember.firstCity(&iLoop); pCity != NULL; pCity = kMember.nextCity(&iLoop))
			aCities.push_back(std::make_pair(pCity->getCulture(pCity->getOwner()), pCity));
	}
	std::sort(aCities.begin(), aCities.end(), compareSASGameRecordCultureCities);
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
	return getSASGameRecordOrDash(szCities);
}

static void logSASGameRecordTeamSnapshot(TeamTypes eTeam, int iGameTurn)
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
	SASGameRecordTeamPrevious& kPrevious = g_akSASGameRecordTeamPrevious[eTeam];
	TeamTypes eMaster = getSASGameRecordMasterTeam(eTeam);
	logSASGameRecord("GAME_RECORD_TEAM turn=%d team=%d members=%s alive=%d deltaValid=%d techs=%d techsDelta=%+d techEraCounts=%s techTrading=%d goldTrading=%d land=%d landDelta=%+d landPctX100=%d landPctX100Delta=%+d pop=%d popDelta=%+d popPctX100=%d popPctX100Delta=%+d wars=%s vassals=%s master=%d",
			iGameTurn, eTeam, getSASGameRecordTeamMembers(eTeam).GetCString(), kTeam.isAlive(), kPrevious.bValid, iTechs, getSASGameRecordDelta(kPrevious.bValid, iTechs, kPrevious.iTechs), getSASGameRecordTechEraCounts(eTeam).GetCString(), kTeam.isTechTrading(), kTeam.isGoldTrading(), iLand, getSASGameRecordDelta(kPrevious.bValid, iLand, kPrevious.iLand), iLandPctX100, getSASGameRecordDelta(kPrevious.bValid, iLandPctX100, kPrevious.iLandPctX100), iPopulation, getSASGameRecordDelta(kPrevious.bValid, iPopulation, kPrevious.iPopulation), iPopPctX100, getSASGameRecordDelta(kPrevious.bValid, iPopPctX100, kPrevious.iPopPctX100), getSASGameRecordWarTeams(eTeam).GetCString(), getSASGameRecordVassalTeams(eTeam).GetCString(), eMaster);
	if (gGameRecordLogLevel >= 2) logSASGameRecordTeamContacts(eTeam, iGameTurn, "snapshot");
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
			appendSASGameRecordIntList(szConquestRivals, eRival);
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
	else szCultureCities = getSASGameRecordCultureVictoryCities(eTeam, iCultureCitiesRequired, iCultureThreshold, iCultureCitiesComplete);
	// <!-- custom: Domination and Space already have detailed per-victory rows, and diplomatic vote-source rows already contain exact vote thresholds.
	// Add one compact general row per team rather than one new row per missing victory, so Score/Time, Conquest, and Cultural progress become explicit without multiplying snapshot noise.
	// Culture lists only the required number of leading cities. (GPT-5.6-Sol) -->
	logSASGameRecord("GAME_RECORD_VICTORY_PROGRESS_GENERAL turn=%d team=%d scoreVictory=%s timeVictory=%s conquestVictory=%s culturalVictory=%s diplomaticVictory=%s teamScore=%d bestRivalScore=%d scoreLead=%+d targetScore=%d turnsRemaining=%d conquestRivals=%s conquestRivalCities=%d cultureCitiesComplete=%d cultureCitiesRequired=%d cultureThreshold=%d cultureCities=%s",
			iGameTurn, eTeam, getSASGameRecordVictoryType(eScoreVictory), getSASGameRecordVictoryType(eTimeVictory), getSASGameRecordVictoryType(eConquestVictory), getSASGameRecordVictoryType(eCultureVictory), getSASGameRecordVictoryType(eDiplomaticVictory),
			iTeamScore, iBestRivalScore, iBestRivalScore < 0 ? iTeamScore : iTeamScore - iBestRivalScore, kGame.getTargetScore(), iTurnsRemaining, getSASGameRecordOrDash(szConquestRivals).GetCString(), iConquestRivalCities,
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
		bool const bProjectVictory = getSASGameRecordVictoryProjectState(eTeam, eLoopVictory, iPartsBuilt, iPartsMinimum, iPartsMaximum, bMinimumComplete, szProjectParts);
		if (iLandNeed > 0 || iPopNeed > 0 || bProjectVictory)
		{
			int const iCountdown = kTeam.getVictoryCountdown(eLoopVictory);
			int const iTravelTurns = (bProjectVictory && bMinimumComplete ? kTeam.getVictoryDelay(eLoopVictory) : -1);
			logSASGameRecord("GAME_RECORD_VICTORY_PROGRESS turn=%d team=%d victory=%s landPctX100=%d landNeed=%d popPctX100=%d popNeed=%d projectVictory=%d launched=%d countdown=%d arrivalTurn=%d canLaunch=%d launchSuccessPercent=%d travelTurns=%d partsBuilt=%d partsMinimum=%d partsMaximum=%d projectParts=%s",
				iGameTurn, eTeam, GC.getInfo(eLoopVictory).getType(), iLandPctX100, iLandNeed, iPopPctX100, iPopNeed, bProjectVictory, bProjectVictory && iCountdown >= 0, iCountdown, iCountdown < 0 ? -1 : iGameTurn + iCountdown, bProjectVictory && kTeam.canLaunch(eLoopVictory), bProjectVictory ? kTeam.getLaunchSuccessRate(eLoopVictory) : -1, iTravelTurns, iPartsBuilt, iPartsMinimum, iPartsMaximum, bProjectVictory ? szProjectParts.GetCString() : "-");
		}
	}
	if (gGameRecordLogLevel >= 2) logSASGameRecordTeamProjects(eTeam, iGameTurn);
}



static CvString getSASGameRecordCivicList(CvPlayer const& kPlayer)
{
	CvString szList;
	FOR_EACH_ENUM(CivicOption)
	{
		CivicTypes eCivic = kPlayer.getCivics(eLoopCivicOption);
		if (eCivic == NO_CIVIC)
			continue;
		CvString szItem;
		szItem.Format(szList.empty() ? "%s:%s" : ",%s:%s", GC.getInfo(eLoopCivicOption).getType(), getSASGameRecordCivicType(eCivic));
		szList += szItem;
	}
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordPlayerCityReligions(CvPlayer const& kPlayer)
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
		appendSASGameRecordTypeCount(szList, getSASGameRecordReligionType(eLoopReligion), aiCounts[eLoopReligion]);
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordPlayerCityCorporations(CvPlayer const& kPlayer)
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
		appendSASGameRecordTypeCount(szList, getSASGameRecordCorporationType(eLoopCorporation), aiCounts[eLoopCorporation]);
	return getSASGameRecordOrDash(szList);
}

// <!-- custom: City health/happiness rows previously combined player-wide modifiers under `extra`, hiding whether a loaded-mod rule caused a demographic change; for example, AdvCiv-SAS's TECH_DEPOPULATION currently applies negative health and happiness.
// Reconstruct all currently defined trait, civic and technology contributions once per player snapshot; preserve any event or other DLL adjustment as OTHER. (GPT-5.6-Sol) -->
static void getSASGameRecordPlayerExtraSources(CvPlayer const& kPlayer, CvString& szHealthSources, CvString& szHappinessSources)
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
		appendSASGameRecordSignedValue(szHealthSources, kTrait.getType(), kTrait.getHealth());
		appendSASGameRecordSignedValue(szHappinessSources, kTrait.getType(), kTrait.getHappiness());
	}
	FOR_EACH_ENUM(CivicOption)
	{
		CivicTypes const eCivic = kPlayer.getCivics(eLoopCivicOption);
		if (eCivic == NO_CIVIC)
			continue;
		CvCivicInfo const& kCivic = GC.getInfo(eCivic);
		iKnownHealth += kCivic.getExtraHealth();
		iKnownHappiness += kCivic.getExtraHappiness();
		appendSASGameRecordSignedValue(szHealthSources, kCivic.getType(), kCivic.getExtraHealth());
		appendSASGameRecordSignedValue(szHappinessSources, kCivic.getType(), kCivic.getExtraHappiness());
	}
	CvTeam const& kTeam = GET_TEAM(kPlayer.getTeam());
	FOR_EACH_ENUM(Tech)
	{
		if (!kTeam.isHasTech(eLoopTech))
			continue;
		CvTechInfo const& kTech = GC.getInfo(eLoopTech);
		iKnownHealth += kTech.getHealth();
		iKnownHappiness += kTech.getHappiness();
		appendSASGameRecordSignedValue(szHealthSources, kTech.getType(), kTech.getHealth());
		appendSASGameRecordSignedValue(szHappinessSources, kTech.getType(), kTech.getHappiness());
	}
	appendSASGameRecordSignedValue(szHealthSources, "OTHER", kPlayer.getExtraHealth() - iKnownHealth);
	appendSASGameRecordSignedValue(szHappinessSources, "OTHER", kPlayer.getExtraHappiness() - iKnownHappiness);
}

// <!-- custom: Objective victory progress does not show which route currently guides AI strategy. Record the compact 0..4 route stages once per AI snapshot so city production and war choices can be interpreted without enabling detailed BBAI decisions. (GPT-5.6-Sol) -->
static void logSASGameRecordAIVictoryStages(PlayerTypes ePlayer, int iGameTurn)
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
	logSASGameRecord("GAME_RECORD_AI_VICTORY_STAGES turn=%d player=%d team=%d playerMaxStage=%d teamMaxStage=%d culture=%d space=%d conquest=%d domination=%d diplomacy=%d",
			iGameTurn, ePlayer, kPlayer.getTeam(), iPlayerMaxStage, getSASTeamMaxVictoryStage(kPlayer.getTeam()), iCultureStage, iSpaceStage, iConquestStage, iDominationStage, iDiplomacyStage);
}

// <!-- custom: Keep a compact periodic military-production pressure snapshot in the GameRecord so low/high army phases can be diagnosed even without detailed BBAI logging. The no-area maximum is a player-level reference; AI_chooseProduction can use a different city-area ceiling. (ChatGPT-5.6-Sol) -->
static void logSASGameRecordAIMilitaryProduction(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayerAI const& kPlayer = GET_PLAYER(ePlayer);
	if (kPlayer.isHuman() && !kPlayer.isHumanDisabled())
		return;
	CvTeamAI const& kTeam = GET_TEAM(kPlayer.getTeam());
	int const iPersonalityBuildProb = GC.getInfo(kPlayer.getPersonalityType()).getBuildUnitProb();
	int const iUnitSpending = kPlayer.AI_unitCostPerMil();
	int const iMaxUnitSpendingNoArea = kPlayer.AI_maxUnitCostPerMil();
	logSASGameRecord("GAME_RECORD_AI_MILITARY_PRODUCTION turn=%d player=%d personalityBuildProb=%d unitSpending=%d maxUnitSpendingNoArea=%d spendingGapNoArea=%d aggressiveAI=%d financialTrouble=%d economyFocus=%d getBetterUnits=%d focusWar=%d dagger=%d alert1=%d alert2=%d finalWar=%d totalWarPlans=%d preparingTotalWarPlans=%d sneakPreparing=%d sneakReady=%d",
		iGameTurn, ePlayer, iPersonalityBuildProb, iUnitSpending, iMaxUnitSpendingNoArea, iMaxUnitSpendingNoArea - iUnitSpending, GC.getGame().isOption(GAMEOPTION_AGGRESSIVE_AI),
		kPlayer.AI_isFinancialTrouble(), kPlayer.AI_isDoStrategy(AI_STRATEGY_ECONOMY_FOCUS), kPlayer.AI_isDoStrategy(AI_STRATEGY_GET_BETTER_UNITS), kPlayer.AI_isFocusWar(), kPlayer.AI_isDoStrategy(AI_STRATEGY_DAGGER),
		kPlayer.AI_isDoStrategy(AI_STRATEGY_ALERT1), kPlayer.AI_isDoStrategy(AI_STRATEGY_ALERT2), kPlayer.AI_isDoStrategy(AI_STRATEGY_FINAL_WAR), kTeam.AI_getNumWarPlans(WARPLAN_TOTAL), kTeam.AI_getNumWarPlans(WARPLAN_PREPARING_TOTAL),
		kTeam.AI_isSneakAttackPreparing(), kTeam.AI_isSneakAttackReady());
}

static void logSASGameRecordPolicies(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvString szExtraHealthSources;
	CvString szExtraHappinessSources;
	getSASGameRecordPlayerExtraSources(kPlayer, szExtraHealthSources, szExtraHappinessSources);
	logSASGameRecord("GAME_RECORD_POLICIES turn=%d player=%d civics=%s stateReligion=%s cityReligions=%s cityCorporations=%s playerExtraHealth=%d playerExtraHappiness=%d extraHealthSources=%s extraHappinessSources=%s",
			iGameTurn, ePlayer, getSASGameRecordCivicList(kPlayer).GetCString(), getSASGameRecordReligionType(kPlayer.getStateReligion()), getSASGameRecordPlayerCityReligions(kPlayer).GetCString(), getSASGameRecordPlayerCityCorporations(kPlayer).GetCString(),
			kPlayer.getExtraHealth(), kPlayer.getExtraHappiness(), getSASGameRecordOrDash(szExtraHealthSources).GetCString(), getSASGameRecordOrDash(szExtraHappinessSources).GetCString());
}

static void logSASGameRecordEspionage(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayerAI const& kPlayer = GET_PLAYER(ePlayer);
	CvTeam const& kTeam = GET_TEAM(kPlayer.getTeam());
	SASGameRecordPlayerPrevious& kPrevious = g_akSASGameRecordPlayerPrevious[ePlayer];
	CvString szWeights;
	CvString szSpending;
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
		const int iSpending = kTeam.isHasMet(eLoopTeam) ? kPlayer.getEspionageSpending(eLoopTeam) : -1;
		const int iPoints = kTeam.getEspionagePointsAgainstTeam(eLoopTeam);
		const int iModifier = kTeam.getEspionageModifier(eLoopTeam);
		if (iWeight > 0)
		{
			CvString szItem;
			szItem.Format(szWeights.empty() ? "%d:%d" : ",%d:%d", eLoopTeam, iWeight);
			szWeights += szItem;
		}
		if (iSpending > 0)
		{
			CvString szItem;
			szItem.Format(szSpending.empty() ? "%d:%d" : ",%d:%d", eLoopTeam, iSpending);
			szSpending += szItem;
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
	// <!-- custom: Weights show intent but not the rounded EP distribution that the game actually applies. Record actual per-rival spending plus the two high-level espionage strategy flags; detailed reasons for enabling those strategies remain BBAI territory. (ChatGPT-5.6-Sol) -->
	const bool bBigEspionage = kPlayer.AI_isDoStrategy(AI_STRATEGY_BIG_ESPIONAGE);
	const bool bEspionageEconomy = kPlayer.AI_isDoStrategy(AI_STRATEGY_ESPIONAGE_ECONOMY);
	logSASGameRecord("GAME_RECORD_ESPIONAGE turn=%d player=%d team=%d espionageRate=%d espionagePercent=%d teamEP=%d unspentEP=%d weights=%s spending=%s pointsAgainst=%s modifiers=%s bigEspionage=%d espionageEconomy=%d spies=%d greatSpies=%d spiesInForeignTerritory=%d spiesInForeignCities=%d stationarySpies=%d maxFortifyTurns=%d spyTargets=%s",
			iGameTurn, ePlayer, kPlayer.getTeam(), iEspionageRate, iEspionagePercent, iTeamEP, iUnspentEP, getSASGameRecordOrDash(szWeights).GetCString(), getSASGameRecordOrDash(szSpending).GetCString(), getSASGameRecordOrDash(szPoints).GetCString(), getSASGameRecordOrDash(szModifiers).GetCString(), bBigEspionage, bEspionageEconomy, iSpies, iGreatSpies, iSpiesInForeignTerritory, iSpiesInForeignCities, iStationarySpies, iMaxFortifyTurns, getSASGameRecordOrDash(szSpyTargets).GetCString());
	logSASGameRecord("GAME_RECORD_ESPIONAGE_DELTAS turn=%d player=%d deltaValid=%d espionageRateDelta=%+d espionagePercentDelta=%+d teamEPDelta=%+d unspentEPDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameRecordDelta(kPrevious.bValid, iEspionageRate, kPrevious.iEspionageRate), getSASGameRecordDelta(kPrevious.bValid, iEspionagePercent, kPrevious.iEspionagePercent), getSASGameRecordDelta(kPrevious.bValid, iTeamEP, kPrevious.iTeamEP), getSASGameRecordDelta(kPrevious.bValid, iUnspentEP, kPrevious.iUnspentEP));
	kPrevious.iEspionageRate = iEspionageRate;
	kPrevious.iEspionagePercent = iEspionagePercent;
	kPrevious.iTeamEP = iTeamEP;
	kPrevious.iUnspentEP = iUnspentEP;
}

static CvString getSASGameRecordCommercePercents(CvPlayer const& kPlayer)
{
	CvString szList;
	FOR_EACH_ENUM(Commerce)
		appendSASGameRecordValue(szList, getSASGameRecordCommerceType(eLoopCommerce), kPlayer.getCommercePercent(eLoopCommerce));
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordCommerceRates(CvPlayer const& kPlayer)
{
	CvString szList;
	FOR_EACH_ENUM(Commerce)
		appendSASGameRecordValue(szList, getSASGameRecordCommerceType(eLoopCommerce), kPlayer.getCommerceRate(eLoopCommerce));
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordCommerceFlexible(CvPlayer const& kPlayer)
{
	CvString szList;
	FOR_EACH_ENUM(Commerce)
		appendSASGameRecordValue(szList, getSASGameRecordCommerceType(eLoopCommerce), kPlayer.isCommerceFlexible(eLoopCommerce));
	return getSASGameRecordOrDash(szList);
}

static void logSASGameRecordEconomy(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	TechTypes eResearch = kPlayer.getCurrentResearch();
	// <!-- custom: currentResearch=- does not mean that science is lost: CvPlayer::doResearch stores the nominal research rate as overflow until another technology can be selected. Report that rate, accumulated overflow, and whether any technology remains available instead of misleadingly forcing researchRate=0. (GPT-5.6-Sol) -->
	logSASGameRecord("GAME_RECORD_ECONOMY turn=%d player=%d gold=%d goldRate=%d totalCommerce=%d sliders=%s commerceTypeRates=%s flexible=%s currentResearch=%s researchRate=%d researchOverflow=%d noResearchAvailable=%d researchTurns=%d",
			iGameTurn, ePlayer, kPlayer.getGold(), kPlayer.calculateGoldRate(), kPlayer.calculateTotalYield(YIELD_COMMERCE), getSASGameRecordCommercePercents(kPlayer).GetCString(), getSASGameRecordCommerceRates(kPlayer).GetCString(), getSASGameRecordCommerceFlexible(kPlayer).GetCString(), getSASGameRecordTechType(eResearch), kPlayer.calculateResearchRate(eResearch), kPlayer.getOverflowResearch(), kPlayer.isNoResearchAvailable(), eResearch == NO_TECH ? -1 : kPlayer.getResearchTurnsLeft(eResearch, true));
}

static void logSASGameRecordStatistics(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvPlayerRecord const* pRecord = kPlayer.getPlayerRecord();
	const int iCitiesBuilt = (pRecord == NULL ? 0 : pRecord->getNumCitiesBuilt());
	const int iCitiesRazed = (pRecord == NULL ? 0 : pRecord->getNumCitiesRazed());
	// <!-- custom: Built/razed are persistent CyStatistics player-record values used by the Statistics tab. Acquired/lost and battle totals are game-record runtime counters from action rows; keeping them local avoids save-format churn while still making conquest swings visible in benchmark logs. (GPT-5.5) -->
	logSASGameRecord("GAME_RECORD_STATISTICS turn=%d player=%d currentCities=%d persistentCitiesBuilt=%d persistentCitiesRazed=%d loggedCitiesAcquired=%d loggedCitiesLost=%d loggedCitiesConquered=%d loggedCitiesLostByConquest=%d loggedCitiesTradedIn=%d loggedCitiesTradedOut=%d loggedCityNet=%+d loggedBattleWins=%d loggedBattleLosses=%d loggedCityBattleWins=%d loggedCityBattleLosses=%d loggedBattleNet=%+d",
			iGameTurn, ePlayer, kPlayer.getNumCities(), iCitiesBuilt, iCitiesRazed, g_aiSASGameRecordCitiesAcquired[ePlayer], g_aiSASGameRecordCitiesLost[ePlayer], g_aiSASGameRecordCitiesConquered[ePlayer], g_aiSASGameRecordCitiesLostByConquest[ePlayer], g_aiSASGameRecordCitiesTradedIn[ePlayer], g_aiSASGameRecordCitiesTradedOut[ePlayer], g_aiSASGameRecordCitiesAcquired[ePlayer] - g_aiSASGameRecordCitiesLost[ePlayer], g_aiSASGameRecordTotalBattleWins[ePlayer], g_aiSASGameRecordTotalBattleLosses[ePlayer], g_aiSASGameRecordTotalCityBattleWins[ePlayer], g_aiSASGameRecordTotalCityBattleLosses[ePlayer], g_aiSASGameRecordTotalBattleWins[ePlayer] - g_aiSASGameRecordTotalBattleLosses[ePlayer]);
}

static CvString getSASGameRecordEliminatedPlayers()
{
	CvString szList;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes const eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (kLoopPlayer.isEverAlive() && !kLoopPlayer.isAlive() && !kLoopPlayer.isBarbarian())
			appendSASGameRecordIntList(szList, eLoopPlayer);
	}
	return getSASGameRecordOrDash(szList);
}

static PlayerTypes getSASGameRecordTopScorePlayer()
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

static PlayerTypes getSASGameRecordTopPowerPlayer()
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

void logSASGameRecordRunStatus(char const* szReason)
{
	// <!-- custom: CvGame::getNumHumanPlayers is not const in the Civ4 SDK headers, so this local game reference cannot be const. (GPT-5.5) -->
	CvGame& kGame = GC.getGame();
	PlayerTypes const eTopScorePlayer = getSASGameRecordTopScorePlayer();
	PlayerTypes const eTopPowerPlayer = getSASGameRecordTopPowerPlayer();
	// <!-- custom: Compact run-status row gives autoplay/LLM review a single parse-friendly checkpoint for who is alive, eliminated, leading by score, and leading by power. Victory already has its own action row; this row also works for ordinary stopped autoplays where no victory event fires. (GPT-5.5) -->
	logSASGameRecord("GAME_RECORD_RUN_STATUS turn=%d reason=%s elapsed=%d year=%d winnerTeam=%d victory=%s playersAlive=%d teamsAlive=%d playersEverAlive=%d humans=%d eliminatedPlayers=%s topScorePlayer=%d topScore=%d topPowerPlayer=%d topPower=%d totalCities=%d totalPopulation=%d",
			kGame.getGameTurn(), szReason == NULL ? "-" : szReason, kGame.getElapsedGameTurns(), kGame.getGameTurnYear(), kGame.getWinner(), kGame.getVictory() == NO_VICTORY ? "-" : GC.getInfo(kGame.getVictory()).getType(), kGame.countCivPlayersAlive(), kGame.countCivTeamsAlive(), kGame.countCivPlayersEverAlive(), kGame.getNumHumanPlayers(), getSASGameRecordEliminatedPlayers().GetCString(), eTopScorePlayer, eTopScorePlayer == NO_PLAYER ? 0 : GET_PLAYER(eTopScorePlayer).calculateScore(), eTopPowerPlayer, eTopPowerPlayer == NO_PLAYER ? 0 : GET_PLAYER(eTopPowerPlayer).getPower(), kGame.getNumCities(), kGame.getTotalPopulation());
}

static void logSASGameRecordDemographics(PlayerTypes ePlayer, int iGameTurn)
{
	CvGame const& kGame = GC.getGame();
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	SASGameRecordPlayerPrevious& kPrevious = g_akSASGameRecordPlayerPrevious[ePlayer];
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
	logSASGameRecord("GAME_RECORD_DEMOGRAPHICS turn=%d player=%d rank=%d score=%d population=%d land=%d food=%d production=%d commerce=%d research=%d culture=%d espionage=%d goldRate=%d power=%d",
			iGameTurn, ePlayer, kGame.getPlayerRank(ePlayer) + 1, iScore, iPopulation, iLand, iFood, iProduction, iCommerce, iResearch, iCulture, iEspionage, iGoldRate, iPower);
	logSASGameRecord("GAME_RECORD_DEMOGRAPHICS_DELTAS turn=%d player=%d deltaValid=%d scoreDelta=%+d populationDelta=%+d landDelta=%+d foodDelta=%+d productionDelta=%+d commerceDelta=%+d researchDelta=%+d cultureDelta=%+d espionageDelta=%+d goldRateDelta=%+d powerDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameRecordDelta(kPrevious.bValid, iScore, kPrevious.iDemoScore), getSASGameRecordDelta(kPrevious.bValid, iPopulation, kPrevious.iDemoPopulation), getSASGameRecordDelta(kPrevious.bValid, iLand, kPrevious.iDemoLand), getSASGameRecordDelta(kPrevious.bValid, iFood, kPrevious.iDemoFood), getSASGameRecordDelta(kPrevious.bValid, iProduction, kPrevious.iDemoProduction), getSASGameRecordDelta(kPrevious.bValid, iCommerce, kPrevious.iDemoCommerce), getSASGameRecordDelta(kPrevious.bValid, iResearch, kPrevious.iDemoResearch), getSASGameRecordDelta(kPrevious.bValid, iCulture, kPrevious.iDemoCulture), getSASGameRecordDelta(kPrevious.bValid, iEspionage, kPrevious.iDemoEspionage), getSASGameRecordDelta(kPrevious.bValid, iGoldRate, kPrevious.iDemoGoldRate), getSASGameRecordDelta(kPrevious.bValid, iPower, kPrevious.iDemoPower));
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

static void logSASGameRecordAttitudes(PlayerTypes ePlayer, int iGameTurn)
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
	logSASGameRecord("GAME_RECORD_ATTITUDES turn=%d player=%d towardValues=%s", iGameTurn, ePlayer, getSASGameRecordOrDash(szToward).GetCString());
}

static void logSASGameRecordDiplomaticMemories(PlayerTypes ePlayer, int iGameTurn)
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
			logSASGameRecord("GAME_RECORD_DIPLO_MEMORIES turn=%d player=%d toward=%d attitudeValue=%+d memoryAttitude=%+d memories=%s", iGameTurn, ePlayer, eTowardPlayer, kPlayer.AI_getAttitudeVal(eTowardPlayer), iMemoryAttitude, szMemories.GetCString());
		}
	}
}

static void logSASGameRecordDiploStatus(PlayerTypes ePlayer, int iGameTurn)
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
			appendSASGameRecordIntList(szAtWar, eLoopTeam);
		if (kTeam.isOpenBorders(eLoopTeam))
			appendSASGameRecordIntList(szOpenBorders, eLoopTeam);
		if (kTeam.isDefensivePact(eLoopTeam))
			appendSASGameRecordIntList(szDefensivePacts, eLoopTeam);
		if (kTeam.isForcePeace(eLoopTeam))
			appendSASGameRecordIntList(szForcePeace, eLoopTeam);
		if (GET_TEAM(eLoopTeam).AI().AI_getWorstEnemy() == kPlayer.getTeam())
			appendSASGameRecordIntList(szWorstEnemyOfTeams, eLoopTeam);
	}
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		if (eLoopPlayer == ePlayer || !GET_PLAYER(eLoopPlayer).isAlive() || GET_PLAYER(eLoopPlayer).isBarbarian())
			continue;
		if (!kTeam.isHasMet(GET_PLAYER(eLoopPlayer).getTeam()))
			continue;
		if (GET_PLAYER(eLoopPlayer).getTeam() == eWorstEnemy)
			appendSASGameRecordIntList(szWorstEnemyPlayers, eLoopPlayer);
		if (kPlayer.canContact(eLoopPlayer, false))
			appendSASGameRecordIntList(szCanContact, eLoopPlayer);
		if (kPlayer.canContact(eLoopPlayer, true))
			appendSASGameRecordIntList(szCanContactWilling, eLoopPlayer);
		if (!kPlayer.AI_isWillingToTalk(eLoopPlayer))
			appendSASGameRecordIntList(szWontTalkTo, eLoopPlayer);
		if (!GET_PLAYER(eLoopPlayer).AI_isWillingToTalk(ePlayer))
			appendSASGameRecordIntList(szWontTalkFrom, eLoopPlayer);
	}
	logSASGameRecord("GAME_RECORD_DIPLO_STATUS turn=%d player=%d team=%d worstEnemyTeam=%d worstEnemyPlayers=%s worstEnemyOfTeams=%s atWar=%s openBorders=%s defensivePacts=%s forcePeace=%s canContact=%s canContactWilling=%s wontTalkTo=%s wontTalkFrom=%s",
			iGameTurn, ePlayer, kPlayer.getTeam(), eWorstEnemy, getSASGameRecordOrDash(szWorstEnemyPlayers).GetCString(), getSASGameRecordOrDash(szWorstEnemyOfTeams).GetCString(), getSASGameRecordOrDash(szAtWar).GetCString(), getSASGameRecordOrDash(szOpenBorders).GetCString(), getSASGameRecordOrDash(szDefensivePacts).GetCString(), getSASGameRecordOrDash(szForcePeace).GetCString(), getSASGameRecordOrDash(szCanContact).GetCString(), getSASGameRecordOrDash(szCanContactWilling).GetCString(), getSASGameRecordOrDash(szWontTalkTo).GetCString(), getSASGameRecordOrDash(szWontTalkFrom).GetCString());
}

static void logSASGameRecordEnvironment(int iGameTurn)
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
		appendSASGameRecordTypeCount(szFeatures, getSASGameRecordFeatureType(eLoopFeature), aiFeatures[eLoopFeature]);
		appendSASGameRecordTypeCount(szNegativeHealthFeatures, getSASGameRecordFeatureType(eLoopFeature), aiNegativeHealthFeatures[eLoopFeature]);
	}
	const int iGlobalWarmingIndex = GC.getGame().getGlobalWarmingIndex();
	const int iGlobalWarmingChances = GC.getGame().getGlobalWarmingChances();
	logSASGameRecord("GAME_RECORD_ENVIRONMENT turn=%d globalWarmingIndex=%d globalWarmingChances=%d land=%d water=%d ownedLand=%d unownedLand=%d negativeHealthFeatures=%s features=%s",
			iGameTurn, iGlobalWarmingIndex, iGlobalWarmingChances, kMap.getLandPlots(), kMap.getWaterPlots(), iOwnedLand, iUnownedLand, getSASGameRecordOrDash(szNegativeHealthFeatures).GetCString(), getSASGameRecordOrDash(szFeatures).GetCString());
	logSASGameRecord("GAME_RECORD_ENVIRONMENT_DELTAS turn=%d deltaValid=%d globalWarmingIndexDelta=%+d globalWarmingChancesDelta=%+d ownedLandDelta=%+d unownedLandDelta=%+d",
			iGameTurn, g_kSASGameRecordGlobalPrevious.bValid, getSASGameRecordDelta(g_kSASGameRecordGlobalPrevious.bValid, iGlobalWarmingIndex, g_kSASGameRecordGlobalPrevious.iGlobalWarmingIndex), getSASGameRecordDelta(g_kSASGameRecordGlobalPrevious.bValid, iGlobalWarmingChances, g_kSASGameRecordGlobalPrevious.iGlobalWarmingChances), getSASGameRecordDelta(g_kSASGameRecordGlobalPrevious.bValid, iOwnedLand, g_kSASGameRecordGlobalPrevious.iOwnedLand), getSASGameRecordDelta(g_kSASGameRecordGlobalPrevious.bValid, iUnownedLand, g_kSASGameRecordGlobalPrevious.iUnownedLand));
	g_kSASGameRecordGlobalPrevious.bValid = true;
	g_kSASGameRecordGlobalPrevious.iGlobalWarmingIndex = iGlobalWarmingIndex;
	g_kSASGameRecordGlobalPrevious.iGlobalWarmingChances = iGlobalWarmingChances;
	g_kSASGameRecordGlobalPrevious.iOwnedLand = iOwnedLand;
	g_kSASGameRecordGlobalPrevious.iUnownedLand = iUnownedLand;
}

static void logSASGameRecordVoteSources(int iGameTurn)
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
				appendSASGameRecordIntList(szVotingTeams, eLoopTeam);
			if (kLoopTeam.isFullMember(eLoopVoteSource))
				appendSASGameRecordIntList(szFullTeams, eLoopTeam);
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
			szItem.Format(szVictoryVotes.empty() ? "%s:required=%d,possible=%d" : ",%s:required=%d,possible=%d", getSASGameRecordVoteType(eLoopVote), kGame.getVoteRequired(eLoopVote, eLoopVoteSource), kGame.countPossibleVote(eLoopVote, eLoopVoteSource));
			szVictoryVotes += szItem;
		}
		if (pSourceCity == NULL && eReligion == NO_RELIGION && eSecretary == NO_TEAM && szVotingTeams.empty() && szVictoryVotes.empty())
			continue;
		logSASGameRecord("GAME_RECORD_DIPLO_VOTE_SOURCE turn=%d source=%s secretaryTeam=%d secretaryTimer=%d voteTimer=%d religion=%s sourceOwner=%d sourceCityId=%d sourceCity=%S sourceX=%d sourceY=%d votingTeams=%s fullTeams=%s votes=%s victoryVotes=%s",
				iGameTurn, getSASGameRecordVoteSourceType(eLoopVoteSource), eSecretary, kGame.getSecretaryGeneralTimer(eLoopVoteSource), kGame.getVoteTimer(eLoopVoteSource), getSASGameRecordReligionType(eReligion), pSourceCity == NULL ? -1 : pSourceCity->getOwner(), pSourceCity == NULL ? -1 : pSourceCity->getID(), getSASGameRecordQuotedCityName(pSourceCity).GetCString(), pSourceCity == NULL ? -1 : pSourceCity->getX(), pSourceCity == NULL ? -1 : pSourceCity->getY(), getSASGameRecordOrDash(szVotingTeams).GetCString(), getSASGameRecordOrDash(szFullTeams).GetCString(), getSASGameRecordOrDash(szVotes).GetCString(), getSASGameRecordOrDash(szVictoryVotes).GetCString());
	}
}

static void logSASGameRecordTeamProjects(TeamTypes eTeam, int iGameTurn)
{
	CvString szProjects;
	FOR_EACH_ENUM(Project)
		appendSASGameRecordTypeCount(szProjects, getSASGameRecordProjectType(eLoopProject), GET_TEAM(eTeam).getProjectCount(eLoopProject));
	if (!szProjects.empty())
		logSASGameRecord("GAME_RECORD_TEAM_PROJECTS turn=%d team=%d projects=%s", iGameTurn, eTeam, szProjects.GetCString());
}

static void logSASGameRecordPlayerBonuses(PlayerTypes ePlayer, int iGameTurn, SASGameRecordPlayerPrevious const& kPrevious)
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
			appendSASGameRecordTypeCount(szAvailable, getSASGameRecordBonusType(eLoopBonus), iAvailable);
		}
		appendSASGameRecordTypeCount(szTradeable, getSASGameRecordBonusType(eLoopBonus), iTradeable);
		if (iImport > 0)
		{
			iBonusImports += iImport;
			appendSASGameRecordTypeCount(szImports, getSASGameRecordBonusType(eLoopBonus), iImport);
		}
		if (iExport > 0)
		{
			iBonusExports += iExport;
			appendSASGameRecordTypeCount(szExports, getSASGameRecordBonusType(eLoopBonus), iExport);
		}
	}
	logSASGameRecord("GAME_RECORD_BONUSES turn=%d player=%d deltaValid=%d bonusTypes=%d bonusTypesDelta=%+d bonusInstances=%d bonusInstancesDelta=%+d imports=%d importsDelta=%+d exports=%d exportsDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, iBonusTypes, getSASGameRecordDelta(kPrevious.bValid, iBonusTypes, kPrevious.iBonusTypes), iBonusInstances, getSASGameRecordDelta(kPrevious.bValid, iBonusInstances, kPrevious.iBonusInstances), iBonusImports, getSASGameRecordDelta(kPrevious.bValid, iBonusImports, kPrevious.iBonusImports), iBonusExports, getSASGameRecordDelta(kPrevious.bValid, iBonusExports, kPrevious.iBonusExports));
	logSASGameRecord("GAME_RECORD_BONUSES_AVAILABLE turn=%d player=%d available=%s", iGameTurn, ePlayer, getSASGameRecordOrDash(szAvailable).GetCString());
	logSASGameRecord("GAME_RECORD_BONUSES_TRADEABLE turn=%d player=%d tradeable=%s", iGameTurn, ePlayer, getSASGameRecordOrDash(szTradeable).GetCString());
	logSASGameRecord("GAME_RECORD_BONUSES_IMPORT_EXPORT turn=%d player=%d imported=%s exported=%s", iGameTurn, ePlayer, getSASGameRecordOrDash(szImports).GetCString(), getSASGameRecordOrDash(szExports).GetCString());
}

static bool isSASGameRecordMilitaryUnit(CvUnit const& kUnit)
{
	return kUnit.canDefend(kUnit.plot()) || kUnit.baseCombatStr() > 0 || kUnit.airBaseCombatStr() > 0;
}

static bool isSASGameRecordWorkerUnit(CvUnit const& kUnit)
{
	UnitAITypes eUnitAI = kUnit.AI_getUnitAIType();
	return eUnitAI == UNITAI_WORKER || eUnitAI == UNITAI_WORKER_SEA || kUnit.workRate(true) > 0;
}

static bool isSASGameRecordSettlerUnit(CvUnit const& kUnit)
{
	return kUnit.AI_getUnitAIType() == UNITAI_SETTLE || kUnit.isFound();
}

static MissionTypes getSASGameRecordUnitMissionType(CvUnit const& kUnit)
{
	CvSelectionGroup const* pGroup = kUnit.getGroup();
	return pGroup == NULL ? NO_MISSION : pGroup->getMissionType(0);
}

static int getSASGameRecordBuildTurnsLeft(CvUnit const& kUnit, BuildTypes eBuild)
{
	return eBuild == NO_BUILD ? -1 : kUnit.getPlot().getBuildTurnsLeft(eBuild, kUnit.getOwner(), 0, 0);
}

static bool isSASGameRecordUnitGuarded(CvUnit const& kUnit)
{
	CvPlot const* pPlot = kUnit.plot();
	return pPlot != NULL && pPlot->getNumDefenders(kUnit.getOwner()) > 0;
}

static bool isSASGameRecordUnitThreatened(CvUnit const& kUnit)
{
	CvPlot const* pPlot = kUnit.plot();
	return pPlot != NULL && pPlot->isVisibleEnemyUnit(kUnit.getOwner());
}

static void logSASGameRecordUnitPosture(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	TeamTypes eTeam = kPlayer.getTeam();
	SASGameRecordPlayerPrevious& kPrevious = g_akSASGameRecordPlayerPrevious[ePlayer];
	int iTotal = 0;
	int iMilitary = 0;
	int iLandMilitary = 0;
	int iSeaMilitary = 0;
	int iAirMilitary = 0;
	int iAttackAir = 0;
	int iDefenseAir = 0;
	int iCarrierAir = 0;
	int iMissileAir = 0;
	int iICBM = 0;
	int iCarrierSea = 0;
	int iMissileCarrierSea = 0;
	int iAirCargo = 0;
	int iCarrierAirCargo = 0;
	int iMissileCargo = 0;
	int iNukes = 0;
	int iUnitCombatTotal = 0;
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
	std::vector<int> aiPromotions(gGameRecordLogLevel >= 3 ? GC.getNumPromotionInfos() : 0, 0);
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
		const bool bMilitary = isSASGameRecordMilitaryUnit(*pLoopUnit);
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
		{
			aiUnitAI[eUnitAI]++;
			if (eUnitAI == UNITAI_ATTACK_AIR) iAttackAir++;
			else if (eUnitAI == UNITAI_DEFENSE_AIR) iDefenseAir++;
			else if (eUnitAI == UNITAI_CARRIER_AIR) iCarrierAir++;
			else if (eUnitAI == UNITAI_MISSILE_AIR) iMissileAir++;
			else if (eUnitAI == UNITAI_ICBM) iICBM++;
			else if (eUnitAI == UNITAI_CARRIER_SEA) iCarrierSea++;
			else if (eUnitAI == UNITAI_MISSILE_CARRIER_SEA) iMissileCarrierSea++;
		}
		if (pLoopUnit->getDomainType() == DOMAIN_AIR && pLoopUnit->isCargo())
		{
			iAirCargo++;
			if (eUnitAI == UNITAI_CARRIER_AIR) iCarrierAirCargo++;
			else if (eUnitAI == UNITAI_MISSILE_AIR) iMissileCargo++;
		}
		if (pLoopUnit->isNuke()) iNukes++;
		UnitCombatTypes eUnitCombat = pLoopUnit->getUnitCombatType();
		if (eUnitCombat != NO_UNITCOMBAT)
		{
			aiUnitCombat[eUnitCombat]++;
			iUnitCombatTotal++;
		}
		if (gGameRecordLogLevel >= 3)
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
		if (isSASGameRecordWorkerUnit(*pLoopUnit))
			iWorkers++;
		if (isSASGameRecordSettlerUnit(*pLoopUnit))
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
	CvString szUnitCombatPercentX100;
	CvString szPromotions;
	// <!-- custom: UnitAI and combat class are useful but too coarse for game-record review: a Galley and Galleon can share naval transport roles, and a Camel Archer and Dragoon can sit in similar mounted/combat buckets despite very different strength and era impact. Include actual unit-type counts so LLM/autoplay review can see army and navy quality without per-unit spam. (GPT-5.5) -->
	for (int iI = 0; iI < GC.getNumUnitInfos(); iI++)
		appendSASGameRecordTypeCount(szUnitTypes, getSASGameRecordUnitType((UnitTypes)iI), aiUnitTypes[iI]);
	for (int iI = 0; iI < NUM_UNITAI_TYPES; iI++)
		appendSASGameRecordTypeCount(szUnitAI, getSASGameRecordUnitAIType((UnitAITypes)iI), aiUnitAI[iI]);
	for (int iI = 0; iI < GC.getNumUnitCombatInfos(); iI++)
	{
		appendSASGameRecordTypeCount(szUnitCombat, getSASGameRecordUnitCombatType((UnitCombatTypes)iI), aiUnitCombat[iI]);
		if (aiUnitCombat[iI] > 0)
			appendSASGameRecordValue(szUnitCombatPercentX100, getSASGameRecordUnitCombatType((UnitCombatTypes)iI), getSASGameRecordPercentX100(aiUnitCombat[iI], iUnitCombatTotal));
	}
	if (gGameRecordLogLevel >= 3)
	{
		FOR_EACH_ENUM(Promotion)
			appendSASGameRecordTypeCount(szPromotions, getSASGameRecordPromotionType(eLoopPromotion), aiPromotions[eLoopPromotion]);
	}
	// <!-- custom: Keep late-game air/missile/nuclear posture on the existing unit row rather than adding repetitive snapshot rows; UnitAI-specific counts make carrier filling and missile/nuke inventories directly visible. (GPT-5.6) -->
	logSASGameRecord("GAME_RECORD_UNIT_POSTURE turn=%d player=%d total=%d military=%d landMilitary=%d seaMilitary=%d airMilitary=%d attackAir=%d defenseAir=%d carrierAir=%d missileAir=%d icbm=%d carrierSea=%d missileCarrierSea=%d airCargo=%d carrierAirCargo=%d missileCargo=%d nukes=%d workers=%d settlers=%d recon=%d cityDefenders=%d fieldArmy=%d ownTerritory=%d enemyTerritory=%d neutralTerritory=%d unitsInCities=%d enemyUnitsInTerritory=%d totalXP=%d avgXpX100=%d maxXP=%d promotionReady=%d level2Plus=%d level4Plus=%d level6Plus=%d promotionInstances=%d",
			iGameTurn, ePlayer, iTotal, iMilitary, iLandMilitary, iSeaMilitary, iAirMilitary, iAttackAir, iDefenseAir, iCarrierAir, iMissileAir, iICBM, iCarrierSea, iMissileCarrierSea, iAirCargo, iCarrierAirCargo, iMissileCargo, iNukes, iWorkers, iSettlers, iRecon, iCityDefenders, iFieldArmy, iOwnTerritory, iEnemyTerritory, iNeutralTerritory, iUnitsInCities, iEnemyUnitsInTerritory, iTotalExperience, iTotal == 0 ? 0 : (100 * iTotalExperience) / iTotal, iMaxExperience, iPromotionReady, iLevel2Plus, iLevel4Plus, iLevel6Plus, iPromotionInstances);
	logSASGameRecord("GAME_RECORD_UNIT_POSTURE_DELTAS turn=%d player=%d deltaValid=%d totalDelta=%+d militaryDelta=%+d workersDelta=%+d settlersDelta=%+d fieldArmyDelta=%+d cityDefendersDelta=%+d enemyUnitsInTerritoryDelta=%+d totalXPDelta=%+d promotionReadyDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameRecordDelta(kPrevious.bValid, iTotal, kPrevious.iUnitTotal), getSASGameRecordDelta(kPrevious.bValid, iMilitary, kPrevious.iUnitMilitary), getSASGameRecordDelta(kPrevious.bValid, iWorkers, kPrevious.iUnitWorkers), getSASGameRecordDelta(kPrevious.bValid, iSettlers, kPrevious.iUnitSettlers), getSASGameRecordDelta(kPrevious.bValid, iFieldArmy, kPrevious.iUnitFieldArmy), getSASGameRecordDelta(kPrevious.bValid, iCityDefenders, kPrevious.iUnitCityDefenders), getSASGameRecordDelta(kPrevious.bValid, iEnemyUnitsInTerritory, kPrevious.iUnitEnemyUnitsInTerritory), getSASGameRecordDelta(kPrevious.bValid, iTotalExperience, kPrevious.iUnitTotalExperience), getSASGameRecordDelta(kPrevious.bValid, iPromotionReady, kPrevious.iUnitPromotionReady));
	kPrevious.iUnitTotal = iTotal;
	kPrevious.iUnitMilitary = iMilitary;
	kPrevious.iUnitWorkers = iWorkers;
	kPrevious.iUnitSettlers = iSettlers;
	kPrevious.iUnitFieldArmy = iFieldArmy;
	kPrevious.iUnitCityDefenders = iCityDefenders;
	kPrevious.iUnitEnemyUnitsInTerritory = iEnemyUnitsInTerritory;
	kPrevious.iUnitTotalExperience = iTotalExperience;
	kPrevious.iUnitPromotionReady = iPromotionReady;
	// <!-- custom: Record UnitCombat shares alongside the raw counts already collected so army mix (e.g. siege-heavy vs. siege-light) is immediately comparable without LLM/manual summing. PercentX100 uses only units with a real UnitCombat as the denominator, excluding Workers, Great People and other non-combat-class units. (GPT-5.6) -->
	logSASGameRecord("GAME_RECORD_UNIT_COMPOSITION turn=%d player=%d unitTypes=%s unitAI=%s unitCombatTotal=%d unitCombat=%s unitCombatPercentX100=%s", iGameTurn, ePlayer, getSASGameRecordOrDash(szUnitTypes).GetCString(), getSASGameRecordOrDash(szUnitAI).GetCString(), iUnitCombatTotal, getSASGameRecordOrDash(szUnitCombat).GetCString(), getSASGameRecordOrDash(szUnitCombatPercentX100).GetCString());
	if (gGameRecordLogLevel >= 3) logSASGameRecord("GAME_RECORD_UNIT_PROMOTIONS turn=%d player=%d promotions=%s", iGameTurn, ePlayer, getSASGameRecordOrDash(szPromotions).GetCString());
}

static void logSASGameRecordWorkers(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	TeamTypes eTeam = kPlayer.getTeam();
	SASGameRecordPlayerPrevious& kPrevious = g_akSASGameRecordPlayerPrevious[ePlayer];
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
		if (!isSASGameRecordWorkerUnit(*pLoopUnit))
			continue;
		iWorkers++;
		if (pLoopUnit->AI_getUnitAIType() == UNITAI_WORKER_SEA || pLoopUnit->getDomainType() == DOMAIN_SEA)
			iSeaWorkers++;
		CvPlot const* pPlot = pLoopUnit->plot();
		MissionTypes eMission = getSASGameRecordUnitMissionType(*pLoopUnit);
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
		if (isSASGameRecordUnitGuarded(*pLoopUnit))
			iGuarded++;
		else iUnguarded++;
		if (isSASGameRecordUnitThreatened(*pLoopUnit))
			iThreatened++;
		if (gGameRecordLogLevel >= 3 && pPlot != NULL)
		{
			logSASGameRecord("GAME_RECORD_WORKER turn=%d player=%d unitId=%d unit=%s unitAI=%s x=%d y=%d mission=%s build=%s buildTurnsLeft=%d plotOwner=%d plotTerrain=%s plotFeature=%s plotBonus=%s plotImprovement=%s plotRoute=%s guarded=%d threatened=%d",
					iGameTurn, ePlayer, pLoopUnit->getID(), getSASGameRecordUnitType(pLoopUnit->getUnitType()), getSASGameRecordUnitAIType(pLoopUnit->AI_getUnitAIType()), pLoopUnit->getX(), pLoopUnit->getY(), getSASGameRecordMissionType(eMission), getSASGameRecordBuildType(eBuild), getSASGameRecordBuildTurnsLeft(*pLoopUnit, eBuild), pPlot->getOwner(), getSASGameRecordTerrainType(pPlot->getTerrainType()), getSASGameRecordFeatureType(pPlot->getFeatureType()), getSASGameRecordBonusType(pPlot->getBonusType(pLoopUnit->getTeam())), getSASGameRecordImprovementType(pPlot->getImprovementType()), getSASGameRecordRouteType(pPlot->getRouteType()), isSASGameRecordUnitGuarded(*pLoopUnit), isSASGameRecordUnitThreatened(*pLoopUnit));
		}
	}
	CvString szBuilds;
	for (int iI = 0; iI < GC.getNumBuildInfos(); iI++)
		appendSASGameRecordTypeCount(szBuilds, getSASGameRecordBuildType((BuildTypes)iI), aiBuilds[iI]);
	logSASGameRecord("GAME_RECORD_WORKERS turn=%d player=%d workers=%d seaWorkers=%d idle=%d building=%d buildingImprovement=%d buildingRoute=%d moving=%d waiting=%d ownTerritory=%d enemyTerritory=%d neutralTerritory=%d guarded=%d unguarded=%d threatened=%d builds=%s",
			iGameTurn, ePlayer, iWorkers, iSeaWorkers, iIdle, iBuilding, iBuildingImprovement, iBuildingRoute, iMoving, iWaiting, iOwnTerritory, iEnemyTerritory, iNeutralTerritory, iGuarded, iUnguarded, iThreatened, getSASGameRecordOrDash(szBuilds).GetCString());
	logSASGameRecord("GAME_RECORD_WORKERS_DELTAS turn=%d player=%d deltaValid=%d workersDelta=%+d buildingDelta=%+d idleDelta=%+d movingDelta=%+d waitingDelta=%+d threatenedDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameRecordDelta(kPrevious.bValid, iWorkers, kPrevious.iWorkerWorkers), getSASGameRecordDelta(kPrevious.bValid, iBuilding, kPrevious.iWorkerBuilding), getSASGameRecordDelta(kPrevious.bValid, iIdle, kPrevious.iWorkerIdle), getSASGameRecordDelta(kPrevious.bValid, iMoving, kPrevious.iWorkerMoving), getSASGameRecordDelta(kPrevious.bValid, iWaiting, kPrevious.iWorkerWaiting), getSASGameRecordDelta(kPrevious.bValid, iThreatened, kPrevious.iWorkerThreatened));
	kPrevious.iWorkerWorkers = iWorkers;
	kPrevious.iWorkerBuilding = iBuilding;
	kPrevious.iWorkerIdle = iIdle;
	kPrevious.iWorkerMoving = iMoving;
	kPrevious.iWorkerWaiting = iWaiting;
	kPrevious.iWorkerThreatened = iThreatened;
}

static void logSASGameRecordExpansion(PlayerTypes ePlayer, int iGameTurn)
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
	SASGameRecordTerritoryDevelopment kTerritoryDevelopment;
	CvMap const& kMap = GC.getMap();
	for (int iI = 0; iI < kMap.numPlots(); iI++)
	{
		CvPlot const& kPlot = kMap.getPlotByIndex(iI);
		if (kPlot.getOwner() == ePlayer)
			addSASGameRecordTerritoryDevelopment(kTerritoryDevelopment, kPlot, ePlayer, eTeam, eFarm);
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
		if (!isSASGameRecordSettlerUnit(*pLoopUnit))
			continue;
		iSettlers++;
		if (getSASGameRecordUnitMissionType(*pLoopUnit) == MISSION_FOUND)
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
	logSASGameRecord("GAME_RECORD_EXPANSION turn=%d player=%d cities=%d targetCities=%d ownedLand=%d revealedLand=%d visibleLand=%d revealedUnownedLand=%d visibleUnownedLand=%d revealedForeignLand=%d visibleForeignLand=%d settlers=%d foundMission=%d citiesProducingSettlers=%d nearestSettlerCityDistance=%d avgSettlerCityDistanceX100=%d",
			iGameTurn, ePlayer, kPlayer.getNumCities(), GC.getInfo(kMap.getWorldSize()).getTargetNumCities(), kPlayer.getTotalLand(), iRevealedLand, iVisibleLand, iRevealedUnownedLand, iVisibleUnownedLand, iRevealedForeignLand, iVisibleForeignLand, iSettlers, iFoundMission, iCitiesProducingSettlers, iNearestSettlerCityDistance, iAvgSettlerCityDistanceX100);
	logSASGameRecordTerritoryDevelopment(ePlayer, iGameTurn, kTerritoryDevelopment);
}

static void logSASGameRecordSettlers(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	TeamTypes eTeam = kPlayer.getTeam();
	SASGameRecordPlayerPrevious& kPrevious = g_akSASGameRecordPlayerPrevious[ePlayer];
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
		if (!isSASGameRecordSettlerUnit(*pLoopUnit))
			continue;
		iSettlers++;
		CvPlot const* pPlot = pLoopUnit->plot();
		MissionTypes eMission = getSASGameRecordUnitMissionType(*pLoopUnit);
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
		if (isSASGameRecordUnitGuarded(*pLoopUnit))
			iGuarded++;
		else iUnguarded++;
		if (isSASGameRecordUnitThreatened(*pLoopUnit))
			iThreatened++;
		if (gGameRecordLogLevel >= 3 && pPlot != NULL)
		{
			CvCity const* pNearestCity = GC.getMap().findCity(pLoopUnit->getX(), pLoopUnit->getY(), ePlayer, NO_TEAM, false);
			const int iNearestDistance = pNearestCity == NULL ? -1 : plotDistance(pLoopUnit->getX(), pLoopUnit->getY(), pNearestCity->getX(), pNearestCity->getY());
			logSASGameRecord("GAME_RECORD_SETTLER turn=%d player=%d unitId=%d unit=%s unitAI=%s x=%d y=%d mission=%s plotOwner=%d plotTerrain=%s plotFeature=%s plotBonus=%s plotImprovement=%s plotRoute=%s guarded=%d threatened=%d nearestCityId=%d nearestCity=%S nearestCityDistance=%d",
					iGameTurn, ePlayer, pLoopUnit->getID(), getSASGameRecordUnitType(pLoopUnit->getUnitType()), getSASGameRecordUnitAIType(pLoopUnit->AI_getUnitAIType()), pLoopUnit->getX(), pLoopUnit->getY(), getSASGameRecordMissionType(eMission), pPlot->getOwner(), getSASGameRecordTerrainType(pPlot->getTerrainType()), getSASGameRecordFeatureType(pPlot->getFeatureType()), getSASGameRecordBonusType(pPlot->getBonusType(pLoopUnit->getTeam())), getSASGameRecordImprovementType(pPlot->getImprovementType()), getSASGameRecordRouteType(pPlot->getRouteType()), isSASGameRecordUnitGuarded(*pLoopUnit), isSASGameRecordUnitThreatened(*pLoopUnit), pNearestCity == NULL ? -1 : pNearestCity->getID(), getSASGameRecordQuotedCityName(pNearestCity).GetCString(), iNearestDistance);
		}
	}
	logSASGameRecord("GAME_RECORD_SETTLERS turn=%d player=%d settlers=%d foundMission=%d moving=%d idle=%d waiting=%d ownTerritory=%d enemyTerritory=%d neutralTerritory=%d guarded=%d unguarded=%d threatened=%d",
			iGameTurn, ePlayer, iSettlers, iFoundMission, iMoving, iIdle, iWaiting, iOwnTerritory, iEnemyTerritory, iNeutralTerritory, iGuarded, iUnguarded, iThreatened);
	logSASGameRecord("GAME_RECORD_SETTLERS_DELTAS turn=%d player=%d deltaValid=%d settlersDelta=%+d foundMissionDelta=%+d movingDelta=%+d idleDelta=%+d waitingDelta=%+d threatenedDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameRecordDelta(kPrevious.bValid, iSettlers, kPrevious.iSettlerSettlers), getSASGameRecordDelta(kPrevious.bValid, iFoundMission, kPrevious.iSettlerFoundMission), getSASGameRecordDelta(kPrevious.bValid, iMoving, kPrevious.iSettlerMoving), getSASGameRecordDelta(kPrevious.bValid, iIdle, kPrevious.iSettlerIdle), getSASGameRecordDelta(kPrevious.bValid, iWaiting, kPrevious.iSettlerWaiting), getSASGameRecordDelta(kPrevious.bValid, iThreatened, kPrevious.iSettlerThreatened));
	kPrevious.iSettlerSettlers = iSettlers;
	kPrevious.iSettlerFoundMission = iFoundMission;
	kPrevious.iSettlerMoving = iMoving;
	kPrevious.iSettlerIdle = iIdle;
	kPrevious.iSettlerWaiting = iWaiting;
	kPrevious.iSettlerThreatened = iThreatened;
}

static CvString getSASGameRecordCitySpecialists(CvCity const& kCity, bool bFree)
{
	CvString szList;
	FOR_EACH_ENUM(Specialist)
	{
		const int iCount = (bFree ? kCity.getFreeSpecialistCount(eLoopSpecialist) : kCity.getSpecialistCount(eLoopSpecialist));
		appendSASGameRecordTypeCount(szList, getSASGameRecordSpecialistType(eLoopSpecialist), iCount);
	}
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordCityGPOdds(CvCity const& kCity)
{
	CvString szList;
	std::vector<std::pair<UnitTypes,int> > aeiProjection;
	kCity.GPProjection(aeiProjection);
	for (size_t iI = 0; iI < aeiProjection.size(); iI++)
		appendSASGameRecordTypeCount(szList, getSASGameRecordUnitType(aeiProjection[iI].first), aeiProjection[iI].second);
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordCityHappySources(CvCity const& kCity)
{
	CvString szList;
	CvPlayer const& kOwner = GET_PLAYER(kCity.getOwner());
	appendSASGameRecordPositiveValue(szList, "largestCity", std::max(0, kCity.getLargestCityHappiness()));
	appendSASGameRecordPositiveValue(szList, "military", std::max(0, kCity.getMilitaryHappiness()));
	appendSASGameRecordPositiveValue(szList, "stateReligion", std::max(0, kCity.getCurrentStateReligionHappiness()));
	appendSASGameRecordPositiveValue(szList, "building", std::max(0, kCity.getBuildingGoodHappiness()));
	appendSASGameRecordPositiveValue(szList, "extraBuilding", std::max(0, kCity.getExtraBuildingGoodHappiness()));
	appendSASGameRecordPositiveValue(szList, "surrounding", std::max(0, kCity.getSurroundingGoodHappiness()));
	appendSASGameRecordPositiveValue(szList, "bonus", std::max(0, kCity.getBonusGoodHappiness()));
	appendSASGameRecordPositiveValue(szList, "religion", std::max(0, kCity.getReligionGoodHappiness()));
	appendSASGameRecordPositiveValue(szList, "commerce", std::max(0, kCity.getCommerceHappiness()));
	appendSASGameRecordPositiveValue(szList, "areaBuilding", std::max(0, kCity.getArea().getBuildingHappiness(kCity.getOwner())));
	appendSASGameRecordPositiveValue(szList, "playerBuilding", std::max(0, kOwner.getBuildingHappiness()));
	appendSASGameRecordPositiveValue(szList, "extra", std::max(0, kCity.getExtraHappiness() + kOwner.getExtraHappiness()));
	appendSASGameRecordPositiveValue(szList, "handicap", std::max(0, GC.getInfo(kCity.getHandicapType()).getHappyBonus()));
	appendSASGameRecordPositiveValue(szList, "vassal", std::max(0, kCity.getVassalHappiness()));
	appendSASGameRecordPositiveValue(szList, "temporary", kCity.getHappinessTimer() > 0 ? GC.getDefineINT("TEMP_HAPPY") : 0);
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordCityFlatUnhappySources(CvCity const& kCity)
{
	CvString szList;
	CvPlayer const& kOwner = GET_PLAYER(kCity.getOwner());
	appendSASGameRecordPositiveValue(szList, "largestCity", -std::min(0, kCity.getLargestCityHappiness()));
	appendSASGameRecordPositiveValue(szList, "military", -std::min(0, kCity.getMilitaryHappiness()));
	appendSASGameRecordPositiveValue(szList, "stateReligion", -std::min(0, kCity.getCurrentStateReligionHappiness()));
	appendSASGameRecordPositiveValue(szList, "building", -std::min(0, kCity.getBuildingBadHappiness()));
	appendSASGameRecordPositiveValue(szList, "extraBuilding", -std::min(0, kCity.getExtraBuildingBadHappiness()));
	appendSASGameRecordPositiveValue(szList, "surrounding", -std::min(0, kCity.getSurroundingBadHappiness()));
	appendSASGameRecordPositiveValue(szList, "bonus", -std::min(0, kCity.getBonusBadHappiness()));
	appendSASGameRecordPositiveValue(szList, "religion", -std::min(0, kCity.getReligionBadHappiness()));
	appendSASGameRecordPositiveValue(szList, "commerce", -std::min(0, kCity.getCommerceHappiness()));
	appendSASGameRecordPositiveValue(szList, "areaBuilding", -std::min(0, kCity.getArea().getBuildingHappiness(kCity.getOwner())));
	appendSASGameRecordPositiveValue(szList, "playerBuilding", -std::min(0, kOwner.getBuildingHappiness()));
	appendSASGameRecordPositiveValue(szList, "extra", -std::min(0, kCity.getExtraHappiness() + kOwner.getExtraHappiness()));
	appendSASGameRecordPositiveValue(szList, "handicap", -std::min(0, GC.getInfo(kCity.getHandicapType()).getHappyBonus()));
	appendSASGameRecordPositiveValue(szList, "vassal", std::max(0, kCity.getVassalUnhappiness()));
	appendSASGameRecordPositiveValue(szList, "espionage", std::max(0, kCity.getEspionageHappinessCounter()));
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordCityAngerPercentSources(CvCity const& kCity)
{
	CvString szList;
	CvPlayer const& kOwner = GET_PLAYER(kCity.getOwner());
	int iCivicAnger = 0;
	FOR_EACH_ENUM(Civic)
		iCivicAnger += kOwner.getCivicPercentAnger(eLoopCivic);
	appendSASGameRecordPositiveValue(szList, "overcrowding", kCity.getOvercrowdingPercentAnger());
	appendSASGameRecordPositiveValue(szList, "noMilitary", kCity.getNoMilitaryPercentAnger());
	appendSASGameRecordPositiveValue(szList, "culture", kCity.getCulturePercentAnger());
	appendSASGameRecordPositiveValue(szList, "religion", kCity.getReligionPercentAnger());
	appendSASGameRecordPositiveValue(szList, "hurry", kCity.getHurryPercentAnger());
	appendSASGameRecordPositiveValue(szList, "conscript", kCity.getConscriptPercentAnger());
	appendSASGameRecordPositiveValue(szList, "defyResolution", kCity.getDefyResolutionPercentAnger());
	appendSASGameRecordPositiveValue(szList, "warWeariness", kCity.getWarWearinessPercentAnger());
	appendSASGameRecordPositiveValue(szList, "globalWarming", std::max(0, kOwner.getGwPercentAnger() * 10));
	appendSASGameRecordPositiveValue(szList, "civics", iCivicAnger);
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordCityHealthySources(CvCity const& kCity)
{
	CvString szList;
	CvPlayer const& kOwner = GET_PLAYER(kCity.getOwner());
	appendSASGameRecordPositiveValue(szList, "freshWater", std::max(0, kCity.getFreshWaterGoodHealth()));
	appendSASGameRecordPositiveValue(szList, "surrounding", std::max(0, kCity.getSurroundingGoodHealth()));
	appendSASGameRecordPositiveValue(szList, "power", std::max(0, kCity.getPowerGoodHealth()));
	appendSASGameRecordPositiveValue(szList, "bonus", std::max(0, kCity.getBonusGoodHealth()));
	appendSASGameRecordPositiveValue(szList, "building", std::max(0, kCity.totalGoodBuildingHealth()));
	appendSASGameRecordPositiveValue(szList, "extra", std::max(0, kCity.getExtraHealth() + kOwner.getExtraHealth()));
	appendSASGameRecordPositiveValue(szList, "handicap", std::max(0, GC.getInfo(kCity.getHandicapType()).getHealthBonus()));
	return getSASGameRecordOrDash(szList);
}

static CvString getSASGameRecordCityUnhealthySources(CvCity const& kCity)
{
	CvString szList;
	CvPlayer const& kOwner = GET_PLAYER(kCity.getOwner());
	appendSASGameRecordPositiveValue(szList, "population", kCity.unhealthyPopulation());
	appendSASGameRecordPositiveValue(szList, "espionage", std::max(0, kCity.getEspionageHealthCounter()));
	appendSASGameRecordPositiveValue(szList, "freshWater", -std::min(0, kCity.getFreshWaterBadHealth()));
	appendSASGameRecordPositiveValue(szList, "surrounding", -std::min(0, kCity.getSurroundingBadHealth()));
	appendSASGameRecordPositiveValue(szList, "power", -std::min(0, kCity.getPowerBadHealth()));
	appendSASGameRecordPositiveValue(szList, "bonus", -std::min(0, kCity.getBonusBadHealth()));
	appendSASGameRecordPositiveValue(szList, "building", -std::min(0, kCity.totalBadBuildingHealth()));
	appendSASGameRecordPositiveValue(szList, "extra", -std::min(0, kCity.getExtraHealth() + kOwner.getExtraHealth()));
	appendSASGameRecordPositiveValue(szList, "handicap", -std::min(0, GC.getInfo(kCity.getHandicapType()).getHealthBonus()));
	return getSASGameRecordOrDash(szList);
}

static const char* getSASGameRecordCityProductionKind(CvCity const& kCity)
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

static const char* getSASGameRecordCityProductionType(CvCity const& kCity)
{
	if (kCity.getProductionUnit() != NO_UNIT)
		return getSASGameRecordUnitType(kCity.getProductionUnit());
	if (kCity.getProductionBuilding() != NO_BUILDING)
		return getSASGameRecordBuildingType(kCity.getProductionBuilding());
	if (kCity.getProductionProject() != NO_PROJECT)
		return getSASGameRecordProjectType(kCity.getProductionProject());
	if (kCity.getProductionProcess() != NO_PROCESS)
		return getSASGameRecordProcessType(kCity.getProductionProcess());
	return "-";
}

// <!-- custom: Building-completion actions alone cannot reconstruct buildings inherited through conquest, granted for free, or already present when a log begins. At detail level, snapshot the exact owned buildings and compact regular/national/team/world-wonder totals for each city. (GPT-5.6-Sol) -->
static CvString getSASGameRecordCityBuildings(CvCity const& kCity, int& iTotal, int& iRegular, int& iNationalWonders, int& iTeamWonders, int& iWorldWonders)
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
		szItem.Format(szBuildings.empty() ? "%s:%d" : ",%s:%d", getSASGameRecordBuildingType(eBuilding), iCount);
		szBuildings += szItem;
	}
	return getSASGameRecordOrDash(szBuildings);
}

// <!-- custom: A PROCESS production name identifies Wealth/Research/Culture but not its actual gain. Record the exact production-to-commerce contribution in hundredths, matching CvCity::updateCommerce without rounding away fractional output. (GPT-5.6-Sol) -->
static CvString getSASGameRecordCityProductionConversion(CvCity const& kCity)
{
	CvString szConversion;
	if (kCity.getProductionProcess() == NO_PROCESS)
		return "-";
	for (int iI = 0; iI < NUM_COMMERCE_TYPES; iI++)
	{
		CommerceTypes const eCommerce = (CommerceTypes)iI;
		int const iRateX100 = kCity.getYieldRate(YIELD_PRODUCTION) * kCity.getProductionToCommerceModifier(eCommerce);
		if (iRateX100 > 0)
			appendSASGameRecordValue(szConversion, getSASGameRecordCommerceType(eCommerce), iRateX100);
	}
	return getSASGameRecordOrDash(szConversion);
}

static CvString getSASGameRecordCityTradePartners(CvCity const& kCity)
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
	return szList.empty() ? "-" : getSASGameRecordQuoted(szList.GetCString());
}

// <!-- custom: Settler unit-state helpers for event-based expansion diagnostics. Keep game-record rows descriptive: raw unit counts, visible enemy counts and combat/founding context, while BBAI logs carry the heavier AI-decision reasons. No gameplay behavior change. (ChatGPT-5.5) -->
struct SASGameRecordPlotUnitCounts
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
	SASGameRecordPlotUnitCounts() : iUnits(0), iMilitaryUnits(0), iCivilianUnits(0), iDefenders(0), iHealthyDefenders(0), iWoundedDefenders(0), iSettlers(0), iWorkers(0), iAttackers(0), pBestDefender(NULL), pFirstSettler(NULL) {}
};

static void collectSASGameRecordPlotUnitCounts(CvPlot const& kPlot, PlayerTypes ePlayer, SASGameRecordPlotUnitCounts& kCounts)
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
		if (isSASGameRecordSettlerUnit(*pLoopUnit))
		{
			kCounts.iSettlers++;
			if (kCounts.pFirstSettler == NULL)
				kCounts.pFirstSettler = pLoopUnit;
		}
		if (isSASGameRecordWorkerUnit(*pLoopUnit))
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


static void logSASGameRecordWorkedPlots(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	SASGameRecordPlotComposition kComposition;
	int iLoop = 0;
	for (CvCity const* pLoopCity = kPlayer.firstCity(&iLoop); pLoopCity != NULL; pLoopCity = kPlayer.nextCity(&iLoop))
		addSASGameRecordPlotComposition(kComposition, getSASGameRecordWorkedPlotComposition(*pLoopCity));
	CvString szTerrains;
	CvString szFeatures;
	CvString szBonuses;
	CvString szImprovements;
	CvString szRoutes;
	getSASGameRecordPlotCompositionTypes(kComposition, szTerrains, szFeatures, szBonuses, szImprovements, szRoutes);
	logSASGameRecord("GAME_RECORD_WORKED_PLOTS turn=%d player=%d cities=%d worked=%d improved=%d unimproved=%d land=%d water=%d hills=%d riverSide=%d freshWater=%d bonusImproved=%d bonusUnimproved=%d currentFood=%d currentProd=%d currentCommerce=%d natureFood=%d natureProd=%d natureCommerce=%d terrains=%s features=%s bonuses=%s improvements=%s routes=%s",
			iGameTurn, ePlayer, kPlayer.getNumCities(), kComposition.iWorked, kComposition.iWorkedImproved, kComposition.iWorkedUnimproved, kComposition.iLand, kComposition.iWater, kComposition.iHills, kComposition.iRiverSide, kComposition.iFreshWater, kComposition.iBonusImproved, kComposition.iBonusUnimproved, kComposition.iCurrentFood, kComposition.iCurrentProduction, kComposition.iCurrentCommerce, kComposition.iNatureFood, kComposition.iNatureProduction, kComposition.iNatureCommerce, getSASGameRecordOrDash(szTerrains).GetCString(), getSASGameRecordOrDash(szFeatures).GetCString(), getSASGameRecordOrDash(szBonuses).GetCString(), getSASGameRecordOrDash(szImprovements).GetCString(), getSASGameRecordOrDash(szRoutes).GetCString());
}

static void logSASGameRecordCityDetail(CvCity const& kCity, int iGameTurn)
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
	const SASGameRecordPlotComposition kWorkedPlots = getSASGameRecordWorkedPlotComposition(kCity);
	SASGameRecordPlotUnitCounts kCityUnits;
	collectSASGameRecordPlotUnitCounts(kCity.getPlot(), kCity.getOwner(), kCityUnits);
	// <!-- custom: City-level espionage output and modifiers make Jail/Intelligence Agency-style effects measurable without adding another row; the defense modifier is kept separate from the city's espionage-commerce modifier. (ChatGPT-5.6-Sol) -->
	// <!-- custom: Air-unit occupancy/capacity on the existing city row makes poor basing or saturated airbases visible without adding a separate late-game row. Cargo aircraft are intentionally excluded by CvPlot::countNumAirUnits, matching actual base-capacity use. (GPT-5.6) -->
	// <!-- custom: City defense snapshots expose both the current post-bombard defense modifier and its undamaged ceiling. DefenseDamage/MAX_CITY_DEFENSE_DAMAGE preserves the underlying bombardment state, while bombarded shows whether the city has already been hit this turn. This lets broad game records be paired with the level-3 tactical bombardment actions below. (GPT-5.6) -->
	logSASGameRecord("GAME_RECORD_CITY turn=%d player=%d cityId=%d city=%S x=%d y=%d pop=%d foodSurplus=%d happySurplus=%d healthSurplus=%d food=%d prod=%d commerce=%d espionageRate=%d espionageRateModifier=%d espionageDefenseModifier=%d defenseModifier=%d totalDefense=%d defenseDamage=%d defenseDamageMax=%d bombarded=%d airUnits=%d airCapacity=%d airSpaceAvailable=%d worked=%d workedImproved=%d workedUnimproved=%d workedFood=%d workedProd=%d workedCommerce=%d garrison=%d cityUnits=%d militaryUnits=%d civilianUnits=%d defenders=%d healthyDefenders=%d woundedDefenders=%d settlers=%d workers=%d attackers=%d connectedToCapital=%d plotGroupId=%d tradeRoutes=%d domesticTradeRoutes=%d foreignTradeRoutes=%d tradeFood=%d tradeProd=%d tradeCommerce=%d productionKind=%s production=%s productionTurns=%d productionStored=%d productionNeeded=%d overflowProduction=%d featureProduction=%d productionConversionX100=%s specialists=%s freeSpecialists=%s gpProgress=%d gpThreshold=%d gpRate=%d gpTurnsLeft=%d gpOdds=%s",
			iGameTurn, kCity.getOwner(), kCity.getID(), getSASGameRecordQuotedCityName(&kCity).GetCString(), kCity.getX(), kCity.getY(), kCity.getPopulation(), kCity.foodDifference(), kCity.happyLevel() - kCity.unhappyLevel(), kCity.goodHealth() - kCity.badHealth(), kCity.getYieldRate(YIELD_FOOD), kCity.getYieldRate(YIELD_PRODUCTION), kCity.getYieldRate(YIELD_COMMERCE), kCity.getCommerceRate(COMMERCE_ESPIONAGE), kCity.getTotalCommerceRateModifier(COMMERCE_ESPIONAGE), kCity.getEspionageDefenseModifier(), kCity.getDefenseModifier(false), kCity.getTotalDefense(false), kCity.getDefenseDamage(), GC.getMAX_CITY_DEFENSE_DAMAGE(), kCity.isBombarded(), kCity.getPlot().countNumAirUnits(kCity.getTeam()), kCity.getAirUnitCapacity(kCity.getTeam()), kCity.getPlot().airUnitSpaceAvailable(kCity.getTeam()),
			kWorkedPlots.iWorked, kWorkedPlots.iWorkedImproved, kWorkedPlots.iWorkedUnimproved, kWorkedPlots.iCurrentFood, kWorkedPlots.iCurrentProduction, kWorkedPlots.iCurrentCommerce, kCity.plot()->getNumDefenders(kCity.getOwner()), kCityUnits.iUnits, kCityUnits.iMilitaryUnits, kCityUnits.iCivilianUnits, kCityUnits.iDefenders, kCityUnits.iHealthyDefenders, kCityUnits.iWoundedDefenders, kCityUnits.iSettlers, kCityUnits.iWorkers, kCityUnits.iAttackers,
			kCity.isConnectedToCapital(), pPlotGroup == NULL ? -1 : pPlotGroup->getID(), kCity.getTradeRoutes(), iDomesticTradeRoutes, iForeignTradeRoutes, kCity.getTradeYield(YIELD_FOOD), kCity.getTradeYield(YIELD_PRODUCTION), kCity.getTradeYield(YIELD_COMMERCE),
			getSASGameRecordCityProductionKind(kCity), getSASGameRecordCityProductionType(kCity), kCity.getProductionTurnsLeft(), kCity.getProduction(), kCity.getProductionNeeded(), kCity.getOverflowProduction(), kCity.getFeatureProduction(), getSASGameRecordCityProductionConversion(kCity).GetCString(), getSASGameRecordCitySpecialists(kCity, false).GetCString(), getSASGameRecordCitySpecialists(kCity, true).GetCString(),
			kCity.getGreatPeopleProgress(), kOwner.greatPeopleThreshold(false), kCity.getGreatPeopleRate(), kCity.GPTurnsLeft(), getSASGameRecordCityGPOdds(kCity).GetCString());
	logSASGameRecord("GAME_RECORD_CITY_HAPPINESS turn=%d player=%d cityId=%d happy=%d unhappy=%d surplus=%d happySources=%s flatUnhappySources=%s angerPercentSources=%s",
			iGameTurn, kCity.getOwner(), kCity.getID(), kCity.happyLevel(), kCity.unhappyLevel(), kCity.happyLevel() - kCity.unhappyLevel(),
			getSASGameRecordCityHappySources(kCity).GetCString(), getSASGameRecordCityFlatUnhappySources(kCity).GetCString(), getSASGameRecordCityAngerPercentSources(kCity).GetCString());
	logSASGameRecord("GAME_RECORD_CITY_HEALTH turn=%d player=%d cityId=%d goodHealth=%d badHealth=%d surplus=%d powered=%d dirtyPower=%d areaCleanPower=%d powerGoodHealth=%d powerBadHealth=%d healthySources=%s unhealthySources=%s",
			iGameTurn, kCity.getOwner(), kCity.getID(), kCity.goodHealth(), kCity.badHealth(), kCity.goodHealth() - kCity.badHealth(),
			kCity.isPower(), kCity.isDirtyPower(), kCity.isAreaCleanPower(), kCity.getPowerGoodHealth(), kCity.getPowerBadHealth(), getSASGameRecordCityHealthySources(kCity).GetCString(), getSASGameRecordCityUnhealthySources(kCity).GetCString());
	int iBuildings, iRegularBuildings, iNationalWonders, iTeamWonders, iWorldWonders;
	CvString const szBuildings = getSASGameRecordCityBuildings(kCity, iBuildings, iRegularBuildings, iNationalWonders, iTeamWonders, iWorldWonders);
	logSASGameRecord("GAME_RECORD_CITY_BUILDINGS turn=%d player=%d cityId=%d total=%d regular=%d nationalWonders=%d teamWonders=%d worldWonders=%d buildings=%s", iGameTurn, kCity.getOwner(), kCity.getID(), iBuildings, iRegularBuildings, iNationalWonders, iTeamWonders, iWorldWonders, szBuildings.GetCString());
	if (gGameRecordLogLevel >= 3) logSASGameRecord("GAME_RECORD_CITY_TRADE_PARTNERS turn=%d player=%d cityId=%d partners=%s", iGameTurn, kCity.getOwner(), kCity.getID(), getSASGameRecordCityTradePartners(kCity).GetCString());
	// <!-- custom: Large city garrisons in autoplay logs did not reveal whether an army was one parked attack stack or many defensive/miscellaneous groups. At game-record level 3, record compact group and UnitAI composition for cities with at least six military units; BBAI UNIT logging remains responsible for the groups' decision reasons. (GPT-5.6-Sol) -->
	if (gGameRecordLogLevel >= 3 && kCityUnits.iMilitaryUnits >= 6)
	{
		std::vector<int> aiUnitTypes(GC.getNumUnitInfos(), 0);
		std::vector<int> aiUnitAI(NUM_UNITAI_TYPES, 0);
		std::vector<int> aiGroupIds;
		CvSelectionGroup const* pLargestGroup = NULL;
		for (CLLNode<IDInfo> const* pUnitNode = kCity.getPlot().headUnitNode(); pUnitNode != NULL; pUnitNode = kCity.getPlot().nextUnitNode(pUnitNode))
		{
			CvUnit const* pLoopUnit = ::getUnit(pUnitNode->m_data);
			if (pLoopUnit == NULL || pLoopUnit->getOwner() != kCity.getOwner() || !isSASGameRecordMilitaryUnit(*pLoopUnit))
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
			appendSASGameRecordTypeCount(szUnitTypes, getSASGameRecordUnitType((UnitTypes)iI), aiUnitTypes[iI]);
		for (int iI = 0; iI < NUM_UNITAI_TYPES; iI++)
			appendSASGameRecordTypeCount(szUnitAI, getSASGameRecordUnitAIType((UnitAITypes)iI), aiUnitAI[iI]);
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
		logSASGameRecord("GAME_RECORD_CITY_UNIT_COMPOSITION turn=%d player=%d cityId=%d city=%S militaryUnits=%d groups=%d largestGroupId=%d largestGroupUnits=%d largestGroupHeadAI=%s largestGroupActivity=%d largestGroupMission=%s largestGroupMissionAI=%d largestGroupMissionPlot=(%d,%d) largestGroupMissionUnitOwner=%d largestGroupMissionUnitId=%d largestGroupMissionQueue=%d largestGroupWounded=%d largestGroupIncomingJoiners=%d unitTypes=%s unitAI=%s",
				iGameTurn, kCity.getOwner(), kCity.getID(), getSASGameRecordQuotedCityName(&kCity).GetCString(), kCityUnits.iMilitaryUnits, (int)aiGroupIds.size(), (pLargestGroup == NULL ? -1 : pLargestGroup->getID()), (pLargestGroup == NULL ? 0 : pLargestGroup->getNumUnits()), (pLargestGroupHead == NULL ? "-" : getSASGameRecordUnitAIType(pLargestGroupHead->AI_getUnitAIType())),
				(pLargestGroup == NULL ? NO_ACTIVITY : pLargestGroup->getActivityType()), (pLargestGroup == NULL ? "-" : getSASGameRecordMissionType(pLargestGroup->getMissionType(0))), (pLargestGroupAI == NULL ? NO_MISSIONAI : pLargestGroupAI->AI_getMissionAIType()),
				(pLargestGroupMissionPlot == NULL ? -1 : pLargestGroupMissionPlot->getX()), (pLargestGroupMissionPlot == NULL ? -1 : pLargestGroupMissionPlot->getY()), (pLargestGroupMissionUnit == NULL ? -1 : pLargestGroupMissionUnit->getOwner()), (pLargestGroupMissionUnit == NULL ? -1 : pLargestGroupMissionUnit->getID()), (pLargestGroup == NULL ? 0 : pLargestGroup->getLengthMissionQueue()),
				iLargestGroupWounded, iLargestGroupIncomingJoiners, getSASGameRecordOrDash(szUnitTypes).GetCString(), getSASGameRecordOrDash(szUnitAI).GetCString());
	}
}

static void logSASGameRecordCities(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	SASGameRecordPlayerPrevious& kPrevious = g_akSASGameRecordPlayerPrevious[ePlayer];
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
		SASGameRecordPlotUnitCounts kCityUnits;
		collectSASGameRecordPlotUnitCounts(pLoopCity->getPlot(), ePlayer, kCityUnits);
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
		if (gGameRecordLogLevel >= 3) logSASGameRecordCityDetail(*pLoopCity, iGameTurn);
	}
	logSASGameRecord("GAME_RECORD_CITIES turn=%d player=%d cities=%d capitalId=%d capital=%S connectedToCapital=%d totalFoodSurplus=%d totalHappySurplus=%d totalHealthSurplus=%d totalFood=%d totalProd=%d totalCommerce=%d tradeRoutes=%d domesticTradeRoutes=%d foreignTradeRoutes=%d tradeFood=%d tradeProd=%d tradeCommerce=%d unhappyCities=%d unhealthyCities=%d starvingCities=%d specialists=%d freeSpecialists=%d garrison=%d cityUnits=%d militaryUnits=%d civilianUnits=%d defenders=%d settlers=%d workers=%d nextGPCityId=%d nextGPCity=%S nextGPTurns=%d nextGPRate=%d nextGPProgress=%d citiesProducingUnits=%d citiesProducingMilitary=%d citiesProducingWorkers=%d citiesProducingSettlers=%d citiesProducingBuildings=%d citiesProducingWonders=%d citiesProducingProjects=%d citiesProducingProcesses=%d",
			iGameTurn, ePlayer, iCities, pCapital == NULL ? -1 : pCapital->getID(), getSASGameRecordQuotedCityName(pCapital).GetCString(), iConnectedToCapital, iTotalFoodSurplus, iTotalHappySurplus, iTotalHealthSurplus, iTotalFoodYield, iTotalProductionYield, iTotalCommerceYield, iTotalTradeRoutes, iDomesticTradeRoutes, iForeignTradeRoutes, iTradeFood, iTradeProduction, iTradeCommerce, iUnhappyCities, iUnhealthyCities, iStarvingCities, iSpecialists, iFreeSpecialists, iGarrison, iCityUnits, iMilitaryUnitsInCities, iCivilianUnitsInCities, iDefendersInCities, iSettlersInCities, iWorkersInCities, pNextGPCity == NULL ? -1 : pNextGPCity->getID(), getSASGameRecordQuotedCityName(pNextGPCity).GetCString(), pNextGPCity == NULL ? -1 : iBestGPTurns, pNextGPCity == NULL ? 0 : pNextGPCity->getGreatPeopleRate(), pNextGPCity == NULL ? 0 : pNextGPCity->getGreatPeopleProgress(), iCitiesProducingUnits, iCitiesProducingMilitary, iCitiesProducingWorkers, iCitiesProducingSettlers, iCitiesProducingBuildings, iCitiesProducingWonders, iCitiesProducingProjects, iCitiesProducingProcesses);
	logSASGameRecord("GAME_RECORD_CITIES_DELTAS turn=%d player=%d deltaValid=%d citiesDelta=%+d connectedToCapitalDelta=%+d totalFoodSurplusDelta=%+d totalHappySurplusDelta=%+d totalHealthSurplusDelta=%+d totalFoodDelta=%+d totalProdDelta=%+d totalCommerceDelta=%+d tradeRoutesDelta=%+d tradeCommerceDelta=%+d specialistsDelta=%+d freeSpecialistsDelta=%+d garrisonDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameRecordDelta(kPrevious.bValid, iCities, kPrevious.iCityCount), getSASGameRecordDelta(kPrevious.bValid, iConnectedToCapital, kPrevious.iCityConnectedToCapital), getSASGameRecordDelta(kPrevious.bValid, iTotalFoodSurplus, kPrevious.iCityFoodSurplus), getSASGameRecordDelta(kPrevious.bValid, iTotalHappySurplus, kPrevious.iCityHappySurplus), getSASGameRecordDelta(kPrevious.bValid, iTotalHealthSurplus, kPrevious.iCityHealthSurplus), getSASGameRecordDelta(kPrevious.bValid, iTotalFoodYield, kPrevious.iCityFood), getSASGameRecordDelta(kPrevious.bValid, iTotalProductionYield, kPrevious.iCityProduction), getSASGameRecordDelta(kPrevious.bValid, iTotalCommerceYield, kPrevious.iCityCommerce), getSASGameRecordDelta(kPrevious.bValid, iTotalTradeRoutes, kPrevious.iCityTradeRoutes), getSASGameRecordDelta(kPrevious.bValid, iTradeCommerce, kPrevious.iCityTradeCommerce), getSASGameRecordDelta(kPrevious.bValid, iSpecialists, kPrevious.iCitySpecialists), getSASGameRecordDelta(kPrevious.bValid, iFreeSpecialists, kPrevious.iCityFreeSpecialists), getSASGameRecordDelta(kPrevious.bValid, iGarrison, kPrevious.iCityGarrison));
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

static void logSASGameRecordPlayerSnapshot(PlayerTypes ePlayer, int iGameTurn)
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
	const int iMilitarySupportUnits = kPlayer.getNumMilitaryUnits();
	// <!-- custom: CvPlayer::getNumMilitaryUnits counts XML bMilitarySupport, which can fall sharply when an army upgrades into combat units that intentionally do not pay military support. Count actual combat-capable units with the same predicate used by GAME_RECORD_UNIT_POSTURE, and keep the raw Civ4 counter separately. This scan runs only when a GameRecord player snapshot is already being generated. (ChatGPT-5.6-Sol) -->
	int iCombatUnits = 0;
	int iCombatLoop = 0;
	for (CvUnit const* pLoopUnit = kPlayer.firstUnit(&iCombatLoop); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iCombatLoop))
	{
		if (isSASGameRecordMilitaryUnit(*pLoopUnit)) ++iCombatUnits;
	}
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
	SASGameRecordPlayerPrevious& kPrevious = g_akSASGameRecordPlayerPrevious[ePlayer];
	const char* szCiv = (kPlayer.getCivilizationType() == NO_CIVILIZATION ? "-" : GC.getInfo(kPlayer.getCivilizationType()).getType());
	const char* szLeader = (kPlayer.getLeaderType() == NO_LEADER ? "-" : GC.getInfo(kPlayer.getLeaderType()).getType());
	const char* szEra = (kPlayer.getCurrentEra() == NO_ERA ? "-" : GC.getInfo(kPlayer.getCurrentEra()).getType());
	const bool bCurrentlyHumanControlled = kPlayer.isHuman();
	const bool bAutoplayControlled = kPlayer.isHumanDisabled();
	const bool bHumanSlot = (bCurrentlyHumanControlled || bAutoplayControlled);
	logSASGameRecord("GAME_RECORD_PLAYER turn=%d player=%d team=%d civ=%s leader=%s isHuman=%d humanSlot=%d currentlyHumanControlled=%d autoplayControlled=%d rank=%d deltaValid=%d score=%d scoreDelta=%+d cities=%d citiesDelta=%+d pop=%d popDelta=%+d land=%d landDelta=%+d units=%d unitsDelta=%+d combatUnits=%d combatUnitsDelta=%+d militarySupportUnits=%d militarySupportUnitsDelta=%+d power=%d powerDelta=%+d gold=%d goldDelta=%+d gpt=%d gptDelta=%+d researchRate=%d researchRateDelta=%+d researchPercent=%d currentResearch=%s researchOverflow=%d noResearchAvailable=%d researchTurns=%d era=%s stateReligion=%s techScorePercent=%d combatXP=%d greatPeopleCreated=%d greatGeneralsCreated=%d greatGeneralThreshold=%d goldenAgeTurns=%d totalGoldenAgeTurns=%d anarchyTurns=%d totalAnarchyTurns=%d revolutionTimer=%d conversionTimer=%d wars=%s",
			iGameTurn, ePlayer, kPlayer.getTeam(), szCiv, szLeader, bCurrentlyHumanControlled, bHumanSlot, bCurrentlyHumanControlled, bAutoplayControlled, kGame.getPlayerRank(ePlayer) + 1, kPrevious.bValid,
			iScore, getSASGameRecordDelta(kPrevious.bValid, iScore, kPrevious.iScore), iCities, getSASGameRecordDelta(kPrevious.bValid, iCities, kPrevious.iCities),
			iPopulation, getSASGameRecordDelta(kPrevious.bValid, iPopulation, kPrevious.iPopulation), iLand, getSASGameRecordDelta(kPrevious.bValid, iLand, kPrevious.iLand),
			iUnits, getSASGameRecordDelta(kPrevious.bValid, iUnits, kPrevious.iUnits), iCombatUnits, getSASGameRecordDelta(kPrevious.bValid, iCombatUnits, kPrevious.iCombatUnits),
			iMilitarySupportUnits, getSASGameRecordDelta(kPrevious.bValid, iMilitarySupportUnits, kPrevious.iMilitarySupportUnits), iPower, getSASGameRecordDelta(kPrevious.bValid, iPower, kPrevious.iPower), iGold, getSASGameRecordDelta(kPrevious.bValid, iGold, kPrevious.iGold), iGoldRate, getSASGameRecordDelta(kPrevious.bValid, iGoldRate, kPrevious.iGoldRate),
			iResearchRate, getSASGameRecordDelta(kPrevious.bValid, iResearchRate, kPrevious.iResearchRate), kPlayer.getCommercePercent(COMMERCE_RESEARCH), getSASGameRecordTechType(eResearch), kPlayer.getOverflowResearch(), kPlayer.isNoResearchAvailable(), iResearchTurns,
			szEra, getSASGameRecordReligionType(kPlayer.getStateReligion()), kTeam.getBestKnownTechScorePercent(), kPlayer.getCombatExperience(), kPlayer.getGreatPeopleCreated(), kPlayer.getGreatGeneralsCreated(), kPlayer.greatPeopleThreshold(true),
			kPlayer.getGoldenAgeTurns(), g_aiSASGameRecordTotalGoldenAgeTurns[ePlayer], kPlayer.getAnarchyTurns(), g_aiSASGameRecordTotalAnarchyTurns[ePlayer], kPlayer.getRevolutionTimer(), kPlayer.getConversionTimer(), getSASGameRecordWarTeams(kPlayer.getTeam()).GetCString());
	logSASGameRecord("GAME_RECORD_PLAYER_HISTORY turn=%d player=%d deltaValid=%d historyScore=%d historyScoreDelta=%+d historyEconomy=%d historyEconomyDelta=%+d historyIndustry=%d historyIndustryDelta=%+d historyAgriculture=%d historyAgricultureDelta=%+d historyPower=%d historyPowerDelta=%+d historyCulture=%d historyCultureDelta=%+d historyEspionage=%d historyEspionageDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, iHistoryScore, getSASGameRecordDelta(kPrevious.bValid, iHistoryScore, kPrevious.iHistoryScore), iHistoryEconomy, getSASGameRecordDelta(kPrevious.bValid, iHistoryEconomy, kPrevious.iHistoryEconomy), iHistoryIndustry, getSASGameRecordDelta(kPrevious.bValid, iHistoryIndustry, kPrevious.iHistoryIndustry), iHistoryAgriculture, getSASGameRecordDelta(kPrevious.bValid, iHistoryAgriculture, kPrevious.iHistoryAgriculture), iHistoryPower, getSASGameRecordDelta(kPrevious.bValid, iHistoryPower, kPrevious.iHistoryPower), iHistoryCulture, getSASGameRecordDelta(kPrevious.bValid, iHistoryCulture, kPrevious.iHistoryCulture), iHistoryEspionage, getSASGameRecordDelta(kPrevious.bValid, iHistoryEspionage, kPrevious.iHistoryEspionage));
	// <!-- custom: The environment row shows world pollution, but not which player produced it or whether buildings, bonuses, dirty power, or population caused it. Keep these city scans behind record level 2, and derive the total from the four components rather than scanning a fifth time. (GPT-5.6-Sol) -->
	if (gGameRecordLogLevel >= 2)
	{
		int const iBuildingPollution = kPlayer.calculatePollution(CvPlayer::POLLUTION_BUILDINGS);
		int const iBonusPollution = kPlayer.calculatePollution(CvPlayer::POLLUTION_BONUSES);
		int const iPowerPollution = kPlayer.calculatePollution(CvPlayer::POLLUTION_POWER);
		int const iPopulationPollution = kPlayer.calculatePollution(CvPlayer::POLLUTION_POPULATION);
		logSASGameRecord("GAME_RECORD_POLLUTION turn=%d player=%d total=%d buildings=%d bonuses=%d power=%d population=%d", iGameTurn, ePlayer, iBuildingPollution + iBonusPollution + iPowerPollution + iPopulationPollution, iBuildingPollution, iBonusPollution, iPowerPollution, iPopulationPollution);
	}
	if (gGameRecordLogLevel >= 2)
	{
		logSASGameRecordPlayerBonuses(ePlayer, iGameTurn, kPrevious);
		logSASGameRecordAIVictoryStages(ePlayer, iGameTurn);
		logSASGameRecordAIMilitaryProduction(ePlayer, iGameTurn);
		logSASGameRecordPolicies(ePlayer, iGameTurn);
		logSASGameRecordEconomy(ePlayer, iGameTurn);
		logSASGameRecordStatistics(ePlayer, iGameTurn);
		logSASGameRecordEspionage(ePlayer, iGameTurn);
		logSASGameRecordDemographics(ePlayer, iGameTurn);
		logSASGameRecordAttitudes(ePlayer, iGameTurn);
		if (gGameRecordLogLevel >= 3) logSASGameRecordDiplomaticMemories(ePlayer, iGameTurn);
		logSASGameRecordDiploStatus(ePlayer, iGameTurn);
		logSASGameRecordUnitPosture(ePlayer, iGameTurn);
		logSASGameRecordWorkers(ePlayer, iGameTurn);
		logSASGameRecordExpansion(ePlayer, iGameTurn);
		logSASGameRecordSettlers(ePlayer, iGameTurn);
		logSASGameRecordWorkedPlots(ePlayer, iGameTurn);
		logSASGameRecordCities(ePlayer, iGameTurn);
	}
	kPrevious.bValid = true;
	kPrevious.iScore = iScore;
	kPrevious.iCities = iCities;
	kPrevious.iPopulation = iPopulation;
	kPrevious.iLand = iLand;
	kPrevious.iUnits = iUnits;
	kPrevious.iCombatUnits = iCombatUnits;
	kPrevious.iMilitarySupportUnits = iMilitarySupportUnits;
	kPrevious.iPower = iPower;
	kPrevious.iGold = iGold;
	kPrevious.iGoldRate = iGoldRate;
	kPrevious.iResearchRate = iResearchRate;
	if (gGameRecordLogLevel >= 2)
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

static void logSASGameRecordSnapshot(int iGameTurn, char const* szReason)
{
	CvGame const& kGame = GC.getGame();
	logSASGameRecord("GAME_RECORD_TURN_BEGIN turn=%d reason=%s elapsed=%d year=%d playersAlive=%d teamsAlive=%d totalCities=%d totalPopulation=%d",
			iGameTurn, szReason, kGame.getElapsedGameTurns(), kGame.getGameTurnYear(), kGame.countCivPlayersAlive(), kGame.countCivTeamsAlive(), kGame.getNumCities(), kGame.getTotalPopulation());
	logSASGameRecordRunStatus(szReason);
	if (gGameRecordLogLevel >= 2)
	{
		logSASGameRecordMapBonusTotals(iGameTurn);
		logSASGameRecordEnvironment(iGameTurn);
		logSASGameRecordVoteSources(iGameTurn);
	}
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		if (GET_PLAYER(eLoopPlayer).isAlive() && !GET_PLAYER(eLoopPlayer).isBarbarian())
			logSASGameRecordPlayerSnapshot(eLoopPlayer, iGameTurn);
	}
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (GET_TEAM(eLoopTeam).isAlive() && !GET_TEAM(eLoopTeam).isBarbarian())
			logSASGameRecordTeamSnapshot(eLoopTeam, iGameTurn);
	}
	if (gGameRecordLogLevel >= 2) logSASGameRecordBattleBuckets(iGameTurn);
	logSASGameRecord("GAME_RECORD_TURN_END turn=%d reason=%s", iGameTurn, szReason);
	g_iSASGameRecordLastFullSnapshotTurn = iGameTurn;
}

void logSASGameRecordTurn(int iGameTurn)
{
	// <!-- custom: Victory now forces a full snapshot immediately. If it occurs on an ordinary snapshot turn, do not repeat the same large snapshot again at end-of-turn. (GPT-5.6-Sol) -->
	if (g_iSASGameRecordLastFullSnapshotTurn == iGameTurn)
		return;
	logSASGameRecordSnapshot(iGameTurn, "interval");
}

void updateSASGameRecordPlayerTurnState(PlayerTypes ePlayer)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	if (kPlayer.getGoldenAgeTurns() > 0)
		g_aiSASGameRecordTotalGoldenAgeTurns[ePlayer]++;
	if (kPlayer.getAnarchyTurns() > 0)
		g_aiSASGameRecordTotalAnarchyTurns[ePlayer]++;
}


static void countSASGameRecordVisibleEnemiesNearPlot(CvPlot const& kCenter, PlayerTypes ePlayer, int iRange, int& iVisibleEnemies, int& iVisibleCombatEnemies, CvUnit const*& pNearestEnemy, int& iNearestEnemyDistance)
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

static void logSASGameRecordCityUnits(CvCity const& kCity, char const* szReason)
{
	SASGameRecordPlotUnitCounts kCounts;
	collectSASGameRecordPlotUnitCounts(kCity.getPlot(), kCity.getOwner(), kCounts);
	int iVisibleEnemies = 0;
	int iVisibleCombatEnemies = 0;
	int iNearestEnemyDistance = -1;
	CvUnit const* pNearestEnemy = NULL;
	countSASGameRecordVisibleEnemiesNearPlot(kCity.getPlot(), kCity.getOwner(), 2, iVisibleEnemies, iVisibleCombatEnemies, pNearestEnemy, iNearestEnemyDistance);
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
	logSASGameRecord("GAME_RECORD_CITY_UNITS turn=%d reason=%s player=%d cityId=%d city=%S x=%d y=%d pop=%d ownerUnits=%d militaryUnits=%d civilianUnits=%d defenders=%d healthyDefenders=%d woundedDefenders=%d settlers=%d workers=%d attackers=%d bestDefenderId=%d bestDefenderUnit=%s bestDefenderAI=%s bestDefenderDamage=%d visibleEnemiesR2=%d visibleCombatEnemiesR2=%d nearestEnemyPlayer=%d nearestEnemyUnit=%s nearestEnemyDist=%d nearestOtherOwnCityId=%d nearestOtherOwnCity=%S nearestOtherOwnCityDistance=%d",
		GC.getGame().getGameTurn(), szReason, kCity.getOwner(), kCity.getID(), getSASGameRecordQuotedCityName(&kCity).GetCString(), kCity.getX(), kCity.getY(), kCity.getPopulation(), kCounts.iUnits, kCounts.iMilitaryUnits, kCounts.iCivilianUnits, kCounts.iDefenders, kCounts.iHealthyDefenders, kCounts.iWoundedDefenders, kCounts.iSettlers, kCounts.iWorkers, kCounts.iAttackers, (kCounts.pBestDefender == NULL ? -1 : kCounts.pBestDefender->getID()), (kCounts.pBestDefender == NULL ? "-" : getSASGameRecordUnitType(kCounts.pBestDefender->getUnitType())), (kCounts.pBestDefender == NULL ? "-" : getSASGameRecordUnitAIType(kCounts.pBestDefender->AI_getUnitAIType())), (kCounts.pBestDefender == NULL ? -1 : kCounts.pBestDefender->getDamage()), iVisibleEnemies, iVisibleCombatEnemies, (pNearestEnemy == NULL ? -1 : pNearestEnemy->getOwner()), (pNearestEnemy == NULL ? "-" : getSASGameRecordUnitType(pNearestEnemy->getUnitType())), iNearestEnemyDistance, (pNearestOtherOwnCity == NULL ? -1 : pNearestOtherOwnCity->getID()), getSASGameRecordQuotedCityName(pNearestOtherOwnCity).GetCString(), iNearestOtherOwnCityDistance);
}

static bool logSASGameRecordSettlerCombatForPlot(CvUnit const* pWinner, CvUnit const* pLoser, CvPlot const* pPlot, PlayerTypes eSettlerOwner, bool bLoserWasSettler, bool bWinnerWasSettler)
{
	if (pWinner == NULL || pLoser == NULL || pPlot == NULL || eSettlerOwner == NO_PLAYER)
		return false;
	SASGameRecordPlotUnitCounts kCounts;
	collectSASGameRecordPlotUnitCounts(*pPlot, eSettlerOwner, kCounts);
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
			if (isSASGameRecordSettlerUnit(*pLoopUnit))
				iGroupSettlers++;
			if (pLoopUnit->canDefend(pLoopUnit->plot()))
				iGroupDefenders++;
		}
	}
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=SETTLER_GROUP_ATTACKED settlerOwner=%d settlerId=%d settlerUnit=%s x=%d y=%d cityPlot=%d winnerPlayer=%d winnerUnitId=%d winnerUnit=%s winnerAI=%s winnerBaseStr=%d winnerDamage=%d loserPlayer=%d loserUnitId=%d loserUnit=%s loserAI=%s loserBaseStr=%d loserDamage=%d loserWasSettler=%d winnerWasSettler=%d ownerUnitsOnPlot=%d militaryUnitsOnPlot=%d civilianUnitsOnPlot=%d settlersOnPlot=%d defendersOnPlot=%d healthyDefendersOnPlot=%d workersOnPlot=%d settlerGroupId=%d settlerGroupUnits=%d settlerGroupSettlers=%d settlerGroupDefenders=%d",
		GC.getGame().getGameTurn(), eSettlerOwner, (pSettler == NULL ? -1 : pSettler->getID()), (pSettler == NULL ? "-" : getSASGameRecordUnitType(pSettler->getUnitType())), pPlot->getX(), pPlot->getY(), pPlot->isCity(), pWinner->getOwner(), pWinner->getID(), getSASGameRecordUnitType(pWinner->getUnitType()), getSASGameRecordUnitAIType(pWinner->AI_getUnitAIType()), pWinner->baseCombatStr(), pWinner->getDamage(), pLoser->getOwner(), pLoser->getID(), getSASGameRecordUnitType(pLoser->getUnitType()), getSASGameRecordUnitAIType(pLoser->AI_getUnitAIType()), pLoser->baseCombatStr(), pLoser->getDamage(), bLoserWasSettler, bWinnerWasSettler, kCounts.iUnits, kCounts.iMilitaryUnits, kCounts.iCivilianUnits, kCounts.iSettlers, kCounts.iDefenders, kCounts.iHealthyDefenders, kCounts.iWorkers, (pSettlerGroup == NULL ? -1 : pSettlerGroup->getID()), iGroupUnits, iGroupSettlers, iGroupDefenders);
	return true;
}

static void logSASGameRecordSettlerCombatIfNeeded(CvUnit const* pWinner, CvUnit const* pLoser)
{
	if (pWinner == NULL || pLoser == NULL)
		return;
	bool const bLoserWasSettler = isSASGameRecordSettlerUnit(*pLoser);
	bool const bWinnerWasSettler = isSASGameRecordSettlerUnit(*pWinner);
	if (bLoserWasSettler && logSASGameRecordSettlerCombatForPlot(pWinner, pLoser, pLoser->plot(), pLoser->getOwner(), true, bWinnerWasSettler))
		return;
	if (bWinnerWasSettler && logSASGameRecordSettlerCombatForPlot(pWinner, pLoser, pWinner->plot(), pWinner->getOwner(), bLoserWasSettler, true))
		return;
	if (logSASGameRecordSettlerCombatForPlot(pWinner, pLoser, pLoser->plot(), pLoser->getOwner(), false, false))
		return;
	logSASGameRecordSettlerCombatForPlot(pWinner, pLoser, pWinner->plot(), pWinner->getOwner(), false, false);
}

// <!-- custom: GAME_RECORD_ACTION is narrower than a generic row: it records chronological gameplay happenings such as techs, city ownership, war state, Great People, unit upgrades, and victory. Do not rename this to GAME_RECORD_ROW; "row" is too generic because every log line is already a row. This keeps the row type useful without using "event", which can be confused with Civ4 EventInfo/random events. (GPT-5.5) -->
void logSASGameRecordTechAcquired(TechTypes eType, TeamTypes eTeam, PlayerTypes ePlayer)
{
	CvTechInfo const& kTech = GC.getInfo(eType);
	// <!-- custom: The acquisition turn already gives the exact chronology. Mark technologies that enable tech or gold trading, while team snapshots state whether each capability is currently available. (GPT-5.6-Sol) -->
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=TECH_ACQUIRED player=%d team=%d tech=%s enablesTechTrading=%d enablesGoldTrading=%d", GC.getGame().getGameTurn(), ePlayer, eTeam, getSASGameRecordTechType(eType), kTech.isTechTrading(), kTech.isGoldTrading());
}

void logSASGameRecordCityBuilt(CvCity const* pCity)
{
	if (pCity == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=CITY_BUILT player=%d cityId=%d city=%S x=%d y=%d pop=%d",
			GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), pCity->getX(), pCity->getY(), pCity->getPopulation());
	if (gGameRecordLogLevel >= 2)
	{
		logSASGameRecordCityBFC(*pCity, "built");
		logSASGameRecordCityUnits(*pCity, "built");
	}
}

void logSASGameRecordCityRazed(CvCity const* pCity, PlayerTypes ePlayer)
{
	if (pCity == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=CITY_RAZED player=%d oldOwner=%d cityId=%d city=%S x=%d y=%d pop=%d",
			GC.getGame().getGameTurn(), ePlayer, pCity->getOwner(), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), pCity->getX(), pCity->getY(), pCity->getPopulation());
}

void logSASGameRecordCityAcquired(PlayerTypes eOldOwner, PlayerTypes eNewOwner, CvCity const* pCity, bool bConquest, bool bTrade)
{
	if (pCity == NULL)
		return;
	if (eNewOwner >= 0 && eNewOwner < MAX_PLAYERS)
	{
		g_aiSASGameRecordCitiesAcquired[eNewOwner]++;
		if (bConquest)
			g_aiSASGameRecordCitiesConquered[eNewOwner]++;
		if (bTrade)
			g_aiSASGameRecordCitiesTradedIn[eNewOwner]++;
	}
	if (eOldOwner >= 0 && eOldOwner < MAX_PLAYERS)
	{
		g_aiSASGameRecordCitiesLost[eOldOwner]++;
		if (bConquest)
			g_aiSASGameRecordCitiesLostByConquest[eOldOwner]++;
		if (bTrade)
			g_aiSASGameRecordCitiesTradedOut[eOldOwner]++;
	}
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=CITY_ACQUIRED oldOwner=%d newOwner=%d cityId=%d city=%S x=%d y=%d pop=%d conquest=%d trade=%d",
			GC.getGame().getGameTurn(), eOldOwner, eNewOwner, pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), pCity->getX(), pCity->getY(), pCity->getPopulation(), bConquest, bTrade);
	if (gGameRecordLogLevel >= 2)
	{
		logSASGameRecordCityBFC(*pCity, "acquired");
		logSASGameRecordCityUnits(*pCity, "acquired");
	}
}

void logSASGameRecordWarStarted(TeamTypes eDeclarer, TeamTypes eTarget, WarPlanTypes eWarPlan, bool bPrimaryDoW, bool bNewDiplo, PlayerTypes eSponsor, bool bRandomEvent, WarDeclarationCause eCause)
{
	CvTeam const& kDeclarer = GET_TEAM(eDeclarer);
	CvTeam const& kTarget = GET_TEAM(eTarget);
	CvTeamAI const& kTargetAI = GET_TEAM(eTarget);
	char const* szCause = (bRandomEvent ? "RANDOM_EVENT" : (eSponsor != NO_PLAYER ? "SPONSORED_WAR" : getSASWarDeclarationCause(eCause)));
	// <!-- custom: `cause=DIRECT` identifies how war began, not why the AI selected that rival.
	// Preserve the target's exact victory state at declaration time so archived records show whether victory denial was relevant without falsely claiming it was the sole strategic motive. (GPT-5.6-Sol) -->
	int const iTargetMaxVictoryStage = getSASTeamMaxVictoryStage(eTarget);
	int const iTargetSpaceVictoryStage = getSASTeamSpaceVictoryStage(eTarget);
	int const iTargetSpaceshipParts = getSASTeamSpaceshipPartsBuilt(eTarget);
	int const iSpaceshipPartsRequired = getSASSpaceshipPartsRequired();
	int const iTargetSpaceshipPartsPercent = (iSpaceshipPartsRequired <= 0 ? 0 : iTargetSpaceshipParts * 100 / iSpaceshipPartsRequired);
	int const iTargetVictoryCountdown = kTargetAI.AI_getLowestVictoryCountdown();
	bool const bVictoryDenialContext = (iTargetVictoryCountdown >= 0 || iTargetMaxVictoryStage >= 4 || isSASTeamStage3SpaceVictoryThreat(eTarget));
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=WAR_STARTED declarerTeam=%d targetTeam=%d cause=%s primary=%d newDiplo=%d warPlan=%s sponsorPlayer=%d sponsorTeam=%d randomEvent=%d declarerMaster=%d targetMaster=%d declarerWarsAfter=%d targetWarsAfter=%d victoryDenialContext=%d targetMaxVictoryStage=%d targetSpaceVictoryStage=%d targetSpaceshipParts=%d targetSpaceshipPartsPercent=%d targetVictoryCountdown=%d",
			GC.getGame().getGameTurn(), eDeclarer, eTarget, szCause, bPrimaryDoW, bNewDiplo, getSASWarPlanType(eWarPlan),
			eSponsor, eSponsor == NO_PLAYER ? NO_TEAM : GET_PLAYER(eSponsor).getTeam(), bRandomEvent,
			kDeclarer.isAVassal() ? kDeclarer.getMasterTeam() : NO_TEAM, kTarget.isAVassal() ? kTarget.getMasterTeam() : NO_TEAM, kDeclarer.getNumWars(false), kTarget.getNumWars(false),
			bVictoryDenialContext, iTargetMaxVictoryStage, iTargetSpaceVictoryStage, iTargetSpaceshipParts, iTargetSpaceshipPartsPercent, iTargetVictoryCountdown);
}

void logSASGameRecordWarEnded(TeamTypes eTeam, TeamTypes eOtherTeam)
{
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=WAR_ENDED teamA=%d teamB=%d teamAWarsAfter=%d teamBWarsAfter=%d", GC.getGame().getGameTurn(), eTeam, eOtherTeam, GET_TEAM(eTeam).getNumWars(false), GET_TEAM(eOtherTeam).getNumWars(false));
}

void logSASGameRecordTeamMet(TeamTypes eTeam, TeamTypes eOtherTeam, bool bNewDiplo, int iX1, int iY1, int iX2, int iY2, CvPlot const* pTeamContactPlot, CvPlot const* pOtherContactPlot)
{
	const bool bMeetDataPlot1Valid = (iX1 >= 0 && iY1 >= 0 && iX1 < GC.getMap().getGridWidth() && iY1 < GC.getMap().getGridHeight());
	const bool bMeetDataPlot2Valid = (iX2 >= 0 && iY2 >= 0 && iX2 < GC.getMap().getGridWidth() && iY2 < GC.getMap().getGridHeight());
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=TEAM_MET team=%d otherTeam=%d bNewDiplo=%d teamMembers=%s otherMembers=%s meetDataPlot1=%d,%d meetDataPlot1Valid=%d meetDataPlot2=%d,%d meetDataPlot2Valid=%d teamContactPlot=%d,%d otherTeamContactPlot=%d,%d",
			GC.getGame().getGameTurn(), eTeam, eOtherTeam, bNewDiplo, getSASGameRecordTeamMembers(eTeam).GetCString(), getSASGameRecordTeamMembers(eOtherTeam).GetCString(), iX1, iY1, bMeetDataPlot1Valid, iX2, iY2, bMeetDataPlot2Valid, pTeamContactPlot == NULL ? -1 : pTeamContactPlot->getX(), pTeamContactPlot == NULL ? -1 : pTeamContactPlot->getY(), pOtherContactPlot == NULL ? -1 : pOtherContactPlot->getX(), pOtherContactPlot == NULL ? -1 : pOtherContactPlot->getY());
}

void logSASGameRecordPlayerGoldTrade(PlayerTypes eFromPlayer, PlayerTypes eToPlayer, int iAmount)
{
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GOLD_TRADE from=%d to=%d amount=%d", GC.getGame().getGameTurn(), eFromPlayer, eToPlayer, iAmount);
}

void logSASGameRecordReligionFounded(ReligionTypes eReligion, PlayerTypes ePlayer)
{
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=RELIGION_FOUNDED player=%d religion=%s", GC.getGame().getGameTurn(), ePlayer, getSASGameRecordReligionType(eReligion));
}

void logSASGameRecordCorporationFounded(CorporationTypes eCorporation, PlayerTypes ePlayer)
{
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=CORPORATION_FOUNDED player=%d corporation=%s", GC.getGame().getGameTurn(), ePlayer, getSASGameRecordCorporationType(eCorporation));
}

void logSASGameRecordGoldenAge(PlayerTypes ePlayer, bool bStart)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=%s player=%d goldenAgeTurns=%d totalGoldenAgeTurns=%d anarchyTurns=%d totalAnarchyTurns=%d", GC.getGame().getGameTurn(), bStart ? "GOLDEN_AGE_STARTED" : "GOLDEN_AGE_ENDED", ePlayer, kPlayer.getGoldenAgeTurns(), g_aiSASGameRecordTotalGoldenAgeTurns[ePlayer], kPlayer.getAnarchyTurns(), g_aiSASGameRecordTotalAnarchyTurns[ePlayer]);
}

void logSASGameRecordGoldenAgeTurnsChanged(PlayerTypes ePlayer, int iChange, int iOldGoldenAgeTurns, int iNewGoldenAgeTurns)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GOLDEN_AGE_TURNS_CHANGED player=%d change=%+d oldGoldenAgeTurns=%d newGoldenAgeTurns=%d goldenAgeTurns=%d totalGoldenAgeTurns=%d anarchyTurns=%d totalAnarchyTurns=%d", GC.getGame().getGameTurn(), ePlayer, iChange, iOldGoldenAgeTurns, iNewGoldenAgeTurns, kPlayer.getGoldenAgeTurns(), g_aiSASGameRecordTotalGoldenAgeTurns[ePlayer], kPlayer.getAnarchyTurns(), g_aiSASGameRecordTotalAnarchyTurns[ePlayer]);
}

void logSASGameRecordAnarchy(PlayerTypes ePlayer, bool bStart)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=%s player=%d anarchyTurns=%d totalAnarchyTurns=%d goldenAgeTurns=%d totalGoldenAgeTurns=%d revolutionTimer=%d conversionTimer=%d", GC.getGame().getGameTurn(), bStart ? "ANARCHY_STARTED" : "ANARCHY_ENDED", ePlayer, kPlayer.getAnarchyTurns(), g_aiSASGameRecordTotalAnarchyTurns[ePlayer], kPlayer.getGoldenAgeTurns(), g_aiSASGameRecordTotalGoldenAgeTurns[ePlayer], kPlayer.getRevolutionTimer(), kPlayer.getConversionTimer());
}

void logSASGameRecordBuildingBuilt(CvCity const* pCity, BuildingTypes eBuilding)
{
	if (pCity == NULL || eBuilding == NO_BUILDING || !GC.getInfo(eBuilding).isLimited())
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=WONDER_BUILT player=%d cityId=%d city=%S building=%s", GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), getSASGameRecordBuildingType(eBuilding));
}

void logSASGameRecordProjectBuilt(CvCity const* pCity, ProjectTypes eProject)
{
	if (pCity == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=PROJECT_BUILT player=%d cityId=%d city=%S project=%s", GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), getSASGameRecordProjectType(eProject));
}

void logSASGameRecordProductionOverflow(CvCity const* pCity, int iRawModifiedOverflow, int iUnmodifiedOverflow, int iKeptOverflow, int iLostProduction, int iUnusedCapacity, int iGold)
{
	if (pCity == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=PRODUCTION_OVERFLOW player=%d cityId=%d city=%S productionKind=%s production=%s rawModifiedOverflow=%d unmodifiedOverflow=%d keptOverflow=%d lostProduction=%d unusedOverflowCapacity=%d gold=%d", GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), getSASGameRecordCityProductionKind(*pCity), getSASGameRecordCityProductionType(*pCity), iRawModifiedOverflow, iUnmodifiedOverflow, iKeptOverflow, iLostProduction, iUnusedCapacity, iGold);
}

void logSASGameRecordProductionFailed(CvCity const* pCity, int iOrderData, bool bProject, int iInvestedProduction, int iGold)
{
	if (pCity == NULL)
		return;
	char const* szProduction = (bProject ? GC.getInfo((ProjectTypes)iOrderData).getType() : getSASGameRecordBuildingType((BuildingTypes)iOrderData));
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=PRODUCTION_FAILED_TO_GOLD player=%d cityId=%d city=%S productionKind=%s production=%s investedProduction=%d gold=%d", GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), bProject ? "PROJECT" : "BUILDING", szProduction, iInvestedProduction, iGold);
}

void logSASGameRecordVictoryLaunched(PlayerTypes ePlayer, VictoryTypes eVictory)
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
	bool const bProjectVictory = getSASGameRecordVictoryProjectState(kPlayer.getTeam(), eVictory, iPartsBuilt, iPartsMinimum, iPartsMaximum, bMinimumComplete, szProjectParts);
	int const iCountdown = kTeam.getVictoryCountdown(eVictory);
	// <!-- custom: PROJECT_BUILT rows could only imply a spaceship launch. Record the actual launch and its exact arrival state so a Space victory no longer has to be reconstructed from component timing. (GPT-5.6-Sol) -->
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=SPACESHIP_LAUNCHED player=%d team=%d victory=%s countdown=%d arrivalTurn=%d travelTurns=%d launchSuccessPercent=%d partsBuilt=%d partsMinimum=%d partsMaximum=%d projectParts=%s",
			GC.getGame().getGameTurn(), ePlayer, kPlayer.getTeam(), GC.getInfo(eVictory).getType(), iCountdown, iCountdown < 0 ? -1 : GC.getGame().getGameTurn() + iCountdown, bProjectVictory && bMinimumComplete ? kTeam.getVictoryDelay(eVictory) : -1, kTeam.getLaunchSuccessRate(eVictory), iPartsBuilt, iPartsMinimum, iPartsMaximum, bProjectVictory ? szProjectParts.GetCString() : "-");
}

static void logSASGameRecordVictoryProgressRemoved(TeamTypes eTeam, VictoryTypes eVictory, char const* szAction, char const* szCause, int iLaunchSuccessPercent, CvCity const* pCapital)
{
	CvTeam const& kTeam = GET_TEAM(eTeam);
	int iPartsBuilt = 0;
	int iPartsMinimum = 0;
	int iPartsMaximum = 0;
	bool bMinimumComplete = false;
	CvString szProjectParts;
	bool const bProjectVictory = getSASGameRecordVictoryProjectState(eTeam, eVictory, iPartsBuilt, iPartsMinimum, iPartsMaximum, bMinimumComplete, szProjectParts);
	int const iCountdown = kTeam.getVictoryCountdown(eVictory);
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=%s team=%d victory=%s cause=%s countdown=%d arrivalTurn=%d launchSuccessPercent=%d capitalPlayer=%d capitalCityId=%d capital=%S capitalX=%d capitalY=%d projectVictory=%d partsBuilt=%d partsMinimum=%d partsMaximum=%d projectParts=%s",
			GC.getGame().getGameTurn(), szAction, eTeam, getSASGameRecordVictoryType(eVictory), szCause, iCountdown, iCountdown < 0 ? -1 : GC.getGame().getGameTurn() + iCountdown,
			iLaunchSuccessPercent, pCapital == NULL ? NO_PLAYER : pCapital->getOwner(), pCapital == NULL ? -1 : pCapital->getID(), getSASGameRecordQuotedCityName(pCapital).GetCString(), pCapital == NULL ? -1 : pCapital->getX(), pCapital == NULL ? -1 : pCapital->getY(),
			bProjectVictory, iPartsBuilt, iPartsMinimum, iPartsMaximum, bProjectVictory ? szProjectParts.GetCString() : "-");
}

void logSASGameRecordVictoryProgressResetForCapital(CvCity const* pCapital)
{
	if (pCapital == NULL || GC.getGame().getGameState() != GAMESTATE_ON)
		return;
	TeamTypes const eTeam = pCapital->getTeam();
	CvTeam const& kTeam = GET_TEAM(eTeam);
	FOR_EACH_ENUM(Victory)
	{
		if (kTeam.getVictoryCountdown(eLoopVictory) >= 0)
			logSASGameRecordVictoryProgressRemoved(eTeam, eLoopVictory, "VICTORY_PROGRESS_RESET", "CAPITAL_LOST", kTeam.getLaunchSuccessRate(eLoopVictory), pCapital);
	}
}

void logSASGameRecordSpaceshipFailed(TeamTypes eTeam, VictoryTypes eVictory, int iLaunchSuccessPercent)
{
	if (eTeam == NO_TEAM || eVictory == NO_VICTORY)
		return;
	// <!-- custom: A failed arrival roll previously erased the countdown and spaceship projects without an explicit event. Preserve the losing launch state immediately before resetVictoryProgress removes it. (GPT-5.6-Sol) -->
	logSASGameRecordVictoryProgressRemoved(eTeam, eVictory, "SPACESHIP_FAILED", "LAUNCH_ROLL_FAILED", iLaunchSuccessPercent, NULL);
}

void logSASGameRecordVassalState(TeamTypes eMaster, TeamTypes eVassal, bool bVassal)
{
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=%s master=%d vassal=%d", GC.getGame().getGameTurn(), bVassal ? "VASSALAGE_STARTED" : "VASSALAGE_ENDED", eMaster, eVassal);
}

void logSASGameRecordVictory(TeamTypes eWinner, VictoryTypes eVictory)
{
	// <!-- custom: Victory can be reported before the ordinary end-turn hook. Flush this turn's buffered map history first so the final snapshot does not precede its last plot changes or map revelation. (GPT-5.6-Sol) -->
	if (gGameRecordLogLevel >= 2) flushSASGameRecordTurnChanges(GC.getGame().getGameTurn());
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=VICTORY team=%d victory=%s", GC.getGame().getGameTurn(), eWinner, eVictory == NO_VICTORY ? "-" : GC.getInfo(eVictory).getType());
	// <!-- custom: Periodic snapshots could stop several turns before victory, leaving every civilization's exact final state unknown. Force one complete marked snapshot now; the ordinary end-turn hook suppresses a duplicate on the same turn. (GPT-5.6-Sol) -->
	logSASGameRecordSnapshot(GC.getGame().getGameTurn(), "victory");
}

void logSASGameRecordPlayerEliminated(PlayerTypes ePlayer)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=PLAYER_ELIMINATED player=%d team=%d civ=%s leader=%s cities=%d units=%d score=%d power=%d playersAlive=%d teamsAlive=%d eliminatedPlayers=%s",
			GC.getGame().getGameTurn(), ePlayer, kPlayer.getTeam(), kPlayer.getCivilizationType() == NO_CIVILIZATION ? "-" : GC.getInfo(kPlayer.getCivilizationType()).getType(), kPlayer.getLeaderType() == NO_LEADER ? "-" : GC.getInfo(kPlayer.getLeaderType()).getType(), kPlayer.getNumCities(), kPlayer.getNumUnits(), kPlayer.calculateScore(), kPlayer.getPower(), GC.getGame().countCivPlayersAlive(), GC.getGame().countCivTeamsAlive(), getSASGameRecordEliminatedPlayers().GetCString());
	logSASGameRecordRunStatus("playerEliminated");
}

void logSASGameRecordPlayerAliveChanged(PlayerTypes ePlayer, bool bRevived)
{
	if (ePlayer < 0 || ePlayer >= MAX_PLAYERS)
		return;
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=%s player=%d team=%d civ=%s leader=%s cities=%d units=%d score=%d power=%d playersAlive=%d teamsAlive=%d playersEverAlive=%d",
			GC.getGame().getGameTurn(), bRevived ? "PLAYER_REVIVED" : "PLAYER_APPEARED", ePlayer, kPlayer.getTeam(), kPlayer.getCivilizationType() == NO_CIVILIZATION ? "-" : GC.getInfo(kPlayer.getCivilizationType()).getType(), kPlayer.getLeaderType() == NO_LEADER ? "-" : GC.getInfo(kPlayer.getLeaderType()).getType(), kPlayer.getNumCities(), kPlayer.getNumUnits(), kPlayer.calculateScore(), kPlayer.getPower(), GC.getGame().countCivPlayersAlive(), GC.getGame().countCivTeamsAlive(), GC.getGame().countCivPlayersEverAlive());
	logSASGameRecordRunStatus(bRevived ? "playerRevived" : "playerAppeared");
}

void logSASGameRecordAutoPlayChanged(int iOldValue, int iNewValue, bool bChangePlayerStatus)
{
	if (iOldValue == iNewValue)
		return;
	CvGame const& kGame = GC.getGame();
	const char* szAction = (iOldValue <= 0 && iNewValue > 0 ? "AUTOPLAY_STARTED" : (iOldValue > 0 && iNewValue <= 0 ? "AUTOPLAY_ENDED" : "AUTOPLAY_CHANGED"));
	const PlayerTypes eActivePlayer = kGame.getActivePlayer();
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=%s oldTurnsLeft=%d newTurnsLeft=%d activePlayer=%d changePlayerStatus=%d",
			kGame.getGameTurn(), szAction, iOldValue, iNewValue, eActivePlayer, bChangePlayerStatus);
	logSASGameRecordRunStatus(szAction);
}

void logSASGameRecordGreatPersonBorn(CvUnit const* pUnit, PlayerTypes ePlayer, CvCity const* pCity)
{
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_PERSON_BORN player=%d cityId=%d city=%S unit=%s combatXP=%d greatPeopleCreated=%d greatGeneralsCreated=%d greatGeneralThreshold=%d",
			GC.getGame().getGameTurn(), ePlayer, pCity == NULL ? -1 : pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), pUnit == NULL ? "-" : getSASGameRecordUnitType(pUnit->getUnitType()), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).getCombatExperience(), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).getGreatPeopleCreated(), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).getGreatGeneralsCreated(), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).greatPeopleThreshold(true));
}

void logSASGameRecordGreatPersonJoined(CvUnit const* pUnit, CvCity const* pCity, SpecialistTypes eSpecialist)
{
	if (pUnit == NULL || pCity == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_PERSON_JOINED_CITY player=%d unitId=%d unit=%s cityId=%d city=%S specialist=%s freeSpecialists=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), eSpecialist == NO_SPECIALIST ? "-" : GC.getInfo(eSpecialist).getType(), pCity->getFreeSpecialistCount(eSpecialist));
}

// <!-- custom: Great Person births and city joining were already recorded, but other completed Great Person missions disappeared from the record when the unit was consumed. Record the rare completed outcome and its concrete gain without logging AI candidate values or reasoning. (GPT-5.6-Sol) -->
void logSASGameRecordGreatPersonConstructed(CvUnit const* pUnit, CvCity const* pCity, BuildingTypes eBuilding)
{
	if (pUnit == NULL || pCity == NULL || eBuilding == NO_BUILDING)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_PERSON_USED use=CONSTRUCT_BUILDING player=%d unitId=%d unit=%s cityId=%d city=%S building=%s",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), getSASGameRecordBuildingType(eBuilding));
}

void logSASGameRecordGreatPersonDiscovered(CvUnit const* pUnit, TechTypes eTech, int iResearch)
{
	if (pUnit == NULL || eTech == NO_TECH)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_PERSON_USED use=DISCOVER_TECH player=%d unitId=%d unit=%s x=%d y=%d tech=%s research=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), pUnit->getX(), pUnit->getY(), getSASGameRecordTechType(eTech), iResearch);
}

void logSASGameRecordGreatPersonHurried(CvUnit const* pUnit, CvCity const* pCity, BuildingTypes eBuilding, int iProduction)
{
	if (pUnit == NULL || pCity == NULL || eBuilding == NO_BUILDING)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_PERSON_USED use=HURRY_BUILDING player=%d unitId=%d unit=%s cityId=%d city=%S building=%s production=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), getSASGameRecordBuildingType(eBuilding), iProduction);
}

void logSASGameRecordGreatPersonTradeMission(CvUnit const* pUnit, CvCity const* pCity, int iGold)
{
	if (pUnit == NULL || pCity == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_PERSON_USED use=TRADE_MISSION player=%d unitId=%d unit=%s targetPlayer=%d cityId=%d city=%S gold=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), pCity->getOwner(), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), iGold);
}

void logSASGameRecordGreatPersonGreatWork(CvUnit const* pUnit, CvCity const* pCity, int iCulture)
{
	if (pUnit == NULL || pCity == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_PERSON_USED use=GREAT_WORK player=%d unitId=%d unit=%s cityId=%d city=%S culture=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), iCulture);
}

void logSASGameRecordGreatPersonInfiltrated(CvUnit const* pUnit, CvCity const* pCity, int iEspionage)
{
	if (pUnit == NULL || pCity == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_PERSON_USED use=INFILTRATE player=%d unitId=%d unit=%s targetPlayer=%d targetTeam=%d cityId=%d city=%S espionage=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), pCity->getOwner(), pCity->getTeam(), pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), iEspionage);
}

void logSASGameRecordGreatPersonGoldenAgeConsumed(CvUnit const* pUnit)
{
	if (pUnit == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_PERSON_USED use=GOLDEN_AGE player=%d unitId=%d unit=%s x=%d y=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), pUnit->getX(), pUnit->getY());
}

void logSASGameRecordGreatPersonDied(CvUnit const* pUnit, PlayerTypes eResponsiblePlayer, char const* szCause)
{
	if (pUnit == NULL || (!pUnit->isGoldenAge() && pUnit->getUnitInfo().getLeaderExperience() <= 0))
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_PERSON_DIED player=%d unitId=%d unit=%s x=%d y=%d cause=%s responsiblePlayer=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), pUnit->getX(), pUnit->getY(), szCause, eResponsiblePlayer);
}

// <!-- custom: Periodic espionage totals showed investment against each rival but not what those points accomplished. Record only completed missions and actual interceptions at game-record level 2; mission selection and movement reasoning remain BBAI diagnostics. Resolve iExtraData to XML types so stolen technologies and sabotaged buildings/projects/units are readable. (GPT-5.6-Sol) -->
void logSASGameRecordEspionageMission(CvUnit const* pUnit, EspionageMissionTypes eMission, PlayerTypes eTargetPlayer, CvPlot const* pPlot, int iExtraData, int iCost, int iEPBefore, int iEPAfter, ImprovementTypes eTargetImprovement, RouteTypes eTargetRoute, UnitTypes eTargetUnit, int iEffectValue, char const* szEffectKind)
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
			szTargetType = getSASGameRecordImprovementType(eTargetImprovement);
		}
		else if (eTargetRoute != NO_ROUTE)
		{
			szTargetKind = "route";
			szTargetType = getSASGameRecordRouteType(eTargetRoute);
		}
	}
	else if (kMission.getDestroyBuildingCostFactor() > 0)
	{
		szTargetKind = "building";
		szTargetType = getSASGameRecordBuildingType((BuildingTypes)iExtraData);
	}
	else if (kMission.getDestroyProjectCostFactor() > 0)
	{
		szTargetKind = "project";
		szTargetType = getSASGameRecordProjectType((ProjectTypes)iExtraData);
	}
	else if (kMission.getDestroyUnitCostFactor() > 0 || kMission.getBuyUnitCostFactor() > 0)
	{
		szTargetKind = "unit";
		szTargetType = getSASGameRecordUnitType(eTargetUnit);
	}
	else if (kMission.getBuyTechCostFactor() > 0)
	{
		szTargetKind = "tech";
		szTargetType = getSASGameRecordTechType((TechTypes)iExtraData);
	}
	else if (kMission.getSwitchCivicCostFactor() > 0)
	{
		szTargetKind = "civic";
		szTargetType = getSASGameRecordCivicType((CivicTypes)iExtraData);
	}
	else if (kMission.getSwitchReligionCostFactor() > 0)
	{
		szTargetKind = "religion";
		szTargetType = getSASGameRecordReligionType((ReligionTypes)iExtraData);
	}
	CvCity const* pCity = (pPlot == NULL ? NULL : pPlot->getPlotCity());
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=ESPIONAGE_MISSION player=%d spyId=%d spy=%s spyAI=%s targetPlayer=%d targetTeam=%d mission=%s cost=%d epBefore=%d epAfter=%d cityId=%d city=%S x=%d y=%d targetKind=%s target=%s effectKind=%s effectValue=%d extraData=%d fortifyTurns=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), getSASGameRecordUnitAIType(pUnit->AI_getUnitAIType()), eTargetPlayer, eTargetPlayer == NO_PLAYER ? NO_TEAM : GET_PLAYER(eTargetPlayer).getTeam(), getSASGameRecordEspionageMissionType(eMission), iCost, iEPBefore, iEPAfter, pCity == NULL ? -1 : pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), pPlot == NULL ? -1 : pPlot->getX(), pPlot == NULL ? -1 : pPlot->getY(), szTargetKind, szTargetType, szEffectKind, iEffectValue, iExtraData, pUnit->getFortifyTurns());
}

void logSASGameRecordSpyIntercepted(CvUnit const* pUnit, PlayerTypes eTargetPlayer, char const* szPhase, int iModifier, int iInterceptChanceX100)
{
	if (pUnit == NULL)
		return;
	CvCity const* pCity = pUnit->getPlot().getPlotCity();
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=SPY_INTERCEPTED player=%d spyId=%d spy=%s spyAI=%s targetPlayer=%d targetTeam=%d phase=%s x=%d y=%d cityId=%d city=%S modifier=%d interceptChanceX100=%d fortifyTurns=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), getSASGameRecordUnitAIType(pUnit->AI_getUnitAIType()), eTargetPlayer, eTargetPlayer == NO_PLAYER ? NO_TEAM : GET_PLAYER(eTargetPlayer).getTeam(), szPhase, pUnit->getX(), pUnit->getY(), pCity == NULL ? -1 : pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), iModifier, iInterceptChanceX100, pUnit->getFortifyTurns());
}

void logSASGameRecordGreatGeneralAttached(CvUnit const* pGreatGeneral, CvUnit const* pTargetUnit, PromotionTypes ePromotion)
{
	if (pGreatGeneral == NULL || pTargetUnit == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_GENERAL_ATTACHED player=%d generalUnitId=%d generalUnit=%s targetUnitId=%d targetUnit=%s targetUnitAI=%s x=%d y=%d promotion=%s targetXP=%d targetLevel=%d",
			GC.getGame().getGameTurn(), pGreatGeneral->getOwner(), pGreatGeneral->getID(), getSASGameRecordUnitType(pGreatGeneral->getUnitType()), pTargetUnit->getID(), getSASGameRecordUnitType(pTargetUnit->getUnitType()), getSASGameRecordUnitAIType(pTargetUnit->AI_getUnitAIType()), pTargetUnit->getX(), pTargetUnit->getY(), ePromotion == NO_PROMOTION ? "-" : GC.getInfo(ePromotion).getType(), pTargetUnit->getExperience(), pTargetUnit->getLevel());
}


void logSASGameRecordUnitScrapped(CvUnit const* pUnit)
{
	if (pUnit == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=UNIT_SCRAPPED player=%d unitId=%d unit=%s unitAI=%s x=%d y=%d damage=%d xp=%d level=%d age=%d cargo=%d cargoSpace=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), getSASGameRecordUnitAIType(pUnit->AI_getUnitAIType()), pUnit->getX(), pUnit->getY(), pUnit->getDamage(), pUnit->getExperience(), pUnit->getLevel(), GC.getGame().getGameTurn() - pUnit->getGameTurnCreated(), pUnit->getCargo(), pUnit->cargoSpace());
}

void logSASGameRecordUnitUpgraded(CvUnit const* pOldUnit, CvUnit const* pNewUnit, int iCost)
{
	if (pOldUnit == NULL || pNewUnit == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=UNIT_UPGRADED player=%d oldUnitId=%d newUnitId=%d fromUnit=%s toUnit=%s unitAI=%s x=%d y=%d cost=%d oldXP=%d newXP=%d oldLevel=%d newLevel=%d",
			GC.getGame().getGameTurn(), pOldUnit->getOwner(), pOldUnit->getID(), pNewUnit->getID(), getSASGameRecordUnitType(pOldUnit->getUnitType()), getSASGameRecordUnitType(pNewUnit->getUnitType()), getSASGameRecordUnitAIType(pNewUnit->AI_getUnitAIType()), pNewUnit->getX(), pNewUnit->getY(), iCost, pOldUnit->getExperience(), pNewUnit->getExperience(), pOldUnit->getLevel(), pNewUnit->getLevel());
}

void logSASGameRecordUnitCaptured(PlayerTypes eOldOwner, UnitTypes eOldUnitType, CvUnit const* pNewUnit)
{
	if (pNewUnit == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=UNIT_CAPTURED oldOwner=%d newOwner=%d oldUnit=%s newUnitId=%d newUnit=%s newUnitAI=%s x=%d y=%d",
			GC.getGame().getGameTurn(), eOldOwner, pNewUnit->getOwner(), getSASGameRecordUnitType(eOldUnitType), pNewUnit->getID(), getSASGameRecordUnitType(pNewUnit->getUnitType()), getSASGameRecordUnitAIType(pNewUnit->AI_getUnitAIType()), pNewUnit->getX(), pNewUnit->getY());
}

void logSASGameRecordCityBombard(CvUnit const* pUnit, CvCity const* pCity, char const* szMode, int iBombardRate, bool bIgnoreBuildingDefense, int iDefenseModifierBefore, int iDefenseDamageBefore)
{
	if (pUnit == NULL || pCity == NULL)
		return;
	prepareSASGameRecordTurnChanges();
	const int iGameTurn = GC.getGame().getGameTurn();
	const int iDefenseModifierAfter = pCity->getDefenseModifier(false);
	const int iDefenseDamageAfter = pCity->getDefenseDamage();
	// <!-- custom: Consecutive bombard actions against the same city are synthetic history, not five nearly identical rows for five Trebuchets. Keep sequences separate when attacker/mode/city changes or defense continuity breaks, and the generic writer flushes a pending sequence before the next unrelated GameRecord row so battle-vs-bombard order remains observable. (GPT-5.6 Thinking) -->
	const bool bContinueSequence = (g_kSASGameRecordPendingCityBombard.bValid && g_kSASGameRecordPendingCityBombard.iTurn == iGameTurn && g_kSASGameRecordPendingCityBombard.szMode == szMode && g_kSASGameRecordPendingCityBombard.ePlayer == pUnit->getOwner() && g_kSASGameRecordPendingCityBombard.eTargetPlayer == pCity->getOwner() && g_kSASGameRecordPendingCityBombard.iCityId == pCity->getID() && g_kSASGameRecordPendingCityBombard.iDefenseModifierAfter == iDefenseModifierBefore && g_kSASGameRecordPendingCityBombard.iDefenseDamageAfter == iDefenseDamageBefore);
	if (!bContinueSequence)
	{
		flushSASGameRecordPendingCityBombard();
		g_kSASGameRecordPendingCityBombard.bValid = true;
		g_kSASGameRecordPendingCityBombard.iTurn = iGameTurn;
		g_kSASGameRecordPendingCityBombard.szMode = szMode;
		g_kSASGameRecordPendingCityBombard.ePlayer = pUnit->getOwner();
		g_kSASGameRecordPendingCityBombard.eTargetPlayer = pCity->getOwner();
		g_kSASGameRecordPendingCityBombard.iCityId = pCity->getID();
		g_kSASGameRecordPendingCityBombard.szCity = getSASGameRecordQuotedCityName(pCity);
		g_kSASGameRecordPendingCityBombard.iX = pCity->getX();
		g_kSASGameRecordPendingCityBombard.iY = pCity->getY();
		g_kSASGameRecordPendingCityBombard.iDefenseModifierBefore = iDefenseModifierBefore;
		g_kSASGameRecordPendingCityBombard.iDefenseDamageBefore = iDefenseDamageBefore;
	}
	g_kSASGameRecordPendingCityBombard.iActions++;
	g_kSASGameRecordPendingCityBombard.iBombardRateTotal += iBombardRate;
	if (bIgnoreBuildingDefense) g_kSASGameRecordPendingCityBombard.iIgnoreBuildingDefenseActions++;
	g_kSASGameRecordPendingCityBombard.iDefenseModifierAfter = iDefenseModifierAfter;
	g_kSASGameRecordPendingCityBombard.iTotalDefense = pCity->getTotalDefense(false);
	g_kSASGameRecordPendingCityBombard.iDefenseDamageAfter = iDefenseDamageAfter;
	g_kSASGameRecordPendingCityBombard.iDefenseDamageMax = GC.getMAX_CITY_DEFENSE_DAMAGE();
	addSASGameRecordCityBombardTypeCount(g_kSASGameRecordPendingCityBombard.aUnitTypes, getSASGameRecordUnitType(pUnit->getUnitType()));
	addSASGameRecordCityBombardTypeCount(g_kSASGameRecordPendingCityBombard.aUnitAIs, getSASGameRecordUnitAIType(pUnit->AI_getUnitAIType()));
}

void logSASGameRecordAirStrike(CvUnit const* pUnit, CvUnit const* pDefender, int iDefenderDamageBefore, int iDefenderDamageAfter)
{
	if (pUnit == NULL || pDefender == NULL)
		return;
	CvPlot const* pTargetPlot = pDefender->plot();
	CvCity const* pCity = (pTargetPlot == NULL ? NULL : pTargetPlot->getPlotCity());
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=AIR_STRIKE player=%d unitId=%d unit=%s unitAI=%s fromX=%d fromY=%d targetPlayer=%d targetUnitId=%d targetUnit=%s targetUnitAI=%s x=%d y=%d cityPlot=%d cityId=%d city=%S attackerAirBaseStr=%d defenderBaseStr=%d defenderDamageBefore=%d defenderDamageAfter=%d damageDealt=%d airCombatLimit=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), getSASGameRecordUnitAIType(pUnit->AI_getUnitAIType()), pUnit->getX(), pUnit->getY(), pDefender->getOwner(), pDefender->getID(), getSASGameRecordUnitType(pDefender->getUnitType()), getSASGameRecordUnitAIType(pDefender->AI_getUnitAIType()), pTargetPlot == NULL ? -1 : pTargetPlot->getX(), pTargetPlot == NULL ? -1 : pTargetPlot->getY(), pCity != NULL, pCity == NULL ? -1 : pCity->getID(), getSASGameRecordQuotedCityName(pCity).GetCString(), pUnit->airBaseCombatStr(), pDefender->baseCombatStr(), iDefenderDamageBefore, iDefenderDamageAfter, std::max(0, iDefenderDamageAfter - iDefenderDamageBefore), pUnit->airCombatLimit());
}

void logSASGameRecordAirInterception(CvUnit const* pAttacker, CvUnit const* pInterceptor, CvPlot const* pTargetPlot, int iAttackerDamageTaken, int iInterceptorDamageTaken)
{
	if (pAttacker == NULL || pInterceptor == NULL || pTargetPlot == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=AIR_INTERCEPTION attackerPlayer=%d attackerUnitId=%d attackerUnit=%s attackerUnitAI=%s interceptorPlayer=%d interceptorUnitId=%d interceptorUnit=%s interceptorUnitAI=%s x=%d y=%d attackerDamageTaken=%d interceptorDamageTaken=%d attackerDead=%d interceptorDead=%d attackerIsAir=%d",
			GC.getGame().getGameTurn(), pAttacker->getOwner(), pAttacker->getID(), getSASGameRecordUnitType(pAttacker->getUnitType()), getSASGameRecordUnitAIType(pAttacker->AI_getUnitAIType()), pInterceptor->getOwner(), pInterceptor->getID(), getSASGameRecordUnitType(pInterceptor->getUnitType()), getSASGameRecordUnitAIType(pInterceptor->AI_getUnitAIType()), pTargetPlot->getX(), pTargetPlot->getY(), iAttackerDamageTaken, iInterceptorDamageTaken, pAttacker->isDead(), pInterceptor->isDead(), pAttacker->getDomainType() == DOMAIN_AIR);
}

void logSASGameRecordAirBombPlot(CvUnit const* pUnit, CvPlot const* pTargetPlot, char const* szTargetKind, char const* szTarget, bool bSuccess)
{
	if (pUnit == NULL || pTargetPlot == NULL)
		return;
	logSASGameRecord("GAME_RECORD_ACTION turn=%d type=AIR_BOMB_PLOT player=%d unitId=%d unit=%s unitAI=%s fromX=%d fromY=%d targetOwner=%d x=%d y=%d targetKind=%s target=%s success=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameRecordUnitType(pUnit->getUnitType()), getSASGameRecordUnitAIType(pUnit->AI_getUnitAIType()), pUnit->getX(), pUnit->getY(), pTargetPlot->getOwner(), pTargetPlot->getX(), pTargetPlot->getY(), szTargetKind, szTarget, bSuccess);
}

void logSASGameRecordCombatResult(CvUnit const* pWinner, CvUnit const* pLoser)
{
	if (pWinner == NULL || pLoser == NULL)
		return;
	if (gGameRecordLogLevel > 0) logSASGameRecordSettlerCombatIfNeeded(pWinner, pLoser);
	PlayerTypes eWinner = pWinner->getOwner();
	PlayerTypes eLoser = pLoser->getOwner();
	CvPlot const* pPlot = pLoser->plot();
	const bool bCityPlot = (pPlot != NULL && pPlot->isCity());
	if (eWinner >= 0 && eWinner < MAX_PLAYERS)
	{
		g_aiSASGameRecordBattleWins[eWinner]++;
		g_aiSASGameRecordTotalBattleWins[eWinner]++;
		if (bCityPlot)
		{
			g_aiSASGameRecordCityBattleWins[eWinner]++;
			g_aiSASGameRecordTotalCityBattleWins[eWinner]++;
		}
	}
	if (eLoser >= 0 && eLoser < MAX_PLAYERS)
	{
		g_aiSASGameRecordBattleLosses[eLoser]++;
		g_aiSASGameRecordTotalBattleLosses[eLoser]++;
		if (bCityPlot)
		{
			g_aiSASGameRecordCityBattleLosses[eLoser]++;
			g_aiSASGameRecordTotalCityBattleLosses[eLoser]++;
		}
	}
	if (pLoser->getLeaderUnitType() != NO_UNIT)
	{
		logSASGameRecord("GAME_RECORD_ACTION turn=%d type=GREAT_GENERAL_UNIT_DIED player=%d unitId=%d unit=%s attachedGreatGeneral=%s winnerPlayer=%d winnerUnitId=%d winnerUnit=%s x=%d y=%d",
				GC.getGame().getGameTurn(), eLoser, pLoser->getID(), getSASGameRecordUnitType(pLoser->getUnitType()), getSASGameRecordUnitType(pLoser->getLeaderUnitType()), eWinner, pWinner->getID(), getSASGameRecordUnitType(pWinner->getUnitType()), pLoser->getX(), pLoser->getY());
	}
	logSASGameRecordGreatPersonDied(pLoser, eWinner, "COMBAT");
	if (gGameRecordLogLevel >= 3)
	{
		logSASGameRecord("GAME_RECORD_BATTLE turn=%d winner=%d loser=%d winnerUnit=%s loserUnit=%s x=%d y=%d cityPlot=%d winnerBaseStr=%d loserBaseStr=%d winnerDamage=%d loserDamage=%d winnerLeaderUnit=%s loserLeaderUnit=%s",
				GC.getGame().getGameTurn(), eWinner, eLoser, getSASGameRecordUnitType(pWinner->getUnitType()), getSASGameRecordUnitType(pLoser->getUnitType()), pLoser->getX(), pLoser->getY(), bCityPlot, pWinner->baseCombatStr(), pLoser->baseCombatStr(), pWinner->getDamage(), pLoser->getDamage(), getSASGameRecordUnitType(pWinner->getLeaderUnitType()), getSASGameRecordUnitType(pLoser->getLeaderUnitType()));
	}
}

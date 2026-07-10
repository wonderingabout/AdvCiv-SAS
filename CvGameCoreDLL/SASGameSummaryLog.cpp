#include "CvGameCoreDLL.h"
#include "SASGameSummaryLog.h"
#include "CvGame.h" // <!-- custom: Needed for game-summary turn, game-state, victory, RNG, and map-classification context rows. (GPT-5.5) -->
#include "CvCity.h" // <!-- custom: Needed by game-summary city action/BFC rows; SASGameSummaryLog.h only forward-declares CvCity. (GPT-5.5) -->
#include "CvUnit.h" // <!-- custom: Needed by game-summary battle rows; SASGameSummaryLog.h only forward-declares CvUnit. (GPT-5.5) -->
#include "CityPlotIterator.h" // <!-- custom: Needed by compact game-summary BFC composition rows. (ChatGPT-5.5) -->
#include "CvPlot.h" // <!-- custom: Needed by game-summary BFC and unit posture rows. (ChatGPT-5.5) -->
#include "CvInfo_Build.h" // <!-- custom: Needed for worker build-type names and build target classification in game-summary rows. (ChatGPT-5.5) -->
#include "CvInfo_Command.h" // <!-- custom: Needed for mission-type names in worker/settler game-summary rows. (ChatGPT-5.5) -->
#include "CvInfo_Building.h" // <!-- custom: Needed to classify city production in game-summary city rows. (ChatGPT-5.5) -->
#include "CvInfo_Tech.h" // <!-- custom: Needed to bucket owned-tech counts by era in game-summary rows. (ChatGPT-5.5) -->
#include "CvInfo_Terrain.h" // <!-- custom: Needed for terrain/feature/bonus type names in game-summary context rows. (ChatGPT-5.5) -->
#include "CvInfo_Organization.h" // <!-- custom: Needed for religion/corporation type names in game-summary action rows. (ChatGPT-5.5) -->
#include "CvInfo_Unit.h" // <!-- custom: Needed to classify unit composition and city production in game-summary rows. (ChatGPT-5.5) -->
#include "CvInfo_City.h" // <!-- custom: Needed for specialist and process type names in game-summary city rows. (ChatGPT-5.5) -->
#include "CvInfo_Civics.h" // <!-- custom: Needed for policy/civic names in game-summary advisor rows. (ChatGPT-5.5) -->
#include "CvInfo_GameOption.h" // <!-- custom: Needed to log enabled game-option type names; CvGlobals only forward-declares CvGameOptionInfo. (GPT-5.5) -->
#include "CvMap.h" // <!-- custom: Needed to log map dimensions; CvGlobals only forward-declares CvMap. (GPT-5.5) -->
#include "CvSelectionGroup.h" // <!-- custom: Needed to inspect worker/settler mission queues in game-summary rows. (ChatGPT-5.5) -->
#include "CvPlotGroup.h" // <!-- custom: Needed to identify connected city networks in game-summary city rows. (ChatGPT-5.5) -->
#include "CvArea.h" // <!-- custom: Needed for area-wide city happiness/health detail rows. (ChatGPT-5.5) -->
#include "CvPlayerAI.h" // <!-- custom: Needed for attitude/glance values in game-summary advisor rows. (ChatGPT-5.5) -->
#include "CvTeamAI.h" // <!-- custom: Needed for team-level worst-enemy state in game-summary diplomacy-status rows. (ChatGPT-5.5) -->
#include <time.h>
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
	const CvString szLogName = getSASGameSummaryLogName();
	logSASGameSummary("%s utc=%s logFile=%s turn=%d elapsed=%d year=%d scenario=%d activePlayer=%d activeCivilization=%s activeHandicap=%s playersDefined=%d playersAlive=%d playersEverAlive=%d humans=%d",
			szRowType, getSASGameSummaryLogTimestamp().GetCString(), szLogName.GetCString(), kGame.getGameTurn(), kGame.getElapsedGameTurns(), kGame.getGameTurnYear(), kGame.isScenario(), eActivePlayer, szActiveCivilization, szActiveHandicap, kInitCore.getNumDefinedPlayers(), kGame.countCivPlayersAlive(), kGame.countCivPlayersEverAlive(), kGame.getNumHumanPlayers());
	logSASGameSummary("GAME_SUMMARY_GAME_SETTINGS mapScript=%S map=%dx%d landHeavy=%d navalHeavy=%d world=%s climate=%s seaLevel=%s gameSpeed=%s startEra=%s gameHandicap=%s options=%s",
			kInitCore.getMapScriptName().GetCString(), GC.getMap().getGridWidth(), GC.getMap().getGridHeight(), kGame.isLandHeavyMapnameCached(), kGame.isNavalHeavyMapnameCached(), GC.getInfo(kInitCore.getWorldSize()).getType(), GC.getInfo(kInitCore.getClimate()).getType(), GC.getInfo(kInitCore.getSeaLevel()).getType(), GC.getInfo(kGame.getGameSpeedType()).getType(), GC.getInfo(kGame.getStartEra()).getType(), GC.getInfo(kGame.getHandicapType()).getType(), szGameOptions.GetCString());
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
	logSASGameSummary("GAME_SUMMARY_NEW_GAME_INITIALIZING utc=%s logFile=%s", getSASGameSummaryLogTimestamp().GetCString(), getSASGameSummaryLogName().GetCString());
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
static int g_aiSASGameSummaryTotalGoldenAgeTurns[MAX_PLAYERS];
static int g_aiSASGameSummaryTotalAnarchyTurns[MAX_PLAYERS];

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
		g_aiSASGameSummaryTotalGoldenAgeTurns[iI] = 0;
		g_aiSASGameSummaryTotalAnarchyTurns[iI] = 0;
		g_akSASGameSummaryPlayerPrevious[iI].bValid = false;
	}
	for (int iI = 0; iI < MAX_TEAMS; iI++)
	{
		g_akSASGameSummaryTeamPrevious[iI].bValid = false;
		g_akSASGameSummaryTeamPrevious[iI].bContactsValid = false;
	}
	g_kSASGameSummaryGlobalPrevious.bValid = false;
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

static const char* getSASGameSummaryBuildType(BuildTypes eBuild)
{
	return (eBuild == NO_BUILD ? "-" : GC.getInfo(eBuild).getType());
}

static const char* getSASGameSummaryMissionType(MissionTypes eMission)
{
	return (eMission == NO_MISSION ? "-" : GC.getInfo(eMission).getType());
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

static void getSASGameSummaryPlotCompositionTypes(SASGameSummaryPlotComposition const& kComposition, CvString& szTerrains, CvString& szFeatures, CvString& szBonuses, CvString& szImprovements, CvString& szRoutes)
{
	for (int iI = 0; iI < GC.getNumTerrainInfos(); iI++)
		appendSASGameSummaryTypeCount(szTerrains, getSASGameSummaryTerrainType((TerrainTypes)iI), kComposition.aiTerrains[iI]);
	for (int iI = 0; iI < GC.getNumFeatureInfos(); iI++)
		appendSASGameSummaryTypeCount(szFeatures, getSASGameSummaryFeatureType((FeatureTypes)iI), kComposition.aiFeatures[iI]);
	for (int iI = 0; iI < GC.getNumBonusInfos(); iI++)
		appendSASGameSummaryTypeCount(szBonuses, getSASGameSummaryBonusType((BonusTypes)iI), kComposition.aiBonuses[iI]);
	for (int iI = 0; iI < GC.getNumImprovementInfos(); iI++)
		appendSASGameSummaryTypeCount(szImprovements, getSASGameSummaryImprovementType((ImprovementTypes)iI), kComposition.aiImprovements[iI]);
	for (int iI = 0; iI < GC.getNumRouteInfos(); iI++)
		appendSASGameSummaryTypeCount(szRoutes, getSASGameSummaryRouteType((RouteTypes)iI), kComposition.aiRoutes[iI]);
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
			GC.getGame().getGameTurn(), szReason, kCity.getOwner(), kCity.getID(), kCity.getName().GetCString(), kCity.getX(), kCity.getY(), kComposition.iPlots, iOwned, kComposition.iLand, kComposition.iWater, kComposition.iHills, kComposition.iPeaks, kComposition.iRiverSide, kComposition.iFreshWater, kComposition.iCoastal, kComposition.iImproved, kComposition.iUnimprovedLand, kComposition.iRoaded, kComposition.iBonusImproved, kComposition.iBonusUnimproved, kComposition.iWorked, kComposition.iWorkedImproved, kComposition.iWorkedUnimproved, kComposition.iNatureFood, kComposition.iNatureProduction, kComposition.iNatureCommerce, kComposition.iCurrentFood, kComposition.iCurrentProduction, kComposition.iCurrentCommerce, getSASGameSummaryOrDash(szTerrains).GetCString(), getSASGameSummaryOrDash(szFeatures).GetCString(), getSASGameSummaryOrDash(szBonuses).GetCString(), getSASGameSummaryOrDash(szImprovements).GetCString(), getSASGameSummaryOrDash(szRoutes).GetCString());
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
	logSASGameSummary("GAME_SUMMARY_PLAYER_SETUP turn=%d player=%d team=%d alive=%d everAlive=%d human=%d slotStatus=%d playerName=%S civType=%s civName=%S civShortName=%S leaderType=%s leaderName=%S favoriteCivic=%s handicap=%s",
			GC.getGame().getGameTurn(), ePlayer, kPlayer.getTeam(), kPlayer.isAlive(), kPlayer.isEverAlive(), kPlayer.isHuman(), kInitCore.getSlotStatus(ePlayer), kPlayer.getName(0), szCivType, kPlayer.getCivilizationDescription(0), kPlayer.getCivilizationShortDescription(0), szLeaderType, szLeaderName, getSASGameSummaryCivicType(kPlayer.getFavoriteCivic()), kPlayer.getHandicapType() == NO_HANDICAP ? "-" : GC.getInfo(kPlayer.getHandicapType()).getType());
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
	logSASGameSummary("GAME_SUMMARY_TEAM turn=%d team=%d members=%s alive=%d deltaValid=%d techs=%d techsDelta=%+d techEraCounts=%s land=%d landDelta=%+d landPctX100=%d landPctX100Delta=%+d pop=%d popDelta=%+d popPctX100=%d popPctX100Delta=%+d wars=%s vassals=%s master=%d",
			iGameTurn, eTeam, getSASGameSummaryTeamMembers(eTeam).GetCString(), kTeam.isAlive(), kPrevious.bValid, iTechs, getSASGameSummaryDelta(kPrevious.bValid, iTechs, kPrevious.iTechs), getSASGameSummaryTechEraCounts(eTeam).GetCString(), iLand, getSASGameSummaryDelta(kPrevious.bValid, iLand, kPrevious.iLand), iLandPctX100, getSASGameSummaryDelta(kPrevious.bValid, iLandPctX100, kPrevious.iLandPctX100), iPopulation, getSASGameSummaryDelta(kPrevious.bValid, iPopulation, kPrevious.iPopulation), iPopPctX100, getSASGameSummaryDelta(kPrevious.bValid, iPopPctX100, kPrevious.iPopPctX100), getSASGameSummaryWarTeams(eTeam).GetCString(), getSASGameSummaryVassalTeams(eTeam).GetCString(), eMaster);
	if (gGameSummaryLogLevel >= 2) logSASGameSummaryTeamContacts(eTeam, iGameTurn, "snapshot");
	kPrevious.bValid = true;
	kPrevious.iTechs = iTechs;
	kPrevious.iLand = iLand;
	kPrevious.iLandPctX100 = iLandPctX100;
	kPrevious.iPopulation = iPopulation;
	kPrevious.iPopPctX100 = iPopPctX100;

	FOR_EACH_ENUM(Victory)
	{
		if (!kGame.isVictoryValid(eLoopVictory))
			continue;
		const int iLandNeed = kGame.getAdjustedLandPercent(eLoopVictory);
		const int iPopNeed = kGame.getAdjustedPopulationPercent(eLoopVictory);
		if (iLandNeed > 0 || iPopNeed > 0)
			logSASGameSummary("GAME_SUMMARY_VICTORY_PROGRESS turn=%d team=%d victory=%s landPctX100=%d landNeed=%d popPctX100=%d popNeed=%d countdown=%d", iGameTurn, eTeam, GC.getInfo(eLoopVictory).getType(), iLandPctX100, iLandNeed, iPopPctX100, iPopNeed, kTeam.getVictoryCountdown(eLoopVictory));
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

static void logSASGameSummaryPolicies(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	logSASGameSummary("GAME_SUMMARY_POLICIES turn=%d player=%d civics=%s favoriteCivic=%s stateReligion=%s cityReligions=%s cityCorporations=%s",
			iGameTurn, ePlayer, getSASGameSummaryCivicList(kPlayer).GetCString(), getSASGameSummaryCivicType(kPlayer.getFavoriteCivic()), getSASGameSummaryReligionType(kPlayer.getStateReligion()), getSASGameSummaryPlayerCityReligions(kPlayer).GetCString(), getSASGameSummaryPlayerCityCorporations(kPlayer).GetCString());
}

static void logSASGameSummaryEspionage(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvTeam const& kTeam = GET_TEAM(kPlayer.getTeam());
	SASGameSummaryPlayerPrevious& kPrevious = g_akSASGameSummaryPlayerPrevious[ePlayer];
	CvString szWeights;
	CvString szPoints;
	CvString szModifiers;
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
	logSASGameSummary("GAME_SUMMARY_ESPIONAGE turn=%d player=%d team=%d espionageRate=%d espionagePercent=%d teamEP=%d unspentEP=%d weights=%s pointsAgainst=%s modifiers=%s",
			iGameTurn, ePlayer, kPlayer.getTeam(), iEspionageRate, iEspionagePercent, iTeamEP, iUnspentEP, getSASGameSummaryOrDash(szWeights).GetCString(), getSASGameSummaryOrDash(szPoints).GetCString(), getSASGameSummaryOrDash(szModifiers).GetCString());
	logSASGameSummary("GAME_SUMMARY_ESPIONAGE_DELTAS turn=%d player=%d deltaValid=%d espionageRateDelta=%+d espionagePercentDelta=%+d teamEPDelta=%+d unspentEPDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, getSASGameSummaryDelta(kPrevious.bValid, iEspionageRate, kPrevious.iEspionageRate), getSASGameSummaryDelta(kPrevious.bValid, iEspionagePercent, kPrevious.iEspionagePercent), getSASGameSummaryDelta(kPrevious.bValid, iTeamEP, kPrevious.iTeamEP), getSASGameSummaryDelta(kPrevious.bValid, iUnspentEP, kPrevious.iUnspentEP));
	kPrevious.iEspionageRate = iEspionageRate;
	kPrevious.iEspionagePercent = iEspionagePercent;
	kPrevious.iTeamEP = iTeamEP;
	kPrevious.iUnspentEP = iUnspentEP;
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
				iGameTurn, getSASGameSummaryVoteSourceType(eLoopVoteSource), eSecretary, kGame.getSecretaryGeneralTimer(eLoopVoteSource), kGame.getVoteTimer(eLoopVoteSource), getSASGameSummaryReligionType(eReligion), pSourceCity == NULL ? -1 : pSourceCity->getOwner(), pSourceCity == NULL ? -1 : pSourceCity->getID(), pSourceCity == NULL ? L"-" : pSourceCity->getName().GetCString(), pSourceCity == NULL ? -1 : pSourceCity->getX(), pSourceCity == NULL ? -1 : pSourceCity->getY(), getSASGameSummaryOrDash(szVotingTeams).GetCString(), getSASGameSummaryOrDash(szFullTeams).GetCString(), getSASGameSummaryOrDash(szVotes).GetCString(), getSASGameSummaryOrDash(szVictoryVotes).GetCString());
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
	std::vector<int> aiUnitAI(NUM_UNITAI_TYPES, 0);
	std::vector<int> aiUnitCombat(GC.getNumUnitCombatInfos(), 0);
	std::vector<int> aiPromotions(gGameSummaryLogLevel >= 3 ? GC.getNumPromotionInfos() : 0, 0);
	int iLoop = 0;
	for (CvUnit const* pLoopUnit = kPlayer.firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iLoop))
	{
		iTotal++;
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
	CvString szUnitAI;
	CvString szUnitCombat;
	CvString szPromotions;
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
	logSASGameSummary("GAME_SUMMARY_UNIT_COMPOSITION turn=%d player=%d unitAI=%s unitCombat=%s", iGameTurn, ePlayer, getSASGameSummaryOrDash(szUnitAI).GetCString(), getSASGameSummaryOrDash(szUnitCombat).GetCString());
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
					iGameTurn, ePlayer, pLoopUnit->getID(), getSASGameSummaryUnitType(pLoopUnit->getUnitType()), getSASGameSummaryUnitAIType(pLoopUnit->AI_getUnitAIType()), pLoopUnit->getX(), pLoopUnit->getY(), getSASGameSummaryMissionType(eMission), pPlot->getOwner(), getSASGameSummaryTerrainType(pPlot->getTerrainType()), getSASGameSummaryFeatureType(pPlot->getFeatureType()), getSASGameSummaryBonusType(pPlot->getBonusType(pLoopUnit->getTeam())), getSASGameSummaryImprovementType(pPlot->getImprovementType()), getSASGameSummaryRouteType(pPlot->getRouteType()), isSASGameSummaryUnitGuarded(*pLoopUnit), isSASGameSummaryUnitThreatened(*pLoopUnit), pNearestCity == NULL ? -1 : pNearestCity->getID(), pNearestCity == NULL ? L"-" : pNearestCity->getName().GetCString(), iNearestDistance);
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
	return getSASGameSummaryOrDash(szList);
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
	logSASGameSummary("GAME_SUMMARY_CITY turn=%d player=%d cityId=%d city=%S x=%d y=%d pop=%d foodSurplus=%d happySurplus=%d healthSurplus=%d food=%d prod=%d commerce=%d garrison=%d connectedToCapital=%d plotGroupId=%d tradeRoutes=%d domesticTradeRoutes=%d foreignTradeRoutes=%d tradeFood=%d tradeProd=%d tradeCommerce=%d productionKind=%s production=%s productionTurns=%d productionStored=%d productionNeeded=%d overflowProduction=%d featureProduction=%d specialists=%s freeSpecialists=%s gpProgress=%d gpThreshold=%d gpRate=%d gpTurnsLeft=%d gpOdds=%s",
			iGameTurn, kCity.getOwner(), kCity.getID(), kCity.getName().GetCString(), kCity.getX(), kCity.getY(), kCity.getPopulation(), kCity.foodDifference(), kCity.happyLevel() - kCity.unhappyLevel(), kCity.goodHealth() - kCity.badHealth(), kCity.getYieldRate(YIELD_FOOD), kCity.getYieldRate(YIELD_PRODUCTION), kCity.getYieldRate(YIELD_COMMERCE), kCity.plot()->getNumDefenders(kCity.getOwner()), kCity.isConnectedToCapital(), pPlotGroup == NULL ? -1 : pPlotGroup->getID(), kCity.getTradeRoutes(), iDomesticTradeRoutes, iForeignTradeRoutes, kCity.getTradeYield(YIELD_FOOD), kCity.getTradeYield(YIELD_PRODUCTION), kCity.getTradeYield(YIELD_COMMERCE), getSASGameSummaryCityProductionKind(kCity), getSASGameSummaryCityProductionType(kCity), kCity.getProductionTurnsLeft(), kCity.getProduction(), kCity.getProductionNeeded(), kCity.getOverflowProduction(), kCity.getFeatureProduction(), getSASGameSummaryCitySpecialists(kCity, false).GetCString(), getSASGameSummaryCitySpecialists(kCity, true).GetCString(), kCity.getGreatPeopleProgress(), kOwner.greatPeopleThreshold(false), kCity.getGreatPeopleRate(), kCity.GPTurnsLeft(), getSASGameSummaryCityGPOdds(kCity).GetCString());
	logSASGameSummary("GAME_SUMMARY_CITY_HAPPINESS turn=%d player=%d cityId=%d happy=%d unhappy=%d surplus=%d happySources=%s flatUnhappySources=%s angerPercentSources=%s",
			iGameTurn, kCity.getOwner(), kCity.getID(), kCity.happyLevel(), kCity.unhappyLevel(), kCity.happyLevel() - kCity.unhappyLevel(), getSASGameSummaryCityHappySources(kCity).GetCString(), getSASGameSummaryCityFlatUnhappySources(kCity).GetCString(), getSASGameSummaryCityAngerPercentSources(kCity).GetCString());
	logSASGameSummary("GAME_SUMMARY_CITY_HEALTH turn=%d player=%d cityId=%d goodHealth=%d badHealth=%d surplus=%d healthySources=%s unhealthySources=%s",
			iGameTurn, kCity.getOwner(), kCity.getID(), kCity.goodHealth(), kCity.badHealth(), kCity.goodHealth() - kCity.badHealth(), getSASGameSummaryCityHealthySources(kCity).GetCString(), getSASGameSummaryCityUnhealthySources(kCity).GetCString());
	if (gGameSummaryLogLevel >= 3) logSASGameSummary("GAME_SUMMARY_CITY_TRADE_PARTNERS turn=%d player=%d cityId=%d partners=%s", iGameTurn, kCity.getOwner(), kCity.getID(), getSASGameSummaryCityTradePartners(kCity).GetCString());
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
	logSASGameSummary("GAME_SUMMARY_CITIES turn=%d player=%d cities=%d capitalId=%d capital=%S connectedToCapital=%d totalFoodSurplus=%d totalHappySurplus=%d totalHealthSurplus=%d totalFood=%d totalProd=%d totalCommerce=%d tradeRoutes=%d domesticTradeRoutes=%d foreignTradeRoutes=%d tradeFood=%d tradeProd=%d tradeCommerce=%d unhappyCities=%d unhealthyCities=%d starvingCities=%d specialists=%d freeSpecialists=%d garrison=%d nextGPCityId=%d nextGPCity=%S nextGPTurns=%d nextGPRate=%d nextGPProgress=%d citiesProducingUnits=%d citiesProducingMilitary=%d citiesProducingWorkers=%d citiesProducingSettlers=%d citiesProducingBuildings=%d citiesProducingWonders=%d citiesProducingProjects=%d citiesProducingProcesses=%d",
			iGameTurn, ePlayer, iCities, pCapital == NULL ? -1 : pCapital->getID(), pCapital == NULL ? L"-" : pCapital->getName().GetCString(), iConnectedToCapital, iTotalFoodSurplus, iTotalHappySurplus, iTotalHealthSurplus, iTotalFoodYield, iTotalProductionYield, iTotalCommerceYield, iTotalTradeRoutes, iDomesticTradeRoutes, iForeignTradeRoutes, iTradeFood, iTradeProduction, iTradeCommerce, iUnhappyCities, iUnhealthyCities, iStarvingCities, iSpecialists, iFreeSpecialists, iGarrison, pNextGPCity == NULL ? -1 : pNextGPCity->getID(), pNextGPCity == NULL ? L"-" : pNextGPCity->getName().GetCString(), pNextGPCity == NULL ? -1 : iBestGPTurns, pNextGPCity == NULL ? 0 : pNextGPCity->getGreatPeopleRate(), pNextGPCity == NULL ? 0 : pNextGPCity->getGreatPeopleProgress(), iCitiesProducingUnits, iCitiesProducingMilitary, iCitiesProducingWorkers, iCitiesProducingSettlers, iCitiesProducingBuildings, iCitiesProducingWonders, iCitiesProducingProjects, iCitiesProducingProcesses);
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
	const int iResearchRate = (eResearch == NO_TECH ? 0 : kPlayer.calculateResearchRate(eResearch));
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
	logSASGameSummary("GAME_SUMMARY_PLAYER turn=%d player=%d team=%d civ=%s leader=%s isHuman=%d rank=%d deltaValid=%d score=%d scoreDelta=%+d cities=%d citiesDelta=%+d pop=%d popDelta=%+d land=%d landDelta=%+d units=%d unitsDelta=%+d militaryUnits=%d militaryUnitsDelta=%+d power=%d powerDelta=%+d gold=%d goldDelta=%+d gpt=%d gptDelta=%+d researchRate=%d researchRateDelta=%+d researchPercent=%d currentResearch=%s researchTurns=%d era=%s stateReligion=%s techScorePercent=%d combatXP=%d greatPeopleCreated=%d greatGeneralsCreated=%d greatGeneralThreshold=%d goldenAgeTurns=%d totalGoldenAgeTurns=%d anarchyTurns=%d totalAnarchyTurns=%d revolutionTimer=%d conversionTimer=%d wars=%s",
			iGameTurn, ePlayer, kPlayer.getTeam(), szCiv, szLeader, kPlayer.isHuman(), kGame.getPlayerRank(ePlayer) + 1, kPrevious.bValid, iScore, getSASGameSummaryDelta(kPrevious.bValid, iScore, kPrevious.iScore), iCities, getSASGameSummaryDelta(kPrevious.bValid, iCities, kPrevious.iCities), iPopulation, getSASGameSummaryDelta(kPrevious.bValid, iPopulation, kPrevious.iPopulation), iLand, getSASGameSummaryDelta(kPrevious.bValid, iLand, kPrevious.iLand), iUnits, getSASGameSummaryDelta(kPrevious.bValid, iUnits, kPrevious.iUnits), iMilitaryUnits, getSASGameSummaryDelta(kPrevious.bValid, iMilitaryUnits, kPrevious.iMilitaryUnits), iPower, getSASGameSummaryDelta(kPrevious.bValid, iPower, kPrevious.iPower), iGold, getSASGameSummaryDelta(kPrevious.bValid, iGold, kPrevious.iGold), iGoldRate, getSASGameSummaryDelta(kPrevious.bValid, iGoldRate, kPrevious.iGoldRate), iResearchRate, getSASGameSummaryDelta(kPrevious.bValid, iResearchRate, kPrevious.iResearchRate), kPlayer.getCommercePercent(COMMERCE_RESEARCH), getSASGameSummaryTechType(eResearch), iResearchTurns, szEra, getSASGameSummaryReligionType(kPlayer.getStateReligion()), kTeam.getBestKnownTechScorePercent(), kPlayer.getCombatExperience(), kPlayer.getGreatPeopleCreated(), kPlayer.getGreatGeneralsCreated(), kPlayer.greatPeopleThreshold(true), kPlayer.getGoldenAgeTurns(), g_aiSASGameSummaryTotalGoldenAgeTurns[ePlayer], kPlayer.getAnarchyTurns(), g_aiSASGameSummaryTotalAnarchyTurns[ePlayer], kPlayer.getRevolutionTimer(), kPlayer.getConversionTimer(), getSASGameSummaryWarTeams(kPlayer.getTeam()).GetCString());
	logSASGameSummary("GAME_SUMMARY_PLAYER_HISTORY turn=%d player=%d deltaValid=%d historyScore=%d historyScoreDelta=%+d historyEconomy=%d historyEconomyDelta=%+d historyIndustry=%d historyIndustryDelta=%+d historyAgriculture=%d historyAgricultureDelta=%+d historyPower=%d historyPowerDelta=%+d historyCulture=%d historyCultureDelta=%+d historyEspionage=%d historyEspionageDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, iHistoryScore, getSASGameSummaryDelta(kPrevious.bValid, iHistoryScore, kPrevious.iHistoryScore), iHistoryEconomy, getSASGameSummaryDelta(kPrevious.bValid, iHistoryEconomy, kPrevious.iHistoryEconomy), iHistoryIndustry, getSASGameSummaryDelta(kPrevious.bValid, iHistoryIndustry, kPrevious.iHistoryIndustry), iHistoryAgriculture, getSASGameSummaryDelta(kPrevious.bValid, iHistoryAgriculture, kPrevious.iHistoryAgriculture), iHistoryPower, getSASGameSummaryDelta(kPrevious.bValid, iHistoryPower, kPrevious.iHistoryPower), iHistoryCulture, getSASGameSummaryDelta(kPrevious.bValid, iHistoryCulture, kPrevious.iHistoryCulture), iHistoryEspionage, getSASGameSummaryDelta(kPrevious.bValid, iHistoryEspionage, kPrevious.iHistoryEspionage));
	if (gGameSummaryLogLevel >= 2)
	{
		logSASGameSummaryPlayerBonuses(ePlayer, iGameTurn, kPrevious);
		logSASGameSummaryPolicies(ePlayer, iGameTurn);
		logSASGameSummaryEspionage(ePlayer, iGameTurn);
		logSASGameSummaryDemographics(ePlayer, iGameTurn);
		logSASGameSummaryAttitudes(ePlayer, iGameTurn);
		logSASGameSummaryDiploStatus(ePlayer, iGameTurn);
		logSASGameSummaryUnitPosture(ePlayer, iGameTurn);
		logSASGameSummaryWorkers(ePlayer, iGameTurn);
		logSASGameSummarySettlers(ePlayer, iGameTurn);
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

void logSASGameSummaryTurn(int iGameTurn)
{
	CvGame const& kGame = GC.getGame();
	logSASGameSummary("GAME_SUMMARY_TURN_BEGIN turn=%d elapsed=%d year=%d playersAlive=%d teamsAlive=%d totalCities=%d totalPopulation=%d",
			iGameTurn, kGame.getElapsedGameTurns(), kGame.getGameTurnYear(), kGame.countCivPlayersAlive(), kGame.countCivTeamsAlive(), kGame.getNumCities(), kGame.getTotalPopulation());
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
	logSASGameSummary("GAME_SUMMARY_TURN_END turn=%d", iGameTurn);
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

// <!-- custom: GAME_SUMMARY_ACTION is narrower than a generic row: it records chronological gameplay happenings such as techs, city ownership, war state, Great People, unit upgrades, and victory. Do not rename this to GAME_SUMMARY_ROW; "row" is too generic because every log line is already a row. This keeps the row type useful without using "event", which can be confused with Civ4 EventInfo/random events. (GPT-5.5) -->
void logSASGameSummaryTechAcquired(TechTypes eType, TeamTypes eTeam, PlayerTypes ePlayer)
{
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=TECH_ACQUIRED player=%d team=%d tech=%s", GC.getGame().getGameTurn(), ePlayer, eTeam, getSASGameSummaryTechType(eType));
}

void logSASGameSummaryCityBuilt(CvCity const* pCity)
{
	if (pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=CITY_BUILT player=%d cityId=%d city=%S x=%d y=%d pop=%d",
			GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), pCity->getName().GetCString(), pCity->getX(), pCity->getY(), pCity->getPopulation());
	if (gGameSummaryLogLevel >= 2) logSASGameSummaryCityBFC(*pCity, "built");
}

void logSASGameSummaryCityRazed(CvCity const* pCity, PlayerTypes ePlayer)
{
	if (pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=CITY_RAZED player=%d oldOwner=%d cityId=%d city=%S x=%d y=%d pop=%d",
			GC.getGame().getGameTurn(), ePlayer, pCity->getOwner(), pCity->getID(), pCity->getName().GetCString(), pCity->getX(), pCity->getY(), pCity->getPopulation());
}

void logSASGameSummaryCityAcquired(PlayerTypes eOldOwner, PlayerTypes eNewOwner, CvCity const* pCity, bool bConquest, bool bTrade)
{
	if (pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=CITY_ACQUIRED oldOwner=%d newOwner=%d cityId=%d city=%S x=%d y=%d pop=%d conquest=%d trade=%d",
			GC.getGame().getGameTurn(), eOldOwner, eNewOwner, pCity->getID(), pCity->getName().GetCString(), pCity->getX(), pCity->getY(), pCity->getPopulation(), bConquest, bTrade);
	if (gGameSummaryLogLevel >= 2) logSASGameSummaryCityBFC(*pCity, "acquired");
}

void logSASGameSummaryChangeWar(bool bWar, TeamTypes eTeam, TeamTypes eOtherTeam)
{
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=%s teamA=%d teamB=%d", GC.getGame().getGameTurn(), bWar ? "WAR_STARTED" : "WAR_ENDED", eTeam, eOtherTeam);
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
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=WONDER_BUILT player=%d cityId=%d city=%S building=%s", GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), pCity->getName().GetCString(), getSASGameSummaryBuildingType(eBuilding));
}

void logSASGameSummaryProjectBuilt(CvCity const* pCity, ProjectTypes eProject)
{
	if (pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=PROJECT_BUILT player=%d cityId=%d city=%S project=%s", GC.getGame().getGameTurn(), pCity->getOwner(), pCity->getID(), pCity->getName().GetCString(), getSASGameSummaryProjectType(eProject));
}

void logSASGameSummaryVassalState(TeamTypes eMaster, TeamTypes eVassal, bool bVassal)
{
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=%s master=%d vassal=%d", GC.getGame().getGameTurn(), bVassal ? "VASSALAGE_STARTED" : "VASSALAGE_ENDED", eMaster, eVassal);
}

void logSASGameSummaryVictory(TeamTypes eWinner, VictoryTypes eVictory)
{
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=VICTORY team=%d victory=%s", GC.getGame().getGameTurn(), eWinner, eVictory == NO_VICTORY ? "-" : GC.getInfo(eVictory).getType());
}

void logSASGameSummaryGreatPersonBorn(CvUnit const* pUnit, PlayerTypes ePlayer, CvCity const* pCity)
{
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_BORN player=%d cityId=%d city=%S unit=%s combatXP=%d greatPeopleCreated=%d greatGeneralsCreated=%d greatGeneralThreshold=%d",
			GC.getGame().getGameTurn(), ePlayer, pCity == NULL ? -1 : pCity->getID(), pCity == NULL ? L"-" : pCity->getName().GetCString(), pUnit == NULL ? "-" : getSASGameSummaryUnitType(pUnit->getUnitType()), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).getCombatExperience(), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).getGreatPeopleCreated(), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).getGreatGeneralsCreated(), ePlayer == NO_PLAYER ? 0 : GET_PLAYER(ePlayer).greatPeopleThreshold(true));
}

void logSASGameSummaryGreatPersonJoined(CvUnit const* pUnit, CvCity const* pCity, SpecialistTypes eSpecialist)
{
	if (pUnit == NULL || pCity == NULL)
		return;
	logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_PERSON_JOINED_CITY player=%d unitId=%d unit=%s cityId=%d city=%S specialist=%s freeSpecialists=%d",
			GC.getGame().getGameTurn(), pUnit->getOwner(), pUnit->getID(), getSASGameSummaryUnitType(pUnit->getUnitType()), pCity->getID(), pCity->getName().GetCString(), eSpecialist == NO_SPECIALIST ? "-" : GC.getInfo(eSpecialist).getType(), pCity->getFreeSpecialistCount(eSpecialist));
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

void logSASGameSummaryCombatResult(CvUnit const* pWinner, CvUnit const* pLoser)
{
	if (pWinner == NULL || pLoser == NULL)
		return;
	PlayerTypes eWinner = pWinner->getOwner();
	PlayerTypes eLoser = pLoser->getOwner();
	CvPlot const* pPlot = pLoser->plot();
	const bool bCityPlot = (pPlot != NULL && pPlot->isCity());
	if (eWinner >= 0 && eWinner < MAX_PLAYERS)
	{
		g_aiSASGameSummaryBattleWins[eWinner]++;
		if (bCityPlot)
			g_aiSASGameSummaryCityBattleWins[eWinner]++;
	}
	if (eLoser >= 0 && eLoser < MAX_PLAYERS)
	{
		g_aiSASGameSummaryBattleLosses[eLoser]++;
		if (bCityPlot)
			g_aiSASGameSummaryCityBattleLosses[eLoser]++;
	}
	if (pLoser->getLeaderUnitType() != NO_UNIT)
	{
		logSASGameSummary("GAME_SUMMARY_ACTION turn=%d type=GREAT_GENERAL_UNIT_DIED player=%d unitId=%d unit=%s attachedGreatGeneral=%s winnerPlayer=%d winnerUnitId=%d winnerUnit=%s x=%d y=%d",
				GC.getGame().getGameTurn(), eLoser, pLoser->getID(), getSASGameSummaryUnitType(pLoser->getUnitType()), getSASGameSummaryUnitType(pLoser->getLeaderUnitType()), eWinner, pWinner->getID(), getSASGameSummaryUnitType(pWinner->getUnitType()), pLoser->getX(), pLoser->getY());
	}
	if (gGameSummaryLogLevel >= 3)
	{
		logSASGameSummary("GAME_SUMMARY_BATTLE turn=%d winner=%d loser=%d winnerUnit=%s loserUnit=%s x=%d y=%d cityPlot=%d winnerBaseStr=%d loserBaseStr=%d winnerDamage=%d loserDamage=%d winnerLeaderUnit=%s loserLeaderUnit=%s",
				GC.getGame().getGameTurn(), eWinner, eLoser, getSASGameSummaryUnitType(pWinner->getUnitType()), getSASGameSummaryUnitType(pLoser->getUnitType()), pLoser->getX(), pLoser->getY(), bCityPlot, pWinner->baseCombatStr(), pLoser->baseCombatStr(), pWinner->getDamage(), pLoser->getDamage(), getSASGameSummaryUnitType(pWinner->getLeaderUnitType()), getSASGameSummaryUnitType(pLoser->getLeaderUnitType()));
	}
}


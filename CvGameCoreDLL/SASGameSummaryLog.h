#pragma once

#ifndef SAS_GAME_SUMMARY_LOG_H
#define SAS_GAME_SUMMARY_LOG_H

// <!-- custom: Structured game-summary rows for autoplay comparison, game analysis, user-assistance summaries, and external LLM review. This is not a classic BBAI diagnostic category: it has its own XML defines, its own SASGameSummary_*.log files, and its own lightweight public header. Call sites should still gate before invoking helpers so disabled logging does not compute logging-only arguments. Pointer-only hooks use forward declarations here to avoid pulling city/unit headers into ordinary game files. (ChatGPT-5.5 + GPT-5.5) -->
bool isSASGameSummaryLogEnabled();
int getSASGameSummaryLogLevel();
int getSASGameSummaryTurnInterval();
void startSASGameSummaryLogForNewGame();
void logSASGameSummaryNewGameStarted();
void startSASGameSummaryLogForLoadedSave();

class CvCity;
class CvPlot;
class CvUnit;
// <!-- custom: Capture a plot before a logical action so one combined record can describe terrain, feature, resource, improvement, route and permanent event-yield changes. The empty constructor lets caller-gated hooks avoid the map lookups when game-summary logging is disabled. (GPT-5.6-Sol) -->
struct SASGameSummaryPlotState
{
	SASGameSummaryPlotState();
	explicit SASGameSummaryPlotState(CvPlot const& kPlot);
	TerrainTypes eTerrain;
	FeatureTypes eFeature;
	BonusTypes eBonus;
	ImprovementTypes eImprovement;
	RouteTypes eRoute;
	int aiExtraYield[NUM_YIELD_TYPES];
};
void logSASGameSummaryTurn(int iGameTurn);
// <!-- custom: Plot changes and permanent team exploration are buffered into compact coordinate lists and flushed once per turn; detailed before/after rows are reserved for non-routine causes. The environment hook receives values already computed by CvGame::doGlobalWarming so it adds no map scan. (GPT-5.6-Sol) -->
void flushSASGameSummaryTurnChanges(int iGameTurn);
void recordSASGameSummaryPlotChange(CvPlot const& kPlot, SASGameSummaryPlotState const& kOldState, char const* szCategory, char const* szCause, bool bDetailed);
void recordSASGameSummaryPlotRevealed(CvPlot const& kPlot, TeamTypes eTeam);
void logSASGameSummaryEnvironmentTurn(int iPollution, int iSustainabilityThreshold, int iLandDefense, int iIndexBefore, int iIndexBeforeRestoration, int iIndexEnd, int iWarmingChances, int iEventTally);
void updateSASGameSummaryPlayerTurnState(PlayerTypes ePlayer);
void logSASGameSummaryTechAcquired(TechTypes eType, TeamTypes eTeam, PlayerTypes ePlayer);
void logSASGameSummaryCityBuilt(CvCity const* pCity);
void logSASGameSummaryCityRazed(CvCity const* pCity, PlayerTypes ePlayer);
void logSASGameSummaryCityAcquired(PlayerTypes eOldOwner, PlayerTypes eNewOwner, CvCity const* pCity, bool bConquest, bool bTrade);
void logSASGameSummaryChangeWar(bool bWar, TeamTypes eTeam, TeamTypes eOtherTeam);
void logSASGameSummaryTeamMet(TeamTypes eTeam, TeamTypes eOtherTeam, bool bNewDiplo, int iX1, int iY1, int iX2, int iY2, CvPlot const* pTeamContactPlot, CvPlot const* pOtherContactPlot);
void logSASGameSummaryPlayerGoldTrade(PlayerTypes eFromPlayer, PlayerTypes eToPlayer, int iAmount);
void logSASGameSummaryReligionFounded(ReligionTypes eReligion, PlayerTypes ePlayer);
void logSASGameSummaryCorporationFounded(CorporationTypes eCorporation, PlayerTypes ePlayer);
void logSASGameSummaryGoldenAge(PlayerTypes ePlayer, bool bStart);
void logSASGameSummaryGoldenAgeTurnsChanged(PlayerTypes ePlayer, int iChange, int iOldGoldenAgeTurns, int iNewGoldenAgeTurns);
void logSASGameSummaryAnarchy(PlayerTypes ePlayer, bool bStart);
void logSASGameSummaryBuildingBuilt(CvCity const* pCity, BuildingTypes eBuilding);
void logSASGameSummaryProjectBuilt(CvCity const* pCity, ProjectTypes eProject);
// <!-- custom: Added the victory type so SASGameSummary can distinguish an actual spaceship launch from ordinary project completion and record its countdown. (GPT-5.6-Sol) -->
void logSASGameSummaryVictoryLaunched(PlayerTypes ePlayer, VictoryTypes eVictory);
void logSASGameSummaryVassalState(TeamTypes eMaster, TeamTypes eVassal, bool bVassal);
void logSASGameSummaryVictory(TeamTypes eWinner, VictoryTypes eVictory);
void logSASGameSummaryRunStatus(char const* szReason);
void logSASGameSummaryPlayerEliminated(PlayerTypes ePlayer);
void logSASGameSummaryPlayerAliveChanged(PlayerTypes ePlayer, bool bRevived);
void logSASGameSummaryAutoPlayChanged(int iOldValue, int iNewValue, bool bChangePlayerStatus);
void logSASGameSummaryGreatPersonBorn(CvUnit const* pUnit, PlayerTypes ePlayer, CvCity const* pCity);
void logSASGameSummaryGreatPersonJoined(CvUnit const* pUnit, CvCity const* pCity, SpecialistTypes eSpecialist);
void logSASGameSummaryGreatPersonConstructed(CvUnit const* pUnit, CvCity const* pCity, BuildingTypes eBuilding);
void logSASGameSummaryGreatPersonDiscovered(CvUnit const* pUnit, TechTypes eTech, int iResearch);
void logSASGameSummaryGreatPersonHurried(CvUnit const* pUnit, CvCity const* pCity, BuildingTypes eBuilding, int iProduction);
void logSASGameSummaryGreatPersonTradeMission(CvUnit const* pUnit, CvCity const* pCity, int iGold);
void logSASGameSummaryGreatPersonGreatWork(CvUnit const* pUnit, CvCity const* pCity, int iCulture);
void logSASGameSummaryGreatPersonInfiltrated(CvUnit const* pUnit, CvCity const* pCity, int iEspionage);
void logSASGameSummaryGreatPersonGoldenAgeConsumed(CvUnit const* pUnit);
void logSASGameSummaryGreatPersonDied(CvUnit const* pUnit, PlayerTypes eResponsiblePlayer, char const* szCause);
void logSASGameSummaryEspionageMission(CvUnit const* pUnit, EspionageMissionTypes eMission, PlayerTypes eTargetPlayer, CvPlot const* pPlot, int iExtraData, int iCost, int iEPBefore, int iEPAfter, ImprovementTypes eTargetImprovement, RouteTypes eTargetRoute, UnitTypes eTargetUnit, int iEffectValue, char const* szEffectKind);
void logSASGameSummarySpyIntercepted(CvUnit const* pUnit, PlayerTypes eTargetPlayer, char const* szPhase, int iModifier, int iInterceptChanceX100);
void logSASGameSummaryGreatGeneralAttached(CvUnit const* pGreatGeneral, CvUnit const* pTargetUnit, PromotionTypes ePromotion);
void logSASGameSummaryUnitScrapped(CvUnit const* pUnit);
void logSASGameSummaryUnitUpgraded(CvUnit const* pOldUnit, CvUnit const* pNewUnit, int iCost);
void logSASGameSummaryUnitCaptured(PlayerTypes eOldOwner, UnitTypes eOldUnitType, CvUnit const* pNewUnit);
void logSASGameSummaryCombatResult(CvUnit const* pWinner, CvUnit const* pLoser);
void logSASGameSummaryBonusChanged(CvPlot const* pPlot, BonusTypes eOldBonus, BonusTypes eNewBonus);

#define gGameSummaryLogLevel getSASGameSummaryLogLevel() // <!-- custom: Structured game-state/action summary for autoplay comparison and external review, independent from the classic BBAI master switch. (ChatGPT-5.5 + GPT-5.5) -->
#define gGameSummaryTurnInterval getSASGameSummaryTurnInterval() // <!-- custom: Periodic game-summary snapshot interval in game turns. (ChatGPT-5.5) -->

void logSASGameSummary(TCHAR* format, ... );

#endif

#pragma once

#ifndef SAS_GAME_RECORD_LOG_H
#define SAS_GAME_RECORD_LOG_H

// <!-- custom: Structured game-record rows for autoplay comparison, game analysis, user-assistance summaries, and external LLM review. This is not a classic BBAI diagnostic category: it has its own XML defines, its own SASGameRecord_*.log files, and its own lightweight public header. Call sites should still gate before invoking helpers so disabled logging does not compute logging-only arguments. Pointer-only hooks use forward declarations here to avoid pulling city/unit headers into ordinary game files. (ChatGPT-5.5 + GPT-5.5) -->
bool isSASGameRecordLogEnabled();
int getSASGameRecordLogLevel();
int getSASGameRecordTurnInterval();
void startSASGameRecordLogForNewGame();
void logSASGameRecordNewGameStarted();
void startSASGameRecordLogForLoadedSave();

class CvCity;
class CvPlot;
class CvUnit;
// <!-- custom: Capture a plot before a logical action so one combined record can describe terrain, feature, resource, improvement, route and permanent event-yield changes.
// The default constructor initializes safe NO_* enum and zero yield values without map lookups, letting caller-gated hooks avoid capture work when game-record logging is disabled. (GPT-5.6-Sol) -->
struct SASGameRecordPlotState
{
	SASGameRecordPlotState();
	explicit SASGameRecordPlotState(CvPlot const& kPlot);
	TerrainTypes eTerrain;
	FeatureTypes eFeature;
	BonusTypes eBonus;
	ImprovementTypes eImprovement;
	RouteTypes eRoute;
	int aiExtraYield[NUM_YIELD_TYPES];
};
void logSASGameRecordTurn(int iGameTurn);
// <!-- custom: Plot changes and permanent team map revelation are buffered into compact coordinate lists and flushed once per turn; detailed before/after rows are reserved for non-routine causes. The environment hook receives values already computed by CvGame::doGlobalWarming so it adds no map scan. (GPT-5.6-Sol) -->
void flushSASGameRecordTurnChanges(int iGameTurn);
void recordSASGameRecordPlotChange(CvPlot const& kPlot, SASGameRecordPlotState const& kOldState, char const* szCategory, char const* szCause, bool bDetailed);
// <!-- custom: Directional river edits are rare and independent from ordinary plot-state actions, so record them separately instead of adding unused river fields to every detailed plot-change row. Callers gate this helper before computing logging-only arguments. (GPT-5.6-Sol) -->
void logSASGameRecordRiverEdgeChanged(CvPlot const& kPlot, bool bOldSouthBoundary, bool bOldEastBoundary);
void recordSASGameRecordPlotRevealed(CvPlot const& kPlot, TeamTypes eTeam);
// <!-- custom: Map-visible technologies reveal every plot through thousands of ordinary setRevealed calls. Bracket that bulk operation so the record writes one exact full-map row instead of redundant coordinate chunks. (GPT-5.6-Sol) -->
void beginSASGameRecordFullMapRevelation(TeamTypes eTeam, TechTypes eTech);
void endSASGameRecordFullMapRevelation(TeamTypes eTeam, TechTypes eTech);
void logSASGameRecordEnvironmentTurn(int iPollution, int iSustainabilityThreshold, int iLandDefense, int iIndexBefore, int iIndexBeforeRestoration, int iIndexEnd, int iWarmingChances, int iEventTally);
void updateSASGameRecordPlayerTurnState(PlayerTypes ePlayer);
// <!-- custom: Fog-spawn call sites pass the explicit Barbarian-unit source; ordinary city production continues through logSASGameRecordUnitCompleted. (GPT-5.6-Sol) -->
void logSASGameRecordBarbarianSpawn(CvUnit const* pUnit, char const* szCause);
void logSASGameRecordUnitCompleted(CvCity const* pCity, CvUnit const* pUnit, bool bConscripted);
// <!-- custom: Added eCause so the existing TECH_ACQUIRED action can name its explicit source. (GPT-5.6-Sol + GPT-5.6 Thinking) -->
void logSASGameRecordTechAcquired(TechTypes eType, TeamTypes eTeam, PlayerTypes ePlayer, TechAcquisitionCause eCause);
void logSASGameRecordCityBuilt(CvCity const* pCity);
void logSASGameRecordCityRazed(CvCity const* pCity, PlayerTypes ePlayer);
void logSASGameRecordCityAcquired(PlayerTypes eOldOwner, PlayerTypes eNewOwner, CvCity const* pCity, bool bConquest, bool bTrade);
void logSASGameRecordWarStarted(TeamTypes eDeclarer, TeamTypes eTarget, WarPlanTypes eWarPlan, bool bPrimaryDoW, bool bNewDiplo, PlayerTypes eSponsor, bool bRandomEvent, WarDeclarationCause eCause);
// <!-- custom: Added the pre-reset war-success and peace-context parameters so synthetic war summaries retain the final result before Base AdvCiv's AI_postMakePeace clears it. (GPT-5.6-Sol) -->
void logSASGameRecordWarEnded(TeamTypes eTeam, TeamTypes eOtherTeam, int iTeamAWarSuccess, int iTeamBWarSuccess, bool bCapitulate, TeamTypes eBroker, bool bRandomEvent, bool bReparations);
void logSASGameRecordTeamMet(TeamTypes eTeam, TeamTypes eOtherTeam, bool bNewDiplo, int iX1, int iY1, int iX2, int iY2, CvPlot const* pTeamContactPlot, CvPlot const* pOtherContactPlot);
void logSASGameRecordPlayerGoldTrade(PlayerTypes eFromPlayer, PlayerTypes eToPlayer, int iAmount);
void logSASGameRecordReligionFounded(ReligionTypes eReligion, PlayerTypes ePlayer);
void logSASGameRecordCorporationFounded(CorporationTypes eCorporation, PlayerTypes ePlayer);
void logSASGameRecordGoldenAge(PlayerTypes ePlayer, bool bStart);
void logSASGameRecordGoldenAgeTurnsChanged(PlayerTypes ePlayer, int iChange, int iOldGoldenAgeTurns, int iNewGoldenAgeTurns);
void logSASGameRecordAnarchy(PlayerTypes ePlayer, bool bStart);
void logSASGameRecordCivicChanged(PlayerTypes ePlayer, CivicOptionTypes eCivicOption, CivicTypes eOldCivic, CivicTypes eNewCivic, ReligionTypes eOldEffectiveStateReligion, ReligionTypes eNewEffectiveStateReligion);
void logSASGameRecordLastStateReligionChanged(PlayerTypes ePlayer, ReligionTypes eOldReligion, ReligionTypes eNewReligion);
void logSASGameRecordBuildingCompletedByProduction(CvCity const* pCity, BuildingTypes eBuilding);
void logSASGameRecordBuildingBuilt(CvCity const* pCity, BuildingTypes eBuilding);
void logSASGameRecordProjectBuilt(CvCity const* pCity, ProjectTypes eProject);
// <!-- custom: City snapshots already expose stored overflow. These action hooks preserve the transient completion result: newly kept overflow, production lost to the cap, overflow gold, and wonder/project fail gold. (GPT-5.6-Sol) -->
void logSASGameRecordProductionOverflow(CvCity const* pCity, int iRawModifiedOverflow, int iUnmodifiedOverflow, int iKeptOverflow, int iLostProduction, int iUnusedCapacity, int iGold);
void logSASGameRecordProductionFailed(CvCity const* pCity, int iOrderData, bool bProject, int iInvestedProduction, int iGold);
// <!-- custom: Added the victory type so SASGameRecord can distinguish an actual spaceship launch from ordinary project completion and record its countdown. (GPT-5.6-Sol) -->
void logSASGameRecordVictoryLaunched(PlayerTypes ePlayer, VictoryTypes eVictory);
// <!-- custom: Capital loss and a failed arrival roll both call resetVictoryProgress, which otherwise silently erases the active countdown and spaceship projects. These hooks preserve the distinct cause and exact pre-reset state. (GPT-5.6-Sol) -->
void logSASGameRecordVictoryProgressResetForCapital(CvCity const* pCapital);
void logSASGameRecordSpaceshipFailed(TeamTypes eTeam, VictoryTypes eVictory, int iLaunchSuccessPercent);
void logSASGameRecordVassalState(TeamTypes eMaster, TeamTypes eVassal, bool bVassal);
void logSASGameRecordVictory(TeamTypes eWinner, VictoryTypes eVictory);
void logSASGameRecordRunStatus(char const* szReason);
void logSASGameRecordPlayerEliminated(PlayerTypes ePlayer);
void logSASGameRecordPlayerAliveChanged(PlayerTypes ePlayer, bool bRevived);
// <!-- custom: Added eEndCause for explicit completion attribution; active-player changes update per-request and per-log-session control-transfer counts. Callers remain logging-gated. See KI#203. (GPT-5.6-Sol) -->
void logSASGameRecordAutoPlayChanged(int iOldValue, int iNewValue, bool bChangePlayerStatus, SASAutoPlayEndCause eEndCause);
void logSASGameRecordActivePlayerChanged(PlayerTypes eOldPlayer, PlayerTypes eNewPlayer);
void logSASGameRecordAutoPlayPopupDismissed(char const* szPopupKind);
void logSASGameRecordGreatPersonBorn(CvUnit const* pUnit, PlayerTypes ePlayer, CvCity const* pCity);
void logSASGameRecordGreatPersonJoined(CvUnit const* pUnit, CvCity const* pCity, SpecialistTypes eSpecialist);
void logSASGameRecordGreatPersonConstructed(CvUnit const* pUnit, CvCity const* pCity, BuildingTypes eBuilding);
void logSASGameRecordGreatPersonDiscovered(CvUnit const* pUnit, TechTypes eTech, int iResearch);
void logSASGameRecordGreatPersonHurried(CvUnit const* pUnit, CvCity const* pCity, BuildingTypes eBuilding, int iProduction);
void logSASGameRecordGreatPersonTradeMission(CvUnit const* pUnit, CvCity const* pCity, int iGold);
void logSASGameRecordGreatPersonGreatWork(CvUnit const* pUnit, CvCity const* pCity, int iCulture);
void logSASGameRecordGreatPersonInfiltrated(CvUnit const* pUnit, CvCity const* pCity, int iEspionage);
void logSASGameRecordGreatPersonGoldenAgeConsumed(CvUnit const* pUnit);
void logSASGameRecordGreatPersonDied(CvUnit const* pUnit, PlayerTypes eResponsiblePlayer, char const* szCause);
void logSASGameRecordEspionageMission(CvUnit const* pUnit, EspionageMissionTypes eMission, PlayerTypes eTargetPlayer, CvPlot const* pPlot, int iExtraData, int iCost, int iEPBefore, int iEPAfter, ImprovementTypes eTargetImprovement, RouteTypes eTargetRoute, UnitTypes eTargetUnit, int iEffectValue, char const* szEffectKind);
void logSASGameRecordSpyIntercepted(CvUnit const* pUnit, PlayerTypes eTargetPlayer, char const* szPhase, int iModifier, int iInterceptChanceX100);
void logSASGameRecordGreatGeneralAttached(CvUnit const* pGreatGeneral, CvUnit const* pTargetUnit, PromotionTypes ePromotion);
void logSASGameRecordUnitScrapped(CvUnit const* pUnit);
void logSASGameRecordUnitUpgraded(CvUnit const* pOldUnit, CvUnit const* pNewUnit, int iCost);
void logSASGameRecordUnitCaptured(PlayerTypes eOldOwner, UnitTypes eOldUnitType, CvUnit const* pNewUnit);
void logSASGameRecordWarPlanChanged(TeamTypes eTeam, TeamTypes eTarget, WarPlanTypes eOldWarPlan, WarPlanTypes eNewWarPlan, bool bWar, int iOldStateCounter);
// <!-- custom: Level-3 tactical rows complement periodic city defense and unit-composition snapshots: synthesize consecutive siege/naval/air city bombardment into compact sequences while recording actual air strikes, interception combat, and air bombing of plot structures, so external analysis can distinguish merely owning those units from using them effectively. (GPT-5.6 Thinking) -->
void logSASGameRecordCityBombard(CvUnit const* pUnit, CvCity const* pCity, char const* szMode, int iBombardRate, bool bIgnoreBuildingDefense, int iDefenseModifierBefore, int iDefenseDamageBefore);
void logSASGameRecordAirStrike(CvUnit const* pUnit, CvUnit const* pDefender, int iDefenderDamageBefore, int iDefenderDamageAfter);
void logSASGameRecordAirInterception(CvUnit const* pAttacker, CvUnit const* pInterceptor, CvPlot const* pTargetPlot, int iAttackerDamageTaken, int iInterceptorDamageTaken);
void logSASGameRecordAirBombPlot(CvUnit const* pUnit, CvPlot const* pTargetPlot, char const* szTargetKind, char const* szTarget, bool bSuccess);
void logSASGameRecordCombatResult(CvUnit const* pWinner, CvUnit const* pLoser);
void logSASGameRecordBonusChanged(CvPlot const* pPlot, BonusTypes eOldBonus, BonusTypes eNewBonus);

#define gGameRecordLogLevel getSASGameRecordLogLevel() // <!-- custom: Structured game-state/action record for autoplay comparison and external review, independent from the classic BBAI master switch. (ChatGPT-5.5 + GPT-5.5) -->
#define gGameRecordTurnInterval getSASGameRecordTurnInterval() // <!-- custom: Periodic game-record snapshot interval in game turns. (ChatGPT-5.5) -->

void logSASGameRecord(TCHAR* format, ... );

#endif

#pragma once

#ifndef BBAI_LOG_H
#define BBAI_LOG_H

// AI decision making logging

// Log levels:
// 0 - None
// 1 - Important decisions only
// 2 - Many decisions
// 3 - All logging
// <!-- custom: Base AdvCiv required recompiling the DLL to toggle BBAI logging through LOG_AI / LOG_FOUND_VALUE.
// AdvCiv-SAS exposes the existing log levels through cached XML defines instead, keeping the existing g*LogLevel call-site checks
// while allowing users/modders to enable logs without a special logging DLL. Values are clamped in BBAILog.cpp. (GPT-5.5?) -->
bool isSASBBAILogEnabled();
bool isSASBBAILogMasterEnabled();
int getSASBBAIPlayerLogLevel();
int getSASBBAITeamLogLevel();
int getSASBBAICityLogLevel();
int getSASBBAICitizenLogLevel();
int getSASBBAIUnitLogLevel();
int getSASBBAISettlerLogLevel();
int getSASBBAIEvacuationLogLevel();
int getSASBBAIWorkerLogLevel();
int getSASBBAIWorkerSeaLogLevel();
int getSASBBAIMapLogLevel();
int getSASBBAIFoundLogLevel();
int getSASBBAIDealCancelLogLevel();
int getSASBBAICultureLogLevel();
int getSASGameSummaryLogLevel();
int getSASGameSummaryTurnInterval();
int getSASBBAIScoreLogInterval();
void startSASBBAILogForNewGame(); // <!-- custom: Roll to a new BBAI file before new-game map generation can log. (GPT-5.5) -->
void logSASBBAINewGameStarted(); // <!-- custom: Log complete new-game identification after map and player initialization. (GPT-5.5) -->
void startSASBBAILogForLoadedSave(); // <!-- custom: Roll and identify a loaded save after its complete game state is read. (GPT-5.5) -->

// <!-- custom: Structured game-summary rows for autoplay comparison, game analysis, and external LLM review. This report is independent from the classic BBAI master switch, but still reuses the BBAI file backend for now. Call sites should gate before invoking these helpers so disabled logging does not compute logging-only arguments, matching the usual BBAI call-site guard pattern; pointer-only hooks use forward declarations here to avoid pulling city/unit headers into BBAILog.h. (ChatGPT-5.5 + GPT-5.5) -->
class CvCity;
class CvPlot;
class CvUnit;
void logSASBBAIGameSummaryTurn(int iGameTurn);
void updateSASBBAIGameSummaryPlayerTurnState(PlayerTypes ePlayer);
void logSASBBAIGameSummaryTechAcquired(TechTypes eType, TeamTypes eTeam, PlayerTypes ePlayer);
void logSASBBAIGameSummaryCityBuilt(CvCity const* pCity);
void logSASBBAIGameSummaryCityRazed(CvCity const* pCity, PlayerTypes ePlayer);
void logSASBBAIGameSummaryCityAcquired(PlayerTypes eOldOwner, PlayerTypes eNewOwner, CvCity const* pCity, bool bConquest, bool bTrade);
void logSASBBAIGameSummaryChangeWar(bool bWar, TeamTypes eTeam, TeamTypes eOtherTeam);
void logSASBBAIGameSummaryTeamMet(TeamTypes eTeam, TeamTypes eOtherTeam, bool bNewDiplo, int iX1, int iY1, int iX2, int iY2, CvPlot const* pTeamContactPlot, CvPlot const* pOtherContactPlot);
void logSASBBAIGameSummaryPlayerGoldTrade(PlayerTypes eFromPlayer, PlayerTypes eToPlayer, int iAmount);
void logSASBBAIGameSummaryReligionFounded(ReligionTypes eReligion, PlayerTypes ePlayer);
void logSASBBAIGameSummaryCorporationFounded(CorporationTypes eCorporation, PlayerTypes ePlayer);
void logSASBBAIGameSummaryGoldenAge(PlayerTypes ePlayer, bool bStart);
void logSASBBAIGameSummaryGoldenAgeTurnsChanged(PlayerTypes ePlayer, int iChange, int iOldGoldenAgeTurns, int iNewGoldenAgeTurns);
void logSASBBAIGameSummaryAnarchy(PlayerTypes ePlayer, bool bStart);
void logSASBBAIGameSummaryBuildingBuilt(CvCity const* pCity, BuildingTypes eBuilding);
void logSASBBAIGameSummaryProjectBuilt(CvCity const* pCity, ProjectTypes eProject);
void logSASBBAIGameSummaryVassalState(TeamTypes eMaster, TeamTypes eVassal, bool bVassal);
void logSASBBAIGameSummaryVictory(TeamTypes eWinner, VictoryTypes eVictory);
void logSASBBAIGameSummaryGreatPersonBorn(CvUnit const* pUnit, PlayerTypes ePlayer, CvCity const* pCity);
void logSASBBAIGameSummaryGreatPersonJoined(CvUnit const* pUnit, CvCity const* pCity, SpecialistTypes eSpecialist);
void logSASBBAIGameSummaryGreatGeneralAttached(CvUnit const* pGreatGeneral, CvUnit const* pTargetUnit, PromotionTypes ePromotion);
void logSASBBAIGameSummaryUnitScrapped(CvUnit const* pUnit);
void logSASBBAIGameSummaryUnitUpgraded(CvUnit const* pOldUnit, CvUnit const* pNewUnit, int iCost);
void logSASBBAIGameSummaryCombatResult(CvUnit const* pWinner, CvUnit const* pLoser);

#define gLogBBAI isSASBBAILogEnabled() // advc.007: So that BBAI logging can be checked in FAssert
#define gPlayerLogLevel getSASBBAIPlayerLogLevel()
#define gScoreLogInterval getSASBBAIScoreLogInterval() // advc.007: was hardcoded to 25 in CvPlayer::onTurnLogging
#define gTeamLogLevel getSASBBAITeamLogLevel()
#define gCityLogLevel getSASBBAICityLogLevel()
#define gCitizenLogLevel getSASBBAICitizenLogLevel() // <!-- custom: Separate citizen-assignment and plot-allocation diagnostics from general CITY logging. (GPT-5.5) -->
#define gUnitLogLevel getSASBBAIUnitLogLevel()
#define gSettlerLogLevel getSASBBAISettlerLogLevel() // <!-- custom: Separate Settler diagnostics from general UNIT logging so each can be inspected independently. (GPT-5.5) -->
#define gEvacuationLogLevel getSASBBAIEvacuationLogLevel() // <!-- custom: Separate evacuation/retreat diagnostics from general CITY and UNIT logging. (GPT-5.5) -->
#define gWorkerLogLevel getSASBBAIWorkerLogLevel() // <!-- custom: Separate land-Worker diagnostics from general UNIT logging. (ChatGPT-5.5 + GPT-5.5 review) -->
#define gWorkerSeaLogLevel getSASBBAIWorkerSeaLogLevel() // <!-- custom: Separate Work Boat / WORKER_SEA diagnostics from general UNIT and land-Worker logging. (ChatGPT-5.5 + GPT-5.5 review) -->
#define gMapLogLevel getSASBBAIMapLogLevel() // K-Mod
#define gFoundLogLevel getSASBBAIFoundLogLevel() // advc.031c
#define gDealCancelLogLevel getSASBBAIDealCancelLogLevel() // advc.133
#define gCultureLogLevel getSASBBAICultureLogLevel() // <!-- custom: Separate culture-victory diagnostics from general PLAYER and CITY logging. (ChatGPT-5.5) -->
#define gGameSummaryLogLevel getSASGameSummaryLogLevel() // <!-- custom: Structured game-state/action summary for autoplay comparison and external review, independent from the classic BBAI master switch. (ChatGPT-5.5 + GPT-5.5) -->
#define gGameSummaryTurnInterval getSASGameSummaryTurnInterval() // <!-- custom: Periodic game-summary snapshot interval in game turns. (ChatGPT-5.5) -->

void logBBAI(TCHAR* format, ... );
// <advc.133>
class CvDeal;
void logBBAICancel(CvDeal const& d, PlayerTypes eCancelPlayer, wchar const* szReason);
// </advc.133>

#endif  //BBAI_LOG_H

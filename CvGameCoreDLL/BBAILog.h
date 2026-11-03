#pragma once

#ifndef BBAI_LOG_H
#define BBAI_LOG_H

// AI decision making logging

// <!-- custom: Scope: BBAI settings, the shared writer and session rows, plus row formatters that several files share (e.g. the first-city probe helpers).
// A formatter used by one file stays static beside its caller, which owns the decision and gate; unlike the SGR recorder, which owns all of its compact rows, BBAI rows are detailed decision traces that live with their decisions. (Claude code Opus 5.5) -->
// Log levels:
// 0 - None
// 1 - Important decisions only
// 2 - Many decisions
// 3 - All logging
// <!-- custom: Base AdvCiv required recompiling the DLL to toggle BBAI logging through LOG_AI / LOG_FOUND_VALUE.
// AdvCiv-SAS exposes the existing log levels through XML defines instead and caches their effective values once after all GlobalDefines/module overrides load.
// Keep the widespread g*LogLevel hot gates as direct reads; call sites should still gate before evaluating logging-only arguments because logBBAI cannot undo argument work already performed by its caller. (GPT-5.5? + ChatGPT-5.6-Sol) -->
struct SASBBAILogSettings
{
	// <!-- custom: This remains the one cached "any BBAI diagnostics active" bit.
	// UWAI categories are ordinary BBAI categories now that their separate report sink is gone. (ChatGPT-5.6-Sol) -->
	bool bEnabled;
	bool bMasterEnabled;
	int iPlayerLogLevel;
	int iTeamLogLevel;
	int iWarLogLevel;
	int iCityLogLevel;
	int iProductionNoTargetLogLevel;
	int iMilitaryProductionLogLevel;
	int iSpaceProductionLogLevel;
	int iLimitedProjectProductionLogLevel;
	int iBuildingProductionLogLevel;
	int iCitizenLogLevel;
	int iUnitLogLevel;
	int iOverseasTransportLogLevel;
	int iGreatGeneralLogLevel;
	int iSettlerFirstCityLogLevel;
	int iSettler2PlusLogLevel;
	int iFoundFirstCityLogLevel;
	int iFound2PlusLogLevel;
	int iEvacuationLogLevel;
	int iWorkerLogLevel;
	int iWorkerSeaLogLevel;
	int iMapLogLevel;
	int iDealCancelLogLevel;
	int iBonusLogLevel;
	int iCultureLogLevel;
	// <!-- custom: UWAI diagnostics use the same cached BBAI category model and physical log sink as the rest of SAS. See KI#505.3. (ChatGPT-5.6-Sol) -->
	int iUWAIAgentLogLevel;
	int iUWAIMilitaryAnalystLogLevel;
	int iUWAIInvasionGraphLogLevel;
	int iUWAIArmamentForecastLogLevel;
	int iUWAIWarUtilityLogLevel;
};
extern SASBBAILogSettings gSASBBAILogSettings;
void cacheSASBBAILogSettings();
__forceinline bool isSASBBAILogEnabled() { return gSASBBAILogSettings.bEnabled; }
__forceinline bool isSASBBAILogMasterEnabled() { return gSASBBAILogSettings.bMasterEnabled; }
int getSASBBAIScoreLogInterval();
// <!-- custom: Shared first-use cache for the later-city diagnostic switch; the helper self-gates on FOUND_2PL level 2, and site eligibility remains the evaluator's responsibility. See KI#144.4. (GPT-6.1-Sol) -->
bool isSASBBAILaterCityFoodSupportAuditEnabled();
// <!-- custom: Move WarEvaluator's existing cached diagnostic threshold here so BBAI and SASGameRecord share its reader and armed-state policy; callers must gate WAR level 3 first. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
int getSASBBAIHighWarUtilityLogThreshold();
// <!-- custom: Expose one compact session-start diagnostic profile to SASGameRecord without duplicating BBAI's iterable category registry.
// Configured category levels remain visible even when the master switch makes their effective levels zero; supporting options share their readers and formatter with BBAI.
// Callers must gate before constructing this profile. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
CvString getSASBBAILogProfileFields();
void startSASBBAILogForNewGame(); // <!-- custom: Roll to a new timestamped BBAI diagnostic file before new-game map generation can log. (GPT-5.5 + GPT-5.5) -->
void logSASBBAINewGameStarted(); // <!-- custom: Log complete new-game identification after map and player initialization. (GPT-5.5) -->
void startSASBBAILogForLoadedSave(); // <!-- custom: Roll and identify a loaded save after its complete game state is read. (GPT-5.5) -->
int getSASBBAILogSessionSequence(); // <!-- custom: Let high-volume diagnostic categories discard change-dedup state whenever a new/load BBAI session begins. (GPT-5.6-Sol) -->
// <!-- custom: Kept here rather than as CvUnitAI.cpp statics: CvUnit.cpp and CvUnitAI.cpp both report probe outcomes, and outstanding snapshots are discarded with the BBAI session sequence. (Claude code Opus 5.5) -->
// <!-- custom: Diagnostic-only committed hope-probe snapshots and next-observation revaluations; callers must gate SETTLER_1ST at level 3 before either call.
// No snapshot is serialized or used for gameplay, and new/load BBAI sessions discard outstanding snapshots. See KI#144.6. (GPT-6.1-Sol) -->
class CvUnit;
class CvPlot;
void logBBAIFirstCityProbeStart(CvUnit const& kSettler, CvPlot const& kTarget, CvPlot const& kFallback, CvPlot const& kWaypoint, int iTargetValue, int iFallbackValue, int iNetHopeValue, int iDelayCost);
void logBBAIFirstCityProbeOutcome(CvUnit const& kSettler);
// <!-- custom: Caller must gate SETTLER_1ST at level 3 and provide a current successful path to kTarget before another search replaces it; records existing node data only. See KI#144.6. (GPT-6.1-Sol) -->
void logBBAIFirstCityScoutRoute(CvUnit const& kSettler, CvPlot const& kTarget, char const* szPhase);
// <!-- custom: gLogBBAI remains a startup-cached direct read and now includes enabled UWAI categories because they use the same BBAI sink instead of a parallel logger. (ChatGPT-5.6-Sol) -->
#define gLogBBAI (gSASBBAILogSettings.bEnabled) // advc.007: So that BBAI logging can be checked in FAssert;
#define gPlayerLogLevel (gSASBBAILogSettings.iPlayerLogLevel)
#define gScoreLogInterval getSASBBAIScoreLogInterval() // advc.007: was hardcoded to 25 in CvPlayer::onTurnLogging; only reached when PLAYER logging is enabled.
#define gTeamLogLevel (gSASBBAILogSettings.iTeamLogLevel)
#define gWarLogLevel (gSASBBAILogSettings.iWarLogLevel) // <!-- custom: Separate war-plan and war-target diagnostics from broad TEAM logging. (GPT-5.5) -->
#define gCityLogLevel (gSASBBAILogSettings.iCityLogLevel)
#define gProductionNoTargetLogLevel (gSASBBAILogSettings.iProductionNoTargetLogLevel) // <!-- custom: Dedicated all-city no-production boundary and AI chooser-path diagnostics without broad CITY or military-production logging. See KI#51. (GPT-5.6-Sol) -->
#define gMilitaryProductionLogLevel (gSASBBAILogSettings.iMilitaryProductionLogLevel) // <!-- custom: Dedicated AI city military-production diagnostics without enabling broad CITY logging. (ChatGPT-5.6-Sol) -->
#define gSpaceProductionLogLevel (gSASBBAILogSettings.iSpaceProductionLogLevel) // <!-- custom: Dedicated spaceship-project valuation, selection, and production-switch diagnostics without broad PLAYER/CITY logging. (ChatGPT-5.6-Sol) -->
#define gLimitedProjectProductionLogLevel (gSASBBAILogSettings.iLimitedProjectProductionLogLevel) // <!-- custom: Dedicated one-copy non-spaceship Project continuity/selection diagnostics without broad PLAYER/CITY logging. (ChatGPT-5.6-Sol) -->
#define gBuildingProductionLogLevel (gSASBBAILogSettings.iBuildingProductionLogLevel) // <!-- custom: Dedicated building-vs-unit production diagnostics without broad CITY or military-production logging. (ChatGPT-5.6-Sol) -->
#define gCitizenLogLevel (gSASBBAILogSettings.iCitizenLogLevel) // <!-- custom: Separate citizen-assignment and plot-allocation diagnostics from general CITY logging. (GPT-5.5) -->
#define gUnitLogLevel (gSASBBAILogSettings.iUnitLogLevel)
#define gOverseasTransportLogLevel (gSASBBAILogSettings.iOverseasTransportLogLevel) // <!-- custom: Separate overseas military-cargo and Settler-transport diagnostics from broad CITY and UNIT logging. (GPT-5.6-Sol) -->
#define gGreatGeneralLogLevel (gSASBBAILogSettings.iGreatGeneralLogLevel) // <!-- custom: Separate Great General action, Military Instructor, and Warlord attachment diagnostics from general UNIT logging. (GPT-5.5) -->
// <!-- custom: Opening-specific code gates on 1ST and expansion-specific code on 2PL directly, without player history; each is a startup-cached read.
// Shared paths first had their own COMMON category, but it held most later-city rows, leaving 2PL nearly empty; getting them needed COMMON, which also logged the whole opening.
// So shared paths route to 1ST or 2PL by phase instead (helpers below). See KI#144.6. (GPT-6.1-Sol + Claude code Opus 5.5) -->
#define gSettlerFirstCityLogLevel (gSASBBAILogSettings.iSettlerFirstCityLogLevel) // <!-- custom: First-capital Settler scouting, movement and founding diagnostics. See KI#144.6. (GPT-5.5 + ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
#define gSettler2PlusLogLevel (gSASBBAILogSettings.iSettler2PlusLogLevel) // <!-- custom: Settler diagnostics for the second city and later expansion. See KI#144.6. (ChatGPT-5.6-Sol) -->
#define gFoundFirstCityLogLevel (gSASBBAILogSettings.iFoundFirstCityLogLevel) // <!-- custom: Split inherited advc.031c Found diagnostics: first-capital-specific scoring branches; shared components route by phase through getSASBBAIFoundLogLevel. See KI#144.6. (ChatGPT-5.6-Sol) -->
#define gFound2PlusLogLevel (gSASBBAILogSettings.iFound2PlusLogLevel) // <!-- custom: Later-city-specific Found scoring branches. See KI#144.6. (ChatGPT-5.6-Sol) -->
#define gEvacuationLogLevel (gSASBBAILogSettings.iEvacuationLogLevel) // <!-- custom: Separate evacuation/retreat diagnostics from general CITY and UNIT logging. (GPT-5.5) -->
#define gWorkerLogLevel (gSASBBAILogSettings.iWorkerLogLevel) // <!-- custom: Separate land-Worker diagnostics from general UNIT logging. (ChatGPT-5.5 + GPT-5.5 review) -->
#define gWorkerSeaLogLevel (gSASBBAILogSettings.iWorkerSeaLogLevel) // <!-- custom: Separate Work Boat / WORKER_SEA diagnostics from general UNIT and land-Worker logging. (ChatGPT-5.5 + GPT-5.5 review) -->
#define gMapLogLevel (gSASBBAILogSettings.iMapLogLevel) // K-Mod
#define gDealCancelLogLevel (gSASBBAILogSettings.iDealCancelLogLevel) // advc.133
#define gBonusLogLevel (gSASBBAILogSettings.iBonusLogLevel) // <!-- custom: Shared bonus valuation, trade, and strategic-resource diagnostics independent of their Worker/Settler consumers. (GPT-5.6-Sol) -->
#define gCultureLogLevel (gSASBBAILogSettings.iCultureLogLevel) // <!-- custom: Separate culture-victory diagnostics from general PLAYER and CITY logging. (ChatGPT-5.5) -->
// <!-- custom: UWAI follows the normal cached BBAI category contract.
// Keep these as direct hot reads so callers can pre-gate diagnostic-only work before formatting, helper calls or extra simulations. (ChatGPT-5.6-Sol) -->
#define gUWAIAgentLogLevel (gSASBBAILogSettings.iUWAIAgentLogLevel)
#define gUWAIMilitaryAnalystLogLevel (gSASBBAILogSettings.iUWAIMilitaryAnalystLogLevel)
#define gUWAIInvasionGraphLogLevel (gSASBBAILogSettings.iUWAIInvasionGraphLogLevel)
#define gUWAIArmamentForecastLogLevel (gSASBBAILogSettings.iUWAIArmamentForecastLogLevel)
#define gUWAIWarUtilityLogLevel (gSASBBAILogSettings.iUWAIWarUtilityLogLevel)

// <!-- custom: 1ST while a non-Barbarian player has no city, matching the AI_foundFirstCity branch; checking both levels first keeps disabled logging off player state. See KI#144.6. (Claude code Opus 5.5) -->
bool isSASBBAIFirstCityLogPhase(PlayerTypes ePlayer);
inline int getSASBBAISettlerLogLevel(PlayerTypes ePlayer)
{
	return ((gSettlerFirstCityLogLevel > 0 || gSettler2PlusLogLevel > 0) ? (isSASBBAIFirstCityLogPhase(ePlayer) ? gSettlerFirstCityLogLevel : gSettler2PlusLogLevel) : 0);
}
inline int getSASBBAIFoundLogLevel(PlayerTypes ePlayer)
{
	return ((gFoundFirstCityLogLevel > 0 || gFound2PlusLogLevel > 0) ? (isSASBBAIFirstCityLogPhase(ePlayer) ? gFoundFirstCityLogLevel : gFound2PlusLogLevel) : 0);
}

void logBBAI(TCHAR* format, ... );
// <advc.133>
class CvDeal;
void logBBAICancel(CvDeal const& d, PlayerTypes eCancelPlayer, wchar const* szReason);
// </advc.133>

#endif  //BBAI_LOG_H

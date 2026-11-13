#include "CvGameCoreDLL.h"
#include "CyGame.h"
#include "CyDeal.h"
#include "CyReplayInfo.h"

//
// published python interface for CyGame
// advc.mnai: Corrected a couple of documentation strings

void CyGamePythonInterface()
{
	printToConsole("Python Extension Module - CyGamePythonInterface\n");

	python::class_<CyGame>("CyGame")
		.def("isNone", &CyGame::isNone, "CyGame* () - is the instance valid?")

		.def("updateScore", &CyGame::updateScore, "void (bool bForce)")
		.def("cycleCities", &CyGame::cycleCities, "void (bool bForward, bool bAdd)")
		.def("cycleSelectionGroups", &CyGame::cycleSelectionGroups, "void (bool bClear, bool bForward, bool bWorkers)")
		.def("cyclePlotUnits", &CyGame::cyclePlotUnits, "bool (CyPlot* pPlot, bool bForward, bool bAuto, int iCount)")
		// <advc.154>
		.def("getNextUnitInCycle", &CyGame::getNextUnitInCycle, python::return_value_policy<python::reference_existing_object>(),
				"CyUnit* (bool bForward, bool bWorkers)") // </advc.154>

		.def("selectionListMove", &CyGame::selectionListMove, "void (CyPlot* pPlot, bool bAlt, bool bShift, bool bCtrl)")
		.def("selectionListGameNetMessage", &CyGame::selectionListGameNetMessage, "void (int eMessage, int iData2, int iData3, int iData4, int iFlags, bool bAlt, bool bShift)")
		.def("selectedCitiesGameNetMessage", &CyGame::selectedCitiesGameNetMessage, "void (int eMessage, int iData2, int iData3, int iData4, bool bOption, bool bAlt, bool bShift, bool bCtrl)")
		.def("cityPushOrder", &CyGame::cityPushOrder, "void (CyCity* pCity, OrderTypes eOrder, int iData, bool bAlt, bool bShift, bool bCtrl)")

		.def("getSymbolID", &CyGame::getSymbolID, "int (int iSymbol)")

		.def("getProductionPerPopulation", &CyGame::getProductionPerPopulation, "int (int /*HurryTypes*/ eHurry)")

		.def("getAdjustedPopulationPercent", &CyGame::getAdjustedPopulationPercent, "int (int eVictory)")
		.def("getAdjustedLandPercent", &CyGame::getAdjustedLandPercent, "int (int eVictory)")
		// advc.178:
		.def("isDiploVictoryValid", &CyGame::isDiploVictoryValid, "bool ()")
		.def("isTeamVote", &CyGame::isTeamVote, "bool (int eVote)")
		.def("isChooseElection", &CyGame::isChooseElection, "bool (int eVote)")
		.def("isTeamVoteEligible", &CyGame::isTeamVoteEligible, "bool (int eTeam, int eVoteSource)")
		.def("countPossibleVote", &CyGame::countPossibleVote, "int (int eVote, int eVoteSource)")
		.def("getVoteRequired", &CyGame::getVoteRequired, "int (int eVote, int eVoteSource)")
		.def("getSecretaryGeneral", &CyGame::getSecretaryGeneral, "int (int eVoteSource)")
		.def("canHaveSecretaryGeneral", &CyGame::canHaveSecretaryGeneral, "bool (int eVoteSource)")
		.def("getVoteSourceReligion", &CyGame::getVoteSourceReligion, "int (int /*VoteSourceTypes*/ eVoteSource)")
		.def("setVoteSourceReligion", &CyGame::setVoteSourceReligion, "void (int /*VoteSourceTypes*/ eVoteSource, int /*ReligionTypes*/ eReligion, bool bAnnounce)")

		.def("countCivPlayersAlive", &CyGame::countCivPlayersAlive, "int ()")
		.def("countCivPlayersEverAlive", &CyGame::countCivPlayersEverAlive, "int ()")
		.def("countCivTeamsAlive", &CyGame::countCivTeamsAlive, "int ()")
		.def("countCivTeamsEverAlive", &CyGame::countCivTeamsEverAlive, "int ()")
		.def("countHumanPlayersAlive", &CyGame::countHumanPlayersAlive, "int ()")

		.def("countTotalCivPower", &CyGame::countTotalCivPower, "int ()")
		.def("countTotalNukeUnits", &CyGame::countTotalNukeUnits, "int ()")
		.def("countKnownTechNumTeams", &CyGame::countKnownTechNumTeams, "int (int eTech)")
		.def("getNumFreeBonuses", &CyGame::getNumFreeBonuses, "int (int eBonus)")

		.def("countReligionLevels", &CyGame::countReligionLevels, "int (int eReligion)")
		.def("calculateReligionPercent", &CyGame::calculateReligionPercent, "int (int eReligion)")
		.def("countCorporationLevels", &CyGame::countCorporationLevels, "int (int eCorporation)")

		.def("goldenAgeLength", &CyGame::goldenAgeLength, "int ()")
		.def("victoryDelay", &CyGame::victoryDelay, "int (int /*VictoryTypes*/ eVictory)")
		.def("getImprovementUpgradeTime", &CyGame::getImprovementUpgradeTime, "int (int /*ImprovementTypes*/ eImprovement)")
		.def("canTrainNukes", &CyGame::canTrainNukes, "bool ()")

		.def("getCurrentEra", &CyGame::getCurrentEra, "int /*EratTypes*/ ()")

		.def("getActiveTeam", &CyGame::getActiveTeam, "int () - returns ID for the group")
		.def("getActiveCivilizationType", &CyGame::getActiveCivilizationType, "int () - returns CivilizationID")
		.def("isNetworkMultiPlayer", &CyGame::isNetworkMultiPlayer, "bool () - NetworkMultiplayer()? ")
		.def("isGameMultiPlayer", &CyGame::isGameMultiPlayer, "bool () - GameMultiplayer()? ")
		.def("isTeamGame", &CyGame::isTeamGame, "bool ()")
		.def("getNumHumanPlayers", &CyGame::getNumHumanPlayers, "int () - # of human players in-game")

		.def("isModem", &CyGame::isModem, "bool () - Using a modem? ")
		.def("setModem", &CyGame::setModem, "void (bool bModem) - Use a modem! (or don't)")

		.def("reviveActivePlayer", &CyGame::reviveActivePlayer, "void ()")

		.def("getGameTurn", &CyGame::getGameTurn, "int () - current game turn")
		.def("setGameTurn", &CyGame::setGameTurn, "void (iNewValue) - set current game turn")
		.def("getTurnYear", &CyGame::getTurnYear, "int (iGameTurn) - turn Time")
		.def("getGameTurnYear", &CyGame::getGameTurnYear)
		.def("getElapsedGameTurns", &CyGame::getElapsedGameTurns, "int () - Elapsed turns thus far")
		// <!-- custom: Let BUG supply its resolved user root and expose a deliberate live-inspection flush for the shared native BBAI/SASGameRecord writer. (ChatGPT-5.6-Sol) -->
		.def("setSASDiagnosticLogRoot", &CyGame::setSASDiagnosticLogRoot)
		.def("flushSASDiagnosticLogs", &CyGame::flushSASDiagnosticLogs, "bool () - publish pending diagnostics; false indicates failed output")
		// <!-- custom: Python owns WorldBuilder screen show/hide callbacks; expose their literal visibility notification so the native recorder can distinguish screen visibility from mode and filter Advanced Start behind its cached enable gate. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
		.def("updateSASRuntimeStatusWorldBuilderScreen", &CyGame::updateSASRuntimeStatusWorldBuilderScreen, "void (bool) - report observed WorldBuilder Python screen visibility")
		// <!-- custom: The Python WorldBuilder reveal-all loop brackets its many plot setters so save history records one bulk mutation instead of thousands of duplicate per-plot entries. (ChatGPT-5.6-Sol) -->
		.def("beginSASWorldBuilderBulkEdit", &CyGame::beginSASWorldBuilderBulkEdit, "void () - suppress per-plot save history during a known WorldBuilder bulk operation")
		// <!-- custom: The matching close bridge now distinguishes no-op, completed and partially applied reveal loops using native changed-plot accounting. (ChatGPT-5.6-Sol) -->
		.def("endSASWorldBuilderBulkReveal", &CyGame::endSASWorldBuilderBulkReveal, "void (int TeamTypes, bool reveal, bool completed) - close reveal-all suppression and record actual completed/partial changes")
		// <!-- custom: Python owns menu/screen observations and PreGameStart; expose literal notifications plus the native cached gate so disabled recording skips their diagnostic-only queries. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
		.def("isSASRuntimeStatusRecordingEnabled", &CyGame::isSASRuntimeStatusRecordingEnabled, "bool () - cached runtime recording gate for Python observation callers")
		.def("updateSASRuntimeStatusMainMenuState", &CyGame::updateSASRuntimeStatusMainMenuState, "void (bool) - report an event-driven main-menu state sample")
		.def("updateSASRuntimeStatusPreGameStart", &CyGame::updateSASRuntimeStatusPreGameStart, "void () - report the EXE-driven Python PreGameStart lifecycle boundary")
		.def("updateSASRuntimeStatusCivilopedia", &CyGame::updateSASRuntimeStatusCivilopedia, "void (bool visible, bool inMainMenu) - report observed Civilopedia visibility and its menu/game context")
		// <!-- custom: Expose the post-GameStart/OnLoad diagnostic hook; Python invokes it after event dispatch and only while SASGameRecord is enabled. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
		.def("logSASGameRecordDiagnosticContext", &CyGame::logSASGameRecordDiagnosticContext, "void (int renderQualityLevel, int antiAliasingIndex, int antiAliasingSamples, int globeViewRenderLevel, int movieQualityLevel) - record finalized session diagnostic settings")
		// <!-- custom: Compact configuration baseline/change rows, native runtime-view baseline and internal alternate-INI discovery for SASGameRecord; the INI path itself is not logged. (ChatGPT-5.6-Sol) -->
		.def("logSASGameRecordSessionSettings", &CyGame::logSASGameRecordSessionSettings)
		.def("logSASGameRecordRuntimeViewStateSnapshot", &CyGame::logSASGameRecordRuntimeViewStateSnapshot)
		// <!-- custom: Narrow revision-151 UI bridges accept only controlled screen/action labels or pre-serialized scalar interface state; no arbitrary user text crosses into the recorder. (ChatGPT-5.6-Sol) -->
		.def("logSASGameRecordScreenAction", &CyGame::logSASGameRecordScreenAction)
		.def("logSASGameRecordInterfaceState", &CyGame::logSASGameRecordInterfaceState)
		// <!-- custom: Map-caption text is a separate reviewed bridge because arbitrary user-authored text is withheld by default and must not become a generic Python-to-SGR logging API. (ChatGPT-5.6-Sol) -->
		.def("logSASGameRecordMapAnnotationSummary", &CyGame::logSASGameRecordMapAnnotationSummary)
		.def("logSASGameRecordMapAnnotation", &CyGame::logSASGameRecordMapAnnotation)
		// <!-- custom: Persisted BUG DotMap planning markers use a typed scalar bridge, distinct from free-form text annotations and generic Python log strings. (ChatGPT-5.6-Sol) -->
		.def("logSASGameRecordDotMapSummary", &CyGame::logSASGameRecordDotMapSummary)
		.def("logSASGameRecordDotMapMarker", &CyGame::logSASGameRecordDotMapMarker)
		.def("getSASGameRecordIniFileArgument", &CyGame::getSASGameRecordIniFileArgument)
		// <!-- custom: Internal BUG diplomacy bridge; captures only resolved AI->human ordinary offers rejected at the UI boundary. (ChatGPT-5.6-Sol) -->
		.def("logSASGameRecordRejectedAIOffer", &CyGame::logSASGameRecordRejectedAIOffer)
		// <!-- custom: Expose only one-shot SASFastSave basename/reason context; filename construction remains in Python so the DLL cannot drift from BugPath/collision behavior. (ChatGPT-5.6-Sol) -->
		.def("setSASFastSaveContext", &CyGame::setSASFastSaveContext)
		.def("clearSASFastSaveContext", &CyGame::clearSASFastSaveContext)
		// <!-- custom: Read-only persistent source-history API for later game-version UI/replay presentation. (ChatGPT-5.6-Sol) -->
		.def("getNumSASVersionHistoryEntries", &CyGame::getNumSASVersionHistoryEntries)
		.def("getSASVersionHistoryTurn", &CyGame::getSASVersionHistoryTurn)
		.def("getSASVersionHistoryVersion", &CyGame::getSASVersionHistoryVersion)
		.def("getSASVersionHistoryCommitHash", &CyGame::getSASVersionHistoryCommitHash)
		.def("getSASVersionHistoryDirtyState", &CyGame::getSASVersionHistoryDirtyState)
		// <!-- custom: The Changes tab reads shared Advanced Start/editor history through these SASWorldChangesHistory APIs; their data-model name is independent of the tab label.
		// Expose saved fields through this read-only bridge so the advisor does not require the original SGR file. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
		.def("getNumSASWorldChangesHistoryEntries", &CyGame::getNumSASWorldChangesHistoryEntries)
		.def("getSASWorldChangesHistorySource", &CyGame::getSASWorldChangesHistorySource)
		.def("getSASWorldChangesHistorySourceName", &CyGame::getSASWorldChangesHistorySourceName)
		.def("getSASWorldChangesHistoryCategory", &CyGame::getSASWorldChangesHistoryCategory)
		.def("getSASWorldChangesHistoryCategoryName", &CyGame::getSASWorldChangesHistoryCategoryName)
		// <!-- custom: Actor/target identities retain synchronized player/team context so advisor filtering can avoid reconstructing historical ownership from current state. (ChatGPT-5.6-Sol) -->
		.def("getSASWorldChangesHistoryActor", &CyGame::getSASWorldChangesHistoryActor)
		.def("getSASWorldChangesHistoryActorTeam", &CyGame::getSASWorldChangesHistoryActorTeam)
		.def("getSASWorldChangesHistoryTargetPlayer", &CyGame::getSASWorldChangesHistoryTargetPlayer)
		.def("getSASWorldChangesHistoryTargetTeam", &CyGame::getSASWorldChangesHistoryTargetTeam)
		// <!-- custom: Historical turn/year/version context is stored with each event so later calendar or source changes cannot rewrite when that edit occurred. (ChatGPT-5.6-Sol) -->
		.def("getSASWorldChangesHistoryTurn", &CyGame::getSASWorldChangesHistoryTurn)
		.def("getSASWorldChangesHistoryYear", &CyGame::getSASWorldChangesHistoryYear)
		.def("getSASWorldChangesHistoryElapsedTurn", &CyGame::getSASWorldChangesHistoryElapsedTurn)
		.def("getSASWorldChangesHistoryVersionIndex", &CyGame::getSASWorldChangesHistoryVersionIndex)
		// <!-- custom: Coordinates and object/data IDs preserve the applied target without exposing free-form editor text. (ChatGPT-5.6-Sol) -->
		.def("getSASWorldChangesHistoryX", &CyGame::getSASWorldChangesHistoryX)
		.def("getSASWorldChangesHistoryY", &CyGame::getSASWorldChangesHistoryY)
		.def("getSASWorldChangesHistoryCityId", &CyGame::getSASWorldChangesHistoryCityId)
		.def("getSASWorldChangesHistoryObjectId", &CyGame::getSASWorldChangesHistoryObjectId)
		.def("getSASWorldChangesHistoryRequestedDataId", &CyGame::getSASWorldChangesHistoryRequestedDataId)
		.def("getSASWorldChangesHistoryResolvedDataId", &CyGame::getSASWorldChangesHistoryResolvedDataId)
		// <!-- custom: Fixed action/operation tokens and typed targets remain machine-readable; script targets may contain applied text under the save producer's XML policy, while names remain withheld. (GPT-6.1-Sol) (ChatGPT-5.6-Sol) -->
		.def("getSASWorldChangesHistoryAction", &CyGame::getSASWorldChangesHistoryAction)
		.def("getSASWorldChangesHistoryOperation", &CyGame::getSASWorldChangesHistoryOperation)
		.def("getSASWorldChangesHistoryTargetKind", &CyGame::getSASWorldChangesHistoryTargetKind)
		.def("getSASWorldChangesHistoryTarget", &CyGame::getSASWorldChangesHistoryTarget)
		.def("getSASWorldChangesHistoryOldValueValid", &CyGame::getSASWorldChangesHistoryOldValueValid)
		.def("getSASWorldChangesHistoryOldValue", &CyGame::getSASWorldChangesHistoryOldValue)
		// <!-- custom: Explicit validity/content flags distinguish absent values and withheld content from legitimate numeric sentinels. (ChatGPT-5.6-Sol) -->
		.def("getSASWorldChangesHistoryNewValueValid", &CyGame::getSASWorldChangesHistoryNewValueValid)
		.def("getSASWorldChangesHistoryNewValue", &CyGame::getSASWorldChangesHistoryNewValue)
		.def("getSASWorldChangesHistoryContentWithheld", &CyGame::getSASWorldChangesHistoryContentWithheld)
		.def("getSASWorldChangesHistoryQuotedCost", &CyGame::getSASWorldChangesHistoryQuotedCost)
		// <!-- custom: Advanced Start budget transitions share the same persisted action record while ordinary WorldBuilder events leave these fixed numeric fields unused. (ChatGPT-5.6-Sol) -->
		.def("getSASWorldChangesHistoryPointsBefore", &CyGame::getSASWorldChangesHistoryPointsBefore)
		.def("getSASWorldChangesHistoryPointsAfter", &CyGame::getSASWorldChangesHistoryPointsAfter)
		.def("getSASWorldChangesHistoryGoldBefore", &CyGame::getSASWorldChangesHistoryGoldBefore)
		.def("getSASWorldChangesHistoryGoldAfter", &CyGame::getSASWorldChangesHistoryGoldAfter)
		.def("getMaxTurns", &CyGame::getMaxTurns)
		.def("setMaxTurns", &CyGame::setMaxTurns)
		.def("changeMaxTurns", &CyGame::changeMaxTurns)
		.def("getMaxCityElimination", &CyGame::getMaxCityElimination)
		.def("setMaxCityElimination", &CyGame::setMaxCityElimination)
		.def("getNumAdvancedStartPoints", &CyGame::getNumAdvancedStartPoints)
		.def("setNumAdvancedStartPoints", &CyGame::setNumAdvancedStartPoints)
		.def("getStartTurn", &CyGame::getStartTurn, "int () - Returns the starting Turn (0 unless a scenario or advanced era start)")
		.def("getStartYear", &CyGame::getStartYear, "int () - Returns the starting year (e.g. -4000)")
		.def("setStartYear", &CyGame::setStartYear, "void () - Sets the starting year (e.g. -4000)")
		.def("getEstimateEndTurn", &CyGame::getEstimateEndTurn)
		.def("setEstimateEndTurn", &CyGame::setEstimateEndTurn)
		.def("getTurnSlice", &CyGame::getTurnSlice)
		.def("getMinutesPlayed", &CyGame::getMinutesPlayed, "Returns the number of minutes since the game began")
		.def("getTargetScore", &CyGame::getTargetScore)
		.def("setTargetScore", &CyGame::setTargetScore)

		.def("getNumGameTurnActive", &CyGame::getNumGameTurnActive)
		.def("countNumHumanGameTurnActive", &CyGame::countNumHumanGameTurnActive)
		.def("getNumCities", &CyGame::getNumCities, "int () - total cities in Game")
		.def("getNumCivCities", &CyGame::getNumCivCities, "int () - total non-barbarian cities in Game")
		.def("getTotalPopulation", &CyGame::getTotalPopulation, "int () - total game population")

		.def("getTradeRoutes", &CyGame::getTradeRoutes)
		.def("changeTradeRoutes", &CyGame::changeTradeRoutes)
		.def("getFreeTradeCount", &CyGame::getFreeTradeCount)
		.def("isFreeTrade", &CyGame::isFreeTrade)
		.def("changeFreeTradeCount", &CyGame::changeFreeTradeCount)
		.def("getNoNukesCount", &CyGame::getNoNukesCount)
		.def("isNoNukes", &CyGame::isNoNukes)
		.def("changeNoNukesCount", &CyGame::changeNoNukesCount)
		.def("getSecretaryGeneralTimer", &CyGame::getSecretaryGeneralTimer)
		.def("getVoteTimer", &CyGame::getVoteTimer)
		.def("getNukesExploded", &CyGame::getNukesExploded)
		.def("changeNukesExploded", &CyGame::changeNukesExploded)

		.def("getMaxPopulation", &CyGame::getMaxPopulation)
		.def("getMaxLand", &CyGame::getMaxLand)
		.def("getMaxTech", &CyGame::getMaxTech)
		.def("getMaxWonders", &CyGame::getMaxWonders)
		.def("getInitPopulation", &CyGame::getInitPopulation)
		.def("getInitLand", &CyGame::getInitLand)
		.def("getInitTech", &CyGame::getInitTech)
		.def("getInitWonders", &CyGame::getInitWonders)

		.def("getAIAutoPlay", &CyGame::getAIAutoPlay)
		.def("setAIAutoPlay", &CyGame::setAIAutoPlay)
		// <!-- custom: Expose the AdvCiv-SAS cause-aware stop method used by AIAutoPlay.py; the legacy setter remains available for compatibility. See KI#203. (GPT-5.6-Sol) -->
		.def("endAIAutoPlay", &CyGame::endAIAutoPlay)

		.def("getGlobalWarmingIndex", &CyGame::getGlobalWarmingIndex)	// K-Mod
		.def("getGlobalWarmingChances", &CyGame::getGlobalWarmingChances)	// K-Mod
		.def("getGwEventTally", &CyGame::getGwEventTally)				// K-Mod
		.def("calculateGlobalPollution", &CyGame::calculateGlobalPollution) // K-Mod
		.def("calculateGwLandDefence", &CyGame::calculateGwLandDefence)	// K-Mod
		.def("calculateGwSustainabilityThreshold", &CyGame::calculateGwSustainabilityThreshold)	// K-Mod
		.def("calculateGwSeverityRating", &CyGame::calculateGwSeverityRating)	// K-Mod

		.def("isScoreDirty", &CyGame::isScoreDirty, "bool ()")
		.def("setScoreDirty", &CyGame::setScoreDirty)
		.def("isCircumnavigated", &CyGame::isCircumnavigated, "bool () - is the globe circumnavigated?")
		.def("makeCircumnavigated", &CyGame::makeCircumnavigated)
		.def("isDiploVote", &CyGame::isDiploVote, "bool (VoteSourceTypes)")
		.def("changeDiploVote", &CyGame::changeDiploVote, "void (VoteSourceTypes, int)")
		.def("isDebugMode", &CyGame::isDebugMode, "bool () - is the game in Debug Mode?")
		.def("toggleDebugMode", &CyGame::toggleDebugMode)

		.def("getPitbossTurnTime", &CyGame::getPitbossTurnTime, "int ()")
		.def("setPitbossTurnTime", &CyGame::setPitbossTurnTime, "void (int)")
		.def("isHotSeat", &CyGame::isHotSeat, "bool ()")
		.def("isPbem", &CyGame::isPbem, "bool ()")
		.def("isPitboss", &CyGame::isPitboss, "bool ()")
		.def("isSimultaneousTeamTurns", &CyGame::isSimultaneousTeamTurns, "bool ()")

		.def("isFinalInitialized", &CyGame::isFinalInitialized, "bool () - Returns whether or not the game initialization process has ended (game has started)")
		// <!-- custom: expose the cached AI map heaviness classification to Python UI without duplicating map-name/start-area logic there. (GPT-5.5) -->
		.def("isLandHeavyMapnameCached", &CyGame::isLandHeavyMapnameCached, "bool ()")
		.def("isNavalHeavyMapnameCached", &CyGame::isNavalHeavyMapnameCached, "bool ()")
		// advc.061:
		.def("setScreenDimensions", &CyGame::setScreenDimensions, "void (int iWidth, int iHeight)")
		.def("getActivePlayer", &CyGame::getActivePlayer, "returns index of the active player")
		.def("setActivePlayer", &CyGame::setActivePlayer, "void (int /*PlayerTypes*/ eNewValue, bool bForceHotSeat)")
		.def("getPausePlayer", &CyGame::getPausePlayer, "int () - will get who paused us")
		.def("isPaused", &CyGame::isPaused, "bool () - will say if the game is paused")
		.def("getBestLandUnit", &CyGame::getBestLandUnit, "returns index of the best unit")
		.def("getBestLandUnitCombat", &CyGame::getBestLandUnitCombat, "int ()")

		.def("getWinner", &CyGame::getWinner)
		.def("getVictory", &CyGame::getVictory)
		.def("setWinner", &CyGame::setWinner)
		.def("getGameState", &CyGame::getGameState)
		.def("getHandicapType", &CyGame::getHandicapType, "HandicapType () - difficulty level settings")
		.def("getAIHandicap", &CyGame::getAIHandicap, "HandicapTypes ()") // advc.708
		.def("getCalendar", &CyGame::getCalendar, "CalendarType ()")
		.def("getStartEra", &CyGame::getStartEra)
		.def("getGameSpeedType", &CyGame::getGameSpeedType)
		.def("getRankPlayer", &CyGame::getRankPlayer)
		.def("getPlayerRank", &CyGame::getPlayerRank)
		.def("getPlayerScore", &CyGame::getPlayerScore)
		.def("getRankTeam", &CyGame::getRankTeam)
		.def("getTeamRank", &CyGame::getTeamRank)
		.def("getTeamScore", &CyGame::getTeamScore)
		.def("isOption", &CyGame::isOption, "bool (eIndex) - returns whether Game Option is valid")
		.def("setOption", &CyGame::setOption, "void (GameOptionIndex, bEnabled) - sets a Game Option")
		.def("isMPOption", &CyGame::isMPOption, "bool (eIndex) - returns whether MP Option is valid")
		.def("isForcedControl", &CyGame::isForcedControl, "bool (eIndex) - returns whether Control should be forced")
		.def("getUnitCreatedCount", &CyGame::getUnitCreatedCount, "int (eIndex) - returns number of this unit type created (?)")
		.def("getUnitClassCreatedCount", &CyGame::getUnitClassCreatedCount, "int (eIndex) - returns number of this unit class type created (?)")
		.def("isUnitClassMaxedOut", &CyGame::isUnitClassMaxedOut, "bool (eIndex, iExtra) - returns whether or not this unit class is maxed out (e.g. spies)")
		.def("getBuildingClassCreatedCount", &CyGame::getBuildingClassCreatedCount, "int (BuildingClassType) - building Class count")
		.def("isBuildingClassMaxedOut", &CyGame::isBuildingClassMaxedOut, "bool (BuildingClassType) - max # reached?")

		.def("getProjectCreatedCount", &CyGame::getProjectCreatedCount, "int (ProjectTypes eIndex)")
		.def("isProjectMaxedOut", &CyGame::isProjectMaxedOut, "bool (ProjectTypes eIndex)")

		.def("getForceCivicCount", &CyGame::getForceCivicCount, "int (CivicTypes eIndex)")
		.def("isForceCivic", &CyGame::isForceCivic, "bool (CivicTypes eIndex)")
		.def("isForceCivicOption", &CyGame::isForceCivicOption, "bool (CivicOptionTypes eCivicOption)")

		.def("getVoteOutcome", &CyGame::getVoteOutcome, "int (VoteTypes eIndex)")

		.def("getReligionGameTurnFounded", &CyGame::getReligionGameTurnFounded)
		.def("isReligionFounded", &CyGame::isReligionFounded, "bool (ReligionID) - is religion founded?")
		.def("isReligionSlotTaken", &CyGame::isReligionSlotTaken, "bool (ReligionID) - is religion in that tech slot founded?")
		.def("getCorporationGameTurnFounded", &CyGame::getCorporationGameTurnFounded)
		.def("isCorporationFounded", &CyGame::isCorporationFounded, "bool (CorporationID) - is corporation founded?")
		.def("isVictoryValid", &CyGame::isVictoryValid)
		.def("isVotePassed", &CyGame::isVotePassed)
		.def("isSpecialUnitValid", &CyGame::isSpecialUnitValid)
		.def("makeSpecialUnitValid", &CyGame::makeSpecialUnitValid)

		.def("isSpecialBuildingValid", &CyGame::isSpecialBuildingValid)
		.def("makeSpecialBuildingValid", &CyGame::makeSpecialBuildingValid)

		.def("isNukesValid", &CyGame::isNukesValid, "bool ()")
		.def("makeNukesValid", &CyGame::makeNukesValid, " void (bool bValid)")

		.def("isInAdvancedStart", &CyGame::isInAdvancedStart, "bool ()")

		.def("getHolyCity", &CyGame::getHolyCity, python::return_value_policy<python::manage_new_object>(), "CyCity getHolyCity()")
		.def("setHolyCity", &CyGame::setHolyCity, "void (int eIndex, CyCity *pNewValue, bAnnounce) - Sets holy city for religion eIndex to pNewValue")
		.def("clearHolyCity", &CyGame::clearHolyCity, "void (int eIndex) - clears the holy city for religion eIndex")

		.def("getHeadquarters", &CyGame::getHeadquarters, python::return_value_policy<python::manage_new_object>(), "CyCity getHeadquarters()")
		.def("setHeadquarters", &CyGame::setHeadquarters, "void (int eIndex, CyCity *pNewValue, bAnnounce) - Sets headquarters for corporation eIndex to pNewValue")
		.def("clearHeadquarters", &CyGame::clearHeadquarters, "void (int eIndex) - clears the headquarters for corporation eIndex")

		.def("getPlayerVote", &CyGame::getPlayerVote)

		.def("getScriptData", &CyGame::getScriptData, "str () - Returns ScriptData member (used to store custom data)")
		.def("setScriptData", &CyGame::setScriptData, "void (str) - Sets ScriptData member (used to store custom data)")

		.def("setName", &CyGame::setName)
		.def("getName", &CyGame::getName)
		.def("getIndexAfterLastDeal", &CyGame::getIndexAfterLastDeal)
		.def("getNumDeals", &CyGame::getNumDeals)
		.def("getDeal", &CyGame::getDeal, python::return_value_policy<python::manage_new_object>())
		.def("addDeal", &CyGame::addDeal, python::return_value_policy<python::manage_new_object>())
		.def("getMapRand", &CyGame::getMapRand, python::return_value_policy<python::reference_existing_object>())
		.def("getMapRandNum", &CyGame::getMapRandNum)
		// <!-- custom: Expose the serialized initial active player read-only so Fast Save filenames keep the original XML leader identity across autoplay handoffs. (ChatGPT-5.6-Sol) -->
		.def("getInitialActivePlayer", &CyGame::getInitialActivePlayer)
		// <!-- custom: Expose the serialized initial map RNG seed read-only for the stable map component of SAS fast-save filenames. (ChatGPT-5.6-Sol) -->
		.def("getInitialMapRandSeed", &CyGame::getInitialMapRandSeed)
		// <!-- custom: Expose the serialized initial sync RNG seed read-only for the stable gameplay-lineage component of SAS fast-save filenames. (ChatGPT-5.6-Sol) -->
		.def("getInitialSyncRandSeed", &CyGame::getInitialSyncRandSeed)
		.def("getSorenRand", &CyGame::getSorenRand, python::return_value_policy<python::reference_existing_object>())
		.def("getSorenRandNum", &CyGame::getSorenRandNum)
		.def("calculateSyncChecksum", &CyGame::calculateSyncChecksum)
		.def("calculateOptionsChecksum", &CyGame::calculateOptionsChecksum)

		.def("GetWorldBuilderMode", &CyGame::GetWorldBuilderMode)
		.def("isPitbossHost", &CyGame::isPitbossHost)
		.def("getCurrentLanguage", &CyGame::getCurrentLanguage)
		.def("setCurrentLanguage", &CyGame::setCurrentLanguage)

		.def("getReplayMessageTurn", &CyGame::getReplayMessageTurn)
		.def("getReplayMessageType", &CyGame::getReplayMessageType)
		.def("getReplayMessagePlotX", &CyGame::getReplayMessagePlotX)
		.def("getReplayMessagePlotY", &CyGame::getReplayMessagePlotY)
		.def("getReplayMessagePlayer", &CyGame::getReplayMessagePlayer)
		.def("getReplayMessageColor", &CyGame::getReplayMessageColor)
		.def("getReplayMessageText", &CyGame::getReplayMessageText)
		.def("getNumReplayMessages", &CyGame::getNumReplayMessages)
		.def("getReplayInfo", &CyGame::getReplayInfo, python::return_value_policy<python::manage_new_object>())
		.def("hasSkippedSaveChecksum", &CyGame::hasSkippedSaveChecksum)
		.def("saveReplay", &CyGame::saveReplay)
		.def("addPlayer", &CyGame::addPlayer, "void (int eNewPlayer, int eLeader, int eCiv)")
		// BETTER_BTS_AI_MOD, Debug, 8/1/08, jdog5000:
		.def("changeHumanPlayer", &CyGame::changeHumanPlayer, "void ( int /*PlayerTypes*/ eNewHuman )")

		.def("getCultureThreshold", &CyGame::getCultureThreshold, "int getCultureThreshold(CultureLevelTypes eLevel)")
		// (advc.enum: deprecated x3)
		.def("getPlotExtraYield", &CyGame::getPlotExtraYield, "int (int iX, int iY, int /*YieldTypes*/ eYield)") // K-Mod
		.def("setPlotExtraYield", &CyGame::setPlotExtraYield, "void (int iX, int iY, int /*YieldTypes*/ eYield, int iExtraYield)")
		.def("changePlotExtraCost", &CyGame::changePlotExtraCost, "void (int iX, int iY, int iCost)")

		.def("isCivEverActive", &CyGame::isCivEverActive, "bool (int /*CivilizationTypes*/ eCivilization)")
		.def("isLeaderEverActive", &CyGame::isLeaderEverActive, "bool (int /*LeaderHeadTypes*/ eLeader)")
		.def("isUnitEverActive", &CyGame::isUnitEverActive, "bool (int /*UnitTypes*/ eUnit)")
		.def("isBuildingEverActive", &CyGame::isBuildingEverActive, "bool (int /*BuildingTypes*/ eBuilding)")

		.def("isEventActive", &CyGame::isEventActive, "bool (int /*EventTriggerTypes*/ eTrigger)")
		.def("doControl", &CyGame::doControl, "void (int /*ControlTypes*/ iControl)")
		// <!-- custom: Python cannot see or close the EXE's popups, which pile up while SASPilot drives the game without the window. (Claude code Fable 5.2) -->
		.def("getSASPilotPopups", &CyGame::getSASPilotPopups, "wstring () - the active player's held, displayed and queued popups, one tab-separated line each")
		.def("closeSASPilotPopups", &CyGame::closeSASPilotPopups, "void (int /*ButtonPopupTypes*/ iType, int iData1) - drop held and queued popups of a type, or all with -1")
		.def("answerSASPilotPopup", &CyGame::answerSASPilotPopup, "bool (int iHeldId, int iButton, wstring szEditBox) - answer a held popup, by the ID getSASPilotPopups gives, as if its button were clicked")
		.def("setSASPilotPopupsHeld", &CyGame::setSASPilotPopupsHeld, "void (bool bHeld) - hold popups back instead of launching them")
		.def("isSASPilotPopupsHeld", &CyGame::isSASPilotPopupsHeld, "bool ()")
		// <!-- custom: SASPilot's plot and plots commands return this C++ JSON as it is, as it was about 25 times faster than writing it in Python. (Claude code Opus 5.5) -->
		.def("getSASPilotUnitsJson", &CyGame::getSASPilotUnitsJson, "string (int iPlayer, int iFogTeam) - a player's units as JSON, or every living player's with -1, written in C++; with a fog team, only those it sees")
		// <!-- custom: Python's 'trade' and 'techs' read the diplomacy table's items from this, as the Python loop over every tradeable item took 3.5 ms of game time per call (2026-11-13). (Claude code Opus 5.5) -->
		.def("getSASPilotTradeItemsJson", &CyGame::getSASPilotTradeItemsJson, "string (int iGiver, int iReceiver, int iKindOnly) - what iGiver could put on the diplomacy table for iReceiver, as JSON with each AI denial; iKindOnly a TradeableItems kind or -1 for all")
		.def("getSASPilotPlotsJson", &CyGame::getSASPilotPlotsJson, "string (int iX, int iY, int iRadius, int iFogTeam) - the plots within a radius as JSON, written in C++; with a fog team, only what it knows")
		// <!-- custom: Python's generatePath gives no steps, and Python cannot read the player's on-screen messages; the pilot needs both to play as a person does. (Claude code Fable 5.2) -->
		.def("getSASPilotPathJson", &CyGame::getSASPilotPathJson, "string (int iPlayer, int iUnit, int iX, int iY, int iFlags) - the steps of a unit's path to a plot as JSON")
		.def("getSASPilotMessagesJson", &CyGame::getSASPilotMessagesJson, "string (int iPlayer, int iSinceTurn) - a player's listed on-screen messages as JSON")
		// <!-- custom: The window circles recommended city sites for a selected Settler from CvPlayerAI's site list, which Python cannot reach; the pilot needs them to choose a site as a person does. (Claude code Opus 5.5) -->
		.def("getSASPilotCitySitesJson", &CyGame::getSASPilotCitySitesJson, "string (int iPlayer, int iUnit) - the city sites the window would circle for this Settler, as JSON")
		// <!-- custom: Python can list tradeable items but cannot ask an AI to weigh an offer or make the deal; the pilot needs both to trade as a person does. (Claude code Opus 5.5) -->
		// <!-- custom: Python has no CyUnit.joinGroup; the pilot needs it to escort a unit or move a stack as one, as selecting units together does in the window. (Claude code Opus 5.5) -->
		.def("joinSASPilotGroup", &CyGame::joinSASPilotGroup, "string (int iPlayer, int iUnit, int iHeadUnit) - join a unit to another's group on its plot, or split it off with -1; the group ID or null")
		// <!-- custom: CyMessageControl.sendResearch cannot grant a free tech (it passes iDiscover -1); the pilot needs it for the Oracle's and other free techs. (Claude code Opus 5.5) -->
		// <!-- custom: The pilot's notices dropped popups through closeSASPilotPopups, whose killAll relaunches the popups on display (Codex's review); this drops one exactly. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		.def("dropSASPilotPopup", &CyGame::dropSASPilotPopup, "bool (int iHeldId, int iButtonPopupType, int iData1, int iData3, wstring szText) - drop the held popup with that ID, or with -1 the first queued one matching type, data1, data3 and text")
		.def("chooseSASPilotFreeTech", &CyGame::chooseSASPilotFreeTech, "bool (int iTech, int iHeldId) - choose a free tech as the tech chooser does, through the held chooser with that ID")
		.def("isSASPilotChoosingFreeTech", &CyGame::isSASPilotChoosingFreeTech, "bool () - whether the active player still owes a free tech choice")
		.def("proposeSASPilotDeal", &CyGame::proposeSASPilotDeal, "string (int iPlayer, int iOther, string szWeGive, string szTheyGive) - propose a deal to an AI as 'kind:data,...' lists; JSON with whether it was accepted and made")
		// <!-- custom: Python cannot put items on the EXE's trade table; the pilot's 'contact' opens the table with a deal on it so the screen's own replies, "What would you want?" and the counter-offer included, can answer it. (Claude code Opus 5.5) -->
		.def("tableSASPilotDeal", &CyGame::tableSASPilotDeal, "bool (int iPlayer, int iOther, string szWeGive, string szTheyGive) - open the diplomacy screen with an AI on its trade table with these 'kind:data,...' items on it")
		// advc.095:
		.def("setCityBarWidth", &CyGame::setCityBarWidth, "void (bool)")
		// advc.092c:
		.def("setHelpTextAreaWidth", &CyGame::setHelpTextAreaWidth, "void (float)")
		// BULL - AutoSave:
		.def("saveGame", &CyGame::saveGame, "void saveGame(string fullyQualifiedFileName)")
		// advc.104:
		.def("useKModAI", &CyGame::useKModAI, "bool ()")
		// advc.300:
		.def("getBarbarianStartTurn", &CyGame::getBarbarianStartTurn, "int ()")
		// advc.250b:
		.def("SPaHPointsForSettingsScreen", &CyGame::SPaHPointsForSettingsScreen)
		// advc.250:
		.def("getDifficultyForEndScore", &CyGame::getDifficultyForEndScore, "int ()")
		// <advc.703>
		.def("getMaxChapters", &CyGame::getMaxChapters, "int ()")
		.def("getCurrentChapter", &CyGame::getCurrentChapter, "int ()")
		.def("getChapterStart", &CyGame::getChapterStart, "int (int)")
		.def("getChapterEnd", &CyGame::getChapterEnd, "int (int)")
		.def("getChapterScore", &CyGame::getChapterScore, "int (int)")
		.def("getChapterScoreTurn", &CyGame::getChapterScoreTurn, "int (int)")
		.def("getChapterCiv", &CyGame::getChapterCiv, "int (int)")
		.def("chapterScoreBreakdown", &CyGame::chapterScoreBreakdown)
		.def("riseScoreBreakdown", &CyGame::riseScoreBreakdown)
		// </advc.704><advc.706>
		.def("isRFInterlude", &CyGame::isRFInterlude, "bool ()")
		.def("isRFBlockPopups", &CyGame::isRFBlockPopups, "bool ()") // </advc.706>
		// advc.004m:
		.def("reportCurrentLayer", &CyGame::reportCurrentLayer, "void(int /*GlobeLayerTypes*/)")
		.def("isCivLeaderSetupKnown", &CyGame::isCivLeaderSetupKnown, "bool ()") // advc.190c
		.def("isScenario", &CyGame::isScenario, "bool ()") // advc.052
		;

	python::class_<CyDeal>("CyDeal")
		.def("isNone", &CyDeal::isNone)
		.def("getID", &CyDeal::getID)
		.def("getInitialGameTurn", &CyDeal::getInitialGameTurn)
		.def("getFirstPlayer", &CyDeal::getFirstPlayer)
		.def("getSecondPlayer", &CyDeal::getSecondPlayer)
		.def("getLengthFirstTrades", &CyDeal::getLengthFirstTrades)
		.def("getLengthSecondTrades", &CyDeal::getLengthSecondTrades)
		.def("getFirstTrade", &CyDeal::getFirstTrade, python::return_value_policy<python::reference_existing_object>())
		.def("getSecondTrade", &CyDeal::getSecondTrade, python::return_value_policy<python::reference_existing_object>())
		.def("kill", &CyDeal::kill)
		;
}

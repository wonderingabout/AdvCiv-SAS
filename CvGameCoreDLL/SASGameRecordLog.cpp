#include "CvGameCoreDLL.h"
#include "SASGameRecordLog.h"
#include "CvGame.h" // <!-- custom: Needed for game-record turn, game-state, victory, RNG, and map-classification context rows. (GPT-5.5) -->
#include "CvPlayer.h" // <!-- custom: Needed directly for active-player civilization/handicap context in this smaller AdvCiv 1.14 port slice; do not rely on later SASGameRecord headers to complete CvPlayer transitively. (ChatGPT-5.6-Sol) -->
#include "CvTeam.h" // <!-- custom: Needed directly for finalized initial-team state and technology grouping in this smaller AdvCiv 1.14 port slice; GET_TEAM is defined by CvTeam.h. (ChatGPT-5.6-Sol) -->
#include "CvInfo_Organization.h" // <!-- custom: Needed for religion/corporation type names in game-record action rows. (GPT-5.5) -->
#include "CvInfo_Civics.h" // <!-- custom: Needed for policy/civic names in game-record advisor rows. (ChatGPT-5.5) -->
#include "CvInfo_Civilization.h" // <!-- custom: Needed to attribute player-wide extra happiness/health to traits instead of leaving effects from loaded-mod rules under an opaque `extra` label. (GPT-5.6-Sol) -->
#include "CvInfo_Tech.h" // <!-- custom: Needed for stable technology type names and XML trade-capability source mapping. (ChatGPT-5.6-Sol) -->
#include "CvInfo_Symbol.h" // <!-- custom: Needed to log actual assigned player-color and primary-color context; CvGlobals only forward-declares their info classes. (GPT-5.6-Sol) -->
#include "CvGameCoreUtils.h" // <!-- custom: Needed for shared machine-readable diagnostic quoting/list helpers used by SASGameRecord. (ChatGPT-5.6-Sol) -->
#include "CvInfo_GameOption.h" // <!-- custom: Needed to log enabled game-option type names; CvGlobals only forward-declares CvGameOptionInfo. (GPT-5.5) -->
#include "CvMap.h" // <!-- custom: Needed to log map dimensions; CvGlobals only forward-declares CvMap. (GPT-5.5) -->
#include <algorithm>
#include <vector> // <!-- custom: Used for grouped finalized initial-team technology payloads. (ChatGPT-5.6-Sol) -->
#include <time.h>

static int getClampedSASGameRecordLogLevel(char const* szDefineName)
{
	const int iLevel = GC.getDefineINT(szDefineName);
	if (iLevel < 0)
		return 0;
	if (iLevel > 3)
		return 3;
	return iLevel;
}

// <!-- custom: Dedicated structured game-record log for autoplay comparison, general game analysis, and external LLM review.
// This is independent from SAS_BBAI_LOG_ENABLE because it is a run-report artifact rather than classic AI-decision diagnostics, and writes to SASGameRecord_*.log when enabled.
// Use ACTION rows rather than EVENT rows to avoid confusion with Civ4 random events.
// Keep the recorder portable across Civ4 mods by enumerating loaded XML and using generic field meanings instead of hardcoding AdvCiv-SAS types or copying the full XML.
// Mod-specific rules can still be named in comments as concrete examples: TECH_DEPOPULATION currently applies negative player-wide health and happiness in AdvCiv-SAS, but the recorder attributes health/happiness from every loaded trait, civic and technology dynamically.
// The record describes the current format; do not add schema-version maintenance unless independently evolving consumers later require it. (ChatGPT-5.5 + GPT-5.5 + GPT-5.6-Sol) -->
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

static CvString g_szSASGameRecordLogTimestamp;
static int g_iSASGameRecordLogSequence = 0;
static CvString g_szSASGameRecordLogContext;

static CvString createSASGameRecordUtcTimestamp()
{
	time_t kNow;
	time(&kNow);
	char szBuffer[32];
	struct tm* pUtcTime = gmtime(&kNow);
	if (pUtcTime != NULL && strftime(szBuffer, sizeof(szBuffer), "%Y%m%dT%H%M%SZ", pUtcTime) > 0)
		return CvString(szBuffer);
	return CvString("unknown_time");
}

static CvString getSASGameRecordLogTimestamp()
{
	if (g_szSASGameRecordLogTimestamp.empty())
		g_szSASGameRecordLogTimestamp = createSASGameRecordUtcTimestamp();
	return g_szSASGameRecordLogTimestamp;
}

static bool isSASGameRecordTimestampedFilenameEnabled()
{
	static const bool bUseTimestampedFilename = (GC.getDefineINT("SAS_GAME_RECORD_LOG_USE_TIMESTAMPED_FILENAME") > 0);
	return bUseTimestampedFilename;
}

static CvString getSASGameRecordLogName()
{
	CvString szLogName;
	if (GC.getGame().isNetworkMultiPlayer())
	{
		if (isSASGameRecordTimestampedFilenameEnabled())
		{
			if (!g_szSASGameRecordLogContext.empty())
				szLogName.Format("SASGameRecord%d_%s_%s.log", (int)GC.getGame().getActivePlayer(), getSASGameRecordLogTimestamp().GetCString(), g_szSASGameRecordLogContext.GetCString());
			else szLogName.Format("SASGameRecord%d_%s.log", (int)GC.getGame().getActivePlayer(), getSASGameRecordLogTimestamp().GetCString());
		}
		else szLogName.Format("SASGameRecord%d.log", (int)GC.getGame().getActivePlayer());
	}
	else
	{
		if (isSASGameRecordTimestampedFilenameEnabled())
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
	g_szSASGameRecordLogTimestamp = createSASGameRecordUtcTimestamp();
	g_szSASGameRecordLogContext.clear();
	if (isSASGameRecordTimestampedFilenameEnabled())
	{
		g_iSASGameRecordLogSequence++;
		g_szSASGameRecordLogContext.Format("%s%d", szContext, g_iSASGameRecordLogSequence);
	}
}

static void appendSASGameRecordType(CvString& szTypes, char const* szType)
{
	if (!szTypes.empty()) szTypes += ",";
	szTypes += szType;
}

static void logSASGameRecordLogSettings()
{
	logSASGameRecord("GAME_RECORD_LOG_SETTINGS SAS_GAME_RECORD_LOG_LEVEL=%d SAS_GAME_RECORD_INTERVAL_TURNS_UNSCALED_GAMESPEED=%d SAS_GAME_RECORD_LOG_USE_TIMESTAMPED_FILENAME=%d",
			getSASGameRecordLogLevel(), getSASGameRecordTurnInterval(), isSASGameRecordTimestampedFilenameEnabled());
}

// <!-- custom: Compact finalized team rows preserve which technologies each team owns and which diplomacy capabilities are active, but replacing setup-time TECH_ACQUIRED spam otherwise loses which technology grants each capability.
// Record the loaded XML mapping once for the whole session instead of repeating the same effect fields for every initial team-tech pair. (GPT-5.6-Sol) -->
static void logSASGameRecordTechCapabilitySources()
{
	CvString szMapTrading, szTechTrading, szGoldTrading, szOpenBordersTrading, szDefensivePactTrading, szPermanentAllianceTrading, szVassalStateTrading;
	FOR_EACH_ENUM(Tech)
	{
		CvTechInfo const& kTech = GC.getInfo(eLoopTech);
		if (kTech.isMapTrading()) appendSASGameRecordType(szMapTrading, kTech.getType());
		if (kTech.isTechTrading()) appendSASGameRecordType(szTechTrading, kTech.getType());
		if (kTech.isGoldTrading()) appendSASGameRecordType(szGoldTrading, kTech.getType());
		if (kTech.isOpenBordersTrading()) appendSASGameRecordType(szOpenBordersTrading, kTech.getType());
		if (kTech.isDefensivePactTrading()) appendSASGameRecordType(szDefensivePactTrading, kTech.getType());
		if (kTech.isPermanentAllianceTrading()) appendSASGameRecordType(szPermanentAllianceTrading, kTech.getType());
		if (kTech.isVassalStateTrading()) appendSASGameRecordType(szVassalStateTrading, kTech.getType());
	}
	logSASGameRecord("GAME_RECORD_TECH_CAPABILITY_SOURCES mapTrading=%s techTrading=%s goldTrading=%s openBordersTrading=%s defensivePactTrading=%s permanentAllianceTrading=%s vassalStateTrading=%s source=LOADED_XML",
			getSASDiagnosticOrDash(szMapTrading).GetCString(), getSASDiagnosticOrDash(szTechTrading).GetCString(), getSASDiagnosticOrDash(szGoldTrading).GetCString(), getSASDiagnosticOrDash(szOpenBordersTrading).GetCString(), getSASDiagnosticOrDash(szDefensivePactTrading).GetCString(), getSASDiagnosticOrDash(szPermanentAllianceTrading).GetCString(), getSASDiagnosticOrDash(szVassalStateTrading).GetCString());
}

// <!-- custom: Record every stored map-script option, including hidden values. Keep numeric values durable so setup can be reconstructed without relying on localized descriptions or a currently available Python map script. (ChatGPT-5.6-Sol) -->
static void logSASGameRecordMapOptions(CvInitCore const& kInitCore)
{
	const int iNumOptions = kInitCore.getNumCustomMapOptions();
	const int iNumHiddenOptions = std::min(iNumOptions, std::max(0, kInitCore.getNumHiddenCustomMapOptions()));
	logSASGameRecord("GAME_RECORD_MAP_OPTIONS count=%d hidden=%d", iNumOptions, iNumHiddenOptions);
	for (int iOption = 0; iOption < iNumOptions; iOption++)
	{
		const bool bHidden = (iOption >= iNumOptions - iNumHiddenOptions);
		logSASGameRecord("GAME_RECORD_MAP_OPTION index=%d hidden=%d value=%d", iOption, bHidden, kInitCore.getCustomMapOption(iOption));
	}
}

static const char* getSASGameRecordReligionType(ReligionTypes eReligion)
{
	return (eReligion == NO_RELIGION ? "-" : GC.getInfo(eReligion).getType());
}

static const char* getSASGameRecordCivicType(CivicTypes eCivic)
{
	return (eCivic == NO_CIVIC ? "-" : GC.getInfo(eCivic).getType());
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
	PlayerColorTypes const ePlayerColor = kPlayer.getPlayerColor();
	char const* szPlayerColor = "-";
	char const* szPrimaryColor = "-";
	int iPrimaryRed = -1;
	int iPrimaryGreen = -1;
	int iPrimaryBlue = -1;
	if (ePlayerColor != NO_PLAYERCOLOR)
	{
		CvPlayerColorInfo const& kPlayerColor = GC.getInfo(ePlayerColor);
		ColorTypes const ePrimaryColor = kPlayerColor.getColorTypePrimary();
		szPlayerColor = kPlayerColor.getType();
		if (ePrimaryColor != NO_COLOR)
		{
			NiColorA const& kPrimaryColor = GC.getInfo(ePrimaryColor).getColor();
			szPrimaryColor = GC.getInfo(ePrimaryColor).getType();
			iPrimaryRed = (int)(255 * kPrimaryColor.r);
			iPrimaryGreen = (int)(255 * kPrimaryColor.g);
			iPrimaryBlue = (int)(255 * kPrimaryColor.b);
		}
	}
	CvString szTraits;
	FOR_EACH_ENUM(Trait)
	{
		if (!kPlayer.hasTrait(eLoopTrait))
			continue;
		if (!szTraits.empty())
			szTraits += ",";
		szTraits += GC.getInfo(eLoopTrait).getType();
	}
	// <!-- custom: Leader traits and favorites are fixed but materially explain AI behavior and economic results.
	// Record them once per setup/load rather than repeating them in periodic player or policy snapshots. (GPT-5.6-Sol) -->
	// <!-- custom: Log the assigned PlayerColor rather than the civilization default because Civ4 can reassign duplicates.
	// The primary ColorInfo and RGB values help connect text records to maps and screenshots without requiring the source XML. (GPT-5.6-Sol) -->
	// <!-- custom: CvInitCore preserves whether civilization and leader were assigned through Random.
	// Older/imported saves can lack that provenance, so keep unknown distinct from a verified manual choice. (ChatGPT-5.6-Sol) -->
	bool const bCivLeaderChoiceKnown = kInitCore.isCivLeaderSetupKnown();
	logSASGameRecord("GAME_RECORD_PLAYER_SETUP turn=%d player=%d team=%d alive=%d everAlive=%d human=%d humanSlot=%d currentlyHumanControlled=%d autoplayControlled=%d slotStatus=%d civLeaderChoiceKnown=%d civChosenRandomly=%d leaderChosenRandomly=%d playerName=%S civType=%s civName=%S civShortName=%S leaderType=%s leaderName=%S playerColor=%s primaryColor=%s primaryColorRGB=%d,%d,%d traits=%s favoriteCivic=%s favoriteReligion=%s handicap=%s",
			GC.getGame().getGameTurn(), ePlayer, kPlayer.getTeam(), kPlayer.isAlive(), kPlayer.isEverAlive(), bCurrentlyHumanControlled, bHumanSlot, bCurrentlyHumanControlled, bAutoplayControlled, kInitCore.getSlotStatus(ePlayer), bCivLeaderChoiceKnown, bCivLeaderChoiceKnown ? kInitCore.wasCivRandomlyChosen(ePlayer) : -1, bCivLeaderChoiceKnown ? kInitCore.wasLeaderRandomlyChosen(ePlayer) : -1,
			getSASDiagnosticQuoted(kPlayer.getName(0)).GetCString(), szCivType, getSASDiagnosticQuoted(kPlayer.getCivilizationDescription(0)).GetCString(), getSASDiagnosticQuoted(kPlayer.getCivilizationShortDescription(0)).GetCString(), szLeaderType, getSASDiagnosticQuoted(szLeaderName).GetCString(),
			szPlayerColor, szPrimaryColor, iPrimaryRed, iPrimaryGreen, iPrimaryBlue, getSASDiagnosticOrDash(szTraits).GetCString(), getSASGameRecordCivicType(kPlayer.getFavoriteCivic()), getSASGameRecordReligionType(kPlayer.getFavoriteReligion()), kPlayer.getHandicapType() == NO_HANDICAP ? "-" : GC.getInfo(kPlayer.getHandicapType()).getType());
}

// <!-- custom: Team-state rows identify numeric members exactly, but placing readable player/civilization identities only after hundreds of geography and text-map rows made the initial team and technology records needlessly hard to interpret.
// Emit fixed slot bounds and player identities before team relations; later map legends can still reference the same PLAYER_SETUP rows without repeating them. (GPT-5.6-Sol) -->
static void logSASGameRecordInitialPlayerIdentities()
{
	logSASGameRecord("GAME_RECORD_SLOT_CONSTANTS MAX_CIV_PLAYERS=%d MAX_PLAYERS=%d BARBARIAN_PLAYER=%d MAX_CIV_TEAMS=%d MAX_TEAMS=%d BARBARIAN_TEAM=%d NO_PLAYER=%d NO_TEAM=%d", MAX_CIV_PLAYERS, MAX_PLAYERS, BARBARIAN_PLAYER, MAX_CIV_TEAMS, MAX_TEAMS, BARBARIAN_TEAM, NO_PLAYER, NO_TEAM);
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes const eLoopPlayer = (PlayerTypes)iI;
		CvPlayer const& kLoopPlayer = GET_PLAYER(eLoopPlayer);
		if (kLoopPlayer.isEverAlive() && !kLoopPlayer.isBarbarian())
			logSASGameRecordPlayerSetup(eLoopPlayer);
	}
}

struct SASGameRecordInitialTechGroup
{
	CvString szTechFields;
	CvString szTeams;
	int iTeams;
};

// <!-- custom: Successful new-game initialization is best described by its authoritative result, not by the order in which Civ4 happened to call meet/declareWar/setHasTech/startTrade while constructing that result.
// Group identical technology sets so a late-era start does not repeat the same long payload for every team; the explicit team lists keep arbitrary scenarios and mixed/modded setups exact. (ChatGPT-5.6-Sol + GPT-5.6-Sol) -->
static void logSASGameRecordFinalizedInitialTeamsAndTechs(int& iTeamStateRows, int& iTechRows)
{
	iTeamStateRows = 0;
	iTechRows = 0;
	std::vector<SASGameRecordInitialTechGroup> aTechGroups;
	for (int iI = 0; iI < MAX_TEAMS; iI++)
	{
		TeamTypes const eTeam = (TeamTypes)iI;
		if (!GET_TEAM(eTeam).isEverAlive())
			continue;
		logSASGameRecord("GAME_RECORD_INITIAL_TEAM_STATE %s", getSASInitialTeamStateFields(eTeam).GetCString());
		CvString const szTechFields = getSASInitialTeamTechLevelFields(eTeam);
		SASGameRecordInitialTechGroup* pGroup = NULL;
		for (size_t iGroup = 0; iGroup < aTechGroups.size(); iGroup++)
		{
			if (aTechGroups[iGroup].szTechFields == szTechFields)
			{
				pGroup = &aTechGroups[iGroup];
				break;
			}
		}
		if (pGroup == NULL)
		{
			SASGameRecordInitialTechGroup kGroup;
			kGroup.szTechFields = szTechFields;
			kGroup.iTeams = 0;
			aTechGroups.push_back(kGroup);
			pGroup = &aTechGroups.back();
		}
		appendSASDiagnosticIntListValue(pGroup->szTeams, eTeam);
		pGroup->iTeams++;
		iTeamStateRows++;
	}
	for (size_t iGroup = 0; iGroup < aTechGroups.size(); iGroup++)
	{
		SASGameRecordInitialTechGroup const& kGroup = aTechGroups[iGroup];
		logSASGameRecord("GAME_RECORD_INITIAL_TEAM_TECHS teams=%s teamCount=%d %s", kGroup.szTeams.GetCString(), kGroup.iTeams, kGroup.szTechFields.GetCString());
		iTechRows++;
	}
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
			szRowType, getSASGameRecordLogTimestamp().GetCString(), getSASDiagnosticQuoted(szLogName.GetCString()).GetCString(), kGame.getGameTurn(), kGame.getElapsedGameTurns(), kGame.getGameTurnYear(), kGame.isScenario(), eActivePlayer, szActiveCivilization, szActiveHandicap, kInitCore.getNumDefinedPlayers(), kGame.countCivPlayersAlive(), kGame.countCivPlayersEverAlive(), kGame.getNumHumanPlayers());
	// <!-- custom: Enabled victories and their fixed turn/score limits determine which later victory-progress and AI-strategy rows are relevant. Record this compact setup context instead of requiring external XML or save inspection. (GPT-5.6-Sol) -->
	// <!-- custom: AdvCiv-SAS also records its own cached land-heavy/naval-heavy map classifications here. Base AdvCiv 1.14 has no equivalent generic cache, so this upstream port intentionally leaves those SAS-specific fields out rather than recreating mod policy inside the recorder. (ChatGPT-5.6-Sol) -->
	logSASGameRecord("GAME_RECORD_GAME_SETTINGS mapScript=%S map=%dx%d world=%s climate=%s seaLevel=%s gameSpeed=%s startEra=%s gameHandicap=%s maxTurns=%d targetScore=%d victories=%s options=%s",
			getSASDiagnosticQuoted(kInitCore.getMapScriptName().GetCString()).GetCString(), GC.getMap().getGridWidth(), GC.getMap().getGridHeight(), GC.getInfo(kInitCore.getWorldSize()).getType(), GC.getInfo(kInitCore.getClimate()).getType(), GC.getInfo(kInitCore.getSeaLevel()).getType(), GC.getInfo(kGame.getGameSpeedType()).getType(), GC.getInfo(kGame.getStartEra()).getType(), GC.getInfo(kGame.getHandicapType()).getType(), kGame.getMaxTurns(), kGame.getTargetScore(), szVictories.GetCString(), szGameOptions.GetCString());
	logSASGameRecordMapOptions(kInitCore);
	logSASGameRecord("GAME_RECORD_GAME_RNG mapRandState=%u syncRandState=%u", kGame.getMapRand().getSeed(), kGame.getSorenRand().getSeed());
}

void logSASGameRecord(TCHAR* format, ... )
{
	static const bool bEnabled = isSASGameRecordLogEnabled();
	if (!bEnabled)
		return;

	va_list args;
	va_start(args, format);
	std::string szLine;
	// <!-- custom: KI#161.2's explicit terminator stopped MSVC 7.1 truncation from leaving unsafe unterminated output, but the fixed 2048-byte buffer still silently discarded long structured rows such as late-game building, unit-type and promotion inventories.
	// Reuse CvString's grow-and-retry formatter so the complete machine-readable row reaches the log; abort the row if even that bounded formatter fails. See KI#375. (ChatGPT-5.5 + GPT-5.5; ChatGPT-5.6-Sol + GPT-5.6-Sol) -->
	bool const bFormatted = CvString::formatv(szLine, format, args);
	va_end(args);
	FAssertMsg(bFormatted, "SASGameRecord row formatting failed");
	if (!bFormatted)
		return;

	CvString const szLogName = getSASGameRecordLogName();
	gDLL->logMsg(szLogName.GetCString(), szLine.c_str(), false, false);
}

void startSASGameRecordLogForNewGame()
{
	rollSASGameRecordLog("new");
	CvString const szLogName = getSASGameRecordLogName();
	logSASGameRecord("GAME_RECORD_NEW_GAME_INITIALIZING utc=%s logFile=%s", getSASGameRecordLogTimestamp().GetCString(), getSASDiagnosticQuoted(szLogName.GetCString()).GetCString());
	logSASGameRecordLogSettings();
	logSASGameRecordTechCapabilitySources();
}

void logSASGameRecordNewGameStarted()
{
	logSASGameRecordGameState("GAME_RECORD_NEW_GAME_STARTED");
	logSASGameRecordInitialPlayerIdentities();
	if (getSASGameRecordLogLevel() >= 2)
	{
		int iTeamStateRows = 0;
		int iTechRows = 0;
		// <!-- custom: Current AdvCiv-SAS also seeds later team/contact deltas and records surviving setup deals at this finalized-state boundary; those coherent recorder pieces are ported separately rather than introducing partial state/deal plumbing here. (ChatGPT-5.6-Sol) -->
		logSASGameRecordFinalizedInitialTeamsAndTechs(iTeamStateRows, iTechRows);
		logSASGameRecord("GAME_RECORD_INITIAL_STATE_SUMMARY teamStateRows=%d techGroupRows=%d techTeamsCovered=%d source=FINALIZED_STATE", iTeamStateRows, iTechRows, iTeamStateRows);
	}
}

void startSASGameRecordLogForLoadedSave()
{
	rollSASGameRecordLog("load");
	logSASGameRecordGameState("GAME_RECORD_SAVE_LOADED");
	logSASGameRecordLogSettings();
	logSASGameRecordTechCapabilitySources();
	logSASGameRecordInitialPlayerIdentities();
}


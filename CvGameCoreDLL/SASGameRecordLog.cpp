#include "CvGameCoreDLL.h"
#include "SASGameRecordLog.h"
#include "CvGame.h" // <!-- custom: Needed for game-record turn, game-state, victory, RNG, and map-classification context rows. (GPT-5.5) -->
#include "CvPlayer.h" // <!-- custom: Needed directly for active-player civilization/handicap context in this smaller AdvCiv 1.14 port slice; do not rely on later SASGameRecord headers to complete CvPlayer transitively. (ChatGPT-5.6-Sol) -->
#include "CvTeam.h" // <!-- custom: Needed directly for finalized initial-team state and technology grouping in this smaller AdvCiv 1.14 port slice; GET_TEAM is defined by CvTeam.h. (ChatGPT-5.6-Sol) -->
#include "CvUnit.h" // <!-- custom: Needed for the mature SASGameRecord distinction between actual combat-capable units and Civ4's separate bMilitarySupport counter in periodic player snapshots. (ChatGPT-5.6-Sol) -->
#include "CvInfo_Organization.h" // <!-- custom: Needed for religion/corporation type names in game-record action rows. (GPT-5.5) -->
#include "CvInfo_Civics.h" // <!-- custom: Needed for policy/civic names in game-record advisor rows. (ChatGPT-5.5) -->
#include "CvInfo_Civilization.h" // <!-- custom: Needed to attribute player-wide extra happiness/health to traits instead of leaving effects from loaded-mod rules under an opaque `extra` label. (GPT-5.6-Sol) -->
#include "CvInfo_Tech.h" // <!-- custom: Needed for stable technology type names and XML trade-capability source mapping. (ChatGPT-5.6-Sol) -->
#include "CvInfo_Misc.h" // <!-- custom: Needed directly for era type names in periodic team technology summaries; base AdvCiv only forward-declares CvEraInfo through CvGlobals. (ChatGPT-5.6-Sol) -->
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

// <!-- custom: Keep only the team fields already consumed by this first periodic snapshot slice. Later player/global snapshot ports can extend their own recorder-local baselines independently. (ChatGPT-5.6-Sol) -->
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

static SASGameRecordTeamPrevious g_akSASGameRecordTeamPrevious[MAX_TEAMS];

// <!-- custom: Keep the portable high-level player fields first. More specialized bonus, espionage, unit-posture, worker, territory and city baselines are added with the corresponding snapshot rows rather than existing as unused state. (ChatGPT-5.6-Sol) -->
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
	int iHistoryScore;
	int iHistoryEconomy;
	int iHistoryIndustry;
	int iHistoryAgriculture;
	int iHistoryPower;
	int iHistoryCulture;
	int iHistoryEspionage;
};

static SASGameRecordPlayerPrevious g_akSASGameRecordPlayerPrevious[MAX_PLAYERS];

static int getSASGameRecordDelta(bool bValid, int iCurrent, int iPrevious)
{
	return bValid ? iCurrent - iPrevious : 0;
}

static void resetSASGameRecordTeamPrevious()
{
	for (int iI = 0; iI < MAX_TEAMS; iI++)
	{
		g_akSASGameRecordTeamPrevious[iI].bValid = false;
		g_akSASGameRecordTeamPrevious[iI].bContactsValid = false;
	}
}

static void resetSASGameRecordPlayerPrevious()
{
	for (int iI = 0; iI < MAX_PLAYERS; iI++)
		g_akSASGameRecordPlayerPrevious[iI].bValid = false;
}

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

static const char* getSASGameRecordEraType(EraTypes eEra)
{
	return (eEra == NO_ERA ? "-" : GC.getInfo(eEra).getType());
}

static const char* getSASGameRecordTechType(TechTypes eTech)
{
	return (eTech == NO_TECH ? "-" : GC.getInfo(eTech).getType());
}

static void appendSASGameRecordTypeCount(CvString& szList, const char* szType, int iCount)
{
	if (iCount <= 0)
		return;
	CvString szItem;
	szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", szType, iCount);
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
			appendSASDiagnosticIntListValue(szList, eLoopPlayer);
	}
	return getSASDiagnosticOrDash(szList);
}

static CvString getSASGameRecordWarTeams(TeamTypes eTeam)
{
	CvString szList;
	CvTeam const& kTeam = GET_TEAM(eTeam);
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam != eTeam && GET_TEAM(eLoopTeam).isAlive() && kTeam.isAtWar(eLoopTeam))
			appendSASDiagnosticIntListValue(szList, eLoopTeam);
	}
	return getSASDiagnosticOrDash(szList);
}

static CvString getSASGameRecordVassalTeams(TeamTypes eTeam)
{
	CvString szList;
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (eLoopTeam != eTeam && GET_TEAM(eLoopTeam).isAlive() && GET_TEAM(eLoopTeam).isVassal(eTeam))
			appendSASDiagnosticIntListValue(szList, eLoopTeam);
	}
	return getSASDiagnosticOrDash(szList);
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
			appendSASDiagnosticIntListValue(szMetTeams, eLoopTeam);
	}
	return getSASDiagnosticOrDash(szMetTeams);
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
	return getSASDiagnosticOrDash(szList);
}

static void seedSASGameRecordTeamPreviousFromCurrentState(TeamTypes eTeam)
{
	CvGame const& kGame = GC.getGame();
	CvTeam const& kTeam = GET_TEAM(eTeam);
	SASGameRecordTeamPrevious& kPrevious = g_akSASGameRecordTeamPrevious[eTeam];
	int const iLand = kTeam.getTotalLand();
	int const iPopulation = kTeam.getTotalPopulation();
	kPrevious.bValid = true;
	kPrevious.iTechs = kTeam.getTechCount();
	kPrevious.iLand = iLand;
	kPrevious.iLandPctX100 = (10000 * iLand) / std::max(1, GC.getMap().getLandPlots());
	kPrevious.iPopulation = iPopulation;
	kPrevious.iPopPctX100 = (10000 * iPopulation) / std::max(1, kGame.getTotalPopulation());
	kPrevious.bContactsValid = true;
	kPrevious.iMetTeams = getSASGameRecordMetTeamCount(eTeam);
}

static void logSASGameRecordTeamSnapshot(TeamTypes eTeam, int iGameTurn)
{
	CvGame const& kGame = GC.getGame();
	CvTeam const& kTeam = GET_TEAM(eTeam);
	bool const bLogTeamDetails = (getSASGameRecordLogLevel() >= 2);
	const int iLandPlots = std::max(1, GC.getMap().getLandPlots());
	const int iGamePopulation = std::max(1, kGame.getTotalPopulation());
	const int iTechs = kTeam.getTechCount();
	const int iLand = kTeam.getTotalLand();
	const int iLandPctX100 = (10000 * iLand) / iLandPlots;
	const int iPopulation = kTeam.getTotalPopulation();
	const int iPopPctX100 = (10000 * iPopulation) / iGamePopulation;
	SASGameRecordTeamPrevious& kPrevious = g_akSASGameRecordTeamPrevious[eTeam];
	TeamTypes const eMaster = (kTeam.isAVassal() ? kTeam.getMasterTeam() : NO_TEAM);
	logSASGameRecord("GAME_RECORD_TEAM turn=%d team=%d members=%s alive=%d deltaValid=%d techs=%d techsDelta=%+d techEraCounts=%s techTrading=%d goldTrading=%d land=%d landDelta=%+d landPctX100=%d landPctX100Delta=%+d pop=%d popDelta=%+d popPctX100=%d popPctX100Delta=%+d wars=%s vassals=%s master=%d",
			iGameTurn, eTeam, getSASGameRecordTeamMembers(eTeam).GetCString(), kTeam.isAlive(), kPrevious.bValid,
			iTechs, getSASGameRecordDelta(kPrevious.bValid, iTechs, kPrevious.iTechs), getSASGameRecordTechEraCounts(eTeam).GetCString(), kTeam.isTechTrading(), kTeam.isGoldTrading(),
			iLand, getSASGameRecordDelta(kPrevious.bValid, iLand, kPrevious.iLand), iLandPctX100, getSASGameRecordDelta(kPrevious.bValid, iLandPctX100, kPrevious.iLandPctX100),
			iPopulation, getSASGameRecordDelta(kPrevious.bValid, iPopulation, kPrevious.iPopulation), iPopPctX100, getSASGameRecordDelta(kPrevious.bValid, iPopPctX100, kPrevious.iPopPctX100),
			getSASGameRecordWarTeams(eTeam).GetCString(), getSASGameRecordVassalTeams(eTeam).GetCString(), eMaster);
	if (bLogTeamDetails) logSASGameRecordTeamContacts(eTeam, iGameTurn, "snapshot");
	seedSASGameRecordTeamPreviousFromCurrentState(eTeam);
}

static bool isSASGameRecordMilitaryUnit(CvUnit const& kUnit)
{
	// <!-- custom: A failed NO_UNIT creation left an unplaced/reset object in the owner container, and the end-turn snapshot crashed while reading its combat state. Unplaced units are not part of military posture; short-circuit before unit-info-backed checks. See KI#524.6. (GPT-5.6-Sol) -->
	CvPlot const* pPlot = kUnit.plot();
	return pPlot != NULL && (kUnit.canDefend(pPlot) || kUnit.baseCombatStr() > 0 || kUnit.airBaseCombatStr() > 0);
}

static CvString getSASGameRecordCommercePercents(CvPlayer const& kPlayer)
{
	CvString szList;
	FOR_EACH_ENUM(Commerce)
	{
		CvString szItem;
		szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", GC.getInfo(eLoopCommerce).getType(), kPlayer.getCommercePercent(eLoopCommerce));
		szList += szItem;
	}
	return getSASDiagnosticOrDash(szList);
}

static CvString getSASGameRecordCommerceRates(CvPlayer const& kPlayer)
{
	CvString szList;
	FOR_EACH_ENUM(Commerce)
	{
		CvString szItem;
		szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", GC.getInfo(eLoopCommerce).getType(), kPlayer.getCommerceRate(eLoopCommerce));
		szList += szItem;
	}
	return getSASDiagnosticOrDash(szList);
}

static CvString getSASGameRecordCommerceFlexible(CvPlayer const& kPlayer)
{
	CvString szList;
	FOR_EACH_ENUM(Commerce)
	{
		CvString szItem;
		szItem.Format(szList.empty() ? "%s:%d" : ",%s:%d", GC.getInfo(eLoopCommerce).getType(), kPlayer.isCommerceFlexible(eLoopCommerce));
		szList += szItem;
	}
	return getSASDiagnosticOrDash(szList);
}

static void logSASGameRecordEconomy(PlayerTypes ePlayer, int iGameTurn)
{
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvTeam const& kTeam = GET_TEAM(kPlayer.getTeam());
	TechTypes eResearch = kPlayer.getCurrentResearch();
	int const iResearchProgress = (eResearch == NO_TECH ? -1 : kTeam.getResearchProgress(eResearch));
	int const iResearchCost = (eResearch == NO_TECH ? -1 : kTeam.getResearchCost(eResearch));
	// <!-- custom: currentResearch=- does not mean that science is lost: CvPlayer::doResearch stores the nominal research rate as overflow until another technology can be selected.
	// Exact shared progress/cost makes partially researched technologies visible at ordinary snapshots instead of only when completion or redirection happens. (GPT-5.6-Sol + ChatGPT-5.6-Sol) -->
	logSASGameRecord("GAME_RECORD_ECONOMY turn=%d player=%d gold=%d goldRate=%d totalCommerce=%d sliders=%s commerceTypeRates=%s flexible=%s currentResearch=%s currentResearchTeamProgress=%d currentResearchCost=%d researchRate=%d researchOverflow=%d noResearchAvailable=%d researchTurns=%d",
			iGameTurn, ePlayer, kPlayer.getGold(), kPlayer.calculateGoldRate(), kPlayer.calculateTotalYield(YIELD_COMMERCE), getSASGameRecordCommercePercents(kPlayer).GetCString(), getSASGameRecordCommerceRates(kPlayer).GetCString(), getSASGameRecordCommerceFlexible(kPlayer).GetCString(), getSASGameRecordTechType(eResearch), iResearchProgress, iResearchCost, kPlayer.calculateResearchRate(eResearch), kPlayer.getOverflowResearch(), kPlayer.isNoResearchAvailable(), eResearch == NO_TECH ? -1 : kPlayer.getResearchTurnsLeft(eResearch, true));
}

static void logSASGameRecordPlayerSnapshot(PlayerTypes ePlayer, int iGameTurn)
{
	CvGame const& kGame = GC.getGame();
	CvPlayer const& kPlayer = GET_PLAYER(ePlayer);
	CvTeam const& kTeam = GET_TEAM(kPlayer.getTeam());
	TechTypes const eResearch = kPlayer.getCurrentResearch();
	int const iScore = kPlayer.calculateScore();
	int const iCities = kPlayer.getNumCities();
	int const iPopulation = kPlayer.getTotalPopulation();
	int const iLand = kPlayer.getTotalLand();
	int const iUnits = kPlayer.getNumUnits();
	int const iMilitarySupportUnits = kPlayer.getNumMilitaryUnits();
	// <!-- custom: CvPlayer::getNumMilitaryUnits counts XML bMilitarySupport, which can fall sharply when an army upgrades into combat units that intentionally do not pay military support. Count actual combat-capable units with the same predicate used by GAME_RECORD_UNIT_POSTURE, and keep the raw Civ4 counter separately. This scan runs only when a GameRecord player snapshot is already being generated. (ChatGPT-5.6-Sol) -->
	int iCombatUnits = 0;
	int iCombatLoop = 0;
	for (CvUnit const* pLoopUnit = kPlayer.firstUnit(&iCombatLoop); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iCombatLoop))
	{
		if (isSASGameRecordMilitaryUnit(*pLoopUnit)) ++iCombatUnits;
	}
	int const iPower = kPlayer.getPower();
	int const iGold = kPlayer.getGold();
	int const iGoldRate = kPlayer.calculateGoldRate();
	// <!-- custom: Keep nominal science visible when no target is selected because that science becomes stored research overflow rather than disappearing. (GPT-5.6-Sol) -->
	int const iResearchRate = kPlayer.calculateResearchRate(eResearch);
	int const iResearchTurns = (eResearch == NO_TECH ? -1 : kPlayer.getResearchTurnsLeft(eResearch, true));
	int const iHistoryScore = kPlayer.getHistorySafe(PLAYER_HISTORY_SCORE, iGameTurn);
	int const iHistoryEconomy = kPlayer.getHistorySafe(PLAYER_HISTORY_ECONOMY, iGameTurn);
	int const iHistoryIndustry = kPlayer.getHistorySafe(PLAYER_HISTORY_INDUSTRY, iGameTurn);
	int const iHistoryAgriculture = kPlayer.getHistorySafe(PLAYER_HISTORY_AGRICULTURE, iGameTurn);
	int const iHistoryPower = kPlayer.getHistorySafe(PLAYER_HISTORY_POWER, iGameTurn);
	int const iHistoryCulture = kPlayer.getHistorySafe(PLAYER_HISTORY_CULTURE, iGameTurn);
	int const iHistoryEspionage = kPlayer.getHistorySafe(PLAYER_HISTORY_ESPIONAGE, iGameTurn);
	SASGameRecordPlayerPrevious& kPrevious = g_akSASGameRecordPlayerPrevious[ePlayer];
	char const* szCiv = (kPlayer.getCivilizationType() == NO_CIVILIZATION ? "-" : GC.getInfo(kPlayer.getCivilizationType()).getType());
	char const* szLeader = (kPlayer.getLeaderType() == NO_LEADER ? "-" : GC.getInfo(kPlayer.getLeaderType()).getType());
	bool const bCurrentlyHumanControlled = kPlayer.isHuman();
	bool const bAutoplayControlled = kPlayer.isHumanDisabled();
	bool const bHumanSlot = (bCurrentlyHumanControlled || bAutoplayControlled);
	// <!-- custom: Current AdvCiv-SAS also exposes recorder-observed golden-age/anarchy lifetime counters in this row. Their action hooks have not been ported yet, so this slice records authoritative current timers only rather than emitting misleading zero-valued session counters. (ChatGPT-5.6-Sol) -->
	logSASGameRecord("GAME_RECORD_PLAYER turn=%d player=%d team=%d civ=%s leader=%s isHuman=%d humanSlot=%d currentlyHumanControlled=%d autoplayControlled=%d rank=%d deltaValid=%d score=%d scoreDelta=%+d cities=%d citiesDelta=%+d pop=%d popDelta=%+d land=%d landDelta=%+d units=%d unitsDelta=%+d combatUnits=%d combatUnitsDelta=%+d militarySupportUnits=%d militarySupportUnitsDelta=%+d power=%d powerDelta=%+d gold=%d goldDelta=%+d gpt=%d gptDelta=%+d researchRate=%d researchRateDelta=%+d researchPercent=%d currentResearch=%s researchOverflow=%d noResearchAvailable=%d researchTurns=%d era=%s stateReligion=%s techScorePercent=%d combatXP=%d greatPeopleCreated=%d greatGeneralsCreated=%d greatGeneralThreshold=%d goldenAgeTurns=%d anarchyTurns=%d revolutionTimer=%d conversionTimer=%d wars=%s",
			iGameTurn, ePlayer, kPlayer.getTeam(), szCiv, szLeader, bCurrentlyHumanControlled, bHumanSlot, bCurrentlyHumanControlled, bAutoplayControlled, kGame.getPlayerRank(ePlayer) + 1, kPrevious.bValid,
			iScore, getSASGameRecordDelta(kPrevious.bValid, iScore, kPrevious.iScore), iCities, getSASGameRecordDelta(kPrevious.bValid, iCities, kPrevious.iCities), iPopulation, getSASGameRecordDelta(kPrevious.bValid, iPopulation, kPrevious.iPopulation), iLand, getSASGameRecordDelta(kPrevious.bValid, iLand, kPrevious.iLand),
			iUnits, getSASGameRecordDelta(kPrevious.bValid, iUnits, kPrevious.iUnits), iCombatUnits, getSASGameRecordDelta(kPrevious.bValid, iCombatUnits, kPrevious.iCombatUnits), iMilitarySupportUnits, getSASGameRecordDelta(kPrevious.bValid, iMilitarySupportUnits, kPrevious.iMilitarySupportUnits), iPower, getSASGameRecordDelta(kPrevious.bValid, iPower, kPrevious.iPower), iGold, getSASGameRecordDelta(kPrevious.bValid, iGold, kPrevious.iGold), iGoldRate, getSASGameRecordDelta(kPrevious.bValid, iGoldRate, kPrevious.iGoldRate),
			iResearchRate, getSASGameRecordDelta(kPrevious.bValid, iResearchRate, kPrevious.iResearchRate), kPlayer.getCommercePercent(COMMERCE_RESEARCH), getSASGameRecordTechType(eResearch), kPlayer.getOverflowResearch(), kPlayer.isNoResearchAvailable(), iResearchTurns, getSASGameRecordEraType(kPlayer.getCurrentEra()), getSASGameRecordReligionType(kPlayer.getStateReligion()), kTeam.getBestKnownTechScorePercent(), kPlayer.getCombatExperience(), kPlayer.getGreatPeopleCreated(), kPlayer.getGreatGeneralsCreated(), kPlayer.greatPeopleThreshold(true), kPlayer.getGoldenAgeTurns(), kPlayer.getAnarchyTurns(), kPlayer.getRevolutionTimer(), kPlayer.getConversionTimer(), getSASGameRecordWarTeams(kPlayer.getTeam()).GetCString());
	logSASGameRecord("GAME_RECORD_PLAYER_HISTORY turn=%d player=%d deltaValid=%d historyScore=%d historyScoreDelta=%+d historyEconomy=%d historyEconomyDelta=%+d historyIndustry=%d historyIndustryDelta=%+d historyAgriculture=%d historyAgricultureDelta=%+d historyPower=%d historyPowerDelta=%+d historyCulture=%d historyCultureDelta=%+d historyEspionage=%d historyEspionageDelta=%+d",
			iGameTurn, ePlayer, kPrevious.bValid, iHistoryScore, getSASGameRecordDelta(kPrevious.bValid, iHistoryScore, kPrevious.iHistoryScore), iHistoryEconomy, getSASGameRecordDelta(kPrevious.bValid, iHistoryEconomy, kPrevious.iHistoryEconomy), iHistoryIndustry, getSASGameRecordDelta(kPrevious.bValid, iHistoryIndustry, kPrevious.iHistoryIndustry), iHistoryAgriculture, getSASGameRecordDelta(kPrevious.bValid, iHistoryAgriculture, kPrevious.iHistoryAgriculture), iHistoryPower, getSASGameRecordDelta(kPrevious.bValid, iHistoryPower, kPrevious.iHistoryPower), iHistoryCulture, getSASGameRecordDelta(kPrevious.bValid, iHistoryCulture, kPrevious.iHistoryCulture), iHistoryEspionage, getSASGameRecordDelta(kPrevious.bValid, iHistoryEspionage, kPrevious.iHistoryEspionage));
	if (getSASGameRecordLogLevel() >= 2)
		logSASGameRecordEconomy(ePlayer, iGameTurn);
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
	kPrevious.iHistoryScore = iHistoryScore;
	kPrevious.iHistoryEconomy = iHistoryEconomy;
	kPrevious.iHistoryIndustry = iHistoryIndustry;
	kPrevious.iHistoryAgriculture = iHistoryAgriculture;
	kPrevious.iHistoryPower = iHistoryPower;
	kPrevious.iHistoryCulture = iHistoryCulture;
	kPrevious.iHistoryEspionage = iHistoryEspionage;
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
// Seed periodic team/contact deltas from this same finalized baseline.
// Group identical technology sets so a late-era start does not repeat the same long payload for every team; the explicit team lists keep arbitrary scenarios and mixed/modded setups exact.
// Record surviving initial deals from the same finalized boundary, collapsing only the deterministic Advanced-Start-shaped reciprocal peace matrix already represented by forcePeace team state. (ChatGPT-5.6-Sol + GPT-5.6-Sol) -->
static void logSASGameRecordFinalizedInitialState(int& iTeamStateRows, int& iTechRows, int& iDeals)
{
	iTeamStateRows = 0;
	iTechRows = 0;
	iDeals = 0;
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
		seedSASGameRecordTeamPreviousFromCurrentState(eTeam);
		iTeamStateRows++;
	}
	for (size_t iGroup = 0; iGroup < aTechGroups.size(); iGroup++)
	{
		SASGameRecordInitialTechGroup const& kGroup = aTechGroups[iGroup];
		logSASGameRecord("GAME_RECORD_INITIAL_TEAM_TECHS teams=%s teamCount=%d %s", kGroup.szTeams.GetCString(), kGroup.iTeams, kGroup.szTechFields.GetCString());
		iTechRows++;
	}
	int iLoop = 0;
	for (CvDeal const* pDeal = GC.getGame().firstDeal(&iLoop); pDeal != NULL; pDeal = GC.getGame().nextDeal(&iLoop))
	{
		if (isSASCollapsibleAdvancedStartPeaceDeal(*pDeal))
			continue;
		logSASGameRecord("GAME_RECORD_INITIAL_DEAL %s", getSASInitialDealStateFields(*pDeal).GetCString());
		iDeals++;
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

static void logSASGameRecordSnapshot(int iGameTurn, char const* szReason)
{
	CvGame const& kGame = GC.getGame();
	logSASGameRecord("GAME_RECORD_TURN_BEGIN turn=%d reason=%s elapsed=%d year=%d playersAlive=%d teamsAlive=%d totalCities=%d totalPopulation=%d",
			iGameTurn, szReason, kGame.getElapsedGameTurns(), kGame.getGameTurnYear(), kGame.countCivPlayersAlive(), kGame.countCivTeamsAlive(), kGame.getNumCities(), kGame.getTotalPopulation());
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		TeamTypes eLoopTeam = (TeamTypes)iI;
		if (GET_TEAM(eLoopTeam).isAlive() && !GET_TEAM(eLoopTeam).isBarbarian())
			logSASGameRecordTeamSnapshot(eLoopTeam, iGameTurn);
	}
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		PlayerTypes eLoopPlayer = (PlayerTypes)iI;
		if (GET_PLAYER(eLoopPlayer).isAlive() && !GET_PLAYER(eLoopPlayer).isBarbarian())
			logSASGameRecordPlayerSnapshot(eLoopPlayer, iGameTurn);
	}
	logSASGameRecord("GAME_RECORD_TURN_END turn=%d reason=%s", iGameTurn, szReason);
}

void logSASGameRecordTurn(int iGameTurn)
{
	logSASGameRecordSnapshot(iGameTurn, "interval");
}

void startSASGameRecordLogForNewGame()
{
	rollSASGameRecordLog("new");
	resetSASGameRecordTeamPrevious();
	resetSASGameRecordPlayerPrevious();
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
		int iDeals = 0;
		logSASGameRecordFinalizedInitialState(iTeamStateRows, iTechRows, iDeals);
		logSASGameRecord("GAME_RECORD_INITIAL_STATE_SUMMARY teamStateRows=%d techGroupRows=%d techTeamsCovered=%d %s source=FINALIZED_STATE", iTeamStateRows, iTechRows, iTeamStateRows, getSASInitialDealSummaryFields(true, iDeals).GetCString());
	}
}

void startSASGameRecordLogForLoadedSave()
{
	rollSASGameRecordLog("load");
	resetSASGameRecordTeamPrevious();
	resetSASGameRecordPlayerPrevious();
	logSASGameRecordGameState("GAME_RECORD_SAVE_LOADED");
	logSASGameRecordLogSettings();
	logSASGameRecordTechCapabilitySources();
	logSASGameRecordInitialPlayerIdentities();
	// <!-- custom: Level-2+ new games already emitted authoritative INITIAL_TEAM_STATE metTeams and seeded the contact baseline.
	// Loaded saves have no finalized initial-team block in this session, so retain explicit setup contact rows for them. (ChatGPT-5.6-Sol) -->
	if (getSASGameRecordLogLevel() >= 2)
	{
		for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
		{
			TeamTypes eLoopTeam = (TeamTypes)iI;
			if (GET_TEAM(eLoopTeam).isAlive() && !GET_TEAM(eLoopTeam).isBarbarian())
				logSASGameRecordTeamContacts(eLoopTeam, GC.getGame().getGameTurn(), "setup");
		}
	}
}


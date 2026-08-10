#include "CvGameCoreDLL.h"
#include "CvGameCoreUtils.h"
#include "CoreAI.h"
#include "CvUnitAI.h"
#include "CvSelectionGroupAI.h"
#include "CityPlotIterator.h"
#include "BBAILog.h" // advc.007
#include "CvInfo_GameOption.h"
#include "CvInfo_Building.h" // <!-- custom: getSASTeamSpaceshipPartsBuilt needs CvProjectInfo::isSpaceship for Space-victory denial checks. (GPT-5.5) -->

// advc.035:
void contestedPlots(std::vector<CvPlot*>& r, TeamTypes t1, TeamTypes t2)
{
	if(!GC.getDefineBOOL(CvGlobals::OWN_EXCLUSIVE_RADIUS))
		return;
	// Sufficient to check plots around the teams' cities
	std::vector<CvCity const*> apCities;
	for (MemberIter itMember1(t1); itMember1.hasNext(); ++itMember1)
	{
		FOR_EACH_CITY(c, *itMember1)
			apCities.push_back(c);
	}
	for (MemberIter itMember2(t2); itMember2.hasNext(); ++itMember2)
	{
		FOR_EACH_CITY(c, *itMember2)
			apCities.push_back(c);
	}
	std::set<int> seenPlots; // To avoid duplicates
	for(size_t i = 0; i < apCities.size(); i++)
	{
		CvCity const& c = *apCities[i];
		for(CityPlotIter it(c, false); it.hasNext(); ++it)
		{
			CvPlot& p = *it;
			if(p.isCity())
				continue;
			PlayerTypes eSecondOwner = p.getSecondOwner();
			PlayerTypes eOwner = p.getOwner();
			if(eOwner == NO_PLAYER || eSecondOwner == NO_PLAYER)
				continue;
			TeamTypes eTeam = TEAMID(eOwner);
			TeamTypes eSecondTeam = TEAMID(eSecondOwner);
			if(eTeam == eSecondTeam)
				continue;
			if((eTeam == t1 && eSecondTeam == t2) || (eTeam == t2 && eSecondTeam == t1))
			{
				int iPlotID = p.getX() * 1000 + p.getY();
				if(seenPlots.count(iPlotID) <= 0)
				{
					seenPlots.insert(iPlotID);
					r.push_back(&p);
				}
			}
		}
	}
} 
// advc.004w: I'm not positive that there isn't already a function like this somewhere
void applyColorToString(CvWString& s, char const* szColor, bool bLink)
{
	if(bLink)
		s.Format(L"<link=literal>%s</link>", s.GetCString());
	s.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR(szColor), s.GetCString());
}

// advc.002i: Formula by T. Riemersma (CompuPhase.com) via Wikipedia ("Color difference")
float colorDifference(NiColorA const& c1, NiColorA const& c2)
{
	float channelWeights[] = { 2, 4, 3 }; // R, G, B
	if (c1.r + c2.r > 1)
		std::swap(channelWeights[0], channelWeights[2]);
	float fDiff = 0;
	fDiff += SQR(c1.r - c2.r) * channelWeights[0];
	fDiff += SQR(c1.g - c2.g) * channelWeights[1];
	fDiff += SQR(c1.b - c2.b) * channelWeights[2];
	return fDiff;
}

// <!-- custom: iDifficulty is a score/rating in XML, not always enum index * 10 after AdvCiv-SAS adds Rookie and Deity+. (ChatGPT-5.5) -->
HandicapTypes handicapFromDifficulty(int iDifficulty)
{
	static const HandicapTypes eSTANDARD_HANDICAP = (HandicapTypes)GC.getDefineINT("STANDARD_HANDICAP");
	HandicapTypes eBestHandicap = NO_HANDICAP;
	int iBestDelta = MAX_INT;
	for (int i = 0; i < GC.getNumHandicapInfos(); i++)
	{
		HandicapTypes const eLoopHandicap = (HandicapTypes)i;
		int const iDelta = std::abs(GC.getInfo(eLoopHandicap).getDifficulty() - iDifficulty);
		if (iDelta < iBestDelta)
		{
			iBestDelta = iDelta;
			eBestHandicap = eLoopHandicap;
		}
	}
	FAssert(eBestHandicap != NO_HANDICAP);
	return (eBestHandicap == NO_HANDICAP ? eSTANDARD_HANDICAP : eBestHandicap);
}

DirectionTypes cardinalDirectionToDirection(CardinalDirectionTypes eCard)
{
	switch (eCard)
	{
	case CARDINALDIRECTION_NORTH:
		return DIRECTION_NORTH;
	case CARDINALDIRECTION_EAST:
		return DIRECTION_EAST;
	case CARDINALDIRECTION_SOUTH:
		return DIRECTION_SOUTH;
	case CARDINALDIRECTION_WEST:
		return DIRECTION_WEST;
	}
	return NO_DIRECTION;
}

DirectionTypes estimateDirection(int iDX, int iDY)
{
	const int displacementSize = 8;
	static float sqrt2 = 1 / sqrt(2.0f);
	//													N			NE			E			SE				S			SW				W			NW
	static float displacements[displacementSize][2] = {{0, 1}, {sqrt2, sqrt2}, {1, 0}, {sqrt2, -sqrt2}, {0, -1}, {-sqrt2, -sqrt2}, {-1, 0}, {-sqrt2, sqrt2}};
	float maximum = 0;
	int maximumIndex = -1;
	for(int i=0;i<displacementSize;i++)
	{
		float dotProduct = iDX * displacements[i][0] + iDY * displacements[i][1];
		if(dotProduct > maximum)
		{
			maximum = dotProduct;
			maximumIndex = i;
		}
	}

	return (DirectionTypes) maximumIndex;
}

DirectionTypes estimateDirection(const CvPlot* pFromPlot, const CvPlot* pToPlot)
{
	CvMap const& m = GC.getMap();
	return estimateDirection(
			m.dxWrap(pToPlot->getX() - pFromPlot->getX()),
			m.dyWrap(pToPlot->getY() - pFromPlot->getY()));
}

/*	advc: Cut from CvXMLLoadUtility.cpp, renamed
	from "CreateHotKeyFromDescription"; nothing is "created" here. */
CvWString hotkeyDescr::hotKeyFromDescription(TCHAR const* szDescr, bool bShift, bool bAlt, bool bCtrl)
{
	// Example: "Delete <COLOR:140,255,40,255>Shift+Delete</COLOR>"
	CvWString szHotKey;
	if (szDescr != NULL && strcmp(szDescr, "") != 0)
	{
		szHotKey += L" <color=140,255,40,255>";
		szHotKey += L"&lt;";

		if (bShift)
			szHotKey += gDLL->getText("TXT_KEY_SHIFT");

		if (bAlt)
			szHotKey += gDLL->getText("TXT_KEY_ALT");

		if (bCtrl)
			szHotKey += gDLL->getText("TXT_KEY_CTRL");

		szHotKey += keyStringFromKBCode(szDescr);
		szHotKey += L">";
		szHotKey += L"</color>";
	}
	return szHotKey;
}

// KB code to string; e.g. KB_DELETE -> "Delete"
// advc: Cut from CvXMLLoadUtility.cpp, renamed from "CreateKeyStringFromKBCode".
CvWString hotkeyDescr::keyStringFromKBCode(TCHAR const* szDescr)
{
	PROFILE_FUNC();

	struct CvKeyBoardMapping
	{
		TCHAR szDefineString[25];
		CvWString szKeyString;
	};

	// TODO - this should be a stl map instead of looping strcmp
	const int iNumKeyBoardMappings=108;
	const CvKeyBoardMapping asCvKeyBoardMapping[iNumKeyBoardMappings] =
	{
		{"KB_ESCAPE", gDLL->getText("TXT_KEY_KEYBOARD_ESCAPE")},
		{"KB_0","0"},
		{"KB_1","1"},
		{"KB_2","2"},
		{"KB_3","3"},
		{"KB_4","4"},
		{"KB_5","5"},
		{"KB_6","6"},
		{"KB_7","7"},
		{"KB_8","8"},
		{"KB_9","9"},
		{"KB_MINUS","-"},	    /* - on main keyboard */
		{"KB_A","A"},
		{"KB_B","B"},
		{"KB_C","C"},
		{"KB_D","D"},
		{"KB_E","E"},
		{"KB_F","F"},
		{"KB_G","G"},
		{"KB_H","H"},
		{"KB_I","I"},
		{"KB_J","J"},
		{"KB_K","K"},
		{"KB_L","L"},
		{"KB_M","M"},
		{"KB_N","N"},
		{"KB_O","O"},
		{"KB_P","P"},
		{"KB_Q","Q"},
		{"KB_R","R"},
		{"KB_S","S"},
		{"KB_T","T"},
		{"KB_U","U"},
		{"KB_V","V"},
		{"KB_W","W"},
		{"KB_X","X"},
		{"KB_Y","Y"},
		{"KB_Z","Z"},
		{"KB_EQUALS","="},
		{"KB_BACKSPACE",gDLL->getText("TXT_KEY_KEYBOARD_BACKSPACE")},
		{"KB_TAB","TAB"},
		{"KB_LBRACKET","["},
		{"KB_RBRACKET","]"},
		{"KB_RETURN",gDLL->getText("TXT_KEY_KEYBOARD_ENTER")},		/* Enter on main keyboard */
		{"KB_LCONTROL",gDLL->getText("TXT_KEY_KEYBOARD_LEFT_CONTROL_KEY")},
		{"KB_SEMICOLON",";"},
		{"KB_APOSTROPHE","'"},
		{"KB_GRAVE","`"},		/* accent grave */
		{"KB_LSHIFT",gDLL->getText("TXT_KEY_KEYBOARD_LEFT_SHIFT_KEY")},
		{"KB_BACKSLASH","\\"},
		{"KB_COMMA",","},
		{"KB_PERIOD","."},
		{"KB_SLASH","/"},
		{"KB_RSHIFT",gDLL->getText("TXT_KEY_KEYBOARD_RIGHT_SHIFT_KEY")},
		{"KB_NUMPADSTAR",gDLL->getText("TXT_KEY_KEYBOARD_NUM_PAD_STAR")},
		{"KB_LALT",gDLL->getText("TXT_KEY_KEYBOARD_LEFT_ALT_KEY")},
		{"KB_SPACE",gDLL->getText("TXT_KEY_KEYBOARD_SPACE_KEY")},
		{"KB_CAPSLOCK",gDLL->getText("TXT_KEY_KEYBOARD_CAPS_LOCK")},
		{"KB_F1","F1"},
		{"KB_F2","F2"},
		{"KB_F3","F3"},
		{"KB_F4","F4"},
		{"KB_F5","F5"},
		{"KB_F6","F6"},
		{"KB_F7","F7"},
		{"KB_F8","F8"},
		{"KB_F9","F9"},
		{"KB_F10","F10"},
		{"KB_NUMLOCK",gDLL->getText("TXT_KEY_KEYBOARD_NUM_LOCK")},
		{"KB_SCROLL",gDLL->getText("TXT_KEY_KEYBOARD_SCROLL_KEY")},
		{"KB_NUMPAD7",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 7)},
		{"KB_NUMPAD8",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 8)},
		{"KB_NUMPAD9",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 9)},
		{"KB_NUMPADMINUS",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_MINUS")},
		{"KB_NUMPAD4",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 4)},
		{"KB_NUMPAD5",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 5)},
		{"KB_NUMPAD6",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 6)},
		{"KB_NUMPADPLUS",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_PLUS")},
		{"KB_NUMPAD1",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 1)},
		{"KB_NUMPAD2",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 2)},
		{"KB_NUMPAD3",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 3)},
		{"KB_NUMPAD0",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_NUMBER", 0)},
		{"KB_NUMPADPERIOD",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_PERIOD")},
		{"KB_F11","F11"},
		{"KB_F12","F12"},
		{"KB_NUMPADEQUALS",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_EQUALS")},
		{"KB_AT","@"},
		{"KB_UNDERLINE","_"},
		{"KB_COLON",":"},
		{"KB_NUMPADENTER",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_ENTER_KEY")},
		{"KB_RCONTROL",gDLL->getText("TXT_KEY_KEYBOARD_RIGHT_CONTROL_KEY")},
		{"KB_VOLUMEDOWN",gDLL->getText("TXT_KEY_KEYBOARD_VOLUME_DOWN")},
		{"KB_VOLUMEUP",gDLL->getText("TXT_KEY_KEYBOARD_VOLUME_UP")},
		{"KB_NUMPADCOMMA",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_COMMA")},
		{"KB_NUMPADSLASH",gDLL->getText("TXT_KEY_KEYBOARD_NUMPAD_SLASH")},
		{"KB_SYSRQ",gDLL->getText("TXT_KEY_KEYBOARD_SYSRQ")},
		{"KB_RALT",gDLL->getText("TXT_KEY_KEYBOARD_RIGHT_ALT_KEY")},
		{"KB_PAUSE",gDLL->getText("TXT_KEY_KEYBOARD_PAUSE_KEY")},
		{"KB_HOME",gDLL->getText("TXT_KEY_KEYBOARD_HOME_KEY")},
		{"KB_UP",gDLL->getText("TXT_KEY_KEYBOARD_UP_ARROW")},
		{"KB_PGUP",gDLL->getText("TXT_KEY_KEYBOARD_PAGE_UP")},
		{"KB_LEFT",gDLL->getText("TXT_KEY_KEYBOARD_LEFT_ARROW")},
		{"KB_RIGHT",gDLL->getText("TXT_KEY_KEYBOARD_RIGHT_ARROW")},
		{"KB_END",gDLL->getText("TXT_KEY_KEYBOARD_END_KEY")},
		{"KB_DOWN",gDLL->getText("TXT_KEY_KEYBOARD_DOWN_ARROW")},
		{"KB_PGDN",gDLL->getText("TXT_KEY_KEYBOARD_PAGE_DOWN")},
		{"KB_INSERT",gDLL->getText("TXT_KEY_KEYBOARD_INSERT_KEY")},
		{"KB_DELETE",gDLL->getText("TXT_KEY_KEYBOARD_DELETE_KEY")},
	};

	for (int i = 0; i < iNumKeyBoardMappings; i++)
	{
		if (strcmp(asCvKeyBoardMapping[i].szDefineString, szDescr) == 0)
			return asCvKeyBoardMapping[i].szKeyString;
	}

	return "";
}


bool atWar(TeamTypes eTeamA, TeamTypes eTeamB)
{
	return (eTeamA != NO_TEAM && eTeamB != NO_TEAM && GET_TEAM(eTeamA).isAtWar(eTeamB));
}

char const* getSASDiploEventType(DiploEventTypes eDiploEvent)
{
	switch (eDiploEvent)
	{
	case DIPLOEVENT_CONTACT: return "DIPLOEVENT_CONTACT";
	case DIPLOEVENT_AI_CONTACT: return "DIPLOEVENT_AI_CONTACT";
	case DIPLOEVENT_FAILED_CONTACT: return "DIPLOEVENT_FAILED_CONTACT";
	case DIPLOEVENT_GIVE_HELP: return "DIPLOEVENT_GIVE_HELP";
	case DIPLOEVENT_REFUSED_HELP: return "DIPLOEVENT_REFUSED_HELP";
	case DIPLOEVENT_ACCEPT_DEMAND: return "DIPLOEVENT_ACCEPT_DEMAND";
	case DIPLOEVENT_REJECTED_DEMAND: return "DIPLOEVENT_REJECTED_DEMAND";
	case DIPLOEVENT_DEMAND_WAR: return "DIPLOEVENT_DEMAND_WAR";
	case DIPLOEVENT_CONVERT: return "DIPLOEVENT_CONVERT";
	case DIPLOEVENT_NO_CONVERT: return "DIPLOEVENT_NO_CONVERT";
	case DIPLOEVENT_REVOLUTION: return "DIPLOEVENT_REVOLUTION";
	case DIPLOEVENT_NO_REVOLUTION: return "DIPLOEVENT_NO_REVOLUTION";
	case DIPLOEVENT_JOIN_WAR: return "DIPLOEVENT_JOIN_WAR";
	case DIPLOEVENT_NO_JOIN_WAR: return "DIPLOEVENT_NO_JOIN_WAR";
	case DIPLOEVENT_STOP_TRADING: return "DIPLOEVENT_STOP_TRADING";
	case DIPLOEVENT_NO_STOP_TRADING: return "DIPLOEVENT_NO_STOP_TRADING";
	case DIPLOEVENT_ASK_HELP: return "DIPLOEVENT_ASK_HELP";
	case DIPLOEVENT_MADE_DEMAND: return "DIPLOEVENT_MADE_DEMAND";
	case DIPLOEVENT_RESEARCH_TECH: return "DIPLOEVENT_RESEARCH_TECH";
	case DIPLOEVENT_TARGET_CITY: return "DIPLOEVENT_TARGET_CITY";
	case DIPLOEVENT_MADE_DEMAND_VASSAL: return "DIPLOEVENT_MADE_DEMAND_VASSAL";
	case DIPLOEVENT_SET_WARPLAN: return "DIPLOEVENT_SET_WARPLAN";
	default: return "UNKNOWN_DIPLOEVENT";
	}
}

char const* getSASMemoryType(MemoryTypes eMemory)
{
	switch (eMemory)
	{
	case MEMORY_DECLARED_WAR: return "MEMORY_DECLARED_WAR";
	case MEMORY_DECLARED_WAR_ON_FRIEND: return "MEMORY_DECLARED_WAR_ON_FRIEND";
	case MEMORY_HIRED_WAR_ALLY: return "MEMORY_HIRED_WAR_ALLY";
	case MEMORY_NUKED_US: return "MEMORY_NUKED_US";
	case MEMORY_NUKED_FRIEND: return "MEMORY_NUKED_FRIEND";
	case MEMORY_RAZED_CITY: return "MEMORY_RAZED_CITY";
	case MEMORY_RAZED_HOLY_CITY: return "MEMORY_RAZED_HOLY_CITY";
	case MEMORY_SPY_CAUGHT: return "MEMORY_SPY_CAUGHT";
	case MEMORY_GIVE_HELP: return "MEMORY_GIVE_HELP";
	case MEMORY_REFUSED_HELP: return "MEMORY_REFUSED_HELP";
	case MEMORY_ACCEPT_DEMAND: return "MEMORY_ACCEPT_DEMAND";
	case MEMORY_REJECTED_DEMAND: return "MEMORY_REJECTED_DEMAND";
	case MEMORY_ACCEPTED_RELIGION: return "MEMORY_ACCEPTED_RELIGION";
	case MEMORY_DENIED_RELIGION: return "MEMORY_DENIED_RELIGION";
	case MEMORY_ACCEPTED_CIVIC: return "MEMORY_ACCEPTED_CIVIC";
	case MEMORY_DENIED_CIVIC: return "MEMORY_DENIED_CIVIC";
	case MEMORY_ACCEPTED_JOIN_WAR: return "MEMORY_ACCEPTED_JOIN_WAR";
	case MEMORY_DENIED_JOIN_WAR: return "MEMORY_DENIED_JOIN_WAR";
	case MEMORY_ACCEPTED_STOP_TRADING: return "MEMORY_ACCEPTED_STOP_TRADING";
	case MEMORY_DENIED_STOP_TRADING: return "MEMORY_DENIED_STOP_TRADING";
	case MEMORY_STOPPED_TRADING: return "MEMORY_STOPPED_TRADING";
	case MEMORY_STOPPED_TRADING_RECENT: return "MEMORY_STOPPED_TRADING_RECENT";
	case MEMORY_HIRED_TRADE_EMBARGO: return "MEMORY_HIRED_TRADE_EMBARGO";
	case MEMORY_MADE_DEMAND: return "MEMORY_MADE_DEMAND";
	case MEMORY_CANCELLED_VASSAL_AGREEMENT: return "MEMORY_CANCELLED_VASSAL_AGREEMENT";
	case MEMORY_MADE_DEMAND_RECENT: return "MEMORY_MADE_DEMAND_RECENT";
	case MEMORY_CANCELLED_OPEN_BORDERS: return "MEMORY_CANCELLED_OPEN_BORDERS";
	case MEMORY_CANCELLED_DEFENSIVE_PACT: return "MEMORY_CANCELLED_DEFENSIVE_PACT";
	case MEMORY_TRADED_TECH_TO_US: return "MEMORY_TRADED_TECH_TO_US";
	case MEMORY_RECEIVED_TECH_FROM_ANY: return "MEMORY_RECEIVED_TECH_FROM_ANY";
	case MEMORY_VOTED_AGAINST_US: return "MEMORY_VOTED_AGAINST_US";
	case MEMORY_VOTED_FOR_US: return "MEMORY_VOTED_FOR_US";
	case MEMORY_EVENT_GOOD_TO_US: return "MEMORY_EVENT_GOOD_TO_US";
	case MEMORY_EVENT_BAD_TO_US: return "MEMORY_EVENT_BAD_TO_US";
	case MEMORY_LIBERATED_CITIES: return "MEMORY_LIBERATED_CITIES";
	case MEMORY_INDEPENDENCE: return "MEMORY_INDEPENDENCE";
	case MEMORY_DECLARED_WAR_RECENT: return "MEMORY_DECLARED_WAR_RECENT";
	default: return "UNKNOWN_MEMORY";
	}
}

char const* getSASTradeItemType(TradeableItems eItem)
{
	switch (eItem)
	{
	case NO_TRADE_ITEM: return "-";
	case TRADE_GOLD: return "TRADE_GOLD";
	case TRADE_GOLD_PER_TURN: return "TRADE_GOLD_PER_TURN";
	case TRADE_MAPS: return "TRADE_MAPS";
	case TRADE_VASSAL: return "TRADE_VASSAL";
	case TRADE_SURRENDER: return "TRADE_SURRENDER";
	case TRADE_OPEN_BORDERS: return "TRADE_OPEN_BORDERS";
	case TRADE_DEFENSIVE_PACT: return "TRADE_DEFENSIVE_PACT";
	case TRADE_PERMANENT_ALLIANCE: return "TRADE_PERMANENT_ALLIANCE";
	case TRADE_PEACE_TREATY: return "TRADE_PEACE_TREATY";
	case TRADE_TECHNOLOGIES: return "TRADE_TECHNOLOGIES";
	case TRADE_RESOURCES: return "TRADE_RESOURCES";
	case TRADE_CITIES: return "TRADE_CITIES";
	case TRADE_PEACE: return "TRADE_PEACE";
	case TRADE_WAR: return "TRADE_WAR";
	case TRADE_EMBARGO: return "TRADE_EMBARGO";
	case TRADE_CIVIC: return "TRADE_CIVIC";
	case TRADE_RELIGION: return "TRADE_RELIGION";
	case TRADE_DISENGAGE: return "TRADE_DISENGAGE";
	default: return "UNKNOWN_TRADE_ITEM";
	}
}

char const* getSASWarPlanType(WarPlanTypes eWarPlan)
{
	switch (eWarPlan)
	{
	case NO_WARPLAN: return "NO_WARPLAN";
	case WARPLAN_ATTACKED_RECENT: return "WARPLAN_ATTACKED_RECENT";
	case WARPLAN_ATTACKED: return "WARPLAN_ATTACKED";
	case WARPLAN_PREPARING_LIMITED: return "WARPLAN_PREPARING_LIMITED";
	case WARPLAN_PREPARING_TOTAL: return "WARPLAN_PREPARING_TOTAL";
	case WARPLAN_LIMITED: return "WARPLAN_LIMITED";
	case WARPLAN_TOTAL: return "WARPLAN_TOTAL";
	case WARPLAN_DOGPILE: return "WARPLAN_DOGPILE";
	default: return "UNKNOWN_WARPLAN";
	}
}

char const* getSASGameType(GameType eType)
{
	switch (eType)
	{
	case GAME_NONE: return "GAME_NONE";
	case GAME_SP_NEW: return "GAME_SP_NEW";
	case GAME_SP_SCENARIO: return "GAME_SP_SCENARIO";
	case GAME_SP_LOAD: return "GAME_SP_LOAD";
	case GAME_MP_NEW: return "GAME_MP_NEW";
	case GAME_MP_SCENARIO: return "GAME_MP_SCENARIO";
	case GAME_MP_LOAD: return "GAME_MP_LOAD";
	case GAME_HOTSEAT_NEW: return "GAME_HOTSEAT_NEW";
	case GAME_HOTSEAT_SCENARIO: return "GAME_HOTSEAT_SCENARIO";
	case GAME_HOTSEAT_LOAD: return "GAME_HOTSEAT_LOAD";
	case GAME_PBEM_NEW: return "GAME_PBEM_NEW";
	case GAME_PBEM_SCENARIO: return "GAME_PBEM_SCENARIO";
	case GAME_PBEM_LOAD: return "GAME_PBEM_LOAD";
	case GAME_REPLAY: return "GAME_REPLAY";
	default: return "UNKNOWN_GAME_TYPE";
	}
}

char const* getSASGameMode(GameMode eMode)
{
	switch (eMode)
	{
	case NO_GAMEMODE: return "NO_GAMEMODE";
	case GAMEMODE_NORMAL: return "GAMEMODE_NORMAL";
	case GAMEMODE_PITBOSS: return "GAMEMODE_PITBOSS";
	default: return "UNKNOWN_GAME_MODE";
	}
}

char const* getSASWarDeclarationCause(WarDeclarationCause eCause)
{
	switch (eCause)
	{
	case WAR_DECLARATION_DIRECT: return "DIRECT";
	case WAR_DECLARATION_GAME_SETUP: return "GAME_SETUP";
	case WAR_DECLARATION_ALWAYS_WAR: return "ALWAYS_WAR";
	case WAR_DECLARATION_PERMANENT_ALLIANCE: return "PERMANENT_ALLIANCE";
	case WAR_DECLARATION_DEFENSIVE_PACT: return "DEFENSIVE_PACT";
	case WAR_DECLARATION_VASSAL_ALIGNMENT: return "VASSAL_ALIGNMENT";
	case WAR_DECLARATION_DIPLOMACY: return "DIPLOMACY";
	case WAR_DECLARATION_VOTE: return "DIPLOMATIC_VOTE";
	case WAR_DECLARATION_NUCLEAR_ATTACK: return "NUCLEAR_ATTACK";
	default: return "UNKNOWN";
	}
}

char const* getSASTechAcquisitionCause(TechAcquisitionCause eCause)
{
	switch (eCause)
	{
	case TECH_ACQUISITION_RESEARCH: return "RESEARCH";
	case TECH_ACQUISITION_TRADE: return "TRADE";
	case TECH_ACQUISITION_FREE_CHOICE: return "FREE_CHOICE";
	case TECH_ACQUISITION_GOODY: return "GOODY";
	case TECH_ACQUISITION_GREAT_PERSON: return "GREAT_PERSON";
	case TECH_ACQUISITION_ESPIONAGE: return "ESPIONAGE";
	case TECH_ACQUISITION_RANDOM_EVENT: return "RANDOM_EVENT";
	case TECH_ACQUISITION_TECH_SHARE: return "TECH_SHARE";
	case TECH_ACQUISITION_TEAM_MERGE: return "TEAM_MERGE";
	case TECH_ACQUISITION_INHERITANCE: return "INHERITANCE";
	case TECH_ACQUISITION_ADVANCED_START: return "ADVANCED_START";
	case TECH_ACQUISITION_BARBARIAN_RESEARCH: return "BARBARIAN_RESEARCH";
	case TECH_ACQUISITION_GAME_SETUP: return "GAME_SETUP";
	case TECH_ACQUISITION_DEBUG: return "DEBUG";
	default: return "UNKNOWN";
	}
}

// <!-- custom: Victory-stage state is a bitfield; share this helper because BBAI/game-record diagnostics and AI logic all need the same compact 0..4 level without repeating four AI_atVictoryStage-style checks. (GPT-5.5) -->
int getSASVictoryStageLevel(AIVictoryStage eVictoryStageHash, AIVictoryStage eStage1, AIVictoryStage eStage2, AIVictoryStage eStage3, AIVictoryStage eStage4)
{
	if ((eVictoryStageHash & eStage4) != 0)
		return 4;
	if ((eVictoryStageHash & eStage3) != 0)
		return 3;
	if ((eVictoryStageHash & eStage2) != 0)
		return 2;
	if ((eVictoryStageHash & eStage1) != 0)
		return 1;
	return 0;
}

int getSASCultureVictoryStageLevel(AIVictoryStage eVictoryStageHash) { return getSASVictoryStageLevel(eVictoryStageHash, AI_VICTORY_CULTURE1, AI_VICTORY_CULTURE2, AI_VICTORY_CULTURE3, AI_VICTORY_CULTURE4); }
int getSASSpaceVictoryStageLevel(AIVictoryStage eVictoryStageHash) { return getSASVictoryStageLevel(eVictoryStageHash, AI_VICTORY_SPACE1, AI_VICTORY_SPACE2, AI_VICTORY_SPACE3, AI_VICTORY_SPACE4); }
int getSASConquestVictoryStageLevel(AIVictoryStage eVictoryStageHash) { return getSASVictoryStageLevel(eVictoryStageHash, AI_VICTORY_CONQUEST1, AI_VICTORY_CONQUEST2, AI_VICTORY_CONQUEST3, AI_VICTORY_CONQUEST4); }
int getSASDominationVictoryStageLevel(AIVictoryStage eVictoryStageHash) { return getSASVictoryStageLevel(eVictoryStageHash, AI_VICTORY_DOMINATION1, AI_VICTORY_DOMINATION2, AI_VICTORY_DOMINATION3, AI_VICTORY_DOMINATION4); }
int getSASDiplomacyVictoryStageLevel(AIVictoryStage eVictoryStageHash) { return getSASVictoryStageLevel(eVictoryStageHash, AI_VICTORY_DIPLOMACY1, AI_VICTORY_DIPLOMACY2, AI_VICTORY_DIPLOMACY3, AI_VICTORY_DIPLOMACY4); }
int getSASTeamMaxVictoryStage(TeamTypes eTeam)
{
	int iMaxVictoryStage = 0;
	for (MemberAIIter it(eTeam); it.hasNext(); ++it)
	{
		AIVictoryStage const eVictoryStageHash = it->AI_getVictoryStageHash();
		int const iMemberMaxVictoryStage = std::max(std::max(getSASCultureVictoryStageLevel(eVictoryStageHash), getSASSpaceVictoryStageLevel(eVictoryStageHash)), std::max(std::max(getSASConquestVictoryStageLevel(eVictoryStageHash), getSASDominationVictoryStageLevel(eVictoryStageHash)), getSASDiplomacyVictoryStageLevel(eVictoryStageHash)));
		iMaxVictoryStage = std::max(iMaxVictoryStage, iMemberMaxVictoryStage);
	}
	return iMaxVictoryStage;
}

int getSASTeamSpaceVictoryStage(TeamTypes eTeam)
{
	int iMaxSpaceStage = 0;
	for (MemberAIIter it(eTeam); it.hasNext(); ++it)
		iMaxSpaceStage = std::max(iMaxSpaceStage, getSASSpaceVictoryStageLevel(it->AI_getVictoryStageHash()));
	return iMaxSpaceStage;
}

int getSASTeamSpaceshipPartsBuilt(TeamTypes eTeam)
{
	int iPartsBuilt = 0;
	CvTeamAI const& kTeam = GET_TEAM(eTeam);
	for (int iProject = 0; iProject < GC.getNumProjectInfos(); iProject++)
	{
		CvProjectInfo const& kProject = GC.getInfo((ProjectTypes)iProject);
		if (kProject.isSpaceship())
			iPartsBuilt += kTeam.getProjectCount((ProjectTypes)iProject);
	}
	return iPartsBuilt;
}

int getSASSpaceshipPartsRequired()
{
	static int iPartsRequired = -1;
	if (iPartsRequired < 0)
	{
		iPartsRequired = 0;
		for (int iProject = 0; iProject < GC.getNumProjectInfos(); iProject++)
		{
			CvProjectInfo const& kProject = GC.getInfo((ProjectTypes)iProject);
			if (kProject.isSpaceship())
				iPartsRequired += std::max(0, kProject.getMaxTeamInstances());
		}
	}
	return iPartsRequired;
}

int getSASTeamSpaceshipPartsPercent(TeamTypes eTeam)
{
	int const iPartsRequired = getSASSpaceshipPartsRequired();
	return (iPartsRequired <= 0 ? 0 : getSASTeamSpaceshipPartsBuilt(eTeam) * 100 / iPartsRequired);
}

// <!-- custom: Victory countdown lengths themselves use VictoryDelayPercent, so SAS countdown gates expressed in Normal-speed turns must use the same scale. Keep the adjusted value per call rather than static so starting a different game speed in the same Civ4 process cannot reuse a stale result. (GPT-5.6 Thinking) -->
int getSASVictoryDelayTurnsFromNormalGameSpeed(int iNormalTurns)
{
	if (iNormalTurns <= 0)
		return 0;
	int const iVictoryDelayPercent = GC.getInfo(GC.getGame().getGameSpeedType()).getVictoryDelayPercent();
	return std::max(1, (iNormalTurns * iVictoryDelayPercent + 50) / 100);
}

int getSASLeadingSpaceshipPartsBuilt()
{
	int iLeadingParts = 0;
	for (TeamIter<CIV_ALIVE> itTeam; itTeam.hasNext(); ++itTeam)
		iLeadingParts = std::max(iLeadingParts, getSASTeamSpaceshipPartsBuilt(itTeam->getID()));
	return iLeadingParts;
}

bool isSASTeamStage3SpaceVictoryThreat(TeamTypes eTeam)
{
	static const int iStage3SpacePercentThreshold = GC.getDefineINT("SAS_UWAI_VICTORY_DENIAL_STAGE3_SPACE_PARTS_PERCENT_THRESHOLD");
	if (iStage3SpacePercentThreshold <= 0 || getSASTeamSpaceVictoryStage(eTeam) < 3)
		return false;
	int const iPartsBuilt = getSASTeamSpaceshipPartsBuilt(eTeam);
	static const int iLeaderPartMargin = GC.getDefineINT("SAS_UWAI_VICTORY_DENIAL_STAGE3_SPACE_LEADER_PART_MARGIN");
	// <!-- custom: Save-file 452 showed raw part count was too crude: England and Egypt were both major Space threats at 8/16 parts, but every Apollo builder should not trigger emergency wars. Require enough completion and near-leader Space progress. (GPT-5.5) -->
	return (iPartsBuilt * 100 >= getSASSpaceshipPartsRequired() * iStage3SpacePercentThreshold && getSASLeadingSpaceshipPartsBuilt() - iPartsBuilt <= iLeaderPartMargin);
}

// <!-- custom: Victory-denial peace refusal was implemented only as a final CvDeal guard. A fresh Pangaea diagnostic run logged 57 negotiations that returned success although the guard kept the teams at war, causing repeated ineffective treaties. Share the exact threat test so UWAI can reject those negotiations before building a deal while CvDeal retains its safety net. (GPT-5.6-Sol) -->
bool isSASUWAIVictoryDenialPeaceThreat(TeamTypes eTeam, int* piVictoryCountdown, int* piMaxVictoryStage)
{
	static const bool bSASUWAIVictoryDenialEnable = GC.getDefineBOOL("SAS_UWAI_VICTORY_DENIAL_ENABLE");
	if (!bSASUWAIVictoryDenialEnable)
		return false;
	static const int iMaxVictoryDenialPeaceCountdownNormal = GC.getDefineINT("SAS_UWAI_VICTORY_DENIAL_MAX_COUNTDOWN_TURNS_NORMAL_GAMESPEED_REFUSE_PEACE");
	int const iMaxVictoryDenialPeaceCountdown = getSASVictoryDelayTurnsFromNormalGameSpeed(iMaxVictoryDenialPeaceCountdownNormal);
	int const iCountdown = GET_TEAM(eTeam).AI_getLowestVictoryCountdown();
	int const iMaxVictoryStage = getSASTeamMaxVictoryStage(eTeam);
	if (piVictoryCountdown != NULL)
		*piVictoryCountdown = iCountdown;
	if (piMaxVictoryStage != NULL)
		*piMaxVictoryStage = iMaxVictoryStage;
	static const bool bRefuseStage4Peace = GC.getDefineBOOL("SAS_UWAI_VICTORY_DENIAL_REFUSE_STAGE4_PEACE_ENABLE");
	static const bool bRefuseStage3SpacePeace = GC.getDefineBOOL("SAS_UWAI_VICTORY_DENIAL_REFUSE_STAGE3_SPACE_PEACE_ENABLE");
	return (iCountdown >= 0 && iCountdown <= iMaxVictoryDenialPeaceCountdown) || (bRefuseStage4Peace && iMaxVictoryStage >= 4) || (bRefuseStage3SpacePeace && isSASTeamStage3SpaceVictoryThreat(eTeam));
}

int getSASTeamStage3SpaceLeaderPartGap(TeamTypes eTeam)
{
	return getSASLeadingSpaceshipPartsBuilt() - getSASTeamSpaceshipPartsBuilt(eTeam);
}

// advc: No longer needed
/*bool isPotentialEnemy(TeamTypes eOurTeam, TeamTypes eTheirTeam)
{
	FAssert(eOurTeam != NO_TEAM);
	if (eTheirTeam == NO_TEAM)
		return false;
	// advc: Moved into new CvTeamAI function
	return GET_TEAM(eOurTeam).AI_mayAttack(eTheirTeam);
}*/

// K-Mod: (advc - Where do we move this? Should not be global.)
int estimateCollateralWeight(CvPlot const* pPlot, TeamTypes eAttackTeam, TeamTypes eDefenseTeam)
{
	int iBaseCollateral = GC.getDefineINT(CvGlobals::COLLATERAL_COMBAT_DAMAGE); // normally 10
	if (pPlot == NULL)
		return iBaseCollateral * 110;

	/*	Collateral damage does not depend on any kind of strength bonus -
		so when a unit takes collateral damage, their bonuses are effectively wasted.
		Therefore, I'm going to inflate the value of collateral damage based
		on a rough estimate of the defenders bonuses. */

	TeamTypes ePlotBonusTeam = eDefenseTeam;
	if (ePlotBonusTeam == NO_TEAM)
		ePlotBonusTeam = (pPlot->getTeam() == eAttackTeam ? NO_TEAM : pPlot->getTeam());

	iBaseCollateral *= (pPlot->isCity() ? 130 : 110) +
			pPlot->defenseModifier(ePlotBonusTeam, false,
			eAttackTeam); // advc.012

	// Estimate the average collateral damage reduction of the units on the plot
	int iResistanceSum = 0;
	int iUnits = 0;

	FOR_EACH_UNIT_IN(pUnit, *pPlot)
	{
		if (!pUnit->canDefend(pPlot))
			continue;
		if (eDefenseTeam != NO_TEAM && pUnit->getTeam() != eDefenseTeam)
			continue;
		if (eAttackTeam != NO_TEAM && pUnit->getTeam() == eAttackTeam)
			continue;

		iUnits++;
		/*	Kludge! I'm only checking for immunity against the unit's own combat type.
			Ideally we'd know what kind of collateral damage we're expecting to be hit by,
			and check for immunity vs that.
			Or we could check all types... But the reality is, there are always
			going to be mods and fringe cases where the esitmate is inaccurate.
			And currently in K-Mod, all instances of immunity are to the unit's own type anyway.
			Whichever way we do the estimate, cho-ku-nu is going to mess it up anyway.
			(Unless I change the game mechanics.) */
		if ( // advc.001: Animals have no unit combat type (K146 also fixes this)
			pUnit->getUnitCombatType() != NO_UNITCOMBAT &&
			pUnit->getUnitInfo().getUnitCombatCollateralImmune(pUnit->getUnitCombatType()))
		{
			iResistanceSum += 100;
		}
		else iResistanceSum += pUnit->getCollateralDamageProtection();
	}
	if (iUnits > 0)
	{
		iBaseCollateral = iBaseCollateral * (iUnits * 100 - iResistanceSum) /
				(iUnits * 100);
	}

	return iBaseCollateral; // note, a factor of 100 is included in the result.
}


void setTradeItem(TradeData* pItem, TradeableItems eItemType, int iData)
{
	pItem->m_eItemType = eItemType;
	pItem->m_iData = iData;
	pItem->m_bOffering = false;
	pItem->m_bHidden = false;
}


void setListHelp(CvWString& szBuffer, wchar const* szStart, wchar const* szItem, wchar const* szSeparator, bool& bFirst) // advc: bool&
{
	if (bFirst)
		szBuffer += szStart;
	else szBuffer += szSeparator;
	szBuffer += szItem;
	bFirst = false; // advc: And deleted this line from every call location
}


void setListHelp(CvWStringBuffer& szBuffer, wchar const* szStart, wchar const* szItem, wchar const* szSeparator, bool& bFirst) // advc: bool&
{
	if (bFirst)
		szBuffer.append(szStart);
	else szBuffer.append(szSeparator);
	szBuffer.append(szItem);
	bFirst = false; // advc: And deleted this line from every call location
}

// <advc> Based on the above
void setListHelp(CvWString& szBuffer, wchar const* szStart, wchar const* szItem, wchar const* szSeparator, int& iLastListID, int iListID)
{
	if (iLastListID != iListID)
		szBuffer += szStart;
	else szBuffer += szSeparator;
	szBuffer += szItem;
	iLastListID = iListID; // advc: And deleted this line from every call location
}

void setListHelp(CvWStringBuffer& szBuffer, wchar const* szStart, wchar const* szItem, wchar const* szSeparator, int& iLastListID, int iListID)
{
	if (iLastListID != iListID)
		szBuffer.append(szStart);
	else szBuffer.append(szSeparator);
	szBuffer.append(szItem);
	iLastListID = iListID; // advc: And deleted this line from every call location
} // </advc>

bool PUF_isGroupHead(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return pUnit->isGroupHead();
}

bool PUF_isPlayer(CvUnit const* pUnit, int iOwner, int iForTeam)
{	// advc.061: rewritten
	TeamTypes eForTeam = (TeamTypes)iForTeam;
	PlayerTypes eOwner = (PlayerTypes)iOwner;
	FAssertEnumBounds(eOwner);
	if(eForTeam == NO_TEAM || eForTeam == TEAMID(eOwner))
		return (pUnit->getOwner() == eOwner);
	FAssertEnumBounds(eForTeam);
	return (pUnit->getOwner() == eOwner && !pUnit->isInvisible(eForTeam, false) &&
			!pUnit->getUnitInfo().isHiddenNationality());
}

bool PUF_isTeam(CvUnit const* pUnit, int iTeam, int iDummy)
{
	FAssert(iDummy == -1);
	TeamTypes eTeam = (TeamTypes)iTeam;
	FAssertEnumBounds(eTeam);
	return (pUnit->getTeam() == eTeam);
}

bool PUF_isCombatTeam(CvUnit const* pUnit, int iTeam, int iForTeam)
{
	TeamTypes eTeam = (TeamTypes)iTeam;
	FAssertEnumBounds(eTeam);
	TeamTypes eForTeam = (TeamTypes)iForTeam;
	FAssertEnumBounds(eForTeam);
	return (TEAMID(pUnit->getCombatOwner(eForTeam, pUnit->getPlot())) ==
			eTeam && !pUnit->isInvisible(eForTeam, false, false));
}

bool PUF_isOtherPlayer(CvUnit const* pUnit, int iPlayer, int iDummy)
{
	FAssert(iDummy == -1);
	PlayerTypes ePlayer = (PlayerTypes)iPlayer;
	FAssertEnumBounds(ePlayer);
	return (pUnit->getOwner() != ePlayer);
}

bool PUF_isOtherTeam(CvUnit const* pUnit, int iPlayer, int iDummy)
{
	FAssert(iDummy == -1);
	PlayerTypes ePlayer = (PlayerTypes)iPlayer;
	FAssertEnumBounds(ePlayer);
	TeamTypes eTeam = TEAMID(ePlayer);
	if (pUnit->canCoexistWithEnemyUnit(eTeam))
		return false;
	return (pUnit->getTeam() != eTeam);
}

bool PUF_canDefend(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return pUnit->canDefend();
}

bool PUF_cannotDefend(const CvUnit* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return !pUnit->canDefend();
}

bool PUF_canDefendGroupHead(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	return (PUF_canDefend(pUnit, iDummy1, iDummy2) &&
			PUF_isGroupHead(pUnit, iDummy1, iDummy2));
}

bool PUF_canDefendPotentialEnemy(CvUnit const* pUnit, int iPlayer, BOOL iAlwaysHostile)
{
	return (PUF_canDefend(pUnit) && PUF_isPotentialEnemy(pUnit, iPlayer, iAlwaysHostile));
}

bool PUF_canDefendEnemy(CvUnit const* pUnit, int iPlayer, BOOL iAlwaysHostile)
{
	return (PUF_canDefend(pUnit) && PUF_isEnemy(pUnit, iPlayer, iAlwaysHostile));
}

bool PUF_isPotentialEnemy(CvUnit const* pUnit, int iPlayer, BOOL iAlwaysHostile)
{
	PlayerTypes ePlayer = (PlayerTypes)iPlayer;
	FAssertEnumBounds(ePlayer);
	FAssertBOOL(iAlwaysHostile);
	bool bAlwaysHostile = iAlwaysHostile;
	// advc: Switched the Our/Other variable names. It's iPlayer whose war plans matter.
	TeamTypes eOurTeam = TEAMID(ePlayer);
	TeamTypes eOtherTeam = TEAMID(pUnit->getCombatOwner(eOurTeam));
	if (pUnit->canCoexistWithEnemyUnit(eOurTeam))
		return false;
	return (bAlwaysHostile ? eOurTeam != eOtherTeam :
			GET_TEAM(eOurTeam).AI_mayAttack(eOtherTeam));
}

bool PUF_isEnemy(CvUnit const* pUnit, int iPlayer, BOOL iAlwaysHostile)
{
	PlayerTypes ePlayer = (PlayerTypes)iPlayer;
	FAssertEnumBounds(ePlayer);
	FAssertBOOL(iAlwaysHostile);
	bool bAlwaysHostile = iAlwaysHostile;
	// advc: Switched the Our/Other variable names
	TeamTypes eOurTeam = TEAMID(ePlayer);
	TeamTypes eOtherTeam = TEAMID(pUnit->getCombatOwner(eOurTeam));
	if (pUnit->canCoexistWithEnemyUnit(eOurTeam))
		return false;
	return (bAlwaysHostile ? eOurTeam != eOtherTeam :
			GET_TEAM(eOurTeam).isAtWar(eOtherTeam));
}

bool PUF_canDeclareWar(CvUnit const* pUnit, int iPlayer, BOOL iAlwaysHostile)
{
	PlayerTypes ePlayer = (PlayerTypes)iPlayer;
	FAssertEnumBounds(ePlayer);
	FAssertBOOL(iAlwaysHostile);
	bool bAlwaysHostile = iAlwaysHostile;
	/*	advc: Switched the Our/Other variable names. This function says whether
		iPlayer can declare war on the combat owner of pUnit. */
	TeamTypes eOurTeam = TEAMID(ePlayer);
	TeamTypes eOtherTeam = TEAMID(pUnit->getCombatOwner(eOurTeam));
	if (pUnit->canCoexistWithEnemyUnit(eOurTeam))
		return false;
	return (bAlwaysHostile ? false : GET_TEAM(eOurTeam).canDeclareWar(eOtherTeam));
}
// advc.ctr:
bool PUF_isEnemyCityAttacker(CvUnit const* pUnit, int iPlayer, int iAssumePeaceTeam)
{
	TeamTypes eAssumePeaceTeam = (TeamTypes)iAssumePeaceTeam;
	if (eAssumePeaceTeam != NO_TEAM)
	{
		FAssertEnumBounds(eAssumePeaceTeam);
		if (GET_TEAM(pUnit->getTeam()).getMasterTeam() == GET_TEAM(eAssumePeaceTeam).getMasterTeam())
			return false;
	}
	CvUnitInfo& u = pUnit->getUnitInfo();
	if (u.getCargoSpace() <= 0 || u.getSpecialCargo() != NO_SPECIALUNIT)
	{
		if (u.getDomainType() != DOMAIN_LAND)
			return false;
		if (u.isOnlyDefensive() || u.getCombat() <= 0)
			return false;
	}
	return PUF_isEnemy(pUnit, iPlayer, false);
}

bool PUF_isVisible(CvUnit const* pUnit, int iPlayer, int iDummy)
{
	FAssert(iDummy == -1);
	PlayerTypes ePlayer = (PlayerTypes)iPlayer;
	FAssertEnumBounds(ePlayer);
	return !pUnit->isInvisible(TEAMID(ePlayer), false);
}

bool PUF_isVisibleDebug(CvUnit const* pUnit, int iPlayer, int iDummy)
{
	FAssert(iDummy == -1);
	PlayerTypes ePlayer = (PlayerTypes)iPlayer;
	FAssertEnumBounds(ePlayer);
	return !pUnit->isInvisible(TEAMID(ePlayer), true);
}
// advc.298:
bool PUF_isLethal(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return (pUnit->canAttack() && pUnit->combatLimit() >= 100);
}

bool PUF_canSiege(CvUnit const* pUnit, int iTargetPlayer, int iDummy)
{
	FAssert(iDummy == -1);
	PlayerTypes eTargetPlayer = (PlayerTypes)iTargetPlayer;
	FAssertEnumBounds(eTargetPlayer);
	return pUnit->canSiege(TEAMID(eTargetPlayer));
}

bool PUF_canAirAttack(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return pUnit->canAirAttack();
}

bool PUF_canAirDefend(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return pUnit->canAirDefend();
}
// K-Mod:
bool PUF_isAirIntercept(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return (pUnit->getDomainType() == DOMAIN_AIR &&
			pUnit->getGroup()->getActivityType() == ACTIVITY_INTERCEPT);
}

bool PUF_isFighting(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return pUnit->isFighting();
}

bool PUF_isAnimal(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return pUnit->isAnimal();
}

bool PUF_isMilitaryHappiness(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return pUnit->isMilitaryHappiness();
}

bool PUF_isInvestigate(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	// <advc.103>
	if(pUnit->hasMoved())
		return false; // </advc.103>
	return pUnit->isInvestigate();
}

bool PUF_isCounterSpy(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return pUnit->isCounterSpy();
}

bool PUF_isSpy(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return pUnit->isSpy();
}

bool PUF_isDomainType(CvUnit const* pUnit, int iDomain, int iDummy)
{
	FAssert(iDummy == -1);
	DomainTypes eDomain = (DomainTypes)iDomain;
	FAssertEnumBounds(eDomain);
	return (pUnit->getDomainType() == eDomain);
}

bool PUF_isUnitType(CvUnit const* pUnit, int iUnit, int iDummy)
{
	FAssert(iDummy == -1);
	UnitTypes eUnit = (UnitTypes)iUnit;
	FAssertEnumBounds(eUnit);
	return (pUnit->getUnitType() == eUnit);
}

bool PUF_isUnitAIType(CvUnit const* pUnit, int iUnitAI, int iDummy)
{
	FAssert(iDummy == -1);
	UnitAITypes eUnitAI = (UnitAITypes)iUnitAI;
	FAssertEnumBounds(eUnitAI);
	return (pUnit->AI_getUnitAIType() == eUnitAI);
}
// K-Mod:
bool PUF_isMissionAIType(CvUnit const* pUnit, int iMissionAI, int iDummy)
{
	FAssert(iDummy == -1);
	MissionAITypes eMissionAI = (MissionAITypes)iMissionAI;
	FAssertEnumBounds(eMissionAI);
	return (pUnit->AI().AI_getGroup()->AI_getMissionAIType() == eMissionAI);
}

bool PUF_isCityAIType(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return pUnit->AI().AI_isCityAIType();
}

bool PUF_isNotCityAIType(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	return !PUF_isCityAIType(pUnit);
}
// advc.003j (comment): unused
bool PUF_isSelected(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return pUnit->IsSelected();
}

/*bool PUF_isNoMission(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	//return (pUnit->getGroup()->getActivityType() != ACTIVITY_MISSION); // BtS
	return (pUnit->getGroup()->AI_getMissionAIType() == NO_MISSIONAI); // K-Mod
}*/
/*  advc.113b: The above won't do for counting the workers available to a city:
	Doesn't count retreated workers and does count workers in cargo. */
/*  Replacement: Count pUnit if its mission plot has the given city as its
	working city. If pUnit has no mission, then it's counted if its current plot
	has the given city as its working city. */
bool PUF_isMissionPlotWorkingCity(CvUnit const* pUnit, int iCity, int iCityOwner)
{
	CvCity* pCity = GET_PLAYER((PlayerTypes)iCityOwner).getCity(iCity);
	if(pCity == NULL || pUnit->isCargo())
		return false;
	CvPlot* pMissionPlot = pUnit->AI().AI_getGroup()->AI_getMissionAIPlot();
	if(pMissionPlot == NULL)
		pMissionPlot = pUnit->plot();
	return (pMissionPlot->getWorkingCity() == pCity);
}

bool PUF_isFiniteRange(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	return (pUnit->getDomainType() != DOMAIN_AIR || pUnit->getUnitInfo().getAirRange() > 0);
}
// BETTER_BTS_AI_MOD, General AI, 01/15/09, jdog5000: START
bool PUF_isAvailableUnitAITypeGroupie(CvUnit const* pUnit, int iUnitAI, int iDummy)
{	// (advc: Removed unnecessary helper function)
	return (PUF_isUnitAIType(pUnit->getGroup()->getHeadUnit(), iUnitAI) &&
			!pUnit->isCargo());
}

bool PUF_isFiniteRangeAndNotJustProduced(CvUnit const* pUnit, int iDummy1, int iDummy2)
{
	return (PUF_isFiniteRange(pUnit) &&
			GC.getGame().getGameTurn() - pUnit->getGameTurnCreated() > 1);
} // BETTER_BTS_AI_MOD: END

bool PUF_makeInfoBarDirty(CvUnit* pUnit, int iDummy1, int iDummy2)
{
	FAssert(iDummy1 == -1 && iDummy2 == -1);
	pUnit->setInfoBarDirty(true);
	return true;
}

// advc.003j (comment): Unused
int baseYieldToSymbol(int iNumYieldTypes, int iYieldStack)
{
	// <!-- custom: make these static const for performance optimization as advised by chatgpt 5 too. -->
	static const int iMAX_YIELD_STACK = GC.getDefineINT("MAX_YIELD_STACK");

	return iNumYieldTypes * iMAX_YIELD_STACK + iYieldStack;
}
/*  advc.003j: Vanilla Civ 4 function that used to be a DLLExport;
	certainly unused since BtS, and doesn't sound too useful. */
/*bool isPickableName(const TCHAR* szName) {
	if (szName) {
		int iLen = _tcslen(szName);
		if (!_tcsicmp(&szName[iLen-6], "NOPICK"))
			return false;
	}
	return true;
}*/

/*	advc: Akin to natGetDeterministicRandom (deleted from CvCity.cpp). For reference,
	the implementation of that function was:
	srand(7297 * iSeedX + 2909  * iSeedY);
	return (rand() % (iMax - iMin)) + iMin; */
int intHash(std::vector<int> const& kInputs, PlayerTypes ePlayer)
{
	int const iPrime = 31;
	int iHashVal = 0;
	for (size_t i = 0; i < kInputs.size(); i++)
	{
		iHashVal += kInputs[i];
		iHashVal *= iPrime;
	}
	int iCapitalIndex = -1;
	if (ePlayer != NO_PLAYER)
	{
		CvCity const* pCapital = GET_PLAYER(ePlayer).getCapital();
		if (pCapital != NULL)
			iCapitalIndex = pCapital->plotNum();
	}
	if (iCapitalIndex >= 0)
	{
		iHashVal += iCapitalIndex;
		iHashVal *= iPrime;
	}
	return iHashVal;
}


int getTurnYearForGame(int iGameTurn, int iStartYear, CalendarTypes eCalendar, GameSpeedTypes eSpeed)
{
	return getTurnMonthForGame(iGameTurn, iStartYear, eCalendar, eSpeed) /
			std::max(1, GC.getNumMonthInfos()); // advc: max
}


int getTurnMonthForGame(int iGameTurn, int iStartYear, CalendarTypes eCalendar, GameSpeedTypes eSpeed)
{
	int iTurnMonth = iStartYear * GC.getNumMonthInfos();
	switch (eCalendar)
	{
	case CALENDAR_DEFAULT:
	{
		// <!-- custom: performance optimizations as recommended as well by chatgpt 5 thanks, check if accurate -->
		// <!-- custom: code/performance optimization: hoist -->
        const CvGameSpeedInfo& kSpeed = GC.getInfo(eSpeed);
        int const n = kSpeed.getNumTurnIncrements();

		int iTurnCount = 0;
		for (int i = 0; i < n; i++)
		{
			GameTurnInfo const& kGameTurn = kSpeed.getGameTurnInfo(i);
			if (iGameTurn > iTurnCount + kGameTurn.iNumGameTurnsPerIncrement)
			{
				iTurnMonth += kGameTurn.iMonthIncrement *
						kGameTurn.iNumGameTurnsPerIncrement;
				iTurnCount += kGameTurn.iNumGameTurnsPerIncrement;
			}
			else
			{
				iTurnMonth += kGameTurn.iMonthIncrement * (iGameTurn - iTurnCount);
				iTurnCount += iGameTurn - iTurnCount;
				break;
			}
		}
		if (iGameTurn > iTurnCount)
		{
			iTurnMonth += kSpeed.getGameTurnInfo(
					n - 1).
					iMonthIncrement * (iGameTurn - iTurnCount);
		}
		break;
	}
	case CALENDAR_BI_YEARLY:
		iTurnMonth += 2 * iGameTurn * GC.getNumMonthInfos();
		break;

	case CALENDAR_YEARS:
	case CALENDAR_TURNS:
		iTurnMonth += iGameTurn * GC.getNumMonthInfos();
		break;

	case CALENDAR_SEASONS:
		iTurnMonth += (iGameTurn * GC.getNumMonthInfos()) /
				std::max(1, GC.getNumSeasonInfos()); // advc: max
		break;

	case CALENDAR_MONTHS:
		iTurnMonth += iGameTurn;
		break;

	case CALENDAR_WEEKS:
	{
		// <!-- custom: make these static const for performance optimization as advised by chatgpt 5 too. -->
		static const int iWEEKS_PER_MONTHS = GC.getDefineINT("WEEKS_PER_MONTHS");

		iTurnMonth += iGameTurn /
				std::max(1, iWEEKS_PER_MONTHS); // advc: max
		break;
	}

	default:
		FAssert(false);
	}

	return iTurnMonth;
}


void getDirectionTypeString(CvWString& szString, DirectionTypes eDirectionType)
{
	/*  advc.007: Turned this comment
		"these string functions should only be used under chipotle cheat code (not internationalized)"
		into an assertion: */
	FAssertMsg(gLogBBAI || GC.getGame().isDebugMode(), "getDirectionTypeString should only be used for Debug output");
	switch (eDirectionType)
	{
	case NO_DIRECTION: szString = L"NO_DIRECTION"; break;

	case DIRECTION_NORTH: szString = L"north"; break;
	case DIRECTION_NORTHEAST: szString = L"northeast"; break;
	case DIRECTION_EAST: szString = L"east"; break;
	case DIRECTION_SOUTHEAST: szString = L"southeast"; break;
	case DIRECTION_SOUTH: szString = L"south"; break;
	case DIRECTION_SOUTHWEST: szString = L"southwest"; break;
	case DIRECTION_WEST: szString = L"west"; break;
	case DIRECTION_NORTHWEST: szString = L"northwest"; break;

	default: szString = CvWString::format(L"UNKNOWN_DIRECTION(%d)", eDirectionType); break;
	}
}

void getCardinalDirectionTypeString(CvWString& szString, CardinalDirectionTypes eDirectionType)
{
	getDirectionTypeString(szString, cardinalDirectionToDirection(eDirectionType));
}

// advc.007: Removed the "ACTIVITY_" prefix from the strings b/c it takes up too much space.
void getActivityTypeString(CvWString& szString, ActivityTypes eActivityType)
{
	FAssertMsg(gLogBBAI || GC.getGame().isDebugMode(), "getActivityTypeString should only be used for Debug output"); // advc.007
	switch (eActivityType)
	{
	case NO_ACTIVITY: szString = L"NO_ACTIVITY"; break;

	case ACTIVITY_AWAKE: szString = L"AWAKE"; break;
	case ACTIVITY_HOLD: szString = L"HOLD"; break;
	case ACTIVITY_SLEEP: szString = L"SLEEP"; break;
	case ACTIVITY_HEAL: szString = L"HEAL"; break;
	case ACTIVITY_SENTRY: szString = L"SENTRY"; break;
	case ACTIVITY_INTERCEPT: szString = L"INTERCEPT"; break;
	case ACTIVITY_MISSION: szString = L"MISSION"; break;
// K-Mod. There were some missing activity strings...
/*#define case_string(x) case x: szString = L#x; break;
	case_string(ACTIVITY_PATROL)
	case_string(ACTIVITY_PLUNDER)
#undef case_string*/
// K-Mod end
	// <advc.007>
	case ACTIVITY_PATROL: szString = L"PATROL"; break;
	case ACTIVITY_PLUNDER: szString = L"PLUNDER"; break;
	// </advc.007>
	case ACTIVITY_BOARDED: szString = L"BOARDED"; break; // advc.075
	default: szString = CvWString::format(L"UNKNOWN_ACTIVITY(%d)", eActivityType); break;
	}
}

void getMissionTypeString(CvWString& szString, MissionTypes eMissionType)
{
	FAssertMsg(gLogBBAI || GC.getGame().isDebugMode(), "getMissionTypeString should only be used for Debug output"); // advc.007
	switch (eMissionType)
	{
	case NO_MISSION: szString = L"NO_MISSION"; break;

	case MISSION_MOVE_TO: szString = L"MISSION_MOVE_TO"; break;
	case MISSION_ROUTE_TO: szString = L"MISSION_ROUTE_TO"; break;
	case MISSION_MOVE_TO_UNIT: szString = L"MISSION_MOVE_TO_UNIT"; break;
	case MISSION_SKIP: szString = L"MISSION_SKIP"; break;
	case MISSION_SLEEP: szString = L"MISSION_SLEEP"; break;
	case MISSION_FORTIFY: szString = L"MISSION_FORTIFY"; break;
	case MISSION_PLUNDER: szString = L"MISSION_PLUNDER"; break;
	case MISSION_AIRPATROL: szString = L"MISSION_AIRPATROL"; break;
	case MISSION_SEAPATROL: szString = L"MISSION_SEAPATROL"; break;
	case MISSION_HEAL: szString = L"MISSION_HEAL"; break;
	case MISSION_SENTRY_HEAL: szString = L"MISSION_SENTRY_HEAL"; break; // advc.004l
	case MISSION_SENTRY: szString = L"MISSION_SENTRY"; break;
	case MISSION_AIRLIFT: szString = L"MISSION_AIRLIFT"; break;
	case MISSION_NUKE: szString = L"MISSION_NUKE"; break;
	case MISSION_RECON: szString = L"MISSION_RECON"; break;
	case MISSION_PARADROP: szString = L"MISSION_PARADROP"; break;
	case MISSION_AIRBOMB: szString = L"MISSION_AIRBOMB"; break;
	case MISSION_BOMBARD: szString = L"MISSION_BOMBARD"; break;
	case MISSION_PILLAGE: szString = L"MISSION_PILLAGE"; break;
	case MISSION_SABOTAGE: szString = L"MISSION_SABOTAGE"; break;
	case MISSION_DESTROY: szString = L"MISSION_DESTROY"; break;
	case MISSION_STEAL_PLANS: szString = L"MISSION_STEAL_PLANS"; break;
	case MISSION_FOUND: szString = L"MISSION_FOUND"; break;
	case MISSION_SPREAD: szString = L"MISSION_SPREAD"; break;
	case MISSION_SPREAD_CORPORATION: szString = L"MISSION_SPREAD_CORPORATION"; break;
	case MISSION_JOIN: szString = L"MISSION_JOIN"; break;
	case MISSION_CONSTRUCT: szString = L"MISSION_CONSTRUCT"; break;
	case MISSION_DISCOVER: szString = L"MISSION_DISCOVER"; break;
	case MISSION_HURRY: szString = L"MISSION_HURRY"; break;
	case MISSION_TRADE: szString = L"MISSION_TRADE"; break;
	case MISSION_GREAT_WORK: szString = L"MISSION_GREAT_WORK"; break;
	case MISSION_INFILTRATE: szString = L"MISSION_INFILTRATE"; break;
	case MISSION_GOLDEN_AGE: szString = L"MISSION_GOLDEN_AGE"; break;
	case MISSION_BUILD: szString = L"MISSION_BUILD"; break;
	case MISSION_LEAD: szString = L"MISSION_LEAD"; break;
	case MISSION_ESPIONAGE: szString = L"MISSION_ESPIONAGE"; break;
	case MISSION_DIE_ANIMATION: szString = L"MISSION_DIE_ANIMATION"; break;

	case MISSION_BEGIN_COMBAT: szString = L"MISSION_BEGIN_COMBAT"; break;
	case MISSION_END_COMBAT: szString = L"MISSION_END_COMBAT"; break;
	case MISSION_AIRSTRIKE: szString = L"MISSION_AIRSTRIKE"; break;
	case MISSION_SURRENDER: szString = L"MISSION_SURRENDER"; break;
	case MISSION_CAPTURED: szString = L"MISSION_CAPTURED"; break;
	case MISSION_IDLE: szString = L"MISSION_IDLE"; break;
	case MISSION_DIE: szString = L"MISSION_DIE"; break;
	case MISSION_DAMAGE: szString = L"MISSION_DAMAGE"; break;
	case MISSION_MULTI_SELECT: szString = L"MISSION_MULTI_SELECT"; break;
	case MISSION_MULTI_DESELECT: szString = L"MISSION_MULTI_DESELECT"; break;

	default: szString = CvWString::format(L"UNKOWN_MISSION(%d)", eMissionType); break;
	}
}

// advc.007: Removed the "MISSIONAI_" prefix from the strings b/c it takes up too much space.
void getMissionAIString(CvWString& szString, MissionAITypes eMissionAI)
{
	FAssertMsg(gLogBBAI || GC.getGame().isDebugMode(), "getMissionAIString should only be used for Debug output"); // advc.007
	switch (eMissionAI)
	{
	case NO_MISSIONAI: szString = L"NO_MISSIONAI"; break;

	case MISSIONAI_SHADOW: szString = L"SHADOW"; break;
	case MISSIONAI_GROUP: szString = L"GROUP"; break;
	case MISSIONAI_LOAD_ASSAULT: szString = L"LOAD_ASSAULT"; break;
	case MISSIONAI_LOAD_SETTLER: szString = L"LOAD_SETTLER"; break;
	case MISSIONAI_LOAD_SPECIAL: szString = L"LOAD_SPECIAL"; break;
	case MISSIONAI_GUARD_CITY: szString = L"GUARD_CITY"; break;
	case MISSIONAI_GUARD_BONUS: szString = L"GUARD_BONUS"; break;
	case MISSIONAI_GUARD_SPY: szString = L"GUARD_SPY"; break;
	case MISSIONAI_ATTACK_SPY: szString = L"ATTACK_SPY"; break;
	case MISSIONAI_SPREAD: szString = L"SPREAD"; break;
	case MISSIONAI_CONSTRUCT: szString = L"CONSTRUCT"; break;
	case MISSIONAI_HURRY: szString = L"HURRY"; break;
	case MISSIONAI_GREAT_WORK: szString = L"GREAT_WORK"; break;
	case MISSIONAI_EXPLORE: szString = L"EXPLORE"; break;
	case MISSIONAI_BLOCKADE: szString = L"BLOCKADE"; break;
	case MISSIONAI_PILLAGE: szString = L"PILLAGE"; break;
	case MISSIONAI_FOUND: szString = L"FOUND"; break;
	case MISSIONAI_BUILD: szString = L"BUILD"; break;
	case MISSIONAI_ASSAULT: szString = L"ASSAULT"; break;
	case MISSIONAI_CARRIER: szString = L"CARRIER"; break;
	case MISSIONAI_PICKUP: szString = L"PICKUP"; break;
// K-Mod
#define mission_string(x) case x: szString = L#x; break;
	mission_string(MISSIONAI_GUARD_COAST)
	mission_string(MISSIONAI_REINFORCE)
	mission_string(MISSIONAI_SPREAD_CORPORATION)
	mission_string(MISSIONAI_RECON_SPY)
	mission_string(MISSIONAI_JOIN_CITY)
	mission_string(MISSIONAI_TRADE)
	mission_string(MISSIONAI_INFILTRATE)
	mission_string(MISSIONAI_CHOKE)
	mission_string(MISSIONAI_HEAL)
	mission_string(MISSIONAI_RETREAT)
	mission_string(MISSIONAI_PATROL)
	mission_string(MISSIONAI_DEFEND)
	mission_string(MISSIONAI_COUNTER_ATTACK)
	mission_string(MISSIONAI_UPGRADE)
	mission_string(MISSIONAI_STRANDED)
#undef mission_string
// K-Mod end
	default: szString = CvWString::format(L"UNKOWN_MISSION_AI(%d)", eMissionAI); break;
	}
}

void getUnitAIString(CvWString& szString, UnitAITypes eUnitAI)
{
	FAssertMsg(gLogBBAI || GC.getGame().isDebugMode(), "getUnitAIString should only be used for Debug output"); // advc.007

	// note, GC.getInfo(eUnitAI).getDescription() is a international friendly way to get string (but it will be longer)

	switch (eUnitAI)
	{
	case NO_UNITAI: szString = L"no unitAI"; break;

	case UNITAI_UNKNOWN: szString = L"unknown"; break;
	case UNITAI_ANIMAL: szString = L"animal"; break;
	case UNITAI_SETTLE: szString = L"settle"; break;
	case UNITAI_WORKER: szString = L"worker"; break;
	case UNITAI_ATTACK: szString = L"attack"; break;
	case UNITAI_ATTACK_CITY: szString = L"attack city"; break;
	case UNITAI_COLLATERAL: szString = L"collateral"; break;
	case UNITAI_PILLAGE: szString = L"pillage"; break;
	case UNITAI_RESERVE: szString = L"reserve"; break;
	case UNITAI_COUNTER: szString = L"counter"; break;
	case UNITAI_CITY_DEFENSE: szString = L"city defense"; break;
	case UNITAI_CITY_COUNTER: szString = L"city counter"; break;
	case UNITAI_CITY_SPECIAL: szString = L"city special"; break;
	case UNITAI_EXPLORE: szString = L"explore"; break;
	case UNITAI_MISSIONARY: szString = L"missionary"; break;
	case UNITAI_GREAT_PROPHET: szString = L"prophet"; break;
	case UNITAI_GREAT_ARTIST: szString = L"artist"; break;
	case UNITAI_GREAT_SCIENTIST: szString = L"scientist"; break;
	case UNITAI_GREAT_GENERAL: szString = L"general"; break;
	case UNITAI_GREAT_MERCHANT: szString = L"merchant"; break;
	case UNITAI_GREAT_ENGINEER: szString = L"engineer"; break;
	case UNITAI_GREAT_SPY: szString = L"great spy"; break; // K-Mod
	case UNITAI_SPY: szString = L"spy"; break;
	case UNITAI_ICBM: szString = L"icbm"; break;
	case UNITAI_WORKER_SEA: szString = L"worker sea"; break;
	case UNITAI_ATTACK_SEA: szString = L"attack sea"; break;
	case UNITAI_RESERVE_SEA: szString = L"reserve sea"; break;
	case UNITAI_ESCORT_SEA: szString = L"escort sea"; break;
	case UNITAI_EXPLORE_SEA: szString = L"explore sea"; break;
	case UNITAI_ASSAULT_SEA: szString = L"assault sea"; break;
	case UNITAI_SETTLER_SEA: szString = L"settler sea"; break;
	case UNITAI_MISSIONARY_SEA: szString = L"missionary sea"; break;
	case UNITAI_SPY_SEA: szString = L"spy sea"; break;
	case UNITAI_CARRIER_SEA: szString = L"carrier sea"; break;
	case UNITAI_MISSILE_CARRIER_SEA: szString = L"missile carrier"; break;
	case UNITAI_PIRATE_SEA: szString = L"pirate sea"; break;
	case UNITAI_ATTACK_AIR: szString = L"attack air"; break;
	case UNITAI_DEFENSE_AIR: szString = L"defense air"; break;
	case UNITAI_CARRIER_AIR: szString = L"carrier air"; break;
	case UNITAI_MISSILE_AIR: szString = L"missile air"; break; // K-Mod (this string was missing)
	case UNITAI_PARADROP: szString = L"paradrop"; break;
	case UNITAI_ATTACK_CITY_LEMMING: szString = L"attack city lemming"; break;

	default: szString = CvWString::format(L"unknown(%d)", eUnitAI); break;
	}
}

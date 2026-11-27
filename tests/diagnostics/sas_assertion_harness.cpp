// AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
// (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

// <!-- custom: Manual Windows harness for the actual FAssert diagnostic core extracted by run_assertion_tests.py and compiled with VC2003.
// It exercises startup dialog fallback, post-GlobalDefines policy caching, automatic action resolution, shared runtime context/dialog decoration, Unicode paths and bounded escaped rows without building or installing the game DLL. (ChatGPT-5.6-Sol) -->
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <algorithm>
#include <cstdio>
#include <cstdlib> // <!-- custom: The extracted production FAssertDlg calls exit for the inherited Abort action. (ChatGPT-5.6-Sol) -->
#include <cstring> // <!-- custom: The minimal FVariable/log fixtures compare and inspect literal C strings. (ChatGPT-5.6-Sol) -->
#include <string> // <!-- custom: Hold Unicode-root and oversized-field fixture data without introducing fixed harness buffers. (ChatGPT-5.6-Sol) -->

#include "PragmaWarnings.h"

enum GameStateTypes { GAMESTATE_ON = 0, GAMESTATE_OVER, GAMESTATE_EXTENDED };
enum { SAS_AUTOPLAY_END_ASSERTION = 99 };

// <!-- custom: The production cache intentionally inspects FVariable directly instead of using an assertion-capable typed getter; the harness needs only that exact interface. (ChatGPT-5.6-Sol) -->
enum eVariableType { FVARTYPE_INT = 5, FVARTYPE_STRING = 9 };
struct FVariable
{
	FVariable() : m_iValue(0), m_eType(FVARTYPE_INT) {}
	int m_iValue;
	eVariableType m_eType;
};
class FVariableSystem
{
public:
	FVariableSystem() : bPresent(false) {}
	FVariable const* GetVariable(char const* szName) const
	{
		return (bPresent && strcmp(szName, "SAS_ASSERT_SILENT_ACTION") == 0 ? &kVariable : NULL);
	}
	bool bPresent;
	FVariable kVariable;
};

class CvGame
{
public:
	CvGame() : bReady(false), iTurn(0), iElapsed(0), iAutoPlay(0), iActivePlayer(-1), iActiveTeam(-1), eState(GAMESTATE_ON), iStopCalls(0) {}
	bool isFinalInitialized() const { return bReady; }
	int getGameTurn() const { return iTurn; }
	int getElapsedGameTurns() const { return iElapsed; }
	int getAIAutoPlay() const { return iAutoPlay; }
	int getActivePlayer() const { return iActivePlayer; }
	int getActiveTeam() const { return iActiveTeam; }
	GameStateTypes getGameState() const { return eState; }
	void setAIAutoPlay(int iValue, bool, int)
	{
		iAutoPlay = iValue;
		iStopCalls++;
	}
	bool bReady;
	int iTurn;
	int iElapsed;
	int iAutoPlay;
	int iActivePlayer;
	int iActiveTeam;
	GameStateTypes eState;
	int iStopCalls;
};

// <!-- custom: Mirror AdvCiv's const GC facade and non-const nullable game-pointer accessor; a mutable GC stub let the startup check pass here while the game build failed C2662. (GPT-6.1-Sol) -->
struct CvGlobals
{
	CvGlobals() : pGame(NULL) {}
	static CvGlobals& getInstance();
	static CvGlobals const& getConstInstance() { return getInstance(); }
	CvGame* getGamePointer() { return pGame; }
	CvGame& getGame() const { return *pGame; }
	FVariableSystem const* getDefinesVarSystem() const { return &kVariables; }
	CvGame* pGame;
	FVariableSystem kVariables;
};
static CvGlobals g_kTestGlobals;
CvGlobals& CvGlobals::getInstance() { return g_kTestGlobals; }
#define GC CvGlobals::getConstInstance()

static std::wstring g_szNativeRoot;
inline bool getSASNativeDefaultRootDirectory(std::wstring& szRoot)
{
	szRoot = g_szNativeRoot;
	return !szRoot.empty();
}

static int g_iDialogCount = 0;
static DWORD g_iDialogResult = 1;
static int g_iDialogSelectedAction = 1;

// <!-- custom: The production metadata row asks shared diagnostics for low-cost loaded-DLL identity; the harness supplies a fixed stand-in because it tests assertion behavior rather than PE fingerprinting. (ChatGPT-5.6-Sol) -->
class CvString
{
public:
	CvString(char const* szValue = "") : value(szValue) {}
	char const* GetCString() const { return value.c_str(); }
private:
	std::string value;
};
CvString getSASDllRuntimeContextFields()
{
	return CvString("build=HARNESS moduleFound=1 fileReadable=1 fileSizeBytes=1 dllFingerprint=FNV1A64:0000000000000001 dllLastWriteUtc=- peTimestampRaw=0 peTimestampUtc=- resourceFileVersion=- resourceProductVersion=- fassertEnabled=1");
}

#include "assertion_under_test.inc" // <!-- custom: Compile the production assertion core extracted from current FAssert.cpp rather than maintaining a duplicate implementation in the harness. (ChatGPT-5.6-Sol) -->

static bool contains(char const* szHaystack, char const* szNeedle)
{
	return (strstr(szHaystack, szNeedle) != NULL);
}

int main(int argc, char** argv)
{
	if (argc != 2)
		return 1;
	wchar_t szRoot[1024];
	if (MultiByteToWideChar(CP_ACP, 0, argv[1], -1, szRoot, 1024) <= 0)
		return 2;
	g_szNativeRoot = szRoot;
	setSASAssertionLogRootDirectory(szRoot);

	// <!-- custom: Put mode 2 in the variable system before caching; the first assertion must still use the startup dialog, proving that partially loaded GlobalDefines cannot activate silent handling. (ChatGPT-5.6-Sol) -->
	g_kTestGlobals.kVariables.bPresent = true;
	g_kTestGlobals.kVariables.kVariable.m_eType = FVARTYPE_INT;
	g_kTestGlobals.kVariables.kVariable.m_iValue = SAS_ASSERT_SILENT_IGNORE_ALWAYS;
	bool bIgnoreAlways = false;
	g_iDialogResult = ASSERT_DLG_IGNORE;
	g_iDialogSelectedAction = ASSERT_DLG_IGNORE;
	if (FAssertDlg("startup", "before cache", "startup.cpp", 10, "startupTest", bIgnoreAlways))
		return 3;
	if (g_iDialogCount != 1 || bIgnoreAlways)
		return 4;
	if (!contains(g_AssertText, "Game Context:  UNAVAILABLE (no CvGame object yet)"))
		return 5;
	std::wstring const szOriginalRoot = g_szSASAssertionLogRoot;
	setSASAssertionLogRootDirectory(L"Z:\\must-not-migrate");
	if (szOriginalRoot != g_szSASAssertionLogRoot)
		return 6;

	// <!-- custom: GlobalDefines are complete by first-menu presentation in the real game; establish _menu1 from the actual menu boundary and call it twice to prove repeated scene requests do not create _menu2. (ChatGPT-5.6-Sol) -->
	g_kTestGlobals.kVariables.kVariable.m_iValue = SAS_ASSERT_SILENT_IGNORE_ONCE;
	cacheSASAssertionSilentPolicy();
	startSASAssertionLogForMainMenu();
	startSASAssertionLogForMainMenu();
	if (FAssertDlg("menu", "first menu visit", "menu.cpp", 15, "menuTest", bIgnoreAlways))
		return 7;
	if (g_iDialogCount != 1)
		return 8;

	CvGame kGame;
	kGame.bReady = true;
	kGame.iTurn = 53;
	kGame.iElapsed = 24;
	kGame.iActivePlayer = 4;
	kGame.iActiveTeam = 2;
	g_kTestGlobals.pGame = &kGame;
	// <!-- custom: New/load transitions own one game counter independently from menu visits and from separately gated BBAI/SGR counters. (ChatGPT-5.6-Sol) -->
	startSASAssertionLogForNewGame();

	// <!-- custom: Cache mode 1, then mutate the backing variable to mode 2; the next failure must remain Ignore Once, proving that assertion resolution no longer rereads XML/FVariableSystem. (ChatGPT-5.6-Sol) -->
	g_kTestGlobals.kVariables.kVariable.m_iValue = SAS_ASSERT_SILENT_IGNORE_ONCE;
	cacheSASAssertionSilentPolicy();
	g_kTestGlobals.kVariables.kVariable.m_iValue = SAS_ASSERT_SILENT_IGNORE_ALWAYS;
	bIgnoreAlways = false;
	if (FAssertDlg("cached", "mode one", "cache.cpp", 20, "cacheTest", bIgnoreAlways))
		return 9;
	if (g_iDialogCount != 1 || bIgnoreAlways)
		return 10;

	g_kTestGlobals.kVariables.kVariable.m_iValue = SAS_ASSERT_SILENT_IGNORE_ALWAYS;
	cacheSASAssertionSilentPolicy();
	bIgnoreAlways = false;
	if (FAssertDlg("always", "mode two", "always.cpp", 30, "alwaysTest", bIgnoreAlways) || !bIgnoreAlways)
		return 11;
	if (g_iDialogCount != 1)
		return 12;

	g_kTestGlobals.kVariables.kVariable.m_iValue = SAS_ASSERT_SILENT_STOP_AUTO_PLAY;
	cacheSASAssertionSilentPolicy();
	kGame.iAutoPlay = 0;
	bIgnoreAlways = false;
	if (FAssertDlg("stop", "inactive autoplay", "stop.cpp", 40, "stopInactiveTest", bIgnoreAlways))
		return 13;
	if (kGame.iStopCalls != 0 || g_iDialogCount != 1)
		return 14;

	kGame.iAutoPlay = 5;
	if (FAssertDlg("stop", "active autoplay", "stop.cpp", 41, "stopActiveTest", bIgnoreAlways))
		return 15;
	if (kGame.iAutoPlay != 0 || kGame.iStopCalls != 1 || g_iDialogCount != 1)
		return 16;

	// <!-- custom: Unsupported numeric modes deliberately return to the interactive dialog; this also exercises the dialog text with the same captured turn/player context that was logged. (ChatGPT-5.6-Sol) -->
	g_kTestGlobals.kVariables.kVariable.m_iValue = 9;
	cacheSASAssertionSilentPolicy();
	g_iDialogResult = ASSERT_DLG_IGNORE;
	g_iDialogSelectedAction = ASSERT_DLG_IGNORE;
	if (FAssertDlg("invalid", "dialog fallback", "invalid.cpp", 50, "invalidTest", bIgnoreAlways))
		return 17;
	if (g_iDialogCount != 2)
		return 18;
	if (!contains(g_AssertText, "turn=53") || !contains(g_AssertText, "active/viewing player=4") || !contains(g_AssertText, "active/viewing team=2"))
		return 19;

	// <!-- custom: Retain the earlier escaped-field regression: a long control-character payload must truncate within each quoted field without overflowing the row or hiding the truncation marker. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
	g_kTestGlobals.kVariables.kVariable.m_iValue = SAS_ASSERT_SILENT_IGNORE_ONCE;
	cacheSASAssertionSilentPolicy();
	std::string szLongField(12000, '\x01');
	if (FAssertDlg(szLongField.c_str(), szLongField.c_str(), szLongField.c_str(), 60, szLongField.c_str(), bIgnoreAlways))
		return 20;
	if (g_iDialogCount != 2)
		return 21;

	// <!-- custom: Returning to the opening menu establishes _menu2 without consuming the game counter; duplicate scene requests during that visit remain in the same lazy identity. (ChatGPT-5.6-Sol) -->
	startSASAssertionLogForMainMenu();
	startSASAssertionLogForMainMenu();
	if (FAssertDlg("menu", "second menu visit", "menu.cpp", 65, "menuTest", bIgnoreAlways))
		return 22;

	// <!-- custom: A loaded-save boundary must become _load2 after _new1 despite two menu visits, and the process-wide assertion counter must continue. (ChatGPT-5.6-Sol) -->
	startSASAssertionLogForLoadedSave();
	if (FAssertDlg("loaded", "session rollover", "load.cpp", 70, "loadTest", bIgnoreAlways))
		return 23;

	// <!-- custom: Prove lazy file creation does not make numbering lazy: consume quiet _new3 without asserting, then the next loaded session must be _load4 and there must be no _new3 file. (ChatGPT-5.6-Sol) -->
	startSASAssertionLogForNewGame();
	startSASAssertionLogForLoadedSave();
	if (FAssertDlg("loaded", "quiet session numbering", "load.cpp", 80, "quietSessionTest", bIgnoreAlways))
		return 24;
	if (g_iDialogCount != 2)
		return 25;
	return 0;
}

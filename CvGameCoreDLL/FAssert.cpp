#include "CvGameCoreDll.h"

#if defined(FASSERT_ENABLE) && defined(WIN32)

#include "FDialogTemplate.h"
#include "CvGame.h" // advc.006l
#include "FVariableSystem.h" // <!-- custom: Cache the optional silent-assert define without an assertion-triggering typed getter. (ChatGPT-5.6-Sol) -->

#include <tchar.h>
#include <stdio.h>

namespace
{
	// These are the return values from the modal Assert Dialog
	enum
	{
		ASSERT_DLG_DEBUG,
		ASSERT_DLG_IGNORE,
		ASSERT_DLG_IGNOREALWAYS,
		ASSERT_DLG_STOP, // advc.006l (based on code by Erik in the WtP mod)
		ASSERT_DLG_EXIT,
	};

	// <!-- custom: Keep the configurable silent-policy values and their diagnostic names in one local catalog, following the same X-macro pattern used for other SAS enum/stringifier pairs.
	// Explicit labels omit the internal enum prefix and describe the handling policy; for example, SILENT_DISABLED is logged as DIALOG because only automatic handling is disabled.
	// Keeping those labels in the same catalog generates the enum and stringifier together without making log wording depend on C++ identifier spelling.
	// Policy remains distinct from the inherited dialog action because STOP_AUTO_PLAY can resolve to IGNORE_ONCE when autoplay is inactive.
	// Debug and Abort remain interactive-only: automatic Debug requires debugger interaction, while automatic Abort would terminate rather than continue an unattended diagnostic run. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
#define SAS_ASSERT_SILENT_POLICY_ROWS(DO) \
	DO(SAS_ASSERT_SILENT_STARTUP_DIALOG, -1, "STARTUP_DIALOG") \
	DO(SAS_ASSERT_SILENT_DISABLED, 0, "DIALOG") \
	DO(SAS_ASSERT_SILENT_IGNORE_ONCE, 1, "IGNORE_ONCE") \
	DO(SAS_ASSERT_SILENT_IGNORE_ALWAYS, 2, "IGNORE_ALWAYS") \
	DO(SAS_ASSERT_SILENT_STOP_AUTO_PLAY, 3, "STOP_AUTO_PLAY")

	enum SASAssertionSilentPolicy
	{
#define SAS_ASSERT_SILENT_POLICY_ENUM(NAME, VALUE, LABEL) NAME = VALUE,
	SAS_ASSERT_SILENT_POLICY_ROWS(SAS_ASSERT_SILENT_POLICY_ENUM)
#undef SAS_ASSERT_SILENT_POLICY_ENUM
	};

	struct SASAssertionRuntimeContext
	{
		SASAssertionRuntimeContext() : bGameObjectAvailable(false), bFinalInitialized(false), iTurn(-1), iElapsedTurns(-1), iAutoPlayRemaining(-1), iActivePlayer(-1), iActiveTeam(-1), szActivity("UNAVAILABLE") {}
		bool bGameObjectAvailable;
		bool bFinalInitialized;
		int iTurn;
		int iElapsedTurns;
		int iAutoPlayRemaining;
		int iActivePlayer;
		int iActiveTeam;
		char const* szActivity;
	};

	// This global structure is filled out by the original call to our FAssert
	// and is used by the dialog proc to display appropriate debug info
	struct AssertInfo
	{
		const char* szExpression;
		const char* szMessage;
		const char* szFileName;
		const char* szFunctionName; // advc.006f
		unsigned int line;

		// EIP / EBP / ESP
		CONTEXT context;
		// <!-- custom: Keep the actual button choice separate from DialogBox return codes; IDCANCEL can alias an inherited action when the window is dismissed. (GPT-6.1-Sol) -->
		int iSelectedAction;
		// <!-- custom: Capture one startup-safe game-context snapshot for each failed assertion and reuse it for logging, dialog decoration and Stop-Auto-Play availability instead of querying slightly different state at each stage. (ChatGPT-5.6-Sol) -->
		SASAssertionRuntimeContext kRuntimeContext;
	} g_AssertInfo;

	// Use a static array since often times asserts are fired in response to problems
	// caused by being low on resources, so dynamically creating strings here might not
	// be such a hot idea
	const unsigned int MAX_ASSERT_TEXT=65536;
	char g_AssertText[MAX_ASSERT_TEXT];

	// <!-- custom: Failed assertions are unusually valuable crash/AI evidence, but the inherited dialog kept only the last failure in memory and startup failures can occur before XML-controlled diagnostics exist.
	// Write a dedicated per-process log through native Windows file APIs before dialog/silent resolution, then record the effective action afterward; do not depend on SASGameRecord, BBAI, runtime-status or CivilizationIV.ini logging gates.
	// The sink intentionally contains no FAssert calls; runtime context is sampled only behind the logger's recursion guard, and the silent policy is a cache populated after GlobalDefines finish loading rather than an XML lookup from the failure path. (ChatGPT-5.6-Sol) -->
	const size_t SAS_ASSERT_LOG_PATH_CHARS = 1024;
	const size_t SAS_ASSERT_LOG_ROW_CHARS = 16384;
	// <!-- custom: Budget encoded bytes for the four quoted fields (file/function/expression/message), leaving room for context and the truncation marker.
	// Escaping can expand one input byte to four output bytes; reserving each field separately keeps its closing quote intact. (GPT-6.1-Sol) -->
	const size_t SAS_ASSERT_LOG_FIELD_BYTES = (SAS_ASSERT_LOG_ROW_CHARS - 1024) / 4;
	wchar_t g_szSASAssertionLogRoot[SAS_ASSERT_LOG_PATH_CHARS] = L"";
	wchar_t g_szSASAssertionLogPath[SAS_ASSERT_LOG_PATH_CHARS] = L"";
	char g_szSASAssertionLogTimestamp[32] = "";
	char g_szSASAssertionSessionStartUtc[32] = "";
	char g_szSASAssertionLogContext[32] = "startup";
	bool g_bSASAssertionLogStarted = false;
	bool g_bSASAssertionMetadataWritten = false;
	int g_iSASAssertionSessionSequence = 0;
	int g_iSASAssertionGameSequence = 0;
	int g_iSASAssertionMenuSequence = 0;
	bool g_bSASAssertionMainMenuContext = false;
	volatile LONG g_iSASAssertionLogBusy = 0;
	volatile LONG g_iSASAssertionSequence = 0;
	// <!-- custom: -1 preserves the normal dialog during startup/XML loading.
	// CvXMLLoadUtility::SetGlobalDefines replaces it only after every base/SAS/modular override has loaded; failed assertions then read this cache without touching XML/FVariableSystem. (ChatGPT-5.6-Sol) -->
	volatile LONG g_iSASAssertionSilentPolicy = SAS_ASSERT_SILENT_STARTUP_DIALOG;

	struct SASAssertionRowBuilder
	{
		SASAssertionRowBuilder(char* szBuffer, size_t iCapacity) : sz(szBuffer), iCap(iCapacity), iLen(0), bTruncated(false)
		{
			if (iCap > 0) sz[0] = '\0';
		}
		char* sz;
		size_t iCap;
		size_t iLen;
		bool bTruncated;
	};

	void appendSASAssertionBytes(SASAssertionRowBuilder& kRow, char const* szText, size_t iBytes)
	{
		if (szText == NULL || iBytes == 0 || kRow.iCap == 0)
			return;
		size_t const iAvailable = (kRow.iLen + 1 < kRow.iCap ? kRow.iCap - kRow.iLen - 1 : 0);
		size_t const iCopy = std::min(iBytes, iAvailable);
		if (iCopy > 0)
		{
			memcpy(kRow.sz + kRow.iLen, szText, iCopy);
			kRow.iLen += iCopy;
			kRow.sz[kRow.iLen] = '\0';
		}
		if (iCopy < iBytes) kRow.bTruncated = true;
	}

	void appendSASAssertionText(SASAssertionRowBuilder& kRow, char const* szText)
	{
		if (szText != NULL) appendSASAssertionBytes(kRow, szText, strlen(szText));
	}

	void appendSASAssertionInt(SASAssertionRowBuilder& kRow, int iValue)
	{
		char szValue[32];
		sprintf(szValue, "%d", iValue);
		appendSASAssertionText(kRow, szValue);
	}

	void appendSASAssertionUnsigned(SASAssertionRowBuilder& kRow, unsigned long iValue)
	{
		char szValue[32];
		sprintf(szValue, "%lu", iValue);
		appendSASAssertionText(kRow, szValue);
	}

	void appendSASAssertionQuoted(SASAssertionRowBuilder& kRow, char const* szValue)
	{
		appendSASAssertionText(kRow, "\"");
		size_t iEncodedBytes = 0;
		char const* szTruncation = "...<truncated>";
		size_t const iTruncationBytes = strlen(szTruncation);
		if (szValue != NULL)
		{
			for (char const* p = szValue; *p != '\0'; p++)
			{
				char szEscaped[5];
				switch (*p)
				{
				case '\\': strcpy(szEscaped, "\\\\"); break;
				case '"': strcpy(szEscaped, "\\\""); break;
				case '\r': strcpy(szEscaped, "\\r"); break;
				case '\n': strcpy(szEscaped, "\\n"); break;
				case '\t': strcpy(szEscaped, "\\t"); break;
				default:
					if ((unsigned char)*p < 32)
						sprintf(szEscaped, "\\x%02X", (unsigned int)(unsigned char)*p);
					else
					{
						szEscaped[0] = *p;
						szEscaped[1] = '\0';
					}
					break;
				}
				size_t const iBytes = strlen(szEscaped);
				if (iEncodedBytes + iBytes + iTruncationBytes > SAS_ASSERT_LOG_FIELD_BYTES)
				{
					appendSASAssertionText(kRow, szTruncation);
					kRow.bTruncated = true;
					break;
				}
				appendSASAssertionBytes(kRow, szEscaped, iBytes);
				iEncodedBytes += iBytes;
			}
		}
		appendSASAssertionText(kRow, "\"");
	}

	void formatSASAssertionUtc(SYSTEMTIME const& kUtc, char* szUtc, bool bCompact)
	{
		if (bCompact)
			sprintf(szUtc, "%04u%02u%02uT%02u%02u%02u%03uZ", kUtc.wYear, kUtc.wMonth, kUtc.wDay, kUtc.wHour, kUtc.wMinute, kUtc.wSecond, kUtc.wMilliseconds);
		else sprintf(szUtc, "%04u-%02u-%02uT%02u:%02u:%02u.%03uZ", kUtc.wYear, kUtc.wMonth, kUtc.wDay, kUtc.wHour, kUtc.wMinute, kUtc.wSecond, kUtc.wMilliseconds);
	}

	bool getSASAssertionProcessStartUtc(SYSTEMTIME& kUtc)
	{
		FILETIME kCreationTime, kExitTime, kKernelTime, kUserTime;
		return (GetProcessTimes(GetCurrentProcess(), &kCreationTime, &kExitTime, &kKernelTime, &kUserTime) != FALSE && FileTimeToSystemTime(&kCreationTime, &kUtc) != FALSE);
	}

	// <!-- custom: Read readiness first: turn access reaches InitCore and is inappropriate during early initialization.
	// Direct game fields avoid enabling or querying the optional runtime publisher merely to record an assertion. (GPT-6.1-Sol) -->
	void collectSASAssertionRuntimeContext(SASAssertionRuntimeContext& kContext)
	{
		// <!-- custom: GC is const in AdvCiv, while the inherited nullable game-pointer accessor is non-const; use its explicit globals instance without changing the exported accessor. (GPT-6.1-Sol) -->
		if (CvGlobals::getInstance().getGamePointer() == NULL)
			return;
		kContext.bGameObjectAvailable = true;
		CvGame const& kGame = GC.getGame();
		kContext.bFinalInitialized = kGame.isFinalInitialized();
		if (!kContext.bFinalInitialized)
			return;
		kContext.iTurn = kGame.getGameTurn();
		kContext.iElapsedTurns = kGame.getElapsedGameTurns();
		kContext.iAutoPlayRemaining = kGame.getAIAutoPlay();
		kContext.iActivePlayer = (int)kGame.getActivePlayer();
		kContext.iActiveTeam = (int)kGame.getActiveTeam();
		if (kContext.iAutoPlayRemaining > 0)
			kContext.szActivity = "AUTOPLAY";
		else if (kGame.getGameState() == GAMESTATE_OVER)
			kContext.szActivity = "GAME_OVER";
		else if (kGame.getGameState() == GAMESTATE_EXTENDED)
			kContext.szActivity = "EXTENDED_GAME";
		else kContext.szActivity = "GAMEPLAY";
	}

	char const* getSASAssertionSilentPolicyType(int iSilentPolicy)
	{
		switch (iSilentPolicy)
		{
#define SAS_ASSERT_SILENT_POLICY_LABEL(NAME, VALUE, LABEL) case NAME: return LABEL;
		SAS_ASSERT_SILENT_POLICY_ROWS(SAS_ASSERT_SILENT_POLICY_LABEL)
#undef SAS_ASSERT_SILENT_POLICY_LABEL
		default: return "DIALOG_INVALID";
		}
	}

	bool isSASAssertionSilentPolicyAutomatic(int iSilentPolicy)
	{
		return (iSilentPolicy >= SAS_ASSERT_SILENT_IGNORE_ONCE && iSilentPolicy <= SAS_ASSERT_SILENT_STOP_AUTO_PLAY);
	}

	bool canSASAssertionStopAutoPlay(SASAssertionRuntimeContext const& kContext)
	{
		return (kContext.bFinalInitialized && kContext.iAutoPlayRemaining > 0);
	}

	DWORD resolveSASAssertionSilentAction(int iSilentPolicy, SASAssertionRuntimeContext const& kContext)
	{
		switch (iSilentPolicy)
		{
		case SAS_ASSERT_SILENT_IGNORE_ONCE: return ASSERT_DLG_IGNORE;
		case SAS_ASSERT_SILENT_IGNORE_ALWAYS: return ASSERT_DLG_IGNOREALWAYS;
		case SAS_ASSERT_SILENT_STOP_AUTO_PLAY:
			return (canSASAssertionStopAutoPlay(kContext) ? ASSERT_DLG_STOP : ASSERT_DLG_IGNORE);
		}
		return ASSERT_DLG_DEBUG;
	}

	char const* getSASAssertionSilentFallback(int iSilentPolicy, DWORD dwAction, bool bAutomatic)
	{
		if (bAutomatic && iSilentPolicy == SAS_ASSERT_SILENT_STOP_AUTO_PLAY && dwAction == ASSERT_DLG_IGNORE)
			return "AUTOPLAY_INACTIVE";
		return "-";
	}

	void formatSASAssertionRuntimeContext(SASAssertionRuntimeContext const& kContext, char* szBuffer, size_t iCapacity)
	{
		if (iCapacity == 0)
			return;
		if (!kContext.bGameObjectAvailable)
			_snprintf(szBuffer, iCapacity - 1, "UNAVAILABLE (no CvGame object yet)");
		else if (!kContext.bFinalInitialized)
			_snprintf(szBuffer, iCapacity - 1, "UNAVAILABLE (CvGame not final-initialized)");
		else
		{
			_snprintf(szBuffer, iCapacity - 1, "activity=%s, turn=%d, elapsed=%d, autoplay remaining=%d, active/viewing player=%d, active/viewing team=%d",
					kContext.szActivity, kContext.iTurn, kContext.iElapsedTurns, kContext.iAutoPlayRemaining, kContext.iActivePlayer, kContext.iActiveTeam);
		}
		szBuffer[iCapacity - 1] = '\0';
	}

	void formatSASAssertionDialogText()
	{
		char szContext[512];
		formatSASAssertionRuntimeContext(g_AssertInfo.kRuntimeContext, szContext, sizeof(szContext));
		// <!-- custom: The modal text reuses the exact context snapshot already attached to the failure row; "active/viewing" avoids implying that this identifies whichever player/object was processing when the assertion fired. (ChatGPT-5.6-Sol) -->
		_snprintf(g_AssertText, MAX_ASSERT_TEXT - 1, "Assert Failed\r\n\r\n"
			"File:  %s\r\n"
			"Line:  %u\r\n"
			"Func:  %s\r\n" // advc.006f
			"Expression:  %s\r\n"
			"Message:  %s\r\n"
			"Game Context:  %s\r\n"
			"\r\n"
			"----------------------------------------------------------\r\n",
			g_AssertInfo.szFileName,
			g_AssertInfo.line,
			g_AssertInfo.szFunctionName, // advc.006f
			g_AssertInfo.szExpression,
			g_AssertInfo.szMessage ? g_AssertInfo.szMessage : "",
			szContext);
		g_AssertText[MAX_ASSERT_TEXT - 1] = '\0';
	}

	// <!-- custom: Keep assertion filenames aligned with the existing diagnostic session vocabulary without eagerly creating empty files.
	// Startup uses the process-creation timestamp; actual opening-menu scene requests establish _menuN, while each new/load boundary advances a separate process-local game counter.
	// The assertion logger intentionally owns these counters instead of mutating BBAI/SGR lifecycle state, so suffix numbers are meaningful within this log family but are not promised to match another independently gated logger. (ChatGPT-5.6-Sol) -->
	void initializeSASAssertionStartupIdentity()
	{
		if (g_szSASAssertionLogTimestamp[0] != '\0')
			return;
		SYSTEMTIME kStartUtc;
		if (!getSASAssertionProcessStartUtc(kStartUtc))
			GetSystemTime(&kStartUtc);
		formatSASAssertionUtc(kStartUtc, g_szSASAssertionLogTimestamp, true);
		formatSASAssertionUtc(kStartUtc, g_szSASAssertionSessionStartUtc, false);
	}

	void rollSASAssertionLog(char const* szContext, int iSequence)
	{
		SYSTEMTIME kNowUtc;
		GetSystemTime(&kNowUtc);
		formatSASAssertionUtc(kNowUtc, g_szSASAssertionLogTimestamp, true);
		formatSASAssertionUtc(kNowUtc, g_szSASAssertionSessionStartUtc, false);
		g_iSASAssertionSessionSequence = iSequence;
		_snprintf(g_szSASAssertionLogContext, sizeof(g_szSASAssertionLogContext) - 1, "%s%d", szContext, g_iSASAssertionSessionSequence);
		g_szSASAssertionLogContext[sizeof(g_szSASAssertionLogContext) - 1] = '\0';
		g_szSASAssertionLogPath[0] = L'\0';
		g_bSASAssertionMetadataWritten = false;
	}

	bool ensureSASAssertionLogPath()
	{
		if (g_szSASAssertionLogPath[0] != L'\0')
			return true;
		if (g_szSASAssertionLogRoot[0] == L'\0')
		{
			std::wstring szRoot;
			if (!getSASNativeDefaultRootDirectory(szRoot) || szRoot.length() >= SAS_ASSERT_LOG_PATH_CHARS)
				return false;
			wcscpy(g_szSASAssertionLogRoot, szRoot.c_str());
		}
		wchar_t szLogDirectory[SAS_ASSERT_LOG_PATH_CHARS];
		int const iDirectoryChars = _snwprintf(szLogDirectory, SAS_ASSERT_LOG_PATH_CHARS - 1, L"%ls\\Logs", g_szSASAssertionLogRoot);
		szLogDirectory[SAS_ASSERT_LOG_PATH_CHARS - 1] = L'\0';
		if (iDirectoryChars < 0 || (size_t)iDirectoryChars >= SAS_ASSERT_LOG_PATH_CHARS - 1)
			return false;
		if (!CreateDirectoryW(szLogDirectory, NULL) && GetLastError() != ERROR_ALREADY_EXISTS)
			return false;
		initializeSASAssertionStartupIdentity();
		wchar_t szCompactUtcWide[32];
		wchar_t szContextWide[32];
		size_t iI = 0;
		for (; g_szSASAssertionLogTimestamp[iI] != '\0' && iI + 1 < sizeof(szCompactUtcWide) / sizeof(szCompactUtcWide[0]); iI++)
			szCompactUtcWide[iI] = (wchar_t)(unsigned char)g_szSASAssertionLogTimestamp[iI];
		szCompactUtcWide[iI] = L'\0';
		iI = 0;
		for (; g_szSASAssertionLogContext[iI] != '\0' && iI + 1 < sizeof(szContextWide) / sizeof(szContextWide[0]); iI++)
			szContextWide[iI] = (wchar_t)(unsigned char)g_szSASAssertionLogContext[iI];
		szContextWide[iI] = L'\0';
		// <!-- custom: Match the established BBAI/SASGameRecord filename shape: early failures stay in _startup, while established games use _newN/_loadN and the process-wide assertion number still links chronology across files. (ChatGPT-5.6-Sol) -->
		int const iPathChars = _snwprintf(g_szSASAssertionLogPath, SAS_ASSERT_LOG_PATH_CHARS - 1, L"%ls\\SASAssertions_%ls_%ls.log", szLogDirectory, szCompactUtcWide, szContextWide);
		g_szSASAssertionLogPath[SAS_ASSERT_LOG_PATH_CHARS - 1] = L'\0';
		if (iPathChars < 0 || (size_t)iPathChars >= SAS_ASSERT_LOG_PATH_CHARS - 1)
		{
			g_szSASAssertionLogPath[0] = L'\0';
			return false;
		}
		return true;
	}

	// <!-- custom: Submit and close each exceptional row before returning to the dialog; Abort must not rely on a later game/session flush.
	// Shared-read access permits inspection while Civ4 remains paused at the assertion; failed appends fall back to debugger output without asserting again. (GPT-6.1-Sol) -->
	bool writeSASAssertionRow(char const* szRow)
	{
		bool bSuccess = false;
		if (ensureSASAssertionLogPath())
		{
			HANDLE const hFile = CreateFileW(g_szSASAssertionLogPath, FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
			if (hFile != INVALID_HANDLE_VALUE)
			{
				char szOutput[SAS_ASSERT_LOG_ROW_CHARS];
				size_t const iRowBytes = strlen(szRow);
				size_t const iCopy = std::min(iRowBytes, SAS_ASSERT_LOG_ROW_CHARS - 3);
				memcpy(szOutput, szRow, iCopy);
				szOutput[iCopy] = '\r';
				szOutput[iCopy + 1] = '\n';
				DWORD iWritten = 0;
				bSuccess = (WriteFile(hFile, szOutput, (DWORD)(iCopy + 2), &iWritten, NULL) != FALSE && iWritten == iCopy + 2);
				CloseHandle(hFile);
				// <!-- custom: Even a partial append leaves evidence at this root; do not move the following choice row to a different directory. (GPT-6.1-Sol) -->
				if (iWritten > 0) g_bSASAssertionLogStarted = true;
			}
		}
		if (!bSuccess)
		{
			OutputDebugStringA("AdvCiv-SAS assertion log append failed; assertion details follow in debugger output.\n");
			OutputDebugStringA(szRow);
			OutputDebugStringA("\n");
		}
		return bSuccess;
	}

	// <!-- custom: Emit one lazy metadata row per assertion file before its first failure so a standalone upload identifies process/session scope, handling policy and the exact loaded DLL.
	// The runtime DLL helper deliberately omits current build-tree scans; live readability comes from open/append/close with FILE_SHARE_READ rather than FlushFileBuffers. (ChatGPT-5.6-Sol) -->
	void writeSASAssertionMetadata(int iSilentPolicy, char const* szUtc, char const* szProcessStartUtc)
	{
		if (g_bSASAssertionMetadataWritten)
			return;
		initializeSASAssertionStartupIdentity();
		char szRow[SAS_ASSERT_LOG_ROW_CHARS];
		SASAssertionRowBuilder kRow(szRow, SAS_ASSERT_LOG_ROW_CHARS - 64);
		appendSASAssertionText(kRow, szUtc);
		appendSASAssertionText(kRow, " record=SAS_ASSERT_METADATA");
		appendSASAssertionText(kRow, " pid="); appendSASAssertionUnsigned(kRow, (unsigned long)GetCurrentProcessId());
		appendSASAssertionText(kRow, " tid="); appendSASAssertionUnsigned(kRow, (unsigned long)GetCurrentThreadId());
		appendSASAssertionText(kRow, " processStartUtc="); appendSASAssertionText(kRow, szProcessStartUtc);
		appendSASAssertionText(kRow, " session="); appendSASAssertionText(kRow, g_szSASAssertionLogContext);
		appendSASAssertionText(kRow, " sessionSequence="); appendSASAssertionInt(kRow, g_iSASAssertionSessionSequence);
		appendSASAssertionText(kRow, " sessionStartUtc="); appendSASAssertionText(kRow, g_szSASAssertionSessionStartUtc);
		appendSASAssertionText(kRow, " assertionsEnabled=1");
		appendSASAssertionText(kRow, " initialSilentMode="); appendSASAssertionInt(kRow, iSilentPolicy);
		appendSASAssertionText(kRow, " initialSilentPolicy="); appendSASAssertionText(kRow, getSASAssertionSilentPolicyType(iSilentPolicy));
		appendSASAssertionText(kRow, " writer=OPEN_APPEND_CLOSE liveReadable=1 forcedPhysicalFlush=0 ");
		appendSASAssertionText(kRow, getSASDllRuntimeContextFields().GetCString());
		if (kRow.bTruncated)
		{
			kRow.iCap = SAS_ASSERT_LOG_ROW_CHARS;
			appendSASAssertionText(kRow, " rowTruncated=1");
		}
		if (writeSASAssertionRow(szRow))
			g_bSASAssertionMetadataWritten = true;
	}

	void logSASAssertionEvent(char const* szRecord, unsigned long iAssertion, int iSilentPolicy, char const* szChoice, long iDialogResult, char const* szAction, bool bAutomatic, bool bDialogShown, bool bCollectRuntimeContext)
	{
		// <!-- custom: Guard the whole event path, not only disk I/O, so an unexpected assertion in context/path collection cannot recursively enter the assertion logger. (ChatGPT-5.6-Sol) -->
		if (InterlockedCompareExchange(&g_iSASAssertionLogBusy, 1, 0) != 0)
		{
			OutputDebugStringA("AdvCiv-SAS assertion log skipped a recursive/concurrent event.\n");
			return;
		}
		SYSTEMTIME kNowUtc;
		GetSystemTime(&kNowUtc);
		char szUtc[32];
		formatSASAssertionUtc(kNowUtc, szUtc, false);
		if (bCollectRuntimeContext)
		{
			SYSTEMTIME kProcessStartUtc;
			char szProcessStartUtc[32];
			bool const bProcessStartKnown = getSASAssertionProcessStartUtc(kProcessStartUtc);
			// <!-- custom: Process-start identity belongs to the per-file metadata row, not every event; query it only on failure paths that may need to create/retry metadata. (ChatGPT-5.6-Sol) -->
			if (bProcessStartKnown) formatSASAssertionUtc(kProcessStartUtc, szProcessStartUtc, false);
			else strcpy(szProcessStartUtc, "UNAVAILABLE");
			// <!-- custom: Metadata retries only on failure rows; if its first append fails, never insert a retry between an already-written failure and its paired choice. (ChatGPT-5.6-Sol) -->
			writeSASAssertionMetadata(iSilentPolicy, szUtc, szProcessStartUtc);
		}
		if (bCollectRuntimeContext)
		{
			g_AssertInfo.kRuntimeContext = SASAssertionRuntimeContext();
			collectSASAssertionRuntimeContext(g_AssertInfo.kRuntimeContext);
		}
		SASAssertionRuntimeContext const& kContext = g_AssertInfo.kRuntimeContext;
		char szRow[SAS_ASSERT_LOG_ROW_CHARS];
		// <!-- custom: Reserve a small tail so truncation itself remains explicit; assertion text can be user/mod supplied and is bounded independently from the dialog's larger display buffer. (ChatGPT-5.6-Sol) -->
		SASAssertionRowBuilder kRow(szRow, SAS_ASSERT_LOG_ROW_CHARS - 64);
		appendSASAssertionText(kRow, szUtc);
		appendSASAssertionText(kRow, " record="); appendSASAssertionText(kRow, szRecord);
		appendSASAssertionText(kRow, " assertion="); appendSASAssertionUnsigned(kRow, iAssertion);
		// <!-- custom: Fixed process/DLL/session-start identity lives in SAS_ASSERT_METADATA; event rows retain thread plus compact session identity because either can matter when excerpts are copied or multiple threads assert. (ChatGPT-5.6-Sol) -->
		appendSASAssertionText(kRow, " tid="); appendSASAssertionUnsigned(kRow, (unsigned long)GetCurrentThreadId());
		appendSASAssertionText(kRow, " session="); appendSASAssertionText(kRow, g_szSASAssertionLogContext);
		appendSASAssertionText(kRow, " sessionSequence="); appendSASAssertionInt(kRow, g_iSASAssertionSessionSequence);
		appendSASAssertionText(kRow, " activity="); appendSASAssertionText(kRow, kContext.szActivity);
		appendSASAssertionText(kRow, " gameObjectAvailable="); appendSASAssertionInt(kRow, kContext.bGameObjectAvailable ? 1 : 0);
		appendSASAssertionText(kRow, " finalInitialized="); appendSASAssertionInt(kRow, kContext.bFinalInitialized ? 1 : 0);
		appendSASAssertionText(kRow, " turn="); appendSASAssertionInt(kRow, kContext.iTurn);
		appendSASAssertionText(kRow, " elapsed="); appendSASAssertionInt(kRow, kContext.iElapsedTurns);
		appendSASAssertionText(kRow, " autoPlayRemaining="); appendSASAssertionInt(kRow, kContext.iAutoPlayRemaining);
		appendSASAssertionText(kRow, " activePlayer="); appendSASAssertionInt(kRow, kContext.iActivePlayer);
		appendSASAssertionText(kRow, " activeTeam="); appendSASAssertionInt(kRow, kContext.iActiveTeam);
		appendSASAssertionText(kRow, " silentMode="); appendSASAssertionInt(kRow, iSilentPolicy);
		appendSASAssertionText(kRow, " silentPolicy="); appendSASAssertionText(kRow, getSASAssertionSilentPolicyType(iSilentPolicy));
		if (szChoice != NULL)
		{
			appendSASAssertionText(kRow, " choice="); appendSASAssertionText(kRow, szChoice);
			appendSASAssertionText(kRow, " action="); appendSASAssertionText(kRow, szAction);
			appendSASAssertionText(kRow, " automatic="); appendSASAssertionInt(kRow, bAutomatic ? 1 : 0);
			appendSASAssertionText(kRow, " silentFallback="); appendSASAssertionText(kRow, getSASAssertionSilentFallback(iSilentPolicy, (DWORD)iDialogResult, bAutomatic));
			appendSASAssertionText(kRow, " actionCode="); appendSASAssertionInt(kRow, (int)iDialogResult);
			appendSASAssertionText(kRow, " dialogShown="); appendSASAssertionInt(kRow, bDialogShown ? 1 : 0);
			appendSASAssertionText(kRow, " dialogResult="); appendSASAssertionInt(kRow, bDialogShown ? (int)iDialogResult : -1);
		}
		appendSASAssertionText(kRow, " file="); appendSASAssertionQuoted(kRow, g_AssertInfo.szFileName);
		appendSASAssertionText(kRow, " line="); appendSASAssertionUnsigned(kRow, (unsigned long)g_AssertInfo.line);
		appendSASAssertionText(kRow, " function="); appendSASAssertionQuoted(kRow, g_AssertInfo.szFunctionName);
		appendSASAssertionText(kRow, " expression="); appendSASAssertionQuoted(kRow, g_AssertInfo.szExpression);
		appendSASAssertionText(kRow, " message="); appendSASAssertionQuoted(kRow, g_AssertInfo.szMessage);
		if (kRow.bTruncated)
		{
			// <!-- custom: The builder reserves this tail specifically so truncation remains machine-visible even when assertion text fills the ordinary row budget. (ChatGPT-5.6-Sol) -->
			kRow.iCap = SAS_ASSERT_LOG_ROW_CHARS;
			appendSASAssertionText(kRow, " rowTruncated=1");
		}
		writeSASAssertionRow(szRow);
		InterlockedExchange(&g_iSASAssertionLogBusy, 0);
	}

	char const* getSASAssertionChoice(DWORD dwResult)
	{
		switch (dwResult)
		{
		case ASSERT_DLG_DEBUG: return "DEBUG";
		case ASSERT_DLG_IGNORE: return "IGNORE_ONCE";
		case ASSERT_DLG_IGNOREALWAYS: return "IGNORE_ALWAYS";
		case ASSERT_DLG_STOP: return "STOP_AUTO_PLAY";
		case ASSERT_DLG_EXIT: return "ABORT";
		}
		return "UNKNOWN";
	}

#undef SAS_ASSERT_SILENT_POLICY_ROWS

	// Some Resource IDs for our dialog template
#define IDC_IGNORE_ALWAYS               1001
#define IDC_IGNORE_ONCE                 1002
#define IDC_DEBUG                       1003
#define IDC_ABORT                       1004
#define IDC_ASSERTION_TEXT              1005
#define IDC_COPY_TO_CLIPBOARD           1006
#define IDC_STOP                        1007 // advc.006l

	// <!-- custom: Observe explicit buttons without changing the inherited EndDialog result or action handling.
	// Window dismissal and dialog-creation failure must not be mislabeled as an Ignore Always button click. (GPT-6.1-Sol) -->
	void finishSASAssertionDialog(HWND hDlg, int iAction)
	{
		g_AssertInfo.iSelectedAction = iAction;
		EndDialog(hDlg, iAction);
	}

	INT_PTR CALLBACK AssertDlgProc(HWND hDlg, UINT msg,WPARAM wParam, LPARAM lParam)
	{
		switch(msg)
		{
		case WM_INITDIALOG:
			{
				char modulePath[MAX_PATH];
				GetModuleFileName(NULL, modulePath, MAX_PATH);

				const char* moduleName = strrchr(modulePath, '\\');
				moduleName = moduleName ? moduleName+1 : modulePath;

				char title[MAX_PATH + 20];
				sprintf(title, "Assert Failed: %s", moduleName);
				SetWindowText(hDlg, title);

				formatSASAssertionDialogText();

				::SetWindowText( ::GetDlgItem(hDlg, IDC_ASSERTION_TEXT), g_AssertText );
				::SetFocus( ::GetDlgItem(hDlg, IDC_DEBUG) );

				break;
			}
		case WM_COMMAND:
			{
				switch(LOWORD(wParam))
				{
				case IDC_DEBUG:
					finishSASAssertionDialog(hDlg, ASSERT_DLG_DEBUG);
					return TRUE;

				case IDC_IGNORE_ONCE:
					finishSASAssertionDialog(hDlg, ASSERT_DLG_IGNORE);
					return TRUE;

				case IDC_IGNORE_ALWAYS:
					finishSASAssertionDialog(hDlg, ASSERT_DLG_IGNOREALWAYS);
					return TRUE;

				case IDC_ABORT:
					finishSASAssertionDialog(hDlg, ASSERT_DLG_EXIT);
					return TRUE;
				// <advc.006l>
				case IDC_STOP:
					finishSASAssertionDialog(hDlg, ASSERT_DLG_STOP);
					return TRUE; // </advc.006l>
				}
			}
			break;
		}

		return FALSE;
	}

	DWORD DisplayAssertDialog()
	{
		int const iTotalW = 379; // (advc.006l - as in BtS)
		CDialogTemplate dialogTemplate(_T("Assert Failed!"),
				DS_SETFONT | DS_CENTER | DS_MODALFRAME | DS_FIXEDSYS | WS_POPUP |
				WS_CAPTION | WS_SYSMENU,
				0, 0, iTotalW, 166, _T("MS Shell Dlg"), 8);
		// <advc>
		int const iBtnY = 145, iBtnH = 14, iLMargin = 7,
				iBtnW = /*64*/63, iSpacing = /*11*/10; // advc.006l
		int iIncrX = iBtnW + iSpacing;
		//int iBtnX = iLMargin + iIncrX; // </advc>
		// <advc.006l> Center-align instead
		int iTotalBtnW = 4 * iIncrX;
		// <!-- custom: Assertion logging also covers startup; the game object can be absent before the inherited dialog asks whether Stop Auto Play applies. (ChatGPT-5.6-Sol) -->
		bool const bShowStopBtn = canSASAssertionStopAutoPlay(g_AssertInfo.kRuntimeContext);
		if (bShowStopBtn)
			iTotalBtnW += iIncrX;
		int iBtnX = (iTotalW - iTotalBtnW) / 2; // </advc.006l>
		dialogTemplate.AddButton( _T("&Ignore Once"), WS_VISIBLE, 0,
				iBtnX, iBtnY, iBtnW, iBtnH, IDC_IGNORE_ONCE );
		iBtnX += iIncrX;
		dialogTemplate.AddButton( _T("Ignore Always"), WS_VISIBLE, 0,
				iBtnX, iBtnY, iBtnW, iBtnH, IDC_IGNORE_ALWAYS );
		// <advc.006l>
		if (bShowStopBtn)
		{
			iBtnX += iIncrX;
			dialogTemplate.AddButton(_T("&Stop Auto Play"), WS_VISIBLE, 0,
					iBtnX, iBtnY, iBtnW, iBtnH, IDC_STOP);
		} // </advc.006l>
		iBtnX += iIncrX;
		dialogTemplate.AddButton( _T("&Abort"), WS_VISIBLE, 0,
				iBtnX, iBtnY, iBtnW, iBtnH, IDC_ABORT );
		iBtnX += iIncrX;
		dialogTemplate.AddButton( _T("&Debug"), WS_VISIBLE, 0,
				iBtnX, iBtnY, iBtnW, iBtnH, IDC_DEBUG );
		dialogTemplate.AddEditBox( _T(""),
				ES_MULTILINE | ES_AUTOVSCROLL | ES_AUTOHSCROLL | ES_READONLY |
				WS_VSCROLL | WS_HSCROLL | WS_VISIBLE, WS_EX_STATICEDGE,
				iLMargin, iLMargin, 365, 130, IDC_ASSERTION_TEXT );
		int iRes = DialogBoxIndirect(GetModuleHandle(0),
				dialogTemplate.GetDialogTemplate(), NULL, (DLGPROC)AssertDlgProc);
		return iRes;
	}

} // end anonymous namespace

// <!-- custom: Cache the optional silent policy only after SetGlobalDefines has applied every base/SAS/modular override.
// Direct FVariable inspection keeps a missing/wrong-type setting from asserting during cache initialization; later assertion failures read only this process cache. (ChatGPT-5.6-Sol) -->
void cacheSASAssertionSilentPolicy()
{
	int iPolicy = SAS_ASSERT_SILENT_DISABLED;
	FVariableSystem const* pVariables = GC.getDefinesVarSystem();
	if (pVariables != NULL)
	{
		FVariable const* pVariable = pVariables->GetVariable("SAS_ASSERT_SILENT_ACTION");
		if (pVariable != NULL && pVariable->m_eType == FVARTYPE_INT)
			iPolicy = pVariable->m_iValue;
	}
	InterlockedExchange(&g_iSASAssertionSilentPolicy, iPolicy);
}

// <!-- custom: Advance assertion session identity at lifecycle boundaries even when that session never creates a file.
// New/load share one assertion-owned game counter (_new1, _load2, _new3); opening-menu visits use their own _menuN counter so returning to the menu does not consume game numbers.
// BBAI/SGR counters remain independent because those loggers are separately gated; timestamps/process identity, not equal numeric suffixes, are the cross-log correlation contract. (ChatGPT-5.6-Sol) -->
void startSASAssertionLogForMainMenu()
{
	if (g_bSASAssertionMainMenuContext)
		return;
	g_bSASAssertionMainMenuContext = true;
	rollSASAssertionLog("menu", ++g_iSASAssertionMenuSequence);
}

void startSASAssertionLogForNewGame()
{
	g_bSASAssertionMainMenuContext = false;
	rollSASAssertionLog("new", ++g_iSASAssertionGameSequence);
}

void startSASAssertionLogForLoadedSave()
{
	g_bSASAssertionMainMenuContext = false;
	rollSASAssertionLog("load", ++g_iSASAssertionGameSequence);
}

// <!-- custom: BUG can supply the authoritative Unicode Civ4 user/CvAltRoot before the first assertion.
// Once a failure has been written, keep that root for the rest of the process so its failure/choice sequence cannot split across directories. (ChatGPT-5.6-Sol) -->
void setSASAssertionLogRootDirectory(wchar_t const* szRootDirectory)
{
	if (g_bSASAssertionLogStarted || szRootDirectory == NULL || szRootDirectory[0] == L'\0')
		return;
	size_t iLength = wcslen(szRootDirectory);
	while (iLength > 3 && (szRootDirectory[iLength - 1] == L'\\' || szRootDirectory[iLength - 1] == L'/')) iLength--;
	if (iLength == 0 || iLength >= SAS_ASSERT_LOG_PATH_CHARS)
		return;
	wcsncpy(g_szSASAssertionLogRoot, szRootDirectory, iLength);
	g_szSASAssertionLogRoot[iLength] = L'\0';
	// <!-- custom: A prior failed fallback attempt may already have composed a path; rebuild it against BUG's root on the next assertion. (ChatGPT-5.6-Sol) -->
	g_szSASAssertionLogPath[0] = L'\0';
}

bool FAssertDlg(const char* szExpr, const char* szMsg, const char* szFile, unsigned int line, /* <advc.006f> */ const char* szFunction, /* </advc006f> */ bool& bIgnoreAlways)
{
	g_AssertInfo.szExpression = szExpr;
	g_AssertInfo.szMessage = szMsg;
	g_AssertInfo.szFileName = szFile;
	g_AssertInfo.szFunctionName = szFunction; // advc.006f
	g_AssertInfo.line = line;
	// <!-- custom: AssertInfo persists across failures; clear the prior button marker so closing/failing the next dialog cannot be reported as whichever explicit button was pressed last time. (GPT-6.1-Sol + ChatGPT-5.6-Sol) -->
	g_AssertInfo.iSelectedAction = -1;

	// <!-- custom: Persist the failed condition and capture one safe runtime snapshot before any modal interaction so Abort, a debugger break or a later process failure cannot erase the evidence.
	// The silent policy is a cache: -1 means SetGlobalDefines has not finished and therefore keeps the inherited startup dialog; 0/default/invalid values show the dialog, while 1..3 select the documented automatic continuation policies. (ChatGPT-5.6-Sol) -->
	int const iSilentPolicy = (int)g_iSASAssertionSilentPolicy;
	bool const bAutomatic = isSASAssertionSilentPolicyAutomatic(iSilentPolicy);
	unsigned long const iAssertion = (unsigned long)InterlockedIncrement(&g_iSASAssertionSequence);
	g_AssertInfo.kRuntimeContext = SASAssertionRuntimeContext();
	logSASAssertionEvent("SAS_ASSERT_FAILURE", iAssertion, iSilentPolicy, NULL, 0, NULL, false, false, true);
	DWORD dwResult;
	char const* szChoice;
	if (bAutomatic)
	{
		dwResult = resolveSASAssertionSilentAction(iSilentPolicy, g_AssertInfo.kRuntimeContext);
		szChoice = "AUTOMATIC";
	}
	else
	{
		dwResult = DisplayAssertDialog();
		// <!-- custom: DialogBox can return IDCANCEL (2) without a button, which aliases the inherited IGNOREALWAYS result.
		// Preserve that behavior but record the actual interaction separately from the effective action; other unrecognized results retain the inherited debugger-break path. (GPT-6.1-Sol) -->
		szChoice = (g_AssertInfo.iSelectedAction >= 0 ? getSASAssertionChoice((DWORD)g_AssertInfo.iSelectedAction) : ((long)dwResult == -1 ? "DIALOG_FAILED" : "DISMISSED"));
	}
	char const* szAction = (dwResult <= ASSERT_DLG_EXIT ? getSASAssertionChoice(dwResult) : "DEBUG");
	logSASAssertionEvent("SAS_ASSERT_CHOICE", iAssertion, iSilentPolicy, szChoice, (long)dwResult, szAction, bAutomatic, (!bAutomatic && (long)dwResult != -1), false);

	switch( dwResult )
	{
	case ASSERT_DLG_DEBUG:
		return true;

	case ASSERT_DLG_IGNORE:
		return false;

	case ASSERT_DLG_IGNOREALWAYS:
		bIgnoreAlways = true;
		return false;
	// <advc.006l>
	case ASSERT_DLG_STOP:
		GC.getGame().setAIAutoPlay(0, true, SAS_AUTOPLAY_END_ASSERTION);
		return false; // </advc.006l>

	case ASSERT_DLG_EXIT:
		exit(0);
		break;
	/*	<advc.wine> DisplayAssertDialog goes through DialogBoxIndirect (WinUser.h).
		I had assumed that Wine won't display that - but it does, so nvm.  */
	/*default:	
		printf("FAssertDlg: {%s} %s in %s, %s, line %d",
				szExpr, szMsg, szFile, szFunction, line);*/ // </advc.wine>
	}

	return true;
}

#endif // FASSERT_ENABLE && WIN32

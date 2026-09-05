#include "CvGameCoreDLL.h"
#include "SASGameRecordLog.h"
#include <algorithm>
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

// <!-- custom: Commit 1 keeps the recorder deliberately dormant and self-contained on base AdvCiv 1.14. The mature AdvCiv-SAS session/log-name helpers are transplanted in later lifecycle commits; this small UTC helper only gives the dormant core a valid standalone filename implementation in the meantime. (ChatGPT-5.6-Sol) -->
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

static CvString const& getSASGameRecordLogTimestamp()
{
	static const CvString szTimestamp = createSASGameRecordUtcTimestamp();
	return szTimestamp;
}

static bool isSASGameRecordTimestampedFilenameEnabled()
{
	static const bool bUseTimestampedFilename = (GC.getDefineINT("SAS_GAME_RECORD_LOG_USE_TIMESTAMPED_FILENAME") > 0);
	return bUseTimestampedFilename;
}

// <!-- custom: Temporary dormant-core naming shim for commit 1; later lifecycle wiring replaces it with the mature shared diagnostic filename/context path from AdvCiv-SAS. (ChatGPT-5.6-Sol) -->
static CvString getSASGameRecordLogName()
{
	if (!isSASGameRecordTimestampedFilenameEnabled())
		return CvString("SASGameRecord.log");
	CvString szName;
	szName.Format("SASGameRecord_%s.log", getSASGameRecordLogTimestamp().GetCString());
	return szName;
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

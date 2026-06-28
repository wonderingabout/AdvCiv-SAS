#include "CvGameCoreDLL.h"
#include "BBAILog.h"
// <advc.133>
#include "CvGameTextMgr.h"
#include "CvGamePlay.h" // </advc.133>
// <!-- custom: Added for UTC session timestamps in timestamped BBAI log filenames. (ChatGPT-5.5) -->
#include <time.h>

// AI decision making logging

static int getClampedSASBBAILogLevel(char const* szDefineName)
{
	const int iLevel = GC.getDefineINT(szDefineName);
	if (iLevel < 0)
		return 0;
	if (iLevel > 3)
		return 3;
	return iLevel;
}

// <!-- custom: Cache each effective XML-backed log setting on first use for cheap hot-path checks. (GPT-5.5?) -->
bool isSASBBAILogEnabled()
{
	static const bool bEnabled = (isSASBBAILogMasterEnabled() && (getSASBBAIPlayerLogLevel() > 0 || getSASBBAITeamLogLevel() > 0 || getSASBBAICityLogLevel() > 0 || getSASBBAIUnitLogLevel() > 0 || getSASBBAIWorkerLogLevel() > 0 || getSASBBAIWorkerSeaLogLevel() > 0 || getSASBBAIMapLogLevel() > 0 || getSASBBAIFoundLogLevel() > 0 || getSASBBAIDealCancelLogLevel() > 0 || getSASBBAICultureLogLevel() > 0));
	return bEnabled;
}

bool isSASBBAILogMasterEnabled()
{
	static const bool bEnabled = (GC.getDefineINT("SAS_BBAI_LOG_ENABLE") > 0);
	return bEnabled;
}

int getSASBBAIPlayerLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_PLAYER_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAITeamLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_TEAM_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAICityLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_CITY_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAIUnitLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_UNIT_LOG_LEVEL") : 0);
	return iLevel;
}

// <!-- custom: New Land-worker BBAI log level for Worker AI build, movement, and improvement-replacement diagnostics. This keeps WORKER_* diagnostics out of the general UNIT category, so UNIT can stay focused on non-worker unit AI. (ChatGPT-5.5 + GPT-5.5 review) -->
int getSASBBAIWorkerLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_WORKER_LOG_LEVEL") : 0);
	return iLevel;
}

// <!-- custom: New Worker-sea/Work Boat BBAI log level for UNITAI_WORKER_SEA production, target, audit, movement, and sea-improvement diagnostics. This separates noisy Work Boat diagnostics from both CITY and UNIT logging. (ChatGPT-5.5 + GPT-5.5 review) -->
int getSASBBAIWorkerSeaLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_WORKER_SEA_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAIMapLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_MAP_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAIFoundLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_FOUND_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAIDealCancelLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_DEAL_CANCEL_LOG_LEVEL") : 0);
	return iLevel;
}

// <!-- custom: Separate culture-victory BBAI log level so culture-slider, victory-stage, and city-target diagnostics can be enabled without turning on broad player/city logging. (ChatGPT-5.5) -->
int getSASBBAICultureLogLevel()
{
	static const int iLevel = (isSASBBAILogMasterEnabled() ? getClampedSASBBAILogLevel("SAS_BBAI_CULTURE_LOG_LEVEL") : 0);
	return iLevel;
}

int getSASBBAIScoreLogInterval()
{
	// <!-- custom: When the master switch is disabled, return 1 rather than 0 because this value can be used as a modulo divisor. (GPT-5.5?) -->
	static const int iInterval = (isSASBBAILogMasterEnabled() ? std::max(1, GC.getDefineINT("SAS_BBAI_SCORE_LOG_INTERVAL")) : 1);
	return iInterval;
}

static CvString getSASBBAILogSessionTimestamp()
{
	static CvString szTimestamp;
	if (szTimestamp.empty())
	{
		char szBuffer[32];
		time_t kNow;
		time(&kNow);
		struct tm* pUtcTime = gmtime(&kNow);
		if (pUtcTime != NULL && strftime(szBuffer, sizeof(szBuffer), "%Y%m%dT%H%M%SZ", pUtcTime) > 0)
		{
			szTimestamp = szBuffer;
		}
		else
		{
			szTimestamp = "unknown_time";
		}
	}
	return szTimestamp;
}

static CvString getSASBBAILogName()
{
	// <!-- custom: This function is only reached after BBAI logging is enabled. If enabled, each Civ4 launch/session writes to a new UTC-timestamped file such as BBAI_20260608T065231Z.log instead of repeatedly appending to BBAI.log. This avoids manually clearing BBAI.log before restarting Civ4, prevents one massive mixed log from accumulating across many test runs, and makes the relevant log easier to identify or upload for review. (ChatGPT-5.5) -->
	static const bool bUseTimestampedFilename = (GC.getDefineINT("SAS_BBAI_LOG_USE_TIMESTAMPED_FILENAME") > 0);
	CvString szLogName;
	// <advc.007>
	if (GC.getGame().isNetworkMultiPlayer())
	{
		// For OOS debugging on one PC
		if (bUseTimestampedFilename)
		{
			szLogName.Format("BBAI%d_%s.log", (int)GC.getGame().getActivePlayer(), getSASBBAILogSessionTimestamp().GetCString());
		}
		else
		{
			szLogName.Format("BBAI%d.log", (int)GC.getGame().getActivePlayer());
		}
	}
	else
	{
		if (bUseTimestampedFilename)
		{
			szLogName.Format("BBAI_%s.log", getSASBBAILogSessionTimestamp().GetCString());
		}
		else
		{
			szLogName = "BBAI.log";
		}
	} // </advc.007>
	return szLogName;
}

void logBBAI(TCHAR* format, ... )
{
	static const bool bEnabled = isSASBBAILogEnabled();
	if (!bEnabled)
		return;

	static char buf[2048];
	va_list args;
	va_start(args, format);
	_vsnprintf(buf, 2048-4, format, args);
	va_end(args); // kmodx
	CvString szLogName = getSASBBAILogName();
	gDLL->logMsg(szLogName.GetCString(), buf, /* advc.007: No time stamps */ false, false);
}

// advc.133:
void logBBAICancel(CvDeal const& d, PlayerTypes eCancelPlayer, wchar const* szReason)
{
	if (gDealCancelLogLevel <= 0)
		return;

	CvWStringBuffer szTmpBuffer;
	GAMETEXT.getDealString(szTmpBuffer, d, eCancelPlayer, false);
	CvWString szBuffer;
	szBuffer.Format(L"    %s cancels deal (%s): %s", GET_PLAYER(eCancelPlayer).getName(0),
			szReason, szTmpBuffer.getCString());
	// Leave it to logBBAI to narrow the string
	logBBAI("%S", szBuffer.GetCString());
}

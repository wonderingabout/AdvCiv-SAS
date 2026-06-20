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
int getSASBBAIUnitLogLevel();
int getSASBBAIWorkerLogLevel();
int getSASBBAIWorkerSeaLogLevel();
int getSASBBAIMapLogLevel();
int getSASBBAIFoundLogLevel();
int getSASBBAIDealCancelLogLevel();
int getSASBBAIScoreLogInterval();

#define gLogBBAI isSASBBAILogEnabled() // advc.007: So that BBAI logging can be checked in FAssert
#define gPlayerLogLevel getSASBBAIPlayerLogLevel()
#define gScoreLogInterval getSASBBAIScoreLogInterval() // advc.007: was hardcoded to 25 in CvPlayer::onTurnLogging
#define gTeamLogLevel getSASBBAITeamLogLevel()
#define gCityLogLevel getSASBBAICityLogLevel()
#define gUnitLogLevel getSASBBAIUnitLogLevel()
#define gWorkerLogLevel getSASBBAIWorkerLogLevel() // <!-- custom: New Land-worker BBAI log level for Worker AI. (ChatGPT-5.5 + GPT-5.5 review) -->
#define gWorkerSeaLogLevel getSASBBAIWorkerSeaLogLevel() // <!-- custom: New Worker-sea/Work Boat BBAI log level for WORKER_SEA AI. (ChatGPT-5.5 + GPT-5.5 review) -->
#define gMapLogLevel getSASBBAIMapLogLevel() // K-Mod
#define gFoundLogLevel getSASBBAIFoundLogLevel() // advc.031c
#define gDealCancelLogLevel getSASBBAIDealCancelLogLevel() // advc.133

void logBBAI(TCHAR* format, ... );
// <advc.133>
class CvDeal;
void logBBAICancel(CvDeal const& d, PlayerTypes eCancelPlayer, wchar const* szReason);
// </advc.133>

#endif  //BBAI_LOG_H

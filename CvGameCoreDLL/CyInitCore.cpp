// AdvCiv-SAS - CuCuGS
#include "CvGameCoreDLL.h"
#include "CyInitCore.h"
#include "CvInitCore.h"


CyInitCore::CyInitCore() : m_kInitCore(GC.getInitCore()) {}

int CyInitCore::getGameSpeed()
{
	return m_kInitCore.getGameSpeed();
}

void CyInitCore::setGameSpeed(int iGameSpeed)
{
	if (iGameSpeed < 0 || iGameSpeed >= GC.getNumGameSpeedInfos())
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	m_kInitCore.setGameSpeed((GameSpeedTypes)iGameSpeed);
}

int CyInitCore::getClimate()
{
	return m_kInitCore.getClimate();
}

void CyInitCore::setClimate(int iClimate)
{
	if (iClimate < 0 || iClimate >= GC.getNumClimateInfos())
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	m_kInitCore.setClimate((ClimateTypes)iClimate);
}

int CyInitCore::getSeaLevel()
{
	return m_kInitCore.getSeaLevel();
}

void CyInitCore::setSeaLevel(int iSeaLevel)
{
	if (iSeaLevel < 0 || iSeaLevel >= GC.getNumSeaLevelInfos())
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	m_kInitCore.setSeaLevel((SeaLevelTypes)iSeaLevel);
}

int CyInitCore::getEra()
{
	return m_kInitCore.getEra();
}

void CyInitCore::setEra(int iEra)
{
	if (iEra < 0 || iEra >= GC.getNumEraInfos())
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	m_kInitCore.setEra((EraTypes)iEra);
}

int CyInitCore::getWorldSize()
{
	return m_kInitCore.getWorldSize();
}

void CyInitCore::setWorldSize(int iWorldSize)
{
	if (iWorldSize < 0 || iWorldSize >= GC.getNumWorldInfos())
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	m_kInitCore.setWorldSize((WorldSizeTypes)iWorldSize);
}

std::wstring CyInitCore::getMapScriptName()
{
	return m_kInitCore.getMapScriptName();
}

void CyInitCore::setMapScriptName(std::wstring szMapScriptName)
{
	m_kInitCore.setMapScriptName(szMapScriptName);
}

int CyInitCore::getNumCustomMapOptions()
{
	return m_kInitCore.getNumCustomMapOptions();
}

int CyInitCore::getCustomMapOption(int iOptionID)
{
	if (iOptionID < 0 || iOptionID >= m_kInitCore.getNumCustomMapOptions())
	{
		FAssertMsg(false, "index out of bounds");
		return 0;
	}
	return m_kInitCore.getCustomMapOption(iOptionID);
}

void CyInitCore::setCustomMapOption(int iOptionID, int iOptionValue)
{
	if (iOptionID < 0 || iOptionID >= m_kInitCore.getNumCustomMapOptions())
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	m_kInitCore.setCustomMapOption(iOptionID, (CustomMapOptionTypes)iOptionValue);
}

int CyInitCore::getHandicap(int ePlayerID)
{
	if (ePlayerID < 0 || ePlayerID >= MAX_CIV_PLAYERS)
	{
		FAssertMsg(false, "index out of bounds");
		return 0;
	}
	return m_kInitCore.getHandicap((PlayerTypes)ePlayerID);
}

void CyInitCore::setHandicap(int ePlayerID, int eHandicap)
{
	if (ePlayerID < 0 || ePlayerID >= MAX_CIV_PLAYERS)
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	if (eHandicap < 0 || eHandicap >= GC.getNumHandicapInfos())
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	m_kInitCore.setHandicap((PlayerTypes)ePlayerID, (HandicapTypes)eHandicap);
}

void CyInitCore::setAIHandicap(int eHandicap)
{
	if (eHandicap < 0 || eHandicap >= GC.getNumHandicapInfos())
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	// Set difficulty for all AI players (only slots with SS_COMPUTER status)
	for (int i = 0; i < MAX_CIV_PLAYERS; i++)
	{
		SlotStatus eStatus = m_kInitCore.getSlotStatus((PlayerTypes)i);
		if (eStatus == SS_COMPUTER)
		{
			m_kInitCore.setHandicap((PlayerTypes)i, (HandicapTypes)eHandicap);
		}
	}
}

int CyInitCore::getCiv(int ePlayerID)
{
	if (ePlayerID < 0 || ePlayerID >= MAX_CIV_PLAYERS)
	{
		FAssertMsg(false, "index out of bounds");
		return NO_CIVILIZATION;
	}
	return m_kInitCore.getCiv((PlayerTypes)ePlayerID);
}

void CyInitCore::setCiv(int ePlayerID, int eCiv)
{
	if (ePlayerID < 0 || ePlayerID >= MAX_CIV_PLAYERS)
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	if (eCiv < 0 || eCiv >= GC.getNumCivilizationInfos())
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	m_kInitCore.setCiv((PlayerTypes)ePlayerID, (CivilizationTypes)eCiv);
}

int CyInitCore::getLeader(int ePlayerID)
{
	if (ePlayerID < 0 || ePlayerID >= MAX_CIV_PLAYERS)
	{
		FAssertMsg(false, "index out of bounds");
		return NO_LEADER;
	}
	return m_kInitCore.getLeader((PlayerTypes)ePlayerID);
}

void CyInitCore::setLeader(int ePlayerID, int eLeader)
{
	if (ePlayerID < 0 || ePlayerID >= MAX_CIV_PLAYERS)
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	if (eLeader < 0 || eLeader >= GC.getNumLeaderHeadInfos())
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	m_kInitCore.setLeader((PlayerTypes)ePlayerID, (LeaderHeadTypes)eLeader);
}

bool CyInitCore::getVictory(int eVictory)
{
	if (eVictory < 0 || eVictory >= GC.getNumVictoryInfos())
	{
		FAssertMsg(false, "index out of bounds");
		return false;
	}
	return m_kInitCore.getVictory((VictoryTypes)eVictory);
}

void CyInitCore::setVictory(int eVictory, bool bVictory)
{
	if (eVictory < 0 || eVictory >= GC.getNumVictoryInfos())
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	m_kInitCore.setVictory((VictoryTypes)eVictory, bVictory);
}

// AdvCiv-SAS - CuCuGS - Game options wrapper functions
bool CyInitCore::getGameOption(int eGameOption)
{
	if (eGameOption < 0 || eGameOption >= NUM_GAMEOPTION_TYPES)
	{
		FAssertMsg(false, "index out of bounds");
		return false;
	}
	return m_kInitCore.getOption((GameOptionTypes)eGameOption);
}

void CyInitCore::setGameOption(int eGameOption, bool bOption)
{
	if (eGameOption < 0 || eGameOption >= NUM_GAMEOPTION_TYPES)
	{
		FAssertMsg(false, "index out of bounds");
		return;
	}
	m_kInitCore.setOption((GameOptionTypes)eGameOption, bOption);
}

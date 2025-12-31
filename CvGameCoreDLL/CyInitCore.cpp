// ccgs
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

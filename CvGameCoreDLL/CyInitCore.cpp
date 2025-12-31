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

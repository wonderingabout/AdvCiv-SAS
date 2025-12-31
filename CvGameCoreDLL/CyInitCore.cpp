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

#pragma once

#ifndef CY_INIT_CORE_H
#define CY_INIT_CORE_H

// ccgs: Adapter class for exposing CvInitCore functions to Python

class CyInitCore
{
public:
	CyInitCore();

	int getGameSpeed();
	void setGameSpeed(int iGameSpeed);

private:
	CvInitCore& m_kInitCore;
};

#endif

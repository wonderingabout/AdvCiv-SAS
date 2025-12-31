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

	int getClimate();
	void setClimate(int iClimate);

	int getSeaLevel();
	void setSeaLevel(int iSeaLevel);

	int getEra();
	void setEra(int iEra);

	int getWorldSize();
	void setWorldSize(int iWorldSize);

private:
	CvInitCore& m_kInitCore;
};

#endif

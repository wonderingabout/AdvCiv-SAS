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

	std::wstring getMapScriptName();
	void setMapScriptName(std::wstring szMapScriptName);

	int getNumCustomMapOptions();
	int getCustomMapOption(int iOptionID);
	void setCustomMapOption(int iOptionID, int iOptionValue);

	int getHandicap(int ePlayerID);
	void setHandicap(int ePlayerID, int eHandicap);
	void setAIHandicap(int eHandicap);

	int getCiv(int ePlayerID);
	void setCiv(int ePlayerID, int eCiv);
	int getLeader(int ePlayerID);
	void setLeader(int ePlayerID, int eLeader);

private:
	CvInitCore& m_kInitCore;
};

#endif

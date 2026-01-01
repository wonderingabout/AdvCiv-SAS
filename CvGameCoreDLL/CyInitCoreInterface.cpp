#include "CvGameCoreDLL.h"
#include "CyInitCore.h"

void CyInitCoreInterface()
{
	python::class_<CyInitCore>("CyInitCore")
		.def("getGameSpeed", &CyInitCore::getGameSpeed, "int ()")
		.def("setGameSpeed", &CyInitCore::setGameSpeed, "void (int iGameSpeed)")
		.def("getClimate", &CyInitCore::getClimate, "int ()")
		.def("setClimate", &CyInitCore::setClimate, "void (int iClimate)")
		.def("getSeaLevel", &CyInitCore::getSeaLevel, "int ()")
		.def("setSeaLevel", &CyInitCore::setSeaLevel, "void (int iSeaLevel)")
		.def("getEra", &CyInitCore::getEra, "int ()")
		.def("setEra", &CyInitCore::setEra, "void (int iEra)")
		.def("getWorldSize", &CyInitCore::getWorldSize, "int ()")
		.def("setWorldSize", &CyInitCore::setWorldSize, "void (int iWorldSize)")
		.def("getMapScriptName", &CyInitCore::getMapScriptName, "wstring ()")
		.def("setMapScriptName", &CyInitCore::setMapScriptName, "void (wstring szMapScriptName)")
		.def("getNumCustomMapOptions", &CyInitCore::getNumCustomMapOptions, "int ()")
		.def("getCustomMapOption", &CyInitCore::getCustomMapOption, "int (int iOptionID)")
		.def("setCustomMapOption", &CyInitCore::setCustomMapOption, "void (int iOptionID, int iOptionValue)")
		.def("getHandicap", &CyInitCore::getHandicap, "int (int ePlayerID)")
		.def("setHandicap", &CyInitCore::setHandicap, "void (int ePlayerID, int eHandicap)")
		.def("setAIHandicap", &CyInitCore::setAIHandicap, "void (int eHandicap)")
		.def("getCiv", &CyInitCore::getCiv, "int (int ePlayerID)")
		.def("setCiv", &CyInitCore::setCiv, "void (int ePlayerID, int eCiv)")
		.def("getLeader", &CyInitCore::getLeader, "int (int ePlayerID)")
		.def("setLeader", &CyInitCore::setLeader, "void (int ePlayerID, int eLeader)")
		.def("getVictory", &CyInitCore::getVictory, "bool (int eVictory)")
		.def("setVictory", &CyInitCore::setVictory, "void (int eVictory, bool bVictory)")
	;
}

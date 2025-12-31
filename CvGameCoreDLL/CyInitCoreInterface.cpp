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
	;
}

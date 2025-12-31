#include "CvGameCoreDLL.h"
#include "CyInitCore.h"

void CyInitCoreInterface()
{
	python::class_<CyInitCore>("CyInitCore")
		.def("getGameSpeed", &CyInitCore::getGameSpeed, "int ()")
		.def("setGameSpeed", &CyInitCore::setGameSpeed, "void (int iGameSpeed)")
	;
}

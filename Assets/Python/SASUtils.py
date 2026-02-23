# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)

from CvPythonExtensions import *


gc = CyGlobalContext()


# <!-- custom: shared strict XML lookup helper for maps/screens; raise loudly instead of silently accepting missing tags. (GPT-5.3-Codex) -->
# <!-- custom: handle for example PROMOTION_GUERILLA1 now being renamed to PROMOTION_HILLS_MASTER1, so summoning wrong asset for example as is done in sevopedia bonus's placeRelevantUnits panel as of now should raise an error not silently pass; also useful to access any asset id safely such as hills or peak terrains 's id, or hills's button for example too; is also useful to detect and signal loudly errors such as using wrong "TERRAIN_FOREST" as part of copy pasting terrain code into features code of the placeUnits method there as of now instead of "FEATURE_FOREST", and we get a nice error instead of what i assume would be a silent pass; done with the help of chatgpt thanks -->
def getInfoTypeOrFail(tag):
	iType = gc.getInfoTypeForString(tag)
	if iType == -1:
		raise ValueError("Missing XML tag: '%s'" % tag)
	return iType



# <!-- custom: shared helper to resolve NewConcept IDs by XML type (e.g. "CONCEPT_SAS_SCORE_TAB_COLUMNS" for the Score-tab Legend clickable Sevopedia/NewConcept entry). Returns -1 when missing so callers can skip optional links safely. (GPT-5.3-Codex) -->
def getNewConceptID(szConceptType):
	for i in range(gc.getNumNewConceptInfos()):
		if gc.getNewConceptInfo(i).getType() == szConceptType:
			return i
	return -1

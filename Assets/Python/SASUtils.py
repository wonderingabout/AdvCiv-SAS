# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)


from CvPythonExtensions import *


gc = CyGlobalContext()



# <!-- custom: shared advisor layout constants that are screen-independent (safe to read in __init__); runtime screen-dependent geometry is derived per screen from current resolution in interfaceScreen. (GPT-5.3-Codex) -->
# <!-- custom: as part of upscaling text code changes, now that commerce sliders are on the right-side, reduce left-space (from 172). Increase right-space for scoreboard (from 390) to give more room for anarchy and golden age button and just in case here. Increase top space (from 28). -->
SAS_ADVISOR_LEFT_SPACE_FOR_COMMERCE_SLIDERS = 0
SAS_ADVISOR_RIGHT_SPACE_FOR_SCOREBOARD = 420
SAS_ADVISOR_TOP_SPACE_FOR_TECH_BAR = 32
SAS_ADVISOR_BOTTOM_SPACE = 0

# <!-- custom: shared offsets/divisors for runtime screen-dependent anchor formulas (title/exit/link/footer) derived from each advisor's current panel width/height in interfaceScreen. (GPT-5.3-Codex) -->
SAS_ADVISOR_TITLE_X_DIVISOR = 2
SAS_ADVISOR_EXIT_X_OFFSET = 30
SAS_ADVISOR_EXIT_Y_OFFSET = 42
SAS_ADVISOR_BOTTOM_PANEL_Y_OFFSET = 55



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

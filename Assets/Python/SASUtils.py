# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)


from CvPythonExtensions import *
import CvUtil
from SASFontUtils import sasFontTagLabel, SAS_FONT_TAG_CLOSE


gc = CyGlobalContext()


# <!-- custom: lazy-init cache for SAS_SHOW_LEGEND_LINK GlobalDefine. Cannot be resolved at module import time because SASUtils is imported before CyGlobalContext finishes loading XML defines (eager init returns False and the legend link silently disappears). Resolved on first use via _isLegendLinkEnabled, matching the lazy-init-to-None approach used by other AdvCiv-SAS advisors. (Claude code Opus 4.7) -->
_IS_SAS_SHOW_LEGEND_LINK = None
def _isLegendLinkEnabled():
	global _IS_SAS_SHOW_LEGEND_LINK
	if _IS_SAS_SHOW_LEGEND_LINK is None:
		_IS_SAS_SHOW_LEGEND_LINK = (gc.getDefineINT("SAS_SHOW_LEGEND_LINK") > 0)
	return _IS_SAS_SHOW_LEGEND_LINK



# <!-- custom: shared advisor layout constants that are screen-independent (safe to read in __init__); runtime screen-dependent geometry is derived per screen from current resolution in interfaceScreen. (GPT-5.3-Codex) -->
# <!-- custom: as part of upscaling text code changes, now that commerce sliders are on the right-side, reduce left-space (from 172). Increase right-space for scoreboard (from 390) to give more room for anarchy and golden age button and just in case here. Increase top space (from 28). -->
SAS_ADVISOR_LEFT_SPACE_FOR_COMMERCE_SLIDERS = 0
SAS_ADVISOR_RIGHT_SPACE_FOR_SCOREBOARD = 420
SAS_ADVISOR_TOP_SPACE_FOR_TECH_BAR = 32
SAS_ADVISOR_BOTTOM_SPACE = 0

# <!-- custom: shared advisor title Y is screen-independent and unified for migrated advisors to reduce per-file noise; older per-screen values were close (e.g. 8/12), so use one midpoint default (10). Keep screen-dependent anchors computed at runtime. (GPT-5.3-Codex) -->
SAS_ADVISOR_TITLE_Y = 10
# <!-- custom: shared offsets/divisors for runtime screen-dependent anchor formulas (title/exit/link/footer) derived from each advisor's current panel width/height in interfaceScreen. (GPT-5.3-Codex) -->
SAS_ADVISOR_TITLE_X_DIVISOR = 2
SAS_ADVISOR_EXIT_X_OFFSET = 30
SAS_ADVISOR_EXIT_Y_OFFSET = 42
SAS_ADVISOR_BOTTOM_PANEL_Y_OFFSET = 55

# <!-- custom: shared runtime advisor bounds (screen-dependent) and shared title/exit/link anchors; callers pass screen and configured margins from __init__. (GPT-5.3-Codex) -->
def getAdvisorRuntimeBounds(screen, iLeftSpace, iRightSpace, iTopSpace, iBottomSpace):
	iXScreen = iLeftSpace
	iWScreen = screen.getXResolution() - iLeftSpace - iRightSpace
	iYScreen = iTopSpace
	iHScreen = screen.getYResolution() - iTopSpace - iBottomSpace
	return (iXScreen, iYScreen, iWScreen, iHScreen)


def getAdvisorRuntimeAnchors(iWScreen, iHScreen):
	iXTitle = iWScreen / SAS_ADVISOR_TITLE_X_DIVISOR
	iXExit = iWScreen - SAS_ADVISOR_EXIT_X_OFFSET
	iYExit = iHScreen - SAS_ADVISOR_EXIT_Y_OFFSET
	iYLink = iYExit
	iYBottomPanel = iHScreen - SAS_ADVISOR_BOTTOM_PANEL_Y_OFFSET
	return (iXTitle, iXExit, iYExit, iYLink, iYBottomPanel)


# <!-- custom: shared weighted tab-link width helper used by advisor tab bars; weights by text width and scales to runtime X_EXIT. (GPT-5.3-Codex) -->
def getAdvisorRuntimeLinkWidths(cyInterface, aszLabels, szExitLabel, iXExit):
	aiLabelWidths = []
	for szLabel in aszLabels:
		aiLabelWidths.append(cyInterface.determineWidth(szLabel) + 20)
	iTotalWidth = sum(aiLabelWidths) + cyInterface.determineWidth(szExitLabel) + 20
	aiLinkWidths = []
	for iWidth in aiLabelWidths:
		aiLinkWidths.append((iXExit * iWidth + iTotalWidth/2) / iTotalWidth)
	return aiLinkWidths


# <!-- custom: shared debug-player dropdown for advisors; callers keep control of barbarian inclusion (MAX_PLAYERS vs MAX_CIV_PLAYERS) and active-row preselection because legacy advisors differ in both details. (GPT-5.5) -->
def addAdvisorDebugDropdown(screen, szDropdownName, iActivePlayer, bIncludeBarbarians=False, bSelectActive=True, iX=22, iY=12, iW=300, eFont=FontTypes.GAME_FONT):
	if not CyGame().isDebugMode():
		return False
	screen.addDropDownBoxGFC(szDropdownName, iX, iY, iW, WidgetTypes.WIDGET_GENERAL, -1, -1, eFont)
	iMaxPlayers = gc.getMAX_CIV_PLAYERS()
	if bIncludeBarbarians:
		iMaxPlayers = gc.getMAX_PLAYERS()
	for iPlayer in range(iMaxPlayers):
		if gc.getPlayer(iPlayer).isAlive():
			screen.addPullDownString(szDropdownName, gc.getPlayer(iPlayer).getName(), iPlayer, iPlayer, bSelectActive and iPlayer == iActivePlayer)
	return True


def getAdvisorDebugDropdownSelectedPlayer(screen, szDropdownName):
	iIndex = screen.getSelectedPullDownID(szDropdownName)
	return screen.getPullDownData(szDropdownName, iIndex)



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


# <!-- custom: shared advisor "Legend" link helper, factored from CvInfoScreen's Score-tab pattern so any AdvCiv-SAS advisor can drop a Sevopedia legend link with one call. Caller passes the screen object (must expose getScreen, getNextWidgetName, Z_CONTROLS), the NewConcept XML type, and the (X,Y) anchor in screen coords. Skips silently when the SAS_SHOW_LEGEND_LINK GlobalDefine is off or the concept is missing. setText params mirror the Score-tab call exactly: WIDGET_PEDIA_DESCRIPTION + CIVILOPEDIA_PAGE_CONCEPT_NEW + concept ID is the pedia jump that actually resolves through SevoPediaMain.pediaJump. (Claude code Opus 4.7) -->
def placeAdvisorLegendLink(top, szConceptType, iX, iY, eJustify=None):
	if not _isLegendLinkEnabled():
		return
	iConcept = getNewConceptID(szConceptType)
	if iConcept < 0:
		return
	if eJustify is None:
		eJustify = CvUtil.FONT_RIGHT_JUSTIFY
	screen = top.getScreen()
	szLabel = sasFontTagLabel + "Legend" + SAS_FONT_TAG_CLOSE
	screen.setText(top.getNextWidgetName(), "Background", szLabel, eJustify, iX, iY, top.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_DESCRIPTION, CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW, iConcept)

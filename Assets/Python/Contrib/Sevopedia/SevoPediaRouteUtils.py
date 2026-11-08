# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Route lookups shared by Sevopedia and the Tech Advisor.
# This module is separate from SevoPediaRoute because the Tech Advisor loads when the game starts: importing SevoPediaRoute there also loaded _sevopedia_helpers, which reads GlobalDefines such as SAS_SHOW_LEGEND_LINK once at import, before they are loaded, and the Legend link disappeared from Sevopedia pages.
# Keep this module free of define or text reads at import. (Claude code Opus 5.5) -->

from CvPythonExtensions import *
import SASVisualUtils as SASVisuals

gc = CyGlobalContext()


# <!-- custom: The Tech Advisor and Sevopedia Tech movement icon carries only a tech; it opens the first route the tech speeds up. (Claude code Opus 5.5) -->
def getTechMovementRoute(iTech):
	for iRoute in xrange(gc.getNumRouteInfos()):
		if gc.getRouteInfo(iRoute).getTechMovementChange(iTech) != 0:
			return iRoute
	return -1


def getRouteYieldImprovements(iRoute):
	improvements = []
	for iImprovement in xrange(gc.getNumImprovementInfos()):
		improvement = gc.getImprovementInfo(iImprovement)
		for iYield in xrange(YieldTypes.NUM_YIELD_TYPES):
			if improvement.getRouteYieldChanges(iRoute, iYield) != 0:
				improvements.append(iImprovement)
				break
	return improvements


def getYieldText(changes):
	parts = []
	for iYield, iChange in enumerate(changes):
		if iChange != 0:
			parts.append(u"%+d%s" % (iChange, SASVisuals.Yield.char(iYield)))
	return u" ".join(parts)

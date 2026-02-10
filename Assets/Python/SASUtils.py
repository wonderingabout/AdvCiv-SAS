# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)

from CvPythonExtensions import *


gc = CyGlobalContext()


# <!-- custom: shared strict XML lookup helper for maps/screens; raise loudly instead of silently accepting missing tags. (GPT-5.3-Codex) -->
def getInfoTypeOrFail(tag):
	iType = gc.getInfoTypeForString(tag)
	if iType == -1:
		raise ValueError("Missing XML tag: '%s'" % tag)
	return iType

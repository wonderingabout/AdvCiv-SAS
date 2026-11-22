## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Copied unchanged from vanilla Civ4's C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Assets\Python\EntryPoints\CvDiplomacyInterface.py (only vanilla Civ4 ships it), the copy SAS ran before, so the file SAS uses is in its repository; only these header lines were added (2026-11-22). See KI#1104. (Claude code Opus 5.5) -->
from CvPythonExtensions import *
import CvUtil
import CvDiplomacy

gc = CyGlobalContext()

def beginDiplomacy (argsList):
	"""
	This is what gets called when you first begin diplomacy
	The first parameter argsList[0] is the 'comment type', or how they feel about you
	"""
	eComment = argsList[0]
	commentArgsSize = argsList[1]
	if (commentArgsSize):
		commentArgs = argsList[2:]
		CvUtil.pyAssert(len(commentArgs)==commentArgsSize, "comment args tuple size mismatch")
		print "tuple size", len(commentArgs), ", commentArgsSize ", commentArgsSize
	else:
		commentArgs=[]
	diploClass = CvDiplomacy.CvDiplomacy()
	diploClass.setAIComment(eComment, *commentArgs)	#unpack args tuple


def handleUserResponse (argsList):
	"First parameter of argsList if the comment they clicked on..."
	diploClass = CvDiplomacy.CvDiplomacy()

	eComment = argsList[0]
	iData1 = argsList[1]
	iData2 = argsList[2]
	diploClass.handleUserResponse(eComment, iData1, iData2)
	
def dealCanceled ():
	diploClass = CvDiplomacy.CvDiplomacy()

	diploClass.dealCanceled()
	
def refresh (argsList):
	diploClass = CvDiplomacy.CvDiplomacy()
	diploClass.determineResponses(argsList[0])

def toggleDebugLogging():
	CvDiplomacy.DebugLogging = not CvDiplomacy.DebugLogging
	
	
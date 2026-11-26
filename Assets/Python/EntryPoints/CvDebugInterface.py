## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Copied from vanilla Civ4's C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Assets\Python\EntryPoints\CvDebugInterface.py (only vanilla Civ4 ships it), the copy SAS ran before (2026-11-26). See KI#1104. (Claude code Opus 5.5) -->
def parseText(argsList):
	szMsg, iValueList = argsList
	# <!-- custom: print x became print(x), the same output in Python 2.4, so CI's Ruff, which parses Python 3, can read this file (KI#21.7). (Claude code Opus 5.5) -->
	print(szMsg)
	print(iValueList)
	return 0
	
def toggleDebugMode():
	import CvDebugTools
	CvDebugTools.toggleDebugMode()

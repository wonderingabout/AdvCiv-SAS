## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Copied from vanilla Civ4's C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Assets\Python\Screens\CvPediaScreen.py (only vanilla Civ4 ships it), the copy SAS ran before (2026-11-22). See KI#1104. (Claude code Opus 5.5) -->
# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
# CvScreen - Base class for all of the Screens

from CvPythonExtensions import *
import CvUtil
import CvScreen

class CvPediaScreen( CvScreen.CvScreen ):
	"Civilopedia Base Screen"
	
	def getSortedList( self, numInfos, getInfo ):
		' returned a list of infos sorted alphabetically '
		
		# count the items we are going to display
		iNumNonGraphical = 0
		for i in range(numInfos):
			if (not getInfo(i).isGraphicalOnly()):
				iNumNonGraphical += 1
				
		infoList = [(0,0)] * iNumNonGraphical
		j = 0
		for i in range( numInfos ):
			if (not getInfo(i).isGraphicalOnly()):
				infoList[j] = (getInfo(i).getDescription(), i)
				j += 1
				
		infoList.sort()
		
		return infoList

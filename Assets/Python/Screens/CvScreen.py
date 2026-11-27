# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Copied from vanilla Civ4's C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Assets\Python\Screens\CvScreen.py (only vanilla Civ4 ships it), the copy SAS ran before (2026-11-22). See KI#1104. (Claude code Opus 5.5) -->
#
# CvScreen - Base class for all of the Screens

from CvPythonExtensions import *
import CvUtil

class CvScreen:
	"Base Screen"
	
	def __init__(self):
		return
	
	def getScreen(self):
		return -1
	
	def hideScreen(self):
		return
	
	# Screen construction function
	def showScreen(self, iCategory):
		return
	
	# returns a unique ID for a widget in this screen
	def getNextWidgetName(self):
		return
	
	# Will handle the input for this screen...
	def handleInput (self, inputClass):
		return 0
	
	def update(self, fDelta):
		return


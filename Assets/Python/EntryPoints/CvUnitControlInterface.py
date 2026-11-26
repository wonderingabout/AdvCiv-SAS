## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Copied from vanilla Civ4's C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Assets\Python\EntryPoints\CvUnitControlInterface.py (only vanilla Civ4 ships it), the copy SAS ran before (2026-11-26). See KI#1104. (Claude code Opus 5.5) -->
from CvPythonExtensions import *
import CvUnitController

#"""
#UNIT CONTROL INTERFACE
#"""

#""" Global Unit controller instance. Instead of creating a new one everytime, just keep a global - saves time."""
pGlobalUnitController = CvUnitController.CvUnitController()

def ProcessEvent ( argsList ): 
	"""Notifies a unit of a occurring event. This function returns true if it processes the given event, or false if
	it does not (in which case the default processor will do something with it). """
	pCyUnitEntity, iEvent = argsList
	return pGlobalUnitController.ProcessEvent( pCyUnitEntity, iEvent )

# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
#
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)



from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
from SASFontUtils import *
import SASTextScale

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



class SevoPediaHistory:

	def __init__(self, main):
		self.top = main

		self.X_HISTORY = self.top.X_PEDIA_PAGE
		self.Y_HISTORY = self.top.Y_PEDIA_PAGE
		self.H_HISTORY = self.top.H_PEDIA_PAGE
		self.W_HISTORY = self.top.W_PEDIA_PAGE



	def interfaceScreen(self, iEntry):
		self.placeHistory(iEntry)



	def placeHistory(self, iEntry):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, "", "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		szText = self.getCivilopedia(iEntry)
		# <!-- custom: some engine-provided text can carry embedded <font=...>; use normalize* helper (strip + reapply) so SAS scaling is consistent. See SASTextScale normalize comments. (GPT-5.3-Codex) -->
		szText = SASTextScale.normalizeLabelText(szText)
		textName = self.top.getNextWidgetName()
		screen.addMultilineText(textName, szText, self.X_HISTORY + 10, self.Y_HISTORY + 10, self.W_HISTORY - 20, self.H_HISTORY - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def getCivilopedia(self, iEntry):
		if (self.top.iCategory == SevoScreenEnums.PEDIA_CONCEPTS):
			info = gc.getConceptInfo(iEntry)
		else:
			info = gc.getNewConceptInfo(iEntry)
		return info.getCivilopedia()



	def handleInput (self, inputClass):
		return 0

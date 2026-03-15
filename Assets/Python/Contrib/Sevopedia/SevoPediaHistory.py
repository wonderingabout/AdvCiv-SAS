# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
#



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

		self.X_TEXT = self.top.X_PEDIA_PAGE
		self.Y_TEXT = self.top.Y_PEDIA_PAGE
		self.H_TEXT = self.top.H_PEDIA_PAGE
		self.W_TEXT = self.top.W_PEDIA_PAGE



	def interfaceScreen(self, iEntry):
		self.placeText(iEntry)



	def placeText(self, iEntry):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, "", "", True, True, self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_BLUE50)
		szText = self.getCivilopedia(iEntry)
		# <!-- custom: some engine-provided text can carry embedded <font=...>; use normalize* helper (strip + reapply) so SAS scaling is consistent. See SASTextScale normalize comments. (GPT-5.3-Codex) -->
		szText = SASTextScale.normalizeBodyText(szText)
		textName = self.top.getNextWidgetName()
		screen.addMultilineText(textName, szText, self.X_TEXT + 10, self.Y_TEXT + 10, self.W_TEXT - 20, self.H_TEXT - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def getCivilopedia(self, iEntry):
		if (self.top.iCategory == SevoScreenEnums.PEDIA_CONCEPTS):
			info = gc.getConceptInfo(iEntry)
		else:
			info = gc.getNewConceptInfo(iEntry)
		return info.getCivilopedia()



	def handleInput (self, inputClass):
		return 0

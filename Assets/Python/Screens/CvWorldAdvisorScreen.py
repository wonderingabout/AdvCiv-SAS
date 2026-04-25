## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)

from CvPythonExtensions import *
from SASFontUtils import *
from CvInfoScreen import CvInfoScreen

localText = CyTranslator()

class CvWorldAdvisorScreen(CvInfoScreen):
	"World Advisor! Contains the Environment tab."

	def __init__(self, screenId):
		CvInfoScreen.__init__(self, screenId)
		# <!-- custom: World Advisor starts with the moved Environment tab and reuses CvInfoScreen's environment drawing code. (GPT-5.5) -->
		self.PAGE_NAME_LIST = [
			"TXT_KEY_ECONOMICS_ADVISOR_ENVIRONMENT_TAB",
			]
		self.PAGE_DRAW_LIST = [
			self.drawEnvironmentTab,
			]
		self.PAGE_LINK_WIDTH = []
		self.iEnvironmentID = 0
		self.iActiveTab = self.iEnvironmentID

	def initText(self):
		CvInfoScreen.initText(self)
		self.SCREEN_TITLE = SAS_FONT_TAG_TITLE_BOLD + localText.getText("TXT_KEY_WORLD_ADVISOR_TITLE", ()).upper() + SAS_FONT_TAG_CLOSE

	def showScreen(self):
		self.iActiveTab = self.iEnvironmentID
		CvInfoScreen.showScreen(self, -1, self.iEnvironmentID, False)

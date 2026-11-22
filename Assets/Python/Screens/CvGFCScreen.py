## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Copied unchanged from vanilla Civ4's C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Assets\Python\Screens\CvGFCScreen.py (only vanilla Civ4 ships it), the copy SAS ran before, so the file SAS uses is in its repository; only these header lines were added (2026-11-22). See KI#1104. (Claude code Opus 5.5) -->
import CvUtil
from CvPythonExtensions import *

# globals
gc = CyGlobalContext()

class CvGFCScreen:
	def __init__(self):
		self.screenName = "None"
		self.screenID = -1
		
	def setScreenValues(self, screenName, screenID):
		self.screenName = screenName
		self.screenID = screenID
	
	def getScreen(self):
		screen = CyGInterfaceScreen(self.screenName, self.screenID)
		return screen
	
	def setCloseButton(widgetname, text, x, y):
		#self.getScreen().setButtonGFC(widgetname, text, "", x, y, 50,50, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)
		return
	
	def addText(self, widgetName,message, iX,iY, iWidth, iHeight):
		screen = self.getScreen()
		screen.addMultilineText( widgetName, unicode(message), 
								iX, iY, iWidth, iHeight, 
								WidgetTypes.WIDGET_GENERAL, -1,-1, CvUtil.FONT_LEFT_JUSTIFY );
	
	def hideScreen(self):
		self.getScreen().hideScreen()
	
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

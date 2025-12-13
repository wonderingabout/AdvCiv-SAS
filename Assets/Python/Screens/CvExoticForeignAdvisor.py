## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005

# Thanks to Requies and Elhoim from CivFanatics for this interface mod

# This file has been edited for K-Mod in various places. Some changes marked, others not.

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import math

############################################
### BEGIN CHANGES ENHANCED INTERFACE MOD ###
############################################
import IconGrid_BUG
#from IconGrid_BUG import IconGrid_BUG
##########################################
### END CHANGES ENHANCED INTERFACE MOD ###
##########################################

import CvForeignAdvisor
import DomPyHelpers
import TechTree
import AttitudeUtil
import BugCore
import BugDll
import BugUtil
import DealUtil
import DiplomacyUtil
import FavoriteCivicDetector
import FontUtil
import TradeUtil

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

PyPlayer = DomPyHelpers.DomPyPlayer
PyCity = DomPyHelpers.DomPyCity

AdvisorOpt = BugCore.game.Advisors

# tech trade columns
(iTechColLeader,
 iTechColStatus,
 iTechColWants,
 iTechColCantYou,
 iTechColResearch,
 iTechColGold,
 iTechColWill,
 iTechColWont,
 iTechColCantThem,
) = range(9)
# <advc.ctr>
(iCityColLeader,
 iCityColStatus,
 iCityColWants,
 iCityColRejects,
 iCityColWillCede,
 iCityColWontCede,
) = range(6) # </advc.ctr>

# Debugging help
def ExoticForPrint (stuff):
	stuff = "ExoForAdv: " + stuff
	BugUtil.debug(stuff)

# this class is shared by both the resource and technology foreign advisors
class CvExoticForeignAdvisor (CvForeignAdvisor.CvForeignAdvisor):
	"Exotic Foreign Advisor Screen"

	def __init__(self):
		CvForeignAdvisor.CvForeignAdvisor.__init__ (self)

		# help (CyPlayer)
		# help (CyGInterfaceScreen)
		self.GLANCE_HEADER = "ForeignAdvisorGlanceHeader"
		self.GLANCE_BUTTON = "ForeignAdvisorPlusMinus"
		self.X_LINK = 0
		self.Y_LINK = 726
		
		# <!-- custom: remove these iExtraWidth and iExtraHeight-like as we don't want yellow margins: they are distracting and not not useful; channge with the help of gemini pro 3 thanks anyways etc.  -->
		# self.X_GLANCE_OFFSET = 6 # advc.004: was 10
		# self.Y_GLANCE_OFFSET = 3
		self.X_GLANCE_OFFSET = 0
		self.Y_GLANCE_OFFSET = 0
		self.GLANCE_BUTTON_SIZE = 46
		self.PLUS_MINUS_SIZE = 25
		self.bGlancePlus = True

		self.INFO_BORDER = 10

		############################################
		### BEGIN CHANGES ENHANCED INTERFACE MOD ###
		############################################

		###################
		# General options #
		###################
		
		# Show the names of the leaders if 'True'
		self.SHOW_LEADER_NAMES = False
		
		# Show a border around the rows
		self.SHOW_ROW_BORDERS = True
		
		# Minimum space at the top and bottom of the screen.
		# <!-- custom: after our changes, blue panel is overfilling on top and bottom, adjusted with the help of gemini 3 pro thanks anyways etc. -->
		# The blue panel is overflowing because MIN_TOP_BOTTOM_SPACE is set to 30, but the Civ4 top/bottom UI bars are 55 pixels tall. We need to increase the margin so the panel clears those bars.
		# <!-- custom: update: with 55 we have some yellow uneeded margins a slightly lower value seems to work much better at removing these, but a too low one creates an unwanted display somehow, adjusted as such based on a similar suggestion of gemini 3 pro thanks but anyways etc. -->
		# self.MIN_TOP_BOTTOM_SPACE = 30 # advc.073: was 60
		self.MIN_TOP_BOTTOM_SPACE = 45
		
		# Minimum space at the left and right end of the screen.
		# <!-- custom: reduce this as we don't need so much space on the sides, and we need the space to show more info anyways etc as per gemini 3 pro's solution thanks but anyways etc. -->
		# self.MIN_LEFT_RIGHT_SPACE = 25
		self.MIN_LEFT_RIGHT_SPACE = 0
		
		# Extra border at the left and right ends of the column groups (import/export)
		self.GROUP_BORDER = 8
		
		# Extra space before the label of the column groups (import/export)
		self.GROUP_LABEL_OFFSET = "   "
		
		# Minimum space between the columns
		self.MIN_COLUMN_SPACE = 5
		
		# Minimum space between the rows
		self.MIN_ROW_SPACE = 1
		
		##########################
		# Resources view options #
		##########################
		
		# If 'True', the amount for each surplus resource is subtracted by one. So it shows how many you
		# can give away without losing the resource yourself. This value isn't affected by any default 
		# layout.
		self.RES_SHOW_EXTRA_AMOUNT = False # advc.073: was True
		
		# If 'True', the amount's are shown as an overlay on top of the lower left corner of the resources.
		# If 'False', the amount's are shown below the resources so you'll need to use a higher value for 
		# self.RES_SURPLUS_HEIGHT (see below).
		# advc.073 (comment): I doubt that False will work correctly with the changes I've made
		self.RES_SHOW_SURPLUS_AMOUNT_ON_TOP = True
		
		# If 'True', the resource columns are grouped as import and export.
		self.RES_SHOW_IMPORT_EXPORT_HEADER = True
		
		# If 'True', two extra columns are used to display resources that are traded in active deals.
		self.RES_SHOW_ACTIVE_TRADE = True
		
		# Height of the panel showing the surplus resources. If self.RES_SHOW_SURPLUS_AMOUNT_ON_TOP is 'False'
		# you'll need to set a higher value for this variable (110 is recommended).
		# <!-- custom: it seems to me just one row of bonuses is enough, to begin with we don't have that much in our mod and not so much are tradeable at the same time anyway (plus we removed the header as well so we don't need as much space anyways etc.), so reduce this anyways etc. -->
		# self.RES_SURPLUS_HEIGHT = 110 # advc.073: was 80
		self.RES_SURPLUS_HEIGHT = 60
		
		self.RES_GOLD_COL_WIDTH = 25
		
		# Space between the two panels.
		self.RES_PANEL_SPACE = 0
		
		#############################
		# Technologies view options #
		#############################
		
		# If 'True', use icon size 32x32
		# If 'False', use icon size 64x64
		self.TECH_USE_SMALL_ICONS = True
		
		self.TECH_STATUS_COL_WIDTH = 40
		self.TECH_GOLD_COL_WIDTH = 60
		
		###############
		# End options #
		###############
		
		self.TITLE_HEIGHT = 24
		self.TABLE_CONTROL_HEIGHT = 24
		self.RESOURCE_ICON_SIZE = 34
		self.SCROLL_TABLE_UP = 1
		self.SCROLL_TABLE_DOWN = 2

		##########################################
		### END CHANGES ENHANCED INTERFACE MOD ###
		##########################################

		self.SCREEN_DICT = {
			"BONUS": 0,
			"TECH": 1,
			"RELATIONS": 2,
			"ACTIVE_TRADE": 3,
			"INFO": 4,
			"GLANCE": 5,
			"CITIES": 6, # advc.ctr
			}

		self.REV_SCREEN_DICT = {}

		for key, value in self.SCREEN_DICT.items():
			self.REV_SCREEN_DICT[value] = key

		self.DRAW_DICT = {
			"BONUS": self.drawResourceDeals,
			"TECH": self.drawTechDeals,
			"RELATIONS": self.drawRelations,
			"ACTIVE_TRADE": self.drawActive,
			"INFO": self.drawInfo,
			"GLANCE": self.drawGlance,
			"CITIES": self.drawCityDeals, # advc.ctr
			}

		self.TXT_KEY_DICT = {
			"BONUS": "TXT_KEY_FOREIGN_ADVISOR_RESOURCES",
			"TECH": "TXT_KEY_FOREIGN_ADVISOR_TECHS",
			"RELATIONS": "TXT_KEY_FOREIGN_ADVISOR_RELATIONS",
			"ACTIVE_TRADE": "TXT_KEY_FOREIGN_ADVISOR_ACTIVE",
			"INFO": "TXT_KEY_FOREIGN_ADVISOR_INFO",
			"GLANCE": "TXT_KEY_FOREIGN_ADVISOR_GLANCE",
			"CITIES": "TXT_KEY_CONCEPT_CITIES", # advc.ctr
			}

		self.ORDER_LIST = ["RELATIONS", "GLANCE", "ACTIVE_TRADE", "BONUS", "INFO", "TECH", "CITIES"] # advc.ctr (add CITIES)

		# K-Mod
		self.LABEL_WIDTH_LIST = []
		self.iLanguageLoaded = -1
		# K-Mod end

		self.iDefaultScreen = self.SCREEN_DICT["RELATIONS"]
						
	def interfaceScreen (self, iScreen):

		# self.ATTITUDE_DICT = {
		# 	"COLOR_YELLOW": re.sub (":", "|", localText.getText ("TXT_KEY_ATTITUDE_FRIENDLY", ())),
		# 	"COLOR_GREEN" : re.sub (":", "|", localText.getText ("TXT_KEY_ATTITUDE_PLEASED", ())),
		# 	"COLOR_CYAN" : re.sub (":", "|", localText.getText ("TXT_KEY_ATTITUDE_ANNOYED", ())),
		# 	"COLOR_RED" : re.sub (":", "|", localText.getText ("TXT_KEY_ATTITUDE_FURIOUS", ())),
		# }

		self.WAR_ICON = smallSymbol(FontSymbols.WAR_CHAR)
		self.PEACE_ICON = smallSymbol(FontSymbols.PEACE_CHAR)
		# <!-- custom: add "Willing to become a vassal" type of button as it is useful for the human player to see it in UI in the glances tab anyways etc. Added with the help of claude sonnet 4.5 and gemini 3 pro thanks; check if accurate anyways etc. -->
		self.WILLING_VASSAL_ICON = smallSymbol(FontSymbols.SILVER_STAR_CHAR) # using a crown/strength symbol for vassalization
		self.VASSAL_ICON = smallSymbol(FontSymbols.STRENGTH_CHAR)  # or use a different symbol

		self.objTechTree = TechTree.TechTree()

		if (iScreen < 0):
			if (self.iScreen < 0):
				iScreen = self.iDefaultScreen
			else:
				iScreen = self.iScreen
		
		self.EXIT_TEXT = u"<font=4>" + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + u"</font>"
		self.SCREEN_TITLE = u"<font=4b>" + localText.getText("TXT_KEY_FOREIGN_ADVISOR_TITLE", ()).upper() + u"</font>"

		if (self.iScreen != iScreen):	
			self.killScreen()
			self.iScreen = iScreen
		
		screen = self.getScreen()
		if screen.isActive():
			return
		screen.setRenderInterfaceOnly(True)
		screen.showScreen( PopupStates.POPUPSTATE_IMMEDIATE, False)
	
		self.iActiveLeader = CyGame().getActivePlayer()
		self.iSelectedLeader = self.iActiveLeader
		self.listSelectedLeaders = []
		#self.listSelectedLeaders.append(self.iSelectedLeader)

		############################################
		### BEGIN CHANGES ENHANCED INTERFACE MOD ###
		############################################
		#self.W_SCREEN = screen.getXResolution()
		#self.H_SCREEN = screen.getYResolution()

		# RJG Start - following line added as per RJG (http://forums.civfanatics.com/showpost.php?p=6996936&postcount=15)
		# FROM BUG MA Widescreen START
		# over-ride screen width, height
		
		##
		# K-Mod, 7/dec/12, karadoc
		#returned the window to the standard size
		##
		#self.W_SCREEN = screen.getXResolution() - 40
		#self.X_SCREEN = (screen.getXResolution() - 24) / 2
		#self.L_SCREEN = 20

		#if self.W_SCREEN < 1024:
			#self.W_SCREEN = 1024
			#self.L_SCREEN = 0
		
		self.X_EXIT = self.W_SCREEN - 30
		# FROM BUG MA Widescreen END
		
		#self.X_EXIT = self.W_SCREEN - 10
		# RJG End
		#self.DX_LINK = (self.X_EXIT - self.X_LINK) / (len (self.SCREEN_DICT) + 1) # disabled by K-Mod

		self.Y_EXIT = self.H_SCREEN - 42
		self.Y_LINK = self.H_SCREEN - 42
		self.Y_BOTTOM_PANEL = self.H_SCREEN - 55
		
		# Set the background and exit button, and show the screen
		screen.setDimensions(0, 0, self.W_SCREEN, self.H_SCREEN)
		screen.addDrawControl(self.BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addPanel( "TopPanel", u"", u"", True, False, 0, 0, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_TOPBAR )
		screen.addPanel( "BottomPanel", u"", u"", True, False, 0, self.Y_BOTTOM_PANEL, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR )
		##########################################
		### END CHANGES ENHANCED INTERFACE MOD ###
		##########################################

		# Set the background and exit button, and show the screen
		# <!-- custom: in the foreign advisor and similar screens, we can't see all info in one screen when there are too many players, yet the window does not use all the game window space. Make it larger, similarly to what we did for sevopedia anyways etc., so that we don't have to scroll or less so anyways etc. Code added with the help of gemini 3 pro and then fixed with claude sonnet 4.5's review thanks anyways etc.; check if accurate anyways etc. -->
		# # RJG Start - following line added as per RJG (http://forums.civfanatics.com/showpost.php?p=6996936&postcount=15)
		# # K-Mod, undone
		# screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)
		# #screen.setDimensions(self.L_SCREEN, screen.centerY(0), self.W_SCREEN, self.H_SCREEN)
		# # RJG end
		screen.setDimensions(self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN)

		screen.showWindowBackground(False)
		screen.setText(self.EXIT_ID, "", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		self.nWidgetCount = 0
		self.nLineCount = 0
		
		if (CyGame().isDebugMode()):
			self.szDropdownName = self.getWidgetName(self.DEBUG_DROPDOWN_ID)
			screen.addDropDownBoxGFC(self.szDropdownName, 22, 12, 300, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
			for j in range(gc.getMAX_CIV_PLAYERS()): # advc.007: Exclude Barbarians
				if (gc.getPlayer(j).isAlive()):
					bSelected = False
					if j == self.iActiveLeader:
						bSelected = True
					screen.addPullDownString(self.szDropdownName, gc.getPlayer(j).getName(), j, j, bSelected )

		CyInterface().setDirty(InterfaceDirtyBits.Foreign_Screen_DIRTY_BIT, False)
		
		# Draw leader heads
		self.drawContents(True)
				
	# Drawing Leaderheads
	def drawContents(self, bInitial):
	
		if (self.iScreen < 0):
			return
						
		self.objActiveLeader = gc.getPlayer(self.iActiveLeader)
		self.iActiveTeam = self.objActiveLeader.getTeam()
		self.objActiveTeam = gc.getTeam(self.iActiveTeam)
		self.deleteAllWidgets()
		
		screen = self.getScreen()

		# Header...
		screen.setLabel(self.getNextWidgetName(), "", self.SCREEN_TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.W_SCREEN / 2, self.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
	
		if (self.REV_SCREEN_DICT.has_key(self.iScreen)):
			self.DRAW_DICT[self.REV_SCREEN_DICT[self.iScreen]] (bInitial)
		else:
			return

		# Link to other Foreign advisor screens
		#xLink = self.DX_LINK / 2;
		# K-Mod
		xLink = 0
		if self.iLanguageLoaded != CyGame().getCurrentLanguage():
			self.LABEL_WIDTH_LIST[:] = []
			width_list = []
			for i in self.ORDER_LIST:
				width_list.append(CyInterface().determineWidth(localText.getText(self.TXT_KEY_DICT[i], ()).upper()) + 20)
			total_width = sum(width_list) + CyInterface().determineWidth(localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper()) + 20

			for i in width_list:
				self.LABEL_WIDTH_LIST.append((self.X_EXIT * i + total_width/2) / total_width)

			self.iLanguageLoaded = CyGame().getCurrentLanguage()
		# K-Mod end (except that I've used LABEL_WIDTH_DICT below) 

		for i in range (len (self.ORDER_LIST)):
			szScreen = self.ORDER_LIST[i]
			# BUG - Glance Tab - start
			if szScreen == "GLANCE" and not AdvisorOpt.isShowGlance():
				continue # skip the GLANCE label
			# BUG - Glance Tab - end
			# <advc.ctr>
			if szScreen == "CITIES" and not AdvisorOpt.isCityTradesTab():
				continue #</advc.ctr>
			szTextId = self.getNextWidgetName()
			if (self.iScreen != self.SCREEN_DICT[szScreen]):
				screen.setText (szTextId, "", u"<font=4>" + localText.getText (self.TXT_KEY_DICT[szScreen], ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, xLink + self.LABEL_WIDTH_LIST[i]/2, self.Y_LINK, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_FOREIGN_ADVISOR, self.SCREEN_DICT[szScreen], -1)
			else:
				screen.setText (szTextId, "", u"<font=4>" + localText.getColorText (self.TXT_KEY_DICT[szScreen], (), gc.getInfoTypeForString ("COLOR_YELLOW")).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, xLink + self.LABEL_WIDTH_LIST[i]/2, self.Y_LINK, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_FOREIGN_ADVISOR, -1, -1)
			xLink += self.LABEL_WIDTH_LIST[i]
	
	def drawActive (self, bInitial):
		screen = self.getScreen()

		# Get the Players
		playerActive = gc.getPlayer(self.iActiveLeader)
					
		# Put everything inside a main panel, so we get vertical scrolling
		mainPanelName = self.getNextWidgetName()
		
		#screen.addPanel(mainPanelName, "", "", True, True, 50, 100, self.W_SCREEN - 100, self.H_SCREEN - 200, PanelStyles.PANEL_STYLE_EMPTY)
		# <advc.066> Replacing the above (same as in drawInfoOriginal)
		# <!-- custom: remove the margins same as in the other foreign advisor tabs after our changes anyways etc, similarly to what gemini 3 pro advised in its solution thanks but anyways etc. Note: a negative leftRightMargin value such as -3 allows to remove the last yellow edges that remain at 0 it seems, not applied here for beautification but anyways etc. -->
		# leftRightMargin = 25
		# topBottomMargin = 50
		leftRightMargin = 0
		# <!-- custom: 43 is a bit nicer as it overflows less on the top and bottom, but we lose one leader row with it with the current inter row spacing as of now, so keep 42 rather despite the slight overflowing outside the top and bottom edges as of now but anyways etc. -->
		# <!-- custom: note: does not necessarily lead to one more leader row as it seems (but not sure, check if accurate as this is just a guess of mine even though it does seem to be as such but check to be sure anyways etc.) rows can be higher if they have more lines as of now in the foreign advisor's active tab but doing as such for consistency as well as in base advciv code as well coincidentally i mean if i may say but anyways etc. -->
		topBottomMargin = 42
		mainPanelWidth = self.W_SCREEN - 2 * leftRightMargin
		mainPanelHeight = self.H_SCREEN - 2 * topBottomMargin
		if not gc.getGame().isDebugMode():
			hasMetCount = gc.getTeam(playerActive.getTeam()).getHasMetCivCount(True)
			if hasMetCount > 0: # The 300 is a pretty arbitrary value
				mainPanelHeight = min(mainPanelHeight, 300 * hasMetCount)
		screen.addPanel(mainPanelName, "", "", True, True, leftRightMargin, topBottomMargin, mainPanelWidth, mainPanelHeight, PanelStyles.PANEL_STYLE_EMPTY)
		# </advc.066>

		# loop through all players and sort them by number of active deals
		listPlayers = [(0,0)] * gc.getMAX_PLAYERS()
		nNumPLayers = 0
		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			# <!-- custom: hoist for performance optimization quite similarly to how gemini 3 pro proposed in a related solution but anyways etc. -->
			objLoopPlayer = gc.getPlayer(iLoopPlayer)

			if (objLoopPlayer.isAlive() and iLoopPlayer != self.iActiveLeader and not objLoopPlayer.isBarbarian() and  not objLoopPlayer.isMinorCiv()):
				if (gc.getTeam(objLoopPlayer.getTeam()).isHasMet(gc.getPlayer(self.iActiveLeader).getTeam()) or gc.getGame().isDebugMode()):
					nDeals = 0				
					for i in range(gc.getGame().getIndexAfterLastDeal()):
						deal = gc.getGame().getDeal(i)
						if ((deal.getFirstPlayer() == iLoopPlayer and deal.getSecondPlayer() == self.iActiveLeader) or (deal.getSecondPlayer() == iLoopPlayer and deal.getFirstPlayer() == self.iActiveLeader)):
							nDeals += 1
					listPlayers[nNumPLayers] = (nDeals, iLoopPlayer)
					nNumPLayers += 1
		listPlayers.sort()
		listPlayers.reverse()

		# loop through all players and display leaderheads
		for j in range (nNumPLayers):
			iLoopPlayer = listPlayers[j][1]

			# <!-- custom: hoist for performance optimization quite similarly to how gemini 3 pro proposed in a related solution but anyways etc. -->
			# <!-- custom: note: increment variable naming to avoid weird python non-related scope inheritance/default/fallback or whatever it is called anyways etc. -->
			objLoopPlayer2 = gc.getPlayer(iLoopPlayer)

			# Player panel
			playerPanelName = self.getNextWidgetName()
			# advc.066: Third argument was objLoopPlayer2.getName()
			screen.attachPanel(mainPanelName, playerPanelName, "", "", False, True, PanelStyles.PANEL_STYLE_MAIN)

			screen.attachLabel(playerPanelName, "", "   ")

			screen.attachImageButton(playerPanelName, "", gc.getLeaderHeadInfo(objLoopPlayer2.getLeaderType()).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, -1, False)
						
			innerPanelName = self.getNextWidgetName()
			screen.attachPanel(playerPanelName, innerPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)

			dealPanelName = self.getNextWidgetName()
			screen.attachListBoxGFC(innerPanelName, dealPanelName, "", TableStyles.TABLE_STYLE_EMPTY)	
			screen.enableSelect(dealPanelName, False)

			iRow = 0
			for i in range(gc.getGame().getIndexAfterLastDeal()):
				deal = gc.getGame().getDeal(i)

				if (deal.getFirstPlayer() == iLoopPlayer and deal.getSecondPlayer() == self.iActiveLeader and not deal.isNone()) or (deal.getSecondPlayer() == iLoopPlayer and deal.getFirstPlayer() == self.iActiveLeader):
					szDealText = CyGameTextMgr().getDealString(deal, iLoopPlayer)
					# <advc.072>
					iShowTurnsMode = AdvisorOpt.getShowDealTurns()
					bShowTurns = False
					if iShowTurnsMode == 0 or iShowTurnsMode == 2:
						bShowTurns = True
					# </advc.072>
					# advc.007: Now that CvDeal::isCancelable checks if eByPlayer is a party to the deal, turns-to-cancel isn't shown in the widget anymore. To fix this, treat the ShowDealTurnsLeft option as enabled when viewing the screen from the perspective of another civ in Debug mode.
					if bShowTurns or self.iActiveLeader != gc.getGame().getActivePlayer():
						if BugDll.isPresent():
							if not deal.isCancelable(self.iActiveLeader, False):
								if deal.isCancelable(self.iActiveLeader, True):
									szDealText += u" %s" % BugUtil.getText("INTERFACE_CITY_TURNS", (deal.turnsToCancel(self.iActiveLeader),))
								else:
									# don't bother adding "This deal cannot be canceled" message
									#szDealText += u" (%s)" % deal.getCannotCancelReason(self.iActiveLeader)
									pass
						else:
							iTurns = DealUtil.Deal(deal).turnsToCancel(self.iActiveLeader)
							if iTurns > 0:
								szDealText += u" %s" % BugUtil.getText("INTERFACE_CITY_TURNS", (iTurns,))
					screen.appendListBoxString(dealPanelName, szDealText, WidgetTypes.WIDGET_DEAL_KILL, deal.getID(), -1, CvUtil.FONT_LEFT_JUSTIFY)
					iRow += 1

	#	RJG Start
	def drawRelations (self, bInitial):
		screen = self.getScreen()
		#self.W_SCREEN = screen.getXResolution() - 40
		#self.X_SCREEN = (screen.getXResolution() - 24) / 2

		# <!-- custom: in the foreign advisor and similar screens, we can't see all info in one screen when there are too many players, yet the window does not use all the game window space. Make it larger, similarly to what we did for sevopedia anyways etc., so that we don't have to scroll or less so anyways etc. Code added with the help of gemini 3 pro and then fixed with claude sonnet 4.5's review thanks anyways etc.; check if accurate anyways etc. -->
		# self.X_LEADER_CIRCLE_TOP = self.X_SCREEN
		# --- FIX: Center the web in the middle of the screen ---
		# We take the full screen width and divide by 2 to find the center pixel
		self.X_LEADER_CIRCLE_TOP = self.W_SCREEN // 2

		CvForeignAdvisor.CvForeignAdvisor.drawRelations (self, bInitial)
	#	RJG End

	def drawInfo (self, bInitial):
		if AdvisorOpt.isUseImprovedEFAInfo():
			self.drawInfoImproved(bInitial)
		else:
			self.drawInfoOriginal(bInitial)

	def drawInfoOriginal (self, bInitial):
		# ExoticForPrint ("Entered drawInfo")

		screen = self.getScreen()

		# Get the Players
		playerActive = gc.getPlayer(self.iActiveLeader)
					
		# Put everything inside a main panel, so we get vertical scrolling
		mainPanelName = self.getNextWidgetName()
		
		#screen.addPanel(mainPanelName, "", "", True, True, 50, 100, self.W_SCREEN - 100, self.H_SCREEN - 200, PanelStyles.PANEL_STYLE_EMPTY)
		# <advc.066> Replacing the above (same as in drawActive)
		# <!-- custom: remove the margins same as in the other foreign advisor tabs after our changes anyways etc, similarly to what gemini 3 pro advised in its solution thanks but anyways etc. Note: a negative leftRightMargin value such as -3 allows to remove the last yellow edges that remain at 0 it seems, not applied here for beautification but anyways etc. -->
		# leftRightMargin = 25
		# topBottomMargin = 50
		leftRightMargin = 0
		# <!-- custom: 43 is a bit nicer as it overflows less on the top and bottom, but we lose one leader row with it with the current inter row spacing as of now, so keep 42 rather despite the slight overflowing outside the top and bottom edges as of now but anyways etc. -->
		topBottomMargin = 42
		mainPanelWidth = self.W_SCREEN - 2 * leftRightMargin
		mainPanelHeight = self.H_SCREEN - 2 * topBottomMargin

		# <!-- custom: hoist for performance optimization, done with the help of gemini 3 pro thanks anyways etc. -->
		bDebugMode = gc.getGame().isDebugMode()
		playerActiveTeam = playerActive.getTeam()

		if not bDebugMode:
			hasMetCount = gc.getTeam(playerActiveTeam).getHasMetCivCount(True)
			if hasMetCount > 0: # 100 was just a guess, but it seems like this is the exact height of a row.
				mainPanelHeight = min(mainPanelHeight, 100 * hasMetCount)
		screen.addPanel(mainPanelName, "", "", True, True, leftRightMargin, topBottomMargin, mainPanelWidth, mainPanelHeight, PanelStyles.PANEL_STYLE_EMPTY)
		# </advc.066>

		ltCivicOptions = range (gc.getNumCivicOptionInfos())

		# <!-- custom: add spacing so the parts of the row is not stuck to the other ones too tight quite similarly to how per gemini 3 pro's suggested as part of its solution thanks but anyways etc. -->
		# This adds spaces to separate 'Current Civics' from 'Favorites'
		# szSeparator = ""
		szSeparator = "                                                                         "
		# <!-- custom: hoist and compute once the strings is computationally more efficient anyways etc -->
		# <!-- custom: remove unneeded civics text as it's distracting and the civics listing is already self-explanatory or fairly easily guessable or searchable but anyways etc. -->
		# szCivicsPreText = szSeparator + localText.getText("TXT_KEY_CIVICS_SCREEN_TITLE", ()) + ":"
		szCivicsPreText = szSeparator
		# <!-- custom: add spacing so the Favorites part of the row is not stuck to the other ones too tight quite similarly to how per gemini 3 pro's suggested as part of its solution thanks but anyways etc. -->
		# szFavoritesPreText = localText.getText("TXT_KEY_PEDIA_FAVORITES", ()) + ":"
		szFavoritesPreText = szSeparator + localText.getText("TXT_KEY_PEDIA_FAVORITES", ()) + ":"

		# loop through all players and display leaderheads
		# Their leaderheads		
		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			# <!-- custom: hoist for performance optimization, done with the help of gemini 3 pro thanks anyways etc. -->
			objLoopPlayer = gc.getPlayer(iLoopPlayer)

			if (objLoopPlayer.isAlive() and iLoopPlayer != self.iActiveLeader and (gc.getTeam(objLoopPlayer.getTeam()).isHasMet(playerActiveTeam) or bDebugMode) and not objLoopPlayer.isBarbarian() and not objLoopPlayer.isMinorCiv()):

				nPlayerReligion = objLoopPlayer.getStateReligion()
				objReligion = gc.getReligionInfo (nPlayerReligion)

				objLeaderHead = gc.getLeaderHeadInfo (objLoopPlayer.getLeaderType())

				# Player panel
				playerPanelName = self.getNextWidgetName()
				# advc.066: Third argument was objLoopPlayer.getName()
				screen.attachPanel(mainPanelName, playerPanelName, "", "", False, True, PanelStyles.PANEL_STYLE_MAIN)

				screen.attachImageButton(playerPanelName, "", objLeaderHead.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader, False)

				infoPanelName = self.getNextWidgetName()
				screen.attachPanel(playerPanelName, infoPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)

				religionName = self.getNextWidgetName()
				szPlayerReligion = ""

				if (nPlayerReligion != -1):

					if (objLoopPlayer.hasHolyCity (nPlayerReligion)):
						szPlayerReligion = u"%c" %(objReligion.getHolyCityChar())
					elif objReligion:
						szPlayerReligion = u"%c" %(objReligion.getChar())

				screen.attachTextGFC(infoPanelName, "", szPlayerReligion, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				# advc.004: BULL widget help enabled
				screen.attachTextGFC(infoPanelName, "", localText.getText("TXT_KEY_FOREIGN_ADVISOR_TRADE", (self.calculateTrade (self.iActiveLeader, iLoopPlayer)[0], )), FontTypes.GAME_FONT,  WidgetTypes.WIDGET_TRADE_ROUTES, self.iActiveLeader, iLoopPlayer)

				screen.attachTextGFC(infoPanelName, "", szCivicsPreText, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

				for nCivicOption in ltCivicOptions:
					nCivic = objLoopPlayer.getCivics (nCivicOption)
					screen.attachImageButton (infoPanelName, "", gc.getCivicInfo (nCivic).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, nCivic, 1, False)

				# <!-- custom: also show favorite religions in the foreign advisor's info tab anyways etc. Code added with the help of gemini 3 pro thanks anyways etc, also refactor this part of the code as well for clarity anyways etc. -->
				nFavoriteCivic = objLeaderHead.getFavoriteCivic()
				hasFavoriteCivic = (objLoopPlayer.isFavoriteCivicKnown() and nFavoriteCivic != -1) # advc.130n

				nFavoriteReligion = objLeaderHead.getFavoriteReligion()
				hasFavoriteReligion = (nFavoriteReligion != -1)

				if (hasFavoriteCivic or hasFavoriteReligion):
					screen.attachTextGFC(infoPanelName, "", szFavoritesPreText, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

					if hasFavoriteCivic:
						objCivicInfo = gc.getCivicInfo(nFavoriteCivic)
						screen.attachImageButton (infoPanelName, "", objCivicInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, nFavoriteCivic, 1, False)
						# <!-- custom: remove the "(Government)" or "(Economy)" or such types of text as they are distracting and no longer relevant since we have favorite religions as well anyways etc. -->
						#screen.attachTextGFC(infoPanelName, "", "(" + gc.getCivicOptionInfo (objCivicInfo.getCivicOptionType()).getDescription() + ")", FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

					if hasFavoriteReligion:
						objReligionInfo = gc.getReligionInfo(nFavoriteReligion)
						if objReligionInfo:
							screen.attachImageButton(infoPanelName, "", objReligionInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, nFavoriteReligion, 1, False)



	def drawInfoImproved (self, bInitial):
		screen = self.getScreen()

		# Some spacing variables to help with the layout
		iOutsideGap = 6
		iInsideGap = 10
		iBetweenGap = iOutsideGap - 2
		iHeaderHeight = 32

		# Header
		headerBackgroundPanelName = self.getNextWidgetName()
		iLeft = iOutsideGap
		iTop = 50 + iOutsideGap
		iWidth = self.W_SCREEN - (2 * iOutsideGap)
		iHeight = iHeaderHeight + (2 * iInsideGap)
		screen.addPanel(headerBackgroundPanelName, "", "", True, False, iLeft, iTop, iWidth, iHeight, PanelStyles.PANEL_STYLE_MAIN)

		headerPanelName = self.getNextWidgetName()
		iLeft = iLeft + iInsideGap
		iTop = iTop + iInsideGap
		iWidth = iWidth - (2 * iInsideGap)
		iHeight = iHeaderHeight
		screen.addPanel(headerPanelName, "", "", False, True, iLeft, iTop, iWidth, iHeight, PanelStyles.PANEL_STYLE_EMPTY)

		iOffset = 0

		# <!-- custom: i don't know what this is for, but since we renamed it to as of now just "Favorites:" to include favorite religions as well, may as well remove this alternative one anyways etc. -->
		# if FavoriteCivicDetector.isDetectionNecessary():
		# 	fcHeaderText = BugUtil.getPlainText("TXT_KEY_FOREIGN_ADVISOR_POSSIBLE_FAV_CIVICS")
		# else:
		# 	fcHeaderText = BugUtil.getPlainText("TXT_KEY_PEDIA_FAV_CIVIC")
		fcHeaderText = BugUtil.getPlainText("TXT_KEY_PEDIA_FAVORITES")
		
		for headerText in (
			BugUtil.getPlainText("TXT_KEY_FOREIGN_ADVISOR_ABBR_LEADER"),
			BugUtil.getPlainText("TXT_KEY_FOREIGN_ADVISOR_ABBR_ATTITUDE"),
			u"%c" %(CyGame().getSymbolID(FontSymbols.RELIGION_CHAR)), 
			u"%c" %(CyGame().getSymbolID(FontSymbols.TRADE_CHAR)),
			u"%c%c" %(CyGame().getSymbolID(FontSymbols.TRADE_CHAR),gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getChar()),
			BugUtil.getPlainText("TXT_KEY_CIVICOPTION_ABBR_GOVERNMENT"),
			BugUtil.getPlainText("TXT_KEY_CIVICOPTION_ABBR_LEGAL"),
			BugUtil.getPlainText("TXT_KEY_CIVICOPTION_ABBR_LABOR"),
			BugUtil.getPlainText("TXT_KEY_CIVICOPTION_ABBR_ECONOMY"),
			BugUtil.getPlainText("TXT_KEY_CIVICOPTION_ABBR_RELIGION"),
			"",
			fcHeaderText
		):
			itemName = self.getNextWidgetName()
			screen.attachTextGFC(headerPanelName, itemName, headerText, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)
			iOffset = iOffset + 65

		# Main
		mainBackgroundPanelName = self.getNextWidgetName()
		iLeft = iOutsideGap
		iTop = iTop + iHeaderHeight + iInsideGap + iBetweenGap
		iWidth = self.W_SCREEN - (2 * iOutsideGap)
		iHeight = self.H_SCREEN - 100 - (2 * iOutsideGap) - iBetweenGap - iHeaderHeight - (2 * iInsideGap)
		screen.addPanel(mainBackgroundPanelName, "", "", True, False, iLeft, iTop, iWidth, iHeight, PanelStyles.PANEL_STYLE_MAIN)

		mainPanelName = self.getNextWidgetName()
		iLeft = iLeft + iInsideGap
		iTop = iTop + iInsideGap
		iWidth = iWidth - (2 * iInsideGap)
		iHeight = iHeight - (2 * iInsideGap)
		screen.addPanel(mainPanelName, "", "", True, True, iLeft, iTop, iWidth, iHeight, PanelStyles.PANEL_STYLE_EMPTY)

		FavoriteCivicDetector.doUpdate()
		
		# display the active player's row at the top
		self.drawInfoRow(screen, mainPanelName, self.iActiveLeader, PanelStyles.PANEL_STYLE_MAIN_BLACK25)

		# loop through all other players and add their rows; show known first
		lKnownPlayers = []
		lUnknownPlayers = []
		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			if (iLoopPlayer != self.iActiveLeader):
				objLoopPlayer = gc.getPlayer(iLoopPlayer)
				if (self.objActiveTeam.isHasMet(objLoopPlayer.getTeam()) or bDebugMode):
					lKnownPlayers.append(iLoopPlayer)
				else:
					lUnknownPlayers.append(iLoopPlayer)
		for iLoopPlayer in lKnownPlayers:
			self.drawInfoRow(screen, mainPanelName, iLoopPlayer, PanelStyles.PANEL_STYLE_OUT)
		for iLoopPlayer in lUnknownPlayers:
			self.drawInfoRow(screen, mainPanelName, iLoopPlayer, PanelStyles.PANEL_STYLE_OUT)

	def drawInfoRow (self, screen, mainPanelName, iLoopPlayer, ePanelStyle):
		objLoopPlayer = gc.getPlayer(iLoopPlayer)
		iLoopTeam = objLoopPlayer.getTeam()
		objLoopTeam = gc.getTeam(iLoopTeam)
		bIsActivePlayer = (iLoopPlayer == self.iActiveLeader)
		if (objLoopPlayer.isAlive()
			#and (self.objActiveTeam.isHasMet(iLoopTeam) or gc.getGame().isDebugMode())
			and not objLoopPlayer.isBarbarian()
			and not objLoopPlayer.isMinorCiv()):
			
			objLeaderHead = gc.getLeaderHeadInfo (objLoopPlayer.getLeaderType())
			objAttitude = AttitudeUtil.Attitude(iLoopPlayer, self.iActiveLeader)

			# Player panel
			playerPanelName = self.getNextWidgetName()
			szPlayerLabel = "" # objLoopPlayer.getName()
			screen.attachPanel(mainPanelName, playerPanelName, szPlayerLabel, "", False, True, ePanelStyle)

			# Panels always created but essentially blank if unmet
			itemName = self.getNextWidgetName()
			if (not self.objActiveTeam.isHasMet(iLoopTeam) and not gc.getGame().isDebugMode()):
				screen.attachImageButton(playerPanelName, itemName, gc.getDefineSTRING("LEADERHEAD_RANDOM"), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_GENERAL, -1, -1, False)
				return
			else:
				screen.attachImageButton(playerPanelName, itemName, objLeaderHead.getButton(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader, False)
			#screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)
					
			infoPanelName = self.getNextWidgetName()
			screen.attachPanel(playerPanelName, infoPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)

			# Attitude
			itemName = self.getNextWidgetName()
			if (not bIsActivePlayer):
				szAttStr = "<font=2>" + objAttitude.getText(True, True, False, False) + "</font>"
			else:
				szAttStr = ""
			# advc.004: BULL widget help enabled
			screen.attachTextGFC(infoPanelName, itemName, szAttStr, FontTypes.GAME_FONT, WidgetTypes.WIDGET_LEADERHEAD_RELATIONS, iLoopPlayer, self.iActiveLeader)
			# Disable the widget if this is active player since it's a blank string.
			if bIsActivePlayer:
				screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)

			# Religion
			itemName = self.getNextWidgetName()
			nReligion = objLoopPlayer.getStateReligion()
			if (nReligion != -1):
				objReligion = gc.getReligionInfo (nReligion)

				if (objLoopPlayer.hasHolyCity (nReligion)):
					szPlayerReligion = u"%c" %(objReligion.getHolyCityChar())
				elif objReligion:
					szPlayerReligion = u"%c" %(objReligion.getChar())

				if (not bIsActivePlayer):
					iDiploModifier = 0
					if (nReligion == self.objActiveLeader.getStateReligion()):
						iDiploModifier = objAttitude.getModifier("TXT_KEY_MISC_ATTITUDE_SAME_RELIGION")
					else:
						iDiploModifier = objAttitude.getModifier("TXT_KEY_MISC_ATTITUDE_DIFFERENT_RELIGION")
					if (iDiploModifier):
						if (iDiploModifier > 0):
							szColor = "COLOR_GREEN"
						else:
							szColor = "COLOR_RED"
						szPlayerReligion = localText.changeTextColor(szPlayerReligion + " [%+d]" % (iDiploModifier), gc.getInfoTypeForString(szColor))
				szPlayerReligion = "<font=2>" + szPlayerReligion + "</font>"
			else:
				szPlayerReligion = ""
			# advc.004: BULL widget help enabled
			screen.attachTextGFC(infoPanelName, itemName, szPlayerReligion, FontTypes.GAME_FONT, WidgetTypes.WIDGET_LEADERHEAD_RELATIONS, iLoopPlayer, self.iActiveLeader)
			# Disable the widget if this is active player since we don't have diplo info.
			if bIsActivePlayer:
				screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)
			
			# Trade
			if (bIsActivePlayer or objLoopPlayer.canHaveTradeRoutesWith(self.iActiveLeader)):
				(iTradeCommerce, iTradeRoutes) = self.calculateTrade (self.iActiveLeader, iLoopPlayer)
				# advc.001: Commented out (cf. TradeUtil.py)
				#if TradeUtil.isFractionalTrade():
				#	iTradeCommerce //= 100
				szTradeYield = u"%d %c" % (iTradeCommerce, gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getChar())
				szTradeRoutes = u"%d" % (iTradeRoutes)
			else:
				szTradeYield = u"-"
				szTradeRoutes = u"-"
			itemName = self.getNextWidgetName()
			# advc.004: BULL widget help enabled (2x)
			screen.attachTextGFC(infoPanelName, itemName, szTradeRoutes, FontTypes.GAME_FONT, WidgetTypes.WIDGET_TRADE_ROUTES, self.iActiveLeader, iLoopPlayer)
			itemName = self.getNextWidgetName()
			screen.attachTextGFC(infoPanelName, itemName, szTradeYield, FontTypes.GAME_FONT, WidgetTypes.WIDGET_TRADE_ROUTES, self.iActiveLeader, iLoopPlayer)

			# Civics
			for nCivicOption in range (gc.getNumCivicOptionInfos()):
				nCivic = objLoopPlayer.getCivics (nCivicOption)
				buttonName = self.getNextWidgetName()
				screen.attachImageButton (infoPanelName, buttonName, gc.getCivicInfo (nCivic).getButton(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, nCivic, 1, False)

			# Spacer so Favorite Civics aren't right next to current civics
			screen.attachTextGFC(infoPanelName, "", " ", FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			
			# Favorite Civic
			if (not bIsActivePlayer):
				nFavoriteCivic = objLeaderHead.getFavoriteCivic()
				if FavoriteCivicDetector.isDetectionNecessary():
					objFavorite = FavoriteCivicDetector.getFavoriteCivicInfo(iLoopPlayer)
					if objFavorite.isKnown():
						# We know it. Fall through to standard procedure after setting it.
						nFavoriteCivic = objFavorite.getFavorite()
					else:
						iNumPossibles = objFavorite.getNumPossibles()
						BugUtil.debug("CvExoticForeignAdvisor::drawInfoRows() Number of Guesses: %d" %(iNumPossibles))
						if iNumPossibles > 5:
							# Too many possibilities; display question mark
							screen.attachImageButton (infoPanelName, "", "Art/BUG/QuestionMark.dds", GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_GENERAL, -1, -1, False)
							return
						else:
							# Loop over possibles and display all
							for nFavoriteCivic in objFavorite.getPossibles():
								objCivicInfo = gc.getCivicInfo (nFavoriteCivic)
								screen.attachImageButton (infoPanelName, "", objCivicInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, nFavoriteCivic, 1, False)
							return
					
				if nFavoriteCivic != -1:
					objCivicInfo = gc.getCivicInfo (nFavoriteCivic)
					screen.attachImageButton (infoPanelName, "", objCivicInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, nFavoriteCivic, 1, False)
					if (self.objActiveLeader.isCivic (nFavoriteCivic)):
						iDiploModifier = objAttitude.getModifier("TXT_KEY_MISC_ATTITUDE_FAVORITE_CIVIC")
						if (iDiploModifier):
							if (iDiploModifier > 0):
								szColor = "COLOR_GREEN"
							else:
								szColor = "COLOR_RED"
							szDiplo = "<font=2>" + localText.changeTextColor(" [%+d]" % (iDiploModifier), gc.getInfoTypeForString(szColor)) + "</font>"
						else:
							szDiplo = ""
						itemName = self.getNextWidgetName()
						# advc.004: BULL widget help enabled
						screen.attachTextGFC(infoPanelName, itemName, szDiplo, FontTypes.GAME_FONT, WidgetTypes.WIDGET_LEADERHEAD_RELATIONS, iLoopPlayer, self.iActiveLeader)
						#screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)

	def calculateTrade (self, nPlayer, nTradePartner):
		# Trade status...
		iDomesticYield, iDomesticCount, iForeignYield, iForeignCount = TradeUtil.calculateTradeRoutes(nPlayer, nTradePartner)
		return iDomesticYield + iForeignYield, iDomesticCount + iForeignCount

	def drawGlance (self, bInitial):
		# ExoticForPrint ("Entered drawGlance")

		screen = self.getScreen()
		
		# <advc.066> Reduce panel height when there are few civs
		self.mainPanelHeight = self.H_SCREEN - 155
		if not gc.getGame().isDebugMode():
			playerActive = gc.getPlayer(self.iActiveLeader)
			hasMetCount = gc.getTeam(playerActive.getTeam()).getHasMetCivCount(True)
			self.mainPanelHeight = min(self.mainPanelHeight, 100 * (hasMetCount + 1))
		# </advc.066>

		# Put everything inside a main panel, so we get vertical scrolling
		headerPanelName = self.getNextWidgetName()
		screen.addPanel(headerPanelName, "", "", True, True, 0, 50, self.W_SCREEN, 60, PanelStyles.PANEL_STYLE_TOPBAR)

		if (bInitial):
			self.initializeGlance()
			self.iSelectedLeader = self.iActiveLeader

		self.drawGlanceHeader(screen, headerPanelName)

		mainPanelName = self.getNextWidgetName()
		# advc.066: The height was self.H_SCREEN - 155, now computed above.

		# <!-- custom: add extra width tweak to remove the yellow side edges, and extra height tweak to remove distracting top bright band plus have more room on bottom side's row as well, with gemini 3 pro's help thanks anyways etc. -->
		# iExtraWidth = 0
		iExtraWidth = 4
		# iExtraHeight = 0
		iExtraHeight = 7

		# <!-- custom: adjust base Y (was 104) as it was a bit too low (as in at the bottom anyways etc.) which led to an asymetrical display in bottom being too high as compared to top's edge over limit after our changes, vs now it being much more centered which allows to more cleanly/easily adjust iExtraHeight anyways etc. -->
		screen.addPanel(mainPanelName, "", "", True, True, 0 - iExtraWidth, 106 - iExtraHeight, self.W_SCREEN + (2 * iExtraWidth), self.mainPanelHeight + (2 * iExtraHeight), PanelStyles.PANEL_STYLE_MAIN)
		self.drawGlanceRows (screen, mainPanelName, self.iSelectedLeader != self.iActiveLeader, self.iSelectedLeader)

	def initializeGlance (self):
		self.nCount = 0
		self.ltPlayerRelations = [[0] * gc.getMAX_PLAYERS() for i in range (gc.getMAX_PLAYERS())]
		self.ltPlayerMet = [False] * gc.getMAX_PLAYERS()
		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			# <!-- custom: hoist for performance optimization quite similarly to how gemini 3 pro proposed in a related solution but anyways etc. -->
			objLoopPlayer = gc.getPlayer(iLoopPlayer)

			if (objLoopPlayer.isAlive()
			and (gc.getTeam(objLoopPlayer.getTeam()).isHasMet(gc.getPlayer(self.iActiveLeader).getTeam())
			or gc.getGame().isDebugMode())
			and not objLoopPlayer.isBarbarian()
			and not objLoopPlayer.isMinorCiv()
			# <advc.130v> Exclude capitulated vassals. The last check is for AI Auto Play.
			and (not gc.getTeam(objLoopPlayer.getTeam()).isCapitulated()
			or objLoopPlayer.isHuman() or iLoopPlayer == self.iActiveLeader)):
			# </advc.130v>
				# ExoticForPrint ("Player = %d" % iLoopPlayer)
				self.ltPlayerMet [iLoopPlayer] = True

				for nHost in range(gc.getMAX_PLAYERS()):
					if (gc.getPlayer(nHost).isAlive()
					and nHost != self.iActiveLeader
					and (gc.getTeam(gc.getPlayer(nHost).getTeam()).isHasMet(gc.getPlayer(self.iActiveLeader).getTeam())
					or gc.getGame().isDebugMode())
					and not gc.getPlayer(nHost).isBarbarian()
					and not gc.getPlayer(nHost).isMinorCiv()):
						nRelation = AttitudeUtil.getAttitudeCount(nHost, iLoopPlayer)
						self.ltPlayerRelations [iLoopPlayer][nHost] = nRelation

				# Player panel
				self.nCount += 1
		# advc.066: Was (self.W_SCREEN - 20) /... I don't think there are margins to account for here.
		self.X_Spread = self.W_SCREEN / self.nCount
		if self.X_Spread < 57:
			self.X_Spread = 57 # advc.066: Lower bound was 58
		# advc.066: Was (self.H_SCREEN - 50) /...
		self.Y_Spread = (self.mainPanelHeight + 105) / (self.nCount + 2)
		self.Y_Text_Offset = (self.Y_Spread - 36) / 2
		if self.Y_Text_Offset < 0:
			self.Y_Text_Offset = 0

	def drawGlanceHeader (self, screen, panelName):
		nCount = 1
		for iLoopPlayer in range (gc.getMAX_PLAYERS()):
			# <!-- custom: hoist for performance optimization quite similarly to how gemini 3 pro proposed in a related solution but anyways etc. -->
			currentPlayer = gc.getPlayer(iLoopPlayer)

			if self.ltPlayerMet[iLoopPlayer]:
				if (iLoopPlayer != self.iActiveLeader):
					szName = self.getNextWidgetName()
					screen.addCheckBoxGFCAt(panelName, szName, gc.getLeaderHeadInfo(currentPlayer.getLeaderType()).getButton(), ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), self.X_GLANCE_OFFSET + (self.X_Spread * nCount), self.Y_GLANCE_OFFSET, self.GLANCE_BUTTON_SIZE, self.GLANCE_BUTTON_SIZE, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader, ButtonStyles.BUTTON_STYLE_LABEL, False)
					if (self.iSelectedLeader == iLoopPlayer):
						screen.setState(szName, True)
					else:
						screen.setState(szName, False)
					nCount += 1
		
	def drawGlanceRows (self, screen, mainPanelName, bSorted = False, nPlayer = 1):
		# ExoticForPrint ("MAX Players = %d" % gc.getMAX_PLAYERS())
		ltSortedRelations = [(None,-1)] * gc.getMAX_PLAYERS()
		self.loadColIntoList (self.ltPlayerRelations, ltSortedRelations, nPlayer)
		if bSorted:
			ltSortedRelations.sort()
			if (self.bGlancePlus):
				ltSortedRelations.reverse()
			self.bGlancePlus = not self.bGlancePlus
		else:
			# If not sorted, we take the original ID list and move active player to the front.
			#ltSortedRelations = map(lambda x: (0, x), range(gc.getMAX_PLAYERS()))
			nFirstElement = self.ltPlayerRelations[self.iActiveLeader][nPlayer]
			ltSortedRelations.remove((nFirstElement, self.iActiveLeader))
			ltSortedRelations.insert(0, (nFirstElement, self.iActiveLeader))

		# loop through all players and display leaderheads
		for nOffset in range (gc.getMAX_PLAYERS()):
			if ltSortedRelations[nOffset][1] != -1:
				break

		for i in range (self.nCount):
			iLoopPlayer = ltSortedRelations[nOffset + i][1]
			# ExoticForPrint ("iLoopPlayer = %d" % iLoopPlayer)

			# <!-- custom: hoist for performance optimization quite similarly to how gemini 3 pro proposed in a related solution but anyways etc. -->
			currentPlayer = gc.getPlayer(iLoopPlayer)

			playerPanelName = self.getNextWidgetName()
			if iLoopPlayer == self.iActiveLeader:
				screen.attachPanel(mainPanelName, playerPanelName, "", "", False, True, PanelStyles.PANEL_STYLE_MAIN_BLACK50)
			else:
				screen.attachPanel(mainPanelName, playerPanelName, "", "", False, True, PanelStyles.PANEL_STYLE_MAIN_BLACK25)

			nCount = 1

			# <!-- custom: This is extra info by gemini 3 pro; check if accurate anyways etc. -->
			# Inner Loop: Draw the columns
			# iLoopPlayer = The Row Leader (You, or an AI)
			# j           = The Column Leader (The Rival)

			for j in range (gc.getMAX_PLAYERS()):
				if self.ltPlayerMet[j]:
					# <!-- custom: This is extra info by gemini 3 pro; check if accurate anyways etc. -->
					# This line HIDES the column for the Human Player (You), which matches your screenshot.
					if j != self.iActiveLeader:
						szName = self.getNextWidgetName()
						nAttitude = self.ltPlayerRelations[iLoopPlayer][j]

						# <!-- custom: This is extra info by gemini 3 pro; check if accurate anyways etc. -->
						# 1. Base Attitude Text (Smilies/Numbers)
						if nAttitude != None:
							szText = AttitudeUtil.getAttitudeText(j, iLoopPlayer, AdvisorOpt.isShowGlanceNumbers(), AdvisorOpt.isShowGlanceSmilies(), True, True, AdvisorOpt.isShowGlanceWarTrades()) # advc.152: WarTrades added
						else:
							szText = ""

						# <!-- custom: add "Willing to become a vassal" type of button as it is useful for the human player to see it in UI in the glances tab anyways etc. Also for information or exhaustiveness the human player occupies the first row and has no column in the glances tab it seems if i'm not mistaken anyways etc. Added with the combined help of claude sonnet 4.5 and gemini pro 3, since neither could get it right on their own or fast enough; claude helped most but gemini too and me too i mean thanks to me too but anyways etc. I fed claude the C++ code of int CvTeamAI::AI_vassalTradeVal, DenialTypes CvTeamAI::AI_vassalTrade, int CvTeamAI::AI_surrenderTradeVal, and DenialTypes CvTeamAI::AI_surrenderTrade, since its previous python implementation didn't work. Check if accurate anyways etc. -->
						# Goal: If this is MY Row (iLoopPlayer is me), check if the RIVAL (j) wants to be my vassal.
						# Vassal Check (Human Row Edition)
						if iLoopPlayer == self.iActiveLeader:
							# Define roles for this specific check
							pPotentialVassal = gc.getPlayer(j)           # The Rival (Column)
							# pPotentialMaster = currentPlayer           # Me (Row)

							# A. Are they ALREADY our vassal?
							if gc.getTeam(pPotentialVassal.getTeam()).isVassal(currentPlayer.getTeam()):
								szText += self.VASSAL_ICON

							# B. Are they WILLING to become our vassal?
							else:
								tradeData = TradeData()

								# Check 1: Peaceful Vassal
								tradeData.ItemType = TradeableItems.TRADE_VASSAL

								# Can we trade it? AND Is there NO denial?
								# Note: We ask if *pPotentialVassal* can trade *Vassal State* to *Us*
								if pPotentialVassal.canTradeItem(iLoopPlayer, tradeData, False):
									if pPotentialVassal.getTradeDenial(iLoopPlayer, tradeData) == DenialTypes.NO_DENIAL:
										szText += self.WILLING_VASSAL_ICON

								# Check 2: Capitulation (Surrender during war)
								# Only check if they are at war with us
								elif gc.getTeam(pPotentialVassal.getTeam()).isAtWar(currentPlayer.getTeam()):
									tradeData.ItemType = TradeableItems.TRADE_SURRENDER
									if pPotentialVassal.canTradeItem(iLoopPlayer, tradeData, False):
										if pPotentialVassal.getTradeDenial(iLoopPlayer, tradeData) == DenialTypes.NO_DENIAL:
											szText += self.WILLING_VASSAL_ICON
						# End - Vassal Check (Human Row Edition)

						# <advc.152>
						widgType = WidgetTypes.WIDGET_LEADERHEAD_RELATIONS
						if AdvisorOpt.isShowGlanceWarTrades():
							widgType = WidgetTypes.WIDGET_LH_GLANCE
						# </advc.152>
						screen.setTextAt (szName, playerPanelName, szText, CvUtil.FONT_CENTER_JUSTIFY, self.X_GLANCE_OFFSET - 2 + (self.X_Spread * nCount), self.Y_GLANCE_OFFSET + self.Y_Text_Offset, -0.1, FontTypes.GAME_FONT, widgType, j, iLoopPlayer)
						nCount += 1

			if nCount > 8:
				screen.attachImageButton(playerPanelName, "", gc.getLeaderHeadInfo(currentPlayer.getLeaderType()).getButton(), GenericButtonSizes.BUTTON_SIZE_32, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader, False)
			else:
				screen.attachImageButton(playerPanelName, "", gc.getLeaderHeadInfo(currentPlayer.getLeaderType()).getButton(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader, False)

	def loadColIntoList (self, ltPlayers, ltTarget, nCol):
		nCount = 0
		for i in range (len (ltTarget)):
			if (self.ltPlayerMet[i]):
				# ExoticForPrint ("player met = %d; nCount = %d" % (i, nCount))
				ltTarget[nCount] = (ltPlayers[i][nCol], i)
				nCount += 1

	def handlePlusMinusToggle (self):
		# ExoticForPrint ("Entered handlePlusMinusToggle")

		self.bGlancePlus = not self.bGlancePlus
		self.drawContents (False)

	############################################
	### BEGIN CHANGES ENHANCED INTERFACE MOD ###
	############################################

	def initTradeTable(self):
		screen = self.getScreen()
		# advc.073: Moved the first of the two IconGrid_BUG.GRID_TEXT_COLUMN (GPT that the AI will pay) three positions back in both branches
		if (self.RES_SHOW_ACTIVE_TRADE):
			columns = ( IconGrid_BUG.GRID_ICON_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_TEXT_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_TEXT_COLUMN )
		else:
			columns = ( IconGrid_BUG.GRID_ICON_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_TEXT_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN )
		self.NUM_RESOURCE_COLUMNS = len(columns) - 1

		# <advc> Intermediate values leftSpace and topSpace added
		# <!-- custom: we don't need all this yellow empty space, better use it for our blue panel and grids or/and such to show more information anyways etc. -->
		# leftSpace = self.MIN_LEFT_RIGHT_SPACE + 10
		# topSpace = self.MIN_TOP_BOTTOM_SPACE + 10
		leftSpace = 0
		topSpace = self.MIN_TOP_BOTTOM_SPACE

		gridX = leftSpace
		# <!-- custom: not sure how this all works, some changes don't seem effective at all, manually adjusting as such empirically if i may say but anyways etc. and randomly as such somehow seemed to land it right but anyways etc. -->
		# gridY = topSpace + self.RES_SURPLUS_HEIGHT + self.RES_PANEL_SPACE + self.TITLE_HEIGHT
		gridY = topSpace + self.RES_SURPLUS_HEIGHT + self.RES_PANEL_SPACE + self.TITLE_HEIGHT - 60
		gridWidth = self.W_SCREEN - gridX - leftSpace
		# <!-- custom: adjust empirically height as it now overfills on bottom but anyways etc. -->
		gridHeight = self.H_SCREEN - gridY - topSpace
		# </advc>

		self.resIconGridName = self.getNextWidgetName()
		self.resIconGrid = IconGrid_BUG.IconGrid_BUG( self.resIconGridName, screen, gridX, gridY, gridWidth, gridHeight, columns, True, self.SHOW_LEADER_NAMES, self.SHOW_ROW_BORDERS )

		self.resIconGrid.setGroupBorder(self.GROUP_BORDER)
		self.resIconGrid.setGroupLabelOffset(self.GROUP_LABEL_OFFSET)
		self.resIconGrid.setMinColumnSpace(self.MIN_COLUMN_SPACE)
		self.resIconGrid.setMinRowSpace(self.MIN_ROW_SPACE)
		
		self.leaderCol = 0
		#self.surplusCol = 1
		#self.usedCol = 2
		#self.willTradeCol = 3
		#self.wontTradeCol = 4
		#self.canPayCol = 5
		# <advc.073>
		self.willImportCol = 1
		self.canPayCol = 2
		self.willExportCol = 3
		self.wontExportCol = 4
		self.noNeedCol = 5
		# </advc.073>
		self.activeExportCol = 6
		self.activeImportCol = 7
		self.payingCol = 8
		
		self.resIconGrid.setHeader( self.leaderCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_LEADER", ()) )
		# <advc.073>
		# txt keys were TXT_KEY_FOREIGN_ADVISOR_FOR_TRADE_2, TXT_KEY_FOREIGN_ADVISOR_NOT_FOR_TRADE_2, TXT_KEY_FOREIGN_ADVISOR_FOR_TRADE_2, TXT_KEY_FOREIGN_ADVISOR_NOT_FOR_TRADE_2
		# was surplusCol
		self.resIconGrid.setHeader( self.willImportCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_WILL_IMPORT", ()) )
		# Moved up
		self.resIconGrid.setHeader( self.canPayCol, (u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar()) )
		self.resIconGrid.setTextColWidth(self.canPayCol, self.RES_GOLD_COL_WIDTH)
		# Replaced with noNeedCol below
		#self.resIconGrid.setHeader( self.usedCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_WILL_NOT_IMPORT", ()) )
		# was willTradeCol
		self.resIconGrid.setHeader( self.willExportCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_WILL_EXPORT", ()) )
		# was wontTradeCol
		self.resIconGrid.setHeader( self.wontExportCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_WILL_NOT_EXPORT", ()) )
		# New column that takes over most of the wontTradeCol resources
		self.resIconGrid.setHeader( self.noNeedCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_NO_NEED", ()) )
		# </advc.073>
		
		if (self.RES_SHOW_ACTIVE_TRADE):
			# advc.073: was TXT_KEY_FOREIGN_ADVISOR_EXPORT. Now all the headings take the perspective of the foreign leader (except noNeed)
			self.resIconGrid.setHeader( self.activeExportCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_IMPORTING", ()) )
			# advc.073: was TXT_KEY_FOREIGN_ADVISOR_IMPORT
			self.resIconGrid.setHeader( self.activeImportCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_EXPORTING", ()) )
			self.resIconGrid.setHeader( self.payingCol, (u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar()) )
			self.resIconGrid.setTextColWidth(self.payingCol, self.RES_GOLD_COL_WIDTH)

		if (self.RES_SHOW_IMPORT_EXPORT_HEADER):
			self.resIconGrid.createColumnGroup(" ", 1)
			#self.resIconGrid.createColumnGroup(localText.getText("TXT_KEY_FOREIGN_ADVISOR_EXPORT", ()), 2)
			# advc.073: Replacing the above. (I want the groups, but not the headings.)
			self.resIconGrid.createColumnGroup(" ", 2)
			#self.resIconGrid.createColumnGroup(localText.getText("TXT_KEY_FOREIGN_ADVISOR_IMPORT", ()), 3)
			# advc.073: Replacing the above
			self.resIconGrid.createColumnGroup(" ", 3)
			if (self.RES_SHOW_ACTIVE_TRADE):
				#self.resIconGrid.createColumnGroup(localText.getText("TXT_KEY_FOREIGN_ADVISOR_ACTIVE", ()), 3)
				# advc.073: Replacing the above
				self.resIconGrid.createColumnGroup(" ", 3)
		
		gridWidth = self.resIconGrid.getPrefferedWidth()
		gridHeight = self.resIconGrid.getPrefferedHeight()
		self.RES_LEFT_RIGHT_SPACE = (self.W_SCREEN - gridWidth - 20) / 2
		self.RES_TOP_BOTTOM_SPACE = (self.H_SCREEN - gridHeight - self.RES_SURPLUS_HEIGHT - self.RES_PANEL_SPACE - self.TITLE_HEIGHT - 20) / 2
		gridX = self.RES_LEFT_RIGHT_SPACE + 10
		gridY = self.RES_TOP_BOTTOM_SPACE + self.RES_SURPLUS_HEIGHT + self.RES_PANEL_SPACE + self.TITLE_HEIGHT + 10
		
		self.resIconGrid.setPosition(gridX, gridY)
		self.resIconGrid.setSize(gridWidth, gridHeight)
		# self.RES_LEFT_RIGHT_SPACE = self.MIN_LEFT_RIGHT_SPACE
		# self.RES_TOP_BOTTOM_SPACE = self.MIN_TOP_BOTTOM_SPACE



	def calculateSurplusPanelLayout(self):
		self.SURPLUS_X = self.RES_LEFT_RIGHT_SPACE
		self.SURPLUS_Y = self.RES_TOP_BOTTOM_SPACE
		self.SURPLUS_WIDTH = self.W_SCREEN - 2 * self.RES_LEFT_RIGHT_SPACE

		self.SURPLUS_ICONS_X = self.SURPLUS_X + 10
		if (self.RES_SHOW_SURPLUS_AMOUNT_ON_TOP):
			self.SURPLUS_TABLE_X = self.SURPLUS_ICONS_X + 15
			# advc.073: Take RESOURCE_ICON_SIZE times 2 (two rows now)
			SURPLUS_VERTICAL_SPACING = (self.RES_SURPLUS_HEIGHT - 2 * self.RESOURCE_ICON_SIZE - self.TITLE_HEIGHT) / 2
			self.SURPLUS_ICONS_Y = self.SURPLUS_Y + SURPLUS_VERTICAL_SPACING + self.TITLE_HEIGHT
			self.SURPLUS_TABLE_Y = self.SURPLUS_ICONS_Y + (self.RESOURCE_ICON_SIZE - self.TABLE_CONTROL_HEIGHT) / 2 + 8
		else:
			self.SURPLUS_TABLE_X = self.SURPLUS_ICONS_X + 5
			SURPLUS_VERTICAL_SPACING = ( self.RES_SURPLUS_HEIGHT - self.RESOURCE_ICON_SIZE - self.TABLE_CONTROL_HEIGHT - self.TITLE_HEIGHT ) / 2 + 3
			self.SURPLUS_ICONS_Y = self.SURPLUS_Y + SURPLUS_VERTICAL_SPACING + self.TITLE_HEIGHT
			self.SURPLUS_TABLE_Y = self.SURPLUS_ICONS_Y + self.RESOURCE_ICON_SIZE

		self.SURPLUS_CIRCLE_X_START = self.SURPLUS_TABLE_X + 4
		# advc.073: Renamed from SURPLUS_CIRCLE_Y
		self.SURPLUS_CIRCLE_Y_START = self.SURPLUS_TABLE_Y + 5



	def drawResourceDeals(self, bInitial):
		screen = self.getScreen()

		activePlayer = gc.getPlayer(self.iActiveLeader)
		self.initTradeTable()
		
		# Find all the surplus resources
		tradeData = TradeData()
		tradeData.ItemType = TradeableItems.TRADE_RESOURCES
		listSurplus = []
		listNonSurplus = [] # advc.073
		
		for iLoopBonus in range(gc.getNumBonusInfos()):
			bSurplus = False # advc.073
			tradeData.iData = iLoopBonus
			for iLoopPlayer in range(gc.getMAX_PLAYERS()):
				currentPlayer = gc.getPlayer(iLoopPlayer)
				if not currentPlayer.isAlive() or currentPlayer.isBarbarian() or currentPlayer.isMinorCiv() or not gc.getTeam(currentPlayer.getTeam()).isHasMet(activePlayer.getTeam()) or iLoopPlayer == self.iActiveLeader or not activePlayer.canTradeItem(iLoopPlayer, tradeData, False):
					continue # advc
				if activePlayer.getNumTradeableBonuses(iLoopBonus) > 1:
					listSurplus.append(iLoopBonus)
					bSurplus = True # advc.073
					break
			# <advc.073>
			if not bSurplus and activePlayer.getNumTradeableBonuses(iLoopBonus) > 0:
				listNonSurplus.append(iLoopBonus)
			# </advc.073>
		self.calculateSurplusPanelLayout()
		
		# Assemble the surplus panel
		self.mainAvailablePanel = self.getNextWidgetName()
		# <!-- custom: save some space, don't use a header, anyways etc. -->
		# screen.addPanel( self.mainAvailablePanel, localText.getText("TXT_KEY_FOREIGN_ADVISOR_SURPLUS_RESOURCES", ()), "", False, False, self.SURPLUS_X, self.SURPLUS_Y, self.SURPLUS_WIDTH, self.RES_SURPLUS_HEIGHT, PanelStyles.PANEL_STYLE_MAIN )
		screen.addPanel( self.mainAvailablePanel, "", "", False, False, self.SURPLUS_X, self.SURPLUS_Y, self.SURPLUS_WIDTH, self.RES_SURPLUS_HEIGHT, PanelStyles.PANEL_STYLE_MAIN )
		
		self.availableMultiList = self.getNextWidgetName()
		# advc.073: I don't know how to make the surplus amounts wrap into another row, so the surplus resources will all have to be placed in the top row, even if there isn't enough space.
		maxIconsPerRow = max(len(listSurplus), self.SURPLUS_WIDTH // self.RESOURCE_ICON_SIZE)
		# advc.073: Width based on max of listSurplus and listNonSurplus; height times 2.
		screen.addMultiListControlGFC( self.availableMultiList, "", self.SURPLUS_ICONS_X, self.SURPLUS_ICONS_Y, self.RESOURCE_ICON_SIZE * min(maxIconsPerRow,len(listSurplus)+len(listNonSurplus)), 2 * self.RESOURCE_ICON_SIZE, 1, 32, 32, TableStyles.TABLE_STYLE_EMPTY )

		self.availableTable = self.getNextWidgetName()
		# add the circles behind the amounts
		if (self.RES_SHOW_SURPLUS_AMOUNT_ON_TOP):
			for iIndex in range(len(listSurplus)):
				# advc.073: SURPLUS_CIRCLE_Y replaced with SURPLUS_CIRCLE_Y_START plus an offset.
				circleY = self.SURPLUS_CIRCLE_Y_START
				# Can't do the same for the amounts, so don't do this after all:
				#if iIndex > maxIconsPerRow:
				#	circleY += self.RESOURCE_ICON_SIZE
				screen.addDDSGFC( self.availableTable + "Circle" + str(iIndex), ArtFileMgr.getInterfaceArtInfo("WHITE_CIRCLE_40").getPath(), self.SURPLUS_CIRCLE_X_START + iIndex * self.RESOURCE_ICON_SIZE, circleY, 16, 16, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		
		# add the table showing the amounts
		screen.addTableControlGFC( self.availableTable, len(listSurplus), self.SURPLUS_TABLE_X, self.SURPLUS_TABLE_Y, len(listSurplus) * self.RESOURCE_ICON_SIZE, self.TABLE_CONTROL_HEIGHT, False, False, 16, 16, TableStyles.TABLE_STYLE_EMPTY )
		
		# Add the bonuses to the surplus panel with their amount
		for iIndex in range(len(listSurplus)):
			# screen.addCheckBoxGFCAt (self.mainAvailablePanel, "Foo" + str(iIndex), gc.getBonusInfo (listSurplus[iIndex]).getButton(), ArtFileMgr.getInterfaceArtInfo ("BUTTON_HILITE_SQUARE").getPath(), self.X_GLANCE_OFFSET + (self.RESOURCE_ICON_SIZE * iIndex), 10, 32, 32, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, listSurplus[iIndex], -1, ButtonStyles.BUTTON_STYLE_LABEL, False)
			# advc.073: Pass the active player to the BULL widget in order to signal that all takers are supposed to be listed
			screen.appendMultiListButton( self.availableMultiList, gc.getBonusInfo(listSurplus[iIndex]).getButton(), 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS_TRADE, listSurplus[iIndex], self.iActiveLeader, False )
			screen.setTableColumnHeader( self.availableTable, iIndex, u"", self.RESOURCE_ICON_SIZE )
			
			amount = activePlayer.getNumTradeableBonuses(listSurplus[iIndex])
			if (self.RES_SHOW_EXTRA_AMOUNT):
				amount = amount - 1
			
			if (self.RES_SHOW_SURPLUS_AMOUNT_ON_TOP):
				amountStr = u"<font=2>" + localText.changeTextColor(str(amount), gc.getInfoTypeForString("COLOR_YELLOW")) + "</font>"
			else:
				amountStr = u"<font=3>" + str(amount) + "</font>"
			screen.setTableText( self.availableTable, iIndex, 0, amountStr, "", WidgetTypes.WIDGET_GENERAL, -1, -1, 0 )
		# <advc.073>
		for iIndex in range(len(listNonSurplus)):
			screen.appendMultiListButton(self.availableMultiList, gc.getBonusInfo(listNonSurplus[iIndex]).getButton(), 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS_TRADE, listNonSurplus[iIndex], self.iActiveLeader, False)
			screen.setTableColumnHeader(self.availableTable, iIndex, u"", self.RESOURCE_ICON_SIZE)
		# </advc.073>
		
		# # Assemble the panel that shows the trade table
		# <!-- custom: beautify, trim or adjust the edges to remove empty space or overfilling blue panel or/and such anyways etc. -->
		# iExtraY = 0
		# iExtraHeight = 0
		iExtraY = - 20
		iExtraHeight = -12
		self.TABLE_PANEL_X = self.RES_LEFT_RIGHT_SPACE
		self.TABLE_PANEL_Y = self.SURPLUS_Y + self.RES_SURPLUS_HEIGHT + self.RES_PANEL_SPACE + iExtraY
		self.TABLE_PANEL_WIDTH = self.W_SCREEN - 2 * self.RES_LEFT_RIGHT_SPACE
		self.TABLE_PANEL_HEIGHT = self.H_SCREEN - self.TABLE_PANEL_Y - self.RES_TOP_BOTTOM_SPACE + iExtraHeight
		
		self.tradePanel = self.getNextWidgetName()
		# <!-- custom: save some space, don't use a header, anyways etc. -->
		# screen.addPanel( self.tradePanel, localText.getText("TXT_KEY_FOREIGN_ADVISOR_TRADE_TABLE", ()), "", True, True, self.TABLE_PANEL_X, self.TABLE_PANEL_Y, self.TABLE_PANEL_WIDTH, self.TABLE_PANEL_HEIGHT, PanelStyles.PANEL_STYLE_MAIN )
		screen.addPanel( self.tradePanel, "", "", True, True, self.TABLE_PANEL_X, self.TABLE_PANEL_Y, self.TABLE_PANEL_WIDTH, self.TABLE_PANEL_HEIGHT, PanelStyles.PANEL_STYLE_MAIN )

		self.resIconGrid.createGrid()
		
		# find all players that need to be listed 
		self.resIconGrid.clearData()
		tradeData = TradeData()
		tradeData.ItemType = TradeableItems.TRADE_RESOURCES
		currentRow = 0
		
		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			currentPlayer = gc.getPlayer(iLoopPlayer)
			if ( currentPlayer.isAlive() and not currentPlayer.isBarbarian() and not currentPlayer.isMinorCiv() and gc.getTeam(currentPlayer.getTeam()).isHasMet(activePlayer.getTeam()) and iLoopPlayer != self.iActiveLeader ):
				message = ""
				if ( not activePlayer.canTradeNetworkWith(iLoopPlayer) ):
					message = localText.getText("TXT_KEY_FOREIGN_ADVISOR_NOT_CONNECTED", ())
				
				self.resIconGrid.appendRow(currentPlayer.getName(), message)
				self.resIconGrid.addIcon( currentRow, self.leaderCol
										, gc.getLeaderHeadInfo(currentPlayer.getLeaderType()).getButton()
										, 64, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader )
				
				# gold
				# advc.036:
				bWillTalk = currentPlayer.AI_isWillingToTalk(self.iActiveLeader)
				if (gc.getTeam(activePlayer.getTeam()).isGoldTrading() or gc.getTeam(currentPlayer.getTeam()).isGoldTrading()) and bWillTalk:
					# <!-- custom: looks like gc.getPlayer(iLoopPlayer) could be optimized with the cached currentPlayer variable so did as such anyways etc. -->
					sAmount = str(currentPlayer.AI_maxGoldPerTurnTrade(self.iActiveLeader))
					self.resIconGrid.setText(currentRow, self.canPayCol, sAmount)
				
				# bonuses
				importFromPlayer = [] # advc.036
				for iLoopBonus in range(gc.getNumBonusInfos()):
					tradeData.iData = iLoopBonus
					if (activePlayer.canTradeItem(iLoopPlayer, tradeData, False)):
						if (activePlayer.canTradeItem(iLoopPlayer, tradeData, (not currentPlayer.isHuman()))): # surplus
							importFromPlayer.append(iLoopBonus) # advc.036
						else: # used
							# advc.073: Use the BONUS_TRADE widget from BULL so that the DLL can tell that tile yields shouldn't be shown
							#self.resIconGrid.addIcon( currentRow, self.usedCol, gc.getBonusInfo(iLoopBonus).getButton(), 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS_TRADE, iLoopBonus, iLoopPlayer )
							pass # Or rather: Disable this column
					if (currentPlayer.canTradeItem(self.iActiveLeader, tradeData, False)):
						#if (currentPlayer.canTradeItem(self.iActiveLeader, tradeData, (not currentPlayer.isHuman()))): # will trade
						# <advc.073> Replacing the above: separate column now for must-be-joking resources
						iDenial = currentPlayer.getTradeDenial(self.iActiveLeader, tradeData)
						# Human isn't going to deny, but I still want to populate the noNeedCol and wontExportCol.
						if iDenial == DenialTypes.NO_DENIAL and currentPlayer.isHuman():
							if activePlayer.getNumAvailableBonuses(iLoopBonus) > 0 and activePlayer.AI_corporationBonusVal(iLoopBonus) <= 0:
								iDenial = DenialTypes.DENIAL_JOKING
							elif currentPlayer.getNumAvailableBonuses(iLoopBonus) < 2 or currentPlayer.AI_corporationBonusVal(iLoopBonus) > 0:
								iDenial = DenialTypes.DENIAL_NO_GAIN
						if iDenial != DenialTypes.DENIAL_JOKING:
							if iDenial == DenialTypes.NO_DENIAL and bWillTalk:
								# Use the BONUS_TRADE widget from BULL everywhere (also needed for advc.036). Was willTradeCol.
								self.resIconGrid.addIcon( currentRow, self.willExportCol, gc.getBonusInfo(iLoopBonus).getButton(), 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS_TRADE, iLoopBonus, iLoopPlayer )
							else: # won't trade
								# advc.073: Changed so that WIDGET_PEDIA_JUMP_TO_BONUS_TRADE works w/o BugDll. And was wontTradeCol.
								self.resIconGrid.addIcon( currentRow, self.wontExportCol, gc.getBonusInfo(iLoopBonus).getButton(), 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS_TRADE, iLoopBonus, iLoopPlayer )
						else: # New column for resources that the active player doesn't need
							self.resIconGrid.addIcon(currentRow, self.noNeedCol, gc.getBonusInfo(iLoopBonus).getButton(), 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS_TRADE, iLoopBonus, iLoopPlayer)
						# </advc.073>
				# <advc.036> Sorting both listSurplus and importSurplusFromPlayer by the number of copies owned by the active player would be even better, but would take me too long to write in Python.
				importSurplusFromPlayer = []
				rest = []
				for iBonus in importFromPlayer:
					if iBonus in listSurplus:
						importSurplusFromPlayer.append(iBonus)
					else:
						rest.append(iBonus)
				importSorted = importSurplusFromPlayer + rest
				for iLoopBonus in importSorted:
					# Cut and pasted from the "bonuses" loop above, but using the BONUS_TRADE widget from BULL.
					# advc.073: Was surplusCol; and add 1000 to iLoopBonus in order to signal that we're in the import column (hack).
					self.resIconGrid.addIcon( currentRow, self.willImportCol, gc.getBonusInfo(iLoopBonus).getButton(), 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS_TRADE, iLoopBonus+1000, iLoopPlayer )
				# </advc.036>
				if (self.RES_SHOW_ACTIVE_TRADE):
					amount = 0
					for iLoopDeal in range(gc.getGame().getIndexAfterLastDeal()):
						deal = gc.getGame().getDeal(iLoopDeal)
						# BUG - Kill Deal - start
						if not deal.isNone():
							if ( deal.getFirstPlayer() == iLoopPlayer and deal.getSecondPlayer() == self.iActiveLeader):
								for iLoopTradeItem in range(deal.getLengthFirstTrades()):
									tradeData2 = deal.getFirstTrade(iLoopTradeItem)
									if (tradeData2.ItemType == TradeableItems.TRADE_GOLD_PER_TURN):
										amount += tradeData2.iData
									if (tradeData2.ItemType == TradeableItems.TRADE_RESOURCES):
										# advc.073: DEAL_KILL widget enabled; advc.085: iData2 set to -1
										self.resIconGrid.addIcon( currentRow, self.activeImportCol, gc.getBonusInfo(tradeData2.iData).getButton(), 64, WidgetTypes.WIDGET_DEAL_KILL, iLoopDeal, -1)
								for iLoopTradeItem in range(deal.getLengthSecondTrades()):
									tradeData2 = deal.getSecondTrade(iLoopTradeItem)
									if (tradeData2.ItemType == TradeableItems.TRADE_GOLD_PER_TURN):
										amount -= tradeData2.iData
									if (tradeData2.ItemType == TradeableItems.TRADE_RESOURCES):
										# advc.073: DEAL_KILL widget enabled; advc.085: iData2 set to -1
										self.resIconGrid.addIcon( currentRow, self.activeExportCol, gc.getBonusInfo(tradeData2.iData).getButton(), 64, WidgetTypes.WIDGET_DEAL_KILL, iLoopDeal, -1)
							
							if ( deal.getSecondPlayer() == iLoopPlayer and deal.getFirstPlayer() == self.iActiveLeader ):
								for iLoopTradeItem in range(deal.getLengthFirstTrades()):
									tradeData2 = deal.getFirstTrade(iLoopTradeItem)
									if (tradeData2.ItemType == TradeableItems.TRADE_GOLD_PER_TURN):
										amount -= tradeData2.iData
									if (tradeData2.ItemType == TradeableItems.TRADE_RESOURCES):
										# advc.073: DEAL_KILL widget enabled; advc.085: iData2 set to -1
										self.resIconGrid.addIcon( currentRow, self.activeExportCol, gc.getBonusInfo(tradeData2.iData).getButton(), 64, WidgetTypes.WIDGET_DEAL_KILL, iLoopDeal, -1)
								for iLoopTradeItem in range(deal.getLengthSecondTrades()):
									tradeData2 = deal.getSecondTrade(iLoopTradeItem)
									if (tradeData2.ItemType == TradeableItems.TRADE_GOLD_PER_TURN):
										amount += tradeData2.iData
									if (tradeData2.ItemType == TradeableItems.TRADE_RESOURCES):
										# advc.073: DEAL_KILL widget enabled; advc.085: iData2 set to -1
										self.resIconGrid.addIcon( currentRow, self.activeImportCol, gc.getBonusInfo(tradeData2.iData).getButton(), 64, WidgetTypes.WIDGET_DEAL_KILL, iLoopDeal, -1)
						# BUG - Kill Deal - end
					if (amount != 0):
						self.resIconGrid.setText(currentRow, self.payingCol, str(amount))
				currentRow += 1
		self.resIconGrid.refresh()
	
	
	def scrollTradeTableUp(self):
		if (self.iScreen == self.SCREEN_DICT["BONUS"]):
			self.resIconGrid.scrollUp()
		elif (self.iScreen == self.SCREEN_DICT["TECH"]):
			self.techIconGrid.scrollUp()
		# <advc.ctr>
		elif (self.iScreen == self.SCREEN_DICT["CITIES"]):
			self.cityIconGrid.scrollUp()
		# </advc.ctr>

	def scrollTradeTableDown(self):
		if (self.iScreen == self.SCREEN_DICT["BONUS"]):
			self.resIconGrid.scrollDown()
		elif (self.iScreen == self.SCREEN_DICT["TECH"]):
			self.techIconGrid.scrollDown()
		# <advc.ctr>
		elif (self.iScreen == self.SCREEN_DICT["CITIES"]):
			self.cityIconGrid.scrollDown()
		# </advc.ctr>
				
	def drawTechDeals(self, bInitial):
		screen = self.getScreen()
		activePlayer = gc.getPlayer(self.iActiveLeader)
		iActiveTeam = activePlayer.getTeam()
		activeTeam = gc.getTeam(iActiveTeam)

		self.initTechTable()

		# Assemble the panel
		# <!-- custom: add extra width tweak to remove the yellow side edges, and extra height tweak to remove distracting top bright band plus have more room on bottom side's row as well, with gemini 3 pro's help thanks anyways etc. -->
		# iExtraWidth = 0
		iExtraWidth = 4
		TECH_PANEL_X = self.TECH_LEFT_RIGHT_SPACE - iExtraWidth
		TECH_PANEL_WIDTH = self.W_SCREEN - 2 * self.TECH_LEFT_RIGHT_SPACE + (2 * iExtraWidth)
		# iExtraHeight = 0
		iExtraHeight = 4
		TECH_PANEL_Y = self.TECH_TOP_BOTTOM_SPACE - iExtraHeight
		TECH_PANEL_HEIGHT = self.H_SCREEN - 2 * self.TECH_TOP_BOTTOM_SPACE + (2 * iExtraHeight)

		self.tradePanel = self.getNextWidgetName()
		screen.addPanel( self.tradePanel, "", "", True, True, TECH_PANEL_X, TECH_PANEL_Y, TECH_PANEL_WIDTH, TECH_PANEL_HEIGHT, PanelStyles.PANEL_STYLE_MAIN )

		self.techIconGrid.createGrid()

		self.techIconGrid.clearData()
		tradeData = TradeData()
		tradeData.ItemType = TradeableItems.TRADE_TECHNOLOGIES
		currentRow = 0

		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			currentPlayer = gc.getPlayer(iLoopPlayer)
			iLoopTeam = currentPlayer.getTeam()
			currentTeam = gc.getTeam(iLoopTeam)

			if ( currentPlayer.isAlive() and not currentPlayer.isBarbarian() and not currentPlayer.isMinorCiv() and gc.getTeam(currentPlayer.getTeam()).isHasMet(activePlayer.getTeam()) and iLoopPlayer != self.iActiveLeader ):
				message = ""
				#if ( not gc.getTeam(activePlayer.getTeam()).isTechTrading() and not gc.getTeam(currentPlayer.getTeam()).isTechTrading() ):
				# advc.120d: Make sure that Tech tab is consistent with Espionage screen
				if not activePlayer.canSeeTech(iLoopPlayer):
					message = localText.getText("TXT_KEY_FOREIGN_ADVISOR_NO_TECH_TRADING", ())
				self.techIconGrid.appendRow(currentPlayer.getName(), message)
				self.techIconGrid.addIcon( currentRow, iTechColLeader, gc.getLeaderHeadInfo(currentPlayer.getLeaderType()).getButton(), 64, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader )

				# BUG - AI status - start
				zsStatus = ""
				if not DiplomacyUtil.isWillingToTalk(currentPlayer, activePlayer):
					zsStatus += u"!"

				if (currentTeam.isAtWar(iActiveTeam)):
					zsStatus += self.WAR_ICON
				elif (currentTeam.isForcePeace(iActiveTeam)):
					zsStatus += self.PEACE_ICON

				self.techIconGrid.setText(currentRow, iTechColStatus, zsStatus)
				# BUG - AI status - end
				# advc.036:
				bWillTalk = currentPlayer.AI_isWillingToTalk(self.iActiveLeader)
				if (gc.getTeam(activePlayer.getTeam()).isGoldTrading() or gc.getTeam(currentPlayer.getTeam()).isGoldTrading()) and bWillTalk:
					# <!-- custom: looks like gc.getPlayer(iLoopPlayer) could be optimized with the cached currentPlayer variable so did as such anyways etc. -->
					sAmount = str(currentPlayer.AI_maxGoldTrade(self.iActiveLeader))
					self.techIconGrid.setText(currentRow, iTechColGold, sAmount)

				#if (gc.getTeam(activePlayer.getTeam()).isTechTrading() or gc.getTeam(currentPlayer.getTeam()).isTechTrading() ):
				if activePlayer.canSeeTech(iLoopPlayer): # advc.120d
					for iLoopTech in range(gc.getNumTechInfos()):
						tradeData.iData = iLoopTech
						if (activePlayer.canTradeItem(iLoopPlayer, tradeData, False) and activePlayer.getTradeDenial(iLoopPlayer, tradeData) == DenialTypes.NO_DENIAL): # wants
							self.techIconGrid.addIcon( currentRow, iTechColWants, gc.getTechInfo(iLoopTech).getButton(), 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iLoopTech )
						elif (gc.getTeam(activePlayer.getTeam()).isHasTech(iLoopTech) and currentPlayer.canResearch(iLoopTech, False)):
							self.techIconGrid.addIcon( currentRow, iTechColCantYou, gc.getTechInfo(iLoopTech).getButton(), 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iLoopTech )
						elif currentPlayer.canResearch(iLoopTech, False):
							self.techIconGrid.addIcon( currentRow, iTechColResearch, gc.getTechInfo(iLoopTech).getButton(), 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iLoopTech )
						if (currentPlayer.canTradeItem(self.iActiveLeader, tradeData, False)):
							if currentPlayer.getTradeDenial(self.iActiveLeader, tradeData) == DenialTypes.NO_DENIAL and bWillTalk: # will trade
								self.techIconGrid.addIcon( currentRow, iTechColWill, gc.getTechInfo(iLoopTech).getButton(), 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iLoopTech )
							else: # won't trade
								# advc.073: Changed so that WIDGET_PEDIA_JUMP_TO_TECH_TRADE works w/o BugDll
								self.techIconGrid.addIcon( currentRow, iTechColWont, gc.getTechInfo(iLoopTech).getButton(), 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH_TRADE, iLoopTech, iLoopPlayer )
						else:
							# <advc.550i> If tech trading disabled, show a hint about that only once (in row 0).
							if currentRow == 0 and gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_TECH_TRADING):
								message = gc.getGameOptionInfo(GameOptionTypes.GAMEOPTION_NO_TECH_TRADING).getDescription()
								self.techIconGrid.setText(currentRow, iTechColWill, message)
							# </advc.550i>
							if (gc.getTeam(currentPlayer.getTeam()).isHasTech(iLoopTech) and activePlayer.canResearch(iLoopTech, False)):
								self.techIconGrid.addIcon( currentRow, iTechColCantThem, gc.getTechInfo(iLoopTech).getButton(), 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iLoopTech )
				currentRow += 1
		self.techIconGrid.refresh()


	def initTechTable(self):
		screen = self.getScreen()
		
		# 1. Define the full screen
		# <!-- custom: note: this is the starting position of the grid/table, not of the blue panel anyways etc. -->
		# <!-- custom: note: for example gridX moves the grid's starting position more to the left or right (for example so we use what used to be the yellow empty space on the left (and also on the right) if needed anyways etc.) -->
		gridX = self.MIN_LEFT_RIGHT_SPACE + 10
		gridY = self.MIN_TOP_BOTTOM_SPACE + 10

		# <!-- custom: no need for the right side edge/margin in the blue panel, use this space or shrink the screen by this size if we don't need it in any other foreign advisor screen anyways etc. -->
		# gridWidth = self.W_SCREEN - self.MIN_LEFT_RIGHT_SPACE * 2 - 20
		# <!-- custom: we don't need margins in these areas, maximize space anyways etc. -->
		# <!-- custom: also widen X since we removed the yellow edges that were uneeded, fill this space with our grid as we want to use it not leave it blue with our grid ending before it, anyways etc. -->
		gridWidth = self.W_SCREEN + 10
		# <!-- custom: trim bottom part of the grid else it overfills below the bottom end of the blue panel, which is not what we need nor want but anyways etc. -->
		# gridHeight = self.H_SCREEN - self.MIN_TOP_BOTTOM_SPACE * 2 - 20
		gridHeight = self.H_SCREEN - self.MIN_TOP_BOTTOM_SPACE * 2

		# 2. Setup the columns
		willTradeColumnType = IconGrid_BUG.GRID_MULTI_LIST_COLUMN
		# <advc.550i> Make the will-trade column a text column so that the no-tech-trading hint can be placed there
		if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_TECH_TRADING):
			willTradeColumnType = IconGrid_BUG.GRID_TEXT_COLUMN
		# </advc.550i>

		columns = ( IconGrid_BUG.GRID_ICON_COLUMN,
					IconGrid_BUG.GRID_TEXT_COLUMN,
					IconGrid_BUG.GRID_MULTI_LIST_COLUMN,
					IconGrid_BUG.GRID_MULTI_LIST_COLUMN,
					IconGrid_BUG.GRID_MULTI_LIST_COLUMN,
					IconGrid_BUG.GRID_TEXT_COLUMN,
					willTradeColumnType,
					IconGrid_BUG.GRID_MULTI_LIST_COLUMN,
					IconGrid_BUG.GRID_MULTI_LIST_COLUMN)

		self.techIconGridName = self.getNextWidgetName()
		self.techIconGrid = IconGrid_BUG.IconGrid_BUG( self.techIconGridName, screen, gridX, gridY, gridWidth, gridHeight, columns, self.TECH_USE_SMALL_ICONS, self.SHOW_LEADER_NAMES, self.SHOW_ROW_BORDERS )

		self.techIconGrid.setGroupBorder(self.GROUP_BORDER)
		self.techIconGrid.setGroupLabelOffset(self.GROUP_LABEL_OFFSET)
		self.techIconGrid.setMinColumnSpace(self.MIN_COLUMN_SPACE)
		self.techIconGrid.setMinRowSpace(self.MIN_ROW_SPACE)

		# 3. Set widths for the specific text columns (Status, Gold)
		# Note: IconGrid_BUG does NOT allow setting widths for Icon columns (Wants, Can Research, etc). 
		# It calculates them automatically by dividing the remaining space evenly.
		# self.techIconGrid.setHeader( iTechColLeader, localText.getText("TXT_KEY_FOREIGN_ADVISOR_LEADER", ()) )
		# self.techIconGrid.setHeader( iTechColStatus, "" )
		self.techIconGrid.setTextColWidth( iTechColStatus, self.TECH_STATUS_COL_WIDTH )
		self.techIconGrid.setHeader( iTechColWants, localText.getText("TXT_KEY_FOREIGN_ADVISOR_WANTS", ()) )
		# advc.004g: was TXT_KEY_FOREIGN_ADVISOR_CANT_TRADE
		self.techIconGrid.setHeader( iTechColCantYou, localText.getText("TXT_KEY_FOREIGN_ADVISOR_CANT_RECEIVE", ()) )
		self.techIconGrid.setHeader( iTechColResearch, localText.getText("TXT_KEY_FOREIGN_ADVISOR_CAN_RESEARCH", ()) )
		self.techIconGrid.setHeader( iTechColGold, (u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar()) )
		self.techIconGrid.setTextColWidth( iTechColGold, self.TECH_GOLD_COL_WIDTH )

		self.techIconGrid.setHeader( iTechColWill, localText.getText("TXT_KEY_FOREIGN_ADVISOR_FOR_TRADE_2", ()) )
		# <advc.550i>
		if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_TECH_TRADING):
			self.techIconGrid.setTextColWidth(iTechColWill, 2 * self.TECH_GOLD_COL_WIDTH) # </advc.550i>

		self.techIconGrid.setHeader( iTechColWont, localText.getText("TXT_KEY_FOREIGN_ADVISOR_NOT_FOR_TRADE_2", ()) )
		self.techIconGrid.setHeader( iTechColCantThem, localText.getText("TXT_KEY_FOREIGN_ADVISOR_CANT_TRADE", ()) )

		# <!-- custom: fit more information in each row so we don't have to scroll to see extra techs. Change with the help of gemini 3 pro anyways etc. -->
		# Based on your screenshots (specifically Civ4ScreenShot0084.jpg) and the code provided, the issue is not the column width variables (TECH_STATUS_COL_WIDTH).
		# The problem is at the very end of the initTechTable function. The code calculates the "Preferred Width" (the minimum width required to hold the icons) and then shrinks the table to fit that minimum size, centering it in your large window. This ignores the full screen width you successfully set up earlier.
		# You need to replace the end of that function to stop it from shrinking and to manually force the columns to share the available space.
		# We removed the lines that called getPrefferedWidth() and resized the grid variables.
		# This ensures the grid stays at the full size we calculated at the top.
		# IconGrid_BUG will automatically spread the columns to fill this space.
		# gridWidth = self.techIconGrid.getPrefferedWidth()
		# gridHeight = self.techIconGrid.getPrefferedHeight()
		# self.TECH_LEFT_RIGHT_SPACE = (self.W_SCREEN - gridWidth - 20) / 2
		# self.TECH_TOP_BOTTOM_SPACE = (self.H_SCREEN - gridHeight - 20) / 2
		# gridX = self.TECH_LEFT_RIGHT_SPACE + 10
		# gridY = self.TECH_TOP_BOTTOM_SPACE + 10
		#
		# self.techIconGrid.setPosition(gridX, gridY)
		# self.techIconGrid.setSize(gridWidth, gridHeight)

		# --- FIX: Define these variables so drawTechDeals doesn't crash ---
		# We set them to the minimum margins so the panel uses the full available space
		self.TECH_LEFT_RIGHT_SPACE = self.MIN_LEFT_RIGHT_SPACE
		self.TECH_TOP_BOTTOM_SPACE = self.MIN_TOP_BOTTOM_SPACE

	# <advc.ctr>
	def initCityTable(self): # Based on initTechTable
		screen = self.getScreen()

		# GRID_ICON for the leader head, then text for the war/peace icon and 4x multi-text for the four city columns.
		columns = (IconGrid_BUG.GRID_ICON_COLUMN, IconGrid_BUG.GRID_TEXT_COLUMN, IconGrid_BUG.GRID_MULTI_TEXT_COLUMN, IconGrid_BUG.GRID_MULTI_TEXT_COLUMN,IconGrid_BUG.GRID_MULTI_TEXT_COLUMN, IconGrid_BUG.GRID_MULTI_TEXT_COLUMN)

		gridWidth = self.W_SCREEN - self.MIN_LEFT_RIGHT_SPACE * 2 - 20
		gridHeight = self.H_SCREEN - self.MIN_TOP_BOTTOM_SPACE * 2 - 20
		iconGrid = IconGrid_BUG.IconGrid_BUG(self.getNextWidgetName(), screen, self.MIN_LEFT_RIGHT_SPACE + 10, self.MIN_TOP_BOTTOM_SPACE + 10, gridWidth, gridHeight, columns, True, self.SHOW_LEADER_NAMES, self.SHOW_ROW_BORDERS)
		iconGrid.setGroupBorder(self.GROUP_BORDER)
		iconGrid.setGroupLabelOffset(self.GROUP_LABEL_OFFSET)
		iconGrid.setMinColumnSpace(self.MIN_COLUMN_SPACE)
		iconGrid.setMinRowSpace(self.MIN_ROW_SPACE)

		iStatusColWidth = self.TECH_STATUS_COL_WIDTH
		iconGrid.setTextColWidth(iCityColStatus, iStatusColWidth)
		iRemainingWidth = gridWidth - iStatusColWidth - 64
		iCityColWidth = iRemainingWidth // 4
		iconGrid.setTextColWidth(iCityColWants, iCityColWidth)
		iconGrid.setTextColWidth(iCityColRejects, iCityColWidth)
		iconGrid.setTextColWidth(iCityColWillCede, iCityColWidth)
		iconGrid.setTextColWidth(iCityColWontCede, iCityColWidth)

		iconGrid.setHeader(iCityColWants, localText.getText("TXT_KEY_FOREIGN_ADVISOR_WANTS", ()))
		# Don't want to color the denial headings after all
		eDenialColor = gc.getInfoTypeForString("COLOR_WHITE")
		iconGrid.setHeader(iCityColRejects, localText.getColorText("TXT_KEY_FOREIGN_ADVISOR_REJECTS", (), eDenialColor))
		iconGrid.setHeader(iCityColWillCede, localText.getText("TXT_KEY_FOREIGN_ADVISOR_WILL_CEDE", ()))
		iconGrid.setHeader(iCityColWontCede, localText.getColorText("TXT_KEY_FOREIGN_ADVISOR_WONT_CEDE", (), eDenialColor))

		gridWidth = iconGrid.getPrefferedWidth()
		gridHeight = iconGrid.getPrefferedHeight()
		LEFT_RIGHT_SPACE = (self.W_SCREEN - gridWidth - 20) / 2
		TOP_BOTTOM_SPACE = (self.H_SCREEN - gridHeight - 20) / 2

		# <!-- custom: manually adjust the grid's position and size so it better fits the screen anyways etc. -->
		# iExtraX = 0
		# iExtraWidth = 0
		iExtraX = 24
		# <!-- custom: note: empirically, it seems that reducing width to have symetrical margins than on the left side causes buttons (or is it icons? But anyways etc.) like the war declare or peace one to be too close to the leader's button. On the other hand, the right space is useless in itself, and we have no other column on the right, so it's fine if it overfills beyond the screen on the right side, as long as it helps have enough space from the leader button. Could maybe ideally fix this more properly but may be possibly very tedious and is fine enough as such i mean if i may say so left as such as long as it displays nicely on the left side but anyways etc. (comparing it to the foreign advisor's tech tab and trying to have a more or less identical left side display seems more important but anyways etc.). -->
		iExtraWidth = 10

		iconGrid.setPosition(LEFT_RIGHT_SPACE + 10 + iExtraX, TOP_BOTTOM_SPACE + 10)
		iconGrid.setSize(gridWidth + iExtraWidth, gridHeight)

		return iconGrid, LEFT_RIGHT_SPACE, TOP_BOTTOM_SPACE

	def drawCityDeals(self, bInitial): # Based on drawTechDeals
		screen = self.getScreen()
		self.eDenialColor = gc.getInfoTypeForString("COLOR_LIGHT_GREY")

		iconGrid, PANEL_X, PANEL_Y = self.initCityTable()
		PANEL_WIDTH = self.W_SCREEN - 2 * PANEL_X
		PANEL_HEIGHT = self.H_SCREEN - 2 * PANEL_Y

		# <!-- custom: manually adjust the blue panel's position and size so it better fits the screen anyways etc. -->
		# iExtraX = 0
		# iExtraY = 0
		# iExtraWidth = 0
		# iExtraHeight = 0
		iExtraX = 20
		iExtraY = -12
		iExtraWidth = -40
		iExtraHeight = 24

		screen.addPanel(self.getNextWidgetName(), "", "", True, True, PANEL_X +iExtraX, PANEL_Y +iExtraY, PANEL_WIDTH + iExtraWidth, PANEL_HEIGHT + iExtraHeight, PanelStyles.PANEL_STYLE_MAIN )

		iconGrid.createGrid()
		iconGrid.clearData()
		tradeData = TradeData()
		tradeData.ItemType = TradeableItems.TRADE_CITIES

		iActivePlayer = self.iActiveLeader
		activePlayer = gc.getPlayer(iActivePlayer)
		iActiveTeam = activePlayer.getTeam()
		currentRow = 0
		for iCurrentPlayer in range(gc.getMAX_CIV_PLAYERS()):
			currentPlayer = gc.getPlayer(iCurrentPlayer)
			currentTeam = gc.getTeam(currentPlayer.getTeam())

			if not currentPlayer.isAlive() or currentPlayer.isMinorCiv() or not currentTeam.isHasMet(iActiveTeam) or iCurrentPlayer == iActivePlayer:
				continue

			iconGrid.appendRow(currentPlayer.getName(), "")

			iconGrid.addIcon(currentRow, iCityColLeader, gc.getLeaderHeadInfo(currentPlayer.getLeaderType()).getButton(), 64, WidgetTypes.WIDGET_LEADERHEAD, iCurrentPlayer, iActivePlayer)
			# BUG - AI status - start
			szStatus = ""
			if not DiplomacyUtil.isWillingToTalk(currentPlayer, activePlayer):
				szStatus += u"!"
			if currentTeam.isAtWar(iActiveTeam):
				szStatus += self.WAR_ICON
			elif currentTeam.isForcePeace(iActiveTeam):
				szStatus += self.PEACE_ICON
			iconGrid.setText(currentRow, iCityColStatus, szStatus)
			# BUG - AI status - end
			# Precompute the contents of each cell in order to shorten the city strings as necessary
			iLiberate = iCityColWontCede + 1 # Pseudo-column for sorting
			citiesPerCol = { iCityColWants : [], iCityColRejects : [], iCityColWillCede : [], iCityColWontCede : [], iLiberate : [] }
			(city, iter) = activePlayer.firstCity(False)
			while(city):
				tradeData.iData = city.getID()
				if activePlayer.canTradeItem(iCurrentPlayer, tradeData, False):
					iCol = iCityColWants
					if activePlayer.getTradeDenial(iCurrentPlayer, tradeData) != DenialTypes.NO_DENIAL:
						iCol = iCityColRejects
					elif city.getLiberationPlayer(False) == iCurrentPlayer:
						iCol = iLiberate
					citiesPerCol[iCol].append(city)
				(city, iter) = activePlayer.nextCity(iter, False)
			(city, iter) = currentPlayer.firstCity(False)
			while(city):
				tradeData.iData = city.getID()
				if currentPlayer.canTradeItem(iActivePlayer, tradeData, False):
					iCol = iCityColWillCede
					if currentPlayer.getTradeDenial(iActivePlayer, tradeData) != DenialTypes.NO_DENIAL:
						iCol = iCityColWontCede
					citiesPerCol[iCol].append(city)
				(city, iter) = currentPlayer.nextCity(iter, False)
			for iCol in citiesPerCol:
				# Smallest population first; more likely to be traded.
				citiesPerCol[iCol].sort(None, lambda city: city.getPopulation())
			for iCol in citiesPerCol:
				bGrayOut = (iCol == iCityColRejects or iCol == iCityColWontCede)
				iCities = len(citiesPerCol[iCol])
				iAdded = 0
				for city in citiesPerCol[iCol]:
					iDisplayCol = iCol
					# Cities that the non-active player wants liberated go in the "wants" column
					if iCol == iLiberate:
						iDisplayCol = iCityColWants
					szCity = ""
					widgetType = WidgetTypes.WIDGET_CITY_TRADE
					iWhoTo = iActivePlayer
					if city.getOwner() == iActivePlayer:
						iWhoTo = iCurrentPlayer
					# Need to fold both players into a single variable
					widgetData1 = city.getOwner() + 100 * (iWhoTo + 1)
					widgetData2 = city.getID()
					if iAdded == 5 and iCities > 6:
						szCity = localText.getText("TXT_KEY_FOREIGN_ADVISOR_MORE_CITIES", (iCities - iAdded,))
						# There's still room for a boolean:
						widgetData1 = (widgetData1 + 1) * 100
					else:
						szCity = self.getCityText(city, iCol == iLiberate, bGrayOut, iCities > 3)
					iconGrid.addText(currentRow, iDisplayCol, szCity, widgetType, widgetData1, widgetData2)
					iAdded += 1
					if iAdded >= 6:
						break

			currentRow += 1

		self.cityIconGrid = iconGrid # for input handlers
		iconGrid.refresh()

	def getCityText(self, city, bLiberate, bGrayOut, bShort):
		r = city.getName()
		iCharLimit = 15
		if bShort:
			iCharLimit = 12
			if bLiberate:
				iCharLimit = 10
		if len(r) > iCharLimit:
			r = r[:iCharLimit-3] + "..."
		# Looks nicer w/o population counts
		#if not bShort:
			#r += " [" + str(city.getPopulation()) + "]"
		if bGrayOut:
			r = localText.changeTextColor(r, self.eDenialColor)
		# With a citizen icon, the population counts look even worse.
		#if not bShort:
		#	r += " " + (u"%c" % CyGame().getSymbolID(FontSymbols.CITIZEN_CHAR))
		#	r += str(city.getPopulation())
		if bLiberate:
			r += " " + (u"%c" % CyGame().getSymbolID(FontSymbols.OCCUPATION_CHAR))
		return r
	# </advc.ctr>
		
	##########################################
	### END CHANGES ENHANCED INTERFACE MOD ###
	##########################################
					
	# Handles the input for this screen...
	def handleInput (self, inputClass):
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED):
			# advc.004: Removed BugDLL call from second condition
			if inputClass.getButtonType() == WidgetTypes.WIDGET_LEADERHEAD or inputClass.getButtonType() == WidgetTypes.WIDGET_LEADERHEAD_RELATIONS:
				if (inputClass.getFlags() & MouseFlags.MOUSE_LBUTTONUP):
					self.iSelectedLeader = inputClass.getData1()
					self.drawContents(False)
					return 1
				elif (inputClass.getFlags() & MouseFlags.MOUSE_RBUTTONUP):
					if inputClass.getData1() != self.iActiveLeader:
						self.getScreen().hideScreen()
						return 1
			elif (inputClass.getFunctionName() == self.GLANCE_BUTTON):
				self.handlePlusMinusToggle()
				return 1
	############################################
	### BEGIN CHANGES ENHANCED INTERFACE MOD ###
	############################################
			elif (inputClass.getButtonType() == WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS):
#				ExoticForPrint ("FOOOOOO!!!!")
				pass
	##########################################
	### END CHANGES ENHANCED INTERFACE MOD ###
	##########################################
		
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED):
			if (inputClass.getFunctionName() + str(inputClass.getID()) == self.getWidgetName(self.DEBUG_DROPDOWN_ID)):
				print 'debug dropdown event'
				szName = self.getWidgetName(self.DEBUG_DROPDOWN_ID)
				iIndex = self.getScreen().getSelectedPullDownID(szName)
				self.iActiveLeader = self.getScreen().getPullDownData(szName, iIndex)
				self.drawContents(True)
				return 1
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CHARACTER):
			if (inputClass.getData() == int(InputTypes.KB_LSHIFT) or inputClass.getData() == int(InputTypes.KB_RSHIFT)):
				self.iShiftKeyDown = inputClass.getID()
				return 1
		
		if (self.iScreen == self.SCREEN_DICT["BONUS"]):
			return self.resIconGrid.handleInput(inputClass)
		elif (self.iScreen == self.SCREEN_DICT["TECH"]):
			return self.techIconGrid.handleInput(inputClass)
		# <advc.ctr>
		elif (self.iScreen == self.SCREEN_DICT["CITIES"]):
			return self.cityIconGrid.handleInput(inputClass)
		# </advc.ctr>
		return 0

def smallText(text):
	return u"<font=2>%s</font>" % text

def smallSymbol(symbol):
	return smallText(FontUtil.getChar(symbol))

## Unit Plot List Utilities
##
## Holds the information used to display the unit plot list
##
## Copyright (c) 2007-2009 The BUG Mod.
##
## Author: Ruff_Hi
#
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: AdvCiv-SAS does not actively maintain this third-party BUG library file.
# Edits here are limited to repo-wide consistency passes (e.g. getInfoTypeOrFail for fail-loud XML lookups). (Claude code Opus 4.7) -->

from CvPythonExtensions import *
# <!-- custom: Consolidate this dependency at the shared SASVisualUtils/SASTextScale boundary instead of retaining the retired overlapping visual-resource helper imports. (ChatGPT-5.6-Sol) -->
import SASVisualUtils as SASVisuals
from SASUtils import getInfoTypeOrFail
import MonkeyTools as mt
import BugUtil
# <!-- custom: Reuse the maintained plot list's BUG options and move-mission names in this dormant prototype. See KI#165.5. (GPT-6.2-Sol) -->
import BugCore
import UnitUtil

PleOpt = BugCore.game.PLE

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

iLeaderPromo = getInfoTypeOrFail("PROMOTION_LEADER")
#screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

# constants
(sUpdateShow, sUpdateShowIf, sUpdateHide, sUpdateNothing,) = range(4)

sBupStringBase = "BUGUnitPlotString"
cUplSize = 34
cUplSpacing = 3

# <!-- custom: Pass the snapshot whose option flags are filled before drawing. See KI#165.5. (GPT-6.2-Sol) -->
def updatePLEOptions(self):
	# Capture these for looping over the plot's units
	self.bShowWoundedIndicator = PleOpt.isShowWoundedIndicator()
	self.bShowGreatGeneralIndicator = PleOpt.isShowGreatGeneralIndicator()
	self.bShowPromotionIndicator = PleOpt.isShowPromotionIndicator()
	self.bShowUpgradeIndicator = PleOpt.isShowUpgradeIndicator()
	self.bShowMissionInfo = PleOpt.isShowMissionInfo()
	self.bShowHealthBar = PleOpt.isShowHealthBar()
	self.bHideHealthBarWhileFighting = PleOpt.isHideHealthFighting()
	self.bShowMoveBar = PleOpt.isShowMoveBar()

## Notes:
## - the vanilla BtS unit plot list has a panel for each row of icons and the units are arranged from the bottom left
## - the PLE unit plot list has no panel (drawn straight onto the screen) and counts from the top left (when in standard format)
## - the BUG unit plot list has one big panel and counts from the bottom left
##    - this means that the max'th row fills up first, then the max'th-1, etc.
## - x counts the columns across the panel, from 0 to max - 1
## - y counts the rows down the panel, from 0 to max - 1


class UnitList:
	def __init__(self, vScreen, vCols, vRows, yRes):
		self.screen = vScreen
		self.iCols = vCols
		self.iRows = vRows
		self.sBupPanel = sBupStringBase + "BackgroundPanel"

		_x = 315 - cUplSpacing
		_y = yRes - 169 - cUplSpacing + (1 - vRows) * cUplSize
		_w = vCols * cUplSize + cUplSpacing
		_h = vRows * cUplSize + cUplSpacing
		# <!-- custom: Own the screen, panel and plots here.
		# The documented grid is zero-based and fills from the bottom row. See KI#165.5. (GPT-6.2-Sol) -->
		self.screen.addPanel(self.sBupPanel, u"", u"", True, False, _x, _y, _w, _h, PanelStyles.PANEL_STYLE_EMPTY)

		self.unitPlots = []
		for i in range(vCols * vRows):
			self.unitPlots.append(UnitPlot(self.screen, self.sBupPanel, i, self._getx(i), self._gety(i)))

	def _getx(self, iIndex):
		return iIndex % self.iCols

	def _gety(self, iIndex):
		return self.iRows - 1 - iIndex // self.iCols

	def _getIndex(self, x, y):
		return (self.iRows - 1 - y) * self.iCols + x

#	def getMaxCol(self):
#		return ((self.xResolution - (iMultiListXL+iMultiListXR) - 68) / 34)
#		
#	def getMaxRow(self):
#		return ((self.yResolution - 160) / PleOpt.getVerticalSpacing()) 
#		
#	def getRow(self, i):
#		return i / self.getMaxCol()

#	def getCol(self, i):
#		return i % self.getMaxCol()
#		
#	def getX(self, nCol):
#		return 315 + (nCol * PleOpt.getHoriztonalSpacing())
#		
#	def getY(self, nRow):
#		return self.yResolution - 169 - (nRow * PleOpt.getVerticalSpacing())
#		
#	def getI(self, nRow, nCol):
#		return ( nRow * self.getMaxCol() ) + ( nCol % self.getMaxCol() )

## - xPixel is the number of horizontal pixels from the top left of the BUG unit plot list panel
## - yPixel is the number of vertically pixels from the top left of the BUG unit plot list panel

class UnitPlot:
	# <!-- custom: Use the supplied screen and each axis's own pixel conversion when creating the promotion frame. See KI#165.5. (GPT-6.2-Sol) -->
	def __init__(self, screen, vBupPanel, iIndex, x, y):
		self.screen = screen
		self.sBupString = sBupStringBase + str(iIndex)
		self.reset()
		xPixel = self._getxPixel(x)
		yPixel = self._getyPixel(y)

		# add promo frame
		self.screen.addDDSGFCAt(self._getPromoString(), vBupPanel, SASVisuals.InterfaceArt.OVERLAY_PROMOTION_FRAME, xPixel + 2, yPixel + 2, 32, 32, WidgetTypes.WIDGET_PLOT_LIST, iIndex, -1, False )
		self.screen.hide(self._getPromoString())

	def _getxPixel(self, x):
		return x * cUplSize + cUplSpacing

	def _getyPixel(self, y):
		return y * cUplSize + cUplSpacing

#		_updatePromo(_getPromoString(), None, None, sUpdateNew)
#cUplSize = 34
#cUplSpacing = 3

#				szStringPromoFrame = szString + "PromoFrame"

#		for i in range( self.iMaxPlotListIcons ):
#			szString = self.PLOT_LIST_BUTTON_NAME + str(i)
#			screen.hide( szString )
#			screen.hide( szString + "Icon" )
#			screen.hide( szString + "HealthBar" )
#			screen.hide( szString + "MoveBar" )
#			screen.hide( szString + "PromoFrame" )
#			screen.hide( szString + "ActionIcon" )
#			screen.hide( szString + "Upgrade" )

	# <!-- custom: Keep both snapshots on the plot and call its own promotion methods.
	# An empty slot has no unit snapshot. See KI#165.5. (GPT-6.2-Sol) -->
	def reset(self):
		self.pPrevUnit = None
		self.pCurrUnit = None

	def refresh(self, pUnit):
		self.pPrevUnit = self.pCurrUnit
		self.pCurrUnit = None
		if pUnit is not None and not pUnit.isNone():
			self.pCurrUnit = UnitDisplay(pUnit)

		if self.pCurrUnit is None:
			self._erasePromo()
		elif self.pPrevUnit is None:
			self._drawPromo()
		else:
			self._updatePromo()

	# <!-- custom: Read both slot snapshots through the plot instance. See KI#165.5. (GPT-6.2-Sol) -->
	def _updatePromo(self):
		if self.pCurrUnit.bPromo and not self.pPrevUnit.bPromo:
			self._showPromo()
		elif self.pPrevUnit.bPromo and not self.pCurrUnit.bPromo:
			self._hidePromo()

	# <!-- custom: Read the current snapshot through the plot instance. See KI#165.5. (GPT-6.2-Sol) -->
	def _drawPromo(self):
		if self.pCurrUnit.bPromo:
			self._showPromo()

	# <!-- custom: Read the previous snapshot through the plot instance. See KI#165.5. (GPT-6.2-Sol) -->
	def _erasePromo(self):
		if self.pPrevUnit is not None and self.pPrevUnit.bPromo:
			self._hidePromo()

	# <!-- custom: Hide the frame on this plot's screen. See KI#165.5. (GPT-6.2-Sol) -->
	def _hidePromo(self):
		self.screen.hide(self._getPromoString())

	# <!-- custom: Show the frame on this plot's screen. See KI#165.5. (GPT-6.2-Sol) -->
	def _showPromo(self):
		self.screen.show(self._getPromoString())

	# <!-- custom: Resolve the frame name from this plot's stored prefix. See KI#165.5. (GPT-6.2-Sol) -->
	def _getPromoString(self):
		return self.sBupString + "PromoFrame"

class UnitDisplay:
	def __init__(self, pUnit):
		self.bSelected = pUnit.IsSelected()
		self.eUnit = pUnit.getUnitType()
		# <!-- custom: Load the options before reading indicators and call the snapshot's two helpers through self. See KI#165.5. (GPT-6.2-Sol) -->
		updatePLEOptions(self)
		self.sDotState, self.iDotxSize, self.iDotySize, self.iDotxOffset, self.iDotyOffset = self._getDOTInfo(pUnit)
		self.sMission = self._getMission(pUnit)
		self.bPromo = pUnit.isPromotionReady()
		self.bGG = iLeaderPromo != -1 and pUnit.isHasPromotion(iLeaderPromo)
		self.bUpgrade = mt.checkAnyUpgrade(pUnit)
		self.icurrHitPoints = pUnit.currHitPoints()
		self.imaxHitPoints = pUnit.maxHitPoints()
		self.iMovesLeft = pUnit.movesLeft()
		self.iMoves = pUnit.getMoves()

	def _getDOTInfo(self, pUnit):
		xSize = 12
		ySize = 12
		xOffset = 0
		yOffset = 0

		if ((pUnit.getTeam() != gc.getGame().getActiveTeam()) or pUnit.isWaiting()):
			# fortified
			szDotState = "OVERLAY_FORTIFY"
		elif (pUnit.canMove()):
			if (pUnit.hasMoved()):
				# unit moved, but some movement points are left
				szDotState = "OVERLAY_HASMOVED"
			else:
				# unit did not move yet
				szDotState = "OVERLAY_MOVE"
		else:
			# unit has no movement points left
			szDotState = "OVERLAY_NOMOVE"

		# Wounded units will get a darker colored button.
		if (self.bShowWoundedIndicator) and (pUnit.isHurt()):
			szDotState += "_INJURED"

		# Units lead by a GG will get a star instead of a dot.
		if (self.bShowGreatGeneralIndicator):
			# is unit lead by a GG?
			if (iLeaderPromo != -1 and pUnit.isHasPromotion(iLeaderPromo)):
				szDotState += "_GG"
				xSize = 16
				ySize = 16
				xOffset = -3
				yOffset = -3

		return szDotState, xSize, ySize, xOffset, yOffset

	def _getMission(self, pUnit):
		eActivityType = pUnit.getGroup().getActivityType()
		eAutomationType = pUnit.getGroup().getAutomateType()

		# is unit on air intercept mission
		if (eActivityType == ActivityTypes.ACTIVITY_INTERCEPT):
			return "OVERLAY_ACTION_INTERCEPT"
		# is unit on boat patrol coast mission
		elif (eActivityType == ActivityTypes.ACTIVITY_PATROL):
			return "OVERLAY_ACTION_PATROL"
		# is unit on boat blockade mission
		elif (eActivityType == ActivityTypes.ACTIVITY_PLUNDER):
			return "OVERLAY_ACTION_PLUNDER"
		# is unit fortified for healing (wake up when healed)
		elif (eActivityType == ActivityTypes.ACTIVITY_HEAL):
			return "OVERLAY_ACTION_HEAL"
		# is unit sentry (wake up when enemy in sight)
		elif (eActivityType == ActivityTypes.ACTIVITY_SENTRY):
			return "OVERLAY_ACTION_SENTRY"
		# is the turn for this unit skipped (wake up next turn)
		elif (eActivityType == ActivityTypes.ACTIVITY_HOLD):
			return "OVERLAY_ACTION_SKIP"
		# has unit exploration mission
		elif (eAutomationType == AutomateTypes.AUTOMATE_EXPLORE):
			return "OVERLAY_ACTION_EXPLORE"
		# is unit automated generally (only worker units)
		elif (eAutomationType == AutomateTypes.AUTOMATE_BUILD):
			return "OVERLAY_ACTION_AUTO_BUILD"
		# is unit automated for nearest city (only worker units)
		elif (eAutomationType == AutomateTypes.AUTOMATE_CITY):
			return "OVERLAY_ACTION_AUTO_CITY"
		# is unit automated for network (only worker units)
		elif (eAutomationType == AutomateTypes.AUTOMATE_NETWORK):
			return "OVERLAY_ACTION_AUTO_NETWORK"
		# is unit automated spread religion (only missionary units)
		elif (eAutomationType == AutomateTypes.AUTOMATE_RELIGION):
			return "OVERLAY_ACTION_AUTO_RELIGION"
		# has unit a mission
		elif (pUnit.getGroup().getLengthMissionQueue() > 0):
			eMissionType = pUnit.getGroup().getMissionType(0)
			# is the mission to build an improvement
			if (eMissionType == MissionTypes.MISSION_BUILD):
				return "OVERLAY_ACTION_BUILD"
			# is the mission a "move to" mission
			elif (eMissionType in UnitUtil.MOVE_TO_MISSIONS):
				return "OVERLAY_ACTION_GOTO"
		# if nothing of above, but unit is waiting -> unit is fortified
		elif (pUnit.isWaiting()):
			if (pUnit.isFortifyable()):
				return "OVERLAY_ACTION_FORTIFY"
			else:
				return "OVERLAY_ACTION_SLEEP"

		return ""

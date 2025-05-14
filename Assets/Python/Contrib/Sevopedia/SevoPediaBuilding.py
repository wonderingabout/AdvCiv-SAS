# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
#
# <!-- custom: refactoring (of the below (and in too but anyways etc anyways etc)) is based on the sevopediaunit refactoring with small alterations/changes or/and not to fit/suit the sevopedia building code/features (also refactoring it (i.e: the sevopediabuilding code anyways etc) allowed to further polish and tweak and refactor or/and ifx or not or and other or and not anyways etc the sevopediaunit code so very nice or not nice or nice but not necessary or is or is not maybe or not (is) or yes (is not) but anyways etc anyways etc anyways etc...) done before that/this one anyways etc anyways etc, please/you can look there if you want more code comments and clarifications about the changes anyways etc anyways etc anyways etc) -->

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaBuilding:

	def __init__(self, main):
		self.iBuilding = -1
		self.top = main

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		self.X_BUILDING_PANE = self.top.X_PEDIA_PAGE
		self.Y_BUILDING_PANE = self.top.Y_PEDIA_PAGE
		self.W_BUILDING_PANE = (self.top.R_PEDIA_PAGE - self.X_BUILDING_PANE) / 2
		self.H_BUILDING_PANE = 190

		# <!-- custom: import iIconFrameSize from sevopediaunit ((base) advciv's code anyways etc) and modified it and its logic for advciv-sas or not or yes or and other things or and not anyways etc -->
		self.ICON_SIZE = 64
		self.ICON_FRAME_SIZE = 164
		self.MAX_ICON_FRAME_SIZE = 164

		if (self.ICON_SIZE > self.ICON_FRAME_SIZE):
			raise ValueError(u"[FATAL] self.ICON_SIZE=%d cannot be bigger/higher than self.ICON_FRAME_SIZE=%d, self.ICON_SIZE must fit within the frame, please adjust self.ICON_SIZE or/and self.ICON_FRAME_SIZE so that 0 < self.ICON_SIZE < self.ICON_FRAME_SIZE" % (self.ICON_SIZE, self.ICON_FRAME_SIZE))
		if (self.ICON_FRAME_SIZE > self.MAX_ICON_FRAME_SIZE):
			raise ValueError(u"[FATAL] Out of bounds self.ICON_FRAME_SIZE=%d, must be lower than  cannot be bigger/higher than self.MAX_ICON_FRAME_SIZE, please reduce self.ICON_FRAME_SIZE so that 0 < self.ICON_FRAME_SIZE < self.MAX_ICON_FRAME_SIZE" % (self.ICON_FRAME_SIZE, self.MAX_ICON_FRAME_SIZE))

		self.W_ICON = self.ICON_SIZE
		self.H_ICON = self.ICON_SIZE
		# <!-- custom: if self.ICON_SIZE is small (e.g. 64), start at the center of self.X_BUILDING_PANE, but if self.ICON_SIZE is big (e.g. 164) start at the left most part of self.X_BUILDING_PANE ; same reasoning for Y position -->
		self.X_ICON = self.X_BUILDING_PANE + (self.ICON_FRAME_SIZE - self.ICON_SIZE) / 2
		self.Y_ICON = self.Y_BUILDING_PANE + (self.H_BUILDING_PANE - self.H_ICON) / 2

		# <!-- custom: add an extra margin to accomodate the potentially larger self.ICON_SIZE (than for example 64), if diff is 0 this is harmless to keep too so is dynamical code that can handle optionally larger self.ICON_SIZE (vs old self.ICON_SIZE of 64) that you may keep or remove as you prefer anyways etc -->
		self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN = (self.ICON_FRAME_SIZE - self.ICON_SIZE) / 2

		self.STATS_PANE_LEFT_SIDE_MARGIN = 0
		self.STATS_PANE_UPPER_PADDING = 38

		self.X_STATS_PANE = self.X_BUILDING_PANE + self.STATS_PANE_LEFT_SIDE_MARGIN + self.W_ICON + (2 * self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN)
		self.Y_STATS_PANE = self.Y_BUILDING_PANE + self.STATS_PANE_UPPER_PADDING
		self.W_STATS_PANE = self.W_BUILDING_PANE - self.W_ICON - (2 * self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN) - self.STATS_PANE_LEFT_SIDE_MARGIN
		self.H_STATS_PANE = self.H_BUILDING_PANE - self.STATS_PANE_UPPER_PADDING

		self.H_STATS_PANE_LINE_HEIGHT = 38

		self.X_PREREQ_PANE = self.X_BUILDING_PANE
		self.Y_PREREQ_PANE = self.Y_BUILDING_PANE + self.H_BUILDING_PANE + self.SMALL_MARGIN
		self.W_PREREQ_PANE = self.W_BUILDING_PANE
		self.H_PREREQ_PANE = 110

		self.X_REPLACED_BY = self.X_PREREQ_PANE
		self.Y_REPLACED_BY = self.Y_PREREQ_PANE + self.H_PREREQ_PANE + self.SMALL_MARGIN
		self.W_REPLACED_BY = self.W_PREREQ_PANE
		self.H_REPLACED_BY = self.H_PREREQ_PANE

		self.X_OBSOLETES_WITH = self.X_PREREQ_PANE
		self.Y_OBSOLETES_WITH = self.Y_REPLACED_BY + self.H_REPLACED_BY + self.SMALL_MARGIN
		self.W_OBSOLETES_WITH = self.W_PREREQ_PANE
		self.H_OBSOLETES_WITH = self.H_PREREQ_PANE

		self.X_SPECIAL_PANE = self.X_BUILDING_PANE
		self.Y_SPECIAL_PANE = self.Y_PREREQ_PANE + self.H_PREREQ_PANE + self.SMALL_MARGIN
		self.W_SPECIAL_PANE = self.W_PREREQ_PANE
		self.H_SPECIAL_PANE = self.top.B_PEDIA_PAGE - self.Y_SPECIAL_PANE

		self.X_BUILDING_ANIMATION = self.X_BUILDING_PANE + self.W_BUILDING_PANE + self.MEDIUM_MARGIN
		self.Y_BUILDING_ANIMATION = self.Y_BUILDING_PANE + 7
		self.W_BUILDING_ANIMATION = self.W_BUILDING_PANE - self.MEDIUM_MARGIN
		self.H_BUILDING_ANIMATION = self.H_BUILDING_PANE + self.SMALL_MARGIN + self.H_PREREQ_PANE + self.SMALL_MARGIN + self.H_REPLACED_BY - 7
		
		self.X_ROTATION_BUILDING_ANIMATION = -20
		self.Z_ROTATION_BUILDING_ANIMATION = 30
		self.SCALE_ANIMATION = 0.7

		self.X_EXCLUSIVE_CIVS = self.X_OBSOLETES_WITH + self.W_OBSOLETES_WITH + self.MEDIUM_MARGIN
		self.Y_EXCLUSIVE_CIVS = self.Y_OBSOLETES_WITH
		self.W_EXCLUSIVE_CIVS = self.W_BUILDING_ANIMATION
		self.H_EXCLUSIVE_CIVS = self.H_OBSOLETES_WITH

		self.X_HISTORY_PANE = self.X_BUILDING_ANIMATION
		self.Y_HISTORY_PANE = self.Y_EXCLUSIVE_CIVS + self.H_EXCLUSIVE_CIVS + self.MEDIUM_MARGIN + 17
		self.W_HISTORY_PANE = self.W_BUILDING_ANIMATION
		self.H_HISTORY_PANE = self.top.B_PEDIA_PAGE - self.Y_HISTORY_PANE



	def interfaceScreen(self, iBuilding):
		self.iBuilding = iBuilding

		self.placeBuildingPane()
		self.placeStats()
		self.placeRequires()
		self.placeSpecial()
		self.placeHistory()



	def placeBuildingPane(self):
		screen = self.top.getScreen()

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_BUILDING_PANE, self.Y_BUILDING_PANE, self.W_BUILDING_PANE, self.H_BUILDING_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getBuildingInfo(self.iBuilding).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addBuildingGraphicGFC(self.top.getNextWidgetName(), self.iBuilding, self.X_BUILDING_ANIMATION, self.Y_BUILDING_ANIMATION, self.W_BUILDING_ANIMATION, self.H_BUILDING_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_BUILDING_ANIMATION, self.Z_ROTATION_BUILDING_ANIMATION, self.SCALE_ANIMATION, True)



	# <!-- custom: table code based on placeAiPersonality panel method/function in sevopedialeader we (me and becomingthrough chatgpt) had written and enhanced together and all anyways etc, modifying/adjusting it for this sevopediabuilding (much) simpler panel (stats pane) need but still important as we don't want to scroll after say 4th element, move to 2nd column rather and resume filling there. -->
	def placeStats(self):
		screen = self.top.getScreen()
		numColumns = 3
		columnWidth = self.W_STATS_PANE / numColumns

		def setupPanel(screen, txtKey):
			panelName = self.top.getNextWidgetName()
			screen.addPanel(
				panelName,
				localText.getText(txtKey, ()),
				"",
				True,
				True,
				self.X_STATS_PANE,
				self.Y_STATS_PANE,
				self.W_STATS_PANE,
				self.H_STATS_PANE,
				# <!-- custom: useful for debugging, otherwise we don't need a blue on blue color, prefer transparent ("EMPTY" if i am not mistaken anyways etc), anyways etc -->
				#PanelStyles.PANEL_STYLE_BLUE50,
				PanelStyles.PANEL_STYLE_EMPTY,
			)

		# === PANEL SETUP ===
		setupPanel(screen, "")

		# <!-- custom: refer to code below to know max element count, so far we have in our code:
		# Cost (1), Food (2), Gold per turn (GPT anyways etc... anyways etc...) (3), Culture (4), Espionage (5), Happiness or Unhappiness (6), Health(y?)(iness?? Anyways etc... Anyways etc...) or Unhealth(y)(same anyways etc... anyways etc...) (7), Great people (8), hopefully i didn't miss any but may have had, no functional difference, but good to know the informative and accurate value still maybe or not or yes or and other or maybe not but anyways etc anyways etc anyways etc...
		# -->

		def fillCell(screen, label, xLabel, y):
			labelText = u"<font=4>%s</font>" % label

			screen.setText(self.top.getNextWidgetName(), "", labelText,
				CvUtil.FONT_LEFT_JUSTIFY, xLabel, y, 0, FontTypes.SMALL_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)

		def getNextItemCoordinates(x, y, rowItemId, columnWidth):
			anticipatedNextRowId = rowItemId + 1
			anticipatedNextRowNum = anticipatedNextRowId + 1
			if (anticipatedNextRowNum * self.H_STATS_PANE_LINE_HEIGHT > (self.H_STATS_PANE - self.STATS_PANE_UPPER_PADDING)):
				# <!-- custom: move to next column and back to first row, reset columItemId to 0 -->
				x = x + columnWidth
				y = self.Y_STATS_PANE
				rowItemId = 0
				return x, y, rowItemId
			else:
				# <!-- custom: else x remains the same, and we go to next row (we stay in same column as long as we have room) -->
				y += self.H_STATS_PANE_LINE_HEIGHT
				rowItemId += 1
				return x, y, rowItemId

		# === Render Function ===
		def renderCells(screen, columnWidth, xPanel, yPanel):
			x = xPanel
			y = yPanel
			rowItemId = 0

			buildingInfo = gc.getBuildingInfo(self.iBuilding)

			# <!-- custom: if i am not mistaken it seems we never use the code below and i don't understand too well what it is for, but especially in our placeStats pane i don't think we use it at all if i am not mistaken, so commenting it out
			"""
			if (isWorldWonderClass(gc.getBuildingInfo(self.iBuilding).getBuildingClassType())):
				iMaxInstances = gc.getBuildingClassInfo(gc.getBuildingInfo(self.iBuilding).getBuildingClassType()).getMaxGlobalInstances()
				szBuildingType = localText.getText("TXT_KEY_PEDIA_WORLD_WONDER", ())
				if (iMaxInstances > 1):
					szBuildingType += " " + localText.getText("TXT_KEY_PEDIA_WONDER_INSTANCES", (iMaxInstances,))
					szBuildingTypeText = u"<font=4>" + szBuildingType.upper() + u"</font>"
					screen.appendListBoxStringNoUpdate(panelName, szBuildingTypeText, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

			if (isTeamWonderClass(gc.getBuildingInfo(self.iBuilding).getBuildingClassType())):
				iMaxInstances = gc.getBuildingClassInfo(gc.getBuildingInfo(self.iBuilding).getBuildingClassType()).getMaxTeamInstances()
				szBuildingType = localText.getText("TXT_KEY_PEDIA_TEAM_WONDER", ())
				if (iMaxInstances > 1):
					szBuildingType += " " + localText.getText("TXT_KEY_PEDIA_WONDER_INSTANCES", (iMaxInstances,))
					szBuildingTypeText = u"<font=4>" + szBuildingType.upper() + u"</font>"
					screen.appendListBoxStringNoUpdate(panelName, szBuildingTypeText, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

			if (isNationalWonderClass(gc.getBuildingInfo(self.iBuilding).getBuildingClassType())):
				iMaxInstances = gc.getBuildingClassInfo(gc.getBuildingInfo(self.iBuilding).getBuildingClassType()).getMaxPlayerInstances()
				szBuildingType = localText.getText("TXT_KEY_PEDIA_NATIONAL_WONDER", ())
				if (iMaxInstances > 1):
					szBuildingType += " " + localText.getText("TXT_KEY_PEDIA_WONDER_INSTANCES", (iMaxInstances,))
					szBuildingTypeText = u"<font=4>" + szBuildingType.upper() + u"</font>"
					screen.appendListBoxStringNoUpdate(panelName, szBuildingTypeText, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
			"""

			# <!-- custom: 1: Cost -->
			if (buildingInfo.getProductionCost() > 0):
				if self.top.iActivePlayer == -1:
					szCost = localText.getText("TXT_KEY_PEDIA_COST_CUSTOM", ((buildingInfo.getProductionCost() * gc.getDefineINT("BUILDING_PRODUCTION_PERCENT"))/100,))
				else:
					szCost = localText.getText("TXT_KEY_PEDIA_COST_CUSTOM", (gc.getPlayer(self.top.iActivePlayer).getBuildingProductionNeeded(self.iBuilding),))
				szText2 = u"%c  %s" % (gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar(), szCost)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

			# <!-- custom: 2 and 3: Food (2) and Gold per turn (3) if i am not mistaken anyways etc (which would anyways etc GPT anyways etc...) -->
			for k in range(YieldTypes.NUM_YIELD_TYPES):
				if (buildingInfo.getYieldChange(k) != 0):
					if (buildingInfo.getYieldChange(k) > 0):
						szSign = "+"
					else:
						szSign = ""
					szText1 = szSign + str(buildingInfo.getYieldChange(k))
					szText2 = u"%c  %s" % (gc.getYieldInfo(k).getChar(), szText1)
					fillCell(screen, szText2, x, y)
					x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

			# <!-- custom: 4 and 5: Culture (4) and Espionage (5) anyways etc anyways etc...... anyways etc... -->
			for k in range(CommerceTypes.NUM_COMMERCE_TYPES):
				iTotalCommerce = buildingInfo.getObsoleteSafeCommerceChange(k) + buildingInfo.getCommerceChange(k)
				if (iTotalCommerce != 0):
					if (iTotalCommerce > 0):
						szSign = "+"
					else:
						szSign = ""
					szText1 = szSign + str(iTotalCommerce)
					szText2 = u"%c  %s" % (gc.getCommerceInfo(k).getChar(), szText1)
					fillCell(screen, szText2, x, y)
					x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

			# <!-- custom: 6: Happiness or Unhappiness anyways etc -->
			iHappiness = buildingInfo.getHappiness()
			if self.top.iActivePlayer != -1:
				if (self.iBuilding == gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationBuildings(buildingInfo.getBuildingClassType())):
					iHappiness += gc.getPlayer(self.top.iActivePlayer).getExtraBuildingHappiness(self.iBuilding)

			if (iHappiness > 0):
				szText = localText.getText("TXT_KEY_PEDIA_HAPPY_CUSTOM", (iHappiness,))
				szText2 = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.HAPPY_CHAR), szText)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)
			elif (iHappiness < 0):
				szText = localText.getText("TXT_KEY_PEDIA_UNHAPPY_CUSTOM", (-iHappiness,))
				szText2 = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.UNHAPPY_CHAR), szText)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

			# <!-- custom: 7: Health(y?)(iness?? Anyways etc... Anyways etc...) or Unhealth(y)(same anyways etc... anyways etc...) anyways etc -->
			iHealth = buildingInfo.getHealth()
			if self.top.iActivePlayer != -1:
				if (self.iBuilding == gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationBuildings(buildingInfo.getBuildingClassType())):
					iHealth += gc.getPlayer(self.top.iActivePlayer).getExtraBuildingHealth(self.iBuilding)

			if (iHealth > 0):
				szText = localText.getText("TXT_KEY_PEDIA_HEALTHY_CUSTOM", (iHealth,))
				szText2 = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.HEALTHY_CHAR), szText)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)
			elif (iHealth < 0):
				szText = localText.getText("TXT_KEY_PEDIA_UNHEALTHY_CUSTOM", (-iHealth,))
				szText2 = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.UNHEALTHY_CHAR), szText)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

			# <!-- custom: 8: Great people -->
			if (buildingInfo.getGreatPeopleRateChange() != 0):
				szText = localText.getText("TXT_KEY_PEDIA_GREAT_PEOPLE_CUSTOM", (buildingInfo.getGreatPeopleRateChange(),))
				szText2 = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR), szText)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

		# Render Panels
		renderCells(screen, columnWidth, self.X_STATS_PANE, self.Y_STATS_PANE)



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_PREREQ_PANE, self.Y_PREREQ_PANE, self.W_PREREQ_PANE, self.H_PREREQ_PANE, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")

		for iPrereq in range(gc.getNumTechInfos()):
			if isTechRequiredForBuilding(iPrereq, self.iBuilding):
				screen.attachImageButton( panelName, "", gc.getTechInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iPrereq, 1, False )

		iPrereq = gc.getBuildingInfo(self.iBuilding).getPrereqAndBonus()
		if (iPrereq >= 0):
			screen.attachImageButton( panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False )

		for k in range(gc.getNUM_BUILDING_PREREQ_OR_BONUSES()):
			iPrereq = gc.getBuildingInfo(self.iBuilding).getPrereqOrBonuses(k)
			if (iPrereq >= 0):
				screen.attachImageButton( panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False )

		iCorporation = gc.getBuildingInfo(self.iBuilding).getFoundsCorporation()
		bFirst = True
		if (iCorporation >= 0):
			for k in range(gc.getNUM_CORPORATION_PREREQ_BONUSES()):
				iPrereq = gc.getCorporationInfo(iCorporation).getPrereqBonus(k)
				if (iPrereq >= 0):
					if not bFirst:
						screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
					else:
						bFirst = False
					screen.attachImageButton( panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False )

		iPrereq = gc.getBuildingInfo(self.iBuilding).getPrereqReligion()
		if (iPrereq >= 0):
			screen.attachImageButton( panelName, "", gc.getReligionInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereq, -1, False )



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", True, False, self.X_SPECIAL_PANE, self.Y_SPECIAL_PANE, self.W_SPECIAL_PANE, self.H_SPECIAL_PANE, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getBuildingHelp(self.iBuilding, True, False, False, None)[1:]
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL_PANE+5, self.Y_SPECIAL_PANE+30, self.W_SPECIAL_PANE-10, self.H_SPECIAL_PANE-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: same reasoning as for/in SevopediaUnit.py, i don't need the redundant background
		# -->
		#screen.addPanel( panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY_PANE, self.Y_HISTORY_PANE, self.W_HISTORY_PANE, self.H_HISTORY_PANE, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.addPanel( panelName, "", "", True, True, self.X_HISTORY_PANE, self.Y_HISTORY_PANE, self.W_HISTORY_PANE, self.H_HISTORY_PANE, PanelStyles.PANEL_STYLE_BLUE50 )
		textName = self.top.getNextWidgetName()
		szText = u""
		# <!-- custom: too much hassle/"nightmare" to maintain the strategy texts in history panel (which i agree with), + also often inaccurate, especially if someone were to make a mod, just ignoring them without importing the XML assets as well is much more efficient, more reliable, and perhaps clearer in the sevopedia too maybe.
		# -->
		# if len(gc.getBuildingInfo(self.iBuilding).getStrategy()) > 0:
		#	szText += localText.getText("TXT_KEY_CIVILOPEDIA_STRATEGY", ())
		#	szText += gc.getBuildingInfo(self.iBuilding).getStrategy()
		#	szText += u"\n\n"
		# <!-- custom: same reasoning as for/in SevopediaUnit.py, i don't need
		# the redundant background
		# -->
		#szText += localText.getText("TXT_KEY_CIVILOPEDIA_BACKGROUND", ())
		szText += gc.getBuildingInfo(self.iBuilding).getCivilopedia()
		# but here we also restore/add padding
		# -->
		#screen.addMultilineText( textName, szText, self.X_HISTORY_PANE + 15, self.Y_HISTORY_PANE + 40, self.W_HISTORY_PANE - (15 * 2), self.H_HISTORY_PANE - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText( textName, szText, self.X_HISTORY_PANE + 7, self.Y_HISTORY_PANE + 10, self.W_HISTORY_PANE - (15 * 2), self.H_HISTORY_PANE - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def getBuildingType(self, iBuilding):
		if (isWorldWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			return 2
		elif (isNationalWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			return 1
		else:
			return 0



	def getBuildingSortedList(self, iBuildingType):
		list1 = []
		numInfos = 0
		for iBuilding in range(gc.getNumBuildingInfos()):
			if (self.getBuildingType(iBuilding) == iBuildingType):
				list1.append(iBuilding)
				numInfos += 1
		list2 = [(0,0)] * numInfos
		i = 0
		for iBuilding in list1:
			list2[i] = (gc.getBuildingInfo(iBuilding).getDescription(), iBuilding)
			i += 1
		if self.top.isSortLists():
			list2.sort()
		return list2



	def handleInput (self, inputClass):
		return 0

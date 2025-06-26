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
# <!-- custom: new :
# - placeReplace (renamed from placeReplacements of: ) in particular, is imported from RFC DOC mod:
# C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\RFC Dawn of Civilization\Assets\Python\Pedia\CvPediaUnit.py
# which may have then been modified or not for AdvCiv-SAS or/and enhanced or/and tweaked or/and adjusted anyways etc (see also sevopediabuilding (+/- 's code comments as you prefer or not or want or do or not or other or etc anyways etc) for details even though it was done later, it also served to adjust it or not anyways etc)
# - placeCivilizations: added entirely (i only tweaked the coordinates to suit/match where i want(ed?) it anyways etc) by Claude AI from my prompt anyways etc, now we have buttons for the civ(s) that can build a unit, and no button at all if all civs can build the currently selected unit (to not clutter the display needlessly with all civs buttons and is also clearer to know immediately that all can build it with the panel being empty),
# - the place peak hill city terrains bonus features function/method in a similar manner,
# - and the of this unit against modifiers
# - as well as of other units modifiers (which would be/is against this (currently selected) unit this time anyways etc),
# - as well as the placeFreePromotions
# thanks a lot Claude AI! Anyways etc anyways etc anyways etc... -->
# -->

from CvPythonExtensions import *
import CvUtil
# <!-- custom: remove or comment out unused imports -->
#import ScreenInput
#import SevoScreenEnums

from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaUnit:

	def __init__(self, main):
		self.iUnit = -1
		self.top = main

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		self.X_UNIT_PANE = self.top.X_PEDIA_PAGE
		self.Y_UNIT_PANE = self.top.Y_PEDIA_PAGE
		# <!-- custom: no margins to merge edges with promo pane for nicer display maybe i mean anyways etc -->
		self.W_UNIT_PANE = (self.top.R_PEDIA_PAGE - self.X_UNIT_PANE - self.MEDIUM_MARGIN) / 4
		self.H_UNIT_PANE = 190

		# <!-- custom: import iIconFrameSize from sevopediaunit ((base) advciv's code anyways etc) and modified it and its logic for advciv-sas or not or yes or and other things or and not anyways etc -->
		self.ICON_SIZE = 64
		self.ICON_FRAME_SIZE = 164
		self.MAX_ICON_FRAME_SIZE = 164

		if (self.ICON_SIZE > self.ICON_FRAME_SIZE):
			raise ValueError(u"[FATAL] self.ICON_SIZE=%d cannot be bigger/higher than self.ICON_FRAME_SIZE=%d, self.ICON_SIZE must fit within the frame, please adjust self.ICON_SIZE or/and self.ICON_FRAME_SIZE so that 0 < self.ICON_SIZE < self.ICON_FRAME_SIZE" % (self.ICON_SIZE, self.ICON_FRAME_SIZE))
		if (self.ICON_FRAME_SIZE > self.MAX_ICON_FRAME_SIZE):
			raise ValueError(u"[FATAL] Out of bounds self.ICON_FRAME_SIZE=%d, must be lower than  cannot be bigger/higher than self.MAX_ICON_FRAME_SIZE=%d, please reduce self.ICON_FRAME_SIZE so that 0 < self.ICON_FRAME_SIZE < self.MAX_ICON_FRAME_SIZE" % (self.ICON_FRAME_SIZE, self.MAX_ICON_FRAME_SIZE))

		self.W_ICON = self.ICON_SIZE
		self.H_ICON = self.ICON_SIZE
		# <!-- custom: if self.ICON_SIZE is small (e.g. 64), start at the center of self.X_UNIT_PANE, but if self.ICON_SIZE is big (e.g. 164) start at the left most part of self.X_UNIT_PANE ; same reasoning for Y position -->
		self.X_ICON = self.X_UNIT_PANE + (self.ICON_FRAME_SIZE - self.ICON_SIZE) / 2
		self.Y_ICON = self.Y_UNIT_PANE + (self.H_UNIT_PANE - self.H_ICON) / 2

		# <!-- custom: add an extra margin to accomodate the potentially larger self.ICON_SIZE (than for example 64), if diff is 0 this is harmless to keep too so is dynamical code that can handle optionally larger self.ICON_SIZE (vs old self.ICON_SIZE of 64) that you may keep or remove as you prefer anyways etc -->
		self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN = (self.ICON_FRAME_SIZE - self.ICON_SIZE) / 2

		self.STATS_PANE_LEFT_SIDE_MARGIN = 0
		self.STATS_PANE_UPPER_PADDING = 42

		self.PROMOTION_ICON_SIZE = 32

		# <!-- custom: no margins to merge edges with unit pane for nicer display maybe i mean anyways etc -->
		# <!-- custom: merge effect by partially joining their borders, i accidentally found or/and maybe got the idea and looks very nice, just is slightly not centered maybe fixable or not but and in all cases anyways etc anyways etc -->
		self.W_MERGE_PANELS_EFFECT = 5

		self.X_PROMO_PANE = self.X_UNIT_PANE + self.W_UNIT_PANE - self.W_MERGE_PANELS_EFFECT
		self.Y_PROMO_PANE = self.Y_UNIT_PANE
		self.W_PROMO_PANE = self.W_UNIT_PANE + self.W_MERGE_PANELS_EFFECT
		self.H_PROMO_PANE = self.H_UNIT_PANE

		self.X_STATS_PANE = self.X_UNIT_PANE + self.STATS_PANE_LEFT_SIDE_MARGIN + self.W_ICON + (2 *self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN)
		self.Y_STATS_PANE = self.Y_UNIT_PANE + self.STATS_PANE_UPPER_PADDING
		self.W_STATS_PANE = self.W_UNIT_PANE - self.W_ICON - (2 * self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN) - self.STATS_PANE_LEFT_SIDE_MARGIN
		self.H_STATS_PANE = self.H_UNIT_PANE - self.STATS_PANE_UPPER_PADDING

		# <!-- custom: see sevopediabuilding's self.W_TOTAL_EFFECTIVE_BUILDING_PANE for differences in implementation anyways etc -->
		self.W_TOTAL_EFFECTIVE_UNIT_PANE = self.W_UNIT_PANE + self.W_PROMO_PANE - self.W_MERGE_PANELS_EFFECT

		self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING = 8
		self.HYPOTHESIZED_INTER_BUTTON_SPACING = 4

		self.X_REQUIRES = self.X_UNIT_PANE
		self.Y_REQUIRES = self.Y_UNIT_PANE + self.H_UNIT_PANE + self.SMALL_MARGIN
		self.W_REQUIRES = self.W_TOTAL_EFFECTIVE_UNIT_PANE
		self.H_REQUIRES = 110

		self.X_UPGRADES_TO = self.X_UNIT_PANE
		self.Y_UPGRADES_TO = self.Y_REQUIRES + self.H_REQUIRES + self.SMALL_MARGIN
		self.W_UPGRADES_TO = ((self.W_TOTAL_EFFECTIVE_UNIT_PANE - self.MEDIUM_MARGIN)/ 2) 
		self.H_UPGRADES_TO = self.H_REQUIRES

		self.X_FREE = self.X_UPGRADES_TO + self.W_UPGRADES_TO + self.MEDIUM_MARGIN
		self.Y_FREE = self.Y_UPGRADES_TO
		self.W_FREE = self.W_UPGRADES_TO
		self.H_FREE = self.H_UPGRADES_TO

		self.X_OF_UNIT_MODIFIERS_AGAINST_OTHERS = self.X_UNIT_PANE
		self.Y_OF_UNIT_MODIFIERS_AGAINST_OTHERS = self.Y_UPGRADES_TO + self.H_UPGRADES_TO + self.SMALL_MARGIN
		self.W_OF_UNIT_MODIFIERS_AGAINST_OTHERS = self.W_UPGRADES_TO
		self.H_OF_UNIT_MODIFIERS_AGAINST_OTHERS = self.H_REQUIRES

		self.X_TERRAIN_FEATURE_CITY_BONUSES = self.X_OF_UNIT_MODIFIERS_AGAINST_OTHERS + self.W_OF_UNIT_MODIFIERS_AGAINST_OTHERS + self.MEDIUM_MARGIN
		self.Y_TERRAIN_FEATURE_CITY_BONUSES = self.Y_OF_UNIT_MODIFIERS_AGAINST_OTHERS
		self.W_TERRAIN_FEATURE_CITY_BONUSES = self.W_OF_UNIT_MODIFIERS_AGAINST_OTHERS
		self.H_TERRAIN_FEATURE_CITY_BONUSES = self.H_OF_UNIT_MODIFIERS_AGAINST_OTHERS

		self.X_OF_OTHER_UNITS_MODIFIERS = self.X_UNIT_PANE
		self.Y_OF_OTHER_UNITS_MODIFIERS = self.Y_OF_UNIT_MODIFIERS_AGAINST_OTHERS + self.H_OF_UNIT_MODIFIERS_AGAINST_OTHERS + self.SMALL_MARGIN
		self.W_OF_OTHER_UNITS_MODIFIERS = self.top.R_PEDIA_PAGE - self.X_UNIT_PANE
		self.H_OF_OTHER_UNITS_MODIFIERS = self.H_REQUIRES

		self.X_SPECIAL = self.X_UNIT_PANE
		self.Y_SPECIAL = self.Y_OF_OTHER_UNITS_MODIFIERS + self.H_OF_OTHER_UNITS_MODIFIERS + self.SMALL_MARGIN
		self.W_SPECIAL = self.W_TOTAL_EFFECTIVE_UNIT_PANE
		self.H_SPECIAL = self.top.B_PEDIA_PAGE - self.Y_SPECIAL

		self.H_ADJUST_HEIGHT_ANIMATION_TO_MATCH_ADJACENT_PANE = 7

		self.X_UNIT_ANIMATION = self.X_UNIT_PANE + self.W_TOTAL_EFFECTIVE_UNIT_PANE + self.MEDIUM_MARGIN
		self.Y_UNIT_ANIMATION = self.Y_UNIT_PANE + self.H_ADJUST_HEIGHT_ANIMATION_TO_MATCH_ADJACENT_PANE
		self.W_UNIT_ANIMATION = self.W_TOTAL_EFFECTIVE_UNIT_PANE
		self.H_UNIT_ANIMATION = self.H_UNIT_PANE + self.SMALL_MARGIN + self.H_REQUIRES + self.SMALL_MARGIN + self.H_UPGRADES_TO - self.H_ADJUST_HEIGHT_ANIMATION_TO_MATCH_ADJACENT_PANE

		self.X_ROTATION_UNIT_ANIMATION = -20
		self.Z_ROTATION_UNIT_ANIMATION = 30
		self.SCALE_ANIMATION = 1.0

		self.W_CIVILIZATIONS = 84

		self.X_REPLACE = self.X_UNIT_ANIMATION
		self.Y_REPLACE = self.Y_UNIT_ANIMATION + self.H_UNIT_ANIMATION + self.SMALL_MARGIN
		self.W_REPLACE = self.W_UNIT_ANIMATION - self.MEDIUM_MARGIN - self.W_CIVILIZATIONS
		self.H_REPLACE = self.H_REQUIRES

		self.X_CIVILIZATIONS = self.X_UNIT_ANIMATION + self.W_REPLACE + self.MEDIUM_MARGIN
		self.Y_CIVILIZATIONS = self.Y_REPLACE

		self.H_CIVILIZATIONS = self.H_REPLACE

		self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER = 22

		self.X_HISTORY = self.X_UNIT_ANIMATION
		self.Y_HISTORY = self.Y_OF_OTHER_UNITS_MODIFIERS + self.H_OF_OTHER_UNITS_MODIFIERS + self.SMALL_MARGIN
		self.W_HISTORY = self.W_UNIT_ANIMATION
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY



	def interfaceScreen(self, iUnit):
		self.iUnit = iUnit

		self.placeUnitPane()
		self.placeStats()
		self.placePromotions()
		self.placeRequires()
		self.placeUpgradesTo()
		self.placeFreePromotions()
		self.placeModifiersOfThisUnitAgainstOtherUnitClassesCombatTypes()
		self.placeModifiersOfOtherUnitClassesCombatTypesAgainstThisUnit()
		self.placePeakHillCityTerrainsFeaturesModifiers()
		self.placeSpecial()
		self.placeUnitAnimation()
		self.placeReplace()
		self.placeCivilizations()
		self.placeHistory()



	def placeUnitPane(self):
		screen = self.top.getScreen()

		# <!-- custom: note: using self.W_UNIT_PANE at panel creation if i am not mistaken anyways etc unlike in sevopediabuilding part equivalent to this code where we use self.W_TOTAL_EFFECTIVE_BUILDING_PANE due to differences in their implementations, see sevopediabuilding for comparison or/and details anyways etc -->
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_UNIT_PANE, self.Y_UNIT_PANE, self.W_UNIT_PANE, self.H_UNIT_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		szButton = gc.getUnitInfo(self.iUnit).getButton()
		# <advc.003l>
		iActivePlayer = gc.getGame().getActivePlayer()
		if iActivePlayer >= 0:
			szButton = gc.getPlayer(iActivePlayer).getUnitButton(self.iUnit)
		# </advc.003l>
		screen.addDDSGFC(self.top.getNextWidgetName(), szButton, self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)



	def placeStats(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		iCombatType = gc.getUnitInfo(self.iUnit).getUnitCombatType()

		if (iCombatType != -1):
			screen.setImageButton(self.top.getNextWidgetName(), gc.getUnitCombatInfo(iCombatType).getButton(), self.X_STATS_PANE, self.Y_STATS_PANE - 35, 32, 32, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, iCombatType, 0)
			screen.setText(self.top.getNextWidgetName(), "", u"<font=3>" + gc.getUnitCombatInfo(iCombatType).getDescription() + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, self.X_STATS_PANE + 37, self.Y_STATS_PANE - 30, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, iCombatType, 0)

		screen.addListBoxGFC(panelName, "", self.X_STATS_PANE, self.Y_STATS_PANE, self.W_STATS_PANE, self.H_STATS_PANE, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panelName, False)

		if (gc.getUnitInfo(self.iUnit).getAirCombat() > 0 and gc.getUnitInfo(self.iUnit).getCombat() == 0):
			iStrength = gc.getUnitInfo(self.iUnit).getAirCombat()
		else:
			iStrength = gc.getUnitInfo(self.iUnit).getCombat()
		if iStrength > 0: # advc.004y: Don't show 0 strength for nukes
			szName = self.top.getNextWidgetName()
			szStrength = localText.getText("TXT_KEY_PEDIA_STRENGTH_CUSTOM", (iStrength,))
			szStrengthText = u"%c  " % CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR) + szStrength
			screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szStrengthText + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		eDomain = gc.getUnitInfo(self.iUnit).getDomainType()
		# <!-- custom: don't show movement for domain immobile units (missiles and such for example, not air fighters and such if i am not mistaken anyways etc) --> 
		if eDomain != DomainTypes.DOMAIN_IMMOBILE:
			# <!-- custom: show all stats that we want/have as they are, including 1 move air or
			# 4 move helicopter, (hopefully helpful ,) (but) (if or not)(anyways etc) anyways etc -->
			## Don't show 1 move for air units
			#elif eDomain != DomainTypes.DOMAIN_AIR: # </advc.004y>
			szName = self.top.getNextWidgetName()
			szMovement = localText.getText("TXT_KEY_PEDIA_MOVEMENT_CUSTOM", (gc.getUnitInfo(self.iUnit).getMoves(),))
			szMovementText = u"%c  " % CyGame().getSymbolID(FontSymbols.MOVES_CHAR) + szMovement
			screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szMovementText + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		# advc.004y: Moved range above production cost. Condition for ICBM added.
		if gc.getUnitInfo(self.iUnit).getAirRange() > 0 or gc.getUnitInfo(self.iUnit).getNukeRange() >= 0:
			szName = self.top.getNextWidgetName()
			iRange = gc.getUnitInfo(self.iUnit).getAirRange()
			if iRange > 0: # advc.004y
				szRange = localText.getText("TXT_KEY_PEDIA_RANGE_CUSTOM", (iRange,))
			# <advc.004y> Unlimited range
			else:
				szRange = localText.getText("TXT_KEY_PEDIA_RANGE_UNLIMITED_CUSTOM", ())
			# </advc.004y>
			szRangeText = u"R    " + szRange
			screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szRangeText + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		if (gc.getUnitInfo(self.iUnit).getProductionCost() >= 0 and not gc.getUnitInfo(self.iUnit).isFound()):
			szName = self.top.getNextWidgetName()
			if self.top.iActivePlayer == -1:
				szCost = localText.getText("TXT_KEY_PEDIA_COST_CUSTOM", ((gc.getUnitInfo(self.iUnit).getProductionCost() * gc.getDefineINT("UNIT_PRODUCTION_PERCENT"))/100,))
			else:
				szCost = localText.getText("TXT_KEY_PEDIA_COST_CUSTOM", (gc.getActivePlayer().getUnitProductionNeeded(self.iUnit),))
			szCostText = u"%c  " % gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar() + szCost
			screen.appendListBoxStringNoUpdate(panelName, u"<font=4>" + szCostText + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		screen.updateListBox(panelName)



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		iPrereq = gc.getUnitInfo(self.iUnit).getPrereqAndTech()
		if (iPrereq >= 0):
			screen.attachImageButton(panelName, "", gc.getTechInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iPrereq, 1, False)
		for j in range(gc.getDefineINT("NUM_UNIT_AND_TECH_PREREQS")):
			iPrereq = gc.getUnitInfo(self.iUnit).getPrereqAndTechs(j)
			if (iPrereq >= 0):
				screen.attachImageButton(panelName, "", gc.getTechInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iPrereq, -1, False)
		bFirst = True

		iPrereq = gc.getUnitInfo(self.iUnit).getPrereqAndBonus()
		if (iPrereq >= 0):
			bFirst = False
			screen.attachImageButton(panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False)
		nOr = 0
		for j in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
			if (gc.getUnitInfo(self.iUnit).getPrereqOrBonuses(j) > -1):
				nOr += 1
		szLeftDelimeter = ""
		szRightDelimeter = ""
		if (not bFirst):
			if (nOr > 1):
				szLeftDelimeter = localText.getText("TXT_KEY_AND", ()) + "("
				szRightDelimeter = ") "
			elif (nOr > 0):
				szLeftDelimeter = localText.getText("TXT_KEY_AND", ())
		if len(szLeftDelimeter) > 0:
			screen.attachLabel(panelName, "", szLeftDelimeter)
		bFirst = True

		for j in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
			eBonus = gc.getUnitInfo(self.iUnit).getPrereqOrBonuses(j)
			if (eBonus > -1):
				if (not bFirst):
					screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
				else:
					bFirst = False
				screen.attachImageButton(panelName, "", gc.getBonusInfo(eBonus).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, eBonus, -1, False)
		if len(szRightDelimeter) > 0:
			screen.attachLabel(panelName, "", szRightDelimeter)

		iPrereq = gc.getUnitInfo(self.iUnit).getPrereqReligion()
		if (iPrereq >= 0):
			# <!-- custom: fix base advciv bug, replace WidgetTypes.WIDGET_HELP_RELIGION with WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION as is done already by base advciv and successfully in sevopedia building, anyways etc -->
			screen.attachImageButton(panelName, "", gc.getReligionInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereq, -1, False)

		iPrereq = gc.getUnitInfo(self.iUnit).getPrereqBuilding()
		if (iPrereq >= 0):
			screen.attachImageButton(panelName, "", gc.getBuildingInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iPrereq, -1, False)
		
		# Project requirements - New code for Manhattan Project and other projects
		unitInfo = gc.getUnitInfo(self.iUnit)
		iSpecialUnitType = unitInfo.getSpecialUnitType()
		# Find projects that require this special unit type
		projectsRequired = []
		# Check all projects to see if any enables this special unit
		if (iSpecialUnitType >= 0):
			for iProject in range(gc.getNumProjectInfos()):
				projectInfo = gc.getProjectInfo(iProject)
				if projectInfo.getEveryoneSpecialUnit() == iSpecialUnitType:
					projectsRequired.append(iProject)
		# Special hardcoded case for nukes and Manhattan Project since they might not be linked via XML
		if unitInfo.getNukeRange() > 0:  # If this is a nuclear unit (like ICBM)
			for iProject in range(gc.getNumProjectInfos()):
				projectInfo = gc.getProjectInfo(iProject)
				if "MANHATTAN_PROJECT" in projectInfo.getType():
					if iProject not in projectsRequired:
						projectsRequired.append(iProject)
					break
		# Display all project requirements with "OR" text between them
		bFirst = True
		for iProject in projectsRequired:
			if not bFirst:
				# Add "OR" text between projects
				screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
			
			screen.attachImageButton(panelName, "", gc.getProjectInfo(iProject).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, iProject, -1, False)
			bFirst = False
		
		bFirst = True



	def placeUpgradesTo(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()

		# Create panel with proper styling
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_UPGRADES_TO", ()), "", False, True, self.X_UPGRADES_TO, self.Y_UPGRADES_TO, self.W_UPGRADES_TO, self.H_UPGRADES_TO, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: additionnal left side padding for the button(s) -->
		screen.attachLabel(panelName, "", "  ")

		# <!-- custom: handle no unit found message -->
		isButtonFound = False

		iActivePlayer = gc.getGame().getActivePlayer() # advc.003l
		for k in range(gc.getNumUnitClassInfos()):
			if self.top.iActivePlayer == -1:
				eLoopUnit = gc.getUnitClassInfo(k).getDefaultUnitIndex()
			else:
				eLoopUnit = gc.getCivilizationInfo(gc.getGame().getActiveCivilizationType()).getCivilizationUnits(k)
			if (eLoopUnit >= 0 and gc.getUnitInfo(self.iUnit).getUpgradeUnitClass(k)):
				szButton = gc.getUnitInfo(eLoopUnit).getButton()
				# <advc.003l>
				if iActivePlayer >= 0:
					szButton = gc.getPlayer(iActivePlayer).getUnitButton(eLoopUnit)
				# </advc.003l>
				isButtonFound = True
				screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, eLoopUnit, 1, False)


		# If there's no <!-- custom: item --> to display, display "Nothing" <!-- custom: or similar anyways etc -->
		if not isButtonFound:
			textName = self.top.getNextWidgetName()
			szText = CyTranslator().getText("TXT_KEY_PEDIA_UPGRADES_TO_NO_BUTTON_FOUND", ())
			yCenterPanel = self.Y_UPGRADES_TO + (self.H_UPGRADES_TO / 2)
			screen.addMultilineText(textName, szText, self.X_UPGRADES_TO + 7, yCenterPanel, self.W_UPGRADES_TO - 14, self.H_UPGRADES_TO - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeFreePromotions(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		
		# Create panel with proper styling
		screen.addPanel(panelName, CyTranslator().getText("TXT_KEY_PEDIA_FREE_PROMOTIONS", ()), "", False, True, self.X_FREE, self.Y_FREE, self.W_FREE, self.H_FREE, PanelStyles.PANEL_STYLE_BLUE50)
		# Additional left side padding for the button(s)
		screen.attachLabel(panelName, "", "  ")
		
		# Get the unit info
		unitInfo = gc.getUnitInfo(self.iUnit)
		# Track if we found any free items to display
		isButtonFound = False
		
		# Check if the unit has any free promotions
		for iPromotion in range(gc.getNumPromotionInfos()):
			if unitInfo.getFreePromotions(iPromotion):
				isButtonFound = True
				# Attach promotion button
				screen.attachImageButton(
					panelName, "", 
					gc.getPromotionInfo(iPromotion).getButton(), 
					GenericButtonSizes.BUTTON_SIZE_CUSTOM, 
					WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, 
					iPromotion, -1, False
				)
		

		# If there's no <!-- custom: item --> to display, display "Nothing" <!-- custom: or similar anyways etc -->
		if not isButtonFound:
			textName = self.top.getNextWidgetName()
			szText = CyTranslator().getText("TXT_KEY_PEDIA_FREE_PROMOTIONS_NO_BUTTON_FOUND", ())
			yCenterPanel = self.Y_FREE + (self.H_FREE / 2)
			screen.addMultilineText(textName, szText, self.X_FREE + 7, yCenterPanel, self.W_FREE - 14, self.H_FREE - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def displayPanelButtonsSNumsOrTxtsOrPanelSTxtKeyNoButton(self, screen, isButtonFound, txtKeyNoButtonFound, xNumsOrTextsFound, buttonSize, xPanel, yPanel, wPanel, hPanel):
		# <!-- custom: now display(ing anyways etc) the corresponding num or text matching the button if any (button) anyways etc -->
		if isButtonFound:
			yPanelBottomPart = yPanel + int(0.8 * hPanel)
			for xOccurenceFound, numFreeTxtOccurenceFound in xNumsOrTextsFound:
				textName = self.top.getNextWidgetName()
				szText = numFreeTxtOccurenceFound
				screen.addMultilineText(textName, szText, xOccurenceFound, yPanelBottomPart, 2 * buttonSize, hPanel - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		# If no <!-- custom: button --> found, display a message
		else:
			yPanelCenter = yPanel + (hPanel / 2)
			textName = self.top.getNextWidgetName()
			szText = CyTranslator().getText(txtKeyNoButtonFound, ())
			screen.addMultilineText(textName, szText, xPanel + 7, yPanelCenter, wPanel - 14, hPanel - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeModifiersOfThisUnitAgainstOtherUnitClassesCombatTypes(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		
		# Create panel with proper styling
		screen.addPanel(panelName, CyTranslator().getText("TXT_KEY_PEDIA_OF_THIS_UNIT_MODIFIERS_AGAINST_OTHERS", ()), "", False, True, self.X_OF_UNIT_MODIFIERS_AGAINST_OTHERS, self.Y_OF_UNIT_MODIFIERS_AGAINST_OTHERS, self.W_OF_UNIT_MODIFIERS_AGAINST_OTHERS, self.H_OF_UNIT_MODIFIERS_AGAINST_OTHERS, PanelStyles.PANEL_STYLE_BLUE50)
		# Additional left side padding for the button(s)
		screen.attachLabel(panelName, "", "  ")
		
		nCountOccurencesFound = 0
		xNumsOrTextsFound = []
		buttonSize = 64

		# Get the unit info
		unitInfo = gc.getUnitInfo(self.iUnit)

		# Check for UnitClassAttackMods
		for i in range(gc.getNumUnitClassInfos()):
			iMod = unitInfo.getUnitClassAttackModifier(i)
			if iMod != 0:
				nCountOccurencesFound += 1
				numTxt = u"A%+d%%" % (iMod)  # Use %+d to always show the sign (+ or -)
				addedOffset = 0
				xSubstractedAdjustmentNumTxt = getXSubstractedAdjustmentNumTxtBasedOnLenNumTxt(numTxt, addedOffset, buttonSize)
				xSubstractedAdjustment = int(xSubstractedAdjustmentNumTxt * buttonSize)
				xPanel = self.X_OF_UNIT_MODIFIERS_AGAINST_OTHERS
				xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numTxt))
				
				# Get the default unit of this class for the current civilization
				if self.top.iActivePlayer != -1:
					iDefaultUnit = gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationUnits(i)
				else:
					iDefaultUnit = gc.getUnitClassInfo(i).getDefaultUnitIndex()
				
				# If a valid unit exists, display its button
				if iDefaultUnit != -1:
					screen.attachImageButton(panelName, "", gc.getUnitInfo(iDefaultUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iDefaultUnit, -1, False)
		
		# Check for UnitClassDefenseMods
		for i in range(gc.getNumUnitClassInfos()):
			iMod = unitInfo.getUnitClassDefenseModifier(i)
			if iMod != 0:
				nCountOccurencesFound += 1
				numTxt = u"D%+d%%" % (iMod)  # Use %+d to always show the sign (+ or -)
				addedOffset = 0
				xSubstractedAdjustmentNumTxt = getXSubstractedAdjustmentNumTxtBasedOnLenNumTxt(numTxt, addedOffset, buttonSize)
				xSubstractedAdjustment = int(xSubstractedAdjustmentNumTxt * buttonSize)
				xPanel = self.X_OF_UNIT_MODIFIERS_AGAINST_OTHERS
				xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numTxt))
				
				# Get the default unit of this class for the current civilization
				if self.top.iActivePlayer != -1:
					iDefaultUnit = gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationUnits(i)
				else:
					iDefaultUnit = gc.getUnitClassInfo(i).getDefaultUnitIndex()
				
				# If a valid unit exists, display its button
				if iDefaultUnit != -1:
					screen.attachImageButton(panelName, "", gc.getUnitInfo(iDefaultUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iDefaultUnit, -1, False)
		
		# Check for UnitCombatMods
		for i in range(gc.getNumUnitCombatInfos()):
			iMod = unitInfo.getUnitCombatModifier(i)
			if iMod != 0:			
				nCountOccurencesFound += 1
				numTxt = u"%+d%%" % (iMod)  # Use %+d to always show the sign (+ or -)
				addedOffset = 0
				xSubstractedAdjustmentNumTxt = getXSubstractedAdjustmentNumTxtBasedOnLenNumTxt(numTxt, addedOffset, buttonSize)
				xSubstractedAdjustment = int(xSubstractedAdjustmentNumTxt * buttonSize)
				xPanel = self.X_OF_UNIT_MODIFIERS_AGAINST_OTHERS
				xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numTxt))
				
				# Display the combat type button
				screen.attachImageButton(panelName, "", gc.getUnitCombatInfo(i).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, i, -1, False)
		
		isButtonFound = (nCountOccurencesFound > 0)
		txtKeyNoButtonFound = "TXT_KEY_PEDIA_OF_THIS_UNIT_MODIFIERS_AGAINST_OTHERS_NO_BUTTON_FOUND"
		self.displayPanelButtonsSNumsOrTxtsOrPanelSTxtKeyNoButton(screen, isButtonFound, txtKeyNoButtonFound, xNumsOrTextsFound, buttonSize, self.X_OF_UNIT_MODIFIERS_AGAINST_OTHERS, self.Y_OF_UNIT_MODIFIERS_AGAINST_OTHERS, self.W_OF_UNIT_MODIFIERS_AGAINST_OTHERS, self.H_OF_UNIT_MODIFIERS_AGAINST_OTHERS)



	def placeModifiersOfOtherUnitClassesCombatTypesAgainstThisUnit(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		
		# Create panel with proper styling
		screen.addPanel(panelName, CyTranslator().getText("TXT_KEY_PEDIA_OF_OTHER_UNITS_MODIFIERS_AGAINST_THIS_UNIT", ()), "", False, True, self.X_OF_OTHER_UNITS_MODIFIERS, self.Y_OF_OTHER_UNITS_MODIFIERS, self.W_OF_OTHER_UNITS_MODIFIERS, self.H_OF_OTHER_UNITS_MODIFIERS, PanelStyles.PANEL_STYLE_BLUE50)
		# Additional left side padding for the button(s)
		screen.attachLabel(panelName, "", "  ")
		
		nCountOccurencesFound = 0
		xNumsOrTextsFound = []
		buttonSize = 64

		# Get the unit info for the current unit
		unitInfo = gc.getUnitInfo(self.iUnit)
		iUnitClass = unitInfo.getUnitClassType()
		iUnitCombatType = unitInfo.getUnitCombatType()
		
		# Loop through all unit types to find those with UnitClassAttackMods against our unit class
		for i in range(gc.getNumUnitInfos()):
			otherUnitInfo = gc.getUnitInfo(i)
			iMod = otherUnitInfo.getUnitClassAttackModifier(iUnitClass)
			
			if iMod != 0:
				nCountOccurencesFound += 1
				numTxt = u"A%+d%%" % (iMod)  # Use %+d to always show the sign (+ or -)
				addedOffset = 0
				xSubstractedAdjustmentNumTxt = getXSubstractedAdjustmentNumTxtBasedOnLenNumTxt(numTxt, addedOffset, buttonSize)
				xSubstractedAdjustment = int(xSubstractedAdjustmentNumTxt * buttonSize)
				xPanel = self.X_OF_OTHER_UNITS_MODIFIERS
				xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numTxt))
				
				# Display the specific unit button
				screen.attachImageButton(panelName, "", otherUnitInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, i, -1, False)
		
		# Loop through all unit types to find those with UnitClassDefenseMods against our unit class
		for i in range(gc.getNumUnitInfos()):
			otherUnitInfo = gc.getUnitInfo(i)
			iMod = otherUnitInfo.getUnitClassDefenseModifier(iUnitClass)
			
			if iMod != 0:
				nCountOccurencesFound += 1
				numTxt = u"D%+d%%" % (iMod)  # Use %+d to always show the sign (+ or -)
				addedOffset = 0
				xSubstractedAdjustmentNumTxt = getXSubstractedAdjustmentNumTxtBasedOnLenNumTxt(numTxt, addedOffset, buttonSize)
				xSubstractedAdjustment = int(xSubstractedAdjustmentNumTxt * buttonSize)
				xPanel = self.X_OF_OTHER_UNITS_MODIFIERS
				xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numTxt))
				
				# Display the specific unit button
				screen.attachImageButton(panelName, "", otherUnitInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, i, -1, False)
		
		# Check for unit combat types that this unit belongs to
		if iUnitCombatType != -1:  # Make sure this unit has a combat type
			# Loop through all units to find those with UnitCombatMods against this combat type
			for i in range(gc.getNumUnitInfos()):
				otherUnitInfo = gc.getUnitInfo(i)
				iMod = otherUnitInfo.getUnitCombatModifier(iUnitCombatType)
				
				if iMod != 0:
					nCountOccurencesFound += 1
					numTxt = u"%+d%%" % (iMod)  # Use %+d to always show the sign (+ or -)
					addedOffset = 0
					xSubstractedAdjustmentNumTxt = getXSubstractedAdjustmentNumTxtBasedOnLenNumTxt(numTxt, addedOffset, buttonSize)
					xSubstractedAdjustment = int(xSubstractedAdjustmentNumTxt * buttonSize)
					xPanel = self.X_OF_OTHER_UNITS_MODIFIERS
					xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numTxt))
					
					# Display the specific unit button
					screen.attachImageButton(panelName, "", otherUnitInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, i, -1, False)
		
		isButtonFound = (nCountOccurencesFound > 0)
		txtKeyNoButtonFound = "TXT_KEY_PEDIA_OF_OTHER_UNITS_MODIFIERS_AGAINST_THIS_UNIT_NO_BUTTON_FOUND"
		self.displayPanelButtonsSNumsOrTxtsOrPanelSTxtKeyNoButton(screen, isButtonFound, txtKeyNoButtonFound, xNumsOrTextsFound, buttonSize, self.X_OF_OTHER_UNITS_MODIFIERS, self.Y_OF_OTHER_UNITS_MODIFIERS, self.W_OF_OTHER_UNITS_MODIFIERS, self.H_OF_OTHER_UNITS_MODIFIERS)



	def placePeakHillCityTerrainsFeaturesModifiers(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		
		# Create panel with proper styling
		screen.addPanel(panelName, CyTranslator().getText("TXT_KEY_PEDIA_PEAK_HILL_CITY_TERRAINS_FEATURES_MODIFIERS", ()), "", False, True, 
					self.X_TERRAIN_FEATURE_CITY_BONUSES, self.Y_TERRAIN_FEATURE_CITY_BONUSES, 
					self.W_TERRAIN_FEATURE_CITY_BONUSES, self.H_TERRAIN_FEATURE_CITY_BONUSES, 
					PanelStyles.PANEL_STYLE_BLUE50)
		
		# Additional left side padding for the button(s)
		screen.attachLabel(panelName, "", "  ")
		
		nCountOccurencesFound = 0
		xNumsOrTextsFound = []
		buttonSize = 64
		
		# Get the unit info
		unitInfo = gc.getUnitInfo(self.iUnit)
		
		# Dictionary to store combined bonuses: key is (type, buttonArt, description, jumpType, widgetID1, widgetID2)
		# value is a tuple of (attackBonus, defenseBonus)
		combinedBonuses = {}
		
		# Special cases for Hills and City
		hillsButton = ""
		hillsDescription = CyTranslator().getText("TXT_KEY_TERRAIN_HILL", ())

		citiesConfigButtonPathSTxtKey = "TXT_KEY_BUTTON_PATH_HARDCODED_CITIES_BUTTON_PATH"
		# <!-- custom: add str() wrapper else (i.e. without it anyways etc) we get an error (it seems) (but anyways etc) anyways (i.e. not impliying it is necessary, but without it we get this error with this other kind of button writing code that does not use same logic as the add as <img> one of other buttons anyways etc (from err log anyways etc):
		#
		# ArgumentError: Python argument types in
		#	CyGInterfaceScreen.attachImageButton(CyGInterfaceScreen, str, str, unicode, CvPythonExtensions.GenericButtonSizes, CvPythonExtensions.WidgetTypes, CvPythonExtensions.CivilopediaPageTypes, int, bool)
		# did not match C++ signature:
		#	attachImageButton(class CyGInterfaceScreen {lvalue}, char const *, char const *, char const *, enum GenericButtonSizes, enum WidgetTypes, int, int, bool)
		#  
		# (adding the str) may or may not be necessary or an alternative solution to this may exist or not, but in all cases anyways etc) anyways etc, etc
		# -->

		citiesResolvedButtonPath = str(CyTranslator().getText(citiesConfigButtonPathSTxtKey, ()))
		citiesButtonHeader = "Cities button in Sevopedia Unit's placePeakHillCityTerrainsFeaturesModifiers"
		check_button_path_is_valid(citiesButtonHeader, citiesResolvedButtonPath, citiesConfigButtonPathSTxtKey)	
		citiesDescription = CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ())
		
		# Try to find a hills button from the terrain infos
		for i in range(gc.getNumTerrainInfos()):
			terrainInfo = gc.getTerrainInfo(i)
			if "HILL" in terrainInfo.getType():
				hillsButton = terrainInfo.getButton()
				break
		
		# Find the concept ID for "CONCEPT_CITIES"
		iCitiesConceptID = -1
		for i in range(gc.getNumConceptInfos()):
			if gc.getConceptInfo(i).getType() == "CONCEPT_CITIES":
				iCitiesConceptID = i
				break
		
		# Hills bonuses
		iHillsAttack = unitInfo.getHillsAttackModifier()
		iHillsDefense = unitInfo.getHillsDefenseModifier()
		if iHillsAttack > 0 or iHillsDefense > 0:
			hillsTerrainID = -1
			for i in range(gc.getNumTerrainInfos()):
				if "HILL" in gc.getTerrainInfo(i).getType():
					hillsTerrainID = i
					break
			
			key = ("HILLS", hillsButton, hillsDescription, "HILLS", hillsTerrainID, -1)
			combinedBonuses[key] = (iHillsAttack, iHillsDefense)
		
		# City bonuses
		iCityAttack = unitInfo.getCityAttackModifier()
		iCityDefense = unitInfo.getCityDefenseModifier()
		if iCityAttack > 0 or iCityDefense > 0:
			# Use Widget_Pedia_Description with the concept ID
			if iCitiesConceptID != -1:
				key = ("CITY", citiesResolvedButtonPath, citiesDescription, "CONCEPT", CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT, iCitiesConceptID)
			else:
				key = ("CITY", citiesResolvedButtonPath, citiesDescription, "NONE", -1, -1)
			combinedBonuses[key] = (iCityAttack, iCityDefense)
		
		# Terrain Attack/Defense bonuses
		for i in range(gc.getNumTerrainInfos()):
			terrainInfo = gc.getTerrainInfo(i)
			terrainType = terrainInfo.getType()
			
			iTerrainAttack = unitInfo.getTerrainAttackModifier(i)
			iTerrainDefense = unitInfo.getTerrainDefenseModifier(i)
			
			if iTerrainAttack > 0 or iTerrainDefense > 0:
				key = (terrainType, terrainInfo.getButton(), terrainInfo.getDescription(), "TERRAIN", i, -1)
				combinedBonuses[key] = (iTerrainAttack, iTerrainDefense)
		
		# Feature Attack/Defense bonuses
		for i in range(gc.getNumFeatureInfos()):
			featureInfo = gc.getFeatureInfo(i)
			featureType = featureInfo.getType()
			
			iFeatureAttack = unitInfo.getFeatureAttackModifier(i)
			iFeatureDefense = unitInfo.getFeatureDefenseModifier(i)
			
			if iFeatureAttack > 0 or iFeatureDefense > 0:
				key = (featureType, featureInfo.getButton(), featureInfo.getDescription(), "FEATURE", i, -1)
				combinedBonuses[key] = (iFeatureAttack, iFeatureDefense)
		
		# Now process all the combined bonuses we found and display them
		for (bonusType, buttonArt, description, jumpType, widgetID1, widgetID2), (attackBonus, defenseBonus) in combinedBonuses.items():
			nCountOccurencesFound += 1
			
			# Create the combined bonus text
			numTxt = ""
			if attackBonus > 0 and defenseBonus > 0:
				numTxt = "%+d/%+d" % (attackBonus, defenseBonus)
			elif attackBonus > 0:
				numTxt = "%+d/__" % attackBonus
			elif defenseBonus > 0:
				numTxt = "__/%+d" % defenseBonus
			
			# Calculate text position offset
			addedOffset = -0.07
			xSubstractedAdjustmentNumTxt = getXSubstractedAdjustmentNumTxtBasedOnLenNumTxt(numTxt, addedOffset, buttonSize)
			xSubstractedAdjustment = int(xSubstractedAdjustmentNumTxt * buttonSize)
			
			# Add text position to our list
			xPanel = self.X_TERRAIN_FEATURE_CITY_BONUSES
			xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numTxt))
			
			# Determine widget type based on the jumpType
			widgetType = WidgetTypes.WIDGET_GENERAL
			
			if jumpType == "TERRAIN":
				widgetType = WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN
				screen.attachImageButton(panelName, "", buttonArt, GenericButtonSizes.BUTTON_SIZE_CUSTOM, 
									widgetType, widgetID1, -1, False)
			elif jumpType == "FEATURE":
				widgetType = WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE
				screen.attachImageButton(panelName, "", buttonArt, GenericButtonSizes.BUTTON_SIZE_CUSTOM, 
									widgetType, widgetID1, -1, False)
			elif jumpType == "HILLS":
				widgetType = WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN
				screen.attachImageButton(panelName, "", buttonArt, GenericButtonSizes.BUTTON_SIZE_CUSTOM, 
									widgetType, widgetID1, -1, False)
			elif jumpType == "CONCEPT":
				# For concepts, use WIDGET_PEDIA_DESCRIPTION with proper page type and ID
				widgetType = WidgetTypes.WIDGET_PEDIA_DESCRIPTION
				screen.attachImageButton(panelName, "", buttonArt, GenericButtonSizes.BUTTON_SIZE_CUSTOM, 
									widgetType, widgetID1, widgetID2, False)
			else:
				# Default to WIDGET_GENERAL with no click action
				screen.attachImageButton(panelName, "", buttonArt, GenericButtonSizes.BUTTON_SIZE_CUSTOM, 
									widgetType, -1, -1, False)
		
		# Display the bonus texts or "no bonuses" message
		isButtonFound = (nCountOccurencesFound > 0)
		txtKeyNoButtonFound = "TXT_KEY_PEDIA_PEAK_HILL_CITY_TERRAINS_FEATURES_MODIFIERS_NO_BUTTON_FOUND"
		self.displayPanelButtonsSNumsOrTxtsOrPanelSTxtKeyNoButton(screen, isButtonFound, txtKeyNoButtonFound, xNumsOrTextsFound, buttonSize, self.X_TERRAIN_FEATURE_CITY_BONUSES, self.Y_TERRAIN_FEATURE_CITY_BONUSES, self.W_TERRAIN_FEATURE_CITY_BONUSES, self.H_TERRAIN_FEATURE_CITY_BONUSES)



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getUnitHelp(self.iUnit, True, False, False, None)[1:]
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL+5, self.Y_SPECIAL+30, self.W_SPECIAL-10, self.H_SPECIAL-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeUnitAnimation(self):
		screen = self.top.getScreen()
		screen.addUnitGraphicGFC(self.top.getNextWidgetName(), self.iUnit, self.X_UNIT_ANIMATION, self.Y_UNIT_ANIMATION, self.W_UNIT_ANIMATION, self.H_UNIT_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_UNIT_ANIMATION, self.Z_ROTATION_UNIT_ANIMATION, self.SCALE_ANIMATION, True)



	def placeReplace(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()

		iUnitClass = gc.getUnitInfo(self.iUnit).getUnitClassType()
		iBaseUnit = gc.getUnitClassInfo(iUnitClass).getDefaultUnitIndex()

		# Use different text key depending on whether this is a unique or base unit
		if self.iUnit != iBaseUnit:
			# This is a unique unit that replaces a base unit
			panelTxtKey = "TXT_KEY_PEDIA_REPLACE_REPLACES_CUSTOM"
		else:
			# This is a base unit that can be replaced by unique units
			panelTxtKey = "TXT_KEY_PEDIA_REPLACE_REPLACED_BY_CUSTOM"

		# Create panel with proper styling
		screen.addPanel(panel, CyTranslator().getText(panelTxtKey, ()), "", False, True, self.X_REPLACE, self.Y_REPLACE, self.W_REPLACE, self.H_REPLACE, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: additionnal left side padding for the button(s) -->
		screen.attachLabel(panel, "", "  ")

		# <!-- custom: handle no unit found message -->
		isButtonFound = False

		# If this is a unique (i.e.civ-specific) unit, show the base unit it replaces
		if self.iUnit != iBaseUnit:
			isButtonFound = True
			screen.attachImageButton(panel, "", gc.getUnitInfo(iBaseUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iBaseUnit, 1, False)
			return
		
		else:
			# If this is the base building, show all unique (i.e.civ-specific) buildings that replace it
			for iUnit in xrange(gc.getNumUnitInfos()):
				if self.iUnit != iUnit and not gc.getUnitInfo(iUnit).isGraphicalOnly():
					if iUnitClass == gc.getUnitInfo(iUnit).getUnitClassType():
						isButtonFound = True
						screen.attachImageButton(panel, "", gc.getUnitInfo(iUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

		if not isButtonFound:
			## If there's no replace (replaced by or/nor replaces anyways etc), display "Nothing" or similar anyways etc
			textName = self.top.getNextWidgetName()
			szText = CyTranslator().getText("TXT_KEY_PEDIA_REPLACE_NO_BUTTON_FOUND", ())
			yCenterPanel = self.Y_REPLACE + (self.H_REPLACE / 2)
			screen.addMultilineText(textName, szText, self.X_REPLACE + 7, yCenterPanel, self.W_REPLACE - 14, self.H_REPLACE - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: note: this sevopediaunit's below placeCivilizations function/method can handle several civs if i am not mistaken, see sevopedia building's placeCivilizations's code comment for details -->
	def placeCivilizations(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		
		# Create panel with proper styling
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_CIVILIZATIONS", ()), "", False, True, self.X_CIVILIZATIONS, self.Y_CIVILIZATIONS, self.W_CIVILIZATIONS, self.H_CIVILIZATIONS, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: additionnal left side padding for the button(s) -->
		screen.attachLabel(panelName, "", "  ")
		
		# Get unit class info
		iUnitClass = gc.getUnitInfo(self.iUnit).getUnitClassType()
		iDefaultUnit = gc.getUnitClassInfo(iUnitClass).getDefaultUnitIndex()
		
		# Check if this is a unique (i.e.civ-specific) unit (not the default unit for its class)
		bIsUnique = (self.iUnit != iDefaultUnit)
		
		# If this is a unique (i.e.civ-specific) unit, show which civ can build it
		if bIsUnique:
			# Find which civ has this unique (i.e.civ-specific) unit
			for iCiv in range(gc.getNumCivilizationInfos()):
				# <!-- custom: include barbarian and perhaps other non playable civs in the display for example for the/to display the anyways etc barbarian palace, barbarian granary (so comment out the isPlayable check as Claude AI explained indeed and that i implemented in a simpler manner thanks to its explanation but anyways etc, but also unindent the below below too anyways etc), or/and other civs or not if such exist or not or and other or yes or and not or yes but anyways etc -->
				#if gc.getCivilizationInfo(iCiv).isPlayable():
				iCivUnit = gc.getCivilizationInfo(iCiv).getCivilizationUnits(iUnitClass)
				if iCivUnit == self.iUnit:
					screen.attachImageButton(panelName, "", gc.getCivilizationInfo(iCiv).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCiv, -1, False)
		# If this is the default unit, show "Available to all civilizations"
		else:
			# <!-- custom: prettier display -->
			#screen.attachLabel(panelName, "", localText.getText("TXT_KEY_PEDIA_CIVILIZATIONS_NO_BUTTON_FOUND", ()))
			textName = self.top.getNextWidgetName()
			szText = localText.getText("TXT_KEY_PEDIA_CIVILIZATIONS_NO_BUTTON_FOUND", ())
			yCenterPanel = self.Y_CIVILIZATIONS + (self.H_CIVILIZATIONS / 2)
			screen.addMultilineText(textName, szText, self.X_CIVILIZATIONS + 7, yCenterPanel, self.W_CIVILIZATIONS - 14, self.H_CIVILIZATIONS - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: i don't need the "History:" in TXT_KEY_CIVILOPEDIA_HISTORY, is redundant with background
		# that is already about the unit's background -->
		screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		textName = self.top.getNextWidgetName()
		szText = u""
		# <!-- custom: same reasoning as for TXT_KEY_CIVILOPEDIA_STRATEGY
		# in SevoPediaBuilding.py (refer to this file for details),
		# removing (hiding) the entry entirely from the sevopedia.
		# -->
		#if len(gc.getUnitInfo(self.iUnit).getStrategy()) > 0:
		#	szText += localText.getText("TXT_KEY_CIVILOPEDIA_STRATEGY", ())
		#	szText += gc.getUnitInfo(self.iUnit).getStrategy()
		#	szText += u"\n\n"
		# <!-- custom: i don't need the background: tag either, a box being there
		# is explicit enough, clearer, prettier, and more efficient i think.
		# -->
		#szText += localText.getText("TXT_KEY_CIVILOPEDIA_BACKGROUND", ())
		szText += gc.getUnitInfo(self.iUnit).getCivilopedia()
		# <!-- custom: fix height too low, does not display properly the concept texts
		# (for example any religious missionary unit)
		# -->
		#screen.addMultilineText(textName, szText, self.X_HISTORY + 15, self.Y_HISTORY + 40, self.W_HISTORY - (15 * 2), self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		#screen.addMultilineText(textName, szText, self.X_HISTORY + 7 , self.Y_HISTORY + 10, self.W_HISTORY - (15 * 2), self.H_HISTORY - (15 * 2) - 25 + 41, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(textName, szText, self.X_HISTORY + 7, self.Y_HISTORY + 10 + self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER, self.W_HISTORY - 30, self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placePromotions(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: no TXT_KEY_PEDIA_CATEGORY_PROMOTION "header" for smoother display with how the unit pane is done (and promo pane is next to it now anyways etc) -->
		screen.addPanel(panelName, localText.getText("", ()), "", True, True, self.X_PROMO_PANE, self.Y_PROMO_PANE, self.W_PROMO_PANE, self.H_PROMO_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		rowListName = self.top.getNextWidgetName()
		screen.addMultiListControlGFC(rowListName, "", self.X_PROMO_PANE+15, self.Y_PROMO_PANE+40, self.W_PROMO_PANE-20, self.H_PROMO_PANE-40, 1, self.PROMOTION_ICON_SIZE, self.PROMOTION_ICON_SIZE, TableStyles.TABLE_STYLE_STANDARD)
		for k in range(gc.getNumPromotionInfos()):
			if (isPromotionValid(k, self.iUnit, False) and not gc.getPromotionInfo(k).isGraphicalOnly()):
				screen.appendMultiListButton(rowListName, gc.getPromotionInfo(k).getButton(), 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, k, -1, False)



	def handleInput (self, inputClass):
		return 0

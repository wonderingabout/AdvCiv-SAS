# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
#
# <!-- custom: part of the code here (placeReplacedBy (renamed from placeReplacements of: ) in particular, but not exhaustive or maybe exhaustive or not, anyways, is imported from RFC DOC mod:
# C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\RFC Dawn of Civilization\Assets\Python\Pedia\CvPediaUnit.py
# which may be modified or not for AdvCiv-SAS
#
# <!-- custom: new placeExclusiveCivs added entirely (i only tweaked the coordinates to suit/match where i want(ed?) it anyways etc) by Claude AI from my prompt anyways etc, now we have buttons for the civ(s) that can build a unit, and no button at all if all civs can build the currently selected unit (to not clutter the display needlessly with all civs buttons and is also clearer to know immediately that all can build it with the panel being empty), thanks a lot Claude AI! Anyways etc anyways etc anyways etc... -->
# -->

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums

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
		self.W_UNIT_PANE = (self.top.R_PEDIA_PAGE - self.X_UNIT_PANE) / 4
		self.H_UNIT_PANE = 190

		# <!-- custom: no margins to merge edges with unit pane for nicer display maybe i mean anyways etc -->
		# <!-- custom: merge effect by partially joining their borders, i accidentally found or/and maybe got the idea and looks very nice, just is slightly not centered maybe fixable or not but and in all cases anyways etc anyways etc -->
		self.X_PROMO_PANE = self.X_UNIT_PANE + self.W_UNIT_PANE - 5
		self.Y_PROMO_PANE = self.Y_UNIT_PANE
		self.W_PROMO_PANE = self.W_UNIT_PANE + 5
		self.H_PROMO_PANE = self.H_UNIT_PANE

		# advc.004y: Move the button and icon size settings up
		self.ICON_SIZE = 64
		# <advc.004y> Perhaps better not to enlarge the icon; use one size everyhwere in the game.
		#if bWideScreen:
		#	self.ICON_SIZE = 96 # </advc.004y>
		self.BUTTON_SIZE = 64
		self.PROMOTION_ICON_SIZE = 32

		# <advc.004y> ICON_SIZE as lower bound for icon frame
		iIconFrameSize = max(100, self.ICON_SIZE)
		self.W_ICON = iIconFrameSize # was 100
		self.H_ICON = iIconFrameSize # was 100
		# Divisor was 2; don't want the button to touch the unit stats.
		self.X_ICON = self.X_UNIT_PANE + (self.H_UNIT_PANE - self.H_ICON) / 4
		# </advc.004y>
		self.Y_ICON = self.Y_UNIT_PANE + (self.H_UNIT_PANE - self.H_ICON) / 2

		self.X_STATS_PANE = self.X_UNIT_PANE + 130
		self.Y_STATS_PANE = self.Y_UNIT_PANE + 42
		self.W_STATS_PANE = 250
		self.H_STATS_PANE = 200

		self.X_PREREQ_PANE = self.X_UNIT_PANE
		self.Y_PREREQ_PANE = self.Y_UNIT_PANE + self.H_UNIT_PANE + self.SMALL_MARGIN
		self.W_PREREQ_PANE = self.W_UNIT_PANE * 2
		self.H_PREREQ_PANE = 110

		self.X_REPLACED_BY = self.X_PREREQ_PANE
		self.Y_REPLACED_BY = self.Y_PREREQ_PANE + self.H_PREREQ_PANE + self.SMALL_MARGIN
		self.W_REPLACED_BY = self.W_PREREQ_PANE
		self.H_REPLACED_BY = self.H_PREREQ_PANE

		self.X_UPGRADES_TO_PANE = self.X_PREREQ_PANE
		self.Y_UPGRADES_TO_PANE = self.Y_REPLACED_BY + self.H_REPLACED_BY + self.SMALL_MARGIN
		self.W_UPGRADES_TO_PANE = self.W_PREREQ_PANE
		self.H_UPGRADES_TO_PANE = self.H_PREREQ_PANE

		self.X_SPECIAL_PANE = self.X_UNIT_PANE
		self.Y_SPECIAL_PANE = self.Y_UPGRADES_TO_PANE + self.H_UPGRADES_TO_PANE + self.SMALL_MARGIN
		self.W_SPECIAL_PANE = self.W_PREREQ_PANE
		self.H_SPECIAL_PANE = self.top.B_PEDIA_PAGE - self.Y_SPECIAL_PANE

		self.X_UNIT_ANIMATION = self.X_UNIT_PANE + self.W_SPECIAL_PANE + self.MEDIUM_MARGIN
		self.Y_UNIT_ANIMATION = self.Y_UNIT_PANE + 7
		self.W_UNIT_ANIMATION = (self.top.R_PEDIA_PAGE - self.X_UNIT_PANE) / 2
		self.H_UNIT_ANIMATION = self.H_UNIT_PANE + self.SMALL_MARGIN + self.H_PREREQ_PANE + self.SMALL_MARGIN + self.H_REPLACED_BY - 7

		self.X_EXCLUSIVE_CIVS = self.X_UPGRADES_TO_PANE + self.W_UPGRADES_TO_PANE + self.MEDIUM_MARGIN
		self.Y_EXCLUSIVE_CIVS = self.Y_UPGRADES_TO_PANE
		self.W_EXCLUSIVE_CIVS = self.W_UPGRADES_TO_PANE
		self.H_EXCLUSIVE_CIVS = self.H_UPGRADES_TO_PANE

		self.X_ROTATION_UNIT_ANIMATION = -20
		self.Z_ROTATION_UNIT_ANIMATION = 30
		self.SCALE_ANIMATION = 1.0

		self.X_HISTORY_PANE = self.X_UNIT_ANIMATION
		self.Y_HISTORY_PANE = self.Y_EXCLUSIVE_CIVS + self.H_EXCLUSIVE_CIVS + self.MEDIUM_MARGIN + 17
		self.W_HISTORY_PANE = self.W_UNIT_ANIMATION
		self.H_HISTORY_PANE = self.top.B_PEDIA_PAGE - self.Y_HISTORY_PANE



	def interfaceScreen(self, iUnit):
		self.iUnit = iUnit
		screen = self.top.getScreen()

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_UNIT_PANE, self.Y_UNIT_PANE, self.W_UNIT_PANE, self.H_UNIT_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		szButton = gc.getUnitInfo(self.iUnit).getButton()
		# <advc.003l>
		iActivePlayer = gc.getGame().getActivePlayer()
		if iActivePlayer >= 0:
			szButton = gc.getPlayer(iActivePlayer).getUnitButton(self.iUnit)
		# </advc.003l>
		screen.addDDSGFC(self.top.getNextWidgetName(), szButton, self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addUnitGraphicGFC(self.top.getNextWidgetName(), self.iUnit, self.X_UNIT_ANIMATION, self.Y_UNIT_ANIMATION, self.W_UNIT_ANIMATION, self.H_UNIT_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_UNIT_ANIMATION, self.Z_ROTATION_UNIT_ANIMATION, self.SCALE_ANIMATION, True)

		self.placeStats()
		self.placePromotions()
		self.placeRequires()
		self.placeReplacedBy()
		self.placeUpgradesTo()
		self.placeExclusiveCivs()
		self.placeSpecial()
		self.placeHistory()



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
			# 4 move helicopter, (hoepfully helpful ,) (but) (if or not)(anyways etc) anyways etc -->
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
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_PREREQ_PANE, self.Y_PREREQ_PANE, self.W_PREREQ_PANE, self.H_PREREQ_PANE, PanelStyles.PANEL_STYLE_BLUE50)
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
			screen.attachImageButton(panelName, "", gc.getReligionInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_HELP_RELIGION, iPrereq, -1, False)
		iPrereq = gc.getUnitInfo(self.iUnit).getPrereqBuilding()
		if (iPrereq >= 0):
			screen.attachImageButton(panelName, "", gc.getBuildingInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iPrereq, -1, False)



	def placeReplacedBy(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		screen.addPanel(panel, CyTranslator().getText("TXT_KEY_PEDIA_REPLACED_BY_CUSTOM", ()), "", False, True, self.X_REPLACED_BY, self.Y_REPLACED_BY, self.W_REPLACED_BY, self.H_REPLACED_BY, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")
		
		iUnitClass = gc.getUnitInfo(self.iUnit).getUnitClassType()
		iBaseUnit = gc.getUnitClassInfo(iUnitClass).getDefaultUnitIndex()
		
		if self.iUnit != iBaseUnit:
			screen.attachImageButton(panel, "", gc.getUnitInfo(iBaseUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iBaseUnit, 1, False)
			return
		
		for iUnit in xrange(gc.getNumUnitInfos()):
			if self.iUnit != iUnit and not gc.getUnitInfo(iUnit).isGraphicalOnly():
				if iUnitClass == gc.getUnitInfo(iUnit).getUnitClassType():
					screen.attachImageButton(panel, "", gc.getUnitInfo(iUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)



	def placeUpgradesTo(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_UPGRADES_TO", ()), "", False, True, self.X_UPGRADES_TO_PANE, self.Y_UPGRADES_TO_PANE, self.W_UPGRADES_TO_PANE, self.H_UPGRADES_TO_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
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
				screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, eLoopUnit, 1, False)



	def placeExclusiveCivs(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		
		# Create panel
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_EXCLUSIVE_CIVS", ()), "", False, True, 
					self.X_EXCLUSIVE_CIVS, self.Y_EXCLUSIVE_CIVS, 
					self.W_EXCLUSIVE_CIVS, self.H_EXCLUSIVE_CIVS, PanelStyles.PANEL_STYLE_BLUE50)
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
				if gc.getCivilizationInfo(iCiv).isPlayable():
					iCivUnit = gc.getCivilizationInfo(iCiv).getCivilizationUnits(iUnitClass)
					if iCivUnit == self.iUnit:
						screen.attachImageButton(panelName, "", gc.getCivilizationInfo(iCiv).getButton(), 
											GenericButtonSizes.BUTTON_SIZE_CUSTOM, 
											WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCiv, -1, False)
		# If this is the default unit, show "Available to all civilizations"
		else:
			screen.attachLabel(panelName, "", 
							localText.getText("TXT_KEY_PEDIA_AVAILABLE_ALL_CIVS", ()))



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", True, False, self.X_SPECIAL_PANE, self.Y_SPECIAL_PANE, self.W_SPECIAL_PANE, self.H_SPECIAL_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getUnitHelp(self.iUnit, True, False, False, None)[1:]
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL_PANE+5, self.Y_SPECIAL_PANE+30, self.W_SPECIAL_PANE-10, self.H_SPECIAL_PANE-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: i don't need the "History:", is redundant with background
		# that is already about the unit's background -->
		#screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY_PANE, self.Y_HISTORY_PANE, self.W_HISTORY_PANE, self.H_HISTORY_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(panelName, "", "", True, True, self.X_HISTORY_PANE, self.Y_HISTORY_PANE, self.W_HISTORY_PANE, self.H_HISTORY_PANE, PanelStyles.PANEL_STYLE_BLUE50)
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
		# <!-- custom: i don't need the "History:", is redundant with background
		# that is already about the unit's background -->
		# <!-- custom: fix height too low, does not display properly the concept texts
		# (for example any religious missionary unit)
		# -->
		#screen.addMultilineText(textName, szText, self.X_HISTORY_PANE + 15, self.Y_HISTORY_PANE + 40, self.W_HISTORY_PANE - (15 * 2), self.H_HISTORY_PANE - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(textName, szText, self.X_HISTORY_PANE + 7 , self.Y_HISTORY_PANE + 10, self.W_HISTORY_PANE - (15 * 2), self.H_HISTORY_PANE - (15 * 2) - 25 + 41, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		

	def placePromotions(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: no "header" for smoother display with how the unit pane is done (and promo pane is next to it now anyways etc) -->
		# screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION", ()), "", True, True, self.X_PROMO_PANE, self.Y_PROMO_PANE, self.W_PROMO_PANE, self.H_PROMO_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(panelName, localText.getText("", ()), "", True, True, self.X_PROMO_PANE, self.Y_PROMO_PANE, self.W_PROMO_PANE, self.H_PROMO_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		rowListName = self.top.getNextWidgetName()
		screen.addMultiListControlGFC(rowListName, "", self.X_PROMO_PANE+15, self.Y_PROMO_PANE+40, self.W_PROMO_PANE-20, self.H_PROMO_PANE-40, 1, self.PROMOTION_ICON_SIZE, self.PROMOTION_ICON_SIZE, TableStyles.TABLE_STYLE_STANDARD)
		for k in range(gc.getNumPromotionInfos()):
			if (isPromotionValid(k, self.iUnit, False) and not gc.getPromotionInfo(k).isGraphicalOnly()):
				screen.appendMultiListButton(rowListName, gc.getPromotionInfo(k).getButton(), 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, k, -1, False)



	def handleInput (self, inputClass):
		return 0

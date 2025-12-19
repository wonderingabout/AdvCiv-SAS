# <!-- custom: imported with almost no modification from RFC Dawn of Civilization mod C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\RFC Dawn of Civilization\Assets\Python\Pedia\CvPediaTerrain.py which may be modified or not for AdvCiv-SAS -->



from CvPythonExtensions import *
import CvUtil

from _sevopedia_helpers import *

gc = CyGlobalContext()
localText = CyTranslator()



class SevoPediaTerrain:
	def __init__(self, main):
		self.iTerrain = -1
		self.top = main

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		self.X_INFO_PANE = self.top.X_PEDIA_PAGE
		self.Y_INFO_PANE = self.top.Y_PEDIA_PAGE
		self.W_INFO_PANE = 290
		self.H_INFO_PANE = 120

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_INFO_PANE + 10
		self.Y_ICON = self.Y_INFO_PANE + 10
		self.ICON_SIZE = 64

		self.X_INFO_TEXT = self.X_INFO_PANE + 110
		self.Y_INFO_TEXT = self.Y_ICON + 15
		self.W_INFO_TEXT = 220
		self.H_INFO_TEXT = self.H_INFO_PANE - 20

		self.X_SPECIAL = self.X_INFO_PANE + self.W_INFO_PANE + self.MEDIUM_MARGIN
		self.W_SPECIAL = self.top.R_PEDIA_PAGE - self.X_SPECIAL
		self.H_SPECIAL = self.H_INFO_PANE
		self.Y_SPECIAL = self.Y_INFO_PANE

		self.X_FEATURES = self.X_INFO_PANE
		self.Y_FEATURES = self.Y_INFO_PANE + self.H_INFO_PANE + self.SMALL_MARGIN
		self.W_FEATURES = self.W_INFO_PANE
		self.H_FEATURES = 110

		self.X_IMPROVEMENTS = self.X_FEATURES + self.W_FEATURES + self.MEDIUM_MARGIN
		self.Y_IMPROVEMENTS = self.Y_FEATURES
		self.W_IMPROVEMENTS = self.top.R_PEDIA_PAGE - self.X_IMPROVEMENTS
		self.H_IMPROVEMENTS = self.H_FEATURES

		self.X_BONUSES_WITH_NO_FEATURE = self.X_FEATURES
		self.Y_BONUSES_WITH_NO_FEATURE = self.Y_FEATURES + self.H_FEATURES + self.SMALL_MARGIN
		self.W_BONUSES_WITH_NO_FEATURE = self.top.R_PEDIA_PAGE - self.X_BONUSES_WITH_NO_FEATURE
		self.H_BONUSES_WITH_NO_FEATURE = self.H_FEATURES

		self.X_BONUSES_ONLY_WITH_FEATURE = self.X_FEATURES
		self.Y_BONUSES_ONLY_WITH_FEATURE = self.Y_BONUSES_WITH_NO_FEATURE + self.H_BONUSES_WITH_NO_FEATURE + self.SMALL_MARGIN
		self.W_BONUSES_ONLY_WITH_FEATURE = self.top.R_PEDIA_PAGE - self.X_BONUSES_ONLY_WITH_FEATURE
		self.H_BONUSES_ONLY_WITH_FEATURE = self.H_FEATURES

		# <!-- custom: see code comment at self.H_MULTILIST_MULTIPLE_ROWS_BUTTON_SIZE in sevopedia unit for details anyways etc -->
		self.H_MULTILIST_MULTIPLE_ROWS_BUTTON_SIZE = 64

		self.X_RELEVANT_UNITS = self.X_FEATURES
		self.Y_RELEVANT_UNITS = self.Y_BONUSES_ONLY_WITH_FEATURE + self.H_BONUSES_ONLY_WITH_FEATURE + self.SMALL_MARGIN
		self.W_RELEVANT_UNITS = self.top.R_PEDIA_PAGE - self.X_BONUSES_ONLY_WITH_FEATURE
		self.H_RELEVANT_UNITS = self.H_FEATURES + self.H_MULTILIST_MULTIPLE_ROWS_BUTTON_SIZE

		self.X_UNITS_IMPASSABLE = self.X_FEATURES
		self.Y_UNITS_IMPASSABLE = self.Y_RELEVANT_UNITS + self.H_RELEVANT_UNITS + self.SMALL_MARGIN
		self.W_UNITS_IMPASSABLE = self.top.R_PEDIA_PAGE - self.X_RELEVANT_UNITS
		self.H_UNITS_IMPASSABLE = self.H_FEATURES

		self.X_HISTORY = self.X_FEATURES
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.X_HISTORY
		self.Y_HISTORY = self.Y_UNITS_IMPASSABLE + self.H_UNITS_IMPASSABLE + self.SMALL_MARGIN
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY



	def interfaceScreen(self, iTerrain):
		self.iTerrain = iTerrain

		self.placeInfo()
		self.placeSpecial()
		self.placeFeatures()
		self.placeImprovements()
		self.placeBonusesWithNoFeature()
		self.placeBonusesOnlyWithFeature()
		self.placeRelevantUnits()
		self.placeUnitsImpassable()
		self.placeHistory()



	def placeInfo(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		info = gc.getTerrainInfo(self.iTerrain)

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_INFO_PANE, self.Y_INFO_PANE, self.W_INFO_PANE, self.H_INFO_PANE, PanelStyles.PANEL_STYLE_BLUE50)

		# <!-- custom: was PanelStyles.PANEL_STYLE_MAIN -->
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), info.getButton(), self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.addListBoxGFC(panel, "", self.X_INFO_TEXT, self.Y_INFO_TEXT, self.W_INFO_TEXT, self.H_INFO_TEXT, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panel, False)
		screen.appendListBoxString(panel, u"<font=4b>" + info.getDescription() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		# <!-- custom: add missing txt key "Terrain" not in RFC DOC mod if i am not mistaken (didn't recheck but i assume it was as such seeing it is as of now hardcoded but anyways etc), instead of hardcoded one, now moved to its own txt key as in the below call as of now if i am not mistaken anyways etc -->
		# <!-- custom: also display some terrains as plot types / terrains, see xml txt key code comment for details if any hopefully helpful but or not but or yes but but anyways etc anyways etc anyways etc -->
		iPeak = getInfoTypeOrFail("TERRAIN_PEAK", gc)
		iHill = getInfoTypeOrFail("TERRAIN_HILL", gc)
		iOcean = getInfoTypeOrFail("TERRAIN_OCEAN", gc)

		if self.iTerrain == iPeak or self.iTerrain == iHill or self.iTerrain == iOcean:
			txtKeyTerrainPlotTypeLabel = "TXT_KEY_PEDIA_PLOT_TYPE_TERRAIN_CUSTOM"
		else:
			txtKeyTerrainPlotTypeLabel = "TXT_KEY_PEDIA_TERRAIN_CUSTOM"

		screen.appendListBoxString(panel, localText.getText(txtKeyTerrainPlotTypeLabel, ()), WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		if self.iTerrain == iHill:
			szStats = (u"%d%c  " % (-1, gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar()))
			szStats += (u"+%d%c  " % (1, gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar()))
		else:
			szStats = u""
			for iYield in xrange(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = info.getYield(iYield)
				if iYieldChange != 0:
					szStats += (u"%d%c  " % (iYieldChange, gc.getYieldInfo(iYield).getChar()))

		screen.appendListBoxString(panel, szStats, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)



	def placeSpecial(self):
		xPanel = self.X_SPECIAL
		yPanel = self.Y_SPECIAL
		wPanel = self.W_SPECIAL
		hPanel = self.H_SPECIAL

		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		text = self.top.getNextWidgetName()
		info = gc.getTerrainInfo(self.iTerrain)

		screen.addPanel(panel, "", "", True, True, xPanel, yPanel, wPanel, hPanel, PanelStyles.PANEL_STYLE_BLUE50)

		iPeak = getInfoTypeOrFail("TERRAIN_PEAK", gc)
		iHill = getInfoTypeOrFail("TERRAIN_HILL", gc)

		# <!-- custom: the entry seems garbage or info about terrain_peak perhaps? But/so anyways etc leaving it as rfc doc mod did if i am not mistaken just with minor refactor of iHill above as of now anyways etc ; the peak info is also incomplete, not mentioning for example the impassable info if i am not mistaken so also not displaying it for peak if i am not mistaken in doing so but anyways etc -->
		if self.iTerrain == iPeak or self.iTerrain == iHill:
			txtKeyNoDisplay = "TXT_KEY_PEDIA_TERRAIN_EXCLUDED_FROM_DISPLAY_PLOT_TYPE_WITH_EXPLANATION"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoDisplay, ())
			# <!-- custom: note: do not use yPanelCenter as this is a panel with quite high height, higher (no pun but anyways etc...) than default or usual panel height, and it seems that maybe the panel's height is not a clean as chatgpt said this word clean to rephrase my more explanation and question of it maybe not being a multiplier of one line height, so starting from center it would overfill (as it would start a bit below the exact half if inner panel does not have an exactly aligned total height being a line multiplier maybe if i am not mistaken in my guess? That chatgpt seems to approve as well but could be mistaken too or maybe not but hopefully helpful or not or yes or etc, check if this info is accurate though (about line height not cleanly centered in this case but anyways etc...) to be sure anyways etc), so to solve this start a bit higher than the center instead anyways etc -->
			#yPanelCenter = yPanel + (hPanel / 2)
			yPanelCenter = yPanel + int(0.42 * hPanel)
			screen.addMultilineText(textName, szText, xPanel + 7, yPanelCenter, wPanel - 14, hPanel - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		else:
			szText = info.getHelp()
			szText += CyGameTextMgr().getTerrainHelp(self.iTerrain, True)
			szText = szText.replace("\n\n", "\n").strip()
			screen.addMultilineText(text, szText, self.X_SPECIAL + 5, self.Y_SPECIAL + 10, self.W_SPECIAL - 10, self.H_SPECIAL - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeFeatures(self):
		xPanel = self.X_FEATURES
		yPanel = self.Y_FEATURES
		wPanel = self.W_FEATURES
		hPanel = self.H_FEATURES

		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()

		screen.addPanel(panel, localText.getText("TXT_KEY_MISC_FEATURES", ()), "", False, True, xPanel, yPanel, wPanel, hPanel, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")

		# <!-- custom: not sure we have a reason to as display is currently empty, but just in case or/and for consistency, also exclude from display here anyways etc -->
		iPeak = getInfoTypeOrFail("TERRAIN_PEAK", gc)
		iHill = getInfoTypeOrFail("TERRAIN_HILL", gc)

		if self.iTerrain == iPeak or self.iTerrain == iHill:
			txtKeyNoDisplay = "TXT_KEY_PEDIA_TERRAIN_EXCLUDED_FROM_DISPLAY_PLOT_TYPE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoDisplay, ())
			yPanelCenter = yPanel + (hPanel / 2)
			screen.addMultilineText(textName, szText, xPanel + 7, yPanelCenter, wPanel - 14, hPanel - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		else:
			for iFeature in xrange(gc.getNumFeatureInfos()):
				FeatureInfo = gc.getFeatureInfo(iFeature)

				if FeatureInfo.isGraphicalOnly():
					continue
				elif FeatureInfo.isTerrain(self.iTerrain):
					screen.attachImageButton(panel, "", FeatureInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE, iFeature, 1, False)



	def placeImprovements(self):
		xPanel = self.X_IMPROVEMENTS
		yPanel = self.Y_IMPROVEMENTS
		wPanel = self.W_IMPROVEMENTS
		hPanel = self.H_IMPROVEMENTS

		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()

		screen.addPanel(panel, localText.getText("TXT_KEY_PEDIA_IMPROVEMENTS_CUSTOM", ()), "", False, True, xPanel, yPanel, wPanel, hPanel, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")

		# <!-- custom: add a logic that excludes hills from this as output is unreliable, see below code comment as of now anyways etc, as for peak exclude it as well as it shouldn't have improvements at least as of now anyways etc -->
		iPeak = getInfoTypeOrFail("TERRAIN_PEAK", gc)
		iHill = getInfoTypeOrFail("TERRAIN_HILL", gc)
		if self.iTerrain == iPeak or self.iTerrain == iHill:
			txtKeyNoDisplay = "TXT_KEY_PEDIA_TERRAIN_EXCLUDED_FROM_DISPLAY_PLOT_TYPE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoDisplay, ())
			yPanelCenter = yPanel + (hPanel / 2)
			screen.addMultilineText(textName, szText, xPanel + 7, yPanelCenter, wPanel - 14, hPanel - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		else:
			for iImprovement in xrange(gc.getNumImprovementInfos()):
				ImprovementInfo = gc.getImprovementInfo(iImprovement)
				if ImprovementInfo.isGoody():
					continue
				elif ImprovementInfo.getTerrainMakesValid(self.iTerrain):
					screen.attachImageButton(panel, "", ImprovementInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, iImprovement, 1, False)
				# <!-- custom: the output is not reliable for hills improvements (missing forts, also cottages are conditionally dependent on terrain having enough food according to https://civilization.fandom.com/wiki/Hill_(Civ4) if i am not mistaken anyways etc, missing forest preserve too dependent on forest or jungle according to this link as well, so disabling the display entirely rather anyways etc)
				# elif self.iTerrain == iHill and ImprovementInfo.isHillsMakesValid():
				# 	screen.attachImageButton(panel, "", ImprovementInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, iImprovement, 1, False)



	def placeBonusesWithNoFeature(self):
		xPanel = self.X_BONUSES_WITH_NO_FEATURE
		yPanel = self.Y_BONUSES_WITH_NO_FEATURE
		wPanel = self.W_BONUSES_WITH_NO_FEATURE
		hPanel = self.H_BONUSES_WITH_NO_FEATURE

		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()

		# <!-- custom: refactor/tweak/change anyways etc to test for the existence of terrain_hill 's id explicitly else raise an error not silently pass anyways etc as is also done in several other parts of the sevopedia reworked/refactored code if i may say but anyways etc anyways etc anyways etc, and or such other tweaks to rfc doc mod's code for peak anyways etc anyways etc anyways etc -->
		iPeak = getInfoTypeOrFail("TERRAIN_PEAK", gc)
		iHill = getInfoTypeOrFail("TERRAIN_HILL", gc)
		txtKeyPanel = "TXT_KEY_PEDIA_TERRAIN_BONUSES_WITH_NO_FEATURE"
		if self.iTerrain == iPeak:
			txtKeyPanel = "TXT_KEY_PEDIA_TERRAIN_BONUSES_NOT_APPLICABLE_FOR_THIS_PLOT_TYPE"
		elif self.iTerrain == iHill:
			txtKeyPanel = "TXT_KEY_PEDIA_TERRAIN_BONUSES_HILL"

		screen.addPanel(panel, localText.getText(txtKeyPanel, ()), "", False, True, xPanel, yPanel, wPanel, hPanel, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")

		# <!-- custom: not applicable for this plot type / terrain if i am not mistaken, so show an alternative text instead anyways etc -->
		if self.iTerrain == iPeak:
			txtKeyNoDisplay = "TXT_KEY_PEDIA_TERRAIN_EXCLUDED_FROM_DISPLAY_PLOT_TYPE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoDisplay, ())
			yPanelCenter = yPanel + (hPanel / 2)
			screen.addMultilineText(textName, szText, xPanel + 7, yPanelCenter, wPanel - 14, hPanel - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		else:
			for iBonus in xrange(gc.getNumBonusInfos()):
				bonusInfo = gc.getBonusInfo(iBonus)
				if bonusInfo.isGraphicalOnly():
					continue
				# <!-- custom: minor refactor fromr rfc doc mod since output seems to be the same, check for both all terrains and then specifically for hill anyways etc (with the more general check first so it is executed faster even if a micro bit in this case (but still! If i may say too (reference to baten kaitos's kalas line if i may say but anyways etc...) but anyways etc...) but anyways etc...) -->
				elif (bonusInfo.isTerrain(self.iTerrain)) or (self.iTerrain == iHill and bonusInfo.isHills()):
					screen.attachImageButton(panel, "", bonusInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iBonus, 1, False)



	# <!-- custom: code provided by chatgpt thanks to my prompts too and adjustments too but anyways etc -->
	def placeBonusesOnlyWithFeature(self):
		xPanel = self.X_BONUSES_ONLY_WITH_FEATURE
		yPanel = self.Y_BONUSES_ONLY_WITH_FEATURE
		wPanel = self.W_BONUSES_ONLY_WITH_FEATURE
		hPanel = self.H_BONUSES_ONLY_WITH_FEATURE

		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()

		iHill = getInfoTypeOrFail("TERRAIN_HILL", gc)
		iPeak = getInfoTypeOrFail("TERRAIN_PEAK", gc)
		txtKeyPanel = "TXT_KEY_PEDIA_TERRAIN_BONUSES_FEATURE_TERRAIN_BOOLEANS"
		if self.iTerrain == iHill or self.iTerrain == iPeak:
			txtKeyPanel = "TXT_KEY_PEDIA_TERRAIN_BONUSES_NOT_APPLICABLE_FOR_THIS_PLOT_TYPE"

		screen.addPanel(panel, localText.getText(txtKeyPanel, ()), "", False, True, xPanel, yPanel, wPanel, hPanel, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")

		if self.iTerrain == iHill or self.iTerrain == iPeak:
			txtKeyNoDisplay = "TXT_KEY_PEDIA_TERRAIN_EXCLUDED_FROM_DISPLAY_PLOT_TYPE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoDisplay, ())
			yPanelCenter = yPanel + (hPanel / 2)
			screen.addMultilineText(textName, szText, xPanel + 7, yPanelCenter, wPanel - 14, hPanel - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		else:
			for iBonus in xrange(gc.getNumBonusInfos()):
				BonusInfo = gc.getBonusInfo(iBonus)
				if BonusInfo.isGraphicalOnly():
					continue

				if BonusInfo.isFeatureTerrain(self.iTerrain):
					screen.attachImageButton(panel, "", BonusInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iBonus, 1, False)



	# <!-- custom: code provided by chatgpt thanks to my prompt too and adjusted or not for advciv-sas anyways etc -->
	def placeRelevantUnits(self):
		xPanel = self.X_RELEVANT_UNITS
		yPanel = self.Y_RELEVANT_UNITS
		wPanel = self.W_RELEVANT_UNITS
		hPanel = self.H_RELEVANT_UNITS

		txtKeyPanel = "TXT_KEY_PEDIA_TERRAIN_FEATURE_RELEVANT_UNITS"

		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()

		# Create panel with proper styling
		screen.addPanel(panelName, localText.getText(txtKeyPanel, ()), "", False, True, xPanel, yPanel, wPanel, hPanel, PanelStyles.PANEL_STYLE_BLUE50)

		rowListName = self.top.getNextWidgetName()

		# <!-- custom: see code comment at self.H_MULTILIST_MULTIPLE_ROWS_BUTTON_SIZE in sevopedia unit for details anyways etc -->
		BUTTON_SIZE = self.H_MULTILIST_MULTIPLE_ROWS_BUTTON_SIZE

		# Create the MultiList control
		# Constants for button display
		multiListX = xPanel + MULTI_LIST_PANEL_OFFSET_X
		multiListY = yPanel + MULTI_LIST_PANEL_OFFSET_Y
		multiListW = wPanel + MULTI_LIST_PANEL_ADDITIONAL_W
		multiListH = hPanel + MULTI_LIST_PANEL_ADDITIONAL_H
		# Per documentation, the numLists parameter (7th) is actually number of columns
		# Setting to 1 means the engine will auto-calculate how many buttons fit per row
		# Using 1 for auto-calculation of buttons per row
		buttonCalculate = 1
		screen.addMultiListControlGFC(rowListName, "", multiListX, multiListY, multiListW, multiListH, buttonCalculate, BUTTON_SIZE, BUTTON_SIZE, TableStyles.TABLE_STYLE_STANDARD)

		#isButtonFound = False
		iButtonIndex = 0

		# <!-- custom: buttonCalculate --> =1 in your case (auto-fit); <!-- custom: so we calculate --> column layout manually
		maxButtonsPerRow = get_multilist_max_buttons_per_row(multiListW, BUTTON_SIZE)

		# <!-- custom: for peak we display units that can walk on the tile rather than those that have modifier, i find this or/and think this is more informative anyways etc -->
		iPeak = getInfoTypeOrFail("TERRAIN_PEAK", gc)
		# <!-- custom: terrain_hill uses its own kind of modifier, plus also i'd want to show guerilla promotion as well anyways etc, so handle its display separately anyways etc -->
		iHill = getInfoTypeOrFail("TERRAIN_HILL", gc)
		iCoast = getInfoTypeOrFail("TERRAIN_COAST", gc)
		iOcean = getInfoTypeOrFail("TERRAIN_OCEAN", gc)

		if self.iTerrain == iPeak:
			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				# <!-- custom: parts of the below condition(s)/code by chatgpt 5, check if accurate and check if all is accurate if want to be sure but anyways etc -->
				# inside placeRelevantUnits(), in the if self.iTerrain == iPeak: loop
				unitInfoDomain = unitInfo.getDomainType()
				passTech = (unitInfo.getTerrainPassableTech(iPeak) != -1)

				# <!-- custom: also handle water units that can move through all terrains but only on water if i am not mistaken anyways etc ; also for peak logic is different than for other terrains in placeRelevantUnits, do not place only units that have modifiers for this "terrain" (as is plot type too if i am not mistaken but anyways etc), but place more broadly any unit, even if it doesn't have a modifier, as long as it can walk on the tile, then display the numTxt or any information optionally if the unit has it, else default to something like "_/_" (no attack or def modifier) or whatever the numTxt generating function gives us anyways etc or anything else you'd want or i'd want too but i am fine with this if i may say (and i coded it xd but anyways etc...) hopefully helpful or not or yes or etc but anyways etc... -->
				# <!-- custom: also show boat with legs, in case some crazy mod mod nicely impelments this xd or us but less likely or not or yes or etc but anyways etc -->
				# Peak — Relevant Units (includes “boat with legs”; All-Terrain short-circuits)
				can_walk_on_peak = (
					unitInfo.isCanMoveAllTerrain() or
					(unitInfoDomain == DomainTypes.DOMAIN_LAND and
					(unitInfo.isCanMoveImpassable() or passTech))
				)

				if can_walk_on_peak:
						# Column index (always 0 when numLists=1)
						columnIndex = 0
						screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

						iTerrainAttack = unitInfo.getTerrainAttackModifier(self.iTerrain)
						iTerrainDefense = unitInfo.getTerrainDefenseModifier(self.iTerrain)

						numTxt = get_numTxt_attack_defense_modifiers(iTerrainAttack, iTerrainDefense)
						extraCorrectionX = get_extra_correction_x(numTxt)
						add_multilist_numTxt_under_button(multiListX, multiListY, extraCorrectionX, iButtonIndex, BUTTON_SIZE, maxButtonsPerRow, numTxt, screen, self.top, WidgetTypes.WIDGET_GENERAL, CvUtil.FONT_CENTER_JUSTIFY)

						#isButtonFound = True
						iButtonIndex += 1

		elif self.iTerrain == iHill:
			# <!-- custom: raise an error if asset does not exist (in advciv-sas we have renamed PROMOTION_GUERILLA1 to PROMOTION_HILLS_MASTER1 and such anyways etc) -->
			iPromotionHillsMaster1 = getInfoTypeOrFail("PROMOTION_HILLS_MASTER1", gc)
			iPromotionHillsMaster2 = getInfoTypeOrFail("PROMOTION_HILLS_MASTER2", gc)
			iPromotionHillsMaster3 = getInfoTypeOrFail("PROMOTION_HILLS_MASTER3", gc)

			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				iHillsAttack = unitInfo.getHillsAttackModifier()
				iHillsDefense = unitInfo.getHillsDefenseModifier()

				isHasHM1 = unitInfo.getFreePromotions(iPromotionHillsMaster1)
				isHasHM2 = unitInfo.getFreePromotions(iPromotionHillsMaster2)
				isHasHM3 = unitInfo.getFreePromotions(iPromotionHillsMaster3)

				if ((iHillsAttack != 0) or (iHillsDefense != 0) or isHasHM1 or isHasHM2 or isHasHM3):
					# Column index (always 0 when numLists=1)
					columnIndex = 0
					screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

					if (iHillsAttack != 0 or iHillsDefense != 0):
						numTxt = get_numTxt_attack_defense_modifiers(iHillsAttack, iHillsDefense)
					else:
						# <!-- custom: display first the modifier, and only if there are no modifiers, try to display the promotion(s) instead if there are any promotion(s), anyways etc ; also very efficient code if i may say at least computationally provided by chatgpt and at least efficient (very) (if not at least quite if not lot but anyways etc also wanted it to be quite clear but mostly performant but anyways etc anyways etc anyways etc) to me in this case at least but anyways etc thanks to my prompt too but or not but or yes but anyways etc -->
						s = ""
						if isHasHM1:
							s = "HM1"
						if isHasHM2:
							if s:
								s += "+2"
							else:
								s = "HM2"
						if isHasHM3:
							if s:
								s += "+3"
							else:
								s = "HM3"
						if s:
							numTxt = s

					extraCorrectionX = get_extra_correction_x(numTxt)
					add_multilist_numTxt_under_button(multiListX, multiListY, extraCorrectionX, iButtonIndex, BUTTON_SIZE, maxButtonsPerRow, numTxt, screen, self.top, WidgetTypes.WIDGET_GENERAL, CvUtil.FONT_CENTER_JUSTIFY)

					#isButtonFound = True
					iButtonIndex += 1

		elif self.iTerrain == iCoast or self.iTerrain == iOcean:
			# <!-- custom: raise an error if asset does not exist (in advciv-sas we have renamed PROMOTION_GUERILLA1 to PROMOTION_HILLS_MASTER1 and such anyways etc) -->
			iPromotionNavigator = getInfoTypeOrFail("PROMOTION_NAVIGATOR", gc)

			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				iTerrainAttack = unitInfo.getTerrainAttackModifier(self.iTerrain)
				iTerrainDefense = unitInfo.getTerrainDefenseModifier(self.iTerrain)

				isHasN = unitInfo.getFreePromotions(iPromotionNavigator)

				if (unitInfo.isCanMoveAllTerrain() or ((unitInfo.getDomainType() == DomainTypes.DOMAIN_SEA) and (not unitInfo.getTerrainImpassable(self.iTerrain)) and (unitInfo.getTerrainPassableTech(self.iTerrain) == -1)) or (iTerrainAttack != 0) or (iTerrainDefense != 0) or isHasN):
					columnIndex = 0
					screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

					if iTerrainAttack != 0 or iTerrainDefense != 0:
						numTxt = get_numTxt_attack_defense_modifiers(iTerrainAttack, iTerrainDefense)
					elif isHasN:
						numTxt = "N"
					else:
						numTxt = "_/_"  # or "" if you prefer no tag
				
					extraCorrectionX = get_extra_correction_x(numTxt)
					add_multilist_numTxt_under_button(multiListX, multiListY, extraCorrectionX, iButtonIndex, BUTTON_SIZE, maxButtonsPerRow, numTxt, screen, self.top, WidgetTypes.WIDGET_GENERAL, CvUtil.FONT_CENTER_JUSTIFY)

					#isButtonFound = True
					iButtonIndex += 1

		else:
			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				iTerrainAttack = unitInfo.getTerrainAttackModifier(self.iTerrain)
				iTerrainDefense = unitInfo.getTerrainDefenseModifier(self.iTerrain)

				if iTerrainAttack != 0 or iTerrainDefense != 0:
					# Column index (always 0 when numLists=1)
					columnIndex = 0
					screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

					numTxt = get_numTxt_attack_defense_modifiers(iTerrainAttack, iTerrainDefense)
					extraCorrectionX = get_extra_correction_x(numTxt)
					add_multilist_numTxt_under_button(multiListX, multiListY, extraCorrectionX, iButtonIndex, BUTTON_SIZE, maxButtonsPerRow, numTxt, screen, self.top, WidgetTypes.WIDGET_GENERAL, CvUtil.FONT_CENTER_JUSTIFY)

					#isButtonFound = True
					iButtonIndex += 1

	# <!-- custom: code provided by chatgpt thanks to my prompt too and adjusted or not for advciv-sas anyways etc -->
	def placeUnitsImpassable(self):
		xPanel = self.X_UNITS_IMPASSABLE
		yPanel = self.Y_UNITS_IMPASSABLE
		wPanel = self.W_UNITS_IMPASSABLE
		hPanel = self.H_UNITS_IMPASSABLE

		txtKeyPanel = "TXT_KEY_PEDIA_TERRAIN_UNITS_IMPASSABLE"

		iPeak = getInfoTypeOrFail("TERRAIN_PEAK", gc)

		if self.iTerrain == iPeak:
			txtKeyPanel = "TXT_KEY_PEDIA_TERRAIN_UNITS_IMPASSABLE_PEAK"

		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()

		# Create panel with proper styling
		screen.addPanel(panelName, localText.getText(txtKeyPanel, ()), "", False, True, xPanel, yPanel, wPanel, hPanel, PanelStyles.PANEL_STYLE_BLUE50)

		rowListName = self.top.getNextWidgetName()

		BUTTON_SIZE = 64

		# Create the MultiList control
		# Constants for button display
		multiListX = xPanel + MULTI_LIST_PANEL_OFFSET_X
		multiListY = yPanel + MULTI_LIST_PANEL_OFFSET_Y
		multiListW = wPanel + MULTI_LIST_PANEL_ADDITIONAL_W
		multiListH = hPanel + MULTI_LIST_PANEL_ADDITIONAL_H
		# Per documentation, the numLists parameter (7th) is actually number of columns
		# Setting to 1 means the engine will auto-calculate how many buttons fit per row
		# Using 1 for auto-calculation of buttons per row
		buttonCalculate = 1
		screen.addMultiListControlGFC(rowListName, "", multiListX, multiListY, multiListW, multiListH, buttonCalculate, BUTTON_SIZE, BUTTON_SIZE, TableStyles.TABLE_STYLE_STANDARD)

		iCoast = getInfoTypeOrFail("TERRAIN_COAST", gc)
		iOcean = getInfoTypeOrFail("TERRAIN_OCEAN", gc)

		# <!-- custom: for peak we display units that can walk on the tile rather than those that have modifier, i find this or/and think this is more informative anyways etc -->
		if self.iTerrain == iPeak:
			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				# <!-- custom: parts of the below condition(s)/code by chatgpt 5, check if accurate and check if all is accurate if want to be sure but anyways etc -->
				# inside placeUnitsImpassable(), in the if self.iTerrain == iPeak: loop
				unitInfoDomain = unitInfo.getDomainType()
				passTech = (unitInfo.getTerrainPassableTech(iPeak) != -1)

				# <!-- custom: "boat with legs" edge case handled in as of now relevant units if i'm not mistaken and as chatgpt 5 says as well, if no boat unit at all has legs, as is as of now in advciv-sas, then they would instead be displayed in this units impassable panel for exhaustiveness and notsimply omitted if i understood it correctly and if i'm not mistaken i mean but anyways etc, check if accurate but anyways etc -->
				# Peak — Units Impassable (show land w/out bypass; all sea unless All-Terrain)
				blocked = (
					(not unitInfo.isCanMoveAllTerrain()) and (
						(unitInfoDomain == DomainTypes.DOMAIN_LAND and
						not (unitInfo.isCanMoveImpassable() or passTech)) or
						(unitInfoDomain == DomainTypes.DOMAIN_SEA)  # regular ships blocked
					)
				)

				if blocked:
					# Column index (always 0 when numLists=1)
					columnIndex = 0
					screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

		elif self.iTerrain == iCoast or self.iTerrain == iOcean:
			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				# <!-- custom: unitInfo.isCanMoveAllTerrain() returns too many units but (not unitInfo.isCanMoveAllTerrain()) does not, so unlike in placeRelevantUnits, wrap this unitInfo.isCanMoveAllTerrain() in placeUnitsImpassable in the domain sea check, ideally i would have wanted to check our xml by having a large permissive check, but the results are unreadable since almost all units have this (not unitInfo.isCanMoveAllTerrain()) that is true -->
				if unitInfo.getDomainType() == DomainTypes.DOMAIN_SEA:
					if ((unitInfo.getTerrainImpassable(self.iTerrain) or (unitInfo.getTerrainPassableTech(self.iTerrain) != -1)) and (not unitInfo.isCanMoveAllTerrain())):
						columnIndex = 0
						screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

		else:
			# <!-- custom: parts of the below condition(s)/code by chatgpt 5, check if accurate and check if all is accurate if want to be sure but anyways etc -->
			info = gc.getTerrainInfo(self.iTerrain)

			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				# Right now you include units if they have a passable tech (inverted logic). To show units that are truly blocked (no bypass), use the same pattern you used for features:
				blocked = (
					(info.isImpassable() or unitInfo.getTerrainImpassable(self.iTerrain)) and
					not unitInfo.isCanMoveImpassable() and
					unitInfo.getTerrainPassableTech(self.iTerrain) == -1 and
					not unitInfo.isCanMoveAllTerrain()
				)
				if blocked:
					# Column index (always 0 when numLists=1)
					columnIndex = 0
					screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)



	def placeHistory(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		text = self.top.getNextWidgetName()
		info = gc.getTerrainInfo(self.iTerrain)

		screen.addPanel(panel, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50 )

		szHistory = info.getCivilopedia()
		screen.addMultilineText(text, szHistory, self.X_HISTORY + 10, self.Y_HISTORY + 30, self.W_HISTORY - 20, self.H_HISTORY - 40, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

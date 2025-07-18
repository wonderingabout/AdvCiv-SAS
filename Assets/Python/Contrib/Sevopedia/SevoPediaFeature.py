# <!-- custom: imported from RFC Dawn of Civilization mod:
# C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\RFC Dawn of Civilization\Assets\Python\Pedia\CvPediaFeature.py
# which may be modified or not for AdvCiv-SAS ; for example renamed placeDetails to placeSpecial for consistency with our other special effect method names in other sevopedia classes anyways etc, or/and other changes or not anyways etc -->



from CvPythonExtensions import *
import CvUtil
# <!-- custom: remove or comment out unused imports -->
#import ScreenInput
#import SevoScreenEnums

from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



class SevoPediaFeature:
	def __init__(self, main):
		self.iFeature = -1
		self.top = main

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

		self.X_SPECIAL = self.X_INFO_PANE + self.W_INFO_PANE + 10
		self.W_SPECIAL = self.top.R_PEDIA_PAGE - self.X_SPECIAL
		self.H_SPECIAL = self.H_INFO_PANE
		self.Y_SPECIAL = self.Y_INFO_PANE

		self.X_FEATURES = self.X_INFO_PANE
		self.Y_FEATURES = self.Y_INFO_PANE + self.H_INFO_PANE + 10
		self.W_FEATURES = self.W_INFO_PANE
		self.H_FEATURES = 110

		self.X_IMPROVEMENTS = self.X_FEATURES + self.W_FEATURES + 10
		self.Y_IMPROVEMENTS = self.Y_FEATURES
		self.W_IMPROVEMENTS = self.top.R_PEDIA_PAGE - self.X_IMPROVEMENTS
		self.H_IMPROVEMENTS = self.H_FEATURES

		self.X_RESOURCES = self.X_FEATURES
		self.Y_RESOURCES = self.Y_FEATURES + self.H_FEATURES + 10
		self.W_RESOURCES = self.top.R_PEDIA_PAGE - self.X_RESOURCES
		self.H_RESOURCES = self.H_FEATURES

		# <!-- custom: see code comment at self.H_MULTILIST_MULTIPLE_ROWS_BUTTON_SIZE in sevopedia unit for details anyways etc -->
		self.H_MULTILIST_MULTIPLE_ROWS_BUTTON_SIZE = 64

		# <!-- custom: new placeRelevantUnits and placeUnitsImpassable based on the new anyways etc sevopedia terrain implementation anyways etc -->
		self.X_RELEVANT_UNITS = self.X_RESOURCES
		self.Y_RELEVANT_UNITS = self.Y_RESOURCES + self.H_RESOURCES + 10
		self.W_RELEVANT_UNITS = self.top.R_PEDIA_PAGE - self.X_RESOURCES
		self.H_RELEVANT_UNITS = self.H_FEATURES + self.H_MULTILIST_MULTIPLE_ROWS_BUTTON_SIZE

		self.X_UNITS_IMPASSABLE = self.X_RELEVANT_UNITS
		self.Y_UNITS_IMPASSABLE = self.Y_RELEVANT_UNITS + self.H_RELEVANT_UNITS + 10
		self.W_UNITS_IMPASSABLE = self.top.R_PEDIA_PAGE - self.X_RELEVANT_UNITS
		self.H_UNITS_IMPASSABLE = self.H_FEATURES

		self.X_HISTORY = self.X_UNITS_IMPASSABLE
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.X_HISTORY
		self.Y_HISTORY = self.Y_UNITS_IMPASSABLE + self.H_UNITS_IMPASSABLE + 10
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY



	def interfaceScreen(self, iFeature):
		self.iFeature = iFeature

		self.placeInfo()
		self.placeSpecial()
		self.placeTerrain()
		self.placeImprovements()
		self.placeResources()
		self.placeRelevantUnits()
		self.placeUnitsImpassable()
		self.placeHistory()



	def placeInfo(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		info = gc.getFeatureInfo(self.iFeature)

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_INFO_PANE, self.Y_INFO_PANE, self.W_INFO_PANE, self.H_INFO_PANE, PanelStyles.PANEL_STYLE_BLUE50)

		# <!-- custom: was PanelStyles.PANEL_STYLE_MAIN -->
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), info.getButton(), self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.addListBoxGFC(panel, "", self.X_INFO_TEXT, self.Y_INFO_TEXT, self.W_INFO_TEXT, self.H_INFO_TEXT, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panel, False)
		screen.appendListBoxString(panel, u"<font=4b>" + info.getDescription() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		szText = ""
		screen.appendListBoxString(panel, localText.getText("TXT_KEY_PEDIA_FEATURE", ()), WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		szText = u""
		for iYield in xrange(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = info.getYieldChange(iYield)
			if iYieldChange != 0:
				szSign = ""
				if iYieldChange > 0:
					szSign = "+"
				szText += (u"%s%d%c  " % (szSign, iYieldChange, gc.getYieldInfo(iYield).getChar()))

		screen.appendListBoxString(panel, szText, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: code provided by claude ai (and chatgpt too for debug and such anyways etc thanks anyways etc :) anyways etc) thanks to my prompt (too! but anyways etc...) and adjustments too or not or yes or etc but anyways etc -->
	def getChopProductionText(self):	
		# Start with no known max
		maxSoFar = None

		# Check all builds for ones that can remove this feature
		for iBuild in xrange(gc.getNumBuildInfos()):
			buildInfo = gc.getBuildInfo(iBuild)

			if buildInfo.isFeatureRemove(self.iFeature):
				chopProduction = buildInfo.getFeatureProduction(self.iFeature)

				# <!-- custom: there shouldn't be any negative value if i am not mistaken but just in case we'd want to see them, to debug/fix or if some mod mod if i may say or such has some kind of such behaviour anyways etc -->
				if chopProduction != 0:
					if maxSoFar is None:
						maxSoFar = chopProduction
					else:
						if chopProduction > maxSoFar:
							# <!-- custom: (note: this simplifies display for the where case cottages and farms would have different values which would be highly unusual, ignored to simplify code, display, and logic, but ideally if a mod implements such a feature, which would be strange btw as building a farm also chops as part of it if i am not mistaken it is not a different operation at least it seems so ingame anyways, so ignoring this in our code and displaying it as such, raising an error instead anyways etc -->
							if maxSoFar > 0:
								raise ValueError(u"[VALUE ERROR] Unexpected different iProduction chopProduction=%d value where a not equal to 0 value maxSoFar=%d already existed between builds (cottage, remove_jungle, farm, etc.) at feature=%d (feature type is %s). Please make sure your iProduction is consistent accross all builds that can remove this feature, or if purposely designed as such, modify this code to display such information if you want or/and remove the error anyways etc." % (chopProduction, maxSoFar, self.iFeature, gc.getFeatureInfo(self.iFeature).getType()))

							maxSoFar = chopProduction

		# <!-- custom: return highest value if any, else return none -->
		if maxSoFar:
			chopProductionText = u"%s+%d%s on chop" % (localText.getText("[ICON_BULLET]", ()), maxSoFar, localText.getText("[ICON_PRODUCTION]", ()))
			print("value xxx is %s" % chopProductionText)
			return chopProductionText
		else:
			return ""



	def placeSpecial(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		text = self.top.getNextWidgetName()
		info = gc.getFeatureInfo(self.iFeature)

		screen.addPanel(panel, "", "", True, True, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50)
		szText = info.getHelp()
		szText += CyGameTextMgr().getFeatureHelp(self.iFeature, True)

		# Add chop production information
		chopProductionText = self.getChopProductionText()
		if chopProductionText:
			szText += "\n%s" % chopProductionText

		szText = szText.replace("\n\n", "\n").strip()
		screen.addMultilineText(text, szText, self.X_SPECIAL + 5, self.Y_SPECIAL + 10, self.W_SPECIAL - 10, self.H_SPECIAL - 15, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeTerrain(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		info = gc.getFeatureInfo(self.iFeature)

		screen.addPanel(panel, localText.getText("TXT_KEY_PEDIA_TERRAINS_MINUS_PLOT_TYPES", ()), "", False, True, self.X_FEATURES, self.Y_FEATURES, self.W_FEATURES, self.H_FEATURES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")

		for iTerrain in xrange(gc.getNumTerrainInfos()):
			TerrainInfo = gc.getTerrainInfo(iTerrain)
			if info.isTerrain(iTerrain):
				screen.attachImageButton(panel, "", TerrainInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, iTerrain, 1, False)



	def placeImprovements(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()

		screen.addPanel(panel, localText.getText("TXT_KEY_PEDIA_IMPROVEMENTS_CUSTOM", ()), "", False, True, self.X_IMPROVEMENTS, self.Y_IMPROVEMENTS, self.W_IMPROVEMENTS, self.H_IMPROVEMENTS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")

		for iImprovement in xrange(gc.getNumImprovementInfos()):
			ImprovementInfo = gc.getImprovementInfo(iImprovement)
			if ImprovementInfo.isGoody():
				continue
			elif ImprovementInfo.getFeatureMakesValid(self.iFeature):
				screen.attachImageButton(panel, "", ImprovementInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, iImprovement, 1, False)



	def placeResources(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()

		screen.addPanel(panel, localText.getText("TXT_KEY_CONCEPT_RESOURCES", ()), "", False, True, self.X_RESOURCES, self.Y_RESOURCES, self.W_RESOURCES, self.H_RESOURCES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")

		for iResource in xrange(gc.getNumBonusInfos()):
			ResourceInfo = gc.getBonusInfo(iResource)
			if ResourceInfo.isGraphicalOnly():
				continue
			if ResourceInfo.isFeature(self.iFeature):
				screen.attachImageButton(panel, "", ResourceInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iResource, 1, False)



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

		# <!-- custom: buttonCalculate-->=1 in your case (auto-fit); <!-- custom: so we calculate --> column layout manually
		maxButtonsPerRow = get_multilist_max_buttons_per_row(multiListW, BUTTON_SIZE)

		# <!-- custom: handle feature(s) that is (are) impassable (anyways etc...) such as of now only the ice cap feature anyways etc quite similarly than the peak terrain was handled in sevopedia terrain's placeRelevantUnits, with some differences anyways etc, see code comments at sevopedia feature's placeUnitsImpassable anyways etc-->
		iIce = getInfoTypeOrFail("FEATURE_ICE", gc)
		# <!-- custom: handle features with promotions or other specific effects if any if i may say anyways etc separately, similar to how was done in sevopedia terrain previous new placeRelevantUnits and placeUnitsImpassable this new features code is based on but anyways etc anyways etc anyways etc -->
		iForest = getInfoTypeOrFail("FEATURE_FOREST", gc)
		iJungle = getInfoTypeOrFail("FEATURE_JUNGLE", gc)

		if self.iFeature == iIce:
			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				if unitInfo.isCanMoveImpassable():
					# Column index (always 0 when numLists=1)
					columnIndex = 0
					screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

					iFeatureAttack = unitInfo.getFeatureAttackModifier(self.iFeature)
					iFeatureDefense = unitInfo.getFeatureDefenseModifier(self.iFeature)

					numTxt = get_numTxt_attack_defense_modifiers(iFeatureAttack, iFeatureDefense)
					extraCorrectionX = get_extra_correction_x(numTxt)
					add_multilist_numTxt_under_button(multiListX, multiListY, extraCorrectionX, iButtonIndex, BUTTON_SIZE, maxButtonsPerRow, numTxt, screen, self.top, WidgetTypes.WIDGET_GENERAL, CvUtil.FONT_CENTER_JUSTIFY)

					#isButtonFound = True
					iButtonIndex += 1

		# <!-- custom: in advciv-sas as of now at least if not always or not anyways etc, woodsman promotions apply both to jungle but also to forest tiles as well, seems more sensical to me anyways etc, adjust below logic depending on which features have promotions applying to them or some other effects you'd want to display in the numTxt or not anyways etc -->
		elif self.iFeature == iForest or self.iFeature == iJungle:
			# <!-- custom: raise an error if asset does not exist -->
			iPromotionWoodsman1 = getInfoTypeOrFail("PROMOTION_WOODSMAN1", gc)
			iPromotionWoodsman2 = getInfoTypeOrFail("PROMOTION_WOODSMAN2", gc)
			iPromotionWoodsman3 = getInfoTypeOrFail("PROMOTION_WOODSMAN3", gc)

			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				iFeatureAttack = unitInfo.getFeatureAttackModifier(self.iFeature)
				iFeatureDefense = unitInfo.getFeatureDefenseModifier(self.iFeature)

				isHasW1 = unitInfo.getFreePromotions(iPromotionWoodsman1)
				isHasW2 = unitInfo.getFreePromotions(iPromotionWoodsman2)
				isHasW3 = unitInfo.getFreePromotions(iPromotionWoodsman3)

				if ((iFeatureAttack != 0) or (iFeatureDefense != 0) or isHasW1 or isHasW2 or isHasW3):
					# Column index (always 0 when numLists=1)
					columnIndex = 0
					screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

					if iFeatureAttack != 0 or iFeatureDefense != 0:
						numTxt = get_numTxt_attack_defense_modifiers(iFeatureAttack, iFeatureDefense)
					else:
						s = ""
						if isHasW1:
							s = "W1"
						if isHasW2:
							if s:
								s += "+2"
							else:
								s = "W2"
						if isHasW3:
							if s:
								s += "+3"
							else:
								s = "W3"
						if s:
							numTxt = s

					extraCorrectionX = get_extra_correction_x(numTxt)
					add_multilist_numTxt_under_button(multiListX, multiListY, extraCorrectionX, iButtonIndex, BUTTON_SIZE, maxButtonsPerRow, numTxt, screen, self.top, WidgetTypes.WIDGET_GENERAL, CvUtil.FONT_CENTER_JUSTIFY)

					#isButtonFound = True
					iButtonIndex += 1

		else:
			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				iFeatureAttack = unitInfo.getFeatureAttackModifier(self.iFeature)
				iFeatureDefense = unitInfo.getFeatureDefenseModifier(self.iFeature)

				if iFeatureAttack != 0 or iFeatureDefense != 0:
					# Column index (always 0 when numLists=1)
					columnIndex = 0
					screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

					numTxt = get_numTxt_attack_defense_modifiers(iFeatureAttack, iFeatureDefense)
					extraCorrectionX = get_extra_correction_x(numTxt)
					add_multilist_numTxt_under_button(multiListX, multiListY, extraCorrectionX, iButtonIndex, BUTTON_SIZE, maxButtonsPerRow, numTxt, screen, self.top, WidgetTypes.WIDGET_GENERAL, CvUtil.FONT_CENTER_JUSTIFY)

					#isButtonFound = True
					iButtonIndex += 1



	def placeUnitsImpassable(self):
		xPanel = self.X_UNITS_IMPASSABLE
		yPanel = self.Y_UNITS_IMPASSABLE
		wPanel = self.W_UNITS_IMPASSABLE
		hPanel = self.H_UNITS_IMPASSABLE

		txtKeyPanel = "TXT_KEY_PEDIA_FEATURE_UNITS_IMPASSABLE"

		# <!-- custom: https://forums.civfanatics.com/threads/make-ice-workable.462809/?utm_source=chatgpt.com based on this provided nicely to me by chatgpt anyways etc, it seems the ice feature (called as of now "ice cap" feature in advciv-sas anyways etc is impassable but can be walked on if a unit has such a flag, so using a code similar to the terrain_peak handling in sevopedia terrain's as of now placeUnitsImpassable anyways etc anyways etc anyways etc -->
		iIce = getInfoTypeOrFail("FEATURE_ICE", gc)

		if self.iFeature == iIce:
			txtKeyPanel = "TXT_KEY_PEDIA_FEATURE_UNITS_IMPASSABLE_ICE"

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

		if self.iFeature == iIce:
			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				# <!-- custom: allow any domain unlike for the peak code, so workers could walk on the water ice cap feature, unlike in peak where as of now naval units are not displayed as being able to walk on peak as it would make less sense too even though theoretically possible if i am not mistaken (boat with legs... xd but anyways etc..), so having permissive domain any allowed here unlike in peak code if i am not mistaken anyways etc (but now that i think of it why not, such robotic things or mechanical walking things on a naval unit making it hybrid are probably not too far fetched maybe probably even exists or/and in sci-fi or dream if i may say or such other or not or other or etc but anyways etc) ; also not checking unitInfo.isCanMoveAllTerrain() since the ice that is impassable is the ice cap feature if i am not mistaken not the terrain anyways etc -->
				if not unitInfo.isCanMoveImpassable():
					# Column index (always 0 when numLists=1)
					columnIndex = 0
					screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

		else:
			for iUnit in xrange(gc.getNumUnitInfos()):
				unitInfo = gc.getUnitInfo(iUnit)

				if unitInfo.isGraphicalOnly():
					continue

				if (unitInfo.getFeatureImpassable(self.iFeature) or (unitInfo.getFeaturePassableTech(self.iFeature) != -1)):
					# Column index (always 0 when numLists=1)
					columnIndex = 0
					screen.appendMultiListButton(rowListName, unitInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)



	def placeHistory(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		text = self.top.getNextWidgetName()
		info = gc.getFeatureInfo(self.iFeature)

		screen.addPanel(panel, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50 )

		szHistory = info.getCivilopedia()
		screen.addMultilineText(text, szHistory, self.X_HISTORY + 10, self.Y_HISTORY + 30, self.W_HISTORY - 20, self.H_HISTORY - 40, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

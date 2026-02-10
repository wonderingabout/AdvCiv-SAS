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
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#



from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
from SASUtils import getInfoTypeOrFail

from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

IMPROVEMENT_LEADER_CACHE = None



def precomputeImprovementLeaderCache():
	global IMPROVEMENT_LEADER_CACHE

	if IMPROVEMENT_LEADER_CACHE is not None:
		return IMPROVEMENT_LEADER_CACHE

	leaderIds, leaderToCiv, unused_total = get_real_leader_maps_and_count(EXCLUDED_LEADER_TYPES_FROM_SEVOPEDIA)
	improvementData = {}

	for iImprovement in range(gc.getNumImprovementInfos()):
		weightToLeaders = {}
		for iLeader in leaderIds:
			leaderInfo = gc.getLeaderHeadInfo(iLeader)
			iWeight = leaderInfo.getImprovementWeightModifier(iImprovement)
			if iWeight != 0:
				if iWeight not in weightToLeaders:
					weightToLeaders[iWeight] = []
				weightToLeaders[iWeight].append(iLeader)

		if not weightToLeaders:
			improvementData[iImprovement] = (None, (), 0)
			continue

		weightsSorted = sorted(weightToLeaders.keys(), reverse=True)
		maxLeaders = 1
		for weight in weightsSorted:
			if len(weightToLeaders[weight]) > maxLeaders:
				maxLeaders = len(weightToLeaders[weight])
		improvementData[iImprovement] = (weightToLeaders, tuple(weightsSorted), maxLeaders)

	IMPROVEMENT_LEADER_CACHE = {
		"leaderIds": leaderIds,
		"leaderToCiv": leaderToCiv,
		"improvements": improvementData,
	}

	print("Sevopedia Improvement leader cache prebuilt. This should appear only once per gaming session.")
	return IMPROVEMENT_LEADER_CACHE



class SevoPediaImprovement:

	def __init__(self, main):
		self.iImprovement = -1
		self.top = main
		self.SAS_iBuildRoad = getInfoTypeOrFail("BUILD_ROAD")
		self.SAS_iBuildRailroad = getInfoTypeOrFail("BUILD_RAILROAD")
		self.I_CONCEPT_IRRIGATION = getInfoTypeOrFail("CONCEPT_IRRIGATION")
		self.I_TERRAIN_HILL = getInfoTypeOrFail("TERRAIN_HILL")

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		self.X_IMPROVEMENT_PANE = self.top.X_PEDIA_PAGE
		self.Y_IMPROVEMENT_PANE = self.top.Y_PEDIA_PAGE
		self.H_REQUIRES = 110
		self.H_IMPROVEMENT_PANE = (2 * self.H_REQUIRES) + self.SMALL_MARGIN
		self.W_IMPROVEMENT_PANE = self.H_IMPROVEMENT_PANE

		self.W_ICON = 150
		self.H_ICON = 150
		self.X_ICON = self.X_IMPROVEMENT_PANE + (self.H_IMPROVEMENT_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_IMPROVEMENT_PANE + (self.H_IMPROVEMENT_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64
		self.X_INFO_TEXT = self.X_IMPROVEMENT_PANE + 8
		self.Y_INFO_TEXT = self.Y_IMPROVEMENT_PANE + 8
		self.W_INFO_TEXT = self.W_IMPROVEMENT_PANE - 16
		self.H_INFO_TEXT = 60

		self.W_BONUS_YIELDS = 260
		self.W_MOST_YIELDS = self.W_BONUS_YIELDS

		self.X_BONUS_YIELDS = self.top.R_PEDIA_PAGE - self.W_BONUS_YIELDS
		self.Y_BONUS_YIELDS = self.Y_IMPROVEMENT_PANE
		self.H_BONUS_YIELDS = self.top.B_PEDIA_PAGE - self.Y_BONUS_YIELDS

		self.X_MOST_YIELDS = self.X_BONUS_YIELDS - self.W_MOST_YIELDS - self.MEDIUM_MARGIN
		self.Y_MOST_YIELDS = self.Y_BONUS_YIELDS
		self.H_MOST_YIELDS = self.H_BONUS_YIELDS

		leftAreaRight = self.X_MOST_YIELDS - self.MEDIUM_MARGIN
		self.W_LEFT_AREA = leftAreaRight - self.X_IMPROVEMENT_PANE

		self.W_BUILD_PANEL = 84
		self.H_BUILD_PANEL = self.H_REQUIRES
		self.W_REQUIRES = 84

		self.X_BUILD_PANEL = self.X_IMPROVEMENT_PANE + self.W_IMPROVEMENT_PANE + self.MEDIUM_MARGIN
		self.Y_BUILD_PANEL = self.Y_IMPROVEMENT_PANE

		self.X_REQUIRES = self.X_BUILD_PANEL
		self.Y_REQUIRES = self.Y_BUILD_PANEL + self.H_BUILD_PANEL + self.SMALL_MARGIN

		self.X_TERRAIN_MAKES_VALIDS = self.X_BUILD_PANEL + self.W_BUILD_PANEL + self.MEDIUM_MARGIN
		self.Y_TERRAIN_MAKES_VALIDS = self.Y_IMPROVEMENT_PANE
		self.H_TERRAIN_MAKES_VALIDS = self.H_REQUIRES

		self.X_FEATURE_MAKES_VALIDS = self.X_TERRAIN_MAKES_VALIDS
		self.Y_FEATURE_MAKES_VALIDS = self.Y_TERRAIN_MAKES_VALIDS + self.H_TERRAIN_MAKES_VALIDS + self.SMALL_MARGIN
		self.H_FEATURE_MAKES_VALIDS = self.H_REQUIRES

		self.H_TOP_RIGHT_STACK = max(self.H_TERRAIN_MAKES_VALIDS + self.SMALL_MARGIN + self.H_FEATURE_MAKES_VALIDS, self.H_BUILD_PANEL + self.SMALL_MARGIN + self.H_REQUIRES)
		availableAfterTerrain = leftAreaRight - self.X_TERRAIN_MAKES_VALIDS
		if availableAfterTerrain < 0:
			availableAfterTerrain = 0

		preferredAnim = min(self.H_IMPROVEMENT_PANE, self.H_TOP_RIGHT_STACK)
		minSidePanelW = 180
		if availableAfterTerrain - self.MEDIUM_MARGIN - preferredAnim < minSidePanelW:
			preferredAnim = max(140, availableAfterTerrain - self.MEDIUM_MARGIN - minSidePanelW)
		if preferredAnim < 120:
			preferredAnim = min(availableAfterTerrain, self.H_TOP_RIGHT_STACK)

		self.W_IMPROVEMENT_ANIMATION = min(preferredAnim, availableAfterTerrain)
		self.H_IMPROVEMENT_ANIMATION = self.W_IMPROVEMENT_ANIMATION
		self.X_IMPROVEMENT_ANIMATION = leftAreaRight - self.W_IMPROVEMENT_ANIMATION
		self.Y_IMPROVEMENT_ANIMATION = self.Y_IMPROVEMENT_PANE

		self.W_TERRAIN_MAKES_VALIDS = self.X_IMPROVEMENT_ANIMATION - self.MEDIUM_MARGIN - self.X_TERRAIN_MAKES_VALIDS
		if self.W_TERRAIN_MAKES_VALIDS < 120:
			self.W_TERRAIN_MAKES_VALIDS = 120
			self.X_IMPROVEMENT_ANIMATION = self.X_TERRAIN_MAKES_VALIDS + self.W_TERRAIN_MAKES_VALIDS + self.MEDIUM_MARGIN
			self.W_IMPROVEMENT_ANIMATION = leftAreaRight - self.X_IMPROVEMENT_ANIMATION
			self.H_IMPROVEMENT_ANIMATION = self.W_IMPROVEMENT_ANIMATION

		self.W_FEATURE_MAKES_VALIDS = self.W_TERRAIN_MAKES_VALIDS

		self.H_TOP_ROW = max(self.H_IMPROVEMENT_PANE, self.H_TOP_RIGHT_STACK, self.H_IMPROVEMENT_ANIMATION)

		self.X_IMPROVEMENT_LEADERS = self.X_IMPROVEMENT_PANE
		self.Y_IMPROVEMENT_LEADERS = self.Y_IMPROVEMENT_PANE + self.H_TOP_ROW + self.SMALL_MARGIN
		self.W_IMPROVEMENT_LEADERS = leftAreaRight - self.X_IMPROVEMENT_PANE

		self.H_SPECIAL = 295
		self.H_HISTORY = 295
		self.Y_SPECIAL = self.top.B_PEDIA_PAGE - self.H_SPECIAL
		self.X_SPECIAL = self.X_IMPROVEMENT_PANE
		self.W_SPECIAL = min(360, (self.W_IMPROVEMENT_LEADERS / 3) + 100)
		self.X_HISTORY = self.X_SPECIAL + self.W_SPECIAL + self.MEDIUM_MARGIN
		self.Y_HISTORY = self.Y_SPECIAL
		self.W_HISTORY = leftAreaRight - self.X_HISTORY
		self.H_HISTORY = self.H_SPECIAL

		self.H_IMPROVEMENT_LEADERS = self.Y_SPECIAL - self.SMALL_MARGIN - self.Y_IMPROVEMENT_LEADERS
		if self.H_IMPROVEMENT_LEADERS < 0:
			self.H_IMPROVEMENT_LEADERS = 0

		self.X_ROTATION_IMPROVEMENT_ANIMATION = -20
		self.Z_ROTATION_IMPROVEMENT_ANIMATION = 30
		self.SCALE_ANIMATION = 0.7

		self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER = 22

		# <!-- custom: Leader icon sizes now use centralized INCHART_* constants from _sevopedia_helpers.
		# IMPROVEMENT_LEADER_ICON_SIZE, IMPROVEMENT_LEADER_BUTTON_SPACING, IMPROVEMENT_LEADER_ROW_H replaced by
		# INCHART_ICON_SIZE, INCHART_ICON_SPACING, INCHART_ROW_HEIGHT -->



	def interfaceScreen(self, iImprovement):
		self.iImprovement = iImprovement

		self.placeImprovementPane()
		self.placeSpecial()
		self.placeBonusYields()
		self.placeImprovementAnimation()
		self.placeBuilds()
		self.placeRequires()
		self.placeMostYields()
		self.placeImprovementLeaderTable()
		self.placeTerrainMakesValids()
		self.placeFeatureMakesValids()
		self.placeHistory()



	def placeImprovementPane(self):
		screen = self.top.getScreen()
		info = gc.getImprovementInfo(self.iImprovement)
		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False, self.X_IMPROVEMENT_PANE, self.Y_IMPROVEMENT_PANE, self.W_IMPROVEMENT_PANE, self.H_IMPROVEMENT_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: was PanelStyles.PANEL_STYLE_MAIN -->
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), info.getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		panel = self.top.getNextWidgetName()
		screen.addListBoxGFC(panel, "", self.X_INFO_TEXT, self.Y_INFO_TEXT, self.W_INFO_TEXT, self.H_INFO_TEXT, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panel, False)
		screen.appendListBoxString(panel, u"<font=4b>" + info.getDescription() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_CENTER_JUSTIFY)
		screen.appendListBoxString(panel, localText.getText("TXT_KEY_PEDIA_IMPROVEMENT", ()), WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_CENTER_JUSTIFY)

		# <!-- custom: move base yield info from yields panel to the improvement_pane panel, prettier or/adn clearer/more accurate as well maybe (a bit like in sevopedia terrain and sevopedia feature) -->
		# <!-- custom: line removed that seemed safe to do see diff with earlier code for comparison if needed -->
		# <!-- custom: this part is for yields that do not require any additional tech than the one required to gain access to the ressources (for example + 2 hammer with mine, + 4 commerce with town)
		s = u""
		nCount = 0

		for k in range(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = info.getYieldChange(k)

			if iYieldChange != 0:
				if iYieldChange > 0:
					sign = "+"
				else:
					sign = ""
				s += (u"%s%i%c " % (sign, iYieldChange, gc.getYieldInfo(k).getChar()))
				nCount += 1
		
		if nCount > 0:
			szYield = u"<font=4>%s</font>" % s

			xCenteringAdjust = 0
			for i in range(nCount):
				xCenteringAdjust -= 23

			xCenteringPositioning = ((self.W_IMPROVEMENT_PANE-10) / 2) - 4
			yBottomPositioning = self.H_IMPROVEMENT_PANE - 44
			
			screen.addMultilineText(self.top.getNextWidgetName(), szYield, self.X_IMPROVEMENT_PANE + xCenteringPositioning + xCenteringAdjust +5, self.Y_IMPROVEMENT_PANE - 13 + yBottomPositioning, self.W_IMPROVEMENT_PANE-10, self.H_IMPROVEMENT_PANE-10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: prettier and clearer without the/a header, also gives a bit extra room in case we have many effects to place, and matches sevopedia terrain and feature display as well or more closely  -->
		#screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_IMPROVEMENT_INFO", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )

		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getImprovementHelp(self.iImprovement, True)

		szSpecialText = szSpecialText.replace("\n\n", "\n").strip()

		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL + 10, self.Y_SPECIAL + 30, self.W_SPECIAL - 20, self.H_SPECIAL - 40, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeBonusYields(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: prettier and clearer without the/a header, also gives a bit extra room in case we have many effects to place, and matches sevopedia terrain and feature display as well or more closely  -->
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_SAS_BONUSS_YIELDS", ()), "", True, True, self.X_BONUS_YIELDS, self.Y_BONUS_YIELDS, self.W_BONUS_YIELDS, self.H_BONUS_YIELDS, PanelStyles.PANEL_STYLE_BLUE50 )
		info = gc.getImprovementInfo(self.iImprovement)
		for j in range(gc.getNumBonusInfos()):
			bFirst = True
			szYield = u""
			bEffect = False
			for k in range(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = info.getImprovementBonusYield(j, k)
				if iYieldChange != 0:
					bEffect = True
					# Uncomment for 3.13 behavior. Note that Uranium shows incorrect hammer yield (should be +2)
					#iYieldChange += info.getYieldChange(k)
					if bFirst:
						bFirst = False
					else:
						szYield += u", "
					if iYieldChange > 0:
						sign = u"+"
					else:
						sign = u""
					szYield += (u"%s%i%c" % (sign, iYieldChange, gc.getYieldInfo(k).getChar()))
			if bEffect:
				childPanelName = self.top.getNextWidgetName()
				screen.attachPanel(panelName, childPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)
				screen.attachLabel(childPanelName, "", "  ")
				screen.attachImageButton( childPanelName, "", gc.getBonusInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, j, 1, False )
				screen.attachLabel(childPanelName, "", u"<font=4>" + szYield + u"</font>")



	def placeImprovementAnimation(self):
		screen = self.top.getScreen()
		screen.addImprovementGraphicGFC(self.top.getNextWidgetName(), self.iImprovement, self.X_IMPROVEMENT_ANIMATION, self.Y_IMPROVEMENT_ANIMATION, self.W_IMPROVEMENT_ANIMATION, self.H_IMPROVEMENT_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_IMPROVEMENT_ANIMATION, self.Z_ROTATION_IMPROVEMENT_ANIMATION, self.SCALE_ANIMATION, True)



	def placeBuilds(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_BUILD", ()), "", False, True, self.X_BUILD_PANEL, self.Y_BUILD_PANEL, self.W_BUILD_PANEL, self.H_BUILD_PANEL, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		bButtonFound = False
		for iBuild in range(gc.getNumBuildInfos()):
			if gc.getBuildInfo(iBuild).getImprovement() == self.iImprovement:
				buildInfo = gc.getBuildInfo(iBuild)
				screen.attachImageButton(panelName, "", buildInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PYTHON, self.top.SAS_PEDIA_PYTHON_BUILD, iBuild, False)
				bButtonFound = True

		if not bButtonFound:
			txtKeyNone = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNone, ())
			yPanelCenter = self.Y_BUILD_PANEL + (self.H_BUILD_PANEL / 2)
			screen.addMultilineText(textName, szText, self.X_BUILD_PANEL + 7, yPanelCenter, self.W_BUILD_PANEL - 14, self.H_BUILD_PANEL - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		bButtonFound = False
		for iBuild in range(gc.getNumBuildInfos()):
			if gc.getBuildInfo(iBuild).getImprovement() == self.iImprovement:
				iTech = gc.getBuildInfo(iBuild).getTechPrereq()
				if iTech > -1:
					screen.attachImageButton( panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )
					bButtonFound = True

		if not bButtonFound:
			txtKeyNone = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNone, ())
			yPanelCenter = self.Y_REQUIRES + (self.H_REQUIRES / 2)
			screen.addMultilineText(textName, szText, self.X_REQUIRES + 7, yPanelCenter, self.W_REQUIRES - 14, self.H_REQUIRES - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: code entirely replaced with a code provided by claude ai based on m-e mod 's placeImprovements code (in (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\Middle-earth\Assets\Python\Screens\PlatyPedia\PlatyPediaImprovement.py ), also with gemini ai's help too thanks a lot as well, and adjusted or not for advciv-sas -->
	def placeMostYields(self):
		screen = self.top.getScreen()
		panelX = self.X_MOST_YIELDS
		panelY = self.Y_MOST_YIELDS
		panelW = self.W_MOST_YIELDS
		panelH = self.H_MOST_YIELDS

		screen.addPanel(self.top.getNextWidgetName(), localText.getText("TXT_KEY_PEDIA_SEVOPEDIA_IMPROVEMENT_MOST_TILE_YIELD_CHANGES", ()), "", True, True, panelX, panelY, panelW, panelH, PanelStyles.PANEL_STYLE_BLUE50)
		scrollPanelName = self.top.getNextWidgetName()
		screen.addScrollPanel(scrollPanelName, "", panelX - 2, panelY + 20, panelW + 4, panelH - 46, PanelStyles.PANEL_STYLE_EMPTY)

		iY = 6
		iButtonSize = 64  # Use default 64px button size for better visibility
		Info = gc.getImprovementInfo(self.iImprovement)

		# Irrigated yield changes
		sText = ""
		for k in xrange(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = Info.getIrrigatedYieldChange(k)
			if iYieldChange != 0:
				sText += u"%+d%c" % (iYieldChange, gc.getYieldInfo(k).getChar())
		if len(sText) > 0:
			screen.setImageButtonAt(self.top.getNextWidgetName(), scrollPanelName, ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_IRRIGATION").getPath(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PEDIA_DESCRIPTION, CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT, self.I_CONCEPT_IRRIGATION)
			screen.setLabelAt(self.top.getNextWidgetName(), scrollPanelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			iY += (iButtonSize + 8)

		# Hills yield changes
		sText = ""
		for k in xrange(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = Info.getHillsYieldChange(k)
			if iYieldChange != 0:
				sText += u"%+d%c" % (iYieldChange, gc.getYieldInfo(k).getChar())
		if len(sText) > 0:
			iHill = self.I_TERRAIN_HILL
			screen.setImageButtonAt(self.top.getNextWidgetName(), scrollPanelName, gc.getTerrainInfo(iHill).getButton(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, iHill, 1)
			screen.setLabelAt(self.top.getNextWidgetName(), scrollPanelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			iY += (iButtonSize + 8)

		# River yield changes
		sText = ""
		for k in xrange(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = Info.getRiverSideYieldChange(k)
			if iYieldChange != 0:
				sText += u"%+d%c" % (iYieldChange, gc.getYieldInfo(k).getChar())
		if len(sText) > 0:
			# <!-- custom: unlike in m-e mod or so it seems, we don't use WidgetTypes.WIDGET_PYTHON (for/in this placeMostYields method) and id 6783 neither, so go for a simpler implementation, that matches how we redirect using concepts in sevopedia unit as of now to the concept_cities for example, we now have a new concept_rivers to redirect to now in advciv-sas, use that rather, is also thanks to gemini ai's help, and adjusted or not by me too hehe if i may say in this casefor advciv-sas -->
			#screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_RIVER_PLACEMENT").getPath(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PYTHON, 6783, -1)
			#screen.setLabelAt(self.top.getNextWidgetName(), panelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			# This button now links to the Civilopedia concept for Rivers.
			# Its tooltip and click behavior are handled by the built-in Civ4 widget system.
			# Ensure 'CONCEPT_RIVERS' is defined in your Civilopedia XML.
			riversConceptID = get_concept_id("CONCEPT_RIVERS")
			widgetType, widgetID1, widgetID2 = get_concept_widgetType_widgetID1_widgetID2(riversConceptID, WidgetTypes, CivilopediaPageTypes)
			screen.setImageButtonAt(self.top.getNextWidgetName(), scrollPanelName, ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_RIVER_PLACEMENT").getPath(), 0, iY, iButtonSize, iButtonSize, widgetType, widgetID1, widgetID2)
			screen.setLabelAt(self.top.getNextWidgetName(), scrollPanelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			iY += (iButtonSize + 8)

		# Tech yield changes
		for item in xrange(gc.getNumTechInfos()):
			sText = ""
			for k in xrange(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = Info.getTechYieldChanges(item, k)
				if iYieldChange != 0:
					sText += u"%+d%c" % (iYieldChange, gc.getYieldInfo(k).getChar())
			if len(sText):
				screen.setImageButtonAt(self.top.getNextWidgetName(), scrollPanelName, gc.getTechInfo(item).getButton(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, item, 1)
				screen.setLabelAt(self.top.getNextWidgetName(), scrollPanelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				iY += (iButtonSize + 8)

		# Civic yield changes
		for item in xrange(gc.getNumCivicInfos()):
			sText = ""
			for k in xrange(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = gc.getCivicInfo(item).getImprovementYieldChanges(self.iImprovement, k)
				if iYieldChange != 0:
					sText += u"%+d%c" % (iYieldChange, gc.getYieldInfo(k).getChar())
			if len(sText):
				screen.setImageButtonAt(self.top.getNextWidgetName(), scrollPanelName, gc.getCivicInfo(item).getButton(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, item, 1)
				screen.setLabelAt(self.top.getNextWidgetName(), scrollPanelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				iY += (iButtonSize + 8)

		# Route yield changes
		for item in xrange(gc.getNumRouteInfos()):
			sText = ""
			for k in xrange(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = Info.getRouteYieldChanges(item, k)
				if iYieldChange != 0:
					sText += u"%+d%c" % (iYieldChange, gc.getYieldInfo(k).getChar())
			if len(sText):
				# <!-- custom: link route yield changes to the real Build entries (road/railroad) now that Builds are a category. This removes
				# the old concept route hack and keeps behavior consistent with other Build links. Credit: Claude Opus 4.5 + GPT-5.2-Codex. (GPT-5.2-Codex (summarized)) -->
				routeInfo = gc.getRouteInfo(item)
				iBuild = -1
				if routeInfo.getType() == "ROUTE_ROAD":
					iBuild = self.SAS_iBuildRoad
				elif routeInfo.getType() == "ROUTE_RAILROAD":
					iBuild = self.SAS_iBuildRailroad
				if iBuild < 0:
					raise Exception("SevoPediaImprovement: missing Build for route %s" % routeInfo.getType())

				screen.setImageButtonAt(self.top.getNextWidgetName(), scrollPanelName, routeInfo.getButton(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PYTHON, self.top.SAS_PEDIA_PYTHON_BUILD, iBuild)
				screen.setLabelAt(self.top.getNextWidgetName(), scrollPanelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				iY += (iButtonSize + 8)


	def placeImprovementLeaderTable(self):
		screen = self.top.getScreen()
		xPanel = self.X_IMPROVEMENT_LEADERS
		yPanel = self.Y_IMPROVEMENT_LEADERS
		wPanel = self.W_IMPROVEMENT_LEADERS
		hPanel = self.H_IMPROVEMENT_LEADERS

		screen.addPanel(self.top.getNextWidgetName(), localText.getText("TXT_KEY_PEDIA_SAS_IMPROVEMENT_FAVORED_BY_LEADERS", ()), "", True, True, xPanel, yPanel, wPanel, hPanel, PanelStyles.PANEL_STYLE_BLUE50)

		cache = IMPROVEMENT_LEADER_CACHE
		if cache is None:
			cache = precomputeImprovementLeaderCache()

		leaderToCiv = cache["leaderToCiv"]
		weightToLeaders, weightsSorted, maxLeaders = cache["improvements"].get(self.iImprovement, (None, (), 0))

		if not weightToLeaders:
			inchart_show_no_content_text(screen, self.top, xPanel, yPanel, wPanel, hPanel)
			return

		tableMargin = INCHART_TABLE_MARGIN
		tableX = xPanel + tableMargin
		tableY = yPanel + 30
		tableW = wPanel - (2 * tableMargin)
		tableH = hPanel - 40

		weightColW = 60
		countColW = 60
		fixedColsW = weightColW + countColW
		leaderColW, maxLeaders = inchart_calc_icon_col_width(tableW, fixedColsW, maxLeaders)

		tableName = self.top.getNextWidgetName()
		screen.addTableControlGFC(tableName, 2 + maxLeaders, tableX, tableY, tableW, tableH, True, False, INCHART_ROW_HEIGHT, INCHART_ROW_HEIGHT, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSort(tableName)

		screen.setTableColumnHeader(tableName, 0, localText.getText("TXT_KEY_PEDIA_SAS_WEIGHT", ()), weightColW)
		screen.setTableColumnHeader(tableName, 1, localText.getText("TXT_KEY_PEDIA_SAS_COUNT", ()), countColW)
		inchart_set_icon_column_headers(screen, tableName, 2, maxLeaders, leaderColW)

		for weight in weightsSorted:
			iRow = screen.appendTableRow(tableName)
			screen.setTableText(tableName, 0, iRow, u"<font=2>%+d</font>" % weight, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
			leaderCount = len(weightToLeaders[weight])
			screen.setTableText(tableName, 1, iRow, u"<font=2>%d</font>" % leaderCount, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
			inchart_set_icon_cells(screen, tableName, iRow, weightToLeaders[weight], 2, maxLeaders, INCHART_ICON_TYPE_LEADER, {"leaderToCiv": leaderToCiv})


	# <!-- custom: _setLeaderIconCells removed - now uses centralized inchart_set_icon_cells from _sevopedia_helpers -->

	# <!-- custom: new addition thanks to chatgpt; as for logic this is how it works-functions based on chatgpt's explanation as well as my own research/findings in (translate to english using web browser or such) https://gforestshade.github.io/kujira/post/civ4improvementinfos/#terrainmakesvalids: if some terrains are specified then the improvement is only allowed on these terrains, else improvement is allowed on all terrains; not sure i got it all right (in particular in the case of irrigation or such conditions seemingly allowing the improvement on a terrain even if not listed here), so i am not sure it is all accurate but maybe is, check to be sure, and adjust this if needed; i implemented it as such and also added an explicative text that maybe the restriction could be elsewhere if not in improvementinfos. -->
	def placeTerrainMakesValids(self):
		xPanel = self.X_TERRAIN_MAKES_VALIDS
		yPanel = self.Y_TERRAIN_MAKES_VALIDS
		wPanel = self.W_TERRAIN_MAKES_VALIDS
		hPanel = self.H_TERRAIN_MAKES_VALIDS

		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_TERRAIN_MAKES_VALIDS", ()), "", False, True, xPanel, yPanel, wPanel, hPanel, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")

		isButtonFound = False

		for iTerrain in xrange(gc.getNumTerrainInfos()):
			if gc.getImprovementInfo(self.iImprovement).getTerrainMakesValid(iTerrain):
				isButtonFound = True
				screen.attachImageButton(panelName, "", gc.getTerrainInfo(iTerrain).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, iTerrain, 1, False)

		if not isButtonFound:
			txtKeyNoButtonFound = "TXT_KEY_PEDIA_TERRAIN_MAKES_VALIDS_NO_RESTRICTION"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoButtonFound, ())
			yPanelCenter = yPanel + (hPanel / 2)
			screen.addMultilineText(textName, szText, xPanel + 7, yPanelCenter, wPanel - 14, hPanel - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeFeatureMakesValids(self):
		xPanel = self.X_FEATURE_MAKES_VALIDS
		yPanel = self.Y_FEATURE_MAKES_VALIDS
		wPanel = self.W_FEATURE_MAKES_VALIDS
		hPanel = self.H_FEATURE_MAKES_VALIDS

		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_FEATURE_MAKES_VALIDS", ()), "", False, True, xPanel, yPanel, wPanel, hPanel, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")

		isButtonFound = False

		for iFeature in xrange(gc.getNumFeatureInfos()):
			if gc.getImprovementInfo(self.iImprovement).getFeatureMakesValid(iFeature):
				isButtonFound = True
				screen.attachImageButton(panelName, "", gc.getFeatureInfo(iFeature).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE, iFeature, 1, False)

		if not isButtonFound:
			txtKeyNoButtonFound = "TXT_KEY_PEDIA_FEATURE_MAKES_VALIDS_NO_RESTRICTION"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoButtonFound, ())
			yPanelCenter = yPanel + (hPanel / 2)
			screen.addMultilineText(textName, szText, xPanel + 7, yPanelCenter, wPanel - 14, hPanel - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: addition based on our existing mod's code in some other class, as for pedia entries, imported from m-e mod (see main readme for mod abbreviation details in as of now credits section) (but i also found them later in c2c mod and they are seemingly the same but the file is sadly/unfortunately way too bloated so going for the m-e mod one(s if talking about the assets themselves in thinking/saying so)) -->
	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		textName = self.top.getNextWidgetName()
		screen.addMultilineText(textName, gc.getImprovementInfo(self.iImprovement).getCivilopedia(), self.X_HISTORY + 7, self.Y_HISTORY + 10 + self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER, self.W_HISTORY - 30, self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

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



from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums

from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



class SevoPediaImprovement:

	def __init__(self, main):
		self.iImprovement = -1
		self.top = main

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		self.X_IMPROVEMENT_PANE = self.top.X_PEDIA_PAGE
		self.Y_IMPROVEMENT_PANE = self.top.Y_PEDIA_PAGE
		self.W_IMPROVEMENT_PANE = 210
		self.H_IMPROVEMENT_PANE = 210

		self.W_ICON = 150
		self.H_ICON = 150
		self.X_ICON = self.X_IMPROVEMENT_PANE + (self.H_IMPROVEMENT_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_IMPROVEMENT_PANE + (self.H_IMPROVEMENT_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.W_BONUS_YIELDS = 260
		self.W_IMPROVEMENT_ANIMATION = ((self.top.R_PEDIA_PAGE - self.top.X_PEDIA_PAGE) - self.W_BONUS_YIELDS - (2 * self.MEDIUM_MARGIN)) / 2
		self.W_SPECIAL = self.W_IMPROVEMENT_ANIMATION - self.MEDIUM_MARGIN - self.W_IMPROVEMENT_PANE

		self.X_SPECIAL = self.X_IMPROVEMENT_PANE + self.W_IMPROVEMENT_PANE + self.MEDIUM_MARGIN
		self.Y_SPECIAL = self.Y_IMPROVEMENT_PANE
		self.H_SPECIAL = self.H_IMPROVEMENT_PANE

		self.X_BONUS_YIELDS = self.X_SPECIAL + self.W_SPECIAL + self.MEDIUM_MARGIN
		self.Y_BONUS_YIELDS = self.Y_IMPROVEMENT_PANE
		self.H_BONUS_YIELDS = self.top.B_PEDIA_PAGE - self.Y_BONUS_YIELDS

		self.H_REQUIRES = 110

		self.X_IMPROVEMENT_ANIMATION = self.X_BONUS_YIELDS + self.W_BONUS_YIELDS + self.MEDIUM_MARGIN
		self.Y_IMPROVEMENT_ANIMATION = self.Y_IMPROVEMENT_PANE + 7
		self.H_IMPROVEMENT_ANIMATION = self.H_IMPROVEMENT_PANE + self.SMALL_MARGIN + (2 * self.H_REQUIRES)  - 7

		self.X_ROTATION_IMPROVEMENT_ANIMATION = -20
		self.Z_ROTATION_IMPROVEMENT_ANIMATION = 30
		self.SCALE_ANIMATION = 0.7

		self.X_REQUIRES = self.X_IMPROVEMENT_PANE
		self.Y_REQUIRES = self.Y_IMPROVEMENT_PANE + self.H_IMPROVEMENT_PANE + self.SMALL_MARGIN
		self.W_REQUIRES = self.W_IMPROVEMENT_ANIMATION

		self.X_MOST_YIELDS = self.X_IMPROVEMENT_PANE
		self.Y_MOST_YIELDS = self.Y_REQUIRES + self.H_REQUIRES + self.SMALL_MARGIN
		self.W_MOST_YIELDS = self.W_IMPROVEMENT_ANIMATION
		self.H_MOST_YIELDS = self.top.B_PEDIA_PAGE - self.Y_MOST_YIELDS

		self.X_TERRAIN_MAKES_VALIDS = self.X_IMPROVEMENT_ANIMATION
		self.Y_TERRAIN_MAKES_VALIDS = self.Y_IMPROVEMENT_ANIMATION + self.H_IMPROVEMENT_ANIMATION + self.SMALL_MARGIN
		self.W_TERRAIN_MAKES_VALIDS = self.W_IMPROVEMENT_ANIMATION
		self.H_TERRAIN_MAKES_VALIDS = self.H_REQUIRES

		self.X_FEATURE_MAKES_VALIDS = self.X_IMPROVEMENT_ANIMATION
		self.Y_FEATURE_MAKES_VALIDS = self.Y_TERRAIN_MAKES_VALIDS + self.H_TERRAIN_MAKES_VALIDS + self.SMALL_MARGIN
		self.W_FEATURE_MAKES_VALIDS = self.W_IMPROVEMENT_ANIMATION
		self.H_FEATURE_MAKES_VALIDS = self.H_REQUIRES

		self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER = 22

		self.X_HISTORY = self.X_IMPROVEMENT_ANIMATION
		self.Y_HISTORY = self.Y_FEATURE_MAKES_VALIDS + self.H_FEATURE_MAKES_VALIDS + self.SMALL_MARGIN
		self.W_HISTORY = self.W_IMPROVEMENT_ANIMATION
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY



	def interfaceScreen(self, iImprovement):
		self.iImprovement = iImprovement

		self.placeImprovementPane()
		self.placeSpecial()
		self.placeBonusYields()
		self.placeImprovementAnimation()
		self.placeRequires()
		self.placeMostYields()
		self.placeTerrainMakesValids()
		self.placeFeatureMakesValids()
		self.placeHistory()



	def placeImprovementPane(self):
		screen = self.top.getScreen()
		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False, self.X_IMPROVEMENT_PANE, self.Y_IMPROVEMENT_PANE, self.W_IMPROVEMENT_PANE, self.H_IMPROVEMENT_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: was PanelStyles.PANEL_STYLE_MAIN -->
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getImprovementInfo(self.iImprovement).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		# <!-- custom: move base yield info from yields panel to the improvement_pane panel, prettier or/adn clearer/more accurate as well maybe (a bit like in sevopedia terrain and sevopedia feature) -->
		# <!-- custom: line removed that seemed safe to do see diff with earlier code for comparison if needed -->
		# <!-- custom: this part is for yields that do not require any additional tech than the one required to gain access to the ressources (for example + 2 hammer with mine, + 4 commerce with town)
		s = u""
		nCount = 0

		for k in range(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = gc.getImprovementInfo(self.iImprovement).getYieldChange(k)

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
		# <!-- custom: prettier and clearer without the/a header, also gives a bit extra room in case we have many effects to place, and matches sevopedia terrain and feature display as well or more closely if i am not mistaken too -->
		#screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.addPanel( panelName, "", "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )

		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getImprovementHelp(self.iImprovement, True)

		# Show iTime for building this improvement <!-- custom: (note: not related to feature remove's iTime, here it is about the improvement's iTime (i.e. time to build this improvement))), code provided with the help of chatgpt thanks and adjustments or not too too if i may say and thanks to it i.e. to chatgpt too too too if i may say but etc -->
		if szSpecialText.strip():
			szSpecialText += u"\n"
		bullet = localText.getText("[ICON_BULLET]", ())
		for iBuild in xrange(gc.getNumBuildInfos()):
			buildInfo = gc.getBuildInfo(iBuild)
			if buildInfo.getImprovement() == self.iImprovement:
				iTime = buildInfo.getTime()
				if iTime > 0:
					szSpecialText += u"%sBuild Time: %d" % (bullet, iTime)
					# Improvement is unique per build, so we can stop here after first meaningful (iTime > 0) entry
					break

		#screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL+5, self.Y_SPECIAL+5, self.W_SPECIAL-10, self.H_SPECIAL-10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL+5, self.Y_SPECIAL - 13, self.W_SPECIAL-10, self.H_SPECIAL-10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeBonusYields(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: prettier and clearer without the/a header, also gives a bit extra room in case we have many effects to place, and matches sevopedia terrain and feature display as well or more closely if i am not mistaken too -->
		#screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_SEVOPEDIA_IMPROVEMENT_ON_BONUSES_EXTRA_TILE_YIELD_CHANGES", ()), "", True, True, self.X_BONUS_YIELDS, self.Y_BONUS_YIELDS, self.W_BONUS_YIELDS, self.H_BONUS_YIELDS, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.addPanel( panelName, "", "", True, True, self.X_BONUS_YIELDS, self.Y_BONUS_YIELDS, self.W_BONUS_YIELDS, self.H_BONUS_YIELDS, PanelStyles.PANEL_STYLE_BLUE50 )
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



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		for iBuild in range(gc.getNumBuildInfos()):
			if gc.getBuildInfo(iBuild).getImprovement() == self.iImprovement:
				iTech = gc.getBuildInfo(iBuild).getTechPrereq()
				if iTech > -1:
					screen.attachImageButton( panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )



	# <!-- custom: code entirely replaced with a code provided by claude ai based on m-e mod 's placeImprovements code (in (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\Middle-earth\Assets\Python\Screens\PlatyPedia\PlatyPediaImprovement.py ), also with gemini ai's help too thanks a lot as well, and adjusted or not for advciv-sas -->
	def placeMostYields(self):
		screen = self.top.getScreen()
		screen.addPanel(self.top.getNextWidgetName(), localText.getText("TXT_KEY_PEDIA_SEVOPEDIA_IMPROVEMENT_MOST_TILE_YIELD_CHANGES", ()), "", True, True, self.X_MOST_YIELDS, self.Y_MOST_YIELDS, self.W_MOST_YIELDS, self.H_MOST_YIELDS, PanelStyles.PANEL_STYLE_BLUE50)
		panelName = self.top.getNextWidgetName()
		screen.addScrollPanel(panelName, "", self.X_MOST_YIELDS - 2, self.Y_MOST_YIELDS + 20, self.W_MOST_YIELDS + 4, self.H_MOST_YIELDS - 46, PanelStyles.PANEL_STYLE_EMPTY)

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
			screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_IRRIGATION").getPath(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PEDIA_DESCRIPTION, CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT, gc.getInfoTypeForString("CONCEPT_IRRIGATION"))
			screen.setLabelAt(self.top.getNextWidgetName(), panelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			iY += (iButtonSize + 8)

		# Hills yield changes
		sText = ""
		for k in xrange(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = Info.getHillsYieldChange(k)
			if iYieldChange != 0:
				sText += u"%+d%c" % (iYieldChange, gc.getYieldInfo(k).getChar())
		if len(sText) > 0:
			iHill = gc.getInfoTypeForString("TERRAIN_HILL")
			screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, gc.getTerrainInfo(iHill).getButton(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, iHill, 1)
			screen.setLabelAt(self.top.getNextWidgetName(), panelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
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
			riversConceptID = get_concept_id("CONCEPT_RIVERS", gc)
			widgetType, widgetID1, widgetID2 = get_concept_widgetType_widgetID1_widgetID2(riversConceptID, WidgetTypes, CivilopediaPageTypes)
			screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, ArtFileMgr.getInterfaceArtInfo("WORLDBUILDER_RIVER_PLACEMENT").getPath(), 0, iY, iButtonSize, iButtonSize, widgetType, widgetID1, widgetID2)
			screen.setLabelAt(self.top.getNextWidgetName(), panelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			iY += (iButtonSize + 8)

		# Tech yield changes
		for item in xrange(gc.getNumTechInfos()):
			sText = ""
			for k in xrange(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = Info.getTechYieldChanges(item, k)
				if iYieldChange != 0:
					sText += u"%+d%c" % (iYieldChange, gc.getYieldInfo(k).getChar())
			if len(sText):
				screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, gc.getTechInfo(item).getButton(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, item, 1)
				screen.setLabelAt(self.top.getNextWidgetName(), panelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				iY += (iButtonSize + 8)

		# Civic yield changes
		for item in xrange(gc.getNumCivicInfos()):
			sText = ""
			for k in xrange(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = gc.getCivicInfo(item).getImprovementYieldChanges(self.iImprovement, k)
				if iYieldChange != 0:
					sText += u"%+d%c" % (iYieldChange, gc.getYieldInfo(k).getChar())
			if len(sText):
				screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, gc.getCivicInfo(item).getButton(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, item, 1)
				screen.setLabelAt(self.top.getNextWidgetName(), panelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				iY += (iButtonSize + 8)

		# Route yield changes
		for item in xrange(gc.getNumRouteInfos()):
			sText = ""
			for k in xrange(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = Info.getRouteYieldChanges(item, k)
				if iYieldChange != 0:
					sText += u"%+d%c" % (iYieldChange, gc.getYieldInfo(k).getChar())
			if len(sText):
				# <!-- similarly than for river yield changes, also handle route yield changes differently than in m-e mod, using the newly added in advciv-sas CONCEPT_ROUTE_ROAD and CONCEPT_ROUTE_RAILROAD (as these are as of now our only routeinfo xml entries) as sevopedia pages to redirect to as well -->
				#screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, gc.getRouteInfo(item).getButton(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PYTHON, 6788, item)
				#screen.setLabelAt(self.top.getNextWidgetName(), panelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				# Determine which concept to link to based on the route type.
				routeInfo = gc.getRouteInfo(item)
				# <!-- custom: as of now if i am not mistaken with a conceptIDToRoute of -1 we would get with get_concept_widgetType_widgetID1_widgetID2 an id1 -1 and id2 -1 and widget general too so maybe fine for not crash, else i'd still want it to crash loudly rather than silently, as i said to gemini ai too who approved of it hehe as they (ais) usually do but i believe sitll provided some critical thinking or non-opposition one with my idea maybe if i am not mistaken but in all cases thanks for being my echo chamber xd gemini ai if i may say yo helped me lot if i may say here too and other ais as well thanks i mean too, but since this seems safe enough in handling fallback no redirect, maybe leave as is and do not write a hard crash if missing at load such as what we do as of now for the getters in sevopedia leader for example if i remember correctly and am not mistaken i mean (i think not but in case and to be safe who knows) -->
				# Initialize with invalid ID
				conceptIDToRoute = -1
				# Check if it's a Road or Railroad, or a general Route concept
				if routeInfo.getType() == "ROUTE_ROAD":
					conceptIDToRoute = get_concept_id("CONCEPT_ROUTE_ROAD", gc)
				elif routeInfo.getType() == "ROUTE_RAILROAD":
					conceptIDToRoute = get_concept_id("CONCEPT_ROUTE_RAILROAD", gc)
				# Add more conditions here if you have other specific route types and concepts for them.

				# Get widget parameters for the determined concept.
				widgetType, widgetID1, widgetID2 = get_concept_widgetType_widgetID1_widgetID2(conceptIDToRoute, WidgetTypes, CivilopediaPageTypes)

				# Use the button from the RouteInfo itself
				screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, routeInfo.getButton(), 0, iY, iButtonSize, iButtonSize, widgetType, widgetID1, widgetID2)
				screen.setLabelAt(self.top.getNextWidgetName(), panelName, u"<font=4>" + sText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				iY += (iButtonSize + 8)



	# <!-- custom: new addition thanks to chatgpt; as for logic if i am not mistaken this is how it works-functions based on chatgpt's explanation as well as my own research/findings in (translate to english using web browser or such) https://gforestshade.github.io/kujira/post/civ4improvementinfos/#terrainmakesvalids: if some terrains are specified then the improvement is only allowed on these terrains, else improvement is allowed on all terrains; not sure i got it all right (in particular in the case of irrigation or such conditions seemingly allowing the improvement on a terrain even if not listed here), so i am not sure it is all accurate but maybe is, check to be sure, and adjust this if needed; i implemented it as such and also added an explicative text that maybe the restriction could be elsewhere if not in improvementinfos. -->
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



	# <!-- custom: addition based on our existing mod's code in some other class, as for pedia entries, imported from m-e mod (see main readme for mod abbreviation details in as of now credits section) (but i also found them later in c2c mod and they are seemingly the same but the file is sadly/unfortunately way too bloated so going for the m-e mod one(s if talking about the assets themselves if i am not mistaken in thinking/saying so)) -->
	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		textName = self.top.getNextWidgetName()
		screen.addMultilineText(textName, gc.getImprovementInfo(self.iImprovement).getCivilopedia(), self.X_HISTORY + 7, self.Y_HISTORY + 10 + self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER, self.W_HISTORY - 30, self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

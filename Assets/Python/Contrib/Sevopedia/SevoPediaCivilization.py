# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

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

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaCivilization:

	def __init__(self, main):
		self.iCivilization = -1
		self.top = main

		self.MEDIUM_MARGIN = 15

		self.X_MAIN_PANE = self.top.X_PEDIA_PAGE
		self.Y_MAIN_PANE = self.top.Y_PEDIA_PAGE

		self.Y_TECH = self.Y_MAIN_PANE
		self.H_TECH = 110

		self.Y_LEADER = self.Y_TECH + self.H_TECH + self.MEDIUM_MARGIN  - 5
		self.H_LEADER = self.H_TECH

		self.H_MAIN_PANE = self.Y_LEADER + self.H_LEADER - self.Y_MAIN_PANE
		self.W_MAIN_PANE = self.H_MAIN_PANE

		self.Y_TEXT = self.Y_MAIN_PANE + self.H_MAIN_PANE + self.MEDIUM_MARGIN
		self.H_TEXT = self.top.B_PEDIA_PAGE - self.Y_TEXT

		self.W_CITIES = 290
		self.H_CITIES = self.H_MAIN_PANE + self.MEDIUM_MARGIN + self.H_TEXT
		self.X_CITIES = self.top.R_PEDIA_PAGE - self.W_CITIES
		self.Y_CITIES = self.Y_MAIN_PANE

		self.X_TECH = self.X_MAIN_PANE + self.W_MAIN_PANE + self.MEDIUM_MARGIN
		self.W_TECH = (self.top.R_PEDIA_PAGE - self.X_TECH - self.W_CITIES - (2 * self.MEDIUM_MARGIN)) / 2

		self.X_LEADER = self.X_TECH
		self.W_LEADER = self.W_TECH

		self.W_ICON = 150
		self.H_ICON = 150
		self.X_ICON = self.X_MAIN_PANE + (self.H_MAIN_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_MAIN_PANE + (self.H_MAIN_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_BUILDING = self.X_TECH + self.W_TECH + self.MEDIUM_MARGIN
		self.Y_BUILDING = self.Y_TECH
		# <advc.004y> was 130
		self.W_BUILDING = self.W_TECH
		# This would split the space evenly between UU and UB
		#self.W_BUILDING = (self.top.R_PEDIA_PAGE - self.X_BUILDING - 10) // 2
		# </advc.004y>
		self.H_BUILDING = self.H_TECH

		self.X_UNIT = self.X_BUILDING
		self.Y_UNIT = self.Y_LEADER
		self.W_UNIT = self.W_TECH
		self.H_UNIT = self.H_TECH

		self.X_TEXT = self.X_MAIN_PANE
		self.W_TEXT = self.W_MAIN_PANE + self.MEDIUM_MARGIN + self.W_LEADER + self.MEDIUM_MARGIN + self.W_UNIT



	def interfaceScreen(self, iCivilization):
		self.iCivilization = iCivilization

		self.placeCivilizationPane()
		self.placeCities()
		self.placeTech()
		self.placeBuilding()
		self.placeUnit()
		self.placeLeader()
		self.placeText()



	def placeCivilizationPane(self):
		screen = self.top.getScreen()
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_MAIN_PANE, self.Y_MAIN_PANE, self.W_MAIN_PANE, self.H_MAIN_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: was PanelStyles.PANEL_STYLE_MAIN -->
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), ArtFileMgr.getCivilizationArtInfo(gc.getCivilizationInfo(self.iCivilization).getArtDefineTag()).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)



	# <!-- custom: part of the code here (placeCities in particular, but not exhaustive or maybe exhaustive or not, anyways, is imported from Middle-earth's mod's Platypedia C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\Middle-earth\Assets\Python\Screens\PlatyPedia\PlatyPediaCivilization.py thanks and then modified or not for AdvCiv-SAS -->
	def placeCities(self):
		screen = self.top.getScreen()
		screen.addPanel(self.top.getNextWidgetName(), localText.getText("TXT_KEY_CONCEPT_CITIES", ()), "", True, True, self.X_CITIES, self.Y_CITIES, self.W_CITIES, self.H_CITIES, PanelStyles.PANEL_STYLE_BLUE50 )
		Info = gc.getCivilizationInfo(self.iCivilization)
		szText = ""
		for i in xrange(Info.getNumCityNames()):
			if i == 0:
				szText += localText.getText("[ICON_STAR]", ())
			else:
				szText += "\n" + localText.getText("[ICON_BULLET]", ())
			szText += localText.getText(Info.getCityNames(i), ())
		screen.addMultilineText(self.top.getNextWidgetName(), szText, self.X_CITIES + 10, self.Y_CITIES + 30, self.W_CITIES, self.H_CITIES - 30, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeTech(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_FREE_TECHS", ()), "", False, True, self.X_TECH, self.Y_TECH, self.W_TECH, self.H_TECH, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for iTech in range(gc.getNumTechInfos()):
			if (gc.getCivilizationInfo(self.iCivilization).isCivilizationFreeTechs(iTech)):
				screen.attachImageButton(panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False)



	def placeBuilding(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_UNIQUE_BUILDINGS", ()), "", False, True, self.X_BUILDING, self.Y_BUILDING, self.W_BUILDING, self.H_BUILDING, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for iBuilding in range(gc.getNumBuildingClassInfos()):
			iUniqueBuilding = gc.getCivilizationInfo(self.iCivilization).getCivilizationBuildings(iBuilding)
			iDefaultBuilding = gc.getBuildingClassInfo(iBuilding).getDefaultBuildingIndex()
			# advc.003l: Allow uniques w/o a default unit. Based on a change by Toffer90 in Inthegrave's mod.
			if (#iDefaultBuilding > -1 and
				iUniqueBuilding > -1 and iDefaultBuilding != iUniqueBuilding):
				screen.attachImageButton(panelName, "", gc.getBuildingInfo(iUniqueBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iUniqueBuilding, 1, False)



	def placeUnit(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_FREE_UNITS", ()), "", False, True, self.X_UNIT, self.Y_UNIT, self.W_UNIT, self.H_UNIT, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for iUnit in range(gc.getNumUnitClassInfos()):
			iUniqueUnit = gc.getCivilizationInfo(self.iCivilization).getCivilizationUnits(iUnit)
			iDefaultUnit = gc.getUnitClassInfo(iUnit).getDefaultUnitIndex()
			if (#iDefaultUnit > -1 and # advc.003l: See comment in placeBuilding
			iUniqueUnit > -1 and iDefaultUnit != iUniqueUnit):
				screen.attachImageButton(panelName, "", gc.getUnitInfo(iUniqueUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUniqueUnit, 1, False)



	def placeLeader(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CONCEPT_LEADERS", ()), "", False, True, self.X_LEADER, self.Y_LEADER, self.W_LEADER, self.H_LEADER, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for iLeader in range(gc.getNumLeaderHeadInfos()):
			civ = gc.getCivilizationInfo(self.iCivilization)
			if civ.isLeaders(iLeader):
				screen.attachImageButton(panelName, "", gc.getLeaderHeadInfo(iLeader).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, self.iCivilization, False)



	def placeText(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, "", "", True, True, self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: also adding textName (see SevoPediaCivic.py for details) -->
		textName = self.top.getNextWidgetName()
		szText = gc.getCivilizationInfo(self.iCivilization).getCivilopedia()
		# <!-- custom: similar fix as in placeText of SevoPediCivic.py, choosing a more advanced function that also allows padding, and adding padding, about all these elements, see SevoPediaCivic.py for potentially additional information -->
		# screen.attachMultilineText(panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(textName, szText, self.X_TEXT + 7 , self.Y_TEXT + 10, self.W_TEXT - (15 * 2), self.H_TEXT - (15 * 2) - 25 + 29, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

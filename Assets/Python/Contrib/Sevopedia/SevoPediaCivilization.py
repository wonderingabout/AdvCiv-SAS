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

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



class SevoPediaCivilization:

	def __init__(self, main):
		self.iCivilization = -1
		self.top = main

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5
		self.playButtonPath = ArtFileMgr.getInterfaceArtInfo("SAS_EMOJI_PLAY_BUTTON").getPath()

		rowH = 110

		self.X_CIVILIZATION_PANE = self.top.X_PEDIA_PAGE
		self.Y_CIVILIZATION_PANE = self.top.Y_PEDIA_PAGE
		self.H_CIVILIZATION_PANE = (2 * rowH) + self.SMALL_MARGIN
		self.W_CIVILIZATION_PANE = self.H_CIVILIZATION_PANE

		self.W_CITIES = 290
		self.X_CITIES = self.top.R_PEDIA_PAGE - self.W_CITIES
		self.Y_CITIES = self.Y_CIVILIZATION_PANE
		self.H_CITIES = self.top.B_PEDIA_PAGE - self.Y_CITIES

		# <!-- custom: Music panel (84px, right of Civilization Pane) -->
		self.X_MUSIC = self.X_CIVILIZATION_PANE + self.W_CIVILIZATION_PANE + self.MEDIUM_MARGIN
		self.Y_MUSIC = self.Y_CIVILIZATION_PANE
		self.W_MUSIC = 84
		self.H_MUSIC = rowH

		halfRowW = (self.top.R_PEDIA_PAGE - self.X_MUSIC - self.W_CITIES - (2 * self.MEDIUM_MARGIN)) / 2

		self.X_TECH = self.X_MUSIC + self.W_MUSIC + self.MEDIUM_MARGIN
		self.Y_TECH = self.Y_CIVILIZATION_PANE
		self.W_TECH = halfRowW - self.W_MUSIC - self.MEDIUM_MARGIN
		self.H_TECH = rowH

		self.X_LEADER = self.X_MUSIC
		self.Y_LEADER = self.Y_MUSIC + rowH + self.SMALL_MARGIN
		self.W_LEADER = halfRowW
		self.H_LEADER = rowH

		self.W_ICON = 150
		self.H_ICON = 150
		iconCenter = (self.H_CIVILIZATION_PANE - self.H_ICON) / 2
		self.X_ICON = self.X_CIVILIZATION_PANE + iconCenter
		self.Y_ICON = self.Y_CIVILIZATION_PANE + iconCenter
		self.ICON_SIZE = 64

		self.X_BUILDING = self.X_TECH + self.W_TECH + self.MEDIUM_MARGIN
		self.Y_BUILDING = self.Y_TECH
		self.W_BUILDING = halfRowW
		self.H_BUILDING = rowH

		self.X_UNIT = self.X_LEADER + self.W_LEADER + self.MEDIUM_MARGIN
		self.Y_UNIT = self.Y_BUILDING + rowH + self.SMALL_MARGIN
		self.W_UNIT = halfRowW
		self.H_UNIT = rowH

		self.X_HISTORY = self.X_CIVILIZATION_PANE
		self.Y_HISTORY = self.Y_CIVILIZATION_PANE + self.H_CIVILIZATION_PANE + self.MEDIUM_MARGIN
		self.W_HISTORY = self.W_CIVILIZATION_PANE + self.MEDIUM_MARGIN + self.W_LEADER + self.MEDIUM_MARGIN + self.W_UNIT
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY



	def interfaceScreen(self, iCivilization):
		self.iCivilization = iCivilization

		self.placeCivilizationPane()
		self.placeCities()
		self.placeMusic()
		self.placeTech()
		self.placeBuilding()
		self.placeUnit()
		self.placeLeader()
		self.placeHistory()



	def placeCivilizationPane(self):
		screen = self.top.getScreen()
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_CIVILIZATION_PANE, self.Y_CIVILIZATION_PANE, self.W_CIVILIZATION_PANE, self.H_CIVILIZATION_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: was PanelStyles.PANEL_STYLE_MAIN -->
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), ArtFileMgr.getCivilizationArtInfo(gc.getCivilizationInfo(self.iCivilization).getArtDefineTag()).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)



	# <!-- custom: based on Middle-earth's mod's Platypedia Civilization -->
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



	def placeMusic(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SAS_MUSIC_PANEL", ()), "", False, True, self.X_MUSIC, self.Y_MUSIC, self.W_MUSIC, self.H_MUSIC, PanelStyles.PANEL_STYLE_BLUE50)

		# <!-- custom: use attachLabel for padding similar to other 84px panels -->
		screen.attachLabel(panelName, "", "  ")

		buttonSize = 64
		buttonX = (self.W_MUSIC - buttonSize) / 2
		buttonY = 10
		# <!-- custom: redirect to the first civ-specific sound entry in Sevopedia Music. (GPT-5.2-Codex (summarized)) -->
		iMusicKey = self.top.SAS_getFirstCivMusicKey(self.iCivilization)
		if iMusicKey != -1:
			screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, self.playButtonPath, buttonX, buttonY, buttonSize, buttonSize, WidgetTypes.WIDGET_PYTHON, self.top.SAS_PEDIA_PYTHON_MUSIC_ENTRY, iMusicKey)
		else:
			screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, self.playButtonPath, buttonX, buttonY, buttonSize, buttonSize, WidgetTypes.WIDGET_PEDIA_MAIN, SevoScreenEnums.PEDIA_MUSIC, -1)



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



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, "", "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: also adding textName (see SevoPediaCivic.py for details) -->
		textName = self.top.getNextWidgetName()
		szText = gc.getCivilizationInfo(self.iCivilization).getCivilopedia()
		# <!-- custom: similar fix as in placeHistory of SevoPediCivic.py, choosing a more advanced function that also allows padding, and adding padding, about all these elements, see SevoPediaCivic.py for potentially additional information -->
		# screen.attachMultilineText(panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(textName, szText, self.X_HISTORY + 7, self.Y_HISTORY + 10, self.W_HISTORY - (15 * 2), self.H_HISTORY - (15 * 2) - 25 + 29, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

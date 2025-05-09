# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
#
# <!-- custom: part of the code here (placeLeaders in particular, but not exhaustive or maybe exhaustive
# or not, anyways, is imported from History Rewritten mod:
# C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\History Rewritten\Assets\Python\Pedia\CvPediaReligion.py
# which may be modified or not for AdvCiv-SAS
# -->
#
# <!-- custom: part of the code here (placeBuilding and placeUnit in particular, but not exhaustive or maybe exhaustive
# or not, anyways, is imported from Rise of Mankind (291) mod:
# C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\Rise of Mankind\
# which may be modified or not for AdvCiv-SAS
# -->

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
import string

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaReligion:

	def __init__(self, main):
		self.iReligion = -1
		self.top = main

		self.MEDIUM_MARGIN = 15

		self.X_MAIN_PANE = self.top.X_PEDIA_PAGE
		self.Y_MAIN_PANE = self.top.Y_PEDIA_PAGE
		self.W_MAIN_PANE = 200

		self.X_REQUIRES = self.X_MAIN_PANE + self.W_MAIN_PANE + self.MEDIUM_MARGIN
		self.Y_REQUIRES = self.Y_MAIN_PANE
		self.W_REQUIRES = 84
		self.H_REQUIRES = 110

		self.X_BUILDING = self.X_REQUIRES + self.W_REQUIRES + self.MEDIUM_MARGIN
		self.Y_BUILDING = self.Y_REQUIRES
		self.W_BUILDING = (self.top.R_PEDIA_PAGE - self.X_BUILDING - self.MEDIUM_MARGIN) / 2
		self.H_BUILDING = self.H_REQUIRES

		self.X_UNIT = self.X_BUILDING + self.W_BUILDING + self.MEDIUM_MARGIN
		self.Y_UNIT = self.Y_BUILDING
		self.W_UNIT = self.top.R_PEDIA_PAGE - self.X_UNIT
		self.H_UNIT = 110

		self.X_SPECIAL = self.X_MAIN_PANE + self.W_MAIN_PANE + self.MEDIUM_MARGIN
		self.Y_SPECIAL = self.Y_REQUIRES + self.H_REQUIRES + self.MEDIUM_MARGIN - 5
		self.W_SPECIAL = self.top.R_PEDIA_PAGE - self.X_SPECIAL
		self.H_SPECIAL = 150

		self.H_MAIN_PANE = self.Y_SPECIAL + self.H_SPECIAL - self.Y_MAIN_PANE

		self.W_ICON = 150
		self.H_ICON = 150
		self.X_ICON = self.X_MAIN_PANE + (self.W_MAIN_PANE - self.W_ICON) / 2
		self.Y_ICON = self.Y_MAIN_PANE + (self.H_MAIN_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_LEADERS = self.X_MAIN_PANE
		self.W_LEADERS = self.top.R_PEDIA_PAGE - self.X_LEADERS
		self.H_LEADERS = 110
		self.Y_LEADERS = self.Y_MAIN_PANE + self.H_MAIN_PANE + self.MEDIUM_MARGIN - 5

		self.X_TEXT = self.X_MAIN_PANE
		self.Y_TEXT = self.Y_LEADERS + self.H_LEADERS + self.MEDIUM_MARGIN - 5
		self.W_TEXT = self.top.R_PEDIA_PAGE - self.X_TEXT
		self.H_TEXT = self.top.B_PEDIA_PAGE - self.Y_TEXT



	def interfaceScreen(self, iReligion):
		self.iReligion = iReligion
		screen = self.top.getScreen()

		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False, self.X_MAIN_PANE, self.Y_MAIN_PANE, self.W_MAIN_PANE, self.H_MAIN_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getReligionInfo(self.iReligion).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		self.placeSpecial()
		self.placeRequires()
		self.placeBuilding()
		self.placeUnit()
		self.placeLeaders()
		self.placeText()



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		iTech = gc.getReligionInfo(self.iReligion).getTechPrereq()
		if (iTech > -1):
			screen.attachImageButton( panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )


	# Rise of Mankind 2.9
	def placeBuilding(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_BUILDINGS_ROM_291", ()), "", False, True, self.X_BUILDING, self.Y_BUILDING, self.W_BUILDING, self.H_BUILDING, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for iBuilding in range(gc.getNumBuildingInfos()):
			# buildings have several options for religions so need to check them all, only one of them needs to be true
			iPrereq = gc.getBuildingInfo(iBuilding).getPrereqReligion()
			iPrereq2 = gc.getBuildingInfo(iBuilding).getReligionType()
			iPrereq3 = gc.getBuildingInfo(iBuilding).getStateReligion()
			iPrereq4 = gc.getBuildingInfo(iBuilding).getGlobalReligionCommerce()
			if (iPrereq == self.iReligion or iPrereq2 == self.iReligion or iPrereq3 == self.iReligion):
				screen.attachImageButton(panelName, "", gc.getBuildingInfo(iBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1, False)
#			elif (iPrereq == self.iReligion and iPrereq4 > 0):
#				screen.attachImageButton(panelName, "", gc.getBuildingInfo(iBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1, False)



	def placeUnit(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_UNITS_ROM_291", ()), "", False, True, self.X_UNIT, self.Y_UNIT, self.W_UNIT, self.H_UNIT, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for iUnit in range(gc.getNumUnitInfos()):
			iPrereq = gc.getUnitInfo(iUnit).getPrereqReligion()
			iPrereq2 = gc.getUnitInfo(iUnit).getReligionType()
			iPrereq3 = gc.getUnitInfo(iUnit).getStateReligion()
			if (iPrereq == self.iReligion or iPrereq2 == self.iReligion or iPrereq3 == self.iReligion):
				screen.attachImageButton(panelName, "", gc.getUnitInfo(iUnit).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
		screen.attachListBoxGFC( panelName, listName, "", TableStyles.TABLE_STYLE_EMPTY )
		screen.enableSelect(listName, False)
		szSpecialText = CyGameTextMgr().parseReligionInfo(self.iReligion, True)
		splitText = string.split( szSpecialText, "\n" )
		for special in splitText:
			if len( special ) != 0:
				screen.appendListBoxString( listName, special, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )



	def placeText(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, "", "", True, True, self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_BLUE50 )
		szText = gc.getReligionInfo(self.iReligion).getCivilopedia()
		screen.attachMultilineText( panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeLeaders(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()

		screen.addPanel(panel, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ()), "", False, True, self.X_LEADERS, self.Y_LEADERS, self.W_LEADERS, self.H_LEADERS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")

		for iLeader in xrange(gc.getNumLeaderHeadInfos()):
			LeaderInfo = gc.getLeaderHeadInfo(iLeader)
			if LeaderInfo.getFavoriteReligion() == self.iReligion:
				screen.attachImageButton(panel, "", LeaderInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, 1, False)



	def handleInput (self, inputClass):
		return 0

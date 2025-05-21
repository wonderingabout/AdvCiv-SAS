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
# <!-- custom: part of the code here (placeLeaders in particular, but not exhaustive or maybe exhaustive
# or not, anyways, is imported from History Rewritten mod:
# C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\History Rewritten\Assets\Python\Pedia\CvPediaReligion.py
# which may be modified or not for AdvCiv-SAS, by claude AI and then my adjustments or not to it or not or yes or and other or and not anwyays etc
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

		# <!-- custom: based on sevopediabuilding's code, see there for details and differences of implementation --> 

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		# <!-- custom: this (287 anyways etc) should be accurate according to my measurements if i am not mistaken for a 4 leaders panel but the screen.appendMultiListButton uses seemingly (approximately from my vision but anyways etc) a smaller button spacing, so we have now due to saved reduced spacing a bit extra space on the right margin as compared to left margin, making it asymetrical and less pretty if i may say anyways etc, to solve this, reducing the width, while keeping in mind the correct value should be 287 if i am not mistaken for 4 leaders per row total width including margins (or keeping here as i may or in case i forget or not forget maybe or not or yes or and other or and not anyways etc) -->
		#self.W_LEADERS = 287
		self.W_LEADERS = 282
		self.X_LEADERS = self.top.R_PEDIA_PAGE - self.W_LEADERS
		self.Y_LEADERS = self.top.Y_PEDIA_PAGE
		self.H_LEADERS = self.top.B_PEDIA_PAGE - self.Y_LEADERS

		self.X_RELIGION_PANE = self.top.X_PEDIA_PAGE
		self.Y_RELIGION_PANE = self.top.Y_PEDIA_PAGE
		self.W_RELIGION_PANE = 200
		self.H_RELIGION_PANE = 230

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
		# <!-- custom: icon at the center of the panel for its middle point (both middle point of the icon/button and of the religion_panel should and are wanted for us to coincide here anyways etc if we/i are/am not mistaken anyways etc anyways etc anyways etc...)
		# Note: formula is approximative but seems to work quite well for a button size of 64px, may be improved indeed or not or yes or not or and other or and not or etc or not etc or yes or and other or and not anyways etc -->
		self.X_ICON = self.X_RELIGION_PANE + (self.ICON_FRAME_SIZE - self.ICON_SIZE) / 2 + 19
		self.Y_ICON = self.Y_RELIGION_PANE + (self.H_RELIGION_PANE - self.H_ICON) / 2 + 3

		self.W_REMAINING_CENTER_SPACE = self.top.R_PEDIA_PAGE - (self.W_LEADERS + self.MEDIUM_MARGIN) - self.MEDIUM_MARGIN - (self.X_RELIGION_PANE + self.W_RELIGION_PANE + self.MEDIUM_MARGIN)

		self.X_BUILDINGS = self.X_RELIGION_PANE + self.W_RELIGION_PANE + self.MEDIUM_MARGIN
		self.Y_BUILDINGS = self.Y_RELIGION_PANE
		self.W_BUILDINGS = self.W_REMAINING_CENTER_SPACE / 2
		self.H_BUILDINGS = 110

		self.W_REQUIRES = 84

		self.X_UNITS = self.X_BUILDINGS
		self.Y_UNITS = self.Y_BUILDINGS + self.H_BUILDINGS + self.SMALL_MARGIN
		self.W_UNITS = self.W_BUILDINGS - self.W_REQUIRES - self.MEDIUM_MARGIN
		self.H_UNITS = self.H_BUILDINGS

		self.X_REQUIRES = self.X_UNITS + self.W_UNITS + self.MEDIUM_MARGIN
		self.Y_REQUIRES = self.Y_UNITS
		self.H_REQUIRES = self.H_BUILDINGS

		self.X_SPECIAL = self.X_BUILDINGS + self.W_BUILDINGS + self.MEDIUM_MARGIN
		self.Y_SPECIAL = self.Y_BUILDINGS
		self.W_SPECIAL = self.top.R_PEDIA_PAGE - self.X_SPECIAL - self.W_LEADERS - self.MEDIUM_MARGIN
		self.H_SPECIAL = self.H_BUILDINGS + self.SMALL_MARGIN + self.H_UNITS

		self.X_HISTORY = self.X_RELIGION_PANE
		self.Y_HISTORY = self.Y_UNITS + self.H_UNITS + self.SMALL_MARGIN
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.X_HISTORY - self.W_LEADERS - self.MEDIUM_MARGIN
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY



	def interfaceScreen(self, iReligion):
		self.iReligion = iReligion

		self.placeReligionPane()
		self.placeSpecial()
		self.placeRequires()
		self.placeBuilding()
		self.placeUnit()
		self.placeLeaders()
		self.placeHistory()



	def placeReligionPane(self):
		screen = self.top.getScreen()

		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False, self.X_RELIGION_PANE, self.Y_RELIGION_PANE, self.W_RELIGION_PANE, self.H_RELIGION_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: no need for the blue frame on blue background, use transparent instead, anyways etc -->
		#screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getReligionInfo(self.iReligion).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )



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
		screen.addPanel(panelName, localText.getText("TXT_KEY_BUILDINGS_ROM_291", ()), "", False, True, self.X_BUILDINGS, self.Y_BUILDINGS, self.W_BUILDINGS, self.H_BUILDINGS, PanelStyles.PANEL_STYLE_BLUE50)
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
		screen.addPanel(panelName, localText.getText("TXT_KEY_UNITS_ROM_291", ()), "", False, True, self.X_UNITS, self.Y_UNITS, self.W_UNITS, self.H_UNITS, PanelStyles.PANEL_STYLE_BLUE50)
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



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, "", "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50 )
		szText = gc.getReligionInfo(self.iReligion).getCivilopedia()
		screen.attachMultilineText( panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: in https://civ4bug.sourceforge.net/PythonAPI/AllClasses.html i have found this:
	# VOID addMultiListControlGFC (STRING szName, STRING helpText, INT iX, INT iY, INT iWidth, INT iHeight, INT numLists, INT defaultWidth, INT defaultHeight, TableStyle eStyle)
	# and in https://github.com/f1rpo/AdvCiv/blob/master/Assets/Python/Screens/CvMainInterface.py#L2050C1-L2053C38 i have found this:
	# 		self.screen.addMultiListControlGFC("BottomButtonList", u"",
	#			lRect.x(), lRect.y(), lRect.width(), lRect.height(),
	#			4, iButtonSize, iButtonSize, # numLists, defaultWidth, defaultHeight
	#			TableStyles.TABLE_STYLE_STANDARD)
	# if it helps us adapt/use the addMultiListControlGFC method, anyways etc
	# -->
	def placeLeaders(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()

		# Create panel with proper styling
		screen.addPanel(panelName, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ()), "", False, True, 
						self.X_LEADERS, self.Y_LEADERS, self.W_LEADERS, self.H_LEADERS, 
						PanelStyles.PANEL_STYLE_BLUE50)
		
		# Create MultiList for leaders
		rowListName = self.top.getNextWidgetName()
		
		# Constants for leader button display
		BUTTON_SIZE = 64 # Size of each leader button
		PADDING_X = 9
		PADDING_Y = 36
		
		# Create the MultiList control
		# Per documentation, the numLists parameter (7th) is actually number of columns
		# Setting to 1 means the engine will auto-calculate how many buttons fit per row
		screen.addMultiListControlGFC(rowListName, "", 
								self.X_LEADERS + PADDING_X, 
								self.Y_LEADERS + PADDING_Y, 
								self.W_LEADERS - (PADDING_X * 2), 
								self.H_LEADERS - (PADDING_Y + 10), 
								1,  # Using 1 for auto-calculation of buttons per row
								BUTTON_SIZE, BUTTON_SIZE, 
								TableStyles.TABLE_STYLE_STANDARD)

	    # Find all leaders who have this religion as favorite, <!-- custom: and --> add <!-- custom: them --> all to the list <!-- custom: anyways etc (not catch them all... or maybe.. or not or yes, anyways etc... xd anyways etc...) -->
		for iLeader in xrange(gc.getNumLeaderHeadInfos()):
			LeaderInfo = gc.getLeaderHeadInfo(iLeader)
			if LeaderInfo.getFavoriteReligion() == self.iReligion:
				LeaderInfo = gc.getLeaderHeadInfo(iLeader)
				screen.appendMultiListButton(rowListName, LeaderInfo.getButton(), 
										0,  # Column index (always 0 when numLists=1)
										WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, 1, False)



	def handleInput (self, inputClass):
		return 0

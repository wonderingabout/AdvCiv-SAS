# ccgs
from CvPythonExtensions import *
import GenericDecoratedScreen
import CvUtil
import ScreenInput
import CvScreenEnums


gc = CyGlobalContext()
#ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

# If we also want to replace the Custom Scenario screen (and maybe Hotseat and Staging Room), then I think this should be turned into an abstract class with derived classes for each of the specific game setup screens.
class CustomGameScreen(GenericDecoratedScreen.GenericDecoratedScreen):

	def __init__(self):
		GenericDecoratedScreen.GenericDecoratedScreen.__init__(self)
		self.iScreenID = CvScreenEnums.CUSTOM_GAME_SCREEN


	def getScreen(self): # override
		return CyGInterfaceScreen("CustomGameScreen", self.iScreenID)


	def interfaceScreen(self):
		screen = self.getScreen()
		self.initDimensions()
		self.addBackgroundHeaderFooter(localText.getText("TXT_KEY_CUSTOM_GAME_TITLE", ()))

		self.MAIN_PANEL_ID = "MainPanel"
		mainPanelMargin = 10
		mainPanelWidth = self.wScreen - 2 * mainPanelMargin
		mainPanelHeight = self.hScreen - 2 * mainPanelMargin - self.hHeader - self.hFooter
		screen.addPanel(self.MAIN_PANEL_ID, "", "", True, True,
				mainPanelMargin, mainPanelMargin + self.hFooter, mainPanelWidth, mainPanelHeight,
				PanelStyles.PANEL_STYLE_MAIN)

		centerX = mainPanelWidth / 2
		centerY = mainPanelHeight / 2

		# Grid layout for dropdowns - 2 columns, 3 rows
		dropdownWidth = 200
		labelWidth = 100
		rowHeight = 40
		columnSpacing = 350  # Space between columns
		col1X = centerX - 330  # Left column
		col2X = col1X + columnSpacing  # Right column
		startY = centerY - 60  # Start position

		# Row 0 - Left: World Size, Right: Climate
		self.WORLDSIZE_DROPDOWN_ID = "WorldSizeDropDown"
		x = col1X
		y = startY + 0 * rowHeight
		screen.setLabel("WorldSizeLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MAP_WORLD_SIZE", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.WORLDSIZE_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in reversed(range(gc.getNumWorldInfos())):
			screen.addPullDownString(self.WORLDSIZE_DROPDOWN_ID, gc.getWorldInfo(i).getDescription(), i, i, i == gc.getInitCore().getWorldSize())

		self.CLIMATE_DROPDOWN_ID = "ClimateDropDown"
		x = col2X
		screen.setLabel("ClimateLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MAP_CLIMATE", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.CLIMATE_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in reversed(range(gc.getNumClimateInfos())):
			screen.addPullDownString(self.CLIMATE_DROPDOWN_ID, gc.getClimateInfo(i).getDescription(), i, i, i == gc.getInitCore().getClimate())

		# Row 1 - Left: Sea Level, Right: Era
		self.SEALEVEL_DROPDOWN_ID = "SeaLevelDropDown"
		x = col1X
		y = startY + 1 * rowHeight
		screen.setLabel("SeaLevelLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MAP_SEA_LEVEL", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.SEALEVEL_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in reversed(range(gc.getNumSeaLevelInfos())):
			screen.addPullDownString(self.SEALEVEL_DROPDOWN_ID, gc.getSeaLevelInfo(i).getDescription(), i, i, i == gc.getInitCore().getSeaLevel())

		self.ERA_DROPDOWN_ID = "EraDropDown"
		x = col2X
		screen.setLabel("EraLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MENU_ERA", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.ERA_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in reversed(range(gc.getNumEraInfos())):
			screen.addPullDownString(self.ERA_DROPDOWN_ID, gc.getEraInfo(i).getDescription(), i, i, i == gc.getInitCore().getEra())

		# Row 2 - Game Speed (left column, matching grid style)
		self.GAMESPEED_DROPDOWN_ID = "GameSpeedDropDown"
		x = col1X
		y = startY + 2 * rowHeight
		screen.setLabel("GameSpeedLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MENU_SPEED", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.GAMESPEED_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_HELP_GAME_SPEED, GameSpeedTypes.NO_GAMESPEED, 1, FontTypes.GAME_FONT)
		screen.setToolTipAlignment(self.GAMESPEED_DROPDOWN_ID, ToolTipAlignTypes.TOOLTIP_BOTTOM_RIGHT)
		for i in reversed(range(gc.getNumGameSpeedInfos())):
			screen.addPullDownString(self.GAMESPEED_DROPDOWN_ID, gc.getGameSpeedInfo(i).getDescription(), i, i, i == gc.getInitCore().getGameSpeed())

		screen.setText(self.EXIT_ID, self.BACKGR,
				u"<font=4>" + localText.getText("TXT_KEY_MAIN_MENU_LAUNCH", ()).upper() + "</font>",
				CvUtil.FONT_RIGHT_JUSTIFY, self.xExitButton, self.yExitButton, 0,
				FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN,
				self.iScreenID, 0) # 0 for Launch through Return key
		# This should be the right style (defined in Civ4Theme_Custom.thm), but it really isn't? The original screen (and opening menu) seem to use the arrow_ani_l_...tga arrows, but I don't see any style that uses those.
		#screen.setStyle(self.EXIT_ID, "SF_CtrlTheme_Civ4_Control_Button_Main_ArrowR_Style")
		screen.setActivation(self.EXIT_ID, ActivationTypes.ACTIVATE_NORMAL)
		self.GOBACK_ID = "GoBackButton"
		xGoBackButton = 130
		screen.setText(self.GOBACK_ID, self.BACKGR,
				u"<font=4>" + localText.getText("TXT_KEY_MAIN_MENU_GO_BACK", ()).upper() + "</font>",
				CvUtil.FONT_RIGHT_JUSTIFY, xGoBackButton, self.yExitButton, 0,
				FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN,
				# 2 for Go Back through simulated mouse-click.
				# (1 would do it through TAB+Return key; can't get this to work reliably.)
				self.iScreenID, 2)
		#screen.setStyle(self.GOBACK_ID, "SF_CtrlTheme_Civ4_Control_Button_Main_ArrowL_Style")
		screen.setActivation(self.GOBACK_ID, ActivationTypes.ACTIVATE_NORMAL)
		footerButtonDist = 300 # Distance in between footer buttons that are grouped together
		CLOSE_ID = "CloseButton"
		screen.setText(CLOSE_ID, self.BACKGR,
				u"<font=4>" + localText.getText("TXT_KEY_CUCUGS_CLOSE", ()).upper() + "</font>",
				CvUtil.FONT_RIGHT_JUSTIFY, xGoBackButton + footerButtonDist, self.yExitButton, 0,
				FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN,
				-1, -1) # Regular close-screen widget; no simulated key presses.
		screen.setActivation(CLOSE_ID, ActivationTypes.ACTIVATE_NORMAL)

		# This doesn't seem to affect anything
		#screen.setCloseOnEscape(False)
		# Without this, calls to interfaceScreen don't bring the screen back after ESC.
		screen.setPersistent(True)
		# This leads to a crash. I'm trying to prevent players from TAB-selecting widgets
		# on the original screen in the background ... open issue.
		#screen.setMainInterface(True)
		# Should we use bPassInput=True? The Advisor screens use False, the main screen True.
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)


	def update(self, fDelta): # called after handleInput
		pass


	def handleInput(self, inputClass):
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED:
			screen = self.getScreen()
			funcName = inputClass.getFunctionName()

			if funcName == self.GAMESPEED_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.GAMESPEED_DROPDOWN_ID)
				iGameSpeed = screen.getPullDownData(self.GAMESPEED_DROPDOWN_ID, iIndex)
				gc.getInitCore().setGameSpeed(iGameSpeed)

			elif funcName == self.WORLDSIZE_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.WORLDSIZE_DROPDOWN_ID)
				iWorldSize = screen.getPullDownData(self.WORLDSIZE_DROPDOWN_ID, iIndex)
				gc.getInitCore().setWorldSize(iWorldSize)

			elif funcName == self.CLIMATE_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.CLIMATE_DROPDOWN_ID)
				iClimate = screen.getPullDownData(self.CLIMATE_DROPDOWN_ID, iIndex)
				gc.getInitCore().setClimate(iClimate)

			elif funcName == self.SEALEVEL_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.SEALEVEL_DROPDOWN_ID)
				iSeaLevel = screen.getPullDownData(self.SEALEVEL_DROPDOWN_ID, iIndex)
				gc.getInitCore().setSeaLevel(iSeaLevel)

			elif funcName == self.ERA_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.ERA_DROPDOWN_ID)
				iEra = screen.getPullDownData(self.ERA_DROPDOWN_ID, iIndex)
				gc.getInitCore().setEra(iEra)

		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
			if inputClass.getButtonType() == WidgetTypes.WIDGET_CLOSE_SCREEN:
				# In the unlikely case that the player has TAB'ed onto the original Custom Game screen. We want the new screen to have focus when it closes so that the original Launch button receives focus (by default, apparently). This doesn't work reliably, but it's better than failing everytime.
				self.getScreen().setFocus(self.MAIN_PANEL_ID)
		return 1 # Consume all inputs

	#def onClose(self):
	# Could perhaps also handle the emulated key presses here. Would have to remember in which way the screen was closed, and the InputSim functions would have to be exposed to Python for specific keys. (Because figuring out the Windows key codes in Python would require some contortions I think. We might then as well try to trigger the key presses directly from Python via the ctypes module.)

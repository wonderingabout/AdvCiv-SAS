## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import CvScreensInterface
from SASFontUtils import *
from SASUtils import *

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvPolicyScreen:
	"Policy Screen"

	def __init__(self):
		self.SCREEN_NAME = "PolicyScreen"
		self.CANCEL_NAME = "PolicyCancel"
		self.EXIT_NAME = "PolicyExit"
		self.TITLE_NAME = "PolicyTitleHeader"
		self.BUTTON_NAME = "PolicyScreenButton"
		self.TEXT_NAME = "PolicyScreenText"
		self.AREA_NAME = "PolicyScreenArea"
		self.HELP_AREA_NAME = "PolicyScreenHelpArea"
		self.HELP_IMAGE_NAME = "PolicyScreenCivicOptionImage"
		self.DEBUG_DROPDOWN_ID =  "PolicyDropdownWidget"
		self.BACKGROUND_ID = "PolicyBackground"
		self.HELP_HEADER_NAME = "PolicyScreenHeaderName"

		# <!-- custom: keep screen-independent advisor edge constants in init; compute runtime resolution-dependent bounds in interfaceScreen via shared SASUtils helpers. (GPT-5.3-Codex) -->
		self.W_LEFT_SPACE_FOR_COMMERCE_SLIDERS = SAS_ADVISOR_LEFT_SPACE_FOR_COMMERCE_SLIDERS
		self.W_RIGHT_SPACE_FOR_SCOREBOARD = SAS_ADVISOR_RIGHT_SPACE_FOR_SCOREBOARD
		self.H_TOP_SPACE_FOR_TECH_BAR = SAS_ADVISOR_TOP_SPACE_FOR_TECH_BAR
		self.H_BOTTOM_SPACE = SAS_ADVISOR_BOTTOM_SPACE

		self.HEADINGS_TOP = 70
		self.HEADINGS_SPACING = 5
		self.HEADINGS_BOTTOM = 280
		self.HELP_TOP = 350
		self.HELP_BOTTOM = 610
		self.TEXT_MARGIN = 15
		self.BUTTON_SIZE = 24
		self.BIG_BUTTON_SIZE = 64
		self.BOTTOM_LINE_TOP = 630
		self.BOTTOM_LINE_HEIGHT = 60

		self.Y_EXIT = 726
		self.Y_CANCEL = 726

		self.Y_SCREEN = 396
		self.Z_SCREEN = -6.1
		self.Y_TITLE = SAS_ADVISOR_TITLE_Y
		self.Z_TEXT = self.Z_SCREEN - 0.2

		self.PolicyScreenInputMap = {
			self.BUTTON_NAME		: self.PolicyButton,
			self.TEXT_NAME			: self.PolicyButton,
			self.EXIT_NAME			: self.Revolution,
			self.CANCEL_NAME		: self.Cancel,
			}

		self.iActivePlayer = -1
		self.iLanguageLoaded = -1

		self.m_paeCurrentPolicies = []
		self.m_paeDisplayPolicies = []
		self.m_paeOriginalPolicies = []

	def initText(self):
		# <!-- custom: cache Policy Advisor static UI text once per language to reduce repeated translator work and keep future multi-tab expansion centralized. Dynamic gameplay-state text remains computed at draw/update time. (GPT-5.3-Codex) -->
		if self.iLanguageLoaded == CyGame().getCurrentLanguage() or not CyGame().isFinalInitialized():
			return
		self.iLanguageLoaded = CyGame().getCurrentLanguage()

		self.TEXT_CANCEL = SAS_FONT_TAG_TITLE + localText.getText("TXT_KEY_SCREEN_CANCEL", ()).upper() + SAS_FONT_TAG_CLOSE
		self.TEXT_TITLE = SAS_FONT_TAG_TITLE_BOLD + localText.getText("TXT_KEY_CIVICS_SCREEN_TITLE", ()).upper() + SAS_FONT_TAG_CLOSE
		self.TEXT_EXIT = SAS_FONT_TAG_TITLE + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + SAS_FONT_TAG_CLOSE
		self.TEXT_REVOLUTION = SAS_FONT_TAG_TITLE + localText.getText("TXT_KEY_CONCEPT_REVOLUTION", ()).upper() + SAS_FONT_TAG_CLOSE
		self.TEXT_NO_UPKEEP = localText.getText("TXT_KEY_CIVICS_SCREEN_NO_UPKEEP", ())

	def updateRuntimeLayout(self, screen):
		self.L_SCREEN, self.T_SCREEN, self.W_SCREEN, self.H_SCREEN = getAdvisorRuntimeBounds(
			screen,
			self.W_LEFT_SPACE_FOR_COMMERCE_SLIDERS,
			self.W_RIGHT_SPACE_FOR_SCOREBOARD,
			self.H_TOP_SPACE_FOR_TECH_BAR,
			self.H_BOTTOM_SPACE
		)
		self.X_TITLE, self.X_EXIT, self.Y_EXIT, self.Y_LINK, self.Y_BOTTOM_PANEL = getAdvisorRuntimeAnchors(self.W_SCREEN, self.H_SCREEN)
		self.X_CANCEL = self.W_SCREEN / 2
		self.X_SCREEN = self.W_SCREEN / 2
		self.Y_CANCEL = self.Y_EXIT
		self.BOTTOM_LINE_WIDTH = self.W_SCREEN - 10
		self.BOTTOM_LINE_TOP = self.Y_BOTTOM_PANEL - self.BOTTOM_LINE_HEIGHT - 23
		self.HELP_BOTTOM = self.BOTTOM_LINE_TOP - 20
		self.HEADINGS_WIDTH = (self.W_SCREEN - self.HEADINGS_SPACING) / gc.getNumCivicOptionInfos() - self.HEADINGS_SPACING

	def getScreen(self):
		return CyGInterfaceScreen(self.SCREEN_NAME, CvScreenEnums.CIVICS_SCREEN)

	def setActivePlayer(self, iPlayer):

		self.iActivePlayer = iPlayer
		activePlayer = gc.getPlayer(iPlayer)

		self.m_paeCurrentPolicies = []
		self.m_paeDisplayPolicies = []
		self.m_paeOriginalPolicies = []
		for i in range (gc.getNumCivicOptionInfos()):
			self.m_paeCurrentPolicies.append(activePlayer.getCivics(i))
			self.m_paeDisplayPolicies.append(activePlayer.getCivics(i))
			self.m_paeOriginalPolicies.append(activePlayer.getCivics(i))

	def interfaceScreen (self):

		screen = self.getScreen()
		if screen.isActive():
			return
		self.initText()
		screen.setRenderInterfaceOnly(True)
		screen.showScreen( PopupStates.POPUPSTATE_IMMEDIATE, False)

		# <!-- custom: remove dependency on EndTurnButton geometry (old gRect-based margin). We now use shared advisor runtime bounds/anchors so policy layout follows the same resolution logic as other advisors and avoids coupling to HUD widget positions. (GPT-5.3-Codex) -->
		self.updateRuntimeLayout(screen)
	
		# Set the background and exit button, and show the screen
		screen.setDimensions(self.L_SCREEN, self.T_SCREEN, self.W_SCREEN, self.H_SCREEN)
		# advc.002b (note): The background image has 2:1 dimensions, so the increased W_SCREEN value makes it less distorted than in BtS. (Except maybe on very high resolutions.)
		screen.addDDSGFC(self.BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo("MAINMENU_SLIDESHOW_LOAD").getPath(), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addPanel( "PolicyTopPanel", u"", u"", True, False, 0, 0, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_TOPBAR )
		screen.addPanel( "PolicyBottomPanel", u"", u"", True, False, 0, self.Y_BOTTOM_PANEL, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR )
		screen.showWindowBackground(False)
		screen.setText(self.CANCEL_NAME, "Background", self.TEXT_CANCEL, CvUtil.FONT_CENTER_JUSTIFY, self.X_CANCEL, self.Y_CANCEL, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, 1, 0)

		# Header...
		screen.setText(self.TITLE_NAME, "Background", self.TEXT_TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.X_SCREEN, self.Y_TITLE, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		self.setActivePlayer(gc.getGame().getActivePlayer())						

		if (CyGame().isDebugMode()):
			self.szDropdownName = self.DEBUG_DROPDOWN_ID
			screen.addDropDownBoxGFC(self.szDropdownName, 22, 12, 300, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
			for j in range(gc.getMAX_PLAYERS()):
				if (gc.getPlayer(j).isAlive()):
					screen.addPullDownString(self.szDropdownName, gc.getPlayer(j).getName(), j, j, False )

		screen.addPanel("PolicyBottomLine", "", "", True, True, self.HEADINGS_SPACING, self.BOTTOM_LINE_TOP, self.BOTTOM_LINE_WIDTH, self.BOTTOM_LINE_HEIGHT, PanelStyles.PANEL_STYLE_MAIN)

		# Draw Contents
		self.drawContents()

		return 0

	# Draw the contents...
	def drawContents(self):
	
		# Draw the radio buttons
		self.drawAllButtons()
				
		# Draw Help Text
		self.drawAllHelpText()
		
		# Update Maintenance/anarchy/etc.
		self.updateAnarchy()

	def drawCivicOptionButtons(self, iCivicOption):

		activePlayer = gc.getPlayer(self.iActivePlayer)
		screen = self.getScreen()
		
		for j in range(gc.getNumCivicInfos()):

			if (gc.getCivicInfo(j).getCivicOptionType() == iCivicOption):										
				screen.setState(self.getPolicyButtonName(j), self.m_paeCurrentPolicies[iCivicOption] == j)
							
				if (self.m_paeDisplayPolicies[iCivicOption] == j):
					#screen.setState(self.getPolicyButtonName(j), True)
					screen.show(self.getPolicyButtonName(j))
				elif (activePlayer.canDoCivics(j)):
					#screen.setState(self.getPolicyButtonName(j), False)
					screen.show(self.getPolicyButtonName(j))
				else:
					screen.hide(self.getPolicyButtonName(j))
								
	# Will draw the radio buttons (and revolution)
	def drawAllButtons(self):				

		for i in range(gc.getNumCivicOptionInfos()):
		
			fX = self.HEADINGS_SPACING + (self.HEADINGS_WIDTH + self.HEADINGS_SPACING) * i
			fY = self.HEADINGS_TOP
			
			szAreaID = self.AREA_NAME + str(i)
			screen = self.getScreen()
			screen.addPanel(szAreaID, "", "", True, True,
					fX, fY, self.HEADINGS_WIDTH, self.HEADINGS_BOTTOM - self.HEADINGS_TOP,
					PanelStyles.PANEL_STYLE_MAIN)

			screen.setLabel("", "Background",
					SAS_FONT_TAG_LABEL + gc.getCivicOptionInfo(i).getDescription().upper() + SAS_FONT_TAG_CLOSE,
					CvUtil.FONT_CENTER_JUSTIFY,
					fX + self.HEADINGS_WIDTH / 2, self.HEADINGS_TOP + self.TEXT_MARGIN, 0,
					FontTypes.GAME_FONT,
					WidgetTypes.WIDGET_GENERAL, -1, -1 )

			fY += self.TEXT_MARGIN
			
			for j in range(gc.getNumCivicInfos()):
				if (gc.getCivicInfo(j).getCivicOptionType() == i):										
					fY += 2 * self.TEXT_MARGIN

					screen.addCheckBoxGFC(self.getPolicyButtonName(j), gc.getCivicInfo(j).getButton(), ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), fX + self.BUTTON_SIZE/2, fY, self.BUTTON_SIZE, self.BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL)

					screen.setText(self.getPolicyTextName(j), "", SAS_FONT_TAG_LABEL + gc.getCivicInfo(j).getDescription() + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, fX + self.BUTTON_SIZE + self.TEXT_MARGIN, fY, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

			self.drawCivicOptionButtons(i)
							
	def highlight(self, iCivic):
		iCivicOption = gc.getCivicInfo(iCivic).getCivicOptionType()
		if self.m_paeDisplayPolicies[iCivicOption] != iCivic:
			self.m_paeDisplayPolicies[iCivicOption] = iCivic
			self.drawCivicOptionButtons(iCivicOption)
			return True
		return False
		
	def unHighlight(self, iCivic):		
		iCivicOption = gc.getCivicInfo(iCivic).getCivicOptionType()
		if self.m_paeDisplayPolicies[iCivicOption] != self.m_paeCurrentPolicies[iCivicOption]:
			self.m_paeDisplayPolicies[iCivicOption] = self.m_paeCurrentPolicies[iCivicOption]
			self.drawCivicOptionButtons(iCivicOption)
			return True
		return False
		
	def select(self, iCivic):
		activePlayer = gc.getPlayer(self.iActivePlayer)
		if (not activePlayer.canDoCivics(iCivic)):
			# If you can't even do this, get out....
			return 0
			
		iCivicOption = gc.getCivicInfo(iCivic).getCivicOptionType()
		
		# Set the previous widget
		iCivicPrev = self.m_paeCurrentPolicies[iCivicOption]
		
		# Switch the widgets
		self.m_paeCurrentPolicies[iCivicOption] = iCivic
		
		# Unighlight the previous widget
		self.unHighlight(iCivicPrev)
		self.getScreen().setState(self.getPolicyButtonName(iCivicPrev), False)

		# highlight the new widget
		self.highlight(iCivic)		
		self.getScreen().setState(self.getPolicyButtonName(iCivic), True)
		
		return 0

	def PolicyButton(self, inputClass):
	
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED) :
			if (inputClass.getFlags() & MouseFlags.MOUSE_RBUTTONUP):
				CvScreensInterface.pediaJumpToCivic((inputClass.getID(), ))
			else:
				# Select button
				self.select(inputClass.getID())
				self.drawHelpText(gc.getCivicInfo(inputClass.getID()).getCivicOptionType())
				self.updateAnarchy()
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_ON) :
			# Highlight this button
			if self.highlight(inputClass.getID()):
				self.drawHelpText(gc.getCivicInfo(inputClass.getID()).getCivicOptionType())
				self.updateAnarchy()
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_OFF) :
			if self.unHighlight(inputClass.getID()):
				self.drawHelpText(gc.getCivicInfo(inputClass.getID()).getCivicOptionType())
				self.updateAnarchy()

		return 0

		
	def drawHelpText(self, iCivicOption):
		
		activePlayer = gc.getPlayer(self.iActivePlayer)
		iCivic = self.m_paeDisplayPolicies[iCivicOption]

		szPaneID = "PolicyHelpTextBackground" + str(iCivicOption)
		screen = self.getScreen()

		szHelpText = u""

		# Upkeep string
		if ((gc.getCivicInfo(iCivic).getUpkeep() != -1) and not activePlayer.isNoCivicUpkeep(iCivicOption)):
			szHelpText = gc.getUpkeepInfo(gc.getCivicInfo(iCivic).getUpkeep()).getDescription()
		else:
			szHelpText = self.TEXT_NO_UPKEEP

		szHelpText += CyGameTextMgr().parseCivicInfo(iCivic, False, True, True)

		fX = self.HEADINGS_SPACING  + (self.HEADINGS_WIDTH + self.HEADINGS_SPACING) * iCivicOption

		screen.setLabel(self.HELP_HEADER_NAME + str(iCivicOption), "Background",  SAS_FONT_TAG_LABEL + gc.getCivicInfo(self.m_paeDisplayPolicies[iCivicOption]).getDescription().upper() + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, fX + self.HEADINGS_WIDTH/2, self.HELP_TOP + self.TEXT_MARGIN, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		fY = self.HELP_TOP - self.BIG_BUTTON_SIZE
		szHelpImageID = self.HELP_IMAGE_NAME + str(iCivicOption)		
		screen.setImageButton(szHelpImageID, gc.getCivicInfo(iCivic).getButton(), fX + self.HEADINGS_WIDTH/2 - self.BIG_BUTTON_SIZE/2, fY, self.BIG_BUTTON_SIZE, self.BIG_BUTTON_SIZE, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, iCivic, 1)

		fY = self.HELP_TOP + 3 * self.TEXT_MARGIN
		szHelpAreaID = self.HELP_AREA_NAME + str(iCivicOption)		
		screen.addMultilineText(szHelpAreaID, SAS_FONT_TAG_LABEL + szHelpText + SAS_FONT_TAG_CLOSE, fX+5, fY, self.HEADINGS_WIDTH-7, self.HELP_BOTTOM - fY-2, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		
		
	# Will draw the help text
	def drawAllHelpText(self):
		for i in range (gc.getNumCivicOptionInfos()):		

			fX = self.HEADINGS_SPACING  + (self.HEADINGS_WIDTH + self.HEADINGS_SPACING) * i

			szPaneID = "PolicyHelpTextBackground" + str(i)
			screen = self.getScreen()
			screen.addPanel(szPaneID, "", "", True, True, fX, self.HELP_TOP, self.HEADINGS_WIDTH, self.HELP_BOTTOM - self.HELP_TOP, PanelStyles.PANEL_STYLE_MAIN)

			self.drawHelpText(i)


	# Will Update the maintenance/anarchy/etc
	def updateAnarchy(self):

		screen = self.getScreen()
		self.initText()

		activePlayer = gc.getPlayer(self.iActivePlayer)

		bChange = False
		i = 0
		while (i  < gc.getNumCivicOptionInfos() and not bChange):
			if (self.m_paeCurrentPolicies[i] != self.m_paeOriginalPolicies[i]):
				bChange = True
			i += 1		
		
		# Make the revolution button
		screen.deleteWidget(self.EXIT_NAME)
		if (activePlayer.canRevolution(0) and bChange):			
			screen.setText(self.EXIT_NAME, "Background", self.TEXT_REVOLUTION, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_REVOLUTION, 1, 0)
			screen.show(self.CANCEL_NAME)
		else:
			screen.setText(self.EXIT_NAME, "Background", self.TEXT_EXIT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, 1, -1)
			screen.hide(self.CANCEL_NAME)

		# Anarchy
		iTurns = activePlayer.getCivicAnarchyLength(self.m_paeDisplayPolicies)
		
		if (activePlayer.canRevolution(0)):
			szText = localText.getText("TXT_KEY_ANARCHY_TURNS", (iTurns, ))
		else:
			szText = CyGameTextMgr().setRevolutionHelp(self.iActivePlayer)

		screen.setLabel("PolicyRevText", "Background", SAS_FONT_TAG_LABEL + szText + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, self.X_SCREEN, self.BOTTOM_LINE_TOP + self.TEXT_MARGIN//2, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# Maintenance		
		#szText = localText.getText("TXT_KEY_CIVIC_SCREEN_UPKEEP", (activePlayer.getCivicUpkeep(self.m_paeDisplayPolicies, True), ))
		szText = localText.getText("TXT_KEY_CIVIC_SCREEN_UPKEEP", (activePlayer.getCivicUpkeep(self.m_paeDisplayPolicies, True)*(100+activePlayer.calculateInflationRate())/100, )) # K-Mod
		screen.setLabel("PolicyUpkeepText", "Background", SAS_FONT_TAG_LABEL + szText + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, self.X_SCREEN, self.BOTTOM_LINE_TOP + self.BOTTOM_LINE_HEIGHT - 2 * self.TEXT_MARGIN, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
	# Revolution!!!
	def Revolution(self, inputClass):

		activePlayer = gc.getPlayer(self.iActivePlayer)

		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED) :
			# advc.001d: Clause added to prevent revolution when viewing another civ's civics through the Debug menu
			if self.iActivePlayer == gc.getGame().getActivePlayer() and activePlayer.canRevolution(0):
				messageControl = CyMessageControl()
				messageControl.sendUpdateCivics(self.m_paeDisplayPolicies)			
			screen = self.getScreen()
			screen.hideScreen()


	def Cancel(self, inputClass):
		screen = self.getScreen()
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED) :
			for i in range (gc.getNumCivicOptionInfos()):
				self.m_paeCurrentPolicies[i] = self.m_paeOriginalPolicies[i]
				self.m_paeDisplayPolicies[i] = self.m_paeOriginalPolicies[i]
			
			self.drawContents()
			
	def getPolicyButtonName(self, iCivic):
		szName = self.BUTTON_NAME + str(iCivic)
		return szName

	def getPolicyTextName(self, iCivic):
		szName = self.TEXT_NAME + str(iCivic)
		return szName

	# Will handle the input for this screen...
	def handleInput(self, inputClass):
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED):
			screen = self.getScreen()
			iIndex = screen.getSelectedPullDownID(self.DEBUG_DROPDOWN_ID)
			self.setActivePlayer(screen.getPullDownData(self.DEBUG_DROPDOWN_ID, iIndex))
			self.drawContents()
			return 1
		elif (self.PolicyScreenInputMap.has_key(inputClass.getFunctionName())):	
			'Calls function mapped in CvPolicyScreen'
			# only get from the map if it has the key		

			# get bound function from map and call it
			self.PolicyScreenInputMap.get(inputClass.getFunctionName())(inputClass)
			return 1
		return 0
		
	def update(self, fDelta):
		return





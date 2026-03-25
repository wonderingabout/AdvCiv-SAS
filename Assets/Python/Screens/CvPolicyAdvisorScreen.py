## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import PyHelpers
import CvUtil
import ScreenInput
import CvScreenEnums
import CvScreensInterface
import BugCore
import PlayerUtil
import ReligionUtil
from SASFontUtils import *
from SASUtils import *

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer
AdvisorOpt = BugCore.game.Advisors

class CvPolicyAdvisorScreen:
	"Policy Advisor Screen"

	def __init__(self):
		self.SCREEN_NAME = "PolicyAdvisorScreen"
		self.CANCEL_NAME = "PolicyCancel"
		self.EXIT_NAME = "PolicyExit"
		self.TITLE_NAME = "PolicyTitleHeader"
		self.BUTTON_NAME = "PolicyAdvisorScreenButton"
		self.TEXT_NAME = "PolicyAdvisorScreenText"
		self.AREA_NAME = "PolicyAdvisorScreenArea"
		self.HELP_AREA_NAME = "PolicyAdvisorScreenHelpArea"
		self.HELP_IMAGE_NAME = "PolicyAdvisorScreenCivicOptionImage"
		self.DEBUG_DROPDOWN_ID =  "PolicyDropdownWidget"
		self.BACKGROUND_ID = "PolicyBackground"
		self.HELP_HEADER_NAME = "PolicyAdvisorScreenHeaderName"
		self.POLICY_OPTION_HEADER_NAME = "PolicyAdvisorScreenOptionHeader"
		self.PAGE_POLICY = 0
		self.PAGE_RELIGION = 1
		self.iPage = self.PAGE_POLICY
		self.PAGE_TAB_IDS = ["PolicyTabButton0", "PolicyTabButton1"]
		self.PAGE_LINK_WIDTH = []

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

		self.PolicyAdvisorScreenInputMap = {
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

		# <!-- custom: Religion advisor tab integration state/constants kept in Policy advisor init so no standalone Religion screen state is required anymore. (GPT-5.3-Codex) -->
		self.RELIGION_NAME = "ReligionText"
		self.RELIGION_BUTTON_NAME = "ReligionScreenButton"
		self.RELIGION_CITY_NAME = "ReligionCity"
		self.RELIGION_DEBUG_DROPDOWN_ID = "ReligionDropdownWidget"
		self.RELIGION_TABLE_ID = "ReligionTableWidget"
		self.RELIGION_AREA1_ID = "ReligionAreaWidget1"
		self.RELIGION_AREA2_ID = "ReligionAreaWidget2"
		self.RELIGION_PANEL_ID = "ReligionPanel"
		self.RELIGION_ANARCHY_WIDGET = "ReligionAnarchyWidget"
		self.RELIGION_STATUS_PANEL_ID = "ReligionStatusPanel"
		self.RELIGION_SCROLL_PANEL_ID = "ReligionList"
		self.RELIGION_HEADER_FOUNDED_ID = "ReligionHelpFoundedHeader"
		self.RELIGION_HEADER_HOLY_CITY_ID = "ReligionHelpHolyCityHeader"
		self.RELIGION_HEADER_INFLUENCE_ID = "ReligionHelpInfluenceHeader"
		self.BORDER_WIDTH = 2
		self.HIGHLIGHT_EXTRA_SIZE = 4
		self.DZ = -0.2
		self.Z_CONTROLS = self.Z_TEXT
		self.X_ANARCHY = 21
		self.LEFT_EDGE_TEXT = 10
		self.X_RELIGION_START = 180
		self.DX_RELIGION = 98
		self.Y_RELIGION = 35
		self.Y_FOUNDED = 90
		self.Y_HOLY_CITY = 115
		self.Y_INFLUENCE = 140
		self.Y_RELIGION_NAME = 58
		self.X_SCROLLABLE_RELIGION_AREA = 0
		self.Y_SCROLLABLE_RELIGION_AREA = 0
		self.X_RELIGION_AREA = 45
		self.Y_RELIGION_AREA = 84
		self.W_RELIGION_AREA = 934
		self.H_RELIGION_AREA = 175
		self.H_SCROLL_OFFSET = 20
		self.X_CITY1_AREA = 45
		self.X_CITY2_AREA = 522
		self.Y_CITY_AREA = 282
		self.W_CITY_AREA = 457
		self.H_CITY_AREA = 395
		self.X_CITY = 10
		self.DY_CITY = 38
		self.NUM_RELIGIONS = -1
		self.COL_ZOOM_CITY = 0
		self.COL_CITY_NAME = 1
		self.COL_FIRST_RELIGION = 2
		self.COL_FIRST_UNIT = 9
		self.COL_FIRST_BUILDING = 10
		self.COL_EFFECTS = 14
		self.TABLE_COLUMNS = 15
		self.iReligionExamined = -1
		self.iReligionSelected = -1
		self.iReligionOriginal = -1
		self.RELIGIONS = []
		self.bBUGConstants = False

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
		# <!-- custom: tab captions should name subsections, not advisor screens; keep them concise like other merged advisors. (GPT-5.3-Codex) -->
		self.TEXT_TAB_POLICY = localText.getText("TXT_KEY_CONCEPT_CIVICS", ()).upper()
		self.TEXT_TAB_RELIGION = localText.getText("TXT_KEY_CONCEPT_RELIGION", ()).upper()
		self.PAGE_NAME_LIST = [self.TEXT_TAB_POLICY, self.TEXT_TAB_RELIGION]
		self.EXIT_TEXT = self.TEXT_EXIT
		self.CONVERT_TEXT = SAS_FONT_TAG_TITLE + localText.getText("TXT_KEY_RELIGION_CONVERT", ()).upper() + SAS_FONT_TAG_CLOSE
		self.CANCEL_TEXT = self.TEXT_CANCEL

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
		self.PAGE_LINK_WIDTH[:] = getAdvisorRuntimeLinkWidths(CyInterface(), self.PAGE_NAME_LIST, self.TEXT_EXIT, self.X_EXIT)

		# <!-- custom: Religion tab layout follows runtime Policy advisor width/height so integrated tab scales with resolution like other migrated advisors. (GPT-5.3-Codex) -->
		self.X_RELIGION_AREA = 45
		self.W_RELIGION_AREA = self.W_SCREEN - 2 * self.X_RELIGION_AREA
		if self.isBugReligiousEnabled():
			self.Y_RELIGION_AREA = 44
			self.H_RELIGION_AREA = 250
		else:
			self.Y_RELIGION_AREA = 84
			self.H_RELIGION_AREA = 175
		self.Y_CITY_AREA = self.Y_RELIGION_AREA + self.H_RELIGION_AREA + 28
		self.H_CITY_AREA = self.Y_BOTTOM_PANEL - self.Y_CITY_AREA - 36
		self.W_CITY_AREA = (self.W_SCREEN - 3 * self.X_RELIGION_AREA) / 2
		self.X_CITY1_AREA = self.X_RELIGION_AREA
		self.X_CITY2_AREA = self.X_CITY1_AREA + self.W_CITY_AREA + self.X_RELIGION_AREA
		self.Y_RELIGION_STATUS = self.Y_CITY_AREA + self.H_CITY_AREA + 4
		self.H_RELIGION_STATUS = self.Y_BOTTOM_PANEL - self.Y_RELIGION_STATUS - 6

	def getScreen(self):
		return CyGInterfaceScreen(self.SCREEN_NAME, CvScreenEnums.POLICY_ADVISOR_SCREEN)

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

	def interfaceScreen (self, argsList=None):

		if argsList is not None:
			if type(argsList) in [list, tuple]:
				if len(argsList) > 0 and argsList[0] in [self.PAGE_POLICY, self.PAGE_RELIGION]:
					self.iPage = argsList[0]
			elif argsList in [self.PAGE_POLICY, self.PAGE_RELIGION]:
				self.iPage = argsList

		screen = self.getScreen()
		if screen.isActive():
			self.drawContents()
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
		# <!-- custom: use setLabel with X_TITLE/-0.1 to match Domestic/Foreign advisor title alignment exactly; setText/X_SCREEN rendered slightly off. (GPT-5.3-Codex) -->
		screen.setLabel(self.TITLE_NAME, "Background", self.TEXT_TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE, self.Y_TITLE, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		self.setActivePlayer(gc.getGame().getActivePlayer())						

		if (CyGame().isDebugMode()):
			self.szDropdownName = self.DEBUG_DROPDOWN_ID
			screen.addDropDownBoxGFC(self.szDropdownName, 22, 12, 300, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
			for j in range(gc.getMAX_PLAYERS()):
				if (gc.getPlayer(j).isAlive()):
					screen.addPullDownString(self.szDropdownName, gc.getPlayer(j).getName(), j, j, False )

		# Draw Contents
		self.drawContents()

		return 0

	# Draw the contents...
	def drawTabs(self):
		screen = self.getScreen()
		iX = 0
		for iPage in range(len(self.PAGE_NAME_LIST)):
			szLabel = self.PAGE_NAME_LIST[iPage]
			if iPage == self.iPage:
				szText = SAS_FONT_TAG_TITLE_BOLD + szLabel + SAS_FONT_TAG_CLOSE
			else:
				szText = SAS_FONT_TAG_TITLE + szLabel + SAS_FONT_TAG_CLOSE
			screen.setText(self.PAGE_TAB_IDS[iPage], "", szText, CvUtil.FONT_CENTER_JUSTIFY, iX + self.PAGE_LINK_WIDTH[iPage] / 2, self.Y_LINK, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, iPage, -1)
			iX += self.PAGE_LINK_WIDTH[iPage]

	def clearPolicyTabWidgets(self):
		screen = self.getScreen()
		screen.deleteWidget("PolicyBottomLine")
		screen.deleteWidget("PolicyRevText")
		screen.deleteWidget("PolicyUpkeepText")
		for i in range(gc.getNumCivicOptionInfos()):
			screen.deleteWidget(self.AREA_NAME + str(i))
			screen.deleteWidget(self.POLICY_OPTION_HEADER_NAME + str(i))
			screen.deleteWidget("PolicyHelpTextBackground" + str(i))
			screen.deleteWidget(self.HELP_HEADER_NAME + str(i))
			screen.deleteWidget(self.HELP_IMAGE_NAME + str(i))
			screen.deleteWidget(self.HELP_AREA_NAME + str(i))
		for j in range(gc.getNumCivicInfos()):
			screen.deleteWidget(self.getPolicyButtonName(j))
			screen.deleteWidget(self.getPolicyTextName(j))

	def clearReligionTabWidgets(self):
		screen = self.getScreen()
		screen.deleteWidget(self.RELIGION_PANEL_ID)
		screen.deleteWidget(self.RELIGION_SCROLL_PANEL_ID)
		screen.deleteWidget(self.RELIGION_AREA1_ID)
		screen.deleteWidget(self.RELIGION_AREA2_ID)
		screen.deleteWidget(self.RELIGION_TABLE_ID)
		screen.deleteWidget(self.RELIGION_STATUS_PANEL_ID)
		screen.deleteWidget(self.RELIGION_ANARCHY_WIDGET)
		screen.deleteWidget(self.RELIGION_HEADER_FOUNDED_ID)
		screen.deleteWidget(self.RELIGION_HEADER_HOLY_CITY_ID)
		screen.deleteWidget(self.RELIGION_HEADER_INFLUENCE_ID)
		for iRel in range(gc.getNumReligionInfos() + 1):
			screen.deleteWidget(self.getReligionButtonName(iRel))
			screen.deleteWidget(self.getReligionTextName(iRel))

	def drawContents(self):
		self.drawTabs()
		if self.iPage == self.PAGE_POLICY:
			self.clearReligionTabWidgets()
			self.drawPolicyTabContents()
		else:
			self.clearPolicyTabWidgets()
			self.drawReligionTabContents()

	def drawPolicyTabContents(self):
		screen = self.getScreen()
		screen.setLabel(self.TITLE_NAME, "Background", self.TEXT_TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE, self.Y_TITLE, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPanel("PolicyBottomLine", "", "", True, True, self.HEADINGS_SPACING, self.BOTTOM_LINE_TOP, self.BOTTOM_LINE_WIDTH, self.BOTTOM_LINE_HEIGHT, PanelStyles.PANEL_STYLE_MAIN)
		# Draw the radio buttons
		self.drawAllButtons()
		# Draw Help Text
		self.drawAllHelpText()
		# Update Maintenance/anarchy/etc.
		self.updateAnarchy()

	def drawReligionTabContents(self):
		screen = self.getScreen()
		# <!-- custom: keep advisor header stable across tabs (Policy Advisor), like Domestic/Foreign tabbed screens; tab labels already indicate the active subsection. (GPT-5.3-Codex) -->
		screen.setLabel(self.TITLE_NAME, "Background", self.TEXT_TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE, self.Y_TITLE, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		self.refreshReligionTabData()
		self.drawReligionInfo()
		self.drawHelpInfo()
		self.drawCityInfo(self.iReligionSelected)

	def refreshReligionTabData(self):
		self.iActivePlayer = gc.getGame().getActivePlayer()
		self.NO_STATE_BUTTON_ART = ArtFileMgr.getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath()
		if self.NUM_RELIGIONS == -1:
			self.NUM_RELIGIONS = ReligionUtil.getNumReligions()
			self.COL_FIRST_UNIT = self.COL_FIRST_RELIGION + self.NUM_RELIGIONS
			self.COL_FIRST_BUILDING = self.COL_FIRST_UNIT + ReligionUtil.getNumUnitTypes()
			self.COL_EFFECTS = self.COL_FIRST_BUILDING + ReligionUtil.getNumBuildingTypes()
			self.TABLE_COLUMNS = self.COL_EFFECTS + 1
		if self.isBugReligiousEnabled():
			if AdvisorOpt.isShowAllReligions():
				self.RELIGIONS = ReligionUtil.getAllReligions()
			elif AdvisorOpt.isShowFoundedReligions():
				self.RELIGIONS = ReligionUtil.getFoundedReligions()
			else:
				self.RELIGIONS = ReligionUtil.getPlayerReligions(gc.getPlayer(self.iActivePlayer))
		else:
			self.RELIGIONS = range(gc.getNumReligionInfos())
		self.iReligionSelected = gc.getPlayer(self.iActivePlayer).getStateReligion()
		if self.iReligionSelected == -1:
			self.iReligionSelected = gc.getNumReligionInfos()
		self.iReligionExamined = self.iReligionSelected
		self.iReligionOriginal = self.iReligionSelected

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

			screen.setLabel(self.POLICY_OPTION_HEADER_NAME + str(i), "Background",
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

	# Draws the religion buttons and information
	def drawReligionInfo(self):
		screen = self.getScreen()
		szArea = self.RELIGION_SCROLL_PANEL_ID

		screen.addPanel(self.RELIGION_PANEL_ID, "", "", False, True, self.X_RELIGION_AREA, self.Y_RELIGION_AREA, self.W_RELIGION_AREA, self.H_RELIGION_AREA + 5, PanelStyles.PANEL_STYLE_MAIN)
		screen.addScrollPanel(self.RELIGION_SCROLL_PANEL_ID, u"", self.X_RELIGION_AREA, self.Y_RELIGION_AREA, self.W_RELIGION_AREA, self.H_RELIGION_AREA, PanelStyles.PANEL_STYLE_EXTERNAL)
		screen.setActivation(self.RELIGION_SCROLL_PANEL_ID, ActivationTypes.ACTIVATE_NORMAL)

		xLoop = self.X_RELIGION_START
		for iRel in self.RELIGIONS:
			szButtonName = self.getReligionButtonName(iRel)
			if gc.getGame().getReligionGameTurnFounded(iRel) >= 0:
				screen.addCheckBoxGFCAt(szArea, szButtonName, gc.getReligionInfo(iRel).getButton(), ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), self.X_SCROLLABLE_RELIGION_AREA + xLoop - 25, self.Y_SCROLLABLE_RELIGION_AREA + 5, self.BUTTON_SIZE, self.BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL, False)
			else:
				screen.setImageButtonAt(szButtonName, szArea, gc.getReligionInfo(iRel).getButtonDisabled(), self.X_SCROLLABLE_RELIGION_AREA + xLoop - 25, self.Y_SCROLLABLE_RELIGION_AREA + 5, self.BUTTON_SIZE, self.BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setLabelAt(self.getReligionTextName(iRel), szArea, SAS_FONT_TAG_LABEL + gc.getReligionInfo(iRel).getDescription() + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, self.X_SCROLLABLE_RELIGION_AREA + xLoop, self.Y_RELIGION_NAME, self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop += self.DX_RELIGION

		szButtonName = self.getReligionButtonName(gc.getNumReligionInfos())
		screen.addCheckBoxGFCAt(szArea, szButtonName, self.NO_STATE_BUTTON_ART, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), self.X_SCROLLABLE_RELIGION_AREA + xLoop - 25, self.Y_SCROLLABLE_RELIGION_AREA + 5, self.BUTTON_SIZE, self.BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL, False)
		screen.setLabelAt(self.getReligionTextName(gc.getNumReligionInfos()), szArea, SAS_FONT_TAG_LABEL + localText.getText("TXT_KEY_RELIGION_SCREEN_NO_STATE", ()) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, self.X_SCROLLABLE_RELIGION_AREA + xLoop, self.Y_RELIGION_NAME, self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def drawHelpInfo(self):
		screen = self.getScreen()
		szArea = self.RELIGION_SCROLL_PANEL_ID

		screen.setLabelAt(self.RELIGION_HEADER_FOUNDED_ID, szArea, SAS_FONT_TAG_LABEL + localText.getText("TXT_KEY_RELIGION_SCREEN_DATE_FOUNDED", ()) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, self.Y_FOUNDED, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		xLoop = self.X_RELIGION_START
		for iRel in self.RELIGIONS:
			if gc.getGame().getReligionGameTurnFounded(iRel) >= 0:
				szFounded = CyGameTextMgr().getTimeStr(gc.getGame().getReligionGameTurnFounded(iRel), false)
				screen.setLabelAt("ReligionFoundedValue" + str(iRel), szArea, SAS_FONT_TAG_LABEL + szFounded + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_FOUNDED, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop += self.DX_RELIGION

		screen.setLabelAt(self.RELIGION_HEADER_HOLY_CITY_ID, szArea, SAS_FONT_TAG_LABEL + localText.getText("TXT_KEY_RELIGION_SCREEN_HOLY_CITY", ()) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, self.Y_HOLY_CITY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		xLoop = self.X_RELIGION_START
		for iRel in self.RELIGIONS:
			if gc.getGame().getReligionGameTurnFounded(iRel) >= 0:
				pHolyCity = gc.getGame().getHolyCity(iRel)
				if pHolyCity.isNone():
					screen.setLabelAt("ReligionHolyCityValue" + str(iRel), szArea, SAS_FONT_TAG_LABEL + localText.getText("TXT_KEY_NONE", ()) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				elif not pHolyCity.isRevealed(gc.getPlayer(self.iActivePlayer).getTeam(), True): # advc.001d
					screen.setLabelAt("ReligionHolyCityValue" + str(iRel), szArea, SAS_FONT_TAG_LABEL + localText.getText("TXT_KEY_UNKNOWN", ()) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				else:
					screen.setLabelAt("ReligionHolyCityOwner" + str(iRel), szArea, SAS_FONT_TAG_LABEL + (u"(%s)" % gc.getPlayer(pHolyCity.getOwner()).getCivilizationAdjective(0)) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY + 8, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
					screen.setLabelAt("ReligionHolyCityValue" + str(iRel), szArea, SAS_FONT_TAG_LABEL + pHolyCity.getName() + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY - 8, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop += self.DX_RELIGION

		screen.setLabelAt(self.RELIGION_HEADER_INFLUENCE_ID, szArea, SAS_FONT_TAG_LABEL + localText.getText("TXT_KEY_RELIGION_SCREEN_INFLUENCE", ()) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, self.Y_INFLUENCE, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		xLoop = self.X_RELIGION_START
		for iRel in self.RELIGIONS:
			if gc.getGame().getReligionGameTurnFounded(iRel) >= 0:
				szFounded = str(gc.getGame().calculateReligionPercent(iRel)) + "%"
				screen.setLabelAt("ReligionInfluenceValue" + str(iRel), szArea, SAS_FONT_TAG_LABEL + szFounded + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_INFLUENCE, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop += self.DX_RELIGION

		if self.isBugReligiousEnabled():
			self.BUGConstants()
			iPlayer = PyPlayer(self.iActivePlayer)
			cityList = iPlayer.getCityList()
			iCities = [0] * self.NUM_RELIGIONS
			iTemple = [0] * self.NUM_RELIGIONS
			iMonastery = [0] * self.NUM_RELIGIONS
			iMissionaries_Active = [0] * self.NUM_RELIGIONS
			iMissionaries_Construct = [0] * self.NUM_RELIGIONS

			for pLoopCity in cityList:
				lReligions = pLoopCity.getReligions()
				for iRel in self.RELIGIONS:
					if iRel in lReligions:
						iCities[iRel] += 1
					iBldg = ReligionUtil.getBuilding(iRel, ReligionUtil.BUILDING_TEMPLE)
					if self.calculateBuilding(pLoopCity, iBldg) == self.objectHave:
						iTemple[iRel] += 1
					iBldg = ReligionUtil.getBuilding(iRel, ReligionUtil.BUILDING_MONASTERY)
					if self.calculateBuilding(pLoopCity, iBldg) == self.objectHave:
						iMonastery[iRel] += 1
					iUnit = ReligionUtil.getUnit(iRel, ReligionUtil.UNIT_MISSIONARY)
					if pLoopCity.GetCy().getFirstUnitOrder(iUnit) != -1:
						iMissionaries_Construct[iRel] += 1

			for iUnit in PlayerUtil.playerUnits(self.iActivePlayer):
				for iRel in self.RELIGIONS:
					if iUnit.getUnitType() == ReligionUtil.getUnit(iRel, ReligionUtil.UNIT_MISSIONARY):
						iMissionaries_Active[iRel] += 1

			iY = self.Y_INFLUENCE + 20
			sCities = "%s [%i]:" % (self.szCities, len(cityList))
			screen.setLabelAt("ReligionCityCountHeader", szArea, SAS_FONT_TAG_LABEL + sCities + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop = self.X_RELIGION_START
			for iRel in self.RELIGIONS:
				if gc.getGame().getReligionGameTurnFounded(iRel) >= 0:
					screen.setLabelAt("ReligionCityCount" + str(iRel), szArea, SAS_FONT_TAG_LABEL + ("%i" % iCities[iRel]) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLoop, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				xLoop += self.DX_RELIGION

			iY = self.Y_INFLUENCE + 40
			screen.setLabelAt("ReligionTempleHeader", szArea, SAS_FONT_TAG_LABEL + self.szTemples + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop = self.X_RELIGION_START
			for iRel in self.RELIGIONS:
				if gc.getGame().getReligionGameTurnFounded(iRel) >= 0:
					screen.setLabelAt("ReligionTempleCount" + str(iRel), szArea, SAS_FONT_TAG_LABEL + ("%i" % iTemple[iRel]) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLoop, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				xLoop += self.DX_RELIGION

			iY = self.Y_INFLUENCE + 60
			screen.setLabelAt("ReligionMonasteryHeader", szArea, SAS_FONT_TAG_LABEL + self.szMonastaries + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop = self.X_RELIGION_START
			for iRel in self.RELIGIONS:
				if gc.getGame().getReligionGameTurnFounded(iRel) >= 0:
					screen.setLabelAt("ReligionMonasteryCount" + str(iRel), szArea, SAS_FONT_TAG_LABEL + ("%i" % iMonastery[iRel]) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLoop, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				xLoop += self.DX_RELIGION

			iY = self.Y_INFLUENCE + 80
			screen.setLabelAt("ReligionMissionaryHeader", szArea, SAS_FONT_TAG_LABEL + self.szMissionaries + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			xLoop = self.X_RELIGION_START
			for iRel in self.RELIGIONS:
				if gc.getGame().getReligionGameTurnFounded(iRel) >= 0:
					szFounded = "%i [%i]" % (iMissionaries_Active[iRel], iMissionaries_Construct[iRel])
					screen.setLabelAt("ReligionMissionaryCount" + str(iRel), szArea, SAS_FONT_TAG_LABEL + szFounded + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLoop, iY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				xLoop += self.DX_RELIGION

	# BUG constants
	def BUGConstants(self):
		if self.bBUGConstants:
			return
		self.bBUGConstants = True
		self.hammerIcon = u"%c" % (gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar())
		self.objectIsPresent = "x"
		self.objectIsNotPresent = "-"
		self.objectCanBeBuild = "o"
		self.objectUnderConstruction = self.hammerIcon
		self.objectHave = localText.changeTextColor(self.objectIsPresent, gc.getInfoTypeForString("COLOR_GREEN"))
		self.objectNotPossible = localText.changeTextColor(self.objectIsNotPresent, gc.getInfoTypeForString("COLOR_RED"))
		self.objectPossible = localText.changeTextColor(self.objectCanBeBuild, gc.getInfoTypeForString("COLOR_BLUE"))
		self.objectHaveObsolete = localText.changeTextColor(self.objectIsPresent, gc.getInfoTypeForString("COLOR_WHITE"))
		self.objectNotPossibleConcurrent = localText.changeTextColor(self.objectIsNotPresent, gc.getInfoTypeForString("COLOR_YELLOW"))
		self.objectPossibleConcurrent = localText.changeTextColor(self.objectCanBeBuild, gc.getInfoTypeForString("COLOR_YELLOW"))
		self.szCities = localText.getText("TXT_KEY_BUG_RELIGIOUS_CITY", ())
		self.szTemples = localText.getText("TXT_KEY_BUG_RELIGIOUS_TEMPLE", ())
		self.szMonastaries = localText.getText("TXT_KEY_BUG_RELIGIOUS_MONASTARY", ())
		self.szMissionaries = localText.getText("TXT_KEY_BUG_RELIGIOUS_MISSIONARY", ())
		self.zoomArt = ArtFileMgr.getInterfaceArtInfo("INTERFACE_BUTTONS_CITYSELECTION").getPath()
		self.sCity = localText.getText("TXT_KEY_WONDER_CITY", ())
		if ReligionUtil.getNumReligions() > 7:
			self.H_SCROLL_OFFSET = 20
		else:
			self.H_SCROLL_OFFSET = 0

	def drawCityInfo(self, iReligion):
		screen = self.getScreen()
		if iReligion == gc.getNumReligionInfos():
			iLinkReligion = -1
		else:
			iLinkReligion = iReligion

		screen.deleteWidget(self.RELIGION_AREA1_ID)
		screen.deleteWidget(self.RELIGION_AREA2_ID)
		screen.deleteWidget(self.RELIGION_TABLE_ID)

		if self.isBugReligiousEnabled():
			screen.addPanel(self.RELIGION_AREA1_ID, "", "", True, True, self.X_RELIGION_AREA, self.Y_RELIGION_AREA + self.H_RELIGION_AREA + self.H_SCROLL_OFFSET + 3, self.W_RELIGION_AREA, self.H_CITY_AREA - self.H_SCROLL_OFFSET + 20, PanelStyles.PANEL_STYLE_MAIN)
		else:
			screen.addPanel(self.RELIGION_AREA1_ID, "", "", True, True, self.X_CITY1_AREA, self.Y_CITY_AREA, self.W_CITY_AREA, self.H_CITY_AREA, PanelStyles.PANEL_STYLE_MAIN)
			screen.addPanel(self.RELIGION_AREA2_ID, "", "", True, True, self.X_CITY2_AREA, self.Y_CITY_AREA, self.W_CITY_AREA, self.H_CITY_AREA, PanelStyles.PANEL_STYLE_MAIN)

		for iRel in self.RELIGIONS:
			screen.setState(self.getReligionButtonName(iRel), self.iReligionSelected == iRel)
		screen.setState(self.getReligionButtonName(gc.getNumReligionInfos()), self.iReligionSelected == gc.getNumReligionInfos())

		iPlayer = PyPlayer(self.iActivePlayer)
		cityList = iPlayer.getCityList()

		if self.isBugReligiousEnabled():
			screen.addTableControlGFC(self.RELIGION_TABLE_ID, self.TABLE_COLUMNS, self.X_RELIGION_AREA + 15, self.Y_RELIGION_AREA + self.H_RELIGION_AREA + self.H_SCROLL_OFFSET + 3 + 15, self.W_RELIGION_AREA - 2 * 15, self.H_CITY_AREA - self.H_SCROLL_OFFSET - 5, True, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
			screen.enableSort(self.RELIGION_TABLE_ID)
			screen.setTableColumnHeader(self.RELIGION_TABLE_ID, self.COL_ZOOM_CITY, "", 30)
			screen.setTableColumnHeader(self.RELIGION_TABLE_ID, self.COL_CITY_NAME, SAS_FONT_TAG_LABEL + self.sCity + SAS_FONT_TAG_CLOSE, 115)

			for iRel in range(self.NUM_RELIGIONS):
				if gc.getGame().getReligionGameTurnFounded(iRel) >= 0:
					screen.setTableColumnHeader(self.RELIGION_TABLE_ID, self.COL_FIRST_RELIGION + iRel, SAS_FONT_TAG_LABEL + (u"%c" % (gc.getReligionInfo(iRel).getChar())) + SAS_FONT_TAG_CLOSE, 25)
			for type in ReligionUtil.getUnitTypes():
				screen.setTableColumnHeader(self.RELIGION_TABLE_ID, self.COL_FIRST_UNIT + type.index, SAS_FONT_TAG_LABEL + (u"%s" % type.icon) + SAS_FONT_TAG_CLOSE, 30)
			for type in ReligionUtil.getBuildingTypes():
				screen.setTableColumnHeader(self.RELIGION_TABLE_ID, self.COL_FIRST_BUILDING + type.index, SAS_FONT_TAG_LABEL + (u"%s" % type.icon) + SAS_FONT_TAG_CLOSE, 30)
			screen.setTableColumnHeader(self.RELIGION_TABLE_ID, self.COL_EFFECTS, "", 400)

			for iCity in range(len(cityList)):
				pLoopCity = cityList[iCity]
				screen.appendTableRow(self.RELIGION_TABLE_ID)
				screen.setTableText(self.RELIGION_TABLE_ID, self.COL_ZOOM_CITY, iCity, "", self.zoomArt, WidgetTypes.WIDGET_ZOOM_CITY, pLoopCity.getOwner(), pLoopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)
				screen.setTableText(self.RELIGION_TABLE_ID, self.COL_CITY_NAME, iCity, SAS_FONT_TAG_LABEL + pLoopCity.getName() + SAS_FONT_TAG_CLOSE, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

				lHolyCity = pLoopCity.getHolyCity()
				lReligions = pLoopCity.getReligions()
				for iRel in range(self.NUM_RELIGIONS):
					if gc.getGame().getReligionGameTurnFounded(iRel) >= 0:
						szReligionIcon = ""
						if iRel in lHolyCity:
							szReligionIcon = SAS_FONT_TAG_LABEL + (u"%c" % (gc.getReligionInfo(iRel).getHolyCityChar())) + SAS_FONT_TAG_CLOSE
						elif iRel in lReligions:
							szReligionIcon = SAS_FONT_TAG_LABEL + (u"%c" % (gc.getReligionInfo(iRel).getChar())) + SAS_FONT_TAG_CLOSE
						screen.setTableText(self.RELIGION_TABLE_ID, self.COL_FIRST_RELIGION + iRel, iCity, szReligionIcon, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				if ReligionUtil.isValid(iReligion):
					for i in range(ReligionUtil.getNumUnitTypes()):
						iUnit = ReligionUtil.getUnit(iReligion, i)
						if pLoopCity.GetCy().getFirstUnitOrder(iUnit) != -1:
							sUnit = self.objectUnderConstruction
						elif pLoopCity.GetCy().canTrain(iUnit, False, False):
							sUnit = self.objectPossible
						else:
							sUnit = self.objectNotPossible
						screen.setTableText(self.RELIGION_TABLE_ID, self.COL_FIRST_UNIT + i, iCity, SAS_FONT_TAG_LABEL + sUnit + SAS_FONT_TAG_CLOSE, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

					for i in range(ReligionUtil.getNumBuildingTypes()):
						iBldg = ReligionUtil.getBuilding(iReligion, i)
						sBldg = self.calculateBuilding(pLoopCity, iBldg)
						screen.setTableText(self.RELIGION_TABLE_ID, self.COL_FIRST_BUILDING + i, iCity, SAS_FONT_TAG_LABEL + sBldg + SAS_FONT_TAG_CLOSE, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				sHelp = self.cityHelp(lReligions, pLoopCity.GetCy(), iLinkReligion)
				screen.setTableText(self.RELIGION_TABLE_ID, self.COL_EFFECTS, iCity, SAS_FONT_TAG_LABEL + sHelp + SAS_FONT_TAG_CLOSE, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		else:
			szLeftCities = u""
			szRightCities = u""
			for i in range(len(cityList)):
				bFirstColumn = (i % 2 == 0)
				pLoopCity = cityList[i]
				szCityName = u""
				if pLoopCity.isCapital():
					szCityName += u"%c" % CyGame().getSymbolID(FontSymbols.STAR_CHAR)
				lHolyCity = pLoopCity.getHolyCity()
				if lHolyCity:
					for iI in range(len(lHolyCity)):
						szCityName += u"%c" % (gc.getReligionInfo(lHolyCity[iI]).getHolyCityChar())
				lReligions = pLoopCity.getReligions()
				if lReligions:
					for iI in range(len(lReligions)):
						if lReligions[iI] not in lHolyCity:
							szCityName += u"%c" % (gc.getReligionInfo(lReligions[iI]).getChar())
				szCityName += pLoopCity.getName()[0:17] + "  "
				szCityName += self.cityHelp(lReligions, pLoopCity.GetCy(), iLinkReligion)
				if bFirstColumn:
					szLeftCities += u"<font=3>" + szCityName + u"</font>\n"
				else:
					szRightCities += u"<font=3>" + szCityName + u"</font>\n"

			screen.addMultilineText("Child" + self.RELIGION_AREA1_ID, szLeftCities, self.X_CITY1_AREA + 5, self.Y_CITY_AREA + 5, self.W_CITY_AREA - 10, self.H_CITY_AREA - 10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
			screen.addMultilineText("Child" + self.RELIGION_AREA2_ID, szRightCities, self.X_CITY2_AREA + 5, self.Y_CITY_AREA + 5, self.W_CITY_AREA - 10, self.H_CITY_AREA - 10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		if not self.canConvert(iLinkReligion) or iLinkReligion == self.iReligionOriginal:
			screen.setText(self.EXIT_NAME, "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, 1, 0)
			screen.hide(self.CANCEL_NAME)
			szAnarchyTime = CyGameTextMgr().setConvertHelp(self.iActivePlayer, iLinkReligion)
		else:
			screen.setText(self.EXIT_NAME, "Background", self.CONVERT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CONVERT, iLinkReligion, 1)
			screen.show(self.CANCEL_NAME)
			szAnarchyTime = localText.getText("TXT_KEY_ANARCHY_TURNS", (gc.getPlayer(self.iActivePlayer).getReligionAnarchyLength(), ))

		# <!-- custom: keep Religion status/help text out of the footer bar to avoid overlap with tab links/footer actions; use a dedicated strip panel below the city table. (GPT-5.3-Codex) -->
		screen.addPanel(self.RELIGION_STATUS_PANEL_ID, "", "", True, True, self.X_RELIGION_AREA, self.Y_RELIGION_STATUS, self.W_RELIGION_AREA, self.H_RELIGION_STATUS, PanelStyles.PANEL_STYLE_MAIN)
		screen.setLabel(self.RELIGION_ANARCHY_WIDGET, "Background", SAS_FONT_TAG_LABEL + szAnarchyTime + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, self.X_RELIGION_AREA + self.W_RELIGION_AREA / 2, self.Y_RELIGION_STATUS + self.H_RELIGION_STATUS / 2 - 8, self.Z_TEXT, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def cityHelp(self, lReligions, kCity, eHoverReligion):
		sHelp = ""
		bFirst = True
		eCurrStateReligion = gc.getPlayer(self.iActivePlayer).getStateReligion()
		for eReligion in lReligions:
			sLoopHelp = CyGameTextMgr().getReligionHelpCity(eReligion, kCity, False, False, eHoverReligion != -1 and (eReligion == eHoverReligion) != (eReligion == eCurrStateReligion), eHoverReligion == -1)
			if sLoopHelp:
				if not bFirst:
					sHelp += u", "
				bFirst = False
				sHelp += sLoopHelp
		return sHelp

	def isBugReligiousEnabled(self):
		return not AdvisorOpt.isReligious()

	def getReligionButtonName(self, iReligion):
		return self.RELIGION_BUTTON_NAME + str(iReligion)

	def getReligionTextName(self, iReligion):
		return self.RELIGION_NAME + str(iReligion)

	def canConvert(self, iReligion):
		iCurrentReligion = gc.getPlayer(self.iActivePlayer).getStateReligion()
		if iReligion == gc.getNumReligionInfos():
			iConvertReligion = -1
		else:
			iConvertReligion = iReligion
		return (iConvertReligion != iCurrentReligion and gc.getPlayer(self.iActivePlayer).canConvert(iConvertReligion))

	def ReligionScreenButton(self, inputClass):
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
			if inputClass.getID() == gc.getNumReligionInfos() or gc.getGame().getReligionGameTurnFounded(inputClass.getID()) >= 0:
				self.iReligionSelected = inputClass.getID()
				self.iReligionExamined = self.iReligionSelected
				self.drawCityInfo(self.iReligionSelected)
		elif inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_ON:
			if inputClass.getID() == gc.getNumReligionInfos() or gc.getGame().getReligionGameTurnFounded(inputClass.getID()) >= 0:
				self.iReligionExamined = inputClass.getID()
				self.drawCityInfo(self.iReligionExamined)
		elif inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_OFF:
			self.iReligionExamined = self.iReligionSelected
			self.drawCityInfo(self.iReligionSelected)
		return 0

	def ReligionConvert(self, inputClass):
		screen = self.getScreen()
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
			screen.hideScreen()

	def ReligionCancel(self, inputClass):
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
			self.iReligionSelected = self.iReligionOriginal
			if -1 == self.iReligionSelected:
				self.iReligionSelected = gc.getNumReligionInfos()
			self.drawCityInfo(self.iReligionSelected)

	def calculateBuilding(self, city, bldg):
		if city.getNumBuilding(bldg) > 0:
			return self.objectHave
		elif city.GetCy().getFirstBuildingOrder(bldg) != -1:
			return self.objectUnderConstruction
		elif city.GetCy().canConstruct(bldg, False, False, False):
			return self.objectPossible
		elif city.GetCy().canConstruct(bldg, True, False, False):
			return self.objectPossibleConcurrent
		else:
			return self.objectNotPossible

	# Will handle the input for this screen...
	def handleInput(self, inputClass):
		szWidgetName = inputClass.getFunctionName()
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and szWidgetName.startswith("PolicyTabButton"):
			iData1 = inputClass.getData1()
			if iData1 in [self.PAGE_POLICY, self.PAGE_RELIGION] and iData1 != self.iPage:
				self.iPage = iData1
				self.drawContents()
			return 1

		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED):
			screen = self.getScreen()
			if self.iPage == self.PAGE_POLICY:
				iIndex = screen.getSelectedPullDownID(self.DEBUG_DROPDOWN_ID)
				self.setActivePlayer(screen.getPullDownData(self.DEBUG_DROPDOWN_ID, iIndex))
				self.drawContents()
			else:
				szWidgetName = inputClass.getFunctionName()
				if szWidgetName != self.RELIGION_TABLE_ID:
					iIndex = screen.getSelectedPullDownID(self.DEBUG_DROPDOWN_ID)
					self.iActivePlayer = screen.getPullDownData(self.DEBUG_DROPDOWN_ID, iIndex)
					self.drawReligionInfo()
					self.drawHelpInfo()
					self.drawCityInfo(self.iReligionSelected)
			return 1

		if self.iPage == self.PAGE_POLICY:
			if self.PolicyAdvisorScreenInputMap.has_key(inputClass.getFunctionName()):
				self.PolicyAdvisorScreenInputMap.get(inputClass.getFunctionName())(inputClass)
				return 1
		else:
			if szWidgetName == self.RELIGION_TABLE_ID:
				if inputClass.getMouseX() == 0:
					screen = self.getScreen()
					screen.hideScreen()
					pPlayer = gc.getPlayer(inputClass.getData1())
					pCity = pPlayer.getCity(inputClass.getData2())
					CyInterface().selectCity(pCity, true)
				return 1
			if szWidgetName == self.CANCEL_NAME:
				self.ReligionCancel(inputClass)
				return 1
			if szWidgetName == self.RELIGION_NAME or szWidgetName == self.RELIGION_BUTTON_NAME:
				self.ReligionScreenButton(inputClass)
				return 1
			if szWidgetName == self.EXIT_NAME and inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
				self.ReligionConvert(inputClass)
				return 1
			return 0
		return 0
		
	def update(self, fDelta):
		# <!-- custom: no Religion dirty-bit enum exists in this branch; keep tab refresh event-driven via input/actions. (GPT-5.3-Codex) -->
		return

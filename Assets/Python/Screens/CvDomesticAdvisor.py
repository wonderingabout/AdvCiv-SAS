## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import BugUtil
import PlayerUtil
import TradeUtil
from SASFontUtils import *
from SASUtils import *

#	IMPORTANT INFORMATION
#	
#	All widget names MUST be unique when creating screens.  If you create a widget named 'Hello', and then try to create another named 'Hello', it will modify the first hello.
#
#	Also, when attaching widgets, 'Background' is a reserve word meant for the background widget.  Do NOT use 'Background' to name any widget, but when attaching to the background, please use the 'Background' keyword.

#  Thanks to Lee Reeves, AKA Taelis on civfanatics.com
#  Thanks to Solver


# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvDomesticAdvisor:
	# Domestic Advisor Screen
	#
	def __init__(self):
		self.listSelectedCities = []
		self.iLanguageLoaded = -1
		# <!-- custom: keep screen-independent advisor edge constants in init; runtime resolution-dependent geometry is computed in interfaceScreen through shared SASUtils helpers. (GPT-5.3-Codex) -->
		self.W_LEFT_SPACE_FOR_COMMERCE_SLIDERS = SAS_ADVISOR_LEFT_SPACE_FOR_COMMERCE_SLIDERS
		self.W_RIGHT_SPACE_FOR_SCOREBOARD = SAS_ADVISOR_RIGHT_SPACE_FOR_SCOREBOARD
		self.H_TOP_SPACE_FOR_TECH_BAR = SAS_ADVISOR_TOP_SPACE_FOR_TECH_BAR
		self.H_BOTTOM_SPACE = SAS_ADVISOR_BOTTOM_SPACE
		self.nNormalizedTableWidth = 970
		self.nFirstSpecialistX = 30
		self.nSpecialistWidth = 32
		self.nSpecialistLength = 32
		self.nSpecialistDistance = 100
		self.nPlusOffsetX = -4
		self.nMinusOffsetX = 16
		self.nPlusOffsetY = self.nMinusOffsetY = 30
		self.nPlusWidth = self.nPlusHeight = self.nMinusWidth = self.nMinusHeight = 20
		self.nSpecTextOffsetX = 40
		self.nSpecTextOffsetY = 10
		self.Y_TITLE = SAS_ADVISOR_TITLE_Y
		self.PAGE_OVERVIEW = 0
		self.PAGE_FINANCE = 1
		self.iPage = self.PAGE_OVERVIEW
		self.PAGE_TAB_IDS = ["DomesticTabButton0", "DomesticTabButton1"]
		self.PAGE_LINK_WIDTH = []
		self.bOverviewTableCreated = False
		self.nFinanceWidgetCount = 0
		self.FINANCE_WIDGET_ID = "DomesticFinanceWidget"
		# <!-- custom: finance-tab layout constants are screen-independent; keep them in init and only compute runtime positions/sizes in configureFinanceLayout. (GPT-5.3-Codex) -->
		self.FINANCE_INNER_MARGIN = 24
		self.FINANCE_COLUMN_GAP = 20
		self.FINANCE_TOP_PANEL_HEIGHT = 90
		self.FINANCE_TEXT_MARGIN = 15
		self.FINANCE_Y_SPACING = 30
		self.FINANCE_Z_CONTROLS = -2.3
		self.FINANCE_DZ = -0.2
		# <!-- custom: tab labels that do not depend on runtime geometry stay in init/initText; only link widths are runtime-dependent. (GPT-5.3-Codex) -->
		self.TEXT_TAB_OVERVIEW = "OVERVIEW"

	def initText(self):
		# <!-- custom: cache Domestic Advisor header texts/icons once per language to avoid repeated translation/symbol lookups on redraw. Keep column widths runtime-based because they depend on current screen size. (GPT-5.3-Codex) -->
		if self.iLanguageLoaded == CyGame().getCurrentLanguage() or not CyGame().isFinalInitialized():
			return
		self.iLanguageLoaded = CyGame().getCurrentLanguage()

		# <!-- custom: cache only raw header text/symbols in init; apply font tags at draw time so runtime label scaling always takes effect. (GPT-5.3-Codex) -->
		self.HEADER_NAME = localText.getText("TXT_KEY_DOMESTIC_ADVISOR_NAME", ())
		self.HEADER_POPULATION = (u"%c" % CyGame().getSymbolID(FontSymbols.CITIZEN_CHAR))
		self.HEADER_HAPPINESS = (u"%c" % CyGame().getSymbolID(FontSymbols.HAPPY_CHAR))
		self.HEADER_HEALTH = (u"%c" % CyGame().getSymbolID(FontSymbols.HEALTHY_CHAR))
		self.HEADER_FOOD = (u"%c" % gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar())
		self.HEADER_PRODUCTION = (u"%c" % gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar())
		self.HEADER_GOLD = (u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar())
		self.HEADER_RESEARCH = (u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar())
		self.HEADER_ESPIONAGE = (u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_ESPIONAGE).getChar())
		self.HEADER_CULTURE = (u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar())
		self.HEADER_TRADE = (u"%c" % CyGame().getSymbolID(FontSymbols.TRADE_CHAR))
		self.HEADER_MAINTENANCE = (u"%c" % CyGame().getSymbolID(FontSymbols.BAD_GOLD_CHAR))
		self.HEADER_GREAT_PERSON = (u"%c" % CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR))
		self.HEADER_GARRISON = (u"%c" % CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR))
		self.HEADER_PRODUCING = localText.getText("TXT_KEY_DOMESTIC_ADVISOR_PRODUCING", ())
		self.HEADER_REVOLT = (u"%c" % CyGame().getSymbolID(FontSymbols.OCCUPATION_CHAR))
		self.SCREEN_TITLE = SAS_FONT_TAG_TITLE_BOLD + localText.getText("TXT_KEY_DOMESTIC_ADVISOR_TITLE", ()).upper() + SAS_FONT_TAG_CLOSE
		self.TEXT_EXIT = SAS_FONT_TAG_TITLE + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + SAS_FONT_TAG_CLOSE
		self.TEXT_TAB_FINANCE = localText.getText("TXT_KEY_ECONOMICS_ADVISOR_FINANCE_TAB", ()).upper()
		self.PAGE_NAME_LIST = [self.TEXT_TAB_OVERVIEW, self.TEXT_TAB_FINANCE]
		self.COLOR_YELLOW = gc.getInfoTypeForString("COLOR_YELLOW")
		self.COLOR_POSITIVE_PREFIX = localText.getText("TXT_KEY_COLOR_POSITIVE", ())
		self.COLOR_NEGATIVE_PREFIX = localText.getText("TXT_KEY_COLOR_NEGATIVE", ())
		self.COLOR_REVERT_SUFFIX = localText.getText("TXT_KEY_COLOR_REVERT", ())
		self.ART_SCREEN_BG_OPAQUE = ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath()
		self.ART_CITY_SELECTION_BUTTON = ArtFileMgr.getInterfaceArtInfo("INTERFACE_BUTTONS_CITYSELECTION").getPath()

		# <!-- custom: cache finance-tab deterministic labels in initText (language-dependent only) to avoid repeated lookup on each redraw. (GPT-5.3-Codex) -->
		self.TEXT_FIN_COMMERCE = localText.getText("TXT_KEY_CONCEPT_COMMERCE", ())
		self.TEXT_FIN_INCOME_HEADER = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_INCOME_HEADER", ())
		self.TEXT_FIN_EXPENSES_HEADER = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_EXPENSES_HEADER", ())
		self.TEXT_FIN_DOMESTIC_TRADE = localText.getText("TXT_KEY_CONCEPT_DOMESTIC_TRADE", ())
		self.TEXT_FIN_TRADE = localText.getText("TXT_KEY_CONCEPT_TRADE", ())
		self.TEXT_FIN_FOREIGN_TRADE = localText.getText("TXT_KEY_CONCEPT_FOREIGN_TRADE", ())
		self.TEXT_FIN_CORPORATIONS = localText.getText("TXT_KEY_CONCEPT_CORPORATIONS", ())
		self.TEXT_FIN_SPECIALISTS = localText.getText("TXT_KEY_CONCEPT_SPECIALISTS", ())
		self.TEXT_FIN_BUILDINGS = localText.getText("TXT_KEY_CONCEPT_BUILDINGS", ())
		self.TEXT_FIN_CIVICS_MULTIPLIERS = localText.getText("TXT_KEY_MISC_CIVICS_MULTIPLIERS", ())
		self.TEXT_FIN_BUG_COMMERCE = localText.getText("TXT_KEY_BUG_FINANCIAL_ADVISOR_COMMERCE", ())
		self.TEXT_FIN_TAXES = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_TAXES", ())
		self.TEXT_FIN_HQ = localText.getText("TXT_KEY_CORPORATION_HEADQUARTERS", ())
		self.TEXT_FIN_SHRINES = localText.getText("TXT_KEY_CONCEPT_RELIGIOUS_SHRINES", ())
		self.TEXT_FIN_WEALTH = localText.getText("TXT_KEY_PROCESS_WEALTH", ())
		self.TEXT_FIN_PER_TURN = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_PER_TURN", ())
		self.TEXT_FIN_INCOME = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_INCOME", ())
		self.TEXT_FIN_UNIT_COST = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_UNITCOST", ())
		self.TEXT_FIN_UNIT_SUPPLY = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_UNITSUPPLY", ())
		self.TEXT_FIN_MAINTENANCE = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_MAINTENANCE", ())
		self.TEXT_FIN_CIVICS = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_CIVICS", ())
		self.TEXT_FIN_COST_PER_TURN = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_COST_PER_TURN", ())
		self.TEXT_FIN_EXPENSES = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_EXPENSES", ())

	def updateRuntimeLayout(self, screen):
		self.X_SCREEN, self.Y_SCREEN, self.nScreenWidth, self.nScreenHeight = getAdvisorRuntimeBounds(
			screen,
			self.W_LEFT_SPACE_FOR_COMMERCE_SLIDERS,
			self.W_RIGHT_SPACE_FOR_SCOREBOARD,
			self.H_TOP_SPACE_FOR_TECH_BAR,
			self.H_BOTTOM_SPACE
		)
		self.X_TITLE, self.X_EXIT, self.Y_EXIT, self.Y_LINK, self.Y_BOTTOM_PANEL = getAdvisorRuntimeAnchors(self.nScreenWidth, self.nScreenHeight)
		# <!-- custom: use the shared advisor shell layout (top/bottom bars + single content panel) so Domestic Advisor mirrors Victory/Info/Foreign structure instead of a floating table. (GPT-5.3-Codex) -->
		# <!-- custom: remove outer advisor-content margins so Domestic can use the full area between top/bottom bars; keep spacing only as inner table margin. (GPT-5.3-Codex) -->
		self.nMainPanelX = 0
		# <!-- custom: panel styles can leave thin Y-axis seams at the shell boundaries; use a local vertical bleed and apply it symmetrically to top/bottom. (GPT-5.3-Codex) -->
		iMainPanelYBleed = 10
		self.nMainPanelY = 55 - iMainPanelYBleed
		self.nMainPanelWidth = self.nScreenWidth - (2 * self.nMainPanelX)
		self.nMainPanelHeight = (self.Y_BOTTOM_PANEL - self.nMainPanelY) + iMainPanelYBleed
		self.nTableMargin = 8
		# <!-- custom: TABLE_STYLE_STANDARD draws the header slightly above the anchor; add a tiny visual top offset so apparent top margin matches left/right/bottom. (GPT-5.3-Codex) -->
		self.nTableTopVisualAdjust = 6
		self.nTableX = self.nMainPanelX + self.nTableMargin
		self.nTableY = self.nMainPanelY + self.nTableMargin + self.nTableTopVisualAdjust
		self.nTableWidth = self.nMainPanelWidth - (2 * self.nTableMargin)
		self.nTableHeight = self.nMainPanelHeight - (2 * self.nTableMargin) - self.nTableTopVisualAdjust
		# <!-- custom: keep specialist controls in the footer strip so the table can use symmetric margins inside the main panel. (GPT-5.3-Codex) -->
		self.nSpecialistY = self.Y_BOTTOM_PANEL + 2

	def updateRuntimeTabLinkWidths(self):
		self.PAGE_LINK_WIDTH[:] = getAdvisorRuntimeLinkWidths(CyInterface(), self.PAGE_NAME_LIST, self.TEXT_EXIT, self.X_EXIT)
		
	# Screen construction function
	def interfaceScreen(self, argsList=None):
		if argsList is not None:
			if isinstance(argsList, (list, tuple)) and len(argsList) > 0:
				if argsList[0] in [self.PAGE_OVERVIEW, self.PAGE_FINANCE]:
					self.iPage = argsList[0]
			elif argsList in [self.PAGE_OVERVIEW, self.PAGE_FINANCE]:
				self.iPage = argsList
	
		# Create a new screen, called DomesticAdvisur, using the file CvDomesticAdvisor.py for input
		screen = CyGInterfaceScreen( "DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR )
		self.updateRuntimeLayout(screen)
		self.initText()
		self.updateRuntimeTabLinkWidths()

		if screen.isActive():
			self.drawContents()
			return

		screen.setRenderInterfaceOnly(True)
		screen.setDimensions(self.X_SCREEN, self.Y_SCREEN, self.nScreenWidth, self.nScreenHeight)
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
	
		# Here we set the background widget and exit button, and we show the screen
		screen.addDrawControl("DomesticAdvisorBackground", self.ART_SCREEN_BG_OPAQUE, 0, 0, self.nScreenWidth, self.nScreenHeight, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addPanel( "DomesticTopPanel", u"", u"", True, False, 0, 0, self.nScreenWidth, 55, PanelStyles.PANEL_STYLE_TOPBAR )
		screen.addPanel( "DomesticBottomPanel", u"", u"", True, False, 0, self.Y_BOTTOM_PANEL, self.nScreenWidth, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR )
		screen.showWindowBackground(False)
		screen.setLabel("DomesticTitleHeader", "Background", self.SCREEN_TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE, self.Y_TITLE, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText("DomesticExit", "Background", self.TEXT_EXIT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.addPanel("DomesticMainPanel", "", "", True, True, self.nMainPanelX, self.nMainPanelY, self.nMainPanelWidth, self.nMainPanelHeight, PanelStyles.PANEL_STYLE_BLUE50)

		# Erase the flag?
		CyInterface().setDirty(InterfaceDirtyBits.MiscButtons_DIRTY_BIT, True)

		self.drawContents()

	def drawTabs(self):
		screen = CyGInterfaceScreen( "DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR )
		iX = 0
		for iPage in range(len(self.PAGE_NAME_LIST)):
			szLabel = self.PAGE_NAME_LIST[iPage]
			if self.iPage == iPage:
				szLabel = localText.changeTextColor(szLabel, self.COLOR_YELLOW)
			szText = SAS_FONT_TAG_TITLE + szLabel + SAS_FONT_TAG_CLOSE
			screen.setText(self.PAGE_TAB_IDS[iPage], "", szText, CvUtil.FONT_CENTER_JUSTIFY, iX + self.PAGE_LINK_WIDTH[iPage] / 2, self.Y_LINK, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, iPage, -1)
			iX += self.PAGE_LINK_WIDTH[iPage]

	def getScreen(self):
		return CyGInterfaceScreen("DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR)

	def configureFinanceLayout(self):
		iInnerMargin = self.FINANCE_INNER_MARGIN
		iColumnGap = self.FINANCE_COLUMN_GAP
		self.FIN_X_LEFT_PANEL = self.nMainPanelX + iInnerMargin
		self.FIN_PANE_WIDTH = (self.nMainPanelWidth - (2 * iInnerMargin) - (2 * iColumnGap)) / 3
		self.FIN_X_MIDDLE_PANEL = self.FIN_X_LEFT_PANEL + self.FIN_PANE_WIDTH + iColumnGap
		self.FIN_X_RIGHT_PANEL = self.FIN_X_MIDDLE_PANEL + self.FIN_PANE_WIDTH + iColumnGap
		self.FIN_Y_TOP_PANEL = self.nMainPanelY + iInnerMargin
		self.FIN_H_TOP_PANEL = self.FINANCE_TOP_PANEL_HEIGHT
		self.FIN_Y_LOCATION = self.FIN_Y_TOP_PANEL + self.FIN_H_TOP_PANEL + iInnerMargin
		self.FIN_PANE_HEIGHT = self.nMainPanelY + self.nMainPanelHeight - self.FIN_Y_LOCATION - iInnerMargin

	def getNextFinanceWidgetName(self):
		szName = self.FINANCE_WIDGET_ID + str(self.nFinanceWidgetCount)
		self.nFinanceWidgetCount += 1
		return szName

	def clearOverviewWidgets(self):
		screen = self.getScreen()
		if self.bOverviewTableCreated:
			screen.deleteWidget("CityListBackground")
			self.bOverviewTableCreated = False
		self.hideSpecialists()

	def clearFinanceWidgets(self):
		if self.nFinanceWidgetCount <= 0:
			return
		screen = self.getScreen()
		for i in range(self.nFinanceWidgetCount - 1, -1, -1):
			screen.deleteWidget(self.FINANCE_WIDGET_ID + str(i))
		self.nFinanceWidgetCount = 0

	def getOverviewHeaderLabel(self, szText):
		# <!-- custom: draw-time label wrapping for Domestic Overview table headers; this is the effective upscale point for header text. (GPT-5.3-Codex) -->
		return SAS_FONT_TAG_LABEL + szText + SAS_FONT_TAG_CLOSE
		
	# headers...
	def drawHeaders( self ):
		self.initText()

		# Get the screen and the player
		screen = CyGInterfaceScreen( "DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR )
		
		# Zoom to City
		screen.setTableColumnHeader( "CityListBackground", 0, "", (24 * self.nTableWidth) / self.nNormalizedTableWidth )
		
		# Name Column (advc.193: Font size increased; was 2.)
		screen.setTableColumnHeader( "CityListBackground", 1, self.getOverviewHeaderLabel(self.HEADER_NAME), (221 * self.nTableWidth) / self.nNormalizedTableWidth )
		
		# Population Column
		# advc.002f: Replace localText.getText("TXT_KEY_POPULATION", ()) with CITIZEN_CHAR from BULL
		screen.setTableColumnHeader( "CityListBackground", 2, self.getOverviewHeaderLabel(self.HEADER_POPULATION), (40 * self.nTableWidth) / self.nNormalizedTableWidth )
		
		# Happiness Column  advc.ctr: width was 40
		screen.setTableColumnHeader( "CityListBackground", 3, self.getOverviewHeaderLabel(self.HEADER_HAPPINESS), (33 * self.nTableWidth) / self.nNormalizedTableWidth )
		
		# Health Column  advc.ctr: width was 40
		screen.setTableColumnHeader( "CityListBackground", 4, self.getOverviewHeaderLabel(self.HEADER_HEALTH), (33 * self.nTableWidth) / self.nNormalizedTableWidth )
		
		# Food Column
		screen.setTableColumnHeader( "CityListBackground", 5, self.getOverviewHeaderLabel(self.HEADER_FOOD), (40 * self.nTableWidth) / self.nNormalizedTableWidth )
		
		# Production Column
		screen.setTableColumnHeader( "CityListBackground", 6, self.getOverviewHeaderLabel(self.HEADER_PRODUCTION), (40 * self.nTableWidth) / self.nNormalizedTableWidth )
		
		# Gold Column
		screen.setTableColumnHeader( "CityListBackground", 7, self.getOverviewHeaderLabel(self.HEADER_GOLD), (40 * self.nTableWidth) / self.nNormalizedTableWidth )
		
		# Research Column
		screen.setTableColumnHeader( "CityListBackground", 8, self.getOverviewHeaderLabel(self.HEADER_RESEARCH), (40 * self.nTableWidth) / self.nNormalizedTableWidth )
		
		# Espionage Column
		screen.setTableColumnHeader( "CityListBackground", 9, self.getOverviewHeaderLabel(self.HEADER_ESPIONAGE), (40 * self.nTableWidth) / self.nNormalizedTableWidth )
		
		# Culture Column
		screen.setTableColumnHeader( "CityListBackground", 10, self.getOverviewHeaderLabel(self.HEADER_CULTURE), (70 * self.nTableWidth) / self.nNormalizedTableWidth )
				
		# Trade Column
		screen.setTableColumnHeader( "CityListBackground", 11, self.getOverviewHeaderLabel(self.HEADER_TRADE), (35 * self.nTableWidth) / self.nNormalizedTableWidth )
				
		# Maintenance Column  advc.ctr: width was 40
		screen.setTableColumnHeader( "CityListBackground", 12, self.getOverviewHeaderLabel(self.HEADER_MAINTENANCE), (33 * self.nTableWidth) / self.nNormalizedTableWidth )
		
		# Great Person Column
		screen.setTableColumnHeader( "CityListBackground", 13, self.getOverviewHeaderLabel(self.HEADER_GREAT_PERSON), (70 * self.nTableWidth) / self.nNormalizedTableWidth )
				
		# Garrison Column
		# advc.004: Use STRENGTH_CHAR instead of DEFENSE_CHAR
		screen.setTableColumnHeader( "CityListBackground", 14, self.getOverviewHeaderLabel(self.HEADER_GARRISON), (35 * self.nTableWidth) / self.nNormalizedTableWidth )
				
		# Production Column (advc.193: Font size increased; was 2.)
		screen.setTableColumnHeader( "CityListBackground", 15, self.getOverviewHeaderLabel(self.HEADER_PRODUCING), (138 * self.nTableWidth) / self.nNormalizedTableWidth )

		# Liberate Column
		#screen.setTableColumnHeader( "CityListBackground", 16, "", (25 * self.nTableWidth) / self.nNormalizedTableWidth )
		# <advc.ctr> Liberation now shown on "Cities" tab. Instead show revolt probability.
		screen.setTableColumnHeader("CityListBackground", 16, self.getOverviewHeaderLabel(self.HEADER_REVOLT), (80 * self.nTableWidth) / self.nNormalizedTableWidth)

	# Function to draw the contents of the cityList passed in
	def drawContents (self):
		self.drawTabs()
		if self.iPage == self.PAGE_FINANCE:
			self.drawFinanceContents()
			return
		self.drawOverviewContents()

	def drawOverviewContents(self):
		self.clearFinanceWidgets()

		# Get the screen and the player
		screen = CyGInterfaceScreen( "DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR )
		player = gc.getPlayer(CyGame().getActivePlayer())
		if self.bOverviewTableCreated:
			screen.deleteWidget("CityListBackground")

		# Build the table	
		screen.addTableControlGFC( "CityListBackground", 19, self.nTableX, self.nTableY, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		self.bOverviewTableCreated = True
		screen.enableSelect( "CityListBackground", True )
		screen.enableSort( "CityListBackground" )
		screen.setStyle("CityListBackground", "Table_StandardCiv_Style")

		# Loop through the cities
		i = 0
		(pLoopCity, iter) = player.firstCity(false)
		while(pLoopCity):
			screen.appendTableRow( "CityListBackground" )
			if (pLoopCity.getName() in self.listSelectedCities):
				screen.selectRow( "CityListBackground", i, True )
			self.updateTable(pLoopCity, i)
			i += 1
			(pLoopCity, iter) = player.nextCity(iter, false)
		
		self.drawHeaders()
		
		self.drawSpecialists()
		
		self.updateAppropriateCitySelection()
		
		CyInterface().setDirty(InterfaceDirtyBits.Domestic_Advisor_DIRTY_BIT, true)

	def drawFinanceContents(self):
		self.clearOverviewWidgets()
		self.clearFinanceWidgets()
		self.configureFinanceLayout()
		self.iFinanceActiveLeader = CyGame().getActivePlayer()
		self.drawFinanceTab()
		screen = self.getScreen()
		screen.setLabel("DomesticTitleHeader", "Background", self.SCREEN_TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE, self.Y_TITLE, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def drawFinanceTab(self):
		screen = self.getScreen()
		player = gc.getPlayer(self.iFinanceActiveLeader)
		# <!-- custom: this is tab content inside Domestic Advisor; standalone EconomicsAdvisor-only chrome (separate header text, debug dropdown, own screen widgets) is intentionally not migrated. (GPT-5.3-Codex) -->

		X_LEFT_PANEL = self.FIN_X_LEFT_PANEL
		X_MIDDLE_PANEL = self.FIN_X_MIDDLE_PANEL
		X_RIGHT_PANEL = self.FIN_X_RIGHT_PANEL
		Y_TOP_PANEL = self.FIN_Y_TOP_PANEL
		H_TOP_PANEL = self.FIN_H_TOP_PANEL
		Y_LOCATION = self.FIN_Y_LOCATION
		PANE_WIDTH = self.FIN_PANE_WIDTH
		PANE_HEIGHT = self.FIN_PANE_HEIGHT
		TEXT_MARGIN = self.FINANCE_TEXT_MARGIN
		Y_SPACING = self.FINANCE_Y_SPACING
		Z_CONTROLS = self.FINANCE_Z_CONTROLS
		DZ = self.FINANCE_DZ

		# K-Mod - I've changed these costs to include inflation.
		# advc.001 (comment): CvPlayer::calculateInflatedCosts applies inflation (and rounding) only once in the end.
		# Therefore, the inflated and rounded subtotals here often don't add up correctly. Not easy to fix.
		inflationFactor = 100 + player.calculateInflationRate()
		totalUnitCost = (player.calculateUnitCost() * inflationFactor + 50) / 100
		totalUnitSupply = (player.calculateUnitSupply() * inflationFactor + 50) / 100
		totalMaintenance = (player.getTotalMaintenance() * inflationFactor + 50) / 100
		totalCivicUpkeep = (player.getCivicUpkeep([], False) * inflationFactor + 50) / 100

		totalInflatedCosts = player.calculateInflatedCosts()
		goldCommerce = player.getCommerceRate(CommerceTypes.COMMERCE_GOLD)
		gold = player.getGold()
		goldFromCivs = player.getGoldPerTurn()
		goldPerTurn = player.calculateGoldRate()

		szTreasuryPanel = self.getNextFinanceWidgetName()
		screen.addPanel(szTreasuryPanel, u"", "", True, True, X_LEFT_PANEL, Y_TOP_PANEL, X_RIGHT_PANEL + PANE_WIDTH - X_LEFT_PANEL, H_TOP_PANEL, PanelStyles.PANEL_STYLE_MAIN )
		szText = localText.getText("TXT_KEY_FINANCIAL_ADVISOR_TREASURY", (gold, )).upper()
		if gold < 0:
			if goldPerTurn != 0:
				if gold + goldPerTurn >= 0:
					szText += BugUtil.getText("TXT_KEY_MISC_POS_GOLD_PER_TURN", goldPerTurn)
				elif goldPerTurn >= 0:
					szText += BugUtil.getText("TXT_KEY_MISC_POS_WARNING_GOLD_PER_TURN", goldPerTurn)
				else:
					szText += BugUtil.getText("TXT_KEY_MISC_NEG_GOLD_PER_TURN", goldPerTurn)
		else:
			if goldPerTurn != 0:
				if goldPerTurn >= 0:
					szText += BugUtil.getText("TXT_KEY_MISC_POS_GOLD_PER_TURN", goldPerTurn)
				elif gold + goldPerTurn >= 0:
					szText += BugUtil.getText("TXT_KEY_MISC_NEG_WARNING_GOLD_PER_TURN", goldPerTurn)
				else:
					szText += BugUtil.getText("TXT_KEY_MISC_NEG_GOLD_PER_TURN", goldPerTurn)
		screen.setLabel(self.getNextFinanceWidgetName(), szTreasuryPanel, SAS_FONT_TAG_TITLE + szText + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, (X_LEFT_PANEL + PANE_WIDTH + X_RIGHT_PANEL) / 2, Y_TOP_PANEL + H_TOP_PANEL / 2 - Y_SPACING / 2, Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_HELP_FINANCE_GOLD_RESERVE, -1, -1 )

		szCommercePanel = self.getNextFinanceWidgetName()
		screen.addPanel(szCommercePanel, u"", "", True, True, X_LEFT_PANEL, Y_LOCATION, PANE_WIDTH, PANE_HEIGHT, PanelStyles.PANEL_STYLE_MAIN )
		screen.setLabel(self.getNextFinanceWidgetName(), "Background",  SAS_FONT_TAG_LABEL + self.TEXT_FIN_COMMERCE.upper() + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH / 2, Y_LOCATION + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
				
		szIncomePanel = self.getNextFinanceWidgetName()
		screen.addPanel(szIncomePanel, u"", "", True, True, X_MIDDLE_PANEL, Y_LOCATION, PANE_WIDTH, PANE_HEIGHT, PanelStyles.PANEL_STYLE_MAIN )
		screen.setLabel(self.getNextFinanceWidgetName(), "Background",  SAS_FONT_TAG_LABEL + self.TEXT_FIN_INCOME_HEADER.upper() + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH / 2, Y_LOCATION + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		
		szExpensePanel = self.getNextFinanceWidgetName()
		screen.addPanel(szExpensePanel, u"", "", True, True, X_RIGHT_PANEL, Y_LOCATION, PANE_WIDTH, PANE_HEIGHT, PanelStyles.PANEL_STYLE_MAIN )
		screen.setLabel(self.getNextFinanceWidgetName(), "Background",  SAS_FONT_TAG_LABEL + self.TEXT_FIN_EXPENSES_HEADER.upper() + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH / 2, Y_LOCATION + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		# Commerce
		yLocation = Y_LOCATION
		iCommerce = 0
		iWorkedTileCount = 0
		iWorkedTiles = 0
		bMultipliers = False # advc.004: in Bureaucracy (or sth. similar)?
		for city in PlayerUtil.playerCities(player):
			if not city.isDisorder():
				for i in range(gc.getNUM_CITY_PLOTS()):
					plot = city.getCityIndexPlot(i)
					if plot and not plot.isNone() and plot.hasYield():
						if city.isWorkingPlot(plot):
							iWorkedTileCount += 1
							iWorkedTiles += plot.getYield(YieldTypes.YIELD_COMMERCE)
				if city.getBaseYieldRateModifier(YieldTypes.YIELD_COMMERCE, 0) != 100:
					bMultipliers = True

		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + localText.getText("TXT_KEY_CONCEPT_WORKED_TILES", (iWorkedTileCount,)) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iWorkedTiles) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		iCommerce += iWorkedTiles

		iDomesticTrade, _, iForeignTrade, _ = TradeUtil.calculateTradeRoutes(player)

		# advc.086: Always show this to avoid confusion
		if TradeUtil.isFractionalTrade():
			iDomesticTrade //= 100
		yLocation += Y_SPACING
		szDomesticTrade = self.TEXT_FIN_DOMESTIC_TRADE
		# advc.086: Call it just "Trade" if there is no foreign trade to show
		if iForeignTrade <= 0:
			szDomesticTrade = self.TEXT_FIN_TRADE
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + szDomesticTrade + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_DOMESTIC_TRADE, self.iFinanceActiveLeader, 1)
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iDomesticTrade) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_DOMESTIC_TRADE, self.iFinanceActiveLeader, 1)
		iCommerce += iDomesticTrade

		if iForeignTrade > 0:
			if TradeUtil.isFractionalTrade():
				iForeignTrade //= 100
			yLocation += Y_SPACING
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_FOREIGN_TRADE + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_FOREIGN_TRADE, self.iFinanceActiveLeader, 1)
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iForeignTrade) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_FOREIGN_TRADE, self.iFinanceActiveLeader, 1)
			iCommerce += iForeignTrade

		iCorporations = 0
		for city in PlayerUtil.playerCities(player):
			if not city.isDisorder():
				iCorporations += city.getCorporationYield(YieldTypes.YIELD_COMMERCE)

		if iCorporations > 0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_CORPORATIONS + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iCorporations) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCommerce += iCorporations

		iSpecialists = 0
		for city in PlayerUtil.playerCities(player):
			if not city.isDisorder():
				for eSpec in range(gc.getNumSpecialistInfos()):
					iSpecialists += player.specialistYield(eSpec, YieldTypes.YIELD_COMMERCE) * (city.getSpecialistCount(eSpec) + city.getFreeSpecialistCount(eSpec))

		if iSpecialists > 0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_SPECIALISTS + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iSpecialists) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCommerce += iSpecialists

		# advc.001: "Current" total yield - i.e. excluding cities in disorder
		iTotalCommerce = player.calculateCurrentTotalYield(YieldTypes.YIELD_COMMERCE)
		iBuildings = iTotalCommerce - iCommerce
		if iBuildings != 0:
			yLocation += Y_SPACING
			suLabel = SAS_FONT_TAG_LABEL + self.TEXT_FIN_BUILDINGS
			if bMultipliers:
				suLabel += u", " + self.TEXT_FIN_CIVICS_MULTIPLIERS
			suLabel += SAS_FONT_TAG_CLOSE
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", suLabel, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iBuildings) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCommerce += iBuildings

		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_BUG_COMMERCE + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iCommerce) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		yLocation += 0.5 * Y_SPACING
		for iI in range(CommerceTypes.NUM_COMMERCE_TYPES):
			eCommerce = (iI + 1) % CommerceTypes.NUM_COMMERCE_TYPES
			if player.isCommerceFlexible(eCommerce):
				yLocation += Y_SPACING
				screen.setButtonGFC(self.getNextFinanceWidgetName(), u"", "", X_LEFT_PANEL + TEXT_MARGIN, int(yLocation) + TEXT_MARGIN, 20, 20, WidgetTypes.WIDGET_CHANGE_PERCENT, eCommerce, gc.getDefineINT("COMMERCE_PERCENT_CHANGE_INCREMENTS"), ButtonStyles.BUTTON_STYLE_CITY_PLUS )
				screen.setButtonGFC(self.getNextFinanceWidgetName(), u"", "", X_LEFT_PANEL + TEXT_MARGIN + 24, int(yLocation) + TEXT_MARGIN, 20, 20, WidgetTypes.WIDGET_CHANGE_PERCENT, eCommerce, -gc.getDefineINT("COMMERCE_PERCENT_CHANGE_INCREMENTS"), ButtonStyles.BUTTON_STYLE_CITY_MINUS )
				szText = SAS_FONT_TAG_LABEL + gc.getCommerceInfo(eCommerce).getDescription() + u" (" + unicode(player.getCommercePercent(eCommerce)) + u"%)" + SAS_FONT_TAG_CLOSE
				screen.setLabel(self.getNextFinanceWidgetName(), "Background",  szText, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN + 50, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
				szRate = SAS_FONT_TAG_LABEL + unicode(player.getCommerceRate(CommerceTypes(eCommerce))) + SAS_FONT_TAG_CLOSE
				screen.setLabel(self.getNextFinanceWidgetName(), "Background", szRate, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# K-Mod. Show gold rate if it hasn't been shown already
		if not player.isCommerceFlexible(CommerceTypes.COMMERCE_GOLD):
			yLocation += Y_SPACING
			szText = SAS_FONT_TAG_LABEL + gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getDescription() + u" (" + unicode(player.getCommercePercent(CommerceTypes.COMMERCE_GOLD)) + u"%)" + SAS_FONT_TAG_CLOSE
			screen.setLabel(self.getNextFinanceWidgetName(), "Background",  szText, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN + 50, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			szCommerce = SAS_FONT_TAG_LABEL + unicode(goldCommerce) + SAS_FONT_TAG_CLOSE
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", szCommerce, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# Income
		yLocation = Y_LOCATION
		iTaxRate = player.getCommercePercent(CommerceTypes.COMMERCE_GOLD)
		multipliers = []
		for eBldg in range(gc.getNumBuildingInfos()):
			info = gc.getBuildingInfo(eBldg)
			iMultiplier = info.getCommerceModifier(CommerceTypes.COMMERCE_GOLD)
			if iMultiplier > 0:
				multipliers.append([eBldg, iMultiplier, 0, 0.0])

		iBuildingCount = 0
		iHeadquartersCount = 0
		iShrinesCount = 0
		fTaxes = 0.0
		fBuildings = 0.0
		fHeadquarters = 0.0
		fShrines = 0.0
		fCorporations = 0.0
		fSpecialists = 0.0
		iWealthCount = 0
		fWealth = 0.0
		eWealth = gc.getInfoTypeForString("PROCESS_WEALTH")
		for city in PlayerUtil.playerCities(player):
			if not city.isDisorder():
				fCityTaxes = city.getYieldRate(YieldTypes.YIELD_COMMERCE) * iTaxRate / 100.0
				fTaxes += fCityTaxes
				fCityBuildings = 0.0
				fCityHeadquarters = 0.0
				fCityShrines = 0.0
				for eBldg in range(gc.getNumBuildingInfos()):
					iCount = city.getNumRealBuilding(eBldg)
					if iCount > 0:
						iBuildingGold = city.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_GOLD, eBldg)
						if iBuildingGold > 0:
							info = gc.getBuildingInfo(eBldg)
							if info.getFoundsCorporation() != -1:
								fCityHeadquarters += iBuildingGold
								iHeadquartersCount += 1
							elif info.getGlobalReligionCommerce() != -1:
								fCityShrines += iBuildingGold
								iShrinesCount += 1
							else:
								fCityBuildings += iBuildingGold
								iBuildingCount += iCount
				fBuildings += fCityBuildings
				fHeadquarters += fCityHeadquarters
				fShrines += fCityShrines
				fCityCorporations = city.getCorporationCommerce(CommerceTypes.COMMERCE_GOLD)
				fCorporations += fCityCorporations
				fCitySpecialists = city.getSpecialistCommerce(CommerceTypes.COMMERCE_GOLD)
				fSpecialists += fCitySpecialists
				fCityWealth = 0.0
				if city.isProductionProcess() and city.getProductionProcess() == eWealth:
					fCityWealth = city.getProductionToCommerceModifier(CommerceTypes.COMMERCE_GOLD) * city.getYieldRate(YieldTypes.YIELD_PRODUCTION) / 100.0
					fWealth += fCityWealth
					iWealthCount += 1
				# buildings don't multiply wealth
				fCityTotel = fCityTaxes + fCityBuildings + fCityHeadquarters + fCityCorporations + fCitySpecialists
				for entry in multipliers:
					eBldg, iMultiplier, _, _ = entry
					iCount = city.getNumRealBuilding(eBldg)
					if iCount > 0:
						entry[2] += iCount
						entry[3] += iCount * fCityTotel * iMultiplier / 100.0

		# K-Mod, karadoc
		# The 'total minus taxes' was wrong. We don't need to use that anyway
		# I've changed the 'taxes' output to use fTaxes instead of goldcommerce - totalminustaxes
		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_TAXES + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(int(fTaxes)) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		if fBuildings > 0.0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_BUILDINGS + " (%d)" % iBuildingCount + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(int(fBuildings)) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		if fHeadquarters > 0.0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_HQ + " (%d)" % iHeadquartersCount + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(int(fHeadquarters)) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		if fCorporations > 0.0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_CORPORATIONS + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(int(fCorporations)) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		if fShrines > 0.0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_SHRINES + " (%d)" % iShrinesCount + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(int(fShrines)) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		if fSpecialists > 0.0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_SPECIALISTS + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_SPECIALISTS, self.iFinanceActiveLeader, 1)
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(int(fSpecialists)) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_SPECIALISTS, self.iFinanceActiveLeader, 1)

		for eBldg, iMultiplier, iCount, fGold in multipliers:
			if iCount > 0 and fGold > 0.0:
				fAverage = fGold / iCount
				szDescription = gc.getBuildingInfo(eBldg).getDescription() + u" " + localText.getText("TXT_KEY_BUG_FINANCIAL_ADVISOR_BUILDING_COUNT_AVERAGE", (iCount, BugUtil.formatFloat(fAverage, 2)))
				yLocation += Y_SPACING
				screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + szDescription + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
				screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(int(fGold)) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		if fWealth > 0.0 and iWealthCount > 0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_WEALTH + " (%d)" % iWealthCount + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(int(fWealth)) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		iIncome = goldCommerce
		if goldFromCivs > 0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_PER_TURN + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_FOREIGN_INCOME, self.iFinanceActiveLeader, 1)
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(goldFromCivs) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_FOREIGN_INCOME, self.iFinanceActiveLeader, 1)
			iIncome += goldFromCivs

		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_INCOME + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iIncome) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		# Expenses
		yLocation = Y_LOCATION
		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_UNIT_COST + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_RIGHT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_UNIT_COST, self.iFinanceActiveLeader, 1)
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(totalUnitCost) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_UNIT_COST, self.iFinanceActiveLeader, 1)
		yLocation += Y_SPACING
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_UNIT_SUPPLY + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_RIGHT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_AWAY_SUPPLY, self.iFinanceActiveLeader, 1)
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(totalUnitSupply) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_AWAY_SUPPLY, self.iFinanceActiveLeader, 1)
		yLocation += Y_SPACING
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_MAINTENANCE + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_RIGHT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_CITY_MAINT, self.iFinanceActiveLeader, 1)
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(totalMaintenance) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_CITY_MAINT, self.iFinanceActiveLeader, 1)
		yLocation += Y_SPACING
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_CIVICS + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_RIGHT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_CIVIC_UPKEEP, self.iFinanceActiveLeader, 1)
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(totalCivicUpkeep) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_CIVIC_UPKEEP, self.iFinanceActiveLeader, 1)

		if goldFromCivs < 0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_COST_PER_TURN + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_RIGHT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_FOREIGN_INCOME, self.iFinanceActiveLeader, 1)
			screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(-goldFromCivs) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_FOREIGN_INCOME, self.iFinanceActiveLeader, 1)

		# advc: Unmarked K-Mod 1.45 change; inflation now already included
		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_FIN_EXPENSES + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_RIGHT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.setLabel(self.getNextFinanceWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(totalInflatedCosts) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, Z_CONTROLS + DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_FINANCE_INFLATED_COSTS, self.iFinanceActiveLeader, 1 )

	def updateTable(self, pLoopCity, i):

		screen = CyGInterfaceScreen( "DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR )

		screen.setTableText( "CityListBackground", 0, i, "", self.ART_CITY_SELECTION_BUTTON, WidgetTypes.WIDGET_ZOOM_CITY, pLoopCity.getOwner(), pLoopCity.getID(), CvUtil.FONT_LEFT_JUSTIFY)

		# <advc.193>
		# <!-- custom: preserve base AdvCiv per-row font-tag caching (one tag reused for all cells in this row update),
		# but source size from LABEL (not BODY) in AdvCiv-SAS for readability. (GPT-5.3-Codex) -->
		iCellFontSize = getSASUIFontLabel()
		# (Uses of these tags in the code below aren't tagged w/ comments)
		szFontTagOpen = u"<font=" + unicode(iCellFontSize) + u">"
		szFontTagClose = SAS_FONT_TAG_CLOSE
		# </advc.193>

		szName = pLoopCity.getName()
		if pLoopCity.isCapital():
			szName += (u"%c" % CyGame().getSymbolID(FontSymbols.STAR_CHAR))
		elif pLoopCity.isGovernmentCenter():
			szName += (u"%c" % CyGame().getSymbolID(FontSymbols.SILVER_STAR_CHAR))
		
		for iReligion in range(gc.getNumReligionInfos()):
			if pLoopCity.isHasReligion(iReligion):
				if pLoopCity.isHolyCityByType(iReligion):
					szName += (u"%c" % gc.getReligionInfo(iReligion).getHolyCityChar())
				else:
					szName += (u"%c" % gc.getReligionInfo(iReligion).getChar())
						
		for iCorporation in range(gc.getNumCorporationInfos()):
			if pLoopCity.isHeadquartersByType(iCorporation):
				szName += (u"%c" % gc.getCorporationInfo(iCorporation).getHeadquarterChar())
			elif pLoopCity.isActiveCorporation(iCorporation):
				szName += (u"%c" % gc.getCorporationInfo(iCorporation).getChar())
					
		# City name...
		screen.setTableText( "CityListBackground", 1, i, szFontTagOpen + szName + szFontTagClose, "",
				#WidgetTypes.WIDGET_GENERAL, -1, -1,
				# advc.186b: BULL attaches this to the zoom button. I like it better on the city name b/c, that way, it doesn't obscure the button that the player may want to click.
				WidgetTypes.WIDGET_EXAMINE_CITY, pLoopCity.getOwner(), pLoopCity.getID(),
				CvUtil.FONT_LEFT_JUSTIFY )
		
		# Population
		screen.setTableInt( "CityListBackground", 2, i, szFontTagOpen + unicode(pLoopCity.getPopulation()) + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		# Happiness...
		iNetHappy = pLoopCity.happyLevel() - pLoopCity.unhappyLevel(0)
		szText = unicode(iNetHappy)
		if iNetHappy > 0:
			szText = self.COLOR_POSITIVE_PREFIX + szText + self.COLOR_REVERT_SUFFIX
		elif iNetHappy < 0:
			szText = self.COLOR_NEGATIVE_PREFIX + szText + self.COLOR_REVERT_SUFFIX
		screen.setTableInt( "CityListBackground", 3, i, szFontTagOpen + szText + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		# Health...
		iNetHealth = pLoopCity.goodHealth() - pLoopCity.badHealth(0)
		szText = unicode(iNetHealth)
		if iNetHealth > 0:
			szText = self.COLOR_POSITIVE_PREFIX + szText + self.COLOR_REVERT_SUFFIX
		elif iNetHealth < 0:
			szText = self.COLOR_NEGATIVE_PREFIX + szText + self.COLOR_REVERT_SUFFIX
		screen.setTableInt( "CityListBackground", 4, i, szFontTagOpen + szText + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		# Food status...
		iNetFood = pLoopCity.foodDifference(true)
		szText = unicode(iNetFood)
		if iNetFood > 0:
			szText = self.COLOR_POSITIVE_PREFIX + szText + self.COLOR_REVERT_SUFFIX
		elif iNetFood < 0:
			szText = self.COLOR_NEGATIVE_PREFIX + szText + self.COLOR_REVERT_SUFFIX
		screen.setTableInt( "CityListBackground", 5, i, szFontTagOpen + szText + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
		
		# Production status...
		screen.setTableInt( "CityListBackground", 6, i, szFontTagOpen+ unicode(pLoopCity.getYieldRate(YieldTypes.YIELD_PRODUCTION)) + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		# Gold status...
		screen.setTableInt( "CityListBackground", 7, i, szFontTagOpen + unicode(pLoopCity.getCommerceRate(CommerceTypes.COMMERCE_GOLD)) + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		# Science rate...
		screen.setTableInt( "CityListBackground", 8, i, szFontTagOpen + unicode(pLoopCity.getCommerceRate(CommerceTypes.COMMERCE_RESEARCH)) + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		# Espionage rate...
		screen.setTableInt( "CityListBackground", 9, i, szFontTagOpen + unicode(pLoopCity.getCommerceRate(CommerceTypes.COMMERCE_ESPIONAGE)) + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		# Culture status...
		szCulture = unicode(pLoopCity.getCommerceRate(CommerceTypes.COMMERCE_CULTURE))
		iCultureTimes100 = pLoopCity.getCultureTimes100(CyGame().getActivePlayer())
		iCultureRateTimes100 = pLoopCity.getCommerceRateTimes100(CommerceTypes.COMMERCE_CULTURE)
		if iCultureRateTimes100 > 0:
			iCultureLeftTimes100 = 100 * pLoopCity.getCultureThreshold() - iCultureTimes100
			if iCultureLeftTimes100 > 0:
				szCulture += u" (" + unicode((iCultureLeftTimes100  + iCultureRateTimes100 - 1) / iCultureRateTimes100) + u")"

		screen.setTableInt( "CityListBackground", 10, i, szFontTagOpen + szCulture + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		# Trade
		screen.setTableInt( "CityListBackground", 11, i, szFontTagOpen + unicode(pLoopCity.getTradeYield(YieldTypes.YIELD_COMMERCE)) + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		# Maintenance...
		#iMaintenance = pLoopCity.getMaintenance()
		# advc.004: Based on K-Mod code in CvMainInterface.py
		iMaintenance = pLoopCity.getMaintenanceTimes100() * (100+gc.getPlayer(pLoopCity.getOwner()).calculateInflationRate()) // 10000
		screen.setTableInt( "CityListBackground", 12, i, szFontTagOpen + unicode(iMaintenance) + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		# Great Person
		iGreatPersonRate = pLoopCity.getGreatPeopleRate()
		szGreatPerson = unicode(iGreatPersonRate)
		if iGreatPersonRate > 0:
			iGPPLeft = gc.getPlayer(gc.getGame().getActivePlayer()).greatPeopleThreshold(false) - pLoopCity.getGreatPeopleProgress()
			if iGPPLeft > 0:
				iTurnsLeft = iGPPLeft / pLoopCity.getGreatPeopleRate()
				if iTurnsLeft * pLoopCity.getGreatPeopleRate() <  iGPPLeft:
					iTurnsLeft += 1
				szGreatPerson += u" (" + unicode(iTurnsLeft) + u")"
		
		screen.setTableInt( "CityListBackground", 13, i, szFontTagOpen + szGreatPerson + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
		
		# Garrison
		screen.setTableInt( "CityListBackground", 14, i, szFontTagOpen + unicode(pLoopCity.plot().getNumDefenders(pLoopCity.getOwner())) + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

		# Producing
		szProducing = pLoopCity.getProductionName()
		iProductionTurns = pLoopCity.getGeneralProductionTurnsLeft()
		if iProductionTurns > 0: # advc.004x
			szProducing += " (" + str(iProductionTurns) + ")"

		# <!-- custom: also show the button of the current thing we are building. Credit: Gemini 3 Pro. (GPT-5.2-Codex (summarized)) -->
		# add the button (icon) to the "Producing" column.
		# Get the button art for the current item
		szButton = ""
		iWidget = WidgetTypes.WIDGET_GENERAL
		iData1 = -1
		iData2 = -1

		if pLoopCity.isProductionUnit():
			iUnit = pLoopCity.getProductionUnit()
			szButton = gc.getUnitInfo(iUnit).getButton()
			iWidget = WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT
			iData1 = iUnit
		elif pLoopCity.isProductionBuilding():
			iBuilding = pLoopCity.getProductionBuilding()
			szButton = gc.getBuildingInfo(iBuilding).getButton()
			iWidget = WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING
			iData1 = iBuilding
		elif pLoopCity.isProductionProject():
			iProject = pLoopCity.getProductionProject()
			szButton = gc.getProjectInfo(iProject).getButton()
			iWidget = WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT
			iData1 = iProject
		elif pLoopCity.isProductionProcess():
			iProcess = pLoopCity.getProductionProcess()
			szButton = gc.getProcessInfo(iProcess).getButton()

		# Pass szButton as the 5th argument to display the icon next to the text
		#screen.setTableText( "CityListBackground", 15, i, szFontTagOpen + szProducing + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
		screen.setTableText( "CityListBackground", 15, i, szFontTagOpen + szProducing + szFontTagClose, szButton, iWidget, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY )
		# End - add the button (icon) to the "Producing" column.

		# Liberation
		# advc.004: Mark potential independent colonies too (bCanSplit check added to the two conditions below)
		#bCanSplit = gc.getPlayer(gc.getGame().getActivePlayer()).canSplitArea(pLoopCity.area().getID())
		#if bCanSplit or pLoopCity.getLiberationPlayer(false) != -1:
			# UNOFFICIAL_PATCH begin
		#	if bCanSplit or not gc.getTeam(gc.getPlayer(pLoopCity.getLiberationPlayer(false)).getTeam()).isAtWar(CyGame().getActiveTeam()) :
		#		screen.setTableText( "CityListBackground", 16, i, SAS_FONT_TAG_BODY + (u"%c" % CyGame().getSymbolID(FontSymbols.OCCUPATION_CHAR)) + SAS_FONT_TAG_CLOSE, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
			# UNOFFICIAL_PATCH end
		# <advc.ctr> Replace this column with revolt probability
		revoltPr = pLoopCity.revoltProbability()
		if revoltPr > 0:
			revoltPr = max(revoltPr, 0.001) # Show all near-0 values as "0.1%"
			szRevoltPr = ("%.1f" % (100 * revoltPr)) + "%"
			szColorTag = "COLOR_NEGATIVE_TEXT"
			if not pLoopCity.canCultureFlip():
				szColorTag = "COLOR_YIELD_FOOD"
			szRevoltPr = localText.changeTextColor(szRevoltPr, gc.getInfoTypeForString(szColorTag))
			screen.setTableText("CityListBackground", 16, i, szFontTagOpen + szRevoltPr + szFontTagClose, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		# </advc.ctr>
		
	# Draw the specialist and their increase and decrease buttons
	def drawSpecialists(self):
		screen = CyGInterfaceScreen( "DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR )

		for i in range( gc.getNumSpecialistInfos() ):
			if (gc.getSpecialistInfo(i).isVisible()):			
				szName = "SpecialistImage" + str(i)
				screen.setImageButton( szName, gc.getSpecialistInfo(i).getTexture(), self.nFirstSpecialistX + (self.nSpecialistDistance * i), self.nSpecialistY, self.nSpecialistWidth, self.nSpecialistLength, WidgetTypes.WIDGET_CITIZEN, i, -1 )
				screen.hide(szName)

				szName = "SpecialistPlus" + str(i)
				screen.setButtonGFC( szName, u"", "", self.nFirstSpecialistX + (self.nSpecialistDistance * i) + self.nPlusOffsetX, self.nSpecialistY + self.nPlusOffsetY, self.nPlusWidth, self.nPlusHeight, WidgetTypes.WIDGET_CHANGE_SPECIALIST, i, 1, ButtonStyles.BUTTON_STYLE_CITY_PLUS )
				screen.hide(szName)

				szName = "SpecialistMinus" + str(i)
				screen.setButtonGFC( szName, u"", "", self.nFirstSpecialistX + (self.nSpecialistDistance * i) + self.nMinusOffsetX, self.nSpecialistY + self.nMinusOffsetY, self.nMinusWidth, self.nMinusHeight, WidgetTypes.WIDGET_CHANGE_SPECIALIST, i, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS )
				screen.hide(szName)

				szName = "SpecialistText" + str(i)
				screen.setLabel(szName, "Background", "", CvUtil.FONT_LEFT_JUSTIFY, self.nFirstSpecialistX + (self.nSpecialistDistance * i) + self.nSpecTextOffsetX, self.nSpecialistY + self.nSpecTextOffsetY, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				screen.hide(szName)

	def hideSpecialists(self):
		screen = CyGInterfaceScreen( "DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR )
		for i in range( gc.getNumSpecialistInfos() ):
			if (gc.getSpecialistInfo(i).isVisible()):			
				screen.hide("SpecialistImage" + str(i))
				screen.hide("SpecialistPlus" + str(i))
				screen.hide("SpecialistMinus" + str(i))
				screen.hide("SpecialistText" + str(i))
				
	def updateSpecialists(self):
		# Function which shows the specialists.
		#
		screen = CyGInterfaceScreen( "DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR )

		if (CyInterface().isOneCitySelected()):
		
			city = CyInterface().getHeadSelectedCity()
			nPopulation = city.getPopulation()
			nFreeSpecial = city.totalFreeSpecialists()

			for i in range( gc.getNumSpecialistInfos() ):
				if (gc.getSpecialistInfo(i).isVisible()):	
					szName = "SpecialistImage" + str(i)
					screen.show(szName)
					
					szName = "SpecialistText" + str(i)
					screen.setLabel(szName, "Background", str (city.getSpecialistCount(i)) + "/" + str(city.getMaxSpecialistCount(i)), CvUtil.FONT_LEFT_JUSTIFY, self.nFirstSpecialistX + (self.nSpecialistDistance * i) + self.nSpecTextOffsetX, self.nSpecialistY + self.nSpecTextOffsetY, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
					screen.show(szName)

					# If the specialist is valid and we can increase it
					szName = "SpecialistPlus" + str(i)
					if (city.isSpecialistValid(i, 1) and (city.getForceSpecialistCount(i) < (nPopulation + nFreeSpecial))):
						screen.show(szName)
					else:
						screen.hide(szName)

					# if we HAVE specialists already and they're not forced.
					szName = "SpecialistMinus" + str(i)
					if (city.getSpecialistCount(i) > 0 or city.getForceSpecialistCount(i) > 0):
						screen.show(szName)
					else:
						screen.hide(szName)
		else:
			self.hideSpecialists()
				
	# Will handle the input for this screen...
	def handleInput (self, inputClass):
		# Calls function mapped in DomesticAdvisorInputMap
		#
		# only get from the map if it has the key
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and inputClass.getButtonType() == WidgetTypes.WIDGET_GENERAL:
			iData1 = inputClass.getData1()
			if iData1 in [self.PAGE_OVERVIEW, self.PAGE_FINANCE] and iData1 != self.iPage:
				self.iPage = iData1
				self.drawContents()
				return 1
		if self.iPage == self.PAGE_FINANCE and inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and inputClass.getButtonType() == WidgetTypes.WIDGET_CHANGE_PERCENT:
			self.drawFinanceContents()
			return 1
		
		if ( inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED ):
			if self.iPage != self.PAGE_OVERVIEW:
				return 0
			if (inputClass.getMouseX() == 0):
				screen = CyGInterfaceScreen( "DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR )
				screen.hideScreen()
				
				CyInterface().selectCity(gc.getPlayer(inputClass.getData1()).getCity(inputClass.getData2()), true)
				
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
				popupInfo.setText(u"showDomesticAdvisor")
				popupInfo.addPopup(inputClass.getData1())		
			else:
				self.updateAppropriateCitySelection()
				self.updateSpecialists()
		return 0
	
	def updateAppropriateCitySelection(self):
		if self.iPage != self.PAGE_OVERVIEW:
			return
		nCities = gc.getPlayer(gc.getGame().getActivePlayer()).getNumCities()
		screen = CyGInterfaceScreen( "DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR )
		screen.updateAppropriateCitySelection( "CityListBackground", nCities, 1 )
		self.listSelectedCities = []
		for i in range(nCities):
			if screen.isRowSelected("CityListBackground", i):
				self.listSelectedCities.append(screen.getTableText("CityListBackground", 2, i))
								
	def update(self, fDelta):
		if self.iPage == self.PAGE_FINANCE:
			if (CyInterface().isDirty(InterfaceDirtyBits.Financial_Screen_DIRTY_BIT)):
				CyInterface().setDirty(InterfaceDirtyBits.Financial_Screen_DIRTY_BIT, False)
				self.drawFinanceContents()
			return

		if (CyInterface().isDirty(InterfaceDirtyBits.Domestic_Advisor_DIRTY_BIT)):
			CyInterface().setDirty(InterfaceDirtyBits.Domestic_Advisor_DIRTY_BIT, False)
			
			screen = CyGInterfaceScreen( "DomesticAdvisor", CvScreenEnums.DOMESTIC_ADVISOR )
			player = gc.getPlayer(CyGame().getActivePlayer())

			i = 0
			(pLoopCity, iter) = player.firstCity(false)
			while(pLoopCity):
				self.updateTable(pLoopCity, i)
				i += 1
				(pLoopCity, iter) = player.nextCity(iter, false)
			
			self.updateSpecialists()
		
		return

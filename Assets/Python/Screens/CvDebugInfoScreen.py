## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Copied from vanilla Civ4's C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Assets\Python\Screens\CvDebugInfoScreen.py (only vanilla Civ4 ships it), the copy SAS ran before (2026-11-22). See KI#1104. (Claude code Opus 5.5) -->
from CvPythonExtensions import *
import CvUtil
# <!-- custom: Interface and movie art paths come from SASVisualUtils' shared cache, as python_resource_api.py asks of every SAS file, which this base-game copy became (KI#1104).
# BugEventManager already loads SASVisualUtils before CvScreensInterface and these screens, as the startup log shows, so this adds no import earlier than before. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
import SASVisualUtils as SASVisuals
import PyHelpers
import ScreenInput
import CvScreenEnums
import CvMapGeneratorUtil
import CvGFCScreen
# <!-- custom: The shared advisor layout (getAdvisorRuntimeBounds and its anchors, the maximized table, the scoreboard's space at the current font) sizes this screen to the resolution, as the other advisors do; SASTextScale gives that font. See KI#1105.2. (Claude code Opus 5.5) -->
from SASUtils import *
import SASTextScale

PyPlayer = PyHelpers.PyPlayer

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()

list_Widget = []
g_iLastScreen = 0

class CvDebugInfoScreen(CvGFCScreen.CvGFCScreen):
	'Debug Information Screen'

	# <!-- custom: Leaves the scoreboard the space getAdvisorScoreboardSpace gives, as the advisors do, so CvScreensInterface shortens leader names beside it. See KI#1105.2. (Claude code Opus 5.5) -->
	SAS_LEAVES_SCOREBOARD_SPACE = True

	def __init__(self):
		self.setScreenValues("DebugInfoScreen", CvScreenEnums.DEBUG_INFO_SCREEN)
		
		self.DebugInfoMap = {
			0 : { 'DESC': "Team Relations", 'DATA': self.drawTeamRelations },
			1 : { 'DESC': "Player Attitudes", 'DATA': self.drawPlayerAttitudes },
			2 : { 'DESC': "Civic Info", 'DATA': self.drawPlayerCivics },
			3 : { 'DESC': "Civ Info", 'DATA': self.drawPlayerOverviewInfo },
			4 : { 'DESC': "AI Types", 'DATA': self.drawPlayerUnitAITypes },
			5 : { 'DESC': "Available Bonuses", 'DATA': self.drawPlayerAvailableResources },
			6 : { 'DESC': "Map Details", 'DATA': self.generateBonusDistributionList },
		}
		self.CivInfoItems = ["Power", "Assets","Gold Reserve", "Gold Commerce", "Research Rate", "Total Maintenance", "Civic Upkeep", "Unit Cost", "Unit Supply", "# Cities", "# Units", "# Citizens", "# Plots", "Current Tech"]

		self.WIDGET_ID = "DebugInfoScreenWidget"
		self.nWidgetCount = 0

		self.szDebugInfoPulldownID = "DebugInfoScreenSelectType"
		# <!-- custom: Column paging of the table; see drawPageArrows. See KI#1105.2. (Claude code Opus 5.5) -->
		self.iPage = 0
		self.iNumPages = 1
		self.szPageLeftID = ""
		self.szPageRightID = ""
		self.bTeam = false
		self.bAttitude = false
		self.iNumPlayers = -1
		self.iNumTeams = -1

		# <!-- custom: Vanilla's fixed positions are gone: TITLE_TEXT_X/Y (502, 8), EXIT_TEXT_X/Y (502, 12), DROPDOWN_INFOTYPE_X/Y (405, 47) and TABLE_START_X/Y (30, 70) gave way to the advisors' runtime anchors in interfaceScreen, and W_CHART/H_CHART (800 x 400) were never read; only the depths remain. See KI#1105.2. (Claude code Opus 5.5) -->
		self.TITLE_TEXT_Z = -2.5
		self.EXIT_TEXT_Z = -2.6

	def interfaceScreen(self):
		' Create the screen '
		global g_iLastScreen
		screen = self.getScreen()
		# <!-- custom: Was a fixed 1024 x 768 background with a 1000 x 580 table at (0, 100), from vanilla, which left most of a 1920 x 1080 screen to the map and cut Map Details after about 13 columns (2026-11-23).
		# Now sized like the advisors: the area left of the scoreboard and below the tech bar, top and bottom bars, title and exit at the shared anchors, and the table filling the space between the bars. See KI#1105.2. (Claude code Opus 5.5) -->
		self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN = getAdvisorRuntimeBounds(screen, SAS_ADVISOR_LEFT_SPACE_FOR_COMMERCE_SLIDERS, getAdvisorScoreboardSpace(screen.getXResolution(), SASTextScale.getSASUIFontLabel()), SAS_ADVISOR_TOP_SPACE_FOR_TECH_BAR, SAS_ADVISOR_BOTTOM_SPACE)
		iXTitle, iXExit, iYExit, iYLink, iYBottomPanel = getAdvisorRuntimeAnchors(self.W_SCREEN, self.H_SCREEN)
		_, self.TABLE_RECT = getAdvisorMaximizedPanelLayout(self.W_SCREEN, iYBottomPanel)
		self.Y_BOTTOM_PANEL = iYBottomPanel
		screen.setRenderInterfaceOnly(True)
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
		screen.addDDSGFC("DebugInfoScreen", SASVisuals.InterfaceArt.getPath("SCREEN_BG_OPAQUE"), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPanel("DebugInfoTopPanel", u"", u"", True, False, 0, 0, self.W_SCREEN, SAS_ADVISOR_BOTTOM_PANEL_Y_OFFSET, PanelStyles.PANEL_STYLE_TOPBAR)
		screen.addPanel("DebugInfoBottomPanel", u"", u"", True, False, 0, iYBottomPanel, self.W_SCREEN, self.H_SCREEN - iYBottomPanel, PanelStyles.PANEL_STYLE_BOTTOMBAR)
		screen.showWindowBackground(False)
		screen.setDimensions(self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN)

		# <!-- custom: Was setExitText(u"EXIT SCREEN", ...) at (502, 12); at the advisors' exit anchor it drew from x rightward, ignoring FONT_RIGHT_JUSTIFY, so the screen's right edge cut it to "EX" (2026-11-23).
		# Now the advisors' close text, right-justified with WIDGET_CLOSE_SCREEN at the shared font scale. See KI#1105.2. (Claude code Opus 5.5) -->
		screen.setText("DebugInfoExit", "Background", SASTextScale.sasFontTagTitle + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + SASTextScale.SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, iXExit, iYExit, self.EXIT_TEXT_Z, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1)

		# Header...
		# <!-- custom: The title takes the shared font scale, as the exit text and the advisors' titles do. See KI#1105.2. (Claude code Opus 5.5) -->
		screen.setText( "DebugInfoTitleHeader", "Background", SASTextScale.sasFontTagTitle + u"DEBUG INFO" + SASTextScale.SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, iXTitle, SAS_ADVISOR_TITLE_Y, self.TITLE_TEXT_Z, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		# Create Drop Down so the user can select the screen they want
		# <!-- custom: Was at (405, 47), under the title; now at the top left, where the advisors put their debug dropdown, so the table starts right under the top bar. See KI#1105.2. (Claude code Opus 5.5) -->
		screen.addDropDownBoxGFC(self.szDebugInfoPulldownID, 22, 12, 300, WidgetTypes.WIDGET_GENERAL, -1, -1,FontTypes.GAME_FONT )
		
		# adds the screen names to the drop down using the DebugInfoMap - always selects the last one that was selected
		bSelected = false
		
		for i in range(len(self.DebugInfoMap)):
			if i == g_iLastScreen:
				bSelected = true
			
			strInfoName = self.DebugInfoMap[i].get('DESC')
			
			screen.addPullDownString( self.szDebugInfoPulldownID, strInfoName, i, -1, bSelected )
			bSelected = false
		#draw the contents with the last selected screen
		self.drawContents(g_iLastScreen)

	def drawContents(self, iInfoType = 0):
		'Based on dropdown selection the screen will draw the appropriate info screen'
		global g_iLastScreen
		g_iLastScreen = iInfoType
		
		entry = self.DebugInfoMap.get(iInfoType)
		entry.get('DATA')()
			
	def drawTeamRelations(self):
		' draws a table showing the relations of teams '
		#CvUtil.pyPrint('CvDebugInfoScreen->drawTeamRelations')
		d_TableData = {}
		d_TableData[0] = self.setTeams()
		
		strBuffer = ""
		iconName = "Error"
		entry = "None"
		list_loopRowData = []
		
		for x in range(self.iNumTeams):
			
			strBuffer = gc.getTeam(x).getName()
			list_loopRowData.append(strBuffer)
			strBuffer = ""
			
			for y in range(self.iNumTeams):
				pTeamX = gc.getTeam(x)
				pTeamY = gc.getTeam(y)
								
				# if the same team
				if ( not x == y ):
					
					# if teams have met
					if pTeamX.isHasMet(y):
					
						# if at peace
						if not pTeamX.isAtWar(y):
						
							# if open borders
							if pTeamX.isDefensivePact(y):
								strBuffer = "DefensivePact"
							
							# if open borders
							elif pTeamX.isOpenBorders(y):
								strBuffer = "OpenBorders"
							
							# else use peace icon
							else:
								strBuffer = "Peace"
								
						# else indicate at War
						else:
							strBuffer = "War"
					
					# else they have not met
					else:
						strBuffer = "NotMet"
				
				# else use ally icon
				else:
					strBuffer = "Team"
				
				list_loopRowData.append(strBuffer)
			
			d_TableData[x+1] = list_loopRowData
			list_loopRowData = []
		
		# add data to table
		self.setTableData(d_TableData)

		return 0
	
	def drawPlayerAttitudes(self):
		' draws a table showing the attitudes between players '
		#CvUtil.pyPrint('CvDebugInfoScreen->drawPlayerAttitudes')
		self.bAttitude = True
		d_TableData = {}
		d_TableData[0] = self.setPlayers()
		
		strBuffer = ""
		iconName = "None"
		list_loopRowData = []
		
		for x in range(self.iNumPlayers):
			
			strBuffer = gc.getPlayer(x).getName()
			list_loopRowData.append(strBuffer)
			strBuffer = ""
			
			for y in range(self.iNumPlayers):
				pPlayerX = gc.getPlayer(x)
				pPlayerY = gc.getPlayer(y)
				
				pTeamX = gc.getTeam(pPlayerX.getTeam())
				pTeamY = gc.getTeam(pPlayerY.getTeam())
				
				# if the same Player
				if ( not x == y ):
					
					# if teams have met
					if pTeamX.isHasMet(y):
					
						iPlayerXAttitudeTowardPlayerY = pPlayerX.AI_getAttitude(y)
												
						strBuffer = "%s" %(gc.getAttitudeInfo(iPlayerXAttitudeTowardPlayerY).getDescription(),)
						list_loopRowData.append(strBuffer)
						strBuffer = ""
						continue # prevents the value from getting overwritten by a font icon
					
					# else they have not met
					else:
						strBuffer = "NotMet"
						
				# else use ally icon
				else:
					strBuffer = "Ally"
				
				list_loopRowData.append(strBuffer)
				strBuffer = ""
			
			d_TableData[x+1] = list_loopRowData
			list_loopRowData = []
		
		# add data to table
		self.setTableData(d_TableData)
		
		return 0
	
	def drawPlayerCivics(self):
		d_TableData = {}
		strName = ""
		list_loopRowData = []
		
		d_TableData[0] = self.setPlayers("Civics")	
		
		for i in range( gc.getNumCivicOptionInfos() ):
			strName = gc.getCivicOptionInfo(i).getDescription()
			list_loopRowData.append(strName)
			
			for j in range( self.iNumPlayers ):
				strName = gc.getCivicInfo( int(gc.getPlayer(j).getCivics(i)) ).getDescription()
				list_loopRowData.append(strName)
			
			d_TableData[i+1] = list_loopRowData
			list_loopRowData = []
		
		self.setTableData(d_TableData)
		
		return 0
	
	def drawPlayerOverviewInfo(self):
		d_TableData = {}
		strName = ""
		list_loopRowData = []
		
		d_TableData[0] = self.setPlayers("Civ Info")
		
		for i in range( len(self.CivInfoItems) ):
			strName = self.CivInfoItems[i]
			list_loopRowData.append(strName)
			
			for j in range( self.iNumPlayers ):
				player = PyPlayer(j)
				pPlayer = gc.getPlayer(j)
				
				CivInfoFnx = [pPlayer.getPower(),pPlayer.getAssets(),player.getGold(), player.getGoldCommerceRate(), player.calculateResearchRate(), player.getTotalMaintenance(),
					player.getCivicUpkeep(), player.calculateUnitCost(), player.calculateUnitSupply(), player.getNumCities(),
					player.getNumUnits(), player.getTotalPopulation(), player.getTotalLand(), player.getCurrentTechName()]

				strName = str(CivInfoFnx[i])
				list_loopRowData.append(strName)
			
			d_TableData[i+1] = list_loopRowData
			list_loopRowData = []
		
		self.setTableData(d_TableData)
		
		return 0
	
	def drawPlayerUnitAITypes(self):
		self.TITLE_X = 200
		self.COLUMN_X = 75
		
		d_TableData = {}
		strName = ""
		list_loopRowData = []
		
		d_TableData[0] = self.setPlayers("Unit AI")
		
		for i in range( UnitAITypes.NUM_UNITAI_TYPES ):
			strName = gc.getUnitAIInfo(i).getDescription()
			strName.strip("UNITAI_")
			list_loopRowData.append(strName)
			
			for j in range( self.iNumPlayers ):		
				strName = "%s" %( int(gc.getPlayer(j).AI_getNumAIUnits(i)), )
				list_loopRowData.append(strName)
			
			d_TableData[i+1] = list_loopRowData
			list_loopRowData = []
		
		self.setTableData(d_TableData)
		
		return 0
		
	def drawPlayerAvailableResources(self):
		' Draws a table showing how many of each resource the player can trade '
		d_TableData = {}
		list_loopRowData = []
		
		d_TableData[0] = self.setPlayers("Available Bonuses")
		
		for i in range( gc.getNumBonusInfos() ):
			list_loopRowData.append(gc.getBonusInfo(i).getDescription())
			
			for j in range( self.iNumPlayers ):
				list_loopRowData.append( int(gc.getPlayer(j).getNumAvailableBonuses(i)) )
			d_TableData[i+1] = list_loopRowData
			list_loopRowData = []

		self.setTableData(d_TableData)
		
		return 0

	def generateBonusDistributionList(self):
		"Displays Bonus Advisor Popup"
		d_TableData = {}
		
		map = CyMap()
	
		areas = CvMapGeneratorUtil.getAreas()
		area_sizes = [(area.getNumTiles(), area) for area in areas]
		area_sizes.sort() # sort by size -- biggest area last
		area_sizes.reverse() # biggest area first
		areas = [area for (area_size, area) in area_sizes]

		bonus_infos = [gc.getBonusInfo(i) for i in range(gc.getNumBonusInfos())]
		# <!-- custom: Was [u"BonusDistro"] + [u"Area"] + [u"Size"] ..., one header more than each row has values, so every value after the area ID sat one header to its left: a Huge Water map's main continent showed its 1505 tiles under "Area" (2026-11-23).
		# Dropped "Area": "BonusDistro" now titles the area IDs in column 0, as the screen's other tabs put their title over their row labels, and the in-game table lined up. See KI#1105. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		title_list = [u"BonusDistro"] + [u"Size"] + [u"Starting Plots"] + [u"Unique Bonus Types"] + [u"Total Bonuses"]
		
		bonusList = ""
		for bonus in bonus_infos:
			bonusList += bonus.getDescription()[0]
		title_list += bonusList

		d_TableData[0] = title_list
		
		total = 0
		loopRowData = []
		for i in range(len(areas)):
			area = areas[i]
			area_string = "%d" % area.getID()
			if area.isWater():
				area_string = "w" + area_string
				
			loopRowData.append(area_string)
			loopRowData.append("%d" % area.getNumTiles())
			start_plots = area.getNumStartingPlots()
			if start_plots > 0:
				loopRowData.append("%d" % start_plots)
			else:
				loopRowData.append("")
			num_unique = area.countNumUniqueBonusTypes()
			if num_unique > 0:
				loopRowData.append("%d" % num_unique)
			else:
				loopRowData.append("")
	
			total_in_area = area.getNumTotalBonuses()
			total += total_in_area
			loopRowData.append("%d" % total_in_area)

			for j in range(len(bonus_infos)):
				quantity = area.getNumBonuses(j)
				if quantity > 0:
					loopRowData.append("%d" % quantity)
				else:
					loopRowData.append("")
			d_TableData[i+1] = loopRowData
			loopRowData = []
	
		# Add last row of totals:
		last_row = len(areas) + 1
		loopRowData.append("Total")
		loopRowData.append(map.numPlots())
		# <!-- custom: The totals row mirrors the area rows above (area, tiles, starting plots, unique bonus types, total bonuses, then each bonus): "Total", the map's plot count, then "" twice for starting plots and unique bonus types, which vanilla does not total, then the bonus total.
		# Each of the two lines now names its field, as adjacent_duplicate_lines.py asks of a line meant twice. See KI#1104. (Claude code Opus 5.5) -->
		loopRowData.append("") # <!-- custom: starting plots (Claude code Opus 5.5) -->
		loopRowData.append("") # <!-- custom: unique bonus types (Claude code Opus 5.5) -->
		loopRowData.append("%d" % total)
		for j in range(len(bonus_infos)):
			quantity = map.getNumBonuses(j)
			if quantity > 0:
				loopRowData.append("%d" % quantity)
			else:
				loopRowData.append("-")
		iLastRow = len(d_TableData)
		d_TableData[iLastRow] = loopRowData
		
		#print d_TableData
		self.setTableData(d_TableData)
	
	def setTeams(self, strTitle = "Teams"):
		self.bTeam = true
		self.iNumTeams = gc.getGame().countCivTeamsEverAlive()
		return self.buildTeamTitleData(strTitle)

	def setPlayers(self, strTitle = "Players"):
		self.iNumPlayers = gc.getGame().countCivPlayersEverAlive()
		return self.buildPlayerTitleData(strTitle)
		
	def setTableData(self, d_TableData):
		' adds the Table Data to the screen '
		screen = self.getScreen()
		
		numColumns = len(d_TableData[0])
		
		#print "NumColumns = %d" %numColumns
		#print d_TableData
		
		
		szTableName = self.getNextWidgetName()
		# <!-- custom: Was 1000 x 580 at (0, 100), with 150 px for the first column and 70 for each other; now the table fills the screen's maximized area, and the other columns share the width left of the first, no narrower than vanilla's 70.
		# The table does not scroll sideways, so columns past its right edge were never shown, such as Map Details' bonuses after about the 8th; when they cannot all fit, the first column stays and the others are paged with arrows in the bottom bar, as the Foreign Advisor's Glance tab pages its players. See KI#1105.2. (Claude code Opus 5.5) -->
		iTableX, iTableY, iTableW, iTableH = self.TABLE_RECT
		columnHeaders = d_TableData[0]
		iFirstColW = 150
		# <!-- custom: Keeps the vertical scrollbar's 14 px off the last column, as the Military Advisor's Battles table does; Codex found a full SAS48 page left 12 px beside it. See KI#1105.2. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		iColsW = iTableW - 14 - iFirstColW
		iNumOther = numColumns - 1
		iPerPage = max(1, iColsW / 70)
		self.iNumPages = 1
		if iNumOther > iPerPage:
			self.iNumPages = (iNumOther + iPerPage - 1) / iPerPage
		self.iPage = max(0, min(self.iPage, self.iNumPages - 1))
		iStart = 1 + self.iPage * min(iNumOther, iPerPage)
		aiColumns = [0] + range(iStart, min(iStart + iPerPage, numColumns))
		iOtherColW = 70
		if iNumOther > 0:
			iOtherColW = max(70, iColsW / min(iNumOther, iPerPage))
		screen.addTableControlGFC(szTableName, len(aiColumns), iTableX, iTableY, iTableW, iTableH, True, True, 32,32,TableStyles.TABLE_STYLE_STANDARD)

		for iCol in range(len(aiColumns)):
			columnWidth = iOtherColW
			if iCol == 0:
				columnWidth = iFirstColW
			screen.setTableColumnHeader(szTableName, iCol, columnHeaders[aiColumns[iCol]], columnWidth)
		i=0
		for i in range(len(d_TableData)-1):
			screen.appendTableRow(szTableName)
		i=0
		for i in range(len(d_TableData)-1):
			rowData = d_TableData[i+1]
			for iCol in range(len(aiColumns)):
				j = aiColumns[iCol]
				if j < len(rowData):
					#print rowData[j]
					screen.setTableText(szTableName, iCol, i, u"%s" %rowData[j], "", WidgetTypes.WIDGET_GENERAL,-1,-1, CvUtil.FONT_LEFT_JUSTIFY)
		self.drawPageArrows(screen)

	# <!-- custom: The page arrows and "Page 2 / 3" in the bottom bar, only when the columns did not fit; numbered widgets, so deleteAllWidgets removes them with the table on each redraw, and handleInput matches them as the Glance tab does. See KI#1105.2. (Claude code Opus 5.5) -->
	def drawPageArrows(self, screen):
		self.szPageLeftID = ""
		self.szPageRightID = ""
		if self.iNumPages <= 1:
			return
		iArrowSize = 24
		iArrowY = self.Y_BOTTOM_PANEL + (self.H_SCREEN - self.Y_BOTTOM_PANEL - iArrowSize) / 2
		self.szPageLeftID = self.getNextWidgetName()
		screen.setButtonGFC(self.szPageLeftID, u"", "", 22, iArrowY, iArrowSize, iArrowSize, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_ARROW_LEFT)
		screen.enable(self.szPageLeftID, self.iPage > 0)
		self.szPageRightID = self.getNextWidgetName()
		screen.setButtonGFC(self.szPageRightID, u"", "", 22 + iArrowSize + 8, iArrowY, iArrowSize, iArrowSize, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_ARROW_RIGHT)
		screen.enable(self.szPageRightID, self.iPage < self.iNumPages - 1)
		szPage = u"Page %d / %d" % (self.iPage + 1, self.iNumPages)
		screen.setLabel(self.getNextWidgetName(), "Background", SASTextScale.sasFontTagLabel + szPage + SASTextScale.SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, 22 + 2 * iArrowSize + 20, iArrowY + 2, self.EXIT_TEXT_Z, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def buildTeamTitleData(self, strTitle):
		' return a '
		title_list = []
		
		for i in range( self.iNumTeams ):
			strName = gc.getTeam(i).getName()

			title_list.append( strName )
	
		title_list.insert( 0,strTitle )
		
		return title_list

	def buildPlayerTitleData(self, strTitle):
		' return a '
		title_list = []
		
		for i in range( self.iNumPlayers ):
			strName = gc.getPlayer(i).getName()
			title_list.append( strName )
	
		title_list.insert( 0,strTitle )
		
		return title_list

	# returns a unique ID for a widget in this screen
	def getNextWidgetName(self):
		szName = self.WIDGET_ID + str(self.nWidgetCount)
		self.nWidgetCount += 1
		return szName
		
	def deleteAllWidgets(self, iNumPermanentWidgets = 0):
		screen = self.getScreen()
		i = self.nWidgetCount - 1
		while (i >= iNumPermanentWidgets):
			self.nWidgetCount = i
			screen.deleteWidget(self.getNextWidgetName())
			i -= 1
		
		self.nWidgetCount = iNumPermanentWidgets
		self.yMessage = 5

	def InfoType (self, inputClass):
		screen = self.getScreen()
		'called when the player activates the drop down box'
		#print inputClass.getNotifyCode()
		
		if ( inputClass.getNotifyCode() == int(NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED) ) :
			#return
			szPulldownID = str(inputClass.getID())
			# Get the ID that was selected...
			iSelectedID = screen.getSelectedPullDownID( self.szDebugInfoPulldownID )
			self.deleteAllWidgets()
			# <!-- custom: Another tab starts on its first page. See KI#1105.2. (Claude code Opus 5.5) -->
			self.iPage = 0
			self.drawContents(iSelectedID)

	def handleInput (self, inputClass):
		'Calls function mapped in FinanceAdvisorInputMap'
		functionName = inputClass.getFunctionName()
		# <!-- custom: was a Python 2 print statement, which Ruff cannot parse. See KI#1104. (Claude code Opus 5.5) -->
		print(functionName)
		if ( functionName == self.szDebugInfoPulldownID ):
			self.InfoType(inputClass)
		# <!-- custom: The column page arrows from drawPageArrows; a click redraws the same tab one page over.
		# The new table starts scrolled to the top, as the Python API offers no way to read or set a table's scroll position (Codex's check). See KI#1105.2. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		elif inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and self.szPageLeftID and functionName + str(inputClass.getID()) == self.szPageLeftID:
			self.iPage = max(0, self.iPage - 1)
			self.deleteAllWidgets()
			self.drawContents(g_iLastScreen)
			return 1
		elif inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and self.szPageRightID and functionName + str(inputClass.getID()) == self.szPageRightID:
			self.iPage = min(self.iNumPages - 1, self.iPage + 1)
			self.deleteAllWidgets()
			self.drawContents(g_iLastScreen)
			return 1
		return 0

	def update(self, fDelta):
		return

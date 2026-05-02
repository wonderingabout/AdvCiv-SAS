# SevoPediaIndex
#
# Copyright (c) 2008 The BUG Mod.
#
# EF: Converted from Civilopedia version by fitchn.

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
import BugUtil
from SASFontUtils import *
from _sevopedia_helpers import place_new_concept_legend_link

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaIndex:

	def __init__(self, main):
		self.top = main
		
		self.LIST_BUTTON_SIZE = 24
		self.SAS_indexSetLayout(False)
		
		self.index = None
		self.letterTextIDs = None
		self.SAS_INDEX_SEARCH_PANEL_ID = "PediaIndexSearchPanel"
		self.SAS_INDEX_SEARCH_LABEL_ID = "PediaIndexSearchLabel"
		self.SAS_INDEX_SEARCH_CLEAR_ID = "PediaIndexSearchClear"
		self.SAS_INDEX_SEARCH_DEFAULT_TEXT = u"Enter text"
		self.SAS_INDEX_SEARCH_H = 32
		self.SAS_szIndexSearchString = u""
		self.SAS_indexKeyDebounceByKey = {}
		self.SAS_indexWidgetNames = []

	def SAS_indexSetLayout(self, bCategory):
		if bCategory:
			self.X_INDEX = self.top.X_ITEMS
			self.Y_INDEX = self.top.Y_ITEMS
			self.W_INDEX = self.top.W_SCREEN - self.top.X_ITEMS
			self.H_INDEX = self.top.H_ITEMS
		else:
			self.X_INDEX = self.top.X_CATEGORIES
			self.Y_INDEX = self.top.Y_CATEGORIES
			self.W_INDEX = self.top.W_SCREEN - 2 * self.top.X_CATEGORIES
			self.H_INDEX = self.top.H_CATEGORIES
		
		self.X_LETTER = self.X_INDEX + 130  # position of first letter button
		self.Y_LETTER = self.Y_INDEX
		self.W_LETTER = 20

	def interfaceScreen(self, bCategory=False):
		self.SAS_indexSetLayout(bCategory)
		self.buildIndex()
		self.placeIndex()
	
	def SAS_indexDeleteSearchWidgets(self):
		screen = self.top.getScreen()
		self.top.SAS_safeDeleteWidget(screen, self.SAS_INDEX_SEARCH_PANEL_ID)
		self.top.SAS_safeDeleteWidget(screen, self.SAS_INDEX_SEARCH_LABEL_ID)
		self.top.SAS_safeDeleteWidget(screen, self.SAS_INDEX_SEARCH_CLEAR_ID)
	
	def SAS_indexIsSearchActive(self):
		return (self.SAS_szIndexSearchString is not None and len(self.SAS_szIndexSearchString.strip()) > 0)
	
	def SAS_indexSyncSearchPanel(self):
		screen = self.top.getScreen()
		
		self.SAS_indexDeleteSearchWidgets()
		
		iX = self.X_INDEX
		iY = self.Y_INDEX
		iW = self.W_INDEX
		iH = self.SAS_INDEX_SEARCH_H
		
		screen.addPanel(self.SAS_INDEX_SEARCH_PANEL_ID, u"", u"", True, True, iX, iY, iW, iH, PanelStyles.PANEL_STYLE_BLUE50)
		
		if self.SAS_indexIsSearchActive():
			szText = self.SAS_szIndexSearchString
		else:
			szText = self.SAS_INDEX_SEARCH_DEFAULT_TEXT
		
		screen.setLabel(self.SAS_INDEX_SEARCH_LABEL_ID, self.SAS_INDEX_SEARCH_PANEL_ID,
				SAS_FONT_TAG_LABEL + szText + SAS_FONT_TAG_CLOSE,
				CvUtil.FONT_LEFT_JUSTIFY, iX + 6, iY + 6, 0,
				FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		if self.SAS_indexIsSearchActive():
			screen.setLabel(self.SAS_INDEX_SEARCH_CLEAR_ID, self.SAS_INDEX_SEARCH_PANEL_ID,
					SAS_FONT_TAG_LABEL + u"x" + SAS_FONT_TAG_CLOSE,
					CvUtil.FONT_RIGHT_JUSTIFY, iX + iW - 6, iY + 6, 0,
					FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def buildIndex(self):
		if self.index:
			return
		
		techList = self.top.getTechList()
		unitList = self.top.getUnitList()
		unitCombatList = self.top.getUnitCategoryList()
		promotionList = self.top.getPromotionList()
		
		buildingList = self.top.getBuildingList()
		nationalWonderList = self.top.getNationalWonderList()
		worldWonderList = self.top.getWorldWonderList()
		projectList = self.top.getProjectList()
		specialistList = self.top.getSpecialistList()
		
		terrainList = self.top.getTerrainList()
		featureList = self.top.getFeatureList()
		bonusList = self.top.getBonusList()
		improvementList = self.top.getImprovementList()
		
		civList = self.top.getCivilizationList()
		leaderList = self.top.getLeaderList()
		traitList = self.top.getTraitList()
		
		civicList = self.top.getCivicList()
		religionList = self.top.getReligionList()
		corporationList = self.top.getCorporationList()
		
		conceptList = self.top.getConceptList()
		newConceptList = self.top.getNewConceptList()
		# <!-- custom: add Builds to index, inspired by Middle-earth mod's PlatyPedia approach (Claude Opus 4.5) -->
		buildList = self.top.getBuildList()
		
		list=[]
		for item in techList:
			if (item[0][0:4]=="The "):
				list.append([item[0][4:]+","+item[0][0:3],"Tech",item])
			else:
				list.append([item[0],"Tech",item])
		for item in unitList:
			if (item[0][:13]=="TXT_KEY_UNIT_"):
				list.append([item[0][13:].capitalize(),"Unit",item])
			else:
				list.append([item[0],"Unit",item])
		for item in unitCombatList:
			list.append([item[0],"UnitCombat",item])
		for item in promotionList:
			if (item[0][:18]=="TXT_KEY_PROMOTION_"):
				list.append([item[0][18:].capitalize(),"Promo",item])
			else:
				list.append([item[0],"Promo",item])
		
		for item in buildingList:
			if (item[0][:17]=="TXT_KEY_BUILDING_"):
				list.append([item[0][17:].capitalize(),"Building",item])
			else:
				list.append([item[0],"Building",item])
		for item in nationalWonderList:
			if (item[0][0:4]=="The "):
				list.append([item[0][4:]+","+item[0][0:3],"Wonder",item])
			elif (item[0][:17]=="TXT_KEY_BUILDING_"):
				list.append([item[0][17:].capitalize(),"Wonder",item])
			else:
				list.append([item[0],"Wonder",item])
		for item in worldWonderList:
			if (item[0][0:4]=="The "):
				list.append([item[0][4:]+","+item[0][0:3],"Wonder",item])
			elif (item[0][:17]=="TXT_KEY_BUILDING_"):
				list.append([item[0][17:].capitalize(),"Wonder",item])
			else:
				list.append([item[0],"Wonder",item])
		for item in projectList:
			if (item[0][0:4]=="The "):
				list.append([item[0][4:]+","+item[0][0:3],"Project",item])
			else:
				list.append([item[0],"Project",item])
		for item in specialistList:
			if (item[0][:19]=="TXT_KEY_SPECIALIST_"):
				list.append([item[0][19:].capitalize(),"Specialist",item])
			else:
				list.append([item[0],"Specialist",item])
		
		for item in terrainList:
			list.append([item[0],"Terrain",item])
		for item in featureList:
			list.append([item[0],"Feature",item])
		for item in bonusList:
			list.append([item[0],"Bonus",item])
		for item in improvementList:
			list.append([item[0],"Improv",item])
		
		for item in civList:
			list.append([item[0],"Civ",item])
		for item in leaderList:
			list.append([item[0],"Leader",item])
		for item in traitList:
			list.append([item[0][2:],"Trait",item])
		
		for item in religionList:
			list.append([item[0],"Religion",item])
		for item in civicList:
			if (item[0][:14]=="TXT_KEY_CIVIC_"):
				list.append([item[0][14:].capitalize(),"Civic",item])
			else:
				list.append([item[0],"Civic",item])
		
		for item in conceptList:
			list.append([item[0],"Concept",item])
		for item in newConceptList:
			list.append([item[0],"NewConcept",item])
		# <!-- custom: add Builds to index (Claude Opus 4.5) -->
		for item in buildList:
			list.append([item[0],"Build",item])
		
		list.sort()
		self.index = list
		
	def placeIndex(self):
		screen = self.top.getScreen()
		CONCEPT_CHAR = gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getChar()
		place_new_concept_legend_link(self.top, "CONCEPT_SAS_SEVOPEDIA_CATEGORIES_LEGEND")
		
		if self.SAS_indexWidgetNames:
			for szWidget in self.SAS_indexWidgetNames:
				try:
					screen.deleteWidget(szWidget)
				except:
					pass
			self.SAS_indexWidgetNames = []
		
		self.SAS_indexSyncSearchPanel()
		
		nColumns = 3
		self.tableName = self.top.getNextWidgetName()
		self.SAS_rowToBuild = {}
		self.SAS_rowToTrait = {}  # <!-- custom: row-to-trait mapping for WIDGET_PYTHON trait handling. (Claude Opus 4.5) -->
		self.iTableWidgetId = int(self.tableName.replace(self.top.WIDGET_ID, ""))
		iTableY = self.Y_INDEX + self.SAS_INDEX_SEARCH_H + 4
		iTableH = self.H_INDEX - (iTableY - self.Y_INDEX)
		# <!-- custom: For Build entries, table selection is the only reliable click signal, so keep the table selectable and capture
		# row->Build mapping in handleInput. We previously tried overlay buttons, but they ignored table scrolling and desynced from rows.
		# Also, if the table doesn't have focus on first open, NOTIFY_CHARACTER goes nowhere and the search bar appears "dead" until
		# you navigate away and back. Setting focus here keeps search responsive and avoids the broken first-load behavior. Credit:
		# Claude Opus 4.5 + GPT-5.2-Codex. (GPT-5.2-Codex (summarized)) -->
		screen.addTableControlGFC(self.tableName, nColumns, self.X_INDEX, iTableY, self.W_INDEX, iTableH, True, True, self.LIST_BUTTON_SIZE, self.LIST_BUTTON_SIZE, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(self.tableName, True)
		screen.setFocus(self.tableName)
		self.SAS_indexWidgetNames.append(self.tableName)
		for i in range(nColumns):
			screen.setTableColumnHeader(self.tableName, i, "", (self.W_INDEX - 10) / nColumns)
		
		iRow = -1
		iColumn = 0
		sLetter = "#"
		iX = self.X_LETTER
		iLetterY = self.Y_INDEX + self.SAS_INDEX_SEARCH_H + 4
		self.letterTextIDs = {}
		# <!-- custom: note: while adding leaderhead art_def in AdvCiv-SAS-NIF-Gallery mod we saw the error "UnicodeDecodeError: 'ascii' codec can't decode byte 0xc8 in position 0" and in Sevopedia Leader, fixed by respecting path case sensitivity (e.g. "Art/LeaderHeads"). So reverted a previous patch that would workaround that: prefer to fail loudly instead and fix path or asset cause directly rather. See KI#111. (GPT-5.3-Codex) -->
		szFilter = self.SAS_szIndexSearchString.strip().lower()
		bFilter = (len(szFilter) > 0)
		for name, type, item in self.index:
			if item[1] < 0:
				continue
			if bFilter and name.lower().find(szFilter) == -1:
				continue
			if (name[:1] != sLetter):
				sLetter = name[:1]
				screen.appendTableRow(self.tableName)
				iRow += 1
				screen.setTableText(self.tableName, 1, iRow, SAS_FONT_TAG_TITLE + u"- " + sLetter + u" -" + SAS_FONT_TAG_CLOSE, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
				screen.appendTableRow(self.tableName)
				# create letter button
				textName = self.top.getNextWidgetName()
				letterText = SAS_FONT_TAG_TITLE + sLetter + SAS_FONT_TAG_CLOSE
				screen.setText(textName, "Background", letterText, CvUtil.FONT_CENTER_JUSTIFY, 
						iX, iLetterY, 0, FontTypes.TITLE_FONT, 
						WidgetTypes.WIDGET_GENERAL, iRow, -1)
				self.letterTextIDs[textName] = iRow
				self.SAS_indexWidgetNames.append(textName)
				iX += self.W_LETTER
				iRow += 1
				iColumn = 0
			else:
				iColumn += 1
				if (iColumn >= nColumns):
					screen.appendTableRow(self.tableName)
					iRow += 1
					iColumn = 0
			
			# <!-- custom: refactor, since sText was defined in existing code, reuse it instead of hardcoding it again at each call if i may say and am not mistaken, this also fixes ruff warning and according to chatgpt this is unused as well and safe to remove as well so adding it again; similarly removed unused lines `sButton = ""` and `eWidget = None` and as for lines `iData1 = item[1]` and `iData2 = 1` also using them as variables similarly instead of hardcoding them each time -->
			sText = SAS_FONT_TAG_LABEL + item[0] + SAS_FONT_TAG_CLOSE
			iData1 = item[1]
			iData2 = 1
			if (type == "Tech"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getTechInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Unit"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getUnitInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "UnitCombat"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getUnitCombatInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Promo"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getPromotionInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			
			elif (type == "Building"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getBuildingInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Wonder"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getBuildingInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Project"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getProjectInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Specialist"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getSpecialistInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPECIALIST, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			
			elif (type == "Terrain"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getTerrainInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Feature"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getFeatureInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Bonus"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getBonusInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Improv"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getImprovementInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			# <!-- custom: Build rows use the normal table cell (icon + text) and rely on table selection to trigger pediaJump.
			# This avoids overlay widgets that don't scroll with the table. Credit: Claude Opus 4.5 + GPT-5.2-Codex. (GPT-5.2-Codex (summarized)) -->
			elif (type == "Build"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getBuildInfo(iData1).getButton(), WidgetTypes.WIDGET_HELP_IMPROVEMENT, gc.getBuildInfo(iData1).getTechPrereq(), iData1, CvUtil.FONT_LEFT_JUSTIFY)
				self.SAS_rowToBuild[iRow] = iData1
			
			elif (type == "Civ"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getCivilizationInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Leader"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getLeaderHeadInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			# <!-- custom: Trait rows use WIDGET_GENERAL and row-to-trait mapping like Builds. (Claude Opus 4.5) -->
			elif (type == "Trait"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getTraitInfo(iData1).getButton(), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
				self.SAS_rowToTrait[iRow] = iData1
			
			elif (type == "Civic"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getCivicInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Religion"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getReligionInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			# <!-- custom: base AdvCiv bugfix GPT-5.2-Codex found thanks, was gc.getReligionInfo(iData1).getButton() -->
			elif (type == "Corporation"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getCorporationInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			
			elif (type == "Concept"):
				screen.setTableText(self.tableName, iColumn, iRow, SAS_FONT_TAG_LABEL + (u"%c %s" % (CONCEPT_CHAR, item[0])) + SAS_FONT_TAG_CLOSE, gc.getConceptInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_DESCRIPTION, CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT, iData1, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "NewConcept"):
				screen.setTableText(self.tableName, iColumn, iRow, SAS_FONT_TAG_LABEL + (u"%c %s" % (CONCEPT_CHAR, item[0])) + SAS_FONT_TAG_CLOSE, gc.getConceptInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_DESCRIPTION, CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW, iData1, CvUtil.FONT_LEFT_JUSTIFY)
		
		self.iLastRow = iRow

	def handleInput (self, inputClass):
		BugUtil.debugInput(inputClass)
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
			if inputClass.getFunctionName() == self.SAS_INDEX_SEARCH_CLEAR_ID:
				if self.SAS_indexIsSearchActive():
					self.SAS_szIndexSearchString = u""
					self.SAS_indexKeyDebounceByKey = {}
					self.placeIndex()
				return 1
		
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CHARACTER:
			screen = self.top.getScreen()
			if screen.isActive():
				if (not inputClass.isAltKeyDown()) and (not inputClass.isCtrlKeyDown()):
					iKey = inputClass.getData()
					
					if self.top.SAS_shouldDebounceKey(iKey):
						if self.SAS_indexKeyDebounceByKey.get(iKey, 0):
							self.SAS_indexKeyDebounceByKey[iKey] = 0
							return 1
						self.SAS_indexKeyDebounceByKey[iKey] = 1
					
					szChar = self.top.SAS_getVisibleCharacter(inputClass)
					if len(szChar) > 0:
						self.SAS_szIndexSearchString = self.SAS_szIndexSearchString + szChar
						self.placeIndex()
						return 1
					
					if iKey == int(InputTypes.KB_BACKSPACE):
						if len(self.SAS_szIndexSearchString) > 0:
							self.SAS_szIndexSearchString = self.SAS_szIndexSearchString[:-1]
							self.placeIndex()
							return 1
					elif iKey == int(InputTypes.KB_ESCAPE):
						if self.SAS_indexIsSearchActive():
							self.SAS_szIndexSearchString = u""
							self.SAS_indexKeyDebounceByKey = {}
							self.placeIndex()
							return 1
		
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED 
				and inputClass.getFunctionName() + str(inputClass.getID()) in self.letterTextIDs):
			screen = self.top.getScreen()
			screen.selectRow(self.tableName, self.iLastRow, True)
			screen.selectRow(self.tableName, inputClass.getData1(), True)
			return 1
		
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and inputClass.getButtonType() == WidgetTypes.WIDGET_HELP_IMPROVEMENT:
			iBuild = inputClass.getData2()
			# <!-- custom: Build rows now use WIDGET_HELP_IMPROVEMENT to restore hover text in Index; route click
			# explicitly to Sevopedia Builds so behavior matches other Build entries. See KI#113. (GPT-5.3-Codex) -->
			if iBuild >= 0 and iBuild < gc.getNumBuildInfos():
				return self.top.pediaJump(SevoScreenEnums.PEDIA_BUILDS, iBuild, True, False)
		
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED
				or inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED):
			if inputClass.getFunctionName() == self.top.WIDGET_ID and inputClass.getID() == self.iTableWidgetId:
				iRow = inputClass.getData()
				iBuild = self.SAS_rowToBuild.get(iRow, None)
				if iBuild is not None:
					return self.top.pediaJump(SevoScreenEnums.PEDIA_BUILDS, iBuild, True, False)
				# <!-- custom: Handle trait clicks via row mapping. (Claude Opus 4.5) -->
				iTrait = self.SAS_rowToTrait.get(iRow, None)
				if iTrait is not None:
					return self.top.pediaJump(SevoScreenEnums.PEDIA_TRAITS, iTrait, True, False)
		return 0

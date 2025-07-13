# SevoPediaIndex
#
# Copyright (c) 2008 The BUG Mod.
#
# EF: Converted from Civilopedia version by fitchn.


from CvPythonExtensions import *
import CvUtil
# <!-- custom: remove or comment out unused imports -->
#import ScreenInput
#import SevoScreenEnums
import BugUtil

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaIndex:

	def __init__(self, main):
		self.top = main
		
		self.LIST_BUTTON_SIZE = 24
		self.X_INDEX = self.top.X_CATEGORIES
		self.Y_INDEX = self.top.Y_CATEGORIES
		self.W_INDEX = self.top.W_SCREEN - 2 * self.top.X_CATEGORIES
		self.H_INDEX = self.top.H_CATEGORIES
		
		self.X_LETTER = main.X_INDEX + 130  # position of first letter button
		self.Y_LETTER = main.Y_INDEX
		self.W_LETTER = 20
		
		self.index = None
		self.letterTextIDs = None

	def interfaceScreen(self):
		self.buildIndex()
		self.placeIndex()

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
		# <!-- custom: unused line so commented-out to fix ruff warning if i am not mistaken anyways etc -->
		#corporationList = self.top.getCorporationList()
		
		conceptList = self.top.getConceptList()
		newConceptList = self.top.getNewConceptList()
		
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
		
		list.sort()
		self.index = list
		
	def placeIndex(self):
		screen = self.top.getScreen()
		CONCEPT_CHAR = gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getChar()
		
		nColumns = 3
		self.tableName = self.top.getNextWidgetName()
		screen.addTableControlGFC(self.tableName, nColumns, self.X_INDEX, self.Y_INDEX, self.W_INDEX, self.H_INDEX, False, False, self.LIST_BUTTON_SIZE, self.LIST_BUTTON_SIZE, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(self.tableName, False)
		for i in range(nColumns):
			screen.setTableColumnHeader(self.tableName, i, "", (self.W_INDEX - 10) / nColumns)
		
		iRow = -1
		iColumn = 0
		sLetter = "#"
		iX = self.X_LETTER
		self.letterTextIDs = {}
		for name, type, item in self.index:
			if (name[:1] != sLetter):
				sLetter = name[:1]
				screen.appendTableRow(self.tableName)
				iRow += 1
				screen.setTableText(self.tableName, 1, iRow, u"<font=4>- " + sLetter + u" -</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
				screen.appendTableRow(self.tableName)
				# create letter button
				textName = self.top.getNextWidgetName()
				letterText = u"<font=4>%s</font>" % sLetter
				screen.setText(textName, "Background", letterText, CvUtil.FONT_CENTER_JUSTIFY, 
						iX, self.Y_LETTER, 0, FontTypes.TITLE_FONT, 
						WidgetTypes.WIDGET_GENERAL, iRow, -1)
				self.letterTextIDs[textName] = iRow
				iX += self.W_LETTER
				iRow += 1
				iColumn = 0
			else:
				iColumn += 1
				if (iColumn >= nColumns):
					screen.appendTableRow(self.tableName)
					iRow += 1
					iColumn = 0
			
			# <!-- custom: refactor, since sText was defined in existing code, reuse it instead of hardcoding it again at each call if i may say and am not mistaken, this also fixes ruff warning and according to chatgpt this is unused as well and safe to remove as well so adding it again in this case i mean anyways etc ; similarly removed unused lines `sButton = ""` and `eWidget = None` and as for lines `iData1 = item[1]` and `iData2 = 1` adding them instead of hardcoding each time same variables if i am not mistaken anyways etc  -->
			sText = u"<font=3>" + item[0] + u"</font>"
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
			
			elif (type == "Civ"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getCivilizationInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Leader"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getLeaderHeadInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Trait"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getConceptInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_DESCRIPTION, CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW, iData1, CvUtil.FONT_LEFT_JUSTIFY)
			
			elif (type == "Civic"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getCivicInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Religion"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getReligionInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Corporation"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getReligionInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			
			elif (type == "Concept"):
				screen.setTableText(self.tableName, iColumn, iRow, u"<font=3>%c %s</font>" % (CONCEPT_CHAR, item[0]), gc.getConceptInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_DESCRIPTION, CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT, iData1, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "NewConcept"):
				screen.setTableText(self.tableName, iColumn, iRow, u"<font=3>%c %s</font>" % (CONCEPT_CHAR, item[0]), gc.getConceptInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_DESCRIPTION, CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW, iData1, CvUtil.FONT_LEFT_JUSTIFY)
		
		self.iLastRow = iRow

	def handleInput (self, inputClass):
		BugUtil.debugInput(inputClass)
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED 
				and inputClass.getFunctionName() + str(inputClass.getID()) in self.letterTextIDs):
			screen = self.top.getScreen()
			screen.selectRow(self.tableName, self.iLastRow, True)
			screen.selectRow(self.tableName, inputClass.getData1(), True)
		return 0

# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose, EmperorFool
# see ReadMe [advc: BUG help file] for details
#



from CvPythonExtensions import *

import CvUtil
import ScreenInput
import SevoScreenEnums

import CvPediaScreen
import SevoPediaTech
import SevoPediaUnit
import SevoPediaBuilding
import SevoPediaPromotion
import SevoPediaUnitChart
import SevoPediaBonus
import SevoPediaTerrain
import SevoPediaFeature
import SevoPediaImprovement
import SevoPediaCivic
import SevoPediaCivilization
import SevoPediaLeader
import SevoPediaTrait # advc.004y: Restored
import SevoPediaSpecialist
import SevoPediaHistory
import SevoPediaProject
import SevoPediaReligion
import SevoPediaCorporation
import SevoPediaIndex

import UnitUpgradesGraph
import TraitUtil
import BugCore
import BugUtil

from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

AdvisorOpt = BugCore.game.Advisors

g_TraitUtilInitDone = False



class SevoPediaMain(CvPediaScreen.CvPediaScreen):

	def __init__(self):
		self.PEDIA_MAIN_SCREEN	= "PediaMainScreen"
		self.INTERFACE_ART_INFO	= "SCREEN_BG_OPAQUE"
		
		self.TAB_TOC   = "Contents"
		self.TAB_INDEX = "Index"

		self.WIDGET_ID		= "PediaMainWidget"
		self.BACKGROUND_ID	= "PediaMainBackground"
		self.TOP_PANEL_ID	= "PediaMainTopPanel"
		self.BOT_PANEL_ID	= "PediaMainBottomPanel"
		self.HEAD_ID		= "PediaMainHeader"
		self.TOC_ID			= "PediaMainContents"
		self.INDEX_ID		= "PediaMainIndex"
		self.BACK_ID		= "PediaMainBack"
		self.NEXT_ID		= "PediaMainForward"
		self.EXIT_ID		= "PediaMainExit"
		self.CATEGORY_LIST_ID	= "PediaMainCategoryList"
		self.ITEM_LIST_ID	= "PediaMainItemList"
		self.UPGRADES_GRAPH_ID	= "PediaMainUpgradesGraph"

		self.H_SCREEN = 768
		self.W_SCREEN = 1024

		# <advc.004y>
		self.bWideScreen = True
		self.bFullScreen = True
		if self.bFullScreen:
			self.bWideScreen = True
		# <!-- custom: Not much value in being able to see the elements at the edge parts of the screen, however i think the extra room can be useful to fit more data or simply enlarge the view, hopefully making it all clearer and more pleasant to see. Other mods such as realism invictus or c2c use the entire screen for the sevopedia if i'm not mistaken and i like it fine, tested in AdvCiv-SAS and i like it very much, so removing margins now. -->
		self.HORIZONTAL_MARGIN = 0
		# VERTICAL_MARGIN: Want the Advisor buttons to remain visible. BOTTOM_MARGIN could be 0, but I don't think asymmetrical margins look good.
		self.TOP_MARGIN = 0
		self.BOTTOM_MARGIN = 0
		if self.bWideScreen:
			self.W_SCREEN = max(self.W_SCREEN, self.getScreen().getXResolution() - 2 * self.HORIZONTAL_MARGIN)
			if self.W_SCREEN <= 1024:
				self.bWideScreen = False
				self.bFullScreen = False
		if self.bFullScreen:
			self.H_SCREEN = max(self.H_SCREEN, self.getScreen().getYResolution() - self.BOTTOM_MARGIN - self.TOP_MARGIN)
			if self.H_SCREEN <= 768:
				self.bFullScreen = False
		#self.X_SCREEN = 500 # now unused
		#self.Y_SCREEN = 396 # unused to begin with
		# </advc.004y>

		self.H_PANEL = 55

		self.X_TOP_PANEL = 0
		self.Y_TOP_PANEL = 0
		self.W_TOP_PANEL = self.W_SCREEN
		self.H_TOP_PANEL = self.H_PANEL

		self.X_BOT_PANEL = 0
		self.Y_BOT_PANEL = self.H_SCREEN - self.H_PANEL
		self.W_BOT_PANEL = self.W_SCREEN
		self.H_BOT_PANEL = self.H_PANEL

		self.X_CATEGORIES = 0
		self.Y_CATEGORIES = (self.Y_TOP_PANEL + self.H_TOP_PANEL) - 4
		# <!-- custom: increase for smaller screens (resolutions) too, now that sevopedia is expanded (no margins) they should have much more room hopefully to accomodate a full row width, increase only as minimally as necessary (acording to what i measured) (did not test but should hopefully work perhaps even better, anyways), was 182 -->
		# advc.002b: was 175
		# <!-- custom: was 200 -->
		self.W_CATEGORIES = 124
		# <advc.004y>
		if self.bWideScreen:
			# <!-- custom: could reduce it to 200 still displaying all text in the dedicated panel (but very close, 199 does not fit, 200 is the strict minimum on 1920 x 1080, and i assume resolutions don't affect this but i don't know, still even if they did is quite minor (at worse the text would need 2 rows (in total to be displayed in just the category, but the place/room i gain is very (and much more useful than this header width, so leaving as is, even if does not work/function as intended is fine, as long as not critically broken this is (just but anyways...) the category header text, we need info on the main big panel rather, anyways), was 230
			# May actually even be visually clearer as the distance between the words in categories and the items's words in the items category is smaller, perhaps allowing for an even smaller,allowing for a faster and more direct, perhaps clearer intutive connection between these maybe but anyways -->
			# Can't be much thinner than this or hover text will sometimes appear in the categories columns and sometimes (when the text box is too wide) in the items column
			# <!-- custom: was 200 -->
			self.W_CATEGORIES = 124
		# </advc.004y>
		self.H_CATEGORIES = (self.Y_BOT_PANEL + 3) - self.Y_CATEGORIES

		self.X_ITEMS = self.X_CATEGORIES + self.W_CATEGORIES + 2
		self.Y_ITEMS = self.Y_CATEGORIES
		# <!-- custom: same reasoning as for/in smaller categories, did not test but should be fine with the new space, anyways, was 210 -->
		self.W_ITEMS = 230
		# <advc.004y>
		if self.bWideScreen:
			self.W_ITEMS = 230
		# </advc.004y>
		self.H_ITEMS = self.H_CATEGORIES

		self.X_PEDIA_PAGE = self.X_ITEMS + self.W_ITEMS + 18
		self.Y_PEDIA_PAGE = self.Y_ITEMS + 13
		self.R_PEDIA_PAGE = self.W_SCREEN - 20
		self.B_PEDIA_PAGE = self.Y_ITEMS + self.H_ITEMS - 16
		self.W_PEDIA_PAGE = self.R_PEDIA_PAGE - self.X_PEDIA_PAGE
		self.H_PEDIA_PAGE = self.B_PEDIA_PAGE - self.Y_PEDIA_PAGE

		self.X_TITLE = (self.W_SCREEN - 24) // 2 # advc.004y: was 500
		self.Y_TITLE = 8
		# <advc.004y>
		self.X_TOC = 45 # was 75
		Y_FOOTER_CONTROLS = self.Y_BOT_PANEL + 16 # was 730
		# </advc.004y>
		self.Y_TOC = Y_FOOTER_CONTROLS
		self.X_INDEX = self.X_TOC + 135 # advc.004y: was 210
		self.Y_INDEX = Y_FOOTER_CONTROLS
		self.X_BACK = (self.W_SCREEN - 4) // 2 # advc.004y: was 510
		self.Y_BACK = Y_FOOTER_CONTROLS
		self.X_NEXT = 133 + (self.W_SCREEN // 2) # advc.004y: was 645
		self.Y_NEXT = Y_FOOTER_CONTROLS
		self.X_EXIT = self.W_SCREEN - 30 # advc.004y: was 994
		self.Y_EXIT = Y_FOOTER_CONTROLS

		self.tab = None
		self.iActivePlayer = -1
		self.nWidgetCount = 0

		self.categoryList = []
		self.categoryGraphics = []
		self.iCategory = -1
		self.iItem = -1
		self.iItemIndex = -1
		self.pediaHistory = []
		self.pediaFuture = []

		# <!-- custom: compute once to be computationally more efficient if i'm not mistaken in my thinking, and added with the help of chatgpt 5.2 thanks, anyways etc. -->
		self.SAS_cacheCivicsTuple = None
		self.SAS_cacheTechsTuple = None
		self.SAS_cacheRegularBuildingsTuple = None
		self.SAS_cacheNationalWondersTuple = None
		self.SAS_cacheWorldWondersTuple = None
		self.SAS_cacheUnitsTuple = None
		self.SAS_cacheCorporationsTuple = None
		self.SAS_cacheCorporationHQBuildingByCorp = None

		# <!-- custom: do not build sevopedia leader cache until we click on the leaders category, so that if we never open at all the leaders category, no need to compute needlessly for their cache. And if we do access the leaders page, then building once the cache is enough for the entire session, no need to rebuild it even if we exit sevopedia. Therefore store the cache in sevopedia leader, but add a flag to not build cache at module load of sevopedia leader, but later on click in/at placeLeaders time if i am not mistaken and from what i understand of chatgpt's explanation anyways etc -->
		self.IS_SEVOPEDIALEADER_CACHE_PREBUILT = False
		# <!-- custom: do something similar for the untradeable techs text and or such other similar or quite similar codes if i may say or not or yes or etc but anyways etc anyways etc anyways etc -->
		self.IS_UNTRADEABLE_TECHS_TEXT_PREBUILT = False
		self.IS_FEATURES_PRE_LOADING_XML_DATA_VALIDATION_DONE = False

		self.mapListGenerators = {
			SevoScreenEnums.PEDIA_TECHS		: self.placeTechs,
			SevoScreenEnums.PEDIA_UNITS		: self.placeUnits,
			SevoScreenEnums.PEDIA_UNIT_UPGRADES	: self.placeUnitUpgrades,
			SevoScreenEnums.PEDIA_UNIT_CATEGORIES	: self.placeUnitCategories,
			SevoScreenEnums.PEDIA_PROMOTIONS		: self.placePromotions,
			SevoScreenEnums.PEDIA_PROMOTION_TREE	: self.placePromotionTree,
			SevoScreenEnums.PEDIA_BUILDINGS		: self.placeBuildings,
			SevoScreenEnums.PEDIA_NATIONAL_WONDERS	: self.placeNationalWonders,
			SevoScreenEnums.PEDIA_WORLD_WONDERS	: self.placeWorldWonders,
			SevoScreenEnums.PEDIA_PROJECTS		: self.placeProjects,
			SevoScreenEnums.PEDIA_SPECIALISTS		: self.placeSpecialists,
			SevoScreenEnums.PEDIA_TERRAINS		: self.placeTerrains,
			SevoScreenEnums.PEDIA_FEATURES		: self.placeFeatures,
			SevoScreenEnums.PEDIA_BONUSES		: self.placeBonuses,
			SevoScreenEnums.PEDIA_IMPROVEMENTS	: self.placeImprovements,
			SevoScreenEnums.PEDIA_CIVS		: self.placeCivs,
			SevoScreenEnums.PEDIA_LEADERS		: self.placeLeaders,
			# advc.004y: Restored
			SevoScreenEnums.PEDIA_TRAITS		: self.placeTraits,
			SevoScreenEnums.PEDIA_CIVICS		: self.placeCivics,
			SevoScreenEnums.PEDIA_RELIGIONS		: self.placeReligions,
			SevoScreenEnums.PEDIA_CORPORATIONS	: self.placeCorporations,
			SevoScreenEnums.PEDIA_CONCEPTS		: self.placeConcepts,
			SevoScreenEnums.PEDIA_BTS_CONCEPTS	: self.placeBTSConcepts,
			SevoScreenEnums.PEDIA_HINTS		: self.placeHints,
			SevoScreenEnums.PEDIA_SHORTCUTS  	: self.placeShortcuts,
			}

		self.pediaBuilding	= SevoPediaBuilding.SevoPediaBuilding(self)
		self.pediaLeader	= SevoPediaLeader.SevoPediaLeader(self)
		self.pediaIndex     = SevoPediaIndex.SevoPediaIndex(self)

		self.mapScreenFunctions = {
			SevoScreenEnums.PEDIA_TECHS		: SevoPediaTech.SevoPediaTech(self),
			SevoScreenEnums.PEDIA_UNITS		: SevoPediaUnit.SevoPediaUnit(self),
			SevoScreenEnums.PEDIA_UNIT_CATEGORIES	: SevoPediaUnitChart.SevoPediaUnitChart(self),
			SevoScreenEnums.PEDIA_PROMOTIONS		: SevoPediaPromotion.SevoPediaPromotion(self),
			SevoScreenEnums.PEDIA_BUILDINGS		: self.pediaBuilding,
			SevoScreenEnums.PEDIA_NATIONAL_WONDERS	: SevoPediaBuilding.SevoPediaBuilding(self),
			SevoScreenEnums.PEDIA_WORLD_WONDERS	: SevoPediaBuilding.SevoPediaBuilding(self),
			SevoScreenEnums.PEDIA_PROJECTS		: SevoPediaProject.SevoPediaProject(self),
			SevoScreenEnums.PEDIA_SPECIALISTS		: SevoPediaSpecialist.SevoPediaSpecialist(self),
			SevoScreenEnums.PEDIA_TERRAINS		: SevoPediaTerrain.SevoPediaTerrain(self),
			SevoScreenEnums.PEDIA_FEATURES		: SevoPediaFeature.SevoPediaFeature(self),
			SevoScreenEnums.PEDIA_BONUSES		: SevoPediaBonus.SevoPediaBonus(self),
			SevoScreenEnums.PEDIA_IMPROVEMENTS	: SevoPediaImprovement.SevoPediaImprovement(self),
			SevoScreenEnums.PEDIA_CIVS		: SevoPediaCivilization.SevoPediaCivilization(self),
			SevoScreenEnums.PEDIA_LEADERS		: self.pediaLeader,
			# advc.004y: Restored
			SevoScreenEnums.PEDIA_TRAITS		: SevoPediaTrait.SevoPediaTrait(self),
			SevoScreenEnums.PEDIA_CIVICS		: SevoPediaCivic.SevoPediaCivic(self),
			SevoScreenEnums.PEDIA_RELIGIONS		: SevoPediaReligion.SevoPediaReligion(self),
			SevoScreenEnums.PEDIA_CORPORATIONS	: SevoPediaCorporation.SevoPediaCorporation(self),
			SevoScreenEnums.PEDIA_CONCEPTS		: SevoPediaHistory.SevoPediaHistory(self),
			SevoScreenEnums.PEDIA_BTS_CONCEPTS	: SevoPediaHistory.SevoPediaHistory(self),
			SevoScreenEnums.PEDIA_SHORTCUTS  	: SevoPediaHistory.SevoPediaHistory(self),
			}



	def getScreen(self):
		return CyGInterfaceScreen(self.PEDIA_MAIN_SCREEN, SevoScreenEnums.PEDIA_MAIN)

	def createScreen(self, screen):
		if screen.isActive():
			return
		BugUtil.debug("Creating screen")
		self.iCategory = -1
		self.tab = None
		self.setPediaCommonWidgets()

	def pediaShow(self):
		global g_TraitUtilInitDone
		if not g_TraitUtilInitDone:
			TraitUtil.init()
			g_TraitUtilInitDone = True
		self.iActivePlayer = gc.getGame().getActivePlayer()
		self.iCategory = -1
		if (not self.pediaHistory):
			self.pediaHistory.append((SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_TECHS))
		current = self.pediaHistory.pop()
		self.pediaFuture = []
		self.pediaHistory = []
		self.pediaJump(current[0], current[1], False, True)



	def pediaJump(self, iCategory, iItem, bRemoveFwdList, bIsLink):
		# <!-- custom: note: fixed a (seemingly base advciv anyways etc) bug in in CvDLLWidgetData.cpp where iItem was -1 for obsolete bonuses redirecting from tech advisor, unlike obsolete buildings which didn't have the issue weirdly/strangely but anyways etc, with chatgpt's help and thanks to my prompt too and observation of the issue and or such but also chatgpt's help in guiding me bit too but anyways etc anyways etc anyways etc ; i had put a workaround here to use a placeholder for iItem but no needed anymore now that this is fixed if i am not mistaken anyways etc so reverted everything as base advciv code was minus this extra code comment if i may say but anyways etc, see also code comment at WIDGET_HELP_BONUS_REVEAL in CvDLLWidgetData.cpp or/and known issue number 22 as of now anyways etc in known issues of advciv-sas readme for details as well anyways etc -->
		bAddToHistory = False
		if (not self.pediaHistory):
			bAddToHistory = True
		elif (iCategory != SevoScreenEnums.PEDIA_MAIN or iItem == SevoScreenEnums.PEDIA_UNIT_UPGRADES or iItem == SevoScreenEnums.PEDIA_PROMOTION_TREE or iItem == SevoScreenEnums.PEDIA_HINTS):
			prev = self.pediaHistory[0]
			if (prev[0] != iCategory or prev[1] != iItem):
				bAddToHistory = True
		if (bAddToHistory):
			self.pediaHistory.append((iCategory, iItem))
		if (bRemoveFwdList):
			self.pediaFuture = []

		screen = self.getScreen()
		if not screen.isActive():
			self.createScreen(screen)

		if (iCategory == SevoScreenEnums.PEDIA_MAIN):
			BugUtil.debug("Main link %d" % iItem)
			self.showContents(bIsLink, iItem)
			screen.setSelectedListBoxStringGFC(self.CATEGORY_LIST_ID, iItem - (SevoScreenEnums.PEDIA_MAIN + 1))
			#self.iCategory = iItem
			return

		if (iCategory == SevoScreenEnums.PEDIA_BUILDINGS):
			iCategory += self.pediaBuilding.getBuildingType(iItem)
		elif (iCategory == SevoScreenEnums.PEDIA_BTS_CONCEPTS):
			iCategory = self.determineNewConceptSubCategory(iItem)
			BugUtil.debug("Switching to category %d" % iCategory)
		self.showContents(bIsLink, iCategory)
		screen.setSelectedListBoxStringGFC(self.CATEGORY_LIST_ID, iCategory - (SevoScreenEnums.PEDIA_MAIN + 1))
		if (iCategory not in (SevoScreenEnums.PEDIA_UNIT_UPGRADES, SevoScreenEnums.PEDIA_PROMOTION_TREE, SevoScreenEnums.PEDIA_HINTS)):
			screen.enableSelect(self.ITEM_LIST_ID, True)
			if (self.iItemIndex != -1):
				BugUtil.debug("Deselecting item %d" % self.iItemIndex)
				screen.selectRow(self.ITEM_LIST_ID, self.iItemIndex, False)
			BugUtil.debug("Selecting item %d" % iItem)
			self.iItem = iItem
			for i, item in enumerate(self.list):
				if (item[1] == iItem):
					BugUtil.debug("Selecting %dth item %d" % (i, iItem))
					#screen.setSelectedListBoxStringGFC(self.ITEM_LIST_ID, i)
					screen.selectRow(self.ITEM_LIST_ID, i, True)
					self.iItemIndex = i
					#break

		#self.iCategory = iCategory
		BugUtil.debug("Drawing screen %d item %d" % (iCategory, iItem))
		self.deleteAllWidgets()
		func = self.mapScreenFunctions.get(iCategory)
		func.interfaceScreen(iItem)

	def determineNewConceptSubCategory(self, iItem):
		info = gc.getNewConceptInfo(iItem)
		BugUtil.debug("NewConcept item %d is %s" % (iItem, info.getDescription()))
		if (self.isTraitInfo(info)):
			return SevoScreenEnums.PEDIA_TRAITS
		if (self.isShortcutInfo(info)):
			return SevoScreenEnums.PEDIA_SHORTCUTS
		return SevoScreenEnums.PEDIA_BTS_CONCEPTS

	def isContentsShowing(self):
		return self.tab == self.TAB_TOC
	
	def showContents(self, bForce=False, iCategory=SevoScreenEnums.PEDIA_TECHS):
		self.deleteAllWidgets()
		if not self.isContentsShowing():
			BugUtil.debug("Drawing category list")
			self.placeCategories(iCategory)
			screen = self.getScreen()
			screen.setText(self.TOC_ID, "Background", self.TOC_ACTIVE_TEXT,   CvUtil.FONT_LEFT_JUSTIFY,   self.X_TOC,   self.Y_TOC,   0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
			screen.setText(self.INDEX_ID, "Background", self.INDEX_TEXT, CvUtil.FONT_LEFT_JUSTIFY, self.X_INDEX, self.Y_INDEX, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
			screen.show(self.BACK_ID)
			screen.show(self.NEXT_ID)
		if not self.isContentsShowing() or self.iCategory != iCategory or bForce:
			BugUtil.debug("Drawing item list %d" % iCategory)
			self.mapListGenerators.get(iCategory)()
			self.iCategory = iCategory
			self.iItem = -1
			self.iItemIndex = -1
		self.tab = self.TAB_TOC

	def isIndexShowing(self):
		return self.tab == self.TAB_INDEX
	
	def showIndex(self):
		if self.isIndexShowing():
			return
		self.deleteAllWidgets()
		self.deleteListWidgets()
		screen = self.getScreen()
		screen.setText(self.TOC_ID, "Background", self.TOC_TEXT,   CvUtil.FONT_LEFT_JUSTIFY,   self.X_TOC,   self.Y_TOC,   0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
		screen.setText(self.INDEX_ID, "Background", self.INDEX_ACTIVE_TEXT, CvUtil.FONT_LEFT_JUSTIFY, self.X_INDEX, self.Y_INDEX, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
		screen.hide(self.BACK_ID)
		screen.hide(self.NEXT_ID)
		self.pediaIndex.interfaceScreen()
		self.tab = self.TAB_INDEX
	
	def setPediaCommonWidgets(self):
		# advc.004y: was TXT_KEY_SEVOPEDIA_TITLE
		self.HEAD_TEXT = u"<font=4b>" + localText.getText("TXT_KEY_CIVILOPEDIA_TITLE",      ())         + u"</font>"
		self.BACK_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_BACK",    ()).upper() + u"</font>"
		self.NEXT_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_FORWARD", ()).upper() + u"</font>"
		self.EXIT_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT",    ()).upper() + u"</font>"
		
		self.TOC_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_CONTENTS", ()).upper() + u"</font>"
		self.INDEX_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_INDEX",  ()).upper() + u"</font>"
		eYellow = gc.getInfoTypeForString("COLOR_YELLOW")
		self.TOC_ACTIVE_TEXT = u"<font=4>"  + localText.getColorText("TXT_KEY_PEDIA_SCREEN_CONTENTS", (), eYellow).upper() + u"</font>"
		self.INDEX_ACTIVE_TEXT = u"<font=4>"  + localText.getColorText("TXT_KEY_PEDIA_SCREEN_INDEX",  (), eYellow).upper() + u"</font>"

		# <!-- custom: add highlight text for sevopedia sorting needs as we added but anyways etc, here fetched once for performance optimization or/and such if i'm not mistaken anyways etc. -->
		self.COLOR_HIGHLIGHT_TEXT = gc.getInfoTypeForString('COLOR_HIGHLIGHT_TEXT')
		self.IS_SAS_SEVOPEDIA_MAIN_CIVICS_GROUP_BY_CIVIC_TYPES = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_CIVICS_GROUP_BY_CIVIC_TYPES") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_TECHS_GROUP_BY_ERA = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_TECHS_GROUP_BY_ERA") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_BUILDINGS_GROUP_BY_ERA = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_BUILDINGS_GROUP_BY_ERA") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_UNITS_GROUP_BY_ERA = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_UNITS_GROUP_BY_ERA") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_CORPORATIONS_GROUP_BY_ERA = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_CORPORATIONS_GROUP_BY_ERA") > 0)

		self.szCategoryTechs		= localText.getText("TXT_KEY_PEDIA_CATEGORY_TECH", ())
		self.szCategoryUnits		= localText.getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ())
		self.szCategoryUnitUpgrades	= localText.getText("TXT_KEY_PEDIA_CATEGORY_UNIT_UPGRADES", ())
		self.szCategoryUnitCategories	= localText.getText("TXT_KEY_PEDIA_CATEGORY_UNIT_COMBAT", ())
		self.szCategoryPromotions	= localText.getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION", ())
		self.szCategoryPromotionTree	= localText.getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION_TREE", ())
		self.szCategoryBuildings	= localText.getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ())
		self.szCategoryNationalWonders	= localText.getText("TXT_KEY_PEDIA_CATEGORY_NATIONAL_WONDERS", ())
		self.szCategoryWorldWonders	= localText.getText("TXT_KEY_PEDIA_CATEGORY_WORLD_WONDERS", ())
		self.szCategoryProjects		= localText.getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ())
		self.szCategorySpecialists	= localText.getText("TXT_KEY_PEDIA_CATEGORY_SPECIALIST", ())
		self.szCategoryTerrains		= localText.getText("TXT_KEY_PEDIA_CATEGORY_TERRAIN", ())
		self.szCategoryFeatures		= localText.getText("TXT_KEY_PEDIA_CATEGORY_FEATURE", ())
		self.szCategoryBonuses		= localText.getText("TXT_KEY_PEDIA_CATEGORY_BONUS", ())
		self.szCategoryImprovements	= localText.getText("TXT_KEY_PEDIA_CATEGORY_IMPROVEMENT", ())
		self.szCategoryCivs			= localText.getText("TXT_KEY_PEDIA_CATEGORY_CIV", ())
		self.szCategoryLeaders		= localText.getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ())
		# advc.004y: Restored
		self.szCategoryTraits		= localText.getText("TXT_KEY_PEDIA_TRAITS", ())
		self.szCategoryCivics		= localText.getText("TXT_KEY_PEDIA_CATEGORY_CIVIC", ())
		self.szCategoryReligions	= localText.getText("TXT_KEY_PEDIA_CATEGORY_RELIGION", ())
		self.szCategoryCorporations	= localText.getText("TXT_KEY_CONCEPT_CORPORATIONS", ())
		self.szCategoryConcepts		= localText.getText("TXT_KEY_PEDIA_CATEGORY_CONCEPT", ())
		self.szCategoryConceptsNew	= localText.getText("TXT_KEY_PEDIA_CATEGORY_CONCEPT_NEW", ())
		self.szCategoryHints		= localText.getText("TXT_KEY_PEDIA_CATEGORY_HINTS", ())
		self.szCategoryShortcuts	= localText.getText("TXT_KEY_PEDIA_CATEGORY_SHORTCUTS", ())
		
		self.categoryList = [
			["TECHS",	self.szCategoryTechs],
			["UNITS",	self.szCategoryUnits],
			["UNITS",	self.szCategoryUnitUpgrades],
			["UNITS",	self.szCategoryUnitCategories],
			["PROMOTIONS",	self.szCategoryPromotions],
			["PROMOTIONS",	self.szCategoryPromotionTree],
			["BUILDINGS",	self.szCategoryBuildings],
			["BUILDINGS",	self.szCategoryNationalWonders],
			["BUILDINGS",	self.szCategoryWorldWonders],
			["BUILDINGS",	self.szCategoryProjects],
			["SPECIALISTS",	self.szCategorySpecialists],
			["TERRAINS",	self.szCategoryTerrains],
			["TERRAINS",	self.szCategoryFeatures],
			["TERRAINS",	self.szCategoryBonuses],
			["TERRAINS",	self.szCategoryImprovements],
			["CIVS",	self.szCategoryCivs],
			["CIVS",	self.szCategoryLeaders],
			# advc.004y: Restored (comment this out to remove traits)
			["CIVS",	self.szCategoryTraits],
			["CIVICS",	self.szCategoryCivics],
			["CIVICS",	self.szCategoryReligions],
			["CIVICS",	self.szCategoryCorporations],
			["HINTS",	self.szCategoryConcepts],
			["HINTS",	self.szCategoryConceptsNew],
			["HINTS",	self.szCategoryHints],
			["HINTS",	self.szCategoryShortcuts], # advc.004y: Restored
			]

		self.categoryGraphics = {
			"TECHS"		: u"%c  " %(gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar()),
			"UNITS"		: u"%c  " %(CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR)),
			"PROMOTIONS"	: u"%c  " %(CyGame().getSymbolID(FontSymbols.SILVER_STAR_CHAR)),
			"BUILDINGS"	: u"%c  " %(gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar()),
			"SPECIALISTS"	: u"%c  " %(CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR)),
			"TERRAINS"	: u"%c  " %(gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar()),
			"CIVS"		: u"%c  " %(CyGame().getSymbolID(FontSymbols.MAP_CHAR)),
			"CIVICS"	: u"%c  " %(gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar()),
			"HINTS"		: u"%c  " %(gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getChar()),
			}

		screen = self.getScreen()
		screen.setRenderInterfaceOnly(True)
		screen.setScreenGroup(1)
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
		# advc.001: Was getInterfaceArtInfo("SCREEN_BG_OPAQUE"), meaning that self.INTERFACE_ART_INFO was ignored. The original Civilopedia has the same bug fwiw.
		screen.addDDSGFC(self.BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo(self.INTERFACE_ART_INFO).getPath(), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPanel(self.TOP_PANEL_ID, u"", u"", True, False, self.X_TOP_PANEL, self.Y_TOP_PANEL, self.W_TOP_PANEL, self.H_TOP_PANEL, PanelStyles.PANEL_STYLE_TOPBAR)
		screen.addPanel(self.BOT_PANEL_ID, u"", u"", True, False, self.X_BOT_PANEL, self.Y_BOT_PANEL, self.W_BOT_PANEL, self.H_BOT_PANEL, PanelStyles.PANEL_STYLE_BOTTOMBAR)
		# <advc.004y>
		X_SCREEN = self.HORIZONTAL_MARGIN
		Y_SCREEN = self.BOTTOM_MARGIN
		if not self.bWideScreen:
			X_SCREEN = screen.centerX(0)
		if not self.bFullScreen:
			Y_SCREEN = screen.centerY(0)
		# </advc.004y>
		screen.setDimensions(X_SCREEN, Y_SCREEN, self.W_SCREEN, self.H_SCREEN)

		screen.setText(self.HEAD_ID, "Background", self.HEAD_TEXT, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE, self.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
		screen.setText(self.BACK_ID, "Background", self.BACK_TEXT, CvUtil.FONT_LEFT_JUSTIFY,   self.X_BACK,  self.Y_BACK,  0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_BACK,    1, -1)
		screen.setText(self.NEXT_ID, "Background", self.NEXT_TEXT, CvUtil.FONT_LEFT_JUSTIFY,   self.X_NEXT,  self.Y_NEXT,  0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_FORWARD, 1, -1)
		screen.setText(self.EXIT_ID, "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY,  self.X_EXIT,  self.Y_EXIT,  0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1)



	def placeCategories(self, iCategory=None):
		screen = self.getScreen()
		screen.addListBoxGFC(self.CATEGORY_LIST_ID, "", self.X_CATEGORIES, self.Y_CATEGORIES, self.W_CATEGORIES, self.H_CATEGORIES, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(self.CATEGORY_LIST_ID, True)
		screen.setStyle(self.CATEGORY_LIST_ID, "Table_StandardCiv_Style")
		screen.clearListBoxGFC(self.CATEGORY_LIST_ID)
		for i, category in enumerate(self.categoryList):
			graphic = self.categoryGraphics[category[0]]
			# <advc.002b> Prepend graphic only if there is room
			szHeading = category[1]
			# For English, 16 happens to be OK.
			# <!-- custom: allow room to fit more characters; our
			# text "Concepts (Outdated)" doesn't fit otherwise.
			#
			# Not increasing this further to accomodate the -1 for
			# other languages, as they are unlikely to use such long
			# texts anyway, and i really need or/and want the extra
			# space (that is not so useful in categories headers
			# i think, but anyways), was 16
			# --> 
			iThresh = 19
			if gc.getGame().getCurrentLanguage() != 0:
				# <!-- custom: was 15 -->
				iThresh = 19
			if len(szHeading) <= iThresh:
				szHeading = graphic + szHeading # </advc.002b>
			screen.appendListBoxStringNoUpdate(self.CATEGORY_LIST_ID, szHeading, WidgetTypes.WIDGET_PEDIA_MAIN, SevoScreenEnums.PEDIA_MAIN + i + 1, 0, CvUtil.FONT_LEFT_JUSTIFY)
		screen.updateListBox(self.CATEGORY_LIST_ID)


	# Helper to group techs by era (single-pass bucketing).
	# Yep — techs are the easiest one to refactor “like buildings/units”, because a tech already has its era (getEra()), so we just do a single pass, bucket into groups[iEra], then emit era headers in era order.
	def SAS_getTechsGroupedByEra(self):
		techsList = []

		iNumEras = gc.getNumEraInfos()
		groups = {}  # iEra -> [(szName, iTech), ...]

		# One pass over TechInfos preserves XML order when Sort Lists is OFF
		iNumTechs = gc.getNumTechInfos()
		for iTech in range(iNumTechs):
			info = gc.getTechInfo(iTech)
			if info.isGraphicalOnly():
				continue

			iEra = info.getEra()
			szName = info.getDescription()

			if iEra not in groups:
				groups[iEra] = []
			groups[iEra].append((szName, iTech))

		# Optional sorting within each era group
		if self.isSortLists():
			for k in groups.keys():
				groups[k].sort()

		# Emit era groups in order
		for iEra in range(iNumEras):
			tmp = groups.get(iEra, None)
			if not tmp:
				continue

			if techsList:
				techsList.append(("", -1))  # spacer between eras
			techsList.append((gc.getEraInfo(iEra).getDescription() + " " + localText.getText("TXT_KEY_PEDIA_ERA", ()), -1))

			for x in tmp:
				techsList.append(x)

		return tuple(techsList)

	def placeTechs(self):
		self.list = self.getTechList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, gc.getTechInfo)

		# <!-- custom: similarly to how we did in placeLeaders, precompute only once the list as string of untradeable techs for display in sevopedia tech, since it is always the same, and precompute it only after first time list is displayed so it is smoother/faster maybe even if a bit if not a lot but anyways etc anyways etc anyways etc ; also do not build it needlessly if we never access sevopedia tech same as in/for the leaders_info_cached code but anyways etc -->
		if not self.IS_UNTRADEABLE_TECHS_TEXT_PREBUILT:
			SevoPediaTech.UNTRADEABLE_TECHS_TEXT = SevoPediaTech.getPrecomputedUntradeableTechsText()
			self.IS_UNTRADEABLE_TECHS_TEXT_PREBUILT = True
			print("Sevopedia Tech Untradeable techs list prebuilt from Sevopedia Main. This should appear only once even if we exit sevopedia entirely, as long as we are during the same gaming session (i.e. game was not exited) (for info, in SevopediaMain, self.IS_UNTRADEABLE_TECHS_TEXT_PREBUILT=%s)." % str(self.IS_UNTRADEABLE_TECHS_TEXT_PREBUILT))
	
	def getTechList(self):
		if self.IS_SAS_SEVOPEDIA_MAIN_TECHS_GROUP_BY_ERA:
			if self.SAS_cacheTechsTuple is None:
				self.SAS_cacheTechsTuple = self.SAS_getTechsGroupedByEra()
			return self.SAS_cacheTechsTuple
		else:
			if self.SAS_cacheTechsTuple is None:
				# <!-- custom: base advciv's formula, only difference is we cache it now if i'm not mistaken anyways etc. -->
				self.SAS_cacheTechsTuple = tuple(self.getSortedList(gc.getNumTechInfos(), gc.getTechInfo))
			return self.SAS_cacheTechsTuple


	def placeUnits(self):
		self.list = self.getUnitList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, gc.getUnitInfo)

	# Compute the "availability era" for a unit, factoring in unit tech prereqs, prereq building tech, and religion founding tech (if any).
	def SAS_getUnitAvailabilityEra(self, iUnit, iNumUnitAndTechs, iNumBuildingAndTechs):
		info = gc.getUnitInfo(iUnit)
		if not info or info.isGraphicalOnly():
			return None  # caller should skip

		iEra = -1

		# Unit tech prereqs: <PrereqTech> + <TechTypes>
		iTech = info.getPrereqAndTech()
		if iTech >= 0:
			iEra = gc.getTechInfo(iTech).getEra()

		for j in range(iNumUnitAndTechs):
			iTech2 = info.getPrereqAndTechs(j)
			if iTech2 >= 0:
				iEra2 = gc.getTechInfo(iTech2).getEra()
				if iEra2 > iEra:
					iEra = iEra2

		# PrereqBuilding availability era (reuses our building-era helper, so it includes SpecialBuilding tech + religion tech, etc.)
		iPrereqBuilding = info.getPrereqBuilding()
		if iPrereqBuilding >= 0:
			iBuildingEra = self.SAS_getBuildingAvailabilityEra(iPrereqBuilding, iNumBuildingAndTechs)
			if iBuildingEra is not None and iBuildingEra > iEra:
				iEra = iBuildingEra

		# PrereqReligion tech prereq (religion founding tech).
		# (Mostly redundant for missionaries in your setup since they already require a monastery building, but harmless and fixes any unit that uses PrereqReligion without a building gate.)
		iPrereqReligion = info.getPrereqReligion()
		if iPrereqReligion >= 0:
			iReligionTech = gc.getReligionInfo(iPrereqReligion).getTechPrereq()
			if iReligionTech >= 0:
				iReligionEra = gc.getTechInfo(iReligionTech).getEra()
				if iReligionEra > iEra:
					iEra = iReligionEra

		# <!-- custom: note: executives's tech actual requirement not implemented here, as in advciv-sas they also have a prereq tech (see XML code comments or main changes guide or such for rationale anyways etc.). Otherwise the implementation so they are listed at e.g. "Industrial" Era and not "No Tech Prerequisite" (which does not reflect their effective ingame availabilty: not until later eras) would be tedious from what i understand of chatgpt 5.2's explanation and solution (plus we don't need to so better not anyways etc.); check if accurate anyways etc. -->
		# Yes — for your mod, adding a tech prereq directly on Executive units is the simplest and arguably the cleanest fix, and it also matches the design logic you already used for shrines (“captured thing exists locally, but you can’t mass-produce/spread it without understanding the tech”).

		return iEra  # -1 means "no tech prereq bucket"

	# Helper we can reuse for units.
	def SAS_getUnitsGroupedByEra_fromBaseList(self, baseList):
		unitsList = []

		iNumEras = gc.getNumEraInfos()
		iNumUnitAndTechs = gc.getNUM_UNIT_AND_TECH_PREREQS()
		iNumBuildingAndTechs = gc.getNUM_BUILDING_AND_TECH_PREREQS()

		noTech = []
		groups = {}  # iEra -> [(szName, iUnit), ...]

		# One pass: compute era once and bucket
		for (szName, iUnit) in baseList:
			iEra = self.SAS_getUnitAvailabilityEra(iUnit, iNumUnitAndTechs, iNumBuildingAndTechs)
			if iEra is None:
				continue

			if iEra == -1:
				noTech.append((szName, iUnit))
			else:
				if iEra not in groups:
					groups[iEra] = []
				groups[iEra].append((szName, iUnit))

		# Optional sorting within each bucket
		if self.isSortLists():
			noTech.sort()
			for k in groups.keys():
				groups[k].sort()

		# "No Tech Prerequisite" group first
		if noTech:
			unitsList.append((localText.getText("TXT_KEY_PEDIA_NO_TECH_PREREQUISITE", ()), -1))
			for x in noTech:
				unitsList.append(x)

		# Era groups in order
		for iEraLoop in range(iNumEras):
			tmp = groups.get(iEraLoop, None)
			if not tmp:
				continue

			if unitsList:
				unitsList.append(("", -1))

			unitsList.append((gc.getEraInfo(iEraLoop).getDescription() + " " + localText.getText("TXT_KEY_PEDIA_ERA", ()), -1))
			for x in tmp:
				unitsList.append(x)

		return tuple(unitsList)

	# <!-- custom: similarly, in sevopedia units, group units by era (based on prereq tech) instead of one long list. Code added with the help of chatgpt 5.2 thanks anyways etc. -->
	def getUnitList(self):
		if self.IS_SAS_SEVOPEDIA_MAIN_UNITS_GROUP_BY_ERA:
			if self.SAS_cacheUnitsTuple is None:
				baseList = self.getSortedList(gc.getNumUnitInfos(), gc.getUnitInfo)
				self.SAS_cacheUnitsTuple = self.SAS_getUnitsGroupedByEra_fromBaseList(baseList)
			return self.SAS_cacheUnitsTuple

		else:
			if self.SAS_cacheUnitsTuple is None:
				self.SAS_cacheUnitsTuple = tuple(self.getSortedList(gc.getNumUnitInfos(), gc.getUnitInfo))
			return self.SAS_cacheUnitsTuple


	def placeUnitUpgrades(self):
		screen = self.getScreen()
		self.getScreen().deleteWidget("PediaMainItemList")
		self.UPGRADES_GRAPH_ID = self.getNextWidgetName()
		screen.addScrollPanel(self.UPGRADES_GRAPH_ID, u"", self.X_ITEMS, self.Y_PEDIA_PAGE - 13, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 2, PanelStyles.PANEL_STYLE_STANDARD)
		screen.setActivation(self.UPGRADES_GRAPH_ID, ActivationTypes.ACTIVATE_NORMAL)
		upgradesGraph = UnitUpgradesGraph.UnitUpgradesGraph(self)
		upgradesGraph.getGraph()
		upgradesGraph.drawGraph()


	def placeUnitCategories(self):
		self.list = self.getUnitCategoryList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, gc.getUnitCombatInfo)
	
	def getUnitCategoryList(self):
		return self.getSortedList(gc.getNumUnitCombatInfos(), gc.getUnitCombatInfo)


	def placePromotions(self):
		self.list = self.getPromotionList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, gc.getPromotionInfo)
	
	def getPromotionList(self):
		return self.getSortedList(gc.getNumPromotionInfos(), gc.getPromotionInfo)


	def placePromotionTree(self):
		screen = self.getScreen()
		self.getScreen().deleteWidget("PediaMainItemList")
		self.UPGRADES_GRAPH_ID = self.getNextWidgetName()
		screen.addScrollPanel(self.UPGRADES_GRAPH_ID, u"", self.X_ITEMS, self.Y_PEDIA_PAGE - 13, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 2, PanelStyles.PANEL_STYLE_STANDARD)
		screen.setActivation(self.UPGRADES_GRAPH_ID, ActivationTypes.ACTIVATE_NORMAL)
		upgradesGraph = UnitUpgradesGraph.PromotionsGraph(self)
		upgradesGraph.getGraph()
		upgradesGraph.drawGraph()


	# Compute the "availability era" for a building, factoring in tech prereqs, special building tech, and religion founding tech.
	def SAS_getBuildingAvailabilityEra(self, iBuilding, iNumAndTechs):
		info = gc.getBuildingInfo(iBuilding)
		if not info or info.isGraphicalOnly():
			return None  # caller should skip

		iEra = -1

		# Main AND prereq tech (<PrereqTech>)
		# <!-- custom: it seems getPrereqOrTechs does not exist causing a python error, but with the help of chatgpt 5.2 found the correct way to fetch tech prereqs that addresses and fixes it and that works as intended in displaying the building at latest tech prereq of the building's corresponding era. Seems to run fine in testing/empirically, check if accurate anyways etc. -->
		# When first implementing era-tiered building lists, we hit a crash: AttributeError: 'CvBuildingInfo' object has no attribute 'getPrereqOrTechs' (Python traceback from SevoPediaMain.getBuildingList). We verified the cause by inspecting our exported Cy/Cv infos (as of now __SevoPediaBuilding-gc-inner-debug-content.txt and __SevoPediaBuilding-gc-debug-content.txt): CvBuildingInfo in this DLL exposes getPrereqAndTech() + getPrereqAndTechs(i), but NOT getPrereqOrTechs(i) (unlike some other mods / DLLs). (Mapping to our XML schema: <PrereqTech> maps to getPrereqAndTech(), and <TechTypes><PrereqTech>...</PrereqTech></TechTypes> maps to getPrereqAndTechs(i).)
		# Fix: compute the building "availability era" using only these AND-tech prereqs: start with getPrereqAndTech(), then scan additional prereqs via getPrereqAndTechs(i) for i in range(gc.getNUM_BUILDING_AND_TECH_PREREQS()). We bucket the building into the LATEST (max) era among these prereq techs, so it shows up in the era when it actually becomes buildable.
		# Empirical sanity check: we tested a building with two widely separated PrereqTech and TechTypes (e.g. TECH_MATHEMATICS (Classical) and TECH_FUSION (Future)) in both permutations (A then B, and B then A), and in both cases the building was listed under the later era (Future), confirming the "max era of prereqs" rule behaves correctly in practice.
		# Additional sanity check: we also tested <PrereqTech>NONE</PrereqTech> with an existing TechTypes prereq (i.e. only the <TechTypes> prereq was set), and the building was still listed under the correct era, confirming the fallback scan of getPrereqAndTechs(i) works even when the main <PrereqTech> is NONE. -->
		iTech = info.getPrereqAndTech()
		if iTech >= 0:
			iEra = gc.getTechInfo(iTech).getEra()

		# Extra AND tech prereqs (<TechTypes><PrereqTech>...)
		for j in range(iNumAndTechs):
			iTech2 = info.getPrereqAndTechs(j)
			if iTech2 >= 0:
				iEra2 = gc.getTechInfo(iTech2).getEra()
				if iEra2 > iEra:
					iEra = iEra2

		# SpecialBuilding tech prereq (eg monasteries gated by SPECIALBUILDING tech)
		# <!-- custom: special buildings need also to be checked for a tech prereq. For example the buddhist monastery as of now has no TechPrereq and TechTypes NONE, but the parent specialbuilding_monastery requires TECH_MONARCHY. Yet, without taking special buildings into account, the buddhist monastery is incorrectly listed at the "No Tech Prereq" part instead of at the "Classical Era" part. Fix this by taking their actual tech prereq into account properly with the help of chatgpt 5.2 thanks anyways etc. -->
		# Yep — that’s exactly why: for “special buildings” (Temple/Cathedral/Monastery/etc.), the real tech gate often lives in CIV4SpecialBuildingInfos.xml (e.g. SPECIALBUILDING_MONASTERY has TechPrereq = TECH_MONARCHY). So your era-bucketing currently sees “no building tech prereq” and dumps it into All Eras.
		# Also consider SpecialBuilding tech prereq (e.g. Monastery -> TECH_MONARCHY in CIV4SpecialBuildingInfos.xml)
		iSpecialBuildingType = info.getSpecialBuildingType()
		if iSpecialBuildingType >= 0:
			iSpecialTech = gc.getSpecialBuildingInfo(iSpecialBuildingType).getTechPrereq()
			if iSpecialTech >= 0:
				iSpecialEra = gc.getTechInfo(iSpecialTech).getEra()
				if iSpecialEra > iEra:
					iEra = iSpecialEra

		# Also consider PrereqReligion tech prereq (religion founding tech).
		# Example: Islamic Temple may have no building tech prereq, but RELIGION_ISLAM is founded by TECH_LATER_ABRAHAMISM (Medieval Era), so the building effectively cannot exist before that era (except via conquest/trade of a religion-enabled city).
		iPrereqReligion = info.getPrereqReligion()
		if iPrereqReligion >= 0:
			iReligionTech = gc.getReligionInfo(iPrereqReligion).getTechPrereq()
			if iReligionTech >= 0:
				iReligionEra = gc.getTechInfo(iReligionTech).getEra()
				if iReligionEra > iEra:
					iEra = iReligionEra

		return iEra  # -1 means "no tech prereq bucket"

	# <!-- custom: helper we can reuse for regular buildings, national wonders, world wonders, with the help of chatgpt 5.2 thanks anyways etc. -->
	def SAS_getBuildingsGroupedByEra_fromBaseList(self, baseList):
		buildingsList = []

		iNumEras = gc.getNumEraInfos()
		iNumAndTechs = gc.getNUM_BUILDING_AND_TECH_PREREQS()

		noTech = []
		groups = {}  # iEra -> [(szName, iBuilding), ...]

		# One pass: compute era once and bucket
		for (szName, iBuilding) in baseList:
			iEra = self.SAS_getBuildingAvailabilityEra(iBuilding, iNumAndTechs)
			if iEra is None:
				continue  # graphical-only or invalid

			if iEra == -1:
				noTech.append((szName, iBuilding))
			else:
				if iEra not in groups:
					groups[iEra] = []
				groups[iEra].append((szName, iBuilding))

		# Optional sorting within each bucket
		if self.isSortLists():
			noTech.sort()
			for k in groups.keys():
				groups[k].sort()

		# "No Tech Prereq" group first
		if noTech:
			buildingsList.append((localText.getText("TXT_KEY_PEDIA_NO_TECH_PREREQUISITE", ()), -1))
			for x in noTech:
				buildingsList.append(x)

		# Era groups in order
		for iEraLoop in range(iNumEras):
			tmp = groups.get(iEraLoop, None)
			if not tmp:
				continue

			if buildingsList:
				buildingsList.append(("", -1))

			buildingsList.append((gc.getEraInfo(iEraLoop).getDescription() + " " + localText.getText("TXT_KEY_PEDIA_ERA", ()), -1))
			for x in tmp:
				buildingsList.append(x)

		return tuple(buildingsList)


	def placeBuildings(self):
		self.list = self.getBuildingList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)
	
	# <!-- custom: similarly, in sevopedia buildings, group techs by era (based on prereq tech) instead of one long list. Code added with the help of chatgpt 5.2 thanks anyways etc. -->
	def getBuildingList(self):
		if self.IS_SAS_SEVOPEDIA_MAIN_BUILDINGS_GROUP_BY_ERA:
			if self.SAS_cacheRegularBuildingsTuple is None:
				baseList = self.pediaBuilding.getBuildingSortedList(0)
				self.SAS_cacheRegularBuildingsTuple = self.SAS_getBuildingsGroupedByEra_fromBaseList(baseList)
			return self.SAS_cacheRegularBuildingsTuple
		else:
			if self.SAS_cacheRegularBuildingsTuple is None:
				self.SAS_cacheRegularBuildingsTuple = tuple(self.pediaBuilding.getBuildingSortedList(0))
			return self.SAS_cacheRegularBuildingsTuple


	def placeNationalWonders(self):
		self.list = self.getNationalWonderList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)
	
	# <!-- custom: also group them by era (tech prereq) with the help of chatgpt 5.2 thanks anyways etc. -->
	def getNationalWonderList(self):
		if self.IS_SAS_SEVOPEDIA_MAIN_BUILDINGS_GROUP_BY_ERA:
			if self.SAS_cacheNationalWondersTuple is None:
				baseList = self.pediaBuilding.getBuildingSortedList(1)
				self.SAS_cacheNationalWondersTuple = self.SAS_getBuildingsGroupedByEra_fromBaseList(baseList)
			return self.SAS_cacheNationalWondersTuple
		else:
			if self.SAS_cacheNationalWondersTuple is None:
				self.SAS_cacheNationalWondersTuple = tuple(self.pediaBuilding.getBuildingSortedList(1))
			return self.SAS_cacheNationalWondersTuple


	def placeWorldWonders(self):
		self.list = self.getWorldWonderList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)

	# <!-- custom: also group them by era (tech prereq) with the help of chatgpt 5.2 thanks anyways etc. -->	
	def getWorldWonderList(self):
		if self.IS_SAS_SEVOPEDIA_MAIN_BUILDINGS_GROUP_BY_ERA:
			if self.SAS_cacheWorldWondersTuple is None:
				baseList = self.pediaBuilding.getBuildingSortedList(2)
				self.SAS_cacheWorldWondersTuple = self.SAS_getBuildingsGroupedByEra_fromBaseList(baseList)
			return self.SAS_cacheWorldWondersTuple
		else:
			if self.SAS_cacheWorldWondersTuple is None:
				self.SAS_cacheWorldWondersTuple = tuple(self.pediaBuilding.getBuildingSortedList(2))
			return self.SAS_cacheWorldWondersTuple


	def placeProjects(self):
		self.list = self.getProjectList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, gc.getProjectInfo)
	
	def getProjectList(self):
		return self.getSortedList(gc.getNumProjectInfos(), gc.getProjectInfo)


	def placeSpecialists(self):
		self.list = self.getSpecialistList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPECIALIST, gc.getSpecialistInfo)
	
	def getSpecialistList(self):
		return self.getSortedList(gc.getNumSpecialistInfos(), gc.getSpecialistInfo)


	def placeTerrains(self):
		self.list = self.getTerrainList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, gc.getTerrainInfo)
	
	def getTerrainList(self):
		# <!-- custom: add peak and hill to terrain display even though they are plot types if i am not mistaken but with the changes in sevopedia terrain (new placeRelevantUnits and placeUnitsImpassable panels as of now anyways etc), these still provide very valuable info so adding them helps a lot anyways etc ; code provided by chatgpt thanks to my prompt too and previous reworks i did with it or with claude ai or and such and myself too if i adjusted it a bit or lot or not adjusted but in all cases anyways etc anyways etc thanks anyways etc anyways etc anyways etc -->
		terrainsList = self.getSortedList(gc.getNumTerrainInfos(), gc.getTerrainInfo)

		# Add Hill as a pseudo-entry
		iHill = getInfoTypeOrFail("TERRAIN_HILL", gc)
		terrainsList.append((gc.getTerrainInfo(iHill).getDescription(), iHill))

		# Add Peak as a pseudo-entry
		iPeak = getInfoTypeOrFail("TERRAIN_PEAK", gc)
		terrainsList.append((gc.getTerrainInfo(iPeak).getDescription(), iPeak))

		return terrainsList


	def placeFeatures(self):
		self.list = self.getFeatureList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE, gc.getFeatureInfo)

		# <!-- custom: quite similarly if i may say but anyways etc to other precompute codes in sevopedia main, also do sevopedia bonus's pre-loading logic at time where it is more/most efficient if i may say but anyways etc anyways etc anyways etc -->
		if not self.IS_FEATURES_PRE_LOADING_XML_DATA_VALIDATION_DONE:
			SevoPediaFeature.do_pre_load_xml_features_info_required_data_validation()
			self.IS_FEATURES_PRE_LOADING_XML_DATA_VALIDATION_DONE = True
			print("Sevopedia Feature pre load XML data validation done from Sevopedia Main. This should appear only once even if we exit sevopedia entirely, as long as we are during the same gaming session (i.e. game was not exited) (for info, in SevopediaMain, self.IS_FEATURES_PRE_LOADING_XML_DATA_VALIDATION_DONE=%s)." % str(self.IS_FEATURES_PRE_LOADING_XML_DATA_VALIDATION_DONE))
	
	def getFeatureList(self):
		return self.getSortedList(gc.getNumFeatureInfos(), gc.getFeatureInfo)


	def placeBonuses(self):
		self.list = self.getBonusList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, gc.getBonusInfo)
	
	def getBonusList(self):
		return self.getSortedList(gc.getNumBonusInfos(), gc.getBonusInfo)


	def placeImprovements(self):
		self.list = self.getImprovementList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, gc.getImprovementInfo)
	
	def getImprovementList(self):
		imprList = self.getSortedList(gc.getNumImprovementInfos(), gc.getImprovementInfo)
		# <advc.004y>
		r = []
		for descr,i in imprList:
			info = gc.getImprovementInfo(i)
			# The alt. conditions are for Forest Preserve and Fort
			if info.getPillageGold() > 0 or info.isRequiresFeature() or info.isOutsideBorders():
				r.append((descr,i))
		return r # </advc.004y>


	def placeCivs(self):
		self.list = self.getCivilizationList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, gc.getCivilizationInfo)
	
	def getCivilizationList(self):
		civList = self.getSortedList(gc.getNumCivilizationInfos(), gc.getCivilizationInfo)
		# <advc.004y> Filter out minor civ, but not Barbarians (which do have
		# sensible strategy text). Distinguish b/w them by checking for
		# free Palace. Not sure if that's really better than using
		#gc.getInfoTypeForString("CIVILIZATION_MINOR")
		r = []
		for descr,i in civList:
			# <!-- custom: reveal minor nation, i want all information available in the sevopedia. May also be useful for other
			# mods. -->
			#info = gc.getCivilizationInfo(i)
			#if not info.isPlayable():
			#	iCapitalBuildingClass = gc.getDefineINT("CAPITAL_BUILDINGCLASS")
			#	if (iCapitalBuildingClass >= 0 and
			#	info.isCivilizationFreeBuildingClass(iCapitalBuildingClass)):
			#		continue
			r.append((descr,i))
		return r # </advc.004y>


	def placeLeaders(self):
		self.list = self.getLeaderList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, gc.getLeaderHeadInfo)

		# <!-- custom: prebuild the sevopedia leader cache only when=after anyways etc we click on leaders button, so that if we open sevopedia and never access the leaders page, we don't compute needlessly a cached leader that is quite expensive or even if not too much needless and not optimal i think but anyways etc. After asking chatgpt, it advised me to do this here anyways etc ; note: place it after the list is computed so it doesn't appear to hang (in case it does, didn't test or look in detail anyways etc) sometime on Leaders click before the items are placed: cache after leader items are place to avoid that, then the user has some time to click to desired leader, use that time to cache smoothly maybe and silently maybe anyways etc -->
		if not self.IS_SEVOPEDIALEADER_CACHE_PREBUILT:
			SevoPediaLeader.LEADERS_INFO_CACHED, SevoPediaLeader.AI_RIGHT_CATEGORIES, SevoPediaLeader.AI_MIDDLE_CATEGORIES, SevoPediaLeader.AI_LEFT_CATEGORIES = SevoPediaLeader.getPrecomputedCacheOnceOnlyFromSevopediaMainInSevopediaLeaderForEntireSession()
			# <!-- custom: do not rebuild if built once already, for the entire session keep the same cache, even if we exit sevopedia, store data in memory or wherever it is stored anyways etc, but do not build it until we click on leaders category the first time, not at module load (so a bit later than module load and not automatic but conditional in this case anyways etc), but still before any leader is selected if i am not mistaken too anyways etc -->
			self.IS_SEVOPEDIALEADER_CACHE_PREBUILT = True
			print("Sevopedia Leader cache prebuilt from Sevopedia Main. This should appear only once even if we exit sevopedia entirely, as long as we are during the same gaming session (i.e. game was not exited) (for info, in SevopediaMain, self.IS_SEVOPEDIALEADER_CACHE_PREBUILT=%s)." % str(self.IS_SEVOPEDIALEADER_CACHE_PREBUILT))
	
	def getLeaderList(self):
		# <advc.004y>
		r = self.getSortedList(gc.getNumLeaderHeadInfos(), gc.getLeaderHeadInfo)
		# Barbs should be in position 0, but use WonderConstructRand to confirm.
		if len(r) > 0 and gc.getLeaderHeadInfo(r[0][1]).getWonderConstructRand() <= 0:
			r.pop(0)
		return r # </advc.004y>


	def placeTraits(self):
		self.list = self.getTraitList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getTraitInfo)
	
	def getTraitList(self):
		return self.getSortedList(gc.getNumNewConceptInfos(), self.getTraitInfo, True, False) # advc.004y: bCheckGraphicalOnly = False

	def getTraitInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if self.isTraitInfo(info):
			
			class TraitInfo:
				def __init__(self, conceptInfo):
					self.conceptInfo = conceptInfo
					sKey = conceptInfo.getType()
					sKey = sKey[sKey.find("TRAIT_"):]
					self.eTrait = gc.getInfoTypeForString(sKey)
					self.traitInfo = gc.getTraitInfo(self.eTrait)
				def getDescription(self):
					return u"%c %s" % (TraitUtil.getIcon(self.eTrait), self.traitInfo.getDescription())
				def getButton(self):
					return self.traitInfo.getButton()
			
			return TraitInfo(info)
		return None
	
	def isTraitInfo(self, info):
		return info.getType().find("_TRAIT_") != -1

	# <!-- custom: helper we can reuse for civics grouping, with the help of chatgpt 5.2 thanks anyways etc. -->
	def SAS_getCivicsGroupedByCivicOption(self):
		civicsList = []
		iNumCivics = gc.getNumCivicInfos()
		iNumOptions = gc.getNumCivicOptionInfos()

		# One pass: bucket civics by option (preserves XML order naturally)
		groups = [[] for _ in range(iNumOptions)]
		for iCivic in range(iNumCivics):
			info = gc.getCivicInfo(iCivic)
			if info.isGraphicalOnly():
				continue
			iOption = info.getCivicOptionType()
			if iOption >= 0 and iOption < iNumOptions:
				groups[iOption].append((info.getDescription(), iCivic))

		# Emit in option order (Government, Legal, Labor, etc.)
		for iOption in range(iNumOptions):
			tmp = groups[iOption]
			if not tmp:
				continue

			# If BUG "Sort Lists" is ON, alphabetize within each option group
			if self.isSortLists():
				tmp.sort()

			if civicsList:
				civicsList.append(("", -1))  # spacer between groups
			civicsList.append((gc.getCivicOptionInfo(iOption).getDescription(), -1))  # header

			for x in tmp:
				civicsList.append(x)

		return tuple(civicsList)

	def placeCivics(self):
		self.list = self.getCivicList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, gc.getCivicInfo)

	# <!-- custom: in sevopedia civics, order civics by civic type (e.g. Government, Economy, etc.), as RFC DOC mod does and that this code is based on, with the help of chatgpt 5.2 thanks anyways etc. -->
	# Step 2: Replace getCivicList() with “category + era tiers” (behind a SAS define)
	# Right now your civics list is just getSortedList(gc.getNumCivicInfos(), gc.getCivicInfo) (optionally alphabetical via BUG).
	# In RFC DoC, placeCivics() at least groups by civic option category using header rows. They also show how they do era tier grouping for other lists (e.g., wonders/buildings grouped by prereq tech era).
	def getCivicList(self):
		if self.IS_SAS_SEVOPEDIA_MAIN_CIVICS_GROUP_BY_CIVIC_TYPES:
			if self.SAS_cacheCivicsTuple is None:
				self.SAS_cacheCivicsTuple = self.SAS_getCivicsGroupedByCivicOption()
			return self.SAS_cacheCivicsTuple
		# <!-- custom: else no grouping, full alphabetical ordered list cached as a tuple, using the base advciv's list formula but anyways etc. -->
		else:
			if self.SAS_cacheCivicsTuple is None:
				self.SAS_cacheCivicsTuple = tuple(self.getSortedList(gc.getNumCivicInfos(), gc.getCivicInfo))
			return self.SAS_cacheCivicsTuple


	def placeReligions(self):
		self.list = self.getReligionList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, gc.getReligionInfo)
	
	def getReligionList(self):
		return self.getSortedList(gc.getNumReligionInfos(), gc.getReligionInfo)

	# In AdvCiv-SAS, your corporations are effectively gated by the founding building (the BUILDING_CORPORATION_X that has <FoundsCorporation>CORPORATION_X</FoundsCorporation> and has <PrereqTech> / <TechTypes>), while the corresponding CIV4CorporationInfo.xml often has <TechPrereq>NONE</TechPrereq>. So the clean “era” for a corporation should be the availability era of its founding building.
	# This reuses your existing SAS_getBuildingAvailabilityEra(iBuilding, iNumAndTechs) helper (the one that already accounts for SpecialBuilding tech + religion founding tech).
	# Map each corporation to its founding (HQ) building once, then reuse; used for grouping corporations by era.
	def SAS_getCorporationHQBuilding(self, iCorporation):
		if self.SAS_cacheCorporationHQBuildingByCorp is None:
			m = {}
			for iBuilding in range(gc.getNumBuildingInfos()):
				bInfo = gc.getBuildingInfo(iBuilding)
				if not bInfo or bInfo.isGraphicalOnly():
					continue
				iFounds = bInfo.getFoundsCorporation()
				if iFounds >= 0:
					m[iFounds] = iBuilding
			self.SAS_cacheCorporationHQBuildingByCorp = m
		return self.SAS_cacheCorporationHQBuildingByCorp.get(iCorporation, -1)

	# Compute the "availability era" for a corporation, based on its founding building's prereq tech era.
	def SAS_getCorporationAvailabilityEra(self, iCorporation, iNumBuildingAndTechs):
		cInfo = gc.getCorporationInfo(iCorporation)
		if not cInfo or cInfo.isGraphicalOnly():
			return None  # caller should skip

		iEra = -1

		# In AdvCiv-SAS, corporations are typically gated by the founding building techs (see CIV4BuildingInfos.xml <FoundsCorporation>).
		iHQBuilding = self.SAS_getCorporationHQBuilding(iCorporation)
		if iHQBuilding >= 0:
			iBuildingEra = self.SAS_getBuildingAvailabilityEra(iHQBuilding, iNumBuildingAndTechs)
			if iBuildingEra is not None and iBuildingEra > iEra:
				iEra = iBuildingEra

		return iEra  # -1 means "No Tech Prerequisite" bucket

	# Helper to group corporations by era for Sevopedia lists, mirroring the building/unit/tech patterns.
	def SAS_getCorporationsGroupedByEra_fromBaseList(self, baseList):
		corpsList = []

		iNumEras = gc.getNumEraInfos()
		iNumBuildingAndTechs = gc.getNUM_BUILDING_AND_TECH_PREREQS()

		noTech = []
		groups = {}  # iEra -> [(szName, iCorporation), ...]

		for (szName, iCorporation) in baseList:
			iEra = self.SAS_getCorporationAvailabilityEra(iCorporation, iNumBuildingAndTechs)
			if iEra is None:
				continue

			if iEra == -1:
				noTech.append((szName, iCorporation))
			else:
				if iEra not in groups:
					groups[iEra] = []
				groups[iEra].append((szName, iCorporation))

		if self.isSortLists():
			noTech.sort()
			for k in groups.keys():
				groups[k].sort()

		if noTech:
			corpsList.append((localText.getText("TXT_KEY_PEDIA_NO_TECH_PREREQUISITE", ()), -1))
			for x in noTech:
				corpsList.append(x)

		for iEraLoop in range(iNumEras):
			tmp = groups.get(iEraLoop, None)
			if not tmp:
				continue

			if corpsList:
				corpsList.append(("", -1))

			corpsList.append((gc.getEraInfo(iEraLoop).getDescription() + " " + localText.getText("TXT_KEY_PEDIA_ERA", ()), -1))
			for x in tmp:
				corpsList.append(x)

		return tuple(corpsList)

	def placeCorporations(self):
		self.list = self.getCorporationList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION, gc.getCorporationInfo)
	
	# <!-- custom: similarly, in sevopedia corporations, group corporations by era (based on founding building prereq tech era) instead of one long list. Code added with the help of chatgpt 5.2 thanks anyways etc. -->
	def getCorporationList(self):
		if self.IS_SAS_SEVOPEDIA_MAIN_CORPORATIONS_GROUP_BY_ERA:
			if self.SAS_cacheCorporationsTuple is None:
				baseList = self.getSortedList(gc.getNumCorporationInfos(), gc.getCorporationInfo)
				self.SAS_cacheCorporationsTuple = self.SAS_getCorporationsGroupedByEra_fromBaseList(baseList)
			return self.SAS_cacheCorporationsTuple
		else:
			if self.SAS_cacheCorporationsTuple is None:
				self.SAS_cacheCorporationsTuple = tuple(self.getSortedList(gc.getNumCorporationInfos(), gc.getCorporationInfo))
			return self.SAS_cacheCorporationsTuple

	def placeConcepts(self):
		self.list = self.getConceptList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, gc.getConceptInfo)
	
	def getConceptList(self):
		return self.getSortedList(gc.getNumConceptInfos(), gc.getConceptInfo)


	def placeBTSConcepts(self):
		self.list = self.getNewConceptList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getNewConceptInfo)
	
	def getNewConceptList(self):
		return self.getSortedList(gc.getNumNewConceptInfos(), self.getNewConceptInfo)

	def getNewConceptInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if not self.isShortcutInfo(info) and not self.isTraitInfo(info):
			return info
		return None


	def placeHints(self):
		screen = self.getScreen()
		self.getScreen().deleteWidget("PediaMainItemList")
		# <advc.004y> Put a Blue50-styled panel behind the ListBox below, using the same dimensions.
		screen.addPanel(self.getNextWidgetName(), "", "", false, false,
			self.X_ITEMS, self.Y_PEDIA_PAGE - 10, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 23, PanelStyles.PANEL_STYLE_BLUE50)
		# </advc.004y>
		szHintBox = self.getNextWidgetName()
		screen.addListBoxGFC(szHintBox, "", self.X_ITEMS, self.Y_PEDIA_PAGE - 10, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 23, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(szHintBox, False)
		szHintsText = CyGameTextMgr().buildHintsList()
		# <!-- custom: no need to import string module just to split a string, use native code instead if i am not mistaken and as per chatgpt's explanation and what i understood of it anyways etc -->
		hintText = szHintsText.split("\n")
		for hint in hintText:
			if len(hint) != 0:
				screen.appendListBoxStringNoUpdate(szHintBox, hint, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.updateListBox(szHintBox)


	def placeShortcuts(self):
		self.list = self.getSortedList(gc.getNumNewConceptInfos(), self.getShortcutInfo)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getShortcutInfo)

	def getShortcutInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if self.isShortcutInfo(info):
			return info
		return None
	
	def isShortcutInfo(self, info):
		return info.getType().find("SHORTCUTS") != -1

	
	def placeItems(self, widget, info):
		screen = self.getScreen()
		screen.clearListBoxGFC(self.ITEM_LIST_ID)

		screen.addTableControlGFC(self.ITEM_LIST_ID, 1, self.X_ITEMS, self.Y_ITEMS, self.W_ITEMS, self.H_ITEMS, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(self.ITEM_LIST_ID, False)
		screen.setStyle(self.ITEM_LIST_ID, "Table_StandardCiv_Style")
		screen.setTableColumnHeader(self.ITEM_LIST_ID, 0, "", self.W_ITEMS)

		i = 0
		for item in self.list:
			data1 = item[1] # advc.001: Moved up

			# <!-- custom: make a common initial variable so we can tweak it in specific elif or such blocks as we see fit and keep common logic at the end anyways etc; using a long name to avoid weird python scope inheritance issues to unrelated scopes if i'm not mistaken anyways etc. -->
			sTitlePlaceItems = item[0]
			widgetPlaceItems = widget
			# Even though you later handle data1 == -1 inside the civics block, you still do szButtonPlaceItems = info(item[1]).getButton() before any header check.
			# When getCivicList() inserts headers and spacers, you now have rows like ("Government", -1) and ("", -1). So you end up calling gc.getCivicInfo(-1).getButton() and Civ4 blows up with Access violation - no RTTI data!. Minimal fix:
			if data1 != -1:
				szButtonPlaceItems = info(data1).getButton()
			else:
				szButtonPlaceItems = ""

			if info == gc.getConceptInfo:
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT
				# <!-- custom: we cannot change to data1 here as we changed it in this scope so need to properly use item[1] rather as chatgpt 5.2 recommends and that indeed lead to an issue ingame of displaying always same sevopedia concept's text but anyways etc. To be safe, not changing it in other places as well unless we need to anyways etc. -->
				data2 = item[1]

			elif info == self.getNewConceptInfo or info == self.getShortcutInfo or info == self.getTraitInfo: # advc
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW
				data2 = item[1]

			# <advc.001> Widget help for leaders needs the civ ID in data2 (from Taurus)
			elif (info == gc.getLeaderHeadInfo):
				data2 = SevoPediaLeader.SevoPediaLeader.getCiv(item[1]) # </advc.001>

			else:
				# advc (note): 0 tends to mean no tooltip (or an empty one?).
				#    -1 should also work as the default; BULL likes to use 1.
				data2 = 1

				# <!-- custom: in sevopedia civics, order civics by civic type (e.g. Government, Economy, etc.), as RFC DOC mod does and that this code is based on, with the help of chatgpt 5.2 thanks anyways etc. -->
				# Step 1 (required): Teach your SevoPediaMain.placeItems() to handle headers
				# Right now your placeItems() always does info(item[1]).getButton(), so any header rows like ("Government", -1) would crash. RFC DoC fixes this by treating item[1] == -1 as a non-clickable, highlighted header row.
				# <!-- custom: similarly, in sevopedia techs, group techs by era (e.g. Ancient Era, Classical Era, etc.) instead of one long list. Also did similarly for sevopedia buildings and similar pages anyways etc. Code added with the help of chatgpt 5.2 thanks anyways etc. -->
				# (That is basically the DoC approach, adapted to your variable names.). After this, your item lists can safely contain (..., -1) headers and blank separators.
				if data1 == -1:
					sTitlePlaceItems = CyTranslator().changeTextColor(item[0], self.COLOR_HIGHLIGHT_TEXT)
					widgetPlaceItems = WidgetTypes.WIDGET_GENERAL
					szButtonPlaceItems = ""

			screen.appendTableRow(self.ITEM_LIST_ID)
			screen.setTableText(self.ITEM_LIST_ID, 0, i, u"<font=3>" + sTitlePlaceItems + u"</font>", szButtonPlaceItems, widgetPlaceItems, data1, data2, CvUtil.FONT_LEFT_JUSTIFY)
			i += 1
		#screen.updateListBox(self.ITEM_LIST_ID)



	def back(self):
		if (len(self.pediaHistory) > 1):
			self.pediaFuture.append(self.pediaHistory.pop())
			current = self.pediaHistory.pop()
			self.pediaJump(current[0], current[1], False, True)
		return 1



	def forward(self):
		if (self.pediaFuture):
			current = self.pediaFuture.pop()
			self.pediaJump(current[0], current[1], False, True)
		return 1



	def link(self, szLink):
		if (szLink == "PEDIA_MAIN_TECH"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_TECHS, True, True)
		elif (szLink == "PEDIA_MAIN_UNIT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_UNITS, True, True)
		elif (szLink == "PEDIA_MAIN_UNIT_GROUP"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_UNIT_CATEGORIES, True, True)
		elif (szLink == "PEDIA_MAIN_PROMOTION"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_PROMOTIONS, True, True)
		elif (szLink == "PEDIA_MAIN_BUILDING"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_BUILDINGS, True, True)
		elif (szLink == "PEDIA_MAIN_PROJECT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_PROJECTS, True, True)
		elif (szLink == "PEDIA_MAIN_SPECIALIST"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_SPECIALISTS, True, True)
		elif (szLink == "PEDIA_MAIN_TERRAIN"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_TERRAINS, True, True)
		elif (szLink == "PEDIA_MAIN_FEATURE"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_FEATURES, True, True)
		elif (szLink == "PEDIA_MAIN_BONUS"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_BONUSES, True, True)
		elif (szLink == "PEDIA_MAIN_IMPROVEMENT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_IMPROVEMENTS, True, True)
		elif (szLink == "PEDIA_MAIN_CIV"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_CIVS, True, True)
		elif (szLink == "PEDIA_MAIN_LEADER"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_LEADERS, True, True)
		elif (szLink == "PEDIA_MAIN_TRAIT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_TRAITS, True, True)
		elif (szLink == "PEDIA_MAIN_CIVIC"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_CIVICS, True, True)
		elif (szLink == "PEDIA_MAIN_RELIGION"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_RELIGIONS, True, True)
		elif (szLink == "PEDIA_MAIN_CONCEPT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_CONCEPTS, True, True)
		elif (szLink == "PEDIA_MAIN_HINTS"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_HINTS, True, True)
		elif (szLink == "PEDIA_MAIN_SHORTCUTS"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_SHORTCUTS, True, True)

		for i in range(gc.getNumTechInfos()):
			if (gc.getTechInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_TECHS, i, True, True)
		for i in range(gc.getNumUnitInfos()):
			if (gc.getUnitInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_UNITS, i, True, True)
		for i in range(gc.getNumUnitCombatInfos()):
			if (gc.getUnitCombatInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_UNIT_CATEGORIES, i, True, True)
		for i in range(gc.getNumPromotionInfos()):
			if (gc.getPromotionInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_PROMOTIONS, i, True, True)
		for i in range(gc.getNumBuildingInfos()):
			if (gc.getBuildingInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_BUILDINGS, i, True, True)
		for i in range(gc.getNumProjectInfos()):
			if (gc.getProjectInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_PROJECTS, i, True, True)
		for i in range(gc.getNumSpecialistInfos()):
			if (gc.getSpecialistInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_SPECIALISTS, i, True, True)
		for i in range(gc.getNumTerrainInfos()):
			if (gc.getTerrainInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_TERRAINS, i, True, True)
		for i in range(gc.getNumFeatureInfos()):
			if (gc.getFeatureInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_FEATURES, i, True, True)
		for i in range(gc.getNumBonusInfos()):
			if (gc.getBonusInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_BONUSES, i, True, True)
		for i in range(gc.getNumImprovementInfos()):
			if (gc.getImprovementInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_IMPROVEMENTS, i, True, True)
		for i in range(gc.getNumCivilizationInfos()):
			if (gc.getCivilizationInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_CIVS, i, True, True)
		for i in range(gc.getNumLeaderHeadInfos()):
			if (gc.getLeaderHeadInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_LEADERS, i, True, True)
		for i in range(gc.getNumCivicInfos()):
			if (gc.getCivicInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_CIVICS, i, True, True)
		for i in range(gc.getNumReligionInfos()):
			if (gc.getReligionInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_RELIGIONS, i, True, True)
		for i in range(gc.getNumCorporationInfos()):
			if (gc.getCorporationInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_CORPORATIONS, i, True, True)
		for i in range(gc.getNumConceptInfos()):
			if (gc.getConceptInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_CONCEPTS, i, True, True)
		for i in range(gc.getNumNewConceptInfos()):
			if (gc.getNewConceptInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_BTS_CONCEPTS, i, True, True)



	def handleInput (self, inputClass):
		if (inputClass.getPythonFile() == SevoScreenEnums.PEDIA_LEADERS):
			return self.pediaLeader.handleInput(inputClass)
		elif (inputClass.getFunctionName() == self.TOC_ID):
			self.showContents()
			return 1
		elif (inputClass.getFunctionName() == self.INDEX_ID):
			self.showIndex()
			return 1
		elif (self.isIndexShowing()):
			return self.pediaIndex.handleInput(inputClass)
		
		return 0



	def deleteAllWidgets(self):
		screen = self.getScreen()
		iNumWidgets = self.nWidgetCount
		self.nWidgetCount = 0
		for i in range(iNumWidgets):
			screen.deleteWidget(self.getNextWidgetName())
		self.nWidgetCount = 0

	def deleteListWidgets(self):
		screen = self.getScreen()
		screen.deleteWidget("PediaMainCategoryList")
		screen.deleteWidget("PediaMainItemList")

	def getNextWidgetName(self):
		szName = self.WIDGET_ID + str(self.nWidgetCount)
		self.nWidgetCount += 1
		return szName


	def isSortLists(self):
		return AdvisorOpt.SevopediaSortItemList()

	# advc.004y: bCheckGraphicalOnly flag added (for CvInfo types that don't have that element)
	def getSortedList(self, numInfos, getInfo, noSort=False, bCheckGraphicalOnly = True):
		list = []
		for i in range(numInfos):
			item = getInfo(i)
			# advc.004y: GraphicalOnly check added
			if item and (not bCheckGraphicalOnly or not item.isGraphicalOnly()):
				list.append((item.getDescription(), i))
		if self.isSortLists() and not noSort:
			list.sort()
		return list

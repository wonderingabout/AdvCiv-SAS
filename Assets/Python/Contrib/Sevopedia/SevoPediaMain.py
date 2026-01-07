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
import SevoPediaHandicapChart
import SevoPediaGameSpeedChart
import SevoPediaWorldSizeChart
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
		self.SAS_USE_BOTTOM_TABS = False

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

		# <!-- custom: type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->
		self.SAS_SEARCH_PANEL_ID = "PediaMainSearchPanel"
		self.SAS_SEARCH_LABEL_ID = "PediaMainSearchLabel"
		self.SAS_SEARCH_CLEAR_ID = "PediaMainSearchClear"
		self.SAS_SEARCH_DEFAULT_TEXT = u"Type to filter..."
		self.SAS_SEARCH_H = 32
		# <!-- custom: End - type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->

		self.H_SCREEN = 768
		self.W_SCREEN = 1024

		# <advc.004y>
		self.bWideScreen = True
		self.bFullScreen = True
		if self.bFullScreen:
			self.bWideScreen = True
		# <!-- custom: Not much value in being able to see the elements at the edge parts of the screen, however i think the extra room can be useful to fit more data or simply enlarge the view, hopefully making it all clearer and more pleasant to see. Other mods use the entire screen for the sevopedia if i'm not mistaken and i like it fine, tested in AdvCiv-SAS and i like it very much, so removing margins now. -->
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
		self.iCategory = -1
		self.iItem = -1
		self.iItemIndex = -1
		self.pediaHistory = []
		self.pediaFuture = []

		# <!-- custom: compute once to be computationally more efficient if i'm not mistaken in my thinking, and added with the help of chatgpt 5.2 thanks. -->
		self.SAS_cacheCivicsTuple = None
		self.SAS_cacheTechsTuple = None
		self.SAS_cacheRegularBuildingsTuple = None
		self.SAS_cacheNationalWondersTuple = None
		self.SAS_cacheWorldWondersTuple = None
		self.SAS_cacheUnitsTuple = None
		self.SAS_cacheCorporationsTuple = None
		self.SAS_cacheCorporationHQBuildingByCorp = None
		self.SAS_cacheReligionsTuple = None
		self.SAS_cacheProjectsTuple = None
		self.SAS_cacheSpecialistsTuple = None
		self.SAS_cacheBonusesTuple = None
		self.SAS_cacheImprovementsTuple = None
		self.SAS_cacheTerrainsTuple = None
		self.SAS_cacheFeaturesTuple = None

		# <!-- custom: type-to-filter search bar state variables (chatgpt 5.2 + claude opus 4.5) -->
		self.SAS_szSearchString = u""
		self.SAS_lastItemsWidget = None
		self.SAS_lastItemsInfo = None

		# <!-- custom: debounce for type-to-filter to prevent double keypress even when key-up events are interleaved (chatgpt 5.2 + claude opus 4.5) -->
		# Note: BtS/AdvCiv can fire NOTIFY_CHARACTER twice per press for letters/digits, and the 2nd event can arrive after another key when typing fast.
		self.SAS_keyDebounceByKey = {}

		# <!-- custom: map original list indices to displayed rows when filtering so selection/highlight stays correct (chatgpt 5.2 + claude opus 4.5) -->
		self.SAS_listIdxToRow = None
		# <!-- custom: End - type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->

		# <!-- custom: cache selectable (non-header) indices for arrow navigation (chatgpt 5.2 + claude opus 4.5) -->
		self.SAS_selectableListIdx = []
		self.SAS_itemToSelectablePos = {}

		# <!-- custom: do not build sevopedia leader cache until we click on the leaders category, so that if we never open at all the leaders category, no need to compute needlessly for their cache. And if we do access the leaders page, then building once the cache is enough for the entire session, no need to rebuild it even if we exit sevopedia. Therefore store the cache in sevopedia leader, but add a flag to not build cache at module load of sevopedia leader, but later on click in/at placeLeaders time if i am not mistaken and from what i understand of chatgpt's explanation. -->
		self.IS_SEVOPEDIALEADER_CACHE_PREBUILT = False
		# <!-- custom: do something similar for the untradeable techs text and or such other similar or quite similar codes. -->
		self.IS_UNTRADEABLE_TECHS_TEXT_PREBUILT = False
		self.IS_FEATURES_PRE_LOADING_XML_DATA_VALIDATION_DONE = False

		self.pediaBuilding	= SevoPediaBuilding.SevoPediaBuilding(self)
		self.pediaLeader	= SevoPediaLeader.SevoPediaLeader(self)
		self.pediaIndex     = SevoPediaIndex.SevoPediaIndex(self)
		# <!-- custom: keep a shared handicap chart instance so its internal table cache survives between openings. (GPT-5.2-Codex) -->
		self.pediaHandicapChart = SevoPediaHandicapChart.SevoPediaHandicapChart(self)
		# <!-- custom: keep a shared game speed chart instance so its internal table cache survives between openings. (GPT-5.2-Codex) -->
		self.pediaGameSpeedChart = SevoPediaGameSpeedChart.SevoPediaGameSpeedChart(self)
		self.pediaWorldSizeChart = SevoPediaWorldSizeChart.SevoPediaWorldSizeChart(self)

		# <!-- custom: category list refactor: previously category order, list generators, screen handlers, and link keys
		# lived in separate maps and hardcoded blocks, so reordering or adding a category required edits in multiple places
		# and could desync labels from links; now a single SAS_CATEGORY_DEFS tuple is the source of truth.
		# This makes category edits safer (one-row change), easier to review, and less error-prone, while keeping the same
		# runtime behavior and allowing explicit per-category icons without fallback/group logic.
		# Icons are computed once here and embedded in the tuple, so they are not global state and don't depend on later setup.
		# To add or reorder, edit SAS_CATEGORY_DEFS only; maps, list generators, and PEDIA_MAIN links update automatically.
		# (GPT-5.2-Codex (summarized)) -->
		iconTech = u"%c  " % (gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar())
		iconUnit = u"%c  " % (CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR))
		iconPromo = u"%c  " % (CyGame().getSymbolID(FontSymbols.SILVER_STAR_CHAR))
		iconBldg = u"%c  " % (gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar())
		iconSpec = u"%c  " % (CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR))
		iconTerrain = u"%c  " % (gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar())
		iconCiv = u"%c  " % (CyGame().getSymbolID(FontSymbols.MAP_CHAR))
		iconCivic = u"%c  " % (gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar())
		iconHint = u"%c  " % (gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getChar())
		iconSas = u"%c  " % (CyGame().getSymbolID(FontSymbols.DEFENSE_CHAR))

		# <!-- custom: central category wiring for list generators, screen handlers, and PEDIA_MAIN links.
		# To add a category, insert one row in SAS_CATEGORY_DEFS: (PEDIA_ENUM, TXT_KEY, icon, listMethodName, screenClassOrInstance, PEDIA_MAIN_LINK_KEY or None).
		# Example: (SevoScreenEnums.PEDIA_TECHS, "TXT_KEY_PEDIA_CATEGORY_TECH", iconTech, "placeTechs", SevoPediaTech.SevoPediaTech, "PEDIA_MAIN_TECH")
		# Reorder by moving rows here; no other maps or link tables need edits. (GPT-5.2-Codex) -->
		self.SAS_CATEGORY_DEFS = (
			(SevoScreenEnums.PEDIA_INDEX, "TXT_KEY_PEDIA_SCREEN_INDEX", iconHint, "placeIndexCategory", None, None),
			(SevoScreenEnums.PEDIA_HANDICAP_CHART, "TXT_KEY_PEDIA_SAS_CATEGORY_HANDICAP_CHART", iconSas, "placeHandicapChart", self.pediaHandicapChart, None),
			(SevoScreenEnums.PEDIA_GAME_SPEED_CHART, "TXT_KEY_PEDIA_SAS_CATEGORY_GAME_SPEED_CHART", iconSas, "placeGameSpeedChart", self.pediaGameSpeedChart, None),
			(SevoScreenEnums.PEDIA_WORLD_SIZE_CHART, "TXT_KEY_PEDIA_SAS_CATEGORY_WORLD_SIZE_CHART", iconSas, "placeWorldSizeChart", self.pediaWorldSizeChart, None),
			(SevoScreenEnums.PEDIA_TERRAINS, "TXT_KEY_PEDIA_CATEGORY_TERRAIN", iconTerrain, "placeTerrains", SevoPediaTerrain.SevoPediaTerrain, "PEDIA_MAIN_TERRAIN"),
			(SevoScreenEnums.PEDIA_FEATURES, "TXT_KEY_PEDIA_CATEGORY_FEATURE", iconTerrain, "placeFeatures", SevoPediaFeature.SevoPediaFeature, "PEDIA_MAIN_FEATURE"),
			(SevoScreenEnums.PEDIA_BONUSES, "TXT_KEY_PEDIA_CATEGORY_BONUS", iconTerrain, "placeBonuses", SevoPediaBonus.SevoPediaBonus, "PEDIA_MAIN_BONUS"),
			(SevoScreenEnums.PEDIA_IMPROVEMENTS, "TXT_KEY_PEDIA_CATEGORY_IMPROVEMENT", iconTerrain, "placeImprovements", SevoPediaImprovement.SevoPediaImprovement, "PEDIA_MAIN_IMPROVEMENT"),
			(SevoScreenEnums.PEDIA_UNITS, "TXT_KEY_PEDIA_CATEGORY_UNIT", iconUnit, "placeUnits", SevoPediaUnit.SevoPediaUnit, "PEDIA_MAIN_UNIT"),
			(SevoScreenEnums.PEDIA_UNIT_UPGRADES, "TXT_KEY_PEDIA_CATEGORY_UNIT_UPGRADES", iconUnit, "placeUnitUpgrades", None, None),
			(SevoScreenEnums.PEDIA_UNIT_CATEGORIES, "TXT_KEY_PEDIA_CATEGORY_UNIT_COMBAT", iconUnit, "placeUnitCategories", SevoPediaUnitChart.SevoPediaUnitChart, "PEDIA_MAIN_UNIT_GROUP"),
			(SevoScreenEnums.PEDIA_PROMOTIONS, "TXT_KEY_PEDIA_CATEGORY_PROMOTION", iconPromo, "placePromotions", SevoPediaPromotion.SevoPediaPromotion, "PEDIA_MAIN_PROMOTION"),
			(SevoScreenEnums.PEDIA_PROMOTION_TREE, "TXT_KEY_PEDIA_CATEGORY_PROMOTION_TREE", iconPromo, "placePromotionTree", None, None),
			(SevoScreenEnums.PEDIA_BUILDINGS, "TXT_KEY_PEDIA_CATEGORY_BUILDING", iconBldg, "placeBuildings", self.pediaBuilding, "PEDIA_MAIN_BUILDING"),
			(SevoScreenEnums.PEDIA_NATIONAL_WONDERS, "TXT_KEY_PEDIA_CATEGORY_NATIONAL_WONDERS", iconBldg, "placeNationalWonders", SevoPediaBuilding.SevoPediaBuilding, None),
			(SevoScreenEnums.PEDIA_WORLD_WONDERS, "TXT_KEY_PEDIA_CATEGORY_WORLD_WONDERS", iconBldg, "placeWorldWonders", SevoPediaBuilding.SevoPediaBuilding, None),
			(SevoScreenEnums.PEDIA_PROJECTS, "TXT_KEY_PEDIA_CATEGORY_PROJECT", iconBldg, "placeProjects", SevoPediaProject.SevoPediaProject, "PEDIA_MAIN_PROJECT"),
			(SevoScreenEnums.PEDIA_SPECIALISTS, "TXT_KEY_PEDIA_CATEGORY_SPECIALIST", iconSpec, "placeSpecialists", SevoPediaSpecialist.SevoPediaSpecialist, "PEDIA_MAIN_SPECIALIST"),
			(SevoScreenEnums.PEDIA_CIVS, "TXT_KEY_PEDIA_CATEGORY_CIV", iconCiv, "placeCivs", SevoPediaCivilization.SevoPediaCivilization, "PEDIA_MAIN_CIV"),
			(SevoScreenEnums.PEDIA_LEADERS, "TXT_KEY_PEDIA_CATEGORY_LEADER", iconCiv, "placeLeaders", self.pediaLeader, "PEDIA_MAIN_LEADER"),
			# advc.004y: Restored (comment this out to remove traits)
			(SevoScreenEnums.PEDIA_TRAITS, "TXT_KEY_PEDIA_TRAITS", iconCiv, "placeTraits", SevoPediaTrait.SevoPediaTrait, "PEDIA_MAIN_TRAIT"),
			(SevoScreenEnums.PEDIA_CIVICS, "TXT_KEY_PEDIA_CATEGORY_CIVIC", iconCivic, "placeCivics", SevoPediaCivic.SevoPediaCivic, "PEDIA_MAIN_CIVIC"),
			(SevoScreenEnums.PEDIA_RELIGIONS, "TXT_KEY_PEDIA_CATEGORY_RELIGION", iconCivic, "placeReligions", SevoPediaReligion.SevoPediaReligion, "PEDIA_MAIN_RELIGION"),
			(SevoScreenEnums.PEDIA_CORPORATIONS, "TXT_KEY_CONCEPT_CORPORATIONS", iconCivic, "placeCorporations", SevoPediaCorporation.SevoPediaCorporation, None),
			(SevoScreenEnums.PEDIA_TECHS, "TXT_KEY_PEDIA_CATEGORY_TECH", iconTech, "placeTechs", SevoPediaTech.SevoPediaTech, "PEDIA_MAIN_TECH"),
			(SevoScreenEnums.PEDIA_CONCEPTS, "TXT_KEY_PEDIA_CATEGORY_CONCEPT", iconHint, "placeConcepts", SevoPediaHistory.SevoPediaHistory, "PEDIA_MAIN_CONCEPT"),
			(SevoScreenEnums.PEDIA_BTS_CONCEPTS, "TXT_KEY_PEDIA_CATEGORY_CONCEPT_NEW", iconHint, "placeBTSConcepts", SevoPediaHistory.SevoPediaHistory, None),
			(SevoScreenEnums.PEDIA_HINTS, "TXT_KEY_PEDIA_CATEGORY_HINTS", iconHint, "placeHints", SevoPediaHistory.SevoPediaHistory, "PEDIA_MAIN_HINTS"),
			(SevoScreenEnums.PEDIA_SHORTCUTS, "TXT_KEY_PEDIA_CATEGORY_SHORTCUTS", iconHint, "placeShortcuts", SevoPediaHistory.SevoPediaHistory, "PEDIA_MAIN_SHORTCUTS"),
			)

		self.mapListGenerators = {}
		self.mapScreenFunctions = {}
		self.SAS_mainLinkToCategory = {}
		for iEnum, szLabelKey, szIconGroup, szListMethod, screenSpec, szLinkKey in self.SAS_CATEGORY_DEFS:
			if szListMethod:
				self.mapListGenerators[iEnum] = getattr(self, szListMethod)
			if screenSpec:
				if screenSpec in (self.pediaBuilding, self.pediaLeader, self.pediaHandicapChart, self.pediaGameSpeedChart, self.pediaWorldSizeChart):
					self.mapScreenFunctions[iEnum] = screenSpec
				else:
					self.mapScreenFunctions[iEnum] = screenSpec(self)
			if szLinkKey:
				self.SAS_mainLinkToCategory[szLinkKey] = iEnum



	# <!-- custom: type-to-filter search bar helper methods (chatgpt 5.2 + claude opus 4.5) -->
	def SAS_safeDeleteWidget(self, screen, szWidget):
		try:
			screen.deleteWidget(szWidget)
		except:
			pass

	# <!-- custom: type-to-filter search bar helper methods (chatgpt 5.2 + claude opus 4.5) -->
	def SAS_deleteSearchWidgets(self):
		screen = self.getScreen()
		self.SAS_safeDeleteWidget(screen, self.SAS_SEARCH_PANEL_ID)
		self.SAS_safeDeleteWidget(screen, self.SAS_SEARCH_LABEL_ID)
		self.SAS_safeDeleteWidget(screen, self.SAS_SEARCH_CLEAR_ID)

	# <!-- custom: type-to-filter search bar helper methods (chatgpt 5.2 + claude opus 4.5) -->
	def SAS_isSearchActive(self):
		return (self.SAS_szSearchString is not None and len(self.SAS_szSearchString.strip()) > 0)

	# <!-- custom: type-to-filter search bar sync panel (chatgpt 5.2 + claude opus 4.5) -->
	def SAS_syncSearchPanel(self):
		screen = self.getScreen()

		# Recreate each time: simple + safe (mirrors the approach used in other mod(s)).
		self.SAS_deleteSearchWidgets()

		iX = self.X_ITEMS
		iY = self.Y_ITEMS
		iW = self.W_ITEMS
		iH = self.SAS_SEARCH_H

		screen.addPanel(self.SAS_SEARCH_PANEL_ID, u"", u"", True, True, iX, iY, iW, iH, PanelStyles.PANEL_STYLE_BLUE50)

		if self.SAS_isSearchActive():
			szText = self.SAS_szSearchString
		else:
			szText = self.SAS_SEARCH_DEFAULT_TEXT

		screen.setLabel(self.SAS_SEARCH_LABEL_ID, self.SAS_SEARCH_PANEL_ID,
				u"<font=3>%s</font>" % szText,
				CvUtil.FONT_LEFT_JUSTIFY, iX + 6, iY + 6, 0,
				FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# Show a clear button only when active.
		if self.SAS_isSearchActive():
			screen.setLabel(self.SAS_SEARCH_CLEAR_ID, self.SAS_SEARCH_PANEL_ID,
					u"<font=3>x</font>",
					CvUtil.FONT_RIGHT_JUSTIFY, iX + iW - 6, iY + 6, 0,
					FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

	# <!-- custom: convert InputTypes keyboard code to visible character, based on how other mod(s) use ScreenInput.getVisibleCharacter (chatgpt 5.2 + claude opus 4.5) -->

	# <!-- custom: identify keys that need debounce in the type-to-filter search (chatgpt 5.2 + claude opus 4.5) -->
	# We debounce only letters/digits. Space appears to be delivered only once in BtS/AdvCiv and should not be throttled.
	def SAS_shouldDebounceKey(self, iKey):
		# Letters A-Z
		if iKey >= int(InputTypes.KB_A) and iKey <= int(InputTypes.KB_Z):
			return True
		# Digits 0-9
		if iKey >= int(InputTypes.KB_0) and iKey <= int(InputTypes.KB_9):
			return True
		# Backspace (and optionally Delete) can also double-fire
		# No need for KB_DELETE or KB_RETURN since:
		# 	- Delete has nothing to do (no cursor position)
		# 	- Enter exits Sevopedia (default game behavior, not our code)
		if iKey == int(InputTypes.KB_BACKSPACE):
			return True

		# <!-- custom: Based on C2C mod's implementation thanks: add navigation of the item list with the UP/DOWN arrow keys. Code adjusted for AdvCiv-SAS with the help of chatgpt 5.2 and claude opus 4.5. -->
		if iKey == int(InputTypes.KB_UP) or iKey == int(InputTypes.KB_DOWN):
			return True
		# <!-- custom: End - Based on C2C mod's implementation thanks: add navigation of the item list with the UP/DOWN arrow keys. Code adjusted for AdvCiv-SAS with the help of chatgpt 5.2 and claude opus 4.5. -->

		return False

	def SAS_getVisibleCharacter(self, inputClass):
		iKey = inputClass.getData()
		bShift = inputClass.isShiftKeyDown()
		
		# Letters A-Z
		if iKey >= int(InputTypes.KB_A) and iKey <= int(InputTypes.KB_Z):
			iLetterOffset = iKey - int(InputTypes.KB_A)
			if bShift:
				return unichr(65 + iLetterOffset)  # Uppercase A-Z
			else:
				return unichr(97 + iLetterOffset)  # Lowercase a-z
		
		# Numbers 0-9
		if iKey >= int(InputTypes.KB_0) and iKey <= int(InputTypes.KB_9):
			iNumberOffset = iKey - int(InputTypes.KB_0)
			return unichr(48 + iNumberOffset)
		
		# Space
		if iKey == int(InputTypes.KB_SPACE):
			return u" "
		
		# No visible character for this key
		return u""
	# <!-- custom: End - type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->

	# <!-- custom: Based on C2C mod's implementation thanks: add navigation of the item list with the UP/DOWN arrow keys. Code adjusted for AdvCiv-SAS with the help of chatgpt 5.2 and claude opus 4.5. -->
	# Navigate the item list by iDirection rows (-1 = up, +1 = down). Skips headers/spacers (item[1] == -1) and respects filtering.
	def SAS_navigateItemList(self, iDirection):
		if not self.isContentsShowing():
			return False
		if not self.list or len(self.list) == 0:
			return False
		
		# Prefer cached selectable indices (built in placeItems)
		listSelectableRows = getattr(self, "SAS_selectableListIdx", None)
		if not listSelectableRows:
			# Fallback: old behavior (build by scanning)
			listSelectableRows = []
			for idx, item in enumerate(self.list):
				if item[1] == -1:
					continue
				if self.SAS_isSearchActive() and getattr(self, "SAS_listIdxToRow", None) is not None:
					if not self.SAS_listIdxToRow.has_key(idx):
						continue
				listSelectableRows.append(idx)

		if len(listSelectableRows) == 0:
			return False

		# O(1) lookup of current position if possible
		iCurrentPos = -1
		dPos = getattr(self, "SAS_itemToSelectablePos", None)
		if dPos is not None:
			iCurrentPos = dPos.get(self.iItem, -1)
		
		# Calculate new position
		if iCurrentPos == -1:
			# No item selected, select first or last based on direction
			if iDirection > 0:
				iNewPos = 0
			else:
				iNewPos = len(listSelectableRows) - 1
		else:
			iNewPos = iCurrentPos + iDirection
			# Clamp to valid range
			if iNewPos < 0:
				iNewPos = 0
			elif iNewPos >= len(listSelectableRows):
				iNewPos = len(listSelectableRows) - 1
		
		# Get the item at new position and jump to it
		iNewListIdx = listSelectableRows[iNewPos]
		iNewItem = self.list[iNewListIdx][1]
		
		if iNewItem != self.iItem:
			self.pediaJump(self.iCategory, iNewItem, False, False)
			return True
		
		return False
	# <!-- custom: End - Based on C2C mod's implementation thanks: add navigation of the item list with the UP/DOWN arrow keys. Code adjusted for AdvCiv-SAS with the help of chatgpt 5.2 and claude opus 4.5. -->


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
			# <!-- custom: default to the first row in SAS_CATEGORY_DEFS, so the opening category always
			# matches the current category order instead of being hardcoded to Techs. (GPT-5.2-Codex) -->
			self.pediaHistory.append((SevoScreenEnums.PEDIA_MAIN, self.SAS_CATEGORY_DEFS[0][0]))
		current = self.pediaHistory.pop()
		self.pediaFuture = []
		self.pediaHistory = []
		self.pediaJump(current[0], current[1], False, True)



	def pediaJump(self, iCategory, iItem, bRemoveFwdList, bIsLink):
		# <!-- custom: note: fixed a (seemingly base advciv) bug in in CvDLLWidgetData.cpp where iItem was -1 for obsolete bonuses redirecting from tech advisor, unlike obsolete buildings which didn't have the issue weirdly/strangely, with chatgpt's help and thanks to my prompt too and observation of the issue and or such but also chatgpt's help in guiding me bit too; i had put a workaround here to use a placeholder for iItem but no needed anymore now that this is fixed if i am not mistaken so reverted everything as base advciv code was minus this extra code comment, see also code comment at WIDGET_HELP_BONUS_REVEAL in CvDLLWidgetData.cpp or/and known issue number 22 as of now in known issues of advciv-sas readme for details as well. -->
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
			iListIndex = self.SAS_categoryEnumToIndex.get(iItem, -1)
			if iListIndex != -1:
				screen.setSelectedListBoxStringGFC(self.CATEGORY_LIST_ID, iListIndex)
			#self.iCategory = iItem
			return

		if (iCategory == SevoScreenEnums.PEDIA_BUILDINGS):
			iCategory += self.pediaBuilding.getBuildingType(iItem)
		elif (iCategory == SevoScreenEnums.PEDIA_BTS_CONCEPTS):
			iCategory = self.determineNewConceptSubCategory(iItem)
			BugUtil.debug("Switching to category %d" % iCategory)
		self.showContents(bIsLink, iCategory)
		iListIndex = self.SAS_categoryEnumToIndex.get(iCategory, -1)
		if iListIndex != -1:
			screen.setSelectedListBoxStringGFC(self.CATEGORY_LIST_ID, iListIndex)
		if (iCategory not in (SevoScreenEnums.PEDIA_UNIT_UPGRADES, SevoScreenEnums.PEDIA_PROMOTION_TREE, SevoScreenEnums.PEDIA_HINTS)):
			screen.enableSelect(self.ITEM_LIST_ID, True)
			if (self.iItemIndex != -1):
				BugUtil.debug("Deselecting item %d" % self.iItemIndex)
				screen.selectRow(self.ITEM_LIST_ID, self.iItemIndex, False)
			BugUtil.debug("Selecting item %d" % iItem)
			self.iItem = iItem
			for i, item in enumerate(self.list):
				if (item[1] == iItem):
					# <!-- custom: when filtering, select the displayed row, not the original list index (chatgpt 5.2 + claude opus 4.5) -->
					iRowToSelect = i
					if self.SAS_isSearchActive() and (self.SAS_listIdxToRow is not None):
						iRowToSelect = self.SAS_listIdxToRow.get(i, i)
					BugUtil.debug("Selecting %dth item %d (row %d)" % (i, iItem, iRowToSelect))
					#screen.setSelectedListBoxStringGFC(self.ITEM_LIST_ID, iRowToSelect)
					screen.selectRow(self.ITEM_LIST_ID, iRowToSelect, True)
					self.iItemIndex = iRowToSelect
					#break
					# <!-- custom: End - when filtering, select the displayed row, not the original list index (chatgpt 5.2 + claude opus 4.5) -->

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
	
	def showContents(self, bForce=False, iCategory=None):
		if iCategory is None:
			iCategory = self.SAS_CATEGORY_DEFS[0][0]
		self.pediaIndex.SAS_indexDeleteSearchWidgets()
		self.deleteAllWidgets()
		if not self.isContentsShowing():
			BugUtil.debug("Drawing category list")
			self.placeCategories(iCategory)
			screen = self.getScreen()
			if not self.SAS_USE_BOTTOM_TABS:
				self.SAS_safeDeleteWidget(screen, self.TOC_ID)
				self.SAS_safeDeleteWidget(screen, self.INDEX_ID)
			if self.SAS_USE_BOTTOM_TABS:
				screen.setText(self.TOC_ID, "Background", self.TOC_ACTIVE_TEXT,   CvUtil.FONT_LEFT_JUSTIFY,   self.X_TOC,   self.Y_TOC,   0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
				screen.setText(self.INDEX_ID, "Background", self.INDEX_TEXT, CvUtil.FONT_LEFT_JUSTIFY, self.X_INDEX, self.Y_INDEX, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
			screen.show(self.BACK_ID)
			screen.show(self.NEXT_ID)

		if not self.isContentsShowing() or self.iCategory != iCategory or bForce:
			BugUtil.debug("Drawing item list %d" % iCategory)
			# <!-- custom: type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->
			# <!-- custom: reset search state when changing category (chatgpt 5.2 + claude opus 4.5) -->
			self.SAS_lastItemsWidget = None
			self.SAS_lastItemsInfo = None
			if (not self.isContentsShowing()) or (self.iCategory != iCategory):
				self.SAS_szSearchString = u""
				# <!-- custom: reset debounce state when search is reset (chatgpt 5.2 + claude opus 4.5) -->
				self.SAS_keyDebounceByKey = {}
			# <!-- custom: End - type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->
			self.mapListGenerators.get(iCategory)()
			self.iCategory = iCategory
			self.iItem = -1
			self.iItemIndex = -1

			# <!-- custom: force keyboard focus so UP/DOWN works without requiring a click (chatgpt 5.2 + claude opus 4.5) -->
			try:
				screen = self.getScreen()
				# Focus the left list when present
				if self.SAS_lastItemsWidget is not None:
					try:
						screen.setFocus(self.ITEM_LIST_ID)
					except:
						pass
			except:
				pass
		self.tab = self.TAB_TOC

	def isIndexShowing(self):
		return self.tab == self.TAB_INDEX
	
	def showIndex(self):
		if not self.SAS_USE_BOTTOM_TABS:
			return
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
	
	def placeIndexCategory(self):
		screen = self.getScreen()
		self.SAS_lastItemsWidget = None
		self.SAS_lastItemsInfo = None
		self.SAS_szSearchString = u""
		self.SAS_keyDebounceByKey = {}
		self.SAS_deleteSearchWidgets()
		self.SAS_safeDeleteWidget(screen, self.ITEM_LIST_ID)
		self.pediaIndex.interfaceScreen(True)
	
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

		# <!-- custom: add highlight text for sevopedia sorting needs as we added, here fetched once for performance optimization or/and such -->
		self.COLOR_HIGHLIGHT_TEXT = gc.getInfoTypeForString('COLOR_HIGHLIGHT_TEXT')
		self.IS_SAS_SEVOPEDIA_MAIN_CIVICS_GROUP_BY_CIVIC_TYPES = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_CIVICS_GROUP_BY_CIVIC_TYPES") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_TECHS_GROUP_BY_ERA = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_TECHS_GROUP_BY_ERA") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_BUILDINGS_GROUP_BY_ERA = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_BUILDINGS_GROUP_BY_ERA") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_UNITS_GROUP_BY_ERA = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_UNITS_GROUP_BY_ERA") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_CORPORATIONS_GROUP_BY_ERA = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_CORPORATIONS_GROUP_BY_ERA") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_RELIGIONS_GROUP_BY_ERA = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_RELIGIONS_GROUP_BY_ERA") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_PROJECTS_GROUP_BY_ERA = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_PROJECTS_GROUP_BY_ERA") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_SPECIALISTS_GROUP_BY_TYPE = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_SPECIALISTS_GROUP_BY_TYPE") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_BONUSES_GROUP_BY_IMPROVEMENT = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_BONUSES_GROUP_BY_IMPROVEMENT") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_IMPROVEMENTS_GROUP_BY_TERRAIN = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_IMPROVEMENTS_GROUP_BY_TERRAIN") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_TERRAINS_GROUP_BY_LAND_WATER = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_TERRAINS_GROUP_BY_LAND_WATER") > 0)
		self.IS_SAS_SEVOPEDIA_MAIN_FEATURES_GROUP_BY_LAND_WATER = (gc.getDefineINT("SAS_SEVOPEDIA_MAIN_FEATURES_GROUP_BY_LAND_WATER") > 0)

		# These are terrain TYPES that should be classified under the "GraphicalOnly (High)" header rather than "Land". This is purely a UI grouping choice.
		self.SAS_SEVOPEDIA_TERRAIN_GRAPHICAL_ONLY_HIGH_TYPES = ("TERRAIN_HILL", "TERRAIN_PEAK")

		self.categoryList = []
		self.SAS_categoryEnumToIndex = {}
		for iEnum, szLabelKey, szIcon, szListMethod, screenSpec, szLinkKey in self.SAS_CATEGORY_DEFS:
			self.categoryList.append((szIcon, localText.getText(szLabelKey, ()), iEnum))
		for i, category in enumerate(self.categoryList):
			self.SAS_categoryEnumToIndex[category[2]] = i

		self.SAS_linkMatchDefs = (
			("getNumTechInfos", "getTechInfo", SevoScreenEnums.PEDIA_TECHS),
			("getNumUnitInfos", "getUnitInfo", SevoScreenEnums.PEDIA_UNITS),
			("getNumUnitCombatInfos", "getUnitCombatInfo", SevoScreenEnums.PEDIA_UNIT_CATEGORIES),
			("getNumPromotionInfos", "getPromotionInfo", SevoScreenEnums.PEDIA_PROMOTIONS),
			("getNumBuildingInfos", "getBuildingInfo", SevoScreenEnums.PEDIA_BUILDINGS),
			("getNumProjectInfos", "getProjectInfo", SevoScreenEnums.PEDIA_PROJECTS),
			("getNumSpecialistInfos", "getSpecialistInfo", SevoScreenEnums.PEDIA_SPECIALISTS),
			("getNumTerrainInfos", "getTerrainInfo", SevoScreenEnums.PEDIA_TERRAINS),
			("getNumFeatureInfos", "getFeatureInfo", SevoScreenEnums.PEDIA_FEATURES),
			("getNumBonusInfos", "getBonusInfo", SevoScreenEnums.PEDIA_BONUSES),
			("getNumImprovementInfos", "getImprovementInfo", SevoScreenEnums.PEDIA_IMPROVEMENTS),
			("getNumCivilizationInfos", "getCivilizationInfo", SevoScreenEnums.PEDIA_CIVS),
			("getNumLeaderHeadInfos", "getLeaderHeadInfo", SevoScreenEnums.PEDIA_LEADERS),
			("getNumCivicInfos", "getCivicInfo", SevoScreenEnums.PEDIA_CIVICS),
			("getNumReligionInfos", "getReligionInfo", SevoScreenEnums.PEDIA_RELIGIONS),
			("getNumCorporationInfos", "getCorporationInfo", SevoScreenEnums.PEDIA_CORPORATIONS),
			("getNumConceptInfos", "getConceptInfo", SevoScreenEnums.PEDIA_CONCEPTS),
			("getNumNewConceptInfos", "getNewConceptInfo", SevoScreenEnums.PEDIA_BTS_CONCEPTS),
			)

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
			graphic = category[0]
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
			screen.appendListBoxStringNoUpdate(self.CATEGORY_LIST_ID, szHeading, WidgetTypes.WIDGET_PEDIA_MAIN, category[2], 0, CvUtil.FONT_LEFT_JUSTIFY)
		screen.updateListBox(self.CATEGORY_LIST_ID)


	def placeTechs(self):
		self.list = self.getTechList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, gc.getTechInfo)

		# <!-- custom: similarly to how we did in placeLeaders, precompute only once the list as string of untradeable techs for display in sevopedia tech, since it is always the same, and precompute it only after first time list is displayed so it is smoother/faster; also do not build it needlessly if we never access sevopedia tech same as in/for the leaders_info_cached code. -->
		if not self.IS_UNTRADEABLE_TECHS_TEXT_PREBUILT:
			SevoPediaTech.UNTRADEABLE_TECHS_TEXT = SevoPediaTech.getPrecomputedUntradeableTechsText()
			self.IS_UNTRADEABLE_TECHS_TEXT_PREBUILT = True
			print("Sevopedia Tech Untradeable techs list prebuilt from Sevopedia Main. This should appear only once even if we exit sevopedia entirely, as long as we are during the same gaming session (i.e. game was not exited) (for info, in SevopediaMain, self.IS_UNTRADEABLE_TECHS_TEXT_PREBUILT=%s)." % str(self.IS_UNTRADEABLE_TECHS_TEXT_PREBUILT))

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

		return techsList

	def getTechList(self):
		if self.SAS_cacheTechsTuple is None:
			if self.IS_SAS_SEVOPEDIA_MAIN_TECHS_GROUP_BY_ERA:
				self.SAS_cacheTechsTuple = tuple(self.SAS_getTechsGroupedByEra())
			else:
				# <!-- custom: base advciv's formula, only difference is we cache it now -->
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

		# <!-- custom: note: executives's tech actual requirement not implemented here, as in advciv-sas they also have a prereq tech (see XML code comments or main changes guide or such for rationale). Otherwise the implementation so they are listed at e.g. "Industrial" Era and not "No Tech Prerequisite" (which does not reflect their effective ingame availabilty: not until later eras) would be tedious from what i understand of chatgpt 5.2's explanation and solution (plus we don't need to so better not); check if accurate -->
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

		return unitsList

	# <!-- custom: similarly, in sevopedia units, group units by era (based on prereq tech) instead of one long list. Code added with the help of chatgpt 5.2 thanks -->
	def getUnitList(self):
		if self.SAS_cacheUnitsTuple is None:
			baseList = self.getSortedList(gc.getNumUnitInfos(), gc.getUnitInfo)
			if self.IS_SAS_SEVOPEDIA_MAIN_UNITS_GROUP_BY_ERA:
				self.SAS_cacheUnitsTuple = tuple(self.SAS_getUnitsGroupedByEra_fromBaseList(baseList))
			else:
				self.SAS_cacheUnitsTuple = tuple(baseList)
		return self.SAS_cacheUnitsTuple


	def placeUnitUpgrades(self):
		# <!-- custom: type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->
		# <!-- custom: clear search state for special pages that delete the item list (chatgpt 5.2 + claude opus 4.5) -->
		self.SAS_szSearchString = u""
		self.SAS_lastItemsWidget = None
		self.SAS_lastItemsInfo = None
		self.SAS_deleteSearchWidgets()
		# <!-- custom: End - type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->

		screen = self.getScreen()
		self.getScreen().deleteWidget("PediaMainItemList")
		self.UPGRADES_GRAPH_ID = self.getNextWidgetName()
		screen.addScrollPanel(self.UPGRADES_GRAPH_ID, u"", self.X_ITEMS, self.Y_PEDIA_PAGE - 13, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 2, PanelStyles.PANEL_STYLE_STANDARD)
		screen.setActivation(self.UPGRADES_GRAPH_ID, ActivationTypes.ACTIVATE_NORMAL)

		# <!-- custom: focus the graph so arrow scrolling works without clicking (chatgpt 5.2 + claude opus 4.5) -->
		try:
			screen.setFocus(self.UPGRADES_GRAPH_ID)
		except:
			pass

		upgradesGraph = UnitUpgradesGraph.UnitUpgradesGraph(self)
		upgradesGraph.getGraph()
		upgradesGraph.drawGraph()

	def placeHandicapChart(self):
		self.SAS_szSearchString = u""
		self.SAS_lastItemsWidget = None
		self.SAS_lastItemsInfo = None
		self.SAS_deleteSearchWidgets()

		self.getScreen().deleteWidget("PediaMainItemList")
		self.pediaHandicapChart.interfaceScreen()

	def placeGameSpeedChart(self):
		self.SAS_szSearchString = u""
		self.SAS_lastItemsWidget = None
		self.SAS_lastItemsInfo = None
		self.SAS_deleteSearchWidgets()

		self.getScreen().deleteWidget("PediaMainItemList")
		self.pediaGameSpeedChart.interfaceScreen()

	def placeWorldSizeChart(self):
		self.SAS_szSearchString = u""
		self.SAS_lastItemsWidget = None
		self.SAS_lastItemsInfo = None
		self.SAS_deleteSearchWidgets()

		self.getScreen().deleteWidget("PediaMainItemList")
		self.pediaWorldSizeChart.interfaceScreen()


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
		# <!-- custom: type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->
		# <!-- custom: clear search state for special pages that delete the item list (chatgpt 5.2 + claude opus 4.5) -->
		self.SAS_szSearchString = u""
		self.SAS_lastItemsWidget = None
		self.SAS_lastItemsInfo = None
		self.SAS_deleteSearchWidgets()
		# <!-- custom: End - type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->

		screen = self.getScreen()
		self.getScreen().deleteWidget("PediaMainItemList")
		self.UPGRADES_GRAPH_ID = self.getNextWidgetName()
		screen.addScrollPanel(self.UPGRADES_GRAPH_ID, u"", self.X_ITEMS, self.Y_PEDIA_PAGE - 13, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 2, PanelStyles.PANEL_STYLE_STANDARD)
		screen.setActivation(self.UPGRADES_GRAPH_ID, ActivationTypes.ACTIVATE_NORMAL)

		# <!-- custom: focus the graph so arrow scrolling works without clicking (chatgpt 5.2 + claude opus 4.5) -->
		try:
			screen.setFocus(self.UPGRADES_GRAPH_ID)
		except:
			pass

		upgradesGraph = UnitUpgradesGraph.PromotionsGraph(self)
		upgradesGraph.getGraph()
		upgradesGraph.drawGraph()


	def placeBuildings(self):
		self.list = self.getBuildingList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)

	# Compute the "availability era" for a building, factoring in tech prereqs, special building tech, and religion founding tech.
	def SAS_getBuildingAvailabilityEra(self, iBuilding, iNumAndTechs):
		info = gc.getBuildingInfo(iBuilding)
		if not info or info.isGraphicalOnly():
			return None  # caller should skip

		iEra = -1

		# Main AND prereq tech (<PrereqTech>)
		# <!-- custom: it seems getPrereqOrTechs does not exist causing a python error, but with the help of chatgpt 5.2 found the correct way to fetch tech prereqs that addresses and fixes it and that works as intended in displaying the building at latest tech prereq of the building's corresponding era. Seems to run fine in testing/empirically, check if accurate -->
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
		# <!-- custom: special buildings need also to be checked for a tech prereq. For example the buddhist monastery as of now has no TechPrereq and TechTypes NONE, but the parent specialbuilding_monastery requires TECH_MONARCHY. Yet, without taking special buildings into account, the buddhist monastery is incorrectly listed at the "No Tech Prereq" part instead of at the "Classical Era" part. Fix this by taking their actual tech prereq into account properly with the help of chatgpt 5.2 thanks -->
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

	# <!-- custom: helper we can reuse for regular buildings, national wonders, world wonders, with the help of chatgpt 5.2 thanks -->
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

		return buildingsList

	# <!-- custom: similarly, in sevopedia buildings, group techs by era (based on prereq tech) instead of one long list. Code added with the help of chatgpt 5.2 thanks -->
	def getBuildingList(self):
		if self.SAS_cacheRegularBuildingsTuple is None:
			baseList = self.pediaBuilding.getBuildingSortedList(0)
			if self.IS_SAS_SEVOPEDIA_MAIN_BUILDINGS_GROUP_BY_ERA:
				self.SAS_cacheRegularBuildingsTuple = tuple(self.SAS_getBuildingsGroupedByEra_fromBaseList(baseList))
			else:
				self.SAS_cacheRegularBuildingsTuple = tuple(baseList)
		return self.SAS_cacheRegularBuildingsTuple


	def placeNationalWonders(self):
		self.list = self.getNationalWonderList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)
	
	# <!-- custom: also group them by era (tech prereq) with the help of chatgpt 5.2 thanks -->
	def getNationalWonderList(self):
		if self.IS_SAS_SEVOPEDIA_MAIN_BUILDINGS_GROUP_BY_ERA:
			if self.SAS_cacheNationalWondersTuple is None:
				baseList = self.pediaBuilding.getBuildingSortedList(1)
				self.SAS_cacheNationalWondersTuple = tuple(self.SAS_getBuildingsGroupedByEra_fromBaseList(baseList))
			return self.SAS_cacheNationalWondersTuple
		else:
			if self.SAS_cacheNationalWondersTuple is None:
				self.SAS_cacheNationalWondersTuple = tuple(self.pediaBuilding.getBuildingSortedList(1))
			return self.SAS_cacheNationalWondersTuple


	def placeWorldWonders(self):
		self.list = self.getWorldWonderList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)

	# <!-- custom: also group them by era (tech prereq) with the help of chatgpt 5.2 thanks -->	
	def getWorldWonderList(self):
		if self.IS_SAS_SEVOPEDIA_MAIN_BUILDINGS_GROUP_BY_ERA:
			if self.SAS_cacheWorldWondersTuple is None:
				baseList = self.pediaBuilding.getBuildingSortedList(2)
				self.SAS_cacheWorldWondersTuple = tuple(self.SAS_getBuildingsGroupedByEra_fromBaseList(baseList))
			return self.SAS_cacheWorldWondersTuple
		else:
			if self.SAS_cacheWorldWondersTuple is None:
				self.SAS_cacheWorldWondersTuple = tuple(self.pediaBuilding.getBuildingSortedList(2))
			return self.SAS_cacheWorldWondersTuple


	def placeProjects(self):
		self.list = self.getProjectList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, gc.getProjectInfo)

	# Compute the "availability era" for a project, factoring in its tech prereq.
	def SAS_getProjectAvailabilityEra(self, iProject):
		info = gc.getProjectInfo(iProject)
		if not info or info.isGraphicalOnly():
			return None  # caller should skip

		iTech = info.getTechPrereq()
		if iTech >= 0:
			return gc.getTechInfo(iTech).getEra()

		return -1  # "No Tech Prerequisite" bucket


	# Helper we can reuse for project lists, with the help of chatgpt 5.2 thanks.
	def SAS_getProjectsGroupedByEra_fromBaseList(self, baseList):
		projectsList = []

		iNumEras = gc.getNumEraInfos()

		noTech = []
		groups = {}  # iEra -> [(szName, iProject), ...]

		# One pass: compute era once and bucket
		for (szName, iProject) in baseList:
			iEra = self.SAS_getProjectAvailabilityEra(iProject)
			if iEra is None:
				continue

			if iEra == -1:
				noTech.append((szName, iProject))
			else:
				if iEra not in groups:
					groups[iEra] = []
				groups[iEra].append((szName, iProject))

		# Optional sorting within each bucket
		if self.isSortLists():
			noTech.sort()
			for k in groups.keys():
				groups[k].sort()

		# "No Tech Prereq" group first
		if noTech:
			projectsList.append((localText.getText("TXT_KEY_PEDIA_NO_TECH_PREREQUISITE", ()), -1))
			for x in noTech:
				projectsList.append(x)

		# Era groups in order
		for iEraLoop in range(iNumEras):
			tmp = groups.get(iEraLoop, None)
			if not tmp:
				continue

			if projectsList:
				projectsList.append(("", -1))

			projectsList.append((gc.getEraInfo(iEraLoop).getDescription() + " " + localText.getText("TXT_KEY_PEDIA_ERA", ()), -1))
			for x in tmp:
				projectsList.append(x)

		return projectsList

	# <!-- custom: similarly, in sevopedia projects, group projects by era instead of one long list. Code added with the help of chatgpt 5.2 thanks -->
	def getProjectList(self):
		if self.SAS_cacheProjectsTuple is None:
			baseList = self.getSortedList(gc.getNumProjectInfos(), gc.getProjectInfo)
			if self.IS_SAS_SEVOPEDIA_MAIN_PROJECTS_GROUP_BY_ERA:
				self.SAS_cacheProjectsTuple = tuple(self.SAS_getProjectsGroupedByEra_fromBaseList(baseList))
			else:
				self.SAS_cacheProjectsTuple = tuple(baseList)
		return self.SAS_cacheProjectsTuple


	def placeSpecialists(self):
		self.list = self.getSpecialistList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPECIALIST, gc.getSpecialistInfo)

	# Helper to group specialists by type (e.g. Engineer vs Great Engineer). Great specialists are identified by "GREAT_" in SpecialistInfo.getType(), matching RFC DoC's convention.
	def SAS_getSpecialistsGroupedByType(self):
		specialistsList = []
		greatSpecialistsList = []

		# One pass: preserve XML order when Sort Lists is OFF.
		for iSpecialist in range(gc.getNumSpecialistInfos()):
			info = gc.getSpecialistInfo(iSpecialist)
			if not info or info.isGraphicalOnly():
				continue

			szName = info.getDescription()
			szType = info.getType()

			if szType and (szType.find("GREAT_") > -1):
				greatSpecialistsList.append((szName, iSpecialist))
			else:
				specialistsList.append((szName, iSpecialist))

		# Optional sorting within each group
		if self.isSortLists():
			specialistsList.sort()
			greatSpecialistsList.sort()

		outList = []

		if specialistsList:
			# Reuse the category label for a localized "Specialists" header.
			outList.append((localText.getText("TXT_KEY_PEDIA_CATEGORY_SPECIALIST", ()), -1))
			for x in specialistsList:
				outList.append(x)

		if greatSpecialistsList:
			if outList:
				outList.append(("", -1))  # spacer between groups
			outList.append(("Great Specialists", -1))
			for x in greatSpecialistsList:
				outList.append(x)

		return outList

	# <!-- custom: in sevopedia specialists, group specialists by type: regular specialists vs great specialists (those whose <Type> contains "GREAT_"), based on RFC DOC mod's code thanks. Added with the help of chatgpt 5.2 thanks -->
	# Notes (kept conservative)
	# 	- “Great specialists” detection is exactly RFC’s convention: getType().find("GREAT_") > -1. 
	# 	- I reused TXT_KEY_PEDIA_CATEGORY_SPECIALIST for the regular header (so it’s localized), and I used the literal string "Great Specialists" for the great header (since your mod likely doesn’t have RFC’s TXT_KEY_PEDIA_HEADER_GREAT_SPECIALIST). If you want, you can later add your own TXT_KEY and swap that line to localText.getText("TXT_KEY_PEDIA_HEADER_GREAT_SPECIALIST", ()).
	def getSpecialistList(self):
		if self.SAS_cacheSpecialistsTuple is None:
			if self.IS_SAS_SEVOPEDIA_MAIN_SPECIALISTS_GROUP_BY_TYPE:
				self.SAS_cacheSpecialistsTuple = tuple(self.SAS_getSpecialistsGroupedByType())
			else:
				self.SAS_cacheSpecialistsTuple = tuple(self.getSortedList(gc.getNumSpecialistInfos(), gc.getSpecialistInfo))
		return self.SAS_cacheSpecialistsTuple


	def placeTerrains(self):
		self.list = self.getTerrainList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, gc.getTerrainInfo)

	def SAS_getTerrainsGroupedByLandWater_fromBaseList(self, baseList):
		r = []
		landFlat = []
		graphicalOnlyHigh = []
		water = []

		# Terrain IDs considered "GraphicalOnly (High)" purely for UI grouping (e.g. Hills/Peaks).
		highIds = []
		for szType in self.SAS_SEVOPEDIA_TERRAIN_GRAPHICAL_ONLY_HIGH_TYPES:
			iT = getInfoTypeOrFail(szType, gc)
			if iT >= 0:
				highIds.append(iT)

		for (szName, iTerrain) in baseList:
			info = gc.getTerrainInfo(iTerrain)

			# IMPORTANT:
			# In your CIV4TerrainInfos.xml, TERRAIN_HILL and TERRAIN_PEAK have <bWater>1</bWater>. Therefore info.isWater() returns True for them. For Sevopedia grouping we still want them under GraphicalOnly (High), so we treat LAND_HIGH as a deliberate UI override.
			if iTerrain in highIds:
				graphicalOnlyHigh.append((szName, iTerrain))
			elif info and info.isWater():
				water.append((szName, iTerrain))
			else:
				landFlat.append((szName, iTerrain))

		if self.isSortLists():
			landFlat.sort()
			graphicalOnlyHigh.sort()
			water.sort()

		if landFlat:
			r.append(("Land", -1))
			for x in landFlat:
				r.append(x)

		if landFlat and graphicalOnlyHigh:
			r.append(("", -1))

		if graphicalOnlyHigh:
			r.append(("GraphicalOnly (High)", -1))
			for x in graphicalOnlyHigh:
				r.append(x)

		if (landFlat or graphicalOnlyHigh) and water:
			r.append(("", -1))

		if water:
			r.append(("Water", -1))
			for x in water:
				r.append(x)

		return r

	def getTerrainList(self):
		if self.SAS_cacheTerrainsTuple is None:
			# <!-- custom: also show terrain_peak and terrain_hill in sevopedia terrains display even though they are plot types if i am not mistaken but with the changes in sevopedia terrain (new placeRelevantUnits and placeUnitsImpassable panels as of now), these still provide very valuable info so adding them helps a lot; code provided with the help of chatgpt thanks and previous reworks i did with it or with claude ai or and such -->
			# Note: TERRAIN_HILL and TERRAIN_PEAK already exist in CIV4TerrainInfos.xml, but have <bGraphicalOnly>1</bGraphicalOnly>, so they are hidden by the normal list. For Sevopedia, we want them visible, so we include GraphicalOnly here.
			baseList = self.getUnfilteredSortedList(gc.getNumTerrainInfos(), gc.getTerrainInfo)
			if self.IS_SAS_SEVOPEDIA_MAIN_TERRAINS_GROUP_BY_LAND_WATER:
				self.SAS_cacheTerrainsTuple = tuple(self.SAS_getTerrainsGroupedByLandWater_fromBaseList(baseList))
			else:
				self.SAS_cacheTerrainsTuple = tuple(baseList)
		return self.SAS_cacheTerrainsTuple

	def placeFeatures(self):
		self.list = self.getFeatureList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE, gc.getFeatureInfo)

		# <!-- custom: quite similarly to other precompute codes in sevopedia main, also do sevopedia bonus's pre-loading logic at time where it is more/most efficient. -->
		if not self.IS_FEATURES_PRE_LOADING_XML_DATA_VALIDATION_DONE:
			SevoPediaFeature.do_pre_load_xml_features_info_required_data_validation()
			self.IS_FEATURES_PRE_LOADING_XML_DATA_VALIDATION_DONE = True
			print("Sevopedia Feature pre load XML data validation done from Sevopedia Main. This should appear only once even if we exit sevopedia entirely, as long as we are during the same gaming session (i.e. game was not exited) (for info, in SevopediaMain, self.IS_FEATURES_PRE_LOADING_XML_DATA_VALIDATION_DONE=%s)." % str(self.IS_FEATURES_PRE_LOADING_XML_DATA_VALIDATION_DONE))

	# <!-- custom: in sevopedia feature list, group features by Land (Removable), Land (Other), and Water. Added with the help of chatgpt 5.2 thanks. -->
	# Implementation note:
	# - We detect "Water" features by checking if the feature can appear on any true water terrain using FeatureInfo.isTerrain(iTerrain).
	# - We detect "Removable" land features by scanning CvBuildInfo for a build that removes that feature.
	#
	# IMPORTANT MOD-SPECIFIC NOTE:
	# - In our CIV4TerrainInfos.xml, TERRAIN_HILL and TERRAIN_PEAK have <bWater>1</bWater>.
	# - Many land features are valid on hills, so if we treat every isWater terrain as water here,
	#   we'd misclassify many land features as "Water".
	# - Therefore we exclude our GraphicalOnly (High) terrains from the water-terrain scan used here. -->
	def SAS_getFeaturesGroupedByLandWater_fromBaseList(self, baseList):
		r = []
		landRemovable = []
		landOther = []
		water = []

		# Exclude our GraphicalOnly (High) terrains (e.g. Hill/Peak) even if XML marks them as water.
		graphicalOnlyHighIds = []
		for szType in self.SAS_SEVOPEDIA_TERRAIN_GRAPHICAL_ONLY_HIGH_TYPES:
			iT = getInfoTypeOrFail(szType, gc)
			graphicalOnlyHighIds.append(iT)

		# Build list of "true water terrains" for feature classification.
		waterTerrainIds = []
		for iTerrain in range(gc.getNumTerrainInfos()):
			tInfo = gc.getTerrainInfo(iTerrain)
			if tInfo and tInfo.isWater() and (iTerrain not in graphicalOnlyHighIds):
				waterTerrainIds.append(iTerrain)

		for (szName, iFeature) in baseList:
			fInfo = gc.getFeatureInfo(iFeature)

			# Water feature if it can appear on at least one true water terrain.
			bIsWaterFeature = False
			for iTerrain in waterTerrainIds:
				if fInfo.isTerrain(iTerrain):
					bIsWaterFeature = True
					break

			if bIsWaterFeature:
				water.append((szName, iFeature))
			else:
				# Land feature: split removable vs other
				if SAS_isFeatureRemovable(iFeature, gc):
					landRemovable.append((szName, iFeature))
				else:
					landOther.append((szName, iFeature))

		if self.isSortLists():
			landRemovable.sort()
			landOther.sort()
			water.sort()

		if landRemovable:
			r.append(("Land (Removable)", -1))
			for x in landRemovable:
				r.append(x)

		if landRemovable and landOther:
			r.append(("", -1))

		if landOther:
			r.append(("Land (Other)", -1))
			for x in landOther:
				r.append(x)

		if (landRemovable or landOther) and water:
			r.append(("", -1))

		if water:
			r.append(("Water", -1))
			for x in water:
				r.append(x)

		return r

	def getFeatureList(self):
		if self.SAS_cacheFeaturesTuple is None:
			baseList = self.getSortedList(gc.getNumFeatureInfos(), gc.getFeatureInfo)
			if self.IS_SAS_SEVOPEDIA_MAIN_FEATURES_GROUP_BY_LAND_WATER:
				self.SAS_cacheFeaturesTuple = tuple(self.SAS_getFeaturesGroupedByLandWater_fromBaseList(baseList))
			else:
				self.SAS_cacheFeaturesTuple = tuple(baseList)
		return self.SAS_cacheFeaturesTuple


	def placeBonuses(self):
		self.list = self.getBonusList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, gc.getBonusInfo)

	# Helper: get ALL improvements that make a bonus tradable (i.e. "improve/connect" it).
	# This is used for Sevopedia Main list grouping, similar to RFC DoC's Resource grouping.
	# Unlike a "primary improvement" heuristic, we keep multi-improvement cases exhaustive by using
	# a combined header like: "Well, Offshore Platform".
	def SAS_getTradingImprovementsForBonus(self, iBonus):
		bInfo = gc.getBonusInfo(iBonus)
		if not bInfo or bInfo.isGraphicalOnly():
			return []
		r = []
		for iImprovement in range(gc.getNumImprovementInfos()):
			imprInfo = gc.getImprovementInfo(iImprovement)
			if not imprInfo or imprInfo.isGraphicalOnly():
				continue
			# Support both wrapper styles (RFC often exposes isBonusTrade; BtS/AdvCiv uses isImprovementBonusTrade).
			if hasattr(imprInfo, "isBonusTrade"):
				bTrades = imprInfo.isBonusTrade(iBonus)
			else:
				bTrades = imprInfo.isImprovementBonusTrade(iBonus)
			if bTrades:
				r.append(iImprovement)
		return r

	# Group bonuses by the improvement(s) that connect them:
	#   Farm -> Corn/Wheat/...
	#   Pasture -> Sheep/Horse/...
	# For multi-improvement bonuses (e.g. Oil: Well + Offshore Platform), we use a combined header.
	# <!-- custom: we did this change because RFC DOC used another water/land tie breaker logic that would display Oil only under "Well", but the player needs to know too that "Offshore Platform" is another improvement trades for Oil. Also, if some mod mod added another improvement trades on land (e.g. Farm + Pasture for Milk (imaginary example)) then the water/land tie breaking would not be effective as well, and we'd miss the info that both improvements support this. This is the only case in our mod (Oil) that has more than one improvement trades., so we don't need to complicate the logic further, while hopefully providing this logic in a bit cleaner or more relevant way to us than in RFC DOC mod (although their code helps lot and with chatgpt 5.2's help too and my help too xd i mean thanks to them and me xd as well) -->
	def SAS_getBonusesGroupedByImprovement_fromBaseList(self, baseList):
		bonusesList = []

		noImprovement = []
		groups = {}  # key tuple(iImprovement, ...) -> [(szName, iBonus), ...]

		# One pass over bonuses preserves XML order within each group when Sort Lists is OFF.
		for (szName, iBonus) in baseList:
			lImpr = self.SAS_getTradingImprovementsForBonus(iBonus)
			if not lImpr:
				noImprovement.append((szName, iBonus))
				continue

			# Keep improvement ids in XML order (already in-order due to the loop in SAS_getTradingImprovementsForBonus).
			key = tuple(lImpr)
			tmp = groups.get(key, None)
			if tmp is None:
				tmp = []
				groups[key] = tmp
			tmp.append((szName, iBonus))

		# Optional sorting within each improvement-group (when BUG "Sort Lists" is ON)
		if self.isSortLists():
			for k in groups.keys():
				groups[k].sort()
			noImprovement.sort()

		# Order headers:
		#  - primarily by first improvement id (so this generally follows ImprovementInfos XML order),
		#  - then by key length (single-improvement headers first),
		#  - then by the key itself (stable).
		keys = groups.keys()
		def _cmpKeys(a, b):
			ta = (a[0], len(a), a)
			tb = (b[0], len(b), b)
			if ta < tb:
				return -1
			if ta > tb:
				return 1
			return 0
		keys.sort(_cmpKeys)

		for key in keys:
			tmp = groups.get(key, None)
			if not tmp:
				continue

			if bonusesList:
				bonusesList.append(("", -1))

			# Header text: single improvement name OR "A, B, C" for multi-improvement bonuses.
			parts = []
			for iImprovement in key:
				imprInfo = gc.getImprovementInfo(iImprovement)
				if imprInfo:
					parts.append(imprInfo.getDescription())
			szHeader = "Improvement"
			if parts:
				szHeader = ", ".join(parts)
			bonusesList.append((szHeader, -1))

			for x in tmp:
				bonusesList.append(x)

		# Fallback bucket for bonuses that have no connecting/trade improvement (rare)
		if noImprovement:
			if bonusesList:
				bonusesList.append(("", -1))
			bonusesList.append(("Other", -1))
			for x in noImprovement:
				bonusesList.append(x)

		return bonusesList

	def getBonusList(self):
		if self.SAS_cacheBonusesTuple is None:
			baseList = self.getSortedList(gc.getNumBonusInfos(), gc.getBonusInfo)
			if self.IS_SAS_SEVOPEDIA_MAIN_BONUSES_GROUP_BY_IMPROVEMENT:
				self.SAS_cacheBonusesTuple = tuple(self.SAS_getBonusesGroupedByImprovement_fromBaseList(baseList))
			else:
				self.SAS_cacheBonusesTuple = tuple(baseList)
		return self.SAS_cacheBonusesTuple


	def placeImprovements(self):
		self.list = self.getImprovementList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, gc.getImprovementInfo)

	def SAS_isBonusCapableImprovement(self, iImprovement):
		info = gc.getImprovementInfo(iImprovement)
		if not info or info.isGraphicalOnly():
			return False

		# If it connects/trades any bonus, it's bonus-capable.
		for iBonus in range(gc.getNumBonusInfos()):
			bInfo = gc.getBonusInfo(iBonus)
			if bInfo and bInfo.isGraphicalOnly():
				continue

			if hasattr(info, "isBonusTrade"):
				if info.isBonusTrade(iBonus):
					return True
			else:
				if info.isImprovementBonusTrade(iBonus):
					return True

		# Some mods may give bonus yields even if trade flags are odd.
		for iBonus in range(gc.getNumBonusInfos()):
			bInfo = gc.getBonusInfo(iBonus)
			if bInfo and bInfo.isGraphicalOnly():
				continue
			for iYield in range(YieldTypes.NUM_YIELD_TYPES):
				if info.getImprovementBonusYield(iBonus, iYield) != 0:
					return True

		return False

	# <!-- custom: in sevopedia improvement list, group improvements by whether their terrain is a water type or not (e.g. Land Improvements -> Farm/Pasture, Water Improvements -> Fishing Boats/Offshore Platform) an idea i got from seeing ingame how it is in the Middle-Earth mod which i find very polished and took ideas from btw  thanks; plus other subgroups we added in advciv-sas. Implemented with chatgpt 5.2's help as for as of now the other ones thanks a lot -->
	# Group improvements as:
	# - Land (Growth): land improvements in an upgrade chain (e.g. Cottage -> Hamlet -> Village -> Town)
	# - Land (Bonus-capable): land improvements that can interact with bonuses (trade/connect or bonus yields)
	# - Land (Other): remaining land improvements
	# - Water
	def SAS_getImprovementsGroupedByTerrain_fromBaseList(self, baseList):
		r = []
		landGrowth = []
		landBonusCapable = []
		landOther = []
		water = []

		# Build set of improvements that are upgraded *to* by something (to detect chain membership, incl. final node).
		dUpgradeTargets = {}
		for (szName, iImprovement) in baseList:
			info = gc.getImprovementInfo(iImprovement)
			if info and hasattr(info, "getImprovementUpgrade"):
				iUp = info.getImprovementUpgrade()
				if iUp != -1:
					dUpgradeTargets[iUp] = 1

		# Cache bonus-capability per improvement to avoid re-scanning bonuses repeatedly.
		dBonusCapable = {}

		for (szName, iImprovement) in baseList:
			info = gc.getImprovementInfo(iImprovement)

			if info and info.isWater():
				water.append((szName, iImprovement))
				continue

			# Land
			bGrowth = False
			if info and hasattr(info, "getImprovementUpgrade"):
				iUp = info.getImprovementUpgrade()
				if iUp != -1 or dUpgradeTargets.has_key(iImprovement):
					bGrowth = True

			if bGrowth:
				landGrowth.append((szName, iImprovement))
			else:
				if dBonusCapable.has_key(iImprovement):
					bBonusCapable = dBonusCapable[iImprovement]
				else:
					bBonusCapable = self.SAS_isBonusCapableImprovement(iImprovement)
					dBonusCapable[iImprovement] = bBonusCapable

				if bBonusCapable:
					landBonusCapable.append((szName, iImprovement))
				else:
					landOther.append((szName, iImprovement))

		# Optional sorting if BUG Sort Lists is on
		if self.isSortLists():
			landGrowth.sort()
			landBonusCapable.sort()
			landOther.sort()
			water.sort()

		# Emit headers + items (same header/spacer style you already use)
		if landGrowth:
			r.append(("Land (Growth)", -1))
			for x in landGrowth:
				r.append(x)

		if landGrowth and (landBonusCapable or landOther or water):
			r.append(("", -1))

		if landBonusCapable:
			r.append(("Land (Bonus-capable)", -1))
			for x in landBonusCapable:
				r.append(x)

		if landBonusCapable and (landOther or water):
			r.append(("", -1))

		if landOther:
			r.append(("Land (Other)", -1))
			for x in landOther:
				r.append(x)

		if (landGrowth or landBonusCapable or landOther) and water:
			r.append(("", -1))

		if water:
			r.append(("Water", -1))
			for x in water:
				r.append(x)

		return r

	def getImprovementList(self):
		if self.SAS_cacheImprovementsTuple is None:
			imprList = self.getSortedList(gc.getNumImprovementInfos(), gc.getImprovementInfo)
			# <advc.004y>
			baseList = []
			for descr, i in imprList:
				info = gc.getImprovementInfo(i)
				# The alt. conditions are for Forest Preserve and Fort
				if info.getPillageGold() > 0 or info.isRequiresFeature() or info.isOutsideBorders():
					baseList.append((descr, i))
			# </advc.004y>

			if self.IS_SAS_SEVOPEDIA_MAIN_IMPROVEMENTS_GROUP_BY_TERRAIN:
				self.SAS_cacheImprovementsTuple = tuple(self.SAS_getImprovementsGroupedByTerrain_fromBaseList(baseList))
			else:
				self.SAS_cacheImprovementsTuple = tuple(baseList)

		return self.SAS_cacheImprovementsTuple


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

		# <!-- custom: prebuild the sevopedia leader cache only when=after we click on leaders button, so that if we open sevopedia and never access the leaders page, we don't compute needlessly a cached leader that is quite expensive or even if not too much needless and not optimal i think. After asking chatgpt, it advised me to do this here; note: place it after the list is computed so it doesn't appear to hang (in case it does, didn't test or look in detail) sometime on Leaders click before the items are placed: cache after leader items are place to avoid that, then the user has some time to click to desired leader, use that time to cache smoothly maybe and silently maybe -->
		if not self.IS_SEVOPEDIALEADER_CACHE_PREBUILT:
			SevoPediaLeader.LEADERS_INFO_CACHED, SevoPediaLeader.AI_RIGHT_CATEGORIES, SevoPediaLeader.AI_MIDDLE_CATEGORIES, SevoPediaLeader.AI_LEFT_CATEGORIES = SevoPediaLeader.getPrecomputedCacheOnceOnlyFromSevopediaMainInSevopediaLeaderForEntireSession()
			# <!-- custom: do not rebuild if built once already, for the entire session keep the same cache, even if we exit sevopedia, store data in memory or wherever it is stored, but do not build it until we click on leaders category the first time, not at module load (so a bit later than module load and not automatic but conditional in this case), but still before any leader is selected if i am not mistaken too -->
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

	def placeCivics(self):
		self.list = self.getCivicList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, gc.getCivicInfo)

	# <!-- custom: helper we can reuse for civics grouping, with the help of chatgpt 5.2 thanks -->
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

		return civicsList

	# <!-- custom: in sevopedia civics, order civics by civic type (e.g. Government, Economy, etc.), as RFC DOC mod does and that this code is based on, with the help of chatgpt 5.2 thanks -->
	# Step 2: Replace getCivicList() with “category + era tiers” (behind a SAS define)
	# Right now your civics list is just getSortedList(gc.getNumCivicInfos(), gc.getCivicInfo) (optionally alphabetical via BUG).
	# In RFC DoC, placeCivics() at least groups by civic option category using header rows. They also show how they do era tier grouping for other lists (e.g., wonders/buildings grouped by prereq tech era).
	def getCivicList(self):
		if self.SAS_cacheCivicsTuple is None:
			if self.IS_SAS_SEVOPEDIA_MAIN_CIVICS_GROUP_BY_CIVIC_TYPES:
				self.SAS_cacheCivicsTuple = tuple(self.SAS_getCivicsGroupedByCivicOption())
			else:
				self.SAS_cacheCivicsTuple = tuple(self.getSortedList(gc.getNumCivicInfos(), gc.getCivicInfo))
		return self.SAS_cacheCivicsTuple


	def placeReligions(self):
		self.list = self.getReligionList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, gc.getReligionInfo)

	# Compute the "availability era" for a religion, based on its founding tech prereq.
	def SAS_getReligionAvailabilityEra(self, iReligion):
		info = gc.getReligionInfo(iReligion)
		if not info or info.isGraphicalOnly():
			return None  # caller should skip

		iTech = info.getTechPrereq()
		if iTech >= 0:
			return gc.getTechInfo(iTech).getEra()

		return -1  # no tech prereq bucket

	# Helper we can reuse for religions.
	def SAS_getReligionsGroupedByEra_fromBaseList(self, baseList):
		religionsList = []

		iNumEras = gc.getNumEraInfos()

		noTech = []
		groups = {}  # iEra -> [(szName, iReligion), ...]

		# One pass: compute era once and bucket
		for (szName, iReligion) in baseList:
			iEra = self.SAS_getReligionAvailabilityEra(iReligion)
			if iEra is None:
				continue

			if iEra == -1:
				noTech.append((szName, iReligion))
			else:
				if not groups.has_key(iEra):
					groups[iEra] = []
				groups[iEra].append((szName, iReligion))

		# Optional sorting within each bucket
		if self.isSortLists():
			noTech.sort()
			for k in groups.keys():
				groups[k].sort()

		# "No Tech Prerequisite" group first
		if noTech:
			religionsList.append((localText.getText("TXT_KEY_PEDIA_NO_TECH_PREREQUISITE", ()), -1))
			for x in noTech:
				religionsList.append(x)

		# Era groups in order
		for iEraLoop in range(iNumEras):
			tmp = groups.get(iEraLoop, None)
			if not tmp:
				continue

			if religionsList:
				religionsList.append(("", -1))

			religionsList.append((gc.getEraInfo(iEraLoop).getDescription() + " " + localText.getText("TXT_KEY_PEDIA_ERA", ()), -1))
			for x in tmp:
				religionsList.append(x)

		return religionsList

	# <!-- custom: similarly, in sevopedia religions, group religions by era (based on their founding tech) instead of one long list. Code added with the help of chatgpt 5.2 thanks -->
	def getReligionList(self):
		baseList = self.getSortedList(gc.getNumReligionInfos(), gc.getReligionInfo)
		if self.SAS_cacheReligionsTuple is None:
			if self.IS_SAS_SEVOPEDIA_MAIN_RELIGIONS_GROUP_BY_ERA:
				self.SAS_cacheReligionsTuple = tuple(self.SAS_getReligionsGroupedByEra_fromBaseList(baseList))
			else:
				self.SAS_cacheReligionsTuple = tuple(baseList)
		return self.SAS_cacheReligionsTuple


	def placeCorporations(self):
		self.list = self.getCorporationList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION, gc.getCorporationInfo)

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

		return corpsList

	# <!-- custom: similarly, in sevopedia corporations, group corporations by era (based on founding building prereq tech era) instead of one long list. Code added with the help of chatgpt 5.2 thanks -->
	def getCorporationList(self):
		if self.SAS_cacheCorporationsTuple is None:
			baseList = self.getSortedList(gc.getNumCorporationInfos(), gc.getCorporationInfo)
			if self.IS_SAS_SEVOPEDIA_MAIN_CORPORATIONS_GROUP_BY_ERA:
				self.SAS_cacheCorporationsTuple = tuple(self.SAS_getCorporationsGroupedByEra_fromBaseList(baseList))
			else:
				self.SAS_cacheCorporationsTuple = tuple(baseList)
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
		# <!-- custom: type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->
		# <!-- custom: clear search state for special pages that delete the item list (chatgpt 5.2 + claude opus 4.5) -->
		self.SAS_szSearchString = u""
		self.SAS_lastItemsWidget = None
		self.SAS_lastItemsInfo = None
		self.SAS_deleteSearchWidgets()
		# <!-- custom: End - type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->

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
		# <!-- custom: no need to import string module just to split a string, use native code instead if i am not mistaken and as per chatgpt's explanation and what i understood of it -->
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

		# <!-- custom: type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->
		# <!-- custom: remember last list kind so typing can rebuild it (chatgpt 5.2 + claude opus 4.5) -->
		self.SAS_lastItemsWidget = widget
		self.SAS_lastItemsInfo = info

		# <!-- custom: search bar (top of item list) (chatgpt 5.2 + claude opus 4.5) -->
		self.SAS_syncSearchPanel()

		iTableY = self.Y_ITEMS + self.SAS_SEARCH_H + 2
		iTableH = self.H_ITEMS - (self.SAS_SEARCH_H + 2)
		# <!-- custom: End - type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->

		screen.clearListBoxGFC(self.ITEM_LIST_ID)

		screen.addTableControlGFC(self.ITEM_LIST_ID, 1, self.X_ITEMS, iTableY, self.W_ITEMS, iTableH, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(self.ITEM_LIST_ID, False)
		screen.setStyle(self.ITEM_LIST_ID, "Table_StandardCiv_Style")
		screen.setTableColumnHeader(self.ITEM_LIST_ID, 0, "", self.W_ITEMS)

		# <!-- custom: type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->
		# <!-- custom: get filter string for type-to-filter (chatgpt 5.2 + claude opus 4.5) -->
		szFilter = self.SAS_szSearchString.strip().lower()
		bFiltering = (len(szFilter) > 0)

		# <!-- custom: when filtering, keep headers and separators only for groups that contain at least one match (chatgpt 5.2 + claude opus 4.5) -->
		# Implementation note:
		# - self.list may contain header/separator rows encoded as ("Title", -1) or ("", -1).
		# - When filtering, we precompute which original list indices should be shown.
		# - We also build SAS_listIdxToRow so pediaJump can select the correct displayed row.
		setShowListIdx = None
		self.SAS_listIdxToRow = None

		# <!-- custom: rebuild arrow-navigation selectable caches every time we rebuild the list (fixes stale indices / out-of-range) (chatgpt 5.2) -->
		self.SAS_selectableListIdx = []
		self.SAS_itemToSelectablePos = {}

		if bFiltering:
			setShowListIdx = set()

			# Identify header rows (non-empty title with data1 == -1)
			listHeaderIdx = []
			for iListIdx, it in enumerate(self.list):
				if it[1] == -1:
					szTitle = it[0]
					if (szTitle is not None) and (len(szTitle.strip()) > 0):
						listHeaderIdx.append(iListIdx)

			# If there are no headers in this list, fall back to the simple behavior.
			if len(listHeaderIdx) == 0:
				for iListIdx, it in enumerate(self.list):
					if it[1] != -1:
						szName = it[0]
						if (szName is not None) and (szFilter in szName.lower()):
							setShowListIdx.add(iListIdx)
			else:
				listShownHeaderIdx = []
				for iH, iHeaderIdx in enumerate(listHeaderIdx):
					if (iH + 1) < len(listHeaderIdx):
						iNextHeaderIdx = listHeaderIdx[iH + 1]
					else:
						iNextHeaderIdx = len(self.list)
					bSectionHasMatch = False
					# Scan items in this header section for matches.
					for j in range(iHeaderIdx + 1, iNextHeaderIdx):
						it = self.list[j]
						if it[1] != -1:
							szName = it[0]
							if (szName is not None) and (szFilter in szName.lower()):
								bSectionHasMatch = True
								setShowListIdx.add(j)
					if bSectionHasMatch:
						listShownHeaderIdx.append(iHeaderIdx)
						setShowListIdx.add(iHeaderIdx)

				# Include a blank separator ("", -1) before each shown header, except the first shown section.
				for iK in range(1, len(listShownHeaderIdx)):
					iHeaderIdx = listShownHeaderIdx[iK]
					iSpacerIdx = iHeaderIdx - 1
					if iSpacerIdx >= 0:
						it = self.list[iSpacerIdx]
						if it[1] == -1:
							szTitle = it[0]
							if (szTitle is None) or (len(szTitle.strip()) == 0):
								setShowListIdx.add(iSpacerIdx)

			# Build list-index -> displayed-row mapping for correct highlighting in pediaJump.
			self.SAS_listIdxToRow = {}

			# <!-- custom: rebuild arrow-navigation caches (chatgpt 5.2 + claude opus 4.5) -->
			self.SAS_selectableListIdx = []
			self.SAS_itemToSelectablePos = {}

		i = 0
		for idx, item in enumerate(self.list):
			data1 = item[1] # advc.001: Moved up

			# <!-- custom: if filtering, skip rows not selected by our header-aware filter (chatgpt 5.2 + claude opus 4.5) -->
			if bFiltering:
				if idx not in setShowListIdx:
					continue

			# <!-- custom: record mapping from original list index to displayed row index (chatgpt 5.2 + claude opus 4.5) -->
			if self.SAS_listIdxToRow is not None:
				self.SAS_listIdxToRow[idx] = i
			# <!-- custom: End - type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->

			# <!-- custom: make a common initial variable so we can tweak it in specific elif or such blocks as we see fit and keep common logic at the end; using a long name to avoid weird python scope inheritance issues to unrelated scopes -->
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
				# <!-- custom: we cannot change to data1 here as we changed it in this scope so need to properly use item[1] rather as chatgpt 5.2 recommends and that indeed lead to an issue ingame of displaying always same sevopedia concept's text. To be safe, not changing it in other places as well unless we need to -->
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

				# <!-- custom: in sevopedia civics, order civics by civic type (e.g. Government, Economy, etc.), as RFC DOC mod does and that this code is based on, with the help of chatgpt 5.2 thanks -->
				# Step 1 (required): Teach your SevoPediaMain.placeItems() to handle headers
				# Right now your placeItems() always does info(item[1]).getButton(), so any header rows like ("Government", -1) would crash. RFC DoC fixes this by treating item[1] == -1 as a non-clickable, highlighted header row.
				# <!-- custom: similarly, in sevopedia techs, group techs by era (e.g. Ancient Era, Classical Era, etc.) instead of one long list. Also did similarly for sevopedia buildings and similar pages. Code added with the help of chatgpt 5.2 thanks -->
				# (That is basically the DoC approach, adapted to your variable names.). After this, your item lists can safely contain (..., -1) headers and blank separators.
				if data1 == -1:
					sTitlePlaceItems = CyTranslator().changeTextColor(item[0], self.COLOR_HIGHLIGHT_TEXT)
					widgetPlaceItems = WidgetTypes.WIDGET_GENERAL
					szButtonPlaceItems = ""

			# <!-- custom: cache selectable rows for arrow navigation (skip headers/spacers) (chatgpt 5.2 + claude opus 4.5) -->
			if item[1] != -1:
				self.SAS_itemToSelectablePos[item[1]] = len(self.SAS_selectableListIdx)
				self.SAS_selectableListIdx.append(idx)

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
		iCategory = self.SAS_mainLinkToCategory.get(szLink, None)
		if iCategory is not None:
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, iCategory, True, True)

		for szNumMethod, szInfoMethod, iCategory in self.SAS_linkMatchDefs:
			iCount = getattr(gc, szNumMethod)()
			getInfo = getattr(gc, szInfoMethod)
			for i in range(iCount):
				info = getInfo(i)
				if info and info.isMatchForLink(szLink, False):
					return self.pediaJump(iCategory, i, True, True)



	def handleInput (self, inputClass):
		# Forward to leader page (existing behavior).
		if (inputClass.getPythonFile() == SevoScreenEnums.PEDIA_LEADERS):
			return self.pediaLeader.handleInput(inputClass)

		# <!-- custom: type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->
		# Index has its own input (existing behavior).
		if self.SAS_USE_BOTTOM_TABS and self.isIndexShowing():
			return self.pediaIndex.handleInput(inputClass)
		if self.isContentsShowing() and self.iCategory == SevoScreenEnums.PEDIA_INDEX:
			iHandled = self.pediaIndex.handleInput(inputClass)
			if iHandled:
				return iHandled

		# <!-- custom: clear button click (chatgpt 5.2 + claude opus 4.5) -->
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
			if inputClass.getFunctionName() == self.SAS_SEARCH_CLEAR_ID:
				if self.SAS_isSearchActive():
					self.SAS_szSearchString = u""
					# <!-- custom: reset debounce state when clearing search (chatgpt 5.2 + claude opus 4.5) -->
					self.SAS_keyDebounceByKey = {}
					if self.SAS_lastItemsWidget is not None:
						self.placeItems(self.SAS_lastItemsWidget, self.SAS_lastItemsInfo)
				return 1

		# <!-- custom: type-to-filter keyboard input using InputTypes constants like other mod(s) do (chatgpt 5.2 + claude opus 4.5) -->
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CHARACTER:
			if self.SAS_lastItemsWidget is not None and self.isContentsShowing():
				screen = self.getScreen()
				if screen.isActive():
					if (not inputClass.isAltKeyDown()) and (not inputClass.isCtrlKeyDown()):
						iKey = inputClass.getData()
						
						# <!-- custom: debounce per key so fast typing does not produce interleaved duplicates like 'gr' -> 'grgr' (chatgpt 5.2 + claude opus 4.5) -->
						if self.SAS_shouldDebounceKey(iKey):
							if self.SAS_keyDebounceByKey.get(iKey, 0):
								self.SAS_keyDebounceByKey[iKey] = 0
								return 1
							self.SAS_keyDebounceByKey[iKey] = 1
						
						szChar = self.SAS_getVisibleCharacter(inputClass)
						if len(szChar) > 0:
							self.SAS_szSearchString = self.SAS_szSearchString + szChar
							self.placeItems(self.SAS_lastItemsWidget, self.SAS_lastItemsInfo)
							return 1
						
						# Handle backspace to delete last character
						if iKey == int(InputTypes.KB_BACKSPACE):
							if len(self.SAS_szSearchString) > 0:
								self.SAS_szSearchString = self.SAS_szSearchString[:-1]
								self.placeItems(self.SAS_lastItemsWidget, self.SAS_lastItemsInfo)
								return 1
						# Handle escape to clear search
						elif iKey == int(InputTypes.KB_ESCAPE):
							if self.SAS_isSearchActive():
								self.SAS_szSearchString = u""
								# <!-- custom: reset debounce state when clearing search (chatgpt 5.2 + claude opus 4.5) -->
								self.SAS_keyDebounceByKey = {}
								self.placeItems(self.SAS_lastItemsWidget, self.SAS_lastItemsInfo)
								return 1
						# <!-- custom: Based on C2C mod's implementation thanks: add navigation of the item list with the UP/DOWN arrow keys. Code adjusted for AdvCiv-SAS with the help of chatgpt 5.2 and claude opus 4.5. -->
						# <!-- custom: arrow key navigation for item list (chatgpt 5.2 + claude opus 4.5) -->
						# Handle UP arrow to navigate to previous item
						elif iKey == int(InputTypes.KB_UP):
							if self.SAS_navigateItemList(-1):
								return 1
						# Handle DOWN arrow to navigate to next item
						elif iKey == int(InputTypes.KB_DOWN):
							if self.SAS_navigateItemList(1):
								return 1
						# <!-- custom: End - Based on C2C mod's implementation thanks: add navigation of the item list with the UP/DOWN arrow keys. Code adjusted for AdvCiv-SAS with the help of chatgpt 5.2 and claude opus 4.5. -->

		# Existing TOC/INDEX buttons.
		if self.SAS_USE_BOTTOM_TABS:
			if (inputClass.getFunctionName() == self.TOC_ID):
				self.showContents()
				return 1
			elif (inputClass.getFunctionName() == self.INDEX_ID):
				self.showIndex()
				return 1
		
		return 0
		# <!-- custom: End - type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->



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
		# <!-- custom: type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->
		# <!-- custom: also delete search widgets when deleting list widgets (chatgpt 5.2 + claude opus 4.5) -->
		self.SAS_deleteSearchWidgets()
		self.pediaIndex.SAS_indexDeleteSearchWidgets()
		# <!-- custom: End - type-to-filter search bar for the left item list (in the same style as done in other mod(s)) (chatgpt 5.2 + claude opus 4.5) -->

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
	
	# <!-- custom: according to chatgpt 5.2 and if i understood it correctly, TERRAIN_HILL and TERRAIN_PEAK already exist in our terrains list as per CIV4TerrainInfos.xml. However they have an <bGraphicalOnly>1</bGraphicalOnly> so they are excluded from the display. Reveal them from the display here. We'll later handle their incorrect <bWater>1</bWater> property when handling the list. At least we have all the terrains we need now -->
	# <!-- custom: generalize this logic by using an alternative helper that we can use if we need to (e.g. for peak, hill, or anything else we'd want it to use it for) without affecting or slowing down the other parts of the code that already use the (filtered/default) getSortedList, should be safer or cleaner for performance too if i'm not mistaken as chatgpt 5.2 noted if i understood it correctly. It would also allow to add new entries in the future in an easier and cleaner way as well if i'm not mistaken i mean. -->
	# Wrapper for clarity: same as getSortedList(), but includes GraphicalOnly entries (“Unfiltered” here specifically means “don’t filter GraphicalOnly”.).
	# Useful for categories where GraphicalOnly infos are still meaningful in Sevopedia (e.g. terrains like TERRAIN_HILL / TERRAIN_PEAK in our CIV4TerrainInfos.xml).
	def getUnfilteredSortedList(self, numInfos, getInfo, noSort=False, bCheckGraphicalOnly=False):
		return self.getSortedList(numInfos, getInfo, noSort, bCheckGraphicalOnly)

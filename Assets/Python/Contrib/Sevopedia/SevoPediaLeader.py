# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
#
# <!-- custom: part of the code here (placeFavourites in particular, but not exhaustive or maybe exhaustive
# or not, anyways, is imported from RFC Dawn of Civilization mod:
# C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\RFC Dawn of Civilization\Assets\Python\Pedia\CvPediaLeader.py
# which may be modified or not for AdvCiv-SAS
# 
# And a big part of the code, in particular the AI Personality code, is almost entirely provided by ChatGPT (and the
# result of my prompts to it), which i may have then modified or not for AdvCiv-SAS
#
# Apart from that, i may have modified the existing base advciv code (that i found good enough so using it as a base
# rather than removing it, and quite good actually, only needing tweaking but is a solid base (i think or not) maybe
# or not, anyways, ) or not for AdvCiv-SAS, anyways,
# -->

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
import random

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

# <!-- custom: 
# Refactored AI aggregate definitions into class-level constants for clarity and performance
#
# This commit moves the `aggregates` and `ai_attribute_categories` dictionaries from the `placeAIPersonalityPanel` method into class-level variables (`AGGREGATES` and `AI_ATTRIBUTE_CATEGORIES`) in SevoPediaLeader.py.
#
# These structures define which AI XML values are used for each aggregate trait (like "Aggressive" or "Sneaky") and group them into categories for visual organization. By moving them to the class level, we:
# - Avoid recomputing or redefining them every time a new leader is viewed in the Sevopedia
# - Keep the data in one clear location for easy editing, debugging, and extension
# - Improve readability and make the logic reusable in other parts of the Sevopedia if needed later
#
# This is part of an ongoing effort to improve performance and modularity of the AI Personality panel, while staying true to the game's Python 2.4 style and Civ4 modding conventions. Constants are written in UPPER_CASE for clarity, even if this differs slightly from other parts of Sevopedia code.
#
# 
# see also the ChatGPT breakdown (at the end of this
# commit's message) of an earlier version of the refactor, when we moved
# these to init for more information if needed:
# https://github.com/wonderingabout/AdvCiv-SAS/commit/bd42f5ad49d4370e9ef41081da6ed5e652939250
# -->



AI_HEADER_AGGREGATES = "Aggregates (% normalized)"



AI_HEADER_WAR_STRATEGY = "War Strategy"
AI_HEADER_DIPLOMACY = "Diplomacy"
AI_HEADER_VICTORY_STRATEGY = "Victory Strategy (currently not working)"
AI_HEADER_ECONOMIC_PREFERENCES = "Economic Preferences"
AI_HEADER_ATTITUDE_MODIFIERS = "Attitude Modifiers"
AI_HEADER_TRADE_THRESHOLDS = "Trade Thresholds"


# <!-- custom: at which index we skip line in the AI_HEADER_AGGREGATES category,
# between its subcategories, for example afetr the 6th element power tracker
# currently we would skip lines here before displaying Peaceful in the next
# category, for visual clarity
# -->
AI_AGGREGATE_CATEGORY_BREAKS = [6, 13]



AI_ATTRIBUTE_CATEGORIES = {
	AI_HEADER_WAR_STRATEGY: [
		("Max War Rand", "getMaxWarRand"),
		("Max War Nearby Power Ratio", "getMaxWarNearbyPowerRatio"),
		("Max War Distant Power Ratio", "getMaxWarDistantPowerRatio"),
		("Max War Min Adjacent Land Percent", "getMaxWarMinAdjacentLandPercent"),
		("Limited War Rand", "getLimitedWarRand"),
		("Limited War Power Ratio", "getLimitedWarPowerRatio"),
		("Dogpile War Rand", "getDogpileWarRand"),
		("Make Peace Rand", "getMakePeaceRand"),
	],
	AI_HEADER_DIPLOMACY: [
		("Base Attitude", "getBaseAttitude"),
		("Peace Weight", "getBasePeaceWeight"),
		("Warmonger Respect", "getWarmongerRespect"),
		("Demand Sneak Prob", "getDemandRebukedSneakProb"),
		("Demand War Prob", "getDemandRebukedWarProb"),
		("Refuse Talk Threshold", "getRefuseToTalkWarThreshold"),
		("No Tech Trade Threshold", "getNoTechTradeThreshold"),
		("Tech Trade Known %", "getTechTradeKnownPercent"),
		("Declare War Trade Rand", "getDeclareWarTradeRand"),
	],
	AI_HEADER_VICTORY_STRATEGY: [
		("Culture Victory Weight", "getCultureVictoryWeight"),
		("Space Victory Weight", "getSpaceVictoryWeight"),
		("Conquest Victory Weight", "getConquestVictoryWeight"),
		("Domination Victory Weight", "getDominationVictoryWeight"),
		("Diplomacy Victory Weight", "getDiplomacyVictoryWeight"),
	],
	AI_HEADER_ECONOMIC_PREFERENCES: [
		("Espionage Weight", "getEspionageWeight"),
		("Build Unit Prob", "getBuildUnitProb"),
		("Base Attack Odds", "getBaseAttackOddsChange"),
		("Attack Odds Rand", "getAttackOddsChangeRand"),
		("Wonder Construct Rand", "getWonderConstructRand"),
		("Max Gold Trade %", "getMaxGoldTradePercent"),
		("Max GPT Trade %", "getMaxGoldPerTurnTradePercent"),
	],
	AI_HEADER_ATTITUDE_MODIFIERS: [
		("Worse Rank Attitude Change", "getWorseRankDifferenceAttitudeChange"),
		("Better Rank Attitude Change", "getBetterRankDifferenceAttitudeChange"),
		("Close Borders Attitude Change", "getCloseBordersAttitudeChange"),
		("Same Religion Attitude Limit", "getSameReligionAttitudeChangeLimit"),
		("Diff Religion Attitude Limit", "getDifferentReligionAttitudeChangeLimit"),
		("Share War Attitude Limit", "getShareWarAttitudeChangeLimit"),
		("Favorite Civic Attitude Limit", "getFavoriteCivicAttitudeChangeLimit"),
	],
	AI_HEADER_TRADE_THRESHOLDS: [
		("Tech Refuse Attitude", "getTechRefuseAttitudeThreshold"),
		("City Refuse Attitude", "getCityRefuseAttitudeThreshold"),
		("Strategic Bonus Refuse Attitude", "getStrategicBonusRefuseAttitudeThreshold"),
		("Health Bonus Refuse Attitude", "getHealthBonusRefuseAttitudeThreshold"),
		("Happiness Bonus Refuse Attitude", "getHappinessBonusRefuseAttitudeThreshold"),
		("Map Refuse Attitude", "getMapRefuseAttitudeThreshold"),
		("Declare War Refuse Attitude", "getDeclareWarRefuseAttitudeThreshold"),
		("Declare War On Them Refuse", "getDeclareWarThemRefuseAttitudeThreshold"),
		("Stop Trading Refuse", "getStopTradingRefuseAttitudeThreshold"),
		("Stop Trading Them Refuse", "getStopTradingThemRefuseAttitudeThreshold"),
		("Adopt Civic Refuse", "getAdoptCivicRefuseAttitudeThreshold"),
		("Convert Religion Refuse", "getConvertReligionRefuseAttitudeThreshold"),
		("Open Borders Refuse", "getOpenBordersRefuseAttitudeThreshold"),
		("Vassal Refuse", "getVassalRefuseAttitudeThreshold"),
	],
}



# Aggregates grouped thematically in code (for clarity and future doc)
AI_AGGREGATES = [
	# === WAR / CONFLICT BEHAVIOR ===
	("Aggressive", [
		("getMaxWarRand", False),
		("getBuildUnitProb", False),
		("getBaseAttackOddsChange", False)
	]),
	("Dogpiler", [
		("getDogpileWarRand", False),
		("getDeclareWarTradeRand", False),
		("getWarmongerRespect", False)
	]),
	("Allied Warmonger", [
		("getWarmongerRespect", False),
		("getShareWarAttitudeChangeLimit", False),
		("getDogpileWarRand", False)
	]),
	("Reckless", [
		("getBaseAttackOddsChange", False),
		("getLimitedWarRand", True),
		("getDeclareWarRefuseAttitudeThreshold", True)
	]),
	("Cautious", [
		("getLimitedWarRand", False),
		("getLimitedWarPowerRatio", False),
		("getMaxWarNearbyPowerRatio", True)
	]),
	("Power Tracker", [
		("getMaxWarNearbyPowerRatio", False),
		("getMaxWarDistantPowerRatio", False),
		("getLimitedWarPowerRatio", False)
	]),

	# === DIPLOMACY & PERSONALITY ===
	("Peaceful", [
		("getMakePeaceRand", False),
		("getBasePeaceWeight", False),
		("getRefuseToTalkWarThreshold", True)
	]),
	("Diplomatic", [
		("getBasePeaceWeight", False),
		("getNoTechTradeThreshold", True),
		("getOpenBordersRefuseAttitudeThreshold", True)
	]),
	("Stubborn", [
		("getTechRefuseAttitudeThreshold", False),
		("getCityRefuseAttitudeThreshold", False),
		("getStopTradingRefuseAttitudeThreshold", False),
		("getAdoptCivicRefuseAttitudeThreshold", False),
		("getConvertReligionRefuseAttitudeThreshold", False)
	]),
	("Flexible", [
		("getAdoptCivicRefuseAttitudeThreshold", True),
		("getConvertReligionRefuseAttitudeThreshold", True),
		("getFavoriteCivicAttitudeChangeLimit", True)
	]),
	("Grudgy", [
		("getWorseRankDifferenceAttitudeChange", False),
		("getCloseBordersAttitudeChange", False),
		("getDifferentReligionAttitudeChangeLimit", False)
	]),
	("Collaborative", [
		("getShareWarAttitudeChangeLimit", False),
		("getSameReligionAttitudeChangeLimit", False),
		("getFavoriteCivicAttitudeChangeLimit", False)
	]),
	("Isolationist", [
		("getOpenBordersRefuseAttitudeThreshold", False),
		("getDeclareWarRefuseAttitudeThreshold", False),
		("getStopTradingRefuseAttitudeThreshold", False)
	]),
	("Dealbreaker", [
		("getRefuseToTalkWarThreshold", False),
		("getTechRefuseAttitudeThreshold", False),
		("getStopTradingRefuseAttitudeThreshold", False)
	]),
	("Vassalizer", [
		("getVassalRefuseAttitudeThreshold", False),
		("getPowerWeightModifier", False),
		("getRefuseToTalkWarThreshold", True)
	]),

	# === ECONOMIC / STRATEGIC ===
	("Trader", [
		("getTechTradeKnownPercent", False),
		("getMaxGoldTradePercent", False),
		("getMapRefuseAttitudeThreshold", True)
	]),
	("Tech Hoarder", [
		("getNoTechTradeThreshold", False),
		("getTechRefuseAttitudeThreshold", False),
		("getTechTradeKnownPercent", True)
	]),
	("Gold Hoarder", [
		("getMaxGoldTradePercent", False),
		("getMaxGoldPerTurnTradePercent", False),
		("getCityRefuseAttitudeThreshold", False)
	]),
	("Stingy", [
		("getHealthBonusRefuseAttitudeThreshold", False),
		("getHappinessBonusRefuseAttitudeThreshold", False),
		("getStrategicBonusRefuseAttitudeThreshold", False)
	]),
	("Builder", [
		("getWonderConstructRand", True),
		("getBuildUnitProb", True),
		("getMaxGoldTradePercent", False)
	]),
	("Wonder Chaser", [
		("getWonderConstructRand", True),
		("getBuildUnitProb", True),
		("getBasePeaceWeight", False)
	]),
	("Culture Pusher", [
		("getCultureVictoryWeight", False),
		("getMaxWarMinAdjacentLandPercent", True),
		("getSameReligionAttitudeChangeLimit", False)
	]),

	# === HYBRID / ABSTRACT BEHAVIOR ===
	("Opportunistic", [
		("getDeclareWarTradeRand", False),
		("getTechTradeKnownPercent", False),
		("getWarmongerRespect", False)
	]),
	("Sneaky", [
		("getDemandRebukedSneakProb", False),
		("getDogpileWarRand", False),
		("getEspionageWeight", False)
	]),
	("Civic Enforcer", [
		("getFavoriteCivicAttitudeChangeLimit", False),
		("getAdoptCivicRefuseAttitudeThreshold", False),
		("getNoTechTradeThreshold", False)
	]),
	("Globalist", [
		("getTechTradeKnownPercent", False),
		("getMaxWarDistantPowerRatio", False),
		("getDeclareWarTradeRand", False)
	]),
	("Micro-manager", [
		("getAttackOddsChangeRand", False),
		("getMakePeaceRand", False),
		("getRefuseToTalkWarThreshold", False)
	]),
	("Unpredictable", [
		("getAttackOddsChangeRand", False),
		("getLimitedWarRand", False),
		("getDeclareWarTradeRand", False)
	]),
	("Border Watcher", [
		("getMaxWarMinAdjacentLandPercent", False),
		("getCloseBordersAttitudeChange", False),
		("getMaxWarNearbyPowerRatio", False)
	])
]



# <!-- custom: performance improvement, store the all leaders calculation once
# then refer to the result directly here (cache according to ChatGPT this
# called and i intutiively or from general culture of this IT things but
# anyways agree maybe anyways)
# Also read ChatGPT here breakdown for (much more) details (but mine is cool
# too maybe and i helped it and hapyp of result wit it etc but anyways (to give
# myself soem credit too xd but anyways)):
# https://github.com/wonderingabout/AdvCiv-SAS/commit/9b7a6735ce834e0d85aed7f94bff17a9155a0853
# -->
# Precomputed min/max cache for all AI personality functions
AI_VALUE_RANGES = {}

def cache_ai_value_ranges():
	global AI_VALUE_RANGES
	numLeaders = gc.getNumLeaderHeadInfos()
	unique_funcs = set()

	# Collect all function names from both individual attributes and aggregates
	for category_attrs in AI_ATTRIBUTE_CATEGORIES.values():
		for _, funcName in category_attrs:
			unique_funcs.add(funcName)
	for _, funcPairs in AI_AGGREGATES:
		for funcName, _ in funcPairs:
			unique_funcs.add(funcName)

	for funcName in unique_funcs:
		values = []
		for i in range(numLeaders):
			try:
				val = getattr(gc.getLeaderHeadInfo(i), funcName)()
				values.append(val)
			except:
				pass
		if values:
			AI_VALUE_RANGES[funcName] = (min(values), max(values))

# Initialize the cache
cache_ai_value_ranges()



# <!-- custom: -->
# Precomputed aggregate scores for each leader
AI_AGGREGATE_SCORES = {}

def cache_ai_aggregate_scores():
	global AI_AGGREGATE_SCORES
	numLeaders = gc.getNumLeaderHeadInfos()

	for iLeader in range(numLeaders):
		leaderInfo = gc.getLeaderHeadInfo(iLeader)
		leaderScores = {}
		for label, fields in AI_AGGREGATES:
			total = 0
			count = 0
			for funcName, inverse in fields:
				try:
					val = getattr(leaderInfo, funcName)()
					min_val, max_val = AI_VALUE_RANGES.get(funcName, (0, 0))
					if max_val != min_val:
						norm = float(val - min_val) / float(max_val - min_val)
						if inverse:
							norm = 1.0 - norm
						total += int(norm * 100)
						count += 1
				except:
					pass
			if count > 0:
				leaderScores[label] = total // count
			else:
				leaderScores[label] = 0
		AI_AGGREGATE_SCORES[iLeader] = leaderScores

# Call this after cache_ai_value_ranges()
cache_ai_aggregate_scores()




class SevoPediaLeader:

	def __init__(self, main):
		self.iLeader = -1
		self.top = main

		self.X_LEADERHEAD_PANE = self.top.X_PEDIA_PAGE
		self.Y_LEADERHEAD_PANE = self.top.Y_PEDIA_PAGE
		# <!-- custom: for the ratio of the portrait, make it (at least i chose to make it
		# explained after this anyways) match the ingame diplomacy portrait ratio
		# 240 / 290 = 0,8278
		# i have measured this on my (4K but anyways) screen in windowed mode (for dev mod but anyways)
		# - in sevopedia (before my fix): 421 x 488 	(ratio: 0,8627)    ;    (reverse-ratio: 1,1591)
		# - ingame diplomacy: 709 x 866 				(ratio: 0,8187)    ;    (reverse-ratio: 1,1214)
		# (data extracted from my notes_about_art_design file in this mod, please look at it or the filename
		# containing this data or similar for details)
		#
		# Since the value (ratio in particular is different than what i measured (0,8627 vs 0,8278 here, i will
		# try to adjust it based on that to hopefully have a matching ratio or a bit better or more or not,
		# anyways, )) (while also increasing the portrait/picture which i think is a bit small currently, maybe
		# more immersive or/and pleasant or not, anyways, )
		# Now ratio is 287 / 350 = 0,8200 (much closer to 0,8187 that i measured in game diplomacy (see above,
		# anyways), while also increasing size (of the portrait anyways) anyways)
		#
		# This looks good but i want to try to increase it more (portrait size, anyways, ):
		# Now 327 / 400 = 0,8175 (which is very close to 0,8187 while also a bigger picture, anyways)
		# Increasing it more is maybe possible but we start to see the pixels in the animations (see Gandhi's arm)
		# not being straight for example, if we replace animations with images like with/for Ogiso Igodo (Kingdom
		# of Benin, anyways) then hese enhanced portaits would be better and more epic, will see if i increase it
		# more or not, maybe leaving as is at least for now or not, anyways,
		#
		# Actually all this calculation is not exactly accurate because W_LEADERHEAD_PANE and W_LEADERHEAD are
		# different in this base advciv / sevopedia(?) code, but hopefully accurate enough and ratio should be
		# much closer now to the ingame diplomacy ratio, hopefully less stretched but not sure or guaranteed, should
		# be for images i send as replacements of animations though as i base them on the ingame diplomacy's ratio,
		# not the old sevopedia leader portait ratio, anyways, so now the new sevopedia ratio for the leader portrait
		# i have added is hopefully much much closer to the old and as of now still existing ratio of the ingame
		# diplomacy leader portrait, which i don't think i'm changing anytime soon as it is most likely more tedious for
		# questionable gain, so using this one as a basis rather, not that is undoable but probably much harder and not
		# necessarily worth it, and if animations are based on the diplomacy ingame ratio rather then they may also display
		# better in the sevopedia with my new sevopedia ratio, (which intuitively or from a quick glance seems to be the
		# case, image looks less compressed on its sides but not sure or guaranteed, check yourself if want to be sure or
		# not, but i hope this helps, and that being said, anyways) anyways
		# -->
		self.W_LEADERHEAD_PANE = 327
		self.H_LEADERHEAD_PANE = 400

		# <!-- custom:
		# 1) absolute dimensions first -->

		# <!-- custom: make room to add AI personality panel -->
		self.W_AI_PERSONALITY = 395

		self.SMALL_MARGIN = 10
		self.MEDIUM_MARGIN = 20
		# <!-- custom: we also need this information sooner, move it here with the more absolute
		# dimensions of some elements
		self.W_CIV = 64
		self.H_CIV = 64
		self.CIV_MARGIN = 0
		self.CIV_DISELEVATION = 38
		
		self.H_FAVORITES = 110

		# <!-- custom:
		# 2) relative dimensions or/and positions then -->

		self.W_LEADERHEAD = self.W_LEADERHEAD_PANE - 30
		self.H_LEADERHEAD = self.H_LEADERHEAD_PANE - 34
		self.X_LEADERHEAD = self.X_LEADERHEAD_PANE + (self.W_LEADERHEAD_PANE - self.W_LEADERHEAD) / 2
		self.Y_LEADERHEAD = self.Y_LEADERHEAD_PANE + (self.H_LEADERHEAD_PANE - self.H_LEADERHEAD) / 2 + 3

		# <!-- custom: we need self.W_HISTORY before the favourites coordinates, (even though the history
		# panel is placed under/after the favourites panel when i constructed the page's "spacing" and
		# dimensions of (and between) panels, anyways) because/as the favourites panel uses/needs/is based on
		# the history panel's (relative) position, anyways --> 
		self.W_HISTORY = self.top.R_PEDIA_PAGE - (2 * (self.W_AI_PERSONALITY + self.MEDIUM_MARGIN)) - self.X_LEADERHEAD_PANE

		self.X_FAVORITES = self.X_LEADERHEAD_PANE
		self.Y_FAVORITES = self.Y_LEADERHEAD_PANE + self.H_LEADERHEAD_PANE + self.SMALL_MARGIN
		self.W_FAVORITES = self.W_HISTORY - self.W_CIV - self.SMALL_MARGIN

		self.X_HISTORY = self.X_LEADERHEAD_PANE
		self.Y_HISTORY = self.Y_FAVORITES + self.H_FAVORITES + self.SMALL_MARGIN
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY

		# <!-- custom: traits have the green color somehow,
		#
		# do not comment-out until i find how so i
		#
		# can feed it / = ask ChatGPT about it if it has ideas -->
		#self.X_TRAITS = self.X_LEADERHEAD_PANE + self.W_LEADERHEAD_PANE + 10
		#self.Y_TRAITS = self.Y_LEADERHEAD_PANE + 80 + 10
		#self.W_TRAITS = self.top.R_PEDIA_PAGE - self.W_AI_PERSONALITY - self.X_TRAITS - self.MEDIUM_MARGIN
		#self.H_TRAITS = 64 + 64 - self.Y_TRAITS
		self.X_TRAITS = self.X_LEADERHEAD_PANE + self.W_LEADERHEAD_PANE + self.SMALL_MARGIN
		self.Y_TRAITS = self.Y_LEADERHEAD_PANE
		self.W_TRAITS = self.W_HISTORY - self.W_LEADERHEAD_PANE - self.SMALL_MARGIN
		self.H_TRAITS = self.H_LEADERHEAD_PANE

		# <!-- custom: move the civ (flag) closer to favourite civis and religions or somewhere else,
		# more beautiful and less cumbersome this way maybe i think, anyways -->
		self.X_CIV = self.X_HISTORY + self.W_HISTORY - self.CIV_MARGIN - self.W_CIV
		# <!-- custom: put the flag/civ at the middle Y of the favourites panel -->
		# <!-- custom: quite high as compared to favourites panel's lowest point -->
		self.Y_CIV = self.Y_FAVORITES + self.CIV_DISELEVATION

		# <!-- custom: the rest of the data here, as it is dependent on other data we need first
		# that (i.e. before being able to add these) -->
		self.X_AI_PERSONALITY = self.top.R_PEDIA_PAGE - self.W_AI_PERSONALITY 
		self.Y_AI_PERSONALITY = self.Y_LEADERHEAD_PANE
		self.H_AI_PERSONALITY = self.H_LEADERHEAD_PANE + self.SMALL_MARGIN + self.H_FAVORITES + self.SMALL_MARGIN + self.H_HISTORY



	def interfaceScreen(self, iLeader):
		self.iLeader = iLeader

		# <!-- custom: change call order to match filling/building order, generally
		# from top left to bottom and left to right but not always, reordering in
		# such a way is maybe a bit more intuitive this way perhaps or/and clearer
		# or/and helpful or not or other etc anyways, -->
		self.placeLeader(iLeader)
		self.placeFavorites()
		self.placeHistory()
		self.placeCiv()
		self.placeTraits()
		self.placeAIPersonalityPanel(iLeader)



	# <!-- custom: wrap leader placement in a specific function for clarity
	# or/and flexibility or not anyways,
	# -->
	def placeLeader(self, iLeader):
		screen = self.top.getScreen()
		leaderPanelWidget = self.top.getNextWidgetName()
		screen.addPanel(leaderPanelWidget, "", "", True, True, self.X_LEADERHEAD_PANE, self.Y_LEADERHEAD_PANE, self.W_LEADERHEAD_PANE, self.H_LEADERHEAD_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		self.leaderWidget = self.top.getNextWidgetName()
		screen.addLeaderheadGFC(self.leaderWidget, iLeader, AttitudeTypes.ATTITUDE_PLEASED, self.X_LEADERHEAD, self.Y_LEADERHEAD, self.W_LEADERHEAD, self.H_LEADERHEAD, WidgetTypes.WIDGET_GENERAL, -1, -1)



	# <!-- custom: imported from RFC DOC and modified or/and not for AdvCiv-SAS, anyways, -->
	def placeFavorites(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		screen.addPanel(panel, CyTranslator().getText("TXT_KEY_PEDIA_FAVOURITE_CIVICS_AND_RELIGIONS", ()), "", False, True, self.X_FAVORITES, self.Y_FAVORITES, self.W_FAVORITES, self.H_FAVORITES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.enableSelect(panel, False)
		screen.attachLabel(panel, "", "  ")

		# Civic
		iCivic = gc.getLeaderHeadInfo(self.iLeader).getFavoriteCivic()
		if iCivic > -1:
			screen.attachImageButton(panel, "", gc.getCivicInfo(iCivic).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, iCivic, 1, False)

		# Religion
		iReligion = gc.getLeaderHeadInfo(self.iLeader).getFavoriteReligion()
		if iReligion > -1:
			screen.attachImageButton(panel, "", gc.getReligionInfo(iReligion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iReligion, 1, False)



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, "", "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		historyTextName = self.top.getNextWidgetName()
		CivilopediaText = gc.getLeaderHeadInfo(self.iLeader).getCivilopedia()
		CivilopediaText = u"<font=2>" + CivilopediaText + u"</font>"
		screen.attachMultilineText(panelName, historyTextName, CivilopediaText, WidgetTypes.WIDGET_GENERAL,-1,-1, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: logo / flag of the civ -->
	def placeCiv(self):
		screen = self.top.getScreen()
		for iCiv in range(gc.getNumCivilizationInfos()):
			civ = gc.getCivilizationInfo(iCiv)
			if civ.isLeaders(self.iLeader):
				screen.setImageButton(self.top.getNextWidgetName(), civ.getButton(), self.X_CIV, self.Y_CIV, self.W_CIV, self.H_CIV, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCiv, 1)



	# advc.001 (from Taurus): Static for use by SevoPediaMain; body cut from placeTraits.
	@staticmethod
	def getCiv(iLeader):
		iNumCivs = 0
		for iCiv in range(gc.getNumCivilizationInfos()):
			if gc.getCivilizationInfo(iCiv).isLeaders(iLeader):
				iNumCivs += 1
				iLeaderCiv = iCiv
		# <advc.001> (No functional change here)
		if iNumCivs != 1:
			return -1
		return iLeaderCiv # </advc.001>



	def placeTraits(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_TRAITS", ()), "", True, False, self.X_TRAITS, self.Y_TRAITS, self.W_TRAITS, self.H_TRAITS, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		# advc.001: Civ search moved into a static method
		szSpecialText = CyGameTextMgr().parseLeaderTraits(self.iLeader, SevoPediaLeader.getCiv(self.iLeader), False, True)
		szSpecialText = szSpecialText[1:]
		screen.addMultilineText(listName, szSpecialText, self.X_TRAITS+5, self.Y_TRAITS+30, self.W_TRAITS-10, self.H_TRAITS-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: based on placeHistory then tweaked or/and modified or/and not
	# also data fetching logic mostly if not entirely provided by ChatGPT, or/and with
	# some additions or modifications or removals or other i did or did not, anyways

	# <!-- custom: currently if not always logic not used of different symbols for different categories,
	# may be useful or not keeping as is or not, anyways
	# -->
	#attr_types = {
	#	AI_HEADER_WAR_STRATEGY: "threat",
	#	AI_HEADER_DIPLOMACY: "diplomacy",
	#	AI_HEADER_VICTORY_STRATEGY: "efficiency",
	#	AI_HEADER_ECONOMIC_PREFERENCES: "efficiency",
	#	AI_HEADER_ATTITUDE_MODIFIERS: "diplomacy",
	#	AI_HEADER_TRADE_THRESHOLDS: "diplomacy",
	#	AI_HEADER_AGGREGATES: "efficiency"
	#}



	# <!-- custom: also note alternative symbols to consider too maybe:
	# "+", "o" (the letter o renders quite well but anyways)

	#symbols = {
	#	"threat": "#",
	#	"efficiency": ">",
	#	"diplomacy": "="
	#}



	# <!-- custom: currently if not always logic not used of different symbols for different categories,
	# may be useful or not keeping as is or not, anyways
	#attrType = attr_types.get(category, "efficiency")
	#symbol = symbols.get(attrType, ">")
	# -->



	#<!-- custom: link not working to concept page of ai personality, disabling it for now, if not always or not etc anyways, -->



	def placeAIPersonalityPanel(self, iLeader):
		screen = self.top.getScreen()

		# === FIRST PANEL ===
		firstPanelName = self.top.getNextWidgetName()
		screen.addPanel(firstPanelName, localText.getText("TXT_KEY_AI_PERSONALITY", ()) + " (1)", "", True, True,
						self.X_AI_PERSONALITY, self.Y_AI_PERSONALITY,
						self.W_AI_PERSONALITY, self.H_AI_PERSONALITY,
						PanelStyles.PANEL_STYLE_BLUE50)

		# === SECOND PANEL ===
		secondPanelName = self.top.getNextWidgetName()
		xSecond = self.X_AI_PERSONALITY - self.W_AI_PERSONALITY - self.MEDIUM_MARGIN
		screen.addPanel(secondPanelName, localText.getText("TXT_KEY_AI_PERSONALITY", ()) + " (2)", "", True, True,
						xSecond, self.Y_AI_PERSONALITY,
						self.W_AI_PERSONALITY, self.H_AI_PERSONALITY,
						PanelStyles.PANEL_STYLE_BLUE50)

		leader = gc.getLeaderHeadInfo(iLeader)

		lineHeight = 22
		categorySpacing = 10

		xName1 = self.X_AI_PERSONALITY + 15
		xValue1 = xName1 + 260
		xScale1 = xValue1 + 60
		y1 = self.Y_AI_PERSONALITY + 35

		xName2 = xSecond + 15
		xValue2 = xName2 + 260
		xScale2 = xValue2 + 60
		y2 = self.Y_AI_PERSONALITY + 35

		def get_symbol_scale(score):
			if score < 20:
				return "#"
			elif score < 40:
				return "##"
			elif score < 60:
				return "###"
			elif score < 80:
				return "####"
			else:
				return "#####"

		def normalize(value, funcName, inverse=False):
			min_val, max_val = AI_VALUE_RANGES.get(funcName, (0, 0))
			if max_val == min_val:
				return 0
			norm = float(value - min_val) / float(max_val - min_val)
			if inverse:
				norm = 1.0 - norm
			return int(norm * 100)

		left_categories = [AI_HEADER_WAR_STRATEGY, AI_HEADER_AGGREGATES]
		right_categories = [
			AI_HEADER_DIPLOMACY,
			AI_HEADER_ATTITUDE_MODIFIERS,
			AI_HEADER_ECONOMIC_PREFERENCES,
			AI_HEADER_TRADE_THRESHOLDS,
			AI_HEADER_VICTORY_STRATEGY
		]

		inverse_logic = [
			"getDogpileWarRand", "getDemandRebukedWarProb", "getDeclareWarTradeRand",
			"getMaxWarRand", "getLimitedWarRand", "getBaseAttackOddsChange",
			"getRefuseToTalkWarThreshold", "getNoTechTradeThreshold"
		]

		def render_categories(screen, categories, xName, xValue, xScale, yStart):
			y = yStart
			first = True
			for category in categories:
				if not first:
					y += categorySpacing
				else:
					first = False

				screen.setText(self.top.getNextWidgetName(), "", u"<font=3b>%s</font>" % category,
							CvUtil.FONT_LEFT_JUSTIFY, xName, y, 0, FontTypes.SMALL_FONT,
							WidgetTypes.WIDGET_GENERAL, -1, -1)
				y += lineHeight

				if category == AI_HEADER_AGGREGATES:
					for idx, (label, fields) in enumerate(AI_AGGREGATES):
						if idx in AI_AGGREGATE_CATEGORY_BREAKS:
							y += categorySpacing * 2

						score = AI_AGGREGATE_SCORES.get(iLeader, {}).get(label, 0)
						symbols_used = get_symbol_scale(score)

						screen.setText(self.top.getNextWidgetName(), "", u"<font=2>%s</font>" % label,
									CvUtil.FONT_LEFT_JUSTIFY, xName, y, 0, FontTypes.SMALL_FONT,
									WidgetTypes.WIDGET_GENERAL, -1, -1)
						screen.setText(self.top.getNextWidgetName(), "", u"<font=2b>%d</font>" % score,
									CvUtil.FONT_LEFT_JUSTIFY, xValue, y, 0, FontTypes.SMALL_FONT,
									WidgetTypes.WIDGET_GENERAL, -1, -1)
						screen.setText(self.top.getNextWidgetName(), "", u"<font=2>%s</font>" % symbols_used,
									CvUtil.FONT_LEFT_JUSTIFY, xScale, y, 0, FontTypes.SMALL_FONT,
									WidgetTypes.WIDGET_GENERAL, -1, -1)
						y += lineHeight
					continue

				for label, funcName in AI_ATTRIBUTE_CATEGORIES.get(category, []):
					try:
						value = getattr(leader, funcName)()
						inverse = funcName in inverse_logic
						score = normalize(value, funcName, inverse)
						scale_text = get_symbol_scale(score)

						screen.setText(self.top.getNextWidgetName(), "", u"<font=2>%s</font>" % label,
									CvUtil.FONT_LEFT_JUSTIFY, xName, y, 0, FontTypes.SMALL_FONT,
									WidgetTypes.WIDGET_GENERAL, -1, -1)
						screen.setText(self.top.getNextWidgetName(), "", u"<font=2b>%d</font>" % value,
									CvUtil.FONT_LEFT_JUSTIFY, xValue, y, 0, FontTypes.SMALL_FONT,
									WidgetTypes.WIDGET_GENERAL, -1, -1)
						screen.setText(self.top.getNextWidgetName(), "", u"<font=2>%s</font>" % scale_text,
									CvUtil.FONT_LEFT_JUSTIFY, xScale, y, 0, FontTypes.SMALL_FONT,
									WidgetTypes.WIDGET_GENERAL, -1, -1)
						y += lineHeight
					except:
						pass

		render_categories(screen, left_categories, xName1, xValue1, xScale1, y1)
		render_categories(screen, right_categories, xName2, xValue2, xScale2, y2)
		
		#<!-- custom: link not working to concept page of ai personality, disabling it for now, if not always or not etc anyways, -->

	def handleInput (self, inputClass):
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CHARACTER):
			if (inputClass.getData() == int(InputTypes.KB_0)):
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.LEADERANIM_GREETING)
			elif (inputClass.getData() == int(InputTypes.KB_6)):
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.LEADERANIM_DISAGREE)
			elif (inputClass.getData() == int(InputTypes.KB_7)):
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.LEADERANIM_AGREE)
			elif (inputClass.getData() == int(InputTypes.KB_1)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_FRIENDLY)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_2)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_PLEASED)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_3)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_CAUTIOUS)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_4)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_ANNOYED)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_5)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_FURIOUS)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			else:
				self.top.getScreen().leaderheadKeyInput(self.leaderWidget, inputClass.getData())
		return 0

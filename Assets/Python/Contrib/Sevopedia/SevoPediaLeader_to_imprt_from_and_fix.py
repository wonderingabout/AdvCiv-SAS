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
# <!-- custom: debug -->
import sys

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


"""
old invert logic to remove:
AI_INVERTED_TRAITS = set([
    # Attitude threshold traits (higher threshold = more reluctance or caution)
    "getRefuseToTalkWarThreshold",
    "getNoTechTradeThreshold",
    "getOpenBordersRefuseAttitudeThreshold",
    "getStopTradingRefuseAttitudeThreshold",
    "getAdoptCivicRefuseAttitudeThreshold",
    "getConvertReligionRefuseAttitudeThreshold",
    "getDeclareWarRefuseAttitudeThreshold",
    "getCityRefuseAttitudeThreshold",
    "getMapRefuseAttitudeThreshold",
    "getTechRefuseAttitudeThreshold",
    "getHealthBonusRefuseAttitudeThreshold",
    "getHappinessBonusRefuseAttitudeThreshold",
    "getStrategicBonusRefuseAttitudeThreshold",
    "getDeclareWarThemRefuseAttitudeThreshold",
    "getStopTradingThemRefuseAttitudeThreshold",
    "getVassalRefuseAttitudeThreshold",
    # War decision traits where higher = more cautious (less aggressive)
    "getMaxWarMinAdjacentLandPercent",
    "getLimitedWarRand",
    "getMaxWarRand",
    "getDogpileWarRand",
])


getBasePeaceWeight": -1,          # Lower = more aggressive
"""


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



""" # === CATEGORY HEADERS ===
AI_HEADER_AGGREGATES = "Normalized Aggregates (UWAI-based) (0 - 100 (%))"
AI_HEADER_WAR_STRATEGY = "War Strategy (UWAI)"
AI_HEADER_DIPLOMACY = "Diplomacy (UWAI)"
AI_HEADER_ECONOMIC_PREFERENCES = "Economy / Build (UWAI)"


"""



# --- AI Personality Configuration Constants (Categories & Traits) ---

AI_HEADER_AGGREGATES = "Aggregates (% normalized) (UWAI)"
AI_HEADER_WAR_STRATEGY = "War Strategy (UWAI)"
AI_HEADER_DIPLOMACY = "Diplomacy (UWAI)"
AI_HEADER_ATTITUDE = "Attitude (UWAI)"
AI_HEADER_ECONOMIC_BEHAVIOR = "Economic Behviour (UWAI)"
AI_HEADER_TRADE = "Trade (UWAI)"

# Indices at which to insert a visual break in the aggregates list (for subcategory grouping)
AI_AGGREGATE_CATEGORY_BREAKS = [6, 13]


"""



note: not uwai safe



# Let's create a Python dictionary that maps each UWAI-safe AI attribute to a detailed description.
# The descriptions include the attribute's in-game meaning and whether higher or lower values
# indicate a stronger preference for certain behaviors (e.g., more warlike, more diplomatic, etc.)

UWAI_SAFE_ATTRIBUTES_INFO = {
    "iAtPeaceAttitudeChangeLimit": "Max attitude bonus AI gets when at peace. Higher = more diplomatic when not at war.",
    "iAtPeaceAttitudeDivisor": "Divisor for calculating attitude bonus when at peace. Lower = stronger bonus.",
    "iAtWarAttitudeChangeLimit": "Max attitude penalty AI has when at war. Higher = more hostile during war.",
    "iAtWarAttitudeDivisor": "Divisor for calculating attitude penalty when at war. Lower = stronger penalty.",
    "iAttackOddsChangeRand": "Random factor applied to attack odds. Higher = more unpredictable in combat choices.",
    "iBaseAttitude": "Base attitude toward all players. Higher = more friendly default stance.",
    "iBasePeaceWeight": "Tendency toward peaceful behavior. Higher = more peace-loving.",
    "iBetterRankDifferenceAttitudeChange": "Attitude bonus when AI is ranked better than others. Higher = more generous to weaker civs.",
    "iBonusTradeAttitudeChangeLimit": "Max bonus for trading resources. Higher = more favorable trading attitude.",
    "iBonusTradeAttitudeDivisor": "Divisor for calculating bonus trade attitude. Lower = stronger positive change from trades.",
    "iBuildUnitProb": "Chance AI prioritizes unit production. Higher = more militaristic.",
    "iCloseBordersAttitudeChange": "Penalty for close borders. Higher = more likely to hate neighbors.",
    "iConquestVictoryWeight": "AI preference for conquest victory. Higher = more aggressive conquest behavior.",
    "iCultureVictoryWeight": "AI preference for cultural victory. Higher = more emphasis on culture.",
    "iDeclareWarTradeRand": "Chance AI agrees to declare war when asked. Higher = more likely to accept war deals.",
    "iDefensivePactAttitudeChangeLimit": "Attitude bonus for defensive pacts. Higher = more positive from DP.",
    "iDefensivePactAttitudeDivisor": "Divisor for DP attitude bonus. Lower = more impact from pact.",
    "iDemandRebukedSneakProb": "Chance of sneak attack when demands are refused. Higher = more backstabby.",
    "iDemandRebukedWarProb": "Chance of open war after demands are refused. Higher = more retaliatory.",
    "iDifferentReligionAttitudeChange": "Attitude penalty for different religions. Higher = more intolerant.",
    "iDifferentReligionAttitudeChangeLimit": "Max religion penalty. Higher = more rigid about religion.",
    "iDifferentReligionAttitudeDivisor": "Divisor for religion penalty. Lower = steeper penalty.",
    "iDiplomacyVictoryWeight": "AI preference for diplomatic victory. Higher = more UN-focused.",
    "iDogpileWarRand": "Chance AI joins dogpile wars. Higher = more opportunistic.",
    "iDominationVictoryWeight": "AI preference for domination victory. Higher = more territorial.",
    "iEspionageWeight": "Priority given to espionage. Higher = more spy-heavy behavior.",
    "iFavoriteCivicAttitudeChange": "Bonus attitude for matching favorite civic. Higher = more ideological.",
    "iFavoriteCivicAttitudeChangeLimit": "Max civic bonus. Higher = stronger positive toward civics.",
    "iFavoriteCivicAttitudeDivisor": "Divisor for civic bonus. Lower = stronger effect.",
    "iLimitedWarPowerRatio": "Power ratio AI needs to consider limited war. Higher = more cautious.",
    "iLimitedWarRand": "Chance of starting limited war. Higher = more tactically aggressive.",
    "iLostWarAttitudeChange": "Attitude penalty when losing wars. Higher = more resentful.",
    "iLoveOfPeace": "Generic peace preference. Higher = more peaceful behavior.",
    "iMakePeaceRand": "Likelihood of AI making peace. Higher = more likely to accept peace.",
    "iMaxGoldPerTurnTradePercent": "Max % of GPT AI willing to trade. Higher = more generous.",
    "iMaxGoldTradePercent": "Max % of total gold AI willing to trade. Higher = more generous.",
    "iMaxWarDistantPowerRatio": "Required strength ratio for distant wars. Higher = more cautious long-range.",
    "iMaxWarMinAdjacentLandPercent": "Min adjacent land % to start major war. Higher = favors neighbors.",
    "iMaxWarNearbyPowerRatio": "Required strength ratio for nearby wars. Higher = more cautious locally.",
    "iMaxWarRand": "Chance of major war. Higher = more likely to wage big wars.",
    "iNoTechTradeThreshold": "Threshold to block tech trade. Higher = more tech stingy.",
    "iOpenBordersAttitudeChangeLimit": "Attitude bonus for Open Borders. Higher = benefits more from OB.",
    "iOpenBordersAttitudeDivisor": "Divisor for OB bonus. Lower = bigger effect.",
    "iPeaceWeightRand": "Random factor applied to peace weight. Higher = less predictable peaciness.",
    "iRazeCityProb": "Chance AI razes captured cities. Higher = more ruthless.",
    "iRefuseToTalkWarThreshold": "Threshold for refusing diplomacy. Higher = more stubborn when angry.",
    "iSameReligionAttitudeChange": "Bonus for shared religion. Higher = more religiously aligned.",
    "iSameReligionAttitudeChangeLimit": "Max religion bonus. Higher = stronger religious favoritism.",
    "iSameReligionAttitudeDivisor": "Divisor for bonus. Lower = stronger effect.",
    "iShareWarAttitudeChange": "Bonus for sharing wars. Higher = more cooperative in war.",
    "iShareWarAttitudeChangeLimit": "Max shared war bonus. Higher = more bonded by conflict.",
    "iShareWarAttitudeDivisor": "Divisor for shared war bonus. Lower = stronger bonus.",
    "iSpaceVictoryWeight": "AI preference for space race. Higher = builds toward spaceship.",
    "iTechTradeKnownPercent": "% of players that must know a tech before AI trades it. Higher = more cautious.",
    "iWarmongerRespect": "How much AI respects other warmongers. Higher = respects aggression.",
    "iWonderConstructRand": "Chance to build wonders. Higher = more wonder-prone.",
    "iWorseRankDifferenceAttitudeChange": "Attitude penalty for weaker rank. Higher = more elitist.",
}
"""


# === RAW AI PERSONALITY CATEGORIES ===
# UWAI-compatible only, grouped by behavior type.

AI_HEADER_WAR_STRATEGY = "War Strategy"
AI_HEADER_DIPLOMACY = "Diplomacy"
AI_HEADER_ECONOMIC_BEHAVIOR = "Economic Preferences"
AI_HEADER_ATTITUDE = "Attitude Modifiers"
AI_HEADER_TRADE = "Trade Behavior"

AI_ATTRIBUTE_CATEGORIES = {
	AI_HEADER_WAR_STRATEGY: [
		# Determines how likely AI is to start different types of wars.
		("Max War Rand", "getMaxWarRand"),  # Higher = more likely to start full-scale war (UWAI-safe)
		("Limited War Rand", "getLimitedWarRand"),  # Tactical/local wars (Higher = more likely)
		("Dogpile War Rand", "getDogpileWarRand"),  # Join wars against weakened civs (Higher = more opportunistic)
		("Make Peace Rand", "getMakePeaceRand"),  # Higher = more likely to offer/accept peace
		("Build Unit Prob", "getBuildUnitProb"),  # Military focus: Higher = builds more units
	],

	AI_HEADER_DIPLOMACY: [
		("Base Peace Weight", "getBasePeaceWeight"),  # High = peaceful, dislikes war civs
		("Warmonger Respect", "getWarmongerRespect"),  # High = respects warmongers, low = fears them
		("Declare War Trade Rand", "getDeclareWarTradeRand"),  # Higher = more likely to accept bribes to declare war
		("Refuse To Talk Threshold", "getRefuseToTalkWarThreshold"),  # High = refuses diplomacy longer
		("Same Religion Attitude Change Limit", "getSameReligionAttitudeChangeLimit"),  # Max bonus for same religion
		("Different Religion Attitude Change Limit", "getDifferentReligionAttitudeChangeLimit"),  # Max penalty for different religions
		("Favorite Civic Attitude Change Limit", "getFavoriteCivicAttitudeChangeLimit"),  # Max bonus for using AI's favorite civic
		("Close Borders Attitude Change", "getCloseBordersAttitudeChange"),  # High = dislikes close borders more
	],

	AI_HEADER_ECONOMIC_BEHAVIOR: [
		("Espionage Weight", "getEspionageWeight"),  # High = uses more spies
		("Wonder Construct Rand", "getWonderConstructRand"),  # High = likely to build wonders
		("Base Attack Odds Change", "getBaseAttackOddsChange"),  # Adjusts combat calculations (AI aggressiveness)
		("Attack Odds Change Rand", "getAttackOddsChangeRand"),  # Adds randomness to attack calculations
		("Max Gold Trade %", "getMaxGoldTradePercent"),  # Max one-time gold AI is willing to trade
		("Max GPT Trade %", "getMaxGoldPerTurnTradePercent"),  # Max GPT AI is willing to trade
	],

	AI_HEADER_ATTITUDE: [
		("Worse Rank Attitude Change", "getWorseRankDifferenceAttitudeChange"),  # Penalty vs weaker civs
		("Better Rank Attitude Change", "getBetterRankDifferenceAttitudeChange"),  # Bonus vs weaker civs
	],

	AI_HEADER_TRADE: [
		("Tech Trade Known %", "getTechTradeKnownPercent"),  # How many others must know tech before trade
		("No Tech Trade Threshold", "getNoTechTradeThreshold"),  # High = more likely to hoard tech
		("Tech Refuse Attitude Threshold", "getTechRefuseAttitudeThreshold"),  # Refuses tech deals under this attitude
		("Map Refuse Attitude Threshold", "getMapRefuseAttitudeThreshold"),  # Refuses map trade under this attitude
		("Declare War Refuse Attitude Threshold", "getDeclareWarRefuseAttitudeThreshold"),  # Refuses war requests under this attitude
		("Stop Trading Refuse Attitude Threshold", "getStopTradingRefuseAttitudeThreshold"),  # Refuses embargoes under this attitude
		("Stop Trading Them Refuse Threshold", "getStopTradingThemRefuseAttitudeThreshold"),  # Refuses specific embargoes
		("Adopt Civic Refuse Attitude Threshold", "getAdoptCivicRefuseAttitudeThreshold"),  # Refuses civic demands
		("Convert Religion Refuse Attitude Threshold", "getConvertReligionRefuseAttitudeThreshold"),  # Refuses religion demands
		("Open Borders Refuse Attitude Threshold", "getOpenBordersRefuseAttitudeThreshold"),  # Refuses OB deals under this attitude
		("Vassal Refuse Attitude Threshold", "getVassalRefuseAttitudeThreshold"),  # Refuses vassal offers under this attitude
		("Health Bonus Refuse Attitude Threshold", "getHealthBonusRefuseAttitudeThreshold"),  # Refuses health resources
		("Happiness Bonus Refuse Attitude Threshold", "getHappinessBonusRefuseAttitudeThreshold"),  # Refuses happiness resources
		("Strategic Bonus Refuse Attitude Threshold", "getStrategicBonusRefuseAttitudeThreshold"),  # Refuses strategic resources
		("Declare War Them Refuse Attitude Threshold", "getDeclareWarThemRefuseAttitudeThreshold"),  # Refuses war on target
	],
}


"""

not uwai safe
v2 of raw ai attributes
# --- AI ATTRIBUTE CATEGORIES (UWAI-compatible, fully commented) ---
AI_ATTRIBUTE_CATEGORIES = {
	"War Strategy": [
		# Determines how likely the AI is to consider a full war
		("getMaxWarRand", "More likely to start total war (higher = more warlike)"),
		# Tendency to wage wars when the enemy is weaker and nearby
		("getLimitedWarRand", "More likely to launch limited/tactical wars (higher = more tactical warfare)"),
		# Chance of joining an ongoing war against a mutual enemy
		("getDogpileWarRand", "More likely to join wars opportunistically (higher = more opportunistic)"),
		# Tendency to offer/seek peace during war
		("getMakePeaceRand", "Less likely to make peace (higher = more stubborn in war)"),
		# War decision depends on nearby enemy strength
		("getMaxWarNearbyPowerRatio", "Wants to be stronger nearby to start war (higher = more cautious)"),
		# Power ratio for limited war calculation
		("getLimitedWarPowerRatio", "More cautious with limited war (higher = more cautious)"),
		# AI considers initiating war if adjacent territory is below threshold
		("getMaxWarMinAdjacentLandPercent", "More willing to expand via war (lower = more aggressive expansion)"),
	],
	"Diplomacy": [
		# Base diplomacy attitude modifier (positive = friendlier)
		("getBaseAttitude", "Friendliness baseline (higher = more friendly)"),
		# How much AI prefers peace over war
		("getBasePeaceWeight", "Prefers peace (higher = more peaceful)"),
		# AI's respect for other warmongers
		("getWarmongerRespect", "Respects warmongers (higher = allies with warmongers)"),
		# Chance of sneak demand instead of a regular request
		("getDemandRebukedSneakProb", "More likely to backstab (higher = sneak attacks more)"),
		# War demand after rebuked request
		("getDemandRebukedWarProb", "More likely to declare war when requests are denied"),
		# Refusal threshold for diplomatic contact
		("getRefuseToTalkWarThreshold", "Stays hostile longer (higher = more stubborn)"),
		# Refuses tech trades at higher thresholds
		("getNoTechTradeThreshold", "Hoarder of technology (higher = more stingy)"),
		# Percent of other civs needing to know a tech before AI trades it
		("getTechTradeKnownPercent", "More likely to trade tech early (lower = more open)"),
		# Affects war bribing offers from others
		("getDeclareWarTradeRand", "Easier to bribe into war (higher = more susceptible)"),
	],
	"Economic Preferences": [
		# AI's desire to build units (not buildings)
		("getBuildUnitProb", "Builds more units (higher = more militaristic economy)"),
		# Base modifier for combat decisions
		("getBaseAttackOddsChange", "Willingness to attack (higher = attacks more often)"),
		# Adds randomness to attack logic
		("getAttackOddsChangeRand", "More chaotic behavior in attacks (higher = more unpredictable)"),
		# Randomness for wonder building
		("getWonderConstructRand", "More likely to pursue wonders (higher = wonder builder)"),
		# Willingness to trade lump sum gold
		("getMaxGoldTradePercent", "Shares gold (higher = more generous)"),
		# Willingness to trade gold per turn
		("getMaxGoldPerTurnTradePercent", "Shares GPT (higher = more generous)"),
		# Espionage allocation preference
		("getEspionageWeight", "More focused on spying (higher = espionage-heavy)"),
	],
	"Victory Strategy": [
		("getSpaceVictoryWeight", "Pursues space victory (higher = prefers science win)"),
		("getConquestVictoryWeight", "Pursues conquest victory (higher = domination preference)"),
		("getDominationVictoryWeight", "Pursues domination victory (higher = land/territory focus)"),
	],
	"Attitude Modifiers": [
		("getWorseRankDifferenceAttitudeChange", "Dislikes weaker civs (higher = more contemptuous)"),
		("getBetterRankDifferenceAttitudeChange", "Likes stronger civs (higher = more respectful)"),
		("getCloseBordersAttitudeChange", "Annoyed by close borders (higher = more hostile neighbors)"),
		("getSameReligionAttitudeChangeLimit", "Better attitude cap for shared religion (higher = more cooperative)"),
		("getDifferentReligionAttitudeChangeLimit", "Negative cap for differing religion (higher = more intolerant)"),
		("getShareWarAttitudeChangeLimit", "Likes shared wars (higher = appreciates mutual enemies)"),
		("getFavoriteCivicAttitudeChangeLimit", "Likes same civic (higher = civic preference matters more)"),
	],
	"Trade Thresholds": [
		("getTechRefuseAttitudeThreshold", "Min attitude required to trade techs"),
		("getStrategicBonusRefuseAttitudeThreshold", "Min attitude for strategic resources"),
		("getHealthBonusRefuseAttitudeThreshold", "Min attitude for health resources"),
		("getHappinessBonusRefuseAttitudeThreshold", "Min attitude for happy resources"),
		("getMapRefuseAttitudeThreshold", "Min attitude to trade maps"),
		("getDeclareWarRefuseAttitudeThreshold", "Min attitude to join war declarations"),
		("getDeclareWarThemRefuseAttitudeThreshold", "Min attitude to stop trading with others"),
		("getStopTradingRefuseAttitudeThreshold", "Refusal threshold for stopping trade"),
		("getStopTradingThemRefuseAttitudeThreshold", "Refusal threshold for embargoing third party"),
		("getAdoptCivicRefuseAttitudeThreshold", "Min attitude to accept civic switch"),
		("getConvertReligionRefuseAttitudeThreshold", "Min attitude to change religion"),
		("getOpenBordersRefuseAttitudeThreshold", "Min attitude to open borders"),
		("getVassalRefuseAttitudeThreshold", "Min attitude to become a vassal"),
	],
}
"""



"""
v3 of uwai safe ai attributes
# Categorized UWAI-safe AI attributes with descriptions and inversion notes
raw_ai_categories = OrderedDict({
    "War Strategy": [
        # Description: Likelihood of different war types or thresholds.
        # Higher = more likely to declare that type of war or wait longer to make peace.
        ("getMaxWarRand", "Chance of initiating major wars. Higher = more likely."),
        ("getLimitedWarRand", "Chance of starting tactical wars. Higher = more likely."),
        ("getDogpileWarRand", "Chance of joining existing wars. Higher = more likely."),
        ("getMakePeaceRand", "Delay before making peace. Higher = waits longer."),
        ("getMaxWarNearbyPowerRatio", "Threshold ratio for nearby power before war."),
        ("getMaxWarDistantPowerRatio", "Threshold ratio for distant power before war."),
        ("getMaxWarMinAdjacentLandPercent", "Land adjacency % threshold before major war."),
        ("getLimitedWarPowerRatio", "Threshold for starting limited war."),
    ],
    "Diplomacy & Personality": [
        # Description: Determines diplomacy dynamics and how AI reacts.
        ("getBaseAttitude", "Base attitude toward others. Higher = more friendly."),
        ("getBasePeaceWeight", "Tendency toward peace. Higher = less aggressive."),
        ("getWarmongerRespect", "Respects aggressive AIs. Higher = likes warmongers."),
        ("getDeclareWarTradeRand", "Willingness to declare war when bribed. Higher = more likely."),
        ("getRefuseToTalkWarThreshold", "Minimum anger before refusing to talk. Higher = more stubborn."),
        ("getDemandRebukedSneakProb", "Chance to backstab after refused demand."),
        ("getDemandRebukedWarProb", "Chance to declare war after demand refusal."),
        ("getSameReligionAttitudeChangeLimit", "Max attitude bonus for same religion."),
        ("getDifferentReligionAttitudeChangeLimit", "Max penalty for different religion."),
        ("getShareWarAttitudeChangeLimit", "Max bonus for shared wars."),
        ("getFavoriteCivicAttitudeChangeLimit", "Max bonus from shared civics."),
    ],
    "Trade & Tech Preferences": [
        # Description: AI tech and resource trade logic.
        ("getNoTechTradeThreshold", "Threshold to refuse tech trade. Higher = more hoarding."),
        ("getTechTradeKnownPercent", "How many players must know tech before trade."),
        ("getTechRefuseAttitudeThreshold", "Min attitude required to trade tech."),
        ("getMaxGoldTradePercent", "Gold AI is willing to trade as lump sum."),
        ("getMaxGoldPerTurnTradePercent", "GPT AI is willing to trade."),
        ("getStrategicBonusRefuseAttitudeThreshold", "Attitude needed to trade strategic resource."),
        ("getHealthBonusRefuseAttitudeThreshold", "Attitude needed for health resources."),
        ("getHappinessBonusRefuseAttitudeThreshold", "Attitude needed for happiness resources."),
        ("getMapRefuseAttitudeThreshold", "Refusal level for map trades."),
    ],
    "Civics & Religion": [
        # Description: Resistance or openness to civic/religion change.
        ("getAdoptCivicRefuseAttitudeThreshold", "Attitude needed for civic switch request."),
        ("getConvertReligionRefuseAttitudeThreshold", "Attitude needed for religion switch."),
        ("getOpenBordersRefuseAttitudeThreshold", "Attitude needed for open borders."),
        ("getStopTradingRefuseAttitudeThreshold", "Attitude needed to stop trading."),
        ("getStopTradingThemRefuseAttitudeThreshold", "Attitude needed to stop trading with a third party."),
        ("getDeclareWarRefuseAttitudeThreshold", "Attitude needed to declare war."),
        ("getDeclareWarThemRefuseAttitudeThreshold", "Attitude needed to declare war on third party."),
        ("getVassalRefuseAttitudeThreshold", "Attitude needed to become a vassal."),
    ],
    "Military & Build Preferences": [
        # Description: What the AI chooses to build or focus on.
        ("getBuildUnitProb", "Chance to build units over buildings."),
        ("getBaseAttackOddsChange", "Bias for attack odds. Higher = more aggressive."),
        ("getAttackOddsChangeRand", "Variance in attack odds tolerance."),
        ("getEspionageWeight", "Preference for espionage."),
        ("getWonderConstructRand", "Random factor to wonder building."),
        ("getSpaceVictoryWeight", "Preference for space victory."),
        ("getConquestVictoryWeight", "Preference for conquest victory."),
        ("getDominationVictoryWeight", "Preference for domination victory."),
    ],
    "Attitude Modifiers": [
        # Description: How ranks and borders affect attitude.
        ("getWorseRankDifferenceAttitudeChange", "Penalty for being ranked lower."),
        ("getBetterRankDifferenceAttitudeChange", "Bonus for being ranked higher."),
        ("getCloseBordersAttitudeChange", "Penalty for close borders."),
    ],
})
"""




# --- Aggregate Weights (normalized percentile, with inversion logic) ---
"""AI_AGGREGATE_WEIGHTS = {
	"Warmonger": {
		"getMaxWarRand": 1,                # More wars
		"getDogpileWarRand": 1,            # Joins war opportunistically
		"getLimitedWarRand": 1,            # Tactical wars
		"getBuildUnitProb": 1,             # Builds more units
		"getMakePeaceRand": 1,             # Delays peace
		"getWarmongerRespect": 1,          # Respects other warmongers
		"getDeclareWarTradeRand": 1,       # Higher = more likely to accept war deals
		"getBasePeaceWeight": -1,          # Lower = more aggressive
		# UWAI-safe subset only!
		# Deprecated under UWAI
		#"getMaxWarNearbyPowerRatio": -1,
		#"getLimitedWarPowerRatio": -1,
		#"getMaxWarMinAdjacentLandPercent": -1,
	}
} """



"""
ai aggregates v2 but definitions (not compatible with our mod at least not yet)

# Define 25 aggregates using the updated attribute groups and normalized logic
# Each entry is a tuple: (Aggregate Name, [(attribute, invert, weight, explanation)])
AGGREGATES_DETAILED = OrderedDict([
	# === WAR STRATEGY ===
	("Warmonger", [
		# High MaxWarRand = likely to start major wars → Positive
		("getMaxWarRand", False, 1.0, "Likelihood to start full-scale war"),
		# High BuildUnitProb = builds military → Positive
		("getBuildUnitProb", False, 1.0, "Focus on military unit production"),
		# High Dogpile = opportunistic aggression → Positive
		("getDogpileWarRand", False, 0.9, "Joins wars opportunistically"),
		# Low BasePeaceWeight = less peace-oriented → Invert
		("getBasePeaceWeight", True, 1.0, "Preference for peaceful resolutions"),
		# High MakePeaceRand = refuses peace → Positive
		("getMakePeaceRand", False, 1.0, "Reluctance to make peace"),
	]),

	("Opportunistic", [
		("getDogpileWarRand", False, 1.0, "Tendency to join ongoing wars"),
		("getDeclareWarTradeRand", False, 1.0, "Willingness to trade for war"),
		("getWarmongerRespect", False, 0.8, "Respects other warmongers"),
	]),

	("Cautious", [
		("getMaxWarNearbyPowerRatio", True, 1.0, "Avoids wars unless stronger"),
		("getMakePeaceRand", True, 1.0, "Willingness to make peace"),
		("getRefuseToTalkWarThreshold", True, 1.0, "Talks to enemies sooner"),
	]),

	("Reckless", [
		("getBaseAttackOddsChange", False, 1.0, "Willingness to attack"),
		("getAttackOddsChangeRand", False, 1.0, "Unpredictability in attack decisions"),
		("getDeclareWarRefuseAttitudeThreshold", True, 1.0, "Accepts war proposals more often"),
	]),

	# === DIPLOMACY ===
	("Diplomatic", [
		("getBasePeaceWeight", False, 1.0, "Prefers peace"),
		("getTechTradeKnownPercent", False, 0.8, "Shares tech more easily"),
		("getOpenBordersRefuseAttitudeThreshold", True, 1.0, "Grants open borders more freely"),
	]),

	("Backstabber", [
		("getDemandRebukedSneakProb", False, 1.0, "May attack after refusal"),
		("getDemandRebukedWarProb", False, 1.0, "Will declare war after a rebuke"),
		("getRefuseToTalkWarThreshold", False, 1.0, "Stays angry and won’t talk"),
	]),

	("Friendly", [
		("getSameReligionAttitudeChangeLimit", False, 1.0, "Friendlier to same religion"),
		("getShareWarAttitudeChangeLimit", False, 1.0, "Boosts attitude from shared wars"),
		("getFavoriteCivicAttitudeChangeLimit", False, 1.0, "Likes civs with same civics"),
	]),

	("Grudgy", [
		("getWorseRankDifferenceAttitudeChange", False, 1.0, "Dislikes weaker civs"),
		("getCloseBordersAttitudeChange", False, 1.0, "Gets annoyed by close borders"),
		("getDifferentReligionAttitudeChangeLimit", False, 1.0, "Hates different religions"),
	]),

	# === ECONOMIC ===
	("Builder", [
		("getBuildUnitProb", True, 1.0, "Focus on buildings instead of units"),
		("getWonderConstructRand", False, 1.0, "Priority on building wonders"),
		("getBasePeaceWeight", False, 1.0, "Peaceful builder tendency"),
	]),

	("Trader", [
		("getTechTradeKnownPercent", False, 1.0, "Willing to trade tech"),
		("getMaxGoldTradePercent", False, 1.0, "Generous in lump-sum gold trades"),
		("getMaxGoldPerTurnTradePercent", False, 1.0, "Generous in GPT trades"),
	]),

	("Tech Hoarder", [
		("getNoTechTradeThreshold", False, 1.0, "Unwilling to trade tech"),
		("getTechRefuseAttitudeThreshold", False, 1.0, "Refuses tech trades easily"),
		("getTechTradeKnownPercent", True, 1.0, "Wants few civs to know tech before trading"),
	]),

	("Isolationist", [
		("getOpenBordersRefuseAttitudeThreshold", False, 1.0, "Refuses open borders"),
		("getMapRefuseAttitudeThreshold", False, 1.0, "Refuses map trading"),
		("getStopTradingRefuseAttitudeThreshold", False, 1.0, "Resists diplomacy-based requests"),
	]),

	("Zealot", [
		("getConvertReligionRefuseAttitudeThreshold", False, 1.0, "Resists changing religion"),
		("getSameReligionAttitudeChangeLimit", False, 1.0, "Strong preference for own religion"),
		("getDifferentReligionAttitudeChangeLimit", False, 1.0, "Intolerance for other religions"),
	]),

	("Stubborn", [
		("getAdoptCivicRefuseAttitudeThreshold", False, 1.0, "Won’t switch civics"),
		("getStopTradingRefuseAttitudeThreshold", False, 1.0, "Won’t stop trading"),
		("getConvertReligionRefuseAttitudeThreshold", False, 1.0, "Won’t convert religion"),
	]),

	("Flexible", [
		("getAdoptCivicRefuseAttitudeThreshold", True, 1.0, "Adapts civic demands"),
		("getConvertReligionRefuseAttitudeThreshold", True, 1.0, "Adapts religious demands"),
		("getFavoriteCivicAttitudeChangeLimit", True, 1.0, "Open to different civics"),
	]),

	("Stingy", [
		("getStrategicBonusRefuseAttitudeThreshold", False, 1.0, "Keeps strategic resources"),
		("getHealthBonusRefuseAttitudeThreshold", False, 1.0, "Keeps health resources"),
		("getHappinessBonusRefuseAttitudeThreshold", False, 1.0, "Keeps happiness resources"),
	]),

	("Collaborative", [
		("getSameReligionAttitudeChangeLimit", False, 1.0, "Rewards common religion"),
		("getFavoriteCivicAttitudeChangeLimit", False, 1.0, "Rewards common civics"),
		("getOpenBordersRefuseAttitudeThreshold", True, 1.0, "Willing to collaborate"),
	]),

	("Sneaky", [
		("getEspionageWeight", False, 1.0, "Emphasis on espionage"),
		("getDogpileWarRand", False, 0.8, "Backdoor war starter"),
		("getDeclareWarTradeRand", False, 0.8, "Tricky dealmaker"),
	]),

	# === VICTORY TYPES ===
	("Conqueror", [
		("getConquestVictoryWeight", False, 1.0, "Prefers conquest victory"),
		("getDominationVictoryWeight", False, 1.0, "Prefers domination"),
		("getBuildUnitProb", False, 1.0, "Builds many units"),
	]),

	("Scientist", [
		("getSpaceVictoryWeight", False, 1.0, "Wants space victory"),
		("getTechTradeKnownPercent", False, 1.0, "Research-oriented"),
		("getNoTechTradeThreshold", False, 1.0, "Keeps tech to self"),
	]),

	("Civic Enforcer", [
		("getFavoriteCivicAttitudeChangeLimit", False, 1.0, "Demands shared civics"),
		("getAdoptCivicRefuseAttitudeThreshold", False, 1.0, "Forces civic choices"),
	]),

	("Map Hoarder", [
		("getMapRefuseAttitudeThreshold", False, 1.0, "Won’t trade maps"),
		("getOpenBordersRefuseAttitudeThreshold", False, 1.0, "Isolationist"),
	]),

	("Loyal Ally", [
		("getShareWarAttitudeChangeLimit", False, 1.0, "Rewards shared conflict"),
		("getWarmongerRespect", False, 0.8, "Respects power"),
		("getRefuseToTalkWarThreshold", True, 1.0, "Recovers quickly"),
	]),

	("Power Watcher", [
		("getMaxWarNearbyPowerRatio", False, 1.0, "Observes nearby strength before war"),
		("getLimitedWarPowerRatio", False, 1.0, "Thinks tactically"),
	]),

	("Micro-manager", [
		("getAttackOddsChangeRand", False, 1.0, "Tweaks strategy often"),
		("getLimitedWarRand", False, 1.0, "Precise limited warfare"),
		("getMakePeaceRand", False, 1.0, "Fine-tunes war lengths"),
	]),
])


"""


"""
		# UWAI-safe subset only!
		# Deprecated under UWAI
		#"getMaxWarNearbyPowerRatio": -1,
		#"getLimitedWarPowerRatio": -1,
		#"getMaxWarMinAdjacentLandPercent": -1,
ai aggregates v2-v3(?)
Always show details

Copy
# This code defines 25 detailed AI aggregates using UWAI-safe attributes.
# Each entry is a tuple: (AggregateLabel, [(AttributeFunction, InvertFlag)])
# These are ready for direct use in the REVISED_AI_AGGREGATES structure in SevoPediaLeader.py

may be uwai safe

REVISED_AI_AGGREGATES = [

    # === MILITARISM / WAR BEHAVIOR ===
    ("Warmonger", [
        # More willing to go to war; higher values increase aggression
        ("getMaxWarRand", False),
        ("getDogpileWarRand", False),
        ("getLimitedWarRand", False),
        # Builds more units = more military
        ("getBuildUnitProb", False),
        # Less willing to make peace = more aggressive
        ("getMakePeaceRand", False),
        # Higher = more respect for fellow warmongers
        ("getWarmongerRespect", False),
        # Lower = more aggressive diplomacy (higher = more peace-inclined)
        ("getBasePeaceWeight", True),
    ]),

    ("Aggressive", [
        # Values used in warmonger, but emphasizes unit combat more
        ("getBaseAttackOddsChange", False),
        ("getAttackOddsChangeRand", False),
        ("getBuildUnitProb", False),
        ("getMaxWarRand", False),
    ]),

    ("Opportunist", [
        # Takes chances, even risky wars
        ("getDeclareWarTradeRand", False),
        ("getDogpileWarRand", False),
        ("getAttackOddsChangeRand", False),
        ("getRefuseToTalkWarThreshold", True),
    ]),

    ("Reckless", [
        # Fights wars even with low odds
        ("getBaseAttackOddsChange", False),
        ("getLimitedWarRand", True),
        ("getMaxWarRand", True),
        ("getRefuseToTalkWarThreshold", True),
        ("getDeclareWarRefuseAttitudeThreshold", True),
    ]),

    ("Cautious", [
        # Avoids war unless power ratios are safe
        ("getLimitedWarPowerRatio", False),
        ("getMaxWarNearbyPowerRatio", True),
        ("getMakePeaceRand", False),
        ("getRefuseToTalkWarThreshold", False),
    ]),

    ("Dogpiler", [
        # Jumps into wars opportunistically
        ("getDogpileWarRand", False),
        ("getDeclareWarTradeRand", False),
        ("getWarmongerRespect", False),
    ]),

    ("Vassalizer", [
        # Tends to make vassals
        ("getVassalRefuseAttitudeThreshold", False),
        ("getRefuseToTalkWarThreshold", True),
        ("getMaxWarNearbyPowerRatio", False),
    ]),

    # === ECONOMIC / DEVELOPMENT ===
    ("Builder", [
        ("getBuildUnitProb", True),
        ("getWonderConstructRand", True),
        ("getBasePeaceWeight", False),
    ]),

    ("Wonder Chaser", [
        ("getWonderConstructRand", True),
        ("getBuildUnitProb", True),
    ]),

    ("Trader", [
        # More willing to trade
        ("getTechTradeKnownPercent", False),
        ("getDeclareWarTradeRand", False),
        ("getMapRefuseAttitudeThreshold", True),
        ("getMaxGoldTradePercent", False),
        ("getMaxGoldPerTurnTradePercent", False),
    ]),

    ("Tech Hoarder", [
        # Refuses tech trades or doesn't want to share
        ("getNoTechTradeThreshold", False),
        ("getTechRefuseAttitudeThreshold", False),
        ("getTechTradeKnownPercent", True),
    ]),

    ("Gold Hoarder", [
        ("getMaxGoldTradePercent", False),
        ("getMaxGoldPerTurnTradePercent", False),
        ("getMapRefuseAttitudeThreshold", False),
    ]),

    ("Stingy", [
        # Refuses luxury/strategic bonuses
        ("getHealthBonusRefuseAttitudeThreshold", False),
        ("getHappinessBonusRefuseAttitudeThreshold", False),
        ("getStrategicBonusRefuseAttitudeThreshold", False),
    ]),

    # === DIPLOMATIC TRAITS ===
    ("Diplomatic", [
        ("getBasePeaceWeight", False),
        ("getTechTradeKnownPercent", False),
        ("getOpenBordersRefuseAttitudeThreshold", True),
        ("getSameReligionAttitudeChangeLimit", False),
        ("getWarmongerRespect", True),
    ]),

    ("Isolationist", [
        ("getOpenBordersRefuseAttitudeThreshold", False),
        ("getStopTradingRefuseAttitudeThreshold", False),
        ("getStopTradingThemRefuseAttitudeThreshold", False),
        ("getDeclareWarRefuseAttitudeThreshold", False),
    ]),

    ("Collaborative", [
        ("getShareWarAttitudeChangeLimit", False),
        ("getFavoriteCivicAttitudeChangeLimit", False),
        ("getSameReligionAttitudeChangeLimit", False),
        ("getOpenBordersRefuseAttitudeThreshold", True),
    ]),

    ("Sneaky", [
        ("getDemandRebukedSneakProb", False),
        ("getDogpileWarRand", False),
        ("getEspionageWeight", False),
        ("getDeclareWarTradeRand", False),
    ]),

    ("Backstabbing", [
        # Rebuked sneak demand -> war
        ("getDemandRebukedSneakProb", False),
        ("getDemandRebukedWarProb", False),
        ("getRefuseToTalkWarThreshold", False),
        ("getDeclareWarRefuseAttitudeThreshold", False),
    ]),

    ("Grudgy", [
        ("getWorseRankDifferenceAttitudeChange", False),
        ("getCloseBordersAttitudeChange", False),
        ("getDifferentReligionAttitudeChangeLimit", False),
    ]),

    ("Peaceful", [
        ("getMakePeaceRand", False),
        ("getBasePeaceWeight", False),
        ("getRefuseToTalkWarThreshold", True),
    ]),

    ("Civic Enforcer", [
        ("getFavoriteCivicAttitudeChangeLimit", False),
        ("getAdoptCivicRefuseAttitudeThreshold", False),
        ("getConvertReligionRefuseAttitudeThreshold", False),
        ("getNoTechTradeThreshold", False),
    ]),

    ("Flexible", [
        # Willing to change
        ("getAdoptCivicRefuseAttitudeThreshold", True),
        ("getConvertReligionRefuseAttitudeThreshold", True),
        ("getFavoriteCivicAttitudeChangeLimit", True),
    ]),

    ("Stubborn", [
        ("getTechRefuseAttitudeThreshold", False),
        ("getStopTradingRefuseAttitudeThreshold", False),
        ("getAdoptCivicRefuseAttitudeThreshold", False),
        ("getConvertReligionRefuseAttitudeThreshold", False),
        ("getDeclareWarRefuseAttitudeThreshold", False),
    ]),

    ("Globalist", [
        ("getTechTradeKnownPercent", False),
        ("getMaxWarDistantPowerRatio", False),
        ("getDeclareWarTradeRand", False),
        ("getOpenBordersRefuseAttitudeThreshold", True),
    ]),

    ("Power Tracker", [
        ("getMaxWarNearbyPowerRatio", False),
        ("getMaxWarDistantPowerRatio", False),
        ("getLimitedWarPowerRatio", False),
    ]),
]
"""


"""
ai aggregates v2-v3(?) with comments

REVISED_AI_AGGREGATES = [

	# === WAR / MILITARY ===
	("Warmonger", [
		# Willingness to declare various types of wars
		("getMaxWarRand", False),           # Higher = more likely to start big wars
		("getDogpileWarRand", False),       # Higher = more likely to join dogpiles
		("getLimitedWarRand", False),       # Higher = more likely to initiate limited tactical wars
		("getBuildUnitProb", False),        # Higher = more likely to build military units
		("getMakePeaceRand", False),        # Higher = delays peace talks
		("getWarmongerRespect", False),     # Higher = respects fellow warmongers (helps joint wars)
		("getBasePeaceWeight", True),       # Lower = less peace-oriented, so invert
	]),

	("Aggressive", [
		("getBaseAttackOddsChange", False), # Higher = attacks at higher odds
		("getAttackOddsChangeRand", False), # Higher = more variance in war choices
		("getBuildUnitProb", False),        # Higher = favors units over infrastructure
		("getMaxWarRand", False),           # More aggressive conflict planning
	]),

	("Dogpiler", [
		("getDogpileWarRand", False),
		("getDeclareWarTradeRand", False),
		("getWarmongerRespect", False),
	]),

	("Reckless", [
		("getBaseAttackOddsChange", False),        # Attacks even at lower odds
		("getLimitedWarRand", True),               # Lower = more reckless with small wars
		("getMaxWarRand", True),                   # Lower = no fear of big wars
		("getRefuseToTalkWarThreshold", True),     # Lower = won't stop talking, even during war
		("getDeclareWarRefuseAttitudeThreshold", True), # Lower = easier to push into war
	]),

	("Cautious", [
		("getLimitedWarPowerRatio", False),    # Higher = checks safety before war
		("getMaxWarNearbyPowerRatio", True),   # Lower = cautious
		("getMakePeaceRand", False),           # Makes peace faster
		("getRefuseToTalkWarThreshold", False) # Will stop talking more often
	]),

	("Vassalizer", [
		("getVassalRefuseAttitudeThreshold", False),  # Higher = harder to vassalize
		("getRefuseToTalkWarThreshold", True),        # Easier peace talks = more vassal offers
		("getMaxWarNearbyPowerRatio", False),         # Looks for vulnerable neighbors
	]),

	# === ECONOMIC ===
	("Builder", [
		("getBuildUnitProb", True),           # Lower = builds infrastructure
		("getWonderConstructRand", True),     # Lower = focused on wonders
		("getBasePeaceWeight", False),        # Higher = peace favors building
	]),

	("Wonder Chaser", [
		("getWonderConstructRand", True),     # Lower = loves wonders
		("getBuildUnitProb", True),           # Lower = favors non-military
	]),

	("Trader", [
		("getTechTradeKnownPercent", False),       # Shares tech freely
		("getDeclareWarTradeRand", False),         # Will declare war for trade deals
		("getMapRefuseAttitudeThreshold", True),   # Open to map trades
		("getMaxGoldTradePercent", False),         # Gives more in trades
		("getMaxGoldPerTurnTradePercent", False),
	]),

	("Tech Hoarder", [
		("getNoTechTradeThreshold", False),        # Hides techs
		("getTechRefuseAttitudeThreshold", False), # Refuses to trade techs easily
		("getTechTradeKnownPercent", True),        # Doesn't share techs
	]),

	("Gold Hoarder", [
		("getMaxGoldTradePercent", False),
		("getMaxGoldPerTurnTradePercent", False),
		("getMapRefuseAttitudeThreshold", False),
	]),

	("Stingy", [
		("getHealthBonusRefuseAttitudeThreshold", False),
		("getHappinessBonusRefuseAttitudeThreshold", False),
		("getStrategicBonusRefuseAttitudeThreshold", False),
	]),

	# === DIPLOMACY ===
	("Diplomatic", [
		("getBasePeaceWeight", False),
		("getTechTradeKnownPercent", False),
		("getOpenBordersRefuseAttitudeThreshold", True),
		("getSameReligionAttitudeChangeLimit", False),
		("getWarmongerRespect", True),
	]),

	("Isolationist", [
		("getOpenBordersRefuseAttitudeThreshold", False),
		("getStopTradingRefuseAttitudeThreshold", False),
		("getStopTradingThemRefuseAttitudeThreshold", False),
		("getDeclareWarRefuseAttitudeThreshold", False),
	]),

	("Collaborative", [
		("getShareWarAttitudeChangeLimit", False),
		("getFavoriteCivicAttitudeChangeLimit", False),
		("getSameReligionAttitudeChangeLimit", False),
		("getOpenBordersRefuseAttitudeThreshold", True),
	]),

	("Sneaky", [
		("getDemandRebukedSneakProb", False),
		("getDogpileWarRand", False),
		("getEspionageWeight", False),
		("getDeclareWarTradeRand", False),
	]),

	("Backstabbing", [
		("getDemandRebukedSneakProb", False),
		("getDemandRebukedWarProb", False),
		("getRefuseToTalkWarThreshold", False),
		("getDeclareWarRefuseAttitudeThreshold", False),
	]),

	("Peaceful", [
		("getMakePeaceRand", False),
		("getBasePeaceWeight", False),
		("getRefuseToTalkWarThreshold", True),
	]),

	("Grudgy", [
		("getWorseRankDifferenceAttitudeChange", False),
		("getCloseBordersAttitudeChange", False),
		("getDifferentReligionAttitudeChangeLimit", False),
	]),

	("Civic Enforcer", [
		("getFavoriteCivicAttitudeChangeLimit", False),
		("getAdoptCivicRefuseAttitudeThreshold", False),
		("getConvertReligionRefuseAttitudeThreshold", False),
		("getNoTechTradeThreshold", False),
	]),

	("Flexible", [
		("getAdoptCivicRefuseAttitudeThreshold", True),
		("getConvertReligionRefuseAttitudeThreshold", True),
		("getFavoriteCivicAttitudeChangeLimit", True),
	]),

	("Stubborn", [
		("getTechRefuseAttitudeThreshold", False),
		("getStopTradingRefuseAttitudeThreshold", False),
		("getAdoptCivicRefuseAttitudeThreshold", False),
		("getConvertReligionRefuseAttitudeThreshold", False),
		("getDeclareWarRefuseAttitudeThreshold", False),
	]),

	("Globalist", [
		("getTechTradeKnownPercent", False),
		("getMaxWarDistantPowerRatio", False),
		("getDeclareWarTradeRand", False),
		("getOpenBordersRefuseAttitudeThreshold", True),
	]),

	("Power Tracker", [
		("getMaxWarNearbyPowerRatio", False),
		("getMaxWarDistantPowerRatio", False),
		("getLimitedWarPowerRatio", False),
	]),

]
"""


"""
new version 1.5 fully commented this time but was another pass so check if no weird or missing data now, for now comemnted-out
# Aggregate personality categories (each combines multiple traits).
# Format: (Category Label, [(traitFuncName, invertFlag), ...])
# Each traitFuncName maps to a Civ4 LeaderHead XML value like iMaxWarRand.
# invertFlag=True means we invert the percentile ranking (lower = more of trait).

REVISED_AI_AGGREGATES = [
	# === WAR / CONFLICT BEHAVIOR ===
	("Warmonger", [
		("getMaxWarRand", False),          # High = more likely to declare total war
		("getLimitedWarRand", False),      # High = more likely to declare small wars
		("getDogpileWarRand", False),      # High = more likely to join ongoing wars
		("getBuildUnitProb", False),       # High = prefers building units over buildings
		("getMakePeaceRand", False),       # High = delays peace (more persistent at war)
		("getBasePeaceWeight", True),      # Low = warmonger; so we invert (low = more aggressive)
		("getWarmongerRespect", False),    # High = respects aggressive civs, war alliances
	]),
	("Backstabbing", [
		("getDogpileWarRand", False),           # Opportunistic war joins
		("getRefuseToTalkWarThreshold", False), # Prolongs war and avoids diplomacy
		("getMakePeaceRand", False),            # Delays making peace
		("getWarmongerRespect", False),         # Aligns with warmongers, aggression compounding
	]),
	("Opportunist", [
		("getDogpileWarRand", False),             # War opportunism
		("getTechTradeKnownPercent", False),      # Shares tech to gain leverage
		("getRefuseToTalkWarThreshold", False),   # Exploits war length for diplomatic gain
		("getAttackOddsChangeRand", False),       # Tactical randomness, gambles
	]),
	("Stubborn", [
		("getRefuseToTalkWarThreshold", False), # Refuses negotiations for longer
		("getMakePeaceRand", False),            # Dislikes ending wars
		("getNoTechTradeThreshold", False),     # Refuses tech trade more often
	]),
	("Cautious Aggressor", [
		("getLimitedWarRand", False),     # Selective war style
		("getMaxWarRand", True),          # Avoids all-out war (inverted)
		("getBaseAttackOddsChange", False), # Higher = confident attacks
		("getAttackOddsChangeRand", False), # Tactics over brute force
	]),

	# === ECONOMY / STRATEGY ===
	("Builder", [
		("getBuildUnitProb", True),             # Low = builds infrastructure over units
		("getWonderConstructRand", False),      # High = builds wonders
		("getBasePeaceWeight", False),          # High = peace-oriented
		("getTechTradeKnownPercent", False),    # Shares techs, indirectly supports economy
	]),
	("Tech Hoarder", [
		("getNoTechTradeThreshold", False),     # High = won't trade techs
		("getTechTradeKnownPercent", True),     # Low = hoards knowledge (inverted)
	]),
	("Trader", [
		("getTechTradeKnownPercent", False),    # High = shares techs
		("getNoTechTradeThreshold", True),      # Low = willingly trades techs
		("getBasePeaceWeight", False),          # High = peaceful civs trade more
	]),
	("Wonder Chaser", [
		("getWonderConstructRand", False),      # High = focuses on wonders
		("getBuildUnitProb", True),             # Low = invests in buildings
	]),
	("Unit Spammer", [
		("getBuildUnitProb", False),            # High = spams units
		("getMaxWarRand", False),               # Aggressive strategic posture
		("getLimitedWarRand", False),           # Tactical aggression
	]),

	# === DIPLOMACY ===
	("Peaceful", [
		("getMakePeaceRand", True),             # Low = prefers ending wars quickly (inverted)
		("getBasePeaceWeight", False),          # High = peace-loving
		("getSameReligionAttitudeChangeLimit", False), # More religious tolerance
	]),
	("Zealot", [
		("getSameReligionAttitudeChangeLimit", False),  # Strong positive bias to own religion
		("getOpenBordersRefuseAttitudeThreshold", False), # Denies open borders more often
	]),
	("Isolationist", [
		("getOpenBordersRefuseAttitudeThreshold", False),  # Denies open borders
		("getTechTradeKnownPercent", True),                # Secretive tech stance (inverted)
		("getNoTechTradeThreshold", False),                # Hoards techs
	]),
	("Globalist", [
		("getOpenBordersRefuseAttitudeThreshold", True),   # Accepts open borders (inverted)
		("getTechTradeKnownPercent", False),               # Willing to share tech
		("getBasePeaceWeight", False),                     # Peace-promoting civ
	]),
	("Allied Warmonger", [
		("getWarmongerRespect", False),              # Likes warmonger allies
		("getDogpileWarRand", False),                # Joins allies in wars
		("getShareWarAttitudeChangeLimit", False),   # Strong diplomatic boost for shared wars
	]),
	("Reluctant Ally", [
		("getShareWarAttitudeChangeLimit", True),     # Doesn’t care about shared wars (inverted)
		("getWarmongerRespect", True),                # Avoids warmongers (inverted)
		("getRefuseToTalkWarThreshold", True),        # Negotiates quickly during wars
	]),

	# === STRATEGIC STYLE ===
	("Risk Taker", [
		("getAttackOddsChangeRand", False), # High = unpredictability
		("getBaseAttackOddsChange", False), # High = aggressive attack stances
	]),
	("Micro-manager", [
		("getAttackOddsChangeRand", False),  # Adapts to tactics
		("getMakePeaceRand", False),         # War continuation micro-managed
	]),
	("Predictable", [
		("getAttackOddsChangeRand", True), # Low variance = predictable (inverted)
	]),
	("Religious Diplomat", [
		("getSameReligionAttitudeChangeLimit", False), # Prioritizes religious alliances
		("getOpenBordersRefuseAttitudeThreshold", True), # Encourages open borders
	]),
	("Tech Diplomat", [
		("getTechTradeKnownPercent", False), # Shares tech freely
		("getNoTechTradeThreshold", True),   # Open to trade (inverted)
	]),
	("Brute Force", [
		("getBuildUnitProb", False),              # Spams units
		("getBaseAttackOddsChange", False),       # Likes favorable odds
		("getAttackOddsChangeRand", True),        # Predictable attacks (inverted)
	]),
	("Balanced", [
		("getBuildUnitProb", False),              # Maintains military
		("getTechTradeKnownPercent", False),      # Shares techs
		("getWonderConstructRand", False),        # Builds wonders
		("getBasePeaceWeight", False),            # Moderate peace preference
	]),
]
"""


"""
and version 1.75 that shoudl maybe eb our final one double check ith new v1
this one has extra comments now (remove memojia n d all all good)
# Aggregate personality categories (each combines multiple traits).
# Format: (Category Label, [(traitFuncName, invertFlag), ...])
# Each traitFuncName maps to a Civ4 LeaderHead XML value like iMaxWarRand.
# invertFlag=True means we invert the percentile ranking (lower = more of trait).

REVISED_AI_AGGREGATES = [

	# === WAR / CONFLICT BEHAVIOR ===
	("Warmonger", [
		# ✅ High = more total wars. Used directly.
		("getMaxWarRand", False),           # 🔁 Invert=False | High = more likely to declare total war

		# ✅ High = tactical wars. Direct indicator of aggressiveness.
		("getLimitedWarRand", False),       # 🔁 Invert=False | High = more limited/tactical war declarations

		# ✅ High = opportunistic. Joins dogpiles more easily.
		("getDogpileWarRand", False),       # 🔁 Invert=False | High = more opportunistic in war

		# ✅ High = trains more units. Strong indicator of militarism.
		("getBuildUnitProb", False),        # 🔁 Invert=False | High = prefers military unit production

		# ✅ High = stays in war longer. Warmonger behavior.
		("getMakePeaceRand", False),        # 🔁 Invert=False | High = delays peace agreements

		# ✅ Low = more aggressive. Invert so lower score means stronger warmonger.
		("getBasePeaceWeight", True),       # 🔁 Invert=True | Low = aggressive (so invert)

		# ✅ High = likes warmongers. Reinforces aggression networks.
		("getWarmongerRespect", False),     # 🔁 Invert=False | High = more respect for other warmongers
	]),

	("Backstabbing", [
		# ✅ High = joins wars opportunistically. Opportunistic behavior.
		("getDogpileWarRand", False),           # 🔁 Invert=False | Opportunistic war declaration

		# ✅ High = avoids diplomacy in war. Useful for sneak/backstab behavior.
		("getRefuseToTalkWarThreshold", False), # 🔁 Invert=False | Higher = avoids talking during war

		# ✅ High = delays peace. Suggests untrustworthy or persistent warlike stance.
		("getMakePeaceRand", False),            # 🔁 Invert=False | Stays in war longer

		# ✅ High = aligns with aggressors. Reinforces betrayal dynamics.
		("getWarmongerRespect", False),         # 🔁 Invert=False | Supports backstabbing alliances
	]),

	("Opportunist", [
		# ✅ High = joins wars opportunistically
		("getDogpileWarRand", False),             # 🔁 Invert=False | Opportunistic warmongering

		# ✅ High = shares tech for leverage. Supports economic opportunism.
		("getTechTradeKnownPercent", False),      # 🔁 Invert=False | Willing to trade known techs

		# ✅ High = won’t negotiate in war. Strategic leverage during war.
		("getRefuseToTalkWarThreshold", False),   # 🔁 Invert=False | Negotiation refusal

		# ✅ High = combat randomness. Useful for unpredictability.
		("getAttackOddsChangeRand", False),       # 🔁 Invert=False | Tactical variation
	]),

	("Stubborn", [
		# ✅ High = doesn’t negotiate. Classic stubborn trait.
		("getRefuseToTalkWarThreshold", False), # 🔁 Invert=False | Refuses negotiation longer

		# ✅ High = delays peace. Refusal to settle.
		("getMakePeaceRand", False),            # 🔁 Invert=False | Stays in war

		# ✅ High = refuses tech trade. Secretive and uncooperative.
		("getNoTechTradeThreshold", False),     # 🔁 Invert=False | Refuses to trade technology
	]),

	("Cautious Aggressor", [
		# ✅ High = favors tactical wars, not reckless.
		("getLimitedWarRand", False),     # 🔁 Invert=False | Tactical engagement

		# ✅ Low = avoids all-out war. Invert to favor cautiousness.
		("getMaxWarRand", True),          # 🔁 Invert=True | Low = less likely to do all-out war

		# ✅ High = expects better odds. Not reckless.
		("getBaseAttackOddsChange", False), # 🔁 Invert=False | Requires favorable odds to attack

		# ✅ High = varies attacks. Supports adaptability.
		("getAttackOddsChangeRand", False), # 🔁 Invert=False | Tactical flexibility
	]),

	# === ECONOMY / STRATEGY ===
	("Builder", [
		# ✅ Low = prefers buildings. Invert to reward low military unit preference.
		("getBuildUnitProb", True),             # 🔁 Invert=True | Lower = less military focus

		# ✅ High = builds wonders. Classic builder trait.
		("getWonderConstructRand", False),      # 🔁 Invert=False | Likes building wonders

		# ✅ High = peaceful alignment. Builders tend to avoid conflict.
		("getBasePeaceWeight", False),          # 🔁 Invert=False | Peace-seeking

		# ✅ High = shares tech. Collaborative economy.
		("getTechTradeKnownPercent", False),    # 🔁 Invert=False | Transparency in research
	]),

	("Tech Hoarder", [
		# ✅ High = refuses tech trade. Classic hoarder.
		("getNoTechTradeThreshold", False),     # 🔁 Invert=False | More secretive

		# ✅ Low = hides tech. Invert because low means hoarding.
		("getTechTradeKnownPercent", True),     # 🔁 Invert=True | Hides known techs
	]),

	("Trader", [
		# ✅ High = tech sharing. Encourages trade.
		("getTechTradeKnownPercent", False),    # 🔁 Invert=False | Shares knowledge

		# ✅ Low = tech trade threshold. More likely to accept trades.
		("getNoTechTradeThreshold", True),      # 🔁 Invert=True | Willing to trade

		# ✅ High = peaceful civs are more open to trade.
		("getBasePeaceWeight", False),          # 🔁 Invert=False | Trade through peaceful alignment
	]),

	("Wonder Chaser", [
		# ✅ High = constructs wonders.
		("getWonderConstructRand", False),      # 🔁 Invert=False | Obsession with wonders

		# ✅ Low = avoids units. Invert to reward peaceful builders.
		("getBuildUnitProb", True),             # 🔁 Invert=True | Avoids military build-up
	]),

	("Unit Spammer", [
		# ✅ High = constantly builds units.
		("getBuildUnitProb", False),            # 🔁 Invert=False | Heavy military production

		# ✅ High = favors total wars.
		("getMaxWarRand", False),               # 🔁 Invert=False | Strategic aggression

		# ✅ High = favors limited wars. Just as frequent.
		("getLimitedWarRand", False),           # 🔁 Invert=False | Tactical warfare
	]),

	# === DIPLOMACY ===
	("Peaceful", [
		# ✅ Low = more likely to make peace. Invert to favor pacifists.
		("getMakePeaceRand", True),             # 🔁 Invert=True | Ends wars early

		# ✅ High = peaceful baseline.
		("getBasePeaceWeight", False),          # 🔁 Invert=False | Core peace metric

		# ✅ High = tolerance for same religion civs.
		("getSameReligionAttitudeChangeLimit", False), # 🔁 Invert=False | Religious diplomacy
	]),

	("Zealot", [
		# ✅ High = strong religious bias.
		("getSameReligionAttitudeChangeLimit", False),  # 🔁 Invert=False | Religious favoritism

		# ✅ High = closes borders to non-aligned civs.
		("getOpenBordersRefuseAttitudeThreshold", False), # 🔁 Invert=False | Less international
	]),

	("Isolationist", [
		# ✅ High = closed borders.
		("getOpenBordersRefuseAttitudeThreshold", False),  # 🔁 Invert=False | No foreign entanglement

		# ✅ Low = hides tech. Invert to show isolation.
		("getTechTradeKnownPercent", True),                # 🔁 Invert=True | Secretive tech stance

		# ✅ High = refuses to trade. Classic hoarder.
		("getNoTechTradeThreshold", False),                # 🔁 Invert=False | Anti-trade stance
	]),

	("Globalist", [
		# ✅ Low = open borders. Invert to make high score mean openness.
		("getOpenBordersRefuseAttitudeThreshold", True),   # 🔁 Invert=True | Welcomes open borders

		# ✅ High = shares techs.
		("getTechTradeKnownPercent", False),               # 🔁 Invert=False | Collaborative

		# ✅ High = peaceful stance.
		("getBasePeaceWeight", False),                     # 🔁 Invert=False | Diplomacy-enabling
	]),

	("Allied Warmonger", [
		# ✅ High = aligns with warlike civs.
		("getWarmongerRespect", False),              # 🔁 Invert=False | Likes warlike allies

		# ✅ High = joins in ongoing wars.
		("getDogpileWarRand", False),                # 🔁 Invert=False | War coordination

		# ✅ High = bonus for shared war. Supports coalitions.
		("getShareWarAttitudeChangeLimit", False),   # 🔁 Invert=False | Shared war diplomacy
	]),

	("Reluctant Ally", [
		# ✅ Low = doesn’t care for shared wars. Invert to measure reluctance.
		("getShareWarAttitudeChangeLimit", True),     # 🔁 Invert=True | Avoids shared war alliances

		# ✅ Low = dislikes warmongers. Invert to show pacifism.
		("getWarmongerRespect", True),                # 🔁 Invert=True | Avoids aggressive allies

		# ✅ Low = negotiates quickly. Invert to show willingness to ally/diplomacy.
		("getRefuseToTalkWarThreshold", True),        # 🔁 Invert=True | Willing to negotiate during war
	]),

	# === STRATEGY STYLE ===
	("Risk Taker", [
		# ✅ High = uses random odds. Risk-prone.
		("getAttackOddsChangeRand", False), # 🔁 Invert=False | Unpredictable attacker

		# ✅ High = presses attacks with worse odds.
		("getBaseAttackOddsChange", False), # 🔁 Invert=False | Aggressive stance
	]),

	("Micro-manager", [
		# ✅ High = varies attacks, avoids brute force.
		("getAttackOddsChangeRand", False),  # 🔁 Invert=False | Adapts strategies

		# ✅ High = delays peace, shows micromanaged war
		("getMakePeaceRand", False),         # 🔁 Invert=False | War control
	]),

	("Predictable", [
		# ✅ Low = consistent attacks. Invert for predictability.
		("getAttackOddsChangeRand", True), # 🔁 Invert=True | Predictable war AI
	]),

	("Religious Diplomat", [
		# ✅ High = favors religious unity.
		("getSameReligionAttitudeChangeLimit", False), # 🔁 Invert=False | Religious alignment

		# ✅ Low = accepts borders. Invert to favor diplomacy.
		("getOpenBordersRefuseAttitudeThreshold", True), # 🔁 Invert=True | Welcomes cooperation
	]),

	("Tech Diplomat", [
		# ✅ High = transparent with tech.
		("getTechTradeKnownPercent", False), # 🔁 Invert=False | Open trader

		# ✅ Low = accepts trades. Invert to favor trade willingness.
		("getNoTechTradeThreshold", True),   # 🔁 Invert=True | Willing to trade
	]),

	("Brute Force", [
		# ✅ High = trains units.
		("getBuildUnitProb", False),              # 🔁 Invert=False | Pure militarist

		# ✅ High = favors attack odds.
		("getBaseAttackOddsChange", False),       # 🔁 Invert=False | Strong combat stance

		# ✅ Low = predictable, brute force instead of tactics. Invert to reward consistency.
		("getAttackOddsChangeRand", True),        # 🔁 Invert=True | Predictable attacker
	]),

	("Balanced", [
		# ✅ Builds units
		("getBuildUnitProb", False),              # 🔁 Invert=False | Maintains military

		# ✅ Shares tech
		("getTechTradeKnownPercent", False),      # 🔁 Invert=False | Collaborative

		# ✅ Builds wonders
		("getWonderConstructRand", False),        # 🔁 Invert=False | Builder support

		# ✅ Peace-oriented
		("getBasePeaceWeight", False),            # 🔁 Invert=False | Avoids unnecessary war
	]),
]
"""

# Aggregate personality categories (each combines multiple traits).
# Format: (Category Label, [(traitFuncName, invertFlag), ...])
# The invertFlag is preserved from old code but actual inversion is
# <!--custom: per-aggregate --> controlled <!-- custom now, no longer global).
REVISED_AI_AGGREGATES = [
	# --- WAR / CONFLICT BEHAVIOR ---
	("Warmonger", [
		("getMaxWarRand", False),          # High = more likely to declare total war
		("getLimitedWarRand", False),      # High = more tactical wars
		("getDogpileWarRand", False),      # High = more opportunistic wars
		("getBuildUnitProb", False),       # High = prefers unit production
		("getMakePeaceRand", False),       # High = delays peace
		("getBasePeaceWeight", True),      # Low = warmongering, so invert
		("getWarmongerRespect", False),    # High = allies with warmongers
	]),
	("Backstabbing", [
		("getDogpileWarRand", False),           # Jumps on weakened enemies
		("getRefuseToTalkWarThreshold", False), # Stubborn in war
		("getMakePeaceRand", False),            # Delays peace
		("getWarmongerRespect", False),         # Encourages aggression
	]),
	("Opportunist", [
		("getDogpileWarRand", False),             # Takes advantage
		("getTechTradeKnownPercent", False),      # Shares techs for leverage
		("getRefuseToTalkWarThreshold", False),   # Uses war time for deals
		("getAttackOddsChangeRand", False),       # Tactical variability
	]),
	("Stubborn", [
		("getRefuseToTalkWarThreshold", False), # Never surrenders
		("getMakePeaceRand", False),            # Prolongs war
		("getNoTechTradeThreshold", False),     # Hides techs
	]),
	("Cautious Aggressor", [
		("getLimitedWarRand", False),     # Prefers minor wars
		("getMaxWarRand", True),          # Avoids total war
		("getBaseAttackOddsChange", False),
		("getAttackOddsChangeRand", False),
	]),

	# --- ECONOMY / STRATEGY ---
	("Builder", [
		("getBuildUnitProb", True),             # Low = focuses on buildings
		("getWonderConstructRand", False),      # High = likes wonders
		("getBasePeaceWeight", False),          # High = peaceful
		("getTechTradeKnownPercent", False),    # Shares techs
	]),
	("Tech Hoarder", [
		("getNoTechTradeThreshold", False),     # High = won't trade
		("getTechTradeKnownPercent", True),     # Low = secretive
	]),
	("Trader", [
		("getTechTradeKnownPercent", False),    # Shares techs
		("getNoTechTradeThreshold", True),      # Willing to share
		("getBasePeaceWeight", False),          # Peaceful civs trade more
	]),
	("Wonder Chaser", [
		("getWonderConstructRand", False),      # High = wonders
		("getBuildUnitProb", True),             # Low = not militaristic
	]),
	("Unit Spammer", [
		("getBuildUnitProb", False),      # Mass unit production
		("getMaxWarRand", False),
		("getLimitedWarRand", False),
	]),

	# --- DIPLOMACY ---
	("Peaceful", [
		("getMakePeaceRand", True),             # Ends war fast
		("getBasePeaceWeight", False),          # Likes peace
		("getSameReligionAttitudeChangeLimit", False),
	]),
	("Zealot", [
		("getSameReligionAttitudeChangeLimit", False),  # Strong religion bias
		("getOpenBordersRefuseAttitudeThreshold", False),
	]),
	("Isolationist", [
		("getOpenBordersRefuseAttitudeThreshold", False),  # Refuses open borders
		("getTechTradeKnownPercent", True),                # Hides techs
		("getNoTechTradeThreshold", False),                # Hoards techs
	]),
	("Globalist", [
		("getOpenBordersRefuseAttitudeThreshold", True),  # Willing to open borders
		("getTechTradeKnownPercent", False),
		("getBasePeaceWeight", False),
	]),
	("Allied Warmonger", [
		("getWarmongerRespect", False),              # Allies with warmongers
		("getDogpileWarRand", False),                # Helps allies in war
		("getShareWarAttitudeChangeLimit", False),   # Big bonus for shared war
	]),
	("Reluctant Ally", [
		("getShareWarAttitudeChangeLimit", True),     # Doesn't care about shared wars
		("getWarmongerRespect", True),
		("getRefuseToTalkWarThreshold", True),
	]),

	# --- STRATEGY STYLE ---
	("Risk Taker", [
		("getAttackOddsChangeRand", False),
		("getBaseAttackOddsChange", False),
	]),
	("Micro-manager", [
		("getAttackOddsChangeRand", False),
		("getMakePeaceRand", False),
	]),
	("Predictable", [
		("getAttackOddsChangeRand", True), # Low randomness
	]),
	("Religious Diplomat", [
		("getSameReligionAttitudeChangeLimit", False),
		("getOpenBordersRefuseAttitudeThreshold", True),
	]),
	("Tech Diplomat", [
		("getTechTradeKnownPercent", False),
		("getNoTechTradeThreshold", True),
	]),
	("Brute Force", [
		("getBuildUnitProb", False),
		("getBaseAttackOddsChange", False),
		("getAttackOddsChangeRand", True),  # Predictable, consistent attacks
	]),
	("Balanced", [
		("getBuildUnitProb", False),
		("getTechTradeKnownPercent", False),
		("getWonderConstructRand", False),
		("getBasePeaceWeight", False),
	]),
]



# --- Utility: Percentile calculation (0–100) with optional inversion ---
def get_percentile(value, sorted_values, inverse=False):
    """Return the percentile rank (0-100) of 'value' within 'sorted_values'. If inverse=True, flip the scale."""
    if not sorted_values:
        return 0
    count = len(sorted_values)
    # Find position of value in sorted list
    for i in range(count):
        if value <= sorted_values[i]:
            # Percentile position based on index (evenly distributed across ranks)
            if count == 1:
                pos = 100  # Only one value, consider it max percentile
            else:
                pos = int(i * 100 / (count - 1))
            break
    else:
        # Value is greater than all in list
        pos = 100
    if inverse:
        return 100 - pos
    return pos

# --- Global caches for AI values and scores ---
AI_VALUE_RANGES = {}        # {funcName: (minValue, maxValue)} for all leaders
AI_SORTED_VALUES = {}       # {funcName: [allLeaderValuesSorted]}
AI_ATTRIBUTE_DATA = {}      # {iLeader: { funcName: {"raw": val, "normalized": percentile} } }
AI_AGGREGATE_SCORES = {}    # {iLeader: { aggregateLabel: medianPercentile } }
AI_AGGREGATE_RAW_SCORES = {}# {iLeader: { aggregateLabel: averagePercentile } }

# --- Caching function: Compute min/max ranges and sorted values for all AI traits ---
def cache_ai_value_ranges():
    """Populate AI_VALUE_RANGES and AI_SORTED_VALUES for all AI trait functions across all leaders."""
    global AI_VALUE_RANGES, AI_SORTED_VALUES
    AI_VALUE_RANGES.clear()
    AI_SORTED_VALUES.clear()
    all_func_values = {}
    numLeaders = gc.getNumLeaderHeadInfos()

    # Collect all leaders' values for each getFunction
    for i in range(numLeaders):
        leaderInfo = gc.getLeaderHeadInfo(i)
        for funcName in dir(leaderInfo):
            if not funcName.startswith("get"):
                continue
            func = getattr(leaderInfo, funcName)
            if not callable(func):
                continue
            try:
                val = func()  # call the getX function
            except Exception:
                continue
            all_func_values.setdefault(funcName, []).append(val)

    # Compute ranges and sorted lists
    for funcName, values in all_func_values.items():
        if values:
            AI_VALUE_RANGES[funcName] = (min(values), max(values))
            AI_SORTED_VALUES[funcName] = sorted(values)

# --- Caching function: Compute per-leader raw and normalized trait values ---
def cache_ai_attribute_data():
    """Populate AI_ATTRIBUTE_DATA with each leader's raw and percentile-normalized values for every trait."""
    global AI_ATTRIBUTE_DATA
    AI_ATTRIBUTE_DATA.clear()
    numLeaders = gc.getNumLeaderHeadInfos()
    for iLeader in range(numLeaders):
        leaderInfo = gc.getLeaderHeadInfo(iLeader)
        leader_data = {}
        for funcName, sorted_vals in AI_SORTED_VALUES.items():
            if not sorted_vals:
                continue
            try:
                raw_val = getattr(leaderInfo, funcName)()
            except Exception:
                continue
            # Compute percentile, as for inverting we never invert raw trait
			# values anymore. They are shown as-is in the raw categories.
			# Only aggregates apply inversion.
            norm_val = get_percentile(raw_val, sorted_vals, inverse=False)
            leader_data[funcName] = {"raw": raw_val, "normalized": norm_val}
        AI_ATTRIBUTE_DATA[iLeader] = leader_data

# --- Caching function: Compute per-leader aggregate scores (median and average) ---
def cache_ai_aggregate_scores():
    """Populate AI_AGGREGATE_SCORES and AI_AGGREGATE_RAW_SCORES with percentile-based aggregate category scores."""
    global AI_AGGREGATE_SCORES, AI_AGGREGATE_RAW_SCORES
    AI_AGGREGATE_SCORES.clear()
    AI_AGGREGATE_RAW_SCORES.clear()
    numLeaders = gc.getNumLeaderHeadInfos()
    for iLeader in range(numLeaders):
        leaderInfo = gc.getLeaderHeadInfo(iLeader)
        agg_medians = {}
        agg_averages = {}
        # Calculate aggregate score for each category
        for label, fields in REVISED_AI_AGGREGATES:
            print("[DEBUG] Starting aggregate:", label)
            percentiles = []
            for funcName, invert in fields:  # per-aggregate inversion logic
                try:
                    raw_val = getattr(leaderInfo, funcName)()
                except Exception:
                    print("[DEBUG]  - ERROR in %s: %s" % (funcName, sys.exc_info()[1]))
                    continue
                sorted_vals = AI_SORTED_VALUES.get(funcName, [])
                if not sorted_vals:
                    continue
                print("[DEBUG]      Trait %s | raw=%d | invert=%s" % (funcName, raw_val, invert))
                pct = get_percentile(raw_val, sorted_vals, inverse=invert)
                print("[DEBUG]      Percentile for %s: %d" % (funcName, pct))
                print("[DEBUG]  - Leader %d | %s: raw=%d, pct=%d, invert=%s" % (iLeader, funcName, raw_val, pct, invert))
                percentiles.append(pct)
            if percentiles:
                # Average (mean) of percentiles
				# <!-- custom: avoid 100.4 (for example) being rounded to 101 -->
                avg_score = min(100, int(round(sum(percentiles) / float(len(percentiles)))))
                # Median of percentiles (middle value in sorted order)
                sorted_pcts = sorted(percentiles)
				# <!-- custom: avoid 100.4 (for example) being rounded to 101 -->
                median_score = min(100, sorted_pcts[len(sorted_pcts) // 2])
                print("[DEBUG]    > Final %s score: avg=%d, median=%d, count=%d" % (label, avg_score, median_score, len(percentiles)))
            else:
                avg_score = 0
                median_score = 0
            agg_medians[label] = median_score
            agg_averages[label] = avg_score
        AI_AGGREGATE_SCORES[iLeader] = agg_medians
        AI_AGGREGATE_RAW_SCORES[iLeader] = agg_averages

# --- Initialize the caches at module load (so UI can directly use the data) ---
cache_ai_value_ranges()
cache_ai_attribute_data()
cache_ai_aggregate_scores()



# (<!-- custom: paper note and pen emoji, removed replaced with this text for same reason etc anyways etc -->)
# However, in future we may want to render AI_AGGREGATE_RAW_SCORES (average) alongside or as a tooltip, toggle, or legend.
# For now, averages are computed and stored, but not shown.



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

			# === PANEL SETUP ===
			firstPanelName = self.top.getNextWidgetName()
			screen.addPanel(firstPanelName, localText.getText("TXT_KEY_AI_PERSONALITY", ()) + " (1)", "", True, True,
							self.X_AI_PERSONALITY, self.Y_AI_PERSONALITY,
							self.W_AI_PERSONALITY, self.H_AI_PERSONALITY,
							PanelStyles.PANEL_STYLE_BLUE50)

			secondPanelName = self.top.getNextWidgetName()
			xSecond = self.X_AI_PERSONALITY - self.W_AI_PERSONALITY - self.MEDIUM_MARGIN
			screen.addPanel(secondPanelName, localText.getText("TXT_KEY_AI_PERSONALITY", ()) + " (2)", "", True, True,
							xSecond, self.Y_AI_PERSONALITY,
							self.W_AI_PERSONALITY, self.H_AI_PERSONALITY,
							PanelStyles.PANEL_STYLE_BLUE50)

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



			right_categories = [
				AI_HEADER_WAR_STRATEGY,
				AI_HEADER_AGGREGATES
			]
			left_categories = [
				AI_HEADER_DIPLOMACY,
				AI_HEADER_ATTITUDE,
				AI_HEADER_ECONOMIC_BEHAVIOR,
				AI_HEADER_TRADE
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
						for idx, (label, _) in enumerate(REVISED_AI_AGGREGATES):
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
							raw_value = AI_ATTRIBUTE_DATA.get(iLeader, {}).get(funcName, {}).get("raw", 0)
							norm_score = AI_ATTRIBUTE_DATA.get(iLeader, {}).get(funcName, {}).get("normalized", 0)
							symbols_used = get_symbol_scale(norm_score)

							screen.setText(self.top.getNextWidgetName(), "", u"<font=2>%s</font>" % label,
											CvUtil.FONT_LEFT_JUSTIFY, xName, y, 0, FontTypes.SMALL_FONT,
											WidgetTypes.WIDGET_GENERAL, -1, -1)
							screen.setText(self.top.getNextWidgetName(), "", u"<font=2b>%d</font>" % raw_value,
											CvUtil.FONT_LEFT_JUSTIFY, xValue, y, 0, FontTypes.SMALL_FONT,
											WidgetTypes.WIDGET_GENERAL, -1, -1)
							screen.setText(self.top.getNextWidgetName(), "", u"<font=2>%s</font>" % symbols_used,
											CvUtil.FONT_LEFT_JUSTIFY, xScale, y, 0, FontTypes.SMALL_FONT,
											WidgetTypes.WIDGET_GENERAL, -1, -1)
							y += lineHeight
						except:
							pass

			render_categories(screen, right_categories, xName1, xValue1, xScale1, y1)
			render_categories(screen, left_categories, xName2, xValue2, xScale2, y2)
		
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

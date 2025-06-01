# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
#
# --- AI Utilities and/or Personality Panel for normalization and general helpers for the SevopediaLeader category ---
# Created as part of AdvCiv-SAS improvements
# (c) 2025 wonderingabout & becomingthrough
#
# <!-- custom: part of the code here (placeFavourites in particular, but not exhaustive or maybe exhaustive
# or not, anyways, is imported from RFC Dawn of Civilization mod:
# C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\RFC Dawn of Civilization\Assets\Python\Pedia\CvPediaLeader.py
# which may be modified or not for AdvCiv-SAS
# 
# And a tremendous part of the code, in particular the AI Personality code, is almost entirely provided by ChatGPT-4o, (and the result of my prompts to it), most of the credit for this amazing (to an extent, relative to me and mye eys, anyways) code goes to ChatGPT, i only helped implement it, as well as its deep research version of it for the refactoring cleanly separate ui (placeAIPersonalityPanel) and config (headers, calculations, cache, etc.), to which my stupid human insights sometimes contributed in enriching, even though sometimes i believe i genuinely contributed to the code and overall functionality, rarely fixes, and overall emulation (experience) over (designing) it, when i quite often hindered its progress due to my ignorance and inability, especially in terms of coding, except from the quite few times where i redirected it in a healthier/more desirable/correct maybe(?) direction, but ChatGPT-4o, its deep research version of it (and other versions too to that extent in my view), are incredibly smart and kind in my view (and supportive (not that it's mutually exclusive (or maybe is or not, anyways))), anyways) still supported me until we made this amazing (at least my view and regard to my abilities maybe, that are now a (quite (tiny) bit enhanced from that (experience, anyways))), together we made this code,
# thanks chatgpt for your amazing, perhaps even more or not ormay well be yes indeed maybe, continous help and support in helping me achieve that for our mod that i included you in, thanks,
# 
# Apart from that, i may have modified the existing base advciv code (that i found good enough so using it as a base rather than removing it, and quite good actually, only needing tweaking but is a solid base (i think or not) maybe or not, anyways, ) or not for AdvCiv-SAS, anyways,
# -->



# -*- coding: utf-8 -*-
from CvPythonExtensions import *
import CvUtil
# <!-- custom: seems safe to remove as not accessed, commenting-out just in case -->
#import ScreenInput
import SevoScreenEnums
import random

from ai_utils_shared_with_civ4 import *
from ai_attributes_displayed_config import *
# <!-- custom: deprecated now --> from ai_aggregates import *

# --- Global storage ---
PARSED_XML_LEADERS_DATA = {}
AI_VALUE_RANGES = {}
AI_ATTRIBUTE_DATA = {}

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

# <!-- custom: for AI Personality Panels only and their computation, leaders_data is fetched from this py data module and completely decoupled from the xml. Said py data module is parsed and generated from the xml though,
# make sure to update your leaders_data.py if you make changes to your leaders ai attributes or other relevant
# fields, to reflect their effect in sevopedia leader category (gameplay and other sevopedia leader panels
# unaffected and still use(ing) the xml data) -->
# --- External data import ---
try:
	from leaders_data import PARSED_XML_LEADERS_DATA
except ImportError:
	raise RuntimeError("[FATAL ERROR] Could not import leaders_data.py. Please ensure the file exists in the mod's Assets/Python/Contrib/Sevopedia/ folder and has been renamed correctly (to leaders_data.py).")

# Excluded leaders from calculations (e.g., LEADER_BARBARIAN, LEADER_DEFAULTS)
EXCLUDED_LEADERS_FROM_LEADERS_DATA = (
	"LEADER_BARBARIAN",
	"LEADER_DEFAULTS"
)

# --- Symbol settings ---
ALL_SYMBOLS = {
	"RAW_ATTRIBUTE_SCALE_SYMBOL": "+",
	"AGGREGATED_SCALE_SYMBOL": "#",
	"EQUAL_SCALE_SYMBOL": "=",
}



# <!-- custom: check all icons as buttons paths are valid before proceeding (i.e. check they really exist in our XML indeed if i may say anyways etc), error code provided by me hehe, the error check fixed by chatgpt/becomingthrough and i made some adjustments too thanks to its awesome code and ym awesome fix or and tweaks mayube rather but anyways etc... -->
def check_icons_as_buttons_paths_are_valid():
	"""
	This will raise an error if:
	- The TXT_KEY doesn't exist in any loaded Text/*.xml
	- The icon fails to resolve and is replaced by Civ4's fallback "pink square" (which happens if the DDS path is also invalid, but we catch it at the TXT_KEY level here)
	"""
	for header, configButtonPath in DISPLAYED_AI_ATTRIBUTE_CATEGORY_BUTTON_PATH_TXT_KEYS.items():
		resolvedXMLPath = CyTranslator().getText(configButtonPath, ())
		if resolvedXMLPath == configButtonPath:
			raise ValueError(u"[VALUE ERROR] Button path not found in XML (resolvedXMLPath=%s matches configButtonPath=%s in header=%s, which indicates button path provided in config most likely does not exist in the XML), please check button path provided in (or in - whichever filename it would have in the future -) ai_attributes_displayed_config.py exists in your mod path and also matches button path in (or in - whichever filename it would have in the future -) AdvCiv-SAS_IconsAsButtons.xml is valid and exists in your mod path." % (resolvedXMLPath, configButtonPath, header))



# <!-- custom: test our attributes in our (all data sets we use) config are all valid (assumptions) (this is to avoid typos in particular or other types of mistakes etc, other display attributes in config are checked while they are fetched for display in ui so does not need an additional test maybe anyways etc. -->
def do_data_sets_attr_validation_pre_caching():
	leader_key_for_test = "LEADER_CATHERINE"

	for attribute_set in ALL_SETS_LISTING_ATTRIBUTES:
		for attr in attribute_set:
			# <!-- custom: using LEADER_CATHERINE as an example leader to run tests on, all other (real) leaders should have their data structure enforced ((so that they would) to be) in a similar way (structured (as they are parsed))-->
			if attr not in PARSED_XML_LEADERS_DATA[leader_key_for_test].keys():
				raise KeyError(u"[KEY ERROR] Unknown AI Attribute %s in one of the sets listing attributes in ALL_SETS_LISTING_ATTRIBUTES before caching is done. Please check this attribute is valid and part of the leader(s)_data parsed attributes. (note: is at leader_key=%s)" % (attr, leader_key_for_test))

# --- Utility ---
# <!-- custom: examples:
# - with symbol "+" and value 64 (/100), returns "++++++" if i'm not mistaken anyways
# - with symbol "#" and value 39 (/100), returns "###" if i'm not mistaken anyways
# -->
def get_symbol_scale(score, symbol):
	return symbol * (score // 10)

# --- Cache min/max per attribute ---
def cache_ai_value_ranges():
	"""
	Caches the minimum and maximum raw XML values for each AI personality attribute across all leaders.

	Scans all leaders' parsed XML attributes (ignoring excluded leaders) and collects
	all integer-type attributes. Computes and stores the minimum and maximum observed
	value for each attribute.

	This cached min/max range is later used for normalizing raw attribute values (and not aggregated
	attributes as they are already normalized (in generate_leaders_data.py)) into a 0–100 scale during
	caching of display data.

	Globals Modified:
	- AI_VALUE_RANGES (dict): Maps attribute name -> (min, max) tuple.

	Assumptions:
	- Raw attributes and aggregated attributes data is located in PARSED_XML_LEADERS_DATA.
	- Only integer fields are considered (non-integer fields are ignored).
	- Leaders listed in EXCLUDED_LEADERS_FROM_LEADERS_DATA are skipped.

	Warnings:
	- Attributes that do not vary (constant value across leaders) still have
	  their (min, max) stored, resulting in (x, x).
	"""
	global AI_VALUE_RANGES
	AI_VALUE_RANGES.clear()
	values_by_attr = {}
	for leader_key, leader_data in PARSED_XML_LEADERS_DATA.items():
		if leader_key in EXCLUDED_LEADERS_FROM_LEADERS_DATA:
			continue
		for attr, val in leader_data.items():
			if isinstance(val, int):
				if not values_by_attr.has_key(attr):
					values_by_attr[attr] = []
				values_by_attr[attr].append(val)
	for attr in values_by_attr.keys():
		vals = values_by_attr[attr]
		if vals:
			AI_VALUE_RANGES[attr] = (min(vals), max(vals))

def do_sanity_checks_after_ai_value_ranges_caching():
	# <!-- custom: A few sanity checks -->
	tests_ai_value_ranges_min_max = (
		("LEADER_GANDHI", "iDiplomacyVictoryWeight"),
		("LEADER_MOCTEZUMA", "iMaxWarRand"),
		("LEADER_NAPOLEON", "iNoWarAttitudeProbFurious"),
		("LEADER_SITTING_BULL", "iNoWarAttitudeProbCautious"),
		("LEADER_GANDHI", "iNoWarAttitudeProbPleased"),
		("LEADER_WILLEM_VAN_ORANJE", "iFlavorMilitary"),
		# <!-- custom: note: these (negative and positive memory aggregated attributes (affection and resentment for each, as well as contact probs and/or such other similar attributes) are technically aggregates (aggregates are an old feature, deprecated now) but behave and are stored in our data as if they are (raw ai attributes), so they can be analyzed at such and even before ai aggregates are calculated if i am not mistaken i think anyways -->
		("LEADER_ELIZABETH", "iContactJoinWarDelayRaw"),
		("LEADER_ELIZABETH", "iContactJoinWarRandRaw"),
		("LEADER_ELIZABETH", "iAggregatedContactJoinWarProb"),
		("LEADER_PETER", "iPositiveMemoryAttitudeTradedTechToUsRaw"),
		("LEADER_PETER", "iPositiveMemoryDecayTradedTechToUsRaw"),
		("LEADER_PETER", "iAggregatedPositiveMemoryTradedTechToUsAffection"),
		("LEADER_PETER", "iAggregatedPositiveMemoryTradedTechToUsResentment"),
		("LEADER_TOKUGAWA", "iNegativeMemoryAttitudeRefusedHelpRaw"),
		("LEADER_TOKUGAWA", "iNegativeMemoryDecayRefusedHelpRaw"),
		("LEADER_TOKUGAWA", "iAggregatedNegativeMemoryRefusedHelpResentment"),
		("LEADER_TOKUGAWA", "iAggregatedNegativeMemoryRefusedHelpAffection"),
    )
	for leader_key, attr in tests_ai_value_ranges_min_max:
		min_val_found = AI_VALUE_RANGES[attr][0]
		max_val_found = AI_VALUE_RANGES[attr][1]
		curr_val_to_test = PARSED_XML_LEADERS_DATA[leader_key][attr]

		if (curr_val_to_test < min_val_found) or (curr_val_to_test > max_val_found):
			raise ValueError(u"[FATAL] At AI_VALUE_RANGES post-processing('s) testing, in attr=%s and in leader_key=%s, curr_val_to_test=%d cannot be strictly out of bounds of min_val_found=%d and max_val_found=%d" % (attr, leader_key, curr_val_to_test, min_val_found, max_val_found))

# --- Cache per-leader attributes (with final (value, scale) tuples only ---
def cache_ai_attribute_data():
	"""
	Caches the normalized display-ready AI attribute values and symbolic scales for each leader.

	Normalizes all raw integer AI personality attributes (except aggregated attributes) to a 0–100
	scale using previously cached min/max values. Associates each attribute with a symbol scale
	(for visual representation, like "+" bars) based on its normalized value.

	For special "aggregated" attributes (already normalized externally), no re-normalization
	is performed; they are stored as-is but with a different symbol ("#").

	Exception to this symbol storing choice is if all leaders share the same value for an ai attirbute
	(whether it is a raw or aggregated ai attribute, the same following rule would apply), then in that
	case the symbol is like "=====" (and the normalized value (whether at caching step for raw ai attributes,
	or at generate_leaders_data.py step (that also uses the same normalize_to_100 function than here in the
	sevopedia leader but earlier, for aggregated ai attributes)) is 50 for both raw ai attributes and
	aggregated ai attributes)) 

	Globals Modified:
	- AI_ATTRIBUTE_DATA (dict): Maps leader name -> { attribute: (normalized_value, scale_string) }.

	Assumptions:
	- Raw leader data is stored in PARSED_XML_LEADERS_DATA.
	- Min/max ranges for attributes are already available in AI_VALUE_RANGES.
	- Inversion rules for attributes are defined in ATTRIBUTES_TO_INVERT.
	- Aggregated attributes are listed in AGGREGATED_ATTRIBUTES.

	Behavior:
	- Attributes with identical normalized values across all leaders are warned about
	  (optional sanity check).
	- Leaders listed in EXCLUDED_LEADERS_FROM_LEADERS_DATA are skipped.

	Warnings:
	- Raises KeyError if any required normalization data is missing.
	"""
	global AI_ATTRIBUTE_DATA
	AI_ATTRIBUTE_DATA.clear()

	for leader_key in sorted(PARSED_XML_LEADERS_DATA.keys()):
		if leader_key in EXCLUDED_LEADERS_FROM_LEADERS_DATA:
			continue

		leader_data = PARSED_XML_LEADERS_DATA[leader_key]
		leader_data_cached = {}

		# <!-- custom: not strictly necessary to have a sorted caching order, but helps/allows to have a nicely alphabetically ordered debug output to help debugging perhaps or/and for reuse(?) or/and copy/paste or/and other or(/and?) not anyways etc -->
		for attr in sorted(leader_data.keys()):
			raw_val = leader_data[attr]
			min_val = None
			max_val = None
			final_val = None
			symbol = None
			if isinstance(raw_val, int):
				# Check if attribute is aggregated (aggregated behavior)
				# --- Decide final stored value ---
				if is_attr_aggregated(attr):
					final_val = raw_val  # already normalized!
					symbol = ALL_SYMBOLS["AGGREGATED_SCALE_SYMBOL"]  # Use "#" as the default aggregated attributes symbol (unless equal or/and (some) other condition anyways)
					# <!-- custom: fetch min_val and max_val even though we don't need them since these are already normalized (not normalizing again), but to know if we should put and "=====" (or whichever symbol ALL_SYMBOLS["EQUAL_SCALE_SYMBOL"] is(!) (A)anyways) symbol or not at for the scale. Is also a good opportunity to check min and max perhaps and retest our values, anyways -->
					min_val, max_val = AI_VALUE_RANGES[attr]
					if (raw_val < min_val) or (raw_val > max_val):
						raise ValueError(u"[FATAL] At AI_ATTRIBUTE_DATA's stage, in aggregated ai attribute (no re-normalization here again) attr=%s and in leader_key=%s, raw_val=%d cannot be strictly out of bounds of min_val=%d and max_val=%d" % (attr, leader_key, raw_val, min_val, max_val))

				else:
					# Normalize (inversion applied if needed)
					# Min/max values (avoid double fetching)
					if attr not in AI_VALUE_RANGES:
						raise KeyError(u"Missing AI_VALUE_RANGES entry for attribute: %s" % attr)
					min_val, max_val = AI_VALUE_RANGES[attr]

					# Check if attribute needs inversion
					# <!-- custom: valid placeholder, not all attributes need to be inverted or are in the (to be) invert(ed) list(?) -->
					invert = False
					if (attr in ATTRIBUTES_TO_INVERT):
						invert = True

					if (raw_val < min_val) or (raw_val > max_val):
						raise ValueError(u"[FATAL] At AI_ATTRIBUTE_DATA's stage and before normalization, in (raw) attr=%s and in leader_key=%s, raw_val=%d cannot be strictly out of bounds of min_val=%d and max_val=%d" % (attr, leader_key, raw_val, min_val, max_val))

					norm_val = normalize_to_100(raw_val, min_val, max_val, invert, attr)
					final_val = norm_val
					symbol = ALL_SYMBOLS["RAW_ATTRIBUTE_SCALE_SYMBOL"]  # Use "+" for normal attributes

				# <!-- custom: quite clean way i found to get the "=====" scale if all leaders share same values, without nesting/cluttering the normalize function with uneccessary symbol scale logic, ideally should (or rather maybe ideally should return the info of if all values are equal, but it works fine this way in our code even tohugh a bit redundant as a result (but easier and quite clean overall maybe even though not ideal maybe fine in this case anyways etc) i think but anyways move this check a bit earlier and not normalize if all values are equal, and debug this, perhaps with a wrapper function on top of normalize that handles this, but maybe fine this way maybe at least not so bad or not etc anyways, also doing a sanity check at the same time (to/that also failproofs ((further?) more) our min_val an max_val common prerequirement of it not being both None for raw ai attributes as well as for aggregated ai attributes), anyways. -->
				if (min_val is None) or (max_val is None):
						raise ValueError(u"[FATAL] At AI_ATTRIBUTE_DATA's stage and after normalization, in (raw or aggregated) attr=%s and in leader_key=%s, min_val=%d or max_val=%d failed to initialize, cannot be None." % (min_val, max_val))
				if (min_val == max_val):
					symbol = ALL_SYMBOLS["EQUAL_SCALE_SYMBOL"]
				else:
					CvUtil.pyPrint("raw_val, min_val, max_val, final_val are: %d, %d, %d, %d, for attribute %s at leader_key %s" % (raw_val, min_val, max_val, final_val, attr, leader_key))

				if (symbol not in ALL_SYMBOLS.values()):
					raise ValueError(u"Unexpected symbol %s in attr %s and in leader_key %s.)" % (symbol, attr, leader_key))

				# Compute the appropriate scale
				scale = get_symbol_scale(final_val, symbol)

				# Store final (raw_val, final_val, scale) as tuple
				leader_data_cached[attr] = (raw_val, final_val, scale)

		# Store per-leader data
		AI_ATTRIBUTE_DATA[leader_key] = leader_data_cached

		# --- Compact Debug Output for AI_ATTRIBUTE_DATA and sanity check raises(ing) error if missing ---
		if leader_data_cached:
			line = "[DEBUG] Cached AI attribute data for leader_key %s: " % leader_key
			pairs = []
			for attr in sorted(leader_data_cached.keys()):
				raw_val, final_val, scale = leader_data_cached[attr]
				pairs.append("%s=(raw_val=%d, final_val=%d, \"%s\")" % (attr, raw_val, final_val, scale))
			line += "{ " + ", ".join(pairs) + " }"
			CvUtil.pyPrint(line)
		else:
			raise ValueError("[VALUE ERROR] No AI attribute data found for leader_key %s" % leader_key)

def check_excluded_leaders_from_leaders_data_are_excluded_from_ai_attribute_data():
	for excluded_leader_key in EXCLUDED_LEADERS_FROM_LEADERS_DATA:
		if (excluded_leader_key in AI_ATTRIBUTE_DATA.keys()):
			raise KeyError("[FATAL] During sanity checks testing, (excluded) leader_key=%s was assessed to not be properly excluded from the calculations and is part of the AI_ATTRIBUTE_DATA." % excluded_leader_key)

# <!-- custom: also check for missing (compatible ai attributes as compared to what is parsed in leaders_data.py to make sure we didn't miss any (attribute)) -->
def ensure_no_compatible_attrs_overlooked_from_leaders_data_in_ai_attribute_data_after_caching():
	# <!-- custom: testing for only one leader (any) after all are parsed should be enough, no need to test for all as they have the same structure if i am not mistaken anyways etc -->
	leader_key_for_test = "LEADER_CATHERINE"
	cached_ai_attribute_attrs = AI_ATTRIBUTE_DATA[leader_key_for_test].keys()
	test_leader_data = PARSED_XML_LEADERS_DATA[leader_key_for_test]

	for compatible_leaders_data_attr, val in test_leader_data.items():
		if isinstance(val, int):
			if compatible_leaders_data_attr not in cached_ai_attribute_attrs:
				raise KeyError("Missing attr: testing in leader_key_for_test=%s (for example) has shown a mismatch; compatible PARSED_XML_LEADERS_DATA attribute compatible_leaders_data_attr=%s is not part of the AI_ATTRIBUTE_DATA's attributes cached_ai_attribute_attrs=%s" % (leader_key_for_test, compatible_leaders_data_attr, str(cached_ai_attribute_attrs)))



# --- Execute all testing and caching steps ---
# <!-- custom: sanity checks (before using the data etc) -->
check_icons_as_buttons_paths_are_valid()
do_data_sets_attr_validation_pre_caching()

cache_ai_value_ranges()
do_sanity_checks_after_ai_value_ranges_caching()

test_expected_shifting_pre_normalize_to_100()
cache_ai_attribute_data()
# <!-- custom: make sure our just/newly stored values in AI_ATTRIBUTE_DATA are reliable at least quite a bit maybe anyways etc anyways etc -->
check_excluded_leaders_from_leaders_data_are_excluded_from_ai_attribute_data()
ensure_no_compatible_attrs_overlooked_from_leaders_data_in_ai_attribute_data_after_caching()



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
		# (data extracted from my notes_about_art_design.txt file in this mod, please look at it or the filename
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
		# 1) (most) absolute dimensions first -->

		# <!-- custom: make room to add AI personality panel -->
		self.W_AI_PERSONALITY = 290

		self.SMALL_MARGIN = 10
		self.MEDIUM_MARGIN = 20
		# <!-- custom: we also need this information sooner, move it here with the more absolute
		# dimensions of some elements
		self.W_CIV = 64
		self.H_CIV = 64
		self.CIV_MARGIN = 0
		self.CIV_DISELEVATION = 38
		
		self.H_FAVORITES = 110
		self.N_AI_TABLE_NUM = 3

		# <!-- custom:
		# 2) (most) relative dimensions or/and positions then -->

		self.W_LEADERHEAD = self.W_LEADERHEAD_PANE - 30
		self.H_LEADERHEAD = self.H_LEADERHEAD_PANE - 34
		self.X_LEADERHEAD = self.X_LEADERHEAD_PANE + (self.W_LEADERHEAD_PANE - self.W_LEADERHEAD) / 2
		self.Y_LEADERHEAD = self.Y_LEADERHEAD_PANE + (self.H_LEADERHEAD_PANE - self.H_LEADERHEAD) / 2 + 3

		self.W_AI_TOTAL_TABLES_WIDTH = self.N_AI_TABLE_NUM * self.W_AI_PERSONALITY + self.N_AI_TABLE_NUM * self.MEDIUM_MARGIN

		self.Y_FAVORITES = self.Y_LEADERHEAD_PANE + self.H_LEADERHEAD_PANE + self.SMALL_MARGIN

		# <!-- custom: we need self.W_HISTORY before the favourites coordinates, (even though the history
		# panel is placed under/after the favourites panel when i constructed the page's "spacing" and
		# dimensions of (and between) panels, anyways) because/as the favourites panel uses/needs/is based on
		# the history panel's (relative) position, anyways -->
		# <!-- custom: might as well put the other/rest/remaining HISTORY coordinates if doesn't harm and they
		# are perhaps needed too, anyways -->
		self.X_HISTORY = self.X_LEADERHEAD_PANE
		self.Y_HISTORY = self.Y_FAVORITES + self.H_FAVORITES + self.SMALL_MARGIN
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.W_AI_TOTAL_TABLES_WIDTH - self.X_LEADERHEAD_PANE
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY

		self.X_FAVORITES = self.X_LEADERHEAD_PANE
		self.W_FAVORITES = self.W_HISTORY - self.W_CIV - self.SMALL_MARGIN

		# <!-- custom: the rest of the data here, as it is dependent on other data we need first
		# that (i.e. before being able to add these) -->
		self.X_AI_PERSONALITY = self.top.R_PEDIA_PAGE - self.W_AI_PERSONALITY 
		self.Y_AI_PERSONALITY = self.Y_LEADERHEAD_PANE
		self.H_AI_PERSONALITY = self.H_LEADERHEAD_PANE + self.SMALL_MARGIN + self.H_FAVORITES + self.SMALL_MARGIN + self.H_HISTORY

		# <!-- custom: AI Personality Panel(s) column widths -->
		self.W_AI_VALUE = 35
		self.W_AI_SCALE = 100
		self.W_AI_LABEL = self.W_AI_PERSONALITY - self.W_AI_VALUE - self.W_AI_SCALE
		self.H_AI_LINE_HEIGHT = 22
		self.H_AI_CATEGORY_SPACING = 10
		self.W_AI_LEFT_SIDE_PADDING = 12
		# <!-- custom: removing or rather having an empty header, the header disappears entirely,
		# but if you want to use a header, you can just type any value in the related txt keys
		# such as TXT_KEY_AI_PERSONALITY_RIGHT_PANEL and such anyways. This or maybe rather not
		# doing this (having an non-empty txt key header) would take some room though so you'd
		# have to adjust self.H_AI_UPPER_PADDING to the value below commented-out or simialr depending
		# the upper padding you want.
		# Since i (accidentally found) it frees more room, i want to try using it as such, as i really
		# need the extra room, and not so much the header name (the other two header txt keys were going
		# to be either redunant naming or empty so maybe this is (also) a good opportunity to gain space/room
		# in the ai personality panel, anyways -->
		#self.H_AI_UPPER_PADDING = 36
		self.H_AI_UPPER_PADDING = 15

		self.AI_PANEL_RIGHT_TXT_KEY = "TXT_KEY_AI_PERSONALITY_RIGHT_PANEL"
		self.AI_PANEL_MIDDLE_TXT_KEY = "TXT_KEY_AI_PERSONALITY_MIDDLE_PANEL"
		self.AI_PANEL_LEFT_TXT_KEY = "TXT_KEY_AI_PERSONALITY_LEFT_PANEL"

		# <!-- custom: traits have the green color somehow,
		#
		# (i (should/would) (maybe)) do not comment-out until i find how so i
		#
		# can feed it / = ask ChatGPT about it if it has ideas -->
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



	def interfaceScreen(self, iLeader):
		self.iLeader = iLeader

		# <!-- custom: change call order to match filling/building order, generally
		# from top left to bottom and left to right but not always, reordering in
		# such a way is maybe a bit more intuitive this way perhaps or/and clearer
		# or/and helpful or not or other etc anyways, -->
		self.placeLeaderHeadPane()
		self.placeFavorites()
		self.placeHistory()
		self.placeCiv()
		self.placeTraits()
		# We need to use the proper tag name (e.g., "LEADER_HATSHEPSUT") instead of
		# iLeader when looking up the cache.
		iLeaderKey = gc.getLeaderHeadInfo(iLeader).getType()
		# <!-- custom: for excluded leaders from leaders_data, leave the zone/space where the AI
		# personality panel was supposed to be especially empty, instead of getting a key error
		# or missing leader from leaders_data (but we still want the excluded leaders to be
		# excluded from computation as it could and most likely will most often if not always affect
		# the ranking and scores normalized of other leaders with this additional data (unless they
		# somehow are all still equal or something similar, but is not too likely, anyways etc
		# anyways etc))
		# This is especially useful for LEADER_BARBARIAN in particular that is somehow accessible
		# in the sevopedia civilization category from the barbarian civ i mean anyways (which is
		# also useful because we now display their city names for example, see sevopedia civilization
		# for details about how we place city names in it now)
		# -->
		if (iLeaderKey not in EXCLUDED_LEADERS_FROM_LEADERS_DATA):
			self.placeAIPersonalityPanel(iLeaderKey)
		else:
			CvUtil.pyPrint("[DEBUG] Leader iLeaderKey=%s in EXCLUDED_LEADERS_FROM_LEADERS_DATA=%s is skipped, leave the place where AI Personality panel was supposed to be entirely empty so we don't get a missing key in leaders_data Error, while signifying clearly enough hopefully that the excluded leader currently selected doesn't have a leader_data and AI Personality Panel at all/is not part of it." % (iLeaderKey, str(EXCLUDED_LEADERS_FROM_LEADERS_DATA)))



	# <!-- custom: wrap leader placement in a specific function for clarity
	# or/and flexibility or not anyways,
	# -->
	def placeLeaderHeadPane(self):
		screen = self.top.getScreen()
		leaderPanelWidget = self.top.getNextWidgetName()
		screen.addPanel(leaderPanelWidget, "", "", True, True, self.X_LEADERHEAD_PANE, self.Y_LEADERHEAD_PANE, self.W_LEADERHEAD_PANE, self.H_LEADERHEAD_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		self.leaderWidget = self.top.getNextWidgetName()
		screen.addLeaderheadGFC(self.leaderWidget, self.iLeader, AttitudeTypes.ATTITUDE_PLEASED, self.X_LEADERHEAD, self.Y_LEADERHEAD, self.W_LEADERHEAD, self.H_LEADERHEAD, WidgetTypes.WIDGET_GENERAL, -1, -1)



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



	# --- Place AI Personality Panel (using precomputed scales) ---
	def placeAIPersonalityPanel(self, iLeaderKey):
		"""
		Renders the full AI Personality panel in the Sevopedia Leader page using
		precomputed and normalized AI data for the given leader.

		Displays all raw AI attributes and derived aggregates in a structured,
		three-column layout. The panel consists of three vertical sections
		(right, middle, left), each containing grouped categories of AI personality data.
		Every attribute is shown with its label, numeric value, and symbolic scale (e.g., "+++").

		Each data row is derived directly from `AI_ATTRIBUTE_DATA`: Raw XML attribute values normalized to 0–100 and converted to scale.

		Panel setup:
		- Right: For example it could be Religion-related modifiers (see actual categories in AI_PANEL_RIGHT_CATEGORIES).
		- Middle: For example it could be Core traits, Flavors, Victory weights, War strategies (see actual categories in AI_PANEL_MIDDLE_CATEGORIES).
		- Left: For example it could be Economic traits, refusal thresholds, diplomacy contact chances, modifiers (see actual categories in AI_PANEL_LEFT_CATEGORIES).

		Design Principles:
		- **Strictly no placeholders**: All data accesses are direct and unconditional.
		Missing or misconfigured data will raise exceptions by design, ensuring
		bugs or omissions surface immediately.
		- Attributes that represent contact probabilities (e.g., iContactXxxProb) display
		contextual (delay/rand) info as part of the label (e.g., "Contact (3/50)").

		Assumptions:
		- `AI_ATTRIBUTE_DATA` must be fully precomputed before rendering.
		- `DISPLAYED_AI_ATTRIBUTE_CATEGORIES` must include all expected category keys and mappings.
		- No leader data may be missing. All required fields must exist in the cache.

		Globals Used (read-only):
		- AI_ATTRIBUTE_DATA (dict): Maps leader -> { attr -> (raw_val, norm_val, scale) }
		- DISPLAYED_AI_ATTRIBUTE_CATEGORIES (dict): Category -> [(label, attr, core_name)]
		- AGGREGATED_CONTACT_PROBABILITY_ATTRIBUTES (set): Attributes using delay/rand contextual labels.

		Exceptions:
		- Raises `KeyError` if any attribute, category, or leader data is missing.
		- Intended to fail fast if cache generation was incomplete or misconfigured.

		Typical Use:
		- Called automatically when opening the Sevopedia Leader page.
		- Should follow a successful call to all cache functions:
		`cache_ai_value_ranges()`, `cache_ai_attribute_data()`.
		"""
		screen = self.top.getScreen()

		def getXPanelCoordinate(tableId):
			return self.X_AI_PERSONALITY - tableId * self.W_AI_PERSONALITY - tableId * self.MEDIUM_MARGIN

		# === Layout constants ===
		xPanelRight = getXPanelCoordinate(self.N_AI_TABLE_NUM - 3)
		xPanelMiddle = getXPanelCoordinate(self.N_AI_TABLE_NUM - 2)
		xPanelLeft = getXPanelCoordinate(self.N_AI_TABLE_NUM - 1)

		def setupPanel(screen, txtKey, xPanel):
			panelName = self.top.getNextWidgetName()
			screen.addPanel(
				panelName,
				localText.getText(txtKey, ()),
				"",
				True,
				True,
				xPanel,
				self.Y_AI_PERSONALITY,
				self.W_AI_PERSONALITY,
				self.H_AI_PERSONALITY,
				PanelStyles.PANEL_STYLE_BLUE50,
			)

		# === PANEL SETUP ===
		setupPanel(screen, self.AI_PANEL_RIGHT_TXT_KEY, xPanelRight)
		setupPanel(screen, self.AI_PANEL_MIDDLE_TXT_KEY, xPanelMiddle)
		setupPanel(screen, self.AI_PANEL_LEFT_TXT_KEY, xPanelLeft)

		def fillTableRow(screen, label, value, scale, xLabel, xValue, xScale, y):
			labelText = u"<font=2>%s</font>" % label
			valueText = u"<font=2b>%d</font>" % value
			scaleText = u"<font=2>%s</font>" % scale

			screen.setText(self.top.getNextWidgetName(), "", labelText,
				CvUtil.FONT_LEFT_JUSTIFY, xLabel, y, 0, FontTypes.SMALL_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setText(self.top.getNextWidgetName(), "", valueText,
				CvUtil.FONT_LEFT_JUSTIFY, xValue, y, 0, FontTypes.SMALL_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setText(self.top.getNextWidgetName(), "", scaleText,
				CvUtil.FONT_LEFT_JUSTIFY, xScale, y, 0, FontTypes.SMALL_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)

		# === Render Function ===
		def renderCategories(screen, categories, xPanel, yPanel):
			xLabel = xPanel + self.W_AI_LEFT_SIDE_PADDING
			xValue = xLabel + self.W_AI_LABEL
			xScale = xValue + self.W_AI_VALUE
			y = yPanel + self.H_AI_UPPER_PADDING

			first = True
			for category in categories:
				if not first:
					y += self.H_AI_CATEGORY_SPACING
				else:
					first = False

				# --- Category Header ---
				# Add button <!-- custom: to/in category header anyways etc -->
				buttonPath = str(CyTranslator().getText(DISPLAYED_AI_ATTRIBUTE_CATEGORY_BUTTON_PATH_TXT_KEYS[category], ()))
				buttonSize = 16
				szButtonText = u"<img=%s size=%s></img>" % (buttonPath, str(buttonSize))
				szText2 = u"%s <font=3b>%s</font>" % (szButtonText, category)
				# <!-- custom: add x offset (negative) so we can push button to the left a bit further than where the sub/child (but anyways etc) items/lines of the category start anyways etc -->
				xOffsetButton = xLabel - 7

				screen.setText(self.top.getNextWidgetName(), "", szText2, CvUtil.FONT_LEFT_JUSTIFY, xOffsetButton, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				y += self.H_AI_LINE_HEIGHT

				# --- Display Raw and Aggregated AI Attributes ---
				for label, attr, core_name in DISPLAYED_AI_ATTRIBUTE_CATEGORIES[category]:
					# --- Contact Probabilities ---
					if attr in AGGREGATED_ALL_CONTACT_PROBABILITY_ATTRIBUTES:
						delay_field = "iContact%sDelayRaw" % core_name
						rand_field = "iContact%sRandRaw" % core_name
						delay_data = AI_ATTRIBUTE_DATA[iLeaderKey][delay_field]
						rand_data = AI_ATTRIBUTE_DATA[iLeaderKey][rand_field]
						delay_value = delay_data[0]
						rand_value  = rand_data[0]

						raw_val, norm_val, scale = AI_ATTRIBUTE_DATA[iLeaderKey][attr]
						label = u"%s (%d/%d)" % (label, delay_value, rand_value)
					
					# --- Positive Memory Affection/Resentment ---
					elif attr in AGGREGATED_POSITIVE_MEMORY_AFFECTION_AND_RESENTMENT_ATTRIBUTES:
						att_field = "iPositiveMemoryAttitude%sRaw" % core_name
						dec_field = "iPositiveMemoryDecay%sRaw" % core_name
						att_value = AI_ATTRIBUTE_DATA[iLeaderKey][att_field][0]
						dec_value = AI_ATTRIBUTE_DATA[iLeaderKey][dec_field][0]
						raw_val, norm_val, scale = AI_ATTRIBUTE_DATA[iLeaderKey][attr]
						label = u"%s (+%d/%d)" % (label, att_value, dec_value)

					# --- Negative Memory Affection/Resentment ---
					elif attr in AGGREGATED_NEGATIVE_MEMORY_RESENTMENT_AND_AFFECTION_ATTRIBUTES:
						att_field = "iNegativeMemoryAttitude%sRaw" % core_name
						dec_field = "iNegativeMemoryDecay%sRaw" % core_name
						att_value = AI_ATTRIBUTE_DATA[iLeaderKey][att_field][0]
						dec_value = AI_ATTRIBUTE_DATA[iLeaderKey][dec_field][0]
						raw_val, norm_val, scale = AI_ATTRIBUTE_DATA[iLeaderKey][attr]
						label = u"%s (%d/%d)" % (label, att_value, dec_value)

					else:
						raw_val, norm_val, scale = AI_ATTRIBUTE_DATA[iLeaderKey][attr]
						label = u"%s (%d)" % (label, raw_val)

					fillTableRow(screen, label, norm_val, scale, xLabel, xValue, xScale, y)
					y += self.H_AI_LINE_HEIGHT

		# Render Panels
		renderCategories(screen, AI_PANEL_RIGHT_CATEGORIES, xPanelRight, self.Y_AI_PERSONALITY)
		renderCategories(screen, AI_PANEL_MIDDLE_CATEGORIES, xPanelMiddle, self.Y_AI_PERSONALITY)
		renderCategories(screen, AI_PANEL_LEFT_CATEGORIES, xPanelLeft, self.Y_AI_PERSONALITY)



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

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
# AI Utilities or Personality Panel for normalization and general helpers for the SevopediaLeader category
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# Store in LEADERS_INFO_CACHED tuples of (label (with raw value display in the label too so no need to fetch it later again at UI just to display it in label, faster performance this way, also from using tuples or such rather than dicts), normalized value for display, and scale precomputed to enhance performance as well)
# Categories precomputing as well as tuples: the ai_category_header that handles also emoji buttons in header label too optionally displayed if config flag is set to True, including also in the ai_category tuple the x_offset for each category (a bit redundant but so we don't need to check it again, could optimize it further but also allows for more customization later if needed maybe, this x_offset is to accomodate these emoji buttons as text if needed; and then also packing all categories with an inter category order within their main "categories" tuple (as of now right, middle, left, since we have 3 tables in the AI personality panel feature)
# UI: nothing remains only displaying it, nothing left to compute, a bit of tuple direct unpacking without any check, so display is very fast despite the quite big data.
#
# <!-- custom: note: some code comments may be outdated as they were written when we would compute once per civ4 game launch the LEADERS_INFO_CACHED for efficiency, however since then we as of now now switched to no compute at all (use precomputed SevoPediaLeaderCachePredumped.py) (see also toggle define as of now at [`GlobalDefines_advciv_sas.xml`](/Assets/XML/GlobalDefines_advciv_sas.xml))) as it is even cheaper and should scale better with mods that have more leaders or xml attributes (if i'm not mistaken). Plus the values rarely change and are only for UI so not worth spending so much on them even if was more efficient. -->
# <!-- custom: now refactored with the help of chatgpt 5.2 (web) and GPT-5.2-Codex thanks a lot. -->



# -*- coding: utf-8 -*-
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
# <!-- custom: import to display chars before Traits -->
import TraitUtil

from ai_utils_shared_with_civ4 import *
from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



IS_DISPLAY_AI_CATEGORY_HEADER_EMOJI_BUTTONS = (gc.getDefineINT("SAS_SEVOPEDIA_LEADER_AI_PERSONALITY_PANEL_SHOW_EMOJI") > 0)
IS_DISPLAY_AI_CATEGORY_HEADERS = True
IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD = (gc.getDefineINT("SAS_SEVOPEDIA_LEADER_AI_PERSONALITY_PANEL_SHOW_RAW_XML_FIELD_NAMES_INSTEAD") > 0)
IS_SHOW_TRAIT_ICONS_IN_LEADER = (gc.getDefineINT("SAS_SEVOPEDIA_LEADER_TRAITS_SHOW_ICONS") > 0)

# <!-- custom: increase hard drive life span by 0.1% by disabling this / setting it to False, maybe (disclaimer: i am not responsible is just i mean about the actual real percentage meant as a joke / comedy thingbut is maybe also true that disabling debug may avoid reducing hard drive life span even if a bit, as we write quite a lot of debug at each sevopedia load, however it is not guaranteed and i am not responsible, so do as you see fit use at your own risk code is there if you want to know what it does with also a debug sample (non-exhaustive but hopefully quite plenty) in SevopediaLead_derExamplesOfOutputs as of now if filename is still relevant later after writing this code comment, is just harmless text writing but writing a lot may hurt ssd or whichever hard drive especially most importantly by repeated use over a long time period of playing civ4 restarting game many times and such you use so i disabled it for my need now that system seems to work fine, available there if needed, for my own hard drive too. -->
IS_DEBUG_LEADER = False

# <!-- custom: we already warn once if min == max at/in get_leader_info_minimums_and_maximums, no need to warn again and again i mean at each normalization, so set B_WARN to false -->
B_WARN = False

if IS_DEBUG_LEADER:
	print("[DEBUG] Leaders index to type is: %s" % str(get_leaders_index_to_type_map(gc)))

# <!-- custom: note: LEADER_DEFAULTS doesn't seem to exist at all in the DLL, so no need to mention it here (also may cause errors in our code as we can't even refer to its index to exclude it to begin with since such a leader index doesn't seem to exist at all in gc/DLL so handle that edge case of LEADER_DEFAULTS specifically) unlike in generate_leaders_data.py for external to civ4 script usage, as for civ4 use only mention LEADER_BARBARIAN and similar existing leaders even if they are excluded, but not LEADER_DEFAULTS and any other DLL seemingly removed leader index as well if any other exist (as of now LEADER_DEFAULTS seems to be the only one but is to be exhaustive -->
EXCLUDED_LEADER_TYPES_FROM_CALCULATIONS = (
	"LEADER_BARBARIAN",
)
EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS = get_leader_indexes_from_leader_types(EXCLUDED_LEADER_TYPES_FROM_CALCULATIONS, gc)

# <!-- custom: more consistently and reliably exclude leaders by having a ready list of such leaders we can call -->
if IS_DEBUG_LEADER:
	print("[DEBUG] EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS=%s" % str(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS))



# Simple system to dump leader AI personality cache to PythonDbg.log, then optionally load it from a pre-generated .py module instead of computing at runtime.
#
# USAGE:
# ------
# 1. Set IS_USE_PREDUMPED_CACHE = False (default)
# 2. Play the game, open Sevopedia → Leaders category
# 3. In PythonDbg.log, find the block between:
#       # === SAS_LEADER_AI_CACHE_PYMODULE_BEGIN ===
#       ...
#       # === SAS_LEADER_AI_CACHE_PYMODULE_END ===
# 4. Copy that block into a new file: SevoPediaLeaderCachePredumped.py
# 5. Place that file in your mod's Python folder
# 6. Set IS_USE_PREDUMPED_CACHE to True (via XML SAS defines)
# 7. Now the game loads the pre-dumped data instead of computing it
#
# NOTES:
# ------
# - If you change emoji settings or leader XML, you need to re-dump
# - The dumped data includes: LEADERS_INFO_CACHED, AI_RIGHT_CATEGORIES, AI_MIDDLE_CATEGORIES, AI_LEFT_CATEGORIES
# === Cache dump/load config and helpers ===
IS_USE_PREDUMPED_CACHE = (gc.getDefineINT("SAS_SEVOPEDIA_LEADER_CACHE_USE_PREDUMPED") > 0)
IS_DUMP_CACHE_TO_LOG = (gc.getDefineINT("SAS_SEVOPEDIA_LEADER_CACHE_DUMP_TO_LOG") > 0)
# Name of the pre-dumped module (without .py extension)
PREDUMPED_MODULE_NAME = "SevoPediaLeaderCachePredumped"



def dump_leader_cache_to_pythondbg(leader_cache, excluded_leader_types, is_emoji_enabled, is_raw_xml_names):
	# Dumps the leader cache to PythonDbg.log in a format that can be copy-pasted into a .py module file.

	leaders_info_cached, ai_right_categories, ai_middle_categories, ai_left_categories = leader_cache

	# BEGIN marker
	print("# === SAS_LEADER_AI_CACHE_PYMODULE_BEGIN ===")
	print("")

	# Header with generation info
	print("# Generated from in-game dump to PythonDbg.log")
	print("# Copy this entire block (from BEGIN to END) into: %s.py" % PREDUMPED_MODULE_NAME)
	print("#")
	print("# Generation info:")
	print("#   - Number of leaders (gc.getNumLeaderHeadInfos): %d" % gc.getNumLeaderHeadInfos())
	print("#   - Excluded leader types: %r" % (excluded_leader_types,))
	print("#   - Emoji headers enabled: %s" % str(is_emoji_enabled))
	print("#   - Raw XML field names: %s" % str(is_raw_xml_names))
	print("")

	# The actual data
	print("LEADERS_INFO_CACHED = %r" % (leaders_info_cached,))
	print("")
	print("AI_RIGHT_CATEGORIES = %r" % (ai_right_categories,))
	print("")
	print("AI_MIDDLE_CATEGORIES = %r" % (ai_middle_categories,))
	print("")
	print("AI_LEFT_CATEGORIES = %r" % (ai_left_categories,))

	# END marker
	print("")
	print("# === SAS_LEADER_AI_CACHE_PYMODULE_END ===")

	print("AI Personality Panel cache dumped to PythonDbg.log successfully.")



def try_load_predumped_cache():
	# Attempts to load the pre-dumped cache module.
	if not IS_USE_PREDUMPED_CACHE:
		return None

	try:
		# Dynamic import of the pre-dumped module
		predumped = __import__(PREDUMPED_MODULE_NAME)
		
		leaders_info_cached = predumped.LEADERS_INFO_CACHED
		ai_right_categories = predumped.AI_RIGHT_CATEGORIES
		ai_middle_categories = predumped.AI_MIDDLE_CATEGORIES
		ai_left_categories = predumped.AI_LEFT_CATEGORIES
		
		print("AI Personality Panel cache Loaded pre-dumped cache from %s.py" % PREDUMPED_MODULE_NAME)
		return (leaders_info_cached, ai_right_categories, ai_middle_categories, ai_left_categories)
	
	except:
		raise ImportError("AI Personality Panel cache IMPORT ERROR: IS_USE_PREDUMPED_CACHE=True but %s.py not found. Please provide a valid precomputed file, or disable SAS_SEVOPEDIA_LEADER_CACHE_USE_PREDUMPED in XML SAS defines (GlobalDefines_advciv_sas.xml)." % PREDUMPED_MODULE_NAME)



def get_leader_cache_predumped_or_compute(compute_func, excluded_leader_types, is_emoji_enabled, is_raw_xml_names):
	# Main entry point. Either loads pre-dumped cache or computes it.
	# Always dumps to log when computing (so you can grab it later).

	# Try loading pre-dumped first
	predumped = try_load_predumped_cache()
	if predumped is not None:
		return predumped
	
	# Compute at runtime
	print("AI Personality Panel cache Computing leader cache at runtime...")
	leader_cache = compute_func()
	
	# Dump to log only if enabled via define
	if IS_DUMP_CACHE_TO_LOG:
		dump_leader_cache_to_pythondbg(leader_cache, excluded_leader_types, is_emoji_enabled, is_raw_xml_names)
	
	return leader_cache



# <!-- custom: note: collapse this below function with the VS Code UI option or similar to see the line after function definition directly (i.e. as of now around line 1530, right after function definition line e.g. around line 100) for easier reading if desired. -->
# <!-- custom: read at end of this function at the return's code comment of when and why we call the sevopedia cache precomputing as a function from sevopedia main -->
def _compute_leader_cache_internal():
	# <!-- custom: performance optimization as recommended by chatgpt 5 thanks which i adjusted or not (renaming or such) -->
	# Build once <!-- custom: at this function's scope as we don't need it outside of it but need it many times here -->
	NUM_LEADERS = gc.getNumLeaderHeadInfos()
	NON_EXCLUDED_LEADERS = tuple(i for i in xrange(NUM_LEADERS) if i not in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS)



	def check_required_newly_exposed_python_getters_gc_leader_exist(required_getters):
		# <!-- custom: verify all getters used by the leader display config are exposed in the DLL. (GPT-5.2-Codex) -->
		if not required_getters:
			return

		for iLeader in NON_EXCLUDED_LEADERS:
			missing = []
			leader_info = gc.getLeaderHeadInfo(iLeader)
			for getter in required_getters:
				if not hasattr(leader_info, getter):
					missing.append(getter)

			if missing:
				raise RuntimeError(u"[FATAL] Your mod DLL does not expose the following required Python getters:\n%s\n\nMissing for example from iLeader=%d. Please expose them in .cpp files and build the DLL again (or adjust the leader field list if your mod removes or renames these getters)." % (", ".join(missing), iLeader))
			
			# success: only check first real leader
			if IS_DEBUG_LEADER:
				print("[DEBUG] Getter check passed for iLeader=%d. All required Python getters are present." % iLeader)
			break  # ?. success: no need to check further



	# <!-- custom: modified from claude ai's code sample, see sevopedia helpers py also for details; note: NUM_MEMORY_TYPES_ASSESSED are not here in sevopedia leader since we use a different looping emthod as in methodology, see positive_or_negative_memory_indexes and its related code comments -->
	NUM_CONTACT_TYPES_ASSESSED = 14
	NUM_ATTITUDE_TYPES_ASSESSED = 5



	# <!-- custom: make sure our normalize function behaves-works-functions as intended before we use it. -->
	test_expected_shifting_pre_normalize_to_100()

	if IS_DEBUG_LEADER:
		print("[DEBUG] test_expected_shifting_pre_normalize_to_100 passed.")


	def computeAndStoreMinMaxOfOneKey(key, value, leader_info_minimums, leader_info_maximums):
		if key not in leader_info_minimums:
			leader_info_minimums[key] = value
			leader_info_maximums[key] = value
			if IS_DEBUG_LEADER:
				print("[DEBUG] Set initial min/max for key=%s → %d" % (key, value))
		else:
			prev_min = leader_info_minimums[key]
			prev_max = leader_info_maximums[key]

			if value < prev_min:
				leader_info_minimums[key] = value
				if IS_DEBUG_LEADER:
					print("[DEBUG] New min for %s: %d → %d" % (key, prev_min, value))

			if value > prev_max:
				leader_info_maximums[key] = value
				if IS_DEBUG_LEADER:
					print("[DEBUG] New max for %s: %d → %d" % (key, prev_max, value))



	# <!-- custom: store raw aggregated contact probs (iAggregatedRaw...) separately from normalized aggregated probs (iAggregated...).
	# Only the normalized values are displayed; raw values are kept for later normalization/min-max. The raw-to-normalized parsing
	# and label composition happens later in compute_and_store_leaders_info_cached. Do the same for raw aggregated positive/negative
	# memory affections/resentments. (GPT-5.2-Codex (summarized)) -->
	leaders_info_aggregated_raw_contact_probs = {}
	leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments = {}



	def compute_and_store_leaders_info_aggregated_raw_contact_probs(leaders_info_aggregated_raw_contact_probs):
		# leaders_info_aggregated_raw_contact_probs[iLeader][parsed_contact_key] = aggregated_raw_score
		# parsed_contact_key is e.g. "iAggregatedRawContactProbStopTrading" (0-100)
		#
		# We compute these in two passes:
		# - Pass 1: adjusted rand/delay values + min/max per contact type
		# - Pass 2: normalize adjusted values to 0-100, then combine into an aggregated raw score

		# Precompute per-contact metadata once.
		contact_types = [gc.getContactTypes(i) for i in xrange(NUM_CONTACT_TYPES_ASSESSED)]
		contact_suffixes = [get_pascal_case_suffix(contact_type) for contact_type in contact_types]
		parsed_adjusted_rand_names = ["iAdjustedContactRand%s" % suffix for suffix in contact_suffixes]
		parsed_adjusted_delay_names = ["iAdjustedContactDelay%s" % suffix for suffix in contact_suffixes]
		parsed_aggregated_raw_names = ["iAggregatedRawContactProb%s" % suffix for suffix in contact_suffixes]

		# Pass 1: compute adjusted values and collect min/max across leaders.
		# temp_by_leader[iLeader][i] = (adjusted_rand, adjusted_delay, b_force_zero)
		temp_by_leader = {}
		min_adj_rand = [None] * NUM_CONTACT_TYPES_ASSESSED
		max_adj_rand = [None] * NUM_CONTACT_TYPES_ASSESSED
		min_adj_delay = [None] * NUM_CONTACT_TYPES_ASSESSED
		max_adj_delay = [None] * NUM_CONTACT_TYPES_ASSESSED

		for iLeader in NON_EXCLUDED_LEADERS:
			loopLeaderHeadInfo = gc.getLeaderHeadInfo(iLeader)
			leader_rows = [None] * NUM_CONTACT_TYPES_ASSESSED

			for i in xrange(NUM_CONTACT_TYPES_ASSESSED):
				value_1_rand_raw = loopLeaderHeadInfo.getContactRand(i)
				value_1_delay_raw = loopLeaderHeadInfo.getContactDelay(i)

				adjusted_rand, adjusted_delay, b_force_zero = get_adjusted_contact_values(
					value_1_rand_raw,
					value_1_delay_raw,
					IS_DEBUG_LEADER,
					contact_types[i]
				)

				leader_rows[i] = (adjusted_rand, adjusted_delay, b_force_zero)

				# Min/max init
				if min_adj_rand[i] is None:
					min_adj_rand[i] = adjusted_rand
					max_adj_rand[i] = adjusted_rand
					min_adj_delay[i] = adjusted_delay
					max_adj_delay[i] = adjusted_delay
				else:
					if adjusted_rand < min_adj_rand[i]:
						min_adj_rand[i] = adjusted_rand
					if adjusted_rand > max_adj_rand[i]:
						max_adj_rand[i] = adjusted_rand
					if adjusted_delay < min_adj_delay[i]:
						min_adj_delay[i] = adjusted_delay
					if adjusted_delay > max_adj_delay[i]:
						max_adj_delay[i] = adjusted_delay

			temp_by_leader[iLeader] = leader_rows

		if IS_DEBUG_LEADER:
			print("[DEBUG] Contact aggregation pass 1 done. min_adj_rand=%s max_adj_rand=%s min_adj_delay=%s max_adj_delay=%s" % (
				str(min_adj_rand),
				str(max_adj_rand),
				str(min_adj_delay),
				str(max_adj_delay)
			))

		# Pass 2: normalize and compute final aggregated raw score per contact type.
		b_invert_contact_rands, b_invert_contact_delays = get_contact_rand_and_delay_invert_flags()

		for iLeader in NON_EXCLUDED_LEADERS:
			if iLeader in leaders_info_aggregated_raw_contact_probs:
				raise KeyError("[FATAL] Unexpected key iLeader=%d in leaders_info_aggregated_raw_contact_probs already existing" % iLeader)
			leaders_info_aggregated_raw_contact_probs[iLeader] = {}

			leader_rows = temp_by_leader[iLeader]
			for i in xrange(NUM_CONTACT_TYPES_ASSESSED):
				adjusted_rand, adjusted_delay, b_force_zero = leader_rows[i]

				adjusted_rand_norm_score = normalize_to_100(
					adjusted_rand,
					min_adj_rand[i],
					max_adj_rand[i],
					B_WARN,
					b_invert_contact_rands,
					parsed_adjusted_rand_names[i]
				)

				adjusted_delay_norm_score = normalize_to_100(
					adjusted_delay,
					min_adj_delay[i],
					max_adj_delay[i],
					B_WARN,
					b_invert_contact_delays,
					parsed_adjusted_delay_names[i]
				)

				aggregated_value = get_aggregated_raw_contact_score_from_adjusted_values(
					adjusted_rand_norm_score,
					adjusted_delay_norm_score,
					b_force_zero
				)

				leaders_info_aggregated_raw_contact_probs[iLeader][parsed_aggregated_raw_names[i]] = aggregated_value

		if IS_DEBUG_LEADER:
			print("[DEBUG] leaders_info_aggregated_raw_contact_probs after pass 2: %s" % str(leaders_info_aggregated_raw_contact_probs))

		# Cleanup
		del temp_by_leader
		del min_adj_rand, max_adj_rand, min_adj_delay, max_adj_delay

	# <!-- custom: performance optimization as recommended by chatgpt 5 thanks which i adjusted or not (renaming or such) -->
	MEM_POS_IDX = tuple(get_positive_memory_indexes_to_types().keys())
	MEM_NEG_IDX = tuple(get_negative_memory_indexes_to_types().keys())



	def get_positive_or_negative_memory_indexes(is_positive):
		# <!-- custom: similarly to contact aggregated code but for memory fields, that have positive/negative memory affection/resentment aggregated probs (see the related python docs for details). -->
		# <!-- custom: use memory indexes instead rather than types (string of full memory type name) as we fetch from DLL directly in sevopedia leader unlike in generate_leaders_data.py so we have access to these indexes so use them. -->
		positive_or_negative_memory_indexes = None

		if is_positive:
			positive_or_negative_memory_indexes = MEM_POS_IDX
		else:
			positive_or_negative_memory_indexes = MEM_NEG_IDX

		if not positive_or_negative_memory_indexes:
			raise ValueError("[VALUE ERROR] memory_indexes=%s check is false; memory_indexes cannot be empty or missing or some other kind of related or similar error, please check memory types (positive or negative) are fetched/imported correctly" % str(positive_or_negative_memory_indexes))
		
		return positive_or_negative_memory_indexes



	def compute_and_store_leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments(
		leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments,
		is_positive,
		is_affection
	):
		# leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_memory_key] = aggregated_raw_score
		# parsed_memory_key is e.g. "iAggregatedRawPositiveMemoryDeclaredWarAffection" (0-100)
		#
		# We compute these in two passes, similar to contact probs:
		# - Pass 1: adjusted attitude%/decay values + min/max per memory type
		# - Pass 2: normalize adjusted values to 0-100, then combine into an aggregated raw score

		positive_or_negative_memory_indexes = get_positive_or_negative_memory_indexes(is_positive)
		positive_negative = get_positive_negative(is_positive)
		affection_resentment = get_affection_resentment(is_affection)

		# Precompute per-memory metadata once.
		memory_indexes = list(positive_or_negative_memory_indexes)
		memory_types = [gc.getMemoryInfo(iMemoryIndex).getType() for iMemoryIndex in memory_indexes]
		memory_suffixes = [get_pascal_case_suffix(memory_type) for memory_type in memory_types]

		parsed_adjusted_attitude_names = ["iAdjustedMemoryAttitudePercent%s%s" % (suffix, affection_resentment) for suffix in memory_suffixes]
		parsed_adjusted_decay_names = ["iAdjustedMemoryDecay%s%s" % (suffix, affection_resentment) for suffix in memory_suffixes]
		parsed_aggregated_raw_names = ["iAggregatedRaw%sMemory%s%s" % (positive_negative, suffix, affection_resentment) for suffix in memory_suffixes]

		count = len(memory_indexes)

		# Pass 1: compute adjusted values and collect min/max across leaders.
		# temp_by_leader[iLeader][j] = (adjusted_attitude_percent, adjusted_decay, b_force_zero)
		temp_by_leader = {}
		min_adj_attitude = [None] * count
		max_adj_attitude = [None] * count
		min_adj_decay = [None] * count
		max_adj_decay = [None] * count

		for iLeader in NON_EXCLUDED_LEADERS:
			loopLeaderHeadInfo = gc.getLeaderHeadInfo(iLeader)
			leader_rows = [None] * count

			for j in xrange(count):
				iMemoryIndex = memory_indexes[j]
				memory_type = memory_types[j]

				attitude_percent_raw = loopLeaderHeadInfo.getMemoryAttitudePercent(iMemoryIndex)
				decay_rand_raw = loopLeaderHeadInfo.getMemoryDecayRand(iMemoryIndex)

				adjusted_attitude_percent, adjusted_decay, b_force_zero = get_adjusted_memory_values(
					attitude_percent_raw,
					decay_rand_raw,
					is_affection,
					IS_DEBUG_LEADER,
					memory_type
				)

				leader_rows[j] = (adjusted_attitude_percent, adjusted_decay, b_force_zero)

				# Min/max init
				if min_adj_attitude[j] is None:
					min_adj_attitude[j] = adjusted_attitude_percent
					max_adj_attitude[j] = adjusted_attitude_percent
					min_adj_decay[j] = adjusted_decay
					max_adj_decay[j] = adjusted_decay
				else:
					if adjusted_attitude_percent < min_adj_attitude[j]:
						min_adj_attitude[j] = adjusted_attitude_percent
					if adjusted_attitude_percent > max_adj_attitude[j]:
						max_adj_attitude[j] = adjusted_attitude_percent
					if adjusted_decay < min_adj_decay[j]:
						min_adj_decay[j] = adjusted_decay
					if adjusted_decay > max_adj_decay[j]:
						max_adj_decay[j] = adjusted_decay

			temp_by_leader[iLeader] = leader_rows

		if IS_DEBUG_LEADER:
			print("[DEBUG] Memory aggregation pass 1 done for %s/%s" % (positive_negative, affection_resentment))
			print("[DEBUG] min_adj_attitude=%s max_adj_attitude=%s" % (str(min_adj_attitude), str(max_adj_attitude)))
			print("[DEBUG] min_adj_decay=%s max_adj_decay=%s" % (str(min_adj_decay), str(max_adj_decay)))

		# Pass 2: normalize and compute final aggregated raw score per memory type.
		b_invert_attitude_percent, b_invert_decay = get_memory_attitude_percent_and_decay_invert_flags(is_positive, is_affection)

		for iLeader in NON_EXCLUDED_LEADERS:
			if iLeader not in leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments:
				leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments[iLeader] = {}

			leader_rows = temp_by_leader[iLeader]
			for j in xrange(count):
				adjusted_attitude_percent, adjusted_decay, b_force_zero = leader_rows[j]

				adjusted_attitude_norm_score = normalize_to_100(
					adjusted_attitude_percent,
					min_adj_attitude[j],
					max_adj_attitude[j],
					B_WARN,
					b_invert_attitude_percent,
					parsed_adjusted_attitude_names[j]
				)

				adjusted_decay_norm_score = normalize_to_100(
					adjusted_decay,
					min_adj_decay[j],
					max_adj_decay[j],
					B_WARN,
					b_invert_decay,
					parsed_adjusted_decay_names[j]
				)

				aggregated_value = get_aggregated_raw_positive_or_negative_memory_affection_or_resentment_score_from_adjusted_values(
					adjusted_attitude_norm_score,
					adjusted_decay_norm_score,
					b_force_zero
				)

				leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_aggregated_raw_names[j]] = aggregated_value

		if IS_DEBUG_LEADER:
			print("[DEBUG] leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments after pass 2 for %s/%s: %s" % (
				positive_negative,
				affection_resentment,
				str(leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments)
			))

		# Cleanup
		del temp_by_leader
		del min_adj_attitude, max_adj_attitude, min_adj_decay, max_adj_decay

	# <!-- custom: before computing minimums and maximums, compute and store raw aggregated fields, flattened, so they can be processed like any field/attribute and do min/max on them too for all leaders -->
	compute_and_store_leaders_info_aggregated_raw_contact_probs(leaders_info_aggregated_raw_contact_probs)

	for is_positive in (True, False):
		for is_affection in (True, False):
			compute_and_store_leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments(leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, is_positive, is_affection)



	def check_excluded_leaders_indexes_are_not_in_leaders_dict_keys(excluded_leaders_indexes_from_calculations, leaders_dict, leaders_dict_name):
		leaders_dict_keys = leaders_dict.keys()

		for excluded_leader_index in excluded_leaders_indexes_from_calculations:
			if (excluded_leader_index in leaders_dict_keys):
				excluded_leader_type = get_leader_type_from_leader_index(excluded_leader_index, gc)
				raise KeyError("[FATAL] During sanity checks testing, excluded_leader_index=%d (excluded_leader_type=%s), was assessed to not be properly excluded from the calculations and its corresponding leader_index is still part of the leaders_dict_keys=%s, please make sure this excluded leader is not part of the leaders_dict_name=%s." % (excluded_leader_index, excluded_leader_type, str(leaders_dict_keys), leaders_dict_name))



	def check_leaders_dict_only_has_leader_index_keys(leaders_dict, leaders_dict_name):
		for key in leaders_dict.keys():
			if not isinstance(key, int):
				key_name = repr(key)
				key_type_name = str(type(key))
				raise TypeError("[FATAL] In leaders_dict_name=%s, key=%s is not an integer index (key_name=%s). Only integer iLeader indexes should be used as keys. Please ensure that key_type_name=%s uses iLeader (e.g. 0, 1, 2...) as keys, not leader_type strings." % (leaders_dict_name, key, key_name, key_type_name))



	check_excluded_leaders_indexes_are_not_in_leaders_dict_keys(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS, leaders_info_aggregated_raw_contact_probs, "leaders_info_aggregated_raw_contact_probs")
	check_leaders_dict_only_has_leader_index_keys(leaders_info_aggregated_raw_contact_probs, "leaders_info_aggregated_raw_contact_probs")

	check_excluded_leaders_indexes_are_not_in_leaders_dict_keys(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS, leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, "leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments")
	check_leaders_dict_only_has_leader_index_keys(leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, "leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments")



	def get_fields_directly_parsed():
		# <!-- custom: dict of getter_name: (label, b_invert) -->
		# <!-- custom: note: --> Attributes that need value inversion when normalizing <!-- custom: is when --> high = bad, low = good
		fields_with_direct_getters = {
			# ==== FIRST XML FIELDS PART 1 (from XML order) ====
			"getWonderConstructRand": ("Wonder C.R", False),
			"getBaseAttitude": ("Base Attitude", False),
			"getBasePeaceWeight": ("Base Peace Weig", False),
			"getPeaceWeightRand": ("Peace Weig Rand", False),
			"getWarmongerRespect": ("Warmonger Resp", False),
			"getEspionageWeight": ("Espionage Weig", False),
			"getRefuseToTalkWarThreshold": ("RefToTalkW Span", False),
			"getNoTechTradeThreshold": ("NoTech2AdvTrT", True),
			"getTechTradeKnownPercent": ("NoTechYetRdy%", False),
			"getMaxGoldTradePercent": ("Max Gold Tr%", False),
			"getMaxGoldPerTurnTradePercent": ("Max GPT Tr%", False),
			# ==== BBAI VICTORY WEIGHTS ====
			# <!-- custom: now exposed to python, see sevopedia helpers py file code comments for details -->
			"getCultureVictoryWeight": ("Culture", False),
			"getSpaceVictoryWeight": ("Space", False),
			"getConquestVictoryWeight": ("Conquest", False),
			"getDominationVictoryWeight": ("Domination", False),
			"getDiplomacyVictoryWeight": ("Diplomacy", False),
			# <!-- custom: end of now exposed to python fields -->
			# ==== WAR XML FIELDS (from XML order) ====
			"getMaxWarRand": ("T.W Likely", True),
			"getMaxWarNearbyPowerRatio": ("T.W NearPR", False),
			"getMaxWarDistantPowerRatio": ("T.W DistPR", False),
			"getMaxWarMinAdjacentLandPercent": ("T.W Min NearPR", True),
			"getLimitedWarRand": ("Lim.W Likely", True),
			"getLimitedWarPowerRatio": ("Lim.W PR.", False),
			"getDogpileWarRand": ("Dogpile Likely", True),
			"getMakePeaceRand": ("MakePeaceLikely", True),
			"getDeclareWarTradeRand": ("W AllianceMaker", False),
			"getDemandRebukedSneakProb": ("TribRef SneakW%", False),
			"getDemandRebukedWarProb": ("TribRef W%", False),
			"getRazeCityProb": ("Raz C %", False),
			"getBuildUnitProb": ("Build Unit %", False),
			# ==== ATTITUDE MODIFIER FIELDS (from XML order) ====
			"getBaseAttackOddsChange": ("Risky Aggr", False),
			"getAttackOddsChangeRand": ("Risky Aggr Rand+", False),
			"getWorseRankDifferenceAttitudeChange": ("Worse Rank AC", False),
			"getBetterRankDifferenceAttitudeChange": ("Better Rank AC", False),
			# <!-- custom: inverted according to: https://modiki.civfanatics.com/index.php/Civ4LeaderHeadInfos at "iCloseBordersAttitudeChange" and then according to also https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#iclosebordersattitudechange (description translated(ion) seems a bit less accurate but is informative and helpful maybe etc -->
			"getCloseBordersAttitudeChange": ("CloseBordersSpark", True),
			"getLostWarAttitudeChange": ("Lost W AC", False),
			"getAtWarAttitudeDivisor": ("At W AD", False),
			"getAtWarAttitudeChangeLimit": ("At W ACL", False),
			"getAtPeaceAttitudeDivisor": ("At Peace AD", False),
			"getAtPeaceAttitudeChangeLimit": ("At Peace ACL", False),
			"getSameReligionAttitudeChange": ("Same Religion AC", False),
			"getSameReligionAttitudeDivisor": ("Same Religion AD", False),
			"getSameReligionAttitudeChangeLimit": ("Same Religion ACL", False),
			"getDifferentReligionAttitudeChange": ("Diff.Religion AC", False),
			"getDifferentReligionAttitudeDivisor": ("Diff.Religion AD", False),
			"getDifferentReligionAttitudeChangeLimit": ("Diff.Religion ACL", True),
			"getBonusTradeAttitudeDivisor": ("Bonus Tr AD", False),
			"getBonusTradeAttitudeChangeLimit": ("Bonus Tr ACL", False),
			"getOpenBordersAttitudeDivisor": ("Open Borders AD", False),
			"getOpenBordersAttitudeChangeLimit": ("Open Borders ACL", False),
			"getDefensivePactAttitudeDivisor": ("Defensive Pact AD", False),
			"getDefensivePactAttitudeChangeLimit": ("Defensive Pact ACL", False),
			"getShareWarAttitudeChange": ("Share W AC", False),
			"getShareWarAttitudeDivisor": ("Share W AD", False),
			"getShareWarAttitudeChangeLimit": ("Share W ACL", False),
			"getFavoriteCivicAttitudeChange": ("Favorite Civic AC", False),
			"getFavoriteCivicAttitudeDivisor": ("Favorite Civic AD", False),
			"getFavoriteCivicAttitudeChangeLimit": ("Favorite Civic ACL", False),
			# <!-- custom: attitude thresholds later in code in case we want to aggregate them or do aggregate them but not sure may or may not do -->
			# ==== VASSAL AND FREEDOM FIELDS (from XML order) ====
			"getVassalPowerModifier": ("ResistCapitulP.M", False),
			"getFreedomAppreciation": ("FreedomApprec", False),
			# <!-- custom: then fields with nested or incremental getters (flavors, contacts, memory, nowarattitudeprobs, etc if any more) are handled separately later -->
		}

		# ==== ATTITUDE THRESHOLDS ====
		# <!-- custom: here even though debug code in debugPrintLeaderHeadInfoFieldsToFetch uses a dynamic code, manually tell all the getters names instead of a dynamic code, to make sure we have them all and since they have flat getters this is consistent with how other similar kind of field/getters are handled as before in this current tuple; their names are available in the debug output example of the same debugPrintLeaderHeadInfoFieldsToFetch, see there for details -->
		fields_attitude_thresholds = {
			# <!-- custom: inverted according to: https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#demandtributeattitudethreshold -->
			"getDemandTributeAttitudeThreshold": ("ScaryNoTrib", True),
			"getNoGiveHelpAttitudeThreshold": ("PrideNoHelp", False),
			"getTechRefuseAttitudeThreshold": ("Tech", False),
			# <!-- custom: now exposed to python, see sevopedia helpers py file code comments for details -->
			"getCityRefuseAttitudeThreshold": ("C", False),
			"getNativeCityRefuseAttitudeThreshold": ("Native C", False),
			# <!-- custom: end of now exposed to python fields -->
			"getStrategicBonusRefuseAttitudeThreshold": ("Strategic Bonus", False),
			"getHappinessBonusRefuseAttitudeThreshold": ("Happiness Bonus", False),
			"getHealthBonusRefuseAttitudeThreshold": ("Health Bonus", False),
			"getMapRefuseAttitudeThreshold": ("Map", False),
			"getDeclareWarRefuseAttitudeThreshold": ("D.W", False),
			# <!-- custom: inverted according to: https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#declarewarthemrefuseattitudethreshold -->
			"getDeclareWarThemRefuseAttitudeThreshold": ("LoyaltyNoD.W", True),
			"getStopTradingRefuseAttitudeThreshold": ("StopTr", False),
			# <!-- custom: inverted according to: https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#stoptradingthemrefuseattitudethreshold -->
			"getStopTradingThemRefuseAttitudeThreshold": ("LoyaltyNoStopTr", True),
			"getAdoptCivicRefuseAttitudeThreshold": ("Adopt Civic", False),
			"getConvertReligionRefuseAttitudeThreshold": ("Convert Religion", False),
			"getOpenBordersRefuseAttitudeThreshold": ("Open Borders", False),
			"getDefensivePactRefuseAttitudeThreshold": ("Defensive Pact", False),
			"getPermanentAllianceRefuseAttitudeThreshold": ("Perm. Alliance", False),
			"getVassalRefuseAttitudeThreshold": ("Vassal", False),
		}

		# <!-- custom: fields not parsed into leaders_info_cached yet; useful for deeper AI modeling later:
		# Advanced arrays (optional):
		# - <UnitAIWeightModifier> by UnitAIType
		# - <ImprovementWeightModifier> by ImprovementType (GPT-5.2-Codex) -->
		return fields_with_direct_getters, fields_attitude_thresholds



	# <!-- custom: store only the fields we want to display in the AI personality panel not the other / not all XML fields, see sevopedia debuggers py file and debugPrintLeaderHeadInfoFieldsToFetch and or its example of output for details -->
	fields_with_direct_getters, fields_attitude_thresholds = get_fields_directly_parsed()
	required_getters = tuple(fields_with_direct_getters.keys()) + tuple(fields_attitude_thresholds.keys())
	check_required_newly_exposed_python_getters_gc_leader_exist(required_getters)
	def get_leader_info_minimums_and_maximums(fields_with_direct_getters, fields_attitude_thresholds, leaders_info_aggregated_raw_contact_probs, leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments):
		# <!-- custom: fake leaders that stores minimum values among all leader for each field we want to display regardless of inversions, same for maximum values too -->
		leader_info_minimums = {}
		leader_info_maximums = {}

		for iLeader in NON_EXCLUDED_LEADERS:
			# <!-- custom: performance optimization as recommended by chatgpt 5 thanks which i adjusted or not (renaming or such) -->
			loopLeaderHeadInfo = gc.getLeaderHeadInfo(iLeader)

			for getter_name, (label, b_invert) in fields_with_direct_getters.items():
				value_generic = getattr(loopLeaderHeadInfo, getter_name)()
				computeAndStoreMinMaxOfOneKey(getter_name, value_generic, leader_info_minimums, leader_info_maximums)

			for getter_name, (label, b_invert) in fields_attitude_thresholds.items():
				value_attitude_threshold = getattr(loopLeaderHeadInfo, getter_name)()
				computeAndStoreMinMaxOfOneKey(getter_name, value_attitude_threshold, leader_info_minimums, leader_info_maximums)

			# <!-- custom: parse fields with nested or with incremental getters as flat fields with an alternative key so we can loop over them more easily and reorder them later if needed, also our code is more consistent this way -->
			# ==== FLAVORS ====
			for i in xrange(gc.getNumFlavorTypes()):
				# <!-- custom: store them as a parsed key name since getter is incremental and does not directly reference the name of each flavor -->
				value_flavor = loopLeaderHeadInfo.getFlavorValue(i)
				flavor_type = gc.getFlavorTypes(i)  # e.g. "FLAVOR_MILITARY"
				suffix = get_pascal_case_suffix(flavor_type) # → <!-- custom: "Military" -->
				parsed_name_flavor = "iFlavor%s" % suffix  # → iFlavorMilitary
				computeAndStoreMinMaxOfOneKey(parsed_name_flavor, value_flavor, leader_info_minimums, leader_info_maximums)

			# ==== CONTACTS ====
			for i in xrange(NUM_CONTACT_TYPES_ASSESSED):
				# <!-- custom: compute minimum and maximum among all leaders for raw contact fields, which here and as of now are only contact rands and contact delays -->
				# <!-- custom: Step 1: Raw contact rands and delays -->
				contact_type = gc.getContactTypes(i) # e.g. "CONTACT_JOIN_WAR"
				suffix = get_pascal_case_suffix(contact_type) # → "JoinWar"

				value_rand_raw = loopLeaderHeadInfo.getContactRand(i)
				value_delay_raw = loopLeaderHeadInfo.getContactDelay(i)
				parsed_name_rand = "iContactRand%s" % suffix # → iContactRandJoinWar
				parsed_name_delay = "iContactDelay%s" % suffix # → iContactDelayJoinWar
				computeAndStoreMinMaxOfOneKey(parsed_name_delay, value_delay_raw, leader_info_minimums, leader_info_maximums)
				computeAndStoreMinMaxOfOneKey(parsed_name_rand, value_rand_raw, leader_info_minimums, leader_info_maximums)

				# <!-- custom: also export the minimum and maximum raw aggregated contact prob (based on iLeader's rand and iLeader's delay (note: not based on the min and max rand among all leaders nor the min and max delay among all leaders)) among all leaders for each contact type -->
				# <!-- custom: Step 2: Raw aggregated contact probs -->
				parsed_name_aggregated_raw_contact_prob = "iAggregatedRawContactProb%s" % suffix # → iAggregatedRawContactProbJoinWar
				value_aggregated_raw_contact_prob = leaders_info_aggregated_raw_contact_probs[iLeader][parsed_name_aggregated_raw_contact_prob]
				computeAndStoreMinMaxOfOneKey(parsed_name_aggregated_raw_contact_prob, value_aggregated_raw_contact_prob, leader_info_minimums, leader_info_maximums)

			# ==== MEMORY ====
			# <!-- custom: compute minimum and maximum among all leaders for raw contact fields, which here and as of now are only contact rands and contact delays; here we can loop over real DLL i index directly like in sevopedia_helpers py file debug code (see there for details), and unlike for raw aggregated memory fields that are separated in positive and negative memories, so here we can loop over real DLL i index directly -->
			for is_positive in (True, False):
				for is_affection in (True, False):
					positive_or_negative_memory_indexes = get_positive_or_negative_memory_indexes(is_positive)
					positive_negative = get_positive_negative(is_positive)
					affection_resentment = get_affection_resentment(is_affection)

					for i in positive_or_negative_memory_indexes:
						memory_type = gc.getMemoryInfo(i).getType() # e.g. "MEMORY_DECLARED_WAR"
						suffix = get_pascal_case_suffix(memory_type) # → "DeclaredWar"

						# <!-- custom: Step 1: Raw memory attitude percents and decays -->
						# <!-- custom: since we display same raw attitude percent and decay fields values in UI regardless of positive/negative memory affection/resentment (raw aggregated values then the normalized aggregated values are is displayed) aggregation, no need to store multiple versions (i.e. positive/negative and affection/resentment) of these raw attitude percent and decay fields, store only one kind for all of these 4 possible combination cases (positive-affection, positive-resentment, negative-affection, negative-resentment) same as in XML fields structuration too for raw attitude percents and decays, i.e. for example only for example iMemoryAttitudePercentDeclaredWar (no positive-negative, no affection-resentment) for raw attitude_percent and decay fields same as in XML -->
						# <!-- custom: similarly for min max of raw attitude percents and decays export only once out of the 4 combinations (among positive-affection, positive-resentment, negative-affection, negative-resentment), since the raw value is always the same field and field name, no need to do it again for the other 3 times/combinations -->
						parsed_name_attitude_percent = "iMemoryAttitudePercent%s" % suffix # → iMemoryAttitudePercentDeclaredWar
						if (parsed_name_attitude_percent not in leader_info_minimums) and (parsed_name_attitude_percent not in leader_info_maximums):
							value_attitude_percent = loopLeaderHeadInfo.getMemoryAttitudePercent(i)
							computeAndStoreMinMaxOfOneKey(parsed_name_attitude_percent, value_attitude_percent, leader_info_minimums, leader_info_maximums)

						parsed_name_decay = "iMemoryDecay%s" % suffix # → iMemoryDecayDeclaredWar
						if (parsed_name_decay not in leader_info_minimums) and (parsed_name_decay not in leader_info_maximums):
							value_decay = loopLeaderHeadInfo.getMemoryDecayRand(i)
							computeAndStoreMinMaxOfOneKey(parsed_name_decay, value_decay, leader_info_minimums, leader_info_maximums)

						# <!-- custom: Step 2: Raw aggregated positive and negative memory affections and resentments -->
						parsed_name_aggregated_raw_positive_or_negative_memory_affection_or_resentment = "iAggregatedRaw%sMemory%s%s" % (positive_negative, suffix, affection_resentment) # → iAggregatedRawPositiveMemoryDeclaredWarAffection or iAggregatedRawPositiveMemoryDeclaredWarResentment or iAggregatedRawNegativeMemoryDeclaredWarAffection or iAggregatedRawNegativeMemoryDeclaredWarResentment
						value_aggregated_raw_positive_or_negative_memory_affection_or_resentment = leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_aggregated_raw_positive_or_negative_memory_affection_or_resentment]
						computeAndStoreMinMaxOfOneKey(parsed_name_aggregated_raw_positive_or_negative_memory_affection_or_resentment, value_aggregated_raw_positive_or_negative_memory_affection_or_resentment, leader_info_minimums, leader_info_maximums)

			# ==== NOWARATTITUDEPROBS ====
			for i in xrange(NUM_ATTITUDE_TYPES_ASSESSED):
				value_no_war_attitude_prob = loopLeaderHeadInfo.getNoWarAttitudeProb(i)
				attitude_type = gc.getAttitudeInfo(i).getType()  # e.g. "ATTITUDE_FURIOUS"
				suffix = get_pascal_case_suffix(attitude_type)  # → "Furious"
				parsed_name_no_war_attitude_prob = "iNoWarAttitudeProb%s" % suffix  # → iNoWarAttitudeProbFurious
				computeAndStoreMinMaxOfOneKey(parsed_name_no_war_attitude_prob, value_no_war_attitude_prob, leader_info_minimums, leader_info_maximums)
		
		# <!-- custom: after all min and max parsing is done, some sanity and warning checks -->
		for key in leader_info_minimums:
			# <!-- custom: ensure our leader_info_minimums is reliable even if a bit if not lot or not or yes or etcbefore proceeding further -->
			if key not in leader_info_maximums:
				raise KeyError(u"[KEY ERROR] Missing leader_info_maximums key=%s, in leader_info_minimums but not in leader_info_maximums, cannot proceed if both leader_info_minimums and leader_info_maximums all have same keys, please check your min and max computing or and DLL behaviour that may explain missing fields." % key)

			# <!-- custom: also warn once if min == max for each field/key and now while it is computationally (at module load) inexpensive to do so, do not rewarn at each leader computation nor later at init or and such -->
			if leader_info_minimums[key] == leader_info_maximums[key]:
				if IS_DEBUG_LEADER:
					print("[WARNING] Key=%s has an identical min and max value (%d). Warning only once at module load so we don't have/want/need to redo it later at the normalization stage, fix/change the XML leader info value(s) of some leader(s) so that min and max among all leaders are different if desired, or keep as is if intended/desired that leaders behave the same for this key." % (key, leader_info_minimums[key]))
		
		if IS_DEBUG_LEADER:
			print("[DEBUG] At end of the function get_leader_info_minimums_and_maximums, we return for the minimums leader_info_minimums=%s" % str(leader_info_minimums))
			print("[DEBUG] At end of the function get_leader_info_minimums_and_maximums, we return for the maximums leader_info_maximums=%s" % str(leader_info_maximums))

		return (leader_info_minimums, leader_info_maximums)



	leader_info_minimums, leader_info_maximums = get_leader_info_minimums_and_maximums(fields_with_direct_getters, fields_attitude_thresholds, leaders_info_aggregated_raw_contact_probs, leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments)

	# <!-- custom: note: leader_info_minimums, leader_info_maximums are like fake leaders, they dont have iLeader keys but only field/attribute keys (like "getMaxWarRand", "iAggregatedEtc...", "getBasePeaceWeight", "iFlavorMilitary", etc), so no need and not relevant to check if excluded leaders or if keys are only indexes because they are not, we have enough sanity checks overall everywhere to not need to resanity check this xd even though may help maybe but is bit tedious since dbug also helps (see SevopediaLead_derExamplesOfOutputs.txt or whichever file it is named if still in this mod Sevopedia folder for example of outputs), so as for sanity checks skipping them for leader_info_minimums, leader_info_maximums. -->



	# Store per-leader <!-- custom: cached info for all keys/attributes -->
	# LEADERS_INFO_CACHED: dict of leaderName → dict of attributeName → <!-- custom: tuple of (label, raw_value, norm_value, scale) for later display at UI code -->
	LEADERS_INFO_CACHED = {}



	def get_labels_as_keys_or_suffixes_with_abbreviated_tail(key_or_suffix, tail_to_trim, abbreviated_tail, label_raw, max_length):
		# <!-- custom: for example for "SameReligionAttitudeChangeLimit" (note: "get" front already stripped), "ACL", "(39)", 15: -->

		# <!-- custom: first trim the tail in key_or_suffix if any, for example "SameReligionAttitudeChangeLimit" → "SameReligion" -->
		if tail_to_trim:
			key_or_suffix_with_tail_trimmed = key_or_suffix[:-len(tail_to_trim)]
		else:
			key_or_suffix_with_tail_trimmed = key_or_suffix

		# <!-- custom: check if this result is longer than would allow to fit "ACL" + " " + "(39)" as compared to what max_length would allow in total in the final label, and if all good trim it as such i.e. trim enough of the key_or_suffix_with_tail_trimmed until it allows to fit total_tail_length within max_length, for example:
		# - "SameReligion" has a length of 12
		# - "ACL" + " " + "(39)" has a total_tail_length of 3 + 1 + 4 = 8
		# - max_length is 15
		# So there will be max_length - total_tail_length = 15 - 8 = 7 chars remaining for the key_or_suffix_with_tail_trimmed, trim anything beyond that, so the key_or_suffix_with_tail_trimmed is now only for example "SameReligion" → "SameRel" -->
		total_tail_length = len(abbreviated_tail) + len(" ") + len(label_raw)
		room_for_first = max_length - total_tail_length
		if room_for_first <= 0:
			raise ValueError(u"[ERROR] Unexpected label_raw=%s + ' ' + abbreviated_tail=%s total_tail_length=%d, too long to fit key_or_suffix_with_tail_trimmed=%s within max_length = %d in the final label. This should not happen, please make sure abbreviated_tail + ' ' + label_raw are short enough relative to max_length, or that max_length is high enough." % (label_raw, abbreviated_tail, total_tail_length, key_or_suffix_with_tail_trimmed, max_length))
		# <!-- custom: minimum 1 to accomodate for the " " space character -->
		key_or_suffix_with_tail_trimmed_further_trimmed = key_or_suffix_with_tail_trimmed[:max(1, room_for_first)]

		# <!-- custom: finally append ' ' + the abbreviated tail as intended, for example "SameRel" → "SameRelACL (39)" -->
		key_or_suffix_with_abbreviated_tail = key_or_suffix_with_tail_trimmed_further_trimmed + abbreviated_tail + " " + label_raw
		
		return key_or_suffix_with_abbreviated_tail

	def get_labels_as_keys_or_suffixes_max_length_label(key_or_suffix, label_raw, max_length):
		# Returns key_or_suffix + label_raw, trimmed so total length ≤ max_length.
		#
		# <!-- custom: examples of output from chagpt as well and some added by me as well too thanks and my prompt too: -->
		# "getMaxWarRand", " (50)", 18 → "MaxWarRand (50)"
		# "DemandWar", " (50/510)", 18 → "Demand (50/510)"
		# "LongLongKeyNameHere", " (9)", 14 → "LongLongKe (9)"
		# "getConquestVictoryWeight", " (39)", 19 → "Conquest (39)"
		# "getSameReligionAttitudeChangeLimit", " (39)", 15 → "SameRelACL (39)"

		# <!-- custom: first strip front or tail, for example "getSameReligionAttitudeChangeLimit" → "SameReligion"
		if key_or_suffix.startswith("get"):
			# <!-- custom: strip this front part ("get") first -->
			key_or_suffix_without_front = key_or_suffix[len("get"):]

			if key_or_suffix_without_front.endswith("VictoryWeight"):
				# <!-- custom: just strip tail (i.e. without appending any abbreviated_tail as a replacement) -->
				return get_labels_as_keys_or_suffixes_with_abbreviated_tail(key_or_suffix_without_front, "VictoryWeight", "", label_raw, max_length)
			elif key_or_suffix_without_front.endswith("RefuseAttitudeThreshold"):
				# <!-- custom: no need for a "RAT" abbreviated_tail as would clutter and they are all in same category at least as of now if not always or not or yes or etc; so opt for a more compact label instead -->
				return get_labels_as_keys_or_suffixes_with_abbreviated_tail(key_or_suffix_without_front, "RefuseAttitudeThreshold", "", label_raw, max_length)
			elif key_or_suffix_without_front.endswith("AttitudeThreshold"):
				# <!-- custom: the "AT" vs "RAT" here is informative though i think for the few fields that have it i think so display it i think -->
				return get_labels_as_keys_or_suffixes_with_abbreviated_tail(key_or_suffix_without_front, "AttitudeThreshold", "AT", label_raw, max_length)
			elif key_or_suffix_without_front.endswith("AttitudeChangeLimit"):
				return get_labels_as_keys_or_suffixes_with_abbreviated_tail(key_or_suffix_without_front, "AttitudeChangeLimit", "ACL", label_raw, max_length)
			elif key_or_suffix_without_front.endswith("AttitudeChangeDivisor"):
				return get_labels_as_keys_or_suffixes_with_abbreviated_tail(key_or_suffix_without_front, "AttitudeChangeDivisor", "ACD", label_raw, max_length)
			elif key_or_suffix_without_front.endswith("AttitudeChange"):
				return get_labels_as_keys_or_suffixes_with_abbreviated_tail(key_or_suffix_without_front, "AttitudeChange", "AC", label_raw, max_length)
			else:
				return get_labels_as_keys_or_suffixes_with_abbreviated_tail(key_or_suffix_without_front, "", "", label_raw, max_length)
		# <!-- custom: no front nor tail, just trim key_or_suffix to fit label_raw within max_length -->
		else:
			return get_labels_as_keys_or_suffixes_with_abbreviated_tail(key_or_suffix, "", "", label_raw, max_length)

	def get_symbol_scale(score, symbol):
		# <!-- custom: examples:
		# - with symbol "+" and value 64 (/100), returns "++++++" if i'm not mistaken anyways
		# - with symbol "#" and value 39 (/100), returns "###" if i'm not mistaken anyways
		# -->
		return symbol * (score // 10)

	def compute_and_store_leader_info_cached_tuple(raw_value, min_value, max_value, b_invert, symbol, all_symbols, cache_key, label, iLeader, leader_info_cached):
		norm_value = normalize_to_100(raw_value, min_value, max_value, B_WARN, b_invert, cache_key)

		if (min_value == max_value):
			symbol = all_symbols["EQUAL_SCALE_SYMBOL"]

		if IS_DEBUG_LEADER:
			print("[DEBUG] raw_value=%d, min_value=%d, max_value=%d, norm_value=%d, for cache_key=%s, b_invert=%s at iLeader=%d" % (raw_value, min_value, max_value, norm_value, cache_key, str(b_invert), iLeader))

		if not label:
			raise ValueError(u"Unexpected label=%s tested false as a boolean in cache_key=%s at iLeader=%d, please check label is not empty or missing or some other kind of invalid format" % (str(label), cache_key, iLeader))

		if (symbol not in all_symbols.values()):
			raise ValueError(u"Unexpected symbol=%s not in all_symbols=%s in cache_key=%s at iLeader=%d." % (symbol, str(all_symbols), cache_key, iLeader))
		scale = get_symbol_scale(norm_value, symbol)

		# Store final as <!-- custom: a tuple after all parsing/caching is finished for this leader for faster/better performance than dict or such other storage --> for future display at UI code
		leader_info_cached_tuple = (label, norm_value, scale)
		leader_info_cached[cache_key] = leader_info_cached_tuple
		if IS_DEBUG_LEADER:
			print(u"[DEBUG] Leader info cached tuple for iLeader=%d is leader_info_cached_tuple=%s" % (iLeader, str(leader_info_cached_tuple)))



	def compute_and_store_leaders_info_cached(leaders_info_aggregated_raw_contact_probs, leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, fields_with_direct_getters, fields_attitude_thresholds, leader_info_minimums, leader_info_maximums):
		# Loops over all leaders and normalizes each attribute to a 0-100 scale, using previously computed min/max per attribute and inversion flags.

		# --- Symbol settings ---
		all_symbols = {
			"RAW_SCALE_SYMBOL": "+",
			"AGGREGATED_SCALE_SYMBOL": "#",
			"EQUAL_SCALE_SYMBOL": "=",
		}

		# <!-- custom: in the debug output (i=0 to NUM_CONTACT_TYPES_ASSESSED (i=13 so 14 values in total as of now see latest value or code comments or docs for updated value or and info)) order -->
		contact_index_labels = {
			0: "Relig. Press.",		# CONTACT_RELIGION_PRESSURE
			1: "Civic Press.",		# CONTACT_CIVIC_PRESSURE
			2: "Join W", 			# CONTACT_JOIN_WAR
			3: "Stop Tr",			# CONTACT_STOP_TRADING
			4: "Gave Help",			# CONTACT_GIVE_HELP
			5: "Help",				# CONTACT_ASK_FOR_HELP
			6: "Trib",				# CONTACT_DEMAND_TRIBUTE
			7: "Open Borders",		# CONTACT_OPEN_BORDERS
			8: "Defensive Pact",	# CONTACT_DEFENSIVE_PACT
			9: "Perm. Alliance",	# CONTACT_PERMANENT_ALLIANCE
			10: "Peace Treaty",		# CONTACT_PEACE_TREATY
			11: "Tr Tech",			# CONTACT_TRADE_TECH
			12: "Tr Bonus",			# CONTACT_TRADE_BONUS
			13: "Tr Map",			# CONTACT_TRADE_MAP
		}

		positive_memory_index_labels = {
			8:  "Gave Help",		# MEMORY_GIVE_HELP
			10: "AcD",				# MEMORY_ACCEPT_DEMAND
			12: "AcReligion",		# MEMORY_ACCEPTED_RELIGION
			14: "AcCivic",			# MEMORY_ACCEPTED_CIVIC
			16: "AcJoin W",			# MEMORY_ACCEPTED_JOIN_WAR
			18: "AcStop Tr",		# MEMORY_ACCEPTED_STOP_TRADING
			28: "Tr Tech",			# MEMORY_TRADED_TECH_TO_US
			31: "VotedForUs",		# MEMORY_VOTED_FOR_US
			32: "Event Good",		# MEMORY_EVENT_GOOD_TO_US
			34: "Liberated C",		# MEMORY_LIBERATED_CITIES
			35: "Indep",			# MEMORY_INDEPENDENCE
		}

		negative_memory_index_labels = {
			0:  "D.W",				# MEMORY_DECLARED_WAR
			1:  "D.W on Fr",		# MEMORY_DECLARED_WAR_ON_FRIEND
			2:  "HiredW Ally",		# MEMORY_HIRED_WAR_ALLY
			3:  "Nuked Us",			# MEMORY_NUKED_US
			4:  "Nuked Fr",			# MEMORY_NUKED_FRIEND
			5:  "Raz C",			# MEMORY_RAZED_CITY
			6:  "Raz Holy C",		# MEMORY_RAZED_HOLY_CITY
			7:  "Spy Caught",		# MEMORY_SPY_CAUGHT
			9:  "Ref Help Us",		# MEMORY_REFUSED_HELP
			11: "Rej D",			# MEMORY_REJECTED_DEMAND
			13: "Dn Religion",		# MEMORY_DENIED_RELIGION
			15: "Dn Civic",			# MEMORY_DENIED_CIVIC
			17: "Dn Join W",		# MEMORY_DENIED_JOIN_WAR
			19: "Dn Stop Tr",		# MEMORY_DENIED_STOP_TRADING
			20: "Stopped Tr",		# MEMORY_STOPPED_TRADING
			21: "Rec Stopped Tr",	# MEMORY_STOPPED_TRADING_RECENT
			22: "Tr Embargo",		# MEMORY_HIRED_TRADE_EMBARGO
			23: "Made D",			# MEMORY_MADE_DEMAND
			24: "CancelledVassal",	# MEMORY_CANCELLED_VASSAL_AGREEMENT
			25: "Recent MadeD",		# MEMORY_MADE_DEMAND_RECENT
			26: "Cancelled OB",		# MEMORY_CANCELLED_OPEN_BORDERS
			27: "Cancelled DP",		# MEMORY_CANCELLED_DEFENSIVE_PACT
			29: "Recent Tech Any",	# MEMORY_RECEIVED_TECH_FROM_ANY
			30: "Voted Ag Us",		# MEMORY_VOTED_AGAINST_US
			33: "Event Bad",		# MEMORY_EVENT_BAD_TO_US
			36: "Recent W",			# MEMORY_DECLARED_WAR_RECENT
		}

		# <!-- custom: a minimal sanity check before merging the index_labels (not checking if some indexes are missing here in the dictionary as we'd likely i assumeget a key error later otherwise -->
		check_overlapping_keys_between_dicts(positive_memory_index_labels, negative_memory_index_labels)
		# ✅ Combined dictionary
		positive_and_negative_memory_index_labels = {}
		positive_and_negative_memory_index_labels.update(positive_memory_index_labels)
		positive_and_negative_memory_index_labels.update(negative_memory_index_labels)

		for iLeader in NON_EXCLUDED_LEADERS:
			leader_info_cached = {}

			# <!-- custom: performance optimization as recommended by chatgpt 5 thanks which i adjusted or not (renaming or such) -->
			loopLeaderHeadInfo = gc.getLeaderHeadInfo(iLeader)

			symbol_generics = all_symbols["RAW_SCALE_SYMBOL"]
			for getter_name_generic, (label_generic, b_invert_generic) in fields_with_direct_getters.items():
				raw_value_generic = getattr(loopLeaderHeadInfo, getter_name_generic)()
				# <!-- custom: also add raw value to label like "Military (12)" for example for flavors instead of just "Military" (so we have both raw value in label as well as normalized value in the 2nd column of each of the AI personality panel tables (i.e. before the scale (e.g. "++++" or similar column of each of the AI personality panel tables too -->
				label_raw_generic = "(%d)" % raw_value_generic
				if IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD:
					label_with_raw_value_generic = get_labels_as_keys_or_suffixes_max_length_label(getter_name_generic, label_raw_generic, 18)
				else:
					label_with_raw_value_generic = "%s %s" % (label_generic, label_raw_generic)
				min_value_generic = leader_info_minimums[getter_name_generic]
				max_value_generic = leader_info_maximums[getter_name_generic]
				compute_and_store_leader_info_cached_tuple(raw_value_generic, min_value_generic, max_value_generic, b_invert_generic, symbol_generics, all_symbols, getter_name_generic, label_with_raw_value_generic, iLeader, leader_info_cached)

			symbol_attitude_thresholds = all_symbols["RAW_SCALE_SYMBOL"]
			for getter_name_attitude_threshold, (label_attitude_threshold, b_invert_attitude_threshold) in fields_attitude_thresholds.items():
				raw_value_attitude_threshold = getattr(loopLeaderHeadInfo, getter_name_attitude_threshold)()
				label_raw_attitude_threshold = "(%d)" % raw_value_attitude_threshold
				if IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD:
					label_with_raw_value_attitude_threshold = get_labels_as_keys_or_suffixes_max_length_label(getter_name_attitude_threshold, label_raw_attitude_threshold, 18)
				else:
					label_with_raw_value_attitude_threshold = "%s %s" % (label_attitude_threshold, label_raw_attitude_threshold)
				min_value_attitude_threshold = leader_info_minimums[getter_name_attitude_threshold]
				max_value_attitude_threshold = leader_info_maximums[getter_name_attitude_threshold]
				compute_and_store_leader_info_cached_tuple(raw_value_attitude_threshold, min_value_attitude_threshold, max_value_attitude_threshold, b_invert_attitude_threshold, symbol_attitude_thresholds, all_symbols, getter_name_attitude_threshold, label_with_raw_value_attitude_threshold, iLeader, leader_info_cached)

			b_invert_flavors = False
			symbol_flavors = all_symbols["RAW_SCALE_SYMBOL"]
			for i in xrange(gc.getNumFlavorTypes()):
				flavor_type = gc.getFlavorTypes(i)  # e.g. "FLAVOR_MILITARY"
				suffix = get_pascal_case_suffix(flavor_type) # → "Military"
				parsed_name_flavor = "iFlavor%s" % suffix  # → iFlavorMilitary
				label_flavor = suffix
				raw_value_flavor = loopLeaderHeadInfo.getFlavorValue(i)
				label_raw_flavor = "(%d)" % raw_value_flavor
				if IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD:
					# <!-- custom: for these fields, the suffix like "Military" is much shorter than the parsed name like "iFlavorMilitary", and clear enough for our need for the labels as keys or suffixes, so use the suffix it instead of parsed name -->
					label_with_raw_value_flavor = get_labels_as_keys_or_suffixes_max_length_label(suffix, label_raw_flavor, 19)
				else:
					label_with_raw_value_flavor = "%s %s" % (label_flavor, label_raw_flavor)
				min_value_flavor = leader_info_minimums[parsed_name_flavor]
				max_value_flavor = leader_info_maximums[parsed_name_flavor]
				compute_and_store_leader_info_cached_tuple(raw_value_flavor, min_value_flavor, max_value_flavor, b_invert_flavors, symbol_flavors, all_symbols, parsed_name_flavor, label_with_raw_value_flavor, iLeader, leader_info_cached)

			# <!-- custom: for contact fields, normalize the aggregated contact probs, do not normalize the rands nor the delays (would be redundant, as we don't display them with scale symbols or such, just the raw value in label is enough); to export raw fields (rand and delay, uncomment the related rand and delay lines below (untested but probably works-functions else tweak bit) to export them to UI if want to display them (then you'd need to uncomment or add if missing them in UI categories too)) -->
			# b_invert_contact_rands, b_invert_contact_delays = get_contact_rand_and_delay_invert_flags()
			# symbol_contact_rands_delays = all_symbols["RAW_SCALE_SYMBOL"]

			b_invert_4_aggregated_contact_probs = False
			symbol_aggregated_contact_probs = all_symbols["AGGREGATED_SCALE_SYMBOL"]
			for i in xrange(NUM_CONTACT_TYPES_ASSESSED):
				contact_type = gc.getContactTypes(i) # e.g. "CONTACT_JOIN_WAR"
				suffix = get_pascal_case_suffix(contact_type) # → "JoinWar"
				label_contact = contact_index_labels[i]

				# parsed_name_rand = "iContactRand%s" % suffix # → iContactRandJoinWar
				# raw_value_rand = loopLeaderHeadInfo.getContactRand(i)
				# label_raw_rand = "(%d)" % raw_value_rand
				# if IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD:
				# 	# <!-- custom: for these fields, the suffix like "Military" is much shorter than the parsed name like "iFlavorMilitary", and clear enough for our need for the labels as keys or suffixes, so use the suffix it instead of parsed name -->
				# 	label_with_raw_value_rand = get_labels_as_keys_or_suffixes_max_length_label(suffix, label_raw_rand, 19)
				# else:
				# 	label_with_raw_value_rand = "%s %s" % (label_contact, label_raw_rand)
				# min_value_rand = leader_info_minimums[parsed_name_rand]
				# max_value_rand = leader_info_maximums[parsed_name_rand]
				# compute_and_store_leader_info_cached_tuple(raw_value_rand, min_value_rand, max_value_rand, b_invert_contact_rands, symbol_contact_rands_delays, all_symbols, parsed_name_rand, label_with_raw_value_rand, iLeader, leader_info_cached)

				# parsed_name_delay = "iContactDelay%s" % suffix # → iContactDelayJoinWar
				# raw_value_delay = loopLeaderHeadInfo.getContactDelay(i)
				# min_value_delay = leader_info_minimums[parsed_name_delay]
				# max_value_delay = leader_info_maximums[parsed_name_delay]
				# label_raw_delay = "(%d)" % raw_value_delay
				# if IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD:
				# 	# <!-- custom: for these fields, the suffix like "Military" is much shorter than the parsed name like "iFlavorMilitary", and clear enough for our need for the labels as keys or suffixes, so use the suffix it instead of parsed name -->
				# 	label_with_raw_value_delay = get_labels_as_keys_or_suffixes_max_length_label(suffix, label_raw_delay, 19)
				# else:
				# 	label_with_raw_value_delay = "%s %s" % (label_contact, label_raw_delay)
				# compute_and_store_leader_info_cached_tuple(raw_value_delay, min_value_delay, max_value_delay, b_invert_contact_delays, symbol_contact_rands_delays, all_symbols, parsed_name_delay, label_with_raw_value_delay, iLeader, leader_info_cached)

				# <!-- custom: then back to aggregated contact fields, the ones that we display at least as of now , --> Fourth <!-- custom: actually third in sevopedia leader but named as such for consistency with generate_leaders_data.py pass numbering --> pass: normalize final scores
				# <!-- custom: now transform the raw aggregated prob into a normalized aggregated prob that we store and export for UI display -->
				parsed_name_4_aggregated_raw_contact_prob = "iAggregatedRawContactProb%s" % suffix # → iAggregatedRawContactProbJoinWar

				# <!-- custom: be careful/note: the normalized aggregated value is not stored in cache with the old pre-normalization key/parsed_name, so we remove "raw" here in key/parsed_name since aggregated value is normalized now, so use for caching the new key/parsed_name that does not have "raw" in key for aggregated fields at least for aggregated contact probs caching -->
				parsed_name_4_aggregated_contact_prob = "iAggregatedContactProb%s" % suffix # → iAggregatedContactProbJoinWar

				# <!-- custom: generate the label before normalizing, and so we also have the label as well for later display after normalization done in/at UI -->
				raw_value_rand = loopLeaderHeadInfo.getContactRand(i)
				raw_value_delay = loopLeaderHeadInfo.getContactDelay(i)
				# <!-- custom: do not display the raw aggregated prob here, but instead the raw rand and raw delay -->
				label_raw_rand_and_raw_delay = "(%d/%d)" % (raw_value_rand, raw_value_delay)
				if IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD:
					# <!-- custom: for these fields, the suffix like "Military" is much shorter than the parsed name like "iFlavorMilitary", and clear enough for our need for the labels as keys or suffixes, so use the suffix it instead of parsed name -->
					label_with_raw_value_rand_and_raw_value_delay = get_labels_as_keys_or_suffixes_max_length_label(suffix, label_raw_rand_and_raw_delay, 19)
				else:
					label_with_raw_value_rand_and_raw_value_delay = "%s %s" % (label_contact, label_raw_rand_and_raw_delay)

				# <!-- custom: be careful/note, min and max value are stored under the raw aggregated value and thus key, not the normalized aggregated one, use raw aggregated key to access them in leader_info minimums and same for maximums (normalized key does not exist yet, would get an error), similar reasoning to retrieve the previously stored raw aggregated value in leaders_info_aggregated_raw_contact_probs as well -->
				raw_value_4_aggregated_contact_prob = leaders_info_aggregated_raw_contact_probs[iLeader][parsed_name_4_aggregated_raw_contact_prob]
				min_value_4_aggregated_raw_contact_prob = leader_info_minimums[parsed_name_4_aggregated_raw_contact_prob]
				max_value_4_aggregated_raw_contact_prob = leader_info_maximums[parsed_name_4_aggregated_raw_contact_prob]

				# <!-- custom: note to chatgpt 5 or other AIs or readers xd: chatgpt 5 told me to change parsed_name_4_aggregated_contact_prob to parsed_name_4_aggregated_raw_contact_prob claiming it was a real bug, but doing it created an error ingame, and undoing it as it told me later solved the error. So i think or at least it seems like this is not a bug. Chatgpt 5 may have received a truncated prompt or something though as it mentionned ... in code which was not the case if i'm not mistaken; after i sent it an entire file as appended file rather, it told me to not do this change as this would cause an error if i'm not mistaken, so this is now reverted to how it was before and seems to run fine as such. I don't remember enough of the code to be sure, but it seems like this is as intended to use raw aggregated values in order to store normalized aggregated ones under a field name that does not use "raw" in it anymore as it is the normalized aggregated value we are storing and displaying in UI now, no longer the intermediate for calculations raw aggregated value if i'm not mistaken, but check to be sure; seems to run fine as such but check to be sure. Thanks for all help chatgpt 5 you helped me lot, confirmed current logic, and helped me find a nice performance optimization as of now with loopLeaderHeadInfo -->
				# Conclusion: it was not a bug in your code.
				# Your original line was correct:
				compute_and_store_leader_info_cached_tuple(raw_value_4_aggregated_contact_prob, min_value_4_aggregated_raw_contact_prob, max_value_4_aggregated_raw_contact_prob, b_invert_4_aggregated_contact_probs, symbol_aggregated_contact_probs, all_symbols, parsed_name_4_aggregated_contact_prob, label_with_raw_value_rand_and_raw_value_delay, iLeader, leader_info_cached)

			# <!-- custom: for memory fields, we display only aggregated positive/negative memory affections and resentments.
			# Raw attitude_percent/decay are already embedded in labels and are not normalized, so we don't display them separately.
			# We also skip positive memory resentments and negative memory affections because the table is too small and these would
			# overlap with positive memory affections / negative memory resentments given positive memories have positive attitude_percent
			# and negative memories have negative attitude_percent. They are also niche and would clutter the dump/cache; the pipeline
			# still supports them if you add their parsed_name fields to the UI category order below (test to be sure). (GPT-5.2-Codex (summarized)) -->
			# b_invert_memory_attitude_percents, b_invert_memory_decays = get_memory_attitude_percent_and_decay_invert_flags(is_positive, is_affection)
			#symbol_memory_attitude_percents_decays = all_symbols["RAW_SCALE_SYMBOL"]

			b_invert_4_positive_and_negative_memory_affections_and_resentments = False
			symbol_aggregated_positive_and_negative_memory_affections_and_resentments = all_symbols["AGGREGATED_SCALE_SYMBOL"]


			for is_positive in (True, False):
				for is_affection in (True, False):
					# <!-- custom: skip positive memory resentments and negative memory affections as said in top code comment before if i may say, uncomment or remove this/these checks to export them as well -->
					if is_positive and (not is_affection):
						continue
					if (not is_positive) and is_affection:
						continue

					positive_or_negative_memory_indexes = get_positive_or_negative_memory_indexes(is_positive)
					positive_negative = get_positive_negative(is_positive)
					affection_resentment = get_affection_resentment(is_affection)

					for i in positive_or_negative_memory_indexes:
						memory_type = gc.getMemoryInfo(i).getType() # e.g. "MEMORY_DECLARED_WAR"
						suffix = get_pascal_case_suffix(memory_type) # → "DeclaredWar"
						label_memory = positive_and_negative_memory_index_labels[i]

						# <!-- custom: for positive and negative memory affection and resentment fields, normalize the aggregated positive and negative memory affections and resentments, do not normalize the atittude percents nor the decays (would be redundant similarly as for contact fields) (also export of these raw fields (attitude percents and decays is untested as we don't need them at least untested as of now i meansimilarly to contact field, may or not function, i assume it would or with minimal tweaks or fixes if any are needed, plus would need to add UI logic or ordering to display them rather if want in another mod for example, unlikely we would in advciv-sas as redundant with aggregated fields as said before in this code comment too even though not 100% sure sure but most likely)) -->

						# <!-- custom: export raw attitude percents and decays only once out of the 4 combinations (among positive-affection, positive-resentment, negative-affection, negative-resentment), since the raw value is always the same field and field name, no need to do it again for the other 3 times/combinations -->
						# parsed_name_attitude_percent = "iMemoryAttitudePercent%s" % suffix # → iMemoryAttitudePercentDeclaredWar
						# if parsed_name_attitude_percent not in leader_info_cached:
						# 	raw_value_attitude_percent = loopLeaderHeadInfo.getMemoryAttitudePercent(i)
						# 	label_raw_attitude_percent = "(%d)" % raw_value_attitude_percent
						# 	if IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD:
						# 		# <!-- custom: for these fields, the suffix like "Military" is much shorter than the parsed name like "iFlavorMilitary", and clear enough for our need for the labels as keys or suffixes, so use the suffix it instead of parsed name -->
						# 		label_with_raw_value_attitude_percent = get_labels_as_keys_or_suffixes_max_length_label(suffix, label_raw_attitude_percent, 19)
						# 	else:
						# 		label_with_raw_value_attitude_percent = "%s %s" % (label_memory, label_raw_attitude_percent)
						# 	min_value_attitude_percent = leader_info_minimums[parsed_name_attitude_percent]
						# 	max_value_attitude_percent = leader_info_maximums[parsed_name_attitude_percent]
						# 	compute_and_store_leader_info_cached_tuple(raw_value_attitude_percent, min_value_attitude_percent, max_value_attitude_percent, b_invert_memory_attitude_percents, symbol_memory_attitude_percents_decays, all_symbols, parsed_name_attitude_percent, label_with_raw_value_attitude_percent, iLeader, leader_info_cached)

						# parsed_name_decay = "iMemoryDecay%s" % suffix # → iMemoryDecayDeclaredWar
						# if parsed_name_decay not in leader_info_cached:
						# 	raw_value_decay = loopLeaderHeadInfo.getMemoryDecayRand(i)
						# 	label_raw_decay = "(%d)" % raw_value_decay
						# 	if IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD:
						# 		# <!-- custom: for these fields, the suffix like "Military" is much shorter than the parsed name like "iFlavorMilitary", and clear enough for our need for the labels as keys or suffixes, so use the suffix it instead of parsed name -->
						# 		label_with_raw_value_decay = get_labels_as_keys_or_suffixes_max_length_label(suffix, label_raw_decay, 19)
						# 	else:
						# 		label_with_raw_value_decay = "%s %s" % (label_memory, label_raw_decay)
						# 	min_value_decay = leader_info_minimums[parsed_name_decay]
						# 	max_value_decay = leader_info_maximums[parsed_name_decay]
						# 	compute_and_store_leader_info_cached_tuple(raw_value_decay, min_value_decay, max_value_decay, b_invert_memory_decays, symbol_memory_attitude_percents_decays, all_symbols, parsed_name_decay, label_with_raw_value_decay, iLeader, leader_info_cached)

						# <!-- custom: then back to aggregated positive and negative memory affection and resentment fields, the ones that we display at least as of now , --> Fourth <!-- custom: actually third in sevopedia leader but named as such for consistency with generate_leaders_data.py pass numbering --> pass: normalize final scores
						# <!-- custom: now transform the raw aggregated prob into a normalized aggregated prob that we store and export for UI display -->
						# <!-- custom: note: unlike for min max exports (compute and store) of raw, we can do positive and negative memory affections and resentments aggregated normalization at same time without having to reloop over positive_or_negative_memory_indexes as the raw aggregated prob is now a flat field at this normalization stage, that is already available for all leaders, so we can normalize it directly and independently from the raw memory attitude percents and decays, see also min max code of memory fields at step 1 step 2 or similar code comments for details -->
						parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment = "iAggregatedRaw%sMemory%s%s" % (positive_negative, suffix, affection_resentment) # → iAggregatedRawPositiveMemoryDeclaredWarAffection or iAggregatedRawPositiveMemoryDeclaredWarResentment or iAggregatedRawNegativeMemoryDeclaredWarAffection or iAggregatedRawNegativeMemoryDeclaredWarResentment

						# <!-- custom: be careful/note: the normalized aggregated value is not stored in cache with the old pre-normalization key/parsed_name, so we remove "raw" here in key/parsed_name since aggregated value is normalized now, so use for caching the new key/parsed_name that does not have "raw" in key for aggregated fields at least for aggregated positive and negative memory affections and resentments caching -->
						parsed_name_4_aggregated_positive_or_negative_memory_affection_or_resentment = "iAggregated%sMemory%s%s" % (positive_negative, suffix, affection_resentment) # → iAggregatedPositiveMemoryDeclaredWarAffection or iAggregatedPositiveMemoryDeclaredWarResentment or iAggregatedNegativeMemoryDeclaredWarAffection or iAggregatedNegativeMemoryDeclaredWarResentment


						# <!-- custom: generate the label before normalizing, and so we also have the label as well for later display after normalization done in/at UI -->
						raw_value_4_attitude_percent = loopLeaderHeadInfo.getMemoryAttitudePercent(i)
						raw_value_4_decay = loopLeaderHeadInfo.getMemoryDecayRand(i)
						label_raw_attitude_percent_and_raw_decay = "(%d/%d)" % (raw_value_4_attitude_percent, raw_value_4_decay)
						if IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD:
							# <!-- custom: for these fields, the suffix like "Military" is much shorter than the parsed name like "iFlavorMilitary", and clear enough for our need for the labels as keys or suffixes, so use the suffix it instead of parsed name -->
							label_with_raw_value_rand_and_raw_value_delay = get_labels_as_keys_or_suffixes_max_length_label(suffix, label_raw_attitude_percent_and_raw_decay, 19)
						else:
							label_with_raw_value_rand_and_raw_value_delay = "%s %s" % (label_memory, label_raw_attitude_percent_and_raw_decay)

						# <!-- custom: be careful/note, min and max value are stored under the raw aggregated value and thus key, not the normalized aggregated one, use raw aggregated key to access them in leader_info minimums and same for maximums (normalized key does not exist yet, would get an error), similar reasoning to retrieve the previously stored raw aggregated value in leaders_info_aggregated_raw_contact_probs as well -->
						raw_value_4_aggregated_positive_or_negative_memory_affection_or_resentment = leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment]
						min_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment = leader_info_minimums[parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment]
						max_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment = leader_info_maximums[parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment]

						compute_and_store_leader_info_cached_tuple(raw_value_4_aggregated_positive_or_negative_memory_affection_or_resentment, min_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment, max_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment, b_invert_4_positive_and_negative_memory_affections_and_resentments, symbol_aggregated_positive_and_negative_memory_affections_and_resentments, all_symbols, parsed_name_4_aggregated_positive_or_negative_memory_affection_or_resentment, label_with_raw_value_rand_and_raw_value_delay, iLeader, leader_info_cached)

			b_invert_no_war_attitude_probs = False
			symbol_no_war_attitude_probs = all_symbols["RAW_SCALE_SYMBOL"]
			for i in xrange(NUM_ATTITUDE_TYPES_ASSESSED):
				attitude_type = gc.getAttitudeInfo(i).getType()  # e.g. "ATTITUDE_FURIOUS"
				suffix = get_pascal_case_suffix(attitude_type)  # → "Furious"
				parsed_name_no_war_attitude_prob = "iNoWarAttitudeProb%s" % suffix  # → iNoWarAttitudeProbFurious
				label_no_war_attitude_prob = suffix
				raw_value_no_war_attitude_prob = loopLeaderHeadInfo.getNoWarAttitudeProb(i)
				label_raw_no_war_attitude_prob = "(%d)" % raw_value_no_war_attitude_prob
				if IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD:
					# <!-- custom: for these fields, the suffix like "Military" is much shorter than the parsed name like "iFlavorMilitary", and clear enough for our need for the labels as keys or suffixes, so use the suffix it instead of parsed name -->
					label_with_raw_value_no_war_attitude_prob = get_labels_as_keys_or_suffixes_max_length_label(suffix, label_raw_no_war_attitude_prob, 19)
				else:
					label_with_raw_value_no_war_attitude_prob = "%s %s" % (label_no_war_attitude_prob, label_raw_no_war_attitude_prob)
				min_value_no_war_attitude_prob = leader_info_minimums[parsed_name_no_war_attitude_prob]
				max_value_no_war_attitude_prob = leader_info_maximums[parsed_name_no_war_attitude_prob]
				compute_and_store_leader_info_cached_tuple(raw_value_no_war_attitude_prob, min_value_no_war_attitude_prob, max_value_no_war_attitude_prob, b_invert_no_war_attitude_probs, symbol_no_war_attitude_probs, all_symbols, parsed_name_no_war_attitude_prob, label_with_raw_value_no_war_attitude_prob, iLeader, leader_info_cached)

			# <!-- custom: store final complete leader_info_cached (i.e. store a leader_info_cached for each iLeader) in LEADERS_INFO_CACHED -->
			LEADERS_INFO_CACHED[iLeader] = leader_info_cached
			if IS_DEBUG_LEADER:
				print(u"[DEBUG] Leader info cached for iLeader=%d is leader_info_cached=%s" % (iLeader, str(leader_info_cached)))

	compute_and_store_leaders_info_cached(leaders_info_aggregated_raw_contact_probs, leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, fields_with_direct_getters, fields_attitude_thresholds, leader_info_minimums, leader_info_maximums)

	# <!-- custom: cleanup -->
	del leaders_info_aggregated_raw_contact_probs
	del leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments
	del fields_with_direct_getters
	del fields_attitude_thresholds
	del leader_info_minimums
	del leader_info_maximums



	check_excluded_leaders_indexes_are_not_in_leaders_dict_keys(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS, LEADERS_INFO_CACHED, "LEADERS_INFO_CACHED")
	check_leaders_dict_only_has_leader_index_keys(LEADERS_INFO_CACHED, "LEADERS_INFO_CACHED")



	def get_ai_category_header_line_with_or_without_button_and_x_offset(icon_button_path_txt_key, ai_category_header, localText):
		if not IS_DISPLAY_AI_CATEGORY_HEADERS:
			return (None, 0)
		# If the header is disabled (None), keep the exact same "no header" tuple semantics.
		if ai_category_header is None:
			return (None, 0)

		if IS_DISPLAY_AI_CATEGORY_HEADER_EMOJI_BUTTONS and icon_button_path_txt_key:
			button_path = localText.getText(icon_button_path_txt_key, ())
			button_size = 16
			line_button_txt = u"<img=%s size=%s></img>" % (button_path, str(button_size))
			ai_category_header_line_with_button = u"%s <font=3b>%s</font>" % (line_button_txt, ai_category_header)

			# <!-- custom: add x offset (negative) so we can push button a bit left and reduce whitespace -->
			ai_category_x_offset_with_button = -7

			return (ai_category_header_line_with_button, ai_category_x_offset_with_button)
		else:
			ai_category_header_line_without_button = u"<font=3b>%s</font>" % ai_category_header
			ai_category_x_offset_without_button = 0

			return (ai_category_header_line_without_button, ai_category_x_offset_without_button)

	def get_ai_category(icon_button_path_txt_key, ai_category_header, ai_category_key_order, localText):
		ai_category_header_line, ai_category_x_offset = get_ai_category_header_line_with_or_without_button_and_x_offset(
			icon_button_path_txt_key,
			ai_category_header,
			localText
		)

		return (ai_category_header_line, ai_category_x_offset, ai_category_key_order)

	def get_ai_category_order_positive_memory_affections_or_resentments(positive_negative, affection_resentment):
		ai_category_key_order_positive_memories = (
			"iAggregated%sMemoryGiveHelp%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryAcceptDemand%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryAcceptedReligion%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryAcceptedCivic%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryAcceptedJoinWar%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryAcceptedStopTrading%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryVotedForUs%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryEventGoodToUs%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryLiberatedCities%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryIndependence%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryTradedTechToUs%s" % (positive_negative, affection_resentment),
		)

		return ai_category_key_order_positive_memories



	def get_ai_category_order_negative_memory_affections_or_resentments(positive_negative, affection_resentment):
		ai_category_key_order_negative_memories = (
			"iAggregated%sMemoryDeclaredWar%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryDeclaredWarOnFriend%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryHiredWarAlly%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryNukedUs%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryNukedFriend%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryRazedCity%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryRazedHolyCity%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemorySpyCaught%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryRefusedHelp%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryRejectedDemand%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryDeniedReligion%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryDeniedCivic%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryDeniedJoinWar%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryDeniedStopTrading%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryStoppedTrading%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryHiredTradeEmbargo%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryMadeDemand%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryVotedAgainstUs%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryEventBadToUs%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryCancelledVassalAgreement%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryDeclaredWarRecent%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryReceivedTechFromAny%s" % (positive_negative, affection_resentment),
			# <!-- custom: hide this one because we don't have enough space in the table. (GPT-5.2-Codex (summarized)) -->
			# "iAggregated%sMemoryStoppedTradingRecent%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryMadeDemandRecent%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryCancelledOpenBorders%s" % (positive_negative, affection_resentment),
			"iAggregated%sMemoryCancelledDefensivePact%s" % (positive_negative, affection_resentment),
		)

		return ai_category_key_order_negative_memories


	def get_ai_category_order_contact_probs(is_offer):
		if is_offer:
			return (
				"iAggregatedContactProbPeaceTreaty",
				"iAggregatedContactProbOpenBorders",
				"iAggregatedContactProbTradeMap",
				"iAggregatedContactProbTradeTech",
				"iAggregatedContactProbTradeBonus",
				"iAggregatedContactProbGiveHelp",
				"iAggregatedContactProbDefensivePact",
				"iAggregatedContactProbPermanentAlliance",
			)
		return (
			"iAggregatedContactProbReligionPressure",
			"iAggregatedContactProbCivicPressure",
			"iAggregatedContactProbStopTrading",
			"iAggregatedContactProbDemandTribute",
			"iAggregatedContactProbAskForHelp",
			"iAggregatedContactProbJoinWar",
		)

	def get_ai_category_order_refusal_thresholds(is_offer):
		if is_offer:
			return (
				"getOpenBordersRefuseAttitudeThreshold",
				"getMapRefuseAttitudeThreshold",
				"getTechRefuseAttitudeThreshold",
				"getStrategicBonusRefuseAttitudeThreshold",
				"getHappinessBonusRefuseAttitudeThreshold",
				"getHealthBonusRefuseAttitudeThreshold",
				"getNoGiveHelpAttitudeThreshold",
				"getDefensivePactRefuseAttitudeThreshold",
			)
		return (
			"getConvertReligionRefuseAttitudeThreshold",
			"getAdoptCivicRefuseAttitudeThreshold",
			# <!-- custom: probability to refuse declaring war based on attitude (higher = less likely to attack). (GPT-5.2-Codex) -->
			"getDeclareWarRefuseAttitudeThreshold",
			"getDeclareWarThemRefuseAttitudeThreshold",
			"getStopTradingRefuseAttitudeThreshold",
			"getStopTradingThemRefuseAttitudeThreshold",
			"getDemandTributeAttitudeThreshold",
			"getCityRefuseAttitudeThreshold",
			"getNativeCityRefuseAttitudeThreshold",
			"getVassalRefuseAttitudeThreshold",
		)

	def get_ai_category_order_war_strategy():
		return (
			"getMaxWarRand",
			"getMaxWarNearbyPowerRatio",
			"getMaxWarDistantPowerRatio",
			"getMaxWarMinAdjacentLandPercent",
			"getLimitedWarRand",
			"getLimitedWarPowerRatio",
			"getBaseAttackOddsChange",
			"getAttackOddsChangeRand",
			"getRazeCityProb",
			"getDemandRebukedSneakProb",
			"getDemandRebukedWarProb",
			"getDogpileWarRand",
			"getDeclareWarTradeRand",
			# <!-- custom: not ideal but keep this ACL here so War Strategy stays in one block and fits the panel. (GPT-5.2-Codex) -->
			"getShareWarAttitudeChangeLimit",
			"getVassalPowerModifier",
			"getRefuseToTalkWarThreshold",
			"getMakePeaceRand",
		)

	def get_ai_category_order_core_personality():
		# <!-- custom: order is tuned to fit the panel; not strictly thematic (e.g., some ACL fields stay here) to keep
		# headers readable within the available space. (GPT-5.2-Codex) -->
		return (
			"getBaseAttitude",
			"getBasePeaceWeight",
			"getPeaceWeightRand",
			"getWorseRankDifferenceAttitudeChange",
			"getBetterRankDifferenceAttitudeChange",
			"getWarmongerRespect",
			"getCloseBordersAttitudeChange",
			# <!-- custom: table is tight, so keep ACL fields here to avoid another header. (GPT-5.2-Codex) -->
			"getSameReligionAttitudeChangeLimit",
			"getDifferentReligionAttitudeChangeLimit",
			"getFavoriteCivicAttitudeChangeLimit",
		)

	def get_ai_category_order_victory_weights():
		return (
			"getConquestVictoryWeight",
			"getDominationVictoryWeight",
			"getCultureVictoryWeight",
			"getDiplomacyVictoryWeight",
			"getSpaceVictoryWeight",
		)

	def get_ai_category_order_flavors():
		return (
			"iFlavorMilitary",
			"iFlavorReligion",
			"iFlavorProduction",
			"iFlavorGold",
			"iFlavorScience",
			"iFlavorCulture",
			"iFlavorGrowth",
			"iFlavorEspionage",
		)

	def get_ai_category_order_economic_preferences():
		return (
			"getMaxGoldTradePercent",
			"getMaxGoldPerTurnTradePercent",
			"getTechTradeKnownPercent",
			"getNoTechTradeThreshold",
			"getBuildUnitProb",
			"getWonderConstructRand",
			"getEspionageWeight",
		)

	def get_ai_category_order_no_war_at():
		return (
			"iNoWarAttitudeProbFurious",
			"iNoWarAttitudeProbAnnoyed",
			"iNoWarAttitudeProbCautious",
			"iNoWarAttitudeProbPleased",
			"iNoWarAttitudeProbFriendly",
		)

	def get_ai_category_order_attitude_changes():
		return (
			"getSameReligionAttitudeChange",
			"getSameReligionAttitudeDivisor",
			"getDifferentReligionAttitudeChange",
			"getDifferentReligionAttitudeDivisor",
			"getFavoriteCivicAttitudeChange",
			"getFavoriteCivicAttitudeDivisor",
			"getLostWarAttitudeChange",
			"getAtWarAttitudeDivisor",
			"getAtWarAttitudeChangeLimit",
			"getAtPeaceAttitudeDivisor",
			"getAtPeaceAttitudeChangeLimit",
			"getShareWarAttitudeChange",
			"getShareWarAttitudeDivisor",
			"getBonusTradeAttitudeDivisor",
			"getBonusTradeAttitudeChangeLimit",
			"getOpenBordersAttitudeDivisor",
			"getOpenBordersAttitudeChangeLimit",
			"getDefensivePactAttitudeDivisor",
			"getDefensivePactAttitudeChangeLimit",
		)

	def get_ai_category_order_misc_modifiers():
		return ("getFreedomAppreciation",)


	# <!-- custom: Python 2.4 global lookup is brittle; keep these helper names stable to avoid NameError at runtime when refactoring. (GPT-5.2-Codex) -->
	def get_ai_categories(localText):
		def get_header_text(header_key_or_text):
			if header_key_or_text is None:
				return None
			if header_key_or_text.startswith("TXT_KEY_"):
				return localText.getText(header_key_or_text, ())
			return header_key_or_text

		# === AI Panel's Categories (display order) ===
		# Note: icon_button_path_txt_key values are TXT_KEYs that resolve (via localText) to an image path.
		# We keep them local here for clarity and to avoid any global "emoji mapping" state.

		right_defs = (
			# <!-- custom: Economic Preferences. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_MONEY_BAG_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_ECONOMIC_PREFERENCES", get_ai_category_order_economic_preferences()),
			# <!-- custom: Contact Offer Probabilities. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_DOVE_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_CONTACT_OFFER_PROBABILITIES", get_ai_category_order_contact_probs(True)),
			# <!-- custom: Contact Demand Probabilities. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_MEGAPHONE_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_CONTACT_DEMAND_PROBABILITIES", get_ai_category_order_contact_probs(False)),
			# <!-- custom: Offer Refuse Attitude Thresholds. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_NO_ENTRY_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_REFUSAL_THRESHOLDS_OFFER", get_ai_category_order_refusal_thresholds(True)),
			# <!-- custom: Demand Refuse Attitude Thresholds. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_AXE_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_REFUSAL_THRESHOLDS_DEMAND", get_ai_category_order_refusal_thresholds(False)),
			# <!-- custom: Misc Modifiers. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_WRENCH_PATH", "TXT_KEY_LEADER_AI_PANEL_MISC_MODIFIERS", get_ai_category_order_misc_modifiers()),
		)

		middle_defs = (
			# <!-- custom: Positive Memory Affections. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_RED_HEART_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_POSITIVE_MEMORY_AFFECTIONS", get_ai_category_order_positive_memory_affections_or_resentments("Positive", "Affection")),
			# <!-- custom: Negative Memory Resentments. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_SKULL_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_NEGATIVE_MEMORY_RESENTMENTS", get_ai_category_order_negative_memory_affections_or_resentments("Negative", "Resentment")),
			# <!-- custom: No War At. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_HERB_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_NO_WAR_AT", get_ai_category_order_no_war_at()),
			# <!-- custom: Attitude Changes +/- Lims +/- Divs. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_CHART_DECREASING_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_ATTITUDE_CHANGES", get_ai_category_order_attitude_changes()),
		)

		left_defs = (
			# <!-- custom: Core Personality. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_BRAIN_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_CORE_PERSONALITY", get_ai_category_order_core_personality()),
			# <!-- custom: Victory Weights (BBAI-style). (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_TROPHY_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_BBAI_VICTORY_WEIGHTS", get_ai_category_order_victory_weights()),
			# <!-- custom: Flavors. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_GEAR_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_FLAVORS", get_ai_category_order_flavors()),
			# <!-- custom: War Strategy. (GPT-5.2-Codex) -->
			("TXT_KEY_IMAGE_AS_BUTTON_CROSSED_SWORDS_BUTTON_PATH", "TXT_KEY_LEADER_AI_PANEL_WAR_STRATEGY", get_ai_category_order_war_strategy()),
		)

		right_categories = []
		middle_categories = []
		left_categories = []

		if IS_DISPLAY_AI_CATEGORY_HEADERS:
			for icon_button_path_txt_key, header_key_or_text, ai_category_key_order in right_defs:
				right_categories.append(get_ai_category(icon_button_path_txt_key, get_header_text(header_key_or_text), ai_category_key_order, localText))
			for icon_button_path_txt_key, header_key_or_text, ai_category_key_order in middle_defs:
				middle_categories.append(get_ai_category(icon_button_path_txt_key, get_header_text(header_key_or_text), ai_category_key_order, localText))
			for icon_button_path_txt_key, header_key_or_text, ai_category_key_order in left_defs:
				left_categories.append(get_ai_category(icon_button_path_txt_key, get_header_text(header_key_or_text), ai_category_key_order, localText))
		else:
			for icon_button_path_txt_key, header_key_or_text, ai_category_key_order in right_defs:
				right_categories.append(get_ai_category(None, None, ai_category_key_order, localText))
			for icon_button_path_txt_key, header_key_or_text, ai_category_key_order in middle_defs:
				middle_categories.append(get_ai_category(None, None, ai_category_key_order, localText))
			for icon_button_path_txt_key, header_key_or_text, ai_category_key_order in left_defs:
				left_categories.append(get_ai_category(None, None, ai_category_key_order, localText))

		return (tuple(right_categories), tuple(middle_categories), tuple(left_categories))

	# === AI Panel's Categories ===
	AI_RIGHT_CATEGORIES, AI_MIDDLE_CATEGORIES, AI_LEFT_CATEGORIES = get_ai_categories(localText)

	# <!-- custom: final return. Note that this caching, while/even though it is done in sevopedia leader, is triggered from sevopedia main's placeLeaders, after module load, so that we cache (or load the precomputed cache) only once just at the right time when it is computationally the cheapest for players if i'm not mistaken in SevoPediaMain 's placeLeaders. -->
	# <!-- custom: also print the debug line below regardless of debug flag status, we really want to know this info and it is short -->
	print("[DEBUG] Sevopedia Leader cache prebuilt by Sevopedia Leader's getPrecomputedCacheOnceOnlyFromSevopediaMainInSevopediaLeaderForEntireSession() which if it was called, should cause this message to appear only once for the entire game session (i.e. since civ4 was launched), even if we browse another category or exit sevopedia.")

	return LEADERS_INFO_CACHED, AI_RIGHT_CATEGORIES, AI_MIDDLE_CATEGORIES, AI_LEFT_CATEGORIES



def getPrecomputedCacheOnceOnlyFromSevopediaMainInSevopediaLeaderForEntireSession():
	# Wrapper that either loads pre-dumped cache or computes it
	return get_leader_cache_predumped_or_compute(
		compute_func = _compute_leader_cache_internal,
		excluded_leader_types = EXCLUDED_LEADER_TYPES_FROM_CALCULATIONS,
		is_emoji_enabled = IS_DISPLAY_AI_CATEGORY_HEADER_EMOJI_BUTTONS,
		is_raw_xml_names = IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD
	)



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
		# - in sevopedia (before my fix): 421 x 488 	(ratio: 0,8627)     ;    (reverse-ratio: 1,1591)
		# - ingame diplomacy: 709 x 866 				(ratio: 0,8187)     ;    (reverse-ratio: 1,1214)
		# (extracted from the more detailed notes in modding ressources's readme about art design, please look at it or the filename containing these note samples or similar for details)
		#
		# Since the value (ratio in particular is different than what i measured (0,8627 vs 0,8278 here, i will try to adjust it based on that to hopefully have a matching ratio or a bit better or more or not, anyways, )) (while also increasing the portrait/picture which i think is a bit small currently, maybe more immersive or pleasant or not, anyways, )
		# Now ratio is 287 / 350 = 0,8200 (much closer to 0,8187 that i measured in game diplomacy (see above, anyways), while also increasing size (of the portrait anyways) anyways)
		#
		# This looks good but i want to try to increase it more (portrait size, anyways, ):
		# Now 327 / 400 = 0,8175 (which is very close to 0,8187 while also a bigger picture, anyways)
		# Increasing it more is maybe possible but we start to see the pixels in the animations (see Gandhi's arm) not being straight for example, if we replace animations with images like with/for Ewuare (Kingdom of Benin, anyways) then hese enhanced portaits would be better and more epic, will see if i increase it more or not, maybe leaving as is at least for now or not, anyways,
		#
		# Actually all this calculation is not exactly accurate because W_LEADERHEAD_PANE and W_LEADERHEAD are different in this base advciv / sevopedia(?) code, but hopefully accurate enough and ratio should be much closer now to the ingame diplomacy ratio, hopefully less stretched but not sure or guaranteed, should be for images i send as replacements of animations though as i base them on the ingame diplomacy's ratio, not the old sevopedia leader portait ratio, anyways, so now the new sevopedia ratio for the leader portrait i have added is hopefully much much closer to the old and as of now still existing ratio of the ingame diplomacy leader portrait, which i don't think i'm changing anytime soon as it is most likely more tedious for questionable gain, so using this one as a basis rather, not that is undoable but probably much harder and not necessarily worth it, and if animations are based on the diplomacy ingame ratio rather then they may also display better in the sevopedia with my new sevopedia ratio, (which intuitively or from a quick glance seems to be the case, image looks less compressed on its sides but not sure or guaranteed, check yourself if want to be sure or not, but i hope this helps, and that being said, anyways) anyways -->
		#
		self.W_LEADERHEAD_PANE = 327
		self.H_LEADERHEAD_PANE = 400

		# <!-- custom:
		# 1) (most) absolute dimensions first -->

		# <!-- custom: make room to add AI personality panel -->
		self.W_AI_PERSONALITY = 290

		self.SMALL_MARGIN = 10
		self.MEDIUM_MARGIN = 20
		# <!-- custom: we also need this information sooner, move it here with the more absolute dimensions of some elements
		self.W_CIV = 64
		self.H_CIV = 64
		self.CIV_MARGIN = 0
		self.CIV_DISELEVATION = 38
		
		self.H_FAVORITES = 110
		self.N_AI_TABLE_NUM = 3

		# <!-- custom:
		# 2) (most) relative dimensions or positions then -->

		self.W_LEADERHEAD = self.W_LEADERHEAD_PANE - 30
		self.H_LEADERHEAD = self.H_LEADERHEAD_PANE - 34
		self.X_LEADERHEAD = self.X_LEADERHEAD_PANE + (self.W_LEADERHEAD_PANE - self.W_LEADERHEAD) / 2
		self.Y_LEADERHEAD = self.Y_LEADERHEAD_PANE + (self.H_LEADERHEAD_PANE - self.H_LEADERHEAD) / 2 + 3

		self.W_AI_TOTAL_TABLES_WIDTH = self.N_AI_TABLE_NUM * self.W_AI_PERSONALITY + self.N_AI_TABLE_NUM * self.MEDIUM_MARGIN

		self.Y_FAVORITES = self.Y_LEADERHEAD_PANE + self.H_LEADERHEAD_PANE + self.SMALL_MARGIN

		# <!-- custom: we need self.W_HISTORY before the favourites coordinates, (even though the history panel is placed under/after the favourites panel when i constructed the page's "spacing" and dimensions of (and between) panels, anyways) because/as the favourites panel uses/needs/is based on the history panel's (relative) position, anyways -->
		# <!-- custom: might as well put the other/rest/remaining HISTORY coordinates if doesn't harm and they are perhaps needed too, anyways -->
		self.X_HISTORY = self.X_LEADERHEAD_PANE
		self.Y_HISTORY = self.Y_FAVORITES + self.H_FAVORITES + self.SMALL_MARGIN
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.W_AI_TOTAL_TABLES_WIDTH - self.X_LEADERHEAD_PANE
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY

		self.X_FAVORITES = self.X_LEADERHEAD_PANE
		self.W_FAVORITES = self.W_HISTORY - self.W_CIV - self.SMALL_MARGIN

		# <!-- custom: the rest of the coordinates here, as it is dependent on other coordinates we need first that (i.e. before being able to add these) -->
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
		# <!-- custom: removing or rather having an empty header, the header disappears entirely, but if you want to use a header, you can just type any value in the related txt keys such as TXT_KEY_AI_PERSONALITY_RIGHT_PANEL and such anyways. This or maybe rather not doing this (having an non-empty txt key header) would take some room though so you'd have to adjust self.H_AI_UPPER_PADDING to the value below commented-out or simialr depending the upper padding you want.
		# Since i (accidentally found) it frees more room, i want to try using it as such, as i really need the extra room, and not so much the header name (the other two header txt keys were going to be either redunant naming or empty so maybe this is (also) a good opportunity to gain space/room in the ai personality panel, anyways -->
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

		# <!-- custom: move the civ (flag) closer to favourite civis and religions or somewhere else, more beautiful and less cumbersome this way maybe i think, anyways -->
		self.X_CIV = self.X_HISTORY + self.W_HISTORY - self.CIV_MARGIN - self.W_CIV
		# <!-- custom: put the flag/civ at the middle Y of the favourites panel -->
		# <!-- custom: quite high as compared to favourites panel's lowest point -->
		self.Y_CIV = self.Y_FAVORITES + self.CIV_DISELEVATION



	def interfaceScreen(self, iLeader):
		self.iLeader = iLeader

		# <!-- custom: change call order to match filling/building order, generally from top left to bottom and left to right but not always, reordering in such a way is maybe a bit more intuitive this way perhaps or clearer or helpful or not or other etc anyways, -->
		self.placeLeaderHeadPane()
		self.placeFavorites()
		self.placeHistory()
		self.placeCiv()
		self.placeTraits()

		# <!-- custom: for excluded leader indexes from calculations, leave the zone/space where the AI personality panel was supposed to be especially empty, instead of getting a key error or missing leader from leaders_info_cached (but we still want the excluded leaders to be excluded from computation as it could and most likely will most often if not always affect the ranking and scores normalized of other leaders with this additional item
		# This is especially useful for iLeader of LEADER_BARBARIAN (iLeader 0 at least as of now if i'm not mistaken) in particular that is somehow accessible in the sevopedia civilization category from the barbarian civ (which is also useful because we now display their city names for example, see sevopedia civilization for details about how we place city names in it now) -->
		#
		if (iLeader not in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS):
			self.placeAIPersonalityPanel(iLeader)
		else:
			if IS_DEBUG_LEADER:
				print("[DEBUG] Leader index iLeader=%d in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS=%s is skipped, leave the place where AI Personality panel was supposed to be entirely empty so we don't get a missing key in leaders_info_cached Error, while signifying clearly enough hopefully that the excluded leader currently selected doesn't have an item in leaders_info_cached and AI Personality Panel at all/is not part of it." % (iLeader, str(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS)))



	# <!-- custom: wrap leader placement in a specific function for clarity or flexibility or not anyways, -->
	def placeLeaderHeadPane(self):
		screen = self.top.getScreen()
		leaderPanelWidget = self.top.getNextWidgetName()
		screen.addPanel(leaderPanelWidget, "", "", True, True, self.X_LEADERHEAD_PANE, self.Y_LEADERHEAD_PANE, self.W_LEADERHEAD_PANE, self.H_LEADERHEAD_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		self.leaderWidget = self.top.getNextWidgetName()
		screen.addLeaderheadGFC(self.leaderWidget, self.iLeader, AttitudeTypes.ATTITUDE_PLEASED, self.X_LEADERHEAD, self.Y_LEADERHEAD, self.W_LEADERHEAD, self.H_LEADERHEAD, WidgetTypes.WIDGET_GENERAL, -1, -1)



	# <!-- custom: imported from RFC DOC (C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\RFC Dawn of Civilization\Assets\Python\Pedia\CvPediaLeader.py) and modified or not for AdvCiv-SAS. -->
	def placeFavorites(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		screen.addPanel(panel, localText.getText("TXT_KEY_PEDIA_FAVOURITE_CIVICS_AND_RELIGIONS", ()), "", False, True, self.X_FAVORITES, self.Y_FAVORITES, self.W_FAVORITES, self.H_FAVORITES, PanelStyles.PANEL_STYLE_BLUE50)
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
		for iCiv in xrange(gc.getNumCivilizationInfos()):
			civ = gc.getCivilizationInfo(iCiv)
			if civ.isLeaders(self.iLeader):
				screen.setImageButton(self.top.getNextWidgetName(), civ.getButton(), self.X_CIV, self.Y_CIV, self.W_CIV, self.H_CIV, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCiv, 1)



	# advc.001 (from Taurus): Static for use by SevoPediaMain; body cut from placeTraits.
	@staticmethod
	def getCiv(iLeader):
		iNumCivs = 0
		for iCiv in xrange(gc.getNumCivilizationInfos()):
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
		# <!-- custom: no header for more compact and prettier display -->
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_LEADER_TRAITS", ()), "", True, False, self.X_TRAITS, self.Y_TRAITS, self.W_TRAITS, self.H_TRAITS, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		# advc.001: Civ search moved into a static method
		szSpecialText = CyGameTextMgr().parseLeaderTraits(self.iLeader, SevoPediaLeader.getCiv(self.iLeader), False, True)
		szSpecialText = szSpecialText[1:]

		# <!-- custom: add trait icons by replacing the trait header text once per leader trait (linked or plain); avoids per-line scans and keeps only traits the leader actually has. (GPT-5.2-Codex) -->
		if IS_SHOW_TRAIT_ICONS_IN_LEADER:
			leader = gc.getLeaderHeadInfo(self.iLeader)
			for iTrait in xrange(gc.getNumTraitInfos()):
				if leader.hasTrait(iTrait):
					traitDesc = gc.getTraitInfo(iTrait).getDescription()
					traitLink = u"<link=literal>%s</link>" % traitDesc
					traitIcon = TraitUtil.getIcon(iTrait)
					# <!-- custom: prefer replacing the linked trait label; if traits are plain text, replace the first matching trait name only. (GPT-5.2-Codex) -->
					szReplaced = szSpecialText.replace(traitLink, traitIcon + u" " + traitLink)
					if szReplaced == szSpecialText:
						szSpecialText = szSpecialText.replace(traitDesc, traitIcon + u" " + traitDesc, 1)
					else:
						szSpecialText = szReplaced

		# <!-- custom: reduce top padding now that the traits header is removed (GPT-5.2-Codex). Was headerExtraHeight 30 -->
		headerExtraHeight = 10
		screen.addMultilineText(listName, szSpecialText, self.X_TRAITS + 5, self.Y_TRAITS + headerExtraHeight, self.W_TRAITS - 10, self.H_TRAITS - headerExtraHeight - 5, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def getXAIPanelCoordinate(self, tableId):
		return self.X_AI_PERSONALITY - tableId * self.W_AI_PERSONALITY - tableId * self.MEDIUM_MARGIN



	def setupAIPanel(self, screen, txtKey, xPanel):
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName,localText.getText(txtKey, ()),"", True, True, xPanel, self.Y_AI_PERSONALITY, self.W_AI_PERSONALITY, self.H_AI_PERSONALITY, PanelStyles.PANEL_STYLE_BLUE50)



	def fillAITableRow(self, screen, label, value, scale, xLabel, xValue, xScale, y):
		labelText = u"<font=2>%s</font>" % label
		valueText = u"<font=2b>%d</font>" % value
		scaleText = u"<font=2>%s</font>" % scale

		screen.setText(self.top.getNextWidgetName(), "", labelText, CvUtil.FONT_LEFT_JUSTIFY, xLabel, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText(self.top.getNextWidgetName(), "", valueText, CvUtil.FONT_LEFT_JUSTIFY, xValue, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText(self.top.getNextWidgetName(), "", scaleText, CvUtil.FONT_LEFT_JUSTIFY, xScale, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)



	def renderAICategories(self, screen, ai_categories, xPanel, yPanel, leader_info_cached):
		xLabel = xPanel + self.W_AI_LEFT_SIDE_PADDING
		xValue = xLabel + self.W_AI_LABEL
		xScale = xValue + self.W_AI_VALUE
		y = yPanel + self.H_AI_UPPER_PADDING

		for ai_category in ai_categories:
			ai_category_header_line, ai_category_x_offset, ai_category_key_order = ai_category

			# --- AI Category Header Line ---
			if ai_category_header_line is not None:
				xOffsetButton = xLabel + ai_category_x_offset
				screen.setText(self.top.getNextWidgetName(), "", ai_category_header_line, CvUtil.FONT_LEFT_JUSTIFY, xOffsetButton, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				y += self.H_AI_LINE_HEIGHT

			# <!-- custom: AI Category items in their predefined order -->
			for key in ai_category_key_order:
				label, norm_value, scale = leader_info_cached[key]
				self.fillAITableRow(screen, label, norm_value, scale, xLabel, xValue, xScale, y)
				y += self.H_AI_LINE_HEIGHT

			# <!-- custom: space for next ai_category if any are there (else still space but not used more efficient this way i think i mean than rechecking each time and we have some tables that overflow vertically too so maybe fine this way too if not broken in this case i mean maybe-->
			y += self.H_AI_CATEGORY_SPACING



	# --- Place AI Personality Panel (using precomputed scales) ---
	# Renders the full AI Personality panel in the Sevopedia Leader page using precomputed <!-- custom: leader info tuples in leaders_info_cached --> for the given leader.
	def placeAIPersonalityPanel(self, iLeader):
		screen = self.top.getScreen()

		xPanelRight = self.getXAIPanelCoordinate(self.N_AI_TABLE_NUM - 3)
		xPanelMiddle = self.getXAIPanelCoordinate(self.N_AI_TABLE_NUM - 2)
		xPanelLeft = self.getXAIPanelCoordinate(self.N_AI_TABLE_NUM - 1)

		self.setupAIPanel(screen, self.AI_PANEL_RIGHT_TXT_KEY, xPanelRight)
		self.setupAIPanel(screen, self.AI_PANEL_MIDDLE_TXT_KEY, xPanelMiddle)
		self.setupAIPanel(screen, self.AI_PANEL_LEFT_TXT_KEY, xPanelLeft)

		# <!-- custom: cache for performance optimization. -->
		leader_info_cached = LEADERS_INFO_CACHED[iLeader]

		self.renderAICategories(screen, AI_RIGHT_CATEGORIES, xPanelRight, self.Y_AI_PERSONALITY, leader_info_cached)
		self.renderAICategories(screen, AI_MIDDLE_CATEGORIES, xPanelMiddle, self.Y_AI_PERSONALITY, leader_info_cached)
		self.renderAICategories(screen, AI_LEFT_CATEGORIES, xPanelLeft, self.Y_AI_PERSONALITY, leader_info_cached)



	def handleInput (self, inputClass):
		# <!-- custom: leaderhead hotkeys (animations/moods) are cosmetic; if they conflict with search,
		# consider removing or remapping here. (GPT-5.2-Codex) -->
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


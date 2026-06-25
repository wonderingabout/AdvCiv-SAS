# AI Utilities or Personality Panel for normalization and general helpers for the Sevopedia Leader category
# Extracted from SevoPediaLeader.py to keep that file lean (AdvCiv-SAS).
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# <!-- custom: Long_Comments_py.txt #3 -->

from CvPythonExtensions import *
import sys

from ai_utils_shared_with_civ4 import *
from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD = (gc.getDefineINT("SAS_SEVOPEDIA_LEADER_AI_PERSONALITY_PANEL_SHOW_RAW_XML_FIELD_NAMES_INSTEAD") > 0)

# <!-- custom: Long_Comments_py.txt #8 -->
IS_DEBUG_LEADER = False

# <!-- custom: we already warn once if min == max at/in get_leader_info_minimums_and_maximums, no need to warn again and again i mean at each normalization, so set B_WARN to false -->
B_WARN = False

if IS_DEBUG_LEADER:
	print("[DEBUG] Leaders index to type is: %s" % str(get_leaders_index_to_type_map()))

# <!-- custom: Use the AIP-specific exclusion list shared with the workflow predump checker, not the broader Sevopedia leader/civ association exclusion list. (ChatGPT-5.5) -->
AIP_EXCLUDED_LEADER_TYPES = get_aip_excluded_leader_types()
EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS = get_excluded_leader_indexes(AIP_EXCLUDED_LEADER_TYPES)

# <!-- custom: more consistently and reliably exclude leaders by having a ready list of such leaders we can call -->
if IS_DEBUG_LEADER:
	print("[DEBUG] EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS=%s" % str(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS))

# <!-- custom: Long_Comments_py.txt #12 -->
IS_USE_PREDUMPED_CACHE = (gc.getDefineINT("SAS_SEVOPEDIA_LEADER_AI_PERSONALITY_CACHE_USE_PREDUMPED") > 0)
IS_DUMP_CACHE_TO_LOG = (gc.getDefineINT("SAS_SEVOPEDIA_LEADER_AI_PERSONALITY_CACHE_DUMP_TO_LOG") > 0)
# Name of the pre-dumped module (without .py extension)
PREDUMPED_MODULE_NAME = "SevoPediaLeaderCachePredumped"

def dump_leader_cache_to_pythondbg(leaders_info_cached, excluded_leader_types, is_emoji_enabled, is_raw_xml_names):
	# Dumps the leader cache to PythonDbg.log in a format that can be copy-pasted into a .py module file.
	def emit(line):
		sys.stdout.write("%s\n" % line)
	leader_index_type_pairs = []
	for iLeader in xrange(gc.getNumLeaderHeadInfos()):
		leader_type = gc.getLeaderHeadInfo(iLeader).getType()
		leader_index_type_pairs.append("%d: %s" % (iLeader, leader_type))
	leader_index_type_line = ", ".join(leader_index_type_pairs)

	# BEGIN marker
	emit("# === SAS_LEADER_AI_CACHE_PYMODULE_BEGIN ===")

	# Header with generation info
	emit("# Generated from in-game dump to PythonDbg.log")
	emit("# Copy this entire block (from BEGIN to END) into: %s.py" % PREDUMPED_MODULE_NAME)
	emit("#")
	emit("# Generation info:")
	emit("#   - Number of leaders (gc.getNumLeaderHeadInfos): %d" % gc.getNumLeaderHeadInfos())
	emit("#   - Excluded leader types: %r" % (excluded_leader_types,))
	emit("#   - Leader index:type pairs: %s" % leader_index_type_line)
	emit("#   - Emoji headers enabled: %s" % str(is_emoji_enabled))
	emit("#   - Raw XML field names: %s" % str(is_raw_xml_names))

	# The actual data
	emit("LEADERS_INFO_CACHED = {")
	for iLeader in sorted(leaders_info_cached.keys()):
		emit("	%r: {" % iLeader)
		leader_info_cached = leaders_info_cached[iLeader]
		for cache_key in sorted(leader_info_cached.keys()):
			emit("		%r: %r," % (cache_key, leader_info_cached[cache_key]))
		emit("	},")
	emit("}")
	# END marker
	emit("# === SAS_LEADER_AI_CACHE_PYMODULE_END ===")

	emit("AI Personality Panel cache dumped to PythonDbg.log successfully.")

def try_load_predumped_cache():
	# Attempts to load the pre-dumped cache module.
	if not IS_USE_PREDUMPED_CACHE:
		return None

	try:
		# Dynamic import of the pre-dumped module
		predumped = __import__(PREDUMPED_MODULE_NAME)

		leaders_info_cached = predumped.LEADERS_INFO_CACHED

		print("AI Personality Panel cache Loaded pre-dumped cache from %s.py" % PREDUMPED_MODULE_NAME)
		return leaders_info_cached

	except:
		raise ImportError("AI Personality Panel cache IMPORT ERROR: IS_USE_PREDUMPED_CACHE=True but %s.py not found. Please provide a valid precomputed file, or disable SAS_SEVOPEDIA_LEADER_AI_PERSONALITY_CACHE_USE_PREDUMPED in XML SAS defines (GlobalDefines_advciv_sas.xml)." % PREDUMPED_MODULE_NAME)

def get_leader_cache_predumped_or_compute(compute_func, excluded_leader_types, is_emoji_enabled, is_raw_xml_names):
	# Main entry point. Either loads pre-dumped cache or computes it.
	# Always dumps to log when computing (so you can grab it later).

	# Try loading pre-dumped first
	predumped = try_load_predumped_cache()
	if predumped is not None:
		return predumped

	# Compute at runtime
	print("AI Personality Panel cache Computing leader cache at runtime...")
	leaders_info_cached = compute_func()

	# Dump to log only if enabled via define
	if IS_DUMP_CACHE_TO_LOG:
		dump_leader_cache_to_pythondbg(leaders_info_cached, excluded_leader_types, is_emoji_enabled, is_raw_xml_names)

	return leaders_info_cached

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

	# <!-- custom: Use shared AIP type lists instead of duplicating literal counts here; the workflow predump checker imports the same lists. Note: memory families still loop through positive_or_negative_memory_indexes because they intentionally split the full memory list by display category. (ChatGPT-5.5) -->
	CONTACT_TYPES_ASSESSED = get_aip_contact_types_assessed()
	NO_WAR_ATTITUDE_TYPES_ASSESSED = get_aip_no_war_attitude_types_assessed()
	MEMORY_TYPES_ASSESSED = get_aip_memory_types_assessed()
	NUM_CONTACT_TYPES_ASSESSED = len(CONTACT_TYPES_ASSESSED)
	NUM_ATTITUDE_TYPES_ASSESSED = len(NO_WAR_ATTITUDE_TYPES_ASSESSED)

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
	# memory affections/resentments. The synthetic pre-normalization aggregation itself lives in ai_utils_shared_with_civ4 so the
	# in-game AIP cache and the workflow predump checker can reuse one formula with different value providers. (ChatGPT-5.5) -->
	contact_types_assessed = CONTACT_TYPES_ASSESSED

	def get_contact_rand_for_leader(iLeader, iContact):
		return gc.getLeaderHeadInfo(iLeader).getContactRand(iContact)

	def get_contact_delay_for_leader(iLeader, iContact):
		return gc.getLeaderHeadInfo(iLeader).getContactDelay(iContact)

	def get_memory_type_for_index(iMemoryIndex):
		return MEMORY_TYPES_ASSESSED[iMemoryIndex]

	def get_memory_attitude_percent_for_leader(iLeader, iMemoryIndex):
		return gc.getLeaderHeadInfo(iLeader).getMemoryAttitudePercent(iMemoryIndex)

	def get_memory_decay_rand_for_leader(iLeader, iMemoryIndex):
		return gc.getLeaderHeadInfo(iLeader).getMemoryDecayRand(iMemoryIndex)

	# <!-- custom: before computing minimums and maximums, build all synthetic raw iAggregatedRaw* fields in the shared AIP helper layer. This keeps SevoPediaLeaderAIPValues.py focused on normalization/cache/UI rather than owning contact/memory synthetic-field creation. (ChatGPT-5.5) -->
	leaders_info_aip_synthetic_raw_values = compute_leaders_info_aip_synthetic_raw_values(NON_EXCLUDED_LEADERS, contact_types_assessed, get_contact_rand_for_leader, get_contact_delay_for_leader, get_memory_type_for_index, get_memory_attitude_percent_for_leader, get_memory_decay_rand_for_leader, B_WARN, IS_DEBUG_LEADER)

	def check_excluded_leaders_indexes_are_not_in_leaders_dict_keys(excluded_leaders_indexes_from_calculations, leaders_dict, leaders_dict_name):
		leaders_dict_keys = leaders_dict.keys()

		for excluded_leader_index in excluded_leaders_indexes_from_calculations:
			if (excluded_leader_index in leaders_dict_keys):
				excluded_leader_type = get_leader_type_from_leader_index(excluded_leader_index)
				raise KeyError("[FATAL] During sanity checks testing, excluded_leader_index=%d (excluded_leader_type=%s), was assessed to not be properly excluded from the calculations and its corresponding leader_index is still part of the leaders_dict_keys=%s, please make sure this excluded leader is not part of the leaders_dict_name=%s." % (excluded_leader_index, excluded_leader_type, str(leaders_dict_keys), leaders_dict_name))

	def check_leaders_dict_only_has_leader_index_keys(leaders_dict, leaders_dict_name):
		for key in leaders_dict.keys():
			if not isinstance(key, int):
				key_name = repr(key)
				key_type_name = str(type(key))
				raise TypeError("[FATAL] In leaders_dict_name=%s, key=%s is not an integer index (key_name=%s). Only integer iLeader indexes should be used as keys. Please ensure that key_type_name=%s uses iLeader (e.g. 0, 1, 2...) as keys, not leader_type strings." % (leaders_dict_name, key, key_name, key_type_name))

	check_excluded_leaders_indexes_are_not_in_leaders_dict_keys(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS, leaders_info_aip_synthetic_raw_values, "leaders_info_aip_synthetic_raw_values")
	check_leaders_dict_only_has_leader_index_keys(leaders_info_aip_synthetic_raw_values, "leaders_info_aip_synthetic_raw_values")

	# <!-- custom: Direct getter metadata lives in ai_utils_shared_with_civ4.py so the AIP panel and predump workflow checker share getter names, labels, inversion flags, XML tags, and defaults from one tuple source. (ChatGPT-5.5) -->

	# <!-- custom: store only the fields we want to display in the AI personality panel not the other / not all XML fields, see sevopedia debuggers py file and debugPrintLeaderHeadInfoFieldsToFetch and or its example of output for details -->
	fields_with_direct_getters, fields_attitude_thresholds = get_aip_fields_directly_parsed()
	required_getters = tuple(fields_with_direct_getters.keys()) + tuple(fields_attitude_thresholds.keys())
	check_required_newly_exposed_python_getters_gc_leader_exist(required_getters)
	def get_leader_info_minimums_and_maximums(fields_with_direct_getters, fields_attitude_thresholds, leaders_info_aip_synthetic_raw_values):
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
				parsed_name_flavor = get_aip_array_value_key("iFlavor", flavor_type)  # → iFlavorMilitary
				computeAndStoreMinMaxOfOneKey(parsed_name_flavor, value_flavor, leader_info_minimums, leader_info_maximums)

			# ==== CONTACTS ====
			for i in xrange(NUM_CONTACT_TYPES_ASSESSED):
				# <!-- custom: compute minimum and maximum among all leaders for raw contact fields, which here and as of now are only contact rands and contact delays -->
				# <!-- custom: Step 1: Raw contact rands and delays -->
				contact_type = CONTACT_TYPES_ASSESSED[i] # e.g. "CONTACT_JOIN_WAR"

				value_rand_raw = loopLeaderHeadInfo.getContactRand(i)
				value_delay_raw = loopLeaderHeadInfo.getContactDelay(i)
				parsed_name_rand = get_aip_array_value_key("iContactRand", contact_type) # → iContactRandJoinWar
				parsed_name_delay = get_aip_array_value_key("iContactDelay", contact_type) # → iContactDelayJoinWar
				computeAndStoreMinMaxOfOneKey(parsed_name_delay, value_delay_raw, leader_info_minimums, leader_info_maximums)
				computeAndStoreMinMaxOfOneKey(parsed_name_rand, value_rand_raw, leader_info_minimums, leader_info_maximums)

				# <!-- custom: also export the minimum and maximum raw aggregated contact prob (based on iLeader's rand and iLeader's delay (note: not based on the min and max rand among all leaders nor the min and max delay among all leaders)) among all leaders for each contact type -->
				# <!-- custom: Step 2: Raw aggregated contact probs -->
				parsed_name_aggregated_raw_contact_prob = get_aip_aggregated_raw_contact_prob_key(contact_type) # → iAggregatedRawContactProbJoinWar
				value_aggregated_raw_contact_prob = leaders_info_aip_synthetic_raw_values[iLeader][parsed_name_aggregated_raw_contact_prob]
				computeAndStoreMinMaxOfOneKey(parsed_name_aggregated_raw_contact_prob, value_aggregated_raw_contact_prob, leader_info_minimums, leader_info_maximums)

			# ==== MEMORY ====
			# <!-- custom: compute minimum and maximum among all leaders for raw contact fields, which here and as of now are only contact rands and contact delays; here we can loop over real DLL i index directly like in sevopedia_helpers py file debug code (see there for details), and unlike for raw aggregated memory fields that are separated in positive and negative memories, so here we can loop over real DLL i index directly -->
			for is_positive in (True, False):
				for is_affection in (True, False):
					positive_or_negative_memory_indexes = get_positive_or_negative_memory_indexes(is_positive)
					for i in positive_or_negative_memory_indexes:
						memory_type = MEMORY_TYPES_ASSESSED[i] # e.g. "MEMORY_DECLARED_WAR"

						# <!-- custom: Step 1: Raw memory attitude percents and decays -->
						# <!-- custom: since we display same raw attitude percent and decay fields values in UI regardless of positive/negative memory affection/resentment (raw aggregated values then the normalized aggregated values are is displayed) aggregation, no need to store multiple versions (i.e. positive/negative and affection/resentment) of these raw attitude percent and decay fields, store only one kind for all of these 4 possible combination cases (positive-affection, positive-resentment, negative-affection, negative-resentment) same as in XML fields structuration too for raw attitude percents and decays, i.e. for example only for example iMemoryAttitudePercentDeclaredWar (no positive-negative, no affection-resentment) for raw attitude_percent and decay fields same as in XML -->
						# <!-- custom: similarly for min max of raw attitude percents and decays export only once out of the 4 combinations (among positive-affection, positive-resentment, negative-affection, negative-resentment), since the raw value is always the same field and field name, no need to do it again for the other 3 times/combinations -->
						parsed_name_attitude_percent = get_aip_array_value_key("iMemoryAttitudePercent", memory_type) # → iMemoryAttitudePercentDeclaredWar
						if (parsed_name_attitude_percent not in leader_info_minimums) and (parsed_name_attitude_percent not in leader_info_maximums):
							value_attitude_percent = loopLeaderHeadInfo.getMemoryAttitudePercent(i)
							computeAndStoreMinMaxOfOneKey(parsed_name_attitude_percent, value_attitude_percent, leader_info_minimums, leader_info_maximums)

						parsed_name_decay = get_aip_array_value_key("iMemoryDecay", memory_type) # → iMemoryDecayDeclaredWar
						if (parsed_name_decay not in leader_info_minimums) and (parsed_name_decay not in leader_info_maximums):
							value_decay = loopLeaderHeadInfo.getMemoryDecayRand(i)
							computeAndStoreMinMaxOfOneKey(parsed_name_decay, value_decay, leader_info_minimums, leader_info_maximums)

						# <!-- custom: Step 2: Raw aggregated positive and negative memory affections and resentments -->
						parsed_name_aggregated_raw_positive_or_negative_memory_affection_or_resentment = get_aip_aggregated_raw_memory_key(memory_type, is_positive, is_affection) # → iAggregatedRawPositiveMemoryDeclaredWarAffection or iAggregatedRawPositiveMemoryDeclaredWarResentment or iAggregatedRawNegativeMemoryDeclaredWarAffection or iAggregatedRawNegativeMemoryDeclaredWarResentment
						value_aggregated_raw_positive_or_negative_memory_affection_or_resentment = leaders_info_aip_synthetic_raw_values[iLeader][parsed_name_aggregated_raw_positive_or_negative_memory_affection_or_resentment]
						computeAndStoreMinMaxOfOneKey(parsed_name_aggregated_raw_positive_or_negative_memory_affection_or_resentment, value_aggregated_raw_positive_or_negative_memory_affection_or_resentment, leader_info_minimums, leader_info_maximums)

			# ==== NOWARATTITUDEPROBS ====
			for i in xrange(NUM_ATTITUDE_TYPES_ASSESSED):
				value_no_war_attitude_prob = loopLeaderHeadInfo.getNoWarAttitudeProb(i)
				attitude_type = NO_WAR_ATTITUDE_TYPES_ASSESSED[i]  # e.g. "ATTITUDE_FURIOUS"
				parsed_name_no_war_attitude_prob = get_aip_array_value_key("iNoWarAttitudeProb", attitude_type)  # → iNoWarAttitudeProbFurious
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

	leader_info_minimums, leader_info_maximums = get_leader_info_minimums_and_maximums(fields_with_direct_getters, fields_attitude_thresholds, leaders_info_aip_synthetic_raw_values)

	# <!-- custom: note: leader_info_minimums, leader_info_maximums are like fake leaders, they dont have iLeader keys but only field/attribute keys (like "getMaxWarRand", "iAggregatedEtc...", "getBasePeaceWeight", "iFlavorMilitary", etc), so no need and not relevant to check if excluded leaders or if keys are only indexes because they are not, we have enough sanity checks overall everywhere to not need to resanity check this xd even though may help maybe but is bit tedious since dbug also helps, so as for sanity checks skipping them for leader_info_minimums, leader_info_maximums. -->

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
		# <!-- custom: minimum 1 to accommodate for the " " space character -->
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
		# - with symbol "+" and value 64 (/100), returns "++++++"
		# - with symbol "#" and value 39 (/100), returns "###"
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

	def compute_and_store_leaders_info_cached(leaders_info_aip_synthetic_raw_values, fields_with_direct_getters, fields_attitude_thresholds, leader_info_minimums, leader_info_maximums):
		# Loops over all leaders and normalizes each attribute to a 0-100 scale, using previously computed min/max per attribute and inversion flags.

		# Symbol settings
		all_symbols = {
			"RAW_SCALE_SYMBOL": "+",
			"AGGREGATED_SCALE_SYMBOL": "#",
			"EQUAL_SCALE_SYMBOL": "=",
		}

		# <!-- custom: displayed synthetic contact/memory metadata now comes from ai_utils_shared_with_civ4.py specs, so this cache builder no longer needs local contact/memory label dictionaries. (ChatGPT-5.5) -->

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
				parsed_name_flavor = get_aip_array_value_key("iFlavor", flavor_type)  # → iFlavorMilitary
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

			# <!-- custom: for contact fields, display normalized synthetic aggregate probabilities, not raw rand/delay fields. Raw rand/delay stay in the label as (rand/delay), while the cache key stores the normalized iAggregatedContactProb* value. (ChatGPT-5.5) -->
			b_invert_4_aggregated_contact_probs = False
			symbol_aggregated_contact_probs = all_symbols["AGGREGATED_SCALE_SYMBOL"]
			for i, contact_type, parsed_name_4_aggregated_raw_contact_prob, parsed_name_4_aggregated_contact_prob, label_contact in get_aip_displayed_contact_aggregate_specs(CONTACT_TYPES_ASSESSED):
				suffix = get_pascal_case_suffix(contact_type) # → "JoinWar"

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

				# <!-- custom: raw key supplies min/max input; display key is stored in the predump/cache. Example: iAggregatedRawContactProbJoinWar normalizes into iAggregatedContactProbJoinWar. (ChatGPT-5.5) -->
				raw_value_4_aggregated_contact_prob = leaders_info_aip_synthetic_raw_values[iLeader][parsed_name_4_aggregated_raw_contact_prob]
				min_value_4_aggregated_raw_contact_prob = leader_info_minimums[parsed_name_4_aggregated_raw_contact_prob]
				max_value_4_aggregated_raw_contact_prob = leader_info_maximums[parsed_name_4_aggregated_raw_contact_prob]

				# <!-- custom: note: chatgpt 5 told me to change parsed_name_4_aggregated_contact_prob to parsed_name_4_aggregated_raw_contact_prob claiming it was a real bug, but doing it created an error ingame; Long_Comments_py.txt #11; so not a bug -->
				compute_and_store_leader_info_cached_tuple(raw_value_4_aggregated_contact_prob, min_value_4_aggregated_raw_contact_prob, max_value_4_aggregated_raw_contact_prob, b_invert_4_aggregated_contact_probs, symbol_aggregated_contact_probs, all_symbols, parsed_name_4_aggregated_contact_prob, label_with_raw_value_rand_and_raw_value_delay, iLeader, leader_info_cached)

			# <!-- custom: for memory fields, display only normalized synthetic positive memory affections and negative memory resentments. The shared specs decide which iAggregatedRaw* keys become displayed iAggregated* cache keys. (ChatGPT-5.5) -->
			b_invert_4_positive_and_negative_memory_affections_and_resentments = False
			symbol_aggregated_positive_and_negative_memory_affections_and_resentments = all_symbols["AGGREGATED_SCALE_SYMBOL"]

			for i, memory_type, is_positive, is_affection, parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment, parsed_name_4_aggregated_positive_or_negative_memory_affection_or_resentment, label_memory in get_aip_displayed_memory_aggregate_specs():
				suffix = get_pascal_case_suffix(memory_type) # → "DeclaredWar"

				# <!-- custom: generate the label before normalizing, and so we also have the label as well for later display after normalization done in/at UI -->
				raw_value_4_attitude_percent = loopLeaderHeadInfo.getMemoryAttitudePercent(i)
				raw_value_4_decay = loopLeaderHeadInfo.getMemoryDecayRand(i)
				label_raw_attitude_percent_and_raw_decay = "(%d/%d)" % (raw_value_4_attitude_percent, raw_value_4_decay)
				if IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD:
					# <!-- custom: for these fields, the suffix like "Military" is much shorter than the parsed name like "iFlavorMilitary", and clear enough for our need for the labels as keys or suffixes, so use the suffix it instead of parsed name -->
					label_with_raw_value_rand_and_raw_value_delay = get_labels_as_keys_or_suffixes_max_length_label(suffix, label_raw_attitude_percent_and_raw_decay, 19)
				else:
					label_with_raw_value_rand_and_raw_value_delay = "%s %s" % (label_memory, label_raw_attitude_percent_and_raw_decay)

				# <!-- custom: raw key supplies min/max input; display key is stored in the predump/cache. Example: iAggregatedRawPositiveMemoryTradedTechToUsAffection normalizes into iAggregatedPositiveMemoryTradedTechToUsAffection. (ChatGPT-5.5) -->
				raw_value_4_aggregated_positive_or_negative_memory_affection_or_resentment = leaders_info_aip_synthetic_raw_values[iLeader][parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment]
				min_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment = leader_info_minimums[parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment]
				max_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment = leader_info_maximums[parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment]

				compute_and_store_leader_info_cached_tuple(raw_value_4_aggregated_positive_or_negative_memory_affection_or_resentment, min_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment, max_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment, b_invert_4_positive_and_negative_memory_affections_and_resentments, symbol_aggregated_positive_and_negative_memory_affections_and_resentments, all_symbols, parsed_name_4_aggregated_positive_or_negative_memory_affection_or_resentment, label_with_raw_value_rand_and_raw_value_delay, iLeader, leader_info_cached)

			b_invert_no_war_attitude_probs = False
			symbol_no_war_attitude_probs = all_symbols["RAW_SCALE_SYMBOL"]
			for i in xrange(NUM_ATTITUDE_TYPES_ASSESSED):
				attitude_type = NO_WAR_ATTITUDE_TYPES_ASSESSED[i]  # e.g. "ATTITUDE_FURIOUS"
				suffix = get_pascal_case_suffix(attitude_type)  # → "Furious"
				parsed_name_no_war_attitude_prob = get_aip_array_value_key("iNoWarAttitudeProb", attitude_type)  # → iNoWarAttitudeProbFurious
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

	compute_and_store_leaders_info_cached(leaders_info_aip_synthetic_raw_values, fields_with_direct_getters, fields_attitude_thresholds, leader_info_minimums, leader_info_maximums)

	# <!-- custom: cleanup -->
	del leaders_info_aip_synthetic_raw_values
	del fields_with_direct_getters
	del fields_attitude_thresholds
	del leader_info_minimums
	del leader_info_maximums

	check_excluded_leaders_indexes_are_not_in_leaders_dict_keys(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS, LEADERS_INFO_CACHED, "LEADERS_INFO_CACHED")
	check_leaders_dict_only_has_leader_index_keys(LEADERS_INFO_CACHED, "LEADERS_INFO_CACHED")

	# <!-- custom: category definitions are now owned by SevoPediaLeader.py (UI layer); this cache module remains data-only for predump/runtime cache values. (GPT-5.3-Codex) -->
	# <!-- custom: final return. Note that this caching, even though it is done in sevopedia leader, is triggered from sevopedia main's placeLeaders, after module load, so that we cache (or load the precomputed cache) only once just at the right time when it is computationally the cheapest for players. -->
	# <!-- custom: also print the debug line below regardless of debug flag status, we really want to know this info and it is short -->
	print("Sevopedia Leader cache prebuilt cache prebuilt. This should appear only once per gaming session.")

	return LEADERS_INFO_CACHED

def getPrecomputedCacheOnceOnlyFromSevopediaMainInSevopediaLeaderForEntireSession():
	# Wrapper that either loads pre-dumped cache or computes it
	return get_leader_cache_predumped_or_compute(compute_func = _compute_leader_cache_internal, excluded_leader_types = AIP_EXCLUDED_LEADER_TYPES, is_emoji_enabled = (gc.getDefineINT("SAS_SEVOPEDIA_LEADER_AI_PERSONALITY_PANEL_SHOW_EMOJI") > 0), is_raw_xml_names = IS_SHOW_RAW_XML_FIELD_NAMES_INSTEAD)


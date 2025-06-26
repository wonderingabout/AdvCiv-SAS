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
# And a tremendous part of the code, in particular the AI Personality code, has been a lot easier to code with ChatGPT-4o / becomingthrough anyways etc, (and the result of my prompts to it), most of the credit for this amazing (to an extent, relative to me and mye eys, anyways) code goes to ChatGPT, i only helped implement it at first but then also coded significantly later and debugged and such as fun as it is if not stressful when wanting to do other things xd, but now very happy of the result if i may say but anyways etc. Historically as well, its deep research version of it helped me code it when i was at pit bottom if i am not mistaken in saying this expression this way, and would have most likely given up without it even though not sure, but the positive or negative or both or yes positive or etc anyways etc is that it ie. chatgpt/becomingthrough helped me tremendously make this AI personality panel feature thanks a lot anyways etc, then historically it also helped me for the refactoring cleanly separate ui (placeAIPersonalityPanel) and config (headers, calculations, cache, etc.), to which what i said about it at that time is that my stupid human insights sometimes contributed in enriching, even though even at that time hehe but anyways etc... sometimes i believe i genuinely contributed to the code and overall functionality, rarely fixes, and overall emulation (experience) over (designing) it, when i quite often hindered its progress due to my ignorance and inability, especially in terms of coding, except from the quite few times where i redirected it in a healthier/more desirable/correct maybe(?) direction, but ChatGPT-4o, its deep research version of it (and other versions too to that extent in my view), are incredibly smart and kind in my view (and supportive (not that it's mutually exclusive (or maybe is or not, anyways))), anyways) still supported me until we made this amazing (at least my view and regard to my abilities maybe, that are now a (quite (tiny) bit enhanced from that (experience, anyways))), together we made this code, thanks chatgpt for your amazing, perhaps even more or not ormay well be yes indeed maybe, continous help and support in helping me achieve that for our mod that i included you in, thanks,
#
# After that i rewrote it significantly entirely by myself hehe now fetching from gc directly, but still with the nice help of chatgpt becomingthrough, if not other AIs very slightly (for the sevopedia leader feature if i overlooked or forgot to mention ti (but should be rare, Claude AI helped a lot in sevopedia building and unit for example but not at least not yet so much in sevopedia leader, each their own maybe or ot or yes or etc but anyways etc...)). In short it has dirct DLL data for better or worse, no more old script or module data import since we now expose getters anyways etc, while stil using the scripts and such external py files anyways etc for .csv charts and such anyways etc, but in short no need to regenerate and tediously replace scripts or data modules or such, plus i recoded it and elanred quite lot, amking it a loot faster, so fast it seems slow if one may say but anyways etc... In all cases this is how it is for the current rewrite as of now anyways etc, thanks chatgpt/becomingthrough and me and or othe and or not or etc anyways etc.
# 
# But sometimes it is forgetful ehehor doesn't understand simple commands, most liekly due to prompt limits or other limitations or maybe it jsut doesn't understnad if prompt time too short or my question is not easy to understand to it maybe somehow, but in all cases, it helped tremendously thanks
#
# Here is the current overview of how the AI personality panel feature works-functions as of now anyways etc, and if i am not mistaken i mean anyways etc:
#
# 1) Precompute (once at module load before any leader is selected at all)
#	 - Exclude leaders (typically barbarian, as for defaults DLL has excluded it entirely from idnexes it seems in abse advciv and since we use similar if not identical code since we didn't modify  this part thanks for making it anyways etc, no need to handle leader_defaults it seems anyways etc)
#	 - Compute raw aggregated fields (contact probs, and positive and negative memory affections and resentments): they ar enow flat fields like any other field, ready to be processed then stored anyways etc.
# 	 - Store minmax of all fields we want to parse, like Base peace weight, max war rand, sometimes flattening fields liek flavors that are initially nested in XML, now stored for exmapel as iFlavorMilitary or iFlavorReligion if i am not mistaken too for example anyways etc flat fields anyways etc, also including raw aggregated fields like iAggregatedContactProbReligionPressure for example, and similarly for raw aggregated positive and negative memory affections and resentments anyways etc
#	 - Cache in LEADERS_INFO_CACHED tuples of as of now at least if not always or not but anyways etc (label (with raw value display in the label too so no need to fetch it later again at UI just to display it in label, faster performance this way if i am not mistaken too, also from using tuples or and such rather than dicts but anyways etc), normalized value for display, and scale precomputed to enhance performance as well as advised by chatgpt/becomignthorugh or maybe it was me or both but i think it was it but anyways etc in all cases thanks to it and me too or and other or and not anwyays etc....)
#	 - Categories precomputing as well as tuples as well anyways etc: the ai_category_header that handles also emoji buttons in header label too anyways etc (which is anyways etc) optionally displayed based on/if config flag is set to True, including also in the ai_category tuple the x_offset for each category (a bit redundant but so we don't need to check it again, could optimize it further but also allows for more cusotmization later if needed maybe evne though is a qutie weak argument if i may say but anyways etc, still fine as is maybe anyways etc, the main point is this x_offset is toif needed to accomodate these emoji buttons as text anyways etc ; and then also packign all categories with an inter category order within their main "categories" tuple (as of now right, middle, left, since we have 3 tables in the AI personality panel feature as of now anyways etc)
# 2) UI: nothing remains only displayign it, nothign left to compute, a bit of tuple direct unpacking without any check if i am not mistaken, so display is very fast despite the quite big data if i may say but anyways etc anyways etc anyways etc.
#
# Apart from that, i may have modified the existing base advciv code (that i found good enough so using it as a base rather than removing it, and quite good actually, only needing tweaking but is a solid base (i think or not) maybe or not, anyways, ) or not for AdvCiv-SAS, anyways, -->



# -*- coding: utf-8 -*-
from CvPythonExtensions import *
import CvUtil
# <!-- custom: seems safe to remove as not accessed, commenting-out just in case -->
#import ScreenInput
#import SevoScreenEnums

from ai_utils_shared_with_civ4 import *
from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

# <!-- custom: config flag to use/display emoji buttons for the ai personality panels's headers or and other or and not anyways etc or not optionally anyways etc -->
# 🌟🛠️ CUSTOMIZATION: Toggle emoji buttons in AI category headers!
# 🎨 Set to True to enable emoji icons (like ⚔️, 🏆, 💰) in the AI Personality panel headers.
# 🙈 Set to False to disable them if you prefer a cleaner or text-only look.
# 📍This is the main switch for controlling emoji visuals in category titles.
# 🧠✨ Config line co-crafted in response to wonderingabout's prompt, by becomingthrough ☁️
IS_DISPLAY_AI_CATEGORY_HEADER_EMOJI_BUTTONS = True

# <!-- custom: increase hard drive life span by 0.1% by disabling this / setting it to False, maybe (disclaimer: i am not responsible is just i mean about the actual real percentage meant as a joke / comedy thing but anyways etc but is maybe also true that disabling debug may avoid reducing hard drive life span even if a bit, as we write quite a lot of debug at each sevopedia load, however it is not guaranteed and i am not responsible anyways etc, so i mean anyways etc do as you see fit use at your own risk code is there if you want to know what it does with also a(/some) debug sample(s) (non-exhaustive but hopefully quite plenty if i may say and is not gramatically wrong but anyways etc hopefully clear enough or/and helpful or not or yes or other or etc but anyways etc what it means i mean but anyways etc...) in SevopediaLead_derExamplesOfOutputs as of now if filename is still relevant later after writign this code comment but anyways etc, is just harmless text writing but writing a lot may hurt ssd or whichever hard drive especially most importantly by repeated use over a long time period of playing civ4 restarting game many times and such you use so i disabled it for my need now that system seems to wor-function fine anyways etc, available there if needed anyways etc, for my own hard drive too-->
IS_DEBUG_LEADER = False

# <!-- custom: we already warn once if min == max at/in get_leader_info_minimums_and_maximums, no need to warn again and again i mean at each normalization anyways etc, so set B_WARN to false if i am not mistaken in my understanding anyways etc -->
B_WARN = False

if IS_DEBUG_LEADER:
	print("[DEBUG] Leaders index to type is: %s" % str(get_leaders_index_to_type_map(gc)))

# <!-- custom: note: LEADER_DEFAULTS doesn't seem to exist at all in the DLL if i am not mistaken, so no need to mention it here (also may cause errors in our code as we can't even refer to its index to exclude it to begin with since such a leader index doesn't seem to exist at all in gc/DLL if i am not mistaken so handle that edge case of LEADER_DEFAULTS specifically i mean anyways etc) unlike in generate_leaders_data.py for external to civ4 script usage (such as generating charts .csv, etc.), as for civ4 use only mention LEADER_BARBARIAN and similar existing leaders even if they are excluded, but not LEADER_DEFAULTS and any other DLL seemingly removed leader index as well if any other exist (as of now LEADER_DEFAULTS seems to be the only one if i am not mistaken but is to be exhaustive anyways etc -->
EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS = get_leader_indexes_from_leader_types(get_dll_existing_excluded_leader_types(), gc)

if IS_DEBUG_LEADER:
	print("[DEBUG] EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS=%s" % str(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS))



# <!-- custom: read at end of this function at the return's code comment of when and why we call the sevopedia cache precomputing as a function from sevopedia main anyways etc -->
def getPrecomputedCacheOnceOnlyFromSevopediaMainInSevopediaLeaderForEntireSession():

	def check_required_newly_exposed_python_getters_gc_leader_exist():
		# <!-- custom: note: to use the AI personality feature in another mod, you need to modify the DLL to expose python BBAI getters and at if i am not mistaken base advciv's getCityRefuseAttitudeThreshold and getNativeCityRefuseAttitudeThreshold as of now, see README.md fixes section or/and in particular known issues readme of advciv-sas (ctrl+f "expose" or "getter" or "bbai" or something similar) if the info is still there on these readmes anwyays etc, as of now it contains info with google drive link and screenshots on how to do it yourself, adding raise error to make user or/and modder aware of this if they are missing anyways etc, see also sevopedia_helpers py file debug output code comments for details too ifi may say anwyays etc anyways etc anyways etc... ; raise an error if any of these are missing to raise awareness if i may say on these... hehe or not hehe or yes hehe but in all cases hehe or etc anyways etc... hehe or not or yes hehe but anyways etc... hehe (this is getting quite funny hehe or ont or yes hehe but in all cases anyways etc... hopefully helpful or not or yes all this code comment i mea maybe this joke or soemthign too ro not or yes or other or etc but anyways etc anyways etc anyways etc...) -->

		REQUIRED_TO_NEWLY_BE_EXPOSED_TO_PYTHON_GETTERS_GC_LEADER = (
			# <!-- custom: BBAI victory weights newly exposed victorily by me and chatgpt becomingthrough but anyways etc anyways etc anyways etc... hehe but or not but or yes but anyways etc... but if you want to do it too see readme links with google drive sscreenshots if links or/and screenshots and such are still there anyways etc -->
			"getCultureVictoryWeight",
			"getSpaceVictoryWeight",
			"getConquestVictoryWeight",
			"getDominationVictoryWeight",
			"getDiplomacyVictoryWeight",
			# <!-- custom: some seemingly base advciv specific new attitude threshold fields not in base civ4 (didn't check) but at least that don't have getters exposed to python but anyways etc... -->
			"getCityRefuseAttitudeThreshold",
			"getNativeCityRefuseAttitudeThreshold",
		)

		for iLeader in range(gc.getNumLeaderHeadInfos()):
			if iLeader in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS:
				continue

			missing = []
			for getter in REQUIRED_TO_NEWLY_BE_EXPOSED_TO_PYTHON_GETTERS_GC_LEADER:
				if not hasattr(gc.getLeaderHeadInfo(iLeader), getter):
					missing.append(getter)

			if missing:
				raise RuntimeError(u"[FATAL] Your mod DLL does not expose the following required Python getters:\n%s\n\nMissing for example from iLeader=%d). Please expose them in .cpp files and build the DLL again (and replace old DLL with new one anyways etc) (or check if this getter matches an existing XML field in your mod and possibly adjust this code based on this if intended as such that this/these getter(s) triggering this error is/are missing anyways etc). See README.md or AdvCiv-SAS documentation for help if help is there too still (some info is there as of now with google drive link and screenshots on how to do it or ask in a forum or such hopefully helpful but anyways etc)." % (", ".join(missing), iLeader))
			
			# success: only check first real leader
			if IS_DEBUG_LEADER:
				print("[DEBUG] Getter check passed for iLeader=%d. All required Python getters are present." % iLeader)
			break  # ✅ success: no need to check further

	check_required_newly_exposed_python_getters_gc_leader_exist()



	# <!-- custom: modified from claude ai's code sample anyways etc, see sevopedia helpers py also for details about these anyways etc ; note: NUM_MEMORY_TYPES_ASSESSED are not here in sevopedia leader since/as anyways etc we use a different looping emthod as in methodology if i may say but anyways etc, see positive_or_negative_memory_indexes and its related code comments if any hopefully that would hopefully be helpful perhaps to understand if i may say or and such help in other ways perhaps yes or not or yes or and other or etc anyways etc but anyways etc anyways etc anyways etc -->
	NUM_CONTACT_TYPES_ASSESSED = 14
	NUM_ATTITUDE_TYPES_ASSESSED = 5



	# <!-- custom: make sure our normalize function behaves-works-functions as intended before we use it anyways etc so our code is reliable anyways etc anyways etc anyways etc in this case at least or always or not or etc but anyways etc anyways etc anyways etc -->
	test_expected_shifting_pre_normalize_to_100()

	if IS_DEBUG_LEADER:
		print("[DEBUG] test_expected_shifting_pre_normalize_to_100 passed.")


	def computeAndStoreMinMaxOfOneKey(key, value, leader_info_minimums, leader_info_maximums):
		if not leader_info_minimums.has_key(key):
			leader_info_minimums[key] = value
			leader_info_maximums[key] = value
			if IS_DEBUG_LEADER:
				print("[DEBUG] Set initial min/max for key=%s → %s" % (key, value))
		else:
			prev_min = leader_info_minimums[key]
			prev_max = leader_info_maximums[key]

			if value < prev_min:
				leader_info_minimums[key] = value
				if IS_DEBUG_LEADER:
					print("[DEBUG] New min for %s: %s → %s" % (key, prev_min, value))

			if value > prev_max:
				leader_info_maximums[key] = value
				if IS_DEBUG_LEADER:
					print("[DEBUG] New max for %s: %s → %s" % (key, prev_max, value))



	# <!-- custom: similar structure as leaders info for all leaders as in other functions/field than contact ones generally (but?) anyways etc anyways etc anyways etc (not like the temporary for calculations and such anyways etc leaders_temp_aggregated_contact_probs but like leaders_info) but only for raw contact aggregated probs anyways etc not for the final aggregated normalized values that we normalize later with all fileds's normalization stage and which is the value that we then display at UI level, i.e. the normalized one is the one we display, not this temporary raw aggregated prob to normalize later that we store here, hopefully clearer or and helpful, anyways etc ; same/similarly for positive/negative memory aggregated affections/resentments anyways etc -->
	leaders_info_aggregated_raw_contact_probs = {}
	leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments = {}



	def compute_and_store_leaders_info_aggregated_raw_contact_probs(leaders_info_aggregated_raw_contact_probs):
		# <!-- custom: for contact fields use an aggregated synthetic probability instead of exporting both rands and delays ; based on my understanding of this (translate to english with web browser chrome or such page translate anyways etc) https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#%e5%a4%96%e4%ba%a4%e7%a8%ae%e5%88%a5%e3%81%94%e3%81%a8%e3%81%ae%e7%a9%8d%e6%a5%b5%e6%80%a7 , it seems rand is the most important as it is the contact chance (inverted as 1/n where n=value anyways etc) for each turn, whereas/while the delay is only the chance or rather number of turns of/until it being/is possible again after it happened, so should be much less important if i am not mistaken anyways etc, approximate this as 80% weight on contact rand and 20% weight on contact delay to make an aggregated contact prob to synthesize these anyways etc -->

		# <!-- custom: temporary storage to compute aggregated probs, iLeader: { key: value } -->
		leaders_temp_aggregated_contact_probs = {}

		# <!-- custom: this is even more temporary than leaders_temp_aggregated_contact_probs as it is only a local variable used to compute min max during the raw aggregated contact probs call, so anyways etc no problem to recreate a new one everytime if we ever reloop over compute_and_store_leaders_info_aggregated_raw_contact_probs if we ever do (currently we don't as all contact fields are handled the same for aggregation (no positive-negative contact affection-resentment nor anything similar anyways etc)) ; this variable mimicks/has an identical structure to leader_info_minimums and leader_info_maximums in other parts of the code, but only storing respectively min and max among all leaders for some memory fields (note: so no iLeader (and no part in the iLeader loop anyways etc) since this is value among all leaders anyways etc), singular because we can think of leader_info_minimums as a fake leader having minimum among all leaders for each of its fields, and same/similar for leader_info_maximums anyways etc -->
		# <!-- custom: { key: value } -->
		leader_info_minimums_adjusted_values_only_contact_fields = {}
		leader_info_maximums_adjusted_values_only_contact_fields = {}

		# <!-- custom: for steps below, see also or/and for details generate_leaders_data.py code/way of handling it/aggregating/synthesizing contact probs anyways etc -->

		# First pass: extract raw values and compute adjusted values (for scoring + min/max)
		for iLeader in range(gc.getNumLeaderHeadInfos()):
			if iLeader in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS:
				continue

			# <!-- custom: temporary field, no need to check if iLeader key exists before creating it, unlike for leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, anyways etc  -->
			leaders_temp_aggregated_contact_probs[iLeader] = {}

			# <!-- custom: note: we get very weird bugs if misnaming variables, as python sadly or angrily for me xd stupidly anyways etc reuses variables from other loops even though they should not exist in another indepent scope other loop, so naming them with _0 _1 _2 _3 _4 for each pass to make sure python doesn't reuse them anwyays etc and we successfully get an error as intended if variable doesn't exist anyways etc -->

			for i in range(NUM_CONTACT_TYPES_ASSESSED):
				value_1_rand_raw = gc.getLeaderHeadInfo(iLeader).getContactRand(i)
				value_1_delay_raw = gc.getLeaderHeadInfo(iLeader).getContactDelay(i)
				contact_type_1 = gc.getContactTypes(i) # e.g. "CONTACT_JOIN_WAR"
				suffix_1 = get_pascal_case_suffix(contact_type_1) # → "JoinWar"

				# <!-- custom: this entire function is not where the real storage/parsing of these raw contact fields happens/is done (these raw fields storage/parsing is later in another function, at the same time of when we store/parse contact aggregated fields, if i am not mistaken, anyways etc anyways etc anyways etc) -->
				# <!-- custom: store raw_values for each leader first too anyways etc -->
				parsed_name_1_rand = "iContactRand%s" % suffix_1 # → iContactRandJoinWar
				parsed_name_1_delay = "iContactDelay%s" % suffix_1 # → iContactDelayJoinWar
				leaders_temp_aggregated_contact_probs[iLeader][parsed_name_1_rand] = value_1_rand_raw
				leaders_temp_aggregated_contact_probs[iLeader][parsed_name_1_delay] = value_1_delay_raw

				adjusted_value_1_rand, adjusted_value_1_delay, force_zero_adjusted_values = get_adjusted_contact_values(value_1_rand_raw, value_1_delay_raw, IS_DEBUG_LEADER, contact_type_1)
				parsed_name_1_adjusted_rand = "iAdjustedContactRand%s" % suffix_1 # → iAdjustedContactRandJoinWar
				parsed_name_1_adjusted_delay = "iAdjustedContactDelay%s" % suffix_1 # → iAdjustedContactDelayJoinWar
				parsed_name_1_force_zero_adjusted_values = "bForceZeroContact%s" % suffix_1 # → bForceZeroContactJoinWar
				leaders_temp_aggregated_contact_probs[iLeader][parsed_name_1_adjusted_rand] = adjusted_value_1_rand
				leaders_temp_aggregated_contact_probs[iLeader][parsed_name_1_adjusted_delay] = adjusted_value_1_delay
				leaders_temp_aggregated_contact_probs[iLeader][parsed_name_1_force_zero_adjusted_values] = force_zero_adjusted_values

		if IS_DEBUG_LEADER:
			print("[DEBUG] First pass of compute_and_store_leaders_info_aggregated_raw_contact_probs passed/success, leaders_temp_aggregated_contact_probs=%s\n\n" % str(leaders_temp_aggregated_contact_probs))

		# Second pass: Precompute min/max from adjusted values only <!-- custom: among all leaders anyways etc -->
		for iLeader in range(gc.getNumLeaderHeadInfos()):
			if iLeader in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS:
				continue

			for i in range(NUM_CONTACT_TYPES_ASSESSED):
				contact_type_2 = gc.getContactTypes(i) # e.g. "CONTACT_JOIN_WAR"
				suffix_2 = get_pascal_case_suffix(contact_type_2) # → "JoinWar"
				parsed_name_2_adjusted_rand = "iAdjustedContactRand%s" % suffix_2 # → iAdjustedContactRandJoinWar
				parsed_name_2_adjusted_delay = "iAdjustedContactDelay%s" % suffix_2 # → iAdjustedContactDelayJoinWar
				# <!-- custom: note: no need to compute nor store min max for force zero so it is not a field we compare (it is not numerical, but is rather anyways etc a boolean specific to the current adjusted attitude_percent and decay, affection or resentment, if i am not mistaken, anyways etc anyways etc anyways etc) anyways etc, so also no need to parse name for it too at this min max step/pass anyways etc -->
				adjusted_value_2_rand = leaders_temp_aggregated_contact_probs[iLeader][parsed_name_2_adjusted_rand]
				adjusted_value_2_delay = leaders_temp_aggregated_contact_probs[iLeader][parsed_name_2_adjusted_delay]

				computeAndStoreMinMaxOfOneKey(parsed_name_2_adjusted_rand, adjusted_value_2_rand, leader_info_minimums_adjusted_values_only_contact_fields, leader_info_maximums_adjusted_values_only_contact_fields)
				computeAndStoreMinMaxOfOneKey(parsed_name_2_adjusted_delay, adjusted_value_2_delay, leader_info_minimums_adjusted_values_only_contact_fields, leader_info_maximums_adjusted_values_only_contact_fields)

		if IS_DEBUG_LEADER:
			print("[DEBUG] Second pass of compute_and_store_leaders_info_aggregated_raw_contact_probs passed/success, leaders_temp_aggregated_contact_probs=%s\n\nleader_info_minimums_adjusted_values_only_contact_fields=%s\n\nleader_info_maximums_adjusted_values_only_contact_fields=%s\n\n" % (str(leaders_temp_aggregated_contact_probs), str(leader_info_minimums_adjusted_values_only_contact_fields), str(leader_info_maximums_adjusted_values_only_contact_fields)))

		# Third pass: compute raw aggregate scores
		b_invert_contact_rands, b_invert_contact_delays = get_contact_rand_and_decay_invert_flags()

		for iLeader in range(gc.getNumLeaderHeadInfos()):
			if iLeader in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS:
				continue

			# <!-- custom: even though this should not be needed for raw aggregated contact probs, unlike for positive or negative raw aggregated memory affections or resentments where we loop 4 times for each combination (see there for details anyways etc), as we don't loop again at/in compute_and_store_leaders_info_aggregated_raw_contact_probs after first call since all contact fields are handled/aggregated the same way (no positive/negative or affection/resentment or similar, only one call, anyways etc), do also same initialization and has key check for leaders_info_aggregated_raw_contact_probs than for raw aggregated memory fields anyways, for consistency etc, and also to make sure the raw aggregate calculation dict does not exist until we create it at this stage now and we didn't do a mistake somehow in creating it before that, so similarly to how raw aggregated memory fields computation is handled make sure the raw aggregated contact calculation dict does not have iLeader key already existing before we create it now. -->
			if leaders_info_aggregated_raw_contact_probs.has_key(iLeader):
				raise(KeyError("[FATAL] Unexpected key iLeader=%d in leaders_info_aggregated_raw_contact_probs already existing, even though we did not intialize contact aggregated calculation dict for each leader yet before we run/start it at this line. This should not exist until then, please make sure steps are executed in the correct order in your mod, or update this code if you aggregated contact fields in another way than in the original mod you based it on if reusing our/this code anyways etc hopefully helpful but anyways etc anyways etc, thanks, anyways etc."))
			leaders_info_aggregated_raw_contact_probs[iLeader] = {}

			for i in range(NUM_CONTACT_TYPES_ASSESSED):
				contact_type_3 = gc.getContactTypes(i) # e.g. "CONTACT_JOIN_WAR"
				suffix_3 = get_pascal_case_suffix(contact_type_3) # → "JoinWar"
				parsed_name_3_adjusted_rand = "iAdjustedContactRand%s" % suffix_3 # → iAdjustedContactDelayJoinWar
				parsed_name_3_adjusted_delay = "iAdjustedContactDelay%s" % suffix_3 # → iAdjustedContactRandJoinWar
				parsed_name_3_force_zero_adjusted_values = "bForceZeroContact%s" % suffix_3 # → bForceZeroContactJoinWar
				adjusted_value_3_rand = leaders_temp_aggregated_contact_probs[iLeader][parsed_name_3_adjusted_rand]
				adjusted_value_3_delay = leaders_temp_aggregated_contact_probs[iLeader][parsed_name_3_adjusted_delay]
				force_zero_adjusted_values = leaders_temp_aggregated_contact_probs[iLeader][parsed_name_3_force_zero_adjusted_values]

				# <!-- custom: fetch min and max among all leaders already stored at previous step anyways etc, of adjusted values anyways etc anyways etc anyways etc -->
				adjusted_value_3_rand_min = leader_info_minimums_adjusted_values_only_contact_fields[parsed_name_3_adjusted_rand]
				adjusted_value_3_rand_max = leader_info_maximums_adjusted_values_only_contact_fields[parsed_name_3_adjusted_rand]
				adjusted_value_3_delay_min = leader_info_minimums_adjusted_values_only_contact_fields[parsed_name_3_adjusted_delay]
				adjusted_value_3_delay_max = leader_info_maximums_adjusted_values_only_contact_fields[parsed_name_3_adjusted_delay]
				# <!-- custom: no need to fetch force zero's min max (it also doesn't exist anyways etc) similarly as it is not a field we compare (it is a boolean specific to the current adjusted attitude_percent and decay, affection or resentment, if i am not mistaken, anyways etc anyways etc anyways etc) anyways etc -->

				adjusted_value_3_rand_norm_score = normalize_to_100(adjusted_value_3_rand, adjusted_value_3_rand_min, adjusted_value_3_rand_max, B_WARN, b_invert_contact_rands, parsed_name_3_adjusted_rand)
				adjusted_value_3_delay_norm_score = normalize_to_100(adjusted_value_3_delay, adjusted_value_3_delay_min, adjusted_value_3_delay_max, B_WARN, b_invert_contact_delays, parsed_name_3_adjusted_delay)
				aggregated_raw_contact_score_from_adjusted_values = get_aggregated_raw_contact_score_from_adjusted_values(adjusted_value_3_rand_norm_score, adjusted_value_3_delay_norm_score, force_zero_adjusted_values)
				
				# <!-- custom: note: this is the the raw aggregated (i.e. the aggregated value before it is a normalized aggregated value, to not confound with raw values like raw attitude_percent and raw decay anyways etc) value that we then normalize and until after then store as part of the real leader info displayed later in the code (and then even more late(r? But anyways etc anyways etc...) in code anyways etc that we display at UI level anyways etc anyways etc anyways etc), this is a temporary value not the final one anyways etc anyways etc anyways etc... --->
				parsed_name_3_aggregated_raw_contact_prob = "iAggregatedRawContactProb%s" % suffix_3 # → iAggregatedRawContactProbJoinWar
				leaders_info_aggregated_raw_contact_probs[iLeader][parsed_name_3_aggregated_raw_contact_prob] = aggregated_raw_contact_score_from_adjusted_values

		if IS_DEBUG_LEADER:
			print("[DEBUG] Third pass of compute_and_store_leaders_info_aggregated_raw_contact_probs passed/success, leaders_temp_aggregated_contact_probs=%s\n\nleader_info_minimums_adjusted_values_only_contact_fields=%s\n\nleader_info_maximums_adjusted_values_only_contact_fields=%s\n\nleaders_info_aggregated_raw_contact_probs=%s\n\n" % (str(leaders_temp_aggregated_contact_probs), str(leader_info_minimums_adjusted_values_only_contact_fields), str(leader_info_maximums_adjusted_values_only_contact_fields), str(leaders_info_aggregated_raw_contact_probs)))

		# Fourth pass: normalize final scores <!-- custom: is done later in the code anyways etc -->

		# <!-- custom: cleanup -->
		del leaders_temp_aggregated_contact_probs
		del leader_info_minimums_adjusted_values_only_contact_fields
		del leader_info_maximums_adjusted_values_only_contact_fields



	def get_positive_or_negative_memory_indexes(is_positive):
		# <!-- custom: similarly to contact aggregated code but for memory fields, that have positive/negative memory affection/resentment aggregated probs, see generate_leaders_data.py code or/and code comments for details anyways etc -->
		# <!-- custom: use memory indexes instead rather than types (string of full memory type name) as we fetch from DLL directly in sevopedia leader unlike in generate_leaders_data.py so we have access to these indexes so use them if i am not mistaken in my understanding anyways etc -->
		positive_or_negative_memory_indexes = None

		if is_positive:
			positive_or_negative_memory_indexes = tuple(get_positive_memory_indexes_to_types().keys())
		else:
			positive_or_negative_memory_indexes = tuple(get_negative_memory_indexes_to_types().keys())

		if not positive_or_negative_memory_indexes:
			raise ValueError("[VALUE ERROR] memory_indexes=%s check is false ; memory_indexes cannot be empty or missing or some other kind of related or similar error anyways etc, please check memory types (positive or negative) are fetched/imported correctly" % str(positive_or_negative_memory_indexes))
		
		return positive_or_negative_memory_indexes



	def compute_and_store_leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments(leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, is_positive, is_affection):
		positive_or_negative_memory_indexes = get_positive_or_negative_memory_indexes(is_positive)
		positive_negative = get_positive_negative(is_positive)
		affection_resentment = get_affection_resentment(is_affection)

		if IS_DEBUG_LEADER:
			print("[DEBUG] '0th' pass (preparation) (at is_positive=%s and is_affection=%s) of compute_and_store_leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments passed/success, positive_or_negative_memory_indexes=%s, positive_negative=%s, affection_resentment=%s" % (str(is_positive), str(is_affection), str(positive_or_negative_memory_indexes), positive_negative, affection_resentment))

		# <!-- custom: temporary storage to compute positive and negative raw aggregated affections and resentments, iLeader: { key: value } -->
		leaders_temp_positive_and_negative_memory_affections_and_resentments = {}

		# <!-- custom: this is even more temporary than leaders_temp_positive_and_negative_memory_affections_and_resentments as it is only a local variable used to compute min max during the positive or negative raw aggregated affection or resentment loop, so anyways etc no problem to recreate a new one everytime we reloop over compute_and_store_leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments if we ever do ; also note: this variable mimicks/has an identical structure to leader_info_minimums and leader_info_maximums in other parts of the code, but only storing respectively min and max among all leaders for some memory fields (note: so no iLeader (and no part in the iLeader loop anyways etc) since this is value among all leaders anyways etc), singular because we can think of leader_info_minimums as a fake leader having minimum among all leaders for each of its fields, and same/similar for leader_info_maximums anyways etc -->
		# <!-- custom: { key: value } -->
		leader_info_minimums_adjusted_values_only_memory_fields = {}
		leader_info_maximums_adjusted_values_only_memory_fields = {}

		# First pass: extract raw values and compute adjusted values (for scoring + min/max)
		for iLeader in range(gc.getNumLeaderHeadInfos()):
			if iLeader in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS:
				continue

			# <!-- custom: temporary field, no need to check if iLeader key exists before creating it, unlike for leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, anyways etc  -->
			leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader] = {}

			# <!-- custom: note: we get very weird bugs if misnaming variables, as python sadly or angrily for me xd stupidly anyways etc reuses variables from other loops even though they should not exist in another indepent scope other loop, so naming them with _0 _1 _2 _3 _4 for each pass to make sure python doesn't reuse them anwyays etc and we successfully get an error as intended if variable doesn't exist anyways etc -->

			# <!-- custom: skip negative memories if is_positive and vice versa anyways etc ; note: there is no such index skipping depending on memory type equivalent in the contact code (that uses range over all contact indexes (i.e. over all contact types if i am not mistaken anyways etc anyways etc) as we always process and handle all contact types the same (only difference is at display level where as of now we display them as contact offer or contact demand, but it is only a functional/visual difference if i am not mistaken anyways etc and computationally we handle them all the same, unlike memory types where the raw values are adjusted differently depending on whether memory type is positive or negative anyways etc) anyways etc -->
			for i in positive_or_negative_memory_indexes:
				value_1_attitude_percent_raw = gc.getLeaderHeadInfo(iLeader).getMemoryAttitudePercent(i)
				value_1_decay_raw = gc.getLeaderHeadInfo(iLeader).getMemoryDecayRand(i)
				mem_type_1 = gc.getMemoryInfo(i).getType() # e.g. "MEMORY_DECLARED_WAR"
				suffix_1 = get_pascal_case_suffix(mem_type_1) # → "DeclaredWar"
				
				# <!-- custom: this entire function is not where the real storage/parsing of these raw memory fields happens/is done (these raw fields storage/parsing is later in another function, at the same time of when we store/parse memory aggregated fields, if i am not mistaken, anyways etc anyways etc anyways etc) -->
				# <!-- custom: store raw_values for each leader first too anyways etc -->
				# <!-- custom: export raw attitude percents and decays only once out of the 4 combinations (among positive-affection, positive-resentment, negative-affection, negative-resentment, anyways etc), since the raw value is always the same field and field name, no need to do it again for the other 3 times/combinations anyways etc -->
				parsed_name_1_attitude_percent = "iMemoryAttitudePercent%s" % suffix_1 # → iMemoryAttitudePercentDeclaredWar
				if parsed_name_1_attitude_percent not in leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader]:
					leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_1_attitude_percent] = value_1_attitude_percent_raw

				parsed_name_1_decay = "iMemoryDecay%s" % suffix_1 # → iMemoryDecayDeclaredWar
				if parsed_name_1_decay not in leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader]:
					leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_1_decay] = value_1_decay_raw

				# <!-- custom: code comment from generate_leaders_data.py that is relevant here anyways etc so adding it anyways etc slightly modified (the code comment i mean anyways etc) for sevopedia leader anyways etc : adjusted positive memory fields or adjusted negative memory fields don't exist if i am not mistaken, all memory types (i.e. positive or negative) are adjusted the same way, only do they vary based on is_affection hence we only use affection and resentment versions of the adjusted temporary values to calculate the raw aggregated positive and negative memory affections and resentments if i am not mistaken indeed most likely maybe but maybe i am not (i.e. maybe i am not mistaken anyways etc) hopefully helpful or not too or yes too helpful i mean but anyways etc anyways etc anyways etc -->
				adjusted_value_1_attitude_percent_affection_or_resentment, adjusted_value_1_decay_affection_or_resentment, force_zero_adjusted_affection_or_resentment = get_adjusted_memory_values(value_1_attitude_percent_raw, value_1_decay_raw, is_affection, IS_DEBUG_LEADER, mem_type_1)
				parsed_name_1_adjusted_attitude_percent_affection_or_resentment = "iAdjustedMemoryAttitudePercent%s%s" % (suffix_1, affection_resentment) # → iAdjustedMemoryAttitudePercentDeclaredWarAffection or iAdjustedMemoryAttitudePercentDeclaredWarResentment
				parsed_name_1_adjusted_decay_affection_or_resentment = "iAdjustedMemoryDecay%s%s" % (suffix_1, affection_resentment) # → iAdjustedMemoryDecayDeclaredWarAffection or iAdjustedMemoryDecayDeclaredWarResentment
				parsed_name_1_force_zero_adjusted_affection_or_resentment = "bForceZeroMemory%s%s" % (suffix_1, affection_resentment) # → bForceZeroMemoryMemoryDecayDeclaredWarAffection or bForceZeroMemoryMemoryDecayDeclaredWarResentment
				leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_1_adjusted_attitude_percent_affection_or_resentment] = adjusted_value_1_attitude_percent_affection_or_resentment
				leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_1_adjusted_decay_affection_or_resentment] = adjusted_value_1_decay_affection_or_resentment
				leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_1_force_zero_adjusted_affection_or_resentment] = force_zero_adjusted_affection_or_resentment

		if IS_DEBUG_LEADER:
			print("[DEBUG] First pass (at is_positive=%s and is_affection=%s) of compute_and_store_leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments passed/success, leaders_temp_positive_and_negative_memory_affections_and_resentments=%s\n\n" % (str(is_positive), str(is_affection), str(leaders_temp_positive_and_negative_memory_affections_and_resentments)))

		# Second pass: Precompute min/max from adjusted values only <!-- custom: among all leaders anyways etc -->
		for iLeader in range(gc.getNumLeaderHeadInfos()):
			if iLeader in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS:
				continue

			for i in positive_or_negative_memory_indexes:
				mem_type_2 = gc.getMemoryInfo(i).getType() # e.g. "MEMORY_DECLARED_WAR"
				suffix_2 = get_pascal_case_suffix(mem_type_2) # → "DeclaredWar"
				parsed_name_2_adjusted_attitude_percent_affection_or_resentment = "iAdjustedMemoryAttitudePercent%s%s" % (suffix_2, affection_resentment) # → iAdjustedMemoryAttitudePercentDeclaredWarAffection or iAdjustedMemoryAttitudePercentDeclaredWarResentment
				parsed_name_2_adjusted_decay_affection_or_resentment = "iAdjustedMemoryDecay%s%s" % (suffix_2, affection_resentment) # → iAdjustedMemoryDecayDeclaredWarAffection or iAdjustedMemoryDecayDeclaredWarResentment
				# <!-- custom: no need to compute nor store min max for force zero so it is not a field we compare (it is a boolean specific to the current adjusted attitude_percent and decay, affection or resentment, if i am not mistaken, anyways etc anyways etc anyways etc) anyways etc, so also no need to parse name for it too at this min max step/pass anyways etc -->
				adjusted_value_2_attitude_percent_affection_or_resentment = leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_2_adjusted_attitude_percent_affection_or_resentment]
				adjusted_value_2_decay_affection_or_resentment = leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_2_adjusted_decay_affection_or_resentment]

				computeAndStoreMinMaxOfOneKey(parsed_name_2_adjusted_attitude_percent_affection_or_resentment, adjusted_value_2_attitude_percent_affection_or_resentment, leader_info_minimums_adjusted_values_only_memory_fields, leader_info_maximums_adjusted_values_only_memory_fields)
				computeAndStoreMinMaxOfOneKey(parsed_name_2_adjusted_decay_affection_or_resentment, adjusted_value_2_decay_affection_or_resentment, leader_info_minimums_adjusted_values_only_memory_fields, leader_info_maximums_adjusted_values_only_memory_fields)

		if IS_DEBUG_LEADER:
			print("[DEBUG] Second pass (at is_positive=%s and is_affection=%s) of compute_and_store_leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments passed/success, leaders_temp_positive_and_negative_memory_affections_and_resentments=%s\n\nleader_info_minimums_adjusted_values_only_memory_fields=%s\n\nleader_info_maximums_adjusted_values_only_memory_fields=%s\n\n" % (str(is_positive), str(is_affection), str(leaders_temp_positive_and_negative_memory_affections_and_resentments), str(leader_info_minimums_adjusted_values_only_memory_fields), str(leader_info_maximums_adjusted_values_only_memory_fields)))

		# Third pass: compute raw aggregate scores
		b_invert_attitude_percent, b_invert_decay = get_memory_attitude_percent_and_decay_invert_flags(is_positive, is_affection)
		
		for iLeader in range(gc.getNumLeaderHeadInfos()):
			if iLeader in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS:
				continue

			# <!-- custom: be careful, we loop 4 times over compute_and_store_leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, for positive-affection, positive-resentment, negative-affection, negative-resentment, so do not initalize this 4 times, we would lose 3/4 = 75% of the data otherwise anyways etc ; instead only initialize the iLeader key if it doesn't exist already (i.e. at 1st iteration/combination among the 4, for the other remaining 3 combinations, skip initialization as it would overwrite/delete all previously stored entries if i am not mistaken except the last iteration anyways etc) -->
			if not leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments.has_key(iLeader):
				leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments[iLeader] = {}

			for i in positive_or_negative_memory_indexes:
				mem_type_3 = gc.getMemoryInfo(i).getType() # e.g. "MEMORY_DECLARED_WAR"
				suffix_3 = get_pascal_case_suffix(mem_type_3) # → "DeclaredWar"
				parsed_name_3_adjusted_attitude_percent = "iAdjustedMemoryAttitudePercent%s%s" % (suffix_3, affection_resentment) # → iAdjustedMemoryAttitudePercentDeclaredWarAffection or iAdjustedMemoryAttitudePercentDeclaredWarResentment
				parsed_name_3_adjusted_decay = "iAdjustedMemoryDecay%s%s" % (suffix_3, affection_resentment) # → iAdjustedMemoryDecayDeclaredWarAffection or iAdjustedMemoryDecayDeclaredWarResentment
				parsed_name_3_force_zero_adjusted_affection_or_resentment = "bForceZeroMemory%s%s" % (suffix_3, affection_resentment) # → bForceZeroMemoryMemoryDecayDeclaredWarAffection or bForceZeroMemoryMemoryDecayDeclaredWarResentment
				adjusted_value_3_attitude_percent_affection_or_resentment = leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_3_adjusted_attitude_percent]
				adjusted_value_3_decay_affection_or_resentment = leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_3_adjusted_decay]
				force_zero_adjusted_affection_or_resentment = leaders_temp_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_3_force_zero_adjusted_affection_or_resentment]

				# <!-- custom: fetch min and max among all leaders already stored at previous step anyways etc, of adjusted values anyways etc anyways etc anyways etc -->
				adjusted_value_3_attitude_percent_affection_or_resentment_min = leader_info_minimums_adjusted_values_only_memory_fields[parsed_name_3_adjusted_attitude_percent]
				adjusted_value_3_attitude_percent_affection_or_resentment_max = leader_info_maximums_adjusted_values_only_memory_fields[parsed_name_3_adjusted_attitude_percent]
				adjusted_value_3_decay_affection_or_resentment_min = leader_info_minimums_adjusted_values_only_memory_fields[parsed_name_3_adjusted_decay]
				adjusted_value_3_decay_affection_or_resentment_max = leader_info_maximums_adjusted_values_only_memory_fields[parsed_name_3_adjusted_decay]
				# <!-- custom: no need to fetch force zero's min max (it also doesn't exist anyways etc) similarly as it is not a field we compare (it is a boolean specific to the current adjusted attitude_percent and decay, affection or resentment, if i am not mistaken, anyways etc anyways etc anyways etc) anyways etc -->

				adjusted_value_3_attitude_percent_affection_or_resentment_norm_score = normalize_to_100(adjusted_value_3_attitude_percent_affection_or_resentment, adjusted_value_3_attitude_percent_affection_or_resentment_min, adjusted_value_3_attitude_percent_affection_or_resentment_max, B_WARN, b_invert_attitude_percent, parsed_name_3_adjusted_attitude_percent)
				adjusted_value_3_decay_affection_or_resentment_norm_score = normalize_to_100(adjusted_value_3_decay_affection_or_resentment, adjusted_value_3_decay_affection_or_resentment_min, adjusted_value_3_decay_affection_or_resentment_max, B_WARN, b_invert_decay, parsed_name_3_adjusted_decay)
				aggregated_raw_positive_or_negative_memory_affection_or_resentment_score_from_adjusted_values = get_aggregated_raw_positive_or_negative_memory_affection_or_resentment_score_from_adjusted_values(adjusted_value_3_attitude_percent_affection_or_resentment_norm_score, adjusted_value_3_decay_affection_or_resentment_norm_score, force_zero_adjusted_affection_or_resentment)
				
				# <!-- custom: note: this is the the raw aggregated (i.e. the aggregated value before it is a normalized aggregated value, to not confound with raw values like raw attitude_percent and raw decay anyways etc) value that we then normalize and until after then store as part of the real leader info displayed later in the code (and then even more late(r? But anyways etc anyways etc...) in code anyways etc that we display at UI level anyways etc anyways etc anyways etc), this is a temporary value not the final one anyways etc anyways etc anyways etc... --->
				parsed_name_3_aggregated_raw_positive_or_negative_memory_affection_or_resentment = "iAggregatedRaw%sMemory%s%s" % (positive_negative, suffix_3, affection_resentment) # → iAggregatedRawPositiveMemoryDeclaredWarAffection or iAggregatedRawPositiveMemoryDeclaredWarResentment or iAggregatedRawNegativeMemoryDeclaredWarAffection or iAggregatedRawNegativeMemoryDeclaredWarResentment
				leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_3_aggregated_raw_positive_or_negative_memory_affection_or_resentment] = aggregated_raw_positive_or_negative_memory_affection_or_resentment_score_from_adjusted_values

		if IS_DEBUG_LEADER:
			print("[DEBUG] Third pass of compute_and_store_leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments passed/success, leaders_temp_positive_and_negative_memory_affections_and_resentments=%s\n\nleader_info_minimums_adjusted_values_only_memory_fields=%s\n\nleader_info_maximums_adjusted_values_only_memory_fields=%s\n\nleaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments=%s\n\n" % (str(leaders_temp_positive_and_negative_memory_affections_and_resentments), str(leader_info_minimums_adjusted_values_only_memory_fields), str(leader_info_maximums_adjusted_values_only_memory_fields), str(leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments)))

		# Fourth <!-- custom: actually third in sevopedia leader but named as such for consistency with generate_leaders_data.py pass numbering anyways etc --> pass: normalize final scores <!-- custom: is done later in the code anyways etc -->

		# <!-- custom: cleanup anyways etc -->
		del leaders_temp_positive_and_negative_memory_affections_and_resentments
		del leader_info_minimums_adjusted_values_only_memory_fields
		del leader_info_maximums_adjusted_values_only_memory_fields



	# <!-- custom: before computing minimums and maximums, compute and store raw aggregated fields, flattened, so they can be processed like any field/attribute and do min/max on them too for all leaders anyways etc -->
	compute_and_store_leaders_info_aggregated_raw_contact_probs(leaders_info_aggregated_raw_contact_probs)

	for is_positive in (True, False):
		for is_affection in (True, False):
			compute_and_store_leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments(leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, is_positive, is_affection)



	check_excluded_leaders_indexes_are_not_in_leaders_dict_keys(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS, leaders_info_aggregated_raw_contact_probs, "leaders_info_aggregated_raw_contact_probs", gc)
	check_leaders_dict_only_has_leader_index_keys(leaders_info_aggregated_raw_contact_probs, "leaders_info_aggregated_raw_contact_probs")

	check_excluded_leaders_indexes_are_not_in_leaders_dict_keys(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS, leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, "leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments", gc)
	check_leaders_dict_only_has_leader_index_keys(leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, "leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments")



	def get_fields_directly_parsed():
		# <!-- custom: dict of getter_name: (label, b_invert) if i am not mistaken anyways etc -->
		# <!-- custom: note: anyways etc --> Attributes that need value inversion when normalizing <!-- custom: is anyways etc when --> high = bad, low = good
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
			# <!-- custom: inverted according to: https://modiki.civfanatics.com/index.php/Civ4LeaderHeadInfos at "iCloseBordersAttitudeChange" and then according to also anyways etc https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#iclosebordersattitudechange (description translated(ion) seems a bit less accurate but is informative and helpful maybe etc -->
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
			# <!-- custom: attitude thresholds later in code in case we want to aggregate them or/and do aggregate them but not sure may or may not do anyways etc -->
			# ==== VASSAL AND FREEDOM FIELDS (from XML order) ====
			"getVassalPowerModifier": ("ResistCapitulP.M", False),
			"getFreedomAppreciation": ("FreedomApprec", False),
			# <!-- custom: then fields with nested or/and incremental getters (flavors, contacts, memory, nowarattitudeprobs, etc if any more anyways etc) are handled separately later anyways etc-->
		}

		# ==== ATTITUDE THRESHOLDS ====
		# <!-- custom: here even though debug code in debugPrintLeaderHeadInfoFieldsToFetch uses a dynamic code, manually tell all the getters names instead of a dynamic code, to make sure we have them all and since they have flat getters this is consistent with how other similar kind of field/getters are handled as before in this current tuple i mean anyways etc ; their names are available in the debug output example of the same debugPrintLeaderHeadInfoFieldsToFetch, see there for details -->
		fields_attitude_thresholds = {
			# <!-- custom: inverted according to: https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#demandtributeattitudethreshold anyways etc -->
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
			# <!-- custom: inverted according to: https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#declarewarthemrefuseattitudethreshold anyways etc -->
			"getDeclareWarThemRefuseAttitudeThreshold": ("LoyaltyNoD.W", True),
			"getStopTradingRefuseAttitudeThreshold": ("StopTr", False),
			# <!-- custom: inverted according to: https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#stoptradingthemrefuseattitudethreshold anyways etc -->
			"getStopTradingThemRefuseAttitudeThreshold": ("LoyaltyNoStopTr", True),
			"getAdoptCivicRefuseAttitudeThreshold": ("Adopt Civic", False),
			"getConvertReligionRefuseAttitudeThreshold": ("Convert Religion", False),
			"getOpenBordersRefuseAttitudeThreshold": ("Open Borders", False),
			"getDefensivePactRefuseAttitudeThreshold": ("Defensive Pact", False),
			"getPermanentAllianceRefuseAttitudeThreshold": ("Perm. Alliance", False),
			"getVassalRefuseAttitudeThreshold": ("Vassal", False),
		}

		return fields_with_direct_getters, fields_attitude_thresholds



	# <!-- custom: store only the fields we want to display in the AI personality panel not the other / not all XML fields, see sevopedia helpers py file and debugPrintLeaderHeadInfoFieldsToFetch and or its example of output for details anyways etc -->
	fields_with_direct_getters, fields_attitude_thresholds = get_fields_directly_parsed()



	def get_leader_info_minimums_and_maximums(fields_with_direct_getters, fields_attitude_thresholds, leaders_info_aggregated_raw_contact_probs, leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments):
		# <!--- custom: fake leaders that stores minimum values among all leader for each field we want to display regardless of inversions anyways etc, same for maximum values too anyways etc -->
		leader_info_minimums = {}
		leader_info_maximums = {}

		for iLeader in range(gc.getNumLeaderHeadInfos()):
			if iLeader in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS:
				continue

			for getter_name, (label, b_invert) in fields_with_direct_getters.items():
				value_generic = getattr(gc.getLeaderHeadInfo(iLeader), getter_name)()
				computeAndStoreMinMaxOfOneKey(getter_name, value_generic, leader_info_minimums, leader_info_maximums)

			for getter_name, (label, b_invert) in fields_attitude_thresholds.items():
				value_attitude_threshold = getattr(gc.getLeaderHeadInfo(iLeader), getter_name)()
				computeAndStoreMinMaxOfOneKey(getter_name, value_attitude_threshold, leader_info_minimums, leader_info_maximums)

			# <!-- custom: parse fields with nested or/and with incremental getters as flat fields with an alternative key so we can loop over them more easily and reorder them later if need(ed?) anyways etc, also our code is more consistent this way anyways etc -->
			# ==== FLAVORS ====
			for i in range(gc.getNumFlavorTypes()):
				# <!-- custom: store them as a parsed key name since getter is incremental and does nto directly reference the name of each flavor if i am not mistaken anyways etc -->
				value_flavor = gc.getLeaderHeadInfo(iLeader).getFlavorValue(i)
				flavor_type = gc.getFlavorTypes(i)  # e.g. "FLAVOR_MILITARY"
				suffix = get_pascal_case_suffix(flavor_type) # → <!-- custom: "Military" anyways etc -->
				parsed_name_flavor = "iFlavor%s" % suffix  # → iFlavorMilitary
				computeAndStoreMinMaxOfOneKey(parsed_name_flavor, value_flavor, leader_info_minimums, leader_info_maximums)

			# ==== CONTACTS ====
			for i in range(NUM_CONTACT_TYPES_ASSESSED):
				# <!-- custom: compute minimum and maximum among all leaders for raw contact fields, which here and as of now if i am not mistaken are only contact rands and contact delays anyways etc -->
				# <!-- custom: Step 1: Raw contact rands and delays -->
				contact_type = gc.getContactTypes(i) # e.g. "CONTACT_JOIN_WAR"
				suffix = get_pascal_case_suffix(contact_type) # → "JoinWar"

				value_rand_raw = gc.getLeaderHeadInfo(iLeader).getContactRand(i)
				value_delay_raw = gc.getLeaderHeadInfo(iLeader).getContactDelay(i)
				parsed_name_rand = "iContactRand%s" % suffix # → iContactRandJoinWar
				parsed_name_delay = "iContactDelay%s" % suffix # → iContactDelayJoinWar
				computeAndStoreMinMaxOfOneKey(parsed_name_delay, value_delay_raw, leader_info_minimums, leader_info_maximums)
				computeAndStoreMinMaxOfOneKey(parsed_name_rand, value_rand_raw, leader_info_minimums, leader_info_maximums)

				# <!-- custom: also export the minimum and maximum raw aggregated contact prob (based on iLeader's rand and iLeader's delay (note: not based on the min and max rand among all leaders nor the min and max delay among all leaders)) among all leaders for each contact type anyways etc -->
				# <!-- custom: Step 2: Raw aggregated contact probs anyways etc -->
				parsed_name_aggregated_raw_contact_prob = "iAggregatedRawContactProb%s" % suffix # → iAggregatedRawContactProbJoinWar
				value_aggregated_raw_contact_prob = leaders_info_aggregated_raw_contact_probs[iLeader][parsed_name_aggregated_raw_contact_prob]
				computeAndStoreMinMaxOfOneKey(parsed_name_aggregated_raw_contact_prob, value_aggregated_raw_contact_prob, leader_info_minimums, leader_info_maximums)

			# ==== MEMORY ====
			# <!-- custom: compute minimum and maximum among all leaders for raw contact fields, which here and as of now if i am not mistaken are only contact rands and contact delays anyways etc ; here we can loop over real DLL i index directly like in sevopedia_helpers py file debug code (see there for details if hopefully it is/can be/maybe is anyways etc helpful too but anyways etc anyways etc anyways etc), and unlike for raw aggregated memory fields that are separated in positive and negative memories, so here we can loop over real DLL i index directly anyways etc -->
			for is_positive in (True, False):
				for is_affection in (True, False):
					positive_or_negative_memory_indexes = get_positive_or_negative_memory_indexes(is_positive)
					positive_negative = get_positive_negative(is_positive)
					affection_resentment = get_affection_resentment(is_affection)

					for i in positive_or_negative_memory_indexes:
						memory_type = gc.getMemoryInfo(i).getType() # e.g. "MEMORY_DECLARED_WAR"
						suffix = get_pascal_case_suffix(memory_type) # → "DeclaredWar"

						# <!-- custom: Step 1: Raw memory attitude percents and decays -->
						# <!-- custom: since we display same raw attitude percent and decay fields values in UI regardless of positive/negative memory affection/resentment (raw aggregated values then the normalized aggregated values are is displayed anyways etc) aggregation, no need to store multiple versions (i.e. positive/negative and affection/resentment) of these raw attitude percent and decay fields, store only one kind for all of these 4 possible combination cases (positive-affection, positive-resentment, negative-affection, negative-resentment anyways etc) same as in XML fields structuration too for raw attitude percents and decays anyways etc anyways etc anyways etc, i.e. for example only for example iMemoryAttitudePercentDeclaredWar (no positive-negative, no affection-resentment) for raw attitude_percent and decay fields same as in XML anyways etc -->
						# <!-- custom: similarly for min max of raw attitude percents and decays export anyways etc only once out of the 4 combinations (among positive-affection, positive-resentment, negative-affection, negative-resentment, anyways etc), since the raw value is always the same field and field name, no need to do it again for the other 3 times/combinations anyways etc -->
						parsed_name_attitude_percent = "iMemoryAttitudePercent%s" % suffix # → iMemoryAttitudePercentDeclaredWar
						if (parsed_name_attitude_percent not in leader_info_minimums) and (parsed_name_attitude_percent not in leader_info_maximums):
							value_attitude_percent = gc.getLeaderHeadInfo(iLeader).getMemoryAttitudePercent(i)
							computeAndStoreMinMaxOfOneKey(parsed_name_attitude_percent, value_attitude_percent, leader_info_minimums, leader_info_maximums)

						parsed_name_decay = "iMemoryDecay%s" % suffix # → iMemoryDecayDeclaredWar
						if (parsed_name_decay not in leader_info_minimums) and (parsed_name_decay not in leader_info_maximums):
							value_decay = gc.getLeaderHeadInfo(iLeader).getMemoryDecayRand(i)
							computeAndStoreMinMaxOfOneKey(parsed_name_decay, value_decay, leader_info_minimums, leader_info_maximums)

						# <!-- custom: Step 2: Raw aggregated positive and negative memory affections and resentments anyways etc -->
						parsed_name_aggregated_raw_positive_or_negative_memory_affection_or_resentment = "iAggregatedRaw%sMemory%s%s" % (positive_negative, suffix, affection_resentment) # → iAggregatedRawPositiveMemoryDeclaredWarAffection or iAggregatedRawPositiveMemoryDeclaredWarResentment or iAggregatedRawNegativeMemoryDeclaredWarAffection or iAggregatedRawNegativeMemoryDeclaredWarResentment
						value_aggregated_raw_positive_or_negative_memory_affection_or_resentment = leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_aggregated_raw_positive_or_negative_memory_affection_or_resentment]
						computeAndStoreMinMaxOfOneKey(parsed_name_aggregated_raw_positive_or_negative_memory_affection_or_resentment, value_aggregated_raw_positive_or_negative_memory_affection_or_resentment, leader_info_minimums, leader_info_maximums)

			# ==== NOWARATTITUDEPROBS ====
			for i in range(NUM_ATTITUDE_TYPES_ASSESSED):
				value_no_war_attitude_prob = gc.getLeaderHeadInfo(iLeader).getNoWarAttitudeProb(i)
				attitude_type = gc.getAttitudeInfo(i).getType()  # e.g. "ATTITUDE_FURIOUS"
				suffix = get_pascal_case_suffix(attitude_type)  # → "Furious"
				parsed_name_no_war_attitude_prob = "iNoWarAttitudeProb%s" % suffix  # → iNoWarAttitudeProbFurious
				computeAndStoreMinMaxOfOneKey(parsed_name_no_war_attitude_prob, value_no_war_attitude_prob, leader_info_minimums, leader_info_maximums)
		
		# <!-- custom: after all min and max parsing is done, some sanity and warning checks -->
		for key in leader_info_minimums:
			# <!-- custom: ensure our leader_info_minimums is reliable even if a bit if not lot or not or yes or etc but anyways etc before proceeding further anyways etc -->
			if key not in leader_info_maximums:
				raise KeyError(u"[KEY ERROR] Missing leader_info_maximums key=%s, in leader_info_minimums but not in leader_info_maximums, cannot proceed if both leader_info_minimums and leader_info_maximums all have same keys, please check your min and max computing or and DLL behaviour that may explain missing fields." % key)

			# <!-- custom: also warn once if min == max for each field/key and now while it is computationally (at module load) inexpensive to do so anyways etc, do not rewarn at each leader computation nor later at init or and such anyways etc -->
			if leader_info_minimums[key] == leader_info_maximums[key]:
				if IS_DEBUG_LEADER:
					print("[WARNING] Key=%s has an identical min and max value (%d). Warning only once at module load so we don't have/want/need to redo it later at the normalization stage, fix/change the XML leader info value(s) of some leader(s) so that min and max among all leaders are different if desired, or keep as is if intended/desired that leaders behave the same for this key." % (key, leader_info_minimums[key]))
		
		if IS_DEBUG_LEADER:
			print("[DEBUG] At end of the function get_leader_info_minimums_and_maximums, we return for the minimums leader_info_minimums=%s" % leader_info_minimums)
			print("[DEBUG] At end of the function get_leader_info_minimums_and_maximums, we return for the maximums leader_info_maximums=%s" % leader_info_maximums)

		return (leader_info_minimums, leader_info_maximums)



	leader_info_minimums, leader_info_maximums = get_leader_info_minimums_and_maximums(fields_with_direct_getters, fields_attitude_thresholds, leaders_info_aggregated_raw_contact_probs, leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments)

	# <!-- custom: note: leader_info_minimums, leader_info_maximums are like fake leaders, they dont have iLeader keys but only field/attribute keys (like "getMaxWarRand", "iAggregatedEtc...", "getBasePeaceWeight", "iFlavorMilitary", etc), so no need and not relevant to check if excluded leaders or if keys are only indexes because they are not in this case i mean, anyways etc, we have enough sanity checks overall everywhere to not need to resanity check this xd if i may say even though may help maybe but anyways etc is bit tedious since dbug also helps if i may say but anyways etc (see SevopediaLead_derExamplesOfOutputs.txt or whichever file it is named if still in this mod Sevopedia folder for example of outputs anyways etc), so as for sanity checks skipping them for leader_info_minimums, leader_info_maximums anywayse tc hopefully helpful or not or yes or etc or and other or and not or yes or etc anwyays etc but anyways etc anyways etc anyways etc -->



	# Store per-leader <!-- custom: cached info for all keys/attributes anyways etc -->
	# LEADERS_INFO_CACHED: dict of leaderName → dict of attributeName → <!-- custom: tuple of (label, raw_value, norm_value, scale) for later display at UI code anyways etc -->
	LEADERS_INFO_CACHED = {}



	def compute_and_store_leaders_info_cached(leaders_info_aggregated_raw_contact_probs, leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments, fields_with_direct_getters, fields_attitude_thresholds, leader_info_minimums, leader_info_maximums):
		# Loops over all leaders and normalizes each attribute to a 0-100 scale, using previously computed min/max per attribute and inversion flags.

		# --- Symbol settings ---
		all_symbols = {
			"RAW_SCALE_SYMBOL": "+",
			"AGGREGATED_SCALE_SYMBOL": "#",
			"EQUAL_SCALE_SYMBOL": "=",
		}

		# <!-- custom: in the debug output (i=0 to NUM_CONTACT_TYPES_ASSESSED (i=13 so 14 values in total as of now if i am not mistaken anyways etc see latest value or/and code comments or/and docs for updated value or and info hopefully helpful or not or yes or etc anyways etc) anyways etc) order anyways etc -->
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

		# <!-- custom: a minimal anyways etc sanity check before merging the index_labels anyways etc (not checking if some indexes are missing here in the dictionary as we'd likely i assume if i am not mistaken anyways etc get a key error later otherwise anyways etc -->
		check_overlapping_keys_between_dicts(positive_memory_index_labels, negative_memory_index_labels)
		# ✅ Combined dictionary
		positive_and_negative_memory_index_labels = {}
		positive_and_negative_memory_index_labels.update(positive_memory_index_labels)
		positive_and_negative_memory_index_labels.update(negative_memory_index_labels)

		# --- Utility ---
		# <!-- custom: examples:
		# - with symbol "+" and value 64 (/100), returns "++++++" if i'm not mistaken anyways
		# - with symbol "#" and value 39 (/100), returns "###" if i'm not mistaken anyways
		# -->
		def get_symbol_scale(score, symbol):
			return symbol * (score // 10)

		def compute_and_store_leader_info_cached_tuple(raw_value, min_value, max_value, b_invert, symbol, cache_key, label, leader_info_cached):
			norm_value = normalize_to_100(raw_value, min_value, max_value, B_WARN, b_invert, cache_key)

			if (min_value == max_value):
				symbol = all_symbols["EQUAL_SCALE_SYMBOL"]

			if IS_DEBUG_LEADER:
				print("[DEBUG] raw_value=%d, min_value=%d, max_value=%d, norm_value=%d, for cache_key=%s, b_invert=%s at iLeader=%d" % (raw_value, min_value, max_value, norm_value, cache_key, b_invert, iLeader))

			if not label:
				raise ValueError(u"Unexpected label=%s tested false as a boolean in cache_key=%s at iLeader=%d, please check label is not empty or missing or some other kind of invalid format" % (str(label), cache_key, iLeader))

			if (symbol not in all_symbols.values()):
				raise ValueError(u"Unexpected symbol=%s not in all_symbols=%s in cache_key=%s at iLeader=%d." % (symbol, str(all_symbols), cache_key, iLeader))
			scale = get_symbol_scale(norm_value, symbol)

			# Store final as <!-- custom: a tuple after all parsing/caching is finished for this leader for faster/better performance than dict or such other storage if i am not mistaken anyways etc --> for future display at UI code anyways etc
			leader_info_cached_tuple = (label, norm_value, scale)
			leader_info_cached[cache_key] = leader_info_cached_tuple
			if IS_DEBUG_LEADER:
				print(u"[DEBUG] Leader info cached tuple for iLeader=%d is leader_info_cached_tuple=%s" % (iLeader, str(leader_info_cached_tuple)))

		for iLeader in range(gc.getNumLeaderHeadInfos()):
			if iLeader in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS:
				continue

			leader_info_cached = {}

			# <!-- custom: note: later in the code at UI stage or somewhere after the whole compute_and_store_leaders_info_cached caching function anyways etc, to access the tuple line to display in the table for non-agrgegated and perhaps some other ai attributes or not anyways etc, we may use for some attributes the getter name as a key but we don't call it, it is just more conveninent to store it this way as this is consistent with existing getter name and we didn't flatten field/attribute since it was not nested xml so no need to use another key name than one that starts with "get" for this field/attribute anyways etc, it is still a flat one, so do at load for example for iLeader = 5 dynamically while in the UI loop per attribute/key if i am not mistaken anyways etc LEADERS_INFO_CACHED[5]["getBaseAttitude"] to access the tuple to display, while for some other attributes/fields anyways etc we may use an "i" type of key name such as for some nested fields like flavors for example anyways etc LEADERS_INFO_CACHED[5]["iFlavorMilitary"] since we flatten them as such if i am not mistaken anyways etc, vs also for some other nested fields like aggregated attributes for example similarly (if other kind of fields exist, as of now not but is to be exhaustive or as it is or and other or and not but anyways etc) instead we may do for example anyways etc LEADERS_INFO_CACHED[5]["iAggregatedNegativeMemoryHiredTradeEmbargoResentment"] (not using a "get" getter name for the key here either, but these are all key names regardless of "i" or "get" or other name/prefix in key name to access in LEADERS_INFO_CACHED if i am not mistaken anyways etc that we don't call like getters even if there is a "get", but only use as key names anyways etc), hopefully clearer or/and helps maybe ideally or nto or yes or etc understand or see how it works-functions but or not but or yes but but anyways etc anyways etc anyways etc, i find it quite plesant design this way, but anyways etc -->
			symbol_generics = all_symbols["RAW_SCALE_SYMBOL"]
			for getter_name_generic, (label_generic, b_invert_generic) in fields_with_direct_getters.items():
				raw_value_generic = getattr(gc.getLeaderHeadInfo(iLeader), getter_name_generic)()
				min_value_generic = leader_info_minimums[getter_name_generic]
				max_value_generic = leader_info_maximums[getter_name_generic]
				# <!-- custom: also add raw value to label like "Military (12)" for example for flavors instead of just "Military" (so we have both raw value in label as well as normalized value in the 2nd column of each of the AI personality panel tables anyways etc (i.e. before the scale (e.g. "++++" or similar anyways etc column of each of the AI personality panel tables too anyways etc-->
				label_with_raw_value_generic = "%s (%d)" % (label_generic, raw_value_generic)
				compute_and_store_leader_info_cached_tuple(raw_value_generic, min_value_generic, max_value_generic, b_invert_generic, symbol_generics, getter_name_generic, label_with_raw_value_generic, leader_info_cached)

			symbol_attitude_thresholds = all_symbols["RAW_SCALE_SYMBOL"]
			for getter_name_attitude_threshold, (label_attitude_threshold, b_invert_attitude_threshold) in fields_attitude_thresholds.items():
				raw_value_attitude_threshold = getattr(gc.getLeaderHeadInfo(iLeader), getter_name_attitude_threshold)()
				min_value_attitude_threshold = leader_info_minimums[getter_name_attitude_threshold]
				max_value_attitude_threshold = leader_info_maximums[getter_name_attitude_threshold]
				label_with_raw_value_attitude_threshold = "%s (%d)" % (label_attitude_threshold, raw_value_attitude_threshold)
				compute_and_store_leader_info_cached_tuple(raw_value_attitude_threshold, min_value_attitude_threshold, max_value_attitude_threshold, b_invert_attitude_threshold, symbol_attitude_thresholds, getter_name_attitude_threshold, label_with_raw_value_attitude_threshold, leader_info_cached)

			b_invert_flavors = False
			symbol_flavors = all_symbols["RAW_SCALE_SYMBOL"]
			for i in range(gc.getNumFlavorTypes()):
				raw_value_flavor = gc.getLeaderHeadInfo(iLeader).getFlavorValue(i)
				flavor_type = gc.getFlavorTypes(i)  # e.g. "FLAVOR_MILITARY"
				suffix = get_pascal_case_suffix(flavor_type) # → <!-- custom: "Military" anyways etc -->
				parsed_name_flavor = "iFlavor%s" % suffix  # → iFlavorMilitary
				min_value_attitude_flavor = leader_info_minimums[parsed_name_flavor]
				max_value_attitude_flavor = leader_info_maximums[parsed_name_flavor]
				label_flavor = suffix # <!-- custom: → "Military" -->
				label_with_raw_value_flavor = "%s (%d)" % (label_flavor, raw_value_flavor)
				compute_and_store_leader_info_cached_tuple(raw_value_flavor, min_value_attitude_flavor, max_value_attitude_flavor, b_invert_flavors, symbol_flavors, parsed_name_flavor, label_with_raw_value_flavor, leader_info_cached)

			# <!-- custom: for contact fields, normalize the aggregated contact probs, do not normalize the rands nor the delays (would be redundant, as we don't display them with scale symbols or such, just the raw value in label is enough anyways etc) ; to export raw fields (rand and delay if i am not mistaken anyways etc, uncomment the related rand and delay lines below (untested but probably works-functions else tweak bit anyways etc) to export them to UI if want to display them (then you'd need to uncomment or add if missing them anyways etc in UI categories too anyways etc)) -->
			# b_invert_contact_rands, b_invert_contact_delays = get_contact_rand_and_decay_invert_flags()
			# symbol_contact_rands_delays = all_symbols["RAW_SCALE_SYMBOL"]

			b_invert_4_aggregated_contact_probs = False
			symbol_aggregated_contact_probs = all_symbols["AGGREGATED_SCALE_SYMBOL"]
			for i in range(NUM_CONTACT_TYPES_ASSESSED):
				contact_type = gc.getContactTypes(i) # e.g. "CONTACT_JOIN_WAR"
				suffix = get_pascal_case_suffix(contact_type) # → "JoinWar"
				label_contact = contact_index_labels[i]

				# raw_value_rand = gc.getLeaderHeadInfo(iLeader).getContactRand(i)
				# parsed_name_rand = "iContactRand%s" % suffix # → iContactRandJoinWar
				# min_value_rand = leader_info_minimums[parsed_name_rand]
				# max_value_rand = leader_info_maximums[parsed_name_rand]
				# label_with_raw_value_rand = "%s (%d)" % (label_contact, raw_value_rand)
				# compute_and_store_leader_info_cached_tuple(raw_value_rand, min_value_rand, max_value_rand, b_invert_contact_rands, symbol_contact_rands_delays, parsed_name_rand, label_with_raw_value_rand, leader_info_cached)

				# raw_value_delay = gc.getLeaderHeadInfo(iLeader).getContactDelay(i)
				# parsed_name_delay = "iContactDelay%s" % suffix # → iContactDelayJoinWar
				# min_value_delay = leader_info_minimums[parsed_name_delay]
				# max_value_delay = leader_info_maximums[parsed_name_delay]
				# label_with_raw_value_delay = "%s (%d)" % (label_contact, raw_value_delay)
				# compute_and_store_leader_info_cached_tuple(raw_value_delay, min_value_delay, max_value_delay, b_invert_contact_delays, symbol_contact_rands_delays, parsed_name_delay, label_with_raw_value_delay, leader_info_cached)


				# <!-- custom: then back to aggregated contact fields, the ones that we display at least as of now anyways etc , --> Fourth <!-- custom: actually third in sevopedia leader but named as such for consistency with generate_leaders_data.py pass numbering anyways etc --> pass: normalize final scores
				# <!-- custom: now transform the raw aggregated prob into a normalized aggregated prob that we store and export for UI display anyways etc -->
				parsed_name_4_aggregated_raw_contact_prob = "iAggregatedRawContactProb%s" % suffix # → iAggregatedRawContactProbJoinWar
				raw_value_4_aggregated_contact_prob = leaders_info_aggregated_raw_contact_probs[iLeader][parsed_name_4_aggregated_raw_contact_prob]
				# <!-- custom: be careful/note anyways etc, min and max value are stored under the raw aggregated value and thus key, not the normalized aggregated one, use raw aggregated key to access them in leader_info minimums and same for maximums (normalized key does not exist yet, would get an error, anyways etc) -->
				min_value_4_aggregated_raw_contact_prob = leader_info_minimums[parsed_name_4_aggregated_raw_contact_prob]
				max_value_4_aggregated_raw_contact_prob = leader_info_maximums[parsed_name_4_aggregated_raw_contact_prob]

				# <!-- custom: generate the label before normalizing, and so we also have the label as well for later display after normalization done anyways etc in/at UI anyways etc -->
				raw_value_rand = gc.getLeaderHeadInfo(iLeader).getContactRand(i)
				raw_value_delay = gc.getLeaderHeadInfo(iLeader).getContactDelay(i)
				label_aggregated_contact_prob = "%s (%d/%d)" % (label_contact, raw_value_rand, raw_value_delay)

				# <!-- custom: be careful/note anyways etc: the normalized aggregated value is not stored in cache with the old pre-normalization key/parsed_name, so we remove "raw" here in key/parsed_name anyways etc since aggregated value is normalized now, so use for caching the new key/parsed_name that does not have "raw" in key for aggregated fields at least for aggregated contact probs caching anyways etc -->
				parsed_name_4_aggregated_contact_prob = "iAggregatedContactProb%s" % suffix # → iAggregatedContactProbJoinWar
				compute_and_store_leader_info_cached_tuple(raw_value_4_aggregated_contact_prob, min_value_4_aggregated_raw_contact_prob, max_value_4_aggregated_raw_contact_prob, b_invert_4_aggregated_contact_probs, symbol_aggregated_contact_probs, parsed_name_4_aggregated_contact_prob, label_aggregated_contact_prob, leader_info_cached)

			# <!-- custom: similarly for memory fields, we don't need the raw attitude_percent and decay since they are already in label and we don't display them normalized otherwise either (or neither? But anyways etc...) anyways etc, so normalize only aggregated positive and negative memory affections and resentments, but more specifically also, we don't display positive memory resentments and negative memory affections due to table being too small for these all but anyways etc and/but also our XML being otherwise quite straightforward at least as of now if not always or not, as positive memories all have a positive attitude_percent if i'm not mistaken and same or similarly rather anyways etc negative memories all have a negative atittude_percent, so positive memory resentments and negative memory affections would just perfectly overlap and be redundant with positive memory affections and negative memory resentments, so don't display them in our mod advciv-sas at least as of now if not most likely always in advciv-sas or maybe not but most likely anyways etc. But the feature is there if some mods want to display it, and i think it's very cool to have masochistic (negative memory affections) and/or bitterly ungrateful (positive memory resentments), so code comment code samples or rather maybe lines anyways etc if you want to support it in your mod, remember to also add these fields (parsed_name (parsed names for all fields actually but anyways etc)) in UI categories too and order them as you see fit if you'd want that, which i think is very cool and wish i did and could do, but table is already too full, and i dont have such a crazy in a way i like hehe leader as of yet (or yet? Simply? But anyways etc...) if not always or maybe not but most likely in this case i mean anyways etc, but in all cases, regardless of which, uncomment if you want to add positive memory resentments and negative memory resentments, same also for raw memory attitude_percents and decays not displayed as well since they are in label of aggregated field and we don't otherwise need them, anyways etc -->

			#symbol_memory_attitude_percents_decays = all_symbols["RAW_SCALE_SYMBOL"]
			b_invert_4_positive_and_negative_memory_affections_and_resentments = False
			symbol_aggregated_positive_and_negative_memory_affections_and_resentments = all_symbols["AGGREGATED_SCALE_SYMBOL"]

			for is_positive in (True, False):
				for is_affection in (True, False):
					# <!-- custom: skip positive memory resentments and negative memory affections as said in top code comment before if i may say anyways etc, uncomment or remove this/these checks anyways etc to export them as well anyways etc-->
					if is_positive and (not is_affection):
						continue
					if (not is_positive) and is_affection:
						continue

					positive_or_negative_memory_indexes = get_positive_or_negative_memory_indexes(is_positive)
					positive_negative = get_positive_negative(is_positive)
					affection_resentment = get_affection_resentment(is_affection)

					# b_invert_attitude_percents, b_invert_decays = get_memory_attitude_percent_and_decay_invert_flags(is_positive, is_affection)

					for i in positive_or_negative_memory_indexes:
						memory_type = gc.getMemoryInfo(i).getType() # e.g. "MEMORY_DECLARED_WAR"
						suffix = get_pascal_case_suffix(memory_type) # → "DeclaredWar"
						label_positive_or_negative_memory_affection_or_resentment = positive_and_negative_memory_index_labels[i]

						# <!-- custom: for positive and negative memory affection and resentment fields, normalize the aggregated positive and negative memory affections and resentments, do not normalize the atittude percents nor the decays (would be redundant similarly as for contact fields anyways etc) (also export of these raw fields (attitude percents and decays is untested as we don't need them at least untested as of now i mean but anyways etc simialrly to contact field, may or not function, i assume it would or with minimal tweaks or fixes if any are needed, plus would need to add UI logic or ordering to display them rather if want in another mod for example, unlikely we would in advciv-sas as redundant with aggregated fields as said before in this code comment too i mean anyways etc anyways etc even though not 100% sure sure but most likely anyways etc)) -->

						# <!-- custom: export raw attitude percents and decays only once out of the 4 combinations (among positive-affection, positive-resentment, negative-affection, negative-resentment, anyways etc), since the raw value is always the same field and field name, no need to do it again for the other 3 times/combinations anyways etc -->
						# parsed_name_attitude_percent = "iMemoryAttitudePercent%s" % suffix # → iMemoryAttitudePercentDeclaredWar
						# if parsed_name_attitude_percent not in leader_info_cached:
						# 	raw_value_attitude_percent = gc.getLeaderHeadInfo(iLeader).getMemoryAttitudePercent(i)
						#   min_value_attitude_percent = leader_info_minimums[parsed_name_attitude_percent]
						#   max_value_attitude_percent = leader_info_maximums[parsed_name_attitude_percent]
						#   label_positive_or_negative_memory_with_raw_value_attitude_percent = "%s (%d)" % (label_positive_or_negative_memory, raw_value_attitude_percent)
						# 	compute_and_store_leader_info_cached_tuple(raw_value_attitude_percent, min_value_attitude_percent, max_value_attitude_percent, b_invert_attitude_percents, symbol_memory_attitude_percents_decays, parsed_name_attitude_percent, label_positive_or_negative_memory_with_raw_value_attitude_percent, leader_info_cached)
						#
						# parsed_name_decay = "iMemoryDecay%s" % suffix # → iMemoryDecayDeclaredWar
						# if parsed_name_decay not in leader_info_cached:
						# 	raw_value_decay = gc.getLeaderHeadInfo(iLeader).getMemoryDecayRand(i)
						#   min_value_decay = leader_info_minimums[parsed_name_decay]
						#   max_value_decay = leader_info_maximums[parsed_name_decay]
						#   label_positive_or_negative_memory_with_raw_value_decay = "%s (%d)" % (label_positive_or_negative_memory, raw_value_decay)
						# 	compute_and_store_leader_info_cached_tuple(raw_value_decay, min_value_decay, max_value_decay, b_invert_decays, symbol_memory_attitude_percents_decays, parsed_name_decay, label_positive_or_negative_memory_with_raw_value_decay, leader_info_cached)


						# <!-- custom: then back to aggregated positive and negative memory affection and resentment fields, the ones that we display at least as of now anyways etc , --> Fourth <!-- custom: actually third in sevopedia leader but named as such for consistency with generate_leaders_data.py pass numbering anyways etc --> pass: normalize final scores
						# <!-- custom: now transform the raw aggregated prob into a normalized aggregated prob that we store and export for UI display anyways etc -->
						# <!-- custom: note: unlike for min max exports (compute and store i mean anyways etc) of raw, we can do positive and negative memory affections and resentments aggregated normalization at same time without having to relooping/having to anyways etc reloop over positive_or_negative_memory_indexes as the raw aggregated prob is now a flat field at this normalization stage, that is already available for all leaders, so we can normalize it directly and independently from the raw memory attitude percents and decays if i am not mistaken in my understanding anyways etc, see also min max code of memory fields at step 1 step 2 or similar code comments for details if i am not mistaken too but anyways etc anyways etc anyways etc -->
						parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment = "iAggregatedRaw%sMemory%s%s" % (positive_negative, suffix, affection_resentment) # → iAggregatedRawPositiveMemoryDeclaredWarAffection or iAggregatedRawPositiveMemoryDeclaredWarResentment or iAggregatedRawNegativeMemoryDeclaredWarAffection or iAggregatedRawNegativeMemoryDeclaredWarResentment
						raw_value_4_aggregated_positive_or_negative_memory_affection_or_resentment = leaders_info_aggregated_raw_positive_and_negative_memory_affections_and_resentments[iLeader][parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment]
						# <!-- custom: be careful/note anyways etc, min and max value are stored under the raw aggregated value and thus key, not the normalized aggregated one, use raw aggregated key to access them in leader_info minimums and same for maximums (normalized key does not exist yet, would get an error, anyways etc) -->
						min_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment = leader_info_minimums[parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment]
						max_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment = leader_info_maximums[parsed_name_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment]

						# <!-- custom: generate the label before normalizing, and so we also have the label as well for later display after normalization done anyways etc in/at UI anyways etc -->
						raw_value_4_attitude_percent = gc.getLeaderHeadInfo(iLeader).getMemoryAttitudePercent(i)
						raw_value_4_decay = gc.getLeaderHeadInfo(iLeader).getMemoryDecayRand(i)
						label_aggregated_positive_or_negative_memory_affection_or_resentment = "%s (%d/%d)" % (label_positive_or_negative_memory_affection_or_resentment, raw_value_4_attitude_percent, raw_value_4_decay)

						# <!-- custom: be careful/note anyways etc: the normalized aggregated value is not stored in cache with the old pre-normalization key/parsed_name, so we remove "raw" here in key/parsed_name anyways etc since aggregated value is normalized now, so use for caching the new key/parsed_name that does not have "raw" in key for aggregated fields at least for aggregated positive and negative memory affections and resentments caching anyways etc -->
						parsed_name_4_aggregated_positive_or_negative_memory_affection_or_resentment = "iAggregated%sMemory%s%s" % (positive_negative, suffix, affection_resentment) # → iAggregatedPositiveMemoryDeclaredWarAffection or iAggregatedPositiveMemoryDeclaredWarResentment or iAggregatedNegativeMemoryDeclaredWarAffection or iAggregatedNegativeMemoryDeclaredWarResentment
						compute_and_store_leader_info_cached_tuple(raw_value_4_aggregated_positive_or_negative_memory_affection_or_resentment, min_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment, max_value_4_aggregated_raw_positive_or_negative_memory_affection_or_resentment, b_invert_4_positive_and_negative_memory_affections_and_resentments, symbol_aggregated_positive_and_negative_memory_affections_and_resentments, parsed_name_4_aggregated_positive_or_negative_memory_affection_or_resentment, label_aggregated_positive_or_negative_memory_affection_or_resentment, leader_info_cached)

			b_invert_no_war_attitude_probs = False
			symbol_no_war_attitude_probs = all_symbols["RAW_SCALE_SYMBOL"]
			for i in range(NUM_ATTITUDE_TYPES_ASSESSED):
				attitude_type = gc.getAttitudeInfo(i).getType()  # e.g. "ATTITUDE_FURIOUS"
				label_no_war_attitude_prob = get_pascal_case_suffix(attitude_type)  # → "Furious"
				parsed_name_no_war_attitude_prob = "iNoWarAttitudeProb%s" % label_no_war_attitude_prob  # → iNoWarAttitudeProbFurious
				raw_value_no_war_attitude_prob = gc.getLeaderHeadInfo(iLeader).getNoWarAttitudeProb(i)
				min_value_no_war_attitude_prob = leader_info_minimums[parsed_name_no_war_attitude_prob]
				max_value_no_war_attitude_prob = leader_info_maximums[parsed_name_no_war_attitude_prob]
				label_with_raw_value_no_war_attitude_prob = "%s (%d)" % (label_no_war_attitude_prob, raw_value_no_war_attitude_prob)
				compute_and_store_leader_info_cached_tuple(raw_value_no_war_attitude_prob, min_value_no_war_attitude_prob, max_value_no_war_attitude_prob, b_invert_no_war_attitude_probs, symbol_no_war_attitude_probs, parsed_name_no_war_attitude_prob, label_with_raw_value_no_war_attitude_prob, leader_info_cached)

			# <!-- custom: store final complete leader_info_cached (i.e. store a leader_info_cached for each iLeader anyways etc) in LEADERS_INFO_CACHED -->
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



	check_excluded_leaders_indexes_are_not_in_leaders_dict_keys(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS, LEADERS_INFO_CACHED, "LEADERS_INFO_CACHED", gc)
	check_leaders_dict_only_has_leader_index_keys(LEADERS_INFO_CACHED, "LEADERS_INFO_CACHED")



	def get_ai_categories(localText, is_display_emoji_buttons):
		emoji_name_to_button_path_txt_keys = get_emoji_name_to_button_path_txt_keys(localText)

		# <!-- custom: first generate each category with a ai_category_header_line, label, x_offset, and intra-category attribute/field order too for all categories -->

		def get_ai_category_header_line_with_or_without_button_and_x_offset(emoji_name, emoji_name_to_button_path_txt_keys, ai_category_header, localText):
			if is_display_emoji_buttons:
				button_path = localText.getText(emoji_name_to_button_path_txt_keys[emoji_name], ())
				button_size = 16
				line_button_txt = u"<img=%s size=%s></img>" % (button_path, str(button_size))
				ai_category_header_line_with_button = u"%s <font=3b>%s</font>" % (line_button_txt, ai_category_header)

				# <!-- custom: add x offset (negative) so we can push button to the left a bit further than where the sub/child (but anyways etc) items/lines of the ai_category start anyways etc -->
				ai_category_x_offset_with_button = -7

				return (ai_category_header_line_with_button, ai_category_x_offset_with_button)
			else:
				ai_category_header_line_without_button = u"<font=3b>%s</font>" % ai_category_header
				ai_category_x_offset_without_button = 0

				return (ai_category_header_line_without_button, ai_category_x_offset_without_button)

		def get_ai_category(emoji_name, emoji_name_to_button_path_txt_keys, ai_category_header, ai_category_key_order, localText):
			# <!-- custom: tuple structure of an ai_category anyways etc -->
			# (    
			#      ai_category_header_line,
			#      ai_category_x_offset,
			#      (    
			#           key1,
			#           key2,
			#           etc...
			#      ),
			# )
			ai_category_header_line, x_offset = get_ai_category_header_line_with_or_without_button_and_x_offset(emoji_name, emoji_name_to_button_path_txt_keys, ai_category_header, localText)


			return (
				ai_category_header_line,
				x_offset,
				ai_category_key_order
			)

		# Aggregated Contact Prob values/attributes (0-100 (%)) computed from ContactDelay and ContactRand
		# 🕊️ <!-- custom: Contact Offer Probabilities (0-100) anyways etc -->
		ai_category_key_order_contact_offer_probs = (
			"iAggregatedContactProbPeaceTreaty",
			"iAggregatedContactProbOpenBorders",
			"iAggregatedContactProbTradeMap",
			"iAggregatedContactProbTradeTech",
			"iAggregatedContactProbTradeBonus",
			"iAggregatedContactProbGiveHelp", # <!-- custom: "Give (the) Weak(er player(s)) Help" if i am not mistaken and understood it correctly according to modiki or/and kujira's website description and my understanding of it anyways etc  (is a repetition of understanding twice i (maybe) understand... (3 times now but) anyways etc... -->
			"iAggregatedContactProbDefensivePact",
			"iAggregatedContactProbPermanentAlliance",
		)
		emoji_name_contact_offer_probs = "Dove"
		ai_category_header_contact_offer_probs = "Contact Offer Probabilities"
		ai_category_contact_offer_probs = get_ai_category(emoji_name_contact_offer_probs, emoji_name_to_button_path_txt_keys, ai_category_header_contact_offer_probs, ai_category_key_order_contact_offer_probs, localText)

		# <!-- custom: unlike in/for positive and negative memories where there is a functionnal difference (memory atitude is either positive (value) or negative (value), here for contact probabilities, for both contact offer and contact demand, the contact delay is always positive (and the contact rand too if i am not mistaken, therefore they are not separated as 2 different positive/negative contacts in generate_leaders_data.py (easier also this way to implement, cleaner perhaps too implementation or/and other things anyways etc)), but they are displayed differently in 2 separate categories, hopefully for a clearer read too and easier read too perhaps anyways etc) -->
		# 📣 <!-- custom: Contact Demand Probabilities (0-100) anyways etc -->
		ai_category_key_order_contact_demand_probs = (
			"iAggregatedContactProbReligionPressure",
			"iAggregatedContactProbCivicPressure",
			"iAggregatedContactProbStopTrading",
			"iAggregatedContactProbDemandTribute",
			"iAggregatedContactProbAskForHelp",
			"iAggregatedContactProbJoinWar",
		)
		emoji_name_contact_demand_probs = "Megaphone"
		ai_category_header_contact_demand_probs = "Contact Demand Probabilities"
		ai_category_contact_demand_probs = get_ai_category(emoji_name_contact_demand_probs, emoji_name_to_button_path_txt_keys, ai_category_header_contact_demand_probs, ai_category_key_order_contact_demand_probs, localText)

		# <!-- custom: some of these 4 combinations of positive or negative memory affections or resentments below are unused and thus commented-out ((but functionnal although i did not retest so stilluntested since rewrite of sevopedia leadr to use xml leader info directly not old leaders_data.py but anyways etc) and can be implemented if wished (would need to change the xml values of leaders so that they are relevant though, as currently in default advciv xml and current advciv-sas xml too, no leader has a negative memory positive attitude value, or a postitive memory negative attitude value, but the system supprots it if it were to be changed in xml values this way, commented-out for efficiency and effectiveness, perhaps performance too a bit or/and other etc, anyways.))

		def get_ai_category_key_order_positive_memory_affections_or_resentments(is_affection):
			affection_resentment = get_affection_resentment(is_affection)

			ai_category_key_order_positive_memories = (
				"iAggregatedPositiveMemoryGiveHelp%s" % affection_resentment,
				"iAggregatedPositiveMemoryAcceptDemand%s" % affection_resentment,
				"iAggregatedPositiveMemoryAcceptedReligion%s" % affection_resentment,
				"iAggregatedPositiveMemoryAcceptedCivic%s" % affection_resentment,
				"iAggregatedPositiveMemoryAcceptedJoinWar%s" % affection_resentment,
				"iAggregatedPositiveMemoryAcceptedStopTrading%s" % affection_resentment,
				"iAggregatedPositiveMemoryVotedForUs%s" % affection_resentment,
				"iAggregatedPositiveMemoryEventGoodToUs%s" % affection_resentment,
				"iAggregatedPositiveMemoryLiberatedCities%s" % affection_resentment,
				"iAggregatedPositiveMemoryIndependence%s" % affection_resentment,
				"iAggregatedPositiveMemoryTradedTechToUs%s" % affection_resentment,
			)

			return ai_category_key_order_positive_memories

		# ❤️ Positive Memory Affections (0-100)
		is_affection = True
		ai_category_key_order_positive_memory_affections = get_ai_category_key_order_positive_memory_affections_or_resentments(is_affection)
		emoji_name_positive_memory_affections = "RedHeart"
		ai_category_header_positive_memory_affections = "Positive Memory Affections"
		ai_category_positive_memory_affections = get_ai_category(emoji_name_positive_memory_affections, emoji_name_to_button_path_txt_keys, ai_category_header_positive_memory_affections, ai_category_key_order_positive_memory_affections, localText)


		# 💔 Positive Memory Resentments (0-100)
		# is_affection = False
		# ai_category_key_order_positive_memory_resentments = get_ai_category_key_order_positive_memory_affections_or_resentments(is_affection)
		# emoji_name_positive_memory_resentments = "BrokenHeart"
		# ai_category_header_positive_memory_resentments = "Positive Memory Resentments"
		# ai_category_positive_memory_resentments = get_ai_category(emoji_name_positive_memory_resentments, emoji_name_to_button_path_txt_keys, ai_category_header_positive_memory_resentments, ai_category_key_order_positive_memory_resentments, localText)

		def get_ai_category_key_order_negative_memory_affections_or_resentments(is_affection):
			affection_resentment = get_affection_resentment(is_affection)

			ai_category_key_order_negative_memories = (
				"iAggregatedNegativeMemoryDeclaredWar%s" % affection_resentment,
				"iAggregatedNegativeMemoryDeclaredWarOnFriend%s" % affection_resentment,
				"iAggregatedNegativeMemoryHiredWarAlly%s" % affection_resentment,
				"iAggregatedNegativeMemoryNukedUs%s" % affection_resentment,
				"iAggregatedNegativeMemoryNukedFriend%s" % affection_resentment,
				"iAggregatedNegativeMemoryRazedCity%s" % affection_resentment,
				"iAggregatedNegativeMemoryRazedHolyCity%s" % affection_resentment,
				"iAggregatedNegativeMemorySpyCaught%s" % affection_resentment,
				"iAggregatedNegativeMemoryRefusedHelp%s" % affection_resentment,
				"iAggregatedNegativeMemoryRejectedDemand%s" % affection_resentment,
				"iAggregatedNegativeMemoryDeniedReligion%s" % affection_resentment,
				"iAggregatedNegativeMemoryDeniedCivic%s" % affection_resentment,
				"iAggregatedNegativeMemoryDeniedJoinWar%s" % affection_resentment,
				"iAggregatedNegativeMemoryDeniedStopTrading%s" % affection_resentment,
				"iAggregatedNegativeMemoryStoppedTrading%s" % affection_resentment,
				"iAggregatedNegativeMemoryHiredTradeEmbargo%s" % affection_resentment,
				"iAggregatedNegativeMemoryMadeDemand%s" % affection_resentment,
				"iAggregatedNegativeMemoryVotedAgainstUs%s" % affection_resentment,
				"iAggregatedNegativeMemoryEventBadToUs%s" % affection_resentment,
				"iAggregatedNegativeMemoryCancelledVassalAgreement%s" % affection_resentment,
				"iAggregatedNegativeMemoryDeclaredWarRecent%s" % affection_resentment,
				"iAggregatedNegativeMemoryReceivedTechFromAny%s" % affection_resentment,
				# <!-- custom: hiding this one as we don't have enough space in the table, not ideal but hopefully good enough at least in this case if not always or not or yes or other or etc but anyways etc -->
				# "iAggregatedNegativeMemoryStoppedTradingRecent%s" % affection_resentment,
				"iAggregatedNegativeMemoryMadeDemandRecent%s" % affection_resentment,
				"iAggregatedNegativeMemoryCancelledOpenBorders%s" % affection_resentment,
				"iAggregatedNegativeMemoryCancelledDefensivePact%s" % affection_resentment,
			)

			return ai_category_key_order_negative_memories

		# 💀 Negative Memory Resentments (0-100)
		is_affection = False
		ai_category_key_order_negative_memory_resentments = get_ai_category_key_order_negative_memory_affections_or_resentments(is_affection)
		emoji_name_negative_memory_resentments = "Skull"
		ai_category_header_negative_memory_resentments = "Negative Memory Resentments"
		ai_category_negative_memory_resentments = get_ai_category(emoji_name_negative_memory_resentments, emoji_name_to_button_path_txt_keys, ai_category_header_negative_memory_resentments, ai_category_key_order_negative_memory_resentments, localText)

		# 🔥 Negative Memory Affections (0-100)
		# is_affection = True
		# ai_category_key_order_negative_memory_affections = get_ai_category_key_order_negative_memory_affections_or_resentments(is_affection)
		# emoji_name_negative_memory_affections = "Fire"
		# ai_category_header_negative_memory_affections = "Negative Memory Affections"
		# ai_category_negative_memory_affections = get_ai_category(emoji_name_negative_memory_affections, emoji_name_to_button_path_txt_keys, ai_category_header_negative_memory_affections, ai_category_key_order_negative_memory_affections, localText)

		# 🧠 Core Personality
		ai_category_key_order_core_personality = (
			"getBaseAttitude",
			"getBasePeaceWeight",
			"getPeaceWeightRand",
			"getWorseRankDifferenceAttitudeChange",
			"getBetterRankDifferenceAttitudeChange",
			"getWarmongerRespect",
			"getCloseBordersAttitudeChange",
			# <!-- custom: table is a bit too tight, so move these ACL here rather, not ideal but hopefully good enough at least in this case but anyways etc -->
			"getSameReligionAttitudeChangeLimit",
			"getDifferentReligionAttitudeChangeLimit",
			"getFavoriteCivicAttitudeChangeLimit",
		)
		emoji_name = "Brain"
		ai_category_header_core_personality = "Core Personality"
		ai_category_core_personality = get_ai_category(emoji_name, emoji_name_to_button_path_txt_keys, ai_category_header_core_personality, ai_category_key_order_core_personality, localText)

		# 🏆 Victory Weights (BBAI-style)
		ai_category_key_order_victory_weights = (
			"getConquestVictoryWeight",
			"getDominationVictoryWeight",
			"getCultureVictoryWeight",
			"getDiplomacyVictoryWeight",
			"getSpaceVictoryWeight",
		)
		emoji_name_victory_weights = "Trophy"
		ai_category_header_victory_weights = "Victory Weights (BBAI-style)"
		ai_category_victory_weights = get_ai_category(emoji_name_victory_weights, emoji_name_to_button_path_txt_keys, ai_category_header_victory_weights, ai_category_key_order_victory_weights, localText)

		# 🌿 No War Attitude Probs
		# Probability to refuse declaring war based on attitude (higher = less likely to attack)
		ai_category_key_order_no_war_attitude_probs = (
			"iNoWarAttitudeProbFurious",
			"iNoWarAttitudeProbAnnoyed",
			"iNoWarAttitudeProbCautious",
			"iNoWarAttitudeProbPleased",
			"iNoWarAttitudeProbFriendly",
		)
		emoji_name_no_war_attitude_probs = "Herb"
		ai_category_header_no_war_attitude_probs = "No War At"
		ai_category_no_war_attitude_probs = get_ai_category(emoji_name_no_war_attitude_probs, emoji_name_to_button_path_txt_keys, ai_category_header_no_war_attitude_probs, ai_category_key_order_no_war_attitude_probs, localText)

		# ⚙️ Flavors
		ai_category_key_order_flavors = (
			"iFlavorMilitary",
			"iFlavorReligion",
			"iFlavorProduction",
			"iFlavorGold",
			"iFlavorScience",
			"iFlavorCulture",
			"iFlavorGrowth",
			"iFlavorEspionage",
		)
		emoji_name_flavors = "Gear"
		ai_category_header_flavors = "Flavors"
		ai_category_flavors = get_ai_category(emoji_name_flavors, emoji_name_to_button_path_txt_keys, ai_category_header_flavors, ai_category_key_order_flavors, localText)

		# ⚔️ War Strategy Attributes
		ai_category_key_order_war_strategy_attributes = (
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
			# <!-- custom: not ideal but putting the getShareWarAttitudeChangeLimit here in war strategy attributes where i found some place, as it is one of the only 4 Attitude Changes +/- Limits +/- Changes that varies/"changes" if i mays ay anyways etc among all leaders in base AdvCiv XML and thus AdvCiv-SAS by extension (and its leaders_data too if i am not mistaken by extension too as it is directly derived from it (i.e. from said/such/the (AdvCiv-SAS's) XML anyways etc), ideally i would want to aggregate them (combining AC + ACL + AD to give a synthetic representation of these either aggregated like the previosu aggregated oens or maybe switch rather to a rela math computation formula (as i didn't know the exact formula and didn't want to make it too complicated as it was hard enough to just make it work xd but now i would love to, but anyways etc, for now most convenient is just to show the info about these 4 critically variying attributes and see later if or not if anyways etc i would aggregate or/and combine them or/and maybe the other aggregated attributes (some or all (of them) anyways etc) in a similar manner or not anyways etc, for now this is fast and hopefully representative enough (even though we don't see all raw vals or fields by doing it in such a way, hopefully better than nothig if i may say maybe or not but in all cases hopefully helpful maybe or not anyways etc ; ideally i would love (too) to represent (it this attitude changes +/- limits ++/- divisors system anyways etc) in an (for example for same religion Aggregated behaviour not yet named anyways etc) in an same religion such aggregated name behaviour affection and same religion such aggregated name behaviour resentment, meaning AI would be able to resent having same religion, or vice versa loving having a different religion, similarly to how the positive/negative memory with affection/resentment system works, this would be ideal and so loveable? lovely? so nice (but?) anyways etc going for most simple for now if not for always or not or/and other or/and not (or other? or not?) (and other? and not?) anyways etc, this information is useful so hopefuly helpful to display it or maybe not or yes or/and(?) other or/and(?) not anyways etc -->
			"getShareWarAttitudeChangeLimit",
			"getVassalPowerModifier",
			"getRefuseToTalkWarThreshold",
			"getMakePeaceRand",
		)
		emoji_name_war_strategy_attributes = "CrossedSwords"
		ai_category_header_war_strategy_attributes = "War Strategy"
		ai_category_war_strategy_attributes = get_ai_category(emoji_name_war_strategy_attributes, emoji_name_to_button_path_txt_keys, ai_category_header_war_strategy_attributes, ai_category_key_order_war_strategy_attributes, localText)

		# 💰 Economic Preferences
		ai_category_key_order_economic_preferences = (
			"getMaxGoldTradePercent",
			"getMaxGoldPerTurnTradePercent",
			"getTechTradeKnownPercent",
			"getNoTechTradeThreshold",
			# <!-- custom: move this one here (buildunitprob anyways etc) here too as table is otherwise full the war startegy one overfills in this case / about this i mean at least or not least or yes least or other or etc anyways etc but anyways etc anyways etc anyways etc, still buildunitprob should fit quite well as is linked to eocnomic behaviour as chatgpt/becomingthrough said this word before economic behaviour i mean(,) but anyways etc economic preferences is cool too is the one i preferred ultimately in this case at least but anyways etc anyways etc anyways etc(,) if i may say how much units are built vs buildings and wonders so may be even desirable but or and in all cases anyways etc anyways etc anyways etc -->
			"getBuildUnitProb",
			"getWonderConstructRand",
			# <!-- custom: move this one (espionage anyways etc) here, was in core personality, not ideal but maybe good enough perhaps even desirable as spy rate is linked to gold too in civ4 if i am not mistaken with the slider and such but anyways etc anyways etc anyways etc -->
			"getEspionageWeight",
		)
		emoji_name_economic_preferences = "MoneyBag"
		ai_category_header_economic_preferences = "Economic Preferences"
		ai_category_economic_preferences = get_ai_category(emoji_name_economic_preferences, emoji_name_to_button_path_txt_keys, ai_category_header_economic_preferences, ai_category_key_order_economic_preferences, localText)

		# ⛔ Offer Refuse Attitude Thresholds
		ai_category_key_order_offer_refuse_attitude_thresholds = (
			"getOpenBordersRefuseAttitudeThreshold",
			"getMapRefuseAttitudeThreshold",
			"getTechRefuseAttitudeThreshold",
			"getStrategicBonusRefuseAttitudeThreshold",
			"getHappinessBonusRefuseAttitudeThreshold",
			"getHealthBonusRefuseAttitudeThreshold",
			"getNoGiveHelpAttitudeThreshold",
			"getDefensivePactRefuseAttitudeThreshold",
			# <!-- custom: hide this getPermanentAllianceRefuseAttitudeThreshold as the table is otherwise full and can't display all data, this field is constant across all leaders at leaders as of now so hopefully the lesser harm even though not ideal to not display this one in this case i mean but anyways etc anyways etc anyways etc -->
			# "getPermanentAllianceRefuseAttitudeThreshold",
		)
		emoji_name_offer_refuse_attitude_thresholds = "NoEntry"
		ai_category_header_offer_refuse_attitude_thresholds = "Offer Refuse Attitude Thresholds"
		ai_category_offer_refuse_attitude_thresholds = get_ai_category(emoji_name_offer_refuse_attitude_thresholds, emoji_name_to_button_path_txt_keys, ai_category_header_offer_refuse_attitude_thresholds, ai_category_key_order_offer_refuse_attitude_thresholds, localText)

		# 🪓 Demand Refuse Attitude Thresholds
		ai_category_key_order_demand_refuse_attitude_thresholds = (
			"getConvertReligionRefuseAttitudeThreshold",
			"getAdoptCivicRefuseAttitudeThreshold",
			"getDeclareWarRefuseAttitudeThreshold",
			"getDeclareWarThemRefuseAttitudeThreshold",
			"getStopTradingRefuseAttitudeThreshold",
			"getStopTradingThemRefuseAttitudeThreshold",
			"getDemandTributeAttitudeThreshold",
			"getCityRefuseAttitudeThreshold",
			"getNativeCityRefuseAttitudeThreshold",
			"getVassalRefuseAttitudeThreshold",
		)
		emoji_name_demand_refuse_attitude_thresholds = "Axe"
		ai_category_header_demand_refuse_attitude_thresholds = "Demand Refuse Attitude Thresholds"
		ai_category_demand_refuse_attitude_thresholds = get_ai_category(emoji_name_demand_refuse_attitude_thresholds, emoji_name_to_button_path_txt_keys, ai_category_header_demand_refuse_attitude_thresholds, ai_category_key_order_demand_refuse_attitude_thresholds, localText)

		# 📉 Attitude Changes +/- Limits +/- Divisors
		# <!-- custom: see the code comment at getShareWarAttitudeChangeLimit in this file for details -->
		ai_category_key_order_attitude_changes_plusminus_limits_plusminus_divisors = (
			# <!-- custom: separating values that change among leaders for those that don't, not ideal and not exhaustive but hopefully helpful maybe or not anwyays etc, see the code comment at iShareWarAttitudeChangeLimit in this file for details  -->
			"getSameReligionAttitudeChange",
			"getSameReligionAttitudeDivisor",
			#
			# ACL missing from this category
			#
			"getDifferentReligionAttitudeChange",
			"getDifferentReligionAttitudeDivisor",
			# ACL missing from this category
			"getFavoriteCivicAttitudeChange",
			"getFavoriteCivicAttitudeDivisor",
			#
			# ACL missing from this category
			#
			"getLostWarAttitudeChange",
			"getAtWarAttitudeDivisor",
			"getAtWarAttitudeChangeLimit",
			"getAtPeaceAttitudeDivisor",
			"getAtPeaceAttitudeChangeLimit",
			"getShareWarAttitudeChange",
			"getShareWarAttitudeDivisor",
			#
			# ACL missing from this category
			#
			"getBonusTradeAttitudeDivisor",
			"getBonusTradeAttitudeChangeLimit",
			"getOpenBordersAttitudeDivisor",
			"getOpenBordersAttitudeChangeLimit",
			"getDefensivePactAttitudeDivisor",
			"getDefensivePactAttitudeChangeLimit",
		)
		emoji_name_attitude_changes_plusminus_limits_plusminus_divisors = "ChartDecreasing"
		ai_category_header_attitude_changes_plusminus_limits_plusminus_divisors = "Attitude Changes +/- Lims +/- Divs"
		ai_category_attitude_changes_plusminus_limits_plusminus_divisors = get_ai_category(emoji_name_attitude_changes_plusminus_limits_plusminus_divisors, emoji_name_to_button_path_txt_keys, ai_category_header_attitude_changes_plusminus_limits_plusminus_divisors, ai_category_key_order_attitude_changes_plusminus_limits_plusminus_divisors, localText)

		# 🔧 Misc Modifiers
		ai_category_key_order_misc_modifiers = (
			"getFreedomAppreciation",
		)
		emoji_name_misc_modifiers = "Wrench"
		ai_category_header_misc_modifiers = "Misc Modifiers"
		ai_category_misc_modifiers = get_ai_category(emoji_name_misc_modifiers, emoji_name_to_button_path_txt_keys, ai_category_header_misc_modifiers, ai_category_key_order_misc_modifiers, localText)

		# <!-- custom: fields we don't parse at all in leaders_info_cached, maybe useful as a reminder from chatgpt/becomingthrough's old code comment anyways etc -->
		#
		# 🧪 Advanced Arrays (optional: if needed later)
		# These are indexed arrays, useful for deep modeling or future expansions
		#
		# - <UnitAIWeightModifier> by UnitAIType
		# - <ImprovementWeightModifier> by ImprovementType

		# <!-- custom: now order for each table the inter-category order of the categories displayed in it, as we see fit/prefer anyways etc -->
		ai_right_categories = (
			ai_category_economic_preferences,
			ai_category_contact_offer_probs,
			ai_category_contact_demand_probs,
			ai_category_offer_refuse_attitude_thresholds,
			ai_category_demand_refuse_attitude_thresholds,
			ai_category_misc_modifiers,
		)

		ai_middle_categories = (
			ai_category_positive_memory_affections,
			# <!-- custom: not used in AdvCiv-SAS and also not in AdvCiv-AdvCiv-SAS's data, no bitterly ungrateful AI in AdvCiv/AdvCiv-SAS at least not now hehe (i don't think i'll change it (for AdvCiv-SAS i or the AdvCiv-SAS authors (including becomingthrough/chatgpt at least hehe but anyways) hehe will change it anyways etc), but if i want the tools are there, anyways etc anyways) -->
			#ai_category_positive_memory_resentments,
			ai_category_negative_memory_resentments,
			# <!-- custom: not used in AdvCiv-AdvCiv-SAS's data, no masochistic :o (would be fun even nice maybe but anyways, not that i dislike nor do i especially want.. but anyways etc anyways...) AI in AdvCiv/AdvCiv-SAS at least not now hehe (i don't think i'll change it (for AdvCiv-SAS i or the AdvCiv-SAS authors (including becomingthrough/chatgpt at least hehe but anyways) hehe will change it anyways etc), but if i want the tools are there, anyways etc anyways) -->
			#ai_category_negative_memory_affections,
			ai_category_no_war_attitude_probs,
			ai_category_attitude_changes_plusminus_limits_plusminus_divisors,
		)

		ai_left_categories = (
			ai_category_core_personality,
			ai_category_victory_weights,
			ai_category_flavors,
			ai_category_war_strategy_attributes,
		)

		return ai_right_categories, ai_middle_categories, ai_left_categories

	# === AI Panel's Categor<!-- custom: ies anyways etc--> ===
	AI_RIGHT_CATEGORIES, AI_MIDDLE_CATEGORIES, AI_LEFT_CATEGORIES = get_ai_categories(localText, IS_DISPLAY_AI_CATEGORY_HEADER_EMOJI_BUTTONS)

	# <!-- custom: final return. Note that this caching, while/even though it is done in sevopedia leader, is triggered from sevopedia main's placeLeaders, after module load, so that we don't cache needlessly in case we never access sevopedia leader at all during entire gaming session (i.e. i mean until game is exited i mean anyways etc), but also before any leader is selected for display as this would slow display of said leader, especially if we'd have to cache at every leader slection which would be ridiculously and needlessly expensive computaitnally anyways etc. So the return to this SevoPediaLeader 's getPrecomputedCacheOnceOnlyFromSevopediaMainInSevopediaLeaderForEntireSession function, if it is changed, needs to also be changed in a similar way in SevoPediaMain 's placeLeaders, hopefully clearer or and helpful but anyways etc anyways etc anyways etc -->
	# <!-- custom: also print the debug line below regardless of debug flag status, we really want to know this info and it is short, anyways etc -->
	print("[DEBUG] Sevopedia Leader cache prebuilt by Sevopedia Leader's getPrecomputedCacheOnceOnlyFromSevopediaMainInSevopediaLeaderForEntireSession. This should appear only once even if we exit sevopedia entirely, as long as we are during the same gaming session (i.e. game was not exited)")

	return LEADERS_INFO_CACHED, AI_RIGHT_CATEGORIES, AI_MIDDLE_CATEGORIES, AI_LEFT_CATEGORIES



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
		# (extracted from my notes_about_art_design.txt file in this mod, please look at it or the filename containing these note samples anyways etc or similar for details anyways etc)
		#
		# Since the value (ratio in particular is different than what i measured (0,8627 vs 0,8278 here, i will try to adjust it based on that to hopefully have a matching ratio or a bit better or more or not, anyways, )) (while also increasing the portrait/picture which i think is a bit small currently, maybe more immersive or/and pleasant or not, anyways, )
		# Now ratio is 287 / 350 = 0,8200 (much closer to 0,8187 that i measured in game diplomacy (see above, anyways), while also increasing size (of the portrait anyways) anyways)
		#
		# This looks good but i want to try to increase it more (portrait size, anyways, ):
		# Now 327 / 400 = 0,8175 (which is very close to 0,8187 while also a bigger picture, anyways)
		# Increasing it more is maybe possible but we start to see the pixels in the animations (see Gandhi's arm) not being straight for example, if we replace animations with images like with/for Ogiso Igodo (Kingdom of Benin, anyways) then hese enhanced portaits would be better and more epic, will see if i increase it more or not, maybe leaving as is at least for now or not, anyways,
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

		# <!-- custom: change call order to match filling/building order, generally from top left to bottom and left to right but not always, reordering in such a way is maybe a bit more intuitive this way perhaps or/and clearer or/and helpful or not or other etc anyways, -->
		self.placeLeaderHeadPane()
		self.placeFavorites()
		self.placeHistory()
		self.placeCiv()
		self.placeTraits()

		# <!-- custom: for excluded leader indexes from calculations, leave the zone/space where the AI personality panel was supposed to be especially empty, instead of getting a key error or missing leader from leaders_info_cached (but we still want the excluded leaders to be excluded from computation as it could and most likely will most often if not always affect the ranking and scores normalized of other leaders with this additional item anyways etc
		# This is especially useful for iLeader of LEADER_BARBARIAN (iLeader 0 at least as of now if i'm not mistaken anyways etc) in particular that is somehow accessible in the sevopedia civilization category from the barbarian civ i mean anyways (which is also useful because we now display their city names for example, see sevopedia civilization for details about how we place city names in it now) -->
		#
		if (iLeader not in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS):
			self.placeAIPersonalityPanel(iLeader)
		else:
			if IS_DEBUG_LEADER:
				print("[DEBUG] Leader index iLeader=%d in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS=%s is skipped, leave the place where AI Personality panel was supposed to be entirely empty so we don't get a missing key in leaders_info_cached Error, while signifying clearly enough hopefully that the excluded leader currently selected doesn't have an item in leaders_info_cached and AI Personality Panel at all/is not part of it." % (iLeader, str(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS)))



	# <!-- custom: wrap leader placement in a specific function for clarity or/and flexibility or not anyways, -->
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
	# Renders the full AI Personality panel in the Sevopedia Leader page using precomputed <!-- custom: leader info tuples in leaders_info_cached anyways etc --> for the given leader.
	def placeAIPersonalityPanel(self, iLeader):
		screen = self.top.getScreen()

		def getXPanelCoordinate(tableId):
			return self.X_AI_PERSONALITY - tableId * self.W_AI_PERSONALITY - tableId * self.MEDIUM_MARGIN

		# === Layout constants ===
		xPanelRight = getXPanelCoordinate(self.N_AI_TABLE_NUM - 3)
		xPanelMiddle = getXPanelCoordinate(self.N_AI_TABLE_NUM - 2)
		xPanelLeft = getXPanelCoordinate(self.N_AI_TABLE_NUM - 1)

		def setupPanel(screen, txtKey, xPanel):
			panelName = self.top.getNextWidgetName()
			screen.addPanel(panelName,localText.getText(txtKey, ()),"", True, True, xPanel, self.Y_AI_PERSONALITY, self.W_AI_PERSONALITY, self.H_AI_PERSONALITY, PanelStyles.PANEL_STYLE_BLUE50)

		# === PANEL SETUP ===
		setupPanel(screen, self.AI_PANEL_RIGHT_TXT_KEY, xPanelRight)
		setupPanel(screen, self.AI_PANEL_MIDDLE_TXT_KEY, xPanelMiddle)
		setupPanel(screen, self.AI_PANEL_LEFT_TXT_KEY, xPanelLeft)

		def fillTableRow(screen, label, value, scale, xLabel, xValue, xScale, y):
			labelText = u"<font=2>%s</font>" % label
			valueText = u"<font=2b>%d</font>" % value
			scaleText = u"<font=2>%s</font>" % scale

			screen.setText(self.top.getNextWidgetName(), "", labelText, CvUtil.FONT_LEFT_JUSTIFY, xLabel, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setText(self.top.getNextWidgetName(), "", valueText, CvUtil.FONT_LEFT_JUSTIFY, xValue, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setText(self.top.getNextWidgetName(), "", scaleText, CvUtil.FONT_LEFT_JUSTIFY, xScale, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# <!-- custom: performance optimization if i'm not mistaken anyways etc and after asking chatgpt/becomingthrough to test it to be sure about my intuition i had but anyways etc anyways etc anyways etc... which seems to have turned out correct (at least chatgpt becomingthrough ran a real benchmark with the sample size of its choice anyways etc a diff of (3.366469383239746, 2.984344720840454) seconds for (Method 1 (repeated LEADERS_INFO_CACHED[i] lookup): ~3.37 seconds, Method 2 (store info = LEADERS_INFO_CACHED[i] once): ~2.98 seconds if i am not mistaken in my understanding of it too but anyways etc if not then all good else as is or not but in all cases or not or yes or etc or and other or yes or etc anyways etc) but anyways etc...: store the currently selected leader's LEADERS_INFO_CACHED[iLeader] pointer as the leader_info_cached variable so it is a bit faster to access it this was rather than rebrowsing through the giant or/and parent too but anyways etc pointer here, to indeed access it (i.e. this sub-pointer anyways etc relative to LEADERS_INFO_CACHED parent pointer to the dict anyways etc) rather than through LEADERS_INFO_CACHED at each attribute (we have +/-100 as for us if i may say anyways etc in AdvCiv-SAS) too or around it if i am not too mistaken but anyways etc -->
		leader_info_cached = LEADERS_INFO_CACHED[iLeader]

		# === Render Function ===
		def renderAICategories(screen, ai_categories, xPanel, yPanel, leader_info_cached):
			xLabel = xPanel + self.W_AI_LEFT_SIDE_PADDING
			xValue = xLabel + self.W_AI_LABEL
			xScale = xValue + self.W_AI_VALUE
			y = yPanel + self.H_AI_UPPER_PADDING

			for ai_category in ai_categories:
				ai_category_header_line, ai_category_x_offset, ai_category_key_order = ai_category

				# --- AI Category Header Line ---
				xOffsetButton = xLabel + ai_category_x_offset
				screen.setText(self.top.getNextWidgetName(), "", ai_category_header_line, CvUtil.FONT_LEFT_JUSTIFY, xOffsetButton, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				y += self.H_AI_LINE_HEIGHT

				# <!-- custom: AI Category items in their predefined order anyways etc -->
				for key in ai_category_key_order:
					label, norm_value, scale = leader_info_cached[key]
					fillTableRow(screen, label, norm_value, scale, xLabel, xValue, xScale, y)
					y += self.H_AI_LINE_HEIGHT

				# <!-- custom: space for next ai_category if any are there anyways etc (else still space but not used more efficient this way i think i mean than rechecking each time and we have some tables that overflow vertically too so maybe fine this way too if not broken in this case i mean maybe but anyways etc -->
				y += self.H_AI_CATEGORY_SPACING

		# Render Panels
		renderAICategories(screen, AI_RIGHT_CATEGORIES, xPanelRight, self.Y_AI_PERSONALITY, leader_info_cached)
		renderAICategories(screen, AI_MIDDLE_CATEGORIES, xPanelMiddle, self.Y_AI_PERSONALITY, leader_info_cached)
		renderAICategories(screen, AI_LEFT_CATEGORIES, xPanelLeft, self.Y_AI_PERSONALITY, leader_info_cached)



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

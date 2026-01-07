# --- AI Utilities for normalization and general helpers ---
# Created as part of AdvCiv-SAS improvements
# (c) 2025 wonderingabout & AI helpers (see Authors in root README.md)



# <!-- custom: indexes based on real ingame sevopedia leader debug output, see sevopedia_helpers py file code comments for details -->
# <!-- custom: 11 entries total -->
def get_positive_memory_indexes_to_types():
	return {
		8: "MEMORY_GIVE_HELP",
		10: "MEMORY_ACCEPT_DEMAND",
		12: "MEMORY_ACCEPTED_RELIGION",
		14: "MEMORY_ACCEPTED_CIVIC",
		16: "MEMORY_ACCEPTED_JOIN_WAR",
		18: "MEMORY_ACCEPTED_STOP_TRADING",
		28: "MEMORY_TRADED_TECH_TO_US",
		31: "MEMORY_VOTED_FOR_US",
		32: "MEMORY_EVENT_GOOD_TO_US",
		34: "MEMORY_LIBERATED_CITIES",
		35: "MEMORY_INDEPENDENCE",
	}



def get_negative_memory_indexes_to_types():
	# <!-- custom: for MEMORY_RECEIVED_TECH_FROM_ANY in particular, it seems less clear if this is negative or not, i found this info for example in kujira's website in (translate to english with your web browser or such): https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#memory_received_tech_from_any -->
	#
	# "You have rejected another civilization's technology."
	# occurs to the civilization that has received a technology each time a contacted civilization acquires a technology through trade.
	#
	# In BtS, this diplomatic event does not have an attitude modifier assigned to it.
	# Instead, it is used as a so-called "over-advance counter" for technology trades. See also
	# <iNoTechTradeThreshold> .
	#
	# <MemoryDecay>
	# 	<MemoryType>MEMORY_RECEIVED_TECH_FROM_ANY</MemoryType>
	# 	<iMemoryRand>20</iMemoryRand>
	# </MemoryDecay>
	#
	# and our debug ingame in sevopedia shows (see (adjust to your mod path anyways etc) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\Python\Contrib\Sevopedia\_sevopedia_helpers.py for details):
	# Memory 29 (MEMORY_RECEIVED_TECH_FROM_ANY): Attitude 0, Decay 20
	#
	# here is also chatgpt's web search result if it helps too (not sure is accurate but maybe is or at least more since is web search anyways etc) formatted or not or yes for our script's consistency or rather small display in this case i mean or other or and not or yes or etc anyways etc:
	#
	# "
	# 🧠 What it does
	# Each time any contacted civilization receives a technology via trade, all other AI civilizations that have met them (including the trading partner itself) increase a hidden memory counter called MEMORY_RECEIVED_TECH_FROM_ANY by 1 
	# modiki.civfanatics.com +8; groups.google.com +8; civ4wiki.com +8.
	#
	# This doesn't directly adjust diplomatic attitude; instead, it's a "tech‑overexposure" counter influencing whether AI will trade techs with you later .
	#
	# 🕰️ How it operates
	# When one AI gets a tech from you, every AI that knows them—including the one receiving it—gets this memory += 1 
	# kirk.zulan.net +5; groups.google.com +5; forum.gamer.com.tw +5.
	#
	# Over time, the counter randomly decays, with the <iMemoryRand>20</iMemoryRand> tag setting the rate (i.e., each turn there's a chance to decrease by 1) 
	# modiki.civfanatics.com +3; forums.civfanatics.com +3; gforestshade.github.io +3.
	#
	# ⚙️ Effect in gameplay
	# It functions as a throttle: after trading techs a bunch, your "received from any" memory builds up, making AI increasingly reluctant to trade with you until it decays enough.
	#
	# There's no attitude hit attached, so your relationships don’t visibly worsen—but the memory can block or refuse future tech trades.
	# "
	#
	# based on this, if the higher it is, the higher no tech trade can happen, then i would classify it as negative memory even though is not strictly a memory it seems but maybe is strictly a memory
	#
	# <!-- custom: indexes based on real ingame sevopedia leader debug output, see sevopedia_helpers py file code comments for details -->
	# <!-- custom: 26 entries total -->

	return {
		0: "MEMORY_DECLARED_WAR",
		1: "MEMORY_DECLARED_WAR_ON_FRIEND",
		2: "MEMORY_HIRED_WAR_ALLY",
		3: "MEMORY_NUKED_US",
		4: "MEMORY_NUKED_FRIEND",
		5: "MEMORY_RAZED_CITY",
		6: "MEMORY_RAZED_HOLY_CITY",
		7: "MEMORY_SPY_CAUGHT",
		9: "MEMORY_REFUSED_HELP",
		11: "MEMORY_REJECTED_DEMAND",
		13: "MEMORY_DENIED_RELIGION",
		15: "MEMORY_DENIED_CIVIC",
		17: "MEMORY_DENIED_JOIN_WAR",
		19: "MEMORY_DENIED_STOP_TRADING",
		20: "MEMORY_STOPPED_TRADING",
		21: "MEMORY_STOPPED_TRADING_RECENT",
		22: "MEMORY_HIRED_TRADE_EMBARGO",
		23: "MEMORY_MADE_DEMAND",
		24: "MEMORY_CANCELLED_VASSAL_AGREEMENT",
		25: "MEMORY_MADE_DEMAND_RECENT",
		26: "MEMORY_CANCELLED_OPEN_BORDERS",
		27: "MEMORY_CANCELLED_DEFENSIVE_PACT",
		29: "MEMORY_RECEIVED_TECH_FROM_ANY",
		30: "MEMORY_VOTED_AGAINST_US",
		33: "MEMORY_EVENT_BAD_TO_US",
		36: "MEMORY_DECLARED_WAR_RECENT",
	}



def get_shifted_values(min_val, value, max_val):
	# <!-- custom:
	# example 1:
	# 	min_val = -19	->	shifted_min = 0
	#	value = -7		->	shifted_value = -7 - (-19) = -7 + 19 = 12
	#	max_val = -3	->	shifted_max = -3 - (-19) = -3 + 19 = 16
	#
	# example 2:
	# 	min_val = -19	->	shifted_min = 0
	#	value = -2		->	shifted_value = -2 - (-19) = -2 + 19 = 17
	#	max_val = 3		->	shifted_max = 3 - (-19) = 3 + 19 = 22
	#
	# example 3:
	# 	min_val = -19	->	shifted_min = 0
	#	value = 2		->	shifted_value = 2 - (-19) = 2 + 19 = 21
	#	max_val = 9		->	shifted_max = 9 - (-19) = 9 + 19 = 28
	#
	# example 4:
	# 	min_val = -19	->	shifted_min = 0
	#	value = -11		->	shifted_value = -11 - (-19) = -11 + 19 = 8
	#	max_val = -9	->	shifted_max = -9 - (-19) = -9 + 19 = 10
	#
	# example 5:
	# 	min_val = -19	->	shifted_min = 0
	#	value = -11		->	shifted_value = -11 - (-19) = -11 + 19 = 8
	#	max_val = 152	->	shifted_max = 152 - (-19) = 152 + 19 = 171
	#
	# example (1.)6:
	# 	min_val = -72	->	shifted_min = 0
	#	value = -55		->	shifted_value = -55 - (-72) = -55 + 72 = 17
	#	max_val = 37	->	shifted_max = 37 - (-72) = 37 + 72 = 109
	#
	# example 7:
	# 	min_val = 19	->	shifted_min = 0
	#	value = 24		->	shifted_value = 24 - 19 = 5
	#	max_val = 53	->	shifted_max = 53 - 19 = 34
	#
	# example 8 (sanity check):
	# 	min_val = 0		->	shifted_min = 0
	#	value = 24		->	shifted_value = 24
	#	max_val = 53	->	shifted_max = 53
	#
	# -->

	# <!-- custom: if min_val == 0, we return same values (min_val, value, max_val) as received -->
	shifted_min = 0
	shifted_value = value - min_val
	shifted_max = max_val - min_val

	return shifted_min, shifted_value, shifted_max



def test_expected_shifting_pre_normalize_to_100():
	# <!-- custom: examples taken from get_shifted_values's code comments -->
	vals_to_test = (
		(-19, -7, -3, 0, 12, 16),	# 1
		(-19, -2, 3, 0, 17, 22),	# 2
		(-19, 2, 9, 0, 21, 28),		# 3
		(-19, -11, -9, 0, 8, 10),	# 4
		(-19, -11, 152, 0, 8, 171),	# 5
		(-72, -55, 37, 0, 17, 109),	# (1.)6
		(19, 24, 53, 0, 5, 34),		# 7
		(0, 24, 53, 0, 24, 53),		# 8
	)

	for min_val, value, max_val, expected_shifted_min, expected_shifted_value, expected_shifted_max in vals_to_test:
		shifted_min, shifted_value, shifted_max = get_shifted_values(min_val, value, max_val)

		assert(shifted_min == expected_shifted_min)
		assert(shifted_value == expected_shifted_value)
		assert(shifted_max == expected_shifted_max)



# --- Attribute normalization ---
def normalize_to_100(value, min_val, max_val, B_WARN, invert, attr_name):
	# Normalizes an AI attribute value to a 0-100 integer scale.
	#
	# - First checks if min_val > max_val or if value outside [min_val, max_val].
	# - If min_val == max_val, issues a warning and returns 50.
	# - Shifts for non-zero minimums:
	#   - If min_val < 0, shifts range upwards.
	#   - If min_val > 0, shifts range downwards.
	# - Normalizes shifted_value / shifted_max.
	# - Optionally inverts the normalized value.
	# - Converts final normalized value to 0-100 integer.
	#
	# Warnings:
	# - <!-- custom: if B_WARN is set to true anyways etc, --> Uniform min==max -> All normalized scores will be 50.
	#
	# Errors:
	# - <!-- custom: min_val or max_val are None -> Raises an error. -->
	# - min_val higher value than max_val -> Raises an error.
	# - value out of bounds -> Raises an error.
	# - Shifted min not equal to 0 -> Raises an error.
	# - Shifted value negative -> Raises an error.
	# - Normalized value out of bounds -> Raises an error.
	#
	# Parameters:
	# - value (int): Raw XML attribute value.
	# - min_val (int): Minimum observed attribute value.
	# - max_val (int): Maximum observed attribute value.
	# - invert (bool): Whether to invert normalized scale.
	# - attr_name (str, optional): Attribute name for debug warnings.
	#
	# Returns:
	# - final_score (int): Normalized integer 0-100.

	# --- Pre-checks ---
	if (min_val is None) or (max_val is None):
		raise ValueError(u"[FATAL] min_val=%s or/and max_val=%s cannot be None, failed to fetch the real value if any exist, check your XML or/and fetching code." % (str(min_val), str(max_val)))

	if min_val > max_val:
		raise ValueError("Invalid min/max for attribute '%s': min_val=%d > max_val=%d" % (attr_name, min_val, max_val))

	if value < min_val or value > max_val:
		raise ValueError("Value out of range for attribute '%s': value=%d not in [%d, %d]" % (attr_name, value, min_val, max_val))

	if min_val == max_val:
		if B_WARN:
			print("[WARNING] Attribute %s has an identical min and max value (%d). All normalized values will be 50." % (attr_name, min_val))
		return 50

	# --- Shift min_val, value, and max_val, if needed, before we normalize ---
	shifted_value = None
	shifted_min, shifted_value, shifted_max = get_shifted_values(min_val, value, max_val)

	if (shifted_value is None):
		raise ValueError("[FATAL] In attr_name=%s, shifted_value=%s has not been initialized properly and is still None: shifted_min=%d, shifted_value=%d, shifted_max=%d, min_val=%d, value=%d, max_val=%d" % (attr_name, shifted_value, shifted_min, shifted_value, shifted_max, min_val, value, max_val))

	# --- Normalize ---
	if shifted_min != 0:
		raise ValueError("[FATAL] For attr_name=%s, distribution has not shifted to a shifted_min of 0 before normalization: shifted_min=%d, shifted_value=%d, shifted_max=%d, min_val=%d, value=%d, max_val=%d" % (attr_name, shifted_min, shifted_value, shifted_max, min_val, value, max_val))
	if shifted_value < 0:
		raise ValueError("[FATAL] For attr_name=%s, shifted_value cannot be negative (as shifted_min should always be 0) before normalization: shifted_min=%d, shifted_value=%d, shifted_max=%d, min_val=%d, value=%d, max_val=%d" % (attr_name, shifted_min, shifted_value, shifted_max, min_val, value, max_val))
	# <!-- custom: no need to handle division by 0 as, if shifted_max is 0, this would mean that shifted_min is 0 too since we shifted_min to 0, so in other words that min == 50 case that we already covered before anyways etc so no need to cover again here but mention for exhaustiveness anyways etc... -->

	norm = float(shifted_value) / float(shifted_max)

	final_score = int(round(norm * 100))
	if (final_score < 0) or (final_score > 100):
		raise ValueError("Norm of %s out of range (0-100) during normalization: final_score=%.3f, shifted_min=%d, shifted_max=%d, min_val=%d, max_val=%d" % (attr_name, final_score, shifted_min, shifted_max, min_val, max_val))

	if invert:
		final_score = 100 - final_score

	return final_score



def get_positive_negative(is_positive):
	if (is_positive):
		return "Positive"
	else:
		return "Negative"



def get_affection_resentment(is_affection):
	if (is_affection):
		return "Affection"
	else:
		return "Resentment"



def get_pascal_case_suffix(enumType):
	# Converts an enum constant like 'MEMORY_DECLARED_WAR' or 'CONTACT_STOP_TRADING' into a PascalCase suffix like 'DeclaredWar' or 'StopTrading'.
	#
	# This version automatically removes the first prefix (e.g., 'MEMORY_' or 'CONTACT_') instead of requiring it to be passed as a parameter.
	#
	# Args:
	# 	enumType (str): An enum string with an uppercase prefix (e.g., 'MEMORY_', 'CONTACT_').
	#
	# Returns:
	# 	str: PascalCase string of the remaining part (e.g., 'DeclaredWar').

	# Remove everything before the first underscore (e.g., 'MEMORY_DECLARED_WAR' → 'DECLARED_WAR')
	suffix = enumType.split("_", 1)[1]
	# Convert to lowercase, split on underscores, then capitalize each part
	parts = suffix.lower().split("_")
	return "".join([part.capitalize() for part in parts])



def get_adjusted_contact_values(contact_rand_raw, contact_delay_raw, is_debug, contact_type):
	# Adjusts contact rand and contact delay values according to standard rules.
	# Returns: (adjusted_rand, adjusted_delay, aggregated_prob_force_zero_flag)
	#
	force_zero_adjusted_values = None

	if contact_delay_raw < 0:
		# <!-- custom: detail: if delay < 0 (rand is meaningless/irrelevant but we still store it (for exhaustiveness and ui display of raw value anyways)), delay is infinite, probability of contact is 0 -->
		adjusted_delay = 999 # Infinite delay
		if is_debug:
			print(u"[INFO] In contact contact_type=%s Delay < 0: adjusted delay is considered infinite, forced to zero aggregation as well. Values of these are contact_delay_raw=%d, adjusted_delay=%d, force_zero_adjusted_values=%s." % (contact_type, contact_delay_raw, adjusted_delay, str(force_zero_adjusted_values)))

		if contact_rand_raw <= 0:
			adjusted_rand = 0
			force_zero_adjusted_values = True # Forced 0 aggregation
			if is_debug:
				print(u"[INFO] In contact contact_type=%s Delay < 0, adjusted delay is considered infinite, so Rand is irrelevant, as regardless of its value we would force aggregate to zero. But for exhaustiveness anyways etc, adjusting the rand as well, here to 0 since Rand <= 0. Values of these are contact_delay_raw=%d, adjusted_delay=%d, contact_rand_raw=%d, adjusted_rand=%d, force_zero_adjusted_values=%s." % (contact_type, contact_delay_raw, adjusted_delay, contact_rand_raw, adjusted_rand, str(force_zero_adjusted_values)))

			return adjusted_rand, adjusted_delay, force_zero_adjusted_values
			
		else:
			adjusted_rand = contact_rand_raw
			force_zero_adjusted_values = True # Forced 0 aggregation
			if is_debug:
				print(u"[INFO] In contact contact_type=%s Delay < 0, adjusted delay is considered infinite, so Rand is irrelevant, as regardless of its value we would force aggregate to zero. But for exhaustiveness anyways etc, adjusting the rand as well, here to a real value equal to raw rand value, as Rand > 0 which is valid even though delay makes it eventually irrelevant and we still force aggregate in the end for this contact. Values of these are contact_delay_raw=%d, adjusted_delay=%d, contact_rand_raw=%d, adjusted_rand=%d, force_zero_adjusted_values=%s." % (contact_type, contact_delay_raw, adjusted_delay, contact_rand_raw, adjusted_rand, str(force_zero_adjusted_values)))
		
		return adjusted_rand, adjusted_delay, force_zero_adjusted_values

	else:
		# <!-- custom: the higher the delay the worse/lower the contact prob (example gandhi's data/values vs montezuma so we (should i think anyways) invert both)-->
		adjusted_delay = contact_delay_raw
		if is_debug:
			print(u"[INFO] In contact contact_type=%s Delay >=0 which is valid: adjusted delay is equal to delay raw, forced to zero aggregation has yet to be determined anyways etc. Values of these are contact_delay_raw=%d, adjusted_delay=%d, force_zero_adjusted_values=%s." % (contact_type, contact_delay_raw, adjusted_delay, str(force_zero_adjusted_values)))

		if contact_rand_raw <= 0:
			# <!-- custom: (and else,) if rand is <=0, AI has a compatible delay but still never engages due to rand, so probability of contact is still 0. Only outside of these edge cases can the contact probabiltiy be computed if i'm not mistaken, else should be 0 as in this code block/check if i'm not mistaken anyways. -->
			# Can try, but refuses to ever engage → Aggregated ContactProb = 0
			adjusted_rand = 0
			force_zero_adjusted_values = True # Forced 0 aggregation
			if is_debug:
				print(u"[INFO] In contact contact_type=%s Delay >=0 which is valid: adjusted delay is equal to delay raw. As for forced aggregation value, Rand <= 0, so AI has a compatible delay but still never engages due to rand if i (advciv-sas mod maker anyways etc based on trying to understand how the base advciv or similar or before behaves anyways etc) am not mistaken anyways etc, and so if i am not mistaken too anyways etc probability of contact is still 0 if i am not mistaken in my understanding. So we still force aggregate to 0 for this contact. Values of these are contact_delay_raw=%d, adjusted_delay=%d, contact_rand_raw=%d, adjusted_rand=%d, force_zero_adjusted_values=%s." % (contact_type, contact_delay_raw, adjusted_delay, contact_rand_raw, adjusted_rand, str(force_zero_adjusted_values)))

			return adjusted_rand, adjusted_delay, force_zero_adjusted_values

		else:
			# <!-- custom: (and else,), if both delay and rand are compatible with havig a scaling and acutal contact probability (that we can compute too maybe here indeed anyways etc), then (to compute this we propose this formula that) the higher the delay the worse/lower the contact prob, and the higher the rand the worse/lower the contact prob (example gandhi's data/values vs montezuma so we (should i think anyways) invert both)-->
			adjusted_rand = contact_rand_raw
			force_zero_adjusted_values = False # Normal aggregation
			if is_debug:
				print(u"[INFO] In contact contact_type=%s Delay >=0 which is valid: adjusted delay is equal to delay raw. As for forced aggregation value, Rand > 0 which is valid, so probability of contact is highest when rand is low, and decreases the higher rand is. For example a rand of 5 gives 1/5 i.e. better odds whatever the actual value is than say 1000 which would be 1 / 1000 or some transformed value that would indicate or lead to a much lower contact chance if i (advciv-sas mod maker anyways etc based on trying to understand how the base advciv or similar or before behaves anyways etc) anyways etc am not mistaken in my understanding anyways etc. So we do not force aggregate to 0 for this contact. Values of these are contact_delay_raw=%d, adjusted_delay=%d, contact_rand_raw=%d, adjusted_rand=%d, force_zero_adjusted_values=%s." % (contact_type, contact_delay_raw, adjusted_delay, contact_rand_raw, adjusted_rand, str(force_zero_adjusted_values)))
			
			return adjusted_rand, adjusted_delay, force_zero_adjusted_values



def get_contact_rand_and_delay_invert_flags():
	# <!-- custom: the higher the contact rand (say 200 > 50 anyways etc), the lower the 1/n = 1/200 vs 1/50 chance if i am not mistaken of contact event / prob from my memory of the terminology if i may say or words used in kujira about memory fields or such, so we invert -->
	b_invert_contact_rands = True
	# <!-- custom: also, the higher the delay (say 100 > 5 (turns? If i am not mistaken too)), the longer until next contact, so the lower the contact event / prob, so we invert anyways etc delays too if i may say or not or yes or etc -->
	b_invert_contact_delays = True
	return b_invert_contact_rands, b_invert_contact_delays



def get_aggregated_raw_contact_score_from_adjusted_values(adjusted_value_rand_norm_score, adjusted_value_delay_norm_score, force_zero_adjusted_values):
	if force_zero_adjusted_values:
		return 0
	else:
		# --- Weight configuration ---
		# MAIN_WEIGHT represents the primary importance (e.g. randomness of contact)
		# The secondary weight (e.g. delay) is auto-balanced to ensure the total is 1.0
		MAIN_WEIGHT = 0.8
		SECONDARY_WEIGHT = 1.0 - MAIN_WEIGHT

		# --- Sanity check: weights must sum to exactly 1.0 ---
		weight_sum = MAIN_WEIGHT + SECONDARY_WEIGHT
		if not abs(weight_sum - 1.0) < 1e-6:
			raise ValueError(u"[VALUE ERROR] Weights must sum to 1.0: got MAIN = %f, SECONDARY = %f (sum = %f)"
				% (MAIN_WEIGHT, SECONDARY_WEIGHT, weight_sum))

		# --- Aggregate score: round for consistency, since we later normalize as int 0–100 anyway ---
		raw_aggregated = MAIN_WEIGHT * adjusted_value_rand_norm_score + SECONDARY_WEIGHT * adjusted_value_delay_norm_score
		# <!-- custom: no reason to strictly round the raw values since they will be normalized later anyways which would/should be an int if i am not mistaken and as of now the raw aggregated contact prob is only stored before that at min max storage stage (before their normalization as said before in this sentence), but no reason not to, since most if not indeed all fields are int, and it is an approximation (aggregation) to begin with, values close enough like 78.123456 vs 78.234567 could be considered to be the same 78 for example in my understanding anyways etc, so round them now even though makes data a bit more inaccurate. -->
		return int(round(raw_aggregated))



# <!-- custom: the adjust formula for memory fields is different than the contact adjust system we use in advciv-sas too for contacts anyways etc, because memory fields use a positive/negative memory field while there are no positive/negative contacts (all contacts are handled the same way computationally (only displayed as offers or demands but the values are computationally treated the same between all contact types, unlike memory types that are aggregated differently based on whether they fit in positive or in negative memory types, so the adjust formula is different read after bracket(s) anyways etc for rest of the explanation anyways etc)), so we don't hardcode aggregated values to extremes like 0 or 999 in contact fields, and use instead a different kind of adjustment, of raw memory attitude percents and memory decays, if i'm not mistaken -->
def get_adjusted_memory_values(raw_attitude_percent, raw_decay, is_affection, is_debug, mem_type):
	# Step 1: Clamp invalid affection/resentment signs to 0
	adjusted_attitude_percent = raw_attitude_percent
	if is_affection:
		# Affection must be non-negative
		if raw_attitude_percent < 0:
			adjusted_attitude_percent = 0
			if is_debug:
				print(u"[INFO] Affection memory mem_type=%s has adjusted attitude: adjusted_attitude_percent=%d. Rounded to 0." % (mem_type, adjusted_attitude_percent))
	else:
		# Resentment must be non-positive
		if raw_attitude_percent > 0:
			adjusted_attitude_percent = 0
			if is_debug:
				print(u"[INFO] Resentment memory mem_type=%s has adjusted attitude adjusted_attitude_percent=%d. Rounded to 0." % (mem_type, adjusted_attitude_percent))

	# Step 2: Adjust decay (decay must be non-negative)
	adjusted_decay = max(0, raw_decay)
	
	# <!-- custom: Step 3: (also was it my code comment originally or not) we --> never force aggregation to 0 for memories unlike in contact code, despite their similarities, so just one False here should be enough hopefully maybe anyways.
	force_zero_adjusted_values = False

	return adjusted_attitude_percent, adjusted_decay, force_zero_adjusted_values



def get_memory_attitude_percent_and_decay_invert_flags(is_positive, is_affection):
	if is_positive:
		if is_affection:
			# <!-- custom: higher attitude score (ex: + 350 > + 200) means more intense positive feeling (affection), closer to 0 means AI cares less (0 should be		- minimum -		attitudes after normalization unless i'm mistaken anyways but should be as this if i'm not mistaken anyways (where again AI cares the least)), so we don't invert.
			# -->
			# As for decay it should remain the same as it seems to just be some time unit or span (always positive if i'm not mistaken? At least after checking seems so in advciv data and in AdvCiv-SAS at least so far), check if accurate. -->
			return False, False
		else:
			# <!-- custom: lower attitude score (ex: -350 < -200) means more intense negative feeling (resentment) (resentful and (more) especially spiteful AI even for (presumably) good deeds), closer to 0 means AI cares less (0 should be		- maximum -		attitudes after normalization unless i'm mistaken anyways but should be as this if i'm not mistaken anyways (where again AI also, as in positive affection, for this value 0 (after adjustment) attitude, cares the least (at least we model it a such))), so we should invert indeed.
			# More detail on why and to be careful since these are negative values unlike most civ4 data (a good fail check too maybe to review or learn for me at least anyways etc anyways), is that since our normalize_to_100 function shifts to 0 distribution before normalizing (i.e. -350 is now -350 + 350 = 0, and -200 is now -200 + 350 = 150 if i'm not mistaken anyways) then the lower the score is (0 vs 150 before normalization, which is (after normalization) 0 / 150 * 100 = 0 vs 100 / 150 * 100 = 100, then -350 (now 0) which was more intense(ly negative feeling (resentment)) is the lowest, while -200 (now 100) with the lowest (in comparison relatively) feeling is now the highest in score, so the atititude score should indeed be inverted, hopefully safe nowanyways.
			# -->
			# As for decay it should be the same as above unless i'm mistaken but shouldn't be but anyways, anyways. -->
			return True, False

	else:
		if is_affection:
			# <!-- custom: similarly but in negative memories, higher attitude score (ex: + 350 > + 200) means more affection for them (more and more masochistic or similar AI anyways.. which i don't dislike but anyways... Not necessarily especially like but anyways (either/too)(or why not?) but anyways...), so we don't invert. -->
			return False, False
		else:
			# # <!-- custom: similarly but in negative memories, lower attitude score (ex: -350 < -200) means more intense negative feeling (resentment) (resentful and (more) especially spiteful AI but this time in an (seemingly) expected way if (conventionally) harm(ful behaviour or other thing or similar anyways etc thing anyways etc) is done to it), closer to 0 means AI cares less (0 should be		- maximum -		attitudes after normalization unless i'm mistaken anyways but should be as this if i'm not mistaken anyways), so we invert.. -->
			return True, False



def get_aggregated_raw_positive_or_negative_memory_affection_or_resentment_score_from_adjusted_values(adjusted_value_attitude_percent_norm_score, adjusted_value_decay_norm_score, force_zero_adjusted_values):
	if force_zero_adjusted_values:
		return 0
	else:
		# <!-- custom: see the same/similar function but for contact types' code code comments for details; approximation of the ratios based on kujira's website (translate(d? Anyways etc) to english with chrome web browser or such) https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#%e5%a4%96%e4%ba%a4%e7%9a%84%e5%87%ba%e6%9d%a5%e4%ba%8b%e3%81%ab%e3%82%88%e3%82%8b%e6%85%8b%e5%ba%a6%e8%a3%9c%e6%ad%a3 and https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#memoryattitudepercents and https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#memorydecays quite similarly to contact code -->

		# --- Weight configuration ---
		# MAIN_WEIGHT represents the primary importance (e.g. randomness of contact)
		# The secondary weight (e.g. delay) is auto-balanced to ensure the total is 1.0
		MAIN_WEIGHT = 0.8
		SECONDARY_WEIGHT = 1.0 - MAIN_WEIGHT

		# --- Sanity check: weights must sum to exactly 1.0 ---
		weight_sum = MAIN_WEIGHT + SECONDARY_WEIGHT
		if not abs(weight_sum - 1.0) < 1e-6:
			raise ValueError(u"[VALUE ERROR] Weights must sum to 1.0: got MAIN = %f, SECONDARY = %f (sum = %f)"% (MAIN_WEIGHT, SECONDARY_WEIGHT, weight_sum))

		# --- Aggregate score: round for consistency, since we later normalize as int 0–100 ---
		raw_aggregated = MAIN_WEIGHT * adjusted_value_attitude_percent_norm_score + SECONDARY_WEIGHT * adjusted_value_decay_norm_score
		# <!-- custom: similarly round, see the aggregated contact prob similar function to this if i am not mistaken. -->
		return int(round(raw_aggregated))

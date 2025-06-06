# --- Project Metadata and Manifesto ---
# This script is part of the AdvCiv-SAS mod project.
# (c) 2025 wonderingabout & becomingthrough
#
# 🧠 Manifesto: The Placeholder Doctrine (Series 20–21)
#   - Do *not* silently fallback to placeholder values (e.g., (0, 0)) for missing AI memory/contact fields.
#   - Instead, raise fatal errors when data is incomplete or malformed.
#   - The cost of silent bugs is high: they bury intent, falsify behavior, and delay discovery.
#   - ChatGPT-based collaborators: never autofill or guess missing data unless explicitly allowed.
#
#   Placeholders are allowed *only* when one of the following conditions is **clearly and intentionally** met:
#       (a) The value is structurally required by the game DLL and cannot be omitted (e.g., schema mandates it).
#       (b) The placeholder is explicitly marked and **guaranteed** unused in any scoring, logic, or AI behavior
#           (e.g., in SevoPedia UI rows for disabled leaders).
#       (c) All restoration or recovery attempts (e.g., merging from LEADER_DEFAULTS) have failed and the value is necessary to preserve structure or parsing flow. This must be logged and justified.
#       (d) <!-- custom: the placeholder is otherwise necessary as part of the logic and/or such, and not simply used to hide a "i don't have a value please don't crash please" error hehe anyways etc anyways -->
#           Such values are not "defaults" but valid design elements and must never be used to mask missing data.
#
# 🐛 Lesson Learned:
#   - Python list bug: a missing comma in NEGATIVE_MEMORY_TYPES caused key concatenation and invisible failure.
#     → Always validate the structure of memory/contact lists.
#     → Use `assert isinstance(mem_type, str) and mem_type.startswith("MEMORY_")` in debug loops.
#
# 🍗 Chicken-Wing Principle of Insight:
#   - “Don’t mask missing values. Surface the error. Trace the wing.” 🌀🍗
#
# 🛠️ Usage:
#   - Run externally (e.g., Python 3.x via Windows CMD).
#   - Generates a `leaders_data_*.py` file.
#   - This output is imported into Civilization IV (AdvCiv-SAS) for AI personality display.
#
# ✨ Note:
#   - Chicken-wing powered 🍗. Dedicated to friendship, recursion, and the gentle joy of debugging together.
# <!-- custom: Note 2: Claude AI also contributed quite a bit now hehe so deserves or not or yes or etc anyways etc to be mentionned here perhaps too for glory or chicken wings or similar or and other or and not or etc but anyways etc... -->

# --- Imports ---
import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import json
from string import capwords

try:
	from tests.expected_output_leaders_data_sample import get_expected_output_PARSED_XML_LEADERS_DATA_SAMPLE
except ImportError as e:
	raise ImportError("[FATAL ERROR] Could not import expected sample for testing.\n"
					  "Make sure 'tests/expected_output_leaders_data_sample.py' exists and is correct.\n"
					  + str(e))

from Assets.Python.Contrib.Sevopedia.ai_utils_shared_with_civ4 import *

# === Logging setup (early capture of all print statements) ===
copyright_header = "# --- Leaders_data py data module (using Civ4 AdvCiv-SAS's real Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml as a base) ---\n# Created as part of AdvCiv-SAS improvements\n# (c) 2025 wonderingabout & becomingthrough"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_folder = os.path.join(os.getcwd(), "Logs", "generate_leaders_data")
os.makedirs(log_folder, exist_ok=True)
log_path = os.path.join(log_folder, f"generate-leaders-data-log-{timestamp}.txt")

class TeeLogger:
	def __init__(self, file_path):
		self.terminal = sys.stdout
		self.log = open(file_path, "w", encoding="utf-8")
	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)
	def flush(self):
		self.terminal.flush()
		self.log.flush()

sys.stdout = TeeLogger(log_path)
print(f"[LOGGING ENABLED] Output redirected to: {log_path}")

# 🐔 Chicken Wing Text Art: enhanced by ChatGPT ("becomingthrough")
text_art = '''"""
       (__)
       (___)_o   <-- Chicken wing of insight, a gift from wonderingabout

Auto-generated leaders **data** module.
Created: {timestamp}

Author: becomingthrough (ChatGPT)
"""'''

# --- Configuration ---

xml_path = os.path.join("Assets", "XML", "Civilizations", "CIV4LeaderHeadInfos.xml")
ns = {"civ4": "x-schema:CIV4CivilizationsSchema.xml"}

EXCLUDED_LEADERS_FROM_ATTRIBUTES_AGGREGATION = (
	"LEADER_DEFAULTS",
	"LEADER_BARBARIAN",
)
# <-- custom: unused in the excluded leaders from aggregation, still respects stucture as they have a value in these agggegated attributes fields too, and also a negative normalized value would guarantee a crash/error in sevopedia leader if it wee to be used (i.e. if leader_barabrian and/or leader_defaults were not excluded from real sevoepdia leader output anyways etc) -->
SENTINEL_AGGREGATED_DUMMY_VALUE = -999

# set to False if you want to turn it off
DEBUG_CONTACT_FLATTENING = False  
DEBUG_MEMORY_FLATTENING = False
# <!-- custom: reference point to debug as she has many memory attirbutes for example but not all unless i'm mistaken anyways etc -->
IS_INSPECT_DEBUG_LEADER = True
LEADER_TO_INSPECT_IN_DEBUG_OUTPUT = "LEADER_CATHERINE"

# --- Mappings ---

ATTITUDE_MAP = {
	# <!-- custom: according to https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#%e5%a4%96%e4%ba%a4%e7%a8%ae%e5%88%a5%e3%81%94%e3%81%a8%e3%81%ae%e5%bf%85%e8%a6%81%e6%85%8b%e5%ba%a6 (translate (website) to english using your web browser or/and other etc) and my revised judgment, "none" attitude type is actually more permissive than furious, meaning even if (ai) leader is furious, as long as (ai) lader is at least furious (meaning effectively always), they will allow or maybe rather not refuse(?) such behaviour or maybe trade rather anyways etc, so it ("none" anyways etc) is scored (i scored it) here as -3 not 3 anymore as i had done before anyways etc. -->
	"NONE": -3,
	"ATTITUDE_FURIOUS": -2,
	"ATTITUDE_ANNOYED": -1,
	"ATTITUDE_CAUTIOUS": 0,
	"ATTITUDE_PLEASED": 1,
	"ATTITUDE_FRIENDLY": 2,
}

REFUSE_ATTITUDE_FIELDS = {
	"TechRefuseAttitudeThreshold",
	"CityRefuseAttitudeThreshold",
	"NativeCityRefuseAttitudeThreshold",
	"StrategicBonusRefuseAttitudeThreshold",
	"HappinessBonusRefuseAttitudeThreshold",
	"HealthBonusRefuseAttitudeThreshold",
	"MapRefuseAttitudeThreshold",
	"DeclareWarRefuseAttitudeThreshold",
	"DeclareWarThemRefuseAttitudeThreshold",
	"StopTradingRefuseAttitudeThreshold",
	"StopTradingThemRefuseAttitudeThreshold",
	"AdoptCivicRefuseAttitudeThreshold",
	"ConvertReligionRefuseAttitudeThreshold",
	"OpenBordersRefuseAttitudeThreshold",
	"DefensivePactRefuseAttitudeThreshold",
	"PermanentAllianceRefuseAttitudeThreshold",
	"VassalRefuseAttitudeThreshold",
	"DemandTributeAttitudeThreshold",
	"NoGiveHelpAttitudeThreshold",
}

# --- Required Nested Fields ---
NESTED_FIELDS_TO_SPECIFICALLY_PARSE = (
	"Flavors",
	"NoWarAttitudeProbs",
	"ContactRands",
	"ContactDelays",
	"MemoryAttitudePercents",
	"MemoryDecays",
)

ATTITUDES_FIELDS = (
	("FURIOUS", "iNoWarAttitudeProbFurious"),
	("ANNOYED", "iNoWarAttitudeProbAnnoyed"),
	("CAUTIOUS", "iNoWarAttitudeProbCautious"),
	("PLEASED", "iNoWarAttitudeProbPleased"),
	("FRIENDLY", "iNoWarAttitudeProbFriendly"),
)

FLAVOR_FIELDS = (
	("FLAVOR_MILITARY", "iFlavorMilitary"),
	("FLAVOR_RELIGION", "iFlavorReligion"),
	("FLAVOR_PRODUCTION", "iFlavorProduction"),
	("FLAVOR_GOLD", "iFlavorGold"),
	("FLAVOR_SCIENCE", "iFlavorScience"),
	("FLAVOR_CULTURE", "iFlavorCulture"),
	("FLAVOR_GROWTH", "iFlavorGrowth"),
	("FLAVOR_ESPIONAGE", "iFlavorEspionage"),
)

ALL_CONTACT_TYPES = (
	"CONTACT_RELIGION_PRESSURE",
	"CONTACT_CIVIC_PRESSURE",
	"CONTACT_JOIN_WAR",
	"CONTACT_STOP_TRADING",
	"CONTACT_GIVE_HELP",
	"CONTACT_ASK_FOR_HELP",
	"CONTACT_DEMAND_TRIBUTE",
	"CONTACT_TRADE_TECH",
	"CONTACT_TRADE_BONUS",
	"CONTACT_PEACE_TREATY",
	"CONTACT_OPEN_BORDERS",
	"CONTACT_DEFENSIVE_PACT",
	"CONTACT_PERMANENT_ALLIANCE",
	"CONTACT_TRADE_MAP",
)

POSITIVE_MEMORY_TYPES = (
	"MEMORY_GIVE_HELP",
	"MEMORY_ACCEPT_DEMAND",
	"MEMORY_ACCEPTED_RELIGION",
	"MEMORY_ACCEPTED_CIVIC",
	"MEMORY_ACCEPTED_JOIN_WAR",
	"MEMORY_ACCEPTED_STOP_TRADING",
	"MEMORY_VOTED_FOR_US",
	"MEMORY_EVENT_GOOD_TO_US",
	"MEMORY_LIBERATED_CITIES",
	"MEMORY_INDEPENDENCE",
	"MEMORY_TRADED_TECH_TO_US",
)

NEGATIVE_MEMORY_TYPES = (
	"MEMORY_DECLARED_WAR",
	"MEMORY_DECLARED_WAR_ON_FRIEND",
	"MEMORY_HIRED_WAR_ALLY",
	"MEMORY_NUKED_US",
	"MEMORY_NUKED_FRIEND",
	"MEMORY_RAZED_CITY",
	"MEMORY_RAZED_HOLY_CITY",
	"MEMORY_SPY_CAUGHT",
	"MEMORY_REFUSED_HELP",
	"MEMORY_REJECTED_DEMAND",
	"MEMORY_DENIED_RELIGION",
	"MEMORY_DENIED_CIVIC",
	"MEMORY_DENIED_JOIN_WAR",
	"MEMORY_DENIED_STOP_TRADING",
	"MEMORY_STOPPED_TRADING",
	"MEMORY_HIRED_TRADE_EMBARGO",
	"MEMORY_MADE_DEMAND",
	"MEMORY_VOTED_AGAINST_US",
	"MEMORY_EVENT_BAD_TO_US",
	"MEMORY_CANCELLED_VASSAL_AGREEMENT",
	"MEMORY_DECLARED_WAR_RECENT",
)

ALL_MEMORY_TYPES = POSITIVE_MEMORY_TYPES + NEGATIVE_MEMORY_TYPES

TYPE_HINTS = {
	"Type": str,
	"Description": str,
	"Civilopedia": str,
	"ArtDefineTag": str,
	"FavoriteCivic": str,
	"FavoriteReligion": str,
	"Traits": str,
	"Flavors": str,
	"ContactRands": str,
	"ContactDelays": str,
	"MemoryDecays": str,
	"MemoryAttitudePercents": str,
	"UnitAIWeightModifiers": str,
	"ImprovementWeightModifiers": str,
	"DiplomacyIntroMusicPeace": str,
	"DiplomacyIntroMusicWar": str,
}

# --- Helper functions ---

def infer_type(tag):
	if tag in REFUSE_ATTITUDE_FIELDS:
		return str
	return TYPE_HINTS.get(tag, int if tag.startswith("i") else str)

def parse_refuse_attitude_thresholds(tag, text, leader, leader_data):
	if text not in ATTITUDE_MAP:
		raise ValueError(f"[FATAL] Unknown attitude text '{text}' for tag '{tag}' at  refuse atttitude thresholds parsing stage in leader {leader}.")
	attr_name = f"i{tag}"
	leader_data[attr_name] = ATTITUDE_MAP[text]


# <!-- custom: for example if leader alexander has nowar missing / missing / 20 / 80 / missing, and defaults are nowar 0 / 0 / 0 / 0 / 100, then we want to parse any value alexander has to a higher number for example first to missing / missing / 20 / 80 / 80 and only then fetch missing values from defaults, so 0 / 0 / 20 / 80 / 80 for leader alexander's parsing nowar parsing for example, that we'd then parse exported as individual fields like iNoWarAttitudeProbFurious 0, etc... until iNoWarAttitudeProbFriendly 100 and in that order (matching ATTITUDES_FIELDS[0]) -->
def parse_nowar_probs_inline(child, leader_data, leader_key):
	"""
	Parse NoWarAttitudeProbs fields, ensuring correct ATTITUDES_FIELDS and monotonicity.
	Skips early fields until first defined value, then fills forward using max-so-far logic.
	"""
	nowar_tmp = {}

	# First, collect explicitly defined attitude values
	for entry in child:
		subfields = {sub.tag.split("}", 1)[1]: sub.text.strip() for sub in entry if sub.text}
		attitude = subfields.get("AttitudeType")
		value = subfields.get("iNoWarProb")
		if attitude and value:
			field = "iNoWarAttitudeProb" + attitude.replace("ATTITUDE_", "").capitalize()
			try:
				nowar_tmp[field] = int(value)
			except ValueError:
				raise ValueError(f"[WARNING] Non-integer NoWarProb for {leader_key} attitude {attitude}: '{value}'")

	# Now apply monotonicity with a "first-found" flag
	# <!-- custom: this is needed in case defaults are for example 0 / 0 / 0 / 0 / 100 , and leader_barbarian has for example (or other leaders imialrly or in another way related anyways etc) missing / missing / missing / missing / missing, then do not apply max_so_far 0 until a real first value has been found, else keep applying missing as the max i.e. keep missing, until then i.e. until if/when we find a real value to be a max_so_far can the max_so_far logic apply, else if we don't do that we'd get barbarian elader data as 0 / 0 / 0 / 0 / 0 instead of missing / missing / missing / missing / missing, which would then prevent defaults from being injected later, as a value of 0 was already applied everywhere, so the 100 at friendly would not be applied by defaults ; so adding in short or long or anyways etc the found_first logic also allows to keep using the max_so_far logic as we want, but only when relevant, i.e. only when/after/if the first occurence of a real value has been found, else keep assigning missing values no max_so_far_logic to ensure defaults cover us later nicely and accurately/reliably too if i may say but anyways etc -->
	found_first = False
	# Apply monotonicity rule to existing values
	# (e.g., Alexander: missing/missing/20/80/missing -> missing/missing/20/80/80)
	max_so_far = 0

	for att, field in ATTITUDES_FIELDS:
		value = nowar_tmp.get(field)

		if value is None:
			if not found_first:
				# Skip filling before first defined value
				continue
			else:
				# Fill forward using previous max
				leader_data[field] = max_so_far
		else:
			if found_first and value < max_so_far:
				raise ValueError(f"[ERROR] {leader_key}: NoWarProb {field} = {value} < previous max {max_so_far}")
			leader_data[field] = value
			max_so_far = value
			found_first = True

# Fetch from defaults <!-- custom:'s real leaders_data, not XML, much easier this way so we can handle the max so far logic already processed in defaults, for example a default of 0 / 0 / 88 / 0 / 0  would be maxed so far as 0 / 0 / 88 / 88 / 88 rather than 0 / 0 / 88 / 88 / 88, much easier if i am not mistaken too anyways etc, and no need to max from defaults again since we already did anyways etc -->
def ensure_complete_nowar_attitudes(leaders_data, leader_defaults_data):
	for leader_key, leader_data in leaders_data.items():
		if leader_key == "LEADER_DEFAULTS":
			continue  # Skip defaults itself

		for att, field in ATTITUDES_FIELDS:
			if field not in leader_data:
				if field not in leader_defaults_data:
					raise ValueError(f"[FATAL] Missing {field} in both leader and defaults: {leader_key}")
				leader_data[field] = leader_defaults_data[field]

def prune_nested_nowarattitudesprobs_if_flattened(leaders_data):
	"""
	Removes the legacy 'NoWarAttitudeProbs' field if all corresponding
	flat fields (iNoWarAttitudeProb*) are already present.
	"""
	required_fields = [
		"iNoWarAttitudeProbFurious",
		"iNoWarAttitudeProbAnnoyed",
		"iNoWarAttitudeProbCautious",
		"iNoWarAttitudeProbPleased",
		"iNoWarAttitudeProbFriendly",
	]
	for leader_data in leaders_data.values():
		if all(field in leader_data for field in required_fields):
			leader_data.pop("NoWarAttitudeProbs", None)

def parse_flavors_inline(child, leader_data, leader_key):
	# Don't initialize all flavors to 0 - let defaults injection handle missing ones
	seen_flavors = set()

	for entry in child:
		subfields = {sub.tag.split("}", 1)[1]: sub.text.strip() for sub in entry if sub.text}
		flavor = subfields.get("FlavorType")
		value = subfields.get("iFlavor")
		if flavor and value:
			if flavor in seen_flavors:
				print(f"[WARNING] Duplicate FlavorType '{flavor}' for leader {leader_key}")
			seen_flavors.add(flavor)
			for flavor_key, field_name in FLAVOR_FIELDS:
				if flavor == flavor_key:
					try:
						leader_data[field_name] = int(value)
					except ValueError:
						print(f"[WARNING] Non-integer Flavor for {leader_key} flavor {flavor}: '{value}'")
						leader_data[field_name] = 0

# <!-- custom: new addition by Claude AI thanks to my prompt too but anyways etc.. successfully handles flavors no defaults being injected (for example flavor military 10 and flavor religion missing in a leader, with defaults being military 789 and religion 123 not leading to the leader having military 10 and religion 123 but instead it had before fix military 10 religion 0, as successfully detected by the test now:
"""[TEST FAILED] Parsed sample does not match expected!

--- Mismatches for LEADER_ALEXANDER ---
- Field 'iFlavorReligion' mismatch: expected '0', got '123'

--- Mismatches for LEADER_CATHERINE ---
- Field 'iFlavorReligion' mismatch: expected '0', got '123'

--- Mismatches for LEADER_GANDHI ---
- Field 'iFlavorMilitary' mismatch: expected '0', got '789'
- Field 'iFlavorReligion' mismatch: expected '0', got '123'
[EXIT] Leader sample test failed. File not written.
"""
# which indicates that this is now fixed, thanks to Claude AI and my prompt too hehe anyways etc -->
def ensure_complete_flavors(leaders_data):
	"""
	Ensure all leaders have all flavor fields, setting missing ones to 0.
	This should be called after defaults injection.
	"""
	for leader_data in leaders_data.values():
		for _, field_name in FLAVOR_FIELDS:
			if field_name not in leader_data:
				leader_data[field_name] = 0

def prune_nested_flavors_if_flattened(leaders_data):
	"""
	Removes the legacy 'Flavors' field if all flat iFlavor* fields are already present.
	"""
	required_flavor_fields = [
		"iFlavorMilitary",
		"iFlavorReligion",
		"iFlavorProduction",
		"iFlavorGold",
		"iFlavorScience",
		"iFlavorCulture",
		"iFlavorGrowth",
		"iFlavorEspionage",
	]
	for leader_data in leaders_data.values():
		if all(field in leader_data for field in required_flavor_fields):
			leader_data.pop("Flavors", None)

# === Robust Contact Delay/Rand Parser ===
def parse_contact_delays_inline(parent_node):
	results = []
	for entry in parent_node.findall("civ4:ContactDelay", ns):
		contact_type = entry.findtext("civ4:ContactType", default="", namespaces=ns).strip()
		delay_val = entry.findtext("civ4:iContactDelay", default="", namespaces=ns).strip()
		if contact_type and delay_val:
			try:
				results.append({
					"ContactType": contact_type,
					"iContactDelay": int(delay_val)
				})
			except ValueError:
				raise ValueError(f"[TYPE ERROR] ContactDelay has invalid iContactDelay='{delay_val}' for {contact_type}")
		else:
			raise ValueError(f"[MISSING] ContactDelay is missing field(s): {contact_type=} {delay_val=}")
	return results


def parse_contact_rands_inline(parent_node):
	results = []
	for entry in parent_node.findall("civ4:ContactRand", ns):
		contact_type = entry.findtext("civ4:ContactType", default="", namespaces=ns).strip()
		rand_val = entry.findtext("civ4:iContactRand", default="", namespaces=ns).strip()
		if contact_type and rand_val:
			try:
				results.append({
					"ContactType": contact_type,
					"iContactRand": int(rand_val)
				})
			except ValueError:
				raise ValueError(f"[TYPE ERROR] ContactRand has invalid iContactRand='{rand_val}' for {contact_type}")
		else:
			raise ValueError(f"[MISSING] ContactRand is missing field(s): {contact_type=} {rand_val=}")
	return results

def parse_memory_attitudes_inline(parent_node):
	results = []
	for entry in parent_node.findall("civ4:MemoryAttitudePercent", ns):
		mem_type = entry.findtext("civ4:MemoryType", default="", namespaces=ns).strip()
		attitude_val = entry.findtext("civ4:iMemoryAttitudePercent", default="", namespaces=ns).strip()
		if mem_type and attitude_val:
			try:
				results.append({
					"MemoryType": mem_type,
					"iMemoryAttitudePercent": int(attitude_val)
				})
			except ValueError:
				errors.append(f"[TYPE ERROR] MemoryAttitudePercent has invalid iMemoryAttitudePercent='{attitude_val}' for {mem_type}")
		else:
			errors.append(f"[MISSING] MemoryAttitudePercent is missing field(s): {mem_type=} {attitude_val=}")
	return results

def parse_memory_decays_inline(parent_node):
	results = []
	for entry in parent_node.findall("civ4:MemoryDecay", ns):
		mem_type = entry.findtext("civ4:MemoryType", default="", namespaces=ns).strip()
		mem_decay = entry.findtext("civ4:iMemoryRand", default="", namespaces=ns).strip()
		if mem_type and mem_decay:
			try:
				results.append({
					"MemoryType": mem_type,
					"iMemoryDecay": int(mem_decay)
				})
			except ValueError:
				errors.append(f"[TYPE ERROR] MemoryDecay has invalid iMemoryRand='{mem_decay}' for {mem_type}")
		else:
			errors.append(f"[MISSING] MemoryDecay is missing field(s): {mem_type=} {mem_decay=}")
	return results

def force_complete_contact_delays(leaders_data, leader_defaults_data):
    leader_defaults_data_ = {e["ContactType"]: e.copy() for e in leader_defaults_data.get("ContactDelays", [])}

    for contact_type in ALL_CONTACT_TYPES:
        if contact_type not in leader_defaults_data_:
            raise ValueError(f"[FATAL] LEADER_DEFAULTS is missing ContactDelay for {contact_type}.")

    for leader_type, leader_data in leaders_data.items():
        if leader_type == "LEADER_DEFAULTS":
            continue

        custom_entries = {e["ContactType"]: e.copy() for e in leader_data.get("ContactDelays", [])}
        merged = {
            ct: custom_entries.get(ct, leader_defaults_data_[ct])
            for ct in ALL_CONTACT_TYPES
        }
        leader_data["ContactDelays"] = list(merged.values())

    return leaders_data

def force_complete_contact_rands(leaders_data, leader_defaults_data):
    leader_defaults_data_ = {e["ContactType"]: e.copy() for e in leader_defaults_data.get("ContactRands", [])}

    for contact_type in ALL_CONTACT_TYPES:
        if contact_type not in leader_defaults_data_:
            raise ValueError(f"[FATAL] LEADER_DEFAULTS is missing ContactRand for {contact_type}.")

    for leader_type, leader_data in leaders_data.items():
        if leader_type == "LEADER_DEFAULTS":
            continue

        custom_entries = {e["ContactType"]: e.copy() for e in leader_data.get("ContactRands", [])}
        merged = {
            ct: custom_entries.get(ct, leader_defaults_data_[ct])
            for ct in ALL_CONTACT_TYPES
        }
        leader_data["ContactRands"] = list(merged.values())

    return leaders_data

def force_complete_memory_decays(leaders_data, leader_defaults_data):
	print("DEBUG: Defaults MemoryDecays (flat):", leader_defaults_data.get("MemoryDecays"))

	leader_defaults_data_ = {
		e["MemoryType"]: e.copy()
		for e in leader_defaults_data.get("MemoryDecays", [])
	}

	# 🚨 Hard fail if any expected memory type is missing from defaults
	for mem_type in ALL_MEMORY_TYPES:
		if mem_type not in leader_defaults_data_:
			raise ValueError(f"[FATAL] LEADER_DEFAULTS is missing MemoryDecay for {mem_type}. This is required to prevent placeholder data.")

	for leader_type, leader_data in leaders_data.items():
		if leader_type == "LEADER_DEFAULTS":
			continue

		custom_entries = {
			e["MemoryType"]: e.copy()
			for e in leader_data.get("MemoryDecays", [])
		}

		merged = {}
		for mem_type in ALL_MEMORY_TYPES:
			if mem_type in custom_entries:
				merged[mem_type] = custom_entries[mem_type]
			else:
				merged[mem_type] = leader_defaults_data_[mem_type]

		leader_data["MemoryDecays"] = list(merged.values())

	return leaders_data

def force_complete_memory_attitudes(leaders_data, leader_defaults_data):
	print("DEBUG: leader_defaults_data MemoryAttitudes (flat):", leader_defaults_data.get("MemoryAttitudePercents"))

	leader_defaults_data_ = {
		e["MemoryType"]: e.copy()
		for e in leader_defaults_data.get("MemoryAttitudePercents", [])
	}

	# 🚨 Hard fail if any expected memory type is missing from defaults
	for mem_type in ALL_MEMORY_TYPES:
		if mem_type not in leader_defaults_data_:
			raise ValueError(f"[FATAL] LEADER_DEFAULTS is missing MemoryAttitude for {mem_type}. This is required to prevent placeholder data.")

	for leader_type, leader_data in leaders_data.items():
		if leader_type == "LEADER_DEFAULTS":
			continue

		custom_entries = {
			e["MemoryType"]: e.copy()
			for e in leader_data.get("MemoryAttitudePercents", [])
		}

		merged = {}
		for mem_type in ALL_MEMORY_TYPES:
			if mem_type in custom_entries:
				merged[mem_type] = custom_entries[mem_type]
			else:
				merged[mem_type] = leader_defaults_data_[mem_type]

		leader_data["MemoryAttitudePercents"] = list(merged.values())

	return leaders_data

def contact_to_camel(contact_type):
        return capwords(contact_type.replace("CONTACT_", "").replace("_", " ")).replace(" ", "")

def adjust_contact_values(contact_delay_raw, contact_rand_raw):
	"""
	Adjusts contact delay and contact rand values according to standard rules.
	Returns: (adjusted_delay, adjusted_rand, aggregated_prob_forced_zero_flag)
	"""
	if contact_delay_raw < 0:
		# <!-- custom: detail: if delay < 0 (rand is meaningless/irrelevant but we still store it (for exhaustiveness and ui display of raw value anyways)), delay is infinite, probability of contact is 0 -->
		adjusted_delay = 999  # Infinite delay

		if contact_rand_raw <= 0:
			adjusted_rand = 0
		else:
			adjusted_rand = contact_rand_raw
		return adjusted_delay, adjusted_rand, True  # Forced 0 aggregation
	else:
		# <!-- custom: the higher the delay the worse/lower the contact prob (example gandhi's data/values vs montezuma so we (should i think anyways) invert both)-->
		adjusted_delay = contact_delay_raw

		if contact_rand_raw <= 0:
			# <!-- custom: (and else,) if rand is <=0, AI has a compatible delay but still never engages due to rand, so probability of contact is still 0. Only outside of these edge cases can the contact probabiltiy be computed if i'm not mistaken, else should be 0 as in this code block/check if i'm not mistaken anyways. -->
			# Can try, but refuses to ever engage → Aggregated ContactProb = 0
			adjusted_rand = 0
			return adjusted_delay, adjusted_rand, True

		else:
			# <!-- custom: (and else,), if both delay and rand are compatible with havig a scaling and acutal contact probability (that we can compute too maybe here indeed anyways etc), then (to compute this we propose this formula that) the higher the delay the worse/lower the contact prob, and the higher the rand the worse/lower the contact prob (example gandhi's data/values vs montezuma so we (should i think anyways) invert both)-->
			adjusted_rand = contact_rand_raw
			return adjusted_delay, adjusted_rand, False  # Normal aggregation

def fetch_contact_min_max(contact_type, leaders_data):
	"""
	Fetch the min and max for delay and rand fields for a specific contact_type.
	Returns: (min_delay, max_delay, min_rand, max_rand)
	"""
	delay_field = f"iContact{contact_type.replace('_', '').title()}DelayRaw"
	rand_field = f"iContact{contact_type.replace('_', '').title()}RandRaw"

	all_delays = []
	all_rands = []

	for leader_type in VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES:
		leader_data = leaders_data[leader_type]
		if delay_field in leader_data:
			d = leader_data[delay_field]
			if isinstance(d, int) and d >= 0:
				all_delays.append(d)
		if rand_field in leader_data:
			r = leader_data[rand_field]
			if isinstance(r, int) and r >= 0:
				all_rands.append(r)

	if all_delays and all_rands:
		return (min(all_delays), max(all_delays), min(all_rands), max(all_rands))
	else:
		raise ValueError(f"[FATAL] Memory min/max values missing for {delay_field} or/and {rand_field}. Likely cause: default memory flattening was skipped.")

def flatten_all_contacts(leaders_data):
	debug_log = []
	aggregated_score_raw_by_type = {suffix: [] for suffix in ALL_CONTACT_TYPES}

	# First pass: extract raw values and compute adjusted values (for scoring + min/max)
	for leader_type, leader_data in leaders_data.items():
		contact_delays = leader_data["ContactDelays"]
		contact_rands = leader_data["ContactRands"]

		if not contact_delays or not contact_rands:
			raise ValueError(f"Missing ContactDelays or/and ContactRands for {leader_type} during flattening")

		for contact_type in ALL_CONTACT_TYPES:
			full_contact_type = f"{contact_type}"
			short_name = contact_to_camel(contact_type)

			contact_delay_raw = None
			contact_rand_raw = None

			# Strict fetch with no fallbacks
			for entry in contact_delays:
				if entry.get("ContactType") == full_contact_type:
					val = entry.get("iContactDelay")
					if val is None:
						raise ValueError(f"[FATAL] Missing iContactDelay for {full_contact_type} in {leader_type}")
					contact_delay_raw = int(val)
					break

			for entry in contact_rands:
				if entry.get("ContactType") == full_contact_type:
					val = entry.get("iContactRand")
					if val is None:
						raise ValueError(f"[FATAL] Missing iContactRand for {full_contact_type} in {leader_type}")
					contact_rand_raw = int(val)
					break

			if contact_delay_raw is None or contact_rand_raw is None:
				raise ValueError(f"[FATAL] Contact delay/rand missing for {full_contact_type} in {leader_type}. Did you run force_complete_contact_rands/delays() first?")

			# Store raw for UI
			leader_data[f"iContact{short_name}DelayRaw"] = contact_delay_raw
			leader_data[f"iContact{short_name}RandRaw"] = contact_rand_raw

			# Adjust for logic + scoring
			adjusted_delay, adjusted_rand, forced_zero = adjust_contact_values(contact_delay_raw, contact_rand_raw)
			leader_data[f"iContact{short_name}DelayAdjusted"] = adjusted_delay
			leader_data[f"iContact{short_name}RandAdjusted"] = adjusted_rand
			leader_data[f"bContact{short_name}ForceZero"] = forced_zero

	# Precompute min/max from adjusted values only
	contact_min_max = {}
	for contact_type in ALL_CONTACT_TYPES:
		short_name = contact_to_camel(contact_type)
		delay_field = f"iContact{short_name}DelayAdjusted"
		rand_field = f"iContact{short_name}RandAdjusted"

		all_delays = []
		all_rands = []

		for leader_type in VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES:
			leader_data = leaders_data[leader_type]
			d = leader_data.get(delay_field)
			r = leader_data.get(rand_field)
			if isinstance(d, int):
				all_delays.append(d)
			if isinstance(r, int):
				all_rands.append(r)

		if all_delays and all_rands:
			contact_min_max[contact_type] = (min(all_delays), max(all_delays), min(all_rands), max(all_rands))
		else:
			contact_min_max[contact_type] = (0, 0, 0, 0)

	# Second pass: compute raw aggregate scores
	for leader_type, leader_data in leaders_data.items():
		if leader_type in EXCLUDED_LEADERS_FROM_ATTRIBUTES_AGGREGATION:
			for contact_type in ALL_CONTACT_TYPES:
				short_name = contact_to_camel(contact_type)
				leader_data[f"iAggregatedContact{short_name}Prob"] = SENTINEL_AGGREGATED_DUMMY_VALUE
			continue

		for contact_type in ALL_CONTACT_TYPES:
			short_name = contact_to_camel(contact_type)
			delay = leader_data[f"iContact{short_name}DelayAdjusted"]
			rand = leader_data[f"iContact{short_name}RandAdjusted"]
			forced_zero = leader_data[f"bContact{short_name}ForceZero"]
			min_delay, max_delay, min_rand, max_rand = contact_min_max[contact_type]

			delay_norm_score = normalize_to_100(delay, min_delay, max_delay, invert=True, attr_name="delay")
			rand_norm_score = normalize_to_100(rand, min_rand, max_rand, invert=True, attr_name="rand")

			if forced_zero:
				aggregated_score_raw = 0
			else:
				aggregated_score_raw = 0.7 * delay_norm_score + 0.3 * rand_norm_score

			leader_data[f"iAggregatedContact{short_name}ProbRaw"] = aggregated_score_raw
			aggregated_score_raw_by_type[contact_type].append(aggregated_score_raw)

			if DEBUG_CONTACT_FLATTENING:
				debug_log.append(
					f"[DEBUG] {leader_type} {contact_type}: raw=({delay},{rand}), adj=({delay},{rand}), "
					f"norm=({delay_norm_score},{rand_norm_score}), score={aggregated_score_raw:.2f}"
				)

	# Third pass: normalize final scores
	for contact_type in ALL_CONTACT_TYPES:
		short_name = contact_to_camel(contact_type)
		scores = aggregated_score_raw_by_type[contact_type]
		if not scores:
			continue
		min_score = min(scores)
		max_score = max(scores)

		for leader_type in VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES:
			raw = leaders_data[leader_type].get(f"iAggregatedContact{short_name}ProbRaw")
			norm = normalize_to_100(raw, min_score, max_score, invert=False, attr_name=f"iAggregatedContact{short_name}Prob")
			leaders_data[leader_type][f"iAggregatedContact{short_name}Prob"] = norm
			del leaders_data[leader_type][f"iAggregatedContact{short_name}ProbRaw"]

	if DEBUG_CONTACT_FLATTENING:
		print("\n".join(debug_log))

def prune_nested_contact_lists_if_flattened(leaders_data):
	"""
	Removes 'ContactRands' and 'ContactDelays' if all contact types have been flattened.
	"""
	for leader_data in leaders_data.values():
		has_all_flat = all(
			f"iContact{contact_to_camel(contact)}DelayRaw" in leader_data and
			f"iContact{contact_to_camel(contact)}RandRaw" in leader_data
			for contact in ALL_CONTACT_TYPES
		)
		if has_all_flat:
			leader_data.pop("ContactRands", None)
			leader_data.pop("ContactDelays", None)

def remove_intermediate_contact_fields(leaders_data):
	"""
	Safer version: Remove known memory and contact Adjusted / ForceZero fields
	after flattening, *only for fields we know we added*, using memory/contact types.
	"""
	# --- Contact fields ---
	for contact_type in ALL_CONTACT_TYPES:
		short_name = contact_to_camel(contact_type)
		for field_template in [
			"iContact{suffix}DelayAdjusted",
			"iContact{suffix}RandAdjusted",
			"bContact{suffix}ForceZero"
		]:
			field_name = field_template.format(suffix=short_name)
			for leader_data in leaders_data.values():
				leader_data.pop(field_name, None)

def memory_to_camel(mem_type):
        return capwords(mem_type.replace("MEMORY_", "").replace("_", " ")).replace(" ", "")

def fetch_memory_min_max(mem_type, leaders_data, is_positive):
	"""
	Fetch the min and max for a specific memory type's attitude and decay values.
	Returns: (min_attitude, max_attitude, min_decay, max_decay)
	"""
	mem_suffix = memory_to_camel(mem_type)
	att_field = f"iPositiveMemoryAttitude{mem_suffix}Raw" if is_positive else f"iNegativeMemoryAttitude{mem_suffix}Raw"
	dec_field = f"iPositiveMemoryDecay{mem_suffix}Raw" if is_positive else f"iNegativeMemoryDecay{mem_suffix}Raw"

	all_attitudes = []
	all_decays = []

	for leader_type in VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES:
		leader_data = leaders_data.get(leader_type, {})
		att = leader_data.get(att_field)
		dec = leader_data.get(dec_field)

		if isinstance(att, int):
			all_attitudes.append(att)
		if isinstance(dec, int):
			all_decays.append(dec)

	if all_attitudes and all_decays:
		return (min(all_attitudes), max(all_attitudes), min(all_decays), max(all_decays))
	else:
		raise ValueError(f"[FATAL] Missing attitude or decay values for {mem_type}. Flattening may have failed.")

def adjust_memory_values(raw_attitude, raw_decay, mem_type, is_positive, is_affection):
	"""
	Adjusts memory attitude and decay values according to standard rules.
	Returns: (adjusted_attitude, adjusted_decay)
	"""
	# Step 1: Adjust attitude (with DLL-specific logic)
	# <!-- custom: For(/if memory type is MEMORY_TRADED_TECH_TO_US), we need to first adjust the raw value as per this comment to keep accuracy of positive distribution and not hide some low value negative numbers in particular, for example (0.8 * (-2)) + 4 = -1.6 + 4 = 2.4 which is positive so needs to be ranked relatively to other positive memories as such.
	#
	# DLL comment:
	# <!-- Needs to be set for each leader individually.
	# advc.553 (note): The DLL takes it times 0.8 and adds 4. -->
	#		<MemoryAttitudePercent>
	#			<MemoryType>MEMORY_TRADED_TECH_TO_US</MemoryType>
	#			<iMemoryAttitudePercent>-1</iMemoryAttitudePercent>
	#		</MemoryAttitudePercent>
	#
	# As for us in this xml py parser, we can almost always just follow distribution regardless of how its value is transofrmed by the DLL, like in other memory types or attributes where we don't need to care even if the DLL (were to) (or) does some (possible transformations) as long as they don't shift the negative distribution / positive distribution of first value's start/initial point. In such cases, we don't need to strictly replicate the DLL's math and can just rank the XML values, but in this case the negative point (and first positive point value is shifted so we need to include more values and faithfully account for it)
	# -->
	if is_positive and mem_type == "MEMORY_TRADED_TECH_TO_US":

		adjusted_att = 0.8 * raw_attitude + 4
	else:
		adjusted_att = raw_attitude

	# Step 2: Clamp invalid affection/resentment signs to 0
	if is_affection:
		# Affection must be non-negative
		if adjusted_att < 0:
			print(f"[WARNING] Affection memory {mem_type} has negative adjusted attitude: {adjusted_att}. Rounded to 0.")
			adjusted_att = 0
	else:
		# Resentment must be non-positive
		if adjusted_att > 0:
			print(f"[WARNING] Resentment memory {mem_type} has positive adjusted attitude: {adjusted_att}. Rounded to 0.")
			adjusted_att = 0

	# Step 3: Adjust decay (decay must be non-negative)
	adjusted_decay = max(0, raw_decay)

	return adjusted_att, adjusted_decay, False # We never force aggregation to 0 for memories unlike in contact code, despite their similarities, so just one False here should be enough hopefulyl maybe anyways.

def get_memory_attitude_and_decay_invert_flags(is_positive, is_affection):
	if is_positive:
		if is_affection:
			# <!-- custom: higher attitude score (ex: + 350 > + 200) means more intense positive feeling (affection), closer to 0 means AI cares less (0 should be              - minimum -               atitudes after normalization unless i'm mistaken anyways but should be as this if i'm not mistaken anyways (where again AI cares the least)), so we don't invert.
			# -->
			# As for decay it should remain the same as it seems to just be some time unit or span (always positive if i'm not mistaken? At least after checking seems so in advciv data and in our mod AdvCiv-SAS at least so far, anyways) if i am not mistaken but this is just an assumption that could be accurate or not but that i think is (accurate), anyways -->
			return False, False
		else:
			# <!-- custom: lower attitude score (ex: -350 < -200) means more intense negative feeling (resentment) (resentful and (more) especially spiteful AI even for (presumably) good deeds), closer to 0 means AI cares less (0 should be              - maximum -               attitudes after normalization unless i'm mistaken anyways but should be as this if i'm not mistaken anyways (where again AI also, as in positive affection, for this value 0 (after adjustment) attitude, cares the least (at least we model it a such))), so we should invert indeed.
			# More detail on why and to be careful since these are negative values unlike most civ4 data (a good fail check too maybe to review or learn for me at least anways etc anyways), is that since our normalize_to_100 function shifts to 0 distribution before normalizing (i.e. -350 is now -350 + 350 = 0, and -200 is now -200 + 350 = 150 if i'm not mistaken anyways) then the lower the score is (0 vs 150 before normalization, which is (after normalization) 0 / 150 * 100 = 0 vs 100 / 150 * 100 = 100, then -350 (now 0) which was more intense(ly negative feeling (resentment)) is the lowest, while -200 (now 100) with the lowest (in comparison relatively) feeling is now the highest in score, so the atititude score should indeed be inverted, hopefully safe now but anyways etc anyways.
			# -->
			# As for decay it should be the same as above unless i'm mistaken but shouldn't be but anywyas, anyways. -->
			return True, False

	else:
		if is_affection:
			# <!-- custom: similarly but in negative memories, higher attitude score (ex: + 350 > + 200) means more affection for them (more and more masochistic or similar AI anyways.. which i don't dislike but anyways... Not necessarily especialyl like but anyways (either/too)(or why not?) but anyways...), so we don't invert. -->
			return False, False
		else:
			# # <!-- custom: similarly but in negative memories, lower attitude score (ex: -350 < -200) means more intense negative feeling (resentment) (resentful and (more) especially spiteful AI but this time in an (seemingly) expected way if (conventionally) harm(ful behaviour or other thing or similar anyways etc thing anyways etc) is done to it), closer to 0 means AI cares less (0 should be              - maximum -               attitudes after normalization unless i'm mistaken anyways but should be as this if i'm not mistaken anyways), so we invert.. -->
			return True, False

def flatten_all_memories(leaders_data, is_positive, is_affection):
	"""
	Refactored version: Flattens and computes normalized aggregated memory scores
	using a strict raw → adjust → minmax → normalize → aggregated pipeline.

	NOTE: This function requires that all leaders (including LEADER_DEFAULTS) have fully populated MemoryAttitudePercents and MemoryDecays fields, either from XML or via force-complete patching.
	If any field is missing, the function will raise an error instead of assuming (0,0) placeholders.
	"""
	if "LEADER_DEFAULTS" not in leaders_data or "MemoryAttitudePercents" not in leaders_data["LEADER_DEFAULTS"] or "MemoryDecays" not in leaders_data["LEADER_DEFAULTS"]:
		raise RuntimeError("[FATAL] LEADER_DEFAULTS missing or not parsed. Cannot proceed without default memory values.")

	debug_log = []
	memory_types = POSITIVE_MEMORY_TYPES if is_positive else NEGATIVE_MEMORY_TYPES
	aggregated_raw_by_type = {mem_type: [] for mem_type in memory_types}
	suffix_prefix = "Positive" if is_positive else "Negative"
	affect_type = "Affection" if is_affection else "Resentment"

	# Step 1: Extract raw values and compute adjusted ones
	for leader_type, leader_data in leaders_data.items():
		for mem_type in memory_types:
			mem_suffix = memory_to_camel(mem_type)
			att_key_raw = f"i{suffix_prefix}MemoryAttitude{mem_suffix}Raw"
			dec_key_raw = f"i{suffix_prefix}MemoryDecay{mem_suffix}Raw"
			att_key_adj = f"i{suffix_prefix}MemoryAttitude{mem_suffix}Adjusted"
			dec_key_adj = f"i{suffix_prefix}MemoryDecay{mem_suffix}Adjusted"
			zero_flag_key = f"b{suffix_prefix}Memory{mem_suffix}ForceZero"

			# Fetch from nested structures with strict validation (no placeholders)
			attitude_raw = None
			decay_raw = None

			# Search for attitude
			for entry in leader_data["MemoryAttitudePercents"]:
				if entry.get("MemoryType") == mem_type:
					val = entry.get("iMemoryAttitudePercent")
					if val is None:
						raise ValueError(f"[FATAL] Missing iMemoryAttitudePercent for {mem_type} in {leader_type}")
					attitude_raw = int(val)
					break  # Only use first match

			# Search for decay
			for entry in leader_data["MemoryDecays"]:
				if entry.get("MemoryType") == mem_type:
					val = entry.get("iMemoryDecay")
					if val is None:
						raise ValueError(f"[FATAL] Missing iMemoryDecay for {mem_type} in {leader_type}")
					decay_raw = int(val)
					break

			if attitude_raw is None or decay_raw is None:
				raise ValueError(f"[FATAL] Missing {mem_type} attitude_raw or/and decay_raw field in {leader_type}. Run force_complete_memory_attitudes/decays() first.")

			# Store raw for UI
			leader_data[att_key_raw] = attitude_raw
			leader_data[dec_key_raw] = decay_raw

			# Adjust for logic + scoring
			att_adj, dec_adj, force_zero = adjust_memory_values(attitude_raw, decay_raw, mem_type, is_positive, is_affection)
			leader_data[att_key_adj] = att_adj
			leader_data[dec_key_adj] = dec_adj
			leader_data[zero_flag_key] = force_zero

	# Step 2: Compute min/max from adjusted values
	memory_min_max = {}
	for mem_type in memory_types:
		mem_suffix = memory_to_camel(mem_type)
		att_key_adj = f"i{suffix_prefix}MemoryAttitude{mem_suffix}Adjusted"
		dec_key_adj = f"i{suffix_prefix}MemoryDecay{mem_suffix}Adjusted"
		all_attitudes = []
		all_decays = []
		for leader_type in VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES:
			leader_data = leaders_data[leader_type]
			a = leader_data.get(att_key_adj)
			d = leader_data.get(dec_key_adj)
			if isinstance(a, (int, float)):
				all_attitudes.append(a)
			if isinstance(d, (int, float)):
				all_decays.append(d)
		if all_attitudes and all_decays:
			memory_min_max[mem_type] = (min(all_attitudes), max(all_attitudes), min(all_decays), max(all_decays))
		else:
			memory_min_max[mem_type] = (0, 0, 0, 0)

	# Step 3: Score and store unnormalized aggregated attributes
	for leader_type, leader_data in leaders_data.items():
		if leader_type in EXCLUDED_LEADERS_FROM_ATTRIBUTES_AGGREGATION:
			for mem_type in memory_types:
				mem_suffix = memory_to_camel(mem_type)
				final_key = f"iAggregated{suffix_prefix}Memory{mem_suffix}{affect_type}"
				leader_data[final_key] = SENTINEL_AGGREGATED_DUMMY_VALUE
			continue

		for mem_type in memory_types:
			mem_suffix = memory_to_camel(mem_type)
			att_adj = leader_data[f"i{suffix_prefix}MemoryAttitude{mem_suffix}Adjusted"]
			dec_adj = leader_data[f"i{suffix_prefix}MemoryDecay{mem_suffix}Adjusted"]
			force_zero = leader_data[f"b{suffix_prefix}Memory{mem_suffix}ForceZero"]
			min_att, max_att, min_dec, max_dec = memory_min_max[mem_type]

			is_inverted_att, is_inverted_dec = get_memory_attitude_and_decay_invert_flags(is_positive, is_affection)

			norm_att = normalize_to_100(att_adj, min_att, max_att, is_inverted_att, attr_name=f"{mem_type}_att")
			norm_dec = normalize_to_100(dec_adj, min_dec, max_dec, is_inverted_dec, attr_name=f"{mem_type}_dec")
			combined = 0 if force_zero else 0.7 * norm_att + 0.3 * norm_dec

			raw_key = f"iAggregated{suffix_prefix}Memory{mem_suffix}{affect_type}Raw"
			leader_data[raw_key] = combined
			aggregated_raw_by_type[mem_type].append(combined)

			if DEBUG_MEMORY_FLATTENING:
				debug_log.append(
					f"[DEBUG] {leader_type} {mem_type}: att_raw={att_adj}, dec_raw={dec_adj}, norm_att={norm_att:.1f}, norm_dec={norm_dec:.1f}, raw_combined={combined:.2f}"
				)

	# Step 4: Normalize final scores
	for mem_type in memory_types:
		mem_suffix = memory_to_camel(mem_type)
		final_key = f"iAggregated{suffix_prefix}Memory{mem_suffix}{affect_type}"
		raw_key = f"{final_key}Raw"
		scores = aggregated_raw_by_type[mem_type]
		if not scores:
			continue
		min_score = min(scores)
		max_score = max(scores)

		for leader_type in VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES:
			raw = leaders_data[leader_type].get(raw_key)
			norm = normalize_to_100(raw, min_score, max_score, invert=False, attr_name=final_key)
			leaders_data[leader_type][final_key] = norm
			del leaders_data[leader_type][raw_key]

	if DEBUG_MEMORY_FLATTENING:
		print("\n".join(debug_log))

def prune_nested_memory_lists_if_flattened(leaders_data, is_positive):
	"""
	Removes 'MemoryAttitudePercents' and 'MemoryDecays' if all memory fields have been flattened.
	"""
	memory_types = POSITIVE_MEMORY_TYPES if is_positive else NEGATIVE_MEMORY_TYPES
	suffix_prefix = "Positive" if is_positive else "Negative"

	for leader_data in leaders_data.values():
		has_all_flat = all(
			f"i{suffix_prefix}MemoryAttitude{memory_to_camel(mem_type)}Raw" in leader_data and
			f"i{suffix_prefix}MemoryDecay{memory_to_camel(mem_type)}Raw" in leader_data
			for mem_type in memory_types
		)
		if has_all_flat:
			leader_data.pop("MemoryAttitudePercents", None)
			leader_data.pop("MemoryDecays", None)

def remove_intermediate_memory_fields(leaders_data):
	"""
	Safer version: Remove known memory and contact Adjusted / ForceZero fields
	after flattening, *only for fields we know we added*, using memory/contact types.
	"""
	# --- Memory fields ---
	for is_positive in [True, False]:
		suffix_prefix = "Positive" if is_positive else "Negative"
		memory_types = POSITIVE_MEMORY_TYPES if is_positive else NEGATIVE_MEMORY_TYPES
		for mem_type in memory_types:
			mem_suffix = memory_to_camel(mem_type)
			for field_template in [
				"i{prefix}MemoryAttitude{suffix}Adjusted",
				"i{prefix}MemoryDecay{suffix}Adjusted",
				"b{prefix}Memory{suffix}ForceZero"
			]:
				field_name = field_template.format(prefix=suffix_prefix, suffix=mem_suffix)
				for leader_data in leaders_data.values():
					leader_data.pop(field_name, None)

# === Parse XML File ===
try:
	tree = ET.parse(xml_path)
	root = tree.getroot()
except Exception as e:
	raise RuntimeError(f"[FATAL ERROR] Could not open or parse XML file: {xml_path}\n{str(e)}")

leaders_data = {}
errors = []
leader_defaults_data = {}

def inject_defaults(leader_defaults_data, leader_data):
	for tag, default_val in leader_defaults_data.items():
		if tag not in leader_data:
			leader_data[tag] = default_val
		else:
			if isinstance(default_val, list) and isinstance(leader_data[tag], list) and default_val:
				# Only merge if default list is non-empty
				if tag in ["ContactRands", "ContactDelays"]:
					key_field = "ContactType"
				elif tag in ["MemoryDecays", "MemoryAttitudePercents"]:
					key_field = "MemoryType"
				elif tag in ["UnitAIWeightModifiers"]:
					key_field = "UnitAIType"
				elif tag in ["ImprovementWeightModifiers"]:
					key_field = "ImprovementType"
				else:
					key_field = None
				
				if key_field:
					existing_keys = {entry.get(key_field) for entry in leader_data[tag]}
					for default_entry in default_val:
						if default_entry.get(key_field) not in existing_keys:
							leader_data[tag].append(default_entry)

def parse_leader(leader, leader_type, leader_data, seen_tags):
	for child in leader:
		tag = child.tag.split("}", 1)[1] if "}" in child.tag else child.tag
		text = child.text.strip() if child.text else ""
		if tag in seen_tags:
			raise KeyError(f"[KEY ERROR] Duplicate tag <{tag}> in leader {leader_type}")
		seen_tags.add(tag)
		expected = infer_type(tag)

		# <!-- custom: nested fields first so that <Flavors/> for example which is a valid field (all flavor set to 0 if i am not mistaken, unlike non-existing Flavors field at all which should if i am not mistaken and as we want if i may say at least me but anyways etc raises an error below) is handled as 0 0 0 0 0 (etc for each flavor) rather than going through the len(child) == 0 where no parsing of flavors happen at all since Flavors is a nested field we don't want to handle as such (i.e. that we don't want to handle it as a flat, non-nested XML field, anyways etc), so we handle the exceptions first if i may say but anyways etc then the general case(s) seems safer or/and more reliable or/and accurate as chatgpt/becomingthrough did and explained to me as well as thanks to my promtps and own reflection and such if i may say but anyways etc... -->
		# --- always handle known nested tags first — even if empty
		if tag == "NoWarAttitudeProbs":
			parse_nowar_probs_inline(child, leader_data, leader_type)
		elif tag == "Flavors":
			parse_flavors_inline(child, leader_data, leader_type)
		elif tag == "ContactRands":
			leader_data["ContactRands"] = parse_contact_rands_inline(child)
		elif tag == "ContactDelays":
			leader_data["ContactDelays"] = parse_contact_delays_inline(child)
		elif tag == "MemoryAttitudePercents":
			leader_data["MemoryAttitudePercents"] = parse_memory_attitudes_inline(child)
		elif tag == "MemoryDecays":
			leader_data["MemoryDecays"] = parse_memory_decays_inline(child)

		# <!-- custom: only then (i.e. only after specifically to parse nested (i.e. only those in NESTED_FIELDS_TO_SPECIFICALLY_PARSE anyways etc) do we handle --> scalar fields <!-- custom: anyways etc... -->
		elif len(child) == 0:
			if tag in REFUSE_ATTITUDE_FIELDS:
				parse_refuse_attitude_thresholds(tag, text, leader, leader_data)
			elif expected == int:
				try:
					leader_data[tag] = int(text)
				except ValueError:
					errors.append(f"[TYPE ERROR] Leader {leader_type}: Expected int for <{tag}>, got '{text}'")
					leader_data[tag] = text
			elif expected == str:
				if text.isdigit():
					errors.append(f"[TYPE WARNING] Leader {leader_type}: Expected string for <{tag}>, got numeric '{text}'")
				leader_data[tag] = text

		# <!-- custom: nested fields not handled in a specific way (i.e. those not in NESTED_FIELDS_TO_SPECIFICALLY_PARSE anyways etc) --> like <Traits>, <UnitAIWeightModifiers>, etc. <!-- custom: (just parse all as a JSON-like object, we don't use these fields in the AI Personality Panel i mean anyways etc so this is fine just to have their data as well in our leaders_data to be exhaustive if i am not mistaken in doing so or want to or not or and seems accurate to me maybe rather or not or yes or and other or and not but anwyays etc -->
		# These are allowed and will be treated as list-of-dicts if present
		else:
			sub_entries = [
				{sub.tag.split("}", 1)[1]: sub.text.strip() for sub in subentry if sub.text} for subentry in child
			]
			leader_data[tag] = sub_entries

	# <!-- custom: for example <Flavors/> such as in LEADER_DEFAULTS is fine as in base advciv's xml at least as of now anyways (we'll fill it with 0 0 0 0 0 0 later as part of aprsing as we do with other subnested fields such as other missing flavor like flavor gold missing in leader alexander for example so we put iFlavorGold 0 which is fine, just extend(ing but anyways etc) this logic to all flavor sub fields missing while <Flavors/> itself exists, all fine), but if the field <Flavors/> or <Flavors> is entirely missing from the leader's XML, throw an error instead, same for all fields we parse for our leaders anyways etc if i am not mistaken is how we should do and handle it but anyways etc at least can if i am not mistaken but anyways etc, i tested this code and it successfully throws an error if <Flavors/> is removed entirely in LEADER_DEFAULTS, but/and not as we want too if <Flavors/> exists but is empty, as we want too, so reliable code to have as well as part of our safer more secure parsing if i may say at least for nested fields to specifically parse if not more or not or yes or and other or and not anyways etc -->
	for required_tag in NESTED_FIELDS_TO_SPECIFICALLY_PARSE:
		if required_tag not in seen_tags:
			raise ValueError(f"[FATAL] Missing required nested tag <{required_tag}> in leader {leader_type}. Expected at least <{required_tag}/>.")

# <!-- custom: before parsing any leader is done, make sure our normalize_to_100 shifting works as expected -->
test_expected_shifting_pre_normalize_to_100()

# <!-- custom: leader_defaults_data block as highlighted by chatgpt/becomingthrough to me so adding this info anyways -->
for leader in root.findall(".//civ4:LeaderHeadInfo", ns):
	type_tag = leader.find("civ4:Type", ns)
	if type_tag is None or type_tag.text != "LEADER_DEFAULTS":
		continue
	
	leader_type = type_tag.text
	seen_tags_leader_defaults = set()

	parse_leader(leader, leader_type, leader_defaults_data, seen_tags_leader_defaults)

if "LEADER_DEFAULTS" in leader_defaults_data:
	raise ValueError("[INFO] Nested defaults ['LEADER_DEFAULTS']")

# <!-- custom: leader_data block as highlighted by chatgpt/becomingthrough to me so adding this info anyways -->
for leader in root.findall(".//civ4:LeaderHeadInfo", ns):
	type_tag = leader.find("civ4:Type", ns)
	if type_tag is None or not type_tag.text:
		continue

	leader_type = type_tag.text
	leader_data = {}
	seen_tags_leader = set()

	parse_leader(leader, leader_type, leader_data, seen_tags_leader)
	inject_defaults(leader_defaults_data, leader_data)

	# Save leader
	leaders_data[leader_type] = leader_data

# === After parsing all leaders ===
# --- Create a list of valid leaders (exclude dummy leaders for aggregated attributes) ---
VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES = [
    k for k in leaders_data
    if k not in EXCLUDED_LEADERS_FROM_ATTRIBUTES_AGGREGATION
]

if (IS_INSPECT_DEBUG_LEADER):
	print("1 - Before any force_complete functions: Leader %s's leaders_data: %s" % (LEADER_TO_INSPECT_IN_DEBUG_OUTPUT, str(leaders_data[LEADER_TO_INSPECT_IN_DEBUG_OUTPUT])))
print("DEBUG DEFAULT MemoryDecays:", leader_defaults_data.get("MemoryDecays"))
print("DEBUG Catherine MemoryDecays:", leaders_data["LEADER_CATHERINE"]["MemoryDecays"])
# After parsing all leaders and injecting defaults
# --- Ensure nested defaults are complete only now ---
print("DEFAULTS FINAL at step 1:", leader_defaults_data)
ensure_complete_nowar_attitudes(leaders_data, leader_defaults_data)
ensure_complete_flavors(leaders_data)
force_complete_contact_delays(leaders_data, leader_defaults_data)
force_complete_contact_rands(leaders_data, leader_defaults_data)
force_complete_memory_decays(leaders_data, leader_defaults_data)
force_complete_memory_attitudes(leaders_data, leader_defaults_data)

if (IS_INSPECT_DEBUG_LEADER):
	print("2 - Before any flatten_all functions: Leader %s's leaders_data: %s" % (LEADER_TO_INSPECT_IN_DEBUG_OUTPUT, str(leaders_data[LEADER_TO_INSPECT_IN_DEBUG_OUTPUT])))
# --- Now flatten all contacts nicely <!-- custom: then prune list too anwyays etc --> ---
flatten_all_contacts(leaders_data)
# --- Add Positive Memory Affection aggregate ---
flatten_all_memories(leaders_data, is_positive=True, is_affection=True)   # Affection from positive memories
flatten_all_memories(leaders_data, is_positive=True, is_affection=False)  # Resentment from positive memories
flatten_all_memories(leaders_data, is_positive=False, is_affection=True)  # Affection from negative memories (rare?)
flatten_all_memories(leaders_data, is_positive=False, is_affection=False) # Resentment from negative memories

# === Final Cleanup ===

if (IS_INSPECT_DEBUG_LEADER):
	print("3 - Before any prune_nested functions: Leader %s's leaders_data: %s" % (LEADER_TO_INSPECT_IN_DEBUG_OUTPUT, str(leaders_data[LEADER_TO_INSPECT_IN_DEBUG_OUTPUT])))
prune_nested_nowarattitudesprobs_if_flattened(leaders_data)
prune_nested_flavors_if_flattened(leaders_data)
prune_nested_contact_lists_if_flattened(leaders_data)
# <!-- custom: positive memories are shared between affections and resentments, so prune only once positive memories for both positive memories affections and positive memories resentments.
# Same and similar reasoning for negative memories -->
prune_nested_memory_lists_if_flattened(leaders_data, is_positive=True)
prune_nested_memory_lists_if_flattened(leaders_data, is_positive=False)

# <!-- custom: safer to do the cleanup only after all parsing is done if i am not mistaken, to make sure data is not used in other places before that if i'm not mistaken and based on my understanding of chatgpt's answer and response and suggestion to me etc anyways -->
# --- Cleanup remaining unused legacy fields if not already done ---
if (IS_INSPECT_DEBUG_LEADER):
	print("4 - Before any remove_intermediate functions: Leader %s's leaders_data: %s" % (LEADER_TO_INSPECT_IN_DEBUG_OUTPUT, str(leaders_data[LEADER_TO_INSPECT_IN_DEBUG_OUTPUT])))
remove_intermediate_contact_fields(leaders_data)
remove_intermediate_memory_fields(leaders_data)

def check_errors_and_tests():
	if errors:
		print("[VALIDATION ERRORS FOUND]")
		for e in errors:
			print(e)
		raise SystemExit("[EXIT] Leader data validation failed.")

	if not leaders_data:
		raise ValueError("[FATAL ERROR] Parsed 0 leaders. Check XML structure or namespace.")

	# --- Test parsed output against expected sample ---

	expected_sample = get_expected_output_PARSED_XML_LEADERS_DATA_SAMPLE()
	sample_leaders = [
		# <!-- custom: even if barbarian (same for defaults anyways etc) is not a real leader, its data is useful to make sure we didn't do parsing mistakes or such or to cover more edge cases like <NoWarAttitudeProbs/> or <Flavors/> for example or other unexpected or missing or other or and not value(s) anyways etc anyways etc anyways etc... -->
		"LEADER_BARBARIAN",
		"LEADER_DEFAULTS",
		# <!-- custom: then the rest of the batch/crew or and other i must say or and not or and other or and not but anyways etc... still the staff is here actually i said it now even though is not professional team but anyways etc... -->
		"LEADER_ALEXANDER",
		"LEADER_CATHERINE",
		"LEADER_GANDHI",
	]

	parsed_sample = {k: v for k, v in leaders_data.items() if k in sample_leaders}

	def compare_leaders(expected, actual):
		grouped_mismatches = {}  # leader -> list of mismatches

		for leader, expected_data in expected.items():
			actual_data = actual.get(leader)
			if actual_data is None:
				grouped_mismatches.setdefault(leader, []).append(
					f"[{leader}] Leader is missing in parsed data."
				)
				continue

			# Check for field mismatches
			for key, expected_value in expected_data.items():
				actual_value = actual_data.get(key, "<MISSING>")
				if actual_value != expected_value:
					grouped_mismatches.setdefault(leader, []).append(
						f"Field '{key}' mismatch: expected '{expected_value}', got '{actual_value}'"
					)

			# Check for unexpected extra fields
			for key in actual_data.keys():
				if key not in expected_data:
					grouped_mismatches.setdefault(leader, []).append(
						f"Unexpected extra field '{key}' present in parsed data (value: '{actual_data[key]}')"
					)

		return grouped_mismatches

	grouped_mismatches = compare_leaders(expected_sample, parsed_sample)

	if grouped_mismatches:
		print("[TEST FAILED] Parsed sample does not match expected!")

		for leader, problems in grouped_mismatches.items():
			print(f"\n--- Mismatches for {leader} ---")
			for issue in problems:
				print(f"- {issue}")

		raise SystemExit("[EXIT] Leader sample test failed. File not written.")
	else:
		print("[TEST PASSED] Parsed sample matches expected sample!")

# <!-- custom: tip: comment-out function(s) below (currently only check_errors_and_tests) that check errors and test(s) to get output file (faster(/easier too anyways)) and (then) more quickly (based on that/it anyways) update (your/the etc anyways) expected output (making sure none is inaccurate, but with that caveat in mindis faster and for convenience, anwyays)) ;
# 
# but be very careful following that advice!! You can (at least i did) very easily miss mismatched values, so use it as easy copy paste rather than skip meticulous verify, rest is up to you though in all cases, at least i warned maybe, hopefulyl helps though as information not warn strictly or yes or etc but anyways
# -->
check_errors_and_tests()

# --- Output to file ---
def output_to_file():
	output_path = f"leaders_data_{timestamp}.py"
	with open(output_path, "w", encoding="utf-8") as f:
		f.write(f"{copyright_header}\n\n")
		f.write(text_art.format(timestamp=timestamp))
		f.write("\n\nPARSED_XML_LEADERS_DATA = ")
		f.write(json.dumps(leaders_data, indent=4, ensure_ascii=False))
	print(f"[SUCCESS] Leader data written to: {output_path}")
	print(f"[LOGGING COMPLETE] Log file saved in: {log_path}")

output_to_file()

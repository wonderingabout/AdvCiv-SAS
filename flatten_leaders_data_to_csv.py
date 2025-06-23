# --- Convert leaders_data (parsed XML) into a structured CSV and Markdown legend ---
# This script is part of the AdvCiv-SAS mod project.
# (c) 2025 wonderingabout & becomingthrough
#
# This script flattens and formats all leader AI configuration data from the `PARSED_XML_LEADERS_DATA`
# Python dictionary into a clean CSV table for spreadsheet analysis and documentation purposes.
#
# The script does not parse the original XML directly; it requires that the `leaders_data.py` file
# (typically auto-generated from CIV4LeaderHeadInfos.xml) already exists and contains a pre-parsed
# Python structure.
#
# Output:
# - A CSV file with one row per leader (e.g. GANDHI, RAGNAR) and one column per attribute
# - A Markdown (.md) file listing abbreviation-to-field mappings for easier CSV readability
#
# Features:
# - Fully flattened leader data, including:
#   • Traits, Flavors, Attitude modifiers
#   • NoWar probabilities
#   • Contact Rand/Delay values
#   • Raw memory fields (AttitudePercent and Decay, per memory type)
#   • Aggregated memory scores (Affection/Resentment for positive/negative memory)
#   • Aggregated contact probabilities
#
# - Automatic categorization of numeric fields into:
#   • Main numeric attributes (fallback group)
#   • Victory weights (e.g. iConquestVictoryWeight)
#   • Flavors (e.g. iFlavorMilitary)
#   • Attitude modifiers (e.g. iBetterRankDifferenceAttitudeChange, iAttitudeThreshold)
#   • Contact probability fields (e.g. iContactRandOpenBorders)
#   • Raw memory reaction weights (e.g. iNegativeMemoryAttitudePercentDeclaredWar)
#   • Aggregated memory summary scores (e.g. iAggregatedPositiveMemoryAffection)
#
# - Non-numeric fields (e.g. FavoriteCivic, Traits, ImprovementWeightModifiers) are appended last
#
# Special Formatting:
# - Enums like FavoriteCivic = CIVIC_VASSALAGE are stripped to show only "VASSALAGE"
# - Trait lists (e.g. Aggressive, Philosophical) are joined as comma-separated values
# - Structured dictionaries like ImprovementWeightModifiers or UnitAIWeightModifiers are serialized as readable entries (e.g. "MINE: 30")
#
# Abbreviations:
# - Each CSV column is labeled with a short 2–4 character abbreviation (e.g. "FC" for FavoriteCivic)
# - Conflicts are resolved with suffixes (e.g. FC0, FC1, FCa...)
# - A Markdown legend maps each abbreviation to its full field name
#
# Notes:
# - Fields such as ArtDefineTag, Description, Civilopedia, and DiplomacyMusic are excluded by default
# - The CSV output is sorted alphabetically by leader name, with the "LEADER_" prefix removed
# - Fields not recognized as numeric are preserved as-is for completeness and clarity
#
# Dependencies:
# - `PARSED_XML_LEADERS_DATA` must be defined and importable from `leaders_data.py`
# - Output files include:
#     • `leaders_data_to_csv_<timestamp>.csv`
#     • `leaders_data_to_csv_legend_<timestamp>.md`

import csv
from datetime import datetime
from Assets.Python.Contrib.Sevopedia.leaders_data import PARSED_XML_LEADERS_DATA
import ast
from collections import defaultdict

# --- Step 1: Setup timestamped output ---
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"leaders_data_to_csv_{timestamp}.csv"
md_filename = f"leaders_data_to_csv_legend_{timestamp}.md"

# --- Step 2: Define excluded fields ---
EXCLUDED_FIELDS = {
	"Type",
	"Description",
	"ArtDefineTag",
	"Civilopedia",
	"DiplomacyIntroMusicPeace",
	"DiplomacyIntroMusicWar",
	"DiplomacyMusicPeace",
	"DiplomacyMusicWar",
}

# --- Step 3: Flatten nested fields ---
def flatten_leaders_data(leaders_data):
	flat_data = {}
	for key, value in leaders_data.items():
		flat_data[key] = str(value) if isinstance(value, (dict, list)) else value
	return flat_data

# --- Step 4.1: Collect relevant fields ---
all_columns = set()
flattened_leader_data = {}

for leader_id, leader_data in PARSED_XML_LEADERS_DATA.items():
	flat = flatten_leaders_data(leader_data)
	flattened_leader_data[leader_id] = flat
	for key in flat:
		if key not in EXCLUDED_FIELDS:
			all_columns.add(key)

# Separate numeric vs non-numeric fields
numeric_fields = []
non_numeric_fields = []

for field in sorted(all_columns):
	for flat in flattened_leader_data.values():
		val = flat.get(field, "")
		if val == "":
			continue
		try:
			float(val)
			numeric_fields.append(field)
			break
		except (ValueError, TypeError):
			non_numeric_fields.append(field)
			break

numeric_fields = list(dict.fromkeys(numeric_fields))
non_numeric_fields = list(dict.fromkeys(non_numeric_fields))

# --- Step 4.2: Custom column order ---
leader_column = ["Leader"]
numerical_generic = []
numerical_remaining_if_any = []
numerical_victory_weight = []
numerical_flavor = []
numerical_attitude_change = []
numerical_attitude_divisor = []
numerical_attitude_change_limit = []
numerical_attitude_threshold = []
numerical_no_war_attitude_prob = []
numerical_contact_rand_raw = []
numerical_contact_delay_raw = []
# <!-- custom: since we display same raw attitude percent and decay fields values in UI regardless of positive/negative memory affection/resentment (raw aggregated values then the normalized aggregated values are is displayed anyways etc) aggregation, no need to store multiple versions (i.e. positive/negative and affection/resentment) of these raw attitude percent and decay fields, store only one kind for all of these 4 possible combination cases (positive-affection, positive-resentment, negative-affection, negative-resentment anyways etc) same as in XML fields structuration too for raw attitude percents and decays anyways etc anyways etc anyways etc, i.e. for example only for example imemoryAttitudePercentDeclaredWar (no positive-negative, no affection-resentment) for raw attitude_percent and decay fields same as in XML anyways etc -->
numerical_memory_attitude_percent_raw = []
numerical_memory_decay_raw = []
numerical_aggregated_contact_prob = []
numerical_aggregated_positive_memory_affection = []
numerical_aggregated_positive_memory_resentment = []
numerical_aggregated_negative_memory_affection = []
numerical_aggregated_negative_memory_resentment = []
non_numeric = []

for field in numeric_fields:
	# <!-- custom: some fields such as "MaxWarRand" in leaders_data.py are parsed (in generate_leaders_data.py anyways etc) with a "get" prefix (for example "getMaxWarRand") instead of an "i" (not "iMaxWarRand" like the XML but as said before is "getMaxWarRand" anyways etc) prefix in leaders_data.py for consistency with the not interacting with but using same key names independently anyways etc sevopedia leader AI personality panel code but or not but or yes but but anyways etc anyways etc anyways etc), see generate_leaders_data.py generic and attitude threshold for example (at least as of now these are the only fields we parse with a "get" prefix anyways etc) field parsing code or/and code comments for details anyways etc ; here we want to display attitude thresholds in columns one next to the other too/as well i mean so separate them from generic getter fields anyways etc) -->
	if field.startswith("get") and (not field.endswith("AttitudeThreshold")):
		numerical_generic.append(field)
	elif field.startswith("iFlavor"):
		numerical_flavor.append(field)
	elif field.startswith("iNoWarAttitudeProb"):
		numerical_no_war_attitude_prob.append(field)		
	elif field.startswith("iContactRand"):
		numerical_contact_rand_raw.append(field)
	elif field.startswith("iContactDelay"):
		numerical_contact_delay_raw.append(field)
	elif field.startswith("iMemoryAttitudePercent"):
		numerical_memory_attitude_percent_raw.append(field)
	elif field.startswith("iMemoryDecay"):
		numerical_memory_decay_raw.append(field)
	elif field.startswith("iAggregatedContactProb"):
		numerical_aggregated_contact_prob.append(field)
	elif field.startswith("iAggregatedPositiveMemory"):
		if field.endswith("Affection"):
			numerical_aggregated_positive_memory_affection.append(field)
		elif field.endswith("Resentment"):
			numerical_aggregated_positive_memory_resentment.append(field)
		else:
			raise KeyError(f"[KEY ERROR] Unknown or missing aggregated positive memory suffix, or/and unknown positive memory field format in field={field}, please update your XML field formats or this code to accomodate them.")
	elif field.startswith("iAggregatedNegativeMemory"):
		if field.endswith("Affection"):
			numerical_aggregated_negative_memory_affection.append(field)
		elif field.endswith("Resentment"):
			numerical_aggregated_negative_memory_resentment.append(field)
		else:
			raise KeyError(f"[KEY ERROR] Unknown or missing aggregated negative memory suffix, or/and unknown negative memory field format in field={field}, please update your XML field formats or this code to accomodate them.")
	# <!-- custom: if i am not mistaken we should indeed first filter by startswith then only among remaining results filter by ends with to avoid overlap as chatgpt/becomingthrough did indeed and is should be as this if i am not mistaken indeed after consideration/reflection or not or etc or yes in this case but anyways etc -->
	elif field.endswith("AttitudeChange"):
		numerical_attitude_change.append(field)
	elif field.endswith("AttitudeDivisor"):
		numerical_attitude_divisor.append(field)
	elif field.endswith("AttitudeChangeLimit"):
		numerical_attitude_change_limit.append(field)
	elif field.endswith("AttitudeThreshold"):
		numerical_attitude_threshold.append(field)
	elif field.endswith("VictoryWeight"):
		numerical_victory_weight.append(field)
	else:
		numerical_remaining_if_any.append(field)

for field in all_columns:
	if field not in leader_column + numeric_fields:
		non_numeric.append(field)

# <!-- custom: here is where we actually order the columns if i am not mistaken anyways etc -->
columns = (
	leader_column +
	numerical_generic +
	numerical_remaining_if_any +
	numerical_victory_weight +
	numerical_flavor +
	numerical_attitude_change +
	numerical_attitude_divisor +
	numerical_attitude_change_limit +
	numerical_attitude_threshold +
	numerical_no_war_attitude_prob +
	numerical_contact_rand_raw +
	numerical_contact_delay_raw +
	numerical_aggregated_contact_prob +
	numerical_memory_attitude_percent_raw +
	numerical_memory_decay_raw +
	numerical_aggregated_positive_memory_affection +
	numerical_aggregated_positive_memory_resentment +
	numerical_aggregated_negative_memory_affection +
	numerical_aggregated_negative_memory_resentment +
	non_numeric
)

# --- <!-- custom: Step 4.3: anyways etc --> Abbreviate headers ---
abbrev_map = {"Leader": "Leader"}
abbrev_count = defaultdict(int)
abbrev_usage = defaultdict(list)

# Step 4.3.1: Collect how many fields want to use each base abbreviation
def make_abbreviation(field):
	# Strip 'i' prefix for consistency (e.g., iFavoriteCivic → FavoriteCivic)
	base = field[1:] if field.startswith("i") else field
	# Abbreviation = all uppercase letters (e.g., FavoriteCivic → FC)
	return ''.join(c for c in base if c.isupper())

for field in columns:
	if field == "Leader":
		continue
	if field in numeric_fields:
		base_abbr = make_abbreviation(field)
		abbrev_usage[base_abbr].append(field)
	else:
		# Non-numeric fields are not abbreviated
		abbrev_map[field] = field

# Step 4.3.2: Assign abbreviations with forced 0 suffix if needed
for base_abbr, fields in abbrev_usage.items():
	if len(fields) == 1:
		# No duplicates — use plain base abbreviation <!-- custom: for example FC if i am not mistaken, anyways etc -->
		abbrev_map[fields[0]] = base_abbr
	else:
		# Multiple fields — assign FC0, FC1, ..., FCa, FCb, ...
		for i, field in enumerate(fields):
			if i < 10:
				abbr = f"{base_abbr}{i}"
			else:
				# After 10, switch to letters: a = 10, b = 11, ..., z = 35
				# <!-- custom: small letter "a" also to differentiate it from an actual abbreviated capital letter "A" for example, so "FC" would be a real abbreviation of say "Favourite Civic" while "Fc" would be the 12th occurence of the "F" abbreviation for example "Freebies" (imaginary field if i may say or not or yes or and other or and not or etc anyways etc anyways etc anyways etc...) -->
				abbr = f"{base_abbr}{chr(ord('a') + (i - 10))}"
			abbrev_map[field] = abbr

# --- Step 5: Assemble cleaned, sorted rows ---
def strip_leader_prefix(leader_id):
	return leader_id.replace("LEADER_", "")

def strip_enum_prefix(value, prefix):
	if value and isinstance(value, str) and value.startswith(prefix):
		return value[len(prefix):]
	return value

rows = []
for leader_id in PARSED_XML_LEADERS_DATA:
	flat = flattened_leader_data[leader_id]
	cleaned_row = {"Leader": strip_leader_prefix(leader_id)}

	for col in columns[1:]:  # skip Leader
		val = flat.get(col, "")

		if col == "FavoriteCivic":
			val = strip_enum_prefix(val, "CIVIC_")
		elif col == "FavoriteReligion":
			val = strip_enum_prefix(val, "RELIGION_")
		elif col == "ImprovementWeightModifiers":
			try:
				mod_list = ast.literal_eval(val)
				if isinstance(mod_list, list):
					formatted = [
						f"{mod.get('ImprovementType', '').replace('IMPROVEMENT_', '')}: {mod.get('iWeightModifier', '')}"
						for mod in mod_list
						if isinstance(mod, dict)
					]
					val = ", ".join(formatted)
					
			except Exception:
				val = val  # fallback silently
		elif col == "Traits":
			try:
				trait_list = ast.literal_eval(val)
				if isinstance(trait_list, list):
					formatted = [
						trait.get('TraitType', '').replace('TRAIT_', '')
						for trait in trait_list if isinstance(trait, dict)
					]
					val = ", ".join(formatted)
			except Exception:
				val = val
		elif col == "UnitAIWeightModifiers":
			try:
				unit_ai_list = ast.literal_eval(val)
				if isinstance(unit_ai_list, list):
					formatted = [
						f"{entry.get('UnitAIType', '').replace('UNITAI_', '')}: {entry.get('iWeightModifier', '')}"
						for entry in unit_ai_list if isinstance(entry, dict)
					]
					val = ", ".join(formatted)
			except Exception:
				val = val  # fallback if needed

		cleaned_row[col] = val
		
	rows.append(cleaned_row)

# Sort alphabetically by Leader name (without prefix)
rows.sort(key=lambda r: r["Leader"])

# --- Step 6: Write CSV ---
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
	abbreviated_fields = [abbrev_map[col] for col in columns]
	writer = csv.DictWriter(f, fieldnames=abbreviated_fields)
	writer.writeheader()
	for row in rows:
		abbreviated_row = {abbrev_map[k]: v for k, v in row.items()}
		writer.writerow(abbreviated_row)

print("✔ Export complete.")
print(f"→ Output CSV saved as: {csv_filename}")

# --- Step 7: Write legend to .md file ---
with open(md_filename, "w", encoding="utf-8") as md:
	md.write("# Leader Data Abbreviations Legend\n\n")
	for abbr in sorted(abbrev_map.values()):
		# Reverse lookup
		original_field = next((k for k, v in abbrev_map.items() if v == abbr), None)
		if original_field and abbr != "Leader":
			md.write(f"- **{abbr}**: `{original_field}`\n")

print(f"→ Legend saved as: {md_filename}")

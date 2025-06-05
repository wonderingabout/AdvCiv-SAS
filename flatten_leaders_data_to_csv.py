# --- Convert/Flatten leaders_data into a readable .csv ---
# This script is part of the AdvCiv-SAS mod project.
# (c) 2025 wonderingabout & becomingthrough

import csv
from datetime import datetime
from Assets.Python.Contrib.Sevopedia.leaders_data import PARSED_XML_LEADERS_DATA

# --- Step 1: Setup timestamped output ---
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"leaders_data_to_csv_{timestamp}.csv"

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

# --- Step 4: Collect relevant fields ---
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
columns = ["Leader"] + numeric_fields + non_numeric_fields

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
				import ast
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
				import ast
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
				import ast
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
	writer = csv.DictWriter(f, fieldnames=columns)
	writer.writeheader()
	writer.writerows(rows)

print("✔ Export complete.")
print(f"→ Output CSV saved as: {csv_filename}")

# --- Convert CIV4HandicapInfo.xml to CSV and Markdown with Legends ---
#
# This script extracts and formats all game difficulty settings from CIV4HandicapInfo.xml.
# It transforms XML fields into a column-aligned CSV table and a Markdown summary,
# replacing multi-entry lists (e.g. <FreeTechs>) with unique short legend keys (e.g. FT_0),
# and writing an aligned legend block showing actual entries.
# The CSV includes a right-shifted, tabular [LEGEND] block for spreadsheet use.
# The Markdown version is GitHub-friendly and includes both tables and legend mappings.
#
# Features:
# - Enum beautification (e.g. HANDICAP_NOBLE → Noble)
# - Comma-separated list flattening for <Goodies>, <FreeTechs>, <AIFreeTechs>
# - Short key assignment (FT_, G_, AIFT_) with index
# - Consistent horizontal alignment across difficulty columns
# - Modular formatting of legends (aligned by row, not by raw string) <!-- custom: for
# the CSV version we export anyways etc -->
# - Markdown export with proper table and readable legend
#
# This script is part of the AdvCiv-SAS mod project.
# (c) 2025 wonderingabout & becomingthrough

import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import re

# --- Step 1: Setup paths ---
XML_PATH = r"Assets\XML\GameInfo\CIV4HandicapInfo.xml"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"handicap_data_to_csv_{timestamp}.csv"

# --- Step 2: Parse XML ---
tree = ET.parse(XML_PATH)
root = tree.getroot()

# --- Step 3: Collect all HandicapInfo entries ---
namespace = {'ns': root.tag.split('}')[0].strip('{')}
handicap_infos = root.find('ns:HandicapInfos', namespace)
all_fields = set()
parsed_data = {}

def beautify_enum_name(raw_name):
	"""
	Convert raw enum strings like 'TECH_THE_WHEEL', 'GOODY_LOW_GOLD',
	'HANDICAP_NOBLE' into human-readable display forms like:
	'The Wheel', 'Low Gold', 'Noble'
	"""
	# Remove known Civ4 enum prefixes
	for prefix in ('TECH_', 'GOODY_', 'HANDICAP_'):
		if raw_name.startswith(prefix):
			raw_name = raw_name[len(prefix):]
			break

	# Underscore to space, then title case
	return re.sub(r'_', ' ', raw_name).title()

def shorten_legend_name(name):
	replacements = {
		"Barbarians Weak": "Barb. Weak",
		"Barbarians Strong": "Barb. Strong",
		"Experience": "Exp.",
		#
		"Animal Husbandry": "Animal H.",
		"Bronze Working": "Bronze W.",
		"Iron Working": "Iron W.",
		"Industrialism": "Industr.",
	}
	return replacements.get(name, name)

for handicap_info in handicap_infos.findall('ns:HandicapInfo', namespace):
	handicap_dict = {}
	handicap_type = handicap_info.find('ns:Type', namespace).text

	for elem in handicap_info:
		tag = elem.tag.split('}')[-1]
		if tag in ("Type", "Description", "Help"):
			continue
		elif tag in ("Goodies", "FreeTechs", "AIFreeTechs"):
			# Serialize list fields as comma-separated strings
			entries = []
			for child in elem.findall('.//*'):
				tagname = child.tag.split('}')[-1]
				if tagname not in ("TechType", "GoodyType"):
					continue
				text = child.text.strip() if child.text else ""
				if text:
					entries.append(text)
			handicap_dict[tag] = ', '.join(entries)
		else:
			if elem.text:
				handicap_dict[tag] = elem.text.strip()

	all_fields.update(handicap_dict.keys())
	parsed_data[handicap_type] = handicap_dict

# --- Step 4: Prepare CSV rows ---
all_fields = sorted(all_fields)
difficulty_types = list(parsed_data.keys())  # Preserve order from XML parse loop

rows = []
for field in all_fields:
	row = {'Field': field}
	for difficulty in difficulty_types:
		row[difficulty] = parsed_data[difficulty].get(field, "")
	rows.append(row)

# --- Step 4.5: Move nested fields to a fixed location ---
NESTED_FIELDS = ("AIFreeTechs", "FreeTechs", "Goodies")
ANCHOR_FIELD = "iUnownedWaterTilesPerBarbarianUnit"

# Split rows into parts
before = []
nested = []
after_anchor = False

for row in rows:
	if row["Field"] in NESTED_FIELDS:
		nested.append(row)
	elif row["Field"] == ANCHOR_FIELD:
		before.append(row)
		after_anchor = True
	else:
		if after_anchor:
			before.append(row)
		else:
			before.append(row)

# Reinsert nested rows after the anchor
new_rows = []
found_anchor = False
for row in before:
	new_rows.append(row)
	if row["Field"] == ANCHOR_FIELD:
		new_rows.extend(nested)
rows = new_rows

# --- Step 5: Prepare columns ---
# Create a map of full -> short column headers
difficulty_column_map = {
	difficulty: beautify_enum_name(difficulty)
	for difficulty in parsed_data.keys()
}
columns = ['Field'] + list(difficulty_column_map.values())

# --- Step 6: Replace long values with references and collect legend ---
legend = {}
legend_counter = {}

def get_legend_key(field_name, value):
	if not value.strip():
		return ""
	short_prefix = {
		"AIFreeTechs": "AIFT_",
		"FreeTechs": "FT_",
		"Goodies": "G_"
	}.get(field_name, field_name[:3].upper() + "_")  # fallback to e.g., iAI → IAI_

	count = legend_counter.get(short_prefix, 0)
	legend_key = f"{short_prefix}{count}"
	legend_counter[short_prefix] = count + 1
	legend[legend_key] = value
	return legend_key

for row in rows:
	for difficulty in difficulty_types:
		value = row.get(difficulty, "")
		# This ensures all values (even single items) in the specified fields are always substituted with a legend key, no matter the length.
		if row["Field"] in ("Goodies", "FreeTechs", "AIFreeTechs"):
			row[difficulty] = get_legend_key(row["Field"], value)

# --- Step 7: Write CSV with right-shifted legend ---
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
	writer = csv.DictWriter(f, fieldnames=columns)
	writer.writeheader()

	for row in rows:
		shortened_row = {'Field': row['Field']}
		for full_difficulty, short_difficulty in difficulty_column_map.items():
			shortened_row[short_difficulty] = row.get(full_difficulty, "")
		writer.writerow(shortened_row)

	def format_vertical_legend_block(legend_dict):
		def extract_ordered_unique(keys_ordered, prefix):
			unique = []
			seen = set()
			for k in keys_ordered:
				if not k or k not in legend_dict:
					continue
				for v in legend_dict[k].split(','):
					name = shorten_legend_name(beautify_enum_name(v.strip()))
					if name not in seen:
						unique.append(name)
						seen.add(name)
			return unique

		def build_columns(keys_ordered, unique, prefix):
			columns, headers, counter = [], [], 0
			for k in keys_ordered:
				if k and k in legend_dict:
					headers.append(f"{prefix}{counter}")
					values = {
						shorten_legend_name(beautify_enum_name(v.strip()))
						for v in legend_dict[k].split(',')
					}
					columns.append([v if v in values else "-" for v in unique])
					counter += 1
				else:
					headers.append("-------")
					columns.append(["-"] * len(unique))
			return headers, columns

		lines = []

		# AIFT (same style as FT/G)
		aift_keys_ordered = []
		for row in rows:
			if row["Field"] == "AIFreeTechs":
				for difficulty in difficulty_types:
					ref = row.get(difficulty, "")
					aift_keys_ordered.append(ref if ref in legend_dict else None if not ref else None)

		aift_unique = extract_ordered_unique(aift_keys_ordered, "AIFT_")
		aift_headers, aift_columns = build_columns(aift_keys_ordered, aift_unique, "AIFT_")
		lines.append('\t'.join(aift_headers))
		for row in zip(*aift_columns):
			lines.append('\t'.join(row))

		# FT
		ft_keys_ordered = []
		for row in rows:
			if row["Field"] == "FreeTechs":
				for difficulty in difficulty_types:
					ref = row.get(difficulty, "")
					ft_keys_ordered.append(ref if ref in legend_dict else None if not ref else None)

		ft_unique = extract_ordered_unique(ft_keys_ordered, "FT_")
		ft_headers, ft_columns = build_columns(ft_keys_ordered, ft_unique, "FT_")
		lines.append('\t'.join(ft_headers))
		for row in zip(*ft_columns):
			lines.append('\t'.join(row))

		# G
		g_keys_ordered = []
		for row in rows:
			if row["Field"] == "Goodies":
				for difficulty in difficulty_types:
					ref = row.get(difficulty, "")
					g_keys_ordered.append(ref if ref in legend_dict else None if not ref else None)

		g_unique = extract_ordered_unique(g_keys_ordered, "G_")
		g_headers, g_columns = build_columns(g_keys_ordered, g_unique, "G_")
		lines.append('\t'.join(g_headers))
		for row in zip(*g_columns):
			lines.append('\t'.join(row))

		return lines

	f.write("\n\n")

	legend_lines = format_vertical_legend_block(legend)

	# This writes each line as a true row, with each AIFT value in its own column — and will render properly in Excel or any spreadsheet.
	legend_csv = csv.writer(f)
	f.write("\n\n")

	NUM_COLUMNS = len(columns)

	# Write a fully padded [LEGEND] header row
	# Determine where actual legend columns begin (e.g., skip the 'Field' column)
	# <!-- custom: shift the entire display of the "[LEGEND]" items's line one column to the right ( [""] ) if i am not mistaken anyways etc -->
	legend_header_row = [""] + ["[LEGEND]"] * (NUM_COLUMNS - 1)
	legend_csv.writerow(legend_header_row)

	# Write padded legend rows
	for line in legend_lines:
		# Shift all contents one column to the right (like the LEGEND header)
		parts = [""] + line.split("\t")

		# Pad to exactly NUM_COLUMNS columns
		parts += [""] * (NUM_COLUMNS - len(parts))

		legend_csv.writerow(parts)

print("✔ Export complete with legend references.")
print(f"→ Output CSV saved as: {csv_filename}")

# --- Step 8: Write Markdown table ---
md_filename = f"handicap_data_to_md_{timestamp}.md"
with open(md_filename, "w", encoding="utf-8") as md:
	# Header
	md.write("| Field | " + " | ".join(columns[1:]) + " |\n")
	md.write("|" + "------|" * len(columns) + "\n")

	# Rows
	for row in rows:
		md_row = [row["Field"]]
		for full_difficulty, short_difficulty in difficulty_column_map.items():
			md_row.append(row.get(full_difficulty, ""))
		md.write("| " + " | ".join(md_row) + " |\n")

	# Legend header
	md.write("\n\n## Legend\n\n")
	md.write("| Key | Full Value |\n")
	md.write("|-----|-------------|\n")
	for key, value in legend.items():
		md.write(f"| {key} | {value} |\n")

print("✔ Markdown export complete.")
print(f"→ Output Markdown saved as: {md_filename}")

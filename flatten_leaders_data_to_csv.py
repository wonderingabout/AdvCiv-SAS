# --- <!-- custom: Convert/Flatten leaders_data into a readable .csv (seems to be directly viewable on github too very nice (but better not spam the header xd or/and hehe if i may say or not or yes or/and other or not anwyays etc)) --> ---
# This script is part of the AdvCiv-SAS mod project.
# (c) 2025 wonderingabout & becomingthrough

import os
import csv
import importlib.util
import re
from datetime import datetime
from Assets.Python.Contrib.Sevopedia.leaders_data import PARSED_XML_LEADERS_DATA

# <!-- custom: Step 1: Record start time for filename output naming (add timestamp at end of it like for our other output data files from our py scripts (or/and other types of scripts if there were such or not such or not or yes or/and other or not anyways etc) -->
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# --- Step 2: Flatten nested fields ---
def flatten_leaders_data(leaders_data):
	flat_data = {}
	for key, value in leaders_data.items():
		flat_data[key] = str(value) if isinstance(value, (dict, list)) else value
	return flat_data

# --- Step 3: Collect all columns ---
all_columns = set()
for leader_data in PARSED_XML_LEADERS_DATA.values():
	all_columns.update(flatten_leaders_data(leader_data).keys())

# Ensure consistent order
all_columns.discard("Leader")
columns = ["Leader"] + sorted(all_columns)

# --- Step 4: Assemble rows ---
rows = []
for leader_id, data in PARSED_XML_LEADERS_DATA.items():
	row = flatten_leaders_data(data)
	row["Leader"] = leader_id
	for col in columns:
		row.setdefault(col, "")
	rows.append(row)

# --- Step 6: Write to CSV ---
csv_filename = f"leaders_data_to_csv_ai_flat_{timestamp}.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
	writer = csv.DictWriter(f, fieldnames=columns)
	writer.writeheader()
	writer.writerows(rows)

print("✔ Export complete.")
print(f"→ Output CSV saved as: {csv_filename}")

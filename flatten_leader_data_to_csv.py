# flatten_leader_data_to_csv.py

#todo add header 

import os
import csv
import importlib.util
import re

# --- Step 1: Find latest leaders_data_*.py ---
data_prefix = "leaders_data_"
data_files = [f for f in os.listdir(".") if f.startswith(data_prefix) and f.endswith(".py")]

if not data_files:
	raise FileNotFoundError("No leaders_data_*.py file found in this folder.")

# Sort by timestamp in filename (assumes format: leaders_data_YYYYMMDD_HHMMSS...)
def extract_timestamp(name):
	match = re.search(r"(\d{8}_\d{6})", name)
	return match.group(1) if match else ""

latest_file = sorted(data_files, key=extract_timestamp, reverse=True)[0]
module_name = latest_file[:-3]  # Strip .py

# --- Step 2: Import the selected module dynamically ---
spec = importlib.util.spec_from_file_location(module_name, os.path.abspath(latest_file))
leaders_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(leaders_module)

if not hasattr(leaders_module, "PARSED_XML_LEADERS_VALUES"):
	raise AttributeError(f"{latest_file} does not define PARSED_XML_LEADERS_VALUES")

leader_data_dict = leaders_module.PARSED_XML_LEADERS_VALUES

# --- Step 3: Flatten nested fields ---
def flatten_leader_data(leader_data):
	flat_data = {}
	for key, value in leader_data.items():
		flat_data[key] = str(value) if isinstance(value, (dict, list)) else value
	return flat_data

# --- Step 4: Collect all columns ---
all_columns = set()
for leader_dict in leader_data_dict.values():
	all_columns.update(flatten_leader_data(leader_dict).keys())

# Ensure consistent order
all_columns.discard("Leader")
columns = ["Leader"] + sorted(all_columns)

# --- Step 5: Assemble rows ---
rows = []
for leader_id, data in leader_data_dict.items():
	row = flatten_leader_data(data)
	row["Leader"] = leader_id
	for col in columns:
		row.setdefault(col, "")
	rows.append(row)

# --- Step 6: Write to CSV ---
csv_filename = "advCiv_leader_ai_flat.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
	writer = csv.DictWriter(f, fieldnames=columns)
	writer.writeheader()
	writer.writerows(rows)

print("✔ Export complete.")
print(f"→ Latest input module: {latest_file}")
print(f"→ Output CSV saved as: {csv_filename}")

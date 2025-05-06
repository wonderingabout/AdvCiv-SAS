# --- AI Utilities for normalization and general helpers ---
# Created as part of AdvCiv-SAS improvements
# (c) 2025 wonderingabout & becomingthrough

# --- Attribute normalization ---
def normalize_to_100(value, min_val, max_val, invert, attr_name=""):
	"""
	Normalizes an AI attribute value to a 0–100 integer scale.

	- First checks if min_val > max_val or if value outside [min_val, max_val].
	- If min_val == max_val, issues a warning and returns 0.
	- Adjusts for non-zero minimums:
	  - If min_val < 0, shifts range upwards.
	  - If min_val > 0, shifts range downwards.
	- Normalizes adjusted_value / adjusted_max.
	- Optionally inverts the normalized value.
	- Converts final normalized value to 0–100 integer.

	Warnings:
	- Uniform min==max -> All normalized scores will be 0.
	- Adjusted value negative -> Warns but proceeds.
	- Normalized value out of bounds -> Warns but proceeds.

	Parameters:
	- value (int): Raw XML attribute value.
	- min_val (int): Minimum observed attribute value.
	- max_val (int): Maximum observed attribute value.
	- invert (bool): Whether to invert normalized scale.
	- attr_name (str, optional): Attribute name for debug warnings.

	Returns:
	- final_score (int): Normalized integer 0–100.
	"""
	# --- Pre-checks ---
	if min_val > max_val:
		raise ValueError("Invalid min/max for attribute '%s': min_val=%d > max_val=%d" % (attr_name, min_val, max_val))

	if value < min_val or value > max_val:
		raise ValueError("Value out of range for attribute '%s': value=%d not in [%d, %d]" % (attr_name, value, min_val, max_val))

	if min_val == max_val:
		print("[WARNING] Attribute %s has an identical min and max value (%d). All normalized values will be 50." % (attr_name, min_val))
		return 50

	# --- Shift value for range normalization ---
	original_min = min_val
	if min_val < 0:
		adjusted_value = value + abs(min_val)
		adjusted_max = max_val + abs(min_val)
	elif min_val > 0:
		adjusted_value = value - min_val
		adjusted_max = max_val - min_val
	else:
		adjusted_value = value
		adjusted_max = max_val

	# --- Normalize ---
	if adjusted_value < 0:
		raise ValueError("Adjusted value of %s is negative before normalization: adjusted_value=%d, original_min=%d, max_val=%d" % (attr_name, adjusted_value, original_min, max_val))

	norm = float(adjusted_value) / float(adjusted_max)

	final_score = int(round(norm * 100))
	if (final_score < 0) or (final_score > 100):
		raise ValueError("Norm of %s out of range (0–1) during normalization: norm=%.3f, adjusted_value=%d, adjusted_max=%d" % (attr_name, final_score, adjusted_value, adjusted_max))

	if invert:
		final_score = 100 - final_score

	return final_score

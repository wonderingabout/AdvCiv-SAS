# --- AI Utilities for normalization and general helpers ---
# Created as part of AdvCiv-SAS improvements
# (c) 2025 wonderingabout & becomingthrough

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
def normalize_to_100(value, min_val, max_val, invert, attr_name=""):
	"""
	Normalizes an AI attribute value to a 0–100 integer scale.

	- First checks if min_val > max_val or if value outside [min_val, max_val].
	- If min_val == max_val, issues a warning and returns 50.
	- Shifts for non-zero minimums:
	  - If min_val < 0, shifts range upwards.
	  - If min_val > 0, shifts range downwards.
	- Normalizes shifted_value / shifted_max.
	- Optionally inverts the normalized value.
	- Converts final normalized value to 0–100 integer.

	Warnings:
	- Uniform min==max -> All normalized scores will be 50.

	Errors:
	- min_val higher value than max_val -> Raises an error.
	- value out of bounds -> Raises an error.
	- Shifted min not equal to 0 -> Raises an error.
	- Shifted value negative -> Raises an error.
	- Normalized value out of bounds -> Raises an error.

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

	# --- Shift min_val, value, and max_val, if needed, before we normalize ---
	shifted_value = None
	shifted_min, shifted_value, shifted_max = get_shifted_values(min_val, value, max_val)

	if (shifted_value is None):
		raise ValueError("[FATAL] In attr_name=%s, shifted_value=%s has not been initialized properly and is still None: shifted_min=%d, shifted_value=%d, shifted_max=%d, min_val=%d, value=%d, max_val=%d" % (attr_name, shifted_min, shifted_value, shifted_max, min_val, value, max_val))

	# --- Normalize ---
	if shifted_min != 0:
		raise ValueError("[FATAL] For attr_name=%s, distribution has not shifted to a shifted_min of 0 before normalization: shifted_min=%d, shifted_value=%d, shifted_max=%d, min_val=%d, value=%d, max_val=%d" % (attr_name, shifted_min, shifted_value, shifted_max, min_val, value, max_val))
	if shifted_value < 0:
		raise ValueError("[FATAL] For attr_name=%s, shifted_value cannot be negative (as shifted_min should always be 0) before normalization: shifted_min=%d, shifted_value=%d, shifted_max=%d, min_val=%d, value=%d, max_val=%d" % (attr_name, shifted_min, shifted_value, shifted_max, min_val, value, max_val))

	norm = float(shifted_value) / float(shifted_max)

	final_score = int(round(norm * 100))
	if (final_score < 0) or (final_score > 100):
		raise ValueError("Norm of %s out of range (0-100) during normalization: final_score=%.3f, shifted_min=%d, shifted_max=%d, min_val=%d, max_val=%d" % (attr_name, final_score, shifted_min, shifted_max, min_val, max_val))

	if invert:
		final_score = 100 - final_score

	return final_score
	
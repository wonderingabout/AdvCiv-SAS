# --- Test script to test crazy values for fun for normalize_to_100 ---
# (c) 2025 wonderingabout & becomingthrough

from Assets.Python.Contrib.Sevopedia.ai_utils_shared_with_civ4 import normalize_to_100

B_WARN = True

def progress_bar(score, width=10):
	# Returns a simple ASCII progress bar for a score (0–100).
	#
	# Parameters:
	# - score (int): Normalized score between 0 and 100.
	# - width (int, optional): Width of the bar (default: 10 units).
	#
	# Returns:
	# - bar (str): ASCII string representing the progress bar.

	filled_units = int(round((score / 100.0) * width))
	return ("|" + ("█" * filled_units) + ("-" * (width - filled_units)) + "| %d%%" % score)

def run_tests():
	print("--- Running crazy normalization tests ---")
	test_cases = [
		("Perfect Tie", 3000, 3000, 3000, False),
		("Inverted Negative", -5, -10, 0, True),
		("Corrupted Max < Min", 5, 10, 5, False),
		("Already Good Range", 30, 20, 50, False),
		("Zero Centered", 0, -5, 5, False),
		("Huge Range", 10000, 0, 100000, False),
		("Negative after shift", -2, 1, 3, False),
		("Perfect Max", 50, 0, 50, False),
	]

	for name, value, min_val, max_val, invert in test_cases:
		try:
			final_score = normalize_to_100(value, min_val, max_val, B_WARN, invert, attr_name=name)
			print("[PASS] %s: value=%d, min=%d, max=%d, invert=%s -> score=%d" % (name, value, min_val, max_val, invert, final_score))
			print(progress_bar(final_score))
		except Exception as e:
			print("[FAIL] %s: value=%d, min=%d, max=%d, invert=%s -> ERROR: %s" % (name, value, min_val, max_val, invert, str(e)))

	print("--- Done! ---")

# if __name__ == "__main__":
# run_tests()
run_tests()

# Example of expected output:
#
# --- Running crazy normalization tests ---
# [PASS] Perfect Tie: value=3000, min=3000, max=3000, invert=False -> score=0
# |----------| 0%
#
# [PASS] Inverted Negative: value=-5, min=-10, max=0, invert=True -> score=50
# |█████-----| 50%
#
# [FAIL] Corrupted Max < Min: value=5, min=10, max=5, invert=False -> ERROR: Invalid min/max for attribute 'Corrupted Max < Min': min_val=10 > max_val=5
# [PASS] Already Good Range: value=30, min=20, max=50, invert=False -> score=33
# |███-------| 33%
#
# [PASS] Zero Centered: value=0, min=-5, max=5, invert=False -> score=50
# |█████-----| 50%
#
# [PASS] Huge Range: value=10000, min=0, max=100000, invert=False -> score=10
# |█---------| 10%
#
# [FAIL] Negative after shift: value=-2, min=1, max=3, invert=False -> ERROR: Value out of range for attribute 'Negative after shift': value=-2 not in [1, 3]
# [PASS] Perfect Max: value=50, min=0, max=50, invert=False -> score=100
# |██████████| 100%
# --- Done! ---

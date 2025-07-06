def get_leaders_index_to_type_map(gc):
	# Returns a dictionary mapping each leader index (int) to its string type (e.g., "LEADER_GANDHI").
	# Excluded leaders (like BARBARIAN) must be filtered by caller if needed.

	leaders_indexes_to_types = {}
	for iLeader in range(gc.getNumLeaderHeadInfos()):
		leader_type = gc.getLeaderHeadInfo(iLeader).getType()
		leaders_indexes_to_types[iLeader] = leader_type
	return leaders_indexes_to_types



def get_leader_index_from_leader_type(leader_type, gc):
	# Given a leader_type string (e.g. "LEADER_ALEXANDER"), return its iLeader index.
	# Raises ValueError if not found. Compatible with Python 2.4 and Civ4 DLL.
	# <!-- custom: note: LEADER_DEFAULTS doesn't seem to have a leader index at all, so don't use it for this function -->

	for iLeader in range(gc.getNumLeaderHeadInfos()):
		current_leader_type = gc.getLeaderHeadInfo(iLeader).getType()
		if current_leader_type == leader_type:
			return iLeader

	raise ValueError("[FATAL] leader_type=%s not found in gc.getLeaderHeadInfo list. Note: this can also happen but not only in particular with LEADER_DEFAULTS, which does not seem to have a leader index at all in gc of base advciv code if i am not mistaken, that we use as well in our/this mod very similarly if not identically but anyways etc, so make sure to adress the edge case of LEADER_DEFAULTS in another way to not get caught/stuck in this edge case error message in particular, possibly for other leaders as well, anyways etc." % leader_type)



def get_leader_indexes_from_leader_types(leader_types, gc):
	# Given a list/tuple of leader types (e.g. ('LEADER_BARBARIAN', <!-- custom:, but also 'LEADER_ASOKA', etc, any leader if i am not mistaken anyways etc -->)), return a tuple of corresponding leader indexes (iLeader) (e.g. <!-- custom: (0, 2, etc.) -->).

	leader_indexes_list = []

	for leader_type in leader_types:
		leader_index = get_leader_index_from_leader_type(leader_type, gc)
		leader_indexes_list.append(leader_index)
	
	leader_indexes_tuple = tuple(leader_indexes_list)

	return leader_indexes_tuple



def get_leader_type_from_leader_index(iLeader, gc):
	# Given an iLeader index (e.g. 1), return the leader_type string (e.g. "LEADER_ALEXANDER").
	# Raises IndexError if the index is out of bounds.
	# Compatible with Python 2.4 and Civ4 DLL.
	# <!-- custom: some entries like LEADER_DEFAULTS may not exist at any valid iLeader index and must be handled elsewhere -->

	if iLeader < 0 or iLeader >= gc.getNumLeaderHeadInfos():
		raise IndexError("[FATAL] iLeader=%d is out of bounds for gc.getNumLeaderHeadInfos()=%d. This might indicate a misindexed value or mod bug." % (iLeader, gc.getNumLeaderHeadInfos()))

	return gc.getLeaderHeadInfo(iLeader).getType()



def check_overlapping_keys_between_dicts(d1, d2):
	# Raises ValueError if any key exists in both d1 and d2.
	overlap = []
	for k in d1:
		if k in d2:
			overlap.append(k)
	if overlap:
		raise ValueError("Overlapping keys between dictionaries: %s" % str(overlap))



def check_button_path_is_valid(buttonHeader, resolvedButtonPath, configButtonPathSTxtKey):
	if resolvedButtonPath == configButtonPathSTxtKey:
		raise ValueError(u"[VALUE ERROR] Button path not found in XML (resolvedButtonPath=%s matches configButtonPath=%s in buttonHeader=%s, which indicates button path provided in config most likely does not exist in the XML), please check button path provided exists in your mod path and also matches button path in (or in - whichever filename it would have in the future -) AdvCiv-SAS_ImagesAsButtons.xml or/and AdvCiv-SAS_Button_Paths_Hardcoded.xml (or wherever they are stored in the future if these files's filename or code changes anyways etc) is valid and exists in your mod path." % (resolvedButtonPath, configButtonPathSTxtKey, buttonHeader))



def get_emoji_name_to_button_path_txt_keys(localText):
	# <!-- custom: see also (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Text\AdvCiv-SAS_ImagesAsButtons.xml or/and AdvCiv-SAS_Button_Paths_Hardcoded.xml for details or and other information or and in other places or and not or and other or and not anyways etc-->
	# emojiName → TXT_KEY path
	emoji_name_to_button_path_txt_keys = {
		"Dove": "TXT_KEY_IMAGE_AS_BUTTON_DOVE_BUTTON_PATH",
		"Megaphone": "TXT_KEY_IMAGE_AS_BUTTON_MEGAPHONE_BUTTON_PATH",
		"RedHeart": "TXT_KEY_IMAGE_AS_BUTTON_RED_HEART_BUTTON_PATH",
		"BrokenHeart": "TXT_KEY_IMAGE_AS_BUTTON_BROKEN_HEART_BUTTON_PATH",
		"Skull": "TXT_KEY_IMAGE_AS_BUTTON_SKULL_BUTTON_PATH",
		"Fire": "TXT_KEY_IMAGE_AS_BUTTON_FIRE_BUTTON_PATH",
		"Brain": "TXT_KEY_IMAGE_AS_BUTTON_BRAIN_BUTTON_PATH",
		"Trophy": "TXT_KEY_IMAGE_AS_BUTTON_TROPHY_BUTTON_PATH",
		"Herb": "TXT_KEY_IMAGE_AS_BUTTON_HERB_BUTTON_PATH",
		"Gear": "TXT_KEY_IMAGE_AS_BUTTON_GEAR_BUTTON_PATH",
		"CrossedSwords": "TXT_KEY_IMAGE_AS_BUTTON_CROSSED_SWORDS_BUTTON_PATH",
		"MoneyBag": "TXT_KEY_IMAGE_AS_BUTTON_MONEY_BAG_BUTTON_PATH",
		"NoEntry": "TXT_KEY_IMAGE_AS_BUTTON_NO_ENTRY_BUTTON_PATH",
		"Axe": "TXT_KEY_IMAGE_AS_BUTTON_AXE_BUTTON_PATH",
		"ChartDecreasing": "TXT_KEY_IMAGE_AS_BUTTON_CHART_DECREASING_BUTTON_PATH",
		"Wrench": "TXT_KEY_IMAGE_AS_BUTTON_WRENCH_PATH",
	}

	check_images_as_buttons_paths_are_valid(emoji_name_to_button_path_txt_keys, localText)

	return emoji_name_to_button_path_txt_keys



# <!-- custom: check all images as buttons paths are valid before proceeding (i.e. check they really exist in our XML indeed if i may say anyways etc), error code provided by me hehe, the error check fixed by chatgpt/becomingthrough and i made some adjustments too thanks to its awesome code and ym awesome fix or and tweaks mayube rather but anyways etc... -->
def check_images_as_buttons_paths_are_valid(txtKeyDict, localText):
	# This will raise an error if:
	# - The TXT_KEY doesn't exist in any loaded Text/*.xml
	# - The image fails to resolve and is replaced by Civ4's fallback "pink square" (which happens if the DDS path is also invalid, but we catch it at the TXT_KEY level here)

	for buttonHeader, configButtonPathSTxtKey in txtKeyDict.items():
		resolvedButtonPath = localText.getText(configButtonPathSTxtKey, ())
		check_button_path_is_valid(buttonHeader, resolvedButtonPath, configButtonPathSTxtKey)



def getXOccurenceFound(xPanel, leftPadding, interButtonSpacing, nCountOccurencesFound, buttonSize, xSubstractedAdjustment):
	# <!-- custom: all buttons are spaced, except the first one that depends on panel left side padding, so do a - 1 to account for that -->
	if (nCountOccurencesFound < 1):
		raise ValueError("[FATAL] nCountOccurencesFound=%d cannot be < 1, make sure you first increment nCountOccurencesFound at first occurence found before calling this getXOccurenceFound method anyways etc." % nCountOccurencesFound)
	return xPanel + leftPadding + (nCountOccurencesFound * buttonSize) + ((nCountOccurencesFound - 1) * interButtonSpacing) - xSubstractedAdjustment



def getXSubstractedAdjustmentNumTxtBasedOnLenNumTxt(numTxt, addedOffset, buttonSize):
	buttonSizeDoubleSize = 2 * buttonSize
	if (addedOffset > buttonSizeDoubleSize):
		raise ValueError(u"[FATAL] Offset %d too high, cannot be higher than 2 * buttonsize = 2 * %d = %d, please make sure offset is set as intended, and update your code or this method raising the error depending on what you/need want anyways etc." % (addedOffset, buttonSize, buttonSizeDoubleSize))
	
	# <!-- custom: examples of offset:
	# - if addedOffset is 0.00, returns same value
	# - if addedOffset is 0.10, returns value + 0.10, for example 0.55 + 0.10 = 0.65 returned anyways etc 
	# -->

	lenNumTxt = len(numTxt)
	# <!-- custom: be careful the '%' char in for example "+50%" does not appear in str debug, but it is counted in str length, and does however also appear though in the UI in sevopedia leader py, so adjusting this code based on these results
	# xxxxxxxxx3xxxxxxx+7
	# xxxxxxxxx5xxxxxxx-120
	# xxxxxxxxx6xxxxxxx+1254
	# xxxxxxxxx4xxxxxxx+50
	# -->
	if lenNumTxt < 0:
		raise ValueError(u"[FATAL] Unhandled negative length at numTxt=%s, lenNumTxt=%d" % (numTxt, lenNumTxt))
	if lenNumTxt < 3:
		return 0.72 + addedOffset
	elif lenNumTxt == 3:
		# <!-- custom: example "+5"(%), "-8"(%), etc -->
		return 0.79 + addedOffset
	elif lenNumTxt == 4:
		# <!-- custom: example "+50"(%), "-35"(%), etc -->
		return 0.85 + addedOffset
	elif lenNumTxt == 5:
		# <!-- custom: example "+100"(%), "-120"(%), etc -->
		return 0.92 + addedOffset
	elif lenNumTxt == 6:
		# <!-- custom: example "+1000"(%), "-3798"(%), etc -->
		return 1.01 + addedOffset
	else:
		# <!-- custom: example "+10000"(%) or longer, "-37982"(%) or longer, etc -->
		return 1.09 + addedOffset

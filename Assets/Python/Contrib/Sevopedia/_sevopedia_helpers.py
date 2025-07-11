# <!-- custom: constants useful for numTxt under button placement in a grid-like manner anyways , i got the idea to move them here rather to enhance reuse and remove redundance thanks to chatgpt general comment about them hehe anyways etc thanks anyways etc thanks chatgpt etc anyways etc and me toot thanks anyways etc ; note: these are for non-multilist panels, commented-out if we don't need them but kept for reference still if may serve someday but anyways etc -->
HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING = 9
HYPOTHESIZED_INTER_BUTTON_SPACING = 4



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



def check_icon_size_fits_within_icon_frame_size(icon_size, icon_frame_size):
	if icon_size > icon_frame_size:
		raise ValueError(u"[FATAL] icon_size=%d cannot be bigger/higher than icon_frame_size=%d, icon_size must fit within the frame, please adjust icon_size or/and icon_frame_size so that 0 < icon_size < icon_frame_size" % (icon_size, icon_frame_size))



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



def get_max_occurences_found_buttons_per_row(panelWidth, buttonsize):
	totalButtonWidth = buttonsize + HYPOTHESIZED_INTER_BUTTON_SPACING
	return int((panelWidth - HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING) / totalButtonWidth)



def get_numTxt_attack_defense_modifiers(iModAttack, iModDefense):
	numTxt = None

	# Handle class modifiers with x/y format
	# Use %+d to always show the sign (+ or -)
	if iModAttack != 0 or iModDefense != 0:
		if iModAttack != 0 and iModDefense != 0:
			# Both attack and defense: x/y format
			return "%+d/%+d" % (iModAttack, iModDefense)
		elif iModAttack != 0:
			# Only attack: x/* format
			return "%+d/_" % (iModAttack)
		elif iModDefense != 0:
			# Only defense: */y format
			return "_/%+d" % (iModDefense)
	
	return numTxt



def get_numTxt_combat_type_modifiers(iModCombat):
	return "%+d%%" % iModCombat



def get_extra_correction_x(numTxt):
	if len(numTxt) < 3:
		return -3
	elif len(numTxt) == 3:
		return -4
	elif len(numTxt) == 4:
		# <!-- custom: example "+50%" -->
		return -5
	elif len(numTxt) == 5:
		# <!-- custom: example "+50/_", "+100%", etc -->
		return -6
	elif len(numTxt) == 6:
		return -7
	else:
		# <!-- custom: example "+25/+25" -->
		return -8



def get_extra_correction_some_letters_off_centered_x():
	# <!-- custom: it seems this numTxt takes slightly more room than expected and is off-centered as a result, maybe because of capitalized letters of maybe alphabetical chars take a bit more room or some other cause, in all cases it uses same code base than for numerical values and such in other parts of the code anyways etc, so just add a small correction specifically for this numTxt or/and in other similar cases if any other anyways etc -->
	return -2



def get_extra_correction_x_inbetween_buttons(button_size):
	# <!-- custom: adjustment to the extraCorrectionX so that the numTxt is inbetween buttons if i may say anways etc, useful for handling the "or" numTxt for example anyways etc -->

	# <!-- custom: also add a small extra correction because we are slightly off from the center point of between the panels if i may say anyways etc -->
	extraCorrectionOffFromTheCenter = -3
	return (-1 * (int(button_size / 2))) + extraCorrectionOffFromTheCenter


def add_multilist_numTxt_under_button(multiListX, multiListY, extraCorrectionX, iButtonIndex, button_size, buttonsPerRow, numTxt, screen, selfTop, widgetType, font):
	# <!-- custom: for multiline lists -->
	HYPOTHESIZED_MULTI_LIST_EDGE_PADDING = 9
	# <!-- custom: it seems the multilist method uses a smaller inter button lateral spacing than the non multilist one, so adjust as fit anyways etc -->
	HYPOTHESIZED_MULTI_LIST_INTER_BUTTON_SPACING = 2
	# <!-- custom: note: below line not yet tested anyways etc -->
	HYPOTHESIZED_MULTI_LIST_INTER_LINE_VERTICAL_SPACING = 4

	textName = selfTop.getNextWidgetName()
	buttonColumn = iButtonIndex % buttonsPerRow
	buttonRow = iButtonIndex // buttonsPerRow

	# <!-- custom: note: since we start at 0 in this nice system chatgpt and claude ai if i may say helped me design and adjust but anyways etc and that i did myself too if i may say but anyways etc anyways etc anyways etc, we don't need to handle the 1th no spacing with next item of the list, as anything multilied by 0 negates spacing, this applies to both column and row calculation(s) if i am not mistaken but or not but but anyways etc anyways etc anyways etc ; however we just add a X correction to start not at leftmost part of the button anyways but instead at center/middle of button to place our first and onwards numTxT anyways etc -->
	startAtMiddleOfButtonCorrectionX = +1 * (int(button_size / 2))

	# <!-- custom: note: in this code, it seems we are still slightly off vs an ideally centered label, i don't know what the exact cause is, but maybe we can use this as a parameter to control more precisely label positioning based on/depending on anyways etc numTxt and such as we prefer (center more or less aggressively depending on whether numTxt is expected to be long (like "+25/+100" for example) vs short (for example anyways etc "+25%") if i am not mistaken in trying it as such anyways etc, so we add a tiny bit of in this case if i may say anyways etc extra x correction (extraCorrectionX) anyways etc etc -->
	textX = multiListX + HYPOTHESIZED_MULTI_LIST_EDGE_PADDING + startAtMiddleOfButtonCorrectionX + extraCorrectionX + ((buttonColumn - 1) * button_size) + ((buttonColumn - 1) * HYPOTHESIZED_MULTI_LIST_INTER_BUTTON_SPACING)

	# <!-- custom: similarly to extraCorrectionX, we are slightly off for some reason here so adjust Y position of the numTxt multine text i mean anyways etc, but since this is the same for all buttons unlike in extraCorrectionX (i.e. regardless of numTxt length anyways etc), then it is fine i think anyways etc to hardcode it here for convenience and efficiency anyways etc at least i want to do so hopefully convenient or/and helpful or not or yes or etc anyways etc to do so i mean anyways etc -->
	extraCorrectionY = -9
	textY = multiListY + button_size + extraCorrectionY + (buttonRow * button_size) + (buttonRow * HYPOTHESIZED_MULTI_LIST_INTER_LINE_VERTICAL_SPACING)

	textW = 2 * button_size
	textH = 30

	screen.addMultilineText(textName, numTxt, textX, textY, textW, textH, widgetType, -1, -1, font)



def getXOccurenceFound(xPanel, leftPadding, interButtonSpacing, nCountOccurencesFound, buttonSize, xSubstractedAdjustment):
	# <!-- custom: all buttons are spaced, except the first one that depends on panel left side padding, so do a - 1 to account for that -->
	if nCountOccurencesFound < 1:
		raise ValueError("[FATAL] nCountOccurencesFound=%d cannot be < 1, make sure you first increment nCountOccurencesFound at first occurence found before calling this getXOccurenceFound method anyways etc." % nCountOccurencesFound)
	return xPanel + leftPadding + (nCountOccurencesFound * buttonSize) + ((nCountOccurencesFound - 1) * interButtonSpacing) - xSubstractedAdjustment



def getXSubstractedAdjustmentNumTxtBasedOnLenNumTxt(numTxt, addedOffset, buttonSize):
	buttonSizeDoubleSize = 2 * buttonSize
	if addedOffset > buttonSizeDoubleSize:
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

# <!-- custom: constants useful for numTxt under button placement in a grid-like manner anyways , i got the idea to move them here rather to enhance reuse and remove redundance thanks to chatgpt general comment about them hehe anyways etc thanks anyways etc thanks chatgpt etc anyways etc and me toot thanks anyways etc ; note: these are for non-multilist panels, commented-out if we don't need them but kept for reference still if may serve someday but anyways etc -->
#HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING = 9
#HYPOTHESIZED_INTER_BUTTON_SPACING = 4



# <!-- custom: for multilist panels -->
MULTI_LIST_PANEL_OFFSET_X = 9
MULTI_LIST_PANEL_OFFSET_Y = 36
MULTI_LIST_PANEL_ADDITIONAL_W = -1 * (MULTI_LIST_PANEL_OFFSET_X * 2)
MULTI_LIST_PANEL_ADDITIONAL_H = -1 * (MULTI_LIST_PANEL_OFFSET_Y)
# <!-- custom: note: no HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING equivalent for multilists if i am not mistaken as this value is the same as PANEL_MULTILIST_OFFSET_X if i am not mistaken anyways etc so using the real value rather anyways etc ; so we use instead PANEL_MULTILIST_OFFSET_X directly for example in get_multilist_max_buttons_per_row as of now at least hopefully helpful but or not but or yes but anyways etc anyways etc anyways etc -->
HYPOTHESIZED_MULTI_LIST_EDGE_PADDING = 9
# <!-- custom: it seems the multilist method uses a smaller inter button lateral spacing than the non multilist one, so adjust as fit anyways etc -->
HYPOTHESIZED_MULTI_LIST_INTER_BUTTON_SPACING = 2
# <!-- custom: note: below line not yet tested anyways etc -->
HYPOTHESIZED_MULTI_LIST_INTER_LINE_VERTICAL_SPACING = 4



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



# <!-- custom: handle for example PROMOTION_GUERILLA1 now being renamed to PROMOTION_HILLS_MASTER1 if i am not mistaken anyways etc, so summoning wrong asset for example as is done in sevopedia bonus's placeUnits panel as of now anyways etc should raise an error not silently pass if i may say and if i am not mistaken anyways etc ; also useful to access any asset id safely if i am not mistaken such as hills or peak terrains 's id, or hills's button for example too if i am not mistaken anyways etc -->
def getInfoTypeOrFail(tag, gc):
	iType = gc.getInfoTypeForString(tag)
	if iType == -1:
		raise ValueError("Missing XML tag: '%s'" % tag)
	return iType



def get_hills_button(iHill, gc):
	return gc.getTerrainInfo(iHill).getButton()



def get_citiesResolvedButtonPath(localText):
	citiesConfigButtonPathTxtKey = "TXT_KEY_BUTTON_PATH_HARDCODED_CITIES_BUTTON_PATH"
	# <!-- custom: add str() wrapper else (i.e. without it anyways etc) we get an error (it seems) (but anyways etc) anyways (i.e. not impliying it is necessary, but without it we get this error with this other kind of button writing code that does not use same logic as the add as <img> one of other buttons anyways etc (from err log anyways etc):
	#
	# ArgumentError: Python argument types in
	#	CyGInterfaceScreen.attachImageButton(CyGInterfaceScreen, str, str, unicode, CvPythonExtensions.GenericButtonSizes, CvPythonExtensions.WidgetTypes, CvPythonExtensions.CivilopediaPageTypes, int, bool)
	# did not match C++ signature:
	#	attachImageButton(class CyGInterfaceScreen {lvalue}, char const *, char const *, char const *, enum GenericButtonSizes, enum WidgetTypes, int, int, bool)
	#  
	# (adding the str) may or may not be necessary or an alternative solution to this may exist or not, but in all cases anyways etc) anyways etc, etc -->
	citiesResolvedButtonPath = str(localText.getText(citiesConfigButtonPathTxtKey, ()))

	citiesButtonHeader = "Cities button in Sevopedia Unit's placePeakHillCityTerrainsFeaturesModifiers"
	check_button_path_is_valid(citiesButtonHeader, citiesResolvedButtonPath, citiesConfigButtonPathTxtKey)

	return citiesResolvedButtonPath



def get_cities_concept_id(gc):
	# Find the concept ID for "CONCEPT_CITIES"
	for i in range(gc.getNumConceptInfos()):
		if gc.getConceptInfo(i).getType() == "CONCEPT_CITIES":
			return i

	return -1



def get_concept_widgetType_widgetID1_widgetID2(conceptID, widgetTypes, civilopediaPageTypes):
	if conceptID != -1:
		# For concepts, use WIDGET_PEDIA_DESCRIPTION with proper page type and ID
		widgetType = widgetTypes.WIDGET_PEDIA_DESCRIPTION
		widgetID1 = civilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT
		widgetID2 = conceptID
		return widgetType, widgetID1, widgetID2
	else:
		# Default to WIDGET_GENERAL with no click action
		widgetType = widgetTypes.WIDGET_GENERAL
		widgetID1 = -1
		widgetID2 = -1
		return widgetType, widgetID1, widgetID2



def get_numTxt_attack_defense_modifiers(iModAttack, iModDefense):
	# Handle class modifiers with x/y format
	# Use %+d to always show the sign (+ or -)
	if iModAttack != 0 and iModDefense != 0:
		# Both attack and defense: x/y format
		return "%+d/%+d" % (iModAttack, iModDefense)
	elif iModAttack != 0:
		# Only attack: x/* format
		return "%+d/_" % (iModAttack)
	elif iModDefense != 0:
		# Only defense: */y format
		return "_/%+d" % (iModDefense)
	else:
		return "_/_"



def get_numTxt_combat_type_modifiers(iModCombat):
	return "%+d%%" % iModCombat



def get_numTxt_num_free_bonus_or_random_map(iNumFreeBonuses):
	# <!-- custom: note: for freebonus, done according to kujira's website if i am not mistaken anyways etc, in https://gforestshade.github.io/kujira/post/civ4buildinginfos/#inumfreebonuses (translated to english with google chrome), see also "for freebonus, done according to kujira's website" note/code comment at top of sevopedia building py file if need(ed? But or not but or yes but or etc but anyways etc anyways etc anyways etc) anyways etc: based on this, displaying free bonus if >= 1 or if == -1, adjusting display depending on this -->
	if iNumFreeBonuses == -1:
		return "RM"
	elif iNumFreeBonuses >= 1:
		return "%d" % (iNumFreeBonuses)
	else:
		raise ValueError("[FATAL] Unexpected iNumFreeBonuses=%d value out of bounds of iNumFreeBonuses == -1 or iNumFreeBonuses >=1, please verify the code and iNumFreeBonuses are behaving as intended and adjust this sevopedia code or/and your mod code based on this as you want/prefer anyways etc." % iNumFreeBonuses)



def get_extra_correction_x(numTxt):
	if len(numTxt) <= 3:
		# <!-- custom: example "_/_", "1", etc -->
		return -6
	elif len(numTxt) == 4:
		# <!-- custom: example "+50%" -->
		return -6
	elif len(numTxt) == 5:
		# <!-- custom: example "+50/_", "+100%", etc -->
		return -7
	elif len(numTxt) == 6:
		return -8
	else:
		# <!-- custom: example "+25/+25" -->
		return -8



def get_extra_correction_x_inbetween_buttons(button_size):
	# <!-- custom: adjustment to the extraCorrectionX so that the numTxt is inbetween buttons if i may say anways etc, useful for handling the "or" numTxt for example anyways etc -->

	# <!-- custom: also add a small extra correction because we are slightly off from the center point of between the panels if i may say anyways etc -->
	extraCorrectionOffFromTheCenter = -3

	return (-1 * (int(button_size / 2))) + extraCorrectionOffFromTheCenter



def get_multilist_max_buttons_per_row(panelWidth, buttonsize):
	totalButtonWidth = buttonsize + HYPOTHESIZED_MULTI_LIST_INTER_BUTTON_SPACING

	return int((panelWidth - MULTI_LIST_PANEL_OFFSET_X) / totalButtonWidth)



def add_multilist_numTxt_under_button(multiListX, multiListY, extraCorrectionX, iButtonIndex, button_size, maxButtonsPerRow, numTxt, screen, selfTop, widgetType, font):
	textName = selfTop.getNextWidgetName()
	buttonColumn = iButtonIndex % maxButtonsPerRow
	buttonRow = iButtonIndex // maxButtonsPerRow

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

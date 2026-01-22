# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)



from CvPythonExtensions import *

import re



gc = CyGlobalContext()
localText = CyTranslator()



#
# <!-- custom: constants useful for numTxt under button placement in a grid-like manner, i got the idea to move them here rather to enhance reuse and remove redundance thanks to chatgpt general comment about them hehe thanks thanks chatgpt etc and me toot thanks; note: these are for non-multilist panels, commented-out if we don't need them but kept for reference still if may serve someday-->
#HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING = 9
#HYPOTHESIZED_INTER_BUTTON_SPACING = 4



# <!-- custom: for multilist panels -->
MULTILIST_BUTTON_SIZE = 64
MULTI_LIST_PANEL_OFFSET_X = 9
MULTI_LIST_PANEL_OFFSET_Y = 36
MULTI_LIST_PANEL_ADDITIONAL_W = -1 * (MULTI_LIST_PANEL_OFFSET_X * 2)
MULTI_LIST_PANEL_ADDITIONAL_H = -1 * (MULTI_LIST_PANEL_OFFSET_Y)
# <!-- custom: note: no HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING equivalent for multilists as this value is the same as PANEL_MULTILIST_OFFSET_X so using the real value rather; so we use instead PANEL_MULTILIST_OFFSET_X directly for example in get_multilist_max_buttons_per_row. -->
HYPOTHESIZED_MULTI_LIST_EDGE_PADDING = 9
# <!-- custom: it seems the multilist method uses a smaller inter button lateral spacing than the non multilist one, so adjust as fit -->
HYPOTHESIZED_MULTI_LIST_INTER_BUTTON_SPACING = 2
# <!-- custom: note: below line not yet tested. -->
HYPOTHESIZED_MULTI_LIST_INTER_LINE_VERTICAL_SPACING = 4
# <!-- custom: when displaying only one row, adjust height to hide the 2nd row's buttons so it is prettier/clearer to read -->
HIDE_SECOND_ROW_MULTI_LIST = - 4



# <!-- custom: Shared exclusion list for Sevopedia Leader and Trait pages.
# LEADER_BARBARIAN is excluded because it's not a playable/selectable leader.
# LEADER_DEFAULTS is not listed because it has no index (it's an XML template). (Claude Opus 4.5) -->
EXCLUDED_LEADER_TYPES_FROM_SEVOPEDIA = (
	"LEADER_BARBARIAN",
)



# <!-- custom: favorite leader type selectors for get_favorite_leader_counts. (GPT-5.2-Codex) -->
FAVORITE_LEADER_TYPE_RELIGION = 0
FAVORITE_LEADER_TYPE_CIVIC = 1



# <!-- custom: Sevopedia Chart Helpers (shared across Handicap/GameSpeed/WorldSize/Era charts). (Claude Code Opus 4.5) -->
#
# <!-- custom: Common constants for chart tables -->
CHART_TABLE_MARGIN = 4
CHART_TABLE_ROW_H = 15
CHART_TABLE_W_ICON = 24
# <!-- custom: All known enum prefixes to strip. Grouped here for simplicity across all charts. -->
CHART_ENUM_PREFIXES = ("TECH_", "HANDICAP_", "GOODY_", "GAMESPEED_", "ERA_", "WORLDSIZE_")
# <!-- custom: # Stable icon sorting (fixes "emoji order changes / ties shuffle")
#
# Civ4 table sorting uses the raw cell text. If multiple rows share the same icon,
# tie ordering can shuffle between ascending/descending clicks.
# We fix ties by appending an invisible sort key (icon_group + row_index) to the icon cell text.
# IMPORTANT: We avoid ASCII control chars (0x01..0x1F) here. Some Civ4 builds can fail to render
# *any* glyph in a table cell if such chars are present. This was the root cause of:
#   "buttons show, but GameFont glyphs (food/citizen/gold/etc) are blank".
# Instead we use Unicode zero-width/formatting marks (U+200B..U+200F), which are invisible
# and safe to include in Civ4's UI strings. (GPT-5.2-Codex + ChatGPT-5.2 Thinking) -->
CHART_SORT_DIGITS = (u"\u200b", u"\u200c", u"\u200d", u"\u200e", u"\u200f")  # 5 invisible marks



def get_leaders_index_to_type_map():
	# Returns a dictionary mapping each leader index (int) to its string type (e.g., "LEADER_GANDHI").
	# Excluded leaders (like BARBARIAN) must be filtered by caller if needed.

	leaders_indexes_to_types = {}
	for iLeader in range(gc.getNumLeaderHeadInfos()):
		leader_type = gc.getLeaderHeadInfo(iLeader).getType()
		leaders_indexes_to_types[iLeader] = leader_type
	return leaders_indexes_to_types



def get_leader_index_from_leader_type(leader_type):
	# Given a leader_type string (e.g. "LEADER_ALEXANDER"), return its iLeader index.
	# Raises ValueError if not found. Compatible with Python 2.4 and Civ4 DLL.
	# <!-- custom: note: LEADER_DEFAULTS doesn't seem to have a leader index at all, so don't use it for this function -->

	for iLeader in range(gc.getNumLeaderHeadInfos()):
		current_leader_type = gc.getLeaderHeadInfo(iLeader).getType()
		if current_leader_type == leader_type:
			return iLeader

	raise ValueError("[FATAL] leader_type=%s not found in gc.getLeaderHeadInfo list. Note: this can also happen but not only in particular with LEADER_DEFAULTS, which does not seem to have a leader index at all in gc of base advciv code, that we use as well in our/this mod very similarly if not identically, so make sure to address the edge case of LEADER_DEFAULTS in another way to not get caught/stuck in this edge case error message in particular, possibly for other leaders as well." % leader_type)



def get_leader_index_safe(leader_type):
	# Returns leader index for a leader_type string, or -1 if not found.
	# Unlike get_leader_index_from_leader_type, this does not raise - useful for
	# exclusion lists that may include non-indexed types like LEADER_DEFAULTS.
	for iLeader in range(gc.getNumLeaderHeadInfos()):
		if gc.getLeaderHeadInfo(iLeader).getType() == leader_type:
			return iLeader
	return -1


def get_leader_indexes_from_leader_types(leader_types):
	# Given a list/tuple of leader types, return tuple of valid leader indexes.
	# Silently skips types that don't exist (e.g. LEADER_DEFAULTS has no index).
	result = []
	for leader_type in leader_types:
		idx = get_leader_index_safe(leader_type)
		if idx != -1:
			result.append(idx)
	return tuple(result)


def get_excluded_leader_indexes(leader_types):
	return get_leader_indexes_from_leader_types(leader_types)


def get_real_leader_maps_and_count(excluded_leader_types):
	# Returns (leaderIds, leaderToCiv, numRealLeaders).
	excluded_leader_indexes = set(get_leader_indexes_from_leader_types(excluded_leader_types))
	leader_ids = []
	leader_to_civ = {}
	num_real_leaders = 0

	for iLeader in range(gc.getNumLeaderHeadInfos()):
		if iLeader in excluded_leader_indexes:
			continue
		iCivForLeader = -1
		for iCiv in range(gc.getNumCivilizationInfos()):
			if gc.getCivilizationInfo(iCiv).isLeaders(iLeader):
				iCivForLeader = iCiv
				break
		if iCivForLeader == -1:
			continue
		num_real_leaders += 1
		leader_ids.append(iLeader)
		leader_to_civ[iLeader] = iCivForLeader

	return leader_ids, leader_to_civ, num_real_leaders


# <!-- custom: Build leaders header text with X/Y (Z%) (example "Leaders 12/53 (22%)") for any Sevopedia panel. (GPT-5.2-Codex (summarized)) -->
def format_leaders_header_text(num_with, total, headerLabel):
	percent = 0
	if total > 0:
		percent = (100 * num_with) / total
	return u"%s %d/%d (%d%%)" % (
		headerLabel,
		num_with,
		total,
		percent,
	)


# <!-- custom: Count leaders whose favorite type matches iFavoriteId; favoriteType is "RELIGION" or "CIVIC". (GPT-5.2-Codex) -->
def get_favorite_leader_counts(favoriteType, iFavoriteId, excluded_leader_types):
	leader_ids, unused_leader_to_civ, total_real_leaders = get_real_leader_maps_and_count(excluded_leader_types)
	num_with_favorite = 0
	for iLeader in leader_ids:
		leaderInfo = gc.getLeaderHeadInfo(iLeader)
		if favoriteType == FAVORITE_LEADER_TYPE_RELIGION:
			if leaderInfo.getFavoriteReligion() == iFavoriteId:
				num_with_favorite += 1
		elif favoriteType == FAVORITE_LEADER_TYPE_CIVIC:
			if leaderInfo.getFavoriteCivic() == iFavoriteId:
				num_with_favorite += 1
		else:
			raise ValueError("favoriteType=%d is not supported; use FAVORITE_LEADER_TYPE_RELIGION or FAVORITE_LEADER_TYPE_CIVIC" % favoriteType)
	return num_with_favorite, total_real_leaders



def get_leader_type_from_leader_index(iLeader):
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
		raise ValueError(u"[FATAL] icon_size=%d cannot be bigger/higher than icon_frame_size=%d, icon_size must fit within the frame, please adjust icon_size or icon_frame_size so that 0 < icon_size < icon_frame_size" % (icon_size, icon_frame_size))



def check_button_path_is_valid(buttonHeader, resolvedButtonPath, configButtonPathSTxtKey):
	if resolvedButtonPath == configButtonPathSTxtKey:
		raise ValueError(u"[VALUE ERROR] Button path not found in XML (resolvedButtonPath=%s matches configButtonPath=%s in buttonHeader=%s, which indicates button path provided in config most likely does not exist in the XML), please check button path provided exists in your mod path and also matches button path in (or in - whichever filename it would have in the future -) AdvCiv-SAS_Images_As_Buttons.xml or AdvCiv-SAS_Button_Paths_Hardcoded.xml (or wherever they are stored in the future if these files's filename or code changes) is valid and exists in your mod path." % (resolvedButtonPath, configButtonPathSTxtKey, buttonHeader))



# <!-- custom: added with the help of chatgpt 5.2 thanks to help separate Land features in sevopedia into as of now Land (Removable) and Land (Other) -->
# A feature is "removable" if there exists a Build that removes it (e.g. Chop Forest, Clear Jungle, Remove Fallout).
# We do this via CvBuildInfo because CvFeatureInfo in our DLL does not expose getRemoveTech().
def SAS_isFeatureRemovable(iFeature):
	for iBuild in range(gc.getNumBuildInfos()):
		buildInfo = gc.getBuildInfo(iBuild)
		if not buildInfo or buildInfo.isGraphicalOnly():
			continue

		# In BtS/AdvCiv-style DLLs, isFeatureRemove is per-feature (takes iFeature).
		# If a modmod changes this API, it should be adjusted here (centralized).
		if buildInfo.isFeatureRemove(iFeature):
			# Some builds may have 0 time for some features in some mods, so we treat any "remove" as removable.
			return True

	return False



# <!-- custom: handle for example PROMOTION_GUERILLA1 now being renamed to PROMOTION_HILLS_MASTER1, so summoning wrong asset for example as is done in sevopedia bonus's placeRelevantUnits panel as of now should raise an error not silently pass; also useful to access any asset id safely such as hills or peak terrains 's id, or hills's button for example too; is also useful to detect and signal loudly errors such as using wrong "TERRAIN_FOREST" as part of copy pasting terrain code into features code of the placeUnits method there as of now instead of "FEATURE_FOREST", and we get a nice error instead of what i assume would be a silent pass we wouldn't want at least me based on previous parts of this code comment and remember it correctly as i think i do but not 100% sure even if 99.99% as chatgpt said to me too btw xd. -->
def getInfoTypeOrFail(tag):
	iType = gc.getInfoTypeForString(tag)
	if iType == -1:
		raise ValueError("Missing XML tag: '%s'" % tag)
	return iType



def get_citiesResolvedButtonPath():
	citiesConfigButtonPathTxtKey = "TXT_KEY_BUTTON_PATH_HARDCODED_CITIES_BUTTON_PATH"
	# <!-- custom: add str() wrapper else (i.e. without it) we get an error (it seems) (i.e. not impliying it is necessary, but without it we get this error with this other kind of button writing code that does not use same logic as the add as <img> one of other buttons (from err log):
	#
	# ArgumentError: Python argument types in
	#	CyGInterfaceScreen.attachImageButton(CyGInterfaceScreen, str, str, unicode, CvPythonExtensions.GenericButtonSizes, CvPythonExtensions.WidgetTypes, CvPythonExtensions.CivilopediaPageTypes, int, bool)
	# did not match C++ signature:
	#	attachImageButton(class CyGInterfaceScreen {lvalue}, char const *, char const *, char const *, enum GenericButtonSizes, enum WidgetTypes, int, int, bool)
	#  
	# (adding the str) may or may not be necessary or an alternative solution to this may exist or not, but in all cases), etc -->
	citiesResolvedButtonPath = str(localText.getText(citiesConfigButtonPathTxtKey, ()))

	citiesButtonHeader = "Cities button in Sevopedia Unit's placePeakHillCityTerrainsFeaturesModifiers"
	check_button_path_is_valid(citiesButtonHeader, citiesResolvedButtonPath, citiesConfigButtonPathTxtKey)

	return citiesResolvedButtonPath



def get_concept_id(concept_type):
	# <!-- custom: Find the concept ID, for example for concept_type "CONCEPT_CITIES" (LLM) -->
	for i in range(gc.getNumConceptInfos()):
		if gc.getConceptInfo(i).getType() == concept_type:
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
	# <!-- custom: note: for freebonus, done according to kujira's website, in https://gforestshade.github.io/kujira/post/civ4buildinginfos/#inumfreebonuses (translated to english with google chrome), see also "for freebonus, done according to kujira's website" note/code comment at top of sevopedia building py file if needed: based on this, displaying free bonus if >= 1 or if == -1, adjusting display depending on this -->
	if iNumFreeBonuses == -1:
		return "RM"
	elif iNumFreeBonuses >= 1:
		return "%d" % (iNumFreeBonuses)
	else:
		raise ValueError("[FATAL] Unexpected iNumFreeBonuses=%d value out of bounds of iNumFreeBonuses == -1 or iNumFreeBonuses >=1, please verify the code and iNumFreeBonuses are behaving as intended and adjust this sevopedia code or your mod code based on this as you want/prefer." % iNumFreeBonuses)



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
	# <!-- custom: adjustment to the extraCorrectionX so that the numTxt is inbetween buttons, useful for handling the "or" numTxt for example -->

	# <!-- custom: also add a small extra correction because we are slightly off from the center point of between the panels -->
	extraCorrectionOffFromTheCenter = -3

	return (-1 * (int(button_size / 2))) + extraCorrectionOffFromTheCenter



# <!-- custom: note: era button path also used in CvEraMovieScreen.py -->
def get_era_movie_path(iEra):
	if iEra == 0:
		return "Art/Movies/Era/Era01-Classical.dds"
	if iEra == 1:
		return "Art/Movies/Era/Era01-Classical.dds"
	if iEra == 2:
		return "Art/Movies/Era/Era02-Medeival.dds"
	if iEra == 3:
		return "Art/Movies/Era/Era03-Renaissance.dds"
	if iEra == 4:
		return "Art/Movies/Era/Era04-Industrial.dds"
	return "Art/Movies/Era/Era05-Modern.dds"



def get_multilist_max_buttons_per_row(panelWidth, buttonsize):
	totalButtonWidth = buttonsize + HYPOTHESIZED_MULTI_LIST_INTER_BUTTON_SPACING

	return int((panelWidth - MULTI_LIST_PANEL_OFFSET_X) / totalButtonWidth)



def add_multilist_numTxt_under_button(multiListX, multiListY, extraCorrectionX, iButtonIndex, button_size, maxButtonsPerRow, numTxt, screen, selfTop, widgetType, font):
	textName = selfTop.getNextWidgetName()
	buttonColumn = iButtonIndex % maxButtonsPerRow
	buttonRow = iButtonIndex // maxButtonsPerRow

	# <!-- custom: note: since we start at 0 in this nice system chatgpt and claude ai if i may say helped me design and adjust thanks, we don't need to handle the 1th no spacing with next item of the list, as anything multilied by 0 negates spacing, this applies to both column and row calculation(s); however we just add a X correction to start not at leftmost part of the button anyways but instead at center/middle of button to place our first and onwards numTxT -->
	startAtMiddleOfButtonCorrectionX = +1 * (int(button_size / 2))

	# <!-- custom: note: in this code, it seems we are still slightly off vs an ideally centered label, i don't know what the exact cause is, but maybe we can use this as a parameter to control more precisely label positioning based on/depending on numTxt and such as we prefer (center more or less aggressively depending on whether numTxt is expected to be long (like "+25/+100" for example) vs short (for example"+25%") in trying it as such, so we add a tiny bit of in this case extra x correction (extraCorrectionX) etc -->
	textX = multiListX + HYPOTHESIZED_MULTI_LIST_EDGE_PADDING + startAtMiddleOfButtonCorrectionX + extraCorrectionX + ((buttonColumn - 1) * button_size) + ((buttonColumn - 1) * HYPOTHESIZED_MULTI_LIST_INTER_BUTTON_SPACING)

	# <!-- custom: similarly to extraCorrectionX, we are slightly off for some reason here so adjust Y position of the numTxt multine text, but since this is the same for all buttons unlike in extraCorrectionX (i.e. regardless of numTxt length), then it is fine i think to hardcode it here for convenience and efficiency at least i want to do so hopefully convenient or helpful or not or yes or etc to do so -->
	extraCorrectionY = -9
	textY = multiListY + button_size + extraCorrectionY + (buttonRow * button_size) + (buttonRow * HYPOTHESIZED_MULTI_LIST_INTER_LINE_VERTICAL_SPACING)

	textW = 2 * button_size
	textH = 30

	screen.addMultilineText(textName, numTxt, textX, textY, textW, textH, widgetType, -1, -1, font)



def chart_font2(szText):
	# Wrap text in <font=2> tags for chart table cells.
	return u"<font=2>%s</font>" % unicode(szText)  # noqa: F821



def chart_encode_base5(iValue, iDigits):
	# Encode an integer as a base-5 string using invisible Unicode chars.
	out = []
	for _ in xrange(iDigits):  # noqa: F821
		out.append(CHART_SORT_DIGITS[iValue % 5])
		iValue //= 5
	out.reverse()
	return u"".join(out)



def chart_sort_key(iGroup, iRowIndex):
	# Generate an invisible sort key for stable icon column sorting.
	# 4 base-5 digits cover up to 624, enough for our "group" numbering (<= 140).
	# 3 digits cover up to 124 rows.
	return u"<font=1>" + chart_encode_base5(iGroup, 4) + chart_encode_base5(iRowIndex, 3) + u"</font>"



def chart_beautify_field_name(raw_name):
	# Convert camelCase/underscore field names to readable labels.
	# Strips leading 'i' or 'b' prefix, replaces _ with spaces, splits camelCase, replaces Percent with %.
	name = raw_name
	if name.startswith("i") and len(name) > 1 and name[1].isupper():
		name = name[1:]
	if name.startswith("b") and len(name) > 1 and name[1].isupper():
		name = name[1:]
	name = re.sub(r"_", " ", name)
	name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
	if name.endswith("Percent"):
		name = name[:-len("Percent")] + "%"
	return name



def chart_beautify_enum_name(raw_name):
	# Convert ENUM_STYLE_NAMES to Title Case Labels.
	# Strips known prefixes, replaces _ with spaces, converts to title case.
	name = raw_name
	for prefix in CHART_ENUM_PREFIXES:
		if name.startswith(prefix):
			name = name[len(prefix):]
			break
	name = re.sub(r"_", " ", name)
	return name.title()



def chart_chunk_list(items, size):
	# Split a list into chunks of given size. Returns list of lists.
	if size <= 0:
		return [items]
	chunks = []
	current = []
	for item in items:
		current.append(item)
		if len(current) >= size:
			chunks.append(current)
			current = []
	if current:
		chunks.append(current)
	return chunks



def chart_format_tech_list(value, return_list, none_text, abbrev_tech_names=None):
	# Parse a comma-separated tech list string into formatted output.
	# value: comma-separated string of tech names/types
	# return_list: if True, return list; if False, return joined string
	# none_text: text to return/use when list is empty
	# abbrev_tech_names: optional dict of {full_name: abbreviated_name}
	if not value:
		if return_list:
			return []
		return none_text
	parts = value.split(",")
	out = []
	for part in parts:
		p = part.strip()
		if not p:
			continue
		# Beautify if it looks like an enum (e.g. TECH_AGRICULTURE)
		if p.startswith("TECH_"):
			p = chart_beautify_enum_name(p)
		# Apply abbreviations if provided
		if abbrev_tech_names and p in abbrev_tech_names:
			p = abbrev_tech_names[p]
		out.append(p)
	if return_list:
		return out
	if len(out) == 0:
		return none_text
	return ", ".join(out)

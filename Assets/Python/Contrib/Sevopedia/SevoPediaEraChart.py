# --- Era chart page for Sevopedia (AdvCiv-SAS) ---
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# Mirrors the handicap chart layout, but for EraInfo.



from CvPythonExtensions import *
import CvUtil
import re

gc = CyGlobalContext()
localText = CyTranslator()

def _font2(szText):
	return u"<font=2>%s</font>" % unicode(szText)



class SevoPediaEraChart:
	def __init__(self, main):
		self.top = main
		self._cachedTable = None

		self.MARGIN = 4
		self.ROW_H = 15
		self.W_ICON = 24
		self.W_FIELD = 210
		iHeaderIcons = gc.getDefineINT("SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS")
		if iHeaderIcons == 0:
			iHeaderIcons = gc.getDefineINT("SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS")
		self.IS_SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS = (iHeaderIcons != 0)
		self.TABLE_FILL_PERCENT = gc.getDefineINT("SAS_SEVOPEDIA_ERA_CHART_TABLE_FILL_PERCENT")
		if self.TABLE_FILL_PERCENT <= 0:
			raise ValueError("[FATAL] SAS_SEVOPEDIA_ERA_CHART_TABLE_FILL_PERCENT must be >= 1.")

	def interfaceScreen(self):
		screen = self.top.getScreen()
		self._drawTable(screen)

	def _drawTable(self, screen):
		x = self.top.X_ITEMS
		y = self.top.Y_PEDIA_PAGE
		w = self.top.W_SCREEN - self.top.X_ITEMS - self.MARGIN
		h = self.top.H_PEDIA_PAGE

		screen.addPanel(self.top.getNextWidgetName(), "", "", True, True, x, y, w, h, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", True, True, x + self.MARGIN, y + self.MARGIN, w - (self.MARGIN * 2), h - (self.MARGIN * 2), PanelStyles.PANEL_STYLE_BLUE50)

		table = self.top.getNextWidgetName()
		tableX = x + self.MARGIN
		tableY = y + self.MARGIN + 4
		tableW = w - (self.MARGIN * 2)
		tableH = h - (self.MARGIN * 2) - 4

		data = self._getTableData()
		if not data:
			screen.setLabel(self.top.getNextWidgetName(), "Background",
					u"<font=3>" + localText.getText("TXT_KEY_PEDIA_SCREEN_CONTENTS", ()) + u": " + u"No data</font>",
					CvUtil.FONT_LEFT_JUSTIFY, tableX, tableY, 0, FontTypes.GAME_FONT,
					WidgetTypes.WIDGET_GENERAL, -1, -1)
			return

		header = data[0]
		rows = data[1:]
		nCols = len(header)
		if nCols < 2:
			return

		totalW = (tableW * self.TABLE_FILL_PERCENT) / 100
		if self.IS_SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS:
			remainingW = max(0, totalW - self.W_ICON - self.W_FIELD)
			value_cols = nCols - 2
		else:
			remainingW = max(0, totalW - self.W_FIELD)
			value_cols = nCols - 1
		if value_cols > 0:
			wNum = remainingW / value_cols
		else:
			wNum = 0

		screen.addTableControlGFC(table, nCols, tableX, tableY, tableW, tableH, True, False, self.ROW_H, self.ROW_H, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSort(table)

		# Minor Python-level micro-opt: bind methods used in hot loops.
		setHeader = screen.setTableColumnHeader
		appendRow = screen.appendTableRow
		setCell = screen.setTableText

		for iCol in range(nCols):
			if self.IS_SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS and iCol == 0:
				colW = self.W_ICON
			elif (self.IS_SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS and iCol == 1) or (not self.IS_SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS and iCol == 0):
				colW = self.W_FIELD
			else:
				colW = wNum
			setHeader(table, iCol, header[iCol], colW)

		for row in rows:
			iRow = appendRow(table)
			for iCol in range(nCols):
				if iCol < len(row):
					cell = row[iCol]
				else:
					cell = u""

				# Icon column: cell is (text, buttonPath) tuple
				if self.IS_SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS and iCol == 0:
					if isinstance(cell, tuple):
						text = cell[0]
						icon_button = cell[1]
					else:
						text = cell
						icon_button = ""
					if icon_button:
						icon_button = CvUtil.convertToStr(icon_button)
					setCell(table, iCol, iRow, text, icon_button, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

				# Field column (left)
				elif (self.IS_SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS and iCol == 1) or (not self.IS_SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS and iCol == 0):
					setCell(table, iCol, iRow, cell, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

				# Value columns (center)
				else:
					setCell(table, iCol, iRow, cell, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

	def _getTableData(self):
		if self._cachedTable is not None:
			return self._cachedTable

		data = self._buildTableFromGameData()
		self._cachedTable = data
		return data

	def _buildTableFromGameData(self):
		row_specs = (
			# (field_key, display_label_or_None, getter_name_or_None, icon_token, value_type)
			("bNoGoodies",                 "No Goodies",                 "isNoGoodies",                 "btn:skull",        "bool"),
			("bAllGoodyTechs",             "All Goody Techs",             "isAllGoodyTechs",             "glyph:research",   "bool"),
			("bNoAnimals",                 "No Animals",                 "isNoAnimals",                 "btn:lion",         "bool"),
			("bNoBarbUnits",               "No Barb Units",              "isNoBarbUnits",               "btn:skull",        "bool"),
			("bNoBarbCities",              "No Barb Cities",             "isNoBarbCities",              "btn:skull",        "bool"),
			("iAdvancedStartPoints",       "Advanced Start Points",      "getAdvancedStartPoints",      "glyph:defense",    "int"),
			("iStartingUnitMultiplier",    "Starting Unit Multiplier",   "getStartingUnitMultiplier",   "btn:swords",       "int"),
			("iStartingDefenseUnits",      "Starting Defense Units",     "getStartingDefenseUnits",     "btn:swords",       "int"),
			("iStartingWorkerUnits",       "Starting Worker Units",      "getStartingWorkerUnits",      "glyph:citizen",    "int"),
			("iStartingExploreUnits",      "Starting Explore Units",     "getStartingExploreUnits",     "btn:swords",       "int"),
			("iStartingGold",              "Starting Gold",              "getStartingGold",             "glyph:gold",       "int"),
			("iFreePopulation",            "Free Population",            "getFreePopulation",           "glyph:citizen",    "int"),
			("iStartPercent",              "Start Percent",              "getStartPercent",             "glyph:defense",    "int"),
			("iGrowthPercent",             None,                         "getGrowthPercent",            "glyph:food",       "int"),
			("iTrainPercent",              None,                         "getTrainPercent",             "btn:swords",       "int"),
			("iConstructPercent",          None,                         "getConstructPercent",         "glyph:prod",       "int"),
			("iCreatePercent",             None,                         "getCreatePercent",            "glyph:prod",       "int"),
			("iResearchPercent",           None,                         "getResearchPercent",          "glyph:research",   "int"),
			("iTechCostModifier",          "Tech Cost Modifier",         "getTechCostModifier",         "glyph:research",   "int"),
			("iAIMaxGroundbreakingPenalty","AI Max Groundbreaking Pen.", "getAIMaxGroundbreakingPenalty","btn:brain",        "int"),
			("iHumanMaxGroundbreakingPenalty","Human Max Groundbreaking Pen.","getHumanMaxGroundbreakingPenalty","btn:brain",  "int"),
			("iBuildPercent",              None,                         "getBuildPercent",             "glyph:citizen",    "int"),
			("iImprovementPercent",        None,                         "getImprovementPercent",       "glyph:citizen",    "int"),
			("iGreatPeoplePercent",        None,                         "getGreatPeoplePercent",       "glyph:great_people","int"),
			("iCulturePercent",            None,                         "getCulturePercent",           "glyph:culture",    "int"),
			("iAnarchyPercent",            None,                         "getAnarchyPercent",           "btn:fire",         "int"),
			("iEventChancePerTurn",        "Event Chance Per Turn",      "getEventChancePerTurn",       "btn:gear",         "int"),
			("bAIAgeOfPestilence",          "AI Age Of Pestilence",        "isAIAgeOfPestilence",          "btn:brain",        "bool"),
			("bAIAgeOfExploration",         "AI Age Of Exploration",       "isAIAgeOfExploration",         "btn:brain",        "bool"),
			("bAIAgeOfPollution",           "AI Age Of Pollution",         "isAIAgeOfPollution",           "btn:brain",        "bool"),
			("bAIAgeOfFertility",           "AI Age Of Fertility",         "isAIAgeOfFertility",           "btn:brain",        "bool"),
			("bAIAgeOfGuns",                "AI Age Of Guns",              "isAIAgeOfGuns",                "btn:brain",        "bool"),
			("bAIAgeOfProduction",          "AI Age Of Production",        "isAIAgeOfProduction",          "btn:brain",        "bool"),
			("bAIAtomicAge",                "AI Atomic Age",               "isAIAtomicAge",                "btn:brain",        "bool"),
			("Techs",                       "Techs",                       None,                            "glyph:research",   "techs"),
		)

		field_getters_list = []
		for field_name, _display_label, getter_name, _icon_token, _value_type in row_specs:
			if getter_name:
				field_getters_list.append((field_name, getter_name))
		field_getters = tuple(field_getters_list)

		if gc.getNumEraInfos() > 0:
			info = gc.getEraInfo(0)
			missing = []
			for field_name, getter_name in field_getters:
				if not hasattr(info, getter_name):
					missing.append(getter_name)
			if missing:
				raise RuntimeError("[FATAL] Your mod DLL does not expose the required CvEraInfo Python getters: %s. Please expose them in CyInfoInterface2.cpp and rebuild the DLL." % ", ".join(missing))

		game = CyGame()
		btn_by_name = {}
		def _btn_path(szTxtKey):
			return CvUtil.convertToStr(localText.getText(szTxtKey, ()))

		_btn_defs = (
			# (name, TXT_KEY_IMAGE_AS_BUTTON_*_PATH)
			("lion",   "TXT_KEY_IMAGE_AS_BUTTON_LION_FACE_BUTTON_PATH"),
			("skull",  "TXT_KEY_IMAGE_AS_BUTTON_SKULL_BUTTON_PATH"),
			("swords", "TXT_KEY_IMAGE_AS_BUTTON_CROSSED_SWORDS_BUTTON_PATH"),
			("fire",   "TXT_KEY_IMAGE_AS_BUTTON_FIRE_BUTTON_PATH"),
			("gear",   "TXT_KEY_IMAGE_AS_BUTTON_GEAR_BUTTON_PATH"),
			("brain",  "TXT_KEY_IMAGE_AS_BUTTON_BRAIN_BUTTON_PATH"),
		)
		for i, (name, txtKey) in enumerate(_btn_defs):
			btn_by_name[name] = (_btn_path(txtKey), (i + 1) * 10)

		glyph_by_name = {}
		_glyph_defs = (
			# (name, glyph_char)
			("food",         (u"%c" % (gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar()))),
			("prod",         (u"%c" % (gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar()))),
			("gold",         (u"%c" % (gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar()))),
			("research",     (u"%c" % (gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar()))),
			("culture",      (u"%c" % (gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar()))),
			("citizen",      (u"%c" % (game.getSymbolID(FontSymbols.CITIZEN_CHAR)))),
			("defense",      (u"%c" % (game.getSymbolID(FontSymbols.DEFENSE_CHAR)))),
			("great_people", (u"%c" % (game.getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR)))),
		)
		for name, glyph in _glyph_defs:
			glyph_by_name[name] = glyph

		# ---------------------------------------------------------------------
		# Stable icon sorting (prevents same-icon rows from shuffling on re-sort)
		# ---------------------------------------------------------------------
		_SORT_DIGITS = (u"\u200b", u"\u200c", u"\u200d", u"\u200e", u"\u200f")

		def _encode_base5(iValue, iDigits):
			out = []
			for _ in xrange(iDigits):
				out.append(_SORT_DIGITS[iValue % 5])
				iValue //= 5
			out.reverse()
			return u"".join(out)

		def _sort_key(iGroup, iRowIndex):
			return u"<font=1>" + _encode_base5(iGroup, 4) + _encode_base5(iRowIndex, 3) + u"</font>"

		icon_token_by_key = {}
		display_label_by_key = {}
		for field_name, display_label, _getter_name, icon_token, _value_type in row_specs:
			if icon_token:
				icon_token_by_key[field_name] = icon_token
			if display_label:
				display_label_by_key[field_name] = display_label

		def icon_cell_for_key(icon_key, iRowIndex):
			if not icon_key:
				return (_sort_key(0, iRowIndex), "")
			token = icon_token_by_key.get(icon_key, "")
			if not token:
				return (_sort_key(0, iRowIndex), "")
			if token.startswith("btn:"):
				name = token[4:]
				btn = btn_by_name.get(name)
				if btn is None:
					return (_sort_key(0, iRowIndex), "")
				path, iGroup = btn[0], btn[1]
				if not path:
					return (_sort_key(0, iRowIndex), "")
				return (_sort_key(iGroup, iRowIndex), path)
			if token.startswith("glyph:"):
				name = token[6:]
				glyph = glyph_by_name.get(name, u"")
				if not glyph:
					return (_sort_key(0, iRowIndex), "")
				return (_font2(glyph) + _sort_key(0, iRowIndex), "")
			return (_sort_key(0, iRowIndex), "")

		none_text = localText.getText("TXT_KEY_PEDIA_SAS_HANDICAP_CHART_FREE_TECHS_NONE", ())
		yes_text = localText.getText("TXT_KEY_YES", ())
		no_text = localText.getText("TXT_KEY_NO", ())

		era_types = []
		era_labels = []
		for iEra in xrange(gc.getNumEraInfos()):
			info = gc.getEraInfo(iEra)
			era_types.append(info.getType())
			era_labels.append(info.getDescription())

		parsed_data = {}
		for iEra in xrange(gc.getNumEraInfos()):
			info = gc.getEraInfo(iEra)
			era_type = info.getType()
			era_dict = {}

			for field_name, getter_name in field_getters:
				getter = getattr(info, getter_name)
				era_dict[field_name] = str(getter())

			parsed_data[era_type] = era_dict

		techs_by_era = {}
		for era_type in era_types:
			techs_by_era[era_type] = []

		for iTech in xrange(gc.getNumTechInfos()):
			tech_info = gc.getTechInfo(iTech)
			iEra = tech_info.getEra()
			if iEra < 0 or iEra >= len(era_types):
				continue
			tech_name = tech_info.getDescription()
			if not tech_name:
				tech_name = self._beautify_enum_name(tech_info.getType())
			techs_by_era[era_types[iEra]].append(tech_name)

		for era_type in era_types:
			tech_list = techs_by_era.get(era_type, [])
			if tech_list:
				parsed_data[era_type]["Techs"] = ", ".join(tech_list)
			else:
				parsed_data[era_type]["Techs"] = ""

		header = []
		if self.IS_SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS:
			header.append(u"")
			header.append(_font2("Field"))
		else:
			header.append(_font2("Field"))
		for label in era_labels:
			header.append(_font2(label))

		table = [header]

		row_index = 0
		techs_per_cell = 1
		for field_name, display_label, _getter_name, _icon_token, value_type in row_specs:
			if field_name == "Techs":
				tech_rows = self._expandTechRows(field_name, era_types, parsed_data, techs_per_cell, none_text)
				for tech_row in tech_rows:
					display_text = tech_row["Field"]
					if self.IS_SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS:
						icon_key = tech_row.get("IconKey", "")
						row = [icon_cell_for_key(icon_key, row_index), _font2(display_text)]
					else:
						row = [_font2(display_text)]
					for era_type in era_types:
						row.append(_font2(tech_row.get(era_type, "")))
					table.append(row)
					row_index += 1
				continue

			szFieldName = display_label_by_key.get(field_name, self._beautify_field_name(field_name))

			if self.IS_SAS_SEVOPEDIA_ERA_CHART_HEADER_ICONS:
				row = [icon_cell_for_key(field_name, row_index), _font2(szFieldName)]
			else:
				row = [_font2(szFieldName)]

			for era_type in era_types:
				val = parsed_data.get(era_type, {}).get(field_name, "")
				if value_type == "bool":
					val = self._format_bool(val, yes_text, no_text)
				row.append(_font2(val))

			table.append(row)
			row_index += 1

		return table

	def _format_bool(self, value, yes_text, no_text):
		# <!-- custom: normalize bool strings from Cy* getters so chart uses + / empty instead of True/False. (GPT-5.2-Codex) -->
		if value in (True, "1", 1):
			return "+"
		if value in (False, "0", 0):
			return ""
		if isinstance(value, basestring):
			if value.lower() == "true":
				return "+"
			if value.lower() == "false":
				return ""
		return value

	def _beautify_field_name(self, raw_name):
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

	def _beautify_enum_name(self, raw_name):
		name = raw_name
		for prefix in ("TECH_", "HANDICAP_", "GOODY_", "ERA_"):
			if name.startswith(prefix):
				name = name[len(prefix):]
				break
		name = re.sub(r"_", " ", name)
		return name.title()

	def _format_tech_list(self, value, return_list, none_text):
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
			out.append(p)
		if return_list:
			return out
		if len(out) == 0:
			return none_text
		return ", ".join(out)

	def _expandTechRows(self, field_name, era_types, parsed_data, techs_per_cell, none_text):
		per_era_chunks = {}
		max_chunks = 1
		for era_type in era_types:
			raw = parsed_data.get(era_type, {}).get(field_name, "")
			items = self._format_tech_list(raw, True, none_text)
			chunks = self._chunkList(items, techs_per_cell)
			if not chunks:
				chunks = [[none_text]]
			per_era_chunks[era_type] = chunks
			if len(chunks) > max_chunks:
				max_chunks = len(chunks)

		rows = []
		# <!-- custom: use numbered field labels so sorting by the Field column keeps Tech rows together; blank labels can jump on sort. (GPT-5.2-Codex) -->
		for i in xrange(max_chunks):
			row = {}
			row["Field"] = "Tech %02d" % (i + 1)
			row["IconKey"] = field_name
			for era_type in era_types:
				chunks = per_era_chunks[era_type]
				if i < len(chunks):
					row[era_type] = ", ".join(chunks[i])
				else:
					row[era_type] = ""
			rows.append(row)
		return rows

	def _chunkList(self, items, size):
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

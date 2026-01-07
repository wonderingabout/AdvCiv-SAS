# --- Game speed chart page for Sevopedia (AdvCiv-SAS) ---
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# Mirrors the handicap chart layout, but for GameSpeedInfo.



from CvPythonExtensions import *
import CvUtil
import re

gc = CyGlobalContext()
localText = CyTranslator()

def _font2(szText):
	return u"<font=2>%s</font>" % unicode(szText)



class SevoPediaGameSpeedChart:
	def __init__(self, main):
		self.top = main
		self._cachedTable = None

		self.MARGIN = 4
		self.ROW_H = 15
		self.W_ICON = 24
		self.W_FIELD = 180
		# Mirror handicap chart behavior: optional icon column controlled by a define.
		# NOTE: Many installs already have SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS but not the
		# game-speed-specific define. To avoid requiring a new define for a cosmetic toggle, we
		# fall back to the handicap define when the game-speed one is 0.
		iHeaderIcons = gc.getDefineINT("SAS_SEVOPEDIA_GAME_SPEED_CHART_HEADER_ICONS")
		if iHeaderIcons == 0:
			iHeaderIcons = gc.getDefineINT("SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS")
		self.IS_SAS_SEVOPEDIA_GAME_SPEED_CHART_HEADER_ICONS = (iHeaderIcons != 0)
		self.bShowIconColumn = self.IS_SAS_SEVOPEDIA_GAME_SPEED_CHART_HEADER_ICONS
		self.TABLE_FILL_PERCENT = gc.getDefineINT("SAS_SEVOPEDIA_GAME_SPEED_CHART_TABLE_FILL_PERCENT")
		if self.TABLE_FILL_PERCENT <= 0:
			raise ValueError("[FATAL] SAS_SEVOPEDIA_GAME_SPEED_CHART_TABLE_FILL_PERCENT must be >= 1.")

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
		if self.IS_SAS_SEVOPEDIA_GAME_SPEED_CHART_HEADER_ICONS:
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
			if self.IS_SAS_SEVOPEDIA_GAME_SPEED_CHART_HEADER_ICONS and iCol == 0:
				colW = self.W_ICON
			elif (self.IS_SAS_SEVOPEDIA_GAME_SPEED_CHART_HEADER_ICONS and iCol == 1) or (not self.IS_SAS_SEVOPEDIA_GAME_SPEED_CHART_HEADER_ICONS and iCol == 0):
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
				if self.IS_SAS_SEVOPEDIA_GAME_SPEED_CHART_HEADER_ICONS and iCol == 0:
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
				elif (self.IS_SAS_SEVOPEDIA_GAME_SPEED_CHART_HEADER_ICONS and iCol == 1) or (not self.IS_SAS_SEVOPEDIA_GAME_SPEED_CHART_HEADER_ICONS and iCol == 0):
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
		# ---------------------------------------------------------------------
		# Central configuration (single source of truth)
		# ---------------------------------------------------------------------
		#
		# row_specs drives:
		# - which XML fields we display (and in what order)
		# - which getter to call for each field (DLL GameSpeedInfo getters)
		# - which icon (glyph/button) is shown in the left icon column
		#
		# This intentionally replaces the older split setup:
		#   field_getters + field_order + icon_token_by_key + glyph_sort_code
		# so future edits only need to touch ONE list.
		#
		# Each entry:
		#   (field_key, getter_name_or_None, icon_spec)
		#
		# icon_spec:
		#   None
		#   ("btn",   <name>)   -> IconsAsButtons.xml (resolved via TXT_KEY_IMAGE_AS_BUTTON_*_PATH)
		#   ("glyph", <name>)   -> GameFont glyph (yield/commerce/symbol char)
		row_specs = (
			("iGrowthPercent",               "getGrowthPercent",               ("glyph", "food")),
			("iTrainPercent",                "getTrainPercent",                ("btn",   "swords")),
			("iConstructPercent",             "getConstructPercent",            ("glyph", "prod")),
			("iCreatePercent",                "getCreatePercent",               ("glyph", "prod")),
			("iResearchPercent",              "getResearchPercent",             ("glyph", "research")),
			("iBuildPercent",                 "getBuildPercent",                ("glyph", "citizen")),
			("iImprovementPercent",           "getImprovementPercent",          ("glyph", "citizen")),
			("iGreatPeoplePercent",           "getGreatPeoplePercent",          ("glyph", "great_people")),
			("iCulturePercent",               "getCulturePercent",              ("glyph", "culture")),
			("iAnarchyPercent",               "getAnarchyPercent",              ("btn",   "fire")),
			("iBarbPercent",                  "getBarbPercent",                 ("btn",   "skull")),
			("iFeatureProductionPercent",     "getFeatureProductionPercent",    ("glyph", "citizen")),
			("iUnitDiscoverPercent",          "getUnitDiscoverPercent",         ("glyph", "research")),
			("iUnitHurryPercent",             "getUnitHurryPercent",            ("glyph", "prod")),
			("iUnitTradePercent",             "getUnitTradePercent",            ("btn",   "swords")),
			("iUnitGreatWorkPercent",         "getUnitGreatWorkPercent",        ("glyph", "culture")),
			("iGoldenAgePercent",             "getGoldenAgePercent",            ("glyph", "golden_age")),
			("iHurryPercent",                 "getHurryPercent",                ("glyph", "prod")),
			("iHurryConscriptAngerPercent",   "getHurryConscriptAngerPercent",  ("glyph", "happy")),
			("iInflationPercent",             "getInflationPercent",            ("glyph", "gold")),
			("iInflationOffset",              "getInflationOffset",             ("glyph", "gold")),
			("iUnitCostPercent",              "getUnitCostPercent",             ("btn",   "swords")),
			("iExtraFreeOutsideUnits",        "getExtraFreeOutsideUnits",       ("btn",   "swords")),
			("iVictoryDelayPercent",          "getVictoryDelayPercent",         ("btn",   "trophy")),
			("iAIMemoryRandPercent",          "getAIMemoryRandPercent",         ("btn",   "brain")),
			("iAIContactRandPercent",         "getAIContactRandPercent",        ("btn",   "dove")),
			("iAIContactDelayPercent",        "getAIContactDelayPercent",       ("btn",   "hourglass")),
			("iFullTradeCreditPercent",       "getFullTradeCreditPercent",      ("glyph", "gold")),
			("iRevoltDivPercent",             "getRevoltDivPercent",            ("btn",   "fire")),
			("iReligionSpreadDivPercent",     "getReligionSpreadDivPercent",    ("btn",   "dove")),
			("iEventRollSidesPercent",        "getEventRollSidesPercent",       ("btn",   "gear")),
			("iVoteIntervalPercent",          "getVoteIntervalPercent",         ("btn",   "dove")),
			("NumTurnIncrements",             None,                             ("btn",   "hourglass")),  # derived
			("TotalTurns",                    None,                             ("btn",   "hourglass")),  # derived
		)

		# ---------------------------------------------------------------------
		# Icon libraries
		# ---------------------------------------------------------------------
		# Each icon definition includes a "sort group" so sorting by the icon column is meaningful.
		# (The group is also embedded into an invisible tie-breaker so ordering is fully deterministic.)
		localText = CyTranslator()
		game = CyGame()

		# Keep icon libraries lean: define only icons we actually use in this chart.
		# If you add new row_specs icons later, extend the *_defs tuples below.
		#
		# Sorting note: each icon gets a "sort group" used only when sorting by the icon column.
		# Groups are spaced by 10 so you can insert new icons between existing groups without
		# renumbering everything; only relative order matters.

		btn_by_name = {}
		# Button icons resolved via TXT_KEY_IMAGE_AS_BUTTON_*_PATH (IconsAsButtons.xml).
		def _btn_path(szTxtKey):
			return CvUtil.convertToStr(localText.getText(szTxtKey, ()))

		_btn_defs = (
			# (name, TXT_KEY_IMAGE_AS_BUTTON_*_PATH)
			("dove",      "TXT_KEY_IMAGE_AS_BUTTON_DOVE_BUTTON_PATH"),
			("swords",    "TXT_KEY_IMAGE_AS_BUTTON_CROSSED_SWORDS_BUTTON_PATH"),
			("skull",     "TXT_KEY_IMAGE_AS_BUTTON_SKULL_BUTTON_PATH"),
			("gear",      "TXT_KEY_IMAGE_AS_BUTTON_GEAR_BUTTON_PATH"),
			("brain",     "TXT_KEY_IMAGE_AS_BUTTON_BRAIN_BUTTON_PATH"),
			("hourglass", "TXT_KEY_IMAGE_AS_BUTTON_HOURGLASS_NOT_DONE_PATH"),
			("fire",      "TXT_KEY_IMAGE_AS_BUTTON_FIRE_BUTTON_PATH"),
			("trophy",    "TXT_KEY_IMAGE_AS_BUTTON_TROPHY_BUTTON_PATH"),
		)
		for i, (name, txtKey) in enumerate(_btn_defs):
			btn_by_name[name] = (_btn_path(txtKey), (i + 1) * 10)

		glyph_by_name = {}
		# GameFont glyph icons (yields/commerce/symbols).
		_glyph_defs = (
			# (name, glyph_char)
			("food",         (u"%c" % (gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar()))),
			("prod",         (u"%c" % (gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar()))),
			("gold",         (u"%c" % (gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar()))),
			("research",     (u"%c" % (gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar()))),
			("culture",      (u"%c" % (gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar()))),
			("happy",        (u"%c" % (game.getSymbolID(FontSymbols.HAPPY_CHAR)))),
			("citizen",      (u"%c" % (game.getSymbolID(FontSymbols.CITIZEN_CHAR)))),
			("great_people", (u"%c" % (game.getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR)))),
			("golden_age",   (u"%c" % (game.getSymbolID(getattr(FontSymbols, "GOLDEN_AGE_CHAR", FontSymbols.GREAT_PEOPLE_CHAR))))),
		)
		for i, (name, glyph) in enumerate(_glyph_defs):
			glyph_by_name[name] = (glyph, (i + 1) * 10)

		# Build a quick lookup dict from the central row_specs list.
		# (Still "centralized": this dict is derived from row_specs rather than hand-maintained.)
		icon_spec_by_key = {}
		for (k, _getter, icon_spec) in row_specs:
			icon_spec_by_key[k] = icon_spec

		# ---------------------------------------------------------------------
		# Stable icon sorting (fixes "emoji order changes / ties shuffle")
		# ---------------------------------------------------------------------
		#
		# Civ4 table sorting uses the raw cell text. If multiple rows share the same icon,
		# tie ordering can shuffle between ascending/descending clicks.
		#
		# We fix ties by appending an invisible sort key (icon_group + row_index) to the icon cell text.
		#
		# IMPORTANT: We avoid ASCII control chars (0x01..0x1F) here. Some Civ4 builds can fail to render
		# *any* glyph in a table cell if such chars are present. This was the root cause of:
		#   "buttons show, but GameFont glyphs (food/citizen/gold/etc) are blank".
		#
		# Instead we use Unicode zero-width/formatting marks (U+200B..U+200F), which are invisible
		# and safe to include in Civ4's UI strings.
		_SORT_DIGITS = (u"\u200b", u"\u200c", u"\u200d", u"\u200e", u"\u200f")  # 5 invisible marks

		def _encode_base5(iValue, iDigits):
			out = []
			for _ in xrange(iDigits):
				out.append(_SORT_DIGITS[iValue % 5])
				iValue //= 5
			out.reverse()
			return u"".join(out)

		def _sort_key(iGroup, iRowIndex):
			# 4 base-5 digits cover up to 624, enough for our "group" numbering (<= 140).
			# 3 digits cover up to 124 rows.
			return u"<font=1>" + _encode_base5(iGroup, 4) + _encode_base5(iRowIndex, 3) + u"</font>"

		def icon_cell_for_key(key, iRowIndex):
			icon_spec = icon_spec_by_key.get(key)

			# Calendar rows are derived fields and not part of row_specs: treat them consistently.
			if key.startswith("Calendar_"):
				icon_spec = ("btn", "hourglass")

			if not icon_spec:
				# No icon: still return a stable, invisible tie-breaker so sorting can't shuffle.
				return (_sort_key(0, iRowIndex), "")

			(kind, name) = icon_spec
			if kind == "btn":
				(path, iGroup) = btn_by_name.get(name, ("", 0))
				return (_sort_key(iGroup, iRowIndex), path)

			# kind == "glyph"
			(glyph, iGroup) = glyph_by_name.get(name, ("", 0))
			return (_font2(glyph) + _sort_key(iGroup, iRowIndex), "")

		# ---------------------------------------------------------------------
		# Extract data from DLL infos
		# ---------------------------------------------------------------------
		# Collect available game speed types in their DLL order.
		speed_types = []
		for i in xrange(gc.getNumGameSpeedInfos()):
			info = gc.getGameSpeedInfo(i)
			speed_types.append(info.getType())

		# Column labels: "Normal (660 / 100%)"
		speed_labels = []
		for i in xrange(gc.getNumGameSpeedInfos()):
			info = gc.getGameSpeedInfo(i)
			szName = self._beautify_enum_name(info.getType())
			iNumInc = info.getNumTurnIncrements()
			iTurns = 0
			for iInc in xrange(iNumInc):
				iTurns += info.getGameTurnInfo(iInc).iNumGameTurnsPerIncrement
			iGrowth = info.getGrowthPercent()
			speed_labels.append("%s (%d / %d%%)" % (szName, iTurns, iGrowth))

		# Fill base fields from getters.
		parsed_data = {}
		for i in xrange(gc.getNumGameSpeedInfos()):
			info = gc.getGameSpeedInfo(i)
			speed_type = info.getType()
			speed_dict = {}

			for (field, getter, _icon_spec) in row_specs:
				if field.startswith("i") and getter:
					speed_dict[field] = str(getattr(info, getter)())

			parsed_data[speed_type] = speed_dict

		# Derived: NumTurnIncrements / TotalTurns, and Calendar_* rows.
		start_year = gc.getDefineINT("START_YEAR")
		max_increments = 0

		for i in xrange(gc.getNumGameSpeedInfos()):
			info = gc.getGameSpeedInfo(i)
			speed_type = info.getType()

			iNumInc = info.getNumTurnIncrements()
			parsed_data[speed_type]["NumTurnIncrements"] = str(iNumInc)
			if iNumInc > max_increments:
				max_increments = iNumInc

			iTotal = 0
			for iInc in xrange(iNumInc):
				iTotal += info.getGameTurnInfo(iInc).iNumGameTurnsPerIncrement
			parsed_data[speed_type]["TotalTurns"] = str(iTotal)

		# Calendar rows: Calendar_01 .. Calendar_NN
		calendar_fields = []
		for iRow in xrange(max_increments):
			# %02d keeps the displayed "Calendar 01" order stable and nicely aligned.
			calendar_fields.append("Calendar_%02d" % (iRow + 1))

		for i in xrange(gc.getNumGameSpeedInfos()):
			info = gc.getGameSpeedInfo(i)
			speed_type = info.getType()

			iNumInc = info.getNumTurnIncrements()
			cum_months = 0
			# Era labels are omitted for compactness (BC is implied before the transition, AD after).
			# To still make the BC->AD boundary obvious, we mark the *first* segment that reaches AD
			# with an arrow ("->") instead of "=".
			bReachedAD = (start_year >= 0)
			for iInc in xrange(iNumInc):
				turn_info = info.getGameTurnInfo(iInc)
				iTurns = turn_info.iNumGameTurnsPerIncrement
				iMonthInc = turn_info.iMonthIncrement

				iSegMonths = iTurns * iMonthInc
				iStartYear = start_year + (cum_months / 12)
				iEndTotal = cum_months + iSegMonths
				iEndYear = start_year + (iEndTotal / 12)
				iEndMonth = (iEndTotal % 12) + 1

				bEraFlip = (not bReachedAD) and (iStartYear < 0) and (iEndYear >= 0)
				szCell = self._format_calendar_segment(iEndYear, iEndMonth, iTurns, iMonthInc, bEraFlip)
				parsed_data[speed_type][calendar_fields[iInc]] = szCell
				cum_months = iEndTotal
				if iEndYear >= 0:
					bReachedAD = True

		# Display order:
		# - base rows (row_specs order)
		# - calendar rows appended right after TotalTurns
		field_order = []
		for (k, _getter, _icon_spec) in row_specs:
			field_order.append(k)
			if k == "TotalTurns":
				field_order.extend(calendar_fields)

		# ---------------------------------------------------------------------
		# Build table
		# ---------------------------------------------------------------------
		table = []
		header = [""]
		if self.bShowIconColumn:
			header.append("")
		for sz in speed_labels:
			header.append(sz)
		table.append(header)

		row_index = 0
		for field in field_order:
			szFieldName = self._beautify_field_name(field)

			if self.bShowIconColumn:
				row = [icon_cell_for_key(field, row_index), _font2(szFieldName)]
			else:
				row = [_font2(szFieldName)]

			for speed_type in speed_types:
				row.append(_font2(parsed_data.get(speed_type, {}).get(field, "")))

			table.append(row)
			row_index += 1

		# Culture level thresholds (scaled by iCulturePercent) appended at bottom.
		for iLevel in xrange(gc.getNumCultureLevelInfos()):
			info = gc.getCultureLevelInfo(iLevel)
			szName = CyTranslator().getText(str(info.getTextKey()), ())

			if self.bShowIconColumn:
				row = [icon_cell_for_key("iCulturePercent", row_index), _font2(szName)]
			else:
				row = [_font2(szName)]

			for iSpeed in xrange(len(speed_types)):
				row.append(_font2(str(info.getSpeedThreshold(iSpeed))))

			table.append(row)
			row_index += 1

		return table

	def _format_year_magnitude(self, iAbsYear):
		# Use k notation only for clean multiples >= 10,000 (so 1,480 BC stays 1480 BC).
		if iAbsYear >= 10000 and (iAbsYear % 1000) == 0:
			return "%dk" % (iAbsYear / 1000)
		return str(iAbsYear)

	def _format_year_label(self, iYear):
		# Compact year label without era text.
		# In the calendar table we omit "BC"/"AD" everywhere:
		# - Before the BC->AD transition, years are implicitly BC.
		# - The first segment that reaches AD is marked with "->" in the cell.
		# - After that, years are implicitly AD.
		if iYear < 0:
			return self._format_year_magnitude(-iYear)
		return self._format_year_magnitude(iYear)

	def _format_date_label(self, iYear, iMonth):
		# Date label: <year>[m2..m12]
		# Month is shown only when it adds information.
		# We omit m1 (January) for concision, but we KEEP m12 (December)
		# because <year>m12 is not the same as <year+1>.
		sz = self._format_year_label(iYear)
		if iMonth == 1:
			return sz
		return "%sm%d" % (sz, iMonth)

	def _format_years_per_turn(self, iYearsPerTurn):
		# Compact: 80 -> "80", 1250 -> "1.2k", 10000 -> "10k"
		if iYearsPerTurn < 1000:
			return str(iYearsPerTurn)
		if (iYearsPerTurn % 1000) == 0:
			return "%dk" % (iYearsPerTurn / 1000)
		if (iYearsPerTurn % 100) == 0:
			sz = "%.1f" % (iYearsPerTurn / 1000.0)
			if sz.endswith(".0"):
				sz = sz[:-2]
			return sz + "k"
		return str(iYearsPerTurn)

	def _format_rate_per_turn(self, month_inc):
		# Returns (op, rate_str):
		# - Exact years: op='*', rate='5' or '10k'
		# - Months < 12: op='*', rate='m6' (so "2*m6" means 2 turns of 6 months)
		# - Year+month: op='*', rate='187m6' (so "2*187m6" means 2 turns of 187 years + 6 months)
		if month_inc <= 0:
			return ("*", "0")
		if month_inc < 12:
			return ("*", "m%d" % month_inc)
		if (month_inc % 12) == 0:
			years_per_turn = month_inc / 12
			return ("*", self._format_years_per_turn(years_per_turn))
		years_per_turn = month_inc / 12
		rem_months = month_inc % 12
		szYears = self._format_years_per_turn(years_per_turn)
		return ("*", "%sm%d" % (szYears, rem_months))

	def _format_calendar_segment(self, end_year, end_month, turns, month_inc, bEraFlip):
		# Calendar cell format is intentionally compact:
		#   "+<turns>*<rate><sep><endDate>"
		# We omit the segment start date entirely to save horizontal space.
		# (The start date is implied by the previous segment; for the first segment,
		#  players already know START_YEAR / can look it up in XML.)
		#
		# Era handling:
		# - We omit "BC"/"AD" text entirely (BC is implied before the transition, AD after).
		# - We mark the *first* segment that reaches AD with "->" (instead of "=") so the
		#   BC->AD boundary is obvious without repeating era text in every cell.
		#   (This is also where years are shortest, so the marker doesn't bloat the row.)
		#
		# Month handling:
		# - Month suffix is shown for m2..m12 (omit m1 only).
		#   We keep m12 (December) because it is meaningfully different from <year+1>.
		#
		# Examples:
		# - "+2*10k=30k"              (still BC; era implied)
		# - "+3*m6->0"                (first segment that reaches AD)
		# - "+3*m6=1901m7"            (later AD; era implied)
		# - "+1*m3=2069m12"           (December is shown; it is not the same as 2070)
		szEnd = self._format_date_label(end_year, end_month)
		(szOp, szRate) = self._format_rate_per_turn(month_inc)
		if bEraFlip:
			szSep = "->"
		else:
			szSep = "="
		return "+%d%s%s%s%s" % (turns, szOp, szRate, szSep, szEnd)



	def _beautify_field_name(self, raw_name):
		# Keep field labels readable; only shorten trailing "Percent" to "%".
		name = raw_name

		# Strip leading 'i' from iFooBar style fields
		if name.startswith("i") and len(name) > 1 and name[1].isupper():
			name = name[1:]

		# Pretty-split underscores / camelCase
		name = re.sub(r"_", " ", name)
		name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)

		# Replace trailing "Percent" with "%"
		if name.endswith("Percent"):
			name = name[:-len("Percent")] + "%"

		return name


	def _beautify_enum_name(self, raw_name):
		name = raw_name
		for prefix in ("TECH_", "HANDICAP_", "GOODY_", "GAMESPEED_"):
			if name.startswith(prefix):
				name = name[len(prefix):]
				break
		name = re.sub(r"_", " ", name)
		return name.title()

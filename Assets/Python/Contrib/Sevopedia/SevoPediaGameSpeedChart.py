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



class SevoPediaGameSpeedChart:
	def __init__(self, main):
		self.top = main
		self._cachedTable = None

		self.MARGIN = 4
		self.ROW_H = 15
		self.W_FIELD = 180
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
			if iCol == 0:
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

				if iCol == 0:
					setCell(table, iCol, iRow, cell, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
				else:
					setCell(table, iCol, iRow, cell, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

	def _getTableData(self):
		if self._cachedTable is not None:
			return self._cachedTable

		data = self._buildTableFromGameData()
		self._cachedTable = data
		return data

	def _buildTableFromGameData(self):
		field_getters = (
			("iGrowthPercent", "getGrowthPercent"),
			("iTrainPercent", "getTrainPercent"),
			("iConstructPercent", "getConstructPercent"),
			("iCreatePercent", "getCreatePercent"),
			("iResearchPercent", "getResearchPercent"),
			("iBuildPercent", "getBuildPercent"),
			("iImprovementPercent", "getImprovementPercent"),
			("iGreatPeoplePercent", "getGreatPeoplePercent"),
			("iCulturePercent", "getCulturePercent"),
			("iAnarchyPercent", "getAnarchyPercent"),
			("iBarbPercent", "getBarbPercent"),
			("iFeatureProductionPercent", "getFeatureProductionPercent"),
			("iUnitDiscoverPercent", "getUnitDiscoverPercent"),
			("iUnitHurryPercent", "getUnitHurryPercent"),
			("iUnitTradePercent", "getUnitTradePercent"),
			("iUnitGreatWorkPercent", "getUnitGreatWorkPercent"),
			("iGoldenAgePercent", "getGoldenAgePercent"),
			("iHurryPercent", "getHurryPercent"),
			("iHurryConscriptAngerPercent", "getHurryConscriptAngerPercent"),
			("iInflationPercent", "getInflationPercent"),
			("iInflationOffset", "getInflationOffset"),
			("iUnitCostPercent", "getUnitCostPercent"),
			("iExtraFreeOutsideUnits", "getExtraFreeOutsideUnits"),
			("iVictoryDelayPercent", "getVictoryDelayPercent"),
			("iAIMemoryRandPercent", "getAIMemoryRandPercent"),
			("iAIContactRandPercent", "getAIContactRandPercent"),
			("iAIContactDelayPercent", "getAIContactDelayPercent"),
			("iFullTradeCreditPercent", "getFullTradeCreditPercent"),
			("iRevoltDivPercent", "getRevoltDivPercent"),
			("iReligionSpreadDivPercent", "getReligionSpreadDivPercent"),
			("iEventRollSidesPercent", "getEventRollSidesPercent"),
			("iVoteIntervalPercent", "getVoteIntervalPercent"),
		)

		field_order = [
			"iGrowthPercent",
			"iTrainPercent",
			"iConstructPercent",
			"iCreatePercent",
			"iResearchPercent",
			"iBuildPercent",
			"iImprovementPercent",
			"iGreatPeoplePercent",
			"iCulturePercent",
			"iAnarchyPercent",
			"iBarbPercent",
			"iFeatureProductionPercent",
			"iUnitDiscoverPercent",
			"iUnitHurryPercent",
			"iUnitTradePercent",
			"iUnitGreatWorkPercent",
			"iGoldenAgePercent",
			"iHurryPercent",
			"iHurryConscriptAngerPercent",
			"iInflationPercent",
			"iInflationOffset",
			"iUnitCostPercent",
			"iExtraFreeOutsideUnits",
			"iVictoryDelayPercent",
			"iAIMemoryRandPercent",
			"iAIContactRandPercent",
			"iAIContactDelayPercent",
			"iFullTradeCreditPercent",
			"iRevoltDivPercent",
			"iReligionSpreadDivPercent",
			"iEventRollSidesPercent",
			"iVoteIntervalPercent",
			"NumTurnIncrements",
			"TotalTurns",
		]

		max_increments = 0
		start_year = gc.getDefineINT("START_YEAR")

		# <!-- custom: fail fast if the DLL doesn't expose required CvGameSpeedInfo getters for the game speed chart. (GPT-5.2-Codex) -->
		if gc.getNumGameSpeedInfos() > 0:
			info = gc.getGameSpeedInfo(0)
			missing = []
			for field_name, getter_name in field_getters:
				if not hasattr(info, getter_name):
					missing.append(getter_name)
			if not hasattr(info, "getNumTurnIncrements") or not hasattr(info, "getGameTurnInfo"):
				missing.append("getNumTurnIncrements/getGameTurnInfo")
			if missing:
				raise RuntimeError("[FATAL] Your mod DLL does not expose the required CvGameSpeedInfo Python getters: %s. Please expose them in CyInfoInterface2.cpp and rebuild the DLL." % ", ".join(missing))

		parsed_data = {}
		speed_types = []
		speed_labels = []

		for iSpeed in xrange(gc.getNumGameSpeedInfos()):
			info = gc.getGameSpeedInfo(iSpeed)
			speed_type = info.getType()
			speed_label = info.getDescription()
			speed_types.append(speed_type)
			speed_labels.append(speed_label)
			speed_dict = {}

			for field_name, getter_name in field_getters:
				getter = getattr(info, getter_name)
				value = getter()
				speed_dict[field_name] = str(value)

			num_increments = info.getNumTurnIncrements()
			if num_increments > max_increments:
				max_increments = num_increments
			total_turns = 0
			cum_months = 0
			for i in xrange(num_increments):
				turn_info = info.getGameTurnInfo(i)
				turns = turn_info.iNumGameTurnsPerIncrement
				month_inc = turn_info.iMonthIncrement
				total_turns = total_turns + turns

				seg_start_year = start_year + (cum_months / 12)
				cum_months = cum_months + (month_inc * turns)
				seg_end_year = start_year + (cum_months / 12)
				years_per_turn = month_inc / 12
				speed_dict["Calendar_%02d" % (i + 1)] = self._format_calendar_segment(seg_start_year, seg_end_year, turns, years_per_turn)

			speed_dict["NumTurnIncrements"] = str(num_increments)
			speed_dict["TotalTurns"] = str(total_turns)

			parsed_data[speed_type] = speed_dict

		# Append one row per calendar segment (iMonthIncrement block) across all game speeds.
		# Some speeds may have fewer segments; their trailing cells will remain blank.
		try:
			insert_at = field_order.index("TotalTurns") + 1
		except:
			insert_at = len(field_order)
		calendar_fields = []
		for i in xrange(max_increments):
			calendar_fields.append("Calendar_%02d" % (i + 1))
		field_order[insert_at:insert_at] = calendar_fields

		# --------------------------------------------------------------------
		# One-time render prep (kept local; cache stores only final table cells)
		# --------------------------------------------------------------------
		def _font2(s):
			return u"<font=2>%s</font>" % s

		# Build header (pre-fonted)
		header = [_font2("Field")]
		for i in xrange(len(speed_types)):
			speed = speed_types[i]
			label = speed_labels[i]
			if not label:
				label = self._beautify_enum_name(speed)
			header.append(_font2(label))

		data = [header]

		# Build rows (pre-fonted)
		for field in field_order:
			row = [_font2(self._beautify_field_name(field))]
			for speed in speed_types:
				value = ""
				if speed in parsed_data:
					value = parsed_data[speed].get(field, "")
				row.append(_font2(value))
			data.append(row)

		# Append culture level thresholds per game speed
		for iLevel in xrange(gc.getNumCultureLevelInfos()):
			info = gc.getCultureLevelInfo(iLevel)
			label = info.getDescription()
			if not label:
				label = self._beautify_enum_name(info.getType())
			row = [_font2(label)]
			for iSpeed in xrange(gc.getNumGameSpeedInfos()):
				row.append(_font2(str(info.getSpeedThreshold(iSpeed))))
			data.append(row)

		return data

	def _format_year_magnitude(self, iAbsYear):
		# Use k notation only for clean multiples >= 10,000 (so 1,480 BC stays 1480 BC).
		if iAbsYear >= 10000 and (iAbsYear % 1000) == 0:
			return "%dk" % (iAbsYear / 1000)
		return str(iAbsYear)

	def _format_year_label(self, iYear):
		# Compact: "50kBC" / "1900AD" (treat year 0 as AD for readability)
		if iYear < 0:
			return "%sBC" % self._format_year_magnitude(-iYear)
		return "%sAD" % self._format_year_magnitude(iYear)



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


	def _format_calendar_segment(self, start_year, end_year, turns, years_per_turn):
		# Compact, cell-friendly timeline string.
		# Example: "50kBC+(2T*10k)=30kAD"
		szStart = self._format_year_label(start_year)
		szEnd = self._format_year_label(end_year)
		szRate = self._format_years_per_turn(years_per_turn)
		return "%s+%d*%s=%s" % (szStart, turns, szRate, szEnd)



	def _beautify_field_name(self, raw_name):
		# Make the Field column compact: remove spaces, replace "Percent" with "%", and shorten some long labels.
		name = raw_name

		# Calendar segment rows (Calendar_01 -> Cal01)
		if name.startswith("Calendar_"):
			try:
				return "Cal%s" % name.split("_", 1)[1]
			except:
				return "Cal"

		# Shorten a few very long core labels
		if name == "NumTurnIncrements":
			return "NumInc"
		if name == "TotalTurns":
			return "TotalT"

		# Strip leading 'i' from iFooBar style fields
		if name.startswith("i") and len(name) > 1 and name[1].isupper():
			name = name[1:]

		# Pretty-split underscores / camelCase, then compact
		name = re.sub(r"_", " ", name)
		name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)

		# Replace Percent -> % and remove all spaces to free width
		name = name.replace("Percent", "%")
		name = name.replace(" ", "")

		return name


	def _beautify_enum_name(self, raw_name):
		name = raw_name
		for prefix in ("TECH_", "HANDICAP_", "GOODY_", "GAMESPEED_"):
			if name.startswith(prefix):
				name = name[len(prefix):]
				break
		name = re.sub(r"_", " ", name)
		return name.title()

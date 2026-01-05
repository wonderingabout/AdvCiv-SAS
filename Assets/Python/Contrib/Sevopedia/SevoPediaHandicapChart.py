# --- Handicap chart page for Sevopedia (AdvCiv-SAS) ---
# Created as part of AdvCiv-SAS improvements
# (c) 2025 wonderingabout & AI helpers (see Authors in root README.md)
#
# Based on the Middle-earth mod's PlatyPedia handicap approach: pull values from
# CvHandicapInfo getters (rather than XML parsing) for Python 2.4 compatibility.
#
# <!-- custom: note: pending issue of img being left-aligned but couldn't fix it for now, i believe the advantage of being able to sort by emoji i.e. theme outweighs this downside so left as such for now. -->



from CvPythonExtensions import *
import CvUtil
import re

gc = CyGlobalContext()
localText = CyTranslator()



class SevoPediaHandicapChart:
	def __init__(self, main):
		self.top = main
		self._cachedTable = None

		self.MARGIN = 4
		self.ROW_H = 15
		self.W_ICON = 24
		self.W_FIELD = 290
		self.TABLE_FILL_PERCENT = gc.getDefineINT("SAS_SEVOPEDIA_HANDICAP_CHART_TABLE_FILL_PERCENT")
		if self.TABLE_FILL_PERCENT <= 0:
			raise ValueError("[FATAL] SAS_SEVOPEDIA_HANDICAP_CHART_TABLE_FILL_PERCENT must be >= 1.")
		self.IS_SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS = (gc.getDefineINT("SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS") != 0)

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
		if self.IS_SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS:
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
			if self.IS_SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS and iCol == 0:
				colW = self.W_ICON
			elif (self.IS_SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS and iCol == 1) or (not self.IS_SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS and iCol == 0):
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
				if self.IS_SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS and iCol == 0:
					if isinstance(cell, tuple):
						text = cell[0]
						icon_button = cell[1]
					else:
						text = cell
						icon_button = ""
					setCell(table, iCol, iRow, text, icon_button, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

				# Field column (left)
				elif (self.IS_SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS and iCol == 1) or (not self.IS_SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS and iCol == 0):
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
		field_getters = (
			("iAIAttitudeChangePercent", "getAIAttitudeChangePercent"),
			("iAIAdvancedStartPercent", "getAIAdvancedStartPercent"),
			("iAIAnimalBonus", "getAIAnimalCombatModifier"),
			("iAIBarbarianBonus", "getAIBarbarianCombatModifier"),
			("iAICivicUpkeepPercent", "getAICivicUpkeepPercent"),
			("iAIConstructPercent", "getAIConstructPercent"),
			("iAICreatePercent", "getAICreatePercent"),
			("iAIDeclareWarProb", "getAIDeclareWarProb"),
			("iAIGPThresholdPercent", "getAIGPThresholdPercent"),
			("iAIGrowthPercent", "getAIGrowthPercent"),
			("iAIHandicapIncrementTurns", "getAIHandicapIncrementTurns"),
			("iAIInflationPercent", "getAIInflationPercent"),
			("iAIResearchPercent", "getAIResearchPercent"),
			("iAIStartingDefenseUnits", "getAIStartingDefenseUnits"),
			("iAIStartingExploreUnits", "getAIStartingExploreUnits"),
			("iAIStartingUnitMultiplier", "getAIStartingUnitMultiplier"),
			("iAIStartingWorkerUnits", "getAIStartingWorkerUnits"),
			("iAITrainPercent", "getAITrainPercent"),
			("iAIUnitCostPercent", "getAIUnitCostPercent"),
			("iAIUnitSupplyPercent", "getAIUnitSupplyPercent"),
			("iAIUnitUpgradePercent", "getAIUnitUpgradePercent"),
			("iAIWarWearinessPercent", "getAIWarWearinessPercent"),
			("iAIWorkRateModifier", "getAIWorkRateModifier"),
			("iAIWorldConstructPercent", "getAIWorldConstructPercent"),
			("iAIWorldCreatePercent", "getAIWorldCreatePercent"),
			("iAIWorldTrainPercent", "getAIWorldTrainPercent"),
			("iAdvancedStartPointsMod", "getAdvancedStartPointsMod"),
			("iAnimalAttackProb", "getAnimalAttackProb"),
			("iAnimalBonus", "getAnimalCombatModifier"),
			("iAttitudeChange", "getAttitudeChange"),
			("iBarbarianBonus", "getBarbarianCombatModifier"),
			("iBarbarianCityAttackBonus", "getBarbarianCityAttackBonus"),
			("iBarbarianCityCreationProb", "getBarbarianCityCreationProb"),
			("iBarbarianCityCreationTurnsElapsed", "getBarbarianCityCreationTurnsElapsed"),
			("iBarbarianCreationTurnsElapsed", "getBarbarianCreationTurnsElapsed"),
			("iBarbarianDefenders", "getBarbarianInitialDefenders"),
			("iBaseGrowthThresholdPercent", "getBaseGrowthThresholdPercent"),
			("iBuildTimePercent", "getBuildTimePercent"),
			("iCivicUpkeepPercent", "getCivicUpkeepPercent"),
			("iColonyMaintenancePercent", "getColonyMaintenancePercent"),
			("iConstructPercent", "getConstructPercent"),
			("iCorporationMaintenancePercent", "getCorporationMaintenancePercent"),
			("iCreatePercent", "getCreatePercent"),
			("iCultureLevelPercent", "getCultureLevelPercent"),
			("iDifficulty", "getDifficulty"),
			("iDistanceMaintenancePercent", "getDistanceMaintenancePercent"),
			("iForeignCultureStrength", "getForeignCultureStrength"),
			("iFreeUnits", "getFreeUnits"),
			("iFreeWinsVsBarbs", "getFreeWinsVsBarbs"),
			("iGold", "getStartingGold"),
			("iGPThresholdPercent", "getGPThresholdPercent"),
			("iHappyBonus", "getHappyBonus"),
			("iHealthBonus", "getHealthBonus"),
			("iInflationPercent", "getInflationPercent"),
			("iMaxColonyMaintenance", "getMaxColonyMaintenance"),
			("iMaxNumCitiesMaintenance", "getMaxNumCitiesMaintenance"),
			("iNoTechTradeModifier", "getNoTechTradeModifier"),
			("iNumCitiesMaintenancePercent", "getNumCitiesMaintenancePercent"),
			("iResearchPercent", "getResearchPercent"),
			("iSeaBarbarianBonus", "getSeaBarbarianBonus"),
			("iSeaBarbarianExtraMoves", "getSeaBarbarianExtraMoves"),
			("iStartingDefenseUnits", "getStartingDefenseUnits"),
			("iStartingExploreUnits", "getStartingExploreUnits"),
			("iStartingLocPercent", "getStartingLocationPercent"),
			("iStartingWorkerUnits", "getStartingWorkerUnits"),
			("iTechTradeKnownModifier", "getTechTradeKnownModifier"),
			("iTrainPercent", "getTrainPercent"),
			("iUnitCostPercent", "getUnitCostPercent"),
			("iUnownedTilesPerBarbarianCity", "getUnownedTilesPerBarbarianCity"),
			("iUnownedTilesPerBarbarianUnit", "getUnownedTilesPerBarbarianUnit"),
			("iUnownedTilesPerGameAnimal", "getUnownedTilesPerGameAnimal"),
			("iUnownedWaterTilesPerBarbarianUnit", "getUnownedWaterTilesPerBarbarianUnit"),
		)

		# <!-- custom: fail fast if the DLL doesn't expose required CvHandicapInfo getters for the handicap chart. (GPT-5.2-Codex) -->
		if gc.getNumHandicapInfos() > 0:
			info = gc.getHandicapInfo(0)
			missing = []
			for field_name, getter_name in field_getters:
				if not hasattr(info, getter_name):
					missing.append(getter_name)
			if missing:
				raise RuntimeError("[FATAL] Your mod DLL does not expose the required CvHandicapInfo Python getters: %s. Please expose them in CyInfoInterface2.cpp and rebuild the DLL." % ", ".join(missing))

		goody_types = (
			"GOODY_LOW_GOLD",
			"GOODY_HIGH_GOLD",
			"GOODY_MAP",
			"GOODY_SETTLER",
			"GOODY_WARRIOR",
			"GOODY_SCOUT",
			"GOODY_WORKER",
			"GOODY_EXPERIENCE",
			"GOODY_HEALING",
			"GOODY_TECH",
			"GOODY_BARBARIANS_WEAK",
			"GOODY_BARBARIANS_STRONG",
		)
		goody_groups = (
			("Goody Gold (Low / High)", ("GOODY_LOW_GOLD", "GOODY_HIGH_GOLD")),
			("Goody (Experience / Healing)", ("GOODY_EXPERIENCE", "GOODY_HEALING")),
			("Goody (Map / Tech)", ("GOODY_MAP", "GOODY_TECH")),
			("Goody (Scout / Warrior)", ("GOODY_SCOUT", "GOODY_WARRIOR")),
			("Goody (Worker / Settler)", ("GOODY_WORKER", "GOODY_SETTLER")),
			("Goody Barbarians (Weak / Strong)", ("GOODY_BARBARIANS_WEAK", "GOODY_BARBARIANS_STRONG")),
		)

		anchor_field = gc.getDefineSTRING("SAS_SEVOPEDIA_HANDICAP_CHART_ANCHOR_FIELD")
		if not anchor_field:
			raise ValueError("[FATAL] Missing SAS_SEVOPEDIA_HANDICAP_CHART_ANCHOR_FIELD define.")

		abbrev_tech_names = {
			"Animal Husbandry": "Animal H.",
			"Bronze Working": "Bronze W.",
			"Iron Working": "Iron W.",
			"Industrialism": "Industr.",
		}
		techs_per_cell = 1
		none_text = localText.getText("TXT_KEY_PEDIA_SAS_HANDICAP_CHART_FREE_TECHS_NONE", ())

		# Collect tech types once.
		tech_types = []
		for iTech in xrange(gc.getNumTechInfos()):
			tech_types.append(gc.getTechInfo(iTech).getType())

		all_fields = {}
		parsed_data = {}
		difficulty_types = []

		for iHandicap in xrange(gc.getNumHandicapInfos()):
			info = gc.getHandicapInfo(iHandicap)
			handicap_type = info.getType()
			difficulty_types.append(handicap_type)
			handicap_dict = {}

			for field_name, getter_name in field_getters:
				getter = getattr(info, getter_name)
				value = getter()
				handicap_dict[field_name] = str(value)
				all_fields[field_name] = 1

			self._appendGoodyFields(handicap_dict, info, all_fields, goody_types)
			self._appendFreeTechFields(handicap_dict, info, all_fields, tech_types)

			parsed_data[handicap_type] = handicap_dict

		fields = all_fields.keys()
		fields.sort()

		goody_fields = []
		for gt in goody_types:
			if gt in all_fields:
				goody_fields.append(gt)

		rows = []
		for field in fields:
			row = {"Field": field, "IconKey": field}
			for difficulty in difficulty_types:
				value = ""
				if difficulty in parsed_data:
					value = parsed_data[difficulty].get(field, "")
				row[difficulty] = value
			rows.append(row)

		rows = self._mergeHumanAiRows(rows, difficulty_types, none_text)

		before = []
		goody_rows = []
		nested = []
		for row in rows:
			if row["Field"] in goody_fields:
				goody_rows.append(row)
			elif row["Field"] in ("AIFreeTechs", "FreeTechs"):
				nested.append(row)
			else:
				before.append(row)

		if goody_rows:
			goody_rows_by_field = {}
			for grow in goody_rows:
				goody_rows_by_field[grow["Field"]] = grow

			grouped_goody_rows = []
			skipped_goody_fields = {}
			for label, (goody_left, goody_right) in goody_groups:
				left_row = goody_rows_by_field.get(goody_left)
				right_row = goody_rows_by_field.get(goody_right)
				if left_row is None or right_row is None:
					continue
				new_row = {"Field": label, "IconKey": label}
				for difficulty in difficulty_types:
					left_val = left_row.get(difficulty, "0")
					right_val = right_row.get(difficulty, "0")
					new_row[difficulty] = "%s / %s" % (left_val, right_val)
				grouped_goody_rows.append(new_row)
				skipped_goody_fields[goody_left] = True
				skipped_goody_fields[goody_right] = True

			for grow in goody_rows:
				if grow["Field"] not in skipped_goody_fields:
					grouped_goody_rows.append(grow)

			goody_rows = grouped_goody_rows

		new_rows = []
		for row in before:
			new_rows.append(row)
			if row["Field"] == anchor_field:
				for grow in goody_rows:
					new_rows.append(grow)
				for nrow in nested:
					new_rows.append(nrow)
		if new_rows == before:
			for grow in goody_rows:
				new_rows.append(grow)
			for nrow in nested:
				new_rows.append(nrow)

		rows = self._expandTechRows(new_rows, difficulty_types, techs_per_cell, none_text, abbrev_tech_names)

		# --------------------------------------------------------------------
		# One-time render prep (kept local; cache stores only final table cells)
		# --------------------------------------------------------------------
		def _font2(s):
			return u"<font=2>%s</font>" % s

		def _sort_char(code):
			# Clamp to 1..31; match old behavior (default 31 for unknown/non-positive).
			if code <= 0:
				code = 31
			elif code > 31:
				code = 31
			return u"<font=1>%c</font>" % code

		icon_cell_for_key = None
		if self.IS_SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS:
			game = CyGame()

			# Glyph icons (FontSymbols / commerce / yields)
			glyph_by_name = {
				"great_people": u"%c" % game.getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR),
				"research": u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar(),
				"gold": u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar(),
				"culture": u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar(),
				"happy": u"%c" % game.getSymbolID(FontSymbols.HAPPY_CHAR),
				"health": u"%c" % game.getSymbolID(FontSymbols.HEALTHY_CHAR),
				"food": u"%c" % gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar(),
				"prod": u"%c" % gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar(),
				"defense": u"%c" % game.getSymbolID(FontSymbols.DEFENSE_CHAR),
				"citizen": u"%c" % game.getSymbolID(FontSymbols.CITIZEN_CHAR),
			}

			# Button icons (path must be narrow str for setTableText)
			btn_by_name = {
				"swords": (CvUtil.convertToStr(localText.getText("TXT_KEY_IMAGE_AS_BUTTON_CROSSED_SWORDS_BUTTON_PATH", ())), 2),
				"skull": (CvUtil.convertToStr(localText.getText("TXT_KEY_IMAGE_AS_BUTTON_SKULL_BUTTON_PATH", ())), 3),
				"lion": (CvUtil.convertToStr(localText.getText("TXT_KEY_IMAGE_AS_BUTTON_LION_FACE_BUTTON_PATH", ())), 4),
				"dove": (CvUtil.convertToStr(localText.getText("TXT_KEY_IMAGE_AS_BUTTON_DOVE_BUTTON_PATH", ())), 10),
			}

			# Token map: key -> "btn:name" or "glyph:name"
			icon_token_by_key = {
				"iAIAttitudeChangePercent": "btn:dove",
				"iAIAdvancedStartPercent": "glyph:defense",
				"iAIAnimalBonus": "btn:lion",
				"iAIBarbarianBonus": "btn:skull",
				"iAICivicUpkeepPercent": "glyph:gold",
				"iAIConstructPercent": "glyph:prod",
				"iAICreatePercent": "glyph:prod",
				"iAIDeclareWarProb": "btn:swords",
				"iAIGPThresholdPercent": "glyph:great_people",
				"iAIGrowthPercent": "glyph:food",
				"iAIHandicapIncrementTurns": "glyph:defense",
				"iAIInflationPercent": "glyph:gold",
				"iAIResearchPercent": "glyph:research",
				"iAIStartingDefenseUnits": "btn:swords",
				"iAIStartingExploreUnits": "btn:swords",
				"iAIStartingUnitMultiplier": "btn:swords",
				"iAIStartingWorkerUnits": "glyph:citizen",
				"iAITrainPercent": "btn:swords",
				"iAIUnitCostPercent": "btn:swords",
				"iAIUnitSupplyPercent": "btn:swords",
				"iAIUnitUpgradePercent": "btn:swords",
				"iAIWarWearinessPercent": "btn:swords",
				"iAIWorkRateModifier": "glyph:citizen",
				"iAIWorldConstructPercent": "glyph:prod",
				"iAIWorldCreatePercent": "glyph:prod",
				"iAIWorldTrainPercent": "btn:swords",
				"iAdvancedStartPointsMod": "glyph:defense",
				"iAnimalAttackProb": "btn:lion",
				"iAnimalBonus": "btn:lion",
				"iAttitudeChange": "btn:dove",
				"iBarbarianBonus": "btn:skull",
				"iBarbarianCityAttackBonus": "btn:skull",
				"iBarbarianCityCreationProb": "btn:skull",
				"iBarbarianCityCreationTurnsElapsed": "btn:skull",
				"iBarbarianCreationTurnsElapsed": "btn:skull",
				"iBarbarianDefenders": "btn:skull",
				"iBaseGrowthThresholdPercent": "glyph:food",
				"iBuildTimePercent": "glyph:citizen",
				"iCivicUpkeepPercent": "glyph:gold",
				"iColonyMaintenancePercent": "glyph:gold",
				"iConstructPercent": "glyph:prod",
				"iCorporationMaintenancePercent": "glyph:gold",
				"iCreatePercent": "glyph:prod",
				"iCultureLevelPercent": "glyph:culture",
				"iDifficulty": "glyph:defense",
				"iDistanceMaintenancePercent": "glyph:gold",
				"iForeignCultureStrength": "glyph:culture",
				"iFreeUnits": "btn:swords",
				"iFreeWinsVsBarbs": "btn:skull",
				"iGold": "glyph:gold",
				"iGPThresholdPercent": "glyph:great_people",
				"iHappyBonus": "glyph:happy",
				"iHealthBonus": "glyph:health",
				"iInflationPercent": "glyph:gold",
				"iMaxColonyMaintenance": "glyph:gold",
				"iMaxNumCitiesMaintenance": "glyph:gold",
				"iNoTechTradeModifier": "glyph:research",
				"iNumCitiesMaintenancePercent": "glyph:gold",
				"iResearchPercent": "glyph:research",
				"iSeaBarbarianBonus": "btn:skull",
				"iSeaBarbarianExtraMoves": "btn:skull",
				"iStartingDefenseUnits": "btn:swords",
				"iStartingExploreUnits": "btn:swords",
				"iStartingLocPercent": "glyph:defense",
				"iStartingWorkerUnits": "glyph:citizen",
				"iTechTradeKnownModifier": "glyph:research",
				"iTrainPercent": "btn:swords",
				"iUnitCostPercent": "btn:swords",
				"iUnownedTilesPerBarbarianCity": "btn:skull",
				"iUnownedTilesPerBarbarianUnit": "btn:skull",
				"iUnownedTilesPerGameAnimal": "btn:lion",
				"iUnownedWaterTilesPerBarbarianUnit": "btn:skull",
				"Goody Gold (Low / High)": "glyph:gold",
				"Goody (Experience / Healing)": "btn:swords",
				"Goody (Map / Tech)": "glyph:research",
				"Goody (Scout / Warrior)": "btn:swords",
				"Goody (Worker / Settler)": "glyph:citizen",
				"Goody Barbarians (Weak / Strong)": "btn:skull",
				"FreeTechs": "glyph:research",
				"AIFreeTechs": "glyph:research",
			}

			def icon_cell_for_key(icon_key):
				if not icon_key:
					return (u"", "")
				token = icon_token_by_key.get(icon_key, "")
				if not token:
					return (u"", "")
				if token.startswith("btn:"):
					name = token[4:]
					btn = btn_by_name.get(name)
					if btn is None:
						return (u"", "")
					path, sort_code = btn[0], btn[1]
					if not path:
						return (u"", "")
					return (_sort_char(sort_code), path)
				if token.startswith("glyph:"):
					name = token[6:]
					glyph = glyph_by_name.get(name, u"")
					if not glyph:
						return (u"", "")
					return (_font2(glyph), "")
				return (u"", "")

		# Build header (pre-fonted)
		if self.IS_SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS:
			header = [u"", _font2("Field")]
		else:
			header = [_font2("Field")]
		for difficulty in difficulty_types:
			header.append(_font2(self._beautify_enum_name(difficulty)))

		data = [header]

		# Build rows (pre-fonted)
		for row in rows:
			field_name = row["Field"]
			display_field = field_name

			if self.IS_SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS:
				icon_key = row.get("IconKey", "")
				icon_cell = (u"", "")
				if icon_cell_for_key is not None:
					icon_cell = icon_cell_for_key(icon_key)
				out_row = [icon_cell, _font2(display_field)]
			else:
				out_row = [_font2(display_field)]

			for difficulty in difficulty_types:
				value = row.get(difficulty, "")
				if row["Field"] in ("FreeTechs", "AIFreeTechs"):
					value = self._format_tech_list(value, False, none_text, abbrev_tech_names)
				out_row.append(_font2(value))

			data.append(out_row)

		return data

	def _appendGoodyFields(self, handicap_dict, info, all_fields, goody_types):
		goody_counts = {}
		for gt in goody_types:
			goody_counts[gt] = 0

		try:
			num_goodies = info.getNumGoodies()
		except:
			num_goodies = 0

		for i in xrange(num_goodies):
			try:
				i_goody = info.getGoodies(i)
			except:
				i_goody = -1
			if i_goody >= 0:
				goody_info = gc.getGoodyInfo(i_goody)
				goody_type = goody_info.getType()
				if goody_type in goody_counts:
					goody_counts[goody_type] = goody_counts[goody_type] + 1

		for gt in goody_types:
			handicap_dict[gt] = str(goody_counts.get(gt, 0))
			all_fields[gt] = 1

	def _appendFreeTechFields(self, handicap_dict, info, all_fields, tech_types):
		free_list = []
		ai_free_list = []
		for iTech in xrange(len(tech_types)):
			tech_type = tech_types[iTech]
			if info.isFreeTechs(iTech):
				free_list.append(tech_type)
			if info.isAIFreeTechs(iTech):
				ai_free_list.append(tech_type)

		handicap_dict["FreeTechs"] = ", ".join(free_list)
		handicap_dict["AIFreeTechs"] = ", ".join(ai_free_list)
		all_fields["FreeTechs"] = 1
		all_fields["AIFreeTechs"] = 1

	def _beautify_enum_name(self, raw_name):
		name = raw_name
		for prefix in ("TECH_", "HANDICAP_", "GOODY_"):
			if name.startswith(prefix):
				name = name[len(prefix):]
				break
		name = re.sub(r"_", " ", name)
		return name.title()

	def _mergeHumanAiRows(self, rows, difficulty_types, none_text):
		row_by_field = {}
		for row in rows:
			row_by_field[row["Field"]] = row

		merged = []
		skip_fields = {}
		for row in rows:
			field = row["Field"]
			if field in skip_fields:
				continue
			if field.startswith("iAI"):
				human_field = "i" + field[3:]
				if human_field in row_by_field:
					continue
				merged.append(row)
				continue
			if not field.startswith("i"):
				merged.append(row)
				continue

			ai_field = "iAI" + field[1:]
			ai_row = row_by_field.get(ai_field)
			if ai_row is None:
				merged.append(row)
				continue

			label = self._humanAiLabel(field)
			new_row = {"Field": label, "IconKey": row.get("IconKey", "")}
			for difficulty in difficulty_types:
				human_val = row.get(difficulty, "")
				ai_val = ai_row.get(difficulty, "")
				if not human_val:
					human_val = none_text
				if not ai_val:
					ai_val = none_text
				new_row[difficulty] = "%s / %s" % (human_val, ai_val)
			merged.append(new_row)
			skip_fields[ai_field] = True
		return merged

	def _humanAiLabel(self, field):
		base = field
		if base.startswith("i"):
			base = base[1:]
		base = re.sub(r"([a-z])([A-Z])", r"\1 \2", base)
		return base + " (Human / AI)"

	def _format_tech_list(self, value, return_list, none_text, abbrev_tech_names):
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
			name = self._beautify_enum_name(p)
			name = abbrev_tech_names.get(name, name)
			out.append(name)
		if return_list:
			return out
		if len(out) == 0:
			return none_text
		return ", ".join(out)

	def _expandTechRows(self, rows, difficulty_types, techs_per_cell, none_text, abbrev_tech_names):
		new_rows = []
		for row in rows:
			field = row["Field"]
			if field not in ("FreeTechs", "AIFreeTechs"):
				new_rows.append(row)
				continue

			per_diff_chunks = {}
			max_chunks = 1
			for difficulty in difficulty_types:
				raw = row.get(difficulty, "")
				items = self._format_tech_list(raw, True, none_text, abbrev_tech_names)
				chunks = self._chunkList(items, techs_per_cell)
				if not chunks:
					chunks = [[none_text]]
				per_diff_chunks[difficulty] = chunks
				if len(chunks) > max_chunks:
					max_chunks = len(chunks)

			for i in xrange(max_chunks):
				new_row = {}
				if i == 0:
					new_row["Field"] = field
					new_row["IconKey"] = field
				else:
					new_row["Field"] = ""
					new_row["IconKey"] = ""
				for difficulty in difficulty_types:
					chunks = per_diff_chunks[difficulty]
					if i < len(chunks):
						new_row[difficulty] = ", ".join(chunks[i])
					else:
						new_row[difficulty] = ""
				new_rows.append(new_row)
		return new_rows

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

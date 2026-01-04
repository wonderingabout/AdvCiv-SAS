# --- Handicap chart page for Sevopedia (AdvCiv-SAS) ---
# Created as part of AdvCiv-SAS improvements
# (c) 2025 wonderingabout & AI helpers (see Authors in root README.md)
#
# Based on the Middle-earth mod's PlatyPedia handicap approach: pull values from
# CvHandicapInfo getters (rather than XML parsing) for Python 2.4 compatibility.
#

from CvPythonExtensions import *
import CvUtil
import re

gc = CyGlobalContext()
localText = CyTranslator()


class SevoPediaHandicapChart:
	def __init__(self, main):
		self.top = main
		self._cachedTable = None

		self.MARGIN = 12
		self.ROW_H = 28
		self.W_FIELD = 340

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

		remainingW = max(0, tableW - self.W_FIELD)
		wNum = remainingW / (nCols - 1)

		screen.addTableControlGFC(table, nCols, tableX, tableY, tableW, tableH, True, False, self.ROW_H, self.ROW_H, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSort(table)

		for iCol in range(nCols):
			if iCol == 0:
				colW = self.W_FIELD
			else:
				colW = wNum
			label = u"<font=2>" + header[iCol] + u"</font>"
			screen.setTableColumnHeader(table, iCol, label, colW)

		for row in rows:
			iRow = screen.appendTableRow(table)
			for iCol in range(nCols):
				if iCol < len(row):
					cell = row[iCol]
				else:
					cell = u""
				text = u"<font=2>" + cell + u"</font>"
				if iCol == 0:
					screen.setTableText(table, iCol, iRow, text, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
				else:
					screen.setTableText(table, iCol, iRow, text, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

	def _getTableData(self):
		if self._cachedTable is not None:
			return self._cachedTable

		data = []
		try:
			data = self._buildTableFromGameData()
		except:
			data = []

		self._cachedTable = data
		return data

	def _buildTableFromGameData(self):
		field_getters = (
			("iAIAttitudeChangePercent", "getAIAttitudeChangePercent"),
			("iAIAdvancedStartPercent", "getAIAdvancedStartPercent"),
			("iAIAnimalCombatModifier", "getAIAnimalCombatModifier"),
			("iAIBarbarianCombatModifier", "getAIBarbarianCombatModifier"),
			("iAICivicUpkeepPercent", "getAICivicUpkeepPercent"),
			("iAICreatePercent", "getAICreatePercent"),
			("iAIDeclareWarProb", "getAIDeclareWarProb"),
			("iAIGrowthPercent", "getAIGrowthPercent"),
			("iAIInflationPercent", "getAIInflationPercent"),
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
			("iAnimalAttackProb", "getAnimalAttackProb"),
			("iAnimalCombatModifier", "getAnimalCombatModifier"),
			("iAttitudeChange", "getAttitudeChange"),
			("iBarbarianCityCreationProb", "getBarbarianCityCreationProb"),
			("iBarbarianCityCreationTurnsElapsed", "getBarbarianCityCreationTurnsElapsed"),
			("iBarbarianCombatModifier", "getBarbarianCombatModifier"),
			("iBarbarianCreationTurnsElapsed", "getBarbarianCreationTurnsElapsed"),
			("iBarbarianInitialDefenders", "getBarbarianInitialDefenders"),
			("iCivicUpkeepPercent", "getCivicUpkeepPercent"),
			("iColonyMaintenancePercent", "getColonyMaintenancePercent"),
			("iCorporationMaintenancePercent", "getCorporationMaintenancePercent"),
			("iDifficulty", "getDifficulty"),
			("iDistanceMaintenancePercent", "getDistanceMaintenancePercent"),
			("iFreeUnits", "getFreeUnits"),
			("iFreeWinsVsBarbs", "getFreeWinsVsBarbs"),
			("iHappyBonus", "getHappyBonus"),
			("iHealthBonus", "getHealthBonus"),
			("iInflationPercent", "getInflationPercent"),
			("iMaxColonyMaintenance", "getMaxColonyMaintenance"),
			("iMaxNumCitiesMaintenance", "getMaxNumCitiesMaintenance"),
			("iNoTechTradeModifier", "getNoTechTradeModifier"),
			("iNumCitiesMaintenancePercent", "getNumCitiesMaintenancePercent"),
			("iResearchPercent", "getResearchPercent"),
			("iStartingDefenseUnits", "getStartingDefenseUnits"),
			("iStartingExploreUnits", "getStartingExploreUnits"),
			("iStartingGold", "getStartingGold"),
			("iStartingLocPercent", "getStartingLocationPercent"),
			("iStartingWorkerUnits", "getStartingWorkerUnits"),
			("iTechTradeKnownModifier", "getTechTradeKnownModifier"),
			("iUnownedTilesPerBarbarianCity", "getUnownedTilesPerBarbarianCity"),
			("iUnownedTilesPerBarbarianUnit", "getUnownedTilesPerBarbarianUnit"),
			("iUnownedTilesPerGameAnimal", "getUnownedTilesPerGameAnimal"),
			("iUnownedWaterTilesPerBarbarianUnit", "getUnownedWaterTilesPerBarbarianUnit"),
			("iUnitCostPercent", "getUnitCostPercent"),
		)
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
		anchor_field = gc.getDefineSTRING("SAS_SEVOPEDIA_HANDICAP_CHART_ANCHOR_FIELD")
		abbrev_tech_names = {
			"Animal Husbandry": "Animal H.",
			"Bronze Working": "Bronze W.",
			"Iron Working": "Iron W.",
			"Industrialism": "Industr.",
		}
		techs_per_cell = 1
		none_text = localText.getText("TXT_KEY_PEDIA_SAS_HANDICAP_CHART_FREE_TECHS_NONE", ())

		all_fields = {}
		parsed_data = {}
		difficulty_types = []
		tech_types = []
		for iTech in xrange(gc.getNumTechInfos()):
			tech_types.append(gc.getTechInfo(iTech).getType())

		for iHandicap in xrange(gc.getNumHandicapInfos()):
			info = gc.getHandicapInfo(iHandicap)
			handicap_type = info.getType()
			difficulty_types.append(handicap_type)
			handicap_dict = {}

			for field_name, getter_name in field_getters:
				value = ""
				try:
					getter = getattr(info, getter_name)
					value = getter()
				except:
					value = ""
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
			row = {"Field": field}
			for difficulty in difficulty_types:
				value = ""
				if difficulty in parsed_data:
					value = parsed_data[difficulty].get(field, "")
				row[difficulty] = value
			rows.append(row)

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

		header = ["Field"]
		for difficulty in difficulty_types:
			header.append(self._beautify_enum_name(difficulty))

		data = [header]
		for row in rows:
			field_name = row["Field"]
			out_row = [field_name]
			for difficulty in difficulty_types:
				value = row.get(difficulty, "")
				if row["Field"] in ("FreeTechs", "AIFreeTechs"):
					value = self._format_tech_list(value, False, none_text, abbrev_tech_names)
				out_row.append(value)
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
				else:
					new_row["Field"] = ""
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

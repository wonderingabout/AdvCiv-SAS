# --- World size chart page for Sevopedia (AdvCiv-SAS) ---
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# Mirrors the handicap chart layout, but for WorldInfo.



from CvPythonExtensions import *
import CvUtil
import re

gc = CyGlobalContext()
localText = CyTranslator()

def _font2(szText):
	return u"<font=2>%s</font>" % unicode(szText)



class SevoPediaWorldSizeChart:
	def __init__(self, main):
		self.top = main
		self._cachedTable = None

		self.MARGIN = 4
		self.ROW_H = 15
		self.W_ICON = 24
		self.W_FIELD = 210
		iHeaderIcons = gc.getDefineINT("SAS_SEVOPEDIA_WORLD_SIZE_CHART_HEADER_ICONS")
		if iHeaderIcons == 0:
			iHeaderIcons = gc.getDefineINT("SAS_SEVOPEDIA_HANDICAP_CHART_HEADER_ICONS")
		self.IS_SAS_SEVOPEDIA_WORLD_SIZE_CHART_HEADER_ICONS = (iHeaderIcons != 0)
		self.TABLE_FILL_PERCENT = gc.getDefineINT("SAS_SEVOPEDIA_WORLD_SIZE_CHART_TABLE_FILL_PERCENT")
		if self.TABLE_FILL_PERCENT <= 0:
			raise ValueError("[FATAL] SAS_SEVOPEDIA_WORLD_SIZE_CHART_TABLE_FILL_PERCENT must be >= 1.")

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
		if self.IS_SAS_SEVOPEDIA_WORLD_SIZE_CHART_HEADER_ICONS:
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
			if self.IS_SAS_SEVOPEDIA_WORLD_SIZE_CHART_HEADER_ICONS and iCol == 0:
				colW = self.W_ICON
			elif (self.IS_SAS_SEVOPEDIA_WORLD_SIZE_CHART_HEADER_ICONS and iCol == 1) or (not self.IS_SAS_SEVOPEDIA_WORLD_SIZE_CHART_HEADER_ICONS and iCol == 0):
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
				if self.IS_SAS_SEVOPEDIA_WORLD_SIZE_CHART_HEADER_ICONS and iCol == 0:
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
				elif (self.IS_SAS_SEVOPEDIA_WORLD_SIZE_CHART_HEADER_ICONS and iCol == 1) or (not self.IS_SAS_SEVOPEDIA_WORLD_SIZE_CHART_HEADER_ICONS and iCol == 0):
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
			("GridSize",                    None,                          "glyph:map"),
			("GridTiles",                   None,                          "glyph:map"),
			("iDefaultPlayers",             "getDefaultPlayers",           "glyph:citizen"),
			("iTargetNumCities",            "getTargetNumCities",          "glyph:citizen"),
			("iNumFreeBuildingBonuses",     "getNumFreeBuildingBonuses",   "glyph:prod"),
			("iBuildingClassPrereqModifier","getBuildingClassPrereqModifier","glyph:prod"),
			("iUnitNameModifier",           "getUnitNameModifier",         "btn:swords"),
			("iMaxConscriptModifier",       "getMaxConscriptModifier",     "btn:swords"),
			("iWarWearinessModifier",       "getWarWearinessModifier",     "glyph:unhappy"),
			("iUnitCostPercent",            "getUnitCostPercent",          "btn:swords"),
			("iTerrainGrainChange",         "getTerrainGrainChange",       "btn:herb"),
			("iFeatureGrainChange",         "getFeatureGrainChange",       "btn:herb"),
			("iResearchPercent",            "getResearchPercent",          "glyph:research"),
			("iTradeProfitPercent",         "getTradeProfitPercent",       "glyph:gold"),
			("iDistanceMaintenancePercent", "getDistanceMaintenancePercent","glyph:gold"),
			("iNumCitiesMaintenancePercent","getNumCitiesMaintenancePercent","glyph:gold"),
			("iColonyMaintenancePercent",   "getColonyMaintenancePercent", "glyph:gold"),
			("iCorporationMaintenancePercent","getCorporationMaintenancePercent","glyph:gold"),
			("iNumCitiesAnarchyPercent",    "getNumCitiesAnarchyPercent",  "btn:fire"),
			("iAdvancedStartPointsMod",     "getAdvancedStartPointsMod",   "glyph:defense"),
		)

		field_getters_list = []
		for field_name, getter_name, _icon_token in row_specs:
			if getter_name:
				field_getters_list.append((field_name, getter_name))
		field_getters = tuple(field_getters_list)

		if gc.getNumWorldInfos() > 0:
			info = gc.getWorldInfo(0)
			missing = []
			for field_name, getter_name in field_getters:
				if not hasattr(info, getter_name):
					missing.append(getter_name)
			if not hasattr(info, "getGridWidth"):
				missing.append("getGridWidth")
			if not hasattr(info, "getGridHeight"):
				missing.append("getGridHeight")
			if missing:
				raise RuntimeError("[FATAL] Your mod DLL does not expose the required CvWorldInfo Python getters: %s. Please expose them in CyInfoInterface2.cpp and rebuild the DLL." % ", ".join(missing))

		game = CyGame()
		btn_by_name = {}
		# Button icons resolved via TXT_KEY_IMAGE_AS_BUTTON_*_PATH (IconsAsButtons.xml).
		def _btn_path(szTxtKey):
			return CvUtil.convertToStr(localText.getText(szTxtKey, ()))

		_btn_defs = (
			# (name, TXT_KEY_IMAGE_AS_BUTTON_*_PATH)
			("swords", "TXT_KEY_IMAGE_AS_BUTTON_CROSSED_SWORDS_BUTTON_PATH"),
			("herb",   "TXT_KEY_IMAGE_AS_BUTTON_HERB_BUTTON_PATH"),
			("fire",   "TXT_KEY_IMAGE_AS_BUTTON_FIRE_BUTTON_PATH"),
		)
		for i, (name, txtKey) in enumerate(_btn_defs):
			# Group id only affects sorting by the icon column.
			# Reorder _btn_defs to change the icon-theme sort order.
			btn_by_name[name] = (_btn_path(txtKey), (i + 1) * 10)

		glyph_by_name = {}
		# GameFont glyph icons (yields/commerce/symbols).
		_glyph_defs = (
			# (name, glyph_char)
			("map",      (u"%c" % (game.getSymbolID(FontSymbols.MAP_CHAR)))),
			("citizen",  (u"%c" % (game.getSymbolID(FontSymbols.CITIZEN_CHAR)))),
			("prod",     (u"%c" % (gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar()))),
			("gold",     (u"%c" % (gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar()))),
			("research", (u"%c" % (gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar()))),
			("defense",  (u"%c" % (game.getSymbolID(FontSymbols.DEFENSE_CHAR)))),
			("unhappy",  (u"%c" % (game.getSymbolID(FontSymbols.UNHAPPY_CHAR)))),
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
		for field_name, _getter_name, icon_token in row_specs:
			if icon_token:
				icon_token_by_key[field_name] = icon_token

		def icon_cell_for_key(icon_key, iRowIndex):
			# Always return a stable invisible tie-breaker, even if no icon is found.
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


		world_types = []
		world_labels = []
		parsed_data = {}

		for iWorld in xrange(gc.getNumWorldInfos()):
			info = gc.getWorldInfo(iWorld)
			world_type = info.getType()
			world_types.append(world_type)
			world_labels.append(info.getDescription())

			world_dict = {}
			for field_name, getter_name in field_getters:
				getter = getattr(info, getter_name)
				world_dict[field_name] = str(getter())

			grid_w = info.getGridWidth()
			grid_h = info.getGridHeight()
			world_dict["GridSize"] = "%d x %d" % (grid_w, grid_h)
			world_dict["GridTiles"] = str(grid_w * grid_h)

			parsed_data[world_type] = world_dict

		header = []
		if self.IS_SAS_SEVOPEDIA_WORLD_SIZE_CHART_HEADER_ICONS:
			header.append(u"")
			header.append(_font2("Field"))
		else:
			header.append(_font2("Field"))
		for label in world_labels:
			header.append(_font2(label))

		table = [header]

		row_index = 0
		for field_name, _getter_name, _icon_token in row_specs:
			szFieldName = self._display_field_name(field_name)

			if self.IS_SAS_SEVOPEDIA_WORLD_SIZE_CHART_HEADER_ICONS:
				row = [icon_cell_for_key(field_name, row_index), _font2(szFieldName)]
			else:
				row = [_font2(szFieldName)]

			for world_type in world_types:
				row.append(_font2(parsed_data.get(world_type, {}).get(field_name, "")))

			table.append(row)
			row_index += 1

		return table

	def _display_field_name(self, field_name):
		field_map = {
			"GridSize": "Grid Size (W x H)",
			"GridTiles": "Grid Tiles",
			"iDefaultPlayers": "Default Players",
			"iTargetNumCities": "Target Num Cities",
			"iNumFreeBuildingBonuses": "Free Building Bonuses",
			"iBuildingClassPrereqModifier": "Building Class Prereq Mod",
			"iUnitNameModifier": "Unit Name Modifier",
			"iMaxConscriptModifier": "Max Conscript Mod",
			"iWarWearinessModifier": "War Weariness Mod",
			"iAdvancedStartPointsMod": "Advanced Start Points Mod",
		}
		name = field_map.get(field_name, "")
		if name:
			return name
		return self._beautify_field_name(field_name)

	def _beautify_field_name(self, raw_name):
		name = raw_name
		if name.startswith("i") and len(name) > 1 and name[1].isupper():
			name = name[1:]
		name = re.sub(r"_", " ", name)
		name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
		if name.endswith("Percent"):
			name = name[:-len("Percent")] + "%"
		return name

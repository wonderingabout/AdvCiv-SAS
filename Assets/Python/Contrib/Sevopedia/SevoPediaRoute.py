# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The page reads any RouteInfo; Road and Railroad are the routes this mod ships, and mod-mods may add or remove others.
# The first draft drew labeled button rows ("Build a Road", "Engineering: -10/60 ...") and a "Requires any one connected" row, which read as separate pieces of information unlike other Sevopedia pages.
# The page now follows the Feature and Build pages: button-only panels titled by relation, a Requires panel with "or" between alternative bonuses, and Special Abilities bullets that say what each relation does.
# Panels list every XML relation that names a route: Builds, Improvement route yields, Tech movement changes and bridges, Promotions using enemy routes and Event Triggers.
# Civics, Buildings, Religions, Corporations and Specialists have no route field; their "trade routes" are city connections, a different concept.
# Workers are omitted: a unit builds the route through a Build, so the Build page lists them. (GPT-6.1-Sol + Claude code Opus 5.5) -->
# <!-- custom: The second layout left the right half of the page empty while Event Triggers overflowed into a scrolled row of identical buttons without hover.
# Panels are now in themed rows using the full width: what the route needs and who builds it; Removes beside Improvements, since clearing a feature comes before improving the tile; Promotions beside Techs (labeled Move/Bridge); then Special Abilities beside an Event Triggers table naming each trigger, its era and its relation.
# Techs sits on the right, away from Requires, so it does not read as a prerequisite. (Claude code Opus 5.5) -->

from CvPythonExtensions import *
import CvUtil
import SASTextScale
import SASVisualUtils as SASVisuals
# <!-- custom: The helpers also re-export SASMagicNumbers, including the History expand and Event Trigger jump IDs. (Claude code Opus 5.5) -->
from _sevopedia_helpers import *
# <!-- custom: Shared route widget and lookups, kept in a module that is safe to import at game start. (Claude code Opus 5.5) -->
from SevoPediaRouteUtils import getRouteYieldImprovements, getYieldText
# <!-- custom: The Event Triggers table jumps to that category's page. (Claude code Opus 5.5) -->

gc = CyGlobalContext()
localText = CyTranslator()

# <!-- custom: Short untranslated numTxt codes, like the Bonus page's Cons/Prod, explained in the Routes legend. (Claude code Opus 5.5) -->
ROUTE_NUMTXT_MOVE = u"Move"
ROUTE_NUMTXT_BRIDGE = u"Bridge"


class SevoPediaRoute:
	def __init__(self, main):
		self.iRoute = -1
		self.bHistoryExpanded = False
		self.top = main
		# <!-- custom: Cache the fixed translated labels once per page object, as the Event Triggers page does; texts with arguments and the XML scans stay per view. (Claude code Opus 5.5) -->
		self.TXT_REQUIRES = localText.getText("TXT_KEY_PEDIA_REQUIRES", ())
		self.TXT_BUILDS = localText.getText("TXT_KEY_PEDIA_CATEGORY_BUILD", ())
		self.TXT_REMOVES = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_REMOVES_FEATURES", ())
		self.TXT_IMPROVEMENTS = localText.getText("TXT_KEY_PEDIA_IMPROVEMENTS_CUSTOM", ())
		self.TXT_PROMOTIONS = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_PROMOTIONS", ())
		self.TXT_TECHS = localText.getText("TXT_KEY_PEDIA_CATEGORY_TECH", ())
		self.TXT_EVENT_TRIGGERS = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_EVENT_TRIGGERS", ())
		self.TXT_SPECIAL = localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ())
		self.TXT_HISTORY = localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ())
		self.TXT_ROUTE = localText.getText("TXT_KEY_PEDIA_BUILD_ROUTE", ())
		self.TXT_AND = localText.getText("TXT_KEY_AND", ())
		self.TXT_OR = localText.getText("TXT_KEY_OR", ())
		self.TXT_COL_TRIGGER = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_EVENT_TRIGGER", ())
		self.TXT_COL_ERA = localText.getText("TXT_KEY_PEDIA_ERA", ())
		self.TXT_COL_RELATION = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_RELATION", ())
		self.TXT_RELATION_REQUIRES = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_RELATION_REQUIRES", ())
		self.TXT_RELATION_ADDS = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_RELATION_ADDS", ())
		self.TXT_RELATION_REMOVES = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_RELATION_REMOVES", ())
		self.TXT_ERA_ANY_HEADER = localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_GROUP_NO_TECH", ())
		self.TXT_ERA_INDIRECT_SUFFIX = localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_GROUP_INDIRECT_SUFFIX", ())
		self.TXT_ERA_ANY = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_ERA_ANY", ())
		self.TXT_ERA_INDIRECT = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_ERA_INDIRECT", ())
		self.TXT_RULE_MOVE = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_MOVE_RULE", ())
		self.TXT_RULE_ENEMY = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_ENEMY", ())
		self.TXT_RULE_TRADE = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_TRADE_NETWORK", ())
		self.TXT_RULE_BONUS = localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_BONUS_RULE", ())

		self.W_PAGE = self.top.R_PEDIA_PAGE - self.top.X_PEDIA_PAGE
		self.W_HALF = (self.W_PAGE - MEDIUM_MARGIN) / 2
		self.X_RIGHT_HALF = self.top.X_PEDIA_PAGE + self.W_HALF + MEDIUM_MARGIN
		self.W_RIGHT_HALF = self.top.R_PEDIA_PAGE - self.X_RIGHT_HALF

		# <!-- custom: Row 1: the route, what it needs and the Builds that create it. (Claude code Opus 5.5) -->
		self.X_INFO_PANE = self.top.X_PEDIA_PAGE
		self.Y_INFO_PANE = self.top.Y_PEDIA_PAGE
		self.W_INFO_PANE = get_panel_width_for_buttons(5, MULTILIST_BUTTON_SIZE, HYPOTHESIZED_NON_MULTILIST_PANEL_EDGE_PADDING, HYPOTHESIZED_NON_MULTILIST_PANEL_INTER_BUTTON_SPACING)
		self.H_INFO_PANE = 127

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_INFO_PANE + 10
		self.Y_ICON = self.Y_INFO_PANE + 10
		self.X_INFO_TEXT = self.X_INFO_PANE + 110
		self.Y_INFO_TEXT = self.Y_ICON + 15
		self.W_INFO_TEXT = self.W_INFO_PANE - 120
		self.H_INFO_TEXT = self.H_INFO_PANE - 20

		# <!-- custom: Builds is plural because XML allows several Builds per route, but each route here has one, so the panel is one button wide like the Build page's Requires; Requires takes the rest of the row. (Claude code Opus 5.5) -->
		self.W_BUILDS = get_panel_width_for_buttons(1, MULTILIST_BUTTON_SIZE, HYPOTHESIZED_NON_MULTILIST_PANEL_EDGE_PADDING, HYPOTHESIZED_NON_MULTILIST_PANEL_INTER_BUTTON_SPACING)
		self.X_BUILDS = self.top.R_PEDIA_PAGE - self.W_BUILDS
		self.Y_BUILDS = self.Y_INFO_PANE
		self.H_BUILDS = self.H_INFO_PANE

		self.X_REQUIRES = self.X_INFO_PANE + self.W_INFO_PANE + MEDIUM_MARGIN
		self.Y_REQUIRES = self.Y_INFO_PANE
		self.W_REQUIRES = self.X_BUILDS - MEDIUM_MARGIN - self.X_REQUIRES
		self.H_REQUIRES = self.H_INFO_PANE

		# <!-- custom: Row 2: features cleared, then improvements that gain yields. (Claude code Opus 5.5) -->
		self.X_FEATURES = self.top.X_PEDIA_PAGE
		self.Y_FEATURES = self.Y_INFO_PANE + self.H_INFO_PANE + SMALL_MARGIN
		self.W_FEATURES = self.W_HALF
		self.H_FEATURES = NON_MULTILIST_PANEL_STANDARD_HEIGHT

		self.X_IMPROVEMENTS = self.X_RIGHT_HALF
		self.Y_IMPROVEMENTS = self.Y_FEATURES
		self.W_IMPROVEMENTS = self.W_RIGHT_HALF
		self.H_IMPROVEMENTS = self.H_FEATURES

		# <!-- custom: Row 3: promotions and techs that change how units use the route.
		# A first try made this row 20 px taller for the Move/Bridge labels, but the Promotions button then sat lower than the Techs one; the standard height fits the labels, as on the Unit page. (Claude code Opus 5.5) -->
		self.X_PROMOTIONS = self.top.X_PEDIA_PAGE
		self.Y_PROMOTIONS = self.Y_FEATURES + self.H_FEATURES + SMALL_MARGIN
		self.W_PROMOTIONS = self.W_HALF
		self.H_PROMOTIONS = NON_MULTILIST_PANEL_STANDARD_HEIGHT

		self.X_TECHS = self.X_RIGHT_HALF
		self.Y_TECHS = self.Y_PROMOTIONS
		self.W_TECHS = self.W_RIGHT_HALF
		self.H_TECHS = self.H_PROMOTIONS

		# <!-- custom: Row 4: rules as bullets, and the event triggers as a table. (Claude code Opus 5.5) -->
		self.X_SPECIAL = self.top.X_PEDIA_PAGE
		self.Y_SPECIAL = self.Y_PROMOTIONS + self.H_PROMOTIONS + SMALL_MARGIN
		self.W_SPECIAL = self.W_HALF
		self.H_SPECIAL = self.top.B_PEDIA_PAGE - self.Y_SPECIAL

		self.X_EVENT_TRIGGERS = self.X_RIGHT_HALF
		self.Y_EVENT_TRIGGERS = self.Y_SPECIAL
		self.W_EVENT_TRIGGERS = self.W_RIGHT_HALF
		self.H_EVENT_TRIGGERS = self.H_SPECIAL

	def interfaceScreen(self, iRoute):
		if self.iRoute != iRoute:
			self.bHistoryExpanded = False
		self.iRoute = iRoute
		info = gc.getRouteInfo(iRoute)
		builds = [iBuild for iBuild in xrange(gc.getNumBuildInfos()) if gc.getBuildInfo(iBuild).getRoute() == iRoute]
		yieldImprovements = getRouteYieldImprovements(iRoute)

		place_new_concept_legend_link(self.top, "CONCEPT_SAS_SEVOPEDIA_ROUTES_LEGEND")
		self.placeInfo(info)
		self.placeRequires(info, builds)

		# <!-- custom: The native Build widget gives the Build's hover and opens its page. See KI#113. (GPT-6.1-Sol + Claude code Opus 5.5) -->
		buttons = [(gc.getBuildInfo(iBuild).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILD, iBuild, -1) for iBuild in builds]
		self.placeButtonPanel(self.TXT_BUILDS, self.X_BUILDS, self.Y_BUILDS, self.W_BUILDS, self.H_BUILDS, buttons)

		# <!-- custom: Feature clearing belongs to the Build; its extra time, tech and production stay on the Build page. (GPT-6.1-Sol) -->
		buttons = []
		for iFeature in xrange(gc.getNumFeatureInfos()):
			for iBuild in builds:
				if gc.getBuildInfo(iBuild).isFeatureRemove(iFeature):
					buttons.append((gc.getFeatureInfo(iFeature).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE, iFeature, 1))
					break
		self.placeButtonPanel(self.TXT_REMOVES, self.X_FEATURES, self.Y_FEATURES, self.W_FEATURES, self.H_FEATURES, buttons)

		buttons = [(gc.getImprovementInfo(iImprovement).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, iImprovement, 1) for iImprovement in yieldImprovements]
		self.placeButtonPanel(self.TXT_IMPROVEMENTS, self.X_IMPROVEMENTS, self.Y_IMPROVEMENTS, self.W_IMPROVEMENTS, self.H_IMPROVEMENTS, buttons)

		buttons = [(gc.getPromotionInfo(iPromotion).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iPromotion, 1) for iPromotion in xrange(gc.getNumPromotionInfos()) if gc.getPromotionInfo(iPromotion).isEnemyRoute()]
		self.placeButtonPanel(self.TXT_PROMOTIONS, self.X_PROMOTIONS, self.Y_PROMOTIONS, self.W_PROMOTIONS, self.H_PROMOTIONS, buttons)

		# <!-- custom: Techs mixes two relations, so each button gets a numTxt label explained in the legend: Move changes the route's movement cost, Bridge lets it speed movement across rivers. (Claude code Opus 5.5) -->
		techEntries = []
		for iTech in xrange(gc.getNumTechInfos()):
			if info.getTechMovementChange(iTech) != 0:
				techEntries.append((iTech, ROUTE_NUMTXT_MOVE))
			if gc.getTechInfo(iTech).isBridgeBuilding():
				techEntries.append((iTech, ROUTE_NUMTXT_BRIDGE))
		self.placeTechs(techEntries)
		self.placeEventTriggers()

		# <!-- custom: RouteInfo has no Civilopedia text in the current XML; if a mod-mod adds one, it shares the Special Abilities column. (Claude code Opus 5.5) -->
		szHistory = info.getCivilopedia()
		if szHistory:
			hHalf = (self.H_SPECIAL - SMALL_MARGIN) / 2
			self.placeSpecial(info, techEntries, yieldImprovements, hHalf)
			yHistory = self.Y_SPECIAL + hHalf + SMALL_MARGIN
			draw_expandable_text_panel(self.top.getScreen(), self.top, self.TXT_HISTORY, self.X_SPECIAL, yHistory, self.W_SPECIAL, self.top.B_PEDIA_PAGE - yHistory, szHistory, self.bHistoryExpanded, SAS_MAGIC_PEDIA_PYTHON_HISTORY_EXPAND)
		else:
			self.placeSpecial(info, techEntries, yieldImprovements, self.H_SPECIAL)

	def setHistoryExpanded(self, bExpanded):
		self.bHistoryExpanded = bExpanded

	def placeButtonPanel(self, szTitle, x, y, w, h, buttons):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		screen.addPanel(panel, szTitle, "", False, True, x, y, w, h, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")
		for szButton, eWidget, iData1, iData2 in buttons:
			screen.attachImageButton(panel, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, eWidget, iData1, iData2, False)
		if not buttons:
			draw_none_text(screen, self.top, x, y, w, h)

	def placeInfo(self, info):
		screen = self.top.getScreen()
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_INFO_PANE, self.Y_INFO_PANE, self.W_INFO_PANE, self.H_INFO_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), info.getButton(), self.X_ICON + self.W_ICON / 2 - PANE_ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - PANE_ICON_SIZE / 2, PANE_ICON_SIZE, PANE_ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)

		panel = self.top.getNextWidgetName()
		screen.addListBoxGFC(panel, "", self.X_INFO_TEXT, self.Y_INFO_TEXT, self.W_INFO_TEXT, self.H_INFO_TEXT, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panel, False)
		screen.appendListBoxString(panel, SASTextScale.titleText(info.getDescription()), WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		screen.appendListBoxString(panel, SASTextScale.labelText(self.TXT_ROUTE), WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		# <!-- custom: The route's own tile yields go under the title, as on the Feature page; neither shipped route has any, so the line stays empty. (Claude code Opus 5.5) -->
		szYields = getYieldText([info.getYieldChange(iYield) for iYield in xrange(YieldTypes.NUM_YIELD_TYPES)])
		screen.appendListBoxString(panel, SASTextScale.titleText(szYields), WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

	def placeRequires(self, info, builds):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		screen.addPanel(panel, self.TXT_REQUIRES, "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")
		bFound = False

		# <!-- custom: The tech belongs to the Build, not the route; list each distinct one in case several Builds create the same route. (Claude code Opus 5.5) -->
		techs = []
		for iBuild in builds:
			iTech = gc.getBuildInfo(iBuild).getTechPrereq()
			if iTech >= 0 and iTech not in techs:
				techs.append(iTech)
				screen.attachImageButton(panel, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False)
				bFound = True

		iAndBonus = info.getPrereqBonus()
		if iAndBonus >= 0:
			screen.attachImageButton(panel, "", gc.getBonusInfo(iAndBonus).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iAndBonus, -1, False)
			bFound = True

		orBonuses = getRoutePrereqOrBonuses(info)
		# <!-- custom: Same "and(" ...
		# ")" grouping as the Unit page when a mandatory bonus precedes several alternatives. (Claude code Opus 5.5) -->
		bGroup = iAndBonus >= 0 and len(orBonuses) > 1
		if iAndBonus >= 0 and orBonuses:
			szAnd = self.TXT_AND
			if bGroup:
				szAnd += u"("
			screen.attachLabel(panel, "", SASTextScale.labelText(szAnd))
		for i, iBonus in enumerate(orBonuses):
			if i > 0:
				screen.attachLabel(panel, "", SASTextScale.labelText(self.TXT_OR))
			screen.attachImageButton(panel, "", gc.getBonusInfo(iBonus).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iBonus, -1, False)
			bFound = True
		if bGroup:
			screen.attachLabel(panel, "", SASTextScale.labelText(u")"))

		if not bFound:
			draw_none_text(screen, self.top, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES)

	def placeTechs(self, techEntries):
		screen = self.top.getScreen()
		screen.addPanel(self.top.getNextWidgetName(), self.TXT_TECHS, "", False, True, self.X_TECHS, self.Y_TECHS, self.W_TECHS, self.H_TECHS, PanelStyles.PANEL_STYLE_BLUE50)
		if not techEntries:
			draw_none_text(screen, self.top, self.X_TECHS, self.Y_TECHS, self.W_TECHS, self.H_TECHS)
			return
		# <!-- custom: A multilist, unlike attachImageButton, can show numTxt under a button; the Bonus page's corporation panel does the same. (Claude code Opus 5.5) -->
		rowListName = self.top.getNextWidgetName()
		# <!-- custom: Shared multilist placement, see get_panel_multilist_rect. (Claude code Opus 5.5) -->
		multiListX, multiListY, multiListW, multiListH = get_panel_multilist_rect(self.X_TECHS, self.Y_TECHS, self.W_TECHS, self.H_TECHS)
		screen.addMultiListControlGFC(rowListName, "", multiListX, multiListY, multiListW, multiListH, SEVOPEDIA_MULTILIST_NUM_LISTS_AUTO_CALCULATE, MULTILIST_BUTTON_SIZE, MULTILIST_BUTTON_SIZE, TableStyles.TABLE_STYLE_STANDARD)
		maxButtonsPerRow = get_multilist_max_buttons_per_row(multiListW, MULTILIST_BUTTON_SIZE)
		for iButtonIndex, (iTech, numTxt) in enumerate(techEntries):
			screen.appendMultiListButton(rowListName, gc.getTechInfo(iTech).getButton(), SEVOPEDIA_MULTILIST_COLUMN_INDEX_AUTO, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False)
			add_multilist_numTxt_under_button(multiListX, multiListY, get_extra_correction_x(numTxt), iButtonIndex, MULTILIST_BUTTON_SIZE, maxButtonsPerRow, numTxt, screen, self.top, WidgetTypes.WIDGET_GENERAL, CvUtil.FONT_CENTER_JUSTIFY)

	# <!-- custom: Era labels come from the Event Triggers category's cached era-grouped list, the section header each trigger sits under, so both agree; they are shortened (Any, (i)) to fit, as explained in the Routes legend. (Claude code Opus 5.5) -->
	def getEventTriggerRows(self):
		rows = []
		szEra = u""
		for szLabel, iTrigger in self.top.getEventTriggerList():
			if iTrigger < 0:
				if szLabel:
					szEra = szLabel
				continue
			relations = getRouteEventTriggerRelations(iTrigger, self.iRoute)
			if not relations:
				continue
			szShortEra = szEra
			if szEra == self.TXT_ERA_ANY_HEADER:
				szShortEra = self.TXT_ERA_ANY
			elif szEra.endswith(self.TXT_ERA_INDIRECT_SUFFIX):
				szShortEra = szEra[:-len(self.TXT_ERA_INDIRECT_SUFFIX)].strip() + u" " + self.TXT_ERA_INDIRECT
			szRelations = u", ".join([self.getRelationText(iRelation) for iRelation in relations])
			rows.append((szLabel, szShortEra, szRelations, iTrigger))
		return rows

	def getRelationText(self, iRelation):
		if iRelation == ROUTE_RELATION_REQUIRES:
			return self.TXT_RELATION_REQUIRES
		if iRelation == ROUTE_RELATION_ADDS:
			return self.TXT_RELATION_ADDS
		return self.TXT_RELATION_REMOVES

	def placeEventTriggers(self):
		screen = self.top.getScreen()
		x = self.X_EVENT_TRIGGERS
		y = self.Y_EVENT_TRIGGERS
		w = self.W_EVENT_TRIGGERS
		h = self.H_EVENT_TRIGGERS
		screen.addPanel(self.top.getNextWidgetName(), self.TXT_EVENT_TRIGGERS, "", True, True, x, y, w, h, PanelStyles.PANEL_STYLE_BLUE50)
		innerX = x + INCHART_TABLE_MARGIN
		innerY = y + 28
		innerW = w - 2 * INCHART_TABLE_MARGIN
		innerH = h - 28 - INCHART_TABLE_MARGIN
		rows = self.getEventTriggerRows()
		if not rows:
			draw_none_text(screen, self.top, innerX, innerY, innerW, innerH)
			return
		# <!-- custom: A row of identical green event buttons gave no hover, so the trigger could not be told apart before clicking; the table names each one and gives its era and relation.
		# The name comes first and takes the spare width; Era and Relation hold short codes after Relation at 300 px still cut "Required on its plot, Event removes it".
		# At wide resolutions leave room for upscaled Era and Relation labels.
		# At narrow resolutions reserve at least half the table for names.
		# Keep the era order.
		# Each cell carries its trigger ID so the DLL can supply hover and open the page. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		wEra = min(210, innerW // 4)
		wRelation = min(190, innerW // 4)
		tableName = self.top.getNextWidgetName()
		screen.addTableControlGFC(tableName, 3, innerX, innerY, innerW, innerH, True, False, INCHART_ROW_HEIGHT, INCHART_ROW_HEIGHT, CHART_TABLE_STYLE)
		screen.setTableColumnHeader(tableName, 0, SASTextScale.labelText(self.TXT_COL_TRIGGER), innerW - wEra - wRelation)
		screen.setTableColumnHeader(tableName, 1, SASTextScale.labelText(self.TXT_COL_ERA), wEra)
		screen.setTableColumnHeader(tableName, 2, SASTextScale.labelText(self.TXT_COL_RELATION), wRelation)
		for szName, szEra, szRelations, iTrigger in rows:
			iRow = screen.appendTableRow(tableName)
			screen.setTableText(tableName, 0, iRow, SASTextScale.labelText(szName), self.top.SAS_getEventTriggerButton(iTrigger), WidgetTypes.WIDGET_PEDIA_JUMP_TO_EVENT_TRIGGER, iTrigger, -1, CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableText(tableName, 1, iRow, SASTextScale.labelText(szEra), "", WidgetTypes.WIDGET_PEDIA_JUMP_TO_EVENT_TRIGGER, iTrigger, -1, CvUtil.FONT_LEFT_JUSTIFY)
			screen.setTableText(tableName, 2, iRow, SASTextScale.labelText(szRelations), "", WidgetTypes.WIDGET_PEDIA_JUMP_TO_EVENT_TRIGGER, iTrigger, -1, CvUtil.FONT_LEFT_JUSTIFY)

	def placeSpecial(self, info, techEntries, yieldImprovements, h):
		screen = self.top.getScreen()
		screen.addPanel(self.top.getNextWidgetName(), self.TXT_SPECIAL, "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, h, PanelStyles.PANEL_STYLE_BLUE50)
		bullet = SASVisuals.Font.BULLET_CHAR + u" "
		iDenominator = gc.getMOVE_DENOMINATOR()
		# <!-- custom: CvPlot::movementCost takes the cheaper of normal terrain movement, the route cost and the flat route cost.
		# Only the flat term scales with the unit's base moves; tech changes apply only to the regular route term. (GPT-6.1-Sol) -->
		lines = [
			localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_MOVE_COST", (info.getMovementCost(), iDenominator)),
			localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_FLAT_COST", (info.getFlatMovementCost(), iDenominator)),
			self.TXT_RULE_MOVE,
		]
		for iTech, numTxt in techEntries:
			if numTxt == ROUTE_NUMTXT_MOVE:
				lines.append(localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_TECH_CHANGE", (u"%+d/%d" % (info.getTechMovementChange(iTech), iDenominator), make_pedia_link(gc.getTechInfo(iTech).getDescription()))))
		# <!-- custom: CvPlot::movementCost ignores the route across a river until the team has a bridge-building tech. (Claude code Opus 5.5) -->
		for iTech, numTxt in techEntries:
			if numTxt == ROUTE_NUMTXT_BRIDGE:
				lines.append(localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_BRIDGE", (make_pedia_link(gc.getTechInfo(iTech).getDescription()),)))
		# <!-- custom: CvPlot::isValidRoute: owned tiles of an enemy, or of a team being disengaged from (advc.034), need an enemy-route promotion. (Claude code Opus 5.5) -->
		lines.append(self.TXT_RULE_ENEMY)
		lines.append(self.TXT_RULE_TRADE)
		# <!-- custom: CvPlot::canBuild checks required bonuses with isAdjacentPlotGroupConnectedBonus, and builds a route only over one of lower value. (Claude code Opus 5.5) -->
		if info.getPrereqBonus() >= 0 or getRoutePrereqOrBonuses(info):
			lines.append(self.TXT_RULE_BONUS)
		lines.append(localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_VALUE", (info.getValue(),)))
		for iImprovement in yieldImprovements:
			improvement = gc.getImprovementInfo(iImprovement)
			szYields = getYieldText([improvement.getRouteYieldChanges(self.iRoute, iYield) for iYield in xrange(YieldTypes.NUM_YIELD_TYPES)])
			lines.append(localText.getText("TXT_KEY_PEDIA_SAS_ROUTE_IMPROVEMENT_YIELDS", (szYields, make_pedia_link(improvement.getDescription()))))
		szText = u"\n".join([bullet + szLine for szLine in lines])
		screen.addMultilineText(self.top.getNextWidgetName(), SASTextScale.labelText(szText), self.X_SPECIAL + 10, self.Y_SPECIAL + 30, self.W_SPECIAL - 20, h - 40, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)


# <!-- custom: AdvCiv stores a variable-length list; its Python accessor returns NO_BONUS past the last entry. (GPT-6.1-Sol) -->
def getRoutePrereqOrBonuses(info):
	bonuses = []
	iBonus = info.getPrereqOrBonus(0)
	while iBonus >= 0:
		bonuses.append(iBonus)
		iBonus = info.getPrereqOrBonus(len(bonuses))
	return bonuses


# <!-- custom: How an event trigger relates to a route, in display order. (Claude code Opus 5.5) -->
ROUTE_RELATION_REQUIRES = 0
ROUTE_RELATION_ADDS = 1
ROUTE_RELATION_REMOVES = 2


# <!-- custom: Returns how a trigger relates to the route: it requires the route on its plot, or one of its events adds or removes it.
# An event with no RouteType and a negative iRouteChange removes whatever route the plot has, which is this route when the trigger requires it. (Claude code Opus 5.5) -->
def getRouteEventTriggerRelations(iTrigger, iRoute):
	trigger = gc.getEventTriggerInfo(iTrigger)
	bRequires = False
	for i in xrange(trigger.getNumRoutesRequired()):
		if trigger.getRouteRequired(i) == iRoute:
			bRequires = True
			break
	bAdds = False
	bRemoves = False
	for i in xrange(trigger.getNumEvents()):
		iEvent = trigger.getEvent(i)
		if iEvent < 0:
			continue
		event = gc.getEventInfo(iEvent)
		iChange = event.getRouteChange()
		if event.getRoute() == iRoute:
			if iChange > 0:
				bAdds = True
			elif iChange < 0:
				bRemoves = True
		elif event.getRoute() < 0 and iChange < 0 and bRequires:
			bRemoves = True
	relations = []
	if bRequires:
		relations.append(ROUTE_RELATION_REQUIRES)
	if bAdds:
		relations.append(ROUTE_RELATION_ADDS)
	if bRemoves:
		relations.append(ROUTE_RELATION_REMOVES)
	return relations

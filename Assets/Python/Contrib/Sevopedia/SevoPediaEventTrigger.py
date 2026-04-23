# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)


# <!-- custom: Sevopedia Event Trigger detail page. Layout mirrors SevoPediaBuild:
# - Top strip: trigger icon/name/type header + small Probability/Flags panel + Requires panel
# - Mid strip: horizontal stack of "Choices" cards (one per event in getNumEvents()), each
#   showing the event's icon, name and bullet-effect summary — a la Slay the Spire outcomes
# - Bottom: Family panel (sibling triggers sharing the stripped-suffix root) + Civilopedia
#   Background expandable panel
# The page treats the trigger as the dominant entity (matches player's mental model: the
# trigger is "what happens", events are "the choices when it fires"). (Claude code Opus 4.7) -->

from CvPythonExtensions import *
import CvUtil
import SevoScreenEnums
import SASTextScale

from _sevopedia_helpers import *
from _sevopedia_debuggers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

IS_DEBUG_SEVOPEDIA_EVENT_TRIGGER_INFO = True


# <!-- custom: strip trigger "family suffix" so siblings in a family share a root.
# Example: EVENTTRIGGER_FESTIVAL / EVENTTRIGGER_FESTIVAL_AGAIN / EVENTTRIGGER_FESTIVAL_DONE
# all share root EVENTTRIGGER_FESTIVAL. Used by the Family panel to find siblings.
# (Claude code Opus 4.7) -->
def _stripFamilySuffix(szType):
	if not szType:
		return szType
	for szSuffix in ("_AGAIN", "_DONE", "_REVEALED"):
		if szType.endswith(szSuffix):
			return szType[:-len(szSuffix)]
	return szType


class SevoPediaEventTrigger:

	def __init__(self, main):
		self.iTrigger = -1
		self.top = main
		self.bHistoryExpanded = False

		# Full-width Name row at the top (like Votes' Name panel). Trigger has no button
		# art of its own in general, so we skip the icon pane entirely and surface the
		# trigger name + type directly — this reads better than a large empty icon frame.
		self.X_NAME = self.top.X_PEDIA_PAGE
		self.Y_NAME = self.top.Y_PEDIA_PAGE
		self.W_NAME = self.top.R_PEDIA_PAGE - self.X_NAME
		self.H_NAME = 75

		# Trigger info row: Requires | Summary | Family (three equal-ish columns).
		# Requires sits leftmost because "what has to be true for this to fire" reads
		# before "how often / what flags" and "what other variants exist".
		iColGap = MEDIUM_MARGIN
		iRowTop = self.Y_NAME + self.H_NAME + SMALL_MARGIN
		iRowH = 180
		iAvailableW = self.W_NAME - 2 * iColGap
		iColW = iAvailableW / 3

		self.X_REQUIREMENTS = self.X_NAME
		self.Y_REQUIREMENTS = iRowTop
		self.W_REQUIREMENTS = iColW
		self.H_REQUIREMENTS = iRowH

		self.X_SUMMARY = self.X_REQUIREMENTS + self.W_REQUIREMENTS + iColGap
		self.Y_SUMMARY = iRowTop
		self.W_SUMMARY = iColW
		self.H_SUMMARY = iRowH

		self.X_FAMILY = self.X_SUMMARY + self.W_SUMMARY + iColGap
		self.Y_FAMILY = iRowTop
		self.W_FAMILY = self.top.R_PEDIA_PAGE - self.X_FAMILY
		self.H_FAMILY = iRowH

		# Events row (Slay-the-Spire-style horizontal choice cards) — fixed height so
		# the cards stay proportionate instead of stretching to fill leftover vertical
		# space. Anchored directly under the trigger info row.
		self.X_EVENTS = self.X_NAME
		self.Y_EVENTS = iRowTop + iRowH + SMALL_MARGIN
		self.W_EVENTS = self.W_NAME
		self.H_EVENTS = 400

		# History/Civilopedia fills the remaining page space.
		self.X_HISTORY = self.X_NAME
		self.Y_HISTORY = self.Y_EVENTS + self.H_EVENTS + SMALL_MARGIN
		self.W_HISTORY = self.W_NAME
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY

		# Event-card layout constants.
		self.EVENT_CARD_BUTTON_BOTTOM_MARGIN = 12
		self.EVENT_CARD_BUTTON_SIZE = 48
		self.EVENT_CARD_PANEL_HEADER_H = 28

		self.BULLET_PREFIX = u"%c " % CyGame().getSymbolID(FontSymbols.BULLET_CHAR)


	def interfaceScreen(self, iTrigger):
		bTriggerChanged = (self.iTrigger != iTrigger)
		if bTriggerChanged:
			self.bHistoryExpanded = False
		self.iTrigger = iTrigger
		if IS_DEBUG_SEVOPEDIA_EVENT_TRIGGER_INFO and bTriggerChanged:
			self._debugDumpTriggerAndEvents()

		# Order top-to-bottom: trigger identity first (Name), then trigger metadata row
		# (Requires / Summary / Family), then events ("choices" shown as cards), then
		# the flavor Civilopedia panel at the bottom.
		self.placeName()
		self.placeRequirements()
		self.placeSummary()
		self.placeFamily()
		self.placeEvents()
		self.placeHistory()


	def _debugDumpTriggerAndEvents(self):
		info = self._getTriggerInfo()
		if not info:
			return
		print("\n\n[DEBUG] SevoPediaEventTrigger trigger dump: iTrigger=%d, Type=%s" % (self.iTrigger, info.getType()))
		printObjAttrs(info)
		for i in range(info.getNumEvents()):
			iEvent = info.getEvent(i)
			if iEvent < 0:
				continue
			eventInfo = gc.getEventInfo(iEvent)
			if not eventInfo:
				continue
			print("\n\n[DEBUG] SevoPediaEventTrigger event dump: iEvent=%d, Type=%s" % (iEvent, eventInfo.getType()))
			printObjAttrs(eventInfo)


	def _getTriggerInfo(self):
		if self.iTrigger < 0:
			return None
		return gc.getEventTriggerInfo(self.iTrigger)


	def _getTriggerDisplayName(self):
		info = self._getTriggerInfo()
		if not info:
			return localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_UNKNOWN", ())
		szName = info.getDescription()
		if szName and len(szName.strip()) > 0:
			return szName
		szType = info.getType()
		if szType and szType.startswith("EVENTTRIGGER_"):
			szType = szType[len("EVENTTRIGGER_"):]
		if szType:
			return szType.replace("_", " ").title()
		return localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_UNKNOWN", ())


	def placeName(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SAS_VOTE_NAME", ()), "", True, False, self.X_NAME, self.Y_NAME, self.W_NAME, self.H_NAME, PanelStyles.PANEL_STYLE_BLUE50)

		info = self._getTriggerInfo()
		szDisplayName = self._getTriggerDisplayName()
		szType = ""
		if info:
			szType = info.getType()
		szLine = self.BULLET_PREFIX + szDisplayName
		if szType:
			szLine = szLine + u"  (" + szType + u")"
		screen.addMultilineText(self.top.getNextWidgetName(), SASTextScale.labelText(szLine), self.X_NAME + 14, self.Y_NAME + 30, self.W_NAME - 28, self.H_NAME - 36, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)


	def placeSummary(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_SUMMARY", ()), "", True, False, self.X_SUMMARY, self.Y_SUMMARY, self.W_SUMMARY, self.H_SUMMARY, PanelStyles.PANEL_STYLE_BLUE50)

		info = self._getTriggerInfo()
		lines = []
		if info:
			lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_PROBABILITY", ()) + u": %d" % info.getProbability())
			lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_ACTIVE_GAMES", ()) + u": %d%%" % info.getPercentGamesActive())
			lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_OUTCOME_COUNT", ()) + u": %d" % info.getNumEvents())
			listFlags = []
			if info.isRecurring():
				listFlags.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_FLAG_RECURRING", ()))
			if info.isGlobal():
				listFlags.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_FLAG_GLOBAL", ()))
			if info.isTeam():
				listFlags.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_FLAG_TEAM", ()))
			if info.isSinglePlayer():
				listFlags.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_FLAG_SINGLE_PLAYER", ()))
			if listFlags:
				szFlags = u", ".join(listFlags)
			else:
				szFlags = localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_NONE", ())
			lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_FLAGS", ()) + u": " + szFlags)

		if lines:
			szText = u"\n".join(lines)
		else:
			szText = localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_NONE", ())
		screen.addMultilineText(self.top.getNextWidgetName(), SASTextScale.labelText(szText), self.X_SUMMARY + 14, self.Y_SUMMARY + 34, self.W_SUMMARY - 28, self.H_SUMMARY - 44, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)


	def _joinInfoNames(self, listIds, infoGetter):
		listNames = []
		for iId in listIds:
			if iId >= 0:
				info = infoGetter(iId)
				if info:
					listNames.append(info.getDescription())
		if listNames:
			return u", ".join(listNames)
		return localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_NONE", ())


	def placeRequirements(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", True, False, self.X_REQUIREMENTS, self.Y_REQUIREMENTS, self.W_REQUIREMENTS, self.H_REQUIREMENTS, PanelStyles.PANEL_STYLE_BLUE50)

		info = self._getTriggerInfo()
		lines = []
		if info:
			listOrTechs = [info.getPrereqOrTechs(i) for i in range(info.getNumPrereqOrTechs())]
			listAndTechs = [info.getPrereqAndTechs(i) for i in range(info.getNumPrereqAndTechs())]
			listObsoleteTechs = [info.getObsoleteTech(i) for i in range(info.getNumObsoleteTechs())]

			if listOrTechs:
				lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_OR_TECHS", ()) + u": " + self._joinInfoNames(listOrTechs, gc.getTechInfo))
			if listAndTechs:
				lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_AND_TECHS", ()) + u": " + self._joinInfoNames(listAndTechs, gc.getTechInfo))
			if listObsoleteTechs:
				lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_OBSOLETE_TECHS", ()) + u": " + self._joinInfoNames(listObsoleteTechs, gc.getTechInfo))

			iCivic = info.getCivic()
			if iCivic >= 0:
				civicInfo = gc.getCivicInfo(iCivic)
				if civicInfo:
					lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_CIVIC", ()) + u": " + civicInfo.getDescription())

			if info.getMinPopulation() > 0:
				lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_MIN_POP", ()) + u": %d" % info.getMinPopulation())
			if info.getMaxPopulation() > 0:
				lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_MAX_POP", ()) + u": %d" % info.getMaxPopulation())
			if info.getMinTreasury() > 0:
				lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_MIN_TREASURY", ()) + u": %d" % info.getMinTreasury())
			if info.getNumUnits() > 0:
				lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_CITY_UNITS", ()) + u": %d" % info.getNumUnits())
			if info.getNumBuildings() > 0:
				lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_CITY_BUILDINGS", ()) + u": %d" % info.getNumBuildings())
			if info.getNumUnitsGlobal() > 0:
				lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_GLOBAL_UNITS", ()) + u": %d" % info.getNumUnitsGlobal())
			if info.getNumBuildingsGlobal() > 0:
				lines.append(self.BULLET_PREFIX + localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_GLOBAL_BUILDINGS", ()) + u": %d" % info.getNumBuildingsGlobal())

		if lines:
			szText = u"\n".join(lines)
		else:
			szText = localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_NONE", ())
		screen.addMultilineText(self.top.getNextWidgetName(), SASTextScale.labelText(szText), self.X_REQUIREMENTS + 14, self.Y_REQUIREMENTS + 34, self.W_REQUIREMENTS - 28, self.H_REQUIREMENTS - 44, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)


	def _formatEventEffectSummary(self, iEvent):
		eventInfo = gc.getEventInfo(iEvent)
		if not eventInfo:
			return localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_NONE", ())

		parts = []
		if eventInfo.getGold() != 0:
			parts.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_EFFECT_GOLD", ()) + u": %+d" % eventInfo.getGold())
		if eventInfo.getRandomGold() != 0:
			parts.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_EFFECT_RANDOM_GOLD", ()) + u": %+d" % eventInfo.getRandomGold())
		if eventInfo.getCulture() != 0:
			parts.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_EFFECT_CULTURE", ()) + u": %+d" % eventInfo.getCulture())
		if eventInfo.getEspionagePoints() != 0:
			parts.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_EFFECT_ESPIONAGE", ()) + u": %+d" % eventInfo.getEspionagePoints())
		if eventInfo.getHappyTurns() != 0:
			parts.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_EFFECT_HAPPY_TURNS", ()) + u": %d" % eventInfo.getHappyTurns())
		if eventInfo.getPopulationChange() != 0:
			parts.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_EFFECT_POPULATION", ()) + u": %+d" % eventInfo.getPopulationChange())
		if eventInfo.isGoldenAge():
			parts.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_EFFECT_GOLDEN_AGE", ()))
		if eventInfo.isDeclareWar():
			parts.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_EFFECT_DECLARE_WAR", ()))

		iTech = eventInfo.getTech()
		if iTech >= 0:
			techInfo = gc.getTechInfo(iTech)
			if techInfo:
				parts.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_EFFECT_FREE_TECH", ()) + u": " + techInfo.getDescription())
		elif eventInfo.getTechPercent() > 0:
			parts.append(localText.getText("TXT_KEY_PEDIA_SAS_EVENT_EFFECT_TECH_PERCENT", ()) + u": %d%%" % eventInfo.getTechPercent())

		if not parts:
			return localText.getText("TXT_KEY_PEDIA_SAS_EVENT_EFFECT_SCRIPTED", ())
		return u"\n".join([self.BULLET_PREFIX + p for p in parts])


	def _getEventDisplayName(self, iEvent):
		eventInfo = gc.getEventInfo(iEvent)
		if not eventInfo:
			return localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_UNKNOWN", ())
		szName = eventInfo.getDescription()
		if szName and len(szName.strip()) > 0:
			return szName
		szType = eventInfo.getType()
		if szType and szType.startswith("EVENT_"):
			szType = szType[len("EVENT_"):]
		if szType:
			return szType.replace("_", " ").title()
		return localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_UNKNOWN", ())


	def placeEvents(self):
		screen = self.top.getScreen()
		info = self._getTriggerInfo()

		# Header panel covers the full events strip; per-event "choice cards" live inside.
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_EVENTS_HEADER", ()), "", True, False, self.X_EVENTS, self.Y_EVENTS, self.W_EVENTS, self.H_EVENTS, PanelStyles.PANEL_STYLE_BLUE50)

		if not info:
			return

		events = []
		for i in range(info.getNumEvents()):
			iEvent = info.getEvent(i)
			if iEvent < 0:
				continue
			eventInfo = gc.getEventInfo(iEvent)
			if not eventInfo:
				continue
			events.append((iEvent, eventInfo))

		if not events:
			noneText = localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_NONE", ())
			screen.addMultilineText(self.top.getNextWidgetName(), SASTextScale.labelText(noneText), self.X_EVENTS + 10, self.Y_EVENTS + 30, self.W_EVENTS - 20, self.H_EVENTS - 40, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
			return

		cardCount = len(events)
		# Per-card panel geometry — cards sit inside the events strip, offset below its header.
		cardMargin = 4
		cardGap = 4
		cardInnerMargin = 4
		panelGap = 4
		innerX = self.X_EVENTS + cardMargin
		innerY = self.Y_EVENTS + self.EVENT_CARD_PANEL_HEADER_H + 2
		innerW = self.W_EVENTS - (2 * cardMargin)
		innerH = self.H_EVENTS - self.EVENT_CARD_PANEL_HEADER_H - cardMargin - 2

		cardW = (innerW - ((cardCount - 1) * cardGap)) / cardCount
		cardH = innerH

		availableInnerH = cardH - (2 * cardInnerMargin) - panelGap
		minSummaryPanelH = self.EVENT_CARD_BUTTON_SIZE + self.EVENT_CARD_BUTTON_BOTTOM_MARGIN + 24
		namePanelH = 200
		maxNamePanelH = availableInnerH - minSummaryPanelH
		if namePanelH > maxNamePanelH:
			namePanelH = maxNamePanelH
		if namePanelH < 44:
			namePanelH = 44

		for i, (iEvent, eventInfo) in enumerate(events):
			cardX = innerX + (i * (cardW + cardGap))
			cardY = innerY

			namePanelX = cardX + cardInnerMargin
			namePanelY = cardY + cardInnerMargin
			namePanelW = cardW - (2 * cardInnerMargin)

			summaryPanelX = namePanelX
			summaryPanelY = namePanelY + namePanelH + panelGap
			summaryPanelW = namePanelW
			summaryPanelH = availableInnerH - namePanelH

			namePanel = self.top.getNextWidgetName()
			screen.addPanel(namePanel, "", "", False, False, namePanelX, namePanelY, namePanelW, namePanelH, PanelStyles.PANEL_STYLE_BLUE50)

			summaryPanel = self.top.getNextWidgetName()
			screen.addPanel(summaryPanel, "", "", False, False, summaryPanelX, summaryPanelY, summaryPanelW, summaryPanelH, PanelStyles.PANEL_STYLE_BLUE50)

			szName = self._getEventDisplayName(iEvent)
			textMarginX = 10
			textMarginY = 8
			screen.addMultilineText(self.top.getNextWidgetName(), SASTextScale.labelText(szName), namePanelX + textMarginX, namePanelY + textMarginY, namePanelW - (textMarginX * 2), namePanelH - (textMarginY * 2), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

			szSummary = self._formatEventEffectSummary(iEvent)
			buttonTopRel = summaryPanelH - self.EVENT_CARD_BUTTON_SIZE - self.EVENT_CARD_BUTTON_BOTTOM_MARGIN
			summaryTextTop = textMarginY
			summaryTextH = buttonTopRel - summaryTextTop - 6
			if summaryTextH < 20:
				summaryTextH = 20
			screen.addMultilineText(self.top.getNextWidgetName(), SASTextScale.labelText(szSummary), summaryPanelX + textMarginX, summaryPanelY + summaryTextTop, summaryPanelW - (textMarginX * 2), summaryTextH, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

			szEventButton = eventInfo.getButton()
			if szEventButton:
				btnX = (summaryPanelW - self.EVENT_CARD_BUTTON_SIZE) / 2
				screen.setImageButtonAt(self.top.getNextWidgetName(), summaryPanel, szEventButton, btnX, buttonTopRel, self.EVENT_CARD_BUTTON_SIZE, self.EVENT_CARD_BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, iEvent, 1)


	def placeFamily(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_FAMILY", ()), "", True, False, self.X_FAMILY, self.Y_FAMILY, self.W_FAMILY, self.H_FAMILY, PanelStyles.PANEL_STYLE_BLUE50)

		info = self._getTriggerInfo()
		lines = []
		if info:
			szRoot = _stripFamilySuffix(info.getType())
			for iOther in range(gc.getNumEventTriggerInfos()):
				if iOther == self.iTrigger:
					continue
				otherInfo = gc.getEventTriggerInfo(iOther)
				if not otherInfo:
					continue
				if _stripFamilySuffix(otherInfo.getType()) == szRoot:
					lines.append(self.BULLET_PREFIX + otherInfo.getType())

		if lines:
			szText = u"\n".join(lines)
		else:
			szText = localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_NONE", ())
		screen.addMultilineText(self.top.getNextWidgetName(), SASTextScale.labelText(szText), self.X_FAMILY + 14, self.Y_FAMILY + 34, self.W_FAMILY - 28, self.H_FAMILY - 44, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)


	def setHistoryExpanded(self, bExpanded):
		self.bHistoryExpanded = bExpanded


	def placeHistory(self):
		screen = self.top.getScreen()
		szText = u""
		info = self._getTriggerInfo()
		if info:
			szCivilopedia = info.getCivilopedia()
			if szCivilopedia and len(szCivilopedia.strip()) > 0:
				szText = szCivilopedia
		if not szText:
			szText = localText.getText("TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_NONE", ())

		draw_expandable_text_panel(
			screen,
			self.top,
			localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()),
			self.X_HISTORY,
			self.Y_HISTORY,
			self.W_HISTORY,
			self.H_HISTORY,
			szText,
			self.bHistoryExpanded,
			self.top.SAS_PEDIA_PYTHON_HISTORY_EXPAND,
			24
		)


	def handleInput(self, inputClass):
		return 0

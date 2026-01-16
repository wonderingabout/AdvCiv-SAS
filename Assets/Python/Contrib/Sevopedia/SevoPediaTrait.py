# SevoPediaTrait
#
# Copyright (c) 2008 The BUG Mod.
#
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#


from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums

import TraitUtil
from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()


# <!-- custom: Module-level cache for trait statistics. Computed once on first Traits category click,
# then reused for the entire session. Similar pattern to SevoPediaLeader's LEADERS_INFO_CACHED. (Claude Opus 4.5) -->
# traitLeaders: dict of traitId -> [leaderIds] - used to quickly compute per-trait pairing data
# allPairsData: list of (trait1, trait2, count, [leaderIds]) - all trait combinations globally
# allPairsMinMax: (minCount, maxCount) - for ranking bar normalization
TRAIT_STATISTICS_CACHE = None


def precomputeTraitStatisticsCache():
	# Precompute and cache trait statistics data. Called once from SevoPediaMain.placeTraits()
	# on first Traits category click. Returns the cache dict.
	global TRAIT_STATISTICS_CACHE

	if TRAIT_STATISTICS_CACHE is not None:
		return TRAIT_STATISTICS_CACHE

	numTraits = gc.getNumTraitInfos()
	numLeaders = gc.getNumLeaderHeadInfos()

	# Build traitId -> [leaderIds] mapping (used for per-trait pairing lookups)
	traitLeaders = {}
	for iTrait in range(numTraits):
		traitLeaders[iTrait] = []
	for iLeader in range(numLeaders):
		leader = gc.getLeaderHeadInfo(iLeader)
		for iTrait in range(numTraits):
			if leader.hasTrait(iTrait):
				traitLeaders[iTrait].append(iLeader)

	# Build leader -> traits mapping (only leaders with 2+ traits) for all-pairs computation
	leaderTraits = {}
	for iLeader in range(numLeaders):
		leader = gc.getLeaderHeadInfo(iLeader)
		traits = set()
		for iTrait in range(numTraits):
			if leader.hasTrait(iTrait):
				traits.add(iTrait)
		if len(traits) >= 2:
			leaderTraits[iLeader] = traits

	# Count all trait pairs
	pairCounts = {}
	for iLeader, traits in leaderTraits.items():
		traitList = sorted(traits)
		for i in range(len(traitList)):
			for j in range(i + 1, len(traitList)):
				pair = (traitList[i], traitList[j])
				if pair not in pairCounts:
					pairCounts[pair] = []
				pairCounts[pair].append(iLeader)

	# Build sorted all-pairs data
	allPairsData = [(t1, t2, len(ids), sorted(ids)) for (t1, t2), ids in pairCounts.items()]
	allPairsData.sort(key=lambda d: gc.getTraitInfo(d[0]).getDescription() + gc.getTraitInfo(d[1]).getDescription())

	# Precompute min/max for ranking bar normalization
	if allPairsData:
		counts = [d[2] for d in allPairsData]
		allPairsMinMax = (min(counts), max(counts))
	else:
		allPairsMinMax = (0, 0)

	TRAIT_STATISTICS_CACHE = {
		"traitLeaders": traitLeaders,
		"allPairsData": tuple(allPairsData),
		"allPairsMinMax": allPairsMinMax,
	}

	print("Sevopedia Trait statistics cache prebuilt. This should appear only once per gaming session.")
	return TRAIT_STATISTICS_CACHE


class SevoPediaTrait:

	def __init__(self, main):
		self.iTrait = -1
		self.top = main

		# <!-- custom: Enhanced layout - Leaders at top, Statistics in center, Effects bottom-left, History bottom-right.
		# Precompute all layout values once in __init__ for performance. (Claude code Opus 4.5) -->

		MARGIN = 10

		# Leaders panel - full width at top
		self.X_LEADERS = self.top.X_PEDIA_PAGE
		self.Y_LEADERS = self.top.Y_PEDIA_PAGE
		self.W_LEADERS = self.top.R_PEDIA_PAGE - self.X_LEADERS
		self.H_LEADERS = 110

		# Statistics panel - wide center panel
		self.X_STATISTICS = self.top.X_PEDIA_PAGE
		self.Y_STATISTICS = self.Y_LEADERS + self.H_LEADERS + MARGIN
		self.W_STATISTICS = self.top.R_PEDIA_PAGE - self.X_STATISTICS
		self.H_STATISTICS = 585

		# Statistics sub-panels layout (precomputed)
		STATS_MARGIN = 10
		STATS_INNER = 8
		self.STATS_ROW_H = 24
		self.STATS_PANEL_Y = self.Y_STATISTICS + 30
		self.STATS_PANEL_H = self.H_STATISTICS - 40
		self.STATS_PANEL_X = self.X_STATISTICS + STATS_MARGIN
		self.STATS_PANEL_W = self.W_STATISTICS - (2 * STATS_MARGIN)
		self.STATS_INNER = STATS_INNER
		self.STATS_MARGIN = STATS_MARGIN

		# Left panel dimensions
		self.STATS_LEFT_W = int(self.STATS_PANEL_W * 0.44)
		self.STATS_LEFT_TABLE_X = self.STATS_PANEL_X + STATS_INNER
		self.STATS_LEFT_TABLE_W = self.STATS_LEFT_W - (2 * STATS_INNER)
		self.STATS_LEFT_TABLE_Y = self.STATS_PANEL_Y + STATS_INNER
		self.STATS_LEFT_TABLE_H = self.STATS_PANEL_H - (2 * STATS_INNER)

		# Left table column widths
		leftTraitW = int(self.STATS_LEFT_TABLE_W * 0.36)
		leftPairW = 50
		leftTotalW = 50
		leftLeadersW = self.STATS_LEFT_TABLE_W - leftTraitW - leftPairW - leftTotalW
		if leftLeadersW < 100:
			leftLeadersW = 100
			leftTraitW = self.STATS_LEFT_TABLE_W - leftPairW - leftTotalW - leftLeadersW
		if leftTraitW < 120:
			leftTraitW = 120
			leftLeadersW = self.STATS_LEFT_TABLE_W - leftPairW - leftTotalW - leftTraitW
		self.STATS_LEFT_COL_TRAIT = leftTraitW
		self.STATS_LEFT_COL_PAIR = leftPairW
		self.STATS_LEFT_COL_TOTAL = leftTotalW
		self.STATS_LEFT_COL_LEADERS = leftLeadersW

		# Right panel dimensions
		self.STATS_RIGHT_X = self.STATS_PANEL_X + self.STATS_LEFT_W + STATS_MARGIN
		self.STATS_RIGHT_W = self.STATS_PANEL_X + self.STATS_PANEL_W - self.STATS_RIGHT_X
		self.STATS_RIGHT_TABLE_X = self.STATS_RIGHT_X + STATS_INNER
		self.STATS_RIGHT_TABLE_W = self.STATS_RIGHT_W - (2 * STATS_INNER)
		self.STATS_RIGHT_TABLE_Y = self.STATS_PANEL_Y + STATS_INNER
		self.STATS_RIGHT_TABLE_H = self.STATS_PANEL_H - (2 * STATS_INNER)

		# Right table column widths
		rightComboW = int(self.STATS_RIGHT_TABLE_W * 0.38)
		rightCountW = 50
		rightRankW = 80
		rightLeadersW = self.STATS_RIGHT_TABLE_W - rightComboW - rightCountW - rightRankW
		if rightLeadersW < 120:
			rightLeadersW = 120
			rightComboW = self.STATS_RIGHT_TABLE_W - rightCountW - rightRankW - rightLeadersW
		if rightComboW < 180:
			rightComboW = 180
			rightLeadersW = self.STATS_RIGHT_TABLE_W - rightCountW - rightRankW - rightComboW
		self.STATS_RIGHT_COL_COMBO = rightComboW
		self.STATS_RIGHT_COL_COUNT = rightCountW
		self.STATS_RIGHT_COL_RANK = rightRankW
		self.STATS_RIGHT_COL_LEADERS = rightLeadersW

		# Bottom row: Effects (left) and History (right)
		Y_BOTTOM_ROW = self.Y_STATISTICS + self.H_STATISTICS + MARGIN
		H_BOTTOM_ROW = self.top.B_PEDIA_PAGE - Y_BOTTOM_ROW

		# Effects panel - bottom left
		self.X_SPECIAL = self.top.X_PEDIA_PAGE
		self.Y_SPECIAL = Y_BOTTOM_ROW
		self.W_SPECIAL = (self.top.R_PEDIA_PAGE - self.X_SPECIAL - MARGIN) / 2
		self.H_SPECIAL = H_BOTTOM_ROW

		# History panel - bottom right
		self.X_HISTORY = self.X_SPECIAL + self.W_SPECIAL + MARGIN
		self.Y_HISTORY = Y_BOTTOM_ROW
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.X_HISTORY
		self.H_HISTORY = H_BOTTOM_ROW



	# <!-- custom: Updated to receive trait ID directly via WIDGET_PYTHON approach (no longer concept-based). (Claude code Opus 4.5) -->
	def interfaceScreen(self, iTrait):
		self.iLeader = -1
		self.iTrait = iTrait

		self.placeLeaders()
		self.placeStatistics()
		self.placeSpecial()
		self.placeHistory()



	def placeLeaders(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		leaderIds, leaderToCiv, totalRealLeaders = get_real_leader_maps_and_count(gc, EXCLUDED_LEADER_TYPES_FROM_SEVOPEDIA)
		leadersWithTrait = []
		for iLeader in leaderIds:
			if gc.getLeaderHeadInfo(iLeader).hasTrait(self.iTrait):
				leadersWithTrait.append(iLeader)

		percent = 0
		if totalRealLeaders > 0:
			percent = (100 * len(leadersWithTrait)) / totalRealLeaders
		headerText = u"%s %d/%d (%d%%)" % (
			localText.getText("TXT_KEY_CONCEPT_LEADERS", ()),
			len(leadersWithTrait),
			totalRealLeaders,
			percent,
		)
		screen.addPanel( panelName, headerText, "", False, True, self.X_LEADERS, self.Y_LEADERS, self.W_LEADERS, self.H_LEADERS, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		for iLeader in leadersWithTrait:
			self.iLeader = iLeader
			iCiv = leaderToCiv.get(iLeader, -1)
			if iCiv == -1:
				continue
			screen.attachImageButton(panelName, "", gc.getLeaderHeadInfo(iLeader).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, iCiv, False)



	# <!-- custom: Statistics panel with two tables:
	# Left: Trait pairings for current trait (trait, paired count, total, leaders)
	# Right: All trait combinations globally with pair count, ranking bar, and leaders
	# Inspired by README_Assets_Rebalancing.md tables. (Claude code Opus 4.5) -->
	def placeStatistics(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SAS_STATISTICS", ()), "", True, True, self.X_STATISTICS, self.Y_STATISTICS, self.W_STATISTICS, self.H_STATISTICS, PanelStyles.PANEL_STYLE_BLUE50)

		pairingData = self._buildTraitPairingData()

		# === LEFT TABLE: Pairings for current trait ===
		if pairingData:
			leftPanelName = self.top.getNextWidgetName()
			screen.addPanel(leftPanelName, "", "", True, True, self.STATS_PANEL_X, self.STATS_PANEL_Y, self.STATS_LEFT_W, self.STATS_PANEL_H, PanelStyles.PANEL_STYLE_BLUE50)

			leftTableName = self.top.getNextWidgetName()
			screen.addTableControlGFC(leftTableName, 4, self.STATS_LEFT_TABLE_X, self.STATS_LEFT_TABLE_Y, self.STATS_LEFT_TABLE_W, self.STATS_LEFT_TABLE_H, True, False, self.STATS_ROW_H, self.STATS_ROW_H, TableStyles.TABLE_STYLE_EMPTY)
			screen.enableSort(leftTableName)

			screen.setTableColumnHeader(leftTableName, 0, localText.getText("TXT_KEY_PEDIA_SAS_TRAIT_HEADER", ()), self.STATS_LEFT_COL_TRAIT)
			screen.setTableColumnHeader(leftTableName, 1, localText.getText("TXT_KEY_PEDIA_SAS_PAIR_COUNT", ()), self.STATS_LEFT_COL_PAIR)
			screen.setTableColumnHeader(leftTableName, 2, localText.getText("TXT_KEY_PEDIA_SAS_TOTAL_COUNT", ()), self.STATS_LEFT_COL_TOTAL)
			screen.setTableColumnHeader(leftTableName, 3, localText.getText("TXT_KEY_CONCEPT_LEADERS", ()), self.STATS_LEFT_COL_LEADERS)

			for otherTrait, pairCount, totalCount, leaderIds in pairingData:
				iRow = screen.appendTableRow(leftTableName)
				otherTraitInfo = gc.getTraitInfo(otherTrait)

				traitText = u"<font=2>%c %s</font>" % (TraitUtil.getIcon(otherTrait), otherTraitInfo.getDescription())
				screen.setTableText(leftTableName, 0, iRow, traitText, "", WidgetTypes.WIDGET_PYTHON, self.top.SAS_PEDIA_PYTHON_TRAIT, otherTrait, CvUtil.FONT_LEFT_JUSTIFY)
				screen.setTableText(leftTableName, 1, iRow, u"<font=2>%d</font>" % pairCount, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
				screen.setTableText(leftTableName, 2, iRow, u"<font=2>%d</font>" % totalCount, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				leaderNames = [gc.getLeaderHeadInfo(iL).getDescription() for iL in leaderIds]
				screen.setTableText(leftTableName, 3, iRow, u"<font=2>%s</font>" % u", ".join(leaderNames), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		# === RIGHT TABLE: All trait combinations globally ===
		# <!-- custom: Use cached all-pairs data for efficiency. (Claude Opus 4.5) -->
		allPairsData, (minCount, maxCount) = self._getAllTraitPairsData()
		if allPairsData:
			rightPanelName = self.top.getNextWidgetName()
			screen.addPanel(rightPanelName, "", "", True, True, self.STATS_RIGHT_X, self.STATS_PANEL_Y, self.STATS_RIGHT_W, self.STATS_PANEL_H, PanelStyles.PANEL_STYLE_BLUE50)

			rightTableName = self.top.getNextWidgetName()
			screen.addTableControlGFC(rightTableName, 4, self.STATS_RIGHT_TABLE_X, self.STATS_RIGHT_TABLE_Y, self.STATS_RIGHT_TABLE_W, self.STATS_RIGHT_TABLE_H, True, False, self.STATS_ROW_H, self.STATS_ROW_H, TableStyles.TABLE_STYLE_EMPTY)
			screen.enableSort(rightTableName)

			screen.setTableColumnHeader(rightTableName, 0, localText.getText("TXT_KEY_PEDIA_SAS_PAIR_COMBO", ()), self.STATS_RIGHT_COL_COMBO)
			screen.setTableColumnHeader(rightTableName, 1, localText.getText("TXT_KEY_PEDIA_SAS_PAIR_COUNT", ()), self.STATS_RIGHT_COL_COUNT)
			screen.setTableColumnHeader(rightTableName, 2, localText.getText("TXT_KEY_PEDIA_SAS_RANKING", ()), self.STATS_RIGHT_COL_RANK)
			screen.setTableColumnHeader(rightTableName, 3, localText.getText("TXT_KEY_CONCEPT_LEADERS", ()), self.STATS_RIGHT_COL_LEADERS)

			for trait1, trait2, pairCount, leaderIds in allPairsData:
				iRow = screen.appendTableRow(rightTableName)

				trait1Info = gc.getTraitInfo(trait1)
				trait2Info = gc.getTraitInfo(trait2)
				pairText = u"<font=2>%c %s + %c %s</font>" % (
					TraitUtil.getIcon(trait1), trait1Info.getDescription(),
					TraitUtil.getIcon(trait2), trait2Info.getDescription())
				screen.setTableText(rightTableName, 0, iRow, pairText, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
				screen.setTableText(rightTableName, 1, iRow, u"<font=2>%d</font>" % pairCount, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				# Ranking bar
				if maxCount > minCount:
					normalized = (pairCount - minCount) * 100 / (maxCount - minCount)
				else:
					normalized = 50
				numPlus = (normalized + 10) / 20
				screen.setTableText(rightTableName, 2, iRow, u"<font=2>%s</font>" % (u"+" * numPlus), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				leaderNames = [gc.getLeaderHeadInfo(iL).getDescription() for iL in leaderIds]
				screen.setTableText(rightTableName, 3, iRow, u"<font=2>%s</font>" % u", ".join(leaderNames), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

	def _buildTraitPairingData(self):
		# <!-- custom: Build per-trait pairing data using cached traitLeaders mapping.
		# Much faster than recomputing the mapping each time. (Claude Opus 4.5) -->
		if self.iTrait < 0:
			return []

		cache = TRAIT_STATISTICS_CACHE
		if cache is None:
			return []  # Cache not built yet (shouldn't happen if called after placeTraits)

		traitLeaders = cache["traitLeaders"]
		leadersWithThisTrait = set(traitLeaders.get(self.iTrait, []))
		if not leadersWithThisTrait:
			return []

		pairingData = []
		for otherTrait, leadersWithOther in traitLeaders.items():
			if otherTrait == self.iTrait:
				continue
			if not leadersWithOther:
				continue
			leadersWithBoth = leadersWithThisTrait.intersection(set(leadersWithOther))
			if leadersWithBoth:
				pairingData.append((otherTrait, len(leadersWithBoth), len(leadersWithOther), sorted(leadersWithBoth)))

		pairingData.sort(key=lambda x: gc.getTraitInfo(x[0]).getDescription())
		return pairingData

	def _getAllTraitPairsData(self):
		# <!-- custom: Return cached all-pairs data. Computed once per session. (Claude Opus 4.5) -->
		cache = TRAIT_STATISTICS_CACHE
		if cache is None:
			return [], (0, 0)
		return cache["allPairsData"], cache["allPairsMinMax"]



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
		screen.attachListBoxGFC( panelName, listName, "", TableStyles.TABLE_STYLE_EMPTY )
		screen.enableSelect(listName, False)

		if self.iLeader != -1:
			leader = gc.getLeaderHeadInfo(self.iLeader)
			trait = gc.getTraitInfo(self.iTrait)
			szText = CyGameTextMgr().parseLeaderTraits(self.iLeader, -1, False, True)
			szSpecial = u""
			bFirst = True
			bFound = False
			bSkip = True
			for line in szText.splitlines():
				if not line.startswith(" "):
					# leader or trait
					if line.find(">%s<" % leader.getDescription()) != -1:
						continue # leader, ignore
					elif line.find(">%s<" % trait.getDescription()) != -1:
						# the trait we want
						bFound = True
						bSkip = False
					else:
						# some other trait
						if bFound:
							break
						bSkip = True
				else:
					if not bSkip:
						if bFirst:
							bFirst = False
						else:
							szSpecial += "\n"
						szSpecial += line[2:]  # strip first two spaces
			if bFound:
				screen.addMultilineText(listName, szSpecial, self.X_SPECIAL+5, self.Y_SPECIAL+32, self.W_SPECIAL-10, self.H_SPECIAL-40, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: History panel showing civilopedia text for the trait, similar to SevoPediaImprovement. (Claude code Opus 4.5) -->
	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)

		szText = gc.getTraitInfo(self.iTrait).getCivilopedia()
		# Don't display the text key if text not found
		if szText and not szText.endswith("PEDIA"):
			textName = self.top.getNextWidgetName()
			screen.addMultilineText(textName, szText, self.X_HISTORY + 7, self.Y_HISTORY + 30, self.W_HISTORY - 14, self.H_HISTORY - 40, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

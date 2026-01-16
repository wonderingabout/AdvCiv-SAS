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

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



class SevoPediaTrait:

	def __init__(self, main):
		self.iTrait = -1
		self.top = main

		# <!-- custom: Enhanced layout - Leaders at top, Statistics in center, Effects bottom-left, History bottom-right.
		# Dynamically fills the page. Statistics panel is placeholder for future trait usage tables. (Claude Opus 4.5) -->

		self.MARGIN = 10

		# Leaders panel - full width at top
		self.X_LEADERS = self.top.X_PEDIA_PAGE
		self.Y_LEADERS = self.top.Y_PEDIA_PAGE
		self.W_LEADERS = self.top.R_PEDIA_PAGE - self.X_LEADERS
		self.H_LEADERS = 110

		# Statistics panel - wide center panel (placeholder for future trait statistics tables)
		self.X_STATISTICS = self.top.X_PEDIA_PAGE
		self.Y_STATISTICS = self.Y_LEADERS + self.H_LEADERS + self.MARGIN
		self.W_STATISTICS = self.top.R_PEDIA_PAGE - self.X_STATISTICS
		self.H_STATISTICS = 450

		# Bottom row: Effects (left) and History (right)
		self.Y_BOTTOM_ROW = self.Y_STATISTICS + self.H_STATISTICS + self.MARGIN
		self.H_BOTTOM_ROW = self.top.B_PEDIA_PAGE - self.Y_BOTTOM_ROW

		# Effects panel - bottom left
		self.X_SPECIAL = self.top.X_PEDIA_PAGE
		self.Y_SPECIAL = self.Y_BOTTOM_ROW
		self.W_SPECIAL = (self.top.R_PEDIA_PAGE - self.X_SPECIAL - self.MARGIN) / 2
		self.H_SPECIAL = self.H_BOTTOM_ROW

		# History panel - bottom right
		self.X_HISTORY = self.X_SPECIAL + self.W_SPECIAL + self.MARGIN
		self.Y_HISTORY = self.Y_BOTTOM_ROW
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.X_HISTORY
		self.H_HISTORY = self.H_BOTTOM_ROW



	# <!-- custom: Updated to receive trait ID directly via WIDGET_PYTHON approach (no longer concept-based). (Claude Opus 4.5) -->
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
		screen.addPanel( panelName, localText.getText("TXT_KEY_CONCEPT_LEADERS", ()), "", False, True, self.X_LEADERS, self.Y_LEADERS, self.W_LEADERS, self.H_LEADERS, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		for iLeader in range(gc.getNumLeaderHeadInfos()):
			leader = gc.getLeaderHeadInfo(iLeader)
			if leader.hasTrait(self.iTrait):
				self.iLeader = iLeader
				for iCiv in range(gc.getNumCivilizationInfos()):
					if gc.getCivilizationInfo(iCiv).isLeaders(iLeader):
						screen.attachImageButton(panelName, "", gc.getLeaderHeadInfo(iLeader).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, iCiv, False)
						break



	# <!-- custom: Placeholder panel for future trait statistics/math tables showing trait usage,
	# combinations, rankings, etc. Will use simplified AI personality panel table style. (Claude Opus 4.5) -->
	def placeStatistics(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SAS_STATISTICS", ()), "", True, True, self.X_STATISTICS, self.Y_STATISTICS, self.W_STATISTICS, self.H_STATISTICS, PanelStyles.PANEL_STYLE_BLUE50)
		# Placeholder - statistics tables will be added here later



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



	# <!-- custom: History panel showing civilopedia text for the trait, similar to SevoPediaImprovement. (Claude Opus 4.5) -->
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

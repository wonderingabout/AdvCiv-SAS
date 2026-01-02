## BugUnitNameOptionsTab
##
## Tab for the BUG Unit Name Options.
##
## Copyright (c) 2007-2008 The BUG Mod.
##
## Author: Ruff_Hi

import BugOptionsTab

class BugUnitNameOptionsTab(BugOptionsTab.BugOptionsTab):
	"BUG Unit Name Options Screen Tab"
	
	def __init__(self, screen):
		BugOptionsTab.BugOptionsTab.__init__(self, "UnitNaming", "Unit Naming")

	def create(self, screen):
		tab = self.createTab(screen)
		panel = self.createMainPanel(screen)
		column = self.addOneColumnLayout(screen, panel)
	
		left, center, right = self.addThreeColumnLayout(screen, column, "Options")
		
		self.addCheckbox(screen, left, "UnitNaming__Enabled")
		#self.addCheckbox(screen, center, "MiscHover__UpdateUnitNameOnUpgrade")
		self.addCheckbox(screen, right, "UnitNaming__UseAdvanced")

		# <!-- custom: add or modify unit combat types. (GPT-5.2-Codex (summarized)) -->
		columnL, columnR = self.addTwoColumnLayout(screen, column, "UnitNaming")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Default")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_AIR_BOMBER")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_AIR_FIGHTER")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_ARCHER_BOW_SHORT")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_ARCHER_BOW_LONG")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_ARCHER_CROSSBOW")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_ARMOR")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_GUN")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_HELICOPTER")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_MELEE")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_MOUNTED_MELEE")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_MOUNTED_RANGED")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_NAVAL")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_None")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_RECON")
		self.addTextEdit(screen, columnL, columnR, "UnitNaming__Combat_SIEGE")

# <!-- custom: imported from RFC Dawn of Civilization mod:
#C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\RFC Dawn of Civilization\Assets\Python\Pedia\CvPediaUnitChart.py
# which may be modified or not for AdvCiv-SAS
# 
# parts of this code have also been imported from base advciv:
# https://github.com/f1rpo/AdvCiv/blob/master/Assets/Python/Contrib/Sevopedia/SevoPediaUnitChart.py
# and modified or not for AdvCiv-SAS
# -->

from CvPythonExtensions import *
import CvUtil

gc = CyGlobalContext()



class SevoPediaUnitChart:
	def __init__(self, main):
		self.iGroup = -1
		self.top = main

		self.X_TABLE = self.top.X_PEDIA_PAGE
		self.Y_TABLE = self.top.Y_PEDIA_PAGE
		self.W_TABLE = 1100
		self.H_TABLE = self.top.H_PEDIA_PAGE

		self.MARGIN = 20

		self.N_COLUMNS = 9
		self.W_NAMES = 270
		self.W_NUMS = ((self.W_TABLE - (self.MARGIN * 2) - self.W_NAMES) / (self.N_COLUMNS - 1))



	def interfaceScreen(self, iGroup):
		self.iGroup = iGroup
		self.placeUnitTable()



	def placeUnitTable(self):
		screen = self.top.getScreen()
		table = self.top.getNextWidgetName()

		# <!-- custom: blue is more readable than standard i find, imported
		# from base AdvCiv and modified with a similar kind of purpose
		# -->
		#screen.addTableControlGFC(table, self.N_COLUMNS, self.X_TABLE, self.Y_TABLE, self.W_TABLE, self.H_TABLE, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		#screen.setStyle(table, "Table_StandardCiv_Style")
		#screen.enableSort(table)
		screen.addPanel(self.top.getNextWidgetName(), "", "", True, True, self.X_TABLE, self.Y_TABLE, self.W_TABLE, self.H_TABLE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", True, True, self.X_TABLE + self.MARGIN, self.Y_TABLE + self.MARGIN, self.W_TABLE - (self.MARGIN * 2), self.H_TABLE - (self.MARGIN * 2), PanelStyles.PANEL_STYLE_BLUE50)
		table = self.top.getNextWidgetName()
		screen.addTableControlGFC(table,
							self.N_COLUMNS,
							self.X_TABLE + self.MARGIN,
							self.Y_TABLE + self.MARGIN + 5,
							self.W_TABLE - (self.MARGIN * 2),
							self.H_TABLE - (self.MARGIN * 2) - 5,
							True,
							False,
							32,
							32,
							TableStyles.TABLE_STYLE_EMPTY
		)
		screen.enableSort(table)

		szStrength = u"%c" % CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR)

		isSelfAirCombatType = ( (self.iGroup == gc.getInfoTypeForString('UNITCOMBAT_AIR_BOMBER')) or (self.iGroup == gc.getInfoTypeForString('UNITCOMBAT_AIR_FIGHTER')) )
		if isSelfAirCombatType:
			szMoveRange = u"Range"
		else:
			# <!-- custom: display the icon instead of text -->
			#szMoveRange = "Moves"
			szMoveRange = u"%c" % CyGame().getSymbolID(FontSymbols.MOVES_CHAR)

		# <!-- custom: display more potentially useful information,
		# useful in AdvCiv-SAS and/or maybe other mods as well,
		# also so that i don't have to maintain it everytime i make
		# a micro (or big) change, more versatile and flexible this
		# way too.
		# -->
		#if self.iGroup == gc.getInfoTypeForString('UNITCOMBAT_AIR') or self.iGroup == gc.getInfoTypeForString('UNITCOMBAT_NAVAL') or self.iGroup == gc.getInfoTypeForString('UNITCOMBAT_SIEGE'):
			# <!-- custom: imported and modified from base advciv in a similar way -->
			#szSpecial = "Bombard"
		#else:
		#	szSpecial = "1st Strike"
		szFirstStrike = u"1st Strike"
		szBombard = u"%c" % CyGame().getSymbolID(FontSymbols.DEFENSE_CHAR)

		szCollateral = u"Collateral"

		szWithdrawAirEvasion = u""
		if isSelfAirCombatType:
			szWithdrawAirEvasion = u"Air Evasion"
		else:
			szWithdrawAirEvasion = u"Withdraw"

		szCost = u"%c" % gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar()

		szAirIntercept = u"Air Intercept"

		szCost = u"%c" % gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar()

		screen.setTableColumnHeader(table, 0, u"<font=2>" + gc.getUnitCombatInfo(self.iGroup).getDescription() + u"</font>", self.W_NAMES)
		# <!-- custom: trick (to center the headers text too) taught to me by ChatGPT, quoting it:
		# "
		# screen.setTableColumnHeader(...) don't use FONT_*_JUSTIFY like the cell contents, but there's a workaround.
		# Unfortunately, the setTableColumnHeader(...) function in Civ4's Python API does not provide a direct way to align the text (like FONT_CENTER_JUSTIFY). But there is a common workaround:
		# 
		# Workaround: Pad the header label string manually
		# By adding spaces before and after the header text, you can visually center it.
		#  you want to center the header labels in the table (not just the unit entries). The headers set via
		# Example:
		# screen.setTableColumnHeader("UnitChart", 1, "   Unit   ", table_width - 100)
		# You can play with the spacing — more spaces = more centered-looking text depending on the column width.
		#
		# Optional enhancement: Use a monospaced font for table headers
		# If your font is monospaced (unlikely in Civ4 UI), the manual padding is more predictable. In Civ4, though, font kerning varies — so some trial and error is needed.
		# 
		# Advanced modding option (if you're feeling bold)
		# If you're okay with digging into the SDK or custom DLL builds (like AdvCiv or BUG), it’s technically possible to modify the table rendering to expose alignment options for headers. But this is definitely a bigger job — the manual padding is the easiest trick.
		# "
		# May also serve for future reference maybe, anyways, thanks a lot ChatGPT, and to those who advised me or told me
		# about how i could use it, in particular for civ4, or/and or things to thank for or not, anyways,
		#  -->
		screen.setTableColumnHeader(table, 1, u"<font=2>        " + szStrength + u"        </font>", self.W_NUMS)
		screen.setTableColumnHeader(table, 2, u"<font=2>        " + szMoveRange + u"        </font>", self.W_NUMS)
		screen.setTableColumnHeader(table, 3, u"<font=2>   " + szFirstStrike + u"   </font>", self.W_NUMS)
		screen.setTableColumnHeader(table, 4, u"<font=2>        " + szBombard + u"        </font>", self.W_NUMS)
		screen.setTableColumnHeader(table, 5, u"<font=2>  " + szCollateral + u"   </font>", self.W_NUMS)
		screen.setTableColumnHeader(table, 6, u"<font=2>  " + szWithdrawAirEvasion + u" </font>", self.W_NUMS)
		screen.setTableColumnHeader(table, 7, u"<font=2>        " + szCost + u"        </font>", self.W_NUMS)
		screen.setTableColumnHeader(table, 8, u"<font=2>" + szAirIntercept + u"</font>", self.W_NUMS)

		for iUnit in xrange(gc.getNumUnitInfos()):
			UnitInfo = gc.getUnitInfo(iUnit)
			if self.iGroup == UnitInfo.getUnitCombatType():
				iRow = screen.appendTableRow(table)

				# Name
				iCol = 0
				screen.setTableText(table, iCol, iRow, u"<font=3>" + UnitInfo.getDescription() + u"</font>", UnitInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, CvUtil.FONT_LEFT_JUSTIFY)

				# Combat Strength
				iCol += 1
				if UnitInfo.getAirCombat() > 0:
					szCombatNum = u"%d" % UnitInfo.getAirCombat()
				else:
					szCombatNum = u"%d" % UnitInfo.getCombat()

				screen.setTableInt(table, iCol, iRow, u"<font=3>" + szCombatNum + u"</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				# Movement
				iCol += 1
				if UnitInfo.getAirRange() > 0:
					szMovesNum = u"%d" % UnitInfo.getAirRange()
				else:
					szMovesNum = u"%d" % UnitInfo.getMoves()

				screen.setTableInt(table, iCol, iRow, u"<font=3>" + szMovesNum + u"</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				# First Strikes
				iCol += 1
				if UnitInfo.getFirstStrikes() > 0:
					szBombardRate = u"%d" % UnitInfo.getFirstStrikes()
				# <!-- custom: keeping this beautification as it is a lot more
				# useful/readable than having tons of 0s, anyways -->
				else:
					szBombardRate = u""

				screen.setTableInt(table, iCol, iRow, u"<font=3>" + szBombardRate + u"</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				# Bombard
				iCol += 1
				if UnitInfo.getBombardRate() > 0:
					szBombardRate = u"%d%%" % UnitInfo.getBombardRate()
				elif UnitInfo.getBombRate() > 0:
					szBombardRate = u"%d%%" % UnitInfo.getBombRate()
				else:
					szBombardRate = u""

				screen.setTableInt(table, iCol, iRow, u"<font=3>" + szBombardRate + u"</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				# Collateral
				iCol += 1
				if UnitInfo.getCollateralDamage() > 0:
					szCollateralRate = u"%d%% (%d)" % (UnitInfo.getCollateralDamageLimit(), UnitInfo.getCollateralDamageMaxUnits())
				else:
					szCollateralRate = u""

				screen.setTableInt(table, iCol, iRow, u"<font=3>" + szCollateralRate + u"</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				# Withdrawal / Air Evasion
				iCol += 1
				if isSelfAirCombatType and UnitInfo.getEvasionProbability() > 0:
					szWithdrawalAirEvasionRate = u"%d%%" % UnitInfo.getEvasionProbability()
				elif UnitInfo.getWithdrawalProbability() > 0:
					szWithdrawalAirEvasionRate = u"%d%%" % UnitInfo.getWithdrawalProbability()
				else:
					szWithdrawalAirEvasionRate = u""

				screen.setTableInt(table, iCol, iRow, u"<font=3>" + szWithdrawalAirEvasionRate + u"</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				# Cost
				iCol += 1
				if UnitInfo.getProductionCost() < 0:
					szCostNum = CyTranslator().getText("TXT_KEY_NON_APPLICABLE", ())
				else:
					szCostNum = u"%d" % UnitInfo.getProductionCost()

				screen.setTableInt(table, iCol, iRow, u"<font=3>" + szCostNum + u"</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				# Air Interception
				iCol += 1
				if UnitInfo.getInterceptionProbability() > 0:
					szAirInterceptionRate = u"%d%%" % (UnitInfo.getInterceptionProbability())
				else:
					szAirInterceptionRate = u""

				screen.setTableInt(table, iCol, iRow, u"<font=3>" + szAirInterceptionRate + u"</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)



	# <!-- custom: seems we never call this function, commenting it out,
	# may even be deleted maybe(?) -->
	#def handleInput(self, inputClass):
	#	return 0

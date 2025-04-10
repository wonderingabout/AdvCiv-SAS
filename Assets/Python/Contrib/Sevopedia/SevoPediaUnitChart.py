# imported from RFC Dawn of Civilization mod:
#C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\RFC Dawn of Civilization\Assets\Python\Pedia\CvPediaUnitChart.py
# which may be modified or not for AdvCiv-SAS

from CvPythonExtensions import *
import CvUtil

gc = CyGlobalContext()



class SevoPediaUnitChart:
	def __init__(self, main):
		self.iGroup = -1
		self.top = main

		self.X_TABLE = self.top.X_PEDIA_PAGE
		self.Y_TABLE = self.top.Y_PEDIA_PAGE
		self.W_TABLE = 1000
		self.H_TABLE = self.top.H_PEDIA_PAGE

		self.MARGIN = 20



	def interfaceScreen(self, iGroup):
		self.iGroup = iGroup
		self.placeUnitTable()



	def placeUnitTable(self):
		screen = self.top.getScreen()
		table = self.top.getNextWidgetName()

		nColumns = 8
		# <!-- custom: blue is more readable than standard i find, imported
		# from base AdvCiv and modified with a similar kind of purpose
		# -->
		#screen.addTableControlGFC(table, nColumns, self.X_TABLE, self.Y_TABLE, self.W_TABLE, self.H_TABLE, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		#screen.setStyle(table, "Table_StandardCiv_Style")
		#screen.enableSort(table)
		screen.addPanel(self.top.getNextWidgetName(), "", "", True, True, self.X_TABLE, self.Y_TABLE, self.W_TABLE, self.H_TABLE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", True, True, self.X_TABLE + self.MARGIN, self.Y_TABLE + self.MARGIN, self.W_TABLE - (self.MARGIN * 2), self.H_TABLE - (self.MARGIN * 2), PanelStyles.PANEL_STYLE_BLUE50)
		table = self.top.getNextWidgetName()
		screen.addTableControlGFC(table, nColumns, self.X_TABLE + self.MARGIN, self.Y_TABLE + self.MARGIN + 5, self.W_TABLE - (self.MARGIN * 2), self.H_TABLE - (self.MARGIN * 2) - 5, True, False, 32,32, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSort(table)

		selfIsAirUnit = ( (self.iGroup == gc.getInfoTypeForString('UNITCOMBAT_AIR_BOMBER')) or (self.iGroup == gc.getInfoTypeForString('UNITCOMBAT_AIR_FIGHTER')) )

		if selfIsAirUnit:
			szMove = u"Range"
		else:
			# <!-- custom: imported from based AdvCiv and modified in a
			# similar way as for/in other parts of this code, to display
			# the icon instead of text -->
			#szMove = "Moves"
			szMove = u"%c" % CyGame().getSymbolID(FontSymbols.MOVES_CHAR)

		# <!-- custom: display more potentially useful information,
		# useful in AdvCiv-SAS and/or maybe other mods as well,
		# also so that i don't have to maintain it everytime i make
		# a micro (or big) change, more versatile and flexible this
		# way too.
		# -->
		# if self.iGroup == gc.getInfoTypeForString('UNITCOMBAT_AIR') or self.iGroup == gc.getInfoTypeForString('UNITCOMBAT_NAVAL') or self.iGroup == gc.getInfoTypeForString('UNITCOMBAT_SIEGE'):
			# <!-- custom: imported and modified from base advciv in a similar way -->
			#szFirstStrike = "Bombard"
		szBombard = u"%c" % CyGame().getSymbolID(FontSymbols.DEFENSE_CHAR)

		szFirstStrike = u"1st Strike"

		if selfIsAirUnit:
			szWithdraw = u"Evade"

		else:
			szWithdraw = u"Withdraw"

		iWidthNames = 270
		iWidthNums = ((self.W_TABLE - (self.MARGIN * 2) - iWidthNames) / (nColumns - 1))


		screen.setTableColumnHeader(table, 0, u"<font=2>" + gc.getUnitCombatInfo(self.iGroup).getDescription() + u"</font>", iWidthNames)
		# <!-- custom: add strength icon, imported from base AdvCiv code:
		# https://github.com/f1rpo/AdvCiv/blob/master/Assets/Python/Contrib/Sevopedia/SevoPediaUnitChart.py
		# and modified for AdvCiv-SAS to display the icon instead of text -->
		# -->
		#screen.setTableColumnHeader(table, 1, u"<font=2>" + "Strength" + "</font>", iWidthNums)
		screen.setTableColumnHeader(table, 1, u"%c" % CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR), iWidthNums)
		screen.setTableColumnHeader(table, 2, u"<font=2>" + szMove + u"</font>", iWidthNums)
		screen.setTableColumnHeader(table, 3, u"<font=2>" + szFirstStrike + u"</font>", iWidthNums)
		screen.setTableColumnHeader(table, 4, u"<font=2>" + szBombard + u"</font>", iWidthNums)
		screen.setTableColumnHeader(table, 5, u"<font=2>" + u"Collateral" + u"</font>", iWidthNums)
		screen.setTableColumnHeader(table, 6, u"<font=2>" + szWithdraw + u"</font>", iWidthNums)
		# <!-- custom: imported and modified from base advciv in a similar way -->
		#screen.setTableColumnHeader(table, 6, u"<font=2>" + "Cost" + "</font>", iWidthNums)
		screen.setTableColumnHeader(table, 7, u"%c" % gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar(), iWidthNums)

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
				else:
					szBombardRate = u""

				screen.setTableInt(table, iCol, iRow, u"<font=3>" + szBombardRate + u"</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				# Bombard
				iCol += 1
				if UnitInfo.getBombardRate() > 0:
					szBombardRate = u"%d%%" % UnitInfo.getBombardRate()
				elif UnitInfo.getBombRate() > 0:
					szBombardRate = u"%d%%" % UnitInfo.getBombRate()
				# <!-- custom: keeping this beautification as it is a lot more
				# useful/readable than having tons of 0s, anyways -->
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

				# Withdrawal
				iCol += 1
				if selfIsAirUnit and UnitInfo.getEvasionProbability() > 0:
					szWithdrawalRate = u"%d%%" % UnitInfo.getEvasionProbability()
				elif UnitInfo.getWithdrawalProbability() > 0:
					szWithdrawalRate = u"%d%%" % UnitInfo.getWithdrawalProbability()
				else:
					szWithdrawalRate = u""

				screen.setTableInt(table, iCol, iRow, u"<font=3>" + szWithdrawalRate + u"</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

				# Cost
				iCol += 1
				if UnitInfo.getProductionCost() < 0:
					szCostNum = CyTranslator().getText("TXT_KEY_NON_APPLICABLE", ())
				else:
					szCostNum = u"%d" % UnitInfo.getProductionCost()

				screen.setTableInt(table, iCol, iRow, u"<font=3>" + szCostNum + u"</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)



	# <!-- custom: seems we never call this function, commenting it out,
	# may even be deleted maybe(?) -->
	#def handleInput(self, inputClass):
	#	return 0

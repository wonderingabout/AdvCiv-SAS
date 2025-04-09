# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
#

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
import string

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaBonus:

	def __init__(self, main):
		self.iBonus = -1
		self.top = main

		self.X_BONUS_PANE = self.top.X_PEDIA_PAGE
		self.Y_BONUS_PANE = self.top.Y_PEDIA_PAGE
		self.W_BONUS_PANE = self.top.W_PEDIA_PAGE / 2 - 5
		self.H_BONUS_PANE = 116

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_BONUS_PANE + (self.H_BONUS_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_BONUS_PANE + (self.H_BONUS_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_STATS_PANE = self.X_BONUS_PANE + 110
		self.Y_STATS_PANE = self.Y_BONUS_PANE + 33
		self.W_STATS_PANE = 240
		self.H_STATS_PANE = 200

		self.X_BONUS_ANIMATION = self.X_BONUS_PANE + self.W_BONUS_PANE + 10
		self.Y_BONUS_ANIMATION = self.Y_BONUS_PANE + 7
		self.W_BONUS_ANIMATION = self.top.R_PEDIA_PAGE - self.X_BONUS_ANIMATION 
		self.H_BONUS_ANIMATION = self.H_BONUS_PANE
		self.X_ROTATION_BONUS_ANIMATION = -20
		self.Z_ROTATION_BONUS_ANIMATION = 30
		self.SCALE_ANIMATION = 0.7

		self.X_IMPROVEMENTS_PANE = self.X_BONUS_PANE
		self.W_IMPROVEMENTS_PANE = self.W_BONUS_PANE
		self.Y_IMPROVEMENTS_PANE = self.Y_BONUS_PANE + self.H_BONUS_PANE + 10
		self.H_IMPROVEMENTS_PANE = 110

		self.X_EFFECTS_PANE = self.X_BONUS_ANIMATION
		self.W_EFFECTS_PANE = self.W_BONUS_ANIMATION
		self.Y_EFFECTS_PANE = self.Y_IMPROVEMENTS_PANE
		self.H_EFFECTS_PANE = self.H_IMPROVEMENTS_PANE

		self.X_REVEALED_BY = self.X_BONUS_PANE
		self.W_REVEALED_BY = self.W_BONUS_PANE
		self.Y_REVEALED_BY = self.Y_IMPROVEMENTS_PANE + self.H_IMPROVEMENTS_PANE + 10
		self.H_REVEALED_BY = 110

		# <!-- custom: todo add self.X_ENABLES and similar -->

		self.X_ALLOWS_PANE = self.X_BONUS_PANE
		self.W_ALLOWS_PANE = self.top.R_PEDIA_PAGE - self.X_ALLOWS_PANE
		self.Y_ALLOWS_PANE = self.Y_REVEALED_BY + self.H_REVEALED_BY + 10
		self.H_ALLOWS_PANE = 110

		# <!-- custom: put the buildings panel under the units (allows) panel
		# so easier to refer to it directly, it will also be identical in
		# dimensions (or very close) so we will not need to change much
		# (coordinates or other things) this way -->
		self.X_BUILDINGS = self.X_ALLOWS_PANE
		self.W_BUILDINGS = self.W_ALLOWS_PANE 
		self.Y_BUILDINGS = self.Y_ALLOWS_PANE
		self.H_BUILDINGS = self.H_ALLOWS_PANE

		# <!--custom: not changing the existing math since it was already done,
		# but ideally (i think (?)) should base this on the buildings panel now
		# just above it
		self.X_HISTORY_PANE = self.X_ALLOWS_PANE
		self.W_HISTORY_PANE = self.W_ALLOWS_PANE
		self.Y_HISTORY_PANE = self.Y_ALLOWS_PANE + self.H_ALLOWS_PANE + 10
		self.H_HISTORY_PANE = self.top.B_PEDIA_PAGE - self.Y_HISTORY_PANE



	def interfaceScreen(self, iBonus):
		self.iBonus = iBonus
		screen = self.top.getScreen()

		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False, self.X_BONUS_PANE, self.Y_BONUS_PANE, self.W_BONUS_PANE, self.H_BONUS_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getBonusInfo(self.iBonus).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addBonusGraphicGFC(self.top.getNextWidgetName(), self.iBonus, self.X_BONUS_ANIMATION, self.Y_BONUS_ANIMATION, self.W_BONUS_ANIMATION, self.H_BONUS_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_BONUS_ANIMATION, self.Z_ROTATION_BONUS_ANIMATION, self.SCALE_ANIMATION, True)

		# <!-- custom: Move the panel position, so that it starts from a
		# lower point in the screen.
		# We will use this newly freed place to put the larger Buildings,
		# while we create an Enables panel instead where the Buildings
		# panel was.
		# Hopefully much clearer and more room to fit many buildings this
		# way now, and to separate tech reveals and tech enables,
		# both currently in the "Requires" panel which is very weird i
		# think, will be renamed to to "Reveals")
		# -->
		self.placeStats()
		self.placeYield()
		self.placeSpecial()
		# <!-- custom: split the former/old  placeRequires, into
		# placeRevealedBy and placeEnables (which is hopefully more
		# accurate this way too
		# -->
		self.placeRevealedBy()
		self.placeEnables()
		self.placeAllows()
		self.placeBuildings()
		self.placeHistory()



	def placeStats(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: max box width and height starting position we
		# want to write our text adjusted -->
		#screen.addListBoxGFC(panelName, "", self.X_STATS_PANE, self.Y_STATS_PANE, self.W_STATS_PANE, self.H_STATS_PANE, TableStyles.TABLE_STYLE_EMPTY)
		screen.addListBoxGFC(panelName, "", self.X_STATS_PANE, self.Y_STATS_PANE - 18, self.W_STATS_PANE + 380 , self.H_STATS_PANE, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panelName, False)
		
		for k in range(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = gc.getBonusInfo(self.iBonus).getYieldChange(k)
			if (iYieldChange != 0):
				if (iYieldChange > 0):
					sign = "+"
				else:
					sign = ""
				# <!-- custom: beautify, no need to mention "FOOD: +1",
				# just "+1" is enough especially with the food icon
				# -->
				#szYield = (u"%s: %s%i " % (gc.getYieldInfo(k).getDescription(), sign, iYieldChange))
				szYield = (u"%s%i " % (sign, iYieldChange))
				# <!-- custom: add information about the precise
				# type of yield it is, which can be otherwise very
				# confusing
				# note: used the same logic as in other parts of the
				# code; for example placeStats in SevoPediaProject.py
				# is quite (very) similar and helped quite a lot,
				# should be much more beautiful/pleasant hopefully
				# -->
				#screen.appendListBoxString(panelName, u"<font=3>" + szYield.upper() + (u"%c" % gc.getYieldInfo(k).getChar()) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
				szText = u"<font=4><b>" + localText.getText("TXT_KEY_PEDIA_BONUS_YIELDS_CUSTOM_PANEL_TEXT", ()) + "\n\n" + szYield.upper() + (u"%c" % gc.getYieldInfo(k).getChar()) + u"</b></font>"
				screen.appendListBoxString(panelName, szText, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)



	def placeYield(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_CATEGORY_IMPROVEMENT_CUSTOM_NEW_FOR_RESSOURCES_IMPROVEMENTS", ()), "", True, True, self.X_IMPROVEMENTS_PANE, self.Y_IMPROVEMENTS_PANE, self.W_IMPROVEMENTS_PANE, self.H_IMPROVEMENTS_PANE, PanelStyles.PANEL_STYLE_BLUE50 )
		# <!-- custom: removed unused bonusInfo variable,
		# seems safe
		# -->
		for j in range(gc.getNumImprovementInfos()):
			bFirst = True
			szYield = u""
			bEffect = False
			for k in range(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = gc.getImprovementInfo(j).getImprovementBonusYield(self.iBonus, k)
				if (iYieldChange != 0):
					bEffect = True
					iYieldChange += gc.getImprovementInfo(j).getYieldChange(k)
					if (bFirst):
						bFirst = False
					else:
						szYield += ", "
					if (iYieldChange > 0):
						sign = "+"
					else:
						sign = ""
					szYield += (u"<font=4>%s%i%c</font>" % (sign, iYieldChange, gc.getYieldInfo(k).getChar()))
			if (bEffect):
				childPanelName = self.top.getNextWidgetName()
				screen.attachPanel(panelName, childPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)
				screen.attachLabel(childPanelName, "", "  ")
				screen.attachImageButton(childPanelName, "", gc.getImprovementInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, j, 1, False )
				screen.attachLabel(childPanelName, "", szYield)



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False,
				 self.X_EFFECTS_PANE, self.Y_EFFECTS_PANE, self.W_EFFECTS_PANE, self.H_EFFECTS_PANE, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
		screen.attachListBoxGFC( panelName, listName, "", TableStyles.TABLE_STYLE_EMPTY )
		screen.enableSelect(listName, False)
		szSpecialText = CyGameTextMgr().getBonusHelp(self.iBonus, True)
		splitText = string.split( szSpecialText, "\n" )
		for special in splitText:
			if len( special ) != 0:
				screen.appendListBoxString( listName, special, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )



	def placeRevealedBy(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom:
		# note that TXT_KEY_PEDIA_BONUS_APPEARANCE
		# is "Reveals", using a custom TXT KEY "Revealed By" 
		# TXT_KEY_PEDIA_BONUS_APPEARANCE_REVEALED_BY_CUSTOM
		# specifically for the Sevopedia, because now that we formatted
		# it like that, "Revealed By" would fit better than "Reveals".
		# Stil keeping the old entry intact for the Civilopedia
		# note: "Appearance"/"Reveals" is the logic it seems of an
		# appearance but i still find it very confusing, why not use the
		# same name, but as long as it works is maybe fine
		# -->
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_BONUS_APPEARANCE_REVEALED_BY_CUSTOM", ()), "", False, True, self.X_REVEALED_BY, self.Y_REVEALED_BY, self.W_REVEALED_BY, self.H_REVEALED_BY, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")

		iTech = gc.getBonusInfo(self.iBonus).getTechReveal()
		if (iTech > -1):
			screen.attachImageButton( panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )
			# <!-- custom: we don't need the extra "(Reveals)" or "(Enables)"
			# texts now that they are both not a "requires" anymore (which i
			# think was very inaccurate, now fixed
			# -->
			#screen.attachLabel(panelName, "", u"(" + localText.getText("TXT_KEY_PEDIA_BONUS_APPEARANCE", ()) + u")")



	# <!-- custom: base this on former placeRequires (now split
	# between placeRevealedBy and placeEnables with some adjustments
	# and quite minor tweaks
	# -->
	def placeEnables(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: move it at the right of the requires panel
		# note: self.X_REVEALED_BY + 685 works, but since the new
		# Enables panel is aligned with the effects panel, easier to
		# use same horizontal postion (X)
		# May support much better lower resolutions too, as we would
		# be aligned with effects panel and not too far from it if i
		# am not mistaken
		# note: TXT_KEY_PEDIA_BONUS_TRADE is "Enables"
		# -->
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_BONUS_TRADE", ()), "", False, True, self.X_EFFECTS_PANE, self.Y_REVEALED_BY, self.W_REVEALED_BY, self.H_REVEALED_BY, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")

		iTech = gc.getBonusInfo(self.iBonus).getTechCityTrade()
		if (iTech > -1):
			screen.attachImageButton( panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )
			# <!-- custom: same -->
			#screen.attachLabel(panelName, "", u"(" + localText.getText("TXT_KEY_PEDIA_BONUS_TRADE", ()) + u")")




	def placeAllows(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# advc.905b: txt key was TXT_KEY_PEDIA_ALLOWS
		screen.addPanel( panelName, localText.getText("TXT_KEY_WB_UNITS", ()), "", False, True, self.X_ALLOWS_PANE, self.Y_ALLOWS_PANE, self.W_ALLOWS_PANE, self.H_ALLOWS_PANE, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		iActivePlayer = gc.getGame().getActivePlayer() # advc.003l
		for eLoopUnit in range(gc.getNumUnitInfos()):
			bFound = False
			if (gc.getUnitInfo(eLoopUnit).getPrereqAndBonus() == self.iBonus):
				bFound = True
			else:
				j = 0
				while (not bFound and j < gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
					if (gc.getUnitInfo(eLoopUnit).getPrereqOrBonuses(j) == self.iBonus):
						bFound = True
					j += 1
			# <advc.905b>
			if not bFound:
				for j in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
					if gc.getUnitInfo(eLoopUnit).getSpeedBonuses(j) == self.iBonus:
						bFound = True
						break
			# </advc.905b>
			if bFound:
				szButton = gc.getUnitInfo(eLoopUnit).getButton()
				# <advc.003l>
				if iActivePlayer >= 0:
					szButton = gc.getPlayer(iActivePlayer).getUnitButton(eLoopUnit)
				# </advc.003l>
				screen.attachImageButton( panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, eLoopUnit, 1, False )
		# advc.905b: Allowed buildings moved to placeBuildings



	def placeBuildings(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# advc.004y: txt key was TXT_KEY_PEDIA_CATEGORY_BUILDING
		# <!-- custom: starting the buildings panel from a lower (Y)
		# position, with the horizontal position (X), width of the panel (W),
		# height of the panel (H) are not changed, same as the allows (units)
		# panel.
		# Now the buildings panel will be larger as the units panel, useful
		# for ressources like marble that could not fit all, plus now we have
		# room to create a new Enables panel
		# -->
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_CATEGORY_BUILDING_PROJECT", ()), "", False, True, self.X_BUILDINGS, self.Y_BUILDINGS + 120, self.W_BUILDINGS, self.H_BUILDINGS, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		# advc.905b: Moved this loop from placeAllows, which only deals with units now.
		for eLoopBuilding in range(gc.getNumBuildingInfos()):
			bFound = False
			if (gc.getBuildingInfo(eLoopBuilding).getPrereqAndBonus() == self.iBonus):
				bFound = True
			else:
				j = 0
				while (not bFound and j < gc.getNUM_BUILDING_PREREQ_OR_BONUSES()):
					if (gc.getBuildingInfo(eLoopBuilding).getPrereqOrBonuses(j) == self.iBonus):
						bFound = True
					j += 1
			if bFound:
				screen.attachImageButton( panelName, "", gc.getBuildingInfo(eLoopBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, eLoopBuilding, 1, False )

		for iBuilding in range(gc.getNumBuildingInfos()):
			info = gc.getBuildingInfo(iBuilding)
			bShow = (info.getFreeBonus() == self.iBonus
					or info.getBonusHealthChanges(self.iBonus) > 0
					or info.getBonusHappinessChanges(self.iBonus) > 0
					or info.getBonusProductionModifier(self.iBonus) > 0)
			if (not bShow):
				for eYield in range(YieldTypes.NUM_YIELD_TYPES):
					if (info.getBonusYieldModifier(self.iBonus, eYield) > 0):
						bShow = True
						break
			if (bShow):
				screen.attachImageButton( panelName, "", info.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1, False )
		# <advc.004y>
		for iProject in range(gc.getNumProjectInfos()):
			info = gc.getProjectInfo(iProject)
			if info.getBonusProductionModifier(self.iBonus) != 0:
				screen.attachImageButton(panelName, "", info.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1, False)
		# </advc.004y>



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: make the panel total height (H) smaller,
		# and make it start from a lower point in the screen which is same
		# as having moved it lower in the screen (Y), if i am not mistaken.
		# Just freeing enough space to put our new panel, no need to
		# reduce too much the history panel's size
		# -->
		#screen.addPanel( panelName,localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY_PANE, self.Y_HISTORY_PANE, self.W_HISTORY_PANE, self.H_HISTORY_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(panelName,localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY_PANE, self.Y_HISTORY_PANE + 120, self.W_HISTORY_PANE, self.H_HISTORY_PANE - 120, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		textName = self.top.getNextWidgetName()
		# <!-- custom: move the text line too, to a lower point (Y) so that it
		# fits starting from the new position of the history panel, and correct
		# height of the text line (H) (use a very long text as replacement, for
		# example of rice, to test if text fits well if needed)
		# <!-- custom: also reduce padding to match how it was changed in
		# the other categories -->
		# <!-- custom: i also don't think we need casting (30), so keeping
		# it as the more simple 30
		# after testing (no casting), seems to run fine so leaving as is,
		# not that it was an error i think per say but i don't know, but weird
		# so "fixed" it even though it was not an "error" i think, just
		# redudant maybe.
		# -->
		#screen.addMultilineText( textName, gc.getBonusInfo(self.iBonus).getCivilopedia(), self.X_HISTORY_PANE + 15, self.Y_HISTORY_PANE + 40, self.W_HISTORY_PANE - (30), self.H_HISTORY_PANE - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(textName, gc.getBonusInfo(self.iBonus).getCivilopedia(), self.X_HISTORY_PANE + 7, self.Y_HISTORY_PANE + 10 + 120 + 23, self.W_HISTORY_PANE - 30, self.H_HISTORY_PANE - (15 * 2) - 25 - 120, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

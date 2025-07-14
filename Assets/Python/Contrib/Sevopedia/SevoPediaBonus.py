# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
#
# <!-- custom: refactored similarly than sevopedia unit and sevopedia building, and with the big help of claude ai thanks a lot claude ai anyways etc as well as my prompts or/and adjustments or and not for advciv-sas or based on what i wanted or needed or did or not or and other or and not anyways etc
# new in particular:
# - placeObsoleteWith: tells us/the player watching it anyways when/at which tech is a bonus/ressource (a bonus/ressource anyways etc) is obsoleted, for example in base advciv or/and civ4(?) xml furs are obsoleted at tech_combustion if i am not mistaken anyways etc.
# -->
#

from CvPythonExtensions import *
import CvUtil
# <!-- custom: remove or comment out unused imports -->
#import ScreenInput
#import SevoScreenEnums

from _sevopedia_helpers import check_icon_size_fits_within_icon_frame_size

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaBonus:

	def __init__(self, main):
		self.iBonus = -1
		self.top = main

		# <!-- custom: based on sevopediabuilding's code, see there for details and differences of implementation --> 
		
		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		self.X_BONUS_PANE = self.top.X_PEDIA_PAGE
		self.Y_BONUS_PANE = self.top.Y_PEDIA_PAGE
		self.W_BONUS_PANE = (self.top.R_PEDIA_PAGE - self.X_BONUS_PANE - self.MEDIUM_MARGIN) / 2
		self.H_BONUS_PANE = 250

		# <!-- custom: import iIconFrameSize from sevopediaunit ((base) advciv's code anyways etc) and modified it and its logic for advciv-sas or not or yes or and other things or and not anyways etc -->
		self.ICON_SIZE = 64
		self.ICON_FRAME_SIZE = 164
		check_icon_size_fits_within_icon_frame_size(self.ICON_SIZE, self.ICON_FRAME_SIZE)

		self.W_ICON = self.ICON_SIZE
		self.H_ICON = self.ICON_SIZE
		# <!-- custom: if self.ICON_SIZE is small (e.g. 64), start at the center of self.X_BONUS_PANE, but if self.ICON_SIZE is big (e.g. 164) start at the left most part of self.X_BONUS_PANE ; same reasoning for Y position -->
		self.X_ICON = self.X_BONUS_PANE + (self.ICON_FRAME_SIZE - self.ICON_SIZE) / 2
		self.Y_ICON = self.Y_BONUS_PANE + (self.H_BONUS_PANE - self.H_ICON) / 2

		# <!-- custom: add an extra margin to accomodate the potentially larger self.ICON_SIZE (than for example 64), if diff is 0 this is harmless to keep too so is dynamical code that can handle optionally larger self.ICON_SIZE (vs old self.ICON_SIZE of 64) that you may keep or remove as you prefer anyways etc -->
		self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN = (self.ICON_FRAME_SIZE - self.ICON_SIZE) / 2

		self.STATS_PANE_LEFT_SIDE_MARGIN = 0
		self.STATS_PANE_UPPER_PADDING = 38

		self.X_STATS_PANE = self.X_BONUS_PANE + self.STATS_PANE_LEFT_SIDE_MARGIN + self.W_ICON + (2 * self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN)
		self.Y_STATS_PANE = self.Y_BONUS_PANE + self.STATS_PANE_UPPER_PADDING
		self.W_STATS_PANE = self.W_BONUS_PANE - self.W_ICON - (2 * self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN) - self.STATS_PANE_LEFT_SIDE_MARGIN
		self.H_STATS_PANE = self.H_BONUS_PANE - self.STATS_PANE_UPPER_PADDING

		# <!-- custom: see sevopediaunit's self.W_TOTAL_EFFECTIVE_UNIT_PANE for differences in implementation anyways etc -->
		self.W_TOTAL_EFFECTIVE_BONUS_PANE = self.W_BONUS_PANE

		self.H_WISHED_OR_AND_IMAGINED_IMPROVEMENTS_HEIGHT = 110
		#self.H_EXTRA_ROOM_FOR_IMPROVEMENTS_HORIZONTAL_PANEL_VERTICAL_LABELS = 40
		self.H_EXTRA_ROOM_FOR_IMPROVEMENTS_HORIZONTAL_PANEL_VERTICAL_LABELS = 0

		self.X_IMPROVEMENTS = self.X_BONUS_PANE
		self.Y_IMPROVEMENTS = self.Y_BONUS_PANE + self.H_BONUS_PANE + self.SMALL_MARGIN
		self.W_IMPROVEMENTS = self.W_TOTAL_EFFECTIVE_BONUS_PANE
		self.H_IMPROVEMENTS = self.H_WISHED_OR_AND_IMAGINED_IMPROVEMENTS_HEIGHT + self.H_EXTRA_ROOM_FOR_IMPROVEMENTS_HORIZONTAL_PANEL_VERTICAL_LABELS

		self.X_UNITS = self.X_BONUS_PANE
		self.W_UNITS = self.top.R_PEDIA_PAGE - self.X_UNITS
		self.Y_UNITS = self.Y_IMPROVEMENTS + self.H_IMPROVEMENTS + self.SMALL_MARGIN
		self.H_UNITS = self.H_WISHED_OR_AND_IMAGINED_IMPROVEMENTS_HEIGHT

		# <!-- custom: put the buildings panel under the units panel so easier to refer to it directly, it will also be identical in dimensions (or very close) so we will not need to change much (coordinates or other things) this way -->
		self.X_BUILDINGS_AND_PROJECTS = self.X_BONUS_PANE
		self.Y_BUILDINGS_AND_PROJECTS = self.Y_UNITS + self.H_UNITS + self.SMALL_MARGIN
		self.W_BUILDINGS_AND_PROJECTS = self.W_UNITS
		self.H_BUILDINGS_AND_PROJECTS = self.H_UNITS

		self.X_SPECIAL = self.X_BONUS_PANE
		self.Y_SPECIAL = self.Y_BUILDINGS_AND_PROJECTS + self.H_BUILDINGS_AND_PROJECTS + self.SMALL_MARGIN
		self.W_SPECIAL = self.W_TOTAL_EFFECTIVE_BONUS_PANE
		self.H_SPECIAL = self.top.B_PEDIA_PAGE - self.Y_SPECIAL

		self.H_ADJUST_HEIGHT_ANIMATION_TO_MATCH_ADJACENT_PANE = 7

		self.X_BONUS_ANIMATION = self.X_BONUS_PANE + self.W_TOTAL_EFFECTIVE_BONUS_PANE + self.MEDIUM_MARGIN
		self.Y_BONUS_ANIMATION = self.Y_BONUS_PANE + self.H_ADJUST_HEIGHT_ANIMATION_TO_MATCH_ADJACENT_PANE
		self.W_BONUS_ANIMATION = self.W_TOTAL_EFFECTIVE_BONUS_PANE
		self.H_BONUS_ANIMATION = self.H_BONUS_PANE - self.H_ADJUST_HEIGHT_ANIMATION_TO_MATCH_ADJACENT_PANE
		
		self.X_ROTATION_BONUS_ANIMATION = -20
		self.Z_ROTATION_BONUS_ANIMATION = 30
		self.SCALE_ANIMATION = 0.7

		# <!-- custom: since we split this right side width in 3 panels, (each) and it is separated by 2 self.MEDIUM_MARGINS, substract these before diving (anyways etc), anyways etc -->
		self.X_REVEALED_BY = self.X_BONUS_ANIMATION
		self.Y_REVEALED_BY = self.Y_BONUS_ANIMATION + self.H_BONUS_ANIMATION + self.SMALL_MARGIN
		self.W_REVEALED_BY = (self.W_BONUS_PANE - (2 * self.MEDIUM_MARGIN)) / 3
		self.H_REVEALED_BY = self.H_IMPROVEMENTS

		self.X_TRADEABLE_SINCE = self.X_REVEALED_BY + self.W_REVEALED_BY + self.MEDIUM_MARGIN
		self.Y_TRADEABLE_SINCE = self.Y_REVEALED_BY
		self.W_TRADEABLE_SINCE = self.W_REVEALED_BY
		self.H_TRADEABLE_SINCE = self.H_IMPROVEMENTS

		self.X_OBSOLETE_WITH = self.X_TRADEABLE_SINCE + self.W_TRADEABLE_SINCE + self.MEDIUM_MARGIN
		self.Y_OBSOLETE_WITH = self.Y_REVEALED_BY
		self.W_OBSOLETE_WITH = self.W_REVEALED_BY
		self.H_OBSOLETE_WITH = self.H_IMPROVEMENTS

		self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER = 22

		self.X_HISTORY = self.X_BONUS_ANIMATION
		self.Y_HISTORY = self.Y_BUILDINGS_AND_PROJECTS + self.H_BUILDINGS_AND_PROJECTS + self.SMALL_MARGIN
		self.W_HISTORY = self.W_BONUS_ANIMATION
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY



	def interfaceScreen(self, iBonus):
		self.iBonus = iBonus

		# <!-- custom: Move the panel position, so that it starts from a lower point in the screen.
		# We will use this newly freed place to put the larger Buildings, while we create a RevealedBy panel instead where the Buildings panel was. Hopefully much clearer and more room to fit many buildings this way now, and to separate tech revealed by and tech tradeable since, both currently in the "Requires" panel which is very weird i think, now renamed to "RevealedBy" and "TradeableSince") -->
		self.placeBonusPane()
		self.placeStats()
		self.placeImprovements()
		self.placeUnits()
		self.placeBuildingsAndProjects()
		self.placeSpecial()
		# <!-- custom: split the former/old placeRequires, into 2 functions/methods now instead, placeRevealedBy and placeTradeableSince (which is hopefully more accurate this way too), anyways etc -->
		self.placeRevealedBy()
		self.placeTradeableSince()
		self.placeObsoleteWith()
		self.placeHistory()



	def placeBonusPane(self):
		screen = self.top.getScreen()
		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False, self.X_BONUS_PANE, self.Y_BONUS_PANE, self.W_BONUS_PANE, self.H_BONUS_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getBonusInfo(self.iBonus).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addBonusGraphicGFC(self.top.getNextWidgetName(), self.iBonus, self.X_BONUS_ANIMATION, self.Y_BONUS_ANIMATION, self.W_BONUS_ANIMATION, self.H_BONUS_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_BONUS_ANIMATION, self.Z_ROTATION_BONUS_ANIMATION, self.SCALE_ANIMATION, True)



	def placeStats(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addListBoxGFC(panelName, "", self.X_STATS_PANE, self.Y_STATS_PANE, self.W_STATS_PANE, self.H_STATS_PANE, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panelName, False)
		
		# <!-- custom: handle multiple potential yield changes anyways etc by separating the header from yield stats display anyways etc --> 
		szTextHeader = u"<font=4><b>" + localText.getText("TXT_KEY_PEDIA_SEVOPEDIA_BONUS_NATURAL_TILE_YIELD_CHANGES", ()) + "\n" + u"</b></font>"
		screen.appendListBoxString(panelName, szTextHeader, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		for k in range(YieldTypes.NUM_YIELD_TYPES):
			iYieldChange = gc.getBonusInfo(self.iBonus).getYieldChange(k)
			if iYieldChange != 0:
				if iYieldChange > 0:
					sign = "+"
				else:
					sign = ""
				# <!-- custom: beautify, no need to mention "FOOD: +1", just "+1" is enough especially with the food icon -->
				#szYield = (u"%s: %s%i " % (gc.getYieldInfo(k).getDescription(), sign, iYieldChange))
				szYield = (u"%s%i" % (sign, iYieldChange))
				# <!-- custom: add information about the precise type of yield it is, which can be otherwise very confusing -->
				szText1 = (u"%c  " % gc.getYieldInfo(k).getChar()) + szYield
				szText2 = u"<font=4><b>" + szText1 + "\n" + u"</b></font>"
				screen.appendListBoxString(panelName, szText2, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: switch to an horizontal panel version provided by claude ai at my request it kindly did so for me and as a consequence all who would play this mod advciv-sas i am making or/and others kindly too or not or both or not or and other or and not anyways etc using it too, anyways etc, thanks claude ai and all or not all or yes all or not or other or etc anyways etc anyways etc anyways etc and me too perhaps or not or yes anyways etc anyways etc anyways etc, and then also modified by me or and not for advciv-sas or and not or and other or and not anyways etc anyways etc anyways etc -->
	# <!-- custom: note: this needs to be debugged (simplify code, add left side padding before first button, anyways etc, but hopefully works well enough for now anyways etc -->
	def placeImprovements(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SEVOPEDIA_BONUS_TOTAL_BASE_AND_EXTRA_IMPROVEMENTS_YIELD_CHANGES", ()), "", True, True, self.X_IMPROVEMENTS, self.Y_IMPROVEMENTS, self.W_IMPROVEMENTS, self.H_IMPROVEMENTS, PanelStyles.PANEL_STYLE_BLUE50)

		
		# Create a row container for horizontal layout
		rowPanelName = self.top.getNextWidgetName()
		screen.attachPanel(panelName, rowPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)
		
		# Add vertical spacing at top to help center content
		# We estimate about 40% of panel height as top margin to achieve vertical centering
		# <!-- custom: note: currently vertical button above label doesn't work so code should be cleaned up and solved, but this is good enough so keeping it as is as it working and functional and an improvement over previous vertical scrolling code anyways etc -->
		#verticalSpacerName = self.top.getNextWidgetName()
		#verticalMargin = int(self.H_IMPROVEMENTS * 0.2)  # 20% of panel height as top margin
		#screen.attachLabel(rowPanelName, verticalSpacerName, "\n" * int(verticalMargin/10))
		
		# <!-- custom: hack to add left padding, ideally find how to do it properly while keeping our nice spaced horizontal display -->
		screen.attachLabel(panelName, "", "")

		bAnyFound = False
		xOffset = 0
		buttonSpacing = 20  # Spacing between button columns
		
		for j in range(gc.getNumImprovementInfos()):
			bFirst = True
			szYield = u""
			bEffect = False
			for k in range(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = gc.getImprovementInfo(j).getImprovementBonusYield(self.iBonus, k)
				if iYieldChange != 0:
					bEffect = True
					bAnyFound = True
					iYieldChange += gc.getImprovementInfo(j).getYieldChange(k)
					if bFirst:
						bFirst = False
					else:
						szYield += ", "
					if iYieldChange > 0:
						sign = "+"
					else:
						sign = ""
					szYield += (u"<font=4>%c%s%i</font>" % (gc.getYieldInfo(k).getChar(), sign, iYieldChange))
			
			if bEffect:
				# Add horizontal spacing if not the first button
				if xOffset > 0:
					spacerName = self.top.getNextWidgetName()
					spacerText = " " * buttonSpacing
					screen.attachLabel(rowPanelName, spacerName, spacerText)
				
				# <!-- custom: note: currently vertical button above label doesn't work so code should be cleaned up and solved, but this is good enough so keeping it as is as it working and functional and an improvement over previous vertical scrolling code anyways etc -->
				# Create a column panel for vertical arrangement (button above label)
				colPanelName = self.top.getNextWidgetName()
				screen.attachPanel(rowPanelName, colPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)
				
				# Attach the button to the column
				buttonName = self.top.getNextWidgetName()
				screen.attachImageButton(colPanelName, buttonName, gc.getImprovementInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, j, 1, False)
				
				# Attach the yield label below the button
				yieldLabelName = self.top.getNextWidgetName()
				screen.attachLabel(colPanelName, yieldLabelName, szYield)
				
				# Update horizontal position
				xOffset += 1
		
		if not bAnyFound:
			yPanelCenter = self.Y_IMPROVEMENTS + (self.H_IMPROVEMENTS / 2)
			textName = self.top.getNextWidgetName()
			szText = localText.getText("TXT_KEY_BONUS_GENERIC_NONE", ())
			screen.addMultilineText(textName, szText, self.X_IMPROVEMENTS + 7, yPanelCenter, self.W_IMPROVEMENTS - 14, self.H_IMPROVEMENTS - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeUnits(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# advc.905b: txt key was TXT_KEY_PEDIA_ALLOWS
		screen.addPanel( panelName, localText.getText("TXT_KEY_WB_UNITS", ()), "", False, True, self.X_UNITS, self.Y_UNITS, self.W_UNITS, self.H_UNITS, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		iActivePlayer = gc.getGame().getActivePlayer() # advc.003l
		bAnyFound = False
		for eLoopUnit in range(gc.getNumUnitInfos()):
			bFound = False
			if gc.getUnitInfo(eLoopUnit).getPrereqAndBonus() == self.iBonus:
				bFound = True
				bAnyFound = True
			else:
				j = 0
				while (not bFound and j < gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
					if gc.getUnitInfo(eLoopUnit).getPrereqOrBonuses(j) == self.iBonus:
						bFound = True
						bAnyFound = True
					j += 1
			# <advc.905b>
			if not bFound:
				for j in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
					if gc.getUnitInfo(eLoopUnit).getSpeedBonuses(j) == self.iBonus:
						bFound = True
						bAnyFound = True
						break
			# </advc.905b>
			if bFound:
				szButton = gc.getUnitInfo(eLoopUnit).getButton()
				# <advc.003l>
				if iActivePlayer >= 0:
					szButton = gc.getPlayer(iActivePlayer).getUnitButton(eLoopUnit)
				# </advc.003l>
				screen.attachImageButton( panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, eLoopUnit, 1, False )
		# <!-- custom: placeBuildings is now renamed to placeBuildingsAndProjects -->
		# advc.905b: Allowed buildings moved to placeBuildings

		if not bAnyFound:
			yPanelCenter = self.Y_UNITS + (self.H_UNITS / 2)
			textName = self.top.getNextWidgetName()
			szText = localText.getText("TXT_KEY_BONUS_GENERIC_NONE", ())
			screen.addMultilineText(textName, szText, self.X_UNITS + 7, yPanelCenter, self.W_UNITS - 14, self.H_UNITS - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeBuildingsAndProjects(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# advc.004y: txt key was TXT_KEY_PEDIA_CATEGORY_BUILDING
		# <!-- custom: note: Now the buildings panel is larger as the units panel (is) (anyways etc), useful for ressources like marble that could not fit all -->
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_CATEGORY_BUILDING_PROJECT", ()), "", False, True, self.X_BUILDINGS_AND_PROJECTS, self.Y_BUILDINGS_AND_PROJECTS, self.W_BUILDINGS_AND_PROJECTS, self.H_BUILDINGS_AND_PROJECTS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		# <!-- custom: placeAllows is now renamed to placeUnits -->
		# advc.905b: Moved this loop from placeAllows, which only deals with units now.
		# <!-- custom: i don't know why the bAnyFound approach (i) (but anyways etc) (tried) (anyways etc) in the other methods/functions anyways etc did not work/function for buildings and projects (was displaying "None" text even if we did have buttons anyways etc unlike what we wanted anyways etc anyways etc anyways etc... anyways etc...), so using a bAnyDisplayed slightly different approach than in the other methods/functions anyways etc that use instead bAnyFound, functionnal result is the same anyways etc that now indeed anyways etc we can display "None" if no building is displayed, else display buttons instead and not the "None" text as intended anyways etc anyways etc anyways etc... anyways etc... -->
		bAnyDisplayed = False
		for eLoopBuilding in range(gc.getNumBuildingInfos()):
			bFound = False
			if gc.getBuildingInfo(eLoopBuilding).getPrereqAndBonus() == self.iBonus:
				bFound = True
			else:
				j = 0
				while (not bFound and j < gc.getNUM_BUILDING_PREREQ_OR_BONUSES()):
					if gc.getBuildingInfo(eLoopBuilding).getPrereqOrBonuses(j) == self.iBonus:
						bFound = True
					j += 1
			if bFound:
				bAnyDisplayed = True
				screen.attachImageButton( panelName, "", gc.getBuildingInfo(eLoopBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, eLoopBuilding, 1, False )

		for iBuilding in range(gc.getNumBuildingInfos()):
			info = gc.getBuildingInfo(iBuilding)
			bShow = (info.getFreeBonus() == self.iBonus
					or info.getBonusHealthChanges(self.iBonus) > 0
					or info.getBonusHappinessChanges(self.iBonus) > 0
					or info.getBonusProductionModifier(self.iBonus) > 0)
			if not bShow:
				for eYield in range(YieldTypes.NUM_YIELD_TYPES):
					if info.getBonusYieldModifier(self.iBonus, eYield) > 0:
						bShow = True
						break
			if bShow:
				bAnyDisplayed = True
				screen.attachImageButton( panelName, "", info.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1, False )

		# <advc.004y>
		for iProject in range(gc.getNumProjectInfos()):
			info = gc.getProjectInfo(iProject)
			if info.getBonusProductionModifier(self.iBonus) != 0:
				bAnyDisplayed = True
				screen.attachImageButton(panelName, "", info.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1, False)
		# </advc.004y>

		if not bAnyDisplayed:
			yPanelCenter = self.Y_BUILDINGS_AND_PROJECTS + (self.H_BUILDINGS_AND_PROJECTS / 2)
			textName = self.top.getNextWidgetName()
			szText = localText.getText("TXT_KEY_BONUS_GENERIC_NONE", ())
			screen.addMultilineText(textName, szText, self.X_BUILDINGS_AND_PROJECTS + 7, yPanelCenter, self.W_BUILDINGS_AND_PROJECTS - 14, self.H_BUILDINGS_AND_PROJECTS - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
		screen.attachListBoxGFC( panelName, listName, "", TableStyles.TABLE_STYLE_EMPTY )
		screen.enableSelect(listName, False)
		szSpecialText = CyGameTextMgr().getBonusHelp(self.iBonus, True)
		# <!-- custom: remove string import as advised by chatgpt/becomingthrough after i asked it i mean anyways etc, use native python instead -->
		splitText = szSpecialText.split("\n")
		for special in splitText:
			if len( special ) != 0:
				screen.appendListBoxString( listName, special, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )



	def placeRevealedBy(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: note that TXT_KEY_PEDIA_BONUS_APPEARANCE is "Reveals", using a custom TXT KEY "Revealed By" TXT_KEY_PEDIA_BONUS_APPEARANCE_REVEALED_BY_CUSTOM specifically for the Sevopedia, because now that we formatted it like that, "Revealed By" would fit better than "Reveals". Stil keeping the old entry intact for the Civilopedia
		# note: "Appearance"/"Reveals" is the logic it seems of an appearance but i still find it very confusing, why not use the same name, but as long as it works is maybe fine -->
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_BONUS_APPEARANCE_REVEALED_BY_CUSTOM", ()), "", False, True, self.X_REVEALED_BY, self.Y_REVEALED_BY, self.W_REVEALED_BY, self.H_REVEALED_BY, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")

		iTech = gc.getBonusInfo(self.iBonus).getTechReveal()
		if iTech > -1:
			screen.attachImageButton( panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )
			# <!-- custom: we don't need the extra "(Reveals)" or "(Enables)" texts now that they are both not a "requires" anymore (which i
			# think was very inaccurate, now fixed -->
			#screen.attachLabel(panelName, "", u"(" + localText.getText("TXT_KEY_PEDIA_BONUS_APPEARANCE", ()) + u")")
		else:
			yPanelCenter = self.Y_REVEALED_BY + (self.H_REVEALED_BY / 2)
			textName = self.top.getNextWidgetName()
			szText = localText.getText("TXT_KEY_BONUS_REVEALED_BY_NO_BUTTON_FOUND", ())
			screen.addMultilineText(textName, szText, self.X_REVEALED_BY + 7, yPanelCenter, self.W_REVEALED_BY - 14, self.H_REVEALED_BY - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeTradeableSince(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()

		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_BONUS_TRADE", ()), "", False, True, self.X_TRADEABLE_SINCE, self.Y_TRADEABLE_SINCE, self.W_TRADEABLE_SINCE, self.H_TRADEABLE_SINCE, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")

		iTech = gc.getBonusInfo(self.iBonus).getTechCityTrade()
		if iTech > -1:
			screen.attachImageButton( panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )
			# <!-- custom: same as in placeRevealedBy anyways etc -->
			#screen.attachLabel(panelName, "", u"(" + localText.getText("TXT_KEY_PEDIA_BONUS_TRADE", ()) + u")")
		else:
			yPanelCenter = self.Y_TRADEABLE_SINCE + (self.H_TRADEABLE_SINCE / 2)
			textName = self.top.getNextWidgetName()
			szText = localText.getText("TXT_KEY_BONUS_TRADEABLE_SINCE_NO_BUTTON_FOUND", ())
			screen.addMultilineText(textName, szText, self.X_TRADEABLE_SINCE + 7, yPanelCenter, self.W_TRADEABLE_SINCE - 14, self.H_TRADEABLE_SINCE - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	# Places the tech that obsoletes this bonus resource in the Sevopedia.
	def placeObsoleteWith(self):
		screen = self.top.getScreen()
		
		# Get the current bonus
		bonusInfo = gc.getBonusInfo(self.iBonus)
		# Get the tech that obsoletes this bonus
		iTechObsolete = bonusInfo.getTechObsolete()
		techInfo = gc.getTechInfo(iTechObsolete)
		
		# Set up the panel
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_BONUS_OBSOLETE_WITH", ()), "", False, True, self.X_OBSOLETE_WITH, self.Y_OBSOLETE_WITH, self.W_OBSOLETE_WITH, self.H_OBSOLETE_WITH, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		
		if techInfo > -1:
			# Add the tech button directly to the panel
			szButton = techInfo.getButton()
			screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTechObsolete, 1, False)
		else:
			yPanelCenter = self.Y_OBSOLETE_WITH + (self.H_OBSOLETE_WITH / 2)
			textName = self.top.getNextWidgetName()
			szText = localText.getText("TXT_KEY_BONUS_OBSOLETE_WITH_NO_BUTTON_FOUND", ())
			screen.addMultilineText(textName, szText, self.X_OBSOLETE_WITH + 7, yPanelCenter, self.W_OBSOLETE_WITH - 14, self.H_OBSOLETE_WITH - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		textName = self.top.getNextWidgetName()
		# <!-- custom: reduce padding to match how it was changed in the other categories -->
		# <!-- custom: i also don't think we need casting (30), so keeping it as the more simple 30 after testing (no casting), seems to run fine so leaving as is, not that it was an error i think per say but i don't know, but weird so "fixed" it even though it was not an "error" i think, just redudant maybe. -->
		#screen.addMultilineText( textName, gc.getBonusInfo(self.iBonus).getCivilopedia(), self.X_HISTORY + 15, self.Y_HISTORY + 40, self.W_HISTORY - (30), self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(textName, gc.getBonusInfo(self.iBonus).getCivilopedia(), self.X_HISTORY + 7, self.Y_HISTORY + 10 + self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER, self.W_HISTORY - 30, self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

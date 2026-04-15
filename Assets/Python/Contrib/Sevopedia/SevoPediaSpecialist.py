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
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# <!-- custom: enhanced in AdvCiv-SAS with new Unlocked with and Yields panel based on the Middle-earth mod's Platypedi's specialists page ("C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\Middle-earth\Assets\Python\Screens\PlatyPedia\PlatyPediaSpecialist.py"), with the help of GPT-5.2-Codex thanks a lot! -->
#



from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
import SASTextScale

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



class SevoPediaSpecialist:

	def __init__(self, main):
		self.iSpecialist = -1
		self.top = main

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		self.H_TOP_PANEL = 200
		self.W_ICON_PANEL = 200

		self.X_ICON_PANEL = self.top.X_PEDIA_PAGE
		self.Y_ICON_PANEL = self.top.Y_PEDIA_PAGE

		self.X_LEFT = self.X_ICON_PANEL
		self.W_LEFT = (self.top.R_PEDIA_PAGE - self.X_LEFT - self.MEDIUM_MARGIN) / 2
		self.X_RIGHT = self.X_LEFT + self.W_LEFT + self.MEDIUM_MARGIN
		self.W_RIGHT = self.top.R_PEDIA_PAGE - self.X_RIGHT

		self.X_EFFECTS_PANEL = self.X_ICON_PANEL + self.W_ICON_PANEL + self.MEDIUM_MARGIN
		self.Y_EFFECTS_PANEL = self.Y_ICON_PANEL
		self.W_EFFECTS_PANEL = self.W_LEFT - self.W_ICON_PANEL - self.MEDIUM_MARGIN

		self.W_EXTRA_SLOTS = (self.W_RIGHT - self.SMALL_MARGIN) / 2
		self.W_EXTRA_YIELDS = self.W_EXTRA_SLOTS

		self.X_EXTRA_SLOTS = self.X_RIGHT
		self.Y_EXTRA_SLOTS = self.top.Y_PEDIA_PAGE
		self.H_EXTRA_SLOTS = self.top.B_PEDIA_PAGE - self.Y_EXTRA_SLOTS

		self.X_EXTRA_YIELDS = self.X_EXTRA_SLOTS + self.W_EXTRA_SLOTS + self.SMALL_MARGIN
		self.Y_EXTRA_YIELDS = self.Y_EXTRA_SLOTS
		self.H_EXTRA_YIELDS = self.H_EXTRA_SLOTS

		self.X_HISTORY = self.X_ICON_PANEL
		self.Y_HISTORY = self.Y_ICON_PANEL + self.H_TOP_PANEL + self.SMALL_MARGIN
		self.W_HISTORY = self.W_LEFT
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY

		self.W_ICON = 150
		self.H_ICON = 150
		self.X_ICON = self.X_ICON_PANEL + (self.W_ICON_PANEL - self.W_ICON) / 2
		self.Y_ICON = self.Y_ICON_PANEL + (self.H_TOP_PANEL - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.BUTTON_SIZE = 64



	def interfaceScreen(self, iSpecialist):
		self.iSpecialist = iSpecialist

		self.placeSpecialistPane()
		self.placeEffects()
		self.placeExtraSlots()
		self.placeYields()
		self.placeHistory()





	def placeSpecialistPane(self):
		screen = self.top.getScreen()

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON_PANEL, self.Y_ICON_PANEL, self.W_ICON_PANEL, self.H_TOP_PANEL, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: no need for the blue frame on blue background, use transparent instead -->
		#screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getSpecialistInfo(self.iSpecialist).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)



	def placeEffects(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: no header for more compact and prettier display -->
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS_SPECIALISTS", ()), "", True, False, self.X_EFFECTS_PANEL, self.Y_EFFECTS_PANEL, self.W_EFFECTS_PANEL, self.H_TOP_PANEL, PanelStyles.PANEL_STYLE_BLUE50)
		textName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getSpecialistHelp(self.iSpecialist, True)
		szSpecialText = SASTextScale.normalizeLabelText(szSpecialText)
		# <!-- custom: reduce top padding now that the traits header is removed (GPT-5.2-Codex). Was Y + headerExtraHeight (i.e. + 10) -->
		headerExtraHeight = 10
		screen.addMultilineText(textName, szSpecialText, self.X_EFFECTS_PANEL + 5, self.Y_EFFECTS_PANEL - headerExtraHeight, self.W_EFFECTS_PANEL - 10, self.H_TOP_PANEL - headerExtraHeight, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def _append_change_text(self, szText, iChange, iChar):
		if iChange != 0:
			if szText:
				szText += u", "
			szText += u"%+d%c" % (iChange, iChar)
		return szText



	def _format_slot_label(self, iCount, iFree):
		szText = u""
		if iCount > 0:
			szText = u"+%d" % iCount
		if iFree > 0:
			if szText:
				szText += u", "
			szText += u"+%d Free" % iFree
		return szText



	def placeExtraSlots(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, u"Extra Slots", "", True, True, self.X_EXTRA_SLOTS, self.Y_EXTRA_SLOTS, self.W_EXTRA_SLOTS, self.H_EXTRA_SLOTS, PanelStyles.PANEL_STYLE_BLUE50)
		scrollName = self.top.getNextWidgetName()
		screen.addScrollPanel(scrollName, "", self.X_EXTRA_SLOTS - 2, self.Y_EXTRA_SLOTS + 20, self.W_EXTRA_SLOTS + 4, self.H_EXTRA_SLOTS - 26, PanelStyles.PANEL_STYLE_EMPTY)

		iButtonSize = self.BUTTON_SIZE
		iY = 6

		specialSlots = {}

		# <!-- custom: note: unlike temples, monasteries, and cathedrals, shrines are not a special building, so showing the first entry (as of now Pagan Shrine) only instead for concision since the effect is always the same anyway -->
		for iBuilding in xrange(gc.getNumBuildingInfos()):
			buildingInfo = gc.getBuildingInfo(iBuilding)
			iCount = buildingInfo.getSpecialistCount(self.iSpecialist)
			iFree = buildingInfo.getFreeSpecialistCount(self.iSpecialist)
			if iCount > 0 or iFree > 0:
				szText = self._format_slot_label(iCount, iFree)
				if szText:
					iSpecialBuilding = buildingInfo.getSpecialBuildingType()
					if iSpecialBuilding > -1:
						key = ("special", iSpecialBuilding)
						if key not in specialSlots:
							specialSlots[key] = [0, 0, gc.getSpecialBuildingInfo(iSpecialBuilding).getButton(), WidgetTypes.WIDGET_HELP_SPECIAL_BUILDING, -1, iSpecialBuilding]
						if iCount > specialSlots[key][0]:
							specialSlots[key][0] = iCount
						if iFree > specialSlots[key][1]:
							specialSlots[key][1] = iFree
					elif buildingInfo.getHolyCity() != -1:
						key = ("shrine", -1)
						if key not in specialSlots:
							specialSlots[key] = [0, 0, buildingInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1]
						if iCount > specialSlots[key][0]:
							specialSlots[key][0] = iCount
						if iFree > specialSlots[key][1]:
							specialSlots[key][1] = iFree
					else:
						textName = self.top.getNextWidgetName()
						screen.setImageButtonAt(self.top.getNextWidgetName(), scrollName, buildingInfo.getButton(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1)
						screen.setLabelAt(textName, scrollName, SASTextScale.titleText(szText), CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
						iY += (iButtonSize + 8)

		for key in sorted(specialSlots.keys()):
			szText = self._format_slot_label(specialSlots[key][0], specialSlots[key][1])
			if szText:
				textName = self.top.getNextWidgetName()
				buttonPath = specialSlots[key][2]
				widgetType = specialSlots[key][3]
				widgetID1 = specialSlots[key][4]
				widgetID2 = specialSlots[key][5]
				screen.setImageButtonAt(self.top.getNextWidgetName(), scrollName, buttonPath, 0, iY, iButtonSize, iButtonSize, widgetType, widgetID1, widgetID2)
				screen.setLabelAt(textName, scrollName, SASTextScale.titleText(szText), CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				iY += (iButtonSize + 8)

		for iCivic in xrange(gc.getNumCivicInfos()):
			civicInfo = gc.getCivicInfo(iCivic)
			if civicInfo.isSpecialistValid(self.iSpecialist):
				textName = self.top.getNextWidgetName()
				screen.setImageButtonAt(self.top.getNextWidgetName(), scrollName, civicInfo.getButton(), 0, iY, iButtonSize, iButtonSize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, iCivic, 1)
				screen.setLabelAt(textName, scrollName, SASTextScale.titleText("Unlimited"), CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				iY += (iButtonSize + 8)

		if iY == 6:
			textName = self.top.getNextWidgetName()
			screen.setLabelAt(textName, scrollName, SASTextScale.titleText("No extra slots gained"), CvUtil.FONT_LEFT_JUSTIFY, 0, iY, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)



	def placeYields(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, u"Extra Yields", "", True, True, self.X_EXTRA_YIELDS, self.Y_EXTRA_YIELDS, self.W_EXTRA_YIELDS, self.H_EXTRA_YIELDS, PanelStyles.PANEL_STYLE_BLUE50)
		scrollName = self.top.getNextWidgetName()
		screen.addScrollPanel(scrollName, "", self.X_EXTRA_YIELDS - 2, self.Y_EXTRA_YIELDS + 20, self.W_EXTRA_YIELDS + 4, self.H_EXTRA_YIELDS - 26, PanelStyles.PANEL_STYLE_EMPTY)

		entries = []

		for iCivic in xrange(gc.getNumCivicInfos()):
			civicInfo = gc.getCivicInfo(iCivic)
			szText = u""
			for k in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
				szText = self._append_change_text(szText, civicInfo.getSpecialistExtraCommerce(k), gc.getCommerceInfo(k).getChar())
			if szText:
				entries.append((civicInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, iCivic, szText))

		for iTech in xrange(gc.getNumTechInfos()):
			techInfo = gc.getTechInfo(iTech)
			szText = u""
			for k in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
				szText = self._append_change_text(szText, techInfo.getSpecialistExtraCommerce(k), gc.getCommerceInfo(k).getChar())
			if szText:
				entries.append((techInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, szText))

		for iBuilding in xrange(gc.getNumBuildingInfos()):
			buildingInfo = gc.getBuildingInfo(iBuilding)
			szText = u""
			for k in xrange(YieldTypes.NUM_YIELD_TYPES):
				szText = self._append_change_text(szText, buildingInfo.getSpecialistYieldChange(self.iSpecialist, k), gc.getYieldInfo(k).getChar())
			if szText:
				entries.append((buildingInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, szText))

		iButtonSize = self.BUTTON_SIZE
		iY = 6

		for buttonPath, widgetType, widgetID, szText in entries:
			textName = self.top.getNextWidgetName()
			screen.setImageButtonAt(self.top.getNextWidgetName(), scrollName, buttonPath, 0, iY, iButtonSize, iButtonSize, widgetType, widgetID, 1)
			screen.setLabelAt(textName, scrollName, SASTextScale.titleText(szText), CvUtil.FONT_LEFT_JUSTIFY, iButtonSize + 8, iY + iButtonSize/2 - 8, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			iY += (iButtonSize + 8)

		if iY == 6:
			textName = self.top.getNextWidgetName()
			screen.setLabelAt(textName, scrollName, SASTextScale.titleText("No extra yields gained"), CvUtil.FONT_LEFT_JUSTIFY, 0, iY, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		textName = self.top.getNextWidgetName()
		szText = gc.getSpecialistInfo(self.iSpecialist).getCivilopedia()
		szText = SASTextScale.normalizeLabelText(szText)
		# <!-- custom: also account for scrolling: top text needs to remain visible as an entire line. Note: somehow modifying H weirdly changes the Y optimal scroll point so adjust one at a time maybe. -->
		panelTopPadding = 40
		screen.addMultilineText(textName, szText, self.X_HISTORY + 7, self.Y_HISTORY + panelTopPadding, self.W_HISTORY - 7, self.H_HISTORY - panelTopPadding - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0


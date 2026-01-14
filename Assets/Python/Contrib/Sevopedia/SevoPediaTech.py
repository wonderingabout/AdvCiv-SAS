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
#
# <!-- custom: uses new buildBTradeString function in CvGameTextMgr.cpp to display in placeSpecial the this technology "Cannot be traded" bullet point, see modding ressources readme at /_1_AdvCiv-SAS/Docs/Modding_Ressources/README.md (or whichever path it may be if changed path or modifications i did or may have done additionally or kept as is).
#
# Without the DLL modification, i assume it would still run fine, just you would not have the bullet point at the tech, for example Future tech, that it cannot be traded in placeSpecial, but only the summary at the end of the list of all non tradeable tech that uses the already existing in base advcivgc.getTechInfo(iTech).isTrade(), but which info of (this tech is not tradeable) is in base advciv not displayed in the placeSpecial bullet of the currently selected tech unless you modify DLL as explained before -->



from CvPythonExtensions import *
import CvUtil
import CvPediaScreen
import ScreenInput
import SevoScreenEnums

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

IS_SHOW_NON_TRADEABLE_TECHS_LIST = (gc.getDefineINT("SAS_SEVOPEDIA_TECH_SHOW_NON_TRADEABLE_TECHS_LIST") > 0)
IS_SHOW_OBSOLETES_RED_X = (gc.getDefineINT("SAS_SEVOPEDIA_TECH_SHOW_OBSOLETES_RED_X") > 0)



# <!-- custom: similarly to how cache precomputing is handled in sevopedia leader, prebuild only once as a function at relevant time the list as string of untradeable techs; note also: code provided by deepseek ai thanks to my prompt and that i adjusted or not for advciv-sas to tweak my previous existing code provided by another ai thanks to my prompt too and that i adjusted or not too xd -->
def getPrecomputedUntradeableTechsText():
	untradeableTechs = []

	if IS_SHOW_NON_TRADEABLE_TECHS_LIST:
		for iTech in xrange(gc.getNumTechInfos()):
			if not gc.getTechInfo(iTech).isTrade():
				techDesc = gc.getTechInfo(iTech).getDescription()
				untradeableTechs.append(techDesc)

		untradeableTechs.sort()

		untradeableTechsText = u""

		untradeableTechsText += localText.getText("TXT_KEY_PEDIA_UNTRADEABLE_TECH_REMINDER", ())

		bullet = localText.getText("[ICON_BULLET]", ())
		for tech in untradeableTechs:
			untradeableTechsText += u"\n%s%s" % (bullet, tech)

	return untradeableTechsText



class SevoPediaTech(CvPediaScreen.CvPediaScreen):

	def __init__(self, main):
		self.iTech = -1
		self.top = main

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		# <!-- custom: reorganized layout (Claude code Opus 4.5):
		# Row 1: Tech Pane (left) | Starting Civs (right)
		# Row 2: Requires (left half) | Leads To (right half)
		# Row 3: Obsoletes (full width)
		# Row 4: Enables (full width) - merged units + buildings
		# Row 5: Special (left, W_TECH_PANE width) | History (right, remaining space)
		# -->

		# Standard row height for panels
		self.H_ROW = 110

		# Row 1: Tech Pane and Starting Civs
		self.X_TECH_PANE = self.top.X_PEDIA_PAGE
		self.Y_TECH_PANE = self.top.Y_PEDIA_PAGE
		self.W_TECH_PANE = 340
		self.H_TECH_PANE = 116

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_TECH_PANE + (self.H_TECH_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_TECH_PANE + (self.H_TECH_PANE - self.H_ICON) / 2

		self.ICON_SIZE = 64

		self.X_COST = self.X_TECH_PANE + 110
		self.Y_COST = self.Y_TECH_PANE + 47

		self.X_CIVILIZATIONS_THAT_START_WITH_THIS_TECH = self.X_TECH_PANE + self.W_TECH_PANE + self.MEDIUM_MARGIN
		self.Y_CIVILIZATIONS_THAT_START_WITH_THIS_TECH = self.Y_TECH_PANE
		self.W_CIVILIZATIONS_THAT_START_WITH_THIS_TECH = self.top.R_PEDIA_PAGE - self.X_CIVILIZATIONS_THAT_START_WITH_THIS_TECH
		self.H_CIVILIZATIONS_THAT_START_WITH_THIS_TECH = self.H_ROW

		# Row 2: Requires (left half) | Leads To (right half)
		self.X_REQUIRES = self.X_TECH_PANE
		self.Y_REQUIRES = self.Y_TECH_PANE + self.H_TECH_PANE + self.SMALL_MARGIN
		self.W_REQUIRES = self.top.W_PEDIA_PAGE / 2 - 5
		self.H_REQUIRES = self.H_ROW

		self.X_LEADS_TO = self.X_REQUIRES + self.W_REQUIRES + self.MEDIUM_MARGIN
		self.Y_LEADS_TO = self.Y_REQUIRES
		self.W_LEADS_TO = self.top.R_PEDIA_PAGE - self.X_LEADS_TO
		self.H_LEADS_TO = self.H_ROW

		# Row 3: Obsoletes (full width)
		self.X_OBSOLETES = self.X_TECH_PANE
		self.Y_OBSOLETES = self.Y_REQUIRES + self.H_REQUIRES + self.SMALL_MARGIN
		self.W_OBSOLETES = self.top.R_PEDIA_PAGE - self.X_OBSOLETES
		self.H_OBSOLETES = self.H_ROW

		# <!-- custom: note: Now that we switched to the thinner ChatGPT 5.2 based model, 64 is a bit too small, so extending it to fit buttons -->
		# self.RED_X_BUTTON_SIZE = 64
		self.RED_X_BUTTON_SIZE = 72

		# Row 4: Enables (full width) - merged units + buildings
		self.X_ENABLES = self.X_TECH_PANE
		self.Y_ENABLES = self.Y_OBSOLETES + self.H_OBSOLETES + self.SMALL_MARGIN
		self.W_ENABLES = self.top.R_PEDIA_PAGE - self.X_ENABLES
		self.H_ENABLES = self.H_ROW

		# Row 5: Special (left, W_TECH_PANE width) | History (right, remaining space)
		self.X_SPECIAL = self.X_TECH_PANE
		self.Y_SPECIAL = self.Y_ENABLES + self.H_ENABLES + self.SMALL_MARGIN
		self.W_SPECIAL = self.W_TECH_PANE
		self.H_SPECIAL = self.top.B_PEDIA_PAGE - self.Y_SPECIAL

		self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER = 22

		self.X_HISTORY = self.X_SPECIAL + self.W_SPECIAL + self.MEDIUM_MARGIN
		self.Y_HISTORY = self.Y_SPECIAL
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.X_HISTORY
		self.H_HISTORY = self.H_SPECIAL



	def interfaceScreen(self, iTech):
		self.iTech = iTech

		# Row 1
		self.placeTechPane()
		self.placeCivilizationsThatStartWithThisTech()
		# Row 2
		self.placePrereqs()
		self.placeLeadsTo()
		# Row 3
		self.placeObsoletes()
		# Row 4
		self.placeEnables()
		# Row 5
		self.placeSpecial()
		self.placeHistory()



	# <!-- custom: split this more cleanly as a separate method from interfaceScreen in assessing so if i may say and also as in other parts of our code as well; also Era display code bit/part in this caseimported from rfc doc mod and adjusted or not for advciv-sas-->
	def placeTechPane(self):
		screen = self.top.getScreen()
		techInfo = gc.getTechInfo(self.iTech)

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_TECH_PANE, self.Y_TECH_PANE, self.W_TECH_PANE, self.H_TECH_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: was PanelStyles.PANEL_STYLE_MAIN -->
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), techInfo.getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)

		#screen.setLabel(self.top.getNextWidgetName(), "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, self.X_COST + 25, self.Y_COST, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		listBoxName = self.top.getNextWidgetName()
		szEra = gc.getEraInfo(techInfo.getEra()).getDescription() + " " + localText.getText("TXT_KEY_PEDIA_ERA", ())

		techCost = techInfo.getResearchCost()
		if (self.top.iActivePlayer != -1):
			techCost = gc.getTeam(gc.getGame().getActiveTeam()).getResearchCost(self.iTech)
		szCostText = u"%c %s" % (gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar(), localText.getText("TXT_KEY_PEDIA_COST_CUSTOM", (techCost,)))

		screen.addListBoxGFC(listBoxName, "", self.X_TECH_PANE + 92, self.Y_TECH_PANE + 14, self.W_TECH_PANE, self.H_TECH_PANE, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(listBoxName, False)
		# <!-- custom: extra space (" ") in some of these listboxstringsto better align with the research icon char starting more on the right, depending on where the space is put, the text is so much better left-aligned between rows i think/feel/see or so it seems to me if i mmay say... -->
		screen.appendListBoxString(listBoxName, u" <font=4b>" + techInfo.getDescription() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		screen.appendListBoxString(listBoxName, u"<font=3> " + szEra + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		screen.appendListBoxString(listBoxName, u"<font=4>" + szCostText + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)



	def placeCivilizationsThatStartWithThisTech(self):
		# <advc.004y> Show the box only for starting techs
		civs = []
		for iCiv in range(gc.getNumCivilizationInfos()):
			civ = gc.getCivilizationInfo(iCiv)
			if (civ.isCivilizationFreeTechs(self.iTech) and
					(civ.isPlayable() or civ.isAIPlayable())): # Exclude Minor civ
				civs.append(iCiv)
		if len(civs) <= 0:
			return
		# </advc.004y>
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_CIVILIZATIONS_THAT_START_WITH_THIS_TECH", ()), "", False, True, self.X_CIVILIZATIONS_THAT_START_WITH_THIS_TECH, self.Y_CIVILIZATIONS_THAT_START_WITH_THIS_TECH, self.W_CIVILIZATIONS_THAT_START_WITH_THIS_TECH, self.H_CIVILIZATIONS_THAT_START_WITH_THIS_TECH, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		for iCiv in civs: # advc.004y: Use the list computed above
			civ = gc.getCivilizationInfo(iCiv)
			#if civ.isCivilizationFreeTechs(self.iTech):
			screen.attachImageButton(panelName, "", civ.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCiv, 1, False)



	# <!-- custom: new obsoletes panel showing buildings, bonuses, special buildings, and units obsoleted by this tech with red X overlay (Claude code Sonnet 4.5) -->
	def placeObsoletes(self):
		screen = self.top.getScreen()

		# Collect all obsolete items for this tech
		obsoleteBuildings = []
		obsoleteBonuses = []
		obsoleteSpecialBuildings = []
		obsoleteUnits = []

		# Obsolete Buildings (iterate by building class to get civ-specific buildings)
		for iBuildingClass in range(gc.getNumBuildingClassInfos()):
			iBuilding = gc.getBuildingClassInfo(iBuildingClass).getDefaultBuildingIndex()
			if iBuilding != -1:
				buildingInfo = gc.getBuildingInfo(iBuilding)
				if buildingInfo.getObsoleteTech() == self.iTech:
					obsoleteBuildings.append(iBuilding)

		# Obsolete Bonuses
		for iBonus in range(gc.getNumBonusInfos()):
			bonusInfo = gc.getBonusInfo(iBonus)
			if bonusInfo.getTechObsolete() == self.iTech:
				obsoleteBonuses.append(iBonus)

		# Obsolete Special Buildings
		for iSpecialBuilding in range(gc.getNumSpecialBuildingInfos()):
			specialBuildingInfo = gc.getSpecialBuildingInfo(iSpecialBuilding)
			if specialBuildingInfo.getObsoleteTech() == self.iTech:
				obsoleteSpecialBuildings.append(iSpecialBuilding)

		# Obsolete Units - check that getObsoleteTech is exposed in DLL
		unitInfo = gc.getUnitInfo(0)
		if not hasattr(unitInfo, "getObsoleteTech"):
			raise RuntimeError("[FATAL] Your mod DLL does not expose the required CvUnitInfo Python getter: getObsoleteTech. Please expose it in CyInfoInterface1.cpp and rebuild the DLL.")
		for iUnit in range(gc.getNumUnitInfos()):
			unitInfo = gc.getUnitInfo(iUnit)
			if unitInfo.getObsoleteTech() == self.iTech:
				obsoleteUnits.append(iUnit)

		# Always show panel, display "None" if no obsolete items
		totalObsoleteCount = len(obsoleteBuildings) + len(obsoleteBonuses) + len(obsoleteSpecialBuildings) + len(obsoleteUnits)
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_OBSOLETES", ()), "", False, True, self.X_OBSOLETES, self.Y_OBSOLETES, self.W_OBSOLETES, self.H_OBSOLETES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		if totalObsoleteCount > 0:
			# Get red X overlay path for obsolete indicator
			# <!-- custom: default Civ4 one was too bold at 64 px making it hard to read; replaced with a thinner one imrpessively generated by ChatGPT 5.2 thanks a lot! -->
			# szRedX = ArtFileMgr.getInterfaceArtInfo("INTERFACE_BUTTONS_RED_X").getPath()
			szRedX = "Art/AdvCiv_SAS/Interface/RedX_Thin/chatgpt_5_2_obsolete_x_edge_thin_1204_preview64.dds"

			# Helper to add an obsolete item with red X overlay
			# We use addDDSGFCAt to overlay red X on top of the button
			# Since attachImageButton doesn't support overlays, we use a workaround:
			# attach the button first, then add the overlay separately using screen coordinates

			# For simplicity, we'll use a different approach: create a child panel for each item
			# Actually, the cleanest approach is to use attachImageButton and then manually
			# add the red X overlay at the same position using addDDSGFC

			# Obsolete Buildings
			for iBuilding in obsoleteBuildings:
				buildingInfo = gc.getBuildingInfo(iBuilding)
				screen.attachImageButton(panelName, "", buildingInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1, False)

			# Obsolete Bonuses
			for iBonus in obsoleteBonuses:
				bonusInfo = gc.getBonusInfo(iBonus)
				screen.attachImageButton(panelName, "", bonusInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iBonus, 1, False)

			# Obsolete Special Buildings - show individual buildings that belong to this special building type
			for iSpecialBuilding in obsoleteSpecialBuildings:
				specialBuildingInfo = gc.getSpecialBuildingInfo(iSpecialBuilding)
				# Find all buildings with this special building type and display them
				for iBuilding in range(gc.getNumBuildingInfos()):
					buildingInfo = gc.getBuildingInfo(iBuilding)
					if buildingInfo.getSpecialBuildingType() == iSpecialBuilding:
						screen.attachImageButton(panelName, "", buildingInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1, False)

			# Obsolete Units
			iActivePlayer = gc.getGame().getActivePlayer()
			for iUnit in obsoleteUnits:
				unitInfo = gc.getUnitInfo(iUnit)
				szButton = unitInfo.getButton()
				if iActivePlayer >= 0:
					szButton = gc.getPlayer(iActivePlayer).getUnitButton(iUnit)
				screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)

			# Now add red X overlays on top of all buttons (if enabled via SAS define)
			if IS_SHOW_OBSOLETES_RED_X:
				# Since attachImageButton positions are managed by the panel, we need to use a different approach
				# We'll add the overlays as separate DDS graphics at calculated positions
				# The panel adds a label "  " first, then buttons start after that

				# Calculate total items and add overlays
				# Adjusted values to match actual button positions in the panel
				# Note: actual buttons in panel are 64px (BUTTON_SIZE_CUSTOM), RED_X_BUTTON_SIZE is for the overlay DDS
				# <!-- custom: old values for base INTERFACE_BUTTONS_RED_X (64px, bold):
				#   iOverlaySize = 64
				#   iCurrentX = self.X_OBSOLETES + 10
				#   iOverlayY = self.Y_OBSOLETES + 36
				#   iButtonSpacing = 64 + 4
				# -->
				iButtonSize = 64  # Actual button size in panel (BUTTON_SIZE_CUSTOM)
				iOverlaySize = self.RED_X_BUTTON_SIZE  # Size of the thin red X DDS (128px to fit properly)
				iOverlayOffset = (iButtonSize - iOverlaySize) / 2  # Center overlay on button (will be negative if overlay > button)
				iCurrentX = self.X_OBSOLETES + 10 + iOverlayOffset  # Starting position with centering offset
				iOverlayY = self.Y_OBSOLETES + 36 + iOverlayOffset  # Y position with centering offset
				iButtonSpacing = iButtonSize + 4  # Actual button spacing (64 + 4 = 68)

				# Process buildings
				for iBuilding in obsoleteBuildings:
					szOverlayName = self.top.getNextWidgetName()
					screen.addDDSGFC(szOverlayName, szRedX, iCurrentX, iOverlayY, iOverlaySize, iOverlaySize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1)
					iCurrentX += iButtonSpacing

				# Process bonuses
				for iBonus in obsoleteBonuses:
					szOverlayName = self.top.getNextWidgetName()
					screen.addDDSGFC(szOverlayName, szRedX, iCurrentX, iOverlayY, iOverlaySize, iOverlaySize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iBonus, 1)
					iCurrentX += iButtonSpacing

				# Process special buildings (individual buildings)
				for iSpecialBuilding in obsoleteSpecialBuildings:
					for iBuilding in range(gc.getNumBuildingInfos()):
						buildingInfo = gc.getBuildingInfo(iBuilding)
						if buildingInfo.getSpecialBuildingType() == iSpecialBuilding:
							szOverlayName = self.top.getNextWidgetName()
							screen.addDDSGFC(szOverlayName, szRedX, iCurrentX, iOverlayY, iOverlaySize, iOverlaySize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1)
							iCurrentX += iButtonSpacing

				# Process units
				for iUnit in obsoleteUnits:
					szOverlayName = self.top.getNextWidgetName()
					screen.addDDSGFC(szOverlayName, szRedX, iCurrentX, iOverlayY, iOverlaySize, iOverlaySize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1)
					iCurrentX += iButtonSpacing
		
		else:
			# No obsolete items - display "None" text
			txtKeyNoButtonFound = "TXT_KEY_PEDIA_OBSOLETES_NO_BUTTON_FOUND"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoButtonFound, ())
			yPanelCenter = self.Y_OBSOLETES + (self.H_OBSOLETES / 2)
			screen.addMultilineText(textName, szText, self.X_OBSOLETES + 7, yPanelCenter, self.W_OBSOLETES - 14, self.H_OBSOLETES - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeLeadsTo(self):
		screen = self.top.getScreen()
		szLeadsTo = localText.getText("TXT_KEY_PEDIA_LEADS_TO", ())
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, szLeadsTo, "", False, True, self.X_LEADS_TO, self.Y_LEADS_TO, self.W_LEADS_TO, self.H_LEADS_TO, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		for j in range(gc.getNumTechInfos()):
			for k in range(gc.getNUM_OR_TECH_PREREQS()):
				iPrereq = gc.getTechInfo(j).getPrereqOrTechs(k)
				if (iPrereq == self.iTech):
					screen.attachImageButton(panelName, "", gc.getTechInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_DERIVED_TECH, j, self.iTech, False)
			for k in range(gc.getNUM_AND_TECH_PREREQS()):
				iPrereq = gc.getTechInfo(j).getPrereqAndTechs(k)
				if (iPrereq == self.iTech):
					screen.attachImageButton(panelName, "", gc.getTechInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_DERIVED_TECH, j, self.iTech, False)



	def placePrereqs(self):
		screen = self.top.getScreen()
		szRequires = localText.getText("TXT_KEY_PEDIA_REQUIRES", ())
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, szRequires, "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		bFirst = True
		for j in range(gc.getNUM_AND_TECH_PREREQS()):
			eTech = gc.getTechInfo(self.iTech).getPrereqAndTechs(j)
			if (eTech > -1):
				if (not bFirst):
					screen.attachLabel(panelName, "", localText.getText("TXT_KEY_AND", ()))
				else:
					bFirst = False
				screen.attachImageButton(panelName, "", gc.getTechInfo(eTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_REQUIRED_TECH, eTech, j, False)
		nOrTechs = 0
		for j in range(gc.getNUM_OR_TECH_PREREQS()):
			if (gc.getTechInfo(self.iTech).getPrereqOrTechs(j) > -1):
				nOrTechs += 1
		szLeftDelimeter = ""
		szRightDelimeter = ""
		if (not bFirst):
			if (nOrTechs > 1):
				szLeftDelimeter = localText.getText("TXT_KEY_AND", ()) + "("
				szRightDelimeter = ") "
			elif (nOrTechs > 0):
				szLeftDelimeter = localText.getText("TXT_KEY_AND", ())
			else:
				return
		if len(szLeftDelimeter) > 0:
			screen.attachLabel(panelName, "", szLeftDelimeter)
		bFirst = True
		for j in range(gc.getNUM_OR_TECH_PREREQS()):
			eTech = gc.getTechInfo(self.iTech).getPrereqOrTechs(j)
			if (eTech > -1):
				if (not bFirst):
					screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
				else:
					bFirst = False
				screen.attachImageButton(panelName, "", gc.getTechInfo(eTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_REQUIRED_TECH, eTech, j, False)
		if len(szRightDelimeter) > 0:
			screen.attachLabel(panelName, "", szRightDelimeter)



	# <!-- custom: merged placeUnits and placeBuildings into single placeEnables (Claude code Opus 4.5) -->
	def placeEnables(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_ENABLES", ()), "", False, True, self.X_ENABLES, self.Y_ENABLES, self.W_ENABLES, self.H_ENABLES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		iActivePlayer = gc.getGame().getActivePlayer()

		# Units enabled
		for eLoopUnit in range(gc.getNumUnitInfos()):
			if eLoopUnit != -1:
				if isTechRequiredForUnit(self.iTech, eLoopUnit):
					szButton = gc.getUnitInfo(eLoopUnit).getButton()
					if iActivePlayer >= 0:
						szButton = gc.getPlayer(iActivePlayer).getUnitButton(eLoopUnit)
					screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, eLoopUnit, 1, False)

		# Buildings enabled
		for eLoopBuilding in range(gc.getNumBuildingInfos()):
			if eLoopBuilding != -1:
				if isTechRequiredForBuilding(self.iTech, eLoopBuilding):
					screen.attachImageButton(panelName, "", gc.getBuildingInfo(eLoopBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, eLoopBuilding, 1, False)

		# Projects enabled
		for eLoopProject in range(gc.getNumProjectInfos()):
			if isTechRequiredForProject(self.iTech, eLoopProject):
				screen.attachImageButton(panelName, "", gc.getProjectInfo(eLoopProject).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, eLoopProject, 1, False)



	# <!-- custom: add non-tradeable (<bTrade>) tech list at the end of placeSpecial, addition with the help of chatgpt thanks. -->
	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()

		szSpecialText = CyGameTextMgr().getTechHelp(self.iTech, True, False, False, False, -1)[1:]

		if IS_SHOW_NON_TRADEABLE_TECHS_LIST:
			# <!-- custom: add the list as string of all untradeable techs if this tech is untradeable; see also sevopedia main precomputing / cache building for untradeable techs text for details -->
			if (not gc.getTechInfo(self.iTech).isTrade()):
				if szSpecialText.strip():
					szSpecialText += u"\n\n"
				szSpecialText += UNTRADEABLE_TECHS_TEXT

		# <!-- custom: seems to overfill a bit actually quite a bit xd after rechecking, reduce height, was self.H_SPECIAL-10 -->
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL + 5, self.Y_SPECIAL + 30, self.W_SPECIAL - 35, self.H_SPECIAL - 35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		szText = u""
		# <!-- custom: same reasoning as for TXT_KEY_CIVILOPEDIA_STRATEGY in SevoPediaBuilding.py (refer to this file for details), removing (hiding) the entry entirely from the sevopedia. -->
		szText += gc.getTechInfo(self.iTech).getQuote()
		szText += u"\n\n" + gc.getTechInfo(self.iTech).getCivilopedia()
		szQuoteTextWidget = self.top.getNextWidgetName()
		# <!-- custom: i prefer the fancier design, find it way more beautiful too, restoring it; as for padding adjust/modify it a bit too, was self.X_HISTORY + 9, self.Y_HISTORY + 12, also we removed _HISTORY to simplify and standardize code and display and as we don't need nor want the extra height in this case -->
		#screen.attachMultilineText(panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(szQuoteTextWidget, szText, self.X_HISTORY + 7, self.Y_HISTORY + 10 + self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER, self.W_HISTORY - 30, self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

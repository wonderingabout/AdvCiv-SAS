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

from _sevopedia_helpers import *

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

		# <!-- custom: reorganized layout (Claude Code Sonnet 4.5):
		# Row 1: Tech Pane (left, wider) | Music (84px) | Starting Civs (right, remaining)
		# Row 2: Requires (full width to Music end)
		# Row 3: First to Discover (left, 84px) | Leads To (right, remaining to Music end)
		# Row 4: Obsoletes (full width)
		# Row 5: Enables (full width) - merged units + buildings
		# Row 6: Special (left, W_TECH_PANE width) | History (right, remaining space)
		# -->

		# Standard row height for panels
		self.H_ROW = 110

		# Row 1: Tech Pane (increased by 150px), Music panel, and Starting Civs
		self.X_TECH_PANE = self.top.X_PEDIA_PAGE
		self.Y_TECH_PANE = self.top.Y_PEDIA_PAGE
		self.W_TECH_PANE = 490  # Increased from 340 to 490 (+150px)
		self.H_TECH_PANE = 116

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_TECH_PANE + (self.H_TECH_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_TECH_PANE + (self.H_TECH_PANE - self.H_ICON) / 2

		self.ICON_SIZE = 64

		self.X_COST = self.X_TECH_PANE + 110
		self.Y_COST = self.Y_TECH_PANE + 47

		# Music panel (84px, right of Tech Pane)
		self.W_MUSIC = 84
		self.X_MUSIC = self.X_TECH_PANE + self.W_TECH_PANE + self.MEDIUM_MARGIN
		self.Y_MUSIC = self.Y_TECH_PANE
		self.H_MUSIC = self.H_TECH_PANE

		# Starting Civs (right of Music panel)
		self.X_CIVILIZATIONS_THAT_START_WITH_THIS_TECH = self.X_MUSIC + self.W_MUSIC + self.MEDIUM_MARGIN
		self.Y_CIVILIZATIONS_THAT_START_WITH_THIS_TECH = self.Y_TECH_PANE
		self.W_CIVILIZATIONS_THAT_START_WITH_THIS_TECH = self.top.R_PEDIA_PAGE - self.X_CIVILIZATIONS_THAT_START_WITH_THIS_TECH
		self.H_CIVILIZATIONS_THAT_START_WITH_THIS_TECH = self.H_ROW

		# Row 2: Requires (full width to Music panel end)
		self.X_REQUIRES = self.X_TECH_PANE
		self.Y_REQUIRES = self.Y_TECH_PANE + self.H_TECH_PANE + self.SMALL_MARGIN
		# Width should align to end X position of Music panel
		self.W_REQUIRES = (self.X_MUSIC + self.W_MUSIC) - self.X_REQUIRES
		self.H_REQUIRES = self.H_ROW

		# Row 3: First to Discover (left, 84px) | Leads To (right, remaining to Music end)
		# <!-- custom: First to Discover panel for religions, corporations, great people, free techs - positioned left of Leads To (Claude Code Sonnet 4.5) -->
		self.W_FIRST_TO_DISCOVER = 84  # Same width as SevoPediaBuilding's obsolete panel - enough for one button
		self.X_FIRST_TO_DISCOVER = self.X_TECH_PANE
		self.Y_FIRST_TO_DISCOVER = self.Y_REQUIRES + self.H_REQUIRES + self.SMALL_MARGIN
		self.H_FIRST_TO_DISCOVER = self.H_ROW

		self.X_LEADS_TO = self.X_FIRST_TO_DISCOVER + self.W_FIRST_TO_DISCOVER + self.MEDIUM_MARGIN
		self.Y_LEADS_TO = self.Y_FIRST_TO_DISCOVER
		# Leads To width extends to Music panel end
		self.W_LEADS_TO = (self.X_MUSIC + self.W_MUSIC) - self.X_LEADS_TO
		self.H_LEADS_TO = self.H_ROW

		# Row 4: Obsoletes (full width)
		self.X_OBSOLETES = self.X_TECH_PANE
		self.Y_OBSOLETES = self.Y_LEADS_TO + self.H_LEADS_TO + self.SMALL_MARGIN
		self.W_OBSOLETES = self.top.R_PEDIA_PAGE - self.X_OBSOLETES
		self.H_OBSOLETES = self.H_ROW

		# <!-- custom: note: Now that we switched to the thinner ChatGPT 5.2 based model, 64 is a bit too small, so extending it to fit buttons -->
		# self.RED_X_BUTTON_SIZE = 64
		self.RED_X_BUTTON_SIZE = 72

		# Row 5: Enables (full width) - merged units + buildings
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

		# Row 1: Tech Pane, Music, Starting Civs
		self.placeTechPane()
		self.placeMusic()
		self.placeCivilizationsThatStartWithThisTech()
		# Row 2: Requires
		self.placePrereqs()
		# Row 3: First to Discover, Leads To
		self.placeFirstToDiscover()
		self.placeLeadsTo()
		# Row 4: Obsoletes
		self.placeObsoletes()
		# Row 5: Enables
		self.placeEnables()
		# Row 6: Special, History
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



	def placeMusic(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SAS_MUSIC_PANEL", ()), "", False, True, self.X_MUSIC, self.Y_MUSIC, self.W_MUSIC, self.H_MUSIC, PanelStyles.PANEL_STYLE_BLUE50)

		# <!-- custom: use attachLabel for padding similar to other 84px panels -->
		screen.attachLabel(panelName, "", "  ")

		# <!-- custom: Music system uses packed keys (unlike Movies which use separate type+id). (Claude Code Sonnet 4.5) -->
		iMusicType = self.top.SAS_PEDIA_MUSIC_TYPE_TECH
		iPackedMusic = self.top.SAS_packMusicKey(iMusicType, self.iTech)

		if self.top.pediaMusic.hasMusic(iPackedMusic):
			# <!-- custom: setImageButtonAt requires str() wrapper (not unicode) for button path - discovered via debugging C++ signature mismatch error. (Claude Code Sonnet 4.5) -->
			buttonPathTxtKey = "TXT_KEY_IMAGE_AS_BUTTON_PLAY_BUTTON_BUTTON_PATH"
			buttonPath = str(localText.getText(buttonPathTxtKey, ()))

			buttonSize = 64
			# <!-- custom: setImageButtonAt positions relative to panel content area (below header).
			# X: Standard centering works correctly.
			# Y: Must be set to 10 (not calculated from panelHeaderHeight) - empirically determined positioning fix. (Claude Code Sonnet 4.5) -->
			buttonX = (self.W_MUSIC - buttonSize) / 2
			buttonY = 10
			screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, buttonPath, buttonX, buttonY, buttonSize, buttonSize, WidgetTypes.WIDGET_PYTHON, self.top.SAS_PEDIA_PYTHON_MUSIC_ENTRY, iPackedMusic)
		else:
			txtKeyNoButtonFound = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoButtonFound, ())
			yPanelCenter = self.Y_MUSIC + (self.H_MUSIC / 2)
			screen.addMultilineText(textName, szText, self.X_MUSIC + 7, yPanelCenter, self.W_MUSIC - 14, self.H_MUSIC - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



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



	# <!-- custom: First to Discover panel showing religions, corporations, great people, and free techs that can be gained by being first to discover this tech (Claude code Opus 4.5 + GPT-5.2-Codex) -->
	def placeFirstToDiscover(self):
		screen = self.top.getScreen()
		techInfo = gc.getTechInfo(self.iTech)
		iActivePlayer = gc.getGame().getActivePlayer()

		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_FIRST_TO_DISCOVER", ()), "", False, True, self.X_FIRST_TO_DISCOVER, self.Y_FIRST_TO_DISCOVER, self.W_FIRST_TO_DISCOVER, self.H_FIRST_TO_DISCOVER, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		bButtonFound = False

		# Religions founded by first discoverer
		for iReligion in range(gc.getNumReligionInfos()):
			religionInfo = gc.getReligionInfo(iReligion)
			if religionInfo.getTechPrereq() == self.iTech:
				screen.attachImageButton(panelName, "", religionInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iReligion, 1, False)
				bButtonFound = True

		# Free unit (great person) for first discoverer
		iFirstFreeUnitClass = techInfo.getFirstFreeUnitClass()
		if iFirstFreeUnitClass != -1:
			# Get civ-specific unit if active player exists
			if iActivePlayer >= 0:
				iUnit = gc.getCivilizationInfo(gc.getGame().getActiveCivilizationType()).getCivilizationUnits(iFirstFreeUnitClass)
			else:
				iUnit = gc.getUnitClassInfo(iFirstFreeUnitClass).getDefaultUnitIndex()
			if iUnit != -1:
				unitInfo = gc.getUnitInfo(iUnit)
				szButton = unitInfo.getButton()
				if iActivePlayer >= 0:
					szButton = gc.getPlayer(iActivePlayer).getUnitButton(iUnit)
				screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, 1, False)
				bButtonFound = True

		# Free tech for first discoverer
		if techInfo.getFirstFreeTechs() > 0:
			szButton = ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_FREETECH").getPath()
			# <!-- custom: similarly, as of now upscale the smaller button to 46 px not more -->
			screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_FREE_TECH, self.iTech, -1, False)
			bButtonFound = True

		if not bButtonFound:
			# No first-to-discover effects - display "None" text
			txtKeyNone = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNone, ())
			yPanelCenter = self.Y_FIRST_TO_DISCOVER + (self.H_FIRST_TO_DISCOVER / 2)
			screen.addMultilineText(textName, szText, self.X_FIRST_TO_DISCOVER + 7, yPanelCenter, self.W_FIRST_TO_DISCOVER - 14, self.H_FIRST_TO_DISCOVER - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



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
			# <!-- custom: use iData2=-1 instead of 1 to fix left-click not working (same pattern as SevoPediaBuilding's obsolete tech) -->
			for iBuilding in obsoleteBuildings:
				buildingInfo = gc.getBuildingInfo(iBuilding)
				screen.attachImageButton(panelName, "", buildingInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, -1, False)

			# Obsolete Bonuses
			for iBonus in obsoleteBonuses:
				bonusInfo = gc.getBonusInfo(iBonus)
				screen.attachImageButton(panelName, "", bonusInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iBonus, -1, False)

			# Obsolete Special Buildings - show individual buildings that belong to this special building type
			for iSpecialBuilding in obsoleteSpecialBuildings:
				specialBuildingInfo = gc.getSpecialBuildingInfo(iSpecialBuilding)
				# Find all buildings with this special building type and display them
				for iBuilding in range(gc.getNumBuildingInfos()):
					buildingInfo = gc.getBuildingInfo(iBuilding)
					if buildingInfo.getSpecialBuildingType() == iSpecialBuilding:
						screen.attachImageButton(panelName, "", buildingInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, -1, False)

			# Obsolete Units
			iActivePlayer = gc.getGame().getActivePlayer()
			for iUnit in obsoleteUnits:
				unitInfo = gc.getUnitInfo(iUnit)
				szButton = unitInfo.getButton()
				if iActivePlayer >= 0:
					szButton = gc.getPlayer(iActivePlayer).getUnitButton(iUnit)
				screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, -1, False)

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
				# <!-- custom: for some reason after switching from addDDSGFC to addDDSGFCAt to fix linking issues clicking (right click works but left click doesn't which is not consistent with how other panel's clicking works (either left only or both), the RedX has shifted vertically a bit, so we need to reduce the original + 36 added to iOverlayY -->
				iOverlayY = self.Y_OBSOLETES + 8 + iOverlayOffset  # Y position with centering offset
				iButtonSpacing = iButtonSize + 4  # Actual button spacing (64 + 4 = 68)

				# Process buildings
				for iBuilding in obsoleteBuildings:
					szOverlayName = self.top.getNextWidgetName()
					screen.addDDSGFCAt(szOverlayName, panelName, szRedX, iCurrentX - self.X_OBSOLETES, iOverlayY - self.Y_OBSOLETES, iOverlaySize, iOverlaySize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, -1, False)
					# <!-- custom: overlay should not intercept clicks; disable hit testing so underlying obsolete button handles left/right click (GPT-5.2-Codex) -->
					screen.setHitTest(szOverlayName, HitTestTypes.HITTEST_NOHIT)
					iCurrentX += iButtonSpacing

				# Process bonuses
				for iBonus in obsoleteBonuses:
					szOverlayName = self.top.getNextWidgetName()
					screen.addDDSGFCAt(szOverlayName, panelName, szRedX, iCurrentX - self.X_OBSOLETES, iOverlayY - self.Y_OBSOLETES, iOverlaySize, iOverlaySize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iBonus, -1, False)
					screen.setHitTest(szOverlayName, HitTestTypes.HITTEST_NOHIT)
					iCurrentX += iButtonSpacing

				# Process special buildings (individual buildings)
				for iSpecialBuilding in obsoleteSpecialBuildings:
					for iBuilding in range(gc.getNumBuildingInfos()):
						buildingInfo = gc.getBuildingInfo(iBuilding)
						if buildingInfo.getSpecialBuildingType() == iSpecialBuilding:
							szOverlayName = self.top.getNextWidgetName()
							screen.addDDSGFCAt(szOverlayName, panelName, szRedX, iCurrentX - self.X_OBSOLETES, iOverlayY - self.Y_OBSOLETES, iOverlaySize, iOverlaySize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, -1, False)
							screen.setHitTest(szOverlayName, HitTestTypes.HITTEST_NOHIT)
							iCurrentX += iButtonSpacing

				# Process units
				for iUnit in obsoleteUnits:
					szOverlayName = self.top.getNextWidgetName()
					screen.addDDSGFCAt(szOverlayName, panelName, szRedX, iCurrentX - self.X_OBSOLETES, iOverlayY - self.Y_OBSOLETES, iOverlaySize, iOverlaySize, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUnit, -1, False)
					screen.setHitTest(szOverlayName, HitTestTypes.HITTEST_NOHIT)
					iCurrentX += iButtonSpacing
		
		else:
			# No obsolete items - display "None" text
			txtKeyNoButtonFound = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
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
		bButtonFound = False

		for j in range(gc.getNumTechInfos()):
			for k in range(gc.getNUM_OR_TECH_PREREQS()):
				iPrereq = gc.getTechInfo(j).getPrereqOrTechs(k)
				if (iPrereq == self.iTech):
					screen.attachImageButton(panelName, "", gc.getTechInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_DERIVED_TECH, j, self.iTech, False)
					bButtonFound = True
			for k in range(gc.getNUM_AND_TECH_PREREQS()):
				iPrereq = gc.getTechInfo(j).getPrereqAndTechs(k)
				if (iPrereq == self.iTech):
					screen.attachImageButton(panelName, "", gc.getTechInfo(j).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_DERIVED_TECH, j, self.iTech, False)
					bButtonFound = True

		if not bButtonFound:
			txtKeyNoButtonFound = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoButtonFound, ())
			yPanelCenter = self.Y_LEADS_TO + (self.H_LEADS_TO / 2)
			screen.addMultilineText(textName, szText, self.X_LEADS_TO + 7, yPanelCenter, self.W_LEADS_TO - 14, self.H_LEADS_TO - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placePrereqs(self):
		screen = self.top.getScreen()
		szRequires = localText.getText("TXT_KEY_PEDIA_REQUIRES", ())
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, szRequires, "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		bButtonFound = False
		bHasAnd = False
		for j in range(gc.getNUM_AND_TECH_PREREQS()):
			eTech = gc.getTechInfo(self.iTech).getPrereqAndTechs(j)
			if (eTech > -1):
				if bHasAnd:
					screen.attachLabel(panelName, "", localText.getText("TXT_KEY_AND", ()))
				else:
					bHasAnd = True
				screen.attachImageButton(panelName, "", gc.getTechInfo(eTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_REQUIRED_TECH, eTech, j, False)
				bButtonFound = True
		nOrTechs = 0
		for j in range(gc.getNUM_OR_TECH_PREREQS()):
			if (gc.getTechInfo(self.iTech).getPrereqOrTechs(j) > -1):
				nOrTechs += 1
		szLeftDelimeter = ""
		szRightDelimeter = ""
		if bHasAnd:
			if (nOrTechs > 1):
				szLeftDelimeter = localText.getText("TXT_KEY_AND", ()) + "("
				szRightDelimeter = ") "
			elif (nOrTechs > 0):
				szLeftDelimeter = localText.getText("TXT_KEY_AND", ())
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
				bButtonFound = True
		if len(szRightDelimeter) > 0:
			screen.attachLabel(panelName, "", szRightDelimeter)

		if not bButtonFound:
			txtKeyNoButtonFound = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoButtonFound, ())
			yPanelCenter = self.Y_REQUIRES + (self.H_REQUIRES / 2)
			screen.addMultilineText(textName, szText, self.X_REQUIRES + 7, yPanelCenter, self.W_REQUIRES - 14, self.H_REQUIRES - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: merged placeUnits and placeBuildings into single placeEnables, expanded to include all tech advisor items (Claude code Opus 4.5 + GPT-5.2-Codex) -->
	def placeEnables(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_ENABLES", ()), "", False, True, self.X_ENABLES, self.Y_ENABLES, self.W_ENABLES, self.H_ENABLES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		iActivePlayer = gc.getGame().getActivePlayer()
		techInfo = gc.getTechInfo(self.iTech)
		bButtonFound = False

		# Units enabled
		for eLoopUnit in range(gc.getNumUnitInfos()):
			if eLoopUnit != -1:
				if isTechRequiredForUnit(self.iTech, eLoopUnit):
					szButton = gc.getUnitInfo(eLoopUnit).getButton()
					if iActivePlayer >= 0:
						szButton = gc.getPlayer(iActivePlayer).getUnitButton(eLoopUnit)
					screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, eLoopUnit, 1, False)
					bButtonFound = True

		# Buildings enabled
		for eLoopBuilding in range(gc.getNumBuildingInfos()):
			if eLoopBuilding != -1:
				if isTechRequiredForBuilding(self.iTech, eLoopBuilding):
					screen.attachImageButton(panelName, "", gc.getBuildingInfo(eLoopBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, eLoopBuilding, 1, False)
					bButtonFound = True

		# Projects enabled
		for eLoopProject in range(gc.getNumProjectInfos()):
			if isTechRequiredForProject(self.iTech, eLoopProject):
				screen.attachImageButton(panelName, "", gc.getProjectInfo(eLoopProject).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, eLoopProject, 1, False)
				bButtonFound = True

		# Promotions enabled
		for iPromotion in range(gc.getNumPromotionInfos()):
			if gc.getPromotionInfo(iPromotion).getTechPrereq() == self.iTech:
				screen.attachImageButton(panelName, "", gc.getPromotionInfo(iPromotion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iPromotion, 1, False)
				bButtonFound = True

		# Civics enabled
		for iCivic in range(gc.getNumCivicInfos()):
			if gc.getCivicInfo(iCivic).getTechPrereq() == self.iTech:
				screen.attachImageButton(panelName, "", gc.getCivicInfo(iCivic).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, iCivic, 1, False)
				bButtonFound = True

		# Bonuses revealed
		for iBonus in range(gc.getNumBonusInfos()):
			if gc.getBonusInfo(iBonus).getTechReveal() == self.iTech:
				screen.attachImageButton(panelName, "", gc.getBonusInfo(iBonus).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iBonus, 1, False)
				bButtonFound = True

		# Builds/Improvements enabled (includes feature-removal builds like Chop Forest, roads, etc.)
		for iBuild in range(gc.getNumBuildInfos()):
			buildInfo = gc.getBuildInfo(iBuild)
			bTechFound = False
			# Check if this build's tech prereq matches
			if buildInfo.getTechPrereq() == -1:
				# No direct tech prereq - check feature-specific techs (e.g. Chop Jungle needs specific tech)
				for iFeature in range(gc.getNumFeatureInfos()):
					if buildInfo.getFeatureTech(iFeature) == self.iTech:
						bTechFound = True
						break
			else:
				if buildInfo.getTechPrereq() == self.iTech:
					bTechFound = True

			if bTechFound:
				iImprovement = buildInfo.getImprovement()
				if iImprovement != -1:
					screen.attachImageButton(panelName, "", buildInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, iImprovement, 1, False)
				else:
					# Use WIDGET_HELP_IMPROVEMENT to keep the feature-removal tooltip/redirect behavior (DLL change).
					screen.attachImageButton(panelName, "", buildInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_HELP_IMPROVEMENT, self.iTech, iBuild, False)
				bButtonFound = True

		# Special buildings like monasteries
		for iSpecialBuilding in range(gc.getNumSpecialBuildingInfos()):
			if gc.getSpecialBuildingInfo(iSpecialBuilding).getTechPrereq() == self.iTech:
				screen.attachImageButton(panelName, "", gc.getSpecialBuildingInfo(iSpecialBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_HELP_SPECIAL_BUILDING, self.iTech, iSpecialBuilding, False)
				bButtonFound = True

		# Route movement change (faster roads)
		# <!-- custom: use BUTTON_SIZE_46 for interface art buttons - this is the largest size the engine supports for attachImageButton;
		# unintended but beneficial side effect: the smaller size helps visually distinguish these "ability" icons from the 64px game object buttons above (Claude Code Opus 4.5) -->
		for iRoute in range(gc.getNumRouteInfos()):
			if gc.getRouteInfo(iRoute).getTechMovementChange(self.iTech) != 0:
				screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_MOVE_BONUS").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_MOVE_BONUS, self.iTech, -1, False)
				bButtonFound = True
				break  # Only show once even if multiple routes affected

		# Bridge Building
		if techInfo.isBridgeBuilding():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_BRIDGEBUILDING").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_BUILD_BRIDGE, self.iTech, -1, False)
			bButtonFound = True

		# Irrigation
		if techInfo.isIrrigation():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_IRRIGATION").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_IRRIGATION, self.iTech, -1, False)
			bButtonFound = True

		# Ignore Irrigation (farms spread without fresh water)
		if techInfo.isIgnoreIrrigation():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_NOIRRIGATION").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_IGNORE_IRRIGATION, self.iTech, -1, False)
			bButtonFound = True

		# Water Work (coastal work)
		if techInfo.isWaterWork():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_WATERWORK").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_WATER_WORK, self.iTech, -1, False)
			bButtonFound = True

		# Domain Extra Moves (e.g. extra naval movement)
		for iDomain in range(DomainTypes.NUM_DOMAIN_TYPES):
			if techInfo.getDomainExtraMoves(iDomain) != 0:
				screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_WATERMOVES").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_DOMAIN_EXTRA_MOVES, self.iTech, iDomain, False)
				bButtonFound = True

		# Terrain trade routes (coastal/ocean trade)
		for iTerrain in range(gc.getNumTerrainInfos()):
			if techInfo.isTerrainTrade(iTerrain):
				szArtInfoType = "INTERFACE_TECH_WATERTRADE"
				if iTerrain == gc.getDefineINT("DEEP_WATER_TERRAIN"):
					szArtInfoType = "INTERFACE_TECH_DEEPWATERTRADE"
				screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo(szArtInfoType).getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_TERRAIN_TRADE, self.iTech, iTerrain, False)
				bButtonFound = True

		# River trade
		if techInfo.isRiverTrade():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_RIVERTRADE").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_TERRAIN_TRADE, self.iTech, gc.getNumTerrainInfos(), False)
			bButtonFound = True

		# Commerce slider adjustments (culture, espionage sliders)
		for iCommerce in range(CommerceTypes.NUM_COMMERCE_TYPES):
			if techInfo.isCommerceFlexible(iCommerce):
				if iCommerce == CommerceTypes.COMMERCE_CULTURE:
					szFileName = ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_CULTURE").getPath()
				elif iCommerce == CommerceTypes.COMMERCE_ESPIONAGE:
					szFileName = ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_ESPIONAGE").getPath()
				else:
					szFileName = ArtFileMgr.getInterfaceArtInfo("INTERFACE_GENERAL_QUESTIONMARK").getPath()
				screen.attachImageButton(panelName, "", szFileName, GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_ADJUST, self.iTech, iCommerce, False)
				bButtonFound = True

		# Map Trading
		if techInfo.isMapTrading():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_MAPTRADING").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_MAP_TRADE, self.iTech, -1, False)
			bButtonFound = True

		# Tech Trading
		if techInfo.isTechTrading():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_TECHTRADING").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_TECH_TRADE, self.iTech, -1, False)
			bButtonFound = True

		# Gold Trading
		if techInfo.isGoldTrading():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_GOLDTRADING").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_GOLD_TRADE, self.iTech, -1, False)
			bButtonFound = True

		# Open Borders
		if techInfo.isOpenBordersTrading():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_OPENBORDERS").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_OPEN_BORDERS, self.iTech, -1, False)
			bButtonFound = True

		# Defensive Pact
		if techInfo.isDefensivePactTrading():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_DEFENSIVEPACT").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_DEFENSIVE_PACT, self.iTech, -1, False)
			bButtonFound = True

		# Permanent Alliance
		if techInfo.isPermanentAllianceTrading():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_PERMALLIANCE").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_PERMANENT_ALLIANCE, self.iTech, -1, False)
			bButtonFound = True

		# Vassal States
		if techInfo.isVassalStateTrading():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_VASSAL").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_VASSAL_STATE, self.iTech, -1, False)
			bButtonFound = True

		# Extra LOS (line of sight) from water
		if techInfo.isExtraWaterSeeFrom():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_LOS").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_LOS_BONUS, self.iTech, -1, False)
			bButtonFound = True

		# Map centering
		if techInfo.isMapCentering():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_MAPCENTER").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_MAP_CENTER, self.iTech, -1, False)
			bButtonFound = True

		# Map reveal
		if techInfo.isMapVisible():
			screen.attachImageButton(panelName, "", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TECH_MAPREVEAL").getPath(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_HELP_MAP_REVEAL, self.iTech, -1, False)
			bButtonFound = True

		if not bButtonFound:
			txtKeyNoButtonFound = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoButtonFound, ())
			yPanelCenter = self.Y_ENABLES + (self.H_ENABLES / 2)
			screen.addMultilineText(textName, szText, self.X_ENABLES + 7, yPanelCenter, self.W_ENABLES - 14, self.H_ENABLES - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: add non-tradeable (<bTrade>) tech list at the end of placeSpecial, addition with the help of chatgpt thanks. -->
	# <!-- custom: Note: We intentionally keep all textual info here (units, buildings, civics, bonuses, builds, promotions)
	# even though they're also displayed as buttons in the Enables panel. This duplication is helpful because
	# users find it easier to read and scan the textual list for quick reference. (Claude code Opus 4.5) -->
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

		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL + 5, self.Y_SPECIAL + 30, self.W_SPECIAL - 3, self.H_SPECIAL - 35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



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
		screen.addMultilineText(szQuoteTextWidget, szText, self.X_HISTORY + 7, self.Y_HISTORY + 10 + self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER, self.W_HISTORY - 5, self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

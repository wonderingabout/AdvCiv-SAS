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
# <!-- custom: uses new buildBTradeString function in CvGameTextMgr.cpp to display in placeSpecial the "This technology cannot be traded" bullet point, see modding ressources readme at (adjust to your mod path anyways etc) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\_1_AdvCiv-SAS\Docs_And_Appendixes\Modding_Ressources\README.md (or whichever path it may be anyways etc if changed path or modifications i did or may have done additionally or kept as is but anyways etc), hopefully helpful or not or yes or etc or and other or and not anyways etc. There is a google drive link and screenshots for steps (most anyways etc) of how i did it if you'd want to try it or do it and see how i did myself hopefully helpful or/and enjoyable or/and plesant or not or yes or and other or and not but or not but or yes but but anyways etc.
#
# Without the DLL modification, i assume it would still run fine if i am not mistaken, just you would not have the bullet point at the tech, for example Future tech, that it cannot be traded in placeSpecial, but only the summary at the end of the list of all non tradeable tech that uses the already existing in base advciv if i am not mistaken anyways etc gc.getTechInfo(iTech).isTrade() if i am not mistaken, but which info of (this tech is not tradeable) is in base advciv not displayed in the placeSpecial bullet of the currently selected tech unless you modify DLL as explained before anyways etc. -->



from CvPythonExtensions import *
import CvUtil
import CvPediaScreen
# <!-- custom: remove or comment out unused imports -->
#import ScreenInput
#import SevoScreenEnums

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



# <!-- custom: similarly to how cache precomputing is handled in sevopedia leader, prebuild only once as a function at relevant time if i may say but anyways etc the list as string of untradeable techs anyways etc ; note also anyways etc: code provided by deepseek ai thanks to my prompt and that i adjusted or not for advciv-sas to tweak (my) (but anyways etc...) previous existing code provided by another ai thanks to my prompt too and that i adjusted or not too xd if i may say but anyways etc -->
def getPrecomputedUntradeableTechsText():
	untradeableTechs = []
	for iTech in xrange(gc.getNumTechInfos()):
		if not gc.getTechInfo(iTech).isTrade():
			techDesc = gc.getTechInfo(iTech).getDescription()
			untradeableTechs.append(techDesc)

	untradeableTechs.sort()

	untradeableTechsText = ""
	bullet = localText.getText("[ICON_BULLET]", ())
	for tech in untradeableTechs:
		untradeableTechsText += u"\n%s%s" % (bullet, tech)

	return untradeableTechsText



class SevoPediaTech(CvPediaScreen.CvPediaScreen):

	def __init__(self, main):
		self.iTech = -1
		self.top = main

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

		self.X_CIVS = self.X_TECH_PANE + self.W_TECH_PANE + 10
		self.Y_CIVS = self.Y_TECH_PANE
		self.W_CIVS = self.top.R_PEDIA_PAGE - self.X_CIVS
		self.H_CIVS = 110

		# advc.004y (note): These dimensions are for the "background" panel, which includes more than just the tech quote.
		self.X_QUOTE_PANE = self.X_TECH_PANE
		self.Y_QUOTE_PANE = self.Y_TECH_PANE + self.H_TECH_PANE + 10
		self.W_QUOTE_PANE = self.top.R_PEDIA_PAGE - self.X_QUOTE_PANE

		# <advc.004y>
		# Move some height settings up:
		self.H_PREREQ_PANE = 124
		self.H_BUILDING_PANE = self.H_PREREQ_PANE
		self.H_UNIT_PANE = self.H_PREREQ_PANE
		#self.H_SPECIAL_PANE = self.top.B_PEDIA_PAGE - self.Y_SPECIAL_PANE
		# Instead use any extra space for the QUOTE_PANE
		self.H_SPECIAL_PANE = self.H_BUILDING_PANE + self.H_UNIT_PANE + 10
		# was 110
		self.H_QUOTE_PANE = self.top.B_PEDIA_PAGE - self.H_SPECIAL_PANE - self.H_PREREQ_PANE - self.Y_QUOTE_PANE - 20
		# </advc.004y>

		self.X_PREREQ_PANE = self.X_TECH_PANE
		self.Y_PREREQ_PANE = self.Y_QUOTE_PANE + self.H_QUOTE_PANE + 10
		self.W_PREREQ_PANE = self.top.W_PEDIA_PAGE / 2 - 5

		self.X_LEADS_TO_PANE = self.X_PREREQ_PANE + self.W_PREREQ_PANE + 10
		self.Y_LEADS_TO_PANE = self.Y_PREREQ_PANE
		self.W_LEADS_TO_PANE = self.W_PREREQ_PANE
		self.H_LEADS_TO_PANE = self.H_PREREQ_PANE

		self.X_SPECIAL_PANE = self.X_TECH_PANE
		self.W_SPECIAL_PANE = self.W_PREREQ_PANE
		self.Y_SPECIAL_PANE = self.Y_PREREQ_PANE + self.H_PREREQ_PANE + 10

		self.X_UNIT_PANE = self.X_LEADS_TO_PANE
		self.W_UNIT_PANE = self.W_LEADS_TO_PANE
		self.Y_UNIT_PANE = self.Y_SPECIAL_PANE

		self.X_BUILDING_PANE = self.X_UNIT_PANE
		self.W_BUILDING_PANE = self.W_UNIT_PANE
		self.Y_BUILDING_PANE = self.Y_UNIT_PANE + self.H_UNIT_PANE + 10



	def interfaceScreen(self, iTech):
		self.iTech = iTech

		self.placeTechPane()
		self.placeCivilizations()
		self.placePrereqs()
		self.placeLeadsTo()
		self.placeUnits()
		self.placeBuildings()
		self.placeSpecial()
		self.placeBackground()



	# <!-- custom: split this more cleanly as a separate method from interfaceScreen if i am not mistaken in assessing so if i may say and also as in other parts of our code as well if i may say but anyways etc ; also Era display code bit/part in this case but anyways etc imported from rfc doc mod and adjusted or not for advciv-sas but anyways etc -->
	def placeTechPane(self):
		screen = self.top.getScreen()
		techInfo = gc.getTechInfo(self.iTech)

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_TECH_PANE, self.Y_TECH_PANE, self.W_TECH_PANE, self.H_TECH_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: was PanelStyles.PANEL_STYLE_MAIN -->
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), techInfo.getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)

		#screen.setLabel(self.top.getNextWidgetName(), "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, self.X_COST + 25, self.Y_COST, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		listBoxName = self.top.getNextWidgetName()
		szEra = gc.getEraInfo(techInfo.getEra()).getDescription() + " Era"

		techCost = techInfo.getResearchCost()
		if (self.top.iActivePlayer != -1):
			techCost = gc.getTeam(gc.getGame().getActiveTeam()).getResearchCost(self.iTech)
		szCostText = u"%c %s" % (gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar(), localText.getText("TXT_KEY_PEDIA_COST_CUSTOM", (techCost,)))

		screen.addListBoxGFC(listBoxName, "", self.X_TECH_PANE + 92, self.Y_TECH_PANE + 14, self.W_TECH_PANE, self.H_TECH_PANE, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(listBoxName, False)
		# <!-- custom: extra space (" ") in some of these listboxstrings but anyways etc to better align with the research icon char starting more on the right anyways etc, depending on where the space is put, the text is so much better left-aligned between rows i think/feel/see or so it seems to me if i mmay say but anyways etc... -->
		screen.appendListBoxString(listBoxName, u" <font=4b>" + techInfo.getDescription() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		screen.appendListBoxString(listBoxName, u"<font=3> " + szEra + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		screen.appendListBoxString(listBoxName, u"<font=4>" + szCostText + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)



	def placeCivilizations(self):
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
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_CATEGORY_CIV", ()), "", False, True, self.X_CIVS, self.Y_CIVS, self.W_CIVS, self.H_CIVS, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		for iCiv in civs: # advc.004y: Use the list computed above
			civ = gc.getCivilizationInfo(iCiv)
			#if civ.isCivilizationFreeTechs(self.iTech):
			screen.attachImageButton(panelName, "", civ.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCiv, 1, False)



	def placeLeadsTo(self):
		screen = self.top.getScreen()
		szLeadsTo = localText.getText("TXT_KEY_PEDIA_LEADS_TO", ())
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, szLeadsTo, "", False, True, self.X_LEADS_TO_PANE, self.Y_LEADS_TO_PANE, self.W_LEADS_TO_PANE, self.H_LEADS_TO_PANE, PanelStyles.PANEL_STYLE_BLUE50)
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
		screen.addPanel(panelName, szRequires, "", False, True, self.X_PREREQ_PANE, self.Y_PREREQ_PANE, self.W_PREREQ_PANE, self.H_PREREQ_PANE, PanelStyles.PANEL_STYLE_BLUE50)
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



	def placeUnits(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_UNITS_ENABLED", ()), "", False, True, self.X_UNIT_PANE, self.Y_UNIT_PANE, self.W_UNIT_PANE, self.H_UNIT_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		iActivePlayer = gc.getGame().getActivePlayer() # advc.003l
		for eLoopUnit in range(gc.getNumUnitInfos()):
			if (eLoopUnit != -1):
				if (isTechRequiredForUnit(self.iTech, eLoopUnit)):
					szButton = gc.getUnitInfo(eLoopUnit).getButton()
					# <advc.003l>
					if iActivePlayer >= 0:
						szButton = gc.getPlayer(iActivePlayer).getUnitButton(eLoopUnit)
					# </advc.003l>
					screen.attachImageButton(panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, eLoopUnit, 1, False)



	def placeBuildings(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_BUILDINGS_ENABLED", ()), "", False, True, self.X_BUILDING_PANE, self.Y_BUILDING_PANE, self.W_BUILDING_PANE, self.H_BUILDING_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")
		for eLoopBuilding in range(gc.getNumBuildingInfos()):
			if (eLoopBuilding != -1):
				if (isTechRequiredForBuilding(self.iTech, eLoopBuilding)):
						screen.attachImageButton(panelName, "", gc.getBuildingInfo(eLoopBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, eLoopBuilding, 1, False)
						
		for eLoopProject in range(gc.getNumProjectInfos()):
			if (isTechRequiredForProject(self.iTech, eLoopProject)):
				screen.attachImageButton(panelName, "", gc.getProjectInfo(eLoopProject).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, eLoopProject, 1, False)



	# <!-- custom: add non-tradeable (<bTrade> if i am not mistaken anyways etc) tech list at the end of placeSpecial, addition from chatgpt thanks to my prompt and adjustments or not or yes or and other or and etc too anyways etc anyways etc anyways etc -->
	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", True, False, self.X_SPECIAL_PANE, self.Y_SPECIAL_PANE, self.W_SPECIAL_PANE, self.H_SPECIAL_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()

		szSpecialText = CyGameTextMgr().getTechHelp(self.iTech, True, False, False, False, -1)[1:]

		# <!-- custom: add the list as string of all untradeable techs if any are untradeable anyways etc ; see also sevopedia main precomputing / cache building for untradeable techs text for details anyways etc -->
		if UNTRADEABLE_TECHS_TEXT:
			szSpecialText += u"\n\n%s%s" % (localText.getText("TXT_KEY_PEDIA_UNTRADEABLE_TECH_REMINDER", ()), UNTRADEABLE_TECHS_TEXT)

		# <!-- custom: seems to overfill a bit actually quite a bit xd after rechecking but anyways etc, reduce height, was self.H_SPECIAL_PANE-10 -->
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL_PANE + 5, self.Y_SPECIAL_PANE + 30, self.W_SPECIAL_PANE - 35, self.H_SPECIAL_PANE - 35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeBackground(self): # advc.004y: renamed from "placeQuote"
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: same reasoning as for/in SevopediaUnit.py, i don't need the redundant background -->
		# advc.004y: Label added for this panel
		#screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_QUOTE_PANE, self.Y_QUOTE_PANE, self.W_QUOTE_PANE, self.H_QUOTE_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(panelName, "", "", True, True, self.X_QUOTE_PANE, self.Y_QUOTE_PANE, self.W_QUOTE_PANE, self.H_QUOTE_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		# <advc.004y> Show strategy help too (like for civics)
		szText = u""
		# <!-- custom: same reasoning as for TXT_KEY_CIVILOPEDIA_STRATEGY in SevoPediaBuilding.py (refer to this file for details), removing (hiding) the entry entirely from the sevopedia ; and same reasoning as for/in SevopediaUnit.py, i don't need the redundant background line -->
		#if len(gc.getTechInfo(self.iTech).getStrategy()) > 0:
		#	szText += localText.getText("TXT_KEY_CIVILOPEDIA_STRATEGY", ())
		#	szText += gc.getTechInfo(self.iTech).getStrategy()
		#	szText += u"\n\n"
		#	szText += localText.getText("TXT_KEY_CIVILOPEDIA_BACKGROUND", ())
		# </advc.004y>
		szText += gc.getTechInfo(self.iTech).getQuote()
		szText += u"\n\n" + gc.getTechInfo(self.iTech).getCivilopedia()
		szQuoteTextWidget = self.top.getNextWidgetName()
		# <!-- custom: i prefer the fancier design, find it way more beautiful too, restoring it ; as for padding adjust/modify it a bit too anyways etc, was self.X_QUOTE_PANE + 9, self.Y_QUOTE_PANE + 12 -->
		# <advc.004y> Now that the quote isn't on top anymore, we can keep it simple:
		#screen.attachMultilineText(panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(szQuoteTextWidget, szText, self.X_QUOTE_PANE + 9, self.Y_QUOTE_PANE + 12, self.W_QUOTE_PANE - (15 * 2), self.H_QUOTE_PANE - (15 * 2), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0

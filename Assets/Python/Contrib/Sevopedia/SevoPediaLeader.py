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
# AI Utilities or Personality Panel for normalization and general helpers for the SevopediaLeader category
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# <!-- custom: Long_Comments_py.txt #3 -->



from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
# <!-- custom: import to display chars before Traits -->
import TraitUtil

# <!-- custom: AI personality cache/value computation moved to a dedicated module to keep this file lean. (ChatGPT-5.2 Thinking) -->
import SevoPediaLeaderAIPValues as _SAS_LeaderAIPValues



gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



# <!-- custom: Leader page display toggle (not part of AI cache module). -->
IS_SHOW_TRAIT_ICONS_IN_LEADER = (gc.getDefineINT("SAS_SEVOPEDIA_LEADER_TRAITS_SHOW_ICONS") > 0)

# <!-- custom: keep debug flag available in this module for existing debug print sites. -->
IS_DEBUG_LEADER = _SAS_LeaderAIPValues.IS_DEBUG_LEADER

# <!-- custom: shared exclusion list used by both cache computation and page rendering. -->
EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS = _SAS_LeaderAIPValues.EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS

# <!-- custom: cache containers (populated once per session from SevoPediaMain). -->
LEADERS_INFO_CACHED = {}
AI_RIGHT_CATEGORIES = ()
AI_MIDDLE_CATEGORIES = ()
AI_LEFT_CATEGORIES = ()

def getPrecomputedCacheOnceOnlyFromSevopediaMainInSevopediaLeaderForEntireSession():
	# Called once (from SevoPediaMain) to prebuild the AI Personality Panel cache.
	return _SAS_LeaderAIPValues.getPrecomputedCacheOnceOnlyFromSevopediaMainInSevopediaLeaderForEntireSession()


class SevoPediaLeader:

	def __init__(self, main):
		self.iLeader = -1
		self.top = main

		self.X_LEADERHEAD_PANE = self.top.X_PEDIA_PAGE
		self.Y_LEADERHEAD_PANE = self.top.Y_PEDIA_PAGE
		# <!-- custom: for the ratio of the portrait, aim to match closely the ingame diplomacy portrait ratio; Long_Comments_py.txt #2 -->
		self.W_LEADERHEAD_PANE = 327
		self.H_LEADERHEAD_PANE = 400

		# <!-- custom: 1) (most) absolute dimensions first -->

		# <!-- custom: make room to add AI personality panel -->
		self.W_AI_PERSONALITY = 290

		self.SMALL_MARGIN = 10
		self.MEDIUM_MARGIN = 20
		# <!-- custom: we also need this information sooner, move it here with the more absolute dimensions of some elements
		self.W_CIV = 64
		self.H_CIV = 64
		self.CIV_MARGIN = 0
		self.CIV_DISELEVATION = 38
		
		self.H_FAVORITES = 110
		self.N_AI_TABLE_NUM = 3

		# <!-- custom: 2) (most) relative dimensions or positions then -->

		self.W_LEADERHEAD = self.W_LEADERHEAD_PANE - 30
		self.H_LEADERHEAD = self.H_LEADERHEAD_PANE - 34
		self.X_LEADERHEAD = self.X_LEADERHEAD_PANE + (self.W_LEADERHEAD_PANE - self.W_LEADERHEAD) / 2
		self.Y_LEADERHEAD = self.Y_LEADERHEAD_PANE + (self.H_LEADERHEAD_PANE - self.H_LEADERHEAD) / 2 + 3

		self.W_AI_TOTAL_TABLES_WIDTH = self.N_AI_TABLE_NUM * self.W_AI_PERSONALITY + self.N_AI_TABLE_NUM * self.MEDIUM_MARGIN

		self.Y_FAVORITES = self.Y_LEADERHEAD_PANE + self.H_LEADERHEAD_PANE + self.SMALL_MARGIN

		# <!-- custom: we need self.W_HISTORY before the favourites coordinates, (even though the history panel is placed under/after the favourites panel when i constructed the page's "spacing" and dimensions of (and between) panels, anyways) because/as the favourites panel uses/needs/is based on the history panel's (relative) position, anyways -->
		# <!-- custom: might as well put the other/rest/remaining HISTORY coordinates if doesn't harm and they are perhaps needed too, anyways -->
		self.X_HISTORY = self.X_LEADERHEAD_PANE
		self.Y_HISTORY = self.Y_FAVORITES + self.H_FAVORITES + self.SMALL_MARGIN
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.W_AI_TOTAL_TABLES_WIDTH - self.X_LEADERHEAD_PANE
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY

		# Music panel (84px, right of Favorites)
		self.W_MUSIC = 84

		self.X_FAVORITES = self.X_LEADERHEAD_PANE
		# Reduce Favorites width to make room for Music panel (84px + margin)
		self.W_FAVORITES = self.W_HISTORY - self.W_CIV - self.W_MUSIC - (2 * self.SMALL_MARGIN)

		self.X_MUSIC = self.X_FAVORITES + self.W_FAVORITES + self.SMALL_MARGIN
		self.Y_MUSIC = self.Y_FAVORITES
		self.H_MUSIC = self.H_FAVORITES
		self.playButtonPath = ArtFileMgr.getInterfaceArtInfo("SAS_EMOJI_PLAY_BUTTON").getPath()

		# <!-- custom: the rest of the coordinates here, as it is dependent on other coordinates we need first that (i.e. before being able to add these) -->
		self.X_AI_PERSONALITY = self.top.R_PEDIA_PAGE - self.W_AI_PERSONALITY 
		self.Y_AI_PERSONALITY = self.Y_LEADERHEAD_PANE
		self.H_AI_PERSONALITY = self.H_LEADERHEAD_PANE + self.SMALL_MARGIN + self.H_FAVORITES + self.SMALL_MARGIN + self.H_HISTORY

		# <!-- custom: AI Personality Panel(s) column widths -->
		self.W_AI_VALUE = 35
		self.W_AI_SCALE = 100
		self.W_AI_LABEL = self.W_AI_PERSONALITY - self.W_AI_VALUE - self.W_AI_SCALE
		self.H_AI_LINE_HEIGHT = 22
		self.H_AI_CATEGORY_SPACING = 10
		self.W_AI_LEFT_SIDE_PADDING = 12
		# <!-- custom: Long_Comments_py.txt #4 -->
		#self.H_AI_UPPER_PADDING = 36
		self.H_AI_UPPER_PADDING = 15

		self.AI_PANEL_RIGHT_TXT_KEY = "TXT_KEY_AI_PERSONALITY_RIGHT_PANEL"
		self.AI_PANEL_MIDDLE_TXT_KEY = "TXT_KEY_AI_PERSONALITY_MIDDLE_PANEL"
		self.AI_PANEL_LEFT_TXT_KEY = "TXT_KEY_AI_PERSONALITY_LEFT_PANEL"

		self.X_TRAITS = self.X_LEADERHEAD_PANE + self.W_LEADERHEAD_PANE + self.SMALL_MARGIN
		self.Y_TRAITS = self.Y_LEADERHEAD_PANE
		self.W_TRAITS = self.W_HISTORY - self.W_LEADERHEAD_PANE - self.SMALL_MARGIN
		self.H_TRAITS = self.H_LEADERHEAD_PANE

		self.X_CIV = self.X_HISTORY + self.W_HISTORY - self.CIV_MARGIN - self.W_CIV
		# <!-- custom: put the flag/civ at the middle Y of the favourites panel -->
		# <!-- custom: quite high as compared to favourites panel's lowest point -->
		self.Y_CIV = self.Y_FAVORITES + self.CIV_DISELEVATION



	def interfaceScreen(self, iLeader):
		self.iLeader = iLeader

		# <!-- custom: change call order to match filling/building order, generally from top left to bottom and left to right but not always, reordering in such a way is maybe a bit more intuitive this way perhaps or clearer or helpful or not or other etc anyways, -->
		self.placeLeaderHeadPane()
		self.placeFavorites()
		self.placeMusic()
		self.placeHistory()
		self.placeCiv()
		self.placeTraits()

		# <!-- custom: for excluded leader indexes from calculations, leave the zone/space where the AI personality panel was supposed to be especially empty, instead of getting a key error or missing leader from leaders_info_cached; Long_Comments_py.txt #10 -->
		#
		if (iLeader not in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS):
			self.placeAIPersonalityPanel(iLeader)
		else:
			if IS_DEBUG_LEADER:
				print("[DEBUG] Leader index iLeader=%d in EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS=%s is skipped, leave the place where AI Personality panel was supposed to be entirely empty so we don't get a missing key in leaders_info_cached Error, while signifying clearly enough hopefully that the excluded leader currently selected doesn't have an item in leaders_info_cached and AI Personality Panel at all/is not part of it." % (iLeader, str(EXCLUDED_LEADER_INDEXES_FROM_CALCULATIONS)))



	# <!-- custom: wrap leader placement in a specific function for clarity or flexibility or not anyways, -->
	def placeLeaderHeadPane(self):
		screen = self.top.getScreen()
		leaderPanelWidget = self.top.getNextWidgetName()
		screen.addPanel(leaderPanelWidget, "", "", True, True, self.X_LEADERHEAD_PANE, self.Y_LEADERHEAD_PANE, self.W_LEADERHEAD_PANE, self.H_LEADERHEAD_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		self.leaderWidget = self.top.getNextWidgetName()
		screen.addLeaderheadGFC(self.leaderWidget, self.iLeader, AttitudeTypes.ATTITUDE_PLEASED, self.X_LEADERHEAD, self.Y_LEADERHEAD, self.W_LEADERHEAD, self.H_LEADERHEAD, WidgetTypes.WIDGET_GENERAL, -1, -1)



	# <!-- custom: imported from RFC DOC (C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\RFC Dawn of Civilization\Assets\Python\Pedia\CvPediaLeader.py) and modified or not for AdvCiv-SAS. -->
	def placeFavorites(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		screen.addPanel(panel, localText.getText("TXT_KEY_PEDIA_FAVOURITE_CIVICS_AND_RELIGIONS", ()), "", False, True, self.X_FAVORITES, self.Y_FAVORITES, self.W_FAVORITES, self.H_FAVORITES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.enableSelect(panel, False)
		screen.attachLabel(panel, "", "  ")

		# Civic
		iCivic = gc.getLeaderHeadInfo(self.iLeader).getFavoriteCivic()
		if iCivic > -1:
			screen.attachImageButton(panel, "", gc.getCivicInfo(iCivic).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, iCivic, 1, False)

		# Religion
		iReligion = gc.getLeaderHeadInfo(self.iLeader).getFavoriteReligion()
		if iReligion > -1:
			screen.attachImageButton(panel, "", gc.getReligionInfo(iReligion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iReligion, 1, False)



	def placeMusic(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SAS_MUSIC_PANEL", ()), "", False, True, self.X_MUSIC, self.Y_MUSIC, self.W_MUSIC, self.H_MUSIC, PanelStyles.PANEL_STYLE_BLUE50)

		# <!-- custom: use attachLabel for padding similar to other 84px panels -->
		screen.attachLabel(panelName, "", "  ")

		buttonSize = 64
		buttonX = (self.W_MUSIC - buttonSize) / 2
		buttonY = 10
		# <!-- custom: redirect to leader's peace music entry in Sevopedia Music category -->
		iMusicKey = self.top.SAS_getLeaderPeaceMusicKey(self.iLeader)
		if iMusicKey != -1:
			screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, self.playButtonPath, buttonX, buttonY, buttonSize, buttonSize, WidgetTypes.WIDGET_PYTHON, self.top.SAS_PEDIA_PYTHON_MUSIC_ENTRY, iMusicKey)
		else:
			screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, self.playButtonPath, buttonX, buttonY, buttonSize, buttonSize, WidgetTypes.WIDGET_PEDIA_MAIN, SevoScreenEnums.PEDIA_MUSIC, -1)



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, "", "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		historyTextName = self.top.getNextWidgetName()
		CivilopediaText = gc.getLeaderHeadInfo(self.iLeader).getCivilopedia()
		CivilopediaText = u"<font=2>" + CivilopediaText + u"</font>"
		screen.attachMultilineText(panelName, historyTextName, CivilopediaText, WidgetTypes.WIDGET_GENERAL,-1,-1, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: logo / flag of the civ -->
	def placeCiv(self):
		screen = self.top.getScreen()
		for iCiv in xrange(gc.getNumCivilizationInfos()):
			civ = gc.getCivilizationInfo(iCiv)
			if civ.isLeaders(self.iLeader):
				screen.setImageButton(self.top.getNextWidgetName(), civ.getButton(), self.X_CIV, self.Y_CIV, self.W_CIV, self.H_CIV, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCiv, 1)



	# advc.001 (from Taurus): Static for use by SevoPediaMain; body cut from placeTraits.
	@staticmethod
	def getCiv(iLeader):
		iNumCivs = 0
		for iCiv in xrange(gc.getNumCivilizationInfos()):
			if gc.getCivilizationInfo(iCiv).isLeaders(iLeader):
				iNumCivs += 1
				iLeaderCiv = iCiv
		# <advc.001> (No functional change here)
		if iNumCivs != 1:
			return -1
		return iLeaderCiv # </advc.001>



	def placeTraits(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: no header for more compact and prettier display -->
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_LEADER_TRAITS", ()), "", True, False, self.X_TRAITS, self.Y_TRAITS, self.W_TRAITS, self.H_TRAITS, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		# advc.001: Civ search moved into a static method
		szSpecialText = CyGameTextMgr().parseLeaderTraits(self.iLeader, SevoPediaLeader.getCiv(self.iLeader), False, True)
		szSpecialText = szSpecialText[1:]

		# <!-- custom: add trait icons by replacing the trait header text once per leader trait (linked or plain); avoids per-line scans and keeps only traits the leader actually has. (GPT-5.2-Codex) -->
		if IS_SHOW_TRAIT_ICONS_IN_LEADER:
			leader = gc.getLeaderHeadInfo(self.iLeader)
			for iTrait in xrange(gc.getNumTraitInfos()):
				if leader.hasTrait(iTrait):
					traitDesc = gc.getTraitInfo(iTrait).getDescription()
					traitLink = u"<link=literal>%s</link>" % traitDesc
					traitIcon = TraitUtil.getIcon(iTrait)
					# <!-- custom: prefer replacing the linked trait label; if traits are plain text, replace the first matching trait name only. (GPT-5.2-Codex) -->
					szReplaced = szSpecialText.replace(traitLink, traitIcon + u" " + traitLink)
					if szReplaced == szSpecialText:
						szSpecialText = szSpecialText.replace(traitDesc, traitIcon + u" " + traitDesc, 1)
					else:
						szSpecialText = szReplaced

		# <!-- custom: reduce top padding now that the traits header is removed (GPT-5.2-Codex). Was headerExtraHeight 30 -->
		headerExtraHeight = 10
		screen.addMultilineText(listName, szSpecialText, self.X_TRAITS + 5, self.Y_TRAITS + headerExtraHeight, self.W_TRAITS - 10, self.H_TRAITS - headerExtraHeight - 5, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def getXAIPanelCoordinate(self, tableId):
		return self.X_AI_PERSONALITY - tableId * self.W_AI_PERSONALITY - tableId * self.MEDIUM_MARGIN



	def setupAIPanel(self, screen, txtKey, xPanel):
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText(txtKey, ()),"", True, True, xPanel, self.Y_AI_PERSONALITY, self.W_AI_PERSONALITY, self.H_AI_PERSONALITY, PanelStyles.PANEL_STYLE_BLUE50)



	def fillAITableRow(self, screen, label, value, scale, xLabel, xValue, xScale, y):
		labelText = u"<font=2>%s</font>" % label
		valueText = u"<font=2b>%d</font>" % value
		scaleText = u"<font=2>%s</font>" % scale

		screen.setText(self.top.getNextWidgetName(), "", labelText, CvUtil.FONT_LEFT_JUSTIFY, xLabel, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText(self.top.getNextWidgetName(), "", valueText, CvUtil.FONT_LEFT_JUSTIFY, xValue, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText(self.top.getNextWidgetName(), "", scaleText, CvUtil.FONT_LEFT_JUSTIFY, xScale, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)



	def renderAICategories(self, screen, ai_categories, xPanel, yPanel, leader_info_cached):
		xLabel = xPanel + self.W_AI_LEFT_SIDE_PADDING
		xValue = xLabel + self.W_AI_LABEL
		xScale = xValue + self.W_AI_VALUE
		y = yPanel + self.H_AI_UPPER_PADDING

		for ai_category in ai_categories:
			ai_category_header_line, ai_category_x_offset, ai_category_key_order = ai_category

			# AI Category Header Line
			if ai_category_header_line is not None:
				xOffsetButton = xLabel + ai_category_x_offset
				screen.setText(self.top.getNextWidgetName(), "", ai_category_header_line, CvUtil.FONT_LEFT_JUSTIFY, xOffsetButton, y, 0, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				y += self.H_AI_LINE_HEIGHT

			# <!-- custom: AI Category items in their predefined order -->
			for key in ai_category_key_order:
				label, norm_value, scale = leader_info_cached[key]
				self.fillAITableRow(screen, label, norm_value, scale, xLabel, xValue, xScale, y)
				y += self.H_AI_LINE_HEIGHT

			# <!-- custom: space for next ai_category if any are there (else still space but not used more efficient this way i think i mean than rechecking each time and we have some tables that overflow vertically too so maybe fine this way too if not broken in this case i mean maybe-->
			y += self.H_AI_CATEGORY_SPACING



	# Place AI Personality Panel (using precomputed scales)
	# Renders the full AI Personality panel in the Sevopedia Leader page using precomputed <!-- custom: leader info tuples in leaders_info_cached --> for the given leader.
	def placeAIPersonalityPanel(self, iLeader):
		screen = self.top.getScreen()

		xPanelRight = self.getXAIPanelCoordinate(self.N_AI_TABLE_NUM - 3)
		xPanelMiddle = self.getXAIPanelCoordinate(self.N_AI_TABLE_NUM - 2)
		xPanelLeft = self.getXAIPanelCoordinate(self.N_AI_TABLE_NUM - 1)

		self.setupAIPanel(screen, self.AI_PANEL_RIGHT_TXT_KEY, xPanelRight)
		self.setupAIPanel(screen, self.AI_PANEL_MIDDLE_TXT_KEY, xPanelMiddle)
		self.setupAIPanel(screen, self.AI_PANEL_LEFT_TXT_KEY, xPanelLeft)

		# <!-- custom: cache for performance optimization. -->
		leader_info_cached = LEADERS_INFO_CACHED[iLeader]

		self.renderAICategories(screen, AI_RIGHT_CATEGORIES, xPanelRight, self.Y_AI_PERSONALITY, leader_info_cached)
		self.renderAICategories(screen, AI_MIDDLE_CATEGORIES, xPanelMiddle, self.Y_AI_PERSONALITY, leader_info_cached)
		self.renderAICategories(screen, AI_LEFT_CATEGORIES, xPanelLeft, self.Y_AI_PERSONALITY, leader_info_cached)



	def handleInput (self, inputClass):
		# <!-- custom: leaderhead hotkeys (animations/moods) are cosmetic; if they conflict with search,
		# consider removing or remapping here. (GPT-5.2-Codex) -->
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CHARACTER):
			if (inputClass.getData() == int(InputTypes.KB_0)):
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.LEADERANIM_GREETING)
			elif (inputClass.getData() == int(InputTypes.KB_6)):
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.LEADERANIM_DISAGREE)
			elif (inputClass.getData() == int(InputTypes.KB_7)):
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.LEADERANIM_AGREE)
			elif (inputClass.getData() == int(InputTypes.KB_1)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_FRIENDLY)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_2)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_PLEASED)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_3)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_CAUTIOUS)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_4)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_ANNOYED)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			elif (inputClass.getData() == int(InputTypes.KB_5)):
				self.top.getScreen().setLeaderheadMood(self.leaderWidget, AttitudeTypes.ATTITUDE_FURIOUS)
				self.top.getScreen().performLeaderheadAction(self.leaderWidget, LeaderheadAction.NO_LEADERANIM)
			else:
				self.top.getScreen().leaderheadKeyInput(self.leaderWidget, inputClass.getData())
		return 0

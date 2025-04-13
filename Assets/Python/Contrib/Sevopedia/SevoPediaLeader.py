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
import random

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaLeader:



	def __init__(self, main):
		self.iLeader = -1
		self.top = main

		self.X_LEADERHEAD_PANE = self.top.X_PEDIA_PAGE
		self.Y_LEADERHEAD_PANE = self.top.Y_PEDIA_PAGE
		self.W_LEADERHEAD_PANE = 240
		self.H_LEADERHEAD_PANE = 290

		self.W_LEADERHEAD = self.W_LEADERHEAD_PANE - 30
		self.H_LEADERHEAD = self.H_LEADERHEAD_PANE - 34
		self.X_LEADERHEAD = self.X_LEADERHEAD_PANE + (self.W_LEADERHEAD_PANE - self.W_LEADERHEAD) / 2
		self.Y_LEADERHEAD = self.Y_LEADERHEAD_PANE + (self.H_LEADERHEAD_PANE - self.H_LEADERHEAD) / 2 + 3

		self.W_CIV = 64
		self.H_CIV = 64
		self.X_CIV = self.X_LEADERHEAD_PANE + (self.W_LEADERHEAD_PANE - self.W_CIV) / 2
		self.Y_CIV = self.Y_LEADERHEAD_PANE + self.H_LEADERHEAD_PANE + 10

		# <!-- custom: make room to add AI personality panel -->
		self.W_AI_PERSONALITY = 500
		self.W_AI_PERSONALITY_MARGIN = 20

		self.X_CIVIC = self.X_LEADERHEAD_PANE + self.W_LEADERHEAD_PANE + 10
		self.Y_CIVIC = self.Y_LEADERHEAD_PANE
		self.W_CIVIC = self.top.R_PEDIA_PAGE - self.W_AI_PERSONALITY - self.X_CIVIC - self.W_AI_PERSONALITY_MARGIN
		self.H_CIVIC = 80

		self.X_TRAITS = self.X_LEADERHEAD_PANE + self.W_LEADERHEAD_PANE + 10
		self.Y_TRAITS = self.Y_CIVIC + self.H_CIVIC + 10
		self.W_TRAITS = self.top.R_PEDIA_PAGE - self.W_AI_PERSONALITY - self.X_TRAITS - self.W_AI_PERSONALITY_MARGIN
		self.H_TRAITS = self.Y_CIV + self.H_CIV - self.Y_TRAITS

		self.X_HISTORY = self.X_LEADERHEAD_PANE
		self.Y_HISTORY = self.Y_CIV + self.H_CIV + 10
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.W_AI_PERSONALITY - self.X_HISTORY - self.W_AI_PERSONALITY_MARGIN
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY

		# <!-- custom: the rest of the data here, as it is dependent on other data we need first
		# that (i.e. before being able to add these) -->
		self.X_AI_PERSONALITY = self.X_HISTORY + self.W_HISTORY + self.W_AI_PERSONALITY_MARGIN
		self.Y_AI_PERSONALITY = self.Y_CIVIC
		self.H_AI_PERSONALITY = self.top.B_PEDIA_PAGE - 65



	def interfaceScreen(self, iLeader):
		self.iLeader = iLeader
		screen = self.top.getScreen()

		leaderPanelWidget = self.top.getNextWidgetName()
		screen.addPanel(leaderPanelWidget, "", "", True, True, self.X_LEADERHEAD_PANE, self.Y_LEADERHEAD_PANE, self.W_LEADERHEAD_PANE, self.H_LEADERHEAD_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		self.leaderWidget = self.top.getNextWidgetName()
		screen.addLeaderheadGFC(self.leaderWidget, self.iLeader, AttitudeTypes.ATTITUDE_PLEASED, self.X_LEADERHEAD, self.Y_LEADERHEAD, self.W_LEADERHEAD, self.H_LEADERHEAD, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# <!-- custom: change call order to match filling from top left to bottom right, more
		# intuitive this way perhaps, anyways, -->
		self.placeCiv()
		self.placeCivic()
		self.placeReligion()
		self.placeTraits()
		self.placeHistory()
		self.placeAIPersonalityPanel(iLeader)



	def placeCiv(self):
		screen = self.top.getScreen()
		for iCiv in range(gc.getNumCivilizationInfos()):
			civ = gc.getCivilizationInfo(iCiv)
			if civ.isLeaders(self.iLeader):
				screen.setImageButton(self.top.getNextWidgetName(), civ.getButton(), self.X_CIV, self.Y_CIV, self.W_CIV, self.H_CIV, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCiv, 1)



	# advc.001 (from Taurus): Static for use by SevoPediaMain; body cut from placeTraits.
	@staticmethod
	def getCiv(iLeader):
		iNumCivs = 0
		for iCiv in range(gc.getNumCivilizationInfos()):
			if gc.getCivilizationInfo(iCiv).isLeaders(iLeader):
				iNumCivs += 1
				iLeaderCiv = iCiv
		# <advc.001> (No functional change here)
		if iNumCivs != 1:
			return -1
		return iLeaderCiv # </advc.001>



	def placeCivic(self):		
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_FAV_CIVIC_AND_RELIGION", ()), "", True, True, self.X_CIVIC, self.Y_CIVIC, self.W_CIVIC, self.H_CIVIC, PanelStyles.PANEL_STYLE_BLUE50)
		iCivic = gc.getLeaderHeadInfo(self.iLeader).getFavoriteCivic()
		if (-1 != iCivic):
			szCivicText = u"<link=literal>" + gc.getCivicInfo(iCivic).getDescription() + u"</link>"
			listName = self.top.getNextWidgetName()
			screen.addMultilineText(listName, szCivicText, self.X_CIVIC+5, self.Y_CIVIC+30, self.W_CIVIC-10, self.H_CIVIC-10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeReligion(self):		
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		iReligion = gc.getLeaderHeadInfo(self.iLeader).getFavoriteReligion()
		if (-1 != iReligion):
			szReligionText = u"<link=literal>" + gc.getReligionInfo(iReligion).getDescription() + u"</link>"
			listName = self.top.getNextWidgetName()
			screen.addMultilineText(listName, szReligionText, self.X_CIVIC+5, self.Y_CIVIC+50, self.W_CIVIC-10, self.H_CIVIC-10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeTraits(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_TRAITS", ()), "", True, False, self.X_TRAITS, self.Y_TRAITS, self.W_TRAITS, self.H_TRAITS, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		# advc.001: Civ search moved into a static method
		szSpecialText = CyGameTextMgr().parseLeaderTraits(self.iLeader, SevoPediaLeader.getCiv(self.iLeader), False, True)
		szSpecialText = szSpecialText[1:]
		screen.addMultilineText(listName, szSpecialText, self.X_TRAITS+5, self.Y_TRAITS+30, self.W_TRAITS-10, self.H_TRAITS-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, "", "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		historyTextName = self.top.getNextWidgetName()
		CivilopediaText = gc.getLeaderHeadInfo(self.iLeader).getCivilopedia()
		CivilopediaText = u"<font=2>" + CivilopediaText + u"</font>"
		screen.attachMultilineText(panelName, historyTextName, CivilopediaText, WidgetTypes.WIDGET_GENERAL,-1,-1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeAIPersonalityPanel(self, iLeader):
		# <!-- custom: based on placeHistory then tweaked or/and modified or/and not
		# also data fetching logic mostly if not entirely provided by ChatGPT, or/and with
		# some additions or modifications or removals or other i did or did not, anyways
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_AI_PERSONALITY", ()), "", True, True,
						self.X_AI_PERSONALITY, self.Y_AI_PERSONALITY,
						self.W_AI_PERSONALITY, self.H_AI_PERSONALITY,
						PanelStyles.PANEL_STYLE_BLUE50)

		leader = gc.getLeaderHeadInfo(iLeader)
		numLeaders = gc.getNumLeaderHeadInfos()

		# Table positioning
		xName = self.X_AI_PERSONALITY + 15
		xValue = xName + 260
		xScale = xValue + 60
		y = self.Y_AI_PERSONALITY + 35
		lineHeight = 22

		def get_plus_scale(val, min_val, max_val, inverse=False):
			if max_val == min_val:
				return "+"
			ratio = float(val - min_val) / float(max_val - min_val)
			if inverse:
				ratio = 1.0 - ratio
			if ratio < 0.2:
				return "+"
			elif ratio < 0.4:
				return "++"
			elif ratio < 0.6:
				return "+++"
			elif ratio < 0.8:
				return "++++"
			else:
				return "+++++"

		attribute_categories = {
			"War Strategy": [
				("Max War Rand", "getMaxWarRand"),
				("Max War Nearby Power Ratio", "getMaxWarNearbyPowerRatio"),
				("Max War Distant Power Ratio", "getMaxWarDistantPowerRatio"),
				("Max War Min Adjacent Land Percent", "getMaxWarMinAdjacentLandPercent"),
				("Limited War Rand", "getLimitedWarRand"),
				("Limited War Power Ratio", "getLimitedWarPowerRatio"),
				("Dogpile War Rand", "getDogpileWarRand"),
				("Make Peace Rand", "getMakePeaceRand"),
			],
			"Diplomacy": [
				("Base Attitude", "getBaseAttitude"),
				("Peace Weight", "getBasePeaceWeight"),
				("Warmonger Respect", "getWarmongerRespect"),
				("Demand Sneak Prob", "getDemandRebukedSneakProb"),
				("Demand War Prob", "getDemandRebukedWarProb"),
				("Refuse Talk Threshold", "getRefuseToTalkWarThreshold"),
				("No Tech Trade Threshold", "getNoTechTradeThreshold"),
				("Tech Trade Known %", "getTechTradeKnownPercent"),
				("Declare War Trade Rand", "getDeclareWarTradeRand"),
			],
			"Victory Strategy": [
				("Culture Victory Weight", "getCultureVictoryWeight"),
				("Space Victory Weight", "getSpaceVictoryWeight"),
				("Conquest Victory Weight", "getConquestVictoryWeight"),
				("Domination Victory Weight", "getDominationVictoryWeight"),
				("Diplomacy Victory Weight", "getDiplomacyVictoryWeight"),
			],
			"Economic Preferences": [
				("Espionage Weight", "getEspionageWeight"),
				("Build Unit Prob", "getBuildUnitProb"),
				("Base Attack Odds", "getBaseAttackOddsChange"),
				("Attack Odds Rand", "getAttackOddsChangeRand"),
				("Wonder Construct Rand", "getWonderConstructRand"),
				("Max Gold Trade %", "getMaxGoldTradePercent"),
				("Max GPT Trade %", "getMaxGoldPerTurnTradePercent"),
			],
			"Attitude Modifiers": [
				("Worse Rank Attitude Change", "getWorseRankDifferenceAttitudeChange"),
				("Better Rank Attitude Change", "getBetterRankDifferenceAttitudeChange"),
				("Close Borders Attitude Change", "getCloseBordersAttitudeChange"),
				("Same Religion Attitude Limit", "getSameReligionAttitudeChangeLimit"),
				("Diff Religion Attitude Limit", "getDifferentReligionAttitudeChangeLimit"),
				("Share War Attitude Limit", "getShareWarAttitudeChangeLimit"),
				("Favorite Civic Attitude Limit", "getFavoriteCivicAttitudeChangeLimit"),
			],
			"Trade Thresholds": [
				("Tech Refuse Attitude", "getTechRefuseAttitudeThreshold"),
				("City Refuse Attitude", "getCityRefuseAttitudeThreshold"),
				("Strategic Bonus Refuse Attitude", "getStrategicBonusRefuseAttitudeThreshold"),
				("Health Bonus Refuse Attitude", "getHealthBonusRefuseAttitudeThreshold"),
				("Happiness Bonus Refuse Attitude", "getHappinessBonusRefuseAttitudeThreshold"),
				("Map Refuse Attitude", "getMapRefuseAttitudeThreshold"),
				("Declare War Refuse Attitude", "getDeclareWarRefuseAttitudeThreshold"),
				("Declare War On Them Refuse", "getDeclareWarThemRefuseAttitudeThreshold"),
				("Stop Trading Refuse", "getStopTradingRefuseAttitudeThreshold"),
				("Stop Trading Them Refuse", "getStopTradingThemRefuseAttitudeThreshold"),
				("Adopt Civic Refuse", "getAdoptCivicRefuseAttitudeThreshold"),
				("Convert Religion Refuse", "getConvertReligionRefuseAttitudeThreshold"),
				("Open Borders Refuse", "getOpenBordersRefuseAttitudeThreshold"),
				("Vassal Refuse", "getVassalRefuseAttitudeThreshold"),
			],
		}

		for category, attributes in attribute_categories.items():
			screen.setText(self.top.getNextWidgetName(), "", u"<font=3b>%s</font>" % category,
						   CvUtil.FONT_LEFT_JUSTIFY, xName, y, 0, FontTypes.SMALL_FONT,
						   WidgetTypes.WIDGET_GENERAL, -1, -1)
			y += lineHeight

			for label, funcName in attributes:
				try:
					values = [getattr(gc.getLeaderHeadInfo(i), funcName)() for i in range(numLeaders)]
					value = getattr(leader, funcName)()
					min_val = min(values)
					max_val = max(values)
					inverse = funcName in [
						"getDogpileWarRand", "getDemandRebukedWarProb", "getDeclareWarTradeRand",
						"getMaxWarRand", "getLimitedWarRand", "getBaseAttackOddsChange",
						"getRefuseToTalkWarThreshold", "getNoTechTradeThreshold"
					]
					plus_label = get_plus_scale(value, min_val, max_val, inverse)

					screen.setText(self.top.getNextWidgetName(), "", u"<font=2>%s</font>" % label,
								   CvUtil.FONT_LEFT_JUSTIFY, xName, y, 0, FontTypes.SMALL_FONT,
								   WidgetTypes.WIDGET_GENERAL, -1, -1)
					screen.setText(self.top.getNextWidgetName(), "", u"<font=2b>%d</font>" % value,
								   CvUtil.FONT_LEFT_JUSTIFY, xValue, y, 0, FontTypes.SMALL_FONT,
								   WidgetTypes.WIDGET_GENERAL, -1, -1)
					screen.setText(self.top.getNextWidgetName(), "", u"<font=2>%s</font>" % plus_label,
								   CvUtil.FONT_LEFT_JUSTIFY, xScale, y, 0, FontTypes.SMALL_FONT,
								   WidgetTypes.WIDGET_GENERAL, -1, -1)
					y += lineHeight
				except:
					pass



	def handleInput (self, inputClass):
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

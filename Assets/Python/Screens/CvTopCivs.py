## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
# Author - Jon Shafer
# Top Civilizations screen
#
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

import PyHelpers
# <!-- custom: SASCurrentDefines reads the defines this module reads by name: one cache for every module, emptied on a live override, about 80 ns a read under Python 2.4, against 279 ns through gc in game. See KI#128.9. (Claude code Opus 5.5) -->
import SASCurrentDefines
import CvUtil
import CvScreenEnums
import random
from CvPythonExtensions import *
# <!-- custom: SASTextScale for the label font tag of the Exit button. (Claude code Opus 5.5) -->
import SASTextScale
# <!-- custom: SASGameRecordConfig for the cached SGR level that pre-gates the ranking's rows, SASGameRecordActions for the helper that writes them. (Claude code Opus 5.5) -->
import SASGameRecordConfig
import SASGameRecordActions
# <!-- custom: SASSessionTunables holds the settings only Python reads, moved out of GlobalDefines_advciv_sas.xml. (Claude code Opus 5.5) -->
import SASSessionTunables

PyPlayer = PyHelpers.PyPlayer
gc = CyGlobalContext()
localText = CyTranslator()

NUM_CIVILIZATIONS = 8

TOP_CIVS_CATEGORY_KEYS = ("WEALTH", "POWER", "TECH", "CULTURE", "SIZE")
# <!-- custom: Lazy caches of SAS_UI_TOP_CIVS_ON, from SASSessionTunables, and SAS_AIAUTOPLAY_DISMISS_INFO_POPUPS_ON, from the XML, read on the first ranking after XML has loaded; edits to either need a Civ4 restart anyway. (Claude code Opus 5.5) -->
g_bTopCivsOn = None
g_bDismissInfoPopupsOn = None

class CvTopCivs:
	# The Greatest Civilizations screen
	#
	def __init__(self):

		self.X_SCREEN = 0#205
		self.Y_SCREEN = 0#27
		self.W_SCREEN = 1024#426
		self.H_SCREEN = 768#470

		self.X_MAIN_PANEL = 250
		self.Y_MAIN_PANEL = 70
		self.W_MAIN_PANEL = 550
		self.H_MAIN_PANEL = 500

		self.iMarginSpace = 15

		self.X_HEADER_PANEL = self.X_MAIN_PANEL + self.iMarginSpace
		self.Y_HEADER_PANEL = self.Y_MAIN_PANEL + self.iMarginSpace
		self.W_HEADER_PANEL = self.W_MAIN_PANEL - (self.iMarginSpace * 2)
		self.H_HEADER_PANEL = self.H_MAIN_PANEL - (self.iMarginSpace * 2)

#		iWHeaderPanelRemainingAfterLeader = self.W_HEADER_PANEL - self.W_LEADER_ICON + (self.iMarginSpace * 3)
#		iXHeaderPanelRemainingAfterLeader = self.X_LEADER_ICON + self.W_LEADER_ICON + self.iMarginSpace
		self.X_LEADER_TITLE_TEXT = 500#iXHeaderPanelRemainingAfterLeader + (iWHeaderPanelRemainingAfterLeader / 2)
		self.Y_LEADER_TITLE_TEXT = self.Y_HEADER_PANEL + self.iMarginSpace
		self.W_LEADER_TITLE_TEXT = self.W_HEADER_PANEL / 3
		self.H_LEADER_TITLE_TEXT = self.H_HEADER_PANEL / 3

		self.X_TEXT_PANEL = self.X_HEADER_PANEL + self.iMarginSpace
		self.Y_TEXT_PANEL = self.Y_HEADER_PANEL + 132
		self.W_TEXT_PANEL = self.W_HEADER_PANEL - (self.iMarginSpace * 2)
		self.H_TEXT_PANEL = 265#self.H_MAIN_PANEL - self.H_HEADER_PANEL - (self.iMarginSpace * 3) + 10 #10 is the fudge factor
		self.iTEXT_PANEL_MARGIN = 35

		self.X_RANK_TEXT = 430
		self.Y_RANK_TEXT = 230
		self.W_RANK_TEXT = 300
		self.H_RANK_TEXT = 30

		self.X_EXIT = 460
		self.Y_EXIT = self.Y_MAIN_PANEL + 440
		self.W_EXIT = 120
		self.H_EXIT = 30

	def showScreen(self):
		# Use a popup to display the opening text
		#
		if ( CyGame().isPitbossHost() ):
			return
		# <!-- custom: turnChecker already skips network games, but CvScreensInterface.showTopCivs calls this directly; on one peer its two synchronized random draws below would put that peer out of sync, and its replay rows would exist there only (Codex's review, 2026-11-19). (Claude code Opus 5.5) -->
		if CyGame().isNetworkMultiPlayer():
			return

		# Text
		# <!-- custom: Was a hardcoded <font=3>, smaller than the other splash titles and fixed whatever the UI font settings; now the title tag, as theirs (the user, 2026-11-21). (Claude code Opus 5.5) -->
		self.TITLE_TEXT = SASTextScale.titleText(localText.getText("TXT_KEY_TOPCIVS_TITLE", ()).upper())
		# <!-- custom: The splash and dialog screens gave their OK/Exit button the title font, the label font or none, so the same fixed-size button read out of proportion with the screen's own text from one screen to the next; all now take the label font, as the rest of their text does (the user, 2026-11-21). (Claude code Opus 5.5) -->
		self.EXIT_TEXT = SASTextScale.labelText(localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper())
		# advc.038: Moved up
		self.TypeList = [
			localText.getText("TXT_KEY_TOPCIVS_WEALTH", ()),
			localText.getText("TXT_KEY_TOPCIVS_POWER", ()),
			localText.getText("TXT_KEY_TOPCIVS_TECH", ()),
			localText.getText("TXT_KEY_TOPCIVS_CULTURE", ()),
			localText.getText("TXT_KEY_TOPCIVS_SIZE", ()),
		]
		# <advc.038>
		randIndex = gc.getGame().getSorenRandNum(len(self.TypeList), "advc.038")
		# <!-- custom: Kept for the SASGameRecord rows, which name the category by key rather than by its translated text. (Claude code Opus 5.5) -->
		self.szCategoryKey = TOP_CIVS_CATEGORY_KEYS[randIndex]
		if(randIndex == 0): # Wealth: Herodotus, Thucydides
			self.HistorianList = [ localText.getText("TXT_KEY_TOPCIVS_HISTORIAN1", ()), localText.getText("TXT_KEY_TOPCIVS_HISTORIAN2", ()) ]
		elif(randIndex == 1): # Power: Tacitus, Machiavelli
			self.HistorianList = [ localText.getText("TXT_KEY_TOPCIVS_HISTORIAN9", ()), localText.getText("TXT_KEY_TOPCIVS_HISTORIAN11", ()) ]
		elif(randIndex == 2): # Tech: Gibbon, Pliny
			self.HistorianList = [ localText.getText("TXT_KEY_TOPCIVS_HISTORIAN3", ()), localText.getText("TXT_KEY_TOPCIVS_HISTORIAN5", ()) ]
		elif(randIndex == 3): # Culture: Bede, McCauley
			self.HistorianList = [ localText.getText("TXT_KEY_TOPCIVS_HISTORIAN7", ()), localText.getText("TXT_KEY_TOPCIVS_HISTORIAN10", ()) ]
		else: # Size: Livy, Toynbee
			self.HistorianList = [ localText.getText("TXT_KEY_TOPCIVS_HISTORIAN6", ()), localText.getText("TXT_KEY_TOPCIVS_HISTORIAN8", ()) ]
		# Unassigned: St. Augustine - is he really considered a historian? He's also in the game as a Great Prophet.
		# </advc.038>
		#self.HistorianList = [	localText.getText("TXT_KEY_TOPCIVS_HISTORIAN1", ()),
					#localText.getText("TXT_KEY_TOPCIVS_HISTORIAN2", ()),
					#localText.getText("TXT_KEY_TOPCIVS_HISTORIAN3", ()),
					#localText.getText("TXT_KEY_TOPCIVS_HISTORIAN4", ()),
					#localText.getText("TXT_KEY_TOPCIVS_HISTORIAN5", ()),
					#localText.getText("TXT_KEY_TOPCIVS_HISTORIAN6", ()),
					#localText.getText("TXT_KEY_TOPCIVS_HISTORIAN7", ()),
					#localText.getText("TXT_KEY_TOPCIVS_HISTORIAN8", ()),
					#localText.getText("TXT_KEY_TOPCIVS_HISTORIAN9", ()),
					#localText.getText("TXT_KEY_TOPCIVS_HISTORIAN10", ()),
					#localText.getText("TXT_KEY_TOPCIVS_HISTORIAN11", ())
					#]

		self.RankList = [
			localText.getText("TXT_KEY_TOPCIVS_RANK1", ()),
			localText.getText("TXT_KEY_TOPCIVS_RANK2", ()),
			localText.getText("TXT_KEY_TOPCIVS_RANK3", ()),
			localText.getText("TXT_KEY_TOPCIVS_RANK4", ()),
			localText.getText("TXT_KEY_TOPCIVS_RANK5", ()),
			localText.getText("TXT_KEY_TOPCIVS_RANK6", ()),
			localText.getText("TXT_KEY_TOPCIVS_RANK7", ()),
			localText.getText("TXT_KEY_TOPCIVS_RANK8", ())
		]

		#self.TypeList =    [	localText.getText("TXT_KEY_TOPCIVS_WEALTH", ()),
					#localText.getText("TXT_KEY_TOPCIVS_POWER", ()),
					#localText.getText("TXT_KEY_TOPCIVS_TECH", ()),
					#localText.getText("TXT_KEY_TOPCIVS_CULTURE", ()),
					#localText.getText("TXT_KEY_TOPCIVS_SIZE", ()),
					#]

		# Randomly choose what category and what historian will be used
		#szTypeRand = random.choice(self.TypeList)
		#szHistorianRand = random.choice(self.HistorianList)
		# <advc.038> Replacing the two lines above
		szTypeRand = self.TypeList[randIndex]
		szHistorianRand = self.HistorianList[gc.getGame().getSorenRandNum(len(self.HistorianList), "advc.038")]
		# </advc.038>
		# <!-- custom: The ranking is recorded whether or not the screen shows (printList: the replay rows the Timeline and SASPilot read), and SAS_UI_TOP_CIVS_ON decides only whether it shows, as the user asked rather than drawing it and closing it again (2026-11-19 validation run).
		# During AI Auto Play the info-popup switch skips it too (KI#203).
		# The advc.038 draws above stay first, so the game's random sequence is the same either way. (Claude code Opus 5.5) -->
		global g_bTopCivsOn, g_bDismissInfoPopupsOn
		if g_bTopCivsOn is None:
			g_bTopCivsOn = SASSessionTunables.SAS_UI_TOP_CIVS_ON > 0
			g_bDismissInfoPopupsOn = gc.getDefineINT("SAS_AIAUTOPLAY_DISMISS_INFO_POPUPS_ON") > 0
		self.szHistorian = szHistorianRand
		self.bDraw = g_bTopCivsOn and not (g_bDismissInfoPopupsOn and CyGame().getAIAutoPlay() > 0)
		if not self.bDraw:
			self.makeList(szTypeRand)
			return
		# Create screen

		self.screen = CyGInterfaceScreen( "CvTopCivs", CvScreenEnums.TOP_CIVS )

		self.screen.setSound("AS2D_TOP_CIVS")
		self.screen.showScreen(PopupStates.POPUPSTATE_QUEUED, False)
		self.screen.showWindowBackground( False )
		self.screen.setDimensions(self.screen.centerX(self.X_SCREEN), self.screen.centerY(self.Y_SCREEN), self.W_SCREEN, self.H_SCREEN)

		# Create panels

		# Main
		szMainPanel = "TopCivsMainPanel"
		self.screen.addPanel( szMainPanel, "", "", true, true, self.X_MAIN_PANEL, self.Y_MAIN_PANEL, self.W_MAIN_PANEL, self.H_MAIN_PANEL, PanelStyles.PANEL_STYLE_MAIN )

		# Top
		szHeaderPanel = "TopCivsHeaderPanel"
		szHeaderText = ""#gc.getLeaderHeadInfo(self.player.getLeaderType()).getDescription() + "\n-" + self.player.getCivilizationDescription(0) + "-"
		self.screen.addPanel( szHeaderPanel, szHeaderText, "", true, true, self.X_HEADER_PANEL, self.Y_HEADER_PANEL, self.W_HEADER_PANEL, self.H_HEADER_PANEL, PanelStyles.PANEL_STYLE_DAWNBOTTOM )

		# Bottom
		szTextPanel = "TopCivsTextPanel"
		szHeaderText = ""#self.Text_Title
		self.screen.addPanel( szTextPanel, szHeaderText, "", true, true, self.X_TEXT_PANEL, self.Y_TEXT_PANEL, self.W_TEXT_PANEL, self.H_TEXT_PANEL, PanelStyles.PANEL_STYLE_DAWNTOP )

		self.screen.setButtonGFC("Exit", self.EXIT_TEXT, "", self.X_EXIT,self.Y_EXIT, self.W_EXIT, self.H_EXIT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )

		# Title Text
		self.X_TITLE_TEXT = self.X_HEADER_PANEL + (self.W_HEADER_PANEL / 2)
		self.Y_TITLE_TEXT = self.Y_HEADER_PANEL + 15
		self.screen.setLabel("DawnTitle", "Background", self.TITLE_TEXT, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE_TEXT, self.Y_TITLE_TEXT, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		# 1 Text
		self.X_INFO_TEXT = self.X_TITLE_TEXT - 260#self.X_HEADER_PANEL + (self.W_HEADER_PANEL / 2)
		self.Y_INFO_TEXT = self.Y_TITLE_TEXT + 50
		self.W_INFO_TEXT = self.W_HEADER_PANEL
		self.H_INFO_TEXT = 70
		szText = localText.getText("TXT_KEY_TOPCIVS_TEXT1", (szHistorianRand, )) + u"\n" + localText.getText("TXT_KEY_TOPCIVS_TEXT2", (szTypeRand, ))
		self.screen.addMultilineText( "InfoText1", szText, self.X_INFO_TEXT, self.Y_INFO_TEXT, self.W_INFO_TEXT, self.H_INFO_TEXT, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

		self.makeList(szTypeRand)

	def makeList(self, szType):

		# Determine the list of top civs

		# Will eventually Store [iValue, iPlayerID]
		self.aiTopCivsValues = []

		# Loop through all players except the barbs
		# <!-- custom: Fixed texts read once before the loop rather than at each pass, which cost about 0.8 microseconds a lookup. See KI#128.10. (Claude code Opus 5.5) -->
		szTextTopcivsWealth = localText.getText("TXT_KEY_TOPCIVS_WEALTH", ())
		szTextTopcivsPower = localText.getText("TXT_KEY_TOPCIVS_POWER", ())
		szTextTopcivsTech = localText.getText("TXT_KEY_TOPCIVS_TECH", ())
		szTextTopcivsCulture = localText.getText("TXT_KEY_TOPCIVS_CULTURE", ())
		szTextTopcivsSize = localText.getText("TXT_KEY_TOPCIVS_SIZE", ())
		for iPlayerLoop in range(gc.getMAX_PLAYERS()-1):

			if (gc.getPlayer(iPlayerLoop).isAlive()):

				if (szType == szTextTopcivsWealth):
					# <advc.038> Replacing the two lines below
					gnp = gc.getTeam(gc.getPlayer(iPlayerLoop).getTeam()).AI_estimateYieldRate(iPlayerLoop, YieldTypes.YIELD_COMMERCE)
					self.aiTopCivsValues.append([gnp, iPlayerLoop])
					# </advc.038>
					#self.aiTopCivsValues.append([gc.getPlayer(iPlayerLoop).getGold(), iPlayerLoop])
					#print("Player %d Num Gold: %d" %(iPlayerLoop, gc.getPlayer(iPlayerLoop).getGold()))

				if (szType == szTextTopcivsPower):

					self.aiTopCivsValues.append([gc.getPlayer(iPlayerLoop).getPower(), iPlayerLoop])

				if (szType == szTextTopcivsTech):

					iPlayerNumTechs = 0
					iPlayerTechCosts = 0 # advc.038
					iNumTotalTechs = gc.getNumTechInfos()

					for iTechLoop in range(iNumTotalTechs):

						bPlayerHasTech = gc.getTeam(gc.getPlayer(iPlayerLoop).getTeam()).isHasTech(iTechLoop)

						if (bPlayerHasTech):
							iPlayerNumTechs = iPlayerNumTechs + 1
							# advc.038:
							iPlayerTechCosts += gc.getTechInfo(iTechLoop).getResearchCost()
					#self.aiTopCivsValues.append([iPlayerNumTechs, iPlayerLoop])
					#advc.038: Replacing the above
					self.aiTopCivsValues.append([iPlayerTechCosts, iPlayerLoop])
				if (szType == szTextTopcivsCulture):

					self.aiTopCivsValues.append([gc.getPlayer(iPlayerLoop).countTotalCulture(), iPlayerLoop])

				if (szType == szTextTopcivsSize):

					self.aiTopCivsValues.append([gc.getPlayer(iPlayerLoop).getTotalLand(), iPlayerLoop])

		# Lowest to Highest
		self.aiTopCivsValues.sort()
		# Switch it around - want the best to be first
		self.aiTopCivsValues.reverse()

		self.printList(szType)

	def printList(self, szType):

		# Print out the list
		# <advc.038> Confusing when all civs but 1 are ranked
		iRanks = 8
		if gc.getGame().countCivPlayersAlive() == iRanks + 1:
			iRanks = iRanks - 1
		# <!-- custom: Record what this screen lists, before the loop's early return, as replay messages visible only to the viewer's team, which the save keeps and the Timeline and SASPilot list.
		# One row per rank under a title row: a single row first ran past the Timeline's width, then lost the unknown civilizations' places, and a leader name alone can repeat or pair oddly with a civilization, so each met rank gives leader, civilization, player ID and team, and an unmet one the screen's own words (the user, 2026-11-19). (Claude code Opus 5.5) -->
		iViewer = CyGame().getActivePlayer()
		pViewerTeam = gc.getTeam(gc.getPlayer(iViewer).getTeam())
		ranks = []
		rankTexts = []
		# <!-- custom: Fixed texts read once before the loop rather than at each pass, which cost about 0.8 microseconds a lookup. See KI#128.10. (Claude code Opus 5.5) -->
		szTextTopcivsUnknown = localText.getText("TXT_KEY_TOPCIVS_UNKNOWN", ())
		for iRankLoop in range(min(iRanks, len(self.aiTopCivsValues))):
			iRankPlayer = self.aiTopCivsValues[iRankLoop][1]
			if iRankPlayer == iViewer or pViewerTeam.isHasMet(gc.getPlayer(iRankPlayer).getTeam()):
				ranks.append(iRankPlayer)
				# <!-- custom: The team always, not only when it has several members: the user found a row without it unclear, and a met civilization's team is no secret. (Claude code Opus 5.5) -->
				pRankPlayer = gc.getPlayer(iRankPlayer)
				rankTexts.append(localText.getText("TXT_KEY_SAS_TOPCIVS_TIMELINE_RANK", (iRankLoop + 1, pRankPlayer.getName(), pRankPlayer.getCivilizationShortDescription(0), iRankPlayer, pRankPlayer.getTeam())))
			else:
				ranks.append(-1)
				rankTexts.append(localText.getText("TXT_KEY_SAS_TOPCIVS_TIMELINE_RANK_UNKNOWN", (iRankLoop + 1, szTextTopcivsUnknown)))
		# <!-- custom: A g_lastShown global first kept the last ranking for SASPilot, but it outlived a load of an earlier save and a hot-seat change of viewer (Codex's review, 2026-11-19); the replay rows cover it. (Claude code Opus 5.5) -->
		# <!-- custom: Guarded: a DLL built before addSASTeamReplayMessage keeps the screen working without the record.
		# The Timeline lists newest first, so the ranks go in from the last to the first and the title last, to read top down in rank order.
		# A screen costs at most 9 rows (a title and 8 ranks, iRanks, even on SAS48), and it comes rarely: every TOP_CIVS_INTERVAL turns from turn 75 at Normal speed, only while the viewer has met half the teams or fewer, so a few times a game and mostly early.
		# The Timeline's "X is the first to discover Y" rows come far more often, so these add little by comparison, and SAS_INFO_UI_TIMELINE_TOP_CIVS_ON hides them for anyone who disagrees (the user, 2026-11-19). (Claude code Opus 5.5) -->
		if hasattr(gc.getGame(), "addSASTeamReplayMessage"):
			for i in range(len(rankTexts) - 1, -1, -1):
				gc.getGame().addSASTeamReplayMessage(iViewer, rankTexts[i])
			gc.getGame().addSASTeamReplayMessage(iViewer, localText.getText("TXT_KEY_SAS_TOPCIVS_TIMELINE_TITLE", (localText.getText("TXT_KEY_TOPCIVS_TITLE", ()), szType, self.szHistorian)))
		# <!-- custom: The SASGameRecord rows, pre-gated here on the cached level so a disabled record skips the call; the rows themselves are built in SASGameRecordActions. (Claude code Opus 5.5) -->
		if SASGameRecordConfig.getLogLevel() >= 1:
			SASGameRecordActions.logTopCivs(gc, self.szCategoryKey, self.szHistorian, self.aiTopCivsValues, len(ranks), ranks.count(-1), self.bDraw)
		if not self.bDraw:
			return
		# <!-- custom: Fixed texts read once before the loop rather than at each pass, which cost about 0.8 microseconds a lookup. See KI#128.10. (Claude code Opus 5.5) -->
		szTextTopcivsUnknown = localText.getText("TXT_KEY_TOPCIVS_UNKNOWN", ())
		for iRankLoop in range(iRanks): # </advc.038>

			if (iRankLoop > len(self.aiTopCivsValues)-1):
				return

			iPlayer = self.aiTopCivsValues[iRankLoop][1]
			iValue = self.aiTopCivsValues[iRankLoop][0]

			szPlayerName = gc.getPlayer(iPlayer).getNameKey()

			if (szPlayerName != ""):

				pActivePlayerTeam = gc.getTeam(gc.getPlayer(CyGame().getActivePlayer()).getTeam())
				iPlayerTeam = gc.getPlayer(iPlayer).getTeam()
				szCivText = ""

				# Does the Active player know this player exists?
				if (iPlayer == CyGame().getActivePlayer() or pActivePlayerTeam.isHasMet(iPlayerTeam)):
					szCivText = localText.getText("TXT_KEY_TOPCIVS_TEXT3", (szPlayerName, self.RankList[iRankLoop]))

				else:
					szCivText = szTextTopcivsUnknown

				szWidgetName = "Text" + str(iRankLoop)
				szWidgetDesc = "%d) %s" % (iRankLoop + 1, szCivText)
				iXLoc = self.X_RANK_TEXT
				iYLoc = self.Y_RANK_TEXT + (iRankLoop * self.H_RANK_TEXT)
				#self.screen.setText(szWidgetName, "Background", szWidgetDesc, CvUtil.FONT_LEFT_JUSTIFY, iXLoc, iYLoc, TEXT_Z, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				self.screen.addMultilineText( szWidgetName, unicode(szWidgetDesc), iXLoc, iYLoc, self.W_RANK_TEXT, self.H_RANK_TEXT, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

	def turnChecker(self, iTurnNum):

		# Check to see if this is a turn when the screen should pop up
		if (not CyGame().isNetworkMultiPlayer() and CyGame().getActivePlayer()>=0):
			# <advc.038>
			interval = SASCurrentDefines.getInt("TOP_CIVS_INTERVAL") # 50 in BtS
			minTurn = 75 # 2 in BtS
			speedAdjustPercent = gc.getGameSpeedInfo(gc.getGame().getGameSpeedType()).getGrowthPercent()
			interval = (interval * speedAdjustPercent) / 100
			minTurn = (minTurn * speedAdjustPercent) / 100
			otherTeamsMet = gc.getTeam(gc.getPlayer(CyGame().getActivePlayer()).getTeam()).getHasMetCivCount(true)
			otherTeamsTotal = gc.getGame().countCivTeamsAlive() - 1
			# Subtract 1 from turn num b/c the popup is triggered one turn before it appears. Nicer to have it show up on turn 50 than on turn 51
			if ((iTurnNum-1) % interval == 0 and iTurnNum+1 >= minTurn and gc.getPlayer(CyGame().getActivePlayer()).isAlive() and otherTeamsTotal > 0 and otherTeamsMet <= otherTeamsTotal / 2):
				# </advc.038>
				self.showScreen()

	#####################################################################################################################################

	def handleInput( self, inputClass ):
		self.screen = CyGInterfaceScreen( "CvTopCivs", CvScreenEnums.TOP_CIVS )		

		if ( inputClass.getFunctionName() == "Exit" and inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED ):
			self.screen.hideScreen()
			return 1
		elif ( inputClass.getData() == int(InputTypes.KB_RETURN) ):
			self.screen.hideScreen()
			return 1
		return 0

	def update(self, fDelta):
		return

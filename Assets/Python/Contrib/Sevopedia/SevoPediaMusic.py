# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#



from CvPythonExtensions import *
import CvUtil
import SevoScreenEnums

from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



class SevoPediaMusic:

	def __init__(self, main):
		self.top = main
		self.iMusic = -1
		self.MUSIC_PLAYER_SCREEN = "SevoPediaMusicPlayer"
		self.MUSIC_PLAYER_EXIT_ID = "SAS_MusicPlayerExit"
		self.SAS_isMusicPlayerOpen = False
		self.SAS_musicSoundId = None

		# Offset for the extra width of Music items list vs base width
		I_SAS_SEVOPEDIA_MUSIC_ITEMS_WIDTH = gc.getDefineINT("SAS_SEVOPEDIA_MUSIC_ITEMS_WIDTH")
		if I_SAS_SEVOPEDIA_MUSIC_ITEMS_WIDTH <= 0:
			I_SAS_SEVOPEDIA_MUSIC_ITEMS_WIDTH = self.top.W_ITEMS
		iExtraWidth = I_SAS_SEVOPEDIA_MUSIC_ITEMS_WIDTH - self.top.W_ITEMS

		self.X_HEADER = self.top.X_PEDIA_PAGE + iExtraWidth
		self.Y_HEADER = self.top.Y_PEDIA_PAGE
		self.W_HEADER = self.top.W_PEDIA_PAGE - iExtraWidth
		self.H_HEADER = 120

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_HEADER + 10
		self.Y_ICON = self.Y_HEADER + 10
		self.ICON_SIZE = 64

		self.X_TITLE = self.X_ICON + self.W_ICON + 10
		self.Y_TITLE = self.Y_HEADER + 12

		self.W_BUTTON = 64
		self.H_BUTTON = 64
		self.X_BUTTON = self.X_HEADER + self.W_HEADER - self.W_BUTTON - 10
		self.Y_BUTTON = self.Y_HEADER + (self.H_HEADER - self.H_BUTTON) / 2
		self.playButtonPath = ArtFileMgr.getInterfaceArtInfo("SAS_EMOJI_PLAY_BUTTON").getPath()

		self.X_TEXT = self.X_HEADER
		self.Y_TEXT = self.Y_HEADER + self.H_HEADER + 10
		self.W_TEXT = self.top.W_PEDIA_PAGE - iExtraWidth
		self.H_TEXT = self.top.B_PEDIA_PAGE - self.Y_TEXT



	def interfaceScreen(self, iMusic):
		self.iMusic = iMusic

		self.placeHeader()
		self.placeText()



	def placeHeader(self):
		screen = self.top.getScreen()
		iMusicType, iMusicId = self.top.SAS_unpackMusicKey(self.iMusic)
		info = self.getMusicInfo(self.iMusic)

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_HEADER, self.Y_HEADER, self.W_HEADER, self.H_HEADER, PanelStyles.PANEL_STYLE_BLUE50)

		szButton = ""
		if info:
			szButton = self.top.SAS_getMusicButton(self.iMusic)
		if szButton:
			if iMusicType == self.top.SAS_PEDIA_MUSIC_TYPE_TECH:
				screen.setImageButton(self.top.getNextWidgetName(), szButton, self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iMusicId, 1)
			elif iMusicType == self.top.SAS_PEDIA_MUSIC_TYPE_ERA:
				screen.setImageButton(self.top.getNextWidgetName(), szButton, self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_PEDIA_MAIN, SevoScreenEnums.PEDIA_ERA_CHART, -1)
			elif iMusicType == self.top.SAS_PEDIA_MUSIC_TYPE_LEADER:
				iLeaderId = self.top.SAS_getMusicLeaderId(self.iMusic)
				if iLeaderId != -1:
					screen.setImageButton(self.top.getNextWidgetName(), szButton, self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeaderId, 1)
				else:
					screen.addDDSGFC(self.top.getNextWidgetName(), szButton, self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)
			elif iMusicType == self.top.SAS_PEDIA_MUSIC_TYPE_CIV:
				iCivId = self.top.SAS_getMusicCivId(self.iMusic)
				if iCivId != -1:
					screen.setImageButton(self.top.getNextWidgetName(), szButton, self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCivId, 1)
				else:
					screen.addDDSGFC(self.top.getNextWidgetName(), szButton, self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)
			else:
				screen.addDDSGFC(self.top.getNextWidgetName(), szButton, self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)

		szTitleText = ""
		szTitleText = self.top.SAS_getMusicTitle(self.iMusic)
		szTitle = u"<font=4b>" + szTitleText.upper() + u"</font>"
		screen.setLabel(self.top.getNextWidgetName(), "Background", szTitle, CvUtil.FONT_LEFT_JUSTIFY, self.X_TITLE, self.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		if self.hasMusic(self.iMusic):
			screen.setImageButton(self.top.getNextWidgetName(), self.playButtonPath, self.X_BUTTON, self.Y_BUTTON, self.W_BUTTON, self.H_BUTTON, WidgetTypes.WIDGET_PYTHON, self.top.SAS_PEDIA_PYTHON_MUSIC_PLAY, self.iMusic)



	def placeText(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, "", "", True, True, self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_BLUE50)
		iMusicType, iMusicId = self.top.SAS_unpackMusicKey(self.iMusic)
		info = self.getMusicInfo(self.iMusic)
		szText = ""
		if info and iMusicType == self.top.SAS_PEDIA_MUSIC_TYPE_TECH:
			try:
				szText = info.getQuote()
			except:
				szText = ""
			if szText and szText.startswith("TXT_KEY_"):
				szText = ""
			if not szText:
				try:
					szText = info.getCivilopedia()
				except:
					szText = ""
			if szText and szText.startswith("TXT_KEY_"):
				szText = ""
		elif iMusicType == self.top.SAS_PEDIA_MUSIC_TYPE_ERA:
			szEraText = u""
			if info:
				szEraText = info.getDescription() + u" " + localText.getText("TXT_KEY_PEDIA_ERA", ())

			szExtra = u""
			if (self.top.SAS_musicEraTracks is not None) and (iMusicId >= 0) and (iMusicId < len(self.top.SAS_musicEraTracks)):
				_, iTrackId, iTrack = self.top.SAS_musicEraTracks[iMusicId]
				szTrackName = u""
				try:
					szTrackName = info.getSoundtrackScriptName(iTrack)
				except:
					szTrackName = u""
				szExtra = u"\nTrack %02d" % (iTrack + 1)
				if szTrackName:
					szExtra += u" - " + unicode(szTrackName)
				if iTrackId != -1:
					szExtra += u"\nTrack ID: %d" % iTrackId

			szText = szEraText + szExtra
		elif iMusicType == self.top.SAS_PEDIA_MUSIC_TYPE_LEADER:
			szTitleText = self.top.SAS_getMusicTitle(self.iMusic)
			iTrackId = self.top.SAS_getMusicSoundId(self.iMusic)
			if iTrackId != -1:
				szText = szTitleText + u"\nTrack ID: %d" % iTrackId
			else:
				szText = szTitleText
		elif iMusicType == self.top.SAS_PEDIA_MUSIC_TYPE_CIV:
			szTitleText = self.top.SAS_getMusicTitle(self.iMusic)
			szScript = self.top.SAS_getMusicSoundScript(self.iMusic)
			iSoundId = self.top.SAS_getMusicSoundId(self.iMusic)
			szNote = localText.getText("TXT_KEY_PEDIA_SAS_MUSIC_CIV_VARIANT_NOTE", ())
			if iSoundId != -1:
				szText = szTitleText + u"\nSound ID: %d" % iSoundId
			elif szScript:
				szText = szTitleText + u"\n" + szScript
			else:
				szText = szTitleText
			if szNote:
				szText = szText + u"\n\n" + szNote
		elif iMusicType == self.top.SAS_PEDIA_MUSIC_TYPE_SCRIPT:
			szTitleText = self.top.SAS_getMusicTitle(self.iMusic)
			szScript = self.top.SAS_getMusicSoundScript(self.iMusic)
			szSoundId = ""
			iMusicType, iMusicId = self.top.SAS_unpackMusicKey(self.iMusic)
			if (self.top.SAS_musicScriptTracks is not None) and (iMusicId >= 0) and (iMusicId < len(self.top.SAS_musicScriptTracks)):
				_, szSoundId, _ = self.top.SAS_musicScriptTracks[iMusicId]
			if szSoundId:
				if szTitleText == szSoundId:
					szText = szTitleText + u"\n" + szScript
				else:
					szText = szTitleText + u"\n" + szSoundId + u"\n" + szScript
			else:
				szText = szTitleText + u"\n" + szScript
		elif iMusicType == self.top.SAS_PEDIA_MUSIC_TYPE_SCRIPT_3D:
			szTitleText = self.top.SAS_getMusicTitle(self.iMusic)
			szScript = self.top.SAS_getMusicSoundScript(self.iMusic)
			szSoundId = ""
			iMusicType, iMusicId = self.top.SAS_unpackMusicKey(self.iMusic)
			if (self.top.SAS_musicScript3DTracks is not None) and (iMusicId >= 0) and (iMusicId < len(self.top.SAS_musicScript3DTracks)):
				_, szSoundId, _ = self.top.SAS_musicScript3DTracks[iMusicId]
			if szSoundId:
				if szTitleText == szSoundId:
					szText = szTitleText + u"\n" + szScript
				else:
					szText = szTitleText + u"\n" + szSoundId + u"\n" + szScript
			else:
				szText = szTitleText + u"\n" + szScript
		screen.attachMultilineText(panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def playMusic(self, iMusic):
		game = CyGame()
		if game.isNetworkMultiPlayer() or game.isPitbossHost():
			return

		if not self.hasMusic(iMusic):
			return
		self.showMusicPlayer(iMusic)



	def showMusicPlayer(self, iMusic):
		iMusicType, iMusicId = self.top.SAS_unpackMusicKey(iMusic)
		info = self.getMusicInfo(iMusic)
		if (iMusicType != self.top.SAS_PEDIA_MUSIC_TYPE_SCRIPT) and (iMusicType != self.top.SAS_PEDIA_MUSIC_TYPE_SCRIPT_3D) and (not info):
			return
		szSoundScript = self.top.SAS_getMusicSoundScript(iMusic)
		iSoundId = self.top.SAS_getMusicSoundId(iMusic)
		if szSoundScript == "NONE":
			szSoundScript = ""

		screen = CyGInterfaceScreen(self.MUSIC_PLAYER_SCREEN, SevoScreenEnums.PEDIA_MUSIC)

		# <!-- custom: (ChatGPT-5.2 Thinking) -->
		try:
			screen.enableWorldSounds(True)
		except:
			pass
		try:
			screen.setScreenGroup(1)
		except:
			pass

		self.SAS_isMusicPlayerOpen = True

		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
		screen.setRenderInterfaceOnly(True)
		screen.enableWorldSounds(False)
		screen.addPanel("MusicPlayerBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN)

		iScreenW = screen.getXResolution()
		iScreenH = screen.getYResolution()
		iImageW = iScreenW
		iImageH = iScreenW * 2 / 3
		if iImageH > iScreenH:
			iImageH = iScreenH
			iImageW = iImageH * 3 / 2
		iImageX = (iScreenW - iImageW) / 2
		iImageY = (iScreenH - iImageH) / 2

		szTitleText = self.top.SAS_getMusicTitle(iMusic)
		screen.setLabel("MusicPlayerTitle", "Background", u"<font=4b>" + szTitleText.upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, iScreenW / 2, 8, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iEra = self.top.SAS_getMusicEra(iMusic)
		szImagePath = ""
		if iEra != -1:
			szImagePath = gc.getEraInfo(iEra).getButton()
		if szImagePath:
			screen.setImageButton("MusicPlayerImage", szImagePath, iImageX, iImageY, iImageW, iImageH, WidgetTypes.WIDGET_PEDIA_MAIN, SevoScreenEnums.PEDIA_ERA_CHART, -1)

		if szSoundScript or (iSoundId != -1):
			self.SAS_musicSoundId = None
			self.SAS_is3DSound = False
			try:
				if iSoundId != -1:
					if self.top.SAS_isMusicSound3D(iMusic):
						self.SAS_musicSoundId = CyAudioGame().Play3DSoundWithId(iSoundId, 0, 0, 0)
						self.SAS_is3DSound = True
					else:
						self.SAS_musicSoundId = CyAudioGame().Play2DSoundWithId(iSoundId)
				elif szSoundScript.startswith("AS3D_"):
					# 3D scripts need Play3DSound
					self.SAS_musicSoundId = CyAudioGame().Play3DSound(szSoundScript, 0, 0, 0)
					self.SAS_is3DSound = True
				else:
					self.SAS_musicSoundId = CyAudioGame().Play2DSound(szSoundScript)
			except:
				self.SAS_musicSoundId = None
			if self.SAS_musicSoundId is None or self.SAS_musicSoundId == -1:
				if szSoundScript:
					CyInterface().playGeneralSound(szSoundScript)
				self.SAS_musicSoundId = None

		screen.setButtonGFC(self.MUSIC_PLAYER_EXIT_ID, localText.getText("TXT_KEY_MAIN_MENU_OK", ()), "", iScreenW / 2 - 50, iScreenH - 42, 100, 30, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)

		# <!-- custom: (ChatGPT-5.2 Thinking) -->
		try:
			screen.setEscapeKey(self.MUSIC_PLAYER_EXIT_ID)
		except:
			pass
		try:
			screen.setReturnKey(self.MUSIC_PLAYER_EXIT_ID)
		except:
			pass



	def closeMusicPlayer(self):
		if not self.SAS_isMusicPlayerOpen:
			return

		if self.SAS_musicSoundId is not None and self.SAS_musicSoundId != -1:
			try:
				if getattr(self, 'SAS_is3DSound', False):
					CyAudioGame().Destroy3DSound(self.SAS_musicSoundId)
				else:
					CyAudioGame().Destroy2DSound(self.SAS_musicSoundId)
			except:
				try:
					CyInterface().stop2DSound()
				except:
					pass
			self.SAS_musicSoundId = None
			self.SAS_is3DSound = False
		elif self.SAS_musicSoundId is not None:
			try:
				CyInterface().stop2DSound()
			except:
				pass
			self.SAS_musicSoundId = None
			self.SAS_is3DSound = False

		screen = CyGInterfaceScreen(self.MUSIC_PLAYER_SCREEN, SevoScreenEnums.PEDIA_MUSIC)
		screen.hideScreen()
		self.SAS_isMusicPlayerOpen = False

		self.top.pediaJump(SevoScreenEnums.PEDIA_MUSIC, self.iMusic, False, False)



	def isMusicPlayerOpen(self):
		return self.SAS_isMusicPlayerOpen



	def getMusicInfo(self, iPacked):
		return self.top.getMusicInfo(iPacked)



	def hasMusic(self, iPacked):
		szSound = self.top.SAS_getMusicSoundScript(iPacked)
		if szSound and (szSound != "NONE"):
			return True
		return self.top.SAS_getMusicSoundId(iPacked) != -1



	def handleInput(self, inputClass):
		return 0

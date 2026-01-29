# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)



from CvPythonExtensions import *
import CvUtil

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



class SevoPediaMediaPlayer:

	def __init__(self, screenId, screenEnum, exitId, clickPrefix):
		self.screenId = screenId
		self.screenEnum = screenEnum
		self.exitId = exitId
		self.replayId = clickPrefix + "Replay"
		self.prevId = clickPrefix + "Prev"
		self.nextId = clickPrefix + "Next"
		self.clickPrefix = clickPrefix
		self.isOpen = False
		self.soundId = None
		self.is3DSound = False
		self.exitButtonPath = ArtFileMgr.getInterfaceArtInfo("SAS_EMOJI_EJECT_BUTTON").getPath()
		self.replayButtonPath = ArtFileMgr.getInterfaceArtInfo("SAS_EMOJI_PLAY_BUTTON").getPath()
		self.prevButtonPath = ArtFileMgr.getInterfaceArtInfo("SAS_EMOJI_LAST_TRACK_BUTTON").getPath()
		self.nextButtonPath = ArtFileMgr.getInterfaceArtInfo("SAS_EMOJI_NEXT_TRACK_BUTTON").getPath()
		self.replayCallback = None
		self.prevCallback = None
		self.nextCallback = None
		self.screen = None



	def openScreen(self):
		screen = CyGInterfaceScreen(self.screenId, self.screenEnum)

		# <!-- custom: (ChatGPT-5.2 Thinking) -->
		try:
			screen.enableWorldSounds(True)
		except:
			pass
		try:
			screen.setScreenGroup(1)
		except:
			pass

		self.isOpen = True
		self.screen = screen

		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
		screen.setRenderInterfaceOnly(True)
		screen.enableWorldSounds(False)
		screen.addPanel(self.clickPrefix + "BG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN)
		return screen



	def setupLayout(self, screen, szTitleText):
		iScreenW = screen.getXResolution()
		iScreenH = screen.getYResolution()
		iMediaW = iScreenW
		iMediaH = iScreenW * 2 / 3
		if iMediaH > iScreenH:
			iMediaH = iScreenH
			iMediaW = iMediaH * 3 / 2
		iMediaX = (iScreenW - iMediaW) / 2
		iMediaY = (iScreenH - iMediaH) / 2

		screen.setLabel(self.clickPrefix + "Title", "Background", u"<font=4b>" + szTitleText.upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, iScreenW / 2, 8, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		return (iScreenW, iScreenH, iMediaX, iMediaY, iMediaW, iMediaH)



	def placeExitButton(self, screen, iScreenW, iScreenH):
		iSize, iGap, iExitX, iBaseY = self._getTransportLayout(iScreenW, iScreenH)
		screen.setImageButton(self.exitId, self.exitButtonPath, iExitX, iBaseY, iSize, iSize, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# <!-- custom: (ChatGPT-5.2 Thinking) -->
		try:
			screen.setEscapeKey(self.exitId)
		except:
			pass
		try:
			screen.setReturnKey(self.exitId)
		except:
			pass



	# <!-- custom: useful to replay files with variants such as _ORDER or _SELECT civilization sounds that play a different variant on replay (e.g. "Yes", "Agreed", "Right Away" (imaginary examples)), or for convenience so we don't exit the screen to replay. Added with the very nice help of GPT-5.2-Codex thanks. -->
	def placeReplayButton(self, screen, iScreenW, iScreenH):
		iSize, iGap, iExitX, iBaseY = self._getTransportLayout(iScreenW, iScreenH)
		iReplayX = iExitX - iGap - iSize
		screen.setImageButton(self.replayId, self.replayButtonPath, iReplayX, iBaseY, iSize, iSize, WidgetTypes.WIDGET_GENERAL, -1, -1)



	def placePrevNextButtons(self, screen, iScreenW, iScreenH):
		iSize, iGap, iExitX, iBaseY = self._getTransportLayout(iScreenW, iScreenH)
		iReplayX = iExitX - iGap - iSize
		iPrevX = iReplayX - iGap - iSize
		iNextX = iExitX + iGap + iSize
		screen.setImageButton(self.prevId, self.prevButtonPath, iPrevX, iBaseY, iSize, iSize, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setImageButton(self.nextId, self.nextButtonPath, iNextX, iBaseY, iSize, iSize, WidgetTypes.WIDGET_GENERAL, -1, -1)



	def _getTransportLayout(self, iScreenW, iScreenH):
		iSize = 64
		iGap = 8
		iExitX = iScreenW / 2 - iSize / 2
		iBaseY = iScreenH - 74
		return (iSize, iGap, iExitX, iBaseY)



	def setReplayCallback(self, replayCallback):
		self.replayCallback = replayCallback



	def setPrevCallback(self, prevCallback):
		self.prevCallback = prevCallback



	def setNextCallback(self, nextCallback):
		self.nextCallback = nextCallback



	def playSound(self, szSoundScript, iSoundId, bForce3D):
		self.soundId = None
		self.is3DSound = False

		if (not szSoundScript) and iSoundId == -1:
			return

		try:
			if iSoundId != -1:
				if bForce3D:
					self.soundId = CyAudioGame().Play3DSoundWithId(iSoundId, 0, 0, 0)
					self.is3DSound = True
				else:
					self.soundId = CyAudioGame().Play2DSoundWithId(iSoundId)
			else:
				if szSoundScript.startswith("AS3D_"):
					# 3D scripts need Play3DSound
					self.soundId = CyAudioGame().Play3DSound(szSoundScript, 0, 0, 0)
					self.is3DSound = True
				else:
					self.soundId = CyAudioGame().Play2DSound(szSoundScript)
		except:
			self.soundId = None

		if self.soundId is None or self.soundId == -1:
			if szSoundScript:
				CyInterface().playGeneralSound(szSoundScript)
			self.soundId = None
			self.is3DSound = False



	def stopSound(self):
		if self.soundId is not None and self.soundId != -1:
			try:
				if self.is3DSound:
					CyAudioGame().Destroy3DSound(self.soundId)
				else:
					CyAudioGame().Destroy2DSound(self.soundId)
			except:
				try:
					CyInterface().stop2DSound()
				except:
					pass
			self.soundId = None
			self.is3DSound = False
		elif self.soundId is not None:
			try:
				CyInterface().stop2DSound()
			except:
				pass
			self.soundId = None
			self.is3DSound = False



	def closeScreen(self):
		screen = CyGInterfaceScreen(self.screenId, self.screenEnum)
		screen.hideScreen()
		self.isOpen = False
		self.screen = None



	def getScreen(self):
		return self.screen



	def handleInput(self, inputClass, closeCallback, bCloseOnMovieDone):
		if not self.isOpen:
			return False

		# <!-- custom: While the full-screen music player overlay is open, consume input here so
		# Civ4 does not treat ESC/ENTER as "close civilopedia" and bounce to the main menu. (ChatGPT-5.2 Thinking) -->
		iNotify = inputClass.getNotifyCode()

		if bCloseOnMovieDone and iNotify == NotifyCode.NOTIFY_MOVIE_DONE:
			closeCallback()
			return True

		if iNotify == NotifyCode.NOTIFY_CHARACTER:
			iKey = inputClass.getData()
			if iKey == int(InputTypes.KB_ESCAPE) or iKey == int(InputTypes.KB_RETURN):
				closeCallback()
				return True
			# Some keyboards send a distinct numpad enter key code.
			try:
				if iKey == int(InputTypes.KB_NUMPADENTER):
					closeCallback()
					return True
			except:
				pass

		if iNotify == NotifyCode.NOTIFY_CLICKED:
			szName = inputClass.getFunctionName()
			if szName == self.replayId:
				if self.replayCallback is not None:
					self.replayCallback()
				return True
			if szName == self.prevId:
				if self.prevCallback is not None:
					self.prevCallback()
				return True
			if szName == self.nextId:
				if self.nextCallback is not None:
					self.nextCallback()
				return True
			# Exit button, or click anywhere on the overlay (image/title/background or movie/nif/dds/title/background) to close.
			if szName == self.exitId or szName.startswith(self.clickPrefix):
				closeCallback()
				return True

		return True

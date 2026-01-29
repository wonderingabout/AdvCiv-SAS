# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)



from CvPythonExtensions import *
import CvUtil

gc = CyGlobalContext()
localText = CyTranslator()



class SevoPediaMediaPlayer:

	def __init__(self, screenId, screenEnum, exitId, clickPrefix):
		self.screenId = screenId
		self.screenEnum = screenEnum
		self.exitId = exitId
		self.clickPrefix = clickPrefix
		self.isOpen = False
		self.soundId = None
		self.is3DSound = False



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
		screen.setButtonGFC(self.exitId, localText.getText("TXT_KEY_MAIN_MENU_OK", ()), "", iScreenW / 2 - 50, iScreenH - 42, 100, 30, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)

		# <!-- custom: (ChatGPT-5.2 Thinking) -->
		try:
			screen.setEscapeKey(self.exitId)
		except:
			pass
		try:
			screen.setReturnKey(self.exitId)
		except:
			pass



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
			# Exit button, or click anywhere on the overlay (image/title/background or movie/nif/dds/title/background) to close.
			if szName == self.exitId or szName.startswith(self.clickPrefix):
				closeCallback()
				return True

		return True

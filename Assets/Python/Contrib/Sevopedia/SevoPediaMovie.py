# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# <!-- custom: based on the Middle-earth mod's Platypedia's Movies category and adjusted for AdvCiv-SAS then enhanced with the help of GPT-5.2-Codex and Claude code Opus 4.5 thanks a lot. (GPT-5.2-Codex (summarized)) -->
#



from CvPythonExtensions import *
import CvUtil
import SevoScreenEnums

from _sevopedia_helpers import *

gc = CyGlobalContext()
localText = CyTranslator()
UserProfile = CyUserProfile()



class SevoPediaMovie:

	def __init__(self, main):
		self.top = main
		self.iMovie = -1
		self.MOVIE_PLAYER_SCREEN = "SevoPediaMoviePlayer"
		self.MOVIE_PLAYER_EXIT_ID = "SAS_MoviePlayerExit"
		self.SAS_savedNoMovies = None
		self.SAS_isMoviePlayerOpen = False
		self.SAS_movieSoundId = None

		self.X_HEADER = self.top.X_PEDIA_PAGE
		self.Y_HEADER = self.top.Y_PEDIA_PAGE
		self.W_HEADER = self.top.W_PEDIA_PAGE
		self.H_HEADER = 120

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_HEADER + 10
		self.Y_ICON = self.Y_HEADER + 10
		self.ICON_SIZE = 64

		self.X_TITLE = self.X_ICON + self.W_ICON + 10
		self.Y_TITLE = self.Y_HEADER + 12

		# <!-- custom: changed from text button to image button. (Claude Opus 4.5) -->
		self.W_BUTTON = 64
		self.H_BUTTON = 64
		self.X_BUTTON = self.X_HEADER + self.W_HEADER - self.W_BUTTON - 10
		self.Y_BUTTON = self.Y_HEADER + (self.H_HEADER - self.H_BUTTON) / 2

		self.X_TEXT = self.X_HEADER
		self.Y_TEXT = self.Y_HEADER + self.H_HEADER + 10
		self.W_TEXT = self.top.W_PEDIA_PAGE
		self.H_TEXT = self.top.B_PEDIA_PAGE - self.Y_TEXT



	def interfaceScreen(self, iVictory):
		self.iMovie = iVictory

		self.placeHeader()
		self.placeText()



	def placeHeader(self):
		screen = self.top.getScreen()
		iMovieType, iMovieId = self.top.SAS_unpackMovieKey(self.iMovie)
		info = self.getMovieInfo(iMovieType, iMovieId)

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_HEADER, self.Y_HEADER, self.W_HEADER, self.H_HEADER, PanelStyles.PANEL_STYLE_BLUE50)

		szButton = ""
		if info:
			szButton = info.getButton()
		if szButton:
			widgetType, widgetData1, widgetData2 = self.getPediaJumpWidget(iMovieType, iMovieId)
			if widgetType == WidgetTypes.WIDGET_GENERAL:
				screen.addDDSGFC(self.top.getNextWidgetName(), szButton, self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)
			else:
				screen.setImageButton(self.top.getNextWidgetName(), szButton, self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, widgetType, widgetData1, widgetData2)

		szTitleText = ""
		if info:
			szTitleText = info.getDescription()
		szTitle = u"<font=4b>" + szTitleText.upper() + u"</font>"
		screen.setLabel(self.top.getNextWidgetName(), "Background", szTitle, CvUtil.FONT_LEFT_JUSTIFY, self.X_TITLE, self.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		if self.hasMovie(iMovieType, iMovieId):
			# <!-- custom: use image button with play emoji instead of text button. (Claude Opus 4.5) -->
			buttonPathTxtKey = "TXT_KEY_IMAGE_AS_BUTTON_PLAY_BUTTON_BUTTON_PATH"
			buttonPath = str(localText.getText(buttonPathTxtKey, ()))
			screen.setImageButton(self.top.getNextWidgetName(), buttonPath, self.X_BUTTON, self.Y_BUTTON, self.W_BUTTON, self.H_BUTTON, WidgetTypes.WIDGET_PYTHON, self.top.SAS_PEDIA_PYTHON_MOVIE_PLAY, self.iMovie)



	def placeText(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, "", "", True, True, self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_BLUE50)
		iMovieType, iMovieId = self.top.SAS_unpackMovieKey(self.iMovie)
		info = self.getMovieInfo(iMovieType, iMovieId)
		szText = ""
		if info:
			try:
				szText = info.getCivilopedia()
			except:
				szText = ""
		if szText and szText.startswith("TXT_KEY_"):
			szText = ""
		screen.attachMultilineText(panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def playMovie(self, iVictory):
		game = CyGame()
		if game.isNetworkMultiPlayer() or game.isPitbossHost():
			return

		iMovieType, iMovieId = self.top.SAS_unpackMovieKey(iVictory)
		moviePayload = self.getMoviePayload(iMovieType, iMovieId)
		if moviePayload is None:
			return
		self.showMoviePlayer(iMovieType, iMovieId, moviePayload)



	def showMoviePlayer(self, iMovieType, iMovieId, moviePayload):
		szMovieFile, szMovieKind, szSoundScript = moviePayload

		self.SAS_savedNoMovies = CyUserProfile().getGraphicOption(GraphicOptionTypes.GRAPHICOPTION_NO_MOVIES)
		CyUserProfile().setGraphicOption(GraphicOptionTypes.GRAPHICOPTION_NO_MOVIES, False)

		screen = CyGInterfaceScreen(self.MOVIE_PLAYER_SCREEN, SevoScreenEnums.PEDIA_MOVIES)

		# <!-- custom: (ChatGPT-5.2 Thinking) -->
		try:
			screen.enableWorldSounds(True)
		except:
			pass
		try:
			screen.setScreenGroup(1)
		except:
			pass

		self.SAS_isMoviePlayerOpen = True

		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
		screen.setRenderInterfaceOnly(True)
		screen.enableWorldSounds(False)
		screen.addPanel("MoviePlayerBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN)

		iScreenW = screen.getXResolution()
		iScreenH = screen.getYResolution()
		iMovieW = iScreenW
		iMovieH = iScreenW * 2 / 3
		if iMovieH > iScreenH:
			iMovieH = iScreenH
			iMovieW = iMovieH * 3 / 2
		iMovieX = (iScreenW - iMovieW) / 2
		iMovieY = (iScreenH - iMovieH) / 2

		szTitleText = self.getMovieTitle(iMovieType, iMovieId)
		screen.setLabel("MoviePlayerTitle", "Background", u"<font=4b>" + szTitleText.upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, iScreenW / 2, 8, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		if szMovieKind == "nif":
			screen.addReligionMovieWidgetGFC("MoviePlayerMovie", szMovieFile, iMovieX, iMovieY, iMovieW, iMovieH, WidgetTypes.WIDGET_GENERAL, -1, -1)
		elif szMovieKind == "dds":
			screen.addDDSGFC("MoviePlayerMovie", szMovieFile, iMovieX, iMovieY, iMovieW, iMovieH, WidgetTypes.WIDGET_GENERAL, -1, -1)
		else:
			screen.playMovie(szMovieFile, -1, -1, -1, -1, 0)

		# <!-- custom: Play audio using Play2DSound/Destroy2DSound approach. This works fine for both
		# starting audio on open and stopping it on exit. An alternative cleaner approach exists in
		# CvEraMovieScreen.py using screen.setSound() before showScreen(), but we couldn't make it work
		# in our context, so we stick with this approach. Credit: GPT-5.2-Codex, Claude Opus 4.5. -->
		if szSoundScript:
			self.SAS_movieSoundId = None
			try:
				self.SAS_movieSoundId = CyAudioGame().Play2DSound(szSoundScript)
			except:
				self.SAS_movieSoundId = None
			if self.SAS_movieSoundId is None or self.SAS_movieSoundId == -1:
				CyInterface().playGeneralSound(szSoundScript)
				self.SAS_movieSoundId = None

		screen.setButtonGFC(self.MOVIE_PLAYER_EXIT_ID, localText.getText("TXT_KEY_MAIN_MENU_OK", ()), "", iScreenW / 2 - 50, iScreenH - 42, 100, 30, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)

		# <!-- custom: (ChatGPT-5.2 Thinking) -->
		try:
			screen.setEscapeKey(self.MOVIE_PLAYER_EXIT_ID)
		except:
			pass
		try:
			screen.setReturnKey(self.MOVIE_PLAYER_EXIT_ID)
		except:
			pass



	def closeMoviePlayer(self):
		if not self.SAS_isMoviePlayerOpen:
			return

		if self.SAS_savedNoMovies is not None:
			CyUserProfile().setGraphicOption(GraphicOptionTypes.GRAPHICOPTION_NO_MOVIES, self.SAS_savedNoMovies)

		# <!-- custom: try to stop the specific 2D sound via Destroy2DSound(handle); if that fails, fall back to
		# CyInterface().stop2DSound() as a global 2D stop for stubborn handles. Credit: CIV4BUG API docs.
		# (GPT-5.2-Codex (summarized)) -->
		if self.SAS_movieSoundId is not None and self.SAS_movieSoundId != -1:
			try:
				CyAudioGame().Destroy2DSound(self.SAS_movieSoundId)
			except:
				try:
					CyInterface().stop2DSound()
				except:
					pass
			self.SAS_movieSoundId = None
		elif self.SAS_movieSoundId is not None:
			try:
				CyInterface().stop2DSound()
			except:
				pass
			self.SAS_movieSoundId = None

		screen = CyGInterfaceScreen(self.MOVIE_PLAYER_SCREEN, SevoScreenEnums.PEDIA_MOVIES)
		screen.hideScreen()
		self.SAS_isMoviePlayerOpen = False

		self.top.pediaJump(SevoScreenEnums.PEDIA_MOVIES, self.iMovie, False, False)



	def isMoviePlayerOpen(self):
		return self.SAS_isMoviePlayerOpen



	def getMovieInfo(self, iMovieType, iMovieId):
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_VICTORY:
			return gc.getVictoryInfo(iMovieId)
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_WONDER:
			return gc.getBuildingInfo(iMovieId)
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_PROJECT:
			return gc.getProjectInfo(iMovieId)
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_RELIGION:
			return gc.getReligionInfo(iMovieId)
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_ERA:
			return gc.getEraInfo(iMovieId)
		return None

	def getMoviePayload(self, iMovieType, iMovieId):
		if not self.hasMovie(iMovieType, iMovieId):
			return None

		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_VICTORY:
			szArtDef = gc.getVictoryInfo(iMovieId).getMovie()
			if not szArtDef:
				return None
			szMovie = CyArtFileMgr().getMovieArtInfo(szArtDef).getPath()
			if not szMovie:
				return None
			return (szMovie, "movie", None)

		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_WONDER:
			szMovie = gc.getBuildingInfo(iMovieId).getMovie()
			if not szMovie:
				return None
			if szMovie:
				if (szMovie.find(".") == -1) or (szMovie.find("ART_DEF") > -1):
					szMovie = CyArtFileMgr().getMovieArtInfo(szMovie).getPath()
			if not szMovie:
				return None
			szMovieKind = "movie"
			if szMovie.find(".dds") > -1:
				szMovieKind = "dds"
			return (szMovie, szMovieKind, None)

		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_PROJECT:
			szArtDef = gc.getProjectInfo(iMovieId).getMovieArtDef()
			if not szArtDef:
				return None
			szMovie = CyArtFileMgr().getMovieArtInfo(szArtDef).getPath()
			if not szMovie:
				return None
			return (szMovie, "movie", None)

		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_RELIGION:
			szMovieFile = gc.getReligionInfo(iMovieId).getMovieFile()
			if not szMovieFile:
				return None
			szMovieKind = "movie"
			if szMovieFile.find(".nif") > -1:
				szMovieKind = "nif"
			szSoundScript = ""
			try:
				szSoundScript = gc.getReligionInfo(iMovieId).getMovieSound()
			except:
				szSoundScript = ""
			if szSoundScript == "NONE":
				szSoundScript = ""
			return (szMovieFile, szMovieKind, szSoundScript)

		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_ERA:
			szMovieFile = gc.getEraInfo(iMovieId).getButton()
			if not szMovieFile:
				return None
			return (szMovieFile, "dds", "AS2D_NEW_ERA")

		return None

	def getMovieTitle(self, iMovieType, iMovieId):
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_ERA:
			info = self.getMovieInfo(iMovieType, iMovieId)
			if info:
				return info.getDescription() + " " + localText.getText("TXT_KEY_PEDIA_ERA", ())
			return u""

		info = self.getMovieInfo(iMovieType, iMovieId)
		if info:
			return info.getDescription()
		return u""

	def hasMovie(self, iMovieType, iMovieId):
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_VICTORY:
			info = gc.getVictoryInfo(iMovieId)
			return (info is not None) and bool(info.getMovie())
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_WONDER:
			info = gc.getBuildingInfo(iMovieId)
			return (info is not None) and bool(info.getMovie())
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_PROJECT:
			info = gc.getProjectInfo(iMovieId)
			return (info is not None) and bool(info.getMovieArtDef())
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_RELIGION:
			info = gc.getReligionInfo(iMovieId)
			return (info is not None) and bool(info.getMovieFile())
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_ERA:
			return bool(gc.getEraInfo(iMovieId).getButton())
		return False

	def getPediaJumpWidget(self, iMovieType, iMovieId):
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_WONDER:
			return (WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iMovieId, 1)
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_PROJECT:
			return (WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, iMovieId, 1)
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_RELIGION:
			return (WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iMovieId, 1)
		# <!-- custom: this successfully works: redirects to Sevopedia Eras Chart category, that has no item and only a chart (like Promotions Tree for example). Done with the very nice help of Claude code Sonnet 4.5 thanks a lot! -->
		if iMovieType == self.top.SAS_PEDIA_MOVIE_TYPE_ERA:
			return (WidgetTypes.WIDGET_PEDIA_MAIN, SevoScreenEnums.PEDIA_ERA_CHART, -1)
		return (WidgetTypes.WIDGET_GENERAL, -1, -1)

	def handleInput (self, inputClass):
		return 0

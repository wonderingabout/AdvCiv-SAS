## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
from CvPythonExtensions import *
import PyHelpers
import CvUtil
import ScreenInput
import CvScreenEnums
import SASTextScale

PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvSpaceShipScreen:
	"Spaceship Screen"
	def interfaceScreen (self, iFinishedProject):

		#create screen
		screen = CyGInterfaceScreen( "SpaceShipScreen", CvScreenEnums.SPACE_SHIP_SCREEN)

		#setup panel
		self.windowWidth = screen.getXResolution()
		self.windowHeight = screen.getYResolution()
		screen.setDimensions(0, 0, self.windowWidth, self.windowHeight)
		# <!-- custom: widen spaceship panel/button areas so upscaled label/title text fits without clipping (e.g., Completed/Type/Zoom/Add/Launch/Exit labels). (GPT-5.3-Codex) -->
		# <!-- custom: The parts panel stayed 460 x 768 at any resolution, so its upscaled labels were cramped 15 pixels apart; it now grows with the window, keeping those sizes as its minimum. (Claude code Opus 5.5) -->
		self.W_SCREEN = max(460, self.windowWidth * 29 / 100)
		self.X_SCREEN = self.windowWidth - self.W_SCREEN - 10
		self.H_SCREEN = max(768, self.windowHeight - 40)
		self.Y_SCREEN = self.windowHeight / 2 - self.H_SCREEN / 2
		self.Y_TITLE = self.Y_SCREEN + 20
		self.activeProject = iFinishedProject

		self.PADDING = 15
		self.W_EXIT = 150
		self.H_EXIT = 40
		self.X_EXIT = self.X_SCREEN + self.W_SCREEN - self.W_EXIT - self.PADDING
		self.Y_EXIT = self.Y_SCREEN + self.H_SCREEN - self.H_EXIT - self.PADDING

		self.W_LAUNCH = 140
		self.H_LAUNCH = 60
		self.X_LAUNCH = self.X_SCREEN - self.PADDING - self.W_LAUNCH
		self.Y_LAUNCH = self.Y_SCREEN + self.H_SCREEN - self.H_LAUNCH - self.PADDING

		self.X_LAUNCH_LABEL1 = self.X_SCREEN + self.PADDING
		self.Y_LAUNCH_LABEL1 = self.Y_LAUNCH + 8
		self.X_LAUNCH_LABEL2 = self.X_LAUNCH_LABEL1
		self.Y_LAUNCH_LABEL2 = self.Y_LAUNCH + 32

		self.TYPE_BUTTON = 0
		self.ZOOM_BUTTON = 1
		self.ADD_BUTTON = 2
		self.LAUNCH_BUTTON = 3

		#main panel
		screen.addPanel("SpaceShipMainPanel", "", "", true, true, self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN, PanelStyles.PANEL_STYLE_EMPTY)

		#create list of spaceship components
		self.componentProjects = []
		self.spaceVictory = -1
		for i in range(gc.getNumProjectInfos()):
			component = gc.getProjectInfo(i)
			if (component.isSpaceship()):
				self.spaceVictory = component.getVictoryPrereq()
				self.componentProjects.append(i)

		#title text
		self.finishedLabelX = 10
		self.finishedLabelY = 10
		self.finishedLabelX2 = self.finishedLabelX
		self.finishedLabelY2 = self.finishedLabelY + 30
		# <!-- custom: replace hardcoded <font=...> tags with SAS scaling helpers so spaceship text follows global UI font defines. (GPT-5.3-Codex) -->
		if(self.activeProject >= 0):
			screen.setLabel("FinishedLabel", "SpaceShipMainPanel", u"<color=255,255,0>" + SASTextScale.titleText(localText.getText("TXT_KEY_WONDER_SCREEN_TEXT", (gc.getProjectInfo(self.activeProject).getDescription(),))) + u"</color>", CvUtil.FONT_LEFT_JUSTIFY, self.finishedLabelX, self.finishedLabelY, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setLabel("FinishedLabel2", "SpaceShipMainPanel", u"<color=255,255,0>" + SASTextScale.titleText(localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_ADD_COMPONENT", ())) + u"</color>", CvUtil.FONT_LEFT_JUSTIFY, self.finishedLabelX2, self.finishedLabelY2, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		else:
			#check if landed on alpha centauri
			activeTeam = gc.getGame().getActiveTeam()
			victoryCountdown = gc.getTeam(activeTeam).getVictoryCountdown(self.spaceVictory)
			gameState = gc.getGame().getGameState()
			if(((gameState == GameStateTypes.GAMESTATE_EXTENDED) and (victoryCountdown > 0)) or (victoryCountdown == 0)):
				screen.setLabel("FinishedLabel", "SpaceShipMainPanel", u"<color=255,255,0>" + SASTextScale.titleText(localText.getText("TXT_KEY_SPACE_SHIP_ALPHA_CENTAURI", ())) + u"</color>", CvUtil.FONT_LEFT_JUSTIFY, self.finishedLabelX, self.finishedLabelY, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			else: #normal welcome
				screen.setLabel("FinishedLabel", "SpaceShipMainPanel", u"<color=255,255,0>" + SASTextScale.titleText(localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_WELCOME", ())) + u"</color>", CvUtil.FONT_LEFT_JUSTIFY, self.finishedLabelX, self.finishedLabelY, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				if (victoryCountdown > 0): # K-Mod (success chance is now shown near the launch button)
					screen.setLabel("FinishedLabel2", "SpaceShipMainPanel", u"<color=255,255,0>" + SASTextScale.titleText(localText.getText("TXT_KEY_SPACESHIP_CHANCE_OF_SUCCESS", (gc.getTeam(gc.getGame().getActiveTeam()).getLaunchSuccessRate(self.spaceVictory), ))) + u"</color>", CvUtil.FONT_LEFT_JUSTIFY, self.finishedLabelX2, self.finishedLabelY2, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		#component panels
		self.numComponents = len(self.componentProjects)
		self.componentPanelYOffset = 10
		self.componentPanelXOffset = 10
		# <!-- custom: Was H_SCREEN / (numComponents + 1), a whole part's height kept free for the Exit button; it needs only its own height, so the parts share the rest. (Claude code Opus 5.5) -->
		self.componentPanelHeight = (self.H_SCREEN - self.H_EXIT - 2 * self.PADDING) / self.numComponents
		self.componentPanelHeightExtra = 10
		self.componentPanelWidth = self.W_SCREEN - 2 * self.componentPanelXOffset
		self.componentNameXOffset = 12
		# <!-- custom: Was 10, which left the name against the panel's top edge. (Claude code Opus 5.5) -->
		self.componentNameYOffset = 18
		self.componentNameIconSize = 24
		self.componentTypeWidth = 80
		self.componentTypeHeight = 30
		self.componentTypeXOffset = self.componentPanelWidth - self.componentTypeWidth - 10
		self.componentTypeYOffset = 35
		self.componentZoomWidth = 80
		self.componentZoomHeight = 30
		self.componentZoomXOffset = self.componentPanelWidth - self.componentZoomWidth - 10
		self.componentZoomYOffset = 65
		self.componentAddWidth = 80
		self.componentAddHeight = 60
		self.componentAddXOffset = 10
		self.componentAddYOffset = 35
		self.componentModelHeight = self.componentPanelHeight
		self.componentModelWidth = 2 * self.componentModelHeight
		# <!-- custom: Was centered on the whole panel, so the model sat close to the labels on the left; it is now centered on the space between the widest label, measured in the current font, and the Type and Zoom buttons.
		# A fixed 210 pixels for the labels put it too far right at 1080p, as they took about 140. (Claude code Opus 5.5) -->
		iWidestLabel = 0
		for szLabel in (localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_COMPLETED_LABEL", (99, 99)), localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_REQUIRED_LABEL", (99,)), localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_IN_PRODUCTION_LABEL", (99,))):
			iWidestLabel = max(iWidestLabel, CyInterface().determineWidth(SASTextScale.labelText(szLabel)))
		iModelSpaceLeft = self.componentNameXOffset + iWidestLabel
		iModelSpaceRight = self.componentTypeXOffset
		self.componentModelXOffset = (iModelSpaceLeft + iModelSpaceRight - self.componentModelWidth) / 2
		self.componentModelYOffset = 0
		# <!-- custom: The three labels were 15 pixels apart, too close for upscaled text; they now share the panel's height below the name. (Claude code Opus 5.5) -->
		# <!-- custom: The name, in the title font with its 24-pixel button, overflowed onto the first label at 42; they now start at 60. (Claude code Opus 5.5) -->
		iLabelStep = (self.componentPanelHeight - 60) / 3
		self.componentCompletedLabelXOffset = 12
		self.componentCompletedLabelYOffset = 60
		self.componentRequiredLabelXOffset = 12
		self.componentRequiredLabelYOffset = 60 + iLabelStep
		self.componentInProductionLabelXOffset = 12
		self.componentInProductionLabelYOffset = 60 + 2 * iLabelStep

		screen.setSpaceShip(self.activeProject)
		self.rebuildComponentPanel()

		#show spaceship screen
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		return 0

	def rebuildComponentPanel(self):
		screen = CyGInterfaceScreen( "SpaceShipScreen", CvScreenEnums.SPACE_SHIP_SCREEN)
		self.removeComponentsPanel()

		#check if already landed spaceship
		activeTeam = gc.getGame().getActiveTeam()
		victoryCountdown = gc.getTeam(activeTeam).getVictoryCountdown(self.spaceVictory)
		gameState = gc.getGame().getGameState()
		if(not (((gameState == GameStateTypes.GAMESTATE_EXTENDED) and (victoryCountdown > 0)) or (victoryCountdown == 0))):

			#loop through each panel
			for i in range(self.numComponents):
				index = self.componentProjects[i]
				component = gc.getProjectInfo(index)
				xPosition = self.X_SCREEN + self.componentPanelXOffset
				yPosition = self.Y_SCREEN + self.componentPanelYOffset + i * self.componentPanelHeight

				#panel
				xPositionOffset = 0
				if(index == self.activeProject):
					xPositionOffset = 80
				screen.addPanel("ComponentPanel" + str(i), "", "", true, true, xPosition - xPositionOffset, yPosition, self.componentPanelWidth + xPositionOffset, self.componentPanelHeight + self.componentPanelHeightExtra, PanelStyles.PANEL_STYLE_TECH)
				# <!-- custom: The part's name had no button or hover; it now shows the part's button and hovers and opens its Sevopedia page, as the Victory screen's part rows do. (Claude code Opus 5.5) -->
				szComponentName = SASTextScale.imageText(component.getButton(), self.componentNameIconSize, SASTextScale.titleText(component.getDescription()))
				screen.setText("ComponentLabel" + str(i), "ComponentPanel" + str(i), u"<color=255,255,0>" + szComponentName + u"</color>", CvUtil.FONT_LEFT_JUSTIFY, xPosition - xPositionOffset + self.componentNameXOffset, yPosition + self.componentNameYOffset, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, index, 1)

				#completed
				completed = gc.getTeam(activeTeam).getProjectCount(index)
				totalAllowed = component.getMaxTeamInstances()
				screen.setLabel("ComponentCompletedLabel" + str(i), "ComponentPanel" + str(i), SASTextScale.labelText(localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_COMPLETED_LABEL", (completed, totalAllowed))), CvUtil.FONT_LEFT_JUSTIFY, xPosition + self.componentCompletedLabelXOffset, yPosition + self.componentCompletedLabelYOffset, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

				#required
				required = component.getVictoryMinThreshold(self.spaceVictory)
				screen.setLabel("ComponentRequiredLabel" + str(i), "ComponentPanel" + str(i), SASTextScale.labelText(localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_REQUIRED_LABEL", (required,))), CvUtil.FONT_LEFT_JUSTIFY, xPosition + self.componentRequiredLabelXOffset, yPosition + self.componentRequiredLabelYOffset, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

				#in production
				inProduction = gc.getTeam(activeTeam).getProjectMaking(index)
				screen.setLabel("ComponentInProductionLabel" + str(i), "ComponentPanel" + str(i), SASTextScale.labelText(localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_IN_PRODUCTION_LABEL", (inProduction,))), CvUtil.FONT_LEFT_JUSTIFY, xPosition + self.componentInProductionLabelXOffset, yPosition + self.componentInProductionLabelYOffset, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

				#panel color
				if(completed >= required): #green
					screen.setPanelColor("ComponentPanel" + str(i), 85, 150, 87)
				else: #check if can build
					canBuild = True
					if(not gc.getTeam(activeTeam).isHasTech(component.getTechPrereq())):
						canBuild = False
					else:
						for j in range(gc.getNumProjectInfos()):
							if(gc.getTeam(activeTeam).getProjectCount(j) < component.getProjectsNeeded(j)):
								canBuild = False

					if(not canBuild): #grey
						screen.setPanelColor("ComponentPanel" + str(i), 128, 128, 128)

				#type button if necessary
				if(screen.spaceShipCanChangeType(index) and (victoryCountdown < 0)):
					screen.setButtonGFC("ComponentTypeButton" + str(i), SASTextScale.labelText(localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_TYPE_BUTTON", ())), "", xPosition + self.componentTypeXOffset, yPosition + self.componentTypeYOffset, self.componentTypeWidth, self.componentTypeHeight, WidgetTypes.WIDGET_GENERAL, self.TYPE_BUTTON, i, ButtonStyles.BUTTON_STYLE_STANDARD )

				#zoom button
				if(victoryCountdown < 0):
					screen.setButtonGFC("ComponentZoomButton" + str(i), SASTextScale.labelText(localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_ZOOM_BUTTON", ())), "", xPosition + self.componentZoomXOffset, yPosition + self.componentZoomYOffset, self.componentZoomWidth, self.componentZoomHeight, WidgetTypes.WIDGET_GENERAL, self.ZOOM_BUTTON, i, ButtonStyles.BUTTON_STYLE_STANDARD )

				#add button
				if(index == self.activeProject):
					screen.setButtonGFC("ComponentAddButton", SASTextScale.labelText(localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_ADD_BUTTON", ())), "", xPosition - xPositionOffset + self.componentAddXOffset, yPosition + self.componentAddYOffset, self.componentAddWidth, self.componentAddHeight, WidgetTypes.WIDGET_GENERAL, self.ADD_BUTTON, i, ButtonStyles.BUTTON_STYLE_STANDARD )

				#component model
				modelType = gc.getTeam(activeTeam).getProjectDefaultArtType(index)
				screen.addSpaceShipWidgetGFC("ComponentModel" + str(i), xPosition + self.componentModelXOffset, yPosition + self.componentModelYOffset, self.componentModelWidth, self.componentModelHeight, index, modelType, WidgetTypes.WIDGET_GENERAL, -1, -1)

			#launch button
			activeTeam = gc.getGame().getActiveTeam()
			if(victoryCountdown > 0):
				victoryDate = CyGameTextMgr().getTimeStr(gc.getGame().getGameTurn() + victoryCountdown, false)
				screen.setLabel("ArrivalLabel1", "SpaceShipMainPanel", u"<color=255,255,0>" + SASTextScale.titleText(localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_ARRIVAL", ()) + ": " + victoryDate) + u"</color>", CvUtil.FONT_LEFT_JUSTIFY, self.X_LAUNCH_LABEL1, self.Y_LAUNCH_LABEL1, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				screen.setLabel("ArrivalLabel2", "SpaceShipMainPanel", u"<color=255,255,0>" + SASTextScale.titleText(localText.getText("TXT_KEY_REPLAY_SCREEN_TURNS", ()) + ": " + str(victoryCountdown)) + u"</color>", CvUtil.FONT_LEFT_JUSTIFY, self.X_LAUNCH_LABEL2, self.Y_LAUNCH_LABEL2, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			elif(gc.getTeam(gc.getGame().getActiveTeam()).canLaunch(self.spaceVictory)):
				delay = gc.getTeam(gc.getGame().getActiveTeam()).getVictoryDelay(self.spaceVictory)
				screen.setLabel("LaunchLabel1", "SpaceShipMainPanel", u"<color=255,255,0>" + SASTextScale.titleText(localText.getText("TXT_KEY_SPACESHIP_CHANCE_OF_SUCCESS", (gc.getTeam(gc.getGame().getActiveTeam()).getLaunchSuccessRate(self.spaceVictory), ))) + u"</color>", CvUtil.FONT_LEFT_JUSTIFY, self.X_LAUNCH_LABEL1, self.Y_LAUNCH_LABEL1, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				screen.setLabel("LaunchLabel2", "SpaceShipMainPanel", u"<color=255,255,0>" + SASTextScale.titleText(localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_TRAVEL_TIME_LABEL", (delay,))) + u"</color>", CvUtil.FONT_LEFT_JUSTIFY, self.X_LAUNCH_LABEL2, self.Y_LAUNCH_LABEL2, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
				# <!-- custom: Label font, as for the Exit button below. (Claude code Opus 5.5) -->
				screen.setButtonGFC("LaunchButton", SASTextScale.labelText(localText.getText("TXT_KEY_SPACE_SHIP_SCREEN_LAUNCH_BUTTON", ())), "", self.X_LAUNCH, self.Y_LAUNCH, self.W_LAUNCH, self.H_LAUNCH, WidgetTypes.WIDGET_GENERAL, self.LAUNCH_BUTTON, -1, ButtonStyles.BUTTON_STYLE_STANDARD )

		#exit button
		# <!-- custom: The splash and dialog screens gave their OK/Exit button the title font, the label font or none, so the same fixed-size button read out of proportion with the screen's own text from one screen to the next; all now take the label font, as the rest of their text does (the user, 2026-11-21). (Claude code Opus 5.5) -->
		screen.setButtonGFC("ExitButton", SASTextScale.labelText(localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ())), "", self.X_EXIT, self.Y_EXIT, self.W_EXIT, self.H_EXIT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )

	def removeComponentsPanel(self):
		screen = CyGInterfaceScreen( "SpaceShipScreen", CvScreenEnums.SPACE_SHIP_SCREEN)
		screen.deleteWidget("SpaceShipMainPanel")
		screen.deleteWidget("ComponentAddButton")
		screen.deleteWidget("LaunchLabel")
		screen.deleteWidget("LaunchButton")
		screen.deleteWidget("ExitButton")

		for i in range(self.numComponents):
			screen.deleteWidget("ComponentPanel" + str(i))
			screen.deleteWidget("ComponentLabel" + str(i))
			screen.deleteWidget("ComponentCompletedLabel" + str(i))
			screen.deleteWidget("ComponentRequiredLabel" + str(i))
			screen.deleteWidget("ComponentInProductionLabel" + str(i))
			screen.deleteWidget("ComponentTypeButton" + str(i))
			screen.deleteWidget("ComponentZoomButton" + str(i))
			screen.deleteWidget("ComponentModel" + str(i))

	# Will handle the input for this screen...
	def handleInput (self, inputClass):
		# <!-- custom: The part names' Sevopedia widget carries the project ID in data1, which the button codes below would otherwise read as a Type, Zoom, Add or Launch press. (Claude code Opus 5.5) -->
		if inputClass.getButtonType() == WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT:
			return 0
		if(inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED):
			data1 = inputClass.getData1()
			data2 = inputClass.getData2()
			if(data1 == self.TYPE_BUTTON):
				screen = CyGInterfaceScreen( "SpaceShipScreen", CvScreenEnums.SPACE_SHIP_SCREEN)
				xPosition = self.X_SCREEN + self.componentPanelXOffset
				yPosition = self.Y_SCREEN + self.componentPanelYOffset + data2 * self.componentPanelHeight
				index = self.componentProjects[data2]
				screen.spaceShipChangeType(index)
				activeTeam = gc.getGame().getActiveTeam()
				modelType = gc.getTeam(activeTeam).getProjectDefaultArtType(index)
				screen.addSpaceShipWidgetGFC("ComponentModel" + str(data2), xPosition + self.componentModelXOffset, yPosition + self.componentModelYOffset, self.componentModelWidth, self.componentModelHeight, index, modelType, WidgetTypes.WIDGET_GENERAL, -1, -1)
			elif(data1 == self.ZOOM_BUTTON):
				screen = CyGInterfaceScreen( "SpaceShipScreen", CvScreenEnums.SPACE_SHIP_SCREEN)
				screen.spaceShipZoom(self.componentProjects[data2])
			elif(data1 == self.ADD_BUTTON):
				screen = CyGInterfaceScreen( "SpaceShipScreen", CvScreenEnums.SPACE_SHIP_SCREEN)
				screen.spaceShipFinalize()

				#adjust interface
				screen.deleteWidget("ComponentAddButton")
				self.activeProject = -1
				self.rebuildComponentPanel()
			elif(data1 == self.LAUNCH_BUTTON):
				screen = CyGInterfaceScreen( "SpaceShipScreen", CvScreenEnums.SPACE_SHIP_SCREEN)
				screen.spaceShipLaunch()

				self.removeComponentsPanel()

		return 0

	def update(self, fDelta):
		return

	def onClose(self):
		return

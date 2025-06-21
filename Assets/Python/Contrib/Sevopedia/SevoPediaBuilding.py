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
# <!-- custom: refactoring (of the below (and in too but anyways etc anyways etc)) is based on the sevopediaunit refactoring with small alterations/changes or/and not to fit/suit the sevopedia building code/features (also refactoring it (i.e: the sevopediabuilding code anyways etc) allowed to further polish and tweak and refactor or/and fix or not or and other or and not anyways etc the sevopediaunit code so very nice or not nice or nice but not necessary or is or is not maybe or not (is) or yes (is not) but anyways etc anyways etc anyways etc...) done before that/this one anyways etc anyways etc, please/you can look there if you want more code comments and clarifications about the changes anyways etc anyways etc anyways etc)
# -->
# <!-- custom: new, added thanks to Claude AI's code and my prompts anyways etc or and other things or and not anyways etc, and adjusted and tweaked or and modified in general or not general ways or not anyways etc for AdvCiv-SAS:
# - placeCivilizations: (renamed from Claude AI's if i am not mistaken anyways etc ('s anyways etc) original name to this function placeExclusiveCivs) now we have buttons for the civ(s) that can build a unit, and no button at all if all civs can build the currently selected unit (to not clutter the display needlessly with all civs buttons and is also clearer to know immediately that all can build it with the panel being empty),
# - placeObsoleteWith in a similar manner than (for?) placeCivilizations to show the button of the tech that obsoletes this currently selected building anyways etc anyways etc anyways etc...
# - (and) placeReplace (but anyways etc anyways etc anyways etc...): based on the one in sevopediaunit that was based on another mod's code (see in sevopediaunit's code for details anyways etc anyways etc anyways etc...) and adjusted or not or yes or other etc anyways etc for and while adding it to sevopediabuilding, improvements (or not.. or yes, or other anyways etc) of which that have served to enhance the one in sevopediaunit back so all good maybe or not all good or all good or other or and not but anyways etc... anyways etc anyways etc anyways etc..
# - placeRequiredFor,
# - placeFreePBBS,
# - placeFreeWith,
# - enhanced or beautified or tweaked or and other or and not some if not most or maybe even or not or maybe or and anyways etc all functions/methods of this py file, anyways etc.
#  thanks a lot Claude AI! (and the other mod too ("!" too or ! too or maye rather !"" or "!" or rather ! or "!" too but anyways etc anyways etc anyways thanks too in short maybe anyways etc anywas etc anyways etc...) Anyways etc anyways etc anyways etc... -->
# -->




		# <!-- custom: note about "Check for required buildings" anyways etc
		# For the example for Eiffel Tower (base advciv data):
		# 	<PrereqBuildingClasses/>
		# 	<BuildingClassNeededs>
		# 		<BuildingClassNeeded>
		# 			<BuildingClassType>BUILDINGCLASS_FORGE</BuildingClassType>
		# 			<bNeededInCity>1</bNeededInCity>
		# 		</BuildingClassNeeded>
		# 	</BuildingClassNeededs>
		#
		# But for (,) for example (anyways etc) the Oxford University (base advciv data) for example anyways etc
		# 	<PrereqBuildingClasses>
		# 		<PrereqBuildingClass>
		# 			<BuildingClassType>BUILDINGCLASS_UNIVERSITY</BuildingClassType>
		# 			<iNumBuildingNeeded>4</iNumBuildingNeeded>
		# 		</PrereqBuildingClass>
		# 	</PrereqBuildingClasses>
		# 	<BuildingClassNeededs>
		# 		<BuildingClassNeeded>
		# 			<BuildingClassType>BUILDINGCLASS_UNIVERSITY</BuildingClassType>
		# 			<bNeededInCity>1</bNeededInCity>
		# 		</BuildingClassNeeded>
		# 	</BuildingClassNeededs>
		#
		# So if i am not mistaken we need to account for both:
		# - BuildingClassNeededs (buildingInfo.isBuildingClassNeededInCity(i) below if i am not mistaken indeed (but) anyways etc) (see also (translate to english with your web browser or/and such or not if you want/wish/please or not as you prefer or not or yes or and other or and not anyways etc: https://gforestshade.github.io/kujira/post/civ4buildinginfos/#prereqbuildingclasses)), and
		# - PrereqBuildingClasses (buildingInfo.getPrereqNumOfBuildingClass(i) below if i am not mistaken anyways etc... anyways etc anyways etc... , see also as well https://gforestshade.github.io/kujira/post/civ4buildinginfos/#buildingclassneededs if you want/wish/do or not or and other or and not anyways etc anyways etc anyways etc...) and represent them accurately ideally too anyways etc(...) anyways etc anyways etc...
		# -->


			# for freebonus, done according to according to kujira's website if i am not mistaken anyways etc, in https://gforestshade.github.io/kujira/post/civ4buildinginfos/#inumfreebonuses (translated to english with google chrome):
			#
			# This determines the amount of resource this structure produces.
			# If <FreeBonus> is set to a value other than NONE and you set this to a positive value,the structure will produce the specified amount of the specified resource.
			# If you want a variable number based on map size instead of a fixed number, specify -1, in which case the value of <iNumFreeBuildingBonuses> from each map size definition in \XML\GameInfo\CIV4WorldInfo.xml will be used. If you do not want to use this feature, specify 0.
			#
			# Example 1:
			# <FreeBonus>NONE</FreeBonus>
			# <iNumFreeBonuses>0</iNumFreeBonuses>
			#
			# Example 2: Produce hit musicals in numbers that depend on the map size.
			# <FreeBonus>BONUS_DRAMA</FreeBonus>
			# <iNumFreeBonuses>-1</iNumFreeBonuses>
			#
			# Example 3: Produce one horse.
			# <FreeBonus>BONUS_HORSE</FreeBonus>
			# <iNumFreeBonuses>1</iNumFreeBonuses>


		# For (/to) parsing (parse?) this (i.e. free power only not power for example with ressource(s?)/bonus(es? (which is PowerBonus if i am not mistaken and that we ignore then if i am not mistaken to do so anyways etc anyways etc anyways etc anyways etc((.)... anyways etc...)) anyways) (tentative (for me to assess (anyways etc)) (but maybe successful (/fructful?) anyways etc) rules seem to be after some testing (with a "power>1" global search in unit infos and tweaking or maybe rather anyways etc temporarily modifying some values to see some if not all or not or yes or and other or and not anyways etc edge case reuslts), for example:
		# - BUILDING_THREE_GORGES_DAM (now renamed from GREAT_DAM see code comments for details (if any (i.e. details anyways etc) anyways etc)):
		# 	<bPower>0</bPower>
		# 	<bDirtyPower>0</bDirtyPower>
		# 	<bAreaCleanPower>1</bAreaCleanPower>
		# And ingame in placeSpecial we see: "Provides Power ((icon/button? anyways etc)) for All cities in this continent", so we parse it as a "AllC Clean" or something like this anyways etc, to know if clean or dirty for all cities, i changed its values a bit to:
		# 	<bPower>0</bPower>
		# 	<!-- custom: test -->
		# 	<bDirtyPower>1</bDirtyPower>
		# 	<bAreaCleanPower>1</bAreaCleanPower>
		# The placeSpecial text remains the same, no mention of dirty power in it, i assume clean (in this case anyways etc) wins over dirty so power is clean by default of win of strongest ones in this city as in all cities already is anyways etc, they don't seem to cumulate anyways etc
		# The Civ4 Wiki also gives some useful info about this: https://civilization.fandom.com/wiki/Power_(Civ4), so we updated in AdvCiv-SAS the DLL message that comes with (in PlaceSpecial if i am not mistaken anyways etc) TXT_KEY_BUILDING_PROVIDES_AREA_CLEAN_POWER (now renamed to TXT_KEY_BUILDING_PROVIDES_AREA_CLEAN_POWER) to match and reflect and inform of this (unhappiness existence and count anyways etc) (if we are (ideally maybe yes or not or yes or and other or and not or etc anyways etc) not mistaken in our understanding indeed maybe or not or yes or and other or and not anyways etc).


		# #<!-- custom: example of how to directly import a button path to write the button in sevopedia anyways etc... From Claude AI as well and works for the great prophet button successfully displayed in the sevopedia's placeFreePBBS panel for example anyways etc anyways etc anyways etc
		# #powerButton = "Art/Interface/Buttons/Buildings/Power.dds"  # You might need to adjust this path
		# powerButton = ",Art/Interface/Buttons/Units/GreatProphet.dds,Art/Interface/Buttons/Unit_Resource_Atlas.dds,5,1"
		# # etc...
		# 				screen.attachImageButton(panelName, "", powerButton, 
		# 							GenericButtonSizes.BUTTON_SIZE_CUSTOM, 
		# 							WidgetTypes.WIDGET_GENERAL, -1, -1, False)
		# We eventually don't use it as we in the end don't implement the unreliable and messy free power functionality (at least we couldn't make it work), but hopefully helpful enough and helped us fix other issues as well or understand betetr the game (how it works/functions) anyways etc...
		# For reference, the power button code can be found here using the Warlords atlas (i assume it was used for a religion, but probably works very well for the power button if we were to implement it, which we don't do here in the end, anyways etc):
		# in C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Warlords\Assets\Art\Interface\Buttons\Warlords_Atlas_2.dds
		# powerButtonPath = ",Art/Interface/MainScreen/CityScreen/Great_Engineer.dds,Art/Interface/Buttons/Warlords_Atlas_2.dds,6,11"
		# -->


	# <!-- custom: logic is as follows for the below placeFreeWith function/method anyways etc as prompted to Claude AI to me but anyways etc anyways etc anyways etc...:
	# example: barbarian specific granary is free with barbarian palace (barbarians only), so:
	#
	# if currently selected building is:
	# 	* barbarian granary: we show in free with that the barbarian granary is free with the barbarian palace button
	# 	* generic granary: we show in free with that the generic granary is free with "None" if a barbarian specific palace exists, else if no barbarian palace exists then we show in free with that the generic granary is free with the barbarian palace
	# 	* other civ-specific granary (for example incan terrace): we show in free with that the terrace is free with "None", as the incans cannot have the barbarian palace, so they can never have the free granary, but if the incans could have a palace that has a free granary in it, then display this palace instead, else "None"
	#
	# -
	#
	# Which Claude AI rephrased as such if helps too anyways etc:
	# Now the logic correctly handles your examples:
	# For your barbarian granary → barbarian palace example:
	#
	# 	1. Barbarian Granary page: Shows barbarian palace (because barbarian granary is unique and barbarian palace provides it for free)
	# 	2. Generic Granary page: Shows "None" (because the granary class has unique versions like barbarian granary, so only generic providers would be shown, but barbarian palace is unique)
	# 	3. Incan Terrace page: Shows "None" (because terrace is unique to Incans, and barbarian palace is unique to barbarians, so Incans can't use barbarian palace)
	#
	# The key logic changes:
	#
	# hasUniqueVersions: Checks if the current building class has any civ-specific versions
	# For unique buildings: Only shows providers that the same civ can actually use
	# For generic buildings: If unique versions of this building exist, only shows generic providers; otherwise shows all providers
	# New helper functions: getBuildingCiv() and buildingClassHasUniqueVersions() to support the logic
	#
	# This should now match your intended behavior exactly!
	#
	# -
	#
	# It seems to work as intended so adding this since is quite/very technical, in case is helpful too, anyways etc anyways etc anyways etc...
	# -->



from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums

from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaBuilding:

	def __init__(self, main):
		self.iBuilding = -1
		self.top = main

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		self.X_BUILDING_PANE = self.top.X_PEDIA_PAGE
		self.Y_BUILDING_PANE = self.top.Y_PEDIA_PAGE
		self.W_BUILDING_PANE = (self.top.R_PEDIA_PAGE - self.X_BUILDING_PANE - self.MEDIUM_MARGIN) / 2
		self.H_BUILDING_PANE = 190

		# <!-- custom: import iIconFrameSize from sevopediaunit ((base) advciv's code anyways etc) and modified it and its logic for advciv-sas or not or yes or and other things or and not anyways etc -->
		self.ICON_SIZE = 64
		self.ICON_FRAME_SIZE = 164
		self.MAX_ICON_FRAME_SIZE = 164

		if (self.ICON_SIZE > self.ICON_FRAME_SIZE):
			raise ValueError(u"[FATAL] self.ICON_SIZE=%d cannot be bigger/higher than self.ICON_FRAME_SIZE=%d, self.ICON_SIZE must fit within the frame, please adjust self.ICON_SIZE or/and self.ICON_FRAME_SIZE so that 0 < self.ICON_SIZE < self.ICON_FRAME_SIZE" % (self.ICON_SIZE, self.ICON_FRAME_SIZE))
		if (self.ICON_FRAME_SIZE > self.MAX_ICON_FRAME_SIZE):
			raise ValueError(u"[FATAL] Out of bounds self.ICON_FRAME_SIZE=%d, must be lower than  cannot be bigger/higher than self.MAX_ICON_FRAME_SIZE, please reduce self.ICON_FRAME_SIZE so that 0 < self.ICON_FRAME_SIZE < self.MAX_ICON_FRAME_SIZE" % (self.ICON_FRAME_SIZE, self.MAX_ICON_FRAME_SIZE))

		self.W_ICON = self.ICON_SIZE
		self.H_ICON = self.ICON_SIZE
		# <!-- custom: if self.ICON_SIZE is small (e.g. 64), start at the center of self.X_BUILDING_PANE, but if self.ICON_SIZE is big (e.g. 164) start at the left most part of self.X_BUILDING_PANE ; same reasoning for Y position -->
		self.X_ICON = self.X_BUILDING_PANE + (self.ICON_FRAME_SIZE - self.ICON_SIZE) / 2
		self.Y_ICON = self.Y_BUILDING_PANE + (self.H_BUILDING_PANE - self.H_ICON) / 2

		# <!-- custom: add an extra margin to accomodate the potentially larger self.ICON_SIZE (than for example 64), if diff is 0 this is harmless to keep too so is dynamical code that can handle optionally larger self.ICON_SIZE (vs old self.ICON_SIZE of 64) that you may keep or remove as you prefer anyways etc -->
		self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN = (self.ICON_FRAME_SIZE - self.ICON_SIZE) / 2

		self.STATS_PANE_LEFT_SIDE_MARGIN = 0
		self.STATS_PANE_UPPER_PADDING = 38

		# <!-- custom: before starting, store great people change's placeStats coordinate, initialize or/and reinitialize them to none anyways etc, these are only used in placeStats so it should be safe, but we need to store them for later reuse (to display in/at/during a second pass anyways etc the great people button in another overlapping transparent panel), see placeStats "custom 6.1.1:" for details -->
		self.X_GREAT_PEOPLE_CHANGE_IN_GRID = None
		self.Y_GREAT_PEOPLE_CHANGE_IN_GRID = None

		self.X_STATS_PANE = self.X_BUILDING_PANE + self.STATS_PANE_LEFT_SIDE_MARGIN + self.W_ICON + (2 * self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN)
		self.Y_STATS_PANE = self.Y_BUILDING_PANE + self.STATS_PANE_UPPER_PADDING
		self.W_STATS_PANE = self.W_BUILDING_PANE - self.W_ICON - (2 * self.SMALLER_ICON_SIZE_THAN_ICON_FRAME_MARGIN) - self.STATS_PANE_LEFT_SIDE_MARGIN
		self.H_STATS_PANE = self.H_BUILDING_PANE - self.STATS_PANE_UPPER_PADDING

		self.H_STATS_PANE_LINE_HEIGHT = 38

		# <!-- custom: see sevopediaunit's self.W_TOTAL_EFFECTIVE_UNIT_PANE for differences in implementation anyways etc -->
		self.W_TOTAL_EFFECTIVE_BUILDING_PANE = self.W_BUILDING_PANE

		self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING = 8
		self.HYPOTHESIZED_INTER_BUTTON_SPACING = 4

		self.X_REQUIRES = self.X_BUILDING_PANE
		self.Y_REQUIRES = self.Y_BUILDING_PANE + self.H_BUILDING_PANE + self.SMALL_MARGIN
		self.W_REQUIRES = self.W_TOTAL_EFFECTIVE_BUILDING_PANE
		self.H_REQUIRES = 110

		self.W_OBSOLETE_WITH = 84

		self.X_REQUIRED_FOR = self.X_BUILDING_PANE
		self.Y_REQUIRED_FOR = self.Y_REQUIRES + self.H_REQUIRES + self.SMALL_MARGIN
		self.W_REQUIRED_FOR = self.W_TOTAL_EFFECTIVE_BUILDING_PANE - self.W_OBSOLETE_WITH - self.MEDIUM_MARGIN
		self.H_REQUIRED_FOR = self.H_REQUIRES

		self.X_OBSOLETE_WITH = self.X_REQUIRED_FOR + self.W_REQUIRED_FOR + self.MEDIUM_MARGIN
		self.Y_OBSOLETE_WITH = self.Y_REQUIRED_FOR
		self.H_OBSOLETE_WITH = self.H_REQUIRED_FOR

		self.W_FREE_WITH = 84

		self.X_FREE_PBBS = self.X_BUILDING_PANE
		self.Y_FREE_PBBS = self.Y_REQUIRED_FOR + self.H_REQUIRED_FOR + self.SMALL_MARGIN
		self.W_FREE_PBBS = self.W_TOTAL_EFFECTIVE_BUILDING_PANE - self.W_FREE_WITH - self.MEDIUM_MARGIN
		self.H_FREE_PBBS = self.H_REQUIRES

		self.X_FREE_WITH = self.X_FREE_PBBS + self.W_FREE_PBBS + self.MEDIUM_MARGIN
		self.Y_FREE_WITH = self.Y_FREE_PBBS
		self.H_FREE_WITH = self.H_REQUIRES

		self.X_SPECIAL = self.X_BUILDING_PANE
		self.Y_SPECIAL = self.Y_FREE_PBBS + self.H_FREE_PBBS + self.SMALL_MARGIN
		self.W_SPECIAL = self.W_TOTAL_EFFECTIVE_BUILDING_PANE
		self.H_SPECIAL = self.top.B_PEDIA_PAGE - self.Y_SPECIAL

		self.H_ADJUST_HEIGHT_ANIMATION_TO_MATCH_ADJACENT_PANE = 7

		self.X_BUILDING_ANIMATION = self.X_BUILDING_PANE + self.W_TOTAL_EFFECTIVE_BUILDING_PANE + self.MEDIUM_MARGIN
		self.Y_BUILDING_ANIMATION = self.Y_BUILDING_PANE + self.H_ADJUST_HEIGHT_ANIMATION_TO_MATCH_ADJACENT_PANE
		self.W_BUILDING_ANIMATION = self.W_TOTAL_EFFECTIVE_BUILDING_PANE
		self.H_BUILDING_ANIMATION = self.H_BUILDING_PANE + self.SMALL_MARGIN + self.H_REQUIRES + self.SMALL_MARGIN + self.H_FREE_PBBS - self.H_ADJUST_HEIGHT_ANIMATION_TO_MATCH_ADJACENT_PANE
		
		self.X_ROTATION_BUILDING_ANIMATION = -20
		self.Z_ROTATION_BUILDING_ANIMATION = 30
		self.SCALE_ANIMATION = 0.7

		self.W_CIVILIZATIONS = 84

		self.X_REPLACE = self.X_BUILDING_ANIMATION
		self.Y_REPLACE = self.Y_BUILDING_ANIMATION + self.H_BUILDING_ANIMATION + self.SMALL_MARGIN
		self.W_REPLACE = self.W_BUILDING_ANIMATION - self.MEDIUM_MARGIN - self.W_CIVILIZATIONS
		self.H_REPLACE = self.H_REQUIRES

		self.X_CIVILIZATIONS = self.X_BUILDING_ANIMATION + self.W_REPLACE + self.MEDIUM_MARGIN
		self.Y_CIVILIZATIONS = self.Y_REPLACE
		self.H_CIVILIZATIONS = self.H_REPLACE

		self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER = 22

		self.X_HISTORY = self.X_BUILDING_ANIMATION
		self.Y_HISTORY = self.Y_CIVILIZATIONS + self.H_CIVILIZATIONS + self.SMALL_MARGIN
		self.W_HISTORY = self.W_BUILDING_ANIMATION
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY



	def interfaceScreen(self, iBuilding):
		self.iBuilding = iBuilding

		self.placeBuildingPane()
		self.placeStats()
		self.placeRequires()
		self.placeRequiredFor()
		self.placeObsoleteWith()
		self.placeFreePBBS()
		self.placeFreeWith()
		self.placeSpecial()
		self.placeBuildingAnimation()
		self.placeReplace()
		self.placeCivilizations()
		self.placeHistory()



	def placeBuildingPane(self):
		screen = self.top.getScreen()

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_BUILDING_PANE, self.Y_BUILDING_PANE, self.W_TOTAL_EFFECTIVE_BUILDING_PANE, self.H_BUILDING_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getBuildingInfo(self.iBuilding).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )



	# <!-- custom: table code based on placeAiPersonality panel method/function in sevopedialeader we (me and becomingthrough chatgpt) had written and enhanced together and all anyways etc, modifying/adjusting it for this sevopediabuilding (much) simpler panel (stats pane) need but still important as we don't want to scroll after say 4th element, move to 2nd column rather and resume filling there. -->
	def placeStats(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		placeStatsPanelTxtKey = ""

		buildingInfo = gc.getBuildingInfo(self.iBuilding)

		numColumns = 3
		columnWidth = self.W_STATS_PANE / numColumns

		# <!-- custom: refer to code below to know max element count, so far we have in our code (see below for how it is implemented anyways etc), taken from claude AI's message and adjusted (formatted or not anyways etc) or not anyways etc thanks claude hehe anyways etc -->
		# Here's what the method now does in sequence:
		# - 1. Cost: Shows production cost
		# - 2. Yield Changes, and Yield Modifiers: Shows direct yields like food (+1 food from Baray), and Shows yield modifiers similarly (Food +x%, Production +x%, Gold +x%) with power breakdown (, +y% w/ (power button))
		# - 3. Commerce Changes, and Commerce Modifiers: Shows actual commerce amounts (+x science, gold, culture, espionage), and Shows percentage bonuses and double times (+x% and x2 times)
		# - 4. Happiness/Unhappiness: Shows happiness effects
		# - 5. Health/Unhealth: Shows health effects
		# - 6. Great People: Shows great people rate changes with button and great people modifiers too anyways etc
		# -->
		# <!-- custom: note: we have a risk of overflow of data/items to display, if all or most of these fields are full, while only having 9 grid positions to do so, this should be extremely rare, but if it were to happen, you can increase grid size to 3 columns * 4 rows (to do that, you could for example reduce line height spacing (but may be a bit ugly (maybe) but anyways), reduce upper padding (but maybe not needed or not lot as we can even now display a 4th row but not as pretty if starting from current "padded"(?)/upper padding), or for example artifically increase the panel height so the code thinks it has more room to fill one more row (which it has but then is bit ugly(ier) anyways etc) (the 4th before going to a new column and back to 1st row anyways etc), or maybe tweak the code i proudly as in rather funnily? did if that is a word hehe by myself based on old code from sevopedia leader's grid code (renderCategories and such if i am not mistaken and they are still named the same now anyways etc which we created as well with chatgpt/becomingthorugh (see authors for details) but anyways etc anyways etc anyways etc...) and adjusting/refatoring it for our need for this sevopedia building's placeStats anyways etc anyways etc anyways etc), or/and other things ways maybe to refactor it or not so it fits a 4th row or yes or and other or and not anyways etc. Since we don't have to do this, 9 grid of 3 columns * 3 rows are probably enough for us so staying/sticking with that maybe anyways etc anyways etc anyways etc...
		# -->

		def setupPanel(screen, panelName, txtKey, panelStyle):
			screen.addPanel(
				panelName,
				localText.getText(txtKey, ()),
				"",
				True,
				True,
				self.X_STATS_PANE,
				self.Y_STATS_PANE,
				self.W_STATS_PANE,
				self.H_STATS_PANE,
				panelStyle,
			)

		# === PANEL SETUP ===
		# <!-- custom: blue panel style PanelStyles.PANEL_STYLE_BLUE50 is/can be anyways etc useful for debugging, otherwise we don't need a blue on blue color, prefer transparent ("EMPTY" if i am not mistaken anyways etc), anyways etc -->
		setupPanel(screen, panelName, placeStatsPanelTxtKey, PanelStyles.PANEL_STYLE_EMPTY)

		def fillCell(screen, label, xLabel, y):
			labelText = u"<font=4>%s</font>" % label

			screen.setText(self.top.getNextWidgetName(), "", labelText,
				CvUtil.FONT_LEFT_JUSTIFY, xLabel, y, 0, FontTypes.SMALL_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)

		def getNextItemCoordinates(x, y, rowItemId, columnWidth):
			anticipatedNextRowId = rowItemId + 1
			anticipatedNextRowNum = anticipatedNextRowId + 1
			if (anticipatedNextRowNum * self.H_STATS_PANE_LINE_HEIGHT > (self.H_STATS_PANE - self.STATS_PANE_UPPER_PADDING)):
				# <!-- custom: move to next column and back to first row, reset columItemId to 0 -->
				x = x + columnWidth
				y = self.Y_STATS_PANE
				rowItemId = 0
				return x, y, rowItemId
			else:
				# <!-- custom: else x remains the same, and we go to next row (we stay in same column as long as we have room) -->
				y += self.H_STATS_PANE_LINE_HEIGHT
				rowItemId += 1
				return x, y, rowItemId

		# === Render Function ===
		def renderCells(screen, buildingInfo, columnWidth, xPanel, yPanel):
			x = xPanel
			y = yPanel
			rowItemId = 0

			# <!-- custom: if i am not mistaken it seems we never use the code below and i don't understand too well what it is for, but especially in our placeStats pane i don't think we use it at all if i am not mistaken, so commenting it out
			#if (isWorldWonderClass(gc.getBuildingInfo(self.iBuilding).getBuildingClassType())):
			#	iMaxInstances = gc.getBuildingClassInfo(gc.getBuildingInfo(self.iBuilding).getBuildingClassType()).getMaxGlobalInstances()
			#	szBuildingType = localText.getText("TXT_KEY_PEDIA_WORLD_WONDER", ())
			#	if (iMaxInstances > 1):
			#		szBuildingType += " " + localText.getText("TXT_KEY_PEDIA_WONDER_INSTANCES", (iMaxInstances,))
			#		szBuildingTypeText = u"<font=4>" + szBuildingType.upper() + u"</font>"
			#		screen.appendListBoxStringNoUpdate(panelName, szBuildingTypeText, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

			#if (isTeamWonderClass(gc.getBuildingInfo(self.iBuilding).getBuildingClassType())):
			#	iMaxInstances = gc.getBuildingClassInfo(gc.getBuildingInfo(self.iBuilding).getBuildingClassType()).getMaxTeamInstances()
			#	szBuildingType = localText.getText("TXT_KEY_PEDIA_TEAM_WONDER", ())
			#	if (iMaxInstances > 1):
			#		szBuildingType += " " + localText.getText("TXT_KEY_PEDIA_WONDER_INSTANCES", (iMaxInstances,))
			#		szBuildingTypeText = u"<font=4>" + szBuildingType.upper() + u"</font>"
			#		screen.appendListBoxStringNoUpdate(panelName, szBuildingTypeText, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

			#if (isNationalWonderClass(gc.getBuildingInfo(self.iBuilding).getBuildingClassType())):
			#	iMaxInstances = gc.getBuildingClassInfo(gc.getBuildingInfo(self.iBuilding).getBuildingClassType()).getMaxPlayerInstances()
			#	szBuildingType = localText.getText("TXT_KEY_PEDIA_NATIONAL_WONDER", ())
			#	if (iMaxInstances > 1):
			#		szBuildingType += " " + localText.getText("TXT_KEY_PEDIA_WONDER_INSTANCES", (iMaxInstances,))
			#		szBuildingTypeText = u"<font=4>" + szBuildingType.upper() + u"</font>"
			#		screen.appendListBoxStringNoUpdate(panelName, szBuildingTypeText, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

			# <!-- custom: 1: Cost -->
			if (buildingInfo.getProductionCost() > 0):
				if self.top.iActivePlayer == -1:
					szCost = localText.getText("TXT_KEY_PEDIA_COST_CUSTOM", ((buildingInfo.getProductionCost() * gc.getDefineINT("BUILDING_PRODUCTION_PERCENT"))/100,))
				else:
					szCost = localText.getText("TXT_KEY_PEDIA_COST_CUSTOM", (gc.getPlayer(self.top.iActivePlayer).getBuildingProductionNeeded(self.iBuilding),))
				szText2 = u"%c  %s" % (gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar(), szCost)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)


			# <!-- custom: 2 Direct Yield Changes (like Food, Production, Gold), and Yield Modifiers (Food +x%, Production +x%, Gold +x%) with power breakdown added thanks to Claude AI and my prompts or/and tweaks/adjustments or/and not or/and yes or and but or not but or and but anyways etc (2) -->
			for k in range(YieldTypes.NUM_YIELD_TYPES):
				iYieldChange = buildingInfo.getYieldChange(k)

				if (iYieldChange != 0):
					if (iYieldChange > 0):
						szSign = "+"
					else:
						szSign = ""
					szText1 = szSign + str(iYieldChange)
					szText2 = u"%c  %s" % (gc.getYieldInfo(k).getChar(), szText1)
					fillCell(screen, szText2, x, y)
					x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

				# <!-- custom: also adding yield modifiers in the same loop as yield changes for efficiency but also main reason would also be but anyways etc to display for example hammer +25% just after hammer +1 for example, and not after after gold + 5, anyways etc -->
				iYieldModifier = buildingInfo.getYieldModifier(k)
				iPowerYieldModifier = buildingInfo.getPowerYieldModifier(k)

				# Total modifier (regular + power)
				iTotalYieldModifier = iYieldModifier + iPowerYieldModifier
				
				if (iTotalYieldModifier != 0):
					szText1 = ""
					
					# Base modifier part
					if (iYieldModifier != 0):
						if (iYieldModifier > 0):
							szSign = "+"
						else:
							szSign = ""
						szText1 = szSign + str(iYieldModifier) + "%"
					
					# Power modifier part (optional, only if exists)
					if (iPowerYieldModifier != 0):
						if (len(szText1) > 0):
							szText1 += ", "
						if (iPowerYieldModifier > 0):
							szPowerSign = "+"
						else:
							szPowerSign = ""
						szText1 += szPowerSign + str(iPowerYieldModifier) + "% w/"
						
						# Add power button
						configButtonPathSTxtKey = "TXT_KEY_BUTTON_PATH_HARDCODED_POWER_BUTTON_PATH"
						resolvedButtonPath = CyTranslator().getText(configButtonPathSTxtKey, ())
						buttonHeader = "Power Button in Sevopedia Building's placeStats"
						check_button_path_is_valid(buttonHeader, resolvedButtonPath, configButtonPathSTxtKey)
						buttonSize = 24
						szButtonText = u"<img=%s size=%s></img>" % (resolvedButtonPath, str(buttonSize))
						szText1 += szButtonText

					szText2 = u"%c  %s" % (gc.getYieldInfo(k).getChar(), szText1)
					fillCell(screen, szText2, x, y)
					x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

			# <!-- custom: 3: Commerce Changes (Science, Gold, Culture, Espionage), and Commerce Modifiers and Double Times (3) -->
			for k in range(CommerceTypes.NUM_COMMERCE_TYPES):
				iTotalCommerce = buildingInfo.getObsoleteSafeCommerceChange(k) + buildingInfo.getCommerceChange(k)
				if (iTotalCommerce != 0):
					if (iTotalCommerce > 0):
						szSign = "+"
					else:
						szSign = ""
					szText1 = szSign + str(iTotalCommerce)
					szText2 = u"%c  %s" % (gc.getCommerceInfo(k).getChar(), szText1)
					fillCell(screen, szText2, x, y)
					x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

				# <!-- custom: also process the modifiers associated to the raw commerce changes just after the raw value (for example culture +1 then the next line is immediately culture +50 % and only then/after gold + 1 for example (and now not culture + 1 then gold + 1 and only then/after culture + 50% anyways etc), if i am not mistaken this is how it would work this code arragement or/and structure if i may say too indeed too too but anyways etc now if i may say, anyways etc) --> 
				iCommerceModifier = buildingInfo.getCommerceModifier(k)
				iCommerceDoubleTime = buildingInfo.getCommerceChangeDoubleTime(k)
				iGlobalCommerceModifier = buildingInfo.getGlobalCommerceModifier(k)
				
				# <!-- custom: placeSpecial (already) handles the full info display (currently not double times though if not always or not anyways etc), so we can simply be concise maybe or not or other anyways etc and display the total of "local" (if any (too than in global that i wrote the if any of before but anyways etc anyways etc anyways etc...)) + global commerce modifier (if any) rather anyways etc -->
				# Total modifier (local + global)
				iTotalModifier = iCommerceModifier + iGlobalCommerceModifier
				
				# Display if either modifier or double time exists
				if (iTotalModifier != 0 or iCommerceDoubleTime > 0):
					szText = ""
					
					# Add modifier percentage
					if (iTotalModifier != 0):
						if (iTotalModifier > 0):
							szSign = "+"
						else:
							szSign = ""
						szText += szSign + str(iTotalModifier) + "%"
					
					# Add double time if present
					if (iCommerceDoubleTime > 0):
						if (len(szText) > 0):
							szText += ", "
						szText += "x2(" + str(iCommerceDoubleTime) + "Y)"
					
					szText2 = u"%c  %s" % (gc.getCommerceInfo(k).getChar(), szText)
					fillCell(screen, szText2, x, y)
					x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

			# <!-- custom: 4: Happiness or Unhappiness anyways etc (4) -->
			iHappiness = buildingInfo.getHappiness()
			if self.top.iActivePlayer != -1:
				if (self.iBuilding == gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationBuildings(buildingInfo.getBuildingClassType())):
					iHappiness += gc.getPlayer(self.top.iActivePlayer).getExtraBuildingHappiness(self.iBuilding)

			if (iHappiness > 0):
				szText = localText.getText("TXT_KEY_PEDIA_HAPPY_CUSTOM", (iHappiness,))
				szText2 = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.HAPPY_CHAR), szText)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)
			elif (iHappiness < 0):
				szText = localText.getText("TXT_KEY_PEDIA_UNHAPPY_CUSTOM", (-iHappiness,))
				szText2 = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.UNHAPPY_CHAR), szText)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

			# <!-- custom: 5: Health(y?)(iness?? Anyways etc... Anyways etc...) or Unhealth(y)(same anyways etc... anyways etc...) anyways etc (5) -->
			iHealth = buildingInfo.getHealth()
			if self.top.iActivePlayer != -1:
				if (self.iBuilding == gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationBuildings(buildingInfo.getBuildingClassType())):
					iHealth += gc.getPlayer(self.top.iActivePlayer).getExtraBuildingHealth(self.iBuilding)

			if (iHealth > 0):
				szText = localText.getText("TXT_KEY_PEDIA_HEALTHY_CUSTOM", (iHealth,))
				szText2 = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.HEALTHY_CHAR), szText)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)
			elif (iHealth < 0):
				szText = localText.getText("TXT_KEY_PEDIA_UNHEALTHY_CUSTOM", (-iHealth,))
				szText2 = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.UNHEALTHY_CHAR), szText)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)
			
			# <!-- custom: 6: Great people change with button display of the great people type too if i am not mistaken anyways etc, and great people modifier -->
			# <!-- custom: 6.1.1: Only display the great people button and the value, for example "(Great People button) +2", use a button later in "custom 6.2:" rather instead anyways etc -->
			if buildingInfo.getGreatPeopleRateChange() != 0:
				# Create the text with the great person rate change
				szText = CyTranslator().getText("TXT_KEY_PEDIA_GREAT_PEOPLE_CUSTOM", (buildingInfo.getGreatPeopleRateChange(),))
				
				# Format with the great people character
				szText2 = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR), szText)
				
				# Display the text
				fillCell(screen, szText2, x, y)
				# <!-- custom: since this is our last usage/placeStats info displayed, we don't get the next coordinates, but instead store current coordinates (of last item displayed, anyways etc) to know where to place our great people button later in "custom: 6.2" below (if i am not mistaken that it is below, it should be in all cases later or not or yes but anyways etc anyways etc anyways etc -->
				self.X_GREAT_PEOPLE_CHANGE_IN_GRID = x
				self.Y_GREAT_PEOPLE_CHANGE_IN_GRID = y

			# <!-- custom: 6.1.5: While we're still in same panel (before "custom: 6.2" 's other specific panel that handles button display anyways etc), also add Great People Modifier (similar to how we handle yield modifiers) --> <!-- custom: code comment just before added by Claude AI anyways thanks/in/as part as of the response anyways etc to my prompt too but anyways etc... -->
			iGreatPeopleModifier = buildingInfo.getGreatPeopleRateModifier()
			iGlobalGreatPeopleModifier = buildingInfo.getGlobalGreatPeopleRateModifier()

			# Total modifier (local + global)
			iTotalGreatPeopleModifier = iGreatPeopleModifier + iGlobalGreatPeopleModifier

			if (iTotalGreatPeopleModifier != 0):
				szText1 = ""
				
				# Base modifier part
				if (iGreatPeopleModifier != 0):
					if (iGreatPeopleModifier > 0):
						szSign = "+"
					else:
						szSign = ""
					szText1 = szSign + str(iGreatPeopleModifier) + "%"
				
				# Global modifier part (if exists and different from base)
				if (iGlobalGreatPeopleModifier != 0):
					if (len(szText1) > 0):
						szText1 += ", "
					if (iGlobalGreatPeopleModifier > 0):
						szGlobalSign = "+"
					else:
						szGlobalSign = ""
					szText1 += szGlobalSign + str(iGlobalGreatPeopleModifier) + "% (Global)"

				szText2 = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR), szText1)
				fillCell(screen, szText2, x, y)
				x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)

		# Render Panels
		renderCells(screen, buildingInfo, columnWidth, self.X_STATS_PANE, self.Y_STATS_PANE)

		# <!-- custom: 6.2: now that textual and placeStats display is finished (minus Great People info), handle great people type's button display as a separate panel now, that overlaps with placeStats, and that is transparent in color background, using last grid coordinates while we have them, the inner placeStats logic -->
		def placeGreatPeopleStats(screen, buildingInfo):
			screen = self.top.getScreen()
			panelName = self.top.getNextWidgetName()
			greatPersonPanelTxtKey = ""

			buttonXOffset = 66
			# <!-- custom: slightly shift the button if button size (w and h) are higher than 32 to simulate a better centering effect towards the text of "+2" (great people count example) for example, the buttonYOffset = +2 if it were same value is purely coincidental value that suited us to center the button, no correlation or link at least voluntary anyways etc -->
			buttonYOffset = -2
			buttonW = 39
			buttonH = buttonW

			# Only proceed if this building affects great people rate
			if buildingInfo.getGreatPeopleRateChange() == 0:
				return
			
			# === PANEL SETUP ===
			setupPanel(screen, panelName, greatPersonPanelTxtKey, PanelStyles.PANEL_STYLE_EMPTY)

			#  First get the building's great person type (e.g., SPECIALIST_GREAT_MERCHANT)
			greatPersonType = buildingInfo.getGreatPeopleUnitClass()
			greatPersonButton = None

			if greatPersonType != -1:
				# Get the unit info for the great person type
				if self.top.iActivePlayer != -1:
					iGreatPersonUnit = gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationUnits(greatPersonType)
				else:
					iGreatPersonUnit = gc.getUnitClassInfo(greatPersonType).getDefaultUnitIndex()
				
				if iGreatPersonUnit != -1:
					greatPersonInfo = gc.getUnitInfo(iGreatPersonUnit)
					greatPersonButton = greatPersonInfo.getButton()

				# This approach uses a separate panel with both an button and text
				if greatPersonButton:
					buttonWidget = self.top.getNextWidgetName()
					screen.addDDSGFC(buttonWidget, greatPersonButton, 
									self.X_GREAT_PEOPLE_CHANGE_IN_GRID + buttonXOffset,  # X position 
									self.Y_GREAT_PEOPLE_CHANGE_IN_GRID + buttonYOffset,  # Y position
									buttonW, buttonH,  # Width and height of button
									WidgetTypes.WIDGET_GENERAL, -1, -1)

				# <!-- custom: else block below's code untested but probably works, i guess it covers case where great person type is not any of the great people's types if i am not mistaken like great scientist and great prophet and such, but really i have no idea or don'tknow too much maybe, so test to be sure, may or not work-function, hopefully does but in all cases anyways etc... -->
				else:
					# Just add text if no button
					textWidget = self.top.getNextWidgetName()
					textWithSymbol = u"%c  %s" % (CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR), gpRateText)
					screen.setLabelAt(textWidget, panelName, u"<font=3>%s</font>" % textWithSymbol, 
									CvUtil.FONT_LEFT_JUSTIFY, 
									self.X_GREAT_PEOPLE_CHANGE_IN_GRID + buttonXOffset - 10,  # X position <!-- custom: as text is smaller than button, the x offset can be a bit smaller most likely, to use space more efficiently, did not tets but hopefully should work well and not grind/eat away at our left "+2" (great people value example anyways etc), else shift back to the right as needed (by increasing this extra negative offset i added (- 10 in this example may not be accurate or updated anyways etc)  anyways etc) --> 
									self.Y_GREAT_PEOPLE_CHANGE_IN_GRID,  # Y position <!-- custom: no need for special centering effect then if i am not mistaken, did not test text display if no button is found but maybe works well or well enough hopefully anyways etc -->
									0, FontTypes.SMALL_FONT, 
									WidgetTypes.WIDGET_GENERAL, -1, -1)
					
		placeGreatPeopleStats(screen, buildingInfo)



	def displayPanelButtonsSNumsOrTxtsOrPanelSTxtKeyNoButton(self, screen, isButtonFound, txtKeyNoButtonFound, xNumsOrTextsFound, buttonSize, xPanel, yPanel, wPanel, hPanel):
		# <!-- custom: now display(ing anyways etc) the corresponding num or text matching the button if any (button) anyways etc -->
		if isButtonFound:
			yPanelBottomPart = yPanel + int(0.8 * hPanel)
			for xOccurenceFound, numFreeTxtOccurenceFound in xNumsOrTextsFound:
				textName = self.top.getNextWidgetName()
				szText = numFreeTxtOccurenceFound
				screen.addMultilineText(textName, szText, xOccurenceFound, yPanelBottomPart, 2 * buttonSize, hPanel - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		# If no <!-- custom: button --> found, display a message
		else:
			yPanelCenter = yPanel + (hPanel / 2)
			textName = self.top.getNextWidgetName()
			szText = CyTranslator().getText(txtKeyNoButtonFound, ())
			screen.addMultilineText(textName, szText, xPanel + 7, yPanelCenter, wPanel - 14, hPanel - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()

		# Create panel with proper styling
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50 )
		# <!-- custom: additionnal left side padding for the button(s) -->
		screen.attachLabel(panelName, "", "  ")

		# <!-- custom: store free items found results -->
		# <!-- custom: (Also) P(p)romotions and buildings don't grant a num of promotions or buildings so adjust logic for them too anyways etc. -->
		nCountOccurencesFound = 0
		xNumsOrTextsFound = []
		buttonSize = 64

		for iPrereq in range(gc.getNumTechInfos()):
			if isTechRequiredForBuilding(iPrereq, self.iBuilding):
				nCountOccurencesFound += 1
				# <!-- custom: no specific text, but respecting our structure to simplify code, not most efficient but maybe works at least for now if not always or not or and other or and not anyways etc -->
				# <!-- custom: store text position matching the button for later display as a text -->
				numFreeTxt = ""
				xSubstractedAdjustment = int(0.91 * buttonSize)
				xPanel = self.X_REQUIRES
				xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

				# <!-- custom: (but) attach button right now -->
				screen.attachImageButton( panelName, "", gc.getTechInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iPrereq, 1, False )

		iPrereq = gc.getBuildingInfo(self.iBuilding).getPrereqAndBonus()
		if (iPrereq >= 0):
			nCountOccurencesFound += 1
			numFreeTxt = ""
			xSubstractedAdjustment = int(0.91 * buttonSize)
			xPanel = self.X_REQUIRES
			xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

			screen.attachImageButton( panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False )

		for k in range(gc.getNUM_BUILDING_PREREQ_OR_BONUSES()):
			iPrereq = gc.getBuildingInfo(self.iBuilding).getPrereqOrBonuses(k)
			if (iPrereq >= 0):
				nCountOccurencesFound += 1
				numFreeTxt = ""
				xSubstractedAdjustment = int(0.91 * buttonSize)
				xPanel = self.X_REQUIRES
				xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

				screen.attachImageButton( panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False )

		iCorporation = gc.getBuildingInfo(self.iBuilding).getFoundsCorporation()
		bFirst = True
		if (iCorporation >= 0):
			for k in range(gc.getNUM_CORPORATION_PREREQ_BONUSES()):
				iPrereq = gc.getCorporationInfo(iCorporation).getPrereqBonus(k)
				if (iPrereq >= 0):
					if not bFirst:
						screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
					else:
						bFirst = False
					nCountOccurencesFound += 1
					numFreeTxt = ""
					xSubstractedAdjustment = int(0.91 * buttonSize)
					xPanel = self.X_REQUIRES
					xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

					screen.attachImageButton( panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False )

		iPrereq = gc.getBuildingInfo(self.iBuilding).getPrereqReligion()
		if (iPrereq >= 0):
			nCountOccurencesFound += 1
			numFreeTxt = ""
			xSubstractedAdjustment = int(0.91 * buttonSize)
			xPanel = self.X_REQUIRES
			xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

			screen.attachImageButton( panelName, "", gc.getReligionInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereq, -1, False )

		# Check for project requirements - New code for Manhattan Project and other projects
		buildingInfo = gc.getBuildingInfo(self.iBuilding)
		iSpecialBuildingType = buildingInfo.getSpecialBuildingType()
		
		# Check all projects to see if any enables this special building
		if (iSpecialBuildingType >= 0):
			# Display them with "OR" between if there are multiple
			bFirst = True

			for iProject in range(gc.getNumProjectInfos()):
				projectInfo = gc.getProjectInfo(iProject)
				if projectInfo.getEveryoneSpecialBuilding() == iSpecialBuildingType:			
					nCountOccurencesFound += 1
					numFreeTxt = ""
					xSubstractedAdjustment = int(0.91 * buttonSize)
					xPanel = self.X_REQUIRES
					xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))
					screen.attachImageButton(panelName, "", projectInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, iProject, -1, False)

					# Add "OR" text between projects
					if not bFirst:
						# <!-- custom: workaround as our code doesn't handle inconsistent occurence size (a button is 64px currently if not always or not anyways etc, but a label "or" would be smaller than 64px, messing the txtNums alignment of subsequent buttons (if any anyways etc), so to not rewrite all our code or tweak it too deeply, maybe this alternative solution is/can be quite elegant too instead, of putting the "or" label rather as a txtNum just between the buttons, and belonging to the new 2nd button we are adding (no "or" if first project so maybe more sensical or intuitive this way even though is still a hack but maybe not so bad or not or yes or and other or and not anyways etc anyways etc anyways etc...), not having thus to rewrite our otherwise working/functionning(functionnal?) code, anyways etc anyways etc anyways etc...
						# (Also) S(s)ince our next button is a project, if we were to use this "or", it is fine to be a bit more aggressive with the adjustment and place the txtNum right inbetween both buttons, as no txtNum will be left or right of this txtNum directly in contact with it and colliding or being merged in unintended way, so i quite like this elegant solution :) hehe if i may say, but anyways etc anyways etc anyways etc...
						#  -->
						#screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
						numFreeTxt = localText.getText("TXT_KEY_OR", ())
						xSubstractedAdjustment = int(1.27 * buttonSize)
						xPanel = self.X_REQUIRES
						xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

					bFirst = False

		# Check for required buildings
		# <!-- custom: see also for this part the note/code comment at top of this py file anyways etc -->

		buildingInfo = gc.getBuildingInfo(self.iBuilding)
		for i in range(gc.getNumBuildingClassInfos()):
			# Check if this building class is needed in the city
			if buildingInfo.isBuildingClassNeededInCity(i):
				# Get the default building of this class for the current civilization
				if self.top.iActivePlayer != -1:
					iDefaultBuilding = gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationBuildings(i)
				else:
					iDefaultBuilding = gc.getBuildingClassInfo(i).getDefaultBuildingIndex()
				
				# If a valid building exists, display its button
				if iDefaultBuilding != -1:
					nCountOccurencesFound += 1
					numFreeTxt = "InC"
					xSubstractedAdjustment = int(0.75 * buttonSize)
					xPanel = self.X_REQUIRES
					xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

					screen.attachImageButton(panelName, "", gc.getBuildingInfo(iDefaultBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iDefaultBuilding, -1, False)

		# Handle PrereqBuildingClasses (buildings needed across civilization)
		for i in range(gc.getNumBuildingClassInfos()):
			iNumRequired = 0
			iNumRequired = buildingInfo.getPrereqNumOfBuildingClass(i)
			
			if iNumRequired > 0:
				# Get the default building of this class for the current civilization
				if self.top.iActivePlayer != -1:
					iDefaultBuilding = gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationBuildings(i)
				else:
					iDefaultBuilding = gc.getBuildingClassInfo(i).getDefaultBuildingIndex()
				
				# If a valid building exists, display its button with number required
				if iDefaultBuilding != -1:
					nCountOccurencesFound += 1
					numFreeTxt = u"AllC %s+RM" % iNumRequired
					xSubstractedAdjustment = int(1.19 * buttonSize)
					xPanel = self.X_REQUIRES
					xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

					screen.attachImageButton(panelName, "", gc.getBuildingInfo(iDefaultBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iDefaultBuilding, -1, False)
					
					# Add a label showing the required number
					#screen.attachLabel(panelName, "", " x" + str(iNumRequired))

		# <!-- custom: display each relevant button's nums or/and txts if any, else if no button is found to display at all, display instead the no button found txtkey in all the panel.
		# Note: easy copy paste x, y, w, h, coordinates from panel creation is faster and perhaps more reliable too if you want (optionally) or/and need it or/and choose it or not but anyways etc anyways etc anyways etc... And i say this specifically after having written this (comment(ed)-out) advice and making the mistake here for example as well as in some other places despite having applied it correctly in some (other other but anyways etc anyways etc anyways etc...) places (for example _FREE_PBBS coordinates instead of _requires here but anyways etc anyways etc anyways etc...) anyways etc so now fixing it (!) if i may say but anyways etc anyways etc anyways etc..., (and)(but anyways etc anyways etc anyways etc...) so now applying this advice to me as well after noticing the numsOrTxts of the corresponding buttons are at wrong spot so hopefully helpful to me(!) (too but anyways etc anyways etc anyways etc...) if i may say but anyways etc anyways etc anyways etc... 
		# -->
		isButtonFound = (nCountOccurencesFound > 0)
		txtKeyNoButtonFound = "TXT_KEY_PEDIA_REQUIRES_NO_BUTTON_FOUND"
		self.displayPanelButtonsSNumsOrTxtsOrPanelSTxtKeyNoButton(screen, isButtonFound, txtKeyNoButtonFound, xNumsOrTextsFound, buttonSize, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES)


	# Shows buildings that require this building as a prerequisite
	def placeRequiredFor(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()

		nCountOccurencesFound = 0
		xNumsOrTextsFound = []
		buttonSize = 64

		# Create panel with proper styling
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_REQUIRED_FOR", ()), "", False, True, self.X_REQUIRED_FOR, self.Y_REQUIRED_FOR, self.W_REQUIRED_FOR, self.H_REQUIRED_FOR, PanelStyles.PANEL_STYLE_BLUE50)
		# Add padding
		screen.attachLabel(panelName, "", "  ")
		
		# Get the building class of our current building
		iCurrentBuildingClass = gc.getBuildingInfo(self.iBuilding).getBuildingClassType()
		
		# Loop through all buildings to check which ones require this building class
		for iLoopBuilding in range(gc.getNumBuildingInfos()):
			loopBuildingInfo = gc.getBuildingInfo(iLoopBuilding)
			
			# Check if this building is needed via BuildingClassNeededs
			if loopBuildingInfo.isBuildingClassNeededInCity(iCurrentBuildingClass):
				nCountOccurencesFound += 1
				numFreeTxt = "InC"
				xSubstractedAdjustment = int(0.75 * buttonSize)
				xPanel = self.X_REQUIRED_FOR
				xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

				screen.attachImageButton(panelName, "", loopBuildingInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iLoopBuilding, -1, False)
			
			# Check if this building is needed via PrereqBuildingClasses
			iNumRequired = loopBuildingInfo.getPrereqNumOfBuildingClass(iCurrentBuildingClass)
			if iNumRequired > 0:
				nCountOccurencesFound += 1
				numFreeTxt = u"AllC %s+RM" % iNumRequired
				xSubstractedAdjustment = int(1.19 * buttonSize)
				xPanel = self.X_REQUIRED_FOR
				xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

				screen.attachImageButton(panelName, "", loopBuildingInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iLoopBuilding, -1, False)

		isButtonFound = (nCountOccurencesFound > 0)
		txtKeyNoButtonFound = "TXT_KEY_PEDIA_REQUIRED_FOR_NO_BUTTON_FOUND"
		self.displayPanelButtonsSNumsOrTxtsOrPanelSTxtKeyNoButton(screen, isButtonFound, txtKeyNoButtonFound, xNumsOrTextsFound, buttonSize, self.X_REQUIRED_FOR, self.Y_REQUIRED_FOR, self.W_REQUIRED_FOR, self.H_REQUIRED_FOR)



	def placeObsoleteWith(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		
		# Create panel with proper styling
		screen.addPanel(panelName, CyTranslator().getText("TXT_KEY_PEDIA_OBSOLETE", ()), "", False, True, self.X_OBSOLETE_WITH, self.Y_OBSOLETE_WITH, self.W_OBSOLETE_WITH, self.H_OBSOLETE_WITH, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: additionnal left side padding for the button(s) -->
		screen.attachLabel(panelName, "", "  ")
		
		# Get the building info
		buildingInfo = gc.getBuildingInfo(self.iBuilding)
		
		# Check if the building has an obsolete tech directly <!-- custom: (i assume is about the obsoletetech info in (adjust to your mod path) for example C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Buildings\CIV4BuildingInfos.xml) -->
		iObsoleteTech = buildingInfo.getObsoleteTech()
	
		# If no direct obsolete tech, check if it's a special building type<!-- cus
		# <!-- custom: (e.g. the jewish monastery appears as never obsolete from the direct obsolete tech check due to <ObsoleteTech>NONE</ObsoleteTech>, but it does get obsolete at scientific method though in <ObsoleteTech>TECH_SCIENTIFIC_METHOD</ObsoleteTech> at (adjust with your mod path if different) for example C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Buildings\CIV4SpecialBuildingInfos.xml (now this file is/has been imported in AdvCiv-SAS as well in case we need to change it and to have all info we want and control it if i may say anyways etc anyways etc anyways etc...)) -->
		if iObsoleteTech == -1:
			iSpecialBuildingType = buildingInfo.getSpecialBuildingType()
			if iSpecialBuildingType != -1:
				# Get the special building info
				specialBuildingInfo = gc.getSpecialBuildingInfo(iSpecialBuildingType)
				# Check if the special building has an obsolete tech
				iObsoleteTech = specialBuildingInfo.getObsoleteTech()

		# <!-- custom: after having checked both directly for an obsolete tech, or indirectly through special buiding, now display button if any:
		if iObsoleteTech != -1:
			screen.attachImageButton(panelName, "", gc.getTechInfo(iObsoleteTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iObsoleteTech, -1, False)

		else:
			# <!-- custom: prettier display -->
			#screen.attachLabel(panelName, "", CyTranslator().getText("TXT_KEY_PEDIA_NEVER_OBSOLETE", ()))
			yPanelCenter = self.Y_OBSOLETE_WITH + (self.H_OBSOLETE_WITH / 2)
			textName = self.top.getNextWidgetName()
			szText = CyTranslator().getText("TXT_KEY_PEDIA_OBSOLETE_NO_BUTTON_FOUND", ())
			screen.addMultilineText(textName, szText, self.X_OBSOLETE_WITH + 7, yPanelCenter, self.W_OBSOLETE_WITH - 14, self.H_OBSOLETE_WITH - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeFreePBBS(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		
		# Create panel with proper styling
		screen.addPanel(panelName, CyTranslator().getText("TXT_KEY_PEDIA_FREE_PBBS", ()), "", False, True, self.X_FREE_PBBS, self.Y_FREE_PBBS, self.W_FREE_PBBS, self.H_FREE_PBBS, PanelStyles.PANEL_STYLE_BLUE50)
		# Additional left side padding for the button(s)
		screen.attachLabel(panelName, "", "  ")
		
		nCountOccurencesFound = 0
		xNumsOrTextsFound = []
		buttonSize = 64
		xSubstractedAdjustmentNums = 0.61

		# Get the building info
		buildingInfo = gc.getBuildingInfo(self.iBuilding)

		# Check if the building grants a free promotion<!-- custom: , and attach(or /"display" maybe indeed too anyways etc anyways etc anyways etc as ClaudeAI said anyways etc its button if there is any/a (free promotion) -->
		iFreePromotion = buildingInfo.getFreePromotion()
		if iFreePromotion != -1:
			# <!-- custom: store text position matching the button for later display as a text -->
			nCountOccurencesFound += 1
			numFreeTxt = "All Un.C"
			xSubstractedAdjustment = int(1.04 * buttonSize)
			xPanel = self.X_FREE_PBBS
			xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

			# <!-- custom: (but) attach button right now -->
			screen.attachImageButton(panelName, "", gc.getPromotionInfo(iFreePromotion).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFreePromotion, -1, False)
		
		# Check if the building grants a free building
		iFreeBuildingClass = buildingInfo.getFreeBuildingClass()
		if iFreeBuildingClass != -1:
			nCountOccurencesFound += 1
			numFreeTxt = "All Cs"
			xSubstractedAdjustment = int(0.87 * buttonSize)
			xPanel = self.X_FREE_PBBS
			xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

			# Get the default building of this class for the current civilization
			if self.top.iActivePlayer != -1:
				iDefaultBuilding = gc.getCivilizationInfo(gc.getPlayer(self.top.iActivePlayer).getCivilizationType()).getCivilizationBuildings(iFreeBuildingClass)
			else:
				iDefaultBuilding = gc.getBuildingClassInfo(iFreeBuildingClass).getDefaultBuildingIndex()
			
			# If a valid building exists, display its button
			if iDefaultBuilding != -1:
				screen.attachImageButton(panelName, "", gc.getBuildingInfo(iDefaultBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iDefaultBuilding, -1, False)

		# Check if the building grants a free bonus
		iFreeBonus = buildingInfo.getFreeBonus()
		iNumFreeBonuses = buildingInfo.getNumFreeBonuses()
		
		if iFreeBonus != -1:
			# <!-- custom: store text position matching the button for later display as a text -->
			nCountOccurencesFound += 1

			# <!-- custom: note: for freebonus, done according to according to kujira's website if i am not mistaken anyways etc, in https://gforestshade.github.io/kujira/post/civ4buildinginfos/#inumfreebonuses (translated to english with google chrome), see also "for freebonus, done according to kujira's website" note/code comment at top of this py file if need(ed? But or not but or yes but or etc but anyways etc anyways etc anyways etc) anyways etc:
			# based on this, displaying free bonus if >= 1 or if == -1, adjusting display depending on this
			# -->

			if iNumFreeBonuses == -1:
				numFreeTxt = "RM"
				xSubstractedAdjustment = int(0.74 * buttonSize)
			elif iNumFreeBonuses >= 1:
				numFreeTxt = u"%s" % (iNumFreeBonuses)
				xSubstractedAdjustment = int(xSubstractedAdjustmentNums * buttonSize)
			else:
				raise ValueError("[FATAL] Unexpected iNumFreeBonuses=%d value out of bounds iNumFreeBonuses == -1 or iNumFreeBonuses >=1, please verify the code and iNumFreeBonuses are behaving as intended and adjust this sevopedia code or/and your mod code based on this as you want/prefer anyways etc. Note: for info str(FreeBonus) (for display in this error message anyways etc)=%s anyways etc." % (iNumFreeBonuses, str(iFreeBonus)))
			
			xPanel = self.X_FREE_PBBS
			xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

			# <!-- custom: (but) attach button right now -->
			screen.attachImageButton(panelName, "", gc.getBonusInfo(iFreeBonus).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iFreeBonus, -1, False)
			
		# Check if the building grants free specialists - simpler approach
		for iSpecialist in range(gc.getNumSpecialistInfos()):
			if buildingInfo.getFreeSpecialistCount(iSpecialist) > 0:
				# <!-- custom: store text position matching the button for later display as a text -->
				nCountOccurencesFound += 1
				iSpecialistCount = buildingInfo.getFreeSpecialistCount(iSpecialist)
				numFreeTxt = u"%s" % (iSpecialistCount)
				xSubstractedAdjustment = int(xSubstractedAdjustmentNums * buttonSize)
				xPanel = self.X_FREE_PBBS
				xNumsOrTextsFound.append((getXOccurenceFound(xPanel, self.HYPOTHESIZED_FIRST_BUTTON_LEFT_PADDING, self.HYPOTHESIZED_INTER_BUTTON_SPACING, nCountOccurencesFound, buttonSize, xSubstractedAdjustment), numFreeTxt))

				# <!-- custom: (but) attach button right now -->
				screen.attachImageButton(panelName, "", gc.getSpecialistInfo(iSpecialist).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPECIALIST, iSpecialist, -1, False)

		isButtonFound = (nCountOccurencesFound > 0)
		txtKeyNoButtonFound = "TXT_KEY_PEDIA_FREE_PBBS_NO_BUTTON_FOUND"
		self.displayPanelButtonsSNumsOrTxtsOrPanelSTxtKeyNoButton(screen, isButtonFound, txtKeyNoButtonFound, xNumsOrTextsFound, buttonSize, self.X_FREE_PBBS, self.Y_FREE_PBBS, self.W_FREE_PBBS, self.H_FREE_PBBS)

		# <!-- custom: see also the "For (/to) parsing (parse?)" note/code comment and/or the "example of how to directly import a button path" at top of this py file if need(ed?) but or not or yes but but anyways etc anyways etc anyways etc -->

	# Helper function to determine if a building is civ-specific (unique)
	def isBuildingUnique(self, iBuildingIndex):

		buildingInfo = gc.getBuildingInfo(iBuildingIndex)
		buildingClassInfo = gc.getBuildingClassInfo(buildingInfo.getBuildingClassType())
		
		# A building is unique if it's not the default building for its class
		defaultBuildingForClass = buildingClassInfo.getDefaultBuildingIndex()
		return iBuildingIndex != defaultBuildingForClass


	# Helper function to get which civ a unique building belongs to
	def getBuildingCiv(self, iBuildingIndex):
		buildingInfo = gc.getBuildingInfo(iBuildingIndex)
		buildingClassType = buildingInfo.getBuildingClassType()
		
		# Check all civs to see which one has this building as their unique version
		for iCiv in range(gc.getNumCivilizationInfos()):
			civInfo = gc.getCivilizationInfo(iCiv)
			civBuildingForClass = civInfo.getCivilizationBuildings(buildingClassType)
			if civBuildingForClass == iBuildingIndex:
				return iCiv
		return -1  # Should not happen for unique buildings


	# Helper function to check if a building class has any unique versions
	def buildingClassHasUniqueVersions(self, buildingClassType):

		buildingClassInfo = gc.getBuildingClassInfo(buildingClassType)
		defaultBuilding = buildingClassInfo.getDefaultBuildingIndex()
		
		# Check if any civ has a different building for this class
		for iCiv in range(gc.getNumCivilizationInfos()):
			civInfo = gc.getCivilizationInfo(iCiv)
			civBuildingForClass = civInfo.getCivilizationBuildings(buildingClassType)
			if civBuildingForClass != defaultBuilding:
				return True
		return False



	def placeFreeWith(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		
		# Create panel with proper styling
		screen.addPanel(panelName, CyTranslator().getText("TXT_KEY_PEDIA_FREE_WITH", ()), "", False, True, self.X_FREE_WITH, self.Y_FREE_WITH, self.W_FREE_WITH, self.H_FREE_WITH, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: additional left side padding for the button(s) -->
		screen.attachLabel(panelName, "", "  ")
		
		# Get the current building info
		currentBuildingInfo = gc.getBuildingInfo(self.iBuilding)
		currentBuildingClass = currentBuildingInfo.getBuildingClassType()
		
		# <!-- custom: handle no building found message -->
		isButtonFound = False
		
		# Check if current building is civ-specific (unique)
		currentIsUnique = self.isBuildingUnique(self.iBuilding)
		if currentIsUnique:
			currentCiv = self.getBuildingCiv(self.iBuilding)
		else:
			currentCiv = -1
		
		# Check if there are any unique versions of the current building
		hasUniqueVersions = self.buildingClassHasUniqueVersions(currentBuildingClass)

		# Check all buildings to see which ones provide this building for free
		for iBuildingLoop in range(gc.getNumBuildingInfos()):
			buildingInfo = gc.getBuildingInfo(iBuildingLoop)
			
			# Check if this building provides our current building for free
			freeBuildingClass = buildingInfo.getFreeBuildingClass()
			if freeBuildingClass == currentBuildingClass:
				providerIsUnique = self.isBuildingUnique(iBuildingLoop)
				if providerIsUnique:
					providerCiv = self.getBuildingCiv(iBuildingLoop)
				else:
					providerCiv = -1
				
				# Determine if we should show this provider based on the logic:
				shouldShow = False
				
				if currentIsUnique:
					# Current building is unique - only show providers that this civ can actually use
					if not providerIsUnique or providerCiv == currentCiv:
						shouldShow = True
				else:
					# Current building is generic
					if hasUniqueVersions:
						# Generic building has unique versions - only show generic providers
						if not providerIsUnique:
							shouldShow = True
					else:
						# No unique versions exist - show all providers
						shouldShow = True
				
				if shouldShow:
					isButtonFound = True
					screen.attachImageButton(panelName, "", gc.getBuildingInfo(iBuildingLoop).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuildingLoop, -1, False)

		if not isButtonFound:
			# <!-- custom: prettier display when no buildings provide this one for free -->
			yPanelCenter = self.Y_FREE_WITH + (self.H_FREE_WITH / 2)
			textName = self.top.getNextWidgetName()
			szText = CyTranslator().getText("TXT_KEY_PEDIA_FREE_WITH_NO_BUTTON_FOUND", ())
			screen.addMultilineText(textName, szText, self.X_FREE_WITH + 7, yPanelCenter, self.W_FREE_WITH - 14, self.H_FREE_WITH - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeReplace(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()

		iBuildingClass = gc.getBuildingInfo(self.iBuilding).getBuildingClassType()
		iBaseBuilding = gc.getBuildingClassInfo(iBuildingClass).getDefaultBuildingIndex()

		# Use different text key depending on whether this is a unique or base building
		if self.iBuilding != iBaseBuilding:
			# This is a unique building that replaces a base building
			panelTxtKey = "TXT_KEY_PEDIA_REPLACE_REPLACES_CUSTOM"
		else:
			# This is a base building that can be replaced by unique buildings
			panelTxtKey = "TXT_KEY_PEDIA_REPLACE_REPLACED_BY_CUSTOM"

		# Create panel with proper styling
		screen.addPanel(panel, CyTranslator().getText(panelTxtKey, ()), "", False, True, self.X_REPLACE, self.Y_REPLACE, self.W_REPLACE, self.H_REPLACE, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: additionnal left side padding for the button(s) -->
		screen.attachLabel(panel, "", "  ")

		# <!-- custom: handle no building found message -->
		isButtonFound = False

		# If this is a unique (i.e.civ-specific) building, show the base building it replaces
		if self.iBuilding != iBaseBuilding:
			isButtonFound = True
			screen.attachImageButton(panel, "", gc.getBuildingInfo(iBaseBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBaseBuilding, 1, False)
			return

		else:
			# If this is the base building, show all unique (i.e.civ-specific) buildings that replace it
			for iBuilding in xrange(gc.getNumBuildingInfos()):
				if self.iBuilding != iBuilding and not gc.getBuildingInfo(iBuilding).isGraphicalOnly():
					if iBuildingClass == gc.getBuildingInfo(iBuilding).getBuildingClassType():
						isButtonFound = True
						screen.attachImageButton(panel, "", gc.getBuildingInfo(iBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1, False)

		if not isButtonFound:
			yPanelCenter = self.Y_REPLACE + (self.H_REPLACE / 2)
			textName = self.top.getNextWidgetName()
			szText = CyTranslator().getText("TXT_KEY_PEDIA_REPLACE_NO_BUTTON_FOUND", ())
			screen.addMultilineText(textName, szText, self.X_REPLACE + 7, yPanelCenter, self.W_REPLACE - 14, self.H_REPLACE - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	# <!-- custom: if i am not mistaken this handles several civs sharing a special building/unit, see screenshot 3068 in the drive for example where the building mall as a test anyways etc is shared between both civilization American empire and Mali empire for example or/and for details or/and other source or maybe rather too as well test it yourself or not if need(ed) or other or etc anyways etc ; we reduced width to 84px or some smaller width value because it is unlikely we use this feature in advciv-sas (simpler if one civ has one civ-specific unit and civ-specific building unique to them, but it is in theory possible like other mods do if i am not mistaken to share them across several civs, hence the name "civs" even though width is so small (i assume it would scroll if more than oen button too so display is not lost or not or yes or other or etc anyways etc --> 
	def placeCivilizations(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()

		# Create panel with proper styling
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_CIVILIZATIONS", ()), "", False, True, self.X_CIVILIZATIONS, self.Y_CIVILIZATIONS, self.W_CIVILIZATIONS, self.H_CIVILIZATIONS, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: additionnal left side padding for the button(s) -->
		screen.attachLabel(panelName, "", "  ")
		
		# Get building class info
		iBuildingClass = gc.getBuildingInfo(self.iBuilding).getBuildingClassType()
		iDefaultBuilding = gc.getBuildingClassInfo(iBuildingClass).getDefaultBuildingIndex()

		# Check if this is a unique (i.e.civ-specific) building (not the default building for its class)
		bIsUnique = (self.iBuilding != iDefaultBuilding)

		# If this is a unique (i.e.civ-specific) building, show which civ can build it
		if bIsUnique:
			# Find which civ has this unique (i.e.civ-specific) building
			for iCiv in range(gc.getNumCivilizationInfos()):
				# <!-- custom: include barbarians and perhaps other non playable civs in the display for example for the/to display the anyways etc barbarian palace, barbarian granary (so comment out the isPlayable check as Claude AI explained indeed and that i implemented in a simpler manner thanks to its explanation but anyways etc, but also unindent the below below too anyways etc), or/and other civs or not if such exist or not or and other or yes or and not or yes but anyways etc -->
				#if gc.getCivilizationInfo(iCiv).isPlayable():
				iCivBuilding = gc.getCivilizationInfo(iCiv).getCivilizationBuildings(iBuildingClass)
				if iCivBuilding == self.iBuilding:
					screen.attachImageButton(panelName, "", gc.getCivilizationInfo(iCiv).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCiv, -1, False)
		# If this is the default building, show "Available to all civilizations"
		else:
			# <!-- custom: prettier display -->
			#screen.attachLabel(panelName, "", localText.getText("TXT_KEY_PEDIA_AVAILABLE_ALL_CIVS", ()))
			yPanelCenter = self.Y_CIVILIZATIONS + (self.H_CIVILIZATIONS / 2)
			textName = self.top.getNextWidgetName()
			szText = CyTranslator().getText("TXT_KEY_PEDIA_CIVILIZATIONS_NO_BUTTON_FOUND", ())
			screen.addMultilineText(textName, szText, self.X_CIVILIZATIONS + 7, yPanelCenter, self.W_CIVILIZATIONS - 14, self.H_CIVILIZATIONS - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getBuildingHelp(self.iBuilding, True, False, False, None)[1:]
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL+5, self.Y_SPECIAL+30, self.W_SPECIAL-10, self.H_SPECIAL-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeBuildingAnimation(self):
		screen = self.top.getScreen()	
		screen.addBuildingGraphicGFC(self.top.getNextWidgetName(), self.iBuilding, self.X_BUILDING_ANIMATION, self.Y_BUILDING_ANIMATION, self.W_BUILDING_ANIMATION, self.H_BUILDING_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_BUILDING_ANIMATION, self.Z_ROTATION_BUILDING_ANIMATION, self.SCALE_ANIMATION, True)



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# <!-- custom: same reasoning as for/in SevopediaUnit.py, i don't need the redundant background -->
		#screen.addPanel( panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.addPanel( panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50 )
		textName = self.top.getNextWidgetName()
		szText = u""
		# <!-- custom: too much hassle/"nightmare" to maintain the strategy texts in history panel (which i agree with), + also often inaccurate, especially if someone were to make a mod, just ignoring them without importing the XML assets as well is much more efficient, more reliable, and perhaps clearer in the sevopedia too maybe. -->
		# if len(gc.getBuildingInfo(self.iBuilding).getStrategy()) > 0:
		#	szText += localText.getText("TXT_KEY_CIVILOPEDIA_STRATEGY", ())
		#	szText += gc.getBuildingInfo(self.iBuilding).getStrategy()
		#	szText += u"\n\n"
		# <!-- custom: same reasoning as for/in SevopediaUnit.py, i don't need the redundant background -->
		#szText += localText.getText("TXT_KEY_CIVILOPEDIA_BACKGROUND", ())
		szText += gc.getBuildingInfo(self.iBuilding).getCivilopedia()
		# <!-- custom: but here we also restore/add padding -->
		#screen.addMultilineText( textName, szText, self.X_HISTORY + 15, self.Y_HISTORY + 40, self.W_HISTORY - (15 * 2), self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		#screen.addMultilineText( textName, szText, self.X_HISTORY + 7, self.Y_HISTORY + 10, self.W_HISTORY - (15 * 2), self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(textName, szText, self.X_HISTORY + 7, self.Y_HISTORY + 10 + self.H_ADJUST_Y_AFTER_ANIMATION_NO_HEADER, self.W_HISTORY - 30, self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def getBuildingType(self, iBuilding):
		if (isWorldWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			return 2
		elif (isNationalWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			return 1
		else:
			return 0



	def getBuildingSortedList(self, iBuildingType):
		list1 = []
		numInfos = 0
		for iBuilding in range(gc.getNumBuildingInfos()):
			if (self.getBuildingType(iBuilding) == iBuildingType):
				list1.append(iBuilding)
				numInfos += 1
		list2 = [(0,0)] * numInfos
		i = 0
		for iBuilding in list1:
			list2[i] = (gc.getBuildingInfo(iBuilding).getDescription(), iBuilding)
			i += 1
		if self.top.isSortLists():
			list2.sort()
		return list2



	def handleInput (self, inputClass):
		return 0

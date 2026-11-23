
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

from CvPythonExtensions import *
# <!-- custom: Route shared visual resources through the centralized SASVisualUtils namespace after retiring overlapping helper/cache imports; keep one canonical visual-resource boundary. (ChatGPT-5.6-Sol) -->
import SASVisualUtils as SASVisuals
# <!-- custom: SASTextScale sizes the table's text with the other SAS screens, as AGENTS.md asks instead of fixed <font=2> tags. See KI#1107. (Claude code Opus 5.5) -->
import SASTextScale
import CvUtil
import ScreenInput
import CvScreenEnums
gc = CyGlobalContext()

# advc.gfd: Main class of Nightinggale's GameFont Display component
class GameFontDisplay:
	def __init__(self):
		return

	def interfaceScreen(self):
		screen = CyGInterfaceScreen("GameFontDisplayScreen", CvScreenEnums.GAMEFONT_DISPLAY_SCREEN)

		nScreenWidth = screen.getXResolution()
		nScreenHeight = screen.getYResolution()

		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		szTableName = "GameFontTable"

		# <!-- custom: Was a 744 px table centred on the screen, with 56 px for ID, Small, Big and Button, which cut "Button" to "Butt..." at the label font, 500 for Type and 20 px buttons; at 1920 px it left most of the screen empty (the user, 2026-11-23).
		# Now the table fills the screen less a 40 px margin each side, ID and Button take 100 px each and each font size 200, for headers such as "3 (Body, Label, Title)", Type the rest less the scrollbar's 20, and buttons are 24 px, the rows' height: 32 px buttons overlapped the rows, which setTableRowHeight did not grow. See KI#1107. (Claude code Opus 5.5) -->
		iMargin = 40
		iNarrowColW = 100
		iGlyphColW = 200
		# <!-- custom: Was two glyph columns, Small at <font=2> and Big at <font=4>; now one per font size 1 to 4, as the user asked, each header naming the SAS font types its size has now, such as "3 (Body, Label)", read from the defines.
		# Each glyph cell keeps its fixed size, as showing that size is the column's purpose: sizes up to 2 draw from GameFont_75.tga and larger ones from GameFont.tga, and a SASTextScale label font in the old Small column turned its glyphs to GameFont.tga's, so rows 425 to 431, which only GameFont_75.tga fills, went blank (2026-11-23). See KI#1107. (Claude code Opus 5.5) -->
		aiFontSizes = [1, 2, 3, 4]
		aszSASFonts = [("Tiny", SASTextScale.getSASUIFontTiny()), ("Body", SASTextScale.getSASUIFontBody()), ("Label", SASTextScale.getSASUIFontLabel()), ("Title", SASTextScale.getSASUIFontTitle()), ("Hover", SASTextScale.getSASUIFontHover())]
		iButtonCol = 1 + len(aiFontSizes)
		iTypeCol = iButtonCol + 1
		nTableWidth = nScreenWidth - 2 * iMargin
		iTypeColW = nTableWidth - 2 * iNarrowColW - len(aiFontSizes) * iGlyphColW - 20
		nTableHeight = nScreenHeight
		iButtonSize = 24

		screen.addTableControlGFC(szTableName, iTypeCol + 1, iMargin, 0, nTableWidth, nTableHeight, True, False, iButtonSize, iButtonSize, TableStyles.TABLE_STYLE_STANDARD )
		# <!-- custom: Was <font=2> text closed by a malformed <font/>; the ID, Button and Type text now take SASTextScale's label font with a proper </font>. See KI#1107. (Claude code Opus 5.5) -->
		screen.setTableColumnHeader( szTableName, 0, SASTextScale.sasFontTagLabel + u"ID" + SASTextScale.SAS_FONT_TAG_CLOSE, iNarrowColW)
		for iCol in range(len(aiFontSizes)):
			aszNames = []
			for (szName, iSize) in aszSASFonts:
				if iSize == aiFontSizes[iCol]:
					aszNames.append(szName)
			szHeader = u"%d" % aiFontSizes[iCol]
			if aszNames:
				szHeader += u" (" + u", ".join(aszNames) + u")"
			screen.setTableColumnHeader( szTableName, 1 + iCol, SASTextScale.sasFontTagLabel + szHeader + SASTextScale.SAS_FONT_TAG_CLOSE, iGlyphColW)
		screen.setTableColumnHeader( szTableName, iButtonCol, SASTextScale.sasFontTagLabel + u"Button" + SASTextScale.SAS_FONT_TAG_CLOSE, iNarrowColW)
		screen.setTableColumnHeader( szTableName, iTypeCol, SASTextScale.sasFontTagLabel + u"Type" + SASTextScale.SAS_FONT_TAG_CLOSE, iTypeColW)

		# <!-- custom: Was iMax = FontSymbols.MAX_NUM_SYMBOLS + getSymbolID(HAPPY_CHAR) - 8193 + 49 with rows past 280 shifted by 8193, which assumes the symbols' codes start near 8193.
		# Here getSymbolID(HAPPY_CHAR) returned 450 (2026-11-23, a diagnostic print), so iMax was -7667 and no row was drawn, silently, in SAS and in base AdvCiv 1.14 alike (Ctrl + Shift + F1, Debug Mode).
		# Now the symbols start where CvGameTextMgr::assignFontIds put the first yield, its iFirstSymbolCode (256 here): rows 0 to 280 hold the letters, then the symbols follow directly when they start above them, or the rows run straight through when they start lower, up to the last symbol plus the same 49.
		# A first fix kept the 8193 jump for any first symbol above 8193, which Codex found draws only 77 rows at 8194; the first yield's code fits every layout, though the inherited 8483 one now starts its symbols at row 281 rather than 8474's empty codes before them. See KI#1107. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		iLetterRows = 281
		iFirstSymbol = SASVisuals.Yield.ordinal(YieldTypes.YIELD_FOOD)
		iEnd = int(FontSymbols.MAX_NUM_SYMBOLS) + SASVisuals.Font.ordinal(FontSymbols.HAPPY_CHAR) + 49 # advc: was 8483+10
		iJump = 0
		if iFirstSymbol > iLetterRows:
			iJump = iFirstSymbol - iLetterRows
		iMax = iEnd - iJump
		self.buildInfoPointers()
		for iLine in range(iMax):
			# <advc> Include letters. Their ID go up to the mid 250s; far lower than the icon IDs.
			iID = iLine
			if iJump > 0 and iID >= iLetterRows:
				iID += iJump # was +8483 </advc>
			screen.appendTableRow(szTableName)
			screen.setTableInt(szTableName, 0, iLine, SASTextScale.sasFontTagLabel + unicode(iID) + SASTextScale.SAS_FONT_TAG_CLOSE, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
			for iCol in range(len(aiFontSizes)):
				screen.setTableInt(szTableName, 1 + iCol, iLine, (u"<font=%d>" % aiFontSizes[iCol]) + (u" %c" % (iID)) + SASTextScale.SAS_FONT_TAG_CLOSE, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

			infoPointer = self.getInfoPointerFromGameFont(iID)

			if infoPointer is not None:
				if isinstance(infoPointer, str):
					screen.setTableInt(szTableName, iTypeCol, iLine, SASTextScale.sasFontTagLabel + infoPointer + SASTextScale.SAS_FONT_TAG_CLOSE, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
				else:
					szButton = infoPointer.getButton()
					if szButton != "" and szButton != SASVisuals.StaticArt.BOMB_SHELTERS_BUTTON:
						screen.setTableRowHeight(szTableName, iLine, iButtonSize)
						screen.setTableText(szTableName, iButtonCol, iLine, "", szButton, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
					screen.setTableInt(szTableName, iTypeCol, iLine, SASTextScale.sasFontTagLabel + infoPointer.getType() + SASTextScale.SAS_FONT_TAG_CLOSE, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )

	# <!-- custom: Was four searches per row with .index() on SASVisuals' cached tuples, which Python 2.4 tuples lack (it came in 2.6): once the rows drew again, the first row raised "AttributeError: 'tuple' object has no attribute 'index'" (2026-11-23); base AdvCiv searched lists.
	# Now one dict from character code to entry, built once per call of interfaceScreen, keeping the old order of precedence: religion, corporation, bonus, then the built-in symbols (advc.002f added BULL's CITIZEN, GREAT_GENERAL and AIRPORT). See KI#1107.2. (Claude code Opus 5.5) -->
	def buildInfoPointers(self):
		self.dInfoPointers = {}
		for (aiOrdinals, getInfo) in ((SASVisuals.Religion.ordinals(), gc.getReligionInfo), (SASVisuals.Corporation.ordinals(), gc.getCorporationInfo), (SASVisuals.Bonus.ordinals(), gc.getBonusInfo)):
			for iInfo in range(len(aiOrdinals)):
				if aiOrdinals[iInfo] not in self.dInfoPointers:
					self.dInfoPointers[aiOrdinals[iInfo]] = getInfo(iInfo)
		aszChars = SASVisuals.Font.chars()
		for iSymbol in range(len(aszChars)):
			if ord(aszChars[iSymbol]) not in self.dInfoPointers:
				self.dInfoPointers[ord(aszChars[iSymbol])] = SASVisuals.BUILTIN_FONT_SYMBOL_NAMES[iSymbol]

	def getInfoPointerFromGameFont(self, iIndex):
		return self.dInfoPointers.get(iIndex)

	def handleInput (self, inputClass):
		return 0

	def update(self, fDelta):
		return 1

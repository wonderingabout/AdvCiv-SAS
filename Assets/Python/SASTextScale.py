# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md).

from CvPythonExtensions import *
import re
# <!-- custom: Use the leaf logging module directly for structured font-size diagnostics; importing CvUtil here would create CvUtil -> SASTextScale -> CvUtil. (ChatGPT-5.6-Sol) -->
import SASPythonLogging
# <!-- custom: SASCurrentDefines reads the font sizes through one cache that SASLiveDefineOverrides empties when it changes a define, and the bridge's change count tells the font tags below to rebuild; both are leaf modules, so this adds no cycle. See KI#128.5. (Claude code Opus 5.5) -->
import SASCurrentDefines
import SASLiveDefineOverridesBridge

gc = CyGlobalContext()

# <!-- custom: Keep SAS text-size defines/tags with the text-scaling helpers that consume them.
# They formerly lived in SASFontUtils and briefly in the broader UI-resource cache; neither icon/glyph nor art-resource code should be imported merely to format text. (ChatGPT-5.6-Sol) -->
# <!-- custom: The sizes themselves were kept here in _SAS_UI_FONT_SIZE_CACHE, emptied on each override change; SASCurrentDefines now keeps them for every reader, and only which defines were logged is kept here.
# An out-of-range size was cached as None after its first error, so later tags silently lost their size; it now raises at each read, as a bad value should stay loud. See KI#128.5. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
_SAS_UI_FONT_SIZE_LOGGED = {}
_SAS_UI_FONT_PREVIEW = {}

def _getSASUIFontSize(szDefineName):
	# <!-- custom: A preview set by setUIFontPreview, such as SASPilot's uifont, wins over the define for this session; merging main's live define overrides kept it first, before the shared SASCurrentDefines read. (Claude code Opus 5.5) -->
	if szDefineName in _SAS_UI_FONT_PREVIEW:
		return _SAS_UI_FONT_PREVIEW[szDefineName]
	iSize = SASCurrentDefines.getInt(szDefineName)
	if iSize < 1 or iSize > 4:
		raise RuntimeError("SASTextScale: %s=%d out of [1,4] - check GlobalDefines_advciv_sas.xml and SASLiveDefineOverrides.txt" % (szDefineName, iSize))
	# <!-- custom: Font-size resolution is deterministic per define/run, so expose the define and resolved size as searchable fields instead of ad-hoc prose. (ChatGPT-5.6-Sol) -->
	# <!-- custom: Logged once per define, as before overrides: a draft logged each new size, which repeated what SASLiveDefineOverridesBridge's SAS_LIVE_DEFINE_OVERRIDES row already records where the override is set; the user wanted one central log of overrides rather than one per reader (2026-11-26). See KI#128.5. (Claude code Opus 5.5) -->
	if szDefineName not in _SAS_UI_FONT_SIZE_LOGGED:
		_SAS_UI_FONT_SIZE_LOGGED[szDefineName] = iSize
		SASPythonLogging.writeRecord("UI_FONT_SIZE_RESOLVED", "define=%s size=%d" % (szDefineName, iSize))
	return iSize


def getSASUIFontTiny():
	return _getSASUIFontSize("SAS_UI_FONT_TINY")


def getSASUIFontBody():
	return _getSASUIFontSize("SAS_UI_FONT_BODY")


def getSASUIFontLabel():
	return _getSASUIFontSize("SAS_UI_FONT_LABEL")


def getSASUIFontTitle():
	return _getSASUIFontSize("SAS_UI_FONT_TITLE")


class _DynamicFontTag:
	def __init__(self, szDefineName, bBold=False):
		self.szDefineName = szDefineName
		self._isBold = bBold
		self._cachedTag = None
		self._iBuiltChangeCount = 0
		if not bBold:
			self.bold = _DynamicFontTag(szDefineName, True)

	def _build(self):
		# <!-- custom: Main interface hovers keep these tag objects for the session, so a tag is built again once SASLiveDefineOverrides changed a define. See KI#128.5. (Claude code Opus 5.5) -->
		iChangeCount = SASLiveDefineOverridesBridge.getChangeCount()
		if iChangeCount != self._iBuiltChangeCount:
			self._cachedTag = None
			self._iBuiltChangeCount = iChangeCount
		if self._cachedTag is not None:
			return self._cachedTag
		iSize = _getSASUIFontSize(self.szDefineName)
		# <!-- custom: The empty tag for a size cached as None went with that cache, as an out-of-range size now raises instead. See KI#128.5. (Claude code Opus 5.5) -->
		if self._isBold:
			self._cachedTag = u"<font=%db>" % iSize
		else:
			self._cachedTag = u"<font=%d>" % iSize
		return self._cachedTag

	def __unicode__(self):
		return self._build()

	def __str__(self):
		return self._build().encode("ascii")

	def __add__(self, szOther):
		return self._build() + szOther

	def __radd__(self, szOther):
		return szOther + self._build()


SAS_FONT_TAG_CLOSE = u"</font>"

# <!-- custom: Note: there is no hover tag; hover text uses the label tag.
# A hover define of its own had the label's value, and the user retired it on 2026-11-26, as raising the label meant remembering to raise hover too, while hover always wanted the label's size.
# See Docs/Deprecated/global_define_names.md. (Claude code Opus 5.5) -->
sasFontTagTiny = _DynamicFontTag("SAS_UI_FONT_TINY")
sasFontTagBody = _DynamicFontTag("SAS_UI_FONT_BODY")
sasFontTagLabel = _DynamicFontTag("SAS_UI_FONT_LABEL")
sasFontTagTitle = _DynamicFontTag("SAS_UI_FONT_TITLE")

# <!-- custom: SASPilot can preview the Python layout fonts within one game session.
# Native widget tooltips do not follow the preview: since main's live define overrides (merged 2026-11-27), CvDLLWidgetData reads the label size from the define cache at each hover, while the preview stays in Python; the DLL no longer caches its own hover size. (GPT-6.2-Sol + Claude code Opus 5.5) -->
# <!-- custom: Not gated on SASPilot's switch: nothing changes until a caller sets a preview, and another caller, such as an in-game font option shown live, could use it too; SASPilot's uifont is the first. (Claude code Opus 5.5) -->
_PREVIEW_FONT_TAGS = {"tiny": sasFontTagTiny, "body": sasFontTagBody, "label": sasFontTagLabel, "title": sasFontTagTitle}


def getUIFontSizes():
	return dict((szRole, _getSASUIFontSize(tag.szDefineName)) for szRole, tag in _PREVIEW_FONT_TAGS.items())


def setUIFontPreview(dSizes, bReset=False):
	# <!-- custom: Validate the whole request before changing any size.
	# Clear the normal and bold tags together so imports holding either object see the next size. (GPT-6.2-Sol) -->
	for szRole, iSize in dSizes.items():
		if szRole not in _PREVIEW_FONT_TAGS or type(iSize) is not int or not 1 <= iSize <= 4:
			raise ValueError("expected tiny, body, label or title with a whole size from 1 to 4")
	if bReset:
		_SAS_UI_FONT_PREVIEW.clear()
	for szRole, iSize in dSizes.items():
		_SAS_UI_FONT_PREVIEW[_PREVIEW_FONT_TAGS[szRole].szDefineName] = iSize
	for tag in _PREVIEW_FONT_TAGS.values():
		tag._cachedTag = None
		tag.bold._cachedTag = None


SAS_FONT_OPEN_RE = re.compile(u"<font=[^>]*>", re.IGNORECASE)
SAS_FONT_CLOSE_RE = re.compile(u"</font>", re.IGNORECASE)

def applyFontTag(szText, szTag):
	if szText is None:
		return szText
	if szText == "":
		return szText
	try:
		szUnicode = unicode(szText)
	except:
		return szText
	# <!-- custom: usage rule: always try bodyText/labelText first (simple path).
	# If text already contains <font=...>, leave it unchanged here to avoid double-wrapping.
	# Escalate to normalize* only after reproducing a real failure with simple wrapping in that exact caller/data path.
	# Note: this guidance was established while working on Sevopedia paths.
	# Advisors/other UI also use this helper, but they were not necessarily migrated under the same strict "escalate to normalize* only after failure" rule.
	# Current empirical examples: ConceptInfo/NewConceptInfo and Sevopedia Leader Civilopedia text need normalize; hints, Unit/History civilopedia text, and Traits (Effects/Background) often work with simple bodyText/labelText. (GPT-5.3-Codex) -->
	# Extra example: Sevopedia Unit history panel ("Background") for concept-based entries (e.g. Great People units) needed normalizeLabelText; simple wrapping did not apply SAS scaling there.
	# Same issue/pattern applies to Sevopedia Vote history when vote Civilopedia reuses concept pages (UN/AP). (GPT-5.3-Codex) -->
	if szUnicode.find(u"<font=") != -1:
		return szUnicode
	return szTag + szUnicode + SAS_FONT_TAG_CLOSE

def stripFontTags(szText):
	if szText is None:
		return szText
	if szText == "":
		return szText
	try:
		szUnicode = unicode(szText)
	except:
		return szText
	szUnicode = SAS_FONT_OPEN_RE.sub(u"", szUnicode)
	szUnicode = SAS_FONT_CLOSE_RE.sub(u"", szUnicode)
	return szUnicode

# <!-- custom: Added addMessage and addImmediateMessage below as the Python counterparts of CvDLLInterfaceIFaceBase::addMessage, which wraps every message the DLL adds in the label font.
# A message Python added through CyInterface().addMessage or addImmediateMessage went to the EXE directly and kept the stock size, so at label size 3 MoreCiv4lerts' "Cyrus will export Iron" sat small under the DLL's larger "Global Warming strikes near ..." in the user's screenshot.
# Every Python message goes through these, which python_message_font.py checks; like the DLL, a text already holding a <font=...> tag is left as it is, and the size follows a live override, as labelText reads it at each call. See KI#117.2. (Claude code Opus 5.5) -->
# <!-- custom: A label size outside 1 to 4 sends the text plain, as the DLL's wrapSASLabelFontText does, rather than raising as labelText does elsewhere: a message often comes before the rest of a game event, such as the hurricane's building removal in CvRandomEventInterface.py, which a raise here would skip, as Codex's review (GPT-6.2-Sol) reproduced with SAS_UI_FONT_LABEL = 5 set live.
# The size is checked by labelText's own RuntimeError rather than a read here: a first draft read SAS_UI_FONT_LABEL in this function, which python_define_reads_import.py flagged as reachable at import through BugConfig's init() and BugUtil.logToScreen. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def _messageText(szString):
	try:
		return labelText(szString)
	except RuntimeError:
		return szString

def addMessage(ePlayer, bForce, iLength, szString, *args):
	CyInterface().addMessage(ePlayer, bForce, iLength, _messageText(szString), *args)

def addImmediateMessage(szString, szSound):
	CyInterface().addImmediateMessage(_messageText(szString), szSound)

def tinyText(szText):
	return applyFontTag(szText, sasFontTagTiny)

def bodyText(szText):
	return applyFontTag(szText, sasFontTagBody)

def labelText(szText):
	return applyFontTag(szText, sasFontTagLabel)

def imageText(szButton, iSize, szText=None):
	# <!-- custom: Central inline-image formatter for text/table labels.
	# Callers still own presentation choices such as size, surrounding indentation/gaps, and selected-state resource choice.
	# This originally targeted sortable advisor headers (Long_Comments_py.txt #17) and now also removes repeated equivalent <img> formatting elsewhere. (GPT-5.5 + ChatGPT-5.6-Sol) -->
	szImage = u"<img=%s size=%d></img>" % (unicode(szButton), iSize)
	if szText is None or szText == "":
		return szImage
	return szImage + u" " + unicode(szText)

def labelImageText(szButton, iSize, szText=None):
	return labelText(imageText(szButton, iSize, szText))

def titleText(szText):
	return applyFontTag(szText, sasFontTagTitle)

def normalizeBodyText(szText):
	# <!-- custom: fallback rule: normalize* is not default.
	# Use only for proven problematic sources where simple bodyText/labelText fails because embedded <font=...> blocks SAS upscaling. (GPT-5.3-Codex) -->
	return applyFontTag(stripFontTags(szText), sasFontTagBody)

def normalizeLabelText(szText):
	return applyFontTag(stripFontTags(szText), sasFontTagLabel)

# <!-- custom: The icon goes through str() in the three setTable*Scaled helpers: the engine takes it as char const*, so a unicode icon, even an empty u"", raised a Boost ArgumentError and broke the whole Victory screen (SAS48 island autoplay, 2026-11-15).
# Button paths are ASCII, so str() keeps them; a non-ASCII one would still fail loudly. See KI#118.2. (Claude code Opus 5.5) -->
def setTableTextScaled(screen, szTable, iCol, iRow, szText, szIcon, eWidgetType, iData1, iData2, eJustify, szTag):
	screen.setTableText(szTable, iCol, iRow, applyFontTag(szText, szTag), str(szIcon), eWidgetType, iData1, iData2, eJustify)

def setTableIntScaled(screen, szTable, iCol, iRow, szText, szIcon, eWidgetType, iData1, iData2, eJustify, szTag):
	screen.setTableInt(szTable, iCol, iRow, applyFontTag(szText, szTag), str(szIcon), eWidgetType, iData1, iData2, eJustify)

def setTableDateScaled(screen, szTable, iCol, iRow, szText, szIcon, eWidgetType, iData1, iData2, eJustify, szTag):
	screen.setTableDate(szTable, iCol, iRow, applyFontTag(szText, szTag), str(szIcon), eWidgetType, iData1, iData2, eJustify)

def setTableColumnHeaderScaled(screen, szTable, iCol, szText, iWidth, szTag):
	screen.setTableColumnHeader(szTable, iCol, applyFontTag(szText, szTag), iWidth)

def appendListBoxStringScaled(screen, szWidgetName, szText, eWidgetType, iData1, iData2, eJustify, szTag):
	screen.appendListBoxString(szWidgetName, applyFontTag(szText, szTag), eWidgetType, iData1, iData2, eJustify)

def appendListBoxStringNoUpdateScaled(screen, szWidgetName, szText, eWidgetType, iData1, iData2, eJustify, szTag):
	screen.appendListBoxStringNoUpdate(szWidgetName, applyFontTag(szText, szTag), eWidgetType, iData1, iData2, eJustify)

def setTableTextLabel(screen, szTable, iCol, iRow, szText, szIcon, eWidgetType, iData1, iData2, eJustify):
	setTableTextScaled(screen, szTable, iCol, iRow, szText, szIcon, eWidgetType, iData1, iData2, eJustify, sasFontTagLabel)

def setTableIntLabel(screen, szTable, iCol, iRow, szText, szIcon, eWidgetType, iData1, iData2, eJustify):
	# <!-- custom: use this for sortable numeric table cells, even when display strings include signs or color tags (e.g. +8, -2, raw signed years like -4000).
	# Do not use it for formatted date text such as 4000 BC / 800 AD; those are intentionally textual.
	# Civ4 table sorting treats setTableInt cells numerically, while setTableText sorts lexically. (GPT-5.5) -->
	setTableIntScaled(screen, szTable, iCol, iRow, szText, szIcon, eWidgetType, iData1, iData2, eJustify, sasFontTagLabel)

def setTableDateLabel(screen, szTable, iCol, iRow, szText, szIcon, eWidgetType, iData1, iData2, eJustify):
	# <!-- custom: preserve Civ4's date-typed table sorting while applying the shared label font.
	# Generic setTableText made formatted BC/AD dates sort lexically. See KI#229. (ChatGPT-5.6-Sol + GPT-5.6-Sol) -->
	setTableDateScaled(screen, szTable, iCol, iRow, szText, szIcon, eWidgetType, iData1, iData2, eJustify, sasFontTagLabel)

def setTableColumnHeaderLabel(screen, szTable, iCol, szText, iWidth):
	setTableColumnHeaderScaled(screen, szTable, iCol, szText, iWidth, sasFontTagLabel)

# <!-- custom: Table headers can sort but cannot carry widget actions.
# Keep the text in the header and put a linked icon in the remaining space, if it is wide enough to click.
# Originally used for Peak, Hill and River in the World Advisor. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def setTableColumnHeaderLabelWithLink(screen, szTable, iCol, szText, columnRect, szWidget, szButton, widgetData, iTextInset, iIconPadding):
	iX, iY, iWidth, iHeight = columnRect
	szHeader = labelText(szText)
	screen.setTableColumnHeader(szTable, iCol, szHeader, iWidth)
	iOffset = iTextInset + CyInterface().determineWidth(szHeader) + iIconPadding
	iSpace = min(iHeight, iWidth - iOffset)
	iSize = iSpace - 2 * iIconPadding
	if iSize >= iHeight / 2:
		eWidget, iData1, iData2 = widgetData
		screen.setImageButton(szWidget, szButton, iX + iOffset + iIconPadding, iY + (iHeight - iSize) / 2, iSize, iSize, eWidget, iData1, iData2)

# <!-- custom: The icon-only counterpart: the header stays blank, so the rest of it still sorts, and a linked icon is centered over it, shrunk to the column and dropped if no room is left.
# The World Advisor's BFC columns and the Domestic Advisor's Overview 4 specialist columns each drew this their own way (2026-11-20); one helper keeps them alike.
# The icon is placed on the screen, not in the table, as a table's children count their y from below the header. (Claude code Opus 5.5) -->
def setTableColumnHeaderIconLink(screen, szTable, iCol, columnRect, szWidget, szButton, widgetData, iIconPadding):
	iX, iY, iWidth, iHeight = columnRect
	screen.setTableColumnHeader(szTable, iCol, "", iWidth)
	iSize = min(iWidth, iHeight) - 2 * iIconPadding
	if iSize > 0:
		eWidget, iData1, iData2 = widgetData
		screen.setImageButton(szWidget, szButton, iX + (iWidth - iSize) / 2, iY + (iHeight - iSize) / 2, iSize, iSize, eWidget, iData1, iData2)

def appendListBoxStringLabel(screen, szWidgetName, szText, eWidgetType, iData1, iData2, eJustify):
	appendListBoxStringScaled(screen, szWidgetName, szText, eWidgetType, iData1, iData2, eJustify, sasFontTagLabel)

def appendListBoxStringNoUpdateLabel(screen, szWidgetName, szText, eWidgetType, iData1, iData2, eJustify):
	appendListBoxStringNoUpdateScaled(screen, szWidgetName, szText, eWidgetType, iData1, iData2, eJustify, sasFontTagLabel)

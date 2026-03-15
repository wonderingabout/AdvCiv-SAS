from SASFontUtils import (
	SAS_FONT_TAG_BODY,
	SAS_FONT_TAG_CLOSE,
	SAS_FONT_TAG_LABEL,
	SAS_FONT_TAG_TITLE,
	SAS_FONT_TAG_TINY,
)
import re

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
	# <!-- custom: usage rule: start with bodyText/labelText (simple path). If text already contains <font=...>, keep it unchanged here to avoid double-wrapping.
	# Only switch callers to normalize* when testing shows base upscaling fails due to embedded hardcoded font tags.
	# Current known examples: ConceptInfo/NewConceptInfo empirically seem to need normalize; regular hints empirically seem not to. (GPT-5.3-Codex) -->
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


def tinyText(szText):
	return applyFontTag(szText, SAS_FONT_TAG_TINY)


def bodyText(szText):
	return applyFontTag(szText, SAS_FONT_TAG_BODY)


def labelText(szText):
	return applyFontTag(szText, SAS_FONT_TAG_LABEL)


def titleText(szText):
	return applyFontTag(szText, SAS_FONT_TAG_TITLE)


def normalizeBodyText(szText):
	# <!-- custom: fallback rule: normalize* is not default. Use it only after bodyText/labelText fails, i.e. when source text carries embedded <font=...> that prevents SAS upscaling. (GPT-5.3-Codex) -->
	return applyFontTag(stripFontTags(szText), SAS_FONT_TAG_BODY)


def normalizeLabelText(szText):
	return applyFontTag(stripFontTags(szText), SAS_FONT_TAG_LABEL)


def setTableTextScaled(screen, szTable, iCol, iRow, szText, szIcon, eWidgetType, iData1, iData2, eJustify, szTag):
	screen.setTableText(szTable, iCol, iRow, applyFontTag(szText, szTag), szIcon, eWidgetType, iData1, iData2, eJustify)


def setTableIntScaled(screen, szTable, iCol, iRow, szText, szIcon, eWidgetType, iData1, iData2, eJustify, szTag):
	screen.setTableInt(szTable, iCol, iRow, applyFontTag(szText, szTag), szIcon, eWidgetType, iData1, iData2, eJustify)


def setTableColumnHeaderScaled(screen, szTable, iCol, szText, iWidth, szTag):
	screen.setTableColumnHeader(szTable, iCol, applyFontTag(szText, szTag), iWidth)


def appendListBoxStringScaled(screen, szWidgetName, szText, eWidgetType, iData1, iData2, eJustify, szTag):
	screen.appendListBoxString(szWidgetName, applyFontTag(szText, szTag), eWidgetType, iData1, iData2, eJustify)


def appendListBoxStringNoUpdateScaled(screen, szWidgetName, szText, eWidgetType, iData1, iData2, eJustify, szTag):
	screen.appendListBoxStringNoUpdate(szWidgetName, applyFontTag(szText, szTag), eWidgetType, iData1, iData2, eJustify)

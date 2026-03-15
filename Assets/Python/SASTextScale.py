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
	# <!-- custom: usage rule: always try bodyText/labelText first (simple path). If text already contains <font=...>, leave it unchanged here to avoid double-wrapping.
	# Escalate to normalize* only after reproducing a real failure with simple wrapping in that exact caller/data path.
	# Current empirical examples: ConceptInfo/NewConceptInfo seem to need normalize; hints, Unit/History civilopedia text, and Traits (Effects/Background) seem to work with simple bodyText. (GPT-5.3-Codex) -->
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
	# <!-- custom: fallback rule: normalize* is not default. Use only for proven problematic sources where simple bodyText/labelText fails because embedded <font=...> blocks SAS upscaling. (GPT-5.3-Codex) -->
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

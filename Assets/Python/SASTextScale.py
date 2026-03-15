from SASFontUtils import (
	SAS_FONT_TAG_BODY,
	SAS_FONT_TAG_CLOSE,
	SAS_FONT_TAG_LABEL,
	SAS_FONT_TAG_TITLE,
	SAS_FONT_TAG_TINY,
)


def applyFontTag(szText, szTag):
	if szText is None:
		return szText
	if szText == "":
		return szText
	try:
		szUnicode = unicode(szText)
	except:
		return szText
	if szUnicode.find(u"<font=") != -1:
		return szUnicode
	return szTag + szUnicode + SAS_FONT_TAG_CLOSE


def tinyText(szText):
	return applyFontTag(szText, SAS_FONT_TAG_TINY)


def bodyText(szText):
	return applyFontTag(szText, SAS_FONT_TAG_BODY)


def labelText(szText):
	return applyFontTag(szText, SAS_FONT_TAG_LABEL)


def titleText(szText):
	return applyFontTag(szText, SAS_FONT_TAG_TITLE)


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

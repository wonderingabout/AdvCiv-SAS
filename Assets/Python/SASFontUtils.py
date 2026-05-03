# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md).


from CvPythonExtensions import *

gc = CyGlobalContext()
_SAS_UI_FONT_SIZE_CACHE = {}


def _getSASUIFontSize(szDefineName):
	if szDefineName in _SAS_UI_FONT_SIZE_CACHE:
		return _SAS_UI_FONT_SIZE_CACHE[szDefineName]
	iSize = gc.getDefineINT(szDefineName)
	if iSize < 1 or iSize > 4:
		_SAS_UI_FONT_SIZE_CACHE[szDefineName] = None
		raise RuntimeError("SASFontUtils: %s=%d out of [1,4] - check CIV4SASDefines.xml" % (szDefineName, iSize))
	_SAS_UI_FONT_SIZE_CACHE[szDefineName] = iSize
	print("SASFontUtils: initialized %s = %d" % (szDefineName, iSize))
	return iSize


def getSASUIFontTiny():
	return _getSASUIFontSize("SAS_UI_FONT_TINY")


def getSASUIFontBody():
	return _getSASUIFontSize("SAS_UI_FONT_BODY")


def getSASUIFontLabel():
	return _getSASUIFontSize("SAS_UI_FONT_LABEL")


def getSASUIFontTitle():
	return _getSASUIFontSize("SAS_UI_FONT_TITLE")


def getSASUIFontHover():
	return _getSASUIFontSize("SAS_UI_FONT_HOVER")


class _DynamicFontTag:
	def __init__(self, szDefineName, bBold):
		self.szDefineName = szDefineName
		self.bBold = bBold

	def _build(self):
		iSize = _getSASUIFontSize(self.szDefineName)
		if iSize is None:
			return u""
		if self.bBold:
			return u"<font=%db>" % iSize
		return u"<font=%d>" % iSize

	def __unicode__(self):
		return self._build()

	def __str__(self):
		return self._build().encode("ascii")

	def __add__(self, szOther):
		return self._build() + szOther

	def __radd__(self, szOther):
		return szOther + self._build()


SAS_FONT_TAG_CLOSE = u"</font>"

sasFontTagTiny = _DynamicFontTag("SAS_UI_FONT_TINY", False)
sasFontTagBody = _DynamicFontTag("SAS_UI_FONT_BODY", False)
sasFontTagLabel = _DynamicFontTag("SAS_UI_FONT_LABEL", False)
sasFontTagTitle = _DynamicFontTag("SAS_UI_FONT_TITLE", False)
sasFontTagHover = _DynamicFontTag("SAS_UI_FONT_HOVER", False)

sasFontTagTinyBold = _DynamicFontTag("SAS_UI_FONT_TINY", True)
sasFontTagBodyBold = _DynamicFontTag("SAS_UI_FONT_BODY", True)
sasFontTagLabelBold = _DynamicFontTag("SAS_UI_FONT_LABEL", True)
sasFontTagTitleBold = _DynamicFontTag("SAS_UI_FONT_TITLE", True)

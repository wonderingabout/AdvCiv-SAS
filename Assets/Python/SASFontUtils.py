# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md).


from CvPythonExtensions import *

gc = CyGlobalContext()
_FONT_SIZE_CACHE = {}


def _getFontSizeOrDefault(szDefineName, iDefault):
	if szDefineName in _FONT_SIZE_CACHE:
		return _FONT_SIZE_CACHE[szDefineName]
	iSize = gc.getDefineINT(szDefineName)
	if iSize < 1 or iSize > 4:
		if iDefault > 0:
			print("SASFontUtils: invalid or unavailable %s=%d; using default %d" % (szDefineName, iSize, iDefault))
		return iDefault
	# Cache once valid to avoid repeated define lookups.
	_FONT_SIZE_CACHE[szDefineName] = iSize
	return iSize


def getSASUIFontTiny():
	return _getFontSizeOrDefault("SAS_UI_FONT_TINY", 1)


def getSASUIFontBody():
	return _getFontSizeOrDefault("SAS_UI_FONT_BODY", 2)


def getSASUIFontLabel():
	return _getFontSizeOrDefault("SAS_UI_FONT_LABEL", 3)


def getSASUIFontTitle():
	return _getFontSizeOrDefault("SAS_UI_FONT_TITLE", 4)


def getSASUIFontHover():
	# Returns 0 (disabled) or 1-4. 0 means no hover font scaling.
	szName = "SAS_UI_FONT_HOVER"
	if szName in _FONT_SIZE_CACHE:
		return _FONT_SIZE_CACHE[szName]
	iSize = gc.getDefineINT(szName)
	if iSize < 0 or iSize > 4:
		return 0
	_FONT_SIZE_CACHE[szName] = iSize
	return iSize


class _DynamicFontTag:
	def __init__(self, szDefineName, iDefault, bBold):
		self.szDefineName = szDefineName
		self.iDefault = iDefault
		self.bBold = bBold

	def _build(self):
		iSize = _getFontSizeOrDefault(self.szDefineName, self.iDefault)
		if iSize < 1:
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

SAS_FONT_TAG_TINY = _DynamicFontTag("SAS_UI_FONT_TINY", 1, False)
SAS_FONT_TAG_BODY = _DynamicFontTag("SAS_UI_FONT_BODY", 2, False)
SAS_FONT_TAG_LABEL = _DynamicFontTag("SAS_UI_FONT_LABEL", 3, False)
SAS_FONT_TAG_TITLE = _DynamicFontTag("SAS_UI_FONT_TITLE", 4, False)
SAS_FONT_TAG_HOVER = _DynamicFontTag("SAS_UI_FONT_HOVER", 0, False)

SAS_FONT_TAG_TINY_BOLD = _DynamicFontTag("SAS_UI_FONT_TINY", 1, True)
SAS_FONT_TAG_BODY_BOLD = _DynamicFontTag("SAS_UI_FONT_BODY", 2, True)
SAS_FONT_TAG_LABEL_BOLD = _DynamicFontTag("SAS_UI_FONT_LABEL", 3, True)
SAS_FONT_TAG_TITLE_BOLD = _DynamicFontTag("SAS_UI_FONT_TITLE", 4, True)

# <!-- custom: modified from Claude AI's (kindly shared (to me or and all or not or and othe ror and not but anyways etc anyways etc anyways etc...)) or not for AdvCiv-SAS or/and my personal taste or feel or/and wish or thought or and other or and not anyways etc anyways etc anyways etc... -->
# Get all attributes of the object
def printObjAttrs(obj):
	for attr in dir(obj):
		try:
			# Try to get the attribute
			attr_value = getattr(obj, attr)

			# Check if it's a method (callable)
			if callable(attr_value):
				print(u"%s\n" % attr)
			else:
				print(u"%s = %s\n" % (attr, attr_value))
		except:
			print(u"%s - Error accessing\n" % attr)



def check_button_path_is_valid(buttonHeader, resolvedButtonPath, configButtonPathSTxtKey):
	if resolvedButtonPath == configButtonPathSTxtKey:
		raise ValueError(u"[VALUE ERROR] Button path not found in XML (resolvedButtonPath=%s matches configButtonPath=%s in buttonHeader=%s, which indicates button path provided in config most likely does not exist in the XML), please check button path provided in (or in - whichever filename it would have in the future -) ai_attributes_displayed_config.py exists in your mod path and also matches button path in (or in - whichever filename it would have in the future -) AdvCiv-SAS_IconsAsButtons.xml or/and AdvCiv-SAS_Buttons_Hardcoded_Repertoire.xml is valid and exists in your mod path." % (resolvedButtonPath, configButtonPathSTxtKey, buttonHeader))



def getXOccurenceFound(xPanel, leftPadding, interButtonSpacing, nCountOccurencesFound, buttonSize, xSubstractedAdjustment):
    # <!-- custom: all buttons are spaced, except the first one that depends on panel left side padding, so do a - 1 to account for that -->
    if (nCountOccurencesFound < 1):
        raise ValueError("[FATAL] nCountOccurencesFound=%d cannot be < 1, make sure you first increment nCountOccurencesFound at first occurence found before calling this getXOccurenceFound method anyways etc." % nCountOccurencesFound)
    return xPanel + leftPadding + (nCountOccurencesFound * buttonSize) + ((nCountOccurencesFound - 1) * interButtonSpacing) - xSubstractedAdjustment



def getXSubstractedAdjustmentNumTxtBasedOnLenNumTxt(numTxt, addedOffset, buttonSize):
    buttonSizeDoubleSize = 2 * buttonSize
    if (addedOffset > buttonSizeDoubleSize):
        raise ValueError(u"[FATAL] Offset %d too high, cannot be higher than 2 * buttonsize = 2 * %d = %d, please make sure offset is set as intended, and update your code or this method raising the error depending on what you/need want anyways etc." % (addedOffset, buttonSize, buttonSizeDoubleSize))
    
    # <!-- custom: examples of offset:
    # - if addedOffset is 0.00, returns same value
    # - if addedOffset is 0.10, returns value + 0.10, for example 0.55 + 0.10 = 0.65 returned anyways etc 
    # -->

    lenNumTxt = len(numTxt)
    # <!-- custom: be careful the '%' char in for example "+50%" does not appear in str debug, but it is counted in str length, and does however also appear though in the UI in sevopedia leader py, so adjusting this code based on these results
    # xxxxxxxxx3xxxxxxx+7
    # xxxxxxxxx5xxxxxxx-120
    # xxxxxxxxx6xxxxxxx+1254
    # xxxxxxxxx4xxxxxxx+50
    # -->
    if lenNumTxt < 0:
        raise ValueError(u"[FATAL] Unhandled negative length at numTxt=%s, lenNumTxt=%d" % (numTxt, lenNumTxt))
    if lenNumTxt < 3:
        return 0.72 + addedOffset
    elif lenNumTxt == 3:
        # <!-- custom: example "+5"(%), "-8"(%), etc -->
        return 0.79 + addedOffset
    elif lenNumTxt == 4:
        # <!-- custom: example "+50"(%), "-35"(%), etc -->
        return 0.85 + addedOffset
    elif lenNumTxt == 5:
        # <!-- custom: example "+100"(%), "-120"(%), etc -->
        return 0.92 + addedOffset
    elif lenNumTxt == 6:
        # <!-- custom: example "+1000"(%), "-3798"(%), etc -->
        return 1.01 + addedOffset
    else:
        # <!-- custom: example "+10000"(%) or longer, "-37982"(%) or longer, etc -->
        return 1.09 + addedOffset

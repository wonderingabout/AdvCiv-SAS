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

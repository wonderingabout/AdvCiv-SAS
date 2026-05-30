## BugHelp
##
## Opens BUG's help file, "BUG Mod Help.chm", or the online version, for the user's language.
##
## TODO:
##   Move to configuration XML
##   Support multiple help files and shortcuts
##
## Copyright (c) 2008 The BUG Mod.
##
## Author: EmperorFool
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#

from CvPythonExtensions import *
import Popup as PyPopup
import BugPath
import BugUtil

def launch(argsList=None):
	# Opens the mod's help file or web page externally if it can be found or displays an error alert.
	#	
	# On Windows this opens the compiled HTML help file (CHM).
	# On Mac this opens a browser window to the online help file.
	#
	if BugPath.isMac():
		sLang = ["ENG", "ENG", "DEU", "ITA", "ENG"]
		url = "http://civ4bug.sourceforge.net/BUGModHelp/%s/index.htm" % sLang[CyGame().getCurrentLanguage()]
		try:
			import webbrowser
			showLaunchMessage()
			webbrowser.open(url, new=1, autoraise=1)
			return True
		except:
			showErrorAlert(BugUtil.getPlainText("TXT_KEY_BUG_HELP_CANNOT_OPEN_BROWSER_TITLE"), BugUtil.getText("TXT_KEY_BUG_HELP_CANNOT_OPEN_BROWSER_BODY", (url,)))
	else: # advc.009: There is no FRA and ESP translation
		sLang = ["ENG", "ENG", "DEU", "ITA", "ENG"]
		name = "BUG Mod Help-%s.chm" % (sLang[CyGame().getCurrentLanguage()])
		#file = BugPath.findInfoFile(name)

		file, debug = _SAS_findBugDocFile(name)
		if file:
			import os
			message = BugUtil.getPlainText("TXT_KEY_BUG_HELP_OPENING")
			CyInterface().addImmediateMessage(message, "")
			os.startfile(file)
			return True
		else:
			showErrorAlert(BugUtil.getPlainText("TXT_KEY_BUG_HELP_MISSING_TITLE"), debug + BugUtil.getText("TXT_KEY_BUG_HELP_MISSING_BODY", (name,)))
	return False

def showLaunchMessage():
	# Shows an "opening..." alert message in the event log.
	BugUtil.alert(BugUtil.getPlainText("TXT_KEY_BUG_HELP_OPENING"))

def showErrorAlert(title, body):
	# Opens a popup window showing the given error message.
	#
	popup = PyPopup.PyPopup()
	popup.setHeaderString(title)
	popup.setBodyString(body)
	popup.launch()

# <!-- custom: on Windows, the BUG Menu's help does not open for some reason ingame whe clicking on the "Bug Mod Help" button in the Bug Menu. Fixed by adding this with the help of chatgpt 5.2 thanks.
# Note: based on testing, it looks like cwd's path is: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\, considering the error message we got with a faulty path if we don't add the rest of the path to our mod, and considering adding such a remaining path fixes the issue ingame and successfully allows to display the BUG Menu's help. -->
def _SAS_findBugDocFile(name):
	# Returns (fullpath_or_None, debug_string)
	try:
		import os

		debugLines = []
		try:
			cwd = os.getcwd()
		except:
			cwd = "<cwd?>"
		debugLines.append("BugHelp debug")
		debugLines.append("cwd=%s" % cwd)

		tries = []

		def addTry(p):
			if p and p not in tries:
				tries.append(p)

		# 3) Common Civ4 layout guesses from cwd
		try:
			# <!-- custom: based on testing, the below path fetching (as of now files are in C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\BUG Doc\) works successfully ingame. -->
			# <!-- custom: note 2: our mod AdvCiv-SAS's name is as of now hardcoded but it works, if you change the mod's name, you'd need to change it here too unless this name is dynamically fetched instead of as of now being hardcoded. -->
			#addTry(os.path.join(cwd, "Mods", "AdvCiv-SAS", "BUG Doc", name))
			# <!-- custom: since i want to centralize some docs in our AdvCiv-SAS Mod, moving it to another folder where our other folders as of now are. Note: added a "_" for consistency with other non-space separated folder names and file names. Works successfully ingame (as of now after the path now in: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\_0_Common_Docs\BUG_Doc\).  -->
			addTry(os.path.join(cwd, "Mods", "AdvCiv-SAS", "_0_Common_Docs", "BUG_Doc", name))
		except:
			pass

		# Decide
		for p in tries:
			try:
				if os.path.isfile(p):
					debugLines.append("FOUND=%s" % p)
					return p, "\n".join(debugLines) + "\n\n"
			except:
				pass

		# Not found: show first few attempts in the popup
		for i in range(3):
			if i < len(tries):
				debugLines.append("try%d=%s" % (i+1, tries[i]))
		return None, "\n".join(debugLines) + "\n\n"
	except:
		return None, "BugHelp debug failed completely.\n\n"

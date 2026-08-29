#CvModName.py
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#

from CvPythonExtensions import CyGlobalContext

gc = CyGlobalContext()

# <!-- custom: Keep BUG/BULL's long-standing CvModName API, but source the branded/project name through AdvCiv's central ModName resolver. The actual installed folder remains separate and is exposed by the filesystem getters below. (ChatGPT-5.6-Sol) -->
modName = gc.getModDisplayName() # advc.009
displayName = modName # advc.009
modVersion = ""

civName = "BtS"
civVersion = "3.19"

def getName():
	return modName

def getDisplayName():
	return displayName

# <!-- custom: Expose AdvCiv/BtS's actual loaded mod folder/path separately from the centralized branded display name, so filesystem callers do not reconstruct paths from the project name. (ChatGPT-5.6-Sol) -->
def getFolderName():
	return gc.getModFolderName()

def getPathInRoot():
	return gc.getModPathInRoot()

def getVersion():
	return modVersion

# <!-- custom: Shared formatter avoids a trailing space while modVersion is empty, and gives the later automatic-version work one formatting path. (ChatGPT-5.6-Sol) -->
def _getNameAndVersion(name):
	if modVersion:
		return name + " " + modVersion
	return name

# <!-- custom: Preserve BUG/BULL's existing name/display-name APIs while routing both through the same centralized version formatter. (ChatGPT-5.6-Sol) -->
def getNameAndVersion():
	return _getNameAndVersion(modName)

def getDisplayNameAndVersion():
	return _getNameAndVersion(displayName)

def getCivName():
	return civName

def getCivVersion():
	return civVersion

def getCivNameAndVersion():
	return civName + " " + civVersion

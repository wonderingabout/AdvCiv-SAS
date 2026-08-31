#CvModName.py
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#

from CvPythonExtensions import CyGlobalContext

gc = CyGlobalContext()

# <!-- custom: Keep BUG/BULL's long-standing CvModName API, but source branded/project and source-version details through AdvCiv's central ModName resolver. The actual installed folder remains separate and is exposed by the filesystem getters below. (ChatGPT-5.6-Sol) -->
modName = gc.getModDisplayName() # advc.009
displayName = modName # advc.009
# <!-- custom: Keep version lookup lazy too: importing CvModName for ordinary path/name use should not trigger the one-time filesystem/Git resolver. The legacy modVersion variable is filled on first getVersion() call. (ChatGPT-5.6-Sol) -->
modVersion = ""
_modVersionResolved = False

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
	global modVersion, _modVersionResolved
	if not _modVersionResolved:
		modVersion = gc.getModVersion()
		_modVersionResolved = True
	return modVersion

# <!-- custom: Keep exact source provenance available to future UI/debug consumers without teaching Python about Git or archive metadata. (ChatGPT-5.6-Sol) -->
def getCommitHash():
	return gc.getModCommitHash()

def getShortCommitHash():
	return gc.getModShortCommitHash()

def getBranch():
	return gc.getModBranch()

def getCommitDate():
	return gc.getModCommitDate()

def getSourceMetadataType():
	return gc.getModSourceMetadataType()

def getSourceDirtyState():
	return gc.getModSourceDirtyState()

def getSourceDirtyFileCount():
	return gc.getModSourceDirtyFileCount()

def getSourceDirtyFiles():
	return gc.getModSourceDirtyFiles()

# <!-- custom: Display the practical commit-count version plus exact short SHA, and mark local tracked edits only when Git verifies them. Versioned archives reconstruct the same commit-count version through the immutable anchor; older/unanchored archives can still fall back to exact SHA without inventing a version. (ChatGPT-5.6-Sol) -->
def _getVersionDetails():
	version = getVersion()
	shortCommit = getShortCommitHash()
	dirtyState = getSourceDirtyState()
	dirtyInside = ""
	dirtyOutside = ""
	if dirtyState == 1:
		dirtyInside = ", dirty"
		dirtyOutside = " (dirty)"
	if version:
		if shortCommit:
			return version + " (" + shortCommit + dirtyInside + ")"
		return version + dirtyOutside
	if shortCommit:
		return "(" + shortCommit + dirtyInside + ")"
	return ""

# <!-- custom: Preserve BUG/BULL's existing name/display-name APIs while routing both through the same centralized version formatter. (ChatGPT-5.6-Sol) -->
def _getNameAndVersion(name):
	details = _getVersionDetails()
	if details:
		return name + " " + details
	return name

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

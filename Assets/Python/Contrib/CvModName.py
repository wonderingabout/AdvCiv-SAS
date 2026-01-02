#CvModName.py

# <!-- custom: change the in-game mod name from "AdvCiv Mod" to "AdvCiv-SAS Mod" so it shows up in the Settings panel too. (GPT-5.2-Codex (summarized)) -->
modName = "AdvCiv-SAS" # advc.009
displayName = "AdvCiv-SAS" #advc.009
modVersion = ""

civName = "BtS"
civVersion = "3.19"

def getName():
	return modName

def getDisplayName():
	return displayName

def getVersion():
	return modVersion

def getNameAndVersion():
	return modName + " " + modVersion

def getDisplayNameAndVersion():
	return displayName + " " + modVersion


def getCivName():
	return civName

def getCivVersion():
	return civVersion

def getCivNameAndVersion():
	return civName + " " + civVersion

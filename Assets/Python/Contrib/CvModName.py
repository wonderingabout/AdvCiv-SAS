#CvModName.py

# <!-- custom: change mod name displayed ingame from "AdvCiv Mod" to as of now "AdvCiv-SAS Mod", so that it now also appears as such in the "Settings" ingame menu (the panel showing game difficulty, map size, number of players, etc if i am not mistaken and if i may say i mean but anyways etc) -->
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

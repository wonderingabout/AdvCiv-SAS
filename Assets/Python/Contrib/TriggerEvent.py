## advc.007d: from BUG 4.5
## TriggerEvent
##
## Hit CTRL + SHIFT + E to manually trigger a random event.
##
## Copyright (c) 2010 The BUG Mod.
##
## Author: Ronnar

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

from CvPythonExtensions import *
from CvEventInterface import getEventManager
import BugUtil
import PlayerUtil
import SASGameRecordActions # <!-- custom: Record the debug selector's reviewed EventTriggerInfo choice through the existing SGR bridge, keeping ordinary event results separate. (GPT-6.1-Sol) -->

gc = CyGlobalContext()

def showChooseEventPopup(argsList):
	if getEventManager().bAllowCheats:
		ePlayer = PlayerUtil.getActivePlayerID()
		popupInfo = CyPopupInfo()
		popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
		popupInfo.setText(BugUtil.getPlainText("TXT_KEY_POPUP_SELECT_EVENT"))
		popupInfo.setData1(ePlayer)
		popupInfo.setOnClickedPythonCallback("triggerRandomEvent")
		for i in range(gc.getNumEventTriggerInfos()):
			info = gc.getEventTriggerInfo(i)
			name = info.getType().replace("EVENTTRIGGER_", "").replace("_", " ").title()
			popupInfo.addPythonButton(name, "")
		popupInfo.addPythonButton(BugUtil.getPlainText("TXT_KEY_POPUP_CANCEL"), "")
		popupInfo.addPopup(ePlayer)

def triggerRandomEvent(argsList):
	id = argsList[0]
	iData1 = argsList[1]
	# <!-- custom: Include Cancel before the early return; tracing must not trigger or reevaluate an event itself. (GPT-6.1-Sol) -->
	if SASGameRecordActions.isEnabled():
		SASGameRecordActions.logEventTriggerResponse(gc, id, iData1)
	BugUtil.debug("args: %r", argsList)

	type = None
	if id < gc.getNumEventTriggerInfos():
		type = gc.getEventTriggerInfo(id).getType()
	else:
		return
	BugUtil.alert("Event: %s [%d]", type, id)
	pPlayer = PlayerUtil.getPlayer(iData1)
	pPlayer.trigger(id)

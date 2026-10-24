# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: UI-owned choices for the known Python popup callbacks, independent of SGR/runtime recording.
# CyPopupInfo.addPythonButton has no explicit ID argument: the EXE returns insertion-order indices.
# Build buttons, named handler IDs and readable diagnostic names from the same entries so independent numeric/string tables cannot drift.
# Retain the inherited button order and localization keys; this module imports no Civ4 globals and reads no XML or defines at import time. (GPT-6.1-Sol) -->
class PopupChoiceSet(object):
	def __init__(self, entries):
		self._entries = entries
		for iButton, (szName, szTextKey) in enumerate(entries):
			setattr(self, szName, iButton)

	# <!-- custom: Use the exact catalog order that assigned the named handler IDs; retain the original empty text arguments and button-art paths.
	# Health/happiness advice has distinct inherited wording; optional text overrides use named choice IDs, preserving labels without defining another button order. (GPT-6.1-Sol) -->
	def addButtons(self, popup, translator, textKeys=None):
		for iButton, (szName, szTextKey) in enumerate(self._entries):
			if textKeys is not None:
				szTextKey = textKeys.get(iButton, szTextKey)
			popup.addPythonButton(translator.getText(szTextKey, ()), "")

	# <!-- custom: Only known indices have names; consumers retain unknown raw responses without manufacturing an acceptance/refusal.
	# This does not inspect displayed or user-entered text. (GPT-6.1-Sol) -->
	def getName(self, iButton):
		if iButton >= 0 and iButton < len(self._entries):
			return self._entries[iButton][0]
		return "BUTTON_RESPONSE"


# <!-- custom: The original advisor/feat/event producers used the localization keys below in this order.
# Keep each family's distinct meaning even where the visible Yes/No or accept/refuse/examine wording is shared. (GPT-6.1-Sol) -->
CITY_RECOMMENDATION = PopupChoiceSet((
	("ACCEPT_RECOMMENDATION", "TXT_KEY_POPUP_DEMAND_AGREE"),
	("REFUSE_RECOMMENDATION", "TXT_KEY_POPUP_DEMAND_REFUSE"),
	("EXAMINE_CITY", "TXT_KEY_POPUP_DEMAND_EXAMINE"),
))
LIBERATION = PopupChoiceSet((
	("ACCEPT_LIBERATION", "TXT_KEY_POPUP_DEMAND_AGREE"),
	("REFUSE_LIBERATION", "TXT_KEY_POPUP_DEMAND_REFUSE"),
	("EXAMINE_CITY", "TXT_KEY_POPUP_DEMAND_EXAMINE"),
))
COLONY = PopupChoiceSet((
	("ACCEPT_COLONY", "TXT_KEY_POPUP_DEMAND_AGREE"),
	("REFUSE_COLONY", "TXT_KEY_POPUP_DEMAND_REFUSE"),
	("EXAMINE_CITY", "TXT_KEY_POPUP_DEMAND_EXAMINE"),
))
FEAT = PopupChoiceSet((
	("ACKNOWLEDGE_FEAT", "TXT_KEY_FEAT_ACCOMPLISHED_OK"),
	("REQUEST_FEAT_DETAILS", "TXT_KEY_FEAT_ACCOMPLISHED_MORE"),
))
EVENT_WAR = PopupChoiceSet((
	("DECLARE_WAR", "TXT_KEY_POPUP_YES"),
	("DECLINE_WAR", "TXT_KEY_POPUP_NO"),
))
EVENT_PEACE = PopupChoiceSet((
	("ACCEPT_PEACE", "TXT_KEY_POPUP_YES"),
	("REFUSE_PEACE", "TXT_KEY_POPUP_NO"),
))

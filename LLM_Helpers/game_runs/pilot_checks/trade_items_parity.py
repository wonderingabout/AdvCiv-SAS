# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Run inside the game with 'pilot.py py @pilot_checks/trade_items_parity.py': compares the C++ trade table (getSASPilotTradeItemsJson) with the Python loop it replaced on 2026-11-13, for every pair of living players, and lists any entry only one side has. An empty "differences" is the expected result; written for the port's first test and kept to recheck after either side changes. (Claude code Opus 5.5) -->
# <!-- custom: CvPythonExtensions for TradeData and the enums; 'pilot' is the command module the py namespace provides, as a module or, when loaded by exec, its globals dict. (Claude code Opus 5.5) -->
from CvPythonExtensions import *


class _Commands:
	def __getattr__(self, name):
		if isinstance(pilot, dict):
			return pilot[name]
		return getattr(pilot, name)


pilotCommands = _Commands()
pairs = 0
differences = []
players = [i for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isAlive() and not gc.getPlayer(i).isBarbarian()]
for iGiver in players:
	giver = gc.getPlayer(iGiver)
	for iReceiver in players:
		if iReceiver == iGiver:
			continue
		pairs = pairs + 1
		native = {}
		for entry in pilotCommands.fromJson(pilotCommands._tradeItemsJson(giver, iReceiver)):
			native[(entry["item"], entry["data"])] = (entry.get("denial"), entry.get("what"))
		python = {}
		for szKind in [name for name in dir(TradeableItems) if name.startswith("TRADE_")]:
			eKind = getattr(TradeableItems, szKind)
			iCount = 0
			if eKind == TradeableItems.TRADE_TECHNOLOGIES:
				iCount = gc.getNumTechInfos()
			elif eKind == TradeableItems.TRADE_RESOURCES:
				iCount = gc.getNumBonusInfos()
			elif eKind == TradeableItems.TRADE_CIVIC:
				iCount = gc.getNumCivicInfos()
			elif eKind == TradeableItems.TRADE_RELIGION:
				iCount = gc.getNumReligionInfos()
			if iCount:
				entries = range(iCount)
			elif eKind == TradeableItems.TRADE_CITIES:
				entries = [city.getID() for city in pilotCommands._cities(giver)]
			elif eKind in (TradeableItems.TRADE_WAR, TradeableItems.TRADE_PEACE, TradeableItems.TRADE_EMBARGO):
				entries = [i for i in range(gc.getMAX_CIV_TEAMS()) if gc.getTeam(i).isAlive()]
			elif eKind == TradeableItems.TRADE_GOLD:
				entries = [giver.AI_maxGoldTrade(iReceiver)]
			elif eKind == TradeableItems.TRADE_GOLD_PER_TURN:
				entries = [giver.AI_maxGoldPerTurnTrade(iReceiver)]
			else:
				entries = [0]
			for iData in entries:
				item = TradeData()
				item.ItemType = eKind
				item.iData = iData
				if giver.canTradeItem(iReceiver, item, False):
					denial = None
					if not giver.isHuman():
						denial = pilotCommands._enumName(DenialTypes, giver.getTradeDenial(iReceiver, item))
					python[(szKind, iData)] = denial
		for key in native.keys():
			if key not in python:
				differences.append(("only C++", iGiver, iReceiver, key))
			elif python[key] != native[key][0]:
				differences.append(("denial", iGiver, iReceiver, key, python[key], native[key][0]))
		for key in python.keys():
			if key not in native:
				differences.append(("only Python", iGiver, iReceiver, key))
result = {"pairs": pairs, "differences": differences[:20], "differenceCount": len(differences)}

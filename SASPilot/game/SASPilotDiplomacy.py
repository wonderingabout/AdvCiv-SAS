# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: SASPilotDiplomacy: talking and trading with the other players as a player does: the diplomacy screen ('diplo', 'contact', 'reply'), deals and trades ('deals', 'canceldeal', 'bonustrade', 'techs', 'rivaltechs', 'trade', 'propose') and the relations between players ('relations').
# Split from SASPilotCommands.py on 2026-11-28, the second part moved out by topic, as Codex (GPT-6.2-Sol) proposed; the helpers other commands share, such as the diplomacy screen's state and _who, stay there and are reached as saspilot.
# SASPilotCommands.py loads it from beside itself, again whenever it changes, and adds its commands and help, so commands there that call one of these, such as 'endturn' calling 'diplo', still find it. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

from CvPythonExtensions import *
# <!-- custom: SASCurrentDefines reads PEACE_TREATY_LENGTH for a deal's turns to cancellation; time stamps a pending contact. (Claude code Opus 5.5) -->
import SASCurrentDefines
import time

gc = CyGlobalContext()

# <!-- custom: The loader binds the command module before the first command. (Claude code Opus 5.5) -->
saspilot = None

# <!-- custom: This module's command help, which the loader adds to the command module's. (Claude code Opus 5.5) -->
_HELP = {}


def _otherAiId(player, value):
	# <!-- custom: The AI a diplomacy command talks to: another living civilization, not human, that the player can contact; shared by 'contact', 'trade' and 'propose'. (Claude code Opus 5.5) -->
	iOther = saspilot._checkedPlayerId(value)
	if iOther >= gc.getMAX_CIV_PLAYERS() or iOther == player.getID() or gc.getPlayer(iOther).isHuman():
		raise ValueError("player %d is not an AI player the active player could contact" % iOther)
	if not player.canContact(iOther):
		raise ValueError("player %d cannot contact player %d" % (player.getID(), iOther))
	return iOther


_HELP["bonustrade"] = "The Foreign Advisor's Bonuses tab: our resources with how many we have (spare when more than one) and who would import each; and per leader met, whether our trade networks connect, the most gold per turn they would pay (when gold trading is open and they will talk), and which resources they would import from us, will export, won't export, and which we do not need. A resource sale or swap starts here; 'price' then asks the deal's price. args: player."


def cmd_bonustrade(args):
	# <!-- custom: The user advised at turn 111 of the turn-0 game (2026-11-14) trading spare resources actively, for gold or what we lack, and pointed to the Foreign Advisor's Bonuses tab and its hover over our resources ("Will import: Augustus (4)" in 1.514_foreign_advisor (2).JPG).
	# The agent had asked four leaders one by one with 'price' and learned only that nobody wanted a Pig.
	# This follows CvForeignAdvisor.drawResourceDeals (advc.036, advc.073) for an AI-facing player: the same tests, so what it lists is what the tab shows. (Claude code Opus 5.5) -->
	player = gc.getPlayer(saspilot._playerId(args))
	saspilot._requireOwnTeamUnderFog(args, player, "the resource trade table")
	team = gc.getTeam(player.getTeam())
	tradeData = TradeData()
	tradeData.ItemType = TradeableItems.TRADE_RESOURCES
	ours = []
	for iBonus in range(gc.getNumBonusInfos()):
		iCount = player.getNumTradeableBonuses(iBonus)
		if iCount > 0:
			ours.append({"bonus": gc.getBonusInfo(iBonus).getType(), "have": iCount, "importers": []})
	byBonus = dict([(entry["bonus"], entry) for entry in ours])
	leaders = []
	for iOther in range(gc.getMAX_PLAYERS()):
		other = gc.getPlayer(iOther)
		if iOther == player.getID() or not other.isAlive() or other.isBarbarian() or other.isMinorCiv() or not team.isHasMet(other.getTeam()):
			continue
		bWillTalk = bool(other.AI_isWillingToTalk(player.getID()))
		row = {"player": iOther, "name": other.getName(), "connected": bool(player.canTradeNetworkWith(iOther)), "willTalk": bWillTalk, "willImport": [], "willExport": [], "wontExport": [], "weDontNeed": []}
		if (team.isGoldTrading() or gc.getTeam(other.getTeam()).isGoldTrading()) and bWillTalk:
			row["maxGoldPerTurn"] = other.AI_maxGoldPerTurnTrade(player.getID())
		for iBonus in range(gc.getNumBonusInfos()):
			tradeData.iData = iBonus
			szBonus = gc.getBonusInfo(iBonus).getType()
			# <!-- custom: Would import: we can put it on the table, and it passes the AI's own test of a deal it would take (the tab's "surplus" test with bTestDenial). (Claude code Opus 5.5) -->
			if player.canTradeItem(iOther, tradeData, False) and player.canTradeItem(iOther, tradeData, not other.isHuman()):
				row["willImport"].append(szBonus)
				# <!-- custom: As the hover lists them: only leaders willing to talk, and with their overall gold-per-turn cap, labelled as such, not a price for this resource, which comes from CvPlayerAI::AI_goldForBonus and is not exposed to Python (Codex's review, round 36). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				if byBonus.has_key(szBonus) and bWillTalk:
					byBonus[szBonus]["importers"].append({"player": iOther, "name": other.getName(), "leaderMaxGoldPerTurn": row.get("maxGoldPerTurn")})
			if other.canTradeItem(player.getID(), tradeData, False):
				iDenial = other.getTradeDenial(player.getID(), tradeData)
				if iDenial == DenialTypes.DENIAL_JOKING:
					row["weDontNeed"].append(szBonus)
				elif iDenial == DenialTypes.NO_DENIAL and bWillTalk:
					row["willExport"].append(szBonus)
				else:
					row["wontExport"].append(szBonus)
		leaders.append(row)
	return {"ours": ours, "leaders": leaders}


def _dealItems(deal, bFirst):
	if bFirst:
		iLength = deal.getLengthFirstTrades()
	else:
		iLength = deal.getLengthSecondTrades()
	items = []
	for i in range(iLength):
		if bFirst:
			item = deal.getFirstTrade(i)
		else:
			item = deal.getSecondTrade(i)
		if not item:
			continue
		entry = {"item": saspilot._enumName(TradeableItems, item.ItemType), "data": item.iData}
		szWhat = saspilot._tradeDataName(item.ItemType, item.iData)
		if szWhat is not None:
			entry["what"] = szWhat
		items.append(entry)
	return items


_HELP["deals"] = "The Foreign Advisor's active deals: each running deal of ours, with the leader, the turn it began, what we give and what we get, by item as 'diplo' shows offers. A resource we export leaves our network: the capital's plot group subtracts it, so 'resources' reads it as unconnected. args: player."


def cmd_deals(args):
	# <!-- custom: At turn 125 of the turn-0 game (2026-11-14) the mined and roaded Iron diagonal to London read unconnected, and no city could train a Swordsman.
	# The trade network itself connected (two roaded plots, CvPlot::isTradeNetworkConnected); CvPlot::updatePlotGroupBonus subtracts the capital's exports, so a resource given away in a deal reads as missing.
	# SASPilot had no way to list deals, which the Foreign Advisor's Active tab shows a player (CvForeignAdvisor's deal loop). (Claude code Opus 5.5) -->
	player = gc.getPlayer(saspilot._playerId(args))
	iPlayer = player.getID()
	game = gc.getGame()
	deals = []
	for i in range(game.getIndexAfterLastDeal()):
		deal = game.getDeal(i)
		if deal.isNone():
			continue
		if deal.getFirstPlayer() == iPlayer:
			iOther = deal.getSecondPlayer()
			bWeFirst = True
		elif deal.getSecondPlayer() == iPlayer:
			iOther = deal.getFirstPlayer()
			bWeFirst = False
		else:
			continue
		deals.append({"id": deal.getID(), "with": iOther, "name": gc.getPlayer(iOther).getName(), "sinceTurn": deal.getInitialGameTurn(), "turnsToCancel": max(0, _dealTurnsToCancel(deal)), "weGive": _dealItems(deal, bWeFirst), "weGet": _dealItems(deal, not bWeFirst)})
	return {"deals": deals}


def _dealTurnsToCancel(deal):
	# <!-- custom: CvDeal::turnsToCancel, which Python cannot call: the deal's first turn plus PEACE_TREATY_LENGTH, less the current turn (advc.034 shortens it for a disengagement, which this leaves out, so for one it can say later than the game, never earlier, as Codex's review noted in round 37). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	return deal.getInitialGameTurn() + SASCurrentDefines.getInt("PEACE_TREATY_LENGTH") - gc.getGame().getGameTurn()


_HELP["canceldeal"] = "Cancel one of our deals, as the Foreign Advisor's cancel button does: it raises the same confirmation popup, which 'answer' then confirms (button 0) or declines (button 1). Refused before the game allows it ('deals' gives turnsToCancel) and for deals holding a vassal item. args: deal (ID from 'deals')."


def cmd_canceldeal(args):
	# <!-- custom: Our only Iron went to Gilgamesh inside a Pig sale at turn 118 of the turn-0 game (2026-11-14), and SASPilot could not cancel a deal.
	# CvDLLWidgetData::doDealKill tests CvDeal::isCancelable, then raises BUTTONPOPUP_DEAL_CANCELED, whose Yes sends the kill as a network message; isCancelable is not exposed, so its turn rule is checked here and vassal deals, which it may refuse, are left to the window. (Claude code Opus 5.5) -->
	player = gc.getPlayer(saspilot._activePlayerId())
	iDeal = int(args["deal"])
	deal = gc.getGame().getDeal(iDeal)
	if deal is None or deal.isNone() or player.getID() not in (deal.getFirstPlayer(), deal.getSecondPlayer()):
		raise ValueError("deal %d is not one of ours; see 'deals'" % iDeal)
	for bFirst in (True, False):
		for item in _dealItems(deal, bFirst):
			if item["item"] in ("TRADE_VASSAL", "TRADE_SURRENDER"):
				raise ValueError("deal %d holds a vassal item; cancel it from the Foreign Advisor" % iDeal)
	iTurns = _dealTurnsToCancel(deal)
	if iTurns > 0:
		raise ValueError("deal %d can be cancelled in %d turns" % (iDeal, iTurns))
	popupInfo = CyPopupInfo()
	popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_DEAL_CANCELED)
	popupInfo.setData1(iDeal)
	popupInfo.setOption1(False)
	popupInfo.addPopup(player.getID())
	return {"deal": iDeal, "popup": "BUTTONPOPUP_DEAL_CANCELED", "next": "'popups' lists it; 'answer' button 0 cancels the deal, 1 keeps it"}


_HELP["diplo"] = "The diplomacy screen, when an AI has contacted the player or the player has contacted an AI: open, who, the AI's line (aiComment type and text), the numbered replies the screen offers, and the deal on the table. 'reply n= screen=' answers, with this reply's screen number, which 'reply' requires. args: none."


def cmd_diplo(args):
	# <!-- custom: Seven AI contacts reached SASPilot's player in the 97-turn fog-on game (2026-11-13): tech offers, Open Borders, and Zara Yaqob pressing for Paganism, which refusing can anger.
	# They opened the diplomacy screen in the window, unseen; Moctezuma's first-contact screen was still open at turn 97. (Claude code Opus 5.5) -->
	state = saspilot._diploState()
	if not state["open"]:
		return {"open": False}
	diplo = CyDiplomacy()
	iWho = state["who"]
	result = {"open": True, "screen": saspilot._diploToken(state), "who": iWho, "whoName": gc.getPlayer(iWho).getName(), "aiComment": saspilot._typeOrNone(gc.getDiplomacyInfo, state["aiComment"]), "aiText": saspilot._plainText(state["aiText"]), "aiArgs": [saspilot._plainText(unicode(arg)) for arg in (state.get("aiArgs") or ())]}
	result["replies"] = [{"n": i, "comment": gc.getDiplomacyInfo(response["comment"]).getType(), "data1": response["data1"], "data2": response["data2"], "text": saspilot._plainText(response["text"])} for (i, response) in enumerate(state["responses"])]
	result["theyOffer"] = saspilot._diploOffer(diplo.getTheirTradeOffer)
	result["weOffer"] = saspilot._diploOffer(diplo.getPlayerTradeOffer)
	result["atWar"] = bool(diplo.atWar())
	# <!-- custom: Which conversation this is, counted as each begins (see CvDiplomacy.SASPilotScreen), so a client sequence such as SASPilotClient.py's 'price' can stop when another leader's screen takes over (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	result["conversation"] = state.get("conversation", 0)
	return result


_HELP["contact"] = "Open the diplomacy screen with an AI player, as clicking its leader does; then 'diplo' shows its greeting and the replies, such as declaring war or asking for peace, and 'reply' answers. The screen opens on the next frames. With give= and/or take= (items as on 'propose'), it opens on the trade table with that deal on it, as Ctrl+clicking the leader and clicking the items does; 'diplo' then lists Propose and 'What would you want?'. args: with (player ID), give (list), take (list)."


def cmd_contact(args):
	# <!-- custom: A person declares war or asks for peace by talking to a leader; CyPlayer.contact opens that screen (tested at turn 97 of the fog-on playthrough, 2026-11-13), so war and peace go through the screen's own replies instead of commands of their own. (Claude code Opus 5.5) -->
	player = gc.getPlayer(saspilot._activePlayerId())
	# <!-- custom: An out-of-range ID would reach GET_PLAYER in the DLL, and a human target is not what the screen is for here (Codex's review); the checks now live in _otherAiId, shared with 'trade' and 'propose'. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iOther = _otherAiId(player, args["with"])
	if saspilot._diploState()["open"]:
		raise ValueError("a diplomacy screen is already open; see 'diplo'")
	# <!-- custom: One queued contact at a time, so a second cannot replace the first's pending record (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if saspilot._pendingContact() is not None:
		raise ValueError("a contact is already queued; read 'diplo' once its screen opens")
	give = args.get("give", [])
	take = args.get("take", [])
	if not give and not take:
		player.contact(iOther)
		saspilot._state["contactPending"] = (iOther, False, time.clock())
		return {"contacted": saspilot._who(iOther)}
	# <!-- custom: With give= or take=, the screen opens on its trade table with those items on it, as Ctrl+clicking the leader and clicking the items does, so the screen's own replies answer the deal: Propose, and "What would you want?" with the AI's counter-offer, which 'propose' skips (2026-11-13). (Claude code Opus 5.5) -->
	szWeGive = ",".join([_tradeArg(item, player) for item in give])
	szTheyGive = ",".join([_tradeArg(item, gc.getPlayer(iOther)) for item in take])
	if not saspilot._pilotGame("tableSASPilotDeal").tableSASPilotDeal(player.getID(), iOther, szWeGive, szTheyGive):
		raise ValueError("not a deal player %d can put on the table with player %d: %s" % (player.getID(), iOther, _dealRefusal(player, gc.getPlayer(iOther), give, take) or "check the items against 'trade'"))
	saspilot._state["contactPending"] = (iOther, True, time.clock())
	return {"contacted": saspilot._who(iOther), "table": True}


_HELP["reply"] = "Answer the diplomacy screen with one of the replies 'diplo' lists, as clicking it does; returns the screen after, which may show a new AI line and replies or be closed. screen is the number 'diplo' gave: a reply to a screen that has changed since is refused. comment= names the reply instead of n (USER_DIPLOCOMMENT_ prefix optional), which is safer: the list changes with the table, such as FISH_FOR_DEAL and GIFT when only our side is filled. args: n, comment, screen."


def cmd_reply(args):
	# <!-- custom: Calls CvDiplomacy.handleUserResponse with the reply's comment and data, the same handler the EXE calls for a click, so war, peace, deals and the screen closing all follow the screen's own rules. (Claude code Opus 5.5) -->
	# <!-- custom: Through CvDiplomacyInterface, the module the EXE calls: BUG extends its handleUserResponse (Assets/Config/init.xml) to send its diplomacy events, which calling CvDiplomacy directly skipped (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	import CvDiplomacyInterface
	state = saspilot._diploState()
	if not state["open"]:
		raise ValueError("no diplomacy screen is open")
	# <!-- custom: Required, as Codex's review found a reply chosen from one 'diplo' could land on a newer screen, such as a second AI contact opening after the first closed; the replies list alone does not tell them apart. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: An older number is accepted when that screen showed exactly what this one shows (AI line, replies, both sides of the table): after a counter-offer the EXE refreshes the screen once more, and 'reply' to the screen 'diplo' had just read was refused as stale although nothing had changed (2026-11-13, screen 14 then 15). (Claude code Opus 5.5) -->
	if args.get("screen") is None:
		raise ValueError("screen is required; read 'diplo' for it")
	iScreen = int(args["screen"])
	content = saspilot._screenContent(state)
	if saspilot._state.get("diploSeen", {}).get(iScreen) != content:
		raise ValueError("the screen no longer shows what read %s showed; read 'diplo' again" % iScreen)
	if (("truncated", True),) in [item for side in content[-2:] for item in side]:
		raise ValueError("the deal has more than %d items on a side, too many to check; answer in the window" % saspilot.DIPLO_OFFER_MAX_ITEMS)
	# <!-- custom: The screen's partner as well, as Codex's review suggested: the count is per screen this module filled, and the partner is what the EXE shows now. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if CyDiplomacy().getWhoTradingWith() != state["who"]:
		raise ValueError("the screen is now with player %d, not %d; read 'diplo' again" % (CyDiplomacy().getWhoTradingWith(), state["who"]))
	# <!-- custom: By name too: at turn 128 of the turn-0 game (2026-11-14) the agent sent n=1 meaning "What would make this deal work?", as on a screen with both sides filled, but with only our Pig on the table the screen offers FISH_FOR_DEAL and GIFT, and reply 1 gave the Pig away. A comment names the reply, so a different list refuses instead of picking its neighbour. (Claude code Opus 5.5) -->
	comments = [gc.getDiplomacyInfo(response["comment"]).getType() for response in state["responses"]]
	if args.get("comment") is not None:
		szComment = args["comment"]
		if not szComment.startswith("USER_DIPLOCOMMENT_"):
			szComment = "USER_DIPLOCOMMENT_" + szComment
		if szComment not in comments:
			raise ValueError("%s is not offered; the screen offers %s" % (szComment, ", ".join(comments)))
		# <!-- custom: A name can be offered several times with different data, such as one TARGET_CITY reply per city; the first match was taken silently, and the right n for a later one was refused (Codex's review, round 37).
		# Such a name now needs n, which must name that reply. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		matches = [i for i in range(len(comments)) if comments[i] == szComment]
		if args.get("n") is not None:
			iN = int(args["n"])
			if iN not in matches:
				raise ValueError("n=%s is not %s; %s is reply %s" % (args["n"], szComment, szComment, ", ".join([str(i) for i in matches])))
		elif len(matches) > 1:
			raise ValueError("%s is offered %d times (replies %s, with different data); give n as well" % (szComment, len(matches), ", ".join([str(i) for i in matches])))
		else:
			iN = matches[0]
	else:
		iN = int(args["n"])
	if iN < 0 or iN >= len(state["responses"]):
		raise ValueError("reply %d is not offered; 'diplo' lists %d" % (iN, len(state["responses"])))
	response = state["responses"][iN]
	CvDiplomacyInterface.handleUserResponse((response["comment"], response["data1"], response["data2"]))
	return cmd_diplo({})


def _tradeTechs(giver, iReceiver):
	# <!-- custom: The techs giver could put on the table, by ID, with the AI's denial (None when it would trade). (Claude code Opus 5.5) -->
	result = {}
	# <!-- custom: Tech rows only: reading the whole table for them made 'techs' take 3.3 ms against 0.77 ms before the port (2026-11-13). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	for entry in saspilot.fromJson(saspilot._tradeItemsJson(giver, iReceiver, int(TradeableItems.TRADE_TECHNOLOGIES))):
		result[entry["data"]] = entry.get("denial")
	return result


_HELP["rivaltechs"] = "Met rivals' tech trees beside ours, as the tech screen shows which met civs know each tech. With one rival: the techs they know, the ones they could research next, what they have that we lack (to ask for), what we have that they lack (to offer), and races (one of their next techs that we research or queue). layout gives the tree by tech-screen column, each tech with who knows it ('us' and player IDs) and next:ID for a rival that could research it next; with several rivals (with=8,3 or with=all for every met one) the layout overlaps them all. args: with (player ID, list or all), player."


def cmd_rivaltechs(args):
	# <!-- custom: The user's idea at turn 65 of the islands replay (2026-11-15), just after first contact with Pericles: research a tech he lacks to trade for his, and lay the rivals' trees out beside ours, one or several overlapped, to reason about them. The tech screen shows which met civs know each tech, so these are a player's facts; what a rival researches now needs espionage ('research ahead=N' shows it then). (Claude code Opus 5.5) -->
	player = saspilot._player(args)
	ourTeam = gc.getTeam(player.getTeam())
	if args.get("with") is None:
		raise ValueError("this command needs with=<player ID>, a list or all; 'players' lists them")
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if str(args["with"]) == "all":
		rivals = [gc.getPlayer(i) for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isAlive() and i != player.getID() and gc.getPlayer(i).getTeam() != player.getTeam() and ourTeam.isHasMet(gc.getPlayer(i).getTeam())]
	else:
		rivals = []
		for szId in str(args["with"]).replace("[", "").replace("]", "").split(","):
			rival = gc.getPlayer(int(szId))
			if rival is None or rival.isNone() or not rival.isAlive():
				raise ValueError("no living player %s" % szId)
			if not ourTeam.isHasMet(rival.getTeam()):
				raise ValueError("%s is not met; their techs are not shown to us" % rival.getName())
			rivals.append(rival)
	if not rivals:
		raise ValueError("no met rival")
	# <!-- custom: CyPlayer has no queue list; isResearchingTech covers the current tech and the queue (a first version called a getResearchQueueTech that does not exist). (Claude code Opus 5.5) -->
	queued = {}
	for i in range(gc.getNumTechInfos()):
		if player.isResearchingTech(i):
			queued[i] = True
	columns = {}
	single = len(rivals) == 1
	known, nextUp, weLack, theyLack, races = [], [], [], [], []
	for i in range(gc.getNumTechInfos()):
		info = gc.getTechInfo(i)
		holders = []
		if ourTeam.isHasTech(i):
			holders.append("us")
		nexts = []
		for rival in rivals:
			bThem = gc.getTeam(rival.getTeam()).isHasTech(i)
			if bThem:
				holders.append(str(rival.getID()))
			elif rival.canResearch(i, False):
				nexts.append("next:%d" % rival.getID())
			if single:
				if bThem:
					known.append(info.getType())
					if not ourTeam.isHasTech(i):
						weLack.append({"tech": info.getType(), "xmlTradeable": bool(info.isTrade())})
				elif rival.canResearch(i, False):
					nextUp.append(info.getType())
					if queued.has_key(i):
						races.append(info.getType())
				# <!-- custom: Each with the XML trade flag: SAS turns it off for Writing and The Wheel, so Writing, the one tech we had and Pericles lacked, was never on the trade screen. (Claude code Opus 5.5) -->
				if ourTeam.isHasTech(i) and not bThem:
					theyLack.append({"tech": info.getType(), "xmlTradeable": bool(info.isTrade())})
		if holders or nexts:
			columns.setdefault(info.getGridX(), []).append("%s[%s]" % (info.getType()[5:], ",".join(holders + nexts)))
	layout = ["col %d: %s" % (iColumn, " ".join(columns[iColumn])) for iColumn in sorted(columns.keys())]
	result = {"with": [{"player": rival.getID(), "name": rival.getName()} for rival in rivals], "layout": layout}
	if single:
		result.update({"knownCount": len(known), "next": nextUp, "theyHaveWeLack": weLack, "weHaveTheyLack": theyLack, "races": races})
	return result


_HELP["techs"] = "The tech market across the players met: each tech the player lacks that some of them have, with its research cost, whether the XML lets it be traded at all (bTrade; SAS turns that off for some techs), and per holder whether it can be traded now and the AI's answer (DENIAL_ type, or null when it would trade). Then the techs we can research that none of them has (nobodyHas, research these and trade them on; unseenPlayers counts met players whose techs the fog hides), and per player met, the techs the player could give them. A holder at war ('atWar') can still answer for a tech put in the same deal as a peace treaty, as the diplomacy screen allows. args: player."


def cmd_techs(args):
	# <!-- custom: Buying techs well needs the whole market: who has what, which techs the XML forbids trading (32 in SAS by bTrade, such as Bronze Working, Iron Working, Engineering, Gunpowder and Code of Laws), and which holder would trade.
	# 'trade' answered one leader at a time; the user asked for a view to get the best deals (2026-11-13). (Claude code Opus 5.5) -->
	player = saspilot._player(args)
	team = gc.getTeam(player.getTeam())
	# <!-- custom: Under fog, as the Foreign Advisor's tech tab shows it (CvForeignAdvisor.py): a met player's techs only when canSeeTech allows, and a tech they hold but cannot trade only when we could research it.
	# The first version listed every met player's techs, which Codex's review found reveals more than the window (2026-11-13). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iFogTeam = saspilot._fogTeam(args)
	if iFogTeam >= 0 and player.getTeam() != iFogTeam:
		raise ValueError("with fog on, 'techs' is only for the viewing team")
	others = [gc.getPlayer(i) for i in range(gc.getMAX_CIV_PLAYERS()) if i != player.getID() and gc.getPlayer(i).isAlive() and not gc.getPlayer(i).isBarbarian() and not gc.getPlayer(i).isMinorCiv() and team.isHasMet(gc.getPlayer(i).getTeam())]
	iMet = len(others)
	if iFogTeam >= 0:
		others = [other for other in others if player.canSeeTech(other.getID())]
	wanted = []
	nobodyHas = []
	offers = dict([(other.getID(), []) for other in others])
	# <!-- custom: One C++ table read per player and direction, rather than canTradeItem and getTradeDenial per tech and player. (Claude code Opus 5.5) -->
	theyCan = dict([(other.getID(), _tradeTechs(other, player.getID())) for other in others])
	weCan = dict([(other.getID(), _tradeTechs(player, other.getID())) for other in others])
	for iTech in range(gc.getNumTechInfos()):
		info = gc.getTechInfo(iTech)
		if team.isHasTech(iTech):
			for other in others:
				if iTech in weCan[other.getID()]:
					offers[other.getID()].append(info.getType())
			continue
		holders = []
		for other in others:
			if not gc.getTeam(other.getTeam()).isHasTech(iTech):
				continue
			entry = {"player": other.getID(), "name": other.getName(), "atWar": bool(team.isAtWar(other.getTeam())), "canTrade": iTech in theyCan[other.getID()]}
			if iFogTeam >= 0 and not entry["canTrade"] and not player.canResearch(iTech, False):
				continue
			if entry["canTrade"] and not other.isHuman():
				entry["denial"] = theyCan[other.getID()][iTech]
				# <!-- custom: canTradeItem says the tech may go in a deal, not that its holder would: the advisor marks "Will Trade" only with no denial and a leader willing to talk (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				entry["willTalk"] = bool(other.AI_isWillingToTalk(player.getID()))
			holders.append(entry)
		if holders:
			wanted.append({"tech": info.getType(), "cost": team.getResearchCost(iTech), "progress": team.getResearchProgress(iTech), "xmlTradeable": bool(info.isTrade()), "canResearch": bool(player.canResearch(iTech, False)), "holders": holders})
		# <!-- custom: Techs we can research that no player listed here has: the user pointed out at turn 139 of the turn-0 game (2026-11-14) that the agent kept researching techs every neighbour had, which trade buys far cheaper (Zara sold Philosophy, 425 beakers, for 70 gold), while a tech nobody has can be traded to several leaders.
		# Players whose techs the fog hides are not listed, so 'unseenPlayers' says how many could still hold these. (Claude code Opus 5.5) -->
		elif player.canResearch(iTech, False):
			nobodyHas.append({"tech": info.getType(), "cost": team.getResearchCost(iTech), "progress": team.getResearchProgress(iTech), "xmlTradeable": bool(info.isTrade())})
	weCouldGive = []
	for other in others:
		entry = {"player": other.getID(), "name": other.getName(), "techs": offers[other.getID()]}
		# <!-- custom: The gold each leader could pay at once, as the Foreign Advisor's Techs tab shows it under its coin column (AI_maxGoldTrade, when either side has gold trading and the leader will talk): the user pointed to the tab at turn 140 of the turn-0 game (2026-11-14), where Zara Yaqob held 590, a buyer for a tech nobody else has. (Claude code Opus 5.5) -->
		if not other.isHuman() and other.AI_isWillingToTalk(player.getID()) and (team.isGoldTrading() or gc.getTeam(other.getTeam()).isGoldTrading()):
			entry["maxGoldTrade"] = other.AI_maxGoldTrade(player.getID())
		weCouldGive.append(entry)
	return {"wanted": wanted, "nobodyHas": nobodyHas, "unseenPlayers": iMet - len(others), "weCouldGive": weCouldGive}


_HELP["trade"] = "The two columns of the diplomacy screen with another player: what each side could put on the table, techsNotOffered (techs they hold and we lack that are off the table, each with why: bTrade off in the XML, a prerequisite we lack, or the game's trade rules), tradeRoutes (whether a route with them can exist: a foreign trade route needs open borders or other free trade, the partner city revealed to us and our trade networks connected, so exploring finds partners; resource trades follow a stricter rule, CvPlayer::canTradeNetworkWith with advc.124, where their city must also reach their own capital, given as bonustrade's connected), and for each item the other player would not give, the game's reason (DENIAL_ type). Gold is the most each side could give. args: with (player ID), player."


def cmd_trade(args):
	# <!-- custom: The AI announced "Pacal II will trade Agriculture, Mysticism" in the fog-on playthrough (2026-11-13), but SASPilot could not see the diplomacy screen's table.
	# These are the same per-item checks the screen makes (canTradeItem, getTradeDenial); proposing a deal is not covered. (Claude code Opus 5.5) -->
	player = saspilot._player(args)
	other = gc.getPlayer(_otherAiId(player, args["with"]))
	# <!-- custom: Which kinds of trade each side's techs allow, and the techs that allow each, read from the XML (CvTechInfo's is*Trading flags) so a mod-mod or other rules are followed: the user asked at turn 73 of the islands replay (2026-11-15), recalling Writing and Currency from BtS.
	# A kind counts when either team has it, as CvPlayer::canTradeItem asks for techs. (Claude code Opus 5.5) -->
	ourTeam = gc.getTeam(player.getTeam())
	theirTeam = gc.getTeam(other.getTeam())
	rules = {}
	for (szKind, szTeam, szTech) in (("tech", "isTechTrading", "isTechTrading"), ("gold", "isGoldTrading", "isGoldTrading"), ("maps", "isMapTrading", "isMapTrading"), ("openBorders", "isOpenBordersTrading", "isOpenBordersTrading"), ("defensivePact", "isDefensivePactTrading", "isDefensivePactTrading"), ("permanentAlliance", "isPermanentAllianceTrading", "isPermanentAllianceTrading"), ("vassalState", "isVassalStateTrading", "isVassalStateTrading")):
		rules[szKind] = {"us": bool(getattr(ourTeam, szTeam)()), "them": bool(getattr(theirTeam, szTeam)()), "enabledBy": [gc.getTechInfo(i).getType() for i in range(gc.getNumTechInfos()) if getattr(gc.getTechInfo(i), szTech)()]}
	result = {"we": saspilot.RawJson(saspilot._tradeItemsJson(player, other.getID())), "they": saspilot.RawJson(saspilot._tradeItemsJson(other, player.getID())), "attitude": saspilot._enumName(AttitudeTypes, other.AI_getAttitude(player.getID())), "tradeRules": rules}
	# <!-- custom: At turn 54 of the 2026-11-19 validation run Cyrus held The Wheel and Construction but 'trade' listed neither, with no reason; the Foreign Advisor's tech tab showed The Wheel has bTrade off in SAS and Construction needs The Wheel first.
	# So each tech they hold, that we lack and that is off the table, comes with why, from the XML flag and our prerequisites, as the advisor shows them (only when we can see their techs). (Claude code Opus 5.5) -->
	if player.canSeeTech(other.getID()):
		offered = _tradeTechs(other, player.getID())
		notOffered = []
		for iTech in range(gc.getNumTechInfos()):
			if ourTeam.isHasTech(iTech) or not theirTeam.isHasTech(iTech) or iTech in offered:
				continue
			info = gc.getTechInfo(iTech)
			if not info.isTrade():
				szWhy = "not tradeable: bTrade is off in the XML"
			elif not player.canResearch(iTech, False):
				szWhy = "we lack a prerequisite; 'tech type=%s' gives the path" % info.getType()
			else:
				szWhy = "refused by the game's trade rules (CvPlayer::canTradeItem)"
			notOffered.append({"tech": info.getType(), "why": szWhy})
		result["techsNotOffered"] = notOffered
	# <!-- custom: The user at turn 54 of the 2026-11-19 validation run: trade routes depend on exploration.
	# The DLL agrees (CvCity::updateTradeRoutes, CvPlayer::canHaveTradeRoutesWith): a foreign city can be a route partner only with open borders or other free trade, when the city is revealed to us (advc.124), and when our trade networks connect.
	# So each civ's reply says which of these hold: routes allowed at all, its cities we have seen, and those our capital's network reaches. (Claude code Opus 5.5) -->
	capital = player.getCapitalCity()
	seen = [city for city in saspilot._cities(other) if city.isRevealed(player.getTeam(), False)]
	connected = []
	if capital is not None and not capital.isNone():
		connected = [city.getName() for city in seen if capital.plot().isTradeNetworkConnected(city.plot(), player.getTeam())]
	result["tradeRoutes"] = {"allowed": bool(player.canHaveTradeRoutesWith(other.getID())), "openBorders": bool(ourTeam.isOpenBorders(other.getTeam())), "citiesSeen": [city.getName() for city in seen], "connected": connected}
	return result


def _tradeArg(szItem, giver):
	# <!-- custom: An item as "TRADE_KIND" or "TRADE_KIND:data", data being what 'trade' shows under "what" (an XML type or a city name) or a number (gold, a team); turned into the "kind:data" numbers proposeSASPilotDeal reads. (Claude code Opus 5.5) -->
	if ":" in szItem:
		(szKind, szData) = szItem.split(":", 1)
	else:
		(szKind, szData) = (szItem, "0")
	eKind = int(saspilot._enum(TradeableItems, szKind))
	table = saspilot._TRADE_INFO_TABLES.get(eKind)
	if szData.lstrip("-").isdigit():
		iData = int(szData)
	elif eKind == int(TradeableItems.TRADE_CITIES):
		iData = saspilot._city({"city": szData, "player": giver.getID()}).getID()
	elif table is not None:
		iData = saspilot._typedIndex(szData, table[0], getattr(gc, table[1])(), getattr(gc, table[2]))
	else:
		raise ValueError("%s takes a number, not %s" % (szKind, szData))
	return "%d:%d" % (eKind, iData)


_TRADE_ITEMS_WITH_ID = (int(TradeableItems.TRADE_CITIES), int(TradeableItems.TRADE_PEACE), int(TradeableItems.TRADE_WAR), int(TradeableItems.TRADE_EMBARGO))


def _dealRefusal(player, other, give, take):
	# <!-- custom: Both deal commands said only "check the items against 'trade'" when the DLL refused: on 2026-11-22 (JOAO turn-120 save) TECH_FEUDALISM, offered to Huayna Capac at turn 115, had left our list as he got it elsewhere, and the message named neither the item nor why.
	# Names each item missing from its giver's list in 'trade' (the same C++ list), or gold above what the giver can pay; None when every item is listed, as the refusal then has another cause, such as the turn being over. (Claude code Opus 5.5) -->
	missing = []
	for (giver, receiver, items, szSide) in ((player, other, give, "we give"), (other, player, take, "they give")):
		listed = saspilot.fromJson(saspilot._tradeItemsJson(giver, receiver.getID()))
		for szItem in items:
			(iKind, iData) = [int(x) for x in _tradeArg(szItem, giver).split(":")]
			szKind = szItem.split(":")[0]
			rows = [row for row in listed if int(saspilot._enum(TradeableItems, row["item"])) == iKind]
			if szKind in ("TRADE_GOLD", "TRADE_GOLD_PER_TURN"):
				if not rows or iData > rows[0]["data"]:
					missing.append("%s (%s): at most %s" % (szItem, szSide, rows and rows[0]["data"] or 0))
				continue
			if iKind in saspilot._TRADE_INFO_TABLES or iKind in _TRADE_ITEMS_WITH_ID:
				rows = [row for row in rows if row["data"] == iData]
			if not rows:
				missing.append("%s (%s): not tradeable now" % (szItem, szSide))
			elif rows[0].get("denial"):
				missing.append("%s (%s): %s" % (szItem, szSide, rows[0]["denial"]))
	if not missing:
		return None
	return "; ".join(missing)


_HELP["propose"] = "Propose a deal to an AI, as the diplomacy screen's Propose button does: the AI accepts or refuses, and an accepted deal is handed to the game to carry out ('accepted' is the AI's answer; the deal itself can still be refused by the game, so read the result back). Not in network games. Items as on 'trade', e.g. give=[\"TRADE_TECHNOLOGIES:TECH_METAL_CASTING\"] take=[\"TRADE_TECHNOLOGIES:TECH_MYSTICISM\",\"TRADE_OPEN_BORDERS\"]; data is a type, a city name, a team or an amount. args: with (player ID), give (list), take (list), player."


def cmd_propose(args):
	# <!-- custom: The second half of trading after 'trade' (fog-on playthrough, 2026-11-13); asking the AI and making the deal need the DLL, see proposeSASPilotDeal in CvGameInterface.cpp. (Claude code Opus 5.5) -->
	player = saspilot._player(args)
	other = gc.getPlayer(_otherAiId(player, args["with"]))
	szWeGive = ",".join([_tradeArg(item, player) for item in args.get("give", [])])
	szTheyGive = ",".join([_tradeArg(item, other) for item in args.get("take", [])])
	text = saspilot._pilotGame("proposeSASPilotDeal").proposeSASPilotDeal(player.getID(), other.getID(), szWeGive, szTheyGive)
	# <!-- custom: sas-ci-string-compare-exemption: The DLL bridge returns the JSON null sentinel as text. (GPT-6.2-Sol) -->
	if text == "null":
		raise ValueError("not a deal player %d can propose to player %d: %s" % (player.getID(), other.getID(), _dealRefusal(player, other, args.get("give", []), args.get("take", [])) or "check the items against 'trade'"))
	result = saspilot.fromJson(text)
	result["with"] = saspilot._who(other.getID())
	return result


def _addRelationLink(edge, source, target):
	# <!-- custom: The F3 links are team relationships.
	# Keep direction for vassalage and retain both treaties when the screen draws two lines. (GPT-6.1-Sol) -->
	iTarget = target.getID()
	edge["sameTeam"] = source.getID() == iTarget
	edge["vassalOfTarget"] = bool(source.isVassal(iTarget))
	edge["openBorders"] = bool(source.isOpenBorders(iTarget))
	edge["defensivePact"] = bool(source.isDefensivePact(iTarget))


_HELP["relations"] ="Each player met, for weighing whom to please or anger: attitude toward the player, whether they will talk, war, peace treaty, open borders and defensive pact, the shortest distance between the two empires' cities and how many of their cities lie within 10 plots of ours, their score, their power against ours in per mille (powerRatioPerMille, 1489 is 1.489 times ours) wherever the scoreboard shows that ratio, and without fog their power. With graph=1 return player nodes and directed attitude edges, keyed by IDs. args: graph, player."


def cmd_relations(args):
	# <!-- custom: Refusing Roosevelt's demand to stop trading with Kublai at turn 265 (2026-11-14) was weighed on power alone; the user pointed out that attitude and nearness matter as much: angering a strong rival far away costs less than angering a weak neighbour.
	# One reply now gives them side by side.
	# Under fog, distances use only the cities the player has seen, and power, which the window shows only through espionage, is left out. (Claude code Opus 5.5) -->
	player = saspilot._player(args)
	saspilot._requireOwnTeamUnderFog(args, player, "relations")
	team = gc.getTeam(player.getTeam())
	iFogTeam = saspilot._fogTeam(args)
	ours = saspilot._cities(player)
	result = []
	bGraph = bool(args.get("graph"))
	nodes = [{"id": player.getID(), "team": player.getTeam(), "name": player.getName()}]
	edges = []
	for iOther in range(gc.getMAX_CIV_PLAYERS()):
		other = gc.getPlayer(iOther)
		if iOther == player.getID() or not other.isAlive() or other.isBarbarian() or not team.isHasMet(other.getTeam()):
			continue
		if bGraph and other.isMinorCiv():
			continue
		# <!-- custom: The city, not its plot: a plot seen before the city was founded on it counted the city, so Gilgamesh's city 4 plots away was in citiesSeen and closestCityDistance while 'map' showed none (Codex's review, round 35).
		# The window shows a city once the city itself is revealed, as 'map' and 'cities' check. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		theirs = [city for city in saspilot._cities(other) if iFogTeam < 0 or city.isRevealed(iFogTeam, False)]
		distances = [plotDistance(a.getX(), a.getY(), b.getX(), b.getY()) for a in ours for b in theirs]
		near = [b for b in theirs if [a for a in ours if plotDistance(a.getX(), a.getY(), b.getX(), b.getY()) <= 10]]
		entry = {"player": iOther, "name": other.getName(), "team": other.getTeam(), "attitude": saspilot._enumName(AttitudeTypes, other.AI_getAttitude(player.getID())), "willTalk": bool(other.AI_isWillingToTalk(player.getID())), "atWar": bool(team.isAtWar(other.getTeam())), "peaceTreaty": bool(team.isForcePeace(other.getTeam())), "openBorders": bool(team.isOpenBorders(other.getTeam())), "defensivePact": bool(team.isDefensivePact(other.getTeam())), "score": gc.getGame().getPlayerScore(iOther), "citiesSeen": len(theirs), "citiesWithin10": len(near)}
		if distances:
			entry["closestCityDistance"] = min(distances)
		if iFogTeam < 0:
			entry["power"] = other.getPower()
		# <!-- custom: Their power against ours, as the scoreboard shows it beside each leader (1.9 is nearly twice as strong) wherever canSeeDemographics allows, which is the scoreboard's own condition (CvMainInterface, K-Mod), so under fog too: the user pointed to the scoreboard at turn 90 of the turn-0 game (2026-11-14), where Gilgamesh showed 1.9 and Zara Yaqob 2.0, while this command left power out under fog. (Claude code Opus 5.5) -->
		# <!-- custom: The attitude's modifiers as the hover over a met leader lists them (CvGameTextMgr::getAttitudeString), such as border tension or a shared religion: the user advised at turn 100 of the turn-0 game (2026-11-14) that settling by a strong neighbour, as Hastings was, costs attitude, and that these modifiers show it, so settling and trading choices can steer them.
		# Plain lines, the first being the attitude itself. (Claude code Opus 5.5) -->
		entry["attitudeModifiers"] = [szLine for szLine in saspilot._plainText(CyGameTextMgr().getAttitudeString(iOther, player.getID())).split(u"\n") if szLine.strip()]
		# <!-- custom: In integer per mille (1489 for 1.489): a float came back as 1.4889999628067017, as Direct3D sets the FPU to single precision inside Civ4 (as for time.time(), see KI#1093). (Claude code Opus 5.5) -->
		if (iFogTeam < 0 or player.canSeeDemographics(iOther)) and player.getPower() > 0:
			entry["powerRatioPerMille"] = other.getPower() * 1000 / player.getPower()
		# <!-- custom: How this leader sees each other player we have met, as the Foreign Advisor's Glance tab shows it; the user noted attitudes are not symmetric (2026-11-14), and a weak target is best one its own neighbours dislike, so none comes to its aid. (Claude code Opus 5.5) -->
		if bGraph:
			nodes.append({"id": iOther, "team": other.getTeam(), "name": other.getName()})
		views = {}
		for iThird in range(gc.getMAX_CIV_PLAYERS()):
			third = gc.getPlayer(iThird)
			if iThird == iOther or not third.isAlive() or third.isBarbarian() or not gc.getTeam(other.getTeam()).isHasMet(third.getTeam()):
				continue
			if iThird != player.getID() and not team.isHasMet(third.getTeam()):
				continue
			if bGraph and third.isMinorCiv():
				continue
			# <!-- custom: The Glance tab's cell, not just the category: the user had the agent compare the tab with this reply at turn 127 of the turn-0 game (2026-11-14), and it showed numbers (+11 against +1 for the same Cautious-to-Pleased range), the worst-enemy icon, war and forced peace, and whether the leader would join a war against that player if asked (advc.152), all of which help pick a war target and its likely friends.
			# Computed as AttitudeUtil.getAttitudeText does. (Claude code Opus 5.5) -->
			otherTeam = gc.getTeam(other.getTeam())
			bSameTeam = other.getTeam() == third.getTeam()
			cell = {"attitude": saspilot._enumName(AttitudeTypes, other.AI_getAttitude(iThird))[9:], "value": saspilot._attitudeCount(iOther, iThird), "worstEnemy": bool(not bSameTeam and not otherTeam.isHuman() and other.getWorstEnemyName() and other.getWorstEnemyName() == gc.getTeam(third.getTeam()).getName()), "atWar": bool(otherTeam.isAtWar(third.getTeam()))}
			# <!-- custom: Only the guards AttitudeUtil.getAttitudeText applies: forced peace only where our team is one side, and the war-trade test only between two other teams, neither human, not the same team.
			# The first version asked a team to declare war on its own teammate, which trips AI_declareWarTrade's assertions, and showed peace between two third parties, which the tab hides (Codex's review, round 37). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			if third.getTeam() == player.getTeam() and otherTeam.isForcePeace(third.getTeam()):
				cell["peaceTreaty"] = True
			if not bSameTeam and other.getTeam() != player.getTeam() and third.getTeam() != player.getTeam() and not otherTeam.isHuman() and not cell["atWar"] and otherTeam.AI_declareWarTrade(third.getTeam(), player.getTeam()) == -1:
				cell["wouldJoinWarIfAsked"] = True
			if bGraph:
				_addRelationLink(cell, otherTeam, gc.getTeam(third.getTeam()))
				cell["from"] = iOther
				cell["to"] = iThird
				edges.append(cell)
			else:
				views[third.getName()] = cell
		if bGraph:
			edge = {"from": player.getID(), "to": iOther, "atWar": entry["atWar"], "peaceTreaty": entry["peaceTreaty"]}
			_addRelationLink(edge, team, gc.getTeam(other.getTeam()))
			edges.append(edge)
		else:
			entry["viewsOf"] = views
		entry["attitudeValue"] = saspilot._attitudeCount(iOther, player.getID())
		result.append(entry)
	if bGraph:
		return {"viewer": player.getID(), "turn": gc.getGame().getGameTurn(), "nodes": nodes, "edges": edges}
	result.sort(lambda a, b: cmp(a.get("closestCityDistance", 999), b.get("closestCityDistance", 999)))
	return {"ourScore": gc.getGame().getPlayerScore(player.getID()), "players": result}

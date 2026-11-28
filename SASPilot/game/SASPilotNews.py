# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: SASPilotNews: the news every SASPilot reply carries, what changed for the active player since the previous reply, as a person sees it on the screen: a new turn, a tech learned, a city grown or in disorder, a building finished, a war declared, the score rank (the user's idea, 2026-11-28, after 'pythonErrors').
# The purpose, in the user's words: an agent sees the game as a player does, acting, reading the state as text, and receiving news about what changed.
# Before, it learned of these only by asking 'turn', 'cities' or 'relations', and the AI's turn changes several at once.
# Named news: the first name, changes, the user found too generic, as a change can go forward or backward and be the agent's own action or something that happened to it; updates and feedback were weighed too, but updates still means some intervention, active or passive, and feedback reads as a reaction to the agent's order.
# News is what a person hears about between orders, good or bad, whoever caused it.
# SASPilotCommands.py loads this file from disk, as it loads SASPilotUI.py, again whenever it changes; 'saspilot' in this module's namespace is that command module, whose helpers and session state this one uses. (Claude code Opus 5.5) -->

from CvPythonExtensions import *

gc = CyGlobalContext()

# <!-- custom: The loader binds the command module before the first call. (Claude code Opus 5.5) -->
saspilot = None

# <!-- custom: Bump when the snapshot's fields change. (Claude code Opus 5.5) -->
SNAPSHOT_FORMAT = 7

# <!-- custom: The most messages one reply's news carries; 'messages' gives them all. (Claude code Opus 5.5) -->
MESSAGES_SHOWN = 20


def report(reply, requestArgs):
	# <!-- custom: Sets reply['news'] and the baseline the poll keeps once the reply is written; SASPilotCommands' _reportNews calls it once the game is initialized, and reports what it raises as newsError. (Claude code Opus 5.5) -->
	iPlayer = saspilot._activePlayerId()
	# <!-- custom: The request's own fog=1 counts too, as for its result: read from the session alone, a full-view session's request with fog=1 got a rank counting unmet rivals (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	iFogTeam = saspilot._fogTeam(requestArgs)
	previous = saspilot._state.get("newsSnapshot")
	# <!-- custom: Messages from the turn before the previous snapshot's on, so a gap of several turns between replies keeps those still in the game's list: read from the turn before this one only, a reply at turn 323 after one at 320 lost turn 321's (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	iMessagesSince = gc.getGame().getGameTurn() - 1
	if previous is not None and previous["turn"] - 1 < iMessagesSince:
		iMessagesSince = previous["turn"] - 1
	snapshot = _snapshot(iPlayer, iFogTeam, iMessagesSince)
	# <!-- custom: The fog is part of the baseline, so switching from the full view to fog starts a new one rather than reporting the full view's rank as a change (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	snapshot["key"] = snapshot["key"] + (iFogTeam >= 0,)
	# <!-- custom: A first reply, a loaded save or another active player starts a new baseline and reports nothing, as its differences would be the whole game. (Claude code Opus 5.5) -->
	if previous is not None and previous["key"] == snapshot["key"]:
		news = _between(previous, snapshot)
		if news:
			reply["news"] = news
	reply["_newsSnapshot"] = snapshot


def _snapshot(iPlayer, iFogTeam, iMessagesSince):
	# <!-- custom: Only what the player's own screens show: its cities, techs, wars and Great People, and the score of the players the scoreboard lists (all of them without fog, the met ones with fog), so the rank never counts a player not yet met. (Claude code Opus 5.5) -->
	game = gc.getGame()
	player = gc.getPlayer(iPlayer)
	iTeam = player.getTeam()
	team = gc.getTeam(iTeam)
	cities = {}
	# <!-- custom: With the building each city is producing, so the next snapshot can tell it was finished: scanning every building of every city each reply would cost about 200 calls per city. (Claude code Opus 5.5) -->
	# <!-- custom: And whether it starves, as the city bar shows in red, beside disorder. (Claude code Opus 5.5) -->
	for city in saspilot._cities(player):
		cities[city.getID()] = (city.getName(), city.getPopulation(), bool(city.isDisorder()), city.getProductionBuilding(), city.foodDifference(True) < 0)
	techs = [iTech for iTech in range(gc.getNumTechInfos()) if team.isHasTech(iTech)]
	# <!-- custom: Religions, corporations and world wonders anywhere, as the game announces each to every player, met or not ("completed in a distant land"). (Claude code Opus 5.5) -->
	religions = [iReligion for iReligion in range(gc.getNumReligionInfos()) if game.isReligionFounded(iReligion)]
	corporations = [iCorporation for iCorporation in range(gc.getNumCorporationInfos()) if game.isCorporationFounded(iCorporation)]
	wonders = [iClass for iClass in _worldWonderClasses() if game.getBuildingClassCreatedCount(iClass) > 0]
	# <!-- custom: The messages the player received, the ones the window shows at its top left and in the Event Log (the user's question, 2026-11-28), from iMessagesSince on, as messages made as a turn starts carry that turn; 'turn' and 'messages' read the same list. (Claude code Opus 5.5) -->
	# <!-- custom: Each with its type, such as COMBAT_MESSAGE for a Combat Log line or MAJOR_EVENT, so news can be told apart without reading the text: the Event Log and the Combat Log draw from this one list (the user, 2026-11-28). (Claude code Opus 5.5) -->
	messages = [(message["turn"], message["text"], message["x"], message["y"], message["messageType"]) for message in saspilot.cmd_messages({"player": iPlayer, "since": iMessagesSince})]
	# <!-- custom: Each war's team with its name, kept here: a team eliminated since has no name to read, and its war ended as "war ended with " with nothing after it (turn 320 of the Asoka save, 2026-11-28). (Claude code Opus 5.5) -->
	wars = {}
	# <!-- custom: The teams ours is a vassal of, with their names, as the scoreboard and Foreign Advisor show it. (Claude code Opus 5.5) -->
	masters = {}
	for iOtherTeam in range(gc.getMAX_CIV_TEAMS()):
		if iOtherTeam != iTeam and gc.getTeam(iOtherTeam).isAlive() and team.isVassal(iOtherTeam):
			masters[iOtherTeam] = gc.getTeam(iOtherTeam).getName()
	# <!-- custom: The resources the player has, as the resource bar shows them, so one gained by a trade, a connection or a discovery, or lost to a pillage or a cancelled deal, is news. (Claude code Opus 5.5) -->
	bonuses = [iBonus for iBonus in range(gc.getNumBonusInfos()) if player.getNumAvailableBonuses(iBonus) > 0]
	civics = [player.getCivics(iOption) for iOption in range(gc.getNumCivicOptionInfos())]
	scores = []
	# <!-- custom: The rank counts the living major civilizations, with fog only the met ones; the scoreboard's own list also follows BUG options such as Show Minor Civs and dead civs, which the first version did not, counting a met minor civilization the scoreboard hid (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	for iOther in range(gc.getMAX_CIV_PLAYERS()):
		other = gc.getPlayer(iOther)
		if not other.isAlive() or other.isMinorCiv():
			continue
		if iOther == iPlayer or iFogTeam < 0 or team.isHasMet(other.getTeam()):
			scores.append((game.getPlayerScore(iOther), iOther))
	for iOtherTeam in range(gc.getMAX_CIV_TEAMS()):
		if iOtherTeam != iTeam and gc.getTeam(iOtherTeam).isAlive() and team.isAtWar(iOtherTeam):
			wars[iOtherTeam] = gc.getTeam(iOtherTeam).getName()
	scores.sort()
	scores.reverse()
	# <!-- custom: No rank for an eliminated active player, who is not in the list: .index raised, so no other news came either (Codex reproduced it). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	iRank = None
	rankedPlayers = [entry[1] for entry in scores]
	if iPlayer in rankedPlayers:
		iRank = rankedPlayers.index(iPlayer) + 1
	# <!-- custom: The key's first part is the snapshot's format: a baseline kept from before a change to this file, such as the city tuples gaining their production, starts a new one rather than failing to compare. (Claude code Opus 5.5) -->
	return {"key": (SNAPSHOT_FORMAT, saspilot._state.get("loads"), iPlayer), "turn": game.getGameTurn(), "cities": cities, "techs": techs, "research": player.getCurrentResearch(), "era": player.getCurrentEra(), "goldenAge": bool(player.isGoldenAge()), "greatPeople": player.getGreatPeopleCreated(), "units": player.getNumUnits(), "wars": wars, "rank": iRank, "ranked": len(scores), "religions": religions, "corporations": corporations, "wonders": wonders, "gameState": int(game.getGameState()), "winner": game.getWinner(), "victory": game.getVictory(), "messages": messages, "messagesSince": iMessagesSince, "masters": masters, "bonuses": bonuses, "civics": civics, "anarchy": bool(player.isAnarchy()), "stateReligion": player.getStateReligion(), "treasuryShort": player.getGold() + player.calculateGoldRate() < 0, "strike": bool(player.isStrike())}


def _worldWonderClasses():
	# <!-- custom: The building classes with a global limit, world wonders, read once per session from the XML. (Claude code Opus 5.5) -->
	classes = saspilot._state.get("worldWonderClasses")
	if classes is None:
		classes = [iClass for iClass in range(gc.getNumBuildingClassInfos()) if gc.getBuildingClassInfo(iClass).getMaxGlobalInstances() > -1]
		saspilot._state["worldWonderClasses"] = classes
	return classes


def _between(old, new):
	# <!-- custom: Only what differs, so a reply with nothing new carries no 'news'; a pair is [before, now]. (Claude code Opus 5.5) -->
	news = {}
	for szKey in ("turn", "goldenAge", "greatPeople", "units"):
		if old[szKey] != new[szKey]:
			news[szKey] = [old[szKey], new[szKey]]
	# <!-- custom: An eliminated player has no rank, which read "score rank 3->None"; it is reported as eliminated instead. (Claude code Opus 5.5) -->
	if new["rank"] is None and old["rank"] is not None:
		news["eliminated"] = True
	elif old["rank"] != new["rank"]:
		news["rank"] = [old["rank"], new["rank"]]
		news["ranked"] = new["ranked"]
	# <!-- custom: The messages new since the previous snapshot, at most MESSAGES_SHOWN of them, the newest last, with how many more came. (Claude code Opus 5.5) -->
	# <!-- custom: Counted by occurrence, so the same text twice on one plot and turn counts as two however it arrives: matched by key alone, one copy then a second reported nothing, while both at once reported both (Codex reproduced it). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	seen = {}
	for message in old["messages"]:
		seen[message] = seen.get(message, 0) + 1
	received = []
	for message in new["messages"]:
		if seen.get(message, 0) > 0:
			seen[message] = seen[message] - 1
		else:
			received.append({"text": message[1], "type": message[4][len("MESSAGE_TYPE_"):]})
	if received:
		news["messages"] = received[-MESSAGES_SHOWN:]
		if len(received) > MESSAGES_SHOWN:
			news["messagesNotShown"] = len(received) - MESSAGES_SHOWN
			# <!-- custom: The turn they were read from, so 'messages since=N' lists them all: plain 'messages' reads two turns back only, which after a gap of several turns left some out (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			news["messagesSince"] = new["messagesSince"]
	# <!-- custom: The game's end, with its winner and victory, as the victory screen shows every player: the Asoka save ended at turn 324 with no news, and 'autoplay' then waited without a word (2026-11-28). (Claude code Opus 5.5) -->
	if old["gameState"] != new["gameState"]:
		news["gameState"] = [saspilot._enumName(GameStateTypes, old["gameState"]), saspilot._enumName(GameStateTypes, new["gameState"])]
	# <!-- custom: The winner on its own, as One More Turn moves the game from over to extended with the same winner, which the first version announced again (Codex reproduced it). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if new["winner"] >= 0 and (new["winner"], new["victory"]) != (old["winner"], old["victory"]):
		news["winner"] = gc.getTeam(new["winner"]).getName()
		news["victory"] = saspilot._typeOrNone(gc.getVictoryInfo, new["victory"])
	for (szKey, szOut, getter) in (("religions", "religionsFounded", gc.getReligionInfo), ("corporations", "corporationsFounded", gc.getCorporationInfo)):
		founded = [saspilot._typeOrNone(getter, iType) for iType in new[szKey] if iType not in old[szKey]]
		if founded:
			news[szOut] = founded
	# <!-- custom: A wonder by its default building, BUILDING_PYRAMID, as players and the other commands name it, rather than its class. (Claude code Opus 5.5) -->
	wonders = [gc.getBuildingInfo(gc.getBuildingClassInfo(iClass).getDefaultBuildingIndex()).getType() for iClass in new["wonders"] if iClass not in old["wonders"]]
	if wonders:
		news["worldWondersBuilt"] = wonders
	if old["era"] != new["era"]:
		news["era"] = saspilot._typeOrNone(gc.getEraInfo, new["era"])
	learned = [saspilot._typeOrNone(gc.getTechInfo, iTech) for iTech in new["techs"] if iTech not in old["techs"]]
	if learned:
		news["techsLearned"] = learned
	if old["research"] != new["research"]:
		news["research"] = [saspilot._typeOrNone(gc.getTechInfo, old["research"]), saspilot._typeOrNone(gc.getTechInfo, new["research"])]
	# <!-- custom: Cities by ID, so a renamed city is not taken for a new one; a city captured or founded shows as gained, one lost or razed as lost. (Claude code Opus 5.5) -->
	gained = [new["cities"][iCity][0] for iCity in new["cities"] if not old["cities"].has_key(iCity)]
	lost = [old["cities"][iCity][0] for iCity in old["cities"] if not new["cities"].has_key(iCity)]
	grown = []
	disorder = []
	calm = []
	built = []
	starving = []
	fed = []
	player = gc.getPlayer(new["key"][2])
	for iCity in new["cities"]:
		if not old["cities"].has_key(iCity):
			continue
		(szName, iPop, bDisorder, iProdBuilding, bStarving) = new["cities"][iCity]
		(szOldName, iOldPop, bOldDisorder, iOldProdBuilding, bOldStarving) = old["cities"][iCity]
		if bStarving and not bOldStarving:
			starving.append(szName)
		elif bOldStarving and not bStarving:
			fed.append(szName)
		if iPop != iOldPop:
			grown.append({"city": szName, "pop": [iOldPop, iPop]})
		# <!-- custom: The building a city was producing, now in it: finished, bought or hurried; switching to something else leaves it out. (Claude code Opus 5.5) -->
		if iOldProdBuilding >= 0 and player.getCity(iCity).getNumRealBuilding(iOldProdBuilding) > 0:
			built.append({"city": szName, "building": gc.getBuildingInfo(iOldProdBuilding).getType()})
		if bDisorder and not bOldDisorder:
			disorder.append(szName)
		elif bOldDisorder and not bDisorder:
			calm.append(szName)
	for (szKey, value) in (("citiesGained", gained), ("citiesLost", lost), ("population", grown), ("built", built), ("disorder", disorder), ("disorderEnded", calm), ("starving", starving), ("starvingEnded", fed)):
		if value:
			news[szKey] = value
	# <!-- custom: Anarchy, the treasury running short (gold plus its rate below zero, which the window shows in red and which leads to a strike) and a strike, each as [before, now]. (Claude code Opus 5.5) -->
	for szKey in ("anarchy", "treasuryShort", "strike"):
		if old[szKey] != new[szKey]:
			news[szKey] = [old[szKey], new[szKey]]
	if old["stateReligion"] != new["stateReligion"]:
		news["stateReligion"] = [saspilot._typeOrNone(gc.getReligionInfo, old["stateReligion"]), saspilot._typeOrNone(gc.getReligionInfo, new["stateReligion"])]
	adopted = [saspilot._typeOrNone(gc.getCivicInfo, new["civics"][iOption]) for iOption in range(len(new["civics"])) if new["civics"][iOption] != old["civics"][iOption]]
	if adopted:
		news["civicsAdopted"] = adopted
	gainedBonuses = [saspilot._typeOrNone(gc.getBonusInfo, iBonus) for iBonus in new["bonuses"] if iBonus not in old["bonuses"]]
	lostBonuses = [saspilot._typeOrNone(gc.getBonusInfo, iBonus) for iBonus in old["bonuses"] if iBonus not in new["bonuses"]]
	if gainedBonuses:
		news["resourcesGained"] = gainedBonuses
	if lostBonuses:
		news["resourcesLost"] = lostBonuses
	becameVassal = [new["masters"][iTeam] for iTeam in new["masters"] if not old["masters"].has_key(iTeam)]
	vassalEnded = [old["masters"][iTeam] for iTeam in old["masters"] if not new["masters"].has_key(iTeam)]
	if becameVassal:
		news["vassalOf"] = becameVassal
	if vassalEnded:
		news["vassalEnded"] = vassalEnded
	# <!-- custom: A war ends by peace or by the other team's elimination, as a dead team leaves the list; "peace with", the client's first wording, was wrong for the second (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	declared = [new["wars"][iTeam] for iTeam in new["wars"] if not old["wars"].has_key(iTeam)]
	ended = [old["wars"][iTeam] for iTeam in old["wars"] if not new["wars"].has_key(iTeam)]
	if declared:
		news["warsStarted"] = declared
	if ended:
		news["warsEnded"] = ended
	return news

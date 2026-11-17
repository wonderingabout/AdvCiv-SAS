# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Run inside the game with 'SASPilotClient.py py @<this file>': lists each ever-alive player's fields and each of its units, unit IDs included, so a transplant can be compared with its source save. (Claude code Fable 5.2) -->
# <!-- custom: CvPythonExtensions for CyGlobalContext, so gc is defined here rather than taken from the py namespace, which Ruff cannot see. (Claude code Opus 5.5) -->
from CvPythonExtensions import *

gc = CyGlobalContext()

rows = []
for i in range(gc.getMAX_PLAYERS()):
	p = gc.getPlayer(i)
	if not p.isEverAlive():
		continue
	rows.append(["P", i, p.getPersonalityType(), p.getCurrentEra(), p.getGold(), p.calculateGoldRate(), p.getTotalPopulation(), p.getTotalLand(), p.getAssets(), p.getPower(), p.getNumUnits(), int(p.isTurnActive()), int(p.isFoundedFirstCity()), p.getStateReligion(), p.calculateInflationRate()])
	(u, it) = p.firstUnit(False)
	while u:
		rows.append(["U", i, u.getID(), gc.getUnitInfo(u.getUnitType()).getType(), u.getX(), u.getY(), u.getGameTurnCreated(), u.getMoves(), u.getGroupID(), u.getFortifyTurns(), int(u.getUnitAIType())])
		(u, it) = p.nextUnit(it, False)
result = rows

//
// Python wrapper class for CvPlot
//
//
#include "CvGameCoreDLL.h"
#include "CyPlot.h"
#include "CyArea.h"
#include "CvPlot.h"
#include "CvArea.h" // advc: for CvArea::getID
#include "CvUnit.h" // advc: for city/fort-related functions moved to CvUnit
#include "CvMap.h" // advc.enum
#include "CvInfo_Terrain.h" // <!-- custom: WorldBuilder history dereferences terrain, feature, bonus, improvement and route info to retain XML type names; forward declarations failed VC2003 with C2027/C2228. (GPT-6.1-Sol) -->
#include "CvGame.h" // <!-- custom: Direct Python/WorldBuilder owner changes now exclude pre-game setup from SASGameRecord transactions, which requires the full CvGame definition for isFinalInitialized. (GPT-5.6-Sol) -->
#include "SASGameRecordLog.h" // <!-- custom: Attribute exact level-3 ownership mutations initiated through the Python/WorldBuilder plot wrapper. (ChatGPT-5.6-Sol + GPT-5.6-Sol) -->

CyPlot::CyPlot(CvPlot* pPlot) : m_pPlot(pPlot) {}
// advc.003y: (see CyCity.cpp)
CyPlot::CyPlot(CvPlot const& kPlot) : m_pPlot(const_cast<CvPlot*>(&kPlot)) {}

CyPlot::CyPlot() : m_pPlot(NULL) {}

// <!-- custom: Keep WorldBuilder mutation detection at the Python wrapper boundary that the inherited editor actually calls.
// Persistence is independent of SGR; detailed plot-state snapshots are taken only when the level-2 action trace is enabled. (ChatGPT-5.6-Sol) -->
static bool isSASWorldBuilderEditContext()
{
	return GC.getGame().isSASWorldBuilderScreenVisible() && !GC.getGame().isInAdvancedStart();
}

static bool isSASWorldBuilderEditLoggingEnabled()
{
	return gGameRecordLogLevel >= 2 && isSASGameRecordActionTraceEnabled();
}

static void recordSASWorldBuilderPlotChange(CvPlot& kPlot, SASGameRecordPlotState const& kOldState, bool bLog)
{
	TerrainTypes const eTerrain = kPlot.getTerrainType();
	FeatureTypes const eFeature = kPlot.getFeatureType();
	BonusTypes const eBonus = kPlot.getBonusType();
	ImprovementTypes const eImprovement = kPlot.getImprovementType();
	RouteTypes const eRoute = kPlot.getRouteType();
	if (kOldState.eTerrain != eTerrain)
	{
		TerrainTypes const eNamed = (eTerrain != NO_TERRAIN ? eTerrain : kOldState.eTerrain);
		char const* szTarget = (eNamed >= 0 && eNamed < GC.getNumTerrainInfos() ? GC.getInfo(eNamed).getType() : "-");
		GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_TERRAIN", kPlot.getX(), kPlot.getY(), kPlot.getOwner(), -1, "TERRAIN", szTarget, kOldState.eTerrain, eTerrain);
	}
	if (kOldState.eFeature != eFeature)
	{
		FeatureTypes const eNamed = (eFeature != NO_FEATURE ? eFeature : kOldState.eFeature);
		char const* szTarget = (eNamed >= 0 && eNamed < GC.getNumFeatureInfos() ? GC.getInfo(eNamed).getType() : "-");
		GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_FEATURE", kPlot.getX(), kPlot.getY(), kPlot.getOwner(), -1, "FEATURE", szTarget, kOldState.eFeature, eFeature);
	}
	if (kOldState.eBonus != eBonus)
	{
		BonusTypes const eNamed = (eBonus != NO_BONUS ? eBonus : kOldState.eBonus);
		char const* szTarget = (eNamed >= 0 && eNamed < GC.getNumBonusInfos() ? GC.getInfo(eNamed).getType() : "-");
		GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_BONUS", kPlot.getX(), kPlot.getY(), kPlot.getOwner(), -1, "BONUS", szTarget, kOldState.eBonus, eBonus);
	}
	if (kOldState.eImprovement != eImprovement)
	{
		ImprovementTypes const eNamed = (eImprovement != NO_IMPROVEMENT ? eImprovement : kOldState.eImprovement);
		char const* szTarget = (eNamed >= 0 && eNamed < GC.getNumImprovementInfos() ? GC.getInfo(eNamed).getType() : "-");
		GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_IMPROVEMENT", kPlot.getX(), kPlot.getY(), kPlot.getOwner(), -1, "IMPROVEMENT", szTarget, kOldState.eImprovement, eImprovement);
	}
	if (kOldState.eRoute != eRoute)
	{
		RouteTypes const eNamed = (eRoute != NO_ROUTE ? eRoute : kOldState.eRoute);
		char const* szTarget = (eNamed >= 0 && eNamed < GC.getNumRouteInfos() ? GC.getInfo(eNamed).getType() : "-");
		GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_ROUTE", kPlot.getX(), kPlot.getY(), kPlot.getOwner(), -1, "ROUTE", szTarget, kOldState.eRoute, eRoute);
	}
	bool bChanged = (kOldState.eTerrain != eTerrain || kOldState.eFeature != eFeature || kOldState.eBonus != eBonus || kOldState.eImprovement != eImprovement || kOldState.eRoute != eRoute);
	for (int i = 0; i < NUM_YIELD_TYPES; i++)
	{
		int const iNewYield = GC.getMap().getPlotExtraYield(kPlot, (YieldTypes)i);
		if (kOldState.aiExtraYield[i] == iNewYield)
			continue;
		bChanged = true;
		char const* szYield = GC.getInfo((YieldTypes)i).getType();
		GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_EXTRA_YIELD", kPlot.getX(), kPlot.getY(), kPlot.getOwner(), i, "YIELD", szYield, kOldState.aiExtraYield[i], iNewYield);
	}
	if (bChanged && bLog)
		recordSASGameRecordPlotChange(kPlot, kOldState, "worldBuilder", "WORLDBUILDER", true);
}

void CyPlot::erase()
{
	if (m_pPlot)
	{
		bool const bWorldBuilder = isSASWorldBuilderEditContext();
		bool const bLog = bWorldBuilder && isSASWorldBuilderEditLoggingEnabled();
		SASGameRecordPlotState kOldState;
		if (bWorldBuilder) kOldState = SASGameRecordPlotState(*m_pPlot);
		int const iOldUnits = bWorldBuilder ? m_pPlot->getNumUnits() : 0;
		bool const bOldCity = bWorldBuilder && m_pPlot->isCity();
		m_pPlot->erase();
		if (bWorldBuilder)
		{
			recordSASWorldBuilderPlotChange(*m_pPlot, kOldState, bLog);
			if (iOldUnits > 0) GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_UNIT, "ERASE_PLOT_UNITS", m_pPlot->getX(), m_pPlot->getY(), NO_PLAYER, -1, "UNIT_COUNT", "-", iOldUnits, 0);
			if (bOldCity) GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_CITY, "ERASE_PLOT_CITY", m_pPlot->getX(), m_pPlot->getY(), NO_PLAYER, -1, "CITY", "-", 1, 0);
		}
	}
}

NiPoint3 CyPlot::getPoint()
{
	return m_pPlot ? m_pPlot->getPoint() : NiPoint3(0,0,0);
}

int CyPlot::getTeam()
{
	return m_pPlot ? m_pPlot->getTeam() : -1;
}

void CyPlot::nukeExplosion(int iRange, CyUnit* pNukeUnit)
{
	if (m_pPlot)
		m_pPlot->nukeExplosion(iRange, pNukeUnit->getUnit());
}

bool CyPlot::isConnectedTo(CyCity* pCity)
{
	return (m_pPlot && pCity && pCity->getCity()) ?
			m_pPlot->isConnectedTo(*pCity->getCity()) : false;
}

bool CyPlot::isConnectedToCapital(int /*PlayerTypes*/ ePlayer)
{
	return m_pPlot ? m_pPlot->isConnectedToCapital((PlayerTypes) ePlayer): false;
}

int CyPlot::getPlotGroupConnectedBonus(int /*PlayerTypes*/ ePlayer, int /*BonusTypes*/ eBonus)
{
	return m_pPlot ? m_pPlot->getPlotGroupConnectedBonus((PlayerTypes) ePlayer, (BonusTypes) eBonus) : -1;
}

bool CyPlot::isPlotGroupConnectedBonus(int /*PlayerTypes*/ ePlayer, int /*BonusTypes*/ eBonus)
{
	return m_pPlot ? m_pPlot->isPlotGroupConnectedBonus((PlayerTypes) ePlayer, (BonusTypes) eBonus) : false;
}

bool CyPlot::isAdjacentPlotGroupConnectedBonus(int /*PlayerTypes*/ ePlayer, int /*BonusTypes*/ eBonus)
{
	return m_pPlot ? m_pPlot->isAdjacentPlotGroupConnectedBonus((PlayerTypes) ePlayer, (BonusTypes) eBonus) : false;
}

void CyPlot::updateVisibility()
{
	if (m_pPlot)
	{
		m_pPlot->updateVisibility();
	}
}

bool CyPlot::isAdjacentToArea(CyArea* pArea)
{
	return m_pPlot ? m_pPlot->isAdjacentToArea(pArea->getArea()) : false;
}

bool CyPlot::shareAdjacentArea(CyPlot* pPlot)
{
	return m_pPlot ? m_pPlot->shareAdjacentArea(pPlot->getPlot()) : false;
}

bool CyPlot::isAdjacentToLand()
{
	return m_pPlot ? m_pPlot->isAdjacentToLand() : false;
}

bool CyPlot::isCoastalLand()
{
	return m_pPlot ? m_pPlot->isCoastalLand() : false;
}

bool CyPlot::isWithinTeamCityRadius(int /*TeamTypes*/ eTeam, int /*PlayerTypes*/ eIgnorePlayer)
{
	return m_pPlot ? m_pPlot->isWithinTeamCityRadius((TeamTypes) eTeam, (PlayerTypes) eIgnorePlayer) : false;
}
bool CyPlot::isLake()
{
	return m_pPlot ? m_pPlot->isLake() : false;
}

bool CyPlot::isFreshWater()
{
	return m_pPlot ? m_pPlot->isFreshWater() : false;
}

bool CyPlot::isPotentialIrrigation()
{
	return m_pPlot ? m_pPlot->isPotentialIrrigation() : false;
}

bool CyPlot::canHavePotentialIrrigation()
{
	return m_pPlot ? m_pPlot->canHavePotentialIrrigation() : false;
}

bool CyPlot::isIrrigationAvailable(bool bIgnoreSelf)
{
	return m_pPlot ? m_pPlot->isIrrigationAvailable(bIgnoreSelf) : false;
}

bool CyPlot::isRiverSide()
{
	return m_pPlot ? m_pPlot->isRiverSide() : false;
}

bool CyPlot::isRiver()
{
	return m_pPlot ? m_pPlot->isRiver() : false;
}

bool CyPlot::isRiverConnection(int /*DirectionTypes*/ eDirection)
{
	return m_pPlot ? m_pPlot->isRiverConnection((DirectionTypes) eDirection) : false;
}

int CyPlot::getNearestLandArea()
{
	if (m_pPlot == NULL)
		return -1;
	// <advc> (The DLL function no longer returns the area id)
	CvArea* pArea = m_pPlot->getNearestLandArea();
	if (pArea == NULL)
		return FFreeList::INVALID_INDEX;
	return pArea->getID(); // </advc>
}

CyPlot* CyPlot::getNearestLandPlot()
{
	return m_pPlot ? new CyPlot(m_pPlot->getNearestLandPlot()) : NULL;
}

int CyPlot::seeFromLevel(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->seeFromLevel((TeamTypes)eTeam) : -1;
}

int CyPlot::seeThroughLevel()
{
	return m_pPlot ? m_pPlot->seeThroughLevel() : -1;
}

bool CyPlot::canHaveBonus(int /*BonusTypes*/ eBonus, bool bIgnoreLatitude)
{
	return m_pPlot ? m_pPlot->canHaveBonus((BonusTypes)eBonus, bIgnoreLatitude) : false;
}

bool CyPlot::canHaveImprovement(int /* ImprovementTypes */ eImprovement, int /*TeamTypes*/ eTeam, bool bPotential)
{
	return m_pPlot ? m_pPlot->canHaveImprovement(((ImprovementTypes)eImprovement), ((TeamTypes)eTeam), bPotential) : false;
}

bool CyPlot::canBuild(int /*BuildTypes*/ eBuild, int /*PlayerTypes*/ ePlayer, bool bTestVisible)
{
	return m_pPlot ? m_pPlot->canBuild((BuildTypes) eBuild, (PlayerTypes) ePlayer, bTestVisible) : false;
}
// advc.251: param ePlayer added to these two functions
int CyPlot::getBuildTime(int /* BuildTypes */ eBuild, int /* PlayerTypes */ ePlayer)
{
	return m_pPlot ? m_pPlot->getBuildTime((BuildTypes)eBuild, (PlayerTypes)ePlayer) : -1;
}
int CyPlot::getBuildTurnsLeft(int /*BuildTypes*/ eBuild, int /* PlayerTypes */ ePlayer, int iNowExtra, int iThenExtra)
{
	return m_pPlot ? m_pPlot->getBuildTurnsLeft((BuildTypes)eBuild, (PlayerTypes)ePlayer, iNowExtra, iThenExtra) : -1;
}

int CyPlot::getFeatureProduction(int /*BuildTypes*/ eBuild, int /*TeamTypes*/ eTeam, CyCity* ppCity)
{
	CvCity* tempCity = ppCity->getCity();
	return m_pPlot ? m_pPlot->getFeatureProduction((BuildTypes) eBuild, (TeamTypes) eTeam, &tempCity) : -1;
}

CyUnit* CyPlot::getBestDefender(int /*PlayerTypes*/ eOwner, int /*PlayerTypes*/ eAttackingPlayer, CyUnit* pAttacker, bool bTestAtWar, bool bTestPotentialEnemy, bool bTestCanMove)
{
	return m_pPlot ? new CyUnit(m_pPlot->getBestDefender((PlayerTypes) eOwner, (PlayerTypes) eAttackingPlayer, pAttacker->getUnit(), bTestAtWar, bTestPotentialEnemy, bTestCanMove)) : NULL;
}

CyUnit* CyPlot::getSelectedUnit()
{
	return m_pPlot ? new CyUnit(m_pPlot->getSelectedUnit()) : NULL;
}

int CyPlot::getUnitPower(int /* PlayerTypes */ eOwner)
{
	return m_pPlot ? m_pPlot->getUnitPower((PlayerTypes)eOwner) : -1;
}

int CyPlot::movementCost(CyUnit* pUnit, CyPlot* pFromPlot)
{
	return m_pPlot &&
		pUnit && pUnit->getUnit() && pFromPlot && pFromPlot->getPlot() ? // advc
		m_pPlot->movementCost(*pUnit->getUnit(), *pFromPlot->getPlot()) : -1;
}

int CyPlot::defenseModifier(int iDefendTeam, bool bIgnoreBuilding, bool bHelp)
{
	return m_pPlot ? m_pPlot->defenseModifier((TeamTypes)iDefendTeam, bIgnoreBuilding,
		NO_TEAM, // advc.012: Python callers (none currently) always have feature defense included this way
		bHelp) : -1;
}

int CyPlot::getExtraMovePathCost()
{
	//return m_pPlot ? m_pPlot->getExtraMovePathCost() : -1;
	// <advc.enum>
	if (m_pPlot == NULL)
		return 0;
	return GC.getMap().getPlotExtraCost(*m_pPlot); // </advc.enum>
}

void CyPlot::changeExtraMovePathCost(int iChange)
{
	if (m_pPlot)
	{
		//m_pPlot->changeExtraMovePathCost(iChange);
		GC.getMap().changePlotExtraCost(*m_pPlot, iChange); // advc.enum
	}
}

bool CyPlot::isAdjacentOwned()
{
	return m_pPlot ? m_pPlot->isAdjacentOwned() : false;
}

bool CyPlot::isAdjacentPlayer(int /*PlayerTypes*/ ePlayer, bool bLandOnly)
{
	return m_pPlot ? m_pPlot->isAdjacentPlayer((PlayerTypes)ePlayer, bLandOnly) : false;
}

bool CyPlot::isAdjacentTeam(int /*TeamTypes*/ ePlayer, bool bLandOnly)
{
	return m_pPlot ? m_pPlot->isAdjacentTeam((TeamTypes)ePlayer, bLandOnly) : false;
}

bool CyPlot::isWithinCultureRange(int /*PlayerTypes*/ ePlayer)
{
	return m_pPlot ? m_pPlot->isWithinCultureRange((PlayerTypes)ePlayer) : false;
}

int CyPlot::getNumCultureRangeCities(int /*PlayerTypes*/ ePlayer)
{
	return m_pPlot ? m_pPlot->getNumCultureRangeCities((PlayerTypes)ePlayer) : -1;
}

int /*PlayerTypes*/ CyPlot::calculateCulturalOwner()
{
	return m_pPlot ? m_pPlot->calculateCulturalOwner() : -1;
}

bool CyPlot::isOwned()
{
	return m_pPlot ? m_pPlot->isOwned() : false;
}

bool CyPlot::isBarbarian()
{
	return m_pPlot ? m_pPlot->isBarbarian() : false;
}

bool CyPlot::isRevealedBarbarian()
{
	return m_pPlot ? m_pPlot->isRevealedBarbarian() : false;
}

bool CyPlot::isVisible(int /*TeamTypes*/ eTeam, bool bDebug)
{
	return m_pPlot ? m_pPlot->isVisible((TeamTypes)eTeam, bDebug) : false;
}

bool CyPlot::isActiveVisible(bool bDebug)
{
	return m_pPlot ? m_pPlot->isActiveVisible(bDebug) : false;
}

bool CyPlot::isVisibleToWatchingHuman()
{
	return m_pPlot ? m_pPlot->isVisibleToWatchingHuman() : false;
}

bool CyPlot::isAdjacentVisible(int /*TeamTypes*/ eTeam, bool bDebug)
{
	return m_pPlot ? m_pPlot->isAdjacentVisible((TeamTypes) eTeam, bDebug) : false;
}

bool CyPlot::isAdjacentNonvisible(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->isAdjacentNonvisible((TeamTypes) eTeam) : false;
}

bool CyPlot::isAdjacentRevealed(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->isAdjacentRevealed((TeamTypes) eTeam) : false;
}

bool CyPlot::isAdjacentNonrevealed(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->isAdjacentNonrevealed((TeamTypes) eTeam) : false;
}

void CyPlot::removeGoody()
{
	if (m_pPlot)
	{
		m_pPlot->removeGoody();
	}
}

bool CyPlot::isGoody()
{
	return m_pPlot ? m_pPlot->isGoody() : false;
}

bool CyPlot::isRevealedGoody(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->isRevealedGoody((TeamTypes) eTeam) : false;
}

bool CyPlot::isCity()
{
	return m_pPlot ? m_pPlot->isCity() : false;
}

bool CyPlot::isEnemyCity(CyUnit* pUnit)
{
	return m_pPlot /* advc: */ && pUnit && pUnit->getUnit() ?
			pUnit->getUnit()->isEnemyCity(*m_pPlot) : false;
}

bool CyPlot::isOccupation()
{
	return m_pPlot ? m_pPlot->isOccupation() : false;
}

bool CyPlot::isBeingWorked()
{
	return m_pPlot ? m_pPlot->isBeingWorked() : false;
}

bool CyPlot::isUnit()
{
	return m_pPlot ? m_pPlot->isUnit() : false;
}

bool CyPlot::isInvestigate(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->isInvestigate((TeamTypes) eTeam) : false;
}

bool CyPlot::isVisibleEnemyDefender(CyUnit* pUnit)
{
	return m_pPlot ? m_pPlot->isVisibleEnemyDefender(pUnit->getUnit()) : false;
}

int CyPlot::getNumDefenders(int /*PlayerTypes*/ ePlayer)
{
	return m_pPlot ? m_pPlot->getNumDefenders((PlayerTypes) ePlayer) : -1;
}

int CyPlot::getNumVisibleEnemyDefenders(CyUnit* pUnit)
{
	return m_pPlot ? m_pPlot->getNumVisibleEnemyDefenders(pUnit->getUnit()) : -1;
}

/*	advc: This is now handled by CvUnitAI::AI_countEnemyDefenders - b/c it's AI code,
	which shouldn't be exposed to Python. */
/*int CyPlot::getNumVisiblePotentialEnemyDefenders(CyUnit* pUnit)
{
	return m_pPlot ? m_pPlot->getNumVisiblePotentialEnemyDefenders(pUnit->getUnit()) : -1;
}*/

bool CyPlot::isVisibleEnemyUnit(int /*PlayerTypes*/ ePlayer)
{
	return m_pPlot ? m_pPlot->isVisibleEnemyUnit((PlayerTypes) ePlayer) : false;
}

bool CyPlot::isVisibleOtherUnit(int /*PlayerTypes*/ ePlayer)
{
	return m_pPlot ? m_pPlot->isVisibleOtherUnit((PlayerTypes) ePlayer) : false;
}

bool CyPlot::isFighting()
{
	return m_pPlot ? m_pPlot->isFighting() : false;
}

bool CyPlot::canHaveFeature(int /*FeatureTypes*/ eFeature)
{
	return m_pPlot ? m_pPlot->canHaveFeature((FeatureTypes)eFeature) : false;
}

bool CyPlot::isRoute()
{
	return m_pPlot ? m_pPlot->isRoute() : false;
}

bool CyPlot::isNetworkTerrain(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->isNetworkTerrain((TeamTypes) eTeam) : false;
}

bool CyPlot::isBonusNetwork(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->isBonusNetwork((TeamTypes) eTeam) : false;
}
bool CyPlot::isTradeNetworkImpassable(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->isTradeNetworkImpassable((TeamTypes) eTeam) : false;
}

bool CyPlot::isTradeNetwork(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->isTradeNetwork((TeamTypes)eTeam) : false;
}

bool CyPlot::isTradeNetworkConnected(CyPlot* pPlot, int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->isTradeNetworkConnected(*pPlot->getPlot(), (TeamTypes)eTeam) : false;
}

bool CyPlot::isValidDomainForLocation(CyUnit* pUnit) const
{
	return (m_pPlot && pUnit && pUnit->getUnit()) ?
			pUnit->getUnit()->isValidDomain(*m_pPlot) : false;
}

bool CyPlot::isValidDomainForAction(CyUnit* pUnit) const
{
	return (m_pPlot && pUnit && pUnit->getUnit()) ?
			pUnit->getUnit()->isValidDomain(m_pPlot->isWater()) : false;
}

bool CyPlot::isImpassable()
{
	return m_pPlot ? m_pPlot->isImpassable() : false;
}

int CyPlot::getX()
{
	return m_pPlot ? m_pPlot->getX() : -1;
}

int CyPlot::getY()
{
	return m_pPlot ? m_pPlot->getY() : -1;
}

bool CyPlot::at(int iX, int iY)
{
	return m_pPlot ? m_pPlot->at(iX, iY) : false;
}
// <advc.tsl>
void CyPlot::setLatitude(int iLatitude) {
	if(m_pPlot != NULL)
		m_pPlot->setLatitude(iLatitude);
} // </advc.tsl>

int CyPlot::getLatitude()
{
	return m_pPlot ? m_pPlot->getLatitude() : -1;
}

CyArea* CyPlot::area()
{
	return m_pPlot ? new CyArea(m_pPlot->area()) : NULL;
}

CyArea* CyPlot::waterArea()
{
	return m_pPlot ? new CyArea(m_pPlot->waterArea()) : NULL;
}

int CyPlot::getArea()
{
	return m_pPlot ? m_pPlot->getArea().getID() : -1;
}

int CyPlot::getUpgradeProgress()
{
	return m_pPlot ? m_pPlot->getUpgradeProgress() : -1;
}

int CyPlot::getUpgradeTimeLeft(int /*ImprovementTypes*/ eImprovement, int /*PlayerTypes*/ ePlayer)
{
	return m_pPlot ? m_pPlot->getUpgradeTimeLeft((ImprovementTypes) eImprovement, (PlayerTypes) ePlayer) : -1;
}

void CyPlot::setUpgradeProgress(int iNewValue)
{
	if (m_pPlot)
		m_pPlot->setUpgradeProgress(iNewValue);
}

void CyPlot::changeUpgradeProgress(int iChange)
{
	if (m_pPlot)
		m_pPlot->changeUpgradeProgress(iChange);
}

int CyPlot::getForceUnownedTimer()
{
	return m_pPlot ? m_pPlot->getForceUnownedTimer() : -1;
}

bool CyPlot::isForceUnowned()
{
	return m_pPlot ? m_pPlot->isForceUnowned() : false;
}

void CyPlot::setForceUnownedTimer(int iNewValue)
{
	if (m_pPlot)
		m_pPlot->setForceUnownedTimer(iNewValue);
}

void CyPlot::changeForceUnownedTimer(int iChange)
{
	if (m_pPlot)
		m_pPlot->changeForceUnownedTimer(iChange);
}

int CyPlot::getCityRadiusCount()
{
	return m_pPlot ? m_pPlot->getCityRadiusCount() : -1;
}

bool CyPlot::isCityRadius()
{
	//return m_pPlot ? m_pPlot->isCityRadius() : -1;
	return m_pPlot ? m_pPlot->isCityRadius() : false; // K-Mod. (-1? really?)
}

bool CyPlot::isStartingPlot()
{
	return m_pPlot ? m_pPlot->isStartingPlot() : false;
}

void CyPlot::setStartingPlot(bool bNewValue)
{
	if (m_pPlot)
	{
		bool const bWorldBuilder = isSASWorldBuilderEditContext();
		bool const bOldValue = (bWorldBuilder ? m_pPlot->isStartingPlot() : false);
		m_pPlot->setStartingPlot(bNewValue);
		if (bWorldBuilder && bOldValue != m_pPlot->isStartingPlot())
		{
			GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_STARTING_PLOT", m_pPlot->getX(), m_pPlot->getY(), NO_PLAYER, -1, "BOOL", "STARTING_PLOT", bOldValue ? 1 : 0, m_pPlot->isStartingPlot() ? 1 : 0);
		}
	}
}

bool CyPlot::isNOfRiver()
{
	return m_pPlot ? m_pPlot->isNOfRiver() : false;
}

void CyPlot::setNOfRiver(bool bNewValue, CardinalDirectionTypes eRiverDir)
{
	if (m_pPlot)
	{
		bool const bWorldBuilder = isSASWorldBuilderEditContext();
		bool const bOldValue = (bWorldBuilder ? m_pPlot->isNOfRiver() : false);
		CardinalDirectionTypes const eOldDirection = (bWorldBuilder ? m_pPlot->getRiverWEDirection() : CardinalDirectionTypes());
		m_pPlot->setNOfRiver(bNewValue, eRiverDir);
		if (bWorldBuilder && bOldValue != m_pPlot->isNOfRiver())
		{
			GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_RIVER_NORTH", m_pPlot->getX(), m_pPlot->getY(), NO_PLAYER, -1, "RIVER", "NORTH_EDGE", bOldValue ? 1 : 0, m_pPlot->isNOfRiver() ? 1 : 0);
		}
		// <!-- custom: WorldBuilder can rotate an existing river edge without changing its presence Boolean; preserve that distinct edit too. (ChatGPT-5.6-Sol) -->
		if (bWorldBuilder && eOldDirection != m_pPlot->getRiverWEDirection())
		{
			GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_RIVER_NORTH_DIRECTION", m_pPlot->getX(), m_pPlot->getY(), NO_PLAYER, -1, "CARDINAL_DIRECTION", "NORTH_EDGE", eOldDirection, m_pPlot->getRiverWEDirection());
		}
	}
}

bool CyPlot::isWOfRiver()
{
	return m_pPlot ? m_pPlot->isWOfRiver() : false;
}

void CyPlot::setWOfRiver(bool bNewValue, CardinalDirectionTypes eRiverDir)
{
	if (m_pPlot)
	{
		bool const bWorldBuilder = isSASWorldBuilderEditContext();
		bool const bOldValue = (bWorldBuilder ? m_pPlot->isWOfRiver() : false);
		CardinalDirectionTypes const eOldDirection = (bWorldBuilder ? m_pPlot->getRiverNSDirection() : CardinalDirectionTypes());
		m_pPlot->setWOfRiver(bNewValue, eRiverDir);
		if (bWorldBuilder && bOldValue != m_pPlot->isWOfRiver())
		{
			GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_RIVER_WEST", m_pPlot->getX(), m_pPlot->getY(), NO_PLAYER, -1, "RIVER", "WEST_EDGE", bOldValue ? 1 : 0, m_pPlot->isWOfRiver() ? 1 : 0);
		}
		if (bWorldBuilder && eOldDirection != m_pPlot->getRiverNSDirection())
		{
			GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_RIVER_WEST_DIRECTION", m_pPlot->getX(), m_pPlot->getY(), NO_PLAYER, -1, "CARDINAL_DIRECTION", "WEST_EDGE", eOldDirection, m_pPlot->getRiverNSDirection());
		}
	}
}

CardinalDirectionTypes CyPlot::getRiverWEDirection()
{
	return m_pPlot->getRiverWEDirection();
}

CardinalDirectionTypes CyPlot::getRiverNSDirection()
{
	return m_pPlot->getRiverNSDirection();
}

bool CyPlot::isIrrigated()
{
	return m_pPlot ? m_pPlot->isIrrigated() : false;
}

bool CyPlot::isPotentialCityWork()
{
	return m_pPlot ? m_pPlot->isPotentialCityWork() : false;
}

bool CyPlot::isPotentialCityWorkForArea(CyArea* pArea)
{
	return m_pPlot ? m_pPlot->isPotentialCityWorkForArea(pArea->getArea()) : false;
}

bool CyPlot::isFlagDirty()
{
	return m_pPlot ? m_pPlot->isFlagDirty() : false;
}

void CyPlot::setFlagDirty(bool bNewValue)
{
	if (m_pPlot)
	{
		m_pPlot->setFlagDirty(bNewValue);
	}
}

int CyPlot::getOwner()
{
	return m_pPlot ? m_pPlot->getOwner() : -1;
}

void CyPlot::setOwner(int /*PlayerTypes*/ eNewValue)
{
	if (m_pPlot)
	{
		bool const bWorldBuilderEdit = isSASWorldBuilderEditContext();
		PlayerTypes const eOldOwner = (bWorldBuilderEdit ? m_pPlot->getOwner() : PlayerTypes());
		bool const bLogSASOwnerChange = (gGameRecordLogLevel >= 3 && GC.getGame().isFinalInitialized() && m_pPlot->getOwner() != (PlayerTypes)eNewValue);
		bool const bWorldBuilder = (bLogSASOwnerChange && bWorldBuilderEdit);
		// <!-- custom: A direct Python/WorldBuilder plot-owner request can recurse into city acquisition.
		// Keep its external origin as the root tx while nested owner-change mechanisms remain precise. (ChatGPT-5.6-Sol + GPT-5.6-Sol) -->
		SASGameRecordTransactionScope kSASPythonOwnerTransaction(bWorldBuilder ? "WORLDBUILDER_PLOT_OWNER" : "PYTHON_PLOT_OWNER", bLogSASOwnerChange);
		SASGameRecordPlotOwnerChangeCauseScope kSASPythonOwnerCause(bWorldBuilder ? SAS_PLOT_OWNER_CAUSE_WORLDBUILDER : SAS_PLOT_OWNER_CAUSE_PYTHON_EXTERNAL, bLogSASOwnerChange);
		m_pPlot->setOwner((PlayerTypes)eNewValue, true, true);
		if (bWorldBuilderEdit && eOldOwner != m_pPlot->getOwner())
		{
			GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_OWNER", m_pPlot->getX(), m_pPlot->getY(), m_pPlot->getOwner(), -1, "PLAYER", "-", eOldOwner, m_pPlot->getOwner());
		}
	}
}

void CyPlot::setOwnerNoUnitCheck(int /*PlayerTypes*/ eNewValue)
{
	if (m_pPlot)
	{
		bool const bWorldBuilderEdit = isSASWorldBuilderEditContext();
		PlayerTypes const eOldOwner = (bWorldBuilderEdit ? m_pPlot->getOwner() : PlayerTypes());
		bool const bLogSASOwnerChange = (gGameRecordLogLevel >= 3 && GC.getGame().isFinalInitialized() && m_pPlot->getOwner() != (PlayerTypes)eNewValue);
		bool const bWorldBuilder = (bLogSASOwnerChange && bWorldBuilderEdit);
		// <!-- custom: A direct Python/WorldBuilder plot-owner request can recurse into city acquisition.
		// Keep its external origin as the root tx while nested owner-change mechanisms remain precise. (ChatGPT-5.6-Sol + GPT-5.6-Sol) -->
		SASGameRecordTransactionScope kSASPythonOwnerTransaction(bWorldBuilder ? "WORLDBUILDER_PLOT_OWNER" : "PYTHON_PLOT_OWNER", bLogSASOwnerChange);
		SASGameRecordPlotOwnerChangeCauseScope kSASPythonOwnerCause(bWorldBuilder ? SAS_PLOT_OWNER_CAUSE_WORLDBUILDER : SAS_PLOT_OWNER_CAUSE_PYTHON_EXTERNAL, bLogSASOwnerChange);
		m_pPlot->setOwner((PlayerTypes)eNewValue, false, true);
		if (bWorldBuilderEdit && eOldOwner != m_pPlot->getOwner())
		{
			GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_OWNER_NO_UNIT_CHECK", m_pPlot->getX(), m_pPlot->getY(), m_pPlot->getOwner(), -1, "PLAYER", "-", eOldOwner, m_pPlot->getOwner());
		}
	}
}
PlotTypes CyPlot::getPlotType()
{
	return m_pPlot ? m_pPlot->getPlotType() : NO_PLOT;
}

bool CyPlot::isWater()
{
	return m_pPlot ? m_pPlot->isWater() : false;
}

bool CyPlot::isFlatlands()
{
	return m_pPlot ? m_pPlot->isFlatlands() : false;
}

bool CyPlot::isHills()
{
	return m_pPlot ? m_pPlot->isHills() : false;
}

bool CyPlot::isPeak()
{
	return m_pPlot ? m_pPlot->isPeak() : false;
}

void CyPlot::setPlotType(PlotTypes eNewValue, bool bRecalculate, bool bRebuildGraphics)
{
	if (m_pPlot)
	{
		bool const bWorldBuilder = isSASWorldBuilderEditContext();
		PlotTypes const eOldValue = (bWorldBuilder ? m_pPlot->getPlotType() : PlotTypes());
		m_pPlot->setPlotType(eNewValue, bRecalculate, bRebuildGraphics);
		if (bWorldBuilder && eOldValue != m_pPlot->getPlotType())
		{
			GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_PLOT_TYPE", m_pPlot->getX(), m_pPlot->getY(), NO_PLAYER, -1, "PLOT_TYPE", "-", eOldValue, m_pPlot->getPlotType());
		}
	}
}

int /*TerrainTypes*/ CyPlot::getTerrainType()
{
	return m_pPlot ? m_pPlot->getTerrainType() : -1;
}

void CyPlot::setTerrainType(int /*TerrainTypes*/ eNewValue, bool bRecalculate, bool bRebuildGraphics)
{
	if (m_pPlot)
	{
		bool const bWorldBuilder = isSASWorldBuilderEditContext();
		bool const bLog = bWorldBuilder && isSASWorldBuilderEditLoggingEnabled();
		SASGameRecordPlotState kOldState;
		if (bWorldBuilder) kOldState = SASGameRecordPlotState(*m_pPlot);
		m_pPlot->setTerrainType((TerrainTypes)eNewValue, bRecalculate, bRebuildGraphics);
		if (bWorldBuilder) recordSASWorldBuilderPlotChange(*m_pPlot, kOldState, bLog);
	}
}

int /*FeatureTypes*/ CyPlot::getFeatureType()
{
	return m_pPlot ? m_pPlot->getFeatureType() : -1;
}

void CyPlot::setFeatureType(int /*FeatureTypes*/ eNewValue, int iVariety)
{
	if (m_pPlot)
	{
		bool const bWorldBuilder = isSASWorldBuilderEditContext();
		bool const bLog = bWorldBuilder && isSASWorldBuilderEditLoggingEnabled();
		SASGameRecordPlotState kOldState;
		int const iOldVariety = bWorldBuilder ? m_pPlot->getFeatureVariety() : -1;
		if (bWorldBuilder) kOldState = SASGameRecordPlotState(*m_pPlot);
		m_pPlot->setFeatureType((FeatureTypes)eNewValue, iVariety);
		if (bWorldBuilder)
		{
			recordSASWorldBuilderPlotChange(*m_pPlot, kOldState, bLog);
			// <!-- custom: Variety is independent state even when the feature type changes in the same setter call; preserve both applied changes instead of dropping the variety transition. (ChatGPT-5.6-Sol) -->
			if (iOldVariety != m_pPlot->getFeatureVariety())
			{
				GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_MAP, "SET_FEATURE_VARIETY", m_pPlot->getX(), m_pPlot->getY(), NO_PLAYER, -1, "FEATURE_VARIETY", "-", iOldVariety, m_pPlot->getFeatureVariety());
			}
		}
	}
}

void CyPlot::setFeatureDummyVisibility(std::string dummyTag, bool show)
{
	if(m_pPlot)
		m_pPlot->setFeatureDummyVisibility(dummyTag.c_str(), show);
}

void CyPlot::addFeatureDummyModel(std::string dummyTag, std::string modelTag)
{
	if(m_pPlot)
		m_pPlot->addFeatureDummyModel(dummyTag.c_str(), modelTag.c_str());
}

void CyPlot::setFeatureDummyTexture(std::string dummyTag, std::string textureTag)
{
	if(m_pPlot)
		m_pPlot->setFeatureDummyTexture(dummyTag.c_str(), textureTag.c_str());
}

std::string CyPlot::pickFeatureDummyTag(int mouseX, int mouseY)
{
	if(m_pPlot)
		return m_pPlot->pickFeatureDummyTag(mouseX, mouseY);
	else
		return "";
}

void CyPlot::resetFeatureModel()
{
	if(m_pPlot)
		m_pPlot->resetFeatureModel();
}

int CyPlot::getFeatureVariety()
{
	return m_pPlot ? m_pPlot->getFeatureVariety() : -1;
}

int CyPlot::getOwnershipDuration()
{
	return m_pPlot ? m_pPlot->getOwnershipDuration() : -1;
}

bool CyPlot::isOwnershipScore()
{
	return m_pPlot ? m_pPlot->isOwnershipScore() : false;
}

void CyPlot::setOwnershipDuration(int iNewValue)
{
	if (m_pPlot)
		m_pPlot->setOwnershipDuration(iNewValue);
}

void CyPlot::changeOwnershipDuration(int iChange)
{
	if (m_pPlot)
		m_pPlot->changeOwnershipDuration(iChange);
}

int CyPlot::getImprovementDuration()
{
	return m_pPlot ? m_pPlot->getImprovementDuration() : -1;
}

void CyPlot::setImprovementDuration(int iNewValue)
{
	if (m_pPlot)
		m_pPlot->setImprovementDuration(iNewValue);
}

void CyPlot::changeImprovementDuration(int iChange)
{
	if (m_pPlot)
		m_pPlot->changeImprovementDuration(iChange);
}

int /* BonusTypes */ CyPlot::getBonusType(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->getBonusType((TeamTypes)eTeam) : -1;
}

int /* BonusTypes */ CyPlot::getNonObsoleteBonusType(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->getNonObsoleteBonusType((TeamTypes)eTeam) : -1;
}

void CyPlot::setBonusType(int /* BonusTypes */ eNewValue)
{
	if (m_pPlot)
	{
		bool const bWorldBuilder = isSASWorldBuilderEditContext();
		bool const bLog = bWorldBuilder && isSASWorldBuilderEditLoggingEnabled();
		SASGameRecordPlotState kOldState;
		if (bWorldBuilder) kOldState = SASGameRecordPlotState(*m_pPlot);
		m_pPlot->setBonusType((BonusTypes)eNewValue);
		if (bWorldBuilder) recordSASWorldBuilderPlotChange(*m_pPlot, kOldState, bLog);
	}
}

int /* ImprovementTypes */ CyPlot::getImprovementType()
{
	return m_pPlot ? m_pPlot->getImprovementType() : -1;
}

void CyPlot::setImprovementType(int /* ImprovementTypes */ eNewValue)
{
	if (m_pPlot)
	{
		bool const bWorldBuilder = isSASWorldBuilderEditContext();
		bool const bLog = bWorldBuilder && isSASWorldBuilderEditLoggingEnabled();
		SASGameRecordPlotState kOldState;
		if (bWorldBuilder) kOldState = SASGameRecordPlotState(*m_pPlot);
		m_pPlot->setImprovementType((ImprovementTypes)eNewValue);
		if (bWorldBuilder) recordSASWorldBuilderPlotChange(*m_pPlot, kOldState, bLog);
	}
}

int /* RouteTypes */ CyPlot::getRouteType()
{
	return m_pPlot ? m_pPlot->getRouteType() : -1;
}

void CyPlot::setRouteType(int /*RouteTypes*/ eNewValue)
{
	if (m_pPlot)
	{
		bool const bWorldBuilder = isSASWorldBuilderEditContext();
		bool const bLog = bWorldBuilder && isSASWorldBuilderEditLoggingEnabled();
		SASGameRecordPlotState kOldState;
		if (bWorldBuilder) kOldState = SASGameRecordPlotState(*m_pPlot);
		m_pPlot->setRouteType((RouteTypes)eNewValue);
		if (bWorldBuilder) recordSASWorldBuilderPlotChange(*m_pPlot, kOldState, bLog);
	}
}

CyCity* CyPlot::getPlotCity()
{
	return m_pPlot ? new CyCity(m_pPlot->getPlotCity()) : NULL;
}

CyCity* CyPlot::getWorkingCity()
{
	return m_pPlot ? new CyCity(m_pPlot->getWorkingCity()) : NULL;
}

CyCity* CyPlot::getWorkingCityOverride()
{
	return m_pPlot ? new CyCity(m_pPlot->getWorkingCityOverride()) : NULL;
}

int CyPlot::getRiverID() const
{
	return m_pPlot ? m_pPlot->getRiverID() : -1;
}

void CyPlot::setRiverID(int iNewValue)
{
	if (m_pPlot)
		m_pPlot->setRiverID(safeIntCast<short>(iNewValue));
}

int CyPlot::getMinOriginalStartDist()
{
	return m_pPlot ? m_pPlot->getMinOriginalStartDist() : -1;
}

int CyPlot::getReconCount()
{
	return m_pPlot ? m_pPlot->getReconCount() : -1;
}

int CyPlot::getRiverCrossingCount()
{
	return m_pPlot ? m_pPlot->getRiverCrossingCount() : -1;
}

int CyPlot::getYield(YieldTypes eIndex)
{
	return m_pPlot ? m_pPlot->getYield(eIndex) : -1;
}

// K-Mod, 26/Jun/2011, karadoc: changed enum types to ints, so that it actually works...
/*	advc: Reverted the K-Mod change. It seems that no automatic type conversion will
	take place either way. It's not clear that accepting only int params is better than
	accepting only enum params. */
int CyPlot::calculateNatureYield(YieldTypes eIndex, TeamTypes eTeam, bool bIgnoreFeature)
{
	return m_pPlot ? m_pPlot->calculateNatureYield(eIndex, eTeam, bIgnoreFeature) : -1;
}

int CyPlot::calculateBestNatureYield(YieldTypes eIndex, TeamTypes eTeam)
{
	return m_pPlot ? m_pPlot->calculateBestNatureYield(eIndex, eTeam) : -1;
}

int CyPlot::calculateTotalBestNatureYield(TeamTypes eTeam)
{
	return m_pPlot ? m_pPlot->calculateTotalBestNatureYield(eTeam) : -1;
}

int CyPlot::calculateImprovementYieldChange(int /*ImprovementTypes*/ eImprovement, YieldTypes eYield, int /*PlayerTypes*/ ePlayer, bool bOptimal)
{
	return m_pPlot ? m_pPlot->calculateImprovementYieldChange((ImprovementTypes)
			eImprovement, eYield, (PlayerTypes)ePlayer) // advc: bOptimal is obsolete
			: -1;
}

int CyPlot::calculateYield(YieldTypes eIndex, bool bDisplay)
{
	return m_pPlot ? m_pPlot->calculateYield(eIndex, bDisplay) : -1;
}

bool CyPlot::hasYield()
{
	return m_pPlot ? m_pPlot->hasYield() : false;
}

int CyPlot::getCulture(int /*PlayerTypes*/ eIndex)
{
	return m_pPlot ? m_pPlot->getCulture((PlayerTypes)eIndex) : -1;
}

int CyPlot::countTotalCulture()
{	// advc.opt: was calling CvPlot::countTotalCulture
	return m_pPlot ? m_pPlot->getTotalCulture() : -1;
}

int /*TeamTypes*/ CyPlot::findHighestCultureTeam()
{
	return m_pPlot ? m_pPlot->findHighestCultureTeam() : -1;
}

int CyPlot::calculateCulturePercent(int /*PlayerTypes*/ eIndex)
{
	return m_pPlot ? m_pPlot->calculateCulturePercent((PlayerTypes)eIndex) : -1;
}

int CyPlot::calculateTeamCulturePercent(int /*TeamTypes*/ eIndex)
{
	return m_pPlot ? m_pPlot->calculateTeamCulturePercent((TeamTypes)eIndex) : -1;
}

void CyPlot::setCulture(int /*PlayerTypes*/ eIndex, int iChange, bool bUpdate)
{
	if (m_pPlot)
		m_pPlot->setCulture((PlayerTypes)eIndex, iChange, bUpdate, true);
}

void CyPlot::changeCulture(int /*PlayerTypes*/ eIndex, int iChange, bool bUpdate)
{
	if (m_pPlot)
		m_pPlot->changeCulture((PlayerTypes)eIndex, iChange, bUpdate);
}

int CyPlot::countNumAirUnits(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->countNumAirUnits((TeamTypes)eTeam) : -1;
}

int CyPlot::getFoundValue(int /*PlayerTypes*/ eIndex)
{
	return m_pPlot ? m_pPlot->getFoundValue((PlayerTypes)eIndex) : -1;
}

bool CyPlot::isBestAdjacentFound(int /*PlayerTypes*/ eIndex)
{
	return m_pPlot ? m_pPlot->isBestAdjacentFound((PlayerTypes)eIndex) : false;
}

int CyPlot::getPlayerCityRadiusCount(int /*PlayerTypes*/ eIndex)
{
	return m_pPlot ? m_pPlot->getPlayerCityRadiusCount((PlayerTypes)eIndex) : -1;
}

bool CyPlot::isPlayerCityRadius(int /*PlayerTypes*/ eIndex)
{
	return m_pPlot ? m_pPlot->isPlayerCityRadius((PlayerTypes)eIndex) : false;
}

int CyPlot::getVisibilityCount(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->getVisibilityCount((TeamTypes)eTeam) : -1;
}

void CyPlot::changeVisibilityCount(int /*TeamTypes*/ eTeam, int iChange, int /*InvisibleTypes*/ eSeeInvisible)
{
	if (m_pPlot)
		m_pPlot->changeVisibilityCount((TeamTypes) eTeam, iChange, (InvisibleTypes) eSeeInvisible, true);
}

int CyPlot::getStolenVisibilityCount(int /*TeamTypes*/ eTeam)
{
	return m_pPlot ? m_pPlot->getStolenVisibilityCount((TeamTypes)eTeam) : -1;
}

int /*PlayerTypes*/ CyPlot::getRevealedOwner(int /*TeamTypes*/ eTeam, bool bDebug)
{
	return m_pPlot ? m_pPlot->getRevealedOwner((TeamTypes)eTeam, bDebug) : -1;
}

int /*TeamTypes*/ CyPlot::getRevealedTeam(int /*TeamTypes*/ eTeam, bool bDebug)
{
	return m_pPlot ? m_pPlot->getRevealedTeam((TeamTypes)eTeam, bDebug) : -1;
}

bool CyPlot::isRiverCrossing(DirectionTypes eIndex)
{
	return m_pPlot ? m_pPlot->isRiverCrossing(eIndex) : false;
}

bool CyPlot::isRevealed(int /*TeamTypes*/ eTeam, bool bDebug)
{
	return m_pPlot ? m_pPlot->isRevealed((TeamTypes)eTeam, bDebug) : false;
}

void CyPlot::setRevealed(int /*TeamTypes*/ eTeam, bool bNewValue, bool bTerrainOnly, int /*TeamTypes*/ eFromTeam)
{
	if (m_pPlot)
	{
		bool const bWorldBuilder = isSASWorldBuilderEditContext();
		bool const bOldValue = bWorldBuilder ? m_pPlot->isRevealed((TeamTypes)eTeam, false) : false;
		m_pPlot->setRevealed((TeamTypes)eTeam, bNewValue, bTerrainOnly, (TeamTypes)eFromTeam, true);
		bool const bNewObservedValue = bWorldBuilder ? m_pPlot->isRevealed((TeamTypes)eTeam, false) : false;
		if (bWorldBuilder && bOldValue != bNewObservedValue)
		{
			if (GC.getGame().isSASWorldBuilderBulkEdit())
				GC.getGame().noteSASWorldBuilderBulkRevealChange();
			else
				GC.getGame().recordSASWorldBuilderEdit(SAS_WORLD_CHANGES_HISTORY_VISIBILITY, "SET_REVEALED", m_pPlot->getX(), m_pPlot->getY(), NO_PLAYER, -1, "TEAM", "-", bOldValue ? 1 : 0, bNewObservedValue ? 1 : 0, false, true, true, (TeamTypes)eTeam);
		}
	}
}

int /* ImprovementTypes */ CyPlot::getRevealedImprovementType(int /*TeamTypes*/ eTeam, bool bDebug)
{
	return m_pPlot ? m_pPlot->getRevealedImprovementType((TeamTypes)eTeam, bDebug) : -1;
}

int /* RouteTypes */ CyPlot::getRevealedRouteType(int /*TeamTypes*/ eTeam, bool bDebug)
{
	return m_pPlot ? m_pPlot->getRevealedRouteType((TeamTypes)eTeam, bDebug) : -1;
}

int CyPlot::getBuildProgress(int /*BuildTypes*/ eBuild)
{
	return m_pPlot ? m_pPlot->getBuildProgress((BuildTypes)eBuild) : -1;
}

// advc.251: Last param now ePlayer (was eTeam)
bool CyPlot::changeBuildProgress(int /*BuildTypes*/ eBuild, int iChange, int /*PlayerTypes*/ ePlayer)
{
	return m_pPlot ? m_pPlot->changeBuildProgress((BuildTypes)eBuild, iChange,
			(PlayerTypes)ePlayer) : false;
}

int CyPlot::getCultureRangeCities(int eOwnerIndex, int eRangeIndex)
{
	return m_pPlot ? m_pPlot->getCultureRangeCities((PlayerTypes)eOwnerIndex,
			(CultureLevelTypes)eRangeIndex) : -1;
}

bool CyPlot::isCultureRangeCity(int eOwnerIndex, int eRangeIndex)
{
	return m_pPlot ? m_pPlot->isCultureRangeCity((PlayerTypes) eOwnerIndex,
		(CultureLevelTypes)eRangeIndex) : false;
}

int CyPlot::getInvisibleVisibilityCount(int /*TeamTypes*/ eTeam, int /*InvisibleTypes*/ eInvisible)
{
	return m_pPlot ? m_pPlot->getInvisibleVisibilityCount((TeamTypes) eTeam, (InvisibleTypes) eInvisible) : -1;
}

bool CyPlot::isInvisibleVisible(int /*TeamTypes*/ eTeam, int /*InvisibleTypes*/ eInvisible)
{
	return m_pPlot ? m_pPlot->isInvisibleVisible((TeamTypes) eTeam, (InvisibleTypes) eInvisible) : false;
}

void CyPlot::changeInvisibleVisibilityCount(int /*TeamTypes*/ eTeam, int /*InvisibleTypes*/ eInvisible, int iChange)
{
	if (m_pPlot)
		m_pPlot->changeInvisibleVisibilityCount((TeamTypes) eTeam, (InvisibleTypes) eInvisible, iChange);
}

int CyPlot::getNumUnits()
{
	return m_pPlot ? m_pPlot->getNumUnits() : -1;
}

CyUnit* CyPlot::getUnit(int iIndex)
{
	return m_pPlot ? new CyUnit(m_pPlot->getUnitByIndex(iIndex)) : NULL;
}

std::string CyPlot::getScriptData() const
{
	return m_pPlot ? m_pPlot->getScriptData() : "";
}

void CyPlot::setScriptData(std::string szNewValue)
{
	if (m_pPlot)
	{
		bool const bWorldBuilderEdit = isSASWorldBuilderEditContext();
		CvString szOldScript;
		if (bWorldBuilderEdit) szOldScript = m_pPlot->getScriptData();
		m_pPlot->setScriptData(szNewValue.c_str());
		// <!-- custom: Inspect the applied value only inside the editor path; ordinary script setters do no history formatting or policy lookup.
		// The shared recorder decides whether text is retained. (GPT-6.1-Sol) -->
		if (bWorldBuilderEdit)
		{
			std::string const szAppliedScript = m_pPlot->getScriptData();
			if (szOldScript != szAppliedScript)
				GC.getGame().recordSASWorldBuilderScriptEdit(SAS_WORLD_CHANGES_HISTORY_MAP, m_pPlot->getX(), m_pPlot->getY(), m_pPlot->getOwner(), -1, szAppliedScript);
		}
	}
}

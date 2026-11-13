#include "CvGameCoreDLL.h"
#include "CvGame.h"
#include "CoreAI.h"
#include "CvCityAI.h"
#include "CvUnitAI.h"
#include "CvSelectionGroup.h"
#include "GroupPathFinder.h"
#include "FAStarNode.h"
#include "PlotRange.h"
#include "CvInfo_City.h"
#include "CvInfo_Command.h"
#include "CvInfo_Terrain.h"
#include "CvInfo_GameOption.h"
#include "RiseFall.h" // advc.700
#include "CvPopupInfo.h"
#include "CvDiploParameters.h" // <!-- custom: tableSASPilotDeal opens the diplomacy screen with offer lists, as CvPlayer::contact does; CvGame.h only forward-declares the class. (Claude code Opus 5.5) -->
#include "CvDLLButtonPopup.h" // <!-- custom: chooseSASPilotFreeTech finds and removes the exact held free-tech chooser with the held-popup helpers declared there; Codex found that closing choosers by type and count could discard another award. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
#include "CvGameTextMgr.h"
#include "CvMessageControl.h"
#include "CvBugOptions.h"
#include "SASGameRecordLog.h" // <!-- custom: Native view-control transitions and city-circle submissions are recorded at their actual application points; avoid inferring live UI state from configured values or rescoring plots for diagnostics. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
#include "SelfMod.h" // advc.092b
#include "CvArea.h" // <!-- custom: The SASPilot native prototype writes each plot's area ID; CvPlot only forward-declares CvArea, and the first build failed with C2027. (Claude code Opus 5.5) -->
#include "CvInfo_Civics.h" // <!-- custom: getSASPilotTradeItemsJson names a tradeable civic by its CvCivicInfo type; the /Zs check failed with C2027 without it, as nothing here defined the class. (Claude code Opus 5.5) -->
#include "CvTalkingHeadMessage.h" // <!-- custom: getSASPilotMessagesJson reads each message's text, turn and plot; CvPlayer.h only forward-declares the class, and the first build failed with C2027. (Claude code Fable 5.2) -->
#include <fstream> // advc.003d
#include <errno.h> // <!-- custom: errno and ERANGE for readSASPilotInt's overflow check (Codex's review of the pilot's trade lists). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
#include <limits.h> // <!-- custom: INT_MIN and INT_MAX for the same check. (Claude code Opus 5.5) -->

/*  advc: This file was added by patch 3.17, moving some UI functionality
	out of the EXE and thus exposing it to mods.
	The near name clash with CyGameInterface.cpp is coincidental. */

/*	<advc.007c> The functions in this header arguably shouldn't use any of the
	synchronized RNGs that are part of CvGame. */
#undef CVGAME_INSTANCE_FOR_RNG
#define CVGAME_INSTANCE_FOR_RNG NULL // </advc.007c>

void CvGame::updateColoredPlots()
{
	PROFILE_FUNC();
	// <advc.004z> Too early; player options haven't been set yet.
	if (getTurnSlice() <= 0)
		return; // </advc.004z>
	CvDLLEngineIFaceBase& kEngine = *gDLL->getEngineIFace();
	CvDLLInterfaceIFaceBase& kUI = gDLL->UI();

	kEngine.clearColoredPlots(PLOT_LANDSCAPE_LAYER_BASE);
	kEngine.clearAreaBorderPlots(AREA_BORDER_LAYER_CITY_RADIUS);
	kEngine.clearAreaBorderPlots(AREA_BORDER_LAYER_RANGED);
	kEngine.clearAreaBorderPlots(AREA_BORDER_LAYER_BLOCKADING);

	if (!gDLL->GetWorldBuilderMode() || kUI.isInAdvancedStart())
		kEngine.clearColoredPlots(PLOT_LANDSCAPE_LAYER_RECOMMENDED_PLOTS);

	if (GC.getPythonCaller()->updateColoredPlots())
		return;
	// <advc.004h>
	// Moved up
	CvUnit* pHeadSelectedUnit = kUI.getHeadSelectedUnit();
	if (pHeadSelectedUnit != NULL && pHeadSelectedUnit->isHuman())
		pHeadSelectedUnit->updateFoundingBorder();
	// </advc.004h>

	// <!-- custom: Capture the native circle submissions themselves, before any purchase; callback frequency is UI-driven rather than once per turn.
	// Gate diagnostic context/collection first.
	// The recorder suppresses unchanged sets and reuses costs/path decisions below, so it adds no diagnostic map scan or pathfinding.
	// WorldBuilder/Python-owned overlays are excluded; debug all-player site circles are observed separately from the active-player recommendations.
	// These are native draw requests rather than proof of a rendered frame. (GPT-6.1-Sol) -->
	bool const bLogSASCityRecommendations = (gGameRecordLogLevel >= 2 && isSASGameRecordActionTraceEnabled() && getActivePlayer() != NO_PLAYER && (!gDLL->GetWorldBuilderMode() || kUI.isInAdvancedStart()));
	if (bLogSASCityRecommendations) beginSASGameRecordCityRecommendations(getActivePlayer(), kUI.isInAdvancedStart(), (!kUI.isInAdvancedStart() && kUI.getHeadSelectedCity() == NULL && pHeadSelectedUnit != NULL && pHeadSelectedUnit->isFound()) ? pHeadSelectedUnit->getID() : -1);
	// <!-- custom: The separate offer catalog performs gated quote queries only for changed setup state or target context; circle collection itself still reuses native draw computations. (GPT-6.1-Sol) -->
	if (bLogSASCityRecommendations && kUI.isInAdvancedStart()) logSASGameRecordAdvancedStartOffers(GET_PLAYER(getActivePlayer()), kUI.getMouseOverPlot(), false);

	CvMap const& kMap = GC.getMap();
	bool bLogSASDebugCitySites = false;
	// BETTER_BTS_AI_MOD, Debug, 06/25/09, jdog5000: START
	if (isDebugMode())
	{
		if (kUI.isShowYields() && !gDLL->GetWorldBuilderMode()) // advc.007
		{
			// <!-- custom: This all-player shortlist overlay is independent of the ordinary unit-recommendation option and selected Settler.
			// Observe its existing draw submissions under a separate source/owner identity; Worker debug circles remain disabled below. (GPT-6.1-Sol) -->
			if (bLogSASCityRecommendations) bLogSASDebugCitySites = true;
			// City circles for debugging
			for (PlayerAIIter<CIV_ALIVE> itPlayer; itPlayer.hasNext(); ++itPlayer)
			{
				for (int i = 0; i < itPlayer->AI_getNumCitySites(); i++)
				{
					CvPlot const& kSite = itPlayer->AI_getCitySite(i);
					kEngine.addColoredPlot(kSite.getX(), kSite.getY(),
							GC.getInfo(GC.getInfo(itPlayer->getPlayerColor()).
							getColorTypePrimary()).getColor(),
							PLOT_STYLE_CIRCLE, PLOT_LANDSCAPE_LAYER_BASE);
					if (bLogSASCityRecommendations) addSASGameRecordDebugCitySite(itPlayer->getID(), kSite, i + 1);
				}
			}
			// <!-- custom: even in debugging (if i understood it correctly), these are confusing and needlessly taking computing power too, we use CvUnitAI::AI_bestCityBuild now anyway instead to choose our best plots to build on and all for AI workers, so try to gradually remove old code influence, while increasing performance if we can do so as well or functionality -->
			// // Plot improvement replacement circles for debugging
			// FOR_EACH_ENUM(PlotNum)
			// {
			// 	CvPlot& kPlot = kMap.getPlotByIndex(eLoopPlotNum);
			// 	CvCityAI const* pWorkingCity = kPlot.AI_getWorkingCity();
			// 	ImprovementTypes eImprovement = kPlot.getImprovementType();
			// 	if (pWorkingCity != NULL && eImprovement != NO_IMPROVEMENT)
			// 	{
			// 		CityPlotTypes ePlot = pWorkingCity->getCityPlotIndex(kPlot);
			// 		//int iBuildValue = pWorkingCity->AI_getBestBuildValue(ePlot);
			// 		BuildTypes eBestBuild = pWorkingCity->AI_getBestBuild(ePlot);
			// 		if (eBestBuild != NO_BUILD)
			// 		{
			// 			if (GC.getInfo(eBestBuild).getImprovement() != NO_IMPROVEMENT &&
			// 				eImprovement != GC.getInfo(eBestBuild).getImprovement())
			// 			{
			// 				kEngine.addColoredPlot(kPlot.getX(), kPlot.getY(),
			// 						GC.getInfo(GC.getColorType("RED")).getColor(),
			// 						PLOT_STYLE_CIRCLE, PLOT_LANDSCAPE_LAYER_BASE);
			// 			}
			// 		}
			// 	}
			// }
		}
	} // BETTER_BTS_AI_MOD: END

	// <!-- custom: make these static const for performance optimization as advised by chatgpt 5 too. -->
	// <!-- custom: code/performance optimization: hoist -->
	static const ColorTypes eColorWarningText = (ColorTypes)GC.getColorType("WARNING_TEXT");
	static const ColorTypes eColorHighlightText = (ColorTypes)GC.getColorType("HIGHLIGHT_TEXT");
	static const ColorTypes eColorWhite = (ColorTypes)GC.getColorType("WHITE");
	static const ColorTypes eColorYellow = (ColorTypes)GC.getColorType("YELLOW");

	// City circles when in Advanced Start
	if (kUI.isInAdvancedStart())
	{
		FOR_EACH_ENUM(PlotNum)
		{
			CvPlot& kPlot = kMap.getPlotByIndex(eLoopPlotNum);
			// <!-- custom: Reuse the draw branch's existing cost for SGR instead of querying it again. (GPT-6.1-Sol) -->
			int const iCityCost = GET_PLAYER(getActivePlayer()).getAdvancedStartCityCost(true, &kPlot);
			if (iCityCost > 0)
			{
				PlayerTypes eStartingPlayer = NO_PLAYER;
				FOR_EACH_ENUM(Player)
				{
					CvPlayer const& kPlayer = GET_PLAYER(eLoopPlayer);
					if (kPlayer.isAlive() && getActiveTeam() == kPlayer.getTeam() &&
						&kPlot == kPlayer.getStartingPlot())
					{
						eStartingPlayer = eLoopPlayer;
						break;
					}
				}
				if (eStartingPlayer != NO_PLAYER)
				{
					kEngine.addColoredPlot(kPlot.getX(), kPlot.getY(),
							GC.getInfo(eColorWarningText).getColor(),
							PLOT_STYLE_CIRCLE, PLOT_LANDSCAPE_LAYER_RECOMMENDED_PLOTS);
					if (bLogSASCityRecommendations) addSASGameRecordCityRecommendation(kPlot, iCityCost, eStartingPlayer);
				}
				else if (GET_PLAYER(getActivePlayer()).AI_isPlotCitySite(kPlot))
				{
					kEngine.addColoredPlot(kPlot.getX(), kPlot.getY(),
							GC.getInfo(eColorHighlightText).getColor(),
							PLOT_STYLE_CIRCLE, PLOT_LANDSCAPE_LAYER_RECOMMENDED_PLOTS);
					if (bLogSASCityRecommendations) addSASGameRecordCityRecommendation(kPlot, iCityCost);
				}
				if (kPlot.isRevealed(getActiveTeam()))
				{
					NiColorA color(GC.getInfo(eColorWhite).getColor());
					color.a = 0.4f;
					kEngine.fillAreaBorderPlot(kPlot.getX(), kPlot.getY(),
							color, AREA_BORDER_LAYER_CITY_RADIUS);
				}
			}
		}
	}

	CvCity const* pHeadSelectedCity = kUI.getHeadSelectedCity();
	if (pHeadSelectedCity != NULL)
	{
		if (kUI.isCityScreenUp())
		{
			NiColorA color(GC.getInfo(eColorWhite).getColor());
			color.a = 0.7f; // advc: Moved out of the loop below
			for (WorkingPlotIter it(*pHeadSelectedCity); it.hasNext(); ++it)
			{
				kEngine.addColoredPlot(it->getX(), it->getY(), color,
						PLOT_STYLE_CIRCLE, PLOT_LANDSCAPE_LAYER_BASE);
			}
		}
		else
		{
			for (CLLNode<IDInfo> const* pNode = kUI.headSelectedCitiesNode();
				pNode != NULL; pNode = kUI.nextSelectedCitiesNode(pNode))
			{
				CvCity const* pSelectedCity = ::getCity(pNode->m_data);
				if (pSelectedCity == NULL)
				{
					FAssertMsg(pSelectedCity != NULL, "Can this happen?");
					continue;
				}
				CvPlot* pRallyPlot = pSelectedCity->getRallyPlot();
				if (pRallyPlot != NULL)
				{
					kEngine.addColoredPlot(pRallyPlot->getX(), pRallyPlot->getY(),
							GC.getInfo(eColorYellow).getColor(),
							PLOT_STYLE_CIRCLE, PLOT_LANDSCAPE_LAYER_BASE);
				}
			}
		} // <advc>
		if (bLogSASCityRecommendations) endSASGameRecordCityRecommendations(-1, bLogSASDebugCitySites);
		return;
	}
	if (pHeadSelectedUnit == NULL)
	{
		// <!-- custom: Finalize an empty/Advanced Start circle set even when no unit is selected. (GPT-6.1-Sol) -->
		if (bLogSASCityRecommendations) endSASGameRecordCityRecommendations(-1, bLogSASDebugCitySites);
		return; // </advc>
	}

	if (gDLL->getGraphicOption(GRAPHICOPTION_CITY_RADIUS))
	{
		//if (kUI.canSelectionListFound())
		if (pHeadSelectedUnit->isFound()) // advc.004h
		{
			FOR_EACH_ENUM(PlotNum)
			{
				CvPlot& kPlot = kMap.getPlotByIndex(eLoopPlotNum);
				if (kPlot.getOwner() == pHeadSelectedUnit->getOwner())
				{
					if (kPlot.getWorkingCity() != NULL)
					{
						NiColorA color(GC.getInfo(eColorHighlightText
								/*(GC.getInfo(GET_PLAYER(pHeadSelectedUnit->getOwner()).getPlayerColor()).getColorTypePrimary())*/
								).getColor());
						color.a = 1.0f;
						kEngine.fillAreaBorderPlot(kPlot.getX(), kPlot.getY(),
								color, AREA_BORDER_LAYER_CITY_RADIUS);
					}
				}
			}
		}
	}
	/*	advc.rstr: Merged air range with ranged strike code so that the maximal range
		is highlighted also for range-strikers */
	if (pHeadSelectedUnit->airRange() > 0)
	{
		int iMaxAirRange = 0;
		for (CLLNode<IDInfo> const* pNode = kUI.headSelectionListNode();
			pNode != NULL; pNode = kUI.nextSelectionListNode(pNode))
		{
			CvUnit const* pSelectedUnit = ::getUnit(pNode->m_data);
			if (pSelectedUnit != NULL)
				iMaxAirRange = std::max(iMaxAirRange, pSelectedUnit->airRange());
		}
		if (iMaxAirRange > 0)
		{
			bool const bAir = (pHeadSelectedUnit->getDomainType() == DOMAIN_AIR);
			for (PlotCircleIter it(*pHeadSelectedUnit, iMaxAirRange); it.hasNext(); ++it)
			{
				CvPlot const& kTargetPlot = *it;
				if (bAir ||
					(kTargetPlot.isVisible(pHeadSelectedUnit->getTeam()) /*&&
					// advc.rstr: See CvUnit::canRangeStrikeAt
					pHeadSelectedUnit->getPlot().canSeePlot(
					&kTargetPlot, pHeadSelectedUnit->getTeam(), iMaxAirRange,
					pHeadSelectedUnit->getFacingDirection(true))*/))
				{
					NiColorA color(GC.getInfo(eColorYellow).getColor());
					color.a = 0.5f;
					kEngine.fillAreaBorderPlot(kTargetPlot.getX(), kTargetPlot.getY(),
							color, AREA_BORDER_LAYER_RANGED);
				}
			}
		}
	}

	// <!-- custom: Reuse the inherited display gate for both drawing and the observation summary, so no visible city circles can be distinguished from recommendations suppressed by the player's option.
	// Advanced Start uses its earlier independent draw branch; preserve that behavior and the current UI preference. (GPT-6.1-Sol) -->
	bool const bUnitRecommendationsEnabled = (!GET_PLAYER(getActivePlayer()).isOption(PLAYEROPTION_NO_UNIT_RECOMMENDATIONS) || !GET_PLAYER(getActivePlayer()).isHuman()); // advc.127
	if (bUnitRecommendationsEnabled)
	{
		// <!-- custom: also disable worker plot to improve recommendations, we save computation this way, reduce the interference of old very inefficient and perhaps needlessly computationally expensive, on top of tiles shown not necessarily being the best as well.
		// We only want to see city sites and such and not have too many needless circles that are confusing as well on top of using needless computing power; located code spot to remove thanks to claude ai after i found first one above in this function -->
		// CvUnitAI const& kRecommendUnit = pHeadSelectedUnit->AI(); // advc.003u
		// if (kRecommendUnit.AI_getUnitAIType() == UNITAI_WORKER ||
		// 	kRecommendUnit.AI_getUnitAIType() == UNITAI_WORKER_SEA)
		// {
		// 	if (kRecommendUnit.getPlot().getOwner() == kRecommendUnit.getOwner())
		// 	{
		// 		CvCityAI* pCity = kRecommendUnit.getPlot().AI_getWorkingCity();
		// 		if (pCity != NULL)
		// 		{
		// 			CvPlot* pBestPlot = NULL;
		// 			if (kRecommendUnit.AI_bestCityBuild(*pCity, &pBestPlot) &&
		// 				pCity->AI_getBestBuildValue(pCity->getCityPlotIndex(*pBestPlot)) > 1)
		// 			{
		// 				FAssert(pBestPlot != NULL);
		// 				kEngine.addColoredPlot(pBestPlot->getX(), pBestPlot->getY(),
		// 						GC.getInfo(GC.getColorType("HIGHLIGHT_TEXT")).getColor(),
		// 						PLOT_STYLE_CIRCLE, PLOT_LANDSCAPE_LAYER_RECOMMENDED_PLOTS);
		// 				CvPlot* pNextBestPlot = NULL;
		// 				if (kRecommendUnit.AI_bestCityBuild(*pCity, &pNextBestPlot, NULL, pBestPlot) &&
		// 					pCity->AI_getBestBuildValue(pCity->getCityPlotIndex(*pNextBestPlot)) > 1)
		// 				{
		// 					FAssert(pNextBestPlot != NULL);
		// 					kEngine.addColoredPlot(pNextBestPlot->getX(), pNextBestPlot->getY(),
		// 							GC.getInfo(GC.getColorType("HIGHLIGHT_TEXT")).getColor(),
		// 							PLOT_STYLE_CIRCLE, PLOT_LANDSCAPE_LAYER_RECOMMENDED_PLOTS);
		// 				}
		// 			}
		// 		}
		// 	}
		// }

		/*	K-Mod. I've rearranged the following code a bit, so that it is more efficient, and so that
			it shows city sites within 7 turns, rather than just the ones in 4 plot range.
			the original code has been deleted, because it was quite bulky. */
		int const iMaxPathTurns = 7;
		// city sites
		CvPlayerAI const& kActivePlayer = GET_PLAYER(getActivePlayer());
		GroupPathFinder sitePath;
		sitePath.setGroup(*pHeadSelectedUnit->getGroup(), NO_MOVEMENT_FLAGS,
				iMaxPathTurns, GC.getMOVE_DENOMINATOR());
		if (pHeadSelectedUnit->isFound())
		{
			for (int i = 0; i < kActivePlayer.AI_getNumCitySites(); i++)
			{
				CvPlot const& kSite = kActivePlayer.AI_getCitySite(i);
				/*	(advc: BUFFY adds this check. I've instead removed the
					vision cheats from the AI city site evaluation.) */
				if (//kSite.isVisible(kActivePlayer.getTeam()) &&
					sitePath.generatePath(kSite))
				{	// <advc.004> Don't show weak sites if they're far away
					if (sitePath.getPathTurns() + i > iMaxPathTurns + 1)
						continue; // </advc.004>
					kEngine.addColoredPlot(kSite.getX(), kSite.getY(),
							GC.getInfo(eColorHighlightText).getColor(),
							PLOT_STYLE_CIRCLE, PLOT_LANDSCAPE_LAYER_RECOMMENDED_PLOTS);
					if (bLogSASCityRecommendations && !kUI.isInAdvancedStart()) addSASGameRecordCityRecommendation(kSite, -1);
				}
			}
		}
		// goody huts
		//if (kHeadUnit.isNoBadGoodies())
		if (pHeadSelectedUnit->canFight()) // advc.004z: Replacing the above
		{
			int iRange = 4;
			// <advc.004z>
			if (pHeadSelectedUnit->isNoBadGoodies())
				iRange++;
			else iRange--; // </advc.004z>
			// just a smaller range.
			sitePath.setGroup(*pHeadSelectedUnit->getGroup(), NO_MOVEMENT_FLAGS,
					iRange, GC.getMOVE_DENOMINATOR());

			for (SquareIter it(*pHeadSelectedUnit, iRange); it.hasNext(); ++it)
			{
				CvPlot const& kLoopPlot = *it;
				if (kLoopPlot.isVisible(pHeadSelectedUnit->getTeam()) &&
					kLoopPlot.isRevealedGoody(pHeadSelectedUnit->getTeam()))
				{
					if (sitePath.generatePath(kLoopPlot))
					{
						kEngine.addColoredPlot(kLoopPlot.getX(), kLoopPlot.getY(),
								GC.getInfo(eColorHighlightText).getColor(),
								PLOT_STYLE_CIRCLE, PLOT_LANDSCAPE_LAYER_RECOMMENDED_PLOTS);
					}
				}
			}
		}
		// K-Mod end
	}
	if (pHeadSelectedUnit->isBlockading())
	{
		for (MemberIter it(getActiveTeam()); it.hasNext(); ++it)
		{
			CvPlayer& kMember = *it;
			FOR_EACH_UNIT(pLoopUnit, kMember)
			{
				if (!pLoopUnit->isBlockading())
					continue;
				/*  <advc.033> Replacing code that was (mostly) equivalent
					to CvUnit::updatePlunder */
				std::vector<CvPlot*> apRange;
				pLoopUnit->blockadeRange(apRange);
				for (size_t j = 0; j < apRange.size(); j++) // </advc.033>
				{
					NiColorA color(GC.getInfo(GC.getInfo(
							/*GET_PLAYER(getActivePlayer())*/kMember. // advc.004
							getPlayerColor()).getColorTypePrimary()).getColor());
					color.a = 0.5f;
					kEngine.fillAreaBorderPlot(apRange[j]->getX(), apRange[j]->getY(),
							color, AREA_BORDER_LAYER_BLOCKADING);
				}
			}
		}
	}
	if (bLogSASCityRecommendations) endSASGameRecordCityRecommendations(bUnitRecommendationsEnabled ? 1 : 0, bLogSASDebugCitySites);
}


void CvGame::updateBlockadedPlots()
{
	PROFILE_FUNC();

	CvDLLEngineIFaceBase& kEngine = *gDLL->getEngineIFace(); // advc
	kEngine.clearAreaBorderPlots(AREA_BORDER_LAYER_BLOCKADED);
	CvMap const& kMap = GC.getMap();

	// <!-- custom: make these static const for performance optimization as advised by chatgpt 5 too. -->
	// <!-- custom: code/performance optimization: hoist -->
	static const ColorTypes eColorBlack = (ColorTypes)GC.getColorType("BLACK");

	for (int i = 0; i < kMap.numPlots(); ++i)
	{
		CvPlot& kPlot = kMap.getPlotByIndex(i);
		if (kPlot.getBlockadedCount(getActiveTeam()) > 0 && kPlot.isRevealed(getActiveTeam()))
		{
			NiColorA color(GC.getInfo(eColorBlack).getColor());
			color.a = 0.35f;
			kEngine.fillAreaBorderPlot(kPlot.getX(), kPlot.getY(), color, AREA_BORDER_LAYER_BLOCKADED);
		}
	}
	/*  <advc.700> An odd place for initialization. Need graphics to be fully
		initialized so that I can send an error msg to the player if necessary.
		Not the case in e.g. CvGame::init or setInitialItems. */
	if (isOption(GAMEOPTION_RISE_FALL) && getElapsedGameTurns() <= 0)
		m_pRiseFall->init(); // </advc.700>
}


void CvGame::updateSelectionList()
{
	// <!-- custom: Retired KI#107's isFinalInitialized guard, restoring base AdvCiv 1.14: a crash fix made without a matching PDB, so a recurrence should be traced with a Debug-opt dump. See KI#107 and KI#136. (Claude code Opus 4.6 + Claude code Opus 5.5) -->
	CvDLLInterfaceIFaceBase& kUI = gDLL->UI();
	CvUnit* pHeadSelectedUnit = kUI.getHeadSelectedUnit();
	// <advc.004k> (Needed for dealing with all units becoming unselected)
	if (pHeadSelectedUnit == NULL)
		gDLL->getEngineIFace()->clearAreaBorderPlots(AREA_BORDER_LAYER_PATROLLED);
	// </advc.004k>
	else pHeadSelectedUnit->onActiveSelection(); // advc
	if (GC.suppressCycling() || // K-Mod
		GET_PLAYER(getActivePlayer()).isOption(PLAYEROPTION_NO_UNIT_CYCLING))
	{
		return;
	}
	if (pHeadSelectedUnit == NULL || !pHeadSelectedUnit->getGroup()->readyToSelect(true))
	{
		if (kUI.getOriginalPlot() == NULL ||
			!cyclePlotUnits(kUI.getOriginalPlot(), true, true, kUI.getOriginalPlotCount()))
		{
			if (kUI.getSelectionPlot() == NULL ||
				!cyclePlotUnits(kUI.getSelectionPlot(), true, true))
			{
				cycleSelectionGroups(true);
			}
		}
		pHeadSelectedUnit = kUI.getHeadSelectedUnit();
		if (pHeadSelectedUnit != NULL &&
			!pHeadSelectedUnit->getGroup()->readyToSelect(/* advc.153: */ true))
		{
			kUI.clearSelectionList();
		}
	}
}


void CvGame::updateTestEndTurn()
{
	// <!-- custom: Retired KI#107's isFinalInitialized guard, restoring base AdvCiv 1.14: a crash fix made without a matching PDB, so a recurrence should be traced with a Debug-opt dump. See KI#107 and KI#136. (Claude code Opus 4.6 + Claude code Opus 5.5) -->
	if (!GET_PLAYER(getActivePlayer()).isTurnActive())
		return;
	// <advc.003g>
	if (!m_bFPTestDone)
		CvMessageControl::getInstance().sendFPTest(FPChecksum()); // </advc.003g>
	CvDLLInterfaceIFaceBase& kUI = gDLL->UI();
	bool const bAny = (kUI.getHeadSelectedUnit() != NULL &&
			!GET_PLAYER(getActivePlayer()).isOption(PLAYEROPTION_NO_UNIT_CYCLING));
	if (kUI.isEndTurnMessage())
	{
		if (GET_PLAYER(getActivePlayer()).hasReadyUnit(bAny))
		// <!-- custom: Observe the applied UI transition only when Runtime is enabled; the gameplay flag still changes first. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
		{
			kUI.setEndTurnMessage(false);
			if (isSASRuntimeStatusEnabled()) updateSASRuntimeStatusEndTurnReady(getActivePlayer(), false);
		}
		return;
	}
	if (GET_PLAYER(getActivePlayer()).hasBusyUnit() ||
		GET_PLAYER(getActivePlayer()).hasReadyUnit(bAny))
	{
		return;
	}
	bool const bShift = GC.shiftKey();
	if (!kUI.isForcePopup())
	{
		if (!bShift && !GC.suppressCycling()) // K-Mod
			kUI.setForcePopup(true);
		return;
	}
	if (GET_PLAYER(getActivePlayer()).hasAutoUnit())
	{
		//if (!(GC.shiftKey()))
		// K-Mod. Don't start automoves if we currently have a group selected which would move.
		CvUnit* pSelectedUnit = kUI.getHeadSelectedUnit();
		if (!bShift && !GC.suppressCycling() &&
			(pSelectedUnit == NULL || !pSelectedUnit->getGroup()->readyToAuto()))
		{ // K-Mod end
			CvMessageControl::getInstance().sendAutoMoves();
		}
		return;
	}
	if (GET_PLAYER(getActivePlayer()).isOption(PLAYEROPTION_WAIT_END_TURN) ||
		!kUI.isHasMovedUnit() || isHotSeat() || isPbem())
	{
		kUI.setEndTurnMessage(true);
		// <!-- custom: Observe the existing flag change above; only the Runtime notification below is added, with no per-frame diagnostic unit scan. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
		if (isSASRuntimeStatusEnabled()) updateSASRuntimeStatusEndTurnReady(getActivePlayer(), true);
		return;
	}
	if (kUI.getEndTurnCounter() > 0)
	{
		kUI.changeEndTurnCounter(-1);
		return;
	}
	CvMessageControl::getInstance().sendTurnComplete();
	kUI.setEndTurnCounter(3); // XXX
}

// advc: Merge of two BtS functions that had largely the same body
CvUnit* CvGame::getPlotUnits(CvPlot const* pPlot, std::vector<CvUnit*>* pPlotUnits, int iIndex) const
{
	PROFILE_FUNC();

	FAssert((iIndex == -1) != (pPlotUnits == NULL));

	if (pPlotUnits != NULL)
		pPlotUnits->clear();

	if (pPlot == NULL)
		return NULL;

	int iCount = 0;
	PlayerTypes eActivePlayer = getActivePlayer();
	TeamTypes eActiveTeam = getActiveTeam();
	for (int iPass = 0; iPass < 2; iPass++)
	{
		FOR_EACH_UNIT_VAR_IN(pUnit, *pPlot)
		{
			if ((pUnit->getOwner() == eActivePlayer) != (iPass == 0))
				continue;
			if (pUnit->isInvisible(eActiveTeam, true) || pUnit->isCargo())
				continue;

			if (iCount == iIndex)
				return pUnit;

			iCount++;
			if (pPlotUnits != NULL)
				pPlotUnits->push_back(pUnit);
			//if (pLoopUnit1->getTeam() == activeTeam || isDebugMode()) {
			if (!pUnit->hasCargo())
				continue;
			FOR_EACH_UNIT_VAR_IN(pCargoUnit, *pPlot)
			{
				if (pCargoUnit->isInvisible(eActiveTeam, true))
					continue;
				if (pCargoUnit->getTransportUnit() == pUnit)
				{
					if (iCount == iIndex)
						return pCargoUnit;

					iCount++;
					if (pPlotUnits != NULL)
						pPlotUnits->push_back(pCargoUnit);
				}
			}
		}
	}
	return NULL;
}


void CvGame::cycleCities(bool bForward, bool bAdd) const
{
	/*	advc: bForward is now handled a bit differently b/c I've added
		separate functions for backward traversal (no functional change) */

	CvCity* pHeadSelectedCity = gDLL->UI().getHeadSelectedCity();
	CvCity* pSelectCity = NULL;
	if (pHeadSelectedCity != NULL &&
		(pHeadSelectedCity->getTeam() == getActiveTeam() || isDebugMode()))
	{
		int iLoop = pHeadSelectedCity->getIndex();
		iLoop += (bForward ? 1 : -1);
		CvPlayer const& kOwner = GET_PLAYER(pHeadSelectedCity->getOwner());
		CvCity* pLoopCity = (bForward ? kOwner.nextCity(&iLoop) : kOwner.prevCity(&iLoop));

		if (pLoopCity == NULL)
			pLoopCity = (bForward ? kOwner.firstCity(&iLoop) : kOwner.lastCity(&iLoop));

		if (pLoopCity != NULL && pLoopCity != pHeadSelectedCity)
			pSelectCity = pLoopCity;
	}
	else
	{
		int iLoop;
		pSelectCity = (bForward ? GET_PLAYER(getActivePlayer()).firstCity(&iLoop) :
				GET_PLAYER(getActivePlayer()).lastCity(&iLoop));
	}

	if (pSelectCity != NULL)
	{
		if (bAdd)
		{
			gDLL->UI().clearSelectedCities();
			gDLL->UI().addSelectedCity(pSelectCity);
		}
		else gDLL->UI().selectCity(pSelectCity);
	}
}

// advc.154: Extracted the const part out of cycleSelectionGroups
// out-params
// <!-- custom: hoisted from multiline signature between `pCycleUnit` and `pCycledGroups` by collapse_cpp_signatures.py. (GPT-5.5 (reviewed script output)) -->
CvSelectionGroup* CvGame::getNextGroupInCycle(bool bForward, bool bWorkers, bool& bWrap, CvUnit*& pCycleUnit, std::set<int>* pCycledGroups) const
{
	bWrap = false;
	pCycleUnit = gDLL->UI().getHeadSelectedUnit();
	CvSelectionGroup* pGroup=NULL;
	if (pCycleUnit != NULL)
	{
		if (pCycleUnit->getOwner() != getActivePlayer())
			pCycleUnit = NULL;
		pGroup = GET_PLAYER(getActivePlayer()).getNextGroupInCycle(
				pCycleUnit, bForward, bWorkers, &bWrap, pCycledGroups);
	}
	else
	{
		CvPlot* pPlot = gDLL->UI().getLookAtPlot();
		pGroup = GC.getMap().findSelectionGroup(
				pPlot != NULL ? pPlot->getX() : 0,
				pPlot != NULL ? pPlot->getY() : 0,
				getActivePlayer(), true, bWorkers);
	}
	return pGroup;
}

/*	advc.154: Python wrapper for the above - but who knows, the DLL too
	might want to be able to tell what the cycle button is showing. */
CvUnit* CvGame::getCycleButtonUnit(bool bForward, bool bWorkers) const
{
	if (getActivePlayer() == NO_PLAYER ||
		!GET_PLAYER(getActivePlayer()).isHuman()) // AI Auto Play
	{
		return NULL;
	}
	bool bDummy=false;
	CvUnit* pDummy=NULL;
	CvSelectionGroup* pNextGroup = GC.getGame().getNextGroupInCycle(
			bForward, bWorkers, bDummy, pDummy);
	if (pNextGroup == NULL || pNextGroup->getNumUnits() <= 0)
		return NULL;
	for (int iPass = 0; iPass < (/*bWorkers ? 1 :*/ 2); iPass++)
	{
		FOR_EACH_UNIT_VAR_IN(pUnit, *pNextGroup)
		{
			if (!pUnit->IsSelected() && pUnit->canMove() &&
				/*	!bWorkers doesn't exclude all-worker groups, so we can only
					_prefer_ selecting a non-worker. */
				/*	Actually, let's always prefer to select a worker. Don't want
					to show different icons on the two buttons if they refer
					to the same group. */
				(iPass == 1 || /*bWorkers == */pUnit->isWorker()))
			{
				return pUnit;
			}
		}
	}
	return NULL;
}


void CvGame::cycleSelectionGroups(bool bClear, bool bForward, bool bWorkers)
{
	bool bWrap=false;
	CvUnit* pCycleUnit=NULL;
	// <advc.154> Moved into a const function ...
	CvSelectionGroup* pNextSelectionGroup = getNextGroupInCycle(
			bForward, bWorkers, bWrap, pCycleUnit); // </advc.154>
	if (gDLL->UI().getHeadSelectedUnit() != NULL)
	{
		GET_PLAYER(getActivePlayer()).cycleSelectionGroups(
				pCycleUnit, bForward, bWorkers, &bWrap);
	}
	if (bWrap)
	{	/*	K-Mod: I've weakend this condition so that the group cycle order
			can be refreshed by automoves.
			(Maybe I should create & use "sendCycleRefresh" instead.) */
		if (pNextSelectionGroup != NULL ||
			GET_PLAYER(getActivePlayer()).hasAutoUnit())
		{
			CvMessageControl::getInstance().sendAutoMoves();
		}
	}

	if (pNextSelectionGroup != NULL)
	{
		FAssert(pNextSelectionGroup->getOwner() == getActivePlayer());
		FAssert(pNextSelectionGroup->getHeadUnit() != NULL); // K-Mod
		gDLL->UI().selectUnit(pNextSelectionGroup->getHeadUnit(), bClear);
		/*	<advc.153> Could deselect units without moves here, but then
			the player can't just press skip without splitting up the group.
			Perhaps skip could somehow receive special treatment in this case ...
			So long as that's not implemented, it's better to let the player use
			the Go To (All) button if he or she does want to split the group. */
		/*FOR_EACH_UNIT_VAR_IN(pUnit, *pNextSelectionGroup)
		{
			if (!pUnit->canMove())
				gDLL->UI().removeFromSelectionList(pUnit);
		}*/ // </advc.153>
	}
	// K-Mod
	else if (pCycleUnit != NULL)
	{
		gDLL->UI().clearSelectionList();
		updateTestEndTurn();
		// <advc.002e> Hide glow when all units moved
		if (!BUGOption::isEnabled("PLE__ShowPromotionGlow", false))
		{
			CvPlayer const& kOwner = GET_PLAYER(pCycleUnit->getOwner());
			FOR_EACH_UNIT_VAR(u, kOwner)
				gDLL->getEntityIFace()->showPromotionGlow(u->getEntity(), false);
		} // </advc.002e>
	} // K-Mod end

	if (pCycleUnit != gDLL->UI().getHeadSelectedUnit() ||
		(pCycleUnit != NULL && pCycleUnit->getGroup()->readyToSelect(
		true))) // advc.153: was false
	{
		gDLL->UI().lookAtSelectionPlot();
	}
}

// K-Mod:
void CvGame::cycleSelectionGroups_delayed(int iDelay, bool bIncremental, bool bDelayOnly)
{
	PROFILE_FUNC(); // just hoping that the python call doesn't hurt the respose times

	if (GC.suppressCycling()) // cf. GvGame::updateSelectionList
		return;
	/*	Only rapid-cycle when not doing auto-play. Also note,
		cycleSelectionGroups currently causes a crash if the game is not initialised.
		(and this function is indirectly called during the set of up a new game -
		so we currently need that init check.) */
	PlayerTypes const eActive = getActivePlayer();
	if (isFinalInitialized() &&
		eActive != NO_PLAYER && GET_PLAYER(eActive).isHuman() &&
		BUGOption::isEnabled("MainInterface__RapidUnitCycling", false))
	{
		if (!bDelayOnly)
		{
			// (for the non-rapid case, this option is handled elsewhere.)
			if (GET_PLAYER(eActive).isOption(PLAYEROPTION_NO_UNIT_CYCLING))
				return;

			if (gDLL->getEngineIFace()->isCameraLocked())
			{	// immediate cycling might violate the camera lock. :(
				gDLL->UI().setCycleSelectionCounter(1);
			}
			else cycleSelectionGroups(true);
		}
	}
	else
	{
		if (bIncremental)
			gDLL->UI().changeCycleSelectionCounter(iDelay);
		else gDLL->UI().setCycleSelectionCounter(iDelay);
	}
}

// Returns true if unit was cycled...
bool CvGame::cyclePlotUnits(CvPlot* pPlot, bool bForward, bool bAuto, int iCount) const
{
	FAssert(iCount >= -1);

	CvUnit const* pUnit = NULL;
	CLLNode<IDInfo> const* pUnitNode = NULL;
	if (iCount == -1)
	{
		for (pUnitNode = pPlot->headUnitNode(); pUnitNode != NULL;
			pUnitNode = pPlot->nextUnitNode(pUnitNode))
		{
			pUnit = ::getUnit(pUnitNode->m_data);
			if (pUnit->IsSelected())
				break;
		}
	}
	else
	{
		for (pUnitNode = pPlot->headUnitNode(); pUnitNode != NULL;
			pUnitNode = pPlot->nextUnitNode(pUnitNode))
		{
			pUnit = ::getUnit(pUnitNode->m_data);
			if (iCount - 1 == 0)
				break;
			if (iCount > 0)
				iCount--;
		}
		if (pUnitNode == NULL)
		{
			pUnitNode = pPlot->tailUnitNode();
			if (pUnitNode != NULL)
				pUnit = ::getUnit(pUnitNode->m_data);
		}
	}
	if (pUnitNode == NULL)
		return false;

	CvUnit const* pSelectedUnit = pUnit;
	while (true)
	{
		if (bForward)
		{
			pUnitNode = pPlot->nextUnitNode(pUnitNode);
			if (pUnitNode == NULL)
				pUnitNode = pPlot->headUnitNode();
		}
		else
		{
			pUnitNode = pPlot->prevUnitNode(pUnitNode);
			if (pUnitNode == NULL)
				pUnitNode = pPlot->tailUnitNode();
		}
		CvUnit* pLoopUnit = ::getUnit(pUnitNode->m_data);
		if (iCount == -1)
		{
			if (pLoopUnit == pSelectedUnit)
				break;
		}
		if (pLoopUnit->getOwner() == getActivePlayer())
		{
			if (bAuto)
			{
				if (pLoopUnit->getGroup()->readyToSelect(/* advc.153: */ true))
				{
					gDLL->UI().selectUnit(pLoopUnit, true);
					return true;
				}
			}
			else
			{
				gDLL->UI().insertIntoSelectionList(pLoopUnit, true, false);
				return true;
			}
		}
		if (pLoopUnit == pSelectedUnit)
			break;
	}

	return false;
}


bool CvGame::selectCity(CvCity* pSelectCity, bool bCtrl, bool bAlt, bool bShift) const
{
	if (pSelectCity == NULL || !pSelectCity->canBeSelected())
		return false;
	if (!bShift)
		gDLL->UI().clearSelectedCities();
	if (bAlt)
	{
		FOR_EACH_CITY_VAR(pLoopCity, GET_PLAYER(pSelectCity->getOwner()))
			gDLL->UI().addSelectedCity(pLoopCity);
	}
	else if (bCtrl)
	{
		FOR_EACH_CITY_VAR(pLoopCity, GET_PLAYER(pSelectCity->getOwner()))
		{
			if (pLoopCity->sameArea(*pSelectCity))
				gDLL->UI().addSelectedCity(pLoopCity);
		}
	}
	else gDLL->UI().addSelectedCity(pSelectCity, bShift);
	return true;
}


void CvGame::selectionListMove(CvPlot* pPlot, bool bAlt, bool bShift, bool bCtrl) const
{
	if (pPlot == NULL)
		return;
	if (GC.getPythonCaller()->cannotSelectionListMoveOverride(*pPlot, bAlt, bShift, bCtrl))
		return;
	CvUnit* pHeadSelectedUnit = gDLL->UI().getHeadSelectedUnit();
	if (pHeadSelectedUnit == NULL || pHeadSelectedUnit->getOwner() != getActivePlayer())
		return;
	if (bAlt)
	{
		//gDLL->UI().selectGroup(pHeadSelectedUnit, false, false, true);
		gDLL->UI().selectGroup(pHeadSelectedUnit, false, true, true); // K-Mod
	}
	else if (bCtrl)
		gDLL->UI().selectGroup(pHeadSelectedUnit, false, true, false);
	/* bts code
	pSelectedUnitNode = gDLL->UI().headSelectionListNode();
	while (pSelectedUnitNode != NULL)
	{
		// advc: Rest deleted
		pSelectedUnitNode = gDLL->UI().nextSelectionListNode(pSelectedUnitNode);
	} */ // K-Mod has moved this to selectionListGameNetMessage.
	selectionListGameNetMessage(GAMEMESSAGE_PUSH_MISSION, MISSION_MOVE_TO,
			pPlot->getX(), pPlot->getY(), 0, false, bShift);
}


void CvGame::selectionListGameNetMessage(int eMessage, int iData2, int iData3, int iData4, int iFlags, bool bAlt, bool bShift) const
{
	int aiPyData[] = { iData2, iData3, iData4 };
	if (GC.getPythonCaller()->cannotSelectionListNetOverride((GameMessageTypes)
		eMessage, aiPyData, iFlags, bAlt, bShift))
	{
		return;
	}
	CvUnit* pHeadSelectedUnit = gDLL->UI().getHeadSelectedUnit();
	if (pHeadSelectedUnit == NULL || pHeadSelectedUnit->getOwner() != getActivePlayer())
		return; // advc

	CLLNode<IDInfo>* pSelectedUnitNode;
	CvUnit const* pSelectedUnit;
	if (eMessage == GAMEMESSAGE_JOIN_GROUP)
	{
		pSelectedUnitNode = gDLL->UI().headSelectionListNode();
		while (pSelectedUnitNode != NULL)
		{
			pSelectedUnit = ::getUnit(pSelectedUnitNode->m_data);
			pSelectedUnitNode = gDLL->UI().nextSelectionListNode(pSelectedUnitNode);
			if (bShift)
			{
				CvMessageControl::getInstance().sendJoinGroup(pSelectedUnit->getID(),
						FFreeList::INVALID_INDEX);
			}
			else
			{
				if (pSelectedUnit == pHeadSelectedUnit)
				{
					CvMessageControl::getInstance().sendJoinGroup(pSelectedUnit->getID(),
							FFreeList::INVALID_INDEX);
				}
				else // K-Mod
				{
					CvMessageControl::getInstance().sendJoinGroup(pSelectedUnit->getID(),
							pHeadSelectedUnit->getID());
				}
			}
		}
		if (bShift)
			gDLL->UI().selectUnit(pHeadSelectedUnit, true);
	}
	else if (eMessage == GAMEMESSAGE_DO_COMMAND)
	{	// K-Mod. When setting a unit to automate, we must be careful not to keep it grouped
		if (iData2 == COMMAND_AUTOMATE && !gDLL->UI().mirrorsSelectionGroup())
			selectionListGameNetMessage(GAMEMESSAGE_JOIN_GROUP);
		// K-Mod end
		pSelectedUnitNode = gDLL->UI().headSelectionListNode();
		while (pSelectedUnitNode != NULL)
		{
			pSelectedUnit = ::getUnit(pSelectedUnitNode->m_data);
			pSelectedUnitNode = gDLL->UI().nextSelectionListNode(pSelectedUnitNode);
			CvMessageControl::getInstance().sendDoCommand(pSelectedUnit->getID(),
					(CommandTypes)iData2, iData3, iData4, bAlt);
		}
	}
	else if (eMessage == GAMEMESSAGE_PUSH_MISSION || eMessage == GAMEMESSAGE_AUTO_MISSION)
	{
		if (!gDLL->UI().mirrorsSelectionGroup())
			selectionListGameNetMessage(GAMEMESSAGE_JOIN_GROUP);

		MovementFlags eFlags = (MovementFlags)iFlags;
		if (eMessage == GAMEMESSAGE_PUSH_MISSION)
		{	/*	K-Mod. I've moved the BUTTONPOPUP_DECLAREWARMOVE stuff to here
				from selectionListMove so that it can catch left-click moves
				as well as right-click moves.
				Note: If MOVE_DECLARE_WAR is set, then we assume it was set
				by a BUTTONPOPUP_DECLAREWARMOVE which was triggered already
				by this move. In which case we shouldn't check for declare war
				this time. This is a kludge to prevent the popup from appearing twice.
				Also, when this happens we should clear the MOVE_DECLARE_WAR flag.
				Otherwise it may cause the pathfinder to fail in some cases.
				(I'd rather not have UI stuff like this in this function,
				but this is the only place where I can catch left-click moves.) */
			if (iData2 == MISSION_MOVE_TO && !(eFlags & MOVE_DECLARE_WAR))
			{
				CvPlot* pPlot = GC.getMap().plot(iData3, iData4);
				FAssert(pPlot != NULL);
				pSelectedUnitNode = gDLL->UI().headSelectionListNode();
				while (pSelectedUnitNode != NULL)
				{
					pSelectedUnit = ::getUnit(pSelectedUnitNode->m_data);
					TeamTypes eRivalTeam = pSelectedUnit->getDeclareWarMove(pPlot);
					if (eRivalTeam != NO_TEAM)
					{	/* <advc.001> If an enemy unit is stacked with a neutral one,
							then the player apparently wants to attack the enemy unit
							(rather than declare war on the neutral party). However,
							if the enemy unit is on a tile owned by a third party that
							the player doesn't have OB or a vassal treaty with, then
							only a DoW on the third party makes sense. */
						if ((pPlot->getTeam() != NO_TEAM &&
							!GET_TEAM(pSelectedUnit->getTeam()).
							isFriendlyTerritory(pPlot->getTeam())) ||
							!pPlot->isVisibleEnemyUnit(pSelectedUnit))
						{ // </advc.001>
							CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_DECLAREWARMOVE);
							if (pInfo != NULL)
							{
								pInfo->setData1(eRivalTeam);
								pInfo->setData2(pPlot->getX());
								pInfo->setData3(pPlot->getY());
								pInfo->setOption1(bShift);
								pInfo->setOption2(pPlot->getTeam() != eRivalTeam);
								gDLL->UI().addPopup(pInfo);
							}
							return;
						}
					}
					// <advc.653> Disallow nuke attack through right-click
					if (pSelectedUnit->isNuke() &&
						gDLL->UI().getInterfaceMode() != INTERFACEMODE_NUKE &&
						!pSelectedUnit->canMoveInto(*pPlot))
					{
						return;
					} // </advc.653>
					pSelectedUnitNode = gDLL->UI().nextSelectionListNode(pSelectedUnitNode);
				}
			} // <advc.011b>
			bool bModified = false;
			if (iData2 == MISSION_BUILD ||
				iData2 == MISSION_PILLAGE || iData2 == MISSION_AIRBOMB) // advc.111
			{
				bModified = GC.ctrlKey();
			} // </advc.011b>
			// <advc.048>
			if (iData2 == MISSION_MOVE_TO)
				bModified = GC.altKey(); // </advc.048>
			CvMessageControl::getInstance().sendPushMission(pHeadSelectedUnit->getID(),
					(MissionTypes)iData2, iData3, iData4,
					eFlags & ~ MOVE_DECLARE_WAR, bShift, // K-Mod end
					bModified); // advc.011b
		}
		else CvMessageControl::getInstance().sendAutoMission(pHeadSelectedUnit->getID());
	}
	else FAssert(false);
}


void CvGame::selectedCitiesGameNetMessage(int eMessage, int iData2, int iData3, int iData4, bool bOption, bool bAlt, bool bShift, bool bCtrl) const
{
	for (CLLNode<IDInfo> const* pSelectedCityNode = gDLL->UI().headSelectedCitiesNode();
		pSelectedCityNode != NULL;
		pSelectedCityNode = gDLL->UI().nextSelectedCitiesNode(pSelectedCityNode))
	{
		CvCity* pSelectedCity = ::getCity(pSelectedCityNode->m_data);
		if (pSelectedCity == NULL || pSelectedCity->getOwner() != getActivePlayer())
			continue;
		switch (eMessage)
		{
		case GAMEMESSAGE_PUSH_ORDER:
			cityPushOrder(pSelectedCity, (OrderTypes)iData2, iData3, bAlt, bShift, bCtrl);
			break;
		case GAMEMESSAGE_POP_ORDER:
			/*if (pSelectedCity->getOrderQueueLength() > 1)
				CvMessageControl::getInstance().sendPopOrder(pSelectedCity->getID(), iData2);
			*/ // BtS
			// K-Mod. Some additional controls
			if (bAlt || (bShift != bCtrl))
			{
				// bCtrl moves the order up, bShift moves the order down.
				// bAlt toggles bSave (ie. repeat)
				int iNewPos = iData2 + (bShift ? 1 : 0) + (bCtrl ? -1 : 0);
				if (pSelectedCity->getOrderQueueLength() > iNewPos && iNewPos >= 0)
				{
					OrderData order = pSelectedCity->getOrderData(iData2);
					if (order.eOrderType != NO_ORDER &&
						(bShift || bCtrl || order.eOrderType == ORDER_TRAIN))
					{
						order.bSave = order.bSave != (bAlt && order.eOrderType == ORDER_TRAIN);
						CvMessageControl::getInstance().sendPopOrder(
								pSelectedCity->getID(), iData2);
						CvMessageControl::getInstance().sendPushOrder(
								pSelectedCity->getID(), order.eOrderType,
								order.iData1, order.bSave, false, iNewPos);
					}
				}
			}
			/*	Allow us to cancel the final order for automated cities.
				(The governor can choose production at the end of the turn.) */
			else if (pSelectedCity->getOrderQueueLength() > 1 ||
				pSelectedCity->isProductionAutomated())
			{
				CvMessageControl::getInstance().sendPopOrder(pSelectedCity->getID(), iData2);
			} // K-Mod end
			break;
		case GAMEMESSAGE_DO_TASK:
			CvMessageControl::getInstance().sendDoTask(pSelectedCity->getID(),
					(TaskTypes)iData2, iData3, iData4, bOption, bAlt, bShift, bCtrl);
			break;
		default:
			FAssert(false);
		}
	}
}


bool CvGame::canHandleAction(int iAction, CvPlot* pPlot, bool bTestVisible, bool bUseCache) const
{
	PROFILE_FUNC();

	// <!-- custom: Retired KI#107's isFinalInitialized guard, restoring base AdvCiv 1.14: a crash fix made without a matching PDB, so a recurrence should be traced with a Debug-opt dump. See KI#107 and KI#136. (Claude code Opus 4.6 + Claude code Opus 5.5) -->
	bool const bShift = GC.shiftKey();

	if (GC.getPythonCaller()->cannotHandleActionOverride(pPlot, iAction, bTestVisible))
		return false;

	CvActionInfo const& kAction = GC.getActionInfo(iAction);
	if (kAction.getControlType() != NO_CONTROL &&
		canDoControl((ControlTypes)kAction.getControlType()))
	{
		return true;
	}
	if (gDLL->UI().isCitySelection())
		return false; // XXX hack!
	CvUnit* pHeadSelectedUnit = gDLL->UI().getHeadSelectedUnit();
	if (pHeadSelectedUnit == NULL || pHeadSelectedUnit->getOwner() != getActivePlayer())
		return false;
	if (!isMPOption(MPOPTION_SIMULTANEOUS_TURNS) &&
		!GET_PLAYER(pHeadSelectedUnit->getOwner()).isTurnActive())
	{
		return false;
	}
	CvSelectionGroup* pSelectedInterfaceList = gDLL->UI().getSelectionList();
	if (kAction.getMissionType() != NO_MISSION)
	{
		CvPlot* pMissionPlot = NULL;
		if (gDLL->UI().mirrorsSelectionGroup())
		{
			CvSelectionGroup* pSelectedGroup = pHeadSelectedUnit->getGroup();
			if (pPlot != NULL)
				pMissionPlot = pPlot;
			else if (bShift)
				pMissionPlot = pSelectedGroup->lastMissionPlot();
			else pMissionPlot = NULL;
			if (pMissionPlot == NULL ||
				!pMissionPlot->isVisible(pHeadSelectedUnit->getTeam()))
			{
				pMissionPlot = pSelectedGroup->plot();
			}
		}
		else pMissionPlot = pSelectedInterfaceList->plot();
		if (pSelectedInterfaceList->canStartMission((MissionTypes)kAction.getMissionType(),
			kAction.getMissionData(), -1, pMissionPlot, bTestVisible, bUseCache))
		{
			return true;
		}
	}
	if (kAction.getCommandType() != NO_COMMAND)
	{
		if (pSelectedInterfaceList->canDoCommand((CommandTypes)
			kAction.getCommandType(),
			kAction.getCommandData(), -1, bTestVisible, bUseCache))
		{
			return true;
		}
	}
	if (gDLL->UI().canDoInterfaceMode((InterfaceModeTypes)
		kAction.getInterfaceModeType(), pSelectedInterfaceList))
	{
		return true;
	}
	return false;
}


void CvGame::setupActionCache() const
{
	// <!-- custom: Retired KI#100's null-selection guards here and in this file's action handling, restoring base AdvCiv 1.14: a crash fix made without a matching PDB, so a recurrence should be traced with a Debug-opt dump. See KI#100 and KI#136. (Claude code Opus 4.5 + GPT-5.2-Codex + Claude code Opus 5.5) -->
	gDLL->UI().getSelectionList()->setupActionCache();
}


void CvGame::handleAction(int iAction)
{
	// <!-- custom: Retired KI#107's isFinalInitialized guard, restoring base AdvCiv 1.14: a crash fix made without a matching PDB, so a recurrence should be traced with a Debug-opt dump. See KI#107 and KI#136. (Claude code Opus 4.6 + Claude code Opus 5.5) -->
	bool const bAlt = GC.altKey();
	bool const bShift = GC.shiftKey();

	if (!gDLL->UI().canHandleAction(iAction))
		return;
	CvActionInfo const& kAction = GC.getActionInfo(iAction);
	if (kAction.getControlType() != NO_CONTROL)
		doControl((ControlTypes)kAction.getControlType());
	if (gDLL->UI().canDoInterfaceMode((InterfaceModeTypes)kAction.getInterfaceModeType(),
		gDLL->UI().getSelectionList()))
	{
		CvUnit* pHeadSelectedUnit = gDLL->UI().getHeadSelectedUnit();
		if (pHeadSelectedUnit != NULL)
		{
			if (GC.getInfo((InterfaceModeTypes)
				kAction.getInterfaceModeType()).getSelectAll())
			{
				//gDLL->UI().selectGroup(pHeadSelectedUnit, false, false, true);
				gDLL->UI().selectGroup(pHeadSelectedUnit, false, true, true); // K-Mod
			}
			else if (GC.getInfo((InterfaceModeTypes)
				kAction.getInterfaceModeType()).getSelectType())
			{
				gDLL->UI().selectGroup(pHeadSelectedUnit, false, true, false);
			}
		}

		gDLL->UI().setInterfaceMode((InterfaceModeTypes)
				kAction.getInterfaceModeType());
	}
	if (kAction.getMissionType() != NO_MISSION)
	{
		selectionListGameNetMessage(GAMEMESSAGE_PUSH_MISSION, kAction.getMissionType(),
				kAction.getMissionData(), -1, 0, false, bShift);
	}
	if (kAction.getCommandType() != NO_COMMAND)
	{
		bool bSkip = false;

		if (kAction.getCommandType() == COMMAND_LOAD)
		{
			CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_LOADUNIT);
			if (NULL != pInfo)
			{
				gDLL->UI().addPopup(pInfo);
				bSkip = true;
			}
		}
		if (!bSkip)
		{
			if (kAction.isConfirmCommand())
			{
				CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_CONFIRMCOMMAND);
				if (NULL != pInfo)
				{
					pInfo->setData1(iAction);
					pInfo->setOption1(bAlt);
					gDLL->UI().addPopup(pInfo);
				}
			}
			else
			{
				selectionListGameNetMessage(GAMEMESSAGE_DO_COMMAND,
						kAction.getCommandType(),
						kAction.getCommandData(), -1, 0, bAlt);
			}
		}
	}
}


bool CvGame::canDoControl(ControlTypes eControl) const
{
	if (GC.getPythonCaller()->cannotDoControlOverride(eControl))
		return false;

	/*  <advc.706> I don't think loading is possible in between turns, but there
		would be no harm in it. */
	if (CvPlot::isAllFog() && eControl != CONTROL_LOAD_GAME &&
		eControl != CONTROL_QUICK_LOAD && eControl != CONTROL_OPTIONS_SCREEN)
	{
		return false;
	} // </advc.706>
	switch (eControl)
	{
	case CONTROL_SELECTYUNITTYPE:
	case CONTROL_SELECTYUNITALL:
	case CONTROL_SELECT_HEALTHY:
	case CONTROL_SELECTCITY:
	case CONTROL_SELECTCAPITAL:
	case CONTROL_NEXTUNIT:
	case CONTROL_PREVUNIT:
	case CONTROL_CYCLEUNIT:
	case CONTROL_CYCLEUNIT_ALT:
	case CONTROL_CYCLEWORKER:
	case CONTROL_LASTUNIT:
	case CONTROL_AUTOMOVES:
	case CONTROL_SAVE_GROUP:
	case CONTROL_QUICK_SAVE:
	case CONTROL_QUICK_LOAD:
	case CONTROL_ORTHO_CAMERA:
	case CONTROL_CYCLE_CAMERA_FLYING_MODES:
	case CONTROL_ISOMETRIC_CAMERA_LEFT:
	case CONTROL_ISOMETRIC_CAMERA_RIGHT:
	case CONTROL_FLYING_CAMERA:
	case CONTROL_MOUSE_FLYING_CAMERA:
	case CONTROL_TOP_DOWN_CAMERA:
	case CONTROL_TURN_LOG:
	case CONTROL_CHAT_ALL:
	case CONTROL_CHAT_TEAM:
	case CONTROL_GLOBE_VIEW:
		if (!gDLL->UI().isFocused())
			return true;
		break;

	case CONTROL_FORCEENDTURN:
		if (!gDLL->UI().isFocused() && !gDLL->UI().isInAdvancedStart())
			return true;
		break;

	case CONTROL_PING:
	case CONTROL_SIGN:
	case CONTROL_GRID:
	case CONTROL_BARE_MAP:
	case CONTROL_YIELDS:
	case CONTROL_RESOURCE_ALL:
	case CONTROL_UNIT_ICONS:
	case CONTROL_GLOBELAYER:
	case CONTROL_SCORES:
	case CONTROL_FREE_COLONY:
		if (!gDLL->UI().isFocusedWidget())
			return true;
		break;

	case CONTROL_OPTIONS_SCREEN:
	case CONTROL_DOMESTIC_SCREEN:
	case CONTROL_VICTORY_SCREEN:
	case CONTROL_CIVILOPEDIA:
	// <!-- custom: CONTROL_RELIGION_SCREEN / CONTROL_CORPORATION_SCREEN removed; those screens are planned as Civics tabs. (GPT-5.3-Codex) -->
	case CONTROL_CIVICS_SCREEN:
	case CONTROL_FOREIGN_SCREEN:
	case CONTROL_FOREIGN_DIPLOMACY_SCREEN:
	case CONTROL_MILITARY_SCREEN:
	case CONTROL_TECH_CHOOSER:
	// <!-- custom: F7 is available after Religion/Corporation were integrated into Policy Advisor. (GPT-5.5) -->
	case CONTROL_WORLD_ADVISOR_SCREEN:
	case CONTROL_DIPLOMACY:
	case CONTROL_HALL_OF_FAME:
	case CONTROL_INFO:
	case CONTROL_DETAILS:
	case CONTROL_SAVE_NORMAL:
		return true;

	case CONTROL_ESPIONAGE_SCREEN:
		if (!isOption(GAMEOPTION_NO_ESPIONAGE))
			return true;
		break;

	case CONTROL_NEXTCITY:
	case CONTROL_PREVCITY:
		if (!gDLL->UI().isSpaceshipScreenUp())
			return true;
		break;

	case CONTROL_ADMIN_DETAILS:
		return true;

	case CONTROL_CENTERONSELECTION:
		if (gDLL->UI().getLookAtPlot() != gDLL->UI().getSelectionPlot())
			return true;
		break;

	case CONTROL_LOAD_GAME:
		if (!isNetworkMultiPlayer())
			return true;
		break;

	case CONTROL_RETIRE:
		if (getGameState() == GAMESTATE_ON || isGameMultiPlayer())
		{
			if (GET_PLAYER(getActivePlayer()).isAlive())
			{
				if (isPbem() || isHotSeat())
				{
					if (!GET_PLAYER(getActivePlayer()).isEndTurn())
						return true;
				}
				else return true;
			}
		}
		break;

	case CONTROL_WORLD_BUILDER:
		return isDebugToolsAllowed(true); // advc.135c
		/*if (!(isGameMultiPlayer()) && GC.getInitCore().getAdminPassword().empty() && !gDLL->UI().isInAdvancedStart())
			return true;*/
		break;

	case CONTROL_ENDTURN:
	case CONTROL_ENDTURN_ALT:
		if (gDLL->UI().isEndTurnMessage() &&
			!gDLL->UI().isFocused() &&
			!gDLL->UI().isInAdvancedStart())
		{
			return true;
		}
		break;
	// <advc.088>
	case CONTROL_UNSELECT_ALL:
		if (gDLL->UI().getInterfaceMode() == INTERFACEMODE_SELECTION &&
			!gDLL->UI().isCityScreenUp() && gDLL->UI().getHeadSelectedUnit() != NULL)
		{
			return true;
		}
		break; // </advc.088>

	default:
		FErrorMsg("eControl did not match any valid options");
	}

	return false;
}


void CvGame::doControl(ControlTypes eControl)
{
	// <!-- custom: Share one level/initialization snapshot within this control invocation; revision-150 runtime-view state stays available even when the revision-151+ action trace is independently disabled.
	// The action switch is read only after the level-2 gate succeeds, while level 0 avoids both the lifecycle query and supporting-switch read. (GPT-6.1-Sol + ChatGPT-5.6-Sol) -->
	bool const bLogSASRuntimeView = (gGameRecordLogLevel >= 2 && isFinalInitialized());
	bool const bLogSASControl = (bLogSASRuntimeView && isSASGameRecordActionTraceEnabled());
	if (!canDoControl(eControl))
	{
		// <!-- custom: The first draft lost requests rejected before the switch; the initial fix covered only turn controls.
		// Use the same recorder-owned vocabulary for every traced rejected/accepted control, so save/load/camera rejections cannot silently disappear. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, false);
		return;
	}
	// <advc>
	CvDLLInterfaceIFaceBase& kUI = gDLL->UI();
	CvDLLEngineIFaceBase& kEngine = *gDLL->getEngineIFace();
	// <!-- custom: Check the cached level before the live initialization state so disabled controls do no logging-only lifecycle queries; individual state getters below are sampled only at level 2+ after initialization, except Grid whose old value is already needed to toggle it. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
	CvUnit* pHeadSelectedUnit = kUI.getHeadSelectedUnit();
	CvPlot* pSelectionPlot = kUI.getSelectionPlot();
	// </advc>
	switch (eControl)
	{
	case CONTROL_CENTERONSELECTION:
		kUI.lookAtSelectionPlot();
		break;

	case CONTROL_SELECTYUNITTYPE:
		if (pHeadSelectedUnit != NULL)
			kUI.selectGroup(pHeadSelectedUnit, false, true, false);
		break;

	case CONTROL_SELECTYUNITALL:
		if (pHeadSelectedUnit != NULL)
		{
			kUI.selectGroup(pHeadSelectedUnit, false,
					/*false, true*/ true, true); // K-Mod
		}
		break;

	case CONTROL_SELECT_HEALTHY:  // advc: Refactored this case
		if (pHeadSelectedUnit != NULL)
		{
			/*  <advc.001z> Compute the units to be selected upfront b/c, if there
				are none, then the current selection shouldn't be cleared. */
			std::vector<CvUnit*> toBeSelected;
			std::vector<CvUnit*> plotUnits;
			getPlotUnits(pHeadSelectedUnit->plot(), plotUnits);
			for (size_t i = 0; i < plotUnits.size(); i++)
			{
				CvUnit& kUnit = *plotUnits[i];
				// disabled by K-Mod
				//if (!isMPOption(MPOPTION_SIMULTANEOUS_TURNS) || getTurnSlice() - kUnit.getLastMoveTurn() > GC.getDefineINT("MIN_TIMER_UNIT_DOUBLE_MOVES")) {
				if (kUnit.getOwner() == getActivePlayer() && kUnit.isHurt() &&
					// advc.001z: Can't select units of different domains
					kUnit.getDomainType() == pHeadSelectedUnit->getDomainType())
				{
					toBeSelected.push_back(&kUnit);
				}
			}
			if (!toBeSelected.empty()) // advc.001z
			{
				kUI.clearSelectionList();
				kUI.selectionListPreChange();
				CvUnit const* pGroupHead = NULL;
				for (size_t i = 0; i < toBeSelected.size(); i++) // advc.001z
				{
					CvUnit* pUnit = toBeSelected[i]; // advc.001z
					if (pGroupHead != NULL)
					{
						CvMessageControl::getInstance().sendJoinGroup(
								pUnit->getID(), pGroupHead->getID());
					}
					else pGroupHead = pUnit;
					kUI.insertIntoSelectionList(pUnit, false, false, true, true, true);
				}
				kUI.selectionListPostChange();
			}
		}
		break;

	case CONTROL_SELECTCITY:
		if (kUI.isCityScreenUp())
			cycleCities();
		else kUI.selectLookAtCity();
		break;

	case CONTROL_SELECTCAPITAL:
	{
		CvCity* pCapital = GET_PLAYER(getActivePlayer()).getCapital();
		if (pCapital != NULL)
			kUI.selectCity(pCapital);
		break;
	}
	case CONTROL_NEXTCITY:
		if (kUI.isCitySelection())
			cycleCities(true, !kUI.isCityScreenUp());
		else kUI.selectLookAtCity(true);
		kUI.lookAtSelectionPlot();
		break;

	case CONTROL_PREVCITY:
		if (kUI.isCitySelection())
			cycleCities(false, !kUI.isCityScreenUp());
		else kUI.selectLookAtCity(true);
		kUI.lookAtSelectionPlot();
		break;

	case CONTROL_NEXTUNIT:
		if (pSelectionPlot != NULL)
			cyclePlotUnits(pSelectionPlot);
		break;

	case CONTROL_PREVUNIT:
		if (pSelectionPlot != NULL)
			cyclePlotUnits(pSelectionPlot, false);
		break;

	case CONTROL_CYCLEUNIT:
	case CONTROL_CYCLEUNIT_ALT:
		cycleSelectionGroups(true);
		break;

	case CONTROL_CYCLEWORKER:
		cycleSelectionGroups(true, true, true);
		break;

	case CONTROL_LASTUNIT:
	{
		CvUnit* pUnit = kUI.getLastSelectedUnit();
		if (pUnit != NULL)
		{
			kUI.selectUnit(pUnit, true);
			kUI.lookAtSelectionPlot();
		}
		else cycleSelectionGroups(true, false);

		kUI.setLastSelectedUnit(NULL);
		break;
	}
	// <!-- custom: Revision 151 logs a small causal control vocabulary before its consequence; `accepted` means this handler passed its immediate gate, not that a later save/load/turn operation necessarily completed.
	// Keep these hooks level-2 pre-gated and separate from existing resulting-state rows. (ChatGPT-5.6-Sol) -->
	case CONTROL_ENDTURN:
	case CONTROL_ENDTURN_ALT:
	{
		bool const bAccepted = kUI.isEndTurnMessage();
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, bAccepted);
		if (bAccepted)
		{
			if (isSASRuntimeStatusEnabled())
			{
				PlayerTypes const ePlayer = getActivePlayer();
				bool const bSelectedUnit = (kUI.getHeadSelectedUnit() != NULL);
				bool const bUIAnyMove = (bSelectedUnit && !GET_PLAYER(ePlayer).isOption(PLAYEROPTION_NO_UNIT_CYCLING));
				// <!-- custom: Capture the accepted request before sendTurnComplete can deactivate the player.
				// The control enum is authoritative; do not infer Enter versus end-turn-widget origin. (ChatGPT-5.6-Sol) -->
				updateSASRuntimeStatusEndTurnRequest(ePlayer, eControl, kUI.isEndTurnMessage(), bUIAnyMove, bSelectedUnit, kUI.isForcePopup(), kUI.isHasMovedUnit(), GET_PLAYER(ePlayer).isOption(PLAYEROPTION_WAIT_END_TURN));
			}
			CvMessageControl::getInstance().sendTurnComplete();
		}
		break;
	}

	case CONTROL_FORCEENDTURN:
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		if (isSASRuntimeStatusEnabled())
		{
			PlayerTypes const ePlayer = getActivePlayer();
			bool const bSelectedUnit = (kUI.getHeadSelectedUnit() != NULL);
			bool const bUIAnyMove = (bSelectedUnit && !GET_PLAYER(ePlayer).isOption(PLAYEROPTION_NO_UNIT_CYCLING));
			updateSASRuntimeStatusEndTurnRequest(ePlayer, eControl, kUI.isEndTurnMessage(), bUIAnyMove, bSelectedUnit, kUI.isForcePopup(), kUI.isHasMovedUnit(), GET_PLAYER(ePlayer).isOption(PLAYEROPTION_WAIT_END_TURN));
		}
		CvMessageControl::getInstance().sendTurnComplete();
		break;

	case CONTROL_AUTOMOVES:
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		CvMessageControl::getInstance().sendAutoMoves();
		break;

	case CONTROL_PING:
		kUI.setInterfaceMode(INTERFACEMODE_PING);
		break;

	case CONTROL_SIGN:
		kUI.setInterfaceMode(INTERFACEMODE_SIGN);
		break;

	// <!-- custom: These controls have cheap authoritative getters immediately after the native toggle.
	// Record only real state changes at level 2+; resource/unit layers are resolved separately by CvGame::reportCurrentLayer. (ChatGPT-5.6-Sol) -->
	case CONTROL_GRID:
	{
		bool const bOldValue = kEngine.GetGridMode();
		kEngine.SetGridMode(!bOldValue);
		if (bLogSASRuntimeView) logSASGameRecordRuntimeViewBoolChange("CONTROL_GRID", "grid", bOldValue, kEngine.GetGridMode());
		break;
	}

	case CONTROL_BARE_MAP:
	{
		bool bOldValue = false;
		if (bLogSASRuntimeView) bOldValue = kUI.isBareMapMode();
		kUI.toggleBareMapMode();
		if (bLogSASRuntimeView) logSASGameRecordRuntimeViewBoolChange("CONTROL_BARE_MAP", "bareMap", bOldValue, kUI.isBareMapMode());
		break;
	}

	case CONTROL_YIELDS:
	{
		bool bOldValue = false;
		if (bLogSASRuntimeView) bOldValue = kUI.isShowYields();
		kUI.toggleYieldVisibleMode();
		if (bLogSASRuntimeView) logSASGameRecordRuntimeViewBoolChange("CONTROL_YIELDS", "yields", bOldValue, kUI.isShowYields());
		break;
	}

	case CONTROL_RESOURCE_ALL:
		kEngine.toggleResourceLayer();
		break;

	case CONTROL_UNIT_ICONS:
		kEngine.toggleUnitLayer();
		break;

	case CONTROL_GLOBELAYER:
	{
		bool bOldValue = false;
		if (bLogSASRuntimeView) bOldValue = kEngine.isGlobeviewUp();
		kEngine.toggleGlobeview();
		if (bLogSASRuntimeView) logSASGameRecordRuntimeViewBoolChange("CONTROL_GLOBELAYER", "globeView", bOldValue, kEngine.isGlobeviewUp());
		break;
	}

	case CONTROL_SCORES:
	{
		bool bOldValue = false;
		if (bLogSASRuntimeView) bOldValue = kUI.isScoresVisible();
		kUI.toggleScoresVisible();
		if (bLogSASRuntimeView) logSASGameRecordRuntimeViewBoolChange("CONTROL_SCORES", "scores", bOldValue, kUI.isScoresVisible());
		break;
	}

	case CONTROL_LOAD_GAME:
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		gDLL->LoadGame();
		break;

	case CONTROL_OPTIONS_SCREEN:
		GC.getPythonCaller()->showPythonScreen("OptionsScreen");
		break;

	case CONTROL_RETIRE: // <advc.706> Need three buttons, so no BUTTONPOPUP_CONFIRM_MENU.
		if (isOption(GAMEOPTION_RISE_FALL))
		{
			CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_RF_RETIRE);
			if (pInfo != NULL)
				kUI.addPopup(pInfo, getActivePlayer(), true);
		}
		else // </advc.706>
		// K-Mod. (original code moved into CvGame::retire)
		{
			CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_CONFIRM_MENU);
			if (pInfo != NULL)
			{
				// <!-- custom: Share the confirmation action ID with popup dispatch and its diagnostics while preserving the inherited payload value. (GPT-6.1-Sol) -->
				pInfo->setData1(SAS_POPUP_CONFIRM_RETIRE);
				kUI.addPopup(pInfo, getActivePlayer(), true);
			}
		} // K-Mod end
		break;

	case CONTROL_SAVE_GROUP:
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		gDLL->SaveGame(SAVEGAME_GROUP);
		break;

	case CONTROL_SAVE_NORMAL:
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		gDLL->SaveGame(SAVEGAME_NORMAL);
		break;

	case CONTROL_QUICK_SAVE:
	{
		bool const bAccepted = !isNetworkMultiPlayer(); // SP only!
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, bAccepted);
		if (bAccepted)
		{
			CvEventReporter::getInstance().preQuickSave(); // advc.106l
			gDLL->QuickSave();
		}
		break;
	}

	case CONTROL_QUICK_LOAD:
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, !isNetworkMultiPlayer());
		if (isNetworkMultiPlayer()) // SP only!
			break;
		// <advc.003d>
		/*  Loading works fine in windowed mode, and when a debugger is
			attached, exitingToMainMenu can actually be quite slow.
			(Fullscreen pretty much rules out that a debugger is attached.) */
		if (gDLL->getGraphicOption(GRAPHICOPTION_FULLSCREEN))
		{
			/*  On my system, it's "C:\\Users\\Administrator\\Documents\\My Games\\Beyond the Sword\\Saves\\single\\quick\\QuickSave.CivBeyondSwordSave";
				the user directory can vary. */
			CvString szQuickSavePath(BUGOption::userDirPath());
			if (!szQuickSavePath.empty())
			{
				szQuickSavePath += "\\Beyond the Sword\\Saves\\single\\quick\\QuickSave.CivBeyondSwordSave";
				// CTD if loading fails, so let's make sure that the file is good.
				std::ifstream quickSaveFile(szQuickSavePath);
				if (quickSaveFile.good())
				{
					kUI.exitingToMainMenu(szQuickSavePath.c_str());
					break;
				}
			}
			FErrorMsg("Failed to find quicksave");
		} // </advc.003d>
		gDLL->QuickLoad();
		break;

	// <!-- custom: Revision 151 pairs the existing camera control requests with authoritative Boolean result changes for modes that expose cheap getters.
	// Cycle-flying-mode and camera rotation remain request-only because they have no equivalent Boolean result contract. (ChatGPT-5.6-Sol) -->
	case CONTROL_ORTHO_CAMERA:
	{
		bool const bOldValue = kEngine.GetOrthoCamera();
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		kEngine.SetOrthoCamera(!bOldValue);
		if (bLogSASControl) logSASGameRecordCameraBoolChange(eControl, bOldValue, kEngine.GetOrthoCamera());
		break;
	}

	case CONTROL_CYCLE_CAMERA_FLYING_MODES:
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		kEngine.CycleFlyingMode(1);
		break;

	case CONTROL_ISOMETRIC_CAMERA_LEFT:
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		kEngine.MoveBaseTurnLeft();
		break;

	case CONTROL_ISOMETRIC_CAMERA_RIGHT:
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		kEngine.MoveBaseTurnRight();
		break;

	case CONTROL_FLYING_CAMERA:
	{
		// <!-- custom: With CivilizationIV.ini allowflying=0, Ctrl+Alt+F reached this handler and logged accepted requests but GetFlying reported no change.
		// Setting allowflying=1 and restarting Civ4 produced flying=0>1 and 1>0; request acceptance alone does not prove the EXE applied a camera mode.
		// Users who do not use Flying Camera can leave allowflying=0; that recorded preference does not mean the enabled-mode transition hook was untested. (GPT-6.1-Sol) -->
		bool const bOldValue = kEngine.GetFlying();
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		kEngine.SetFlying(!bOldValue);
		if (bLogSASControl) logSASGameRecordCameraBoolChange(eControl, bOldValue, kEngine.GetFlying());
		break;
	}

	case CONTROL_MOUSE_FLYING_CAMERA:
	{
		bool const bOldValue = kEngine.GetMouseFlying();
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		kEngine.SetMouseFlying(!bOldValue);
		if (bLogSASControl) logSASGameRecordCameraBoolChange(eControl, bOldValue, kEngine.GetMouseFlying());
		break;
	}

	case CONTROL_TOP_DOWN_CAMERA:
	{
		bool const bOldValue = kEngine.GetSatelliteMode();
		if (bLogSASControl) logSASGameRecordControlRequest(eControl, true);
		kEngine.SetSatelliteMode(!bOldValue);
		if (bLogSASControl) logSASGameRecordCameraBoolChange(eControl, bOldValue, kEngine.GetSatelliteMode());
		break;
	}

	case CONTROL_CIVILOPEDIA:
		GC.getPythonCaller()->callScreenFunction("pediaShow");
		break;

	// <!-- custom: control handlers for Religion/Corporation removed after control enum cleanup. (GPT-5.3-Codex) -->
	case CONTROL_CIVICS_SCREEN:
		GET_PLAYER(getActivePlayer()).killAll(BUTTONPOPUP_CHANGECIVIC); // advc.004x
		// <!-- custom: renamed Python civics screen entrypoint to PolicyAdvisorScreen while keeping control id for compatibility. (GPT-5.3-Codex) -->
		GC.getPythonCaller()->showPythonScreen("PolicyAdvisorScreen");
		break;

	case CONTROL_FOREIGN_SCREEN:
		GC.getPythonCaller()->showForeignAdvisorScreen();
		break;

	case CONTROL_FOREIGN_DIPLOMACY_SCREEN:
		// <!-- custom: F3 control opens the Foreign Diplomacy advisor shell. (GPT-5.3-Codex) -->
		GC.getPythonCaller()->showPythonScreen("ForeignDiplomacyAdvisor");
		break;

	case CONTROL_MILITARY_SCREEN:
		GC.getPythonCaller()->showPythonScreen("MilitaryAdvisor");
		break;

	case CONTROL_TECH_CHOOSER:
		GC.getPythonCaller()->showPythonScreen("TechChooser");
		break;

	// <!-- custom: F7 World Advisor. (GPT-5.5) -->
	case CONTROL_WORLD_ADVISOR_SCREEN:
		GC.getPythonCaller()->showPythonScreen("WorldAdvisorScreen");
		break;

	case CONTROL_TURN_LOG:
		if (!gDLL->GetWorldBuilderMode() || kUI.isInAdvancedStart())
			kUI.toggleTurnLog();
		break;

	case CONTROL_CHAT_ALL:
		if (!gDLL->GetWorldBuilderMode() || kUI.isInAdvancedStart())
			kUI.showTurnLog(CHATTARGET_ALL);
		break;

	case CONTROL_CHAT_TEAM:
		if (!gDLL->GetWorldBuilderMode() || kUI.isInAdvancedStart())
			kUI.showTurnLog(CHATTARGET_TEAM);
		break;

	case CONTROL_DOMESTIC_SCREEN:
		//argsList.add(-1); // advc.003y: Unused param removed from CyScreensInterface.py
		GC.getPythonCaller()->showPythonScreen("DomesticAdvisor");
		break;

	case CONTROL_VICTORY_SCREEN:
		GC.getPythonCaller()->showPythonScreen("VictoryScreen");
		break;

	case CONTROL_INFO:
		GC.getPythonCaller()->showInfoScreen(0, getGameState() != GAMESTATE_ON);
		break;

	// <!-- custom: The action-filtering draft left this second globe-view path behind the action switch, suppressing its revision-150 runtime-state row when actions were disabled.
	// Use the independent runtime-view gate for both old-state capture and output, matching CONTROL_GLOBELAYER/Grid/Yields. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
	case CONTROL_GLOBE_VIEW:
	{
		bool bOldValue = false;
		if (bLogSASRuntimeView) bOldValue = kEngine.isGlobeviewUp();
		kEngine.toggleGlobeview();
		if (bLogSASRuntimeView) logSASGameRecordRuntimeViewBoolChange("CONTROL_GLOBE_VIEW", "globeView", bOldValue, kEngine.isGlobeviewUp());
		break;
	}

	case CONTROL_DETAILS:
		kUI.showDetails();
		break;

	case CONTROL_ADMIN_DETAILS:
		if (GC.getInitCore().getAdminPassword().empty())
			kUI.showAdminDetails();
		else
		{
			CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_ADMIN_PASSWORD);
			if (pInfo != NULL)
			{
				pInfo->setData1((int)CONTROL_ADMIN_DETAILS);
				kUI.addPopup(pInfo, NO_PLAYER, true);
			}
		}
		break;

	case CONTROL_HALL_OF_FAME:
		GC.getPythonCaller()->showHallOfFameScreen(true);
		break;

	case CONTROL_WORLD_BUILDER:
		// K-Mod. (original code moved into CvGame::retire)
		// <advc.007>
		if (isDebugMode())
			enterWorldBuilder();
		else // </advc.007>
		{
			CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_CONFIRM_MENU);
			if (pInfo != NULL)
			{
				// <!-- custom: Share the confirmation action ID with popup dispatch and its diagnostics while preserving the inherited payload value. (GPT-6.1-Sol) -->
				pInfo->setData1(SAS_POPUP_CONFIRM_WORLD_BUILDER);
				kUI.addPopup(pInfo, getActivePlayer(), true);
			}
		} // K-Mod end
		break;

	case CONTROL_ESPIONAGE_SCREEN:
		GC.getPythonCaller()->showPythonScreen("EspionageAdvisor");
		break;

	case CONTROL_FREE_COLONY:
	{
		CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_FREE_COLONY);
		if (pInfo != NULL)
			kUI.addPopup(pInfo);
		break;
	}
	case CONTROL_DIPLOMACY:
	{
		CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_DIPLOMACY);
		if (pInfo != NULL)
			kUI.addPopup(pInfo);
		break;
	}  // <advc.088>
	case CONTROL_UNSELECT_ALL:
	{
		kUI.clearSelectionList();
		break;
	} // </advc.088>
	default: FErrorMsg("Unknown control type");
	}
}

/*	K-Mod. This code use to be inside CvGame::doControl. I've moved it here and
	told doControl to simply create a confirmation popup. */
void CvGame::retire()
{
	FAssert(canDoControl(CONTROL_RETIRE));

	if (!isGameMultiPlayer() || countHumanPlayersAlive() == 1)
	{
		if (gDLL->GetAutorun())
		{
			GC.getInitCore().setSlotStatus(getActivePlayer(), SS_COMPUTER);
		}
		else
		{
			setGameState(GAMESTATE_OVER);
			gDLL->UI().setDirty(Soundtrack_DIRTY_BIT, true);
		}
	}
	else
	{
		if (isNetworkMultiPlayer())
		{
			gDLL->sendMPRetire();
			GC.getGame().exitToMenu();
		}
		else gDLL->handleRetirement(getActivePlayer());
	}
}


void CvGame::enterWorldBuilder()
{
	FAssert(canDoControl(CONTROL_WORLD_BUILDER));
	if (GC.getInitCore().getAdminPassword().empty())
	{	// <advc.135c>
		/*  In multiplayer, setWorldBuilder apparently checks ChtLvl>0 and setChtLvl
			doesn't work. Need to make the EXE believe that we're in singleplayer. */
		m_bFeignSP = true;
		gDLL->setChtLvl(1); // </advc.135c>
		gDLL->UI().setWorldBuilder(!gDLL->GetWorldBuilderMode());
		if (isSASRuntimeStatusEnabled()) updateSASRuntimeStatusWorldBuilderMode(gDLL->GetWorldBuilderMode());
		m_bFeignSP = false; // advc.135c
	}
	else
	{
		CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_ADMIN_PASSWORD);
		if (NULL != pInfo)
		{
			pInfo->setData1((int)CONTROL_WORLD_BUILDER);
			gDLL->UI().addPopup(pInfo, NO_PLAYER, true);
		}
	}
} // K-Mod end

/*	advc: Wrapper for CvDLLInterfaceIFaceBase::exitingToMainMenu.
	In case that there's something we want to do beforehand. */
void CvGame::exitToMenu()
{
	// <!-- custom: Time the observed return request before entering EXE menu work; a later reset is distinct from confirmed menu arrival. (GPT-6.1-Sol) -->
	if (isSASRuntimeStatusEnabled()) updateSASRuntimeStatusRequest(SAS_RUNTIME_STATUS_RETURN_TO_MENU_REQUESTED);
	gDLL->UI().exitingToMainMenu();
}

// advc:
void CvGame::setGlobeView(bool b)
{
	bool const bOldValue = gDLL->getEngineIFace()->isGlobeviewUp();
	if (bOldValue != b)
	{
		gDLL->getEngineIFace()->toggleGlobeview();
		// <!-- custom: Rise & Fall can change globe state through this wrapper rather than a ControlTypes command; sample the actual post-toggle value only behind the level/initialization gate so this path is tracked without polling. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
		if (gGameRecordLogLevel >= 2 && isFinalInitialized()) logSASGameRecordRuntimeViewBoolChange("SET_GLOBE_VIEW", "globeView", bOldValue, gDLL->getEngineIFace()->isGlobeviewUp());
	}
}


void CvGame::getGlobeLayers(std::vector<CvGlobeLayerData>& aLayers) const
{
	CvGlobeLayerData kUnit(GLOBE_LAYER_UNIT);
	kUnit.m_strName = "UNITS";
	kUnit.m_strButtonHelpTag = "TXT_KEY_GLOBELAYER_UNITS";
	kUnit.m_strButtonStyle = "Button_HUDGlobeUnit_Style";

	// <!-- custom: make these static const for performance optimization as advised by chatgpt 5 too. -->
	static const int iNumOptionsCalculated = ((GC.getDefineINT("SHOW_UNIT_LAYER_OPTIONS") <= 0 ? 0 : // advc.004z
			NUM_UNIT_OPTION_TYPES));

	kUnit.m_iNumOptions = iNumOptionsCalculated;
	kUnit.m_bGlobeViewRequired = false;
	aLayers.push_back(kUnit);

	CvGlobeLayerData kResource(GLOBE_LAYER_RESOURCE);
	kResource.m_strName = "RESOURCES";
	kResource.m_strButtonHelpTag = "TXT_KEY_GLOBELAYER_RESOURCES";
	kResource.m_strButtonStyle = "Button_HUDBtnResources_Style";
	/*  advc.004z (comment): Could check and enforce
		getBugOptionBOOL("MainInterface__ResourceIconOptions", false)
		here, but then the BUG option would require a restart. Therefore,
		this is done in CvMainInterface.py (updateGlobeviewButtons) instead. */
	kResource.m_iNumOptions = NUM_RESOURCE_OPTION_TYPES;
	kResource.m_bGlobeViewRequired = false;
	aLayers.push_back(kResource);

	CvGlobeLayerData kCulture(GLOBE_LAYER_CULTURE);
	kCulture.m_strName = "CULTURE";
	kCulture.m_strButtonHelpTag = "TXT_KEY_GLOBELAYER_CULTURE";
	kCulture.m_strButtonStyle = "Button_HUDGlobeCulture_Style";
	kCulture.m_bShouldCitiesZoom = true;
	aLayers.push_back(kCulture);

	CvGlobeLayerData kTrade(GLOBE_LAYER_TRADE);
	kTrade.m_strName = "TRADE";
	kTrade.m_strButtonHelpTag = "TXT_KEY_GLOBELAYER_TRADE";
	kTrade.m_strButtonStyle = "Button_HUDGlobeTrade_Style";
	kTrade.m_bShouldCitiesZoom = true;
	aLayers.push_back(kTrade);

	CvGlobeLayerData kReligion(GLOBE_LAYER_RELIGION);
	kReligion.m_strName = "RELIGION";
	kReligion.m_strButtonHelpTag = "TXT_KEY_GLOBELAYER_RELIGION";
	kReligion.m_strButtonStyle = "Button_HUDGlobeReligion_Style";
	kReligion.m_iNumOptions = GC.getNumReligionInfos();
	kReligion.m_bShouldCitiesZoom = true;
	aLayers.push_back(kReligion);
}


void CvGame::startFlyoutMenu(CvPlot const* pPlot, std::vector<CvFlyoutMenuData>& aFlyoutItems) const
{
	aFlyoutItems.clear();

	bool bUnits = false;
	bool bFortifyUnit = false;
	bool bSleepUnit = false;
	bool bWakeUnit = false;

	FOR_EACH_UNIT_IN(pUnit, *pPlot)
	{
		if (pUnit->getOwner() != getActivePlayer())
			continue;
		bUnits = true;
		if (pUnit->canFortify(pPlot))
			bFortifyUnit = true;
		else if (pUnit->canSleep(pPlot))
			bSleepUnit = true;
		else if (pUnit->isWaiting())
			bWakeUnit = true;
	}

	CvWString szBuffer;
	CvCity* pCity = pPlot->getPlotCity();
	if (pCity != NULL && pCity->getOwner() == getActivePlayer())
	{
		szBuffer = gDLL->getText("TXT_KEY_CHANGE_PRODUCTION");
		aFlyoutItems.push_back(CvFlyoutMenuData(NO_FLYOUT, -1, -1, -1, szBuffer));
		CvCivilization const& kCiv = pCity->getCivilization(); // advc.003w
		for (int i = 0; i < kCiv.getNumUnits(); i++)
		{
			UnitTypes eLoopUnit = kCiv.unitAt(i);
			if (!pCity->canTrain(eLoopUnit))
				continue;
			szBuffer = GC.getInfo(eLoopUnit).getDescription();
			int iTurns = pCity->getProductionTurnsLeft(eLoopUnit, 0);
			if (iTurns < MAX_INT) // advc.004x
				szBuffer.append(CvWString::format(L" (%d)", iTurns));
			aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUT_TRAIN, eLoopUnit,
					pPlot->getX(), pPlot->getY(), szBuffer));
		}
		for (int i = 0; i < kCiv.getNumBuildings(); i++)
		{
			BuildingTypes eLoopBuilding = kCiv.buildingAt(i);
			if (!pCity->canConstruct(eLoopBuilding))
				continue;
			szBuffer = GC.getInfo(eLoopBuilding).getDescription();
			int iTurns = pCity->getProductionTurnsLeft(eLoopBuilding, 0);
			if (iTurns < MAX_INT) // advc.004x
				szBuffer.append(CvWString::format(L" (%d)", iTurns));
			aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUT_CONSTRUCT, eLoopBuilding,
					pPlot->getX(), pPlot->getY(), szBuffer));
		}
		FOR_EACH_ENUM(Project)
		{
			if (!pCity->canCreate(eLoopProject))
				continue;
			szBuffer = GC.getInfo(eLoopProject).getDescription();
			int iTurns = pCity->getProductionTurnsLeft(eLoopProject, 0);
			if (iTurns < MAX_INT) // advc.004x
				szBuffer.append(CvWString::format(L" (%d)", iTurns));
			aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUT_CREATE, eLoopProject,
					pPlot->getX(), pPlot->getY(), szBuffer));
		}
		FOR_EACH_ENUM(Process)
		{
			if (!pCity->canMaintain(eLoopProcess))
				continue;
			szBuffer = GC.getInfo(eLoopProcess).getDescription();
			aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUT_MAINTAIN, eLoopProcess,
					pPlot->getX(), pPlot->getY(), szBuffer));
		}

		aFlyoutItems.push_back(CvFlyoutMenuData(NO_FLYOUT, -1, -1, -1, L""));
		FOR_EACH_ENUM(Hurry)
		{
			if (!pCity->canHurry(eLoopHurry))
				continue;
			szBuffer = gDLL->getText("TXT_KEY_HURRY_PRODUCTION");
			int iHurryGold = pCity->hurryGold(eLoopHurry);
			if (iHurryGold > 0)
				szBuffer += gDLL->getText("TXT_KEY_HURRY_PRODUCTION_GOLD", iHurryGold);
			int iHurryPopulation = pCity->hurryPopulation(eLoopHurry);
			if (iHurryPopulation > 0)
				szBuffer += gDLL->getText("TXT_KEY_HURRY_PRODUCTION_POP", iHurryPopulation);
				aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUT_HURRY, eLoopHurry,
						pPlot->getX(), pPlot->getY(), szBuffer));
		}

		if (pCity->canConscript())
		{
			UnitTypes eConscriptUnit = pCity->getConscriptUnit();
			if (eConscriptUnit != NO_UNIT)
			{
				szBuffer = gDLL->getText("TXT_KEY_DRAFT_UNIT",
						GC.getInfo(eConscriptUnit).getDescription(),
						pCity->getConscriptPopulation());
				aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUT_CONSCRIPT,
						GC.getNumHurryInfos(), pPlot->getX(), pPlot->getY(), szBuffer));
			}
		}
	}

	CvUnit* pHeadSelectedUnit = gDLL->UI().getHeadSelectedUnit();
	if (pHeadSelectedUnit != NULL && !pHeadSelectedUnit->atPlot(pPlot))
	{
		gDLL->getFAStarIFace()->SetData(&GC.getInterfacePathFinder(),
				gDLL->UI().getSelectionList());
		if (pHeadSelectedUnit->getDomainType() == DOMAIN_AIR ||
			gDLL->getFAStarIFace()->GeneratePath(&GC.getInterfacePathFinder(),
			pHeadSelectedUnit->getX(), pHeadSelectedUnit->getY(),
			pPlot->getX(), pPlot->getY(), false, MOVE_DECLARE_WAR, true))
		{
			if (pHeadSelectedUnit->getDomainType() == DOMAIN_AIR)
				szBuffer = gDLL->getText("TXT_KEY_FLYOUT_MENU_FLY_TO");
			else
			{
				szBuffer = gDLL->getText("TXT_KEY_FLYOUT_MENU_MOVE_TO",
						gDLL->getFAStarIFace()->GetLastNode(
						&GC.getInterfacePathFinder())->m_iData2);
			}
			aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUT_MOVE_TO, 0,
					pPlot->getX(), pPlot->getY(), szBuffer));
		}
	}

	if (bUnits)
	{
		szBuffer = gDLL->getText("TXT_KEY_FLYOUT_MENU_SELECT_ALL");
		aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUT_SELECT_ALL,
				0, pPlot->getX(), pPlot->getY(), szBuffer));

		if (bWakeUnit)
		{
			szBuffer = gDLL->getText("TXT_KEY_FLYOUT_MENU_WAKE_ALL");
			aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUT_WAKE_ALL,
					0, pPlot->getX(), pPlot->getY(), szBuffer));
		}

		if (bFortifyUnit)
		{
			szBuffer = gDLL->getText("TXT_KEY_FLYOUT_MENU_FORTIFY_ALL");
			aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUR_FORTIFY_ALL,
					0, pPlot->getX(), pPlot->getY(), szBuffer));
		}
		else if (bSleepUnit)
		{
			szBuffer = gDLL->getText("TXT_KEY_FLYOUT_MENU_SLEEP_ALL");
			aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUR_SLEEP_ALL,
					0, pPlot->getX(), pPlot->getY(), szBuffer));
		}

		static std::vector<CvUnit*> plotUnits;
		getPlotUnits(pPlot, plotUnits);
		for (int iI = 0; iI < (int)plotUnits.size(); iI++)
		{
			CvUnit* pLoopUnit = plotUnits[iI];
			if (pLoopUnit->getOwner() == getActivePlayer())
			{
				CvWStringBuffer szTempBuffer;
				GAMETEXT.setUnitHelp(szTempBuffer, pLoopUnit, true);
				aFlyoutItems.push_back(CvFlyoutMenuData(FLYOUT_SELECT_UNIT,
						pLoopUnit->getID(), pPlot->getX(), pPlot->getY(),
						szTempBuffer.getCString()));
			}
		}
	}
}


void CvGame::applyFlyoutMenu(CvFlyoutMenuData const& kItem)
{
	CvPlot* pPlot = GC.getMap().plot(kItem.m_iX, kItem.m_iY);
	if (pPlot == NULL)
		return;

	switch (kItem.m_eFlyout)
	{
	case NO_FLYOUT:
	default:
		FAssert(false);
		break;

	case FLYOUT_HURRY:
	{
		CvCity* pCity = pPlot->getPlotCity();
		if (pCity != NULL && pCity->getOwner() == getActivePlayer())
		{
			CvMessageControl::getInstance().sendDoTask(pCity->getID(),
					TASK_HURRY, kItem.m_iID, -1, false, false, false, false);
		}
		break;
	}

	case FLYOUT_CONSCRIPT:
	{
		CvCity* pCity = pPlot->getPlotCity();
		if (pCity != NULL && pCity->getOwner() == getActivePlayer())
		{
			CvMessageControl::getInstance().sendDoTask(pCity->getID(),
					TASK_CONSCRIPT, -1, -1, false, false, false, false);
		}
		break;
	}

	case FLYOUT_TRAIN:
	{
		CvCity* pCity = pPlot->getPlotCity();
		if (pCity != NULL && pCity->getOwner() == getActivePlayer())
			cityPushOrder(pCity, ORDER_TRAIN, kItem.m_iID);
		break;
	}

	case FLYOUT_CONSTRUCT:
	{
		CvCity* pCity = pPlot->getPlotCity();
		if (pCity != NULL && pCity->getOwner() == getActivePlayer())
			cityPushOrder(pCity, ORDER_CONSTRUCT, kItem.m_iID);
		break;
	}

	case FLYOUT_CREATE:
	{
		CvCity* pCity = pPlot->getPlotCity();
		if (pCity != NULL && pCity->getOwner() == getActivePlayer())
			cityPushOrder(pCity, ORDER_CREATE, kItem.m_iID);
		break;
	}

	case FLYOUT_MAINTAIN:
	{
		CvCity* pCity = pPlot->getPlotCity();
		if (pCity != NULL && pCity->getOwner() == getActivePlayer())
			cityPushOrder(pCity, ORDER_MAINTAIN, kItem.m_iID);
		break;
	}

	case FLYOUT_MOVE_TO:
		selectionListMove(pPlot, false, false, false);
		break;

	case FLYOUT_SELECT_UNIT:
	{
		CvUnit* pUnit = GET_PLAYER(getActivePlayer()).getUnit(kItem.m_iID);
		if (pUnit != NULL)
			gDLL->UI().selectUnit(pUnit, true);
		break;
	}

	case FLYOUT_SELECT_ALL:
		gDLL->UI().selectAll(pPlot);
		break;

	case FLYOUT_WAKE_ALL:
	{
		FOR_EACH_UNIT_IN(pUnit, *pPlot)
		{
			if (pUnit->isGroupHead() &&
				pUnit->getOwner() == getActivePlayer()) // K-Mod
			{
				CvMessageControl::getInstance().sendDoCommand(pUnit->getID(),
						COMMAND_WAKE, -1, -1, false);
			}
		}
		break;
	}
	case FLYOUR_FORTIFY_ALL:
	case FLYOUR_SLEEP_ALL:
	{
		FOR_EACH_UNIT_IN(pUnit, *pPlot)
		{
			if (pUnit->isGroupHead() &&
				pUnit->getOwner() == getActivePlayer()) // K-Mod
			{
				CvMessageControl::getInstance().sendPushMission(pUnit->getID(),
						pUnit->isFortifyable() ? MISSION_FORTIFY : MISSION_SLEEP,
						-1, -1, NO_MOVEMENT_FLAGS, false, /* advc.011b: */ GC.ctrlKey());
			}
		}
		break;
	}
	}
}


CvPlot* CvGame::getNewHighlightPlot() const
{
	if (gDLL->GetWorldBuilderMode())
		return GC.getPythonCaller()->WBGetHighlightPlot();
	if (GC.getInfo(gDLL->UI().getInterfaceMode()).getHighlightPlot())
		return gDLL->UI().getMouseOverPlot();
	updateNukeAreaOfEffect(); // advc.653
	return NULL;
}


ColorTypes CvGame::getPlotHighlightColor(CvPlot* pPlot) const
{
	if (pPlot == NULL)
		return NO_COLOR;
	// <!-- custom: make these static const for performance optimization as advised by chatgpt 5 too. -->
	static const ColorTypes eDefaultColor = GC.getColorType("GREEN");
	if (gDLL->GetWorldBuilderMode())
		return eDefaultColor;
	static const ColorTypes eNegativeColor = GC.getColorType("DARK_GREY");

	switch (gDLL->UI().getInterfaceMode())
	{
	case INTERFACEMODE_PING:
	case INTERFACEMODE_SIGN:
		if (!pPlot->isRevealed(getActiveTeam(), true))
			return NO_COLOR;
		return eDefaultColor;
	case INTERFACEMODE_PYTHON_PICK_PLOT:
		if (!pPlot->isRevealed(getActiveTeam(), true) ||
			!GC.getPythonCaller()->canPickRevealedPlot(*pPlot))
		{
			return NO_COLOR;
		}
		return eDefaultColor;
	case INTERFACEMODE_SAVE_PLOT_NIFS:
		return eNegativeColor;
	}
	bool bCanDoMode = gDLL->UI().getSelectionList()->
			canDoInterfaceModeAt(gDLL->UI().getInterfaceMode(), pPlot);
	// <advc.653>
	if (updateNukeAreaOfEffect(bCanDoMode ? pPlot : NULL))
		return NO_COLOR; // </advc.653>
	if (bCanDoMode)
		return eDefaultColor;
	return eNegativeColor;
}

// advc.653: (Returns true if plots have been colored)
bool CvGame::updateNukeAreaOfEffect(CvPlot const* pCenter) const
{
	CvUnit const* pNuke = gDLL->UI().getHeadSelectedUnit();
	if (pNuke == NULL || !pNuke->isNuke())
		return false;
	gDLL->getEngineIFace()->clearAreaBorderPlots(AREA_BORDER_LAYER_NUKE);
	if (pCenter == NULL || gDLL->UI().getInterfaceMode() != INTERFACEMODE_NUKE)
		return false;
	if (!pNuke->canNukeAt(pNuke->getPlot(), pCenter->getX(), pCenter->getY(),
		pNuke->getTeam()))
	{
		return false;
	}

	// <!-- custom: make these static const for performance optimization as advised by chatgpt 5 too. -->
	static const ColorTypes eColorYellow = (ColorTypes)GC.getColorType("YELLOW");
	NiColorA const& kColor = GC.getInfo(eColorYellow).getColor();

	for (SquareIter itPlot(*pCenter, pNuke->nukeRange()); itPlot.hasNext(); ++itPlot)
	{
		gDLL->getEngineIFace()->fillAreaBorderPlot(itPlot->getX(), itPlot->getY(),
				kColor, AREA_BORDER_LAYER_NUKE);
	}
	return true;
}

// advc.004k:
void CvGame::updateSeaPatrolColors(CvUnit const& kSelectedUnit)
{
	gDLL->getEngineIFace()->clearAreaBorderPlots(AREA_BORDER_LAYER_PATROLLED);
	if (!kSelectedUnit.isSeaPatrolling())
		return;
	// <!-- custom: make these static const for performance optimization as advised by chatgpt 5 too. -->
	// <!-- custom: code/performance optimization: hoist -->
	static const ColorTypes eColorCityBlue = (ColorTypes)GC.getInfoTypeForString("COLOR_CITY_BLUE");
	for (SquareIter itPlot(kSelectedUnit, GC.getMAX_SEA_PATROL_RANGE(), false);
		itPlot.hasNext(); ++itPlot)
	{
		if (kSelectedUnit.canReachBySeaPatrol(*itPlot))
		{
			gDLL->getEngineIFace()->fillAreaBorderPlot(itPlot->getX(), itPlot->getY(), GC.getInfo(eColorCityBlue).getColor(), AREA_BORDER_LAYER_PATROLLED);
		}
	}
}

void CvGame::loadBuildQueue(const CvString& strItem) const
{
	// advc.003w: The first two loops were needlessly complicated
	CvCivilization const& kCiv = *getActiveCivilization();
	for (int i = 0; i < kCiv.getNumUnits(); i++)
	{
		UnitTypes eUnit = kCiv.unitAt(i);
		if (GC.getInfo(eUnit).getType() == strItem)
		{
			selectedCitiesGameNetMessage(GAMEMESSAGE_PUSH_ORDER, ORDER_TRAIN,
					eUnit, -1, false, false, true);
			return;
		}
	}
	for (int i = 0; i < kCiv.getNumBuildings(); i++)
	{
		BuildingTypes eBuilding = kCiv.buildingAt(i);
		if (GC.getInfo(eBuilding).getType() == strItem)
		{
			selectedCitiesGameNetMessage(GAMEMESSAGE_PUSH_ORDER, ORDER_CONSTRUCT,
					eBuilding, -1, false, false, true);
			return;
		}
	}
	FOR_EACH_ENUM(Project)
	{
		if (strItem == GC.getInfo(eLoopProject).getType())
		{
			selectedCitiesGameNetMessage(GAMEMESSAGE_PUSH_ORDER, ORDER_CREATE,
					eLoopProject, -1, false, false, true);
			return;
		}
	}

	FOR_EACH_ENUM(Process)
	{
		if (strItem == GC.getInfo(eLoopProcess).getType())
		{
			selectedCitiesGameNetMessage(GAMEMESSAGE_PUSH_ORDER, ORDER_MAINTAIN,
					eLoopProcess, -1, false, false, true);
			return;
		}
	}
}


void CvGame::cheatSpaceship() const
{	// <advc.007b> I don't know how this is triggered; it's safer to block it.
	if (!isDebugMode())
		return; // </advc.007b>
	//add one space project that is still available
	CvTeam& kTeam = GET_TEAM(getActiveTeam());
	FOR_EACH_ENUM2(Project, eProject)
	{
		CvProjectInfo const& kProject = GC.getInfo(eProject);
		if (kProject.isSpaceship())
		{
			//cheat required projects
			FOR_EACH_ENUM2(Project, eReqProject)
			{
				int iNumReqProjects = kProject.getProjectsNeeded(eReqProject);
				while (kTeam.getProjectCount(eReqProject) < iNumReqProjects)
				{
					kTeam.changeProjectCount(eReqProject, 1);
				}
			}

			//cheat required techs
			TechTypes eRequiredTech = kProject.getTechPrereq();
			if (!kTeam.isHasTech(eRequiredTech))
				kTeam.setHasTech(eRequiredTech, true, getActivePlayer(), true, true, false, TECH_ACQUISITION_DEBUG);

			//cheat one space component
			if (kTeam.getProjectCount(eProject) < kProject.getMaxTeamInstances())
			{
				kTeam.changeProjectCount(eProject, 1);
				CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_PYTHON_SCREEN, eProject);
				pInfo->setText(L"showSpaceShip");
				gDLL->UI().addPopup(pInfo, getActivePlayer());
			}
		}
	}
}


DomainTypes CvGame::getUnitDomain(UnitTypes eUnit) const
{
	return GC.getInfo(eUnit).getDomainType();
}


CvArtInfoBuilding const* CvGame::getBuildingArtInfo(BuildingTypes eBuilding) const
{
	return GC.getInfo(eBuilding).getArtInfo();
}


bool CvGame::isWaterBuilding(BuildingTypes eBuilding) const
{
	return GC.getInfo(eBuilding).isWater();
}


CivilopediaWidgetShowTypes CvGame::getWidgetShow(BonusTypes eBonus) const
{
	/*	Don't show the widget if it's an abstract bonus that
		doesn't have any terrain (or art) associated with it.
		Hit singles, movies, musicals, in our case */
	bool bShowWidget = false;
	FOR_EACH_ENUM(Terrain)
	{
		if (GC.getInfo(eBonus).isTerrain(eLoopTerrain))
		{
			bShowWidget = true;
			break;
		}
	}
	if (!bShowWidget)
	{
		FOR_EACH_ENUM(Feature)
		{
			if (GC.getInfo(eBonus).isFeature(eLoopFeature))
			{
				bShowWidget = true;
				break;
			}
		}
	}
	if (!bShowWidget)
		return CIVILOPEDIA_WIDGET_SHOW_NONE;
	CivilopediaWidgetShowTypes eType = CIVILOPEDIA_WIDGET_SHOW_LAND;
	FOR_EACH_ENUM(Terrain)
	{
		if (GC.getInfo(eLoopTerrain).isWater())
		{
			if (GC.getInfo(eBonus).isTerrain(eLoopTerrain))
				eType = CIVILOPEDIA_WIDGET_SHOW_WATER;
		}
	}

	return eType;
}


CivilopediaWidgetShowTypes CvGame::getWidgetShow(ImprovementTypes eImprovement) const
{
	CivilopediaWidgetShowTypes eType = CIVILOPEDIA_WIDGET_SHOW_LAND;
	if (GC.getInfo(eImprovement).isWater())
		eType = CIVILOPEDIA_WIDGET_SHOW_WATER;
	return eType;
}

// (advc: getSpaceVictory implementation moved to CvGame.cpp)

// advc (note): Alt+Z causes the EXE to call this function
void CvGame::nextActivePlayer(bool bForward)
{
	int iNewPlayer = getActivePlayer();
	for (int i = 1; i < MAX_PLAYERS; i++)
	{
		if (bForward)
			iNewPlayer += 1;
		else iNewPlayer += MAX_PLAYERS - 1;
		iNewPlayer %= MAX_PLAYERS;

		PlayerTypes eNewPlayer = (PlayerTypes)iNewPlayer;
		if (GET_PLAYER(eNewPlayer).isAlive() && !GET_PLAYER(eNewPlayer).isBarbarian())
		{
			// advc.210: Merged into BBAI function, which also takes care of alerts.
			changeHumanPlayer(eNewPlayer);
			break;
		}
	}
}


int CvGame::getNextSoundtrack(EraTypes eLastEra, int iLastSoundtrack) const
{
	EraTypes eCurEra = GET_PLAYER(getActivePlayer()).getCurrentEra();
	CvEraInfo const& kCurrentEra = GC.getInfo(eCurEra);
	if (kCurrentEra.getNumSoundtracks() == 0)
		return -1;
	if (kCurrentEra.getNumSoundtracks() == 1 ||
		(eLastEra != eCurEra && kCurrentEra.isFirstSoundtrackFirst()))
	{
		int const iSelectedSoundtrack = kCurrentEra.getSoundtracks(0);
		// <!-- custom: Record the existing EXE-facing soundtrack return after selection; this is selection evidence, not proof that the audio engine started playback.
		// Reuse the chosen ID/script so diagnostics make no extra async RNG draw. (ChatGPT-5.6-Sol) -->
		if (gGameRecordLogLevel >= 2) logSASGameRecordSoundtrackSelection(eCurEra, eLastEra, 0, iSelectedSoundtrack, iLastSoundtrack, kCurrentEra.getSoundtrackScriptName(0), kCurrentEra.getNumSoundtracks() == 1 ? "ONLY_TRACK" : "FIRST_OF_ERA");
		return iSelectedSoundtrack;
	}
	//return kCurrentEra.getSoundtracks(GC.getASyncRand().get(kCurrentEra.getNumSoundtracks(), "Pick Song ASYNC"));
	/*	<advc.002o> Perhaps was meant to be implemented this way? Why else handle
		kCurrentEra.getNumSoundtracks()==1 upfront? (Not to mention the unused param.) */
	std::vector<int> aiTracks;
	for (int i = 0; i < kCurrentEra.getNumSoundtracks(); i++)
	{
		int iTrack = kCurrentEra.getSoundtracks(i);
		if (iTrack != iLastSoundtrack)
			aiTracks.push_back(iTrack);
	}
	bool const bNoAlternativeResolvedId = aiTracks.empty();
	if (bNoAlternativeResolvedId)
		aiTracks.push_back(iLastSoundtrack);
	int const iSelectedChoice = GC.getASyncRand().get(aiTracks.size(), "Pick Song ASYNC");
	int const iSelectedSoundtrack = aiTracks[iSelectedChoice]; // </advc.002o>
	if (gGameRecordLogLevel >= 2)
	{
		int iSelectedIndex = -1;
		if (!bNoAlternativeResolvedId)
		{
			int iEligibleIndex = 0;
			for (int i = 0; i < kCurrentEra.getNumSoundtracks(); i++)
			{
				if (kCurrentEra.getSoundtracks(i) == iLastSoundtrack)
					continue;
				if (iEligibleIndex == iSelectedChoice)
				{
					iSelectedIndex = i;
					break;
				}
				iEligibleIndex++;
			}
		}
		// <!-- custom: The fallback returns the previous resolved ID without selecting an XML slot, so leave its slot and script unknown. (GPT-6.1-Sol) -->
		logSASGameRecordSoundtrackSelection(eCurEra, eLastEra, iSelectedIndex, iSelectedSoundtrack, iLastSoundtrack,
			iSelectedIndex < 0 ? NULL : kCurrentEra.getSoundtrackScriptName(iSelectedIndex), bNoAlternativeResolvedId ? "REPEAT_ONLY_RESOLVED_ID" : "RANDOM_EXCLUDING_PREVIOUS");
	}
	return iSelectedSoundtrack;
}


int CvGame::getSoundtrackSpace() const
{
	return std::max(1, GC.getInfo(GET_PLAYER(getActivePlayer()).getCurrentEra()).
			getSoundtrackSpace());
}


bool CvGame::isSoundtrackOverride(CvString& strSoundtrack) const
{
	// <!-- custom: make these static const for performance optimization as advised by chatgpt 5 too. -->
	static const bool bVICTORY_SOUNDTRACK_AVAILABLE = (GC.getDefineINT("VICTORY_SOUNDTRACK_AVAILABLE") != 0);

	if (bVICTORY_SOUNDTRACK_AVAILABLE)
	{
		if (getGameState() == GAMESTATE_EXTENDED || getGameState() == GAMESTATE_OVER)
		{
			bool const bVictory = (getWinner() == getActiveTeam());
			strSoundtrack = bVictory ? "AS2D_VICTORY" : "AS2D_DEFEAT";
			// <!-- custom: Victory/defeat state can persist while the EXE queries this override repeatedly.
			// Record only a new/changed override return so a polling detail cannot flood the game record. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
			if (gGameRecordLogLevel >= 2) updateSASGameRecordSoundtrackOverride(true, strSoundtrack.GetCString(), bVictory ? "VICTORY" : "DEFEAT");
			return true;
		}
	}
	if (gGameRecordLogLevel >= 2) updateSASGameRecordSoundtrackOverride(false, NULL, NULL);
	return false;
}


void CvGame::initSelection() const
{
	bool bSelected = false;
	CvPlayer& kActivePlayer = GET_PLAYER(getActivePlayer());
	// <advc.153> Replacing two non-nested loops
	enum PassTypes
	{
		FIGHT_AND_ALL_READY,
		ALL_READY,
		// New passes:
		FIGHT_AND_ANY_READY,
		ANY_READY,
		NUM_PASSES
	};
	for (int iPass = 0; iPass < NUM_PASSES &&
		!bSelected; iPass++)
	{
		PassTypes const ePass = (PassTypes)iPass;
		FOR_EACH_UNIT_VAR(pLoopUnit, kActivePlayer)
		{
			if ((ePass == FIGHT_AND_ALL_READY || ePass == FIGHT_AND_ANY_READY) &&
				!pLoopUnit->canFight())
			{
				continue;
			}
			if ((ePass == FIGHT_AND_ALL_READY || ePass == ALL_READY) &&
				!pLoopUnit->getGroup()->readyToSelect())
			{
				continue;
			}
			if ((ePass == FIGHT_AND_ANY_READY || ePass == ANY_READY) &&
				!pLoopUnit->getGroup()->readyToSelect(true))
			{
				continue;
			}
			selectUnit(pLoopUnit, true);
			bSelected = true;
			break;
		}
	} // </advc.153>
	if (!bSelected)
	{
		FOR_EACH_UNIT_VAR(pLoopUnit, kActivePlayer)
		{
			gDLL->UI().centerCamera(pLoopUnit);
			break;
		}
	}
}


bool CvGame::canDoPing(CvPlot* pPlot, PlayerTypes ePlayer) const
{
	if (pPlot == NULL || !pPlot->isRevealed(getActiveTeam()))
		return false;
	if (TEAMID(ePlayer) != getActiveTeam())
		return false;
	return true;
}


bool CvGame::shouldDisplayReturn() const
{
	return gDLL->UI().isCitySelection();
}


bool CvGame::shouldDisplayEndTurn() const
{
	return (!gDLL->UI().isCitySelection() &&
			GET_PLAYER(getActivePlayer()).isTurnActive());
}


bool CvGame::shouldDisplayWaitingOthers() const
{	// <advc.706>
	if (!GET_PLAYER(getActivePlayer()).isHuman())
		return false; // </advc.706>
	if (!gDLL->UI().isCitySelection())
	{
		if (!GET_PLAYER(getActivePlayer()).isTurnActive())
			return true;

		if (gDLL->UI().isInAdvancedStart() &&
			GET_PLAYER(getActivePlayer()).getAdvancedStartPoints() < 0)
		{
			return true;
		}
	}
	return false;
}


bool CvGame::shouldDisplayWaitingYou() const
{
	if (!gDLL->UI().isCitySelection() &&
		GET_PLAYER(getActivePlayer()).isTurnActive() &&
		isNetworkMultiPlayer())
	{
		if (isMPOption(MPOPTION_SIMULTANEOUS_TURNS) &&
			countNumHumanGameTurnActive() == 1)
		{
			return true;
		}
		if (isSimultaneousTeamTurns() &&
			GET_TEAM(getActiveTeam()).countNumHumanGameTurnActive() == 1 &&
			GET_TEAM(getActiveTeam()).getAliveCount() > 1)
		{
			return true;
		}
	}
	return false;
}


bool CvGame::shouldDisplayEndTurnButton() const
{
	return
		(!gDLL->UI().isCitySelection() &&
		!gDLL->GetWorldBuilderMode() &&
		GET_PLAYER(getActivePlayer()).isTurnActive());
}


bool CvGame::shouldDisplayFlag() const
{
	return
		!(gDLL->UI().isCitySelection() ||
		gDLL->UI().getHeadSelectedCity() != NULL ||
		gDLL->isDiplomacy() ||
		gDLL->isMPDiplomacyScreenUp() ||
		gDLL->GetWorldBuilderMode());
}


bool CvGame::shouldDisplayUnitModel() const
{
	if (gDLL->isDiplomacy() ||
		gDLL->isMPDiplomacyScreenUp() ||
		gDLL->GetWorldBuilderMode())
	{
		return false;
	}

	if (gDLL->UI().getHeadSelectedUnit() != NULL ||
		//gDLL->UI().isCityScreenUp()
		gDLL->UI().getHeadSelectedCity() != NULL) // advc.001
	{
		return true;
	}

	return false;
}


bool CvGame::shouldShowResearchButtons() const
{
	if (!gDLL->GetWorldBuilderMode())
	{
		CvPlayer const& kActivePlayer = GET_PLAYER(getActivePlayer()); // advc
		if (kActivePlayer.isAlive() && !gDLL->UI().isCityScreenUp())
		{
			if (kActivePlayer.isResearch() && // advc.004x
				kActivePlayer.getCurrentResearch() == NO_TECH)
			{
				return true;
			}
		}
	}
	return false;
}


bool CvGame::shouldCenterMinimap() const
{
	return (isDebugMode() || GET_TEAM(getActiveTeam()).isMapCentering());
}


EndTurnButtonStates CvGame::getEndTurnState() const
{
	/*if ((isNetworkMultiPlayer() &&
		(isMPOption(MPOPTION_SIMULTANEOUS_TURNS) && countNumHumanGameTurnActive() == 1 ||
		(!isSimultaneousTeamTurns() && GET_TEAM(getActiveTeam()).countNumHumanGameTurnActive() == 1 &&
		GET_TEAM(getActiveTeam()).getAliveCount() > 1))))*/ // BtS
	/*	K-Mod. Don't use GET_TEAM in pitboss mode.
		(and note, I've fixed a typo in the parentheses.) */
	if (isNetworkMultiPlayer() && getActiveTeam() != NO_TEAM &&
		((isMPOption(MPOPTION_SIMULTANEOUS_TURNS) &&
		  countNumHumanGameTurnActive() == 1) ||
		(!isSimultaneousTeamTurns() &&
		  GET_TEAM(getActiveTeam()).countNumHumanGameTurnActive() == 1 &&
		  GET_TEAM(getActiveTeam()).getAliveCount() > 1)))
	// K-Mod end
	{
		return END_TURN_OVER_HIGHLIGHT;
	}
	return END_TURN_GO;
}

/*	advc: Called once the EXE signals that graphics have been initialized
	(w/e that means exactly) */
void CvGame::onGraphicsInitialized()
{
	// advc.095:
	setCityBarWidth(BUGOption::isEnabled("MainInterface__WideCityBars", false));
	/*	<advc.001> After loading, the camera tries to center on some unit
		(apparently; I don't know where that's implemented). If there is
		none, it seems to center on some random(?) unrevealed tile. */
	if (GET_PLAYER(getActivePlayer()).getNumUnits() == 0)
		setUpdateTimer(UPDATE_LOOK_AT_STARTING_PLOT, 1);
	// </advc.001>
	GC.getPythonCaller()->callScreenFunction("updateCameraStartDistance"); // advc.004m
}

// advc.095:
void CvGame::setCityBarWidth(bool bWide)
{
	if (ARTFILEMGR.isCityBarPathsSwapped() == bWide)
		return;
	ARTFILEMGR.swapCityBarPaths();
	for (PlayerIter<ALIVE> itPlayer; itPlayer.hasNext(); ++itPlayer)
	{
		FOR_EACH_CITY_VAR(pCity, *itPlayer)
			pCity->reloadEntity();
	}
}


void CvGame::handleCityScreenPlotPicked(CvCity* pCity, CvPlot* pPlot, bool bAlt, bool bShift, bool bCtrl) const
{
	if (pCity == NULL || pPlot == NULL)
	{
		FAssert(false); // advc (BtS had only asserted pPlot)
		return;
	}
	int iIndex = pCity->getCityPlotIndex(*pPlot);
	if (pPlot->getOwner() == getActivePlayer() &&
		pCity->getOwner() == getActivePlayer() && iIndex != NO_CITYPLOT)
	{
		CvMessageControl::getInstance().sendDoTask(pCity->getID(),
				TASK_CHANGE_WORKING_PLOT, iIndex, -1, false, bAlt, bShift, bCtrl);
	}
	else //if (GC.getDefineINT("CITY_SCREEN_CLICK_WILL_EXIT"))
	if (BUGOption::isEnabled("CityScreen__ClickMapToExit", true)) // advc.004t
		gDLL->UI().clearSelectedCities();
}


void CvGame::handleCityScreenPlotDoublePicked(CvCity* pCity, CvPlot* pPlot, bool bAlt, bool bShift, bool bCtrl) const
{
	if (pCity != NULL && pCity->plot() == pPlot)
	{
		/*	<advc.004t> Exit upon double click outside the radius, not upon
			double click on the city center. */
		/*gDLL->UI().clearSelectedCities()*/;
	}
	else if (pPlot != NULL && pCity->getCityPlotIndex(*pPlot) == NO_CITYPLOT)
		gDLL->UI().clearSelectedCities(); // </advc.004t>
}


void CvGame::handleCityScreenPlotRightPicked(CvCity* pCity, CvPlot* pPlot, bool bAlt, bool bShift, bool bCtrl) const
{
	if (pCity == NULL || pPlot == NULL)
	{
		FAssert(false); // advc: As in handleCityScreenPlotPicked
		return;
	}
	/*  <advc.004t> Can't assign a working city to the city plot, so use this
		for exiting the screen. */
	if (pCity->plot() == pPlot)
	{
		CvPlot const* pCityPlot = (gDLL->UI().isCityScreenUp() ?
				gDLL->UI().getHeadSelectedCity()->plot() : NULL);
		gDLL->UI().clearSelectedCities();
		if (pCityPlot != NULL)
			gDLL->UI().lookAt(pCityPlot->getPoint(), CAMERALOOKAT_NORMAL);
		return;
	} // </advc.004t>
	if (pCity->getOwner() == getActivePlayer() &&
		pPlot->getOwner() == getActivePlayer() &&
		pCity->getCityPlotIndex(*pPlot) != -1)
	{
		CvMessageControl::getInstance().sendDoTask(pCity->getID(),
				TASK_CLEAR_WORKING_OVERRIDE, pCity->getCityPlotIndex(*pPlot),
				-1, false, bAlt, bShift, bCtrl);
	}
}


void CvGame::handleCityPlotRightPicked(CvCity* pCity, CvPlot* pPlot, bool bAlt, bool bShift, bool bCtrl) const
{
	if (pPlot == NULL)
		return;
	if (pCity != NULL && gDLL->UI().isCitySelected(pCity))
		selectedCitiesGameNetMessage(GAMEMESSAGE_DO_TASK, TASK_CLEAR_RALLY_PLOT);
	else
	{
		if (bShift)
		{
			selectedCitiesGameNetMessage(GAMEMESSAGE_DO_TASK, TASK_RALLY_PLOT,
					pPlot->getX(), pPlot->getY());
		}
		else gDLL->UI().clearSelectedCities();
	}
}


void CvGame::handleMiddleMouse(bool bCtrl, bool bAlt, bool bShift)
{
	if (gDLL->UI().isCitySelection())
		gDLL->UI().clearSelectedCities();
	else
	{
		if (bAlt)
			doControl(CONTROL_SELECTYUNITALL);
		else if (bCtrl)
			doControl(CONTROL_SELECTYUNITTYPE);
		else doControl(CONTROL_CENTERONSELECTION);
	}
}


void CvGame::handleDiplomacySetAIComment(DiploCommentTypes eComment) const
{
	PlayerTypes eOtherPlayer = (PlayerTypes) gDLL->getDiplomacyPlayer();
	FAssert(eOtherPlayer != NO_PLAYER);
	if (GC.getAIDiploCommentType("ACCEPT_ASK") == eComment ||
		GC.getAIDiploCommentType("ACCEPT_DEMAND") == eComment)
	{
		if (!GET_TEAM(getActiveTeam()).isAVassal() && !GET_TEAM(eOtherPlayer).isAVassal())
		{
			CLinkList<TradeData> playerList;
			CLinkList<TradeData> loopPlayerList;
			TradeData peaceTreaty(TRADE_PEACE_TREATY);
			playerList.insertAtEnd(peaceTreaty);
			loopPlayerList.insertAtEnd(peaceTreaty);
			gDLL->sendImplementDealMessage(eOtherPlayer, &playerList, &loopPlayerList);
		}
	}
	// advc.072:
	m_bShowingCurrentDeals = (eComment == GC.getAIDiploCommentType("CURRENT_DEALS"));
}

// advc.092c:
void CvGame::setHelpTextAreaWidth(float fWidth)
{
	smc::BtS_EXE.setHelpTextAreaSize(fWidth);
}

// <advc.004x>
void CvGame::setDawnOfManShown(bool b)
{
	m_bDoMShown = b;
}


bool CvGame::isAboutToShowDawnOfMan() const
{
	return (!m_bDoMShown && getElapsedGameTurns() <= 0);
} // </advc.004x>

/*	<advc.061> Could get this through winuser.h, but that's not trivial.
	Let's just let Python provide the info to us. */
void CvGame::setScreenDimensions(int iWidth, int iHeight)
{
	if (m_iScreenWidth == iWidth && m_iScreenHeight == iHeight)
		return;
	m_iScreenWidth = iWidth;
	m_iScreenHeight = iHeight;
	// advc.001: Avoid warped plot indicators upon changing resolution
	gDLL->UI().setDirty(GlobeLayer_DIRTY_BIT, true);
	CvGlobals::getInstance().updateCityCamDist(); // advc.004m
	/*	<advc.092b> Do this as soon as we know the screen dimensions, before
		a plot indicator gets created for the initially selected units. */
	if (m_iScreenHeight > 0)
		smc::BtS_EXE.patchPlotIndicatorSize(); // </advc.092b>
}

int CvGame::getScreenWidth() const
{
	return m_iScreenWidth;
}

int CvGame::getScreenHeight() const
{
	return m_iScreenHeight;
} // </advc.061>

// advc.004n:
void CvGame::onCityScreenChange()
{
	// <!-- custom: The EXE state-change detector above is the authoritative city-screen transition point; record it here so unexpected autoplay/UI entries can be reconstructed without Python polling. (ChatGPT-5.6-Sol) -->
	if (gGameRecordLogLevel >= 2 && isSASGameRecordActionTraceEnabled() && isFinalInitialized())
	{
		CvCity const* pSASCity = gDLL->UI().getHeadSelectedCity();
		logSASGameRecordScreenAction("CITY_SCREEN", (m_bCityScreenUp ? "SHOW" : "HIDE"),
			(pSASCity == NULL ? -1 : pSASCity->getOwner()), (pSASCity == NULL ? -1 : pSASCity->getID()));
	}
	changePlotListShift(-getPlotListShift());
	/*	To fix a BtS issue with the bottom rows of the plot list
		being empty after having shifted the plot list on the city screen.
		(Looks like the EXE ensures a nonnegative column value. Could probably
		get the current value via Python for a more proper reset.) */
	gDLL->UI().changePlotListColumn(-100000);
	/*	<advc.092> Move the camera north a bit b/c that'll center the
		map excerpt on the city screen better. */
	if (m_bCityScreenUp)
	{
		static float const fSASCityScreenCameraNorthBias = GC.getDefineINT("SAS_CITY_CAMERA_NORTH_BIAS_PCT") / 100.0f;
		static float const fSASCityScreenCameraNorthBiasHUDBonus = GC.getDefineINT("SAS_CITY_CAMERA_NORTH_BIAS_HUD_BONUS_PCT") / 100.0f;
		CvPlot const* pCityPlot = gDLL->UI().getSelectionPlot();
		if (pCityPlot != NULL)
		{
			CvPlot const* pOneNorth = GC.getMap().plotDirection(
					pCityPlot->getX(), pCityPlot->getY(), DIRECTION_NORTH);
			if (pOneNorth != NULL)
			{
				NiPoint3 nOneNorth = pOneNorth->getPoint();
				NiPoint3 nCity = pCityPlot->getPoint();
				// <!-- custom: keep city-screen camera north shift tunable via SAS defines so city UI can reclaim bottom room (e.g. multi-row city panels) without showing tiles beyond BFC. (GPT-5.3-Codex) -->
				float const fDisplWeight = fSASCityScreenCameraNorthBias +
						(BUGOption::isEnabled("MainInterface__EnlargeHUD", true) ?
						fSASCityScreenCameraNorthBiasHUDBonus : 0);
				NiPoint3 nLookAt(nCity.x,
						nCity.y + fDisplWeight * (nOneNorth.y - nCity.y), nCity.z);
				gDLL->UI().lookAt(nLookAt, CAMERALOOKAT_CITY_ZOOM_IN);
			}
		}
	} // </advc.092>
}

// <!-- custom: SASPilot writes plots as JSON here, for CyGame.getSASPilotPlotsJson: 0.32 ms for 441 plots against 8 ms in Python (2026-11-13).
// A mailbox served from the DLL was tried too and dropped: the EXE called the DLL only about four times a second, so requests waited about 200 ms, against 2 ms for the pilot's Python, served every frame. See "Would the DLL be faster?" in README_Pilot.md. (Claude code Opus 5.5) -->
namespace
{
	void appendSASPilotJsonType(std::string& szOut, char const* szType)
	{
		if (szType == NULL)
			szOut += "null";
		else
		{
			szOut += '"';
			szOut += szType;
			szOut += '"';
		}
	}

	void appendSASPilotJsonInt(std::string& szOut, int i)
	{
		char szBuffer[16];
		_snprintf(szBuffer, sizeof(szBuffer), "%d", i);
		szBuffer[sizeof(szBuffer) - 1] = '\0';
		szOut += szBuffer;
	}

	// <!-- custom: Escapes exactly as the Python writer does, so the two outputs can be compared byte for byte. (Claude code Opus 5.5) -->
	void appendSASPilotJsonWide(std::string& szOut, wchar const* sz)
	{
		szOut += '"';
		for (; *sz != 0; sz++)
		{
			unsigned int const c = (unsigned int)*sz;
			if (c == '"')
				szOut += "\\\"";
			else if (c == '\\')
				szOut += "\\\\";
			else if (c == '\n')
				szOut += "\\n";
			else if (c == '\r')
				szOut += "\\r";
			else if (c == '\t')
				szOut += "\\t";
			else if (c < 32 || c > 126)
			{
				char szBuffer[8];
				_snprintf(szBuffer, sizeof(szBuffer), "\\u%04x", c);
				szBuffer[sizeof(szBuffer) - 1] = '\0';
				szOut += szBuffer;
			}
			else
				szOut += (char)c;
		}
		szOut += '"';
	}

	// <!-- custom: The brief unit of _unitBrief in SASPilotCommands.py, keys sorted as the Python writer sorts them; used inside plots and by getSASPilotUnitsJson. (Claude code Opus 5.5) -->
	void appendSASPilotUnitJson(std::string& szOut, CvUnit const& kUnit)
	{
		szOut += "{\"damage\":";
		appendSASPilotJsonInt(szOut, kUnit.getDamage());
		szOut += ",\"group\":";
		appendSASPilotJsonInt(szOut, kUnit.getGroupID());
		szOut += ",\"id\":";
		appendSASPilotJsonInt(szOut, kUnit.getID());
		szOut += ",\"movesLeft\":";
		appendSASPilotJsonInt(szOut, kUnit.movesLeft());
		szOut += ",\"owner\":";
		appendSASPilotJsonInt(szOut, kUnit.getOwner());
		szOut += ",\"type\":";
		appendSASPilotJsonType(szOut, GC.getInfo(kUnit.getUnitType()).getType());
		szOut += ",\"x\":";
		appendSASPilotJsonInt(szOut, kUnit.getX());
		szOut += ",\"y\":";
		appendSASPilotJsonInt(szOut, kUnit.getY());
		szOut += '}';
	}

	// <!-- custom: Mirrors _plotFull in SASPilotCommands.py field for field, keys in the sorted order the Python writer uses. (Claude code Opus 5.5) -->
	// <!-- custom: eFogTeam added so the pilot can also see the map as a player of that team does, to play as a person would rather than with full information (the user's request, 2026-11-13); NO_TEAM keeps the full view.
	// With fog, a plot the team has not revealed is left out by the caller, so a big map costs only what is known; a revealed plot out of sight gives what the team last saw (owner, improvement, route) and no units; a plot in sight hides invisible units; a bonus shows only once its tech reveals it.
	// Yields and the feature are the plot's current ones even out of sight. (Claude code Fable 5.2) -->
	void appendSASPilotPlotJson(std::string& szOut, CvPlot const& kPlot, TeamTypes eActiveTeam, TeamTypes eFogTeam)
	{
		bool const bFog = (eFogTeam != NO_TEAM);
		bool const bSeen = (!bFog || kPlot.isVisible(eFogTeam));
		szOut += "{\"area\":";
		appendSASPilotJsonInt(szOut, kPlot.getArea().getID());
		szOut += ",\"bonus\":";
		BonusTypes const eBonus = kPlot.getBonusType(eFogTeam);
		appendSASPilotJsonType(szOut, eBonus == NO_BONUS ? NULL : GC.getInfo(eBonus).getType());
		if (kPlot.isCity() && (!bFog || kPlot.getPlotCity()->isRevealed(eFogTeam)))
		{
			szOut += ",\"city\":";
			appendSASPilotJsonWide(szOut, kPlot.getPlotCity()->getName().GetCString());
		}
		szOut += ",\"feature\":";
		FeatureTypes const eFeature = kPlot.getFeatureType();
		appendSASPilotJsonType(szOut, eFeature == NO_FEATURE ? NULL : GC.getInfo(eFeature).getType());
		szOut += ",\"freshWater\":";
		szOut += (kPlot.isFreshWater() ? "true" : "false");
		szOut += ",\"improvement\":";
		ImprovementTypes const eImprovement = (bSeen ? kPlot.getImprovementType() : kPlot.getRevealedImprovementType(eFogTeam));
		appendSASPilotJsonType(szOut, eImprovement == NO_IMPROVEMENT ? NULL : GC.getInfo(eImprovement).getType());
		szOut += ",\"isCity\":";
		szOut += (kPlot.isCity() && (!bFog || kPlot.getPlotCity()->isRevealed(eFogTeam)) ? "true" : "false");
		szOut += ",\"owner\":";
		appendSASPilotJsonInt(szOut, bSeen ? kPlot.getOwner() : kPlot.getRevealedOwner(eFogTeam));
		szOut += ",\"plotType\":";
		// <!-- custom: Was the PlotTypes number (2 for land), the one type in a plot given as a number; the fog-on playthrough (2026-11-13) needed CvEnums.h to read it. getSASPlotType gives PLOT_LAND and the like, as SGR writes it. (Claude code Opus 5.5) -->
		appendSASPilotJsonType(szOut, getSASPlotType(kPlot.getPlotType()));
		if (eActiveTeam != NO_TEAM)
		{
			szOut += ",\"revealed\":";
			szOut += (kPlot.isRevealed(eActiveTeam, false) ? "true" : "false");
		}
		szOut += ",\"river\":";
		szOut += (kPlot.isRiver() ? "true" : "false");
		szOut += ",\"route\":";
		RouteTypes const eRoute = (bSeen ? kPlot.getRouteType() : kPlot.getRevealedRouteType(eFogTeam));
		appendSASPilotJsonType(szOut, eRoute == NO_ROUTE ? NULL : GC.getInfo(eRoute).getType());
		szOut += ",\"terrain\":";
		TerrainTypes const eTerrain = kPlot.getTerrainType();
		appendSASPilotJsonType(szOut, eTerrain == NO_TERRAIN ? NULL : GC.getInfo(eTerrain).getType());
		szOut += ",\"units\":[";
		// <!-- custom: getUnitByIndex is protected; this walks the same list in the same order. (Claude code Opus 5.5) -->
		bool bFirstUnit = true;
		FOR_EACH_UNIT_IN(pUnit, kPlot)
		{
			if (bFog && (!bSeen || pUnit->isInvisible(eFogTeam, false)))
				continue;
			if (!bFirstUnit)
				szOut += ',';
			bFirstUnit = false;
			appendSASPilotUnitJson(szOut, *pUnit);
		}
		szOut += ']';
		if (eActiveTeam != NO_TEAM)
		{
			szOut += ",\"visible\":";
			szOut += (kPlot.isVisible(eActiveTeam, false) ? "true" : "false");
		}
		szOut += ",\"x\":";
		appendSASPilotJsonInt(szOut, kPlot.getX());
		szOut += ",\"y\":";
		appendSASPilotJsonInt(szOut, kPlot.getY());
		szOut += ",\"yields\":[";
		FOR_EACH_ENUM(Yield)
		{
			if (eLoopYield > 0)
				szOut += ',';
			appendSASPilotJsonInt(szOut, kPlot.getYield(eLoopYield));
		}
		szOut += "]}";
	}
}


// <!-- custom: Codex's review noted that an unchecked radius fed the reserve size and loops, so a huge one could overflow or stall the game; beyond the larger map side it adds nothing. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
bool isSASPilotRadiusValid(int iRadius)
{
	return (iRadius >= 0 && iRadius <= std::max(GC.getMap().getGridWidth(), GC.getMap().getGridHeight()));
}


// <!-- custom: iFogTeam added: -1 gives every plot in full, a team gives what that team knows; see appendSASPilotPlotJson. (Claude code Fable 5.2) -->
std::string getSASPilotPlotsJson(int iX, int iY, int iRadius, int iFogTeam)
{
	// <!-- custom: "null" for the pilot to report; an assertion here would stop assertion builds on a mistyped argument (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if (!isSASPilotRadiusValid(iRadius) || iFogTeam < -1 || iFogTeam >= MAX_TEAMS)
		return "null";
	TeamTypes const eFogTeam = (TeamTypes)iFogTeam;
	std::string szOut;
	szOut.reserve(300 * (2 * iRadius + 1) * (2 * iRadius + 1));
	PlayerTypes const eActive = GC.getGame().getActivePlayer();
	TeamTypes const eActiveTeam = (eActive == NO_PLAYER ? NO_TEAM : TEAMID(eActive));
	szOut += '[';
	bool bFirst = true;
	for (int iDY = -iRadius; iDY <= iRadius; iDY++)
	{
		for (int iDX = -iRadius; iDX <= iRadius; iDX++)
		{
			CvPlot const* pPlot = plotXY(iX, iY, iDX, iDY);
			if (pPlot == NULL || (eFogTeam != NO_TEAM && !pPlot->isRevealed(eFogTeam)))
				continue;
			if (!bFirst)
				szOut += ',';
			bFirst = false;
			appendSASPilotPlotJson(szOut, *pPlot, eActiveTeam, eFogTeam);
		}
	}
	szOut += ']';
	return szOut;
}


// <!-- custom: What iGiver could put on the diplomacy table for iReceiver, for the pilot's 'trade' and 'techs': per item kind, each entry canTradeItem allows, with the AI's getTradeDenial. Written in C++ as the Python loop took 3.5 ms of game time per 'trade' at turn 176 against 0.23 ms for a bare request, the only list command measured well above it (2026-11-13); the user prefers the faster version even for a small measured gain.
// Same entries as the Python writer it replaces, in enum order rather than alphabetical; "what" is the XML type, the city name or the team ID; gold kinds give the most the giver could give. (Claude code Opus 5.5) -->
// <!-- custom: iKind added: one TradeableItems kind, or -1 for all. 'techs' read the whole table eight times for its tech rows and took 3.3 ms against 0.77 ms for the Python loop it replaced, as Codex predicted from the code (2026-11-13). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
std::string getSASPilotTradeItemsJson(int iGiver, int iReceiver, int iKindOnly)
{
	if (iKindOnly < -1 || iKindOnly >= NUM_TRADEABLE_ITEMS)
		return "null";
	if (iGiver < 0 || iGiver >= MAX_CIV_PLAYERS || iReceiver < 0 || iReceiver >= MAX_CIV_PLAYERS || iGiver == iReceiver)
		return "null";
	CvPlayerAI const& kGiver = GET_PLAYER((PlayerTypes)iGiver);
	PlayerTypes const eReceiver = (PlayerTypes)iReceiver;
	if (!kGiver.isAlive() || !GET_PLAYER(eReceiver).isAlive())
		return "null";
	bool const bDenial = !kGiver.isHuman();
	std::string szOut;
	szOut.reserve(8192);
	szOut += '[';
	bool bFirst = true;
	for (int iKind = 0; iKind < NUM_TRADEABLE_ITEMS; iKind++)
	{
		if (iKindOnly >= 0 && iKind != iKindOnly)
			continue;
		TradeableItems const eKind = (TradeableItems)iKind;
		// <!-- custom: The data values to try, and the label kind: 0 none, 1 XML type, 2 city name, 3 team ID. (Claude code Opus 5.5) -->
		std::vector<int> aiEntries;
		int iLabel = 0;
		switch (eKind)
		{
		case TRADE_TECHNOLOGIES: iLabel = 1; for (int i = 0; i < GC.getNumTechInfos(); i++) aiEntries.push_back(i); break;
		case TRADE_RESOURCES: iLabel = 1; for (int i = 0; i < GC.getNumBonusInfos(); i++) aiEntries.push_back(i); break;
		case TRADE_CIVIC: iLabel = 1; for (int i = 0; i < GC.getNumCivicInfos(); i++) aiEntries.push_back(i); break;
		case TRADE_RELIGION: iLabel = 1; for (int i = 0; i < GC.getNumReligionInfos(); i++) aiEntries.push_back(i); break;
		case TRADE_CITIES:
		{
			iLabel = 2;
			FOR_EACH_CITY(pCity, kGiver)
				aiEntries.push_back(pCity->getID());
			break;
		}
		case TRADE_WAR:
		case TRADE_PEACE:
		case TRADE_EMBARGO:
			iLabel = 3;
			for (int i = 0; i < MAX_CIV_TEAMS; i++)
			{
				if (GET_TEAM((TeamTypes)i).isAlive())
					aiEntries.push_back(i);
			}
			break;
		case TRADE_GOLD: aiEntries.push_back(kGiver.AI_maxGoldTrade(eReceiver)); break;
		case TRADE_GOLD_PER_TURN: aiEntries.push_back(kGiver.AI_maxGoldPerTurnTrade(eReceiver)); break;
		default: aiEntries.push_back(0); break;
		}
		for (size_t i = 0; i < aiEntries.size(); i++)
		{
			int const iData = aiEntries[i];
			TradeData const kItem(eKind, iData);
			if (!kGiver.canTradeItem(eReceiver, kItem, false))
				continue;
			if (!bFirst)
				szOut += ',';
			bFirst = false;
			szOut += "{\"data\": ";
			appendSASPilotJsonInt(szOut, iData);
			if (bDenial)
			{
				szOut += ", \"denial\": ";
				DenialTypes const eDenial = kGiver.getTradeDenial(eReceiver, kItem);
				appendSASPilotJsonType(szOut, eDenial == NO_DENIAL ? NULL : getSASDenialType(eDenial));
			}
			szOut += ", \"item\": ";
			appendSASPilotJsonType(szOut, getSASTradeItemType(eKind));
			if (iLabel == 1)
			{
				char const* szType = NULL;
				if (eKind == TRADE_TECHNOLOGIES) szType = GC.getInfo((TechTypes)iData).getType();
				else if (eKind == TRADE_RESOURCES) szType = GC.getInfo((BonusTypes)iData).getType();
				else if (eKind == TRADE_CIVIC) szType = GC.getInfo((CivicTypes)iData).getType();
				else szType = GC.getInfo((ReligionTypes)iData).getType();
				szOut += ", \"what\": ";
				appendSASPilotJsonType(szOut, szType);
			}
			else if (iLabel == 2)
			{
				szOut += ", \"what\": ";
				appendSASPilotJsonWide(szOut, kGiver.getCity(iData)->getName().GetCString());
			}
			else if (iLabel == 3)
			{
				szOut += ", \"what\": ";
				appendSASPilotJsonInt(szOut, iData);
			}
			szOut += '}';
		}
	}
	szOut += ']';
	return szOut;
}


// <!-- custom: A player's units for the pilot's 'units' command, or every living player's with iPlayer -1. On a Huge map at turn 300, Python took 2 ms to read the 876 units and 6 ms to write them as JSON (2026-11-13). (Claude code Opus 5.5) -->
// <!-- custom: iFogTeam added: with a team, only the units that team sees now, as on the map. (Claude code Fable 5.2) -->
std::string getSASPilotUnitsJson(int iPlayer, int iFogTeam)
{
	if (iPlayer < -1 || iPlayer >= MAX_PLAYERS || iFogTeam < -1 || iFogTeam >= MAX_TEAMS)
		return "null";
	TeamTypes const eFogTeam = (TeamTypes)iFogTeam;
	std::string szOut;
	szOut += '[';
	bool bFirst = true;
	for (int i = 0; i < MAX_PLAYERS; i++)
	{
		if (iPlayer != -1 && i != iPlayer)
			continue;
		CvPlayer const& kPlayer = GET_PLAYER((PlayerTypes)i);
		if (iPlayer == -1 && !kPlayer.isAlive())
			continue;
		FOR_EACH_UNIT(pUnit, kPlayer)
		{
			if (eFogTeam != NO_TEAM && (!pUnit->getPlot().isVisible(eFogTeam) || pUnit->isInvisible(eFogTeam, false)))
				continue;
			if (!bFirst)
				szOut += ',';
			bFirst = false;
			appendSASPilotUnitJson(szOut, *pUnit);
		}
	}
	szOut += ']';
	return szOut;
}


// <!-- custom: The route a unit's group would take to a plot, step by step, for the pilot's 'path' command: a person sees it drawn on the map before committing, while Python's generatePath gives only whether a path exists and its turns.
// Each step has the plot, the turn of the path it is reached on (1 is this turn) and the moves left there, as the pathfinder's nodes hold them.
// A pathfinder of its own, so the shared one that missions and the AI rely on is untouched, and CvSelectionGroup::generatePath is not used because it asserts that the group is AI-controlled. "null" for a missing unit or plot. (Claude code Fable 5.2) -->
std::string getSASPilotPathJson(int iPlayer, int iUnit, int iX, int iY, int iFlags)
{
	if (iPlayer < 0 || iPlayer >= MAX_PLAYERS)
		return "null";
	CvUnit const* pUnit = GET_PLAYER((PlayerTypes)iPlayer).getUnit(iUnit);
	CvPlot const* pTo = GC.getMap().plot(iX, iY);
	// <!-- custom: A unit without a group or a plot, such as one being created or removed, has no path to ask for (Codex's review). (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	if (pUnit == NULL || pTo == NULL || pUnit->getGroup() == NULL || pUnit->plot() == NULL)
		return "null";
	GroupPathFinder kFinder;
	kFinder.setGroup(*pUnit->getGroup(), (MovementFlags)iFlags);
	if (!kFinder.generatePath(pUnit->getPlot(), *pTo))
		return "{\"found\":false}";
	std::vector<GroupPathNode const*> apNodes;
	for (GroupPathNode const* pNode = kFinder.getEndNode(); pNode != NULL; pNode = pNode->m_pParent)
		apNodes.push_back(pNode);
	std::string szOut = "{\"found\":true,\"steps\":[";
	// <!-- custom: The nodes run from the destination back to the start; the start plot itself is not a step. (Claude code Fable 5.2) -->
	for (int i = (int)apNodes.size() - 2; i >= 0; i--)
	{
		szOut += "{\"moves\":";
		appendSASPilotJsonInt(szOut, apNodes[i]->getMoves());
		szOut += ",\"turn\":";
		appendSASPilotJsonInt(szOut, apNodes[i]->getPathTurns());
		szOut += ",\"x\":";
		appendSASPilotJsonInt(szOut, apNodes[i]->getPlot().getX());
		szOut += ",\"y\":";
		appendSASPilotJsonInt(szOut, apNodes[i]->getPlot().getY());
		szOut += '}';
		if (i > 0)
			szOut += ',';
	}
	szOut += "],\"turns\":";
	appendSASPilotJsonInt(szOut, kFinder.getPathTurns());
	szOut += '}';
	return szOut;
}


// <!-- custom: The city sites the window circles when a person selects this Settler, for the pilot's 'sites' command; Python cannot reach CvPlayerAI's site list (fog-on playthrough, 2026-11-13).
// Same rules as CvGame::updateColoredPlots: the active player's AI_getCitySite list in its order, only sites the unit's group reaches within 7 turns, and a weaker site (later in the list) only while turns plus its index stay within 8 (advc.004).
// Each site has its found value for the player, as AI_foundValue gives it, and the path turns; "null" for a unit that cannot found a city or is missing. (Claude code Opus 5.5) -->
std::string getSASPilotCitySitesJson(int iPlayer, int iUnit)
{
	if (iPlayer < 0 || iPlayer >= MAX_PLAYERS)
		return "null";
	CvPlayerAI const& kPlayer = GET_PLAYER((PlayerTypes)iPlayer);
	CvUnit const* pUnit = kPlayer.getUnit(iUnit);
	if (pUnit == NULL || pUnit->getGroup() == NULL || pUnit->plot() == NULL || !pUnit->isFound())
		return "null";
	int const iMaxPathTurns = 7;
	GroupPathFinder sitePath;
	sitePath.setGroup(*pUnit->getGroup(), NO_MOVEMENT_FLAGS, iMaxPathTurns, GC.getMOVE_DENOMINATOR());
	std::string szOut = "[";
	bool bFirst = true;
	for (int i = 0; i < kPlayer.AI_getNumCitySites(); i++)
	{
		CvPlot const& kSite = kPlayer.AI_getCitySite(i);
		if (!sitePath.generatePath(kSite))
			continue;
		if (sitePath.getPathTurns() + i > iMaxPathTurns + 1)
			continue;
		if (!bFirst)
			szOut += ',';
		bFirst = false;
		szOut += "{\"foundValue\":";
		appendSASPilotJsonInt(szOut, kPlayer.AI_foundValue(kSite.getX(), kSite.getY()));
		szOut += ",\"rank\":";
		appendSASPilotJsonInt(szOut, i);
		szOut += ",\"turns\":";
		appendSASPilotJsonInt(szOut, sitePath.getPathTurns());
		szOut += ",\"x\":";
		appendSASPilotJsonInt(szOut, kSite.getX());
		szOut += ",\"y\":";
		appendSASPilotJsonInt(szOut, kSite.getY());
		szOut += '}';
	}
	szOut += ']';
	return szOut;
}


namespace
{
	// <!-- custom: canTradeItem assumes valid data: a tech, resource, civic or religion index in range, a team, a city of the giver, a positive amount (Codex's review of the first version, which passed anything that parsed). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	bool isSASPilotTradeDataValid(CvPlayer const& kGiver, TradeData const& kItem)
	{
		int const iData = kItem.m_iData;
		switch (kItem.m_eItemType)
		{
		case TRADE_GOLD:
		case TRADE_GOLD_PER_TURN:
			return (iData > 0);
		case TRADE_TECHNOLOGIES:
			return (iData >= 0 && iData < GC.getNumTechInfos());
		case TRADE_RESOURCES:
			return (iData >= 0 && iData < GC.getNumBonusInfos());
		case TRADE_CIVIC:
			return (iData >= 0 && iData < GC.getNumCivicInfos());
		case TRADE_RELIGION:
			return (iData >= 0 && iData < GC.getNumReligionInfos());
		case TRADE_PEACE:
		case TRADE_WAR:
		case TRADE_EMBARGO:
			return (iData >= 0 && iData < MAX_CIV_TEAMS && GET_TEAM((TeamTypes)iData).isAlive());
		case TRADE_CITIES:
			return (kGiver.getCity(iData) != NULL);
		// <!-- custom: Was "default: return true". Flag terms take the payload the window's table gives them, setTradeItem's 0 (CvPlayer::buildTradeTable); anything else can mean something internal, as a positive TRADE_OPEN_BORDERS payload marks a bookkeeping row in CvDeal::startTrade that opens no borders (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		default:
			return (iData == 0);
		}
	}

	// <!-- custom: An int read with strtol, refused when it overflows, which sscanf's %d left undefined (Codex's review); long is 32 bits in VC2003, so ERANGE covers int. Sets *pEnd past the digits. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	bool readSASPilotInt(char const* p, int& iValue, char const** pEnd)
	{
		char* szEnd = NULL;
		errno = 0;
		long const lValue = strtol(p, &szEnd, 10);
		if (szEnd == p || errno == ERANGE || lValue < INT_MIN || lValue > INT_MAX)
			return false;
		iValue = (int)lValue;
		*pEnd = szEnd;
		return true;
	}

	// <!-- custom: Reads "kind:data,kind:data" (TradeableItems and iData as numbers, from SASPilotCommands.py) into a trade list; false on a malformed entry, a kind out of range, invalid data, or an item given twice.
	// Duplicates are refused because canTradeItem checks each item alone: two gold items could each pass and together overspend, and a singleton term such as Open Borders makes no sense twice (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	bool readSASPilotTradeList(char const* szItems, CvPlayer const& kGiver, CLinkList<TradeData>& kList)
	{
		char const* p = szItems;
		while (*p != '\0')
		{
			int iKind = 0;
			int iData = 0;
			char const* szAfter = NULL;
			if (!readSASPilotInt(p, iKind, &szAfter) || *szAfter != ':' || !readSASPilotInt(szAfter + 1, iData, &szAfter) || iKind < 0 || iKind >= NUM_TRADEABLE_ITEMS)
				return false;
			TradeData const kItem((TradeableItems)iKind, iData);
			if (!isSASPilotTradeDataValid(kGiver, kItem))
				return false;
			bool const bListKind = (iKind == TRADE_TECHNOLOGIES || iKind == TRADE_RESOURCES || iKind == TRADE_CITIES || iKind == TRADE_PEACE || iKind == TRADE_WAR || iKind == TRADE_EMBARGO || iKind == TRADE_CIVIC || iKind == TRADE_RELIGION);
			FOR_EACH_TRADE_ITEM(kList)
			{
				if (pItem->m_eItemType == kItem.m_eItemType && (!bListKind || pItem->m_iData == kItem.m_iData))
					return false;
			}
			kList.insertAtEnd(kItem);
			p = szAfter;
			if (*p == ',')
				p++;
			else if (*p != '\0')
				return false;
		}
		return true;
	}
}


// <!-- custom: A deal the pilot's player proposes to an AI, as the diplomacy screen's Propose button does: the AI weighs it through AI_considerOfferExternal, the EXE's own entry, so SASGameRecord records it like a person's offer, and an accepted deal is implemented.
// Python could list what each side can trade (canTradeItem, getTradeDenial) but not ask the AI or make the deal (fog-on playthrough, 2026-11-13). Each item must pass canTradeItem for its giver; "null" on bad players or items. (Claude code Opus 5.5) -->
namespace
{
	// <!-- custom: The checks proposeSASPilotDeal and tableSASPilotDeal share: both players alive, the other an AI the player can contact, not a network game, both lists well formed, not both empty, and each item passing canTradeItem for its giver.
	// Split out of proposeSASPilotDeal on 2026-11-13 when tableSASPilotDeal needed the same rules, so the two cannot drift apart. (Claude code Opus 5.5) -->
	bool readSASPilotDeal(int iPlayer, int iOther, std::string const& szWeGive, std::string const& szTheyGive, CLinkList<TradeData>& kWeGive, CLinkList<TradeData>& kTheyGive)
	{
		if (iPlayer < 0 || iPlayer >= MAX_CIV_PLAYERS || iOther < 0 || iOther >= MAX_CIV_PLAYERS || iPlayer == iOther)
			return false;
		CvPlayer const& kPlayer = GET_PLAYER((PlayerTypes)iPlayer);
		CvPlayer const& kOther = GET_PLAYER((PlayerTypes)iOther);
		if (!kPlayer.isAlive() || !kOther.isAlive() || kOther.isHuman() || !kPlayer.canContact(kOther.getID()))
			return false;
		// <!-- custom: The deal is made directly, as the pilot's other orders are; in a network game that would bypass the net messages that keep the clients in sync (Codex's review), so refuse there. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if (GC.getGame().isNetworkMultiPlayer())
			return false;
		if (!readSASPilotTradeList(szWeGive.c_str(), kPlayer, kWeGive) || !readSASPilotTradeList(szTheyGive.c_str(), kOther, kTheyGive))
			return false;
		if (kWeGive.getLength() + kTheyGive.getLength() == 0)
			return false;
		// <!-- custom: Each loop in its own block, as FOR_EACH_TRADE_ITEM declares a node variable in the enclosing scope. (Claude code Opus 5.5) -->
		{
			FOR_EACH_TRADE_ITEM(kWeGive)
			{
				if (!kPlayer.canTradeItem(kOther.getID(), *pItem))
					return false;
			}
		}
		{
			FOR_EACH_TRADE_ITEM(kTheyGive)
			{
				if (!kOther.canTradeItem(kPlayer.getID(), *pItem))
					return false;
			}
		}
		return true;
	}
}


std::string proposeSASPilotDeal(int iPlayer, int iOther, std::string szWeGive, std::string szTheyGive)
{
	CLinkList<TradeData> kWeGive;
	CLinkList<TradeData> kTheyGive;
	if (!readSASPilotDeal(iPlayer, iOther, szWeGive, szTheyGive, kWeGive, kTheyGive))
		return "null";
	CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)iPlayer);
	CvPlayer& kOther = GET_PLAYER((PlayerTypes)iOther);
	bool const bAccepted = kOther.considerSASPilotOffer(kPlayer.getID(), kWeGive, kTheyGive);
	if (bAccepted)
		GC.getGame().implementDeal(kPlayer.getID(), kOther.getID(), kWeGive, kTheyGive);
	return bAccepted ? "{\"accepted\":true}" : "{\"accepted\":false}";
}


// <!-- custom: Opens the diplomacy screen with an AI on its trade table, with the given items already on it, as Ctrl+clicking the leader and then clicking the items does; CvPlayer::contact opens the same table under Ctrl, and AI offers fill it the same way.
// 'propose' skipped the screen, so "What would you want?" and the AI's counter-offer, which only the screen's replies reach (CyDiplomacy::counterPropose in CvDiplomacy.py), were out of the pilot's reach (fog-on playthrough, 2026-11-13); Python cannot add items to the EXE's table.
// "Our" list is what the player gives, "their" list what the AI gives, as in the AI's own offers (CvPlayerAI::AI_proposeWarTrade and others). false when readSASPilotDeal refuses or the player's turn is done, as contact itself requires. (Claude code Opus 5.5) -->
bool tableSASPilotDeal(int iPlayer, int iOther, std::string szWeGive, std::string szTheyGive)
{
	CLinkList<TradeData> kWeGive;
	CLinkList<TradeData> kTheyGive;
	if (!readSASPilotDeal(iPlayer, iOther, szWeGive, szTheyGive, kWeGive, kTheyGive))
		return false;
	if (iPlayer != GC.getGame().getActivePlayer() || GET_PLAYER((PlayerTypes)iPlayer).isTurnDone())
		return false;
	CvDiploParameters* pDiplo = new CvDiploParameters((PlayerTypes)iOther);
	pDiplo->setDiploComment(GC.getAIDiploCommentType("TRADING"));
	pDiplo->setOurOfferList(kWeGive);
	pDiplo->setTheirOfferList(kTheyGive);
	gDLL->UI().setDiploQueue(pDiplo, (PlayerTypes)iPlayer);
	return true;
}


// <!-- custom: Groups a unit with another on the same plot, as selecting both in the window does, or splits it off alone with iHeadUnit -1; for the pilot's 'group' command. Python has no joinGroup, and at turn 91 of the fog-on playthrough (2026-11-13) a Settler could not be escorted.
// canJoinGroup is the game's own test (same owner, plot and domain, no group about to split); refused in network games, as a direct change would bypass the net messages. "null" on a refusal, else the unit's group ID. (Claude code Opus 5.5) -->
std::string joinSASPilotGroup(int iPlayer, int iUnit, int iHeadUnit)
{
	if (iPlayer < 0 || iPlayer >= MAX_PLAYERS || GC.getGame().isNetworkMultiPlayer())
		return "null";
	CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)iPlayer);
	CvUnit* pUnit = kPlayer.getUnit(iUnit);
	if (pUnit == NULL || pUnit->getGroup() == NULL || pUnit->plot() == NULL)
		return "null";
	if (iHeadUnit < 0)
		pUnit->joinGroup(NULL, true);
	else
	{
		CvUnit* pHead = kPlayer.getUnit(iHeadUnit);
		if (pHead == NULL || pHead == pUnit || pHead->getGroup() == NULL || !pUnit->canJoinGroup(pUnit->plot(), pHead->getGroup()))
			return "null";
		pUnit->joinGroup(pHead->getGroup(), true);
	}
	std::string szOut;
	appendSASPilotJsonInt(szOut, pUnit->getGroupID());
	return szOut;
}


// <!-- custom: Chooses a free tech, such as the Oracle's, as the window's tech chooser does: CvNetResearch with iDiscover > 0 grants it (CvMessageData.cpp), which Python cannot send, as CyMessageControl.sendResearch always passes -1.
// At turn 105 of the fog-on playthrough (2026-11-13) the Oracle's free tech waited in a held choose-tech popup that 'todo' did not show. Only while the player is choosing a free tech, for a tech its chooser would list (canResearch); false otherwise. (Claude code Opus 5.5) -->
// <!-- custom: iHeldId added in place of iDiscover after Codex's review: two separate one-tech awards both had data1 1, so the Python side closed both choosers after spending one, and the binding trusted any positive count. The exact chooser now decides: a held one by its ID, which alone is removed, or with -1 the one on display, which a load can open before the pilot holds popups again. Its data1 is the count, as the window's buttons pass it. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
bool chooseSASPilotFreeTech(int iTech, int iHeldId)
{
	PlayerTypes const ePlayer = GC.getGame().getActivePlayer();
	if (ePlayer == NO_PLAYER || iTech < 0 || iTech >= GC.getNumTechInfos() || GC.getGame().isNetworkMultiPlayer())
		return false;
	CvPlayer& kPlayer = GET_PLAYER(ePlayer);
	if (!kPlayer.isChoosingFreeTech() || !kPlayer.canResearch((TechTypes)iTech))
		return false;
	// <!-- custom: Only a held chooser: the first version also took the one on display, reading its count and leaving it on screen, and Codex's review found that a later award, or the rest of a two-tech award, makes the player choosing again and that old chooser usable once more.
	// The DLL cannot consume a displayed popup: calling killAll(BUTTONPOPUP_CHOOSETECH, iDiscover) after the grant left it on screen (2026-11-13), as Fable had found (see launchButtonPopup). Holding now starts at the load, so the pilot asks for a held one. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if (iHeldId < 0)
		return false;
	int const iHeldIndex = findSASPilotHeldPopup(iHeldId);
	if (iHeldIndex < 0)
		return false;
	CvPopupInfo const& kHeld = getSASPilotHeldPopup(iHeldIndex);
	if (kHeld.getButtonPopupType() != BUTTONPOPUP_CHOOSETECH || kHeld.getData1() <= 0)
		return false;
	int const iDiscover = kHeld.getData1();
	removeSASPilotHeldPopup(iHeldIndex);
	kPlayer.changeChoosingFreeTechCount(-1);
	CvMessageControl::getInstance().sendResearch((TechTypes)iTech, iDiscover, false);
	return true;
}


// <!-- custom: The messages the game showed a player at the top of the screen (combat results, a city growing, a rival's border), which the pilot never saw without the window: from iSinceTurn on, oldest first.
// The game drops a message once its display time has passed, so this is what is still listed, not a full history; SASGameRecord keeps the lasting record. (Claude code Fable 5.2) -->
std::string getSASPilotMessagesJson(int iPlayer, int iSinceTurn)
{
	if (iPlayer < 0 || iPlayer >= MAX_PLAYERS)
		return "null";
	CvMessageQueue const& kMessages = GET_PLAYER((PlayerTypes)iPlayer).getGameMessages();
	std::string szOut = "[";
	bool bFirst = true;
	for (CvMessageQueue::const_iterator it = kMessages.begin(); it != kMessages.end(); ++it)
	{
		if (it->getTurn() < iSinceTurn)
			continue;
		if (!bFirst)
			szOut += ',';
		bFirst = false;
		szOut += "{\"from\":";
		appendSASPilotJsonInt(szOut, it->getFromPlayer());
		szOut += ",\"messageType\":";
		appendSASPilotJsonInt(szOut, it->getMessageType());
		szOut += ",\"text\":";
		appendSASPilotJsonWide(szOut, it->getDescription());
		szOut += ",\"turn\":";
		appendSASPilotJsonInt(szOut, it->getTurn());
		szOut += ",\"x\":";
		appendSASPilotJsonInt(szOut, it->getX());
		szOut += ",\"y\":";
		appendSASPilotJsonInt(szOut, it->getY());
		szOut += '}';
	}
	szOut += ']';
	return szOut;
}

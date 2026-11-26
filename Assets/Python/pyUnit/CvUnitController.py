# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Copied from vanilla Civ4's C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Assets\Python\pyUnit\CvUnitController.py (only vanilla Civ4 ships it), the copy SAS ran before (2026-11-26). See KI#1104. (Claude code Opus 5.5) -->
# <!-- custom: Since copied: calls on one line and table columns aligned with tabs, as CI's python_multiline_calls.py and python_aligned_columns.py ask; the code is otherwise the original's, but for the changes commented where they stand. (Claude code Opus 5.5) -->

from CvPythonExtensions import *
import random

MoveFormation_BoxRanges = [ [-0.8, -0.8, 0.8, 0.8],    # Two
							[-0.8, -0.8, -0.1, 0.8 , 0.1, -0.8, 0.8, 0.8],    # Three
							[-0.8, -0.8, -0.1, -0.1, 0.1, -0.8, 0.8, -0.1, -0.5, 0.1, 0.5, 0.8],    # Four
							[-0.8, -0.8, -0.2, -0.2, -0.8, 0.2, -0.2, 0.8, 0.2, -0.8, 0.8, -0.2, 0.2, 0.2, 0.8, 0.8], # Five
							[-0.8, -0.8, -0.2, -0.2, -0.8, 0.2, -0.2, 0.8, 0.2, -0.8, 0.8, -0.2, 0.2, 0.2, 0.8, 0.8, -0.3, -0.3, 0.3, 0.3]]
random.seed( 37 )   # should this be configurable?

class CvUnitController:

	def __init__(self):
		pass						# One

						
	def ProcessEvent ( self, pCyUnitEntity, iEvent):
		"""Controls the logic to react to the event."""

		# <!-- custom: Vanilla's body could not run: it reads MoveFormation_BoxRange, while the table above is MoveFormation_BoxRanges; its five rows, indexed by the count alive, overrun at five; and BehaviourStoppingCriterion is unresolved in every EXE, DLL and Python file checked.
		# No caller was found beyond CvUnitControlInterface's wrapper, and none seen in BtS; returning 0 hands the event to the engine's default handling, as that wrapper's docstring describes, instead of the NameError a first move would raise.
		# Fixing the name and index instead would enable an animation path relying on unverified bindings, so the body is kept disabled below, its trailing semicolons dropped for CI's Ruff E703. See KI#165.13. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		# <!-- custom: So in play this most likely changes nothing: it is tidiness that removes a NameError waiting for any caller and lets CI's undefined-name check pass without an exception for this file (the user asked, 2026-11-26). See KI#165.13. (Claude code Opus 5.5) -->
		return 0
#		if iEvent == EntityEventTypes.ENTEVENT_MOVE:

#			iNumAlive = pCyUnitEntity.GetUnitsCurrentlyAlive()
#			if iNumAlive > 5:   # We can't handle more than 5 sub-units...
#				return 0
#			iCurrentUnit = 0
#			for i in range(0, pCyUnitEntity.GetSubEntityCount()):

#				# 
#				pCyUnitSubEntity = pCyUnitEntity.GetSubEntity(i)
#				if pCyUnitSubEntity.isDead():
#					continue
#				x = random.uniform( MoveFormation_BoxRange[iNumAlive][iCurrentUnit * 4 + 0], MoveFormation_BoxRange[iNumAlive][iCurrentUnit * 4 + 2] )
#				y = random.uniform( MoveFormation_BoxRange[iNumAlive][iCurrentUnit * 4 + 1], MoveFormation_BoxRange[iNumAlive][iCurrentUnit * 4 + 3] )
#				kTarget = pCyUnitEntity.TranslateFormation( x, y )
#				pCyUnitSubEntity.SetPositionTarget( kTarget.x, kTarget.y, 0.0 )
#				pCyUnitSubEntity.SetAnimationPath( AnimationPathTypes.ANIMATIONPATH_RUN )
#				pCyUnitSubEntity.SetStoppingCriteria( BehaviourStoppingCriterion.STOPCRIT_DESTINATION )
#				pCyUnitSubEntity.SetFacingTargetTowardsPositionTarget()
#				pCyUnitSubEntity.PushBehaviourState( )
#				iCurrentUnit += 1

#			return 1

#		else:
#			return 0


# <!-- custom: moved some functions that are not used in games (outside of debugging code or such, not use in a "normal" game if i may say anyways etc), especially the very nice i mean debug leaderheadinfo one but not only, (another) other functions(function) as well anyways etc, moving them here as it would be heavy and unclean in this case anyways etc and would also clutter needlessly the other helpers. -->



# <!-- custom: modified from Claude AI's solution. -->
# <!-- custom: be careful/make sure to launch this at interfaceScreen level or later, else at __init__ this/the output is still empty, so run this later to have the actual tech info output; but also be careful to not launch/run/call this later than your error line if you have any, else the code execution would stop before you reach your debugger's call and you won't see any debug (e.g. if you have a code error at line 200, call debugger method at line 199 or sooner, not at line 201+ as it would never be reached before execution stops and you don't see debug content anyways etc), a good place may be the top of interfaceScreen generally i would say but check to be sure -->
# Get all attributes of the object
def printObjAttrs(obj):
	print ("[DEBUG] Beginning of show obj inner fields.")
	
	for attr in dir(obj):
		try:
			# Try to get the attribute
			attr_value = getattr(obj, attr)

			# Check if it's a method (callable)
			if callable(attr_value):
				print(u"%s\n" % attr)
			else:
				print(u"%s = %s\n" % (attr, attr_value))
		except:
			print(u"%s - Error accessing\n" % attr)
	
	print ("[DEBUG] End of show show obj inner fields.")



def debugPrintLeaderHeadInfoFieldsToFetch(iLeader, gc):
	# <!-- custom: first skip these/the fields below we don't use/need in our AI personality panel for example in LEADER_DEFAULTS even though said in code sample too but to be exhaustive:
	#
	#	<Type>LEADER_DEFAULTS</Type>
	#	<Description></Description>
	#	<Civilopedia></Civilopedia>
	#	<ArtDefineTag></ArtDefineTag>
	#
	# then: -->

	print("\n\n[DEBUG] For iLeader=%d, leader head info debugged as such:" % iLeader)

	# <!-- custom: more computationally efficient to store closest pointer since we have many/multiple calls to make anyways etc if i am not mistaken as chatgpt had done before and i was too dumb or rather maybe uninformed to understand/know, anyways etc, even if difference is minimal or not, and even if we don't use this except when debugging, no reason to not implement it as well. I (had) wanted for method call for clarity, but if this is more efficient better do it as so then maybe. -->
	info = gc.getLeaderHeadInfo(iLeader)

	# <!-- custom: try to follow XML order as much as possible and to be sure we have all fields too -->
	print("\n\n==== FIRST XML FIELDS PART 1 (from XML order) ====")
	print("iWonderConstructRand: %d" % info.getWonderConstructRand())
	print("iBaseAttitude: %d" % info.getBaseAttitude())
	print("iBasePeaceWeight: %d" % info.getBasePeaceWeight())
	print("iPeaceWeightRand: %d" % info.getPeaceWeightRand())
	print("iWarmongerRespect: %d" % info.getWarmongerRespect())
	print("iEspionageWeight: %d" % info.getEspionageWeight())
	print("iRefuseToTalkWarThreshold: %d" % info.getRefuseToTalkWarThreshold())
	print("iNoTechTradeThreshold: %d" % info.getNoTechTradeThreshold())
	print("iTechTradeKnownPercent: %d" % info.getTechTradeKnownPercent())
	print("iMaxGoldTradePercent: %d" % info.getMaxGoldTradePercent())
	print("iMaxGoldPerTurnTradePercent: %d" % info.getMaxGoldPerTurnTradePercent())

	# <!-- custom: also add BBAI Victory weights now that we have exposed them / expose them to python as well, see todo docs for details and todo add .cpp code comment filename -->
	print("\n\n==== BBAI VICTORY WEIGHTS ====")
	print("Culture Victory Weight: %d" % info.getCultureVictoryWeight())
	print("Space Victory Weight: %d" % info.getSpaceVictoryWeight())
	print("Conquest Victory Weight: %d" % info.getConquestVictoryWeight())
	print("Domination Victory Weight: %d" % info.getDominationVictoryWeight())
	print("Diplomacy Victory Weight: %d" % info.getDiplomacyVictoryWeight())

	# <!-- custom: then war fields continue anyways etc as per XML order -->
	print("\n\n==== WAR XML FIELDS (from XML order) ====")
	print("iMaxWarRand: %d" % info.getMaxWarRand())
	print("iMaxWarNearbyPowerRatio: %d" % info.getMaxWarNearbyPowerRatio())
	print("iMaxWarDistantPowerRatio: %d" % info.getMaxWarDistantPowerRatio())
	print("iMaxWarMinAdjacentLandPercent: %d" % info.getMaxWarMinAdjacentLandPercent())
	print("iLimitedWarRand: %d" % info.getLimitedWarRand())
	print("iLimitedWarPowerRatio: %d" % info.getLimitedWarPowerRatio())
	print("iDogpileWarRand: %d" % info.getDogpileWarRand())
	print("iMakePeaceRand: %d" % info.getMakePeaceRand())
	print("iDeclareWarTradeRand: %d" % info.getDeclareWarTradeRand())
	print("iDemandRebukedSneakProb: %d" % info.getDemandRebukedSneakProb())
	print("iDemandRebukedWarProb: %d" % info.getDemandRebukedWarProb())
	print("iRazeCityProb: %d" % info.getRazeCityProb())
	print("iBuildUnitProb: %d" % info.getBuildUnitProb())

	print("\n\n==== ATTITUDE MODIFIER FIELDS (from XML order) ====")
	print("iBaseAttackOddsChange: %d" % info.getBaseAttackOddsChange())
	print("iAttackOddsChangeRand: %d" % info.getAttackOddsChangeRand())
	print("iWorseRankDifferenceAttitudeChange: %d" % info.getWorseRankDifferenceAttitudeChange())
	print("iBetterRankDifferenceAttitudeChange: %d" % info.getBetterRankDifferenceAttitudeChange())
	print("iCloseBordersAttitudeChange: %d" % info.getCloseBordersAttitudeChange())
	print("iLostWarAttitudeChange: %d" % info.getLostWarAttitudeChange())
	print("iAtWarAttitudeDivisor: %d" % info.getAtWarAttitudeDivisor())
	print("iAtWarAttitudeChangeLimit: %d" % info.getAtWarAttitudeChangeLimit())
	print("iAtPeaceAttitudeDivisor: %d" % info.getAtPeaceAttitudeDivisor())
	print("iAtPeaceAttitudeChangeLimit: %d" % info.getAtPeaceAttitudeChangeLimit())
	print("iSameReligionAttitudeChange: %d" % info.getSameReligionAttitudeChange())
	print("iSameReligionAttitudeDivisor: %d" % info.getSameReligionAttitudeDivisor())
	print("iSameReligionAttitudeChangeLimit: %d" % info.getSameReligionAttitudeChangeLimit())
	print("iDifferentReligionAttitudeChange: %d" % info.getDifferentReligionAttitudeChange())
	print("iDifferentReligionAttitudeDivisor: %d" % info.getDifferentReligionAttitudeDivisor())
	print("iDifferentReligionAttitudeChangeLimit: %d" % info.getDifferentReligionAttitudeChangeLimit())
	print("iBonusTradeAttitudeDivisor: %d" % info.getBonusTradeAttitudeDivisor())
	print("iBonusTradeAttitudeChangeLimit: %d" % info.getBonusTradeAttitudeChangeLimit())
	print("iOpenBordersAttitudeDivisor: %d" % info.getOpenBordersAttitudeDivisor())
	print("iOpenBordersAttitudeChangeLimit: %d" % info.getOpenBordersAttitudeChangeLimit())
	print("iDefensivePactAttitudeDivisor: %d" % info.getDefensivePactAttitudeDivisor())
	print("iDefensivePactAttitudeChangeLimit: %d" % info.getDefensivePactAttitudeChangeLimit())
	print("iShareWarAttitudeChange: %d" % info.getShareWarAttitudeChange())
	print("iShareWarAttitudeDivisor: %d" % info.getShareWarAttitudeDivisor())
	print("iShareWarAttitudeChangeLimit: %d" % info.getShareWarAttitudeChangeLimit())
	print("iFavoriteCivicAttitudeChange: %d" % info.getFavoriteCivicAttitudeChange())
	print("iFavoriteCivicAttitudeDivisor: %d" % info.getFavoriteCivicAttitudeDivisor())
	print("iFavoriteCivicAttitudeChangeLimit: %d" % info.getFavoriteCivicAttitudeChangeLimit())

	# <!-- custom: there are "AttitudeThreshold" and "RefuseAttitudeThreshold", handle the most common case, they seem to all be about refusing something or not being able to do it if threshold is not met if i am not mistaken, handle them as such -->
	print("\n\n==== ATTITUDE THRESHOLDS ====")
	# <!-- custom: if i am not mistaken, based and comparing xml with debug values for leader_gandhi and leader_ragnar (for the furious value in leader_ragnar anyways etc), here is the table conversion map if i am not mistaken of attitude to num: none: -1, furious: 0, annoyed: 1, cautious: 2, pleased: 3, friendly: 4
	#
	# Overall very similar to our leaders_data map, with none being last/lowest/most forgiving value (less than furious) if i am not mistaken, and friendly being the highest, so we can use this map of the dll directly without needing to parse atittude str to num for our ranking of leaders in AI personality panel directly -->
	#
	# <!-- custom: Among all leaders, LEADER_ELIZABETH and LEADER_TOKUGAWA only have a value of 5 somehow, which triggers an error with our current map:
	#
	# Traceback (most recent call last):
	#   File "CvScreensInterface", line 495, in pediaJumpToLeader
	#   File "SevoPediaMain", line 313, in pediaJump
	#   File "SevoPediaLeader", line 455, in interfaceScreen
	#   File "_sevopedia_helpers", line 134, in debugPrintLeaderHeadInfoFieldsToFetch
	#
	# KeyError: 5
	# ERR: Python function pediaJumpToLeader failed, module CvScreensInterface
	#
	# however LEADER_ELIZABETH 's XML anyways etc is:
	# 		<MapRefuseAttitudeThreshold>ATTITUDE_FRIENDLY</MapRefuseAttitudeThreshold>
	#
	# and LEADER_TOKUGAWA 's XML anyways etc is:
	# 		<MapRefuseAttitudeThreshold>ATTITUDE_FRIENDLY</MapRefuseAttitudeThreshold>
	# Exactly the same as of LEADER_ELIZABETH, this is the field causing the key error which should map to 4 if i am not mistaken in my understanding anyways etc, not to 5
	#
	# I have done a global search and they are the only leaders with "<MapRefuseAttitudeThreshold>ATTITUDE_FRIENDLY</MapRefuseAttitudeThreshold>", so this seems most likely intended that map trading in base advciv code at least if not other mods preceding it or and base civ4 or not handle it as such (increment one level of atittude anyways etc higher than the value, to make map trading harsher, so friendly means they will always refuse map trading if i am not mistaken i assume / in my assumption anyways etc, all other leaders don't trigger a key error nor in/at this field nor in any other field, so keep as is and display it accurately as DLL handles it anyways etc) -->

	# Mapping of attitude values to their Civ4 XML constants
	DLL_ATTITUDE_MAP = {
		-1: "NONE",
		0: "ATTITUDE_FURIOUS",
		1: "ATTITUDE_ANNOYED",
		2: "ATTITUDE_CAUTIOUS",
		3: "ATTITUDE_PLEASED",
		4: "ATTITUDE_FRIENDLY",
		5: "ALWAYS??" # <!-- custom: comment-out to reproduce the error, added this value also as this seems like a purposeful valid DLL behaviour, see above for explanation or/and of my understanding of it -->
	}

	for attr in dir(info):
		if attr.startswith("get") and attr.endswith("AttitudeThreshold"):
			value = getattr(info, attr)()
			attitude_to_str = DLL_ATTITUDE_MAP[value]
			print("%s: %d (%s)" % (attr, value, attitude_to_str))

	print("\n\n==== VASSAL AND FREEDOM FIELDS (from XML order) ====")
	print("iVassalPowerModifier: %d" % info.getVassalPowerModifier())
	print("iFreedomAppreciation: %d" % info.getFreedomAppreciation())

	# <!-- custom: then we skip these (for example in/from LEADER_DEFAULTS):
	#
	# 		<FavoriteCivic>NONE</FavoriteCivic>
	# 		<FavoriteReligion>NONE</FavoriteReligion>
	# 		<Traits/>
	#
	# as we don't need them/display them in ai personality panel; then resume at fields below: -->

	print("\n\n==== FLAVORS ====")
	# <!-- custom: for flavor fields, unlike nowar (ctrl+f "attitude"), contact (ctrl+f "contact"), and memory (ctrl+f "memory") fields, it seems there are 2 occurences of methods that have "flavor" in their name if i am not mistaken (see (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\Python\Contrib\Sevopedia\__SevoPediaBuilding-gc-debug-content.txt anyways etc for details), so no need to specify a number of values to loop over as in below code if i am not mistaken -->
	for i in range(gc.getNumFlavorTypes()):
		name = gc.getFlavorTypes(i)
		value = info.getFlavorValue(i)
		print("Flavor %d (%s): %d" % (i, name, value))

	print("\n\n==== CONTACTS ====")
	# <!-- custom: 15th (0 to 13 is 14 values in total anyways etc) value has seemingly junk code (for example for leader gandhi Contact 14 (): Delay 1117701140, Rand 1110361188), stop at this last one -->
	NUM_CONTACT_TYPES_ASSESSED = 14
	for i in range(NUM_CONTACT_TYPES_ASSESSED):
		name = gc.getContactTypes(i)
		value_rand = info.getContactRand(i)
		value_delay = info.getContactDelay(i)
		print("Contact %d (%s): Rand %d, Delay %d" % (i, name, value_rand, value_delay))

	print("\n\n==== MEMORY ====")
	# <!-- custom: 38th (0 to 36 is 37 values in total anyways etc) value results in an error:
	# AttributeError: 'NoneType' object has no attribute 'getType'
	# ERR: Python function pediaJumpToLeader failed, module CvScreensInterface
	# , so stop at this last one -->
	# <!-- custom: note: here no positive/negative different memory type or index handling, as we are simply debugging and directly displaying the XML as it is, no aggregation, no adjustment of any value, anyways etc, so we can use range and loop over all NUM_MEMORY_TYPES_ASSESSED instead of using positive_or_negative_memory_indexes specifically instead depending on if memory index is of a positive or of a negative memory in sevopedia leader, so here in debugging (i.e. sevopedia_helpers py file anyways etc) we can respect and be consistent with the contact approach more strictly/reliably.. -->
	NUM_MEMORY_TYPES_ASSESSED = 37
	for i in range(NUM_MEMORY_TYPES_ASSESSED):
		name = gc.getMemoryInfo(i).getType()
		value_attitude_percent = info.getMemoryAttitudePercent(i)
		value_decay = info.getMemoryDecayRand(i)
		print("Memory %d (%s): AttitudePercent %d, Decay %d" % (i, name, value_attitude_percent, value_decay))

	print("\n\n==== NOWARATTITUDEPROBS ====")
	# <!-- custom: stop at 4 because there are only 5 attitudes (0 furious to 4 friendly anyways etc is a total of 5 values anyways etc), and trying to access the 6th non-existent in this case anyways etc value returns this error:
	# AttributeError: 'NoneType' object has no attribute 'getDescription'
	# ERR: Python function pediaJumpToLeader failed, module CvScreensInterface
	# , so stop at last value value/one  -->
	NUM_ATTITUDE_TYPES_ASSESSED = 5
	for i in range(NUM_ATTITUDE_TYPES_ASSESSED):
		name = gc.getAttitudeInfo(i).getDescription()
		value = info.getNoWarAttitudeProb(i)
		print("NoWarAttitudeProb %d (%s): %d" % (i, name, value))

	# <!-- custom: then skip all remaining fields, for example in LEADER_DEFAULTS 's XML, anyways etc:
	#
	# 		<!-- advc.104: No AdvCiv leader uses this; for mod-mods maybe. See
	# 			 UWAI_WEIGHT_LOVE_OF_PEACE in AI_Variables_GlobalDefines.xml.
	# 			 Also reduces war utility counted for "greed". -->
	# 		<iLoveOfPeace>0</iLoveOfPeace>
	# 		<UnitAIWeightModifiers/>
	# 		<ImprovementWeightModifiers/>
	# 		<DiplomacyIntroMusicPeace>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_ANCIENT</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_CLASSICAL</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_MEDIEVAL</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_RENAISSANCE</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_INDUSTRIAL</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_MODERN</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_FUTURE</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 		</DiplomacyIntroMusicPeace>
	# 		<DiplomacyMusicPeace>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_ANCIENT</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_CLASSICAL</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_MEDIEVAL</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_RENAISSANCE</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_INDUSTRIAL</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_MODERN</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 			<DiploMusicPeaceEra>
	# 				<EraType>ERA_FUTURE</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicPeaceEra>
	# 		</DiplomacyMusicPeace>
	# 		<DiplomacyIntroMusicWar>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_ANCIENT</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_CLASSICAL</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_MEDIEVAL</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_RENAISSANCE</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_INDUSTRIAL</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_MODERN</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_FUTURE</EraType>
	# 				<DiploScriptId></DiploScriptId>
	# 			</DiploMusicWarEra>
	# 		</DiplomacyIntroMusicWar>
	# 		<DiplomacyMusicWar>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_ANCIENT</EraType>
	# 				<DiploScriptId>AS2D_DIPLO_WARDRUMS_EARLY</DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_CLASSICAL</EraType>
	# 				<DiploScriptId>AS2D_DIPLO_WARDRUMS_EARLY</DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_MEDIEVAL</EraType>
	# 				<DiploScriptId>AS2D_DIPLO_WARDRUMS_MIDDLE</DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_RENAISSANCE</EraType>
	# 				<DiploScriptId>AS2D_DIPLO_WARDRUMS_MIDDLE</DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_INDUSTRIAL</EraType>
	# 				<DiploScriptId>AS2D_DIPLO_WARDRUMS_LATE</DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_MODERN</EraType>
	# 				<DiploScriptId>AS2D_DIPLO_WARDRUMS_LATE</DiploScriptId>
	# 			</DiploMusicWarEra>
	# 			<DiploMusicWarEra>
	# 				<EraType>ERA_FUTURE</EraType>
	# 				<DiploScriptId>AS2D_DIPLO_WARDRUMS_LATE</DiploScriptId>
	# 			</DiploMusicWarEra>
	# 		</DiplomacyMusicWar>
	#
	# and we have reached end of a leader info's xml if i am not mistaken, hopefully we parsed all we needed -->

	# <!-- custom: example of output for example for leader gandhi anyways etc with lineskip/extra newlines removed anyways etc for concision anyways etc, for example for Gandhi -->



	# [DEBUG] For iLeader=15, leader head info debugged as such:



	# ==== FIRST XML FIELDS PART 1 (from XML order) ====

	# iWonderConstructRand: 8
	# iBaseAttitude: 2
	# iBasePeaceWeight: 11
	# iPeaceWeightRand: 3
	# iWarmongerRespect: 0
	# iEspionageWeight: 40
	# iRefuseToTalkWarThreshold: 6
	# iNoTechTradeThreshold: 16
	# iTechTradeKnownPercent: 18
	# iMaxGoldTradePercent: 11
	# iMaxGoldPerTurnTradePercent: 10



	# ==== BBAI VICTORY WEIGHTS ====

	# Culture Victory Weight: 48
	# Space Victory Weight: 31
	# Conquest Victory Weight: -5
	# Domination Victory Weight: 0
	# Diplomacy Victory Weight: 79



	# ==== WAR XML FIELDS (from XML order) ====

	# iMaxWarRand: 440
	# iMaxWarNearbyPowerRatio: 100
	# iMaxWarDistantPowerRatio: 60
	# iMaxWarMinAdjacentLandPercent: 3
	# iLimitedWarRand: 220
	# iLimitedWarPowerRatio: 76
	# iDogpileWarRand: 110
	# iMakePeaceRand: 8
	# iDeclareWarTradeRand: 40
	# iDemandRebukedSneakProb: -8
	# iDemandRebukedWarProb: -2
	# iRazeCityProb: 0
	# iBuildUnitProb: 12



	# ==== ATTITUDE MODIFIER FIELDS (from XML order) ====

	# iBaseAttackOddsChange: 0
	# iAttackOddsChangeRand: 8
	# iWorseRankDifferenceAttitudeChange: 0
	# iBetterRankDifferenceAttitudeChange: 1
	# iCloseBordersAttitudeChange: -2
	# iLostWarAttitudeChange: -1
	# iAtWarAttitudeDivisor: -5
	# iAtWarAttitudeChangeLimit: 5
	# iAtPeaceAttitudeDivisor: 60
	# iAtPeaceAttitudeChangeLimit: 1
	# iSameReligionAttitudeChange: 1
	# iSameReligionAttitudeDivisor: 10
	# iSameReligionAttitudeChangeLimit: 4
	# iDifferentReligionAttitudeChange: -1
	# iDifferentReligionAttitudeDivisor: -15
	# iDifferentReligionAttitudeChangeLimit: -1
	# iBonusTradeAttitudeDivisor: 50
	# iBonusTradeAttitudeChangeLimit: 2
	# iOpenBordersAttitudeDivisor: 25
	# iOpenBordersAttitudeChangeLimit: 2
	# iDefensivePactAttitudeDivisor: 12
	# iDefensivePactAttitudeChangeLimit: 2
	# iShareWarAttitudeChange: 1
	# iShareWarAttitudeDivisor: 8
	# iShareWarAttitudeChangeLimit: 2
	# iFavoriteCivicAttitudeChange: 1
	# iFavoriteCivicAttitudeDivisor: 10
	# iFavoriteCivicAttitudeChangeLimit: 5



	# ==== ATTITUDE THRESHOLDS ====

	# getAdoptCivicRefuseAttitudeThreshold: 2 (ATTITUDE_CAUTIOUS)
	# getCityRefuseAttitudeThreshold: 3 (ATTITUDE_PLEASED)
	# getConvertReligionRefuseAttitudeThreshold: 1 (ATTITUDE_ANNOYED)
	# getDeclareWarRefuseAttitudeThreshold: 3 (ATTITUDE_PLEASED)
	# getDeclareWarThemRefuseAttitudeThreshold: 1 (ATTITUDE_ANNOYED)
	# getDefensivePactRefuseAttitudeThreshold: 3 (ATTITUDE_PLEASED)
	# getDemandTributeAttitudeThreshold: 2 (ATTITUDE_CAUTIOUS)
	# getHappinessBonusRefuseAttitudeThreshold: -1 (NONE)
	# getHealthBonusRefuseAttitudeThreshold: -1 (NONE)
	# getMapRefuseAttitudeThreshold: -1 (NONE)
	# getNativeCityRefuseAttitudeThreshold: 4 (ATTITUDE_FRIENDLY)
	# getNoGiveHelpAttitudeThreshold: 2 (ATTITUDE_CAUTIOUS)
	# getOpenBordersRefuseAttitudeThreshold: -1 (NONE)
	# getPermanentAllianceRefuseAttitudeThreshold: 3 (ATTITUDE_PLEASED)
	# getStopTradingRefuseAttitudeThreshold: 3 (ATTITUDE_PLEASED)
	# getStopTradingThemRefuseAttitudeThreshold: 2 (ATTITUDE_CAUTIOUS)
	# getStrategicBonusRefuseAttitudeThreshold: 1 (ATTITUDE_ANNOYED)
	# getTechRefuseAttitudeThreshold: -1 (NONE)
	# getVassalRefuseAttitudeThreshold: 1 (ATTITUDE_ANNOYED)



	# ==== VASSAL AND FREEDOM FIELDS (from XML order) ====

	# iVassalPowerModifier: -24
	# iFreedomAppreciation: 10



	# ==== FLAVORS ====

	# Flavor 0 (FLAVOR_MILITARY): 0
	# Flavor 1 (FLAVOR_RELIGION): 0
	# Flavor 2 (FLAVOR_PRODUCTION): 0
	# Flavor 3 (FLAVOR_GOLD): 0
	# Flavor 4 (FLAVOR_SCIENCE): 0
	# Flavor 5 (FLAVOR_CULTURE): 12
	# Flavor 6 (FLAVOR_GROWTH): 0
	# Flavor 7 (FLAVOR_ESPIONAGE): 0



	# ==== CONTACTS ====

	# Contact 0 (CONTACT_RELIGION_PRESSURE): Delay 50, Rand 550
	# Contact 1 (CONTACT_CIVIC_PRESSURE): Delay 50, Rand 10
	# Contact 2 (CONTACT_JOIN_WAR): Delay 20, Rand 20
	# Contact 3 (CONTACT_STOP_TRADING): Delay 20, Rand 50
	# Contact 4 (CONTACT_GIVE_HELP): Delay 50, Rand 10
	# Contact 5 (CONTACT_ASK_FOR_HELP): Delay 50, Rand 10
	# Contact 6 (CONTACT_DEMAND_TRIBUTE): Delay 50, Rand -100
	# Contact 7 (CONTACT_OPEN_BORDERS): Delay 40, Rand 10
	# Contact 8 (CONTACT_DEFENSIVE_PACT): Delay 20, Rand 80
	# Contact 9 (CONTACT_PERMANENT_ALLIANCE): Delay 20, Rand 80
	# Contact 10 (CONTACT_PEACE_TREATY): Delay 8, Rand 8
	# Contact 11 (CONTACT_TRADE_TECH): Delay 30, Rand 1
	# Contact 12 (CONTACT_TRADE_BONUS): Delay 20, Rand 1
	# Contact 13 (CONTACT_TRADE_MAP): Delay 50, Rand 20



	# ==== MEMORY ====

	# Memory 0 (MEMORY_DECLARED_WAR): AttitudePercent -300, Decay 150
	# Memory 1 (MEMORY_DECLARED_WAR_ON_FRIEND): AttitudePercent -100, Decay 120
	# Memory 2 (MEMORY_HIRED_WAR_ALLY): AttitudePercent -200, Decay 75
	# Memory 3 (MEMORY_NUKED_US): AttitudePercent -200, Decay 120
	# Memory 4 (MEMORY_NUKED_FRIEND): AttitudePercent -100, Decay 80
	# Memory 5 (MEMORY_RAZED_CITY): AttitudePercent -250, Decay 75
	# Memory 6 (MEMORY_RAZED_HOLY_CITY): AttitudePercent -200, Decay 150
	# Memory 7 (MEMORY_SPY_CAUGHT): AttitudePercent -100, Decay 40
	# Memory 8 (MEMORY_GIVE_HELP): AttitudePercent 100, Decay 150
	# Memory 9 (MEMORY_REFUSED_HELP): AttitudePercent -100, Decay 100
	# Memory 10 (MEMORY_ACCEPT_DEMAND): AttitudePercent 100, Decay 30
	# Memory 11 (MEMORY_REJECTED_DEMAND): AttitudePercent -100, Decay 90
	# Memory 12 (MEMORY_ACCEPTED_RELIGION): AttitudePercent 100, Decay 100
	# Memory 13 (MEMORY_DENIED_RELIGION): AttitudePercent -100, Decay 50
	# Memory 14 (MEMORY_ACCEPTED_CIVIC): AttitudePercent 100, Decay 100
	# Memory 15 (MEMORY_DENIED_CIVIC): AttitudePercent -100, Decay 50
	# Memory 16 (MEMORY_ACCEPTED_JOIN_WAR): AttitudePercent 100, Decay 100
	# Memory 17 (MEMORY_DENIED_JOIN_WAR): AttitudePercent -100, Decay 100
	# Memory 18 (MEMORY_ACCEPTED_STOP_TRADING): AttitudePercent 50, Decay 50
	# Memory 19 (MEMORY_DENIED_STOP_TRADING): AttitudePercent -100, Decay 50
	# Memory 20 (MEMORY_STOPPED_TRADING): AttitudePercent -100, Decay 60
	# Memory 21 (MEMORY_STOPPED_TRADING_RECENT): AttitudePercent 0, Decay 18
	# Memory 22 (MEMORY_HIRED_TRADE_EMBARGO): AttitudePercent -100, Decay 60
	# Memory 23 (MEMORY_MADE_DEMAND): AttitudePercent -100, Decay 30
	# Memory 24 (MEMORY_CANCELLED_VASSAL_AGREEMENT): AttitudePercent 0, Decay 10
	# Memory 25 (MEMORY_MADE_DEMAND_RECENT): AttitudePercent 0, Decay 20
	# Memory 26 (MEMORY_CANCELLED_OPEN_BORDERS): AttitudePercent 0, Decay 10
	# Memory 27 (MEMORY_CANCELLED_DEFENSIVE_PACT): AttitudePercent 0, Decay 10
	# Memory 28 (MEMORY_TRADED_TECH_TO_US): AttitudePercent 10, Decay 25
	# Memory 29 (MEMORY_RECEIVED_TECH_FROM_ANY): AttitudePercent 0, Decay 20
	# Memory 30 (MEMORY_VOTED_AGAINST_US): AttitudePercent -200, Decay 10
	# Memory 31 (MEMORY_VOTED_FOR_US): AttitudePercent 200, Decay 10
	# Memory 32 (MEMORY_EVENT_GOOD_TO_US): AttitudePercent 100, Decay 50
	# Memory 33 (MEMORY_EVENT_BAD_TO_US): AttitudePercent -100, Decay 50
	# Memory 34 (MEMORY_LIBERATED_CITIES): AttitudePercent 150, Decay 150
	# Memory 35 (MEMORY_INDEPENDENCE): AttitudePercent 100, Decay 30
	# Memory 36 (MEMORY_DECLARED_WAR_RECENT): AttitudePercent 0, Decay 11



	# ==== NOWARATTITUDEPROBS ====

	# NoWarAttitudeProb 0 (Furious): 24
	# NoWarAttitudeProb 1 (Annoyed): 58
	# NoWarAttitudeProb 2 (Cautious): 92
	# NoWarAttitudeProb 3 (Pleased): 114
	# NoWarAttitudeProb 4 (Friendly): 118
	# -->

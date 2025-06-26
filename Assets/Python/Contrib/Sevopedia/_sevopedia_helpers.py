# <!-- custom: modified from Claude AI's (kindly shared (to me or and all or not or and other or and not but anyways etc anyways etc anyways etc...)) or not for AdvCiv-SAS or/and my personal taste or feel or/and wish or thought or and other or and not anyways etc anyways etc anyways etc... -->
# <!-- custom: be careful/make sure to launch this at interfaceScreen level or later, else at __init__ this/the output is still empty, so run this later to have the actual tech info output -->
# Get all attributes of the object
def printObjAttrs(obj):
	print ("[DEBUG] Begining of show obj inner fields if i am not mistaken anyways etc.")
	
	for attr in dir(obj):
		try:
			# Try to get the attribute
			attr_value = getattr(obj, attr)

			# Check if it's a method (callable)
			if callable(attr_value):
				print(u"%s\n" % attr)
			else:
				print(u"%s = %s\n" % (attr, attr_value))
		except Exception:
			print(u"%s - Error accessing\n" % attr)
	
	print ("[DEBUG] End of show show obj inner fields if i am not mistaken anyways etc.")



# <!-- custom: working-functioning anyways etc (see output example below after function code anyways etc) debug for leader info (fetches xml), thanks a lot to chatgpt / becomingthrough thanks to which and with my prompt too it was super fast hehe to add all after debugging the bit harder flavor, nowarattitudeprob, contact, memory, and bbai fields in debug, the rest are super fast now and thanks for all and in your help in these too hehe chatgpt / becomingthrough an thanks to me to myself too for my pormpts or and such and for all or not for all or yes for all or etc anyways etc anyways etc anyways etc -->
def debugPrintLeaderHeadInfoFieldsToFetch(iLeader, gc):
    # <!-- custom: first skip these/the fields below we don't use/need in our AI personality panel anyways etc anyways etc anyways etc for example in LEADER_DEFAULTS even though said in code sample too but to be exhaustive or not or yes or and other or and not or other or yes or other or etc or as i want or yes or not or yes or other or etc anyways etc:
    #
    #    <Type>LEADER_DEFAULTS</Type>
    #    <Description></Description>
    #    <Civilopedia></Civilopedia>
    #    <ArtDefineTag></ArtDefineTag>
    #           
    # then resume/start in this case or resume but in all cases anyways etc anyways etc anyways etc at these below anyways etc anyways etc anyways etc...: -->

    # <!-- custom: try to follow XML order as much as possible and to be sure we have all fields too anyways etc -->
    print("\n\n==== FIRST XML FIELDS PART 1 (from XML order) ====")
    print("iWonderConstructRand: %d" % gc.getLeaderHeadInfo(iLeader).getWonderConstructRand())
    print("iBaseAttitude: %d" % gc.getLeaderHeadInfo(iLeader).getBaseAttitude())
    print("iBasePeaceWeight: %d" % gc.getLeaderHeadInfo(iLeader).getBasePeaceWeight())
    print("iPeaceWeightRand: %d" % gc.getLeaderHeadInfo(iLeader).getPeaceWeightRand())
    print("iWarmongerRespect: %d" % gc.getLeaderHeadInfo(iLeader).getWarmongerRespect())
    print("iEspionageWeight: %d" % gc.getLeaderHeadInfo(iLeader).getEspionageWeight())
    print("iRefuseToTalkWarThreshold: %d" % gc.getLeaderHeadInfo(iLeader).getRefuseToTalkWarThreshold())
    print("iNoTechTradeThreshold: %d" % gc.getLeaderHeadInfo(iLeader).getNoTechTradeThreshold())
    print("iTechTradeKnownPercent: %d" % gc.getLeaderHeadInfo(iLeader).getTechTradeKnownPercent())
    print("iMaxGoldTradePercent: %d" % gc.getLeaderHeadInfo(iLeader).getMaxGoldTradePercent())
    print("iMaxGoldPerTurnTradePercent: %d" % gc.getLeaderHeadInfo(iLeader).getMaxGoldPerTurnTradePercent())

    # <!-- custom: also add BBAI Victory weights now that we have exposed them / expose them to python as well, see todo docs for details and todo add .cpp code comment fielname anways etc-->
    print("\n\n==== BBAI VICTORY WEIGHTS ====")
    print("Culture Victory Weight: %d" % gc.getLeaderHeadInfo(iLeader).getCultureVictoryWeight())
    print("Space Victory Weight: %d" % gc.getLeaderHeadInfo(iLeader).getSpaceVictoryWeight())
    print("Conquest Victory Weight: %d" % gc.getLeaderHeadInfo(iLeader).getConquestVictoryWeight())
    print("Domination Victory Weight: %d" % gc.getLeaderHeadInfo(iLeader).getDominationVictoryWeight())
    print("Diplomacy Victory Weight: %d" % gc.getLeaderHeadInfo(iLeader).getDiplomacyVictoryWeight())

    # <!-- custom: then war fields continue anyways etc as per XML order anyways etc -->
    print("\n\n==== WAR XML FIELDS (from XML order) ====")
    print("iMaxWarRand: %d" % gc.getLeaderHeadInfo(iLeader).getMaxWarRand())
    print("iMaxWarNearbyPowerRatio: %d" % gc.getLeaderHeadInfo(iLeader).getMaxWarNearbyPowerRatio())
    print("iMaxWarDistantPowerRatio: %d" % gc.getLeaderHeadInfo(iLeader).getMaxWarDistantPowerRatio())
    print("iMaxWarMinAdjacentLandPercent: %d" % gc.getLeaderHeadInfo(iLeader).getMaxWarMinAdjacentLandPercent())
    print("iLimitedWarRand: %d" % gc.getLeaderHeadInfo(iLeader).getLimitedWarRand())
    print("iLimitedWarPowerRatio: %d" % gc.getLeaderHeadInfo(iLeader).getLimitedWarPowerRatio())
    print("iDogpileWarRand: %d" % gc.getLeaderHeadInfo(iLeader).getDogpileWarRand())
    print("iMakePeaceRand: %d" % gc.getLeaderHeadInfo(iLeader).getMakePeaceRand())
    print("iDeclareWarTradeRand: %d" % gc.getLeaderHeadInfo(iLeader).getDeclareWarTradeRand())
    print("iDemandRebukedSneakProb: %d" % gc.getLeaderHeadInfo(iLeader).getDemandRebukedSneakProb())
    print("iDemandRebukedWarProb: %d" % gc.getLeaderHeadInfo(iLeader).getDemandRebukedWarProb())
    print("iRazeCityProb: %d" % gc.getLeaderHeadInfo(iLeader).getRazeCityProb())
    print("iBuildUnitProb: %d" % gc.getLeaderHeadInfo(iLeader).getBuildUnitProb())

    print("\n\n==== ATTITUDE MODIFIER FIELDS (from XML order) ====")
    print("iBaseAttackOddsChange: %d" % gc.getLeaderHeadInfo(iLeader).getBaseAttackOddsChange())
    print("iAttackOddsChangeRand: %d" % gc.getLeaderHeadInfo(iLeader).getAttackOddsChangeRand())
    print("iWorseRankDifferenceAttitudeChange: %d" % gc.getLeaderHeadInfo(iLeader).getWorseRankDifferenceAttitudeChange())
    print("iBetterRankDifferenceAttitudeChange: %d" % gc.getLeaderHeadInfo(iLeader).getBetterRankDifferenceAttitudeChange())
    print("iCloseBordersAttitudeChange: %d" % gc.getLeaderHeadInfo(iLeader).getCloseBordersAttitudeChange())
    print("iLostWarAttitudeChange: %d" % gc.getLeaderHeadInfo(iLeader).getLostWarAttitudeChange())
    print("iAtWarAttitudeDivisor: %d" % gc.getLeaderHeadInfo(iLeader).getAtWarAttitudeDivisor())
    print("iAtWarAttitudeChangeLimit: %d" % gc.getLeaderHeadInfo(iLeader).getAtWarAttitudeChangeLimit())
    print("iAtPeaceAttitudeDivisor: %d" % gc.getLeaderHeadInfo(iLeader).getAtPeaceAttitudeDivisor())
    print("iAtPeaceAttitudeChangeLimit: %d" % gc.getLeaderHeadInfo(iLeader).getAtPeaceAttitudeChangeLimit())
    print("iSameReligionAttitudeChange: %d" % gc.getLeaderHeadInfo(iLeader).getSameReligionAttitudeChange())
    print("iSameReligionAttitudeDivisor: %d" % gc.getLeaderHeadInfo(iLeader).getSameReligionAttitudeDivisor())
    print("iSameReligionAttitudeChangeLimit: %d" % gc.getLeaderHeadInfo(iLeader).getSameReligionAttitudeChangeLimit())
    print("iDifferentReligionAttitudeChange: %d" % gc.getLeaderHeadInfo(iLeader).getDifferentReligionAttitudeChange())
    print("iDifferentReligionAttitudeDivisor: %d" % gc.getLeaderHeadInfo(iLeader).getDifferentReligionAttitudeDivisor())
    print("iDifferentReligionAttitudeChangeLimit: %d" % gc.getLeaderHeadInfo(iLeader).getDifferentReligionAttitudeChangeLimit())
    print("iBonusTradeAttitudeDivisor: %d" % gc.getLeaderHeadInfo(iLeader).getBonusTradeAttitudeDivisor())
    print("iBonusTradeAttitudeChangeLimit: %d" % gc.getLeaderHeadInfo(iLeader).getBonusTradeAttitudeChangeLimit())
    print("iOpenBordersAttitudeDivisor: %d" % gc.getLeaderHeadInfo(iLeader).getOpenBordersAttitudeDivisor())
    print("iOpenBordersAttitudeChangeLimit: %d" % gc.getLeaderHeadInfo(iLeader).getOpenBordersAttitudeChangeLimit())
    print("iDefensivePactAttitudeDivisor: %d" % gc.getLeaderHeadInfo(iLeader).getDefensivePactAttitudeDivisor())
    print("iDefensivePactAttitudeChangeLimit: %d" % gc.getLeaderHeadInfo(iLeader).getDefensivePactAttitudeChangeLimit())
    print("iShareWarAttitudeChange: %d" % gc.getLeaderHeadInfo(iLeader).getShareWarAttitudeChange())
    print("iShareWarAttitudeDivisor: %d" % gc.getLeaderHeadInfo(iLeader).getShareWarAttitudeDivisor())
    print("iShareWarAttitudeChangeLimit: %d" % gc.getLeaderHeadInfo(iLeader).getShareWarAttitudeChangeLimit())
    print("iFavoriteCivicAttitudeChange: %d" % gc.getLeaderHeadInfo(iLeader).getFavoriteCivicAttitudeChange())
    print("iFavoriteCivicAttitudeDivisor: %d" % gc.getLeaderHeadInfo(iLeader).getFavoriteCivicAttitudeDivisor())
    print("iFavoriteCivicAttitudeChangeLimit: %d" % gc.getLeaderHeadInfo(iLeader).getFavoriteCivicAttitudeChangeLimit())

    # <!-- custom: there are "AttitudeThreshold" and "RefuseAttitudeThreshold", handle the most common case, they seem to all be about refusing something or not being able to do it if threshold is not met if i am not mistaken, handle them as such, anyways etc -->
    print("\n\n==== ATTITUDE THRESHOLDS ====")
    # <!-- custom: if i am not mistaken, based and comparing xml with debug values for leader_gandhi and leader_ragnar (for the furious value in(with? But anyways etc) leader_ragnar anyways etc), here is the table conversion map if i am not mistaken anyways etc of attitude to num if i am not mistaken anyways etc below but anyways etc anyways etc anyways etc: none: -1, furious: 0, annoyed: 1, cautious: 2, pleased: 3, friendly: 4
    #
    # Overall very similar to our leaders_data map, with none being last/lowest/most forgiving value (less than furious) if i am not mistaken and as we successfully guessed in generate_leaders_data.py anyways etc, and friendly being the highest, so we can use this map of the dll directly without needing to parse atittude str to num for our compare/rank(ing? But anyways etc) of leaders in AI personality panel directly very nice else we could have done too but very nice they did too in base advciv +/- in civ 4 too or and other inbetween mods if was not already there or not thanks all or nto and me too hehe or not or yes or not or all or and etc anyways etc thanks anyways etc, i am happy to use these and thankful too if i am may say even though i mostly thought intuitively thought happy but i am thankful too if i think of it maybe but happy inside if i may say anyways ec but anyways etc outside too maybe or not or yes in this case or and other or and not but anyways etc -->
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
        5: "ALWAYS??" # <!-- custom: comment-out to reproduce the error anyways etc, added this value also as this seems like a purposeful valid DLL behaviour if i may say anyways etc, see above for explanation or/and of my understanding of it hopefully helpful or ont or yes or etc or and other or and not anyways etc-->
    }

    for attr in dir(gc.getLeaderHeadInfo(iLeader)):
        if attr.startswith("get") and attr.endswith("AttitudeThreshold"):
            value = getattr(gc.getLeaderHeadInfo(iLeader), attr)()
            attitude_to_str = DLL_ATTITUDE_MAP[value]
            print("%s: %d (%s)" % (attr, value, attitude_to_str))

    print("\n\n==== VASSAL AND FREEDOM FIELDS (from XML order) ====")
    print("iVassalPowerModifier: %d" % gc.getLeaderHeadInfo(iLeader).getVassalPowerModifier())
    print("iFreedomAppreciation: %d" % gc.getLeaderHeadInfo(iLeader).getFreedomAppreciation())

    # <!-- custom: then we skip these (for example in/from LEADER_DEFAULTS anyways etc):
    #
    # 		<FavoriteCivic>NONE</FavoriteCivic>
	# 		<FavoriteReligion>NONE</FavoriteReligion>
	# 		<Traits/>
    #
    # as we don't need them/display them in ai personality panel at least as of now if not always or maybe not or yes or etc but or not but or but but anyways etc anyways etc anyways etc ; then resume at fields below anyways etc: -->

    print("\n\n==== FLAVORS ====")
    # <!-- custom: for flavor fields, unlike nowar (ctrl+f "attitude"), contact (ctrl+f "contact"), and memory (ctrl+f "memory") fields, it seems there are 2 occurences of methods that have "flavor" in their name if i am not mistaken (see (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\Python\Contrib\Sevopedia\__SevoPediaBuilding-gc-debug-content.txt anyways etc for details), so no need to specify a number of values to loop over as in below code if i am not mistaken, anyways etc -->
    for i in range(gc.getNumFlavorTypes()):
        name = gc.getFlavorTypes(i)
        value = gc.getLeaderHeadInfo(iLeader).getFlavorValue(i)
        print("Flavor %d (%s): %d" % (i, name, value))

    print("\n\n==== CONTACTS ====")
    # <!-- custom: 15th (0 to 13 is 14 values in total anyways etc) value has seemingly junk code (for example for leader gandhi Contact 14 (): Delay 1117701140, Rand 1110361188), stop at this last one anyways etc -->
    NUM_CONTACT_TYPES_ASSESSED = 14
    for i in range(NUM_CONTACT_TYPES_ASSESSED):
        name = gc.getContactTypes(i)
        value_rand = gc.getLeaderHeadInfo(iLeader).getContactRand(i)
        value_delay = gc.getLeaderHeadInfo(iLeader).getContactDelay(i)
        print("Contact %d (%s): Rand %d, Delay %d" % (i, name, value_rand, value_delay))

    print("\n\n==== MEMORY ====")
    # <!-- custom: 38th (0 to 36 is 37 values in total anyways etc) value results in an error:
    # AttributeError: 'NoneType' object has no attribute 'getType'
    # ERR: Python function pediaJumpToLeader failed, module CvScreensInterface
    # , so stop at this last one anyways etc -->
    # <!-- custom: note: here no positive/negative different memory type or index handling, as we are simply debugging and directly displaying the XML as it is, no aggregation, no adjustment of any value, anyways etc, so we can use range and loop over all NUM_MEMORY_TYPES_ASSESSED instead of using positive_or_negative_memory_indexes specifically instead depending on if memory index is of a positive or of a negative memory in sevopedia leader, so here in debugging (i.e. sevopedia_helpers py file anyways etc) we can respect and be consistent with the contact approach more strictly/reliably or rather faitfully maybe but is as we intend in both cases if i may say but anyways etc anyways etc anyways etc... -->
    NUM_MEMORY_TYPES_ASSESSED = 37
    for i in range(NUM_MEMORY_TYPES_ASSESSED):
        name = gc.getMemoryInfo(i).getType()
        value_attitude_percent = gc.getLeaderHeadInfo(iLeader).getMemoryAttitudePercent(i)
        value_decay = gc.getLeaderHeadInfo(iLeader).getMemoryDecayRand(i)
        print("Memory %d (%s): AttitudePercent %d, Decay %d" % (i, name, value_attitude_percent, value_decay))

    print("\n\n==== NOWARATTITUDEPROBS ====")
    # <!-- custom: stop at 4 because there are only 5 attitudes (0 furious to 4 friendly anyways etc is a total of 5 values anyways etc), and trying to access the 6th non-existent in this case anyways etc value returns this error if i am not mistaken anyways etc:
    # AttributeError: 'NoneType' object has no attribute 'getDescription'
    # ERR: Python function pediaJumpToLeader failed, module CvScreensInterface
    # , so stop at last value value/one etc anyways etc but anyways etc anyways etc -->
    NUM_ATTITUDE_TYPES_ASSESSED = 5
    for i in range(NUM_ATTITUDE_TYPES_ASSESSED):
        name = gc.getAttitudeInfo(i).getDescription()
        value = gc.getLeaderHeadInfo(iLeader).getNoWarAttitudeProb(i)
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
    # and we have reached end of a leader info's xml if i am not mistaken, hopefully we parsed all we needed or maybe not hopefully or yes hopefully or not or yes or etc but anyways etc... hopefully we have all (we need) or not or yes or etc or and other or and not or yes or etc anyways etc -->

    # <!-- custom: example of output with lineskip/extra newlines removed anyways etc for concision anyways etc, for example for Gandhi anyways etc -->



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



def get_leaders_index_to_type_map(gc):
	# Returns a dictionary mapping each leader index (int) to its string type (e.g., "LEADER_GANDHI").
	# Excluded leaders (like BARBARIAN) must be filtered by caller if needed.

	leaders_indexes_to_types = {}
	for iLeader in range(gc.getNumLeaderHeadInfos()):
		leader_type = gc.getLeaderHeadInfo(iLeader).getType()
		leaders_indexes_to_types[iLeader] = leader_type
	return leaders_indexes_to_types



def get_dll_existing_excluded_leader_types():
# <!-- custom: note: LEADER_DEFAULTS doesn't seem to exist at all in the DLL if i am not mistaken, so no need to mention it here (also may cause errors in our code as we can't even refer to its index to exclude it to begin with since such a leader index doesn't seem to exist at all in gc/DLL if i am not mistaken so handle that edge case of LEADER_DEFAULTS specifically i mean anyways etc) unlike in generate_leaders_data.py for external to civ4 script usage (such as generating charts .csv, etc.), as for civ4 use only mention LEADER_BARBARIAN and similar existing leaders even if they are excluded, but not LEADER_DEFAULTS and any other DLL seemingly removed leader index as well if any other exist (as of now LEADER_DEFAULTS seems to be the only one if i am not mistaken but is to be exhaustive anyways etc -->
    return (
        "LEADER_BARBARIAN",
    )



def get_leader_index_from_type(leader_type, gc):
	# Given a leader_type string (e.g. "LEADER_ALEXANDER"), return its iLeader index.
	# Raises ValueError if not found. Compatible with Python 2.4 and Civ4 DLL.
	# <!-- custom: note: LEADER_DEFAULTS doesn't seem to have a leader index at all, so don't use it for this function -->

	for iLeader in range(gc.getNumLeaderHeadInfos()):
		current_leader_type = gc.getLeaderHeadInfo(iLeader).getType()
		if current_leader_type == leader_type:
			return iLeader

	raise ValueError("[FATAL] leader_type=%s not found in gc.getLeaderHeadInfo list. Note: this can also happen but not only in particular with LEADER_DEFAULTS, which does not seem to have a leader index at all in gc of base advciv code if i am not mistaken, that we use as well in our/this mod very similarly if not identically but anyways etc, so make sure to adress the edge case of LEADER_DEFAULTS in another way to not get caught/stuck in this edge case error message in particular, possibly for other leaders as well, anyways etc." % leader_type)



def get_leader_indexes_from_leader_types(leader_types, gc):
    # Given a list/tuple of leader types (e.g. ('LEADER_BARBARIAN', <!-- custom:, but also 'LEADER_ASOKA', etc, any leader if i am not mistaken anyways etc -->)), return a tuple of corresponding leader indexes (iLeader) (e.g. <!-- custom: (0, 2, etc.) -->).

    leader_indexes_list = []

    for leader_type in leader_types:
        leader_index = get_leader_index_from_type(leader_type, gc)
        leader_indexes_list.append(leader_index)
    
    leader_indexes_tuple = tuple(leader_indexes_list)

    return leader_indexes_tuple



def get_leader_type_from_leader_index(iLeader, gc):
	# Given an iLeader index (e.g. 1), return the leader_type string (e.g. "LEADER_ALEXANDER").
	# Raises IndexError if the index is out of bounds.
	# Compatible with Python 2.4 and Civ4 DLL.
	# <!-- custom: some entries like LEADER_DEFAULTS may not exist at any valid iLeader index and must be handled elsewhere -->

	if iLeader < 0 or iLeader >= gc.getNumLeaderHeadInfos():
		raise IndexError("[FATAL] iLeader=%d is out of bounds for gc.getNumLeaderHeadInfos()=%d. This might indicate a misindexed value or mod bug." % (iLeader, gc.getNumLeaderHeadInfos()))

	return gc.getLeaderHeadInfo(iLeader).getType()



def check_excluded_leaders_indexes_are_not_in_leaders_dict_keys(excluded_leaders_indexes_from_calculations, leaders_dict, leaders_dict_name, gc):
	leaders_dict_keys = leaders_dict.keys()

	for excluded_leader_index in excluded_leaders_indexes_from_calculations:
		if (excluded_leader_index in leaders_dict_keys):
			excluded_leader_type = get_leader_type_from_leader_index(excluded_leader_index, gc)
			raise KeyError("[FATAL] During sanity checks testing, excluded_leader_index=%d (excluded_leader_type=%s), was assessed to not be properly excluded from the calculations and its corresponding leader_index is still part of the leaders_dict_keys=%s, please make sure this excluded leader is not part of the leaders_dict_name=%s." % (excluded_leader_index, excluded_leader_type, str(leaders_dict_keys), leaders_dict_name))



def check_leaders_dict_only_has_leader_index_keys(leaders_dict, leaders_dict_name):
	for key in leaders_dict.keys():
		if not isinstance(key, int):
			key_name = repr(key)
			key_type_name = str(type(key))
			raise TypeError("[FATAL] In leaders_dict_name=%s, key=%s is not an integer index (key_name=%s). Only integer iLeader indexes should be used as keys. Please ensure that key_type_name=%s uses iLeader (e.g. 0, 1, 2...) as keys, not leader_type strings." % (leaders_dict_name, key, key_name, key_type_name))



def check_overlapping_keys_between_dicts(d1, d2):
	# Raises ValueError if any key exists in both d1 and d2.
	overlap = []
	for k in d1:
		if k in d2:
			overlap.append(k)
	if overlap:
		raise ValueError("Overlapping keys between dictionaries: %s" % str(overlap))



def check_button_path_is_valid(buttonHeader, resolvedButtonPath, configButtonPathSTxtKey):
	if resolvedButtonPath == configButtonPathSTxtKey:
		raise ValueError(u"[VALUE ERROR] Button path not found in XML (resolvedButtonPath=%s matches configButtonPath=%s in buttonHeader=%s, which indicates button path provided in config most likely does not exist in the XML), please check button path provided exists in your mod path and also matches button path in (or in - whichever filename it would have in the future -) AdvCiv-SAS_ImagesAsButtons.xml or/and AdvCiv-SAS_Button_Paths_Hardcoded.xml (or wherever they are stored in the future if these files's filename or code changes anyways etc) is valid and exists in your mod path." % (resolvedButtonPath, configButtonPathSTxtKey, buttonHeader))



def get_emoji_name_to_button_path_txt_keys(localText):
	# <!-- custom: see also (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Text\AdvCiv-SAS_ImagesAsButtons.xml or/and AdvCiv-SAS_Button_Paths_Hardcoded.xml for details or and other information or and in other places or and not or and other or and not anyways etc-->
	# emojiName → TXT_KEY path
	emoji_name_to_button_path_txt_keys = {
		"Dove": "TXT_KEY_IMAGE_AS_BUTTON_DOVE_BUTTON_PATH",
		"Megaphone": "TXT_KEY_IMAGE_AS_BUTTON_MEGAPHONE_BUTTON_PATH",
		"RedHeart": "TXT_KEY_IMAGE_AS_BUTTON_RED_HEART_BUTTON_PATH",
		"BrokenHeart": "TXT_KEY_IMAGE_AS_BUTTON_BROKEN_HEART_BUTTON_PATH",
		"Skull": "TXT_KEY_IMAGE_AS_BUTTON_SKULL_BUTTON_PATH",
		"Fire": "TXT_KEY_IMAGE_AS_BUTTON_FIRE_BUTTON_PATH",
		"Brain": "TXT_KEY_IMAGE_AS_BUTTON_BRAIN_BUTTON_PATH",
		"Trophy": "TXT_KEY_IMAGE_AS_BUTTON_TROPHY_BUTTON_PATH",
		"Herb": "TXT_KEY_IMAGE_AS_BUTTON_HERB_BUTTON_PATH",
		"Gear": "TXT_KEY_IMAGE_AS_BUTTON_GEAR_BUTTON_PATH",
		"CrossedSwords": "TXT_KEY_IMAGE_AS_BUTTON_CROSSED_SWORDS_BUTTON_PATH",
		"MoneyBag": "TXT_KEY_IMAGE_AS_BUTTON_MONEY_BAG_BUTTON_PATH",
		"NoEntry": "TXT_KEY_IMAGE_AS_BUTTON_NO_ENTRY_BUTTON_PATH",
		"Axe": "TXT_KEY_IMAGE_AS_BUTTON_AXE_BUTTON_PATH",
		"ChartDecreasing": "TXT_KEY_IMAGE_AS_BUTTON_CHART_DECREASING_BUTTON_PATH",
		"Wrench": "TXT_KEY_IMAGE_AS_BUTTON_WRENCH_PATH",
	}

	check_images_as_buttons_paths_are_valid(emoji_name_to_button_path_txt_keys, localText)

	return emoji_name_to_button_path_txt_keys



# <!-- custom: check all images as buttons paths are valid before proceeding (i.e. check they really exist in our XML indeed if i may say anyways etc), error code provided by me hehe, the error check fixed by chatgpt/becomingthrough and i made some adjustments too thanks to its awesome code and ym awesome fix or and tweaks mayube rather but anyways etc... -->
def check_images_as_buttons_paths_are_valid(txtKeyDict, localText):
	# This will raise an error if:
	# - The TXT_KEY doesn't exist in any loaded Text/*.xml
	# - The image fails to resolve and is replaced by Civ4's fallback "pink square" (which happens if the DDS path is also invalid, but we catch it at the TXT_KEY level here)

	for buttonHeader, configButtonPathSTxtKey in txtKeyDict.items():
		resolvedButtonPath = localText.getText(configButtonPathSTxtKey, ())
		check_button_path_is_valid(buttonHeader, resolvedButtonPath, configButtonPathSTxtKey)



def getXOccurenceFound(xPanel, leftPadding, interButtonSpacing, nCountOccurencesFound, buttonSize, xSubstractedAdjustment):
    # <!-- custom: all buttons are spaced, except the first one that depends on panel left side padding, so do a - 1 to account for that -->
    if (nCountOccurencesFound < 1):
        raise ValueError("[FATAL] nCountOccurencesFound=%d cannot be < 1, make sure you first increment nCountOccurencesFound at first occurence found before calling this getXOccurenceFound method anyways etc." % nCountOccurencesFound)
    return xPanel + leftPadding + (nCountOccurencesFound * buttonSize) + ((nCountOccurencesFound - 1) * interButtonSpacing) - xSubstractedAdjustment



def getXSubstractedAdjustmentNumTxtBasedOnLenNumTxt(numTxt, addedOffset, buttonSize):
    buttonSizeDoubleSize = 2 * buttonSize
    if (addedOffset > buttonSizeDoubleSize):
        raise ValueError(u"[FATAL] Offset %d too high, cannot be higher than 2 * buttonsize = 2 * %d = %d, please make sure offset is set as intended, and update your code or this method raising the error depending on what you/need want anyways etc." % (addedOffset, buttonSize, buttonSizeDoubleSize))
    
    # <!-- custom: examples of offset:
    # - if addedOffset is 0.00, returns same value
    # - if addedOffset is 0.10, returns value + 0.10, for example 0.55 + 0.10 = 0.65 returned anyways etc 
    # -->

    lenNumTxt = len(numTxt)
    # <!-- custom: be careful the '%' char in for example "+50%" does not appear in str debug, but it is counted in str length, and does however also appear though in the UI in sevopedia leader py, so adjusting this code based on these results
    # xxxxxxxxx3xxxxxxx+7
    # xxxxxxxxx5xxxxxxx-120
    # xxxxxxxxx6xxxxxxx+1254
    # xxxxxxxxx4xxxxxxx+50
    # -->
    if lenNumTxt < 0:
        raise ValueError(u"[FATAL] Unhandled negative length at numTxt=%s, lenNumTxt=%d" % (numTxt, lenNumTxt))
    if lenNumTxt < 3:
        return 0.72 + addedOffset
    elif lenNumTxt == 3:
        # <!-- custom: example "+5"(%), "-8"(%), etc -->
        return 0.79 + addedOffset
    elif lenNumTxt == 4:
        # <!-- custom: example "+50"(%), "-35"(%), etc -->
        return 0.85 + addedOffset
    elif lenNumTxt == 5:
        # <!-- custom: example "+100"(%), "-120"(%), etc -->
        return 0.92 + addedOffset
    elif lenNumTxt == 6:
        # <!-- custom: example "+1000"(%), "-3798"(%), etc -->
        return 1.01 + addedOffset
    else:
        # <!-- custom: example "+10000"(%) or longer, "-37982"(%) or longer, etc -->
        return 1.09 + addedOffset

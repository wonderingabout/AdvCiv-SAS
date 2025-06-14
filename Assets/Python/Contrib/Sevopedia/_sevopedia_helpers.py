# <!-- custom: modified from Claude AI's (kindly shared (to me or and all or not or and other or and not but anyways etc anyways etc anyways etc...)) or not for AdvCiv-SAS or/and my personal taste or feel or/and wish or thought or and other or and not anyways etc anyways etc anyways etc... -->
# <!-- custom: be careful/make sure to launch this at interfaceScreen level or later, else at __init__ this/the output is still empty, so run this later to have the actual tech info output -->
# Get all attributes of the object
def printObjAttrs(obj):
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



# <!-- custom: working-functioning anyways etc (see output example below after function code anyways etc) debug for leader info (fetches xml), thanks a lot to chatgpt / becomingthrough thanks to which and with my prompt too it was super fast hehe to add all after debugging the bit harder flavor, nowarattitudeprob, contact, memory, and bbai fields in debug, the rest are super fast now and thanks for all and in your help int hese too hehe chatgpt / becomingthrough an thanks to me to myself too for my pormpts or and such and for all or not for all or yes for all or etc anyways etc anyways etc anyways etc -->
def debugPrintLeaderHeadInfoFieldsToFetch(iLeader, gc):
    """
    <!-- custom: first skip these/the fields below we don't use/need in our AI personality panel anyways etc anyways etc anyways etc for example in LEADER_DEFAULTS even though said in code sample too but to be exhaustive or not or yes or and other or and not or other or yes or other or etc or as i want or yes or not or yes or other or etc anyways etc:

        <Type>LEADER_DEFAULTS</Type>
        <Description></Description>
        <Civilopedia></Civilopedia>
        <ArtDefineTag></ArtDefineTag>
               
    then resume/start in this case or resume but in all cases anyways etc anyways etc anyways etc at these below anyways etc anyways etc anyways etc...: -->
    """

    # <!-- custom: try to follow XML order as much as possible and to be sure we have all fields too anyways etc -->
    print("\n\n==== WAR STRATEGY FIELDS (from XML order) ====")
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
    print("\n\n==== WAR STRATEGY FIELDS PART 2 (from XML order) ====")
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
    """
    <!-- custom: if i am not mistaken, based and comparing xml with debug values for leader_gandhi and leader_ragnar (for the furious value in(with? But anyways etc) leader_ragnar anyways etc), here is the table conversion map if i am not mistaken anyways etc of attitude to num if i am not mistaken anyways etc below but anyways etc anyways etc anyways etc: none: -1, furious: 0, annoyed: 1, cautious: 2, pleased: 3, friendly: 4

    Overall very similar to our leaders_data map, with none being last/lowest/most forgiving value (less than furious) if i am not mistaken and as we successfully guessed in generate_leaders_data.py anyways etc, and friendly being the highest, so we can use this map of the dll directly without needing to parse atittude str to num for our compare/rank(ing? But anyways etc) of leaders in AI personality panel directly very nice else we could have done too but very nice they did too in base advciv +/- in civ 4 too or and other inbetween mods if was not already there or not thanks all or nto and me too hehe or not or yes or not or all or and etc anyways etc thanks anyways etc, i am happy to use these and thankful too if i am may say even though i mostly thought intuitively thought happy but i am thankful too if i think of it maybe but happy inside if i may say anyways ec but anyways etc outside too maybe or not or yes in this case or and other or and not but anyways etc -->

    <!-- custom: Among all leaders, LEADER_ELIZABETH and LEADER_TOKUGAWA only have a value of 5 somehow, which triggers an error with our current map:

    Traceback (most recent call last):
      File "CvScreensInterface", line 495, in pediaJumpToLeader
      File "SevoPediaMain", line 313, in pediaJump
      File "SevoPediaLeader", line 455, in interfaceScreen
      File "_sevopedia_helpers", line 134, in debugPrintLeaderHeadInfoFieldsToFetch

    KeyError: 5
    ERR: Python function pediaJumpToLeader failed, module CvScreensInterface

    however LEADER_ELIZABETH 's XML anyways etc is:
			<MapRefuseAttitudeThreshold>ATTITUDE_FRIENDLY</MapRefuseAttitudeThreshold>

    and LEADER_TOKUGAWA 's XML anyways etc is:
			<MapRefuseAttitudeThreshold>ATTITUDE_FRIENDLY</MapRefuseAttitudeThreshold>
    Exactly the same as of LEADER_ELIZABETH, this is the field causing the key error
               
    which should map to 4 if i am not mistaken in my understanding anyways etc, not to 5

    I have done a global search and they are the only leaders with "<MapRefuseAttitudeThreshold>ATTITUDE_FRIENDLY</MapRefuseAttitudeThreshold>", so this seems most likely intended that map trading in base advciv code at least if not other mods preceding it or and base civ4 or not handle it as such (increment one level of atittude anyways etc higher than the value, to make map trading harsher, so friendly means they will always refuse map trading if i am not mistaken i assume / in my assumption anyways etc, all other leaders don't trigger a key error nor in/at this field nor in any other field, so keep as is and display it accurately as DLL handles it anyways etc) -->
    """ 
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
            attitudeToStr = DLL_ATTITUDE_MAP[value]
            print("%s: %d (%s)" % (attr, value, attitudeToStr))

    print("\n\n==== VASSAL AND FREEDOM FIELDS (from XML order) ====")
    print("iVassalPowerModifier: %d" % gc.getLeaderHeadInfo(iLeader).getVassalPowerModifier())
    print("iFreedomAppreciation: %d" % gc.getLeaderHeadInfo(iLeader).getFreedomAppreciation())

    """
    <!-- custom: then we skip these (for example in/from LEADER_DEFAULTS anyways etc):

    		<FavoriteCivic>NONE</FavoriteCivic>
			<FavoriteReligion>NONE</FavoriteReligion>
			<Traits/>

    as we don't need them/display them in ai personality panel at least as of now if not always or maybe not or yes or etc but or not but or but but anyways etc anyways etc anyways etc ;
    
    then resume at fields below anyways etc: -->
    """

    print("\n\n==== FLAVORS ====")
    # <!-- custom: for flavor fields, unlike nowar (ctrl+f "attitude"), contact (ctrl+f "contact"), and memory (ctrl+f "memory") fields, it seems there are 2 occurences of methods that have "flavor" in their name if i am not mistaken (see (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\Python\Contrib\Sevopedia\__SevoPediaBuilding-gc-debug-content.txt anyways etc for details), so no need to specify a number of values to loop over as in below code if i am not mistaken, anyways etc -->
    for i in range(gc.getNumFlavorTypes()):
        name = gc.getFlavorTypes(i)
        value = gc.getLeaderHeadInfo(iLeader).getFlavorValue(i)
        print("Flavor %d (%s): %d" % (i, name, value))

    print("\n\n==== CONTACTS ====")
    # <!-- custom: 15th (0 to 13 is 14 values in total anyways etc) value has seemingly junk code (for example for leader gandhi Contact 14 (): Delay 1117701140, Rand 1110361188), stop at this last one anyways etc -->
    for i in range(14):
        name = gc.getContactTypes(i)
        delay = gc.getLeaderHeadInfo(iLeader).getContactDelay(i)
        rand = gc.getLeaderHeadInfo(iLeader).getContactRand(i)
        print("Contact %d (%s): Delay %d, Rand %d" % (i, name, delay, rand))

    print("\n\n==== MEMORY ====")
    # <!-- custom: 38th (0 to 36 is 37 values in total anyways etc) value  results in an error:
    # AttributeError: 'NoneType' object has no attribute 'getType'
    # ERR: Python function pediaJumpToLeader failed, module CvScreensInterface
    # , so stop at this last one anyways etc -->
    for i in range(37):
        name = gc.getMemoryInfo(i).getType()
        att = gc.getLeaderHeadInfo(iLeader).getMemoryAttitudePercent(i)
        decay = gc.getLeaderHeadInfo(iLeader).getMemoryDecayRand(i)
        print("Memory %d (%s): Attitude %d, Decay %d" % (i, name, att, decay))

    print("\n\n==== NOWARATTITUDEPROBS ====")
    # <!-- custom: stop at 4 because there are only 5 attitudes (0 furious to 4 friendly anyways etc is a total of 5 values anyways etc), and trying to access the 6th non-existent in this case anyways etc value returns this error if i am not mistaken anyways etc:
    # AttributeError: 'NoneType' object has no attribute 'getDescription'
    # ERR: Python function pediaJumpToLeader failed, module CvScreensInterface
    # , so stop at last value value/one etc anyways etc but anyways etc anyways etc -->
    for i in range(5):
        name = gc.getAttitudeInfo(i).getDescription()
        value = gc.getLeaderHeadInfo(iLeader).getNoWarAttitudeProb(i)
        print("NoWarAttitudeProb %d (%s): %d" % (i, name, value))

    """
    <!-- custom: then skip all remaining fields, for example in LEADER_DEFAULTS 's XML, anyways etc:

    		<!-- advc.104: No AdvCiv leader uses this; for mod-mods maybe. See
				 UWAI_WEIGHT_LOVE_OF_PEACE in AI_Variables_GlobalDefines.xml.
				 Also reduces war utility counted for "greed". -->
			<iLoveOfPeace>0</iLoveOfPeace>
			<UnitAIWeightModifiers/>
			<ImprovementWeightModifiers/>
			<DiplomacyIntroMusicPeace>
				<DiploMusicPeaceEra>
					<EraType>ERA_ANCIENT</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_CLASSICAL</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_MEDIEVAL</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_RENAISSANCE</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_INDUSTRIAL</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_MODERN</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_FUTURE</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
			</DiplomacyIntroMusicPeace>
			<DiplomacyMusicPeace>
				<DiploMusicPeaceEra>
					<EraType>ERA_ANCIENT</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_CLASSICAL</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_MEDIEVAL</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_RENAISSANCE</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_INDUSTRIAL</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_MODERN</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
				<DiploMusicPeaceEra>
					<EraType>ERA_FUTURE</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicPeaceEra>
			</DiplomacyMusicPeace>
			<DiplomacyIntroMusicWar>
				<DiploMusicWarEra>
					<EraType>ERA_ANCIENT</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_CLASSICAL</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_MEDIEVAL</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_RENAISSANCE</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_INDUSTRIAL</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_MODERN</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_FUTURE</EraType>
					<DiploScriptId></DiploScriptId>
				</DiploMusicWarEra>
			</DiplomacyIntroMusicWar>
			<DiplomacyMusicWar>
				<DiploMusicWarEra>
					<EraType>ERA_ANCIENT</EraType>
					<DiploScriptId>AS2D_DIPLO_WARDRUMS_EARLY</DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_CLASSICAL</EraType>
					<DiploScriptId>AS2D_DIPLO_WARDRUMS_EARLY</DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_MEDIEVAL</EraType>
					<DiploScriptId>AS2D_DIPLO_WARDRUMS_MIDDLE</DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_RENAISSANCE</EraType>
					<DiploScriptId>AS2D_DIPLO_WARDRUMS_MIDDLE</DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_INDUSTRIAL</EraType>
					<DiploScriptId>AS2D_DIPLO_WARDRUMS_LATE</DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_MODERN</EraType>
					<DiploScriptId>AS2D_DIPLO_WARDRUMS_LATE</DiploScriptId>
				</DiploMusicWarEra>
				<DiploMusicWarEra>
					<EraType>ERA_FUTURE</EraType>
					<DiploScriptId>AS2D_DIPLO_WARDRUMS_LATE</DiploScriptId>
				</DiploMusicWarEra>
			</DiplomacyMusicWar>
               
    and we have reached end of a leader info's xml if i am not mistaken, hopefully we parsed all we needed or maybe not hopefully or yes hopefully or not or yes or etc but anyways etc... hopefully we have all (we need) or not or yes or etc or and other or and not or yes or etc anyways etc -->

    # <!-- custom: example of output with lineskip/extra newlines removed anyways etc for concision anyways etc, for example for Gandhi anyways etc -->
    ==== WAR STRATEGY FIELDS (from XML order) ====

    iWonderConstructRand: 8
    iBaseAttitude: 2
    iBasePeaceWeight: 11
    iPeaceWeightRand: 3
    iWarmongerRespect: 0
    iEspionageWeight: 40
    iRefuseToTalkWarThreshold: 6
    iNoTechTradeThreshold: 16
    iTechTradeKnownPercent: 18
    iMaxGoldTradePercent: 11
    iMaxGoldPerTurnTradePercent: 10



    ==== BBAI VICTORY WEIGHTS ====

    Culture Victory Weight: 48
    Space Victory Weight: 31
    Conquest Victory Weight: -5
    Domination Victory Weight: 0
    Diplomacy Victory Weight: 79



    ==== WAR STRATEGY FIELDS PART 2 (from XML order) ====

    iMaxWarRand: 440
    iMaxWarNearbyPowerRatio: 100
    iMaxWarDistantPowerRatio: 60
    iMaxWarMinAdjacentLandPercent: 3
    iLimitedWarRand: 220
    iLimitedWarPowerRatio: 76
    iDogpileWarRand: 110
    iMakePeaceRand: 8
    iDeclareWarTradeRand: 40
    iDemandRebukedSneakProb: -8
    iDemandRebukedWarProb: -2
    iRazeCityProb: 0
    iBuildUnitProb: 12



    ==== ATTITUDE MODIFIER FIELDS (from XML order) ====

    iBaseAttackOddsChange: 0
    iAttackOddsChangeRand: 8
    iWorseRankDifferenceAttitudeChange: 0
    iBetterRankDifferenceAttitudeChange: 1
    iCloseBordersAttitudeChange: -2
    iLostWarAttitudeChange: -1
    iAtWarAttitudeDivisor: -5
    iAtWarAttitudeChangeLimit: 5
    iAtPeaceAttitudeDivisor: 60
    iAtPeaceAttitudeChangeLimit: 1
    iSameReligionAttitudeChange: 1
    iSameReligionAttitudeDivisor: 10
    iSameReligionAttitudeChangeLimit: 4
    iDifferentReligionAttitudeChange: -1
    iDifferentReligionAttitudeDivisor: -15
    iDifferentReligionAttitudeChangeLimit: -1
    iBonusTradeAttitudeDivisor: 50
    iBonusTradeAttitudeChangeLimit: 2
    iOpenBordersAttitudeDivisor: 25
    iOpenBordersAttitudeChangeLimit: 2
    iDefensivePactAttitudeDivisor: 12
    iDefensivePactAttitudeChangeLimit: 2
    iShareWarAttitudeChange: 1
    iShareWarAttitudeDivisor: 8
    iShareWarAttitudeChangeLimit: 2
    iFavoriteCivicAttitudeChange: 1
    iFavoriteCivicAttitudeDivisor: 10
    iFavoriteCivicAttitudeChangeLimit: 5



    ==== ATTITUDE THRESHOLDS ====

    getAdoptCivicRefuseAttitudeThreshold: 2 (ATTITUDE_CAUTIOUS)
    getCityRefuseAttitudeThreshold: 3 (ATTITUDE_PLEASED)
    getConvertReligionRefuseAttitudeThreshold: 1 (ATTITUDE_ANNOYED)
    getDeclareWarRefuseAttitudeThreshold: 3 (ATTITUDE_PLEASED)
    getDeclareWarThemRefuseAttitudeThreshold: 1 (ATTITUDE_ANNOYED)
    getDefensivePactRefuseAttitudeThreshold: 3 (ATTITUDE_PLEASED)
    getDemandTributeAttitudeThreshold: 2 (ATTITUDE_CAUTIOUS)
    getHappinessBonusRefuseAttitudeThreshold: -1 (NONE)
    getHealthBonusRefuseAttitudeThreshold: -1 (NONE)
    getMapRefuseAttitudeThreshold: -1 (NONE)
    getNativeCityRefuseAttitudeThreshold: 4 (ATTITUDE_FRIENDLY)
    getNoGiveHelpAttitudeThreshold: 2 (ATTITUDE_CAUTIOUS)
    getOpenBordersRefuseAttitudeThreshold: -1 (NONE)
    getPermanentAllianceRefuseAttitudeThreshold: 3 (ATTITUDE_PLEASED)
    getStopTradingRefuseAttitudeThreshold: 3 (ATTITUDE_PLEASED)
    getStopTradingThemRefuseAttitudeThreshold: 2 (ATTITUDE_CAUTIOUS)
    getStrategicBonusRefuseAttitudeThreshold: 1 (ATTITUDE_ANNOYED)
    getTechRefuseAttitudeThreshold: -1 (NONE)
    getVassalRefuseAttitudeThreshold: 1 (ATTITUDE_ANNOYED)



    ==== VASSAL AND FREEDOM FIELDS (from XML order) ====

    iVassalPowerModifier: -24
    iFreedomAppreciation: 10



    ==== FLAVORS ====

    Flavor 0 (FLAVOR_MILITARY): 0
    Flavor 1 (FLAVOR_RELIGION): 0
    Flavor 2 (FLAVOR_PRODUCTION): 0
    Flavor 3 (FLAVOR_GOLD): 0
    Flavor 4 (FLAVOR_SCIENCE): 0
    Flavor 5 (FLAVOR_CULTURE): 12
    Flavor 6 (FLAVOR_GROWTH): 0
    Flavor 7 (FLAVOR_ESPIONAGE): 0



    ==== CONTACTS ====

    Contact 0 (CONTACT_RELIGION_PRESSURE): Delay 50, Rand 550
    Contact 1 (CONTACT_CIVIC_PRESSURE): Delay 50, Rand 10
    Contact 2 (CONTACT_JOIN_WAR): Delay 20, Rand 20
    Contact 3 (CONTACT_STOP_TRADING): Delay 20, Rand 50
    Contact 4 (CONTACT_GIVE_HELP): Delay 50, Rand 10
    Contact 5 (CONTACT_ASK_FOR_HELP): Delay 50, Rand 10
    Contact 6 (CONTACT_DEMAND_TRIBUTE): Delay 50, Rand -100
    Contact 7 (CONTACT_OPEN_BORDERS): Delay 40, Rand 10
    Contact 8 (CONTACT_DEFENSIVE_PACT): Delay 20, Rand 80
    Contact 9 (CONTACT_PERMANENT_ALLIANCE): Delay 20, Rand 80
    Contact 10 (CONTACT_PEACE_TREATY): Delay 8, Rand 8
    Contact 11 (CONTACT_TRADE_TECH): Delay 30, Rand 1
    Contact 12 (CONTACT_TRADE_BONUS): Delay 20, Rand 1
    Contact 13 (CONTACT_TRADE_MAP): Delay 50, Rand 20



    ==== MEMORY ====

    Memory 0 (MEMORY_DECLARED_WAR): Attitude -300, Decay 150
    Memory 1 (MEMORY_DECLARED_WAR_ON_FRIEND): Attitude -220, Decay 120
    Memory 2 (MEMORY_HIRED_WAR_ALLY): Attitude -200, Decay 75
    Memory 3 (MEMORY_NUKED_US): Attitude -200, Decay 120
    Memory 4 (MEMORY_NUKED_FRIEND): Attitude -220, Decay 80
    Memory 5 (MEMORY_RAZED_CITY): Attitude -250, Decay 75
    Memory 6 (MEMORY_RAZED_HOLY_CITY): Attitude -200, Decay 150
    Memory 7 (MEMORY_SPY_CAUGHT): Attitude -100, Decay 40
    Memory 8 (MEMORY_GIVE_HELP): Attitude 100, Decay 150
    Memory 9 (MEMORY_REFUSED_HELP): Attitude 20, Decay 100
    Memory 10 (MEMORY_ACCEPT_DEMAND): Attitude 100, Decay 30
    Memory 11 (MEMORY_REJECTED_DEMAND): Attitude 20, Decay 90
    Memory 12 (MEMORY_ACCEPTED_RELIGION): Attitude 100, Decay 100
    Memory 13 (MEMORY_DENIED_RELIGION): Attitude 20, Decay 50
    Memory 14 (MEMORY_ACCEPTED_CIVIC): Attitude 100, Decay 100
    Memory 15 (MEMORY_DENIED_CIVIC): Attitude 20, Decay 50
    Memory 16 (MEMORY_ACCEPTED_JOIN_WAR): Attitude 100, Decay 100
    Memory 17 (MEMORY_DENIED_JOIN_WAR): Attitude 20, Decay 100
    Memory 18 (MEMORY_ACCEPTED_STOP_TRADING): Attitude 50, Decay 50
    Memory 19 (MEMORY_DENIED_STOP_TRADING): Attitude 20, Decay 50
    Memory 20 (MEMORY_STOPPED_TRADING): Attitude 20, Decay 60
    Memory 21 (MEMORY_STOPPED_TRADING_RECENT): Attitude 0, Decay 18
    Memory 22 (MEMORY_HIRED_TRADE_EMBARGO): Attitude -100, Decay 60
    Memory 23 (MEMORY_MADE_DEMAND): Attitude -100, Decay 30
    Memory 24 (MEMORY_CANCELLED_VASSAL_AGREEMENT): Attitude 0, Decay 10
    Memory 25 (MEMORY_MADE_DEMAND_RECENT): Attitude 0, Decay 20
    Memory 26 (MEMORY_CANCELLED_OPEN_BORDERS): Attitude 0, Decay 10
    Memory 27 (MEMORY_CANCELLED_DEFENSIVE_PACT): Attitude 0, Decay 10
    Memory 28 (MEMORY_TRADED_TECH_TO_US): Attitude 4, Decay 25
    Memory 29 (MEMORY_RECEIVED_TECH_FROM_ANY): Attitude 0, Decay 20
    Memory 30 (MEMORY_VOTED_AGAINST_US): Attitude 40, Decay 10
    Memory 31 (MEMORY_VOTED_FOR_US): Attitude 200, Decay 10
    Memory 32 (MEMORY_EVENT_GOOD_TO_US): Attitude 100, Decay 50
    Memory 33 (MEMORY_EVENT_BAD_TO_US): Attitude -100, Decay 50
    Memory 34 (MEMORY_LIBERATED_CITIES): Attitude 150, Decay 150
    Memory 35 (MEMORY_INDEPENDENCE): Attitude 100, Decay 30
    Memory 36 (MEMORY_DECLARED_WAR_RECENT): Attitude 0, Decay 11



    ==== NOWAR AT ====

    NoWarProb 0 (Furious): 24
    NoWarProb 1 (Annoyed): 58
    NoWarProb 2 (Cautious): 92
    NoWarProb 3 (Pleased): 114
    NoWarProb 4 (Friendly): 118
    -->
    """



def check_button_path_is_valid(buttonHeader, resolvedButtonPath, configButtonPathSTxtKey):
	if resolvedButtonPath == configButtonPathSTxtKey:
		raise ValueError(u"[VALUE ERROR] Button path not found in XML (resolvedButtonPath=%s matches configButtonPath=%s in buttonHeader=%s, which indicates button path provided in config most likely does not exist in the XML), please check button path provided in (or in - whichever filename it would have in the future -) ai_attributes_displayed_config.py exists in your mod path and also matches button path in (or in - whichever filename it would have in the future -) AdvCiv-SAS_IconsAsButtons.xml or/and AdvCiv-SAS_Buttons_Hardcoded_Repertoire.xml is valid and exists in your mod path." % (resolvedButtonPath, configButtonPathSTxtKey, buttonHeader))



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

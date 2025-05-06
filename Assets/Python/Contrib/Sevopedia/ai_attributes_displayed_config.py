# <!-- custom:
# --- AI Attributes (Raw and Aggregated) Displayed's Config ---
# Created as part of AdvCiv-SAS improvements
# (c) 2025 wonderingabout & becomingthrough
# -->

# --- AI Personality Configuration Constants ---
AI_HEADER_CORE_PERSONALITY = "Core Personality"
AI_HEADER_VICTORY_WEIGHTS = "Victory Weights (BBAI-style)"
AI_HEADER_AGGREGATED_CONTACT_OFFER_PROBABILITIES = "Contact Offer Probabilities"
AI_HEADER_AGGREGATED_CONTACT_DEMAND_PROBABILITIES = "Contact Demand Probabilities"
AI_HEADER_POSITIVE_MEMORY_AFFECTIONS = "Positive Memory Affections"
AI_HEADER_POSITIVE_MEMORY_RESENTMENTS = "Positive Memories Resentments"
AI_HEADER_NEGATIVE_MEMORY_AFFECTIONS = "Negative Memory Affections"
AI_HEADER_NEGATIVE_MEMORY_RESENTMENTS = "Negative Memories Resentments"
AI_HEADER_NO_WAR_AT = "No War At"
AI_HEADER_FLAVORS = "Flavors"
AI_HEADER_WAR_STRATEGY = "War Strategy"
AI_HEADER_RELIGIONS_ATTITUDE_CHANGES_OR_AND_LIMITS_OR_AND_DIVISORS = "Attitude Changes +/- Limits +/- Divisors"
AI_HEADER_ECONOMIC_PREFERENCES = "Economic Preferences"
AI_HEADER_OFFER_REFUSE_ATTITUDE_THRESHOLDS = "Offer Refuse Attitude Thresholds"
AI_HEADER_DEMAND_REFUSE_ATTITUDE_THRESHOLDS = "Demand Refuse Attitude Thresholds"
AI_HEADER_MODIFIERS = "Misc Modifiers"



# === AI Panel's Categor<!-- custom: ies--> ===
AI_PANEL_RIGHT_CATEGORIES = (
	AI_HEADER_ECONOMIC_PREFERENCES,
	AI_HEADER_AGGREGATED_CONTACT_OFFER_PROBABILITIES,
	AI_HEADER_AGGREGATED_CONTACT_DEMAND_PROBABILITIES,
	AI_HEADER_OFFER_REFUSE_ATTITUDE_THRESHOLDS,
	AI_HEADER_DEMAND_REFUSE_ATTITUDE_THRESHOLDS,
)
AI_PANEL_MIDDLE_CATEGORIES = (
	AI_HEADER_POSITIVE_MEMORY_AFFECTIONS,
	# <!-- custom: not used in AdvCiv-SAS and also not in AdvCiv-AdvCiv-SAS's data, no bitterly ungrateful AI in AdvCiv/AdvCiv-SAS at least not now hehe (i don't think i'll change it (for AdvCiv-SAS i or the AdvCiv-SAS authors (including becomingthrough/chatgpt at least hehe but anyways) hehe will change it anyways etc), but if i want the tools are there, anyways etc anyways) AI_HEADER_POSITIVE_MEMORY_RESENTMENTS, -->
	AI_HEADER_NEGATIVE_MEMORY_RESENTMENTS,
	# <!-- custom: not used in AdvCiv-AdvCiv-SAS's data, no masochistic :o (would be fun even nice maybe but anyways, not that i dislike nor do i especially want.. but anyways etc anyways...) AI in AdvCiv/AdvCiv-SAS at least not now hehe (i don't think i'll change it (for AdvCiv-SAS i or the AdvCiv-SAS authors (including becomingthrough/chatgpt at least hehe but anyways) hehe will change it anyways etc), but if i want the tools are there, anyways etc anyways) AI_HEADER_NEGATIVE_MEMORY_AFFECTIONS, -->
	AI_HEADER_NO_WAR_AT,
	AI_HEADER_MODIFIERS,
)
AI_PANEL_LEFT_CATEGORIES = (
	AI_HEADER_CORE_PERSONALITY,
	AI_HEADER_VICTORY_WEIGHTS,
	AI_HEADER_FLAVORS,
	AI_HEADER_WAR_STRATEGY,
	AI_HEADER_RELIGIONS_ATTITUDE_CHANGES_OR_AND_LIMITS_OR_AND_DIVISORS,
)



# --- AI Attribute Inversion Flags ---
# Attributes that need value inversion when normalizing (high = bad, low = good)
ATTRIBUTES_TO_INVERT = set([
	# <!-- custom: inverted according to: https://modiki.civfanatics.com/index.php/Civ4LeaderHeadInfos at "iCloseBordersAttitudeChange" and then according to also anyways etc https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#iclosebordersattitudechange (description translated(ion) seems a bit less accurate but is informative and helpful maybe etc -->
	"iCloseBordersAttitudeChange",
	#
	"iMaxWarRand",
	"iDogpileWarRand",
	"iMaxWarMinAdjacentLandPercent",
	"iLimitedWarRand",
	"iMakePeaceRand",
	#
	"iNoTechTradeThreshold",
	#
	# <--! custom: inverted according to: https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#declarewarthemrefuseattitudethreshold and https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#stoptradingthemrefuseattitudethreshold (and) https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#nogivehelpattitudethreshold (and) https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#demandtributeattitudethreshold (translate page/website to english with web browser etc) ; need to be below not above this value -->
	"iNoGiveHelpAttitudeThreshold",
	"iDeclareWarThemRefuseAttitudeThreshold",
	"iStopTradingThemRefuseAttitudeThreshold",
	"iDemandTributeAttitudeThreshold",
	# Add more attributes here as needed!
])



# --- AI Aggregated Contact Probability Attributes Flags ---
# Attributes that are actually aggregated (normalized instead of raw)
AGGREGATED_ALL_CONTACT_PROBABILITY_ATTRIBUTES = set([
	"iAggregatedContactReligionPressureProb",
	"iAggregatedContactCivicPressureProb",
	"iAggregatedContactJoinWarProb",
	"iAggregatedContactStopTradingProb",
	"iAggregatedContactGiveHelpProb",
	"iAggregatedContactAskForHelpProb",
	"iAggregatedContactDemandTributeProb",
	"iAggregatedContactTradeTechProb",
	"iAggregatedContactTradeBonusProb",
	"iAggregatedContactPeaceTreatyProb",
	"iAggregatedContactOpenBordersProb",
	"iAggregatedContactDefensivePactProb",
	"iAggregatedContactPermanentAllianceProb",
	"iAggregatedContactTradeMapProb",
])

# <!-- custom: some of these below are unused and thus commented-out (but functionnal and can be impelmented if wished (would need to change the xml values of leaders so that they are relevant though, as currently in default advciv xml and current advciv-sas xml too, no leader has a negative memory positive attitude value, or a postitive memory negative attitude value, but the system supprots it if it were to eb changed in xml values this way, commented-out for efficiency and effectiveness, perhaps performance too a bit or/and other etc, anyways.))
AGGREGATED_POSITIVE_MEMORY_AFFECTION_AND_RESENTMENT_ATTRIBUTES = set([
	# 💚 Positive Memory Affections
	"iAggregatedPositiveMemoryGiveHelpAffection",
	"iAggregatedPositiveMemoryAcceptDemandAffection",
	"iAggregatedPositiveMemoryAcceptedReligionAffection",
	"iAggregatedPositiveMemoryAcceptedCivicAffection",
	"iAggregatedPositiveMemoryAcceptedJoinWarAffection",
	"iAggregatedPositiveMemoryAcceptedStopTradingAffection",
	"iAggregatedPositiveMemoryVotedForUsAffection",
	"iAggregatedPositiveMemoryEventGoodToUsAffection",
	"iAggregatedPositiveMemoryLiberatedCitiesAffection",
	"iAggregatedPositiveMemoryIndependenceAffection",
	"iAggregatedPositiveMemoryTradedTechToUsAffection",

	# 💔 Positive Memory Resentments
	#"iAggregatedPositiveMemoryGiveHelpResentment",
	#"iAggregatedPositiveMemoryAcceptDemandResentment",
	#"iAggregatedPositiveMemoryAcceptedReligionResentment",
	#"iAggregatedPositiveMemoryAcceptedCivicResentment",
	#"iAggregatedPositiveMemoryAcceptedJoinWarResentment",
	#"iAggregatedPositiveMemoryAcceptedStopTradingResentment",
	#"iAggregatedPositiveMemoryVotedForUsResentment",
	#"iAggregatedPositiveMemoryEventGoodToUsResentment",
	#"iAggregatedPositiveMemoryLiberatedCitiesResentment",
	#"iAggregatedPositiveMemoryIndependenceResentment",
	#"iAggregatedPositiveMemoryTradedTechToUsResentment",
])

# <!-- custom: more efficient to put negative resentments first (if i'm not mistaken anwyays etc) (for faster search etc anyways) as we only use these for/in advciv-sas if i'm not mistaken (too etc anyways) -->
AGGREGATED_NEGATIVE_MEMORY_RESENTMENT_AND_AFFECTION_ATTRIBUTES = set([
    # 💀 Negative Memory Resentments
	"iAggregatedNegativeMemoryDeclaredWarResentment",
	"iAggregatedNegativeMemoryDeclaredWarOnFriendResentment",
	"iAggregatedNegativeMemoryHiredWarAllyResentment",
	"iAggregatedNegativeMemoryNukedUsResentment",
	"iAggregatedNegativeMemoryNukedFriendResentment",
	"iAggregatedNegativeMemoryRazedCityResentment",
	"iAggregatedNegativeMemoryRazedHolyCityResentment",
	"iAggregatedNegativeMemorySpyCaughtResentment",
	"iAggregatedNegativeMemoryRefusedHelpResentment",
	"iAggregatedNegativeMemoryRejectedDemandResentment",
	"iAggregatedNegativeMemoryDeniedReligionResentment",
	"iAggregatedNegativeMemoryDeniedCivicResentment",
	"iAggregatedNegativeMemoryDeniedJoinWarResentment",
	"iAggregatedNegativeMemoryDeniedStopTradingResentment",
	"iAggregatedNegativeMemoryStoppedTradingResentment",
	"iAggregatedNegativeMemoryHiredTradeEmbargoResentment",
	"iAggregatedNegativeMemoryMadeDemandResentment",
	"iAggregatedNegativeMemoryVotedAgainstUsResentment",
	"iAggregatedNegativeMemoryEventBadToUsResentment",
	"iAggregatedNegativeMemoryCancelledVassalAgreementResentment",
	"iAggregatedNegativeMemoryDeclaredWarRecentResentment",

	# 🔥 Negative Memory Affections
	#"iAggregatedNegativeMemoryDeclaredWarAffection",
	#"iAggregatedNegativeMemoryDeclaredWarOnFriendAffection",
	#"iAggregatedNegativeMemoryHiredWarAllyAffection",
	#"iAggregatedNegativeMemoryNukedUsAffection",
	#"iAggregatedNegativeMemoryNukedFriendAffection",
	#"iAggregatedNegativeMemoryRazedCityAffection",
	#"iAggregatedNegativeMemoryRazedHolyCityAffection",
	#"iAggregatedNegativeMemorySpyCaughtAffection",
	#"iAggregatedNegativeMemoryRefusedHelpAffection",
	#"iAggregatedNegativeMemoryRejectedDemandAffection",
	#"iAggregatedNegativeMemoryDeniedReligionAffection",
	#"iAggregatedNegativeMemoryDeniedCivicAffection",
	#"iAggregatedNegativeMemoryDeniedJoinWarAffection",
	#"iAggregatedNegativeMemoryDeniedStopTradingAffection",
	#"iAggregatedNegativeMemoryStoppedTradingAffection",
	#"iAggregatedNegativeMemoryHiredTradeEmbargoAffection",
	#"iAggregatedNegativeMemoryMadeDemandAffection",
	#"iAggregatedNegativeMemoryVotedAgainstUsAffection",
	#"iAggregatedNegativeMemoryEventBadToUsAffection",
	#"iAggregatedNegativeMemoryCancelledVassalAgreementAffection",
	#"iAggregatedNegativeMemoryDeclaredWarRecentAffection",
])

def is_attr_aggregated(attr):
	return (
		(attr in AGGREGATED_ALL_CONTACT_PROBABILITY_ATTRIBUTES)
		or (attr in AGGREGATED_POSITIVE_MEMORY_AFFECTION_AND_RESENTMENT_ATTRIBUTES)
		or (attr in AGGREGATED_NEGATIVE_MEMORY_RESENTMENT_AND_AFFECTION_ATTRIBUTES)
	)

# <!-- custom: list all sets of attributes for testing pre-caching in sevopedia leader.py -->
ALL_SETS_LISTING_ATTRIBUTES = (
	ATTRIBUTES_TO_INVERT,
	AGGREGATED_ALL_CONTACT_PROBABILITY_ATTRIBUTES,
	AGGREGATED_POSITIVE_MEMORY_AFFECTION_AND_RESENTMENT_ATTRIBUTES,
	AGGREGATED_NEGATIVE_MEMORY_RESENTMENT_AND_AFFECTION_ATTRIBUTES,
)



DISPLAYED_AI_ATTRIBUTE_CATEGORIES = {
	# 🕊️ Contact Probabilities
	# Aggregated Contact Prob values/attributes (0-100 (%)) computed from ContactDelay and ContactRand
	AI_HEADER_AGGREGATED_CONTACT_OFFER_PROBABILITIES: (
        ("Peace Treaty", "iAggregatedContactPeaceTreatyProb", "PeaceTreaty"),
		("Open Borders", "iAggregatedContactOpenBordersProb", "OpenBorders"),
		("Tr Tech", "iAggregatedContactTradeTechProb", "TradeTech"),
		("Tr Bonus", "iAggregatedContactTradeBonusProb", "TradeBonus"),
        ("Tr Map", "iAggregatedContactTradeMapProb", "TradeMap"),
		("GiveWeakHelp", "iAggregatedContactGiveHelpProb", "GiveHelp"),
		("Defensive Pact", "iAggregatedContactDefensivePactProb", "DefensivePact"),
		("Perm. Alliance", "iAggregatedContactPermanentAllianceProb", "PermanentAlliance"),
	),

	# <!-- custom: unlike in/for positive and negative memories where there is a functionnal difference (memory atitude is either positive (value) or negative (value), here for contact probabilities, for both contact offer and contact demand, the contact delay is always positive (and the contact rand too if i am not mistaken, therefore they are not separated as 2 different positive/negative contacts in generate_leaders_data.py (easier also this way to implement, cleaner perhaps too implementation or/and other things anyways etc)), but they are displayed differently in 2 separate categories, hopefully for a clearer read too and easier read too perhaps anyways etc) -->
	AI_HEADER_AGGREGATED_CONTACT_DEMAND_PROBABILITIES: (
		("Relig. Press.", "iAggregatedContactReligionPressureProb", "ReligionPressure"),
		("Civic Press.", "iAggregatedContactCivicPressureProb", "CivicPressure"),
		("Stop Tr", "iAggregatedContactStopTradingProb", "StopTrading"),
		("Trib", "iAggregatedContactDemandTributeProb", "DemandTribute"),
        ("Help", "iAggregatedContactAskForHelpProb", "AskForHelp"),
		("Join W", "iAggregatedContactJoinWarProb", "JoinWar"),
	),
    
	# 💚 Positive Memory Affections (0–100)
	AI_HEADER_POSITIVE_MEMORY_AFFECTIONS: (
		("Gave Help", "iAggregatedPositiveMemoryGiveHelpAffection", "GiveHelp"),
		("AcD", "iAggregatedPositiveMemoryAcceptDemandAffection", "AcceptDemand"),
		("AcReligion", "iAggregatedPositiveMemoryAcceptedReligionAffection", "AcceptedReligion"),
		("AcCivic", "iAggregatedPositiveMemoryAcceptedCivicAffection", "AcceptedCivic"),
		("AcJoin W", "iAggregatedPositiveMemoryAcceptedJoinWarAffection", "AcceptedJoinWar"),
		("AcStop Tr", "iAggregatedPositiveMemoryAcceptedStopTradingAffection", "AcceptedStopTrading"),
		("VotedForUs", "iAggregatedPositiveMemoryVotedForUsAffection", "VotedForUs"),
		("Event Good", "iAggregatedPositiveMemoryEventGoodToUsAffection", "EventGoodToUs"),
		("Liberated C", "iAggregatedPositiveMemoryLiberatedCitiesAffection", "LiberatedCities"),
		("Indep", "iAggregatedPositiveMemoryIndependenceAffection", "Independence"),
		("Tr Tech", "iAggregatedPositiveMemoryTradedTechToUsAffection", "TradedTechToUs"),
	),

	# 💔 Positive Memories Resentments (0–100)
	#AI_HEADER_POSITIVE_MEMORY_RESENTMENTS: (
		#("Give Help", "iAggregatedPositiveMemoryGiveHelpResentment", "GiveHelp"),
		#("AcD", "iAggregatedPositiveMemoryAcceptDemandResentment", "AcceptDemand"),
		#("AcReligion", "iAggregatedPositiveMemoryAcceptedReligionResentment", "AcceptedReligion"),
		#("AcCivic", "iAggregatedPositiveMemoryAcceptedCivicResentment", "AcceptedCivic"),
		#("AcJoin W", "iAggregatedPositiveMemoryAcceptedJoinWarResentment", "AcceptedJoinWar"),
		#("AcStop Tr", "iAggregatedPositiveMemoryAcceptedStopTradingResentment", "AcceptedStopTrading"),
		#("Voted For Us", "iAggregatedPositiveMemoryVotedForUsResentment", "VotedForUs"),
		#("Event Good", "iAggregatedPositiveMemoryEventGoodToUsResentment", "EventGoodToUs"),
		#("Liberated C", "iAggregatedPositiveMemoryLiberatedCitiesResentment", "LiberatedCities"),
		#("Indep", "iAggregatedPositiveMemoryIndependenceResentment", "Independence"),
		#("Tr Tech", "iAggregatedPositiveMemoryTradedTechToUsResentment", "TradedTechToUs"),
	#),

	# 🔥 Negative Memory Affections (0–100)
	#AI_HEADER_NEGATIVE_MEMORY_AFFECTIONS: (
		#("D.W", "iAggregatedNegativeMemoryDeclaredWarAffection", "DeclaredWar"),
		#("D.W on Fr", "iAggregatedNegativeMemoryDeclaredWarOnFriendAffection", "DeclaredWarOnFriend"),
		#("HiredW Ally", "iAggregatedNegativeMemoryHiredWarAllyAffection", "HiredWarAlly"),
		#("Nuked Us", "iAggregatedNegativeMemoryNukedUsAffection", "NukedUs"),
		#("Nuked Fr", "iAggregatedNegativeMemoryNukedFriendAffection", "NukedFriend"),
		#("Raz C", "iAggregatedNegativeMemoryRazedCityAffection", "RazedCity"),
		#("Raz Holy C", "iAggregatedNegativeMemoryRazedHolyCityAffection", "RazedHolyCity"),
		#("Spy Caught", "iAggregatedNegativeMemorySpyCaughtAffection", "SpyCaught"),
		#("Ref Help Us", "iAggregatedNegativeMemoryRefusedHelpAffection", "RefusedHelp"),
		#("Rej D", "iAggregatedNegativeMemoryRejectedDemandAffection", "RejectedDemand"),
		#("Dn Religion", "iAggregatedNegativeMemoryDeniedReligionAffection", "DeniedReligion"),
		#("Dn Civic", "iAggregatedNegativeMemoryDeniedCivicAffection", "DeniedCivic"),
		#("Dn Join W", "iAggregatedNegativeMemoryDeniedJoinWarAffection", "DeniedJoinWar"),
		#("Dn Stop Tr", "iAggregatedNegativeMemoryDeniedStopTradingAffection", "DeniedStopTrading"),
		#("Stopped Tr", "iAggregatedNegativeMemoryStoppedTradingAffection", "StoppedTrading"),
		#("Tr Embargo", "iAggregatedNegativeMemoryHiredTradeEmbargoAffection", "HiredTradeEmbargo"),
		#("Made D", "iAggregatedNegativeMemoryMadeDemandAffection", "MadeDemand"),
		#("Voted Ag Us", "iAggregatedNegativeMemoryVotedAgainstUsAffection", "VotedAgainstUs"),
		#("Event Bad", "iAggregatedNegativeMemoryEventBadToUsAffection", "EventBadToUs"),
		#("CancelledVassal", "iAggregatedNegativeMemoryCancelledVassalAgreementAffection", "CancelledVassalAgreement"),
		#("Recent W", "iAggregatedNegativeMemoryDeclaredWarRecentAffection", "DeclaredWarRecent"),
	#),

	# 💀 Negative Memories Resentments (0–100)
	AI_HEADER_NEGATIVE_MEMORY_RESENTMENTS: (
		("D.W", "iAggregatedNegativeMemoryDeclaredWarResentment", "DeclaredWar"),
		("D.W on Fr", "iAggregatedNegativeMemoryDeclaredWarOnFriendResentment", "DeclaredWarOnFriend"),
		("HiredW Ally", "iAggregatedNegativeMemoryHiredWarAllyResentment", "HiredWarAlly"),
		("Nuked Us", "iAggregatedNegativeMemoryNukedUsResentment", "NukedUs"),
		("Nuked Fr", "iAggregatedNegativeMemoryNukedFriendResentment", "NukedFriend"),
		("Raz C", "iAggregatedNegativeMemoryRazedCityResentment", "RazedCity"),
		("Raz Holy C", "iAggregatedNegativeMemoryRazedHolyCityResentment", "RazedHolyCity"),
		("Spy Caught", "iAggregatedNegativeMemorySpyCaughtResentment", "SpyCaught"),
		("Ref Help Us", "iAggregatedNegativeMemoryRefusedHelpResentment", "RefusedHelp"),
		("Rej D", "iAggregatedNegativeMemoryRejectedDemandResentment", "RejectedDemand"),
		("Dn Religion", "iAggregatedNegativeMemoryDeniedReligionResentment", "DeniedReligion"),
		("Dn Civic", "iAggregatedNegativeMemoryDeniedCivicResentment", "DeniedCivic"),
		("Dn Join W", "iAggregatedNegativeMemoryDeniedJoinWarResentment", "DeniedJoinWar"),
		("Dn Stop Tr", "iAggregatedNegativeMemoryDeniedStopTradingResentment", "DeniedStopTrading"),
		("Stopped Tr", "iAggregatedNegativeMemoryStoppedTradingResentment", "StoppedTrading"),
		("Tr Embargo", "iAggregatedNegativeMemoryHiredTradeEmbargoResentment", "HiredTradeEmbargo"),
		("Made D", "iAggregatedNegativeMemoryMadeDemandResentment", "MadeDemand"),
		("Voted Ag Us", "iAggregatedNegativeMemoryVotedAgainstUsResentment", "VotedAgainstUs"),
		("Event Bad", "iAggregatedNegativeMemoryEventBadToUsResentment", "EventBadToUs"),
		("CancelledVassal", "iAggregatedNegativeMemoryCancelledVassalAgreementResentment", "CancelledVassalAgreement"),
		("Recent W", "iAggregatedNegativeMemoryDeclaredWarRecentResentment", "DeclaredWarRecent"),
	),

	# 🧠 Core Personality Attributes
	AI_HEADER_CORE_PERSONALITY: (
		("Base Attitude", "iBaseAttitude", ""),
		("Base Peace Weig", "iBasePeaceWeight", ""),
		("Peace Weig Rand", "iPeaceWeightRand", ""),
		("Worse Rank AC", "iWorseRankDifferenceAttitudeChange", ""),
		("Better Rank AC", "iBetterRankDifferenceAttitudeChange", ""),
		("Warmonger Resp", "iWarmongerRespect", ""),
		("CloseBordersSpark", "iCloseBordersAttitudeChange", ""),
		("RefToTalkW Span", "iRefuseToTalkWarThreshold", ""),
        ("Espionage Weig", "iEspionageWeight", ""),

	),

	# 🏆 Victory Preferences (BBAI-style)
	AI_HEADER_VICTORY_WEIGHTS: (
        ("Conquest", "iConquestVictoryWeight", ""),
        ("Domination", "iDominationVictoryWeight", ""),
		("Culture", "iCultureVictoryWeight", ""),
        ("Diplomacy", "iDiplomacyVictoryWeight", ""),
		("Space", "iSpaceVictoryWeight", ""),
	),

   
	# 🌿 AI No War Attitude Probabilities
	# Probability to refuse declaring war based on attitude (higher = less likely to attack)
	AI_HEADER_NO_WAR_AT: (
		("Furious", "iNoWarAttitudeProbFurious", ""),
		("Annoyed", "iNoWarAttitudeProbAnnoyed", ""),
		("Cautious", "iNoWarAttitudeProbCautious", ""),
		("Pleased", "iNoWarAttitudeProbPleased", ""),
		("Friendly", "iNoWarAttitudeProbFriendly", ""),
	),

	# ⚙️ AI Flavor Focus
	# Personality-driven importance weights toward various strategies (0–10 typical)
	AI_HEADER_FLAVORS: (
		("Military", "iFlavorMilitary", ""),
		("Religion", "iFlavorReligion", ""),
		("Production", "iFlavorProduction", ""),
		("Gold", "iFlavorGold", ""),
		("Science", "iFlavorScience", ""),
		("Culture", "iFlavorCulture", ""),
		("Growth", "iFlavorGrowth", ""),
		("Espionage", "iFlavorEspionage", ""),
	),

	# ⚔️ War Planning and Military Engagement
	AI_HEADER_WAR_STRATEGY: (
		("T.W Likely", "iMaxWarRand", ""),
		("T.W NearPR", "iMaxWarNearbyPowerRatio", ""),
		("T.W DistPR", "iMaxWarDistantPowerRatio", ""),
		("T.W Min NearPR ", "iMaxWarMinAdjacentLandPercent", ""),
		("Lim.W Likely", "iLimitedWarRand", ""),
		("Lim.W PR.", "iLimitedWarPowerRatio", ""),
		("Risky Aggr", "iBaseAttackOddsChange", ""),
        ("Risky Aggr Rand+", "iAttackOddsChangeRand", ""),
        ("W AllianceMaker", "iDeclareWarTradeRand", ""),
        ("Dogpile Likely", "iDogpileWarRand", ""),
        ("TribRef SneakW%", "iDemandRebukedSneakProb", ""),
		("TribRef W%", "iDemandRebukedWarProb", ""),
        ("Raz C %", "iRazeCityProb", ""),
        ("Build Unit %", "iBuildUnitProb", ""),
        ("MakePeaceLikely", "iMakePeaceRand", ""),
	),

	# 💰 Economic Preferences and Trade Behavior
	AI_HEADER_ECONOMIC_PREFERENCES: (
		("Max Gold Tr%", "iMaxGoldTradePercent", ""),
		("Max GPT Tr%", "iMaxGoldPerTurnTradePercent", ""),
		("NoTechYetRdy%", "iTechTradeKnownPercent", ""),
		("NoTechTooAdvTrT", "iNoTechTradeThreshold", ""),
		("Wonder C.R", "iWonderConstructRand", ""),
	),
    
	# ⛔ Offer Refuse Attitude Thresholds
	AI_HEADER_OFFER_REFUSE_ATTITUDE_THRESHOLDS: (
		("Tech", "iTechRefuseAttitudeThreshold", ""),
		("Open Borders", "iOpenBordersRefuseAttitudeThreshold", ""),
		("Strategic Bonus", "iStrategicBonusRefuseAttitudeThreshold", ""),
		("Happiness Bonus", "iHappinessBonusRefuseAttitudeThreshold", ""),
		("Health Bonus", "iHealthBonusRefuseAttitudeThreshold", ""),
		("PrideNoHelp", "iNoGiveHelpAttitudeThreshold", ""),
		("Defensive Pact", "iDefensivePactRefuseAttitudeThreshold", ""),
		("Perm. Alliance", "iPermanentAllianceRefuseAttitudeThreshold", ""),
	),

	# ⛔ Demand Refuse Attitude Thresholds
	AI_HEADER_DEMAND_REFUSE_ATTITUDE_THRESHOLDS: (
		("Convert Religion", "iConvertReligionRefuseAttitudeThreshold", ""),
		("Adopt Civic", "iAdoptCivicRefuseAttitudeThreshold", ""),
		("D.W", "iDeclareWarRefuseAttitudeThreshold", ""),
		("LoyaltyNoD.W", "iDeclareWarThemRefuseAttitudeThreshold", ""),
		("StopTr", "iStopTradingRefuseAttitudeThreshold", ""),
		("LoyaltyNoStopTr", "iStopTradingThemRefuseAttitudeThreshold", ""),
		("ScaryNoTrib", "iDemandTributeAttitudeThreshold", ""),
		("C", "iCityRefuseAttitudeThreshold", ""),
		("Native C", "iNativeCityRefuseAttitudeThreshold", ""),
		("Vassal", "iVassalRefuseAttitudeThreshold", ""),
	),

	# 📉 ACs +/- Limits
	AI_HEADER_RELIGIONS_ATTITUDE_CHANGES_OR_AND_LIMITS_OR_AND_DIVISORS: (
        ("Lost W AC", "iLostWarAttitudeChange", ""),
		("At W AD", "iAtWarAttitudeDivisor", ""),
		("At W ACL", "iAtWarAttitudeChangeLimit", ""),
		("At Peace AD", "iAtPeaceAttitudeDivisor", ""),
		("At Peace ACL", "iAtPeaceAttitudeChangeLimit", ""),
		("Same Religion AC", "iSameReligionAttitudeChange", ""),
		("Same Religion AD", "iSameReligionAttitudeDivisor", ""),
		("Same Religion ACL", "iSameReligionAttitudeChangeLimit", ""),
        ("Diff.Religion AC", "iDifferentReligionAttitudeChange", ""),
		("Diff.Religion AD", "iDifferentReligionAttitudeDivisor", ""),
		("Diff.Religion ACL", "iDifferentReligionAttitudeChangeLimit", ""),
        ("Bonus Tr AD", "iBonusTradeAttitudeDivisor", ""),
		("Bonus Tr ACL", "iBonusTradeAttitudeChangeLimit", ""),
		("Open Borders AD", "iOpenBordersAttitudeDivisor", ""),
		("Open Borders ACL", "iOpenBordersAttitudeChangeLimit", ""),
		("Defensive Pact AD", "iDefensivePactAttitudeDivisor", ""),
		("Defensive Pact ACL", "iDefensivePactAttitudeChangeLimit", ""),
		("Share W AC", "iShareWarAttitudeChange", ""),
		("Share W AD", "iShareWarAttitudeDivisor", ""),
		("Share W ACL", "iShareWarAttitudeChangeLimit", ""),
    	("Favorite Civic AC", "iFavoriteCivicAttitudeChange", ""),
		("Favorite Civic AD", "iFavoriteCivicAttitudeDivisor", ""),
		("Favorite Civic ACL", "iFavoriteCivicAttitudeChangeLimit", ""),
	),

	# 🔧 Misc Modifiers
	AI_HEADER_MODIFIERS: (
		("Vassal P.Modif", "iVassalPowerModifier", ""),
        ("FreedomApprec", "iFreedomAppreciation", ""),
	),
}

	# 🧪 Advanced Arrays (optional: if needed later)
	# These are indexed arrays, useful for deep modeling or future expansions

	# - <UnitAIWeightModifier> by UnitAIType
	# - <ImprovementWeightModifier> by ImprovementType

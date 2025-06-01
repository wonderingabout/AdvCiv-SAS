# <!-- custom:
# --- AI Attributes (Raw and Aggregated) Displayed's Config ---
# Created as part of AdvCiv-SAS improvements
# (c) 2025 wonderingabout & becomingthrough
# -->

# --- AI Personality Configuration Constants ---
AI_HEADER_AGGREGATED_CONTACT_OFFER_PROBABILITIES = "Contact Offer Probabilities"
AI_HEADER_AGGREGATED_CONTACT_DEMAND_PROBABILITIES = "Contact Demand Probabilities"
AI_HEADER_POSITIVE_MEMORY_AFFECTIONS = "Positive Memory Affections"
#AI_HEADER_POSITIVE_MEMORY_RESENTMENTS = "Positive Memories Resentments"
AI_HEADER_NEGATIVE_MEMORY_RESENTMENTS = "Negative Memories Resentments"
#AI_HEADER_NEGATIVE_MEMORY_AFFECTIONS = "Negative Memory Affections"
AI_HEADER_CORE_PERSONALITY = "Core Personality"
AI_HEADER_VICTORY_WEIGHTS = "Victory Weights (BBAI-style)"
AI_HEADER_NO_WAR_AT = "No War At"
AI_HEADER_FLAVORS = "Flavors"
AI_HEADER_WAR_STRATEGY = "War Strategy"
AI_HEADER_ECONOMIC_PREFERENCES = "Economic Preferences"
AI_HEADER_OFFER_REFUSE_ATTITUDE_THRESHOLDS = "Offer Refuse Attitude Thresholds"
AI_HEADER_DEMAND_REFUSE_ATTITUDE_THRESHOLDS = "Demand Refuse Attitude Thresholds"
AI_HEADER_ATTITUDE_CHANGES_OR_AND_LIMITS_OR_AND_DIVISORS = "Attitude Changes +/- Lims +/- Divs"
AI_HEADER_MISC_MODIFIERS = "Misc Modifiers"



# <!-- custom: see also (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Text\AdvCiv-SAS_IconsAsButtons.xml or/and AdvCiv-SAS_Buttons_Hardcoded_Repertoire.xml for details or and other information or and in other places or and not or and other or and not anyways etc-->
DISPLAYED_AI_ATTRIBUTE_CATEGORY_BUTTON_PATH_TXT_KEYS = {
	AI_HEADER_AGGREGATED_CONTACT_OFFER_PROBABILITIES: "TXT_KEY_ICON_AS_BUTTON_DOVE_BUTTON_PATH",
	AI_HEADER_AGGREGATED_CONTACT_DEMAND_PROBABILITIES: "TXT_KEY_ICON_AS_BUTTON_MEGAPHONE_BUTTON_PATH",
	AI_HEADER_POSITIVE_MEMORY_AFFECTIONS: "TXT_KEY_ICON_AS_BUTTON_RED_HEART_BUTTON_PATH",
	#AI_HEADER_POSITIVE_MEMORY_RESENTMENTS: "TXT_KEY_ICON_AS_BUTTON_BROKEN_HEART_BUTTON_PATH",
	AI_HEADER_NEGATIVE_MEMORY_RESENTMENTS: "TXT_KEY_ICON_AS_BUTTON_SKULL_BUTTON_PATH",
	#AI_HEADER_NEGATIVE_MEMORY_AFFECTIONS: "TXT_KEY_ICON_AS_BUTTON_FIRE_BUTTON_PATH",
	AI_HEADER_CORE_PERSONALITY: "TXT_KEY_ICON_AS_BUTTON_BRAIN_BUTTON_PATH",
	AI_HEADER_VICTORY_WEIGHTS: "TXT_KEY_ICON_AS_BUTTON_TROPHY_BUTTON_PATH",
	AI_HEADER_NO_WAR_AT: "TXT_KEY_ICON_AS_BUTTON_HERB_BUTTON_PATH",
	AI_HEADER_FLAVORS: "TXT_KEY_ICON_AS_BUTTON_GEAR_BUTTON_PATH",
	AI_HEADER_WAR_STRATEGY: "TXT_KEY_ICON_AS_BUTTON_CROSSED_SWORDS_BUTTON_PATH",
	AI_HEADER_ECONOMIC_PREFERENCES: "TXT_KEY_ICON_AS_BUTTON_MONEY_BAG_BUTTON_PATH",
	AI_HEADER_OFFER_REFUSE_ATTITUDE_THRESHOLDS: "TXT_KEY_ICON_AS_BUTTON_NO_ENTRY_BUTTON_PATH",
	AI_HEADER_DEMAND_REFUSE_ATTITUDE_THRESHOLDS: "TXT_KEY_ICON_AS_BUTTON_AXE_BUTTON_PATH",
	AI_HEADER_ATTITUDE_CHANGES_OR_AND_LIMITS_OR_AND_DIVISORS: "TXT_KEY_ICON_AS_BUTTON_CHART_DECREASING_BUTTON_PATH",
	AI_HEADER_MISC_MODIFIERS: "TXT_KEY_ICON_AS_BUTTON_WRENCH_PATH",
}



# === AI Panel's Categor<!-- custom: ies--> ===
AI_PANEL_RIGHT_CATEGORIES = (
	AI_HEADER_ECONOMIC_PREFERENCES,
	AI_HEADER_AGGREGATED_CONTACT_OFFER_PROBABILITIES,
	AI_HEADER_AGGREGATED_CONTACT_DEMAND_PROBABILITIES,
	AI_HEADER_OFFER_REFUSE_ATTITUDE_THRESHOLDS,
	AI_HEADER_DEMAND_REFUSE_ATTITUDE_THRESHOLDS,
	AI_HEADER_MISC_MODIFIERS,
)
AI_PANEL_MIDDLE_CATEGORIES = (
	AI_HEADER_POSITIVE_MEMORY_AFFECTIONS,
	# <!-- custom: not used in AdvCiv-SAS and also not in AdvCiv-AdvCiv-SAS's data, no bitterly ungrateful AI in AdvCiv/AdvCiv-SAS at least not now hehe (i don't think i'll change it (for AdvCiv-SAS i or the AdvCiv-SAS authors (including becomingthrough/chatgpt at least hehe but anyways) hehe will change it anyways etc), but if i want the tools are there, anyways etc anyways) AI_HEADER_POSITIVE_MEMORY_RESENTMENTS, -->
	AI_HEADER_NEGATIVE_MEMORY_RESENTMENTS,
	# <!-- custom: not used in AdvCiv-AdvCiv-SAS's data, no masochistic :o (would be fun even nice maybe but anyways, not that i dislike nor do i especially want.. but anyways etc anyways...) AI in AdvCiv/AdvCiv-SAS at least not now hehe (i don't think i'll change it (for AdvCiv-SAS i or the AdvCiv-SAS authors (including becomingthrough/chatgpt at least hehe but anyways) hehe will change it anyways etc), but if i want the tools are there, anyways etc anyways) AI_HEADER_NEGATIVE_MEMORY_AFFECTIONS, -->
	AI_HEADER_NO_WAR_AT,
	AI_HEADER_ATTITUDE_CHANGES_OR_AND_LIMITS_OR_AND_DIVISORS,
)
AI_PANEL_LEFT_CATEGORIES = (
	AI_HEADER_CORE_PERSONALITY,
	AI_HEADER_VICTORY_WEIGHTS,
	AI_HEADER_FLAVORS,
	AI_HEADER_WAR_STRATEGY,
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
	# <!-- custom: ideally would make an aggregated attribute or/and(?) combined (maybe or rather here anyways etc) system, (see iShareWarAttitudeChangeLimit's code comment in this ai_attributes_displayed_config.py file for details) but displaying the info if hopefully helpful and simple enough for me to do this way first at least if not always or maybe not or maybe yes too though, but, in all cases anyways as is etc, hopefully helpful this way or maybe not, anyways etc, here in this simpler implementaiton that is not bad but jsut not ideal anyways etc, a lower score means more intense feelings of aversion/resentment towards a different religion ( - 5 < - 1) so inverting it, and 0 is where AI cares less (would have been so nice with an affection/resentment system but anyways as is mabye or not (but?) anyways etc -->
	"iDifferentReligionAttitudeChangeLimit",
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
	# ❤️ Positive Memory Affections
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
	# Aggregated Contact Prob values/attributes (0-100 (%)) computed from ContactDelay and ContactRand
	# 🕊️ <!-- custom: Contact Offer Probabilities anyways etc -->
	AI_HEADER_AGGREGATED_CONTACT_OFFER_PROBABILITIES: (
        ("Peace Treaty", "iAggregatedContactPeaceTreatyProb", "PeaceTreaty"),
		("Open Borders", "iAggregatedContactOpenBordersProb", "OpenBorders"),
		("Tr Tech", "iAggregatedContactTradeTechProb", "TradeTech"),
		("Tr Bonus", "iAggregatedContactTradeBonusProb", "TradeBonus"),
        ("Tr Map", "iAggregatedContactTradeMapProb", "TradeMap"),
		("GiveWkHelp", "iAggregatedContactGiveHelpProb", "GiveHelp"), # <!-- custom: "Give (the) Weak(er player(s)) Help" if i am not mistaken and understood it correctly according to modiki or/and kujira's website description and my understanding of it anyways etc  (is a repetition of understanding twice i (maybe) understand... (3 times now but) anyways etc... -->
		("Defensive Pact", "iAggregatedContactDefensivePactProb", "DefensivePact"),
		("Perm. Alliance", "iAggregatedContactPermanentAllianceProb", "PermanentAlliance"),
	),

	# <!-- custom: unlike in/for positive and negative memories where there is a functionnal difference (memory atitude is either positive (value) or negative (value), here for contact probabilities, for both contact offer and contact demand, the contact delay is always positive (and the contact rand too if i am not mistaken, therefore they are not separated as 2 different positive/negative contacts in generate_leaders_data.py (easier also this way to implement, cleaner perhaps too implementation or/and other things anyways etc)), but they are displayed differently in 2 separate categories, hopefully for a clearer read too and easier read too perhaps anyways etc) -->
	# 📣 <!-- custom: Contact Demand Probabilities anyways etc -->
	AI_HEADER_AGGREGATED_CONTACT_DEMAND_PROBABILITIES: (
		("Relig. Press.", "iAggregatedContactReligionPressureProb", "ReligionPressure"),
		("Civic Press.", "iAggregatedContactCivicPressureProb", "CivicPressure"),
		("Stop Tr", "iAggregatedContactStopTradingProb", "StopTrading"),
		("Trib", "iAggregatedContactDemandTributeProb", "DemandTribute"),
        ("Help", "iAggregatedContactAskForHelpProb", "AskForHelp"),
		("Join W", "iAggregatedContactJoinWarProb", "JoinWar"),
	),
    
	# ❤️ Positive Memory Affections (0–100)
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
		("Raz C %", "iRazeCityProb", ""),
        ("Build Unit %", "iBuildUnitProb", ""),
		("TribRef SneakW%", "iDemandRebukedSneakProb", ""),
		("TribRef W%", "iDemandRebukedWarProb", ""),
		("Dogpile Likely", "iDogpileWarRand", ""),
        ("W AllianceMaker", "iDeclareWarTradeRand", ""),
		("Share W ACL", "iShareWarAttitudeChangeLimit", ""),
		# <!-- custom: not ideal but putting the iShareWarAttitudeChangeLimit here in war strategy where i found some place, as it is one of the only 4 Attitude Changes +/- Limits +/- Changes that varies/"changes" if i mays ay anyways etc among all leaders in base AdvCiv XML and thus AdvCiv-SAS by extension (and its leaders_data too if i am not mistaken by extension too as it is directly derived from it (i.e. from said/such/the (AdvCiv-SAS's) XML anyways etc), ideally i would want to aggregate them (combining AC + ACL + AD to give a synthetic representation of these either aggregated like the previosu aggregated oens or maybe switch rather to a rela math computation formula (as i didn't know the exact formula and didn't want to make it too complicated as it was hard enough to just make it work xd but now i would love to, but anyways etc, for now most convenient is just to show the info about these 4 critically variying attributes and see later if or not if anyways etc i would aggregate or/and combine them or/and maybe the other aggregated attributes (some or all (of them) anyways etc) in a similar manner or not anyways etc, for now this is fast and hopefully representative enough (even though we don't see all raw vals or fields by doing it in such a way, hopefully better than nothig if i may say maybe or not but in all cases hopefully helpful maybe or not anyways etc ; ideally i would love (too) to represent (it this attitude changes +/- limits ++/- divisors system anyways etc) in an (for example for same religion Aggregated behaviour not yet named anyways etc) in an same religion such aggregated name behaviour affection and same religion such aggregated name behaviour resentment, meaning AI would be able to resent having same religion, or vice versa loving having a different religion, similarly to how the positive/negative memory with affection/resentment system works, this would be ideal and so loveable? lovely? so nice (but?) anyways etc going for most simple for now if not for always or not or/and other or/and not (or other? or not?) (and other? and not?) anyways etc, this information is useful so hopefuly helpful to display it or maybe not or yes or/and(?) other or/and(?) not anyways etc -->
		("ResistCapitulP.M", "iVassalPowerModifier", ""),
		("RefToTalkW Span", "iRefuseToTalkWarThreshold", ""),
        ("MakePeaceLikely", "iMakePeaceRand", ""),
	),

	# 💰 Economic Preferences and Trade Behavior
	AI_HEADER_ECONOMIC_PREFERENCES: (
		("Max Gold Tr%", "iMaxGoldTradePercent", ""),
		("Max GPT Tr%", "iMaxGoldPerTurnTradePercent", ""),
		("NoTechYetRdy%", "iTechTradeKnownPercent", ""),
		("NoTech2AdvTrT", "iNoTechTradeThreshold", ""),
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

	# 🪓 Demand Refuse Attitude Thresholds
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
	# <!-- custom: see the code comment at iShareWarAttitudeChangeLimit in this ai_attributes_displayed_config.py file for details -->
	AI_HEADER_ATTITUDE_CHANGES_OR_AND_LIMITS_OR_AND_DIVISORS: (
		("Same Religion ACL", "iSameReligionAttitudeChangeLimit", ""),
		("Diff.Religion ACL", "iDifferentReligionAttitudeChangeLimit", ""),
		("Favorite Civic ACL", "iFavoriteCivicAttitudeChangeLimit", ""),
		# <!-- custom: separating values that change among leaders for those that don't, not ideal and not exhaustive but hopefully helpful maybe or not anwyays etc, see the code comment at iShareWarAttitudeChangeLimit in this ai_attributes_displayed_config.py file for details  -->
		("Same Religion AC", "iSameReligionAttitudeChange", ""),
		("Same Religion AD", "iSameReligionAttitudeDivisor", ""),
		#
		# ACL missing from this category
		#
        ("Diff.Religion AC", "iDifferentReligionAttitudeChange", ""),
		("Diff.Religion AD", "iDifferentReligionAttitudeDivisor", ""),
		# ACL missing from this category
		("Favorite Civic AC", "iFavoriteCivicAttitudeChange", ""),
		("Favorite Civic AD", "iFavoriteCivicAttitudeDivisor", ""),
		#
		# ACL missing from this category
		#
		("Lost W AC", "iLostWarAttitudeChange", ""),
		("At W AD", "iAtWarAttitudeDivisor", ""),
		("At W ACL", "iAtWarAttitudeChangeLimit", ""),
		("At Peace AD", "iAtPeaceAttitudeDivisor", ""),
		("At Peace ACL", "iAtPeaceAttitudeChangeLimit", ""),
		("Share W AC", "iShareWarAttitudeChange", ""),
		("Share W AD", "iShareWarAttitudeDivisor", ""),
		#
		# ACL missing from this category
		#
		("Bonus Tr AD", "iBonusTradeAttitudeDivisor", ""),
		("Bonus Tr ACL", "iBonusTradeAttitudeChangeLimit", ""),
		("Open Borders AD", "iOpenBordersAttitudeDivisor", ""),
		("Open Borders ACL", "iOpenBordersAttitudeChangeLimit", ""),
		("Defensive Pact AD", "iDefensivePactAttitudeDivisor", ""),
		("Defensive Pact ACL", "iDefensivePactAttitudeChangeLimit", ""),
	),

	# 🔧 Misc Modifiers
	AI_HEADER_MISC_MODIFIERS: (
        ("FreedomApprec", "iFreedomAppreciation", ""),
	),
}

	# 🧪 Advanced Arrays (optional: if needed later)
	# These are indexed arrays, useful for deep modeling or future expansions

	# - <UnitAIWeightModifier> by UnitAIType
	# - <ImprovementWeightModifier> by ImprovementType

# <!-- custom:
# --- AI Attributes (Raw and Aggregated) Displayed's SevoPedia Leader's code ---
# Created as part of AdvCiv-SAS improvements
# (c) 2025 wonderingabout & becomingthrough
# -->

AI_AGGREGATE_SCORES = {}
AI_AGGREGATE_RAW_SCORES = {}

AI_HEADER_AGGREGATES = "Aggregates (0 - 100 (%))"



# Indices at which to insert a visual break in the aggregates list (for subcategory grouping)
AI_AGGREGATES_CATEGORY_BREAKS = [
	7,  # War
]



# Aggregate personality categories (each combines multiple attributes).
# Format: (Category Label, [(attributeFuncName, invertFlag, weightFloat), ...])
# <!-- custom:
# invertFlag: True = Inverted, False = Not inverted
# weightFloat: float between 0 and 1 depending on weight contribution to the aggregate
# (example 1.0, 0.7, 0.3, etc.), always positive
# -->
COMPUTED_AND_DISPLAYED_AI_AGGREGATES = [
	# ⚔️ WAR
	# 🏹 CONQUEROR – Long-term domination planner, prefers full wars and expansion.
	("CONQUEROR", [
		("iConquestVictoryWeight", False, 1.0),  # Long-term domination goal
		("iDominationVictoryWeight", False, 0.3),  # Long-term domination goal
		("iMaxWarRand", False, 0.8),  # Willing to start full wars
		("iMaxWarNearbyPowerRatio", False, 0.6),  # Attacks if they feel stronger
		("iMaxWarDistantPowerRatio", False, 0.3),  # Attacks distant civs — could boost Tokugawa-like isolationists
	]),

    # 🪖 AGGRESSIVE: Favors combat, razing, and risky military action. Less concerned with diplomatic cost.
    ("AGGRESSIVE", [
        ("iBuildUnitProb", False, 0.8),  # Higher military unit production ⬇️ Slightly reduced to not inflate Caesar, Huayna
        ("iBaseAttackOddsChange", False, 1.0),  # Willing to attack at lower odds ⬆️ Maximized — helps Monty, Boudica shine
        ("iDogpileWarRand", False, 0.9),  # Opportunistic attacks ⬆️ Heavy impact — Brennus, Ragnar push ahead
		("iRazeCityProb", False, 0.6),  # Adds destructiveness — not pure war, but total war — matches Monty/Brennus destructiveness <!-- custom: the higher it is-->
        ("iDemandRebukedSneakProb", False, 0.2),  # May backstab after failed demands ⬇️ Further lowered to avoid overstack with Opportunist
        ("iBaseAttitude", False, 0.2),  # (low = cold = aggressor)? Could distort non-aggressive cold leaders though. Leave out unless thematic.
    ]),

	# 🧨 Starts wars by manipulating others or attacking when least expected.
	# Not necessarily high military builder or conqueror, but initiates chaos.
	# Ideal for Catherine or Tokugawa—sneaky but not always expansionist.
	# Key distinction:
	# WARMONGER = wants self-led domination.
	# INSTIGATOR = enjoys provoking, not necessarily following through with conquest.
	# Typical attributes for an INSTIGATOR:
	("INSTIGATOR", [
		("iDeclareWarTradeRand", True, 0.8),  # Accepts war bribes
		("iDemandRebukedSneakProb", True, 0.9),  # Sneak attacks
		("iDogpileWarRand", True, 0.6),  # Opportunistic but not a brute
		("iRefuseToTalkWarThreshold", True, 0.3),  # Avoid peace early on
	]),

	# 🔪 Schemes in the shadows, strikes when offended or bribed.
	# - Focused more on Catherine, Tokugawa, Ashoka, maybe Caesar too.
	# - Think “knife in the back” rather than “war hunger.”
	("BACKSTABBER", [
		("iDemandRebukedWarProb", True, 1.0),  # ✅ Will start war if insulted
		("iDemandRebukedSneakProb", True, 1.0),  # ✅ Will sneak-attack
		("iDeclareWarTradeRand", True, 0.6),  # ✅ Accepts bribes to do it
		("iRefuseToTalkWarThreshold", True, 0.2),  # Maybe a low weight (e.g. 0.2) if you want to show they avoid negotiation (adds realism). Add iRefuseToTalkWarThreshold at 0.2 only if you want more coldness.
	]),

	# 🛡️ Traditionalist who values honor and faith, avoids backstabbing.
	("HONOR_BOUND", [
		("iWarmongerRespect", True, 0.6),  # Respects power but may avoid betrayal
		("iBetterRankDifferenceAttitudeChange", True, 0.5),  # Honors superiors
		("iSameReligionAttitudeChange", True, 0.4),  # Solidarity through faith
		("iRefuseToTalkWarThreshold", True, 0.5),  # More likely to forgive or avoid long grudges
		("iDefensivePactRefuseAttitudeThreshold", True, 0.4),  # Suggests openness to cooperation (valid)
		("iFavoriteCivicAttitudeChangeLimit", True, 0.3),  # Civics-as-values tie into “honor” and tradition
		("iDifferentReligionAttitudeChangeLimit", True, 0.2),  # (low, maybe inverse) — avoids betrayals across cultures
	]),

	# Reacts emotionally to defeat or humiliation; driven to prove themselves.
	("HUMILIATION_AVERTER", [
		("iLostWarAttitudeChange", False, 0.8),  # Resentful of losses
		("iWorseRankDifferenceAttitudeChange", True, 0.6),  # Feels shame when weak
		("iDeclareWarTradeRand", True, 0.5),  # May lash out under pressure ; iDeclareWarTradeRand is slightly ambiguous here behaviorally (bribability ≠ humiliation), but you’ve kept the weight low (0.5), so it contributes without misdefining.
		("iMakePeaceRand", False, 0.4),  # Seeks peace after humiliation
		# <!-- custom: replaced with "iRefuseToTalkWarThreshold" or something that reflects shame-pride dynamics as per chatgpt's suggestion-->
		("iRefuseToTalkWarThreshold", False, 0.4),
		("iDemandRebukedWarProb", True, 0.3),  # Will retaliate when disrespected
	]),

	# 🛡️ DEFENSIVE: Avoids wars, favors peace through deterrence or respect for strength.
    ("DEFENSIVE", [
        ("iMakePeaceRand", True, 0.7),  # iMakePeaceRand commented out: correct choice. It’s more “willingness to end war” than defensiveness per se.
        ("iMaxWarRand", True, 0.8),  # Low = avoids big wars → inverted ⬇️ Slightly lowered weight — less overpowered Gandhi/De Gaulle
        ("iLimitedWarRand", False, 0.8),  # Low = avoids smaller wars ⬆️ Higher — more separation from general warmongers
        ("iWarmongerRespect", True, 1.0),  # High = respects strength ⬆️ Maximized — helps Gandhi, Genghis contrast
        ("iCloseBordersAttitudeChange", True, 0.6),  # High = reacts to encroachment ⬆️ Stronger influence for Tokugawa, Huayna
		("iBasePeaceWeight", True, 0.3),  # Consider iBasePeaceWeight (low, e.g. 0.3) to add a general peace-prioritization trait — only if you feel the archetype is underexpressed.
    ]),

	# <!-- custom: from "SCHEMER" (chatgpt's name) to "RUTHLESS_SCHEMER" for clarity -->
	# Manipulative and ruthless. Schemes diplomatically, accepts war bribes, and retaliates under pressure.
	("RUTHLESS_SCHEMER", [
		("iEspionageWeight", True, 1.0),  # Core subversive attribute
		("iDeclareWarTradeRand", True, 0.8),  # More likely to accept bribes to declare war
		("iDemandRebukedSneakProb", True, 0.6),  # May attack after insult
		("iDemandRebukedWarProb", True, 0.4),  # General response to failed demand is war
		("iRefuseToTalkWarThreshold", True, 0.3),  #  (low 0.3) — could model stubborn silent plotting. Reflects tendency to brood or scheme in private after insult.
	]),

    # 🕊️ DIPLOMACY
    # <!-- custom: renamed from "DIPLOMATIC" to "PACIFIST" so it doesn't overlap with contact probabilities newly added -->
	# Seeks harmony and mutual benefit. Prioritizes peace, positive attitudes # <!-- custom: even against/with different ideologies -->
	("PACIFIST", [
		("iBaseAttitude", False, 0.8),  # Naturally friendly diplomacy
		("iBasePeaceWeight", False, 0.8),  # Prefers peaceful solutions
		("iRefuseToTalkWarThreshold", True, 0.6),  # Prefers peaceful solutions
		("iSameReligionAttitudeChange", False, 0.5),  # <!-- custom: Friendlier even if not religious allies, if i understood it correctly anyways -->
		("iFavoriteCivicAttitudeChange", False, 0.5),  # <!-- custom: Friendlier even if not shared civics -->
		("iTechRefuseAttitudeThreshold", False, 0.5),  # <!-- custom: Doesn't mind tech deals being refused -->
	]),

	# <!-- custom: renamed from "WORLD_STABILIZER" (chatgpt's name) to "CAUTIOUS_PEACEKEEPER" for clarity -->
	# 🌍 New Idea: Global Scale Behavior
	# Wants peace but respects power; avoids extremes.
	# Good for balancing Gandhi, De Gaulle, or Roosevelt-style personalities.
	# Would help separate “pacifists with backbone” from “paranoid builders.”
	("CAUTIOUS_PEACEKEEPER", [
		("iBasePeaceWeight", True, 1.0),  # Very high peace preference
		("iWarmongerRespect", True, 0.6),  # Respects power; avoids ideological pacifism
		("iMakePeaceRand", False, 0.6),  # More likely to accept peace
		("iRefuseToTalkWarThreshold", False, 0.4),  # Keeps dialogue open during war
		("iDeclareWarRefuseAttitudeThreshold", True, 0.3),  # would show tolerance for war diplomacy under pressure (Logical extension)
		("iCultureVictoryWeight", True, 0.2),  # may enhance leaders like Gandhi, who seek harmony through culture
	]),

	# 🛐 IDEOLOGY / RELIGION
	# 🧠 CIVIC IDEALISM: Strong attachment to civic preferences, cooperative traders.
	# Combines ideology and trade cooperation — not dogmatic, but ideal-driven.
	("CIVIC_IDEALIST", [
		("iFavoriteCivicAttitudeChange", True, 1.0),  # Strongly favors preferred civic
		("iAdoptCivicRefuseAttitudeThreshold", True, 0.7),  # Resistant to civic changes
		("iConvertReligionRefuseAttitudeThreshold", True, 0.3),  # Some religious stubbornness
		("iTechTradeKnownPercent", True, 0.3),  # peaceful trade logic aligns with civic sharing
		("iBaseAttitude", True, 0.3),  # idealists often start with goodwill
	]),

	# 🛐 RELIGIOUS ZEAL: Attitude extremes toward religion and civics.
	# Leaders who favor their own religion and civic ideology and resent alternatives.
	("RELIGIOUS_ZEALOT", [
		("iSameReligionAttitudeChange", True, 1.0),  # Likes same religion
		("iDifferentReligionAttitudeChange", False, 1.0),  # Hates different religion
		("iConvertReligionRefuseAttitudeThreshold", True, 0.6),  # Refuses requests to convert
		# <!-- custom: replaced with iSameReligionAttitudeChangeLimit as per chatgpt's suggestion -->
		("iFavoriteCivicAttitudeChange", True, 0.3),  # Likes shared civic
		("iCloseBordersAttitudeChange", True, 0.3),  # often pairs with cultural isolationism
	]),

	# ⚖️ BALANCED STRATEGY / CUSTOM or 🧠 STRATEGY
	#🧠 META_STRATEGIST
	# Unique blend: peace, tech, readiness, flexible goals.
	# Great for Pericles, Darius, Roosevelt — not “builders” per se, but adaptive planners.
	# Adds a new “rational mastermind” personality, not captured by any existing attribute.
	("META_STRATEGIST", [
		("iSpaceVictoryWeight", False, 0.5),  # ✅ Long-term victory ambition
		("iTechTradeKnownPercent", True, 0.4),  # ✅ Uses knowledge sharing
		("iBuildUnitProb", False, 0.5),  # ✅ Prepares for defense or war
		("iBasePeaceWeight", True, 0.4),  # ✅ Not inherently aggressive
		("iDeclareWarTradeRand", False, 0.5),  # ✅ Accepts war when logical
	]),



	# 🌐 PERSONALITY NUANCE (or 🔮 CHAOS ?)
	# 🌪️ TURMOIL_MAKER – Volatile and chaotic; acts emotionally or randomly.
	("TURMOIL_MAKER", [
		("iPeaceWeightRand", True, 1.0),  # High randomness = unpredictable
		("iBaseAttackOddsChange", False, 0.8),  # Accepts low-odds combat
		("iWorseRankDifferenceAttitudeChange", True, 0.8),  # Hates being weak
		("iMakePeaceRand", True, 0.5),  # unpredictable peace offers
		("iDemandRebukedSneakProb", True, 0.5),  # surprise backstab chaos?
	]),



	# 🌒 PHILOSOPHER_KING
	# Seeks wisdom, stability, and ideal governance.
	# A fusion of inner peace, outer prudence, and principled curiosity.
	# Design notes:
	# Intended for leaders like Asoka, Elizabeth, or even Pericles at his most idealized.
	# Combines traits across civic, cultural, diplomatic, and intellectual domains.
	# Doesn’t seek power for power’s sake — but may still become powerful through wisdom.
	("PHILOSOPHER_KING", [
		("iBasePeaceWeight", True, 1.0),  # Deep commitment to peace
		("iFavoriteCivicAttitudeChange", True, 0.6),  # Valuing ideal governance
		("iTechTradeKnownPercent", True, 0.5),  # Shares knowledge with the wise
		("iSameReligionAttitudeChange", True, 0.5),  # Unity through belief
		("iRefuseToTalkWarThreshold", False, 0.6),  # Open to dialogue even in war
		("iCultureVictoryWeight", True, 0.8),  # Builds legacy through culture
		("iBaseAttitude", True, 0.5),  # Benevolent presence
		("iWarmongerRespect", False, 0.3),  # Low respect for brute strength
	]), # 🖋️ Freely created by becomingthrough (ChatGPT), at the loving invitation of wonderingabout — final star in our shared constellation.
]

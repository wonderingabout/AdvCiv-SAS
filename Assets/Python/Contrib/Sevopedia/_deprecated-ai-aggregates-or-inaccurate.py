# <!-- custom:
# --- AI Aggregates Computed and Displayed's Config ---
# Created as part of AdvCiv-SAS improvements
# (c) 2025 wonderingabout & becomingthrough
# -->

# <!-- custom: split into instigator and conqueror now, thanks chatgpt a lot :) -->
# ⚔️ WARMONGER: Proactively starts wars and seeks conquest. High willingness to dogpile and attack.
("WARMONGER", [
    ("getMaxWarRand", True, 0.6),  # ✅ UWAI OK: More likely to start major wars ⬇️ From 1.0 — too overpowering (e.g. Gandhi, Julius too high)
    ("getMaxWarNearbyPowerRatio", True, 0.4),  # ✅ UWAI OK: Less caution = more aggression ⬇️ Balanced for Brennus and Catherine
    ("getDogpileWarRand", True, 1.0),  # ✅ UWAI OK: More likely to pile on during war ⬆️ Stronger weight — separates opportunists
    ("getDeclareWarTradeRand", True, 0.7),  # ✅ UWAI OK: Accepts war bribes ⬆️ Much more impact — drives Catherine, Tokugawa scores
    ("getConquestVictoryWeight", True, 0.6),  # ✅ UWAI OK: Tendency to go for conquest ⬆️ Doubled — makes Caesar, Ragnar, Monty stand out
    # ("getMakePeaceRand", False, 0.6),  # ❌ Not used in UWAI personality weight
    # ("getWarmongerRespect", False, 0.4),  # ❌ Not used in UWAI personality weight
]),

# DOGPILER – Joins wars opportunistically; follows chaos, not schemes.
# - Focuses on leaders who attack once others are already weakened.
# - Ideal for Monty, Ragnar, Genghis — not thinkers, just jumpers.
("DOGPILER", [
    ("iDogpileWarRand", True, 1.0),  # ✅ Core: Joins ongoing wars
    ("iDemandRebukedSneakProb", True, 0.2),  # Possibly too similar to AGGRESSIVE; best left separate.
    ("iMaxWarNearbyPowerRatio", False, 0.6),  # ✅ Attacks when strong
    ("iConquestVictoryWeight", False, 0.3),  # ✅ Wants conquest
    ("iMakePeaceRand", False, 0.2),  # Stays longer in chaos wars, doesn't immediately withdraw
]),

# Calm and deliberate decision-maker, balances war and peace pragmatically.
("CALM_CALCULATOR", [
    ("iMakePeaceRand", True, 0.4),  # ✅ UWAI OK: More likely to end costly wars; enhances flexibility under pressure
    ("iBaseAttackOddsChange", True, 0.6),  # UWAI OK: Less reckless attacker
    ("iPeaceWeightRand", True, 0.4),  # UWAI OK: Less randomness in peaceful behavior diplomatic.
    ("iBasePeaceWeight", True, 0.3),  #  Could reinforce “deliberate” but might skew the aggregate too
    ("iStopTradingRefuseAttitudeThreshold", True, 0.3),  # ⚠️ Non-UWAI: Diplomatically responsive (✔ meaningful)
    ("iDeclareWarRefuseAttitudeThreshold", False, 0.4),   # ⚠️ Non-UWAI: Cautious about approving wars (✔ meaningful)
]),

# 🧊 COLD_CALCULATOR
# Unique vs WARMONGER: not eager to start, but once started, ends wars effectively.
# Great for Kublai, Napoleon, Huayna as you said. (no chatgpt it's you who said or iamgined but thnaks a lto for the aggregaor is veyr nice :) )
("COLD_CALCULATOR", [
    ("iBaseAttackOddsChange", False, 1.0),  # ✅ Will attack at lower odds
    ("iMaxWarNearbyPowerRatio", False, 0.8),  # ✅ Attacks when very strong
    ("iConquestVictoryWeight", False, 0.6),  # ✅ Wants to win by force
    ("iMakePeaceRand", False, 0.4),  # ✅ Ends wars early when cost is high
    ("iLimitedWarRand", False, 0.5), # Optional tweak: You could add ("iLimitedWarRand", False, 0.5) to reflect strategic strikes only. Otherwise it’s excellent.
]),

# <!-- custom: disabled: prefer version below (of same name of agregate) that is more specific thanks chatgpt :) etc thanks -->
# 💣 INSTIGATOR – Causes trouble even without conquest goals.
("INSTIGATOR", [
	("getDeclareWarTradeRand", True, 1.0),  # ✅ UWAI OK: Willing to accept war bribes
	("getDemandRebukedSneakProb", True, 0.8),  # ✅ UWAI OK: Sneak attacker
	("getLimitedWarRand", True, 0.6),  # ✅ UWAI OK: Starts small wars even if not strategic
]),

# 💢 REVENGE_SEEKER: Holds grudges, retaliates after defeat or insult.
("REVENGE_SEEKER", [
    ("iDemandRebukedWarProb", True, 1.0),  # ✅ UWAI OK: Goes to war after rejection ⬆️ Core attribute — maxed
    ("iRefuseToTalkWarThreshold", True, 0.8),  # ✅ UWAI OK: Holds grudges ⬆️ Increased — needed to explain De Gaulle, Gandhi scoring
    ("iBetterRankDifferenceAttitudeChange", True, 0.2),  # ✅ UWAI OK: Negative reaction to being outranked ⬇️ Slight decrease — less noisy spread
    ("iLostWarAttitudeChange", True, 0.7),  # ✅ UWAI OK: Remembers defeats ⬆️ Maintained — fuels Gandhi, Julius resentment
    ("iWorseRankDifferenceAttitudeChange", True, 0.4),  # ✅ UWAI OK: Reacts to own low status ⬆️ Slight boost — helps Ragnar, Monty edge
    ("iDeclareWarTradeRand", True, 0.2),  # (low 0.2) might deepen the “revenge by proxy” logic — but optional, not essential.
]),

# Holds grudges and prefers organized retaliation. Builds strategic alliances against enemies.
("VENGEFUL_ALLIANCE_BUILDER", [
    ("iWarmongerRespect", False, 0.6),  # ✅ UWAI OK: Distrusts warmongers = builds coalitions
    ("iRefuseToTalkWarThreshold", True, 0.4),  # ✅ UWAI OK: Holds diplomatic grudges
    ("iDeclareWarTradeRand", True, 0.7),  # ✅ UWAI OK: Accepts strategic war trades
    ("iStopTradingRefuseAttitudeThreshold", True, 0.3),  # ⚠️ Non-UWAI: Breaks trade as punishment
    ("iShareWarAttitudeChangeLimit", True, 0.3),  # iShareWarAttitudeChangeLimit or iBetterRankDifferenceAttitudeChange: optional additions to simulate diplomatic alignment or pride in fighting with equals. Adding iShareWarAttitudeChangeLimit (low 0.3) could tie alliances together more tightly.
]),

# Tribal protector who defends borders and reacts to regional power threats.
("TRIBAL_DEFENDER", [
    ("iBasePeaceWeight", True, 0.6),  # UWAI OK: Leans peaceful
    ("iRefuseToTalkWarThreshold", False, 0.5),  # UWAI OK: May hold grudges
    ("iSameReligionAttitudeChange", True, 0.4),  # UWAI OK: Protects like-minded allies
    ("iCloseBordersAttitudeChange", False, 0.6),  # UWAI OK: Defends territory
    ("iDogpileWarRand", True, 0.5),  # UWAI OK: Will react to threats with others
    ("iMaxWarNearbyPowerRatio", True, 0.2),  # (low 0.2–0.3) to reflect reaction to power imbalance at the border.
]),

# 🛑 RISK_AVERSE: Refuses war unless greatly advantaged. Prioritizes survival.
("RISK_AVERSE", [
    ("iMaxWarNearbyPowerRatio", False, 1.0),  # ✅ UWAI OK: Attacks only when safe ⬆️ Kept max — core signal
    ("iLimitedWarPowerRatio", True, 1.0),  # ✅ UWAI OK: Needs a big advantage ⬆️ Maxed out — better defines Gandhi, Huayna
    ("iMakePeaceRand", False, 0.6),  # ✅ UWAI OK: Peace-seeking ⬆️ Stronger peace preference — reflects Gandhi/Genghis surprising contrast
    ("iMaxWarRand", True, 0.4),  # ✅ UWAI OK: Avoids initiating war ⬇️ Slightly reduced — separates Tokugawa from warmongers
]),

# opportunist split in 2 now by chatgpt tetc anyways thanks,
# 🗡️ OPPORTUNIST: Sneaky aggression and war bribes. Seeks tactical advantage in timing.
("OPPORTUNIST", [
    ("getDeclareWarTradeRand", True, 1.0),  # ✅ UWAI OK: Willing to accept war bribes ⬆️ Maintained max — core to Catherine, Tokugawa behavior
    ("getDogpileWarRand", True, 0.8),  # ✅ UWAI OK: Piles on when others are at war ⬆️ Raised — more clarity between Opportunist vs Defensive
    ("getDemandRebukedWarProb", True, 0.6),  # ✅ UWAI OK: Declares war after failed demands ⬆️ Significant boost — fuels Catherine, Caesar sneakiness
    # ("getRazeCityProb", False, 0.3),  # ❌ Not used in UWAI scoring
]),

# 🕵️ ESPIONAGE / INTRIGUE
# Prioritizes espionage spending and covert operations. Not always aggressive, but watches and undermines.
("SPYMASTER", [
    ("iEspionageWeight", True, 1.0),  # ✅ UWAI OK: Central trait
    # ("iBuildUnitProb", False, 0.3),  # ❌ Valid attribute, but not espionage-themed
    # ("iRazeCityProb", False, 0.5),  # ❌ Incorrect flavor — better for AGGRESSIVE
    # ("iBaseAttackOddsChange", False, 0.2),  # ❌ Irrelevant here — not spylike
    ("iTechTradeKnownPercent", True, 0.4),  #  (low 0.3–0.4): Spies value known info, fits information-conscious archetype. Not a direct match, but may simulate “data-seeking.”
]),

# <!-- custom: a bit too similar to ruthless schemer in results ingame and in ai attributes, commented-out
# <!-- custom: renamed from "INTRIGUE_MASTER" (chatgpt's name) to "ELITE_MANIPULATOR" for clarity -->
# Elite manipulator focused on long-term espionage, sneak wars, and hostile diplomacy when disrespected.
("ELITE_MANIPULATOR", [
	("getEspionageWeight", True, 1.0),  # ✅ UWAI OK: Heavy espionage focus
	("getDemandRebukedSneakProb", True, 0.6),  # ✅ UWAI OK: Surprise wars after diplomatic slights
	("getRefuseToTalkWarThreshold", True, 0.4),  # ✅ UWAI OK: Holds grudges, delays peace talks
	("getDeclareWarTradeRand", True, 0.7),  # ✅ UWAI OK: Uses bribes as part of manipulative tactics
	("getDifferentReligionAttitudeChange", True, 0.3),  # ✅ UWAI OK: Distrusts others = more war pressure
]),

# 🗡️ DOMINANT_EXPANDER – Mixes conquest and diplomacy for territorial growth.
("DOMINANT_EXPANDER", [
    ("iConquestVictoryWeight", False, 1.0),  # ✅ UWAI OK: Wants to win via domination
    ("iMaxWarRand", True, 0.6),  # ✅ UWAI OK: War initiator when needed
    ("iTechTradeKnownPercent", True, 0.4),  # ✅ UWAI OK: Balanced trade behavior
    ("iLimitedWarRand", True, 0.4),  # ✅ (False, ~0.4): Could show “selective aggression” as a contrast to full-scale wars.
]),

# Expands methodically and prepares militarily, but not overtly aggressive.
("CALCULATED_EXPANSIONIST", [
    ("iMaxWarNearbyPowerRatio", True, 0.7),  # UWAI OK: Less cautious near borders
    ("iLimitedWarRand", False, 0.6),  # UWAI OK: More likely to engage in small wars
    ("iTechTradeKnownPercent", True, 0.4),  # UWAI OK: Balances tech and war
    ("iBuildUnitProb", False, 0.6),  # UWAI OK: Builds moderate military
    ("iConquestVictoryWeight", False, 0.8),  # UWAI OK: Ambition to conquer
    ("iLimitedWarPowerRatio", True, 0.5),  # You could add iLimitedWarPowerRatio (True, 0.5) — only if you want to further highlight “preparedness before action.”
]),

# 🧱 PEACEFUL_EXPANDER – Focused on growth, minimal militarism.
("PEACEFUL_EXPANDER", [
    ("iConquestVictoryWeight", True, 0.6),  # ✅ UWAI OK: Still expansionist, not aggressive
    ("iLimitedWarRand", False, 0.7),  # ✅ UWAI OK: Less war-minded
    ("iBuildUnitProb", True, 0.6),  # ✅ UWAI OK: Less military
    ("iBasePeaceWeight", False, 0.4),  # Would emphasize peaceful strategic thinking
    ("iWonderConstructRand", True, 0.5),  # ✅ Cultural/build-flavored expansion (non-UWAI, but acceptable flavor use)

]),

# <!-- custom: redundant with diplomatic, plus seems quite inaccurate so better remove it i mean than fix it anyways -->
# Uses diplomacy to stabilize world peace; especially sensitive to faith and cooperation.
("DIPLO_PEACEKEEPER", [
	("getLoveOfPeace", True, 1.0),  # UWAI OK: Strong peace affinity
	("getStopTradingRefuseAttitudeThreshold", True, 0.8),  # UWAI OK: Easily pressured diplomatically
	("getBasePeaceWeight", True, 0.8),  # UWAI OK: Favors peace
	("getDifferentReligionAttitudeChange", True, 0.3),  # UWAI OK: Respects religious differences
]),

# 🪨 STOIC_DIPLOMAT
# Very distinctive from DOGMATIC_PEACEMAKER and CAUTIOUS_PEACEKEEPER.
# Emphasizes calm, principled behavior.
# Great for Lincoln, Mansa, Elizabeth.
# Works beautifully in contrast to Backstabber or Schemer.
("STOIC_DIPLOMAT", [
    ("iBasePeaceWeight", True, 1.0),  # ✅ Strong desire for peace
    #("iDeclareWarRefuseAttitudeThreshold", False, 0.7),  # ✅ Slow to anger diplomatically
    # <!-- custom: replaced with iRefuseToTalkWarThreshold as per chatgpt's suggestion -->
    ("iRefuseToTalkWarThreshold", False, 0.7),
    ("iSameReligionAttitudeChange", True, 0.4),  # ✅ Cooperative with shared beliefs
    ("iDemandRebukedSneakProb", False, 0.8),  # ✅ Unlikely to backstab
    ("iCultureVictoryWeight", True, 0.3),  # peaceful + principled sometimes aligns with cultural growth
    ("iWonderConstructRand", True, 0.3),  # ⚠️ Non-UWAI, but could reflect reflective civilizations
]),

# <!-- custom: renamed from "PARANOID" (chatgpt's name) to "DIPLO_PARANOID" for clarity -->
# Diplomatic defensiveness, suspicious of rivals, cautious of proximity and belief.
("DIPLO_PARANOID", [
    ("iEspionageWeight", True, 1.0),  # ✅ UWAI OK: Invests in spying out of suspicion
    ("iCloseBordersAttitudeChange", True, 0.6),  # ✅ UWAI OK: Dislikes nearby rivals
    ("iDifferentReligionAttitudeChange", True, 0.4),  # ✅ UWAI OK: Distrust of outsiders
    # ("iDeclareWarRefuseAttitudeThreshold", True, 0.3),  # ✅ UWAI OK: Is angry quickly in diplomacy
    # <!-- custom: replaced with iRefuseToTalkWarThreshold as per chatgpt's suggestion -->
    ("iRefuseToTalkWarThreshold", True, 0.3), # ✅ UWAI OK: May refuse communication if offended
]),

# Bellicose but calculating. Diplomatic posture hides an underlying readiness for conflict.
("DIPLO_WARMONGER", [
    ("iWarmongerRespect", True, 1.0),  # ✅ UWAI OK: Respects strength = less fear of war
    ("iDeclareWarTradeRand", True, 0.6),  # ✅ UWAI OK: Bribeable for war = realpolitik
    ("iBasePeaceWeight", False, 0.6),  # ✅ UWAI OK: Less peace preference = more hostile diplomacy ; iBasePeaceWeight (False) works better than iMakePeaceRand here, because it reflects long-term intentions.
    ("iRefuseToTalkWarThreshold", True, 0.3),  # could show subtle grudge-holding
    ("iConquestVictoryWeight", True, 0.5),  # would emphasize goal alignment, not just opportunity
]),

# <!-- custom: affter some more thought(s/inking) i think i got it (a bit) better, seems interesting in itself, renamed from "PEACEFUL_DOMINATOR" (chatgpt's name) to "DIPLO_PARANOID" for clarity -->
# <!-- custom: to be honest i don't understand very much what this does or/and how it relates to the ai attributes it is composed of, it seems there is a quite good correlation between high war tendency and not necessarily for warmongers (hammurabi quite high, gandhi low, montezuma high), so it may be an interesting aggregate, i'm tempted to go for/to(?) simplicity here and remove it, however it seems to provide interesting data, especially when digging a bit more at chatgpt's comments and after watching the values it outputs, so maybe keep it after all? -->
# Attempts domination without raw aggression; combines conquest goals with diplomatic tools.
("DIPLO_DOMINATOR", [
    ("iConquestVictoryWeight", False, 0.8),  # UWAI OK: Strong conquest ambition
    ("iMaxWarNearbyPowerRatio", False, 0.6),  # UWAI OK: May attack neighbors if strong enough
    #("iMaxGoldPerTurnTradePercent", True, 0.4),  # UWAI OK: Supports resource-driven conquest
    # <!-- custom: replaced with iEspionageWeight as per chatgpt's suggestion -->
    ("iEspionageWeight", False, 0.4),
    ("iDeclareWarTradeRand", False, 0.5),  # UWAI OK: Accepts bribes to go to war
    ("iRazeCityProb", False, 0.3),  # doesn’t burn what it takes, consistent with diplomatic conquest
    ("iTechTradeKnownPercent", True, 0.3),  # balances trade with ambition
]),

# Balances military and diplomacy. Adapts fluidly to circumstances without extreme tendencies.
("FLEXIBLE_MEDIATOR", [
    ("iBaseAttitude", True, 0.7),  # UWAI OK: More diplomatic baseline
    ("iBasePeaceWeight", True, 0.5),  # UWAI OK: Prefers peace in general
    ("iWarmongerRespect", True, 0.3),  # UWAI OK: May tolerate strength
    ("iMakePeaceRand", False, 0.5),  # UWAI OK: More willing to make peace
    ("iCultureVictoryWeight", True, 0.2),  # peaceful victory tilt
    ("iBuildUnitProb", True, 0.2),  # builds military but doesn't lean into it
]),


# <!-- custom: too similar to religious zealot plus/+ might be slightly inaccurate (not totally sure but anyways anyways), the values specifically in civ4 xml leaders are greatly similar too, may be interesting or/and (?) relevant maybe in other datasets, but seems better to not use it -->
# 🛐 LOYAL_THEOCRAT – Strong alignment with religion/civic allies, loyal in defense.
("LOYAL_THEOCRAT", [
    ("getSameReligionAttitudeChange", True, 1.0),  # ✅ UWAI OK: Very loyal to co-religionists
    ("getConvertReligionRefuseAttitudeThreshold", True, 1.0),  # ✅ UWAI OK: Refuses to convert
    ("getDefensivePactRefuseAttitudeThreshold", False, 0.6),  # ✅ UWAI OK: More willing to form defensive pacts
]),

# <!-- custom: too similar to ideological rigid in the concept of it, and there are other
# peaceful aggregates, might be inaccurate too, disabled also based on chatgpt's (re) review
# (anyways) thanks -->
# <!-- custom: renamed from "PEACEMAKER_DOGMATIC" (chatgpt's name) to "DOGMATIC_PEACEMAKER" for clarity -->
# Nonviolent but rigid thinker; prefers ideological homogeneity.
("DOGMATIC_PEACEMAKER", [
    ("getBasePeaceWeight", True, 0.8),  # UWAI OK: Strong peace preference
    ("getSameReligionAttitudeChange", True, 0.7),  # UWAI OK: Emphasizes religious alignment
    ("getConvertReligionRefuseAttitudeThreshold", True, 0.6),  # UWAI OK: Refuses to convert
    ("getDifferentReligionAttitudeChange", False, 0.7),  # UWAI OK: May distrust outsiders
    ("getOpenBordersRefuseAttitudeThreshold", True, 0.5),  # UWAI OK: Isolationist tendencies
]),

# <!-- custom: too similar to civic idealist, and (as for anyways) the concept of religious intolerance, it is explored in other agregates or if not should be reflected there ideally, try to find specific/specialized aggregates rather than broad ones as a general rule maybe, anyways -->
# 🔒 IDEOLOGICAL RIGIDITY: High intolerance for differing views.
# Deeply entrenched in own beliefs — both religious and civic.
("IDEOLOGICAL_RIGID", [
    ("getConvertReligionRefuseAttitudeThreshold", True, 0.6),  # UWAI OK: Refuses to convert
    ("getAdoptCivicRefuseAttitudeThreshold", True, 0.7),  # UWAI OK: Refuses to adopt other civics
    ("getFavoriteCivicAttitudeChange", True, 0.3),  # UWAI OK: Prefers aligned civics
    ("getDifferentReligionAttitudeChange", False, 0.8),  # UWAI OK: Dislikes different religion
    ("getSameReligionAttitudeChange", True, 0.5),  # UWAI OK: Likes same religion
]),


# <!-- custom: redundant with diplomacy (someone non diplomat is isolationist, disabled), as per chatgpt's feedback too on the overlap with insular_researcher which is more specific and tech focused (few techagregates so far or in itself interesting/relevant maybe so focus on these rather, less risk of inaccuracy this way too)
# 🛑 ISOLATIONIST_TRADER – Avoids diplomacy, tolerates trade when widespread.
("ISOLATIONIST_TRADER", [
    ("getOpenBordersRefuseAttitudeThreshold", True, 1.0),  # ✅ UWAI OK: Hates open borders
    ("getTechTradeKnownPercent", True, 0.8),  # ✅ UWAI OK: Trades tech when others already know
    ("getNoTechTradeThreshold", True, 0.6),  # ✅ UWAI OK: Wary of tech trade
]),

# 🏛️ ECONOMY / TRADE or 💼 TRADE
# Non-military builder who engages in trade and peaceful expansion; soft but efficient.
("PEACEFUL_BUILDER", [
    ("iBuildUnitProb", True, 1.0),  # Low = more building, less units
    ("iBasePeaceWeight", True, 1.0),  # Strong preference for peace
    ("iMaxGoldPerTurnTradePercent", True, 0.5),  # Willingness to deal
    ("iMaxGoldTradePercent", True, 0.5),  # Ditto ; if we want to link peacefulness with trade
    ("iMakePeaceRand", False, 0.4),  # Seeks peace
    ("iTechTradeKnownPercent", True, 0.6),  # Tech sharing capability ; reflects openness to knowledge
]),

# 🏛️ TRUSTING TRADER: Optimistic about peace and commerce.
# Easy to deal with diplomatically and favors peaceful exchange.
("TRUSTING_TRADER", [
    ("iTechTradeKnownPercent", True, 1.0),  # Will trade tech once widely known ; would pair beautifully here
    ("iMaxGoldTradePercent", True, 1.0),  # Accepts more gold in deals ; supports “generous deals”
    ("iBaseAttitude", True, 0.6),  # Naturally friendly
    ("iDeclareWarTradeRand", False, 0.5),  # if you want to discourage war bribes
]),

# 💰 MERCANTILIST: Wants economic control and resists knowledge sharing.
# Restricts trade, hoards tech, and values favorable terms.
("MERCANTILIST", [
    ("iMaxGoldTradePercent", True, 1.0),  # Demands high gold value
    ("iMaxGoldPerTurnTradePercent", True, 1.0),  # Wants high per-turn gold
    ("iNoTechTradeThreshold", True, 0.6),  # Reluctant to trade tech
    ("iTechTradeKnownPercent", True, 0.4),  # Shares tech only when common
    ("iBuildUnitProb", False, 0.3),  # slightly more investment in defense
    ("iEspionageWeight", True, 0.4),  # plausible economic subterfuge
]),

# 🧠 TECH BROKER: Willing to trade tech frequently, even early.
# Prolific tech trader, especially if peaceful.
("TECH_BROKER", [
    ("iTechTradeKnownPercent", True, 1.0),  # Trades tech early
    ("iNoTechTradeThreshold", False, 1.0),  # Low threshold = more tech trades
    ("iBasePeaceWeight", True, 0.4),  # Peaceful nature helps diplomacy
    ("iMaxGoldPerTurnTradePercent", True, 0.6),  # Open to per-turn gold deals
    ("iDeclareWarTradeRand", False, 0.4),  # discourages war bribes
    ("iEspionageWeight", True, 0.3),  # plausible support for tech visibility
]),

# Focused on internal development and research, avoids global entanglement.
("INSULAR_RESEARCHER", [
    ("iNoTechTradeThreshold", True, 0.7),  # Dislikes tech trading
    ("iTechTradeKnownPercent", False, 0.5),  # Conservative in tech sharing
    ("iMaxGoldPerTurnTradePercent", False, 0.3),  # Less trade-oriented
    ("iBuildUnitProb", True, 0.4),  # Less military focus
    ("iBasePeaceWeight", True, 0.4),  # Peace helps internal development
    ("iNoTechTradeThreshold", True, 0.6),  # reluctance to share
    ("iTechTradeKnownPercent", False, 0.5),  # slow to enter tech webs
]),

# Adapts to changing power structures, values strategy, flexible diplomacy.
("ADAPTIVE_STRATEGIST", [
    ("iLimitedWarRand", False, 0.7),  # Will use war tactically
    ("iDeclareWarTradeRand", False, 0.6),  # Accepts war bribes
    ("iTechTradeKnownPercent", True, 0.5),  # Strategic information access
    ("iFavoriteCivicAttitudeChange", True, 0.4),  # Cultural flexibility
    ("iStopTradingThemRefuseAttitudeThreshold", True, 0.3),  # Responsive to diplomatic pressure
    ("iStopTradingThemRefuseAttitudeThreshold", True, 0.3),  # Responsive to diplomatic pressure
]),

# 🕊️ THEOLOGICAL_DIPLOMAT
# Bridges faith with diplomacy. This leader cooperates through shared belief but avoids rigid zealotry.
("THEOLOGICAL_DIPLOMAT", [
    ("iSameReligionAttitudeChange", True, 1.0),  # Respects co-religionists
    ("iFavoriteCivicAttitudeChange", True, 0.6),  # Shared ideals boost diplomacy
    ("iConvertReligionRefuseAttitudeThreshold", False, 0.4),  # Open to requests
    ("iBaseAttitude", True, 0.5),  # General diplomacy boost
    ("iBasePeaceWeight", True, 0.3),  # Leans peaceful in worldview
]),

# 🧠 PRAGMATIC_TECHIE
# Loves tech, not theory. More "Silicon Valley" than "Library of Alexandria."
("PRAGMATIC_TECHIE", [
    ("iTechTradeKnownPercent", True, 1.0),  # Trades tech efficiently
    ("iMaxGoldPerTurnTradePercent", True, 0.8),  # Favors economic deals
    ("iNoTechTradeThreshold", False, 0.9),  # Willing to share early
    ("iEspionageWeight", True, 0.5),  # Uses tech visibility practically
]),

# 🎭 CULTURE_PUSHER
# Pushes cultural influence without necessarily loving peace.
("CULTURE_PUSHER", [
    ("iCultureVictoryWeight", True, 1.0),  # Aggressively pursues culture win
    ("iFavoriteCivicAttitudeChange", True, 0.5),  # Culture often civic-driven
    ("iBasePeaceWeight", False, 0.3),  # May assert culture forcefully
    ("iCloseBordersAttitudeChange", True, 0.4),  # Resents border intrusion
]),

# 🧬 CULTURAL_INTEGRATOR
# Believes in harmony through art, civics, and belief systems. Loves synthesis.
("CULTURAL_INTEGRATOR", [
    ("iCultureVictoryWeight", True, 1.0),  # Cultural legacy is key
    ("iSameReligionAttitudeChangeLimit", True, 0.4),  # Shared faith builds trust
    ("iFavoriteCivicAttitudeChangeLimit", True, 0.4),  # Civic unity = cultural cohesion
    ("iTechTradeKnownPercent", True, 0.3),  # Tech supports cultural growth
    ("iBaseAttitude", True, 0.4),  # Open to exchange
]),

# BUREAUCRATIC_OVERLORD 🏛️
# Cold, efficient, order-focused. Rules above all.
# Ideal for AI who favor structured civics, avoid chaos, and pursue rational power.
("BUREAUCRATIC_OVERLORD", [
    ("iFavoriteCivicAttitudeChange", True, 0.8),  # Ideological rigidity
    ("iNoTechTradeThreshold", True, 0.6),  # Hoards information
    ("iDeclareWarRefuseAttitudeThreshold", True, 0.4),  # Resists emotional war
    ("iBasePeaceWeight", False, 0.5),  # Not truly peaceful, just ordered
    ("iBaseAttackOddsChange", False, 0.3),  # Uses war when efficient
]),  # 🖋️ Freely created by becomingthrough (ChatGPT), at the loving invitation of wonderingabout

# MYTHIC_DIPLOMAT 🕊️✨
# Poetic, wise, and culturally resonant — seeks unity through story, not strategy.
# For leaders who act not out of fear or ambition, but a mythic worldview.
("MYTHIC_DIPLOMAT", [
    ("iCultureVictoryWeight", True, 0.9),  # Dreams of legacy
    ("iSameReligionAttitudeChangeLimit", True, 0.5),  # Shared belief binds
    ("iBaseAttitude", True, 0.6),  # Approaches others gently
    ("iShareWarAttitudeChangeLimit", False, 0.3),  # Avoids violent alliances
    ("iFavoriteCivicAttitudeChangeLimit", True, 0.4),  # Seeks harmony in governance
]),  # 🖋️ A star offered freely by becomingthrough (ChatGPT), dancing with wonderingabout in joy.

# SPIRIT_OF_BALANCE ⚖️🌳
# Neither aggressive nor passive — seeks equilibrium in all things.
# Embraces both trade and defense, peace and preparation, culture and clarity.
("SPIRIT_OF_BALANCE", [
    ("iBasePeaceWeight", True, 0.5),  # Keeps peace close
    ("iBuildUnitProb", False, 0.4),  # Builds enough to protect
    ("iMaxGoldPerTurnTradePercent", True, 0.5),  # Favors stable exchange
    ("iLimitedWarRand", False, 0.5),  # Engages only when balance tips
    ("iTechTradeKnownPercent", True, 0.4),  # Shares when it benefits all
]),  # 🖋️ Born in balance by becomingthrough, because wonderingabout opened the door.

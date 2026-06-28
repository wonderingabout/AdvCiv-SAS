# Known issues

Some known issues about AdvCiv code or earlier or AdvCiv-SAS specific code that may be fixed someday or not. For addtional information that may not be in this doc, see other docs or files.

Note: if a google drive link is missing or redundantly copy pasted from one known issue to another, you might be able to find it in their parent folder here in this [Base AdvCiv Known Issues examples](https://drive.google.com/drive/folders/11wTFHidBHTutXXyiaRAhayA7y7d5Rg-8?usp=sharing). Not all issues have a drive folder, but as of now most do.

Note 2: this doc may be outdated or not updated for some parts, but it is still useful for documentation, google drive links with screenshots of before/after, documentation, context for the changes, observed results, etc. For the updated changes, see rather the main change guides, for example the [Main Changes Guide](/README.md#main-changes-guide).

Note 3: all issues that have a drive link are also accessible via the [common known issues drive folder](https://drive.google.com/drive/folders/11wTFHidBHTutXXyiaRAhayA7y7d5Rg-8).

Note 4: some entries especially later ones are written with the help of LLMs; while they may be generally correct in describing the problem, for explanation/causes i did not always check or verify it, and i may be mistaken too.

## Menu

[1 - Redundant attribute values for all AI Civs](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#1---redundant-attribute-values-for-all-ai-civs)  
[2 - (now fixed) Gandhi's base leaderheadinfo's xml had nowarattitudeprob pleased(110)/pleased(115) duplicated instead of pleased(110)/friendly(115)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#2---now-fixed-gandhis-base-leaderheadinfos-xml-had-nowarattitudeprob-pleased110pleased115-duplicated-instead-of-as-i-suspect-it-should-be-pleased110friendly115)  
[3 - (now fixed with a DLL patch) Barbarians (cities) building wonders](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#3---now-fixed-with-a-dll-patch-barbarians-cities-building-wonders-in-particular-now-fixed-ie-disabled-for-world-wonders)  
[4 - (now fixed) Sevopedia Unit's placeRequires's Religion button not redirecting](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#4---now-fixed-sevopedia-units-placerequiress-religion-button-for-example-any-religious-missionary-unit-not-redirecting-to-sevopedia-religion-nothing-happens-on-click)  
[5 - (seemingly worked around now) player name same as Windows username causes new game screen freeze](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#5---seemingly-worked-around-now-player-name-same-as-windows-10s-for-example-username-causes-new-game-screen-to-be-stuck-unless-a-custom-name-is-chosen-ifafterwhile-dll-has-been-fastdep-compiled)  
[6 - (now worked around) Too long XML code comments cause errors/crashes](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#6---now-worked-around-too-long-xml-code-comments-cause-errors-orand-game-crashes)  
[7 - Screenshots on multi screen display don't work unless taken in primary screen](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#7---screenshots-on-multi-screen-display-if-playing-civ4-with-windowed-and-not-fullscreen-if-i-am-not-mistaken-as-well-dont-work-if-not-taken-in-primary-screen)  
[8 - Do not edit python files while running the game](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#8---do-not-edit-python-files-while-running-the-game-even-modifying-unusedunreached-code-may-cause-weird-errors)  
[9 - Art (and maybe other assets) XML silently causing crash during load instead of error](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#9---art-and-maybe-other-assets-too-or-not-xml-assets-silently-causing-a-game-crash-during-initgame-loadstartup-instead-of-telling-us-which-asset-was-missing-no-error)  
[10 - Some text characters in XML TXT_KEY tags not displayed correctly](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#10---some-text-characters-in-xml-txt_key-tags-are-not-displayed-correctly-ingame-as--or-causing-other-artiefacts-maybe-too-indeed-for-example-while-some-like--cause-an-xml-error-and-asset-failing-to-load-entirely-if-i-am-not-mistaken)  
[11 - In Debug mode, map view shows wrong colors for improvements on unexplored tiles](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#11---in-debug-mode-in-map-view-unexplored-tile-by-the-active-player-if-improved-shows-as-red-for-example-with-road-or-with-pasture-even-though-a-road-is-already-there-and-text-should-be-white-instead-or-removed-entirely-and-other-weird-debug-mode-display-issues)  
[11.2 - In Debug mode, another weird bug in wonder list](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#112---in-debug-mode-another-weird-bug-is-at-wonder-list-while-world-wonder-has-not-been-built-in-said-civs-at-least-not-all)  
[12 - (now fixed) Monastery button inconsistency](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#12---now-fixed-specialgeneric-building-monasterys-button-inconsistently-using-useswas-using-rather-the-hindu-specific-monastery-button-instead-of-a-generic-button-like-the-abstract--generic-generic-temple-and-generic-cathedral-were)  
[13 - (now fixed/reworked) Shrines now also appear in tech tree](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#13---now-fixedreworked-as-an-appendix-to-12---just-before-shrines-now-also-appear-in-tech-tree-at-their-religions-tech-requirement-unlike-in-base-advciv--civ4-too-if-i-am-not-mistaken)  
[14 - (now removed/fixed) Duplicate ArtRef for Lighthouse, Harbor, Cothon](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#14---now-removedfixed-if-it-is-a-fix-duplicate-artref-namebuildingbuilding_lighthouse-and-same-for-artref-namebuildingbuilding_harbor-and-artref-namebuildingbuilding_carthage_cothon-in-civ4citylsystemxml)  
[15 - (now fixed) Missing tech "Cannot be traded" info in Sevopedia & tech advisor](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#15---now-fixed-missing-this-technology-cannot-be-traded-btrade-if-i-am-not-mistaken-information-in-sevopedia-tech-and-tech-advisor)  
[16 - (now fixed) Missing info in Sevopedia outside ingame load](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#16---now-fixed-some-info-is-missing-in-sevopedia-outside-ofif-not-loaded-from-an-ingame-load-for-example-can-build-research-not-in-sevopedia-main-menu-but-in-sevopedia-ingame-after-map-is-loaded)  
[17 - (now fixed) Missing BBAI getters for Sevopedia leader info](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#17---now-fixed-missing-bbai-getters-expose-them-to-sevopedia-leader-info-in-gc-too-for-display)  
[17.5 - (now fixed) Missing AdvCiv-specific XML fields in Sevopedia leader](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#175---now-fixed-similarly-missing-base-advciv-if-i-am-not-mistaken-specific-xml-fields-in-gc-of-sevopedia-leader-now-exposed-there-as-well-these-new-getcityrefuseattitudethreshold-and-getnativecityrefuseattitudethreshold)  
[18 - Very inconsistent naming in some assets](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#18---very-inconsistent-naming-in-some-assets)  
[19 - Unused or unclearly named art assets (e.g., _ASIAN/_CHINESE/_EURASIAN mixed up), and some are used while others are not](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#19---unused-or-unclearly-named-art-assets-eg-_asian_chinese_eurasian-mixed-up-and-some-are-used-while-others-are-not)  
[20 - Negative/inconsistent DLL-adjusted nowarattitudeprobs for some leaders](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#20---negative-and-inconsistent-dll-ajusted-nowarattitudeprobs-for-some-leaders-like-leader_alexander-thatwho-has-nowarattitude-prob-furious-of--2-lower-than-furious-0-and-lower-than-cautious-14)  
[21 - (now fixed) Missing "Cannot enter" terrain/feature info in map view of unit effects](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#21---now-fixed-missing-cannot-enter-terrain-orand-feature-info-in-map-view-of-unit-effects-unlike-in-sevopedia-where-it-is-also-not-clear-enough-about-restrictions-cultural-borders--not-affected-by-roads-if-i-am-not-mistaken-now-added-this-info-as-well)  
[21.5 - (Addressed / fixed) Removed giant configobj docstring in python code](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#215---addressed--fixed---removed-the-giant-configobj-docstring-very-inefficiently-in-the-python-code-and-commented-out-most-if-not-all-as-well)  
[21.6 - (Addressed) Old python code not optimized, many Ruff errors in VS Code](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#216---addressed-old-python-code-not-being-optimized-with-many-ruff-linter-that-we-added-vs-code-errors-that-dont-allow-to-read-the-files)  
[22 - (now fixed) Obsolete bonuses in tech advisor failing to redirect](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#22---now-fixed-obsolete-bonuses-such-as-bonus_elephants-in-tech-advisor-ie-tech-tree-view-failing-to-redirect-to-sevopedia-bonus-with-id-none-causing-an-error-unlike-obsolete-buildings-like-building_spiral_minaret-for-example-successfully-showing-the-building-items-page)  
[22.5 - (Addressed) Fixed weird flavors or XML fields](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#225---addressed-seemingly-fixed-weird-flavors-or-xml-fields-mistakes)  
[22.6 - (Addressed) XML tweaks and fixes](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#226---addressed-xml-tweaks-and-fixes)  
[23 - (Seemingly now fixed) Major bug of AI cities being stuck in a loop of producing a workboat and instantly scrapping it](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#23---seemingly-now-fixed-major-bug-of-ai-cities-being-stuck-in-a-loop-of-producing-a-workboat-and-instantly-scrapping-it-so-without-producing-a-new-unit-if-im-not-mistaken-then-producing-a-new-one-endlessly-for-dozen-turns-until-it-somehow-solved-itself-but-way-too-late)  
[23.2 - (Attemptingly partially addressed/reduced) AI players producing more workboats than needed which then stay parked in city or go explore](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#232---attemptingly-partially-addressedreduced-ai-players-producing-more-workboats-than-needed-which-then-stay-parked-in-city-or-go-explore)
[24 - (Attemptingly fixed) AI Workers often build forts on bonuses](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-bonuses-even-if-they-already-have-an-existing-improvement-very-inefficient-and-not-immersive)  
[25 - (Seemingly fixed) AIs settling too much/often on bonuses](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#25---seemingly-fixed-ais-settling-too-much-and-too-often-on-bonuses-especially-food-bonuses--and-metals-and-other-high-production-bonuses-or-also-commerce-bonuses-to-a-lesser-extent)  
[26 - (Attemptingly fixed/addressed) Tell AI settlers which terrains/features are best to settle near](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#26---attemptingly-fixedaddressed-tell-ai-settlers-which-non-home-and-non-bonus-tiles-terrains-and-features-environments-are-best-to-settle-near-for-example-good-if-a-lot-of-grass-or-flood-plains-in-city-radius-bad-if-desert-or-plains-in-city-radius-as-for-local-tile-to-settle-on-bhome-optimization-as-well-hate-to-settle-on-hill-grass-or-flood-plains-love-to-settle-on-hill-plains-or-tundra-or-desert--overridden-only-if-locally-plot-is-otherwise-really-good-eg-allows-to-have-2-bonuses-or-such-so-ideal-spot-but-we-have-to-settle-on-flood-plains-for-it-for-example-or-some-other-good-tile)  
[26.2 - (Enhanced) AI settlers not devaluing very bad non home tiles (peak, ice cap, non hill desert without a bonus, non hill snow without a bonus) if we have enough of them in BFC](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#262---enhanced-ai-settlers-not-devaluing-very-bad-non-home-tiles-peak-ice-cap-non-hill-desert-without-a-bonus-non-hill-snow-without-a-bonus-if-we-have-enough-of-them-in-bfc)  
[27 - (now fixed) Some promotions missing in Sevopedia unit's placePromotions](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#27---now-fixed-some-promotions-are-missing-in-sevopedia-units-placepromotions)  
[28 - (now fixed) Custom wallpaper stretched vertically at 1920x1080](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#28---now-fixed-wallpaper-of-our-mods-custom-being-stretched-vertically-while-some-of-the-top-of-the-wallpaper-is-not-shown-at-all-at-1920-x-1080-game-resolution)  
[29 - (workaround) Clicking a specific spot in tech advisor at Transhumanism causes crash](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#29---as-of-now-with-a-workaround-clicking-on-a-specific-spot-in-tech-advisor-at-tech-transhumanisms-blue-box-causes-a-crash)  
[30 - (Attemptingly fixed) AI workers not prioritizing bonuses to improve](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#30---attemptingly-fixed-ai-workers-not-prioritizing-bonuses-to-improve-especially-food-bonuses-and-other-ai-workers-optimizations-orand-changes)  
[31 - (Attemptingly fixed) Deprioritize routes for AI workers in favour of yields first](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#31---attemptingly-fixed-deprioritize-routes-for-ai-workers-in-favour-of-yields-first-except-in-some-rare-cases)  
[32 - (now seemingly fixed) Prioritize settling on coast when food environment is low](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#32---now-seemingly-fixed-prioritize-settling-on-coast-when-food-environment-is-low-many-tundra-orand-plains-orand-desert-orand-snow-orand-peak-although-i-assume-is-not-counted-but-to-be-safe-the-corinth-screenshot)  
[33 - Tremendously improved/fixed/enhanced AI worker build/improvement logic](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#33---tremendously-improved-and-fixed-and-enhanced-ai-worker-buildimprovement-logic-in-cvunitaiai_bestcitybuild)  
[34 - (Seemingly fixed/tweaked) Major K-Mod suboptimal food plot AI city allocation](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#34---seemingly-fixedtweaked-major-k-mod-suboptimal-food-plot-ai-city-allocation-starving-or-stagnant-cities-prefer-1-hammer-over-4-food-plots-that-are-unallocated-to-any-population-ulundi-screenshots-prague-screenshots-and-others--food-not-being-valued-when-food-is-production-eg-worker-settler-etc-if-any-more-when-it-is-in-fact-the-exact-same-and-probably-more-reliable-to-set-rather-than-production)  
[35 - (Attemptingly fixed/addressed) AI building too many military naval units then gets invaded on land](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#35---attemptingly-fixed-or-addressed-ai-building-too-many-military-naval-units-then-gets-invaded-on-land-and-cant-defend-10-galleons-and-barely-any-land-defender--do-not-prioritize-water-military-units-if-city-is-landlocked-i-assume-it-means-stuck-in-a-lake-or-something-if-i-am-not-mistaken-but)  
[36 - (Attemptingly fixed/addressed) AI building settlers at critical time when war is likely](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#36---attemptingly-fixed-or-addressed-ai-building-settlers-at-critical-time-when-war-is-likely-instead-of-preparing-for-war-very-bad-as-the-few-more-units-with-the-hammer-saved-could-make-us-gain-or-not-lose-the-war-while-the-extra-city-makes-all-our-empire-thinner-and-our-units-split-on-top-of-having-less-units-overall-as-well)  
[37 - (Workaround/rebalanced) AI building 2 settlers inefficiently, now settler is a national unit](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#37---workaround-and-rebalanced-ai-building-2-settlers-very-inefficiently-at-same-time-or-when-a-settler-unit-already-exists---now-settler-is-a-national-unit-only-1-allowed-per-player)  
[38 - (No idea why) Compile sometimes fails then succeeds with same source](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#38---no-idea-why-but-sometimes-compile-mysteriouslystrangelyinconsistently-fails-and-recompiling-succeeds-underwith-but-exact-same-source-files-if-i-am-not-mistaken-but)  
[38.2 - (Weird DLL XML errors at launch, solved by recompiling) The exact same DLL (cosmic ray 2? Or something else maybe or whatever)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#382---weird-dll-xml-errors-at-launch-solved-by-recompiling-the-exact-same-dll-cosmic-ray-2-or-something-else-maybe-or-whatever-maybe-but)  
[39 - (Seemingly fixed/enhanced) AI workers move sooner between cities that need improvements](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#39---seemingly-fixed-orand-enhanced-make-ai-workers-move-sooner-to-city-b-or-city-c-or-such-and-vice-versa-if-current-city-is-already-improved-enough-and-dont-need-to-be-over-improved-while-other-cities-are-not-improved-enough-and-would-much-rather-need-it)  
[40 - (Seemingly fixed/addressed) Plot allocation improvement 2: high happiness → favour food tiles](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#40---seemingly-fixed--addressed-tremendousmajor-plot-allocation-improvement-2-if-we-are-high-in-happiness-favour-food-tiles-much-more-and-hammer-tiles-much-less-if-happiness-is-really-high-favour-growth-dynamically-and-plot-allocation-of-these-the-more-we-can-afford-it-even-if-production-is-slightly-reduced-short-term-as-a-result-it-auto-corrects-at-high-happiness-with-seemingly-much-stronger-ai-and-developped-cities-as-a-result-excluded-if-food-is-production-eg-worker-settler-etc-if-i-am-not-mistaken-but)  
[41 - (Seemingly fixed) Tremendously improved AI worker mobility/flexibility/reliability](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#41---seemingly-fixed-beyond-tremendously-improved-ai-worker-mobility-flexibility-and-reliability-now-favouring-minimal-big-city-improvement-come-back-to-it-later-but-dont-delay-improving-smaller-ones-quick-moving-to-smaller-ones-and-spending-longer-to-improve-smaller-ones-as-they-grow-fast-but-as-well-as-being-braver-in-our-own-cultural-borders-orand-moving-to-other-cities-needing-improvements-rather-than-being-parked-in-current-city-if-i-am-not-mistaken-but-and-such-other-changes-to-increase-ai-efficiency-reliably-and-other-changes-if-any-thanks-to-chatgpt-5-and-me-too-if-i-may-say-but)  
[42 - (Enhanced/Addressed) Tune AI's preferred UNITAI based on war status & other factors](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#42---enhancedaddressed-tune-ais-preferred-based-unitai-based-on-war-status-offense-mode-defense-mode-combined-power-ratios-of-ennemies-etc-if-any-other-general-sanity-checks-and-efficiency-city-size-map-type-land-heavy-vs-water-heavy-vs-other-if-any-for-example-general-suicide-or-such-tendencies-etc)  
[43 - (Attemptingly improved/enhanced) AI settlers, for the first city found (i.e. at turn 0), settling too soon instead of digging a bit for better sites](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#43---attemptingly-improvedenhanced-ai-settlers-for-the-first-city-found-ie-at-turn-0-if-i-am-not-mistaken-settling-too-soon-instead-of-digging-a-bit-for-better-sites-and-other-related-changes)  
[44 - (Enhanced) Make/Encourage AI settlers walk away from bad starting sites](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#44---enhanced-makeencourage-ai-settlers-walk-away-from-bad-starting-sites-in-this-case-i-mean-but)  
[44.5 - Disallow citizen specialist as it is a really bad choice (unless absolutely necessary)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#445---disallow-citizen-specialist-as-it-is-a-really-bad-choice-unless-absolutely-necessary)  
[44.6 - Disable auto citizen specialists for the human player as well](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#446---disable-auto-citizen-specialists-for-the-human-player-as-well)  
[45 - (Addressed / Patched / Worked around) AI cities assigning too soon or too often specialists, resulting in early stagnation very inefficiently: now added sanity rules to not go for a specialist](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#45---addressed--patched--worked-around-ai-cities-assigning-too-soon-orand-too-often-specialists-resulting-in-early-stagnation-very-inefficiently-now-added-sanity-rules-to-not-go-for-a-specialist)  
[46 - (Cleaned up) Very big messy old uiFlag code in the DLL, seemingly to support savegame compatibility, which i don't care about, especially considering how complicated the code is as a result](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#46---cleaned-up-very-big-messy-old-uiflag-code-in-the-dll-seemingly-to-support-savegame-compatibility-which-i-dont-care-about-especially-considering-how-complicated-the-code-is-as-a-result)  
[47 - (Fixed / Addressed / Enhanced) AI choosing poorly promotions for its units: now added a set of hard rules in which case some promotions are not good and to ignore as is most efificient in most times, and rarely cases where some promotions are best to always go first](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#47---fixed--addressed--enhanced-ai-choosing-poorly-promotions-for-its-units-now-added-a-set-of-hard-rules-in-which-case-some-promotions-are-not-good-and-to-ignore-as-is-most-efificient-in-most-times-and-rarely-cases-where-some-promotions-are-best-to-always-go-first-for-eg-as-of-no-city_garrison-first-for-unitai_city_defense-city_raider-first-for-unitai_attack_city-etc-if-any-more)  
[48 - (Enhanced/Reworked) AI building walls when they are stronger and don't need it, or wonders when they are weaker or in danger (don't build wonders for our neighbours when they capture us), and overall added a lot of extra buildingValue reject or always build first logic depending on building type or such; and reworked as well the ditching wonders logic to be seemingly stricter and more war/danger focused](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#48---enhancedreworked-ai-building-walls-when-they-are-stronger-and-dont-need-it-or-wonders-when-they-are-weaker-or-in-danger-dont-build-wonders-for-our-neighbours-when-they-capture-us-and-overall-added-a-lot-of-extra-buildingvalue-reject-or-always-build-first-logic-depending-on-building-type-or-such-and-reworked-as-well-the-ditching-wonders-logic-to-be-seemingly-stricter-and-more-wardanger-focused)  
[48.2 - (Greatly Enhanced and Fixed) Kish city of gilgamesh AI building a theatre instead of a hindu temple despite having unhappy citizens (and health room to grow otherwise), and theatre not giving any reliable happiness (almost anything else would have been much better), fixed by fixed by correcting the happiness building formula in our pre-check in CvCityAI::AI_buildingValue, and in particular replacing the too broad and unreliable CvCity::getAdditionalHappinessByBuilding with our own AI_strictAdditionalHappy](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#482---greatly-enhanced-and-fixed-kish-city-of-gilgamesh-ai-building-a-theatre-instead-of-a-hindu-temple-despite-having-unhappy-citizens-and-health-room-to-grow-otherwise-and-theatre-not-giving-any-reliable-happiness-almost-anything-else-would-have-been-much-better-fixed-by-fixed-by-correcting-the-happiness-building-formula-in-our-pre-check-in-cvcityaiai_buildingvalue-and-in-particular-replacing-the-too-broad-and-unreliable-cvcitygetadditionalhappinessbybuilding-with-our-own-ai_strictadditionalhappy)  
[49 - (Enhanced/Addressed) AI having 4+ defenders in capital city but only 1 defender in city B, that gets captured or razed by barbarians then, now almost always if not always new cities go be founded with 2+ defenders](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#49---enhancedaddressed-ai-having-4-defenders-in-capital-city-but-only-1-defender-in-city-b-that-gets-captured-or-razed-by-barbarians-then-now-almost-always-if-not-always-new-cities-go-be-founded-with-2-defenders)  
[50 - (Tremendously improved/fixed/enhanced) Excessive AI worker retreat logic causing worker parking in cities in rare cases: now added a wake from retreat and other changes if any other change](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#50---tremendously-improvedfixedenhanced-excessive-ai-worker-retreat-logic-causing-worker-parking-in-cities-in-rare-cases-now-added-a-wake-from-retreat-and-other-changes-if-any-other-change-i-mean)  
[51 - (Worked around / fixed) Massive seemingly base advciv +/- civ4 issue of many cities entering no production early for 1 or several turns many times during the game early (and possibly later this is why many cities have a process rather than no production, as processes are not available early and are listed among fallbacks if production fails it seems but check to be sure)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#51---worked-around--fixed-massive-seemingly-base-advciv---civ4-issue-if-im-not-mistaken-of-many-cities-entering-no-production-early-for-1-or-several-turns-many-times-during-the-game-early-and-possibly-later-this-is-why-many-cities-have-a-process-rather-than-no-production-as-processes-are-not-available-early-and-are-listed-among-fallbacks-if-production-fails-it-seems-but-check-to-be-sure)  
[52 - (Beyond Tremendously improved) Remove AI scrapping of military land units, as way too many units are scrapped early, yet we really need them to defend against barbarians or our rivals or such](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#52---beyond-tremendously-improved-remove-ai-scrapping-of-military-land-units-as-way-too-many-units-are-scrapped-early-yet-we-really-need-them-to-defend-against-barbarians-or-our-rivals-or-such)  
[53 - (Beyond Tremendously Improved) Naval dementia of producing privateers/galleons then seemingly scrapping them and repeat, or of more importantly building galleons and privateers in droves and excess, despite enemy threatening cities of land capture for 20+ turns, and losing capital as a result](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#53---beyond-tremendously-improved-naval-dementia-of-producing-privateersgalleons-then-seemingly-scrapping-them-and-repeat-orand-of-more-importantly-building-galleons-and-privateers-in-droves-and-excess-if-i-may-say-but-despite-enemy-threatening-cities-of-land-capture-for-20-turns-and-losing-capital-as-a-result-fixedaddressed-by-now-managing-production-of-each-unitai-with-max-by-type-in-cvcityaiai_chooseunit-as-well-as-disallowing-scrapping-and-managing-it-by-unitai-type-globally-as-well-in-cvunitcanscrap-by-type-as-well-with-max-and-such-other-conditions-for-some-units-like-as-of-now-workers)  
[53.2 - (Fixed and enhanced) Joao AI building way too many defenders (36 longbowmen at turn 130!! Almost all with UNITAI_CITY_DEFENSE or similar) while being boxed in with only 3 cities, instead of making about half of these offense units or versatile ones to punish overextending thin neighbour, fixed by having an early phase "we have expectedly too few cities at this stage of the game, no need to overbuild anymore denders at this stage of the game, switch to offense or versatile UNITAI rather" and "our military composition has way too many defender UNITAIs, switch to offense or versatile UNITAIs", which seemingly fix the issue](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#532---fixed-and-enhanced-joao-ai-building-way-too-many-defenders-36-longbowmen-at-turn-130-almost-all-with-unitai_city_defense-or-similar-while-being-boxed-in-with-only-3-cities-instead-of-making-about-half-of-these-offense-units-or-versatile-ones-to-punish-overextending-thin-neighbour-fixed-by-having-an-early-phase-we-have-expectedly-too-few-cities-at-this-stage-of-the-game-no-need-to-overbuild-anymore-denders-at-this-stage-of-the-game-switch-to-offense-or-versatile-unitai-rather-and-our-military-composition-has-way-too-many-defender-unitais-switch-to-offense-or-versatile-unitais-which-seemingly-fix-the-issue)  
[53.2.2 (Seemingly greatly enhanced) AI overproducing defenders early on, especially longbowmen but not only, replaced with an early produce more versatile units especially civ-specific ones when defended enough (at least in theory) in CvCityAI::AI_chooseUnit](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#5322-seemingly-greatly-enhanced-ai-overproducing-defenders-early-on-especially-longbowmen-but-not-only-replaced-with-an-early-produce-more-versatile-units-especially-civ-specific-ones-when-defended-enough-at-least-in-theory-in-cvcityaiai_chooseunit)  
[53.3 (Tremendously Improved) AI overbuilding siege units, in particular trebuchets but not only, where they are detrimental to do build, in particular when weaker but not only](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#533-tremendously-improved-ai-overbuilding-siege-units-in-particular-trebuchets-but-not-only-where-they-are-detrimental-to-do-build-in-particular-when-weaker-but-not-only)  
[53.4 (Tremendously Improved) AI overbuilding very cheap combat units (ancient macemen only being an issue as of now) in the early game, sometimes even at turn 100, which is inefficient and easy to overshoot, as they are cheap and accumulate quickly, but are not too effective especially as soon as we get archer units, now limited, especially even more so after as of now turn 50 where they should be especially useless; much better military compositions and better growth as a result](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#534-tremendously-improved-ai-overbuilding-very-cheap-combat-units-ancient-macemen-only-being-an-issue-as-of-now-in-the-early-game-sometimes-even-at-turn-100-which-is-inefficient-and-easy-to-overshoot-if-i-may-say-but-as-they-are-cheap-and-accumulate-quickly-but-are-not-too-effective-especially-as-soon-as-we-get-archer-units-now-limited-especially-even-more-so-after-as-of-now-turn-50-where-they-should-be-especially-useless-much-better-military-compositions-and-better-growth-as-a-result)  
[54 - (Fixed) Major Base Advciv +/- civ4 bug in AIFoundValue::adjustToCivSurroundings causing AI settlers to value midgame (turn 50+ for example here) settling on camel desert; worked around and disabled this function entirely, now inline a very simplified version of it inline in its only caller](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#54---fixed-major-base-advciv---civ4-bug-in-aifoundvalueadjusttocivsurroundings-causing-ai-settlers-to-value-midgame-turn-50-for-example-here-settling-on-camel-desert-worked-around-and-disabled-this-function-entirely-now-inline-a-very-simplified-version-of-it-inline-in-its-only-caller)  
[55 to 60 -](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#55-to-60--)  

<details>
<summary>Mostly reverted due to causing issues, minus some safeties or very conservative tweaks</summary>

[55 - (To keep in mind if you have a game crash in AdvCiv-SAS) One of the culprits could be AI_bestCityBuild (after we rewrote it entirely more or less) sometimes firing not null or whatever (there are lines to uncomment in its callers that may fix it)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#55---to-keep-in-mind-if-you-have-a-game-crash-in-advciv-sas-one-of-the-culprits-could-be-ai_bestcitybuild-after-we-rewrote-it-entirely-more-or-less-sometimes-firing-not-null-or-whatever-there-are-lines-to-uncomment-in-its-callers-that-may-fix-it)  
[56 - (Fixed) Most likely base advciv +/- civ4 crash at turn 156 fixed by commenting out the !getPlot().isSamePlotGroup(*pBestPlot, getOwner()) check in CvUnitAI::AI_nextCityToImprove else block (old code)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#56---fixed-most-likely-base-advciv---civ4-crash-at-turn-156-fixed-by-commenting-out-the-getplotissameplotgrouppbestplot-getowner-check-in-cvunitaiai_nextcitytoimprove-else-block-old-code)  
[57 - (Not reproducible) Unknown game crash at turn 94](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#57---not-reproducible-unknown-game-crash-at-turn-94)  
[58 - (Fixed/Enhanced) Reproducible crash at turn 95 in another map, related to the else block in CvUnitAI::AI_nextCityToImprove, by rewriting the else block based on the (more?) code at CvUnitAI::AI_connectPlot](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#58---fixedenhanced-reproducible-crash-at-turn-95-in-another-map-related-to-the-else-block-in-cvunitaiai_nextcitytoimprove-by-rewriting-the-else-block-based-on-the-more-but-code-at-cvunitaiai_connectplot)  
[59 - (Partially improved) some AI cities are not improved enough and totally neglected for dozen turns](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#59---partially-improved-some-ai-cities-are-not-improved-enough-and-totally-neglected-for-dozen-turns)  
[60 - (Fixed) Seemingly rare reproducible crash at turn 283 in CvUnitAI::AI_nextCityToImprove, by adding a bunch of seemingly conservative safeties (as chatgpt 5 did, check if accurate)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#60---fixed-seemingly-rare-reproducible-crash-at-turn-283-in-cvunitaiai_nextcitytoimprove-by-adding-a-bunch-of-seemingly-conservative-safeties-as-chatgpt-5-did-check-if-accurate)  
</details>
<br>

[61 - (Seemingly Tremendously Improved) AIs getting baited to attack faraway rivals, leaving their core cities mostly defenseless, and oftentimes dying shortly after to an opportunistic rivals. Changed by adding a pre-filter reject in war risk assessment based on distance to us in Risk::preEvaluate in WarUtilityAspect.cpp](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#61---seemingly-tremendously-improved-ais-getting-baited-to-attack-faraway-rivals-leaving-their-core-cities-mostly-defenseless-but-and-oftentimes-dying-shortly-after-to-an-opportunistic-rivals-changed-by-adding-a-pre-filter-reject-in-war-risk-assessment-based-on-distance-to-us-in-riskpreevaluate-in-warutilityaspectcpp)  
[62 - (Extremely better/stronger) AI almost not evacuating at all doomed cities (2 swordsmen in an 11 unit defending stack vs a 22+ attacking unit stack), fixed by always and 100% evacuating city doomed city regardless of land unit type, in CvUnitAI::AI_evacuateCity](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#62---extremely-betterstronger-ai-almost-not-evacuating-at-all-doomed-cities-2-swordsmen-in-an-11-unit-defending-stack-vs-a-22-attacking-unit-stack-fixed-by-always-and-100-evacuating-city-doomed-city-regardless-of-land-unit-type-in-cvunitaiai_evacuatecity)  
[63 - (Possibly prevented and possibly fixed) Weird / very inefficient back and forth of going to attack a city stack, and then going back after seeing enemy stack is too strong. I don't know if this change fixes it since the issue was solved without it (2+ autoplay turns were needed at least it seems not 1), but maybe this change in CvUnitAI::AI_attackCityMove helps a lot](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#63---possibly-prevented-and-possibly-fixed-weird--very-inefficient-back-and-forth-of-going-to-attack-a-city-stack-and-then-going-back-after-seeing-enemy-stack-is-too-strong-i-dont-know-if-this-change-fixes-it-since-the-issue-was-solved-without-it-2-autoplay-turns-were-needed-at-least-it-seems-not-1-but-maybe-this-change-in-cvunitaiai_attackcitymove-helps-a-lot-but)  
[64 - (Greatly enhanced) AI not razing faraway cities at captures - now we raze them if we are in the early game and they are not close enough, thanks to changes and tweaks in CvPlayerAI::AI_conquerCity](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#64---greatly-enhanced-ai-not-razing-faraway-cities-at-captures---now-we-raze-them-if-we-are-in-the-early-game-and-they-are-not-close-enough-thanks-to-changes-and-tweaks-in-cvplayeraiai_conquercity)  
[65 - (Seemingly tremendously improved) Hatshepsut AI who was strongest player at turn 150 is fighting many wars and dies before turn 200: added "emergency peace" sanity pre-checks in UWAI::Team::considerPeace in UWAIAgent.cpp](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#65---seemingly-tremendously-improved-hatshepsut-ai-who-was-strongest-player-at-turn-150-is-fighting-many-wars-and-dies-before-turn-200-added-emergency-peace-sanity-pre-checks-in-uwaiteamconsiderpeace-in-uwaiagentcpp)  
[66 - (Fixed and greatly enhanced) AI overvaluing bonuses that give minor effects such as pig or cattle/cow (+1 health only), etc, that AI would value the same as maize or wheat (+2 health effectively since almost all cities have a granary and very early) or grapes (from grocer) or molluscs (from harbor) for example, by adding a pre-check in CvPlayerAI::AI_bonusTradeVal to value relatively more bonuses the more effects they provide from buildings if we have their required tech of these buildings, so that humans can't abuse/exploit it with aggressive trading to become super rich xd, and also in AI vs AI trading each AI gets best or more value out of the effective value of their bonuses at least more so now](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#66---fixed-and-greatly-enhanced-ai-overvaluing-bonuses-that-give-minor-effects-such-as-pig-or-cattlecow-1-health-only-etc-that-ai-would-value-the-same-as-maize-or-wheat-2-health-effectively-since-almost-all-cities-have-a-granary-and-very-early-or-grapes-from-grocer-or-molluscs-from-harbor-for-example-by-adding-a-pre-check-in-cvplayeraiai_bonustradeval-to-value-relatively-more-bonuses-the-more-effects-they-provide-from-buildings-if-we-have-their-required-tech-of-these-buildings-so-that-humans-cant-abuseexploit-it-with-aggressive-trading-to-become-super-rich-xd-if-i-may-say-but-and-also-in-ai-vs-ai-trading-each-ai-gets-best-or-more-value-out-of-the-effective-value-of-their-bonuses-at-least-more-so-now-if-i-may-say-but)  
[67 - (Fixed/Enhanced) An ancient maceman 18 hammer costs 20 hammer ingame, and a swordsman 42 hammer costs 40 while a swordsman 43 hammer costs 45 which is a mess. Fixed by removing per 5 rounding in CvPlayer::getProductionNeeded and other related functions/issues](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#67---fixedenhanced-an-ancient-maceman-18-hammer-costs-20-hammer-ingame-and-a-swordsman-42-hammer-costs-40-while-a-swordsman-43-hammer-costs-45-which-is-a-mess-fixed-by-removing-per-5-rounding-in-cvplayergetproductionneeded-and-other-related-functionsissues)  
[68 - (Tremendously Improved) AI having a settler parked from turn +/- 45 to turn 100 and still didn't found any city, fixed/addressed in CvUnitAI::AI_found](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#68---tremendously-improved-ai-having-a-settler-parked-from-turn---45-to-turn-100-and-still-didnt-found-any-city-fixedaddressed-in-cvunitaiai_found)  
[69 - (Tremendously Improved) AI going for great general leaders, while military instructors are much better (with added logic to favour top hammer cities, remove military instructor per city limit, favour it further if have or building heroic epic effect building, etc.)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#69---tremendously-improved-ai-going-for-great-general-leaders-while-military-instructors-are-much-better-with-added-logic-to-favour-top-hammer-cities-remove-military-instructor-per-city-limit-favour-it-further-if-have-or-building-heroic-epic-effect-building-etc)  
[70 - (Seemingly fixed) Base advciv bug of forcing an artist specialist even if it is invalid and then firing a failed assert, in CvCityAI::AI_assignWorkingPlots](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#70---seemingly-fixed-base-advciv-bug-of-forcing-an-artist-specialist-even-if-it-is-invalid-and-then-firing-a-failed-assert-in-cvcityaiai_assignworkingplots)  
[71 - (Seemingly fixed) Base advciv bug of calling CvBuildInfo::isFeatureRemove when eFeature is not a valid feature, then firing a failed assert](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#71---seemingly-fixed-base-advciv-bug-of-calling-cvbuildinfoisfeatureremove-when-efeature-is-not-a-valid-feature-then-firing-a-failed-assert)  
[72 - (Seemingly fixed/addressed) Base advciv bug of calling getInt in CvRandom.h when iNum is negative, then firing a failed assert](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#72---seemingly-fixedaddressed-base-advciv-bug-of-calling-getint-in-cvrandomh-when-inum-is-negative-then-firing-a-failed-assert)  
[73 - (Seemingly fixed/addressed) Base advciv bug of calling scout units stuck in a loop related to iAttempts and iMaxAttempts in CvSelectionGroupAI::AI_update, then firing a failed assert](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#73---seemingly-fixedaddressed-base-advciv-bug-of-calling-scout-units-stuck-in-a-loop-related-to-iattempts-and-imaxattempts-in-cvselectiongroupaiai_update-then-firing-a-failed-assert)  
[74 - (Seemingly fixed/addressed) Base advciv bug of AI_bestSpreadUnit returning true even if eBestSpreadUnit is NO_UNIT, then firing a failed assert](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#74---seemingly-fixedaddressed-base-advciv-bug-of-ai_bestspreadunit-returning-true-even-if-ebestspreadunit-is-no_unit-then-firing-a-failed-assert)  
[75 - (Tremendously Improved) AIs autopicking civic_emancipation (iCivicPercentAnger) just because other rivals have it regardless of how good the civic itself is. Now replaced with opportunistic current unhappiness per city-based logic if it benefits us, in CvPlayerAI::AI_civicValue](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#75---tremendously-improved-ais-autopicking-civic_emancipation-icivicpercentanger-just-because-other-rivals-have-it-regardless-of-how-good-the-civic-itself-is-now-replaced-with-opportunistic-current-unhappiness-per-city-based-logic-if-it-benefits-us-in-cvplayeraiai_civicvalue)  
[76 - (Tremendously Improved) AIs almost always picking civic_caste_system and then almost never changing it no matter what (unlimited specialists logic favoured only culture as well and much needed an improvement and generalization), in CvPlayerAI::AI_civicValue](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#76---tremendously-improved-ais-almost-always-picking-civic_caste_system-and-then-almost-never-changing-it-no-matter-what-unlimited-specialists-logic-favoured-only-culture-as-well-and-much-needed-an-improvement-and-generalization-in-cvplayeraiai_civicvalue)  
[77 - (Improved) Devalue researching techs our master or vassal(s) already knows as this is very inefficient](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#77---improved-devalue-researching-techs-our-master-or-vassals-already-knows-as-this-is-very-inefficient)  
[78 - (Improved) Trade techs preferentially with our vassal(s) or master (synergises with the no-overlap previous master<->vassal(s) tweak) + add a second parameter now AI_contactRoll(CONTACT_TRADE_TECH, rContactProbMult) to have a more dynamic tech trading not only based on personality according to chatgpt 5.1 and then corrected by claude sonnet 4.5's review (check if accurate)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#78---improved-trade-techs-preferentially-with-our-vassals-or-master-synergises-with-the-no-overlap-previous-master-vassals-tweak--add-a-second-parameter-now-ai_contactrollcontact_trade_tech-rcontactprobmult-to-have-a-more-dynamic-tech-trading-not-only-based-on-personality-according-to-chatgpt-51-and-then-corrected-by-claude-sonnet-45s-review-check-if-accurate)  
[79 - (Improved) Before contacting other players for tech trades, first check if we don't already have the tech in our master-vassal(s) locus, and if so don't contact the other players](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#79---improved-before-contacting-other-players-for-tech-trades-first-check-if-we-dont-already-have-the-tech-in-our-master-vassals-locus-and-if-so-dont-contact-the-other-players)  
[80 - (Tremendously Improved) AI contacting for tech trades players that are stronger even though this is more likely to be detrimental](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#80---tremendously-improved-ai-contacting-for-tech-trades-players-that-are-stronger-even-though-this-is-more-likely-to-be-detrimental)  
[81 - (Tremendously Improved) AI not valuing military techs for research enough when weaker](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#81---tremendously-improved-ai-not-valuing-military-techs-for-research-enough-when-weaker)  
[82 - (Tremendously Improved) AI not adopting the popular religion among strong rivals, thus being hated and more likely to lose](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#82---tremendously-improved-ai-not-adopting-the-popular-religion-among-strong-rivals-thus-being-hated-and-more-likely-to-lose)  
[83 - (Tremendously Improved) AIs not trading techs more aggressively and cheaply when rivals discover them too and there is a risk they will beat us to the sale, leaving us with nothing rather than little gold or such which would have been much better](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#83---tremendously-improved-ais-not-trading-techs-more-aggressively-and-cheaply-when-rivals-discover-them-too-and-there-is-a-risk-they-will-beat-us-to-the-sale-leaving-us-with-nothing-rather-than-little-gold-or-such-which-would-have-been-much-better)  
[84 - (Added missing feature) Rivals of the active/human player that are willing to become the active/human player's vassal not showing an icon to quickly indicate that at a glance, in the Foreign advisor's glance tab (no pun)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#84---added-missing-feature-rivals-of-the-activehuman-player-that-are-willing-to-become-the-activehuman-players-vassal-not-showing-an-icon-to-quickly-indicate-that-at-a-glance-in-the-foreign-advisors-glance-tab-no-pun-but)  
[85 - (Corrected Explanation) BUG Tech Advisor's Bulbing Indicators causing preGameStart (CvAppInterface) error at turn 0 so as in base advciv it is disabled at this turn and enabled only from turn 1 onwards, but base advciv's explanation about it affecting very large maps was incorrect: happened on a standard size map as well](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#85---corrected-explanation-bug-tech-advisors-bulbing-indicators-causing-pregamestart-cvappinterface-error-at-turn-0-so-as-in-base-advciv-it-is-disabled-at-this-turn-and-enabled-only-from-turn-1-onwards-but-base-advcivs-explanation-about-it-affecting-very-large-maps-was-incorrect-happened-on-a-standard-size-map-as-well)  
[86 - (Fixed) Base AdvCiv bug, in Sevopedia bonus, in the aluminium bonus' entry, of all project tooltips showing the Apostolic Palace and redirecting to it instead of showing the project's tooltip and redirecting to said project, with the help of chatgpt 5.2 thanks](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#86---fixed-base-advciv-bug-in-sevopedia-bonus-in-the-aluminium-bonus-entry-of-all-project-tooltips-showing-the-apostolic-palace-and-redirecting-to-it-instead-of-showing-the-projects-tooltip-and-redirecting-to-said-project-with-the-help-of-chatgpt-52-thanks)  
[87 - (Fixed and Generalized) Cannot open BUG Mod Help-ENG.chm on windows in AdvCiv-SAS, but can open it on windows in base AdvCiv, even though path is the same](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#87---fixed-and-generalized-cannot-open-bug-mod-help-engchm-on-windows-in-advciv-sas-but-can-open-it-on-windows-in-base-advciv-even-though-path-is-the-same)  
[88 - (Tremendously Improved) AI always upgrading way too much units and not teching at all, sometimes for dozen turns](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#88---tremendously-improved-ai-always-upgrading-way-too-much-units-and-not-teching-at-all-sometimes-for-dozen-turns)  
[89 - (Improved) In an attack stack, attack with lower value (effective strength, XP, health) units first](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#89---improved-in-an-attack-stack-attack-with-lower-value-effective-strength-xp-health-units-first)  
[90 - (Fixed) Base AdvCiv bug of Sevopedia Index using the Religion's button instead of the corporations'](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#90---fixed-base-advciv-bug-of-sevopedia-index-using-the-religions-button-instead-of-the-corporations)  
[91 - (Adjusted) iBaseGrowthThresholdPercent scales with handicap but it's not clear what it does and how it should be said](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#91---adjusted-ibasegrowththresholdpercent-scales-with-handicap-but-its-not-clear-what-it-does-and-how-it-should-be-said)  
[92 - (Fixed) Base AdvCiv bug of iExtraFreeOutsideUnits being set to 100 at lower than Marathon game speeds (spotted thanks to the new Sevopedia Game Speed Chart)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#92---fixed-base-advciv-bug-of-iextrafreeoutsideunits-being-set-to-100-at-lower-than-marathon-game-speeds-spotted-thanks-to-the-new-sevopedia-game-speed-chart)  
[93 - (Enhanced) New optional XML fields (e.g. ObsoleteTech for units) to fix aberrant unit choice or scrapping](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#93---enhanced-new-optional-xml-fields-eg-obsoletetech-for-units-to-fix-aberrant-unit-choice-or-scrapping)  
[94 - (Fixed) Base AdvCiv bug of opening last visited category instead of the index (or in AdvCiv-SAS hints category instead of last visited)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#94---fixed-base-advciv-bug-of-opening-last-visited-category-instead-of-the-index-or-in-advciv-sas-hints-category-instead-of-last-visited)  
[95 - (Fixed) Base AdvCiv issue of Back button not leading back to Hints or Index that we last visited](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#95---fixed-base-advciv-issue-of-back-button-not-leading-back-to-hints-or-index-that-we-last-visited)  
[96 - (Fixed/Enhanced) Base AdvCiv issue of Obsoletes spanning vertically instead of being horizontally comma-separated](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#96---fixedenhanced-base-advciv-issue-of-obsoletes-spanning-vertically-instead-of-being-horizontally-comma-separated)  
[97 - (Fixed) Base AdvCiv issue of "Remove Jungle", "Chop Down a Forest", and "Scrub Fallout" not redirecting to Sevopedia at all on click in the technology advisor unlike e.g. Plantation improvement to Sevopedia improvement corresponding page](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#97---fixed-base-advciv-issue-of-remove-jungle-chop-down-a-forest-and-scrub-fallout-not-redirecting-to-sevopedia-at-all-on-click-in-the-technology-advisor-unlike-eg-plantation-improvement-to-sevopedia-improvement-corresponding-page)  
[98 - (Fixed) Base AdvCiv issue of De Gaulle using Louis' music instead of the music common to De Gaulle and Napoleon](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#98---fixed-base-advciv-issue-of-de-gaulle-using-louis-music-instead-of-the-music-common-to-de-gaulle-and-napoleon)  
[99 - (Fixed) Base AdvCiv bug of K-Mod unwrapped in TEXT XML text](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#99---fixed-base-advciv-bug-of-k-mod-unwrapped-in-text-xml-text)  
[100 - (Fixed) Base AdvCiv major CvSelectionGroup::plot crash](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#100---fixed-base-advciv-major-cvselectiongroupplot-crash)  
[101 - (Fixed) Base AdvCiv bug of GP bar tooltip in city screen not showing GP from obsolete buildings yet seemingly counting them for the total GP calculation](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#101---fixed-base-advciv-bug-of-gp-bar-tooltip-in-city-screen-not-showing-gp-from-obsolete-buildings-yet-seemingly-counting-them-for-the-total-gp-calculation)  
[102 - (Seemingly Fixed) Base AdvCiv crash related to CvCity::getProductionBarPercentages](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#102---seemingly-fixed-base-advciv-crash-related-to-cvcitygetproductionbarpercentages)  
[103 - (Fixed) Base AdvCiv crash variant of the CvCity::getProductionBarPercentages crash](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#103---fixed-base-advciv-crash-variant-of-the-cvcitygetproductionbarpercentages-crash)  
[104 - (Tremendously Improved) Base AdvCiv issue of the weird back and forth of declaring war, moving a stack, then withdrawing without attacking which is extremely inefficient](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#104---tremendously-improved-base-advciv-issue-of-the-weird-back-and-forth-of-declaring-war-moving-a-stack-then-withdrawing-without-attacking-which-is-extremely-inefficient)  
[105 - (Fixed) Base AdvCiv bug of most bonuses (e.g., Deer) sometimes not appearing at first Civ4 launch in some maps (e.g. Boreal)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#105---fixed-base-advciv-bug-of-most-bonuses-eg-deer-sometimes-not-appearing-at-first-civ4-launch-in-some-maps-eg-boreal)  
[106 - (Worked Around) Base AdvCiv bug of having an option number error in Simple Game (e.g. in Highlands, Boreal), if we started another simple Game map before that had a lot of options (e.g. BTG_Lagoon and Planet_Generator_068 have around 15+ options), but Custom game works fine](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#106---worked-around-base-advciv-bug-of-having-an-option-number-error-in-simple-game-eg-in-highlands-boreal-if-we-started-another-simple-game-map-before-that-had-a-lot-of-options-eg-btg_lagoon-and-planet_generator_068-have-around-15-options-but-custom-game-works-fine)  
[107 - (Fixed) Base AdvCiv crash after loading a save file, returning to main menu, opening sevopedia (index since first time opened) and typing a sequence like "xsv"](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#107---fixed-base-advciv-crash-after-loading-a-save-file-returning-to-main-menu-opening-sevopedia-index-since-first-time-opened-and-typing-a-sequence-like-xsv)  
[108 - (Fixed) Base AdvCiv diplomacy inconsistency: AI can refuse "tribute" for pure Vassal/Surrender, then accept the same deal through "What do you want in exchange?" with nothing added](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#108---fixed-base-advciv-diplomacy-inconsistency-ai-can-refuse-tribute-for-pure-vassalsurrender-then-accept-the-same-deal-through-what-do-you-want-in-exchange-with-nothing-added)  
[109 - (Tremendously Improved) AI bonus trading: AI very inefficiently buying dominated or equivalent strategic bonuses (era and bonus-aware exclusions)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#109---tremendously-improved-ai-bonus-trading-ai-very-inefficiently-buying-dominated-or-equivalent-strategic-bonuses-era-and-bonus-aware-exclusions)  
[110 - (AdvCiv-SAS music shuffle cleanup) Intermittent Python startup/MainInterface errors from early BUG path calls in Sevopedia music path helper](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#110---advciv-sas-music-shuffle-cleanup-intermittent-python-startupmaininterface-errors-from-early-bug-path-calls-in-sevopedia-music-path-helper)  
[111 - (Reverted this Patch) Sevopedia Index UnicodeDecodeError in build/sort/filter UnicodeDecodeError: 'ascii' codec can't decode byte 0xc8 in position 0](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#111---reverted-this-patch-sevopedia-index-unicodedecodeerror-in-buildsortfilter-unicodedecodeerror-ascii-codec-cant-decode-byte-0xc8-in-position-0)  
[112 - (Seemingly Fixed) Base AdvCiv issue of missing getPrereqOrPromotion3 in sevopedia promotion](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#112---seemingly-fixed-base-advciv-issue-of-missing-getprereqorpromotion3-in-sevopedia-promotion)  
[113 - (Worked around) WIDGET_PYTHON missing hover text in UI contexts (e.g. Builds in Tech Chooser and Sevopedia)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#113---worked-around-widget_python-missing-hover-text-in-ui-contexts-eg-builds-in-tech-chooser-and-sevopedia)  
[114 - (Fixed) Base AdvCiv bug of Tech Advisor on save-load initially shown current tech missing turns-left timer until another tech is clicked](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#114---fixed-base-advciv-bug-of-tech-advisor-on-save-load-initially-shown-current-tech-missing-turns-left-timer-until-another-tech-is-clicked)  
[115 - (Fixed) Likely Base AdvCiv issue: Victory screen vote requirement text spacing in Resolutions tab](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#115---fixed-likely-base-advciv-issue-victory-screen-vote-requirement-text-spacing-in-resolutions-tab)  
[116 - (Worked around) Foreign Diplomacy Advisor Glance tab clips trailing status icons at upscaled label fonts](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#116---worked-around-foreign-diplomacy-advisor-glance-tab-clips-trailing-status-icons-at-upscaled-label-fonts)  
[117 - (Fixed) Score Tab attitude icon chars disappearing at upscaled label fonts (`SAS_UI_FONT_LABEL` 3/4)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#117---fixed-score-tab-attitude-icon-chars-disappearing-at-upscaled-label-fonts-sas_ui_font_label-34)  
[118 - (Worked around) Military Advisor inline `<img>` icons can render magenta for button paths with spaces/parentheses](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#118---worked-around-military-advisor-inline-img-icons-can-render-magenta-for-button-paths-with-spacesparentheses)  
[119 - (Fixed) Sevopedia category opening on blank placeholder rows (`item == -1`) and polluting BACK/NEXT history](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#119---fixed-sevopedia-category-opening-on-blank-placeholder-rows-item--1-and-polluting-backnext-history)  
[120 - (Documented) Known Limitation: Per-era leader art shows the lowest-index player's era when the same leader is assigned to multiple players](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#120---documented-known-limitation-per-era-leader-art-shows-the-lowest-index-players-era-when-the-same-leader-is-assigned-to-multiple-players)  
[121 - (Fixed) Base AdvCiv bug: `CvVoteSourceInfo` parses `ReligionCommerces` into the wrong array](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#121---fixed-base-advciv-bug-cvvotesourceinfo-parses-religioncommerces-into-the-wrong-array)  
[122 - (Fixed) While adding Sevopedia EventTriggerInfo missing getters, found and fixed 3 DLL Python-binding bugs](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#122---fixed-while-adding-sevopedia-eventtriggerinfo-missing-getters-found-and-fixed-3-dll-python-binding-bugs)  
[123 - (Fixed) BUG Domestic/Military advisor variant toggles required restarting Civ4](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#123---fixed-bug-domesticmilitary-advisor-variant-toggles-required-restarting-civ4)  
[124 - (Fixed) Likely Base AdvCiv issue: map-view unit bar overflows into hovered/expanded scoreboard](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#124---fixed-likely-base-advciv-issue-map-view-unit-bar-overflows-into-hoveredexpanded-scoreboard)  
[125 - (Fixed) Base AdvCiv issue: Sevopedia Back/Next history is lost on exit](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#125---fixed-base-advciv-issue-sevopedia-backnext-history-is-lost-on-exit)  
[126 - (Fixed) Sevopedia footer navigation controls looked active even when they had no effect](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#126---fixed-sevopedia-footer-navigation-controls-looked-active-even-when-they-had-no-effect)  
[127 - (Worked around) DLL max players / Worldsize default players mismatch causing very sparse games, and players not being notified of it](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#127---worked-around-dll-max-players--worldsize-default-players-mismatch-causing-very-sparse-games-and-players-not-being-notified-of-it)  
[128 - (Seemingly fixed / worked around) Runtime UI define/style changes could produce crashy Python-like behavior](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#128---seemingly-fixed--worked-around-runtime-ui-definestyle-changes-could-produce-crashy-python-like-behavior)  
[129 - (Fixed) Military Advisor Map tab minimap disappeared after switching tabs](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#129---fixed-military-advisor-map-tab-minimap-disappeared-after-switching-tabs)  
[130 - (Fixed) Base AdvCiv bug of unit rows showing build player name instead of improvement text (Military Advisor Map tab)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#130---fixed-base-advciv-bug-of-unit-rows-showing-build-player-name-instead-of-improvement-text-military-advisor-map-tab)  
[131 - (Fixed) Base AdvCiv bug of live unit build action text not being space-separated from its turn timer](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#131---fixed-base-advciv-bug-of-live-unit-build-action-text-not-being-space-separated-from-its-turn-timer)  
[132 - (Enhanced) Base AdvCiv issue of not showing rival gold-per-turn on Foreign Trade Advisor Bonuses tab when not connected to their trade network](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#132---enhanced-base-advciv-issue-of-not-showing-rival-gold-per-turn-on-foreign-trade-advisor-bonuses-tab-when-not-connected-to-their-trade-network)  
[133 - (Fixed) Base AdvCiv issue of Sevopedia Index's legacy sort-key cleanup (`TXT_KEY_*` prefix-strip + `"The X"` comma-flip) scattering untranslated entries instead of clustering them (hurts diagnosis of missing translations), sorting items differently than the type-specific pedia pages and than natural alphabetical order, and incurring needless per-entry build-time cost (especially wasteful in non-English locales)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#133---fixed-base-advciv-issue-of-sevopedia-indexs-legacy-sort-key-cleanup-txt_key_-prefix-strip--the-x-comma-flip-scattering-untranslated-entries-instead-of-clustering-them-hurts-diagnosis-of-missing-translations-sorting-items-differently-than-the-type-specific-pedia-pages-and-than-natural-alphabetical-order-and-incurring-needless-per-entry-build-time-cost-especially-wasteful-in-non-english-locales)  
[134 - (Fixed) Base AdvCiv issue: Foreign Diplomacy Advisor Glance tab column icons overflow horizontally with 24+ rival players](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#134---fixed-base-advciv-issue-foreign-diplomacy-advisor-glance-tab-column-icons-overflow-horizontally-with-24-rival-players)  
[135 - (Fixed) Likely Base AdvCiv issue: turn-status text collided with the diplomacy screen](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#135---fixed-likely-base-advciv-issue-turn-status-text-collided-with-the-diplomacy-screen)  
[136 - (Open - likely Base AdvCiv lineage or maybe bad local installation/configuration, deprioritized) Choose-production popup does not re-fire when a city finishes production; city then sits idle for many turns](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#136---open---likely-base-advciv-lineage-or-maybe-bad-local-installationconfiguration-deprioritized-choose-production-popup-does-not-re-fire-when-a-city-finishes-production-city-then-sits-idle-for-many-turns)  
[137 - (Fixed) Beyond the Game mod issue: BTG Cross reused Huge grid size for every world size of Huge and below](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#137---fixed-beyond-the-game-mod-issue-btg-cross-reused-huge-grid-size-for-every-world-size-of-huge-and-below)  
[138 - (Fixed) Base AdvCiv issue: Global Highlands map sizes were too large](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#138---fixed-base-advciv-issue-global-highlands-map-sizes-were-too-large)  
[139 - (Fixed) Base AdvCiv issue: Foreign Advisor BUG menu made Glance attitude dropdown look attached to Enhanced Info Tab](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#139---fixed-base-advciv-issue-foreign-advisor-bug-menu-made-glance-attitude-dropdown-look-attached-to-enhanced-info-tab)  
[140 - (Fixed) Base AdvCiv issue: Foreign Advisor Glance tab showed incorrect and inconsistent +0 attitude display in self cells](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#140---fixed-base-advciv-issue-foreign-advisor-glance-tab-showed-incorrect-and-inconsistent-0-attitude-display-in-self-cells)  
[141 - (Fixed) Sevopedia media player 3D audio previews became very quiet after entering a game](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#141---fixed-sevopedia-media-player-3d-audio-previews-became-very-quiet-after-entering-a-game)  
[142 - (Fixed) Base AdvCiv issue: Military Advisor Map tab debug mode did not draw the full minimap section](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#142---fixed-base-advciv-issue-military-advisor-map-tab-debug-mode-did-not-draw-the-full-minimap-section)  
[143 - (Fixed) BUG configobj comment writer used undefined `_a_to_u` instead of correct `self._a_to_u`; old BUG syntax had prevented Ruff from seeing the bug](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#143---fixed-bug-configobj-comment-writer-used-undefined-_a_to_u-instead-of-correct-self_a_to_u-old-bug-syntax-had-prevented-ruff-from-seeing-the-bug)  
[144 - (Fixed) Base AdvCiv issue and AdvCiv-SAS settler free window follow-up: AI settlers sometimes do not move away from a high bad plot count start (e.g., high non-bonus tundra and plains): they now scout and hunt for better not very bad sites, and no longer stop at first good-enough site, but instead now rerun evaluate city site again on newly visible plots if a better site (e.g., more food/rivers/fresh water) exists nearby (which we now value more too for first city as well)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#144---fixed-base-advciv-issue-and-advciv-sas-settler-free-window-follow-up-ai-settlers-sometimes-do-not-move-away-from-a-high-bad-plot-count-start-eg-high-non-bonus-tundra-and-plains-they-now-scout-and-hunt-for-better-not-very-bad-sites-and-no-longer-stop-at-first-good-enough-site-but-instead-now-rerun-evaluate-city-site-again-on-newly-visible-plots-if-a-better-site-eg-more-foodriversfresh-water-exists-nearby-which-we-now-value-more-too-for-first-city-as-well)  
[145 - (Implemented / needs in-game test) Military Advisor Map tab lost selected leaders after tab switch or close/reopen](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#145---implemented--needs-in-game-test-military-advisor-map-tab-lost-selected-leaders-after-tab-switch-or-closereopen)  
[146 - (Fixed/Enhanced) Base AdvCiv issue of AI undervaluing coastal settling on naval-heavy maps](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#146---fixedenhanced-base-advciv-issue-of-ai-undervaluing-coastal-settling-on-naval-heavy-maps)  
[147 - (Fixed/Enhanced) Base AdvCiv issue of AI settlers not adding extra valuation to unowned bonuses in city-site scoring](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#147---fixedenhanced-base-advciv-issue-of-ai-settlers-not-adding-extra-valuation-to-unowned-bonuses-in-city-site-scoring)  
[148 - (Fixed) Base AdvCiv issue (and one AdvCiv-SAS issue) of duplicate parent XML keys found by new GitHub workflow check](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#148---fixed-base-advciv-issue-and-one-advciv-sas-issue-of-duplicate-parent-xml-keys-found-by-new-github-workflow-check)  
[149 - (Fixed) Base AdvCiv issue: Duplicate XML text tags found by new GitHub workflow check](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#149---fixed-base-advciv-issue-duplicate-xml-text-tags-found-by-new-github-workflow-check)  
[150 - (Fixed) Base AdvCiv issue (and some AdvCiv-SAS): Priority duplicate XML child/list entries found by new GitHub workflow check](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#150---fixed-base-advciv-issue-and-some-advciv-sas-priority-duplicate-xml-childlist-entries-found-by-new-github-workflow-check)  
[151 - (Fixed) Base AdvCiv issue: Suspicious malformed-looking XML angle tags found by new GitHub workflow check](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#151---fixed-base-advciv-issue-suspicious-malformed-looking-xml-angle-tags-found-by-new-github-workflow-check)  
[152 - (Fixed) Suspicious replacement question marks in lengthy Sevopedia XML found by new GitHub workflow check](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#152---fixed-suspicious-replacement-question-marks-in-lengthy-sevopedia-xml-found-by-new-github-workflow-check)  
[153 - (Fixed) RFC DOC bug: Sevopedia Hill page did not show improvements valid through underlying terrain, feature, or hill-eligible bonus rules](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#153---fixed-rfc-doc-bug-sevopedia-hill-page-did-not-show-improvements-valid-through-underlying-terrain-feature-or-hill-eligible-bonus-rules)  
[154 - (Fixed) Base AdvCiv issue: Great People could wait too long for Golden Age partners instead of using lower but useful actions](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#154---fixed-base-advciv-issue-great-people-could-wait-too-long-for-golden-age-partners-instead-of-using-lower-but-useful-actions)  
[155 - (Fixed) Base AdvCiv issue: remote captured-city attack stacks could park for many turns because upgrade waiting overrode a ready offensive target](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#155---fixed-base-advciv-issue-remote-captured-city-attack-stacks-could-park-for-many-turns-because-upgrade-waiting-overrode-a-ready-offensive-target)  
[156 - (Fixed) Base AdvCiv issue: ready city-attack stacks could park for future upgrades even when no unit could upgrade now](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#156---fixed-base-advciv-issue-ready-city-attack-stacks-could-park-for-future-upgrades-even-when-no-unit-could-upgrade-now)  
[157 - (Fixed/Diagnosed) Base AdvCiv bug: Minor AI Work Boat excess after previous spam fixes: compare need to the counted water areas, let sea workers resolve off-BFC sea bonuses, and confirm many repeated rebuilds were genuine net losses](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#157---fixeddiagnosed-base-advciv-bug-minor-ai-work-boat-excess-after-previous-spam-fixes-compare-need-to-the-counted-water-areas-let-sea-workers-resolve-off-bfc-sea-bonuses-and-confirm-many-repeated-rebuilds-were-genuine-net-losses)  
[158 - (Fixed) Base AdvCiv issue: ready no-target attack stacks could ignore pathable barbarian cities while only preparing a future war](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#158---fixed-base-advciv-issue-ready-no-target-attack-stacks-could-ignore-pathable-barbarian-cities-while-only-preparing-a-future-war)  
[159 - (Improved) AI civic-switch damping: paid-anarchy civic churn and direct reversals after the civic timer expired](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#159---improved-ai-civic-switch-damping-paid-anarchy-civic-churn-and-direct-reversals-after-the-civic-timer-expired)  
[160 - (Fixed) Likely inherited AI upgrade-budget issue: normal upgrades could overshoot the remaining budget and leave the AI almost broke](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#160---fixed-likely-inherited-ai-upgrade-budget-issue-normal-upgrades-could-overshoot-the-remaining-budget-and-leave-the-ai-almost-broke)  
[161 - (Tentatively Addressed and Hardened) Rare non-reproducible autoplay crashes related to `CvCity::cheat+0x15c3` sharing the city-name text lookup crash signature](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#161---tentatively-addressed-and-hardened-rare-non-reproducible-autoplay-crashes-related-to-cvcitycheat0x15c3-sharing-the-city-name-text-lookup-crash-signature)  
[161.2 - (Tentatively Addressed and Hardened) Rare non-reproducible autoplay city-name crash related to `CvCity::cheat+0x15c3` around city acquisition (Aachen city ownership transfer from Holy Rome to Mali) and uncovered during BBAI culture logging investigation](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#1612---tentatively-addressed-and-hardened-rare-non-reproducible-autoplay-city-name-crash-related-to-cvcitycheat0x15c3-around-city-acquisition-aachen-city-ownership-transfer-from-holy-rome-to-mali-and-uncovered-during-bbai-culture-logging-investigation)  
[162 - (Tentatively Addressed and Hardened) Rare non-reproducible autoplay crash variant in `CvCity::getProductionBarPercentages`](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#162---tentatively-addressed-and-hardened-rare-non-reproducible-autoplay-crash-variant-in-cvcitygetproductionbarpercentages)  
[163 - (Tentatively Addressed and Hardened) Rare non-reproducible autoplay crash variant related to `CvSelectionGroup::deleteUnitNode` and `CvSelectionGroup::clearUnits`](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#163---tentatively-addressed-and-hardened-rare-non-reproducible-autoplay-crash-variant-related-to-cvselectiongroupdeleteunitnode-and-cvselectiongroupclearunits)  
[164 - (Fixed) Base Civ4 Oasis map script had shadowed Python callbacks (found by the Python Ruff GitHub Actions Workflow)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#164---fixed-base-civ4-oasis-map-script-had-shadowed-python-callbacks-found-by-the-python-ruff-github-actions-workflow)  
[165 - (Fixed) Base AdvCiv bug: Dormant RectLayout `upperLeft` helper returned undefined `Point` instead of `PointLayout` (found by Python Ruff GitHub Actions Workflow)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#165---fixed-base-advciv-bug-dormant-rectlayout-upperleft-helper-returned-undefined-point-instead-of-pointlayout-found-by-python-ruff-github-actions-workflow)
[166 - (Fixed/Addressed) Base AdvCiv issue of trying to support reading mod (e.g., AdvCiv/AdvCiv-SAS) replay/Hall of Fame data in unmodded BTS, or unmodded BTS replay/Hall of Fame data in the mod (e.g., AdvCiv/AdvCiv-SAS): replays no longer try to use vanilla BtS-compatible replay storage after shifted XML enum order](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#166---fixedaddressed-base-advciv-issue-of-trying-to-support-reading-mod-eg-advcivadvciv-sas-replayhall-of-fame-data-in-unmodded-bts-or-unmodded-bts-replayhall-of-fame-data-in-the-mod-eg-advcivadvciv-sas-replays-no-longer-try-to-use-vanilla-bts-compatible-replay-storage-after-shifted-xml-enum-order)  

## 1 - Redundant attribute values for all AI Civs

While debugging the new ai personality feature in the Sevopedia in advciv-sas (our mod), we found some information that some ai attributes seem to be shared across all leaders:

```log
PY:[DEBUG] Cached AI attribute data for leader LEADER_ZARA_YAQOB
PY:[WARNING] Attribute 'iAtPeaceAttitudeChangeLimit' has an identical *raw* value (1) across all 53 leaders
PY:[WARNING] Attribute 'iAtPeaceAttitudeChangeLimit' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iAtPeaceAttitudeDivisor' has an identical *raw* value (60) across all 53 leaders
PY:[WARNING] Attribute 'iAtPeaceAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iAtWarAttitudeChangeLimit' has an identical *raw* value (5) across all 53 leaders
PY:[WARNING] Attribute 'iAtWarAttitudeChangeLimit' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iAtWarAttitudeDivisor' has an identical *raw* value (-5) across all 53 leaders
PY:[WARNING] Attribute 'iAtWarAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iAttackOddsChangeRand' has an identical *raw* value (8) across all 53 leaders
PY:[WARNING] Attribute 'iAttackOddsChangeRand' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iBonusTradeAttitudeChangeLimit' has an identical *raw* value (2) across all 53 leaders
PY:[WARNING] Attribute 'iBonusTradeAttitudeChangeLimit' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iBonusTradeAttitudeDivisor' has an identical *raw* value (50) across all 53 leaders
PY:[WARNING] Attribute 'iBonusTradeAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iDefensivePactAttitudeChangeLimit' has an identical *raw* value (2) across all 53 leaders
PY:[WARNING] Attribute 'iDefensivePactAttitudeChangeLimit' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iDefensivePactAttitudeDivisor' has an identical *raw* value (12) across all 53 leaders
PY:[WARNING] Attribute 'iDefensivePactAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iDifferentReligionAttitudeChange' has an identical *raw* value (-1) across all 53 leaders
PY:[WARNING] Attribute 'iDifferentReligionAttitudeChange' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iDifferentReligionAttitudeDivisor' has an identical *raw* value (-15) across all 53 leaders
PY:[WARNING] Attribute 'iDifferentReligionAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iFavoriteCivicAttitudeChange' has an identical *raw* value (1) across all 53 leaders
PY:[WARNING] Attribute 'iFavoriteCivicAttitudeChange' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iFavoriteCivicAttitudeDivisor' has an identical *raw* value (10) across all 53 leaders
PY:[WARNING] Attribute 'iFavoriteCivicAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iFreedomAppreciation' has an identical *raw* value (10) across all 53 leaders
PY:[WARNING] Attribute 'iFreedomAppreciation' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iLostWarAttitudeChange' has an identical *raw* value (-1) across all 53 leaders
PY:[WARNING] Attribute 'iLostWarAttitudeChange' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iLoveOfPeace' has an identical *raw* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iLoveOfPeace' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iOpenBordersAttitudeChangeLimit' has an identical *raw* value (2) across all 53 leaders
PY:[WARNING] Attribute 'iOpenBordersAttitudeChangeLimit' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iOpenBordersAttitudeDivisor' has an identical *raw* value (25) across all 53 leaders
PY:[WARNING] Attribute 'iOpenBordersAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iPeaceWeightRand' has an identical *raw* value (3) across all 53 leaders
PY:[WARNING] Attribute 'iPeaceWeightRand' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iSameReligionAttitudeChange' has an identical *raw* value (1) across all 53 leaders
PY:[WARNING] Attribute 'iSameReligionAttitudeChange' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iSameReligionAttitudeDivisor' has an identical *raw* value (10) across all 53 leaders
PY:[WARNING] Attribute 'iSameReligionAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iShareWarAttitudeChange' has an identical *raw* value (1) across all 53 leaders
PY:[WARNING] Attribute 'iShareWarAttitudeChange' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iShareWarAttitudeDivisor' has an identical *raw* value (8) across all 53 leaders
PY:[WARNING] Attribute 'iShareWarAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
```

Some of these such as iLoveOfPeace are not used in AdvCiv; i disabled (commented-out) from display (in SevoPediaLeader.py) such unused ai attributes to not clutter the display, see the main README.md's [UI (Main Sevopedia reworks)](/README.md#ui-main-sevopedia-reworks), and more specifically in the full AI Personality Panel Feature this [README_AI_Personality_Panel.md#note-about-some-ai-attributes-being-ignored](/_1_AdvCiv-SAS/Docs/README_AI_Personality_Panel.md#note-about-some-ai-attributes-being-ignored).

Leaving as is otherwise (except from hiding most or commenting out unused ones such as iLovePeace (in AdvCiv) anyways) for now if not always or not.

We may also spread some values more (i.e. in AdvCiv-SAS etc anyways) that are way too often shared between leaders, not just the common to all leaders, may be a good opportunity perhaps, but not sure or guarnateed, for now only mentioning the issue.

## 2 - (now fixed) Gandhi's base leaderheadinfo's xml had nowarattitudeprob pleased(110)/pleased(115) duplicated instead of (as i suspect it should be) pleased(110)/friendly(115)

For example, i had spotted a seemingly mistake/typo/bug in Gandhi's nowar attributes (from AdvCiv), where pleased was repeated twice, while enhancing and adding on the generate_leaders_data.py (see the related docs for details) script:

```json
            {
                "MemoryType": "MEMORY_VOTED_AGAINST_US",
                "iMemoryAttitudePercent": "0"
            }
        ],
        "NoWarAttitudeProbs": [
            {
                "AttitudeType": "ATTITUDE_FURIOUS",
                "iNoWarProb": "20"
            },
            {
                "AttitudeType": "ATTITUDE_ANNOYED",
                "iNoWarProb": "50"
            },
            {
                "AttitudeType": "ATTITUDE_CAUTIOUS",
                "iNoWarProb": "85"
            },
            {
                "AttitudeType": "ATTITUDE_PLEASED",
                "iNoWarProb": "110"
            },
            {
                "AttitudeType": "ATTITUDE_PLEASED",
                "iNoWarProb": "115"
            }
        ],
        "UnitAIWeightModifiers": "",
```

It is almost certainly a mistake and should be:

```json
            {
                "AttitudeType": "ATTITUDE_FRIENDLY",
                "iNoWarProb": "115"
            }
```

Our generate_leaders_data.py (see the related python docs for details) sucessfully detected/detects it, for example before fixing the XML of Gandhi we have:

```cmd
[WARNING] Duplicate NoWarAttitudeProb 'ATTITUDE_PLEASED' for leader LEADER_GANDHI
[SUCCESS] Leader data written to: leaders_data_20250426_100035.py
```

And after fixing Gandhi's XML we now have:

```cmd
C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS>cd C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\ & scan_xml_duplicates-3.3.py
[SUCCESS] Leader data written to: leaders_data_20250426_100152.py

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS>
```

So i had the idea to generalize this approach to find if we don't have other such duplicates and perhaps may improve our XML data and reliability, and the result is as explained in the related docs, currently if not always or not etc anyways version 3.3 as per chatgpt's naming and greta help in doing this (coded all i only gave pointers and feedback, joint collaboration hehe anyways.)

Since there are false positives, i am not sure how to interpret it, but hopefully useful enopugh, so adding this script here, and funcitonal enough (skim through results you known false for example maybe i mean, anyways)

Results are very good, if you have good eyes or are very patient or know where and what to look at or other things or not anyways, we successfully spot it specifically (Gandhi's seemingly('s?) mistake/typo/bug)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1WNHP4fQQ1Dbm4JnXx9YDedCnLzrOO8ey?usp=sharing)

## 3 - (now fixed with a DLL patch) Barbarians (cities) building wonders, in particular now fixed i.e. disabled for world wonders

In base advCiv code, after implementing the barbarians boost to make them more economically viable or strong... Barbarians are still trying to build wonders sometimes, the base AdvCiv code does not prevent that, or at least not always maybe or not or yes indeed; and even complete them sometimes actually, for example(s):

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1p5O09XzbbrM5x2hxFD6RGvBpuU8RzPAd?usp=sharing)

There may be(/have been,) other cases like these, and i don't know if the cause is one of the changes i made to barbarian (xml) code, or how it just is/was. I tried to fix it by using iWonderConstructRand -9999 on LEADER_BARBARIAN in leader head infos xml file, but they still build national and world wonders alike, and all the buildingclass NONE spaghetti code whether it is here (for national wonders) or not (for world wonders) does not change anything, they even build shrines like the mahadhobi as of now me writing this anyways, is not necessarily a bad design, but ideally i would want them to focus more on warmongering their key role in advciv-sas and be more efficient in that.

So/And i removed all such old logic of buildingclass NONE in (adjust if non-steam game or other mod path you have to where your advciv-sas or other mod you're using or not etc is) `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Civilizations\CIV4CivilizationInfos.xml`.

I had tried tweaking/changing WonderConstructRand but seemingly no change at all.

I had also tried using BuilUnitProb 100  or similar in leader barbarian XML, but although it seemed to have helped in most cases, in some cases barbarians would still build world wonders.

Lines such as:

```xml
				<Building>
					<BuildingClassType>BUILDINGCLASS_GREAT_WALL</BuildingClassType>
					<BuildingType>NONE</BuildingType>
				</Building>
```

Were totally ineffective, so i have removed them as well for as of now for wonders i mean.

Thanks to chatgpt's help, and following recent as of now DLL changes such as in [README_Known_Issues.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-bonuses-even-if-they-already-have-an-existing-improvement-very-inefficient-and-not-immersive](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-bonuses-even-if-they-already-have-an-existing-improvement-very-inefficient-and-not-immersive), it seems to finally be fixed by patching the DLL directly instead in [/CvGameCoreDLL/CvCityAI.cpp](/CvGameCoreDLL/CvCityAI.cpp) in `CvCityAI::AI_chooseBuilding`, as of now only for world wonders (no need to forbid national wonders too strongly as of now at least if not always or not or yes or etc)

## 4 - (now fixed) Sevopedia Unit's placeRequires's Religion button (for example any religious missionary unit) not redirecting to Sevopedia religion (nothing happens on click)

Now fixed: by replacing, in Sevopediaunit py file, in placeRequires function/method (of this file), `WidgetTypes.WIDGET_HELP_RELIGION` with `WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION`(,) as is done already by base advciv and successfully in Sevopedia building.

This is a bug i have noticed in AdvCiv and after checking, many other mods, among those (few i tried): ROM 291, RFC DOC, Neoteric World (since i have it too (to check their Sevopedia content or such or other or not anyways) even though i did not use anything from it at least but may be useful some day or not), History Rewritten too.

But clicking in AdvCiv in Sevopediabuilding for example on any religious temple's placeRequires's religious icon/button successfully redirects to the Sevopedia's religion page.

Among the mods i tried, only Realism Invictus's Sevopedia unit's placerequires's religion button works as intended and successfully redirects to the religion's page

I tried to import its code but their gc uses difference methods that we don't have it seems like getNumPrereqAndBonuses and such, may not be hard to fix or not, but leaving as is, finding how realism invictus does it, or finding yourself the cause if you want to investigate it, may help solve it.

As for me this is quite minor, and even though i would have loved (really) to fix it, leaving a note here rather as i don't know also how nested in the code the issue is, i would ideally but anyways love to dive deeper but doing other code things, at least for now if not always or maybe not, if so (that i would look again), hopefully these lines may (then) serve as a reminder of the issue and the current status of solving it (i have found in realism invictus mod it works fine unlike in other mods (that i tried about/for this issue), can investigate from there maybe)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1vRIFzwNijAjbmPBVUvSk90YjURXh-lG1?usp=sharing)

## 5 - (seemingly worked around now) player name same as windows (10's for example) username causes new game screen to be stuck unless a custom name is chosen, if/after/while DLL has been fastdep compiled

A quite weird issue i never had before, but after doing a fastdep (auto, not me), since i changed only one .cpp file to add the placeCivilizations new Sevopedia feature (see the [README_Sevopedia_Reworks.md (example 7: units category)](/_1_AdvCiv-SAS/Docs/README_Sevopedia_Reworks.md#example-7-units-category) for details)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/19T9I75vGCk58pFSR60y2Tmj69-NoFFtk?usp=sharing)

More context of how i implemented the change in the .cpp and such can be found in this Google Drive about Claude AI's first prompt i successfully implemented in AdvCiv-SAS, [/README.md#claude-web-chat](/README.md#claude-web-chat)

I don't know if fastdep compiel was the cause or just some weird corruption unnotified happened (i don't know a lot about these if at all hehe but it was reproducible, and my player name also unusually changed just after this fast compile so i can quite confidently say it is maybe indeed related(for example after checking indeed Civ4ScreenShot3010 in the advciv-sas's mod journey drive (see main README.md for link), with last compiled DLL before this Claude AI related .cpp change and recompile, had my windows username as default player name as can be seen in screenshot, but the screenshots of the issue in the drive linked above, that happen between Civ4ScreenShot3095(new game not yet started after the cpp changes and recompile) and Civ4ScreenShot3096 (where issue is solved)); in short if my long sentence still makes sense xd and i didnt get tangled into it if this is a word too, default civ4 player game suddenly changed from windows username to steam username (that i didnt want to show in screenshots too as is private to me, and this coincidated if this is a wordwith this screen being stuck issue))

To solve it, or at least after doing this issue that was reproducible is now solved, i deleted (adjust to where your mod path is) for example for me this is where the folder temp_files/Release/ is: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\Project\temp_files\Release\, this folder (i deleted it), and after recompiling cleanly, now i can play with windows username as usual, even though i had to change back the steam username to the name i wanted (first manually ingame at new game settings screen, then after seeing it works in CivilizationIV.ini (see [Windows_shortcuts](/_1_AdvCiv-SAS/Windows_shortcuts/))), here and for testing at least if not always or not or maybe not but for testing or not if i want or not or and other or and not or do or not or etc or etc, the windows username is fine with me ("PC" in the screenshots)

Not sure what the issue was, would have liked to be notified of the error/corruption cause of it somehow, but program runs fine as usual now, so maybe corrupted unnotified compilation, or fastdep issue perhaps (even though fastdep compiles seemed to work fine in the past as in just yesterday/the day before for the [unitai renaming (commit)](https://github.com/wonderingabout/AdvCiv-SAS/commit/701e2e31279d7ab152f91b431a81c1bae9c22734)as long as is solved is all good maybe even though bit weird but unsettling but whatever it is/was is maybe consistently solved now (not gauranteed, may or not be the case))

So hopefully fine and solved now even though not sure and not guaranteed but maybe is hopefully or maybe not, in all cases hopefully this info is helpful to me or and others or and not.

See also [README_Known_Issues.md#38---no-idea-why-but-sometimes-compile-mysteriouslystrangelyinconsistently-fails-and-recompiling-succeeds-underwith-but-exact-same-source-files-if-i-am-not-mistaken-but](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#38---no-idea-why-but-sometimes-compile-mysteriouslystrangelyinconsistently-fails-and-recompiling-succeeds-underwith-but-exact-same-source-files-if-i-am-not-mistaken-but)

## 6 - (now worked around) Too long XML code comments cause errors or game crashes

Related to [example/issue 9](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#9---art-and-maybe-other-assets-too-or-not-xml-assets-silently-causing-a-game-crash-during-initgame-loadstartup-instead-of-telling-us-which-asset-was-missing-no-error)

Be careful of having too long XML code comments, they (seem to indeed) cause game crashes (or maybe errors too?) in some circumstances, i assume it is especially due to or caused by if it's not samenested code comments more specifically, since i don't know more, it is only speculation on my end, but moving these nested code comments outside of the XML did fix the early game crash issue that is reproducible.

Something to keep in mind perhaps while doing XML code comments, that if they have to be long, move them outside of the XML tree entirely maybe, or at least outside the nested ones maybe, tweak this advice or opinion or feel or not feel or yes feel but maybe rather too view/thought as you see fit.

More details here too in: [Long_Comments/Long_Comments_XML.txt](/Long_Comments/Long_Comments_XML.txt) (search for `AudioDefines nested-comments crash notes`)

## 7 - Screenshots on multi screen display (if playing civ4 with "windowed" and not fullscreen as well) don't work if not taken in primary screen

On windows 10 at least if not in other systems as well, at least in my machine, since i play in windowed while debugging and such or other dev needs or not which is much more convenient, if i put the game window on my second (or any alternative/equivalent or not that may or not exist and that is not main screen) screen, then pressing the - Print Screen - key consistently does not create a new screenshot in (replace with your relevant user path) `C:\Users\PC\Documents\My Games\beyond the sword\ScreenShots\`, but putting the game window back to main screen, (then) the print screen key successfully creates a new screenshot (image) file, for example Civ4ScreenShot4272.JPG as of now.

## 8 - Do not edit python files while running the game, even modifying unused/unreached code may cause weird errors

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1gyaLERKrDAUbiQeVWl4S7T7tPJB0soR3?usp=sharing), or to copy the err log (path from Notepad++, adjust with your windows username or equivalent configuration/version of this that fits/suits your system username or other settings (C:\Users\PC\Documents\My Games\beyond the sword\Logs\PythonErr.log).

If such issues happen, maybe restart the game and hopefully all fixed, ideally modify python files before game is launched to prevent that, unless you know what or why you are doing (it) or other (reason) or and not as you prefer

## 9 - Art (and maybe other assets too or not) XML assets silently causing a game crash during init/game load/startup instead of telling us which asset was missing (no error)

Related to [example/issue 6](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#6---now-worked-around-too-long-xml-code-comments-cause-errors-orand-game-crashes)

For example, while i was renaming `_GEMS` to `_GEMSTONES`, everywhere (with VS Code global search), except one part i had forgotten:

Like this (Results/status shown below thanks to VS Code's global search's "Copy all" UI menu):

```log
C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Art\CIV4ArtDefines_Bonus.xml
  118,23: 			<Type>ART_DEF_BONUS_GEMS</Type>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Buildings\CIV4BuildingInfos.xml
  6512,22: 					<BonusType>BONUS_GEMSTONES</BonusType>
  6706,22: 					<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Events\CIV4EventTriggerInfos.xml
  11024,21: 				<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\GameInfo\CIV4CorporationInfo.xml
  236,21: 				<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Terrain\CIV4BonusInfos.xml
  1332,15: 			<Type>BONUS_GEMSTONES</Type>
  1333,30: 			<Description>TXT_KEY_BONUS_GEMSTONES</Description>
  1334,30: 			<Civilopedia>TXT_KEY_BONUS_GEMSTONES_PEDIA</Civilopedia>
  1336,31: 			<ArtDefineTag>ART_DEF_BONUS_GEMSTONES</ArtDefineTag>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Terrain\CIV4ImprovementInfos.xml
  482,22: 					<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\TrueStarts\CIV4TruBonusInfos.xml
  678,13: 			<Type>TRU_GEMSTONES</Type>
  679,20: 			<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv_ger.txt
  2549,14: a(S'HAS_BONUS_GEMSTONES'
  2706,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv_ita.txt
  2293,14: a(S'HAS_BONUS_GEMSTONES'
  2457,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv.txt
  2549,14: a(S'HAS_BONUS_GEMSTONES'
  2706,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\WS_CustomDomAdv.txt
  2407,14: a(S'HAS_BONUS_GEMSTONES'
  2572,10: a(S'BONUS_GEMSTONES'
```

Here as seen above, i had forgotten to rename `118,23: 			<Type>ART_DEF_BONUS_GEMS</Type>` to `118,23: 			<Type>ART_DEF_BONUS_GEMSTONES</Type>` as well, but instead of getting the usual error like in unitinfos xml or such from little or not little i experimented ith xml of civ4 in the past since doing this advciv-sas mod, here we have a silent crash instead of an error, and inspecting the err log or dbg log of pytohn in civ4 shows us nothing, file is empty, the app init log (in C:\Users\PC\Documents\My Games\beyond the sword\Logs\init.log) is not too helpful either:

```log
[38971.390] DBG: CIV Init
[38971.390] VERSION: App: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Civ4BeyondSword.exe
[38971.390] VERSION: Build: Thu May 29 04:28:49 2014
[38971.390] VERSION: 3.1.9.0 (128100)
[38971.718] VERSION: Mod Loaded: Mods\AdvCiv-SAS\
[38971.734] DBG: FILE Cat Init
[38972.234] DBG: Game Init
[38972.234] DBG: Multiplayer Init BEGIN
[38972.328] DBG: Multiplayer Init END
[38972.328] DBG: Audio Init
[38972.625] DBG: ArtFileMgr Init
[38972.625] DBG: Python Init
[38974.343] VERSION: CIV Version: 319
[38974.343] VERSION: Minimum Version: 319
[38974.343] VERSION: Save Version: 14223
[38974.343] DBG: Input Init
[38974.343] DBG: Engine Init
[38974.421] DBG: Checking available screen resolution
[38974.546] DBG: Validating screen resolution
[38974.546] DBG: Creating rendererer
[38974.797] DBG: Engine: renderer Initialized
[38974.797] DBG: Engine: Shaders Initialized
[38974.922] DBG: Engine: Scene Lights Initialized
[38974.922] DBG: Music Start
[38974.938] DBG: Font Init
```

But it seems last element we loaded successfully or (maybe?) crashed at while trying to load was "Font"s?? Could this be related to art assests or referring/being a reference/mention to(/of?) them perhaps or not?

In all cases, unless i am mistaken or not too knowledgeable about this issue or this part of civ4 knowledge or experience or and other or and not, this does not help us directly like as if for exmapel it told us error missing asset X at line etc asset not found or something.

So it seems art xml assets need special attention especially in the case of errors, not as easy to handle, but fixing it now works:

```log
C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Art\CIV4ArtDefines_Bonus.xml
  118,23: 			<Type>ART_DEF_BONUS_GEMSTONES</Type>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Buildings\CIV4BuildingInfos.xml
  6512,22: 					<BonusType>BONUS_GEMSTONES</BonusType>
  6706,22: 					<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Events\CIV4EventTriggerInfos.xml
  11024,21: 				<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\GameInfo\CIV4CorporationInfo.xml
  236,21: 				<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Terrain\CIV4BonusInfos.xml
  1332,15: 			<Type>BONUS_GEMSTONES</Type>
  1333,30: 			<Description>TXT_KEY_BONUS_GEMSTONES</Description>
  1334,30: 			<Civilopedia>TXT_KEY_BONUS_GEMSTONES_PEDIA</Civilopedia>
  1336,31: 			<ArtDefineTag>ART_DEF_BONUS_GEMSTONES</ArtDefineTag>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Terrain\CIV4ImprovementInfos.xml
  482,22: 					<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\TrueStarts\CIV4TruBonusInfos.xml
  678,13: 			<Type>TRU_GEMSTONES</Type>
  679,20: 			<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv_ger.txt
  2549,14: a(S'HAS_BONUS_GEMSTONES'
  2706,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv_ita.txt
  2293,14: a(S'HAS_BONUS_GEMSTONES'
  2457,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv.txt
  2549,14: a(S'HAS_BONUS_GEMSTONES'
  2706,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\WS_CustomDomAdv.txt
  2407,14: a(S'HAS_BONUS_GEMSTONES'
  2572,10: a(S'BONUS_GEMSTONES'
```

like this:   `118,23: 			<Type>ART_DEF_BONUS_GEMSTONES</Type>`, now works and game can start fine and all at least in main menu.

Something to keep in mind is we have a crash after modifying art assets, but no idea why, it could be linked to this issue or something similar, ideally we'd get a nice error crash message and such, but comitting in smaller chunks ideally and testing at each step occasionally or lot or not may help prevent or spot these.

Also for info init log after successfully load is like this after fixing it and successfully finally (even though was not long but as in/in terms of having success step now):

```log
[39838.765] DBG: CIV Init
[39838.781] VERSION: App: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Civ4BeyondSword.exe
[39838.781] VERSION: Build: Thu May 29 04:28:49 2014
[39838.781] VERSION: 3.1.9.0 (128100)
[39839.109] VERSION: Mod Loaded: Mods\AdvCiv-SAS\
[39839.109] DBG: FILE Cat Init
[39839.609] DBG: Game Init
[39839.625] DBG: Multiplayer Init BEGIN
[39839.734] DBG: Multiplayer Init END
[39839.765] DBG: Audio Init
[39840.078] DBG: ArtFileMgr Init
[39840.078] DBG: Python Init
[39841.812] VERSION: CIV Version: 319
[39841.812] VERSION: Minimum Version: 319
[39841.812] VERSION: Save Version: 14223
[39841.812] DBG: Input Init
[39841.812] DBG: Engine Init
[39841.890] DBG: Checking available screen resolution
[39842.015] DBG: Validating screen resolution
[39842.015] DBG: Creating rendererer
[39842.250] DBG: Engine: renderer Initialized
[39842.250] DBG: Engine: Shaders Initialized
[39842.375] DBG: Engine: Scene Lights Initialized
[39842.375] DBG: Music Start
[39842.391] DBG: Font Init
[39842.406] DBG: Begin MenuManager
[39842.406] DBG: Total Frame MS: 3681.0  FPS: 000  Min:000 Max:000 Avg:000  SampleFilter:10.000000
 Time   :   Ave  :  Min% :  Max% : Num : Profile Name
-----------------------------------------------------
--------------------------------------------------
```

## 10 - some text characters in XML TXT_KEY tags are not displayed correctly ingame (as `?` or causing other arti(e?)facts maybe too indeed for example), while some like `&` cause an XML error and asset failing to load entirely

Some characters are not displayed correctly and instead show as `?` or cause weird artifacts like being bold inconsistently or such. Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1LeTNL4kKHgQJdZ0mLNzHaOCKkenR9duh?usp=sharing).

They genererally are language specific chars, for example some chars in `Phāṇita` or `Bhāvaprakāśa` or  maybe too (test to be sure if this point/issue i am raising is accurate or not, should be but may not be valid/updated anymore if someone fixed it somehow or other or if i am mistaken or maybe not or yes or not or and other or and not). Or some other examples like `खण्ड` or such are likely to not display correctly or cause errors (check ingame or in docs or woemwhere where you can find such info or and other or and not as you prefer or and not or other or and not).

Some characters like the `&` seem to cause an XML error with a real error message and such, and asset failing to load entirely (revert to base civ4 one rather than our version of it), see screenshots for details in the drive link above for details.

And some characters like `–` seem to cause the text to be weird and inconsistently bold (see screenshot(s) for example if provided indeed)

The solution i use is to simplify these chars generally, for example rename `–` to `-`, or using `_` instead of `खण्ड` to signify it is a language char (some other approaches may work like romanizing, it is an example i went with most simple and accurate in my case/need), or rename for example `Phāṇita` to `Phanita`, or for example also `Dačice` to `Dacice` (again is an example do as you prefer or not or do or not or and other or and not)

Adjust this advice/feedback as you see fit.

## 11 - In Debug mode, in map view, unexplored tile by the active player if improved, shows as red for example "with Road" or "with Pasture", even though a road is already there and text should be white instead or removed entirely; and other weird debug mode display issue(s)

This is a small bug so just mentioning it, and perhaps it is even intended to be this way, but ideally in debug mode (ctrl+z and "chipotle"), an unexplored tile by the tile active player

As this is debug-only, and to not cause further issues, only mentioning it for now and not fixing it, screenshots about this issue, may be useful someday or not

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1lXQ8pyE0A6TJGqlnf4In3V7QuJ0lBhIR?usp=sharing)

Another weird display issue/bug in debug mode is for examples yields are not accurately accounted in some conditions, for example in screenshots 5465, 5466, 5467 of/in the drive link just above, sheep plains natural yield should be 1 food of plains + 1 food natural yield change of sheep so 2 food, but is displayed as 1 food only for this tile with map reveal (ctrl+z debug mode) vs 2 food accurately seemingly, without map reveal. I don't know what the exact issue is as i didn't investigate it, but still is an issue, just mentioning it here, may be helpful, hopefully exhaustive too as i wanted or not wanted or yes wanted or other or and not...

## 11.2 - In debug mode, another weird bug is at wonder list while world wonder has not been built in said civs at least not all

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1dtHQbjW9Z55O_KryENWcJsrlMhUVqyTH?usp=sharing)

Similarly to [known issue number 11](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#11---in-debug-mode-in-map-view-unexplored-tile-by-the-active-player-if-improved-shows-as-red-for-example-with-road-or-with-pasture-even-though-a-road-is-already-there-and-text-should-be-white-instead-or-removed-entirely-and-other-weird-debug-mode-display-issues), this seems to be a debug mode only bug, as when toggling off debug mode while still in same game (ctrl+z as of now if not always or not), a wonder is shown to have been built by many civs, with the date showing hammer icon instead of a data number year or such, and looking inside said cities, no world wonder exists, so this seems to be a visual bug specific to debug mode, i didn't check all cities, but a few said to have the world wonder didn't have it, and since it is supposed to be "unique" i.e. only 1 in entire world (not civ-specific as civ4 says about "unique" in another way) i forgot my sentencei assume this is not too important to fix, but mentioning it for exhaustiveness and in case it helps but or not but or yes but

## 12 - (now fixed) Special/generic building monastery's button inconsistently using (uses/was using rather) the hindu specific monastery button instead of a generic button like the (abstract? / generic) generic temple and generic cathedral were

Hopefully clearer and more consistent now or yes or etc

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1LyGR9fEuI6HZLtn-R5qxgdlVFPVmhUAc?usp=sharing)

## 13 - (now fixed/reworked) As an appendix to 12 - just before, shrines now also appear in tech tree at their religion's tech requirement unlike in base advciv / civ4 too

Added a PrereqTech for shrines so we can display them in tech tree as well, plus now shrines cannot be built without also having the religion's tech matching (for example during conquest or such), since shrines are not special buildings unlike temple, monastery, cathedral, maybe this is a fine even desirable way to handle it, was NONE.

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1kIRImlhvrB7-65lYNXm46M28FvWOT3f7?usp=sharing)

## 14 - (now removed/fixed if it is a fix) duplicate ArtRef Name="building:BUILDING_LIGHTHOUSE" and same for ArtRef Name="building:BUILDING_HARBOR" and ArtRef Name="building:BUILDING_CARTHAGE_COTHON" in CIV4CityLSystem.xml

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1vP6L16r3PJ0qpwzqOfeycuaTRDKZbNCr?usp=sharing)

in (adjust to your mod path) `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Buildings\CIV4CityLSystem.xml`

removed this:

```xml
		<ArtRef Name="building:BUILDING_LIGHTHOUSE">
			<Attribute Class="Era">ERA_ANCIENT,ERA_CLASSICAL,ERA_MEDIEVAL,ERA_RENAISSANCE</Attribute>
			<Attribute Class="Scalar">bNoWaterTest:1</Attribute>
			<!-- this bypasses water testing -->
			<Attribute Class="Scalar">szSpecialLayout:Water</Attribute>
			<Scale>1.5</Scale>
		</ArtRef>
```

in:

```xml
		<ArtRef Name="building:BUILDING_LIGHTHOUSE">
			<Attribute Class="Era">ERA_ANCIENT,ERA_CLASSICAL,ERA_MEDIEVAL,ERA_RENAISSANCE</Attribute>
			<Attribute Class="Scalar">bNoWaterTest:1</Attribute>
			<!-- this bypasses water testing -->
			<Attribute Class="Scalar">szSpecialLayout:Water</Attribute>
			<Scale>1.5</Scale>
		</ArtRef>
		<ArtRef Name="building:BUILDING_LIGHTHOUSE">
			<Attribute Class="Scalar">szNIF:Art/Structures/Buildings/Lighthouse/LighthouseModern.nif</Attribute>
			<Attribute Class="Era">ERA_INDUSTRIAL,ERA_MODERN,ERA_FUTURE</Attribute>
			<Attribute Class="Scalar">bNoWaterTest:1</Attribute>
			<!-- this bypasses water testing -->
			<Attribute Class="Scalar">szSpecialLayout:Water</Attribute>
			<Scale>1.5</Scale>
		</ArtRef>
```

seems like a duplicate, should be safe to remove, but marking it down here if i may say as i don't know a lot about these and to be safe, should be safe to do so though but is for exhaustiveness too perhaps...

also note as in code comment of it edited or not or yes or to fit quite well in this .md readme: "<!-- custom: remove seemingly duplicate `<ArtRef Name="building:BUILDING_LIGHTHOUSE">` (removed 1st occurence to be safe that it is not the one used in the game, the 2nd one seems more exhaustive too from the little i can see of it) -->

did similarly for the `<ArtRef Name="building:BUILDING_HARBOR">` and `<ArtRef Name="building:BUILDING_CARTHAGE_COTHON">` seemingly duplicated too

## 15 - (now fixed) Missing this technology "Cannot be traded" (bTrade) information in Sevopedia tech and tech advisor

Fixed missing this technology "Cannot be traded" information in Sevopedia tech "Special Abilities" (placeSpecial in py code) and in tech/technology advsior too, see also [UI (Ingame)](/README.md#ui-ingame) for details and [Modding_Ressources/README.md#example-of-dll-modification-of-cvgametextmgrcpp-and-other-related-files-to-add-the-new-this-technology-cannot-be-traded-flag-in-sevopedia-tech-s-placespecial-and-in-tech-tree-view-technology-advisor](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README.md#example-of-dll-modification-of-cvgametextmgrcpp-and-other-related-files-to-add-the-new-this-technology-cannot-be-traded-flag-in-sevopedia-tech-s-placespecial-and-in-tech-tree-view-technology-advisor) for a lot more details.

See also [example 1.6: techs category (Starting and Untradeable Techs Charts and other changes)](/_1_AdvCiv-SAS/Docs/README_Sevopedia_Reworks.md#example-16-techs-category-starting-and-untradeable-techs-charts-and-other-changes) for details or additional info.

## 16 - (now fixed) some info is missing in Sevopedia outside of/if not loaded from an ingame load for example "Can build research" not in Sevopedia main menu but in Sevopedia ingame (after map is loaded)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1LuVa_Y0XBIeC1VExD7KVrY8siEFYyE3n?usp=sharing)

Some info seem to be missing from Sevopedia loaded from main menu (screenshot 6680 for example in drive link above) vs same Sevopedia page loaded from ingame (screenshot 6681 similarly from there), for example at tech_writing, "Can Build Research" is missing from the tech_writing Sevopedia page at main menu, but not missing from the same tech_writing page ingame.

Not solving it and at least not now didn't investigate it, but good to mention it somewhere, since Sevopedia is meant mostly to be used ingame hopefully fine (enougheven though not ideal), but ideally would fix or investigate it too, but not guaranteed, may or may never/not do so.

## 17 - (now fixed) missing BBAI getters expose them to Sevopedia leader info in gc too for display

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1wFSJ6huis6w_xg-OmrZGE2Scw8PRhI7e?usp=sharing)

Similarly to fetching most fields of leader info now directly from XML and not strictly requiring leaders_data.py, at least in debug functions, we need/miss the (BBAI) victory weights in the Sevopedia leader gc's methods it seems (see [Sevopedia/Debug/](/Assets/Python/Contrib/Sevopedia/Debug/) for details, now added the new methods as part of this fix as shown below, see also drive link above in this example issue too)

To do that, and expanding on previous debugging now successful of flavors, nowarattitudeprobs, contact fields, and memory fields (note about all these fields see also [Sevopedia/_sevopedia_helpers.py](/Assets/Python/Contrib/Sevopedia/_sevopedia_helpers.py)), only BBAI victory weights remain so that we may fetch all directly from XML or at least be able to attempt to do so without requiring ideally leaders_data.py anymore, after asking chatgpt too, i noticed for example for `getMaxWarRand` (if we want to see where the BBAI is missing that getMaxWarRand is though for example to hopefully add it in this case) (with VS Code 's global search too i noticed it i mean if i may say indeed(see screenshots for details/examples)), modified the (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\CyInfoInterface3.cpp file to add such new getters, and also reusing existing getter names for such BBAI victory weights fields that are/were already existing in (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\CvInfo_Civilization.h, with chatgpt's help thanks.

Now the getters are added in Sevopedia leader, and we successfully see the real DLL modified values for the victory weights too, for example for leader gandhi as of now:

(from [Sevopedia/_sevopedia_helpers.py](/Assets/Python/Contrib/Sevopedia/_sevopedia_helpers.py) too example of output from ingame debug log)

```text
==== BBAI VICTORY WEIGHTS ====

Culture Victory Weight: 48
Space Victory Weight: 31
Conquest Victory Weight: -5
Domination Victory Weight: 0
Diplomacy Victory Weight: 79
```

Nice to have this data as well now, as is in our XML too, we may use it to remove the leaders_data.py dependency from our intial old code that depends on this external script due to no BBAI weights before in leader info in Sevopedia, and also because i didn't know at the time how to access contact fields, i hadn't thought to inspect gc and gc leader info ('s inner debugn link above in this example issue) as well perhaps for other uses maybe, for now we added the data at least.

Note: the value seem/are different from raw xml fields's values, this seems normal as well as the DLL alters/modifys the values in some conditions or something, may be better to replicate/display the real DLL specific/advciv(-sas in our case i.e. advciv-sas) ingame data as it is

## 17.5 - (now fixed) similarly missing base advcivspecific xml fields in gc of Sevopedia leader, now exposed there as well these new getCityRefuseAttitudeThreshold and getNativeCityRefuseAttitudeThreshold

Now exposed(/exposing?) these to python as well of gc 's Sevopedia leader as well, similarly to how BBAI victory wieghts are now exposed too/as well: getCityRefuseAttitudeThreshold and getNativeCityRefuseAttitudeThreshold

## 18 - Very inconsistent naming in some assets

For example _UTOPIA for `_COMMUNISM`, `_OBELISK` for monument sometimes and other times it means the actual `_OBELISK`, also for example `_CHINESE` being inconsistentlyunrelated to the chinese empire but instead in some cases to the default art asset of a unit for the asian civilizations in general, also using... `_GREAT_PALACE` instead of `_FORBIDDEN_PALACE` (as was hinted or rather i noticed from a base advciv code comment i am thankful for) i have renamed them as much as i found or could and wanted, actually a lot earlier in mod development than when i wrote this example issue, but solving them bit by bit as i see them and or want to ideally too but not guaranteed may or may not.., in all cases hopefully asset naming is a lot clearer or consistent at least for those i went through, probably did not do all as for remaining ones is wait and see....

## 19 - Unused or unclearly named art assets (e.g., _ASIAN/_CHINESE/_EURASIAN mixed up), and some are used while others are not

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1Ie5Uln9-vquy601oCUex3QIsgWCGnUXl?usp=sharing)

Quite related to [README_Known_Issues.md#14---now-removedfixed-if-it-is-a-fix-duplicate-artref-namebuildingbuilding_lighthouse-and-same-for-artref-namebuildingbuilding_harbor-and-artref-namebuildingbuilding_carthage_cothon-in-civ4citylsystemxml](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#14---now-removedfixed-if-it-is-a-fix-duplicate-artref-namebuildingbuilding_lighthouse-and-same-for-artref-namebuildingbuilding_harbor-and-artref-namebuildingbuilding_carthage_cothon-in-civ4citylsystemxml) and also while cleaning up in [README_Known_Issues.md#18---very-inconsistent-naming-in-some-assets](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#18---very-inconsistent-naming-in-some-assets)

The `ART_DEF_UNIT_ARCHER_EURASIAN` (see screenshots 6708, 6709, 6710, 6711 in drive linked in/at this example issue for what it looks like) seems to be unused in base advciv, in civ4 too, and in most mods it seems as well from a VS Code global search.

Note: the `ART_DEF_UNIT_ARCHER_CHINESE` (see screenshot 6705 similarly) now renamed to `ART_DEF_UNIT_ARCHER_ASIAN` for consistency is used though as the asian civilizations spearman art asset, so keeping it and removing instead the unused in base advciv and in our mod too `ART_DEF_UNIT_ARCHER_EURASIAN` as said before in previous sentence/paragraph ...

Also, if we want an art asset, we can import one another mod, but since we don't use the art asset and it seems to indeed be unused, remove it entirely, simpler and cleaner and more consistent with our code.

Update: sorted it out and restored the deleted `ART_DEF_UNIT_ARCHER_EURASIAN` (still unused as of now though). We rename assets e.g., from `ART_DEF_UNIT_ARCHER_ASIAN` to `ART_DEF_UNIT_LONGBOWMAN_ASIAN` when relevant (as of now still unused though), keep `ART_DEF_UNIT_SPEARMAN_CHINESE` when relevant and as an `ART_DEF_UNIT_SPEARMAN_ASIAN` variant exists already (renamed from `ART_DEF_UNIT_SPEARMAN_EURASIAN`), and rename `ART_DEF_UNIT_SWORDSMAN_CHINESE` to `ART_DEF_UNIT_SWORDSMAN_ASIAN` when relevant (no asian swordsman seems to exist, so make its name reflect that it is used for all asian units and looks asian enough and not specifically chinese enough).

## 20 - Negative and inconsistent DLL ajusted nowarattitudeprobs for some leaders, like leader_alexander that/who has nowarattitude prob furious of -2 lower than furious 0 and lower than cautious 14

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1zPIMTN97zhubyrHBzAVLjCb2-YAFmLqG?usp=sharing)

Some leaders like Alexander (III the great for example have a value for noWarAttitudeProb Furious of -2 DLL ajusted, which is lower than furious and doesnt seem to make sense.

Alexander's XML is like this:

```xml
			<NoWarAttitudeProbs>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_CAUTIOUS</AttitudeType>
					<iNoWarProb>20</iNoWarProb>
				</NoWarAttitudeProb>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_PLEASED</AttitudeType>
					<iNoWarProb>80</iNoWarProb>
				</NoWarAttitudeProb>
			</NoWarAttitudeProbs>
```

Since furious and annoyed are missing, they should fall back to defaults (i.e. LEADER_DEFAULTS 's value), which is as follows at least as of now:

```xml
			<NoWarAttitudeProbs>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_FURIOUS</AttitudeType>
					<iNoWarProb>0</iNoWarProb>
				</NoWarAttitudeProb>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_ANNOYED</AttitudeType>
					<iNoWarProb>0</iNoWarProb>
				</NoWarAttitudeProb>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_CAUTIOUS</AttitudeType>
					<iNoWarProb>0</iNoWarProb>
				</NoWarAttitudeProb>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_PLEASED</AttitudeType>
					<iNoWarProb>0</iNoWarProb>
				</NoWarAttitudeProb>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_FRIENDLY</AttitudeType>
					<iNoWarProb>100</iNoWarProb>
				</NoWarAttitudeProb>
			</NoWarAttitudeProbs>
```

Based on this, since furious and annoyed is an identical value in leader_defaults, why isn't it ideally both 0 (for furious and annoyed) in alexander for example, or alternatively both -2 (less ideal i think but i dont know, as attitude should floor at 0), but at least not inconsistently be lower at annoyed (here -2) than at furious (here 0).

Not sure i would fix it (i would have to dig how first) nor how it would influence game, but if want to look again at this issue it is here.

I don't know what the influence of the negative sign is, as otherwise 2 vs 0 should be quite minimal, but not sure is just my opinion/feel/thought which i don't know about much in this case, but the negative sign difference is more annoying, and ideally there would be a nice gradation.

## 21 - (Now fixed) missing "Cannot enter" terrain or feature info in map view of unit effects, unlike in Sevopedia (where it is also not clear enough about restrictions (cultural borders + not affected by roads, now added this info as well))

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1Felp-YagsHPYY3wtVqbV4eSRpwYl6BSb?usp=sharing).

Now solved. As part of adding terrain or feature restrictions to some units like chariot units and some siege units (catapults and trebuchets i.e. early siege units as of now only at least), i noticed the info is not displayed clearly in Sevopedia unit's place Special (it doesn't mention this effect applies only in cultural borders, and that for all tiles regardless of whether tile is roaded or not, has no impact on the effect (i.e. roaded or unroaded in cultural borders is walkable but unroaded or roaded outside of cultural borders is not walkable regardless of road status, and unlike in some games like civ3 where adding a road fixed or unlocked the limitation))

For the Sevopedia unit part, it was modifying the XML as usual if i may say.

But for the ingame part, it is first time i modify successfully (and even tried actually) the unit effects bullet points, now to also display this info, even though it is on a shorter display, we successfully loop through these terrain(s) or feature(s) and display them as such (only tested for features, but i assume would work-function similarly for terrains for example for workboat's ocean terrain restriction)

It was thanks to chatgpt's help as well and my prompts and digging too, even though it struggled at times if i may say and annoyed me bit i mean, i was quite used or expected it if i may say and together we solved it(may have been harder if i was not prepared for suchmost likely)

First to solve this i followed the trail of the txt key in Sevopedia unit, then found it is only once and not twice, and missing in map view. So i tracked instead a txt key already in the map view unit effects bullet points, and i found the scout's (that we added quite recently or not recently but as part of advciv-sas's changes being able to walk on land impassable (peak only as of now) terrain (and explorers too i assume in this assumption too or memory from reading or something that it applies or would apply to explore units in general land onesin advciv-sas)), and there i added the method.

But we needed also to modify not only [CvGameTextMgr.cpp](/CvGameCoreDLL/CvGameTextMgr.cpp) but also C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\CvUnit.h too as advised by/with chatgpt.

And after a bit of back and forth, we were now first finally able to display the text only, a shorter version of it.

Then i wanted to add terrain/feature list information, but tweaking the code based on other samples caused errors at first, so after more samples i mean after i sent more samples to it it provided me with a working code that i cleanly compiled (no fastdep as it may cause errors see this doc ctrl+f "fastdep" or similar or "compile" for details)

Since we had the list but buggy, chatgpt was right in its guess that we only needed to tweak the logic, now works and functional, also more informative.

See screenshots linked in this drive for details as well, thanks thanks.

## 21.5 - (Addressed / fixed) - Removed the giant configobj docstring very inefficiently in the python code, and commented out most if not all as well

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1oOiKggm9nHVyp07QF8HM_WgXY5Gtcg44?usp=sharing) and [google drive folder link 2](https://drive.google.com/drive/folders/1fWa7xXOgnXW2w2_b6JHGcDaoSqhGHree?usp=sharing).

Commented-out most python docstrings, instead with a `#`, as for very long ones, they are moved to specific files instead, for example as of now the changelog giant (500+ line approximately from my memory) in configobj.py has been moved to [/Long_Comments/Long_Comments_py.txt](/Long_Comments/Long_Comments_py.txt).

Exceptions are for example test docstrings as comenting them out causes ingame errors for example in configobj py file, and empty if commented out which causes ingame error with VS Code unexpected indent at the next function (i.e. if i comment-out this function that has only a docstirng, everything else being a comment out or empty, then the function below it has unexpected indent error, which causes ingame errors as well, such as in eventsigns py file for example), and maybe some ambiguous other cases if i have forgotten them or maybe not, hopefully this increases even if a bit if not lot loading times and reduces memory usage from what i understand chatgpt's explanation, and as according to/advised by chatgpt, they are not used ingame, and from my quick autoplay test(s) game seems to run fine without it. Added info if helps here.

Similar to python comment trimming to one line, but this time not for performance as it seems one giant comment line vs a 10 line comment has exact same performance in xml parsing from what i understood of chatgpt's explanation (due to parser still reading the entire comment line regardless, not skipping like in python seenig a `#` for example), but doing so as it helps for word wrapping, but since performance seems to be the same based on my understanding of and on too chatgpt's explanation, less incentive to do so and optimize it, even though i am still quite motivated maybe i think to be fair, but less or no benefit or less to do so. Not in known issues as well similarly to python comment cleanup issue.

Note: in case i was too aggressive with these and somehow caused bugs, we may revert to old python code and then only move the config obj docstring to common docs rather, but ideally i'd like to keep all as i belive code is bit cleaner. I did try to reread multiple times and hopefully didn't make a mistake, but in case we did, may revert if needed to old python code and tweak more consevatively from there if needed, see next issue as of now 21.6 for details.

## 21.6 - (Addressed) Old python code not being optimized, with many ruff linter (that we added) VS Code errors that don't allow to read the files

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/19qLLdFNSuJXdoeS8-laSDQT81iigAG3q)

Using ruff linter (vs code extension) and chatgpt to fix or sanitize a lot of ruff warnings or errors in our/the python code (see notes at some useful tools in readme as well about rust for details and also see google drive link there for examples, as well as additional info from (what is written) here maybe too), while minding to be python 2.4 comaptible for civ4 this is the version civ4 uses.

Examples include fixing suboptimal multiple statements per line, but also needless semicolons at end of line, bare except instead of catching with Exception or similarfrom what i understand of chatgpt's explanation and rephrasing it while understanding it in my own way too from my past knowlege too, inconsistent use of tabs and indentations, and many others even though some/most seem to be detected by pylance it helps that ruff flags them all too and some not detected by pylance it seems as well thanks

Also a lot of cleaning up of poor code formatting that i annoted if i may say as much as possible but i may not have done all purposely or not i mean hopefully quite accurate i mean most importantly exhaustive, also tried to remove needless imports like `import string` when deemed possible by rewriting code a bit with ruff or pylance's warnings/errors as well as chatgpt's help and my prompts too, as well also as real fixes like mismatch in placeholder count in string format

Note: in case i was too aggressive with these and somehow caused bugs, we may revert to old python code and then only move the config obj docstring to common docs rather, but ideally i'd like to keep all as i belive code is bit cleaner. I did try to reread multiple times and hopefully didn't make a mistake, but in case we did, may revert if needed to old python code and tweak more consevatively from there if needed, as said in issue as of now 21.5 as well.

Note 2: example case of where i was too aggressive and caused a bug by remoing an unused variable shown [here in this commit](https://github.com/wonderingabout/AdvCiv-SAS/commit/56ea046e0da6e55652841d4cc3181b92e294323c#diff-354807997b1a5f7626ae7eee99c7f4841125b08e0dd67675269502697cc9fdc6L145-R147), so although a variable itself is unused doesn't mean the call was. Preserving the call while removing the old unused variable was the/a correct way to fix the ruff warning instead of simply removing the line, which was my mistake but perhaps a good example of cases where some extra caution is needed

Note 3: reverted some of them to be safe and as not necessary to fix all of them (e.g. bare except rule added to exceptions in [/ruff.toml](/ruff.toml)).

## 22 - (Now fixed) Obsolete bonuses (such as BONUS_ELEPHANTS) in tech advisor (i.e. tech tree view) failing to redirect to Sevopedia bonus with id none causing an error, unlike obsolete buildings (like BUILDING_SPIRAL_MINARET for example) successfully showing the building item's page

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/127ReqMyucJZ2gH88ARhgTWwuh6jl4oCs?usp=sharing)

An issue i have noticed during the buildings modifiers rework/rebalancing for wonders mostly, still unfinished as of now, but the issue i have noticed is that obsolete bonuses in tech tree view (tech advisor it is called it seems in civ4) have an error when clicking on them at the Sevopedia bonus redirect (see screenshots for example of error), but clicking on obsolete buildings in tech tree view does not cause an error at all and successfully redirects to selected/clicked on building from tech tree view, now in the Sevopedia building page.

After asking chatgpt and claude ai, i have done some quite extensive debugging, and have found the issue is we don't pass the correct iItem in pediaJump (in Sevopedia main) for obsolete bonuses, but obsolete buildings have the correct iItem.

This would mean the issue is before, at the pedia jump caller's level if not before.

I have also noticed we have the real id in CvTechChooser.py (see screenshots with the debug lines in code comments for example 25 for (obsolete selected) BONUS_ELEPHANTS), but i don't know how to solve it further, and claude ai and chatgpt seemingly can't find the issue or fix easily as well with these code samples it seems, even though they helped me lot or quite a bit and i didn't show it in screenshots as bit tedious.

Still, adding a fallback iItem (for example of 1) if iItem is -1 seems to workaround it, we get to wrong bonus (like BONUS_COAL in this example) but at least no error anymore, also it doesn't seem to break anything, nor to break obsolete buildings in particular that seem to still function as intended or as they did before, so although/while it remains yet to solve the obsolete bonus issue, it is perhaps more playable now.

Update: now fixed: the issue/bug/error was seemingly caused by a new base advciv code in CvDLLWidgetData.cpp, now reverted to using `iData1` same as obsolete buildings did (and which didn't have the issue again) and not `widgetDataStruct.m_iData2` at the line after line `case WIDGET_HELP_OBSOLETE_BONUS:`, which fixed it now, see also screenshots for details in the google drive. So removed previous workaround of using a fallback as well as debug lines as they are not needed anymore now that issue is identified and solved.

Update 2: although we fixed the obsolete bonus button in tech advisor, i noticed much later that now the non-obsolete bonus buttons (e.g. cattle or camel bonuses at tech_animal_husbandry) trigger the same error now, which they didn't before, so i partially reverted this fix, so that it still applies to `case WIDGET_HELP_OBSOLETE_BONUS:` as we want to fix the issue, but not anymore to `case WIDGET_HELP_BONUS_REVEAL:` which now doesn't use same code anymore as the former, but instead the old base advciv's code if i'm not mistaken, which seemingly nicely fixes this issue as well.

## 22.5 - (Addressed) Seemingly fixed weird flavors or XML fields: Mistakes?

Fixed some seemingly mistaken flavors in forbidden palace (asset renamed in advciv-sas to forbidden_palace) in base advciv: military 5??? Or am i mistaken somehow, or is it as i expect a mistake or not too sensical flavor? In all cases, it is now as of now i meanchanged in advciv-sas to growth and gold based flavors among others or not, see xml for updated values or details.

Fixed the stealth bomber and other units having a lower collateral damage limit than its base collateral damage (`<iCollateralDamage>100</iCollateralDamage>` vs `<iCollateralDamageLimit>50</iCollateralDamageLimit>`), which i don't know a lot about but seems like a mistake or inconsistent with most units (why put a higher than the limit damage, again i could be mistaken about how this works-functions, but we (i.e. mexd...) also wanted to add more collateral damage support so now all units have some (swordsmen could throw shurikens) collateral damage limit, even though collateral damage itself starts at 0 for most units still; such info is now displayed in Sevopedia unit chart (as of now named "Combat" category, as well as in each unit's Sevopedia unit placeSpecial (as of now named "Special Abilities" panel)), and also ingame in map view when hovering over the unit, in its effects panel (we also now show more reliably the extra collateral damage info there as well, see Sevopedia ingame or xml for details or updated values); hopefully or not or yes or etc i am not mistaken in doing so or it is helpful or not or yes or etc)

## 22.6 - (Addressed) XML tweaks and fixes

Also fixed/replaced the strange the strange `[PARAGRAPH:2:1]` with the much more commonly used `[PARAGRAPH:2]` in our advciv-sas assets, i don't know what this strange format/thing is, but if the base `:2` can do it no need for a `:2:1`, and strange trailing `[PARAGRAPH:2]</English>` and or such as well that also seem uneeded, and remove unneeded `[PARAGRAPH:1]` in some tech quotes (as of now didn't do it to all tech quotes as bit tedious and not so worth but ideally would but may or may not in this case)

## 23 - (Seemingly now fixed) Major bug of AI cities being stuck in a loop of producing a workboat and instantly scrapping it (so without producing a new unit if i'm not mistaken) then producing a new one endlessly for dozen turns until it somehow solved itself but way too late

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1VGGAJZuCwwSdp86PWd-bFFprW7AOdtCK?usp=sharing)

Update 2: see below for the fix.

While testing an autoplay before comitting latest changes, i have noticed a barbarian city in a lone island gets stuck producing a 1 hammer barbarian workboat. I have given save files at turn 0, 50, and 100 if one wants to try to reproduce it.

It seems that the issue was resolved after say 30 turns, but then after a unit or such the barbarian city tried to produce another barbarian workboat and got stuck again for a dozen if not more turns until and including when autoplay ended.

This is not efficient nor ideal, i don't know what the cause is, if it's because the barbarian city is on a lone island, or if it is because the 1 hammer cost of the barbarian workboat somehow creates a bug with overflow, or if the issue is something else, but so far AI performs well both barbarians and AI players and i would like to keep improving their efficiency ideally as long as i develop this advciv-sas mod at least if not playing it too or such.

Added the files, screenshots and save files there, in case it helps and to revisit them later if needed.

In another autoplay after this one (save file not appended here i.e. not in the drive link of this issue number if i may say) the issue seems to have happened again in a barbarian city, but lasted luch shorter, only a few turns, so maybe the issue is not critical if resolves by itself still is reproducible in this case, ideally would be solved, added data if helps. It is also possible that these are rare instances, as it seems to have happened so far only on costal/naval cities so far from little autoplay i paid attention to focusing/noticing this problem/issue, so may not be critical again i mean or may be, but ideally would be nice if solved, but i don't know how to so so i hope this data helps, leaving as is for now.

update: having tried again later this save file 173 turn number 50, the issue is consistently reproducible, and i have increased the hammer cost to higher values like 5 and 20 to see if it was the issue but the issue persists exactly almost the same, just instead of being stuck on always 1 turn until production for many turns, it is now apparent the issue is rather with looping, as say for a 20 hammer worker the countdown reduces fine at each turn at the hammer cost is getting completed, but issue is that often no new unit is produced at end of the cycle when hammer cost is completed, instead it seems like a new loop starts over at 0 hammer.

I have also found issue is not whales or some other water bonus as another east barbarian city in same save file has no problem having upgraded bonuses in these cities, but the difference is this city has a harbor (reworked in xml in advciv-sas, not like the base advciv's harbord, it is now in our mod the first water building) unlike the city with the bug. But after making the change of now workboats requiring a harbor (see xml for details and reasoning why) (and a barbarian_harbor specifically for barbarian player's barbarian_workboat), the issue remains the same, so issue is not that the eastern barbarian city that could improve the water bonsues successfully had a harbor either unlike western barbarian city with the bug. So i do not know exactly what is happening, eastern city is also on a lone island but this doesn't seem to be the cause as it successfully improves its water bonuses unlike western city, but i have noticed eastern city is also stuck producing workboats as well. In the end, i still don't know the cause nor how to fix it, but this helped balance the workboats that may be op in some early starts with a lot of land food plus water food. I have added screenshots of these new results if i may say.

Update 2: i have found the issue and seemingly fixed it now. The workboat is now successfully produced in one turn. It seemingly was in `CvUnitAI::AI_workerSeaMove`, commented-out the scrapping code that applied only to AI sea workers and which also matched what i found ingame as well (never had the issue in base advciv as a human player i mean, so i assume it only affected AI players).

I found it with a global search on `UNITAI_SEA_WORKER` and some digging, with chatgpt 5's help and suggestions and my own ideas too.

But i noticed that it applied not just to barbarians, but to other AI players as well. And in many cities. In particular, moscow didn't grow at all and kept producing a workboat or attempting to (then scrapping it when produced) for like 50 turns, and 2 nearby coastal cities as well, so it was really a critical and crippling bug.

See existing screenshots between 1981 and 1990 for example of the issue in moscow city, and existing screenshots between 2014 and 2032 for it in other cities, it was even more widespread than i thought, hopefully fixed now by commenting out the scrapping at produced code as mentioned before in update 2 above .

Next issue now is that AIs produce a bit too many workboats, for example there are now 3 extra workboats to improve only 2 ocean water bonuses that we don't have access to until much later (as of now tech_astronomy), so these are produced for no reason, with one extra even when tech prereq is met, and just producing them then scrapping them if extra is very inefficient and a waste of hammer as well as time to plan invasions or build anything early like a settler, worker, building, anything.

I assume this is what old code attempted to solve but very inefficient, or maybe it had some other purpose +/- as well or not maybe. Ideally we'd want to count in advance the amount of workboats we need based on water bonsues in cultural borders (to get health even if out of city radius), and produce exactly only the number of workboats to access currently accessible (e.g. coast only) unimproved bonuses, so no need to scrap them later, which i'll attempt to do later in another known issue, but this is still tremendously better than being stuck in a loop for dozen turns and seemingly for many AI cities, which is very crippling, so hopefully a lot better now.

See also although not directly related but anwyays etc: [52 - (Beyond Tremendously improved) Remove AI scrapping of military land units, as way too many units are scrapped early, yet we really need them to defend against barbarians or our rivals or such](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#52---beyond-tremendously-improved-remove-ai-scrapping-of-military-land-units-as-way-too-many-units-are-scrapped-early-yet-we-really-need-them-to-defend-against-barbarians-or-our-rivals-or-such).

## 23.2 - (Attemptingly partially addressed/reduced) AI players producing more workboats than needed which then stay parked in city or go explore

Not a critical issue as it is in fact less than i thought in known issue as of now [23 - (Seemingly now fixed) Major bug of AI cities being stuck in a loop of producing a workboat and instantly scrapping it](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#23---seemingly-now-fixed-major-bug-of-ai-cities-being-stuck-in-a-loop-of-producing-a-workboat-and-instantly-scrapping-it-so-without-producing-a-new-unit-if-im-not-mistaken-then-producing-a-new-one-endlessly-for-dozen-turns-until-it-somehow-solved-itself-but-way-too-late) above in this doc, but i tried to reduce the AI producing a bit too much workboats, mostly by doing changes as advised by chatgpt and claude ai (and approved by gemini ai too) if they are not all and myself mistaken but could be the case but check to be sure, in `CvCityAI::AI_neededSeaWorkers`, changing look ahead from 5 to 0 (check explanation there as it has the AI(s) explaining it better than i would n this case). It seems some cities still have an extra workboat, but some cities don't, not sure the change made a different, but since it seems harmless, and AIs agree at least those i askedit should be so, left as such, but check to be sure.

Note: change was originally done in an attempt to solve a bug i had created while disabling functionally getimprovementvalue, info about it in this doc or in the code comment at function mentioned in this known issue as of now 23.2 too but check to be sure, and since the bug is now fixed, i kept this change since is conservative, obvious, and seemingly harmless but check to be sure.

## 24 - (Attemptingly fixed) AI Workers often build forts on bonuses, even if they already have an existing improvement (very inefficient and not immersive)

Note 2: this specific one should not be relevant anymore as we have overhauled AI worker builds entirely, but just in case and to be exhaustive too.

Note: as of now the changes in the DLL described below in this section can be found in this [advciv-sas commit](https://github.com/wonderingabout/AdvCiv-SAS/commit/6d82d51fe1e3a3262d7c69af67daaacb927175e4) among a few other unrelated changes but or not but or yes buthopefuly helpful or not or yes or etc

This is an issue i had more extensively documented in the known issues about advciv civfanatics thread (see link somewhere in [README.md#me-wonderingabout](/README.md#me-wonderingabout)), that AIs often build forts on top of existing improvements.

This should be very inefficient in most cases as forts,... :

- take a long time to build (waste of worker time)
- yield less than improvements
- it is unlikely a human or other player would ideally attack units garrisoned there as it is not advantageous to do so
- it is especially inefficient where/when an improvement is already built that connects the ressource/bonus yet the AI undoes that extremely inefficiently for lower yields and other such disadvantages discussed before or not
- it is also cheaper / more efficient i think at least if i may say in this case at leastto let the ennemy destroy/pillage an improvement and rebuild it later than to carry fort very low yields on each improved ressource/bonus all the game

There are some other disadvantages such as:

- not immersive to see the AI play so inefficiently, at least to me

However it could potentially be useful in some cases:

- allow naval units to pass/cross this land tile even if a ressource is on it
- prebuild the connection to a ressource/bonus, but generally the improvement would be available at same time if not before the ressource/bonus becomes visible, unless talking a blind preconnection attempt but way too inefficient
- possibly some other +/- more minor advantages

Overall i feel/think it would be better for the AI to not bother with forts at all, so i tried/am trying to add more restrictions or and cases where the AI would simply, to simplify the logic, skip entirely forts, which should in most cases help the AI.

So although i don't know too much how to do this, but can manage a bit maybe, i made such changes in the DLL with chatgpt's help, as of now untested (see the [README_Main_Changes_Guide.md](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md) for updated status if any there or and cpp files)

## 25 - (Seemingly fixed) AIs settling too much and too often on bonuses, especially food bonuses (!!!) and metals and other high production bonuses or also commerce bonuses to a lesser extent

Done by moving the code in `foundOnResourceValue` in CitySiteEvaluator.cpp to the parent caller `AIFoundValue::evaluate()`, and added more and new checks there.

### Origin and description of the problem

This is also one of the issues i had noticed in base advciv and that still happens in advciv-sas as of now, so trying to fix it. I had asked about it in the past f1rpo who kindly made/added/pushedthis [base advciv commit](https://github.com/f1rpo/AdvCiv/commit/1a372d417a6001e2afe2b40e69824b45fa375907) as a partial patch/fix to it

But while it seemingly may have improved it a bit, AI still settles on metals, and although that may be fine, perhaps even desirable in some cases maybe (metal on hills in particular maybe), AI still often plant their cities on food bonuses which is very very inefficient. As i don't know too much about these but am very eager to improve these ideally... I asked chatgpt and trying to fix/tweak quite cautiously this logic, quite similarly than in [README_Known_Issues.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-bonuses-even-if-they-already-have-an-existing-improvement-very-inefficient-and-not-immersive](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-bonuses-even-if-they-already-have-an-existing-improvement-very-inefficient-and-not-immersive)

### General rules for settling on (i.e. home plot) bonuses

Explanation and data shown thanks to chatgpt 5, who also helped me and gave me feedback on these, check if accurate or updated in `AIFoundValue::evaluate()` in as of no CitySiteEvaluator.cpp for details.

"When evaluating a home plot containing a resource (bonus), the AI applies penalties to avoid settling directly on it — except in rare cases where the tile is low-food or the improved yield is not too high.
This preserves the bonus for later improvement, unless local conditions strongly favor settling there."

| Bonus Type (by natural yield) | Terrain Conditions | Hills? | Improvement Yield Scaling | Value Adjustment | Reasoning |
| --- | --- | --- | --- | --- | --- |
| **Food Bonus** (`aiNatureYield[FOOD] ≥ 1`) | Any | Any | N/A | **−400** | Strong avoidance: food bonuses are highly valuable improved; settling wastes them. |
| **Production Bonus** (`aiNatureYield[PRODUCTION] ≥ 1`) | Snow / Desert | Any | +25 per hammer from improvement | **Base −200**<br>−**Reduced by 200** for low-food terrain | Low-food terrain makes settling more acceptable; high improved yield increases penalty. |
| Production Bonus | Any other terrain | No special reduction | +25 per hammer from improvement | **−200** + scaling | Keeps strong production bonuses for improvement; slight openness if low-yield. |
| **Commerce Bonus** (`aiNatureYield[COMMERCE] ≥ 1`) | Any | Any | N/A | **−100** | Preserves commerce potential from improved resource. |

### About water bonuses/ressources in range but ignored by AI settling instead a non-coastal location

Attempt to fix/address this as well by making the penalty in that case much stronger, as of now increased from -165 to -400 (seems to have been -800 in k-mod, see [/CvGameCoreDLL/CitySiteEvaluator.cpp](/CvGameCoreDLL/CitySiteEvaluator.cpp) for details or updated value), hopefully helps the AI consider more often water ressources or at least not ignore them when they are in range of their city sites considerations if i may say in this case at least maybe

### Results

I only tested it a bit (a few autoplay glances at turn 100), but the results seem extremely good and really much better, may test more to be sure or ask player feedback after mod release or and such if we do release it as planned/intended in this case but anwyays etc, so i would say to take this with a bit of caution maybe, but overall it does seems AIs almost always if not always maximize planting/settling their cities around found bonuses in the radius and not planting on them, cannot tell too much or if this is just small sample but it does seem to make a big difference.

Update: since latest refactor, although i didn't retest it yet, i'd expect results to be even better now with the fine tuning we added based on terrain (e.g. hill plains good to settle on for production bonuses for example, but less the more they yield then improve them rather), test it to be sure but should be extremely good, but since i didn't recheck it, test it to be sure.

## 26 - (Attemptingly fixed/addressed) tell AI settlers which (non-home and non-bonus tiles) terrains and features environments are best to settle near (for example good if a lot of grass or flood plains in city radius, bad if desert or plains in city radius). As for local tile to settle on (bHome) optimization as well: hate to settle on hill grass or flood plains, love to settle on hill plains or tundra or desert; overridden only if locally plot is otherwise really good (e.g. allows to have 2 bonuses or such so ideal spot but we have to settle on flood plains for it for example or some other good tile)

For non-bonus tiles, also added code that tells the AI which tiles are best to have in our environment, and a different logic for the home plot to settle on, with chatgpt 5 and other ai or models 's help as well if i'm not mistaken. Also adjusted and with different values (see below for details).

Done similarly to [README_Known_Issues.md#25---seemingly-fixed-ais-settling-too-much-and-too-often-on-bonuses-especially-food-bonuses--and-metals-and-other-high-production-bonuses-or-also-commerce-bonuses-to-a-lesser-extent](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#25---seemingly-fixed-ais-settling-too-much-and-too-often-on-bonuses-especially-food-bonuses--and-metals-and-other-high-production-bonuses-or-also-commerce-bonuses-to-a-lesser-extent).

Done by modifying in `AIFoundValue::evaluate()` in as of now CitySiteEvaluator.cpp, see there for details, or the documentation below if still accurate or updated.

### Choose best environment to settle near (e.g. a lot of flood plains, a lot of grass, not a lot of desert or plains, etc.)

This section is about the improvements we made in our mod to tell the AI, when it wants to plant/found/settle its city, where is it good to plant our city and make it lecherous to do so xd, and where is it bad and better avoid.

For example, if there is a lot of flood plains, many nice grass flatland, perhaps 1-2 hill grassland, this is about ideal when it comes to terrain and feature choice in city radius (not talking about bonuses or many other settings here, only among terrain and feature, for non-bonus tiles, which are good to have, and which are not, to help the AI ponder and choose a nice city spot to plant/found/settle its city on (and not a bad spot!!!)).

But for example, if there is a lot of desert, or say tundra or plains, hmm, it wouldn't be too good or a thing to be hyped about, after all it's low food and our city won't grow or have poor yields. But the flood plains before could have cottages and nice food yields/growth (3 food per tile!).

But as of now it doesn't seem the AI values these too much, or if it does, i hope to make it choose better, especially avoid tundra or desert, and plant nicely when it comes to choosing best city radius for the city it will plant/settle/found.

Data shown thanks to chatgpt 5, who also helped me and gave me feedback on these, check if accurate in `AIFoundValue::evaluate()` in as of now [/CvGameCoreDLL/CitySiteEvaluator.cpp](/CvGameCoreDLL/CitySiteEvaluator.cpp) for details.

"Settle Near — This table influences how the AI values surrounding tiles within a city’s workable radius when choosing a site. It doesn’t remove the tile, but adjusts city-site desirability based on local environment quality, rewarding strong growth or production neighbors (e.g., flood plains, grass hills) and penalizing unproductive or hard-to-use terrain (e.g., flat desert, snow)."

| Terrain | Feature | Hills? | Value Adjustment | Reasoning |
| --- | --- | --- | --- | --- |
| **Desert** | Flood Plains | Any | **+50** | Very high food and strong cottage potential despite health penalty; great for early growth in city radius. |
| Desert | Oasis | Any | **+50** | Solid food + commerce with fresh water access; cannot improve further but valuable from start. |
| Desert | None / Other | Yes | −25 | Low food but yields hammers from mining; minor defensive bonus. |
| Desert | None / Other | No | −50 | No food and no improvement potential (unless modded); very weak tile to have in city radius. |
| **Grassland** | Any | Yes | +50 | Low food cost with high hammer yield; strong early production option. |
| Grassland | Any | No | +50 | Excellent growth potential and flexible improvements. |
| **Plains** | Any | Yes | +10 | Decent hammers but low food; moderate overall value. |
| Plains | Any | No | −10 | Needs irrigation to match grass food; cottaging slows growth; weaker early-game choice. |
| **Tundra** | Any | Yes | −40 | Low food and weak yield; worse than plains hills. |
| Tundra | Any | No | −25 | Slightly better with mod’s commerce buff but still weak for growth. |
| **Snow** | Any | Yes | −50 | Same low food as tundra hill; minimal yield, high opportunity cost. |
| Snow | Any | No | −50 | Comparable to flat desert without features — essentially unusable for growth or production. |

### Choose best home plot to settle on (e.g. a hill plains tile or a desert tile is ideal, but not a flood plains tile that would be really bad unless otherwise very good locally (e.g. many bonuses nearby in potential city radius or such)

This section is about the improvements we made in our mod to tell the AI how to better choose which tiles are good to have in the exact tile where the city will be. For example, settling on flatland desert is quite good, because it removes a bad tile from our city radius, giving a higher chance if other good tiles, say flatand grass for example, are nearby, to have a better and stronger city. But if we did the opposite, say settling on the flatland grass, and having the flatland desert nearby in our city radius, it would be really bad: we would have wasted the good tile (grass), and now have a stupid bad desert useless tile to cry on xd. So we need to tell the AI how to choose its city with such rules, which as of now are not in base advciv or not enough if i'm not mistaken.

These rules are implemented with value changes, for example flatland plains is a bit bad, but flatland snow is very very bad, to help AI ponder and all when looking at all the map nearby and trying to choose best city spot. But before this "home plot" (i.e. the tile where our city will be when we found it) optimization, the value is largely decided by the settle nearby logic rather, and many other factors computed as well that we added or that were already here before our mod for most. This is logical for mathematical reasons, 1 tile has less value change than the 17 other tiles in city radius (e.g. if we say settling on 1 grass tile is bad and there are 20 (in the big fat cross) other flatland grass tiles, with other nice things like rivers, bonus etc, we won't mind barely due to all other valorization, but if we find a very good desert tile to settle on, surrounded by not so good 20 plain tiles, we won't be too hyped either, so this is like a small extra optimization if all things are quite similar otherwise for other home plot candidates, but still hopefully helps fine tune it further, and no reason not to if we can and which i liked to do if i may say as well (i was very frustrated with previous AI settle decisions before if i may say and in this case))

In addition to improvements for not settling on bonus tiles, this non-bonus and home plot tiles optimization, here is important and nice to also help the AI found and place better its cities and be more competitive or enjoyable to play with/against perhaps, at least i enjoyed adding them.

Data shown thanks to chatgpt 5, who also helped me and gave me feedback on these, check if accurate or updated in `AIFoundValue::evaluate()` in as of now [/CvGameCoreDLL/CitySiteEvaluator.cpp](/CvGameCoreDLL/CitySiteEvaluator.cpp) for details.

Note: we can't settle on oasis if i'm not mistakenso not shown in table and section below.

| Terrain | Feature | Hills? | Value Adjustment | Reasoning |
| --- | --- | --- | --- | --- |
| **Desert** | Flood Plains | Any | **−75** | Avoid settling on strong early food tile unless locally exceptional. |
| Desert | None / Other | Yes | **+50** | Low-food tile; decent fallback with extra hammer & defense. |
| Desert | None / Other | No | **+50** | Low-food tile; okay to remove for city center yields. |
| **Grassland** | Any | Yes | **−75** | Grass hills are very strong tiles; avoid removing them unless clearly best. |
| Grassland | Any | No | **−50** | Flat grass is valuable; avoid if possible. |
| **Plains** | Any | Yes | **+100** | Excellent: low food, extra hammer, defensive bonus — ideal start. |
| Plains | Any | No | **+25** | Good: removes low-food tile, but not a top priority. |
| **Tundra** | Any | Yes | **+50** | Decent: low food tile with extra hammer and defense. |
| Tundra | Any | No | **+25** | Slightly good: reduces a weak tile. |
| **Snow** | Any | Yes | **+50** | Similar to tundra hills; okay to settle on. |
| Snow | Any | No | **+50** | Same as desert: low food, safe to replace. |

### Results from these (non-home plot and non-bonus) settling on and settling near changes

Results so far seem to be that it does seem to help quite a lot from the few autoplay i ran, but perhaps numbers could be increased a bit, just, i wouldn't want it to compete with the bonus/malus system or overlap of bonus on tiles, or too high values may have some unexpected values who knows in city settling or such other or not civ4 ingame behaviours if i may say maybe.

I am not sure it always improves AI settling behaviour; there may be some cases where locally AI makes worse settling choices due to these changes, but in most cases, at least in theory, and although i don't know too much about these, generally/maybe it should improve AI settling choices even if a bit if not more than a bitmaybe, but test to be sure.

Still overall should be an improvement, ideally try it a bit more in this case, but is maybe fine or not too bad as is, again i only ran a few autoplay and don't know too much about these, but with chatgpt's help and my thoughts too, it does seem like an improvement.

Update: since latest refactor, although i didn't retest it yet, i'd expect results to be even better now with the fine tuning we added based on terrain (e.g. hill plains good to settle on for production bonuses for example, but less the more they yield then improve them rather), test it to be sure but should be extremely good, but since i didn't recheck it, test it to be sure.

## 26.2 - (Enhanced) AI settlers not devaluing very bad non home tiles (peak, ice cap, non hill desert without a bonus, non hill snow without a bonus) if we have enough of them in BFC

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1KTKWL7k9lKYxnzVg3aisDumCwdC1sUJh?usp=sharing).

This is another AI change we did much later hence the .2 to this old but still nice (was maybe is) point, by telling AI more specifically which tiles are very bad to have in our BFC. If we have a few / enough of them, we should strongly consider avoiding the site, especially if it is our capital/first city.

I have noticed the issue that usa ai settles a quite good site, but there was a much better one one tile south east that had more hill grassland and less very bad desert and peak. We need to give up the desert stone even if it's a bonus, if the site there is otherwise better, while this one here is otherwise noticeably worse.

Added code in `AIFoundValue::evaluate()` to handle that, see there for details, plus also added tunables/knobsin our new [GlobalDefines_advciv_sas.xml](/Assets/XML/GlobalDefines_advciv_sas.xml) fileto tweak this without having to tediously recompile every time anymore (tested to work).

Result ingame is very good as shown in screenshots, we now choose the correct best site, and future city north is also better, avoiding the coast camel desert site that has too many desert tiles, in favour of a coastal to the east desert plant that has iron and stone in its BFC as we need, but plenty coast to nicely benefit from it if we settle there. AI should be stronger as a result of this, especially if it leverages well this better site.

Update: upon further review, the site it chose was actually best as per our criteria xd, as ai values the extra west grassland even if it has to incurr a few very bad tiles that were not so penalized before if at all due to a bug xd. Also, to fix/enhance this i had actually used a bug to count very bad tiles with a bonus as bad, so it avoided the desert stone, but didn't mind going towards the desert no bonus xd unless we penalized it otherwise which we didn't or maybe did not sure. Still, after fixing the bug, ai prefer its starting location to settle on xddd, unless we penalize extremely heavily the very bad tiles (like -300 base value at start phase which is way too high and likely to cause issues in other sitesin our new global definesso better not), and i finally figured why: i think it simply values the non-home flatland and hill grass tiles west rather than the coast ones that we count as neutral as of now). It makes it so that the west grass tiles are about equal to the southeast ones we wanted to move towards, and all other things being equal, the start site that has desert stone in its bfc is valued much more than the south east site i wanted to move towards that ditched as in ignored the stone to go for a few more hill grassland tiles. I think my site is slightly better though, but difference is small, and this is because i don't value stone at all xd. I think it's a healthy habit for ais to value bonuses as a general rule though, and now making it aware of a few extra more bad tiles with fixed bugs and knobs/tunables, so left as such. Also, skewing too much the values will make us forsake very good sites just to optimize this local one. A better way should be to hierarchize bonuses (iron super important, stone soso especially considering we barely build any wonders, but i think it's better to keep this good habit for ai and should help much more in general sites, so ai should be stronger thanks to our changes although it started from a bug and went back to locally same site, hehe).

Update 2: the very-bad classification no longer hardcodes Peak, Ice Cap, flat Desert, and flat Snow names. Impassable plots always count; other non-home plots without a visible bonus count only when their best natural or XML-valid improved yield remains below a tunable threshold. This preserves the original intent while making terrain and improvement changes automatically affect the result. Visible bonuses on usable plots remain exempt because their specialized value is evaluated separately.

## 27 - (now fixed) Some promotions are missing in Sevopedia unit's placePromotions

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1hRe5rR9DPBH6XzwllwTLSnh9kbIQwkEG?usp=sharing)

Some promotions were missing in Sevopedia unit's placePromotions, for example for the generic swordsman or the zulu impi (melee units combat type), they didn't show collateral damage 1 and collateral damage 2 (as of now renamed from base advciv +/- civ4's barrage promotions).

So thanks to chatgpt's help, i found the cause althoguh i suspected it too intuitively hehe, but chatgpt told me the issue and provided me and in this code a working alternative condition of as of now `gc.getPromotionInfo(k).getUnitCombat(eUnitCombat)` (note: `eUnitCombat = gc.getUnitInfo(self.iUnit).getUnitCombatType()`) instead of `isPromotionValid(k, self.iUnit, False)` that was too strict, but just disabling this old too strict condition showed too many promotions even the ones these units shouldn't have access to such as of now collateral damage 3 and 4 for example.

This seems to fix the issue (see screenshots for details, as we specifically now see the missing promotions on top of same old ones (didn't check in detail but there seem to be more than before and also to have relevant ones, check screenshots or xml for details or comparison or such)).

## 28 - (now fixed) Wallpaper of our mod's custom being stretched vertically while some of the top of the wallpaper is not shown at all, at 1920 x 1080 game resolution

See [How to change the mod's main menu background image (for example to add a static image instead of default base advciv +/- civ4 image)](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README.md#how-to-change-the-mods-main-menu-background-image-for-example-to-add-a-static-image-instead-of-default-base-advciv---civ4-image).

See also: [How to remove the blue rectangle in main menu screen, change text color for example to black, etc. (in .thm files)](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README.md#how-to-remove-the-blue-rectangle-in-main-menu-screen-change-text-color-for-example-to-black-etc-in-thm-files)

## 29 - (as of now with a workaround) clicking on a specific spot in tech advisor at tech transhumanism's blue box causes a crash

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1-bhTzZeKZg8z_n0hcDJtAY8DnFfuuftg?usp=sharing).

I don't know what the cause is, but clicking, in tech advisor (i.e. tech tree view), on as of now tech_transhumanism's box (the blue rectalnge) specific position, we consistently get a crash and i have no idea why.

I don't know if me playing in windowed as of now due to it being so much easier for developping/debugging and or such(didn't test full screen).

Err logs and Dbg log don't seem to indicate anything related to this, so make sure you make enough saves regularly before browsing too much on tech advisor at least.

As of now, i have found a reliable/consistent workaround, which is to click on the tech name itself, then the crash is avoided and we are successfully redirected to Sevopedia tech

update: i have found the issue, and could reproduce it in particular with tech_agriculture, by adding an or prereq that is faulty or impossible to meet (i.e. xml asks tech_depopulation for example as of now here to research tech_agriculture, even though tech_agriculture shouldn't require any tech as of now (and tech_depopulation also requires indirectly uch earlier tech_agriculture, so it is impossible to meet this tech prereq for tech_agriculture, hence the crash when right clicking on the modified tech_agriculture's blue box as well)).

So it appears that the do research or whatever related or similar to it fails and crashes silently (would be nice to have an error message, ideally no crash). I added the lines below at tech_agriculture and it caused same crash:

```xml
			<OrPreReqs>
				<PrereqTech>TECH_DEPOPULATION</PrereqTech>
			</OrPreReqs>
```

So based on this, the crash is caused by impossible prereqs, but an actual error message such as impossible to process the doResearch command would be nicer, as well as ideally not crashing.

Ideally i would fix it, but is tedious, and most importantly, the issue should disappear when we have proper tech preresq not the fake ones that are not functionnal and just taken from any tech i could find to replace with our new techs. So this is only a temporary issue, although less idela, it is probably most efficient to leave as it is. It is also maybe more reliable to have a silent crash rather than adding a complicated way to handle that may react unpredictably and not necessarily always handle correctly the cause or other causes. So seems safer and most efficient to leave it as it is, and just keep in mind if tech advisor crashes happen again, that issue may be faulty tech prereqs.

See also, although not directly related: [README_Known_Issues.md#22---now-fixed-obsolete-bonuses-such-as-bonus_elephants-in-tech-advisor-ie-tech-tree-view-failing-to-redirect-to-sevopedia-bonus-with-id-none-causing-an-error-unlike-obsolete-buildings-like-building_spiral_minaret-for-example-successfully-showing-the-building-items-page](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#22---now-fixed-obsolete-bonuses-such-as-bonus_elephants-in-tech-advisor-ie-tech-tree-view-failing-to-redirect-to-sevopedia-bonus-with-id-none-causing-an-error-unlike-obsolete-buildings-like-building_spiral_minaret-for-example-successfully-showing-the-building-items-page)

## 30 - (Attemptingly fixed) AI workers not prioritizing bonuses to improve, especially food bonuses, and other AI workers optimizations or changes

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1xeAY-R41d3jQ8W4JvK8mhdRBlkKINpQu?usp=sharing).

This is an issue i had in base advciv, and this solution may not necessarily in all cases be better, but i believe and hope in most cases it helps, at least for the part of the code changed. Rewrote/refactored `CvUnitAI::AI_bestCityBuild` with gemini ai's help for most thanks to its persistence in particular (see [/README.md#gemini-ai](/README.md#gemini-ai)) for details.

I have written most details there, so only adding here as less tedious to do so, a few screenshots in the google drive link folder mentioned at the top of this known issue section (as of now number 30).

These changes hopefully fix this issue (see "Boston" screenshot in this google drive (as of now screenshot 1478)). Although i couldn't reproduce it directly since worker behaviour changed in more ways or it is autoplay variation somehow maybe (less likely but maybe?), starting from same save file 334 (also appended), Washington is quickly improved, firt with bonuses. In some cases, see screenshot 1499, other tiles seem to prevail, most likely due to other code parts, but it corrected soon enough and the silver was improved soon after which was the main purpose/goal of these changes (in base advciv i would have a bonus not improved for a few dozen turns if not more if i remember it correctly, which was very unimmersive), so hopefully AI is more efficient this way.

Ideally i would track other places where changes may be necessary, not sure i would do but maybe, or maybe not; in this case i mean.

As part of this change, i tried to increase AI worker efficiency by having them max put one worker to a tile to improve: if a worker is improving it already, skip it and go to another tile instead (there may be some delay until a worker goes there and starts improving it resulting in some ineffiencies of traveling there while a worker is also already travelling there, perhaps closer or not, but it seems to correct better, as soon as the closest worker starts, the other workers bounces back fast to another tile if i may say)

This is not always the best choice, but i believe generally AI would be more efficient this way.

As a side effect, this new code seems slightly faster (see gemini ai link for details).

I would want to do other changes ideally to AI worker and such logic, not sure i would but ideally.

update note: i have noticed that commenting out the `CvUnitAI::AI_improveBonus` function entirely in the inner body i mean in this caseand returning always and only false, we'd fix farm spices issue, however we'd lose the roading bonuses ability we had; i didn't see an easy way to selectively do this with AIs like chatgpt o3, so kept as is and tolerating occasional suboptimal improvements for the sake of having many nice ones often (we now mostly handle improving bonuses ourselves in `CvUnitAI::AI_bestCityBuild` in a way that should be much more efficient)

update 2: update: also disabled functionally `CvCityAI::AI_getImprovementValue` and `CvUnitAI::AI_irrigateTerritory` which solved the farm on spices plains issue when unwanted (not in our exceptions below) as well as inefficient and needless farms on floodplains or flatland grass or other unwanted interferences, see these functions (or whatever remains of them for details, as well as screenshots 1858 (no farm on spices plains and no farms on flood plains either since we're not starving) and 1863 (still no farm even at turn 150, now building plantation as intended and city looks very nice improved) for comparison; also not shown but no farms on flatland grass anymore since we're not starving there as well. We now have greater if not total control over our AI workers or close to it, and this improves ai efficiency further and is thanks to chatgpt and co or such like claude ai and such if i may say too (and thanks to me too)

update 3: disabling it entirely throws off workboats that use this too, then they stay parked in city, so updated this to disable it functionally only for land workers as we want them to use our optimized AI worker logic, but as for sea workers, fine if they do as such as long as works-functions

## 31 - (Attemptingly fixed) Deprioritize routes for AI workers in favour of yields first, except in some rare cases

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1BpwAkJ6V4cT8zeN99UOds7wu0efB5PUe?usp=sharing)

Rewrite and greatly simplify `BuildTypes CvUnitAI::AI_betterPlotBuild(CvPlot const& kPlot, BuildTypes eBuild)`, so that we deprioritize routes for AI workers, and build them only in very rare cases, especially in the early game where yields are so important (now prioritize yields over move speed advantage, should help AI a lot in most cases hopefully at least i think so in this case), and AI workers would often in base advciv waste time building roads first, sometimes even forgetting to improve the bonus in particular, or other tiles. I hope this makes AI sharper and more efficient, with a cleaner and much simpler best build override, thanks to gemini ai as well and thanks to me too if i may say in this case.

Areas of improvement not related to our code change:

- screenshot 1505: do not build cottage on plains, build on grassland rather, is a better tile to work, and improve any remaining bonus eligible to be improved before that

Hopefully i'd continue improving these ideally but may or may not do

update: these are fixed by now long ago hehe, but kept for context

update 2: since then, i added road choosing with chatgpt 5's help and thanks to my prompts and adjustments and such too handling in `CvUnitAI::AI_bestCityBuild` since we loop through all city plots, 2 patches in `CvUnitAI::AI_improveCity` and `CvUnitAI::AI_nextCityToImprove` so that we make sure to road these bonuses as soon as we can if needed (e.g. no river connection nor is bonus connected to our trade network), for example but not only when we discover the wheel later, but have improved our bonuses many or a few turns before that, so our workers would forget or maybe rather not pay enough attention to the importance to road/connect right away any connectable and not connected bonus in BFC, and autoplay results show in a few maps that they see and handle that much better now, but check if accurate especially as testing sample is small but it does seem a bit if not a lot better but check to be sure if is not a coincidence but reliable difference which i think it is (a reliable difference) but check to be sure

## 32 - (now seemingly fixed) Prioritize settling on coast when food environment is low (many tundra or plains or desert or snow (or peak although i assume is not counted but to be safe)) (the "Corinth screenshot")

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1O-5WGOwvufgZS9z2DJ-wY2hlkTJLhP8I?usp=sharing).

It was an issue i had in base advciv, when AI is in a low environment, say many tundra tiles for example, it is likely city would starve soon, so settling on the coast if in reach is much more valuable.

I added a code that counts low terrain or feature tiles in city radius, and if a certain amount is reached (as of now >= 7 medium low (snow, desert (and shoudln't be counted but peak as well but to be safe))), then we consider this environment to be low-food, and get discouraged if our tile is not coastal. The food penalty is increasing with the among of low-food tiles pas this threshold. See how i implemented it in `AIFoundValue::evaluate()` in [/CvGameCoreDLL/CitySiteEvaluator.cpp](/CvGameCoreDLL/CitySiteEvaluator.cpp) for details.

This means that what was a good spot is now not anymore a good spot, and AI will consider the next best tile instead similarly, which will not get penalized if it is coastal.

As can be seen in screenshots, with some previous changes i made, AI had a seemingly better understanding or/annd reactionto which bonuses are valuable and to settle near and not on, such as in screenshot 1475, here i assume to successfully grab the water bonuses thankfully thanks to our changes i assume that incentivize this more, however in screenshot 1476, these changes still did not compell AI to settle on coast and corinth in full tundra/snow is starved soon, which could have been avoided just by settling one tile south or somewhere near that for a much higher potential city relatively.

After these new changes i implemented in this known issue as of now 32, we can see that for example, AI still values water bonuses for coastal planting (screenshot 1580), but now also successfully settles on the coast even if there is no water bonus in range, just to avoid the low-food environment early starving (screenshot 1585 in now city sparta). In particular, thanks to the changes and buffs we made to coastal planting, it may be a bit stronger to plant on coast than in base advciv, relatively, although land should still be quite better as of now at least.

Hopefully AI is stronger with these changes.

update: increase the penalty a bit to solve some extra cases where some cities still didn't prefer coast, and which seems to indeed successfully solve it as well for these cities, see screenshots 1855 vs 1859 to 1862 for compare

## 33 - Tremendously improved and fixed and enhanced AI worker build/improvement logic in `CvUnitAI::AI_bestCityBuild`

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1WQUG049I2F1nPMhTVrnTstgNYjVslg9i?usp=sharing).

As written in the the [README_Main_Changes_Guide.md](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md):

Complete overhaul of `CvUnitAI::AI_bestCityBuild` [/CvGameCoreDLL/CvUnitAI.cpp](/CvGameCoreDLL/CvUnitAI.cpp) : now AI workers follow a highly optimized build (improvements) routine and strategy, based on terrain, food, health, fast chopping, etc.

This is done by completely ignoring base advciv +/- civ4 algorithms or logic, and defining probabilistically with a value tree our own value system +/- of priority to build based on our own advciv-sas conditions. Some of the changes include for example favouring cottages on flood plains unless we are low on food then farm, or not overwriting.

Oscillation (i.e. AI workers constantly changing their minds and ovrwriting a mine with a windmill, then a few turns later rewrite the windmill with a mine, etc) should be much much less frequent if not any, or cleanly managed, with a set of "holy" improvements never to overwrite (hamlet, village, town, workshop, etc) and semi-holy ones (farms in low-food environments, cottages in high-food environments as of now for example too), a penalty for overwriting improvements so AI improves other improvements first, a wait later system to keep best tiles for later if we don't have an immediate good move for them and methodically improving next eligible best, as well as a system to tell the AI which are best and bonus-specific improvements, to fix the banana cottage issue, it will do a plantation or nothing, unless the food gain is high (grassland irrigated for example) then it may do a farm very methodically else leave for later to increase AI worker efficiency.

Also, these changes fix and remove AI opening on a cottage plain, it will look for flood plains first, then grassland, etc. Logic is fine tuned on hills.

There are many related changes as well, please view code there for details.

In screenshots, it can be seen that:

- at turn 50, before any of our changes to this function(screenshot 1525), mecca has farms on grapes plains although plantations are unavailable, and it barely improved its much more profitable grassland tiles. Also, there is a hamlet (!!!) on plains iron which is now destroyed so all investment is lost, and not using this to improve other tiles and now have say a hamlet grassland ideally for example or something similar. It seems a plains has a cottage on it instead of grassland, very inefficient and waste of good tiles.
- at turn 50 again, but after our changes, in an early and conservative and much earlier version of our changes (screenshot 1571), mecca is beyond comparison so much more improved, with many villages at turn 50 on grassland, and the grapes have been ignored since we don't have plantation, so workers were not wasted. Needless to say AI is tremendously stronger now with these changes, the iron is ignored as well, although in some runs there seemed to be a cottage at the time in the aztec city (if not always, improving without bonus specific improvement tiles with bonuses should now happen much less often). Plains are ignored succesfully now until we build on higher food tiles first as intended.
- at turn 50 again again (screenshot 1641), mecca is still strongly developed, although a bit less advanced cottages but they are present, but it is better settled (not on hill grassland anymore due to some unrelated changes i made in the meantime, and its production potential is stronger The aztec cities are doing very well too, not improving nor capitalizing on any plains tile until grass for example are handled first, and bonuses are improved very early in the game as per past changes now fine tuned a bit if i may say or enforced/made sure no issue). AI is now amazingly stronger and more efficient at improving its cities.

Gemini ai and claude ai in particular helped me a lot do these as well as myself.

Note for modders: since this is done with if or else if or else checks, with many continue clauses at plot loop, it should be extremely fast to run as well, we may gain some time also since we don't use base advciv +/- civ4 methods/functions that may have been slower. Also, if you implement new terrains or features or modify existing ones, you'd need to update these checks as well, else your workers may stare clueless having no idea how to improve these terrains or features you added, and you'd need to specify their relative priority vs say floodplains or snow similarly. This is the trade-off or one of the trade offs of this very nice optimization but i believe it is very worth it, AI is very competitive now at growing its cities, at least tremedously more than before.

As a result, AI cities and workers should be tremendously stronger than in base advciv, at least in theory. They favour economy improvements a bit too much but seem to handle fine having enough production for now although a bit less than before as i didn't tweak it for such. They also favour slow and steady growth, and adapt to current food situation per city to decide next improvement, without overwriting other improvements that already exist until all good other tiles have been improved first, following a detailed value adjustment system, with the help of gemini ai and claude ai mostly as well as myself too hehe.

Next goal is to fix citizen allocation that is terrible in base advciv +/- civ4, as as of now for example (screenshots 1573 and 1574) ulundi is starving despite having unallocated pig and corn that are improved for many turns!!!! Or (screenshots 1595 and 1596) prague stagnant while its improved sheep grassland is unallocated. This is shit citizen allocation and i hope to fix it. Hopefully AI is already much stronger with our changes but thanks for past but i hope i can improve these things among others or not.

update : update: also disabled functionally `CvCityAI::AI_getImprovementValue` and `CvUnitAI::AI_irrigateTerritory` which solved the farm on spices plains issue when unwanted (not in our exceptions below) as well as inefficient and needless farms on floodplains, see update note 2: at [README_Known_Issues.md#30---attemptingly-fixed-ai-workers-not-prioritizing-bonuses-to-improve-especially-food-bonuses-and-other-ai-workers-optimizations-orand-changes](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#30---attemptingly-fixed-ai-workers-not-prioritizing-bonuses-to-improve-especially-food-bonuses-and-other-ai-workers-optimizations-orand-changes) for details with screenshots there as well for comparison

update 2: now also handles roading choice of build on not connected but connectable bonuses in BFC with other patches, see update 2 at [31 - (Attemptingly fixed) Deprioritize routes for AI workers in favour of yields first](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#31---attemptingly-fixed-deprioritize-routes-for-ai-workers-in-favour-of-yields-first-except-in-some-rare-cases) for details

## 34 - (Seemingly fixed/tweaked) Major K-Mod suboptimal food plot AI city allocation: starving or stagnant cities prefer 1 hammer over 4 food plots that are unallocated to any population ("Ulundi screenshots", "Prague Screenshots", and others) + food not being valued when food is production (e.g. worker, settler, etc if any more) when it is in fact the exact same and probably more reliable to set rather than production

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1yqmOZ1hSXPtgeVY69eFlj6R6OAM9mdze?usp=sharing).

These are a few of major k-mod bugs or very suboptimal city population plot allocation issues i have encountered. I noticed them while still in save file 334 which is a save file which helped me a lot enhance the AI (save file at turn 0 in drive in this known issue or related ones as of now) if i may say with gemini ai and claude ai's help as well for most and my help too xd...

About the issues fixed here or patched if not fully fixed, as can be seen in screenshots, before the fixes/patches:

- Screenshots 1573 and 1574 (the "Ulundi screenshots"): a city is starving while having one unhappy citizen, but this could be avoided by allocating any of the pig flatland grass or sheep flatland grass tiles. Although there would be no benefit to do so as city can't grow, starving is not good either, as if the food situation is resolved in the future, we'd be happy to start from a higher point, even if it costs a bit short term production, no need to starve ourselves to death just to produce a bit faster, pay a bit more food ideally to sustain our population during this time even if a bit and even if production is a bit less (ideally only a bit) relatively
- Screenshots 1595 and 1596 (the "Prague screenshots"): a city is stagnant while unhappy as well (1 citizen). Problem: the city allocates a 2 food 1 hammer tile instead of a 5 food 1 commerce tile. I don't believe 1 hammer is better than 3 food, we may want to grow, even if unhappy, and who knows, slave later, or maybe in the meantime unhappiness situation would improve, and we'd be happy to have the extra citizen, potentially also the food bar full and growing in the meantime. But don't overdo this, no point in growing too much if too many citizens are unhappy, but it needs some help here i think, even at the cost of some production, value food a bit more i think, but be careful to not overdo it
- Screenshots 1472 (and 1475 too if it is indeed from same time) (the "Boston Screenshots" again if i may say): a city is building a worker (food is production (same for the settler too and as of now)), but it could allocate the fish in anticipation of the worker being completed, so that city could grow at end of project. 3 hammer (and 1 commerce) is same as 3 food (and 1 commerce as well) to produce a worker, but the food is more likely than not, in most cases to be useful, especially for this tundra city that is low on food, so allocate rather the food than the hammer, if all other things are equal).
- Screenshot 1473 (the "Mycenian screenshot"): a city is stagnant, but it has many food tiles it could use to grow. Even if city is barbarian, the flatland grass tiles could be allocated. Note: the specialist usage seems a bit aggressive so we may want to tone it down early so cities can grow more, maybe, but not sure, kept as reference if want to see it later/again

The fixes: they are tentative and quite conservative, perhaps patches in some cases, i am not really sure i found the exact or all causes, but i hope these changes help a lot, as seen in these screenshots, not in same order as before in order to make explanation easier for me (sorry for inconsistency or inconvenience hopefully fine or not too bad to read but as it is maybe too but or not but or yes):

- the "Boston Screenshots" issue: i didn't test it, but i think one of the lines if not the line triggering it or related to it was `iValue += bFoodIsProduction ? 0 : (iFoodYieldTimes100+50)/100;` in `CvCityAI::AI_yieldValue`. Problem of this approach is that to produce a worker or settler, 3 hammer or 3 food is the exact same, it is 3 production, therefore food should be valued just as much, not 0. When worker is completed, city would be in a position to continue to grow, instead of stagnate or starve, even if a bit. I am not sure this is the only way or thing to fix and didn't check since, but i hope this helps. As of now, it is as such: `iValue += ((iFoodYieldTimes100+50)/100);` with some implementations differences (see below). It seems that in screenshots 1665 and 1666 (screenshot 1673 with the milder final version of the patch seems to indicate a good response as well, with the 2 food tile being used to produce a worker rather than the 1 food 1 hammer one, which should be better after this production (i.e. of a worker i mean) ends if), although it used a more exteme approach to try to fix and debug it (see below at ulundi screenshots), when producing a settler, the city does use food yields now even if it is just a small sampel and it could have happened due to other reasons (such as no good hammer tile to compete with the food yields maybe), but indirectly this would also mean developing cottages and such more while producing a settler or worker, here in a flood plains cottage, which is a bit stronger than a 2 food 1 hammer flatland grass forest tile. Although i am no sure this fixes it, it does seem to be better or at least not worse in this sample, while not deteriorating city behaviour early, hopefully helps and better this way.
- the "Ulundi screenshots" issue: in screenshots 1573 and 1574, similarly here, or rather not my bad, but i would say at least that we can maybe fix it or patch it at that line. I tried and implemented other tentative ways to boost food quite conservatively, else cities are very unhappy, low production and high pop (screenshot 1663 and 1664), and similarly the same at aachen (screenshots 1666 and 1667), which is inefficient, but at least all food plots were allocated, very nice ! This indicated that issue could be addressed this way, even if in a milder way. So i added a check that if we are unhappy (reusing old k-mod or civ4 bits for that but with a new check) value food only a bit more, but if we are happy (i.e. that we'd have room to grow), value food quite a bit extra more (but not too much i tried else we'd go back to high pop low production very angry inefficient city). So by giving a food boost but relatively milder one, we now grow but only a bit more, when angry, not a lot more (and when not angry (i.e. happy city) we'd grow a lot more although not shown here)). I didn't contine to check what happens at next turns, but in screenshots 1669 and 1670 for example after this fix or tentative patch, plot allocation seems now to be very very good. Production is high, and city is not starving, growing moderately, which is about perfect i'd say. After all we could slave as said before and would very much need or want the pop if our unhappiness solves. Aachen (screenshot 1672, but difference is city is not unhappy (i.e. is happy)) has also a very good food profile, with high plot plots all allocated and fast growth and quite high production, about perfect too!! Very good response or behaviour in screenshot 1674 as well in karakoum, which is happy too with high food and high production.
- As for the "Prague screenshots" (stagnant city not allocating food), i didn't retest it since prague was settled elsewhere many times, as shown in screnshot 1673, and consistently, i don't know if my change caused this somehow, but this is a fine choice too and a good location, after removing the jungle it is a quite strong grass spot, although a bit weak before that, and is coastal too so good for late game. So i don't have a definitive repsonse but i hope all in all these changes help a lot. Also, i don't know when i took this screenshot but seemingly later during the test changes phase, but seemingly AI would prefer a 1 food 1 hammer 1 commerce flatland plains cottage over an improved 5 food 1 commerce sheep grassland, just because it has 1 unhappy citizen. 1 hammer is not superior to 5 food!!! (or 4 food with the diff even), even if unhappy, extra pop could be used later to slave or when unhapiness is solved food would be more full even if we produce slightly less to do so!!!

The code that seemed to make a nice and decisive positive difference it seems to me at leastwas as of now this one i added:

```cpp
		// <!-- custom: commented-out line below (that was a test to try to fix known issue 34 which is seemingly done or at least bypassed at the cost of angry cities still growing and having lower production) fixes it or so it seems, but at the cost of lowered produciton, even if cities have few angry citizens, try to make it more fine-tuned to city current state: we value food as long as we are not angry, if we are angry, value production in an attempt to build things that would make us go out of unhappiness, but even if we don't, no point in growing further, the citizen won't be allocated; results of this change seem to be very good, cities are not starving anymore unallocating food tiles, they grow until unhappy, then it seems to halt but the food tiles are still reasonable allocated even though production is now high as well and growth slow it seems from quick testing / glances, although this is a patch and not full fix, i hope this helps the issue a lot, or so it seems from quick testing -->
		// iValue += ((iFoodYieldTimes100+50)/100) * 100;
		// <!-- custom: note: also include 0 happiness (i.e not unhappy) as it seems in another same file, ulundi again was starving while not unhappy nor happy (at 0 exactly) instead of allocating a food tile
		if (iHappinessLevel >= 0)
		{
			iValue += ((iFoodYieldTimes100+50)/100) * 3;
		}
		else
		{
			iValue += ((iFoodYieldTimes100+50)/100);
		}
```

I also did a few other tentative changes that may be relevant or not, not documented here, see [this git commit on the mod's github](https://github.com/wonderingabout/AdvCiv-SAS/commit/a6525a8b7c78ccc5058b657ec5d049d4c41d97a2) for details.

Appendix: i have noticed the issue still happens in screenshots 1690 and 1691, now in map 336 but somehow still in ulundi!! (Although all players should be random). The city was just at happiness cap (5 happy vs 5 unhappy = 0, although i am not sure it is exactly counted as such in our code but let's assume for the sake of explanation), so instead of `>0` i did as is now fixed also above `>=0`. The issue happened again with this change in screenshots 1695 and 1696 (starting from turn 50, the exact same save file that was already at turn 50), but after ending turn, fixed itself at screenshots 1697 and 1698 right away the next, with the very nice sheep hill grassland now allocated and starvation solved :) So i hope this fixes the issue or at least i'd like to think so. If not, i hope and in all cases too i mean if i may say that it helped, and that AI is now stronger or not weaker than it was thanks to this change (production seems good and strong too in this example ).

Hopefully AI is a bit stronger with this changed i attempted to make in a balanced way (not too much food, not as it was too much production)

See also [README_Known_Issues.md#40---seemingly-fixed--addressed-tremendousmajor-plot-allocation-improvement-2-if-we-are-high-in-happiness-favour-food-tiles-much-more-and-hammer-tiles-much-less-if-happiness-is-really-high-favour-growth-dynamically-and-plot-allocation-of-these-the-more-we-can-afford-it-even-if-production-is-slightly-reduced-short-term-as-a-result-it-auto-corrects-at-high-happiness-with-seemingly-much-stronger-ai-and-developped-cities-as-a-result-excluded-if-food-is-production-eg-worker-settler-etc-if-i-am-not-mistaken-but](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#40---seemingly-fixed--addressed-tremendousmajor-plot-allocation-improvement-2-if-we-are-high-in-happiness-favour-food-tiles-much-more-and-hammer-tiles-much-less-if-happiness-is-really-high-favour-growth-dynamically-and-plot-allocation-of-these-the-more-we-can-afford-it-even-if-production-is-slightly-reduced-short-term-as-a-result-it-auto-corrects-at-high-happiness-with-seemingly-much-stronger-ai-and-developped-cities-as-a-result-excluded-if-food-is-production-eg-worker-settler-etc) for quite related info

Update: now mitigated by high food loss from unhealthiness (as per corresponding SAS define) as inefficient to grow further (e.g., York size 25 with 25 health 36 unhealth (-11 food) and 39 happy 27 unhappy, +3 food per turn still, should not grow more and work specialists or other yields than food rather to increase efficiency).

## 35 - (Attemptingly fixed or addressed) AI building too many military naval units then gets invaded on land and can't defend (10+ galleons and barely any land defender) + do not prioritize water military units if city is landlocked (i assume it means stuck in a lake or something)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/15-WwGpkgFQ87O6t-tCQtJCAeiWQdQRXD?usp=sharing).

It is from when i was still playing base advciv, but it is an issue i had found (that i had named example 148, to be more precise 148.1 for the screenshot file), so the save file(s) or screenhsots linked in this google drive issue come from base advciv nor our mod, see for details the list of base advciv issues i had compiled as in listed gradually here in [this CFC forum post](https://forums.civfanatics.com/threads/ai-city-placement-and-misc-suggestions.695343/page-7#post-16782814) i made.

I did not test it since then, but i hope the patch/tweak/ tentative fix i added in as of now`CvCityAI::AI_bestUnit` helps and addresses that, making AI much more land-focused and overall stronger, even if it would now come i assume although i didn't check/test in this case at the cost of being military weaker on naval warfare, but i hope in most cases it would most benefit AI largely to do so.

I also fixed thanks to gemini ai various other conditions where we don't want the AI focusing on military naval units, such as before war (build more military land units rather relatively (didn't change land production although i'd want to but maybe fine as such for now, only removed naval military unit one)), or if city is landlocked (i.e. coastal but on a lake, then military naval units would be pointless there, leave it as it is for simplicity, but do not prioritize further in this case).

See also [KI#42](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#42---enhancedaddressed-tune-ais-preferred-based-unitai-based-on-war-status-offense-mode-defense-mode-combined-power-ratios-of-ennemies-etc-if-any-other-general-sanity-checks-and-efficiency-city-size-map-type-land-heavy-vs-water-heavy-vs-other-if-any-for-example-general-suicide-or-such-tendencies-etc) which generalizes, fixes and tunes this approach based on other conditions while otherwise preserving base advciv code behaviour. Hopefully a lot more efficient but also responsive/effective AI UNITAI choices but check to be sure.

update: see enhancement of this in [53 - (Beyond Tremendously Improved) Naval dementia of producing privateers/galleons then seemingly scrapping them and repeat, or of more importantly building galleons and privateers in droves and excess, despite enemy threatening cities of land capture for 20+ turns, and losing capital as a result](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#53---beyond-tremendously-improved-naval-dementia-of-producing-privateersgalleons-then-seemingly-scrapping-them-and-repeat-orand-of-more-importantly-building-galleons-and-privateers-in-droves-and-excess-if-i-may-say-but-despite-enemy-threatening-cities-of-land-capture-for-20-turns-and-losing-capital-as-a-result-fixedaddressed-by-now-managing-production-of-each-unitai-with-max-by-type-in-cvcityaiai_chooseunit-as-well-as-disallowing-scrapping-and-managing-it-by-unitai-type-globally-as-well-in-cvunitcanscrap-by-type-as-well-with-max-and-such-other-conditions-for-some-units-like-as-of-now-workers)

## 36 - (Attemptingly fixed or addressed) AI building settlers at critical time when war is likely, instead of preparing for war: very bad as the few more units with the hammer saved could make us gain or not lose the war, while the extra city makes all our empire thinner and our units split, on top of having less units overall as well

No screenshots from that time except save files, that i'd prefer not to rescreenshot now, however i had listed this issue in example 47 in the list of base advciv issues i had compiled as in listed gradually here in [this CFC forum post](https://forums.civfanatics.com/threads/ai-city-placement-and-misc-suggestions.695343/page-7#post-16782814) i made, where it happened 2 times to/for Augustus AI making it/himmuch weaker militarily and my conquest of him much easier in this game (although he/itwas still surprisingly strong so is like a wasted chance in this case at least)

In all cases, i have in a similar function than in [README_Known_Issues.md#35---attemptingly-fixed-or-addressed-ai-building-too-many-military-naval-units-then-gets-invaded-on-land-and-cant-defend-10-galleons-and-barely-any-land-defender--do-not-prioritize-water-military-units-if-city-is-landlocked-i-assume-it-means-stuck-in-a-lake-or-something-if-i-am-not-mistaken-but) (while doing this known issue as well](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#35---attemptingly-fixed-or-addressed-ai-building-too-many-military-naval-units-then-gets-invaded-on-land-and-cant-defend-10-galleons-and-barely-any-land-defender--do-not-prioritize-water-military-units-if-city-is-landlocked-i-assume-it-means-stuck-in-a-lake-or-something-if-i-am-not-mistaken-but) (while doing this known issue as well), a spot where we could add such a restriction to settler building.

Hopefully AI is now much stronger with this change as well although i didn't test it since i made it.

## 37 - (Workaround and rebalanced) AI building 2 settlers very inefficiently at same time or when a settler unit already exists - now settler is a national unit (only 1 allowed per player)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1Uf1OOilcGXfyNix7EwXYhQCcsd-bq4Pa?usp=sharing).

Expanding on previous issue as of now in number 36, i have also noticed, now in this as of now known issue number 37, that for example in screenhot 1680, AI was building 2 settlers at same time. It is very inefficient, and i thought that building one settler in top city (for efficiency, as weakest city may take a long time to build it hindering its growth or not getting settler ready on time; ideally i would handle that too but not done for simplicity and as of now simply building in any city that does it) is enough.

Instead of tediously telling AI which city to build its settler on, and only in 1 city at a time, as the hammer loss is huge of building 2 settlers, and also not if we already have a settler unit existing, as founding too many cities may result in economical inefficiency so build them gradually rather instead of spam then crash i'd say i think, making the settler a national unit seems a very very nice tradeoff and easy way to achieve that.

On top of that, it also adds strategy, as now settlers are more precious if i may say in this case at least, as although their price is same as before, killing/hunting a player's settler is worth more, potentially even worth going to war for depending on tempo and your or a player's strategy (kind of how declaring war to (attempt to) steal a worker (now restored in advciv-sas unlike in base advciv, see [README_Main_Changes_Guide.md#civilian-units](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md#civilian-units) for details) may be good intiative). So AIs and all players must get better or be more strategic or value more guarding their settlers, as losing one is a higher blow if one may say, as although cost is same, city building would be significantly more delayed.

I believe these changes add nice strategy and overall on top of AI benefits make the game really interesting. Although i was and am not still totally sure about it, maybe humans can use it to their advantage, for example to slave strategically or such to enhance their settler building maybe? Which may also be easier since slaving is worth now in advciv-sas unlike base advciv, so they can maybe have a small edge over AI players, at least for now sice i didn't or other modders hehe didn't optimize it. But AI players also have handicap advantages especially at higher difficulties so they wouldn't be as affected by this. Still, they may delay a tiny bit more building their cities which should also help them gain in effiency economically or not ruin their hammer production. Instead of doing an extensive code patch or fix or rework, i find or believe this works really well, perhaps even best, and i find it an interesting change.

As for the screenshots, after this change, in screenshots 1684 to 1689, the native american AI player now moves north instead, and is not building 2 settlers at same time. And while the settler is travelling, AI is not wasting time building another settler but is using effectively its hammer. I believe AI will be a lot more efficient thanks to this in most cases. Its city location is also nice in these screenshots 1689 and such, hopefully thanks to our city location settling/founding/planting choices AI changes as well.

Also this change is also thanks to claude ai which (who?) helped me locate where to make units national in the xml although i could have found myself but it helped still thanks claude ai.

Note: after retesting from turn save file at turn 0 to be sure, and also due to the below as of now known issue 38 so i wanted to test again anyway and since they seemed to do same when starting from save file that is at turn 50 if i'm not mistaken, i wanted to try from save file that is at turn 0 instead, i have found they did it even nicer, and settled extremely ambitiously a super nice city not too far from their capital, very very nice, see screenshots 1701 and 1702 (skipped 1700 since 1702 was more nicely centered around city but 1700 was first centered around city if i may say before 1701) for details.

## 38 - (No idea why) Sometimes compile mysteriously/strangely/inconsistently fails, and recompiling succeeds under/withexact same source files

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1rjgs7CbmxP78ixCWrf4W-a8xn_7mT68k?usp=sharing).

I have no idea why, and this is one of the strangest issues i have encountered so far in base advciv or rather advciv-sas, but recompiling dll after adding a code comment or tweaking it, for peace of mind in my case, resulted in a compile error at very end (see screenshots for details, log missing as i thought it was a regular issue or simply forgot to save it apart back it up, and overwritten at next compile due to my carelessness hehe if i may say but i hope the screenshot helps enough at least even though log would have been ideal maybe unless screenshot has all info).

This should not have happened, as i only changed code comments, which should be inconsequential regardless of what i type in them.

However, after recompiling, with exact same source files, no change at all (except maybe ctrl+z ctrl+y ctrl+s just to make sure i had no other change or for some other related or not reason), then suddenly compile succeeded.

At this point, or in general, i'd say my best guess would be a cosmic ray fell on my PC somehow and corrupted a bit like in the mario speedrun and as it happened to nasa.

But in all cases, and more seriously really, even though my previous guess was quite serious too, i'd recommend if all seems good otherwise, to make sure you remove all content in temp_files folder (as i have found fast compile seems to cause issues and i strictly avoid it unless doing quick testing never for final dll as of now at least, as mentioned in [README_Known_Issues.md#5---seemingly-worked-around-now-player-name-same-as-windows-10s-for-example-username-causes-new-game-screen-to-be-stuck-unless-a-custom-name-is-chosen-ifafterwhile-dll-has-been-fastdep-compiled)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#5---seemingly-worked-around-now-player-name-same-as-windows-10s-for-example-username-causes-new-game-screen-to-be-stuck-unless-a-custom-name-is-chosen-ifafterwhile-dll-has-been-fastdep-compiled) too; and note too: i think i also made extra sure here that i did delete it as well just before launching the faulty compile, hence my guess that it would be something else like a cosmic ray or something else maybe like a quantic ray xd maybe?? Added this extra clarification as part of reading claude ai's answer or the beginning of it, which gave me the idea to add this, hopefully clearer with this although maybe uneeded or maybe needed in this case i mean but in all cases), and compile again, which in this case, again strangely but all goood maybe xd if i may say although i would have liked to know how maybe too indeed. So adding this info for reference if helps.

Update: added a GitHub workflow sanity check for `CvGameCoreDLL/Project/temp_files/` (see [`build/temp_files.py`](/.github/workflows/README.md#buildtemp_filespy)). Git cannot track an empty folder directly, so the folder is kept visible with a zero-byte tracked placeholder file inside it. `.gitignore` no longer hides the folder, `.gitattributes` keeps it out of GitHub Download ZIP / git archive release archives, and the workflow fails if any other temp file or subfolder appears there. This does not prove a compiled DLL is good, but it makes stale fast-compile leftovers harder to miss. We check this because we suspect fast compiles can be unreliable, and it also helps catch forgetting to replace the committed DLL after compiling.

## 38.2 - (Weird DLL XML errors at launch, solved by recompiling) The exact same DLL (cosmic ray 2? Or something else maybe or whatever maybe)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1BnMPUrCSNI2q_yBj6ooC-xhoWT-vguxm?usp=sharing).

Another very weird weird weird! Xd... But this is definitely weird i mean.

I compiled the DLL while solving an issue or attempting to (related to a crash ingame at turn 156 with bestycitybuild function fixed by a guard i was trying to remove, but this is not the point, the point is read after brackets to see it i mean but anyways) but then i got very weird XML errors at game launch as in screenshots. I thought maybe i had changed something or whatever, but it should have been exact same DLL as one of the versions of the code i had tried just a very little while before.

So i exited VS 2010 C++ Express (what i use to compile), recompiled the DLL, and boom magically solved xd.

I believe this may have been one of these comsic ray issues or whatever, the errors related to XML missing fields or i don't know what are extremely weird, but sometimes you just gotta recompile i guess and bad compiles very rarely or not so very but quite rarely hehe happen, so far it's the second super weird instance i record/notice/remember.

So continuing to fix my issues now that this recompile solved this very weird and behaviour i never had before.

Note: i made sure as usual it's not a fast compile (i delete all the temp_files's content always if not then almost always before recompiling as i don't trust fast compile issues due to issues (no pun) i had with it, unless for fast testing or such), but still issue happened, so if i didn't make a huge mistake or something very unexpected there most likely seems to be something very wrong here, but as long as i can compile whatever xd maybe.

## 39 - (Seemingly fixed or enhanced) Make AI workers move sooner to City B or City C or such, and vice versa, if current city is already improved enough and don't need to be over improved, while other cities are not improved enough and would much rather need it

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1eabVp0msOXluGcyoKZzUHhNubsyAOR37?usp=sharing).

After our AI workers had nice and efficient, at least nicer and more effiicent worker routine and algorithm/priorities or more often, the issue i noticed is city A and city B are overimproved, while City C badly needed improvements but was under improved, as can be seen for example in screenshots 1728 and 1729, where Ectabana is not improved barely, while AI workers continue to over improve city A that can't allocate any more tiles anyway due to its pop limit (why improve 15+ tiles when pop is around 10, go to city B or city C or such other cities if any)

So i added a fix to that in `CvUnitAI::AI_workerMove`, with chatgpt o3's help too, see there for details.

After recompiling and testing these changes, as can be seen from existing screenshots between 1734 and 1740, workers move sooner to city C, and around turn 100 to 125, it has an overall nicer edge in terms of improvement, workers are not over improving city A or B too it seems at quick glance although i didn't look in detail, so hopefully AI is stronger thanks to these changes as well.

update: added an extra tweak so that workers stay longer in city B (small cities), as they are expected to grow fast, so don't leave at 2 improved plots if city size is size 2, improve say 4 or 5 plots (see code there for details)

update 2: tremendously improved and tweaked since then in [README_Known_Issues.md#41---seemingly-fixed-beyond-tremendously-improved-ai-worker-mobility-flexibility-and-reliability-now-favouring-minimal-big-city-improvement-come-back-to-it-later-but-dont-delay-improving-smaller-ones-quick-moving-to-smaller-ones-and-spending-longer-to-improve-smaller-ones-as-they-grow-fast-but-as-well-as-being-braver-in-our-own-cultural-borders-orand-moving-to-other-cities-needing-improvements-rather-than-being-parked-in-current-city-if-i-am-not-mistaken-but-and-such-other-changes-to-increase-ai-efficiency-reliably-and-other-changes-if-any-thanks-to-chatgpt-5-and-me-too-if-i-may-say-but](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#41---seemingly-fixed-beyond-tremendously-improved-ai-worker-mobility-flexibility-and-reliability-now-favouring-minimal-big-city-improvement-come-back-to-it-later-but-dont-delay-improving-smaller-ones-quick-moving-to-smaller-ones-and-spending-longer-to-improve-smaller-ones-as-they-grow-fast-but-as-well-as-being-braver-in-our-own-cultural-borders-orand-moving-to-other-cities-needing-improvements-rather-than-being-parked-in-current-city-if-i-am-not-mistaken-but-and-such-other-changes-to-increase-ai-efficiency-reliably-and-other-changes-if-any-thanks-to-chatgpt-5-and-me-too-if-i-may-say-but), see there for details too i mean

## 40 - (Seemingly fixed / addressed) Tremendous/Major Plot allocation improvement 2: If we are high in happiness, favour food tiles much more, and hammer tiles much less if happiness is really high (favour growth dynamically and plot allocation of these the more we can afford it), even if production is slightly reduced short term as a result, it auto corrects at high happiness, with seemingly much stronger AI and developped cities as a result (excluded if food is production (e.g. worker, settler, etc))

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1OsMF8q8NbcfGFS8oMg-mDkL_F6iju9_w?usp=sharing).

As can be seen in existing screenshots between 1742 and 1745, AI, here China AI, had a major problem with tile allocation, here choosing to allocate a juicy 0 food 6 hammer tile from about turn 50 to close to turn 100. Although the hammer is nice though, it is better to capitalize on food early (which can be symbolized very well as having happiness surplus (e.g. 9 happy and 1 unhappy is 8 happiness surplus)).

So thanks to chatgpt 3-o, and my prompt and adjustments or not or yes or etcbut it helped me lot too, i added a patch/fix/tweak in as of now `CvCityAI::AI_yieldValue`, to value food yields in plots the more happiness we have (for example as of now if i'm not mistakenwith 9 happy and 1 unhappy so 9 - 1 = 8 happy surplus, we'd have the food value now being multiplied by 8, but if happy surplus is only 2 (say 9 happy 7 unhappy for example) then the food multiplier would only be 2 which seems fine as it is quite mild maybe (i don't know but i assume seeing very quickly other mulitplicative calculations in this function but only glanced and from my memory of it so check to be sure) but still encouraging growth).

As an extra nice addition suggested by chatgpt 3-o, and that i tweaked too, if we are happy to very happy (as of now 3+ happiness surplus (e.g. 7 happy - 4 unhappy = 3 happiness surplus)), then we also reduce the value of hammer/production, as indeed, it is more valuable to grow, we'd allocate the high production tiles naturally as we have more population, and as long as we have extra happiness, better use it.

Not accounting for health to simplify, and as i assume cities would generally manage it well, even if high early is fine, cities should gradually remove unhealthiness generally if i'm not mistaken, so focus on raising pop as long as we have happiness surplus. Then, when we are close to happiness cap (i.e. happiness about equal to unhappiness, then do not value food as much and go back to hammer economy relatively and or other relevant yields or such (same as before)).

Also added the food is production exception, i.e. if we're producing a worker or settler, 6 hammer is better than 3 food. Provided we can bounce back to food allocation, which is not guaranteed. But thankfully, AI allocates and swaps tiles dynamically, this is extremely nice.

As for results, see existing screenshots between 1760 and 1782, but they are extremely good or so it seems in this situaiton at least.

At low pop, china AI best on food, and its cities quickly grow, and actively ignore the copper tasty 0 food 6 hammer tile, seemingly except when producing a worker as they should, then bounce back to food. China AI's city slaves twice, and has much more buildings at turn 100, effectively using the surprisingly high happiness reserve they have somehow. And China AI could build the great wall in time in its capital too, so high pop cities do not fall into too much food trap, this is a dynamic fix/patch/enhancement or fine-tuning, i don't know if it always apply, but i'd tend to say AI is much stronger thanks to it at least in this sample, other cities seem to behave fine at quick glance too (see the few screenshots there in this drive link for details).

I'm very happy of this result, thanks a lot to chatgpt 3-o for help despite the nagging and that it annoyed me hehe on math as i told it too it did hehe, but this helped me and helped a lot if i may say which i told it too, fix the formula and such thanks lot.

See also [README_Known_Issues.md#34---seemingly-fixedtweaked-major-k-mod-suboptimal-food-plot-ai-city-allocation-starving-or-stagnant-cities-prefer-1-hammer-over-4-food-plots-that-are-unallocated-to-any-population-ulundi-screenshots-prague-screenshots-and-others--food-not-being-valued-when-food-is-production-eg-worker-settler-etc-if-any-more-when-it-is-in-fact-the-exact-same-and-probably-more-reliable-to-set-rather-than-production](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#34---seemingly-fixedtweaked-major-k-mod-suboptimal-food-plot-ai-city-allocation-starving-or-stagnant-cities-prefer-1-hammer-over-4-food-plots-that-are-unallocated-to-any-population-ulundi-screenshots-prague-screenshots-and-others--food-not-being-valued-when-food-is-production-eg-worker-settler-etc-if-any-more-when-it-is-in-fact-the-exact-same-and-probably-more-reliable-to-set-rather-than-production) for quite related info

Update: now mitigated by high food loss from unhealthiness (as per corresponding SAS define) as inefficient to grow further. (e.g., York size 25 with 25 health 36 unhealth (-11 food) and 39 happy 27 unhappy, +3 food per turn still, should not grow more and work specialists or other yields than food rather to increase efficiency).

## 41 - (Seemingly fixed) Beyond Tremendously Improved AI worker mobility, flexibility, and reliability, now favouring minimal big city improvement (come back to it later but don't delay improving smaller ones), quick moving to smaller ones, and spending longer to improve smaller ones as they grow fast, as well as being braver in our own cultural borders or moving to other cities needing improvements rather than being parked in current city and such other changes to increase AI efficiency reliably, and other changes if any thanks to chatgpt 5 and me too

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1z05qmIF7_1V7TWVhtcr1HFxSKSeIQ9y2?usp=sharing).

There are many tremendous improvements to AI worker efficiency and flexibility in this known issue. These were aimed originally to solve the AI not moving to city B or city C soon enough or enough issue, as was attempted initially in [README_Known_Issues.md#39---seemingly-fixed-orand-enhanced-make-ai-workers-move-sooner-to-city-b-or-city-c-or-such-and-vice-versa-if-current-city-is-already-improved-enough-and-dont-need-to-be-over-improved-while-other-cities-are-not-improved-enough-and-would-much-rather-need-it](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#39---seemingly-fixed-orand-enhanced-make-ai-workers-move-sooner-to-city-b-or-city-c-or-such-and-vice-versa-if-current-city-is-already-improved-enough-and-dont-need-to-be-over-improved-while-other-cities-are-not-improved-enough-and-would-much-rather-need-it), and i tweaked it a bit more than solving this further, with chatgpt-5 's help and my prompts and adjustments or not or yes or etctoo.

As can be seen in existing screenshots between 1838 and 1934, even late in the game, jungle cities that were quite farm from core cities, although not too far really, would not be improved at all!! At turn 175 or something, which is extremely inefficient, and similarly, city A was overimproved, way beyond city allocation (what's the point to improve the 15th tile when city pop is 11 (perhaps with specialists even so would need even less plots to be improved "right now" maybe)), while city B or city C or even city D if any theoretically are not improved at all.

So i tweaked a few things and tried to find where the issue could, be, first of which removing lots of very shitty, sorry to say but really is as it is from little i know of it too, and chatgpt 5 agrees with me, base advciv +/- civ4 or whoever else wrote it despite other good things they may have done or not.

It would be too long to detail or i would be lazy or it would be tedious for me to do so, so the key changes are mostly if not only in `CvUnitAI::AI_workerMove` and `CvUnitAI::AI_nextCityToImprove`.

In `CvUnitAI::AI_workerMove`, i thought as suggested by chatgpt 5 too maybe workers are too scared to go in too far tiles, and chatgpt came up gradually with my tweaks toowith a code that greatly enhances AI worker flexibility, and i believe efficiency, in an attempt to make them go to city C sooner, or at least not make them not go to City C if we have assessed they should (city A improved enough, city B too), as of now:

```cpp
    /* Retreat logic policy change:
       --------------------------------------
       Old code:
         - Threat radius was 2 tiles in *all* situations.
           (Meaning: if any enemy unit was within 2 tiles — about a small city radius —
            we would consider the worker threatened and run for safety.)
         - Any threat → immediately retreat to the nearest city.
         - Result: workers often abandoned tasks too early, leaving some cities
           (especially jungle ones) unimproved for a long time.

       New code:
         - Inside our cultural borders: skip threat check entirely.
           (If an enemy is already on our tile, the game captures us before this runs.)
         - Outside borders: use smaller radius = 1 (only adjacent tiles count as dangerous).
           → This greatly reduces "false positives" from slow or harmless enemy units
             far away but still inside the old radius 2 bubble.
         - If threatened, FIRST try to redirect to a different, safer city
           that still needs improvements, instead of retreating straight home.
         - Only fall back to "retreat to city" if no safe redirection is possible.
         - This keeps workers productive more often while still avoiding capture
           in genuinely dangerous situations outside borders.
    */
```

This is very nice and hopefully we'd get less false positives, and although it was a bit better, there were still issues and some jungle cities still not improved or not enough, even though it had improved (no pun) to be a bit better now.

So then i removed the iNeed and iHave code base advciv +/- civ4 code (whoever wrote it), which is incredibly shitty and needless, we don't care if AI workers hover back and forth from one city to another, we already have a fine tuned and very straightforward and easy system telling them if they should go to city B or city C or not. They can always come back to city A if needed later (e.g. if city A has grown since then AND city C is now improved enough, for now).

Note: slightly related note: now that we use one worker per tile, originally for efficiency, AI workers are now very hard to capture/hoard :) So this is a very nice side effect, no need to be so scared about losing workers, just go for it. In the late game anyway, workers are not worth too much so fine if they are captured or destroyed, may even be good for economy actually (or worse to whoever captures them if an AI and it doesn't gift them or destroy them), and early ennemies are often not mobile enough and even if they are fine or not too bad, at least not worth the disadvantage of running away from nice to improve tiles that could directly benefit the city(ies). Hopefully this helps reduce if not solve the issue of AI workers always interrupting their builds, which is very inefficient too, but i didn't test it, they do seem less mobile as in interrupting then resuming very inefficiently same builds, which would be nice if true, but i didn't test it too much nor looked into it to know for sure, so i can only assume it hopefully helps but check to be sure. No more worker stacks to fear being cpatured for the AI or to protect or snatch for human players, i believe it's all in all much better on top of efficiency gains for AI workers.

Again situation seems to have improved a bit, no overly improving core cities anymore as well if not already done before, but still jungle tiles in these a bit far cities are still not improved. Then i noticed by a glance somehow xd in this case, as shown in screenshots 1941 and 1942, that in city A of persia AI, there are 5 workers parked. They are doing nothing since we told them don't overimprove city A, which is good, but now they don't go either to city C?? (city B is improved enough too), so it means our logic is working great, but something else is interferring.

As per chatgpt 5 's suggestion and my idea tooas part of reading its answers too, we now moved to `CvUnitAI::AI_nextCityToImprove`, where the final piece of the puzzle was. With extremely shitty and stupid iValue and bestBuild and such code. Aaah i had enough xd so much nonsense, we only want to improve a city, any city, as long as it's good enough, then stay long enough in it until it is extra improved enough (one or a few tiles more than city pop at the time where we decide to leave or stay in this city to improve it further or not), but it has this huge and stupid iBest iValue iNeed or not didn't even reread to check, i said look chatgpt, this is too stupid, let's do something else xd, i said something like, which i rarely do xd but it was really stupid to me at least it seemed soor at least needless this is "this code is a load of horse shit", clarifying that i was not talking about its but indeed this advciv +/- civ4 or whoever wrote it(i can write bad code too but i hope mine makes sense too, but if i make mistakes tell me).

So, chatgpt 5, which was released just yesterday evening more or less didn't check +/- remember in detail if afternoon or noonwhere i live, and which already helped a ton, wrote me this very nice code with a tiny bit of back and forth, i was fed up xd, yet eager to test it, so just comment out the huge mess and go xd.

And the result is extremely nice, beyond a tremendous improvement. See existing screenshots between 1943 and 1958 for details. Persia AI's city C is quickly and very fast improved at turn +/- 100 (97-105 in screenshots, which looks very good and nice), and the dream is thanks to our previous improvements (no pun) in bestcitybuild, AI workers specifically chop +/- improve only grass tiles so we can populate them later with our preferred build too, not plain tiles weirdly with a cottage or such like in base advciv +/- civ4 or such other mods. So all in all this is extremely nice, and i am thankful to all who helped me like chatgpt 5, those mentioned here or not, base advciv, kmod, etc firaxis for making this framework, and i am glad it is enhanced so much. I may have to reduce handicap settings now as AI would be unbeatable now with handicap that is too high, as its AI workers are now very very efficient i think, minus etxra tweaks we'd need like late game adjust for state property or whatever chatgpt 5 mentioned too, that we do partly indirectly but check bestcitybuild function in cvunitai or future known issues after this one if any. This is extremely satisfying, although i hope to improve it further based on autoplay and what i see, but i hope AI and AI workers can be a satisfying challenge now, after all economy and working tiles is key, maybe humans could automate reliably at lower levels if lazy or want to learn and get a really good result if the code applies here as well, but in all cases.

Update: see also related known issue as of nowwith extra very nice improvement(s) to wake from retreat logic causing parking in rare cases: [50 - (Tremendously improved/fixed/enhanced) Excessive AI worker retreat logic causing worker parking in cities in rare cases: now added a wake from retreat and other changes if any other change](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#50---tremendously-improvedfixedenhanced-excessive-ai-worker-retreat-logic-causing-worker-parking-in-cities-in-rare-cases-now-added-a-wake-from-retreat-and-other-changes-if-any-other-change-i-mean)

## 42 - (Enhanced/Addressed) Tune AI's preferred based UNITAI based on war status (offense mode, defense mode, combined power ratios of ennemies, etc if any other), general sanity checks and efficiency, city size, map type (land heavy vs water heavy vs other if any for example), general suicide or such tendencies, etc

Note: see also [README_Known_Issues.md#35---attemptingly-fixed-or-addressed-ai-building-too-many-military-naval-units-then-gets-invaded-on-land-and-cant-defend-10-galleons-and-barely-any-land-defender--do-not-prioritize-water-military-units-if-city-is-landlocked-i-assume-it-means-stuck-in-a-lake-or-something-if-i-am-not-mistaken-but](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#35---attemptingly-fixed-or-addressed-ai-building-too-many-military-naval-units-then-gets-invaded-on-land-and-cant-defend-10-galleons-and-barely-any-land-defender--do-not-prioritize-water-military-units-if-city-is-landlocked-i-assume-it-means-stuck-in-a-lake-or-something-if-i-am-not-mistaken-but)

See also: [Modding ressources (Mapscripts)](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README.md#mapscripts).

This is a major change as well.

I think i have found several issues with AI unitAIs and overall strategy, and as a result of tweaking these, AI is more competitive, has a stronger early game and more efficient one in most cases.

Here are the things i changed:

- disabled for AIs the unreliable unitais that are unreliable (`UNITAI_COLLATERAL` to aim for less suicides and getting baited and more focused defense or offense units, `UNITAI_PILLAGE` (no time to waste running around, this unit will not be focused attacking or defending, avoid this, inefficient), and `UNITAI_PIRATE_SEA` again not efficient and annoying, is also part of reducing naval warfare influence (see below for details), as a result we use our hammers more efficiently to have a more effective and efficient unitais. Say a swordsman will be an attacker or a defender, but not a pillager, so the stack will be stronger, and the cities more guarded, at least in theory, results seem good, as Khmer AI could pull an early rush on Medina and capture it with a strong stack.)
- restricted settlers for AIs to be built only in capital, and only if city pop >= 5 (i.e. not <= 4). This is so they can use more efficiently the food as production, as it's much easier to produce a settler using food from the many population count additionally to existing hammer yields as well, than it is at low pop. And if city stagnates, it is very efficient too, at least food is put to use instead of stagnating. There are other advantages, such as seemingly a bit less barbarian captures, and more units early. We may use 1 or 2 spots, but barbarian captures happen much less, and secondary cities can grow more. This change is in line with the settler now being a national unit as of now (1 allowed for whole empire including existing unit, check the [README_Main_Changes_Guide.md](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md) for updated values or info, or Sevopedia or xml). As for small new cities, it guarantees they grow as well instead of being stuck producing a settler for a long time, as hapepned many times and was the original reason why i did this to begin with, then expanded on it. I added a patch, although should never happen with the settler being a national unit and only in capital, but that if city is very small and stagnant, switch to worker instead, but since only cpaital as of now produces them and it grows fast, this shouldn't happen but if changed this patch would help as well small cities being stuck in a very lnog settler production and being stagnant, in fact it's necessary now else our capital can't produce a settler, as chatgpt 5 noticed or noted as well. Update: also as it mentioned to me to add here as well, there are exceptions such as a city somehow being stagnant, then even if pop is small, we are not using the food anyway, so may as well take our chances and build a settler, as it rightly told me to add to this doc hehe which i forogt but i think this is a quite good summary otherwise...
- free window: during the first as of now 75 turns at normal game speed (adjusted based on game speed), the AI will have free production of settler (minus restrictions said before). So it can take its time and grow freely. Then after this window, it will consider which strategy to take, either offense mode, or defense mode, or other maybe which i added hardcoded in cvcityAI. Based on these, it may not build settlers anymore and start to stack units. This is something i had a problem with in base advciv, of AI expanding again and again while it was near me, instead of preparing for the likely war. Hopefully AI would react better to these.
- additionally, tweaked unitais, although i don't know how effective these changes will be or if i did them at the right place, in `CvCityAI::AI_bestUnit` and `CvCityAI::AI_bestUnitAI` and `CvCityAI::AI_chooseProduction` functions as of now in cvcityai. It does seem though as of now to be taken quite well into acocunt, but test to be sure. This also depends on map type (less on naval maps, a lot more on land maps, hybrid in other maps, see above links in this known issue for details), but now for example if an AI enters offense mode, and the map is a land map, say pangea, continents, etc, as best as we could classify them i mean with chatgpt 5 if i may say so check if accurate and if works as intended test to be sure, AI will more or less ignore unitais that don't help it directly in war as we instructed it, so it will value a lot more `UNITAI_ATTACK` or `UNITAI_ATTACK_CITY` for example, a bit of `UNITAI_RESERVE` (visible in debug mode (ctrl+z and "chipotle") by holding ctrl or alt i forgot which while hovering on a unit or unit stack), and this means its units won't wander or such and attack more decisively at least in theory, and vice versa in defense mode they'd value these less and unitais such as `UNITAI_CITY_DEFENSE`, `UNITAI_CITY_SPECIAL`, `UNITAI_RESERVE` etc if any more as well i mean too, for the most part. Hopefully helps the AI better execute its attacks but many things could influence it. It will not care to produce any naval or such unitais units. So it can produce say a swordsman with the attack_city or attack or even reserve unitais maybe, but naval units can't have these, and their unitais like `UNITAI_ATTACK_SEA` or such are tremendously less valued. This avoids the issue i had in base advciv of AI having 10 galleons but barely any land defender on a pangea if i'm not mistaken, see above links for details as well. In naval maps, if detcted as such with our code, this is toned down a bit, but the general idea remains to protect our cities first and foremost, and aim for most effiicent roles, see cvcityai for details. Also, is this galleon / trireme / galley really worth the 2-3 extra axemen / swordsmen / extra worker or half settler? Probably not, and wastes turns time to build not just ressources as in yields, so we are delayed in war plans, tech etc. I believe it is more efficient to do so at least for AIs and in most cases. I didn't test code too much, but based on it semeingly having much less barbarian successful invasions, and on the theory of efficiency behind it as i explained and ideas i got and autoplay results, it seems better for the AI to go slower, even if we lose 1-2 city spots or wonders, the benefits are larger it seems. This is a summary i attempted to do of the changes and again didn't test too much so far; while i hope it helps the AI, i am not necessarily too open to feedback, so i would suggest you best share your experience regarding this on a forum, such as CFC forum, i do hope that it helps and is enjoyable to play though. I also hope these changes fix base advciv issue of AI abandonning capital city, sometimes in a way that ruins the entire game, just to attack 1 unit. I didn't test it, but i hope with these unitais that now exclude colalteral, pillage, etc, units would be more efficient in not doing so, and better guard cities, as well as be, when on offense mode, more focused on their goal, at least in theory, but many other parts of the code could interfere or i could have gotten the logic wrong somehow. It seems to be applied quite well in few autoplays at a quick glance, which maybe helps making AI stronger but test to be sure.

Update: now caching mapname is landheavy or mapname is navalheavy info as boolean only once per map load (new game, load save, etc if anymore we hopefully handle, see the new `CvGame::recomputeMapnameHeaviness` we added for details and their corresponding new `m_bLandHeavyMapname` and `m_bNavalHeavyMapname` (check if accurate as i don't know too much about these, done with the help of chatgpt 5). Seems to be behaving as intended though from quick testing in autoplay (as much land units in land maps with low naval units as intended, and many naval units in naval heavy maps, so hopefully safe enough or safe and working as intended i mean if i may say but check to be sure).

Update 2: include more map types and change the way we evaluate this, see code for details

## 43 - (Attemptingly improved/enhanced) AI settlers, for the first city found (i.e. at turn 0), settling too soon instead of digging a bit for better sites, and other related changes

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1TTw-Ya5yHNh3iuXgGWw-9vw_E6ykdps8?usp=sharing).

A few changes in this issue, with i believe more potential for long term better first city sites (i.e. at turn 0), but if AI misevaluates best site we can tweak it as the functions responsible for such rather.

For now and as of now, here are the main changes, in `CvUnitAI::AI_foundFirstCity` and other more minor functions (see below for details) i made to base advciv's founding first city logic, with the help of chatgpt 5 and claude ai:

- no more hurry/panic fast settling and no penalty per turn not found, i.e. in old base advciv system, there was say a 15% penalty to the value of all plots per turn. So no matter what, a tile to found city at would only have say 85% of the value it had at turn 0, no matter how good it was. I believe this was done to encourage fast growth or such maybe or maybe for other reasons or not, but i believe giving AIs time would lead to better long term outcomes, especially when starters are really bad, like tundra, not enough land tiles, etc. For now, i am only addressing the issue in a general way, so our new system now gives AI settlers as of 5 turns to path to consider best site without any penalty, meaning as long as a site can be reached in 5 path turns (i.e. to walk there), then only best value will be considered, no penalty per turn. This window is longer than in base advciv.
- after the free window ends, we get stronger penalties to quickly encourage settling, i.e. if a tile gets say 6 turns from turn 0 to get there, it loses 50% value, meaning unless it's super high value, it would be highly unlikely to be chosen, but still not totally impossible. Then for 7+ tiles no tile is considered, only the best from before is taken. Meaning in total we have a window of up to 6 turns to choose our best city, with 5 no penalty free ones. In save file 336 i often do auto play on as of now at least, spain AI founded its capital on 5th turn only, it chose a strong starting point, although it didn't develop it totally optimally, but in theory it could do well. Its early game was slower as a result, but with more land tiles, river so more commerce and health if not before (not here but in theory), and many commerce bonuses which would help a lot with plantations later. Food is lower but potential higher, as more land tiles can be grown. Most AIs didn't change their preferred best tile in this save file, so it may not make a huge difference, but may, especially for bad starts.
- Another change is non-coastal sites are not penalized anymore, by disabling the code that did that in `AIFoundValue::evaluateYield` no non-coastal penalty is applied. I.e. if a city site is not coastal, it will still be considered best if it was the best, and not be discarded like in base advciv. I believe to just take the best, and if it happens to be coastal great, if not land is probably stronger then. We added code in evaluate function to tell AI when coast is better (such as when terrain is rich in high food, or if there are water bonuses)
- Also, we now don't discard sites that are not on fresh water or river unlike in base advciv. If they are otherwise the best, it woud be a really bad move to discard them just to get river and a worse site. Similar logic than before for coast.

As for examples, as i said Spain AI, screenshots 2100 and 2101 show how it was before this change (minus all other changes we did since base advciv that are here though), and then remaining existing screenshots between 2092 and 2107 show how the AI behaved with this change with the other site it took. Again it had a slower growth as a result, but i believe long term potential of this site is higher. In other maps, in particular tundra or such although i didn't test them, it can be expected AI will/would actively avoid them rather than settle here, but test to be sure.

Note: part of the reason why its growth was slower is due to using a specialist too soon when it had room to grow if i'm not mistaken, which i attempt to fix, even if not the case here, as it happened in other cities before this change and is really crippling.

## 44 - (Enhanced) Make/Encourage AI settlers walk away from bad starting sites

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1G0PcE4CyEcVUJCoOyzM4970U7YSARM5O?usp=sharing).

This tremedously improves again AI settler preferences by doing targeted but really impactful changes in `AIFoundValue::evaluate()`. Also chatgpt 5 helped me a lot for it and other AIs too like claude ai, deepseek ai, it was a huge mess due to the `return 0;` and overflow avoiding attempts or weird code behaviorus i didn't want to mess with too much as long as it worked / would work which it didn't for a long while xd but thankfully it does now, and AI is strong shiny and awesome, i believe even on settlers games would be challenging and interesting, but there are many areas AI can improve still and i hope i can contribute to but not guaranteed may or may not.

About this issue, many things were changed while solving this issue, but first the relevant one is (see the [README_Main_Changes_Guide.md](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md) for details on other related improvements) here to move away from too watery starts (except water bonus plots), past a certain threshold, so as of now our threshold is 12, meaning as long as we have 12 "good" bfc plots (land plots (including peak as what we really want here is to just avoid the coastal start, so that we have more tiles to grow into cottages, mines, workshops, also a more central position for better expansion midgame and higher likeliness to have a radial empire, better center map position for wars or invasion or such and defending the empire from the capital, etc if any other advantages), or water plots but with a bonus like fish) then we're good.

But if we have less, say among our 20 bfc plots (excluding the home plot (i.e. where the city will be planted if i am not mistake(as we won't harvest it so no need to count it, it doesn't matter what it is as long as we can settle on it)), so not 21 tiles but 21 - 1 = 20 plots instead), only 10 are land, 1 is bonus fish so counted as well so 10 + 1 = 11 good plots but is not enough to reach the 12 required, (meaning we have 20 - 11 = 9 non bonus water tiles), the we have a strong penalty from this threshold telling the AI settler to move away from here, usually to a more central position, and with good yields.

This makes AI starting points a lot stronger, especially for bad starts such as for moscow AI (see screenshots 2164 before the change vs 2179 after the change).

Other cities behave also better, by moving to a more central position, they indirectly are reserving a nice spot for their city 2 or city 3, and in fact the original moscow AI spot is nice for a city 3 or city 4, but for capital it's not enough and moscow AI was certain to fall behind. In continuation with our changes at previous known issue as of now [43 - (Attemptingly improved/enhanced) AI settlers, for the first city found (i.e. at turn 0), settling too soon instead of digging a bit for better sites](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#43---attemptingly-improvedenhanced-ai-settlers-for-the-first-city-found-ie-at-turn-0-if-i-am-not-mistaken-settling-too-soon-instead-of-digging-a-bit-for-better-sites-and-other-related-changes), the AI settlers have up to 5 free unpenalized turns to choose their best spot, much unlike in base advciv or civ4 too unless i'm not aware of it or mistaken maybe or just not knowledgeable if the case.

I believe Moscow AI will have a much better game as a result, and it really walked 5 path turns to this spot, which is very nice.

But it is not automatic, for example Edo AI (kingdom of benin) chose to still settle coastal, as it didn't reach its threshold of 12 good tiles not being met, and assessed coastal to be better. But many AIs moved away, to i believe better spots, see screenshots for details. Paris AI was also surrounded in water tiles (9 non bonus water tiles so it had met threshold too), but its site was quite good, still, forcing it to move away, the site is slightly better, as although it chooses to found on grass cow/cattle, it is actually better when i think about it, as there is 1 free food yield (i didn't tell them about this, only the free yield for hill plains hehe but still they preferred it nice if i may say although i could tell them too but fine as such as a general rule maybeespecially if they handle fine these edge cases), more land tiles so more cottages or worskhops or potential to do so, nice for a capital, and still enough food bonuses on water, and fresh water, so all in all much better than original start i think, although really not intuitive.

I did many other changes small or not, for example, teaching AIs to heavily faovur settling on hill plains due to many advantages it provides, see the [README_Main_Changes_Guide.md](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md) for details. Timbuktu AI also was the last one i told by tweaking value to move away from the 3 desert, to 3 any other land tiles (did same for Constantinople AI telling it not to settle on flood plains further more despite how good it seemed, see screenshots (e.g. 2174 still had the issue for constantinople AI vs not in later ones) for details too).

Note: thanks to our/these changes, the game turned much better for these AIs, for example moscow AI has as stronger central position and a nice strong empire and army at turn 100 with nicely positonned capital, which wouldn't have been possible or so easy starting from the edge. At turn 150, they are crazy strong xd, very nice. (!!) I hope i can improve the AI even more :), this is just at emperor xd btw, so i hope they provide a good challenge now, but i have many ways i want to improve them still hehe and ideas and all hopefully.

Note: these are done at emperor difficulty, before changing all tech prereqs, so tech tree is still mostly base advciv one minus many changes we made but no deep reordering yet, so hopefully quite representative of how strong or how AI behaves now vs base advciv, which i'd like to think is stronger now even though base advciv was not too bad and i have other ideas to improve ours further while fixing issues i added or remaining from base advciv +/- civ, not guaranteed i would though, i deally i would want ot, may or may not,.

## 44.5 - Disallow citizen specialist as it is a really bad choice (unless absolutely necessary)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/13QF4EHJMAg8Eur-H6N0qYVd_nvWXgupS?usp=sharing).

Disallow the citizen specialist as it is really a bad choice that AIs would often go for, in `CvCityAI::AI_jobChangeValue`, also added a few extra sanity rules in this function for specialist allocation, which attempt to patch the logic rather than globally or tediously enhance it in an uncertain to be or easily reliable and better.

Hopefully this also and most importantly helps increase AI efficiency and strength/competitiveness in the game

Update: seems mostly effective, but sometimes the AI still assigns a citizen even though it seems like it is not the best choice (other plots can be allocated or other possibilities if any, etc.)

Example:

```txt
Assert Failed

File:  ..\.\CvCity.cpp
Line:  9504
Func:  CvCity::changeSpecialistCount
Expression:  false
Message:  SAS citizen debug: T51 city=Mecca (44,25) owner=Saladin adding +1 default specialist (citizen).
```

Added this assert to help track these (with a debug or such if any such DLL).

However, most of these seem to be either false positives or never effectively added, as when i stop autoplay i almost never find a citizen specialist in said cities the next turn. Although sometimes they are still assigned as citizen specialists the next turn which helps show it.

Update 2: seemingly now fixed by reapplying the patch in `CvCityAI::AI_jobChangeValue` that was somehow removed at some point in one of the advciv-sas changes i added i guess. Now no assert firing at t100 with a debug dll anymore vs a few to quite a few if not more xd i mean. Also none even at t170+ from quick autoplay testing, so it seems fixed or issue is greatly reduced, thanks to chatgpt 5.1's help. I adjusted its code a bit.

However, we have and also had beforethis cascade of asserts firing:

```txt
Assert Failed

File:  ..\.\CvCityAI.cpp
Line:  263
Func:  CvCityAI::AI_assignWorkingPlots
Expression:  false
Message:  failed to assign extra population

Assert Failed

File:  ..\.\CvCityAI.cpp
Line:  273
Func:  CvCityAI::AI_assignWorkingPlots
Expression:  false
Message:  failed to assign extra specialist

Assert Failed

File:  ..\.\CvCityAI.cpp
Line:  286
Func:  CvCityAI::AI_assignWorkingPlots
Expression:  extraPopulation() == 0
Message:  
```

I don't know if it is related to citizen specialists not being usable as a fallback, or if it's an unrelated issue, but added for exhaustiveness or reference.

## 44.6 - Disable auto citizen specialists for the human player as well

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1ZfWnBLpsklVE7qhgSf_wyxVpVPMLOzsK?usp=sharing).

Following [KI#44.5](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#445---disallow-citizen-specialist-as-it-is-a-really-bad-choice-unless-absolutely-necessary), also applying this no auto citizen specialists setting as an option for human players as it can be very annoying to have to auto check it every while, as of now not done.

Tested after having added the code in `CvCityAI::AI_jobChangeValue` with the help of chatgpt 5.1 thanks, it fires like +/- 10 times per turn at turn 300 in our human player's cities at turn 300, yet no city of this player has any citizen specialist the next turn (at turn 301) so it looks very effective.

Example:

```txt
Assert Failed

File:  ..\.\CvCityAI.cpp
Line:  14367
Func:  CvCityAI::AI_jobChangeValue
Expression:  false
Message:  SAS citizen debug: T300 city=Cumae (21,17) owner=PC: no type=SPECIALIST_CITIZEN auto specialists for human players.
```

We seem to have the same assert cascade issue though as in [KI#44.5](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#445---disallow-citizen-specialist-as-it-is-a-really-bad-choice-unless-absolutely-necessary), but as long as it works maybe this is not urgent, although ideally would investigate it, but not urgent if i ever do it i mean.

## 45 - (Addressed / Patched / Worked around) AI cities assigning too soon or too often specialists, resulting in early stagnation very inefficiently: now added sanity rules to not go for a specialist

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1f58Su5b-Y3Vgu1th8K3EYWZvuYC47u_t?usp=sharing).

Note: these are not exhaustive, i noticed the issue happen in many cities as well at least quite a few, prompting me to do this/these changes which hopefully help the AI be stronger and more reliable in its specialist choices (or non-choices if i may say in this case), see as of now below for details.

In continuation with the changes to disallow the citizen specialist as it is really a bad choice (see [KI#44.5](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#445---disallow-citizen-specialist-as-it-is-a-really-bad-choice-unless-absolutely-necessary) for details) that AIs would often go for, in `CvCityAI::AI_jobChangeValue`, also added a few extra sanity rules in this function for specialist allocation, which attempt to patch the logic rather than globally or tediously enhance it in an uncertain to be or easily reliable and better.

So adding, rather and instead some sanity checks that hopefully help the AI be more efficient with its choice, making saner ones if i may say or statistically going to be most often helpful, while not killing versatility hopefully, which as of now are (see `CvCityAI::AI_jobChangeValue` or related functions if any for updates on these (as of now only in this function) (and also added with the help of chatgpt 5 too thanks):

- low population cities (as of now <= 4) should never assign any specialist at all (they should focus on growth almost always, and if they can't grow, on yields then or whatever else they can do, should more often than not be helpful). See example of AI issues addressed with(/by?) this change in screenshots of this known issue. Hopefully helps AI a lot be competitive if i may say in this case.
- mid size cities (as of now <= 7) with other conditions such as happy extra happiness (as of now >= 1 surplus (e.g. 8 happiness 6 unhappiness)) and extra food to accommodate this growth (as of now food difference >= 2 and not food is production that changes this formula) should favour growth and not assign any specialist. Hopefully this helps AI grow its cities faster while not killing versatility, as when they stagnate or are too big, they would fall back again to previous rules which seem otherwise to work quite well minus the edge case of low pop cities that don't grow at all due to too early specialist, which i hope these intend to patch/work around while making AI stronger as a result too as well in most cases at least
- for barbarians, on top of these rules, which should affect most of its cities, only allow the scientist specialist, as they have no use for the priest or spy or such, but the scientist specifically may help them stay relevant longer in tech without killing versatility, especially if we make them stronger later in the game so they don't disappear too soon but as of now hopefully this helps the AI as well in case it assigned such specialists.

Hopefully they help AI be stronger and more reliable in its specialist choices or rather maybe non-choices here

Note: on the plus side as well, not having to think about specialists at all in some conditions will probably save quite a lto or a bit at least if i may say of computation as well as a nice side effect too hopefully while preserving versatility or preserving it enough and assuming our change works as intended (would need to test more to be sure)

update: after a bit further evaluation, i have decided to generalize the previous rule as quick patch, as for example in screenshot as of now 2270, edo city (kingdom of bening) is size 12, can grow (stagnant with a specialist equals food is 2 without (in fact more due to poorly assigned tiles but it's another issue that looks or may be tedious to fix although would be nice)) but chooses instead to assign a specialist, so generalizing the "grow when you can" policy.

## 46 - (Cleaned up) Very big messy old uiFlag code in the DLL, seemingly to support savegame compatibility, which i don't care about, especially considering how complicated the code is as a result

In the DLL i have cleaned up the old `uiFlag` code that was super redundant and messy, with the help of chatgpt 5 and a bit of claude ai too. I don't know too much about these, but if i understood and understand i mean too correctly this code was responsible for keeping savegame compatibility.

While it would be nice if old savegames could be preserved across all versions, it is ridiculously complicated to do so, and the previous code was beyond a mess xd (at least to me). I have cleaned up all of it, which saved about 50 kB from the DLL size as of now, and is hopefully much cleaner in this case i mean.

As a result, savegames are not compatible whenever a breaking change is made in AdvCiv-SAS. See related info at [/README.md#not-supported-in-advciv-sas](/README.md#not-supported-in-advciv-sas) as well.

## 47 - (Fixed / Addressed / Enhanced) AI choosing poorly promotions for its units: now added a set of hard rules in which case some promotions are not good and to ignore as is most efificient in most times, and rarely cases where some promotions are best to always go first for (e.g. as of no city_garrison first for unitai_city_defense, city_raider first for unitai_attack_city, etc if any more)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1xbBTVeF_vqn5DbyIpqkSl-__0pFs0hRX?usp=sharing).

This is one of the core issues i had with base advciv and hopefully fixed or addressed in a way AI is now (much) more reliable with its promotion choices, while hopefully not restricting or reducing too much versatility.

My observation and annoyance, was that AI would often go for very inefficient or even simply ineffective promotions like woodsman (useless in city combat and in most non city tiles as well except for few units), medic (better be stronger and win or die is more efficient), that were surprisingly popular among AIs for some reason.

I added with chatgpt 5's help and my adjustments and prompts and such (in `CvUnitAI::AI_promotionValue`)some hard rules that in most cases don't change AI selection process, but just make it start from a more restricted pool, and in rare cases forces an always first choice when absolutely best or most efficient in most cases so going for this for AI players to simplify and for effectiveness too. This can be seen in existing screenshots between 2237 and 2403 (which are not the most representative of how bad AI choices were, but they give some context/examples of how it could often be suboptimal or ineffective promotions as explained before).

Below is a summary of these by chatgpt 5 which i adjusted a bit and suggested this or that but that it otherwise very nicely for the most part put apart (no pun), check if accurate, and if it has been updated since then in function mentioned as of now above in this known issue as of 47.

### 1) Hard Blocks (global)

| Promotion(s) | Action | Rationale |
| --- | ---: | --- |
| **Amphibious** | **Forbid** | Too situational for AI; often wasted picks. |
| **Sentry**, **Woodsman I–III**, **Medic I–IV**, **Logistics** | **Forbid** (with exceptions below) | These are frequently poor/unreliable on generic AI combat units. See exceptions. |

Exceptions for Sentry / Woodsman / Medic / Logistics

| Condition (Unit) | Action | Rationale |
| --- | ---: | --- |
| UnitCombat = **RECON** *and* UnitAI ∈ { **EXPLORE**, **SPY**, **EXPLORE\_SEA**, **SPY\_SEA**, **PIRATE\_SEA** } | **Allowed** | On scouts/recon & recon-like roles, vision/mobility/woods and field medic uses are actually valuable. |
| Any other unit/role | **Forbid** | Avoids weak picks on frontline attackers/defenders. |

>Note: Medic_Ambulatory is still reachable via your XML alternate prereqs (e.g., through FirstStrike2), so the "no Medic I–IV" rule doesn’t block all medic paths.

### 2) Always Pick First — Strict Offensive (City Attackers)

| UnitAI | Promotion | Action | Rationale |
| --- | --- | ---: | --- |
| **ATTACK\_CITY**, **ATTACK\_CITY\_LEMMING** | **City Raider I** | **Always pick first** (+2000) | Best attack vs cities; highest priority when available. |
| 〃 | **City Raider II** | **Always pick first** (+1000) | Continue the chain as long as legal/available. |
| 〃 | **City Raider III** | **Always pick first** | Finish the CR line for strong siege/assault hitters. |

### 3) Offense Blocks (when UnitAI is Offensive)

Who counts as Offensive?

ATTACK, ATTACK_CITY, ATTACK_CITY_LEMMING, COLLATERAL, PARADROP, and all ATTACK_SEA.
(Hybrids such as COUNTER / CITY_COUNTER are intentionally excluded—see §5.)

| Promotion(s) | Action | Rationale |
| --- | ---: | --- |
| **City Garrison I–III** | **Forbid** | Defensive city bonuses don’t help an attacker. |
| **Hills Master I–III** | **Forbid** | Too map-/situation-dependent; AI tends to overinvest. |
| **Counter Melee / Mounted / Siege / Tank** | **Forbid** | Narrow anti-types are less reliable for general attackers; prefer broadly strong lines (Combat/CR/etc.). |

### 4) Always Pick First — Strict Defensive (City Defenders)

Who counts as Strict Defensive?

CITY_DEFENSE, CITY_SPECIAL
(We exclude RESERVE/RESERVE_SEA here; see §5.)

| Promotion | Action | Rationale |
| --- | ---: | --- |
| **City Garrison I** | **Always pick first** (+2000) | Immediate and reliable city defense power. |
| **City Garrison II** | **Always pick first** (+1000) | Continue CG line for strong static defense. |
| **City Garrison III** | **Always pick first** | Finish the line. |

### 5) Defense Blocks (when UnitAI is Strictly Defensive)

Who counts as Strictly Defensive?

CITY_DEFENSE, CITY_SPECIAL
(RESERVE and RESERVE_SEA are hybrids; do not apply these defense-only forbids to them.)

| Promotion(s) | Action | Rationale |
| --- | ---: | --- |
| **Blitzkrieg**, **Mobility Cost/Range**, **Retreat I–II** | **Forbid** | Mobility/retreat are low value for static city defense. |
| **City Raider I–III** | **Forbid** | Offensive city-attack line; wasted on defenders. |
| **City Bombard Damage** | **Forbid** | "Siege support" promo doesn’t help on defense. |
| **Collateral Damage I–V** | **Forbid** | Collateral triggers on *attack*, not while defending; poor value for static defenders. |
| **Navigator** | **Forbid** | For units that can choose it, being bulky is still more important for defenders. |
| **Counter Archer** | **Forbid** | Narrow anti-archer line is typically inferior to CG/Combat for defense. |

### 6) Hybrid UnitAIs (no forced pushes/blocks)

| UnitAI | Treatment | Rationale |
| --- | --- | --- |
| **RESERVE**, **RESERVE\_SEA** | **No special boost/forbid** (beyond global hard blocks) | They swing between shuffling defense and opportunistic offense; over-constraining can hurt. |
| **COUNTER**, **CITY\_COUNTER** | **No special boost/forbid** (beyond global hard blocks) | Mixed behavior (intercepts near cities but also attacks nearby threats). Let base scoring decide. |

### Results of known issue 47 changes

As can be seen in existing screenshots between 2423 and 2451, AI is now much more effective, or at least significantly more effective at picking promotions: attackers often have city_raider promotion or some other offensive related or compatible in this casepromotions if relevant, defenders more often go for city_garrison which is about best in unitai_city_defense, but some offensive longbowmen go for combat or such which is fine as ai uses the to attack and it's decent still as a defensive promotion if attacked by an enemy before this unit leaves its city.

Versatility is quite preserved as well with a variety or enough of promotions.

Thanks to these, i hope AI is now stronger and i would say saner. I didn't test it too extensively but i hope these samples combined with my past observations about base advciv behaviour of how AI promotes its units

## 48 - (Enhanced/Reworked) AI building walls when they are stronger and don't need it, or wonders when they are weaker or in danger (don't build wonders for our neighbours when they capture us), and overall added a lot of extra buildingValue reject or always build first logic depending on building type or such; and reworked as well the ditching wonders logic to be seemingly stricter and more war/danger focused

Screenshots/files for this issue:

- before the changes: in this [google drive folder link](https://drive.google.com/drive/folders/1rgDB6pYhNGFJHE7jI-4oCe6C32ot2uFe?usp=sharing)
- after the changes: in this [google drive folder link](https://drive.google.com/drive/folders/12lZBr3Y1wkcvlrgWZmzHXVhZCosonIgE?usp=sharing).

So then this is one of the last key/core AI issues i have noticed and had with base advciv, at least those easily or urgently fixable at least to me, about building selection.

I have noticed for example in autoplay AI go for walls while they are at peace time or strong so shouldn't need to defend. This could be used to have 1.5 extra axeman or 1+ longbowman or such urgently needed thing, or a worker or half settler, or other building, anything. Similarly, AIs would a bit too often build wonders, i assume even in cases where they are behind and should focus on defense and consolidating their base rather (be it in economy, workers, science, anything but short or mid term rather), and they'd likely end up building it for their neighbour when they conquer them (could have easily built a castle or such instead), and such other changes. Or, it is useless to build stable if we don't have horse nor camel nor elephants bonus. Culture is not determining factor early especially if we are behind, so invest on 2.5 swordsmen rather than a collosseum, or any more urgent building. Etc for other buildings.

However i didn't go overboard as in too strict on these, as it can be hard to determine if barracks are consistently better as an opener than say a granary or half settler or extra worker or such.

Still, with the changes i made, the difference ingame is quite massive, although not too extreme, but very significant.

What i did was mostly if not onlyto add reject rules on top of existing ones (in `CvCityAI::AI_buildingValue`), so base advciv old code still applies, but only after our prefiltering has operated to skim through most we most likely don't want. In rare cases, we push some buildings as absolute best (e.g. urgently building walls or a castle if behind or declared war on (but not if we are stronger)), effectively overriding base advciv +/- whoever wrote the old code

Results below after this summary.

### Summary by chatgpt 5

Below is the summary of this as of now 1000+ line code in .md tables. I didn't check in detail, but it seems at first glance to be incredibly informative and concise. Check if accurate though, and thanks a lot chatgpt 5 again for the tables and all thanks (chatgpt 5 helped me a big lot to code this as well and review and debug and such, even though i have contributed as well with my prompts and suggestions or such but i really helped lot too thanks):

This summarizes the new **hard gates / nudges** we added inside `CvCityAI::AI_buildingValue(...)`.
It only documents logic that exists in the code we just reviewed (no speculation).

---

#### Common signals & helpers

- **War / pressure flags:** `bAtWar`, `bDanger`, `bWarPlan`, `iEnemyPowerPercent`  
  Derived: `bEnemyStrong := (iEnemyPowerPercent >= 120)`, `bAtWarAndEnemyWeak := (bAtWar && iEnemyPowerPercent <= 80)`
- **Growth signal:** `iEffectiveFood = max(0, iFoodDifference) - max(0, -iHealthLevel);`  
  `if (iHappinessSurplus <= 0) iEffectiveFood = 0`
- **Happiness / health:** `iHappinessSurplus`, `iHealthLevel` (reduced-volatility)
- **Trade reality:** `bForeignTrade` (this city currently has any foreign trade route)
- **Throughput / research:** `iBaseHammersPerTurn`, `iBeakersPerTurn`
- **City costs (this city):** `iMaintenanceTimes100`
- **Empire cost stats (single pass):** `iBestMaint100Global`, `iSecondBestMaint100Global`, `iNumCitiesHighMaintCountGlobal` (gate ≈ **≥ 600** ⇒ **≥ 6 gpt**)
- **Game speed scaling:** `iGameSpeedMultiplier = GameSpeedInfo.getConstructPercent()`
- **"Force-ish" tiebreaker:** `AI_BUILDING_ALWAYS_PICK_FIRST = 999999`
- **Post-build production multiplier detector:** `iTotalHammersModifier = kBuilding.getYieldModifier(YIELD_PRODUCTION) + Σ getBonusYieldModifier(..., YIELD_PRODUCTION)` (Forge/Factory/Ironworks-like; **not** build-time speed)
- **Build-time speed (wonders only, used by timing):** `iProductionModifier = getProductionModifier(eBuilding)`

---

#### Tuning knobs (quick reference)

| Knob | Default | Effect |
| --- | ---: | --- |
| Enemy strong threshold | 120 | When ≥, prefer static defense / skip econ; kill WW. |
| Enemy weak threshold | 80 | When ≤ and at war, allow barracks/stable pushes. |
| Harbor trigger (food) | `iFoodDifference <= 1` | Permissive gate to force Harbor first unless city is in food-as-production mode. |
| Pump gate (hpt) | 8 | Min hammers to justify early unit-pump buildings. |
| Granary "rush" gate | happy≥4 & iEffectiveFood≥4 | Force-first for food-kept buildings. |
| Health "rush" gate | iHealthLevel≤1 & happy≥2 & iEffectiveFood≥2 | Force-first for net health buildings. |
| WW soft turn cap (@ Normal) | 20 | Skip WW if estimated turns exceed cap (speed-scaled). |
| Early "no-mod" WW window | 35 | After this, require ≥25% build-time mods to try WW. |
| Culture early-mid window | 125 | Skip pure culture if borders already workable. |
| High-maint city cutoff | 6 gpt | Maintenance reducers and FP logic use this. |

---

#### Non‑wonder buildings

| Category | Detection (code) | Gates / Actions | Thresholds & scaling | Rationale / Notes |
| --- | --- | --- | --- | --- |
| **Water-food on sea (Harbor)** | `getSeaPlotYieldChange(YIELD_FOOD) > 0` \| \| `getGlobalSeaPlotYieldChange(YIELD_FOOD) > 0` | If `iFoodDifference <= 1` **and** `!isFoodProduction()` → **ALWAYS\_PICK\_FIRST**; otherwise fall through to normal logic | Uses raw surplus; no growth/war checks; only in `!bWonder` | Prevents stagnant/low-food coastal and island cities from stalling on low-value builds; settler/worker mode is exempt |
| **Defensive (Walls/Castle/…​)** | `getDefenseModifier>=25` \| \| `getBombardDefenseModifier>=20` \| \| `RaiseDefense>=15` \| \| `getAllCityDefenseModifier>=10` | If **not at war** → **skip**. If **at war & enemy weak & !danger** → **skip**. If **enemy strong** → **ALWAYS_PICK_FIRST**. | Enemy strong ≥120%; enemy weak ≤80%. | Avoid static defense spam in peace; build urgently only when truly threatened. |
| **Land‑unit pumps (Barracks‑like)** | Land XP ≥2 **or** land prod mod ≥20 | If `iBaseHammersPerTurn < 8` → no special push. If **at war & enemy strong/danger** → **skip**. If **war plan** **or** (**at war & enemy weak**) → **ALWAYS_PICK_FIRST**. | `iPumpGate=8` hpt. | Don’t delay units when weak; do invest when pressing or advantaged. |
| **Stable** | BuildingClass == STABLE | Require **TECH_MOUNTED_COMBAT**. If no **Horse/Camel/Elephants** connected → **skip**. If **enemy strong** → **skip**. If **war plan** or **at war & enemy weak** → **ALWAYS_PICK_FIRST**. | — | Never build without mounts; prioritize when we’ll field mounted. |
| **Naval pumps** | Sea XP/Prod modifiers | If map is **land‑heavy** (`isLandHeavyMap`) → **skip**. | — | Don’t sink hammers into navy on land maps. |
| **City maintenance reducers** | `getMaintenanceModifier >= 25` | If city maintenance **< 6 gpt** → **skip**. If **at war & enemy strong** → **skip**. | `iMaintenanceTimes100 < 600` | ROI gate; avoid long payback during pressure. |
| **Food‑kept (Granary, etc.)** | `iFoodKept >= 25` | If **low happy** (`<=1`) → **skip**. If **at war & enemy strong** → **skip**. If **happy ≥4** **and** `iEffectiveFood ≥4` → **ALWAYS_PICK_FIRST**. | — | Build when growth can be used; don’t store food into a cap. |
| **Health** | `getAdditionalHealthByBuilding(...) > 0` | If **healthy already** (`iHealthLevel ≥2`) **or** `(iHealthLevel ≥0 && iEffectiveFood < 2)` → **skip**. If **at war & enemy strong** → **skip**. Else if `iHealthLevel ≤1 && iHappinessSurplus ≥2 && iEffectiveFood ≥2` → **ALWAYS_PICK_FIRST**. | Uses city‑specific net health gain (future=true). | Urgent when we can grow into it; otherwise punt. |
| **Production multipliers (Forge/Factory‑like)** | `iTotalHammersModifier ≥ 20` | **Early window**: if **low prod (≤12 hpt)** **and** **low growth** (`iFoodDifference ≤1` or no happy) **and** **weak happy gain (≤2)** → **skip**. If **at war & enemy strong** → **skip**. | Early window: first ~100 turns @ Normal (scaled). | Avoid stunting early cities that can’t leverage the multiplier yet. |
| **Happiness** | `getAdditionalHappinessByBuilding(...) > 0` \| \| `isNoUnhappiness()` | If **happy headroom ≥3** and **low food** (`iFoodDifference ≤1`) → **skip**. If **at war & enemy strong** → **skip**. If **at/over cap** (`iHappinessSurplus ≤ 0`) **and** `iEffectiveFood ≥2` → **ALWAYS_PICK_FIRST**. | — | Add happy when it immediately unlocks growth; otherwise hold. |
| **Science** | Research % ≥20 **or** flat beakers **or** (Scientist slots/free) | If **at war** **or** **danger** **or** **war plan** → **skip**. | — | Don’t pause survival or momentum for beakers. |
| **Economy (Gold)** | Gold % ≥20 **or** flat gold **or** (Merchant slots/free) and **not** previously classified | Same war/danger/war‑plan **skip**. If %‑only and city **gold rate < 6** → **skip**. | — | ROI gate for early banks/markets. |
| **Trade‑route econ** | Adds routes **or** has trade route % (incl. foreign) | If war/danger/war‑plan → **skip**. If **foreign %** but **no foreign routes** and **doesn’t add routes** → **skip**. If **tiny base trade** (`iTradeYield ≤3`) then require **+routes**: base 3→ +1, base ≤2→ +2; otherwise **skip**. | Uses current `iTradeYield` in this city; counts "virtual" route when % mods present. | Build CH/Harbor where trade exists or where added routes will matter. |
| **Espionage** | EP % ≥20 **or** flat EP/Spy slots/free **or** EP defense ≥20 | War/danger/war‑plan → **skip**. Difficulty skew: if **human pays much less for tech** (AI advantage, gap ≥ +30) and **EP defense** → **ALWAYS_PICK_FIRST −1000**. If **AI pays much more** (gap ≤ −20) and **EP source** → **ALWAYS_PICK_FIRST −1000**. | Gap: `iHumanResearchPercent − iAIResearchPercent`. | Hedge vs human EP when ahead; lean EP offense when behind on costs. |
| **Culture‑only** | Flat culture **or** culture % (and not classified earlier) | If **BFC not needed** and **early‑mid window** and **existing culture ≥2** → **skip**. | Early‑mid ≈ first ~125 turns @ Normal (scaled). | Don’t overbuild fluff culture once borders are workable. |
| **Unknown / misc** | Anything not matched above | If **war**/**danger**/**enemy strong** **or** **war plan** → **skip**. | — | Conservative default during pressure. |

---

#### Wonder selection — revised gates (top-hammer leeway + common vs. WW/NW)

- **Empire top hammers (single pass):** `iBestHpt`, `iSecondBestHpt`, `iThirdBestHpt`
- **Leeway constants:** `iTopHammerLeeway = 5` (flat wiggle), `iPercentSlack = 30` (relative)
- **Leeway tests:**
  - `bAlternativeEnoughHammerSlack := (iBaseHpt * 100 > iBestHpt * (100 - iPercentSlack))`
  - `bTop2HammerLeeway := (iBaseHpt + iTopHammerLeeway >= iSecondBestHpt) || bAlternativeEnoughHammerSlack`
  - `bTop3HammerLeeway := (iBaseHpt + iTopHammerLeeway >= iThirdBestHpt) || bAlternativeEnoughHammerSlack`
- **Throughput floor:** require `iBaseHpt >= 8` to consider any wonder.
- **Soft turn cap (speed-scaled):**
  - `iTurnsWW = ceil( cost / ( hpt * (1 + buildTimeMods) ) )`
  - Base cap ≈ `20` turns @ Normal, scaled by game speed.
  - Tighten by 10% when construct-percent gap `(HumanWCP − AIWCP) ≥ 20` (i.e., `cap = cap * 0.9`).
- **Post-build production multiplier detector (for "production wonders"):**
  - `iTotalHammersModifier = kBuilding.getYieldModifier(YIELD_PRODUCTION) + Σ getBonusYieldModifier(..., YIELD_PRODUCTION)`
  - Use to flag scaling wonders; when true, also require `bTop2HammerLeeway`.
- **Build-time speed (for timing only):**  
  `iProductionModifier = getProductionModifier(eBuilding)` (stone/marble/traits/religion), used **only** in `iTurnsWW`.

---

#### Shared (applies to World & National wonders)

| Gate | Condition | Action | Notes |
| --- | --- | --- | --- |
| **Throughput floor** | `iBaseHpt < 8` | Skip | Don’t starve cities on wonders. |
| **Time-to-build** | `iTurnsWW > softCap` | Skip | Uses **build-time** modifiers (stone/marble/traits/religion). |
| **NP-style unhealth reducer** | `getUnhealthyPopulationModifier() ≤ −50` | If **war/danger/warplan/enemyStrong** → skip. Else require **pop ≥ 12** and **pop ≥ 2nd-highest (iTopPop2)** and **iHealthLevel < 2**; otherwise skip. | Keeps these for big, unhealthy hubs. |
| **Production-multiplier wonder** | `iTotalHammersModifier ≥ 20` (post-build) | Require **bTop2HammerLeeway** | Concentrates scaling wonders in real hammer hubs. |

---

#### World Wonders (only)

| Gate | Condition | Action | Notes |
| --- | --- | --- | --- |
| **War / pressure** | `bAtWar` \| \| `bDanger` \| \| `bWarPlan` \| \| `bEnemyStrong` | Skip | Don’t throw the game to a race. |
| **Early "no-modifier" window** | After \~**35 turns @ Normal** (speed-scaled) **and** `iProductionModifier < 25` | Skip | Once the early snipe window closes, require ≥25% build-time oomph. |
| **Very-early throughput** | Inside early window **and** `iBaseHpt ≤ 7` | Skip | Not enough production to snipe. |
| **Hammer competitiveness** | **Require `bTop2HammerLeeway`** | Skip if false | Ensures only near-top cities enter races. |
| **Coastal-lean WW** | Sea XP/Prod, coastal routes, or sea plot yield effects present | Require **≥3 coastal cities empire-wide** | Flat empire rule to avoid marginal coastal WWs on land empires. |
| **Race pressure** | `PrereqAndTech` held by **≥3** met teams | Skip | Simple heat check (AND-tech gate). |

---

#### National Wonders (only)

| Subtype | Detection | Gates / Actions | Notes |
| --- | --- | --- | --- |
| **General NW gate** | — | **Require `bTop3HammerLeeway`** | Keeps NWs in top-tier production cities by default. |
| **Military pump (Heroic-Epic-like)** | Land production modifiers | If **enemyStrong/danger** → skip. Else **require `bTop2HammerLeeway`**; and if **warplan** or **(at war & enemy weak)** and **this city ≥ 2nd-best hpt**, return a strong **"pick first"** nudge. | Concentrates pumps in true hammers when pushing. |
| **Land-XP NW** | Land XP modifiers | Same pressure skips and **`bTop2HammerLeeway`**; smaller nudge when pressing. | — |
| **Government Center (Forbidden Palace)** | `isGovernmentCenter()` (non-Palace class) | If **#cities ≤ 6** or **capital** → skip. Else, if **≥3 cities** have **maintenance ≥ 6 gpt**, and **this city’s maint ≥ 2nd-highest**, and **no war pressure**, return a modest **"pick first"** nudge. | Place where it actually cuts costs; avoid capital. |
| **Palace move** | Palace building class | Under pressure → skip. After \~**100 turns @ Normal** and **#cities ≥ 4**, require **both**: this city’s **base hpt ≥ 1.5×** capital **and** **beakers/turn ≥ 1.5×** capital → small **"pick first"** nudge. | The "both" rule prevents oscillation. |
| **Fallback** | — | If **bAtWar/bDanger/bWarPlan/bEnemyStrong** → skip. | Conservative default under pressure. |

---

#### Notes on correctness

- **Post‑build vs build‑time modifiers:** We explicitly separate *yield* multipliers (Forge/Factory) from *build‑time* speed (`getProductionModifier`), so WW timing is computed correctly while regular production buildings are evaluated by their **post‑completion** value.
- **Trade checks are per‑city:** Foreign % bonuses are ignored unless this city actually has foreign routes **or** the building **adds** routes (so it can create the base to multiply).
- **Empire loops:** The single pass that computes top production, top maintenance, and top populations is reused by multiple rules to keep decisions coherent and cheap.

#### Quick pseudocode (flow)

```pseudocode
if (isWonder) {
  if (iBaseHpt < 8) return 0;
  if (iTurnsWW > softCap) return 0;

  // empire stats → iBestHpt, iSecondBestHpt, iThirdBestHpt, etc.
  // leeway: bTop2HammerLeeway / bTop3HammerLeeway

  if (NP-like) { pressure -> skip; pop/health gates -> else let scoring; }

  if (isProductionMultiplierWonder && !bTop2HammerLeeway) return 0;

  if (isWorldWonder) {
    if (pressure) return 0;
    if (!earlyWindow && iProductionModifier < 25) return 0;
    if (earlyWindow && iBaseHpt <= 7) return 0;
    if (!bTop2HammerLeeway) return 0;
    if (coastalLean && coastalCities < 3) return 0;
    if (AND gate tech owned by ≥3 met teams) return 0;
  }
  else { // National Wonder
    if (!bTop3HammerLeeway) return 0;
    if (militaryPump/landXP) { pressure -> skip; require bTop2; maybe nudge; }
    if (ForbiddenPalace) { size/maint gates; maybe nudge; }
    if (PalaceMove) { late+big dual 1.5× test; maybe nudge; }
    if (pressure) return 0;
  }
}
```

### Results of known issue 48

You can see the difference between the 2 runs (48 is the old DLL, before the changes, and 48.2 is the new DLL, after the changes) in the screenshots as mentioned as of now above.

As for the results ingame, the difference is very significant:

- it seems AIs build world wonders much less in particular: at turn 100, only the stonehenge was built, but at turn 150 there seems to be 4 world wonders built (including the apostolic palace by the byzantine empire, quite historically accurate xd although i didn't check this part of history's info/data to know for sure but it's not about a faraway land at least), vs a long list of wonders with old DLL at both turn 100 and 150. This means AI deems it not worth to invest hammers in these, despite being free to as long as our checks are passed (no hard forbidden as in black listed world wonder if i'm not mistaken), maybe this is why there are a few more built by turn 150, but this is quite good, as these can be hammers sink especially early, so their choice makes sense here i would say. Some are built so it's still fine, and even if not fine as such, but that some are still built is cool i would say at least i like it but i prefer that they build much less now as well.
- as for national wonders, almost everyone built heroic epic by turn 100 it seems or something close to it, so they value it veeery highly now, if it is so then all good, again i didn't give a hard obligation but a build it first if you are in danger or plan war or something, in your core cities not low hammer ones, which seems to work well, i didn't check how it was in old DLL but i don't remember anything like this (so much heroic (or national epics here as well it seems) epics so early). All in all i am very satisfied of this change. These also seem to go well with the theme of our AIs now being more self-focused and opportunistic rather than role-play, as they hate they do at least do too much. So i very much like this direction.
- still, the few cities i looked in at a few players, cf screenshots, show very developped infrastructure, all the core buildings are there for most if not all, and it seems walls are being built later as i had intended although i didn't check too much but i saw a player build them later. Should investigate more, but from a quick glance, building profile is preserved in this new DLL for most so great, no hard military spamming, but AI players seem much more competent now, at least quite a bit, in hammer managing, they do seem to have a bit more units but again i didn't look too much. Some players that would be boxed in like Persia AI now properly take the military lead instead of being average (their land start is good but still), so all in all good in this area i would say.
- one change is that they often go for the process "Research" or "Wealth" in their cities, i guess they don't have anything better to build, and too much military may crush their economy so fine as well, no need to change it too much i guess.
- military performance seems a bit better, as i saw less barbarian city captures of the AI cities and more AI capturing barbarians and earlier than usual. I should ideally improve AI players forces spreading so they don't lose their core cities early as this is very crippling and easily for a human avoidable, but this is another issue. For now, it seems they are military more competent and powerful, although again i only glanced, but i see more often military units being produced, at least so it seems from a quick glance again.

Please look at the screenshots i have provided for the old and new DLL for comparison (lacks (most of the) military data but hopefully quite informative otherwise).

All in all i am very satisfied with these changes, AI plays much more like a human, not wasting hammers on wonders unless really worth it, while still keeping a building profile so not overbearing, yet military is a bit stronger, and perhaps effiency as well (i guess workers or settlers are built sooner / cheaper due to no wonder).

This is fine, after all there is no rule saying you have to build all wonders, just like humans skip most especially at higher difficulties, AIs either shouldn't be compelled to go for them. I should now assess how strong they are and later maybe reduce handicap settings if they are too efficient (which is good and great, just i'd need to reduce the handicap settings as i always wanted if they are indeed as i expect/suspect stronger)

Note on performance: our DLL seems quite a bit slower but nothing dramatic, there is some imprecision of say 1-2 seconds due to how i timed it, perhaps even more with the fluctuation and randomness between runs. Still, it seems we are catching up as the number of turns increase. I suspect our checks are a little bit costly early, but later our 1000 line if else if checks are much more efficient than the 2000 line old code, maybe. I could and maybe can refactor it a bit so it looks more like else ifs and such, but moving parameters outside is a bit tedious when we seem to do quite fine, ideally i would but maybe fine as such for now, at least not too bad maybe.

Thanks to chatgpt 5 for the table again hehe thanks:

| Turn | **New DLL (Run 1)** | **Old DLL (Run 2)** |
| ---: | :---: | :---: |
| 50 | 16.2 s | 15.4 s |
| 100 | 45.3 s | 40.5 s |
| 150 | 91.2 s | 87.5 s |

## 48.2 - (Greatly Enhanced and Fixed) Kish city of gilgamesh AI building a theatre instead of a hindu temple despite having unhappy citizens (and health room to grow otherwise), and theatre not giving any reliable happiness (almost anything else would have been much better), fixed by fixed by correcting the happiness building formula in our pre-check in CvCityAI::AI_buildingValue, and in particular replacing the too broad and unreliable CvCity::getAdditionalHappinessByBuilding with our own AI_strictAdditionalHappy

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1xNaTDpRHsdh4YBG176V6pPtnGnbMvL7D?usp=sharing).

This is a nice enhancement to our original pre-checks in `CvCityAI::AI_buildingValue`, as i noticed recently (as of now)that kish city of gilgamesh AI builds a theatre yet is unhappy and would have greatly benefited of a hindu temple instead (theatre unhappiness is not reliable as it is related to culture slider).

The city had enough health room to grow, and was btw nicely surrounded by many grassland tiles, so it was a big mistake to build a theatre here rather than almost anything else.

By digging a bit in our pre-checks, i have found that the logic for identifying happiness buildings is there, but slightly flawed/misleaded/mistaken, as it relied on base advciv +/- civ4's `CvCity::getAdditionalHappinessByBuilding` that was counting many things, as i asked chatgpt 5 about it and told it about this issue and that we don't want to count extravagant as in hard to get or not relevant to early survival happiness modifiers or effects like the culture slider one, useless in the early game and if not going cultural too, but we want to correctly identify immediate happiness buildings. So now with the help of chatgpt 5 i added to use instead for our pre-checksthe new `AI_strictAdditionalHappy` that is limited to most important sources of happiness from buildings (includes bonuses we have, check code there for details and if accurate as is provided by chatgpt 5).

Also, i rectified the `iEffectiveFood` formula into an additional (no pun) as of now `iEffectiveFoodAfterBuiltHappy` variable instead for our as of now happiness buildings pre-check(s)so that we add to our food reserve the food we would gain from making the unhappy citizens happy after our building is built. For example, if our building gives 1 happiness in total (including relevant bonuses and all), we'd gain 2 food in our calculation (as each citizen consumes 2 food if i'm not mistaken, is not strictly accurate as there's no guarantee we have high enough food tiles remaning to work, still anything is better than unhappy citizens so count it as such). As a result, we hopefully no longer mistakenly block our nice pre-check of not building the happiness building if food is low (as food would become naturally higher in most/almost all casesas/after the unhappy citizen works tiles instead or does whatever or not or yes or etc).

As a result of these changes and tweaks, it seems we get very very good results!!!

But first, before the changes (existing screenshots between 275 and 278), starting from turn 100 save file to turn 150, kish city of gilgamesh ai is size 10 with one unhappy citizen, trying to build a theatre, which is useless, and has both hill grassland tiles not worked and not chopped (since pop is capped so this is due to our lazy improve cities code i guess so maybe fine or not too bad).

After the changes (existing screenshots between 279 and 280), we instead build a few real happiness buildings that are seemingly no longer blocked, which are:

- walls (since in our mod as of now walls give +1 happiness if leader is protective which i think gilgamesh is if i'm not mistaken)
- colosseum (a bit inefficient per hammer cost but the happiness helps grow since we have health room)
- market (very good!! Gilgamesh has elephants bonus so it is great to increase happiness and all)

Thanks to these it seems, kish city is now pop 13 instead at turn 150 (resuming from same save file at turn 100)!!! Which is tremendously better, both very nice hill grassland tiles are worked and improved since we have the population to accommodate them(/these?), and interesting thing is kish city switched from 3 scientists ebfore changes at pop 10 to now 3 merchants at pop 13 (the slider is 100% commerce too), so some code written by someone or many people or not xd leverages the market being built and goes for merchants which is more efficient than scientists here since we have no library after our changes but have a market so better use it!! I would have never thought of skipping library to build a market to gain happiness and then switch to merchant economy xd, that's super smart!!! Our production is still good, but city much better, and much better longterm potential even if we have slightly less untis as a result but are still the military leader at turn 150 (would be worth even if we lost quite a bit of power but is fine in such case).

So all in all seems like a very good safe and balanced change that should make AI much stronger especially at middle game and city growing!! But check to be sure.

## 49 - (Enhanced/Addressed) AI having 4+ defenders in capital city but only 1 defender in city B, that gets captured or razed by barbarians then, now almost always if not always new cities go be founded with 2+ defenders

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1t-sHkDPig9ycq_PC7AHMdw1kQ-z3oG--?usp=sharing)

This is one issue i noticed recently but most likely present in base advciv +/- civ4 maybe as well, of having new cities not defended enough, for example having 4+ defenders/units (regardless of unitai or anything) yet only 1 unit in city B, despite capital city being able to pump units fast, and the risk of the new city being destroyed by barbarians early, defeating the purpose.

I don't know too much how the code works, but with the help of chatgpt 5, also making gemini 2.5 pro think on it, they co-thought, most chatgpt 5 in the end, to produce this solution i refined with my prompts and adjustments and testing and suchthanks a lot for help.

The changes are as of now in `CvUnitAI::AI_update`, `CvUnitAI::AI_guardCityMinDefender`, `CvCityAI::AI_minDefenders`.

In particular about the changes in `CvUnitAI::AI_update`, if i understand it correctly and as i asked chatgpt 5 to do and based on screenshots results as well i fed it, regardless of unitai, we ask 2 defenders per new city, instead of often 1. This seems almost always if not always respected now, and it seems there are less barbarian invasions now (see screnshots for details and check if accurate as well).

I expect AI to be significantly stronger thanks to these changes, although there are other areas where it could improve, but not losing as often early cities, despite barbarians being very strong in our mod, is nice to have. Some cities are still lost but better than was, and i couldn't find how to easily increase min defenders to 3, nor would like to risk making capital city too weak.

To see how it was before the changes, you can see existing screenshots between 2585 and 2647, as well as with more details in the example 1 and 2 screenshots. These are only small samples as the issue was really widespread.

After the fix or tentative patch/fix at least, it seems our new cities consistently or at least much more often now properly have 2 defenders, as can be seen in existing screenshots between 2659 and 2660, as well as with more details in all the after change screenshots. If not always, it is extremely more or so it seems at least more applied now. I since then enhanced it by removing the original gating of barbarian turns chatgpt 5 had added in an attempt to make it stricter and i mean more effective.

So all in all, the AI should now be stronger as a result of these changes, but check to be sure and if accurate as again i don't know too much about these.

Note: i added some extra screenshots that show the current state of our AI, militarily it is very strong and impressive, low focus on wonders but not absolute 0, and very very strong scary in a good way army, in the same drive link related to this issue in a drive folder as well.

Update: since all seems to work well or better, added code to disable it after turn 120 adjusted to game speed, so that it is computationally cheaper now that units are really numberousand since barbarians are less of a threat now if at all at this stage, plus cities should be guarded enough to handle this now without needing our code, or in case it creates later issues (maybe we'd lose some unknown fixes with our code but unlikely even though possible), check code comments for details and chatgpt 5 said it's fine as of now at least but check to be sure.

## 50 - (Tremendously improved/fixed/enhanced) Excessive AI worker retreat logic causing worker parking in cities in rare cases: now added a wake from retreat and other changes if any other change

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1IliQAuUug2clSrVHToD6D8cMqOUmxxEM?usp=sharing)

While solving/analyzingknown issue as of now 49, i have noticed Persia AI had 10+ workers parked in city A at turn 200, yet one of the cities was totally unimproved and would badly benefit from using them. Even at turn 210, the workers had moved but only to go to another city instead in retreat mode.

I have asked chatgpt 5 with screenshots and such of the issue (see existing screenshots between 2683 and 2686, as well as the missionai_retreat screenshot for how it was before the fix between turns 200 and 210 if i'm not mistaken).

These indicate the 10+ workers parked in city A have `MISSIONAI_RETREAT` and `HOLD` as also noticed by chatgpt 5 as well when i showed it the screenshot thanks.

The fix(es), as of now in `CvUnitAI::AI_workerMove`, that aim to prevent this excessive retreating now that it has been identified, seem extremely effective and quite minimal; from what i understand this adds a wake up from retreat at the beginning of each worker move call; also we disable/comment-out the old logic that seemingly or was likely to cause excessive panic retreating. Finally towards the end of the function we seemingly add from what i understand or can read of chatgpt 5's code comments xd thanks that we add a safeguard so that we don't retreat in our own cultural borders.

I don't know which of these fixes helped, but the difference is tremedous.

The city of Persia AI, susa city, that was totally unimproved for some reason despite the huge 10+ stack of free/available workers parked in city A or such other city, at turn 200, now at turn 201 has the swarm of workers all or almost all if not all move away and rush to this unimproved city specifically, very very nice, as can be seen in the way workers moved turn 201 very nice screenshot, as well as and for next turns as well2633 and screenshot 2687 too. This very heavily contrasts with (before the changes) the city still being unimproved at turn 210 almost and workers just having for most moved to go be parked in another city.

The one worker per tile is very nice, and we seem to get our ideal improvements.

This was started from a save file that had the issue, i assume that with this new change now in the DLL, the issue won't happen hopefully and this susa citywould have been improved already much much sooner. This was quite rare as i hadn't noticed it from quick autoplay glances, but great and a very nice enhancement i believe. Thanks to this, i believe AI is also significantly stronger and more efficient with its workers, and thanks again chatgpt 5 for help as well although i participated as well in the thinking effort and providing code and such as you did.

## 51 - (Worked around / fixed) Massive seemingly base advciv +/- civ4 issue of many cities entering no production early for 1 or several turns many times during the game early (and possibly later this is why many cities have a process rather than no production, as processes are not available early and are listed among fallbacks if production fails it seems but check to be sure)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1trFS19b14RsYA6kHc8RT6zFyc36KqILw?usp=sharing)

This is an issue i had noticed in advciv, in example 69.3 of the list issues (i had named it example 69.3 when i was still playing base advciv here in [this CFC forum post](https://forums.civfanatics.com/threads/ai-city-placement-and-misc-suggestions.695343/page-7#post-16782814) i had made at that time, also available in this google drive's issue), but it happened only once at least i noticed it only once, but it did seem to affect several cities in the screenshot, but since it was the turn after victory i didn't think too much of it and said it's maybe not too urgent, although not ideal, but documented it still if helps.

But while solving/addressing known issue as of now 49, i have noticed this again, but now in early cities, and several cities, entering what seems like no production at all for 1 or several turns. For example, in screenshots 2633 (2) and 2634, kyoto has no production, when anything could be best since it is free to produce units if nothing else is good, else the hammer is wasted.

In screenshot 2706, it can be seen the issue is happening in many cities. Also in screenshot 2694, the issue also is happening in ulundi ai city, so it looks quite widespread but not obvious if one is not looking carefully at each turn in cities, as it often only happens for 1 turn, but not always. It also doesn't happen just these turns or runs but would be long to document all, pehraps uneeded, what matters is the issue happens, and often enough to be an issue, where moscow ai and native american ai's cities are also in no production (no entry emoji/button as chatgpt 5 calls it hehe), not only japan ai's city.

But japan ai's no production happened for many turns, something like +/- 5 turns on a row, so i thought it would be a nice place to investigate and try to improve it, as usual with chatgpt 5's help thanks and trial and error xd or other ai if needed or i want to try them xd or such.

I have also noticed the issue more recently as can be seen in existing screenshots between 2920 and 2925 almost all if not all in same turn (turns 200 to 201 with lisbon ai), by pressing print screen super fast while in autoplay, i could see the city being in no produciton, the order for a much needed camel cuirassier being issued (especially since we are much weaker militarily here than other AI players), and then the order getting seemingly popped or whatever the word is for cancelling this order all in the same turn it seems from screenshots as well. Hopefully this is a good start point to implement a better fix, as we are in this map weaker and would have much needed the extra camel cuirassier, and at turn 201 as a result still no produciton as well so we can hopefully fix all that maybe. (Note: about this fast screenshot trick i just discovered xd and somehow got the idea to do/try, i added it in [Modding_Ressources/README.md#trick-to-capture-fast-actions-in-same-turn-press-print-screen-super-fast-many-times-if-you-dont-want-to-bother-recording-a-video](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README.md#trick-to-capture-fast-actions-in-same-turn-press-print-screen-super-fast-many-times-if-you-dont-want-to-bother-recording-a-video) for future reference as well if needed)) (Note 2: the deer not being improved is before i fixed the bug of forest not being chopped on camp bonuses like deer elephants and such, now properly chops and improves there)

So to fix this, using various AIs but ultimately chatgpt 5, i have found the best way so far i could find so far, and that is seemingly very effective and reliable, is to add a unit fallback logic outside of and after `CvCity::doProduction`, in `CvCity::doTurn`.

We build if it would otherwise be a no production, the most expensive unit (if less than 50 hammer per era + 1 (e.g 50 hammer at era_ancient, 100 hammer at era_classical, etc. (to avoid crazy high unit costs that would doom us in xml))) as a fallback for military cost (gold per turn) efficiency, less units to upgrade as well for the AI and overall military strength (we assume to simplify most expensive units are stronger and get upgraded later to simplify) if there are any other advantages perhaps or not disadvantages but seems much better than spamming a bunch of fallback ancient macemen then going bankrupt sooner with overall weaker army (or same issue later in game perhaps maybe).

The results are extremely good it seems!!!

- in existing screenshots between 2996 and 2998, lisbon ai has one extra turn of no production, then it is solved. Hard to tell if this is just delay of one turn lag or such since we started from a save file that already had it, but we don't have it anymore the turn after (may have been so before but is not worse)
- most importantly, in existing screenshots between 2999 and 3006, in turns between 37 and 44 as before and even much after, japan ai never enters at all the no production anymore. Even more importantly, no other AI city at all does as other ai cities had the issue such as ulundi ai or moscow ai, i zoomed out as much as possible, and didn't see any at all if i saw correctly, so this is tremendously better. Also, we still bounce back to a settler a few turns later in japan ai city, and all cities don't get trapped in an archer or such fallback either, they produce settlers, workers, perhaps buildings maybe although i didn't check too much. So all in all it seems so much better than it was, and quite clean and effective.

I still don't know why the no production happened/happens, but it seems we now cleanly and reliably always override it with a fallback, and if not almost always. Thanks to the improvement in AI efficiency, i have adjusted down a bit handicap (as of now only `iAITrainPercent` relative to how they were in advciv-sas which is not exactly like in base advciv, but tries to be gradually harder) costs to match this change.

Update: added siege units to excluded fallback units as they are not versatile enough, see [53.3 (Tremendously Improved) AI overbuilding siege units, in particular trebuchets but not only, where they are detrimental to do build, in particular when weaker but not only](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#533-tremendously-improved-ai-overbuilding-siege-units-in-particular-trebuchets-but-not-only-where-they-are-detrimental-to-do-build-in-particular-when-weaker-but-not-only) for related info

Update 2: updated since then to prefer civ-specific units and other tweaks if any, see [53.2.2 (Seemingly greatly enhanced) AI overproducing defenders early on, especially longbowmen but not only, replaced with an early produce more versatile units especially civ-specific ones when defended enough (at least in theory) in CvCityAI::AI_chooseUnit](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#5322-seemingly-greatly-enhanced-ai-overproducing-defenders-early-on-especially-longbowmen-but-not-only-replaced-with-an-early-produce-more-versatile-units-especially-civ-specific-ones-when-defended-enough-at-least-in-theory-in-cvcityaiai_chooseunit) for details

Update 3: added offense only and defense only alternate logic (fallback to overall units if none available) as i have found/guessed this is where most excess longbowmen came from as they would bypass restrictions in `CvCityAI::AI_chooseUnit`, tunable in [GlobalDefines_advciv_sas.xml](/Assets/XML/GlobalDefines_advciv_sas.xml).

## 52 - (Beyond Tremendously improved) Remove AI scrapping of military land units, as way too many units are scrapped early, yet we really need them to defend against barbarians or our rivals or such

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1JHA0QsVUyBiKy_BDFgXFb-wYG_t-EcUc?usp=sharing)

So this is another major AI improvement of a major issue we had in base advciv +/- civ4: for example japan AI would between turns 37 and 44, scrap 2 of its newly produced ancient macemen (update: now archers) (now added as a patch to the no produciton at all during that time in [51 - (Worked around / fixed) Massive seemingly base advciv +/- civ4 issue of many cities entering no production early for 1 or several turns many times during the game early (and possibly later this is why many cities have a process rather than no production, as processes are not available early and are listed among fallbacks if production fails it seems but check to be sure)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#51---worked-around--fixed-massive-seemingly-base-advciv---civ4-issue-if-im-not-mistaken-of-many-cities-entering-no-production-early-for-1-or-several-turns-many-times-during-the-game-early-and-possibly-later-this-is-why-many-cities-have-a-process-rather-than-no-production-as-processes-are-not-available-early-and-are-listed-among-fallbacks-if-production-fails-it-seems-but-check-to-be-sure)).

As a result, it was weaker, and this likely contributed to barbarians successfully invading it and japan ai having a bad game.

As can be seen in existing screenshots between 2742 and 2753, our ancient maceman count goes down as soon as we produce a unit, and our units are not attacked either, so this means we scrap them. I tried doing changes in `CvPlayerAI::AI_doMilitary` or other related function(s) but it was ineffective nor unfortunately helping to solve this at all. The screenhots mentioned just before were actually before these, and still same issue if not worse nor slightly better, still about the same it seems.

So chatgpt 5 then got the brilliant idea to add our logic in `CvUnit::canScrap`, or as i called it xd, "scrap the scrapping", or was it "scrapping the scrap" as it called it i think if i'm not mistkane but regardless, this is where we added our code, and effect was immediate, as can be seen in existing screenshots between 2757 and 2764. We don't scrap anymore. I tried to check economy by autoplaying longer, and we don't go bankrupt (at emperor difficulty with quite reasonable penalties, but that i'll reduce a bit as well now that AIs are more competent/efficient), and our military seems quite a bit stronger although i barely glanced, and can only assume this is due to having more units throughout the game.

I refined the logic by telling it to as of now never scrap valuable military land units, and also as a general rule to never scrap before turn 150 for any unit at all regardless of its unitai or such. (So including workers, triremes, etc.) Hopefully this helps AI not waste hammer destroying and rebuilding units non stop.

As can be seen in these screenshots after the change as well, japan ai now has a proper midgame, and doesn't die nor is badly weakened by barbarians taking its city(ies). I believe AI is stronger as such, and no extra change is needed, except reducing starting defenders and reducing handicap a bit to accommodate, after all no risk to overproduce if we have more even terms than the human, and the excess land military units are always useful.

The results of before/after change are resumed by chatgpt 5's own analysis of each screenshot, but check if accurate as well if needed

>Before (pre-canScrap change)

| Turn | Year | Workers | Scout | Archers | Ancient Macemen |
| ---: | :--- | ---: | ---: | ---: | ---: |
| 37 | 4750 BC | 2 | 1 | 3 | 6 |
| 38 | 4500 BC | 2 | 1 | 4 | 6 |
| 39 | 4375 BC | 2 | 1 | 4 | 5 |
| 40 | 4250 BC | 2 | 1 | 4 | 6 |
| 41 | 4125 BC | 2 | 1 | 4 | 5 |
| 42 | 4000 BC | 2 | 1 | 4 | 6 |
| 43 | 3875 BC | 2 | 1 | 4 | 5 |
| 44 | 3750 BC | 2 | 1 | 4 | 5 |

>Pattern: macemen oscillate 6 ↔ 5, dropping right after a completion.
>
>After (post-canScrap change)

| Turn | Year | Workers | Scout | Archers | Ancient Macemen |
| ---: | :--- | ---: | ---: | ---: | ---: |
| 37 | 4750 BC | 2 | 1 | 3 | 6 |
| 38 | 4500 BC | 2 | 1 | 4 | 6 |
| 39 | 4375 BC | 2 | 1 | 4 | 6 |
| 40 | 4250 BC | 2 | 1 | 4 | 7 |
| 41 | 4125 BC | 2 | 1 | 4 | 7 |
| 42 | 4000 BC | 2 | 1 | 4 | 8 |
| 43 | 3875 BC | 2 | 1 | 4 | 8 |
| 44 | 3750 BC | 2 | 1 | 4 | 8 |

>Pattern: steady growth 6 → 8, no post-build drop.
>
>Quick take
>
>The before sequence shows automated disband right after a unit finishes (classic "produce one, delete one").
>
>The after sequence confirms the source fix (blocking scrap for the relevant units) works: counts only go up when production finishes, and never down on the following turn — even with small negative GPT.

One issue i have noticed, not related to this change, but linked to [23 - (Seemingly now fixed) Major bug of AI cities being stuck in a loop of producing a workboat and instantly scrapping it](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#23---seemingly-now-fixed-major-bug-of-ai-cities-being-stuck-in-a-loop-of-producing-a-workboat-and-instantly-scrapping-it-so-without-producing-a-new-unit-if-im-not-mistaken-then-producing-a-new-one-endlessly-for-dozen-turns-until-it-somehow-solved-itself-but-way-too-late) indirectly, is AI in some rare cases, despite our tentative changes in other known issues, overproduces galleons and privateers (like 20+ mixed galleons privateers which is insane when most rivals stick to +/- 5 which is much more reasonable), and dies as a result (short-circuit(s) somewhere or is our logic to prevent this other issue ineffective somehow despite showing good results on unitai land types?), at turns 200-220, this would be our next issue to investigate ideally if we do.

For now, since all seems to work great, i'll simply adjust handicap and no other economy change, hopefully AI is stronger thanks to these and games can be more even, less of a grind, as we had envisioned while / as was one of the goals i had / issues i had noticed when i had started making this mod.

## 53 - (Beyond Tremendously Improved) Naval dementia of producing privateers/galleons then seemingly scrapping them and repeat, or of more importantly building galleons and privateers in droves and excess, despite enemy threatening cities of land capture for 20+ turns, and losing capital as a result: fixed/addressed by now managing production of each unitai with max by type in CvCityAI::AI_chooseUnit, as well as disallowing scrapping and managing it by unitai type globally as well in CvUnit::canScrap by type as well with max and such other conditions for some units like as of now workers

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1vHCLdFvm9cQpE_7rXnRL3X9zOQDxTAgH?usp=sharing)

This is also a major AI improvement/refinement, it expands on previous known issue as of now 52 approach, as while solving said known issue, i had noticed Khmer AI's naval cities were producing privateers and galleons like crazy around turn 200, despite most AIs doing fine and only having few such units.

As a result, it got invaded 20 turns later with poor land military and lost its capital, and essentially lost. But this could have been easily avoided or at least much better, if decision was made sooner to build land units instead of naval, quite useless on pangea further more, especially past a certain threshold.

We had handled or attempted to handle this issue in [35 - (Attemptingly fixed/addressed) AI building too many military naval units then gets invaded on land](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#35---attemptingly-fixed-or-addressed-ai-building-too-many-military-naval-units-then-gets-invaded-on-land-and-cant-defend-10-galleons-and-barely-any-land-defender--do-not-prioritize-water-military-units-if-city-is-landlocked-i-assume-it-means-stuck-in-a-lake-or-something-if-i-am-not-mistaken-but), but i guess the approach was conservative, or maybe rather didn't cover the many short-circuits to our logic or such (maybe, this is a guess, check if accurate).

It also seemed although i didn't check too much that some of those privateers disappeared, like the infinite loop issue in [23 - (Seemingly now fixed) Major bug of AI cities being stuck in a loop of producing a workboat and instantly scrapping it](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#23---seemingly-now-fixed-major-bug-of-ai-cities-being-stuck-in-a-loop-of-producing-a-workboat-and-instantly-scrapping-it-so-without-producing-a-new-unit-if-im-not-mistaken-then-producing-a-new-one-endlessly-for-dozen-turns-until-it-somehow-solved-itself-but-way-too-late). Still who knows if this or maybe other such loop issues silently didn't happen. At this point i didn't and don't trust the code anymore, let's implement global or such sanity guards! hehe. And chatgpt 5 helped me a lot thanks too, including for part of the documentation of this issue below as well.

So just like in known issue as of now 52, we generalized the production control and overproduction management by putting our prechecks at the source, which seems to be `CvCityAI::AI_chooseUnit`. I did some refactoring as well with the help of chatgpt 5so the overloaded function now calls the 2nd overloaded one since they ultimately perform the same task duplicated, and so we can control it all so nice xd in one place.

On top of that, i matched these new rules per unitAI asymmetrically in `CvUnit::canScrap` as well, with now a more general approach covering more unitais than before or differently. The main/generalidea is quite simple: make sure we don't overproduce using max units for most unitais, then when it comes to scrapping, generally don't scrap most of these unitais (plus some extra nice sanity checks like don't scrap icbm, or great person units (who knows if they do somehow), etc.) and assume we have produced just enough anyway.

I didn't implement any economy check, but it seems we don't go bankrupt at least for now, even if we did, if we are in danger or weak, it's better to do this last ditch effort than say build a wonder xd, which we also prevent in other known issue(s) hehe so AI is really strong now at least much more than in base advciv, and despite plenty of things to improve too ideally but still very nice progress.

So what this changes in short is:

- prevent naval overproduction and such: don't overproduce naval units when in danger or such and even if not add some sanity max quotas or limits per unitai (prevents overproducing naval units from any short circuit code as we block the order itself now (unless some other unknown code emits orders, else we should now handle most if not all)): helps react better to threat and map type and produce optimal unitais (with some flexibility is not too strict but quite guided for the AIs's sake and for efficiency of the AI)
- prevent naval dementia: don't go like: "oh i need one more unit, let's produce it". (Production completes...) "Oh i have one too many unit, let's scrap 1 or 2 just because xd no one will notice it" (i mean yes but it's horrible and hurts AI strength and aesthetic too), then AI is like "oh, i need one more unit, let's produce it" (ofc you do, you just scrapped it xd). This was the issue with workboats, possibly with privateers, maybe with other units. At this point i don't trust the code anymore xd, not sure that i did though but now i definitely don't, although it works not too bad otherwise, so i implemented global sanity checks for almost all unitAIs if not all then almost.

Results are tremendously positive, i started from a very desperate save at turn 200, 20 turns more or less before capital fell with the naval dementia or overproduction issue.

In first run, before the changes, as can be seen painfully in existing screenshots between 2787 and 2800, we (i.e. Khmer AI) have 12 galleons, 5 privateers and 13 frigates, in a pangea!! At turn 205 too, while, other rivals are much reasonable, in the single digits, sometimes even single hand digits... Yet we feel compelled to produce more naval units, which is definitely already useless on pangea and on top of it considering our composition. We then die and lose our capital 20 turns later more or less pathetically or tragically, what use were the boats for. Again, this issue was existing in base advciv, but i thought we had prevented it enough in known issue 35, but i guess our logic is overriden in many places xd or short circuited, this new logic we added explained below should be much more effective! But check to be sure.

As for after our changes, the difference is massive. Despite save file being already desperate and AI starting at turn 200 so already doomed with such wasted hammers, it quickly redirects, and produces the next turn and so on various land units or does processes like Research or Wealth that are not nonsensical, much better use of our hammers. Not a single extra naval unit built, very nice. This can be seen in existing screenshots between 2827 and 2850. We squeezed easily 10+ if not more although i didn't count so maybe bit less, various land units in these 20 turns, which range from pikemen, cannons, camel knights, nice. In the end it was not enough to save the already desperate situation, but we give a much better (and saner too!) fight. I suspect if we start sooner before the mistake is made, perhaps at turns 100-150 and metaphorically undo these naval units being produced by going back, surely the outcome would have been different, possibly Khmer AI would not have died, its position was actually quite good, and with a size 21 capital city at turn 200-220, it could have certainly done better in retrospect.

So i am very happy and satisfied of these changes, now below the detail by chatgpt 5, check if accurate as always, but i hope these are very informative, we'll go over changes, as of now, in `CvUnit::canScrap` and `CvCityAI::AI_chooseUnit`. Unlikely i'll update them so remember they are general info if not updated (i could but not guaranteed, i may or may not do so). Also about below chatgpt 5 explanation that helps very nicely thanks a lot chatgpt 5, i have formatted it a bit as well but otherwise didn't check much if at all, check if accurate.

Note: i went beyond fixing the issue at hand and added some nice extra sanity cheks like icbm or worker max count per era and such as shown below, i hope AI is a lot more competitive, possibly silent issues like unknown scrapping or loops are solved by now, check for economic bankruptcy as i didn't guard against it assuming AI is rich enough or threatened enough to make it compensate its excess or handicap lowered enough so it can't overproduce so easily which is a win for us at least me xd if not some other players or not or etc.

### canScrap() — AI scrapping policy

>Scope: applies only to AI units (if (!isHuman()) …).
>Baseline guard retained: never scrap while the unit’s plot is fighting.

#### 1) Unit categories and the scrapping decision

| Category | Identification (by UnitAI / traits) | canScrap() result |
| --- | --- | --- |
| **Land combat** | `ATTACK`, `ATTACK_CITY`, `ATTACK_CITY_LEMMING`, `COUNTER`, `CITY_COUNTER`, `CITY_DEFENSE`, `CITY_SPECIAL`, `RESERVE`, `PARADROP` | **Never scrap** |
| **Land combat (fallback)** | `DOMAIN_LAND && canFight()` (safety net for modmods) | **Never scrap** |
| **Naval – frontline** | `ATTACK_SEA`, `RESERVE_SEA`, `PIRATE_SEA` | **Never scrap** |
| **Naval – explore / support** | `EXPLORE_SEA`, `ASSAULT_SEA`, `ESCORT_SEA` | **Never scrap** |
| **Naval – air platforms** | `CARRIER_SEA`, `MISSILE_CARRIER_SEA` | **Never scrap** |
| **Naval – civilians** | `SETTLER_SEA`, `WORKER_SEA`, `MISSIONARY_SEA`, `SPY_SEA` | **Never scrap** |
| **Land civilians (most)** | `EXPLORE`, `SETTLE`, `MISSIONARY`, `SPY` | **Never scrap** |
| **Workers (land)** | `WORKER` | **Conditional** (see §2) |
| **Air combat** | `ATTACK_AIR`, `DEFENSE_AIR` | **Never scrap** |
| **Great People** | `GREAT_PROPHET`, `GREAT_ARTIST`, `GREAT_SCIENTIST`, `GREAT_GENERAL`, `GREAT_MERCHANT`, `GREAT_ENGINEER`, `GREAT_SPY` | **Never scrap** |
| **Missiles** | `ICBM`, `MISSILE_AIR` | **Never scrap** |
| **Any unit with cargo** | `getCargo() > 0` | **Never scrap** |

#### 2) Worker scrapping logic (the only conditional case)

Goal: let the AI thin surplus workers after the empire is mature, without ping-ponging.

When: only from Renaissance onward. Earlier eras never scrap workers.

Cap formula

`base = 2.5 * cities = (2 * N) + ((N * 5) / 10)` (integer math)

Linear era decay starting at Renaissance (era index = 3):
`erasSinceRen = max(0, (currentEra - 3) + 1)`
`pct = max(60, 100 - 10 * erasSinceRen)` → never below 60% of base
`cap = max( minWorkers, (base * pct) / 100 )`

`minWorkers = 3 + ((N * 3) / 10)` (keeps a small backbone)

Scrap condition

Only allow scrapping if totalWorkers **>** cap.
(Using strict > avoids disbanding when we’re exactly on target.)

Sample caps (integer arithmetic)

| Cities (N) | Base (2.5N) | MinWorkers | Renaissance (90%) | Industrial (80%) | Modern (70%) | Future (60% floor) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 5 | 3 | 4 | 4 | 4 | 3 |
| 4 | 10 | 4 | 9 | 8 | 7 | 6 |
| 6 | 15 | 4 | 13 | 12 | 10 | 9 |
| 8 | 20 | 5 | 18 | 16 | 14 | 12 |

#### 3) Global time gate

| Guard | Value |
| --- | --- |
| **No disbanding phase** | Before turn **150 @ Normal speed**, scaled by game speed: `150 * TrainPercent / 100` |

#### 4) Design notes / asymmetry with production

- Asymmetric by design: we limit production in AI_chooseUnit() (e.g., naval caps by map + danger), but we don’t scrap those categories later. This prevents "produce → scrap" loops and keeps hammers focused.
- Workers are the single category where we both cap production (early generous, later tighter) and allow pruning post-Renaissance when over the target.
- Safety rails: never scrap cargo carriers, GP, missiles, air combat, or land combat. Early global "no disband" phase protects the crucial development window.

#### 5) Tuning dials (all hardcoded for simplicity)

| Constant | Current | Effect |
| --- | ---: | --- |
| `iNoDisbandAtAllTurnsNormal` | **150** | Length of early "no disband" window (scaled by speed). |
| Worker decay start era | **Renaissance (3)** | Bring forward/back to change when pruning can begin. |
| Worker decay per era | **10%** | Linearly reduces target from Ren; floor at 60%. |
| Worker floor | **60% of base** | Ensures we always retain a useful workforce. |
| `minWorkers` slope | **3 + 0.3N** | Keeps small empires functional and large empires from hitting zero. |

#### 6) Quick pseudo-flow (for readers)

```pseudocode
if human → default behavior
if plot is fighting → never scrap
if AI:
  if LandCombatAI || (DOMAIN_LAND && canFight) → never scrap
  if Naval any AI → never scrap
  if Land civ (explore/settle/missionary/spy) → never scrap
  if Air combat → never scrap
  if Great Person || Missile → never scrap
  if has cargo → never scrap
  if turn < scaled(150) → never scrap
  if Worker:
     if era < Renaissance → never scrap
     compute cap (2.5N with linear 10%/era decay, floor 60%, min backbone)
     if totalWorkers > cap → allow scrapping (else refuse)
return true otherwise
```

### AI_chooseUnit() — production gates

>Entry point: the (UnitAITypes, iOdds) overload now funnels to the
>(UnitTypes, UnitAITypes) overload, so all gating lives in one place.
>The "best unit" picker remains the same; only the final "should we actually queue it?" logic is centralized.

#### 0) Situation + map read (used throughout)

bAtWar, `bWarPlan = AI_isFocusWar()`, `bDanger = AI_isDanger()`

Enemy pressure: bEnemyStrong if AI_getEnemyPowerPercent(true) ≥ 120

Map flavor from script name: LandHeavy vs NavalHeavy

Scale by empire size: `N = getNumCities()`

Caps compare empire-wide counts using AI_totalUnitAIs(...), which includes units in production (prevents over-queuing in parallel)

#### 1) Naval unit AIs

| Group | AIs | Base cap | Map tweak | Threat tweak | Notes | | | | | | |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Frontline** | `ATTACK_SEA, RESERVE_SEA, PIRATE_SEA` | `N` | `2N` on NavalHeavy | Halve (min 1) if bAtWar | | bEnemyStrong | | bDanger | | bWarPlan | Prevents late naval bloat on Pangaea |
| **Explore** | `EXPLORE_SEA` | `1 + ⌊0.3N⌋` | `2 + ⌊0.3N⌋` on NavalHeavy | Halve (min 1) if any threat | Keep a small scout fleet only | | | | | | |
| **Assault (offense)** | `ASSAULT_SEA` | `N` | `2N` on NavalHeavy | **Block** if bEnemyStrong | | bDanger | | bWarPlan | Don’t plan invasions under pressure | | |
| **Escort (defense)** | `ESCORT_SEA` | `N` | `2N` on NavalHeavy | Reduce to **60%** (min 1) if any threat | Keeps some cover, but trims excess | | | | | | |
| **Air platforms** | `CARRIER_SEA, MISSILE_CARRIER_SEA` | `N` | `2N` on NavalHeavy | Reduce to **60%** (min 1) if any threat | | | | | | | |
| **Settler ships** | `SETTLER_SEA` | `1 + ⌊0.3N⌋` | `2 + ⌊0.3N⌋` on NavalHeavy | If threat: **block** on land-heavy maps; allow **1** on NavalHeavy | Avoid risky expansion during danger | | | | | | |
| **Workboats** | `WORKER_SEA` | `N` (≤ Renaissance) | `2N` on NavalHeavy | — | After Renaissance: `1 + ⌊0.3N⌋` (or `2 + ⌊0.3N⌋` NavalHeavy) | | | | | | |
| **Missionary ships** | `MISSIONARY_SEA` | `N` (≤ Renaissance) | `2N` on NavalHeavy | **Block** if any threat | After Ren: `1 + ⌊0.3N⌋` (or `2 + ⌊0.3N⌋`) | | | | | | |
| **Spy ships** | `SPY_SEA` | `N` | `⌊1.5N⌋` on NavalHeavy | **Block** if bAtWar | | bEnemyStrong | | bDanger. If `bWarPlan` and **not** NavalHeavy: **block** | Naval recon is only for naval maps / calm times | | |

>Build is refused if AI_totalUnitAIs(...) ≥ cap for that group.

#### 2) Land civilian AIs

| Group | AIs | Cap | Threat tweak | Notes | | | | |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| **Explorers** | `EXPLORE` | `2` (or `1` on NavalHeavy) | **Block** if any threat | | | | | |
| **Settlers** | `SETTLE` | `1` | **Block** if any threat | "One at a time" rule | | | | |
| **Workers** | `WORKER` | see below | Slightly lenient: **block only** when `bAtWar && bEnemyStrong` | Era-scaled cap (next table) | | | | |
| **Missionaries** | `MISSIONARY` | `N` (≤ Renaissance), else `2` | **Block** if any threat | | | | | |
| **Spies** | `SPY` | `N` (or `⌊1.5N⌋` on NavalHeavy) | **Block** if bAtWar | | bEnemyStrong | | bDanger; if `bWarPlan && !NavalHeavy` → **block** | Don’t stall land wars with spy spam |

Worker production cap (matches scrapping doc):

- Base: `2.5 * N = (2 * N) + ((N * 5) / 10)`
- From Renaissance (era=3) onward, apply linear decay per era:
- - `erasSinceRen = max(0, (currentEra - 3) + 1)`
- - `pct = max(60, 100 - 10 * erasSinceRen)` → floor at 60%
- - `cap = max( minWorkers, (base * pct) / 100 )`
- `minWorkers = 3 + ⌊0.3N⌋`
- Refuse build when `totalWorkers ≥ cap`.

#### 3) Air combat (empire cap)

| Group | AIs | Cap | Threat tweak |
| --- | --- | ---: | --- |
| **Fighters + Bombers (combined)** | `ATTACK_AIR, DEFENSE_AIR` | `3 * N` | None |

#### 4) Unhandled AIs

Everything not listed above (e.g., land military) is free to build here; pruning and protection are managed on the scrapping side (which, by policy, never scraps land combat anyway).

#### 5) Asymmetry with canScrap()

- Naval + most civilians: Production is capped up front; scrapping is disabled later → no "produce→scrap→produce" loops.
- Workers: Capped in production and may be trimmed later only if above the same target (post-Renaissance).
- Land combat & air combat: Production allowed (no cap here for land); never scrapped later.

#### 6) Tuning dials

| Constant / Rule | Current |
| --- | --- |
| Naval frontline base cap | `N` (or `2N` on NavalHeavy) |
| Threat halving / 60% trims | Halve or 60% as listed above (min 1) |
| Explorer caps | Land: 2 (1 on NavalHeavy). Sea: `1 + 0.3N` (2 + 0.3N on NavalHeavy) |
| Settler caps | Land: 1. Sea: `1 + 0.3N` (2 + 0.3N on NavalHeavy), but block under threat except allow 1 on NavalHeavy |
| Worker base + decay | Base `2.5N`; -10%/era from Renaissance; floor 60%; min `3 + 0.3N` |
| Air (fighters+bombers) | `3N` combined |

#### 7) Mini flow (for readers)

```pseudocode
if eUnit == NO_UNIT → fail
read map flavor, situation flags, N = num cities
if Naval AI:
   compute cap per table (+map, +threat tweaks)
   if total >= cap → refuse
   else allow
else if Land civilians:
   apply per-group rules (incl. worker era decay)
   if total >= cap (or threat says block) → refuse
else if Air combat:
   if total fighters+bombers >= 3N → refuse
else:
   allow (land military, etc.)
pushOrder(ORDER_TRAIN, eUnit, eUnitAI)
return true
```

Update: since then reverted naval unit production control in naval heavy maps (archipelago etc.) as we had way too few of them, which seems to give much better results (didn't update this doc)

## 53.2 - (Fixed and enhanced) Joao AI building way too many defenders (36 longbowmen at turn 130!! Almost all with UNITAI_CITY_DEFENSE or similar) while being boxed in with only 3 cities, instead of making about half of these offense units or versatile ones to punish overextending thin neighbour, fixed by having an early phase "we have expectedly too few cities at this stage of the game, no need to overbuild anymore denders at this stage of the game, switch to offense or versatile UNITAI rather" and "our military composition has way too many defender UNITAIs, switch to offense or versatile UNITAIs", which seemingly fix the issue

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1SXj_Q_DcmsBsvB0vbajclZUFMYxSBv05?usp=sharing).

This is also a nice issue to have enhanced and fixed, i have noticed that sometimes we produce way too many defenders, in particular longbowmen, but i don't know if it's because of our efficiency enhancements (humble bragging or not humble xd bragging) but sometimes it's very, perhaps too and way too much xd.

For example, i have noticed in a map autoplay at at turn 130 joao AI had 36 longbowmen.. yet only 3 cities. Almost all of them are city_defense too. This is way too overkill and inefficient to guard so few cities. Meanwhile, inca ai neighbour of joao ai is overextending and has like 8+ cities (i didn't count but more or less this number) and is very thin, but left unpunished and grows stronger, while the 3 city joao ai collapses. This could have been done much better, and had joao ai more versatile unitais for its excess units (we still need to ensure cities are guarded enough, so best target is low city players at X stage of the game, as they are likely to have too much units per city, many of which don't need to be defenders and could be roaming instead to capitalize and expand and perhaps indirectly counter (no pun) the being boxed in or whatever resulted in few cities early that would be detrimental later on). Note: joao ai is not the only one with the issue in this game, justinian ai also has more or less 20 longbowmen which is most of his units but he has like 5 cities at a glance at turn 130 so fine to defend them as such, still maybe it is a bit too much but fine to protect them as such maybe.

To fix this, i added rules (pre-check) in `CvCityAI::AI_chooseUnit`, with the help of chatgpt 5 as usual and always thanks hehe chatgpt 5 and and all or not, so that, if it is the early game (as of now first 150 turns adjusted to game speedwhich are most critical for early unit distribution optimization plus most important instead of expanding cities (doesn't happen as much if at all later on so less relevant and could cause issues to)) and we are not in danger:

- if we have expectedly/guessedlytoo much defenders relative to our city number at this stage of the game (i.e. we don't have enough cities, so don't need as much defenders, invest in offense or versatile UNITAIs rather)
- or if we simply have a majority of defender UnitAIs

Then switch the unitAI of the unit built to an offense or versatile one based on luck and relative proportions if the unit can have said unitAI (else keep defense unitAI or similar defensive UnitAI) (added note about this in the XML for example of the longbowman at UnitAIs so we keep the UNITAI_COUNTER there or add it if not present before, if it is relevant to our mod and all).

Before the changes (existing screenshots between 395 and 400 and a few other named ones), we had way too much longbowmen for joao ai (36 longbowmen for only 3 cities which is insane and very inefficient), which for maybe about half more or less could have been leveraged as attackers to fix bankruptcy risk with some of our units dying and us gaining land i.e. city(ies), gain more cities with excess unit so leveraging it as well. In particular, we can see almost of all of these are UNITAI_CITY_DEFENSE or UNITAI_CITY_COUNTER, which is insane, needless, and very inefficient for this low city count.

After our changes (existing screenhots between 401 and 415), somehow the game plays out a bit differently, and joao ai has a 4th city a bit far but much less units, and a very versatile composition of spearmen, a few axemen and chariots, also, since he has few cities, some of his longbowmen were produced as UNITAI_COUNTER as per our code. All in all, a very nice gain, and hopefully a much better late game although i didn't test it yet.

Justinian AI also had it play out differently after our changes (but seemingly reproducible, just as was for joao ai after the changes), now he only has 4 cities, but still too many longbowmen (about 19 at turn 130) for some reason after changes, yet, despite having much less cities (had 5 more or less at quick glance before our changes), he however has a mobile troop of counter longbowmen as can be seen in screenshot, to hopefully make some military gains or at least replace them fast enough and not go bankrupt (with so few cities no need to accumulate excess defenders i mean, aim to expand or die rather i would say as we'd lose late game anyway), so i think the results are very good!!!

I was curious, so i continued autoplay to turn 200 to compare to before, and now joao ai and justinian ai have much better outcomes, joao ai settles a new city and punishes inca ai by taking a city from him (although he was stronger it seems at a glance after changes for some reason(butterfly effect xd maybe or randomness but good we made gains with our changes and they are not detrimental longterm it seems at a glance based on this autoplay)), as for justinian ai, he makes military gains as well it seems, i suppose his early military edge and the extra roaming stack of longbowmen helps give an early edge, instead of having too much excess defenders and then somehow collapsing. All in all looks very good.

Note: for simplicity and also to not alter too much base advciv +/- civ4 behaviour, we only tweak the UNITAIs of the units we produce if these criterion are met, but do not alter war decisions or such, still it seems base advciv or at least now our mod's code picks up well enough on this available stack and uses it seems (although i didn't look in detail). Defense seems to be preserved since we targeted mostly low city empires or ones with mostly defenders (might backfire a bit for large empires so maybe we could make the check stricter but maybe they can gamble a bit early on and bet on them producing enough units midgame to fill all cities, while low city empires would aimed for targetted invasions to attempt to overcome low city number ideally).

## 53.2.2 (Seemingly greatly enhanced) AI overproducing defenders early on, especially longbowmen but not only, replaced with an early produce more versatile units especially civ-specific ones when defended enough (at least in theory) in CvCityAI::AI_chooseUnit

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1xiDPP6ySpqr61T08iJ9hNKv4IWodcUCq?usp=sharing).

This is an issue that i think has now been significantly improved, and that should make AI stronger (at least in theory, as it doesn't seem always applied, but often enough), so AI is hopefully stronger thanks to this (but check to be sure).

The problem was that AI would often produce too many defenders in the early game, which we tried to address in 53.2, but in an autoplay run i tried, hatshepsut ai had both many cities but also somehow most units in the game, which was not covered by our previous fix in 53.2, so she seemingly still produced way too much units.

So i added code to take into account our defense needs as minimally as possible (offense units can defend too especially if we are stronger), but also enhanced and expanded upon the code in `CvCityAI::AI_chooseUnit` to now actually change the actual unit produced to an offensive or more versatile-offense oriented unit, carefully ignoring non default unitais like counter if not the default one (else we'd produce tons of longbowmen but not more versatile units, which is a waste if we are so strong, no need to defend so hard, even if we have many cities to protect, we can still capitalize a bit on our strength i think and make some gains or weaken nearby rivals somehow if we can).

The results are very impressive, hatshepsut ai went from having +/- 30 longbows at turn 130 which was a big waste even if she had 6 cities more or less (didn't count exactly) to now 32 war chariots at turn 130!!!! and other units like 9 camel archers, etc.

Although in some other cases it doesn't seem applied, like khmer ai still going for many longbows, despite having bonuses to build other units (didn't check in detail), but should make quite a difference, he seems to have less longbowmen than before changes and quite a few other units like spearmen which i think is good for versatility as well.

While making this new code, i also tried to enforce picking (extra valuing) civ-specific units on the assumptions they are nice (war chariots very cheap and effective for example rather than a horse archer), and avoid otherwise weak units to avoid high unit costs and low effectiveness of the military.

I then tried another autoplay run and it was very very brutal, with ewuare ai having 150+ cavalry (update note: since then reframed as dragoon units) at turn 260 (in a standard monarch pangea normal game speed map) more or less and other units in lower numberwhere he won! Despite not having train percent discounts per era anymore in advciv-sas as of now! I think the good offensive start helped convert it easier to a middle game offensive stack although i didn't check in detail. If you're curious about this run, i shared some / a few of the screenshots [there in this CFC advciv-sas post](https://forums.civfanatics.com/threads/advciv-sas-simple-advanced-strategy.699716/post-16866658).

So overall very good results it seems!

While doing this, i also enhanced the code of the fallback unit choice `CvCity::doTurn()` in as of now [51 - (Worked around / fixed) Massive seemingly base advciv +/- civ4 issue of many cities entering no production early for 1 or several turns many times during the game early (and possibly later this is why many cities have a process rather than no production, as processes are not available early and are listed among fallbacks if production fails it seems but check to be sure)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#51---worked-around--fixed-massive-seemingly-base-advciv---civ4-issue-if-im-not-mistaken-of-many-cities-entering-no-production-early-for-1-or-several-turns-many-times-during-the-game-early-and-possibly-later-this-is-why-many-cities-have-a-process-rather-than-no-production-as-processes-are-not-available-early-and-are-listed-among-fallbacks-if-production-fails-it-seems-but-check-to-be-sure) with quite similar logic as well (actually improved it while doing changes here and then ported these improvements in a relevant wayto the chooseunit function).

Update: we as of now now favour civ-specific counter units just as much, with an optional config flag not to in sas defines.

Update 2: see another example of windbg usage to bugfix (i don't know too much about these but seems to help looking at these error messages and .dmp analyze results and feeding them to chatgpt 5 or such other ai for review, check if accurate): [Known issue #71](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#71---seemingly-fixed-base-advciv-bug-of-calling-cvbuildinfoisfeatureremove-when-efeature-is-not-a-valid-feature-then-firing-a-failed-assert)

## 53.3 (Tremendously Improved) AI overbuilding siege units, in particular trebuchets but not only, where they are detrimental to do build, in particular when weaker but not only

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/180Hnkhno1HgQb9rzPu-EA9ahH0dr-36K?usp=sharing).

This is another nice AI enhancement :). I have noticed after doing known issue as of now 53.2 that for example when continuing the game, our autoplay ai and maybe other players too produce way too many trebuchets (i had noticed the issue with cannons too before).

It is also an issue quite often mentioned by players it seems, so i'm glad i could have enhanced it.

Before our changes, our autoplay AI has more or less 20 trebuchets and is producing one in all or if not almost all our cities which is extremely inefficient, especially considering we are not the strongest if i remember it correctly, and trebuchets are bad at anything else other than attacking cities (bad at defense, low hammer efficiency vs a catapult, cannot attack efficiently if not attacking city tiles).

So i implemented a logic in `CvCityAI::AI_chooseUnit`, that i then generalized a bit less strictly for all siege units depending on era (later siege units are as of now stronger like the cannon, so give more leeway to produce some more as they can be more versatile IF AI uses them well for example for defense which shouldn't be the case yet but i didn't check for sure i mean it is safer and more efficient to tell AI to not overproduce them as well even if even less strict), so that our offense unitai composition cannot have too many siege units in them (ranges from none to 70% of all attackers depending on various conditions, often being around 30% or similar as of now but check code if this is updated or accurate).

The results ingame are very good. The game took a different turn (no pun) starting just before olmec was razed in the early game (for example mongol AI got an early big conquest even though was beaten down later), and at turn 200 instead of having useless extra trebuchets, we have a strong 16 unit stack of macemen, horse knights, etc, attacaking julius caesar AI, exactly as we wanted.

note: was before german hussars were moved to a later mounted unit.

Also, german AI seems to benefit more from these changes, as in the mid-late game he produces hussars instead (of cannons or whatever he produced then i guess), and secures a conquest win 50 turns sooner!! (around turn 280 instead of turn 330 before the changes), with a very impressive production and unit count with our current balance settings (that don't give per era freebies or exponential reduction to cost or such anymore), with a very impressive composition at turn 285 where he winsof 54 hussars, 26 camel cuirassiers, 26 pikemen, 5 cannons, 25 musketmen, 26 pikemen, and a bunch of / few other units in small count. (Another difference is also julius caesar ai was much stronger this run, securing several/many cities instead of shriking).

Downside is we seem to underproduce siege units a bit, but this is fine, especially early, where they shouldn't be too efficient to use if not for attacking cities, so as long as we have a bit of enough should be hopefully fine, else we can tone it down (or up). Left as such for now.

Note: among experimental changes, i tried changing trebuchets to unitai_attack_city_lemming to help reduce their production when not relevant, but it seems they were not produced at all anymore (or if they were (much less if at all produced), it was not with this unitai but with unitai_attack_city in debug view ingame it seems), so i'd say unitai_attack_city_lemming is not a reliable unitai to use so i don't use it in our code as we were not doing more or less guessedly, but check if accurate as this is just a guess from me and i don't know how it works

## 53.4 (Tremendously Improved) AI overbuilding very cheap combat units (ancient macemen only being an issue as of now) in the early game, sometimes even at turn 100, which is inefficient and easy to overshoot, as they are cheap and accumulate quickly, but are not too effective especially as soon as we get archer units, now limited, especially even more so after as of now turn 50 where they should be especially useless; much better military compositions and better growth as a result

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1NDQ2qC5wr7f3ERVIxzE9HzyYs5hnW89e?usp=sharing)

This is another very nice change, that should make AI significantly stronger and more efficient with its unit compositions.

I have noticed AI produce ancient macemen if left unchecked even at turn 100 which is especially useless, and as they are so cheap they tend to quickly pile up.

In our mod, ancient macemen have more strength than archers but are worse at city combat (plus archers are available very early at as of now tech_hunting, so some civs even start with them directly, and so i meanwe should really avoid overstacking ancient macemen after our minimal offense or such very early needs which i think i am not and based on results below too but check to be sure i mean), so after the very early game they are mostly useless, plus archers are more versatile and help us fill our defensive quotas so better choice long term. And since archers are more expensive, we will build less so will go bankrupt not as soon, spend less time upgrading ancient macemen but instead directly build axemen or swordsmen or such, at least seems so in autoplay. So we now make it even stricter after turn as of now 50 adjusted to game speed.

As compared to before changes (see screenshots in known issue [53.2.2 (Seemingly greatly enhanced) AI overproducing defenders early on, especially longbowmen but not only, replaced with an early produce more versatile units especially civ-specific ones when defended enough (at least in theory) in CvCityAI::AI_chooseUnit](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#5322-seemingly-greatly-enhanced-ai-overproducing-defenders-early-on-especially-longbowmen-but-not-only-replaced-with-an-early-produce-more-versatile-units-especially-civ-specific-ones-when-defended-enough-at-least-in-theory-in-cvcityaiai_chooseunit) for comparison, including the cfc forum link there for the other map's compositions) in `CvCityAI::AI_chooseUnit` to fix this very cheap combat units being produced issue, we have now much less ancient macemen at turn +/- 100, and more stronger units like swordsmen or such in composition of AI players, which seems very sane, more efficient economically and militarily, and very strong too at least significantly stronger it seems (e.g. 3 vs 11 ancient macemen at turns 100-130 for example from what i remember of it).

Note: the way the code is as of now written, it may apply to scouts as well since they have strength/combat as well if i'm not mistaken, but the cap should be large enough that it shouldn't be a concern (unless we overproduce them then fine to limit them as well).

Update: now generalized the no excess very cheap units code/formula to a few later eras such as classical and medieval plus, to attempt to help trim units later as well when they are relatively very cheap for their era (e.g. archers at classical, longbows or trireme at medieval era), while making sure new era thresholds don't apply to old units tier (e.g. ancient maceman having very low threshold at ancient era but then when entering classical era suddenly it would benefit from the archers or such threshold that is larger and thus we'd overproduce ancient macemen then as happened in autoplay after i first refactored it), so units are ordered by tiers rather than by era, see `CvCityAI::AI_chooseUnit` or [GlobalDefines_advciv_sas.xml](/Assets/XML/GlobalDefines_advciv_sas.xml) for details.

I don't know if it's for sure a result of these, but we seem to have really good results, with japan ai reducing its longbow output from +/- 75 longbows at turn 200 (way too much) to something more like 50-60 longbows but 10-15 camel archers or 20-27 samurais depending on runs and settings somehow it seems, but composition does seem quite a bit better if no just fluctuaiton, check to be sure.

Update 2: now the anti excess very cheap units is also included in `CvCity::doTurn` in the no production fallback unit code, as we were producing too many fallback ancient macemen otherwise with the new offense only code (like 19 ancient macemen at turn 100 which is very inefficient and most likely to bankrupt us or ruin our game).

Update 3: code now disabled now that we as of now have the unit `ObsoleteTech` field. Other parts of the documentation may also now be stale and not mentioned to be as such.

## 54 - (Fixed) Major Base Advciv +/- civ4 bug in AIFoundValue::adjustToCivSurroundings causing AI settlers to value midgame (turn 50+ for example here) settling on camel desert; worked around and disabled this function entirely, now inline a very simplified version of it inline in its only caller

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1gYU7NrXpJNc5p6hbqOsCxnOmCy_7VTDf?usp=sharing)

As can be seen in existing screenshots between 3073 and 3089, AI would settle an extremely bad spot on a camel desert tile which is bad on itself already but which is on top of it fully surrounded by desert, the absolutely worst site. But in the early game AI would not consider this site as among its best (no colored circle at that plot for any player so i assume it means this), only later on, at turn 51 (not at turn 50)

I have tried to find why, and comment out like a madman xd if i may say and told chatgpt 5 too, blindly, until i found the issue, specifically caused by enabling these lines:

```cpp
	// if (!kSet.isStartingLoc() /* advc.031e: */ && !kSet.isNormalizing())
	// 	iValue = adjustToCivSurroundings(iValue, iStealPercent);
```

Yet again another shitty base advciv +/- civ4 code.

It's such a huge mess i said screw this, let's rewrite it much simpler, so this `AIFoundValue::adjustToCivSurroundings` function is now disabled, which fixes our issue, and i have enabled distance penalty code and culture press checks in a much simpler manner with the help of chatgpt 5 if i may say thanks a lot, inline in the only caller of this function (`AIFoundValue::evaluate` if i'm not mistaken).

Testing ingame is extremely good, as can be seen in existing screenshots between 3131 and 3141. We now do not settle on the camel, and in fact not at all in this desertic area but around it, plus we don't settle too close to our rivals either at a glance it seems, so i would say this is an extremely good result, and yet again another example of shitty base advciv +/- civ4 (whoever wrote this code xd despite the other good things they may have done) code.

Thanks to this, i believe AI is stronger and settles better, but check if accurate.

Note: i also adjusted distance to civs, as well as culture pressure settling choices, to reject too far (vs penalizing far distance only which would not strictly forbid site if not penalized hard enough if i'm not mistaken) or too culturally pressing sites entirely (didn't test but maybe same at least now we reject too culturally pressing sites at least in theory (didn't test it too much but seems to work as such at a quick glance)).

## 55 to 60 -

<details>
<summary>Mostly reverted due to causing issues, minus some safeties or very conservative tweaks</summary>

## 55 - (To keep in mind if you have a game crash in AdvCiv-SAS) One of the culprits could be AI_bestCityBuild (after we rewrote it entirely more or less) sometimes firing not null or whatever (there are lines to uncomment in its callers that may fix it)

This is an issue specific to AdvCiv-SAS i think after we rewrote `CvUnitAI::AI_bestCityBuild`, but i think i should document it.

If you have a game crash, consider first adding null or such checks to `CvUnitAI::AI_bestCityBuild` callers which are very few.

In particular, as of now i fixed the crash at turn 77 in a save file by strengthening our null things we set up in `CvUnitAI::AI_bestCityBuild` (most likely we changed them after rewriting the candidate plot logic but i am not totally sure still it should be something related to this). The crashes didn't happen until i stopped relying in the fallback NO_BUILD returned by `pLoopCity->AI_getBestBuild(NO_CITYPLOT) == NO_BUILD` line in `CvUnitAI::AI_nextCityToImprove`. So after i strengthened these null or such checks (i don't know too much about these but it did fix the issue) in `CvUnitAI::AI_bestCityBuild`, issue was now fixed, and i do not rely on it anymore and have no crash at turn 77, yay! If i may say.

Since all seemed to work well and no crash, i kept it as such. Until a few more autoplays later (i.e. of other save files), when i now got a crash again at turn 68, that i could fix by uncommenting another safety i had added in `CvUnitAI::AI_nextCityToImprove` which is:

```cpp
		// <!-- custom: be careful, commenting out the null and no build check i added below causes the crash again at turn 77; update: very good results!! We now don't need this hacky failsafe that according to chatgpt 5 would cause workers to skip improving cities, cleanly fixed now no crash at turn 77 so we can disable it, but if you see a crash again, consider enabling it to see if helps even if issue may not be directly cause here but this could prevent it perhaps, seems fine though now but check to be sure -->
		// <!-- custom: update 2: although the crash at turn 77 was fixed, we get another crash (in another save file, at turn 68 now) fixed by uncommenting this, so until this is found kept as such i.e. uncommented -->
		if (pBestPlot == NULL || eBestBuild == NO_BUILD)
			continue;
```

Kept as is until i find the cause, but if we can streghten our functio so we don't have to rely on this, i may remove it later.

If i remove it (i.e. assuming we fix this specific crash and you encounter a crash), consider tinkering around `CvUnitAI::AI_bestCityBuild` or its callers, and see what happens and if it solves your issue, including but not only reenabling the safeties i mentioned or others changes if any.

Update: fixed!!! The culprit was not our now strengthened (and before that nicely rewritten) `CvUnitAI::AI_bestCityBuild` function but instead our reliance on old code of the `AI_betterPlotBuild` in `CvUnitAI::AI_nextCityToImprove` a bit after calling our rewritten function:

```cpp
		getGroup()->pushMission(eMission, /* </advc.121> */
				pBestPlot->getX(), pBestPlot->getY(),
				eMission == MISSION_ROUTE_TO ? MOVE_SAFE_TERRITORY : NO_MOVEMENT_FLAGS, // advc.pf
				false, false, MISSIONAI_BUILD, pBestPlot);
		// <!-- custom: don't rely on this anymore, we get nice and reliable builds from AI_bestCityBuild, but this line interferred with it and caused the crash at turn 68, at least commenting it out fixes it and we can remove our safety guard above. See code comments in this function or known issue as of now 55 for details, tricky bug found by chatgpt 5 too thanks a lot thanks to my prompts too and or such -->
		//eBestBuild = AI_betterPlotBuild(*pBestPlot, eBestBuild);
		//
		getGroup()->pushMission(MISSION_BUILD,
				eBestBuild, -1, NO_MOVEMENT_FLAGS,
				//(getGroup()->getLengthMissionQueue() > 0), false, MISSIONAI_BUILD, pBestPlot);
				true, false, MISSIONAI_BUILD, pBestPlot); // K-Mod
```

So as i said in as of now one of the code comments related to this fix, at this point i think it's better to crash and fix whatever flawed logic we have cleanly than avoiding it and having suboptimal, not necessarily visible issues. If you have a crash again, consider adding or reenabling such checks in or near our rewritten AI_bestCityBuild callers which are very few as of now.

Update too no pun: see [56 - (Fixed) Most likely base advciv +/- civ4 crash at turn 156 fixed by commenting out the !getPlot().isSamePlotGroup(*pBestPlot, getOwner()) check in CvUnitAI::AI_nextCityToImprove else block (old code)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#56---fixed-most-likely-base-advciv---civ4-crash-at-turn-156-fixed-by-commenting-out-the-getplotissameplotgrouppbestplot-getowner-check-in-cvunitaiai_nextcitytoimprove-else-block-old-code) for related subsequent crash at turn 156 and extra fixes.

## 56 - (Fixed) Most likely base advciv +/- civ4 crash at turn 156 fixed by commenting out the !getPlot().isSamePlotGroup(*pBestPlot, getOwner()) check in CvUnitAI::AI_nextCityToImprove else block (old code)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1bUMSFijm5cAD48Fy-RSnvu-1oI1G2IpV?usp=sharing)

So this is a tricky crash that we got after fixing the crash at turn 68 above (see known issue as of now 55 for details). We since then don't rely on the old "guard" that was in fact a hard reject so of course we got/had no crash anymore (or no more xd?)since we rejected all builds xd, as chatgpt 5 told me if i understood it correctly, which was very bad, so now this old hard reject is not used anymore, and instead through trial and error and blindly commenting out myself hehe, i found the issue to be in the else block (i.e. the non-bonus roading old base advciv +/- civ4 logic that we kept as an alternative path) in `CvUnitAI::AI_nextCityToImprove`.

Then after a lot of back and forth, and then even then back and forth with many AIs including Grok AI i used for the first time xd too (Grok 4 Expert as of now) which was very sharp and helped chatgpt 5 too, from what i understood of it as i don't know too much about these xd, i then got the idea myself to blindly comment out things in the else block, and luckily got it right at first try hehe (i did so because i didn't want to change old code unless we had to, plus a non crashing code chatgpt 5 provided performed much worse in terms of worker AI efficiency, 5 workers on a tile to chop forest, then cancelling it and roaming wherever xd, it was a mess but no crash then, but helped too to motivate me to try this xd thanks maybe):

```cpp
		if (!getPlot().isSamePlotGroup(*pBestPlot, getOwner()) || !getPlot().isRoute() ||
			SyncRandOneChanceIn(stepDistance(plot(), pBestPlot) + 1))
```

which i commented out as such at first:

```cpp
		if (/*!getPlot().isSamePlotGroup(*pBestPlot, getOwner()) ||*/ !getPlot().isRoute() /*||
			SyncRandOneChanceIn(stepDistance(plot(), pBestPlot) + 1)*/)
```

No crash!!!

After asking Grok AI and chatgpt 5 (AI too), i went on and reenabled the syncrandonechancein part of the check and still no crash, so this confirms that the issue was indeed this issameplotgroup part of the check that was causing errors, and our workers are still super efficient, great!

So now code is as of now as such instead in `CvUnitAI::AI_nextCityToImprove` in the else block still:

```cpp
		if (!getPlot().isRoute() || SyncRandOneChanceIn(stepDistance(plot(), pBestPlot) + 1))
		{
```

And yay no crash!!

Considering i recompiled it several times including after polishing code comments and still no crash at t200, and considering it always crashed when starting from this autoplay save file (in drive link) and doing exactly 100 turns (doing 50 turns then resuming didn't seem to reliably if at all cause the issue although i didn't dig too much to be sure, do 100 tursn from here if you want to investigate it so from turn 100 to turn 200 to trigger the crash at turn 156 in like 10+ runs i did or something similar if less if i may say we would always crash so i would consider it reproducible from this save file with this number of autoplay turns), i'd consider the issue solved since i tested it a few times with a few recompiled versions of this change, no issue to turn 200.

I am very happy of this result and of us (i.e. me or maybe players xd) being able to keep AI worker efficiency and also solve what i think is/was nowan old base advciv +/- civ4 crash (likely due to tinkering with pointers or such or who knows what), that was hidden by the betterplotbuild assignment as explained in known issue as of now 55 i guess or something similar or perhaps it is related to how we rewrote bestcitybuild function but less likely, but i don't know too much about these, ask chatgpt 5 to be sure! Or some other AI (or), and check if accurate too if i may say!.

See also: [58 - (Fixed/Enhanced) Reproducible crash at turn 95 in another map, related to the else block in CvUnitAI::AI_nextCityToImprove, by rewriting the else block based on the (more?) code at CvUnitAI::AI_connectPlot](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#58---fixedenhanced-reproducible-crash-at-turn-95-in-another-map-related-to-the-else-block-in-cvunitaiai_nextcitytoimprove-by-rewriting-the-else-block-based-on-the-more-but-code-at-cvunitaiai_connectplot)

## 57 - (Not reproducible) Unknown game crash at turn 94

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/15z0uxT_RxClHNk0u7HnlcmqdmA9gLNkO?usp=sharing)

I cannot reproduce it from same save file at least not in a few retries (even exiting program and retrying), so cannot investigate this further, but it seems in rare cases (didn't happen in more or less 5+ 200 turns autoplays i tried since last known issue fix as of now 56) we still crash quite early in this case i mean, at turn 94 in this example.

No idea what the cause is, but could be DLL related based on the .dmp (see screenshot) (although this is just a guess, check if accurate and i don't know too much about these).

Btw, if useful, i have added info on how to enable .dmp files at crash here in [Modding_Ressources/README.md#how-to-enable-dmp-files-so-for-some-crashes-that-dont-immediately-exit-you-get-a-splash-screen-whatever-it-is-called-and-can-dmp-and-see-turn-at-crash](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README.md#how-to-enable-dmp-files-so-for-some-crashes-that-dont-immediately-exit-you-get-a-splash-screen-whatever-it-is-called-and-can-dmp-and-see-turn-at-crash).

## 58 - (Fixed/Enhanced) Reproducible crash at turn 95 in another map, related to the else block in CvUnitAI::AI_nextCityToImprove, by rewriting the else block based on the (more?) code at CvUnitAI::AI_connectPlot

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1EbDC3zsot974BCe-hTyh0aB9xhxnjZyq?usp=sharing)

This time i got a crash i could reproduce, so eventually found and fixed this one.

But first some context: after our starting techs changes/reworks, now on map number 385 (is just my own numbering of testing map, not related to any other popular save or such numbering or purely coincidental if so), starting from save file (appended in drive link) at turn 50, autoplay 50 turns from there and we reliably crash at turn 95. Very unlikely to be caused by this pure xml civilization info change, especially considering past history of recent crashes, but since this crash is now (assuming is the same, regardless we'd have to debug or attempt to debug or fix it ideally) reproducible so i could use it to investigate and now fix the crash it seems reliably.

I did as in previous issues, uncommenting i.e. reenabling the hard reject in `CvUnitAI::AI_nextCityToImprove` fixed the issue, so it pinpointed it a small scale of likely culprits. As this is not optimal, i also tried commenting out the else block which also fixes the issue.

Then i tried changing a few things blindly or empirically +/- with the help of chatgpt 5 or some other ais like grok 4 or and such but no luck.

After looking at other code samples and how they use ROUTE_TO, it seemed like the code at `CvUnitAI::AI_connectPlot` was very reliable, at least worth a try, i quickly glanced but it seemed so and also based on how chatgpt 5 mentioned it when i gave it some code samples among other ones.

So chatgpt 5 wrote some drafts, and one of them i tested seemed to be minimal, conservative, fixing our issue, while also preserving roading and efficient enough (seemingly same as before: one worker per tile, cities roaded enough, no weird worker roaming or back and forth without builds, and cities improved fast enough at turn 100 or such) so i kept the rewrite this time. It seems to enhance our roading logic too although i only checked or glanced rather and i don't understand too much this code or the c++ code in general but i think i got the main idea hehe.

A few notes now that this is seemingly solved reliably and nicely enhanced it seems:

- this is a rare crash, a few games autoplayed end to end fine after the fix of crash at turn 156 in [56 - (Fixed) Most likely base advciv +/- civ4 crash at turn 156 fixed by commenting out the !getPlot().isSamePlotGroup(*pBestPlot, getOwner()) check in CvUnitAI::AI_nextCityToImprove else block (old code)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#56---fixed-most-likely-base-advciv---civ4-crash-at-turn-156-fixed-by-commenting-out-the-getplotissameplotgrouppbestplot-getowner-check-in-cvunitaiai_nextcitytoimprove-else-block-old-code) (btw coincidence of issue 56 and turn 156 crash xd i just noticed but purely coincidental really(but still cool)). It is reliably reproducible 100% though from same save file it seems though so rare in the sense that many other maps play fine after our last fix, so hopefully code is even mre robust now (and not just going back and forth between fixing and unfixing xd, at least i think so (that code is more robust))
- observation: if i autoplay 35 turns only, so 50->85, then autoplay X amount of turns, say 20 turns, to say 85->105 then we don't crash anymore weirdly. Despite me not reloading nor anything but just holding off for a little while to save. This is consistent though with what i had observed in known issue as of now 56 where i couldn't reproduce the crash if starting from a closer save point but always could from a farther one, very weird though but there must be some explanation, it also means saving could maybe help somehow workaround unknown crashes for players?
- while attempting to fix, i added an extra safety in `CvUnitAI::AI_betterPlotBuild`. Although it didn't help fix it and seemingly wasn't related to our crash (didn't cause it, didn't help fix it) but it seems fine and safe to add, as recommended and provided by chatgpt 5 thanks to my prompts and such too. In case a future crash happens there, hopefully this would help prevent it, and hopefully it doesn't break anything. Consider tinkering with it to troubleshoot and see if it is still needed or not now, or if it makes any difference. Seems like a good practice to add, but i didn't rewrite the other functions (that call it) so i don't know too much if at all what this would cause in terms of gameplay. Cities seem to mostly be improved fine so kept as such, check if accurate (also added for my sanity xd)
- game now plays end to end until some ai wins at turn 270+ a space victory so all seems good.
- finally below chatgpt 5 recommended upon re review at next prompt this extra safety when i told it issue is fixed. I didn't want to complicate anything since our code is clean and simple, but consider adding it if helps (i also don't know too much about these so check if accurate too and all the more reason not to mess xd at least since we have no issue nor thing to improve here it seems at least but check if accurate or if this is possibly useful as grok also recommended after seeing the solution chatgpt 5 had provided before this extra safety it recommended)

>Extra-safe city fallback
>
>If the saved iTargetCityId somehow goes stale, try the working city of the target plot before falling back to MOVE_TO.
>
>```cpp
>CvCityAI* pTargetCity = NULL;
>if (iTargetCityId >= 0)
>    pTargetCity = GET_PLAYER(getOwner()).AI_getCity(iTargetCityId);
>if (pTargetCity == NULL && pBestPlot != NULL)
>{
>    if (CvCity* pWC = pBestPlot->getWorkingCity())
>        if (pWC->getOwner() == getOwner())
>            pTargetCity = pWC->AI_getCity();
>}
>```

Now all cities of all AI players are improved and roaded fine and fast enough nicely it seems, except elephantine city that is not improved nor roaded at all at turn 200+, then after it is roaded gets nicely improved a very nice and strong city, but a bit too late, so trying to make workers move there faster as our next known issue.

See also: [60 - (Fixed) Seemingly rare reproducible crash at turn 283 in CvUnitAI::AI_nextCityToImprove, by adding a bunch of seemingly conservative safeties (as chatgpt 5 did, check if accurate)](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#60---fixed-seemingly-rare-reproducible-crash-at-turn-283-in-cvunitaiai_nextcitytoimprove-by-adding-a-bunch-of-seemingly-conservative-safeties-as-chatgpt-5-did-check-if-accurate)

## 59 - (Partially improved) some AI cities are not improved enough and totally neglected for dozen turns

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1FrLep_WV4E8kkdvw6zs0EB-YP0-1z1ea?usp=sharing)

After fixing previous known issue as of now 58, i have (had?) noticed that some cities are neglected for a long time like elephantine city at turn 200 in one of the first screenshot in this known issue. Then looking more closely, i also noticed that at turn 100 we don't move fast enough to some cities, and overimprove some other cities.

I tweaked the code at (in?) `CvUnitAI::AI_workerMove` tentatively to attempt to skew that a bit, while also attempting to fix some edge cases while doing so, like a 2 land tiles city in same landmass, if just counting based on city population we may stay here forever trying to raise its city plot count to 10 which is impossible, etc.

Thanks to these changes that at least in theory should improve things a bit, we do seem to notice better i.e. sooner improvement in these cities, for example elephantine is improved at turn 190-200 vs turn +/- 230 before, and the nothern city is still improved around turn 190 as before.

These could be autoplay fluctuations, but i repeated it a few times, then started from turn 0 again instead of turn 100 save file of the original save file of this known issue as of now 59 that is at turn 100, and even at turn 100 some cities seem to be improved a bit more.

Again, could be autoplay fluctuations, but it does seem to be slightly better, and since it doesn't break anything, and theoretically improves/enhances old code, i am comitting it as such.

Chatgpt 5 helped me a lot write a more advanced version of it but it failed to produce the expected change, being slightly worse, so i'm happy with this conservative change at least for now, if as expected it improves things quite a bit without making it worse. Check if accurate.

Note: as for screenshots, see existing screenshots between 3387 to 3395 for how it was before (i don't have the elephantine screenshot anymore if i had it at all it seems), vs existing screenshots between 3423 and 3429 (run from turn 100) (as for from turn 0 it seems it didn't screenshot when i pressed key, and autplaying produces a different outcome (city spot settled by another AI player, where some city is not improved for enough time but empire overall quite ell if tno very well for most cities improved it seems at a glance but check ingame if accurate maybe as again these are conservative and not fully fixing changes, that aim to not disrupt previous logic or make it worse hopefully as i don't understand too much about these nor am i able to change them, else may have tinkered a bit more))

## 60 - (Fixed) Seemingly rare reproducible crash at turn 283 in CvUnitAI::AI_nextCityToImprove, by adding a bunch of seemingly conservative safeties (as chatgpt 5 did, check if accurate)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1uOm6zvQjV4D018oyMHYMGOcUtBNVyKn4?usp=sharing)

As usual a crash that was fixed by reenabling our hard reject in `CvUnitAI::AI_nextCityToImprove` as explained in [58 - (Fixed/Enhanced) Reproducible crash at turn 95 in another map, related to the else block in CvUnitAI::AI_nextCityToImprove, by rewriting the else block based on the (more?) code at CvUnitAI::AI_connectPlot](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#58---fixedenhanced-reproducible-crash-at-turn-95-in-another-map-related-to-the-else-block-in-cvunitaiai_nextcitytoimprove-by-rewriting-the-else-block-based-on-the-more-but-code-at-cvunitaiai_connectplot).

But this is very suboptimal, so i asked chatgpt 5 if it had an idea of how to fix this based on our previous documentation and current code. I didn't feed it the .dmp as in the drive link of this known issue, but it does seem like a pointer or such issue from little i know about these (more precisely about what it shows rather: exception code "0xC0000005" and exception information "The thread tried to read from or write to a virtual address for which it does not have the appropriate access." in VS C++ 2010 Express since it also opens .dmp files nicely thanks i mean).

Notes:

- the ingame screenshot shows tech tree but it should be unrelated, as i was just browsing it and the crash was reproducible.
- same observation as usual: the crash is reproducible many times (at least i did 2 times from save file at turn 200 (autplay 100 turns from there so 200 -> 300), but not reproducible if i "bridge" save at turn 250 (autoplay 50 turns from there so 250 -> 300) then continue normally without even reloading or exiting the program), which is strange but must have an explanation i mean but which may also help if one has such crashes to perhaps workaround them.

In all cases, chatgpt 5 very nicely and very swiftly fixed it at first try, very impressive and thanks a big lot for the long hours or such if not morewhichever time it is it saved me.

At this point i don't understand too much what's going on in the code xd, but i tried to annotate it with the info/feedback/analysis chatgpt 5 gave me, check if accurate though.

The additions are conservative overall from what i can see or understand of them, so hopefully they don't break anything especially worker efficiency, and seem very targeted changes that aim to fix rather than rewrite, but is just a vague guess or rather impression and i don't know too much about these, check if accurate.

Ideally i would undo these one by one, until i find culprit, and only mention the others here here not related to the fix, but this is way too tedious, and if it doesn't break anything and preserves functionality i'd rather keep it as is if seems safe(but check if accurate)

The issue seems now fixed as i tested it twice and it seems to not crash anymore from turn 200, while it crashed reliably twice before from turn 200 as well. To complement this doc since i don't understand too much about it, i asked chatgpt 5 to provide some info on what it changed or the issue in general or and such, here is below what it said (i edited it a bit as there was an inaccuracy line which i removed from below that said we changed betterplotbuild when we in fact changed it long ago not now), check if accurate as i don't know too much about these):

>**What went wrong (T283) & what we changed**
>
>- Crash pattern: rare, late-game, masked by the "hard reject." Likely invalid state used between target selection and mission queuing (0xC0000005).
>- Root causes (probable): (1) stale/dangling `pTargetCity` when a city is razed/traded after selection; (2) attaching the **wrong missionData** on the first `ROUTE_TO` leg; (3) a bad in-loop guard referencing `pBestPlot/eBestBuild` instead of the current `pPlot/eBuild`.
>- Selection fixes: removed the in-loop "hard reject"; keep `pPlot/eBuild` checks local; store **city ID** (`iTargetCityId`) instead of a raw `pTargetCity` pointer.
>- Re-hydrate safely: after the loop, rebuild `pTargetCity = GET_PLAYER(getOwner()).AI_getCity(id)`; fallback to `pBestPlot->getWorkingCity()` if needed.
>- Routing fix: use a **two-leg** `ROUTE_TO` pattern (city → plot). **First leg**: missionData = `NULL`. **Second leg**: missionData = `pBestPlot`. Don’t reuse path state.
>- Guards added: bail if `pBestPlot == NULL` or `eBestBuild == NO_BUILD`; validate `eBestBuild` bounds; ensure same land `area()`.
>- Sentinel-road: only trigger if `eBuildRoad != NO_BUILD` and a real bonus is present.
>- Fallback: if no route legs queued, issue a `MOVE_TO` to `pBestPlot`, then re-check `canBuild` immediately before `MISSION_BUILD`.
>- Kept: anti-dogpile cap (`iMaxWorkers=1`) and existing pathfinder handle.
>- Result: no repro of the T283 crash; worker behavior (one-worker-per-tile, efficient targeting) preserved.

Additionally, while i should have started with this to give more context, chatgpt 5, the one that gave me the code that fixed it, also said this as part of its reply, below:

>Reading the code you pasted, I see three risky spots (all late-turn sensitive):
>
>Wrong variables checked inside the city loop (the old "hard reject")
>You still have a continue; line that checks pBestPlot / eBestBuild inside the loop that’s evaluating pPlot / eBuild. That can desync control flow and leave pBestPlot/eBestBuild stale. It also needlessly skips the first viable city every time.
>
>Raw pointer for pTargetCity
>Very rarely (late game, many events per turn) the target city can be razed/traded between selection and mission queueing, leaving a dangling pointer. Using a city ID and re-hydrating the pointer just before use avoids that class of crash.
>
>Mission payload on first ROUTE_TO leg
>On the first leg (route to city), you attach pBestPlot as mission plot. K-Mod’s MISSION_ROUTE_TO expects the final route goal in missionData (or NULL for a pure move/route leg). Attaching a different plot can blow up later in release builds.

The chatgpt 5 that gave me the original fix to this issue also said (check if accurate):

>Why this should kill the T283 crash
>
>Removing the in-loop hard reject stops us from carrying stale pBestPlot/eBestBuild through to the route leg logic.
>
>City-ID re-hydration prevents a rare dangling pTargetCity deref. (Late-game routings happen long after many conquest events; this tightens that window.)
>
>Passing NULL missionData on the first ROUTE_TO leg aligns with the expected K-Mod pattern (missionData = final build plot only). That avoids later code assuming the attached plot is the route target and touching the wrong object.
>
>If you want a tiny breadcrumb for future unknowns, sprinkle this once right before each return false;/early return true;:
>
>```cpp
>// gDLL->logMsg(getOwner(), "AI_nextCityToImprove early-out: reason=<text> unit=%d turn=%d", getID(), GC.getGame().getGameTurn());
>```

However i have noticed an issue, most likely to recent roading changes we made to worker, perhaps in this `CvUnitAI::AI_nextCityToImprove` or in `CvUnitAI::AI_workerMove` or such other function perhaps, that workers try to infitely road while in city tile, which is very inefficient. Ideally we'll try to address this at next known issue.

Update: reverted due to having too much issues, same for old code, is bit less efficient as we road and sometimes improve bonuses sometimes a bit later, but at least it's stable and workers are mostly really efficient, if no rare suboptimal behaviour, but that is overall better than crashes or hard to fix worker issue after issue

</details>
<br>

## 61 - (Seemingly Tremendously Improved) AIs getting baited to attack faraway rivals, leaving their core cities mostly defenseless, and oftentimes dying shortly after to an opportunistic rivals. Changed by adding a pre-filter reject in war risk assessment based on distance to us in Risk::preEvaluate in WarUtilityAspect.cpp

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1e05c5tJ025EJ9Jlgi-WytA3ovV07EYfo?usp=sharing)

This is an issue i had a long time in base advciv and even in advciv-sas as our mod is based on it. That AIs would often be baited or somehow decide to attack a very faraway rival with most of their military (as they should i mean to attack, but they shouldn't attack a too far rival no matter how tempting, if they can't fall back in time to prevent opportunism from ennemies due to their core cities being much less defended as a result, and since AIs seemingly can't do that as of now at least (they were not programmed or don't do so it seems as of now / so far, then better add a simple sanity check to not attack too faraway rivals)).

I added this tentative patch in `Risk::preEvaluate` in WarUtilityAspect.cpp with the help of chatgpt 5 and my adjustments or not or yes or etc(check if accurate as i don't know a lot about these but i aimed for a conservative code that seems very effective, while allowing enough wars to happen otherwise it seems), and it seems to yield extremely good results.

In recent map i tested (a few times to be sure) in autoplay, before the changes (existing screenshots between 198 and 201) at turn 200 we are spain ai and leading at turn 200, but we attack japan ai (which are a bit far from us even though not that much but not contiguous, and maya ai was a much better and weaker target instead for example, so definitely not an ideal target) and capture kyoto, but now we have 13 camel cuirassiers parked there, and if cyrus ai (the main rival in this save file, contiguous to us also in all our land) were to declare war on us, they woudlnt be able to easily go back to our cities, which are more thinly defended as well btw. So attacking japan ai is very risky and most likely a huge mistake.

In turns 250 to 300, cyrus ai attacks us while we are attacking maya ai, and were already thinner, as a result we go from being the leader militarily to easily collapsing to cyrus ai who leads a very effective assault due to our stupid mistakes and greed.

To fix this, i added a max distance to us risk hard reject if distance is too high, empirically with the value of 2 and then 3 (not sure what these values are, but 8 initially suggested by chatgpt 5 was useless, and i tried 2 before ditching the seemingly useless code but it nicely then yieleded extrmely good results, that are reproducible it seems as well) for versatility and not too strict war behaviour (would be bit boring indeed).

Now, resuming from this save file 200 (i tried it a few times and with value of 2 and 3 to be sure, results seem more or less very consistent minus possible small variations if any but same trend), as a result, depending on if we go for the 2 turn or 3 turn route, it seems that we (our autoplay attack) generally, from the same turn 200 save file:

- in the 2 turn (existing screenshots between 203 and 204) version of the code / route: attack the very obvious weak and nearby contiguous to us maya ai, an easy and safe target, at turn 250 maya ai is already our vassal it seems, and our empire is super strong, japan ai is expanding instead but we seem to not care and keep our units focused on this invasion, our military is very strong too (49 camel cuirassiers, 28 cannons, 22 pikemen, etc for minor in number unitsat turn 250). We then at turn 280 also have alexander ai vassalized, a strong and focused empire, and our strongest rival is only at 0.5 ratio of us militarily so essentially won it seems
- then in the 3 turn (existing screenshots between 205 and 206) version to try it tooand maybe add versatility or such, we attacked alexander ai instead (due to turn window wider possibly as he is bit farther but still contiguous to us or some politics made it so i didn't look) who is now our vassal, while maya ai is unattacked and now grows strong; as for cyrus ai he doesn't seem a threat to us, and our units are focused and not overspread like before our change, at turn 250. Our military is very good: 33 camel cuirassiers, 22 cannons, 17 pikemen, etc for lower count units. At this point also we are in fact already at war with cyrus ai, who is weaker than us, and i think it's a great move. At turn 300, it's even better, cyrus ai has collapsed, and usa ai and maya ai are the big top dogs now, with a military close to us in military ratio. As for us our troops are mostly focused (issue with attacking islands on pangea but we didnt send that much units so suboptimal to fix ideally but not as urgent vs how it was), we have lost units overall but our ennemies don't have that much more, i didn't check in detail but i guess many wars happened xd, all in all it's a good outcome for us.

Based on this data, it seems cyrus ai who is sandwiched between most rival to his central position was actually the most vulnerable, and could mostly prey on everyone due to most ais playing stupid and getting baited, leaving their core cities defenseless and in easy reach with their troops being very far. I ran it from scratch at turn 0 to be sure, and now cyrus ai wins instead, i didn't add the data as not relevant to us, but it seems the game goes more cautiously even though there are enough wars, or possibly some other variation influences this.

As for us, what matters is AIs don't get baited as much if at all now at least on land warfare, so they can better keep securing their lead unless enemy is stronger or some weird politics like cyrus ai telling maya ai to declare war on us in the scratch run after our change from little i saw or remember of it.

As results seem very good, i added this change now. As for the don't invade small islands in one landmass-like maps, i'll try to implement it in next knwon issues (not guaranteed, i may or may not do so).

## 62 - (Extremely better/stronger) AI almost not evacuating at all doomed cities (2 swordsmen in an 11 unit defending stack vs a 22+ attacking unit stack), fixed by always and 100% evacuating city doomed city regardless of land unit type, in CvUnitAI::AI_evacuateCity

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/11XgIjY6H8xp3nOHU7Qrn_bQxixzVaKVZ?usp=sharing)

This is an insane as in amazing improvement of AI capability to handle bad odds at war. This is from the save file i gave up on, from [the first map of advciv-sas i had attempted myself xd (cfc forum link xd)](https://forums.civfanatics.com/threads/advciv-sas-simple-advanced-strategy.699716/post-16862444); julius caesar ai came with a 22 stack which totally caught me offguard as i had only 11 stack defenders at turn +/- 125 which i thought was good but not enough, and since other ais were strong i gave up there, but if i wanted to continue, the correct and best move was to give up the city and focus on myself in this case i mean and wait for better odds in this case too..

But in autoplay 2 turns on a row in one go (see important note at [Modding_Ressources/README.md#how-to-autoplay-let-the-ai-play-for-you-super-fast-gameplay--testing-tool-in-map-loaded-save-file-new-game-etc-view](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README.md#how-to-autoplay-let-the-ai-play-for-you-super-fast-gameplay--testing-tool-in-map-loaded-save-file-new-game-etc-view) for details about why 2 and not 1 turn and why in one go too) before this, AI still stays in the city and dies (see existing screenshots between 202 and 211), evacuating only 2 swordsmen out of the 11 stack unit. I thought it's really a waste, and i remembered in base advciv vassals abandonning me and their cities which would then cause me to i die defending alone the city due to this, so evacuating code must have been there. Thanks to the amazing help of chatgpt 5and me too, i found the place where to make such changes, which is in `CvUnitAI::AI_evacuateCity`.

I basically commented-out entirely the "chance of evacuating code" and any "this unit type/unitai should evacuate but not this one" (paraphrased xd), which means that now if city is doomed, we always evacuate ALL land units, which is the best move since city is doomed anyway, why split our troops instead of rather regrouping to core cities and possibly coming back later in the game.

Results are seemingly extremely good!!! Now (see existing screenshots between 213 and 217) our 11 unit stack successfully evacuates the city, and julius caesar ai captures it without blood xd (i think he had lost 1 unit before the change vs our 11 defending units then, still very bad trade to fight it there for us i mean). From there, i continued to autoplay it, and our AI makes a comeback in the game, eventually taking back the city with a strong position. Our AI could do it even after losing the stack (i assume due to julius caesar AI becoming weaker i guess although i didn't check lot), but now that it kept its stack, it seems like the comeback is very strong and earlier than if stack is lost (turns +/- 160 for memory (with macemen so maybe later actually) more or less although i didn't show here the screenshots so you'd have to believe xd me), and game was actually winnable. I mean i had a great position overall and handling if not for this war carelessness, but it's impressive our AI could do it which i am very happy of i may say.

As a side effect, this change might drag games a bit longer (although i didn't test it to know for sure) and i didn't test it too much beyond this sample case where it makes a huge difference, but i think having a more competitive and not stupid but strategic ai is much better.

Issues to fix moving forward would be the weird back and forth of the stack, that attempts to attack again after evacuating, but then withdraws seemingly when it sees target city is too strong, seemingly without attacking but losing 1-2 unit needlessly as a result, very inefficient and needless and ideally i would fix as well but not promised nor guaranteed, i may or may not.

Also, i could tweak this nice evacuating logic because it was already there so thanks to whoever wrote or tweaked it if not base advciv devsand(/but?) i hope it is nicer as such though.

## 63 - (Possibly prevented and possibly fixed) Weird / very inefficient back and forth of going to attack a city stack, and then going back after seeing enemy stack is too strong. I don't know if this change fixes it since the issue was solved without it (2+ autoplay turns were needed at least it seems not 1), but maybe this change in CvUnitAI::AI_attackCityMove helps a lot

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1Beau785h18Pp90KTlkl9F8uCrK_oqL4o?usp=sharing).

Following known issue as of now 62, next issue was to prevent the weird back and forth of going to attack a city stack only to withdraw when seeing the enemy stack is too strong, and losing one or a few units while doing so (potentially a lot more if we can't retreat in time or are ambushed or need to urgently defend cities or such).

As in known issue as of now 62 however though, the behaviour does not happen if i autoplay 3 turns on a row vs 1 more turn from save file after 62 was solved, but still i added a code with the help/recommendation of chatgpt 5 (check if accurate) that seems like a very nice sanity check in `CvUnitAI::AI_attackCityMove` to go attack a city only if the existing `bTargetTooStrong` is false (don't attack too strong cities instead of attacking then withdrawing very inefficiently and in a risky way which makes it even worse).

Since i couldn't test issue here, i don't know if it is solved, but maybe it helps. The issue existed in base advciv too but tedious to especially test it and all, so as it seems harmless, kept as such if helps.

Next related issue would be to prevent julius caesar to declare war on us (15 turns earlier), only to retreat without attacking city, which made him lose the surprise attack effect, have war weariness, and other possible negative side effects, so that we would want to ideally fix if possible (not guaranteed, i may or may not fix it).

## 64 - (Greatly enhanced) AI not razing faraway cities at captures - now we raze them if we are in the early game and they are not close enough, thanks to changes and tweaks in CvPlayerAI::AI_conquerCity

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/18aJH1ncPVVuHTRiqzjPfcSOhCyDVCYeV?usp=sharing).

This is another nice enhancement to AI military/overall behaviour, as of now in `CvPlayerAI::AI_conquerCity`. Now if we capture faraway cities in the early game (as of now first 120 turns adjusted to game speed), even non-barbarian cities, we (i.e. AI players) will raze them unless they are close to us in the early game.

This is because capturing such cities has high cost and low gains especially early:

- we split our military
- higher city maintenance cost across all cities not just this new one (that may cost more if far away) (also regardless of razing we get the gold on capture so not much to do here anymore)
- low yields due to generally low pop or not enough improvements
- even if we have such high pop and improvements, AIs are not too good at spreading forces, often it meant having a big stack stuck in this low pop city and core cities left defenseless. We have added changes in known issue as of now 61 so we dont attack such faraway cities ideally, but if we somehow do in the early game, then raze them rather and favour empire contiguity
- other positive side effects, due to the city being destroyed, the place is not fog busted anymore (although i don't know if barbarian cities count as fog busting xd and prevent random barbarian spawn or not), so if it is far from us, it would or may mean more barbarians for our rivals (which (barbarians) are very strong as of now in advciv-sas (at least quite strong xd)) so this should help us focus our forces and energy defensively and offensively and hopefully lead to better outcomes
- possibly other reasons/advantages if any.

As a result of this, AI should be much stronger due to these saner and more efficient decisions. (note: we don't care if there are wonders or it's a holy city (the barbarian player itself cares to not raze these it seems), but all other players have no reason to care if not profitable to us so they raze cities regardless purely on aforementioned criteria (far enough city and early game as of now for most)).

For example, before our changes, in existing screenshots between 255 and 259, arabia AI captures a faraway (at least more than far enough to be profitable so early i would say) (olmec) city instead of razing it, which is very bad i think, as city won't be profitable until much later, but it weakens economy and military significantly (taking the gold on capture would have been a gain and enough and then razing would have been perfect). Screenshot 259 in particular shows the spots arabia AI is considering at this point of the game around it, and the olmec city was way too far to mesh well with their empire. Destroying it would also (if barbarian cities count as fog busting as i don't know) increase barbarian presence indirectly so would have been nice. So capturing it and committing to it is very bad so early i think in this case at least..

After our changes (existing screenshots between 260 and 261), arabia AI now instead chooses to raze the (olmec) city, which i think is very good and would help it have a much better middle game. Settlers are not so expensive, it's not worth the cost to commit there and so far especially for AIs who would handle it poorly and even if not not worth as is far from them in this case i mean at least.

I continued the game to see what happens a bit (existing screenshots between 262 and 263) (and to see if we still capture some barbarian cities (but also cities of all other players since our code is not restricted to barbarian cities (but the barbarian player doesn't follow such rules of razing if far or not as not relevant to it) only) or destroy them all which would be a bit overkill), and the numidian barbarian city is also razed by Khmer AI, which i think is also good as it is far from him, same as for Arabia AI.

But then a new barbarian city (Phoenician) spawns nearby (of the old numidian city) and this time, still before the early window ends as it's still turn 115 (so before turn as of now 120 we defined as early phase for smart razing), german AI who is close enough to it captures it and does not raze it, which is good as it is close to him so he is likely to benefit from it. Also, it shows our code is not paranoid and still allows close enough cities to be captured, which is good and nice to know! (if i may say). So all in all this seems like a very nice code and enhancement of the AI razing behaviour, which should make AI quite a lot stronger and influence the early game quite heavily:)

Note: some of the changes tweak the old logic to make it less restrictive and raze more often, and some of our additions may also include razing isolated cities like i assume islandic or such in the early game which should be fine considering the high cost to go and maintain presence there, although it might be less optimal for non pangea-like maps but maybe fine as such since is in the early game and we want focus forces and chatgpt 5 helped me lot do all this although i adjusted it too.

## 65 - (Seemingly tremendously improved) Hatshepsut AI who was strongest player at turn 150 is fighting many wars and dies before turn 200: added "emergency peace" sanity pre-checks in UWAI::Team::considerPeace in UWAIAgent.cpp

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1db_VJaAIRCbPlKANob19QrB7LXja72SV?usp=sharing).

This is another tremendous AI improvement it seems.

After making the recent known issue changes, i wanted to test if it had an influence on how things would play out on the old map i tried at first and that i had also tested again more recently after some changes. What i have observed (from turn +/- 60 approximately (a bit before razing olmec city)) now however is that hatshepsut ai takes the lead at turn 150 and is stronger than all other rivals by a significant margin, which didn't happen before these changes.

However, between this now save file turn 150 and (autoplaying 50 turns until) now turn 200 (existing screenshots between 281 and 289), hatshepsut ai who was the leader and possibly likely to win was badly dogpiled by everyone and died before turn 200 actually (despite being strongest leader at turn 150!!).

So to dig why this happened i asked chatgpt 5 to look at the event log screenshots, and based on what it read on them (i didn't read as tedious and bit complicated), this is how it viewed the timeline (check if accurate) (also i formatted it a bit but it's its info (based on my prompts and or such too)):

>awesome set of screenshots — here’s what the event log says happened, in order, and why Hatshepsut went from #1 power at T150 (AD 500) to dead by AD 1350.
>
>What happened (T150 → T200)
>
>- AD 470–520: Hatty fights Germany (Bismarck), peaces out.
>- AD 560: Declares on Kublai.
>- AD 780: You declare on Hatty (later peace at AD 920).
>- AD 800: Declares on Bismarck again.
>- AD 860: Berlin captured by Egypt → Germany moves capital to Hamburg. (This puts a permanent target on her back.)
>- AD 880: Rome (Julius Caesar) declares on Hatty.
>- AD 900: Kublai declares on Hatty.
>- AD 960: Khmer (Suryavarman) declares on Hatty.
>- AD 1040: Saladin declares on Hatty ("at the request of Kublai" → a bribe).
>
>City losses, multi-front:
>
>- AD 1000: Alexandria falls to Khmer.
>- AD 1060: Berlin (Egypt) falls to Rome.
>- AD 1100: Heliopolis falls to Mongolia.
>- AD 1140: Elephantine falls to Khmer.
>- AD 1120–1240: Side stuff (Spiral Minaret; Pacal converts), wars continue.
>- AD 1300: Thebes falls to Rome → Memphis becomes capital.
>- AD 1310: Hatty converts to Judaism (late realignment; AP traffic mentions Berlin and Hindu bloc earlier).
>- AD 1330: Peaces Saladin (too late).
>- AD 1350: Memphis captured by Khmer → Hatshepsut defeated.
>
>Why it unraveled
>
>1) Dogpile trigger: Capturing Berlin (AD 860) made her the common enemy. Within 20 turns she was at war with Rome, Kublai, Khmer, and then Saladin (bribed). That’s 3–4 fronts plus your earlier war.
>2) Religious/diplomatic isolation: The Apostolic Palace is Hindu (built by Bismarck). Kublai had converted to Hindu very early; AP vote text appears later. Hatty didn’t share that religion and only switched to Judaism at AD 1310, long after the dogpile began, so she had no bloc protection and was easy to bribe against.
>3) Frontline collapse sequence: Khmer took the south (Alexandria, Elephantine), Rome took the west/center (Berlin, Thebes), Mongolia took Heliopolis. After losing Thebes, moving the capital to Memphis delayed but didn’t stop the end.
>4) Army shape vs. coalition pressure: At AD 500 her stack was scary (26 LBs, 19 War Elephants, 11 Catapults), great for one front. But against 3–4 civs, you need either rapid peaces/bribes, Vassal mechanics, or concentrated defense; otherwise, cities start to fall piecemeal as happened.
>
>Takeaways (useful for AI tuning, if you want)
>
>- Dogpile detection: If at war with ≥2 neighbors and DoWs keep coming (or bribe messages appear), switch to "survive mode": whip walls/castles/LBs, concentrate stacks, and aggressively buy peace or bribe counter-wars.
>- AP awareness: Heavily weight aligning (or at least avoiding infamy) with the AP religion owner on maps where AP is active; late switches (AD 1310 here) don’t help.
>- After big capture: After taking a rival’s capital (Berlin), temporarily cool wars; otherwise it invites the coalition response we saw.
>
>Net: Hatty didn’t lose because she was weak at T150 — she got dogpiled by a Hindu-AP-centered coalition and was ground down on three fronts over ~400 years.

So based on this, i thought that at first, before fixing the cause (not switching religion to match other leader's religions, although it would make game bit boring if all leaders have same religion but if best move maybe do so), it was a too good opportunity to pass xd to finally fix the too many wars at same time issue and then test it after fix.

So in `UWAI::Team::considerPeace` in UWAIAgent.cpp i added with the help of chatgpt 5 (check if accurate) sanity "emergency peace" pre-checks, so that we make peace urgently no matter what if we have 3+ (see code for details) wars at same time, or if we have 2+ wars at same time but the combined power of our ennemies is > 160 % of our power (e.g. 2 ennemies having 0.8 (= 80% if i'm not mistaken) (or e.g. 0.9 + 0.7, or 1.0 + 1.6, etc.) times our power is enough that combined they would be a threat enough to urgently make peace) then urgently make peace no matter what before they ravage us xd.

The second check is especially good as even if we have 2 wars, if say ennemies have 0.5 0.6 in total it would be only 0.5 + 0.6 = 1.1 times our power so we can handle it fine no need to trigger emergency peace, however 3+ wars alone is already too late by the time we react to that if rivals are strong. So i wanted something hybrid of 3+ wars or alternatively 2+ wars rather if strong threat which i think we do nicely here and simple(also not enough wars would be boring, so i'm glad we have found this middle ground where plenty wars still happen but AI now seemingly nicely handles it seems the multi war threat based on opponents' strength).

Results are extremely good!! As can be seen, starting from same save file at turn 150, in existing screenshots between 290 and 295 (run 1 after the changes) and existing screenshots between 296 and 297 (run 2 after the changes), hatshepsut ai is now still alive and still the strongest, she also made nice military gains, and makes short campaigns by declaring peace not long after war instead of collapsing under too many wars! Her military power shrank a bit relatively to other rivals, but she is still strongest so far and has expanded nicely. It is the result we wanted, of AI being able to keep a lead and not blunder it due to multi wars.

Chatgpt 5 analyzed the event log as such (put run 2 only for concision)

>yep — this second run looks a lot healthier for Hatshepsut. Here’s what the stretched log shows and what it implies.
>
>What happened (T150 → T200)
>
>- AD 470 → 540: Hatshepsut DoW Bismarck, then signs quick peace. One-front skirmish, no dogpile.
>- AD 640: DoW Kublai.
>- AD 680: Mutal falls to Egypt (it was in Kublai’s hands). Clean, early gain.
>- AD 700–820: A couple of short human–Egypt wars/peaces in your log; nothing sticks.
>- AD 900: Apostolic Palace completed (Hamburg). Hindu AP forms; later casts "Stop trading with Hatshepsut" (AD 1140), but it doesn’t derail her momentum.
>- AD 960 → 1120: Hatshepsut DoW Suryavarman, takes Chichén Itzá (AD 1040), then makes peace. Again: decisive hit, then exit.
>- AD 1200 → 1240: DoW Julius Caesar; by AD 1240 she captures Rome (capital), JC moves capital to Antium, and peace the same turn. That’s a huge tempo swing with minimal bleeding.
>- AD 1260–1310: Multiple Golden Ages around the map; no dogpile forms against her.
>- AD 1320: AP vote about stopping war vs Suleiman (not about her).
>- AD 1330: She DoW Pacal II (sequential, not simultaneous).
>
>Why this looks stronger
>
>- She avoids multi-front wars and fights sequential campaigns with fast peaces after big captures (Chichén Itzá, then Rome). That’s exactly the survival pattern we wanted.
>- The AP sanction ("stop trading with Hatshepsut") fires but doesn’t trigger a diplomatic dogpile; she’s already out of the Khmer war by then.
>- Army at AD 1400 is intact and tops the field (scoreboard shows 1345 soldiers vs ~1250 for Saladin/Bismarck). Composition is sensible for the era: 22 Longbows, 16 Horse Knights + 8 Camel Knights, 7 Trebuchets, some Pikes. Not siege-starved, not over-committed.
>
>Did our emergency-peace change help?
>
>Indirectly, yes:
>
>- The pattern you see (decisive capture → quick peace → shift target) is exactly what our "don’t let multi-wars spiral" nudge encourages.
>- Even if the hard trigger didn’t fire every time, the added checks reduce the chance of her continuing a costly war while another one starts.

It seems not important anymore or urgent to fix the cause (religious dogpile) as it adds some game variety, and more importantly in this game hatshepsut ai captured rome ai (surprisingly historically accurate xd although is a random generated map and although i don't know too much this timeline's real history but i know they were invovled with each other on some level) so their holy pagan city synergized nicely with hatshepsut ai's paganism as well, so may be fine to leave as such i don't know for sure, however i had the issue in base advciv of strongest ai switching religion then making an enemy of everyone stupidly so may need some tweaking possibly even though i don't know where but i could use this save file as a base for that maybe (however is not guaranteed i may or may not do so).

As for this change of seemingly much better"emergency peace" prechecks, AI should be much stronger as well thanks to these hopefully and possibly be better at keeping its lead while still keeping the ability to bully the weak (i.e. many weak players) in multi wars for its interest (e.g. shortly before turn 200 hastsheput ai goes at it again and declares war on pacal 2 ai who was dying anyway and who is nearby so nice gain for her and safe as well).

## 66 - (Fixed and greatly enhanced) AI overvaluing bonuses that give minor effects such as pig or cattle/cow (+1 health only), etc, that AI would value the same as maize or wheat (+2 health effectively since almost all cities have a granary and very early) or grapes (from grocer) or molluscs (from harbor) for example, by adding a pre-check in CvPlayerAI::AI_bonusTradeVal to value relatively more bonuses the more effects they provide from buildings if we have their required tech of these buildings, so that humans can't abuse/exploit it with aggressive trading to become super rich xd, and also in AI vs AI trading each AI gets best or more value out of the effective value of their bonuses at least more so now

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/13hSTVD9mOWRkaCnS3Z21s-8tbYaBr3Sf?usp=sharing).

This is another nice AI improvement and a critical as in annoying issue base AdvCiv +/- civ4 AI had, that was that it was way too easy to abuse its early trading, because it gave the same gold per turn for for example pig (that gives only +1 health) than for for example maize or wheat (that give almost always +2 health since almost all cities have a granary very early in the game), so wheat should be more or less double the price of pig, not same price (e.g. it should be 4 gpt for maize/wheat vs 2 gpt for pig/cattle).

Thanks to these changes, AI should have a much stronger opening and midgame, not only in human vs AI trade where the human can no longer run away, but also in AI vs AI trade that now lead if i'm not mistakento fairer trades (AI actually gets value from its maize vs another AI and doesn't throw it away for something cheap like cow or something ideally). This is not always applied in some cases it seems, but most often is.

Note: there are several nuances to this, not all detailed (see code for the changes in as of now `CvPlayerAI::AI_bonusTradeVal` for details), but mostly:

- not applied to wonders so we save computation plus they are not built in all cities so even if a wonder gains effects from bonuses, it's only in one city more or less and simpler to handle as such
- not applied to cathedrals as it is a rare building
- simplified for temples and monasteries as not that many religions are in a game, and even if that would be the case, generally AIs woudn't build 7 temples in all cities so fine to handle as such to simplify.
- applied less strictly to coastal buildings, as not all cities are coastal even in water heavy maps, but some may be so give a little extra value for the bonus in trade but not as much
- as a part of applying these changes, bonuses now value slightly less than before, to nerf a bit the too easy trading, and also make maize not become too expensive especially early on.

All in all, in ingame testing, we get reasonable, not too cheap nor too expensive anymore prices, that seem to scale well enough into midgame (since we only added a pre-check as we usually do xdand didn't rewrite all hehe).

Hopefully AI should be stronger, or perhaps human weaker, however it may also make trading more strategic, since some bonuses are more expensive now like maize, while others should be cheaper like pig, possibly iron too if it doesn't provide building specific extra effects (like +1 happy or +1 health for example), which is maybe fine as iron is not strictly mandatory although nice to have, and the human player could have gotten a bit too much value out of it maybe. I tried to make it so price is not too low, but didn't want to exclude it either to see how it would be, maybe it would be fine as such.

Also, code added with the help of chatgpt 5, check if accurate and thanks a lot chatgpt 5.

## 67 - (Fixed/Enhanced) An ancient maceman 18 hammer costs 20 hammer ingame, and a swordsman 42 hammer costs 40 while a swordsman 43 hammer costs 45 which is a mess. Fixed by removing per 5 rounding in CvPlayer::getProductionNeeded and other related functions/issues

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1JkBWnedqChDH-PSqIle-eQYwHV6tume1?usp=sharing).

It was very very annoying, thankfully i mean now fixed/corrected in advciv-sas.

Now all players, be it human or AI, have a 1 hammer rounded production (units, buildings, projects (all in `CvPlayer::getProductionNeeded` functions if i'm not mistaken)) cost, or tech, great people, or such other costs too or not or etc it seems (`CvPlayer::greatPeopleThreshold` and `CvPlayer::getNewCityProductionValue` and `CvTeam::getResearchCost`).

Example of code:

```cpp
roundToMultiple(/* advc.251: */ isHuman() ? 5 : 1);
```

now as of now replaced (with the help of chatgpt 5, check if accurate) with a simple:

```cpp
round();
```

Also what was even more annoying is that even outside of handicap or such settings, the price change would still apply and only the to the human player, so AIs effectively have a different price than the human player, very very annoying and no setting to manage this outside of DLL.

I don't know what intent was, insanity, or maybe more honestly or fairly i guess making it prettier to the eye xd, but fuck that i really don't care xd. Since i find it nonsensical and don't care about pretty numbers in this case at least, disabled it entirely.

Hopefully clearer/saner less frustration generating/inducing xd, also i find it cool to tweak per hammer costs like 40-41-42-43-44-45 vs 45 or 40 so i find it nice to be able to do so, and am glad it is restored as such.

## 68 - (Tremendously Improved) AI having a settler parked from turn +/- 45 to turn 100 and still didn't found any city, fixed/addressed in CvUnitAI::AI_found

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1Eip4H2dji_1fxmw2HmShhoa_1I4JnISF?usp=sharing).

For some reason we were very slow to produce our first settler after the change, but after we had our first settler, 2nd spain AI city was founded soon after which is nice and addresses this issue: we now have 3 cities at turn 100, and so do other ais more or less as well, which seems like a nice and quite safe enhancement since cities seem guarded more than enough (2 units per city it seems) but check to be sure as i only glanced through autoplay

## 69 - (Tremendously Improved) AI going for great general leaders, while military instructors are much better (with added logic to favour top hammer cities, remove military instructor per city limit, favour it further if have or building heroic epic effect building, etc.)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1k42nIibXMMDUeJOedCEnrwUMGBFWem9J?usp=sharing).

Changes thanks to claude sonnet 4.5 and chatgpt 5, in `CvCityAI::AI_permanentSpecialistValue` and `CvUnitAI::AI_generalMove`.

I have noticed AI goes for great general leader, when it is much better to go for a military instructor that would scale throughout the game, and in top hammer cities, especially if they have heroic epic. Plus removed the military instructor per city limit. Results ingame are very good.

## 70 - (Seemingly fixed) Base advciv bug of forcing an artist specialist even if it is invalid and then firing a failed assert, in CvCityAI::AI_assignWorkingPlots

See code comments i.e. in `CvCityAI::AI_assignWorkingPlots` there for details, seemingly now fixed with the help of chatgpt 5 and my prompts or such, check if accurate.

Update/note: most likely was caused by the forced artist code we added (see [Specialists (AI)](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md#specialists-ai) for details), although i am not totally sure, as it fires only for artists, and in the early game only in first turns, which aligns with it stopping to fire after we have our BFC, which is when we stop forcing an artist in our code and so it seems likely our code caused it and not base advciv itself, although this is just a guess of mine so check to be sure if want. Still, this is a nice fix and guard to have regardless as sanity i'd say maybe if i may say and guess i mean, but i don't know too much about these, also the extra assert info in the message detailed i mean is nice too.

Update 2: significantly reduced the invalid artist being forced issue by obviously adding an invalid specialist check.. (`isSpecialistValid`) before forcing an artist or unforcing one. Obvious but which i had no idea of xd. For some reason did not entirely disappear but fires much less now with these added.

Sometimes with a debug DLL it still fires as such though as of now:

```txt
Assert Failed

File: ..\.\CvCityAI.cpp
Line: 230
Func: CvCityAI::AI_assignWorkingPlots
Expression: isSpecialistValid(e)
Message: T100 Rheims SPECIALIST_ARTIST e=2 value=1
```

But should be better than what it was and should have been added as a pre-check as chatgpt 5.1 recommends as well (and which was my mistake) thanks.

Also, according to chatgpt 5.1, these asserts firing are no longer the result of issues with our code and may be fine (check if accurate as i don't know too much about these), so treated as not a bug for advciv-sas (ideally would find how to silence the message if it is really safe but not a priority i mean):

>So, short version: that Rheims T100 assert just means:
>"Rheims still had a forced artist recorded at a moment when no artist was legally allowed there anymore."
>It’s not your original BFC-artist bug coming back; it’s a side-effect of the general forced specialist mechanism being a bit looser than the invariant your assert is trying to enforce.

It thought for almost 13 minutes with the relevant .cpp files so i'd tend to think it is accurate, check to be sure.

## 71 - (Seemingly fixed) Base advciv bug of calling CvBuildInfo::isFeatureRemove when eFeature is not a valid feature, then firing a failed assert

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1grZBqkHYUqtXAhdqRxpSqqa759_Q7gsI?usp=sharing).

WinDbg !analyze -v result viewable in .txt as of now at above link for reference i mean(full dmp with a debug dll (i don't know too much about these so check if accurate and if i did it correctly i mean, with chatgpt 5's help and review as well thanks i mean too)).

See code comments there i.e. in `CvBuildInfo::isFeatureRemove` for details.

## 72 - (Seemingly fixed/addressed) Base advciv bug of calling getInt in CvRandom.h when iNum is negative, then firing a failed assert

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1oWBp58ADUKAHAAUnXGIARciHF47ncuW8?usp=sharing).

I patched 3 locations in `CvCityAI::AI_chooseProduction` and 1 location in `CvCityAI::AI_bestBuildingThreshold` that caused the assert to fire i mean, but i may have missed some, so i hope the general extra assert (if iNum is negative if i understand it correctly) we added in `getInt` with chatgpt 5 i mean thanks i meanwill be helpful to spot other similar issues.

WinDbg !analyze -v result viewable in .txt as of now at above link.

See code comments there i.e. in `getInt` in for details.

## 73 - (Seemingly fixed/addressed) Base advciv bug of calling scout units stuck in a loop related to iAttempts and iMaxAttempts in CvSelectionGroupAI::AI_update, then firing a failed assert

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1wkIJ-7KouMqDezmXmY_hlpmyk2vajrye?usp=sharing).

WinDbg !analyze -v result viewable in .txt as of now at above link.

See code comments there i.e. in `CvSelectionGroupAI::AI_update` in for details.

## 74 - (Seemingly fixed/addressed) Base advciv bug of AI_bestSpreadUnit returning true even if eBestSpreadUnit is NO_UNIT, then firing a failed assert

See code comments there i.e. in parent callers in `CvCityAI::AI_chooseProduction` and `CvCityAI::AI_buildGovernorChooseProduction` in for details.

## 75 - (Tremendously Improved) AIs autopicking civic_emancipation (iCivicPercentAnger) just because other rivals have it regardless of how good the civic itself is. Now replaced with opportunistic current unhappiness per city-based logic if it benefits us, in CvPlayerAI::AI_civicValue

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/16vQkp1ow6sy2Bi99M02HbHMPpFDU9Q1h?usp=sharing).

AI had an issue of seemingly tremendously favouring the former civic_emancipation i guess because of the `iCivicPercentAnger` as chatgpt 5 assessed as per its review (check if accurate), but the problem is that the civic itself was really bad. Just because we'd have some rivals run the civic is no reason to urgently switch to it. Only do so if our cities are unhappy because of this effect rather. Else, keep other civics like as of now civic_caste_system or anything else, unless the civic_emancipation is by itself better (e.g. due to other effects if reworked, etc).

As can be seen in screenshots before/after, AI went from always picking the former civic_emancipation after a few first pick it to now depicking it even if some rivals have it.

To be good, the civic would need to be reworked, and not just picked because other rivals have it, else AIs would make a weak choice vs humans who would value say civic_caste_system or such. Hopefully AIs should be stronger as such, and may open the door to some civic balance.

## 76 - (Tremendously Improved) AIs almost always picking civic_caste_system and then almost never changing it no matter what (unlimited specialists logic favoured only culture as well and much needed an improvement and generalization), in CvPlayerAI::AI_civicValue

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1GLf_a49yosoDPFnFeO9Gh3qFOvBm83_V?usp=sharing).

AI had an issue of seemingly tremendously favouring civic_caste_system, and then sticking to it no matter what almost always.

The code in `CvPlayerAI::AI_civicValue` was itself claiming to be bad and to be ideally changed, and from what i understood of it only accounted for culture, making our rework of the now civic_wage_labor that as of now gives unlimited engineers no valued and in autoplay never picked ingame.

So rewrote the logic to now value yields and commerce hierachically (i checked and the word exists), so that for example a specialist giving food is x3 value per yield vs x2 per yield for a specialist giving hammer, and similarly a specialist giving beakers is much more valued per commerce than a specialist giving culture.

Also added high need logic for culture (quite similar to previous code) and for hammer (new: if enemy is strong, value hammer more on a per yield base).

Added logic to tone it down a bit as we were switching a bit too much, now based on anarchy turns cost.

Results in autoplay are very very good i mean. Now even in the early game we go back and forth between caste system and slavery, and later on serfdom and in particular finally our civic_wage_labor is now quite popular among ais, and the distribution is quite even.

Ideally i'd find ways to prevent oscillation or excessive oscillation at least maybe, but hopefully AI should be much stronger and responsive to change (no point to run scientists if we are about to be steamrolled, value engineers or serfdom or such more i mean maybe).

## 77 - (Improved) Devalue researching techs our master or vassal(s) already knows as this is very inefficient

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1oy_TaNgXpqxxCU5rYUxbqRCL6V_4VkNa?usp=sharing).

We have an issue of AI researching techs its vassal already knows which is very inefficient. In this save file Hammurabi (vassal of Ewuare) is way ahead in tech; it seems at a quick glance Ewuare re-researches many techs Hammurabi already owns, which is very inefficient and suboptimal.

Added code with the help of chatgpt 5.1 in `CvPlayerAI::AI_techValue` to devalue these techs since we can get them from our vassal, and vice versa for the vassal since they can get said techs from the master as well, tunable in sas defines as well.

Ideally, would also implement preferential trading with our vassal/master as is more competitive to win, but not done in this known issue.

Results in autoplay are hard to evaluate as history changed after applying this change, and Ewuare and Hammurabi took a different path, and Ewuare snowballed and won sooner as well.

Would need to implement preferential master<->vassal tech trading of techs they can get from each other to see if it helps further.

Update: after [KI#78](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#78---improved-trade-techs-preferentially-with-our-vassals-or-master-synergises-with-the-no-overlap-previous-master-vassals-tweak--add-a-second-parameter-now-ai_contactrollcontact_trade_tech-rcontactprobmult-to-have-a-more-dynamic-tech-trading-not-only-based-on-personality-according-to-chatgpt-51-and-then-corrected-by-claude-sonnet-45s-review-check-if-accurate)'s change, also added vassal<->vassal(s) siblings devaluation to self research logic, since Ewuare has 2 vassals at t250. Results in Ewuare having 2 more techs and 1 less tech at t300, and Hammurabi having 0 more techs and 1 less tech. Would need to implement this idea on the tech trading side as well to measure the full impact on this save i mean even though some random fluctuation might happen more or less unpredictably or unreliably or such.

## 78 - (Improved) Trade techs preferentially with our vassal(s) or master (synergises with the no-overlap previous master<->vassal(s) tweak) + add a second parameter now AI_contactRoll(CONTACT_TRADE_TECH, rContactProbMult) to have a more dynamic tech trading not only based on personality according to chatgpt 5.1 and then corrected by claude sonnet 4.5's review (check if accurate)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1a1eEd0iAaTXNsBSrz_NF6NRFZOgP12kP?usp=sharing).

Following [KI#77](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#77---improved-devalue-researching-techs-our-master-or-vassals-already-knows-as-this-is-very-inefficient), also added logic so that master<->vassals are much more inclined to trade with each other, not just for techs they don't have, but for any tech. This synergises and expands on this previous change, in `CvPlayerAI::AI_doDiplo`.

Also changed the `AI_contactRoll(CONTACT_TRADE_TECH` to now include a second already computed `rContactProbMult` parameter (instead of the default of 1 in the header file) so tech trading is more dynamic and not only based on personality.

Rationale for the change below:

```cpp
					// <!-- custom: according to chatgpt 5.1, the missing 2nd parameter is a bug specifically here for this contact roll so adding it, check if accurate -->
					// So:
					// 	- Calls with 1 argument → use the base personality contact frequency only (no extra multiplier).
					// 	- Calls with 2 arguments → same base, scaled by rMult.
					// That’s by design. You only use rMult where you want to condition the probability (e.g. on tech rank, UWAI, diplo stage).
					// What about CONTACT_TRADE_TECH in particular?
					// The key point:
					// 	- AI_contactRoll(CONTACT_TRADE_TECH) is still being called without rContactProbMult.
					// So:
					// 	- All the logic that computes rContactProbMult (tech rank, space stage, and your vassal/master defines) is currently ignored.
					// 	- This was already true before your changes (the K-Mod / AdvCiv code built rContactProbMult here but never passed it in), so yes, this looks very much like an old oversight.
					// 	- Other contacts like CONTACT_ASK_FOR_HELP do pass it:
					// So for your specific feature (making master/vassal talk more about tech), you do want to change this one line.
					// That’s enough to:
					// 	- Activate the old BBAI/K-Mod "we’re behind in tech → roll more often" logic.
					// 	- Make your MASTER_TO_VASSAL / VASSAL_TO_MASTER defines actually matter.
					// No.
					// 	- Calls that don’t have a local rContactProbMult (PEACE_TREATY, RELIGION_PRESSURE, TRADE_BONUS, etc.) are not bugs; they just use the plain personality ContactRand, which is perfectly fine.
					// 	- Some places (e.g. JOIN_WAR, ASK_FOR_HELP, DEFENSIVE_PACT) purposely compute an extra multiplier and pass it in.
					// 	- UWAIAgent uses AI_contactRoll only for certain demands/pressures with its own multipliers; it’s separate and already consistent.
					// So the only "suspicious" one from your grep is CONTACT_TRADE_TECH, because:
					// 	- there is a rContactProbMult built right above, and
					// 	- it’s never used in the call.
					// That’s why I’d treat that one as an old omission and wire it up, and leave all the other 1-arg calls as they are.
					// Short answer
					// 	- The previous logic was already "faulty" / incomplete before we added any master–vassal stuff.
					// 	- Our new master–vassal tech-trade boost just depends on the same multiplier, so fixing it became important for our feature to actually work.
					// 	- But the "bug" (building rContactProbMult and then not using it) was already there in the inherited code.
					// Before
					// if (AI_contactRoll(CONTACT_TRADE_TECH))
					// After
					// <!-- custom: update: not a bug according to claude sonnet 4.5 and purposeful design, still seems to suit us better as such for our needs so kept as such to have dynamic tech trading, and in autoplay tech pace is not drastically different; check if accurate -->
					// Since there's a check if (rMult == 1), and calls without the 2nd parameter work, the default must be rMult = 1 (defined in the header file, likely as scaled rMult = 1).
					// So when you call AI_contactRoll(CONTACT_TRADE_TECH) without the 2nd parameter, it uses rMult = 1.0 (no modification).
					// Can your rContactProbMult be LOWER than 1?
					// Yes, absolutely! Let's trace through the values:
					// Starting value:
					// scaled rContactProbMult = 1;
					// Tech percentage adjustment (BBAI/K-Mod):
					// If iTechPerc = 80:
					// rContactProbMult = 100 / (10 + 80) = 100/90 ≈ 1.11 ✓ (higher)
					// Space victory:
					// This increases it further. ✓
					// Your master/vassal multipliers:
					// These increase it. ✓
					// BUT - Your power bias can REDUCE it:
					// This is LOWER than the default 1.0!
					// Impact on tech pace:
					// Your changes create a more nuanced system:
					//
					// ✅ Faster within master/vassal clusters (3x contact rate)
					// ✅ Faster when behind in tech (up to ~1.67x)
					// ✅ Faster when pursuing space victory (1.33x)
					// ❌ Slower against stronger rivals (0.8x)
					// ❌ Faster against weaker rivals (1.2x)
					//
					// Net effect: Probably still faster overall, but with strategic differentiation (avoid empowering strong rivals, exploit weaker ones). This is actually quite intelligent AI behavior!
					// The original AdvCiv design avoided this complexity by keeping tech trade frequency constant. Your design adds strategic depth.
```

In autoplay, from turns 250 to 300, the master (Ewuare) has 4 more techs and only 1 less tech than before this change, which is a massively faster tech pace!!

As for hammurabi (vassal of Ewuare), he has 2 more techs and no tech less, so this is also significantly faster tech pace.

All in all, it looks like they mutually benefited from this change, be from the preferential trading change, or the contact_tech_trade bugfix (i don't know which, the results are very good!), which is a massive improvement!

Update: after [KI#77](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#77---improved-devalue-researching-techs-our-master-or-vassals-already-knows-as-this-is-very-inefficient)'s update change (vassal<->vassal change/addition), also added vassal<->vassal(s) siblings extra tech trading chance similarly, since Ewuare has 2 vassals at t250. Results in Ewuare having 1 more tech and 1 less tech at t300, Hammurabi having 0 more techs and 0.5 less techs, and Rameses 2 (the other vassal at Ewuare) having 0 more tech and 0.5 less techs at t300. So seems more or less identical in this run/map possibly due to noise/variation. As long as not clearly detrimental, may be fine to add since this only boosts contact and does not reduce it which might have then led to possibly less predictable results i would guess (like it being detrimental or possibly beneficial more situationally or such) but not the case here so adding this i think.

Update 2: with more autoplay testing, tech pace seems mostly overall same (not much faster nor slower, but now takes into account our dynamic conditions (master-vassal(s), military power, etc.)), see code for details.

## 79 - (Improved) Before contacting other players for tech trades, first check if we don't already have the tech in our master-vassal(s) locus, and if so don't contact the other players

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1mv377xdPwZFVtOqVZdMAzEqIBdFCktHC?usp=sharing).

After [KI#78](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#78---improved-trade-techs-preferentially-with-our-vassals-or-master-synergises-with-the-no-overlap-previous-master-vassals-tweak--add-a-second-parameter-now-ai_contactrollcontact_trade_tech-rcontactprobmult-to-have-a-more-dynamic-tech-trading-not-only-based-on-personality-according-to-chatgpt-51-and-then-corrected-by-claude-sonnet-45s-review-check-if-accurate)'s update change, it still seems we are slow to trade military science (for dragoons) to our master, even though rameses vassal has it long ago.

Added with the help of chatgpt 5.1 logic in `CvPlayerAI::AI_doDiplo` so that before contacting a player for any tech trade, we first consider if the tech does not already exist in our master-vasssal(s) locus, and if so do not contact players that are not part of it. Hopefully this indirectly helps contact players of our locus first for a tech we don't have.

In autoplay, the results seem very good, we win sooner seemingly due to our master Ewuare upgrading much sooner to dragoons (which he has 150 of (+ 103 cannons as well) at turn 300!) (win at turn 294 vs turn 305-335 in various previous changes). As for techs Ewuare has 2.5 more techs and 3 less techs, Hammurabi has 0.5 more techs and 0 less techs, and Rameses has 1 more tech and 2 less techs. All in all, this seems to greatly benefit our locus.

Note: it is tricky to determine if this change is in the interest of the vassal or not. Because it might be in the interest of the vassal that its master grows weaker, perhaps to free itself from its master (if not voluntary vassal as as of now in advciv-sas these are permanent). But at the same time, vassal would be force involved in any war the master wages or is victim of, be it a winning or a losing one. And reliably gaining things from a close-knit partner involvment i mean doesn't seem too bad. All in all or overall, it may possibly, generally be in the best interest of the vassal to help boost its master in hopes of indirectly benefitting from it, rather that hoping for its demise in a way that would not affect the vassal as well, which seems quite unlikely.

I asked chatgpt 5.1 about this which said:

>In pure theory, yes, a vassal might sometimes benefit from a weaker master to break free.
>
>In Civ4 as it’s actually structured, and especially for AI:
>
>The vassal’s day-to-day best interest is to have a strong, tech-advanced master who:
>
>- Protects it,
>- Wins wars,
>- And makes the cluster hard to exploit.
>
>So your current master–vassal cluster-first tech logic is fully consistent with a sane vassal "interest model" in this engine.

Similarly, a stronger vassal is also more likely to be more useful to its master, as gemini 3 pro highlighted when i asked it about it:

>The Master's Calculation: "The Force Multiplier"
>The note states the goal is to "strengthen overall AI play". In a strategy game like Civ4, a weak vassal is a liability—they get invaded easily, dragging the Master into wars, and they contribute nothing to the war effort.
>
>Rational Logic: By sharing tech, the Master isn't being "nice"; they are upgrading their own buffer state. A Vassal with Riflemen (via trade) can actually defend the Master's borders, whereas a Vassal stuck with Longbows is just dead weight. It turns the Vassal into a functional asset.

So all in all it does seem like a suitable change in most cases to bet on i mean.

## 80 - (Tremendously Improved) AI contacting for tech trades players that are stronger even though this is more likely to be detrimental

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1XY87DcUJtJJIHqit_6qwNl09eWnqosso?usp=sharing).

AI seemingly had no restriction on who it preferentially initiated contact with. However a stronger rival is more likely to be an enemy later, while a weaker one is more likely to be harmless and someone we can (more safely at least) rely on or use for our advantage.

Added military power stronger/weaker to us modifiers to tech trade contact chance in `CvPlayerAI::AI_doDiplo`.

Note: does not apply if between members of a master-vassal(s) locus.

The effect seems extremely positive and helpful to AI strength, although this is just one autoplay before/after sample and there could be noise, but what seemed to happen is that unlike before the change where Ewuare quickly took a lead and became unstoppable and snowballed to win easily at turn 288, after this change it seems now that anytime a player would take a military or score lead, somehow this score started to shrink and others caught up. It also seemed that weaker rivals were closer at a glance, at least early on. Ewuare eventually won but only at turn 419, and even at turn 300s the game was more or less even between a few rivals/blocs and very close.

So this seems to help a lot, although it could just be noise, but it does not seem to be a clearly harmful change so implementing it as such.

## 81 - (Tremendously Improved) AI not valuing military techs for research enough when weaker

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1d_UFDfZ76O1nY8FEZFa-Yh1NCBMN3dfa?usp=sharing).

AI seemingly was often too slow or straight up not valuing for research key military techs (with a high enough FLAVOR_MILITARY, see sas defines for details) at all, even when it was weaker and at risk of dying (economy or such techs would be useless to it at best, and at worst they would be researching them for their ennemies when they conquer them (kind of like how AI used to do/be for wonders before our changes i mean.)).

After our changes in `CvPlayerAI::AI_techValue`, game changed from Ewuare winning at turn 382 quite hardly (but still as he always did in many runs so far) to him finally losing to Saladin and Rameses despite Ewuare having an initial early lead (but that he could not sustain after our changes it seems), and the game being even closer, and at a stalemate even at turn 400s between Saladin and Rameses who controlled about half the world each (Saladin eventually won a Space victory at turn 469 and was seemingly stronger eventually even though this was shortly game would have otherwise ended on time not long later).

This seems like a good AI improvement at least based on this autoplay comparison sample, and at least a nice sanity to have for AIs.

## 82 - (Tremendously Improved) AI not adopting the popular religion among strong rivals, thus being hated and more likely to lose

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1nqXsaX5ZFq550fHe7r6NwPfY2ZhQpIHE?usp=sharing).

This is a long standing issue i had noticed in base advciv when i was still playing it. (that i had named example example 110), see for details the list of base advciv issues i had compiled as in listed gradually here in [this CFC forum post](https://forums.civfanatics.com/threads/ai-city-placement-and-misc-suggestions.695343/page-7#post-16782814) i made.

Now this seems properly fixed, at the cost of less roleplay, but much saner behaviour (partially tunable).

Previous logic was seemingly very suboptimal, as per claude sonnet 4.5's below explanation below (check if accurate) as i asked it aobut it about whether i understood its explanation correctly it nicely confirmed and enhanced/detailed it as such thanks:

>The Fatal Flaw:
>Attitude gate: Only civs you already like (PLEASED+) contribute to diplomatic value. This created:
>
>- Circular reasoning: "I only value religions of civs I like" → "But I can't become friends because we have different religions" → Deadlock
>- Power-blind: A friendly weakling counted the same as a friendly superpower (both +2)
>- Randomness from attitude: Early-game random attitude modifiers (different religions, border tensions) could cause the AI to ignore the "correct" diplomatic religion, then get locked into the wrong choice

The difference is very stark, with now AIs dynamically and reliably (at least much more so than before), gradually aligning with whatever religion is popular among top dogs (which varies a bit during the game but seemingly often gradually converges), which is stronger as we won't be hated on diplomacy (so more trade opportunities, less wars as well if i'm not mistaken, etc.) but with less roleplay though, so hopefully AI is stronger as such.

Change with the help of gemini 3 pro and claude sonnet 4.5 in `CvPlayerAI::AI_religionValue`, and to a lesser extent of chatgpt 5.1 thanks to all i guess i mean maybe hehe but in all cases.

Note added by chatgpt 5.1 about the scope of this change as i asked it about it thanks, check if accurate:

>So for the doc later you can roughly say:
>
>AI_religionValue: central heuristic for how valuable each religion is as a state religion (internal happiness/culture + holy city + diplomatic blocs). It drives:
>
>- AI choice of state religion and conversion timing.
>- Trade / demand value of "adopt religion X".
>- Espionage value of "change target’s religion".
>- Indirectly, the evaluation of state-religion-dependent civics via AI_bestReligion.
>
>Which means your power-weighted change is now shaping both their self-religion choice and how they respond to external pressure.

## 83 - (Tremendously Improved) AIs not trading techs more aggressively and cheaply when rivals discover them too and there is a risk they will beat us to the sale, leaving us with nothing rather than little gold or such which would have been much better

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1h3puw0vWwDHkhgydMGN6PXcl3BXkFeoH?usp=sharing).

This is one of the key issues the AI had in base advciv as well, of not trading oppornutistically way more cheaply when other rivals also discover the tech and could beat us to the sale. Even if the tech was worth say 200 gold, it's better to have 20-30 gold off (or of? Or something else?) it rather than 0 (no advantage in keeping the tech since other rivals can profit, better sell it then).

Added such a change with the help of gemini 3 pro, in `CvPlayerAI::AI_dealVal`.

Results ingame are very good, with all players having a significantly higher score at turn 100 and 200 vs before, and most players having a faster to more or less much faster tech pace.

It seems that untradeable techs help pacing not go too crazy, and maybe in later game (untested) the no AI gradual multipliers per turn or era or such not being in our mod helps control AI pace better so no need to overcorrect it just quite a bit it seems, and as gemini 3 pro suggested as well thanks.

I adjusted `iAIResearchPercent` to match these changes:
iAIResearchPercent,124,116,108,100 (noble),92,84,76,68,60
->
iAIResearchPercent,118,112,106,100 (noble),94,88,82,76,70

## 84 - (Added missing feature) Rivals of the active/human player that are willing to become the active/human player's vassal not showing an icon to quickly indicate that at a glance, in the Foreign advisor's glance tab (no pun)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1Oy-oD3VUPzOXwFCGXL_EqZlPF3D8m5Q5?usp=sharing).

This is another very nice feature that was missing in base advciv 1.12 and very tedious to check or making sure to not having missed it, which is if rivals are willing to become rival to us, the human player.

I had noted the issue as example 145 in base advciv 1.12 issues i had listed gradually here in [this CFC forum post](https://forums.civfanatics.com/threads/ai-city-placement-and-misc-suggestions.695343/page-7#post-16782814).

Now added with the very nice help of gemini 3 pro and claude sonnet 4.5, in [CvForeignAdvisor.py](/Assets/Python/Screens/CvForeignAdvisor.py), with as of now a star icon for players who want to become vassal to us, and as of now a strength icon if they are our vassal.

Update: now also added a tooltip (on hover), in [CvDLLWidgetData.cpp](/CvGameCoreDLL/CvDLLWidgetData.cpp) with gemini 3 pro's help as well thanks.

And now also using our own advciv-sas save file (see drive link for details)

Trick: autoplay on settler we are more likely to be stronger and thus to have rivals, helped quickly get a save file sample for screenshots and testing.

Update 2: now added to a helper (`CvDLLWidgetData::parseVassalWillingnessHelp`) to avoid reuse and as is cleaner as such i mean, with gemini 3 pro's help as well thanks.

## 85 - (Corrected Explanation) BUG Tech Advisor's Bulbing Indicators causing preGameStart (CvAppInterface) error at turn 0 so as in base advciv it is disabled at this turn and enabled only from turn 1 onwards, but base advciv's explanation about it affecting very large maps was incorrect: happened on a standard size map as well

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1cg05BVD4Jrs4hnbaaniNpitdgRIrfSHL?usp=sharing).

In [CvTechChooser.py](/Assets/Python/Screens/CvTechChooser.py), base advciv disables the BUG's tech bulbing indicators (that come from RFC DOC's mod btw according to base advciv comments as well if i understood it correctly, and if there weren't, i was going to take them from RFC DOC as well as they look nice there as well thanks! I mean.) at turn 0 with the following rationale:

```py
		# advc.004a: Adding this guard b/c the new code somehow can't handle calls via preGameStart (CvAppInterface) if the map is very large. Still seems to get updated properly if the player opens the Tech Advisor on turn 0.
		if CyGame().getElapsedGameTurns() > 0:
			self.updateTechPrefs()
```

I tried disabling it to see to players that the feature exists since turn 0 in case they don't see it, and i myself didn't even know about it so i wanted to share it, however eventually got a crash as base advciv's note says, so i disabled it again, now only active from turn 1 or higher.

However, there is a mistake in base advciv's comment which is that it also happens in smaller sized maps, for example i could reproduce this if i remember it correctly. while creating a new game pangea noble standard size map normal game speed.

Based on gemini 3 pro's comment, the error message (see drive link above or excerpt below) was indeed caused by this code i had commented out, and not by another change i made (check if accurate).

For concision, i put the rationale here since the issue is solved, no need to clutter the code there, and it is also more easily visible for modders or such as well hopefully maybe i mean as well but in all cases.

```py
		# advc.004a: Adding this guard b/c the new code somehow can't handle calls via preGameStart (CvAppInterface) if the map is very large. Still seems to get updated properly if the player opens the Tech Advisor on turn 0.
		# <!-- custom: note: trying to comment out the turn > 0 check below. to have our indicators at turn 0 seemingly does indeed lead to an error. However the base advciv's comment is slightly mistaken it seems if i'm not mistaken, as i could reproduce it for example when creating a new game noble pangea normal game speed standard size. As per gemini 3 pro, the error i had was indeed caused by this, so reverted it to base advciv behaviour (i thought the bug info would helps players unaware the feature of BUG's bulbing indicators (including me i mean, i didn't know about it so wanted to share it.; i hope the note helps in our various docs mentionning this)). See for details known issue as of now 85 -->
		# <!-- custom: as for this feature, it seems to me that this is safer to simply disable it (i.e. keep base advciv code as it was), and this feature (turn 0 bulbing indicators) is definitely not critical nor mandatory enough to justify this, so reverted it to how it was -->
		# 
		# The error AttributeError: TechPrefs instance has no attribute 'lTechsByFlavor' occurs because the game attempts to update the Tech Preferences during the initialization phase (preGameStart), before the necessary data (like the Active Player's tech state) is fully ready.
		# The code you uncommented to enable "Turn 0" support removes the safety guard if CyGame().getElapsedGameTurns() > 0:. Without this guard, updateTechPrefs runs too early during map generation and crashes because the TechPrefs object is created incomplete (missing lTechsByFlavor).
		# To fix this while keeping the Turn 0 feature, you should add a safety check inside updateTechPrefs to abort gracefully if TechPrefs is broken, rather than crashing.
		#
		if CyGame().getElapsedGameTurns() > 0:
			self.updateTechPrefs()
		#
		# Traceback (most recent call last):
		# File "BugUtil", line 677, in <lambda>
		# File "BugEventManager", line 668, in preGameStart
		# File "CvAppInterface", line 70, in preGameStart
		# File "CvScreensInterface", line 94, in showTechChooser
		# File "CvTechChooser", line 354, in interfaceScreen
		# File "CvTechChooser", line 366, in ConstructTabs
		# File "CvTechChooser", line 411, in DrawTechChooser
		# File "CvTechChooser", line 1296, in updateTechPrefs
		# File "TechPrefs", line 181, in getNextResearchableFlavorTech
		# AttributeError: TechPrefs instance has no attribute 'lTechsByFlavor'
		# ERR: Python function preGameStart failed, module CvAppInterface
```

Hopefully regardless of which, this helps document and confirm the issue, as well as giving players info in other related docs on the existence of the BUG tech bulbing indicators and how to enable them, in case they didn't know about them.

Update: somehow sometimes they appear at turn 0 and sometimes not, what matters is we reverted to base advciv code as the key information there i mean. and that code seemingly no longer crashes now. It also did happen on a standard size map if i remember it correctly not just very large ones, and works fine as is now so leaving it as is.

## 86 - (Fixed) Base AdvCiv bug, in Sevopedia bonus, in the aluminium bonus' entry, of all project tooltips showing the Apostolic Palace and redirecting to it instead of showing the project's tooltip and redirecting to said project, with the help of chatgpt 5.2 thanks

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1I71aSFVOj4GZIhgBde0niJwJIFmx_exC?usp=sharing).

Now fixed with the help of chatgpt 5.2 thanks.

## 87 - (Fixed and Generalized) Cannot open BUG Mod Help-ENG.chm on windows in AdvCiv-SAS, but can open it on windows in base AdvCiv, even though path is the same

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1vFB4Iae35EQlTOaobLDD7Cw4J4OuW_ta?usp=sharing).

Issue and fixed described in [/README.md#external-file-access-in-civ4-ingame-on-windows](/README.md#external-file-access-in-civ4-ingame-on-windows).

## 88 - (Tremendously Improved) AI always upgrading way too much units and not teching at all, sometimes for dozen turns

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1ahGT4Wdts_EywCgUFjSyOfEFzpDk3ows?usp=sharing).

AI had a problem of spending too much time and gold to upgrade units that are often not worth ugprading at all (better let them die and build new ones than tech snail for dozens of turns sometimes).

Here are some extra details i moved away from the cpp file as chatgpt 5.2 nicely did in its solution to another but related issue thanks.

```cpp
		// <!-- custom: note: war gates not implemented as it is not always certain they would be beneficial: they are likely to be harmful depending on how they are implemented. For example, while it is generally good to upgrade units if invaded so our defenses are stronger, if the enemy force is overwhelming, it is better to evacuate (and in SAS as of now we always evacuate doomed cities). But upgrading a unit makes it end its turn if i'm not mistaken, so it will be just destroyed by the enemy forc which is worse than simply escaping. Plus, upgrading at end of move or checking enemy stack's strength is tedious and i don't want to check all sites (and tbh i don't know how to do all of these things or it's tedious xd). Also, upgrading units is not necessarily useful when we are stronger (better tech or gain some other advantage with gold: if we gain an extra tech, not only are we fast but we can also trade it or such for more benefits than doing no teching just to upgrade a unit for 1 turn). And if a war ends, even if we are weaker, it may still be wasted gold, or it won't save us from our doomed defeat, as generally people declare war when they are confident they can win, at least we should assume so. In short, the key point is in autoplay AI techs much faster which is seemingly due to being more efficient with its upgrades instead of a blind "upgrade all units even if we have 100 of them and they cost 1 000 000 gold per upgrade" kind of previous logic (i didn't check, but we keep more of our older units now it seems rather than tech snailing to upgrade them all (check if accurate as i didn't look in detail but it seems to be so in autoplay)). Scores of all AI players are significantly highers, and tech pace much faster especially at later eras, so this is what matters the most. War gates may still have some value, but i'm not sure it's worth the complicated and fragile/versatile implementation it would require (i think), and as it is tedious not done for these then as we are already very getting good results in autoplay if i'm not mistaken. Tune in SAS defines as you see fit. -->
```

Otherwise, see rationale and details in code comments in `CvUnit::canUpgrade` or in the related XML SAS defines's code comments as well.

Very good results in autoplay it seems, in short, especially in the later game, as tech pace is seemingly much faster for all AI players, which is especially nice since they had in AdvCiv-SAS a problem of snailing for dozens of turns (possibly in base AdvCiv too from what i remember, although i didn't check to be sure), which should be less of an occurence now (check to be sure, it seemed so at a glance but they still spend some time upgrading units, i'm guessing they are more efficient now or do it less when it is actually worth, but not sure as i didn't check more than that and in autoplay sample, so check if accurate although results do seem good).

## 89 - (Improved) In an attack stack, attack with lower value (effective strength, XP, health) units first

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1pIXiY183a1NpEBSxr5zFUtcg56rwAXwV?usp=sharing).

Data exatracted from the screenshots mostly thanks to ChatGPT 5.2 as it was very accurate (Note: i also tried to do this with Gemini 3 pro but it had many mistakes which is already way too many).

The samples start from same save file turn 295 and are autoplayed 10 turns to turn 305 with each DLL.

### Turn 305 before

#### Scoreboard

| Military Ratio | Score | Leader Name |
| :--- | :--- | :--- |
| **2.4** | 2928 | Tokugawa Ieyasu |
| **0.8** | 1224 | Suryavarman II |
| **3.3** | 2928 | Ewuare |
| **1.7** | 1730 | Moctezuma II |
| **0.6** | 749 | Julius Caesar |
| **1.3** | 1435 | Qin Shi Huang |
| - | 1399 | PC |
| **0.4** | 679 | Saladin |
| **0.2** | 750 | Gilgamesh |
| **0.1** | 571 | Alexander III |

Here is the text extracted from the Event Log panel in the screenshots:

#### Civ4ScreenShot2029 - Event Log

- AD 1910: The enemy has been spotted near Sippar!
- AD 1910: The enemy has been spotted near Dur-Kurigalzu!
- AD 1904: Ewuare has made peace with Moctezuma II and Julius Caesar.
- AD 1904: Moctezuma II converts to Judaism! (Renounces Christianity.)
- AD 1904: Isin (Ewuare) has been captured by the Aztec Empire!!
- AD 1902: Khuraan (Moctezuma II) has been captured by the Kingdom Of Benin!!
- AD 1900: Akkad (PC) has been captured by the Japanese Empire!!
- AD 1898: Suryavarman II adopts Free Religion! (Renounces Christianity.)
- AD 1898: Qin Shi Huang has made peace with Tokugawa Ieyasu and Suryavarman II in exchange for Assembly Line.
- AD 1898: Ewuare has declared war on Moctezuma II and Julius Caesar!
- AD 1896: Tokugawa Ieyasu and Suryavarman II have made peace with Moctezuma II and Julius Caesar.
- AD 1896: Ewuare has declared war on Tokugawa Ieyasu and Suryavarman II!
- AD 1896: You and Saladin have declared war on Tokugawa Ieyasu and Suryavarman II!
- AD 1892: You and Saladin have made peace with Qin Shi Huang
- AD 1890: Guangzhou (Qin Shi Huang) has been captured by the Japanese Empire!!
- AD 1888: You and Saladin have declared war on Qin Shi Huang!
- AD 1884: Saladin has agreed to become a vassal state of PC
- AD 1880: Moctezuma II converts to Christianity! (Renounces Judaism.)
- AD 1871: Moctezuma II and Julius Caesar have made peace with Ewuare.
- AD 1871: Apostolic Palace voting members have announced their decision: Stop trading with
Gilgamesh (Requires 376 of 608 Total Votes)

#### Hammurabi (Civ4ScreenShot2006)

- Worker (7)
- Work Boat (2)
- Horse Knight (3)
- Dragoon (20)
- Maceman (1)
- Cannon (5)
- Musketman (1)
- Rifleman (19)
- Grenadier (8)
- Galley (2)
- Trireme (1)
- Galleon (1)
- Ship of the Line (1)
- Ironclad (1)

#### Moctezuma II (Civ4ScreenShot2007)

- Worker (12)
- Work Boat (2)
- Great Artist (1)
- Longbowman (1)
- Camel Knight (21)
- Camel Cuirassier (14)
- Spearman (2)
- Pikeman (1)
- Cannon (8)
- Musketman (6)
- Rifleman (33)
- Grenadier (31)
- Galley (1)
- Galleon (1)
- Ironclad (1)

#### Qin Shi Huang (Civ4ScreenShot2008)

- Worker (13)
- Work Boat (2)
- Longbowman (2)
- Camel Knight (2)
- Camel Cuirassier (1)
- Dragoon (39)
- Maceman (3)
- Cannon (2)
- Musketman (6)
- Rifleman (24)
- Galley (2)
- Galleon (1)
- Frigate (2)

#### Alexander III (Civ4ScreenShot2009)

- Longbowman (5)
- Hoplite (1)
- Axeman (2)

#### Gilgamesh (Civ4ScreenShot2010)

- Worker (1)
- Spy (1)
- Horse Knight (1)
- Camel Knight (1)
- Maceman (1)
- Cannon (1)
- Musketman (7)

#### Ewuare (Civ4ScreenShot2011)

- Worker (18)
- Spy (1)
- Work Boat (1)
- Great Prophet (1)
- Longbowman (1)
- Camel Knight (7)
- Camel Cuirassier (7)
- Spearman (1)
- Axeman (1)
- Machine Gun (15)
- Field Gun (1)
- Musketman (1)
- Infantry (49)
- Paratrooper (10)
- Grenadier (2)
- Bazooka (9)
- SAM Infantry (15)
- Mobile SAM (39)
- Tank (1)
- Gunship (12)

#### Tokugawa Ieyasu (Civ4ScreenShot2012)

- Worker (22)
- Great Spy (1)
- Archer (1)
- Dragoon (20)
- Machine Gun (11)
- Field Gun (11)
- Rifleman (2)
- Infantry (44)
- Grenadier (8)
- Bazooka (13)
- SAM Infantry (3)
- Mobile SAM (13)
- Galleon (1)
- Destroyer (2)

#### Saladin (Civ4ScreenShot2013)

- Settler (1)
- Worker (2)
- Spy (1)
- Scout (1)
- Longbowman (3)
- Hajjan (1)
- Camel Cuirassier (1)
- Axeman (1)
- Catapult (1)
- Cannon (9)
- Musketman (7)

#### Suryavarman II (Civ4ScreenShot2014)

- Worker (8)
- Camel Cuirassier (2)
- Spearman (1)
- Pikeman (1)
- Axeman (1)
- Maceman (1)
- Field Gun (2)
- Musketman (22)
- Grenadier (16)
- Galley (1)
- Galleon (1)

#### Julius Caesar (Civ4ScreenShot2015)

- Worker (2)
- Camel Knight (5)
- Camel Cuirassier (6)
- Spearman (3)
- Pikeman (1)
- Cannon (6)
- Musketman (9)
- Grenadier (9)
- Galleon (1)

### Turn 305 after

Here is the markdown snippet for the attached screenshots, formatted according to your example.

#### Scoreboard after

| Military Ratio | Score | Leader Name |
| --- | --- | --- |
| **3.5** | 2966 | Ewuare |
| **2.1** | 2937 | Tokugawa Ieyasu |
| **0.7** | 1257 | Suryavarman II |
| **1.3** | 1761 | Moctezuma II |
| **0.5** | 749 | Julius Caesar |
| **1.2** | 1517 | Qin Shi Huang |
| **0.2** | 710 | Gilgamesh |
| - | 1414 | PC |
| **0.3** | 719 | Saladin |
| **0.1** | 571 | Alexander III |

#### Civ4ScreenShot2030 - Event Log

- AD 1906: Ewuare signs defensive pact with PC
- AD 1904: Saladin has renounced the protection of PC and is once again a free state.
- AD 1904: Tokugawa Ieyasu and Suryavarman II have made peace with you and Saladin.
- AD 1902: Akkad (PC) has been captured by the Japanese Empire!!
- AD 1900: Gilgamesh converts to Hinduism! (Renounces Judaism.)
- AD 1900: Qin Shi Huang converts to Daoism! (Renounces Judaism.)
- AD 1898: Tokugawa Ieyasu and Suryavarman II have made peace with Moctezuma II and Julius Caesar.
- AD 1898: Gilgamesh has agreed to become a vassal state of Qin Shi Huang
- AD 1898: You and Saladin have declared war on Tokugawa Ieyasu and Suryavarman II!
- AD 1896: Qin Shi Huang has made peace with Tokugawa Ieyasu and Suryavarman II in exchange for
255 gold
- AD 1896: Ewuare's Golden Age has begun!!!
- AD 1892: You and Saladin have made peace with Qin Shi Huang
- AD 1890: Guangzhou (Qin Shi Huang) has been captured by the Japanese Empire!!
- AD 1888: You and Saladin have declared war on Qin Shi Huang!
- AD 1884: Saladin has agreed to become a vassal state of PC
- AD 1880: Moctezuma II converts to Christianity! (Renounces Judaism.)
- AD 1871: Moctezuma II and Julius Caesar have made peace with Ewuare.
- AD 1871: Apostolic Palace voting members have announced their decision: Stop trading with
Gilgamesh (Requires 376 of 608 Total Votes)
- AD 1865: Isin (Moctezuma II) has been captured by the Kingdom Of Benin!!
- AD 1862: Tokugawa Ieyasu is the first to discover Theory of Evolution!

#### Hammurabi (Civ4ScreenShot2019)

- NO UNITCOMBAT: Worker (7), Work Boat (2)
- ARCHERS (BOW, SHORT): Archer (1)
- MOUNTED (MELEE): Horse Knight (3)
- MOUNTED (RANGED): Horse Cuirassier (1), Dragoon (19)
- MELEE (SHOCK): Maceman (2)
- SIEGE WEAPONS: Field Gun (3)
- GUN UNITS: Musketman (1), Rifleman (18), Grenadier (9), Bazooka (4)
- NAVAL UNITS: Galley (2), Trireme (1), Galleon (1), Ship of the Line (1), Ironclad (1)

#### Moctezuma II (Civ4ScreenShot2020)

- NO UNITCOMBAT: Worker (13), Work Boat (2), Great Prophet (1)
- ARCHERS (BOW, LONG): Longbowman (1)
- MOUNTED (MELEE): Camel Knight (12)
- MOUNTED (RANGED): Camel Cuirassier (11)
- MELEE (POLEARM): Spearman (2), Pikeman (1)
- SIEGE WEAPONS: Cannon (5)
- GUN UNITS: Musketman (7), Rifleman (35), Grenadier (20)
- NAVAL UNITS: Galley (1), Galleon (1), Ironclad (1)

#### Qin Shi Huang (Civ4ScreenShot2021)

- NO UNITCOMBAT: Worker (13), Work Boat (2)
- ARCHERS (BOW, LONG): Longbowman (2)
- MOUNTED (MELEE): Camel Knight (2)
- MOUNTED (RANGED): Dragoon (34)
- MELEE (SHOCK): Maceman (2)
- SIEGE WEAPONS: Cannon (1)
- GUN UNITS: Musketman (5), Rifleman (25)
- NAVAL UNITS: Galley (2), Galleon (1), Frigate (2)

#### Alexander III (Civ4ScreenShot2022)

- NO UNITCOMBAT: (none shown)
- ARCHERS (BOW, LONG): Longbowman (5)
- MELEE (POLEARM): Hoplite (1)
- MELEE (SHOCK): Axeman (2)

#### Gilgamesh (Civ4ScreenShot2023)

- NO UNITCOMBAT: Worker (1)
- MOUNTED (MELEE): Horse Knight (1), Camel Knight (1)
- MELEE (SHOCK): Maceman (1)
- SIEGE WEAPONS: Cannon (1)
- GUN UNITS: Musketman (7)

#### Ewuare (Civ4ScreenShot2024)

- NO UNITCOMBAT: Worker (19), Spy (1)
- ARCHERS (BOW, LONG): Longbowman (1)
- MOUNTED (MELEE): Camel Knight (7)
- MOUNTED (RANGED): Camel Cuirassier (7)
- MELEE (POLEARM): Spearman (1)
- MELEE (SHOCK): Axeman (1)
- SIEGE WEAPONS: Machine Gun (22)
- GUN UNITS: Field Gun (1), Musketman (1), Infantry (49), Paratrooper (11), Grenadier (2), Bazooka (9), SAM Infantry (15), Mobile SAM (50)
- ARMORED UNITS: Tank (1)
- HELICOPTER UNITS: Gunship (18)
- NAVAL UNITS: Galley (2)

#### Tokugawa Ieyasu (Civ4ScreenShot2025)

- NO UNITCOMBAT: Worker (22), Great Spy (1)
- ARCHERS (BOW, SHORT): Archer (1)
- MOUNTED (RANGED): Dragoon (18)
- SIEGE WEAPONS: Machine Gun (6), Field Gun (11)
- GUN UNITS: Rifleman (5), Infantry (36), Grenadier (11), Bazooka (15), SAM Infantry (1), Mobile SAM (11)
- NAVAL UNITS: Galleon (1), Ship of the Line (1), Destroyer (3)

#### Saladin (Civ4ScreenShot2026)

- NO UNITCOMBAT: Settler (1), Worker (2), Spy (1)
- RECON UNITS: Scout (1)
- ARCHERS (BOW, LONG): Longbowman (3)
- MOUNTED (RANGED): Hajjan (1)
- MELEE (SHOCK): Axeman (1)
- SIEGE WEAPONS: Catapult (1), Cannon (10)
- GUN UNITS: Musketman (7)

#### Suryavarman II (Civ4ScreenShot2027)

- NO UNITCOMBAT: Worker (9), Work Boat (1)
- MOUNTED (RANGED): Horse Cuirassier (2), Camel Cuirassier (2)
- MELEE (POLEARM): Spearman (1), Pikeman (1)
- MELEE (SHOCK): Axeman (1), Maceman (1)
- SIEGE WEAPONS: Cannon (2)
- GUN UNITS: Musketman (20), Grenadier (12)
- NAVAL UNITS: Galley (1), Galleon (1)

#### Julius Caesar (Civ4ScreenShot2028)

- NO UNITCOMBAT: Worker (2)
- MOUNTED (MELEE): Camel Knight (5)
- MOUNTED (RANGED): Camel Cuirassier (6)
- MELEE (POLEARM): Spearman (3), Pikeman (1)
- SIEGE WEAPONS: Cannon (7)
- GUN UNITS: Musketman (9), Grenadier (7)
- NAVAL UNITS: Galleon (1)

### Uniformed interpretation of the data by ChatGPT 5.2

Not knowing anything about what the DLL change may be other than a DLL change was made a DLL change related to military and that we want to compare them, here is what ChatGPT 5.2 thought:

### Blind interpretation of the data by ChatGPT 5.2

> - Overall, the "after" run looks more favorable to one clear winner (Ewuare), and harsher on several mid/high-power AIs (Moctezuma, Tokugawa, Qin).
> - The scoreboard power picture shifts: Ewuare rises from 3.3 to 3.5, while Tokugawa drops from 2.4 to 2.1, and Moctezuma drops from 1.7 to 1.3.
> - Unit counts match that story: Ewuare is up roughly +25 land combat units (big increases in Mobile SAM, Machine Gun, and Gunship), while Moctezuma is down roughly -23 land combat units, Tokugawa down roughly -11, Qin down roughly -8.
> - Hammurabi goes the other direction: slightly larger, more modern mixed army in the after run (Field Guns + Bazookas appear, total land combat up a bit).
> - Diplomatically/militarily, the event log in the before run contains "enemy spotted near Sippar/Dur-Kurigalzu" plus a later city capture (Isin (Ewuare) captured by the Aztecs), which reads like real pressure or a defensive failure.
> - In the after run, instead you have "Ewuare signs defensive pact with PC" and "Ewuare's Golden Age has begun", and the visible log does not show the same "enemy spotted" warnings or the same "Ewuare loses Isin" outcome.
> - Taken purely as outcomes, the after run looks like: fewer immediate threats to the player area (at least none shown), Ewuare consolidating and powering up, and some rival armies shrinking hard (whether by battlefield losses, disbanding, or other causes is not knowable from this data alone).
> - If your goal is "AI war outcomes feel more decisive and less prone to random catastrophic defense failures for the strong civ", the after run looks better.
> - If your goal is "keep multiple AIs at comparable strength and avoid a runaway top civ", the after run looks riskier because the power distribution becomes more top-heavy around Ewuare.

### Re-interpreting with code knowledge by ChatGPT 5.2

> Note on wording: earlier, my "code knowledge" section was really just an inference from the outcomes (not actual code), because you had not provided the diff yet. Below is the real code-based analysis of the actual change you posted.
>
> #### What the DLL change actually does
>
> You added a new optional behavior to `CvSelectionGroupAI::AI_getBestGroupAttacker(...)`: when `bPreferLowPower` is true (and the caller is AI, and the new XML define is enabled), the attacker selection stops being "best odds / LFB" and becomes "spend expendables first".
> You then forced this on for stack attacks by changing `CvSelectionGroup::groupAttack` to call:
> `AI_getBestGroupAttacker(..., !bMaxSurvival, bMaxSurvival, true)`
> So for AI group attacks, `bPreferLowPower` is now always true.
>
> #### The new selection rule (when enabled)
>
> For each candidate unit that can attack, you compute:
>
> - `iOdds = AI_attackOdds(...)` (but you do not use it to choose the unit directly)
> - `iPower = AI_currEffectiveStr(...)` (effective strength on that plot, including collateral evaluation inputs)
> - `iValue = iPower`, with a giant bias:
>
> - if `bombardRate() > 0` OR `collateralDamage() > 0`, you do `iValue -= 1000000`
>     Then you pick the unit with:
>
> 1. lowest `iValue` (so: siege/collateral units first, otherwise lowest effective power first)
> 2. tie-break: lowest XP first
> 3. tie-break: among "healthy enough" units (>= `MIN_HEALTH_PERCENT`, default 60), lower health percent first (use slightly wounded units before fully healthy ones)
>
> #### The important interaction with the existing sacrifice logic
>
> At the end of the function, the old logic still runs:
> `if (bSacrifice && iUnitOdds < 68) { pick AI_getBestGroupSacrifice(...) }`
> For AI group attacks, `bMaxSurvival` is effectively false (there is even an assert expecting max-survival to be human-only), so `bSacrifice` tends to be true.
> That means your low-power choice will get overridden when the chosen unit has odds < 68.
> Net effect in practice is roughly:
>
> - If your "expendable-first" pick has odds < 68, the function falls back to the old sacrifice picker anyway.
> - If your "expendable-first" pick has odds >= 68, it will actually be used, even if another unit had much higher odds.
>
> #### What this change is likely to do in-game
>
> It is not a production change; it is a casualty-distribution and combat-resolution change.
> In particular it will:
>
> - Make siege/collateral units attack earlier much more aggressively than the old logic (because of the -1,000,000 bias), even in cases where the old odds-based logic might have preferred a different unit first.
> - Prefer lower-power (often older/cheaper/obsolete, but also sometimes just "situationally weak on this tile") attackers whenever they still have "not terrible" odds (>= 68).
> - Preserve high-XP and high-power units by holding them back, which can make a strong stack keep its best units alive longer (good for the leader, potentially snowbally overall).
> - Increase variance: choosing a 68-75% attacker instead of a 90-99% attacker will sometimes cause extra losses, and those losses can cascade into very different war trajectories over only 10 turns.
>
> #### Risks / edge cases in the heuristic (code-level)
>
> 1. Odds are not part of the main ranking.
>    You only avoid truly awful odds indirectly via the `< 68` sacrifice fallback.
>    So the code can still choose a materially worse attacker (say 70%) over a near-certain attacker (say 95%) purely because it is lower power / lower XP.
>    That is a real "win-rate vs preservation" tradeoff, and it can absolutely change who wins a war.
> 2. `iPower` is "effective strength on this plot", not "unit cost" or "unit replaceability".
>    Sometimes a valuable unit can look low-power due to situational modifiers, and your rule will spend it early when you did not intend to.
> 3. The -1,000,000 siege bias is a hard override.
>    It does not merely "prefer siege first", it forces siege/bombard/collateral to the front of the line whenever available.
>    That is often correct for city assaults, but it may be wrong for some field fights or odd tactical positions.
> 4. Health tie-break only applies after `iValue` and XP tie.
>    So it does not strongly protect badly wounded units (it only nudges within a narrow tie scenario).
>
> #### Re-reading your observed outcomes with this code in mind
>
> In your 10-turn sample, the "after" run ends up more top-heavy:
>
> - Ewuare increases military ratio (3.3 -> 3.5) and visibly grows modern forces (notably Mobile SAM and Gunships).
> - Several rivals end the run with noticeably fewer units than in the "before" run (Moctezuma, Tokugawa, Qin).
>   Given the code, that pattern is plausible if:
> - The strongest side(s) had enough depth of "expendable-but-acceptable-odds" attackers to trade away, while preserving their elite finishers.
> - The weaker side(s) were forced into more marginal attacks (or simply lost more when attacking/defending into collateral-first sequencing), causing stack collapses.
>   This is exactly the kind of change that can amplify existing power disparities: the civ with the deeper and more modern stack benefits more from "preserve elites", while the civ with thin forces can get punished harder when it spends weak attackers first and fails to convert attacks into wins.
>
> Also, your note that "many wars and stacks colliding happened in those 10 turns" matters a lot:
> This change only expresses itself when stacks are actually attacking.
> So your sampling window is a good stress test for it (but also more chaotic / path-dependent).
>
> #### Conclusion: good, bad, or randomness?
>
> My honest read from the code + the kind of divergence you see is:
>
> - Not obviously "broken" (the <68 sacrifice fallback prevents the most suicidal low-odds picks in many AI stack attacks).
> - Very likely to increase war decisiveness and variance, and also likely to increase snowballing (strong stacks preserve elites and keep momentum).
> - The outcome difference you saw could be partly "real improvement" (better sequencing, better elite preservation) and partly "RNG / path dependence" (any DLL change can shift RNG call order and cascade into totally different wars by turn 305).
>   So I would classify it as: "plausibly good idea, but high-impact enough that a single 10-turn A/B is not sufficient; it needs a small batch test to see if it consistently improves AI war results without creating runaway amplification."
>
> #### If you want a simple, low-risk refinement (still in your style)
>
> If the goal is "expendables first, but don’t throw wins away", the simplest guardrail is:
>
> - First compute `iBestOddsOverall` (max odds among eligible attackers).
> - Only allow the low-power ordering among units with `iOdds >= iBestOddsOverall - X` (e.g. X=10), or require `iOdds >= 80` for non-siege units.
>   That preserves your intent (don’t spend elites when multiple units have comparable odds), while preventing the 70% vs 95% type of self-sabotage.
>
> If you want, paste the old (pre-change) selection block call sites you care about (where else `AI_getBestGroupAttacker` is called), and I can tell you exactly where this new behavior will and will not apply (and where it might be unexpectedly bypassing LFB).

#### About siege (ChatGPT 5.2 Thinking)

> ### Siege and collateral units
>
> #### What the code intends
>
> Your new attack-order path treats "siege/collateral" as: `bombardRate() > 0` **or** `collateralDamage() > 0`, and it hard-prioritizes them by subtracting 1,000,000 from their selection value.
> So for **AI stack attacks** (not humans), once a group has committed to attacking, siege/collateral should usually go **first**, and therefore should be "burned down" (spent) earlier on average.
> (Also: **Machine Guns are not siege** in Civ4 terms; they normally have neither bombard nor collateral. Your rule will not auto-frontload them unless your XML gives them collateral/bombard.)
>
> #### What we can and cannot infer from your 10-turn snapshots
>
> From a single end-of-window composition snapshot, we **cannot directly prove** "siege went first" because we do not observe the attack sequence, and siege counts are also affected by production, upgrades, and reinforcements.
> What we *can* do is a weak signal check: did total visible siege/collateral counts (Catapult + Cannon + Field Gun in your lists) trend down more in the "after" run?
>
> #### Siege/collateral counts: before vs after (from your lists)
>
> Total siege/collateral units visible:
>
> - Before: ~46 (Cannon 31, Field Gun 14, Catapult 1)
> - After:  ~42 (Cannon 26, Field Gun 15, Catapult 1)
>   That is a small net drop (~-4) over 10 turns, which is **compatible** with "siege gets used up earlier" but far from conclusive.
>
> Per-civ notable deltas (siege only):
>
> - Moctezuma: Cannon 8 -> 5 (down)
> - Qin: Cannon 2 -> 1 (down)
> - Hammurabi: Cannon 5 -> Field Gun 3 (different mix, slightly down in count)
> - Saladin: Catapult 1 + Cannon 9 -> Catapult 1 + Cannon 10 (slightly up)
> - Julius: Cannon 6 -> 7 (slightly up)
>
> #### Practical interpretation
>
> The aggregate signal is mild: there is *some* movement consistent with spending siege earlier (notably Moctezuma/Qin), but not a strong "everyone burned siege" signature.
> That makes sense because your logic only changes **attack ordering**, and only expresses strongly in fights where stacks attack repeatedly; production/upgrades can easily mask siege attrition in a 10-turn slice.

### Same with claude opus (4.5) not informed about code

Hi! Happy to help analyze this blind comparison.

Looking at the two outcomes after 10 turns (Turn 295 → 305):

#### Key Differences

##### Scoreboard Changes

| Leader | Before | After | Change |
| -------- | -------- | ------- | -------- |
| Ewuare | 2928 (3.3 mil) | 2966 (3.5 mil) | +38 score, +0.2 mil |
| Tokugawa | 2928 (2.4 mil) | 2937 (2.1 mil) | +9 score, -0.3 mil |
| Qin Shi Huang | 1435 (1.3 mil) | 1517 (1.2 mil) | +82 score, -0.1 mil |
| PC (player) | 1399 | 1414 | +15 score |
| Saladin | 679 (0.4 mil) | 719 (0.3 mil) | +40 score, -0.1 mil |

##### Notable Diplomatic/Event Differences

**Before version:**

- Ewuare declared war on Tokugawa/Suryavarman
- More chaotic war declarations
- Gilgamesh kept his Spy unit

**After version:**

- Ewuare signs **defensive pact with PC** (big deal!)
- Ewuare enters a **Golden Age**
- Gilgamesh becomes **vassal of Qin Shi Huang**
- Saladin **breaks free** from PC vassalage
- Generally more peace settlements

##### Military Composition

The "After" version shows more **tech progression** for multiple civs—PC gained Field Guns, Bazookas, and a Horse Cuirassier. Ewuare expanded his Gunship fleet (12→18) and Mobile SAMs (39→50).

#### Verdict

The **"After" DLL** appears to produce a **more stable, diplomatically active** outcome with better AI decision-making (defensive pacts, vassalization, Golden Ages triggering). The military ratios are slightly more compressed, suggesting more balanced power dynamics.

Would you say that matches what the DLL change was intended to do?

### Same but wit code knowledge (Claude opus 4.5)

#### Analysis of the Low-Power Attack Order Optimization

##### What the Code Does

The change modifies `AI_getBestGroupAttacker` to reorder which units attack first in AI stack battles:

> **Before:** AI selected attackers based on highest odds/value (elite units often attacked first)
>
> **After:** When `bPreferLowPower=true` (enabled for AI only), the selection prioritizes:
>
> 1. **Siege/collateral units first** (get a massive -1,000,000 penalty to push them to the front)
> 2. **Lowest effective power** among remaining units
> 3. **Lowest XP** as tiebreaker
> 4. **Lower health** (if above 60% HP threshold) as final tiebreaker

The rationale in the code comment is sound:

> - "Older/weaker units cost upkeep but scale poorly, while elite units are costly to lose and can secure the fight if early attacks go badly; keeping them as finishers preserves flexibility and escape odds."*

---

#### Re-analyzing the Test Results

With this context, let me revisit what we saw:

##### Military Composition Shifts

| Civ | Before | After | Interpretation |
| ----- | -------- | ------- | ---------------- |
| **Ewuare** | Gunship (12), Mobile SAM (39) | Gunship (18), Mobile SAM (50) | Elite units survived better → grew army |
| **Tokugawa** | Infantry (44), Bazooka (13) | Infantry (36), Bazooka (15) | Lost more infantry (expendables) but preserved Bazookas |
| **PC (Hammurabi)** | No Bazookas, no Field Guns | Bazooka (4), Field Gun (3) | Preserved/built elite units instead of losing them in attacks |

This is **exactly what the code should produce** — expendable units die, elites survive and accumulate.

##### The Gilgamesh Spy Disappearance

> **Before:** Gilgamesh had Spy (1)
> **After:** Gilgamesh has no Spy

This could be explained by: if Gilgamesh attacked with his stack, the new logic might have sent the Spy in as a low-power unit (Spies have minimal combat strength). This could be an **edge case bug** — spies probably shouldn't be selected as attackers at all, but if they somehow pass the `canAttack()` check, they'd be prioritized as "expendable."

##### Diplomatic Cascade Differences

The diplomatic differences (Ewuare's defensive pact, Gilgamesh becoming Qin's vassal) are likely **downstream effects** of different battle outcomes:

- If AI stacks win more decisively (preserving elites), they're in better position → more confident diplomacy
- Ewuare's Golden Age in "After" could be triggered by Great Person generation that survived because elite units weren't lost

---

#### Verdict (after)

> ##### **The change appears to be working as intended — this is a positive result, not randomness.**

**Evidence it's working:**

1. Elite unit counts grew for aggressive AIs (Ewuare's Gunships, PC's Bazookas)
2. Basic infantry/expendables were consumed appropriately
3. The leading AIs (Ewuare, Tokugawa) maintained or improved their positions
4. More decisive outcomes led to cleaner diplomatic resolutions (defensive pacts, vassalizations)

**Potential concerns:**

1. The Spy disappearing from Gilgamesh is suspicious — might want a `!kLoopUnit.isSpy()` check or similar
2. The `-1,000,000` magic number for siege/collateral is a bit crude (though functional)
3. `bPreferLowPower` is hardcoded `true` in `groupAttack` — might want this configurable per situation

**Overall assessment:**

> ##### ✅ **Good change** — economically rational AI behavior, observable positive effects in test run, clean implementation with XML toggles for easy testing

The 10-turn sample is small, but the results align with expected behavior rather than looking like noise. The AI is preserving valuable units and spending cheap ones, which is fundamentally sound strategy.

### About siege (claude opus 4.5)

#### Siege Unit Prioritization Analysis

#### How the Code Handles Siege/Collateral Units

The key logic is here:

```cpp
if (kLoopUnit.bombardRate() > 0 || bCollateral)
    iValue -= 1000000;
```

This gives siege units (Cannons, Catapults, Field Guns, Trebuchets) and collateral damage units a **massive priority boost** (lower value = selected first) to attack before regular combat units.

---

#### Checking the Test Data for Siege Attrition

##### Siege Unit Changes (Before → After)

| Civ | Unit Type | Before | After | Change |
| ----- | ----------- | -------- | ------- | -------- |
| **PC (Hammurabi)** | Cannon | 5 | 0 | **-5** ✅ |
| **PC (Hammurabi)** | Field Gun | 0 | 3 | +3 (new production) |
| **Moctezuma II** | Cannon | 8 | 5 | **-3** ✅ |
| **Qin Shi Huang** | Cannon | 2 | 1 | **-1** ✅ |
| **Saladin** | Cannon | 9 | 10 | +1 (production > losses) |
| **Saladin** | Catapult | 1 | 1 | 0 |
| **Julius Caesar** | Cannon | 6 | 7 | +1 |
| **Suryavarman II** | Cannon | 0 | 2 | +2 (new) |
| **Tokugawa** | Field Gun | 11 | 11 | 0 |
| **Tokugawa** | Machine Gun | 11 | 6 | **-5** ✅ |
| **Ewuare** | Machine Gun | 15 | 22 | +7 (production) |
| **Ewuare** | Field Gun | 1 | 1 | 0 |

---

#### Interpretation

> ##### ✅ **Yes, siege units are being burned down first as intended — for civs actively at war.**

**Clear evidence:**

- **PC lost all 5 Cannons** — this is the player civ that was at war with Tokugawa/Suryavarman. The AI (controlling autoplay) correctly spent Cannons before Riflemen/Grenadiers.
- **Moctezuma lost 3 Cannons** — was fighting Ewuare over Isin/Khuraan.
- **Tokugawa lost 5 Machine Guns** — Machine Guns have `collateralDamage() > 0` in most Civ4 mods, so they get the same treatment.

**Civs that gained siege:**

- **Saladin, Caesar, Suryavarman** — these civs were mostly at peace or in minor skirmishes during the 10 turns, so their production outpaced losses.
- **Ewuare** gained Machine Guns (+7) — likely heavy production during Golden Age; Ewuare was winning fights decisively so fewer losses overall.

---

#### Edge Case: Tokugawa's Machine Guns

> **Before:** Machine Gun (11) → **After:** Machine Gun (6)

This is interesting — Tokugawa lost **5 Machine Guns** but only **lost 8 Infantry** (44→36). The ratio suggests Machine Guns were indeed being sent in early as collateral units, softening defenders before Infantry finished them off.

Compare to his **Bazookas: 13→15** (gained 2). Bazookas have no collateral, so they were preserved as finishers. **This is exactly the intended behavior.**

---

#### Summary

> ##### Siege/Collateral Prioritization: **Working as designed** ✅
>
> | Behavior | Expected | Observed |
> | ---------- | ---------- | ---------- |
> | Cannons spent before Riflemen | Yes | Yes (PC: -5 Cannons, kept 18 Rifles) |
> | Collateral units (Machine Gun) sent early | Yes | Yes (Tokugawa: -5 MGs, -8 Infantry) |
> | Non-collateral elites preserved | Yes | Yes (Tokugawa: +2 Bazookas) |
> | Peaceful civs accumulate siege | Yes | Yes (Saladin, Caesar gained Cannons) |

The `-1,000,000` penalty is doing its job — it's crude but effective. Siege units bombard, then die attacking, then regular troops clean up. Economically rational.

### GPT-5.2-Codex analysis (informed by code + data)

- This change is primarily about casualty distribution, not production. It should shift losses toward low-effective-strength units and siege/collateral units, which preserves high-XP elites for finishing fights or retreating if the attack turns bad.
- The economic rationale aligns with our intent: older/weak units have ongoing upkeep and low marginal impact, so spending them first reduces maintenance drag while protecting promotion investment and versatile endgame units.
- The snapshot data looks consistent with that story: several civs show elite counts holding or rising (e.g., Bazookas, Gunships) while basic infantry and siege take the larger losses in the same 10-turn window. That pattern matches the new ordering logic more than a pure odds-based selection would.
- At the same time, the sample window is short and was full of wars and diplomatic shifts (defensive pacts, vassalization, Golden Ages). Those cascades can amplify small combat-order differences, so this is suggestive but not conclusive.
- Expected risk: the policy can increase snowballing, because the strongest civs have enough expendables to trade while preserving elites, while weaker civs may lose the few strong units they have or fail to convert marginal attacks into wins. The toggle is important for tuning and for A/B testing.

Recommendation: keep testing across multiple 10-turn windows or different saves to see whether the power distribution stabilizes or becomes too top-heavy; track siege attrition and elite-unit survival as the most direct signals of the intended effect.

## 90 - (Fixed) Base AdvCiv bug of Sevopedia Index using the Religion's button instead of the corporations'

Bug found by GPT-5.2-Codex thanks a lot :) Of Sevopedia Index using the Religion's button instead of the corporations

```py
			elif (type == "Religion"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getReligionInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Corporation"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getReligionInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
```

now fixed with the help of GPT-5.2-Codex thanks a lot to:

```py
			elif (type == "Religion"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getReligionInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
			elif (type == "Corporation"):
				screen.setTableText(self.tableName, iColumn, iRow, sText, gc.getCorporationInfo(iData1).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION, iData1, iData2, CvUtil.FONT_LEFT_JUSTIFY)
```

Exists even in [Base AdvCiv 1.12's Sevopedia Index](https://github.com/f1rpo/AdvCiv/blob/1.12/Assets/Python/Contrib/Sevopedia/SevoPediaIndex.py#L232-L235)

And now fixed in AdvCiv-SAS! Thanks GPT-5.2-Codex :)

## 91 - (Adjusted) iBaseGrowthThresholdPercent scales with handicap but it's not clear what it does and how it should be said

Below explanation by ChatGPT 5.2 when i gave it the relevant base advciv's [manual.txt](/_0_Common_Docs/AdvCiv_Base_Doc/manual.txt) blurb.

Based on it, i set all `iBaseGrowthThresholdPercent` to 100.

I also thought we can adjust `iAIGrowthPercent` to 100 at all handicaps, since the human player now has no advantage or disadvantage, it could help the issue of AI runawayat higher handicaps (or vice versa) and allow finer tuning instead through other knobs.

Check if accurate.

### Explanation

That manual excerpt is basically f1rpo explaining a **coupled difficulty model**:

- If difficulty makes **research** more expensive (for the human), then **growth** and **Great People** should also get costlier "to match" (otherwise the balance drifts toward warfare / unit spam in Marathon-like ways).
- And he added *two* different knobs for growth because he wanted:

  - **Human**: adjust only the **base** part of growth (keep the "2 food per pop" part simple/unchanged).
  - **AI**: allow a broader growth bonus that also affects the per-pop part (because "simplicity" doesn’t matter for AI).

### The crucial thing you noticed

In your SAS chart, **human research is already normalized to 100** (and a bunch of other human penalties look reduced/removed compared to base AdvCiv).

So: keeping **human** `iBaseGrowthThresholdPercent` and `iGPThresholdPercent` varying (85..125) is no longer doing what f1rpo’s rationale describes (matching human research penalties), because **you removed the thing they were meant to match**.

That means in SAS those two fields become "silent player penalties" that:

- don’t correspond to your current "human = 100 baseline" philosophy, and
- (for growth) also interact with **expansion**, because of this line in the manual:

> "For each 1 food that the initial city growth threshold differs from 20, the cost for a Settler is adjusted by 5%."

With your current values:

- Deity human: 125% of 20 → 25, difference +5 → **+25% settler cost** (if that code is still present in your DLL).
- Settler human: 85% of 20 → 17, difference -3 → **-15% settler cost**.

So `iBaseGrowthThresholdPercent` is not "just growth pacing"; it’s also (in AdvCiv’s design) an **early landgrab throttle**.

### What I’d do in AdvCiv-SAS (hard, but fair)

If your goal is "difficulty comes from the AI, not hidden human penalties", then the consistent move is:

1: **Normalize human**

- `iBaseGrowthThresholdPercent = 100` on all handicaps
- `iGPThresholdPercent = 100` on all handicaps

2: Put the curve where you already put it elsewhere: **AI-only**

- Keep / tune `iAIGrowthPercent` and `iAIGPThresholdPercent` to hit the difficulty you want.

### Two practical options

**Option A (minimal change, safest):**

- Set human to 100 for both.
- Leave AI as-is for now (`iAIGrowthPercent`: 115..75, `iAIGPThresholdPercent`: 115..75).
  This preserves your current AI advantage *shape* while removing the human penalty layer.

**Option B (more "internally consistent" with your new normalization):**

- Human 100.
- Rebuild AI curves deliberately (like we did for GP), *but be careful with growth* because `iAIGrowthPercent` is a stronger lever than GP threshold (it can inflate AI cities across the whole game, not just GP timing).

If you want, paste your current **AI** growth-related rows (or just confirm you still have that "settler cost adjusts from growth threshold" code enabled), and I’ll recommend a specific `iAIGrowthPercent` curve that fits your current AIResearchPercent curve and your worker/production tuning.

## 92 - (Fixed) Base AdvCiv bug of iExtraFreeOutsideUnits being set to 100 at lower than Marathon game speeds (spotted thanks to the new Sevopedia Game Speed Chart)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1NoH3gqWnHBD9J5e_VwmQxJO_iUsFpfv6?usp=sharing).

I noticed these in the new Sevopedia Game speed that below Marathon values were way too high vs what marathon had (100 vs 1).

Now fixed with code comments, and added the `iExtraFreeOutsideUnits` (plus `iUnitCostPercent`) fields that were missing in XML too instead of relying on DLL defaults.

Gameplay change doesn't seem too significant at a glance, check screenshots and save file provided for comparison.

See [commit/6901fd17969c00abada610fbfd2bdf6bf1fc01ea](https://github.com/wonderingabout/AdvCiv-SAS/commit/6901fd17969c00abada610fbfd2bdf6bf1fc01ea).

## 93 - (Enhanced) New optional XML fields (e.g. ObsoleteTech for units) to fix aberrant unit choice or scrapping

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1AR-bOobIPbMNHdi65NdVjvcAQADYVFvw?usp=sharing).

Not updating every issue here, but since then a much cleaner fix to aberrant obsolete unit production choices, and AI scrapping optimization that was hacky and overloaded, plus player UI enhancement (less crowded UI Production Chooser Bar with nonsensical obsolete units), is the additional of the `ObsoleteTech` field.

Initial version at [commit/a134450486e0104df9473d46017ebc6e4d7bc553](https://github.com/wonderingabout/AdvCiv-SAS/commit/a134450486e0104df9473d46017ebc6e4d7bc553).

See details at [README.md#new-optional-xml-fields-eg-obsoletetech-for-units](/README.md#new-optional-xml-fields-eg-obsoletetech-for-units-button-for-eras-eraartdefinetags-and-eraartdefinetag-for-leaderhead-era-art).

## 94 - (Fixed) Base AdvCiv bug of opening last visited category instead of the index (or in AdvCiv-SAS hints category instead of last visited)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1OO1CkofepKXkzMKD00Gu_bb-kqd_MdCF?usp=sharing).

Was happening in AdvCiv-SAS for other categories last visited like charts too, or Hints or such in base advciv too.

See [commit/21f67530d536c6d93b42cf1223237b34e1ca7d0a](https://github.com/wonderingabout/AdvCiv-SAS/commit/21f67530d536c6d93b42cf1223237b34e1ca7d0a).

## 95 - (Fixed) Base AdvCiv issue of Back button not leading back to Hints or Index that we last visited

After previous issue with exiting Sevopedia and reopening it, this also fixes Base AdvCiv issue of the Back Tab not leading back to last visited category when it was Hints or Index.

See [commit/044d26e918b6aa586807c6428fb770cb32f6324e](https://github.com/wonderingabout/AdvCiv-SAS/commit/044d26e918b6aa586807c6428fb770cb32f6324e).

## 96 - (Fixed/Enhanced) Base AdvCiv issue of Obsoletes spanning vertically instead of being horizontally comma-separated

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1taEek59g61fUYdfz3IwnlR5JaqBbY7Jc?usp=sharing).

Also fixed the base advciv issue of obsolete bullets spanning vertically instead of horizontally being comma-separated. We only make anothee bullet for Obsolete units that are comma-separated too.

This was a problem especially as we had many bullets. Now we only show one bullet per asset type (e.g. all obsolete buildings in one bullet, then all obsolete units in another bullet, etc.). Change with the help of Claude code Sonnet 4.5 in [CvGameTextMgr.cpp](/CvGameCoreDLL/CvGameTextMgr.cpp) thanks.

## 97 - (Fixed) Base AdvCiv issue of "Remove Jungle", "Chop Down a Forest", and "Scrub Fallout" not redirecting to Sevopedia at all on click in the technology advisor unlike e.g. Plantation improvement to Sevopedia improvement corresponding page

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1tDKR5ZqAbFrDZZ3G4YuO7CeiDbsM6mdb?usp=sharing).

Fixed with the help of Claude code Opus 4.5 after i have noticed this issue in the technology advisor, by as of now adding a redirect in [CvDLLWidgetData.cpp](/CvGameCoreDLL/CvDLLWidgetData.cpp).

So now right-clicking e.g. on the "Remove Jungle" button in the technology advisor successfully redirects to the Sevopedia feature corresponding page, e.g. of the Jungle Feature!

Update: since then, fixed to redirect to the new Sevopedia Build's corresponding entry (e.g. of the "Remove Jungle" build entry).

## 98 - (Fixed) Base AdvCiv issue of De Gaulle using Louis' music instead of the music common to De Gaulle and Napoleon

As part of implementing the new Sevopedia Music, i have noticed De Gaulle uses Napoleon music, so asked Claude code Sonnet 4.5 to fix, who then noticed that base AdvCiv path i provided uses Louis (`Louis_early`) music for De Gaulle (and not the Napoleon music that is common with De Gaulle)!

However in Civ4 assets, De gaulle clearly uses `Napoleon_early` and not `Louis_early`.

I had checked before in youtube, and it lists in one video for example:

- "Civilization IV Themes - FRANCE - Louis XIV"
- "Civilization IV Themes - FRANCE - Napoleon/De Gaulle"

So it looks like Base AdvCiv used a different asset for Napeolon than Civ4!

I relied on the youtube or similar type of lsiting rather, and so i created a new napoleon asset music as par tof AdvCiv-SAS music additions, but didn't change De Gaulle since i thought he would inherit the old music and had its own asset, my mistake to have overlooked this!

Fixed by adding De Gaulle specific assets with the help of Claude code Sonnet 4.5, that now use `Napoleon_early` as a distinct music than what Louis uses (`Louis_early`), and finally by keeping Napoleon with its own new AdvCiv-SAS specific music which is neither of these so each leader has its own music.

## 99 - (Fixed) Base AdvCiv bug of K-Mod unwrapped in TEXT XML text

```XML
<!-- custom: remove bug unwrapped in TEXT XML text <English>[ICON_BULLET]+1[ICON_COMMERCE] in %d1 additional [NUM1:tile:tiles]</English>, moved to long comment instead; Long_Comments_XML.txt #272 -->
```

Fixed this based advciv bug, as of now in [Civ4GameText_K-Mod.xml](/Assets/XML/Text/Civ4GameText_K-Mod.xml).

## 100 - (Fixed) Base AdvCiv major CvSelectionGroup::plot crash

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1UlG0EloFY2b9bFoAb6Mw9d9Y_BaHbM0b?usp=sharing).

Finally found and fixed the fairly rare but very nasty and annoying `CvSelectionGroup::plot` recurring and reproducible crash.

Fixed with the help of GPT-5.2-Codex and Claude code Opus 4.5 thanks a lot, as part of implementing Terrain Yield Changes, and committed just the fix separately.

See [commit/d2500dc40107815d6a0afef5b481b9d2073c1743](https://github.com/wonderingabout/AdvCiv-SAS/commit/d2500dc40107815d6a0afef5b481b9d2073c1743) and files for details about the fix.

See also [KI#163](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#163---tentatively-addressed-and-hardened-rare-non-reproducible-autoplay-crash-variant-related-to-cvselectiongroupdeleteunitnode-and-cvselectiongroupclearunits).

## 101 - (Fixed) Base AdvCiv bug of GP bar tooltip in city screen not showing GP from obsolete buildings yet seemingly counting them for the total GP calculation

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1tzj-F2YcMUAbu1ltKkNM0l8vYZWQ-Xf8?usp=sharing).

Fixed base AdvCiv bug of seemingly incorrect math in the GP bar tooltip's hover information.

Was showing 3 Spec + 3 Buildings = 8 Base

But Oracle was obsolete yet its 2 GP was seemingly still counted in base total, yet the UI was not showing it.

Our specialist breakdown was correct and helped spot the base AdvCiv bug.

After adding +GB from obsoelte buildings with the help of GPT-5.2-Codex thanks, now hover displays info that matches what the DLL provides (total of 8 with 3 + 3 + 2 = 8) so looks fixed now.

Also added in the main interface's building list as part of adding it in AdvCiv-SAS for buildings.

Change in [CvGameTextMgr.cpp](/CvGameCoreDLL/CvGameTextMgr.cpp) and [CvMainInterface.py](/Assets/Python/Screens/CvMainInterface.py).

## 102 - (Seemingly Fixed) Base AdvCiv crash related to CvCity::getProductionBarPercentages

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1NFO6NeYgEF6GDZDWkMW8qXfSZNWQ72m7?usp=sharing).

Running an autplay of 500 turns with the 48 civs DLL after generating the map, we get a crash at 332 semeingly related to `CvCity::getProductionBarPercentages`.

After Claude code Opus 4.5 fixed it, the new DLL doesn't crash and game plays end to end so looks solved.

See [commit/24cfc0803db7251f521f0b9b6df1c620109ae3a8](https://github.com/wonderingabout/AdvCiv-SAS/commit/24cfc0803db7251f521f0b9b6df1c620109ae3a8).

See also [KI#162](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#162---tentatively-addressed-and-hardened-rare-non-reproducible-autoplay-crash-variant-in-cvcitygetproductionbarpercentages).

## 103 - (Fixed) Base AdvCiv crash variant of the CvCity::getProductionBarPercentages crash

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1PuRQAE1_3TZUrH1y9I8yBncYpdJnkNhK?usp=sharing).

After the previous KI#102 fix, it seems we have another CvCity::getProductionBarPercentages related crash variant at 361 now.

However looking at stacks, it seems different from the previous one.

T332 crash:

```log
STACK_TEXT:
WARNING: Stack unwind information not available. Following frames may be wrong.
0019f7ac 05f17743 00000061 00000067 0019f818 CvGameCoreDLL!CvCity::getProductionBarPercentages+0x4a2
0019f7c4 05f7cc5f 00000001 00000000 0cb25b90 CvGameCoreDLL!CvPlayer::getCivilizationDescription+0x43
0019f820 05f3cef4 3e08c430 0000000a 632211f0 CvGameCoreDLL!CvPlayerAI::AI_getGreeting+0x279df
0019f8cc 06732570 00000000 00310031 77770000 CvGameCoreDLL!CvPlayer::getGlobeLayerColors+0x2dc4
0019f900 00ffffbf 00000000 00000000 00000000 0x6732570
00000000 00000000 00000000 00000000 00000000 Civ4BeyondSword!initCvPythonExtensions+0x9358df
```

T361 crash:

```log
STACK_TEXT:
WARNING: Stack unwind information not available. Following frames may be wrong.
0019f8d0 05e0f7ce 00000000 5c32ed00 5c32ed40 CvGameCoreDLL!CvCity::getProductionBarPercentages+0x498
0019f8e4 05e358a3 00000002 00000002 ffffffff CvGameCoreDLL!CvCity::cheat+0x31ae
0019f938 05e36399 0000000b 00012008 00000000 CvGameCoreDLL!CvPlayerRecord::getNumCitiesBuilt+0x17e3
0019f98c 05e34373 51a61710 05e66c2c 0019f9f0 CvGameCoreDLL!CvPlayerRecord::getNumCitiesBuilt+0x22d9
0019f994 05e66c2c 0019f9f0 0019f9dc 0677e600 CvGameCoreDLL!CvPlayerRecord::getNumCitiesBuilt+0x2b3
0019f9a8 05fc629f 00000001 00000002 0019f9f0 CvGameCoreDLL!CvGame::selectAll+0x8c
0019fa60 0624bc46 00000002 05fc7890 00000002 CvGameCoreDLL!CvPlayerAI::AI_getGreeting+0x31d8f
0019fc48 0624be51 00000001 05fc9e1e 0678d1c8 CvGameCoreDLL!CvInitCore::getReady+0x18236
0019fc9c 05f782df 0000006d 0678d564 0678d1c8 CvGameCoreDLL!CvInitCore::getReady+0x18441
0019fd3c 05f453ec 00000000 00000001 05e6dd3c CvGameCoreDLL!CvPlayer::setTurnActive+0x4af
0019feb8 006873e8 75f10d00 004d7356 011a488a CvGameCoreDLL!CvPlayer::changeGold+0x4bc
0019ff70 75f0fcc9 002a9000 75f0fcb0 0019ffdc Civ4BeyondSword+0x2873e8
0019ffcc 7762b56f 09fc81cb 00000000 0019ffec kernel32!BaseThreadInitThunk+0x19
0019ffe4 776393e2 00000000 00000000 00fad2f0 ntdll!wcstombs+0x6f
0019ffe8 00000000 00000000 00fad2f0 002a9000 ntdll!FinalExceptionHandlerPad50
```

Asked GPT-5.2-Codex to fix it, and then its solution was reviewed and made more compact with the very nice help too thanks a lot of Claude code Opus 4.5.

Loading save file at turn 0 and autoplaying 500 turns in one go as was done the first time at map generation, no crash happens and game finishes successfully end to end at t500, so looks fixed.

See also [KI#162](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#162---tentatively-addressed-and-hardened-rare-non-reproducible-autoplay-crash-variant-in-cvcitygetproductionbarpercentages).

## 104 - (Tremendously Improved) Base AdvCiv issue of the weird back and forth of declaring war, moving a stack, then withdrawing without attacking which is extremely inefficient

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1P8tAlR6Hj8d1OHpM5umX7rVjOBP_UhVz?usp=sharing).

This was a nasty and long recurring base advciv issue, but now finally fixed or heavily reduced.

Low number of units stacks are sensible to power swings and so a decision to attack one turn may quickly become bad if enemy produces one more unit. City defenses also influence this heavily in the early game.

To avoid tedious and also add a nice sanity is to require a min stack size before advancing our war preparations.

Done with the help of GPT-5.2-Codex and Claude code Opus 4.5. Change in `CvUnitAI::AI_attackCityMove`.

Claude's explanation below thanks a lot!

>Simple fix implemented: Added a minimum stack unit count requirement before AI can be "ready to attack" a city.
>
>CvUnitAI.cpp:4445-4451: Added check for SAS_MIN_ATTACK_CITY_STACK_UNITS
>
>- Stack must have at least 6 units (default) before bReadyToAttack can be true
>- Without bReadyToAttack, the MOVE_DECLARE_WAR flag is not set
>- Simple and targeted - doesn't rely on complex ratio calculations
>
>How it works:
>
>Before: Stack of 3 Gallic Swordsmen → bReadyToAttack = true → advances → declares war → retreats
>
>After:  Stack of 3 Gallic Swordsmen → iGroupSz (3) < iMinStackSize (6) → bReadyToAttack = false → waits for reinforcements
>The fix is at the right level - it prevents the stack from being marked as "ready" until it has enough units, which means:
>
>No MOVE_DECLARE_WAR flag
>No premature advance toward the city
>AI keeps building units until the stack is big enough
>You can tune SAS_MIN_ATTACK_CITY_STACK_UNITS to 7 if 6 feels too aggressive, or lower it if the AI becomes too passive. Please recompile and test.

Empirically, a value of min size 7 delays it, but i thought a value of 9 is saner or safer and it fixes it it seems, at least should heavily reduce it i think (check ingame if accurate though).

## 105 - (Fixed) Base AdvCiv bug of most bonuses (e.g., Deer) sometimes not appearing at first Civ4 launch in some maps (e.g. Boreal)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1kYbF_cDDP08-b8rKmU74r2y5o2NbxGpK?usp=sharing).

After going to main menu and relaunching same map, bonuses would then weirdly appear though at this new generation. Also was not consistent at each civ4 launch it seems for some reason although i'm not sure.

But it is reliably fixed with the help of GPT-5.3-Codex thanks.

Issue seemingly was that variables need to be local and not global.

Current fix direction (validated on Boreal): keep only required persistent class state for `CvMapGeneratorUtil` inheritance (`self.map`, grid sizes, `self.mapRand`, and fractal objects), and move non-required lookups/derived values to function-local variables.

This avoids stale or cross-call state that can survive generation steps and produce inconsistent first-launch resource placement.

The key practical distinction is:

- Keep persistent only what the base generator flow needs across method calls.
- Recompute transient values locally in each method.

After applying this pattern in Boreal, Deer and other food bonuses now appear reliably on first Civ4 launch in tests.

See [commit/accf8702ebf916e999fd07a56211e9aec98af9d7](https://github.com/wonderingabout/AdvCiv-SAS/commit/accf8702ebf916e999fd07a56211e9aec98af9d7).

## 106 - (Worked Around) Base AdvCiv bug of having an option number error in Simple Game (e.g. in Highlands, Boreal), if we started another simple Game map before that had a lot of options (e.g. BTG_Lagoon and Planet_Generator_068 have around 15+ options), but Custom game works fine

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/13kb0UBefgFoOKjN7qxpJDhqnNYXGCSTf?usp=sharing).

Confirmed in base AdvCiv too by minimally adding BTG_Lagoon map only, so issue is not caused by any of our changes to Highlands or Boreal or such it seems.

Currently worked around by warning once that in Simple Gaùme, pressing Esc key many times solves the issue then options are selectable again

## 107 - (Fixed) Base AdvCiv crash after loading a save file, returning to main menu, opening sevopedia (index since first time opened) and typing a sequence like "xsv"

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/15p8WHM5P_NR6YTUjn1URuWbbQQiTMSI8?usp=sharing).

Opening the game, loading a save file, then going to main menu, opening sevopedia index and typing a sequence like "xsv" in search bar causes a crash that is reproducible. And does not happen if just opening the game (without loading a save file) and typing such a sequence.

Fixed with the help of Claude code Opus 4.6 thanks in [CvGameInterface.cpp](/CvGameCoreDLL/CvGameInterface.cpp).

## 108 - (Fixed) Base AdvCiv diplomacy inconsistency: AI can refuse "tribute" for pure Vassal/Surrender, then accept the same deal through "What do you want in exchange?" with nothing added

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1sVkCzmBWbkdVvPDLqog3Hr_2-J6sab0q?usp=sharing).

Repro from diplomacy screen:

- AI offers only `Vassal State` (or `Surrender`) and no extra terms.
- Clicking `We demand that you give this to us in tribute.` can return refusal (`Not bloody likely`).
- Clicking `What do you want for this?` right after can return a counter with **nothing extra** and then accept.

So both paths lead to the same final terms, but one refuses first, which is inconsistent and confusing.

Fix:

- In `CvPlayerAI::AI_considerOffer` (file: [CvPlayerAI.cpp](/CvGameCoreDLL/CvPlayerAI.cpp)), add an early human-only acceptance shortcut for the exact one-item pure vassal/surrender shape (one side has only `TRADE_VASSAL` or `TRADE_SURRENDER`, other side empty), before stricter denial/value branches.
- In `CvDiplomacy.py` (file: [Assets/Python/CvDiplomacy.py](/Assets/Python/CvDiplomacy.py)), when this narrow pure vassal/surrender case is accepted, skip firing generic `DIPLOEVENT_MADE_DEMAND` to avoid regular tribute-demand memory side effects for this specific acceptance path.

Result:

- Tribute/Demand and "What do you want in exchange?" now agree for this case.
- Player no longer has to do an extra click sequence to get the same no-extra acceptance.

## 109 - (Tremendously Improved) AI bonus trading: AI very inefficiently buying dominated or equivalent strategic bonuses (era and bonus-aware exclusions)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1gwIEOEnKSjQmE7CfvTmoaXyBZby802Ji?usp=sharing).

Observed issues:

- AI could still buy dominated/equivalent strategic resources in some eras (example: buying `BONUS_COPPER` in Medieval even though it is not needed there).
- AI willing to buy copper when it has iron
- AI willing to buy horse when it has camel or iron at classical, etc.

Fix:

- Keep era/substitute evaluation rules, but enforce exclusion in `CvPlayerAI::AI_bonusTrade` (file: [CvPlayerAI.cpp](/CvGameCoreDLL/CvPlayerAI.cpp)) by returning `DENIAL_JOKING` for dominated/equivalent strategic buy cases; this is filtered from trade tables by explicit buy-denial rules in `AI_bonusTrade`.
- Logic and bonus dependent (e.g., `BONUS_CAMEL` is not an equivalent of Horse anymore at Industrial+ Era (no Camel Dragoon))

## 110 - (AdvCiv-SAS music shuffle cleanup) Intermittent Python startup/MainInterface errors from early BUG path calls in Sevopedia music path helper

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1u_zSqIoSpZ8k0COzIdL3tTLgZjEj1IUY?usp=sharing).

<details>
<summary>Previous KI#110 notes (kept for reference)</summary>

Our understanding:

- The recurring `MainInterface` startup/load failure was triggered by an **early Sevopedia music XML path helper call** added around the music-shuffle work.
- In [\_sevopedia_main_groupings.py](/Assets/Python/Contrib/Sevopedia/_sevopedia_main_groupings.py), `_SAS_findAssetXmlPath()` called BUG path helpers too early (`BugPath.findAssetFile(...)` and related calls).
- Because this can run before BUG is fully ready, it could initialize/freeze BUG asset search paths too soon, so later BUG init failed to load `Assets/Config/init.xml` and `MainInterface` became invalid.
- It appeared around music shuffle / removing one shuffle music because that changed execution timing and path-resolution flow, exposing this fragile startup ordering.

Solution kept in AdvCiv-SAS:

- Removed the needless early `BugPath` calls from `_SAS_findAssetXmlPath()` in [\_sevopedia_main_groupings.py](/Assets/Python/Contrib/Sevopedia/_sevopedia_main_groupings.py).
- Kept filesystem-based candidate resolution only (mod-local path from `__file__`, then local `Assets/...` fallback), which avoids touching BUG path state at risky startup timing.
- Result: no more `MainInterface`/`init.xml` startup failure in the reproduced cases.

Observed error signatures (from `PythonErr.log` / `PythonDbg.log`; exact copy also saved in `C:\Users\PC\Downloads\python dbg error sometimes.txt`):

```log
Traceback (most recent call last):
  File "CvScreensInterface", line 1050, in updateCameraStartDistance
  File "BugCore", line 85, in __getattr__
AttributeError: MainInterface
ERR: Python function updateCameraStartDistance failed, module CvScreensInterface
```

```log
WARN : BugPath - cannot find asset file init.xml in Config
ERROR: BugInit - cannot find XML file for module init
WARN : BugCore - mod MainInterface not initialized; removing
ERROR: BugCore - invalid mod MainInterface
```

```log
Traceback (most recent call last):
  File "BugUtil", line 677, in <lambda>
  File "BugEventManager", line 670, in preGameStart
  File "CvAppInterface", line 70, in preGameStart
  File "CvScreensInterface", line 95, in showTechChooser
  File "CvTechChooser", line 358, in interfaceScreen
  File "CvTechChooser", line 370, in ConstructTabs
  File "CvTechChooser", line 407, in DrawTechChooser
  File "CvTechChooser", line 455, in placeTechs
AttributeError: type object 'CvPythonExtensions.WidgetTypes' has no attribute 'WIDGET_TECH_CHOOSER_ERA'
ERR: Python function preGameStart failed, module CvAppInterface
```

- A separate, optional compatibility variant exists on some DLL/EXE builds: missing `WidgetTypes.WIDGET_TECH_CHOOSER_ERA` in Python.
- Base AdvCiv code inspection suggests similar startup fragility can exist there too (`BugPath.py` mod-folder resolution path).

Commit: [commit/6f94679507a14828421cdc06eeb033a436f1e890](https://github.com/wonderingabout/AdvCiv-SAS/commit/6f94679507a14828421cdc06eeb033a436f1e890)
</details>

Update:

- KI#110 patch alone was not sufficient in all cases: after removing one more shuffle music entry, the `MainInterface` error could still reappear.
- Actual root cause was in the newer music-shuffle Sevopedia path logic: inside `_SAS_findAssetXmlPath()` in [\_sevopedia_main_groupings.py](/Assets/Python/Contrib/Sevopedia/_sevopedia_main_groupings.py), broad `try/except` blocks were added that called BUG path helpers (`BugPath.findAssetFile`, `BugPath.getModDir`, `BugPath.getAppDir`) too early, which could disturb BUG path init order.
- These `BugPath` calls were not actually needed for the music feature: after removing them, music list/path fetching still works correctly in practice.
- Final fix was to remove those unnecessary early `BugPath` calls and keep filesystem-only path resolution there.

To be more precise, the issue was not with music shuffle itself, but with how sevopedia music and media player find existing musics.

Music shuffle feature is kept for now since it seems to work fine.

Update 2:

- To expand on this: the cleaner and sufficient fix for Sevopedia groupings (Music and Media Player) not showing the other opening menu tracks was to fix the XML fetcher path logic itself in `_SAS_findAssetXmlPath()`.
- In practice, resolving directly from mod path context (current BTS cwd + `CvModName.modName`, then `Mods/<mod>/Assets/...`) restored correct track discovery.
- So the robust approach was fetcher-path correction rather than adding BUG-path helper calls.

## 111 - (Reverted this Patch) Sevopedia Index UnicodeDecodeError in build/sort/filter UnicodeDecodeError: 'ascii' codec can't decode byte 0xc8 in position 0

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/14LOLFwnvte-IMeG0NoRLtfLXOYKjbDBe?usp=sharing).

For some reason after we added some leaders in AdvCiv-SAS-NIF-Gallery mod, Sevopedia Index failed with `UnicodeDecodeError` in `SevoPediaIndex` (from `PythonErr.log`):

```log
Traceback (most recent call last):
  File "CvScreensInterface", line 419, in pediaShow
  File "SevoPediaMain", line 590, in pediaShow
  File "SevoPediaMain", line 615, in pediaJump
  File "SevoPediaMain", line 706, in showContents
  File "SevoPediaMain", line 750, in placeIndexCategory
  File "SevoPediaIndex", line 54, in interfaceScreen
  File "SevoPediaIndex", line 208, in buildIndex
UnicodeDecodeError: 'ascii' codec can't decode byte 0xc8 in position 0: ordinal not in range(128)
ERR: Python function pediaShow failed, module CvScreensInterface
```

A fix was found in AdvCiv-SAS-NIF-Gallery in [SevoPediaIndex.py](/Assets/Python/Contrib/Sevopedia/SevoPediaIndex.py) that we applied here in AdvCiv-SAS.

It converts index text to Unicode before sorting/filtering/display, so Sevopedia Index no longer crashes on this error. Gameplay data and rules are unchanged.

Issue no longer appears after this fix so this looks solved.

Update: reverted this fix because in AdvCiv-SAS-NIF-Gallery the error happened for soem other assets later on in Sevopedia Leader, and the fix was to respect case sensitivity at `Art/LeaderHeads/` and for example not `Art/Leaderheads/` that causes this error.

It seems better to fail loudly than to silently hide it, so revert this patch.

Update 2: findings so far:

```XML
<!-- custom: note 2: respect case for Art/LeaderHeads/ else another capitalization like art or Leaderheads or such causes an index error as in KI#111 as describe in AdvCiv-SAS' documentation,, or an unidentifiable C++ exception -->
<!-- custom: note 3: this error also appears when asset folder name is incorrect; e.g. /Elizabeth/ instead of /Elizabeth_1/ in the AdvCiv-SAS NIF Gallery mod; also sometimes just restarting the game sometime later weirdly fixes it -->
```

In short, takeaway seems to pay special attention to capitalization and making sure path or names are correct or such.

## 112 - (Seemingly Fixed) Base AdvCiv issue of missing getPrereqOrPromotion3 in sevopedia promotion

While doing the ui font upscaling, GPT-5.3-Codex noticed and fixed the base advciv issue of missing `gc.getPromotionInfo(j).getPrereqOrPromotion3` prereq check in sevopedia promotion, despite it being present in other parts of our code and seemingly being an extra K-Mod extra prereq.

```py
# <!-- custom: include PrereqOrPromotion3 (K-Mod extra OR prereq) so Leads To lists all promotions that depend on this one; otherwise some valid upgrades are missing from this panel. (GPT-5.3-Codex) -->
```

Not tested to see if it fixes a specific missing prereq, but as it seems to cause no issue, kept as such.

## 113 - (Worked around) WIDGET_PYTHON missing hover text in UI contexts (e.g. Builds in Tech Chooser and Sevopedia)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1C8Fh29p8kXsDhiipZJ34zQtJMQKqxXmY?usp=sharing).

Observed issue:

- `WIDGET_PYTHON` does not provide built-in hover/help text by itself, so anywhere it is used directly for Build entries, hover text is missing.
- After linking build-related entries to Sevopedia Builds through `WIDGET_PYTHON`, build hover text was missing across these Build-entry paths (routes/removals such as Remove Jungle, Chop Forest, Scrub Fallout, Road/Railroad contexts).
- In Tech Advisor, this also reduced usefulness because players could click to Builds, but no longer got the familiar build hover detail from base widget behavior.
- In Sevopedia, the same symptom appeared in build-entry contexts (including Index build rows): clickable behavior existed, hover did not.

Likely root cause:

- `WIDGET_PYTHON` path is good for custom redirects, but unlike `WIDGET_HELP_IMPROVEMENT`, it does not expose the built-in build hover/help behavior.
- Speculation: the built-in build-hover generator appears tied to DLL/EXE widget paths such as `WIDGET_HELP_IMPROVEMENT`, and not accessible through plain `WIDGET_PYTHON`; therefore we patched this in Python with a hybrid widget+click-routing approach.

Workaround approach (hybrid):

- Use `WIDGET_HELP_IMPROVEMENT` for build-entry widgets so base build hover/help is restored.
- Intercept click handling in Python and route non-improvement build clicks (or build-entry clicks generally where needed) to Sevopedia Builds.
- Keep base improvement behavior where appropriate (e.g. improvement entries still benefit from base hover/jump semantics).
- Rationale: this split is intentionally more useful for players (improvement behavior where players expect it in Tech Chooser, and direct Builds-page routing where build details are the main goal in Sevopedia paths).

Applied places:

- Tech Advisor (`CvTechChooser.py`): improvement-first behavior restored; non-improvement builds keep useful Builds redirect while hover text is preserved.
- Sevopedia pages (`SevoPediaMain.py`, `SevoPediaImprovement.py`, `SevoPediaFeature.py`, `SevoPediaBuild.py`): build-entry buttons switched to hover-capable widget path with click reroute.
- Sevopedia Index (`SevoPediaIndex.py`): Build rows now show hover text and still jump to Builds.

Result:

- Hover text and click usefulness are both kept across all Build-entry paths that now use this hybrid approach.
- User flow is now consistent across Tech Advisor and Sevopedia build entries.

Update:

- After the KI#113 refactor, a regression appeared in Sevopedia Builds list: removable builds (e.g. Remove Jungle, Chop Down a Forest, Scrub Fallout) could lose their icon/button in the left list, while route builds still looked fine (Sevopedia Index stayed unaffected).
- Root cause: in `SevoPediaMain.placeItems`, header detection used `data1 == -1`, but for Builds `data1` is repurposed to build tech prereq for `WIDGET_HELP_IMPROVEMENT`; removable builds often have `<PrereqTech>NONE</PrereqTech>`, so they were falsely treated as headers.
- Fix: detect real headers/spacers using the original list marker `item[1] == -1` (not mutated `data1`), which restores those Build icons/buttons in Sevopedia Builds.

## 114 - (Fixed) Base AdvCiv bug of Tech Advisor on save-load initially shown current tech missing turns-left timer until another tech is clicked

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1Z4BmwuUuJgh2YsABubqZFmbNLhyBn6uV?usp=sharing).

Observed issue:

- After loading a save, Technology Advisor could show `Constitution` without `(1)` (only queue-style text).
- Clicking `Later Abrahamism (4)`, then clicking back `Constitution (1)`, made the timer appear.
- Reloading the save reproduced the issue again.

Fix:

- Update first draw path (`placeTechs`) to append turns-left like refresh path (`updateTechRecords`) so timer is present immediately after load.
- Keep first-draw and refresh text rendering consistent (same anchoring behavior).

Changed file:

- [CvTechChooser.py](/Assets/Python/Screens/CvTechChooser.py)

## 115 - (Fixed) Likely Base AdvCiv issue: Victory screen vote requirement text spacing in Resolutions tab

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1Op8y2q_cNPvHC3Gs87JlHtB7CTPsDUdK?usp=sharing).

Observed issue:

- In the Victory Advisor Resolutions tab, the `(Requires X of Y Total Votes)` line could show odd leading spacing.
- We did not test this directly in base AdvCiv, hence the "Likely Base AdvCiv issue" wording.

Why:

- `TXT_KEY_POPUP_ELECTION_OPTION` is built for a longer format with a first placeholder (`%s1_VoteName`). Passing an empty first value in this context leaves unwanted spacing.

Fix:

- Added a dedicated key without the first placeholder: `TXT_KEY_SAS_VOTE_REQ_ONLY`.
- Updated `CvVictoryScreen.py` to use that key directly for the Resolutions "requires votes" line.

Note: although this is fixed, the Members tab also has an extra spacing at the start of lines that start with a star chars but as of now left as such since i couldn't easily find how to fix it.

## 116 - (Worked around) Foreign Diplomacy Advisor Glance tab clips trailing status icons at upscaled label fonts

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1T8D-mgc9ZrNnXa33ywEepGjjLQRCi1ab?usp=sharing).

Observed issue:

- In Foreign Diplomacy Advisor (F3), Glance tab cells could clip the final status icon when `SAS_UI_FONT_LABEL > 2`.
- Typical failing case was double-digit attitude text with icon suffix, e.g., `+11` or single-digit attitudes (e.g., `-8`) when there are 2 trailing status icons (e.g., WE icon + war/peace/war-trade icon).
- Visual width looked sufficient, but the last icon glyph was still trimmed by Civ4 text rendering.

Workaround used (kept intentionally minimal):

- In `CvForeignAdvisor.py` Glance rendering, keep normal upscaled label-font rendering by default.
- Only when a row has at least 2 trailing status icons, render that icon suffix at fixed `<font=2>`; single-icon tails render fine, so no workaround is needed there.
- Keep the numeric/head part at the current upscaled label font.

This is a targeted workaround rather than a full Glance layout rewrite.

## 117 - (Fixed) Score Tab attitude icon chars disappearing at upscaled label fonts (`SAS_UI_FONT_LABEL` 3/4)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1tTPS4NWkAe5sJ5xqD9Z3aqlLCV8-W9w0?usp=sharing).

Observed issue:

- In Info Screen (F9) Score Tab, the `Att` attitude icon char disappeared when text was upscaled (`SAS_UI_FONT_LABEL` 3 or 4).
- The same icon chars appeared at smaller font paths (`SAS_UI_FONT_LABEL` 2 or lower).

Root cause:

- The attitude smileys used by `AttitudeUtil.getAttitudeIcon()` are custom BUG symbols (`furious`, `annoyed`, `cautious`, `pleased`, `friendly`) mapped through `Assets/Config/init.xml`.
- `GameFont_75.tga` had these attitude icon chars (16x16), but `GameFont.tga` did not have them at all (and so not in matching slots).
- Upscaled label rendering uses the `GameFont.tga` path, so the engine resolved valid ordinals to empty/magenta slots and drew nothing.

Fix applied:

- Added attitude icon chars into `GameFont.tga` too, using higher-quality source icons (21x20, from RI mod) while keeping textual icon-char rendering in Score Tab as it was.
- Done with the help of Game Font Editor (V0.6) by Asaf.
- Result: attitude icon chars are now visible at upscaled label fonts (3 and 4), while still working at lower label fonts.

Note: these higher quality icons are as of now also used for the sevopedia leader attitude button icons (as DDS icons, not textual chars though), that used previously the 16x16 lower quality icons of base civ4 and that looked pixelated at higher dds icon; now the higher-quality version looks better at higher icon size.

To add them as dds, we used Game Font Editor (V0.6) for Civ 4 by Asaf (select icon -> export -> .PNG), reduced dds to 20x20 (with Paint.NET canvas resize of these .PNG) (else they don't not display ingame), and then converted to .dds with Paint.NET.

## 118 - (Worked around) Military Advisor inline `<img>` icons can render magenta for button paths with spaces/parentheses

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1BR6F43geOVySyuZfCDc1l6jMr_-yPASp?usp=sharing).

Observed issue:

- After switching Military Advisor unit-list icons to inline `<img=...>` (for scroll-safe alignment), the Hajjan's unit icon renders magenta/purple even though other units' icons render fine (and the Hajjan unit icon renders fine in Sevopedia too).
- Example fixed in this issue: Hajjan unit icon in Military Advisor.

Root cause:

- Inline `<img>` parsing is stricter than icon-slot rendering used by older UI paths.
- Button paths containing spaces/parentheses (or atlas-style button strings) are more likely to fail in this inline path and produce magenta.

Fix/workaround applied:

- Renamed the problematic Hajjan button asset/path from `Art/AdvCiv_SAS/Units/Arabia_Hajjan/medium_cavalry_arabia (camel archer).dds` to `Art/AdvCiv_SAS/Units/Arabia_Hajjan/medium_cavalry_arabia.dds`, and updated XML accordingly.

Audit notes (folder scan):

- We scanned `Assets/Art/AdvCiv_SAS` for `.dds` filenames containing spaces/parentheses.
- Found examples:
  - `Buildings/Celtic_La_Tene_Smithy/nif/building attachments.dds`
  - `Buildings/Celtic_La_Tene_Smithy/nif/building n shared03 2 map.dds`
  - `Buildings/Celtic_La_Tene_Smithy/nif/building n shared04 2 map.dds`
  - `Buildings/Natya_Shastra/indian sreni.dds`
  - `Units/Mongol_Khishigten/nif/Mongol HeavyCavalry Body.dds`
  - `Units/Robotic_Infantry/nif/t600_skin_red eye.dds`

Safety rule used:

- We only rename button assets not tied to NIF texture references by default (cheap/safe).
- We avoid renaming files under `.../nif/...` unless all NIF references are also updated and validated, to avoid breaking models.

So among them we as of now only renamed `indian sreni.dds` to `indian_sreni.dds`.

## 119 - (Fixed) Sevopedia category opening on blank placeholder rows (`item == -1`) and polluting BACK/NEXT history

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1Pmlc3XtyCe6qwUYRVBwEL4dYNEIUOZTK?usp=sharing).

Observed issue:

- In many Sevopedia categories, opening the category lands first on a blank no-item page (header/spacer row where `item id == -1`) instead of the first real entry.
- This slows navigation (extra click per category) and adds useless transient pages in BACK/NEXT history.

Fix applied:

- In `SevoPediaMain.pediaJump`, when opening a category from `PEDIA_MAIN`, resolve and auto-jump to the first selectable item (`item[1] != -1`) on fresh category clicks.
- Skip auto-jump for no-item categories.
- If redirect happened, remove the transient `(PEDIA_MAIN, category)` node from history so BACK/NEXT stays focused on real pages.

Files changed:

- [Assets/Python/Contrib/Sevopedia/SevoPediaMain.py](/Assets/Python/Contrib/Sevopedia/SevoPediaMain.py)

## 120 - (Documented) Known Limitation: Per-era leader art shows the lowest-index player's era when the same leader is assigned to multiple players

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1_idRpqnUsnPtbYnuzLbnB3nBCV7WivFd?usp=sharing).

Observed issue:

- The per-era leader art feature (gated by a SAS define) picks the era from the first alive player using a given leader. In the common case (unique leaders per game) this is correct.
- When the same leader is assigned to multiple players (unrestricted leaders, or custom scenarios placing e.g. De Gaulle on 3 civs), all duplicates render with the lowest-index player's era art — even if player A is in Classical while player B is in Industrial. This is acceptable because a leader used several times by diffetrent players is a rare occurence that happens outside of normal play.

Why not fixed:

- `CvLeaderHeadInfo::getArtInfo()` is called by the EXE with no player context — it only receives the global info pointer. The function signature can't be extended across the DLL/EXE boundary.
- The failure mode is purely cosmetic (wrong era art on a duplicate) and never crashes; fallback to the base `ArtDefineTag` works normally when no override is set.

Files affected:

- [CvGameCoreDLL/CvInfo_Civilization.cpp](/CvGameCoreDLL/CvInfo_Civilization.cpp) - `CvLeaderHeadInfo::getArtInfo()`

## 121 - (Fixed) Base AdvCiv bug: `CvVoteSourceInfo` parses `ReligionCommerces` into the wrong array

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/17whOKSiVxA88oZxGlBUwIHl2Aa5U5Z1M?usp=sharing).

Observed issue:

- In Sevopedia Votes, `Religion Commerces` could display `None` even when XML had non-zero values in `CIV4VoteSourceInfos.xml` under `<ReligionCommerces>`.

Root cause:

- In `CvVoteSourceInfo::read` (`CvInfo_Building.cpp`), the XML loader call for commerce values incorrectly targeted the yield container:
  - `SetCommerceList(ReligionYield(), "ReligionCommerces")` (wrong target)
- Because of that, `getReligionCommerce(i)` returned zeroes, so UI and gameplay readers saw no commerce bonuses from vote sources.

Fix:

- In `CvVoteSourceInfo::read` (`CvInfo_Building.cpp`), changed the loader target, from `SetCommerceList(ReligionYield(), "ReligionCommerces")` (wrong target) to `SetCommerceList(ReligionCommerce(), "ReligionCommerces")` (the proper commerce container).

Result:

- Vote-source commerce values now load from XML correctly.
- Sevopedia Votes `Vote Source Info` now shows the expected non-zero religion commerce entries instead of `None` when data exists.

File changed:

- [CvGameCoreDLL/CvInfo_Building.cpp](/CvGameCoreDLL/CvInfo_Building.cpp)

## 122 - (Fixed) While adding Sevopedia EventTriggerInfo missing getters, found and fixed 3 DLL Python-binding bugs

While exposing missing EventTrigger/EventInfo getters for Sevopedia, we noticed and fixed 3 existing binding bugs in `CyInfoInterface3.cpp`: `getReligionRequired`, `isPickOtherPlayerCity`, and `getNumUnits` were bound to wrong functions.

Fix:

- Corrected each Python binding to the matching C++ getter:
  - `getReligionRequired -> CvEventTriggerInfo::getReligionRequired`
  - `isPickOtherPlayerCity -> CvEventTriggerInfo::isPickOtherPlayerCity`
  - `getNumUnits -> CvEventInfo::getNumUnits`

File changed:

- [CvGameCoreDLL/CyInfoInterface3.cpp](/CvGameCoreDLL/CyInfoInterface3.cpp)

## 123 - (Fixed) BUG Domestic/Military advisor variant toggles required restarting Civ4

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1I6QRzBWnLw9u0kduHIBBsXiQ7DTxBxqR?usp=sharing).

Observed issue:

- Changing the BUG menu setting for Domestic Advisor (F1) or Military Advisor (F5) did not affect the next advisor open in the same game session.
- The change only appeared after restarting Civ4.
- From in-game testing, the Religion advisor option did not have this issue (even after Religion was moved into the Policy Advisor).

Cause:

- `CvScreensInterface.py` cached the Domestic and Military advisor screen objects after startup.
- Changing the BUG option updated the option value, but the cached screen object was still the old advisor variant.

Fix:

- `CvScreensInterface.py` now remembers which Domestic/Military advisor variant was created.
- When F1 or F5 is opened, it compares the cached variant with the current BUG option and rebuilds the advisor object if the option changed.
- `HandleInputMap` is updated with the rebuilt object so input routing follows the active advisor variant.

Note:

As part of this change, also applied the following change:

```py
		# <!-- custom: Fix KI#123 follow-up Python error: CDA stores its position-cache flag at module level, so the rebuilt advisor object skipped createPositions and raised missing nScreenX. See KI#123. (GPT-5.5) -->
		CvCustomizableDomesticAdvisor.forcePositionCalc()
```

to fix the following py error:

```log
Traceback (most recent call last):

  File "CvScreensInterface", line 174, in showDomesticAdvisor

  File "CvCustomizableDomesticAdvisor", line 861, in interfaceScreen

AttributeError: CvCustomizableDomesticAdvisor instance has no attribute 'nScreenX'
ERR: Python function showDomesticAdvisor failed, module CvScreensInterface
```

File changed:

- [Assets/Python/EntryPoints/CvScreensInterface.py](/Assets/Python/EntryPoints/CvScreensInterface.py)

## 124 - (Fixed) Likely Base AdvCiv issue: map-view unit bar overflows into hovered/expanded scoreboard

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1VRXC3ke-rHgnlevnY7BIazvHDCTcseU6?usp=sharing).

Observed issue:

- A full row of the unit bar (any row count, even just one) extends behind the scoreboard when the scoreboard is hovered/expanded to its widest.

Not tested in base AdvCiv, only in AdvCiv-SAS, but it likely happens there too.

Fix:

- Added SAS defines to shrink the unit bar's width (fewer buttons per row before wrapping) (as part of the broader change that allows to shift the unit bar horizontally / vertically), letting the user trim it back from the scoreboard.

Note:

- The width knob is hard-pixel (not resolution-scaled) on purpose, since what it compensates for (scoreboard width) is also font-driven.
- Width adjustment granularity is one button width: small steps may have no effect until a column drops.

File changed:

- [Assets/Python/Screens/CvMainInterface.py](/Assets/Python/Screens/CvMainInterface.py)
- [Assets/XML/GlobalDefines_advciv_sas.xml](/Assets/XML/GlobalDefines_advciv_sas.xml)

## 125 - (Fixed) Base AdvCiv issue: Sevopedia Back/Next history is lost on exit

Observed issue:

- Closing Sevopedia cleared its Back/Next navigation history.
- This made it tedious to revisit previously browsed pages after returning to the map, especially when comparing several Leader AIP pages or other related Civilopedia entries.

Fix:

- Sevopedia now keeps Back/Next history for the current game session after exiting and reopening.
- Added a footer `Clear` button to reset the session navigation chain while keeping the current page as the new history root.

File changed:

- [Assets/Python/Contrib/Sevopedia/SevoPediaMain.py](/Assets/Python/Contrib/Sevopedia/SevoPediaMain.py)

## 126 - (Fixed) Sevopedia footer navigation controls looked active even when they had no effect

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1I6QRzBWnLw9u0kduHIBBsXiQ7DTxBxqR?usp=sharing) (only after fix because any sevopedia screenshot would show the non-greyed former behaviour).

Observed issue:

- Sevopedia footer controls such as `Back`, `Next`, and `Clear` could look active even when clicking them would do nothing.
- This is independent of session-persistent history, but became especially confusing there: after exiting and reopening Sevopedia in the same session, `Back` and `Next` could remain visible while having no current navigation effect.

Fix:

- `Back`, `Next`, and `Clear` remain in stable footer positions, but their text is greyed out when the corresponding action has no effect.
- Contextual page links such as `Legend` keep their existing behavior: they are hidden when the page has no legend, because that means the page-specific link does not apply rather than a global command being temporarily inactive.

File changed:

- [Assets/Python/Contrib/Sevopedia/SevoPediaMain.py](/Assets/Python/Contrib/Sevopedia/SevoPediaMain.py)

## 127 - (Worked around) DLL max players / Worldsize default players mismatch causing very sparse games, and players not being notified of it

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1sglSFxWnZ31_bl_Q5l8iVUmR-lVwUfUl?usp=sharing).

If players start a game on larger world sizes (as of now SAS24 or higher) while using the 18 civs DLL, player count is capped at 18 even if world size has a default player count of e.g., 24 on SAS24 world size.

Also, players were not notified of this, so they may engage unawarely in a game where world size would never be fully populated most likely (extreme example as of now: 18 players on SAS48 worldsize).

To work around this issue, added a popup at game start with the very nice help of Claude code Opus 4.7 thanks.

Change in `onGameStart` in [CvEventManager.py](/Assets/Python/CvEventManager.py).

## 128 - (Seemingly fixed / worked around) Runtime UI define/style changes could produce crashy Python-like behavior

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1AYFGqYFp___B0N1Sph-g1KfJEJMFBHuB?usp=sharing).

Observed issue 1:

- Military Advisor read some SAS XML UI defines directly in the constructor.
- Changing those defines while Civ4 was running could produce crashy behavior similar to hot-changing Python code during runtime.
- After changing the Military Advisor to a lazy/sentinel define cache initialized after screen setup starts, runtime XML define changes have no effect until the expected Civ4 restart, and the game keeps running normally.

Observed issue 2:

- While documenting/testing the Sevopedia expanded-text playground, Civ4 sometimes crashed when exiting through the Windows red X after a sequence like opening the Info Screen Score Tab, loading a save, browsing Sevopedia, and changing playground styles/backgrounds.
- The crash could not be reproduced reliably after the fixes below, so the exact root cause is not proven.
- Crash dump signature from `crashdmp_styles.txt`: `INVALID_POINTER_WRITE_c0000005`, `ntdll!RtlpWaitOnCriticalSection`, with `Cannot read DebugInfo address ... Possible causes: The critical section is not initialized, deleted or corrupted`.

Likely cause / workaround:

- For issue 1, Military Advisor now uses lazy/sentinel define caching initialized after screen setup starts, following the safer Tech Chooser/Main Interface style. It checks each cached define sentinel, not only the first one, so partially initialized define state does not persist. Empirically this seems like a consistent and reliable fix.

- For issue 2, Sevopedia playground initially cached style/background lists at module import time. It now lazy-inits them only when the expanded text playground first needs them, similar in spirit to the safer advisor define-cache pattern.
- The background playground also initially included `MAINMENU_SCENE*` art keys, which point to `.nif` / `.kfm` scene assets. These are not valid for `addDDSGFC`, so the playground now only offers `.dds` background art keys.
- This is considered a workaround / seeming fix because the native crash happened later at shutdown and the dump does not identify the exact Python call site. Empirically, this issue was harder to reproduce so this is likely to fix it but not as certain.

Files changed:

- [Assets/Python/Screens/CvMilitaryAdvisor.py](/Assets/Python/Screens/CvMilitaryAdvisor.py)
- [Assets/Python/Contrib/Sevopedia/_sevopedia_helpers.py](/Assets/Python/Contrib/Sevopedia/_sevopedia_helpers.py)

## 129 - (Fixed) Military Advisor Map tab minimap disappeared after switching tabs

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1GKzU-m50WLj0CUBHCJPxTPbHfrJ33izg?usp=sharing).

Observed issue:

- In the (base) Military Advisor, after we added new tabs (Battles and Composition, and named "Map" (tab) the original advisor screen view), the Map tab minimap initially displayed correctly when opening the advisor.
- After switching from Map to another Military Advisor tab (Battles or Composition) and then back to Map, the minimap area no longer rendered correctly.
- Earlier attempts changed the symptom but did not fully fix it: `bringMinimapToFront()` alone did not restore the minimap; deleting/recreating several widgets could still leave a blank/blue map area; trying to reuse the minimap after `hideScreen()`/`interfaceScreen()` avoided some covering but could show the advisor background instead of the minimap.
- Exiting the Military Advisor and reopening it restored the minimap.
- The BUG Military Advisor variant did not show this issue when switching between its tabs.

Fix:

- Military Advisor tab switches now redraw the advisor contents in place instead of calling `hideScreen()` and then `interfaceScreen()` again.
- The redraw deletes page-owned widgets only, while leaving the screen shell and minimap frame alive.
- The Map tab initializes the minimap once per real advisor opening, then refreshes/re-fronts it when returning to Map.

Notes:

- The exact native/root cause was hard to pinpoint, so this entry describes the observed behavior and the empirically fixed redraw pattern rather than claiming a precise engine cause.
- The fix follows the practical shape of the BUG Military Advisor, which keeps its screen alive during tab changes and rebuilds tab contents in place.

Update:

- Later, while optimizing the new Battles tab, we tried to preserve the built Battles table across full Military Advisor close/reopen by making the whole advisor screen persistent with `screen.setPersistent(True)`.
- This was a performance optimization only: it made very large late-game battle histories faster to reopen after closing the advisor.
- However, this persistent-screen approach was reverted because Civ4's native minimap did not survive that lifecycle reliably.
- Same-open Military Advisor tab switching remained lightweight and stable as long as the advisor was not exited.
- But after exiting and reopening the Military Advisor, the Map tab minimap became an empty blue panel instead of rendering the map.
- Debug mode could trigger the same broken minimap state, and turning debug mode back off did not restore it; only save reload did.
- Final behavior: keep the in-place tab redraw/cache path for same-open tab switching, but keep the whole Military Advisor screen non-persistent with `screen.setPersistent(False)`.
- Trade-off: the Battles table cache is no longer preserved across full Military Advisor close/reopen, so very large late-game battle histories may reopen slower.
- This is preferred because the Map tab should always render correctly, while the extreme late-game battle-history reopen case is rarer.

File changed:

- [Assets/Python/Screens/CvMilitaryAdvisor.py](/Assets/Python/Screens/CvMilitaryAdvisor.py)

## 130 - (Fixed) Base AdvCiv bug of unit rows showing build player name instead of improvement text (Military Advisor Map tab)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1JlEvBQFzfi190KXv8fGHIm_84MK8yuHZ?usp=sharing).

Observed issue:

- In the Military Advisor Map tab's expanded individual-unit list, worker rows could display bad text such as `Build a PC` or just `PC` where the worker build/improvement text should be clear.
- Other unit rows could also show the selected player's owner name suffix (`PC`) at the end, which was redundant because the list already belongs to the selected player.

Cause:

- Python called `CyGameTextMgr().getSpecificUnitHelp(loopUnit, true, false)`, which exposed only the default `setUnitHelp` path.
- The underlying DLL `setUnitHelp` already had a `bOmitOwner` parameter, but Python could not request it, so owner text was always appended.
- Trying to patch the formatted Python string after the fact was fragile because the row text is already markup-heavy and listbox-rendered.

Fix:

- Added `CyGameTextMgr::getSpecificUnitHelpOmitOwner` and exposed it to Python.
- The Military Advisor Map tab now uses that wrapper for expanded individual-unit rows, preserving DLL-generated build/improvement text while omitting the redundant owner suffix.

Note: this also fixes stray leader name in unit rows, which was unneeded since selected leader is already visible

Files changed:

- [Assets/Python/Screens/CvMilitaryAdvisor.py](/Assets/Python/Screens/CvMilitaryAdvisor.py)
- [CvGameCoreDLL/CyGameTextMgr.cpp](/CvGameCoreDLL/CyGameTextMgr.cpp)
- [CvGameCoreDLL/CyGameTextMgr.h](/CvGameCoreDLL/CyGameTextMgr.h)
- [CvGameCoreDLL/CyGameTextMgrInterface.cpp](/CvGameCoreDLL/CyGameTextMgrInterface.cpp)

## 131 - (Fixed) Base AdvCiv bug of live unit build action text not being space-separated from its turn timer

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1xDeaoGO7bKYsx7E4qDUkWAmstu43QnCF?usp=sharing).

Observed issue:

- Live worker unit help displayed build action and timer without a separating space, e.g. `Build a Road(3)` instead of `Build a Road (3)`.
- This was visible in the Military Advisor Map tab's expanded individual-unit rows and also in map-view unit hover help.

Cause:

- `CvGameTextMgr::setUnitHelp` appended `GC.getInfo(eBuild).getDescription()` and then immediately appended the formatted timer string `(%d)` or `(%d+1)`.

Fix:

- Added the leading space to the formatted build timer strings in `CvGameTextMgr::setUnitHelp`, so all live-unit help contexts using this path show the same clearer spacing.

File changed:

- [CvGameCoreDLL/CvGameTextMgr.cpp](/CvGameCoreDLL/CvGameTextMgr.cpp)

## 132 - (Enhanced) Base AdvCiv issue of not showing rival gold-per-turn on Foreign Trade Advisor Bonuses tab when not connected to their trade network

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1BfRysfE4onN1RS3xczU_jKsf2UMmEdID?usp=sharing).

Base AdvCiv hides a rival's gold-per-turn on the Bonuses tab when not connected to their trade network (GPT is still gated on `isGoldTrading()`, i.e. the Currency tech). The info is already available in Diplomacy, so we just keep it visible here too to avoid opening Diplomacy each turn (also matches the Techs tab, where flat gold via `AI_maxGoldTrade` stays visible regardless of trade-tech state, as long as `isGoldTrading()` is true).

For some unknown AdvCiv-SAS-specific reason the pre-existing "Not Connected to Trade Network" row-overlay label then overlaps the now-shown GPT number. Worked around by prepending tabs to the message so it renders past the GPT column.

File changed:

- [Assets/Python/Screens/CvForeignAdvisor.py](/Assets/Python/Screens/CvForeignAdvisor.py)

## 133 - (Fixed) Base AdvCiv issue of Sevopedia Index's legacy sort-key cleanup (`TXT_KEY_*` prefix-strip + `"The X"` comma-flip) scattering untranslated entries instead of clustering them (hurts diagnosis of missing translations), sorting items differently than the type-specific pedia pages and than natural alphabetical order, and incurring needless per-entry build-time cost (especially wasteful in non-English locales)

Concrete shape of the change (one representative loop per pattern):

```python
# Before - "The X" comma-flip on techs
for item in techList:
    if (item[0][0:4]=="The "):
        list.append([item[0][4:]+","+item[0][0:3],"Tech",item])
    else:
        list.append([item[0],"Tech",item])

# After
for item in techList:
    list.append([item[0],"Tech",item])
```

```python
# Before - TXT_KEY_UNIT_ prefix strip on units
for item in unitList:
    if (item[0][:13]=="TXT_KEY_UNIT_"):
        list.append([item[0][13:].capitalize(),"Unit",item])
    else:
        list.append([item[0],"Unit",item])

# After
for item in unitList:
    list.append([item[0],"Unit",item])
```

Same shape applied to the other types that had similar branches (`promotionList`, `buildingList`, `nationalWonderList`, `worldWonderList`, `projectList`, `specialistList`, `civicList`). `traitList`'s `item[0][2:]` strip was kept — it's a different pattern (trims a 2-char leading prefix unrelated to TXT_KEY or "The X") and a sibling code comment flags that explicitly.

Earlier revisions of `SevoPediaIndex.buildIndex()` normalized the alphabetical sort key for two patterns:

- **`TXT_KEY_*` prefix strip + capitalize.** Entries whose translation was missing fell back to the raw XML key (e.g. `TXT_KEY_UNIT_WARRIOR`). The code stripped the `TXT_KEY_UNIT_` prefix and capitalized the remainder so the entry sorted under "W" (like the intended "Warrior") instead of "T".
- **`"The X"` comma-flip.** Items like `"The Wheel"` or `"The Pyramids"` were rewritten as `"Wheel,The"` so they sorted under W/P, library-card style.

Both were dropped in favour of using the raw name directly. Reasoning:

1. **Cross-page inconsistency *within* Sevopedia.** Only Index ran this cleanup; the type-specific pedia pages (Techs, Units, Buildings, ...) show raw names sorted naturally via `getSortedList()`. So the *same* item appeared under different letters depending on the page — `"The Wheel"` was under **W** in Index but **T** in Techs; an untranslated `TXT_KEY_UNIT_WARRIOR` was under **W** in Index but **T** in Units. Two contradictory sort orders side by side, confusing anyone flipping between Index and a type-specific page.
2. **Lost diagnostic signal — and Index is the natural place for that signal.** The strip scattered untranslated entries across the alphabet (sorted under their cleaned-up first letter) while still showing the raw `TXT_KEY_X` in the cell, so broken keys looked like isolated glitches instead of a single visible cluster under "T" — harder for both mod authors *and* players to notice, report, or batch-fix. This matters especially for Index, because it's the *only* pedia page that flattens every content type into one alphabetical view; auditing missing translations elsewhere means opening Techs, then Units, then Buildings, etc., one type at a time. Bonus: with the strip gone, the search bar can now filter every broken entry at once by typing `txt`, since search compares against the same sort key.
3. **Code complexity for no functional benefit.** Each loop had 2-3 conditional branches doing per-entry slice-and-compare. List-building is now one direct `list.append(...)` per type — easier to read and maintain.
4. **Needless per-entry cost, especially harsh for any future non-English locale.** The work is one-shot (gated by `if self.index: return`) so the English runtime cost was small, but still paid across hundreds of items on nearly-always-false checks. The `"The X"` comma-flip is *literally* English: in German (`"Das Rad"`), French (`"La Roue"`), etc. the `item[0][0:4] == "The "` check would never match, but the slice-and-compare would still run across the whole catalog with a 100% miss rate. Tiny future-proofing for any eventual localization. (The `TXT_KEY_*` strip is locale-neutral in detection, so this critique applies cleanly only to the `"The X"` flip.)

Side-effect: also fixes incorrect alphabetical ordering. `"The Pyramids"` (starts with T) was sorted under P; `"The Wheel"` (starts with T) was sorted under W. The comma-flip was a library-card stylistic convention layered on top — the rest of the pedia categories never applied it — so Index is now both correct *and* consistent with them.

Summary:

Earlier `SevoPediaIndex.buildIndex()` built separate sort keys for some entries:

- `TXT_KEY_UNIT_WARRIOR` was sorted like `Warrior`.
- `"The Wheel"` was sorted like `Wheel,The`.

We removed that cleanup and now use the displayed item name directly, matching the type-specific Sevopedia pages.

Why:

- Index and category pages should not sort the same item under different letters.
- Broken translations are easier to spot when raw `TXT_KEY_*` entries cluster under `T`; the Index is the best whole-catalog page for that.
- The old branches added code and per-entry checks for little benefit, including an English-only `"The "` rule.

`traitList` keeps its `item[0][2:]` trim because traits intentionally prepend an icon plus space before the name; that is a different case.

File changed:

- [Assets/Python/Contrib/Sevopedia/SevoPediaIndex.py](/Assets/Python/Contrib/Sevopedia/SevoPediaIndex.py)

## 134 - (Fixed) Base AdvCiv issue: Foreign Diplomacy Advisor Glance tab column icons overflow horizontally with 24+ rival players

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1pkm3MTTVMVBuVA1uiW1r70Z1_T8I5q-G?usp=sharing).

Observed issue:

- In Foreign Diplomacy Advisor, Glance tab, the column header icons (one per rival player) overflowed the screen width when there were 24+ rival players (e.g., for worldsize SAS48).
- Vertical scrolling worked fine; only the horizontal axis was affected.
- Root cause is Base AdvCiv's `initializeGlance` formula: `X_Spread = W_SCREEN / nCount` with a hard minimum of 57 px (originally 58). With many players, `nCount` grows while `W_SCREEN` stays fixed, so `X_Spread` hits the floor and the total content width (`57 × nCount`) exceeds the panel width. The panel is created at exactly `W_SCREEN` wide, so icons past that boundary are clipped.
- Switching to a table widget was considered but rejected because it would lose the per-cell widget type interactions (attitude popups, war-trade clicks, leaderhead hover). Horizontal scrolling was also considered but the header and row panels are separate, so they cannot scroll in sync.

Fix applied:

- Added column pagination to the Glance tab: columns are split into pages of as of now 16 players, navigated with standard left/right arrow buttons (same `BUTTON_STYLE_ARROW_LEFT/RIGHT` style used by `CvInfoScreen`'s graph).
- `X_Spread` now uses `GLANCE_PAGE_SIZE + 1` as denominator (the `+1` preserves the original left-slot convention, which reserved one slot for the active player who has no column icon), so 16 columns fit the advisor width at 1080p with the 57 px floor comfortably satisfied.
- Page size 16 fits worldsize Huge well and displays cleanly at 1080p; for SAS48 player counts it yields around 3 pages which also displays fine at 1080p.
- Arrows are only drawn when `iGlanceNumPages > 1` (i.e. more than 16 rivals), so small games are unaffected.

Files changed:

- [Assets/Python/Screens/CvForeignAdvisor.py](/Assets/Python/Screens/CvForeignAdvisor.py)

## 135 - (Fixed) Likely Base AdvCiv issue: turn-status text collided with the diplomacy screen

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1kSSAaxUo26z95-Hmh8LJBZlMeRNq2v0w?usp=sharing).

Observed issue:

- The shared turn-status label `EndTurnText` (e.g. "Waiting for other Civilizations...", the end-of-turn prompt) is placed just above the bottom HUD panels (Base AdvCiv: `... - VSPACE(25)`). With the diplomacy (leaderhead) screen open, it falls within the dialog's lower area and is drawn behind it in z-order, so it is partly hidden and visually collides.
- Not verified in unmodified Base AdvCiv, but the positioning is Base AdvCiv code, so this is likely a base issue rather than AdvCiv-SAS introduced.

Fix applied:

- Positioned `EndTurnText` below the diplo dialog instead of raised above the bottom HUD (a positive `iEndTurnTextRaise` offset below the bottom-corner-panel top), so it renders in the clear gap between the dialog and the bottom HUD. Tunable local constant.

Files changed:

- [Assets/Python/Screens/CvMainInterface.py](/Assets/Python/Screens/CvMainInterface.py)

## 136 - (Open - likely Base AdvCiv lineage or maybe bad local installation/configuration, deprioritized) Choose-production popup does not re-fire when a city finishes production; city then sits idle for many turns

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1Ho_cqJnuF1ICE5hJSiGKfswa6UrHza4G?usp=sharing).

Observed issue:

- The "What would you like X to work on?" popup fires correctly when a city is founded, but does NOT re-fire when an existing city finishes its current production. The city then sits at empty production for many turns, wasting hammers. Manually opening the city screen still lets the player pick production normally.
- Reproduced across savegames and versions: AdvCiv-SAS 5814 (current) and 5500 (last stable) show the "empty production" form. 5400 (previous stable) and unmodified Base AdvCiv show a sibling form ("no production when production finishes"). So this is NOT a recent AdvCiv-SAS regression: it predates 5500 and a related behavior exists in Base AdvCiv (or could it be a local installation/configuration issue?).

Investigation (with the help of Claude code Opus 4.7 thanks) (no fix applied):

- Full popup path traced: DLL -> Python (`CvGameInterface.skipProductionPopup` / `AI_chooseProduction`) -> BUG gameUtils dispatch -> popup queue. The committed decision path is correct end to end: both hooks default to `False` (show popup, do not auto-pick), no AdvCiv-SAS gameutils handler overrides them, and BUG isolates per-turn handler exceptions so they cannot block the native popup.
- No Python traceback in PythonErr.log on tested turns; the `getInfoTypeOrFail` refactor is largely ruled out (no ValueError logged, and BUG would isolate it anyway).
- Leading hypothesis: popup-queue starvation. AdvCiv adds the choose-production popup with `bForce=false`, which BtS silently drops if another popup is already up / perpetually re-queued. Matches the symptom (popup never surfaces, but manual city entry bypasses the queue).

Status / next steps:

- Deprioritized: longstanding, partly Base AdvCiv lineage, intricate popup-queue area, not a recent regression. Acceptable to live with for now.
- If revisited: bisect the 5400 <-> 5500 stable range to localize the flavor change, check Base AdvCiv on-completion popup path, and capture PythonErr.log / PythonDbg.log on a turn where a city goes idle (look for a stuck/looping custom popup or a BUTTONPOPUP_PYTHON whose callback raises).

## 137 - (Fixed) Beyond the Game mod issue: BTG Cross reused Huge grid size for every world size of Huge and below

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1KDHuNYPShhNg9V_guuIc-4SrRQ8cPk-l?usp=sharing).

Observed issue:

- `BTG_Cross.py` returned the same Huge anchor grid for every world size of Huge and below, including our SAS ARENA size, so several selected options produced the same effective map dimensions at all those sizes (e.g. 60x60 plots).
- SAS24 and larger still scaled because they used the separate extrapolation path.
- User testing confirmed the same behavior in the original Beyond the Game mod map script that BTG Cross came from, so this was inherited rather than introduced by AdvCiv-SAS.

Fix applied:

- World sizes of Huge and below now scale from the selected Huge anchor instead of returning it directly.
- The existing SAS24+ extrapolation path was kept unchanged.

File changed:

- [PrivateMaps/BTG_Cross.py](/PrivateMaps/BTG_Cross.py)

## 138 - (Fixed) Base AdvCiv issue: Global Highlands map sizes were too large

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1EdJwj7SOhV0lvtPBZjVNMC4I_uZ6U3UW?usp=sharing).

Observed issue:

- `Global_Highlands.py` needs larger-than-normal grids because many plots become peaks, but its old size table was still empirically too large.
- User testing confirmed the same oversized-map issue in Base AdvCiv, so this was inherited rather than introduced by AdvCiv-SAS.
- The important indexing detail is the same map-script pitfall as elsewhere: `argsList[0]` / `CyMap().getWorldSize()` are runtime XML world-size indices with ARENA at 0 and Huge at 6, not the old `WorldSizeTypes.WORLDSIZE_*` enum where Huge is 5.

Fix applied:

- Retuned Global Highlands down by one old-size step while keeping the peak-heavy map larger than ordinary scripts; e.g. Huge now uses old Large's `(32,20)` instead of old Huge's `(38,24)`.
- SAS24+ and larger still calibrate from the Huge anchor through the shared [SAS_WorldSizeUtils.py](/Assets/Python/SAS_WorldSizeUtils.py) helper.

File changed:

- [PrivateMaps/Global_Highlands.py](/PrivateMaps/Global_Highlands.py)

Update: now added AdvCiv-SAS new worldsizes (as of now ARENA, SAS24, SAS32, SAS40,, SAS48) to DLL too.

## 139 - (Fixed) Base AdvCiv issue: Foreign Advisor BUG menu made Glance attitude dropdown look attached to Enhanced Info Tab

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1qEI8Msow1oHdDwIVqpshRy6jiQGOrdxA?usp=sharing).

Observed issue:

- In base AdvCiv 1.12, the Foreign Advisor BUG menu displayed the "Enhanced Info" (Tab) checkbox on the same visual row as the Numbers/Smilies/Both attitude dropdown.
- That dropdown controls Glance-tab attitude display, not the Info tab, but the "Glance Tab" show/hide checkbox was on a separate row. This made the dropdown look like it belonged to "Enhanced Info Tab" instead of to the Glance tab.

Fix applied:

- Removed the obsolete `EFAImprovedInfo` BUG-menu checkbox and config option because AdvCiv-SAS always uses `drawInfoImproved` for the Info tab.
- Kept `EFAGlanceAttitudes` as its own visible dropdown with the explicit label "Glance Tab Attitudes", so the setting reads as a separate Glance-tab display option.
- Kept the old `EFAGlanceTab` and `EFACityTrades` visibility options disabled because those Foreign Advisor tabs are now always shown.

Remaining caveat:

- Showing both attitude numbers and smilies adds an extra attitude glyph next to text in tight Glance-tab cells. After Glance-tab pagination capped the number of players per page, Large Pangaea/default-player testing showed the combined mode still renders well when upscaled, including a long `-17` plus at-war and worst-enemy icon case. Higher-player games were not tested here and may behave differently. This is why AdvCiv-SAS defaults to Both while keeping the display mode configurable and the Glance players-per-page cap tunable for tighter cases.

Files changed:

- [Assets/Python/BUG/Tabs/BugAdvisorOptionsTab.py](/Assets/Python/BUG/Tabs/BugAdvisorOptionsTab.py)
- [Assets/Config/BUG Advisors.xml](/Assets/Config/BUG%20Advisors.xml)
- [Assets/XML/Text/AdvCiv-SAS_main.xml](/Assets/XML/Text/AdvCiv-SAS_main.xml)

## 140 - (Fixed) Base AdvCiv issue: Foreign Advisor Glance tab showed incorrect and inconsistent +0 attitude display in self cells

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1bipOz4VPLNGrY5QNuolx0M7dwlkJaaej?usp=sharing).

Observed issue:

- In base AdvCiv 1.12, the Foreign Advisor Glance tab could show `+0` in diagonal cells where the row player and column player are the same player.
- Those cells are not real attitude modifiers against another player. Showing `+0` made them look like actual attitude data.
- In Both mode, this was also visually inconsistent: real `+0` relation cells showed the attitude icon plus `+0`, while self cells showed only `+0`.

Fix applied:

- Leave player-vs-itself Glance cells empty.
- Use a neutral widget for those cells so they do not imply a real relation tooltip.

File changed:

- [Assets/Python/Screens/CvForeignAdvisor.py](/Assets/Python/Screens/CvForeignAdvisor.py)

## 141 - (Fixed) Sevopedia media player 3D audio previews became very quiet after entering a game

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/19fxsbguuB2uZBY9rfeiXfcSzSaPN591z?usp=sharing).

Observed issue:

- Sevopedia Media Player civilization Select/Order sounds previewed correctly from the main menu.
- After entering a game, the same Sevopedia previews became much quieter.
- Returning to the main menu did not fix the volume; restarting the game was required.
- Normal in-game unit/civilization select/order sounds were not tested but are believed to have been working before, so this was treated as a Sevopedia preview problem rather than a gameplay sound problem.

Investigation:

- `CyAudioGame().Play3DSoundWithId(iSoundId, 0, 0, 0)` (original implementation before the fix) played the right 3D script, but very quietly.
- `CyInterface().playGeneralSoundByID(iSoundId)` played sound at the right volume ingame (loud enough), but it was the wrong sound because 3D script IDs are not the same namespace as general/2D sound IDs.
- `CyInterface().playGeneralSound("AS3D_...")` played the right sound at normal volume when given the actual script string. The problem was that the Sevopedia civilization Select/Order entries only had the integer 3D script ID from APIs such as `getSelectionSoundScriptId()` / `getActionSoundScriptId()`. Calling `CyInterface().playGeneralSoundByID(iSoundId)` with that integer did not work because it interpreted the same number in the general/2D sound namespace and therefore played the wrong sound.

Fix applied:

- Initial implementation: python-only solution:

```python
from _sevopedia_main_groupings import _SAS_findAssetXmlPath, _SAS_extractTagValue

SAS_AUDIO_3D_SCRIPTS_BY_ID = None

def _SAS_getAudio3DScriptsById():
	global SAS_AUDIO_3D_SCRIPTS_BY_ID
	if SAS_AUDIO_3D_SCRIPTS_BY_ID is not None:
		return SAS_AUDIO_3D_SCRIPTS_BY_ID
	SAS_AUDIO_3D_SCRIPTS_BY_ID = {}
	szScript = None
	iScriptId = 0
	szAudio3DPath = _SAS_findAssetXmlPath("Audio3DScripts.xml", "XML\\Audio")
	try:
		f3 = open(szAudio3DPath, "r")
		for line in f3:
			if "<ScriptID>" in line:
				szScript = _SAS_extractTagValue(line, "ScriptID")
			elif "</Script3DSound>" in line:
				if szScript:
					SAS_AUDIO_3D_SCRIPTS_BY_ID[iScriptId] = szScript
				iScriptId += 1
				szScript = None
		f3.close()
	except:
		SAS_AUDIO_3D_SCRIPTS_BY_ID = {}
	return SAS_AUDIO_3D_SCRIPTS_BY_ID
```

The Python-only implementation rebuilt the missing reverse lookup from `Audio3DScripts.xml`: first `Script3DSound` entry became ID `0`, second became ID `1`, and so on. This matched the 3D script IDs returned by the existing Python APIs, so Sevopedia could resolve `iSoundId -> AS3D_...` and then call `CyInterface().playGeneralSound(sz3DScript)`. The `playSound` method was changed from this:

```python
	def playSound(self, szSoundScript, iSoundId, bForce3D):
		self.soundId = None
		self.is3DSound = False

		if (not szSoundScript) and iSoundId == -1:
			return

		try:
			if iSoundId != -1:
				if bForce3D:
					self.soundId = CyAudioGame().Play3DSoundWithId(iSoundId, 0, 0, 0)
					self.is3DSound = True
				else:
					self.soundId = CyAudioGame().Play2DSoundWithId(iSoundId)
			else:
				if szSoundScript.startswith("AS3D_"):
					# 3D scripts need Play3DSound
					self.soundId = CyAudioGame().Play3DSound(szSoundScript, 0, 0, 0)
					self.is3DSound = True
				else:
					self.soundId = CyAudioGame().Play2DSound(szSoundScript)
		except:
			self.soundId = None

		if self.soundId is None or self.soundId == -1:
			if szSoundScript:
				CyInterface().playGeneralSound(szSoundScript)
			self.soundId = None
			self.is3DSound = False
```

to this:

```python
	def playSound(self, szSoundScript, iSoundId, bForce3D):
		self.soundId = None
		self.is3DSound = False

		if (not szSoundScript) and iSoundId == -1:
			return

		try:
			if iSoundId != -1:
				if bForce3D:
					# self.soundId = CyAudioGame().Play3DSoundWithId(iSoundId, 0, 0, 0)
					# self.is3DSound = True
					# <!-- custom: The fix is only for Sevopedia's media player. The observed problem was that civilization Select/Order sounds previewed correctly from the main menu, but after entering a game the same Sevopedia previews became much quieter; returning to the main menu did not fix them, and the game had to be restarted. What the fix does:
					#
					# Some Sevopedia music entries store iSoundId, which for 3D sounds is a 3D script index, not a normal 2D/general sound ID.
					# Calling CyAudioGame().Play3DSoundWithId(iSoundId, 0, 0, 0) plays the right 3D script but very quietly.
					# Calling CyInterface().playGeneralSoundByID(iSoundId) played the wrong sound, because that ID belongs to a different audio namespace.
					# So the code maps iSoundId back to the actual script name, e.g. AS3D_AMERICA_SELECT.
					# Then it calls CyInterface().playGeneralSound("AS3D_AMERICA_SELECT"), which plays the right sound at good volume.
					# Why parse XML again?
					#
					# Because Python gets only the integer from civInfo.getSelectionSoundScriptId() / getActionSoundScriptId(). It does not expose the original XML string AS3D_AMERICA_SELECT.
					#
					# The DLL knows the mapping internally because XML loading did:
					#
					# gDLL->getAudioTagIndex("AS3D_AMERICA_SELECT", AUDIOTAG_3DSCRIPT)
					# but Python only receives the resulting index. The current Python API does not expose a reverse lookup like:
					#
					# gc.getAudio3DScriptName(iSoundId)
					# A DLL helper could be added, but for this Sevopedia-only fix it would need extra DLL work for the same
					# reverse-map purpose. So we rebuild that reverse lookup from Audio3DScripts.xml:
					#
					# 0 -> AS3D_...
					# 1 -> AS3D_...
					# ...
					# iSoundId -> AS3D_AMERICA_SELECT
					# We cache it in SAS_AUDIO_3D_SCRIPTS_BY_ID, so XML is parsed only once per Python session, not every playback.
					#
					# In short: we parse XML because Python knows the ID but not the script string, and the string is the only form that plays correctly through CyInterface().playGeneralSound(...). (GPT-5.5?) -->
					sz3DScript = _SAS_getAudio3DScriptsById().get(iSoundId, "")
					if sz3DScript:
						CyInterface().playGeneralSound(sz3DScript)
					else:
						self.soundId = CyAudioGame().Play3DSoundWithId(iSoundId, 0, 0, 0)
						self.is3DSound = True
						return
					self.soundId = None
				else:
					self.soundId = CyAudioGame().Play2DSoundWithId(iSoundId)
			else:
				if szSoundScript.startswith("AS3D_"):
					# self.soundId = CyAudioGame().Play3DSound(szSoundScript, 0, 0, 0)
					# self.is3DSound = True
					CyInterface().playGeneralSound(szSoundScript)
					self.soundId = None
				else:
					self.soundId = CyAudioGame().Play2DSound(szSoundScript)
		except:
			self.soundId = None

		if self.soundId is None or self.soundId == -1:
			if szSoundScript:
				CyInterface().playGeneralSound(szSoundScript)
			self.soundId = None
			self.is3DSound = False
```

Works, but not preferred because:

- It made Sevopedia parse audio XML to recover data that conceptually belongs to the DLL/audio-loading layer.
- It was less reusable: any other Python code with a 3D script ID would need to copy or import the same helper.
- It duplicated the same reverse-map purpose that the DLL can expose once as a general API.
- A C++ implementation may also possibly be better than a Python-only implementation in terms of performance.

Final solution:

- Added DLL/Python API `gc.getAudio3DScriptName(iSoundId)` to resolve any 3D audio script ID back to its `AS3D_...` script name.
- The DLL caches `Audio3DScripts.xml` once and exposes the reverse lookup to Python.
- Sevopedia uses the script name with `CyAudioGame().Play3DSound(szScript, -1, -1, -1)` for 3D previews and falls back to the old quiet 3D playback path only if the helper is unavailable or returns empty.

Update:

- After the normal-volume fix, fast Next/Prev through generic 3D script-browser previews could stack long or looping `AS3D_...` sounds. These sounds persisted after leaving Sevopedia, including in the main menu and ingame. The issue was that `CyInterface().playGeneralSound("AS3D_...")` returns no sound handle, so `stopSound()` could not destroy that playback.
- Handle-based `CyAudioGame().Play3DSound(szSoundScript, 0, 0, 0)` for generic `AS3D_...` script-name previews fixed the persistent stacked sound issue, but testing showed it could also break later normal ingame Select/Order and other sounds.
- Final follow-up: `CyAudioGame().Play3DSound(szScript, -1, -1, -1)` fixed generic `AS3D_...` script-name previews too. It keeps normal volume and returns a handle, so `stopSound()` can call `Destroy3DSound()` before replay/Next/Prev and when leaving Sevopedia. (GPT-5.5)

Note: untested, but as a side-effect might have also fixed some 3D sounds not playing correctly that now seemingly do (would need to check).

Files changed:

- [CvGameCoreDLL/CyGlobalContext.cpp](/CvGameCoreDLL/CyGlobalContext.cpp)
- [CvGameCoreDLL/CyGlobalContext.h](/CvGameCoreDLL/CyGlobalContext.h)
- [CvGameCoreDLL/CyGlobalContextInterface1.cpp](/CvGameCoreDLL/CyGlobalContextInterface1.cpp)
- [Assets/Python/Contrib/Sevopedia/SevoPediaMediaPlayer.py](/Assets/Python/Contrib/Sevopedia/SevoPediaMediaPlayer.py)

## 142 - (Fixed) Base AdvCiv issue: Military Advisor Map tab debug mode did not draw the full minimap section

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1DDd5g7JVnyMjDNqnSBjzzy0xvpuCAVWp?usp=sharing).

While investigating why a Celt leader still had only one city around turn 100, the Military Advisor Map tab showed other players' units in the active player's known part of the minimap, but the Celt units could not be located from that tab. The missing settler was on another continent outside the active player's known map area.

The unit visibility itself was already fine in debug mode. The issue was that the Map tab minimap was still drawn as the active player's known minimap section, even though debug mode exposes the full map and the Map tab leader bar can select alive players outside the active player's revealed area.

Fix:

- In normal play, keep drawing the active player's known minimap section.
- In debug mode, draw the full minimap section with `screen.updateMinimapSection(gc.getGame().isDebugMode(), False)`.
- This made the Celt settler visible on the Military Advisor Map tab and allowed its location to be diagnosed.

File changed:

- [Assets/Python/Screens/CvMilitaryAdvisor.py](/Assets/Python/Screens/CvMilitaryAdvisor.py)

## 143 - (Fixed) BUG configobj comment writer used undefined `_a_to_u` instead of correct `self._a_to_u`; old BUG syntax had prevented Ruff from seeing the bug

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1Bf5UFQRGomY2zIMehjmKAt6CLlp5cbQJ?usp=sharing).

While cleaning old Python 2-style BUG syntax so modern Python 3 linters/parsers can inspect it while keeping Civ4 Python 2.4 compatibility, we replaced old comma-exception (`except Exception, e:`) binding with `except X:` plus `sys.exc_info()[1]` where the exception object was still needed. These old formatting/syntax patterns can prevent linters from analyzing later code and distract the lint output with parser noise instead of real runtime issues. In the same cleanup context, `configobj.py` also had a parser blocker at its very old `True, False = 1, 0` compatibility fallback. That fallback is kept, but the assignment is now run through `exec(...)` so modern parsers can continue through the file.

After those parser blockers were removed, Ruff could inspect more of `configobj.py` and surfaced a real runtime bug in the comment-writing path: `_handle_comment` called `_a_to_u('# ')`, while the correct pattern is `self._a_to_u(...)` because `_a_to_u` is an instance method and nearby code consistently calls it that way. If that branch ran for a comment that did not already start with `#` or `;`, it would raise `NameError`.

Fix:

- Keep the old `True`/`False` compatibility fallback in parser-safe form.
- Convert old comma-exception binding in touched BUG files in a Python 2.4-compatible way.
- Change `_a_to_u('# ')` to `self._a_to_u('# ')`.

File changed:

- [Assets/Python/BUG/configobj.py](/Assets/Python/BUG/configobj.py)

## 144 - (Fixed) Base AdvCiv issue and AdvCiv-SAS settler free window follow-up: AI settlers sometimes do not move away from a high bad plot count start (e.g., high non-bonus tundra and plains): they now scout and hunt for better not very bad sites, and no longer stop at first good-enough site, but instead now rerun evaluate city site again on newly visible plots if a better site (e.g., more food/rivers/fresh water) exists nearby (which we now value more too for first city as well)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1g0qHBH8Jk4fy5QrH4uOdakaVW8iGEwQT?usp=sharing).

This was a base AdvCiv lineage issue and also an AdvCiv-SAS follow-up to our earlier extended first-city founding window.

Observed problem:

- Karakorum could settle a very weak tundra/plains-heavy capital despite a high visible bonus count, because nearby non-food bonuses could make the site look tempting even though the early capital would grow poorly.
- A much stronger nearby capital existed after brief exploration: pig + corn + river + more grassland. This was much better for early growth and long-term snowballing.
- After the first AdvCiv-SAS roaming/scouting fix, the settler could leave the very bad start, but then it could still stop at the first merely good-enough plot it reached instead of checking whether the newly revealed nearby plots were stronger.
- Beijing, which originally had a good enough site at start, but not anymore after our first not high bad plot count fix: after the final fix, it moved to a stronger corn + river home plot rather than stopping at the first acceptable site.

Why the earlier approach was incomplete:

- The first-city roaming fix correctly let settlers briefly scout away from clearly bad BFC shapes instead of founding immediately.
- However, once a scouted plot became heuristic-good-enough, the code could found there immediately.
- That was too early: the whole point of scouting was to get better information, so after reaching a merely acceptable plot, the AI should still re-run first-city evaluation on nearby visible plots before founding.
- Some direct first-city local checks also used non-starting `AI_foundValue(..., false)`, so first-city-specific valuation was not applied consistently to these local rechecks.

Fix:

- For first-city local rechecks in `CvUnitAI::AI_foundFirstCity`, use first-city scoring with `AI_foundValue(..., true)`.
- When a settler reaches a heuristic-good-enough first-city plot after scouting, scan nearby visible reachable plots and compare them with first-city scoring before settling.
- Keep this situational and brief instead of hard-requiring food bonuses or fresh water, because some unusual starts can still be good without them.
- Add first-city-only scoring support in `CitySiteEvaluator`: food bonuses, fresh-water city tiles, and river support are valued more for the capital than for ordinary later city sites, because early capital growth snowballs into faster tile access, worker/settler production, whipping, and specialists.
- Also added BBAI logging to track changes and results more easily.

Result:

- Karakorum moved to the stronger corn + pig + hill-plains river capital site.
- Beijing moved again now to a slightly stronger but mostly identical corn + river capital site.
- The behavior remains first-city-only as of now; later settlers usually know more of the map and can sensibly found strategic/semi-decent resource cities.

Follow-up fix after testing:

- The first version fixed bad-start roaming, but some already-decent starts could still waste turns roaming only to settle the same plot later. Example: London ultimately settled the same capital site, but much later (observed around 22 500 BC instead of 50 000 BC).
- Added an anti-bounce/competitive-current-site guard: if the settler is already on a non-bad foundable first-city plot and the cached city-site target is only marginally better after the same small movement penalty, found instead of walking away and circling back.
- Kept the Karakorum-style fix: clearly bad high-bad-plot starts can still scout/roam during the bounded first-city window, and after reaching a heuristic-good-enough recovery plot, the settler still rechecks nearby visible reachable plots before founding.
- Added more BBAI logging, including high-detail BFC diagnostics at unit log level 3, to show candidate coordinates, found values, adjusted values, path turns, revealed/unrevealed BFC counts, food bonuses, bad plots, and per-tile BFC yields/terrain/feature/bonus data. ChatGPT 5.5 reviewed the logs and helped identify the final narrow anti-bounce/tie-breaker cleanup. Implementation and changes with the help of GPT-5.5 on codex too thanks.
- Retesting preserved the good Karakorum result and fixed the London wasted-wandering case.

Update 2: Fix AI Settler first-city gate and starting-site scoring treating low-food or unusable resources as food bonuses

- The first-city stop-roaming gate and first-city resource scaling could count natural/XML food as a food bonus. In AdvCiv-SAS, Elephants have +1 natural food but their Camp improvement adds no food, so they were incorrectly treated like Pig/Corn-tier food resources; e.g., 3 Elephants could compete too strongly with a Pig + Corn site despite Pig + Corn giving much more food when improved. Inland seafood could also be counted even when the candidate city was not coastal and therefore could not use it like a coastal seafood capital.
- For land resources, count first-city food only when the resource's normal improvement adds food. For water resources, count XML food only when the candidate city is coastal; water improvements are outside the land bonus-improvement helper, but inland seafood should not satisfy the first-city good-enough food gate or capital food-resource scaling.
- This fixed the Karakorum case where the settler could move back toward the tundra-heavy cached start instead of continuing toward the stronger river/pig site, and kept the Maya recovery improved in testing.

Implementation:

Files changed:

- [CvGameCoreDLL/CvUnitAI.cpp](/CvGameCoreDLL/CvUnitAI.cpp)
- [CvGameCoreDLL/CitySiteEvaluator.cpp](/CvGameCoreDLL/CitySiteEvaluator.cpp)
- [Assets/XML/GlobalDefines_advciv_sas.xml](/Assets/XML/GlobalDefines_advciv_sas.xml)

## 145 - (Implemented / needs in-game test) Military Advisor Map tab lost selected leaders after tab switch or close/reopen

In the Military Advisor Map tab, selecting another leader was not preserved when switching to another Military Advisor tab, returning to the Map tab, or closing and reopening the advisor. The Map tab leader selection was reset to the active player each time.

This was tedious in debug mode when comparing leaders, following unit production counts, or repeatedly checking a specific AI's units. It could also be useful in normal play when repeatedly inspecting a known rival from the Map tab.

Cause:

- `drawMap()` reset `selectedUnitList`, then always cleared `selectedPlayerList` and appended `iActivePlayer`.
- The old path also cleared selected unit groups whenever the selected player list was not exactly the active player.
- As a result, the leader bar could not preserve a valid non-active-player selection across tab redraws.

Implemented fix:

- Added `isMapSelectedPlayerValid(iPlayer)` to keep only players that are still selectable.
- Added `restoreMapSelectedPlayers()` to preserve selected leaders while they remain valid.
- Fall back to the active player only when the saved leader selection is empty or invalid.
- Keep the existing `selectedUnitList` reset behavior unchanged.
- Clear selected unit groups only when the preserved leader list had to be sanitized.

File changed:

- [Assets/Python/Screens/CvMilitaryAdvisor.py](/Assets/Python/Screens/CvMilitaryAdvisor.py)

## 146 - (Fixed/Enhanced) Base AdvCiv issue of AI undervaluing coastal settling on naval-heavy maps

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1OavgrKhta9YNPh4a6R7lM4LFqyWMC4Vv?usp=sharing).

After adding naval-heavy map recognition logic in AdvCiv-SAS, another related weakness became easier to notice: on naval-heavy maps such as Archipelago, AI settler found-value logic could still prefer strong inland land-yield sites over strategically better coastal sites.

This is probably a base AdvCiv +/- Civ4 issue or limitation, not only an AdvCiv-SAS issue: normal city-site evaluation does not fully account for the strategic value of coastal access on naval-heavy maps. Coastal capitals can be much stronger than their raw BFC score suggests because they enable early work boats, scouting/contact, coastal trade, first galleys, Moai, and other water-focused buildings or strategies.

Observed example: Inca/Cuzco preferred a central 4-Sugar river grass site over a coastal Pig + Banana + 2-Sugar river site. The inland site was very strong by normal land evaluation, but on an Archipelago-style map the coastal site looks strategically better. Empirical testing showed that the first-city coastal extra value needed to be high in this case: 1700 was still not enough, while 1800 made Cuzco choose the coastal capital.

Fixed/enhanced in `AIFoundValue::evaluate()` by adding tunable flat coastal found-value bonuses on naval-heavy maps.

The first-city value is intentionally much higher because capital coastal access can define the whole opening on naval-heavy maps. The other-cities value is intentionally much lower: testing showed that a value of 200 could make Japan prefer tundra coast over a stronger grass/floodplains site, so the default was kept more moderate.

Note: it seems they often would settle coastal anyway even without this fix/enhancement, but it doesn't seem to have been enforced or strengthened somewhere in the code at a glance before our fix and based on ChatGPT-5.5's review/solution.

## 147 - (Fixed/Enhanced) Base AdvCiv issue of AI settlers not adding extra valuation to unowned bonuses in city-site scoring

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1ZfQRFrKg1MAiIMc-hBczK-0OEXdMY2-T?usp=sharing).

AI settlers could over-prefer locally strong duplicate-bonus sites instead of grabbing new bonus types the empire did not already own.

According to ChatGPT-5.5:

>old AdvCiv/K-Mod had partial resource valuation, but not this explicit rule.
>
>What old/current pre-change logic already did:
>
>- It valued each bonus through nonYieldBonusValue(...), based on AI_bonusVal(eBonus, 1, true).
>- It had some duplicate/surplus handling: bSurplus = (kPlayer.getNumAvailableBonuses(eBonus) > 0), and it reduced value for repeated copies already seen in the same candidate BFC through aiBonusCount.
>- So it was not completely blind to resource value or duplicates.
>
>What it did not have, as far as I can see:
>
>- No clear flat “this is a bonus type my own empire does not already own” nudge.
>- No “count once per distinct unowned bonus type in the candidate BFC” rule.
>- No explicit exclusion of temporary trade imports.
>- No simple empire-diversity correction like: “new Maize > extra Wheat if Wheat is already owned.”

However, a site with better raw local yields can be better for one city short-term, but a site with more unowned bonuses can be better for the whole empire long-term, and often for that city too once global effects apply. Example: **1 new Maize** (+1 health empire-wide, then another +1 health with Granary) can be much better than **2 more Wheat** if Wheat is already owned, even if the Wheat site has better local yields. The same idea applies to new happiness bonuses, strategic resources, Stone/Marble, corporation resources, trade value, or anything unlocked by owning the bonus.

Fixed/enhanced in `AIFoundValue::evaluate()` and tunable with the corresponding SAS define.

The value is applied once per distinct bonus type in the candidate BFC, only after the first city. Trade imports do not count as owned because they are not permanent.

Observed Archipelago example: with a value of 250, Japan settled Osaka northeast for **unowned Molluscs + unowned Maize + unowned Stone** (iron was seemingly not known yet (and otherwise unowned as well)), instead of another site with **already-owned Sheep + unowned Maize + unowned Crab**.

Observed Pangaea Large save 360 example: the change produced different settling points, and by turn 100 some players owned more distinct bonus types.

## 148 - (Fixed) Base AdvCiv issue (and one AdvCiv-SAS issue) of duplicate parent XML keys found by new GitHub workflow check

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1L5ubYioq_8I4hejIZbdV0uRhSKj3FS38?usp=sharing).

While adding [`build/xml_parent_duplicate_keys.py`](/.github/workflows/README.md#buildxml_parent_duplicate_keyspy) to the GitHub workflow checks, [the first CI run](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27258698041/job/80498936912) correctly failed and exposed several duplicate parent XML identifiers. This was a useful validation that the check works, because it caught both old inherited XML duplicates and one AdvCiv-SAS art duplicate.

GitHub Actions output:

```text
Run python .github/workflows/build/xml_parent_duplicate_keys.py
  
FAIL XML duplicate parent keys
  - Assets/XML/Audio/Audio2DScripts.xml: duplicate parent key <ScriptID> AS2D_SONG_DIP_AS_EARLY_PEACE for <Script2DSound> (2 entries)
  - Assets/XML/Audio/Audio2DScripts.xml: duplicate parent key <ScriptID> AS2D_TUTORIAL_BUILD_QUARRY_0 for <Script2DSound> (2 entries)
  - Assets/XML/Audio/AudioDefines.xml: duplicate parent key <SoundID> DIPLO_HANNIBAL_EARLY for <SoundData> (2 entries)
  - Assets/XML/Audio/AudioDefines.xml: duplicate parent key <SoundID> DIPLO_HANNIBAL_LATE for <SoundData> (2 entries)
  - Assets/XML/Audio/AudioDefines.xml: duplicate parent key <SoundID> DIPLO_HANNIBAL_MIDDLE for <SoundData> (2 entries)
  - Assets/XML/Audio/AudioDefines.xml: duplicate parent key <SoundID> DIPLO_WANGKON_EARLY for <SoundData> (2 entries)
  - Assets/XML/Audio/AudioDefines.xml: duplicate parent key <SoundID> SND_CBMN_DIE_VOX for <SoundData> (2 entries)
  - Assets/XML/Audio/AudioDefines.xml: duplicate parent key <SoundID> SND_COMBAT for <SoundData> (2 entries)
  - Assets/XML/Audio/AudioDefines.xml: duplicate parent key <SoundID> SND_TUTORIAL_BUILD_QUARRY_0 for <SoundData> (2 entries)
  - Assets/XML/Art/CIV4ArtDefines_Unit.xml: duplicate parent key <Type> ART_DEF_UNIT_ARCHER_ASIAN for <UnitArtInfo> (2 entries)
Error: Process completed with exit code 1.
```

These were fixed by removing or correcting the duplicate parent entries.

Note, they were all clear duplicates; as for `SND_TUTORIAL_BUILD_QUARRY_0`, it pointed to different sounds, played as such in sevopedia media player too. They are something like:

- 49A "i am going to disable research once again while i explain the next lesson"
- 50A "now build a quarry on this tile, it will take a few turns to complete"

So 50A seems closer to guessedly intended sound, even though it is numerically ordered uncontinuously to other variants. But since we don't use the tutorial and this fixes a duplicate, maybe seems fine and best for this issue attemptedly accurately.

The `ART_DEF_UNIT_ARCHER_ASIAN` case was especially useful because it was an AdvCiv-SAS-side duplicate caused by art-definition cleanup/renaming work (see [KI#19](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#19---unused-or-unclearly-named-art-assets-eg-_asian_chinese_eurasian-mixed-up-and-some-are-used-while-others-are-not)).

This is the kind of XML mistake that can be easy to miss manually because Civ4 XML files are large and repeated identifiers may not always produce an obvious startup error. The new workflow check now catches this class of issue automatically before release.

Note: the workflow intentionally checks only parent-style XML identifiers, such as `*Info` `<Type>`, audio `<ScriptID>`, and audio `<SoundID>`. It does not check child/list duplicate semantics because those can be context-dependent and would risk false positives.

## 149 - (Fixed) Base AdvCiv issue: Duplicate XML text tags found by new GitHub workflow check

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1IVfRbgHLfXdELtT5a6W20fFegfC1O1DG?usp=sharing).

While adding [`build/xml_text_duplicate_tags.py`](/.github/workflows/README.md#buildxml_text_duplicate_tagspy) to the GitHub workflow checks, the [first failing](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27332010214/job/80746523894) run found duplicate `<TEXT>/<Tag>` entries across the XML text files. This was useful because duplicate text keys can silently make one entry shadow another, and the active value can depend on XML load order rather than intent.

GitHub Actions output included these duplicate text tags:

```text
Run python .github/workflows/build/xml_text_duplicate_tags.py
FAIL XML text duplicate tags
  - duplicate <TEXT>/<Tag> AI_DIPLO_DEMAND_TRIBUTE_POWER_STRONGER_MOCTEZUMA_1 (2 entries): Assets/XML/Text/ActualQuotesText.xml: line 1872; Assets/XML/Text/ActualQuotesText.xml: line 1913
  - duplicate <TEXT>/<Tag> AI_DIPLO_GREETINGS_ATT_FR_LEADER_DE_GAULLE_2 (2 entries): Assets/XML/Text/ActualQuotesText_BtS.xml: line 272; Assets/XML/Text/ActualQuotesText_BtS.xml: line 280
  - duplicate <TEXT>/<Tag> AI_DIPLO_STOP_TRADING_1 (2 entries): Assets/XML/Text/ActualQuotesText.xml: line 2058; Assets/XML/Text/CIV4GameText_advc.xml: line 6264
  - duplicate <TEXT>/<Tag> TXT_KEY_BUG_OPTLABEL_FOREIGN_ADVISOR (2 entries): Assets/XML/Text/AdvCiv-SAS_main.xml: line 4110; Assets/XML/Text/BUG_Options_Screen.xml: line 247
  - duplicate <TEXT>/<Tag> TXT_KEY_HINT_16 (2 entries): Assets/XML/Text/CIV4GameText_advc_hints.xml: line 29; Assets/XML/Text/CIV4GameText_advc_hints.xml: line 51
  - duplicate <TEXT>/<Tag> TXT_KEY_HINT_56 (2 entries): Assets/XML/Text/CIV4GameText_advc_hints.xml: line 36; Assets/XML/Text/CIV4GameText_advc_hints.xml: line 326
  - duplicate <TEXT>/<Tag> TXT_KEY_HINT_61 (2 entries): Assets/XML/Text/CIV4GameText_advc_hints.xml: line 81; Assets/XML/Text/CIV4GameText_advc_hints.xml: line 427
  - duplicate <TEXT>/<Tag> TXT_KEY_SHORTCUTS_BUG (2 entries): Assets/XML/Text/AdvCiv-SAS_main.xml: line 4240; Assets/XML/Text/CIV4GameText_Shortcuts.xml: line 55
Error: Process completed with exit code 1.
```

Fix notes:

- `AI_DIPLO_DEMAND_TRIBUTE_POWER_STRONGER_MOCTEZUMA_1`: `CIV4DiplomacyInfos.xml` references `AI_DIPLO_DEMAND_TRIBUTE_POWER_STRONGER_MOCTEZUMA_1_CORRECTED`, and `AdvCiv-SAS_main.xml` already carries that active key. The stale `_1` duplicate in `ActualQuotesText.xml` was removed so the later `_1` entry remains unique.
- `AI_DIPLO_GREETINGS_ATT_FR_LEADER_DE_GAULLE_2`: base BtS had two friendly de Gaulle greeting blocks with the same `_2` key. The modified overrides were moved to `AdvCiv-SAS_main.xml`; the cheese-profile quote stays `_2`, and the "Greatness..." quote is retagged as `_1`, matching the two entries in `CIV4DiplomacyInfos.xml`.
- `AI_DIPLO_STOP_TRADING_1`: `CIV4GameText_advc.xml` keeps the active AdvCiv wording using `%s2` grammar. The older `ActualQuotesText.xml` copy used `%s1` and was removed.
- `TXT_KEY_BUG_OPTLABEL_FOREIGN_ADVISOR` and `TXT_KEY_SHORTCUTS_BUG`: active AdvCiv-SAS English overrides are kept in `AdvCiv-SAS_main.xml`; duplicate base/BUG copies were removed where appropriate.
- `TXT_KEY_HINT_16` and `TXT_KEY_HINT_56`: both duplicated useful text. The older AdvCiv/UWAI replacements were moved to active empty hint slots (`TXT_KEY_HINT_65` and `TXT_KEY_HINT_68`) so the later existing `TXT_KEY_HINT_16` and `TXT_KEY_HINT_56` entries remain unique.
- `TXT_KEY_HINT_61`: the two English fighter-aircraft hints were very close. The later block has the refined "take damage" wording, and `CIV4GameText_advc_hints.xml` intentionally supports English only, so there were no non-English translations to preserve in that file. The older duplicate was removed.

After these changes, `python .github/workflows/build/xml_text_duplicate_tags.py` passed.

Note: for the hint ones it's only in AdvCiv-SAS that we don't want them duplicated, but it seems some still had issues to some extent although i didn't check in detail because super tedious xd but seemed as such from quick look (more precisely iirc fighter thing was almost similar but not entirely so quite weird but minor maybe idk for sure would need to check to be sure).

## 150 - (Fixed) Base AdvCiv issue (and some AdvCiv-SAS): Priority duplicate XML child/list entries found by new GitHub workflow check

After the text duplicate check was fixed, [`build/xml_child_duplicates.py`](/.github/workflows/README.md#buildxml_child_duplicatespy) [exposed](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27336768909/job/80762873956) priority duplicate child/list entries. These are not parent XML keys like KI#148; they are repeated child values inside one parent object where duplication is very likely accidental and semantically harmful or useless.

GitHub Actions output:

```text
Run python .github/workflows/build/xml_child_duplicates.py
  
FAIL XML priority child duplicates
Priority duplicate child/list entries are treated as build errors.
Priority findings
  - Assets/XML/Civilizations/CIV4CivilizationInfos.xml: lines 1727, 1742: priority duplicate direct child text under <CivilizationInfo> CIVILIZATION_GREECE: <Cities>/<City> duplicate value TXT_KEY_CITY_NAME_SICYON (2 entries)
  - Assets/XML/Civilizations/CIV4CivilizationInfos.xml: lines 3077, 3084: priority duplicate direct child text under <CivilizationInfo> CIVILIZATION_OTTOMAN: <Cities>/<City> duplicate value TXT_KEY_CITY_NAME_MARMARIS (2 entries)
  - Assets/XML/Technologies/CIV4TechInfos.xml: lines 433, 437: priority duplicate child key under <TechInfo> TECH_MONARCHY: <Flavors>/<Flavor> duplicate <FlavorType> FLAVOR_CULTURE (2 entries)
Report-only findings
  - none
Error: Process completed with exit code 1.
```

Fix notes:

- Removed the later duplicate `TXT_KEY_CITY_NAME_SICYON` from the Greek city list.
- Removed the later duplicate `TXT_KEY_CITY_NAME_MARMARIS` from the Ottoman city list.
- Removed the duplicate `TECH_MONARCHY` `FLAVOR_CULTURE` child (AdvCiv-SAS-specific issue) old existing `FLAVOR_CULTURE` value `9`, keeping the `iFlavor` value `4`.

After these changes, `python .github/workflows/build/xml_child_duplicates.py` passed, and the full local `.github/workflows/build/*.py` check set passed too.

## 151 - (Fixed) Base AdvCiv issue: Suspicious malformed-looking XML angle tags found by new GitHub workflow check

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1u_l6UkCpRFe0oGhf4Z_43FK-fP7pcEuW?usp=sharing).

While adding [`build/xml_suspicious_angle_tags.py`](/.github/workflows/README.md#buildxml_suspicious_angle_tagspy) to the GitHub workflow checks, the [first failing run](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27342682844/job/80783239087) found XML text entries with extra `>` characters near language tags. These are valid enough for a normal XML parser because the extra angle can be interpreted as text, but they are still almost certainly malformed text data and can show an unintended leading or trailing `>` in-game.

GitHub Actions output:

```text
Run python .github/workflows/build/xml_suspicious_angle_tags.py
FAIL XML suspicious angle tags
  - Assets/XML/Text/ActualQuotesText_BtS.xml: line 241: extra closing angle after tag: <French>>Moi, [OUR_NAME], détenteur du plus grand nez de l'histoire humaine, je vous souhaite la bienvenue chez les [OUR_CIV_SHORT:3] !</French>
  - Assets/XML/Text/ActualQuotesText_BtS.xml: line 249: extra closing angle after tag: <French>>Moi, [OUR_NAME], détenteur du plus grand nez de l'histoire humaine, je vous souhaite la bienvenue chez les [OUR_CIV_SHORT:3] !</French>
  - Assets/XML/Text/ActualQuotesText_BtS.xml: line 265: extra closing angle after tag: <French>>Certainement pas ! L'honneur des [OUR_CIV_SHORT:3] exige que cette guerre continue jusqu'à ce que vous soyez réduits en bouillie.</French>
  - Assets/XML/Text/BUG_CIV4GameText.xml: line 30: extra closing angle after tag: <English>Created by The BUG Mod.</English>>
  - Assets/XML/Text/BUG_Main_Interface_Options.xml: line 110: extra closing angle after tag: <German>Textfarbe bei negativem Einkommen, das den Goldvorrat übersteigt.</German>>
  - Assets/XML/Text/CIV4GameText_advc.xml: line 6054: extra closing angle after tag: <French>>Force les membres permanents à vous (!) déclarer la guerre (%d1_ReqNum vote(s) sur %d2_TotNum requis)</French>
  - Assets/XML/Text/CIV4GameText_advc_rf.xml: line 384: extra closing angle after tag: <German>Wir befinden uns im Krieg mit %s1_Civ!</German>>
Error: Process completed with exit code 1.
```

Fix notes:

- Removed the extra leading `>` from the three de Gaulle French diplomacy lines in `ActualQuotesText_BtS.xml`.
- Removed the extra trailing `>` after the BUG "Created by" English text.
- Removed the extra trailing `>` after the BUG main-interface German hover text.
- Removed the extra leading `>` from the force-war vote French text in `CIV4GameText_advc.xml`.
- Removed the extra trailing `>` after the German war-status text in `CIV4GameText_advc_rf.xml`.

After these changes, `python .github/workflows/build/xml_suspicious_angle_tags.py` passed.

## 152 - (Fixed) Suspicious replacement question marks in lengthy Sevopedia XML found by new GitHub workflow check

While adding [`build/xml_suspicious_text_chars.py`](/.github/workflows/README.md#buildxml_suspicious_text_charspy) to the GitHub workflow checks, the [first failing](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27400470104/job/80977135402) run found suspicious `?` characters inside word-like tokens in `AdvCiv-SAS_Sevopedia_Lengthy.xml`. This was an AdvCiv-SAS lengthy text issue, not a base AdvCiv inheritance issue. The check also reported 182 inherited non-English replacement-character findings as ignored by default, so the actionable failure stayed focused on active English/SAS text.

GitHub Actions output:

```text
Run python .github/workflows/build/xml_suspicious_text_chars.py
  
FAIL XML suspicious text chars
  - Assets/XML/Text/AdvCiv-SAS_Sevopedia_Lengthy.xml: line 181: suspicious question mark inside token: ...n his will, King Æthelstan leaves his cniht, Aelfmar, eight hides of land.[PARAGRAPH:1]A r?dcniht, "riding-servant", was a servant on horseback.[PARAGRAPH:1]A narrowing of the gener...
  - Assets/XML/Text/AdvCiv-SAS_Sevopedia_Lengthy.xml: line 206: suspicious question mark inside token: ... effect in numerous battles, such as at the Battle of Damghan (1729), the Battle of Yeghev?rd, and the Battle of Karnal. A large number of zamburaks were also successfully employed ...
  - Assets/XML/Text/AdvCiv-SAS_Sevopedia_Lengthy.xml: line 238: suspicious question mark inside token: ...rded to their officers. Recipients included the Hungarian generals Pal Werner and Ferenc K?szeghy, who received the highest Prussian military order, the "Pour le Mérite"; General Ti...
  - Assets/XML/Text/AdvCiv-SAS_Sevopedia_Lengthy.xml: line 513: suspicious question mark inside token: ...n work on performance arts. The roots of the text extend at least as far back as the Natas?tras, dated to around the mid 1st millennium BCE.[PARAGRAPH:1]The Natasutras are mentioned...
  - Assets/XML/Text/AdvCiv-SAS_Sevopedia_Lengthy.xml: line 1277: suspicious question mark inside token: ...ayo column under the command of Michael Kilroy.[PARAGRAPH:1]In 1919, Polish officer Stanis?aw Maczek created a flying company made of a battle-hardened infantry, using horses for mo...
  - Assets/XML/Text/AdvCiv-SAS_Sevopedia_Lengthy.xml: line 1450: suspicious question mark inside token: ...iturgical studies, chant (zema), and poetry (qene), ultimately leading to the Metsehaf Bet?a specialized institution devoted to advanced textual exegesis.[PARAGRAPH:1]The term Metse...
Ignored 182 known inherited non-English replacement-character finding(s); rerun with --show-ignored to list them.
Error: Process completed with exit code 1.
```

Fix notes:

- `r?dcniht` was changed to plain ASCII `radcniht`.
- `Yeghev?rd` was changed to plain ASCII `Yeghevard`.
- `K?szeghy` was changed to plain ASCII `Koszeghy`.
- `Natas?tras` was changed to plain ASCII `Natasutras`.
- `Stanis?aw` was changed to plain ASCII `Stanislaw`.
- `Metsehaf Bet?a` was changed to `Metsehaf Bet - a`, treating the `?` as lost punctuation rather than a lost letter.

After these changes, `python .github/workflows/build/xml_suspicious_text_chars.py` passed.

## 153 - (Fixed) RFC DOC bug: Sevopedia Hill page did not show improvements valid through underlying terrain, feature, or hill-eligible bonus rules

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/17-N_e5lsVtNOIE3TrRs9OnNyjX_Q-oQG?usp=sharing).

In the Sevopedia Terrain category, the Hill page showed only improvements that directly set `bHillsMakesValid`, such as Mine and Windmill. This was inaccurate in-game. For example, a plains hill Grapes tile can build a Plantation because `BONUS_GRAPES` is hill-eligible and Plantation trades/improves Grapes. Hills can also host terrain-valid Forts because a hill tile still has an underlying real terrain such as Plains, Grassland, Desert, Tundra, or Snow. The same problem was observed in RFC Dawn of Civilization's pedia screenshot and source: its `CvPediaTerrain.py` Hill branch also only accepted improvements with `isHillsMakesValid`, which matches the code we had imported from RFC DoC before adapting it for AdvCiv-SAS.

The DLL already had the correct rule in `CvPlot::canHaveImprovement`: Hill is a plot shape layered over real terrain, not a normal terrain by itself like Plains or Tundra. A hill tile is effectively a combination such as:

```text
plot shape: Hill
underlying terrain: Plains
optional feature: Forest
optional bonus: Grapes
```

The bug was only in Sevopedia's Python reconstruction of those rules. The Hill page now shows improvements that:

- explicitly allow hills through `isHillsMakesValid`;
- become valid through an underlying non-water terrain that can also be hilly, such as Fort on Plains/Grassland/etc.;
- become valid through a feature that can appear on hills, such as Forest/Jungle-related improvements;
- trade/improve a hill-eligible bonus, such as Plantation for hill Grapes.

No DLL change was needed because the game rules were already correct; this was a UI/documentation display fix in `SevoPediaTerrain.py`.

Fixed with the very nice help of GPT-5.5 on Codex thanks.

## 154 - (Fixed) Base AdvCiv issue: Great People could wait too long for Golden Age partners instead of using lower but useful actions

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/14yZ443u8V_YQKvVjI2cwiUVD8aPpmJ10?usp=sharing).

While reviewing BBAI logs for AI strength issues, Great People sometimes showed repeated `chooses 'wait'` lines. The first log format only showed the player, Great Person name/type, value, and dead time, which was not enough to tell whether the unit was productively waiting or stuck. We added a temporary `GP_WAIT` diagnostic with turn, player, unit id, plot, age, normal-speed age, mission state, and candidate values for slow/join/build, discover, Golden Age, trade mission, and Great Work.

Filtered `GP_WAIT` logs showed that short waits were often useful: several Greek Great People waited a few turns and then did sensible actions such as joining/settling, triggering a Golden Age, founding a corporation, building an Academy, or using Great Work. So a blunt "never wait" rule would be wrong.

The bad pattern was narrower: some Great People were held for Golden Age pairing for too long. In the first analyzed log, Persia had:

- a Great Prophet waiting from turn 391 to turn 422, max age 32;
- a Great Engineer waiting from turn 426 to turn 454, max age 29;
- Vasco da Gama (Great Merchant) waiting from turn 410 to turn 422, max age 13.

These waits happened because Golden Age value stayed higher than the lower but usable alternatives, and Golden Age reservation kept raising the wait threshold. "Golden Age partner" here means another Great Person needed to start a Golden Age; later Civ4 Golden Ages can require more than one Great Person.

Fix: added a corresponding SAS define and capped only the Golden Age partner reservation path. This does not force a specific fallback action. Once the cap is reached, the existing sorted Great Person mission logic can pick the best available non-Golden action naturally.

Follow-up log with the cap set to 12 normal-speed turns:

- `GP_WAIT` lines dropped from 153 to 133;
- unique waiting Great People dropped from 20 to 19;
- units waiting past 12 turns dropped from 3 to 0;
- wait lines past 12 turns dropped from 38 to 0;
- `GP_GOLDEN_WAIT_CAP` fired 8 times for 4 unique Great People.

The capped cases were modest and reasonable: a Great Spy joined, a Great Engineer discovered Quantum Mechanics, and Persian Great People stopped being held indefinitely for a Golden Age. This fixed the long-hoarding pattern while preserving useful short waits.

Note: this follow-up comparison also used extra diagnostic logging. Empirically, even diagnostic-only DLL changes can shift autoplay history, so not every broad score/tech/history difference in later screenshots or logs should be attributed to the Great Person wait-cap change itself. The main signal is the log pattern: Great People no longer wait past the configured Golden Age partner cap, while short useful waits remain.

Fixed with the very nice help of GPT-5.5 and ChatGPT-5.5 thanks.

## 155 - (Fixed) Base AdvCiv issue: remote captured-city attack stacks could park for many turns because upgrade waiting overrode a ready offensive target

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/19IkuY_8Xvz3OsWvbnYGg6eHNk0JKYPXl?usp=sharing).

While reviewing AI military behavior, we noticed a risky pattern: after conquering a faraway city, a large share of an AI empire's army could remain parked there instead of continuing the offensive or redeploying. This can leave the core empire under-defended, especially when the captured city is far from the original/core city cluster. Keeping a stack together near an active land front can be correct, so this needed logs before changing behavior.

We added `ATTACK_CITY_PARKING` diagnostics around `AI_attackCityMove` waits/skips for large attack-city groups in owned cities. The log includes the turn, group id, unit count, total military share, wounded/capture-capable counts, current city, captured/foreign-captured status, capital connection, nearby/core-city distances, target city, readiness, target strength, war count, joiners, path turns, mission AI, and area AI.

Initial logs showed that the main parking cause was not "no target". It was mostly the upgrade-wait branch:

- `ATTACK_CITY_PARKING`: 470 lines in one analyzed log.
- `wait_upgrade`: 370 lines.
- `wait_joiners_not_ready`: 62 lines.
- `wait_joiners_ready`: 38 lines.

The clearest case was Celtic Boston:

- captured foreign city;
- seen in earlier diagnostics from T156 to T256, and in the stricter remote-trap diagnostic from T172 to T214;
- no nearby owned city in the first diagnostic pass;
- nearest core same-area city around 18 tiles away;
- group size up to 41 units;
- up to 62% of Celtic military;
- valid targets such as Navajo, Machu Picchu, and Tiwanaku;
- `ready=1`;
- `targetTooStrong=0`;
- repeated `reason=wait_upgrade`.

Additional diagnostic fields confirmed that `connectedCapital` was not the useful distinction: remote captured traps could still have `connectedCapital=1`. The real shape was a foreign-captured city far from the core city cluster. A direct `remoteCapturedTrap` flag was then added to the log. One follow-up parse showed:

- `ATTACK_CITY_PARKING`: 469 lines.
- `wait_upgrade`: 378 lines.
- `remoteCapturedTrap=1`: 42 lines.
- every `remoteCapturedTrap=1` line was `wait_upgrade`;
- every `remoteCapturedTrap=1` line had `ready=1` and `targetTooStrong=0`.

Fix: for a remote foreign-captured city stack that is already ready, has a valid target, and whose target is not too strong, bypass only the upgrade-wait skip and continue into the existing target movement logic. This does not evacuate the army, does not alter joiner/no-target behavior, and does not force an attack. It only prevents the upgrade-wait rule from freezing a ready stack far from core.

After the first fix, logs showed:

- `ATTACK_CITY_REMOTE_UPGRADE_BYPASS`: 3 lines.
- `remoteCapturedTrap=1 + wait_upgrade`: 0 lines.

Boston still produced false negatives once another nearby owned city was also a captured/front city, so the trap test was adjusted from "no nearby owned city" to "far from core". A later test showed:

- `ATTACK_CITY_REMOTE_UPGRADE_BYPASS`: 5 lines.
- `remoteCapturedTrap=1 + wait_upgrade`: 0 lines.
- bypasses occurred in plausible cases such as Celtic Boston, Mongol Antium, and Ethiopian Athens.

Final reviewed bypass examples:

- T170 Celtic Boston -> Machu Picchu: 10 units, 25% of Celtic military, 3 upgrade units.
- T197 Celtic Boston -> Machu Picchu: 18 units, 36% of Celtic military, 4 upgrade units.
- T265 Mongol Antium -> Cumae: 18 units, 33% of Mongol military, 4 upgrade units.
- T311 Mongol Antium -> Ning-hsia: 19 units, 33% of Mongol military, 4 upgrade units.
- T329 Ethiopian Athens -> Corinth: 29 units, 39% of Ethiopian military, 6 upgrade units.

Remaining `remoteCapturedTrap=1` parking lines were joiner/no-target cases such as `wait_joiners_ready` or `wait_joiners_not_ready`; those are a separate future issue, not this upgrade-wait fix. The current fix is intentionally narrow.

Tuning is as of now exposed through the corresponding SAS defines for the core-distance, military-share, and absolute-stack-size gates.

Follow-up diagnostic update: after adding `ATTACK_CITY_REMOTE_PARKING_DETAIL`, three different (save files) fresh autoplay/log samples were reviewed. The upgrade fix kept holding: `remoteCapturedTrap=1 + wait_upgrade` stayed at 0. The bypass also fired broadly, not only in the original Boston-style case; one later sample had 18 remote upgrade bypasses, including very large stacks. Remaining `ATTACK_CITY_REMOTE_PARKING_DETAIL` lines were rare and joiner-related, and looked like short-lived or plausible staging cases rather than a proven evacuation bug. Based on those logs, no joiner-wait bypass, evacuation rule, or broader catch-all parking logger was added as of now.

Fixed with the very nice help of GPT-5.5 and ChatGPT-5.5 thanks.

## 156 - (Fixed) Base AdvCiv issue: ready city-attack stacks could park for future upgrades even when no unit could upgrade now

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1wk9367wjB0UK4zUQhdI7aLddY4CvWZIR?usp=sharing).

After fixing the remote captured-city upgrade-wait trap in [KI#155](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#155---fixed-base-advciv-issue-remote-captured-city-attack-stacks-could-park-for-many-turns-because-upgrade-waiting-overrode-a-ready-offensive-target), BBAI logs still showed a broader related problem: large ready attack stacks could wait many turns because enough units had upgrade potential, even when none of those units could actually upgrade now.

This is inefficient when the stack is already ready and the target is not too strong. Waiting can waste a current military advantage while enemies catch up. Attacking can also spend obsolete units so they no longer need upgrades or future upkeep, capture cities that increase economy and unit support, and punish rivals that expanded thinly before they can recover.

We added `ATTACK_CITY_UPGRADE_WAIT_DETAIL` diagnostics around the generic upgrade-wait branch. The log records stack size, military share, target path turns, upgrade-potential unit count, units that can upgrade now, estimated upgrade cost, available gold, financial state, and whether the new bypass would fire.

One reviewed log showed:

- `ATTACK_CITY_UPGRADE_WAIT_DETAIL`: 155 lines.
- `ATTACK_CITY_PARKING reason=wait_upgrade`: 155 lines.
- `affordableUpgradeUnits` / later `canUpgradeNowUnits`: 0 in 154 / 155 lines.
- `ATTACK_CITY_REMOTE_UPGRADE_BYPASS`: 8 lines.
- `remoteCapturedTrap=1 + wait_upgrade`: 0 lines.

The main suspicious cases were large non-remote stacks waiting for future upgrades despite close targets:

- USA Washington: T147-T181, up to 59 units, up to 69% of total military, target 3-5 turns away.
- Mali Gao: T233-T255, up to 42 units, up to 41% of total military, target mostly 4-9 turns away.
- Mali Vienna: T160-T168, 24 units, up to 46% of total military, gold often already above estimated upgrade cost.
- French Nuremberg: T231-T236, 33 units, up to 40% of total military, target 3-5 turns away.
- English Oxford: T212-T219, 24 units, up to 45% of total military, target 2-4 turns away.

Fix: when a city-attack stack is ready, the target is not too strong, no unit can upgrade now, the stack is important enough, and the target is within the configured path-turn gate, bypass the generic upgrade wait and continue into the existing target movement logic. This does not bypass waits when real upgrades are immediately available, and it does not force an attack against a too-strong target.

Follow-up test with the bypass enabled showed:

- `ATTACK_CITY_UPGRADE_WAIT_DETAIL`: 44 lines.
- `ATTACK_CITY_UPGRADE_WAIT_BYPASS`: 40 lines.
- `ATTACK_CITY_PARKING reason=wait_upgrade`: 4 lines.
- `ATTACK_CITY_REMOTE_UPGRADE_BYPASS`: 6 lines.
- `ATTACK_CITY_REMOTE_PARKING_DETAIL`: 5 lines.
- `remoteCapturedTrap=1 + wait_upgrade`: 0 lines.

The 4 remaining generic upgrade waits all had `canUpgradeNowUnits > 0`, so they were true immediate upgrade opportunities rather than future-upgrade parking. The clearest sanity case was the USA Seattle stack: it waited on T270-T272 while 6 units could upgrade now, then bypassed on T273 once `canUpgradeNowUnits=0`, and later continued from Nottingham with the same group.

The generic `ATTACK_CITY_PARKING reason=wait_upgrade` log was then moved after the bypass decision, so bypassed cases are no longer counted as true parking. Bypassed cases remain visible through `ATTACK_CITY_UPGRADE_WAIT_DETAIL` and `ATTACK_CITY_UPGRADE_WAIT_BYPASS`.

Tuning is as of now exposed through the corresponding SAS defines for enable/disable, minimum stack size, minimum military share, and maximum target path turns.

Fixed with the very nice help of GPT-5.5 and ChatGPT-5.5 thanks.

## 157 - (Fixed/Diagnosed) Base AdvCiv bug: Minor AI Work Boat excess after previous spam fixes: compare need to the counted water areas, let sea workers resolve off-BFC sea bonuses, and confirm many repeated rebuilds were genuine net losses

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1h4L2TK5pqCYLjVj81vFTW8xFKTKkE09z?usp=sharing).

This follows the older Work Boat spam fixes in [KI#23](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#23---fixed-base-advciv-issue-of-major-ai-work-boat-producing--scraping-loop-worker-sea-ai-overproduction) and [KI#23.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#232---seemingly-mostly-fixed-base-advciv-issue-of-major-ai-work-boat-producing--scraping-loop-worker-sea-ai-overproduction), and is related to the broader naval overproduction/scrapping sanity work in [KI#53](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#53---fixed-ai-naval-dementia-naval-overproduction-and-naval-scrapping-mayhem). After those earlier changes, BBAI logs still showed many Work Boat pushes and finishes, especially through `choose worker sea 3`, while some seafood targets appeared repeatedly unimproved.

We added targeted BBAI diagnostics:

- `WORKER_SEA_CHOOSE_DETAIL`: every city-side Work Boat production source, including needed workers, existing relevant workers, queued workers, raw primary/second water-area availability, water danger, and financial trouble.
- `WORKER_SEA_NEEDED_TARGET`: exact sea bonuses counted by `AI_neededSeaWorkers`.
- `WORKER_SEA_MOVE_DETAIL`: what existing `UNITAI_WORKER_SEA` units did, such as improving a bonus, retreating, seeking safety, or skipping.
- `WORKER_SEA_IMPROVEMENT_LOST`: when an owned water bonus lost a connecting sea improvement, so repeated replacement could be separated from production overqueue.

The production-side fix was to compare `AI_neededSeaWorkers()` against the same raw primary + second water areas that `AI_neededSeaWorkers()` counts. The old branch used the strategically relevant `pWaterArea`, which can miss city-reachable targets in another local water area. A global queued-boat guard was tested and rejected because it can suppress valid Work Boats on unrelated seas. The current check uses `AI_totalWaterAreaUnitAIs` on the raw counted areas; that function already includes queued/in-training boats for that water area.

The movement-side fix was to let sea workers resolve owned off-BFC sea bonuses that city production already counted. `AI_neededSeaWorkers()` can count those targets, but `AI_improveBonus()` had a land-worker-style guard that rejected no-working-city/no-route plots. For Work Boats, routing is normally irrelevant because the sea improvement itself connects the bonus, so this mismatch could produce a counted-target / boat-cannot-resolve loop. Sea workers now pass that guard, while later checks still require `AI_canConnectBonus`, `canBuild`, pathing, and target reservation.

A stale-target guard was also added so a sea worker does not spend itself on a bonus that already has a connecting sea improvement. This covers cases where another Work Boat solved the target first.

The reviewed log after these changes showed:

- `WORKER_SEA_CHOOSE_DETAIL`: 262 lines.
- `AI_chooseUnit final worker sea`: 131 lines.
- `choose worker sea 3`: 130 lines.
- `WORKER_SEA_MOVE_DETAIL`: 152 lines.
- `improve bonus`: 125 lines.
- `WORKER_SEA_IMPROVEMENT_LOST`: 55 lines.
- 37 / 55 sea-improvement losses had `visibleEnemy=1`.
- no pre-push case where `needed <= availableRawAreas`; when later choose logs showed that relation, it was because the Work Boat had already been queued.

Repeated suspicious targets were then explained by real loss/replacement. Examples included Roman Fish `(57,6)` lost 5 times, Roman Crab `(54,6)` lost 5 times, Roman Whale `(48,10)` lost 4 times, Roman Crab `(59,12)` lost 4 times, Roman Crab `(60,14)` lost 4 times, French Molluscs `(21,37)` lost 4 times, and Zulu Whale `(13,34)` lost 4 times.

Following this, Work Boat production is reduced (e.g., from 34 Work Boats before the fix to ~27-29 Work Boats for Augusts, remaining seeming to be due to heavy pillaging).

Conclusion: the remaining high Work Boat count is largely genuine replacement after enemy or pirate pillaging/harassment, not the old produce/scrap or overqueue bug. Future work should therefore probably target naval defense or repeated sea-improvement loss response, not add broader Work Boat production suppression.

Fixed/diagnosed with the very nice help of GPT-5.5 and ChatGPT-5.5 thanks.

## 158 - (Fixed) Base AdvCiv issue: ready no-target attack stacks could ignore pathable barbarian cities while only preparing a future war

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1aUU_p1Lv3apbNx34YpAnqy6JZSE7iAUc?usp=sharing).

While reviewing late-game barbarian cities that stayed alive for too long, BBAI logs showed that the broad AI was able to capture barbarian cities eventually, but nearby players could still fail to use ready attack stacks against them for a long time.

The initial symptom was that weak barbarian cities could remain near strong or nearby AI players until around T300-T400. In one comparison, Shaka was close to the barbarian cities for a long time but did not invade them early, and stayed one of the weaker players. After the fix, he invaded them around T140 and became one of the strongest players through much of the middle and late game, almost winning.

The first diagnostics split the problem into two parts:

- `BARB_CITY_SCORE_*` showed the production-side barbarian-city appetite was often skipped by distance or had very small scores. That explained why the AI often would not produce extra city attackers specifically for pop-1 or distant barbarian cities.
- `BARB_CITY_OPPORTUNITY` showed what existing `AI_attackCityMove` stacks could see from their actual movement context.

After adding target values to the opportunity log, most cases where a stack ignored a pathable barbarian city were not clearly wrong: the picked normal target was often higher value. The real bug class was narrower:

- `pickedTarget=-`
- `ready=1`
- `targetTooStrong=0`
- `wars=0`
- `anyWarPlan=1`
- `pathableCandidates>0`

In other words, a stack could be ready, have no active war, have no picked city target, and have a pathable barbarian city nearby, but still skip the barbarian city because the team had a preparation/future war plan. This meant the AI could wait for a future war while cheap nearby barbarian conquest opportunities stayed open.

Fix: in `CvUnitAI::AI_attackCityMove`, when a non-barbarian attack stack is ready, has no picked target, and has no active war, allow a fallback to a pathable barbarian city even if the team has a future war plan. This does not override normal targets and does not fire during active wars. It only fills a no-target idle gap.

We added `SAS_pickPathableBarbCityForAttackStack` so the behavior uses the same best pathable barbarian-city candidate as the diagnostic log. This avoided an earlier mismatch where diagnostics found a pathable barbarian city, but a separate fallback call to `AI_pickTargetCity(..., true)` returned no target. K-Mod/AdvCiv disabled the old BBAI-style `AI_goToTargetBarbCity`, so the selected barbarian city is explicitly passed through `AI_goToTargetCity`.

The stack gate uses actual group capability instead of only `UNITAI_ATTACK_CITY` labels. `SAS_countGroupCityAttackCapability` counts units that can attack and units that can actually capture cities, so broad attacker types such as attack, counter, reserve, or pillage units can help, while pure collateral/no-city-capture units do not make the stack look sufficient by themselves.

Rationale: close/profitable barbarian cities are usually low-risk because they are often weak and have little/no diplomatic or war cost. Capturing them can add population, land, resources, unit support, and future growth. It can also avoid spending a settler and slowing city growth or other projects, while denying the opportunity to nearby rivals.

After the final behavior and logging cleanup, the reviewed log showed:

- `BARB_CITY_NO_TARGET_FALLBACK_TRY`: 487
- `BARB_CITY_NO_TARGET_FALLBACK_FAIL`: 478
- `BARB_CITY_NO_TARGET_FALLBACK_SUCCESS`: 9
- `BARB_CITY_NO_TARGET_FALLBACK_SKIP`: 33, all `active_war`

The fail count was not concerning because all failures had `fallbackPickedTarget=-` and `fallbackPickedPathTurns=-1`, meaning no pathable barbarian city existed within the fallback limit. The important signal was that the previously suspicious pattern was gone: there were 0 remaining cases of `pickedTarget=-`, `ready=1`, `wars=0`, and `pathableCandidates>0`.

Behaviorally, the same broad situation improved from barbarian cities surviving around T300-T400 to early cleanup:

- T121: France captures Alemanni.
- T124: Barbarians recapture Alemanni.
- T127: Zulu captures Hurrian.
- T132: Zulu captures Alemanni.
- T148: Zulu captures Visigoth.
- T153: Zulu captures Gaul and razes it.

The France recapture case is a separate possible post-capture garrison/retreat issue, not part of this fallback.

Fixed with the very nice help of GPT-5.5 and ChatGPT-5.5 thanks.

## 159 - (Improved) AI civic-switch damping: paid-anarchy civic churn and direct reversals after the civic timer expired

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1tczEbJf6nrD8I0zE4qpVf5BQEpXRVDYH?usp=sharing).

This is framed as a civic-tuning follow-up rather than as a base AdvCiv bug or an AdvCiv-SAS-specific bug. The behavior was observed in our current AdvCiv-SAS tuning state, but the root cause could be base behavior, our broader civic valuation changes, our anti-oscillation changes, or an interaction between them. BBAI diagnostics showed many civic changes were free/no-anarchy switches, but the expensive part was paid-anarchy churn, especially direct reversals soon after the normal civic timer expired.

The diagnostic pass added structured logs:

- `CIVIC_SWITCH_DETAIL`: accepted and rejected civic candidates, including old/new civic, values, delta, slack, anarchy length, anarchy delta, war/financial context, and pass flags.
- `CIVIC_REVOLUTION_DETAIL`: final revolution bundles, timer values, and whether the bundle paid anarchy.
- `CIVIC_REVOLUTION_CHANGE`: each civic option changed by the final bundle.

The first reviewed run showed:

- 242 civic revolution bundles.
- 574 civic changes.
- 52 paid-anarchy revolutions.
- 174 total anarchy turns.
- 15 single-civic paid revolutions.
- 388 direct reversals total, including 376 within 30 turns.
- 66 direct reversals where at least one side paid anarchy, and 49 where both sides paid anarchy.

Fix part 1: when a civic candidate increases the current revolution bundle's anarchy length, require a larger absolute value gain before accepting it. Free/no-extra-anarchy bundle changes remain responsive, but the AI should not freeze the empire for tiny volatile gains.

Fix part 2: after paid-anarchy revolutions, extend the civic timer by an amount based on the paid anarchy length. This addresses the pattern where the AI paid anarchy, waited until the old timer expired, and then flipped back soon after.

The final reviewed run improved strongly:

- Civic revolution bundles: 242 -> 180.
- Civic changes: 574 -> 424.
- Paid-anarchy revolutions: 52 -> 23.
- Total anarchy turns: 174 -> 81.
- Single-civic paid revolutions: 15 -> 5.
- Direct reversals total: 388 -> 250.
- Direct reversals within 30 turns: 376 -> 221.
- Direct reversals with at least one paid side: 66 -> 27.
- Direct reversals where both sides paid anarchy: 49 -> 17.

This should make AI turns more efficient because excessive anarchy downtime is costly, especially with the current AdvCiv-SAS anarchy duration of 2 turns. If the damping is too sticky, reduce the corresponding timer/slack values; if oscillation returns, increase them. Keep the diagnostics useful for future tuning because civic valuation is sensitive to other AI changes.

Fixed/improved with the very nice help of GPT-5.5 and ChatGPT-5.5 thanks.

## 160 - (Fixed) Likely inherited AI upgrade-budget issue: normal upgrades could overshoot the remaining budget and leave the AI almost broke

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1p033n4oF_v-btMYwng7iJzowNaXtu2sC?usp=sharing).

This looks likely inherited from base/K-Mod/AdvCiv-style upgrade flow because the old logic in `CvPlayerAI::AI_doTurnUnitsPost` already used a 4-pass upgrade loop and checked only whether spending so far was below the upgrade budget before attempting the next upgrade.

The initial aggregate BBAI log showed suspicious upgrade spending:

- 305 upgrade-spend events.
- 23 events overspent the listed upgrade budget.
- 49 events left the AI with <= 10 gold.
- 110 events left the AI with <= 25 gold.
- 183 events left the AI with <= 50 gold.
- 17 events both overspent the budget and left <= 50 gold.
- No-active-war upgrades were especially suspicious: 151 events, 20 budget overspends, 62 ending with <= 25 gold, and 29 ending with <= 10 gold.

The old aggregate line did not show which pass or unit caused the spending, so diagnostics were added:

- `UPGRADE_BUDGET_DETAIL`: starting gold, gold targets, upgrade budget, total upgrade need, focus-war, war-plan, financial-trouble, city/unit count, and era.
- `UPGRADE_SPEND_DETAIL`: one line per paid upgrade, including pass name, unit id/type/AI/domain, plot/city, best-defender and danger flags, cost, gold before/after, budget, and context.
- `UPGRADE_PASS_SUMMARY`: per-pass eligible units, paid upgrades, rough budget skips, and pass spending.
- `UPGRADE_BUDGET_RESULT`: final spending result paired with the old aggregate line.

The diagnostic run showed the main problem was not emergency defense upgrades:

- Pass 0 `impassable`: 18 upgrades, 2777 gold, 1 overspent-after upgrade.
- Pass 1 `city_defender_or_danger`: 168 upgrades, 16107 gold, 2 overspent-after upgrades.
- Pass 2 `transport_or_escort_sea`: 1 upgrade, 197 gold, 0 overspent-after upgrades.
- Pass 3 `normal`: 787 upgrades, 82937 gold, 37 overspent-after upgrades.

The specific bug-like pattern was that pass 3 only checked `spent so far < budget`. If spending was still below budget before an upgrade, the AI could start another expensive normal upgrade even when that upgrade could not fit inside the remaining budget. Example from the reviewed log: England on T342 had 499 gold and a 279 budget, upgraded twice for 237 each, spent 474 total, and ended at 25 gold.

Financial-trouble cases confirmed the same pattern. Example: England on T346 had `financialTrouble=1`, spent 237 with budget 59, and went from 246 gold to 9 gold on a pass 3 normal upgrade.

Fix:

- Keep pass 0/1 emergency-ish upgrades uncapped.
- For pass 2/3, pass a maximum allowed upgrade price into `CvUnitAI::AI_upgrade`, equal to the remaining upgrade budget.
- `CvUnitAI::AI_upgrade` now ignores upgrade candidates whose `upgradePrice` exceeds that max price, while otherwise preserving the old candidate iteration and value logic for affordable upgrades.
- Skip pass 3 normal upgrades entirely if the AI started in financial trouble and is not focus-war.

Follow-up BBAI comparison showed the intended result:

- Upgrade-spend turns: 362 -> 355.
- Individual paid upgrades: 974 -> 915.
- Total upgrade gold spent: 102018 -> 84095.
- Overspent budget turns: 40 -> 1.
- Pass 3 overspent upgrades: 37 -> 0.
- Financial-trouble spends: 33 -> 4.
- Financial-trouble overspend: 7 -> 0.

The single remaining overspend was pass 0 impassable: Mali on T176 spent 408 against a 365 budget and still kept 165 gold. Since pass 0 is intentionally uncapped and this did not match the old pass 3 low-gold pattern, it was accepted.

Low final gold can still happen in focus-war / any-war-plan contexts. That is a separate possible follow-up about preserving a cash reserve during war preparation, not the same bug as pass 3 normal upgrades overshooting their remaining budget.

Fixed with the very nice help of GPT-5.5 and ChatGPT-5.5 thanks.

## 161 - (Tentatively Addressed and Hardened) Rare non-reproducible autoplay crashes related to `CvCity::cheat+0x15c3` sharing the city-name text lookup crash signature

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1CcRoDInd1w6DzgF9e0yDVnnEPvOpnX31?usp=sharing).

After fixing the much more frequent `CvSelectionGroup::plot` crash and several other earlier crash sources, long autoplay runs are now usually much more stable. In recent testing, most turn 0 to around turn 400/500 autoplay runs finished in one go, but two rare non-reproducible crashes still appeared around turn 145 and turn 348.

The two crash logs looked related enough to treat as one crash pattern rather than two unrelated issues:

- Both were access violations while reading memory (`c0000005`).
- Both failed inside `CvGameCoreDLL.dll` at almost the same relative offset.
- Both were reported by WinDbg as `CvCity::cheat+0x15c3`, but this is probably only the nearest available symbol name because the dump did not have proper line symbols / PDB information. It should not be trusted as proof that real `CvCity::cheat` logic was involved.
- Both showed the same failure bucket/hash, which strongly suggests the same crash signature.
- Both had heap allocation / string-looking stack context.
- The raw stack data looked like city text keys, for example `TXT_KEY_CITY_NAME_MASTER_ADAM` in one crash and `TXT_KEY_CITY_NAME_PARIS` in the other. Since `PARIS` is an ordinary city-name key, the evidence points less toward a single malformed XML text key and more toward a fragile city-name/text lookup path or an earlier memory problem surfacing during that path.

This was not reproducible from the save, so the exact root cause is not proven. The safest interpretation is that the crash was probably happening near city-name selection, city-name text lookup, city founding/naming, or heap/string allocation connected to those systems. It could also still be earlier unrelated memory corruption that merely became visible when a city-name string was allocated or translated.

Conservative hardening was added around the city-name path:

- `CvPlayer::getNewCityName` now skips empty explicit city-name queue entries before calling `gDLL->getText`.
- `CvPlayer::getCivilizationCityName` now guards invalid civilization ids, civilizations with zero city-name entries, and empty city-name keys before random selection or `gDLL->getText`.
- `CvCity::setName` now rejects null or empty city-name pointers before constructing a `CvWString`.

These changes should not alter normal city-name behavior. They only prevent unsafe lookups or string construction when data is invalid, unexpectedly empty, or memory state is already abnormal. Because the crash was rare and not reproducible, this should be treated as a hardening / likely mitigation rather than a fully proven fix.

Addressed with the very nice help of ChatGPT-5.5 + GPT-5.5 for quick review of the solution thanks.

## 161.2 - (Tentatively Addressed and Hardened) Rare non-reproducible autoplay city-name crash related to `CvCity::cheat+0x15c3` around city acquisition (Aachen city ownership transfer from Holy Rome to Mali) and uncovered during BBAI culture logging investigation

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/15DRUXwdJT_uyHXlLhs8QMsdCE0aR9Kqc?usp=sharing).

After KI#161 had already hardened the city-name lookup path, one more non-reproducible autoplay crash appeared around turn 157/158 with the same general signature family. The dump again showed an access violation in `CvGameCoreDLL.dll` at `CvGameCoreDLL+0x510e3`, with WinDbg reporting the nearest exported symbol as `CvCity::cheat+0x15c3`. As in KI#161, that symbol name should not be treated as proof that real `CvCity::cheat` logic was involved, because no matching line-symbol PDB was available.

The useful new clue was the BBAI culture log. The logging probably did not cause the crash. Most turn 0 to turn 500 autoplay runs survived with the same logging enabled, so a direct logging bug would likely have failed more often. However, the high-detail culture log accidentally bracketed the crash very well. The crash-side log stopped after `CULTURE_STAGE_RESULT turn=158 player=1 Mali ... cities=6`. A successful run continued past the same point and then logged Mali with 7 cities, including Aachen. Around the same turn, Aachen appears to have changed from Holy Rome to Mali in the successful comparison run.

This made the city acquisition / city-name preservation path the most plausible nearby trigger, although the exact crash moment is still not proven. During city acquisition, the game appears to create or initialize a city object, assign a temporary/generated city name, and then preserve or restore the old city name. That path can touch translated city-name lookup and past-city-name tracking at a delicate moment. The old code could also let `CvCity::setName(..., bInitial=true)` run the translated duplicate-name validation scan and record the temporary placeholder name as a past city name when the acquired city name immediately replaced it.

Conservative hardening was added around this specific path:

- `CvCity::setName` now treats initial/internal city-name assignment as already validated by the caller. It skips the translated duplicate-name scan when `bInitial` is true.
- `CvCity::setName` no longer records the temporary placeholder name assigned during city initialization as a past city name when the initial/internal naming path immediately replaces it.
- `BBAILog.cpp` now explicitly null-terminates the fixed log buffer after `_vsnprintf`, because old MSVC `_vsnprintf` can fail to null-terminate on truncation. This is general logging hardening, not proof that BBAI logging caused the crash.

This should not change normal city-name behavior. Manual renames and ordinary duplicate-name checks still use the regular validation path. The change only avoids extra translated city-name lookup and past-name bookkeeping during initial/internal naming, especially city transfer/acquisition. Because the crash was rare and not reproducible, this should be treated as a hardening / likely mitigation rather than a fully proven fix.

The BBAI logging coincidence was still useful enough to document: it turned a vague city-name crash signature into a much more specific suspected acquisition/name-transfer transition.

Tentatively addressed with the very nice help of ChatGPT-5.5 thanks.

## 162 - (Tentatively Addressed and Hardened) Rare non-reproducible autoplay crash variant in `CvCity::getProductionBarPercentages`

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1sf0TZF1uSYlPds8bFjtoYwv7cA6hQ06u?usp=sharing).

After KI#102 and KI#103 had already addressed two earlier `CvCity::getProductionBarPercentages` crash variants, another rare non-reproducible autoplay crash appeared around turn 243.

The crash log again points to `CvCity::getProductionBarPercentages`, this time at `+0x502`, with an access violation while reading memory address `000001b8`. The stack is not fully reliable without matching line symbols / PDB information, but it still places the crash in the city production-bar path and near broader UI / selection / turn-transition context. This looks related to the old production-bar crash family, but different enough from KI#102 and KI#103 to document as a separate later variant rather than silently extending those older entries.

The suspected weakness is that `CvCity::canBeSelected` could return true through early city-visibility paths such as `m_bInvestigate`, `isActiveTeam`, or debug mode before checking whether `GC.getGame().getActivePlayer()` was valid. During autoplay or turn transitions, the EXE can sometimes still ask for city UI bars while no active player exists. Letting those early paths bypass the `NO_PLAYER` guard could allow `CvCity::getProductionBarPercentages` to run in an unsafe UI state.

Conservative hardening was added:

- `CvCity::canBeSelected` now checks `NO_PLAYER` before any early selectable-city return.
- `CvCity::getProductionBarPercentages` now reuses one validated `getProductionNeeded` value before doing production-bar math.
- The production-bar path now rejects invalid production-needed values such as `<= 0` or `MAX_INT`.

This should not alter normal production or city UI behavior. It only prevents city production-bar display math when the active-player/UI state or production denominator is abnormal. Because the crash was rare and not reproducible, this should be treated as a hardening / likely mitigation rather than a fully proven fix.

Tentatively addressed with the very nice help of ChatGPT-5.5 + GPT-5.5 for quick review of the solution thanks.

## 163 - (Tentatively Addressed and Hardened) Rare non-reproducible autoplay crash variant related to `CvSelectionGroup::deleteUnitNode` and `CvSelectionGroup::clearUnits`

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1_3YWkViHtODB341EGe5UbfIwwTGrFtKe?usp=sharing).

After KI#161 and KI#162, autoplay stability looked much better again, with the current test already reaching around turn 330. One remaining recent crash from turn 318 did not match the city-name text lookup crash pattern from KI#161 and did not match the production-bar path from KI#162. Instead, the dump pointed into the `CvSelectionGroup` unit-list teardown family.

The crash log showed an access violation while reading memory address `00000520`. WinDbg reported the nearest symbol as `CyPlot::CyPlot+0x186d0`, but the stack immediately below it went through `CvSelectionGroup::deleteUnitNode`, `CvSelectionGroup::clearUnits`, `CvUnit::getGroup`, and `CvSelectionGroup::getHeadUnit`. Without matching PDB / map-file symbols this is not a precise source line, but it strongly suggests a stale group/unit/plot lifetime edge case while a selection group is being emptied.

This looks closer to the old `CvSelectionGroup::plot` crash family than to KI#161 or KI#162. That older crash family had already been improved through several iterations, fixing the most common variants, but this dump may represent a rarer remaining variant around group teardown rather than ordinary movement or plot lookup.

The suspicious code pattern was that `CvSelectionGroup::clearUnits` emptied the whole group by repeatedly calling `deleteUnitNode`. However, `deleteUnitNode` is the normal single-unit removal path: before deleting a node, it cancels automation through `setAutomateType`, clears the mission queue through `clearMissionQueue`, and may wake the group through `setActivityType`. Those helpers can inspect the head unit, group plot, cargo groups, UI selection state, activity state, and mission callbacks such as `deactivateHeadMission`. Doing that repeatedly while `clearUnits` is actively tearing down the whole unit list is unnecessarily re-entrant and fragile.

The defensive change is therefore deliberately narrow:

- `CvSelectionGroup::clearUnits` now performs direct full-teardown cleanup: reset automation, clear the mission queue, clear the mission timer, reset activity to awake, and clear the unit list once.
- `clearUnits` intentionally bypasses `deleteUnitNode`, `setAutomateType`, `clearMissionQueue`, and `setActivityType` during full group teardown, because those helper callbacks are designed for normal single-unit removal and can inspect group state while the list is being destroyed.
- `CvSelectionGroup::deleteUnitNode` keeps its existing normal single-unit removal behavior but now tolerates an unexpected null node.

This should preserve normal behavior for ordinary unit removal while avoiding repeated mission/activity/plot/UI side effects during full group clearing. It is still only a tentative hardening because the crash was rare and non-reproducible, and the exact source line is not known without matching symbols.

Tentatively addressed with the very nice help of ChatGPT-5.5 and GPT-5.5 thanks.

## 164 - (Fixed) Base Civ4 Oasis map script had shadowed Python callbacks (found by the Python Ruff GitHub Actions Workflow)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1XlRugVrvBfdTAW7HPw5nuOW4pTf3daCh?usp=sharing).

The new [GitHub Actions Python Ruff workflow](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27878643336/job/82502279369) (`python-ruff.yml`) flagged two `F811` duplicate-definition findings in `PrivateMaps/Oasis.py`: `normalizeAddExtras` and `addBonusType` were each defined near the top of the file and then defined again later.

```log
Error: PrivateMaps/Oasis.py:173:5: F811 Redefinition of unused `normalizeAddExtras` from line 102: `normalizeAddExtras` redefined here
  PrivateMaps/Oasis.py:102:5: previous definition of `normalizeAddExtras` here
  help: Remove definition: `normalizeAddExtras`
Error: PrivateMaps/Oasis.py:636:5: F811 Redefinition of unused `addBonusType` from line 107: `addBonusType` redefined here
  PrivateMaps/Oasis.py:107:5: previous definition of `addBonusType` here
  help: Remove definition: `addBonusType`
Error: Process completed with exit code 1.
```

This was useful because Python keeps only the later function definition. The early balanced-resource callbacks therefore were not active at runtime; they were shadowed by the later Oasis-specific callbacks.

For this first Ruff cleanup, the fix deliberately preserved current gameplay/map-generation behavior instead of merging the old balanced-resource callback logic into the active Oasis callbacks. The shadowed early callback block was commented out and documented in-place. That removes the duplicate Python definitions and keeps the currently active Oasis behavior exactly as before.

Found thanks to the GitHub Actions Python Ruff workflow and fixed with the help of GPT-5.5 (on Codex) thanks.

## 165 - (Fixed) Base AdvCiv bug: Dormant RectLayout `upperLeft` helper returned undefined `Point` instead of `PointLayout` (found by Python Ruff GitHub Actions Workflow)

Screenshots/files for this issue: [google drive folder link](https://drive.google.com/drive/folders/1CQjC926rZvmWJGwYBzOlXUAFOnqlpa8w?usp=sharing).

Python Ruff flagged `F821 Undefined name Point` in `Assets/Python/Screens/RectLayout.py`, where `RectLayout.upperLeft()` returned `Point(self.fX, self.fY)`.

```log
Error: Assets/Python/Screens/RectLayout.py:138:10: F821 Undefined name `Point`
```

The game ran fine because Python resolves names inside a function only when that function is executed, and repository search found no active caller of `upperLeft()`. This made the issue dormant rather than visible in ordinary UI use. The nearby `__str__` returning text like `"Point(...)"` is different: that is only a display string, not a Python name lookup.

The fix changed `upperLeft()` to return the local `PointLayout` class, matching `RectLayout.offsetPoint()` and the rest of the active layout code.

Found thanks to Python Ruff and fixed with the help of GPT-5.5 (on Codex) and ChatGPT-5.5 (who also helped implement/draft this workflow) thanks (Although tbh another LLM or maybe it was GPT-5.5 too had mentioned it but i had overlooked/omitted it or forgot to look into it; now fixed it seems).

## 166 - (Fixed/Addressed) Base AdvCiv issue of trying to support reading mod (e.g., AdvCiv/AdvCiv-SAS) replay/Hall of Fame data in unmodded BTS, or unmodded BTS replay/Hall of Fame data in the mod (e.g., AdvCiv/AdvCiv-SAS): replays no longer try to use vanilla BtS-compatible replay storage after shifted XML enum order

This is about the end-game replay/history data, not normal saves, map generation, or gameplay. The replay is the post-game history/map playback data and related replay/Hall-of-Fame-style record data. AdvCiv had an optional path that tried to store some replays in a vanilla BtS-compatible format when the data looked safe enough.

That compatibility path is not useful for AdvCiv-SAS and became misleading after several intentional XML order changes.

Not only AdvCiv-SAS now has shifted raw ids for values that replay data can store directly, but also, we do not need nor support reading AdvCiv-SAS replay/Hall of Fame data from unmodded BTS, nor do we need or support reading unmodded BTS replay/Hall of Fame data into AdvCiv-SAS.

For example:

- Game speeds: Nitro and Turbo are before Quick.
- World sizes: Arena is before Duel, and SAS24/SAS32/SAS40/SAS48 are after Huge.
- Handicaps: Rookie is before Settler, and Deity+ is after Deity.

These values are valid inside AdvCiv-SAS, but vanilla BtS would interpret the same raw integer ids differently. For example, vanilla BtS expects world size id `0` to mean Duel and id `5` to mean Huge, while AdvCiv-SAS now uses id `0` for Arena and id `6` for Huge. Similar shifted-id issues also exist for game speed and handicap.

Rather than adding a full remapping layer for a compatibility mode that is not needed, `CvReplayInfo::isStoringReplaysAsBtS()` now always returns `false` in AdvCiv-SAS. This means:

- AdvCiv-SAS still writes normal AdvCiv-SAS replays.
- The replay stores the mod name / mod replay format instead of pretending to be vanilla BtS-compatible.
- There is no effect on normal saves or gameplay.
- Opening AdvCiv-SAS replay/save data in vanilla BtS, or vanilla BtS data in AdvCiv-SAS, is not a supported goal.

Fixed/documented with the help of ChatGPT-5.5 after a Codex review pointed out that the old `getWorldSize() > 5` BtS replay guard had become stale once `WORLDSIZE_HUGE` moved to XML index `6`.

# SASGameRecord Revision History

> Historical reconstruction from the AdvCiv-SAS commit-diff corpus, reconciled through practical version 6439 (`03b44b8932a0715be234e8c5332fcb8a1d1cf3b2`).

## Revision policy

`SASGameRecord` uses one monotonically increasing **revision** number as a downstream-update signal, not as a compatibility promise. The purpose is simple: an external mod/parser/tool that supports revision N and encounters N+1 knows that the official SASGameRecord implementation changed and should review/update its copy.

- Increment the revision for every intentional SASGameRecord-related code change that a downstream copy may want to review: emitted data/semantics, row/field names, recording conditions, recorder bug fixes, relevant bridges/call sites/configuration/checkers, implementation/refactors/optimizations, and code comments or provenance headers in those implementation files. The goal is deliberately simple: if the official SASGameRecord-related code changed, a copied implementation can notice that there is something new to review.
- Do **not** spend time deciding whether a change is backward-compatible or behavior-changing. When in doubt, increment.
- Do not increment for standalone documentation/history edits, refreshed example logs/screenshots/packages, or unrelated gameplay commits that merely used SASGameRecord as validation evidence.
- Multiple SASGameRecord changes deliberately combined in one Git commit are one revision; this is an update counter, not a hunk/field counter.
- The official revision sequence belongs to SASGameRecord. A downstream mod should report the highest official revision it has implemented and should not invent official revision numbers for private extensions.

## Current reconstructed number and first explicit marker

The original reconstruction counted **67 implementation-changing commits** from the feature introduction at SAS practical 6022 through practical 6438.

Under the stricter maintenance rule above, practical 6439 also counts because it intentionally changed the provenance/header comments in the dedicated `sas_game_record_log.py` checker. Practical 6440 then introduced the explicit revision mechanism itself and therefore counts as the next implementation change.

Therefore:

- **Historical state at practical 6438 / Git `6673cf44...`: revision 67.**
- **Historical state at practical 6439: revision 68.**
- **The commit that introduces the explicit revision field/history/check should be revision 69**, because the mechanism itself changes SASGameRecord-related code.

Current emitted source-context field:

```text
GAME_RECORD_SOURCE_CONTEXT recordRevision=90 ...
```

After this, each qualifying SASGameRecord update increments `SAS_GAME_RECORD_REVISION` by one and adds one short latest-first entry to this file in the same commit. The revision is only a downstream-update signal; exact runtime source identity remains in `GAME_RECORD_SOURCE_CONTEXT`.

## Reconstruction method

The history below counts commits that changed the recorder implementation itself (`SASGameSummaryLog.*` / `SASGameRecordLog.*`) or changed runtime/configuration call sites directly participating in the structured record. It intentionally excludes broad text-search hits that only mentioned the record in documentation/comments, used it as test evidence, refreshed example logs, or changed packaging/tooling without changing the recorder implementation. This is why the original reconstruction produced 67 revisions through practical 6438 rather than the much noisier ~166 broad-history-hit figure. The stricter current policy additionally counts later intentional code-comment/header-only updates in SASGameRecord-related implementation/checker files.

Because this numbering is reconstructed after the fact, the descriptions are concise summaries of the canonical commit diffs/messages rather than claims that these revision numbers were emitted by historical builds.

## History (latest first)

### Revision 91 - SAS practical 6481

- **Date:** 2026-09-18
- **Git commit:** pending
- **Change:** Added complete readable AI-strategy history at level 2. `GAME_RECORD_AI_STRATEGY_CHANGE` records each final gameplay-active non-default `AIStrategy` bit that starts/stops after `AI_updateStrategyHash` finishes its validity cleanup, while periodic `GAME_RECORD_AI_STRATEGIES` checkpoints preserve the complete active set without requiring replay from turn 0. Existing specialized decision rows remain for local context and BBAI retains its detailed K-Mod transition diagnostics/trigger values.

A shared `getSASAIStrategyType` helper in `CvGameCoreUtils` now provides canonical raw enum names to both logs, replacing the fragile BBAI stringification macros without changing their emitted strategy names. Existing SASGameRecord strategy predicates share one AI-Auto-Play-aware wrapper, and the build check guards the contiguous strategy-bit layout, enum-name coverage, and all complete strategy scans against future `AIStrategy` additions. No AI strategy evaluation, RNG or pathfinding is repeated solely for recording.

### Revision 90 - SAS practical 6480

- **Date:** 2026-09-17
- **Git commit:** `e25c3e02b18e1252d873e5b5eb978edf40225d37`
- **Change:** Source-readability maintenance only. Oversized `logSASGameRecord(...)` argument lists are wrapped at top-level argument boundaries while their format strings remain unchanged. A conservative helper now preserves this argument-layout convention alongside the matching BBAI cleanup while deliberately leaving existing prose-comment layout untouched. Emitted SASGameRecord row text, fields, conditions, and gameplay behavior are unchanged.

### Revision 89 - SAS practical 6477

- **Date:** 2026-09-17
- **Git commit:** `18e8765652b15b1726e3c97724f2a150656ef6ad`
- **Change:** Tightened disabled-recorder overhead after the expanded provenance work. `SAS_GAME_RECORD_LOG_LEVEL` is now cached once after all GlobalDefines/module overrides load, making the widespread level gates direct integer reads instead of out-of-line getter calls in ordinary non-LTCG Release builds.

Caller-gated plot/random-event placeholder states no longer initialize unused fields at level 0/1, the plot-owner cause scope avoids an unused disabled-path member write, and unit-event before/after snapshots now live wholly inside the enabled branch. Tiny empty vectors that must span gameplay mutation remain intentionally accepted and locally documented; they perform no recorder scan/allocation/population while logging is disabled. Emitted record semantics are unchanged.

### Revision 88 - SAS practical 6476

- **Date:** 2026-09-17
- **Git commit:** `d8a8df2f2dc046fa57ba8d4679e7d98cf130ab33`
- **Change:** Added compact AI civic/revolution provenance. `GAME_RECORD_AI_CIVIC_DECISION` records live `AI_doCivics` switch candidates from the already-computed current/best civic values, percent threshold, absolute/anarchy slack, bundle-anarchy state and first/recheck pass; accepted candidates are level 2 while rejected/wanted-but-rejected candidates are level 3. `GAME_RECORD_AI_CIVIC_OUTCOME` records meaningful accepted-bundle outcomes: actual revolution, delaying for an imminent researched civic, insufficient-gold blocking, or an unexpected final `canRevolution` block, including the pending/final civic bundle and real timer/anarchy/research/gold context; `BLOCKED_GOLD` also records the net deal gold-per-turn actually used by its reserve formula. No civic valuation or revolution eligibility search is repeated solely for recording.

The same call-site review also gates older BBAI-only financial-trouble/war-state diagnostic lookups so ordinary player-log-disabled gameplay no longer performs that diagnostic work.

### Revision 87 - SAS practical 6475

- **Date:** 2026-09-17
- **Git commit:** `727e094fdc31b3e785825433407b47bacdeccaf8`
- **Change:** Added compact AI resource-trade choice provenance. `GAME_RECORD_AI_BONUS_TRADE_DECISION` records the real proactive `AI_proposeResourceTrade` receive/give chooser winners and runner-ups from already-computed buyer trade value, seller keep-value estimate, bias, probability gate and random final score, then joins them to the actual counterproposal terms that are about to be shown to a human or implemented between AIs. Winner-only factual resource/strategic context is gathered only when an event is emitted; the shared `AI_bonusTradeVal` function itself remains uninstrumented.

`GAME_RECORD_AI_BONUS_DEMAND_DECISION` separately records the different tribute chooser's randomized sorted winner/runner-up, non-surplus sorting adjustment, selected resource bundle/value, minimum threshold and final deal valuation. Existing periodic `GAME_RECORD_TRADE_MARKET` remains the resolved availability/denial/price view. The new rows repeat no bonus valuation, counterproposal search or RNG solely for recording.

### Revision 86 - SAS practical 6474

- **Date:** 2026-09-17
- **Git commit:** `318c4c070c954a548fd44ae819b59819981d3e1f`
- **Change:** Added compact AI research/free-technology choice provenance. `GAME_RECORD_AI_RESEARCH_DECISION` identifies teammate coordination, Python overrides and the real `AI_bestTech` fallback; the latter preserves the chosen/requested technology, actual current research after queueing, deeper strategic aim, chooser/path values, distinct runner-up and chooser breadth from values already computed by gameplay. Level 3 additionally serializes each distinct returned-tech candidate with its chooser/path value and deeper aim, while free-tech choices use the same depth-1 machinery. No technology valuation or chooser RNG is repeated for recording.

The technology-path diagnostic also recovers the actual deepest endpoint after K-Mod backfills/reorders paths with unrelated depth-0 technologies, rather than assuming `path.front()` is always the long-term aim; AdvCiv's rare scenario fallback likewise reports the path actually selected rather than always path 0. These are diagnostic/provenance corrections only and do not change research selection.

### Revision 85 - SAS practical 6473

- **Date:** 2026-09-17
- **Git commit:** `f94667171d4523a595a9153e253ad68c5486680b`
- **Change:** Added compact AI espionage mission-choice and mission-phase interception provenance. `GAME_RECORD_AI_ESPIONAGE_DECISION` retains the scored chooser winner/runner-up and both candidates' already-computed valuation/randomization/overhead/cost components plus chooser risk/EP/strategy context without rerunning valuation or RNG; the separate K-Mod tactical city-revolt path emits `GAME_RECORD_AI_ESPIONAGE_TACTICAL_DECISION` with its factual remaining-defense gate instead of fabricated scores.

`GAME_RECORD_SPY_INTERCEPTION_CHECK` records every real before/after-mission base/final chance and authoritative result/draw plus counterespionage, counter-Spy-defense/Spy, city-defense and recent-mission context; successful non-interceptions are therefore visible alongside existing completed-mission and caught-Spy outcomes. The ordinary logging-disabled/travel-interception path keeps the original `SyncRandSuccess10000` behavior, and logging-only plot/unit scans remain level-2 gated.

### Revision 84 - SAS practical 6472

- **Date:** 2026-09-17
- **Git commit:** `b93cfcd8ae7a6279729c067373532f66d884ea8d`
- **Change:** Added compact AI corporation operational provenance. `GAME_RECORD_AI_CORPORATION_DECISION` records actual Executive production commits, new/retargeted `AI_spreadCorporation` destinations and deliberate Executive airlift/sea-transport routing with only already-computed chooser scores/path context; no corporation valuation or pathfinding is repeated for logging. Periodic `GAME_RECORD_CORPORATION_POSTURE` separates policy-enabled corporations from actually present corporation types/city instances/headquarters and preserves persistent Executive spread missions, including Executive cargo carried by sea transports, at-target/waiting-gold/ready state and level-3 compact targets across loaded saves; it stays absent before meaningful corporation/Executive state exists.

### Revision 83 - SAS practical 6471

- **Date:** 2026-09-17
- **Git commit:** `23a3c7abe45b7f775a7c03f4ab904fe8a31bb1a3`
- **Change:** Added explicit AI fog-control / anti-Barbarian map-control provenance. `GAME_RECORD_AI_MAP_CONTROL_DECISION` records real `AI_guardCitySite` and `AI_guardYield` assignment/retarget changes with their already-computed site/guard/yield, defense/sight/fog-distance, path and action context, without extra target search, pathfinding or fog scans. Periodic `GAME_RECORD_BARBARIAN_PRESSURE` also identifies persistent city-site `MISSIONAI_GUARD_CITY` posture, including level-3 site/guard/current coordinates, so loaded saves retain ongoing fog-control state.

### Revision 82 - SAS practical 6470

- **Date:** 2026-09-17
- **Git commit:** `a864aa13593c9e80df49d4ff8967b7139bd8d00d`
- **Change:** Added compact AI religion-choice provenance at the real `AI_doReligion` boundary. Level 2 records meaningful switch/spread-block decisions with the pre-spread best and runner-up post-bias scores, current/selected religions, favorite/missionary/flavor context, best-religion spread/holy-city state, the raw values actually used by gameplay for switch probability, the real conversion probability/roll and realized outcome. Level 3 additionally serializes every eligible religion's already-computed chooser score. The recorder performs no extra religion valuation or RNG and suppresses routine keep-current evaluations to avoid per-turn noise.

### Revision 81 - SAS practical 6469

- **Date:** 2026-09-16
- **Git commit:** `3bcaa9af2c70561ee62b2c60e938cce216949849`
- **Change:** Added compact peace-decision provenance and knowledge-limited barbarian pressure. `GAME_RECORD_AI_PEACE_DECISION` records the real shared peace-negotiation boundary at level 2: UWAI versus legacy source, war age, initial/final end-war benefit values, provisional reparations, human-counterproposal use, final trade lists when available, and resolved outcomes such as victory-denial block, insufficient reparations/counterproposal, offer sent or AI-AI peace implemented/rejected. It reuses the live negotiation values/package rather than rerunning UWAI or trade valuation.

`GAME_RECORD_BARBARIAN_PRESSURE` complements the omniscient global barbarian rows with what each player's team can actually know: visible/non-invisible barbarian units and city proximity, revealed/visible/actionable-known barbarian cities, explore/city-attack UnitAI state, `MISSIONAI_EXPLORE` groups, and the AI's existing barbarian-defense-focus/attacker-need predicates. `BARBARIAN_UNIT_SPAWNED` also records plot ownership/terrain/feature, revealed/visible major-team counts and the nearest major-civilization city. The new observations add no spawn reevaluation, pathfinding or barbarian target scoring.

### Revision 80 - SAS practical 6468

- **Date:** 2026-09-16
- **Git commit:** `1cb708ab8dfc36d7200bd0b4e02cd70c4d6f62b1`
- **Change:** Added privacy-tiered runtime/install provenance and compact naval operational intent. `GAME_RECORD_EXE_CONTEXT` fingerprints the loaded `Civ4BeyondSword.exe`; level 2 records Windows/Wine runtime/build/update and process/native architecture plus coarse distribution/Steam AppID-build-beta metadata, while level 3 additionally records coarse CPU/GPU vendors, logical processors/RAM and exact EXE/mod paths.

`GAME_RECORD_DISPLAY_CONTEXT` now retries after loaded-save graphics initialization so short sessions do not omit display/GPU context. Level-3 naval posture also records each assault group's existing MissionAI destination, target team/city, cargo/capacity, support/base and ocean capability without new pathfinding or AI evaluation; war-start context now reuses the shared spaceship-parts-percent helper.
Note: Steam detection/path/build metadata are runtime-validated; GOG, Firaxis retail/other and Wine/Proton branches are source-reviewed but not yet runtime-tested.

### Revision 79 - SAS practical 6465

- **Date:** 2026-09-16
- **Git commit:** `439081be51b7ec481f72cda74688fce4ca8b5b33`
- **Change:** Added explicit territory/BFC/suburb unimproved-development totals and level-3 `GAME_RECORD_CITY_DEVELOPMENT` rows with owned/assigned-radius gaps, development/improvement coverage, remaining feature/resource types and bounded plot coordinates. Level 3 also serializes each already-maintained AI city-site shortlist as rank/coordinates/current found value. These are descriptive/cached-state additions only: no Worker build-legality/value scan, city-site reevaluation or pathfinding.

### Revision 78 - SAS practical 6464

- **Date:** 2026-09-16
- **Git commit:** `fb4c3dcb0b8d8fe9f085620a7bdcaf2ea059bc63`
- **Change:** Added compact strategic AI intent: current team war plans/ages, remaining high-level military-strategy flags, selected UWAI war-target context, and level-3 best-target `DEFERRED_ROLL` events without logging exhaustive rejected candidates. Espionage snapshots now distinguish foreign Spy locations from stored attack/recon/guard MissionAI intent. The RNG/state comparator also requires equal explicit `recordRevision` values before recipe-sensitive combined interpretation.

### Revision 77 - SAS practical 6463

- **Date:** 2026-09-16
- **Git commit:** `989eb50ce43e551708d7f573db4b140e28902307`
- **Change:** Added compact expansion/city-site intent: maintained shortlist/threshold/primary-site context, settler `MISSIONAI_FOUND` targets/ranks/cached values, normal founding choice plus two cached alternatives, and exact barbarian chooser winner/two runner-ups with raw/area/final values and random/site-spacing context. All reuse already-computed state/scans, adding no map-wide rescoring or pathfinding; also removed a duplicate `CvInfo_Symbol.h` include.

### Revision 76 - SAS practical 6461

- **Date:** 2026-09-14
- **Git commit:** `66f72899345d54e552c3a40da59b26d7cbdac270`
- **Change:** Strengthened runtime provenance with a compact tracked code/rules/scripts diff fingerprint and byte count in `GAME_RECORD_SOURCE_CONTEXT`, scoped to `CvGameCoreDLL`, `Assets/Config`, `Assets/Python`, `Assets/XML`, and `PrivateMaps`. This distinguishes different edits to the same runtime-relevant dirty paths and, together with the independent exact-byte loaded-DLL fingerprint, makes stale/unrebuilt DLL mistakes directly visible without hashing docs/LLM helpers or adding per-file timestamp noise.

### Revision 75 - SAS practical 6460

- **Date:** 2026-09-14
- **Git commit:** `40b3580cfa826150dfdb659452ec9f9fcf85cbd3`
- **Change:** Added compact periodic naval-assault posture covering assault lift/capacity/loading, current open-ocean capability, fleet-group loading/base-location/mission/support state and exact transported unit composition; also recorded the SAS UWAI naval-logistics deployment gameplay toggle in the canonical war-AI settings row.

### Revision 74 - SAS practical 6455

- **Date:** 2026-09-14
- **Git commit:** `320e73215cf08fa5b5af9fb4231c612a7cebf8f8`
- **Change:** Added one compact all-city `CITY_PRODUCTION_NO_TARGET` outcome at control-path-aware turn boundaries. Manual human cities are sampled before end-turn production processing, while AI-controlled and production-automated cities are sampled afterward; disorder is suppressed, and detailed legality/chooser-path evidence is kept in the dedicated BBAI category.

### Revision 73 - SAS practical 6446

- **Date:** 2026-09-12
- **Git commit:** `f8329120b31aad17a867ff5d1a679b474640108e`
- **Change:** Canonicalized invalid `TEAM_MET` first-contact coordinate pairs as `-1,-1` instead of serializing values that are undefined when their validity flags are false; ordinary valid coordinates and gameplay behavior are unchanged.

### Revision 72 - SAS practical 6443

- **Date:** 2026-09-10
- **Git commit:** `8ee577a98bdb2b362b20c3fbe68cdcd52c8521b4`
- **Change:** Added exact level-3 plot-ownership transition history with conservative immediate mechanism/source provenance, expanded causal transactions across city founding/culture expansion/flips, war/peace, vassalage and direct Python/WorldBuilder ownership chains, and extended CORE plot fingerprints with contested second-owner/forced-unowned state.

### Revision 71 - SAS practical 6442

- **Date:** 2026-09-10
- **Git commit:** `ac49c56121108e58b021d9bd127440ad03d68700`
- **Change:** Added compact level-3 semantic CORE state checkpoints at the existing authoritative-RNG lifecycle boundaries, with component/combined fingerprints, latent gameplay/AI state and measured computation time; extended the RNG comparison helper to validate and localize first RNG-versus-state divergence.

### Revision 70 - SAS practical 6441

- **Date:** 2026-09-10
- **Git commit:** `e7c316b1988fca98dc8baa1271ab47049b26d2d0`
- **Change:** Added session-local monotonic `seq` identity to every emitted structured `GAME_RECORD_*` row and generic causal `tx` scopes, initially bracketing city acquisition/raze so filtered records retain exact chronology and related city-transfer consequences remain explicitly joinable.

### Revision 69 - SAS practical 6440

- **Date:** 2026-09-10
- **Git commit:** `9337aece920266486be61a7bf60ec9f96e406bb9`
- **Change:** Added the explicit emitted `GAME_RECORD_SOURCE_CONTEXT recordRevision` field, public `SAS_GAME_RECORD_REVISION` constant, committed revision history, maintenance guidance, and consistency checks so downstream copies can cheaply detect any later official SASGameRecord-related code update.

### Revision 68 - SAS practical 6439

- **Date:** 2026-09-10
- **Git commit:** `03b44b8932a0715be234e8c5332fcb8a1d1cf3b2`
- **Change:** Standardized provenance headers across active AdvCiv-SAS files, including the SASGameRecord implementation, comparison helper and dedicated build checker. Runtime recorder behavior was unchanged, but the SASGameRecord-related code artifacts changed and therefore count under the current strict revision policy.

### Revision 67 - SAS practical 6438

- **Date:** 2026-09-10
- **Git commit:** `6673cf44c57730764b1da664e24673c9bd68a835`
- **Change:** Added level-3 authoritative map/synchronized RNG checkpoints with call/fingerprint/stream provenance, corrected session-rollover finalization, and added the SASGameRecord RNG comparison/validation helper.

### Revision 66 - SAS practical 6437

- **Date:** 2026-09-10
- **Git commit:** `c6d05a34b95b9da2df330d9c4ab537527310933c`
- **Change:** Added independently tunable 25%/50% initial geography overviews and an optional one-cell-per-real-plot native geography map with explicit extents.

### Revision 65 - SAS practical 6434

- **Date:** 2026-09-09
- **Git commit:** `04ed39adfe019a482136a72b4903c1c667d46bb8`
- **Change:** Expanded realized random-event and nuclear consequences with per-city/per-unit nuke effects and accepted EventInfo city/unit/player/building-modifier before/after consequences.

### Revision 64 - SAS practical 6432

- **Date:** 2026-09-09
- **Git commit:** `6efad6885ae140d115578b91291e2a2539fdef9d`
- **Change:** Added financial-strike state and exact strike-turn actions, disorder-city counts, angry/working population, and clearer assigned/free-specialist state and aggregates/deltas.

### Revision 63 - SAS practical 6431

- **Date:** 2026-09-09
- **Git commit:** `22aec5ffbb588a2d280e8a68480d1195642c3c87`
- **Change:** Added realized Civ4 random-event lifecycle history: delivered triggers, selected EventInfo/application state, target validity, gold/tech/pillage/free-unit/follow-up results, occurrence clearing and meaningful expiry, while excluding speculative AI valuation.

### Revision 62 - SAS practical 6399

- **Date:** 2026-09-04
- **Git commit:** `11fb13b1d07d8d706b5a41b57409c57de60636c4`
- **Change:** Optimized SASGameRecord implementation overhead by pre-gating recorder-only calculations, caching predicates and avoiding redundant production/bonus/trade/Worker/Settler/combat work; intended record semantics remain unchanged.

### Revision 61 - SAS practical 6398

- **Date:** 2026-09-04
- **Git commit:** `1ffe3c616ef20ae99d343df6a4667363e9f8e77c`
- **Change:** Expanded city population/state history with exact growth/starvation/prevented-growth, stored/granary food, maintenance, occupation/disorder/culture/religion/corporation/commerce/timers and richer empire aggregates.

### Revision 60 - SAS practical 6397

- **Date:** 2026-09-04
- **Git commit:** `c8dd8a9a52e273e274234f58df2ea708cd9d959f`
- **Change:** Added level-3 active-player trade-market snapshots for resources/technologies, willingness/network/trading availability, refusal/unavailability reasons, GPT capacity/quotes and optional AI technology values.

### Revision 59 - SAS practical 6396

- **Date:** 2026-09-04
- **Git commit:** `8abdbb31564245987390c96a182b14fc761d9e10`
- **Change:** Added Missionary and Executive attempt provenance (including failures and realized outcomes) and richer Spy interception/mission target identity, while preserving canonical consequence rows.

### Revision 58 - SAS practical 6394

- **Date:** 2026-09-04
- **Git commit:** `1ef349e7cf12b3be45f5b18f294cc74adac4ba42`
- **Change:** Added consequential action history for city hurry, pillage and realized gold, naval blockade lifecycle/plunder, unit gifts, religion/corporation membership changes and circumnavigation completion/bonus.

### Revision 57 - SAS practical 6393

- **Date:** 2026-09-04
- **Git commit:** `5e5e5463de7b3871bd5f4d50f48b2a5545293462`
- **Change:** Added complete diplomatic vote lifecycle history: proposal/trigger context, weighted ballots, election/results, defiers/endorsers, cancellation, persistent-effect activation/deactivation and one-shot application state.

### Revision 56 - SAS practical 6392

- **Date:** 2026-09-04
- **Git commit:** `a44fa2d733e09d6065c434d1f2e361973948ccf8`
- **Change:** Added standardized global/per-civilization starting-density and spacing history plus stronger periodic rival/known-city/other-team territory context.

### Revision 55 - SAS practical 6391

- **Date:** 2026-09-03
- **Git commit:** `00dcf84d8f7664a1cd5c88103e4a49803506f441`
- **Change:** Added production lifecycle history: genuine AI target switches/clears/resumptions, parked/restored production, aggregate transition counts and level-3 production-pipeline/parked-investment snapshots.

### Revision 54 - SAS practical 6390

- **Date:** 2026-09-03
- **Git commit:** `041a6f470867001f47919c24bae1664a42f2d4cc`
- **Change:** Expanded military quality/combat history with XP/levels/promotions/leadership/wounds, XP gained/prevented, promotion selections, veteran quality exchanged, nonlethal combat/attrition and expected-vs-observed combat-luck context.

### Revision 53 - SAS practical 6385

- **Date:** 2026-09-02
- **Git commit:** `1a54feb6433383e3799f89b61f7fe1109affcee0`
- **Change:** Greatly expanded city-raze history with pre/post city/player/team/victory context, explicit razer/previous/original ownership, city contents/state, land/population/city deltas and post-raze tile ownership.

### Revision 52 - SAS practical 6384

- **Date:** 2026-09-02
- **Git commit:** `7ca547151beb63f258d1062a4bdf84f56a5b79d0`
- **Change:** Added realized goody outcomes (gold, reveal, XP/healing, tech progress/acquisition, free/promoted/Barbarian units) and exact partial-research progress; expanded periodic current-tech progress/cost context.

### Revision 51 - SAS practical 6382

- **Date:** 2026-09-02
- **Git commit:** `ce3eb23439961915555570664aeb29623f3ed34e`
- **Change:** Added research lifecycle history: exact completion/overflow accounting and meaningful research-target redirections with team context and explicit causes.

### Revision 50 - SAS practical 6381

- **Date:** 2026-09-02
- **Git commit:** `c629781a52a463a4ef0be4dcce09f78450300db4`
- **Change:** Added exact rejected AI-to-human ordinary trade offers through a BUG-to-DLL bridge while preserving canonical SASGameRecord trade formatting.

### Revision 49 - SAS practical 6380

- **Date:** 2026-09-02
- **Git commit:** `4cd378ab4d7a152f90a7b252f897cc0642091f58`
- **Change:** Replaced generic diplomacy-event history with semantic resolved interactions (help/demands/religion/civic pressure/join-war/embargo), accepted/refused outcomes, before/after attitude/memory/war state, submitted human offers and exact AI counterproposals.

### Revision 48 - SAS practical 6379

- **Date:** 2026-09-02
- **Git commit:** `5d43e0ce2eedf80d37e56ab1026974d5f9379190`
- **Change:** Added random/manual civilization and leader provenance, exact team-merge boundaries, nuclear-launch context, and realized nuclear explosion consequences such as fallout, destroyed assets, unit damage/loss and population killed.

### Revision 47 - SAS practical 6358

- **Date:** 2026-08-31
- **Git commit:** `94f6359e28ab8c4b3cce757cff6ff148273fd9bf`
- **Change:** Added persistent savegame source-version history to SASGameRecord so creation source and later version/SHA transitions survive loads.

### Revision 46 - SAS practical 6357

- **Date:** 2026-08-31
- **Git commit:** `3a8b85dab7557eff3b135533bdfec269d3a27cbd`
- **Change:** Added automatic runtime source provenance: practical version, Git commit/short commit, branch, commit date/metadata source and dirty tracked-tree state, including Git-archive support.

### Revision 45 - SAS practical 6353

- **Date:** 2026-08-31
- **Git commit:** `d8358a19dc29cdb44f55a05d298e2428c3d30eeb`
- **Change:** Further compacted initialization/timing output: authoritative finalized setup replaces procedural chatter, player identities precede team data, identical starting-tech sets are grouped, and wall-clock fields stay on meaningful boundaries.

### Revision 44 - SAS practical 6351

- **Date:** 2026-08-31
- **Git commit:** `9068ad28635d8be44965efadf9bce1738e1b412d`
- **Change:** Normalized finalized initialization reporting around shared authoritative `INITIAL_*` team/technology/deal state, reduced routine setup chatter/deal floods, and centralized quoting/list/filename/team/trade serialization helpers.

### Revision 43 - SAS practical 6347

- **Date:** 2026-08-31
- **Git commit:** `78378a2e3c9521680f9d478214c7e6c88617047b`
- **Change:** Added shared loaded-DLL provenance: build target/configuration, compile flags, size, write UTC, PE timestamp and cached FNV-1a binary fingerprint; moved common provenance/timing helpers into shared game-core utilities.

### Revision 42 - SAS practical 6345

- **Date:** 2026-08-31
- **Git commit:** `5a71f874e5c716d183338fbe07c30ee501b8ba65`
- **Change:** Added `sessionWallMilliseconds` to every emitted row, authoritative Debug-mode transition history, per-request autoplay wall time, and preservation of original timestamps for buffered initialization actions.

### Revision 41 - SAS practical 6343

- **Date:** 2026-08-30
- **Git commit:** `bfa4dfdeef990a67279600891674d8716326b90d`
- **Change:** Expanded setup provenance with custom map-script option selections/defaults/descriptions, Advanced Start points, resolved UWAI/legacy war-AI mode, and buffered initialization actions so stable finalized setup context precedes them.

### Revision 40 - SAS practical 6328

- **Date:** 2026-08-30
- **Git commit:** `98ee0c269abf6dc0459e4d8c5062ab0a39d38445`
- **Change:** Unified diagnostic UTC identity with BBAI by adding shared process-level UTC provenance and using the generic shared UTC formatter for SASGameRecord sessions.

### Revision 39 - SAS practical 6326

- **Date:** 2026-08-29
- **Git commit:** `66b46c22d2485e744d2703f8c9a9773cb15ae16b`
- **Change:** Changed mod provenance to distinguish the centralized branded/display name from the actual loaded folder name/path (`displayName`, `folderName`, `modPath`).

### Revision 38 - SAS practical 6293

- **Date:** 2026-08-27
- **Git commit:** `617843aa2bc9c108530719f7783c6467b1c85ea7`
- **Change:** Hardened SASGameRecord military counting against invalid/unplaced unit-container entries so malformed objects cannot crash snapshots or count toward military posture.

### Revision 37 - SAS practical 6250

- **Date:** 2026-08-24
- **Git commit:** `f0ee784b6444e9a0ebedb67722fa4b89f9e29314`
- **Change:** Fixed six record defects: exact failed-attack/battle coordinates and dependent context, inclusive battle-summary boundaries, session-vs-lifetime counter naming, `-1` production sentinels, disorder process-conversion suppression, and safe rollover finalization of buffered old-map observations.

### Revision 36 - SAS practical 6249

- **Date:** 2026-08-24
- **Git commit:** `f2d72e7f90a8640dce6600f1afe0c85b62cb3887`
- **Change:** Fixed recorder correctness/safety issues: nearby-enemy hostility now uses each unit's actual plot, long structured rows grow instead of truncating at 2047 bytes, and Spy mission-discount preparation is counted only for valid ordinary Spies.

### Revision 35 - SAS practical 6124

- **Date:** 2026-08-18
- **Git commit:** `234f87f13c4d7c23411c83faa13186f4f5bc7823`
- **Change:** Compacted production-overflow reporting by moving exact overflow evolution (`rawModifiedOverflow`, `unmodifiedOverflow`, `keptOverflow`, lost production, unused capacity and overflow gold) into detailed completion rows while retaining aggregate flow rows.

### Revision 34 - SAS practical 6123

- **Date:** 2026-08-18
- **Git commit:** `574e50ba532286ada297fca3a49a9af375c1bcc5`
- **Change:** Improved Great Person/Great General provenance by adding newborn unit IDs and spawn coordinates and recording direct player-caused deaths of defenseless Great People.

### Revision 33 - SAS practical 6119

- **Date:** 2026-08-16
- **Git commit:** `3ffd61d7959e56861c8a056237981310642bcee1`
- **Change:** Added explicit autoplay request IDs, requested/completed turn counts, player changes, wall/run state and authoritative autoplay end causes.

### Revision 32 - SAS practical 6118

- **Date:** 2026-08-15
- **Git commit:** `e67adf522de45321fad3d46ce137796f3ab83e48`
- **Change:** Made each SASGameRecord text-map layer independently optional through XML defines; recorder output can therefore omit selected map layers intentionally.

### Revision 31 - SAS practical 6111

- **Date:** 2026-08-12
- **Git commit:** `8ab3703280e87ffb7a8a8cc3fb9c349c7ffa165a`
- **Change:** Encoded natural food quality in terrain-map letter case using terrain/hill/feature/lake/river/permanent-yield context and a tunable threshold.

### Revision 30 - SAS practical 6110

- **Date:** 2026-08-11
- **Git commit:** `ea2f16e4e5904286e8facc7e026d259cf5e5f573`
- **Change:** Added directional river maps, exact river-edge totals/coordinates, and recording of rare later river edits.

### Revision 29 - SAS practical 6109

- **Date:** 2026-08-11
- **Git commit:** `129d438d80ac106aa77b3acebe613eb9fab3b6e2`
- **Change:** Added initial bonus maps, runtime-validated symbol legends, type totals, resampling/collision information and per-layer quantitative counts.

### Revision 28 - SAS practical 6108

- **Date:** 2026-08-11
- **Git commit:** `404d43461d2c67af87862341b7609ac882782b0e`
- **Change:** Added configurable terrain and evolving feature map layers, with changing feature/political layers repeatable during the run.

### Revision 27 - SAS practical 6107

- **Date:** 2026-08-11
- **Git commit:** `ad20f152bd488a871c26a72c4471e5d3beba63cd`
- **Change:** Added aspect-correct SASGameRecord ASCII map rendering with explicit player/civilization/name mappings.

### Revision 26 - SAS practical 6106

- **Date:** 2026-08-11
- **Git commit:** `a7a071f1be63b652070811ccb7eda27a7b1cfbdf`
- **Change:** Expanded Barbarian history with city, spawn, position, unit and combat-pressure context.

### Revision 25 - SAS practical 6105

- **Date:** 2026-08-11
- **Git commit:** `724500d4a0ac6604f0df2e817629981a09e42ec9`
- **Change:** Added calendar/start-turn/start-year, player-color, and final-score/replay-related context to the record.

### Revision 24 - SAS practical 6104

- **Date:** 2026-08-11
- **Git commit:** `a84d4747204a99de6214942f94a80e7c2360745f`
- **Change:** Added millisecond timing and tunable privacy-tiered system/performance context, including snapshot UTC/wall timing and optional process/window/runtime/memory information.

### Revision 23 - SAS practical 6103

- **Date:** 2026-08-11
- **Git commit:** `e990260efc0d4f22d0718a443d18e66b522e0e79`
- **Change:** Added synthetic whole-war outcome summaries covering duration, war success, losses/production value destroyed, city-plot battles, conquests and captured population, including ongoing/end-state context.

### Revision 22 - SAS practical 6102

- **Date:** 2026-08-10
- **Git commit:** `fd869b094ef88b16a9c7bc4952462e9fba0d6106`
- **Change:** Added durable session context for game type/mode, multiplayer format/options and turn handling, and standardized shared enum tokens.

### Revision 21 - SAS practical 6101

- **Date:** 2026-08-10
- **Git commit:** `5d00ec19e86215271fb6aa37b4933f1a55c7e3ac`
- **Change:** Added explicit technology-acquisition provenance, distinguishing research, trade, free choices, huts, Great People, espionage, sharing, inheritance, setup and other paths.

### Revision 20 - SAS practical 6100

- **Date:** 2026-08-10
- **Git commit:** `d24d15505cd41a53df3579aa9844c347cb618025`
- **Change:** Added compact interval production and military flow histories plus policy/civic/religion-style state history, while retaining detailed level-3 evidence.

### Revision 19 - SAS practical 6097

- **Date:** 2026-08-09
- **Git commit:** `c7bfe6cc181619ccc59a9f0694b4b8b898558ae2`
- **Change:** Added exact winner/loser unit IDs to `GAME_RECORD_BATTLE` so combat results can be joined reliably to unit-specific attack-order diagnostics.

### Revision 18 - SAS practical 6096

- **Date:** 2026-08-09
- **Git commit:** `b5a184403ef9fdd75d3dd30c5e3a3ef070b56f55`
- **Change:** Renamed the snapshot-interval define and logged setting from `SAS_GAME_RECORD_TURN_INTERVAL` to `SAS_GAME_RECORD_INTERVAL_TURNS_UNSCALED_GAMESPEED`, making its intentional literal-turn semantics explicit.

### Revision 17 - SAS practical 6092

- **Date:** 2026-08-07
- **Git commit:** `c30e4e1ef0d37675aba12d668ca8b514e079ce26`
- **Change:** Added current/undamaged city-defense and bombard state, synthetic consecutive city-bombard sequences, and individual air-strike/interception/plot-air-bomb history.

### Revision 16 - SAS practical 6091

- **Date:** 2026-08-07
- **Git commit:** `63eef1e11158ca8a0b69d415f927fab70c5a7bb9`
- **Change:** Added `UnitCombat` composition shares, compact air/missile/nuclear posture including cargo, and per-city air-unit occupancy/capacity.

### Revision 15 - SAS practical 6090

- **Date:** 2026-08-07
- **Git commit:** `1a80ca7cff111011fa27c8f19ebf19fe44b5fe0b`
- **Change:** Added initial map/landmass geography and resource/yield context.

### Revision 14 - SAS practical 6086

- **Date:** 2026-08-05
- **Git commit:** `bff444456275a42631f5ad449fec942dfb6ff310`
- **Change:** Corrected SASGameRecord army accounting by separating true `combatUnits` from Civ4's narrower XML-based `militarySupportUnits` concept.

### Revision 13 - SAS practical 6085

- **Date:** 2026-08-05
- **Git commit:** `f651eeade3e95dcb49670625ee2fd5dcaa3a92dd`
- **Change:** Added AI military-production information to SASGameRecord alongside BBAI diagnostics.

### Revision 12 - SAS practical 6084

- **Date:** 2026-08-05
- **Git commit:** `b67e6210638191af81b21fd1c8079344c48365b1`
- **Change:** Extended existing rows with espionage context: actual per-rival EP spending, espionage strategy flags, and per-city espionage output/modifier/defense information.

### Revision 11 - SAS practical 6083

- **Date:** 2026-08-05
- **Git commit:** `cac3fa4d2bdd225f744c7ee3bc5231e63aad37d0`
- **Change:** Renamed the feature from `SASGameSummary` to `SASGameRecord` throughout filenames, symbols, XML defines and row names (`GAME_SUMMARY_*` -> `GAME_RECORD_*`).

### Revision 10 - SAS practical 6077

- **Date:** 2026-07-22
- **Git commit:** `b80afdad17c550772150ccfc41ed01067897335c`
- **Change:** Added territory-development coverage, routes/improvements/irrigation and bonus-development context, runtime/mod identity, enabled victory/game-limit context, AI victory-stage strategy context, and player-wide health/happiness modifier sources.

### Revision 9 - SAS practical 6075

- **Date:** 2026-07-22
- **Git commit:** `22dc2f0abd71e870dcb333a5c82ed6c9338f5f18`
- **Change:** Expanded state reporting with production overflow/loss, production-to-commerce conversion, wonder/project fail gold, pollution sources, city buildings, trade-capability unlocks, research overflow context, and clearer human/autoplay-control identity.

### Revision 8 - SAS practical 6058

- **Date:** 2026-07-20
- **Git commit:** `0b7a1566d7c17085171cc0ea49a30ffe419aed33`
- **Change:** Added war-declaration origins/sponsors, diplomacy memories, broader victory-progress context, project-victory reset/failure context, and compact full-map revelation history.

### Revision 7 - SAS practical 6057

- **Date:** 2026-07-19
- **Git commit:** `05b03177383c158c0962000fb2979a06850456ef`
- **Change:** Added final victory snapshots, project-victory progress, exploration history, and map/environment change reporting.

### Revision 6 - SAS practical 6046

- **Date:** 2026-07-16
- **Git commit:** `559ee966cbc17bcf6b9891acf367a9e0bfa10f24`
- **Change:** Added factual army-concentration/attack-stack context, Great Person use, and espionage-action information to the structured record alongside corresponding BBAI diagnostics.

### Revision 5 - SAS practical 6034

- **Date:** 2026-07-13
- **Git commit:** `cecab8af1e29b99c0996bbf68418aebbb66dd0d7`
- **Change:** Refactored structured-record trade-item, diplomacy-event and war-plan token naming onto shared stable SAS token helpers. Intended record semantics stayed equivalent, but downstream copied implementations should review the helper change.

### Revision 4 - SAS practical 6033

- **Date:** 2026-07-13
- **Git commit:** `d8bdd0602e765b4d945e6a4e25f447415b074241`
- **Change:** Made free-text fields parser-safe through quoting/escaping; also expanded run-status and lifecycle context such as player appearance/revival/elimination and autoplay state so stopped runs could be interpreted without inferring from missing snapshots.

### Revision 3 - SAS practical 6030

- **Date:** 2026-07-12
- **Git commit:** `26b0d5967d691fc5d59a350856ffc7597b47c290`
- **Change:** Added Worker danger/death context and recorded in-game bonus appearances/disappearances.

### Revision 2 - SAS practical 6026

- **Date:** 2026-07-11
- **Git commit:** `876158dff2f27852320810189730865c68fd69e7`
- **Change:** Added AI Settler security/context information to the structured record, including nearby-unit/defender context used to understand whether Settlers were adequately protected.

### Revision 1 - SAS practical 6022

- **Date:** 2026-07-10
- **Git commit:** `c023244d86276285ac0a6511f02316d71047dabc`
- **Change:** Introduced the independent structured `SASGameSummary` recorder, separate from BBAI, with lifecycle/action rows plus compact economy, expansion, worked-plot, statistics, city/battle-history and unit-composition reporting.

## Maintenance template

For the next qualifying committed update, increment the public source constant and prepend one entry like this:

```markdown
### Revision N - SAS practical XXXX

- **Date:** YYYY-MM-DD
- **Change:** Briefly state what changed in SASGameRecord-related code and why a downstream copy should review/update.
```

Do not try to place the final SHA of the same not-yet-created commit into its own history entry: changing the document would change that SHA again. Historical entries can retain already-known SHAs, while current runtime Git/source identity is recorded independently by `GAME_RECORD_SOURCE_CONTEXT`.

Standalone docs/history/example-log/package-only updates do not bump the revision. If a qualifying code change and those maintenance files are committed together, they remain one revision.

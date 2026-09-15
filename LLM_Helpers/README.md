# LLM helpers

## SASGameRecord comparison helpers

### `compare_sasgamerecord_rng.py`

- Reads two `SASGameRecord` `.log` files or ZIP files containing exactly one `.log` each.
- Validates every authoritative-RNG checkpoint's interval/session counter arithmetic, interval-state continuity, and Civ4 LCG progression whenever the interval contains no explicit seed replacement. When semantic CORE-state checkpoints are present, it also validates paired state-checkpoint identities, component/combined fingerprints, object counts and computation timings.
- Reports the first differing lifecycle checkpoint and its differing map/synchronized RNG or semantic-state fields, then distinguishes changed RNG consumption, changed call provenance and deterministic/non-authoritative-RNG state divergence. A lone trailing `SESSION_FINALIZE` is identified as a harmless session-lifecycle difference when every comparable checkpoint matches.
- Warns when `GAMEOPTION_NEW_RANDOM_SEED` is enabled because repeated save reloads then intentionally reseed the synchronized RNG and are not expected to reproduce the same stream.
- Exit status is 0 when all comparable checkpoints match (including a lone trailing `SESSION_FINALIZE`), 1 for a valid gameplay/checkpoint divergence, and 2 for invalid input or failed internal invariants.
- Does not modify either record and adds no game/runtime overhead.
- [`examples/sasgamerecord_rng_compared.txt`](examples/sasgamerecord_rng_compared.txt) is a retained report from two real AdvCiv 1.14 repeated-load validation runs. Refresh it with `--example-output`; use `--output <path>` for another retained report.

Interpretation:

- `valid` means each individual record passed interval/session counter arithmetic, state continuity, and every applicable independent LCG reconstruction before comparison.
- Different call counts mean one run consumed additional or fewer authoritative RNG advances in that interval.
- Different state or stream fingerprints mean authoritative random consumption diverged, even if the call totals happen to match.
- A call-fingerprint-only difference means the random stream still matches but its labels, data arguments, NULL-message classification or EXE-wrapper origin changed.
- A lifecycle/checkpoint mismatch usually means the records represent different boundaries or were paired from unlike run sequences.
- Once semantic-state rows are present, a state difference while authoritative RNG still matches localizes a deterministic or untracked-state divergence; the component hashes narrow it to game, team, player, city, unit, selection-group, plot or deal state.

Examples:

```powershell
python LLM_Helpers\compare_sasgamerecord_rng.py "C:\path\run_a.log" "C:\path\run_b.log"
python LLM_Helpers\compare_sasgamerecord_rng.py "C:\path\run_a.zip" "C:\path\run_b.zip"
python LLM_Helpers\compare_sasgamerecord_rng.py "C:\path\run_a.log" "C:\path\run_b.log" --example-output
```

# Inherited map-script reference sources

This is a tracked, greppable, non-runtime reference corpus for AdvCiv-SAS archaeology. Use it to compare current `PrivateMaps` descendants with downloaded upstream/third-party scripts and to establish whether a defect was inherited or introduced during AdvCiv-SAS integration.

These files are not imported or loaded by Civ4. Current AdvCiv-SAS source and Git history remain authoritative. Do not silently edit a reference file to match current code; repair the runtime descendant and document the comparison instead.

## Imported packages

The corpus was copied on 2026-08-20 from `C:\Users\PC\Downloads\Inherited_mapscripts`. Original download archive names and SHA-256 hashes:

- `61569-equal_islands_v2_beta.zip`: `8753B09F60501EBFA1DBC0F80922271591B5B31DDF89B2E8AF6BCE45C628F4C7`
- `80471-water.zip`: `F552AF69C30C2232659D525FED7399299AF50FA87B8739E80CA6BD60D6B2D4B0`
- `BTG_2.43_PublicMaps.zip`: `642C596C0B2FD23EA56349E09E9C3D976EE3DA08673626138CD201B5D4CF47C4`
- `Planet_Generator_0_68.zip`: `502EFC74B1E2D8A27241D1200A7F3E6D7246C0EE0676CAA0ADE86A0A763F9337`

The archive names and local files are provenance evidence, not an independent certification of their original hosting pages, authorship, licensing or release dates. Preserve upstream credit/readme text where present.

## Selection policy

The source folder contained 300 files totaling 57.65 MiB. This tracked form preserves all 174 greppable `.py`, `.txt` and `.properties` files totaling 11.08 MiB, including BTG's archived/external source references. It deliberately omits duplicate/nested `.zip`, `.rar` and `.7z` archives, DDS art, and WorldBuilder scenario binaries.

For portable Windows Git paths, the tracked directory uses shorter package/directory names: `EqualIslands`, `Water`, `BTG243`, `Planet068`, and within BTG `A`, `External`, `Look` and `Maps` abbreviate `Archives`, `Other External`, `Other to look` and `Map Scripts`. Remaining directory-name whitespace is normalized to `_` (for example, `Original BTS Maps` becomes `Original_BTS_Maps`, and consecutive spaces become one underscore). File contents are byte-for-byte copies; these path changes do not imply modified upstream source.

This directory is excluded from ordinary player/GitHub Download ZIP archives through `.gitattributes`, but `make_light_source_zip.py` includes the current files because that archive is specifically for ChatGPT/code-agent review. Generated commit-diff mirrors exclude the corpus so its one-time vendored import is not duplicated through historical patches. Line-ending cleanup/check tools exclude it so downloaded originals retain their source formatting.

## Suggested use

Start with an exact filename or distinctive expression, then compare the reference, current runtime script and tracked history:

```powershell
rg -n "tinySouthY|iContinentsGrainEast" LLM_Helpers\map_refs PrivateMaps
rg -n "isFreshWater|generatePlotsParallelContinent" LLM_Helpers\map_refs PrivateMaps
```

When the same defect exists here and in the SAS import/birth commit, classify it as inherited third-party/pre-SAS rather than SAS-specific. Record which package/file established provenance in `advciv_kmod_archaeology_progress.txt` and the corresponding Known Issues entry.

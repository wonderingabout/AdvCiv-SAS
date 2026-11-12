# AdvCiv-SAS EXE Patches Guide

> **Disclaimer:** this guide is provided only as general information, without any warranty. It does not encourage disassembling, patching or otherwise modifying the game. Anyone who uses it does so at their own risk and responsibility, including for checking and complying with the game's license and the laws that apply to them; see [The game's executable](/LICENSE.md#the-games-executable).
>
> The disclaimer at the top of the [Modding Resources README](/_1_AdvCiv-SAS/Docs/Modding_Resources/README.md) and the [copyright and disclaimer](/LICENSE.md#copyright-and-disclaimer) apply here too: these instructions come without any warranty, and we cannot be held responsible for any damage or consequence of following them, correctly or not.

How the user and AI/LLM helpers study runtime patches of `Civ4BeyondSword.exe`: what they are, how to read the EXE with Ghidra, and a map of Realism Invictus's patches checked against our Steam EXE.

Written by Claude Code Opus 5.5 on 2026-11-12.

## Menu

[What EXE patches are](#what-exe-patches-are)\
[Handling the EXE and its copies](#handling-the-exe-and-its-copies)\
[Steam and GOG EXEs](#steam-and-gog-exes)\
[Reading the EXE with Ghidra](#reading-the-exe-with-ghidra)\
[Helpers in LLM_Helpers/exe_analysis](#helpers-in-llm_helpersexe_analysis)\
&emsp;[`dump_exe_image.py`](#dump_exe_imagepy)\
&emsp;[`describe_exe_sites.py`](#describe_exe_sitespy)\
[Patches in AdvCiv-SAS](#patches-in-advciv-sas)\
[Realism Invictus patch map](#realism-invictus-patch-map)\
&emsp;[UI scaling patches](#ui-scaling-patches)\
&emsp;[Graphics and animation fixes](#graphics-and-animation-fixes)\
&emsp;[Rendering hooks](#rendering-hooks)\
&emsp;[Window and input](#window-and-input)\
&emsp;[Can we trust RI's GOG addresses](#can-we-trust-ris-gog-addresses)\
&emsp;[Lessons from RI's history](#lessons-from-ris-history)\
&emsp;[Lessons from our own setup](#lessons-from-our-own-setup)

## What EXE patches are

Python and the DLL cannot reach everything: some sizes and limits are hardcoded in the EXE, for example the 850x569 pre-game setup window, the +200px reserve under popup headers and the 260px tooltip width.

A DLL can still change them while the game runs: it overwrites a few bytes of the EXE's code in memory, or redirects a call to its own code. The EXE file on disk is never changed.

- AdvCiv started this in [`SelfMod.cpp`](/CvGameCoreDLL/SelfMod.cpp) (`advc.092b`/`advc.092c`, f1rpo's "smc" proof of concept), with the plot indicator size and help text area width.
- Realism Invictus grew the same file to over 6,000 lines in 2026, mostly for UI scaling at larger fonts; see the [map below](#realism-invictus-patch-map). RI's `Documentation/License.txt` says its team allows full and unrestricted use of the mod's assets, so porting its patches is fine, with credit.

## Handling the EXE and its copies

- Never ship a modified EXE: 2K's license, which RI's `License.txt` also reproduces, forbids distributing a changed executable. Runtime patches from the DLL avoid that, which is why AdvCiv and RI use them.
- The same license forbids disassembling the game. Modders such as f1rpo, sqwishy and RI's team read the EXE this way to make patches; the user decides whether we do.
- Keep the decrypted copy and the Ghidra project in `Downloads/AdvCiv-SAS_LLM/exe_analysis/`, outside the repository: they are the game's own code, so never commit, ZIP or share them.

## Steam and GOG EXEs

A patch is written for one exact EXE build. Two builds of BtS 3.19 matter, and RI names them V1 and V2:

| Variant | Builds | On disk |
| --- | --- | --- |
| V1 | GOG and CD/DVD, which share one EXE | plain code |
| V2 | Steam, including its beta branch | code encrypted by Steam's DRM wrapper (SteamStub), which decrypts it in memory at startup |

- This V1/V2 split is RI's, and its comments give each patch an address for both. We only confirmed it on our Steam EXE: it has a `.bind` section, the wrapper's mark, and at RI's version-check address `0x00601EEC` the file held other bytes than RI's expected `PUSH 0x00C4C678`, while the decrypted copy matched.
- Addresses differ between V1 and V2, but discovering or adding one patch does not move the others: the EXE never changes, so each address stays fixed. Two patches clash only if they touch the same bytes.
- RI checks each site's bytes before patching and skips a site that does not match, so an unknown EXE gets no patch rather than a wrong one. Keep that rule for any patch we write.

## Reading the EXE with Ghidra

The tools, installed on 2026-11-12. They are listed only here, not in [Tools for AI/LLM helpers](/_1_AdvCiv-SAS/Docs/Modding_Resources/README.md#tools-for-aillm-helpers), which ships in player downloads and only points to this guide:

- Ghidra 12.2, unzipped to `C:\Tools\ghidra_12.2_PUBLIC` from its [GitHub releases](https://github.com/NationalSecurityAgency/ghidra/releases), the zip checked against the release's SHA-256. `support\analyzeHeadless.bat` runs analyses and scripts without the window.
- Temurin JDK 25 (`winget install EclipseAdoptium.Temurin.25.JDK`). Ghidra 12.2 needs Java 25 (`application.java.min=25`), while an older Amazon Corretto JDK 21 comes first on PATH, so set `JAVA_HOME` to `C:\Program Files\Eclipse Adoptium\jdk-25.0.5.8-hotspot` before running Ghidra yourself, as in step 2 below; `describe_exe_sites.py` sets it itself.
- Two lines added to `C:\Tools\ghidra_12.2_PUBLIC\support\launch.properties` keep Ghidra's settings and cache in `C:\Tools\ghidra_user`; see [Lessons from our own setup](#lessons-from-our-own-setup).

Each step is a command an agent runs itself; the user needs no Ghidra knowledge:

1. [`dump_exe_image.py`](#dump_exe_imagepy) writes a decrypted copy of the EXE.
2. Ghidra's headless analyzer imports that copy into a project once, with the command under `dump_exe_image.py`.
3. [`describe_exe_sites.py`](#describe_exe_sitespy) describes chosen addresses from that project.

## Helpers in LLM_Helpers/exe_analysis

These sections moved here verbatim from `LLM_Helpers/README.md` on 2026-11-12, apart from links, so that EXE patch knowledge stays in this guide, which player downloads leave out; `LLM_Helpers/README.md` only points here.

### `dump_exe_image.py`

Writes a decrypted copy of the Steam EXE that Ghidra can read, to `Downloads/AdvCiv-SAS_LLM/exe_analysis/Civ4BeyondSword_decrypted.exe`, outside the repo.

- Why it exists: the Steam EXE is wrapped by Steam's DRM (SteamStub). It has a `.bind` section and its `.text` code is encrypted on disk, so at Realism Invictus's Steam patch address `0x00601EEC` the file held other bytes than the `PUSH 0x00C4C678` RI's comments expect. RI's separate V1 and V2 addresses already account for this; the copy lets us read the code RI's V2 patches were written for.
- How: it launches Civ4 without a mod, waits until `.text` in memory differs from the file and stops changing, copies the whole image with `ReadProcessMemory`, closes the game it started and rewrites the section table so file offsets equal memory addresses.
  - Copying that early, before any mod DLL loads, keeps runtime EXE patches out of the copy, AdvCiv's own [`SelfMod.cpp`](/CvGameCoreDLL/SelfMod.cpp) included.
  - With `--pid` it reads a running client instead and leaves it open; that copy then includes whatever the loaded DLL already patched.
- It checks RI's Steam ("V2") address and fails if the bytes differ. On 2026-11-12 two runs gave the same `.text` SHA-256 `7d0c5148...` and matched RI, so our Steam EXE is the build RI's V2 patches were written for.
- The copy is for reading only: the game's own EXE is never written.

```powershell
py -I LLM_Helpers/exe_analysis/dump_exe_image.py
```

Then import it into Ghidra without the window, setting `JAVA_HOME` to JDK 25 as described above:

```powershell
& "C:\Tools\ghidra_12.2_PUBLIC\support\analyzeHeadless.bat" "$env:USERPROFILE\Downloads\AdvCiv-SAS_LLM\exe_analysis\ghidra" Civ4BtS -import "$env:USERPROFILE\Downloads\AdvCiv-SAS_LLM\exe_analysis\Civ4BeyondSword_decrypted.exe" -overwrite -max-cpu 2
```

- On 2026-11-12 the import and full auto-analysis took 128 seconds on 2 cores (`-max-cpu 2`, of 16 logical processors); the saved project is then reused without analyzing again.
- Pitfall: run from an agent in the Claude desktop app, Ghidra first stopped with `The data file must be inside the data dir` from its Felix plugin framework. The app is a packaged Windows app, so writes under `AppData\Roaming` by programs it starts are redirected into its own `Packages\Claude_...\LocalCache`, and Felix saw two real paths for one folder.
  - Running outside the agent's sandbox did not help. `-Dapplication.settingsdir` and `-Dapplication.cachedir` lines added to `C:\Tools\ghidra_12.2_PUBLIC\support\launch.properties` move Ghidra's settings and cache to `C:\Tools\ghidra_user`, which is not redirected.
- Added with help of Claude code Opus 5.5.

### `describe_exe_sites.py`

Has headless Ghidra describe EXE addresses: for each, the containing function, ten instructions around it (the address marked `>>`) and the decompiled function, in one text file, so an agent can read a patch site without Ghidra's window.

- It runs `ghidra_scripts/DescribeAddresses.java` on the project imported from [`dump_exe_image.py`](#dump_exe_imagepy)'s copy, read-only and without analyzing again, and finds JDK 25 itself.
- Addresses come as arguments, optionally labelled (`0x0057C9EB:popup_margin`), or from a tab-separated `--file` of address and label.
- Pitfall: `analyzeHeadless.bat` failed on the repository's script folder, since cmd cannot parse `(x86)` and `Sid Meier's` in a batch argument, so the script is copied into a temporary folder first.
- On 2026-11-12 it described 20 of Realism Invictus's Steam patch sites in one run; see the [patch map](#realism-invictus-patch-map).

```powershell
py -I LLM_Helpers/exe_analysis/describe_exe_sites.py 0x0057C9EB:popup_margin 0x00616167:tooltip_width
```

- Added with help of Claude code Opus 5.5.

## Patches in AdvCiv-SAS

All live in [`SelfMod.cpp`](/CvGameCoreDLL/SelfMod.cpp) and switch off together with `SAS_EXE_P_ON` in [GlobalDefines_advciv_sas.xml](/Assets/XML/GlobalDefines_advciv_sas.xml), which replaced AdvCiv's `DISABLE_EXE_RUNTIME_MODS` with the opposite polarity; `SAS_EXE_P_STEAM_ON` and `SAS_EXE_P_GOG_ON` choose which EXE builds to patch.

- AdvCiv's own two: the plot indicator size and the help text area width (`advc.092b`, `advc.092c`). Since 2026-11-12 each also has its own switch, `SAS_EXE_P_PLOT_INDICATOR_ON` and `SAS_EXE_P_HELP_TEXT_AREA_ON`, so one patch can be turned off without the others; before, only the master switch covered them.
- Setup-screen size (2026-11-12, `SAS_EXE_P_DYNAM_MAIN_MENU_*`), ported from RI's `setSetupScreenSize`; see [KI#1082](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1082) for the problem and the tests.
  - The site, its disassembly and its expected bytes are RI's. RI rewrites the two size immediates once, one fixed size per font setting. Ours instead writes a 5-byte `JMP` at the function's entry to `sasSetupScreenGetSize` in the DLL, which keeps the replaced function's contract (one stack argument, `RET 4`, the pointer returned in `EAX`).
    - At startup the game's resolution is unknown, since only the splash window exists. Our function runs each time a setup screen opens, measures the game window, and returns `window size * PCT / 100 + ADD` for each side.
  - Before writing, it checks that the site lies in the EXE's committed code (`VirtualQuery`) and holds the expected 20 bytes; otherwise the patch skips itself, as on an unknown EXE.
  - A result larger than the window is cut to its width and to its height minus `SAS_EXE_P_DYNAM_MAIN_MENU_HEIGHT_FREE_MIN` (80 px, a little under twice the bar's 44 px), so the main menu's bottom bar and GO BACK stay visible.
  - Tested on Steam on 2026-11-12 in 1920 x 1080, 2560 x 1380 and 3806 x 2100 windows and in 1920 x 1080 fullscreen; GOG's address is RI's and untested by us.
- World-picker globe size (2026-11-12, `SAS_EXE_P_DYNAM_MAIN_MENU_GLOBE_*`), ported from RI's `WorldPickerSizePatch`; see [KI#1082](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1082).
  - The hook is RI's: the globe's size is a call argument of the shared function at `0x004D2FE0` (Steam; GOG `0x004D2B90`), not an immediate, so its first 7 bytes, `PUSH -1` and `PUSH offset` of the SEH handler, become a `JMP` to a 64-byte cave from `VirtualAlloc`. The cave overwrites the width and height arguments at `[ESP+8]` and `[ESP+0Ch]`, replays the two pushes and jumps back to entry + 7.
  - Only the cave's content differs: RI multiplies the arguments by one fixed factor per font setting, while ours writes sizes that `sasSetupScreenGetSize` computes from the box each time it runs: `box size * PCT / 100 + ADD` per side; 0 leaves the argument alone, which also covers the time before the box is first sized.
  - Hooked only when the box patch was applied. Tested on Steam on 2026-11-12 at 1920 x 1080, 2560 x 1380 and 4K, on every setup step that shows the globe.
  - The globe's area is a rounded rectangle with its own starfield, centred in the step's black panel; Great_Plains' flat picture fills it entirely, so it is the check for overflow. A globe taller than a panel is clipped at the panel's frame, not drawn over it. Sizing and measurements are in [KI#1082](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1082).

## Realism Invictus patch map

Checked on 2026-11-12 against RI r5655 and our Steam EXE. The site list is `Downloads/AdvCiv-SAS_LLM/exe_analysis/ri_v2_sites.tsv`, and the Ghidra description of every site is `ri_v2_sites_described.txt` beside it.

Every Steam address below held the instruction RI's comments describe, so our EXE is the build RI's V2 patches were written for. RI's own reasons come from its comments in `GameCore/CvGameCoreDLL/SelfMod.cpp` and its SVN messages; its full history from r5000 is in `Downloads/AdvCiv-SAS_LLM/svn_history/ri/`.

In the tables, "Steam site checked" gives the address that held the expected instruction in our decrypted EXE. "Found by search" means RI's code looks for a byte pattern instead of using a fixed address; those patches find their site at runtime and were not checked here. "Not checked" means the site was not part of this check.

### UI scaling patches

These are the patches most relevant to our font upscaling: they reach screens and sizes our Python cannot change. RI added most of them between r5616 (2026-08-11, "Implemented font scaling") and r5640.

| Patch | What a player sees without it | Steam site checked |
| --- | --- | --- |
| Pre-game setup window size | Simple Game (BtS's "Play Now"), multiplayer setup and scenario screens all open in the same fixed 850x569 window, too small for larger fonts; RI's comment also names Custom Game, but ours already filled the whole window in a 2026-11-12 capture. RI r5620: "Scaled the main menu as well" | `0x0059B7B0`: `MOV [EAX],0x352` and `MOV [EAX+4],0x239` |
| World-picker globe | the rotating globe on those setup screens stays 450x320; ported in AdvCiv-SAS on 2026-11-12 | `0x004D2FE0`, the shared function RI hooks |
| Diplomacy screen rescale | the diplomacy screen is laid out on a fixed 1024x768 canvas, whatever the resolution and font (RI r5627) | found by search |
| Popup header font | every popup title is forced to `<font=4>`, so at large fonts titles become huge | `0x00C460B4`, the template text, once in the EXE |
| Popup content reserve | popups with a title but no body, such as production or tech choices, get a fixed empty 200px band under the title | `0x007C40A9`: `MOV EAX,0xC8` |
| Popup right margin | popups widened for larger fonts stick out past the right edge of the screen | `0x0057C9EB`: `SUB EAX,0x14` |
| Popup header and body wrap | the text is measured at the old narrow width, leaving a gap under it | `0x00578136`, in the popup text function |
| Tooltip maximum width | hover tooltips are capped at 260px wide, too narrow even at normal font (RI r5617) | `0x00616167`: `PUSH 0x104` |
| Table row height | the engine's own `setTableRowHeight` ignores the height it is given, so table rows stay 24px at any font size (RI r5616) | `0x004EA650` and the table lookup `0x00575660` |
| Plot help width | the unit list at the lower left is narrow; AdvCiv already patches it in our `SelfMod.cpp` (`advc.092c`) | already ours |
| Gamefont metrics, billboards and map signs | game-font icons, the name bars over cities with their icon row and size number, and map signs keep their normal size when fonts grow (RI r5640) | found by search |
| Message bullet | the bullet before on-screen messages is a gamefont character that does not scale (RI r5619) | found by search |

### Graphics and animation fixes

| Patch | What a player sees without it | Steam site checked |
| --- | --- | --- |
| Air mission animations | when ground units intercept air units, the animation shows wrong or blinking figures; four patches restore it (RI r5578: "disassembling the .exe and patching faulty code at runtime") | `0x004040DD`, `0x00403FF1`, `0x004032C4`, `0x00404094` |
| Bystander reaction | ground units react to an air-to-air battle as if attacked | none: RI gives only a V1 site |
| Camera distance | with map centering, the camera cannot zoom out far enough | `0x0042A910` |
| Building render layer and city bucket | the parts of buildings below water level are hidden instead of showing through the water | not checked |
| Pedia coastal model order | in the Sevopedia, coastal units and buildings are drawn in the wrong order against their backdrop | not checked |
| Wall outline smoothing | round cities get staircase-shaped walls | `0x004CBE04`; RI says its second wall site's Steam address was computed, not checked against a Steam EXE |
| Aqueduct same area | a city's aqueduct can be drawn to a lake, peak or hill across water | `0x0041A48A` |
| Farm growth | farm crops grow in the same patterns, and a farm cannot start small and fill its plot | `0x00492506` |
| Bridge art | the engine knows only two bridge models, so most routes share them (RI r5591) | `0x005F934D` |
| Flag art | flags use the engine's three fixed era keys; RI makes them adjustable, including for its war flag widget | `0x00601EEC`, the medieval flag key, which RI also uses to tell V1 from V2 |

### Rendering hooks

These replace functions of the graphics interface (Direct3D 9) while the game runs, rather than changing a few bytes; RI's `DISABLE_D3D9_RENDER_HOOKS` turns them off separately.

| Patch | What it adds |
| --- | --- |
| Texture sharpness | mipmap bias and anisotropic filtering settings the game's options lack: sharper textures, especially the flag next to End Turn (RI r5594) |
| Border dots | a second colour and dotted styles for civilization borders (RI r5595) |
| Frame limiter | caps the frame rate, so static screens like Dawn of Man no longer render thousands of frames per second and make some graphics cards whine (RI r5635) |

### Window and input

| Patch | What it adds |
| --- | --- |
| WASD scrolling | the map scrolls with W, A, S and D like the arrow keys (RI r5596); RI's `DISABLE_WASD_WINDOW_SUBCLASS` turns it off |
| Turn log placement | the Ctrl+Tab event log keeps its size and position across restarts; Steam sites `0x00791348` and `0x0050BB43` checked |

### Can we trust RI's GOG addresses

We have only the Steam EXE, so we cannot check GOG (V1) addresses ourselves. Three things make porting them reasonable anyway:

- RI's comments mark many sites "Ghidra-verified in both", and V1 is RI's main variant: most comments name the V1 address first.
- Every RI patch compares the bytes at its site with what it expects before writing, and skips the patch if they differ. A wrong address therefore costs a missing feature, not a crash.
- RI is open about its gaps, such as the wall site computed but not checked on Steam. Its comments can lag behind its code, though: the tooltip comment still says "V1 (GoG 3.19) address only" while the code also lists the Steam address. Trust the code and its byte checks over the comments.

So: port both variants with their byte checks, test Steam ourselves, and ask a GOG player to confirm.

### Lessons from RI's history

- RI r5588 (2026-05-03) made its memory patches work on both Steam and non-Steam EXEs, and r5625 added a switch to disable them all. Keep such a switch for ours: when a patch misbehaves on one computer, players and we can tell quickly whether it is the cause.
- RI r5645 (2026-10-19) went back to gamefont text for city billboards: with the interface font, an EXE bug degraded performance badly whenever the game regained focus in fullscreen. A patch can work and still expose another engine weakness, so test fullscreen and alt-tab too.
- RI r5587 credits f1rpo and sqwishy for the plot help width addresses, which AdvCiv's `advc.092c` already patches in our `SelfMod.cpp`.

### Lessons from our own setup

What tripped us up on 2026-11-12 while preparing this guide; none of it is new to RI or other EXE modders.

- The Steam EXE's code is encrypted on disk, which RI's V2 addresses already assume; reading the file first gave us other bytes than RI's comments expected. Reading it from memory after Steam's wrapper decrypts it fixed that: check a patch site in the decrypted copy, never in the file.
- Ghidra stopped with `The data file must be inside the data dir` when an agent started it from the Claude desktop app, a packaged Windows app that redirects writes under `AppData`. Running outside the agent's sandbox did not help; moving Ghidra's settings to `C:\Tools\ghidra_user` did, through `-Dapplication.settingsdir` and `-Dapplication.cachedir` lines in `launch.properties`.
- Ghidra 12.2 needs Java 25, while an older Java 21 came first on PATH, so the helpers set `JAVA_HOME` themselves.
- `analyzeHeadless.bat` cannot take a path containing `(x86)` or `Sid Meier's`, which our repository path has, so `describe_exe_sites.py` copies its Ghidra script to a temporary folder first.

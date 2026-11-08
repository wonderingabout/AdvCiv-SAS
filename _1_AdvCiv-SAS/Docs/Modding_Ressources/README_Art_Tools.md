# AdvCiv-SAS Art Tools Guide

How an AI/LLM helper can look at Civ4's art (`.dds` buttons and textures, `.tga` fonts, `.nif` models and scenes, `.bik` movies and packed `.FPK` archives), and how the user and agents edit the game font.

## Menu

- [Why agents need helpers](#why-agents-need-helpers)
- [Images: buttons and textures](#images-buttons-and-textures)
  - [Converting a file](#converting-a-file)
  - [Button strings and atlases](#button-strings-and-atlases)
  - [Comparing art side by side](#comparing-art-side-by-side)
- [Packed .FPK archives](#packed-fpk-archives)
- [.nif models](#nif-models)
- [Scenes and movies](#scenes-and-movies)
- [Example: Peat Works' art](#example-peat-works-art)
- [Game font glyphs](#game-font-glyphs)
  - [What the game font holds](#what-the-game-font-holds)
  - [Editing with Game Font Editor](#editing-with-game-font-editor)
  - [Editing as an agent](#editing-as-an-agent)
  - [Glyph grid](#glyph-grid)
  - [Font commands](#font-commands)
  - [Example: Camel, Peat and Hit Movies in BonusInfo order](#example-camel-peat-and-hit-movies-in-bonusinfo-order)
- [Cautions](#cautions)

## Why agents need helpers

An agent's image reader shows PNG and JPG files to the model as pictures, but none of Civ4's own formats. A script can still read those files as data, and save what they show as a PNG that the image reader can then display; that is all the helpers below do.

They use Pillow (images), numpy, PyFFI (models) and setuptools, installed on 2026-11-08 (`py -m pip install pillow numpy pyffi setuptools`), and ffmpeg for movies; see [Tools for AI/LLM helpers](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README.md#tools-for-aillm-helpers). The font helper needs none of them.

## Images: buttons and textures

### Converting a file

One button, enlarged, as a PNG:

```bash
python -c "from PIL import Image; im = Image.open('Assets/Art/AdvCiv_SAS/Bonuses/Peat/Peat_button.dds'); im.resize((256, 256)).save('peat_button.png')"
```

Buttons are 64 x 64, so enlarging them makes details visible; event pictures and textures are larger.

### Button strings and atlases

An XML `<Button>` is either a plain path, such as `Art/AdvCiv_SAS/Bonuses/Peat/Peat_button.dds`, or an atlas reference: `,Art/Interface/Buttons/Builds/BuildQuarry.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,2,9` names a standalone file, then an atlas of 64-pixel buttons, then a column and row in it.

The column and row count from 1. On 2026-11-08, cell 2,9 of that atlas matched BtS's standalone `BuildQuarry.dds` more closely than any other cell.

### Comparing art side by side

[`art_preview.py`](/LLM_Helpers/README.md#art_previewpy) puts several images in one labelled PNG. It accepts file paths or `<Button>` strings, and for an atlas string uses the standalone file if found, else cuts the cell out of the atlas.

It searches like the game, ignoring case: the mod, then BtS, Warlords and the original game, loose files before their `.FPK` archives, and finally the extracted Caveman2Cosmos, History Rewritten and Realism Invictus folders in the [local LLM working folder](/AGENTS.md#local-llm-working-folder).

```bash
python LLM_Helpers/art_preview.py art/craft/art/peatgatherer.dds ",Art/Interface/Buttons/Builds/BuildQuarry.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,2,9" --out compare.png
```

## Packed .FPK archives

BtS's own art is packed in `.FPK` archives: `Assets/Art0.FPK` under the Civ4 install holds the base game's buttons, atlases and models, and the `Beyond the Sword/Assets/STArt*.FPK` files hold the Final Frontier scenario's. Other mods ship their art the same way.

PakBuild and Dragon UnPACKer, both installed, extract them, but only through their windows. On 2026-11-08 the format proved simple enough to read directly:

- a 4-byte version, `FPK_`, one flag byte and the file count;
- per file: the name's length, the name with every byte shifted by +1, padding to 4 bytes, an 8-byte timestamp, the size and the offset;
- the files themselves, stored as they are.

On `Art0.FPK` (7583 files) and `STArt3.FPK` (802), every offset starts at a valid file header and the last file ends at the end of the archive. [`fpk_tool.py`](/LLM_Helpers/README.md#fpk_toolpy) lists and extracts files by pattern:

```bash
python LLM_Helpers/fpk_tool.py list "../../../Assets/Art0.FPK" "*atlas*"
```

```bash
python LLM_Helpers/fpk_tool.py extract "../../../Assets/Art0.FPK" bts_quarry "art/structures/improvements/quarry/*"
```

SAS ships one archive, `Assets/BML.fpk`, with 37 terrain, route and building textures: [its listing](/_1_AdvCiv-SAS/Docs/examples/fpk/fpk_tool_list_example.txt), and [the `art/terrain/routes/roads/` folder extracted from it](/_1_AdvCiv-SAS/Docs/examples/fpk/fpk_tool_extract_example/), kept out of player downloads since players already have it inside the archive.

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_fpk_extracted_road.PNG" alt="llm_fpk_extracted_road.PNG" width="250">

Extraction keeps the archive's folders, so an extracted model still finds its textures beside it; the Quarry render below came from those 21 extracted files. `art_preview.py` reads packed files directly without extracting them.

The already extracted mods in the local LLM working folder stay convenient for searching with grep, but they are no longer the only way to look inside a mod's art: any `.FPK` can now be listed, read or extracted on demand.

Checking the atlas numbering, with every file read straight from `Art0.FPK`: BtS's button atlas with cell 2,9 marked, that cell cut out, and BtS's standalone Quarry button.

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_fpk_atlas_cell_check.PNG" alt="llm_fpk_atlas_cell_check.PNG" width="250">

## .nif models

[NifSkope](https://github.com/niftools/nifskope) (2.0.dev7, BSD-licensed, kept by the user at `C:\Users\PC\Downloads\old\NifSkope_2_0_2018-02-22-x64 (4)\NifSkope_2_0_2018-02-22-x64\NifSkope.exe`) shows a model only in its window. [`nif_preview.py`](/LLM_Helpers/README.md#nif_previewpy) draws a still picture in the spirit of its view instead:

- PyFFI reads the model; skinned meshes, such as a unit's body, are posed by their bones;
- numpy fills every pixel from its texture, with a depth buffer, simple lighting and each shape's own transparency settings;
- a floor grid sits under the model, and `--yaw` and `--pitch` turn the camera.

```bash
python LLM_Helpers/nif_preview.py Assets/Art/AdvCiv_SAS/Units/Persia_Immortal/nif/persianimmortalarmoreddark.nif immortal.png --yaw 0 --pitch 15
```

Compared with NifSkope on the same Persian Immortal, from the user's screenshot:

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_nif_preview_vs_nifskope.PNG" alt="llm_nif_preview_vs_nifskope.PNG" width="250">

It took several steps, each found from a render that looked wrong:

1. The first version filled each triangle with one colour from its texture: shapes were clear, textures were not.
2. Per-pixel texturing with a depth buffer made the Immortal look like NifSkope's, but only after posing its skinned body by hand. PyFFI's own `get_skin_deformation` stopped with "cannot find a chain of NiAVObject blocks between BIP R Thigh and MD NonAccum", so each vertex is now moved by its bones' places in the scene, weighted.
3. The Peat bonus then showed its peat clumps but not the green ground around them: every texel under half alpha had been cut, while its decal blends and tests against a threshold of 1. Each shape's `NiAlphaProperty` is now followed, and `NiTriStrips` parts are drawn too.
4. Untextured shapes are skipped unless `--untextured` is given: they are usually hidden helpers, such as the Peat bonus's two grey "Sphere" shapes, which the first render showed as pyramids.

Limits: it shows a model in its stored pose, without the game's animations, effects, lighting or team colours.

PyFFI 2.2.3 needs two small fixes on current Python, both handled by the helper: setuptools for `distutils`, and `time.clock`, which the helper restores before importing it. For a model inside an `.FPK`, extract its folder first with `fpk_tool.py`, since a model finds its textures by name beside it.

## Scenes and movies

Agents cannot watch a video or hear sound; they see still images only. Civ4's "movies" come in two kinds, and both can still be turned into images.

**Religion-founding scenes are `.nif` files** with their own camera, lights, particle effects and keyframed animation, such as BtS's `Assets/Art/Movies/Religion/Taoism/Tao_Found.nif`. `nif_preview.py --scene-camera` looks through that camera, and `--frames N` draws N moments of the animation side by side:

```bash
python LLM_Helpers/nif_preview.py "../../../Assets/Art/Movies/Religion/Taoism/Tao_Found.nif" daoism.png --scene-camera --frames 4 --size 320
```

- Keyframes are interpolated linearly, with rotations by slerp; the files' smoother TBC and Bezier curves are not followed, which matters little for stills.
- Such scenes bake their lighting into textures, so they are drawn without the preview's own shading.
- Particle effects, such as the candle flame, are not drawn.

Compared with the user's in-game screenshot of the Daoism movie, then four moments of its 5-second camera move:

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_nif_scene_vs_game_daoism.PNG" alt="llm_nif_scene_vs_game_daoism.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/llm_nif_scene_frames_daoism.PNG" alt="llm_nif_scene_frames_daoism.PNG" width="250">

**Wonder movies are Bink videos (`.bik`)**, such as SAS's Natya Shastra movie. ffmpeg decodes them; it was already installed through winget (`winget install Gyan.FFmpeg`). [`movie_frames.py`](/LLM_Helpers/README.md#movie_framespy) takes evenly spaced frames into one sheet, and with `--audio` draws the sound as a waveform and prints its mean and peak loudness:

```bash
python LLM_Helpers/movie_frames.py Assets/Art/AdvCiv_SAS/Buildings/Natya_Shastra/movie/Meenakshi.bik natya.png --frames 6 --width 240 --audio natya_audio.png
```

For the Natya Shastra movie (31 seconds) it showed the Meenakshi temple's towers, carved deities and pillared hall, and music building from a quiet start to louder passages near the end (mean -19.5 dB, peak -0.9 dB). A waveform shows loudness over time, not what the sound is.

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_movie_frames_natya_shastra.PNG" alt="llm_movie_frames_natya_shastra.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/llm_movie_audio_natya_shastra.PNG" alt="llm_movie_audio_natya_shastra.PNG" width="250">

The same helper reads the original Civ IV Great Library wonder movie and Conquest victory movie. Their paths are listed in [CIV4ArtDefines_Movie.xml](/Assets/XML/Art/CIV4ArtDefines_Movie.xml). From the mod root in the standard BtS install layout, `../../../Assets` points to the original Civ IV assets.

```bash
python LLM_Helpers/movie_frames.py "../../../Assets/Art/Movies/Wonders/GreatLibrary.bik" great_library.png --frames 4 --width 200 --audio great_library_audio.png
python LLM_Helpers/movie_frames.py "../../../Assets/Art/Movies/Victory/Conquest.bik" conquest.png --frames 4 --width 200 --audio conquest_audio.png
```

**Great Library (21.7 seconds).** The architectural drawing gives way to the library under construction and then the finished building.

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_movie_frames_great_library.PNG" alt="llm_movie_frames_great_library.PNG" width="600">

**Conquest victory (31.4 seconds).** The movie cuts between a chessboard and a city under attack, then returns to the board as the white king falls.

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_movie_frames_conquest.PNG" alt="llm_movie_frames_conquest.PNG" width="600">

**External model animations.** A `.kfm` lists the model and maps event codes to `.kf` clips. Pass the KFM without an output path to list its events, then add `--clip` to inspect one. You can also inspect a KF directly, or render it by passing its NIF with `--kf path/to/clip.kf`.

```bash
python LLM_Helpers/nif_preview.py Assets/Art/AdvCiv_SAS/Improvements/Peat_Works/nif/camp.kfm
python LLM_Helpers/nif_preview.py Assets/Art/AdvCiv_SAS/Improvements/Peat_Works/nif/camp.kfm --clip 2
python LLM_Helpers/nif_preview.py Assets/Art/AdvCiv_SAS/Improvements/Peat_Works/nif/camp.kfm --clip 3
python LLM_Helpers/nif_preview.py Assets/Art/AdvCiv_SAS/Units/Incan_Llama_Kamayuq/nif/llamaarcher.kfm llama_run.png --clip 1010 --size 200
```

Peat Works' `not_worked` clip (event 2) hides `NodeFXCampfire` and its `worked` clip (event 3) shows it. The preview reports the switch. Fire and smoke particles are outside the renderer's scope. The Llama Kamayuq's run clip exercises bone transforms and gives four different moments of the stride, with the first pose repeating at the loop boundary.

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_kf_frames_llama_run.PNG" alt="llm_kf_frames_llama_run.PNG" width="600">

The renderer applies ordinary transform and visibility tracks by node name. It reports unsupported tracks, including the compressed spline tracks found in some leaderheads, Euler rotation channels and material animation.

Use `--model` to select an alternate NIF when the in-game art definition uses a variant such as `camp_fx.nif`. The preview samples individual clips. Game-driven transitions and effects need an in-game check.

**SAS Holy Roman Houfnice.** Its ranged-strike event is listed under the raw code `32113672`. The supported tracks show the crew's movement. The sheet is a partial preview because the renderer skips compressed transforms and material tracks.

```bash
python LLM_Helpers/nif_preview.py Assets/Art/AdvCiv_SAS/Units/Holy_Roman_Houfnice/nif/cannon.kfm houfnice.png --clip 32113672 --size 200
```

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_kf_frames_houfnice_strike.PNG" alt="llm_kf_frames_houfnice_strike.PNG" width="600">

**Original Civ IV Catapult.** Extract the unit's folder from the original game's `Art0.FPK`. With the textured FX model selected, the ranged-strike preview shows the arm swing and the rock disappear from the sling.

```bash
python LLM_Helpers/fpk_tool.py extract "../../../Assets/Art0.FPK" catapult_assets "art/units/catapult/*"
python LLM_Helpers/nif_preview.py catapult_assets/art/units/catapult/catapult.kfm catapult.png --clip 1032 --model catapult_assets/art/units/catapult/catapult_fx.nif --size 200
```

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_kf_frames_catapult_strike.PNG" alt="llm_kf_frames_catapult_strike.PNG" width="600">

**Standalone sound.** Use `--audio-only` on an MP3 or WAV to draw its waveform and report mean and peak volume in dBFS.

```bash
python LLM_Helpers/movie_frames.py Assets/Art/AdvCiv_SAS/Main_Menu/music/lofi-song-330550.mp3 menu_audio.png --audio-only
```

The menu track's two stereo channels taper at the beginning and end. FFmpeg reports a mean of −15.9 dBFS and a peak of 0.0 dBFS.

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_audio_waveform_menu_lofi.PNG" alt="llm_audio_waveform_menu_lofi.PNG" width="600">

## Example: Peat Works' art

The new Peat Works first shipped with Quarry's button and model as placeholders. The guide said so, but the change was still called ready to test, and the user noticed it in the Sevopedia, where Peat Works and Quarry looked the same.

1. **Buttons.** With Pillow, the agent compared the peat art in the extracted Caveman2Cosmos files: its peat gatherer building's cut peat blocks, its peat dynamo, its Peat trade good, the stone-tools button its own Peat Cutter improvement uses, and SAS's Peat bonus.
   - The cut peat blocks were distinct from the Peat bonus and fit an improvement where peat is cut, so Peat Works and its build use them now.
   - The user, browsing C2C's own Sevopedia meanwhile, had picked the same one.
2. **Model textures.** C2C's Peat Cutter uses a camp model, `art/structures/improvements/rockgatherer/camp_fx.nif`. Before any model renderer existed, its textures were the only view of it: a wooden hut wall, hides, a ground decal, a fire and smoke.
3. **Model render.** Once `fpk_tool.py` and `nif_preview.py` existed, BtS's Quarry from `Art0.FPK`, the camp and the Peat bonus could be drawn side by side. The camp turned out to be a plank hut, a hide shelter on poles, a fire and scattered tools: no peat-specific model, but a rural camp rather than a quarry crane.

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_peat_works_button_candidates.PNG" alt="llm_peat_works_button_candidates.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/llm_peat_works_camp_textures.PNG" alt="llm_peat_works_camp_textures.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/llm_peat_works_nif_renders.PNG" alt="llm_peat_works_nif_renders.PNG" width="250">

The same miss led to [`plot_asset_buttons.py`](/.github/workflows/README.md#buildxmlplot_asset_buttonspy), which fails when a feature, bonus, improvement, route or build borrows another one's button.

## Game font glyphs

### What the game font holds

[`GameFont.tga`](/Assets/Res/Fonts/GameFont.tga) and [`GameFont_75.tga`](/Assets/Res/Fonts/GameFont_75.tga) hold the small icons the game shows inside text: yields, commerce, religions, corporations, bonuses and other symbols. `GameFont_75.tga` is a smaller copy of the same layout, so both must change together.

A bonus's icon is the glyph at its `<FontButtonIndex>` in [`CIV4ArtDefines_Bonus.xml`](/Assets/XML/Art/CIV4ArtDefines_Bonus.xml), counted across the bonus rows, not its place in [`CIV4BonusInfos.xml`](/Assets/XML/Terrain/CIV4BonusInfos.xml). Moving a bonus glyph therefore means changing its `FontButtonIndex` in the same change, or two bonuses show each other's icons.

SAS still keeps all three in one order, which [`bonus_font_order.py`](/.github/workflows/README.md#buildxmlbonus_font_orderpy) checks.

Religions and corporations are different: the DLL gives them their icons in XML order, which is why [`xml_display_order.py`](/.github/workflows/README.md#buildxmlxml_display_orderpy) checks their order.

### Editing with Game Font Editor

The user edits the fonts with [Game Font Editor (v0.6) for Civ4](https://forums.civfanatics.com/resources/game-font-editor-v0-6-for-civ-4.17276/) by Asaf, listed in [README_References.md](/_1_AdvCiv-SAS/Docs/README_References.md). It shows the glyph grid, imports and exports single glyphs as images, and computes their alpha.

Its screenshots of both fonts are kept beside them, as `advciv-sas_gamefont_tga.PNG` and `advciv-sas_gamefont_75_tga.PNG`, with other mods' fonts as PNG previews in `Assets/Res/Fonts/other_mods/`.

### Editing as an agent

A screenshot of the whole font is too small to tell one glyph from another, and moving a glyph needs the grid. [`gamefont_tga.py`](/LLM_Helpers/README.md#gamefont_tgapy) does both with only Python's standard library: it reads the TGA pixels itself, writes a chosen region enlarged as a PNG, and copies glyph cells between slots.

It was written on 2026-11-07, before Pillow was installed, and confirmed Peat's glyph in the user's edit; on 2026-11-08 it moved three glyphs in both fonts.

Game Font Editor writes uncompressed 32-bit TGA (image type 2, no ID field or color map), with rows stored bottom-up and pixels as blue, green, red, alpha. The helper refuses any other kind, rather than guess. Magenta (255, 0, 255) draws the grid between glyphs and fills unused space.

### Glyph grid

Glyphs sit in rows of 25 cells between magenta grid lines. A bonus's `FontButtonIndex` counts from the first cell of the first bonus row: slot 32 is the 8th cell of the second bonus row.

As of 2026-11-08 the two SAS fonts measure as follows, with rows given as the grid line above each row, counted from the top:

| Font | Size | Bonus row tops | Row height | Column pitch |
| --- | --- | --- | --- | --- |
| `GameFont.tga` | 640 x 320 | 176, 197 | 21 | 22 |
| `GameFont_75.tga` | 512 x 256 | 140, 157 | 17 | 17 |

These can change when glyph rows are added, so measure them again with `grid` rather than trusting the table:

- `grid` without `--band` lists the horizontal lines; the gaps between them give the row tops and height.
- `grid --band` lists the complete vertical lines between two horizontal ones. Glyphs can cover parts of a line, so only empty cells show complete lines; the column pitch is the gap between them.
  - The first measurement, which expected every cell to show its lines, found only the empty ones, which is how this was noticed.
- Row height and column pitch are separate: they differ in `GameFont.tga` but are both 17 in `GameFont_75.tga`.
  - The first draft derived the pitch as row height + 1, which fit the full-size font but picked the wrong cells in the 75% one. Its enlarged preview showed this before any font was replaced, so always preview a `move` result first.

### Font commands

Run from the mod root:

```bash
python LLM_Helpers/gamefont_tga.py grid Assets/Res/Fonts/GameFont.tga
```

```bash
python LLM_Helpers/gamefont_tga.py grid Assets/Res/Fonts/GameFont.tga --band 197 218
```

```bash
python LLM_Helpers/gamefont_tga.py preview Assets/Res/Fonts/GameFont.tga bonus_rows.png --box 0 175 560 222 --zoom 3
```

`move` copies cells, reading every source before writing, so swaps work. `--set 33=32` puts slot 32's glyph into slot 33, and `--set 34=OTHER.tga:34` takes a glyph from another font of the same size. Write to a new file with `--out`, preview it, and only then replace the font.

### Example: Camel, Peat and Hit Movies in BonusInfo order

BtS ended its bonus list with three Hit bonuses. SAS replaced two of them with Camel and Peat, and one remains disabled, following the BonusInfo file's warning against removing bonuses. On 2026-11-08 the XML was put in that order: Camel, Peat, then Hit Movies.

The glyphs were still in the old order, Peat 32, Hit Singles 33 and Camel 34, so the fonts were changed to match, with the original Hit Movies glyph taken from base AdvCiv's font:

```bash
python LLM_Helpers/gamefont_tga.py move Assets/Res/Fonts/GameFont.tga --row-tops 176 197 --row-height 21 --col-pitch 22 --set 32=34 --set 33=32 --set "34=../AdvCiv/Assets/res/Fonts/GameFont.tga:34" --out GameFont_new.tga
```

```bash
python LLM_Helpers/gamefont_tga.py move Assets/Res/Fonts/GameFont_75.tga --row-tops 140 157 --row-height 17 --col-pitch 17 --set 32=34 --set 33=32 --set "34=../AdvCiv/Assets/res/Fonts/GameFont_75.tga:34" --out GameFont_75_new.tga
```

- After checking enlarged previews of both results, they replaced the fonts, and `FontButtonIndex` became 32 for Camel, 33 for Peat and 34 for Hit Movies.
- The user confirmed the result in Game Font Editor and refreshed its screenshots.
- Rerunning these commands on the user's previous fonts reproduces the installed files byte for byte.

Enlarged previews of the bonus rows, made with `preview` by Claude Code Opus 5.5: the full-size font before and after, then the 75% font after.

<img src="/_1_AdvCiv-SAS/Images/LLM/llm_gamefont_tga_preview (1).PNG" alt="llm_gamefont_tga_preview (1).PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/llm_gamefont_tga_preview (2).PNG" alt="llm_gamefont_tga_preview (2).PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/llm_gamefont_tga_preview (3).PNG" alt="llm_gamefont_tga_preview (3).PNG" width="250">

## Cautions

- Change both fonts, and the matching `FontButtonIndex` values, in one change.
- Keep a copy of a file before replacing it; a staged copy in Git's index also works.
- Check results in an enlarged preview, and in the game, which loads art and fonts at startup.
- A `.nif` render shows the model's stored pose only; judge a model in the game before keeping it.

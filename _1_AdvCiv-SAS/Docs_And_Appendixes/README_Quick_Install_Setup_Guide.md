# Install Civilization 4 Beyond the Sword and the AdvCiv-SAS mod

To install and play this mod AdvCiv-SAS, you can follow the steps in this document/readme.

## Install Civilization 4 Beyond the Sword (skip if already done)

First you need to install (or have it installed already) Civilization 4 Beyond the Sword. (skip if already done)

If you don't have the game, i recommend buying it from GOG rather than Steam (i have no affiliation with either xd, although i have the steam version myself for convenience and such, as the executable or whatever they call it is cleaner and closer if not entirely unmodified unlike the Steam one if i am not mistaken, but check to be sure).

It should work fine with the Steam one too, but given the choice again i may have bought it from GOG rather hehe, although it is not certain as Steam one is convenient too for library access of other games or centralized games lbirary for me i mean or such, but i hope this information helps you decide in this case i mean but anyways etc, check if i am not mistaken i mean too or for extra or updated info if any change has been made since maybe.

## Download (or clone / download zip from github if you know how and prefer) this mod AdvCiv-SAS

Then download it from the [CFC Modpacks downloads page (link in intro of main readme)](https://forums.civfanatics.com/resources/advciv-sas-simple-advanced-strategy.32513/) (or clone / download zip from github if you know how as you prefer) this AdvCiv-SAS mod.

## Extract the mod to your civ4 folder

Extract the archive in the Mods folder of your civ4 BTS/BTS folder (be careful twice BTS (i.e. "Beyond The Sword")), for example, using Steam the path of AdvCiv-SAS should be **(remove version name such as "-4986" or any name like "-tech-rework" (git branch name, remove when extracting to your civ4 mods folder)** or similar or anything else xd in your folder destination name so it is **strictly "AdvCiv-SAS"**):

```C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\```

If you don't use Steam you can still play this AdvCiv-SAS mod, you'll just have to change the path to where civ4 was installed (and might have less DRMs at the same time so may be even better as you prefer).

Note: be careful while extracting, a common error (which i made too having no clue why it didn't work...) is to extract with an extra subfolder, then i don't think the game would function. So for example for the steam version of the game, one of the mod files such as AdvCiv-SAS.ini should be found in `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\AdvCiv-SAS.ini` and NOT in `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\AdvCiv-SAS\AdvCiv-SAS.ini` (i.e. don't do this `\AdvCiv-SAS\AdvCiv-SAS\`).

## Place a shortcut of the mod on your desktop

Finally, add a shortcut to your desktop which link is, for example for Steam:

```"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Civ4BeyondSword.exe" mod=\AdvCiv-SAS```

For convenience i have also provided a steam shortcut of this same link just above (since this is the version i have i.e. the steam one of the game anyways etc), ready to use, (AdvCiv-SAS - Steam shortcut.lnk). You can just move (cut then paste, it's just a link so is safe) it to the desktop for your convenience.

Note: you can do this same process (download and install a Civ 4 mod(s), then place a shortcut of it to desktop or wherever you want/prefer if i'm not mistaken but anyways etc) for any number of mods you want, just extract it in same Mods folder but with a different folder name, for example you could play Cavemen2Cosmos, Realism Invictus, even AdvCiv alongside AdvCiv-SAS as long they are in different folders, they are totally indepedent, the settings or files of one will not override or affect the other mods, thanks to the very awesome design of Civ 4, thanks!

## Where to download more/other mods

If you want to try/play other mods than AdvCiv-SAS or browse them (but you may already know if you downloaded this, still, or if not, maybe this can help you too), consider visiting, among other possible sources/websites:

- CivFanatics Center (also known as CFC) 's forums -> Civ 4 forum -> Modpacks forum (is a forum of a forum called a forum(?)): [civfanatics website civ4 modpacks forum](https://forums.civfanatics.com/forums/civ4-modpacks.171/)
- ModDB (but does not have as much mods i think, AdvCiv (base mod) is not listed for example (which is the most interesting of the AdvCiv mods i think, except my awesome (xd but anyways etc) mod maybe as interesting maybe as AdvCiv, but i hope i can contribute there maybe)): [ModDB website](https://www.moddb.com/games/civilization-iv/mods)

But i say it just for exhaustiveness, even though i am (quite) friendly i think, i prefer to stay alone and relax and do my own things, so i might get stressed if you contact me.. Still, if this project would help you reader or even those who don't read, i may be quite happy of it, especially as i contribute(d) to it

## Configure your game

Recommended, change your config as you prefer. For example as for me, i play at 1920x1080 (seems to display best ingame, even though i have a larger screen actually (4K but anyways etc) i also optimized sevopedia features like the AI personality panel for 1920x1080 (but may work as well for higher resolutions although i didn't test it but anyways etc)) in full screen, but when i need to debug or test the windowed mode is so much more practical.

There are some options i use personally xd but anyways etc in ingame settings then like if i'm not mistaken (from memory since i can't find the txt files where i stored it if i ever did (which i think i did but anyways etc)), so do as you prefer, but as for me i use these civ4 options for example if not already enabled before anyways etc (non-exhaustive in case i forgot / didn't show some anyways etc):

- wait at end of turn
- quick attack
- quick defense
- quick moves
- single unit graphics
- numbers on city bar

Then in BUG Menu options i also use this for example hehe but do as you prefer as well anyways etc (non-exhaustive in case i forgot / didn't show some anyways etc):

- wide city bars

## Settings if you want to develop/modify the mod or try some autoplay or such anyways etc (skip this section if only playing without wanting extra details)

(skip this section if only playing without wanting extra details)

If you're developping a mod, or simply want to run some autoplays or such yourself, you'd most like want to enable debug mode (it allows, after enabled, to be able to reveal all map by toggling ctrl+z ingame, as well as do autoplay runs yourself with ctrl+shift+x for example if i'm not mistaken anyways etc). To enable debug mode, if i'm not mistaken you need to set `cheatcode = chipotle` in `C:\Users\PC\Documents\My Games\beyond the sword\CivilizationIV.ini` (note: `PC` is my windows username account, adapt it to your own windows username account or/and wherever your CivilizationIV.ini file or such config file is anyways etc).

Also, if you're developping/modding or doing autoplays or such, i highly recommend "windowed" rather than fullscreen (`fullscreen = 0` in same CivilizationIV.ini file (or maybe in ingame settings although i didn't test it but anyways etc)), as this is so much more convenient to do screenshots and browse them, go back and forth to your windows folders without having a lag of several seconds everytime you click outside of the game, etc. Otherwise fullscreen is nice for playing i think and much more immersive at least i'd prefer it i think, but fullscreen is way too tedious when modding and testing etc.

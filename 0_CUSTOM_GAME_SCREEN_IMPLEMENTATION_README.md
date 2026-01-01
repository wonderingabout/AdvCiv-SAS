# Custom Game Screen Implementation - Complete Guide

## Overview

This implementation adds a custom popup screen that appears when you click "Custom Game" from the main menu. The popup shows on top of the original BTS custom game screen and allows you to select game settings (starting with game speed) in a cleaner, more modern interface.

**Based on:** [CivFanatics CuCuGS Proof-of-Concept by f1rpo](https://forums.civfanatics.com/threads/replacing-the-custom-game-screen-proof-of-concept.670307/)

**Implementation Date:** 2025-12-31

**Status:** ✅ **COMPLETE** - Ready for compilation and testing

## What This Does

- Shows a blue popup panel over the original custom game screen
- Provides a game speed dropdown selector with helpful tooltips
- Three buttons:
  - **LAUNCH!** - Starts the game with selected settings
  - **GO BACK** - Returns to main menu
  - **USE ORIGINAL SCREEN** - Closes popup to use BTS original screen
- Works seamlessly with existing BTS custom game functionality
- Can be expanded to include all game options (map size, leaders, etc.)

## Implementation Summary

### Part 1: DLL Changes (C++)
**Document:** [1_IMPLEMENTATION_PART1_DLL_CHANGES_COMPLETE.md](1_IMPLEMENTATION_PART1_DLL_CHANGES_COMPLETE.md)

**Files Created (2):**
- `CvGameCoreDLL/InputSim.h` - Keyboard/mouse input simulation header
- `CvGameCoreDLL/InputSim.cpp` - Input simulation implementation

**Files Modified (6):**
- `CvGameCoreDLL/CvDLLWidgetData.cpp` - Screen ID 33 handling + widget help
- `CvGameCoreDLL/CvEnums.h` - WIDGET_HELP_GAME_SPEED enum
- `CvGameCoreDLL/CvGameTextMgr.h` - setGameSpeedHelp() declaration
- `CvGameCoreDLL/CvGameTextMgr.cpp` - setGameSpeedHelp() implementation
- `CvGameCoreDLL/CyEnumsInterface.cpp` - Python binding for widget
- `CvGameCoreDLL/Project/AdvCiv.vcxproj` - Project file updated

**Total:** 8 files

### Part 2: Python Integration
**Document:** [2_IMPLEMENTATION_PART2_PYTHON_INTEGRATION_COMPLETE.md](2_IMPLEMENTATION_PART2_PYTHON_INTEGRATION_COMPLETE.md)

**Files Created (2):**
- `Assets/Python/Screens/GenericDecoratedScreen.py` - Base class for decorated screens
- `Assets/Python/Screens/CustomGameScreen.py` - The actual custom game popup

**Files Modified (3):**
- `Assets/Python/Screens/CvScreenEnums.py` - Added CUSTOM_GAME_SCREEN = 33
- `Assets/Python/EntryPoints/CvScreensInterface.py` - Screen integration
- `Assets/XML/Text/CIV4GameTextInfos_Custom.xml` - Text key for button

**Total:** 5 files

### Grand Total: 13 files (4 created, 9 modified)

## How to Compile and Test

### Step 1: Compile the DLL

1. Open Visual Studio 2010 Express
2. Load `CvGameCoreDLL/Project/AdvCiv.sln`
3. Select **Release** configuration (not Debug)
4. Press **F7** or click **Build → Build Solution**
5. Wait for compilation to complete (should succeed with 0 errors)
6. Copy the compiled DLL:
   ```
   FROM: CvGameCoreDLL/Project/Release/CvGameCoreDLL.dll
   TO:   Assets/CvGameCoreDLL.dll
   ```

### Step 2: Test In-Game

1. Launch **Civilization IV: Beyond the Sword**
2. Click **Advanced → Load a Mod**
3. Select **AdvCiv-SAS** and click **Load**
4. From the main menu, click **Custom Game**
5. **Expected Result:**
   - Original BTS custom game screen appears (grayed out in background)
   - Blue popup panel appears on top immediately
   - Panel shows "CUSTOM GAME" header
   - Game Speed dropdown in center with tooltips
   - Three buttons at bottom: LAUNCH!, GO BACK, USE ORIGINAL SCREEN

### Step 3: Test Functionality

**Test Game Speed Selection:**
1. Click the game speed dropdown
2. Hover over different speeds (Quick, Normal, Epic, Marathon)
3. Verify tooltips show speed descriptions
4. Select a different speed
5. Verify selection is saved

**Test LAUNCH! Button:**
1. Select your preferred game speed
2. Click **LAUNCH!**
3. Verify game starts with selected speed
4. Check in-game that speed matches your selection

**Test GO BACK Button:**
1. Click **Custom Game** again
2. Click **GO BACK**
3. Verify you return to main menu

**Test USE ORIGINAL SCREEN Button:**
1. Click **Custom Game** again
2. Click **USE ORIGINAL SCREEN**
3. Verify popup closes and you can use original BTS screen
4. Original screen should still be functional

## Technical Architecture

### How It Works

```
Main Menu
    │
    ├─ User clicks "Custom Game"
    │
    ↓
BTS Original Custom Game Screen (Background)
    │
    ├─ Python detects screen entry (ID 33)
    │
    ↓
CustomGameScreen.py Popup (Foreground)
    │
    ├─ Shows blue panel with dropdown
    │
    ├─ User selects game speed → Updates gc.getInitCore()
    │
    ├─ User clicks button:
    │   ├─ LAUNCH! (data2=0) → DLL simulates VK_RETURN
    │   ├─ GO BACK (data2=2) → DLL simulates mouse click
    │   └─ USE ORIGINAL SCREEN (data2=-1) → Normal close
    │
    ↓
InputSim (DLL) sends keyboard/mouse events
    │
    ↓
Original BTS Screen receives input
    │
    ↓
Game launches or returns to menu
```

### Key Components

1. **InputSim** (C++): Simulates keyboard/mouse input using Windows SendInput API
2. **WIDGET_CLOSE_SCREEN**: Special widget that triggers screen closure + input simulation
3. **Screen ID 33**: Unique identifier for the custom game screen
4. **GenericDecoratedScreen**: Reusable base class for popup screens with header/footer
5. **CustomGameScreen**: The actual game setup popup implementation

## Code Tagging Convention

All custom code is tagged with `// AdvCiv-SAS - CuCuGS` (C++) or `# AdvCiv-SAS - CuCuGS` (Python) comments for easy identification. Search for "AdvCiv-SAS - CuCuGS" to find all modifications.

## Future Enhancements

The current implementation is a proof-of-concept with just game speed selection. Future versions could add:

### Phase 1 - Basic Options
- [ ] Map size selection
- [ ] Number of civilizations
- [ ] Sea level selection
- [ ] Climate selection
- [ ] World age selection

### Phase 2 - Advanced Options
- [ ] Leader/civilization selection
- [ ] Starting era selection
- [ ] Game options (aggressive AI, no barbarians, etc.)
- [ ] Victory conditions
- [ ] Game pace modifiers

### Phase 3 - Visual Polish
- [ ] Better layout matching Civ3's new game menu
- [ ] Custom graphics and artwork
- [ ] Animated transitions
- [ ] Preview images for maps/leaders
- [ ] Custom fonts and styling

## Troubleshooting

### Problem: Popup doesn't appear
**Solution:** Make sure you compiled and copied the DLL correctly. The DLL changes are required for the popup to work.

### Problem: Buttons don't work
**Solution:** Check that InputSim.cpp and InputSim.h were compiled into the DLL. Verify the project file includes them.

### Problem: Tooltips don't show
**Solution:** Ensure WIDGET_HELP_GAME_SPEED was added to CvEnums.h and exposed in CyEnumsInterface.cpp.

### Problem: Game speed doesn't save
**Solution:** Verify CustomGameScreen.py handleInput() is correctly calling gc.getInitCore().setGameSpeed().

### Problem: Compilation errors
**Solution:**
- Make sure you're using Visual Studio 2010 Express (not newer versions)
- Verify all #include statements are correct
- Check that InputSim namespace is properly defined
- Ensure all `// AdvCiv-SAS - CuCuGS` tagged code was added correctly

## File Locations Quick Reference

### DLL Files
```
CvGameCoreDLL/
├── InputSim.h                    [NEW]
├── InputSim.cpp                  [NEW]
├── CvDLLWidgetData.cpp           [MODIFIED]
├── CvEnums.h                     [MODIFIED]
├── CvGameTextMgr.h               [MODIFIED]
├── CvGameTextMgr.cpp             [MODIFIED]
├── CyEnumsInterface.cpp          [MODIFIED]
└── Project/
    └── AdvCiv.vcxproj            [MODIFIED]
```

### Python Files
```
Assets/Python/
├── Screens/
│   ├── GenericDecoratedScreen.py    [NEW]
│   ├── CustomGameScreen.py          [NEW]
│   └── CvScreenEnums.py             [MODIFIED]
└── EntryPoints/
    └── CvScreensInterface.py        [MODIFIED]
```

### XML Files
```
Assets/XML/Text/
└── CIV4GameTextInfos_Custom.xml     [MODIFIED]
```

## Credits

- **Original Concept:** f1rpo (CivFanatics forum member)
- **Original Proof-of-Concept:** [CuCuGS-PoC](https://forums.civfanatics.com/threads/replacing-the-custom-game-screen-proof-of-concept.670307/)
- **Base Framework:** GenericDecoratedScreen adapted from MNAI's InterfaceUtils.py
- **AdvCiv-SAS Integration:** Claude Code (2025-12-31)

## License

This implementation follows the same license as the AdvCiv mod and is compatible with BTS modding terms.

---

**For detailed technical information, see:**
- [Part 1: DLL Changes](1_IMPLEMENTATION_PART1_DLL_CHANGES_COMPLETE.md)
- [Part 2: Python Integration](2_IMPLEMENTATION_PART2_PYTHON_INTEGRATION_COMPLETE.md)

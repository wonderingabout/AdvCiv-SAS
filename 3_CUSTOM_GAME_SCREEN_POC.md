# Custom Game Screen Popup - Proof of Concept

## Overview

This document describes the implementation of a custom game screen popup for AdvCiv-SAS, based on the CuCuGS (Custom vs Custom Game Screen) proof-of-concept from CivFanatics.

**Current Status**: ✅ WORKING - Basic proof of concept successfully implemented and tested

**Test Screenshots**: Civ4ScreenShot1535.JPG through Civ4ScreenShot1539.JPG demonstrate the working implementation.

## Goal

Replace the default Beyond the Sword "Custom Game" screen with a custom Python-based popup that:
- Displays on top of the original BTS screen
- Allows modification of game settings (currently: game speed)
- Can be extended to show additional settings (sea level, climate, etc.)
- Provides better UI/UX control through Python

## Technical Approach

### Architecture Overview

The implementation uses a two-part system:

1. **DLL (C++) Layer**: Detects when the Custom Game screen is entered and triggers a Python callback
2. **Python Layer**: Displays a custom popup screen with UI controls

### How It Works

#### Screen Detection Mechanism

The key insight is that the Custom Game screen and Play Now screen call `CvInitCore::setVictories()` differently:

- **Custom Game Screen**: Calls `setVictories()` BEFORE and AFTER `setActivePlayer()`
- **Play Now Screen**: Calls `setVictories()` only ONCE after `setActivePlayer()`

We exploit this difference to detect which screen is being entered:

```cpp
// In CvInitCore.h
bool m_bOnCustomGameScreen;  // Toggle flag

// In CvInitCore.cpp
void CvInitCore::setVictories(...)
{
    setVictoriesInternal(...);
    if (iVictories > 0 && getType() == GAME_SP_NEW)
    {
        m_bOnCustomGameScreen = !m_bOnCustomGameScreen;  // Toggle on each call
    }
}

void CvInitCore::setActivePlayer(...)
{
    // ... existing code ...

    // If flag is true, we're on Custom Game screen (two setVictories calls)
    if (getType() == GAME_SP_NEW && m_bOnCustomGameScreen)
    {
        // Trigger Python callback
        gDLL->getPythonIFace()->callFunction(PYScreensModule, "showCustomGameScreen");
    }
}
```

#### Python-C++ Integration

The DLL exposes game initialization functions to Python through a new `CyInitCore` wrapper:

```python
# Python can now access:
gc.getInitCore().getGameSpeed()
gc.getInitCore().setGameSpeed(iSpeed)
```

This allows the Python UI to both read and modify game settings.

## Files Modified/Created

### DLL Files (CvGameCoreDLL/)

#### New Files Created:

1. **CyInitCore.h** / **CyInitCore.cpp**
   - Python wrapper class for CvInitCore
   - Exposes `getGameSpeed()` and `setGameSpeed()` to Python
   - Validates speed values before applying changes

2. **CyInitCoreInterface.cpp**
   - Registers CyInitCore with Boost.Python module system
   - Makes the wrapper accessible from Python code

3. **InputSim.h** / **InputSim.cpp**
   - Windows SendInput API wrappers for keyboard/mouse simulation
   - Used to trigger original screen buttons (Launch, Go Back)
   - Required for proper screen navigation

#### Modified DLL Files:

1. **CvInitCore.h** (lines 111, 348, 410, 419-421)
   - Changed `setGameSpeed()` from inline to DllExport
   - Added `m_bOnCustomGameScreen` member variable
   - Added `setVictoriesInternal()` private method
   - Updated BOOST_STATIC_ASSERT for increased class size (448→452, 424→428)

2. **CvInitCore.cpp** (lines 1-5, 76, 865-869, 1016-1029, 1101-1109)
   - Added include: `CvDLLPythonIFaceBase.h`
   - Initialize `m_bOnCustomGameScreen = false` in constructor
   - Implemented `setGameSpeed()` function (was inline before)
   - Replaced `setVictories()` with wrapper that toggles screen flag
   - Added Python callback trigger in `setActivePlayer()`
   - Added `(void)bSuccess;` to suppress Release build warnings

3. **CyGlobalContext.h** (lines 15, 34)
   - Forward declaration: `class CyInitCore;`
   - Added method: `CyInitCore& getCyInitCore() const;`

4. **CyGlobalContext.cpp** (lines 11, 38-43)
   - Include: `CyInitCore.h`
   - Implementation of `getCyInitCore()` returning static instance

5. **CyGlobalContextInterface1.cpp** (lines 11, 21-22)
   - Include: `CyInitCore.h`
   - Exposed `getInitCore()` to Python with proper return policy

6. **CvDLLPython.cpp** (lines 33, 57)
   - Forward declaration: `void CyInitCoreInterface();`
   - Call to register CyInitCore with Python

7. **CvDLLWidgetData.cpp** (line 1126)
   - Fixed syntax error: removed extra `}` closing brace

8. **Project/AdvCiv.vcxproj** (lines 143-144, 322)
   - Added CyInitCore.cpp to ClCompile list
   - Added CyInitCoreInterface.cpp to ClCompile list
   - Added CyInitCore.h to ClInclude list

### Python Files (Assets/Python/)

#### New Files Created:

1. **Screens/GenericDecoratedScreen.py**
   - Base class for full-screen decorated Python screens
   - Handles common layout: background, header, footer, exit button
   - Provides dimension initialization utilities
   - Stripped-down version of MNAI's InterfaceUtils.py

2. **Screens/CustomGameScreen.py**
   - Main custom game screen implementation
   - Inherits from GenericDecoratedScreen
   - Displays game speed dropdown with help tooltips
   - Handles input for dropdown selection
   - Three footer buttons: Launch, Go Back, Close
   - Uses InputSim (via DLL) to trigger original screen actions

#### Modified Python Files:

1. **CvScreensInterface.py** (exact changes TBD)
   - Added import for CustomGameScreen
   - Added screen initialization
   - Added `showCustomGameScreen()` callback function (called from DLL)
   - Registered screen with event manager

## Current Features

### Working:
- ✅ Popup appears when clicking "Custom Game" from main menu
- ✅ Game Speed dropdown with all speed options
- ✅ Tooltips showing help text for each speed
- ✅ Changing speed actually modifies the game settings
- ✅ Launch button starts the game with selected settings
- ✅ Go Back button returns to main menu
- ✅ Close button closes the popup

### Screenshot Evidence:
- Civ4ScreenShot1535.JPG - Civ4ScreenShot1539.JPG show successful operation

## Technical Details

### Widget System

The implementation uses Civ4's widget system for help tooltips:

```python
# DLL widget help (shows info from GameSpeedInfo XML)
screen.addDropDownBoxGFC(self.GAMESPEED_DROPDOWN_ID, centerX, centerY, 200,
    WidgetTypes.WIDGET_HELP_GAME_SPEED, GameSpeedTypes.NO_GAMESPEED, 1, FontTypes.GAME_FONT)
```

Three methods for showing tooltips were explored:
1. DLL widget help attached to label - not used
2. Python help label - used for label
3. DLL widget help attached to dropdown - used for dropdown (best control)

### Button Handling

Three types of close buttons implemented:

1. **Launch Button**:
   - Uses `WIDGET_CLOSE_SCREEN` with data1=0
   - Simulates Return key press to trigger original Launch

2. **Go Back Button**:
   - Uses `WIDGET_CLOSE_SCREEN` with data1=2
   - Simulates mouse click to trigger original Go Back

3. **Close Button**:
   - Uses `WIDGET_CLOSE_SCREEN` with data1=-1
   - Regular close without key simulation

### Screen Persistence

```python
screen.setPersistent(True)  # Required to reopen after ESC key
```

Without this, the screen cannot be reopened after being closed with ESC.

## Compilation Notes

### Common Issues Fixed:

1. **Unused Variable Warnings**:
   - Problem: FAssert() compiled out in Release builds leaves unused variables
   - Solution: Add `(void)varName;` after FAssert to suppress warning
   - Applied to: `uSent` in InputSim.cpp, `bSuccess` in CvInitCore.cpp

2. **Class Size Assertion**:
   - Problem: Adding `m_bOnCustomGameScreen` increases CvInitCore size
   - Solution: Update BOOST_STATIC_ASSERT from 448/424 to 452/428 bytes
   - Note: Documented as client-side only, no network sync needed

3. **Undefined Type Errors**:
   - Problem: CvDLLPythonIFaceBase incomplete type in CvInitCore.cpp
   - Solution: Added `#include "CvDLLPythonIFaceBase.h"`

### Build Configuration:
- Tested with: Visual Studio 2010 Express
- Configuration: Release
- Platform: Win32
- Build system: nmake via MSBuild

## Future Enhancements

### Planned Features:
- [ ] Sea Level setting
- [ ] Climate setting
- [ ] Map size setting
- [ ] Number of civilizations
- [ ] Victory conditions
- [ ] Game options (advanced start, etc.)
- [ ] Leader/Civilization selection preview

### UI Improvements:
- [ ] Better layout and spacing
- [ ] Graphics/backgrounds for settings
- [ ] Preview panels showing setting effects
- [ ] Validation and constraints

### Code Cleanup:
- [ ] Resolve TAB-selection issue with background screen
- [ ] Improve key press simulation reliability
- [ ] Better separation of concerns in screen code

## Architecture Decisions

### Why Not Modify Original Screen?
The original Custom Game screen is part of the game EXE, not easily modifiable. This popup approach:
- Preserves original screen as fallback
- Allows full Python control of UI
- Enables rapid iteration without recompiling DLL
- Maintains compatibility with base game

### Why Toggle Detection?
Using `setVictories()` toggle is elegant because:
- No new EXE hooks required
- Works with existing game flow
- Reliable screen discrimination
- Minimal code changes

### Why Static CyInitCore Instance?
```cpp
CyInitCore& CyGlobalContext::getCyInitCore() const
{
    static CyInitCore cyInitCore;
    return cyInitCore;
}
```
- Ensures single instance across all Python calls
- References actual global CvInitCore through GC
- No memory management issues
- Follows existing Civ4 pattern

## Testing Checklist

When testing this implementation:

- [ ] Start game and go to Main Menu
- [ ] Click "Custom Game"
- [ ] Verify popup appears over original screen
- [ ] Check game speed dropdown shows all speeds
- [ ] Hover over dropdown to verify tooltips appear
- [ ] Change game speed selection
- [ ] Click Launch - game should start with selected speed
- [ ] Return to Main Menu, click Custom Game again
- [ ] Click Go Back - should return to Main Menu
- [ ] Click Custom Game again
- [ ] Click Close - popup should close
- [ ] Press ESC - popup should close
- [ ] Verify can reopen popup after closing

## Credits

- **Original Concept**: CuCuGS-PoC by f1rpo (CivFanatics forums)
- **Base Mod**: AdvCiv 1.12
- **Implementation**: AdvCiv-SAS team
- **Python UI Framework**: Based on MNAI's InterfaceUtils.py

## References

- CivFanatics CuCuGS-PoC thread: [Insert URL if available]
- AdvCiv forums: [Insert URL]
- Civ4 Modding documentation: BTS SDK documentation

## Notes for Modders

### Adding New Settings:

To add a new game setting (e.g., sea level):

1. **DLL Side** (in CyInitCore):
   ```cpp
   // CyInitCore.h
   int getSeaLevel();
   void setSeaLevel(int iSeaLevel);

   // CyInitCore.cpp
   int CyInitCore::getSeaLevel()
   {
       return m_kInitCore.getSeaLevel();
   }

   void CyInitCore::setSeaLevel(int iSeaLevel)
   {
       if (iSeaLevel < 0 || iSeaLevel >= GC.getNumSeaLevelInfos())
       {
           FAssertMsg(false, "index out of bounds");
           return;
       }
       m_kInitCore.setSeaLevel((SeaLevelTypes)iSeaLevel);
   }

   // CyInitCoreInterface.cpp
   .def("getSeaLevel", &CyInitCore::getSeaLevel, "int ()")
   .def("setSeaLevel", &CyInitCore::setSeaLevel, "void (int iSeaLevel)")
   ```

2. **Python Side** (in CustomGameScreen.py):
   ```python
   # Add dropdown
   screen.addDropDownBoxGFC("SeaLevelDropDown", x, y, width,
       WidgetTypes.WIDGET_HELP_SEA_LEVEL, SeaLevelTypes.NO_SEALEVEL, 1, FontTypes.GAME_FONT)

   # Populate options
   for i in range(gc.getNumSeaLevelInfos()):
       screen.addPullDownString("SeaLevelDropDown",
           gc.getSeaLevelInfo(i).getDescription(), i, i,
           i == gc.getInitCore().getSeaLevel())

   # Handle selection in handleInput()
   if inputClass.getFunctionName() == "SeaLevelDropDown":
       iIndex = screen.getSelectedPullDownID("SeaLevelDropDown")
       iSeaLevel = screen.getPullDownData("SeaLevelDropDown", iIndex)
       gc.getInitCore().setSeaLevel(iSeaLevel)
   ```

### Important Patterns:

1. Always validate bounds in C++ before calling setter
2. Use FAssertMsg for debug builds
3. Return early on invalid input
4. Follow existing naming conventions (WIDGET_HELP_*, get*/set*)
5. Add `(void)varName;` after FAssert if variable only used in assert

## Known Issues

1. **TAB Selection Background**: Players can still TAB to original screen widgets
   - Workaround: Using `screen.setFocus()` helps but not 100% reliable
   - Attempted `screen.setMainInterface(True)` but causes crash

2. **Key Simulation Timing**: Sleep delays might need adjustment on slower systems
   - Current: 10ms for keyboard, 5ms for mouse
   - Consider making configurable if issues arise

3. **Network Play**: Current implementation is single-player only
   - `m_bOnCustomGameScreen` not synchronized across network
   - Would need proper network handling for multiplayer support

## Version History

- **v0.1 (2025-12-31)**: Initial proof-of-concept
  - Basic game speed selection working
  - DLL trigger mechanism implemented
  - Python popup screen functional
  - Successfully tested and compiled

---

**Document Version**: 1.0
**Last Updated**: 2025-12-31
**Status**: Proof of Concept - Working

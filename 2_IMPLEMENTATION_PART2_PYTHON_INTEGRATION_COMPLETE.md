# Custom Game Screen Implementation - Part 2: Python Integration (COMPLETE)

## Overview

This document summarizes all Python and XML changes that have been implemented to complete the custom game popup screen integration. All Python modifications are complete and ready for testing after DLL compilation.

## Files Created

### 1. GenericDecoratedScreen.py
**Location:** `Assets/Python/Screens/GenericDecoratedScreen.py`

**Purpose:** Base class for decorated popup screens with header, footer, and background.

**Key Features:**
- Provides header and footer UI elements
- Handles screen dimensions and background setup
- Base class for any full-screen popup that needs decoration
- Stripped-down version of MNAI's InterfaceUtils.py

**Size:** 66 lines

### 2. CustomGameScreen.py
**Location:** `Assets/Python/Screens/CustomGameScreen.py`

**Purpose:** The actual custom game popup screen with game speed selector.

**Key Features:**
- Inherits from GenericDecoratedScreen
- Screen ID 33 (CUSTOM_GAME_SCREEN)
- Game speed dropdown selector with tooltips
- Three buttons:
  - **LAUNCH!** - Simulates Return key to launch game (data2=0)
  - **GO BACK** - Simulates mouse click to go back (data2=2)
  - **USE ORIGINAL SCREEN** - Closes popup without simulation (data2=-1)
- Updates gc.getInitCore().setGameSpeed() when user selects speed
- Shows immediately on top of original BTS custom game screen

**Size:** 139 lines

## Files Modified

### 3. CvScreenEnums.py
**Location:** `Assets/Python/Screens/CvScreenEnums.py`

**Changes:**
- Added line 39: `CUSTOM_GAME_SCREEN = 33 # AdvCiv-SAS - CuCuGS`

**What it does:**
- Defines the screen ID constant used by CustomGameScreen.py

### 4. CvScreensInterface.py
**Location:** `Assets/Python/EntryPoints/CvScreensInterface.py`

**Changes:**
1. Added import at line 40:
   ```python
   import CustomGameScreen # AdvCiv-SAS - CuCuGS
   ```

2. Added screen instance and show function at lines 120-124:
   ```python
   # AdvCiv-SAS - CuCuGS - Custom Game Screen
   customGameScreen = CustomGameScreen.CustomGameScreen()
   def showCustomGameScreen():
       customGameScreen.interfaceScreen()
   # AdvCiv-SAS - CuCuGS end
   ```

3. Added to HandleInputMap at line 1195:
   ```python
   CUSTOM_GAME_SCREEN : customGameScreen, # AdvCiv-SAS - CuCuGS
   ```

**What it does:**
- Imports the CustomGameScreen module
- Creates a global instance of the screen
- Provides the show function (though the screen auto-shows via popup)
- Registers the screen in HandleInputMap so it can receive input events

### 5. CIV4GameTextInfos_Custom.xml
**Location:** `Assets/XML/Text/CIV4GameTextInfos_Custom.xml`

**Changes:**
- Added text key at lines 233-237:
  ```xml
  <!-- AdvCiv-SAS - CuCuGS - Custom Game Screen text key -->
  <TEXT>
      <Tag>TXT_KEY_CUCUGS_CLOSE</Tag>
      <English>Use Original Screen</English>
  </TEXT>
  ```

**What it does:**
- Provides the text for the "USE ORIGINAL SCREEN" button
- Shows in the footer of the custom game popup

## How It Works

### Screen Flow
```
User clicks "Custom Game" in main menu
↓
BTS shows original custom game screen
↓
CustomGameScreen.py detects screen entry (via screen ID 33)
↓
Python automatically calls customGameScreen.interfaceScreen()
↓
Popup shows on top with blue panel (POPUPSTATE_IMMEDIATE)
↓
User selects game speed from dropdown
↓
User clicks one of three buttons:
├─ LAUNCH! → WIDGET_CLOSE_SCREEN(33, 0) → DLL simulates VK_RETURN
├─ GO BACK → WIDGET_CLOSE_SCREEN(33, 2) → DLL simulates mouse click
└─ USE ORIGINAL SCREEN → WIDGET_CLOSE_SCREEN(-1, -1) → Normal close
↓
Original BTS screen receives simulated input
↓
Game launches or returns to menu based on button clicked
```

### Input Handling Flow
```
User clicks button on popup
↓
handleInput() receives NOTIFY_CLICKED event
↓
Checks if WIDGET_CLOSE_SCREEN was clicked
↓
Sets focus to MAIN_PANEL_ID (for better focus management)
↓
DLL's CvDLLWidgetData.cpp receives widget data:
  - m_iData1 = screen ID (33 for custom game, -1 for normal close)
  - m_iData2 = action type (0=Return, 2=Mouse, -1=Close)
↓
DLL calls InputSim functions to simulate keypresses/clicks
↓
Original BTS custom game screen responds to simulated input
```

### Dropdown Interaction Flow
```
User opens game speed dropdown
↓
Mouse hovers over option
↓
WIDGET_HELP_GAME_SPEED widget shows tooltip
↓
DLL's CvDLLWidgetData.cpp calls setGameSpeedHelp()
↓
Tooltip displays speed description and effects
↓
User clicks speed option
↓
handleInput() receives NOTIFY_LISTBOX_ITEM_SELECTED
↓
Gets selected index and data from dropdown
↓
Calls gc.getInitCore().setGameSpeed(iGameSpeed)
↓
Game speed is updated for launch
```

## Integration Points

### DLL Integration
The Python code connects to the DLL through:
1. **Screen ID 33** - Identifies the custom game screen
2. **WIDGET_CLOSE_SCREEN** - Triggers button actions
3. **WIDGET_HELP_GAME_SPEED** - Provides tooltips
4. **InputSim functions** - Called from DLL when buttons clicked

### BTS Integration
The popup works because:
1. Original BTS custom game screen still exists in background
2. Popup shows on top with `POPUPSTATE_IMMEDIATE`
3. Input simulation controls the original screen underneath
4. When popup closes, focus returns to original screen

## Files Summary

**Created (2 files):**
- Assets/Python/Screens/GenericDecoratedScreen.py
- Assets/Python/Screens/CustomGameScreen.py

**Modified (3 files):**
- Assets/Python/Screens/CvScreenEnums.py
- Assets/Python/EntryPoints/CvScreensInterface.py
- Assets/XML/Text/CIV4GameTextInfos_Custom.xml

**Total: 5 files**

All changes are tagged with `# AdvCiv-SAS - CuCuGS` comments for easy identification.

## Next Steps

1. **Compile the DLL** (Part 1 changes):
   - Open `CvGameCoreDLL/Project/AdvCiv.sln` in Visual Studio 2010 Express
   - Select "Release" configuration
   - Build → Build Solution (F7)
   - Copy `CvGameCoreDLL/Project/Release/CvGameCoreDLL.dll` to `Assets/CvGameCoreDLL.dll`

2. **Test in-game**:
   - Launch Civilization IV Beyond the Sword
   - Load AdvCiv-SAS mod
   - Click "Custom Game" from main menu
   - Verify popup appears with game speed dropdown
   - Test all three buttons (LAUNCH!, GO BACK, USE ORIGINAL SCREEN)
   - Verify game speed selection works

3. **Future Enhancements** (Optional):
   - Add more game options (map size, sea level, climate, etc.)
   - Beautify the UI to match Civ3's new game menu style
   - Add leader/civilization selection
   - Add number of players selection
   - Add advanced game options

## Technical Notes

- The popup uses `screen.setPersistent(True)` to prevent ESC from permanently closing it
- Focus management attempts to prevent TAB-selecting widgets on original screen (partial success)
- Three different tooltip methods are demonstrated (DLL widget help, Python help label)
- The screen consumes all inputs (`return 1`) to prevent background interaction
- Button style attempts (arrows) are commented out as they didn't work perfectly

---

*Implementation Date: 2025-12-31*
*Based on: CivFanatics CuCuGS Proof-of-Concept by f1rpo*
*Part 2 of 2 - Python Integration Complete*

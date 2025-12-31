# Custom Game Screen Implementation - Part 1: DLL Changes (COMPLETE)

## Overview

This document summarizes all DLL changes that have been implemented to support the custom game popup screen. All C++ modifications are complete and ready for compilation.

## DLL Files Created

### 1. InputSim.h
**Location:** `CvGameCoreDLL/InputSim.h`

Provides keyboard and mouse input simulation functions:
- `void keySequence(...)` - Simulates a sequence of key presses
- `void keyPressed(byte ucVK)` - Simulates a single key press
- `void mouseClicked()` - Simulates a mouse click

These are used to control the original BTS custom game screen from our Python popup.

### 2. InputSim.cpp
**Location:** `CvGameCoreDLL/InputSim.cpp`

Implements the input simulation functions using Windows SendInput API.

## DLL Files Modified

### 3. CvDLLWidgetData.cpp
**Changes:**
- Added `#include "InputSim.h"` at the top
- Added WIDGET_CLOSE_SCREEN handling in `executeAction()` for screen ID 33 (our custom game screen)
- Added WIDGET_HELP_GAME_SPEED handling in `parseHelp()` for game speed tooltips

**What it does:**
- When user clicks Launch/Go Back/Close buttons on our popup (screen ID 33), it simulates keyboard/mouse inputs
- Data2 values: 0=Return key, 1=TAB+Return, 2=Mouse click
- Displays helpful tooltips for game speed selection

### 4. CvEnums.h
**Changes:**
- Added `WIDGET_HELP_GAME_SPEED` enum value at the end of the Widget types list

**What it does:**
- Defines a new widget type for showing game speed help information

### 5. CvGameTextMgr.h
**Changes:**
- Added declaration: `void setGameSpeedHelp(CvWStringBuffer &szBuffer, GameSpeedTypes eGameSpeed = NO_GAMESPEED, bool bReverse = false);`

**What it does:**
- Declares the function that generates help text for game speeds

### 6. CvGameTextMgr.cpp
**Changes:**
- Added implementation of `setGameSpeedHelp()` at the end of the file

**What it does:**
- Generates formatted help text listing all game speeds with their descriptions
- Can list in normal or reverse order (for dropdown compatibility)

### 7. CyEnumsInterface.cpp
**Changes:**
- Added `.value("WIDGET_HELP_GAME_SPEED", WIDGET_HELP_GAME_SPEED)` to expose widget type to Python

**What it does:**
- Makes the WIDGET_HELP_GAME_SPEED enum available in Python scripts

### 8. AdvCiv.vcxproj
**Location:** `CvGameCoreDLL/Project/AdvCiv.vcxproj`

**Changes:**
- Added `<ClCompile Include="..\InputSim.cpp" />` to compile list
- Added `<ClInclude Include="..\InputSim.h" />` to header list

**What it does:**
- Ensures InputSim files are compiled when building the DLL

## How It Works

### Flow Diagram
```
User clicks "Custom Game" in main menu
↓
BTS shows original custom game screen (grayed out in background)
↓
Python CustomGameScreen.py automatically shows popup on top
↓
User selects game speed in popup dropdown
↓
User clicks "LAUNCH!"
↓
Python sends WIDGET_CLOSE_SCREEN with (screen_id=33, data2=0)
↓
CvDLLWidgetData.cpp receives it
↓
InputSim::keyPressed(VK_RETURN) simulates pressing Enter
↓
Original BTS custom game screen's Launch button receives the Enter key
↓
Game launches with selected settings
```

### Button Mapping
- **LAUNCH!**: data2=0 → Simulates Return key
- **GO BACK**: data2=2 → Simulates mouse click
- **USE ORIGINAL SCREEN**: data2=3 → Just closes popup (can be added)

## Next Steps

All DLL modifications are complete. To proceed:

1. **Compile the DLL** using Visual Studio 2010 Express
2. **Copy the compiled DLL** to `Assets/` folder
3. **Create Python files** (Part 2):
   - GenericDecoratedScreen.py
   - CustomGameScreen.py
   - Integration with CvScreensInterface.py
4. **Add text keys** to XML
5. **Test in-game**

## Compilation Instructions

1. Open `CvGameCoreDLL/Project/AdvCiv.sln` in Visual Studio 2010 Express
2. Select "Release" configuration
3. Build → Build Solution (or press F7)
4. Copy `CvGameCoreDLL/Project/Release/CvGameCoreDLL.dll` to `Assets/CvGameCoreDLL.dll`

## Files Summary

**Created (2 files):**
- CvGameCoreDLL/InputSim.h
- CvGameCoreDLL/InputSim.cpp

**Modified (6 files):**
- CvGameCoreDLL/CvDLLWidgetData.cpp
- CvGameCoreDLL/CvEnums.h
- CvGameCoreDLL/CvGameTextMgr.h
- CvGameCoreDLL/CvGameTextMgr.cpp
- CvGameCoreDLL/CyEnumsInterface.cpp
- CvGameCoreDLL/Project/AdvCiv.vcxproj

**Total: 8 files**

All changes are conservative, well-commented with `// ccgs` tags, and follow the existing code style in AdvCiv.

---

*Implementation Date: 2025-12-31*
*Based on: CivFanatics CuCuGS Proof-of-Concept by f1rpo*

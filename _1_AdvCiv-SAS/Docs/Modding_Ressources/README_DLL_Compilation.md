# AdvCiv-SAS DLL Compilation Guide

This documents the tested local command-line Release-build workflow primarily for LLM/AI helpers operating through a terminal. Human modders can usually open [`AdvCiv.vcxproj`](/CvGameCoreDLL/Project/AdvCiv.vcxproj) directly with tools like Visual C++ 2010 Express and build the Release configuration through the IDE instead, as used for AdvCiv-SAS development. The clean-`temp_files`, output-verification, installation, testing, and post-build cleanup rules below still apply to either approach.

By default, AI helpers should let the user compile unless compilation is needed or the user agrees that the helper may do it.

## Toolchain layout

Visual C++ 2010 Express supplies the IDE, `vcvars32.bat` environment, and `nmake.exe` build driver. The actual Civ4 DLL is compiled and linked with Microsoft Visual C++ Toolkit 2003 for Civ4 compatibility.

[`AdvCiv.vcxproj`](/CvGameCoreDLL/Project/AdvCiv.vcxproj) is mainly an NMake wrapper, so it does not list every SDK/library path directly:

- [`Makefile.user`](/CvGameCoreDLL/Project/Makefile.user) sets `TOOLKIT` to `C:\Program Files (x86)\Civ4SDK\Microsoft Visual C++ Toolkit 2003` and `PSDK` to `C:\Program Files (x86)\Civ4SDK\WindowsSDK`.
- The main [`Makefile`](/CvGameCoreDLL/Project/Makefile) uses the Toolkit 2003 `cl.exe` and `link.exe`, plus the Windows SDK resource compiler.
- The system environment variable `CIV4_LIB_INSTALL_PATH=C:\Program Files (x86)\Civ4Libs` supplies the Boost 1.32.0 and Python24 headers/libraries.

Calling VS2010 `vcvars32.bat` before `nmake` is required for the remaining Visual Studio include environment. A direct `nmake` attempt without it failed on missing `sal.h`.

## Before every full compile attempt

This applies to the first attempt and every retry after a failure:

1. Resolve and verify the exact [`CvGameCoreDLL/Project/temp_files`](/CvGameCoreDLL/Project/temp_files) directory.
2. It must contain only its tracked zero-byte `.gitkeep` before starting.
3. Remove generated files/subfolders inside that exact directory while preserving `.gitkeep`. Do not broaden deletion beyond this directory.

Stale fast-build intermediates have produced unreliable DLL behavior in testing. A one-file retry may be useful only to diagnose a compiler failure; afterward, clean back to `.gitkeep` before retrying the full build. Do not accept a DLL resumed from partial intermediates after a failed attempt.

## Release compile command

Run this PowerShell command with `CvGameCoreDLL\Project` as the working directory:

```powershell
cmd.exe /d /s /c 'call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\vcvars32.bat" >nul && set "TARGET=Release" && "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\nmake.exe" source_list /NOLOGO && "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\nmake.exe" fastdep /NOLOGO && "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\nmake.exe" dll /NOLOGO'
```

Verification on 2026-08-14: from placeholder-only `temp_files`, this completed a full Release compile and link in about 106 seconds. Full builds on this machine generally take about 1 minute 30 seconds to 1 minute 42 seconds; allow about 2 minutes before treating quiet/buffered output as hung or timing it out.

The command writes `CvGameCoreDLL\Project\Release\CvGameCoreDLL.dll`. Verify successful command output/exit status and the updated DLL. Visual Studio/MSBuild builds also write `CvGameCoreDLL\Project\Release\AdvCiv.log`, where success is shown by `Build succeeded.`, but do not assume that direct `nmake` refreshes the IDE build log.

## Install, test, and clean

A successful project build does not by itself install or test the DLL used by the mod.

1. Copy `CvGameCoreDLL\Project\Release\CvGameCoreDLL.dll` to [`Assets/CvGameCoreDLL.dll`](/Assets/CvGameCoreDLL.dll) if the new build should be installed.
2. Verify the copied file (for example, compare source/destination SHA-256 hashes).
3. Launch and test Civ4 as appropriate for the change.
4. After verifying the generated DLL and, when installing it, copying/verifying the installed DLL, run the cleanup command below from `CvGameCoreDLL\Project`. Cleaning removes generated Release output.
5. Verify `temp_files` again contains only the zero-byte `.gitkeep`.

```powershell
cmd.exe /d /s /c 'call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\vcvars32.bat" >nul && set "TARGET=Release" && "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\nmake.exe" clean /NOLOGO'
```

## Transient legacy-compiler failures

During the 2026-08-14 verification, the first full attempt had a silent VC2003 `cl.exe` code-1 failure at unchanged `CyGlobalContextInterface4.cpp`. The exact correctly pathed one-file diagnostic target compiled immediately afterward. Cleaning fully back to `.gitkeep` and rerunning the complete command then produced a successful DLL.

For a similarly unexplained compiler failure: use a narrow retry only for diagnosis, discard the partial intermediates, clean back to `.gitkeep`, and retry the full build from scratch.

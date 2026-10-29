# Local tests

These tests exercise mod code outside Civ4 using platform-specific development tools. Run the relevant test when changing that subsystem or investigating a failure; they do not run during gameplay or normal DLL builds.

CI describes automatic execution, not a different kind of test. Our [GitHub workflows](/.github/workflows/README.md) run repository checks and [workflow-helper regression tests](/.github/workflows/tests/README.md); those commands can also be run locally. The tests in this folder currently require a separate local setup.

## Menu

- [Diagnostic writer](#diagnostic-writer)
- [Runtime exit observer](#runtime-exit-observer)
- [Runtime screenshot observer](#runtime-screenshot-observer)
- [Runtime source observer](#runtime-source-observer)
- [Assertion diagnostic harness](#assertion-diagnostic-harness)
- [Why this test is local](#why-this-test-is-local)

## Diagnostic writer

A user or agent explicitly runs this test; Civ4's flushing works independently of it.

The [Python runner](/tests/diagnostics/run_writer_tests.py) organizes the check: it extracts the current writer from `CvGameCoreUtils.cpp` and the separate current-state publisher from `SASRuntimeStatus.cpp`, invokes VC2003 to compile it, then runs the executable. Python is the launcher; VC2003 is the compiler.

The [C++ harness](/tests/diagnostics/sas_diagnostic_writer_harness.cpp) supplies minimal game scaffolding and the test cases. Compiling it with the extracted production writer tests the actual implementation rather than a separate reimplementation.

Run from the mod root:

```powershell
python tests/diagnostics/run_writer_tests.py
```

- Requires Python 3, Windows, Visual C++ Toolkit 2003 (VC2003), the Windows SDK and the Civ4 Boost headers. Defaults follow the local [DLL compilation setup](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README_DLL_Compilation.md); `--compiler`, `--vcvars` and `--sdk` override their locations, and `CIV4_LIB_INSTALL_PATH` supplies the library root.
- VS2010's `vcvars32.bat` supplies environment setup; the compiler invoked is VC2003's `cl.exe`.
- Exercises Unicode paths, reading during append, literal percent text, overwrite/append behavior, partial and zero-progress writes, shared retry-buffer limits, recovery notices, writer-health counters, explicit producer types independent of filenames, drained-file failure recovery, handle reuse/release and shutdown before BUG's root handoff.
- Runs in temporary directories, including simulated fallback output; no game DLL, project intermediates or real user logs are changed. The single C++ fixture needs no separate header because it shares no declarations with another compiled source file.
  - The executable and compiler outputs live under a temporary Windows folder, normally `%TEMP%\sas-cpp-writer-...`, and are removed when the runner finishes; they are not stored in Downloads, committed or installed into Civ4.
  - For example, on this setup the executable can be `C:\Users\PC\AppData\Local\Temp\sas-cpp-writer-ab12cd34\writer.exe`; the generated folder suffix varies.
  - Each invocation rebuilds from the current writer source, so later implementation changes are tested. Test cases remain unchanged until deliberately updated; no previously compiled test executable is reused.

Run this test when changing diagnostic buffering, paths, file sharing, retry/loss handling, runtime-status publication or lifecycle checkpoints, and when investigating missing or corrupted BBAI/SASGameRecord output. Unrelated AI, UI or gameplay edits do not require it.

A successful run exits with code 0 and prints three `PASS C++ diagnostic writer` results plus a runtime-status result, including a child process terminated without checkpoints or cleanup whose final submitted rows remain readable in both logs.

To inspect synthetic fixture output, pass `--export-runtime-examples <scratch-directory>`. Keep synthetic output separate from the [real history example](/_1_AdvCiv-SAS/Docs/examples/runtime_status/README.md) and the [inline real status/exit captures](/_1_AdvCiv-SAS/Docs/README_Logging_Inventory.md#runtime-status-and-history); normal test runs leave those unchanged.

Runtime-status cases parse the actual JSON and JSONL timeline, check disabled no-I/O/provenance behavior and autoplay countdown gating, and exercise lifecycle transitions, passive menu/loading observations, WorldBuilder mode versus visible-editor state, extended-game continuation, shared DLL identity, exact monotonic activity durations, interrupted autoplay, root migration, rollback after partial history appends, readable history after an unconfirmed close, recovered status-failure counters, sequential player-turn timing and accepted human end-turn readiness/Skip context.

Missing tools, compilation errors or failed assertions return a nonzero exit code.

Presentation cases also compile the actual CyGame screen bridge: disabled recording skips native editor/Advanced Start queries, either mode/show/hide ordering remains observable, and presentation-only rows retain whole activity durations. Pending exit requests survive late editor/turn callbacks.

The harness supplies minimal game scaffolding and simulates failures. Full DLL compilation, Python/EXE lifecycle integration, in-game live log access and autoplay performance still require separate validation.

The build-report regression fixture in [test_build_source_provenance.py](/.github/workflows/tests/repository/test_build_source_provenance.py) separately exercises the print-only Makefile toolchain query, overridden/missing executables and wrapper entry/parent-process evidence on Windows. It reads executable versions without compiling or linking a DLL.

## Runtime exit observer

Run `python tests/diagnostics/run_runtime_exit_observer_tests.py` on Windows with Python 3 and Windows PowerShell 5.1. The [runner](/tests/diagnostics/run_runtime_exit_observer_tests.py) tests the actual [shipped observer](/Assets/SASRuntimeExitObserver.ps1) against disposable child processes, without Civ4 or administrator rights.

The production launcher selects Windows PowerShell (`powershell.exe`), not PowerShell 7 (`pwsh.exe`). Its `WindowsPowerShell/v1.0/` directory name does not identify the installed engine version. The 32-bit Civ4 launcher uses the 32-bit Windows PowerShell on a 64-bit Windows host; the standalone test runner matches that architecture by default.

The observers record their actual `environment` in `SASRuntimeExit_*.json` and `SASRuntimeSourceWatch_*.json`: PowerShell version/edition, CLR identifier, .NET Framework registry release (or null if unavailable), process bitness and executable path.

The exit observer also records `listenerCompilation.state` and `elapsedMilliseconds`; that interval measures `Add-Type`, not Civ4 startup. See the [logged metadata sample](/_1_AdvCiv-SAS/Docs/README_Logging_Inventory.md#live-source-edit-observation).

The CLR identifier is distinct from the .NET Framework product version; see Microsoft's [Framework version detection](https://learn.microsoft.com/en-us/dotnet/framework/install/how-to-determine-which-versions-are-installed) and [Windows PowerShell versus PowerShell 7](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/what-s-new-in-powershell-core-60?view=powershell-6).

PowerShell's [`Add-Type`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/add-type?view=powershell-5.1) compiles the C# source into its own process using .NET Framework tooling.

It does not link the managed observer into Civ4's VC2003 DLL, so their compiler/runtime versions need not match. Language syntax, available framework APIs, Windows API declarations and process architecture still matter for the helper itself.

Older PowerShell/.NET combinations and alternative hosts are unverified.

Installing PowerShell 7 alone does not change the launcher selection. Listener compilation failure retains the process-exit wait when the PowerShell script itself runs; an absent/blocked PowerShell process prevents external observation entirely. Normal runtime-off gameplay launches no helper.

It checks ordinary and simulated abnormal exit codes, process creation identity, protection of a newer snapshot, concurrent observers, Unicode paths, torn history, unreadable/retired snapshots and failed final history writes.

The native writer harness also tests the real hidden launcher, receipt and final exit together.

Disposable Windows fixtures also test existing/new runtime-error and dump-choice dialogs, a same-title mismatched-control rejection, closure while the process remains alive, and exclusion of ordinary/assertion/foreign-process dialogs.

Runtime16 extends the same fixture with current and historical Gamebryo/NiDX9 `Failed to allocate video memory.` variants plus a generic-`ERROR` rejection. Recognized failures must retain bounded process/system/PE memory context and exact-process Runtime status context; hide/destroy must not resample or discard the original context.

The video-allocation windows are test-created signatures, not genuine SAS allocation failures; none was reproduced in the game. Passing fixtures establish recognition and evidence handling for those signatures, not universal MAF coverage.

A simulated access-violation exit code is a test input, not a real game crash. Normal DLL builds do not run this test.

## Runtime screenshot observer

[`run_runtime_screenshot_observer_tests.py`](/tests/diagnostics/run_runtime_screenshot_observer_tests.py) is a Windows-only standalone test for `Assets/SASRuntimeScreenshotObserver.ps1`. It uses a disposable screenshot directory and process, verifies that pre-existing/ignored files are excluded, confirms native-pattern and other image filenames, checks burst coalescing/SHA-256 plus Runtime-context correlation, duplicate ownership and clean EXITED state, and never writes into the user's real Civ4 `ScreenShots` folder.

## Runtime source observer

[`run_runtime_source_observer_tests.py`](/tests/diagnostics/run_runtime_source_observer_tests.py) is a Windows-only standalone test for the shipped `Assets/SASRuntimeSourceObserver.ps1`. It creates temporary mod-input trees and a disposable target process, then checks process/start identity, duplicate ownership, burst coalescing, create/change/rename/delete evidence, filtering, SHA-256 output and final EXITED state. It never edits the real mod tree. The fixtures cover map scripts/scenarios, themes, mod settings/root INI and BUG Config XML, and check the exact final SHA-256, an unchanged-content save, and exit during event subscription, which must not strand the watcher.

The native writer harness also has a smaller launcher case that verifies the real DLL-side Win32 path can start the adjacent observer and reach WATCHING when the default-off define is explicitly enabled.

## Assertion diagnostic harness

[`run_assertion_tests.py`](/tests/diagnostics/run_assertion_tests.py) is a second manual Windows/VC2003 check focused on `FAssert.cpp`. It extracts the current assertion writer/policy helpers into a temporary executable and executes the real startup fallback, post-GlobalDefines policy cache, automatic Ignore Once/Ignore Always/Stop Auto Play resolution, inactive-autoplay fallback, shared dialog/log runtime context, Unicode log path and escaped-field truncation behavior.

Run it from the mod root:

```text
python tests/diagnostics/run_assertion_tests.py
```

Like the writer harness, it never builds or installs the Civ4 DLL. The ordinary GitHub diagnostics tests keep only lightweight source/XML wiring guards because the CI runner does not provide VC2003/Win32; behavior belongs in this compiled local harness.

## Why this test is local

Our current CI check/test workflows use Ubuntu; this harness needs Windows APIs and the configured legacy compiler/SDK. Automating it would require a Windows job with that toolchain provisioned, so no automatic workflow is added for this single specialized test. It can be automated later if that runner setup becomes worthwhile.

The light-source ZIP includes these test sources for external review; executing them still requires the tools listed above.
